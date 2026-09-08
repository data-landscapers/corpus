#!/usr/bin/env python3
"""test_report_register_check.py — prove the word budget is read from the skeleton, both forms.

The budget lives in the skeleton so there is one knob (`report-layer.md` §K), which means the
script's only hold on it is a regular expression over an English sentence. On 2026-09-08 the
monthly's budget became a rate per ledger row — a longer sentence than the flat form, and one
that can be reworded past. The script's own defence is to exit 2 rather than pass silently; this
asserts that defence still works, in both directions:

  - both forms parse, and a rate resolves against a row count;
  - a skeleton that stops naming one of its documents is fatal, not a silent skip.

The second is the case the real skeletons cannot demonstrate, because they are correct.

    python scripts/test_report_register_check.py
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
from contextlib import redirect_stderr
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "rrc", Path(__file__).resolve().parent / "report-register-check.py")
rrc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rrc)

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


def budgets_from(kind: str, text: str):
    """Run `budgets(kind)` against a skeleton written here, not the repo's."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "skeleton.md"
        path.write_text(text, encoding="utf-8")
        real = rrc.SKELETONS[kind]
        rrc.SKELETONS[kind] = str(path)
        try:
            return rrc.budgets(kind)
        finally:
            rrc.SKELETONS[kind] = real


FLAT = "**Prose only: 1,000–1,450 words for a status report, 700–2,000 for a monthly.**\n"
RATE = ("**Prose only: 1,000–1,450 words for a status report, and 300 + 25 to 1,200 + 55 "
        "words a row for a monthly.**\n")

print("both forms parse")
flat = budgets_from("country", FLAT)
check("flat monthly is not scaled", flat["monthly"].scaled, False)
check("flat monthly ignores rows", flat["monthly"].at(158), (700, 2000))
check("flat status parses", flat["status"].at(0), (1000, 1450))

rate = budgets_from("country", RATE)
check("rate monthly is scaled", rate["monthly"].scaled, True)
check("rate monthly at 4 rows", rate["monthly"].at(4), (400, 1420))
check("rate monthly at 158 rows", rate["monthly"].at(158), (4250, 9890))
check("a flat line beside a rate line still parses", rate["status"].at(0), (1000, 1450))
check("describe names the row count", rate["monthly"].describe(46), "1450-3730 on 46 row(s)")
check("describe stays quiet on a flat band", flat["monthly"].describe(46), "700-2000")

print("\nthe rate line cannot be mistaken for a flat one")
# `1,200 + 55 words a row for a monthly` must not also satisfy the flat pattern, or the monthly
# would carry two bands and the last one written would win by dict ordering.
check("flat pattern finds only the status band in a rate line",
      [m.group(3) for m in rrc.BUDGET_LINE.finditer(RATE)], ["status"])
check("rate pattern finds nothing in a flat line",
      [m.group(5) for m in rrc.BUDGET_RATE_LINE.finditer(FLAT)], [])

print("\na skeleton that stops naming a document is fatal, not a silent skip")
for kind, text, want_missing in (
        ("country", "**Prose only: 1,000–1,450 words for a status report.**\n", "monthly"),
        ("country", "**Prose only: 300 + 25 to 1,200 + 55 words a row for a monthly.**\n", "status"),
        ("region", "**Prose only: 800–1,150 words for a progress report.**\n", "monthly"),
        ("country", "**Prose only: no numbers at all.**\n", "monthly, status")):
    err = io.StringIO()
    code = None
    try:
        with redirect_stderr(err):
            budgets_from(kind, text)
    except SystemExit as e:
        code = e.code
    check(f"{kind}: missing {want_missing} exits 2", code, 2)
    check(f"{kind}: missing {want_missing} is named in the error",
          want_missing in err.getvalue(), True)

print("\nthe repo's own skeletons satisfy their contract")
for kind in ("country", "region"):
    got = set(rrc.budgets(kind))
    check(f"{kind} skeleton names {sorted(rrc.REQUIRED[kind])}",
          rrc.REQUIRED[kind] <= got, True)
check("country monthly is a rate", rrc.budgets("country")["monthly"].scaled, True)
check("region monthly is a rate", rrc.budgets("region")["monthly"].scaled, True)

print("\na rate band with no row count is fatal, not a nought")
err = io.StringIO()
code = None
try:
    with redirect_stderr(err):
        rrc.ledger_rows("---\ntitle: x\n---\n\n# x\n", "outputs/reports/ZZZ/ZZZ-monthly.md")
except SystemExit as e:
    code = e.code
check("missing ledger_rows exits 2", code, 2)
check("the error names the file", "ZZZ-monthly.md" in err.getvalue(), True)
check("a present ledger_rows is read",
      rrc.ledger_rows("---\nledger_rows: 158\n---\n", "x"), 158)

print(f"\n{'FAILURES: ' + ', '.join(failures) if failures else 'all checks passed'}")
sys.exit(1 if failures else 0)
