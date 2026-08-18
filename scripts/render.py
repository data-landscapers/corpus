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

An edition is cut when the content changes, not when a build runs (§9). A document
whose body has not moved since its standing edition was cut is left exactly as it
is, PDF and page alike — see `render()`.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import date
from pathlib import Path

import markdown

CORPUS = Path(__file__).resolve().parent.parent
BUILD = CORPUS / "build"
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
    "bulletin": "Daily bulletin",
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



def record(body_md: str) -> str:
    """The document's content digest — the body, below the frontmatter.

    **Below the frontmatter is the whole of the trick** (design.md §9). `compiled:` moves
    whenever the file is rewritten and `record:` is a digest of the same content, so a hash
    taken over the whole document would differ on every run for a document that had not
    moved, and the gate in `render()` would never once fire.

    Same span, same algorithm and same length as the `record:` field `report-render.py`
    stamps into the frontmatter — but computed here rather than read from there. Not every
    source this is handed carries that field, and a gate that quietly passes everything when
    its input is missing is worse than no gate, because from the outside it looks like one."""
    return hashlib.sha1(body_md.encode("utf-8")).hexdigest()[:12]


# Read back off an already-rendered page: what it was cut from, and what it was cut as.
PRIOR_RECORD = re.compile(r'<meta name="dl-record" content="([0-9a-f]+)">')
PRIOR_EDITION = re.compile(r'data-edition="([^"]+)"')


def built_from() -> str:
    f = CORPUS / "BUILT-FROM"
    return f.read_text(encoding="utf-8").strip() if f.exists() else "(unknown)"


KINDS = ("status", "monthly", "progress", "bulletin")


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


# **One grammar for an edition, in the script that names them.** `country.py` and
# `topic-page.py` both read an edition back off a filename to decide which one is current, and
# a second copy of this rule in either of them is a second place for the two to disagree — the
# `-2` suffix below broke both of them the moment it existed, precisely because they each held
# their own idea of what an edition looks like.
EDITION = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})(?:-(?P<seq>\d+))?$")
STEM_EDITION = re.compile(r"-(\d{4}-\d{2}-\d{2}(?:-\d+)?)$")


def edition_of(stem: str) -> str | None:
    """The edition a rendered filename carries, or None if it carries none.

    Anchored at the end, so the monthly and progress names that still carry a period from before
    the 2026-08-13 rename — `KEN-monthly-2026-07-2026-08-05` — yield the edition and not the
    window."""
    m = STEM_EDITION.search(stem)
    return m.group(1) if m else None


def edition_key(edition: str) -> tuple[str, int]:
    """Sort key for an edition: the date, then the same-day sequence as a **number**.

    Sorting the strings gets this wrong in both directions, and silently. In a filename
    `-2026-08-18-2.pdf` sorts *before* `-2026-08-18.pdf`, because `-` precedes `.`, so taking
    the last name of a sorted list hands back the older edition. In an edition string `-10`
    sorts before `-2`. Either way the page offers a superseded file and looks entirely
    correct doing it."""
    m = EDITION.match(edition or "")
    return (m.group("date"), int(m.group("seq") or 1)) if m else ("", 0)


def next_edition(out_dir: Path, stem: str, today: str) -> str:
    """Today's edition for this document — suffixed if today's name is already taken.

    **The first edition of a day is unsuffixed and the second takes `-2`** (design.md §9). Two
    editions in one day is a normal occurrence rather than an edge case: SWEEP-CYCLE normally
    runs overnight, but a session may be run during the day to force an update on a live issue
    *(Bill, 2026-08-06)*.

    **The first is never renamed when the second appears.** Making it `-1` for symmetry would
    break every URL already handed out, which is the one thing §9 exists to prevent — so the
    names are asymmetric, and most days have one edition, so most of them stay clean.

    Existence on disk is the test, not a count kept somewhere. The retained PDFs *are* the
    record of which names are spoken for, and a document whose content has not moved never
    reaches here at all — the gate in `render()` holds it off first."""
    if not (out_dir / f"{stem}-{today}.pdf").exists():
        return today
    n = 2
    while (out_dir / f"{stem}-{today}-{n}.pdf").exists():
        n += 1
    return f"{today}-{n}"


