#!/usr/bin/env python3
"""test_lint_preambles.py — prove the preamble lint fails where it should and only there.

The risk this carries is a lint that passes on everything: a boundary regex that never
matches makes a file look like pure preamble, one that matches the first line makes every
file look clean, and either reads as a green run. So each case builds a synthetic share and
asserts on the exit code and the message, not just that it ran.

    python scripts/test_lint_preambles.py
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "lint_preambles", Path(__file__).resolve().parent / "lint-preambles.py")
lp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lp)

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


README = """# CORPUS-OSINT-XFER

A pointer preamble and nothing else.

## Conventions

**Closing means moving, and nothing is left at the number.** Numbers are never reused.
**Both sides write, so re-read before editing.** CORPUS does the committing here.
An unpushed commit is as invisible as an uncommitted edit. Neither path is more correct.
Reasoning lives in the repo that owns it. Answering a note
does not let you assign work in it. If a later run can undo it, it is not critical.
"""
CLAUDE = "# CLAUDE.md\n\nReserve his attention for the irreversible and the already-public.\n"
POINTER = "# Notes\n\n*(Conventions: README.md.)*\n\n## Unresolved\n\n**7** [ACT] a note.\n"
RESOLVED_O = "# Resolved\n\n*(Pointer.)*\n\n| Note | Subject |\n|---|---|\n"
RESOLVED_C = "# Resolved\n\n*(Pointer.)*\n\n## 12 — a closed note\n"
JOBS = "# jobs\n\n## NEXT JOB NUMBER: 9\n\n*(Pointer.)*\n\n## Jobs\n\n8. A job.\n"
FROM_BILL = "# Messages from Bill\n\n*(Pointer.)*\n\n## Block 1\n\nText.\n"
FOR_BILL = ("---\ntype: log\n---\n\n# Messages for Bill\n\n*(Pointer.)*\n\n"
            "<!-- newest first: a new block goes directly below this line -->\n\n"
            "## 2026-08-20 16:05 · review\n\n- a block.\n")


def build(tmp: Path, **over: str) -> tuple[Path, Path]:
    """A synthetic share and CORPUS root, with named files overridden."""
    share, root = tmp / "share", tmp / "root"
    (root / "logs").mkdir(parents=True, exist_ok=True)
    share.mkdir(exist_ok=True)
    files = {
        "README.md": README,
        "notes-for-osint.md": POINTER,
        "notes-for-corpus.md": POINTER,
        "notes-for-osint-resolved.md": RESOLVED_O,
        "notes-for-corpus-resolved.md": RESOLVED_C,
        "housekeeping-jobs.md": JOBS,
        "housekeeping-jobs-resolved.md": JOBS,
        "messages-from-bill.md": FROM_BILL,
    }
    files.update({k: v for k, v in over.items() if k in files})
    for name, text in files.items():
        (share / name).write_text(text, encoding="utf-8", newline="\n")
    (root / "CLAUDE.md").write_text(over.get("CLAUDE.md", CLAUDE), encoding="utf-8",
                                    newline="\n")
    (root / "logs" / "messages-for-bill.md").write_text(
        over.get("messages-for-bill.md", FOR_BILL), encoding="utf-8", newline="\n")
    return share, root


def run(share: Path, root: Path) -> tuple[int, str]:
    argv_before = sys.argv
    sys.argv = ["lint-preambles.py", "--share", str(share), "--root", str(root)]
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            rc = lp.main()
    finally:
        sys.argv = argv_before
    return rc, out.getvalue()


print("preamble_of — the boundary is the file's own, not a guess")
check("stops at the named line",
      lp.preamble_of("a\nb\n## Heading\nc", lp.HEADING).split(), ["a", "b"])
check("a file with no boundary is all preamble",
      lp.preamble_of("a\nb\nc", lp.HEADING).split(), ["a", "b", "c"])
check("the job pattern finds a numbered entry",
      lp.preamble_of("intro\n7. a job\n", lp.JOB).split(), ["intro"])
check("a heading is not a job", lp.preamble_of("## Jobs\n7. a job\n", lp.JOB).split(),
      ["##", "Jobs"])

print("flat — a rule wrapped across two lines is still the rule")
check("hard wrapping folds", "If a later run can undo it" in lp.flat(README), True)
check("unwrapped text is unchanged", lp.flat("one two"), "one two")

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)

    print("a share that keeps the discipline passes")
    rc, out = run(*build(tmp))
    check("exit 0", rc, 0)
    check("and says what it checked", "rule(s) stated once" in out, True)

    print("an over-cap preamble in a file CORPUS owns fails")
    fat = "# Notes\n\n" + ("word " * 300) + "\n\n## Unresolved\n\n**7** a note.\n"
    rc, out = run(*build(tmp, **{"notes-for-osint.md": fat}))
    check("exit 1", rc, 1)
    check("names the file and the count", "notes-for-osint.md: preamble is 302" in out, True)

    print("the same in a file it does not own is an advisory, not a failure")
    rc, out = run(*build(tmp, **{"housekeeping-jobs.md":
                                 "# jobs\n\n" + ("word " * 300) + "\n\n8. A job.\n"}))
    check("exit 0", rc, 0)
    check("but it is reported", "note - housekeeping-jobs.md: preamble is 302" in out, True)

    print("a rule restated away from home fails")
    copied = "# Notes\n\n*(Numbers are never reused.)*\n\n## Unresolved\n\n**7** a note.\n"
    rc, out = run(*build(tmp, **{"notes-for-corpus.md": copied}))
    check("exit 1", rc, 1)
    check("names the phrase and its home",
          "restates 'Numbers are never reused', which belongs in README.md" in out, True)

    print("an archive quoting a rule is left alone — rewriting it would falsify it")
    rc, out = run(*build(tmp, **{"notes-for-corpus-resolved.md":
                                 "# Resolved\n\n*(Pointer.)*\n\n"
                                 "## 12 — a note about 'Numbers are never reused'\n"}))
    check("exit 0", rc, 0)

    print("a home that stops stating its own rule fails, so the check cannot disarm itself")
    rc, out = run(*build(tmp, **{"README.md": "# Share\n\n## Conventions\n\nNothing.\n"}))
    check("exit 1", rc, 1)
    check("says the rule left home", "no longer states" in out, True)

    print("messages-for-bill is measured to its marker, and CLAUDE.md is its home")
    rc, out = run(*build(tmp, **{"messages-for-bill.md":
                                 "# Messages\n\n" + ("word " * 300) +
                                 "\n\n<!-- newest first: a new block goes directly below "
                                 "this line -->\n\n## 2026-08-20 16:05 · review\n"}))
    check("an over-cap preamble fails", rc, 1)
    rc, out = run(*build(tmp, **{"messages-for-bill.md":
                                 FOR_BILL.replace("*(Pointer.)*",
                                                  "*(the irreversible and the "
                                                  "already-public)*")}))
    check("a rule copied out of CLAUDE.md fails", rc, 1)

    print("a share that is not there is a 2, not a pass")
    rc, out = run(tmp / "nowhere", tmp / "root")
    check("exit 2", rc, 2)

print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
