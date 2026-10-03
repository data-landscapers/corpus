/* datatable-test.mjs — a headless check of site/assets/js/datatable.js.
 *
 *   cd /tmp/dttest && npm install jsdom && node <this file>
 *
 * Loads a real built page into jsdom with a fetch() that reads the CSV off disk,
 * then asserts on the DOM the component actually produced. Not a substitute for
 * looking at it in a browser — jsdom has no layout, so nothing here can tell you
 * whether the sticky header stays put or the rows read at a comfortable depth —
 * but it does catch what silently produces a plausible-looking wrong table: a CSV
 * row torn in half by an embedded newline, a BOM that stops the first column
 * matching its name, a filter naming a column that is not there, a colgroup the
 * two tables disagree about.
 *
 * Add a page by adding a `suite(...)` line at the foot. Five today: a country's
 * finance and budget tables, and the three all-Africa tables.
 *
 * A dated edition lives in R2 and not in the tree, so a CSV the tree does not hold
 * is fetched from the live site. The table draws PAGE rows at a time; `paging`
 * holds that, and the first draw to the element ceiling `lint-page-weight.py` uses.
 *
 * The same rows are written into the page at build by `scripts/datatable_bake.py`,
 * a port of the script's row and sort code. `baked` runs over every table page in
 * the site and holds the port to the original: the rows written are the rows drawn,
 * cell for cell.
 */
import fs from 'node:fs';
import path from 'node:path';
import { JSDOM, VirtualConsole } from 'jsdom';

const CORPUS = process.env.CORPUS || '/sessions/fervent-intelligent-lovelace/mnt/CORPUS';
const JS = fs.readFileSync(path.join(CORPUS, 'site/assets/js/datatable.js'), 'utf8');
const LIVE = 'https://corpus.data-landscapers.io';
const PAGE = 100;            // rows drawn at first, and added by each "Show more"
const MAX_ELEMENTS = 3000;   // elements on a table page at first draw (Bill, ruling R110)

/* The CSV a page's `data-src` names: the tree's copy, else the live site's. */
const csvCache = new Map();
async function csvFor(pageRel, src) {
  const rel = path.posix.join(path.posix.dirname(pageRel).replace(/^site\/?/, ''), src.split('?')[0]);
  if (csvCache.has(rel)) return csvCache.get(rel);
  const local = path.join(CORPUS, 'site', rel);
  let text = null;
  if (fs.existsSync(local)) text = fs.readFileSync(local, 'utf8');
  else {
    const r = await fetch(`${LIVE}/${rel}`);
    if (r.ok) text = await r.text();
  }
  csvCache.set(rel, text);
  return text;
}

let failures = 0;
function check(label, cond, detail = '') {
  if (cond) console.log(`  ok    ${label}`);
  else { failures++; console.log(`  FAIL  ${label}${detail ? '  — ' + detail : ''}`); }
}

async function load(pageRel) {
  const dom = new JSDOM(fs.readFileSync(path.join(CORPUS, pageRel), 'utf8'), {
    runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole: new VirtualConsole(),
  });
  dom.window.fetch = async (url) => {
    const text = await csvFor(pageRel, url);
    if (text == null) return { ok: false, status: 404, statusText: 'not found' };
    return { ok: true, status: 200, text: async () => text };
  };
  const cellsOf = sel => [...dom.window.document.querySelectorAll(sel)]
    .map(tr => [...tr.cells].map(c => c.innerHTML));
  dom.window.document.baked = cellsOf('.dt-baked tbody tr');       // before the script replaces it
  dom.window.document.drawn = () => cellsOf('.dt-body tbody tr.dt-row').map(r => r.slice(1));
  dom.window.eval(JS);
  // The component fetches, so wait for the frame rather than for a fixed time.
  for (let i = 0; i < 200 && !dom.window.document.querySelector('.dt-frame, .dt-msg--err'); i++) {
    await new Promise(r => setTimeout(r, 50));
  }
  await new Promise(r => setTimeout(r, 50));
  return dom.window.document;
}

async function expectedRows(pageRel, doc) {
  const csv = await csvFor(pageRel, doc.querySelector('.dl-datatable').dataset.src) || '';
  // Count records the way csv.reader does: quote-aware, so embedded newlines
  // inside a description do not read as extra rows.
  let n = 0, inQ = false, seen = false;
  for (let i = 0; i < csv.length; i++) {
    const ch = csv[i];
    if (ch === '"') { if (inQ && csv[i + 1] === '"') i++; else inQ = !inQ; }
    else if (ch === '\n' && !inQ) { if (seen) n++; seen = false; }
    else if (ch !== '\r') seen = true;
  }
  if (seen) n++;
  return n - 1;                       // less the header
}

