#!/usr/bin/env python3
"""progress.py — the two progress tables, `/progress/` and `/progress/countries/`.

    python scripts/progress.py  -> site/progress/index.html
                                   site/progress/countries/index.html

**The same numbers, read two ways.** Every country progress report answers one fixed
frame of 121 indicators, so the answers form a 54 x 121 grid with a value in every
cell. Counting it down the columns gives *for this indicator, how many countries came
out at each value*; counting it down the rows gives *for this country, how many
indicators*. Neither is a new finding — both are the same grid, tallied — which is
why the two pages are one builder and why the totals are asserted rather than
printed and hoped over: every topics row sums to 54 and every countries row to 121,
and a build where one does not has misread a report rather than found something.

**The grid is read out of the published reports, not out of `indicators.csv`.** The
per-country CSV beside each report carries the same values keyed by `indicator_id`
and would be easier to parse, but it holds only the rows that carry evidence — the
*No evidence* count would then be a subtraction this page performed rather than a
number a report states, and the page would be able to disagree with the report a
reader clicks through to. Parsing the markdown costs a table walk and buys the
property that these counts cannot drift from what is published.

Rows are keyed on the report's own `(Topic, Indicator)` pair against
`lookups/indicators.csv`, and the mapping is asserted total in both directions per
report: 121 pairs in, 121 matched, none left over. A renamed indicator therefore
stops the build here rather than quietly dropping a row out of a count.

**Zeros print, muted.** A blank cell in a count table reads as *not counted* rather
than *counted, none*, and 22% of the topics table is zero (Bill, 2026-09-10). The
grey is `progress.css`; the digit is always there.

**Region rows are labels, not links** (Bill, 2026-09-10). A region progress report
is a movement ledger over that region's own institutions on the `MOVEMENTS`
vocabulary and runs no indicator frame at all, so it carries none of the six counts
this table shows; linking the group header would send a reader from a count table to
a page that cannot answer the question the count raised. Topic rows do link, because
a topic progress report *is* the indicator frame for that topic.

Built in RENDER Step 4a, after Step 2 has written the topic progress reports these
link into and their per-indicator anchors — the same reason `topic-page.py` and
`region.py` run there. The anchors are checked, not assumed: a dead bookmark on the
site's most important page is a defect, so a missing report or missing `id` stops the
build with the list.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import markdown
from chrome_lib import chrome, external_links, foot, ga, script, styles  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
CONTENT_DIR = CORPUS / "content"
LOOKUPS = CORPUS / "lookups"
REPORTS = CORPUS / "outputs" / "reports"
SITE = CORPUS / "site"

SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

# The Progress vocabulary, in the order Bill asked these columns to run
# (2026-09-10): best to worst, then the frame's own answer last. That is not the
# order the reports' legend states them in, and deliberately — a legend defines,
# a table is read across.
COLUMNS = ["Movement", "Mixed", "No change", "Stalled", "Regressed", "No evidence"]

# Group headers only. XAF (all Africa), XSS (sub-Saharan) and XGL (global) are
# excluded because they contain the others: a country would be counted twice
# (Bill, 2026-09-10). The five that remain partition the 54 exactly, which
# `build_countries` asserts rather than trusts.
SKIP_REGIONS = {"XAF", "XSS", "XGL"}

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Data Landscapers</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
{styles}
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container">
    <header class="article-header">
      <h1 class="article-header__title">{h1}</h1>
    </header>

    <article class="article-body">
{body}
    </article>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Counted from</dt><dd>{counted}</dd>
        <dt>Text</dt><dd><code>{source}</code></dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>
  </div>
  </main>

{foot}

</div>
{script}
</body>
</html>
"""


# ---------------------------------------------------------------- the grid

def progress_rows(md_path: Path):
    """Every `(Topic, Indicator, value)` in a report's Progress tables.

    A progress report holds two kinds of table and only one of them is this one:
    the indicator frame ends in a `Progress` column, the ledger that shares the
    page ends in `Movement`. They share four of their six words, so keying on the
    header rather than on the values is what keeps a movement out of a progress
    count."""
    lines = md_path.read_text(encoding="utf-8").split("\n")
    i = 0
    while i < len(lines) - 1:
        rule = lines[i + 1].strip().strip("|").replace("|", "")
        if lines[i].startswith("|") and rule and set(rule) <= set("-: "):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            i += 2
            if header[-1] == "Progress":
                while i < len(lines) and lines[i].startswith("|"):
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    yield cells[0], cells[1], stem(cells[-1])
                    i += 1
            continue
        i += 1


def stem(value: str) -> str:
    """The value before its qualifying clause, with the emphasis taken off.

    Two things are stripped and neither is cosmetic. A value may carry a
    qualifying clause after a comma — *Advanced, regulations still pending* is an
    Advanced — and ***No evidence*** is published bold italic, which is markup
    around the word rather than part of it."""
    return value.split(",")[0].strip().strip("*").strip()


