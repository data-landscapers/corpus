#!/usr/bin/env python3
"""test_lint_messages.py — a struck block is gone, not annotated.

    python scripts/test_lint_messages.py

`lint-messages.py` counts two caps and refuses a third thing: a block edited to say its
subject is settled, instead of being deleted (strategic review 4, task 38). The caps were
already countable and are covered here because they share a parser with the new check —
the heading rule had to widen to see a struck heading at all, and a widened heading rule
is exactly the sort of change that quietly reclassifies a body line as a block.

**The cases that matter most are the ones that must NOT fire.** A block's whole job is to
say what a run did, so bullets opening *Done*, *Answered* or *Left as compiled* are the
normal shape of an open block; a check that fired on those would be one nobody could write
a message past, and it would be disabled within a week.
"""
from __future__ import annotations

import importlib.util
import io
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "lint_messages", Path(__file__).resolve().parent / "lint-messages.py")
lm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lm)

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


HEAD = ("---\ntype: log\n---\n\n# Messages for Bill\n\n"
        "*(Pointer to `CLAUDE.md` -> *Be decisive*.)*\n\n"
        + lm.MARKER + "\n\n")


def block(date: str = "2026-09-18", body: str = "- Something happened.") -> str:
    return f"## {date} 12:40 · review\n\n{body}\n\n"


tmp = Path(tempfile.mkdtemp(prefix="lint-messages-"))


def run(content: str) -> tuple[int, str]:
    """(exit code, output) for a file holding `content` under the marker."""
    path = tmp / "messages.md"
    io.open(path, "w", encoding="utf-8", newline="\n").write(HEAD + content)
    argv_before = sys.argv
    sys.argv = ["lint-messages.py", "--file", str(path)]
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            code = lm.main()
    finally:
        sys.argv = argv_before
    return code, out.getvalue()


try:
    # ---- the two caps, which share the parser -------------------------------

    print("the caps")
    check("five blocks pass", run(block() * 5)[0], 0)
    check("six do not", run(block() * 6)[0], 1)
    check("and the message names the count", "6 open blocks" in run(block() * 6)[1], True)
    check("eighty words pass", run(block(body="word " * 80))[0], 0)
    check("eighty-one do not", run(block(body="word " * 81))[0], 1)
    check("a block older than the word cap is reported, not failed",
          run(block(date="2026-08-01", body="word " * 81))[0], 0)
    check("and says so",
          "predates the cap" in run(block(date="2026-08-01", body="word " * 81))[1], True)

    # ---- struck, not gone ---------------------------------------------------

    print("\na block annotated as settled instead of deleted")
    STRUCK = [
        ("a struck-through heading", "## ~~2026-09-18 12:40 · review~~\n\n- Text.\n\n"),
        ("an x-prefixed heading", "## x 2026-09-18 12:40 · review\n\n- Text.\n\n"),
        ("a bold Settled line", block(body="- Text.\n\n**Settled 2026-09-20.**")),
        ("a bold Closed line", block(body="- Text.\n\n**Closed:** Bill ruled.")),
        ("a struck-through bullet", block(body="- ~~Text, now dealt with.~~")),
        ("a Resolved bullet", block(body="- **Resolved** — the run did it after all.")),
    ]
    for name, content in STRUCK:
        code, text = run(content)
        check(name + " fails", code, 1)
        check("  …and is named as annotated", "is annotated as settled, not struck" in text, True)

    print("\nand the same block, actually gone")
    check("nothing left to count", run("")[0], 0)
    check("the count is zero", "0 block(s)" in run("")[1], True)
    # **The rule stated as a count.** Striking by deletion takes a block out of the five;
    # striking by annotation does not, so a sixth block that merely says it is closed
    # trips the cap exactly as an open one would.
    annotated_sixth = block() * 5 + block(body="- Text.\n\n**Settled 2026-09-20.**")
    code, text = run(annotated_sixth)
    check("an annotated sixth still trips the block cap", "6 open blocks" in text, True)
    check("and is itself named", "is annotated as settled, not struck" in text, True)
    check("the run fails on both counts", code, 1)
    check("deleted instead, five blocks are clean", run(block() * 5)[0], 0)

    print("\nwhat must not fire")
    SAFE = [
        ("a bullet opening 'Done'", "- **Done**: the run rebuilt the page itself."),
        ("a bullet opening 'Answered'", "- Answered in the same pass; left as compiled."),
        ("a bullet saying what was left", "- Left as compiled. Bill's call."),
        ("prose containing the word settled",
         "- The question is whether this is settled estate-wide."),
        ("a strikethrough mid-sentence",
         "- The old figure was ~~4,088~~ and is now 3,900."),
    ]
    for name, body in SAFE:
        code, text = run(block(body=body))
        check(name + " passes", (code, "is annotated as settled, not struck" in text), (0, False))

    print("\nthe parser")
    # A struck heading must open a block of its own. Swallowed into the block above it, it
    # would be counted as that block's body — the new check would never see it, and the
    # word cap would fire on the wrong block.
    parsed = lm.blocks(HEAD + block() + "## ~~2026-09-17 09:00 · build~~\n\n- Text.\n")
    check("a struck heading opens its own block", len(parsed), 2)
    check("and carries the strike", bool(parsed[1][3]), True)
    check("while the block above it is clean", parsed[0][3], [])

    print("\nthe file itself")

    def run_path(path: Path) -> tuple[int, str]:
        argv_before = sys.argv
        sys.argv = ["lint-messages.py", "--file", str(path)]
        out = io.StringIO()
        try:
            with redirect_stdout(out):
                return lm.main(), out.getvalue()
        finally:
            sys.argv = argv_before

    check("a missing file exits 2", run_path(tmp / "nope.md")[0], 2)
    no_marker = tmp / "no-marker.md"
    io.open(no_marker, "w", encoding="utf-8", newline="\n").write(
        "# Messages\n\n## 2026-09-18 12:40 \u00b7 review\n\n- Text.\n")
    code, text = run_path(no_marker)
    check("a file with no marker exits 2", code, 2)
    check("and says which line is missing", "newest first" in text, True)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} FAILED: {', '.join(failures)}")
    sys.exit(1)
print("all checks passed")
