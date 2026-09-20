#!/usr/bin/env python3
r"""test_lens_strip_20b.py — the scope is two kinds of root, and one of them has no list.

    python scripts/test_lens_strip_20b.py

`lens-strip-20b.py` finishes what R35 started: the 1,696 files outside `raw/` that still
carry the retired `lens:` key (strategic review 4, R49). The removal itself is R35's, line
for line, and `test_lens_strip.py` already covers it — so this pins the part that is new.

**What is new is that Corpus may not read three of the four roots.** `budget-archive/`,
`new-budget/` and `scratchpad/` are outside the interface, so no list of their paths could
be cut here and the script walks them against a count OSINT published itself. A count that
disagrees means the tree is not what the input describes, and with no list there is
nothing to say *which* files the difference is in — so the root is skipped rather than
stripped. That rule is the whole safety of the counted mode and most of these cases are
about it: the count matching, the count short, the count long, and the count at zero
because the job has already been done.

The rest is the boundary between the two modes: a listed root still behaves exactly as
20a, `raw/` is refused by name in both the scope and the input, and the two scripts' copy
of the removal is checked to still be the same bytes.
"""
from __future__ import annotations

import importlib.util
import inspect
import io
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ls = load("lens_strip_20b", "lens-strip-20b.py")
a20 = load("lens_strip", "lens-strip.py")

fails = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"       got  {got!r}\n       want {want!r}")
        fails.append(name)


# ---- the removal is R35's, and stays R35's ----------------------------------
#
# The two scripts carry their own copy of the removal because each has to run standalone
# on OSINT's machine with nothing beside it. A copy is not sharing unless something
# notices when it goes stale, so this is what notices.

print("the removal is the same code in both scripts")
for fn in ("frontmatter", "strip_one"):
    check(f"{fn}() matches lens-strip.py",
          inspect.getsource(getattr(ls, fn)), inspect.getsource(getattr(a20, fn)))
check("KEY_RE matches", ls.KEY_RE.pattern, a20.KEY_RE.pattern)
check("CONT_RE matches", ls.CONT_RE.pattern, a20.CONT_RE.pattern)

# A handful of the 20a cases run again here, so a divergence that somehow passed the
# source comparison above still fails on behaviour.
print("\nand behaves the same on the bytes that matter")
check("CRLF stays CRLF",
      ls.strip_one(b"---\r\ntype: source\r\nlens: []\r\n---\r\n\r\nbody\r\n")[0],
      b"---\r\ntype: source\r\n---\r\n\r\nbody\r\n")
check("a BOM survives",
      ls.strip_one(b"\xef\xbb\xbf---\nlens: []\ntype: source\n---\n\nbody\n")[0],
      b"\xef\xbb\xbf---\ntype: source\n---\n\nbody\n")
check("a block value is still refused",
      ls.strip_one(b"---\nlens:\n  - sovereignty\n---\n\nbody\n"),
      (None, "the value is a block, not on the key's own line"))

# ---- the scope file ---------------------------------------------------------

CARRIES = b"---\ntype: page\nlens: []\n---\n\nbody\n"
STRIPPED = b"---\ntype: page\n---\n\nbody\n"
UNTOUCHED = b"---\ntype: page\nplaces: [KEN]\n---\n\nbody\n"
BLOCK = b"---\ntype: page\nlens:\n  - x\n---\n\nbody\n"

