#!/usr/bin/env python3
"""bulletin.py — the bulletin: one document over a two-day window.

    python scripts/bulletin.py --scan                 what is in the window, and what still needs a summary
    python scripts/bulletin.py --write {slug} --text "…"   record one item's summary (or pipe it on stdin)
    python scripts/bulletin.py --assemble             write outputs/bulletins/corpus-bulletin.md
    python scripts/bulletin.py --date 2026-08-16 …    run any of the above against another day

**One document, not two** *(Bill, 2026-08-21, `prep/bulletin.md`)*. The country bulletin is
retired: it covered the same window as the topic bulletin, item for item, and differed only in
how it grouped them — so a reader who opened both read every summary twice, and a run that
assembled both wrote every summary twice. What survives is the topic grouping, renamed simply
*Bulletin* and published at `/bulletin/`. The place dimension has not been lost; it is now on
the item, as a country box beside each headline linking to that country's page, which is what
the country bulletin's grouping was for and is one click rather than a second document.

**The window is publication, not acquisition** *(Bill, 2026-08-17)*. An item is in the bulletin
when its `published` date is the run's date or the day before it, and for no other reason. The
corpus acquires in batches — 184 records landed on 2026-08-16 carrying publication dates spread
across the ten days before it — so most runs select a handful and some select none. **An empty
window is a finished bulletin, not a failure**: the document says the window was empty and says
why, because a silence is indistinguishable from a build that did not run.

**A summary is written once and kept.** The window is two days wide and the build runs daily, so
almost every item is selected twice; re-summarising it the second time would burn the model stage
again and word the same item differently on consecutive days. `outputs/bulletins/summaries.json`
is the store, `--write` is the only way into it, and `--scan` asks for summaries only for items
that do not have one. Entries age out 30 days after publication, which is 28 days after the last
window that could cite them.

**Detail sits in one place and everything else points at it** *(Bill, 2026-08-17)*. An item
carrying five topics is written out once and the other four carry a cross-reference to it.

**The summary goes where the item first appears in the document** *(Bill, 2026-08-21)*, which
is the topic with the lowest sort order in `lookups/taxonomy.csv`, not the first topic the
record happens to list. Those were the same rule while the sections were ordered by the record's
own facet order and came apart the moment the taxonomy's order took over: on 2026-08-21 every
item under Governance — the taxonomy's first category, and so the first thing a reader meets —
opened *Summarised under …* and sent them further down the page for the text. A cross-reference
that points backwards is a cross-reference; one that points forwards is a document that will not
start.

**The section order is `lookups/taxonomy.csv`'s** *(Bill, 2026-08-21)*, both the Level-1 groups
and the Level-2 sections inside them, and the labels come from the same file. `taxonomy_lib`'s
own note said ordering waited on Bill reviewing the pages; for the bulletin he has. One
vocabulary rather than two is also what makes the topic nav bar at the head of the document
agree with the headings it jumps to.

**Last updated is OSINT's clock, not this script's** *(Bill, 2026-08-21)*. The build runs after
the sweep cycle closes, so the answer to *when was this page last updated* that is about the
reader's material rather than about us comes from the mirror's `logs/ingested_log.md`. Where the
mirror cannot be read the build clock stands in, and the run says so rather than passing one off
as the other.

**And the moment it names is when collection stopped, which is the start of ingest and not the
end of it** *(Bill, 2026-08-23)*. What the reader is being told is how recent the material is,
and the honest bound on that is the point after which nothing more could have been caught — the
end of the last sweep, `SWEEP-COUNTRY-DEEP` on a nightly cycle. Ingest is the step that reads
what collection staged, so its **start** is the proxy, minutes after the sweep it follows: on
2026-08-22 the last country-deep batch closed at 23:29 and the first slice ingested at 23:55.
The *newest* ingest stamp had been the byline and overstated it, because ingest of a night's
catch runs on for hours after collection has stopped — on 2026-08-23 it read 05:20 for material
that stopped moving at 23:55 the previous evening. Nothing was collected in those five and a
half hours; they were spent writing up what already had been. `osint_lib.ingest_started()`.

**The sweep cycle's own close is preferred over that proxy where the mirror carries it**
*(2026-08-26)*. Bill's ruling named the end of the last sweep; the start of ingest was only ever
the stand-in for a fact Corpus could not then read. `osint_lib.last_cycle_close()` reads it
directly, from the rotation table's `End` column, and the proxy has now been seen to fail: on
2026-08-25 ingest ran unbroken from a 15:30 bulletin top-up through a CMR status-acquire, a
reconcile and an acquire drain into the 21:12 nightly sweep, with no gap wider than 1h52m in it.
`INGEST_RUN_GAP` is four hours, so the run-walk found no boundary and reported 15:30 for material
that stopped moving at 22:57 — the documented failure mode, *merging two runs reports an earlier
start*, understating the page's freshness by five and a half hours on a day the sweep had run.

The proxy stays as the fallback, and the choice is guarded both ways. A close **older** than the
start of the newest ingest run is a stale rotation table, not a later fact, and is refused — a
mirror synced before the closing row was written would otherwise date the byline to yesterday's
cycle while today's catch sat on the page. A close in the future beyond `osint_lib.SKEW` is
refused on the same terms `_newest_stamp` refuses one, being a claim about work that has not
happened. In both cases the run falls back to `ingest_started()` and names which clock it used.

**The two stamps in the frontmatter answer two questions and are both kept.** `collected_to:` is
the byline's — when the material stopped moving. `compiled:` stays what it was, the newest ingest
stamp, and is what the edition picker shows against a dated PDF: not *when did we stop looking*
but *how late is the newest thing in this cut*, which is the question a reader choosing between
two cuts of one day is asking. They are minutes apart on a quiet night and hours apart on a busy
one, and collapsing them would lose one answer to keep the other.

**The stamp moves whenever the material was looked at, even when nothing came of it**
*(Bill, 2026-08-21)*. A sweep that admits fifty sources of which none carries a publication date
inside the two-day window has still updated this document: we looked, and nothing was published.
The stamp was suppressed in that case until Bill's ruling — the file was left alone on the
reasoning that its content had not moved — and the page then went on saying *last updated the
20th* through a night's work, which reports neglect where there was none and which a reader
cannot tell from the real thing.

**What the suppression was protecting is protected somewhere better.** The worry was
`render.py`'s edition gate: a stamp moving on its own would cut a dated PDF every night for a
document nobody had changed. The gate digests the body, which the stamp is not in, so it holds
off exactly as before — and `render.py` now refreshes the bulletin's **page** on a held-off
render while leaving the **PDF** alone. The byline is a claim about the material and moves with
the sweep; the dated file is a snapshot and keeps the stamp it was cut with.

Anchors resolve because `render.py` runs Markdown's `toc` extension, which gives every heading an
id from the same `slugify` this module imports. Two implementations of that slug is how the links
would come to point at nothing, so there is one.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from markdown.extensions.toc import slugify

sys.path.insert(0, str(Path(__file__).resolve().parent))
from home import COUNTRY_NAMES  # noqa: E402
from scope_lib import in_remit  # noqa: E402
import osint_lib  # noqa: E402
import taxonomy_lib  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
BULLETINS = OUTPUTS / "bulletins"
CATALOGUE = OUTPUTS / "catalogue" / "raw-catalogue.csv"
COUNTRIES = OUTPUTS / "vocab" / "countries.csv"
STORE = BULLETINS / "summaries.json"
DOCUMENT = BULLETINS / "corpus-bulletin.md"
RAW = CORPUS / "scripts" / ".workroot" / "raw"

SITE_BASE = "https://corpus.data-landscapers.io"

KEEP_DAYS = 30          # how long a written summary is retained after its item's publication date
UNTOPICED = "\x00untopiced"     # section key for a record carrying no topic at all
UNTOPICED_LABEL = "Not topic-specific"
OTHER_L1 = "Other"

csv.field_size_limit(10 ** 9)

# Titles and place names carry accents and em dashes, and the Windows console is cp1252 — the
# same two lines every other script here opens with, for the same reason.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ── the vocabularies ───────────────────────────────────────────────

def country_names() -> dict[str, str]:
    """Full names from `outputs/vocab/countries.csv` — Corpus's own snapshot — with the home
    page's short forms preferred where it carries one. A country box is the width of a box: it
    has to say `DRC` rather than *Democratic Republic of the Congo*, which is the same judgement
    `home.COUNTRY_NAMES` was written for, so it is that list rather than a second one."""
    names = {}
    if COUNTRIES.exists():
        with COUNTRIES.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                names[row["iso-3"].strip()] = row["country-name"].strip()
    names.update(COUNTRY_NAMES)
    return names


def topic_label(slug: str) -> str:
    return taxonomy_lib.label(slug)


def l1_label(slug: str) -> str:
    return taxonomy_lib.level1(slug) or OTHER_L1


def topic_order() -> list[str]:
    """Level-2 slugs in `lookups/taxonomy.csv`'s own sort order."""
    return taxonomy_lib.keys()


