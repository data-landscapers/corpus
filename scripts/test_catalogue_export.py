#!/usr/bin/env python3
"""test_catalogue_export.py — the filtered download produces the published file's own rows.

    python scripts/test_catalogue_export.py

`site/catalogue/index.html` cuts a filtered CSV in the reader's browser, and the
promise made on the page is that it comes out with the same sixteen columns, in the
same order and the same dialect, as `raw-catalogue.csv`. That promise is a JavaScript
port of `csv.DictWriter` and it can drift in silence — a changed quoting rule, a lost
CRLF, a boolean that starts rendering as `false` instead of `False`. Nothing else in
the build would notice.

So this lifts `csvCell` and `toCSV` out of the **built page** — testing a copy of the
logic would only prove the copy right — runs them over every record in
`raw-catalogue.json`, and compares the bytes to `raw-catalogue.csv`. A filtered export
is then that file with rows removed, and demonstrably nothing else.

Needs node on PATH, and the catalogue built. Skips rather than fails without either,
because this is a check on the site build and not everyone running the suite has one.
See documentation/archived/catalogue-filtered-download.md.
"""
from __future__ import annotations
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
CAT = CORPUS / "site" / "catalogue"

HARNESS = r"""
const fs = require('fs');
const DIR = process.argv[2];
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

const cols = JSON.parse(fs.readFileSync(DIR + '/catalogue-data.js', 'utf8')
  .match(/"cols":(\[[^\]]*\])/)[1]);
const { toCSV } = new Function('CSVCOLS',
  grab('csvCell') + '\n' + grab('toCSV') + '\nreturn {toCSV};')(cols);

const items = JSON.parse(fs.readFileSync(DIR + '/raw-catalogue.json', 'utf8')).items;
const mine = Buffer.from(toCSV(items), 'utf8');
const published = fs.readFileSync(DIR + '/raw-catalogue.csv');

const out = {cols: cols.length, rows: items.length,
             mine: mine.length, published: published.length,
             match: mine.equals(published)};
if (!out.match){
  const a = mine.toString('utf8').split('\r\n'), b = published.toString('utf8').split('\r\n');
  out.first_diff = null;
  for (let i = 0; i < Math.max(a.length, b.length); i++)
    if (a[i] !== b[i]){ out.first_diff = {line: i, page: (a[i]||'').slice(0,200),
                                          published: (b[i]||'').slice(0,200)}; break; }
}
process.stdout.write(JSON.stringify(out));
"""


def main() -> int:
    if not shutil.which("node"):
        print("test_catalogue_export: skipped — node is not on PATH")
        return 0
    missing = [f for f in ("index.html", "catalogue-data.js",
                           "raw-catalogue.json", "raw-catalogue.csv")
               if not (CAT / f).exists()]
    if missing:
        print(f"test_catalogue_export: skipped — run scripts/catalogue.py first "
              f"(no {', '.join(missing)})")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        harness = Path(tmp) / "parity.js"
        harness.write_text(HARNESS, encoding="utf-8")
        proc = subprocess.run(["node", str(harness), str(CAT)],
                              capture_output=True, text=True)
    if proc.returncode:
        print("test_catalogue_export: FAILED — the harness could not run the page's "
              "serialiser, which usually means it was renamed or restructured")
        print(proc.stderr.strip()[:1200])
        return 1

    r = json.loads(proc.stdout)
    if r["match"]:
        print(f"test_catalogue_export: ok — the page's CSV serialiser reproduces "
              f"raw-catalogue.csv byte for byte ({r['rows']:,} rows, {r['cols']} columns, "
              f"{r['published']:,} bytes)")
        return 0

    print(f"test_catalogue_export: FAILED — a filtered download would not match the "
          f"published file ({r['mine']:,} bytes against {r['published']:,})")
    d = r.get("first_diff")
    if d:
        print(f"  first difference at line {d['line']}")
        print(f"    page      {d['page']!r}")
        print(f"    published {d['published']!r}")
    print("  the page's csvCell()/toCSV() and build-catalogue.py's csv.DictWriter have "
          "diverged — see documentation/archived/catalogue-filtered-download.md")
    return 1


if __name__ == "__main__":
    sys.exit(main())
