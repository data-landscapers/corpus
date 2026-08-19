/* datatable-test.mjs — a headless check of site/assets/js/datatable.js.
 *
 *   cd /tmp/dttest && npm install jsdom && node <this file>
 *
 * Loads a real built page (site/finance/all.html and site/countries/ZAF/finance.html)
 * into jsdom with a fetch() that reads the CSV off disk, then asserts on the DOM the
 * component actually produced. Not a substitute for looking at it in a browser —
 * jsdom has no layout, so the sticky header and column-width sync are unverifiable
 * here — but it does catch the things that silently produce a plausible-looking
 * wrong table: a CSV row torn in half by an embedded newline, a BOM that stops the
 * first column matching its name, a filter naming a column that is not there.
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
  const clipped = doc.querySelectorAll('.dt-clip');
  check('long cells are clamped', clipped.length > 0, `${clipped.length} clamped`);

  // Sorting: the initial data-sort must have actually been applied.
  const sorted = doc.querySelector('.dt-head thead th.sort-asc, .dt-head thead th.sort-desc');
  check('initial sort applied', !!sorted, box.dataset.sort);

  await interactions(doc, want, opts);
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

await suite('site/finance/all.html', { linkCol: true, labelled: true });
await suite('site/countries/ZAF/finance.html', { linkCol: true, labelled: false });

console.log(failures ? `\n${failures} failure(s)` : '\nall checks passed');
process.exit(failures ? 1 : 0);
