#!/usr/bin/env python3
r"""alerts.py — the alert sign-up and manage pages, and the two files the Worker reads.

    python scripts/alerts.py
      -> site/alerts/recent.json          the records an alert can match this month
      -> site/alerts/vocab.json           the place and topic vocabularies, as the menus use them
      -> site/alerts/index.html           sign up
      -> site/alerts/manage/index.html    edit what you hold

`documentation/catalogue-alerts.md` is the design record; Part 1 B is what this
implements and Part 2 is the prose, which lives in `content/alerts.md` and reaches
the pages through `copy_lib`. RENDER Step 5 runs this straight after `catalogue.py`,
because both read the same catalogue and the alert pages' menus have to carry the
same vocabulary the catalogue's facets do.

**The site stores no address and this script never sees one.** It publishes two data
files and two pages. Everything to do with a reader — the address, the confirmation,
the unsubscribe — is Buttondown's, and everything to do with an alert *definition* is
the Worker's KV. `design.md` §1 is what that is protecting.

## recent.json, and why it is 28 days of a 90-day rule

The file is the Worker's whole view of the catalogue: the cron reads it, matches each
alert against it, and sends what it finds. Two windows decide what is in it.

**The backfill rule (90 days)** keeps the alert about news. Of the 12,472 records
ingested in the 35 days to 2026-09-14, only 4,453 were published within 30 days of
ingest and 3,106 were over a year old — an alert built on ingest date alone would be
mostly archive material arriving as if it had just happened. A record passes if the
**end** of its publication period is no more than 90 days before it was ingested, so a
report found late still goes out and a 2019 paper does not. The end of the period, not
the date itself: `date_precision` says whether `2026-09` means a day, a month or a
year, and a record dated `2026` is as recent as 31 December 2026 for this purpose.

**The file window (28 days)** is not the send window. The Worker sends a window of at
most 21 days, so that a missed Monday catches up rather than dropping items — and it
can only catch up over records this file still carries. 28 gives it a week of slack.

**Nothing published is more than the catalogue download publishes.** The rows carry a
subset of `build-catalogue.py`'s `CSV_COLS` plus a hash of the URL, and
`scripts/test_alerts.py` asserts it: a column added to the catalogue's internals does
not reach this file by accident.

## The Turnstile site key

`TURNSTILE_SITE_KEY` below is the `corpus-alerts` widget's, set on 2026-09-16 (design
step C4, replacing the placeholder B built with). **A site key is public** and belongs
in the page; the secret that pairs with it is the Worker's `TURNSTILE_SECRET` binding
and never enters this repo. The build still prints a line if the constant is ever put
back to a placeholder, because a page whose form cannot submit looks entirely well.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import catalogue  # noqa: E402  — vocab() and csv_cols(), so the menus cannot drift from the facets
import taxonomy_lib  # noqa: E402
from chrome_lib import chrome, external_links, feedback, foot, ga, script, styles  # noqa: E402
from copy_lib import check, copy, copy_inline  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
OUT = CORPUS / "site" / "alerts"
CATALOGUE_JSON = CORPUS / "outputs" / "catalogue" / "raw-catalogue.json"

SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

RECENT_DAYS = 28
BACKFILL_DAYS = 90
MAX_PER_FACET = 5
MAX_ALERTS = 10

# The `corpus-alerts` Turnstile widget, created 2026-09-16 (design step C3). **The site
# key is public** — it is written into the page and every reader's browser has it. The
# secret that pairs with it is the Worker's `TURNSTILE_SECRET` binding and is never here.
TURNSTILE_SITE_KEY = "0x4AAAAAAE4PyA_1ozsqH54J"

# The columns of a `recent.json` row, all of them `CSV_COLS`, plus the row's own id.
ROW_COLS = ["title", "publisher", "published", "ingested", "places", "topics", "url"]

BLOCKS = ["title", "lede", "how", "what", "site", "several", "manage", "manage-title",
          "manage-lede",
          "manage-empty", "manage-saved", "manage-none", "feed", "privacy",
          "ok", "confirmed", "e-check", "e-input", "e-later", "e-blocked"]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- data

def parse_date(s: str) -> date | None:
    """`YYYY`, `YYYY-MM` or `YYYY-MM-DD` as a date, or None for anything else.

    A partial date parses to the **first** day of its period; `period_end` takes it
    to the last. Anything that is not one of the three shapes — an empty string, a
    range, a word — is None, and a record with no parseable `published` is out of
    the file entirely (the backfill rule has nothing to measure against)."""
    s = (s or "").strip()
    try:
        if re.fullmatch(r"\d{4}", s):
            return date(int(s), 1, 1)
        if re.fullmatch(r"\d{4}-\d{2}", s):
            return date(int(s[:4]), int(s[5:7]), 1)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
            return date.fromisoformat(s)
    except ValueError:                      # 2026-02-30 and its friends
        return None
    return None


def period_end(published: str, precision: str) -> date | None:
    """The last day the publication date could mean.

    `date_precision` is the catalogue's own field and takes `day`, `month` or `year`.
    Where it disagrees with the date's shape — a `month` precision on a full date —
    **the date wins**, because it is the thing that was read off the document. Where
    the precision is missing or unknown, the shape decides."""
    d = parse_date(published)
    if d is None:
        return None
    shape = len((published or "").strip())
    if shape >= 10:                          # YYYY-MM-DD: the day is the period
        return d
    if shape >= 7 or (precision or "") == "month":
        nxt = date(d.year + (d.month == 12), (d.month % 12) + 1, 1)
        return nxt - timedelta(days=1)
    return date(d.year, 12, 31)


def passes_backfill(rec: dict) -> bool:
    """True if the record is news rather than archive, by the 90-day rule."""
    end = period_end(rec.get("published", ""), rec.get("date_precision", ""))
    ing = parse_date(rec.get("ingested", ""))
    if end is None or ing is None:
        return False
    return (ing - end).days <= BACKFILL_DAYS


def record_id(rec: dict) -> str:
    """A stable 16-hex id for a record, from its URL, or its citation without one.

    The id is what an Atom `<id>` carries and what a feed reader keys on, so it has
    to survive a rebuild: it is taken from the record's published fields and never
    from its position in the file or from `slug`, which is internal."""
    url = (rec.get("url") or "").strip()
    basis = url or "|".join((rec.get("title") or "", rec.get("publisher") or "",
                             rec.get("published") or ""))
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def recent(items: list[dict], today: date) -> list[dict]:
    """The rows of `recent.json`: ingested inside the window, and not backfill."""
    cutoff = today - timedelta(days=RECENT_DAYS)
    rows = []
    for rec in items:
        ing = parse_date(rec.get("ingested", ""))
        if ing is None or ing < cutoff:
            continue
        if not passes_backfill(rec):
            continue
        row = {"id": record_id(rec)}
        for col in ROW_COLS:
            v = rec.get(col)
            row[col] = list(v) if isinstance(v, list) else (v or "")
        rows.append(row)
    rows.sort(key=lambda r: (r["ingested"], r["published"], r["title"]), reverse=True)
    return rows


def vocabularies() -> dict:
    """`{places: {code: label}, topics: {slug: label}}`, from the catalogue's own vocab.

    Both maps are in the order the menus want them: places with the regions first and
    the countries alphabetically after, topics in the taxonomy's own sequence. JSON
    objects keep insertion order in every runtime that matters here, and the page
    relies on it rather than re-sorting labels it did not choose."""
    places, regions, topics, _cats, torder = catalogue.vocab()
    ordered_places = {}
    for code in sorted(places, key=lambda k: places[k]):
        if code.startswith("X"):
            ordered_places[code] = places[code]
    for code in sorted(places, key=lambda k: places[k]):
        if not code.startswith("X"):
            ordered_places[code] = places[code]
    ordered_topics = {k: topics[k] for k in torder if k in topics}
    for k in sorted(topics):
        ordered_topics.setdefault(k, topics[k])
    return {"places": ordered_places, "topics": ordered_topics, "regions": regions}


# --------------------------------------------------------------------------- markup

def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def place_options(voc: dict) -> str:
    """The Country menu: an Any option, then Regions, then the countries A–Z.

    Grouped the way the catalogue's place facet is — regions head the list, because a
    reader looking for West Africa is not looking alphabetically — and with the same
    labels, because they come from the same `vocab()`."""
    regions = [(k, v) for k, v in voc["places"].items() if k.startswith("X")]
    countries = [(k, v) for k, v in voc["places"].items() if not k.startswith("X")]
    out = ['<option value="any">Any country</option>',
           '<optgroup label="Regions">']
    out += [f'<option value="{esc(k)}">{esc(v)}</option>' for k, v in regions]
    out += ["</optgroup>", '<optgroup label="Countries">']
    out += [f'<option value="{esc(k)}">{esc(v)}</option>' for k, v in countries]
    out += ["</optgroup>"]
    return "\n".join(out)


def topic_options(voc: dict) -> str:
    """The Topic menu, grouped by Level 1, in the taxonomy's order."""
    level1 = taxonomy_lib.level1s()
    out = ['<option value="any">Any topic</option>']
    group = None
    for k, v in voc["topics"].items():
        g = level1.get(k, "")
        if g != group:
            if group is not None:
                out.append("</optgroup>")
            out.append(f'<optgroup label="{esc(g or "Other")}">')
            group = g
        out.append(f'<option value="{esc(k)}">{esc(v)}</option>')
    if group is not None:
        out.append("</optgroup>")
    return "\n".join(out)


