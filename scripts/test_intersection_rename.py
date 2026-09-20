#!/usr/bin/env python3
r"""test_intersection_rename.py — the link moves with the page, and nothing else moves.

    python scripts/test_intersection_rename.py

`intersection-rename.py` renames pages in OSINT's wiki and rewrites links across the whole
tree (housekeeping job 96). What can go wrong quietly:

- **A prefix match that is not a link.** `[[com--dpi-id]]` must move and
  `[[comoros--dpi-id]]` must not, though one slug is a prefix of the other's file name.
  The same holds inside a labelled link.
- **A substitution that takes a neighbouring character with it.** Every changed line is
  reverted and compared, and a file that does not revert exactly is refused rather than
  written.
- **A rename onto an existing page.** That is a silent overwrite, so it stops the run.
- **Links before renames.** A rename that lands first leaves the tree full of dangling
  pointers for as long as the sweep takes, and for ever if it fails halfway.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "intersection_rename", Path(__file__).resolve().parent / "intersection-rename.py")
ir = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ir)

fails = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"        got  {got!r}\n        want {want!r}")
        fails.append(name)


MAP_CSV = ("place,current_prefix,proposed_prefix\n"
           "COM,com,comoros\n"
           "COM,comoros,comoros\n"
           "AGO,angola,angola\n")


def build(tmp, pages, extra=None):
    root = Path(tmp)
    (root / "wiki" / "intersections").mkdir(parents=True)
    (root / "raw" / "2026").mkdir(parents=True)
    for slug, body in pages.items():
        (root / "wiki" / "intersections" / (slug + ".md")).write_text(
            "---\ntype: intersection\nplace: COM\n---\n\n" + body, encoding="utf-8")
    for rel, text in (extra or {}).items():
        (root / rel).write_text(text, encoding="utf-8")
    (root / "map.csv").write_text(MAP_CSV, encoding="utf-8")
    return root


# -- what a link is --------------------------------------------------------

print("what counts as a link to the page being renamed")
pairs = [("com--dpi-id", "comoros--dpi-id")]
for label, text, want in (
        ("a bare wikilink", "see [[com--dpi-id]] here", "see [[comoros--dpi-id]] here"),
        ("a labelled wikilink", "see [[com--dpi-id|the page]]",
         "see [[comoros--dpi-id|the page]]"),
        ("twice on one line", "[[com--dpi-id]] and [[com--dpi-id]]",
         "[[comoros--dpi-id]] and [[comoros--dpi-id]]"),
):
    check(label, ir.rewrite(text, pairs)[0], want)

for label, text in (
        ("a longer slug that starts the same", "see [[com--dpi-id-extra]]"),
        ("the slug in prose, not in a link", "the com--dpi-id page"),
        ("a page that already carries the new slug", "see [[comoros--dpi-id]]"),
):
    check(label + " is left alone", ir.rewrite(text, pairs)[0], text)

new, hits, why = ir.rewrite("[[com--dpi-id]] and [[com--dpi-pay]]",
                            [("com--dpi-id", "comoros--dpi-id"),
                             ("com--dpi-pay", "comoros--dpi-pay")])
check("hits are counted per slug", dict(hits),
      {"com--dpi-id": 1, "com--dpi-pay": 1})
check("and nothing is refused", why, None)


# -- the whole run ---------------------------------------------------------

print("\nthe sweep, the rename, and the order they happen in")
with tempfile.TemporaryDirectory() as tmp:
    root = build(tmp, {
        "com--dpi-id": "# Comoros x Digital ID\n\nsee [[com--dpi-pay]] and [[angola--dpi-id]]\n",
        "com--dpi-pay": "# Comoros x Payments\n\nnothing links out\n",
        "comoros--tech-ai": "# Comoros x AI\n\nalready named the long way\n",
        "angola--dpi-id": "# Angola\n\nsee [[com--dpi-id|the Comoros page]]\r\n",
    }, {"raw/2026/a-source.md": "---\ntitle: x\n---\n\ncites [[com--dpi-id]]\n"})

    code = ir.main(["--root", str(root), "--map", str(root / "map.csv")])
    check("a dry run changes nothing", code, 0)
    check("  …and the page is still where it was",
          (root / "wiki" / "intersections" / "com--dpi-id.md").exists(), True)

    code = ir.main(["--root", str(root), "--map", str(root / "map.csv"), "--write"])
    check("the write succeeds", code, 0)
    check("the page moved",
          [(root / "wiki" / "intersections" / n).exists()
           for n in ("com--dpi-id.md", "comoros--dpi-id.md")], [False, True])
    check("a page already named the long way is untouched",
          (root / "wiki" / "intersections" / "comoros--tech-ai.md").exists(), True)
    check("a link from another wiki page moved",
          "[[comoros--dpi-id|the Comoros page]]" in
          (root / "wiki" / "intersections" / "angola--dpi-id.md").read_text(encoding="utf-8"),
          True)
    check("  …and its CRLF line ending survived",
          b"\r\n" in (root / "wiki" / "intersections" / "angola--dpi-id.md").read_bytes(),
          True)
    check("a link from raw/ moved",
          "[[comoros--dpi-id]]" in
          (root / "raw" / "2026" / "a-source.md").read_text(encoding="utf-8"), True)
    check("a link inside a renamed page moved too",
          "[[comoros--dpi-pay]]" in
          (root / "wiki" / "intersections" / "comoros--dpi-id.md").read_text(encoding="utf-8"),
          True)
    check("a second run has nothing left to do",
          ir.main(["--root", str(root), "--map", str(root / "map.csv")]), 0)


# -- the refusals ----------------------------------------------------------

print("\nwhat stops a write")
with tempfile.TemporaryDirectory() as tmp:
    root = build(tmp, {"com--dpi-id": "x\n", "comoros--dpi-id": "the target already exists\n"})
    check("a rename onto an existing page stops the run",
          ir.main(["--root", str(root), "--map", str(root / "map.csv"), "--write"]), 1)
    check("  …and nothing was overwritten",
          (root / "wiki" / "intersections" / "comoros--dpi-id.md")
          .read_text(encoding="utf-8").endswith("the target already exists\n"), True)

print("\nthe map")
with tempfile.TemporaryDirectory() as tmp:
    root = build(tmp, {"com--dpi-id": "x\n"})
    check("rows that do not move are skipped",
          ir.read_map(str(root / "map.csv")), {"COM": [("com", "comoros")]})
    check("--places narrows it",
          ir.read_map(str(root / "map.csv"), {"AGO"}), {})

print()
if fails:
    print("%d FAILED: %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("all checks passed")
