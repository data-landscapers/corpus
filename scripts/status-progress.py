#!/usr/bin/env python3
"""The status-init checklist — which countries are through, and what the rest will cost.

    python scripts/status-progress.py            # rewrite logs/status-init-progress.csv, print a summary
    python scripts/status-progress.py --print    # print it without writing

**Done is derived, never ticked.** A country is through when its status report carries
`built_by: STATUS-INIT`, which is the same test `report-render.py` and `status-check.py` use and
the same one that stops the ledger renderer overwriting it. So this file cannot drift out of step
with the work: re-run it and it tells the truth, whereas a hand-maintained checklist tells you what
someone remembered to tick. That matters over a 54-country campaign run one country per session.

**The `notes` column is yours and is preserved** across every rewrite. It is the one column this
script does not own, so a note against a country survives regeneration — which is what makes the
file a worksheet rather than a report.

Rows are ordered by evidence volume, heaviest first, so the file doubles as the run order: the plan
is big ones first, and the right measure of "big" is how much compiled evidence a country has, not
its population or its GDP. NGA is 348KB across fourteen intersections; MRT is 12KB across two.
"""

import argparse
import csv
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402

OSINT = r"C:\OSINT"
PLACES = os.path.join(OSINT, "wiki", "places")
INTERSECTIONS = os.path.join(OSINT, "wiki", "intersections")
VOCAB = os.path.join(S.REPO, "outputs", "vocab", "countries.csv")
OUT = os.path.join(S.REPO, "logs", "status-init-progress.csv")

COLUMNS = ["iso3", "country", "region", "done", "compiled", "sections", "sources", "acquire",
           "intersections", "evidence_kb", "hub_kb", "dpi_rows", "finance_rows", "notes"]


def names():
    """ISO3 -> (country, region), from the published vocabulary snapshot."""
    out = {}
    with open(VOCAB, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            vals = {re.sub(r"[^a-z0-9]", "", (k or "").lower()): (v or "").strip()
                    for k, v in row.items()}
            if vals.get("iso3"):
                out[vals["iso3"].upper()] = (vals.get("countryname", ""), vals.get("region", ""))
    return out


def evidence():
    """place -> (file count, total bytes), over the intersections. One pass, frontmatter only."""
    out = defaultdict(lambda: [0, 0])
    for fn in sorted(os.listdir(INTERSECTIONS)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(INTERSECTIONS, fn)
        with open(path, encoding="utf-8", errors="replace") as fh:
            m = re.search(r"^place:\s*\[?\s*([A-Z]{3})", fh.read(1500), re.M)
        if m:
            out[m.group(1)][0] += 1
            out[m.group(1)][1] += os.path.getsize(path)
    return out


def dpi_counts():
    out = defaultdict(int)
    with open(S.DPI_CSV, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            out[(row.get("Country") or "").strip().upper()] += 1
    return out


def finance_counts():
    out = defaultdict(int)
    with open(S.FINANCE_CSV, encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh)
        key = rd.fieldnames[0]
        for row in rd:
            out[(row.get(key) or "").strip().upper()] += 1
    return out


def existing_notes():
    """Whatever is in the `notes` column today. The one thing here this script does not own."""
    if not os.path.exists(OUT):
        return {}
    with open(OUT, encoding="utf-8-sig", newline="") as fh:
        return {r["iso3"]: r.get("notes", "") for r in csv.DictReader(fh) if r.get("iso3")}


def build():
    look, ev, dpi, fin, notes = names(), evidence(), dpi_counts(), finance_counts(), existing_notes()
    units = sorted(u for u in os.listdir(S.REPORTS)
                   if os.path.isdir(os.path.join(S.REPORTS, u)) and not u.startswith("X"))
    rows = []
    for iso in units:
        path = os.path.join(S.REPORTS, iso, f"{iso}-status.md")
        fm = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                fm = S.frontmatter(fh.read(4096))
        done = fm.get("built_by") == "STATUS-INIT"
        country, region = look.get(iso, (iso, ""))
        n, size = ev.get(iso, [0, 0])
        rows.append({
            "iso3": iso, "country": country, "region": region,
            "done": "yes" if done else "",
            "compiled": fm.get("compiled", "") if done else "",
            "sections": fm.get("sections_written", "") if done else "",
            "sources": fm.get("sources_cited", "") if done else "",
            "acquire": fm.get("acquire_lines", "") if done else "",
            "intersections": n,
            "evidence_kb": round(size / 1024),
            "hub_kb": round(os.path.getsize(os.path.join(PLACES, f"{iso}.md")) / 1024)
                      if os.path.exists(os.path.join(PLACES, f"{iso}.md")) else 0,
            "dpi_rows": dpi.get(iso, 0),
            "finance_rows": fin.get(iso, 0),
            "notes": notes.get(iso, ""),
        })
    rows.sort(key=lambda r: (-r["evidence_kb"], r["iso3"]))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--print", dest="show", action="store_true",
                    help="print the table without writing the file")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    rows = build()
    if not args.show:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(rows)

    done = [r for r in rows if r["done"]]
    todo = [r for r in rows if not r["done"]]
    print(f"{'':4} {'ISO':4} {'country':<26} {'int':>4} {'eviKB':>6} {'dpi':>4} {'fin':>4}  notes")
    for r in rows:
        mark = "[x]" if r["done"] else "[ ]"
        print(f"{mark:4} {r['iso3']:4} {r['country'][:26]:<26} {r['intersections']:>4} "
              f"{r['evidence_kb']:>6} {r['dpi_rows']:>4} {r['finance_rows']:>4}  {r['notes']}")
    print(f"\n{len(done)} of {len(rows)} through · {len(todo)} to go · "
          f"{sum(r['evidence_kb'] for r in todo):,} KB of evidence remaining")
    if not args.show:
        print(f"-> {os.path.relpath(OUT, S.REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
