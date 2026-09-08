#!/usr/bin/env python3
"""test_title_index.py — the title shards find what the in-memory search used to.

    python scripts/test_title_index.py

Part 2 of `documentation/catalogue-split-plan.md` moved title and hero search out of
the reader's browser and onto `site/catalogue/titles/`. The blob it replaced ran
`indexOf` over every title in the corpus, so anything that could be found before and
cannot be found now is a **silent** loss: the results simply look thinner, and nobody
reports that.

So this drives the real thing. It lifts `shardKeyFor` and `hitsFrom` out of the
**built page** — testing a copy of the logic would only prove the copy right — reads
the shards the page would fetch, and runs several thousand queries cut out of the
catalogue's own titles and hero lines. Two properties, and they are the whole promise:

- **Nothing is lost.** A query that occurs in a title or a hero *starting at a word
  boundary* returns the record it came from. That is the contract the shard key
  buys, stated in `build-title-index.py`, and the done-when of Part 2 — a search
  matching only on hero text — is one case of it.
- **Nothing is invented.** Every record returned really does have the query as a
  substring of one of the fields the builder indexed. A prefix index that
  over-returned would be worse than one that under-returned, because it would look
  like it was working.

What is deliberately **not** asserted is equality with the old substring match. A
query starting mid-word (`ercafes` inside `Cybercafes`) was found before and is not
found now; that narrowing is the price of the split, it is recorded in three places,
and a test that demanded the old behaviour would be a test demanding the payload back.

Needs node on PATH, and the catalogue built. Skips rather than fails without either,
on the same grounds as `test_catalogue_export.py`.
"""
from __future__ import annotations
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
CAT = CORPUS / "site" / "catalogue"
RAW = CORPUS / "outputs" / "catalogue" / "raw-catalogue.json"
DOC_IDS = CORPUS / "outputs" / "catalogue" / "doc-ids.csv"
MANIFEST = CORPUS / "outputs" / "titles" / "manifest.json"

HARNESS = r"""
const fs = require('fs');
const [PAGE_DIR, RAW_JSON, DOC_IDS, MANIFEST] = process.argv.slice(2);
const page = fs.readFileSync(PAGE_DIR + '/index.html', 'utf8');

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

const D = JSON.parse(fs.readFileSync(PAGE_DIR + '/data/filter-index.json', 'utf8'));

// The three closure values the lifted functions read, built as the page builds them.
const KEYSTOP = {};
(D.keystop || []).forEach((w) => { KEYSTOP[w] = 1; });
const COMBINING = /[\u0300-\u036f]/g, NOTWORD = /[^0-9a-z]+/;
const api = new Function('KEYSTOP', 'COMBINING', 'NOTWORD',
  grab('shardKeyFor') + '\n' + grab('hitsFrom') + '\nreturn {shardKeyFor, hitsFrom};'
)(KEYSTOP, COMBINING, NOTWORD);

const IX = {meta: D.titles, keys: {}, fallback: D.titles && D.titles.fallback};
if (!D.titles) { process.stdout.write(JSON.stringify({skip: 'the page ships no title index'})); process.exit(0); }
D.titles.keys.forEach((k) => { IX.keys[k] = 1; });

const WINRESERVED = {con: 1, prn: 1, aux: 1, nul: 1};
const SHARDS = {};
function shardText(k){
  if (SHARDS[k] === undefined){
    const f = PAGE_DIR + '/titles/' + (WINRESERVED[k] ? k + '-' : k) + '.txt';
    SHARDS[k] = fs.existsSync(f) ? fs.readFileSync(f, 'utf8') : null;
  }
  return SHARDS[k];
}

// ---- the truth: what the page held in memory before the split ----------------
const ids = {};
for (const row of fs.readFileSync(DOC_IDS, 'utf8').split('\n').slice(1)){
  const c = row.lastIndexOf(',');
  if (c < 1) continue;
  // 213 of these "slugs" are titles with spaces and commas in them, which `csv.writer`
  // quotes. Splitting on the last comma and stopping there silently dropped every one
  // of them, and the records then looked like the index had invented them.
  let slug = row.slice(0, c);
  if (slug.startsWith('"') && slug.endsWith('"')) slug = slug.slice(1, -1).replace(/""/g, '"');
  ids[slug] = +row.slice(c + 1);
}
const items = JSON.parse(fs.readFileSync(RAW_JSON, 'utf8')).items;
// The fields the builder indexed, read off its own manifest rather than restated: a
// field added there and forgotten here would show up as thousands of records the
// index "invented", which is a confusing way to be told about a correct change.
const FIELDS = JSON.parse(fs.readFileSync(MANIFEST, 'utf8')).fields;
const texts = [];                       // [docId, text] for every indexed field
for (const it of items){
  const id = ids[it.slug];
  if (id === undefined) continue;
  for (const f of FIELDS){
    const t = (it[f] || '').replace(/[\t\r\n]+/g, ' ').trim();
    if (t) texts.push([id, t, f]);
  }
}

// ---- the queries: word-aligned phrases cut out of the corpus's own text -------
// Every 12th text, and from each the 1-, 2- and 3-word phrases starting at its
// second and fifth words — off the front, where a title's first word is most often
// the one a reader would not type.
const MINQ = D.titles.minq;
const queries = [];
for (let i = 0; i < texts.length; i += 12){
  const [id, t, field] = texts[i];
  const parts = t.split(/(\s+)/);        // words and the gaps, so offsets survive
  const wordAt = [];
  let off = 0;
  for (const p of parts){ if (p.trim()) wordAt.push(off); off += p.length; }
  for (const start of [1, 4]){
    if (start >= wordAt.length) continue;
    for (const n of [1, 2, 3]){
      const from = wordAt[start], to = start + n < wordAt.length ? wordAt[start + n] : t.length;
      const q = t.slice(from, to).trim().toLowerCase();
      if (q.length < MINQ) continue;
      // A query with no keyable word of its own — all stopwords, all numbers, or not
      // Latin at all — reaches only the fallback shard, by design, and
      // `build-title-index.py` says so. Not a case this asserts.
      const k0 = api.shardKeyFor(IX, q);
      if (k0 === null || k0 === IX.fallback) continue;
      queries.push({q, id, field});
    }
  }
}

// ---- run them ----------------------------------------------------------------
// One document's title and hero, lowercased and keyed by id — the thing the page's
// blob used to be, kept here only so that "nothing invented" is checkable in O(1).
const BY_ID = {};
for (const [id, t] of texts) (BY_ID[id] = BY_ID[id] || []).push(t.toLowerCase());

let lost = [], invented = [], hitTotal = 0;
for (const {q, id, field} of queries){
  const k = api.shardKeyFor(IX, q);
  const hits = api.hitsFrom(shardText(k), q) || {};
  hitTotal += Object.keys(hits).length;
  // Nothing lost: the record the query was cut out of comes back.
  if (!hits[id]) lost.push(lost.length < 8 ? {q, id, field, key: k} : {q});
  // Nothing invented: everything returned really does hold the query.
  for (const h of Object.keys(hits)){
    const held = BY_ID[+h] || [];
    if (!held.some((t) => t.indexOf(q) !== -1))
      invented.push(invented.length < 8 ? {q, id: +h, key: k} : {q});
  }
}

process.stdout.write(JSON.stringify({
  texts: texts.length, queries: queries.length, hits: hitTotal,
  heroQueries: queries.filter((x) => x.field === 'catalogue_hero').length,
  lost: lost.slice(0, 8), lostN: lost.length,
  invented: invented.slice(0, 8), inventedN: invented.length,
}));
"""


