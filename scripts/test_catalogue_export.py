#!/usr/bin/env python3
"""test_catalogue_export.py — the download the page cuts is the published file's own rows.

    python scripts/test_catalogue_export.py

`site/catalogue/index.html` cuts a CSV in the reader's browser, and the promise made on
the page is that it comes out with the same columns, in the same order and the same
dialect, as `raw-catalogue.csv`. Until Part 4 of the split that promise was cheap to
keep: the page fetched the whole published JSON and cut rows out of it, so what it wrote
was the record itself. It now **rebuilds** each record from the filter index and the row
chunks, and that is a reconstruction — the kind of thing that drifts in silence.

So this lifts `itemOf`, `csvCell` and `toCSV` out of the **built page** — testing a copy
of the logic would only prove the copy right — rebuilds every record in the catalogue
from the split payload the page actually fetches, serialises them, and compares the
bytes to `raw-catalogue.csv`. A filtered download is then that file with rows removed,
and demonstrably nothing else.

That covers three things at once, and they used to be three separate risks: the
JavaScript port of `csv.DictWriter` (a changed quoting rule, a lost CRLF, a boolean
rendering as `false` instead of `False`), the encoding of every column into the split
payload, and the reassembly of a record out of it. Nothing else in the build would
notice any of them.

**The columns are the published set, which is not every column the catalogue holds.**
Seven came out of the download on 2026-09-09 (`build-catalogue.py` -> `CSV_COLS`), so what
is compared here is the page's cut against `raw-catalogue.csv` as it now stands. The
fuller table beside it, `catalogue-internal.csv`, is not published and is not what the
page cuts from, so it is not in this comparison at all.

The row **order** is taken from `outputs/catalogue/raw-catalogue.json`, which is the
file `raw-catalogue.csv` was written from and is not published. An export's own order is
the reader's view order, deliberately, so it is not what is being checked here — the
rows and their contents are.

Needs node on PATH, and the catalogue built. Skips rather than fails without either,
because this is a check on the site build and not everyone running the suite has one.
See documentation/archived/catalogue-filtered-download.md.
"""
from __future__ import annotations
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
CAT = CORPUS / "site" / "catalogue"
RAW = CORPUS / "outputs" / "catalogue" / "raw-catalogue.json"

