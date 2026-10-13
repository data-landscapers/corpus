#!/usr/bin/env python3
r"""study-nonstate-carry.py — Corpus's finance tables, carried into the non-state finance study.

    python scripts/study-nonstate-carry.py
    python scripts/study-nonstate-carry.py --dry

`maturity/documentation/maturity-study-method.md` §4: **start from what is already paid
for**, as `study-budget-carry.py` does for the budget tables.
`outputs/non-state-finance/{ISO3}-nonstate.csv` holds every commitment read from a deal
record, so `maturity-study-nonstatefinance.md`'s questions 1 and 2 are answered for the
countries it covers with no document opened:

- `money` = `committed`: one fact per commitment to a Private Sector, Fund or PPP
  beneficiary, Active, Approved or Completed, its instrument neither MoU nor Unknown, with
  an amount, starting in 2024 or later. **The fact is dated by the commitment's
  `start_year`**, which is what question 2 counts.
- `home` = `raised`: the same rows where `HOME` names the financier as the country's own.
  The list is read by hand from the rows' own descriptions; the `african` column says the
  continent and not the country.

Each fact is filed as a drafter would file it, `evidence/{ISO3}/facts/{n}.json`, under the
commitment's own record, which is appended to `readlist.csv` as `why = carried` where the
study's terms did not list it. Run it after `study-select.py` and before the drafters. A
facts file already there is left alone.

Exit: 0 written, 2 the study or the index cannot be read.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402
import vault_lib  # noqa: E402

STUDY = "nonstatefinance"
SUB, CLASS = "private", "private"
TABLES = os.path.join(study_lib.CORPUS, "outputs", "non-state-finance")
FROM = 2024
BENEFICIARY = ("Private Sector", "Fund", "PPP")
STATUS = ("Active", "Approved", "Completed", "Closed")
NOT_INSTRUMENT = ("MoU", "Unknown", "")
# (iso3, the start of the financier's name): the row's description has it as the country's own.
HOME = {("DZA", "Tell Group"), ("EGY", "Hassan Allam"), ("ZAF", "Ninety One"),
        ("ZAF", "Africa Data Centres")}


def facts(rows: list[dict], iso: str, held: set[str]) -> dict[str, list[dict]]:
    """`{slug: facts}` for one country's table."""
    out: dict[str, list[dict]] = collections.defaultdict(list)
    seen = set()
    for r in rows:
        year = r["start_year"].strip()
        if (r["beneficiary_type"] not in BENEFICIARY or r["status"] not in STATUS
                or r["instrument"] in NOT_INSTRUMENT or not year.isdigit() or int(year) < FROM
                or not r["commitment_usd_m"].strip() or r["record"] not in held
                or r["deal_id"] in seen):
            continue
        seen.add(r["deal_id"])
        to = r["recipient_organisation"].strip() or "a private digital beneficiary"
        text = (f"Finance tables: {r['financier']} committed USD {r['commitment_usd_m']} million "
                f"({r['instrument']}, {r['status']}) to {to}, starting {year}: {r['title']}.")
        base = {"sub_indicator": SUB, "fact": text, "as_of": year, "date_precision": "year",
                "system": r["title"], "class": CLASS}
        out[r["record"]].append({**base, "aspect": "money", "value": "committed"})
        if any(iso == i and r["financier"].startswith(f) for i, f in HOME):
            out[r["record"]].append({**base, "aspect": "home", "value": "raised"})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Carry the finance tables into the non-state finance study.")
    ap.add_argument("--dry", action="store_true", help="print the counts, write nothing")
    a = ap.parse_args(argv)
    try:
        study_lib.load(STUDY)
        index = {row["d"]["slug"]: row for row in vault_lib.load_index()}
    except (study_lib.StudyError, vault_lib.ForeignIndex, vault_lib.EmptyIndex) as e:
        print(f"study-nonstate-carry: {e}")
        return 2
    base = os.path.join(study_lib.study_dir(STUDY), "evidence")
    count: collections.Counter = collections.Counter()
    for iso in sorted(study_lib.countries()):
        table = os.path.join(TABLES, f"{iso}-nonstate.csv")
        if not os.path.exists(table):
            continue
        with open(table, encoding="utf-8-sig", newline="") as fh:
            by_slug = facts(list(csv.DictReader(fh)), iso, set(index))
        path = os.path.join(base, iso, "readlist.csv")
        mine = study_lib.read_csv(path)
        n_of = {r["slug"]: str(r["n"]) for r in mine if r.get("kind") == "raw"}
        nxt = max([int(r["n"]) for r in mine if str(r.get("n") or "").isdigit()] or [0])
        new_rows = []
        if by_slug:
            count["countries"] += 1
        for slug in sorted(by_slug):
            if slug not in n_of:
                nxt += 1
                d, fm = index[slug]["d"], index[slug]["fm"]
                new_rows.append({"n": nxt, "slice": "", "pass": "carried", "tier": "", "iso3": iso,
                                 "kind": "raw", "slug": slug, "read": "", "path": index[slug]["path"],
                                 "url": fm.get("url", ""), "title": fm.get("title", ""),
                                 "published": str(fm.get("published", "")), "places": iso,
                                 "why": "carried", "terms": "", "hits": 0, "words": d.get("words", 0)})
                n_of[slug] = str(nxt)
            out = os.path.join(base, iso, "facts", f"{n_of[slug]}.json")
            if os.path.exists(out):
                continue
            for f in by_slug[slug]:
                count[f["value"]] += 1
            if a.dry:
                continue
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8", newline="\n") as fh:
                json.dump({"slug": slug, "facts": by_slug[slug], "systems": [],
                           "note": "carried from outputs/non-state-finance; no document opened"},
                          fh, ensure_ascii=False, indent=1)
                fh.write("\n")
        if new_rows and not a.dry:
            study_lib.write_csv(path, study_lib.READLIST_FIELDS, mine + new_rows)
    print("study-nonstate-carry: " + ", ".join(f"{k}: {count[k]}" for k in ("countries", "committed", "raised"))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
