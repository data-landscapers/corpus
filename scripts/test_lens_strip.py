#!/usr/bin/env python3
r"""test_lens_strip.py — the strip removes one line and leaves every other byte.

    python scripts/test_lens_strip.py

`lens-strip.py` rewrites 15,372 of OSINT's immutable `raw/` records to delete one
frontmatter key (strategic review 4, R35). The failure that matters is not "it did not
remove the key" — that shows up immediately — it is "it removed the key **and** normalised
something", where a corpus-wide rewrite lands a second, unasked-for change in the same
commit and nobody sees it until a diff months later.

So most of these cases are about the bytes it must not touch: a CRLF record, a BOM, a file
with no trailing newline, UTF-8 accents and smart quotes. And the refusals, because none of
them occurs in the corpus as measured and they are therefore the part that has never been
exercised for real.
"""
from __future__ import annotations

import importlib.util
import io
import shutil
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "lens_strip", Path(__file__).resolve().parent / "lens-strip.py")
ls = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ls)

fails = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"       got  {got!r}\n       want {want!r}")
        fails.append(name)


# ---- the removal itself, on bytes -------------------------------------------

CASES = [
    ("a flow value goes, LF kept",
     b"---\ntype: source\nlens: [sovereignty]\nplaces: [KEN]\n---\n\nbody\n",
     b"---\ntype: source\nplaces: [KEN]\n---\n\nbody\n"),
    ("CRLF stays CRLF",
     b"---\r\ntype: source\r\nlens: []\r\nplaces: [KEN]\r\n---\r\n\r\nbody\r\n",
     b"---\r\ntype: source\r\nplaces: [KEN]\r\n---\r\n\r\nbody\r\n"),
    ("a BOM survives",
     b"\xef\xbb\xbf---\ntype: source\nlens: []\n---\n\nbody\n",
     b"\xef\xbb\xbf---\ntype: source\n---\n\nbody\n"),
    ("a file with no trailing newline keeps not having one",
     b"---\ntype: source\nlens: []\n---\n\nbody",
     b"---\ntype: source\n---\n\nbody"),
    ("non-ASCII elsewhere in the frontmatter is untouched",
     "---\ntitle: Développement — “quoted”\nlens: [a, b]\n---\n\ncorps\n".encode("utf-8"),
     "---\ntitle: Développement — “quoted”\n---\n\ncorps\n".encode("utf-8")),
    ("the key first in the block",
     b"---\nlens: []\ntype: source\n---\n\nbody\n",
     b"---\ntype: source\n---\n\nbody\n"),
    ("the key last in the block",
     b"---\ntype: source\nlens: []\n---\n\nbody\n",
     b"---\ntype: source\n---\n\nbody\n"),
    # An empty `lens:` whose next line is another key is a real empty value, not a block
    # opener, and must still go. This is where the block guard could over-refuse and
    # quietly leave part of the corpus alone.
    ("a bare `lens:` followed by another key still goes",
     b"---\ntype: source\nlens:\nplaces: [KEN]\n---\n\nbody\n",
     b"---\ntype: source\nplaces: [KEN]\n---\n\nbody\n"),
]

print("removing the key")
for name, before, after in CASES:
    got, _ = ls.strip_one(before)
    check(name, got, after)

REFUSE = [
    ("a block value is refused, not orphaned",
     b"---\ntype: source\nlens:\n  - sovereignty\n---\n\nbody\n",
     "the value is a block, not on the key's own line"),
    ("the key twice is refused",
     b"---\nlens: []\ntype: source\nlens: [x]\n---\n\nbody\n",
     "`lens:` appears 2 times"),
    ("frontmatter that never closes is refused",
     b"---\ntype: source\nlens: []\n\nbody\n",
     "frontmatter does not open and close"),
    ("a file with no frontmatter is refused",
     b"# Heading\n\nlens: [x] in the body\n",
     "frontmatter does not open and close"),
    ("`lens:` in the body only is not a hit",
     b"---\ntype: source\n---\n\nlens: [x]\n",
     "no `lens:` in the frontmatter"),
]

print("\nwhat it refuses")
for name, before, why in REFUSE:
    got, reason = ls.strip_one(before)
    check(name, (got, reason), (None, why))

# ---- the input list ---------------------------------------------------------

