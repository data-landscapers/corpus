#!/usr/bin/env python3
"""render.py — one report, two outputs.

Renders a report from `upstream/` to HTML and PDF from one template and one
stylesheet (documentation/design.md §8). The PDF is not a second design: it is the same
document with the print rules in `site/assets/css/report.css` applied.

    python scripts/render.py upstream/reports/KEN/KEN-status.md
    python scripts/render.py upstream/reports/KEN/KEN-status.md --out site/

The page is built from the website's own markup vocabulary — `.site-header`,
`.article-header`, `.article-body`, `.badge`, `.site-footer` — so it reads as
part of data-landscapers.com rather than a separate identity (§1). Every
artefact carries its edition, its OSINT commit and its permanent URL, because
a downloaded PDF has to be verifiable away from the site it came from (§9).
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import markdown

CORPUS = Path(__file__).resolve().parent.parent
BUILD = CORPUS / "build"
UPSTREAM = CORPUS / "upstream"
SITE = CORPUS / "site"

SITE_BASE = "https://corpus.data-landscapers.com"
MAIN_SITE = "https://data-landscapers.com"
LICENCE, LICENCE_URL = "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"
ORG = "Bill Anderson / Data Landscapers Ltd"
COMPANY = "Registered in the UK · Co. No. 16040544"

KIND_LABEL = {
    "status": "Status report",
    "monthly": "Monthly update",
    "progress": "Twelve-month progress report",
}

# The site's .badge variants, mapped onto the ledger's status vocabulary
# (REPORT-COUNTRY skeleton). Matched on the leading word or two, so qualified
# values — "Implemented, capacity-capped", "Planned, stalled" — still colour
# by their head term rather than falling through to grey.
BADGE = [
    ("not held",        "badge--red"),
    ("implemented",     "badge--green"),
    ("in force",        "badge--green"),
    ("piloting",        "badge--amber"),
    ("in development",  "badge--blue"),
    ("planned",         "badge--grey"),
    ("discontinued",    "badge--grey"),
]

# The progress report's own vocabulary, for its Movement column (see the
# "Movement values" key each report opens with: Advanced, Stalled, Regressed,
# Closed, No change, Baseline not held). Kept apart from BADGE rather than
# merged into it: the two tables share no terms, and a shared list would be
# one collision away from a status word mis-colouring a movement cell or vice
# versa.
BADGE_MOVEMENT = [
    ("baseline not held", "badge--red"),
    ("advanced",          "badge--green"),
    ("stalled",           "badge--amber"),
    ("regressed",         "badge--red"),
    ("closed",            "badge--grey"),
    ("no change",         "badge--grey"),
]


def frontmatter(text: str) -> tuple[dict, str]:
    """Split the frontmatter from the body. The reports use flat scalar keys
    only, so a YAML parser would be a dependency for nothing."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    head, body = text[3:end], text[end + 4:]
    meta = {}
    for line in head.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, body.lstrip("\n")



def built_from() -> str:
    f = UPSTREAM / "BUILT-FROM"
    return f.read_text(encoding="utf-8").strip() if f.exists() else "(unknown)"


KINDS = ("status", "monthly", "progress")


def parse_name(path: Path) -> tuple[str, str]:
    """`{unit}-{kind}.md` -> (unit, kind). The unit may itself contain hyphens.

    **Split from the right, on a known kind** *(2026-08-14)*. `parts[0], parts[1]` worked while
    every unit was an ISO3 code and stopped working the moment topic reports arrived: a Level-2
    slug is hyphenated (`dpi.pay` -> `dpi-pay`), so `dpi-pay-monthly.md` parsed as unit `dpi`,
    kind `pay` — and `dpi-pay-progress.md` parsed as *the same pair*, so the two documents wrote
    one filename and the second silently replaced the first. Every slug is hyphenated, so that
    was the whole topic tree, not an edge case.

    A name whose tail is not one of the three kinds keeps the old fallback rather than raising:
    this is called on whatever Step 2's glob matched, and a bad name should render oddly, not
    stop a run of 241 documents."""
    stem = path.stem
    for kind in KINDS:
        if stem.endswith(f"-{kind}"):
            return stem[: -len(kind) - 1], kind
    unit, _, kind = stem.partition("-")
    return unit, (kind or "report")


def tree_of(path: Path) -> str:
    """Which output tree a source document belongs to — `reports/` or `topics/`.

    Taken from the source's grandparent directory (`…/topics/dpi-pay/dpi-pay-monthly.md`), so a
    document lands under the site in the tree it was authored in and its permalink says so. It is
    read off the path rather than off the filename because the unit tells you nothing: `KEN` and
    `dpi-pay` are both just units. Anything not recognised renders under `reports/`, which is
    where every document lived before topics existed."""
    parent = path.parent.parent.name.lower()
    return "topics" if parent == "topics" else "reports"


