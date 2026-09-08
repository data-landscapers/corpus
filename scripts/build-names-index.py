#!/usr/bin/env python3
r"""build-names-index.py — the searchable index of names occurring in source bodies.

    python scripts/build-names-index.py            write outputs/names/
    python scripts/build-names-index.py --check     report drift, write nothing
    python scripts/build-names-index.py --stats     size profile, write nothing

Stage 3 of `documentation/archived/catalogue-search.md`. The catalogue's search box reaches
titles, publishers and entity tags; this reaches the **names that occur in the
sources themselves**, so a reader can find the document that mentions a person or
a company nobody tagged.

**What is published is an index, not a text.** Each shard is a list of
`name<TAB>document-ids` — no word order, no sentences, no offsets, nothing from
which prose could be reconstructed, and the page never renders a snippet. Bill
ruled on 2026-08-24 that publishing an index of names is not a licensing or
copyright problem; `design.md` §8's "the boundary that matters is bodies, not
internal reasoning" is the reasoning it was given on. **The line is the snippet**:
match-or-no-match is publishable, an extract is the body in fragments.

Two things this file is careful about.

**The sharding is `shard_lib.py`'s** — stable append-only document ids, bucketing
on the first two characters of every word so that "Cassava Technologies" is
reachable from both `ca` and `te`, a fat bucket re-cut one character deeper, and a
promised shard checked onto disk. That module carries the reasoning for all of it.
What is decided *here* is what text goes in: the names, and only the names.

**Tables and frontmatter are not prose.** The first pass at this indexed the
finance records' column headers — `Value`, `Financier`, `Amount`, `Deal ID` were
among the most frequent "names" in the corpus. Fences, pipe tables and stray
frontmatter lines are stripped before extraction.

The raw root resolves through `scripts/.workroot/` like every other vault reader.
`CORPUS_RAW` overrides it, on the same reasoning as `status_lib.EXCHANGE`'s
`CORPUS_OSINT_XFER`: a path that may move should not need a code change.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault_lib as V                                                # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(V.ROOT)
RAW = Path(os.environ.get("CORPUS_RAW") or (ROOT / "raw"))
CATALOGUE = ROOT / "outputs" / "catalogue" / "raw-catalogue.json"
DOC_IDS = ROOT / "outputs" / "catalogue" / "doc-ids.csv"
OUT_DIR = ROOT / "outputs" / "names"
MANIFEST = OUT_DIR / "manifest.json"

# Extraction, the stopword sets and the Windows filename rules are shared with
# `build-entity-names.py` and `catalogue.py`, and live in `names_lib.py` — moved
# there when the third reader appeared. The shard machinery is shared with
# `build-title-index.py` and lives in `shard_lib.py`, moved there for the same
# reason when that second index appeared.
from names_lib import names_in                                                  # noqa: E402
from shard_lib import (MIN_QUERY, PREFIX, doc_ids, profile, shard,              # noqa: E402
                       write_shards)                                            # noqa: E402


def harvest(items, ids):
    """name -> sorted list of stable document ids."""
    post: dict[str, list[int]] = collections.defaultdict(list)
    missing = 0
    for it in items:
        rel = it.get("path") or ""
        if not rel.startswith("raw/"):
            continue
        fp = RAW / rel[len("raw/"):]
        if not fp.exists():
            missing += 1
            continue
        did = ids[it["slug"]]
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            missing += 1
            continue
        for s in names_in(text):
            post[s].append(did)
    for v in post.values():
        v.sort()
    return post, missing


def write(shards, splits, stats):
    keep = write_shards(OUT_DIR, shards, "names")
    # **A manifest is a promise the page acts on**, so it is written after the shards
    # rather than beside them: every key in it has just been seen on disk.
    MANIFEST.write_text(json.dumps({
        "built": stats["built"],
        "prefix": PREFIX,
        "min_query": MIN_QUERY,
        "splits": splits,
        "shards": sorted(keep),
        "names": stats["names"],
        "postings": stats["postings"],
        "documents": stats["documents"],
        "note": "Index of names occurring in source bodies. Name -> document ids, "
                "delta-encoded; ids resolve through outputs/catalogue/doc-ids.csv. "
                "No word order, no offsets, no text. Derived by "
                "scripts/build-names-index.py; do not edit.",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return keep


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    ap.add_argument("--stats", action="store_true", help="size profile, write nothing")
    a = ap.parse_args()

    if not CATALOGUE.exists():
        print(f"names: no catalogue at {CATALOGUE} — run scripts/build-catalogue.py first")
        return 1
    if not RAW.exists():
        print(f"names: no raw/ at {RAW} — run from scripts/.workroot/, or set CORPUS_RAW")
        return 1

    doc = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    items = doc["items"] if isinstance(doc, dict) and "items" in doc else doc
    ids = doc_ids(DOC_IDS, [i["slug"] for i in items], write=not (a.check or a.stats))
    post, missing = harvest(items, ids)
    shards, splits, lines = shard(post)
    stats = {"built": doc.get("built", ""), "names": len(post),
             "postings": sum(len(v) for v in post.values()), "documents": len(items) - missing}

    if a.check:
        if not MANIFEST.exists():
            print(f"names: not written yet ({len(post):,} names would be)")
            return 1
        held = json.loads(MANIFEST.read_text(encoding="utf-8"))
        drift = len(post) - held.get("names", 0)
        print(f"names: {held.get('names', 0):,} written {held.get('built')}, "
              f"{len(post):,} in the vault ({drift:+,})")
        return 0 if drift == 0 else 1

    p = profile(shards)
    if a.stats:
        print(f"names: {len(post):,} names, {stats['postings']:,} postings, "
              f"{stats['documents']:,} documents")
        print(f"  {p['files']} shards, {p['total']/1e6:.2f} MB gzipped on the server")
        print(f"  per query: median {p['median']/1024:.1f} KB  mean {p['mean']/1024:.1f} KB  "
              f"p90 {p['p90']/1024:.1f} KB  max {p['max']/1024:.1f} KB")
        print(f"  {len(splits)} prefix(es) re-cut at {PREFIX+1} chars: {', '.join(splits) or 'none'}")
        return 0

    keep = write(shards, splits, stats)
    if missing:
        print(f"names: {missing:,} catalogue records had no readable body — skipped")
    print(f"names: {len(post):,} names over {stats['documents']:,} documents -> outputs/names/")
    print(f"  {len(keep)} shards, {p['total']/1e6:.2f} MB gzipped; per query "
          f"median {p['median']/1024:.1f} KB, p90 {p['p90']/1024:.1f} KB, max {p['max']/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
