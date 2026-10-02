#!/usr/bin/env python3
r"""budget-votes.py — check D of the budget data review: which votes have been read.

    python scripts/budget-votes.py            # check budgets/votes-read.csv and print the tally
    python scripts/budget-votes.py GHA        # one country, vote by vote

The plan is the share's `documentation/budget-data-review.md`. `budgets/votes-read.csv` is a
source file like the country files beside it: a sitting writes it and nothing regenerates
it. One row per country, fiscal year and vote, every vote in the summary table of the
document `source_slug` names, each marked

- `lines taken` — its cost centres or sub-heads were read and rows were written from them;
- `read, none digital` — they were read and nothing in them is a digital line;
- `not read` — everything else, including a vote whose rows came from a summary schedule.

**A vote is read only when its cost centres or sub-heads have been read** — the Ghana rule.
Ghana's statistics office is a cost centre of the finance ministry's vote, and a reading of
that vote's programme table had passed it by. So rows held under a vote do not make it read,
and this file is the only thing that says so. It is what gives the dataset a denominator: a
country-year with 3 votes read of 39 is a different thing from one with 39 of 39.

Checked here: the columns, the three statuses, one row per vote, a `lines taken` vote
holding rows in the country file for that year, and every admin head a country-year's rows
name being a vote in this file once the country-year is in it at all.

Exit: 0 the file passes, 1 it does not, 2 there is no file.
"""
from __future__ import annotations

import collections
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget_source  # noqa: E402

PATH = os.path.join(budget_source.BUDGETS, "votes-read.csv")
COLUMNS = ("iso3", "fiscal_year", "vote_code", "vote", "status", "basis", "source_slug", "read")
STATUSES = ("lines taken", "read, none digital", "not read")


def read() -> list[dict]:
    with open(PATH, encoding="utf-8-sig", newline="") as fh:
        rdr = csv.DictReader(fh)
        if tuple(rdr.fieldnames or ()) != COLUMNS:
            raise SystemExit(f"budget-votes: columns are {rdr.fieldnames}, expected {list(COLUMNS)}")
        return list(rdr)


def check(votes: list[dict]) -> list[str]:
    errors, seen = [], set()
    heads: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    for iso3, fy, row in budget_source.rows():
        heads[(iso3, fy)].add((row.get("admin_head_code") or "").strip())
    covered = collections.defaultdict(set)
    slugs = budget_source._slugs()
    for n, v in enumerate(votes, 2):
        where = f"line {n} {v['iso3']} {v['fiscal_year']} {v['vote_code'] or v['vote']}"
        key = (v["iso3"], v["fiscal_year"], v["vote_code"], v["vote"])
        if key in seen:
            errors.append(f"{where}: the vote is listed twice")
        seen.add(key)
        if v["status"] not in STATUSES:
            errors.append(f"{where}: status {v['status']!r} is not one of {STATUSES}")
        if not v["vote"] or not v["source_slug"]:
            errors.append(f"{where}: a vote names itself and the document that lists it")
        elif slugs is not None and v["source_slug"] not in slugs:
            errors.append(f"{where}: source_slug {v['source_slug']} is not in the catalogue")
        if v["status"] != "not read" and not v["read"]:
            errors.append(f"{where}: a vote that was read carries the date it was read")
        if v["status"] == "lines taken" and v["vote_code"] not in heads[(v["iso3"], v["fiscal_year"])]:
            errors.append(f"{where}: lines taken, and no row of that year carries the vote's code")
        covered[(v["iso3"], v["fiscal_year"])].add(v["vote_code"])
    for key, codes in sorted(covered.items()):
        for code in sorted(heads[key] - codes):
            errors.append(f"{key[0]} {key[1]}: rows are held under admin head {code}, which is not a vote here")
    return errors


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not os.path.exists(PATH):
        print("budget-votes: no budgets/votes-read.csv", file=sys.stderr)
        return 2
    votes = read()
    errors = check(votes)
    for e in errors:
        print("budget-votes: " + e)
    only = args[0].upper() if args else ""
    tally: dict[tuple[str, str], collections.Counter] = collections.defaultdict(collections.Counter)
    for v in votes:
        tally[(v["iso3"], v["fiscal_year"])][v["status"]] += 1
        if only == v["iso3"]:
            print(" | ".join(v[c] for c in ("fiscal_year", "vote_code", "vote", "status", "basis")))
    for (iso3, fy), c in sorted(tally.items()):
        if not only or only == iso3:
            total = sum(c.values())
            print(f"budget-votes: {iso3} {fy}: {total - c['not read']} of {total} votes read "
                  f"({c['lines taken']} with lines, {c['read, none digital']} none digital)")
    print(f"budget-votes: {len(tally)} country-years, {len(votes)} votes"
          + (f", {len(errors)} error(s)" if errors else " - ok"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
