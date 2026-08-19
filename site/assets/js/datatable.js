/* datatable.js — the shared data table for data-landscapers and Corpus. v3 (2026-08-19)

   **This file is canonical.** It lives in `data-landscapers/assets/shared/` and
   Corpus carries a copy at `site/assets/js/datatable.js` with a `DATATABLE-FROM`
   marker naming the commit; `Corpus/scripts/lint-shared-assets.py` reports drift.
   Change it here, never there — a fix made downstream is a fix this site never
   gets, and the next copy down reverts it in silence.

   No inline styling: every rule is in the datatable.css beside this file, over
   main.css's variables. No dataset-specific code either — everything is driven by
   data-* attributes on the container.

   Markup contract:

     <div class="dl-datatable"
          data-src="data-centres-v2-display.csv"   the CSV to fetch (required)
          data-cols="a,b,c"                        visible columns, in order (default: all)
          data-filters="country_name,sector"       columns to give a dropdown
          data-numeric="commitment_usd_m,year"     sort these as numbers
          data-links="url"                         render these as links
          data-labels='{"recipient_country":{"ZAF":"South Africa"}}'
          data-badges='{"sovereignty_category":{"Fully African":"green"}}'
          data-detail="description"                also show these in the row panel
          data-sort="start_year:desc"              initial sort
          data-title="Africa data centre mapping"  toolbar heading
          data-full-src="data-centres-v2.csv"      offer the full dataset too
          data-metadata-src="...-metadata.csv"     offer the field dictionary
          data-min-col-width="120"                 floor under every column
          data-empty="Nothing matches those filters.">
       <noscript>...</noscript>
     </div>

   **The toolbar can come from either side.** Where the page supplies a
   `.dt-controls` block — Corpus does, because its download links are dated
   editions whose filenames the page knows and the browser does not, and because a
   reader with JavaScript off still needs them — this script fills in the filters
   and the search box and leaves the rest alone. Where the page supplies none, as
   every Lab and post page does, it builds the whole bar from `data-title`,
   `data-src`, `data-full-src` and `data-metadata-src`.

   ── v2, after Bill read the first one on screen (2026-08-19) ──────────────────

   v1 let the browser distribute the column widths. That is the wrong instrument
   for this data. With twenty columns in a 980px page the browser squeezes every
   column to its minimum content width, and a column like `project_id` — blank in
   61% of ZAF's rows, and a single unbreakable 22-character token in the rest —
   collapses to roughly one character wide and stacks vertically, setting the depth
   of every row it appears in. The header misaligned for the same reason: the two
   tables were sized independently and disagreed.

   So v2 measures the text and decides the widths itself, then fixes them:

     - Column widths are computed from the data (`columnWidth`), sized so that
       every cell fits in three lines and no word is broken, floored by the
       header's own longest word and by MIN_W, and capped at MAX_W. The
       table is then `table-layout: fixed` with an explicit <colgroup>, which the
       header and body tables share — identical widths by construction, so they
       cannot drift apart the way v1's measure-after-render sync could.
     - Every cell clamps to three lines, so row depth is uniform and the table
       scans downward cleanly.
     - The full record is one click away rather than spread sideways: clicking a
       row opens a detail panel beneath it carrying every field the columns leave
       out, in full, unclamped.
     - There is a real scrollbar above the header as well as below the body, both
       driving the same scroll. v1 had neither — the red line under the header that
       looked like one was a 2px border.

   The CSV parser is a character scan rather than a line split, because 44 cells in
   the all-Africa finance export carry newlines inside quoted fields and a
   line-splitting parser tears those rows in half without saying so.
*/
(function () {
  'use strict';

  var ZWSP = '​';        // zero-width space: lets a header wrap at its underscores
  var LINES = 3;          // no cell should need more than this many lines
  var FIT = 1;            // ...and this share of a column's cells must manage it
  var MIN_W = 66;         // px, before padding — narrower than this reads as a sliver
  var MAX_W = 500;        // px, the ceiling; only a column that cannot fit reaches it

  /* ── CSV ──────────────────────────────────────────────────────────────── */
  function parseCSV(text) {
    if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1);          // strip BOM
    text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    var rows = [], row = [], cur = '', inQ = false;
    for (var i = 0; i < text.length; i++) {
      var ch = text[i];
      if (inQ) {
        if (ch !== '"') { cur += ch; }
        else if (text[i + 1] === '"') { cur += '"'; i++; }
        else { inQ = false; }
      } else if (ch === '"') { inQ = true; }
      else if (ch === ',') { row.push(cur.trim()); cur = ''; }
      else if (ch === '\n') { row.push(cur.trim()); rows.push(row); row = []; cur = ''; }
      else { cur += ch; }
    }
    if (cur !== '' || row.length) { row.push(cur.trim()); rows.push(row); }
    var headers = (rows.shift() || []).map(function (h) { return h.trim(); });
    rows = rows.filter(function (r) {
      return r.some(function (c) { return c !== ''; });
    });
    return { headers: headers, rows: rows };
  }

  /* ── small helpers ────────────────────────────────────────────────────── */
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function norm(s) {
    return String(s).toLowerCase().replace(/[\s\-\/]+/g, '_')
      .replace(/_+/g, '_').replace(/^_|_$/g, '');
  }

  function list(attr) {
    return (attr || '').split(',').map(function (s) { return s.trim(); }).filter(Boolean);
  }

  function findCol(headers, name) {
    var n = norm(name);
    for (var i = 0; i < headers.length; i++) if (norm(headers[i]) === n) return i;
    return -1;
  }

  /* Blanks sort last in both directions — a missing amount is not a small one. */
  function numOf(v) {
    if (v == null || v === '') return null;
    var n = parseFloat(String(v).replace(/[, ]/g, ''));
    return isNaN(n) ? null : n;
  }

  function fmtCount(shown, total) {
    var r = total === 1 ? ' row' : ' rows';
    return shown === total
      ? total.toLocaleString() + r
      : shown.toLocaleString() + ' of ' + total.toLocaleString() + r;
  }

  /* A URL is shown as host + a trimmed tail; the full thing sits in the title. */
  function linkCell(url) {
    var label = url.replace(/^https?:\/\//, '').replace(/\/$/, '');
    if (label.length > 64) label = label.slice(0, 63) + '…';
    return '<a href="' + esc(url) + '" target="_blank" rel="noopener noreferrer" title="'
      + esc(url) + '">' + esc(label) + '</a>';
  }

  function debounce(fn, ms) {
    var t;
    return function () { clearTimeout(t); t = setTimeout(fn, ms); };
  }

  /* `[[target|label]]` -> `label`, `[[target]]` -> `target`.

     Wiki-link syntax is how the source records cross-reference each other, and it
     has no business reaching a reader of a table *(Bill, 2026-08-19, having found
     `[[2025-03-06-microsoft-zaf-azure-…]]` in a description cell)*. Applied on
     display rather than only in the compile because the CSVs already published are
     dated editions and are not rewritten; until the next compile the table will
     therefore read slightly cleaner than the file it was drawn from, in five of
     1,257 rows. Unconditional, and no attribute turns it on: there is no dataset
     on either site for which showing the brackets is the wanted behaviour. */
  function dewiki(s) {
    if (s.indexOf('[[') === -1) return s;
    return s.replace(/\[\[[^\]|]*\|([^\]]+)\]\]/g, '$1').replace(/\[\[([^\]]+)\]\]/g, '$1');
  }

  /* A download link, styled as the site's button. Written as an anchor rather
     than a button with a click handler so that it survives with JavaScript
     disabled and can be copied, opened in a tab, or right-clicked like any link. */
  function downloadLink(href, label) {
    var a = document.createElement('a');
    a.className = 'btn';
    a.href = href;
    a.setAttribute('download', '');
    a.innerHTML = '&darr; ' + esc(label);
    return a;
  }

  /* The toolbar, where the page has not supplied one. Corpus writes its own
     because its download filenames are dated editions it alone knows; the Lab
     pages give the script a bare div and expect the bar to appear. */
  function ensureControls(container) {
    var bar = container.querySelector('.dt-controls');
    if (bar) return bar;

    bar = document.createElement('div');
    bar.className = 'dt-controls';

    if (container.dataset.title) {
      var t = document.createElement('span');
      t.className = 'dt-title';
      t.textContent = container.dataset.title.trim();
      bar.appendChild(t);
    }
    var count = document.createElement('span');
    count.className = 'dt-count';
    bar.appendChild(count);

    if (container.dataset.src) bar.appendChild(downloadLink(container.dataset.src, 'CSV'));
    if (container.dataset.fullSrc) bar.appendChild(downloadLink(container.dataset.fullSrc, 'Full dataset'));
    if (container.dataset.metadataSrc) bar.appendChild(downloadLink(container.dataset.metadataSrc, 'Metadata'));

    container.insertBefore(bar, container.firstChild);
    return bar;
  }

  /* ── measuring text ───────────────────────────────────────────────────────
     A canvas gives the real advance width of a string in a given font, which a
     character count cannot: the body face is proportional, so `iiii` and `WWWW`
     are the same four characters and nowhere near the same width. The font is
     read off the rendered cells rather than assumed, so the CSS stays the one
     place the type is decided. */
  function measurer(el) {
    var cs = getComputedStyle(el);
    var size = parseFloat(cs.fontSize) || 14;
    var ctx = null;
    try { ctx = document.createElement('canvas').getContext('2d'); } catch (e) { ctx = null; }
    if (!ctx || !ctx.measureText) {
      // No canvas — a headless runner, or a browser with it switched off. Fall
      // back to the average advance of the face at this size. Cruder, but the
      // widths stay in the right order of magnitude rather than collapsing.
      return function (s) { return String(s || '').length * size * 0.52; };
    }
    ctx.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
    return function (s) { return ctx.measureText(String(s || '')).width; };
  }

  function padOf(el) {
    var cs = getComputedStyle(el);
    return parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
  }

  function longestWord(s) {
    var best = '';
    String(s || '').split(/[\s\/]+/).forEach(function (w) { if (w.length > best.length) best = w; });
    return best;
  }

  /* How many lines a cell takes at a given width — greedy word wrap, the same way
     the browser does it, with `overflow-wrap: break-word` for a word too long to
     fit at all. Counting lines is the only honest way to size for depth: a
     character count cannot see that "Development Bank of Southern Africa" packs
     into three short lines while one 34-character identifier packs into none. */
  function linesAt(words, widths, spaceW, width) {
    var lines = 1, x = 0;
    for (var i = 0; i < words.length; i++) {
      var w = widths[i];
      if (x > 0 && x + spaceW + w <= width) { x += spaceW + w; continue; }
      if (x > 0) { lines++; x = 0; }
      while (w > width) { w -= width; lines++; }      // break-word takes it apart
      x = w;
    }
    return lines;
  }

  /* The width one column should get.

     The rule is stated as the thing actually wanted — *no cell should need more
     than three lines* — and solved for, rather than approximated by a character
     count. For each candidate width the sampled cells are wrapped and their lines
     counted; the answer is the narrowest width at which FIT of them come in at or
     under LINES. Binary search over [MIN_W, MAX_W], because the share fitting
     rises monotonically with width.

     FIT is 1: **a column is sized for its longest cell, not its typical one**
     *(Bill, 2026-08-19, replacing the 90th percentile v2 shipped with)*. Sizing to
     the ninth decile is sizing for the average reader rather than for the record
     in front of them, and it truncates exactly the rows most worth reading — the
     long ones. Horizontal scrolling is the cheaper cost.

     Three floors sit under it. MIN_W, below which a column reads as a sliver. The
     header's own longest word, so a label never stacks one letter per line. And
     **the longest word in the data**, because counting lines is not on its own
     enough: a cell holding the single word "Connectivity" satisfies a three-line
     rule perfectly well by breaking after "Connectivit", which is not what anyone
     means by fitting *(Bill, 2026-08-19 — the `sector` column, one character
     short)*. A word is the unit that must not be broken; the line count governs
     what happens between words. Link columns are exempt, because a URL is one
     unbreakable word 180 characters long and `word-break: break-all` is the
     correct treatment for it.
     The ceiling MAX_W is the one place truncation survives, and on this data it
     binds on `description` alone — 518 characters in a median row, which at three
     lines wants 2,600px, a column wider than the screen it would be read on. So
     description is clamped at the ceiling and carried in full in the detail panel
     as well, and every other column shows everything it holds. */
  function columnWidth(header, values, mText, mHead, pad, breakAnywhere) {
    var headMin = mHead(longestWord(header.replace(/_/g, ' '))) + 18;   // + sort arrow
    var spaceW = mText(' ');

    var cells = [], wordFloor = 0, step = Math.max(1, Math.ceil(values.length / 400));
    for (var i = 0; i < values.length; i += step) {
      if (!values[i]) continue;
      var words = String(values[i]).split(/\s+/).filter(Boolean);
      var widths = words.map(mText);
      cells.push({ w: words, m: widths });
      if (!breakAnywhere) {
        for (var j = 0; j < widths.length; j++) {
          if (widths[j] > wordFloor) wordFloor = widths[j];
        }
      }
    }
    wordFloor = wordFloor ? wordFloor + 1 : 0;     // a pixel of slack for hinting
    if (!cells.length) return Math.ceil(Math.max(MIN_W, headMin) + pad);

    function share(width) {
      var ok = 0;
      for (var j = 0; j < cells.length; j++) {
        if (linesAt(cells[j].w, cells[j].m, spaceW, width) <= LINES) ok++;
      }
      return ok / cells.length;
    }

    var lo = MIN_W, hi = MAX_W;
    if (share(hi) < FIT) lo = hi;                       // no width satisfies it
    else {
      for (var k = 0; k < 9 && hi - lo > 4; k++) {
        var mid = (lo + hi) / 2;
        if (share(mid) >= FIT) hi = mid; else lo = mid;
      }
      lo = hi;
    }
    return Math.ceil(Math.min(MAX_W, Math.max(lo, headMin, wordFloor, MIN_W)) + pad);
  }

  /* ── one table ────────────────────────────────────────────────────────── */
  function build(container) {
    var src = container.dataset.src;
    if (!src) { container.insertAdjacentHTML('beforeend', '<p class="dt-msg dt-msg--err">No data-src set.</p>'); return; }

    var emptyMsg = container.dataset.empty || 'Nothing matches those filters.';
    var labels = {};
    if (container.dataset.labels) {
      try { labels = JSON.parse(container.dataset.labels); } catch (e) { labels = {}; }
    }

    var controls = ensureControls(container);
    var countEl = container.querySelector('.dt-count');
    var minColW = parseFloat(container.dataset.minColWidth) || 0;
    var msg = document.createElement('p');
    msg.className = 'dt-msg';
    msg.textContent = 'Loading data…';
    container.appendChild(msg);

    fetch(src)
      .then(function (r) { if (!r.ok) throw new Error(r.status + ' ' + r.statusText); return r.text(); })
      .then(function (text) {
        var parsed = parseCSV(text);
        var headers = parsed.headers, rows = parsed.rows;

        var wanted = list(container.dataset.cols);
        var cols = wanted.length
          ? wanted.map(function (c) { return findCol(headers, c); }).filter(function (i) { return i > -1; })
          : headers.map(function (_, i) { return i; });
        /* What the detail panel shows: every field the columns leave out, plus any
           named in `data-detail`. A column can be in both — `description` is
           clamped at the ceiling in the table and needs somewhere to be read in
           full, and that somewhere is the panel it is already opening. */
        var alsoDetail = list(container.dataset.detail)
          .map(function (c) { return findCol(headers, c); })
          .filter(function (i) { return i > -1; });
        var detailCols = headers.map(function (_, i) { return i; })
          .filter(function (i) { return cols.indexOf(i) === -1 || alsoDetail.indexOf(i) > -1; });

        var numeric = {};
        list(container.dataset.numeric).forEach(function (c) {
          var i = findCol(headers, c); if (i > -1) numeric[i] = true;
        });
        var linkCols = {};
        list(container.dataset.links).forEach(function (c) {
          var i = findCol(headers, c); if (i > -1) linkCols[i] = true;
        });
        var labelFor = {};                       // column index -> code->label map
        Object.keys(labels).forEach(function (c) {
          var i = findCol(headers, c); if (i > -1) labelFor[i] = labels[c];
        });
        /* One place decides what a value looks like, so the cells, the filter
           options, the sort keys and the search all agree about it. */
        function display(ci, v) { return dewiki((labelFor[ci] && labelFor[ci][v]) || v); }

        /* Badges: a column whose values are a small closed set worth reading as a
           status rather than as text. The mapping is given, never inferred — the
           colours carry meaning here (green for African control, red for US/CN),
           and a palette assigned by sort order would attach that meaning at
           random. A value not in the map renders as ordinary text. */
        var badges = {};
        if (container.dataset.badges) {
          try {
            var spec = JSON.parse(container.dataset.badges);
            Object.keys(spec).forEach(function (c) {
              var i = findCol(headers, c); if (i > -1) badges[i] = spec[c];
            });
          } catch (e) { badges = {}; }
        }

        var filterCols = list(container.dataset.filters)
          .map(function (c) { return findCol(headers, c); })
          .filter(function (i) { return i > -1; });
        var filterState = {};
        filterCols.forEach(function (i) { filterState[i] = ''; });

        var sortCol = -1, sortAsc = true;
        if (container.dataset.sort) {
          var bits = container.dataset.sort.split(':');
          var si = findCol(headers, bits[0]);
          if (si > -1 && cols.indexOf(si) > -1) {
            sortCol = cols.indexOf(si);
            sortAsc = bits[1] !== 'desc';
          }
        }
        var search = '';

        /* ── controls: filters and search, injected before the count ─────── */
        function uniq(ci) {
          var seen = {}, out = [];
          rows.forEach(function (r) {
            var v = r[ci];
            if (v && !seen[v]) { seen[v] = 1; out.push(v); }
          });
          return out.sort(function (a, b) {
            return display(ci, a).localeCompare(display(ci, b));
          });
        }

        if (controls) {
          filterCols.forEach(function (ci) {
            var values = uniq(ci);
            if (values.length < 2) return;
            var sel = document.createElement('select');
            sel.className = 'dt-filter';
            sel.setAttribute('aria-label', 'Filter by ' + headers[ci]);
            sel.innerHTML = '<option value="">All ' + esc(headers[ci].replace(/_/g, ' ')) + '</option>'
              + values.map(function (v) {
                  var lab = display(ci, v);
                  if (lab.length > 60) lab = lab.slice(0, 59) + '…';
                  return '<option value="' + esc(v) + '">' + esc(lab) + '</option>';
                }).join('');
            sel.addEventListener('change', function () { filterState[ci] = sel.value; render(); });
            controls.insertBefore(sel, countEl);
          });

          var box = document.createElement('input');
          box.type = 'search';
          box.className = 'dt-search';
          box.placeholder = 'Search…';
          box.setAttribute('aria-label', 'Search the table');
          box.addEventListener('input', debounce(function () { search = box.value; render(); }, 140));
          controls.insertBefore(box, countEl);
        }

        /* ── shape the data ──────────────────────────────────────────────── */
        function selected() {
          var q = search.trim().toLowerCase();
          return rows.filter(function (r) {
            for (var ci in filterState) {
              if (filterState[ci] && r[ci] !== filterState[ci]) return false;
            }
            if (!q) return true;
            for (var i = 0; i < headers.length; i++) {        // search every field,
              if ((r[i] || '').toLowerCase().indexOf(q) > -1) return true;   // shown or not
            }
            return false;
          });
        }

        function ordered(data) {
          if (sortCol < 0) return data;
          var ci = cols[sortCol], asNum = numeric[ci];
          return data.slice().sort(function (a, b) {
            var av = a[ci] || '', bv = b[ci] || '';
            if (av === '' && bv === '') return 0;
            if (av === '') return 1;                 // blanks last, either direction
            if (bv === '') return -1;
            var cmp;
            if (asNum) {
              var an = numOf(av), bn = numOf(bv);
              cmp = (an == null ? 0 : an) - (bn == null ? 0 : bn);
            } else {
              cmp = display(ci, av).localeCompare(display(ci, bv), undefined, { numeric: true });
            }
            return sortAsc ? cmp : -cmp;
          });
        }

        /* ── frame ────────────────────────────────────────────────────────
           Header and body are two tables, because position:sticky on a th inside
           an overflow-x container sticks to the container, which never scrolls
           vertically — so it does not stick at all. They share an identical
           <colgroup> and an identical total width, which is what keeps them in
           register; v1 measured one against the other after render and drifted. */
        var wrap = document.createElement('div');
        wrap.className = 'dt-frame';
        wrap.innerHTML =
            '<div class="dt-sticky">'
          +   '<div class="dt-scroll-top"><div class="dt-scroll-top__inner"></div></div>'
          +   '<div class="dt-head-scroll"><table class="data-table dt-head"><colgroup></colgroup>'
          +     '<thead><tr></tr></thead></table></div>'
          + '</div>'
          + '<div class="dt-body-scroll"><table class="data-table dt-body"><colgroup></colgroup>'
          +   '<tbody></tbody></table></div>';
        var scrollTop = wrap.querySelector('.dt-scroll-top');
        var scrollTopInner = wrap.querySelector('.dt-scroll-top__inner');
        var headScroll = wrap.querySelector('.dt-head-scroll');
        var bodyScroll = wrap.querySelector('.dt-body-scroll');
        var headTable = wrap.querySelector('.dt-head');
        var bodyTable = wrap.querySelector('.dt-body');
        var headRow = wrap.querySelector('.dt-head tr');
        var tbody = wrap.querySelector('.dt-body tbody');
        container.replaceChild(wrap, msg);

        /* Header cells first — the width measurement reads its fonts off them. */
        cols.forEach(function (ci, vi) {
          var th = document.createElement('th');
          th.innerHTML = esc(headers[ci]).replace(/_/g, '_' + ZWSP);
          th.tabIndex = 0;
          th.setAttribute('role', 'button');
          if (numeric[ci]) th.className = 'num';
          function flip() {
            if (sortCol === vi) sortAsc = !sortAsc; else { sortCol = vi; sortAsc = true; }
            render();
          }
          th.addEventListener('click', flip);
          th.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); flip(); }
          });
          headRow.appendChild(th);
        });
        var caretTh = document.createElement('th');
        caretTh.className = 'dt-caret';
        caretTh.setAttribute('aria-label', 'Open the full record');
        headRow.insertBefore(caretTh, headRow.firstChild);

        /* ── widths ──────────────────────────────────────────────────────── */
        tbody.innerHTML = '<tr><td>&nbsp;</td></tr>';       // a cell to measure against
        var probeTd = tbody.querySelector('td');
        var mText = measurer(probeTd), mHead = measurer(headRow.cells[1] || caretTh);
        var pad = padOf(probeTd);
        var CARET_W = 26;

        var widths = cols.map(function (ci) {
          var w = columnWidth(headers[ci], rows.map(function (r) { return display(ci, r[ci]); }),
                              mText, mHead, pad, !!linkCols[ci]);
          return minColW ? Math.max(w, minColW) : w;      // data-min-col-width is a floor
        });
        var total = widths.reduce(function (a, b) { return a + b; }, CARET_W);

        [headTable, bodyTable].forEach(function (t) {
          var cg = t.querySelector('colgroup');
          cg.innerHTML = '<col style="width:' + CARET_W + 'px">'
            + widths.map(function (w) { return '<col style="width:' + w + 'px">'; }).join('');
          t.style.width = total + 'px';
        });
        scrollTopInner.style.width = total + 'px';

        /* ── rows ────────────────────────────────────────────────────────── */
        function cellHtml(ci, v) {
          if (!v) return '';
          if (linkCols[ci]) return linkCell(v);
          var shown = display(ci, v);
          if (badges[ci]) {
            var tone = badges[ci][v] || badges[ci][shown];
            if (tone) return '<span class="dt-badge dt-badge--' + esc(tone) + '">' + esc(shown) + '</span>';
          }
          return '<span class="dt-cell">' + esc(shown) + '</span>';
        }

        var current = [];        // the rows as currently ordered, for the detail panel

        function render() {
          current = ordered(selected());

          Array.prototype.forEach.call(headRow.cells, function (th, i) {
            th.classList.remove('sort-asc', 'sort-desc');
            if (i - 1 === sortCol) th.classList.add(sortAsc ? 'sort-asc' : 'sort-desc');
          });

          if (!current.length) {
            tbody.innerHTML = '<tr class="dt-none"><td colspan="' + (cols.length + 1) + '">'
              + esc(emptyMsg) + '</td></tr>';
          } else {
            var html = new Array(current.length);
            for (var r = 0; r < current.length; r++) {
              var row = current[r];
              var tds = '<td class="dt-caret"><span aria-hidden="true">›</span></td>';
              for (var c = 0; c < cols.length; c++) {
                var ci = cols[c];
                tds += '<td' + (numeric[ci] ? ' class="num"' : '') + '>' + cellHtml(ci, row[ci]) + '</td>';
              }
              html[r] = '<tr class="dt-row" data-i="' + r + '" tabindex="0">' + tds + '</tr>';
            }
            tbody.innerHTML = html.join('');
          }

          if (countEl) countEl.textContent = fmtCount(current.length, rows.length);
        }

        /* ── the detail panel ─────────────────────────────────────────────
           Every field the columns leave out, in full and unclamped. The table
           gets to stay narrow enough to read without the record losing anything:
           what is not in a column is one click below it, not absent. */
        function detailHtml(row) {
          var dl = detailCols.map(function (ci) {
            var v = row[ci];
            if (!v) return '';
            return '<dt>' + esc(headers[ci]) + '</dt><dd>'
              + (linkCols[ci] ? linkCell(v) : esc(display(ci, v))) + '</dd>';
          }).join('');
          return '<td class="dt-detail__cell" colspan="' + (cols.length + 1) + '">'
            + (dl ? '<dl>' + dl + '</dl>' : '<p>Every field for this row is already in the table.</p>')
            + '</td>';
        }

        function toggle(tr) {
          var next = tr.nextElementSibling;
          if (next && next.classList.contains('dt-detail')) {
            next.remove();
            tr.classList.remove('dt-row--open');
            return;
          }
          var det = document.createElement('tr');
          det.className = 'dt-detail';
          det.innerHTML = detailHtml(current[parseInt(tr.dataset.i, 10)]);
          tr.after(det);
          tr.classList.add('dt-row--open');
        }

        tbody.addEventListener('click', function (e) {
          if (e.target.closest('a')) return;                 // let a link be a link
          var tr = e.target.closest('.dt-row');
          if (tr) toggle(tr);
        });
        tbody.addEventListener('keydown', function (e) {
          if (e.key !== 'Enter' && e.key !== ' ') return;
          var tr = e.target.closest && e.target.closest('.dt-row');
          if (tr) { e.preventDefault(); toggle(tr); }
        });

        /* ── scrolling ───────────────────────────────────────────────────
           Three elements scroll the same axis — the mirror above the header, the
           header, and the body — and any of them may be the one the reader grabs.
           A guard stops the sync recursing. */
        var syncing = false;
        function syncFrom(el) {
          return function () {
            if (syncing) return;
            syncing = true;
            var x = el.scrollLeft;
            if (scrollTop !== el) scrollTop.scrollLeft = x;
            if (headScroll !== el) headScroll.scrollLeft = x;
            if (bodyScroll !== el) bodyScroll.scrollLeft = x;
            syncing = false;
          };
        }
        scrollTop.addEventListener('scroll', syncFrom(scrollTop));
        bodyScroll.addEventListener('scroll', syncFrom(bodyScroll));
        headScroll.addEventListener('scroll', syncFrom(headScroll));

        /* Park the sticky bits below whatever site chrome is already sticky,
           measured rather than assumed — the nav bars differ in height by page. */
        function placeSticky() {
          var top = 0;
          ['.site-header', '.corpus-nav'].forEach(function (sel) {
            var el = document.querySelector(sel);
            if (el && getComputedStyle(el).position === 'sticky') top += el.offsetHeight;
          });
          container.style.setProperty('--dt-top', top + 'px');
          var bar = container.querySelector('.dt-controls');
          if (bar) container.style.setProperty('--dt-bar', bar.offsetHeight + 'px');
        }
        placeSticky();
        window.addEventListener('resize', debounce(placeSticky, 120));

        render();
      })
      .catch(function (err) {
        msg.className = 'dt-msg dt-msg--err';
        msg.textContent = 'Could not load ' + src + ' — ' + err.message
          + '. The CSV is still downloadable from the link above.';
      });
  }

  function init() {
    document.querySelectorAll('.dl-datatable').forEach(build);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
