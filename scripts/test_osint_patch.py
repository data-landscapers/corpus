#!/usr/bin/env python3
r"""test_osint_patch.py — the patch route refuses what it is not allowed to send.

    python scripts/test_osint_patch.py

`osint-patch.py` is the one script in this repo that produces a commit for **another
repository**, so the case that matters is the refusal: a patch straying into `raw/`, into wiki
prose, or into OSINT's `logs/` must not be cut at all. OSINT runs its own check before `git am`
and that is the guard — but a check that only ever fires on the far side is one nobody here
ever sees working.

Every case builds a real git repository in a temp directory and drives the script against it,
because what the script reads is `git status --porcelain`: a fixture of path strings would test
the author's idea of git's output rather than git's.
"""

from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))
_spec = importlib.util.spec_from_file_location("osint_patch", _here / "osint-patch.py")
op = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(op)

failures = ran = 0


def check(name, got, want):
    global failures, ran
    ran += 1
    ok = got == want
    failures += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f"  (got {got!r}, want {want!r})"))


def repo(tmp: Path) -> Path:
    """A repository shaped like OSINT's, with one commit under every tree the check knows."""
    r = tmp / "work"
    r.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "master", str(r)], check=True)
    subprocess.run(["git", "-C", str(r), "config", "user.email", "t@example.com"], check=True)
    subprocess.run(["git", "-C", str(r), "config", "user.name", "test"], check=True)
    for path in ("scripts/a.py", "lookups/b.csv", "wiki/index.md",
                 "wiki/intersections/c.md", "raw/2026/d.md", "logs/log.md"):
        p = r / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("one\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(r), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(r), "commit", "-qm", "base"], check=True)
    return r


print("the allowed set, path by path")
for path, want in [
    ("scripts/a.py", []),
    ("lookups/b.csv", []),
    ("wiki/index.md", []),
    ("wiki/places-index.md", []),
    ("wiki/topics-index.md", []),
    ("wiki/intersections/c.md", ["wiki/intersections/c.md"]),
    ("wiki/facets.md", ["wiki/facets.md"]),
    ("raw/2026/d.md", ["raw/2026/d.md"]),
    ("logs/log.md", ["logs/log.md"]),
    ("SWEEP-CYCLE.md", ["SWEEP-CYCLE.md"]),
]:
    check(f"{path} is {'allowed' if not want else 'refused'}", op.outside([path]), want)

# git reports Windows paths with forward slashes, but a caller passing the other spelling must
# not slip past the prefix test.
check("a backslash spelling is read the same way", op.outside([r"raw\2026\d.md"]),
      ["raw/2026/d.md"])
check("a quoted path (git quotes unusual names) is unquoted before the test",
      op.outside(['"raw/2026/d.md"']), ["raw/2026/d.md"])

print("\nwhat git reports as changed is what is checked")
tmp = Path(tempfile.mkdtemp(prefix="osint-patch-test-"))
saved_work, saved_prepared = op.CLONE, op.PREPARED
try:
    r = repo(tmp)
    op.CLONE = str(r)
    op.PREPARED = str(tmp / "share" / "prepared")

    check("a clean clone has nothing to cut", op.changed(str(r)), [])

    (r / "scripts" / "a.py").write_text("two\n", encoding="utf-8")
    (r / "lookups" / "new.csv").write_text("x\n", encoding="utf-8")
    check("a modified file and an untracked one are both reported",
          op.changed(str(r)), ["lookups/new.csv", "scripts/a.py"])
    check("both are inside the allowed set", op.outside(op.changed(str(r))), [])

    print("\ncut writes a series and a BASE, and refuses a stray path")
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = op.cut("102-103", "the label fallback", dry_run=False)
    check("a clean cut returns 0", code, 0)
    written = sorted(os.listdir(os.path.join(op.PREPARED, "job-102-103")))
    check("BASE is written beside the series", "BASE" in written, True)
    check("one commit makes one patch", sum(f.endswith(".patch") for f in written), 1)
    base = io.open(os.path.join(op.PREPARED, "job-102-103", "BASE"),
                   encoding="utf-8").read().splitlines()[0]
    check("BASE names a full commit id", len(base), 40)
    check("the commit subject names the job",
          op.git("log", "-1", "--format=%s", cwd=str(r)).strip(),
          "job 102-103: the label fallback")

    # The refusal: one allowed edit and one that is not. Nothing may be committed — a partial
    # commit would leave the clone holding half a job and the operator believing it was sent.
    (r / "scripts" / "a.py").write_text("three\n", encoding="utf-8")
    (r / "raw" / "2026" / "d.md").write_text("tampered\n", encoding="utf-8")
    head_before = op.git("rev-parse", "HEAD", cwd=str(r)).strip()
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = op.cut("105", "an edit that strays", dry_run=False)
    check("a stray path refuses with exit 2", code, 2)
    check("the stray path is named", "raw/2026/d.md" in err.getvalue(), True)
    check("nothing was committed", op.git("rev-parse", "HEAD", cwd=str(r)).strip(), head_before)
    check("no directory was made for the refused job",
          os.path.isdir(os.path.join(op.PREPARED, "job-105")), False)

    print("\nthe work clone may not sit inside either repository")
    op.CLONE = os.path.join(op.osint_lib.MIRROR, "scratch")
    check("a clone inside the mirror is refused", bool(op.guard_paths()), True)
    op.CLONE = os.path.join(os.path.dirname(str(_here)), "scratch")
    check("a clone inside Corpus is refused", bool(op.guard_paths()), True)
    op.CLONE = str(r)
    check("a clone outside both is fine", op.guard_paths(), None)
finally:
    op.CLONE, op.PREPARED = saved_work, saved_prepared
    # Windows keeps .git read-only files; rmtree with a chmod fallback.
    def _rm(func, path, _exc):
        os.chmod(path, 0o700)
        func(path)
    import shutil
    shutil.rmtree(tmp, onerror=_rm)

print()
if failures:
    print(f"{failures} of {ran} cases FAILED")
    sys.exit(1)
print(f"all {ran} cases passed")