def main() -> int:
    if not shutil.which("node"):
        print("test_title_index: skipped — node is not on PATH")
        return 0
    missing = [str(p) for p in (CAT / "index.html", CAT / "data" / "filter-index.json",
                                CAT / "titles", RAW, DOC_IDS, MANIFEST) if not p.exists()]
    if missing:
        print(f"test_title_index: skipped — run scripts/build-title-index.py and "
              f"scripts/catalogue.py first (no {', '.join(Path(m).name for m in missing)})")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        harness = Path(tmp) / "titleindex.js"
        harness.write_text(HARNESS, encoding="utf-8")
        proc = subprocess.run(["node", "--max-old-space-size=4096", str(harness),
                               str(CAT), str(RAW), str(DOC_IDS), str(MANIFEST)],
                              capture_output=True, text=True, encoding="utf-8")
    if proc.returncode:
        print("test_title_index: FAILED — the harness could not run the page's own "
              "shard lookup, which usually means it was renamed or restructured")
        print(proc.stderr.strip()[:1200])
        return 1

    r = json.loads(proc.stdout)
    if r.get("skip"):
        print(f"test_title_index: skipped — {r['skip']}")
        return 0

    if not r["lostN"] and not r["inventedN"]:
        print(f"test_title_index: ok — {r['queries']:,} word-aligned queries "
              f"({r['heroQueries']:,} of them cut from hero lines) over "
              f"{r['texts']:,} titles and heroes: every one found its own record, "
              f"and all {r['hits']:,} records returned hold the query")
        return 0

    if r["lostN"]:
        print(f"test_title_index: FAILED — {r['lostN']:,} of {r['queries']:,} queries "
              f"did not return the record they were cut out of")
        for x in r["lost"]:
            print(f"    {x.get('q')!r} -> shard {x.get('key')} missed doc {x.get('id')} "
                  f"({x.get('field')})")
    if r["inventedN"]:
        print(f"test_title_index: FAILED — {r['inventedN']:,} records were returned "
              f"whose title and hero do not hold the query")
        for x in r["invented"]:
            print(f"    {x.get('q')!r} -> shard {x.get('key')} returned doc {x.get('id')}")
    print("  the page's shardKeyFor()/hitsFrom() and build-title-index.py's key_of() "
          "have diverged — see documentation/catalogue-split-plan.md, Part 2")
    return 1


if __name__ == "__main__":
    sys.exit(main())
