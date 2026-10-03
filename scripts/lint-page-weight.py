#!/usr/bin/env python3
"""lint-page-weight.py — what each table page costs a reader's browser, against the size rule.

RENDER Step 7, before the push. A table page is one carrying a `dl-datatable` with a
`data-src`; `site/assets/js/datatable.js` draws it in the browser from that CSV. For each
one this measures three things, appends them to `logs/page-weight.csv`, and fails at the
thresholds Bill ruled *(strategic review of 2026-10-01, R110)*:

- **Elements at first draw: 3,000.** The table draws 100 rows at a time, so this is the
  page's own markup, the table's frame and filters, and 100 rows.
- **The table's data file, compressed: 2 MB.** Past it the answer is the catalogue's split:
  the shown columns up front, the detail columns fetched when a row is opened.
- **100,000 rows, or 5 MB compressed: a query service.** Named so it is not decided in a hurry.

It also fails a page whose table is not written into it: `datatable_bake.py` puts the first
100 rows in every table page at build (R116), and a page without them is blank until its
CSV lands.

**The element count is a ceiling, not a simulation.** A drawn row costs a `<tr>`, a caret
cell, a `<td>` a column and one more element for each cell that holds something. Which 100
rows come first depends on the sort, and the sort is the reader's; so the rows counted are
the 100 fullest in the file, and no ordering draws more. `prototypes/datatable-test.mjs`
counts the real thing in jsdom on five pages; jsdom reads a `<noscript>`'s contents as
elements where a browser does not, so its figure can sit two or three above this one.

**A dated edition is not in the tree** — it lives in R2 — so a CSV the tree does not hold
is fetched from the live site. A page whose CSV can be read from neither is reported and
exits 2: not measured is not the same as within the rule.

    python scripts/lint-page-weight.py            # 0 clean · 1 over a threshold · 2 could not measure
    python scripts/lint-page-weight.py --no-log   # measure and report, write nothing
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import re
import sys
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
SITE = CORPUS / "site"
LOG = CORPUS / "logs" / "page-weight.csv"
SITE_BASE = "https://corpus.data-landscapers.io"

PAGE = 100                       # rows datatable.js draws at first — its `PAGE`
MAX_ELEMENTS = 3_000
MAX_GZ = 2 * 1024 * 1024
SERVICE_ROWS = 100_000
SERVICE_GZ = 5 * 1024 * 1024

FIELDS = ["date", "page", "rows", "bytes_gz", "elements"]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "source", "track", "wbr"}


class _Page(HTMLParser):
    """Counts the elements a browser with scripting on builds from the page as served, and
    keeps the table's attributes. What sits inside `<noscript>` is text to such a browser,
    not elements, and is left out. So is the `.dt-baked` block — the first rows, written at
    build by `datatable_bake.py` — because the script puts its own table in that block's
    place: the two are never on the page together, and the script's is the larger."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements = 0
        self.table: dict[str, str] | None = None
        self.has_controls = False
        self.baked_rows = 0
        self._noscript = 0
        self._baked = False          # inside `.dt-baked`, which holds a table and no <div>

    def handle_starttag(self, tag, attrs):
        if tag == "noscript":
            self.elements += 1
            self._noscript += 1
            return
        if self._noscript:
            return
        if self._baked:
            self.baked_rows += tag == "tr"
            return
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if "dt-baked" in classes:
            self._baked = True
            return
        self.elements += 1
        if "dl-datatable" in classes and a.get("data-src") and self.table is None:
            self.table = {k: v or "" for k, v in a.items()}
        if "dt-controls" in classes:
            self.has_controls = True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "noscript" and self._noscript:
            self._noscript -= 1
        elif tag == "div" and self._baked:
            self._baked = False


def _norm(s: str) -> str:
    """`norm()` in datatable.js: how a name in `data-cols` is matched to a CSV header."""
    return re.sub(r"_+", "_", re.sub(r"[\s\-/]+", "_", s.lower())).strip("_")


def _names(attr: str | None) -> list[str]:
    return [s.strip() for s in (attr or "").split(",") if s.strip()]


def table_elements(table: dict[str, str], has_controls: bool,
                   headers: list[str], rows: list[list[str]]) -> int:
    """The most elements datatable.js adds to the page at first draw, over any sort."""
    index = {_norm(h): i for i, h in reversed(list(enumerate(headers)))}
    wanted = _names(table.get("data-cols"))
    cols = [index[_norm(c)] for c in wanted if _norm(c) in index] if wanted \
        else list(range(len(headers)))
    n = len(cols)

    # The frame: two tables sharing a colgroup, the scrollbar mirror, the "more" control.
    total = 15 + 3 * (n + 1)
    # The toolbar, where the page supplies none: the bar, a count, a title, the downloads.
    if not has_controls:
        total += 2 + sum(1 for k in ("data-title", "data-src", "data-full-src",
                                     "data-metadata-src") if table.get(k))
    # A filter is drawn only where its column holds two values or more.
    for c in _names(table.get("data-filters")):
        if _norm(c) not in index:
            continue
        ci = index[_norm(c)]
        values = {r[ci] for r in rows if ci < len(r) and r[ci]}
        if len(values) >= 2:
            total += 2 + len(values)
    total += 1                                                  # the search box

    if not rows:
        return total + 2                                        # the "nothing matches" row
    filled = sorted((sum(1 for ci in cols if ci < len(r) and r[ci]) for r in rows),
                    reverse=True)[:PAGE]
    return total + len(filled) * (2 + n) + sum(filled)


