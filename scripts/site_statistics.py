#!/usr/bin/env python3
"""site_statistics.py — the charts and tables of `/methodology/statistics/` (Bill, 2026-11-23).

`documentation/site-statistics.md` is the specification. `content/statistics.md` is the page and
places each block with `<!-- stat: name -->`; `fill()` swaps each for HTML at build time, so the
page needs no script. A directive with no block, or a missing source, stops the build.

Acquisitions are `ingested` dates in `raw-catalogue.json`, which begin in July 2026. The monthly
chart keeps all 12 months and draws those before the first as gaps, never zeros; the six-month
tables start at the first month held. A document
tagged to several countries or topics counts once under each. Regional codes (`X..`) are left out
of the country tables.

Weekly site figures come from the daily `site-analytics-access.csv`, because `-pages.csv` holds
months only. Weeks run Monday to Sunday and only complete weeks are drawn. A week's users is the
sum of its daily users, so someone returning on a second day counts twice.
"""
from __future__ import annotations

import collections
import csv
import json
import os
import re
from datetime import date, timedelta
from html import escape
from pathlib import Path

from status_lib import EXCHANGE

CORPUS = Path(__file__).resolve().parent.parent
CATALOGUE = CORPUS / "outputs" / "catalogue" / "raw-catalogue.json"
ACCESS = CORPUS / "logs" / "site-analytics-access.csv"
SITE_COUNTRIES = CORPUS / "logs" / "site-analytics-countries.csv"
COUNTRIES = CORPUS / "lookups" / "countries.csv"
TAXONOMY = CORPUS / "lookups" / "taxonomy.csv"
CITATIONS = Path(EXCHANGE) / "citations.csv"

SITE_START = date(2026, 10, 1)     # the specification's "starting Oct 2026"
TOP = 15
RECENT_CITATIONS = 10
WEEKS = 26
DIRECTIVE = re.compile(r"^<!--\s*stat:\s*([\w-]+)\s*-->\s*$", re.M)


