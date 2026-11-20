/* whos-who.js — the Who's Who search. Corpus only; written by hand, served as is.

   `scripts/whos-who-publish.py` builds the page and the data this reads, and its
   docstring says what the files hold. `documentation/whos-who.md` §8a is the design.

   **Nothing is shown until the reader searches** (Bill, 2026-11-20): three letters
   of a name, position or organisation, a country, or an organisation. The index is
   fetched on first use, not with the page. Each search cuts the matching rows into
   a CSV in memory and hands it to the shared table (`datatable.js` v5, `data-defer`),
   which a new search replaces whole. The table's own toolbar is hidden by
   `whos-who.css`: the search here is the only one.

   **The organisation filter stands alone** (Bill, 2026-11-20): a body with no
   country, or filed under the wrong one, is still one choice away. A country narrows
   the organisations offered and never has to be chosen first.

   **No person is addressable.** The fragment carries the search, the country and
   the organisation, never a person; a name in it is a search and finds everyone of
   that name. A row is one person, position, organisation and year, and carries
   every source saying so: the panel lists them, the download joins them with `; `.
   Source URLs live in `data/src-NNN.json` blocks, fetched when a row is
   opened or the rows on screen are downloaded. */
(function () {
  'use strict';

  var MIN = 3;
  var q = document.getElementById('ww-q');
  var place = document.getElementById('ww-place');
  var org = document.getElementById('ww-org');
  var list = document.getElementById('ww-orgs');
  var dl = document.getElementById('ww-dl');
  var status = document.getElementById('ww-status');
  var results = document.getElementById('ww-results');
  var PROMPT = status.textContent;

  var D = null, loading = null;     // the index, once fetched
  var rowKey = [];                  // per row: folded name, aliases, position, organisation
  var orgKey = [];                  // folded name and abbreviations, by org index
  var orgsByName = {};              // folded name -> [org index]
  var blocks = {};                  // block number -> promise of {id: url}
  var shown = [];                   // row numbers the table currently holds, in its order

  function fold(s) {
    return String(s || '').toLowerCase().replace(/\u2019/g, "'")
      .normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, ' ').trim();
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function csvCell(v) {
    v = String(v == null ? '' : v);
    return /[",\n\r]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  }
  function csv(rows) { return rows.map(function (r) { return r.map(csvCell).join(','); }).join('\n') + '\n'; }

  function load() {
    if (loading) return loading;
    status.textContent = 'Loading…';
    loading = fetch('data/index.json')
      .then(function (r) { if (!r.ok) throw new Error(r.status + ' ' + r.statusText); return r.json(); })
      .then(function (d) {
        D = d;
        var pk = d.people.map(function (p) { return fold(p[0] + ' ' + p[1].join(' ')); });
        // An organisation is found by its name or any abbreviation (o[3]: AfDB, BAD).
        var ok = d.orgs.map(function (o) { return fold(o[0] + ' ' + (o[3] || []).join(' ')); });
        orgKey = ok;
        var tk = d.positions.map(fold);
        var R = d.rows;
        for (var i = 0; i < d.count; i++) rowKey.push(pk[R.p[i]] + ' | ' + tk[R.t[i]] + ' | ' + ok[R.o[i]]);
        d.orgs.forEach(function (o, i) {
          [o[0]].concat(o[3] || []).forEach(function (n) { (orgsByName[fold(n)] = orgsByName[fold(n)] || []).push(i); });
        });
        fillOrgs();
        return d;
      })
      .catch(function (e) {
        loading = null;
        status.textContent = 'Could not load the index (' + e.message + '). The full download still works.';
        throw e;
      });
    return loading;
  }

  /* The organisation list: every organisation, or the chosen country's. */
  function fillOrgs() {
    if (!D) return;
    var pl = place.value, seen = {}, html = [];
    D.orgs.forEach(function (o) {
      if (pl && o[1] !== pl) return;
      if (seen[o[0]]) return;
      seen[o[0]] = 1;
      html.push('<option value="' + esc(o[0]) + '">');
    });
    list.innerHTML = html.join('');
  }

  /* The organisations the box selects: an exact name, with every name its lineage
     group has had; otherwise every organisation whose name holds what was typed. */
  function orgSet() {
    var t = fold(org.value);
    if (!t) return null;
    var hit = orgsByName[t], set = {};
    if (hit) {
      var groups = {};
      hit.forEach(function (i) { groups[D.orgs[i][2]] = 1; });
      D.orgs.forEach(function (o, i) { if (groups[o[2]]) set[i] = 1; });
      return set;
    }
    if (t.length < MIN) return null;
    D.orgs.forEach(function (o, i) { if (orgKey[i].indexOf(t) > -1) set[i] = 1; });
    return set;
  }

  function active() {
    return fold(q.value).length >= MIN || place.value || fold(org.value).length >= MIN
      || (D && orgsByName[fold(org.value)]);
  }

  function writeHash() {
    var p = [];
    if (q.value.trim()) p.push('q=' + encodeURIComponent(q.value.trim()));
    if (place.value) p.push('country=' + encodeURIComponent(place.value));
    if (org.value.trim()) p.push('org=' + encodeURIComponent(org.value.trim()));
    history.replaceState(null, '', p.length ? '#' + p.join('&') : location.pathname);
  }
  function readHash() {
    (location.hash || '').replace(/^#/, '').split('&').forEach(function (kv) {
      var i = kv.indexOf('=');
      if (i < 1) return;
      var k = kv.slice(0, i), v = decodeURIComponent(kv.slice(i + 1));
      if (k === 'q') q.value = v;
      else if (k === 'country') place.value = v;
      else if (k === 'org') org.value = v;
    });
  }

  function clear(msg) {
    results.innerHTML = '';
    shown = [];
    dl.disabled = true;
    status.textContent = msg;
  }

  function run() {
    writeHash();
    if (!active()) { clear(PROMPT); return; }
    load().then(function () {
      if (!active()) { clear(PROMPT); return; }
      var words = fold(q.value).split(' ').filter(function (w) { return w.length; });
      if (fold(q.value).length < MIN) words = [];
      var pl = place.value, os = orgSet(), R = D.rows, hits = [];
      for (var i = 0; i < D.count; i++) {
        if (pl && D.orgs[R.o[i]][1] !== pl) continue;
        if (os && !os[R.o[i]]) continue;
        var k = rowKey[i], ok = true;
        for (var w = 0; w < words.length; w++) if (k.indexOf(words[w]) === -1) { ok = false; break; }
        if (ok) hits.push(i);
      }
      draw(hits);
    });
  }

  function draw(hits) {
    if (!hits.length) { clear('Nothing matches. Try fewer letters, another spelling, or no country.'); return; }
    var src = {};
    hits.forEach(function (i) { D.rows.s[i].forEach(function (k) { src[k] = 1; }); });
    status.textContent = hits.length.toLocaleString() + (hits.length === 1 ? ' row' : ' rows')
      + ' from ' + Object.keys(src).length.toLocaleString()
      + (Object.keys(src).length === 1 ? ' source.' : ' sources.');
    var R = D.rows, table = [['name', 'position', 'organisation', 'country', 'year', 'sources', 'row']];
    hits.forEach(function (i) {
      table.push([D.people[R.p[i]][0], D.positions[R.t[i]], D.orgs[R.o[i]][0], country(R.o[i]),
                  R.y[i], R.s[i].length, i]);
    });
    var url = URL.createObjectURL(new Blob([csv(table)], { type: 'text/csv' }));
    var box = document.createElement('div');
    box.className = 'dl-datatable';
    box.setAttribute('data-defer', '');
    box.dataset.src = url;
    box.dataset.cols = 'name,year,position,organisation,country,sources';
    box.dataset.numeric = 'sources';
    // 50 characters a line for the three long columns (Bill, 2026-11-20).
    box.dataset.colChars = '{"name":50,"position":50,"organisation":50}';
    box.dataset.minColWidth = '60';
    box.innerHTML = '<div class="dt-controls"><span class="dt-count"></span></div>';
    box.addEventListener('dt:render', function (e) {
      var at = e.detail.headers.indexOf('row');
      shown = e.detail.rows.map(function (r) { return +r[at]; });
      dl.disabled = !shown.length;
      URL.revokeObjectURL(url);
    });
    box.addEventListener('dt:detail', function (e) {
      panel(+e.detail.row[e.detail.row.length - 1], e.detail.cell);
    });
    results.innerHTML = '';
    results.appendChild(box);
    window.dlDatatable.build(box);
  }

  /* The organisation's country, or its region for a regional or global body. */
  function country(o) { var c = D.orgs[o][1]; return (c && D.places[c]) || c || ''; }

  function block(n) {
    if (!blocks[n]) {
      var name = 'data/src-' + ('00' + n).slice(-3) + '.json';
      blocks[n] = fetch(name).then(function (r) {
        if (!r.ok) throw new Error(r.status + ' ' + r.statusText);
        return r.json();
      }).catch(function (e) { delete blocks[n]; throw e; });
    }
    return blocks[n];
  }
  function sources(rows) {
    var need = {};
    rows.forEach(function (i) {
      D.rows.s[i].forEach(function (k) { need[Math.floor(k / D.block)] = 1; });
    });
    return Promise.all(Object.keys(need).map(function (n) { return block(+n); }))
      .then(function (maps) {
        var all = {};
        maps.forEach(function (m) { for (var k in m) all[k] = m[k]; });
        return all;
      });
  }

  /* The row panel: the source, then the ways out — this name, this organisation,
     and every held document that mentions the name. */
  function panel(i, cell) {
    var R = D.rows, name = D.people[R.p[i]][0], o = D.orgs[R.o[i]][0];
    cell.innerHTML = '<p class="ww-ways">'
      + '<a class="ww-way" href="#q=' + encodeURIComponent(name) + '" data-q="' + esc(name) + '">Every row for this name</a>'
      + '<a class="ww-way" href="#org=' + encodeURIComponent(o) + '" data-org="' + esc(o) + '">Every row for this organisation</a>'
      + '<a class="ww-way" href="../catalogue/#q=' + encodeURIComponent(name) + '">This name in the catalogue</a></p>'
      + '<dl><dt>' + (R.s[i].length > 1 ? R.s[i].length + ' sources' : 'Source')
      + '</dt><dd class="ww-src">Loading…</dd></dl>';
    sources([i]).then(function (m) {
      cell.querySelector('.ww-src').innerHTML = R.s[i].map(function (k) {
        var u = m[k];
        return u ? '<a href="' + esc(u) + '" target="_blank" rel="noopener noreferrer">' + esc(u) + '</a>'
          : 'Not found.';
      }).join('<br>');
    }, function () { cell.querySelector('.ww-src').textContent = 'Could not load the source.'; });
  }

  results.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-q], a[data-org]');
    if (!a) return;
    e.preventDefault();
    if (a.dataset.q != null) { q.value = a.dataset.q; org.value = ''; }
    else { org.value = a.dataset.org; q.value = ''; }
    place.value = '';
    fillOrgs();
    window.scrollTo({ top: 0 });
    run();
  });

  dl.addEventListener('click', function () {
    if (!shown.length) return;
    dl.disabled = true;
    var rows = shown.slice(), R = D.rows;
    sources(rows).then(function (m) {
      var out = [['name', 'year', 'position', 'organisation', 'country', 'source_url']];
      rows.forEach(function (i) {
        out.push([D.people[R.p[i]][0], R.y[i], D.positions[R.t[i]], D.orgs[R.o[i]][0], country(R.o[i]), R.s[i].map(function (k) { return m[k] || ''; }).join('; ')]);
      });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob(['\ufeff' + csv(out)], { type: 'text/csv' }));
      a.download = 'whos-who-selection.csv';
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
      dl.disabled = false;
    }, function () { dl.disabled = false; status.textContent = 'Could not load the sources for the download.'; });
  });

  /* The search bar sticks beneath the site's own sticky bars, measured as the table
     measures them. */
  var bar = document.querySelector('.ww-bar');
  function placeBar() {
    var top = 0;
    ['.site-header', '.corpus-nav'].forEach(function (sel) {
      var el = document.querySelector(sel);
      if (el && getComputedStyle(el).position === 'sticky') top += el.offsetHeight;
    });
    if (bar) bar.style.setProperty('--ww-top', top + 'px');
  }
  placeBar();
  window.addEventListener('resize', placeBar);

  var later;
  function soon() { clearTimeout(later); later = setTimeout(run, 250); }
  q.addEventListener('input', soon);
  org.addEventListener('input', soon);
  org.addEventListener('focus', function () { load().catch(function () {}); });
  place.addEventListener('change', function () { fillOrgs(); run(); });

  readHash();
  if (location.hash) run();
})();