def read_csv(page: Path, src: str) -> bytes | None:
    """The bytes a page's `data-src` names: the tree's copy, else the live site's."""
    name = src.split("?")[0]
    local = (page.parent / name).resolve()
    if local.is_file():
        return local.read_bytes()
    rel = local.relative_to(SITE.resolve()).as_posix()
    try:
        req = urllib.request.Request(f"{SITE_BASE}/{rel}", headers={"User-Agent": "corpus-lint-page-weight"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()
    except Exception:
        return None


def parse(raw: bytes) -> tuple[list[str], list[list[str]]]:
    """Headers and records as datatable.js reads them: cells trimmed, empty records dropped."""
    text = raw.decode("utf-8-sig")
    records = [[c.strip() for c in r] for r in csv.reader(io.StringIO(text, newline=""))]
    if not records:
        return [], []
    return records[0], [r for r in records[1:] if any(r)]


def measure(page: Path) -> dict | None:
    """One page's row, or None where the page carries no table. `rows` is None where the
    CSV could not be read."""
    p = _Page()
    p.feed(page.read_text(encoding="utf-8"))
    if p.table is None:
        return None
    out = {"page": page.relative_to(SITE).as_posix(), "rows": None, "bytes_gz": None,
           "elements": None, "baked": p.baked_rows - 1}       # less the header row
    raw = read_csv(page, p.table["data-src"])
    if raw is None:
        return out
    headers, rows = parse(raw)
    out["rows"] = len(rows)
    out["bytes_gz"] = len(gzip.compress(raw, 6))
    out["elements"] = p.elements + table_elements(p.table, p.has_controls, headers, rows)
    return out


def findings(m: dict) -> list[str]:
    out = []
    if "baked" in m and m["baked"] != min(PAGE, m["rows"]):
        out.append(f"{m['page']}: {max(m['baked'], 0)} rows written into the page, "
                   f"where the table's first draw is {min(PAGE, m['rows'])}")
    if m["elements"] > MAX_ELEMENTS:
        out.append(f"{m['page']}: {m['elements']:,} elements at first draw, over {MAX_ELEMENTS:,}")
    if m["rows"] >= SERVICE_ROWS or m["bytes_gz"] > SERVICE_GZ:
        out.append(f"{m['page']}: {m['rows']:,} rows, {m['bytes_gz']:,} bytes compressed — "
                   f"past {SERVICE_ROWS:,} rows or 5 MB, a query service")
    elif m["bytes_gz"] > MAX_GZ:
        out.append(f"{m['page']}: data file {m['bytes_gz']:,} bytes compressed, over 2 MB — "
                   f"split the shown columns from the detail")
    return out


def write_log(measured: list[dict], today: str) -> None:
    """Append today's measures. A second run in a day replaces the first, so the file holds
    one row a page a day."""
    kept = []
    if LOG.exists():
        with LOG.open(encoding="utf-8", newline="") as f:
            kept = [r for r in csv.DictReader(f) if r["date"] != today]
    with LOG.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, FIELDS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(kept)
        w.writerows({"date": today, **m} for m in measured)


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure every table page against the size rule.")
    ap.add_argument("--no-log", action="store_true", help="measure and report, write nothing")
    a = ap.parse_args()

    measured, unread, found = [], [], []
    for page in sorted(SITE.rglob("*.html")):
        if 'data-src="' not in page.read_text(encoding="utf-8"):
            continue
        m = measure(page)
        if m is None:
            continue
        if m["rows"] is None:
            unread.append(m["page"])
            continue
        measured.append(m)
        found += findings(m)

    if not a.no_log and measured:
        write_log(measured, date.today().isoformat())

    if measured:
        top = max(measured, key=lambda m: m["elements"])
        big = max(measured, key=lambda m: m["bytes_gz"])
        print(f"lint-page-weight: {len(measured)} table pages; most elements {top['elements']:,} "
              f"({top['page']}); largest file {big['bytes_gz']:,} bytes compressed, "
              f"{big['rows']:,} rows ({big['page']})")
    for f in found:
        print(f"  FAIL  {f}")
    for u in unread:
        print(f"  NOT MEASURED  {u}: its CSV is in neither the tree nor the live site")
    if found:
        return 1
    if unread or not measured:
        return 2
    print("  ok — every table page is inside the size rule")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
