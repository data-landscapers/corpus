#!/usr/bin/env python3
"""test_lint_interface.py — prove the interface check sees code and not prose.

The failure this guards against is a check that passes because it found nothing: a parse
that misses `MIRROR / "logs"`, a scan that skips a computed segment, or an exception list
that has quietly become a permanent licence. Each case runs the check over a synthetic
scripts directory and asserts on the exit code and the message.

    python scripts/test_lint_interface.py
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "lint_interface", Path(__file__).resolve().parent / "lint-interface.py")
li = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(li)

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


VAULT = 'INDEX_ROOTS = ("raw", "wiki")\n'


def build(tmp: Path, **files: str) -> Path:
    d = tmp / "scripts"
    if d.exists():
        for f in d.iterdir():
            f.unlink()
    d.mkdir(parents=True, exist_ok=True)
    (d / "vault_lib.py").write_text(files.pop("vault_lib.py", VAULT), encoding="utf-8",
                                    newline="\n")
    for name, src in files.items():
        (d / name).write_text(src, encoding="utf-8", newline="\n")
    return d


def run(scripts: Path) -> tuple[int, str]:
    argv_before = sys.argv
    sys.argv = ["lint-interface.py", "--scripts", str(scripts)]
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            rc = li.main()
    finally:
        sys.argv = argv_before
    return rc, out.getvalue()


print("segments — both spellings of a path, and neither prose nor comment")
check("os.path.join is read",
      li.segments('import os\np = os.path.join(MIRROR, "raw", "x")\n'), [(2, "raw", True)])
check("the / spelling is read",
      li.segments('p = MIRROR / "wiki"\n'), [(1, "wiki", True)])
check("a nested / chain reports the first segment",
      li.segments('p = MIRROR / "lookups" / "countries.csv"\n'), [(1, "lookups", True)])
check("a computed segment is reported, not skipped",
      li.segments('p = os.path.join(OSINT, root, "x")\n'), [(1, "root", False)])
check("a docstring naming a path is not a read",
      li.segments('"""Reads os.path.join(MIRROR, \\"logs\\") once upon a time."""\n'), [])
check("a comment naming a path is not a read",
      li.segments('# os.path.join(MIRROR, "logs")\np = 1\n'), [])
check("an unrelated join is not a read",
      li.segments('p = os.path.join(ROOT, "logs")\n'), [])

print("index_roots — read out of the source, not imported")
check("the tuple is parsed", li.index_roots(VAULT), {"raw", "wiki"})
check("a missing declaration is empty, not a crash", li.index_roots("x = 1\n"), set())

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    saved_exc, saved_comp = dict(li.EXCEPTIONS), dict(li.COMPUTED)

    print("a script reading only the evidence passes")
    li.EXCEPTIONS, li.COMPUTED = {}, {}
    rc, out = run(build(tmp, **{"a.py": 'p = os.path.join(MIRROR, "raw", "x")\n'
                                        'q = MIRROR / "lookups"\n'}))
    check("exit 0", rc, 0)
    check("and says what it confined", "reads confined to" in out, True)

    print("a read outside the set fails and names the root")
    rc, out = run(build(tmp, **{"a.py": 'p = os.path.join(MIRROR, "reviews", "x")\n'}))
    check("exit 1", rc, 1)
    check("names the root", "reads OSINT's 'reviews/'" in out, True)

    print("a listed exception is reported, not failed")
    li.EXCEPTIONS = {("a.py", "logs"): "a stated reason"}
    rc, out = run(build(tmp, **{"a.py": 'p = os.path.join(MIRROR, "logs", "x")\n'}))
    check("exit 0", rc, 0)
    check("but it is on the record", "note - a.py reads OSINT's logs/ - a stated reason"
          in out, True)

    print("an exception that no longer applies fails, so the list shrinks")
    rc, out = run(build(tmp, **{"a.py": 'p = os.path.join(MIRROR, "raw", "x")\n'}))
    check("exit 1", rc, 1)
    check("says to delete the entry", "Delete the entry" in out, True)

    print("a computed segment must be named, and a stale name fails too")
    li.EXCEPTIONS, li.COMPUTED = {}, {}
    rc, out = run(build(tmp, **{"a.py": 'p = os.path.join(MIRROR, root, "x")\n'}))
    check("an unnamed computed segment fails", rc, 1)
    check("and asks for it to be named", "Name it in COMPUTED" in out, True)
    li.COMPUTED = {("a.py", "root"): "a stated reason"}
    rc, out = run(build(tmp, **{"a.py": 'p = os.path.join(MIRROR, root, "x")\n'}))
    check("a named one passes", rc, 0)
    rc, out = run(build(tmp, **{"a.py": 'p = os.path.join(MIRROR, "raw", "x")\n'}))
    check("a name that has gone fails", rc, 1)

    print("INDEX_ROOTS is checked, because the workroot junctions every root in it")
    li.COMPUTED = {}
    rc, out = run(build(tmp, **{"vault_lib.py": 'INDEX_ROOTS = ("raw", "wiki", "logs")\n',
                                "a.py": "p = 1\n"}))
    check("exit 1", rc, 1)
    check("names the offending root", "INDEX_ROOTS names ['logs']" in out, True)

    print("tests are not scanned — they build paths to prove the check works")
    rc, out = run(build(tmp, **{"test_a.py": 'p = os.path.join(MIRROR, "reviews")\n',
                                "a.py": "p = 1\n"}))
    check("exit 0", rc, 0)

    print("a missing scripts directory is a 2, not a pass")
    rc, out = run(tmp / "nowhere")
    check("exit 2", rc, 2)

    li.EXCEPTIONS, li.COMPUTED = saved_exc, saved_comp

print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
