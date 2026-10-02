#!/usr/bin/env python3
r"""budget-holes.py — check A of the budget data review: the holes a count can find.

    python scripts/budget-holes.py            # write logs/budget-holes.csv and print the tally
    python scripts/budget-holes.py GHA        # one country, printed and not written

The plan is the share's `documentation/budget-data-review.md`. A hole is one of three kinds:
a document not held, a document held and not read, and a line passed over inside a document
that was read. **This finds the first two and never the third** — a file whose rows look
complete says nothing here, which is why checks B, C and D exist.

Six signals, one row per country, fiscal year, signal and subject:

- `no-country` — a country in `lookups/countries.csv` with no budget file at all.
- `year-missing` — a fiscal year from `FIRST_FY` to `LAST_FY` with no rows.
- `year-thin` — a year holding under half the lines of that country's fullest year.
- `country-thin` — a country under `THIN_COUNTRY` lines across every year.
- `head-not-every-year` — an `admin_head` present in one held year and absent from another,
  matched on its code where the country prints one in every year and on its name otherwise.
- `document-uncited` — a catalogued budget document for the country-year that no row cites.
  Only the types that carry a budget stage: a statement or a procurement plan has no lines
  to read (`budget-doc-types.csv`, stages `none` and `as-stated`). `detail` says whether
  `logs/budget-extract.csv` names the document: one it names was read and gave no row of its
  own, and one it does not name is the held-and-not-read hole.

**These are candidates, not findings.** A thin year is often a year whose only held document
is an act with no programme annex, and a head missing from a year is often a renamed ministry.
Each row is where to look, and the looking is a BUDGET-EXTRACT sitting or a note to OSINT.

The output carries no date column, so a run that finds nothing new changes no byte.

Exit: 0 written, 2 there is no `budgets/` folder.
"""
from __future__ import annotations

import collections
import csv
import importlib.util
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget_source  # noqa: E402

ROOT = budget_source.ROOT
OUT = os.path.join(ROOT, "logs", "budget-holes.csv")
COUNTRIES = os.path.join(ROOT, "lookups", "countries.csv")
EXTRACT_LOG = os.path.join(ROOT, "logs", "budget-extract.csv")
FIRST_FY, LAST_FY = 2024, 2026
THIN_COUNTRY = 30
COLUMNS = ("iso3", "fiscal_year", "signal", "subject", "detail")


def fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def countries() -> list[str]:
    """Every country the site covers: the lookup's rows that are not a region."""
    with open(COUNTRIES, encoding="utf-8-sig", newline="") as fh:
        return sorted(r["iso-3"] for r in csv.DictReader(fh) if not r["iso-3"].startswith("X"))


def budget_documents() -> list[dict]:
    """`budget-watch.py`'s list of held budget documents, kept to the catalogued ones."""
    path = os.path.join(ROOT, "scripts", "budget-watch.py")
    spec = importlib.util.spec_from_file_location("budget_watch", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    stages = mod.doc_stages()
    catalogued = budget_source._slugs() or set()
    return [d for d in mod.budget_documents()
            if d["slug"] in catalogued and stages.get(d["doc_type"], "none") not in ("none", "as-stated")]


def head_key(row: dict, by_code: bool) -> str:
    return (row.get("admin_head_code") or "").strip() if by_code else fold(row.get("admin_head"))


def holes(only: str = "") -> list[dict]:
    by_country: dict[str, list[dict]] = collections.defaultdict(list)
    for iso3, _, row in budget_source.rows():
        by_country[iso3].append(row)
    span = [str(y) for y in range(FIRST_FY, LAST_FY + 1)]
    out: list[dict] = []

    def add(iso3, fy, signal, subject, detail):
        out.append(dict(zip(COLUMNS, (iso3, fy, signal, subject, detail))))

    docs = budget_documents()
    with open(EXTRACT_LOG, encoding="utf-8-sig") as fh:
        logged = fh.read()
    cited = {(r.get("source_slug") or "").strip() for rs in by_country.values() for r in rs}
    for iso3 in countries():
        if only and iso3 != only:
            continue
        rs = by_country.get(iso3, [])
        if not rs:
            add(iso3, "", "no-country", "", "no budget file")
        else:
            count = collections.Counter(budget_source.fy_of(r) for r in rs)
            fullest = max(count.values())
            profile = "/".join(str(count.get(y, 0)) for y in span)
            for y in span:
                if not count.get(y):
                    add(iso3, y, "year-missing", "", f"lines by year {profile}")
                elif count[y] * 2 < fullest:
                    add(iso3, y, "year-thin", "", f"{count[y]} lines against {fullest}; by year {profile}")
            if len(rs) < THIN_COUNTRY:
                add(iso3, "", "country-thin", "", f"{len(rs)} lines; by year {profile}")
            held = [y for y in span if count.get(y)]
            by_code = all((r.get("admin_head_code") or "").strip() for r in rs)
            heads: dict[str, dict[str, str]] = collections.defaultdict(dict)
            for r in rs:
                heads[head_key(r, by_code)][budget_source.fy_of(r)] = (r.get("admin_head") or "").strip()
            for key, years in sorted(heads.items()):
                name = next(iter(years.values()))
                for y in held:
                    if y not in years:
                        add(iso3, y, "head-not-every-year", name,
                            "held in " + ", ".join(sorted(years)))
        for d in sorted(docs, key=lambda d: (d["fy"] or 0, d["slug"])):
            if d["iso3"] == iso3 and d["slug"] not in cited and d["fy"] and FIRST_FY <= d["fy"] <= LAST_FY:
                add(iso3, str(d["fy"]), "document-uncited", d["slug"], d["doc_type"]
                    + ("; in the extract log" if d["slug"] in logged else "; not in the extract log"))
    return out


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not os.path.isdir(budget_source.BUDGETS):
        print("budget-holes: no budgets/ folder", file=sys.stderr)
        return 2
    only = args[0].upper() if args else ""
    rows = holes(only)
    tally = collections.Counter(r["signal"] for r in rows)
    where = collections.defaultdict(set)
    for r in rows:
        where[r["signal"]].add(r["iso3"])
    if only:
        for r in rows:
            print(" | ".join(r[c] for c in COLUMNS))
    else:
        with open(OUT, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    print("budget-holes: " + ", ".join(
        f"{s} {n} in {len(where[s])} countries" for s, n in sorted(tally.items()))
        + ("" if only else f" -> {os.path.relpath(OUT, ROOT)}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
