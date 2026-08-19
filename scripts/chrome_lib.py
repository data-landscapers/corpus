#!/usr/bin/env python3
"""chrome_lib.py — the site header, the Corpus nav and the footer. One copy.

    from chrome_lib import chrome, foot
    CHROME = chrome("finance", depth=1)     # site/finance/index.html
    FOOT   = foot(depth=1)

`depth` is how many directories the page sits below `site/`, and decides the
relative path to `assets/`: the home page is 0, `site/finance/index.html` is 1,
`site/countries/ZAF/finance.html` is 2. Everything else on the page is a
site-absolute URL and does not care.

**Why this exists.** The same header was written out five times — in `home.py`,
`country.py`, `topic-page.py`, `catalogue.py` and `finance.py` — differing only in
that path and in which nav item carries `class="active"`. On 2026-08-19 Bill
noticed the Data Landscapers header was missing from the Finance page and present
everywhere else: `finance.py` had been given a cut-down chrome when it was a shell
(a bare logo image and a single nav link), and when the page stopped being a shell
nobody went back for it. That is the failure mode of five copies, and it will
happen again on the next one — a copy nothing compares against does not announce
that it has fallen behind.

The nav is the site's own structure and belongs in code rather than in
`content/`: it is not prose, it does not want an editor, and a wrong link here is
a 404 rather than a sentence that reads badly.
"""
from __future__ import annotations

from datetime import date

SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

# label -> href, in the order they appear. Countries, Regions and Topics are
# sections of the home page; Finance, Catalogue and Method are pages of their own
# (Bill, 2026-08-19 — before that the last three were home-page anchors too).
NAV = [
    ("Countries", f"{SITE_BASE}/#countries"),
    ("Regions", f"{SITE_BASE}/#regions"),
    ("Topics", f"{SITE_BASE}/#topics"),
    ("Finance", f"{SITE_BASE}/finance/"),
    ("Catalogue", f"{SITE_BASE}/catalogue/"),
    ("Method", f"{SITE_BASE}/method/"),
]

# The key a page passes as `active`, matched case-insensitively against the label.
# A page that is not in the nav at all — a country page, a topic page — passes
# whichever section it belongs under, or None.
_MAIN_NAV = ["writing", "lab", "portfolio", "about", "contact", "search"]


def assets(depth: int) -> str:
    return "../" * depth + "assets"


def chrome(active: str | None = None, depth: int = 1, bulletin: bool = False) -> str:
    """The masthead and the Corpus nav, ready to drop into a page template.

    `bulletin=True` adds the Bulletin item the home page carries and no other page
    does, because it links an anchor that only exists there."""
    a = (active or "").strip().lower()

    main_links = "\n".join(
        f'        <a href="{MAIN_SITE}/{p}/">{p.capitalize()}</a>' for p in _MAIN_NAV)

    items = ([("Bulletin", f"{SITE_BASE}/#bulletin")] if bulletin else []) + NAV
    corpus_links = "\n".join(
        '      <a href="%s"%s>%s</a>'
        % (href, ' class="active"' if label.lower() == a else "", label)
        for label, href in items)

    return f"""  <header class="site-header">
    <div class="site-header__inner">
      <a href="{MAIN_SITE}/" class="site-logo">
        <img src="{assets(depth)}/logo.png" alt="Data Landscapers" class="site-logo__img">
        <span class="site-logo__text">Data Landscapers
          <span class="site-logo__sub">Mapping Africa&rsquo;s data landscape</span>
        </span>
      </a>
      <nav class="site-nav" aria-label="Main navigation">
        <a href="{SITE_BASE}/" class="active">Corpus</a>
{main_links}
      </nav>
    </div>
  </header>

  <nav class="corpus-nav" aria-label="Corpus navigation">
    <div class="corpus-nav__inner">
{corpus_links}
    </div>
  </nav>"""


def foot(depth: int = 1, year: int | None = None) -> str:
    """The footer. `depth` is unused today — the footer holds no relative paths —
    and is taken anyway so that a caller need not know that, and so adding one
    later is a change here rather than at five call sites."""
    return f"""  <footer class="site-footer">
    <div class="site-footer__inner">
      <p class="site-footer__copy"><a href="https://creativecommons.org/licenses/by/4.0/" style="color:inherit;border-bottom:none;">CC BY 4.0</a> {year or date.today().year} Bill Anderson / Data Landscapers Ltd &nbsp;·&nbsp; Registered in the UK · Co. No. 16040544</p>
      <div class="site-footer__links">
        <a href="{MAIN_SITE}/">data-landscapers.io</a>
        <a href="{SITE_BASE}/method/">Method</a>
      </div>
    </div>
  </footer>"""


if __name__ == "__main__":
    print(chrome("finance", depth=1))
    print(foot(depth=1))
