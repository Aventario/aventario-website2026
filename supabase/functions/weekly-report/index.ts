import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

// Weekly marketing report. Pulls the numbers nobody currently looks at and posts
// them into the Teams channel as one card: traffic and conversions from GA4,
// clicks and impressions from Search Console, leads and subscribers from our own
// database, split by campaign.
//
// Runs on pg_cron, Mondays 07:15 UTC, right after leads-digest.
//
// Every data source is optional. Missing credentials degrade the card, they never
// break it: the Supabase numbers always work because they need no extra secret.
//
// Secrets it reads:
//   TEAMS_WEBHOOK_URL   the Teams workflow URL. Without it, nothing is posted.
//   GOOGLE_SA_JSON      a Google service account key, the whole JSON as one string.
//                       Grant that service account Viewer on the GA4 property and
//                       read access on the Search Console property.
//   GA4_PROPERTY_ID     numeric GA4 property id, no "properties/" prefix.
//   GSC_SITE_URL        exactly as it appears in Search Console, e.g. https://www.aventario.com/
//
// Deployed as: supabase function weekly-report (verify_jwt = false; guarded by x-hook-secret).

const HOOK_SECRET = Deno.env.get("HOOK_SECRET") ?? "";
const TEAMS_WEBHOOK_URL = Deno.env.get("TEAMS_WEBHOOK_URL");
const GOOGLE_SA_JSON = Deno.env.get("GOOGLE_SA_JSON");
const GA4_PROPERTY_ID = Deno.env.get("GA4_PROPERTY_ID");
const GSC_SITE_URL = Deno.env.get("GSC_SITE_URL");

const DAY = 864e5;
const ymd = (d: Date) => d.toISOString().slice(0, 10);

/* ---------- Google auth ------------------------------------------------ */

function pemToDer(pem: string): Uint8Array {
  const body = pem.replace(/-----[A-Z ]+-----/g, "").replace(/\s+/g, "");
  const raw = atob(body);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
  return out;
}

const b64url = (bytes: Uint8Array | string) => {
  const s = typeof bytes === "string" ? bytes : String.fromCharCode(...bytes);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
};

/** Exchange the service account key for an access token. Standard JWT bearer flow. */
async function googleToken(scopes: string[]): Promise<string | null> {
  if (!GOOGLE_SA_JSON) return null;
  let sa: { client_email: string; private_key: string };
  try {
    sa = JSON.parse(GOOGLE_SA_JSON);
  } catch {
    console.error("[weekly-report] GOOGLE_SA_JSON is not valid JSON");
    return null;
  }

  const now = Math.floor(Date.now() / 1000);
  const header = b64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claim = b64url(JSON.stringify({
    iss: sa.client_email,
    scope: scopes.join(" "),
    aud: "https://oauth2.googleapis.com/token",
    iat: now,
    exp: now + 3600,
  }));

  const key = await crypto.subtle.importKey(
    "pkcs8",
    pemToDer(sa.private_key),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = new Uint8Array(
    await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(`${header}.${claim}`)),
  );
  const assertion = `${header}.${claim}.${b64url(sig)}`;

  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer", assertion }),
  });
  if (!r.ok) {
    console.error("[weekly-report] google token failed", r.status, await r.text());
    return null;
  }
  return (await r.json()).access_token;
}

/* ---------- data sources ----------------------------------------------- */

type Ga4 = { sessions: number; users: number; conversions: number; topPages: string[] } | null;

