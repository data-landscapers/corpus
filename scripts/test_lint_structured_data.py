#!/usr/bin/env python3
"""test_lint_structured_data.py — prove the linter fails where it should.

The same argument as `test_lint_external_links.py`, and the same near-miss twice over. A linter
over a block nobody reads is a linter nobody will notice has stopped looking.

- Its `encoding` check shipped vacuous: it asked whether the PDF named in the block appeared in
  the page, and the block is *in* the page, so the URL matched itself and the assertion could
  not fail. Writing these cases is what found it.
- The fix then over-corrected. It demanded the page carry the *absolute* URL, which every page
  doing the right thing does not — a page links its own downloads relatively. That failed all
  62 place pages at once, which at least failed loudly.
- The finance datasets then put `2026-09-18-2` in a `dateModified`, which is an edition and is
  not a date — the same fault `render.py` had been written to avoid, reintroduced by a second
  caller that did not know to strip it. It showed on exactly one page of 125. `as_date` does it
  inside `structured_data` now, where a caller cannot forget.

So the cases below are mostly failures: three real shipped pages — a document, a catalogue cut
and a finance edition — mutated one fault at a time. Each mutation goes inside the block or outside it and never
blindly, because most of these faults *are* a disagreement between the two, and a replacement
hitting both would leave them agreeing and the page reading clean.

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

SITE = SCRIPTS.parent / "site"
DOC_PAGE = SITE / "reports" / "ZAF" / "ZAF-status.html"
SET_PAGE = SITE / "countries" / "ZAF" / "index.html"          # a catalogue cut — not an edition
FIN_PAGE = SITE / "countries" / "ZAF" / "finance.html"        # a finance table — an edition

failures: list[str] = []


def check(label: str, got: bool) -> None:
    print(f"  {'ok  ' if got else 'FAIL'} {label}")
    if not got:
        failures.append(label)


class Page:
    """One shipped page, split at its structured data so a mutation can be aimed."""

    def __init__(self, path: Path):
        self.path = path
        self.html = path.read_text(encoding="utf-8")
        m = lint.BLOCK.search(self.html)
        if m is None:
            raise SystemExit(f"{path.name} carries no structured data block")
        self.head, self.block, self.tail = (
            self.html[:m.start()], self.html[m.start():m.end()], self.html[m.end():])
        self.data = json.loads(m.group(1))

    def in_block(self, old: str, new: str) -> str:
        """Mutate the structured data and leave the page it sits in alone."""
        assert old in self.block, f"{self.path.name}: {old!r} is not in the block"
        return self.head + self.block.replace(old, new) + self.tail

    def in_page(self, old: str, new: str) -> str:
        """Mutate the page and leave the structured data alone."""
        assert old in self.head + self.tail, f"{self.path.name}: {old!r} is not in the page"
        return self.head.replace(old, new) + self.block + self.tail.replace(old, new)

    def with_data(self, **fields) -> str:
        """Rebuild the block from the parsed data with fields replaced, or removed where the
        value given is None — for a fault that is structural rather than textual, where string
        surgery would either miss it or reach further than the case means to."""
        data = {k: v for k, v in (dict(self.data) | fields).items() if v is not None}
        body = json.dumps(data, ensure_ascii=False, indent=2)
        return (self.head + '<script type="application/ld+json">\n'
                + body + '\n</script>' + self.tail)

    def caught(self, html: str) -> bool:
        return lint.check(self.path.name, html) != []


for p in (DOC_PAGE, SET_PAGE, FIN_PAGE):
    if not p.exists():
        print(f"{p.relative_to(SCRIPTS.parent)} is not there — build the site first")
        sys.exit(1)

doc, dset, fin = Page(DOC_PAGE), Page(SET_PAGE), Page(FIN_PAGE)

print("the shipped pages pass")
check("the document page is clean", lint.check(doc.path.name, doc.html) == [])
check("the catalogue-cut page is clean", lint.check(dset.path.name, dset.html) == [])
check("the finance-edition page is clean", lint.check(fin.path.name, fin.html) == [])

print()
print("a block that is not there, or not JSON")
check("no block at all is a finding",
      doc.caught(doc.html.replace('<script type="application/ld+json">', "<script>")))
check("a block that is not JSON is a finding",
      doc.caught(doc.in_block('"@context": "https://schema.org",',
                              '"@context": "https://schema.org"')))
check("a @type that is neither shape is a finding — a builder with its own implementation",
      doc.caught(doc.in_block('"@type": [\n    "Article",\n    "Report"\n  ]',
                              '"@type": "WebPage"')))

print()
print("a document")
PUB = doc.data["datePublished"]
check("a required field missing is a finding",
      doc.caught(doc.in_block('"headline": "South Africa: status report",', "")))
check("an edition's same-day sequence is not a date",
      doc.caught(doc.in_block(f'"datePublished": "{PUB}"', f'"datePublished": "{PUB}-2"')))
check("a date in the future is a finding",
      doc.caught(doc.in_block(f'"datePublished": "{PUB}"', '"datePublished": "2099-01-01"')))
check("datePublished and dateModified disagreeing is a finding (design.md §9)",
      doc.caught(doc.in_block(f'"dateModified": "{PUB}"', '"dateModified": "2026-01-01"')))
check("mainEntityOfPage pointing elsewhere is a finding",
      doc.caught(doc.in_block(f'"@id": "{doc.data["url"]}"',
                              '"@id": "https://corpus.data-landscapers.io/other.html"')))
check("a description that is not the one in the meta tag is a finding",
      doc.caught(doc.in_page('<meta name="description" content="South Africa:',
                             '<meta name="description" content="Something else:')))
check("a headline past the length search truncates at is a finding",
      doc.caught(doc.in_block('"headline": "South Africa: status report"',
                              '"headline": "%s"' % ("x" * 120))))
check("losing one of the corpus subjects is a finding",
      doc.caught(doc.in_block('"name": "Data governance"', '"name": "Something else"')))
check("losing the document's own place or subject is a finding",
      doc.caught(doc.with_data(about=[{"@type": "Country", "name": ""}] + doc.data["about"][1:])))

print()
print("a dataset")
CSV = dset.data["distribution"][0]["contentUrl"]
SIZE = dset.data["distribution"][0]["contentSize"]
check("a required field missing is a finding",
      dset.caught(dset.with_data(license=None)))
check("an @id that is not the landing page's dataset id is a finding",
      dset.caught(dset.in_block(f'"@id": "{dset.data["@id"]}"', '"@id": "urn:whatever"')))
check("a description too short for a dataset search is a finding",
      dset.caught(dset.in_block(json.dumps(dset.data["description"], ensure_ascii=False),
                                '"Too short."')))
check("temporalCoverage that is not a date interval is a finding",
      dset.caught(dset.in_block(f'"temporalCoverage": "{dset.data["temporalCoverage"]}"',
                                '"temporalCoverage": "the 2020s"')))
check("temporalCoverage running backwards is a finding",
      dset.caught(dset.in_block(f'"temporalCoverage": "{dset.data["temporalCoverage"]}"',
                                '"temporalCoverage": "2026-09-19/1992-05-06"')))
check("a dateModified in the future is a finding",
      dset.caught(dset.in_block(f'"dateModified": "{dset.data["dateModified"]}"',
                                '"dateModified": "2099-01-01"')))
check("describing no columns is a finding — a missing field dictionary",
      dset.caught(dset.with_data(variableMeasured=[])))
check("a column with no definition is a finding",
      dset.caught(dset.in_block('"description": "The date the document was published"',
                                '"description": ""')))
check("keywords that do not name the corpus subjects is a finding",
      dset.caught(dset.in_block('"Data governance",\n    "South Africa"',
                                '"Something else",\n    "South Africa"')))
check("spatialCoverage with no place is a finding",
      dset.caught(dset.in_block('"spatialCoverage": {\n    "@type": "Country",\n'
                                '    "name": "South Africa"\n  }',
                                '"spatialCoverage": {\n    "@type": "Country",\n'
                                '    "name": ""\n  }')))
check("isPartOf naming no whole dataset this site publishes is a finding",
      dset.caught(dset.in_block('"@id": "https://corpus.data-landscapers.io/catalogue/#dataset"',
                                '"@id": "https://example.com/other#dataset"')))

print()
print("downloads — the two checks that shipped wrong")
check("an undated CSV the page does not offer is a finding (the vacuous check)",
      dset.caught(dset.in_block(CSV, CSV.replace("-catalogue.csv", "-nope.csv"))))
check("an undated CSV missing from the built tree is a finding — nothing prunes those",
      dset.caught(dset.in_page('href="ZAF-catalogue.csv"', 'href="ZAF-gone.csv"')
                  .replace(CSV, CSV.replace("ZAF-catalogue.csv", "ZAF-gone.csv"))))
check("a contentSize that is not the file's real size is a finding",
      dset.caught(dset.in_block(f'"contentSize": "{SIZE}"', '"contentSize": "1.0 MB"')))
check("a relative link on the page still counts as offering the file (the over-correction)",
      not dset.caught(dset.html))
check("a PDF the document page does not offer is a finding",
      doc.caught(doc.in_block(doc.data["encoding"]["contentUrl"],
                              doc.data["encoding"]["contentUrl"].replace(".pdf", "-nope.pdf"))))

print()
print("a dataset that is a dated edition")
check("a version that is not an edition is a finding",
      fin.caught(fin.with_data(version="the latest one")))
check("an edition's dateModified and datePublished disagreeing is a finding",
      fin.caught(fin.with_data(datePublished="2020-01-01")))
check("a version that is not the edition the page says it is offering is a finding",
      fin.caught(fin.with_data(version="2019-01-01", dateModified="2019-01-01",
                               datePublished="2019-01-01")))
check("a download that is not the artefact the page records is a finding",
      fin.caught(fin.with_data(distribution=[
          dict(fin.data["distribution"][0],
               contentUrl=fin.data["distribution"][0]["contentUrl"].replace(
                   "-nonstate-", "-somethingelse-"))])))
check("a dated edition absent from the tree is NOT a finding — it is pruned to R2",
      not fin.caught(fin.html))
check("year-precision temporalCoverage is accepted",
      not fin.caught(fin.with_data(temporalCoverage="2015/2042")))
check("a year-precision span running backwards is a finding",
      fin.caught(fin.with_data(temporalCoverage="2042/2015")))
check("isPartOf naming the finance table is accepted",
      not fin.caught(fin.html))
check("isPartOf naming the dataset itself is a finding",
      fin.caught(fin.with_data(isPartOf={"@type": "Dataset", "@id": fin.data["@id"]})))
check("includedInDataCatalog naming /catalogue/ is a finding — one dataset is not the catalogue",
      fin.caught(fin.with_data(includedInDataCatalog={
          "@type": "DataCatalog", "name": "x",
          "url": "https://corpus.data-landscapers.io/catalogue/"})))

print()
print("the shipped tree is clean")
_carries, _findings = [], []
for _p in sorted(SITE.rglob("*.html")):
    _rel = _p.relative_to(SITE).as_posix()
    _html = _p.read_text(encoding="utf-8")
    if lint.BLOCK.search(_html):
        _carries.append(_rel)
        _findings += lint.check(_rel, _html)
    elif lint.DOCUMENT_PAGE.match(_rel):
        _findings.append(f"{_rel}: no block")
check("every page with a block agrees with itself", _findings == [])
check("and it looked at all of them (none skipped)", len(_carries) > 300)

print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
