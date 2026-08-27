#!/usr/bin/env python3
"""methodology.py — the Methodology page and its lookups annex.

    python scripts/methodology.py  -> site/methodology/index.html
                                      site/methodology/lookups/index.html

**The whole page is `content/methodology.md`.** There is no template here beyond the
site chrome: the file is written as markdown with headings and sub-headings, and
this converts it and wraps it. That is different from every other builder in
`scripts/`, and deliberately so — the other pages are compiled views over the base
with prose in the gaps, whereas this one *is* prose, and nothing about it is
derived from anything. A builder that offered slots would be inventing structure
for a document whose structure is the author's business.

`content/methodology-lookups.md` builds the same way to `site/methodology/lookups/`,
with two additions: every `##` gets an id (the markdown `toc` extension slugifies
it — "National newspapers" -> `#national-newspapers`) so the methodology page and
other intro notes can deep-link a section, and a contents strip of those anchors
sits at the top of the page.

This file replaced `method.py` when the page renamed (2026-08-27, Bill).
`site/method/` is kept as a redirect stub because the old URL sat in the baked
chrome of every published page; the stub is written by hand, not built here.

Uses `copy_lib` only in spirit: `##` in these files is a section heading of the
document, not a key, so both are read whole.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import markdown
from chrome_lib import chrome, foot, styles  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
CONTENT = CORPUS / "content" / "methodology.md"
LOOKUPS = CORPUS / "content" / "methodology-lookups.md"
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
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container">
    <article class="article-body">
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


def convert(md_path: Path) -> str:
    return markdown.markdown(
        md_path.read_text(encoding="utf-8"),
        extensions=["tables", "attr_list", "sane_lists", "toc"])


def slug(heading: str) -> str:
    """The id the `toc` extension assigns — kept in step by test, not by import."""
    return re.sub(r"[^\w\s-]", "", heading.lower()).strip().replace(" ", "-")


def contents_strip(md_path: Path) -> str:
    """The site's one idiom for an in-page nav — `.article-toc` in main.css:
    terracotta small caps separated by middots, closed below by a single rule
    (the bulletin's category bar is the sibling use)."""
    h2s = [ln[3:].strip() for ln in md_path.read_text(encoding="utf-8").splitlines()
           if ln.startswith("## ")]
    sep = '\n<span class="article-toc__sep" aria-hidden="true">&middot;</span>\n'
    links = sep.join(f'<a href="#{slug(h)}">{h}</a>' for h in h2s)
    return (f'<nav class="article-toc" aria-label="Sections of this page">\n'
            f'{links}\n</nav>\n')


def indent(html: str) -> str:
    return "\n".join("      " + ln if ln.strip() else ln for ln in html.splitlines())


def build(md_path: Path, out_dir: Path, *, title: str, description: str,
          canonical: str, depth: int, prefix: str = "") -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(PAGE.format(
        title=title, description=description, canonical=canonical,
        base=SITE_BASE, main=MAIN_SITE,
        chrome=chrome('methodology', depth=depth), foot=foot(depth=depth),
        styles=styles(depth, "home.css", "country.css"),
        body=indent(prefix + convert(md_path)),
        source=md_path.relative_to(CORPUS).as_posix(),
        built=date.today().isoformat(),
    ), encoding="utf-8")
    return len(md_path.read_text(encoding="utf-8").split())


def main() -> int:
    for f in (CONTENT, LOOKUPS):
        if not f.exists():
            raise SystemExit(
                f"methodology.py: {f.relative_to(CORPUS)} is missing. The page is "
                f"that file; there is nothing to build without it.")

    words = build(
        CONTENT, OUT, title="Methodology",
        description=("How the Data Landscapers corpus is built: what is collected, "
                     "how it is classified, how figures are dated, and what the "
                     "base does not claim."),
        canonical=f"{SITE_BASE}/methodology/", depth=1)
    print(f"methodology: {words:,} words -> site/methodology/index.html")

    words = build(
        LOOKUPS, OUT / "lookups", title="Methodology — lookups",
        description=("The fixed lists behind the corpus: country and region codes, "
                     "the topic taxonomy, and the journals, newspapers and "
                     "institutions the sweeps search."),
        canonical=f"{SITE_BASE}/methodology/lookups/", depth=2,
        prefix=contents_strip(LOOKUPS))
    print(f"methodology: {words:,} words -> site/methodology/lookups/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
