#!/usr/bin/env python3
"""render.py — one report, two outputs.

Renders a report from `upstream/` to HTML and PDF from one template and one
stylesheet (documentation/design.md §8). The PDF is not a second design: it is the same
document with the print rules in `site/assets/css/report.css` applied.

    python scripts/render.py upstream/reports/KEN/KEN-status.md
    python scripts/render.py upstream/reports/KEN/KEN-status.md --out site/

The page is built from the website's own markup vocabulary — `.site-header`,
`.article-header`, `.article-body`, `.badge`, `.site-footer` — so it reads as
part of data-landscapers.io rather than a separate identity (§1). Every
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chrome_lib import chrome, foot, styles  # noqa: E402
from copy_lib import copy  # noqa: E402

# The edition grammar and the same-day suffix live in `editions.py`, because `country.py`,
# `topic-page.py` and `finance.py` all read or write editions too (§9).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import editions  # noqa: E402
import bulletin_editions  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
BUILD = CORPUS / "build"
SITE = CORPUS / "site"

SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"
LICENCE, LICENCE_URL = "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"
ORG = "Bill Anderson / Data Landscapers Ltd"
COMPANY = "Registered in the UK · Co. No. 16040544"

# The small-caps kicker above the title. **The bulletin has none** *(Bill, 2026-08-21)*: it read
# "DAILY BULLETIN" above a title reading "Bulletin", which is the same word twice and a claim
# about cadence the document does not make — it is written at the end of a sweep, not at a time
# of day. An empty label takes the whole element out rather than leaving a blank line where a
# kicker used to be.
KIND_LABEL = {
    "status": "Status report",
    "monthly": "Monthly update",
    "progress": "Progress report",
    "bulletin": "",
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

# The indicator frame's Progress column (`progress-report-redesign.md` §3), a third vocabulary
# and a third list, on the same reasoning that keeps the first two apart. It shares four terms
# with BADGE_MOVEMENT and is not the same set: *Mixed* has no counterpart there, and **No
# evidence is grey rather than red**. Baseline not held is red because it marks a report that
# cannot answer a question it asked; No evidence is the frame answering exactly as designed —
# a hundred red rows on a median country would read as a broken document rather than a thin
# base, which is the reading §4's opening paragraph exists to prevent.
BADGE_PROGRESS = [
    ("no evidence", "badge--grey"),
    ("advanced",    "badge--green"),
    ("stalled",     "badge--amber"),
    ("regressed",   "badge--red"),
    ("mixed",       "badge--amber"),
    ("no change",   "badge--grey"),
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


def stem_html_of(path: Path) -> str:
    """The undated permalink stem, `{unit}-{kind}`. One implementation, because the gate in
    `render()` has to open the file `build_document` wrote, and a second copy of this rule
    would be a second place for the two to disagree — silently, since a gate that looks for
    the wrong filename finds nothing and cuts an edition, which is indistinguishable from
    the outside from a gate working correctly."""
    unit, kind = parse_name(path)
    # The bulletin is served as a directory index, `/bulletin/`, so its file is `index.html` and
    # its unit never appears in a URL *(Bill, 2026-08-21)*. It is the only document here with a
    # readable address rather than a generated one, and it can have one because there is exactly
    # one of it — every other page is one of 241 and needs its unit in the name to be told apart.
    if kind == "bulletin":
        return "index"
    return f"{unit}-{kind}"


def tree_of(path: Path) -> str:
    """Which output tree a source document belongs to — `reports/`, `topics/` or `bulletins/`.

    Taken from the source's grandparent directory (`…/topics/dpi-pay/dpi-pay-monthly.md`), so a
    document lands under the site in the tree it was authored in and its permalink says so. It is
    read off the path rather than off the filename because the unit tells you nothing: `KEN` and
    `dpi-pay` are both just units. Anything not recognised renders under `reports/`, which is
    where every document lived before topics existed.

    The bulletin is the one tree with no unit beneath it — there is one document and it is the
    whole of it — so it is recognised on the *parent* rather than the grandparent, and `site_rel`
    below is where that shows up."""
    if path.parent.name.lower() == "bulletins":
        return "bulletins"
    parent = path.parent.parent.name.lower()
    return "topics" if parent == "topics" else "reports"


def site_rel(path: Path) -> str:
    """The document's directory under `site/`, relative — `reports/KEN`, `topics/dpi-pay`,
    `bulletin`. One function, because the permalink written into the page and the directory the
    file is written to have to agree and there is no way to notice if they stop.

    **The bulletin's source directory and its site directory differ by an s** — it is authored
    into `outputs/bulletins/` and published at `/bulletin/` *(Bill, 2026-08-21)*. The plural was
    right while there were two of them and is now just the folder the drafts land in; the URL is
    what a reader types, and there is one bulletin."""
    tree = tree_of(path)
    if tree == "bulletins":
        return "bulletin"
    unit, _ = parse_name(path)
    return f"{tree}/{unit}"


def asset_version(path: Path) -> str:
    """A short digest of an asset's bytes, for a `?v=` on the URL that references it.

    **A stylesheet or script at a fixed URL is cached by the reader's browser, and a corrected
    one at the same URL is not fetched** *(2026-08-22)*. That is not a theory: the bulletin's
    filter shipped with a fault, was fixed, deployed, and went on failing for Bill because
    `bulletin-filter.js` was the same URL it had been ten minutes earlier. Everything on the
    server was right and the page was still wrong.

    A query string is invisible to a static host — GitHub Pages serves the file and ignores it —
    so this costs nothing and changes the URL exactly when the bytes change. Where the asset is
    missing the URL is left bare rather than stamped with a guess: a build that cannot read the
    file it is linking should link it plainly and let the 404 be visible.
    """
    try:
        return "?v=" + hashlib.sha1(path.read_bytes()).hexdigest()[:8]
    except OSError:
        return ""


def badge_class(text: str, vocab=BADGE) -> str:
    plain = re.sub(r"<[^>]+>", "", text).strip().lower()
    for head, cls in vocab:
        if plain.startswith(head):
            return cls
    return "badge--grey"


def classify_table(headers: list[str]) -> str:
    """A report holds three shapes of table, told apart by their header row.

    The ledgers are `System or instrument | Status | As at`. The region progress
    report's movement tables are `System or instrument | At <date> |
    At <date> | Movement` — four columns, not three, and the badge belongs on
    the last one rather than the second. A country progress report is the
    indicator frame, `Topic | Indicator | Developments | Progress`, also four
    and also badged on the last, told apart by that header. Everything else is
    gaps-shaped:
    `System or instrument | What would settle it | Last probed`, whose middle
    column is prose. Badging by column position alone put status chrome on
    paragraphs of explanation, so the header row decides instead.
    """
    if len(headers) > 1 and headers[1].startswith("status"):
        return "ledger"
    if len(headers) == 4 and headers[3].startswith("movement"):
        return "movement"
    # The indicator frame: `Topic | Indicator | Developments | Progress`. Four columns like the
    # movement table and badged on the last like it, but a different vocabulary and very
    # different widths — the Developments cell carries prose and the row's expander.
    if len(headers) == 4 and headers[3].startswith("progress"):
        return "indicator"
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
        if cls == "indicator":
            return badge_rows(table, col=3, vocab=BADGE_PROGRESS, split_qualifier=True)
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


def badge_rows(table: str, col: int, vocab, split_qualifier: bool = False) -> str:
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
        elif split_qualifier and "<" not in inner and "," in inner:
            # **The badge carries the stem; the qualifying clause sits beside it.** A badge is a
            # label and has to read as one at a glance. That held while qualifiers were "Advanced,
            # slipped", and stops holding on the indicator frame, where *Mixed* must name which
            # instruments moved which way (`progress-report-redesign.md` §3) and the clause is
            # routinely longer than the value it qualifies. Colouring is unaffected: `badge_class`
            # already keys on the head term.
            head, _, tail = inner.partition(",")
            new = (f'<span class="badge {cls}">{head.strip()}</span>'
                   f'<span class="badge-note">{tail.strip()}</span>')
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
    """A document that opens on a wholly italic paragraph opens on a standfirst, not body copy.

    **Matched on shape and position rather than on its first word** *(2026-08-25)*. This used to
    look for `<p><em>Compiled…`, which was the status report's opener and nobody else's: the
    monthly has always begun "Developments…" and never got the treatment, and the country progress
    report's *Compiled* sentence came off in the same edit that wrote this, so the rule would have
    stopped matching anything but the fourteen ledger-rendered status reports. A leading paragraph
    that is entirely emphasised is a standfirst whatever it says, which is the property the
    styling was always keyed on.

    Only the container changes; the inline markup inside is left exactly as
    Markdown emitted it. An earlier version stripped the wrapping <em> in the
    same substitution, which silently broke the document: the source carries
    `***Not held***` inside that italic run, so Markdown closes and reopens the
    <em> around it, and removing only the outer pair left an unclosed tag that
    italicised every remaining page.
    """
    return re.sub(
        r"\A\s*<p>(<em>.*?</em>)</p>",
        r'<div class="report-standfirst">\1</div>',
        html, count=1, flags=re.S,
    )


# **The reports' contents bar, after the bulletin's** *(Bill, 2026-08-25: "add Level 1 TOC the same
# as Bulletin")*. `.article-toc` is the site-wide treatment `main.css` carries — it went up there
# on 2026-08-24 precisely because the bulletin's bar had become the house idiom for an in-page jump
# nav — so this needs no CSS of its own, and the `bulletin-nav` class is deliberately not copied:
# that one is `bulletin-filter.js`'s hook for pruning the bar to a selected country, which is that
# page's behaviour alone.
#
# It is built here rather than in `report-render.py` for one reason worth stating: the STATUS-INIT
# baseline is not rendered by `report-render.py` at all, so a bar written there would appear on
# fourteen countries' status reports and not on the other forty. Every report passes through this
# function, and by this point the `toc` extension has already put an id on every heading — so the
# anchors are the document's own, and cannot be a second slugifier's guess at them.
H2 = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)


def contents_bar(html: str) -> str:
    """A jump nav over the document's `<h2>`s, or nothing if it has fewer than two."""
    found = H2.findall(html)
    if len(found) < 2:
        return ""
    sep = '<span class="article-toc__sep" aria-hidden="true">&middot;</span>'
    links = f"\n{sep}\n".join(
        f'<a href="#{anchor}">{re.sub(r"<[^>]+>", "", text).strip()}</a>'
        for anchor, text in found)
    return ('<nav class="article-toc" aria-label="Sections in this report">\n'
            f"{links}\n</nav>\n")


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
{styles}
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

{chrome}

  <div class="running-header">{current_url}</div>

  <main id="main">
  <article>
    <div class="container">

      <div class="print-masthead">
        <img src="{logo}" alt="Data Landscapers">
        <div class="tagline">Mapping Africa&rsquo;s data landscape</div>
      </div>

      <header class="article-header{header_mod}">
{kicker}        <h1 class="article-header__title">{h1}</h1>
        <div class="article-header__meta">
          <div class="article-header__byline" data-edition="{edition}">{byline}</div>
          <div class="screen-only">{download}</div>
        </div>
      </header>

      <div class="article-body">
{body}
      </div>

      <section class="report-colophon">
        <div class="report-colophon__label">About this document</div>
        <dl>
          <dt>Edition</dt><dd class="edition">{edition_display}</dd>
{current_row}{colophon_rows}
          <dt>Licence</dt><dd><a href="{licence_url}">{licence}</a></dd>
        </dl>
{colophon_notes}
      </section>

    </div>
  </article>
  </main>

{foot}

</div>
{page_script}
</body>
</html>
"""


# The two standing notes live in `content/document.md` now (Bill, 2026-08-19): they are
# reader-facing prose, they appear on every document rendered, and they were the least
# reachable text on the site for the person whose job is to revise them.
REPORT_NOTES = copy("document", "report-notes")
BULLETIN_NOTES = copy("document", "bulletin-notes")


def archive_picker(entries: list[dict], current: str) -> str:
    """The mini-archive dropdown, for the colophon.

    **In the colophon beside `This file`, not in the header beside `↓ PDF`**
    (`documentation/bulletin-archive.md`). §1's ruling is *expose only current plus a quiet
    earlier-editions affordance*, and while the archive reverses the *no version picker* half of
    that for this one document, *quiet* is still the register. The header row is already
    `flex-wrap: nowrap` with the byline shrinking inside its own box; a third control there is a
    layout problem as well as an emphasis one. `This file` already names the dated PDF, which
    makes *and here are the earlier ones* the sentence that belongs next to it.

    **Every option is a dated URL**, so §9's *no undated download URL exists at all* is
    untouched. The control renders `hidden` and `bulletin-filter.js` removes the attribute, the
    same progressive enhancement the country filter uses: with no script the reader has the
    current PDF and no dead control, which is the right failure.
    """
    if len(entries) < 2:
        # One edition is not an archive, and a picker offering only the file already named two
        # rows above is furniture.
        return ""
    options = "\n".join(
        f'            <option value="{e["file"]}"'
        f'{" selected" if e["edition"] == current else ""}>'
        f'{html_escape(bulletin_editions.label(e))}</option>'
        for e in entries)
    return (
        '          <dt>Earlier editions</dt><dd>\n'
        '            <select id="bulletin-editions" class="edition-picker" hidden'
        ' aria-label="Earlier editions of this bulletin">\n'
        f'{options}\n'
        '            </select>\n'
        '          </dd>\n')


def html_escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_document(md_path: Path, edition: str | None, absolute: bool,
                   pdf: bool = True, archive: list[dict] | None = None) -> tuple[str, str, str, str]:
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
    # the bulletin summarises each item once and cross-references it from every other topic it
    # touches, and its category bar jumps to the same headings; without ids every one of those
    # links lands nowhere.
    # `bulletin.py` imports the same `slugify` to build them, so there is one implementation.
    # It is additive for every other document: an id attribute on a heading and nothing else.
    html_body = markdown.markdown(
        body_md, extensions=["tables", "attr_list", "md_in_html", "sane_lists", "toc"]
    )
    h1, html_body = strip_leading_h1(html_body)
    html_body = promote_standfirst(html_body)
    html_body = promote_key(html_body)
    html_body = style_tables(html_body)

    # The bar sits *under* the standfirst, not above it: the opening italic line says what the
    # document is and over what window, which is what a reader needs before a list of places to
    # jump to. The bulletin has no standfirst and so puts its bar first — same element, same
    # position relative to the prose. `bulletin` is excluded because it builds its own, pruned by
    # a script to the categories an edition actually reaches.
    if kind in ("status", "monthly", "progress"):
        bar = contents_bar(html_body)
        if bar:
            lead = re.match(r'\A(\s*<div class="report-standfirst">.*?</div>\s*)',
                            html_body, re.S)
            html_body = (lead.group(1) + bar + html_body[lead.end():]) if lead \
                else bar + html_body

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
    # `/bulletin/` rather than `/bulletin/index.html`: the file is an index, so the directory is
    # the address, and the two are the same page. The one that goes in `<link rel=canonical>` has
    # to be the one a reader would type or a search engine would keep.
    url_html = (f"{SITE_BASE}/{rel}/" if stem_html == "index"
                else f"{SITE_BASE}/{rel_html}.html")

    rows, not_held = meta.get("ledger_rows", ""), meta.get("not_held", "")
    # A document may state its own byline — the bulletin does, since the window is the one thing a
    # reader needs from the header and no ledger count describes it.
    # **The byline says who compiled it and from what, and no longer counts what is missing**
    # *(Bill, 2026-08-25)*. Two changes, both about what belongs above the first paragraph.
    #
    # The not-held count came off: it is a fact about the ledger's completeness, and the marked
    # rows are visible and countable inside the document, where a reader can see what is not held
    # rather than only how much. In the byline it read as a warning about a report nobody had yet
    # opened. The same number came off the country page's report rows in the same edit.
    #
    # "Compiled by Claude Opus from the documents in the Corpus repository" replaces "compiled from
    # the Data Landscapers source base", which named a thing a reader cannot inspect and said
    # nothing about how the document came to exist. The new line is the disclosure: a model wrote
    # it, over this repository's own holdings, and the catalogue beside it is the list of those
    # holdings. `ledger_rows` still fills the count where a document carries one.
    subtitle = meta.get("subtitle") or (
        f"{rows} systems and instruments tracked" if rows
        else "compiled by Claude Opus from the documents in the Corpus repository"
    )

    # **The colophon names the file, and the byline names the clock** *(Bill, 2026-08-21, second
    # ruling)*. The bulletin's Edition row briefly showed `compiled:` to the minute, so that a
    # bulletin rebuilt twice in a day could be told apart. It cannot show that any more: the
    # page's byline is now refreshed on every sweep while the dated PDF beside it is cut only
    # when the material moves, so a colophon showing the clock would name an edition that is not
    # the file it is offering. `editions.py`'s same-day `-2` suffix already tells two cuts of one
    # day apart, and it is in the filename, which is what a reader holding a download can see.
    edition_display = edition

    # The bulletin's byline is its subtitle and nothing else *(Bill, 2026-08-21)*. Every other
    # document opens "Edition of {date} · {byline}", which the bulletin's own subtitle now says
    # better and in full — "Last updated … at … — Covering sources published on …". The edition
    # is still on the page, in the colophon, where an edition belongs.
    byline = (subtitle if kind == "bulletin"
              else f"Edition of {edition} &nbsp;·&nbsp; {subtitle}")
    kind_label = KIND_LABEL.get(kind, kind.title())
    kicker = (f'        <div class="article-header__kicker">{kind_label}</div>\n'
              if kind_label else "")

    # **The bulletin's header carries no closing rule** *(Bill, 2026-08-21)*. `main.css` gives
    # every `.article-header` a bottom border, and the category bar directly below has a top
    # border of its own, so the page opened with two horizontal lines a few millimetres apart
    # and nothing between them. `main.css` is vendored from the website repo and is not ours to
    # edit, so the header takes a modifier class and `report.css` turns the border off for it.
    header_mod = " article-header--bulletin" if kind == "bulletin" else ""

    # Which nav item lights up. A bulletin is its own item; a country or region report
    # belongs under Countries, and everything else under no item at all rather than a
    # wrong one — `chrome()` matches this against its labels and marks nothing if it
    # does not recognise it.
    nav_active = "bulletin" if kind == "bulletin" else "countries"

    # The stylesheet set and the site chrome both come from `chrome_lib` — the same
    # `main.css` + `corpus.css` + page-type sheet every other page loads, and the same
    # header, nav and footer. This file used to build its own of each, which is how the
    # bulletin and every report came to carry a nav with no main-site row and three links
    # to pages that do not exist (documentation/house-style-review-2026-08-24.md §2).
    #
    # `base` is passed rather than a depth because this is the one builder that emits a
    # document twice: once for the web at a relative path, once for WeasyPrint at `file://`,
    # which has no notion of relative. `screen_only` marks the chrome that `report.css`
    # hides in print, where `.print-masthead` stands in for it on page one.
    css_dir = SITE / "assets" / "css"
    if absolute:
        sheets = styles(0, "report.css", base=css_dir.parent.as_uri())
        logo = (BUILD / "assets" / "logo.png").as_uri()
        page_chrome = chrome(nav_active, base=(BUILD / "assets").as_uri(), screen_only=True)
    else:
        # **How far up `assets/` is, counted from the directory the page lands in** — not the
        # constant `../../` this held until 2026-08-21. That constant was right for the only two
        # trees that existed when it was written, `reports/{unit}/` and `topics/{slug}/`, and
        # wrong for the bulletins the moment they arrived: `site/bulletins/` is one level down,
        # so both stylesheets and the logo resolved above `site/` and the two bulletin pages had
        # been served unstyled since 2026-08-17. Nothing caught it because a page with no CSS is
        # a page, and `--no-pdf` meant no PDF was cut where the breakage would have been obvious.
        up = "../" * len(rel.split("/"))
        # `?v=` on the stylesheets and the script, never on the PDF's `file://` URIs above.
        sheets = styles(0, "report.css", base=f"{up}assets",
                        version=lambda s: asset_version(css_dir / s))
        logo = f"{up}assets/logo.png"
        page_chrome = chrome(nav_active, base=f"{up}assets", screen_only=True)

    # The bulletin's country filter *(Bill, 2026-08-21)*. An external file rather than an inline
    # block: it is 120 lines, it is one page's behaviour, and inlining would put it in the
    # template every other document is built from. Never in the PDF pass — WeasyPrint runs no
    # script, so the tag would be a `file://` reference to something that does nothing.
    page_script = ""
    if kind == "bulletin" and not absolute:
        js = SITE / "assets" / "js" / "bulletin-filter.js"
        page_script = (f'<script src="{up}assets/js/bulletin-filter.js'
                       f'{asset_version(js)}" defer></script>')

    # A document rendered without a PDF must not advertise one *(Bill, 2026-08-17)*. The download
    # button and the `This file` row both name a file that was never cut, so they come out
    # together rather than being left to 404.
    #
    # **`Derived from` and `Verify` were removed on 2026-08-18** *(Bill)*. The commitment this
    # colophon makes to a reader is a moral one rather than a legal one, and the two rows were
    # the legal reading of it — a commit SHA to be produced on demand, and an instruction to
    # hash the file and look the hash up. What is owed instead is that the document says what it
    # is and when it was cut, which is what the rows that remain do. The `Verify` row also named
    # a manifest that was never built, so it had been asking readers to check against nothing.
    # **The button says `↓ PDF` and sits beside the byline** *(Bill, 2026-08-21)*. *Download* is
    # what the arrow already says, and a button on its own line below the byline had the header
    # ending on a call to action rather than on what the document is.
    if pdf:
        download = (f'<a href="{SITE_BASE}/{rel_pdf}.pdf" class="btn btn--accent" '
                    f'style="font-size:0.8rem;">&darr; PDF</a>')
        colophon_rows = f"          <dt>This file</dt><dd>{SITE_BASE}/{rel_pdf}.pdf</dd>"
    else:
        download = ""
        colophon_rows = f"          <dt>This file</dt><dd>{url_html}</dd>"

    # **`Current edition` comes off the bulletin** *(Bill, 2026-08-21)*. On a report it points a
    # reader holding a dated PDF at the live page, which is the whole reason the row exists. The
    # bulletin has one page, that page is the current edition, and the row printed its own
    # address back at whoever was already on it.
    current_row = ("" if kind == "bulletin" else
                   f'          <dt>Current edition</dt>'
                   f'<dd><a href="{url_html}">{url_html}</a></dd>\n')

    # **The retention promise goes on the PDF, not only on the page** (`bulletin-archive.md`).
    # A reader who downloads the file may never see the page it came from, and §9's commitment
    # is that a document says plainly what it is, when it was cut and that it is not revised —
    # a file that will 404 in a week and does not say so fails that on its own terms, for
    # exactly the reader §9 was written about. So the row is inside the colophon and travels
    # into the PDF with everything else, and it names the **date** rather than the interval:
    # *kept for a week* asks the reader to remember when they downloaded it.
    if kind == "bulletin" and pdf:
        until = bulletin_editions.expires_on(edition)
        current_row += (
            f'          <dt>Retention</dt><dd>Kept until {until}. Older bulletins: the '
            f'<a href="{SITE_BASE}/countries/">country pages</a> and the monthly reports.</dd>\n')
        # **Not in the PDF.** The control needs a script to do anything and the PDF runs none,
        # so it renders `hidden` there for ever — and a `<dt>Earlier editions</dt>` with nothing
        # beside it is the same fault as the download button that named a file nobody cut.
        if not absolute:
            current_row += archive_picker(archive or [], edition)

    doc = TEMPLATE.format(
        title=title,
        download=download,
        colophon_rows=colophon_rows,
        current_row=current_row,
        kicker=kicker,
        header_mod=header_mod,
        page_script=page_script,
        byline=byline,
        edition_display=edition_display,
        colophon_notes=BULLETIN_NOTES if kind == "bulletin" else REPORT_NOTES,
        description=(f"{kind_label} — {title}. Edition of {edition_display}." if kind_label
                     else f"{title}: {subtitle}"),
        short_title=h1 or title,
        h1=h1 or title,
        subtitle=subtitle,
        body=html_body,
        styles=sheets, chrome=page_chrome, foot=foot(), logo=logo,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        edition=edition,
        permalink_html=url_html,
        current_url=url_html,
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
           pdf: bool = True, force: bool = False,
           repage: bool = False) -> tuple[Path, Path | None, bool]:
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

    **The bulletin is the exception, because it is the one document whose freshness is news**
    *(Bill, 2026-08-21)*. A sweep that brings in fifty sources of which none carries a date in
    the bulletin's two-day window has still updated the bulletin: we looked, and nothing was
    published. A page that goes on saying *last updated the 20th* through that reports neglect
    where there was work, and the reader cannot tell the two apart. So for `type: bulletin` a
    held-off render still rewrites the **page**, under the edition it is already holding, and
    leaves the **PDF** alone. That is not the disagreement the paragraph above forbids: the
    byline is a claim about the material and moves with the sweep, while the colophon names the
    dated file it is offering and moves only when the material does. A PDF is a snapshot and is
    entitled to the stamp it was cut with.

    **`--repage` gives every document the mechanism the bulletin has, and only that mechanism**
    *(Bill, 2026-08-24)*. It rewrites the page under the edition already held and does not go
    near the PDF, so no edition is minted and no published file is revised. It exists because
    the paragraph above conflates two things the site treats differently. The dated PDF is the
    citable artefact and §9 protects its bytes absolutely. The HTML at `AGO-status.html` is an
    **undated URL** — a view that has always shown whatever the current edition is — and nothing
    can cite its bytes, because they were never promised to stay still. A change to the site
    chrome therefore has no business waiting for a document's content to move: the alternative
    on the day the chrome changed was `--force`, which would have cut 241 new dated PDFs to fix
    a navigation bar, and leaving 241 served pages carrying a nav with three links to pages that
    do not exist. Neither is what §9 is for.

    The guard is that the page is rebuilt **from the held edition**, so the byline, the colophon
    and the download link go on naming the same PDF they named before; and it is written only if
    the bytes differ, so a run over a document whose chrome has not changed touches nothing.

    `--edition` and `--force` are deliberate re-cuts and skip the gate. They do not skip §9's
    same-day suffixing, though: a forced re-cut differs from what is already published — that is
    what it is for — so writing it over the published name would change the bytes under a
    citation, which is the failure the suffix exists to prevent."""
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_head, body_head = frontmatter(md_path.read_text(encoding="utf-8"))
    rec = record(body_head)
    is_bulletin = meta_head.get("type") == "bulletin"
    today = date.today().isoformat()

    held = None if (edition or force) else held_edition(md_path, out_dir, rec)
    if held is not None:
        html_path = out_dir / f"{stem_html_of(md_path)}.html"
        pdf_path = out_dir / f"{md_path.stem}-{held}.pdf" if pdf else None
        if pdf_path is None or pdf_path.exists():
            if is_bulletin or repage:
                # The page is refreshed so the byline is current; the edition passed in is the
                # one already held, so the download link and the colophon go on naming the PDF
                # that is there. `rec` is taken over the body, which has not moved, so the gate
                # holds again next time rather than treating its own refresh as a change.
                #
                # Written only where the bytes differ. A refresh that rewrites an identical
                # page is churn a reader never sees and a diff always does.
                #
                # **`newline=""` is what makes that comparison mean anything** *(2026-08-22)*.
                # Without it Windows translates every `\n` on the way out while the read above
                # translates every `\r\n` back on the way in, so the two never disagree about
                # line endings and the file on disk quietly diverges from the one in git — a
                # 1,205-line diff on a document nothing had changed. Both writes here carry it,
                # and so does `bulletin.py`.
                #
                # **A held-off render writes no manifest entry, because no PDF was cut** — but
                # it does rebuild the listing, which is how a deletion reaches the picker. The
                # rebuild drops anything whose file has gone or whose week is up, so the page
                # this writes offers only editions that are still there. It comes free: the
                # page was being rewritten anyway (`bulletin-archive.md`).
                archive: list[dict] = []
                if is_bulletin:
                    archive = bulletin_editions.refreshed(out_dir, today)
                    if archive != bulletin_editions.load(out_dir).get("editions", []):
                        bulletin_editions.save(out_dir, archive)
                served, _, _, _, _ = build_document(md_path, held, absolute=False, pdf=pdf,
                                                    archive=archive)
                if not html_path.exists() or html_path.read_text(encoding="utf-8") != served:
                    html_path.write_text(served, encoding="utf-8", newline="")
            return html_path, pdf_path, False
        # The page names an edition whose PDF is not there — a file deleted by hand, or a run
        # that died between the two writes. Cut it again under **its own** name rather than
        # minting a new one: the published URL is the thing being repaired, not superseded.
        edition = held

    # A cut edition never lands on a name that is already taken (§9). Only when the renderer is
    # choosing the name: an explicit `--edition` is an operator naming one exactly, and the
    # repair above is restoring one that was published.
    if edition is None and pdf:
        edition = editions.next_edition(
            out_dir, md_path.stem, date.today().isoformat())

    # The listing the page will show, with the edition being minted folded in. Computed before
    # the page is built because the picker is rendered into it, and persisted only after
    # WeasyPrint has actually written the file — a manifest that names a PDF a failed run never
    # cut would be the one thing this listing must never be, which is wrong about the directory
    # it describes.
    archive: list[dict] = []
    if is_bulletin and pdf and edition:
        archive = bulletin_editions.refreshed(out_dir, today, adding={
            "edition": edition, "file": f"{md_path.stem}-{edition}.pdf",
            "compiled": meta_head.get("compiled", ""),
            "items": int(meta_head.get("items") or 0), "bytes": 0})

    served, stem_html, stem_pdf, edition, _ = build_document(
        md_path, edition, absolute=False, pdf=pdf, archive=archive)

    html_path = out_dir / f"{stem_html}.html"
    pdf_path = out_dir / f"{stem_pdf}.pdf" if pdf else None
    # Overwriting in place fails on some synced mounts; replace instead. The
    # HTML is always rewritten (its name never changes); the PDF only
    # replaces the one matching this edition — earlier-dated PDFs are a
    # different filename and are left alone, which is what retains them (§9).
    for f in (html_path, pdf_path):
        if f is not None and f.exists():
            f.unlink()
    html_path.write_text(served, encoding="utf-8", newline="")

    if pdf_path is None:
        return html_path, None, True

    for_pdf, _, _, _, _ = build_document(md_path, edition, absolute=True, pdf=True,
                                         archive=archive)
    from weasyprint import HTML  # imported late: only the PDF path needs it
    HTML(string=for_pdf, base_url=str(SITE / "assets" / "css")).write_pdf(pdf_path)

    # Now the file exists, so the entry can carry its real size and the manifest can be trusted.
    if is_bulletin:
        bulletin_editions.record_cut(
            out_dir, edition, pdf_path.name, meta_head.get("compiled", ""),
            int(meta_head.get("items") or 0), today)

    return html_path, pdf_path, True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("markdown", type=Path)
    # Default deferred to the source: a topic document renders under site/topics/, a unit report
    # under site/reports/, and the permalink in the page agrees with where the file lands. An
    # explicit --out still wins and still takes {unit} beneath it.
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--edition", default=None)
    # **The bulletin cuts a PDF again** *(Bill, 2026-08-21, `prep/bulletin.md` 17)*, reversing the
    # HTML-only ruling of 2026-08-17. The reasoning then was that a bulletin is superseded the
    # next morning, so a dated PDF archives the same news twice; what that missed is that a
    # superseded document is exactly the one a reader wants a copy of, because the page will not
    # be showing it tomorrow. The flag stays for a caller that wants a page without one.
    ap.add_argument("--no-pdf", action="store_true", help="write the HTML and no PDF")
    # Escape hatch for the content gate: a template or stylesheet change moves nothing in the
    # source, so nothing would re-render without it. Re-cutting every document is a decision
    # (241 editions), which is why it is a flag and not the default.
    ap.add_argument("--force", action="store_true",
                    help="cut a new edition even if the content has not moved")
    # The counterpart to --force, and the one to reach for after a chrome or stylesheet change:
    # refresh the served page under the edition already held, touching no PDF and minting
    # nothing. See render() for why an undated HTML view is not what §9 protects.
    ap.add_argument("--repage", action="store_true",
                    help="rewrite the served page under the held edition; no PDF, no new edition")
    args = ap.parse_args()

    src = args.markdown if args.markdown.is_absolute() else CORPUS / args.markdown
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 2

    rel = site_rel(src)                       # `reports/KEN`, `topics/dpi-pay`, `bulletins`
    out_dir = SITE / rel if args.out is None else args.out / rel.split("/")[-1]
    html_path, pdf_path, minted = render(src, out_dir, args.edition,
                                         pdf=not args.no_pdf, force=args.force,
                                         repage=args.repage)

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