print("\nthe input list")
tmp = Path(tempfile.mkdtemp(prefix="lens-"))
try:
    lst = tmp / "list.txt"
    with io.open(lst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("raw/2026/a.md\n"
                 "\n"
                 "# a comment\n"
                 "raw\\2026\\b.md\n"          # a Windows spelling is the same path
                 "wiki/intersections/KEN.md\n"
                 "raw/../etc/passwd.md\n"
                 "lookups/taxonomy.csv\n")
    paths, bad = ls.listed(str(lst), str(tmp))
    check("only raw/ records are taken", paths, ["raw/2026/a.md", "raw/2026/b.md"])
    check("everything else is refused by name", bad,
          ["wiki/intersections/KEN.md", "raw/../etc/passwd.md", "lookups/taxonomy.csv"])

    # ---- end to end, through main() -----------------------------------------
    print("\nend to end")
    CARRIES = b"---\ntype: source\nlens: []\n---\n\nbody\n"
    STRIPPED = b"---\ntype: source\n---\n\nbody\n"
    UNTOUCHED = b"---\ntype: source\nplaces: [KEN]\n---\n\nbody\n"
    BLOCK = b"---\ntype: source\nlens:\n  - x\n---\n\nbody\n"

    root = tmp / "repo"
    raw = root / "raw" / "2026"
    raw.mkdir(parents=True)
    (raw / "keep.md").write_bytes(UNTOUCHED)
    (raw / "go.md").write_bytes(CARRIES)
    (raw / "bad.md").write_bytes(BLOCK)
    lst2 = tmp / "l2.txt"
    lst2.write_text("raw/2026/go.md\nraw/2026/bad.md\n", encoding="utf-8")

    def run(*argv):
        """main() with its output captured, so a case can assert on what it said."""
        out = io.StringIO()
        keep, sys.stdout = sys.stdout, out
        try:
            return ls.main(list(argv)), out.getvalue()
        finally:
            sys.stdout = keep

    rc, _ = run("--root", str(root), "--list", str(lst2))
    check("a dry run writes nothing", (raw / "go.md").read_bytes(), CARRIES)
    check("a refusal exits 1", rc, 1)

    run("--root", str(root), "--list", str(lst2), "--write")
    check("--write strips the good one", (raw / "go.md").read_bytes(), STRIPPED)
    check("--write leaves the refused one alone", (raw / "bad.md").read_bytes(), BLOCK)
    check("a record that never carried the key is untouched",
          (raw / "keep.md").read_bytes(), UNTOUCHED)

    # The second run is what reads badly if nothing is done about it: every listed path is
    # missing the key *because this removed it*, and that is not drift.
    rc2, text = run("--root", str(root), "--list", str(lst2))
    check("a second run counts the stripped rather than listing them",
          "1 listed record(s) no longer carry the key" in text, True)
    check("a second run does not call them drift", "not in the tree" in text, False)
    # `bad.md` still carries the key and is refused again, so the run is not clean.
    check("a second run still exits 1 while a refusal stands", rc2, 1)

    # A listed path that has left the tree is drift, and a different finding.
    (raw / "go.md").unlink()
    rc3, text = run("--root", str(root), "--list", str(lst2))
    check("a listed path missing from the tree is reported",
          "on the list, not in the tree  raw/2026/go.md" in text, True)
    check("and it fails the run", rc3, 1)
    (raw / "go.md").write_bytes(STRIPPED)

    # A record carrying the key that the list does not name is the finding that matters:
    # nothing has written this key since 2026-09-08, so a new carrier means something has.
    (raw / "new.md").write_bytes(CARRIES)
    rc4, text = run("--root", str(root), "--list", str(lst2))
    check("an unlisted carrier is reported",
          "carries the key, not on the list  raw/2026/new.md" in text, True)
    check("and it fails the run", rc4, 1)
    check("and it is not stripped", (raw / "new.md").read_bytes(), CARRIES)
    (raw / "new.md").unlink()

    # Nothing left carrying the key, and every listed path still in the tree: the job is
    # done and the run is clean. `bad.md` leaves the list with it — a path named by the
    # input and absent from the tree stays drift, which the case above covers.
    (raw / "bad.md").unlink()
    lst2.write_text("raw/2026/go.md\n", encoding="utf-8")
    rc5, text = run("--root", str(root), "--list", str(lst2))
    check("with nothing left carrying the key it exits 0", rc5, 0)
    check("and says so rather than reporting nothing",
          "1 listed record(s) no longer carry the key" in text, True)

    check("a missing root exits 2",
          ls.main(["--root", str(tmp / "nope"), "--list", str(lst2)]), 2)
    check("a missing list exits 2",
          ls.main(["--root", str(root), "--list", str(tmp / "nope.txt")]), 2)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
print("all cases pass" if not fails else f"{len(fails)} of the cases FAILED")
sys.exit(1 if fails else 0)
