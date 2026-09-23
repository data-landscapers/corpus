#!/usr/bin/env python3
r"""site-analytics.py — daily views (Google Analytics) and search clicks (Search Console).

`documentation/site-analytics.md` is the design; this implements it. One row per
date x host in `logs/site-analytics.csv`, private, never published.

**It updates rows, it never appends blindly.** Neither source is final the next morning
(GA settles in 24-48 hours, Search Console trails by two to three days), so every run
re-fetches the last `WINDOW` days of each up to yesterday and replaces them. A skipped
night fills itself in: a source's range starts at the earlier of its window and the
first date since `FLOOR` on which it has no value at all.

**Blank means not answered, zero means answered with nothing.** A source *answers* a
date when that date is on or before the newest date it returned any row for. On an
answered date a known host it said nothing about is 0; on an unanswered one (Search
Console has not published yet, or the fetch failed) the old value stands, blank if
there was none. Views from a local preview (`LOCAL`) are dropped, not counted: they
are the site being checked on this machine, not readers. `other` sums `users` across
hosts, which over-counts anyone who hit two of them — it is there so the day's public
views reconcile with the GA interface, not as a headcount.

**A row's `fetched_at` moves only when one of its values does**, so a run that changed
nothing leaves the file byte-identical and the cycle commits nothing.

The key is a credential: its path comes from `CORPUS_GOOGLE_KEY`, its contents are never
printed. The Google libraries are imported inside the fetchers so the tests run without
them.

Usage:  python scripts/site-analytics.py [--dry-run] [--since YYYY-MM-DD]
Exit:   0 both fetched, 1 one or both failed (what succeeded is written),
        2 misconfigured — no key, unreadable key, permission denied.
The last line printed is the message for `log-line.py ANALYTICS`.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import os
import sys
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "logs", "site-analytics.csv")
KEY = os.environ.get("CORPUS_GOOGLE_KEY",
                     os.path.join(os.path.expanduser("~"), ".api-keys", "google-analytics.json"))
GA_PROPERTY = "properties/539744459"
SC_SITE = "sc-domain:data-landscapers.io"

# Bill, 2026-09-23: the log starts here. Search Console has nothing earlier.
FLOOR = dt.date(2026, 9, 13)
HOSTS = ("data-landscapers.io", "corpus.data-landscapers.io")
# Bill, 2026-09-23: a local preview is not a reader; dropped rather than folded into other.
LOCAL = {"localhost", "127.0.0.1", "::1", "[::1]"}
SHORT = {"data-landscapers.io": "dl.io", "corpus.data-landscapers.io": "corpus"}
FIELDS = ["date", "host", "views", "users", "sessions", "clicks", "impressions", "fetched_at"]
COLS = {"ga": ("views", "users", "sessions"), "sc": ("clicks", "impressions")}
WINDOW = {"ga": 3, "sc": 4}
NAME = {"ga": "Google Analytics", "sc": "Search Console"}


class Misconfigured(Exception):
    """No key, an unreadable key, or a permission Google refused — exit 2, needs Bill."""


def fold_host(host: str | None) -> str | None:
    """The table's host for a reported one; None for a local preview, which is dropped."""
    if host in LOCAL:
        return None
    return host if host in HOSTS else "other"


def days(start: dt.date, end: dt.date):
    d = start
    while d <= end:
        yield d
        d += dt.timedelta(days=1)


# --- the table ---------------------------------------------------------------------

def read_table(path: str) -> dict[tuple[str, str], dict[str, str]]:
    if not os.path.exists(path):
        return {}
    with io.open(path, encoding="utf-8", newline="") as fh:
        return {(r["date"], r["host"]): {f: r.get(f) or "" for f in FIELDS}
                for r in csv.DictReader(fh)}


