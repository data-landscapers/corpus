#!/usr/bin/env python3
r"""test_duplicate_briefs.py — the two numbers, the clustering, and what is left out.

    python scripts/test_duplicate_briefs.py

`duplicate-briefs.py` hands OSINT a read-and-judge queue (housekeeping job 107). Four
things in it can be wrong without looking wrong:

- **The two similarity numbers**, because they are what the call is made on. Jaccard alone
  cannot tell an excerpt of a document from a different document, and containment alone
  reads 1.0 whenever one side is short. Each is checked on the case the other gets wrong.
- **The clustering.** A cluster of four is six pairs, which is how job 107's *"six-pair São
  Tomé DGRN cluster"* is four records; and a seven-day window must not re-report a cluster
  the exact grouping already found, or the AU trio arrives twice.
- **What is left out.** Finance records share a title legitimately — one donor programme
  across seven recipients — and a queue that swallows them loses the real hits among them.
- **The scaffold strip.** A capture's own `# heading` and `URL:` lines are the fetch's,
  not the publisher's; left in, they inflate the similarity of any two captures of
  anything and flatten the one number that separates the shapes.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "duplicate_briefs", Path(__file__).resolve().parent / "duplicate-briefs.py")
db = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(db)

fails = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"        got  {got!r}\n        want {want!r}")
        fails.append(name)


def build(tmp, records):
    """A tree and an index over it. `records` maps a path to (frontmatter, body)."""
    root = Path(tmp)
    rows = []
    for rel, (fm, body) in records.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        front = "\n".join("%s: %s" % (k, v) for k, v in fm.items())
        p.write_text("---\n%s\n---\n\n%s\n" % (front, body), encoding="utf-8")
        rows.append({"path": rel, "d": {"ext": ".md", "slug": Path(rel).stem}, "fm": fm})
    index = root / "index"
    index.mkdir(exist_ok=True)
    with open(index / "files.jsonl", "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    (index / "links.jsonl").write_text("", encoding="utf-8")
    return root


# **Not a repeated phrase.** A body built by repetition has almost no distinct shingles,
# so a short slice of it covers the whole set and every similarity number reads 1.0 —
# which is a property of the fixture, not of the code being tested.
LOREM = " ".join("section %d of the notice concerns register entry %d and the document "
                 "issued under it" % (i, i * 7) for i in range(120))
OTHER = " ".join("clause %d covers cable landing station %d and the licence granted to "
                 "its operator" % (i, i * 3) for i in range(120))


# -- the two numbers -------------------------------------------------------

print("jaccard and containment")
check("the same text: both 1.0",
      tuple(round(x, 2) for x in db.overlap(LOREM, LOREM)), (1.0, 1.0))
jac, con = db.overlap(" ".join(LOREM.split()[:60]), LOREM)
check("an excerpt inside a long document: low jaccard", jac < 0.2, True)
check("  …and containment near 1.0 — this is the *replace* call", con > 0.9, True)
jac, con = db.overlap(LOREM, OTHER)
check("two different texts: low on both", (jac < 0.05, con < 0.05), (True, True))
check("an empty side scores zero rather than raising", db.overlap("", LOREM), (0.0, 0.0))


# -- the scaffold ----------------------------------------------------------

print("\nthe capture's own header lines")
with tempfile.TemporaryDirectory() as tmp:
    root = build(tmp, {
        "raw/2026/a.md": ({"title": "T", "published": "2026-01-01"},
                          "# Publisher | T\nURL: https://example.org/a\nAuthor: Someone\n\n"
                          "the body proper starts here"),
    })
    check("heading, URL and author lines are dropped",
          db.body_of(str(root), "raw/2026/a.md"), "the body proper starts here")


# -- the clustering --------------------------------------------------------

print("\nclusters, pairs, and the seven-day window")
with tempfile.TemporaryDirectory() as tmp:
    recs = {}
    # A cluster of four on one date: six pairs, and it is how job 107's "six-pair
    # cluster" is four records.
    for i in range(4):
        recs["raw/2026/quad-%d.md" % i] = (
            {"title": "DGRN - one site title for four pages", "published": "2026-01-01"},
            "page %d about a wholly different service of the same agency" % i)
    # Two records a day apart: outside the exact set, inside the window.
    recs["raw/2025/au-a.md"] = ({"title": "AU validation workshop",
                                 "published": "2025-12-01"}, LOREM)
    recs["raw/2025/au-b.md"] = ({"title": "AU validation workshop",
                                 "published": "2025-12-02"}, LOREM)
    # A finance pair: one programme title, two recipient countries, not a duplicate.
    for iso in ("ken", "mwi"):
        recs["raw/2026/prog-%s.md" % iso] = (
            {"title": "Capacity Building for Government Officials",
             "published": "2026-01-01", "deal_id": "iati-%s" % iso}, LOREM)
    root = build(tmp, recs)
    index = str(root / "index")

    exact = db.rows(str(root), index, "raw", near_days=0)
    check("a cluster of four is six pairs", len(exact), 6)
    check("the finance pair is not in the queue",
          any("prog-" in p["a"]["slug"] for p in exact), False)
    check("nor is the day-apart pair", any("au-" in p["a"]["slug"] for p in exact), False)

    near = db.rows(str(root), index, "raw", near_days=7)
    check("the window adds the day-apart pair and nothing else", len(near), 7)
    check("and flags it rather than merging it",
          [p["near"] for p in near], [False] * 6 + [True])
    check("the near cluster carries its date range",
          [p["key"][1] for p in near if p["near"]], ["2025-12-01 … 2025-12-02"])
    check("a cluster the exact grouping already found is not re-reported",
          sum(1 for p in near if "quad" in p["a"]["slug"]), 6)

    keep = db.rows(str(root), index, "raw", keep_finance=True, near_days=0)
    check("--all puts the finance pair back", len(keep), 7)


# -- already ruled ---------------------------------------------------------

print("\na pair the hub line already links")
with tempfile.TemporaryDirectory() as tmp:
    root = build(tmp, {
        "raw/2026/primary.md": ({"title": "One headline", "published": "2026-08-03",
                                 "hub_line_sources": ["syndicated"]}, LOREM),
        "raw/2026/syndicated.md": ({"title": "One headline", "published": "2026-08-03"},
                                   LOREM),
    })
    got = db.rows(str(root), str(root / "index"), "raw")
    check("the link is seen in either direction", [p["hub_linked"] for p in got], [True])

print()
if fails:
    print("%d FAILED: %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("all checks passed")
