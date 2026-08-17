#!/usr/bin/env python3
"""bulletin.py — the daily bulletin: two documents over a two-day window.

    python scripts/bulletin.py --scan                 what is in the window, and what still needs a summary
    python scripts/bulletin.py --write {slug} --text "…"   record one item's summary (or pipe it on stdin)
    python scripts/bulletin.py --assemble             write outputs/bulletins/{country,topic}-bulletin.md
    python scripts/bulletin.py --date 2026-08-16 …    run any of the above against another day

**The window is publication, not acquisition** *(Bill, 2026-08-17)*. An item is in the bulletin when
its `published` date is the run's date or the day before it, and for no other reason. The corpus
acquires in batches — 184 records landed on 2026-08-16 carrying publication dates spread across the
ten days before it — so most runs select a handful and some select none. **An empty window is a
finished bulletin, not a failure**: the document says the window was empty and says why, because a
silence is indistinguishable from a build that did not run.

**A summary is written once and kept.** The window is two days wide and the build runs daily, so
almost every item is selected twice; re-summarising it the second time would burn the model stage
again and word the same item differently on consecutive days. `outputs/bulletins/summaries.json`
is the store, `--write` is the only way into it, and `--scan` asks for summaries only for items
that do not have one. Entries age out 30 days after publication, which is 28 days after the last
window that could cite them.

**Detail sits in one place and everything else points at it** *(Bill, 2026-08-17)*. An item tagged
five countries is written out once — under a region if it carries one, otherwise under the first
place its record lists — and each of the other four carries a cross-reference to it. The topic
bulletin does the same on the first topic listed, and does not subdivide by country. *First* means
first in the record's own facet list, which `build-catalogue.py` carries across unchanged — often
the order the source itself put them in, and stable run to run either way. It is preferred to
alphabetical order because alphabetical order is a property of the code, not of the item: it would
anchor a nine-country regional story under Benin.

Anchors resolve because `render.py` runs Markdown's `toc` extension, which gives every heading an
id from the same `slugify` this module imports. Two implementations of that slug is how the links
would come to point at nothing, so there is one.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from markdown.extensions.toc import slugify

sys.path.insert(0, str(Path(__file__).resolve().parent))
from home import L1, REGION_NAMES, SUBTOPIC_NAMES, subtopic_label  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
BULLETINS = OUTPUTS / "bulletins"
CATALOGUE = OUTPUTS / "catalogue" / "raw-catalogue.csv"
COUNTRIES = OUTPUTS / "vocab" / "countries.csv"
STORE = BULLETINS / "summaries.json"
RAW = CORPUS / "scripts" / ".workroot" / "raw"

KEEP_DAYS = 30          # how long a written summary is retained after its item's publication date
UNPLACED = "Not place-specific"

csv.field_size_limit(10 ** 9)

# Titles and place names carry accents and em dashes, and the Windows console is cp1252 — the
# same two lines every other script here opens with, for the same reason.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ── the vocabularies ───────────────────────────────────────────────

def country_names() -> dict[str, str]:
    """Full names from `outputs/vocab/countries.csv` — Corpus's own snapshot, and the long form
    rather than the home page's short one: a box the width of a code has to say `DRC`, a bulletin
    heading does not."""
    names = {}
    with COUNTRIES.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            names[row["iso-3"].strip()] = row["country-name"].strip()
    return names


def place_label(code: str, names: dict[str, str]) -> str:
    if code.startswith("X"):
        return REGION_NAMES.get(code, code)
    return names.get(code, code)


def topic_label(slug: str) -> str:
    return subtopic_label(slug)


def topic_order() -> list[str]:
    """Level-2 slugs in the site's own order — `home.SUBTOPIC_NAMES` is grouped by Level-1 and
    hand-ordered within each group, so it is the ordering the topic tiles already use."""
    return list(SUBTOPIC_NAMES)


def l1_of(slug: str) -> str:
    return slug.split(".", 1)[0]


# ── the window ─────────────────────────────────────────────────────

def window(run_date: date) -> tuple[str, str]:
    return (run_date - timedelta(days=1)).isoformat(), run_date.isoformat()


def facets(value: str) -> list[str]:
    return [v.strip() for v in value.split(";") if v.strip()]


def select(run_date: date) -> list[dict]:
    """Every catalogue record published on the run's date or the day before.

    Equality on the `published` column does the date-precision work for free: a month-precision
    record carries `2026-01` and a year-precision one `2026`, neither of which can equal a full
    date, so only records the source itself dated to the day are ever selected."""
    start, end = window(run_date)
    rows = []
    with CATALOGUE.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["published"].strip() in (start, end):
                rows.append(row)
    rows.sort(key=lambda r: (r["published"], r["title"].lower()), reverse=True)
    return rows


def anchor_place(row: dict) -> str:
    """Which entry carries the detail: a region if the record has one, else the first place it
    lists, else the unplaced group."""
    places = facets(row["places"])
    for p in places:
        if p.startswith("X"):
            return p
    return places[0] if places else UNPLACED


def anchor_topic(row: dict) -> str | None:
    topics = facets(row["topics"])
    return topics[0] if topics else None


# ── the summary store ──────────────────────────────────────────────

def load_store() -> dict:
    if not STORE.exists():
        return {}
    return json.loads(STORE.read_text(encoding="utf-8"))


def save_store(store: dict) -> None:
    BULLETINS.mkdir(parents=True, exist_ok=True)
    ordered = {k: store[k] for k in sorted(store)}
    STORE.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prune(store: dict, run_date: date) -> dict:
    cutoff = (run_date - timedelta(days=KEEP_DAYS)).isoformat()
    return {k: v for k, v in store.items() if v.get("published", "") >= cutoff}


def write_summary(slug: str, text: str, run_date: date) -> int:
    published = ""
    with CATALOGUE.open(encoding="utf-8", newline="") as fh:
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
    rows = select(run_date)
    store = load_store()
    pending = [r for r in rows if r["slug"] not in store]

    if as_json:
        print(json.dumps({
            "window": [start, end],
            "items": len(rows),
            "pending": [{"slug": r["slug"], "title": r["title"], "publisher": r["publisher"],
                         "published": r["published"], "places": facets(r["places"]),
                         "topics": facets(r["topics"]), "url": r["url"], "raw": raw_path(r)}
                        for r in pending],
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"window   {start} to {end}")
    print(f"in scope {len(rows)} record(s); {len(rows) - len(pending)} already summarised, "
          f"{len(pending)} to write")
    if not rows:
        print("\nNothing published in the window. Run --assemble: both bulletins say so.")
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


def md_escape(text: str) -> str:
    return text.replace("[", "\\[").replace("]", "\\]")


def head_line(row: dict) -> str:
    return (f"**[{md_escape(row['title'])}]({row['url']})** — {row['publisher']}, "
            f"{long_date(row['published'])}")


def link_to(label: str) -> str:
    return f"[{label}](#{slugify(label, '-')})"


def entry(row: dict, store: dict, others: list[str], anchor_label: str, here: bool) -> list[str]:
    """One item in one section. `here` is whether this section is the one carrying the detail."""
    out = [head_line(row), ""]
    if here:
        body = store[row["slug"]]["summary"]
        if others:
            joined = ", ".join(link_to(o) for o in others[:-1])
            also = f"{joined} and {link_to(others[-1])}" if joined else link_to(others[-1])
            body += f" *Also under {also}.*"
        out += [body, ""]
    else:
        out += [f"Summarised under {link_to(anchor_label)}.", ""]
    return out


def group_sections(rows: list[dict], store: dict, by: str, names: dict[str, str]) -> list[str]:
    """The body of one bulletin. `by` is `place` or `topic`; the two differ in how the sections are
    grouped and ordered and in nothing else, which is why one function writes both."""
    lines: list[str] = []

    if by == "place":
        def label(code: str) -> str:
            return place_label(code, names)
        sections: dict[str, list[tuple[dict, str, str, list[str]]]] = {}
        for row in rows:
            codes = facets(row["places"]) or [UNPLACED]
            anchor = anchor_place(row)
            for code in codes:
                others = [label(c) for c in codes if c != code]
                sections.setdefault(code, []).append((row, anchor, label(anchor), others))
        regions = sorted((c for c in sections if c.startswith("X")), key=label)
        countries = sorted((c for c in sections if not c.startswith("X") and c != UNPLACED),
                           key=label)
        groups = []
        if regions:
            groups.append(("Regions", [(c, label(c)) for c in regions]))
        if countries:
            groups.append(("Countries", [(c, label(c)) for c in countries]))
        if UNPLACED in sections:
            groups.append((UNPLACED, [(UNPLACED, None)]))
    else:
        label = topic_label
        sections = {}
        for row in rows:
            slugs = facets(row["topics"])
            anchor = anchor_topic(row)
            for slug in slugs:
                others = [label(s) for s in slugs if s != slug]
                sections.setdefault(slug, []).append((row, anchor, label(anchor), others))
        order = topic_order()
        rank = {s: i for i, s in enumerate(order)}
        present = sorted(sections, key=lambda s: (rank.get(s, len(order)), label(s)))
        groups = []
        for l1, l1_label in L1.items():
            members = [(s, label(s)) for s in present if l1_of(s) == l1]
            if members:
                groups.append((l1_label, members))
        rest = [(s, label(s)) for s in present if l1_of(s) not in L1]
        if rest:
            groups.append(("Other", rest))

    for group_label, members in groups:
        lines += [f"## {group_label}", ""]
        for code, section_label in members:
            if section_label is not None:
                lines += [f"### {section_label}", ""]
            # Summarised items first, cross-references after them: a section that opens with three
            # pointers to somewhere else reads as having nothing in it. Stable within each half,
            # so the newest item is still the first thing under the heading.
            for row, anchor_code, anchor_label, others in sorted(
                    sections[code], key=lambda item: item[1] != code):
                lines += entry(row, store, others, anchor_label, here=anchor_code == code)
    return lines


def document(kind: str, rows: list[dict], store: dict, run_date: date,
             names: dict[str, str]) -> str:
    start, end = window(run_date)
    phrase = window_phrase(start, end)
    title = "Country bulletin" if kind == "country" else "Topic bulletin"

    # The breadth clause counts the sections the items reach. It is written three ways because a
    # window can be narrow enough to make the ordinary phrasing say "across 0 countries and
    # regions" — which is true, reads as a fault, and is the normal shape of a quiet day.
    if kind == "country":
        breadth = len({c for r in rows for c in facets(r["places"])})
        counted = ("none of it tagged to a country or region" if breadth == 0
                   else "one country or region" if breadth == 1
                   else f"{breadth} countries and regions")
    else:
        breadth = len({t for r in rows for t in facets(r["topics"])})
        counted = ("no topic" if breadth == 0
                   else "one topic" if breadth == 1
                   else f"{breadth} topics")

    n = len(rows)
    if n:
        across = counted if breadth == 0 and kind == "country" else f"across {counted}"
        stand = (f"*Compiled {run_date.isoformat()} · {n} source{'s' if n != 1 else ''} published "
                 f"{phrase}, {across}.*")
    else:
        stand = (f"*Compiled {run_date.isoformat()} · no sources published on "
                 f"{window_phrase(start, end, 'or')}.*")

    head = [
        "---",
        "type: bulletin",
        f"title: {title}",
        f"subtitle: sources published {phrase}",
        f"window_start: {start}",
        f"window_end: {end}",
        f"items: {n}",
        f"compiled: {run_date.isoformat()}",
        "---",
        "",
        f"# {title}",
        "",
        stand,
        "",
    ]

    if not rows:
        body = [
            f"No source in the corpus carries a publication date of "
            f"{window_phrase(start, end, 'or')}.",
            "",
            "The corpus acquires in batches rather than continuously, so an empty window means "
            "nothing was **published** on those two days — not that nothing arrived. Records "
            "ingested in the same period but published earlier are in the country and topic "
            "reports, which select on what a record moves rather than on when it was published.",
            "",
        ]
    elif kind == "country":
        body = group_sections(rows, store, "place", names)
    else:
        body = group_sections(rows, store, "topic", names)

    if kind == "country":
        tail = ["*Each item is summarised once — under a region where it carries one, otherwise "
                "under the first place its record lists — and cross-referenced from every other "
                "country and region it touches.*", ""]
    else:
        tail = ["*Each item is summarised once, under the first topic its record lists, and "
                "cross-referenced from every other topic it carries. The topic bulletin does not "
                "subdivide by country; the country bulletin covers the same window place by "
                "place.*", ""]

    return "\n".join(head + body + (tail if rows else [])).rstrip() + "\n"


def assemble(run_date: date) -> int:
    rows = select(run_date)
    store = load_store()
    missing = [r["slug"] for r in rows if r["slug"] not in store]
    if missing:
        print(f"STOP: {len(missing)} item(s) in the window have no summary — "
              f"the bulletins are not written:", file=sys.stderr)
        for slug in missing:
            print(f"  {slug}", file=sys.stderr)
        print("Run --scan for the work order, then --write each one.", file=sys.stderr)
        return 1

    names = country_names()
    BULLETINS.mkdir(parents=True, exist_ok=True)
    for kind in ("country", "topic"):
        path = BULLETINS / f"{kind}-bulletin.md"
        text = document(kind, rows, store, run_date, names)
        before = path.read_text(encoding="utf-8") if path.exists() else None
        if before == text:
            print(f"unchanged  {path.relative_to(CORPUS)}")
            continue
        path.write_text(text, encoding="utf-8")
        print(f"written    {path.relative_to(CORPUS)}  ({len(rows)} item(s))")

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
    ap.add_argument("--assemble", action="store_true", help="write both bulletins")
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