def rows_of(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def month_label(ym: str, year: bool = True) -> str:
    d = date(int(ym[:4]), int(ym[5:7]), 1)
    return d.strftime("%b %Y" if year else "%b")


def last_months(end: str, n: int) -> list[str]:
    y, m = int(end[:4]), int(end[5:7])
    out = []
    for _ in range(n):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return out[::-1]


def nice_ticks(top: int) -> list[int]:
    """Round gridlines from zero, at least two above it, none above the tallest bar."""
    if top <= 0:
        return [0]
    step = 10 ** (len(str(top)) - 1)
    if top / step < 2 and step > 1:
        step //= 2
    return list(range(0, top + 1, step))


def bar_chart(bars: list[tuple[str, str, int | None]], label: str) -> str:
    """`bars` is (axis label or "", tooltip name, value), in order. A value of None is a period
    with no record, drawn as a gap and never as a zero."""
    held = [v for _, _, v in bars if v is not None]
    if not held:
        raise SystemExit(f"site_statistics: nothing to draw for {label!r}.")
    ticks = nice_ticks(max(held))
    scale = max(max(held), ticks[-1], 1)
    grid = "".join(f'<span class="stat-tick" style="bottom:{t / scale * 100:.2f}%"><b>{t:,}</b></span>'
                   for t in ticks)
    show = len(bars) <= 12
    said = lambda v: "no record" if v is None else f"{v:,}"
    cols = "".join(
        f'<div class="stat-col" title="{escape(name)}: {said(v)}">'
        + ("" if v is None else
           f'<div class="stat-bar" style="height:{v / scale * 100:.2f}%">'
           + (f'<span class="stat-val">{v:,}</span>' if show else "") + "</div>")
        + "</div>"
        for _, name, v in bars)
    axis = "".join(f'<span>{escape(a)}</span>' for a, _, _ in bars)
    summary = "; ".join(f"{name}: {said(v)}" for _, name, v in bars)
    return (f'<figure class="stat-chart" role="img" aria-label="{escape(label)}. {escape(summary)}">'
            f'<div class="stat-plot">{grid}<div class="stat-bars">{cols}</div></div>'
            f'<div class="stat-axis">{axis}</div></figure>')


def month_table(first: str, rows: list[tuple[str, dict]], months: list[str]) -> str:
    """The top rows by window total, busiest first, a column a month."""
    ranked = sorted(((name, c) for name, c in rows if sum(c.get(m, 0) for m in months)),
                    key=lambda r: (-sum(r[1].get(m, 0) for m in months), r[0]))[:TOP]
    head = '<th class="num">Total</th>' + "".join(f'<th class="num">{month_label(m)}</th>' for m in months)
    body = "".join(
        f'<tr><td>{escape(name)}</td><td class="num stat-total">{sum(c.get(m, 0) for m in months):,}</td>'
        + "".join(f'<td class="num">{c.get(m, 0):,}</td>' for m in months) + "</tr>"
        for name, c in ranked)
    return (f'<div class="stat-table"><table><thead><tr><th>{first}</th>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def to_date(day: str) -> str:
    d = date.fromisoformat(day)
    return f'<p class="stat-note">{d.strftime("%B")} to the {d.day}{ordinal(d.day)}.</p>'


def ordinal(n: int) -> str:
    return "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


class Data:
    """Each source read once, and only if a block on the page asks for it."""

    def __init__(self):
        self._items = None
        self._access = None

    @property
    def items(self) -> list[dict]:
        if self._items is None:
            d = json.load(open(CATALOGUE, encoding="utf-8"))
            all_items = d["items"] if isinstance(d, dict) and "items" in d else d
            self._items = [i for i in all_items if i.get("ingested")]
        return self._items

    @property
    def access(self) -> dict[date, tuple[int, int]]:
        if self._access is None:
            self._access = {date.fromisoformat(r["Date"]): (int(r["Users"]), int(r["Pages"]))
                            for r in rows_of(ACCESS)}
        return self._access

    def window(self, n: int) -> list[str]:
        held = sorted({i["ingested"][:7] for i in self.items})
        return [m for m in last_months(held[-1], n) if m >= held[0]]

    def last_ingest(self) -> str:
        return max(i["ingested"] for i in self.items)

    def tally(self, field: str, names: dict[str, str]) -> list[tuple[str, dict]]:
        out: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        for i in self.items:
            for key in set(i.get(field) or []):
                if key in names:
                    out[names[key]][i["ingested"][:7]] += 1
        return list(out.items())


def country_names() -> dict[str, str]:
    return {r["iso-3"]: r["country-name"] for r in rows_of(COUNTRIES) if not r["iso-3"].startswith("X")}


def monthly(data: Data) -> str:
    n = collections.Counter(i["ingested"][:7] for i in data.items)
    first = min(n)
    bars = [(month_label(m, False), month_label(m), n[m] if m >= first else None)
            for m in last_months(max(n), 12)]
    note = "" if bars[0][2] is not None else (
        f'<p class="stat-note">Acquisition dates begin in {date(int(first[:4]), int(first[5:7]), 1).strftime("%B %Y")}.</p>')
    return bar_chart(bars, "Documents acquired each month") + to_date(data.last_ingest()) + note


def acquired_countries(data: Data) -> str:
    return month_table("Country", data.tally("places", country_names()), data.window(6))


def acquired_topics(data: Data) -> str:
    names = {r["Key"]: r["Level 2"] for r in rows_of(TAXONOMY)}
    return month_table("Topic", data.tally("topics", names), data.window(6))


def weekly(data: Data, column: int, label: str) -> str:
    last = max(data.access)
    start = SITE_START + timedelta(days=(7 - SITE_START.weekday()) % 7)
    weeks, monday = [], start
    while monday + timedelta(days=6) <= last:
        days = [monday + timedelta(days=k) for k in range(7)]
        weeks.append((monday, sum(data.access[d][column] for d in days if d in data.access)))
        monday += timedelta(days=7)
    weeks = weeks[-WEEKS:]
    seen, bars = set(), []
    for m, v in weeks:
        ym = m.strftime("%Y-%m")
        bars.append((m.strftime("%b") if ym not in seen else "",
                     f"Week of {m.day} {m.strftime('%b %Y')}", v))
        seen.add(ym)
    return bar_chart(bars, label)


def site_users(data: Data) -> str:
    return weekly(data, 0, "Site users each week")


def site_pages(data: Data) -> str:
    return weekly(data, 1, "Pages viewed each week")


def site_countries(data: Data) -> str:
    rows = rows_of(SITE_COUNTRIES)
    held = [c for c in rows[0] if re.fullmatch(r"\d{4}-\d{2}", c)]
    months = [m for m in held if m >= SITE_START.strftime("%Y-%m")][-6:]
    names = country_names()
    table = [(names[r["iso-3"]], {m: int(r[m] or 0) for m in months})
             for r in rows if r["iso-3"] in names]
    return month_table("Country", table, months) + to_date(max(data.access).isoformat())


def citations(data: Data) -> str:
    rows = sorted(rows_of(CITATIONS), key=lambda r: r["Date"], reverse=True)[:RECENT_CITATIONS]
    def link(u: str) -> str:
        u = u.strip()
        return f'<a href="{escape(u, quote=True)}">{escape(u)}</a>' if u.startswith(("http://", "https://")) else escape(u)
    body = "".join(f'<tr><td class="stat-date">{escape(r["Date"])}</td><td>{escape(r["Title"])}</td>'
                   f'<td>{escape(r["Author"])}</td><td class="stat-url">{link(r["u.r.l"])}</td></tr>'
                   for r in rows)
    return ('<div class="stat-table stat-table--citations"><table><thead><tr><th>Date</th><th>Title</th>'
            f"<th>Author</th><th>URL</th></tr></thead><tbody>{body}</tbody></table></div>")


BLOCKS = {"monthly": monthly, "acquired-countries": acquired_countries,
          "acquired-topics": acquired_topics, "site-users": site_users, "site-pages": site_pages,
          "site-countries": site_countries, "citations": citations}


def fill(text: str) -> str:
    data = Data()
    def block(m: re.Match) -> str:
        name = m.group(1)
        if name not in BLOCKS:
            raise SystemExit(f"site_statistics: no block {name!r}.")
        return BLOCKS[name](data)
    return DIRECTIVE.sub(block, text)