async function suite(pageRel, opts) {
  console.log(`\n${pageRel}`);
  const doc = await load(pageRel);
  const box = doc.querySelector('.dl-datatable');
  const body = doc.querySelectorAll('.dt-body tbody tr');
  const head = doc.querySelectorAll('.dt-head thead th');
  const want = await expectedRows(pageRel, doc);
  const first = Math.min(PAGE, want);

  check('table rendered', body.length > 0, doc.querySelector('.dt-msg')?.textContent || 'no rows');
  if (!body.length) return;
  check(`first draw is ${first} of the CSV's ${want}`, body.length === first, `rendered ${body.length}`);
  const elements = doc.querySelectorAll('*').length;
  check(`first draw is under ${MAX_ELEMENTS} elements (${elements})`, elements <= MAX_ELEMENTS);
  check('every row has a full set of cells',
    [...body].every(tr => tr.cells.length === head.length),
    `header has ${head.length}`);
  check('no header carries a BOM', ![...head].some(th => th.textContent.charCodeAt(0) === 0xFEFF));

  const filters = doc.querySelectorAll('.dt-filter');
  const asked = (box.dataset.filters || '').split(',').filter(Boolean).length;
  check(`every requested filter got a dropdown (${asked})`, filters.length === asked,
    `built ${filters.length}`);
  check('search box built', !!doc.querySelector('.dt-search'));
  check('count reads as rows', /row/.test(doc.querySelector('.dt-count').textContent));

  if (opts.linkCol) {
    const links = doc.querySelectorAll('.dt-body tbody a[href^="http"]');
    check('url column renders as links', links.length > 0, `${links.length} links`);
  }
  if (opts.labelled) {
    const opt = [...doc.querySelectorAll('.dt-filter')][0].options[1];
    check('country filter shows names, holds codes',
      opt.value.length === 3 && opt.textContent.length > 3,
      `${opt.value} -> ${opt.textContent}`);
  }
  check('cells are wrapped for clamping', doc.querySelectorAll('.dt-body .dt-cell').length > 0);

  /* Wiki-link syntax must not reach a reader. ZAF's data carries one; the CSV
   * still holds it, because published editions are not rewritten, so this checks
   * the render — that the brackets are gone and the text inside them survived. */
  const raw = await csvFor(pageRel, box.dataset.src);
  const wiki = [...raw.matchAll(/\[\[([^\]|]*\|)?([^\]]+)\]\]/g)].map(m => m[2]);
  const shownText = doc.querySelector('.dt-body tbody').textContent;
  check(`no [[wiki link]] is rendered (${wiki.length} in the CSV)`,
    !shownText.includes('[['), shownText.slice(shownText.indexOf('[['), shownText.indexOf('[[') + 60));
  if (wiki.length && want <= PAGE) {
    check('and the text inside them survived', shownText.includes(wiki[0]), wiki[0]);
  }

  /* Widths — the thing v1 got wrong, so the thing to assert on hardest. */
  widths(doc, box);
  await expander(doc, box);

  // Sorting: the initial data-sort must have actually been applied.
  const sorted = doc.querySelector('.dt-head thead th.sort-asc, .dt-head thead th.sort-desc');
  check('initial sort applied', !!sorted, box.dataset.sort);

  await interactions(doc, want, opts);
  await paging(doc, want);
}

/* A hundred rows at a time. Filter, sort and search still run over every row; what
 * is held to PAGE is what is drawn, and anything that reorders the rows goes back
 * to the first PAGE. */
