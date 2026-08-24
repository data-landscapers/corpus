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
    ("Bulletin", f"{SITE_BASE}/bulletin/"),
    # A page of its own since 2026-08-24 (Bill), so the nav points at it rather
    # than at the home page's anchor. `/countries/` used to hold the 54
    # per-country folders and no index, which is why it was one of the three
    # dead links this file's own note warned a private copy would accumulate.
    ("Countries", f"{SITE_BASE}/countries/"),
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


def styles(depth: int = 1, *extra: str, base: str | None = None,
           version=None) -> str:
    """The stylesheet links, in load order, for a page `depth` below `site/`.

    `main.css` is a byte-identical copy of the website's and carries the whole
    house style; `corpus.css` follows it with the handful of rules only this
    site needs. **The order is the contract** — corpus.css overrides main.css
    (the sticky header, for one) and does nothing if it loads first.

    Pass any page-type sheet as `extra`: `styles(2, "report.css")`. Those come
    last and hold layout for that page type only, never identity
    (documentation/house-style.md → Where style lives).

    This exists for the same reason `chrome()` does. The link tags were written
    out in six builders, and when `corpus.css` was split out of `main.css` on
    2026-08-24 every one of them needed the same second line — which is exactly
    the edit that gets made in five places and missed in the sixth.

    `base` replaces the computed relative prefix outright, for the one caller
    that cannot use one: `render.py` cuts each document twice, and the PDF pass
    hands WeasyPrint `file://` URIs because a relative href has nothing to be
    relative to.

    `version` is a callable taking a sheet's filename and returning the suffix
    to hang off its href — `render.py`'s `?v=` cache-buster. It is a hook rather
    than a rule because the buster is only wanted on the served copies: the PDF
    pass reads the same files off disk, where a query string is part of the
    filename and the fetch simply fails."""
    root = base if base is not None else assets(depth)
    sheets = ["main.css", "corpus.css", *extra]
    return "\n".join(
        f'<link rel="stylesheet" href="{root}/css/{s}{version(s) if version else ""}">'
        for s in sheets)


def chrome(active: str | None = None, depth: int = 1, *,
           base: str | None = None, screen_only: bool = False) -> str:
    """The masthead and the Corpus nav, ready to drop into a page template.

    **Bulletin is an ordinary nav item now** *(Bill, 2026-08-21)*. It used to be added on the
    home page alone, behind a `bulletin=True` flag, because it linked `/#bulletin` — an anchor
    that exists on no other page. It is a page of its own at `/bulletin/` now, so it belongs in
    the same list as everything else and reaches every page in the site.

    `base` overrides the relative path to `assets/`, as in `styles()`, for the
    PDF pass. `screen_only` adds the class that `report.css` hides in print: a
    rendered document carries its own `.print-masthead` on page one instead,
    because a sticky screen header does not survive pagination.

    **`render.py` came onto this on 2026-08-24** *(house-style-review §2)*. It
    had grown a chrome of its own — no main-site row, a logo pointing at the
    corpus home rather than the website, and three links to pages that do not
    exist (`/data/`, `/regions/`, `/countries/`, all 404 on every bulletin and
    every report since they were written). Two copies of a nav is one nav and
    one liability; the liability was the one nobody was reading."""
    a = (active or "").strip().lower()
    hdr = " screen-only" if screen_only else ""
    root = base if base is not None else assets(depth)

    main_links = "\n".join(
        f'        <a href="{MAIN_SITE}/{p}/">{p.capitalize()}</a>' for p in _MAIN_NAV)

    items = NAV
    corpus_links = "\n".join(
        '      <a href="%s"%s>%s</a>'
        % (href, ' class="active"' if label.lower() == a else "", label)
        for label, href in items)

    return f"""  <header class="site-header{hdr}">
    <div class="site-header__inner">
      <a href="{MAIN_SITE}/" class="site-logo">
        <img src="{root}/logo.png" alt="Data Landscapers" class="site-logo__img">
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

  <nav class="corpus-nav{hdr}" aria-label="Corpus navigation">
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
