/* alerts.js — the behaviour of both alert pages.
 *
 * `scripts/alerts.py` writes the markup and a `window.ALERTS` blob holding the
 * vocabularies, the caps, the Turnstile site key and the reader-facing strings;
 * this is the part that does not change when the catalogue does.
 * `documentation/catalogue-alerts.md` Part 1 B is the design.
 *
 * TWO PAGES, ONE FILE. `ALERTS.page` is `signup` or `manage`. They share the
 * picker — a pair of multi-selects with an Any option and a cap of five — and
 * share Turnstile; everything else is one branch each at the bottom.
 *
 * THE SIGN-UP FORM WORKS WITHOUT THIS SCRIPT. It is a real form posting
 * `application/x-www-form-urlencoded` to the Worker, which answers 303, so the
 * browser's own navigation carries the result. What this adds is the cap, the
 * fragment preselect, the feed address and one refusal the Worker would make
 * anyway. The manage page is the opposite and says so: it needs the script,
 * because the subscriber id has to reach the Worker in a POST body rather than
 * in a URL (see `readKey`).
 *
 * A TURNSTILE TOKEN IS USED ONCE. Cloudflare invalidates a token on
 * verification, so a page that verifies twice — list, then save — has to reset
 * the widget in between. `withToken` is the whole of that: it hands out the
 * token it holds, or waits for the callback, and resets after every use.
 */