def picker(kind: str, label: str, options: str) -> str:
    """One labelled multi-select, with the cap said once beside it.

    **No `id`, and the label is an `aria-label` on the select.** The manage page
    clones its row from a `<template>`, so a `for`/`id` pair here would be a
    duplicate id on every row after the first; `data-pick` is how the script finds
    a select, on both pages, whether it was built here or cloned."""
    return f"""<div class="alert-pick">
  <span class="alert-pick__lab">{esc(label)}<span class="alert-pick__cap">up to {MAX_PER_FACET}</span></span>
  <select name="{kind}" multiple size="8" data-pick="{kind}" aria-label="{esc(label)}">
{options}
  </select>
</div>"""


# **The page script loads before Turnstile's, and Turnstile is told which callback to call.**
# `api.js` is async, so it normally arrives after `alerts.js` has run and found no
# `window.turnstile`; `alerts.js` then leaves `onloadTurnstileCallback` for it. Cloudflare
# calls that only if the script URL names it in `onload=` — without it (2026-09-16, step D5)
# the widget never rendered, no token was posted, and every sign-up came back `?e=check`.
# `alerts.js` goes first so the callback is defined before `api.js` can possibly run.
PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Data Landscapers</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
{robots}{styles}
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container alerts">
    <header class="article-header">
      {feedback}
      <h1 class="article-header__title">{h1}</h1>
      <div class="lede">{lede}</div>
    </header>

