#!/usr/bin/env python3
"""structured_data.py — the `application/ld+json` block, for the builders that emit one.

Three kinds of page describe themselves to a crawler and there is one implementation of what
that means: `render.py` for the 251 documents, `catalogue.py` for the catalogue and `country.py`
for each place's cut of it. The publisher, the corpus's three subjects, the `</` escaping and
the JSON shape were duplicated the moment the second caller existed, which is the arrangement
this repository has a linter for everywhere else.

**Structured data says what the page already says, in the form a machine does not have to guess
at.** Nothing here may assert anything a reader cannot see on the page it sits in: that is the
test `lint-structured-data.py` applies, it is what keeps a site out of trouble with the search
engines, and it is also the only way a document avoids telling two stories about itself.

**What a `Dataset` is here, and what it is not.** The catalogue is metadata and links — title,
publisher, date, facets and the publisher's own URL — and never the body of anyone else's
source. The description says so, because a `Dataset` entry is an invitation and the reader
answering it should not have to click to learn what is on the other side. `license` covers the
compilation, which is ours; it does not and could not cover the documents it points at.
"""

from __future__ import annotations

import json
from datetime import date

SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"

# The publisher, once. `author`/`creator` and `publisher` are the same organisation on every
# page here, and the page says so twice already — the masthead and the licence row.
#
# **It names Data Landscapers and not the model that writes the reports.** The byline does that
# — *compiled by Claude Opus from the documents in the Corpus repository* — and that is where
# the disclosure belongs, in the prose a reader sees. `author` in structured data answers a
# different question: who is accountable for what this says, and who may be asked about it.
# Schema.org has no type that would let the byline's answer go here without lying about the
# range of the property.
ORG = {
    "@type": "Organization",
    "name": "Data Landscapers",
    "url": f"{MAIN_SITE}/",
    "logo": {"@type": "ImageObject", "url": f"{MAIN_SITE}/assets/logo.png"},
}

CATALOG = {
    "@type": "DataCatalog",
    "name": "Data Landscapers Corpus",
    "url": f"{SITE_BASE}/catalogue/",
}

# The three subjects the whole corpus is about, named as things rather than as words in a
# sentence. The page descriptions say them in prose for a reader; this says them where a crawler
# reads entities, which is the half of the same job prose cannot do.
SUBJECTS = ("Digital transformation", "Digital public infrastructure", "Data governance")


def subjects() -> list[dict]:
    """The three, as `Thing`s, for an `about` list."""
    return [{"@type": "Thing", "name": s} for s in SUBJECTS]


def place(code: str, name: str) -> dict:
    """A place, typed on its code: `Country` for an ISO-3, `Place` for a region or bloc.

    The type is the useful part — `Country` resolves *Niger* against a crawler's own gazetteer,
    where `Thing` leaves it a string that also names a river. Every region and bloc code opens
    with `X` (`lookups/countries.csv`), and a region is a `Place` and not a `Country` because
    *West Africa* is not one."""
    return {"@type": "Place" if not code or code.startswith("X") else "Country", "name": name}


def block(data: dict) -> str:
    """Serialise and wrap. The one place the escaping lives.

    `</` is escaped because a `</script` anywhere inside the block would end the element early
    and spill the rest of the JSON onto the page as text. Nothing we emit contains one today;
    the escape is what keeps that from being load-bearing. It is valid JSON either way."""
    body = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return '<script type="application/ld+json">\n' + body + '\n</script>'


def document(*, kind: str, headline: str, description: str, url: str, published: str,
             pdf_url: str | None, entity: dict) -> str:
    """One report, bulletin or update, described as data.

    **Everything here is printed somewhere on the page**: the title in the header, the dates in
    the byline, the licence and the PDF in the colophon, the description in the meta tag beside
    this block.

    **`published` must already be a date.** An edition is `2026-09-16` or `2026-09-16-2`
    (design.md §9) and the second of those is not one; the caller strips the same-day sequence
    through `editions.edition_key`, which is where that parse lives.

    **`dateModified` equals `datePublished` because a published edition is never revised.** That
    is §9 stated in the vocabulary a crawler reads, and it is true: a document whose content
    moves gets a new edition at a new dated URL rather than an edit to this one."""
    data = {
        "@context": "https://schema.org",
        # A bulletin is news and a report is not. Both carry `Article` so that a consumer which
        # only knows the common supertype still recognises them.
        "@type": "NewsArticle" if kind == "bulletin" else ["Article", "Report"],
        "headline": headline,
        "description": description,
        "url": url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "datePublished": published,
        "dateModified": published,
        "inLanguage": "en",
        "license": LICENCE_URL,
        "isAccessibleForFree": True,
        "author": ORG,
        "publisher": ORG,
        "isPartOf": {"@type": "WebSite", "name": "Data Landscapers Corpus",
                     "url": f"{SITE_BASE}/"},
        "about": [entity] + subjects(),
    }
    # Only where one was cut. A document rendered without a PDF must not advertise one — the
    # same rule the download button and the `This file` row follow.
    if pdf_url:
        data["encoding"] = {"@type": "MediaObject",
                            "encodingFormat": "application/pdf",
                            "contentUrl": pdf_url}
    return block(data)


