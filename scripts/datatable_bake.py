#!/usr/bin/env python3
"""datatable_bake.py — the first rows of a table, written into the page at build.

`site/assets/js/datatable.js` draws a table in the browser from the CSV its `data-src`
names, so until that file lands the page shows nothing, and with JavaScript off it never
shows anything. This writes the first `PAGE` rows into the page, in the table's opening
sort, as the catalogue's first screen is written *(strategic review of 2026-10-01, R116)*.
The script replaces the block with its own table once the CSV has arrived.

**Every builder that writes a `dl-datatable` passes its page through `bake()`**, last, after
`external_links()`. It reads everything from the container's own `data-*` attributes — the
same contract the script reads — so a builder states a table once.

**This is a port, and the script is the original.** Which rows come first, what a cell
shows and how wide a column is are decided in `datatable.js`; the functions here follow it
name for name (`display`, `cellHtml`, `compare`, `columnWidth`) and are to be changed
when it changes. Two things are approximate by nature: text order, where the browser
collates by locale and this folds case and accents; and widths, where the browser measures
type on a canvas and this counts characters, as the script itself does without a canvas.
`prototypes/datatable-test.mjs` holds the rows written here to the rows the script draws.

**The CSV is the one the page links.** A dated edition is not kept in the tree, so
`editions.publish` remembers the bytes it was given and `bake()` reads them from there.
A table whose CSV can be read from neither stops the build.
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
import unicodedata
from functools import cmp_to_key
from html.parser import HTMLParser
from pathlib import Path

import editions
from chrome_lib import external_links

PAGE = 100                 # datatable.js `PAGE`
ZWSP = "​"
LINES, MIN_W, MAX_W = 3, 66, 500
CELL_PX, NUM_PX, HEAD_PX = 14.04, 12.96, 12.06     # 0.78, 0.72 and 0.67rem at 18px
PAD = 21.6                                         # 0.6rem either side

_OPEN = re.compile(r'<div class="dl-datatable"[^>]*>')
_NOSCRIPT = re.compile(r"<noscript>.*?</noscript>", re.S)
_NUM = re.compile(r"^\s*[+-]?(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)")
_PLAIN_NUMBER = re.compile(r"^-?\d+(\.\d+)?$")


class _Attrs(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.attrs: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        if not self.attrs:
            self.attrs = {k: v or "" for k, v in attrs}


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def norm(s: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[\s\-/]+", "_", str(s).lower())).strip("_")


def names(attr: str | None) -> list[str]:
    return [s.strip() for s in (attr or "").split(",") if s.strip()]


def num_of(v: str) -> float | None:
    """`parseFloat` over the value with commas and spaces out: the leading number, or none."""
    m = _NUM.match(re.sub(r"[, ]", "", v or ""))
    return float(m.group(0)) if m else None


def dewiki(s: str) -> str:
    if "[[" not in s:
        return s
    return re.sub(r"\[\[([^\]]+)\]\]", r"\1", re.sub(r"\[\[[^\]|]*\|([^\]]+)\]\]", r"\1", s))


def thousands(v: str) -> str:
    """`Number(v).toLocaleString('en-US')`: grouped, and at most three decimal places."""
    s = f"{round(float(v), 3):,.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def link_cell(url: str) -> str:
    label = re.sub(r"/$", "", re.sub(r"^https?://", "", url))
    if len(label) > 64:
        label = label[:63] + "…"
    return (f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer" '
            f'title="{esc(url)}">{esc(label)}</a>')


def collation_key(s: str) -> tuple:
    """Near enough to `localeCompare(…, {numeric: true})` for names and codes: accents and
    case set aside, and a run of digits read as a number."""
    base = "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
    parts = re.split(r"(\d+)", base.casefold())
    return tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in parts if p != "")


def parse(raw: bytes) -> tuple[list[str], list[list[str]]]:
    """Headers and records as the script reads them: cells trimmed, empty records dropped."""
    records = [[c.strip() for c in r]
               for r in csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""))]
    if not records:
        return [], []
    width = len(records[0])
    return records[0], [r + [""] * (width - len(r)) for r in records[1:] if any(r)]


def _lines_at(widths: list[float], space: float, width: float) -> int:
    lines, x = 1, 0.0
    for w in widths:
        if x > 0 and x + space + w <= width:
            x += space + w
            continue
        if x > 0:
            lines, x = lines + 1, 0.0
        while w > width:
            w -= width
            lines += 1
        x = w
    return lines


def column_width(header: str, values: list[str], px: float, break_anywhere: bool) -> int:
    """`columnWidth`: the narrowest width at which every sampled cell fits in three lines,
    floored by the longest word in the header and in the data."""
    def m(s: str) -> float:
        return len(s) * px * 0.52

    head_min = max((len(w) for w in re.split(r"[\s/]+", header.replace("_", " "))), default=0) \
        * HEAD_PX * 0.52 + 18
    step = max(1, math.ceil(len(values) / 400))
    cells = [[m(w) for w in v.split()] for v in values[::step] if v]

    word_floor = 0.0
    if not break_anywhere:
        longest = max((len(w) for v in values if v for w in re.split(r"[\s/]+", v)), default=0)
        word_floor = longest * px * 0.52 + 1
    if not cells:
        return math.ceil(max(MIN_W, head_min) + PAD)

    def fits(width: float) -> bool:
        return all(_lines_at(c, m(" "), width) <= LINES for c in cells)

    lo, hi = float(MIN_W), float(MAX_W)
    if fits(hi):
        for _ in range(9):
            if hi - lo <= 4:
                break
            mid = (lo + hi) / 2
            if fits(mid):
                hi = mid
            else:
                lo = mid
    return math.ceil(min(MAX_W, max(hi, head_min, word_floor, MIN_W)) + PAD)


def _json(attr: str | None) -> dict:
    try:
        return json.loads(attr) if attr else {}
    except ValueError:
        return {}


def table_html(a: dict[str, str], headers: list[str], rows: list[list[str]]) -> str:
    """The first PAGE rows in the opening sort, as a table the stylesheet already knows."""
    index: dict[str, int] = {}
    for i, h in enumerate(headers):
        index.setdefault(norm(h), i)

    def find(name: str) -> int:
        return index.get(norm(name), -1)

    wanted = names(a.get("data-cols"))
    cols = [i for i in (find(c) for c in wanted) if i > -1] if wanted else list(range(len(headers)))
    numeric = {i for i in (find(c) for c in names(a.get("data-numeric"))) if i > -1}
    links = {i for i in (find(c) for c in names(a.get("data-links"))) if i > -1}
    grouped = {i for i in (find(c) for c in names(a.get("data-thousands"))) if i > -1}
    labels = {find(c): m for c, m in _json(a.get("data-labels")).items() if find(c) > -1}
    badges = {find(c): m for c, m in _json(a.get("data-badges")).items() if find(c) > -1}

    def display(ci: int, v: str) -> str:
        if ci in grouped and _PLAIN_NUMBER.match(v):
            return thousands(v)
        return dewiki(labels.get(ci, {}).get(v) or v)

    def cell(ci: int, v: str) -> str:
        if not v:
            return ""
        if ci in links:
            return link_cell(v)
        shown = display(ci, v)
        tone = badges.get(ci, {}).get(v) or badges.get(ci, {}).get(shown)
        if tone:
            return f'<span class="dt-badge dt-badge--{esc(tone)}">{esc(shown)}</span>'
        return f'<span class="dt-cell">{esc(shown)}</span>'

    # The opening sort. One key, blanks last in either direction, ties in file order.
    sort_vi, asc = -1, True
    bits = (a.get("data-sort") or "").split(":")
    if bits[0] and find(bits[0]) in cols:
        sort_vi, asc = cols.index(find(bits[0])), (len(bits) < 2 or bits[1] != "desc")
    ordered = rows
    if sort_vi > -1:
        ci = cols[sort_vi]

        def compare(x: list[str], y: list[str]) -> int:
            av, bv = x[ci], y[ci]
            if not av or not bv:
                return (not av) - (not bv)
            if ci in numeric:
                p, q = num_of(av) or 0.0, num_of(bv) or 0.0
            else:
                p, q = collation_key(display(ci, av)), collation_key(display(ci, bv))
            c = (p > q) - (p < q)
            return c if asc else -c

        ordered = sorted(rows, key=cmp_to_key(compare))

    floor = float(a.get("data-min-col-width") or 0)
    widths = [max(column_width(headers[ci], [display(ci, r[ci]) for r in rows],
                               NUM_PX * 0.6 / 0.52 if ci in numeric else CELL_PX, ci in links),
                  math.ceil(floor)) for ci in cols]

    head = []
    for vi, ci in enumerate(cols):
        cls = (["num"] if ci in numeric else []) \
            + ([("sort-asc" if asc else "sort-desc")] if vi == sort_vi else [])
        head.append(f'<th{" class=" + chr(34) + " ".join(cls) + chr(34) if cls else ""}>'
                    + esc(headers[ci]).replace("_", "_" + ZWSP) + "</th>")
    body = []
    for r in ordered[:PAGE]:
        body.append("<tr>" + "".join(
            f'<td{" class=" + chr(34) + "num" + chr(34) if ci in numeric else ""}>{cell(ci, r[ci])}</td>'
            for ci in cols) + "</tr>")
    return (f'<div class="dt-baked"><table class="data-table" style="width:{sum(widths)}px">'
            "<colgroup>" + "".join(f'<col style="width:{w}px">' for w in widths) + "</colgroup>"
            "<thead><tr>" + "".join(head) + "</tr></thead>\n<tbody>\n"
            + "\n".join(body) + "\n</tbody></table></div>")


def table_page(page_dir: Path, html: str) -> str:
    """What a builder writes for a page carrying a table: `external_links()`, then `bake()`."""
    return bake(external_links(html), page_dir)


def bake(html: str, page_dir: Path) -> str:
    """`html` with the first rows of its table written in, and a `<noscript>` that says so.
    A page carrying no table comes back as it went in."""
    opening = _OPEN.search(html)
    if opening is None:
        return html
    p = _Attrs()
    p.feed(opening.group(0))
    a = p.attrs
    name = a["data-src"].split("?")[0]
    path = (page_dir / name).resolve()
    raw = path.read_bytes() if path.is_file() else editions.PUBLISHED.get(path)
    if raw is None:
        raise SystemExit(f"datatable_bake: {page_dir.name}/{name} is in neither the tree nor "
                         f"this run's published editions — the table cannot be written")
    headers, rows = parse(raw)

    note = (f"The first {PAGE} of {len(rows):,} rows. " if len(rows) > PAGE
            else "Sorting and filters need JavaScript. ")
    block = (f'<noscript>\n        <p>{note}<a href="{esc(name)}">Download the CSV</a> '
             f'for every row and field.</p>\n      </noscript>\n      '
             + table_html(a, headers, rows))
    noscript = _NOSCRIPT.search(html, opening.end())
    if noscript is None:
        raise SystemExit(f"datatable_bake: {page_dir.name}: the table carries no <noscript> to replace")
    return html[:noscript.start()] + block + html[noscript.end():]