def badge_class(text: str, vocab=BADGE) -> str:
    plain = re.sub(r"<[^>]+>", "", text).strip().lower()
    for head, cls in vocab:
        if plain.startswith(head):
            return cls
    return "badge--grey"


def classify_table(headers: list[str]) -> str:
    """A report holds three shapes of table, told apart by their header row.

    The ledgers are `System or instrument | Status | As at`. The progress
    report's movement tables are `System or instrument | At <date> |
    At <date> | Movement` — four columns, not three, and the badge belongs on
    the last one rather than the second. Everything else is gaps-shaped:
    `System or instrument | What would settle it | Last probed`, whose middle
    column is prose. Badging by column position alone put status chrome on
    paragraphs of explanation, so the header row decides instead.
    """
    if len(headers) > 1 and headers[1].startswith("status"):
        return "ledger"
    if len(headers) == 4 and headers[3].startswith("movement"):
        return "movement"
    return "gaps"


def style_tables(html: str) -> str:
    """Classify each table and badge only the ones that carry statuses."""
    def do_table(m: re.Match) -> str:
        table = m.group(0)
        headers = [
            re.sub(r"<[^>]+>", "", h).strip().lower()
            for h in re.findall(r"<th[^>]*>.*?</th>", table, re.S)
        ]
        cls = classify_table(headers)
        table = table.replace("<table>", f'<table class="{cls}">', 1)
        if cls == "ledger":
            table = label_status_header(table)
            return badge_rows(table, col=1, vocab=BADGE)
        if cls == "movement":
            return badge_rows(table, col=3, vocab=BADGE_MOVEMENT)
        return table

    return re.sub(r"<table>.*?</table>", do_table, html, flags=re.S)


def label_status_header(table: str) -> str:
    """Name the affordance in the column header.

    Every status that the base can cite is a link to the record behind it, but
    a coloured badge reads as a label. The arrow marks *which* rows have a
    source — a Not held row has none — and the header says what the arrow is.
    """
    ths = re.findall(r"<th[^>]*>.*?</th>", table, re.S)
    if len(ths) < 2:
        return table
    return table.replace(
        ths[1],
        '<th>Status <span class="th-note">&#8599; source</span></th>',
        1,
    )


def badge_rows(table: str, col: int, vocab) -> str:
    """Turn one column into the site's badge component.

    The cell is often a source link (always, for a ledger's Status; never,
    for a progress report's Movement, which is derived rather than cited),
    so the badge is applied *to* the link where there is one rather than
    around it — the status keeps its colour and stays one click from the
    record it came from.
    """
    def do_row(m: re.Match) -> str:
        row = m.group(0)
        cells = re.findall(r"<td[^>]*>.*?</td>", row, re.S)
        if len(cells) <= col:
            return row
        target = cells[col]
        inner = re.sub(r"^<td[^>]*>|</td>$", "", target, flags=re.S).strip()
        cls = badge_class(inner, vocab)
        if inner.startswith("<a "):
            new = re.sub(r"^<a ", f'<a class="badge {cls}" ', inner, count=1)
        else:
            new = f'<span class="badge {cls}">{inner}</span>'
        return row.replace(target, f"<td>{new}</td>", 1)

    return re.sub(r"<tr>\s*<td.*?</tr>", do_row, table, flags=re.S)


def strip_leading_h1(html: str) -> tuple[str, str]:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    if not m:
        return "", html
    return m.group(1), html[:m.start()] + html[m.end():]


def promote_standfirst(html: str) -> str:
    """The *Compiled …* opener is a standfirst, not body copy.

    Only the container changes; the inline markup inside is left exactly as
    Markdown emitted it. An earlier version stripped the wrapping <em> in the
    same substitution, which silently broke the document: the source carries
    `***Not held***` inside that italic run, so Markdown closes and reopens the
    <em> around it, and removing only the outer pair left an unclosed tag that
    italicised every remaining page.
    """
    return re.sub(
        r"<p>(<em>Compiled.*?</em>)</p>",
        r'<div class="report-standfirst">\1</div>',
        html, count=1, flags=re.S,
    )


