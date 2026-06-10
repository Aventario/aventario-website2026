# Go live: HubSpot → Supabase + Cal.com

The website code is fully switched. HubSpot is removed. To turn the new forms on,
two free accounts need to exist and three values pasted in. ~15 minutes.

## 1. Supabase (forms + lead storage) — free

1. Create an account at https://supabase.com and a **new project**.
2. **Region: Frankfurt (eu-central-1)** — this keeps all data in the EU. Do not pick a US region.
3. In the project, accept the **DPA + SCC** (Settings → Legal/Compliance) before real data goes in.
4. Open **SQL Editor → New query**, paste the contents of [`supabase/schema.sql`](supabase/schema.sql), Run.
5. Grab two values from **Settings → API**:
   - `Project URL`  → goes into `SUPABASE_URL`
   - `service_role` key (the secret one, *not* anon) → goes into `SUPABASE_SERVICE_ROLE_KEY`

## 2. Vercel (where the site runs) — paste the two values

Vercel → the website project → **Settings → Environment Variables**, add:

| Name | Value |
|---|---|
| `SUPABASE_URL` | the Project URL from step 1 |
| `SUPABASE_SERVICE_ROLE_KEY` | the service_role key from step 1 |

Then **redeploy** (Deployments → … → Redeploy). The contact form and the whitepaper
gate now write straight into the `leads` table. View leads in Supabase → Table editor → `leads`.

## 3. Cal.com (booking) — free, replaces the HubSpot scheduler

1. Create an account at https://cal.com (use **cal.eu** if you want EU-hosted data).
2. Make an event type (e.g. a 30-min intro call). Your public link looks like
   `https://cal.com/<username>/<event>`.
3. Put that link in two places (search for `cal.com/aventario/intro` and replace):
   - `contact.html` — the "Or book a call directly" iframe
   - that's the only embed; the homepage just links to `contact.html#book`

## What the code does

- `api/lead.js` — serverless function; stores submissions in Supabase using the
  service_role key **server-side** (the key is never exposed to the browser).
- Contact + whitepaper forms POST to `/api/lead`. If the backend is ever unreachable,
  the contact form falls back to a mailto and the whitepaper still downloads — no lead/visitor is lost.
- `leads.type` distinguishes `contact` vs `whitepaper` (and is ready for `webinar`/`newsletter`).

## Still on the to-do list (not blocking)

- `datenschutz.html` privacy wording was updated to name Supabase (EU) + Cal.com instead
  of HubSpot. **Have this checked** before it goes live — it is legal copy.
- Footer newsletter form is still a placeholder (not wired to Supabase). Say the word and I'll wire it.
