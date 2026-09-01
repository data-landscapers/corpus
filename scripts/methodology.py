#!/usr/bin/env python3
"""methodology.py — the Methodology page and its lookups annex.

    python scripts/methodology.py  -> site/methodology/index.html
                                      site/methodology/lookups/index.html
                                      site/methodology/document-lifecycle/index.html
                                      site/methodology/process-inventory/index.html

**The whole page is `content/methodology.md`.** There is no template here beyond the
site chrome: the file is written as markdown with headings and sub-headings, and
this converts it and wraps it. That is different from every other builder in
`scripts/`, and deliberately so — the other pages are compiled views over the base
with prose in the gaps, whereas this one *is* prose, and nothing about it is
derived from anything. A builder that offered slots would be inventing structure
for a document whose structure is the author's business.

**The annexes build the same way, from the same folder.** `/methodology/` is the
hub and three long documents hang off it, one directory each, named after the
content file: `methodology-lookups.md` -> `lookups/` (the fixed lists),
`document-lifecycle.md` -> `document-lifecycle/` (one document's journey through
the system, told as a story) and `process-inventory.md` -> `process-inventory/`
(the same system as a table of every procedure file). The hub carries a *See also*
line to the three and each annex carries one back; that line is written in the
markdown, not here, because it is prose and the page is its file (2026-09-01, Bill).

Two things this file adds to a page that its markdown cannot. Every `##` gets an id
(the markdown `toc` extension slugifies it — "National newspapers" ->
`#national-newspapers`) so any page can deep-link a section. And where a page asks
for one, a contents strip of those anchors sits at the top: `lookups` and
`document-lifecycle` have enough sections to want one, `process-inventory` has two
headings and does not.

`site/assets/css/methodology.css` is these pages' own stylesheet, and its whole
content is the process inventory's column widths. It replaced `country.css` in the
load list on 2026-09-01, which had been loading on every methodology page since the
rename without one of its selectors matching anything.

The `<h1>` is the page title passed here, so no content file carries one — the same
arrangement as the `<title>` tag, and it is why `methodology.md` and the lookups
open at `##`. Before 2026-09-01 there was no `<h1>` on these pages at all, which
`documentation/house-style.md` → *Type* requires one of.

This file replaced `method.py` when the page renamed (2026-08-27, Bill).
`site/method/` is kept as a redirect stub because the old URL sat in the baked
chrome of every published page; the stub is written by hand, not built here.

Uses `copy_lib` only in spirit: `##` in these files is a section heading of the
document, not a key, so both are read whole.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import markdown
from chrome_lib import chrome, foot, ga, styles  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
CONTENT_DIR = CORPUS / "content"
OUT = CORPUS / "site" / "methodology"

SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

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

    <article class="article-body{body_class}">
{body}
    </article>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Source</dt><dd><code>{source}</code> &mdash; the page is that file, converted</dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>
  </div>
  </main>

{foot}

</div>
</body>
</html>
"""


CODE = re.compile(r"(<code>)(.*?)(</code>)", re.S)
# After a `/` or a `-`, but not between two of them, and not at the very end.
BREAK_AFTER = re.compile(r"(?<=[/-])(?![/-])(?=\S)")


def soft_breaks(html: str) -> str:
    """A `<wbr>` after every `/` and `-` inside a `<code>` span.

    A filename is one unbreakable word to a browser, so a narrow column breaks
    `scripts/rebuild.py --reports all` after the `p` and starts the next line
    with `y`. `<wbr>` marks where a break is allowed without adding a character
    — nothing is inserted into the text, so the path still copies out whole —
    and the browser takes the last one that fits instead of chopping mid-word.
    `overflow-wrap` in `methodology.css` remains the fallback for a segment
    still too long for its column, which is what `--reports` would be.

    Applied to every page here, not just the one with narrow columns: a `<wbr>`
    where a break is never needed does nothing at all."""
    return CODE.sub(
        lambda m: m.group(1) + BREAK_AFTER.sub("<wbr>", m.group(2)) + m.group(3),
        html)


def convert(md_path: Path) -> str:
    return soft_breaks(markdown.markdown(
        md_path.read_text(encoding="utf-8"),
        extensions=["tables", "attr_list", "sane_lists", "toc"]))


def slug(heading: str) -> str:
    """The id the `toc` extension assigns — kept in step by test, not by import."""
    return re.sub(r"[^\w\s-]", "", heading.lower()).strip().replace(" ", "-")


