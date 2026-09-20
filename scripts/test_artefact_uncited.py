#!/usr/bin/env python3
r"""test_artefact_uncited.py — the parse, the boundary, and which shape a row lands in.

    python scripts/test_artefact_uncited.py

`artefact-uncited.py` hands OSINT a queue (housekeeping jobs 108 and 109), and every part
of it can be wrong quietly:

- **The `artefact:` parse.** The key takes a bare name, a flow list and a block list, and
  filenames contain commas. A parser that reads only the bare form reports every
  multi-artefact record's holdings as orphans — that is not hypothetical: `lookups/
  artefact-md5-index.csv`, built on 2026-09-20, marks 95 declared files `(none)` for
  exactly that reason, and this script's first duty is not to repeat it.
- **The name scan's boundary.** A filename is a suffix of a longer filename more often
  than it looks. Without a boundary test, a page naming `market-brief.pdf` marks
  `brief.pdf` as referenced and an orphan disappears from the queue.
- **The shape.** It is the disposition, so a row in the wrong one is either a judgement
  call sent out as a mechanical fix or 126 mechanical fixes sent out as judgement calls.
  The ordering between sidecar, same-directory, other-shard and wiki-only is the part
  with no obvious right answer, so all four are pinned here.
- **The inverse direction.** Its value is the diagnosis, not the count: a path-form
  declaration, a file under another shard, and a file that is nowhere are three different
  repairs and the row has to say which.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "artefact_uncited", Path(__file__).resolve().parent / "artefact-uncited.py")
au = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(au)

fails = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"        got  {got!r}\n        want {want!r}")
        fails.append(name)


def build(tmp, files, fm):
    """A tree and an index over it. `files` maps a repo-relative path to its bytes;
    `fm` maps a record path to the frontmatter the index would carry for it."""
    root = Path(tmp)
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    index = root / "index"
    index.mkdir(exist_ok=True)
    with open(index / "files.jsonl", "w", encoding="utf-8") as fh:
        for rel in files:
            ext = Path(rel).suffix.lower()
            row = {"path": rel, "d": {"ext": ext, "slug": Path(rel).stem},
                   "fm": fm.get(rel) if ext == ".md" else None}
            fh.write(json.dumps(row) + "\n")
    (index / "links.jsonl").write_text("", encoding="utf-8")
    return root


# -- the parse -------------------------------------------------------------
# A record holding three files declares three files. The flow list is the form that
# defeated the index in `lookups/`, and it is the form the vault uses for annexes.

print("the artefact: key, in all three forms")
rows = {
    "raw/2021/decree.md": {"artefact": ["decree.pdf", "annexe-1.pdf", "annexe-2.pdf"]},
    "raw/2021/bare.md": {"artefact": "bare.pdf"},
    "raw/2021/comma.md": {"artefact": "A Report (draft, World Bank).pdf"},
    "raw/2021/none.md": {"title": "no artefact at all"},
}
holds = au.declared({p: {"path": p, "d": {"ext": ".md"}, "fm": f} for p, f in rows.items()})
check("a flow list declares every element", sorted(holds),
      ["raw/2021/A Report (draft, World Bank).pdf", "raw/2021/annexe-1.pdf",
       "raw/2021/annexe-2.pdf", "raw/2021/bare.pdf", "raw/2021/decree.pdf"])
check("a bare name with a comma is one file, not two",
      holds["raw/2021/A Report (draft, World Bank).pdf"], ["raw/2021/comma.md"])
check("the key is resolved beside its own record",
      holds["raw/2021/annexe-1.pdf"], ["raw/2021/decree.md"])


# -- the boundary ----------------------------------------------------------

print("\nthe name scan's boundary")
with tempfile.TemporaryDirectory() as tmp:
    root = build(tmp, {
        "raw/2026/page.md": "see market-brief.pdf for the detail\n",
        "raw/2026/spaced.md": "artefact: 2026-01-01 Some Report.pdf\n",
        "raw/2026/tail.md": "the archive holds report.pdf.bak\n",
        "raw/2026/market-brief.pdf": "x",
        "raw/2026/brief.pdf": "x",
        "raw/2026/2026-01-01 Some Report.pdf": "x",
        "raw/2026/tailcase.pdf": "x",
    }, {})
    names = au.named_by(str(root), ["raw"],
                        {"market-brief.pdf", "brief.pdf", "2026-01-01 Some Report.pdf",
                         "tailcase.pdf"})
    check("the longer name is found", sorted(names["market-brief.pdf"]),
          ["raw/2026/page.md"])
    check("its suffix is not", sorted(names.get("brief.pdf", [])), [])
    check("a space in front of a name is a boundary, not a break",
          sorted(names["2026-01-01 Some Report.pdf"]), ["raw/2026/spaced.md"])
    check("a name continued after the extension is a different file",
          sorted(names.get("tailcase.pdf", [])), [])


# -- the shapes ------------------------------------------------------------
# Built as one tree so the ordering between them is what is being tested, not each rule
# on its own: several rows here would match two rules, and the shape has to be the one
# whose repair is right.

print("\nwhich shape a row lands in")
with tempfile.TemporaryDirectory() as tmp:
    files = {
        # declared PDF + an undeclared text extract of it, and the record also names
        # the .txt in its body — sidecar has to win, or it reads as a missing key.
        "raw/2026/held.md": "the extract is at held.txt\n",
        "raw/2026/held.pdf": "x",
        "raw/2026/held.txt": "x",
        # named by the record beside it, declared by nothing
        "raw/2026/key.md": "source document: key.pdf\n",
        "raw/2026/key.pdf": "x",
        # named by a record in another shard: a bare name cannot reach it
        "raw/2025/far.md": "the 2026 update is at strayed.pdf\n",
        "raw/2026/strayed.pdf": "x",
        # named only by a wiki page: nothing in raw/ holds it
        "wiki/intersections/a--b.md": "see offrecord.pdf\n",
        "raw/2026/offrecord.pdf": "x",
        # a record of the same stem, and nothing names the file at all
        "raw/2026/quiet.md": "no mention of its own document\n",
        "raw/2026/quiet.pdf": "x",
        # nothing at all
        "raw/2026/alone.pdf": "x",
    }
    fm = {"raw/2026/held.md": {"artefact": "held.pdf"}}
    root = build(tmp, files, fm)
    got = {r["artefact"]: (r["shape"], r["record_path"])
           for r in au.rows(str(root), "raw", str(root / "index"), ["raw", "wiki"], None)}
    check("a text extract of a declared document is a sidecar, not a missing key",
          got["raw/2026/held.txt"], ("text sidecar", "raw/2026/held.md"))
    check("the record beside it names it", got["raw/2026/key.pdf"],
          ("key missing", "raw/2026/key.md"))
    check("a record in another shard names it", got["raw/2026/strayed.pdf"],
          ("artefact misfiled", "raw/2025/far.md"))
    check("only a wiki page names it", got["raw/2026/offrecord.pdf"],
          ("named off-record", "wiki/intersections/a--b.md"))
    check("a record of the same stem, unnamed", got["raw/2026/quiet.pdf"],
          ("record beside it", "raw/2026/quiet.md"))
    check("nothing names it and no record matches", got["raw/2026/alone.pdf"],
          ("no record", ""))
    check("a declared artefact is not in the queue at all",
          "raw/2026/held.pdf" in got, False)
    # The split is on the document's own date. A file carrying none falls back to the
    # shard it is filed under, which is the vault's own dating of it; today the two never
    # disagree, and the fallback is what keeps that true rather than a fact to rely on.
    jobs = {r["artefact"]: (r["job"], r["date"])
            for r in au.rows(str(root), "raw", str(root / "index"), ["raw"], None)}
    check("no date in the name: the shard dates it", jobs["raw/2026/alone.pdf"],
          ("108", "2026"))
    check("a dated name in another shard: the name wins",
          au.file_date("raw/2026/2019-04-01-old-thing.pdf"), "2019-04-01")


# -- the inverse -----------------------------------------------------------

print("\nthe other direction, and its diagnosis")
with tempfile.TemporaryDirectory() as tmp:
    files = {
        "raw/2025/path-form.md": "x\n",
        "raw/2025/moved.md": "x\n",
        "raw/2026/moved.pdf": "x",
        "raw/2025/gone.md": "x\n",
    }
    fm = {"raw/2025/path-form.md": {"artefact": "../budget-archive/BEN/x.pdf"},
          "raw/2025/moved.md": {"artefact": "moved.pdf"},
          "raw/2025/gone.md": {"artefact": "gone.pdf"}}
    root = build(tmp, files, fm)
    got = {r["record_path"]: r["why"]
           for r in au.inverse(str(root), "raw", str(root / "index"))}
    check("a path form is reported as a path form, not as an absence",
          got["raw/2025/path-form.md"].startswith("a path, not a bare name"), True)
    check("and it is resolved the way the vault would resolve it",
          [r["resolves_to"] for r in au.inverse(str(root), "raw", str(root / "index"))
           if r["record_path"] == "raw/2025/path-form.md"],
          ["raw/budget-archive/BEN/x.pdf"])
    check("a file under another shard is a move, not a missing document",
          got["raw/2025/moved.md"], "the file is under another shard: raw/2026/moved.pdf")
    check("absent here is stated as absent here",
          got["raw/2025/gone.md"].startswith("no file of that name under raw/"), True)

print()
if fails:
    print("%d FAILED: %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("all checks passed")