{body}

  </div>
  </main>

{foot}

<script>window.ALERTS = {config};</script>
{alerts_js}
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&amp;onload=onloadTurnstileCallback" async defer></script>
</div>
</body>
</html>
"""


def config(page: str, voc: dict) -> str:
    """The build-time data the page's script needs, as one JSON blob.

    The behaviour is a hand-kept asset (`site/assets/js/alerts.js`) and the data is
    built, which is the split every other page here uses: a vocabulary of 62 places
    and 38 topics does not belong in a file somebody edits, and a 400-line event
    handler does not belong in a Python string."""
    return json.dumps({
        "page": page,
        "site": SITE_BASE,
        "mainSite": MAIN_SITE,
        "turnstileKey": TURNSTILE_SITE_KEY,
        "maxPerFacet": MAX_PER_FACET,
        "maxAlerts": MAX_ALERTS,
        "places": voc["places"],
        "topics": voc["topics"],
        "messages": {
            "several": copy_inline("alerts", "several"),
            "ok": copy_inline("alerts", "ok"),
            "confirmed": copy_inline("alerts", "confirmed"),
            "e-check": copy_inline("alerts", "e-check"),
            "e-input": copy_inline("alerts", "e-input"),
            "e-later": copy_inline("alerts", "e-later"),
            "e-blocked": copy_inline("alerts", "e-blocked"),
            "manage-empty": copy_inline("alerts", "manage-empty"),
            "manage-saved": copy_inline("alerts", "manage-saved"),
            "manage-none": copy_inline("alerts", "manage-none"),
        },
    }, ensure_ascii=False, separators=(",", ":"))


def signup_body(voc: dict) -> str:
    """The sign-up form.

    **The form is a real form.** It posts `application/x-www-form-urlencoded` to the
    Worker and the Worker answers with a 303, so the browser's own navigation carries
    the result — no fetch, no JSON, and a page that is still on the reader's screen if
    the script did not load. What the script adds is the cap, the fragment preselect
    and the feed URL; none of the three is the difference between subscribing and not.
    """
    return f"""    <div class="alert-msg" id="msg" role="status" hidden></div>

    <div class="alert-cols">
      <form class="alert-form" method="post" action="/api/alerts/subscribe" id="signup">
        <div class="alert-picks">
{picker("places", "Country", place_options(voc))}
{picker("topics", "Topic", topic_options(voc))}
        </div>
        <p class="alert-note" id="several" hidden>{copy_inline("alerts", "several")}</p>

        <div class="alert-check">
          <label><input type="checkbox" name="site" value="1" id="site">
          <span>{copy_inline("alerts", "site")}</span></label>
        </div>

        <div class="alert-field">
          <label for="email">Email address</label>
          <input type="email" id="email" name="email" required autocomplete="email"
                 placeholder="you@example.com">
        </div>

        <div id="alerts-turnstile"></div>

        <button type="submit" class="btn" id="go">Set up alerts</button>
        <p class="alert-note">{copy_inline("alerts", "manage")}</p>
      </form>

      <aside class="alert-about">
        <h2>How it works</h2>
        {copy("alerts", "how")}
        <h2>What an alert covers</h2>
        {copy("alerts", "what")}
        <h2>Your address</h2>
        {copy("alerts", "privacy")}
      </aside>
    </div>

    <details class="alert-feed">
      <summary>No email — just a feed</summary>
      {copy("alerts", "feed")}
      <p><code id="feedurl">{SITE_BASE}/api/alerts/feed</code></p>
      <p id="feedmain" hidden>And for the main site: <code>{MAIN_SITE}/feed.xml</code></p>
    </details>
