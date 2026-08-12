import "jsr:@supabase/functions-js/edge-runtime.d.ts";

// Fires on every new row in leads / webinar_registrations / subscribers.
// Invoked by a Postgres AFTER INSERT trigger (pg_net) — so it runs for ANY
// insert (website form, API, manual), not just the browser. Sends an email to
// marketing@aventario.com via Resend. If RESEND_API_KEY is not set yet, it logs
// and no-ops gracefully (the row is already safely stored either way).
//
// This function does NOT create Asana tasks. That is handled by a separate
// database trigger, trg_forward_lead_to_asana on public.leads, which posts to
// Asana directly with the PAT held in Supabase Vault (secret name asana_pat).
// Adding an Asana call here would create two tasks per lead.
//
// Deployed as: supabase function notify-lead (verify_jwt = false; guarded by x-hook-secret).

const HOOK_SECRET = Deno.env.get("HOOK_SECRET") ?? "";
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY");
const TO = (Deno.env.get("LEADS_TO") || "marketing@aventario.com").split(",").map((s) => s.trim());
const FROM = Deno.env.get("LEADS_FROM") || "Aventario Website <onboarding@resend.dev>";
// Teams channel post. Set TEAMS_WEBHOOK_URL to the URL of the Teams workflow
// "Post to a channel when a webhook request is received" on Marketing Kampagnen.
// Unset means no channel post, everything else carries on as before.
const TEAMS_WEBHOOK_URL = Deno.env.get("TEAMS_WEBHOOK_URL");

Deno.serve(async (req) => {
  if (req.headers.get("x-hook-secret") !== HOOK_SECRET) {
    return new Response("forbidden", { status: 401 });
  }
  let body: any = {};
  try { body = await req.json(); } catch { /* ignore */ }
  const table = body.table || "leads";
  const rec = body.record || {};
  const subjectName = rec.name || rec.full_name || rec.email || "New submission";
  const kind = table === "webinar_registrations" ? "Webinar registration"
    : table === "subscribers" ? "Newsletter subscriber"
    : ((rec.type ? String(rec.type)[0].toUpperCase() + String(rec.type).slice(1) : "Contact") + " lead");

  const rows = Object.entries(rec)
    .filter(([k, v]) => v !== null && v !== "" && !["id", "user_agent", "confirmation_sent"].includes(k))
    .map(([k, v]) => `<tr><td style="padding:4px 14px 4px 0;color:#5f768b;font:13px Arial;vertical-align:top">${k}</td><td style="padding:4px 0;color:#334b60;font:13px Arial"><b>${String(v).replace(/</g, "&lt;")}</b></td></tr>`)
    .join("");
  const html = `<div style="max-width:560px"><h2 style="font:700 18px Arial;color:#334b60;margin:0 0 2px">${kind}</h2><p style="font:13px Arial;color:#5f768b;margin:0 0 16px">via aventario.com &middot; ${new Date().toISOString().slice(0, 16).replace("T", " ")} UTC</p><table style="border-collapse:collapse">${rows}</table><p style="font:12px Arial;color:#8aa0b2;margin-top:20px">Stored in Supabase &rarr; ${table}. Reply to reach the lead at ${rec.email || "n/a"}.</p></div>`;

  // Channel post first: it is the alert people actually see, and it must not
  // depend on the email working. A failure here is logged, never thrown.
  if (TEAMS_WEBHOOK_URL) {
    const facts = Object.entries(rec)
      .filter(([k, v]) => v !== null && v !== "" && !["id", "user_agent", "confirmation_sent"].includes(k))
      .slice(0, 12)
      .map(([k, v]) => ({ title: k, value: String(v).slice(0, 300) }));
    const card = {
      type: "message",
      attachments: [{
        contentType: "application/vnd.microsoft.card.adaptive",
        content: {
          $schema: "http://adaptivecards.io/schemas/adaptive-card.json",
          type: "AdaptiveCard",
          version: "1.4",
          body: [
            { type: "TextBlock", text: kind, weight: "Bolder", size: "Medium", color: "Accent" },
            { type: "TextBlock", text: subjectName, weight: "Bolder", wrap: true },
            { type: "FactSet", facts },
            { type: "TextBlock", text: `Stored in Supabase, table ${table}. A task is already in the Asana Lead Pipeline.`, isSubtle: true, size: "Small", wrap: true },
          ],
          actions: rec.email
            ? [{ type: "Action.OpenUrl", title: "Reply to this lead", url: `mailto:${rec.email}` }]
            : [],
        },
      }],
    };
    try {
      const t = await fetch(TEAMS_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(card),
      });
      console.log("[notify-lead:teams]", t.status, await t.text());
    } catch (e) {
      console.error("[notify-lead:teams] failed", String(e));
    }
  }

  if (!RESEND_API_KEY) {
    console.error("[notify-lead] RESEND_API_KEY not set — email skipped. Row stored:", JSON.stringify(rec));
    return new Response(JSON.stringify({ ok: false, reason: "no RESEND_API_KEY", stored: true }), { status: 200, headers: { "Content-Type": "application/json" } });
  }
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: FROM, to: TO, reply_to: rec.email || undefined, subject: `${kind}: ${subjectName}`, html }),
  });
  const out = await r.text();
  console.log("[notify-lead]", r.status, out);
  return new Response(JSON.stringify({ ok: r.ok, status: r.status }), { status: 200, headers: { "Content-Type": "application/json" } });
});
