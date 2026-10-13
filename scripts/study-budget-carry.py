#!/usr/bin/env python3
r"""study-budget-carry.py — Corpus's budget tables, carried into the domestic financing study.

    cd scripts/.workroot
    python scripts/study-budget-carry.py
    python scripts/study-budget-carry.py --dry

`maturity/documentation/maturity-study-method.md` §4: **start from what is already paid
for**. `outputs/budgets/{ISO3}-budget.csv` holds every digital line read from a country's
finance laws and estimates, so three of `maturity-study-domesticfinancing.md`'s four
questions are answered for most countries with no document opened:

- `budget` = `allocated`: the latest budget year with an amount against a digital line;
- `budget` = `rose` or `fell`: the lines held in both of the last two budget years, added
  up and compared, in the country's own currency. Flat is `fell`: question 2 asks for
  higher. A country with no line in both years gets neither;
- `budget` = `spent`: the latest budget year with an amount actually spent or audited.

A transfer line is left out of every sum: it is counted again where it lands. A budget year
is ordered by the first four-digit number in its label, and a label with none is passed
over. **A fact is dated by the document it was read from**, not by the label: Ethiopia's
budget years are in its own calendar.

Each fact is filed as a drafter would file it, `evidence/{ISO3}/facts/{n}.json`, under the
table's own source, which is appended to `readlist.csv` as `why = carried` where the study's
terms did not list it. `study-profile.py --merge` then folds carried and drafted alike. Run
it after `study-select.py` and before the drafters. A facts file already there is left alone.

Exit: 0 written, 2 the study or the index cannot be read.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402
import vault_lib  # noqa: E402

STUDY = "domesticfinancing"
SUB, CLASS = "financing", "financing"
BUDGETS = os.path.join(study_lib.CORPUS, "outputs", "budgets")
YEAR = re.compile(r"\d{4}")


def num(s: str) -> float | None:
    try:
        return float((s or "").replace(",", ""))
    except ValueError:
        return None


def key(r: dict) -> tuple:
    return (r["admin_head_code"], r["programme_code"], r["sub_programme_code"], r["econ_class"],
            r["programme_line"])


def facts(rows: list[dict], held: set[str]) -> dict[str, list[dict]]:
    """`{slug: facts}` for one country's table."""
    given: dict[str, dict] = collections.defaultdict(dict)       # fy -> line -> amount
    spent: dict[str, float] = collections.defaultdict(float)
    source: dict[tuple, collections.Counter] = collections.defaultdict(collections.Counter)
    cur = ""
    for r in rows:
        if not YEAR.search(r["fy"]) or r["is_transfer"] == "true" or r["source_slug"] not in held:
            continue
        cur = cur or r["currency"]
        amount = num(r["appropriated"]) or num(r["revised"]) or num(r["proposed"])
        if amount:
            given[r["fy"]][key(r)] = given[r["fy"]].get(key(r), 0) + amount
            source[("given", r["fy"])][r["source_slug"]] += amount
        out = num(r["audited"]) or num(r["actual"])
        if out:
            spent[r["fy"]] += out
            source[("spent", r["fy"])][r["source_slug"]] += out
    order = lambda fy: (int(YEAR.search(fy).group()), fy)  # noqa: E731
    out: dict[str, list[dict]] = collections.defaultdict(list)

    def add(kind: str, fy: str, value: str, text: str) -> None:
        slug = source[(kind, fy)].most_common(1)[0][0]
        out[slug].append({"sub_indicator": SUB, "aspect": "budget", "value": value, "fact": text,
                          "as_of": slug[:10], "date_precision": "day",
                          "system": f"State budget, {fy}", "class": CLASS})

    years = sorted(given, key=order)
    if years:
        fy = years[-1]
        add("given", fy, "allocated",
            f"Budget tables: the budget for {fy} gives {sum(given[fy].values()):,.0f} {cur} to "
            f"{len(given[fy])} digital line(s). Dated by the budget document.")
    if len(years) > 1:
        a, b = years[-2], years[-1]
        both = set(given[a]) & set(given[b])
        if both:
            was, now = sum(given[a][k] for k in both), sum(given[b][k] for k in both)
            add("given", b, "rose" if now > was else "fell",
                f"Budget tables: the {len(both)} digital line(s) held in both years total "
                f"{now:,.0f} {cur} for {b} against {was:,.0f} for {a}"
                + (f", {100 * (now - was) / was:+.1f} per cent" if was else "")
                + f"; {len(given[b])} lines are held for {b}. Dated by the budget document.")
    if spent:
        fy = sorted(spent, key=order)[-1]
        add("spent", fy, "spent",
            f"Budget tables: {spent[fy]:,.0f} {cur} is published as actually spent on digital "
            f"lines for {fy}. Dated by the document that gives the figure.")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Carry the budget tables into the financing study.")
    ap.add_argument("--dry", action="store_true", help="print the counts, write nothing")
    a = ap.parse_args(argv)
    try:
        study_lib.load(STUDY)
        index = {row["d"]["slug"]: row for row in vault_lib.load_index()}
    except (study_lib.StudyError, vault_lib.ForeignIndex, vault_lib.EmptyIndex) as e:
        print(f"study-budget-carry: {e}")
        return 2
    base = os.path.join(study_lib.study_dir(STUDY), "evidence")
    count: collections.Counter = collections.Counter()
    for iso in sorted(study_lib.countries()):
        table = os.path.join(BUDGETS, f"{iso}-budget.csv")
        if not os.path.exists(table):
            continue
        with open(table, encoding="utf-8-sig", newline="") as fh:
            by_slug = facts(list(csv.DictReader(fh)), set(index))
        path = os.path.join(base, iso, "readlist.csv")
        mine = study_lib.read_csv(path)
        n_of = {r["slug"]: str(r["n"]) for r in mine if r.get("kind") == "raw"}
        nxt = max([int(r["n"]) for r in mine if str(r.get("n") or "").isdigit()] or [0])
        new_rows = []
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
                           "note": "carried from outputs/budgets; no document opened"},
                          fh, ensure_ascii=False, indent=1)
                fh.write("\n")
        if new_rows and not a.dry:
            study_lib.write_csv(path, study_lib.READLIST_FIELDS, mine + new_rows)
    print("study-budget-carry: " + ", ".join(f"{k}: {count[k]}" for k in ("allocated", "rose", "fell", "spent"))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
