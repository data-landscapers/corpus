#!/usr/bin/env python3
"""test_osint_cycle_ready.py — prove the sweep-cycle trigger fires, and holds, when it should.

Same principle as `test_mirror_freshness.py`: this check spends almost all of its life
returning 1, and *not firing* is indistinguishable from *nothing has happened* unless
something proves the firing path still works. It is also the one script in the repo whose
input is written by the other system — a rotation table Corpus does not control and cannot
edit — so the parse is worth pinning against a real row, not a paraphrase of one.

**The case that matters most is `manual mirror, same table`.** That is the whole reason the
trigger reads `End` rather than an mtime, and it is the one Bill asked for by name: a
mid-afternoon FreeFileSync run while he is working must not start a build.

Each case writes a synthetic table and watermark into a temp directory, points the module's
path constants at them, and asserts the exit code. `tree_dirty` and `mirror_head` are
stubbed: both shell out to git against the real repo, which would make the result depend on
whatever the working tree happens to look like when the test is run.

    python scripts/test_osint_cycle_ready.py
"""

from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "osint_cycle_ready", Path(__file__).resolve().parent / "osint-cycle-ready.py")
cr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cr)

HEADER = (
    "| Day | Jobs                 | Gate | Skip | Start            | End              "
    "| Duration | Prev Duration | New-Start        |\n"
    "| --- | -------------------- | ---- | ---- | ---------------- | ---------------- "
    "| -------- | ------------- | ---------------- |\n"
)


def table(*rows: tuple[str, str, str, str]) -> str:
    """(day, start, end, new_start) -> the rotation table as OSINT writes it."""
    out = HEADER
    for day, start, end, new_start in rows:
        out += (f"| {day}   | SWEEP-IATI           |      |      | {start:16} | {end:16} "
                f"| 2:58     | 1:16          | {new_start:16} |\n")
    return out


CLOSED_EARLY = ("5", "2026-08-20 14:08", "2026-08-20 17:06", "")
CLOSED_LATE = ("7", "2026-08-20 21:00", "2026-08-21 02:11", "")
RUNNING = ("7", "2026-08-20 21:00", "", "2026-08-21 03:00")

# (name, table text or None, watermark dict or None, files to touch, expected exit)
CASES: list[tuple[str, str | None, dict | None, list[str], int]] = [
    (
        "first ever run, a day has closed",
        table(CLOSED_EARLY), None, [], 0,
    ),
    (
        "a close newer than the watermark",
        table(CLOSED_EARLY, CLOSED_LATE), {"done": "2026-08-20 17:06"}, [], 0,
    ),
    (
        "manual mirror, same table — the case this whole design exists for",
        table(CLOSED_EARLY), {"done": "2026-08-20 17:06"}, [], 1,
    ),
    (
        "two closes in one day, the second still fires",
        table(("7", "2026-08-20 09:21", "2026-08-20 13:22", ""), CLOSED_EARLY),
        {"done": "2026-08-20 13:22"}, [], 0,
    ),
    (
        "newest by timestamp, not last in the table",
        table(CLOSED_LATE, CLOSED_EARLY), {"done": "2026-08-20 17:06"}, [], 0,
    ),
    (
        "a cycle is in flight",
        table(CLOSED_EARLY, RUNNING), None, [], 1,
    ),
    (
        "held by hand",
        table(CLOSED_EARLY), None, [".hold-cycle"], 1,
    ),
    (
        "held by a build in flight",
        table(CLOSED_EARLY), None, [".build-in-progress"], 1,
    ),
    (
        "a claim that never reported done",
        table(CLOSED_LATE), {"done": "2026-08-20 17:06", "claimed": "2026-08-21 02:11",
                             "claimed_at": "2026-08-21 02:20"}, [], 2,
    ),
    (
        "a claim already marked done is not stale",
        table(CLOSED_LATE), {"done": "2026-08-21 02:11", "claimed": None}, [], 1,
    ),
    (
        "no row has ever closed",
        table(("1", "", "", "")), None, [], 2,
    ),
    (
        "the table is not there",
        None, None, [], 2,
    ),
    (
        "the header has been renamed under us",
        table(CLOSED_EARLY).replace("| End ", "| Finish "), None, [], 2,
    ),
    (
        "prose in the file, no table",
        "This file is the rotation, and today it is only prose.\n", None, [], 2,
    ),
]