def stem_html_of(path: Path) -> str:
    """The undated permalink stem, `{unit}-{kind}`. One implementation, because the gate in
    `render()` has to open the file `build_document` wrote, and a second copy of this rule
    would be a second place for the two to disagree — silently, since a gate that looks for
    the wrong filename finds nothing and cuts an edition, which is indistinguishable from
    the outside from a gate working correctly."""
    unit, kind = parse_name(path)
    return f"{unit}-{kind}"


def tree_of(path: Path) -> str:
    """Which output tree a source document belongs to — `reports/`, `topics/` or `bulletins/`.

    Taken from the source's grandparent directory (`…/topics/dpi-pay/dpi-pay-monthly.md`), so a
    document lands under the site in the tree it was authored in and its permalink says so. It is
    read off the path rather than off the filename because the unit tells you nothing: `KEN` and
    `dpi-pay` are both just units. Anything not recognised renders under `reports/`, which is
    where every document lived before topics existed.

    The bulletins are the one tree with no unit beneath it — there are two documents and they are
    the whole of it — so they are recognised on the *parent* rather than the grandparent, and
    `site_rel` below is where that shows up."""
    if path.parent.name.lower() == "bulletins":
        return "bulletins"
    parent = path.parent.parent.name.lower()
    return "topics" if parent == "topics" else "reports"


def site_rel(path: Path) -> str:
    """The document's directory under `site/`, relative — `reports/KEN`, `topics/dpi-pay`,
    `bulletins`. One function, because the permalink written into the page and the directory the
    file is written to have to agree and there is no way to notice if they stop."""
    tree = tree_of(path)
    if tree == "bulletins":
        return tree
    unit, _ = parse_name(path)
    return f"{tree}/{unit}"


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
<meta name="dl-record" content="{record}">
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
        <div class="screen-only" style="margin-top:1rem;">{download}</div>
      </header>

      <div class="article-body">
{body}
      </div>

      <section class="report-colophon">
        <div class="report-colophon__label">About this document</div>
        <dl>
          <dt>Edition</dt><dd class="edition">{edition}</dd>
          <dt>Current edition</dt><dd><a href="{current_url}">{current_url}</a></dd>
{colophon_rows}
          <dt>Licence</dt><dd><a href="{licence_url}">{licence}</a></dd>
        </dl>
{colophon_notes}
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


REPORT_NOTES = """        <p>Figures are dated because most are time-varying: a figure carries the
        date it was true, not the date you are reading it. Where the base holds
        no reliable statement, the document says <strong>Not held</strong> rather
        than leaving a silence &mdash; those are counted, and listed at the end.</p>
        <p>This is a dated edition and is not revised after publication. If a
        figure here has moved, the current edition will say so.</p>"""

BULLETIN_NOTES = """        <p>The bulletin covers what was <em>published</em> in its window, which is not
        the same as what arrived in it: the corpus acquires in batches, so a
        record ingested today may carry any publication date. Each item is
        summarised once and cross-referenced from every other country, region or
        topic it touches.</p>
        <p>This page is rewritten at every build and holds only the window named
        in its byline. It is not an archive; the country, region and topic
        reports are where a development is kept.</p>"""