async function paging(doc, total) {
  const win = doc.defaultView;
  const drawn = () => doc.querySelectorAll('.dt-body tbody tr.dt-row').length;
  const count = () => doc.querySelector('.dt-count').textContent;
  const more = doc.querySelector('.dt-more'), btn = more.querySelector('button');
  const click = () => btn.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  const n = v => v.toLocaleString();

  if (total <= PAGE) {
    check('no "Show more" on a table that fits in one draw', more.hidden);
    check('the count is the row count', count() === `${n(total)} ${total === 1 ? 'row' : 'rows'}`, count());
    return;
  }
  check('the count reads drawn of total', count() === `${PAGE} of ${n(total)} rows`, count());
  const step = Math.min(PAGE, total - PAGE);
  check('"Show more" says how many it adds', !more.hidden && btn.textContent === `Show ${step} more`,
    btn.textContent);

  doc.querySelector('.dt-body tbody tr.dt-row').dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  click();
  check(`and adds them (${PAGE + step})`, drawn() === PAGE + step, `${drawn()} drawn`);
  check('a detail panel open above survives the append', !!doc.querySelector('.dt-body tr.dt-detail'));
  const rows = doc.querySelectorAll('.dt-body tbody tr.dt-row');
  check('appended rows carry their place in the order',
    +rows[rows.length - 1].dataset.i === PAGE + step - 1, rows[rows.length - 1].dataset.i);

  doc.querySelector('.dt-head thead th:nth-child(2)').dispatchEvent(new win.Event('click'));
  check('a sort returns to the first draw', drawn() === PAGE && !more.hidden, `${drawn()} drawn`);

  click();
  const box = doc.querySelector('.dt-search');
  box.value = 'zzzz-not-in-this-data'; box.dispatchEvent(new win.Event('input'));
  await new Promise(r => setTimeout(r, 250));
  check('a search with no hits hides the control',
    more.hidden && count() === `0 rows, filtered from ${n(total)}`, count());
  box.value = ''; box.dispatchEvent(new win.Event('input'));
  await new Promise(r => setTimeout(r, 250));
  check('clearing the search returns to the first draw', drawn() === PAGE, `${drawn()} drawn`);

  click();
  const sel = doc.querySelector('.dt-filter');
  sel.value = sel.options[1].value; sel.dispatchEvent(new win.Event('change'));
  check('a filter returns to the first draw',
    drawn() <= PAGE && count().endsWith(`, filtered from ${n(total)}`), `${drawn()} drawn, ${count()}`);
  sel.value = ''; sel.dispatchEvent(new win.Event('change'));
}

/* The column widths, which v1 left to the browser and got badly wrong: a column
 * of blanks with one unbreakable token in it collapsed to about a character wide
 * and stacked vertically, setting the depth of every row. jsdom has no layout, so
 * what can be checked here is the arithmetic the script committed to — the
 * <colgroup> it wrote and whether the two tables agree — not how it looks. */
