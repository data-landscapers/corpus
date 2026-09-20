#!/usr/bin/env python3
r"""test_artefact_dupes.py — the grouping proves identity, and the counts are the real cost.

    python scripts/test_artefact_dupes.py

`artefact-dupes.py` hands OSINT six read-and-judge calls (housekeeping job 106). Both halves
of what it hands over can be wrong quietly:

- **A group that is not byte-identical** sends someone to retire a record over a digest
  collision, so the grouping is checked against files that share a size, and files that share
  a size and differ.
- **A citation count that is wrong** is worse than absent, because it is the number the
  retirement call is made on. The two ways it inflates are a page citing the same record
  twice and a record's own self-reference, and both are checked.

The title lookup is here because it broke on the first run and did so silently: the index
carries a row per *file*, so an artefact has a row under its record's slug with no
frontmatter, and reading those too blanked the title for exactly the pairs whose artefact is
named after its record — the ones most likely to be duplicates.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "artefact_dupes", Path(__file__).resolve().parent / "artefact-dupes.py")
ad = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ad)

fails = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"       got  {got!r}\n       want {want!r}")
        fails.append(name)


tmp = Path(tempfile.mkdtemp(prefix="dupes-"))
try:
    root = tmp / "repo"
    raw = root / "raw" / "2026"
    raw.mkdir(parents=True)

    # Two identical, one that shares their size and differs, one unique, and a record.
    (raw / "a.pdf").write_bytes(b"IDENTICAL-PAYLOAD")
    (raw / "b.pdf").write_bytes(b"IDENTICAL-PAYLOAD")
    (raw / "c.pdf").write_bytes(b"DIFFERENT-PAYLOD!")      # same 17 bytes, different content
    (raw / "d.pdf").write_bytes(b"UNIQUE")
    (raw / "rec.md").write_bytes(b"---\ntype: source\n---\n\nbody\n")
    check("the same size is not the test",
          len((raw / "c.pdf").read_bytes()), len((raw / "a.pdf").read_bytes()))

    print("grouping")
    found = ad.groups(ad.artefacts(str(root), "raw"))
    check("one group", len(found), 1)
    size, _, members = found[0]
    check("of the two identical files",
          sorted(Path(p).name for p in members), ["a.pdf", "b.pdf"])
    check("at their own size", size, 17)
    check("the .md is not an artefact",
          [p for p in ad.artefacts(str(root), "raw") if p.endswith(".md")], [])
    check("byte comparison settles a size match",
          ad.same(str(raw / "a.pdf"), str(raw / "c.pdf")), False)
    check("and confirms a real one",
          ad.same(str(raw / "a.pdf"), str(raw / "b.pdf")), True)

    print("\nthe vault reading")
    index = root / "index"
    index.mkdir()

    def files_jsonl(rows):
        with open(index / "files.jsonl", "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")

    def links_jsonl(rows):
        with open(index / "links.jsonl", "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")

    files_jsonl([
        {"path": "raw/2026/keeper.md", "d": {"slug": "keeper", "ext": ".md"},
         "fm": {"title": "The keeper", "url": "https://example.org/k",
                "artefact": "a.pdf"}},
        # The artefact's own row, under the same slug and with no frontmatter. Reading it
        # as a record is what blanked the titles on the first real run.
        {"path": "raw/2026/a.pdf", "d": {"slug": "keeper", "ext": ".pdf"}, "fm": {}},
        {"path": "raw/2026/other.md", "d": {"slug": "other", "ext": ".md"},
         "fm": {"title": "The other", "url": "https://example.org/o",
                "artefact": ["b.pdf"]}},
        {"path": "wiki/places/KEN.md", "d": {"slug": "KEN", "ext": ".md"}, "fm": {}},
    ])
    links_jsonl([
        {"from": "wiki/places/KEN.md", "to": "keeper", "via": "sources", "line": 0},
        # The same page reaching the same record again: one citing page, not two.
        {"from": "wiki/places/KEN.md", "to": "keeper", "via": "body", "line": 12},
        {"from": "wiki/concepts/x.md", "to": "keeper", "via": "cite_through", "line": 0},
        # A record's own edge to itself is not a citation of it.
        {"from": "raw/2026/keeper.md", "to": "keeper", "via": "body", "line": 3},
        # An edge that is not a citation at all.
        {"from": "wiki/places/KEN.md", "to": "cassava-technologies",
         "via": "entities", "line": 0},
        {"from": "wiki/places/KEN.md", "to": "other", "via": "sources", "line": 0},
    ])

    holder, cites, about = ad.vault(str(index))
    check("the artefact row does not blank the record's title",
          about["keeper"][0], "The keeper")
    check("the url comes through", about["keeper"][1], "https://example.org/k")
    check("a string artefact and a list of one read the same",
          (holder["a.pdf"], holder["b.pdf"]), (["keeper"], ["other"]))
    check("one page citing twice counts once", cites["keeper"], 2)
    check("an entities edge is not a citation", cites["cassava-technologies"], 0)

    print("\nthe rows it hands over")
    out = ad.rows(str(root), "raw", str(index))
    check("two rows, one group", (len(out), {r["group"] for r in out}), (2, {1}))
    by_file = {Path(r["artefact"]).name: r for r in out}
    check("each side carries its own record and count",
          [(by_file["a.pdf"]["record"], by_file["a.pdf"]["citations"]),
           (by_file["b.pdf"]["record"], by_file["b.pdf"]["citations"])],
          [("keeper", 2), ("other", 1)])

    # An artefact no record declares is its own finding: retiring the other side would
    # leave it unreachable rather than duplicated.
    files_jsonl([
        {"path": "raw/2026/keeper.md", "d": {"slug": "keeper", "ext": ".md"},
         "fm": {"title": "The keeper", "artefact": "a.pdf"}},
    ])
    out = ad.rows(str(root), "raw", str(index))
    by_file = {Path(r["artefact"]).name: r for r in out}
    check("an undeclared artefact says so",
          by_file["b.pdf"]["record"], "(no record declares it)")
    check("and is counted at zero", by_file["b.pdf"]["citations"], 0)

    print("\nexit codes")
    check("collisions exit 1",
          ad.main(["--root", str(root), "--index", str(index)]), 1)
    (raw / "b.pdf").unlink()
    check("none exit 0", ad.main(["--root", str(root), "--index", str(index)]), 0)
    check("a missing tree exits 2",
          ad.main(["--root", str(root), "--tree", "nope", "--index", str(index)]), 2)
    check("a missing index exits 2",
          ad.main(["--root", str(root), "--index", str(tmp / "nope")]), 2)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
print("all cases pass" if not fails else f"{len(fails)} of the cases FAILED")
sys.exit(1 if fails else 0)
