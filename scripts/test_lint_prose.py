#!/usr/bin/env python3
"""test_lint_prose.py — each of lint-prose.py's checks, both directions, and the gate's baseline.

R133 asks for both directions because a check that never fires and a check that always fires
both print a count. The sheet itself is the first case (R132): it is written to its own rules,
so it must pass.

    python scripts/test_lint_prose.py
"""

from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "lint_prose", Path(__file__).resolve().parent / "lint-prose.py")
lp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lp)

failures: list[str] = []
SHEET = Path(os.environ.get("CORPUS_OSINT_XFER", r"C:\corpus-osint-xfer")) / "documentation"


def check(name: str, got, want) -> None:
    if got != want:
        failures.append(f"{name}: got {got!r}, want {want!r}")


def fails(text: str, kind: str = "status") -> list[str]:
    return lp.check(lp.paragraphs(text.splitlines()), kind)["fails"]


LINKED = "[On 3 May 2026 the ministry published the strategy](https://example.org/a)."
SHORT = "It names the agency. The agency has a budget line."

# --- the numbers (R128) ---------------------------------------------------------------------
check("mean passes under 20", "mean" in fails(LINKED + " " + SHORT), False)
long20 = " ".join(["word"] * 32) + "."
check("mean fails at 20 or more", "mean" in fails(LINKED + " " + long20.capitalize()), True)
check("long passes at 40", "long" in fails(LINKED + " " + ("Word " + "word " * 39).strip() + "."),
      False)
check("long fails over 40", "long" in fails(LINKED + " " + ("Word " + "word " * 40).strip() + "."),
      True)
check("one rather than is allowed",
      "contrast" in fails(LINKED + " It chose a fund rather than a loan."), False)
check("two rather thans in a short block fail",
      "contrast" in fails(LINKED + " It chose a fund rather than a loan. Grants rather than credit."),
      True)
check("semicolons do not split", [lp.nwords(s) for s in lp.sentences("One two; three four. Five.")],
      [4, 1])
check("abbreviations do not split", len(lp.sentences("Act No. 4 of 2019 applies. It is short.")), 2)
check("a link label is never split",
      len(lp.sentences("[The act. It says so](https://x.org) today. Next one.")), 2)

# --- the first sentence (R129, status only) ---------------------------------------------------
check("linked and dated passes", "first" in fails(LINKED), False)
check("whole link text passes", "first" in fails("[The ministry published it](https://x.org)."),
      False)
check("a verdict lead fails", "first" in fails("Older commitments have aged. " + LINKED), True)
check("a figure alone fails",
      "first" in fails("Four in ten courts now sit online, the [ministry](https://x.org) says."),
      True)
check("a date with no link fails", "first" in fails("In May 2026 the ministry published it."), True)
check("maturity blocks skip the first test",
      "first" in fails("Older commitments have aged.", "maturity"), False)
check("bulletin summaries skip the first test",
      "first" in fails("The bank plans a framework.", "bulletin"), False)
check("a summary written before the sheet is not read",
      list(lp.bulletin_blocks('{"a": {"written": "2026-10-26", "summary": "Old."}, '
                              '"b": {"written": "2026-10-28", "summary": "New."}}')), ["b"])

# --- the words (R130) and the mood list ------------------------------------------------------
check("apparatus words fail", "words" in fails(LINKED + " No strategy is held."), True)
check("not held fails", "words" in fails(LINKED + " The plan is Not held here."), True)
check("found passes", "words" in fails(LINKED + " No strategy has been found."), False)
check("an election held passes", "words" in fails(LINKED + " Elections were held in May."), False)
check("where data is held passes",
      "words" in fails(LINKED + " No rule says where state data is held."), False)
check("a mood word fails", "mood" in fails(LINKED + " The regulator plainly cannot act."), True)
check("a quoted mood word stands",
      "mood" in fails(LINKED + ' The minister said it was "finally done".'), False)
check("maturity words gate since R136",
      lp.gating("maturity", ["words", "mean"]), ["words", "mean"])
check("the wiki never gates", lp.gating("wiki", ["mean", "long", "words"]), [])

# --- blocks ----------------------------------------------------------------------------------
status = ("---\ntitle: x\n---\n## Governance\n\n### Strategies\n<!-- gov.policy -->\n\n" + LINKED +
          "\n\n<!-- derived -->\nThe lines come to about R13.3 billion appropriated for 2026/27.\n"
          "\n### Laws\n<!-- gov.legislate -->\n\n" + LINKED + "\n")
