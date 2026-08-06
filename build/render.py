#!/usr/bin/env python3
"""render.py — one report, two outputs.

Renders a report from `upstream/` to HTML and PDF from a single template and a
single stylesheet (DESIGN.md §8). The PDF is not a second design: it is the
same document with the print rules in `report.css` applied.

    python build/render.py upstream/reports/KEN/KEN-status.md
    python build/render.py upstream/reports/KEN/KEN-status.md --out site/

Every artefact carries its edition line, its OSINT commit and its permanent
URL, per §9 — a downloaded PDF has to be verifiable on its own, away from the
site it came from.
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
UPSTREAM = CORPUS / "upstream"

SITE_BASE = "https://corpus.data-landscapers.com"
LICENCE = "CC BY 4.0"
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
ORG = "Bill Anderson / Data Landscapers Ltd"
COMPANY = "Registered in the UK · Co. No. 16040544"

KIND_LABEL = {
    "status": "Status report",
    "monthly": "Monthly update",
    "progress": "Twelve-month progress report",
}


def frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML-ish frontmatter from the body. The reports use flat
    scalar keys only, so a full YAML parser would be a dependency for nothing."""
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


def edition_hash(body: str) -> str:
    """§9: editions are minted on content change, hashing the body below the
    frontmatter — `compiled:` changes on every render and would mint an
    edition nightly for a document that had not moved."""
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def built_from() -> str:
    f = UPSTREAM / "BUILT-FROM"
    return f.read_text(encoding="utf-8").strip() if f.exists() else "(unknown)"


def parse_name(path: Path) -> tuple[str, str]:
    """`KEN-status.md` -> (KEN, status); `KEN-monthly-2026-07.md` -> (KEN, monthly)."""
    stem = path.stem
    parts = stem.split("-")
    unit = parts[0]
    kind = parts[1] if len(parts) > 1 else "report"
    return unit, kind


def strip_leading_h1(html: str) -> tuple[str, str]:
    """Pull the first <h1> out of the body so the template can place it."""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    if not m:
        return "", html
    return m.group(1), html[:m.start()] + html[m.end():]


def promote_standfirst(html: str) -> str:
    """The reports open with an italic *Compiled …* paragraph. It is a
    standfirst, not body copy, and reads as one once it is marked up as one.

    Only the container is changed; the inline markup inside it is left exactly
    as Markdown emitted it. An earlier version stripped the wrapping <em> as
    part of the same substitution, which silently broke the document: the
    source has `***Not held***` inside the italic run, so Markdown closes and
    reopens the <em> around it, and removing only the outer pair left an
    unclosed <em> that italicised every remaining page.
    """
    return re.sub(
        r"<p>(<em>Compiled.*?</em>)</p>",
        r'<div class="standfirst">\1</div>',
        html, count=1, flags=re.S,
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{title}">
<link rel="stylesheet" href="{css}">
</head>
<body>

<div class="running-header"><img src="{logo}" alt="">Data Landscapers · {short_title} · edition of {edition}</div>

<header class="masthead">
  <img src="{logo}" alt="Data Landscapers">
  <div>
    <div class="wordmark">Data Landscapers</div>
    <div class="tagline">Mapping Africa&rsquo;s data landscape</div>
  </div>
</header>

<h1>{h1}</h1>

<div class="meta">
  <span class="row"><b>{kind_label}</b> &middot; edition of {edition}</span>
  <span class="row">{permalink}</span>
</div>

{body}

<section class="colophon">
  <h2>About this document</h2>
  <dl>
    <dt>Edition</dt><dd class="edition">{edition}{seq_note}</dd>
    <dt>Current edition</dt><dd>{current_url}</dd>
    <dt>This file</dt><dd>{permalink}</dd>
    <dt>Derived from</dt><dd>Data Landscapers source base, commit <code>{commit}</code></dd>
    <dt>Verify</dt><dd>Hash this file and look it up in {manifest_url}</dd>
    <dt>Licence</dt><dd>{licence} &mdash; {licence_url}</dd>
  </dl>
  <p>Figures are dated because most are time-varying: a figure carries the date
  it was true, not the date you are reading it. Where the base holds no reliable
  statement, the document says <b>Not held</b> rather than leaving a silence &mdash;
  those are counted, and listed at the end.</p>
  <p>This is a dated edition and is not revised after publication. If a figure
  here has moved, the current edition will say so. &copy; {year} {org}. {company}</p>
</section>

</body>
</html>
"""


def render(md_path: Path, out_dir: Path, edition: str | None = None) -> tuple[Path, Path]:
    raw = md_path.read_text(encoding="utf-8")
    meta, body_md = frontmatter(raw)

    unit, kind = parse_name(md_path)
    edition = edition or meta.get("compiled") or date.today().isoformat()

    html_body = markdown.markdown(
        body_md,
        extensions=["tables", "attr_list", "md_in_html", "sane_lists"],
    )
    h1, html_body = strip_leading_h1(html_body)
    html_body = promote_standfirst(html_body)

    title = meta.get("title") or h1 or md_path.stem
    stem = f"{md_path.stem}-{edition}"
    rel = f"reports/{unit}/{stem}.pdf"

    doc = TEMPLATE.format(
        title=title,
        short_title=h1 or title,
        h1=h1 or title,
        body=html_body,
        css=(BUILD / "report.css").as_uri(),
        logo=(BUILD / "assets" / "logo.png").as_uri(),
        kind_label=KIND_LABEL.get(kind, kind.title()),
        edition=edition,
        seq_note="",
        permalink=f"{SITE_BASE}/{rel}",
        current_url=f"{SITE_BASE}/reports/{unit}/",
        manifest_url=f"{SITE_BASE}/manifest.csv",
        commit=built_from()[:12],
        licence=LICENCE,
        licence_url=LICENCE_URL,
        org=ORG,
        company=COMPANY,
        year=edition[:4],
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / f"{stem}.html"
    pdf_path = out_dir / f"{stem}.pdf"
    html_path.write_text(doc, encoding="utf-8")

    from weasyprint import HTML  # imported late: only the PDF path needs it
    HTML(string=doc, base_url=str(BUILD)).write_pdf(pdf_path)

    return html_path, pdf_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("markdown", type=Path)
    ap.add_argument("--out", type=Path, default=CORPUS / "site" / "reports")
    ap.add_argument("--edition", default=None)
    args = ap.parse_args()

    src = args.markdown if args.markdown.is_absolute() else CORPUS / args.markdown
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 2

    unit, _ = parse_name(src)
    html_path, pdf_path = render(src, args.out / unit, args.edition)

    body = frontmatter(src.read_text(encoding="utf-8"))[1]
    print(f"source   {src.relative_to(CORPUS)}")
    print(f"content  sha256 {edition_hash(body)[:12]}  (the edition key, §9)")
    print(f"html     {html_path.relative_to(CORPUS)}  {html_path.stat().st_size/1024:.0f} KB")
    print(f"pdf      {pdf_path.relative_to(CORPUS)}  {pdf_path.stat().st_size/1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
