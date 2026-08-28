#!/usr/bin/env python3
r"""lint-interface.py — Corpus reads OSINT's evidence, and nothing else of OSINT's.

Strategic review task 15. The boundary used to be one-directional but unbounded: Corpus
never wrote to `C:\OSINT`, and read whatever it liked. That is how it came to run linters
over OSINT's internal logs, parse `ingested_log.md` forensically, and carry incident
histories of OSINT's defects in its docstrings. The cause named in the review is an
implicit interface - because nothing defined what Corpus may rely on, Corpus read
everything and policed what it found.

So the interface is now stated as data, and this counts it.

**Corpus may read** OSINT's `raw/`, `wiki/` and `lookups/` - the evidence and the
vocabularies - and the mirror's own git metadata as a staleness clock. **Corpus may not
read** OSINT's `logs/`, `reviews/`, `index/`, `new/`, `sweep/` or any process file. The same
rule binds OSINT in the other direction, over the exchange share.

Two checks, and the second is the one that matters:

- **The workroot junction list.** `rebuild.py` -> `setup_workroot()` links what a stage
  reads, and every junction is a directory exposed to a process that can write. A junction
  onto a root outside the readable set is the boundary breached at the widest point.
- **Every OSINT path a script builds.** A literal first segment is checked against the
  readable set. A computed one is not guessed at: it has to be named in `COMPUTED`, with
  what it resolves to, because a silent skip would read as a pass.

**The known breaches are listed, not tolerated silently.** `EXCEPTIONS` names each one and
the condition that retires it - both retire on the cycle manifest of review task 14,
which is the artefact that replaces reading OSINT's logs at all. A breach not in the list
fails. **A listed breach that has gone also fails**, so the list shrinks as the work lands
rather than outliving it; that is the same both-directions discipline `lint-preambles.py`
applies to its rules.

Usage:  python scripts/lint-interface.py
        python scripts/lint-interface.py --scripts some/other/dir   # for tests
Exit:   0 the interface holds, 1 a read outside it or a stale exception, 2 the scripts
        directory is missing.
"""
from __future__ import annotations

import argparse
import ast
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")

# The interface, as data. Not "what the build happens to need" - what it is allowed.
READABLE = {"raw", "wiki", "lookups"}

# The two names a script binds the mirror root to. Both spellings of a path under them are
# in use — `os.path.join(MIRROR, ...)` and `MIRROR / ...` — and a check that knew only one
# would pass the other.
ROOT_NAMES = {"MIRROR", "OSINT"}

# Reads outside READABLE that exist today, each with what ends it. Keyed by
# (script, root). The reason is carried here rather than in a comment because the check
# reports it: a run that trips this should be told what the path is off, not just that it
# is off.
EXCEPTIONS = {
    ("osint_lib.py", "logs"):
        "the ingest and sweep-close stamps; retires on the cycle manifest (review task 14)",
    ("osint-cycle-ready.py", "logs"):
        "the sweep-cycle close row; retires on the cycle manifest (review task 14)",
}

# Path segments the source computes rather than spells, which the parse reports as a
# name. Each is listed with what it resolves to, because a segment nothing resolves is a
# hole in the check.
COMPUTED = {
    ("rebuild.py", "r"): "vault_lib.INDEX_ROOTS, asserted below to be within the set",
}

# Read straight out of the source: importing vault_lib to learn this would pull the whole
# vault index in to answer a two-element question.
INDEX_ROOTS_RE = re.compile(r"^INDEX_ROOTS\s*=\s*\(([^)]*)\)", re.M)


def index_roots(vault_src: str) -> set[str]:
    m = INDEX_ROOTS_RE.search(vault_src)
    if not m:
        return set()
    return {p.strip().strip("\"'") for p in m.group(1).split(",") if p.strip()}