blocks = lp.status_blocks(status)
check("status keyed by slug", sorted(blocks), ["gov.legislate", "gov.policy"])
check("the derived paragraph is left out", blocks["gov.policy"], [LINKED])
check("the emitted absence block is left out",
      lp.paragraphs([LINKED, "", "<!-- absences -->", "Nothing has been found on ICT strategy.",
                     "<!-- /absences -->"]), [LINKED])
mat = "# Kenya\n\n## Tax\n\n**Online filing.** It files online. It pays online.\n\n***Not held***. None.\n"
mb = lp.maturity_blocks(mat, "taxadmin")
check("maturity keyed by heading and label", sorted(mb),
      ["taxadmin/Tax/Not held#1", "taxadmin/Tax/Online filing#1"])
check("the label is stripped", mb["taxadmin/Tax/Online filing#1"], ["It files online. It pays online."])
check("a citation-only list item is not prose",
      lp.paragraphs(["- [[2026-05-22 Some title]]", "- A sentence of prose here."]),
      ["A sentence of prose here."])

# --- the sheet and the exemplars, R132's first test case --------------------------------------
if (SHEET / "prose-style.md").exists():
    r = lp.check(lp.paragraphs(lp.body(lp.read(str(SHEET / "prose-style.md")))), "doc")
    check("the sheet passes its own lint", r["fails"], [])

# --- the gate: revised is a diff of the block, keyed, against the run's base -----------------
with tempfile.TemporaryDirectory() as tmp:
    run = lambda *a: subprocess.run(["git", *a], cwd=tmp, capture_output=True, check=True)
    run("init", "-q")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    unit = Path(tmp, "outputs", "reports", "KEN")
    unit.mkdir(parents=True)
    bad = "### Laws\n<!-- gov.legislate -->\n\nOlder laws have aged without replacement.\n"
    good = "### Strategies\n<!-- gov.policy -->\n\n" + LINKED + "\n"
    (unit / "KEN-status.md").write_text("## Governance\n\n" + good + "\n" + bad, encoding="utf-8")
    run("add", "-A")
    run("commit", "-qm", "base")
    saved = (lp.ROOT, lp.REPORTS, lp.MATURITY, lp.SUMMARIES, lp.OPEN)
    lp.ROOT, lp.REPORTS = tmp, os.path.join(tmp, "outputs", "reports")
    lp.MATURITY, lp.SUMMARIES = os.path.join(tmp, "none"), os.path.join(tmp, "none.json")
    lp.OPEN = os.path.join(tmp, ".prose-open")
    try:
        with redirect_stdout(io.StringIO()):
            lp.open_run()
            check("an unchanged failing block does not gate", lp.gate(), 0)
            moved = "## Governance\n\n" + bad + "\n" + good
            (unit / "KEN-status.md").write_text(moved, encoding="utf-8")
            check("a block moved unchanged is not revised", lp.gate(), 0)
            (unit / "KEN-status.md").write_text(moved.replace("aged", "aged badly"), encoding="utf-8")
            check("a revised failing block gates", lp.gate(), 1)
            (unit / "KEN-status.md").write_text(
                "## Governance\n\n" + good.replace("strategy", "plan") + "\n" + bad, encoding="utf-8")
            check("a revised passing block does not gate", lp.gate(), 0)
    finally:
        lp.ROOT, lp.REPORTS, lp.MATURITY, lp.SUMMARIES, lp.OPEN = saved

# --- the estate count ------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    log = os.path.join(tmp, "prose.csv")
    Path(log).write_text(
        "date,unit,blocks,failing,words,sentences,mean,longest,contrast,first,word_hits,mood_hits\n"
        "2026-10-26,KEN,9,9,0,0,0,0,0,0,0,0\n"
        "2026-10-27,KEN,9,4,0,0,0,0,0,0,0,0\n2026-10-27,bulletin,9,3,0,0,0,0,0,0,0,0\n"
        "2026-10-27,wiki,9,8,0,0,0,0,0,0,0,0\n", encoding="utf-8")
    check("estate count is the newest night, wiki apart", lp.estate_count(log), 7)
    check("no log, no count", lp.estate_count(os.path.join(tmp, "none.csv")), None)

if failures:
    print("\n".join(failures))
    print(f"test_lint_prose: FAIL - {len(failures)}")
    sys.exit(1)
print("test_lint_prose: ok")
