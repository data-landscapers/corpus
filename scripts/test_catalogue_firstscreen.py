#!/usr/bin/env python3
"""test_catalogue_firstscreen.py — the baked first screen is what the page would draw.

    python scripts/test_catalogue_firstscreen.py

`catalogue.py` writes the newest hundred rows and the three facet menus into
`site/catalogue/index.html` as real markup, so the page shows something before its
payload has arrived (documentation/catalogue-split-plan.md, Part 1). The page then
redraws over the top, and the two have to produce the same markup: a difference is
a flash of one layout replaced by another, and — where the difference is a label or
a count rather than a pixel — a first screen that quietly says something the page
does not.

Python writes one of those and JavaScript writes the other, and nothing in the build
would notice them drifting apart. So this lifts `rowHTML` and `optsHTML` out of the
**built page** — testing a copy of the logic would only prove the copy right — runs
them over the payload the page ships, and compares the result to the markup baked
into the same file.

It compares the two facet menus and the hundred rows character for character. What it
does not cover is the interactive half of those functions, which cannot be baked and
so has nothing to be compared against: a selected checkbox, a type-ahead term, the
option cap, the sort orders other than the default. Those need the browser.

Needs node on PATH, and the catalogue built. Skips rather than fails without either,
on the same grounds as `test_catalogue_export.py`: this is a check on the site build
and not everyone running the suite has one.
"""
from __future__ import annotations
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
CAT = CORPUS / "site" / "catalogue"

# The page's own `rowHTML` and `optsHTML` are pure — values in, string out — which is
# what lets them be called here at all. `catalogue.py` says so where it defines them.
HARNESS = r"""
const fs = require('fs');
const DIR = process.argv[2];
const page = fs.readFileSync(DIR + '/index.html', 'utf8');

// Pull one function out of the page by brace-matching from its declaration.
// Same lift as test_catalogue_export.py; when one of them stops working the other
// usually has too, and the reason is a restructured page rather than a wrong one.
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

// The payload the page ships, read the way the page reads it.
const D = (new Function(grab_payload()))();
function grab_payload(){
  return fs.readFileSync(DIR + '/catalogue-data.js', 'utf8')
           .replace(/^window\.CATALOGUE\s*=/, 'return') + '\n';
}

// The two closure variables `rowHTML` needs, built exactly as the page builds them.
const ENTS = D.ents || [], DERIVED = D.entnames || {}, PRETTY = D.entpretty || {};
const ENTLABEL = {};
for (let i = 0; i < ENTS.length; i++)
  ENTLABEL[ENTS[i]] = DERIVED[ENTS[i]] || PRETTY[ENTS[i]] || ENTS[i];

const helpers = `
  function esc(s){ return String(s).replace(/[<>&]/g, function(c){ return {'<':'&lt;','>':'&gt;','&':'&amp;'}[c]; }); }
  function att(s){ return esc(s).replace(/"/g, '&quot;'); }
`;
const api = new Function('D', 'ENTLABEL', helpers + grab('rowHTML') + '\n' +
                          grab('optsHTML') + '\nreturn {rowHTML, optsHTML};')(D, ENTLABEL);

// ---- the rows ---------------------------------------------------------------
// Stored order is date-descending and the page's default sort is `new`, so the
// first screen is the head of the array with the entity offsets expanded.
const rows = D.rows.slice(0, 100).map(function(r){
  const c = r.slice();
  c[10] = (c[10] || []).map(function(i){ return ENTS[i]; });
  return c;
});
const results = rows.map(api.rowHTML).join('');

// ---- the facets -------------------------------------------------------------
// The counts are over every record, because nothing is filtered on the first screen.
function tally(idx){
  const c = {};
  for (const r of D.rows) for (const v of r[idx]) c[v] = (c[v] || 0) + 1;
  return c;
}
const placeC = tally(3), topicC = tally(4), yearC = {}, yearL = {};
for (const r of D.rows){
  const y = r[2].slice(0, 4);
  if (!y) continue;
  const b = +y < 2020 ? '<2020' : y;
  yearC[b] = (yearC[b] || 0) + 1;
  yearL[b] = b === '<2020' ? '< 2020' : b;
}

const REG = '@regions';
const pg = {}, pgn = {'@regions': 'Regions', '@none': 'Elsewhere'};
for (const k of Object.keys(D.places)) pg[k] = /^X/.test(k) ? REG : (D.regions[k] || '@none');
for (const k of Object.keys(D.regions)){ const r = D.regions[k]; if (r) pgn[r] = D.places[r] || r; }
const byGrp = {};
for (const k of Object.keys(D.places)) (byGrp[pg[k]] = byGrp[pg[k]] || []).push(k);
const gs = Object.keys(byGrp).sort(function(a, b){
  if (a === REG) return -1;
  if (b === REG) return 1;
  if (a === '@none') return 1;
  if (b === '@none') return -1;
  return (pgn[a] || a).localeCompare(pgn[b] || b);
});
let placeKeys = [];
for (const g of gs){
  byGrp[g].sort(function(a, b){ return D.places[a].localeCompare(D.places[b]); });
  placeKeys = placeKeys.concat(byGrp[g]);
}
function keep(keys, labels, c){ return keys.filter(function(k){ return labels[k] !== undefined && c[k]; }); }
placeKeys = keep(placeKeys, D.places, placeC);
const topicKeys = keep(D.torder, D.topics, topicC);
const yearKeys = Object.keys(yearL).filter(function(k){ return k !== '<2020'; }).sort().reverse();
if (yearL['<2020']) yearKeys.push('<2020');

function facet(key, title, keys, labels, c, groups, groupNames, searchable){
  let h = '<div class="facet"><h3>' + title + '</h3>';
  if (searchable) h += '<input class="ftype" data-f="' + key + '" placeholder="Filter ' +
                       title.toLowerCase() + '" autocomplete="off">';
  return h + '<div class="opts" data-opts="' + key + '">' +
         api.optsHTML(key, keys, labels, c, [], groups, groupNames, 0, '') +
         '</div></div>';
}
const facets =
  facet('places', 'Country', placeKeys, D.places, placeC, pg, pgn, true) +
  facet('topics', 'Topic', topicKeys, D.topics, topicC, D.cats, null, true) +
  facet('years', 'Year published', yearKeys, yearL, yearC, null, null, false);

process.stdout.write(JSON.stringify({rows: rows.length, results: results, facets: facets}));
"""

