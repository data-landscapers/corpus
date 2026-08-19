#!/usr/bin/env python3
"""method.py — the Method page.

    python scripts/method.py       -> site/method/index.html

**The whole page is `content/method.md`.** There is no template here beyond the
site chrome: the file is written as markdown with headings and sub-headings, and
this converts it and wraps it. That is different from every other builder in
`scripts/`, and deliberately so — the other pages are compiled views over the base
with prose in the gaps, whereas this one *is* prose, and nothing about it is
derived from anything. A builder that offered slots would be inventing structure
for a document whose structure is the author's business.

`{base}/method/` has been in the site nav on five page types since the nav was
written and has 404'd the whole time (2026-08-19). That is the immediate reason
this exists; the page being worth having is the other one.

Uses `copy_lib` only for its file-loading and markdown conversion, not for its
block splitting: `##` in `content/method.md` is a section heading of the document,
not a key. So this reads the file whole.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import markdown
from chrome_lib import chrome, foot  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
CONTENT = CORPUS / "content" / "method.md"
OUT = CORPUS / "site" / "method"

SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

CHROME = chrome('method', depth=1)

FOOT = foot(depth=1)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Method — Data Landscapers</title>
<meta name="description" content="How the Data Landscapers corpus is built: what becomes a source, how it is classified, how figures are dated, and what the base does not claim.">
<link rel="canonical" href="{base}/method/">
<link rel="stylesheet" href="../assets/css/main.css">
<link rel="stylesheet" href="../assets/css/home.css">
<link rel="stylesheet" href="../assets/css/country.css">
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
        <dt>Source</dt><dd><code>content/method.md</code> &mdash; the page is that file, converted</dd>
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


def main() -> int:
    if not CONTENT.exists():
        raise SystemExit(
            f"method.py: {CONTENT.relative_to(CORPUS)} is missing. The page is that "
            f"file; there is nothing to build without it.")

    body = markdown.markdown(
        CONTENT.read_text(encoding="utf-8"),
        extensions=["tables", "attr_list", "sane_lists", "toc"])

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(PAGE.format(
        base=SITE_BASE, main=MAIN_SITE, chrome=CHROME, foot=FOOT,
        body="\n".join("      " + ln if ln.strip() else ln for ln in body.splitlines()),
        built=date.today().isoformat(),
    ), encoding="utf-8")

    words = len(CONTENT.read_text(encoding="utf-8").split())
    print(f"method: {words:,} words -> site/method/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