def toc_bar(links: list[tuple[str, str]], label: str) -> str:
    """The site's one idiom for a jump bar — `.article-toc` in main.css: terracotta
    small caps separated by middots, closed below by a single rule (the bulletin's
    category bar is the sibling use). Links only, never a plain word: everything in
    the bar is styled by `.article-toc a`, so unlinked text sitting in it would come
    out as 18px body type beside 0.72rem mono."""
    sep = '\n<span class="article-toc__sep" aria-hidden="true">&middot;</span>\n'
    body = sep.join(f'<a href="{href}">{text}</a>' for href, text in links)
    return f'<nav class="article-toc" aria-label="{label}">\n{body}\n</nav>\n'


def see_also(current: str) -> str:
    """The other three pages of the set, from `PAGES`. From an annex the hub is one
    directory up and a sibling annex is `../<slug>/`; from the hub both are below."""
    up = "../" if current else ""
    links = [(up + p["slug"] + "/" if p["slug"] else (up or "./"), p["nav"])
             for p in PAGES if p["slug"] != current]
    return toc_bar(links, "Other pages in this section")


def contents_strip(md_path: Path) -> str:
    """This page's own `##` sections, as anchors."""
    h2s = [ln[3:].strip() for ln in md_path.read_text(encoding="utf-8").splitlines()
           if ln.startswith("## ")]
    return toc_bar([(f"#{slug(h)}", h) for h in h2s], "Sections of this page")


def indent(html: str) -> str:
    return "\n".join("      " + ln if ln.strip() else ln for ln in html.splitlines())


# The hub and its three annexes. `slug` is both the content file's stem (minus the
# `methodology-` prefix the lookups file still carries) and the directory under
# `/methodology/`; `h1` is the page's own title and `nav` the label the see-also
# bar uses for it — the two differ where a heading wants sentence case and a nav
# label wants to name the page. `strip` asks for a contents bar. `body` is an extra
# class on `<article>`, for the one page with geometry of its own; the rules are in
# `methodology.css` and there is no second use of it yet.
PAGES = [
    dict(source="methodology.md", slug="", h1="Methodology",
         title="Methodology", nav="Methodology", strip=False, body="",
         description=("How the Data Landscapers corpus is built: what is collected, "
                      "how it is classified, how figures are dated, and what the "
                      "base does not claim.")),
    dict(source="document-lifecycle.md", slug="document-lifecycle",
         h1="The life of a document", title="Methodology — document lifecycle",
         nav="Document Lifecycle", strip=True, body="",
         description=("One document's journey through Corpus, from a Somali news "
                      "site to three published reports: how it was found, screened, "
                      "classified, stored, and turned into a dated claim.")),
    dict(source="process-inventory.md", slug="process-inventory",
         h1="Process inventory", title="Methodology — process inventory",
         nav="Process Inventory", strip=False,
         body=" article-body--inventory",
         description=("Every procedure Corpus runs, in the order the work happens: "
                      "what each step does, and which instruction file or script "
                      "does it.")),
    dict(source="methodology-lookups.md", slug="lookups", h1="Process lookups",
         title="Methodology — process lookups", nav="Process Lookups",
         strip=True, body="",
         description=("The fixed lists behind the corpus: country and region codes, "
                      "the topic taxonomy, and the journals, newspapers, financiers "
                      "and institutions the sweeps search.")),
]


def build(md_path: Path, out_dir: Path, *, h1: str, title: str, description: str,
          canonical: str, depth: int, prefix: str = "", body_class: str = "") -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(PAGE.format(
        h1=h1, title=title, description=description, canonical=canonical,
        base=SITE_BASE, main=MAIN_SITE, body_class=body_class,
        chrome=chrome('methodology', depth=depth), foot=foot(depth=depth),
        styles=styles(depth, "home.css", "methodology.css"), ga=ga(),
        body=indent(prefix + convert(md_path)),
        source=md_path.relative_to(CORPUS).as_posix(),
        built=date.today().isoformat(),
    ), encoding="utf-8")
    return len(md_path.read_text(encoding="utf-8").split())


def main() -> int:
    for page in PAGES:
        src = CONTENT_DIR / page["source"]
        if not src.exists():
            raise SystemExit(
                f"methodology.py: content/{page['source']} is missing. The page is "
                f"that file; there is nothing to build without it.")

    for page in PAGES:
        src = CONTENT_DIR / page["source"]
        out = OUT / page["slug"] if page["slug"] else OUT
        depth = 2 if page["slug"] else 1
        url = f"/methodology/{page['slug']}/" if page["slug"] else "/methodology/"
        words = build(
            src, out, h1=page["h1"], title=page["title"],
            description=page["description"], canonical=f"{SITE_BASE}{url}",
            depth=depth, body_class=page["body"],
            prefix=see_also(page["slug"])
            + (contents_strip(src) if page["strip"] else ""))
        print(f"methodology: {words:,} words -> site{url}index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
