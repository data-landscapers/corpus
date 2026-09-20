#!/usr/bin/env python3
"""test_alerts.py — the rules `alerts.py` applies to the catalogue before the Worker sees it.

    python scripts/test_alerts.py

Three things, and all three are silent when they go wrong.

**The backfill rule** decides whether an alert is news or an archive dump. A record
ingested today and published in 2019 is a document arriving, not a document happening,
and the difference is `date_precision`: `2026` means the year, so its period ends on 31
December and it is as recent as the end of the year for this purpose. Get that wrong in
either direction and the email is either mostly backfill or missing the late reports the
whole catalogue exists to find — and either way it looks like a working alert.

**The record id** is what a feed reader keys on. If it moved between builds, every
subscriber to a feed would see the same documents again as new.

**The published columns.** `recent.json` is a file on the public site, and the check is
that its rows carry nothing outside `build-catalogue.py`'s `CSV_COLS` — the columns the
catalogue download already publishes — plus the row's own id. A field added to the
catalogue's internals must not reach it by being in the record the loop reads.

The site build is not needed: this works over records built in the test.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

_spec = importlib.util.spec_from_file_location(
    "alerts_mod", Path(__file__).resolve().parent / "alerts.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

import catalogue  # noqa: E402

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        failures.append(name)
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")


def rec(**kw) -> dict:
    """A catalogue record with every field the builder reads, overridable."""
    base = {"title": "A title", "publisher": "A publisher", "author": "",
            "published": "2026-09-01", "date_precision": "day",
            "places": ["KEN"], "topics": ["tech.ai"], "entities": [],
            "ingested": "2026-09-10", "url": "https://example.org/a",
            # Fields the catalogue holds and the download does not. None may appear
            # in recent.json; the last test is what says so.
            "slug": "2026-09-01-ken-a", "path": "raw/2026/x.md", "words": 400,
            "finance": False, "artefact": [], "url_note": "",
            "body_completeness": "full", "catalogue_hero": "A hero line"}
    base.update(kw)
    return base


print("the backfill rule, at each date_precision")

# A day is its own period: ingested 90 days later passes, 91 does not.
check("day, ingested 90 days later", A.passes_backfill(
    rec(published="2026-06-12", date_precision="day", ingested="2026-09-10")), True)
check("day, ingested 91 days later", A.passes_backfill(
    rec(published="2026-06-11", date_precision="day", ingested="2026-09-10")), False)
check("day, ingested the same day", A.passes_backfill(
    rec(published="2026-09-10", date_precision="day", ingested="2026-09-10")), True)

# A month ends on its last day, so June 2026 is current until 28 September.
check("month ends on its last day — June, ingested 28 September", A.passes_backfill(
    rec(published="2026-06", date_precision="month", ingested="2026-09-28")), True)
check("month, ingested 29 September", A.passes_backfill(
    rec(published="2026-06", date_precision="month", ingested="2026-09-29")), False)
check("February in a leap year ends on the 29th", A.period_end("2024-02", "month"),
      date(2024, 2, 29))
check("December rolls the year", A.period_end("2026-12", "month"), date(2026, 12, 31))

# A year ends on 31 December, which is what makes a bare year survivable at all.
check("year ends on 31 December", A.period_end("2026", "year"), date(2026, 12, 31))
check("year 2026, ingested in September, passes", A.passes_backfill(
    rec(published="2026", date_precision="year", ingested="2026-09-10")), True)
check("year 2019 never passes", A.passes_backfill(
    rec(published="2019", date_precision="year", ingested="2026-09-10")), False)

# The date's shape beats a precision that disagrees with it.
check("a full date with month precision is still a day", A.period_end("2026-06-12", "month"),
      date(2026, 6, 12))

# No published date at all: out, because there is nothing to measure against.
check("no published date is excluded", A.passes_backfill(
    rec(published="", date_precision="")), False)
check("an unparseable published date is excluded", A.passes_backfill(
    rec(published="circa 2019", date_precision="year")), False)
check("published ahead of ingest still passes", A.passes_backfill(
    rec(published="2026-10-01", ingested="2026-09-10")), True)


print("the record id")

with_url = A.record_id(rec(url="https://example.org/a"))
check("a URL gives 16 hex", (len(with_url), with_url.strip("0123456789abcdef")), (16, ""))
check("the same URL gives the same id",
      A.record_id(rec(url="https://example.org/a", title="Renamed later")), with_url)
check("a different URL gives a different id",
      A.record_id(rec(url="https://example.org/b")) != with_url, True)

no_url = A.record_id(rec(url=""))
check("no URL gives 16 hex", (len(no_url), no_url.strip("0123456789abcdef")), (16, ""))
check("no URL keys on title, publisher and date",
      A.record_id(rec(url="", slug="anything-else")), no_url)
check("a different title with no URL gives a different id",
      A.record_id(rec(url="", title="Another title")) != no_url, True)
check("a URL and no URL are different ids", no_url != with_url, True)


print("the window, and the file's columns")

rows = A.recent([
    rec(url="https://example.org/in", ingested="2026-09-10"),
    rec(url="https://example.org/edge", ingested="2026-08-14"),     # 28 days back: in
    rec(url="https://example.org/out", ingested="2026-08-13"),      # 29 days back: out
    rec(url="https://example.org/old", ingested="2026-09-10",
        published="2019-01-01"),                                    # backfill: out
], today=date(2026, 9, 11))
check("three candidates, two survive both rules", len(rows), 2)
check("the 28th day is inside the window",
      sorted(r["url"] for r in rows),
      ["https://example.org/edge", "https://example.org/in"])
check("newest ingested first", [r["ingested"] for r in rows], ["2026-09-10", "2026-08-14"])

allowed = set(catalogue.csv_cols()) | {"id"}
keys = {k for r in rows for k in r}
check("no key outside CSV_COLS plus id", sorted(keys - allowed), [])
check("every column the Worker needs is there",
      sorted(keys), sorted(["id"] + A.ROW_COLS))
check("lists stay lists", (rows[0]["places"], rows[0]["topics"]), (["KEN"], ["tech.ai"]))

# The one that would pass silently if `ROW_COLS` grew a column the download does not
# carry: assert the spec itself, not only the rows built from it.
check("ROW_COLS is a subset of CSV_COLS",
      sorted(set(A.ROW_COLS) - set(catalogue.csv_cols())), [])


print("the vocabularies the page and the Worker share")

voc = A.vocabularies()
check("places carry the region codes", all(c in voc["places"] for c in ("XWA", "XAF", "XGL")),
      True)
check("regions come first", list(voc["places"])[0].startswith("X"), True)
check("the last place is a country", list(voc["places"])[-1].startswith("X"), False)
check("topics are in the taxonomy's order",
      list(voc["topics"])[:2], ["gov.policy", "gov.legislate"])


print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