def load_indicators():
    """`lookups/indicators.csv`, in its own sort order, as the frame's spine."""
    rows = list(csv.DictReader((LOOKUPS / "indicators.csv").read_text(
        encoding="utf-8-sig").splitlines()))
    rows.sort(key=lambda r: (int(r["Topic Sort"]), int(r["Indicator Sort"])))
    return rows


def load_countries():
    """`lookups/countries.csv` — the 54 places and the five regions over them."""
    rows = list(csv.DictReader((LOOKUPS / "countries.csv").read_text(
        encoding="utf-8-sig").splitlines()))
    names = {r["iso-3"]: r["country-name"] for r in rows}
    region = {r["iso-3"]: r["Region"] for r in rows}
    return names, region


def read_grid(indicators):
    """`(iso, indicator_id) -> value` over every country progress report.

    Regions are skipped by having no Progress table at all rather than by name:
    their reports run a movement ledger, so `progress_rows` yields nothing for
    them and they drop out without a list to maintain."""
    pair_to_id = {(r["Topic"], r["Progress indicator"]): r["indicator_id"]
                  for r in indicators}
    grid, bad = {}, []
    for md in sorted(REPORTS.glob("*/*-progress.md")):
        iso = md.parent.name
        rows = list(progress_rows(md))
        if not rows:
            continue                      # a region ledger, not the frame
        seen = set()
        for topic, indicator, value in rows:
            key = pair_to_id.get((topic, indicator))
            if key is None:
                bad.append(f"{iso}: no indicator matches ({topic!r}, {indicator!r})")
                continue
            if value not in COLUMNS:
                bad.append(f"{iso}/{key}: value {value!r} is outside the vocabulary")
                continue
            grid[(iso, key)] = value
            seen.add(key)
        missing = {r["indicator_id"] for r in indicators} - seen
        if missing:
            bad.append(f"{iso}: {len(missing)} indicator(s) absent from the report, "
                       f"first {sorted(missing)[0]}")
    if bad:
        raise SystemExit("progress.py: the reports and the indicator frame disagree, "
                         "so a count would be wrong rather than short:\n  "
                         + "\n  ".join(bad[:20]))
    return grid


# ---------------------------------------------------------------- the tables

def cells(counts: Counter) -> str:
    """Six numeric cells. A zero prints and is greyed, never dropped."""
    return "".join(
        f'<td class="num{" zero" if not counts[c] else ""}">{counts[c]}</td>'
        for c in COLUMNS)


def head() -> str:
    cols = "".join(f'<th class="num">{c}</th>' for c in COLUMNS)
    return ('<table class="progress-table">\n<thead>\n'
            f'<tr><th class="rowhead">Topic / Indicator</th>{cols}</tr>\n'
            '</thead>\n<tbody>\n')


def group_row(label: str, href: str | None) -> str:
    """A bold-caps band across the table. The rest of the row is blank by
    instruction (Bill, 2026-09-10) — the band names what follows it, and a total
    on it would compete with the numbers it introduces."""
    inner = f'<a href="{href}">{label}</a>' if href else label
    blanks = '<td class="num"></td>' * len(COLUMNS)
    return f'<tr class="group"><th scope="rowgroup">{inner}</th>{blanks}</tr>\n'


def topics_table(indicators, grid) -> str:
    """One row per topic, then one per indicator under it, counted over places."""
    per_indicator = defaultdict(Counter)
    for (_iso, iid), value in grid.items():
        per_indicator[iid][value] += 1

    places = len({iso for iso, _ in grid})
    out = [head()]
    current = None
    for row in indicators:
        topic_key, anchor = row["indicator_id"].split("--", 1)
        slug = topic_key.replace(".", "-")
        if topic_key != current:
            current = topic_key
            out.append(group_row(row["Topic"].upper(),
                                 f"../topics/{slug}/{slug}-progress.html"))
        counts = per_indicator[row["indicator_id"]]
        total = sum(counts.values())
        if total != places:
            raise SystemExit(
                f"progress.py: {row['indicator_id']} is answered by {total} reports, "
                f"not {places} — every country answers every indicator, so a row "
                f"that does not sum to the place count has lost or doubled one.")
        out.append(
            f'<tr><td class="rowhead indicator">'
            f'<a href="../topics/{slug}/{slug}-progress.html#{anchor}">'
            f'{row["Progress indicator"]}</a></td>{cells(counts)}</tr>\n')
    out.append("</tbody>\n</table>\n")
    return "".join(out)


