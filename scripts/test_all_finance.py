#!/usr/bin/env python3
"""test_all_finance.py — the join behind `/finance/all/` maps each side as the spec says.

    python scripts/test_all_finance.py

`documentation/joined-up-finance-spec.csv` is the mapping. What can go wrong silently is a
value in the wrong unit, a budget title that says one name three times, and a column the
dictionary does not describe.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import finance  # noqa: E402

failures = 0


def check(label, got, want):
    global failures
    ok = got == want
    failures += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + ("" if ok else f"  — got {got!r}, want {want!r}"))


NS = {"recipient": "KEN", "start_year": "2025 (2025-07-06)", "primary_topic": "Connectivity",
      "aid": "true", "african": "non-African", "financier": "World Bank", "recipient_organisation": "ICT Authority",
      "title": "Fibre", "description": "A loan.", "commitment_usd_m": "22.5",
      "deal_id": "wb-ken-1", "scope": "partial", "scope_basis": "Broadband with power."}
BD = {"country": "KEN", "report_year": "2025", "primary_topic": "Registries",
      "admin_head": "Interior", "spending_entity": "Immigration", "programme": "Migration",
      "sub_programme": "Population Registration", "line_name": "population registration",
      "purpose": "Runs the register.", "budget_usd": "396816", "deal_id": "ken-2025-x",
      "scope_confidence": "whole", "scope_basis": "Named system."}

rows = {r["deal_id"]: r for r in finance.all_finance_rows(
    [NS, {**NS, "deal_id": "wb-ken-2", "aid": "false", "commitment_usd_m": ""},
     {**NS, "deal_id": "afx-ken-1", "aid": "false", "african": "African"},
     {**NS, "deal_id": "new-ken-1", "aid": "false", "african": ""},
     {**NS, "deal_id": "wb-ken-old", "start_year": "2023"},
     {**NS, "deal_id": "wb-ken-undated", "start_year": ""}], [BD])}
ns, other, bd = rows["wb-ken-1"], rows["wb-ken-2"], rows["ken-2025-x"]

check("every row has exactly the published columns", list(ns), list(finance.ALL_COLUMNS))
check("a non-state value is whole dollars", ns["value_usd"], "22500000")
check("its year is the bare year", ns["year"], "2025")
check("a commitment before 2024, or with no year, is not joined",
      sorted(rows), ["afx-ken-1", "ken-2025-x", "new-ken-1", "wb-ken-1", "wb-ken-2"])
check("aid is aid", ns["type"], "aid")
check("aid is not split by where the financier is from", "African" in ns["type"], False)
check("anything else from a non-African financier", other["type"], "other non-African finance")
check("or from an African one", rows["afx-ken-1"]["type"], "other African finance")
check("a financier the lookup does not place stays other finance",
      rows["new-ken-1"]["type"], "other finance")
check("no amount stays blank, never zero", other["value_usd"], "")
check("a non-state row carries its scope", (ns["scope"], ns["scope_basis"]),
      ("partial", "Broadband with power."))
check("a budget line is a budget", bd["type"], "budget")
check("its financier is the admin head", bd["financier"], "Interior")
check("its recipient is the spending entity", bd["recipient"], "Immigration")
check("its value is budget_usd as it stands", bd["value_usd"], "396816")
check("its title says each name once, whatever the case",
      bd["title"], "Migration : Population Registration")
check("a title of one repeated name is that name",
      finance.budget_title({"programme": "X", "sub_programme": "", "line_name": "X"}), "X")

with open(finance.ALL_META, encoding="utf-8-sig", newline="") as fh:
    check("the dictionary describes the columns, in order",
          [m["column"] for m in csv.DictReader(fh)], list(finance.ALL_COLUMNS))

print("\nall cases pass" if not failures else f"\n{failures} FAILED")
sys.exit(1 if failures else 0)