async function ga4(from: Date, to: Date): Promise<Ga4> {
  if (!GA4_PROPERTY_ID) return null;
  const token = await googleToken(["https://www.googleapis.com/auth/analytics.readonly"]);
  if (!token) return null;

  const call = (body: unknown) =>
    fetch(`https://analyticsdata.googleapis.com/v1beta/properties/${GA4_PROPERTY_ID}:runReport`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then((r) => (r.ok ? r.json() : r.text().then((t) => { throw new Error(`GA4 ${r.status} ${t}`); })));

  const range = [{ startDate: ymd(from), endDate: ymd(to) }];
  try {
    const totals = await call({
      dateRanges: range,
      metrics: [{ name: "sessions" }, { name: "totalUsers" }, { name: "keyEvents" }],
    });
    const pages = await call({
      dateRanges: range,
      dimensions: [{ name: "pagePath" }],
      metrics: [{ name: "screenPageViews" }],
      orderBys: [{ metric: { metricName: "screenPageViews" }, desc: true }],
      limit: 5,
    });
    const row = totals.rows?.[0]?.metricValues ?? [];
    return {
      sessions: Number(row[0]?.value ?? 0),
      users: Number(row[1]?.value ?? 0),
      conversions: Number(row[2]?.value ?? 0),
      topPages: (pages.rows ?? []).map((r: any) => `${r.dimensionValues[0].value} (${r.metricValues[0].value})`),
    };
  } catch (e) {
    console.error("[weekly-report] ga4", String(e));
    return null;
  }
}

type Gsc = { clicks: number; impressions: number; position: number; topQueries: string[] } | null;

async function gsc(from: Date, to: Date): Promise<Gsc> {
  if (!GSC_SITE_URL) return null;
  const token = await googleToken(["https://www.googleapis.com/auth/webmasters.readonly"]);
  if (!token) return null;

  const url = `https://searchconsole.googleapis.com/webmasters/v3/sites/${encodeURIComponent(GSC_SITE_URL)}/searchAnalytics/query`;
  const call = (body: unknown) =>
    fetch(url, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then((r) => (r.ok ? r.json() : r.text().then((t) => { throw new Error(`GSC ${r.status} ${t}`); })));

  // Search Console data lags about three days, so the window is shifted back.
  const startDate = ymd(new Date(from.getTime() - 3 * DAY));
  const endDate = ymd(new Date(to.getTime() - 3 * DAY));
  try {
    const totals = await call({ startDate, endDate });
    const queries = await call({ startDate, endDate, dimensions: ["query"], rowLimit: 5 });
    const t = totals.rows?.[0] ?? { clicks: 0, impressions: 0, position: 0 };
    return {
      clicks: Math.round(t.clicks ?? 0),
      impressions: Math.round(t.impressions ?? 0),
      position: Math.round((t.position ?? 0) * 10) / 10,
      topQueries: (queries.rows ?? []).map((r: any) => `${r.keys[0]} (${Math.round(r.clicks)})`),
    };
  } catch (e) {
    console.error("[weekly-report] gsc", String(e));
    return null;
  }
}

/* ---------- card -------------------------------------------------------- */

function factSet(facts: { title: string; value: string }[]) {
  return { type: "FactSet", facts };
}

Deno.serve(async (req) => {
  if (req.headers.get("x-hook-secret") !== HOOK_SECRET) return new Response("forbidden", { status: 401 });

  const to = new Date();
  const from = new Date(to.getTime() - 7 * DAY);
  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);

  const [leads, subs, webi, analytics, search] = await Promise.all([
    sb.from("leads").select("source,utm_source,utm_campaign").gte("created_at", from.toISOString()),
    sb.from("subscribers").select("id").gte("created_at", from.toISOString()),
    sb.from("webinar_registrations").select("id").gte("created_at", from.toISOString()),
    ga4(from, to),
    gsc(from, to),
  ]);

  const leadRows = leads.data ?? [];
  const bySource = leadRows.reduce((acc: Record<string, number>, r: any) => {
    const k = r.utm_campaign || r.utm_source || r.source || "direct";
    acc[k] = (acc[k] || 0) + 1;
    return acc;
  }, {});
  const sourceLine = Object.entries(bySource).map(([k, v]) => `${k}: ${v}`).join(", ") || "none";

  const body: unknown[] = [
    { type: "TextBlock", text: "Website report", weight: "Bolder", size: "Medium", color: "Accent" },
    { type: "TextBlock", text: `${ymd(from)} to ${ymd(to)}`, isSubtle: true, size: "Small" },
    { type: "TextBlock", text: "Leads and signups", weight: "Bolder", spacing: "Medium" },
    factSet([
      { title: "Contact leads", value: String(leadRows.length) },
      { title: "Newsletter signups", value: String(subs.data?.length ?? 0) },
      { title: "Webinar registrations", value: String(webi.data?.length ?? 0) },
      { title: "By campaign", value: sourceLine },
    ]),
  ];

  if (analytics) {
    body.push({ type: "TextBlock", text: "Traffic", weight: "Bolder", spacing: "Medium" });
    body.push(factSet([
      { title: "Sessions", value: String(analytics.sessions) },
      { title: "Users", value: String(analytics.users) },
      { title: "Key events", value: String(analytics.conversions) },
      { title: "Top pages", value: analytics.topPages.join("\n") || "no data" },
    ]));
  } else {
    body.push({ type: "TextBlock", text: "Traffic: GA4 not connected. Set GOOGLE_SA_JSON and GA4_PROPERTY_ID.", isSubtle: true, size: "Small", wrap: true, spacing: "Medium" });
  }

  if (search) {
    body.push({ type: "TextBlock", text: "Google search", weight: "Bolder", spacing: "Medium" });
    body.push(factSet([
      { title: "Clicks", value: String(search.clicks) },
      { title: "Impressions", value: String(search.impressions) },
      { title: "Average position", value: String(search.position) },
      { title: "Top queries", value: search.topQueries.join("\n") || "no data" },
    ]));
  } else {
    body.push({ type: "TextBlock", text: "Google search: Search Console not connected. Set GOOGLE_SA_JSON and GSC_SITE_URL.", isSubtle: true, size: "Small", wrap: true, spacing: "Medium" });
  }

  const payload = {
    type: "message",
    attachments: [{
      contentType: "application/vnd.microsoft.card.adaptive",
      content: {
        $schema: "http://adaptivecards.io/schemas/adaptive-card.json",
        type: "AdaptiveCard",
        version: "1.4",
        body,
      },
    }],
  };

  if (!TEAMS_WEBHOOK_URL) {
    console.error("[weekly-report] TEAMS_WEBHOOK_URL not set — nothing posted.", JSON.stringify(bySource));
    return new Response(JSON.stringify({ ok: false, reason: "no TEAMS_WEBHOOK_URL", leads: leadRows.length }), {
      status: 200, headers: { "Content-Type": "application/json" },
    });
  }

  const r = await fetch(TEAMS_WEBHOOK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  console.log("[weekly-report]", r.status, await r.text());
  return new Response(JSON.stringify({ ok: r.ok, leads: leadRows.length, ga4: !!analytics, gsc: !!search }), {
    status: 200, headers: { "Content-Type": "application/json" },
  });
});
