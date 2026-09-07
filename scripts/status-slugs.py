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
no URL is returned with `url: null` and yields no fact — **except where the record documented
having no URL**, which is a different answer and now says so.

`wiki/schemas.md` §4 admits a record whose `url:` is blank where `url_note:` states a dated,
exhausted search: what was tried, when, and why the absence is final. The record itself, usually
with an `artefact:` file beside it, is then the source. Reading the empty field alone reported
nine of these as dead and dropped the facts they carried (`notes-for-corpus` 22). Such a slug now
comes back with `url` set to its entry in Corpus's published catalogue, `held_offline: true`, and
the `url_note` and `artefact` themselves, so a drafter can cite it and see what stands behind it.
"""

import argparse
import csv
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402

FIELDS = ("slug", "title", "publisher", "published", "url", "places", "topics",
          "url_note", "artefact")
SITE_BASE = "https://corpus.data-landscapers.io"


def catalogue():
    out = {}
    with open(S.CATALOGUE_CSV, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            out[row["slug"]] = {k: row.get(k, "") for k in FIELDS}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--file", help="a file of slugs, one per line")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

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
        elif row and row.get("url_note"):
            # The documented absence. The citation is the record's own row in the published
            # catalogue, which is what `report-render.slug_offline()` resolves it to as well —
            # one answer, so a drafter and the renderer cite the same address.
            row = dict(row, held_offline=True,
                       url=f"{SITE_BASE}/catalogue/#q={urllib.parse.quote(slug)}")
            out.append(row)
        else:
            out.append({"slug": slug, "url": None})
    json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
