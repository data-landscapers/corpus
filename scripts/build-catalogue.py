#!/usr/bin/env python3
"""build-catalogue.py — the public catalogue of everything held in `raw/`.

The website needs one thing the index cannot give it directly: a **committed,
self-contained, filterable list of the holdings**. `index/` is local scaffolding —
untracked, rebuilt, 14 MB of parser detail nobody outside a script should read.
This is the published view of it: one JSON file the site fetches, one CSV for
everything else, and the facet counts a filter UI needs so it does not have to
scan the rows to build its own menus.

It goes to `outputs/` because that is the folder the website serves, alongside
the finance exports, and it is **tracked** for the same reason they are — a
published artefact is part of the record, unlike the index it derives from.

**Metadata only, deliberately.** Title, publisher, date, facets, URL, and whether
a document is held — enough to filter, search and cite. It carries no body text:
the bodies are other people's words held for the wiki's own use, and a catalogue
is not a place to republish them. The `url` sends a reader to the publisher.

Usage:
  python scripts/build-catalogue.py                 write outputs/catalogue/
  python scripts/build-catalogue.py --check         report drift, write nothing
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault_lib as V                                                # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT_DIR = os.path.join(V.ROOT, "outputs", "catalogue")
JSON_PATH = os.path.join(OUT_DIR, "raw-catalogue.json")
CSV_PATH = os.path.join(OUT_DIR, "raw-catalogue.csv")
# What the catalogue was built from, so a later stage can tell whether it still holds.
# The report layer resolves its citations here rather than against `index/` (2026-08-14),
# and a resolution table nobody can date is one that goes stale in silence.
STAMP_PATH = os.path.join(OUT_DIR, "catalogue-stamp.json")

# Display names for the entity slugs a wikilink can point at, so `[[bill]]` in an author
# field publishes as "Bill Anderson" rather than as "bill". Corpus's own lookup, resolved
# from this file rather than from the working root: under the workroot `lookups/` is
# OSINT's, and a relative read would open the wrong file (`build-entity-names.py` carries
# the same warning for the write). It is a checked-in table like `taxonomy.csv`, not a
# build input — an absent or stale row costs the bare target and nothing else, which is
# what `dewiki` does without it.
# `realpath`, not `abspath`: `scripts/` is itself a junction in the workroot, so an
# unresolved parent lands on `scripts/.workroot/lookups`, which is OSINT's.
ENTITY_NAMES = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                            "lookups", "entity-names.csv")


def entity_names():
    if not os.path.exists(ENTITY_NAMES):
        return {}
    with open(ENTITY_NAMES, encoding="utf-8-sig", newline="") as fh:
        return {r["slug"]: r["display"] for r in csv.DictReader(fh) if r.get("display")}


CSV_COLS = ["slug", "title", "publisher", "author", "published", "date_precision",
            "places", "topics", "entities", "lens", "body_completeness", "finance",
            "artefact", "words", "ingested", "url"]


def items(rows):
    out = []
    # Every free-text field a reader sees, de-wikilinked. Frontmatter is the wiki's own
    # prose and carries its cross-reference syntax; the catalogue is a published view and
    # must not (`vault_lib.dewiki`).
    names = entity_names()
    def txt(v):
        return V.dewiki(v, names) if isinstance(v, str) else ""
    artefacts = {r["path"].rsplit("/", 1)[-1]
                 for r in rows if r["d"].get("kind") == "artefact"}
    for r in rows:
        if not r["path"].startswith("raw/") or r["d"]["ext"] != ".md":
            continue
        fm, d = r["fm"], r["d"]
        held = [a for a in V.as_list(fm.get("artefact")) if a in artefacts]
        out.append({
            "slug": d["slug"],
            "path": r["path"],
            "title": txt(fm.get("title")) or d["slug"],
            # OSINT's one-line English subtitle for the record (`wiki/schemas.md` §4,
            # from 2026-09-05; `notes-for-corpus` 20). Records ingested before it carry
            # none and the catalogue renders nothing there - a backfill over them is
            # Bill's to commission. De-wikilinked like every other free-text field.
            "catalogue_hero": txt(fm.get("catalogue_hero")),
            "publisher": txt(fm.get("publisher")) or fm.get("publisher") or "",
            "author": txt(fm.get("author")),
            "published": fm.get("published") or "",
            "date_precision": fm.get("date_precision") or "",
            "url": fm.get("url") if isinstance(fm.get("url"), str) else "",
            "places": V.as_list(fm.get("places")),
            "topics": V.as_list(fm.get("topics")),
            "entities": V.as_list(fm.get("entities")),
            "lens": V.as_list(fm.get("lens")),
            "body_completeness": fm.get("body_completeness") or "",
            "finance": bool(fm.get("finance_origin")),
            "artefact": held,
            "words": d.get("words", 0),
            "ingested": fm.get("ingested") or "",
        })
    out.sort(key=lambda x: (x["published"], x["slug"]), reverse=True)
    return out


def facets(rows):
    """Counts a filter UI can render its menus from without scanning the rows."""
    f = {}
    for key in ("places", "topics", "lens", "entities"):
        c = Counter(v for r in rows for v in r[key])
        # entities has a long single-reference tail by design (CLAUDE.md ->
        # Entities). This used to be capped at the top 200, for a filter menu
        # rendered as a list. The browse page renders the entity facet through
        # the same type-ahead it already uses for 62 places and 38 topics, so
        # the cap now only hides vocabulary from anyone reading this file —
        # including a reader checking whether a tag they searched for exists.
        # Uncapped 2026-08-24 (documentation/archived/catalogue-search.md, stage 1).
        f[key] = dict(c.most_common())
    f["publisher"] = dict(Counter(r["publisher"] for r in rows if r["publisher"]).most_common())
    f["year"] = dict(sorted(Counter(r["published"][:4] for r in rows if r["published"]).items()))
    f["body_completeness"] = dict(Counter(r["body_completeness"] for r in rows).most_common())
    return f


def write(rows, meta, stamp):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(STAMP_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"built": meta["built"],
                   "records": len(rows),
                   "raw_md_files": stamp[0],
                   "raw_md_mtime_max": stamp[1]}, fh, indent=2)
        fh.write("\n")
    doc = {"built": meta["built"][:10],
           "count": len(rows),
           "note": "Catalogue of sources held in raw/. Metadata only — follow `url` "
                   "to the publisher. Derived by scripts/build-catalogue.py; do not edit.",
           "facets": facets(rows),
           "items": rows}
    # One item per line: this file is tracked and rebuilt often, so a pretty-printed
    # array would show a 7,700-row rewrite whenever one source changed, while a
    # single minified line would show a whole-file diff. A line per source diffs
    # like the vault does — one changed line per changed source.
    head = {k: v for k, v in doc.items() if k != "items"}
    with open(JSON_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("{\n")
        for k, v in head.items():
            fh.write(f' {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},\n')
        fh.write(' "items": [\n')
        for n, item in enumerate(rows):
            fh.write(json.dumps(item, ensure_ascii=False, sort_keys=True))
            fh.write(",\n" if n < len(rows) - 1 else "\n")
        fh.write(" ]\n}\n")
    # `utf-8-sig` — a BOM, like every other CSV the site publishes *(2026-08-25)*. This
    # file is 26,000 non-ASCII characters of French, Portuguese and Arabic titles, and
    # Excel on Windows opens a BOM-less CSV in the ANSI codepage: `Republica` arrives as
    # `RepÃºblica` on the biggest download on the site while the finance CSVs beside it
    # open clean, because those have carried a BOM since they were written. Nothing was
    # wrong upstream — `lint-mojibake.py` is clean over inputs and derived alike — so the
    # fault was Excel guessing, and the BOM is how a file stops it guessing.
    #
    # The reader's filtered cut must carry one too, or it opens worse than the whole file
    # it was cut from. `catalogue.py` -> `toCSV` prepends it and
    # `test_catalogue_export.py` compares the bytes, so the two cannot drift apart in
    # silence. Every Python reader of this file already opens it `utf-8-sig`, which reads
    # both forms; `bulletin.py` and `lint-scope.py` were the two that did not and now do.
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            flat = dict(r)
            for k in ("places", "topics", "entities", "lens", "artefact"):
                flat[k] = "; ".join(flat[k])
            w.writerow(flat)
    return doc


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="report how far the written catalogue is from the vault")
    a = ap.parse_args()

    # The stamp is read BEFORE the index is refreshed, deliberately. Anything that changes in
    # `raw/` between these two lines then makes the written stamp look *older* than the tree,
    # so the next run rebuilds — where the other order would stamp the catalogue newer than the
    # rows it actually contains and the staleness would never be noticed.
    stamp = V.raw_md_state()
    meta = V.ensure_fresh()
    rows = items(V.load_index(auto=False))

    if a.check:
        if not os.path.exists(JSON_PATH):
            print(f"catalogue: not written yet ({len(rows):,} sources would be)")
            return 1
        held = json.load(open(JSON_PATH, encoding="utf-8"))
        drift = len(rows) - held.get("count", 0)
        print(f"catalogue: {held.get('count', 0):,} rows written {held.get('built')}, "
              f"{len(rows):,} in the vault ({drift:+,})")
        return 0 if drift == 0 else 1

    doc = write(rows, meta, stamp)
    print(f"catalogue: {doc['count']:,} sources -> outputs/catalogue/")
    print(f"  raw-catalogue.json {os.path.getsize(JSON_PATH)/1e6:.1f} MB, "
          f"raw-catalogue.csv {os.path.getsize(CSV_PATH)/1e6:.1f} MB")
    print(f"  facets: {len(doc['facets']['places'])} places, "
          f"{len(doc['facets']['topics'])} topics, "
          f"{len(doc['facets']['publisher'])} publishers, "
          f"{len(doc['facets']['year'])} years")
    return 0


if __name__ == "__main__":
    sys.exit(main())