def size_label(n_bytes: int) -> str:
    """`contentSize`, in the units the reader's save dialog will show.

    The size on disk rather than the bytes that cross the wire, which are gzipped to about a
    quarter of it — the page prints the same number beside the link, and two different sizes
    for one file is a question nobody should have to answer."""
    return f"{n_bytes / 1e6:.1f} MB" if n_bytes >= 1e6 else f"{n_bytes / 1e3:.0f} KB"


def span(dates: list[str]) -> str | None:
    """`temporalCoverage` as an ISO 8601 interval over the dates given, or None if there are
    none to span.

    Built from the records themselves rather than written down, because a hand-kept range is a
    claim that stops being true on the next sweep and says nothing when it does. Anything that
    is not a bare `YYYY-MM-DD` is dropped: the catalogue's `published` column carries a
    `date_precision` beside it, and a record precise only to the year is stored as its first
    day, which is a good enough bound and a bad exact date."""
    days = sorted(d for d in dates if len(d) == 10 and d[4] == "-" and d[7] == "-")
    return f"{days[0]}/{days[-1]}" if days else None


def fields_from(rows: list[dict]) -> list[dict]:
    """`variableMeasured`, from the published field dictionary — the same CSV the page links as
    *what each column means*, so the two cannot drift.

    This is the part of a `Dataset` entry that answers *what is actually in it* before anyone
    downloads anything, and we already had the answer written down for a reader."""
    return [{"@type": "PropertyValue", "name": r["Column"], "description": r["Definition"]}
            for r in rows if r.get("Column")]


def dataset_id(url: str) -> str:
    """The `@id` of the dataset described on a landing page, which is not the page's own."""
    return url + "#dataset"


def dataset(*, name: str, description: str, url: str, csv_url: str, csv_bytes: int,
            records: int, fields: list[dict], entity: dict,
            temporal: str | None = None, modified: str | None = None,
            part_of: str | None = None) -> str:
    """A downloadable table, described as data — for Google Dataset Search and its like.

    **`isPartOf` is what makes 62 place cuts a set rather than 62 unrelated tables.** Each place
    page publishes its own slice of one catalogue; a consumer told that gets one dataset with 62
    subsets, and a consumer not told it gets 62 datasets that happen to share a schema and look
    like duplicates of each other, which is the shape that gets a site's entries suppressed."""
    data = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        # **The dataset is not the page.** `/catalogue/` is a `DataCatalog` — a place where
        # datasets are listed — and it is also where this one is described, so both would
        # otherwise answer to the same identifier and a strict consumer would be told that one
        # URL names two different types. The fragment separates them, and it is what a slice's
        # `isPartOf` points at.
        "@id": dataset_id(url),
        "name": name,
        "description": description,
        "url": url,
        "license": LICENCE_URL,
        "isAccessibleForFree": True,
        "creator": ORG,
        "publisher": ORG,
        "includedInDataCatalog": CATALOG,
        "inLanguage": "en",
        "keywords": list(SUBJECTS) + [entity["name"]],
        "spatialCoverage": entity,
        "variableMeasured": fields,
        "distribution": [{
            "@type": "DataDownload",
            "encodingFormat": "text/csv",
            "contentUrl": csv_url,
            "contentSize": size_label(csv_bytes),
        }],
    }
    if records:
        data["size"] = {"@type": "QuantitativeValue", "unitText": "records", "value": records}
    if temporal:
        data["temporalCoverage"] = temporal
    data["dateModified"] = modified or date.today().isoformat()
    if part_of:
        data["isPartOf"] = {"@type": "Dataset", "@id": dataset_id(part_of), "url": part_of}
    return block(data)
