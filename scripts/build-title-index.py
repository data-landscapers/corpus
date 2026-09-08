#!/usr/bin/env python3
r"""build-title-index.py — the searchable index of catalogue titles and hero lines.

    python scripts/build-title-index.py            write outputs/titles/
    python scripts/build-title-index.py --check     report drift, write nothing
    python scripts/build-title-index.py --stats     size profile, write nothing

Part 2 of `documentation/catalogue-split-plan.md`. The catalogue page used to search
titles by holding every one of them in memory: `catalogue-data.js` shipped them, and
the page concatenated title, publisher, hero, slug and entity tags into a per-row
blob and ran `indexOf` over it. That is the one operation that appears to need the
whole corpus in the browser, and this is the answer — the same machinery already
running for the names found inside the sources, pointed at the text the catalogue
holds about them.

**Hero is indexed alongside title, not after it.** OSINT began writing a one-line
subtitle onto records in September and it was folded into that search blob from the
day it arrived, so it is searched today. Indexing the titles alone would have
narrowed what search finds without changing anything a reader could see: the results
simply look thinner, and nobody reports that.

**This reads `outputs/` and nothing else, and that is the point.** The names index
needs the vault, so it is built from the workroot and a render without one ships a
page with names search turned off. After Part 3 of the split, title search *is* the
search — a page that could lose it whenever the vault was not to hand would be a page
that sometimes cannot find anything.

## What a query can and cannot reach

**The promise is word alignment.** A shard key is a word's first two characters (with
accents folded off), so a record is found when the query occurs in its title or hero
*starting at a word boundary*. `scripts/test_title_index.py` asserts exactly that, and
its converse, over ten thousand queries cut out of the corpus's own text.

The page picks its key from the first word of the query that could be one — not from
the query's own first characters — so `the digital` and `de la transformation` reach
what their second word reaches. Three things still do not:

- **A query that starts mid-word finds nothing.** `cybercafes` reaches the record
  whose hero says so; `ercafes` does not. This is the one real narrowing against the
  substring match this replaces.
- **A query under `MIN_QUERY` characters is not sent here at all.** The page says so,
  and still matches publisher, slug and actors out of what it holds in memory.
- **A query with no keyable word of its own** — every word a stopword, or a number,
  or not Latin — reaches only the `FALLBACK` shard, which is where the texts in the
  same position live. That is 457 of 23,739, nearly all of them Arabic titles, and
  without it they would be reachable by facet and by nothing else.

These are the price of not shipping 20,000 titles to every visitor, they were measured
against the whole catalogue before the switch (`documentation/catalogue-split-plan.md`,
Part 2), and they are stated here because the failure mode is a search that returns
less rather than an error anyone would see.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = Path(__file__).resolve().parent.parent
CATALOGUE = ROOT / "outputs" / "catalogue" / "raw-catalogue.json"
DOC_IDS = ROOT / "outputs" / "catalogue" / "doc-ids.csv"
OUT_DIR = ROOT / "outputs" / "titles"
MANIFEST = OUT_DIR / "manifest.json"

from shard_lib import (FALLBACK, MIN_QUERY, PREFIX, doc_ids, profile, shard,  # noqa: E402
                       write_shards)                                          # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# The fields indexed, in the order they are read off a record. Adding one here is the
# whole change — but see the page, which decides what it still matches in memory.
#
# **The slug joined them at Part 3**, when it left the payload with the rest of the row
# text. It is the identifier every Corpus report cites by, and a record whose `url:` is
# a documented absence is cited *to the catalogue page* by slug
# (`report-render.slug_offline()`, notes-for-corpus 22) — so a slug that cannot be
# searched lands those citations on nothing. Its date prefix keys on nothing, which
# costs it nothing: a pasted slug finds its shard through the first real word in it.
FIELDS = ("title", "catalogue_hero", "slug")

WS = re.compile(r"[\t\r\n]+")
SPLIT = re.compile(r"[^0-9a-z]+")
COMBINING = re.compile(r"[\u0300-\u036f]")


def fold(text: str) -> str:
    """Lowercased with the accents taken off — the form a shard key is cut from.

    **Only the key is folded, never the text and never the match.** The shard holds
    the title as written and the page runs `indexOf` on the query as typed, so
    `côte` still matches Côte and `cote` still does not, exactly as the in-memory
    blob behaved. What folding buys is that the record is *in* the `co` shard at
    all: 5,028 of the 23,739 titles and hero lines here tokenise differently with
    the accents left on, because this corpus is a fifth French and Portuguese.
    """
    return COMBINING.sub("", unicodedata.normalize("NFD", text.lower()))


def words(text: str) -> list[str]:
    """The words a text is keyed on — punctuation gone and accents folded.

    `str.split` is right for a name, where the words are already separated. It is
    wrong for a title: `e-Government` would key on `e-`, which is not a shard key at
    all, and the record would be reachable from neither `e` nor `go`.

    Single characters are dropped rather than padded. A padded key carries an
    underscore, and the page only ever slices a key out of the query, so `l_` — the
    key every French elision lands on — is a shard nothing can ask for. Left in,
    the `d__` bucket alone was the fattest file in the index at 160 KB, and
    unreachable.
    """
    return [w for w in SPLIT.split(fold(text)) if len(w) > 1]


def harvest(items, ids):
    """text -> sorted document ids, one line per distinct title or hero.

    **Title and hero are separate lines for the same document.** Joining them would
    let a query match across the join — text the reader never sees as one string —
    and the page's blob does not do that either, because the publisher sits between
    them in it.

    The text goes in verbatim, lowercased by the page at match time rather than here,
    so that `title.toLowerCase().indexOf(q)` in the shard is the same test the blob
    was running. Only tabs and newlines are touched, and only because they are the
    line format.
    """
    post: dict[str, list[int]] = collections.defaultdict(list)
    docs = 0
    for it in items:
        did = ids.get(it.get("slug") or "")
        if did is None:
            continue
        seen = False
        for f in FIELDS:
            text = WS.sub(" ", (it.get(f) or "")).strip()
            if not text:
                continue
            post[text].append(did)
            seen = True
        docs += seen
    for v in post.values():
        v.sort()
    return post, docs


def write(shards, splits, stats):
    keep = write_shards(OUT_DIR, shards, "titles")
    # **A manifest is a promise the page acts on**, so it is written after the shards
    # rather than beside them: every key in it has just been seen on disk.
    MANIFEST.write_text(json.dumps({
        "built": stats["built"],
        "prefix": PREFIX,
        "min_query": MIN_QUERY,
        "splits": splits,
        "shards": sorted(keep),
        "texts": stats["texts"],
        "postings": stats["postings"],
        "documents": stats["documents"],
        "fields": list(FIELDS),
        # Texts no word could key — Arabic titles, and the few whose every word is
        # a stopword or a number. They live in the `0` shard and the page asks for
        # it when a query yields no key of its own.
        "unkeyed": stats["unkeyed"],
        "fallback": FALLBACK,
        "note": "Index of catalogue titles and hero lines. Text -> document ids, "
                "delta-encoded; ids resolve through outputs/catalogue/doc-ids.csv. "
                "Derived by scripts/build-title-index.py; do not edit.",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return keep


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    ap.add_argument("--stats", action="store_true", help="size profile, write nothing")
    a = ap.parse_args()

    if not CATALOGUE.exists():
        print(f"titles: no catalogue at {CATALOGUE} — run scripts/rebuild.py --catalogue first")
        return 1

    doc = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    items = doc["items"] if isinstance(doc, dict) and "items" in doc else doc
    ids = doc_ids(DOC_IDS, [i["slug"] for i in items], write=not (a.check or a.stats))
    post, docs = harvest(items, ids)
    shards, splits, lines = shard(post, words=words, fallback=FALLBACK)
    unkeyed = len(shards.get(FALLBACK, "").splitlines())
    stats = {"built": doc.get("built", ""), "texts": len(post),
             "postings": sum(len(v) for v in post.values()), "documents": docs,
             "unkeyed": unkeyed}

    if a.check:
        if not MANIFEST.exists():
            print(f"titles: not written yet ({len(post):,} texts would be)")
            return 1
        held = json.loads(MANIFEST.read_text(encoding="utf-8"))
        drift = len(post) - held.get("texts", 0)
        print(f"titles: {held.get('texts', 0):,} written {held.get('built')}, "
              f"{len(post):,} in the catalogue ({drift:+,})")
        return 0 if drift == 0 else 1

    p = profile(shards)
    if a.stats:
        print(f"titles: {len(post):,} texts, {stats['postings']:,} postings, "
              f"{stats['documents']:,} documents")
        print(f"  {p['files']} shards, {p['total']/1e6:.2f} MB gzipped on the server")
        print(f"  per query: median {p['median']/1024:.1f} KB  mean {p['mean']/1024:.1f} KB  "
              f"p90 {p['p90']/1024:.1f} KB  max {p['max']/1024:.1f} KB")
        print(f"  {len(splits)} prefix(es) re-cut at {PREFIX+1} chars: {', '.join(splits) or 'none'}")
        print(f"  {stats['unkeyed']:,} texts with no keyable word -> the {FALLBACK} shard")
        return 0

    keep = write(shards, splits, stats)
    print(f"titles: {len(post):,} titles and hero lines over {stats['documents']:,} "
          f"documents -> outputs/titles/")
    print(f"  {len(keep)} shards, {p['total']/1e6:.2f} MB gzipped; per query "
          f"median {p['median']/1024:.1f} KB, p90 {p['p90']/1024:.1f} KB, max {p['max']/1024:.1f} KB")
    print(f"  {stats['unkeyed']:,} with no keyable word, in the {FALLBACK} shard the "
          f"page falls back to")
    return 0


if __name__ == "__main__":
    sys.exit(main())