function widths(doc, box) {
  const cgs = [...doc.querySelectorAll('.dl-datatable colgroup')];
  check('both tables carry a colgroup', cgs.length === 2);

  const px = cg => [...cg.children].map(c => parseFloat(c.style.width));
  const [head, body] = cgs.map(px);
  check('header and body widths are identical',
    head.length === body.length && head.every((w, i) => w === body[i]),
    `${head.length} vs ${body.length} columns`);
  check('every width is a real number', body.every(w => w > 0 && isFinite(w)),
    JSON.stringify(body));

  const cols = (box.dataset.cols || '').split(',').map(s => s.trim()).filter(Boolean);
  if (cols.length) {
    check('one <col> per visible column, plus the expander',
      body.length === cols.length + 1, `${body.length} cols for ${cols.length} columns`);
  }
  const dataCols = body.slice(1);
  const td0 = doc.querySelector('.dt-body td');
  const cellPad = (parseFloat(doc.defaultView.getComputedStyle(td0).paddingLeft) || 0) * 2;
  check('no column is a sliver', Math.min(...dataCols) >= 66,
    `narrowest ${Math.min(...dataCols)}px`);
  check('no column exceeds the ceiling', Math.max(...dataCols) <= 500 + cellPad + 1,
    `widest ${Math.max(...dataCols)}px against MAX_W 500 + ${cellPad} padding`);

  const total = body.reduce((a, b) => a + b, 0);
  const declared = parseFloat(doc.querySelector('.dt-body').style.width);
  check('the table is as wide as its columns', Math.abs(total - declared) < 1,
    `${total} vs ${declared}`);
  check('the top scrollbar spans the same width',
    Math.abs(parseFloat(doc.querySelector('.dt-scroll-top__inner').style.width) - declared) < 1);
  console.log(`        widths: ${dataCols.join(', ')}  (total ${Math.round(total)}px)`);

  /* The property the widths exist to produce: nine rows in ten read in three
   * lines or fewer. A column is allowed to miss it only by being at the ceiling,
   * where no width would have satisfied it — `description` is the whole of that
   * case, and is why the detail panel exists. */
  const td = doc.querySelector('.dt-body td');
  const size = parseFloat(doc.defaultView.getComputedStyle(td).fontSize) || 14;   // the component's fallback
  const pad = (parseFloat(doc.defaultView.getComputedStyle(td).paddingLeft) || 0) * 2;
  const m = s => String(s || '').length * size * 0.52, sp = m(' ');
  const lines = (t, w) => {
    let n = 1, x = 0;
    for (const word of String(t || '').split(/\s+/).filter(Boolean)) {
      let mw = m(word);
      if (x > 0 && x + sp + mw <= w) { x += sp + mw; continue; }
      if (x > 0) { n++; x = 0; }
      while (mw > w) { mw -= w; n++; }
      x = mw;
    }
    return n;
  };
  const rows = [...doc.querySelectorAll('.dt-body tbody tr.dt-row')];
  const atCeiling = [], missed = [];
  dataCols.forEach((w, i) => {
    const over = rows.filter(tr => lines(tr.cells[i + 1].textContent, w - pad) > 3).length;
    if (over / rows.length <= 0.1) return;
    (w - pad >= 280 ? atCeiling : missed).push(`${cols[i] || i} ${Math.round(over / rows.length * 100)}%`);
  });
  check('nine rows in ten read in three lines or fewer', missed.length === 0, missed.join(', '));
  if (atCeiling.length) console.log(`        clamped by the ceiling: ${atCeiling.join(', ')} — these are the click-into columns`);

  /* No word is broken across lines. Counting lines does not on its own catch this:
   * a cell holding the single word "Connectivity" satisfies a three-line rule by
   * breaking after "Connectivit", which is not fitting. Link columns are exempt —
   * a URL is one unbreakable word and break-all is right for it. */
  const links = (box.dataset.links || '').split(',').map(s => s.trim()).filter(Boolean);
  const broken = [];
  dataCols.forEach((w, i) => {
    if (links.includes(cols[i])) return;
    if (w - pad >= 500) return;          // at the ceiling: break-word is all that is left
    let longest = 0, word = '';
    rows.forEach(tr => tr.cells[i + 1].textContent.split(/[\s\/]+/).forEach(t => {
      if (m(t) > longest) { longest = m(t); word = t; }
    }));
    if (longest > w - pad) broken.push(`${cols[i] || i} "${word}" needs ${Math.ceil(longest)}px in ${Math.round(w - pad)}px`);
  });
  check('no column is narrower than its longest word', broken.length === 0, broken.join('; '));
}

/* The row expander: what the columns leave out has to actually be in it. */
async function expander(doc, box) {
  const win = doc.defaultView;
  const tr = doc.querySelector('.dt-body tbody tr.dt-row');
  check('rows are marked as expandable', !!tr);
  if (!tr) return;

  tr.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  await new Promise(r => setTimeout(r, 20));
  const det = tr.nextElementSibling;
  check('clicking a row opens a detail panel', det && det.classList.contains('dt-detail'));

  const cols = (box.dataset.cols || '').split(',').map(s => s.trim()).filter(Boolean);
  const also = (box.dataset.detail || '').split(',').map(s => s.trim()).filter(Boolean);
  if (cols.length && det) {
    const shown = [...det.querySelectorAll('dt')].map(d => d.textContent);
    check('the panel holds fields the columns leave out', shown.length > 0, `${shown.length} fields`);
    // A column may appear in the panel too, but only by being named in data-detail:
    // `description` is clamped in the table and has to be readable somewhere.
    const repeats = shown.filter(f => cols.includes(f) && !also.includes(f));
    check('and repeats a column only where data-detail asks it to',
      repeats.length === 0, repeats.join(', '));
    // The panel leaves out a field this row holds nothing in, so one is enough.
    if (also.length) {
      check('data-detail carried its fields into the panel', also.some(f => shown.includes(f)),
        `asked ${also.join(', ')}; shown ${shown.join(', ')}`);
    }
    check('the panel spans the whole table',
      +det.querySelector('td').getAttribute('colspan') === cols.length + 1);
  }

  tr.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  await new Promise(r => setTimeout(r, 20));
  check('clicking again closes it',
    !tr.nextElementSibling || !tr.nextElementSibling.classList.contains('dt-detail'));
}

/* Filtering, searching and sorting, driven through the same events a reader
 * generates. The search box is debounced, so each step waits it out. */