# ── the window ─────────────────────────────────────────────────────

def window(run_date: date) -> tuple[str, str]:
    return (run_date - timedelta(days=1)).isoformat(), run_date.isoformat()


def facets(value: str) -> list[str]:
    return [v.strip() for v in value.split(";") if v.strip()]


def select(run_date: date) -> tuple[list[dict], list[dict]]:
    """The window, split into what is published and what the remit excludes.

    Equality on the `published` column does the date-precision work for free: a month-precision
    record carries `2026-01` and a year-precision one `2026`, neither of which can equal a full
    date, so only records the source itself dated to the day are ever selected.

    **The second filter is the geographic remit** *(Bill, 2026-08-20)*, and until that date there
    was none: this function took every record in the window. On 19–20 August that put Thailand's
    national passport scheme, Japan's training-data rule, Korea's teen-algorithm debate and
    India's market-regulator AI rules into a bulletin about Africa, filed under *Digital ID*,
    *Legislation* and *Public discourse* beside Nigeria's NIN.

    `scope_lib.in_remit()` is the rule and it is not restated here. What matters at this callsite
    is that **`unverified` counts as in remit**: a record placed `XGL` is published even though
    nothing here can tell the ITU's global connectivity report from a Türkiye national plan filed
    under the same code. Excluding them would drop good material to catch bad, and the code's
    misuse is a tagging fault upstream (notes 30 and 31 for OSINT) rather than something a
    publishing filter should be guessing at.

    **The excluded rows are returned rather than dropped**, because a filter that removes items
    silently is the same failure as the missing filter: `--scan` and `--assemble` both say how many
    the remit turned away, so a day when it turns away a great deal is visible on the run."""
    start, end = window(run_date)
    rows, excluded = [], []
    with CATALOGUE.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["published"].strip() not in (start, end):
                continue
            (rows if in_remit(row) else excluded).append(row)
    for group in (rows, excluded):
        group.sort(key=lambda r: (r["published"], r["title"].lower()), reverse=True)
    return rows, excluded


