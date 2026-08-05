import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

// Weekly rollup: pulls the last 7 days from every capture table and emails
// marketing@aventario.com a set of CSV attachments (open in Excel). Invoked by
// a pg_cron schedule (Mondays 07:00 UTC). Uses the auto-injected service-role
// key — no extra secret beyond RESEND_API_KEY.
//
// Deployed as: supabase function leads-digest (verify_jwt = false; guarded by x-hook-secret).

const HOOK_SECRET = Deno.env.get("HOOK_SECRET") ?? "";
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY");
const TO = (Deno.env.get("LEADS_TO") || "marketing@aventario.com").split(",").map((s) => s.trim());
const FROM = Deno.env.get("LEADS_FROM") || "Aventario Website <onboarding@resend.dev>";

function toCsv(rows: any[]): string {
  if (!rows.length) return "no submissions in this period";
  const cols = Object.keys(rows[0]);
  const esc = (v: any) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  return [cols.join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\r\n");
}
const b64 = (s: string) => btoa(unescape(encodeURIComponent(s)));

Deno.serve(async (req) => {
  if (req.headers.get("x-hook-secret") !== HOOK_SECRET) return new Response("forbidden", { status: 401 });
  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
  const since = new Date(Date.now() - 7 * 864e5).toISOString();
  const [leads, webi, subs] = await Promise.all([
    sb.from("leads").select("created_at,type,name,email,company,message,source,consent").gte("created_at", since).order("created_at"),
    sb.from("webinar_registrations").select("created_at,name,email,company,webinar,consent,source").gte("created_at", since).order("created_at"),
    sb.from("subscribers").select("created_at,email,source,utm_source,utm_campaign").gte("created_at", since).order("created_at"),
  ]);
  const attachments = [
    { filename: "leads.csv", content: b64(toCsv(leads.data || [])) },
    { filename: "webinar_registrations.csv", content: b64(toCsv(webi.data || [])) },
    { filename: "subscribers.csv", content: b64(toCsv(subs.data || [])) },
  ];
  const n = (leads.data?.length || 0) + (webi.data?.length || 0) + (subs.data?.length || 0);
  const html = `<div style="font:14px Arial;color:#334b60"><h2 style="color:#334b60">Weekly lead digest</h2><p>${n} new submissions in the last 7 days.</p><ul><li>${leads.data?.length || 0} contact leads</li><li>${webi.data?.length || 0} webinar registrations</li><li>${subs.data?.length || 0} newsletter subscribers</li></ul><p>CSV files attached — open in Excel.</p></div>`;
  if (!RESEND_API_KEY) {
    console.error("[leads-digest] RESEND_API_KEY not set — digest skipped. Count:", n);
    return new Response(JSON.stringify({ ok: false, reason: "no RESEND_API_KEY", count: n }), { status: 200, headers: { "Content-Type": "application/json" } });
  }
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: FROM, to: TO, subject: `Weekly lead digest — ${n} new`, html, attachments }),
  });
  console.log("[leads-digest]", r.status, await r.text());
  return new Response(JSON.stringify({ ok: r.ok, count: n }), { status: 200, headers: { "Content-Type": "application/json" } });
});