"""


def manage_body(voc: dict) -> str:
    """The manage page.

    The row template is markup rather than a string in the script, so the pickers on
    an added row are the same markup as the pickers on a loaded one — a `<template>`
    the browser clones. It carries the whole vocabulary twice over, which is the cost
    of not building a `<select>` from JSON in two places."""
    return f"""    <div class="alert-msg" id="msg" role="status" hidden></div>

    <div class="alert-manage" id="manage" hidden>
      <div class="alert-check">
        <label><input type="checkbox" id="site">
        <span>{copy_inline("alerts", "site")}</span></label>
      </div>

      <div id="rows"></div>

      <p class="alert-note" id="several" hidden>{copy_inline("alerts", "several")}</p>

      <button type="button" class="btn btn--sm" id="add">Add alert</button>
      <div id="alerts-turnstile"></div>
      <button type="button" class="btn" id="save">Save</button>
    </div>

    <p class="alert-note" id="nokey" hidden>This page opens from the link at the
    foot of an alert email. Open it from there to see your alerts.</p>

    <template id="rowtpl">
      <div class="alert-row">
        <div class="alert-picks">
{picker("places", "Country", place_options(voc))}
{picker("topics", "Topic", topic_options(voc))}
        </div>
        <button type="button" class="btn btn--sm alert-row__del" data-del="1">Delete</button>
      </div>
    </template>
