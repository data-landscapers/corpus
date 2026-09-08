#!/usr/bin/env python3
"""test_catalogue_index.py — the split payload still holds the whole catalogue.

    python scripts/test_catalogue_index.py

Part 3 of `documentation/catalogue-split-plan.md` took the catalogue out of the one
array the page used to be handed and encoded it as a filter index of integers plus
41 files of row text. Every facet, every count, every sort and every row the page
draws now comes out of that encoding, and a mistake in it does not look like an
error — it looks like a catalogue with the wrong number of records in Kenya.

So this reads `site/catalogue/data/` back and compares it, record by record, to
`outputs/catalogue/raw-catalogue.json` — the file the encoding was made from and the
one `raw-catalogue.csv` is cut from. It is exhaustive rather than sampled: every
row, every place, every topic, every actor, every year bucket.

**It checks the data, not the page.** That the page's `passes()` reads those columns
correctly is what `test_catalogue_firstscreen.py` and the browser cover; what is
checked here is that the columns say what the catalogue says. The two halves matter
separately, because an encoding fault is silent and a rendering fault is visible.

Needs the catalogue built. Skips rather than fails without it.
"""
from __future__ import annotations
import importlib.util, json, sys
from collections import Counter
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
DATA = CORPUS / "site" / "catalogue" / "data"
RAW = CORPUS / "outputs" / "catalogue" / "raw-catalogue.json"
DOC_IDS = CORPUS / "outputs" / "catalogue" / "doc-ids.csv"

# The builder's own sort key, imported rather than restated: a second copy of a
# collation rule is a copy that would eventually disagree, and then this test would be
# asserting that `catalogue.py` matches a stale idea of what it should do. Loaded by
# path because it sits beside a hyphenated neighbourhood and nothing here is a package.
_spec = importlib.util.spec_from_file_location(
    "catalogue_builder", Path(__file__).resolve().parent / "catalogue.py")
_cat = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cat)
coll = _cat.coll


def stored_order(items):
    """The row order the index is in: by `published[:10]`, descending, stably."""
    keyed = [((i.get("published") or "")[:10], n) for n, i in enumerate(items)]
    order = sorted(range(len(items)), key=lambda n: keyed[n][0], reverse=True)
    return [items[n] for n in order]


