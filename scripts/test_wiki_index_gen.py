#!/usr/bin/env python3
r"""test_wiki_index_gen.py — the block is a function of the tree, and nothing else moves.

    python scripts/test_wiki_index_gen.py

`wiki-index-gen.py` writes into two hand-maintained pages in OSINT's wiki (housekeeping
jobs 89 and 117), so what has to hold is narrow and absolute:

- **Nothing outside the markers moves.** The pages carry hundreds of curated glosses that
  no generator can reproduce. A run that reflowed one of them would be found weeks later
  and blamed on anything.
- **The block is a pure function of `wiki/intersections/`.** Two runs over one tree produce
  the same bytes, in the same order, whatever order the filesystem hands the files back —
  otherwise `--check` fires on noise and gets switched off.
- **Splicing is idempotent.** Append once, replace thereafter; a second run is a no-op.
- **It refuses a page it cannot file.** A page with no `place:` or `topic:` is the exact
  case the job exists to stop losing, so it stops the run rather than being skipped.
- **The three shapes differ in the way the ruling turns on.** `inline` names every page,
  `gaps` names only what nothing else names, `bullets` is one pointer a line.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "wiki_index_gen", Path(__file__).resolve().parent / "wiki-index-gen.py")
w = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w)

fails = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"        got  {got!r}\n        want {want!r}")
        fails.append(name)


TAXONOMY = """# Subject taxonomy

## Rules

- nothing here matters to the parser

## Vocabulary

### ICT Infrastructure
- `infra.connect` — Connectivity
- `infra.store` — Data Storage

