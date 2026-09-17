#!/usr/bin/env python3
"""test_osint_freshness.py — prove the OSINT freshness check fires.

Same principle as `test_mirror_freshness.py`: this check reads `ok`
for weeks at a time in normal use, and a check that has only ever passed is not evidence of
anything. What it guards is worse than a late backup — a stale mirror means Corpus compiles,
reports and publishes from old evidence without saying so — so the fault paths are the part
that has to be shown working.

Each case builds a synthetic mirror in a temp directory holding one file,
`cycle-manifest.json`, plus a watermark and a stubbed `HEAD` commit date standing in for the
one git would report. The module's constants are repointed at it and the exit code asserted.

**The log fixtures went with the log reads** *(2026-09-06, `notes-for-corpus` 16)*. Two
suites here used to build `logs/ingested_log.md` and `logs/sweep-cycle_log.md` and pin the
forensics that parsing them needed — a heading four hours in the reader's future, a
date-only heading read at midnight, a queue-drain whose `sweep_closed` walked backwards.
Every one of those was a defence against a format Corpus did not own. What replaces them is
`manifest_cases()`: the manifest is refused, loudly, when it is a schema this does not know
or an account of a tree the mirror is not holding. **Fewer cases guarding a smaller
surface** is the point of the change and not a loss of cover — but the one thing that must
not go with them is the demand that an unreadable mirror be reported rather than
substituted for, which is what the last two `CASES` rows are.

    python scripts/test_osint_freshness.py
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))
import osint_lib  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "lint_osint_freshness", _here / "lint-osint-freshness.py")
of = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(of)

TS = "%Y-%m-%d %H:%M"


def ago(hours: float) -> dt.datetime:
    return dt.datetime.now() - dt.timedelta(hours=hours)


def stamp(hours: float) -> str:
    return ago(hours).strftime(TS)


def manifest(admission: float | None = None, closed: float | None = None,
             close_end: float | None = None, in_progress: list[str] | None = None,
             schema: int = 1) -> str:
    """The cycle manifest as OSINT writes it, with the fields these cases read.

    `head` is deliberately absent. `read_manifest` only compares it against the mirror's own
    HEAD, and a temp directory is not a git repository, so a `head` here would be checked
    against a `None` and skipped — a fixture field nothing reads is a fixture field that will
    one day be wrong without anything noticing."""
    data: dict = {"schema": schema, "written_utc": stamp(0), "pass": "sweep cycle"}
    collection = {}
    if admission is not None:
        collection["last_admission"] = stamp(admission)
    if closed is not None:
        collection["sweep_closed"] = stamp(closed)
    if collection:
        data["collection"] = collection
    rotation: dict = {"days": 5, "in_progress": in_progress or []}
    if close_end is not None:
        rotation["newest_close"] = {"day": "3", "jobs": ["SWEEP-COUNTRY-DEEP"],
                                    "start": stamp(close_end + 1), "end": stamp(close_end),
                                    "duration": "1:00", "skipped": False,
                                    "in_progress": False}
    data["rotation"] = rotation
    return json.dumps(data, indent=1)


# (name, admission hours ago | None, sweep_closed hours ago | None, close End hours ago | None,
#  HEAD hours ago | None, watermark hours ago | None, argv extras, expected exit).
# A `None` for all three manifest stamps means no manifest is written at all.
CASES: list[tuple[str, float | None, float | None, float | None, float | None, float | None,
                  list[str], int]] = [
    (
        "everything fresh",
        1.0, 1.1, 2.0, 0.5, 2.0, [], 0,
    ),
    (
        "quiet between cycles — 70 minutes behind is the normal state",
        1.2, 1.2, 1.2, 1.2, 1.2, [], 0,
    ),
    (
        "the whole mirror is three days old",
        24 * 3.5, 24 * 3.5, 24 * 3.5, 24 * 3.5, 24 * 3.5, [], 1,
    ),
    (
        "old, but inside a raised ceiling",
        24 * 3.5, 24 * 3.5, 24 * 3.5, 24 * 3.5, 24 * 3.5, ["--max-age-hours", "200"], 0,
    ),
    (
        "HEAD alone is fresh — an OSINT commit outside a cycle still counts",
        24 * 5, 24 * 5, 24 * 5, 1.0, 24 * 5, [], 0,
    ),
    (
        "the manifest alone is fresh, git unreadable",
        1.0, 1.1, 2.0, None, 24 * 5, [], 0,
    ),
    (
        "regressed — the mirror's newest close predates the one Corpus built",
        1.0, 1.1, 30.0, 0.5, 2.0, [], 1,
    ),
    (
        "not regressed — the newest close is the one Corpus built",
        1.0, 1.1, 2.0, 0.5, 2.0, [], 0,
    ),
    (
        "no watermark yet — a first run is not a regression",
        1.0, 1.1, 2.0, 0.5, None, [], 0,
    ),
    (
        "nothing readable at all",
        None, None, None, None, 2.0, [], 2,
    ),
    (
        "an unreadable mirror is not reported as merely stale",
        None, None, None, None, 24 * 9, ["--max-age-hours", "1"], 2,
    ),
]


def manifest_cases() -> tuple[int, int]:
    """The manifest is the whole interface now, so its refusals are the whole of the guard.

    Three of these were written when the manifest was one source among two and a refusal
    only meant *fall back to the logs*. Since 2026-09-06 a refusal means Corpus has no
    reading of OSINT's clocks at all, which is a louder thing and worth pinning harder: an
    unknown schema and a half-copied file must both come back `None` **with a reason**, never
    as a plausible-looking stamp."""
    failures = 0
    saved = (osint_lib.MANIFEST, osint_lib.ARCHIVE)
    tmp = Path(tempfile.mkdtemp(prefix="osint-manifest-test-"))
    try:
        osint_lib.MANIFEST = str(tmp / "cycle-manifest.json")
        # The schema-2 case is read like any other, and a read keeps a copy: without this the
        # suite writes into the repository's own `logs/manifests/` (caught 2026-09-17, one
        # fixture manifest left behind in the working tree).
        osint_lib.ARCHIVE = str(tmp / "manifests")
        path = Path(osint_lib.MANIFEST)

        # (name, file text or None, expected sweep_closed, a word the reason must carry)
        cases: list[tuple[str, str | None, str | None, str]] = [
            ("a manifest answers the byline",
             manifest(admission=1.0, closed=1.1, close_end=2.0), stamp(1.1), "manifest"),
            ("no manifest is None, not today",
             None, None, "no cycle manifest"),
            ("a half-copied manifest will not parse and is refused",
             '{"schema": 1, "collection": {"sweep_cl', None, "half-copied"),
            ("a schema this reader does not know is refused, not guessed at",
             manifest(admission=1.0, closed=1.1, close_end=2.0, schema=99), None, "schema"),
            ("schema 2 is read, so the reader lands before OSINT's writer does (R07)",
             manifest(admission=1.0, closed=1.1, close_end=2.0, schema=2), stamp(1.1),
             "manifest"),
            ("a manifest that is not an object at all is refused",
             '["schema", 1]', None, "not an object"),
            ("a manifest carrying no collection block answers None",
             manifest(close_end=2.0), None, "manifest"),
        ]
        for name, text, expected, word in cases:
            if text is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(text, encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                got = osint_lib.sweep_closed()
                _data, why = osint_lib.read_manifest()
            got_s = got.strftime(TS) if got else None
            ok = got_s == expected and word.lower() in why.lower()
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} {name}  "
                  f"(expected {expected}, got {got_s}; reason: {why[:70]})")

        # A read that fails is not an absence (notes-for-corpus 28): a path into a folder that
        # is not there, and a path that is a folder rather than a file, must both say
        # "unreadable" and never "no cycle manifest".
        path.unlink(missing_ok=True)
        unreachable = str(tmp / "no-such-mirror" / "cycle-manifest.json")
        path.mkdir()
        for name, where in [("a mirror that cannot be reached is unreadable, not absent", unreachable),
                            ("a manifest that cannot be opened is unreadable, not absent", str(path))]:
            _data, why = osint_lib.read_manifest(where)
            ok = _data is None and "unreadable" in why and "no cycle manifest" not in why
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} {name}  (reason: {why[:70]})")
        path.rmdir()
    finally:
        osint_lib.MANIFEST, osint_lib.ARCHIVE = saved
        shutil.rmtree(tmp, ignore_errors=True)
    return failures, len(cases) + 2


def archive_cases() -> tuple[int, int]:
    """What Corpus keeps of a manifest it has read (register R07).

    The mirror holds one manifest and every close overwrites it, so a `usage` block lives on
    the disk for one night. The stage-cost table reads a whole rotation, which means the copy
    has to be taken at the moment of reading or not at all. Three properties are worth
    pinning: a schema-1 manifest leaves nothing behind (there is nothing in it that the
    mirror will not still hold tomorrow), a schema-2 one is kept, and reading the same one
    twice keeps one file — every stamp reader calls `read_manifest` again, so a copy per read
    would be a directory of duplicates by morning."""
    failures = ran = 0
    saved_manifest, saved_archive = osint_lib.MANIFEST, osint_lib.ARCHIVE
    tmp = Path(tempfile.mkdtemp(prefix="osint-archive-test-"))
    try:
        osint_lib.MANIFEST = str(tmp / "cycle-manifest.json")
        osint_lib.ARCHIVE = str(tmp / "manifests")
        path = Path(osint_lib.MANIFEST)

        for name, text, expected in [
            ("a schema-1 manifest is read and nothing is kept",
             manifest(admission=1.0, closed=1.1, close_end=2.0), 0),
            ("a schema-2 manifest is kept once it has been read",
             manifest(admission=1.0, closed=1.1, close_end=2.0, schema=2), 1),
        ]:
            path.write_text(text, encoding="utf-8")
            data, why = osint_lib.read_manifest()
            kept = sorted(Path(osint_lib.ARCHIVE).glob("*.json")) \
                if os.path.isdir(osint_lib.ARCHIVE) else []
            ok = data is not None and len(kept) == expected
            failures += not ok
            ran += 1
            print(f"  {'ok  ' if ok else 'FAIL'} {name}  "
                  f"(expected {expected} kept, got {len(kept)}; reason: {why[:40]})")

        # The same manifest read again: every stamp reader calls through here, so this is the
        # ordinary case rather than an edge one.
        before = sorted(p.name for p in Path(osint_lib.ARCHIVE).glob("*.json"))
        for _ in range(3):
            osint_lib.read_manifest()
        after = sorted(p.name for p in Path(osint_lib.ARCHIVE).glob("*.json"))
        ok = before == after and len(after) == 1
        failures += not ok
        ran += 1
        print(f"  {'ok  ' if ok else 'FAIL'} re-reading the same manifest keeps one file  "
              f"(before {len(before)}, after {len(after)})")

        # An archive that cannot be written must cost the caller nothing: the manifest is the
        # read, the copy is bookkeeping beside it.
        osint_lib.ARCHIVE = str(path)          # a file where a directory would have to go
        data, why = osint_lib.read_manifest()
        ok = data is not None
        failures += not ok
        ran += 1
        print(f"  {'ok  ' if ok else 'FAIL'} an unwritable archive still returns the manifest  "
              f"(reason: {why[:40]})")
    finally:
        osint_lib.MANIFEST, osint_lib.ARCHIVE = saved_manifest, saved_archive
        shutil.rmtree(tmp, ignore_errors=True)
    return failures, ran


def collected_to_cases() -> tuple[int, int]:
    """`collected_to()` is the bulletin byline's one claim, and it publishes what it returns.

    It used to take the later of two readings because neither `sweep_closed` nor the cycle's
    `End` covered every path that admits to `raw/`; the manifest is written by every pass
    that mirrors, so `sweep_closed` answers alone (`notes-for-corpus` 16). What is left to
    guard is the refusal: a stated close in the reader's future is a claim about work that
    has not happened, and it must come back `None` so `bulletin.stamps_for()` falls to
    something it can defend rather than publishing it."""
    failures = 0
    saved = osint_lib.MANIFEST
    tmp = Path(tempfile.mkdtemp(prefix="osint-collected-test-"))
    try:
        osint_lib.MANIFEST = str(tmp / "cycle-manifest.json")
        path = Path(osint_lib.MANIFEST)

        cases: list[tuple[str, str | None, str | None]] = [
            ("the stated close is the answer",
             manifest(admission=1.0, closed=1.1, close_end=2.0), stamp(1.1)),
            ("skew of a minute or two is believed, not thrown away",
             manifest(admission=1.0, closed=-2 / 60, close_end=2.0), stamp(-2 / 60)),
            ("a close two days into the future is refused rather than published",
             manifest(admission=1.0, closed=-48.0, close_end=2.0), None),
            ("a manifest with no sweep_closed answers None, not the cycle's End",
             manifest(admission=1.0, close_end=2.0), None),
            ("no manifest at all is None",
             None, None),
        ]
        for name, text, expected in cases:
            if text is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(text, encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                got, why = osint_lib.collected_to()
            got_s = got.strftime(TS) if got else None
            ok = got_s == expected
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} {name}  "
                  f"(expected {expected}, got {got_s}; from: {why[:60]})")
    finally:
        osint_lib.MANIFEST = saved
        shutil.rmtree(tmp, ignore_errors=True)
    return failures, len(cases)


def run() -> int:
    failures = 0
    argv = sys.argv
    saved = (osint_lib.MIRROR, osint_lib.MANIFEST, of.WATERMARK, of.head_committed)
    try:
        for name, adm, closed, end, head, mark, extra, expected in CASES:
            tmp = Path(tempfile.mkdtemp(prefix="osint-fresh-test-"))
            try:
                osint_lib.MIRROR = str(tmp)
                # Repointed rather than left at the module default, which names the real
                # mirror — every case would otherwise be measuring that instead of itself.
                osint_lib.MANIFEST = str(tmp / "cycle-manifest.json")
                of.WATERMARK = str(tmp / ".osint-cycle-seen")

                if any(v is not None for v in (adm, closed, end)):
                    Path(osint_lib.MANIFEST).write_text(
                        manifest(admission=adm, closed=closed, close_end=end),
                        encoding="utf-8")
                if mark is not None:
                    Path(of.WATERMARK).write_text(json.dumps(
                        {"done": stamp(mark), "done_by": "built"}), encoding="utf-8")

                of.head_committed = (lambda h=head: None if h is None else ago(h))

                sys.argv = ["lint-osint-freshness.py", *extra]
                buf = io.StringIO()
                with redirect_stdout(buf):
                    got = of.main()

                ok = got == expected
                failures += not ok
                verdict = "ok  " if ok else "FAIL"
                print(f"  {verdict} {name}  (expected {expected}, got {got})")
                if not ok:
                    for ln in buf.getvalue().splitlines():
                        print(f"       {ln}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    finally:
        sys.argv = argv
        (osint_lib.MIRROR, osint_lib.MANIFEST, of.WATERMARK, of.head_committed) = saved

    man_failures, man_ran = manifest_cases()
    arc_failures, arc_ran = archive_cases()
    col_failures, col_ran = collected_to_cases()
    failures += man_failures + arc_failures + col_failures
    # Counted off the case lists, not added up by hand. It read `len(CASES) + 4 + 6` until
    # 2026-08-24, when three cases were added to a sub-suite and the run went on reporting
    # 22 — a suite that miscounts itself is a suite that can quietly stop running something.
    total = len(CASES) + man_ran + arc_ran + col_ran

    print()
    if failures:
        print(f"{failures} of {total} cases FAILED")
        return 1
    print(f"all {total} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
