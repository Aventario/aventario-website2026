-- Aventario website — lead capture schema for Supabase.
-- Run this once in the Supabase SQL editor (Dashboard -> SQL Editor -> New query -> Run).
--
-- Design: one table, Row-Level Security ON with NO public policies. Only the
-- service_role key (used server-side by the Vercel /api/lead function) can read or
-- write. The anon/public key cannot touch this table, so the lead list is never
-- exposed to the browser. service_role bypasses RLS by design.

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
-- Intentionally NO anon/authenticated policies. Reads/writes happen only via the
-- service_role key from the server. To view leads, use the Supabase Table editor.