def main() -> int:
    if not (DATA / "filter-index.json").exists() or not RAW.exists():
        print("test_catalogue_index: skipped — run scripts/catalogue.py first")
        return 0

    F = json.loads((DATA / "filter-index.json").read_text(encoding="utf-8"))
    items = stored_order(json.loads(RAW.read_text(encoding="utf-8"))["items"])
    fails: list[str] = []

    def bad(msg):
        fails.append(msg)

    # ---- shape ------------------------------------------------------------
    n = F["n"]
    if n != len(items):
        bad(f"the index says {n:,} records, the catalogue holds {len(items):,}")
        return report(fails, 0, 0)
    for col in ("date", "pub", "pl", "tp", "en", "art", "cmp", "doc", "az"):
        if len(F[col]) != n:
            bad(f"column `{col}` has {len(F[col]):,} entries for {n:,} records")
    if fails:
        return report(fails, n, 0)

    # ---- the chunks, read back and stitched -------------------------------
    size = F["chunk"]
    rows = []
    for c in range(0, n, size):
        p = DATA / f"rows-{c // size:03d}.json"
        if not p.exists():
            bad(f"chunk {c // size:03d} is missing, so rows {c:,}-{c + size - 1:,} "
                f"cannot be drawn at all")
            return report(fails, n, 0)
        rows.extend(json.loads(p.read_text(encoding="utf-8")))
    if len(rows) != n:
        bad(f"the chunks hold {len(rows):,} rows for {n:,} records")
        return report(fails, n, 0)

    docids = {}
    if DOC_IDS.exists():
        import csv as _csv
        with open(DOC_IDS, encoding="utf-8", newline="") as fh:
            for r in _csv.DictReader(fh):
                docids[r["slug"]] = int(r["id"])

    # ---- every record, field by field -------------------------------------
    checked = 0
    for i, it in enumerate(items):
        want = {
            "title": it.get("title") or "",
            "url": it.get("url") or "",
            "slug": it.get("slug") or "",
            "hero": it.get("catalogue_hero") or "",
        }
        got = {"title": rows[i][0], "url": rows[i][1], "slug": rows[i][2], "hero": rows[i][3]}
        for k in want:
            if want[k] != got[k] and len(fails) < 12:
                bad(f"row {i:,} {k}: chunk has {got[k][:60]!r}, catalogue has {want[k][:60]!r}")
        if F["dates"][F["date"][i]] != (it.get("published") or "")[:10] and len(fails) < 12:
            bad(f"row {i:,} date: index has {F['dates'][F['date'][i]]!r}, "
                f"catalogue has {(it.get('published') or '')[:10]!r}")
        if F["pubs"][F["pub"][i]] != (it.get("publisher") or "") and len(fails) < 12:
            bad(f"row {i:,} publisher: index has {F['pubs'][F['pub'][i]]!r}")
        if [F["placekeys"][k] for k in F["pl"][i]] != (it.get("places") or []) and len(fails) < 12:
            bad(f"row {i:,} places: index has {[F['placekeys'][k] for k in F['pl'][i]]}, "
                f"catalogue has {it.get('places')}")
        if [F["topickeys"][k] for k in F["tp"][i]] != (it.get("topics") or []) and len(fails) < 12:
            bad(f"row {i:,} topics differ")
        if [F["ents"][k] for k in F["en"][i]] != (it.get("entities") or []) and len(fails) < 12:
            bad(f"row {i:,} entities differ")
        if F["art"][i] != (1 if it.get("artefact") else 0) and len(fails) < 12:
            bad(f"row {i:,} artefact flag differs")
        if F["comp"][F["cmp"][i]] != (it.get("body_completeness") or "") and len(fails) < 12:
            bad(f"row {i:,} body_completeness differs")
        if F["doc"][i] != docids.get(it.get("slug") or "", -1) and len(fails) < 12:
            bad(f"row {i:,} document id differs")
        checked += 1

    # ---- the facets, as sets rather than record by record ------------------
    # A facet is only ever right or wrong in aggregate: this is the count the reader
    # sees beside every option, computed both ways.
    for col, keys, field in (("pl", "placekeys", "places"),
                             ("tp", "topickeys", "topics"),
                             ("en", "ents", "entities")):
        mine, theirs = Counter(), Counter()
        for i, it in enumerate(items):
            for k in F[col][i]:
                mine[F[keys][k]] += 1
            for v in (it.get(field) or []):
                theirs[v] += 1
        if mine != theirs:
            off = {k for k in set(mine) | set(theirs) if mine[k] != theirs[k]}
            bad(f"the {field} facet counts differ on {len(off)} value(s): "
                f"{', '.join(sorted(off)[:6])}")

    years_mine, years_theirs = Counter(), Counter()
    for i, it in enumerate(items):
        d = F["dates"][F["date"][i]][:4]
        if d:
            years_mine["<2020" if int(d) < 2020 else d] += 1
        d2 = (it.get("published") or "")[:4]
        if d2 and d2.isdigit():
            years_theirs["<2020" if int(d2) < 2020 else d2] += 1
    if years_mine != years_theirs:
        bad(f"the year buckets differ: {years_mine} against {years_theirs}")

    # ---- the A-Z rank ------------------------------------------------------
    az = F["az"]
    if sorted(az) != list(range(n)):
        bad("the A–Z ranks are not a permutation of the rows — the sort would drop or "
            "duplicate records")
    else:
        # Restated here rather than imported, deliberately: `catalogue.py` opens no
        # vault but it does build the whole site, and what this needs to know is that
        # the ranks put the titles in order — not how they were arrived at. A rank
        # array that agrees with a re-derivation from the chunks is right whichever
        # code wrote it.
        want = sorted(range(n), key=lambda i: coll(rows[i][0]))
        for pos, i in enumerate(want):
            if az[i] != pos:
                bad(f"the A–Z rank of row {i:,} is {az[i]:,}, but its title sorts at "
                    f"{pos:,} — the sorted order and the ranks disagree")
                break

    return report(fails, n, checked)


def report(fails, n, checked) -> int:
    if not fails:
        print(f"test_catalogue_index: ok — the filter index and the row chunks "
              f"reproduce all {n:,} records ({checked:,} checked field by field, "
              f"every facet count and the A–Z order compared in full)")
        return 0
    print(f"test_catalogue_index: FAILED — {len(fails)} problem(s) in the split payload")
    for f in fails[:12]:
        print(f"    {f}")
    print("  `catalogue.py` → `split()` and the catalogue it was built from have "
          "diverged — see documentation/catalogue-split-plan.md, Part 3")
    return 1


if __name__ == "__main__":
    sys.exit(main())
