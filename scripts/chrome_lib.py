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

# label -> href, in the order they appear. Countries & Regions and Topics are
# sections of the home page; Finance, Catalogue and Methodology are pages of their own
# (Bill, 2026-08-19 — before that the last three were home-page anchors too).
NAV = [
    ("Bulletin", f"{SITE_BASE}/bulletin/"),
    # A page of its own since 2026-08-24 (Bill), so the nav points at it rather
    # than at the home page's anchor. `/countries/` used to hold the 54
    # per-country folders and no index, which is why it was one of the three
    # dead links this file's own note warned a private copy would accumulate.
    #
    # **Renamed from "Countries" on 2026-09-02** (Bill): the region matrix moved
    # to the bottom of this same page rather than getting an address of its own,
    # so the label now names both halves of what `/countries/` holds. The URL is
    # unchanged — `active` matching below keys on the "countries" prefix rather
    # than the full label so every existing caller still lights this item up.
    ("Countries & Regions", f"{SITE_BASE}/countries/"),
    # A page of its own since 2026-08-24 (Bill), the same move the countries
    # matrix made that morning: `/topics/` held the 48 topic and category
    # folders and no index, so the one URL a reader would guess 404'd while
    # every page beneath it resolved.
    ("Topics", f"{SITE_BASE}/topics/"),
    ("Finance", f"{SITE_BASE}/finance/"),
    ("Catalogue", f"{SITE_BASE}/catalogue/"),
    # Renamed from "Method" at /method/ on 2026-08-27 (Bill); /method/ keeps a
    # redirect stub because it sat in every published page's baked chrome.
    ("Methodology", f"{SITE_BASE}/methodology/"),
]

# The key a page passes as `active`, matched case-insensitively against the
# *start* of the label rather than the whole of it — "countries" against
# "Countries & Regions" — so a caller naming a nav item's old one-word label
# still lights it up after a rename. A page that is not in the nav at all — a
# country page, a topic page — passes whichever section it belongs under, or
# None.
# label -> path on the main site. Pairs rather than bare slugs since 2026-08-27:
# the Lab merged into Writing upstream (nav item removed here the same day), and
# Writing's label became "Work in progress" while its path stayed /writing/ —
# so label and path can no longer be derived from one another.
_MAIN_NAV = [
    ("Work in progress", "writing"),
    ("Portfolio", "portfolio"),
    ("About", "about"),
    ("Contact", "contact"),
    ("Search", "search"),
]


# The Google Analytics 4 measurement ID — the same property as the main site
# (`_config.yml` → `google_analytics`), so both sites report into one stream
# and the hostname dimension separates them. Change it there and here together.
GA_ID = "G-BF3X4N6YML"


def ga(ga_id: str = GA_ID) -> str:
    """The GA4 tag, ready to drop into a page's <head>.

    The same snippet the main site carries in `_includes/google-analytics.html`,
    minus the Jekyll templating. It lives here for the reason everything in this
    file does: eight head templates would otherwise each carry a copy, and the
    ninth would be written without one. Templates take it as a `{ga}` field —
    never paste it inline, because the JS braces collide with `str.format`."""
    return f"""<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ga_id}');
</script>"""


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
        f'        <a href="{MAIN_SITE}/{path}/">{label}</a>' for label, path in _MAIN_NAV)

    items = NAV
    corpus_links = "\n".join(
        '      <a href="%s"%s>%s</a>'
        % (href, ' class="active"' if a and label.lower().startswith(a) else "", label)
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
        <a href="{SITE_BASE}/methodology/">Methodology</a>
      </div>
    </div>
  </footer>"""


if __name__ == "__main__":
    print(chrome("finance", depth=1))
    print(foot(depth=1))
