// Aventario website — lead capture endpoint (Vercel serverless function).
//
// Receives JSON form posts from the website and stores them in Supabase (EU region).
// Zero dependencies: talks to the Supabase REST API with native fetch.
//
// Required env vars (Vercel -> Project -> Settings -> Environment Variables):
//   SUPABASE_URL                e.g. https://xxxxxxxx.supabase.co
//   SUPABASE_SERVICE_ROLE_KEY   the service_role key (server-side only, never shipped to the browser)
// Optional:
//   WHITEPAPER_URL              download path returned for type=whitepaper (default /Vendor_Management_Paper.pdf)

function safeParse(s) { try { return JSON.parse(s); } catch { return {}; } }

async function readBody(req) {
  if (req.body !== undefined && req.body !== null) {
    return typeof req.body === 'string' ? safeParse(req.body) : req.body;
  }
  return await new Promise((resolve) => {
    let d = '';
    req.on('data', (c) => { d += c; });
    req.on('end', () => resolve(safeParse(d)));
    req.on('error', () => resolve({}));
  });
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const SUPABASE_URL = process.env.SUPABASE_URL;
  const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
  const whitepaperUrl = process.env.WHITEPAPER_URL || '/Vendor_Management_Paper.pdf';

  const body = (await readBody(req)) || {};
  const email = String(body.email || '').trim();
  if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return res.status(400).json({ error: 'A valid email is required.' });
  }

  const row = {
    type: String(body.type || 'contact').slice(0, 40),
    name: String(body.name || '').slice(0, 200) || null,
    email: email.slice(0, 200),
    company: String(body.company || '').slice(0, 200) || null,
    message: String(body.message || '').slice(0, 4000) || null,
    source: String(body.source || '').slice(0, 120) || null,
    consent: body.consent === true,
    user_agent: String(req.headers['user-agent'] || '').slice(0, 400)
  };

  // Not configured yet -> tell the front-end so it can fall back (mailto / direct download).
  if (!SUPABASE_URL || !SERVICE_KEY) {
    return res.status(503).json({ error: 'Lead store not configured.' });
  }

  try {
    const r = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: SERVICE_KEY,
        Authorization: `Bearer ${SERVICE_KEY}`,
        Prefer: 'return=minimal'
      },
      body: JSON.stringify(row)
    });
    if (!r.ok) {
      const detail = await r.text().catch(() => '');
      return res.status(502).json({ error: 'Could not store lead.', detail: detail.slice(0, 300) });
    }
    const out = { ok: true };
    if (row.type === 'whitepaper') out.download = whitepaperUrl;
    return res.status(200).json(out);
  } catch (err) {
    return res.status(502).json({ error: 'Upstream error.' });
  }
}