def build_document(md_path: Path, edition: str | None, absolute: bool,
                   pdf: bool = True) -> tuple[str, str, str, str]:
    """Return (html, stem_html, stem_pdf, edition, record) for one report.

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
    rec = record(body_md)

    unit, kind = parse_name(md_path)
    # The edition is the date this file was RENDERED, not the date the source was
    # compiled *(Bill, 2026-08-13)*. The date exists so someone holding a download
    # can show where it came from and when; it says nothing about content identity.
    # Taking it from `compiled:` was the bug behind 116 dated PDFs being overwritten
    # in place on 2026-08-13: bodies moved while `compiled:` stood still, so a
    # changed document kept its old edition name and replaced the file a citation
    # would have pointed at. A render date cannot do that — a re-render either
    # writes today's name or writes nothing.
    #
    # The content gate in `render()` *(2026-08-18)* does not touch this and must not: it
    # decides **whether** to cut an edition, never what to name the one it cuts. Naming stayed
    # with the render date precisely so that a document which has moved can never land on a
    # name a citation already rests on.
    edition = edition or date.today().isoformat()

    # `toc` is here for its ids, not for a table of contents *(2026-08-17)*. It gives every
    # heading an id slugified from its text, which is what makes an in-document link resolve —
    # the daily bulletin summarises each item once and cross-references it from every other
    # country or topic it touches, and without ids every one of those links lands nowhere.
    # `bulletin.py` imports the same `slugify` to build them, so there is one implementation.
    # It is additive for every other document: an id attribute on a heading and nothing else.
    html_body = markdown.markdown(
        body_md, extensions=["tables", "attr_list", "md_in_html", "sane_lists", "toc"]
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
    stem_html = stem_html_of(md_path)
    stem_pdf = f"{md_path.stem}-{edition}"
    rel = site_rel(md_path)
    rel_html = f"{rel}/{stem_html}"
    rel_pdf = f"{rel}/{stem_pdf}"

    rows, not_held = meta.get("ledger_rows", ""), meta.get("not_held", "")
    # A document may state its own byline — the bulletins do, since the window is the one thing a
    # reader needs from the header and no ledger count describes them.
    subtitle = meta.get("subtitle") or (
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

    # A document rendered without a PDF must not advertise one *(Bill, 2026-08-17)*. The download
    # button, the `This file` row and the hash-and-verify line all name a file that was never cut,
    # so they come out together rather than being left to 404.
    derived = (f"          <dt>Derived from</dt><dd>Data Landscapers source base, "
               f"commit <code>{built_from()[:12]}</code></dd>")
    if pdf:
        download = (f'\n          <a href="{SITE_BASE}/{rel_pdf}.pdf" class="btn btn--accent" '
                    f'style="font-size:0.8rem;">&darr; Download PDF</a>\n        ')
        colophon_rows = "\n".join([
            f"          <dt>This file</dt><dd>{SITE_BASE}/{rel_pdf}.pdf</dd>",
            derived,
            f"          <dt>Verify</dt><dd>Hash this file and look it up in "
            f'<a href="{SITE_BASE}/manifest.csv">{SITE_BASE}/manifest.csv</a></dd>',
        ])
    else:
        download = ""
        colophon_rows = "\n".join([
            f"          <dt>This file</dt><dd>{SITE_BASE}/{rel_html}.html</dd>",
            derived,
        ])

    doc = TEMPLATE.format(
        title=title,
        download=download,
        colophon_rows=colophon_rows,
        colophon_notes=BULLETIN_NOTES if kind == "bulletin" else REPORT_NOTES,
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
        current_url=f"{SITE_BASE}/{rel_html}.html",
        manifest_url=f"{SITE_BASE}/manifest.csv",
        licence=LICENCE, licence_url=LICENCE_URL,
        org=ORG, company=COMPANY, main_site=MAIN_SITE,
        site_base=SITE_BASE, year=edition[:4],
        record=rec,
    )
    return doc, stem_html, stem_pdf, edition, rec


def held_edition(md_path: Path, out_dir: Path, rec: str) -> str | None:
    """The edition already on disk, if the source has not moved since it was cut — else None.

    **The record is read back out of the served HTML**, which is the one artefact of a document
    whose name never changes. So what an edition was cut from travels inside the edition, and
    the gate needs no state file sitting beside the output to be kept in step with it.

    **A page written before this field existed reports None, so the first run after the gate
    arrives cuts an edition for every document.** That is the same call `report-render.py`
    makes for a document with no stored digest, and it is wrong only in the safe direction:
    one day's worth of editions minted needlessly, against the alternative of adopting an
    edition whose content may have moved since and then never noticing that it had."""
    html_path = out_dir / f"{stem_html_of(md_path)}.html"
    if not html_path.exists():
        return None
    served = html_path.read_text(encoding="utf-8")
    held, ed = PRIOR_RECORD.search(served), PRIOR_EDITION.search(served)
    if held is None or ed is None or held.group(1) != rec:
        return None
    return ed.group(1)


def render(md_path: Path, out_dir: Path, edition: str | None = None,
           pdf: bool = True, force: bool = False) -> tuple[Path, Path | None, bool]:
    """Render the document, or leave its standing edition alone. Returns `(html, pdf, minted)`.

    **An edition is cut when the content changes, not when a build runs** (design.md §9). RENDER
    renders everything on every run and judges nothing, which is right — but a render that cuts
    an edition regardless turns 241 documents into 241 new dated PDFs every render day, retained
    for ever, because retention is what §9 promises. Only a fraction of them differ from the
    edition before. The gate belongs here rather than in the runbook for the same reason the leak
    gate does: a rule a loop has to remember is a rule that eventually stops running.

    **An unchanged document is left entirely alone, the page as well as the PDF.** Rewriting the
    HTML to print today while the PDF beside it still says August would make the page disagree
    with the artefact it offers, which is the undated-URL failure §9 exists to prevent arriving
    one field at a time. A retained edition is not restyled either: the PDF embeds the
    stylesheet, so a change to `report.css` reaches new editions only — which is what *not
    revised after publication* means when it is taken literally, and it is meant literally.

    `--edition` and `--force` are deliberate re-cuts and skip the gate. They do not skip §9's
    same-day suffixing, though: a forced re-cut differs from what is already published — that is
    what it is for — so writing it over the published name would change the bytes under a
    citation, which is the failure the suffix exists to prevent."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = record(frontmatter(md_path.read_text(encoding="utf-8"))[1])

    held = None if (edition or force) else held_edition(md_path, out_dir, rec)
    if held is not None:
        html_path = out_dir / f"{stem_html_of(md_path)}.html"
        pdf_path = out_dir / f"{md_path.stem}-{held}.pdf" if pdf else None
        if pdf_path is None or pdf_path.exists():
            return html_path, pdf_path, False
        # The page names an edition whose PDF is not there — a file deleted by hand, or a run
        # that died between the two writes. Cut it again under **its own** name rather than
        # minting a new one: the published URL is the thing being repaired, not superseded.
        edition = held

    # A cut edition never lands on a name that is already taken (§9). Only when the renderer is
    # choosing the name: an explicit `--edition` is an operator naming one exactly, and the
    # repair above is restoring one that was published.
    if edition is None and pdf:
        edition = next_edition(out_dir, md_path.stem, date.today().isoformat())

    served, stem_html, stem_pdf, edition, _ = build_document(
        md_path, edition, absolute=False, pdf=pdf)

    html_path = out_dir / f"{stem_html}.html"
    pdf_path = out_dir / f"{stem_pdf}.pdf" if pdf else None
    # Overwriting in place fails on some synced mounts; replace instead. The
    # HTML is always rewritten (its name never changes); the PDF only
    # replaces the one matching this edition — earlier-dated PDFs are a
    # different filename and are left alone, which is what retains them (§9).
    for f in (html_path, pdf_path):
        if f is not None and f.exists():
            f.unlink()
    html_path.write_text(served, encoding="utf-8")

    if pdf_path is None:
        return html_path, None, True

    for_pdf, _, _, _, _ = build_document(md_path, edition, absolute=True, pdf=True)
    from weasyprint import HTML  # imported late: only the PDF path needs it
    HTML(string=for_pdf, base_url=str(SITE / "assets" / "css")).write_pdf(pdf_path)

    return html_path, pdf_path, True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("markdown", type=Path)
    # Default deferred to the source: a topic document renders under site/topics/, a unit report
    # under site/reports/, and the permalink in the page agrees with where the file lands. An
    # explicit --out still wins and still takes {unit} beneath it.
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--edition", default=None)
    # The daily bulletin is HTML only *(Bill, 2026-08-17)*. A dated PDF is a retained edition of a
    # document worth citing later; a bulletin is superseded the next morning and its content is
    # kept by the reports, so cutting one would archive the same news twice under a worse name.
    ap.add_argument("--no-pdf", action="store_true", help="write the HTML and no PDF")
    # Escape hatch for the content gate: a template or stylesheet change moves nothing in the
    # source, so nothing would re-render without it. Re-cutting every document is a decision
    # (241 editions), which is why it is a flag and not the default.
    ap.add_argument("--force", action="store_true",
                    help="cut a new edition even if the content has not moved")
    args = ap.parse_args()

    src = args.markdown if args.markdown.is_absolute() else CORPUS / args.markdown
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 2

    rel = site_rel(src)                       # `reports/KEN`, `topics/dpi-pay`, `bulletins`
    out_dir = SITE / rel if args.out is None else args.out / rel.split("/")[-1]
    html_path, pdf_path, minted = render(src, out_dir, args.edition,
                                         pdf=not args.no_pdf, force=args.force)

    print(f"source   {src.relative_to(CORPUS)}")
    if not minted:
        print("edition  unchanged — content has not moved since the standing edition was cut")
    def show(p: Path) -> str:
        try:
            return str(p.relative_to(CORPUS))
        except ValueError:
            return str(p)          # --out may point outside the repo
    print(f"html     {show(html_path)}  {html_path.stat().st_size/1024:.0f} KB")
    if pdf_path is not None:
        print(f"pdf      {show(pdf_path)}  {pdf_path.stat().st_size/1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
