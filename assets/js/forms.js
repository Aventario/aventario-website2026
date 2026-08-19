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


  /* ---- click tracking ------------------------------------------------ */

  /** Sends to GA4 if the visitor has accepted analytics. gtag exists on every
   *  page, but only actually reports once consent loaded the tag, so a denied
   *  visitor costs nothing and nothing is queued behind their back. */
  function track(name, params) {
    if (typeof window.gtag === 'function') window.gtag('event', name, params || {});
  }

  /** Everything a marketer would call a conversion, or a step toward one, was
   *  untracked before 13.08.2026: every CTA, both PDFs, the assessment link,
   *  mailto and tel. Sessions were measured, intent was not. */
  function wireClicks() {
    document.addEventListener('click', function (e) {
      var a = e.target && e.target.closest ? e.target.closest('a') : null;
      if (!a) return;
      var href = a.getAttribute('href') || '';
      var label = (a.textContent || '').trim().slice(0, 80);
      var page = location.pathname;

      if (href.indexOf('mailto:') === 0) {
        return track('contact_click', { method: 'email', link_url: href.slice(7), page_path: page });
      }
      if (href.indexOf('tel:') === 0) {
        return track('contact_click', { method: 'phone', link_url: href.slice(4), page_path: page });
      }
      if (/\.(pdf|docx?|pptx?|xlsx?)($|\?)/i.test(href)) {
        return track('file_download', { file_name: href.split('/').pop().split('?')[0], link_text: label, page_path: page });
      }
      if (/typeform\.com/i.test(href)) {
        return track('assessment_start', { link_text: label, page_path: page });
      }
      if (/managedsuppliers\.com/i.test(href)) {
        // The two sites have separate GA4 properties, so a referred visitor cannot
        // be stitched into one session. This at least records that we sent them.
        return track('outbound_to_product', { link_text: label, page_path: page });
      }
      if (/^(https?:)?\/\//.test(href) && href.indexOf(location.hostname) === -1) {
        return track('outbound_click', { link_url: href, link_text: label, page_path: page });
      }
      if (/\/contact|\/de\/contact/.test(href) || /book|termin|gespr|call/i.test(label)) {
        return track('cta_click', { link_text: label, destination: href, page_path: page });
      }
    }, true);

    // A 404 is a broken link somewhere. Without this nobody ever learns which.
    if (document.title.indexOf('Page not found') === 0 || document.title.indexOf('Seite nicht gefunden') === 0) {
      track('page_not_found', { page_path: location.pathname, referrer: document.referrer || '(none)' });
    }
  }

  function init() {
    attribution();
    wireClicks();
    var forms = document.querySelectorAll('form[data-newsletter]');
    for (var i = 0; i < forms.length; i++) wireNewsletter(forms[i]);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
