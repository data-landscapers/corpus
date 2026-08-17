#!/usr/bin/env python3
"""test_log_line.py — prove the run line carries a duration, and the right one.

Same principle as `test_leak_check.py` and `test_mirror_freshness.py`: this only ever
runs at the end of a job, where a wrong answer looks exactly like a right one — a line
reading `47m` is not visibly different from a line that should have read `4h47m`.

Each case points the module's path constants at a temp directory holding a synthetic
`log.md`, runs `main()` with a built argv, and asserts on the line that came out.

    python scripts/test_log_line.py
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "log_line", Path(__file__).resolve().parent / "log-line.py")
ll = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ll)

HEADER = f"""---
type: log
title: test log
---

{ll.MARKER}
2026-08-16 12:00 · build · 1h00m · an earlier run — ok
"""

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


def run(tmp: Path, argv: list[str]) -> tuple[int, str, list[str]]:
    """Run main() against a fresh log in `tmp`; return (exit code, stdout, log lines)."""
    ll.ROOT = str(tmp)
    ll.LOGS = str(tmp / "logs")
    ll.RUN_LOG = str(tmp / "logs" / "log.md")
    (tmp / "logs").mkdir(exist_ok=True)
    if not (tmp / "logs" / "log.md").exists():
        (tmp / "logs" / "log.md").write_text(HEADER, encoding="utf-8", newline="\n")
    argv_before = sys.argv
    sys.argv = ["log-line.py", *argv]
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            rc = ll.main()
    finally:
        sys.argv = argv_before
    body = (tmp / "logs" / "log.md").read_text(encoding="utf-8").split("\n")
    at = body.index(ll.MARKER)
    return rc, out.getvalue(), body[at + 1:]


def stamped(minutes_ago: int) -> str:
    return (dt.datetime.now() - dt.timedelta(minutes=minutes_ago)).strftime(ll.STAMP_FMT)


print("format_took — a duration a reader takes in at a glance")
check("under a minute", ll.format_took(dt.timedelta(seconds=30)), "<1m")
check("minutes only", ll.format_took(dt.timedelta(minutes=47)), "47m")
check("hours pad the minutes", ll.format_took(dt.timedelta(hours=3, minutes=2)), "3h02m")
check("exactly an hour", ll.format_took(dt.timedelta(hours=1)), "1h00m")
check("days drop the minutes", ll.format_took(dt.timedelta(days=2, hours=4, minutes=9)),
      "2d 04h")
check("seconds never round up a minute", ll.format_took(dt.timedelta(minutes=5, seconds=59)),
      "5m")

print("parse_took — validated, so the field stays comparable")
check("bare number is minutes", ll.parse_took("90"), dt.timedelta(minutes=90))
check("the shape it emits", ll.parse_took("3h02m"), dt.timedelta(hours=3, minutes=2))
check("days and hours", ll.parse_took("2d 04h"), dt.timedelta(days=2, hours=4))
check("free text is refused", ll.parse_took("about three hours"), None)
check("an empty string is refused", ll.parse_took(""), None)

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)

    print("a run with no stamp says so rather than dropping the field")
    rc, out, lines = run(tmp, ["build", "nothing was stamped — ok"])
    check("exit 0", rc, 0)
    check("field reads unclocked", lines[0].split(" · ")[2], ll.UNCLOCKED)

    print("--start then a closing call reports measured elapsed")
    rc, out, _ = run(tmp, ["--start", "build", "--at", stamped(182)])
    check("--start exits 0", rc, 0)
    check("the stamp was written", Path(ll.stamp_path("build")).exists(), True)
    rc, out, lines = run(tmp, ["build", "44 units — ok"])
    check("duration is the measured gap", lines[0].split(" · ")[2], "3h02m")
    check("the stamp is cleared once written", Path(ll.stamp_path("build")).exists(), False)

    print("the stamp is per job, so two passes can be in flight at once")
    run(tmp, ["--start", "build", "--at", stamped(120)])
    run(tmp, ["--start", "render", "--at", stamped(30)])
    _, _, lines = run(tmp, ["render", "241 documents — ok"])
    check("render reports its own start", lines[0].split(" · ")[2], "30m")
    _, _, lines = run(tmp, ["build", "44 units — ok"])
    check("build's stamp survived render's line", lines[0].split(" · ")[2], "2h00m")

    print("--took and --since state it by hand")
    _, _, lines = run(tmp, ["build", "x — ok", "--took", "4h15m"])
    check("--took is used verbatim", lines[0].split(" · ")[2], "4h15m")
    _, _, lines = run(tmp, ["build", "x — ok", "--since", "2026-08-17 06:00",
                            "--at", "2026-08-17 09:30"])
    check("--since is measured against --at", lines[0].split(" · ")[2], "3h30m")
    rc, out, _ = run(tmp, ["build", "x — ok", "--took", "ages"])
    check("an unparseable --took refuses the write", rc, 1)
    rc, out, _ = run(tmp, ["build", "x — ok", "--took", "1h", "--since", "2026-08-17 06:00"])
    check("--took and --since together are refused", rc, 1)

    print("explicit beats a stamp that may belong to an abandoned run")
    run(tmp, ["--start", "build", "--at", stamped(600)])
    _, _, lines = run(tmp, ["build", "x — ok", "--took", "20m"])
    check("--took wins over the stamp", lines[0].split(" · ")[2], "20m")
    check("and leaves the stamp alone", Path(ll.stamp_path("build")).exists(), True)

    print("a clock that runs backwards is reported as unclocked, not as a negative")
    _, out, lines = run(tmp, ["build", "x — ok", "--since", "2026-08-17 12:00",
                              "--at", "2026-08-17 09:00"])
    check("field reads unclocked", lines[0].split(" · ")[2], ll.UNCLOCKED)
    check("and the run is told why", "is after this line's own time" in out, True)

    print("an unreadable stamp is cleared rather than left to poison every later run")
    io.open(ll.stamp_path("build"), "w", encoding="utf-8").write("yesterday\n")
    _, out, lines = run(tmp, ["build", "x — ok"])
    check("field reads unclocked", lines[0].split(" · ")[2], ll.UNCLOCKED)
    check("the bad stamp is gone", Path(ll.stamp_path("build")).exists(), False)

    print("the first two fields do not move — lint-mirror-freshness matches on them")
    import re
    RUN_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s+·\s+(\w[\w-]*)\s+·")
    _, _, lines = run(tmp, ["render", "241 documents — ok"])
    m = RUN_RE.match(lines[0])
    check("the freshness regex still matches", bool(m), True)
    check("and still reads the pass name", m.group(2) if m else None, "render")

    print("--start refuses a message; the closing call requires one")
    rc, out, _ = run(tmp, ["--start", "build", "message here"])
    check("--start with a message exits 1", rc, 1)

print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