async function interactions(doc, want, opts) {
  const win = doc.defaultView;
  const rows = () => doc.querySelectorAll('.dt-body tbody tr').length;
  const settle = ms => new Promise(r => setTimeout(r, ms));
  const label = i => [...doc.querySelectorAll('.dt-head th')]
    .findIndex(th => th.textContent.replace(/[​↕▲▼\s]/g, '') === i);
  const cells = i => [...doc.querySelectorAll('.dt-body tbody tr')].map(r => r.cells[i].textContent);

  const sel = doc.querySelector('.dt-filter');
  const pick = sel.options[1].value;
  sel.value = pick; sel.dispatchEvent(new win.Event('change'));
  await settle(30);
  const filtered = rows();
  check('a filter narrows the table, and the count says so',
    filtered > 0 && /filtered from/.test(doc.querySelector('.dt-count').textContent),
    `${pick} -> ${filtered}, ${doc.querySelector('.dt-count').textContent}`);

  const box = doc.querySelector('.dt-search');
  box.value = 'zzzz-not-in-this-data'; box.dispatchEvent(new win.Event('input'));
  await settle(250);
  check('a search with no hits says so, rather than showing an empty table',
    doc.querySelectorAll('.dt-body tbody tr.dt-none').length === 1);

  box.value = ''; box.dispatchEvent(new win.Event('input'));
  sel.value = ''; sel.dispatchEvent(new win.Event('change'));
  await settle(250);
  check('clearing both restores the first draw', rows() === Math.min(PAGE, want), `${rows()} of ${want}`);

  const mi = label('commitment_usd_m');
  if (mi > -1) {
    const th = doc.querySelectorAll('.dt-head th')[mi];
    th.dispatchEvent(new win.Event('click')); await settle(30);
    const asc = cells(mi).filter(Boolean).map(Number);
    th.dispatchEvent(new win.Event('click')); await settle(30);
    const desc = cells(mi);
    const descNums = desc.filter(v => v !== '').map(Number);
    check('a numeric column sorts as numbers, not as text',
      asc.every((v, i) => i === 0 || asc[i - 1] <= v)
      && descNums.every((v, i) => i === 0 || descNums[i - 1] >= v),
      `asc head ${asc.slice(0, 3)}, desc head ${descNums.slice(0, 3)}`);
    check('blank amounts sort last, not as zero',
      desc.findIndex(v => v === '') === -1 || desc.slice(desc.findIndex(v => v === '')).every(v => v === ''),
      'a missing figure is not a small one');
  }
}

/* Every table page: what the build wrote is what the script draws. The port sorts
 * text by folding case and accents where the browser collates by locale, so this is
 * where a name the two order differently would show. */
async function baked() {
  const pages = [];
  (function walk(dir) {
    for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, f.name);
      if (f.isDirectory()) walk(p);
      else if (f.name.endsWith('.html') && fs.readFileSync(p, 'utf8').includes('class="dl-datatable"')) {
        pages.push(path.relative(CORPUS, p).split(path.sep).join('/'));
      }
    }
  })(path.join(CORPUS, 'site'));

  console.log(`\nbaked rows, ${pages.length} table pages`);
  const wrong = [];
  for (const rel of pages) {
    const doc = await load(rel);
    const was = doc.baked, now = doc.drawn();
    if (!was.length) wrong.push(`${rel}: no rows written into the page`);
    else if (doc.querySelector('.dt-baked')) wrong.push(`${rel}: the written rows were not replaced`);
    else {
      const at = was.findIndex((r, i) => JSON.stringify(r) !== JSON.stringify(now[i]));
      if (was.length !== now.length || at > -1) {
        wrong.push(`${rel}: row ${at}, written ${JSON.stringify(was[at])?.slice(0, 160)}, drawn ${JSON.stringify(now[at])?.slice(0, 160)}`);
      }
    }
    doc.defaultView.close();
  }
  check('every page carries its first rows, and they are the rows the script draws',
    wrong.length === 0, `${wrong.length} page(s)\n        ` + wrong.slice(0, 12).join('\n        '));
}

await baked();
await suite("site/countries/ZAF/finance.html", { linkCol: true, labelled: false });
await suite("site/countries/NGA/budgets.html", { linkCol: false, labelled: false });
await suite("site/finance/index.html", { linkCol: true, labelled: true });
await suite("site/finance/budgets/index.html", { linkCol: false, labelled: true });
await suite("site/finance/all/index.html", { linkCol: false, labelled: true });

console.log(failures ? `\n${failures} failure(s)` : '\nall checks passed');
process.exit(failures ? 1 : 0);
