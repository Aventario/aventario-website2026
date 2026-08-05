# aventario.com

The live Aventario website. Plain HTML, no build step.

Live at https://www.aventario.com (aventario.com redirects to www).

## What this is

| | |
|---|---|
| Stack | Static HTML + a prebuilt Tailwind stylesheet. No framework, no build, no bundler. |
| Pages | About 109. English at the root, German under `de/`. |
| Repo | `github.com/Aventario/aventario-website2026`, branch `main` |
| Hosting | Vercel, project `aventario-website` |
| Forms | Post into Supabase project `zpuywttjadohtxvaloyq`, table `public.leads` |
| Analytics | GA4 `G-WV4NNK7FSV`, loaded directly. No Google Tag Manager on this site. |
| Consent | Self-built banner, element `#av-consent`, Consent Mode v2. Nothing fires before the visitor accepts. |

## How a change goes live

1. Edit a file and commit it to `main`.
2. Vercel sees the commit within seconds and starts publishing.
3. About a minute later it is live.

There is no upload step, no FTP and no server to log into. Committing to `main` is publishing.

## How to undo a change

Vercel keeps every previous version.

1. Open the project in Vercel, go to Deployments.
2. Find the last deployment that was good.
3. Promote to Production.

The old version is back in seconds. You never need a backup for this.

## Working on it locally

Nothing to install. Open any `.html` file in a browser and it works.

To serve the whole site so links resolve properly:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Things that will bite you

**The Tailwind stylesheet is prebuilt.** `assets/tailwind.css` is a compiled file. If you use a Tailwind class that is not already in it, nothing happens and the page silently renders wrong. This has caused real bugs. Check the class exists in `assets/tailwind.css` before relying on it, or write plain CSS on the page.

**The icon font is a subset.** Phosphor icons were cut from 660 KB to 23 KB by keeping only the 53 icons in use. A new icon will not render until the subset is regenerated. Originals are in `_audit/phosphor-backup/`.

**`_staging/` is git-ignored.** Anything in there exists only on one machine and is in no backup.

**Legal pages are legally binding.** Do not let anyone, human or AI, rewrite `impressum.html` or `datenschutz.html` (or their `de/` versions) without a lawyer reading the result.

**Some draft pages are publicly reachable.** `index-b.html`, `index-c.html`, `index-v2.html` and `portfolio.html` are not excluded in `.vercelignore`, so they are live on the domain even though they are variants.

**Known open bug.** `https://www.aventario.com/services` returns 404.

## What runs on a schedule

- `api/keepalive.js`, daily at 06:00 UTC via the Vercel cron in `vercel.json`. Keeps the Supabase free tier from pausing.
- A Supabase `pg_cron` self-ping, daily, as a second line of defense behind the above.

## The lead pipeline

Documented in `supabase/LEAD-PIPELINE.md`. Short version: a form submission is saved to Supabase, a trigger calls the `notify-lead` edge function, Resend emails marketing@aventario.com, and a second trigger creates an Asana task.

The tokens behind this expire. One did, on 23 July 2026, and lead forwarding failed silently for two days. `supabase/asana-healthcheck.sql` now checks every 15 minutes and emails on the first failure. Someone has to own watching it.

## Related

- `managed-suppliers/website/DEPLOY.md` covers the other site, which is a Next.js app and does need a build step.
- `documents/handover/` holds the full handover pack: the system deck, the written handover, and the access workbook.
