#!/usr/bin/env python3
"""test_dewiki.py — wiki-link syntax never reaches a published deliverable.

    python scripts/test_dewiki.py

`[[target]]` is how the source records cross-reference each other inside the wiki. It
is meaningless to a reader of the site, and it has escaped twice: into a finance
description cell (Bill, 2026-08-19) and into the catalogue's author column (Bill,
2026-08-25), where `[[bill]]` published as an author called "bill". The second escape
happened because the first fix lived in the finance pass and nothing else could see it,
so `vault_lib.dewiki` is now the only definition and this tests both halves of the job:
the helper, and the artefacts the compiles actually wrote.

The artefact half skips rather than fails when `outputs/catalogue/` has not been built,
because the vault is not on every machine that runs the suite. Dated editions under
`site/` are deliberately out of scope — a published file is never revised (`RENDER.md`
§9), so the three pre-fix finance editions keep their brackets and always will.
"""
from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault_lib as V  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
failures = []


def check(what, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {what}"
          + ("" if ok else f"\n       got {got!r}\n       want {want!r}"))
    if not ok:
        failures.append(what)


print("the helper")
check("a bare target falls back to itself", V.dewiki("see [[a-slug]]"), "see a-slug")
check("a piped target keeps its label", V.dewiki("see [[a-slug|the deal]]"), "see the deal")
check("an empty label wins anyway — the record meant to hide the target",
      V.dewiki("see [[a-slug|]]"), "see ")
check("a known target resolves to its display name",
      V.dewiki("[[bill]] and Sam", {"bill": "Bill Anderson"}), "Bill Anderson and Sam")
check("an unknown target is still stripped",
      V.dewiki("[[nobody]]", {"bill": "Bill Anderson"}), "nobody")
check("several in one string", V.dewiki("[[a]], [[b|B]] and [[c]]"), "a, B and c")
check("text without brackets is untouched", V.dewiki("nothing here"), "nothing here")
check("a lone bracket pair is not a wikilink", V.dewiki("[a] and [b]"), "[a] and [b]")

print("the artefacts the compiles wrote")
cat = CORPUS / "outputs" / "catalogue" / "raw-catalogue.json"
fin = CORPUS / "outputs" / "non-state-finance" / "all-nonstate.csv"
if not cat.exists():
    print("  skip  outputs/catalogue/ not built")
else:
    rows = json.loads(cat.read_text(encoding="utf-8"))
    rows = rows["items"] if isinstance(rows, dict) and "items" in rows else rows
    bad = [f"{r.get('slug')}: {k}" for r in rows for k, v in r.items()
           if isinstance(v, str) and "[[" in v]
    check("no wikilink in raw-catalogue.json", bad[:5], [])
if not fin.exists():
    print("  skip  outputs/non-state-finance/ not built")
else:
    with io.open(fin, encoding="utf-8-sig", newline="") as fh:
        bad = [f"{r.get('record')}: {k}" for r in csv.DictReader(fh)
               for k, v in r.items() if v and "[[" in v]
    check("no wikilink in all-nonstate.csv", bad[:5], [])

print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