(function () {
  'use strict';

  var C = window.ALERTS || {};
  if (!C.page) { return; }

  var MAX = C.maxPerFacet || 5;
  var ANY = 'any';

  // ---------------------------------------------------------------- pickers

  function values(sel) {
    return Array.prototype.filter.call(sel.options, function (o) { return o.selected; })
      .map(function (o) { return o.value; });
  }

  function setValues(sel, vals) {
    Array.prototype.forEach.call(sel.options, function (o) {
      o.selected = vals.indexOf(o.value) > -1;
    });
    sel.dataset.prev = vals.join(',');
  }

  /* Any and a country are not two answers to one question.
   *
   * Picking Any drops whatever else was held; picking a country drops Any. Over
   * the cap the change is undone rather than trimmed — trimming means the reader
   * watches the page choose four of their five, and cannot tell which. */
  function normalise(sel) {
    var prev = (sel.dataset.prev || ANY).split(',').filter(Boolean);
    var cur = values(sel);
    var gainedAny = cur.indexOf(ANY) > -1 && prev.indexOf(ANY) === -1;
    var real = cur.filter(function (v) { return v !== ANY; });

    if (gainedAny || real.length === 0) { setValues(sel, [ANY]); return true; }
    if (real.length > MAX) { setValues(sel, prev); return false; }
    setValues(sel, real);
    return true;
  }

  /* The selection as the form and the Worker mean it: a list of codes, or an
   * empty list for Any. Every caller wants it this way — the alert definition,
   * the feed URL and the catalogue link are all "the codes, if any". */
  function picked(sel) {
    return values(sel).filter(function (v) { return v !== ANY; });
  }

  function pickers(scope) {
    return {
      places: scope.querySelector('[data-pick="places"]'),
      topics: scope.querySelector('[data-pick="topics"]')
    };
  }

  /* Preselect from a list of codes, silently dropping any the vocabulary does not
   * carry — a shared link outliving a renamed topic should open the page, not
   * break it. Returns true if the list was longer than the cap, which is the one
   * case the reader is told about. */
  function preselect(sel, codes, vocab) {
    var known = codes.filter(function (c) { return Object.prototype.hasOwnProperty.call(vocab, c); });
    if (!known.length) { setValues(sel, [ANY]); return false; }
    setValues(sel, known.slice(0, MAX));
    return known.length > MAX;
  }

  function initPickers(scope) {
    var p = pickers(scope);
    if (p.places) { setValues(p.places, [ANY]); }
    if (p.topics) { setValues(p.topics, [ANY]); }
    return p;
  }

  /* A click toggles one option; it does not replace the selection.
   *
   * A native `<select multiple>` replaces on a plain click and adds only on Ctrl+click,
   * which nobody outside a spreadsheet knows — Bill clicked Nigeria and lost Kenya
   * (2026-09-16, step D14). So a mouse press on an option is taken over: the option flips,
   * the list keeps its scroll position, and a `change` fires so `normalise` still applies
   * Any and the cap. The keyboard is left alone, and so are phones, whose pickers are
   * checkbox lists already and send no mousedown on an option. */
  document.addEventListener('mousedown', function (e) {
    var o = e.target;
    if (!o || o.tagName !== 'OPTION') { return; }
    var sel = o.closest('select[data-pick]');
    if (!sel || o.disabled) { return; }
    e.preventDefault();
    var top = sel.scrollTop;
    o.selected = !o.selected;
    sel.focus();
    sel.scrollTop = top;
    setTimeout(function () { sel.scrollTop = top; }, 0);
    sel.dispatchEvent(new Event('change', { bubbles: true }));
  });

  // ---------------------------------------------------------------- fragment

  /* `#places=KEN,NGA&topics=tech.ai&site=1` — the catalogue's own fragment, so the
   * Get alerts button can hand its state over unchanged. `writeHash` on the
   * catalogue encodes the joined value, so decode before splitting. */
  function fragment() {
    var out = {};
    (location.hash || '').replace(/^#/, '').split('&').forEach(function (kv) {
      if (!kv) { return; }
      var i = kv.indexOf('=');
      if (i < 0) { return; }
      var k = kv.slice(0, i);
      var v = kv.slice(i + 1);
      try { v = decodeURIComponent(v); } catch (e) { /* a stray % : take it raw */ }
      out[k] = v;
    });
    return out;
  }

  function codes(s) {
    return (s || '').split(',').map(function (v) { return v.trim(); }).filter(Boolean);
  }

  // ---------------------------------------------------------------- messages

  var msg = document.getElementById('msg');

  function say(html, ok) {
    if (!msg) { return; }
    msg.innerHTML = html;
    msg.className = 'alert-msg' + (ok ? ' alert-msg--ok' : '');
    msg.hidden = false;
  }

  function said(key, ok) {
    var t = (C.messages || {})[key];
    if (t) { say(t, ok); }
  }

  // ---------------------------------------------------------------- Turnstile

  /* The widget is rendered explicitly rather than by class, because both pages
   * need the token in hand before they can act — the manage page cannot even list
   * without one — and the implicit render gives no handle to reset. */
  var widget = null;
  var token = null;
  var waiting = [];

  /* One waiter per token. `spend` resets the widget, which produces another token and
   * brings us back here for the next one — so the queue drains one at a time rather
   * than handing the same single-use token to everybody in it. */
  function onToken(t) {
    token = t;
    if (waiting.length) { spend(waiting.shift()); }
  }

  function spend(fn) {
    var t = token;
    token = null;
    if (turnstileReady() && widget !== null) { window.turnstile.reset(widget); }
    fn(t);
  }

  function withToken(fn) {
    if (token) { spend(fn); return; }
    waiting.push(fn);
  }

  /* Is Cloudflare's script here — tested by the method, not by the name.
   *
   * A browser makes every element with an `id` a global of the same name, so while
   * the container was `<div id="turnstile">`, `window.turnstile` was that empty div
   * until `api.js` arrived. The old test saw it, called `render` on a div, threw, and
   * never left the callback — no widget, and every sign-up failed the check
   * (2026-09-16, step D5). The container is `alerts-turnstile` now, and the test
   * asks for the function it is about to call, so a renamed id cannot bring it back. */
  function turnstileReady() {
    return !!(window.turnstile && typeof window.turnstile.render === 'function');
  }

  function renderTurnstile() {
    var host = document.getElementById('alerts-turnstile');
    if (!host || !turnstileReady()) { return false; }
    widget = window.turnstile.render(host, {
      sitekey: C.turnstileKey,
      callback: onToken,
      'expired-callback': function () { token = null; },
      'error-callback': function () { token = null; }
    });
    return true;
  }

  /* `api.js` is loaded async, so it may or may not have run by the time this does.
   * `onloadTurnstileCallback` is Cloudflare's own hook for the second case. */
  function startTurnstile(then) {
    if (renderTurnstile()) { then(); return; }
    window.onloadTurnstileCallback = function () { renderTurnstile(); then(); };
  }

  // ---------------------------------------------------------------- sign up

  function signup() {
    var form = document.getElementById('signup');
    if (!form) { return; }
    var p = initPickers(form);
    var site = document.getElementById('site');
    var several = document.getElementById('several');
    var feedurl = document.getElementById('feedurl');
    var feedmain = document.getElementById('feedmain');

    var q = new URLSearchParams(location.search);
    // `?ok=confirmed` is where Buttondown sends a reader after they click the link in
    // its confirmation email; `?ok=added` is the Worker's redirect for a reader already
    // confirmed, and `?ok=1` for a new one who has an email to click.
    if (q.get('ok') === 'confirmed' || q.get('ok') === 'added') { said(q.get('ok'), true); } else if (q.get('ok')) { said('ok', true); }
    if (q.get('e')) { said('e-' + q.get('e'), false); }

    var frag = fragment();
    var over = false;
    if (frag.places) { over = preselect(p.places, codes(frag.places), C.places) || over; }
    if (frag.topics) { over = preselect(p.topics, codes(frag.topics), C.topics) || over; }
    if (frag.site === '1' && site) { site.checked = true; }
    if (over && several) { several.hidden = false; }

    function feed() {
      if (!feedurl) { return; }
      var pl = picked(p.places);
      var tp = picked(p.topics);
      var qs = [];
      if (pl.length) { qs.push('places=' + encodeURIComponent(pl.join(','))); }
      if (tp.length) { qs.push('topics=' + encodeURIComponent(tp.join(','))); }
      feedurl.textContent = qs.length
        ? C.site + '/api/alerts/feed?' + qs.join('&')
        : 'Pick a country or a topic first.';
      if (feedmain) { feedmain.hidden = !(site && site.checked); }
    }

    form.addEventListener('change', function (e) {
      if (e.target.dataset && e.target.dataset.pick) {
        if (!normalise(e.target) && several) { several.hidden = false; }
      }
      feed();
    });

    /* The same refusal the Worker makes, made here so the reader keeps their
     * typing. Everything else the Worker validates — the vocabulary, the caps, the
     * address — either cannot be wrong from this page or is the browser's own job. */
    form.addEventListener('submit', function (e) {
      if (!picked(p.places).length && !picked(p.topics).length && !(site && site.checked)) {
        e.preventDefault();
        said('e-input', false);
        msg.scrollIntoView({ block: 'nearest' });
      }
    });

    feed();
    startTurnstile(function () {});
  }

  // ---------------------------------------------------------------- manage

  /* The subscriber id is read from the fragment and sent in a POST body.
   *
   * A fragment is not sent to a server, does not reach an access log and does not
   * travel in a `Referer`, which a query string does all three of. That is the
   * whole reason the manage link is `#s=…` and the whole reason this page cannot
   * work without JavaScript: there is no form post that keeps the id out of the
   * URL. */
  function readKey() {
    return fragment().s || '';
  }

  function manage() {
    var key = readKey();
    var wrap = document.getElementById('manage');
    var nokey = document.getElementById('nokey');
    /* `#s=…&confirmed=1` is where Buttondown sends a reader after they confirm, with their
     * id in `s` if its redirect setting fills in `{{ subscriber.id }}`. If it does not, the
     * key arrives as literal braces: say *confirmed* anyway, and leave the note pointing at
     * the link in the email. */
    var confirmed = fragment().confirmed === '1';
    if (!/^[A-Za-z0-9_-]{8,64}$/.test(key)) {
      if (confirmed) { said('confirmed', true); }
      if (nokey) { nokey.hidden = false; }
      return;
    }

    var rows = document.getElementById('rows');
    var tpl = document.getElementById('rowtpl');
    var site = document.getElementById('site');
    var add = document.getElementById('add');
    var save = document.getElementById('save');
    var max = C.maxAlerts || 10;

    function count() { return rows.querySelectorAll('.alert-row').length; }

    /* `Alert 1  Countries — Botswana; Topics — Data protection`, above each row's lists,
     * redrawn on every change and renumbered on every delete. The labels are the
     * vocabulary's, so the sentence reads as the lists do. */
    function names(codes, vocab) {
      return codes.length ? codes.map(function (c) { return vocab[c] || c; }).join(', ') : 'Any';
    }
    function summarise() {
      Array.prototype.forEach.call(rows.querySelectorAll('.alert-row'), function (row, i) {
        var p = pickers(row);
        var sum = row.querySelector('.alert-row__sum');
        if (!sum) { return; }
        sum.textContent = '';
        var b = document.createElement('b');
        b.textContent = 'Alert ' + (i + 1);
        sum.appendChild(b);
        sum.appendChild(document.createTextNode(
          'Countries \u2014 ' + names(picked(p.places), C.places) +
          '; Topics \u2014 ' + names(picked(p.topics), C.topics)));
      });
    }

    function addRow(alert) {
      if (count() >= max) { return null; }
      var row = tpl.content.firstElementChild.cloneNode(true);
      rows.appendChild(row);
      var p = initPickers(row);
      if (alert) {
        if (alert.places && alert.places.length) { preselect(p.places, alert.places, C.places); }
        if (alert.topics && alert.topics.length) { preselect(p.topics, alert.topics, C.topics); }
      }
      if (add) { add.disabled = count() >= max; }
      summarise();
      return row;
    }

    function collect() {
      return Array.prototype.map.call(rows.querySelectorAll('.alert-row'), function (row) {
        var p = pickers(row);
        return { places: picked(p.places), topics: picked(p.topics) };
      }).filter(function (a) { return a.places.length || a.topics.length; });
    }

    function post(path, body, done) {
      withToken(function (t) {
        body['cf-turnstile-response'] = t || '';
        fetch(C.site + '/api/alerts/' + path, {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify(body)
        }).then(function (r) {
          return r.ok ? r.json() : Promise.reject(new Error(String(r.status)));
        }).then(done).catch(function () { said('e-later', false); });
      });
    }

    var several = document.getElementById('several');
    rows.addEventListener('change', function (e) {
      if (e.target.dataset && e.target.dataset.pick) {
        if (!normalise(e.target) && several) { several.hidden = false; }
        summarise();
      }
    });

    rows.addEventListener('click', function (e) {
      if (e.target.dataset && e.target.dataset.del) {
        var row = e.target.closest('.alert-row');
        if (row) { row.remove(); }
        if (add) { add.disabled = count() >= max; }
        summarise();
      }
    });

    if (add) { add.addEventListener('click', function () { addRow(null); }); }

    if (save) {
      save.addEventListener('click', function () {
        var alerts = collect();
        save.disabled = true;
        post('manage/save', { s: key, alerts: alerts, site: site && site.checked ? 1 : 0 },
          function () {
            save.disabled = false;
            said(alerts.length || (site && site.checked) ? 'manage-saved' : 'manage-none',
                 alerts.length > 0);
          });
      });
    }

    startTurnstile(function () {
      post('manage/list', { s: key }, function (data) {
        wrap.hidden = false;
        if (site) { site.checked = !!(data && data.site); }
        var held = (data && data.alerts) || [];
        held.forEach(addRow);
        if (confirmed) { said('manage-confirmed', true); }
        else if (!held.length) { said('manage-empty', false); }
        if (!held.length) { addRow(null); }
      });
    });
  }

  if (C.page === 'signup') { signup(); } else if (C.page === 'manage') { manage(); }
})();