"""


def page(*, page_name: str, h1: str, lede: str, title: str, description: str, url: str,
         depth: int, body: str, voc: dict, robots: str = "") -> str:
    """The finished page, with `external_links` run over it as the last pass.

    The same post-pass every other builder here ends with, and for the same reason:
    the outbound links on these pages come out of `content/alerts.md` through the
    Markdown converter, which is inside a library and has no call site to put a
    `rel` on."""
    return external_links(PAGE.format(
        title=esc(title), description=esc(description), canonical=f"{SITE_BASE}{url}",
        robots=robots, styles=styles(depth, "alerts.css"), main=MAIN_SITE, ga=ga(),
        chrome=chrome("catalogue", depth), feedback=feedback("Alerts", f"{SITE_BASE}{url}"),
        h1=esc(h1), lede=copy("alerts", lede), body=body, foot=foot(depth),
        config=config(page_name, voc), alerts_js=script("alerts.js", depth)))


# --------------------------------------------------------------------------- build

def write(path: Path, text: str) -> bool:
    """Write only when the bytes move, so a rebuild that changed nothing commits nothing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    check("alerts", BLOCKS)
    if not CATALOGUE_JSON.exists():
        raise SystemExit("alerts: no outputs/catalogue/raw-catalogue.json — "
                         "run scripts/rebuild.py --catalogue first")

    # UTC, because the Worker's window, its `sent:` keys and the Monday in the subject
    # are all UTC. A build run at 23:30 in London in June would otherwise write a file
    # dated a day ahead of the handler that reads it.
    today = datetime.now(timezone.utc).date()
    items = json.loads(CATALOGUE_JSON.read_text(encoding="utf-8"))["items"]
    rows = recent(items, today)
    voc = vocabularies()

    write(OUT / "recent.json", json.dumps(
        {"built": today.isoformat(), "days": RECENT_DAYS, "count": len(rows), "items": rows},
        ensure_ascii=False, separators=(",", ":")))
    write(OUT / "vocab.json", json.dumps(
        {"places": voc["places"], "topics": voc["topics"]},
        ensure_ascii=False, separators=(",", ":")))

    write(OUT / "index.html", page(
        page_name="signup", h1=copy_inline("alerts", "title"), lede="lede",
        title="Alerts",
        description="Weekly email alerts for new documents in the Corpus catalogue, "
                    "by country and topic.",
        url="/alerts/", depth=1, body=signup_body(voc), voc=voc))

    write(OUT / "manage" / "index.html", page(
        page_name="manage", h1=copy_inline("alerts", "manage-title"),
        lede="manage-lede", title="Your alerts",
        description="Change or stop your Data Landscapers alerts.",
        url="/alerts/manage/", depth=2, body=manage_body(voc), voc=voc,
        # Off the sitemap and out of the index: the page says nothing without a
        # subscriber id, and the id belongs in one reader's email, not in a crawl.
        robots='<meta name="robots" content="noindex, nofollow">\n'))

    print(f"alerts: {len(rows):,} records in the last {RECENT_DAYS} days "
          f"(of {len(items):,}), {len(voc['places'])} places, {len(voc['topics'])} topics "
          f"-> site/alerts/")
    if TURNSTILE_SITE_KEY.startswith("TURNSTILE-SITE-KEY"):
        print("alerts: the Turnstile site key is still the placeholder — the sign-up "
              "form will not submit until C4 replaces TURNSTILE_SITE_KEY and re-renders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
