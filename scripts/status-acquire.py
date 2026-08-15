#!/usr/bin/env python3
"""Write the acquire file — `STATUS-INIT.md` -> *Sources and conflicts*.

    python scripts/status-acquire.py NGA

**The test is whether the source is held, not which intermediary carried it** (Bill, 2026-08-15).
So this asks the catalogue, and only of a URL the catalogue does not resolve:

* held — nothing is owed;
* not held, before 2024 — baseline material, outside the collection perimeter, nothing owed;
* not held, 2024 or later — a gap in the daily sweep, and it owes a line.

The publication date, publisher and title of a cited URL are not in the assembled document, so they
come from `prep/scope/{ISO3}/pool.json`, which is what stage 1 established about that source. A URL
the pool cannot describe is listed with what is known and flagged, rather than dropped: check F
tests the file, and a silently missing line is the one failure mode that looks like success.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iso3")
    ap.add_argument("--compiled", required=True, help="the report's compiled date")
    ap.add_argument("--country", required=True)
    args = ap.parse_args()
    iso = args.iso3.upper()

    path = os.path.join(S.REPORTS, iso, f"{iso}-status.md")
    text = open(path, encoding="utf-8").read()

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

    rows, unknown = [], []
    for url in sorted(S.links(text), key=lambda u: where.get(u, "")):
        if url in cat:
            continue
        fact = pool.get(url)
        published = (fact or {}).get("published") or ""
        if published < "2024":
            continue
        if not fact:
            unknown.append(url)
        rows.append((published or "????", (fact or {}).get("publisher") or "",
                     ((fact or {}).get("title") or "").replace("|", "/"),
                     url, where.get(url, "")))
    rows.sort()

    out = [f"---",
           f"title: {args.country} — sources found by STATUS-INIT and not held",
           f"place: {iso}",
           f"compiled: {args.compiled}",
           f"built_by: STATUS-INIT",
           f"---",
           "",
           "| Published | Publisher | Title | URL | Sub-section |",
           "| --- | --- | --- | --- | --- |"]
    out += [f"| {d} | {p} | {t} | {u} | {s} |" for d, p, t, u, s in rows]
    out.append("")

    apath = os.path.join(S.REPORTS, iso, f"{iso}-acquire.md")
    with open(apath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))

    print(f"{apath}: {len(rows)} line(s)")
    for u in unknown:
        print(f"  ! no pool record for {u} — date and publisher unknown", file=sys.stderr)


if __name__ == "__main__":
    main()
