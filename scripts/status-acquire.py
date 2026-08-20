#!/usr/bin/env python3
"""The acquire feed — `STATUS-INIT.md` -> *Sources and conflicts*.

    python scripts/status-acquire.py NGA --compiled 2026-08-15

**The test is whether the source is held, not which intermediary carried it** (Bill, 2026-08-15).
So this asks the catalogue of every URL the status report cites, and only of one the catalogue does
not resolve:

* held — nothing is owed;
* not held, before 2024 — baseline material, outside the collection perimeter, nothing owed;
* not held, 2024 or later — a gap in the daily sweep, and it owes a line.

**One file for all of Africa, not one per country** *(Bill, 2026-08-15)*. `{ISO3}-acquire.md` put
each country's findings in its own markdown table inside its own report folder, which is the wrong
shape for what this is: a work queue Bill takes into an OSINT session and works down. Fifty-four
tables cannot be sorted by publisher, filtered to what is still outstanding, or counted. So the
lines accumulate in `africa-acquire.csv` in the transfer folder (`status_lib.EXCHANGE`), one row per source with the country in a column, and
`logs/` is where they belong — it is where every other OSINT-ward artefact of this campaign lives.

**A run rewrites only its own country's rows.** Every other country's pass through untouched, so
re-running one country cannot disturb the fifty-three already done.

**The `status` and `notes` columns are Bill's and are preserved** across every rewrite, keyed on the
country and the URL. That is the same rule `status-progress.py` follows for its `notes` column and
for the same reason: a file that loses your working state on regeneration is a report, not a
worksheet.

The publication date, publisher and title of a cited URL are not in the assembled document, so they
come from `prep/scope/{ISO3}/pool.json`, which is what stage 1 established about that source.
"""

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402

OUT = S.ACQUIRE_CSV      # the transfer folder, outside both repos — see status_lib.EXCHANGE
COLUMNS = ["iso3", "published", "publisher", "title", "url", "sub_section", "found",
           "status", "notes"]
MINE = ("status", "notes")          # Bill's columns. This script never writes over them.


def existing():
    """Every row on file today, and whatever is in Bill's columns, keyed on (iso3, url)."""
    rows, kept = [], {}
    if not os.path.exists(OUT):
        return rows, kept
    with open(OUT, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if not row.get("iso3"):
                continue
            rows.append(row)
            kept[(row["iso3"], row.get("url", ""))] = {k: row.get(k, "") for k in MINE}
    return rows, kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iso3")
    ap.add_argument("--compiled", required=True, help="the report's compiled date")
    args = ap.parse_args()
    iso = args.iso3.upper()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    text = open(os.path.join(S.REPORTS, iso, f"{iso}-status.md"), encoding="utf-8").read()

    pool = {}
    ppath = os.path.join(S.REPO, "prep", "scope", iso, "pool.json")
    for fact in json.load(open(ppath, encoding="utf-8")):
        for url in [fact["url"]] + list(fact.get("also") or []):
            pool.setdefault(url, fact)

    cat = S.catalogue_urls()

    # Which sub-section cited it. The first is the one the line names — an acquisition is a source
    # to go and get, not a concordance.
    where = {}
    for slug, label, prose in S.sections(text):
        for url in S.links(prose):
            where.setdefault(url, slug or label)

    old_rows, kept = existing()
    mine, unknown = [], []
    for url in sorted(S.links(text)):
        if url in cat:
            continue
        fact = pool.get(url)
        published = (fact or {}).get("published") or ""
        if published < "2024":
            continue
        if not fact:
            unknown.append(url)
        row = {
            "iso3": iso,
            "published": published or "????",
            "publisher": (fact or {}).get("publisher") or "",
            "title": (fact or {}).get("title") or "",
            "url": url,
            "sub_section": where.get(url, ""),
            "found": args.compiled,
        }
        row.update(kept.get((iso, url), {k: "" for k in MINE}))
        mine.append(row)

    out = [r for r in old_rows if r["iso3"] != iso] + mine
    out.sort(key=lambda r: (r["iso3"], r.get("published", ""), r.get("publisher", "")))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    units = len({r["iso3"] for r in out})
    print(f"{os.path.relpath(OUT, S.REPO)}: {len(mine)} line(s) for {iso}, "
          f"{len(out)} in all across {units} unit(s)")
    for u in unknown:
        print(f"  ! no pool record for {u} — date and publisher unknown", file=sys.stderr)


if __name__ == "__main__":
    main()
