-- Aventario website — lead capture schema for Supabase.
-- Run once: Supabase Dashboard -> SQL Editor -> New query -> paste -> Run.
--
-- The website inserts leads from the browser using the PUBLISHABLE key (safe to expose).
-- RLS is ON with an INSERT-ONLY policy: the public can add a lead but can never read,
-- update, or delete the table. You view leads in Dashboard -> Table editor -> leads.

create extension if not exists "pgcrypto";

create table if not exists public.leads (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  type        text not null default 'contact',   -- contact | whitepaper | newsletter | webinar
  name        text,
  email       text not null,
  company     text,
  message     text,
  source      text,                               -- which page/form submitted it
  consent     boolean not null default false,
  user_agent  text
);

create index if not exists leads_created_at_idx on public.leads (created_at desc);
create index if not exists leads_type_idx       on public.leads (type);

alter table public.leads enable row level security;

-- Allow anonymous INSERT only (the browser submits with the publishable/anon key).
-- No SELECT/UPDATE/DELETE policy => the public can add a lead but never read the table.
drop policy if exists "Public can submit a lead" on public.leads;
create policy "Public can submit a lead"
  on public.leads
  for insert
  to anon
  with check (true);

-- Webinar registrations (webinar.html). Same insert-only RLS pattern.
create table if not exists public.webinar_registrations (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  name        text,
  email       text not null,
  company     text,
  consent     boolean not null default false,
  webinar     text,
  source      text
);
alter table public.webinar_registrations enable row level security;
grant insert on public.webinar_registrations to anon;
drop policy if exists "Public can register for a webinar" on public.webinar_registrations;
create policy "Public can register for a webinar"
  on public.webinar_registrations
  for insert
  to anon
  with check (true);

-- IMPORTANT: the browser sends the publishable key as the `apikey` header ONLY.
-- Do NOT also send `Authorization: Bearer <publishable key>`. The new sb_publishable_
-- keys are not JWTs; sending one as a Bearer token breaks role resolution and trips RLS.