def countries_table(indicators, grid, names, region) -> str:
    """One row per region, then one per country in it, counted over indicators."""
    per_country = defaultdict(Counter)
    for (iso, _iid), value in grid.items():
        per_country[iso][value] += 1

    frame = len(indicators)
    rows = sorted(per_country,
                  key=lambda iso: (names[region[iso]], names[iso]))
    out = [head().replace("Topic / Indicator", "Region / Country")]
    current = None
    for iso in rows:
        if region[iso] in SKIP_REGIONS:
            raise SystemExit(
                f"progress.py: {iso} sits directly under {region[iso]}, which this "
                f"page excludes as a container of the others — it would appear "
                f"under no region at all.")
        if region[iso] != current:
            current = region[iso]
            out.append(group_row(names[current].upper(), None))
        counts = per_country[iso]
        total = sum(counts.values())
        if total != frame:
            raise SystemExit(
                f"progress.py: {iso} answers {total} indicators, not {frame} — the "
                f"frame is fixed, so a report that does not fill it has lost a row.")
        out.append(
            f'<tr><td class="rowhead country">'
            f'<a href="../../reports/{iso}/{iso}-progress.html">{names[iso]}</a>'
            f'</td>{cells(counts)}</tr>\n')
    out.append("</tbody>\n</table>\n")
    return "".join(out)


# ---------------------------------------------------------------- the pages

def toc(current: str) -> str:
    """TOPICS · COUNTRIES, the site's `.article-toc` idiom. The page one is on is
    still a link and points at itself — `.article-toc a` styles everything in the
    bar, so a plain word sitting in it would come out as body type beside mono
    (`methodology.py` → `toc_bar` learned this first). `aria-current` is what says
    which one you are on, to a reader and to a screen reader alike."""
    items = [("Topics", "./" if current == "topics" else "../"),
             ("Countries", "countries/" if current == "topics" else "./")]
    sep = '\n<span class="article-toc__sep" aria-hidden="true">&middot;</span>\n'
    body = sep.join(
        f'<a href="{href}"{" aria-current=\"page\"" if label.lower() == current else ""}>'
        f'{label}</a>' for label, href in items)
    return f'<nav class="article-toc" aria-label="Progress views">\n{body}\n</nav>\n'


def intro(name: str) -> str:
    src = CONTENT_DIR / f"{name}.md"
    if not src.exists():
        raise SystemExit(
            f"progress.py: content/{name}.md is missing. The block of text above "
            f"the table is that file; there is nothing to build without it.")
    return markdown.markdown(src.read_text(encoding="utf-8"),
                            extensions=["tables", "attr_list", "sane_lists", "nl2br"])


def indent(html: str) -> str:
    return "\n".join("      " + ln if ln.strip() else ln for ln in html.splitlines())


def check_links(indicators) -> None:
    """Every topic report and every indicator anchor these tables point at.

    Run before either page is written, so a missing bookmark stops the build
    instead of publishing a link that scrolls nowhere."""
    dead = []
    for row in indicators:
        topic_key, anchor = row["indicator_id"].split("--", 1)
        slug = topic_key.replace(".", "-")
        page = SITE / "topics" / slug / f"{slug}-progress.html"
        if not page.exists():
            dead.append(f"{row['indicator_id']}: {page.relative_to(CORPUS)} not built")
        elif f'id="{anchor}"' not in page.read_text(encoding="utf-8"):
            dead.append(f"{row['indicator_id']}: no #{anchor} in {page.name}")
    if dead:
        raise SystemExit(
            "progress.py: these links would scroll nowhere — run RENDER Step 2 "
            "first, or the indicator has been renamed away from its heading:\n  "
            + "\n  ".join(dead[:20]))


def write(out_dir: Path, *, h1, title, description, url, depth, body, counted,
          source) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(external_links(PAGE.format(
        h1=h1, title=title, description=description, canonical=f"{SITE_BASE}{url}",
        main=MAIN_SITE, chrome=chrome("progress", depth=depth), foot=foot(depth=depth),
        styles=styles(depth, "home.css", "progress.css"), ga=ga(),
        script=script("progress-sticky.js", depth),
        body=indent(body), counted=counted, source=source,
        built=date.today().isoformat(),
    )), encoding="utf-8")


def main() -> int:
    indicators = load_indicators()
    names, region = load_countries()
    check_links(indicators)
    grid = read_grid(indicators)
    places = len({iso for iso, _ in grid})
    counted = (f"{places} country progress reports &times; {len(indicators)} "
               f"indicators, as published")

    write(SITE / "progress",
          h1="Progress", title="Progress by topic",
          description=("How far each of 121 indicators has moved across 54 African "
                       "countries, counted from the country progress reports."),
          url="/progress/", depth=1,
          body=toc("topics") + intro("progress-topics")
               + topics_table(indicators, grid),
          counted=counted, source="content/progress-topics.md")
    print(f"progress: {len(indicators)} indicators over {places} places "
          f"-> site/progress/index.html")

    write(SITE / "progress" / "countries",
          h1="Progress", title="Progress by country",
          description=("How far each of 54 African countries has moved across a "
                       "fixed frame of 121 indicators, counted from the country "
                       "progress reports."),
          url="/progress/countries/", depth=2,
          body=toc("countries") + intro("progress-countries")
               + countries_table(indicators, grid, names, region),
          counted=counted, source="content/progress-countries.md")
    print(f"progress: {places} places over {len(indicators)} indicators "
          f"-> site/progress/countries/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
