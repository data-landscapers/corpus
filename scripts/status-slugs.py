#!/usr/bin/env python3
"""Resolve wiki source slugs to catalogue rows — `STATUS-INIT.md` -> *Stage 1*.

An extraction agent reads one intersection and has to turn the slugs in its `sources:` frontmatter
and its `Source:` lines into the URLs the report will hyperlink. **The catalogue is the resolver**,
not `index/files.jsonl`: the catalogue is Corpus's published table and the set check A tests
against, and the index additionally covers wiki concept pages carrying a `url:`, which are not
sources and must never be cited as though they were.

    python scripts/status-slugs.py 2025-06-10-itana-first-digital-free-zone ...
    python scripts/status-slugs.py --file slugs.txt

One record per slug, as JSON, so an agent does not have to parse a table. A slug that resolves to
no URL is returned with `url: null` and yields no fact.
"""

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402

FIELDS = ("slug", "title", "publisher", "published", "url", "places", "topics")


def catalogue():
    out = {}
    with open(S.CATALOGUE_CSV, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            out[row["slug"]] = {k: row.get(k, "") for k in FIELDS}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--file", help="a file of slugs, one per line")
    args = ap.parse_args()

    slugs = list(args.slugs)
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            slugs += [ln.strip().strip("[]") for ln in fh if ln.strip()]

    cat = catalogue()
    out = []
    for slug in slugs:
        slug = slug.strip().strip("[]")
        row = cat.get(slug)
        if row and row.get("url"):
            out.append(row)
        else:
            out.append({"slug": slug, "url": None})
    json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
