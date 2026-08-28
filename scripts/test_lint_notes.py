#!/usr/bin/env python3
"""test_lint_notes.py — prove the template blocks what it was written to block.

The claim the rule rests on is the review's: the template would have blocked the notes
about the other side's internal housekeeping and none of the genuine interface defects. That
claim is testable, so the last block here runs the check over the real shapes of both kinds
rather than trusting it.

    python scripts/test_lint_notes.py
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "lint_notes", Path(__file__).resolve().parent / "lint-notes.py")
ln = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ln)

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


HEAD = "---\ntype: doc\n---\n\n# Notes\n\n*(Pointer.)*\n\n## Unresolved\n\n"


def note(n: int, affects: str | None = "site/reports/AGO-status.md — the tally is wrong",
         tag: str = "ACT", date: str = "2026-08-28", gap: int = 0) -> str:
    out = f"**{n}** [{tag}] ({date}) - **A title.**\n\n"
    if affects is not None:
        out += "\n" * gap + f"Affects: {affects}\n\n"
    return out + "Body text.\n\n"


def build(tmp: Path, osint: str, corpus: str = "") -> Path:
    share = tmp / "share"
    share.mkdir(exist_ok=True)
    (share / "notes-for-osint.md").write_text(HEAD + osint, encoding="utf-8", newline="\n")
    (share / "notes-for-corpus.md").write_text(HEAD + corpus, encoding="utf-8", newline="\n")
    return share


def run(share: Path) -> tuple[int, str]:
    argv_before = sys.argv
    sys.argv = ["lint-notes.py", "--share", str(share)]
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            rc = ln.main()
    finally:
        sys.argv = argv_before
    return rc, out.getvalue()


print("notes — the shape both archives use, and only that")
check("a note is found with its parts",
      [(n, t, d) for _l, n, t, d, _b in ln.notes(HEAD + note(49))],
      [("49", "ACT", "2026-08-28")])
check("two notes do not run into one another",
      len(ln.notes(HEAD + note(49) + note(50))), 2)
check("a bold number that is not a note is not one", ln.notes("**hello** there\n"), [])

print("affects_of — the field is where a reader looks, not wherever it ends up")
check("read from directly under the title",
      ln.affects_of(note(49).split("\n")), "site/reports/AGO-status.md — the tally is wrong")
check("bold is allowed", ln.affects_of(["**Affects:** outputs/x.csv"]), "outputs/x.csv")
check("buried past the lookahead is not found",
      ln.affects_of(["title", "", "a", "b", "c", "Affects: site/x.md"]), None)

print("problems — the field must be there, and must say something")
check("a good note has none", ln.problems("1", "ACT", "2026-08-28", note(1).split("\n")), [])
check("a missing tag is caught",
      any("carries no tag" in p
          for p in ln.problems("1", None, "2026-08-28", note(1).split("\n"))), True)
check("a missing date is caught",
      any("no (YYYY-MM-DD) date" in p
          for p in ln.problems("1", "ACT", None, note(1).split("\n"))), True)

print("the evasions a compulsory field attracts")
for value in ("n/a", "N/A", "none", "nothing", "-", "TBD", "general", "housekeeping",
              "internal", "no output"):
    got = ln.problems("1", "ACT", "2026-08-28", note(1, affects=value).split("\n"))
    check(f"'{value}' is the field filled in with nothing",
          any("filled in with nothing" in p for p in got), True)
check("a value naming nothing findable is caught",
      any("names nothing a reader can go to" in p for p in
          ln.problems("1", "ACT", "2026-08-28",
                      note(1, affects="the repository feels large").split("\n"))), True)

print("what the review said the template would block, and what it must not")
BLOCKED = [
    "the repo is getting large and should be pruned",
    "the wording of your process file could be clearer",
    "sub-agent spend policy",
    "nothing here is actioned and nothing depends on the answer",
]
KEPT = [
    "site/reports/GNB-progress.md — 100 indicators have no evidence",
    "outputs/non-state-finance/all-nonstate.csv — two rows double-counted",
    "the published bulletin's byline is ten hours out",
    "strategic review task 15 — the interface rule",
    "note 47 — the drop-list rows it asked for",
    "job 79 — its IATI half",
    "scripts/build-catalogue.py — the slug it resolves has moved",
    "KEN-status — the not-held tally",
]
for value in BLOCKED:
    got = ln.problems("1", "ACT", "2026-08-28", note(1, affects=value).split("\n"))
    check(f"blocked: {value[:38]}", bool(got), True)
for value in KEPT:
    got = ln.problems("1", "ACT", "2026-08-28", note(1, affects=value).split("\n"))
    check(f"kept:    {value[:38]}", got, [])

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)

    print("end to end — CORPUS's outbox fails, OSINT's is advisory")
    rc, out = run(build(tmp, note(49)))
    check("a clean pair exits 0", rc, 0)
    rc, out = run(build(tmp, note(49, affects=None)))
    check("a missing line in CORPUS's outbox exits 1", rc, 1)
    check("and says what to write", "would have to say nothing is not a note" in out, True)
    rc, out = run(build(tmp, note(49), corpus=note(9, affects=None)))
    check("the same in OSINT's outbox exits 0", rc, 0)
    check("but is reported", "note - notes-for-corpus.md" in out, True)
    rc, out = run(build(tmp, ""))
    check("an empty queue is clean", rc, 0)

    print("a share that is not there is a 2, not a pass")
    rc, out = run(tmp / "nowhere")
    check("exit 2", rc, 2)

print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
