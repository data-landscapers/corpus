#!/usr/bin/env python3
"""test_osint_cycle_ready.py — prove the sweep-cycle trigger fires, and holds, when it should.

Same principle as `test_mirror_freshness.py`: this check spends almost all of its life
returning 1, and *not firing* is indistinguishable from *nothing has happened* unless
something proves the firing path still works. It is also the one script in the repo whose
input is written by the other system — a manifest Corpus does not control and cannot edit —
so the reading is worth pinning against the real shape, not a paraphrase of one.

**The case that matters most is `manual mirror, same manifest`.** That is the whole reason
the trigger reads a stated close rather than an mtime, and it is the one Bill asked for by
name: a mid-afternoon FreeFileSync run while he is working must not start a build.

**The fixture is `cycle-manifest.json`, not a rotation table** *(2026-09-06,
`notes-for-corpus` 16)*. The trigger parsed `logs/sweep-cycle_log.md` until then and these
cases built one, header and separator row included, with two of them pinning the parse
itself: a renamed `End` column and a maximum taken over rows out of order. Both were
defences against a Markdown table Corpus does not own and may not read. OSINT now names its
own newest close, so what is left to pin is the refusal — a manifest of a schema this does
not know must stop the trigger dead rather than let it read the fields it recognises.

Each case writes a synthetic manifest and watermark into a temp directory, points the
module's path constants at them, and asserts the exit code. `tree_dirty` and `mirror_head`
are stubbed: both shell out to git against the real repo, which would make the result depend
on whatever the working tree happens to look like when the test is run.

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

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))
import osint_lib  # noqa: E402

_spec = importlib.util.spec_from_file_location("osint_cycle_ready", _here / "osint-cycle-ready.py")
cr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cr)


def manifest(day: str = "5", start: str = "2026-08-20 14:08",
             end: str | None = "2026-08-20 17:06", in_progress: list[str] | None = None,
             running: bool = False, rotation: bool = True, schema: int = 1) -> str:
    """The cycle manifest as OSINT writes it, carrying the rotation block this reads.

    `head` is deliberately absent: `read_manifest` only compares it against the mirror's own
    HEAD, and a temp directory is not a git repository, so a value here would be checked
    against `None` and skipped."""
    data: dict = {"schema": schema, "written_utc": "2026-08-20 17:10", "pass": "sweep cycle",
                  "collection": {"sweep_closed": start, "last_admission": end or start}}
    if rotation:
        rot: dict = {"days": 7, "in_progress": in_progress or []}
        if end is not None:
            rot["newest_close"] = {"day": day, "jobs": ["SWEEP-IATI"], "start": start,
                                   "end": end, "duration": "2:58", "skipped": False,
                                   "in_progress": running}
        data["rotation"] = rot
    return json.dumps(data, indent=1)


EARLY = "2026-08-20 17:06"
LATE = "2026-08-21 02:11"

# (name, manifest text or None, watermark dict or None, files to touch, expected exit)
CASES: list[tuple[str, str | None, dict | None, list[str], int]] = [
    (
        "first ever run, a day has closed",
        manifest(), None, [], 0,
    ),
    (
        "a close newer than the watermark",
        manifest(day="7", start="2026-08-20 21:00", end=LATE), {"done": EARLY}, [], 0,
    ),
    (
        "manual mirror, same manifest — the case this whole design exists for",
        manifest(), {"done": EARLY}, [], 1,
    ),
    (
        "two closes in one day, the second still fires",
        manifest(), {"done": "2026-08-20 13:22"}, [], 0,
    ),
    (
        "a cycle is in flight",
        manifest(in_progress=["7"]), None, [], 1,
    ),
    (
        "the newest close is itself re-opened",
        manifest(running=True), None, [], 1,
    ),
    (
        "held by hand",
        manifest(), None, [".hold-cycle"], 1,
    ),
    (
        "held by a build in flight",
        manifest(), None, [".build-in-progress"], 1,
    ),
    (
        "a claim that never reported done",
        manifest(day="7", start="2026-08-20 21:00", end=LATE),
        {"done": EARLY, "claimed": LATE, "claimed_at": "2026-08-21 02:20"}, [], 2,
    ),
    (
        "a claim already marked done is not stale",
        manifest(day="7", start="2026-08-20 21:00", end=LATE),
        {"done": LATE, "claimed": None}, [], 1,
    ),
    (
        "no row has ever closed",
        manifest(end=None), None, [], 2,
    ),
    (
        "the manifest is not there",
        None, None, [], 2,
    ),
    (
        "a schema this reader does not know stops it dead",
        manifest(schema=99), None, [], 2,
    ),
    (
        "a manifest with no rotation block at all",
        manifest(rotation=False), None, [], 2,
    ),
    (
        "prose in the file, no JSON",
        "This file is the rotation, and today it is only prose.\n", None, [], 2,
    ),
]


def run() -> int:
    failures = 0
    argv = sys.argv
    keep = (cr.MIRROR, osint_lib.MANIFEST, cr.STATE, cr.HOLD, cr.SENTINEL,
            cr.tree_dirty, cr.mirror_head)
    cr.tree_dirty = lambda: False
    cr.mirror_head = lambda: "0123456789abcdef"
    try:
        for name, manifest_text, state, touch, expected in CASES:
            tmp = Path(tempfile.mkdtemp(prefix="cycle-trigger-test-"))
            try:
                cr.MIRROR = str(tmp)
                osint_lib.MANIFEST = str(tmp / "cycle-manifest.json")
                cr.STATE = str(tmp / ".osint-cycle-seen")
                cr.HOLD = str(tmp / ".hold-cycle")
                cr.SENTINEL = str(tmp / ".build-in-progress")
                if manifest_text is not None:
                    Path(osint_lib.MANIFEST).write_text(manifest_text, encoding="utf-8")
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
            cr.MIRROR = str(tmp)
            osint_lib.MANIFEST = str(tmp / "cycle-manifest.json")
            cr.STATE = str(tmp / ".osint-cycle-seen")
            cr.HOLD, cr.SENTINEL = str(tmp / ".hold-cycle"), str(tmp / ".build-in-progress")
            Path(osint_lib.MANIFEST).write_text(manifest(), encoding="utf-8")

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
            cr.MIRROR = str(tmp)
            osint_lib.MANIFEST = str(tmp / "cycle-manifest.json")
            cr.STATE = str(tmp / ".osint-cycle-seen")
            cr.HOLD, cr.SENTINEL = str(tmp / ".hold-cycle"), str(tmp / ".build-in-progress")
            Path(osint_lib.MANIFEST).write_text(manifest(), encoding="utf-8")

            sys.argv = ["osint-cycle-ready.py", "--skip"]
            with redirect_stdout(io.StringIO()):
                skipped = cr.main()
            sys.argv = ["osint-cycle-ready.py"]
            with redirect_stdout(io.StringIO()):
                after_skip = cr.main()
            state = json.loads(Path(cr.STATE).read_text(encoding="utf-8"))

            # ...and the next close still fires, which is what makes skipping cost nothing
            Path(osint_lib.MANIFEST).write_text(
                manifest(day="7", start="2026-08-20 21:00", end=LATE), encoding="utf-8")
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
            cr.MIRROR = str(tmp)
            osint_lib.MANIFEST = str(tmp / "cycle-manifest.json")
            cr.STATE = str(tmp / ".osint-cycle-seen")
            cr.HOLD, cr.SENTINEL = str(tmp / ".hold-cycle"), str(tmp / ".build-in-progress")
            Path(osint_lib.MANIFEST).write_text(manifest(), encoding="utf-8")
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
            cr.MIRROR = str(tmp)
            osint_lib.MANIFEST = str(tmp / "cycle-manifest.json")
            cr.STATE = str(tmp / ".osint-cycle-seen")
            cr.HOLD, cr.SENTINEL = str(tmp / ".hold-cycle"), str(tmp / ".build-in-progress")
            Path(osint_lib.MANIFEST).write_text(manifest(), encoding="utf-8")

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
        (cr.MIRROR, osint_lib.MANIFEST, cr.STATE, cr.HOLD, cr.SENTINEL,
         cr.tree_dirty, cr.mirror_head) = keep

    print("all cases passed" if not failures else f"{failures} case(s) failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(run())
