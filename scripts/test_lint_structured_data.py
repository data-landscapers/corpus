#!/usr/bin/env python3
"""test_lint_structured_data.py — prove the linter fails where it should.

The same argument as `test_lint_external_links.py`, and the same near-miss. A linter over a
block nobody reads is a linter nobody will notice has stopped looking, and this one shipped its
`encoding` check vacuous: it asked whether the PDF named in the block appeared in the page,
and the block is *in* the page, so the URL matched itself and the assertion could not fail.
Writing these cases is what found it. So the cases below are mostly failures — one real page,
mutated one fault at a time, checked to see that each is caught.

Each mutation is applied inside the block or outside it, never blindly, because most of these
faults *are* a disagreement between the two and a replacement that hit both would leave them
agreeing and the page clean.

    python scripts/test_lint_structured_data.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location(
    "lint_structured_data", SCRIPTS / "lint-structured-data.py")
lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint)

PAGE = SCRIPTS.parent / "site" / "reports" / "ZAF" / "ZAF-status.html"

failures: list[str] = []


def check(label: str, got: bool) -> None:
    print(f"  {'ok  ' if got else 'FAIL'} {label}")
    if not got:
        failures.append(label)


if not PAGE.exists():
    print(f"{PAGE.relative_to(SCRIPTS.parent)} is not there — render the site first")
    sys.exit(1)

html = PAGE.read_text(encoding="utf-8")
_m = lint.BLOCK.search(html)
if _m is None:
    print(f"{PAGE.name} carries no structured data block — nothing to mutate")
    sys.exit(1)
HEAD, BLOCK, TAIL = html[:_m.start()], html[_m.start():_m.end()], html[_m.end():]

# The values the mutations below have to name, read off the page rather than written in, so
# the cases go on working after the next edition of it is cut.
DATA = json.loads(_m.group(1))
PUBLISHED = DATA["datePublished"]
PDF_URL = DATA["encoding"]["contentUrl"]


def in_block(old: str, new: str) -> str:
    """Mutate the structured data and leave the page it sits in alone."""
    assert old in BLOCK, old
    return HEAD + BLOCK.replace(old, new) + TAIL


def in_page(old: str, new: str) -> str:
    """Mutate the page and leave the structured data alone."""
    assert old in HEAD + TAIL, old
    return HEAD.replace(old, new) + BLOCK + TAIL.replace(old, new)


print("a shipped page passes")
check("the real page is clean", lint.check(PAGE.name, html) == [])

print()
print("a page that has lost its block")
check("no block at all is a finding",
      lint.check("x", html.replace('<script type="application/ld+json">', "<script>")) != [])
check("a block that is not JSON is a finding",
      lint.check("x", in_block('"@context": "https://schema.org",',
                               '"@context": "https://schema.org"')) != [])
check("a block missing a required field is a finding",
      lint.check("x", in_block('"headline": "South Africa: status report",', "")) != [])

print()
print("dates")
check("an edition's same-day sequence is not a date",
      lint.check("x", in_block(f'"datePublished": "{PUBLISHED}"',
                               f'"datePublished": "{PUBLISHED}-2"')) != [])
check("a date in the future is a finding",
      lint.check("x", in_block(f'"datePublished": "{PUBLISHED}"',
                               '"datePublished": "2099-01-01"')) != [])
check("datePublished and dateModified disagreeing is a finding (design.md §9)",
      lint.check("x", in_block(f'"dateModified": "{PUBLISHED}"',
                               '"dateModified": "2026-01-01"')) != [])

print()
print("the page and the block disagreeing")
check("a canonical pointing elsewhere is a finding",
      lint.check("x", in_page('<link rel="canonical" href="https://corpus.data-landscapers.io'
                              '/reports/ZAF/ZAF-status.html">',
                              '<link rel="canonical" href="https://corpus.data-landscapers.io'
                              '/elsewhere.html">')) != [])
check("mainEntityOfPage pointing elsewhere is a finding",
      lint.check("x", in_block('"@id": "https://corpus.data-landscapers.io'
                               '/reports/ZAF/ZAF-status.html"',
                               '"@id": "https://corpus.data-landscapers.io/other.html"')) != [])
check("a description that is not the one in the meta tag is a finding",
      lint.check("x", in_page('<meta name="description" content="South Africa:',
                              '<meta name="description" content="Something else:')) != [])
check("a PDF the page does not offer is a finding — the check that shipped vacuous",
      lint.check("x", in_block(PDF_URL, PDF_URL.replace(".pdf", "-nope.pdf"))) != [])

print()
print("what the block is for")
check("a headline past the length search truncates at is a finding",
      lint.check("x", in_block('"headline": "South Africa: status report"',
                               '"headline": "%s"' % ("x" * 120))) != [])
check("losing one of the corpus subjects is a finding",
      lint.check("x", in_block('"name": "Data governance"', '"name": "Something else"')) != [])
check("losing the document's own place or subject is a finding",
      lint.check("x", in_block('"name": "South Africa"', '"name": ""')) != [])

print()
print("the shipped tree is clean")
_pages = sorted((SCRIPTS.parent / "site").rglob("*.html"))
_docs = [p for p in _pages
         if lint.DOCUMENT.match(p.relative_to(SCRIPTS.parent / "site").as_posix())]
check("every rendered document carries a block and agrees with itself",
      [f for p in _docs
       for f in lint.check(p.name, p.read_text(encoding="utf-8"))] == [])
check("and it looked at every one of them (none skipped)", len(_docs) > 240)

print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
