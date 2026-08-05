-- Aventario lead pipeline — Asana delivery monitor
-- Applied to project zpuywttjadohtxvaloyq on 2026-07-25.
--
-- Why this exists: on 2026-07-23 the Asana token expired and the leads-to-Asana
-- trigger started returning 401. Nothing surfaced it. Leads kept being stored and
-- emailed while the board stayed empty, and it was only found by reading
-- net._http_response by hand two days later.
--
-- What this adds:
--   1. asana_forward_log — one row per lead, holding the pg_net request id.
--   2. forward_lead_to_asana() now writes that log row (task payload unchanged).
--   3. check_asana_forwards() — resolves each request against its HTTP response
--      and emails marketing@aventario.com when any lead failed to reach Asana.
--   4. pg_cron job 'asana-forward-healthcheck', every 15 minutes.
--
-- pg_net keeps response rows for a few hours only, so the check must run often
-- enough to see them. Anything still unresolved after 6 hours is marked unknown
-- rather than alerted, so a purged response never triggers a false alarm.

-- 1. Log table -------------------------------------------------------------
create table if not exists public.asana_forward_log (
  id          bigint generated always as identity primary key,
  lead_id     uuid,
  request_id  bigint,
  outcome     text        not null default 'pending',  -- pending | ok | failed | no_token | unknown
  status_code int,
  response    text,
  alerted     boolean     not null default false,
  created_at  timestamptz not null default now()
);
create index if not exists asana_forward_log_outcome_idx on public.asana_forward_log (outcome, alerted);
create unique index if not exists asana_forward_log_request_idx on public.asana_forward_log (request_id) where request_id is not null;

-- No policies: the table stays invisible to anon and authenticated. The
-- security-definer functions below are the only things that touch it.
alter table public.asana_forward_log enable row level security;

-- 2. Trigger function: same Asana payload, now logged ----------------------
create or replace function public.forward_lead_to_asana()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  tok text;
  task_name text;
  task_notes text;
  req_id bigint;
begin
  select decrypted_secret into tok from vault.decrypted_secrets where name = 'asana_pat' limit 1;
  if tok is null then
    insert into public.asana_forward_log (lead_id, outcome) values (NEW.id, 'no_token');
    return NEW;
  end if;

  if nullif(trim(NEW.name), '') is not null and nullif(trim(NEW.company), '') is not null then
    task_name := NEW.company || ' — ' || NEW.name;
  else
    task_name := coalesce(nullif(trim(NEW.company), ''), nullif(trim(NEW.name), ''), NEW.email, 'New lead');
  end if;

  task_notes :=
       'New lead from ' || coalesce(NEW.source, 'website') || E'\n\n'
    || 'Name: '    || coalesce(NEW.name, '-')    || E'\n'
    || 'Email: '   || coalesce(NEW.email, '-')   || E'\n'
    || 'Company: ' || coalesce(NEW.company, '-') || E'\n'
    || 'Type: '    || coalesce(NEW.type, '-')    || E'\n'
    || 'Source: '  || coalesce(NEW.source, '-')  || E'\n'
    || 'Consent: ' || coalesce(NEW.consent::text, '-') || E'\n'
    || 'Received: '|| coalesce(NEW.created_at::text, now()::text) || E'\n\n'
    || 'Message:'  || E'\n' || coalesce(nullif(NEW.message, ''), '(none)');

  select net.http_post(
    url := 'https://app.asana.com/api/1.0/tasks',
    headers := jsonb_build_object(
      'Authorization', 'Bearer ' || tok,
      'Content-Type', 'application/json'
    ),
    body := jsonb_build_object('data', jsonb_build_object(
      'name', task_name,
      'notes', task_notes,
      'workspace', '1151577748169308',
      'memberships', jsonb_build_array(jsonb_build_object(
        'project', '1216627741325106',
        'section', '1216627741325107'
      ))
    ))
  ) into req_id;

  insert into public.asana_forward_log (lead_id, request_id, outcome) values (NEW.id, req_id, 'pending');
  return NEW;
end;
$$;

-- 3. The check -------------------------------------------------------------
create or replace function public.check_asana_forwards()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  key text;
  row_ record;
  lines text := '';
  n int := 0;
begin
  -- resolve every pending request that now has a response
  update public.asana_forward_log l
     set outcome     = case when r.status_code between 200 and 299 then 'ok' else 'failed' end,
         status_code = r.status_code,
         response    = left(coalesce(r.content, r.error_msg), 300)
    from net._http_response r
   where r.id = l.request_id
     and l.outcome = 'pending';

  -- pg_net has purged the response: stop waiting, do not alert on it
  update public.asana_forward_log
     set outcome = 'unknown'
   where outcome = 'pending'
     and created_at < now() - interval '6 hours';

  for row_ in
    select * from public.asana_forward_log
     where outcome in ('failed', 'no_token') and not alerted
     order by created_at
  loop
    n := n + 1;
    lines := lines
      || coalesce(row_.status_code::text, 'no token in vault')
      || '  ·  lead ' || coalesce(row_.lead_id::text, '?')
      || '  ·  ' || to_char(row_.created_at, 'YYYY-MM-DD HH24:MI') || ' UTC' || E'\n';
  end loop;

  if n = 0 then
    return jsonb_build_object('failures', 0);
  end if;

  select decrypted_secret into key from vault.decrypted_secrets where name = 'resend_api_key' limit 1;
  if key is null then
    raise warning 'check_asana_forwards: % failure(s) but no resend_api_key in vault', n;
    return jsonb_build_object('failures', n, 'emailed', false);
  end if;

  perform net.http_post(
    url := 'https://api.resend.com/emails',
    headers := jsonb_build_object('Authorization', 'Bearer ' || key, 'Content-Type', 'application/json'),
    body := jsonb_build_object(
      'from', 'Aventario Website <onboarding@resend.dev>',
      'to', jsonb_build_array('marketing@aventario.com'),
      'subject', n || ' lead(s) did not reach Asana',
      'html',
         '<div style="font:14px Arial;color:#334b60;max-width:560px">'
      || '<h2 style="color:#334b60;margin:0 0 4px">Lead pipeline warning</h2>'
      || '<p>' || n || ' lead(s) were stored in Supabase, but no task was created in Asana. '
      || 'The lead data is safe, it is only missing from the board.</p>'
      || '<pre style="background:#f4f6f8;padding:10px;font:12px monospace">' || lines || '</pre>'
      || '<p>Most likely cause: the Asana token in Supabase Vault (<b>asana_pat</b>) expired. '
      || 'Rotation steps are in <b>website/supabase/LEAD-PIPELINE.md</b>.</p></div>'
    )
  );

  update public.asana_forward_log
     set alerted = true
   where outcome in ('failed', 'no_token') and not alerted;

  return jsonb_build_object('failures', n, 'emailed', true);
end;
$$;

-- 4. Schedule --------------------------------------------------------------
select cron.schedule('asana-forward-healthcheck', '*/15 * * * *', $$select public.check_asana_forwards();$$);