def run() -> int:
    failures = 0
    argv = sys.argv
    keep = (cr.MIRROR, cr.CYCLE_LOG, cr.STATE, cr.HOLD, cr.SENTINEL,
            cr.tree_dirty, cr.mirror_head)
    cr.tree_dirty = lambda: False
    cr.mirror_head = lambda: "0123456789abcdef"
    try:
        for name, table_text, state, touch, expected in CASES:
            tmp = Path(tempfile.mkdtemp(prefix="cycle-trigger-test-"))
            try:
                (tmp / "logs").mkdir()
                cr.MIRROR = str(tmp)
                cr.CYCLE_LOG = str(tmp / "logs" / "sweep-cycle_log.md")
                cr.STATE = str(tmp / ".osint-cycle-seen")
                cr.HOLD = str(tmp / ".hold-cycle")
                cr.SENTINEL = str(tmp / ".build-in-progress")
                if table_text is not None:
                    Path(cr.CYCLE_LOG).write_text(table_text, encoding="utf-8")
                if state is not None:
                    Path(cr.STATE).write_text(json.dumps(state), encoding="utf-8")
                for fname in touch:
                    (tmp / fname).write_text("", encoding="utf-8")

                sys.argv = ["osint-cycle-ready.py"]
                buf = io.StringIO()
                with redirect_stdout(buf):
                    got = cr.main()

                ok = got == expected
                failures += not ok
                print(f"  {'ok  ' if ok else 'FAIL'} {name}  (expected {expected}, got {got})")
                if not ok:
                    for ln in buf.getvalue().splitlines():
                        print(f"       {ln}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)

        # The claim/done round trip, which the exit-code cases above cannot reach: a run
        # claims a close, a second poll refuses to fire on it, and --done advances past it.
        tmp = Path(tempfile.mkdtemp(prefix="cycle-trigger-test-"))
        try:
            (tmp / "logs").mkdir()
            cr.MIRROR, cr.CYCLE_LOG = str(tmp), str(tmp / "logs" / "sweep-cycle_log.md")
            cr.STATE = str(tmp / ".osint-cycle-seen")
            cr.HOLD, cr.SENTINEL = str(tmp / ".hold-cycle"), str(tmp / ".build-in-progress")
            Path(cr.CYCLE_LOG).write_text(table(CLOSED_EARLY), encoding="utf-8")

            steps = [(["--claim"], 0), ([], 2), (["--done"], 0), ([], 1), (["--done"], 2)]
            for extra, expected in steps:
                sys.argv = ["osint-cycle-ready.py", *extra]
                with redirect_stdout(io.StringIO()) as buf:
                    got = cr.main()
                ok = got == expected
                failures += not ok
                label = " ".join(extra) or "(bare)"
                print(f"  {'ok  ' if ok else 'FAIL'} round trip {label}  "
                      f"(expected {expected}, got {got})")
                if not ok:
                    print(f"       {buf.getvalue().strip()}")

            done = json.loads(Path(cr.STATE).read_text(encoding="utf-8"))
            ok = done.get("done") == "2026-08-20 17:06" and not done.get("claimed")
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} round trip leaves the watermark on the close")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        # --skip passes a close over and stays passed over, and says which it was.
        tmp = Path(tempfile.mkdtemp(prefix="cycle-trigger-test-"))
        try:
            (tmp / "logs").mkdir()
            cr.MIRROR, cr.CYCLE_LOG = str(tmp), str(tmp / "logs" / "sweep-cycle_log.md")
            cr.STATE = str(tmp / ".osint-cycle-seen")
            cr.HOLD, cr.SENTINEL = str(tmp / ".hold-cycle"), str(tmp / ".build-in-progress")
            Path(cr.CYCLE_LOG).write_text(table(CLOSED_EARLY), encoding="utf-8")

            sys.argv = ["osint-cycle-ready.py", "--skip"]
            with redirect_stdout(io.StringIO()):
                skipped = cr.main()
            sys.argv = ["osint-cycle-ready.py"]
            with redirect_stdout(io.StringIO()):
                after_skip = cr.main()
            state = json.loads(Path(cr.STATE).read_text(encoding="utf-8"))

            # ...and the next close still fires, which is what makes skipping cost nothing
            Path(cr.CYCLE_LOG).write_text(table(CLOSED_EARLY, CLOSED_LATE), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                next_close = cr.main()

            ok = (skipped == 0 and after_skip == 1 and next_close == 0
                  and state.get("done") == "2026-08-20 17:06" and state.get("done_by") == "skipped")
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} --skip passes one close over and the next "
                  f"still fires (skip {skipped}, after {after_skip}, next {next_close}, "
                  f"done_by {state.get('done_by')})")

            # A skip must not paper over a claim that never reported done
            Path(cr.STATE).write_text(json.dumps({"done": "2026-08-20 13:22",
                                                  "claimed": "2026-08-20 17:06"}), encoding="utf-8")
            sys.argv = ["osint-cycle-ready.py", "--skip"]
            with redirect_stdout(io.StringIO()):
                over_claim = cr.main()
            failures += over_claim != 2
            print(f"  {'ok  ' if over_claim == 2 else 'FAIL'} --skip refuses over an outstanding "
                  f"claim  (expected 2, got {over_claim})")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        # A hold defers; it does not consume. The close Bill held over must still be waiting
        # when he takes the hold off, or the night is silently skipped — which is the one way
        # the hold could be worse than having no trigger at all.
        tmp = Path(tempfile.mkdtemp(prefix="cycle-trigger-test-"))
        try:
            (tmp / "logs").mkdir()
            cr.MIRROR, cr.CYCLE_LOG = str(tmp), str(tmp / "logs" / "sweep-cycle_log.md")
            cr.STATE = str(tmp / ".osint-cycle-seen")
            cr.HOLD, cr.SENTINEL = str(tmp / ".hold-cycle"), str(tmp / ".build-in-progress")
            Path(cr.CYCLE_LOG).write_text(table(CLOSED_EARLY), encoding="utf-8")
            Path(cr.HOLD).write_text("", encoding="utf-8")

            sys.argv = ["osint-cycle-ready.py", "--claim"]
            with redirect_stdout(io.StringIO()):
                held = cr.main()
            wrote_state = Path(cr.STATE).exists()
            Path(cr.HOLD).unlink()
            sys.argv = ["osint-cycle-ready.py"]
            with redirect_stdout(io.StringIO()):
                after = cr.main()

            ok = held == 1 and not wrote_state and after == 0
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} a hold defers the close rather than consuming it "
                  f"(held {held}, wrote watermark {wrote_state}, after {after})")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        # The "nothing new" line reports base movement — a clause, never a firing condition.
        # It is here because it is the half of this script nothing else would notice going
        # quiet: the exit code is 1 either way, so a broken `base_moved` reads exactly like a
        # base that has not moved. That is the state the clause exists to distinguish.
        tmp = Path(tempfile.mkdtemp(prefix="cycle-trigger-test-"))
        try:
            (tmp / "logs").mkdir()
            cr.MIRROR, cr.CYCLE_LOG = str(tmp), str(tmp / "logs" / "sweep-cycle_log.md")
            cr.STATE = str(tmp / ".osint-cycle-seen")
            cr.HOLD, cr.SENTINEL = str(tmp / ".hold-cycle"), str(tmp / ".build-in-progress")
            Path(cr.CYCLE_LOG).write_text(table(CLOSED_EARLY), encoding="utf-8")

            def git(*args):
                return subprocess.run(["git", "-C", str(tmp), *args],
                                      capture_output=True, text=True)

            git("init", "-q")
            git("config", "user.email", "t@t")
            git("config", "user.name", "t")
            (tmp / "raw").mkdir()
            (tmp / "raw" / "a.md").write_text("one\n", encoding="utf-8")
            git("add", "-A")
            git("commit", "-qm", "first")
            built_at = git("rev-parse", "HEAD").stdout.strip()
            (tmp / "raw" / "b.md").write_text("two\n", encoding="utf-8")
            git("add", "-A")
            git("commit", "-qm", "housekeeping")

            cr.mirror_head = lambda: git("rev-parse", "HEAD").stdout.strip()
            Path(cr.STATE).write_text(json.dumps(
                {"done": "2026-08-20 17:06", "done_head": built_at}), encoding="utf-8")
            sys.argv = ["osint-cycle-ready.py"]
            with redirect_stdout(io.StringIO()) as buf:
                code = cr.main()
            said = buf.getvalue()

            # ...and it stays silent where the base has not moved at all, so the ordinary
            # quiet answer is still one line.
            Path(cr.STATE).write_text(json.dumps(
                {"done": "2026-08-20 17:06", "done_head": cr.mirror_head()}), encoding="utf-8")
            with redirect_stdout(io.StringIO()) as quiet_buf:
                quiet_code = cr.main()
            quiet = quiet_buf.getvalue()

            ok = (code == 1 and "the base has moved since" in said and "raw/ or wiki/" in said
                  and quiet_code == 1 and "the base has moved since" not in quiet)
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} a moved base is reported and never fired on "
                  f"(exit {code}, clause {'the base has moved since' in said}, "
                  f"quiet {'the base has moved since' not in quiet})")
            if not ok:
                print(f"       {said.strip()}")
        finally:
            cr.mirror_head = lambda: "0123456789abcdef"
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        sys.argv = argv
        (cr.MIRROR, cr.CYCLE_LOG, cr.STATE, cr.HOLD, cr.SENTINEL,
         cr.tree_dirty, cr.mirror_head) = keep

    print("all cases passed" if not failures else f"{failures} case(s) failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(run())
