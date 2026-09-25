#!/usr/bin/env python3
r"""lint-interface.py — no Corpus script watches OSINT's process.

Strategic review task 15. The boundary used to be one-directional but unbounded: Corpus
never wrote to `C:\OSINT`, and read whatever it liked. That is how it came to run linters
over OSINT's internal logs, parse `ingested_log.md` forensically, and carry incident
histories of OSINT's defects in its docstrings. The cause named in the review is an
implicit interface - because nothing defined what Corpus may rely on, Corpus read
everything and policed what it found.

So the interface is now stated as data, and this counts it.

**Reading is not restricted; attention is** (Bill, 2026-09-25). A script may read OSINT's
`raw/`, `wiki/`, `lookups/` and `budget-archive/` - the evidence, the vocabularies and the
documents - the mirror's `cycle-manifest.json`, and the mirror's own git metadata as a
staleness clock. **Corpus may not read** OSINT's `logs/`, `reviews/`, `index/`, `new/`,
`sweep/` or any process file. The same rule binds OSINT in the other direction, over the
exchange share.

Two checks, and the second is the one that matters:

- **The workroot junction list.** `rebuild.py` -> `setup_workroot()` links what a stage
  reads, and every junction is a directory exposed to a process that can write. A junction
  onto a root outside the readable set is the boundary breached at the widest point.
- **Every OSINT path a script builds.** A literal first segment is checked against the
  readable set. A computed one is not guessed at: it has to be named in `COMPUTED`, with
  what it resolves to, because a silent skip would read as a pass.

**The known breaches are listed, not tolerated silently.** `EXCEPTIONS` names each one and
the condition that retires it. A breach not in the list fails. **A listed breach that has
gone also fails**, so the list shrinks as the work lands rather than outliving it; that is
the same both-directions discipline `lint-preambles.py` applies to its rules. It worked:
the two it opened with - `osint_lib.py`'s log fallback and `osint-cycle-ready.py`'s
rotation-table parse - were both listed against the cycle manifest of review task 14, and
both went when that manifest landed. **The list is empty**, which is the state it was
written to reach and not a reason to stop asserting it.

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

# The interface, as data. Not "what the build happens to need" - what it is allowed. The
# three directories are the evidence and the vocabularies; `cycle-manifest.json` is the one
# file, and the review named it when it defined the interface: OSINT's machine-readable
# account of a close, which is what lets Corpus stop reading OSINT's logs at all.
# `budget-archive` joined on 2026-09-25 (Bill): reading is not what the boundary restricts -
# watching OSINT's process is. The budget volumes are evidence, and a budget sitting reads
# them rather than re-fetching the publisher's copy to prove the same bytes.
READABLE = {"raw", "wiki", "lookups", "budget-archive", "cycle-manifest.json"}

# The two names a script binds the mirror root to. Both spellings of a path under them are
# in use — `os.path.join(MIRROR, ...)` and `MIRROR / ...` — and a check that knew only one
# would pass the other.
ROOT_NAMES = {"MIRROR", "OSINT"}

# **The work clone is the same boundary at a different address** *(strategic review 4, R1
# and R15)*. `osint-patch.py` clones the mirror and edits the clone, so a path built on that
# root reaches OSINT's material exactly as a path on the mirror does — and unlike the mirror
# it is written to. What may be written is narrower than what may be read: `scripts/`,
# `lookups/` and the wiki index pages, never `raw/`, never wiki prose, never OSINT's own
# files. `.git` is here because cloning and committing are how the lane works at all.
CLONE_NAMES = {"CLONE"}
# `WORK` is taken: `rebuild.py` binds it to Corpus's own `.workroot`, which is why the
# clone constant is named for what it is rather than for where the work happens.
CLONE_TREES = {"scripts", "lookups", "wiki", ".git"}

# The script that owns the lane, and the constants that state its allowed set. They are read
# out of the source rather than imported, for `index_roots`'s reason: the module opens a
# clone and talks to git, and a lint should not need either to answer a question about text.
PATCH_SCRIPT = "osint-patch.py"
ALLOWED_RE = re.compile(r"^ALLOWED_(?:DIRS|FILES)\s*=\s*\(([^)]*)\)", re.M)


def patch_allowed(src: str) -> set[str]:
    """The first path segment of everything `osint-patch.py` says a patch may touch."""
    out: set[str] = set()
    for m in ALLOWED_RE.finditer(src):
        for item in m.group(1).split(","):
            item = item.strip().strip("\"'").replace("\\", "/")
            if item:
                out.add(item.split("/")[0])
    return out

# Reads outside READABLE that exist today, each with what ends it. Keyed by
# (script, root). The reason is carried here rather than in a comment because the check
# reports it: a run that trips this should be told what the path is off, not just that it
# is off.
EXCEPTIONS: dict[tuple[str, str], str] = {
    # Empty since 2026-09-06, and that is the point of it. It held two: `osint_lib.py`'s
    # fallback for a mirror carrying no manifest, and `osint-cycle-ready.py` reading the
    # whole rotation row. Both retired on the cycle manifest of review task 14 - the
    # condition each was listed with - when `notes-for-corpus` 16 was drained. Anything
    # added here is a breach with a stated end, never a permission.
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


def segments(source: str, roots: set[str] | None = None) -> list[tuple[int, str, bool]]:
    """(line number, first path segment, is_literal) for every OSINT path in `source`.

    Parsed rather than matched, because these files talk about the paths they read: this
    script's own docstring names OSINT's log directory, and so does `osint_lib.py`'s. A
    regex over the text reports the sentence as a read, and the only ways out of that are
    to stop writing the docstrings or to stop trusting the check. The tree carries no
    comments and no docstring bodies in expression position, so what it reports is what
    the script does."""
    roots = ROOT_NAMES if roots is None else roots
    found: list[tuple[int, str, bool]] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return found
    for node in ast.walk(tree):
        seg = None
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "join" and len(node.args) >= 2
                and isinstance(node.args[0], ast.Name) and node.args[0].id in roots):
            seg = node.args[1]
        elif (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
              and isinstance(node.left, ast.Name) and node.left.id in roots):
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

    patch = os.path.join(args.scripts, PATCH_SCRIPT)
    if os.path.exists(patch):
        allowed = patch_allowed(io.open(patch, encoding="utf-8").read())
        if not allowed:
            failures.append(f"{PATCH_SCRIPT} no longer states ALLOWED_DIRS and ALLOWED_FILES "
                            f"in a form this can read, so what a patch may touch is "
                            f"unchecked. A lane nothing bounds is the breach itself.")
        outside = allowed - CLONE_TREES
        if outside:
            failures.append(f"{PATCH_SCRIPT} would send a patch touching {sorted(outside)}, "
                            f"outside {sorted(CLONE_TREES - {'.git'})}. raw/ frontmatter "
                            f"travels as a script plus its input, and wiki prose is Phase B's.")

    for name in names:
        src = io.open(os.path.join(args.scripts, name), encoding="utf-8").read()
        for line, seg, literal in segments(src, CLONE_NAMES):
            if not literal:
                failures.append(f"{name}:{line} builds a work-clone path from '{seg}', which "
                                f"this cannot resolve. Use a literal — the clone is written "
                                f"to, so a segment nobody can read is a write nobody checked.")
            elif seg not in CLONE_TREES:
                failures.append(f"{name}:{line} builds '{seg}/' in the work clone, outside "
                                f"{sorted(CLONE_TREES)}. Corpus commits to OSINT's scripts, "
                                f"lookups and index pages, and to nothing else of OSINT's.")
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
