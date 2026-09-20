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
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import editions  # noqa: E402 — the one implementation of the edition grammar (design.md §9)

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

# **The catalogue of datasets is the site, not `/catalogue/`.** That page is the landing page
# of one dataset — the document index — and it already answers to `…/catalogue/#dataset`. Naming
# it as the `DataCatalog` as well made one URL two types and put a dataset inside itself. The
# site is what actually holds several: the document catalogue, the non-state finance table, and
# the place cuts of each.
CATALOG = {
    "@type": "DataCatalog",
    "name": "Data Landscapers Corpus",
    "url": f"{SITE_BASE}/",
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

    **`published` may be an edition or a date**; `as_date` takes off any same-day sequence, so
    `2026-09-16-2` dates the document to the 16th. A document carries no `version`, because its
    dated PDF is named for the full edition and the page links it by name.

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
        "datePublished": as_date(published),
        "dateModified": as_date(published),
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


def bytes_of(path) -> int | None:
    """The size of a file that may have been pruned to R2 — None where it is not there.

    The absence carries no information: `--prune-local` deletes a dated edition once the bucket
    has it, and the Worker serves it from the path it had under `site/`. What must not happen is
    a size carried over from a file this build never saw."""
    return path.stat().st_size if path.exists() else None


def as_date(edition: str) -> str:
    """An edition's date, with any same-day sequence taken off — `2026-09-18-2` → `2026-09-18`.

    **Applied here rather than left to each caller**, because every caller that forgets it emits
    an invalid date, silently, on whichever handful of artefacts happened to be cut twice in one
    day. That has now been the same bug twice: `render.py` was written with the strip, and the
    finance datasets were written without it and put `2026-09-18-2` in a `dateModified` — caught
    by the linter on exactly one of 125 pages, which is how narrow the window is. A caller that
    has already stripped loses nothing: `edition_key` on a bare date gives the date back.

    `version` keeps the full edition, because the sequence is precisely what tells two editions
    of one day apart, and that is a version's job and not a date's."""
    return editions.edition_key(edition)[0] or edition


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


def year_span(years: list) -> str | None:
    """`temporalCoverage` over whole years — `1998/2031` — or None if there are none.

    The finance table is dated to the year a commitment was approved and the year the activity
    ends, and no finer; a year is a valid ISO 8601 interval bound, and padding one to a January
    the 1st would be inventing a precision the source does not have. `span()` above is the
    day-precision counterpart, for the catalogue's publication dates."""
    ys = sorted({int(y) for y in years if str(y).isdigit() and 1000 <= int(y) <= 9999})
    return f"{ys[0]}/{ys[-1]}" if ys else None


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


def dataset(*, name: str, description: str, url: str, csv_url: str,
            csv_bytes: int | None,
            records: int, fields: list[dict], entity: dict,
            temporal: str | None = None, modified: str | None = None,
            part_of: str | None = None, version: str | None = None,
            extra_keywords: tuple[str, ...] = ()) -> str:
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
        "keywords": list(SUBJECTS) + list(extra_keywords) + [entity["name"]],
        "spatialCoverage": entity,
        "variableMeasured": fields,
        # **`contentSize` only where the file is there to measure.** A dated edition is pruned
        # out of the tree once R2 has it (RENDER Step 6b), so a build that kept the standing
        # edition rather than cutting a new one has nothing local to weigh. A download with no
        # size is a download with no size; one carrying last year's is a claim about a file.
        "distribution": [{
            "@type": "DataDownload",
            "encodingFormat": "text/csv",
            "contentUrl": csv_url,
            **({"contentSize": size_label(csv_bytes)} if csv_bytes else {}),
        }],
    }
    if records:
        data["size"] = {"@type": "QuantitativeValue", "unitText": "records", "value": records}
    if temporal:
        data["temporalCoverage"] = temporal
    data["dateModified"] = modified or date.today().isoformat()

    # **An edition dates itself, and a wholesale republication dates itself too — differently.**
    #
    # The finance tables are editions (design.md §9): dated, retained, never revised. What the
    # page offers is one named file cut on one day, and the honest `dateModified` is that day —
    # not the day of the build, which would claim a change on every render of a table nobody
    # has touched since August. `version` is the edition, and `datePublished` moves with it,
    # because for an immutable artefact the two are the same date.
    #
    # The catalogue is not an edition — it is republished wholesale at an undated URL and
    # nobody cites it as of a date — so it passes no version and dates itself to the build,
    # which is the last moment its contents could have changed.
    if version:
        data["version"] = version
        data["dateModified"] = as_date(version)
        data["datePublished"] = data["dateModified"]
    if part_of:
        data["isPartOf"] = {"@type": "Dataset", "@id": dataset_id(part_of), "url": part_of}
    return block(data)