def anchor_topic(row: dict) -> str:
    """Which section carries the summary: the item's earliest topic **in document order**.

    `taxonomy_lib.sort_key` is the document's order, so the minimum over the item's topics is
    the first heading a reader passing down the page reaches it under. Ties cannot happen — a
    sort order is unique — but a slug the taxonomy does not carry scores 10,000, so an item
    tagged only with unknown slugs anchors on the first of them, under *Other*."""
    topics = facets(row["topics"])
    if not topics:
        return UNTOPICED
    return min(topics, key=lambda s: (taxonomy_lib.sort_key(s), topics.index(s)))


# ── the summary store ──────────────────────────────────────────────

def load_store() -> dict:
    if not STORE.exists():
        return {}
    return json.loads(STORE.read_text(encoding="utf-8"))


def save_store(store: dict) -> None:
    BULLETINS.mkdir(parents=True, exist_ok=True)
    ordered = {k: store[k] for k in sorted(store)}
    STORE.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8", newline="")   # newline="": see DOCUMENT.write_text below


def prune(store: dict, run_date: date) -> dict:
    cutoff = (run_date - timedelta(days=KEEP_DAYS)).isoformat()
    return {k: v for k, v in store.items() if v.get("published", "") >= cutoff}


def write_summary(slug: str, text: str, run_date: date) -> int:
    published = ""
    with CATALOGUE.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["slug"] == slug:
                published = row["published"].strip()
                break
    if not published:
        print(f"not in the catalogue: {slug}", file=sys.stderr)
        return 2
    text = " ".join(text.split())
    if not text:
        print(f"empty summary refused: {slug}", file=sys.stderr)
        return 2
    store = load_store()
    store[slug] = {"published": published, "written": run_date.isoformat(), "summary": text}
    save_store(store)
    print(f"written  {slug}  ({len(text)} chars)")
    return 0


# ── the work order ─────────────────────────────────────────────────

def raw_path(row: dict) -> str:
    """Where the model reads the item from. The workroot is `rebuild.py`'s and may not be set up
    when this is run on its own, so the path is stated either way and only verified where it can
    be."""
    slug = row["slug"]
    year = row["published"][:4]
    guess = RAW / year / f"{slug}.md"
    if guess.exists():
        return f"raw/{year}/{slug}.md"
    if RAW.exists():
        for found in RAW.glob(f"*/{slug}.md"):
            return f"raw/{found.parent.name}/{found.name}"
    return f"raw/{year}/{slug}.md"