# What `catalogue.py` baked, read back out of the same file.
BAKED = {"results": re.compile(r'<div id="results">(.*?)</div>\s*<noscript>', re.S),
         "facets": re.compile(r'<aside id="facets">(.*?)</aside>', re.S)}


def main() -> int:
    if not shutil.which("node"):
        print("test_catalogue_firstscreen: skipped — node is not on PATH")
        return 0
    missing = [f for f in ("index.html", "catalogue-data.js")
               if not (CAT / f).exists()]
    if missing:
        print(f"test_catalogue_firstscreen: skipped — run scripts/catalogue.py first "
              f"(no {', '.join(missing)})")
        return 0

    page = (CAT / "index.html").read_text(encoding="utf-8")
    baked = {}
    for name, pat in BAKED.items():
        m = pat.search(page)
        if not m:
            print(f"test_catalogue_firstscreen: FAILED — the built page has no baked "
                  f"{name}. `catalogue.py` writes them into `BODY`; either the slot was "
                  f"removed or the markup around it changed.")
            return 1
        baked[name] = m.group(1)

    with tempfile.TemporaryDirectory() as tmp:
        harness = Path(tmp) / "firstscreen.js"
        harness.write_text(HARNESS, encoding="utf-8")
        proc = subprocess.run(["node", str(harness), str(CAT)],
                              capture_output=True, text=True, encoding="utf-8")
    if proc.returncode:
        print("test_catalogue_firstscreen: FAILED — the harness could not run the "
              "page's own renderers, which usually means they were renamed or "
              "restructured")
        print(proc.stderr.strip()[:1200])
        return 1

    r = json.loads(proc.stdout)
    bad = [k for k in ("results", "facets") if r[k] != baked[k]]
    if not bad:
        print(f"test_catalogue_firstscreen: ok — the baked first screen is character "
              f"for character what the page draws ({r['rows']} rows, "
              f"{baked['facets'].count('<label')} facet options)")
        return 0

    print(f"test_catalogue_firstscreen: FAILED — the baked {' and '.join(bad)} "
          f"{'differ' if len(bad) > 1 else 'differs'} from what the page would draw")
    for k in bad:
        a, b = baked[k], r[k]
        i = next((n for n in range(min(len(a), len(b))) if a[n] != b[n]), min(len(a), len(b)))
        print(f"  {k}: {len(a):,} baked characters against {len(b):,} drawn, "
              f"first difference at {i:,}")
        print(f"    baked  …{a[max(0, i-60):i+80]!r}")
        print(f"    drawn  …{b[max(0, i-60):i+80]!r}")
    print("  `catalogue.py` → `row_html`/`opts_html` and the page's rowHTML/optsHTML "
          "have diverged — see documentation/catalogue-split-plan.md, Part 1")
    return 1


if __name__ == "__main__":
    sys.exit(main())