def _named(node) -> str | None:
    """The name a path segment is written as, for a node that is not a literal."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def segments(source: str) -> list[tuple[int, str, bool]]:
    """(line number, first path segment, is_literal) for every OSINT path in `source`.

    Parsed rather than matched, because these files talk about the paths they read: this
    script's own docstring names OSINT's log directory, and so does `osint_lib.py`'s. A
    regex over the text reports the sentence as a read, and the only ways out of that are
    to stop writing the docstrings or to stop trusting the check. The tree carries no
    comments and no docstring bodies in expression position, so what it reports is what
    the script does."""
    found: list[tuple[int, str, bool]] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return found
    for node in ast.walk(tree):
        seg = None
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "join" and len(node.args) >= 2
                and isinstance(node.args[0], ast.Name) and node.args[0].id in ROOT_NAMES):
            seg = node.args[1]
        elif (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
              and isinstance(node.left, ast.Name) and node.left.id in ROOT_NAMES):
            seg = node.right
        if seg is None:
            continue
        if isinstance(seg, ast.Constant) and isinstance(seg.value, str):
            found.append((seg.lineno, seg.value, True))
        else:
            found.append((getattr(seg, "lineno", node.lineno), _named(seg) or "?", False))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="Corpus reads OSINT's evidence and nothing else.")
    ap.add_argument("--scripts", default=SCRIPTS, help="the scripts directory to scan")
    args = ap.parse_args()

    if not os.path.isdir(args.scripts):
        print(f"lint-interface: no scripts directory at {args.scripts}.")
        return 2

    failures: list[str] = []
    seen_exceptions: set[tuple[str, str]] = set()
    seen_computed: set[tuple[str, str]] = set()

    names = sorted(n for n in os.listdir(args.scripts)
                   if n.endswith(".py") and not n.startswith("test_"))

    vault = os.path.join(args.scripts, "vault_lib.py")
    if os.path.exists(vault):
        roots = index_roots(io.open(vault, encoding="utf-8").read())
        outside = roots - READABLE
        if outside:
            failures.append(f"vault_lib.INDEX_ROOTS names {sorted(outside)}, outside the "
                            f"readable set {sorted(READABLE)} - the workroot junctions "
                            f"every root in it.")

    for name in names:
        src = io.open(os.path.join(args.scripts, name), encoding="utf-8").read()
        for line, seg, literal in segments(src):
            if not literal:
                key = (name, seg)
                if key not in COMPUTED:
                    failures.append(f"{name}:{line} builds an OSINT path from '{seg}', "
                                    f"which this cannot resolve. Name it in COMPUTED with "
                                    f"what it resolves to, or use a literal.")
                else:
                    seen_computed.add(key)
                continue
            if seg in READABLE:
                continue
            key = (name, seg)
            if key in EXCEPTIONS:
                seen_exceptions.add(key)
                continue
            failures.append(f"{name}:{line} reads OSINT's '{seg}/', outside the readable "
                            f"set {sorted(READABLE)}. The interface is the evidence: "
                            f"raw/, wiki/, lookups/ and the mirror's git metadata.")

    # A list that only ever grows stops being a boundary and becomes a record of one.
    for key, why in sorted(EXCEPTIONS.items()):
        if key not in seen_exceptions:
            failures.append(f"EXCEPTIONS still allows {key[0]} to read '{key[1]}/' and it "
                            f"no longer does. Delete the entry - it was there because: {why}")
    for key, why in sorted(COMPUTED.items()):
        if key not in seen_computed:
            failures.append(f"COMPUTED still names {key[0]}'s '{key[1]}' and it is gone. "
                            f"Delete the entry - it was there because: {why}")

    for key in sorted(seen_exceptions):
        print(f"lint-interface: note - {key[0]} reads OSINT's {key[1]}/ - "
              f"{EXCEPTIONS[key]}")
    for msg in failures:
        print(f"lint-interface: FAIL - {msg}")
    if failures:
        return 1
    print(f"lint-interface: ok - {len(names)} script(s), reads confined to "
          f"{sorted(READABLE)} and {len(seen_exceptions)} listed exception(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