def scan(run_date: date, as_json: bool) -> int:
    start, end = window(run_date)
    rows, excluded = select(run_date)
    store = load_store()
    pending = [r for r in rows if r["slug"] not in store]

    if as_json:
        print(json.dumps({
            "window": [start, end],
            "items": len(rows),
            "out_of_remit": [r["slug"] for r in excluded],
            "pending": [{"slug": r["slug"], "title": r["title"], "publisher": r["publisher"],
                         "published": r["published"], "places": facets(r["places"]),
                         "topics": facets(r["topics"]), "url": r["url"], "raw": raw_path(r)}
                        for r in pending],
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"window   {start} to {end}")
    print(f"in scope {len(rows)} record(s); {len(rows) - len(pending)} already summarised, "
          f"{len(pending)} to write")
    if excluded:
        # Named, not merely counted. A filter that removes items silently is the same failure
        # as the missing filter it replaced — and these are the records OSINT owes a place, a
        # `geopol.*` tag or a deletion (notes 30 and 31), so a run that turns away a lot is
        # the signal that the upstream screen has slipped again.
        print(f"remit    {len(excluded)} record(s) in the window carry no African place, "
              f"no XGL and no geopol.* tag — not published:")
        for r in excluded:
            print(f"           {r['slug']}")
    if not rows:
        print("\nNothing published in the window. Run --assemble: the bulletin says so.")
        return 0
    for r in pending:
        print()
        print(r["slug"])
        print(f"    title      {r['title']}")
        print(f"    publisher  {r['publisher']}")
        print(f"    published  {r['published']}")
        print(f"    places     {', '.join(facets(r['places'])) or '—'}")
        print(f"    topics     {', '.join(facets(r['topics'])) or '—'}")
        print(f"    read       {raw_path(r)}")
        print(f"    record     {r['url']}")
    if pending:
        print()
        print("Write each with:  python scripts/bulletin.py --write {slug} --text \"…\"")
    return 0


# ── assembly ───────────────────────────────────────────────────────

def long_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {d:%B %Y}"


def window_phrase(start: str, end: str, joiner: str = "and") -> str:
    """`15 and 16 August 2026`. The joiner turns over to `or` for the sentences that state an
    absence — nothing was published on the one day *or* the other, which *and* does not say."""
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if a.month == b.month:
        return f"{a.day} {joiner} {b.day} {b:%B %Y}"
    return f"{long_date(start)} {joiner} {long_date(end)}"


def covered_phrase(rows: list[dict], start: str, end: str) -> str:
    """The days the bulletin **actually covers**, which is not always the days it looked at
    *(Bill, 2026-08-21)*.

    The window is the run's date and the day before it, and the run happens in the small hours:
    on 2026-08-21 the sweep closed at 00:14 and not one of the fifty items it caught carried a
    publication date of the 21st. The byline said *published on 20 and 21 August 2026* anyway,
    which reads as a claim that the 21st was covered and found empty when in truth the day had
    barely started.

    So the phrase is built from the publication dates in hand. The nominal window still governs
    *selection* and still appears where the document states an absence — nothing was published
    on the 20th **or** the 21st is a statement about the window, and needs both days named."""
    days = sorted({r["published"].strip() for r in rows})
    if not days:
        return window_phrase(start, end)      # nothing in hand: the window is all there is to say
    if len(days) == 1:
        return long_date(days[0])
    return window_phrase(days[0], days[-1])


def md_escape(text: str) -> str:
    return text.replace("[", "\\[").replace("]", "\\]")


def country_boxes(row: dict, names: dict[str, str]) -> str:
    """One box per African country the item is tagged to, linking to that country's page
    *(Bill, 2026-08-21)*.

    This is the country bulletin's job, done on the item instead of in a second document. Only
    the country codes: the `X`-prefixed places are regions, blocs and the global tag, none of
    which has a country page to link to, and a box that 404s is worse than no box.

    The classes are the website's own — `.wip-item-card__status--active`, the green category
    box the Lab index uses — so the component is shared with data-landscapers.io rather than
    reinvented here (`main.css` carries it already, vendored). `country-box` adds nothing but
    spacing, because the Lab's boxes stand at the head of a card and these sit inline at the end
    of a line."""
    codes = [c for c in facets(row["places"]) if not c.startswith("X")]
    return "".join(
        f'<a class="wip-item-card__status wip-item-card__status--active country-box"'
        f' href="{SITE_BASE}/countries/{c}/" title="{c}">{names.get(c, c)}</a>'
        for c in codes)


def head_line(row: dict, names: dict[str, str]) -> str:
    return (f"**[{md_escape(row['title'])}]({row['url']})** — {row['publisher']}, "
            f"{long_date(row['published'])} {country_boxes(row, names)}").rstrip()


def link_to(label: str) -> str:
    return f"[{label}](#{slugify(label, '-')})"


def entry(row: dict, store: dict, others: list[str], anchor_label: str, here: bool,
          names: dict[str, str]) -> list[str]:
    """One item in one section. `here` is whether this section is the one carrying the detail.

    **Each entry is wrapped in a `.bulletin-item` carrying its country codes** *(Bill,
    2026-08-21)*, so the country filter has something to hide. `markdown="1"` is what makes the
    wrapper free: `render.py` runs Markdown's `md_in_html`, which processes the block's contents
    as markdown rather than passing them through as raw HTML, so the headline and the summary
    below are written here exactly as they were before the div existed.

    The codes are the same set the boxes are drawn from and are written even when empty — an
    item with no African country is one the filter should hide the moment a country is chosen,
    and `data-places=""` says that, where a missing attribute would leave it ambiguous."""
    codes = " ".join(c for c in facets(row["places"]) if not c.startswith("X"))
    # **A cross-reference is marked as one** *(Bill, 2026-08-22)*. Reading the document top to
    # bottom they earn their place — they say the item belongs here too and point at where it is
    # written out. Filtered to one country they are noise, and worse than noise in the count:
    # Eswatini's single item sat in two Level-2 sections, so the filter said two entries and
    # showed a summary and a signpost to it.
    cls = "bulletin-item" if here else "bulletin-item bulletin-item--xref"
    out = [f'<div class="{cls}" data-places="{codes}" markdown="1">', "",
           head_line(row, names), ""]
    if here:
        body = store[row["slug"]]["summary"]
        if others:
            joined = ", ".join(link_to(o) for o in others[:-1])
            also = f"{joined} and {link_to(others[-1])}" if joined else link_to(others[-1])
            # **The trailer is a signpost too, and the filter has to be able to take it away**
            # *(2026-08-22)*. The cross-reference above is hidden under a country selection
            # because it points at an item rather than being one; this sentence points at the
            # same places and had been left visible, which cost twice. Its links jump to
            # Level-2 headings the filter has just hidden — 16 of them dead under Kenya, 4
            # under Nigeria — and that is the lesser half. Filtered to Kenya a summary read
            # *Also under Digital Identity and CRVS* while the filter was in the act of
            # removing that item from Digital Identity and CRVS, so the sentence was untrue
            # and not merely unclickable.
            #
            # A `<span>` rather than a class on the paragraph, because the trailer is the tail
            # of the summary and the summary stays. No CSS: a span carries no author
            # `display`, so `el.hidden` is honoured by the UA stylesheet alone — which is the
            # rule `.bulletin-item[hidden]` exists to restore for the two elements that do.
            body += (f' <span class="bulletin-item__also">'
                     f'*Also under {also}.*</span>')
        out += [body, ""]
    else:
        out += [f"Summarised under {link_to(anchor_label)}.", ""]
    return out + ["</div>", ""]


def label_of(slug: str) -> str:
    return UNTOPICED_LABEL if slug == UNTOPICED else topic_label(slug)


def groups_of(rows: list[dict]) -> tuple[dict, list[tuple[str, list[tuple[str, str]]]]]:
    """The sections, and the Level-1 groups they sit in, both in taxonomy order.

    Returns `(sections, groups)` where `sections[slug]` is the list of items to write under that
    Level-2 heading and `groups` is `[(level-1 label, [(slug, label), …]), …]`.

    A slug the taxonomy does not carry still gets a section — it is in the corpus and dropping it
    here would publish a document that silently omits it — grouped under *Other* and sorted after
    everything the taxonomy knows. A record carrying no topic at all lands in a final
    *Not topic-specific* group for the same reason: the old topic bulletin dropped those records
    without saying so, while counting them in its own headline figure."""
    sections: dict[str, list[tuple[dict, str, str, list[str]]]] = {}
    for row in rows:
        slugs = facets(row["topics"]) or [UNTOPICED]
        anchor = anchor_topic(row)
        for slug in slugs:
            others = [label_of(s) for s in slugs if s != slug]
            sections.setdefault(slug, []).append((row, anchor, label_of(anchor), others))

    order = topic_order()
    rank = {s: i for i, s in enumerate(order)}
    present = sorted((s for s in sections if s != UNTOPICED),
                     key=lambda s: (rank.get(s, len(order)), label_of(s)))

    groups: list[tuple[str, list[tuple[str, str]]]] = []
    seen: list[str] = []
    for slug in present:                      # first appearance fixes the Level-1 order, and
        if l1_label(slug) not in seen:        # taxonomy.csv's sort order fixes first appearance
            seen.append(l1_label(slug))
    for l1 in seen:
        members = [(s, label_of(s)) for s in present if l1_label(s) == l1]
        if members:
            groups.append((l1, members))
    if UNTOPICED in sections:
        groups.append((UNTOPICED_LABEL, [(UNTOPICED, None)]))
    return sections, groups


def topic_nav(groups: list[tuple[str, list[tuple[str, str]]]]) -> list[str]:
    """A bar of Level-1 links across the head of the document *(Bill, 2026-08-21)*.

    Only the categories this edition actually holds. A nav item for a category with nothing under
    it would jump to a heading that is not on the page — the bulletin is a two-day window and on
    most days it reaches four or five of the ten categories, so a fixed bar would be mostly dead
    links.

    Raw HTML in the markdown, which `render.py`'s `md_in_html` passes through untouched: this is
    site chrome rather than prose, so it is markup, and it is here rather than in the page
    template because only this document knows which categories are in it."""
    if not groups:
        return []
    # The middot separator is the site's own — `Edition of … · …` in every report byline, and
    # the footer's copyright line — so the bar is punctuated the way the rest of the site is
    # rather than in a third style. It is written into the markup rather than drawn with a CSS
    # `::after` because an `::after` on the anchor is *inside* the link: it would underline on
    # hover and sit inside the click target, and a separator that is clickable is a bug.
    # `aria-hidden` keeps it out of a screen reader, which should hear a list of categories.
    #
    # **The class is `article-toc`, the site-wide one in `main.css`** *(2026-08-24)*. This bar
    # was the first of its kind and the treatment Bill picked; it is now the house idiom for
    # every in-page jump nav — an article's contents, a report's section list — so the rules
    # went up to `main.css` and the private `.bulletin-nav` copy in `report.css` came out.
    # `bulletin-nav` is kept alongside it as the filter's hook: `bulletin-filter.js` prunes
    # this bar to the categories a selected country actually reaches, and that behaviour is
    # this page's alone.
    sep = '<span class="article-toc__sep" aria-hidden="true">&middot;</span>'
    links = f"\n{sep}\n".join(
        f'<a href="#{slugify(label, "-")}">{label}</a>' for label, _ in groups)
    return ['<nav class="article-toc bulletin-nav" aria-label="Categories in this bulletin">',
            links, "</nav>", ""]


def country_filter(rows: list[dict], names: dict[str, str]) -> list[str]:
    """The country filter, after the Lab index's category filter *(Bill, 2026-08-21)*.

    Same control and the same shape — a `<select>` opening on *All countries* — over the
    countries **this edition holds**, which is the equivalent of the Lab's `map: 'category' |
    uniq | sort`. Offering all 54 would be a list of which 30 do nothing.

    Two things the Lab's version does not have to deal with. Its list is flat and each entry
    carries exactly one category, so hiding entries is the whole job; here the entries are
    nested two deep under headings that have to go when they empty out, and an item can carry
    several countries or none. That work is in `bulletin-filter.js`, which is why this emits
    markup and no behaviour.

    **`hidden` until the script removes it.** A `<select>` that filters nothing is worse than no
    select, and the page is perfectly usable without it — the same progressive-enhancement rule
    the home page's topic tiles follow. `screen-only` keeps it out of the PDF, where a control
    is furniture with nothing behind it."""
    codes = sorted({c for r in rows for c in facets(r["places"]) if not c.startswith("X")},
                   key=lambda c: names.get(c, c))
    if len(codes) < 2:
        return []          # one country, or none: a filter with a single option filters nothing
    options = "\n".join(
        f'<option value="{c}">{names.get(c, c)}</option>' for c in codes)
    return ['<div class="bulletin-filter screen-only" hidden>',
            '<label for="bulletin-country">Filter by country</label>',
            '<select id="bulletin-country">',
            '<option value="">All countries</option>',
            options,
            '</select>',
            '<span class="bulletin-filter__count" aria-live="polite"></span>',
            '</div>', ""]


def body_of(rows: list[dict], store: dict, names: dict[str, str], start: str, end: str
            ) -> list[str]:
    if not rows:
        return [
            f"No source in the corpus carries a publication date of "
            f"{window_phrase(start, end, 'or')}.",
            "",
            "The corpus acquires in batches rather than continuously, so an empty window means "
            "nothing was **published** on those two days — not that nothing arrived. Records "
            "ingested in the same period but published earlier are in the country and topic "
            "reports, which select on what a record moves rather than on when it was published.",
            "",
        ]

    sections, groups = groups_of(rows)
    lines = topic_nav(groups) + country_filter(rows, names)
    for group_label, members in groups:
        lines += [f"## {group_label}", ""]
        for slug, section_label in members:
            if section_label is not None:
                lines += [f"### {section_label}", ""]
            # Summarised items first, cross-references after them: a section that opens with three
            # pointers to somewhere else reads as having nothing in it. Stable within each half,
            # so the newest item is still the first thing under the heading.
            for row, anchor_slug, anchor_label, others in sorted(
                    sections[slug], key=lambda item: item[1] != slug):
                lines += entry(row, store, others, anchor_label, here=anchor_slug == slug,
                               names=names)
    return lines


def document(rows: list[dict], store: dict, run_date: date, collected: str, compiled: str,
             names: dict[str, str]) -> str:
    """The whole markdown file. Both stamps are `YYYY-MM-DD HH:MM` and both are passed in rather
    than read from a clock here — see `assemble()` for why. `collected` is when the material
    stopped moving and is what the byline states; `compiled` is the newest ingest and is what the
    edition picker shows."""
    start, end = window(run_date)
    when = datetime.strptime(collected, "%Y-%m-%d %H:%M")
    subtitle = (f"Last updated {when:%d-%m-%Y} at {when:%H:%M} — "
                f"Covering sources published on {covered_phrase(rows, start, end)}")

    head = [
        "---",
        "type: bulletin",
        "title: Bulletin",
        f"subtitle: {subtitle}",
        f"window_start: {start}",
        f"window_end: {end}",
        f"items: {len(rows)}",
        f"collected_to: {collected}",
        f"compiled: {compiled}",
        "---",
        "",
        "# Bulletin",
        "",
    ]
    return "\n".join(head + body_of(rows, store, names, start, end)).rstrip() + "\n"


def held_stamps(path: Path) -> tuple[str, str] | None:
    """`(collected_to, compiled)` as the file on disk carries them, or `None` if either is
    missing — which is what a document written before `collected_to:` existed looks like, and it
    reads as *no held stamp* so the run rebuilds rather than comparing against half a pair."""
    if not path.exists():
        return None
    found = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        for key in ("collected_to:", "compiled:"):
            if line.startswith(key):
                found[key.rstrip(":")] = line.split(":", 1)[1].strip()
    if "collected_to" in found and "compiled" in found:
        return found["collected_to"], found["compiled"]
    return None


# The one source string that means *the mirror could not be read*, named rather than repeated
# because the check for it used to be a literal at each end and the two drifted the moment the
# readable sources gained names *(2026-08-26)*. Splitting "OSINT ingest" into "OSINT ingest
# start" and "OSINT sweep cycle close" left `source != "OSINT ingest"` true on a mirror that had
# just been read perfectly well, so a run reading three clocks announced it could read none —
# a false alarm on the one line whose whole job is to be believed.
BUILD_CLOCK = "build clock (mirror unreadable)"


def stamps_for(now: datetime | None = None) -> tuple[str, str, str]:
    """`(collected_to, compiled, where they came from)`, each `YYYY-MM-DD HH:MM`.

    `compiled` is the newest ingest stamp. `collected_to` is when collection stopped: the sweep
    cycle's own close where the mirror carries a usable one, the start of the newest ingest run
    as the fallback where it does not — see the module docstring for why that order, and for the
    two ways a close is refused. The build clock stands in for both where the mirror cannot be
    read at all. The source is returned rather than logged here so that `--assemble` can print
    it: a fallback nobody is told about is a fallback that becomes the normal case without
    anyone noticing."""
    started, newest = osint_lib.ingest_started(), osint_lib.last_ingest()
    if started is None or newest is None:
        return ((now or datetime.now()).strftime(osint_lib.TS),) * 2 + (BUILD_CLOCK,)

    closed = osint_lib.last_cycle_close()
    if closed is not None and started < closed <= (now or datetime.now()) + osint_lib.SKEW:
        return closed.strftime(osint_lib.TS), newest.strftime(osint_lib.TS), "OSINT sweep cycle close"
    return started.strftime(osint_lib.TS), newest.strftime(osint_lib.TS), "OSINT ingest start"


def assemble(run_date: date, now: datetime | None = None) -> int:
    rows, excluded = select(run_date)
    store = load_store()
    missing = [r["slug"] for r in rows if r["slug"] not in store]
    if missing:
        print(f"STOP: {len(missing)} item(s) in the window have no summary — "
              f"the bulletin is not written:", file=sys.stderr)
        for slug in missing:
            print(f"  {slug}", file=sys.stderr)
        print("Run --scan for the work order, then --write each one.", file=sys.stderr)
        return 1

    names = country_names()
    BULLETINS.mkdir(parents=True, exist_ok=True)

    collected, compiled, source = stamps_for(now)

    # **Is anything different apart from the stamp?** Asked by rebuilding the document with the
    # stamp already on disk and comparing the whole file: if that reproduces what is there, the
    # only thing that moved was the clock. That is no longer a reason to skip the write — see
    # the module docstring, and Bill's ruling of 2026-08-21 — but it is still the difference
    # between *we looked and nothing was published* and *here is what was published*, which are
    # different things for the run to say.
    #
    # The comparison is the whole file. It was the body below the frontmatter until the same
    # day, on the reasoning that the stamp lives in the frontmatter and so must be excluded —
    # which excluded the *whole* frontmatter, and the subtitle is in it. A correction to how the
    # byline is worded therefore could not reach a document whose body had not changed: the fix
    # ran, reported `unchanged`, and left the wrong subtitle in place.
    before = DOCUMENT.read_text(encoding="utf-8") if DOCUMENT.exists() else None
    held = held_stamps(DOCUMENT)
    clock_only = (before is not None and held is not None
                  and document(rows, store, run_date, *held, names) == before)

    text = document(rows, store, run_date, collected, compiled, names)
    where = DOCUMENT.relative_to(CORPUS)
    if text == before:
        print(f"unchanged  {where}  (last updated {held[0]}; the clock has not moved either)")
    else:
        # `newline=""` or Windows turns every \n into \r\n and the file differs from the one in
        # git on every line *(2026-08-22)*. It showed up as a 1,205-line diff between a document
        # CC had just committed and the identical document on disk — `--ignore-cr-at-eol` came
        # back empty. OSINT logged the same defect the same morning, in its own scripts, for the
        # same reason: `write_text` defaults to translating line endings.
        DOCUMENT.write_text(text, encoding="utf-8", newline="")
        if clock_only:
            print(f"checked    {where}  — nothing published in the window since {held[0]}; "
                  f"the page now says so")
        else:
            print(f"written    {where}  ({len(rows)} item(s))")
        print(f"updated    {collected}  — collection stopped, from {source} "
              f"(newest ingest {compiled})")

    # **Said on every run, not only the ones that write.** The mirror being unreadable is a fact
    # about this run either way, and the run most likely to bury it is the quiet one: an
    # unchanged document prints a single line, and that line is where nobody would look. This
    # module's whole reason for returning `None` rather than guessing is that the caller says
    # which it got, and a caller that says so only when it happens to be writing does not.
    if source == BUILD_CLOCK:
        print(f"mirror     {osint_lib.MIRROR} unreadable — no ingest stamp available this run")

    if excluded:
        print(f"remit      {len(excluded)} record(s) in the window excluded by the geographic remit")

    kept = prune(store, run_date)
    if len(kept) != len(store):
        save_store(kept)
        print(f"pruned     {len(store) - len(kept)} summary entr(ies) older than {KEEP_DAYS} days")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=None, help="run date (default today)")
    ap.add_argument("--scan", action="store_true", help="the window and the work order")
    ap.add_argument("--json", action="store_true", help="with --scan, machine-readable")
    ap.add_argument("--write", metavar="SLUG", default=None, help="record one item's summary")
    ap.add_argument("--text", default=None, help="the summary (default: read stdin)")
    ap.add_argument("--assemble", action="store_true", help="write the bulletin")
    args = ap.parse_args()

    run_date = date.fromisoformat(args.date) if args.date else date.today()

    if args.write:
        text = args.text if args.text is not None else sys.stdin.read()
        return write_summary(args.write, text, run_date)
    if args.assemble:
        return assemble(run_date)
    return scan(run_date, args.json)


if __name__ == "__main__":
    sys.exit(main())