def promote_key(html: str) -> str:
    return re.sub(
        r"<p>(<strong>Status values\.</strong>.*?)</p>",
        r'<div class="report-key">\1</div>',
        html, count=1, flags=re.S,
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Data Landscapers</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{permalink_html}">
<link rel="stylesheet" href="{main_css}">
<link rel="stylesheet" href="{report_css}">
<link rel="icon" href="{favicon}" type="image/svg+xml">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{permalink_html}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Data Landscapers">
</head>
<body>
<div class="site-wrap">

  <header class="site-header screen-only">
    <div class="site-header__inner">
      <a href="{site_base}/" class="site-logo">
        <img src="{logo}" alt="Data Landscapers" class="site-logo__img">
        <span class="site-logo__text">
          Data Landscapers
          <span class="site-logo__sub">Mapping Africa&rsquo;s data landscape</span>
        </span>
      </a>
      <nav class="site-nav" aria-label="Main navigation">
        <a href="{site_base}/countries/" class="active">Countries</a>
        <a href="{site_base}/regions/">Regions</a>
        <a href="{site_base}/topics/">Topics</a>
        <a href="{site_base}/catalogue/">Catalogue</a>
        <a href="{site_base}/data/">Data</a>
        <a href="{site_base}/method/">Method</a>
      </nav>
    </div>
  </header>

  <div class="running-header">{current_url}</div>

  <main id="main">
  <article>
    <div class="container">

      <div class="print-masthead">
        <img src="{logo}" alt="Data Landscapers">
        <div class="tagline">Mapping Africa&rsquo;s data landscape</div>
      </div>

      <header class="article-header">
        <div class="article-header__kicker">{kind_label}</div>
        <h1 class="article-header__title">{h1}</h1>
        <div class="article-header__byline" data-edition="{edition}">Edition of {edition} &nbsp;·&nbsp; {subtitle}</div>
        <div class="screen-only" style="margin-top:1rem;">
          <a href="{permalink_pdf}" class="btn btn--accent" style="font-size:0.8rem;">&darr; Download PDF</a>
        </div>
      </header>

      <div class="article-body">
{body}
      </div>

      <section class="report-colophon">
        <div class="report-colophon__label">About this document</div>
        <dl>
          <dt>Edition</dt><dd class="edition">{edition}</dd>
          <dt>Current edition</dt><dd><a href="{current_url}">{current_url}</a></dd>
          <dt>This file</dt><dd>{permalink_pdf}</dd>
          <dt>Derived from</dt><dd>Data Landscapers source base, commit <code>{commit}</code></dd>
          <dt>Verify</dt><dd>Hash this file and look it up in <a href="{manifest_url}">{manifest_url}</a></dd>
          <dt>Licence</dt><dd><a href="{licence_url}">{licence}</a></dd>
        </dl>
        <p>Figures are dated because most are time-varying: a figure carries the
        date it was true, not the date you are reading it. Where the base holds
        no reliable statement, the document says <strong>Not held</strong> rather
        than leaving a silence &mdash; those are counted, and listed at the end.</p>
        <p>This is a dated edition and is not revised after publication. If a
        figure here has moved, the current edition will say so.</p>
      </section>

    </div>
  </article>
  </main>

  <footer class="site-footer screen-only">
    <div class="site-footer__inner">
      <p class="site-footer__copy">
        <a href="{licence_url}" style="color:inherit;border-bottom:none;">{licence}</a>
        {year} {org} &nbsp;·&nbsp; {company}
      </p>
      <div class="site-footer__links">
        <a href="{main_site}/">data-landscapers.com</a>
        <a href="{site_base}/method/">Method</a>
        <a href="{manifest_url}">Manifest</a>
      </div>
    </div>
  </footer>

</div>
</body>
</html>
"""


def build_document(md_path: Path, edition: str | None, absolute: bool) -> tuple[str, str, str, str]:
    """Return (html, stem_html, stem_pdf, edition) for one report.

    `absolute` swaps relative asset paths for file:// URIs. That is the only
    difference between the page the site serves and the document WeasyPrint
    renders — one function, so the two cannot drift apart.

    The HTML and the PDF carry different names on purpose (Bill, 2026-08-11).
    The HTML is the browsable page, so its filename never carries an edition —
    that is what makes it a permanent URL: `KEN-status.html` is overwritten in
    place at every render, and a citation to it stays live. The PDF is a
    dated download, retained edition over edition (§9), so its filename keeps
    the edition it was cut on. `current_url` therefore now names the HTML
    permalink itself rather than the reports directory it lives in — the
    stable address §3's "browse the HTML at a stable address" promises.
    """
    raw = md_path.read_text(encoding="utf-8")
    meta, body_md = frontmatter(raw)

    unit, kind = parse_name(md_path)
    # The edition is the date this file was RENDERED, not the date the source was
    # compiled *(Bill, 2026-08-13)*. The date exists so someone holding a download
    # can show where it came from and when; it says nothing about content identity.
    # Taking it from `compiled:` was the bug behind 116 dated PDFs being overwritten
    # in place on 2026-08-13: bodies moved while `compiled:` stood still, so a
    # changed document kept its old edition name and replaced the file a citation
    # would have pointed at. A render date cannot do that — a re-render either
    # writes today's name or writes nothing.
    edition = edition or date.today().isoformat()

    html_body = markdown.markdown(
        body_md, extensions=["tables", "attr_list", "md_in_html", "sane_lists"]
    )
    h1, html_body = strip_leading_h1(html_body)
    html_body = promote_standfirst(html_body)
    html_body = promote_key(html_body)
    html_body = style_tables(html_body)

    title = meta.get("title") or h1 or md_path.stem
    # The HTML permalink carries no period *(Bill, 2026-08-13)*: `AGO-monthly.html`,
    # not `AGO-monthly-2026-07.html`. The HTML is always the current document, so a
    # period in its name is a contradiction — it would freeze a permanent URL to one
    # month and mint a new address every month, which is the opposite of permanent.
    # A monthly spans one whole month and part of the next, so the period is a
    # property of the edition, not of the document. The dated PDF keeps it.
    stem_html = f"{unit}-{kind}"
    stem_pdf = f"{md_path.stem}-{edition}"
    tree = tree_of(md_path)
    rel_html = f"{tree}/{unit}/{stem_html}"
    rel_pdf = f"{tree}/{unit}/{stem_pdf}"

    rows, not_held = meta.get("ledger_rows", ""), meta.get("not_held", "")
    subtitle = (
        f"{rows} systems and instruments tracked, {not_held} of them not held"
        if rows and not_held else "compiled from the Data Landscapers source base"
    )

    css_dir = SITE / "assets" / "css"
    if absolute:
        main_css = (css_dir / "main.css").as_uri()
        report_css = (css_dir / "report.css").as_uri()
        logo = (BUILD / "assets" / "logo.png").as_uri()
    else:
        main_css, report_css = "../../assets/css/main.css", "../../assets/css/report.css"
        logo = "../../assets/logo.png"

    doc = TEMPLATE.format(
        title=title,
        description=f"{KIND_LABEL.get(kind, kind)} — {title}. Edition of {edition}.",
        short_title=h1 or title,
        h1=h1 or title,
        subtitle=subtitle,
        body=html_body,
        main_css=main_css, report_css=report_css, logo=logo,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        kind_label=KIND_LABEL.get(kind, kind.title()),
        edition=edition,
        permalink_html=f"{SITE_BASE}/{rel_html}.html",
        permalink_pdf=f"{SITE_BASE}/{rel_pdf}.pdf",
        current_url=f"{SITE_BASE}/{rel_html}.html",
        manifest_url=f"{SITE_BASE}/manifest.csv",
        commit=built_from()[:12],
        licence=LICENCE, licence_url=LICENCE_URL,
        org=ORG, company=COMPANY, main_site=MAIN_SITE,
        site_base=SITE_BASE, year=edition[:4],
    )
    return doc, stem_html, stem_pdf, edition


def render(md_path: Path, out_dir: Path, edition: str | None = None) -> tuple[Path, Path]:
    served, stem_html, stem_pdf, edition = build_document(md_path, edition, absolute=False)
    for_pdf, _, _, _ = build_document(md_path, edition, absolute=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / f"{stem_html}.html"
    pdf_path = out_dir / f"{stem_pdf}.pdf"
    # Overwriting in place fails on some synced mounts; replace instead. The
    # HTML is always rewritten (its name never changes); the PDF only
    # replaces the one matching this edition — earlier-dated PDFs are a
    # different filename and are left alone, which is what retains them (§9).
    for f in (html_path, pdf_path):
        if f.exists():
            f.unlink()
    html_path.write_text(served, encoding="utf-8")

    from weasyprint import HTML  # imported late: only the PDF path needs it
    HTML(string=for_pdf, base_url=str(SITE / "assets" / "css")).write_pdf(pdf_path)

    return html_path, pdf_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("markdown", type=Path)
    # Default deferred to the source: a topic document renders under site/topics/, a unit report
    # under site/reports/, and the permalink in the page agrees with where the file lands. An
    # explicit --out still wins and still takes {unit} beneath it.
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--edition", default=None)
    args = ap.parse_args()

    src = args.markdown if args.markdown.is_absolute() else CORPUS / args.markdown
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 2

    unit, _ = parse_name(src)
    base = args.out if args.out is not None else SITE / tree_of(src)
    html_path, pdf_path = render(src, base / unit, args.edition)

    print(f"source   {src.relative_to(CORPUS)}")
    def show(p: Path) -> str:
        try:
            return str(p.relative_to(CORPUS))
        except ValueError:
            return str(p)          # --out may point outside the repo
    print(f"html     {show(html_path)}  {html_path.stat().st_size/1024:.0f} KB")
    print(f"pdf      {show(pdf_path)}  {pdf_path.stat().st_size/1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
