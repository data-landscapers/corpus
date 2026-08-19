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
 * Add a page by adding a `suite(...)` line at the foot. ZAF alone while the
 * column-width work is in flight (Bill, 2026-08-19); put all.html back when it
 * is rebuilt on the same component.
 */
import fs from 'node:fs';
import path from 'node:path';
import { JSDOM } from 'jsdom';

const CORPUS = process.env.CORPUS || '/sessions/fervent-intelligent-lovelace/mnt/CORPUS';
const JS = fs.readFileSync(path.join(CORPUS, 'site/assets/js/datatable.js'), 'utf8');

let failures = 0;
function check(label, cond, detail = '') {
  if (cond) console.log(`  ok    ${label}`);
  else { failures++; console.log(`  FAIL  ${label}${detail ? '  — ' + detail : ''}`); }
}

async function load(pageRel) {
  const pageDir = path.dirname(path.join(CORPUS, pageRel));
  const dom = new JSDOM(fs.readFileSync(path.join(CORPUS, pageRel), 'utf8'), {
    runScripts: 'outside-only', pretendToBeVisual: true,
  });
  dom.window.fetch = async (url) => {
    const p = path.join(pageDir, url);
    if (!fs.existsSync(p)) return { ok: false, status: 404, statusText: 'not found' };
    return { ok: true, status: 200, text: async () => fs.readFileSync(p, 'utf8') };
  };
  dom.window.eval(JS);
  // The component fetches, so let the microtasks and its 60 ms settle timer run.
  await new Promise(r => setTimeout(r, 300));
  return dom.window.document;
}

async function expectedRows(pageRel, doc) {
  const src = doc.querySelector('.dl-datatable').dataset.src;
  const csv = fs.readFileSync(path.join(path.dirname(path.join(CORPUS, pageRel)), src), 'utf8');
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

  check('table rendered', body.length > 0, doc.querySelector('.dt-msg')?.textContent || 'no rows');
  check(`row count matches the CSV (${want})`, body.length === want, `rendered ${body.length}`);
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
  const raw = fs.readFileSync(
    path.join(path.dirname(path.join(CORPUS, pageRel)), box.dataset.src), 'utf8');
  const wiki = [...raw.matchAll(/\[\[([^\]|]*\|)?([^\]]+)\]\]/g)].map(m => m[2]);
  const shownText = doc.querySelector('.dt-body tbody').textContent;
  check(`no [[wiki link]] is rendered (${wiki.length} in the CSV)`,
    !shownText.includes('[['), shownText.slice(shownText.indexOf('[['), shownText.indexOf('[[') + 60));
  if (wiki.length) {
    check('and the text inside them survived', shownText.includes(wiki[0]), wiki[0]);
  }

  /* Widths — the thing v1 got wrong, so the thing to assert on hardest. */
  widths(doc, box);
  await expander(doc, box);

  // Sorting: the initial data-sort must have actually been applied.
  const sorted = doc.querySelector('.dt-head thead th.sort-asc, .dt-head thead th.sort-desc');
  check('initial sort applied', !!sorted, box.dataset.sort);

  await interactions(doc, want, opts);
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
  const size = parseFloat(doc.defaultView.getComputedStyle(td).fontSize) || 16;
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
    also.forEach(f => check(`data-detail carried ${f} into the panel`, shown.includes(f)));
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
  check('a filter narrows the table', filtered > 0 && filtered < want, `${pick} -> ${filtered}`);
  check('the count says so', /of/.test(doc.querySelector('.dt-count').textContent));

  const box = doc.querySelector('.dt-search');
  box.value = 'zzzz-not-in-this-data'; box.dispatchEvent(new win.Event('input'));
  await settle(250);
  check('a search with no hits says so, rather than showing an empty table',
    doc.querySelectorAll('.dt-body tbody tr.dt-none').length === 1);

  box.value = ''; box.dispatchEvent(new win.Event('input'));
  sel.value = ''; sel.dispatchEvent(new win.Event('change'));
  await settle(250);
  check('clearing both restores every row', rows() === want, `${rows()} of ${want}`);

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

await suite("site/countries/ZAF/finance.html", { linkCol: true, labelled: false });

console.log(failures ? `\n${failures} failure(s)` : '\nall checks passed');
process.exit(failures ? 1 : 0);
