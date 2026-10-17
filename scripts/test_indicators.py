#!/usr/bin/env python3
"""test_indicators.py — the indicator frame.

    python scripts/test_indicators.py

`lookups/indicators.csv` is the canonical list and is hand-maintained, so the things a hand can get
wrong are checked: a duplicate or missing id, a subject outside the taxonomy, a chapter the
taxonomy does not carry. The frame covering every Level-2 subject is asserted rather than assumed,
because the frame claims to ask the same set of questions of every country.

The rendering and checks of the progress report this file also tested retired with it on
2026-10-17 (Bill). Nothing in this file touches `outputs/`.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import indicators_lib as il  # noqa: E402

_spec = importlib.util.spec_from_file_location("rr", CORPUS / "scripts" / "report-render.py")
rr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rr)

failures = []


def check(what, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {what}"
          + ("" if ok else f"\n       got {got!r}\n       want {want!r}"))
    if not ok:
        failures.append(what)


# --- the frame ------------------------------------------------------------------------------
print("the frame")
frame = il.frame()
check("every indicator has an id", all(r["indicator_id"] for r in frame), True)
check("ids are unique", len({r["indicator_id"] for r in frame}), len(frame))
tax = {r["Key"]: r["Level 1"] for r in csv.DictReader(
    open(CORPUS / "lookups" / "taxonomy.csv", encoding="utf-8-sig"))}
check("every subject is in the taxonomy",
      sorted({r["subject"] for r in frame} - set(tax)), [])
check("every subject in the taxonomy has at least one indicator — §1's 'same set of questions'",
      sorted(set(tax) - {r["subject"] for r in frame}), [])
check("each indicator's chapter is its subject's Level-1 parent",
      [r["indicator_id"] for r in frame if tax.get(r["subject"]) != r["chapter"]], [])
check("every assessed indicator has a kind from the three",
      [r["indicator_id"] for r in frame if r["assessed"] and r["kind"] not in il.KINDS], [])
check("every row not assessed carries a retired date",
      [r["indicator_id"] for r in frame if not r["assessed"] and not r["retired"]], [])
check("the assessed view holds no row with assessed = 0",
      [r["indicator_id"] for r in il.assessed() if not r["assessed"]], [])
check("the assessed view is the frame less the unassessed rows",
      len(il.assessed()), sum(1 for r in frame if r["assessed"]))
check("the frame itself still returns every row, assessed or not",
      len(frame) > len(il.assessed()), True)
check("the id is the subject plus a slug of the indicator, so it is composable by nobody",
      all(r["indicator_id"].startswith(r["subject"] + "--") for r in frame), True)

order = [s for _, s, _ in rr.sections("ZAF")[0]]
grouped = il.by_chapter(order)
check("by_chapter returns the taxonomy's chapters in the taxonomy's order",
      [c for c, _ in grouped], [c for c in order if c in {r["chapter"] for r in frame}])
check("grouping loses no indicator", sum(len(v) for _, v in grouped), len(frame))

print(f"\n{'PASS' if not failures else 'FAIL — ' + str(len(failures)) + ' assertion(s)'}")
sys.exit(1 if failures else 0)
