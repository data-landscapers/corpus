/* datatable.js — Corpus client-side data tables. v1 (2026-08-19)

   Ported from the Lab's assets/js/datatable.js (data-landscapers repo, v16) and
   rewritten for Corpus: no inline styling — every rule lives in
   assets/css/datatable.css and uses main.css's variables — and no dataset-specific
   code. One component, driven entirely by data-* attributes on the container.

   Markup contract:

     <div class="dl-datatable"
          data-src="ZAF-nonstate-2026-08-19.csv"   the CSV to fetch (required)
          data-cols="a,b,c"                        visible columns, in order (default: all)
          data-filters="financier,sector,status"   columns to give a dropdown
          data-numeric="commitment_usd_m,start_year"  sort these as numbers
          data-links="url"                         render these as links
          data-labels='{"recipient_country":{"ZAF":"South Africa"}}'
          data-clamp="220"                         clamp cells longer than this (0 = never)
          data-sort="start_year:desc"              initial sort
          data-empty="No commitments held.">
       <div class="dt-controls">
         <span class="dt-title">South Africa &mdash; non-state finance</span>
         <span class="dt-count">54 rows</span>
         <a class="btn" href="...csv" download>&darr; Download CSV</a>
       </div>
       <noscript>...</noscript>
     </div>

   The title, the row count and the download links are written server-side and left
   alone here: the download link's filename is a dated edition (RENDER.md §9), which
   the page knows and the browser does not, and a reader without JavaScript still
   needs it. This script only fills in the filters, the search box and the table.

   The CSV parser is a character scan rather than a line split, because 44 cells in
   the all-Africa finance export carry newlines inside quoted fields and a
   line-splitting parser tears those rows in half without saying so.
*/
(function () {
  'use strict';

  var ZWSP = '​';   // zero-width space: lets a header wrap at its underscores

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
    if (label.length > 48) label = label.slice(0, 47) + '…';
    return '<a href="' + esc(url) + '" target="_blank" rel="noopener noreferrer" title="'
      + esc(url) + '">' + esc(label) + '</a>';
  }

  function debounce(fn, ms) {
    var t;
    return function () {
      clearTimeout(t);
      t = setTimeout(fn, ms);
    };
  }

  /* ── one table ────────────────────────────────────────────────────────── */
  function build(container) {
    var src = container.dataset.src;
    if (!src) { container.insertAdjacentHTML('beforeend', '<p class="dt-msg dt-msg--err">No data-src set.</p>'); return; }

    var clamp = container.dataset.clamp === undefined ? 220 : parseInt(container.dataset.clamp, 10);
    var emptyMsg = container.dataset.empty || 'Nothing matches those filters.';
    var labels = {};
    if (container.dataset.labels) {
      try { labels = JSON.parse(container.dataset.labels); } catch (e) { labels = {}; }
    }

    var controls = container.querySelector('.dt-controls');
    var countEl = container.querySelector('.dt-count');
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
        function display(ci, v) {
          return (labelFor[ci] && labelFor[ci][v]) || v;
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
            for (var i = 0; i < cols.length; i++) {
              if ((r[cols[i]] || '').toLowerCase().indexOf(q) > -1) return true;
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

        /* ── the table, built once as a string: 1,257 rows x 20 columns is
              25,000 cells, and node-by-node construction on every keystroke is
              the difference between instant and visibly laggy. ─────────────── */
        var wrap = document.createElement('div');
        wrap.className = 'dt-frame';
        wrap.innerHTML =
          '<div class="dt-head-scroll"><table class="data-table dt-head"><thead><tr></tr></thead></table></div>'
          + '<div class="dt-body-scroll"><table class="data-table dt-body"><tbody></tbody></table></div>';
        var headScroll = wrap.querySelector('.dt-head-scroll');
        var bodyScroll = wrap.querySelector('.dt-body-scroll');
        var headRow = wrap.querySelector('.dt-head tr');
        var tbody = wrap.querySelector('.dt-body tbody');
        container.replaceChild(wrap, msg);

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

        function cellHtml(ci, v) {
          if (!v) return '';
          if (linkCols[ci]) return linkCell(v);
          var shown = display(ci, v);
          if (clamp > 0 && shown.length > clamp) {
            return '<span class="dt-clip" title="Click to expand">' + esc(shown) + '</span>';
          }
          return esc(shown);
        }

        function render() {
          var data = ordered(selected());

          Array.prototype.forEach.call(headRow.cells, function (th, vi) {
            th.classList.remove('sort-asc', 'sort-desc');
            if (vi === sortCol) th.classList.add(sortAsc ? 'sort-asc' : 'sort-desc');
          });

          if (!data.length) {
            tbody.innerHTML = '<tr class="dt-none"><td colspan="' + cols.length + '">'
              + esc(emptyMsg) + '</td></tr>';
          } else {
            var html = new Array(data.length);
            for (var r = 0; r < data.length; r++) {
              var row = data[r], tds = '';
              for (var c = 0; c < cols.length; c++) {
                var ci = cols[c];
                tds += '<td' + (numeric[ci] ? ' class="num"' : '') + '>' + cellHtml(ci, row[ci]) + '</td>';
              }
              html[r] = '<tr>' + tds + '</tr>';
            }
            tbody.innerHTML = html.join('');
          }

          if (countEl) countEl.textContent = fmtCount(data.length, rows.length);
          syncWidths();
        }

        /* Click any clamped cell to see all of it. */
        tbody.addEventListener('click', function (e) {
          var clip = e.target.closest && e.target.closest('.dt-clip');
          if (!clip) return;
          clip.classList.toggle('dt-clip--open');
          clip.title = clip.classList.contains('dt-clip--open') ? 'Click to collapse' : 'Click to expand';
          syncWidths();
        });

        /* ── sticky header ────────────────────────────────────────────────
           position:sticky on a th inside an overflow-x container sticks to the
           container, which never scrolls vertically — so it does not stick at
           all. The header is therefore its own table outside the scroller, with
           its column widths and horizontal scroll slaved to the body's. */
        var headTable = wrap.querySelector('.dt-head');
        var bodyTable = wrap.querySelector('.dt-body');

        function syncWidths() {
          var first = tbody.rows[0];
          if (!first || first.classList.contains('dt-none')) { headTable.style.width = ''; return; }
          headTable.style.width = bodyTable.offsetWidth + 'px';
          Array.prototype.forEach.call(first.cells, function (td, i) {
            if (headRow.cells[i]) headRow.cells[i].style.width = td.offsetWidth + 'px';
          });
          headScroll.scrollLeft = bodyScroll.scrollLeft;
        }

        bodyScroll.addEventListener('scroll', function () { headScroll.scrollLeft = bodyScroll.scrollLeft; });
        window.addEventListener('resize', debounce(syncWidths, 120));

        /* Park the header below whatever site chrome is already sticky, measured
           rather than assumed — the two nav bars differ in height by page. */
        function placeSticky() {
          var top = 0;
          ['.site-header', '.corpus-nav'].forEach(function (sel) {
            var el = document.querySelector(sel);
            if (el && getComputedStyle(el).position === 'sticky') top += el.offsetHeight;
          });
          container.style.setProperty('--dt-top', top + 'px');
        }
        placeSticky();
        window.addEventListener('resize', debounce(placeSticky, 120));

        render();
        setTimeout(syncWidths, 60);      // once webfonts have settled
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