def render_table(table: dict[tuple[str, str], dict[str, str]]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    for key in sorted(table):
        w.writerow(table[key])
    return buf.getvalue()


def write_table(path: str, text: str) -> None:
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# --- the range ---------------------------------------------------------------------

def fetch_start(table, source: str, yesterday: dt.date,
                since: dt.date | None = None) -> dt.date | None:
    """First date this run fetches for `source`, or None when there is nothing to do."""
    if since is not None:
        return since if since <= yesterday else None
    start = max(FLOOR, yesterday - dt.timedelta(days=WINDOW[source] - 1))
    have = {d for (d, _), row in table.items() if any(row[c] != "" for c in COLS[source])}
    for d in days(FLOOR, start - dt.timedelta(days=1)):
        if d.isoformat() not in have:
            start = d
            break
    return start if start <= yesterday else None


# --- merging a fetch in ------------------------------------------------------------

def merge(table, source: str, start: dt.date, end: dt.date,
          got: dict[tuple[str, str], dict[str, int]], now: str) -> list[str]:
    """Replace `source`'s columns for start..end with `got`; return the dates changed.

    `got` is keyed (ISO date, folded host). Only dates the source answered are touched.
    """
    answered_through = max((d for d, _ in got), default=None)
    changed: set[str] = set()
    for day in days(start, end):
        d = day.isoformat()
        if answered_through is None or d > answered_through:
            continue
        hosts = set(HOSTS) | {h for (gd, h) in got if gd == d} | {h for (td, h) in table if td == d}
        for host in hosts:
            row = table.get((d, host)) or {f: "" for f in FIELDS} | {"date": d, "host": host}
            vals = got.get((d, host), {})
            new = dict(row)
            for c in COLS[source]:
                new[c] = str(vals.get(c, 0))
            if new != row or (d, host) not in table:
                new["fetched_at"] = now
                table[(d, host)] = new
                changed.add(d)
    return sorted(changed)


# --- the fetchers ------------------------------------------------------------------

def _load_credentials(scopes: list[str]):
    from google.oauth2 import service_account
    if not os.path.exists(KEY):
        raise Misconfigured(f"no key at {KEY} (set CORPUS_GOOGLE_KEY)")
    try:
        return service_account.Credentials.from_service_account_file(KEY, scopes=scopes)
    except (ValueError, OSError) as e:
        raise Misconfigured(f"key at {KEY} unreadable: {type(e).__name__}") from None


def fetch_ga(start: dt.date, end: dt.date) -> dict[tuple[str, str], dict[str, int]]:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
    from google.api_core import exceptions as gexc

    client = BetaAnalyticsDataClient(credentials=_load_credentials(
        ["https://www.googleapis.com/auth/analytics.readonly"]))
    out: dict[tuple[str, str], dict[str, int]] = {}
    offset, limit = 0, 100_000
    while True:
        try:
            r = client.run_report(RunReportRequest(
                property=GA_PROPERTY,
                dimensions=[Dimension(name="date"), Dimension(name="hostName")],
                metrics=[Metric(name="screenPageViews"), Metric(name="totalUsers"),
                         Metric(name="sessions")],
                date_ranges=[DateRange(start_date=start.isoformat(), end_date=end.isoformat())],
                limit=limit, offset=offset))
        except (gexc.PermissionDenied, gexc.Unauthenticated) as e:
            raise Misconfigured(f"permission denied: {e.message}") from None
        for row in r.rows:
            raw, host = (v.value for v in row.dimension_values)
            if fold_host(host) is None:
                continue
            d = f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"
            acc = out.setdefault((d, fold_host(host)), {c: 0 for c in COLS["ga"]})
            for c, m in zip(COLS["ga"], row.metric_values):
                acc[c] += int(m.value)
        offset += len(r.rows)
        if not r.rows or offset >= r.row_count:
            return out


def fetch_sc(start: dt.date, end: dt.date) -> dict[tuple[str, str], dict[str, int]]:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    sc = build("searchconsole", "v1", cache_discovery=False, credentials=_load_credentials(
        ["https://www.googleapis.com/auth/webmasters.readonly"]))
    acc: dict[tuple[str, str], dict[str, float]] = {}
    start_row, page = 0, 25_000
    while True:
        try:
            r = sc.searchanalytics().query(siteUrl=SC_SITE, body={
                "startDate": start.isoformat(), "endDate": end.isoformat(),
                "dimensions": ["date", "page"], "dataState": "all",
                "rowLimit": page, "startRow": start_row}).execute()
        except HttpError as e:
            if e.resp.status in (401, 403):
                raise Misconfigured(f"permission denied: HTTP {e.resp.status}") from None
            raise
        rows = r.get("rows", [])
        for row in rows:
            d, url = row["keys"]
            if fold_host(urlsplit(url).hostname) is None:
                continue
            a = acc.setdefault((d, fold_host(urlsplit(url).hostname)), {"clicks": 0, "impressions": 0})
            a["clicks"] += row.get("clicks", 0)
            a["impressions"] += row.get("impressions", 0)
        start_row += len(rows)
        if len(rows) < page:
            return {k: {c: int(round(v)) for c, v in a.items()} for k, a in acc.items()}


FETCHERS = {"ga": fetch_ga, "sc": fetch_sc}


# --- the run -----------------------------------------------------------------------

def summary(table, written: list[str], yesterday: dt.date, errors: dict[str, str]) -> str:
    parts = []
    if written:
        parts.append(f"{written[0]}..{written[-1]} written" if len(written) > 1
                     else f"{written[0]} written")
    else:
        parts.append("no values changed")
    y = yesterday.isoformat()
    per_host = []
    for h in HOSTS:
        row = table.get((y, h))
        if row:
            per_host.append(f"{SHORT[h]} {row['views'] or '-'} views / {row['clicks'] or '-'} clicks")
    if per_host:
        parts[-1] += f"; {yesterday.day} {yesterday:%b}: " + ", ".join(per_host)
    for source, err in errors.items():
        parts.append(f"{NAME[source]} FAILED: {err}")
    return "; ".join(parts)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="print the rows, write nothing")
    ap.add_argument("--since", type=dt.date.fromisoformat, help="re-fetch from this date")
    args = ap.parse_args(argv)

    yesterday = dt.date.today() - dt.timedelta(days=1)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    before = read_table(TABLE)
    table = {k: dict(v) for k, v in before.items()}

    written: set[str] = set()
    errors: dict[str, str] = {}
    misconfigured = False
    for source, fetch in FETCHERS.items():
        start = fetch_start(table, source, yesterday, args.since)
        if start is None:
            continue
        try:
            got = fetch(start, yesterday)
        except Misconfigured as e:
            errors[source], misconfigured = str(e), True
            continue
        except Exception as e:  # one source failing never fails the other
            errors[source] = f"{type(e).__name__}: {str(e)[:200]}"
            continue
        written.update(merge(table, source, start, yesterday, got, now))

    text = render_table(table)
    if args.dry_run:
        for key in sorted(table):
            if table[key] != before.get(key):
                print(",".join(table[key][f] for f in FIELDS))
    elif table != before:
        write_table(TABLE, text)
    print(summary(table, sorted(written), yesterday, errors))
    return 2 if misconfigured else 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