tmp = Path(tempfile.mkdtemp(prefix="lens20b-"))
try:
    print("\nthe scope file")
    scope = tmp / "roots.csv"
    scope.write_text(
        "root,mode,expected,source\n"
        "wiki,listed,2,corpus\n"
        "budget-archive,counted,2,osint\n"
        "raw,counted,15372,osint\n"              # 20a's, and finished
        "outputs/catalogue,listed,1,corpus\n"    # not a top-level directory
        "new-budget,sampled,3,osint\n"           # not a mode
        "scratchpad,counted,,osint\n",           # no count is not a count
        encoding="utf-8")
    rows, bad = ls.read_roots(str(scope))
    check("only the well-formed roots are taken",
          [(r, m, n) for r, m, n, _ in rows],
          [("wiki", "listed", 2), ("budget-archive", "counted", 2)])
    check("`raw/` is refused by name", any("task 20a's" in w for w in bad), True)
    check("a nested root is refused", any("single top-level" in w for w in bad), True)
    check("an unknown mode is refused", any("not listed or counted" in w for w in bad), True)
    check("a missing count is refused", any("no expected count" in w for w in bad), True)

    print("\nthe input list")
    lst = tmp / "list.txt"
    with io.open(lst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("wiki/intersections/a.md\n"
                 "\n"
                 "# a comment\n"
                 "wiki\\intersections\\b.md\n"      # a Windows spelling is the same path
                 "raw/2026/c.md\n"                  # 20a's root
                 "budget-archive/d.md\n"            # a counted root has no list
                 "wiki/../etc/passwd.md\n"
                 "lookups/taxonomy.csv\n")
    paths, bad = ls.read_list(str(lst), {"wiki"})
    check("only paths under a listed root are taken", paths,
          ["wiki/intersections/a.md", "wiki/intersections/b.md"])
    check("everything else is refused by name", bad,
          ["raw/2026/c.md", "budget-archive/d.md", "wiki/../etc/passwd.md",
           "lookups/taxonomy.csv"])

    # ---- end to end ---------------------------------------------------------

    print("\nend to end, two listed and two counted")
    root = tmp / "repo"
    wiki = root / "wiki" / "intersections"
    wiki.mkdir(parents=True)
    (wiki / "go.md").write_bytes(CARRIES)
    (wiki / "keep.md").write_bytes(UNTOUCHED)
    ba = root / "budget-archive" / "KEN"
    ba.mkdir(parents=True)
    (ba / "one.md").write_bytes(CARRIES)
    (ba / "two.md").write_bytes(CARRIES)
    (ba / "plain.md").write_bytes(UNTOUCHED)
    nb = root / "new-budget"
    nb.mkdir(parents=True)
    (nb / "three.md").write_bytes(CARRIES)

    scope2 = tmp / "roots2.csv"
    scope2.write_text("root,mode,expected,source\n"
                      "wiki,listed,1,corpus\n"
                      "budget-archive,counted,2,osint\n"
                      "new-budget,counted,1,osint\n", encoding="utf-8")
    lst2 = tmp / "l2.txt"
    lst2.write_text("wiki/intersections/go.md\n", encoding="utf-8")

    def run(*argv):
        """main() with its output captured, so a case can assert on what it said."""
        out = io.StringIO()
        keep, sys.stdout = sys.stdout, out
        try:
            return ls.main(list(argv)), out.getvalue()
        finally:
            sys.stdout = keep

    base = ["--root", str(root), "--roots", str(scope2), "--list", str(lst2)]

    rc, text = run(*base)
    check("a clean dry run exits 0", rc, 0)
    check("and writes nothing", (ba / "one.md").read_bytes(), CARRIES)
    check("and says it would strip all four", "dry run: 4 would be stripped" in text, True)

    run(*base, "--write")
    check("--write strips the listed root", (wiki / "go.md").read_bytes(), STRIPPED)
    check("--write strips a counted root", (ba / "one.md").read_bytes(), STRIPPED)
    check("--write reaches every counted root", (nb / "three.md").read_bytes(), STRIPPED)
    check("a file that never carried the key is untouched",
          (wiki / "keep.md").read_bytes(), UNTOUCHED)
    check("and so is one in a counted root", (ba / "plain.md").read_bytes(), UNTOUCHED)

    # The re-run is the case that reads badly if nothing is done about it: every listed
    # path and every counted root is now empty *because this emptied them*.
    rc2, text = run(*base)
    check("a second run exits 0", rc2, 0)
    check("a listed root counts the stripped rather than listing them",
          "1 listed file(s) no longer carry the key" in text, True)
    check("a counted root says the job is already done",
          text.count("already stripped") == 3, True)

    print("\ncounted roots: the count is the whole of the check")
    (ba / "one.md").write_bytes(CARRIES)          # one of two back: short of the count
    rc3, text = run(*base)
    check("a count short of the input is reported",
          "expected 2 file(s) carrying the key, found 1" in text, True)
    check("and the root is skipped, not stripped", "skipped, not stripped" in text, True)
    check("and nothing in it is touched", (ba / "one.md").read_bytes(), CARRIES)
    check("and the run is not clean", rc3, 1)

    (ba / "two.md").write_bytes(CARRIES)
    (ba / "three.md").write_bytes(CARRIES)        # three of two: something wrote the key
    rc4, text = run(*base)
    check("a count over the input is reported the same way",
          "expected 2 file(s) carrying the key, found 3" in text, True)
    check("and still strips nothing there", (ba / "three.md").read_bytes(), CARRIES)
    check("and the run is not clean", rc4, 1)
    (ba / "three.md").unlink()

    print("\nlisted roots keep 20a's findings")
    (wiki / "new.md").write_bytes(CARRIES)        # a carrier the list does not name
    rc5, text = run(*base)
    check("an unlisted carrier is reported",
          "carries the key, not on the list  wiki/intersections/new.md" in text, True)
    check("and it fails the run", rc5, 1)
    check("and it is not stripped", (wiki / "new.md").read_bytes(), CARRIES)
    (wiki / "new.md").unlink()

    (wiki / "go.md").unlink()                     # a listed path that has left the tree
    rc6, text = run(*base)
    check("a listed path missing from the tree is reported",
          "on the list, not in the tree  wiki/intersections/go.md" in text, True)
    check("and it fails the run", rc6, 1)
    (wiki / "go.md").write_bytes(STRIPPED)

    print("\n--only, refusals and the exit codes")
    rc7, text = run(*base, "--only", "budget-archive")
    check("--only runs one root", [l.split()[0] for l in text.splitlines()
                                   if l.endswith(("listed", "counted")) or "expect" in l
                                   or "input" in l], ["budget-archive/"])
    # The listed roots come from the whole scope, so narrowing the run does not turn
    # `wiki/`'s paths into refusals and report a scope problem that is not there.
    check("and does not refuse the other root's input",
          "not under a listed root" in text, False)
    check("and the root it did run is clean", rc7, 0)
    check("--only naming nothing in the scope exits 2",
          run(*base, "--only", "logs")[0], 2)

    (ba / "one.md").write_bytes(BLOCK)
    (ba / "two.md").write_bytes(CARRIES)
    rc8, text = run(*base, "--only", "budget-archive")
    check("a refusal inside a counted root is named",
          "the value is a block, not on the key's own line" in text, True)
    check("and it fails the run", rc8, 1)
    run(*base, "--only", "budget-archive", "--write")
    check("and the refused file is left alone", (ba / "one.md").read_bytes(), BLOCK)
    check("while its neighbour goes", (ba / "two.md").read_bytes(), STRIPPED)

    check("a root in the scope that is not in the tree exits 2",
          ls.main(["--root", str(tmp / "nope"), "--roots", str(scope2),
                   "--list", str(lst2)]), 2)
    check("a missing scope file exits 2",
          ls.main(["--root", str(root), "--roots", str(tmp / "nope.csv"),
                   "--list", str(lst2)]), 2)
    check("a missing input list exits 2",
          ls.main(["--root", str(root), "--roots", str(scope2),
                   "--list", str(tmp / "nope.txt")]), 2)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
print("all cases pass" if not fails else f"{len(fails)} of the cases FAILED")
sys.exit(1 if fails else 0)
