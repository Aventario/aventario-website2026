/* Aventario shared form + attribution helper.
 *
 * Two jobs:
 *   1. Remember where a visitor came from (UTM tags, gclid, referrer, landing page)
 *      for the length of the session, so a lead can be traced back to a campaign.
 *   2. Make the footer newsletter form actually store the address. Until 13.08.2026
 *      that form only changed its own button text and threw the address away.
 *
 * Loaded on every page as /assets/js/forms.js. Insert-only anon key, same one the
 * contact form uses. Row level security allows INSERT and nothing else.
 */
(function () {
  'use strict';

  var SB_URL = 'https://zpuywttjadohtxvaloyq.supabase.co';
  var SB_KEY = 'sb_publishable_0R1ZCaygbhIA4xY3MhpN6w_qOFeRhoa';
  var STORE = 'av-attribution';

  /* ---- attribution -------------------------------------------------- */

  /** First touch wins: the campaign that brought someone to the site is the one
   *  credited, not whatever page they happened to be on when they filled a form. */
  function attribution() {
    try {
      var saved = sessionStorage.getItem(STORE);
      if (saved) return JSON.parse(saved);
    } catch (e) { /* private mode, carry on without persistence */ }

    var p = new URLSearchParams(location.search);
    var a = {
      utm_source: p.get('utm_source') || null,
      utm_medium: p.get('utm_medium') || null,
      utm_campaign: p.get('utm_campaign') || null,
      utm_term: p.get('utm_term') || null,
      utm_content: p.get('utm_content') || null,
      gclid: p.get('gclid') || p.get('wbraid') || p.get('gbraid') || null,
      referrer: document.referrer ? document.referrer.slice(0, 500) : null,
      landing_page: location.pathname + (location.search || '')
    };
    try { sessionStorage.setItem(STORE, JSON.stringify(a)); } catch (e) { /* ignore */ }
    return a;
  }

  // Expose it so the per-page contact and webinar forms can attach the same data.
  window.avAttribution = attribution;

  /* ---- newsletter ---------------------------------------------------- */

  function statusLine(form) {
    var el = form.parentNode.querySelector('[data-newsletter-status]');
    if (!el) {
      el = document.createElement('p');
      el.setAttribute('data-newsletter-status', '');
      el.className = 'text-sm mt-3';
      el.style.color = 'rgba(250,250,247,0.9)';
      form.parentNode.appendChild(el);
    }
    return el;
  }

  function wireNewsletter(form) {
    var de = (document.documentElement.lang || 'en').slice(0, 2) === 'de';
    var copy = de
      ? { ok: 'Danke. Sie stehen auf der Liste.', busy: 'Wird gesendet...', fail: 'Das hat nicht geklappt. Schreiben Sie uns an office@aventario.com.' }
      : { ok: 'Thanks. You are on the list.', busy: 'Sending...', fail: 'That did not work. Write to us at office@aventario.com.' };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type=email]');
      var btn = form.querySelector('button[type=submit]');
      if (!input || !form.checkValidity()) { form.reportValidity(); return; }

      var out = statusLine(form);
      out.textContent = copy.busy;
      if (btn) btn.disabled = true;

      var body = attribution();
      body.email = input.value.trim();
      body.consent = true;
      body.source = location.hostname.indexOf('managedsuppliers') > -1 ? 'managedsuppliers' : 'aventario';

      fetch(SB_URL + '/rest/v1/subscribers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', apikey: SB_KEY, Prefer: 'return=minimal' },
        body: JSON.stringify(body)
      }).then(function (r) {
        // 409 means the address is already on the list. For the visitor that is a success.
        if (!r.ok && r.status !== 409) throw new Error('HTTP ' + r.status);
        out.textContent = copy.ok;
        form.reset();
        if (window.gtag) gtag('event', 'newsletter_signup', { form_location: location.pathname });
      }).catch(function () {
        out.textContent = copy.fail;
      }).then(function () {
        if (btn) btn.disabled = false;
      });
    });
  }

  function init() {
    attribution();
    var forms = document.querySelectorAll('form[data-newsletter]');
    for (var i = 0; i < forms.length; i++) wireNewsletter(forms[i]);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
