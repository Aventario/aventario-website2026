# Aventario website — lead pipeline (single source of truth)

Everything a website form submission does now, and how it is wired. Deployed live to
Supabase project `zpuywttjadohtxvaloyq` on 2026-07-10. Source lives here so it is never
lost again (the previous lead-router was written and then deleted from the tree).

## Flow

```
Website form (contact / webinar / newsletter)
  → INSERT into Supabase table (leads | webinar_registrations | subscribers)   [already worked]
  → AFTER INSERT trigger  notify_new_submission()   [new]
  → pg_net HTTP POST → Edge Function  notify-lead    [new]
  → Resend → email to marketing@aventario.com        [live since 2026-07-25]

leads table only, a second AFTER INSERT trigger runs in parallel:
  → trg_forward_lead_to_asana → forward_lead_to_asana()
  → pg_net POST → task in Asana project "Lead Pipeline", section "New Leads"

pg_cron 'weekly-lead-digest'  (Mon 07:00 UTC)
  → Edge Function  leads-digest  → Resend → CSV rollup email to marketing@   [new]

pg_cron 'keepalive-selfping'  (daily 06:30 UTC)
  → pg_net GET /rest/v1/leads  → keeps the free-tier project from pausing,
    independent of the Vercel cron (which was the single point of failure)   [new]
```

## Components

| Piece | Where | Notes |
|---|---|---|
| `notify-lead` | `supabase/functions/notify-lead/index.ts` | Per-submission email. `verify_jwt=false`, guarded by `x-hook-secret`. |
| `leads-digest` | `supabase/functions/leads-digest/index.ts` | Weekly CSV email. Uses auto-injected service-role key. |
| `notify_new_submission()` + 3 triggers | migration `lead_notify_trigger` | Fires for form/API/manual inserts alike. |
| `keepalive-selfping`, `weekly-lead-digest` | migration `keepalive_and_digest_cron` | pg_cron jobs. Check with `select * from cron.job;`. |
| Vercel `/api/keepalive` | `api/keepalive.js` | Secondary keepalive, kept as redundancy. |
| `forward_lead_to_asana()` + `trg_forward_lead_to_asana` | database only, no file in this repo | Creates the Asana task. Reads the PAT from Supabase Vault, secret name `asana_pat`. Project `1216627741325106`, section `1216627741325107`. Runs on `leads` only, not on webinar or newsletter rows. |

## Asana: where the token lives, and how it breaks

The Asana call authenticates with a personal access token stored in **Supabase Vault**
under the name `asana_pat`, not in an edge-function secret and not in this repo. When that
token expires or is revoked, the trigger fails silently: the lead row is still stored, the
email still sends, and only `net._http_response` shows the 401. That is exactly what
happened between 2026-07-23 and 2026-07-25.

Check for it:

```sql
select id, status_code, left(content, 80), created
from net._http_response order by created desc limit 5;
```

Rotate the token:

```sql
select vault.update_secret(
  (select id from vault.secrets where name = 'asana_pat'),
  '<new asana PAT>'
);
```

Do not add an Asana call to the `notify-lead` edge function. Both would fire and every
lead would appear twice on the board.

## The monitor

`asana-healthcheck.sql` in this folder is the applied source. Every lead now writes a row
into `public.asana_forward_log` holding the pg_net request id. The pg_cron job
`asana-forward-healthcheck` runs every 15 minutes, matches each request to its HTTP
response, and emails `marketing@aventario.com` as soon as a lead fails to reach Asana.
Each failure is alerted once. Requests still unresolved after 6 hours are marked `unknown`
instead of alerted, because pg_net purges response rows and a purge is not a failure.

The alert needs the Resend key in Vault under the name `resend_api_key` (already set).
State check:

```sql
select outcome, count(*) from public.asana_forward_log group by 1;
select public.check_asana_forwards();   -- returns {"failures": 0} when healthy
```

## Email credential

Set as an edge-function secret on 2026-07-25 and verified end to end.

1. Key comes from https://resend.com (account: `marketing@aventario.com`).
2. Supabase dashboard → Project `zpuywttjadohtxvaloyq` → Edge Functions → **Secrets** →
   `RESEND_API_KEY = re_...`.
   - Optional: `LEADS_TO` (comma-separated recipients; default `marketing@aventario.com`).
   - Optional: `LEADS_FROM` (default `Aventario Website <onboarding@resend.dev>`).
3. For branded deliverability, verify `aventario.com` in Resend (add the DNS records in
   Vercel), then set `LEADS_FROM = Aventario Leads <leads@aventario.com>`. Until then the
   default `onboarding@resend.dev` sender works fine for internal alerts.

Swap-in alternative: to send via the M365 `marketing@aventario.com` mailbox instead of
Resend, only the `fetch(...)` call inside each function changes (Microsoft Graph
`/sendMail`); trigger, cron and CSV logic are provider-agnostic.

## Test it

```sql
-- fires the whole chain; check net._http_response for status 200
insert into public.leads (type,name,email,message,source,consent)
values ('contact','Test','test@example.com','pipeline test','manual-test',true);

select id,status_code,error_msg,created from net._http_response order by created desc limit 3;

-- edge function logs: Supabase dashboard → Edge Functions → notify-lead → Logs
-- (before the key is set you will see "RESEND_API_KEY not set — email skipped").

delete from public.leads where source = 'manual-test';
```

Force a digest now: `select net.http_post(url:='https://zpuywttjadohtxvaloyq.supabase.co/functions/v1/leads-digest', headers:=jsonb_build_object('Content-Type','application/json','x-hook-secret','<HOOK_SECRET>'), body:='{}'::jsonb);`

## The hook secret

`notify-lead` and `leads-digest` are guarded by a shared header, `x-hook-secret`.
It used to be hardcoded in both function files. This repo is public, so on 2026-08-05
it was moved to an environment variable named `HOOK_SECRET`.

The live value is in the protected handover workbook, `Aventario-Access-Handover.xlsx`,
on the `Accounts & Passwords` tab under "Supabase edge functions".

The already-deployed functions still carry the old inlined value, so nothing broke.
Before the next `supabase functions deploy`, set the secret first or the endpoint
will reject every call:

```
supabase secrets set HOOK_SECRET=<value from the workbook>
```