### Governance
- `gov.policy` — Strategies, plans and policies
"""

COUNTRIES = "iso-3,country-name,Region\nAGO,Angola,XSA\nBEN,Benin,XWA\nXWA,West Africa,XAF\n"

PAGES = {
    # Deliberately created in an order that is neither the taxonomy's nor the code's, so
    # a run that leaned on `os.listdir` order would produce different bytes here.
    "benin--gov-policy": ("BEN", "gov.policy"),
    "angola--infra-store": ("AGO", "infra.store"),
    "xwa--infra-connect": ("XWA", "infra.connect"),
    "angola--infra-connect": ("AGO", "infra.connect"),
    "benin--infra-connect": ("BEN", "infra.connect"),
}

PLACES_INDEX = ("# Places index\n\nCurated prose that must not move.\n\n"
                "| Code | Country | Lead topics |\n|---|---|---|\n"
                "| AGO | Angola | infra.store (a gloss worth keeping) "
                "(+ [[angola--infra-store]]) |\n")
TOPICS_INDEX = "# Topics index\n\n- [[infra.connect]] — Connectivity\n"


def build_tree(tmp, pages=PAGES, extra=None):
    root = Path(tmp)
    (root / "wiki" / "intersections").mkdir(parents=True)
    (root / "lookups").mkdir()
    (root / "lookups" / "taxonomy.md").write_text(TAXONOMY, encoding="utf-8")
    (root / "lookups" / "countries.csv").write_text(COUNTRIES, encoding="utf-8")
    (root / "wiki" / "places-index.md").write_text(PLACES_INDEX, encoding="utf-8")
    (root / "wiki" / "topics-index.md").write_text(TOPICS_INDEX, encoding="utf-8")
    for slug, (place, topic) in pages.items():
        fm = "---\ntype: intersection\ntitle: %s\n" % slug
        if place:
            fm += "place: %s\n" % place
        if topic:
            fm += "topic: %s\n" % topic
        fm += "---\n\n# %s\n" % slug
        (root / "wiki" / "intersections" / (slug + ".md")).write_text(fm, encoding="utf-8")
    for rel, text in (extra or {}).items():
        (root / rel).write_text(text, encoding="utf-8")
    return root


# -- the block -------------------------------------------------------------

print("the block is a function of the tree")
with tempfile.TemporaryDirectory() as tmp:
    root = build_tree(tmp)
    rows, unfiled, blocks, overlap = w.build(str(root), "inline")
    check("every page is read", len(rows), 5)
    check("none is unfiled", unfiled, [])
    places = blocks["wiki/places-index.md"]
    topics = blocks["wiki/topics-index.md"]

    check("a place line is ordered by the taxonomy, not the filesystem",
          next(ln for ln in places.split("\n") if ln.startswith("- **AGO**")),
          "- **AGO** Angola — [[angola--infra-connect|infra.connect]], "
          "[[angola--infra-store|infra.store]]")
    check("a topic line is ordered by place code",
          next(ln for ln in topics.split("\n") if ln.startswith("- **infra.connect**")),
          "- **infra.connect** Connectivity — [[angola--infra-connect|AGO]], "
          "[[benin--infra-connect|BEN]], [[xwa--infra-connect|XWA]]")
    check("regions are listed apart from countries",
          places.index("**Regions**") < places.index("**Countries**"), True)
    check("  …and the region is in the regions half",
          places.split("**Countries**")[0].count("- **XWA**"), 1)
    check("topics are grouped by their Level-1 parent",
          [ln for ln in topics.split("\n") if ln.startswith("### ")],
          ["### ICT Infrastructure", "### Governance"])
    check("the run is repeatable byte for byte",
          w.build(str(root), "inline")[2], blocks)
    check("the existing curated pointer is reported as also named outside the block",
          overlap["wiki/places-index.md"], ["angola--infra-store"])


# -- the shapes ------------------------------------------------------------

print("\nthe three shapes")
with tempfile.TemporaryDirectory() as tmp:
    root = build_tree(tmp)
    inline = w.build(str(root), "inline")[2]["wiki/places-index.md"]
    gaps = w.build(str(root), "gaps")[2]["wiki/places-index.md"]
    bullets = w.build(str(root), "bullets")[2]["wiki/places-index.md"]
    check("inline names every page", inline.count("[["), 5)
    check("gaps leaves out the one the prose already names", gaps.count("[["), 4)
    check("  …and it is that one", "angola--infra-store" in gaps, False)
    check("bullets is one pointer a line",
          sum(1 for ln in bullets.split("\n") if ln.startswith("    - [[")), 5)


# -- splicing --------------------------------------------------------------

print("\nsplicing, and what it must not touch")
with tempfile.TemporaryDirectory() as tmp:
    root = build_tree(tmp)
    path = root / "wiki" / "places-index.md"
    before = path.read_text(encoding="utf-8")
    block = w.build(str(root), "inline")[2]["wiki/places-index.md"]

    once, action = w.splice(before, block)
    check("the first run appends", action, "appended")
    check("nothing outside the markers moved", w.verify(before, once, "x"), None)
    check("the curated cell survives",
          "infra.store (a gloss worth keeping)" in once, True)

    twice, action = w.splice(once, block)
    check("the second run replaces rather than appends", action, "replaced")
    check("and is a no-op", twice, once)

    stale = once.replace("[[angola--infra-store|infra.store]]", "[[gone]]")
    fresh, _ = w.splice(stale, block)
    check("a stale block is brought back", fresh, once)

    tampered = once.replace("Curated prose that must not move.", "edited")
    check("a change outside the block is caught",
          (w.verify(tampered, once, "x") or "").endswith(
              "line 3 outside the block changed: 'edited' -> "
              "'Curated prose that must not move.'"), True)


# -- the refusal -----------------------------------------------------------

print("\na page it cannot file")
with tempfile.TemporaryDirectory() as tmp:
    pages = dict(PAGES)
    pages["orphan--nothing"] = ("", "")
    root = build_tree(tmp, pages)
    rows, unfiled, _, _ = w.build(str(root), "inline")
    check("it is reported, not skipped", unfiled, ["orphan--nothing"])
    check("and the run stops",
          w.main(["--root", str(root), "--check"]), 1)

print()
if fails:
    print("%d FAILED: %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("all checks passed")