HARNESS = r"""
const fs = require('fs');
const [DIR, RAW_JSON] = process.argv.slice(2);
const page = fs.readFileSync(DIR + '/index.html', 'utf8');

// Pull one function out of the page by brace-matching from its declaration.
function grab(name){
  const i = page.indexOf('function ' + name + '(');
  if (i < 0) throw new Error('the built page has no ' + name + '()');
  let depth = 0;
  for (let k = page.indexOf('{', i); k < page.length; k++){
    if (page[k] === '{') depth++;
    else if (page[k] === '}' && !--depth) return page.slice(i, k + 1);
  }
  throw new Error('unterminated ' + name + '()');
}

// The split payload, read the way the page reads it.
const D = JSON.parse(fs.readFileSync(DIR + '/data/filter-index.json', 'utf8'));
const rows = [];
for (let c = 0; c * D.chunk < D.n; c++)
  for (const r of JSON.parse(fs.readFileSync(
        DIR + '/data/rows-' + ('00' + c).slice(-3) + '.json', 'utf8'))) rows.push(r);
if (rows.length !== D.n) throw new Error('the chunks hold ' + rows.length + ' of ' + D.n + ' rows');

const PUBS = D.pubs, DATES = D.dates, PLK = D.placekeys, TPK = D.topickeys,
      COMP = D.comp, ENTS = D.ents;
const cDate = D.date, cPub = D.pub, cPl = D.pl, cTp = D.tp, cEn = D.en, cCmp = D.cmp;

const api = new Function('CSVCOLS', 'PUBS', 'DATES', 'PLK', 'TPK', 'COMP', 'ENTS',
                         'cDate', 'cPub', 'cPl', 'cTp', 'cEn', 'cCmp',
  grab('itemOf') + '\n' + grab('csvCell') + '\n' + grab('toCSV') +
  '\nreturn {itemOf, toCSV};')(D.cols, PUBS, DATES, PLK, TPK, COMP, ENTS,
                              cDate, cPub, cPl, cTp, cEn, cCmp);

// Every record, rebuilt from the payload the page fetches, keyed on the chunk's own
// slug field — field 2 of CHUNK_FIELDS. The export itself has carried no slug since
// 2026-09-09, so the key has to come from the payload rather than from the record the
// page builds out of it; the page still holds it because `rowOf` reassembles a row of
// thirteen fields whether it draws them all or not.
const built = {};
for (let i = 0; i < D.n; i++){
  const it = api.itemOf(i, rows[i]), slug = rows[i][2];
  if (built[slug]) throw new Error('two records share the slug ' + slug);
  built[slug] = it;
}

// In the order `raw-catalogue.csv` was written in, which is the JSON's own.
const source = JSON.parse(fs.readFileSync(RAW_JSON, 'utf8')).items;
const items = [], lost = [];
for (const it of source){
  const mine = built[it.slug];
  if (!mine){ if (lost.length < 5) lost.push(it.slug); continue; }
  items.push(mine);
}

const mine = Buffer.from(api.toCSV(items), 'utf8');
const published = fs.readFileSync(DIR + '/raw-catalogue.csv');

const out = {cols: D.cols.length, rows: items.length, source: source.length,
             lost: lost, mine: mine.length, published: published.length,
             match: mine.equals(published)};
if (!out.match){
  const a = mine.toString('utf8').split('\r\n'), b = published.toString('utf8').split('\r\n');
  out.first_diff = null;
  for (let i = 0; i < Math.max(a.length, b.length); i++)
    if (a[i] !== b[i]){ out.first_diff = {line: i, page: (a[i]||'').slice(0,240),
                                          published: (b[i]||'').slice(0,240)}; break; }
}
process.stdout.write(JSON.stringify(out));
"""


def main() -> int:
    if not shutil.which("node"):
        print("test_catalogue_export: skipped — node is not on PATH")
        return 0
    missing = [str(p) for p in (CAT / "index.html", CAT / "data" / "filter-index.json",
                                CAT / "data" / "rows-000.json", CAT / "raw-catalogue.csv",
                                RAW) if not p.exists()]
    if missing:
        print(f"test_catalogue_export: skipped — run scripts/catalogue.py first "
              f"(no {', '.join(Path(m).name for m in missing)})")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        harness = Path(tmp) / "parity.js"
        harness.write_text(HARNESS, encoding="utf-8")
        proc = subprocess.run(["node", "--max-old-space-size=4096", str(harness),
                               str(CAT), str(RAW)],
                              capture_output=True, text=True, encoding="utf-8")
    if proc.returncode:
        print("test_catalogue_export: FAILED — the harness could not rebuild the records "
              "or run the page's serialiser, which usually means one of them was renamed "
              "or restructured")
        print(proc.stderr.strip()[:1200])
        return 1

    r = json.loads(proc.stdout)
    if r["lost"]:
        print(f"test_catalogue_export: FAILED — {r['source'] - r['rows']:,} record(s) in "
              f"the catalogue are not in the split payload at all, so the download would "
              f"be short: {', '.join(r['lost'])}")
        return 1
    if r["match"]:
        print(f"test_catalogue_export: ok — every record rebuilt from the filter index "
              f"and the row chunks serialises to raw-catalogue.csv byte for byte "
              f"({r['rows']:,} rows, {r['cols']} columns, {r['published']:,} bytes)")
        return 0

    print(f"test_catalogue_export: FAILED — a download cut from the page would not match "
          f"the published file ({r['mine']:,} bytes against {r['published']:,})")
    d = r.get("first_diff")
    if d:
        print(f"  first difference at line {d['line']}")
        print(f"    page      {d['page']!r}")
        print(f"    published {d['published']!r}")
    print("  the page's itemOf()/csvCell()/toCSV() and build-catalogue.py's own writer "
          "have diverged — see documentation/archived/catalogue-filtered-download.md")
    return 1


if __name__ == "__main__":
    sys.exit(main())
