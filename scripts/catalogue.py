#!/usr/bin/env python3
"""catalogue.py — the catalogue browse page (documentation/design.md §4).

    python scripts/catalogue.py
      -> site/catalogue/index.html            the browse-and-filter surface
      -> site/catalogue/catalogue-data.js     packed data the page reads
      -> site/catalogue/raw-catalogue.csv     the full download (published from source)
      -> site/catalogue/raw-catalogue.json    the full download

Promoted from `prototypes/catalogue-prototype.html` + `prototypes/build-catalogue-data.py`
once the browse surface was agreed. It reads the catalogue Corpus builds itself
(`outputs/catalogue/raw-catalogue.json`), packs the ten
browse fields into `catalogue-data.js`, and wraps the proven browse UI in the real
site chrome (`scripts/country.py`'s header/nav/footer).

Place and topic vocabularies come from `outputs/vocab/` — snapshotted from OSINT's
`lookups/`, because the site may not read outside `outputs/` (NOTES-FOR-OSINT #9).
Refresh that snapshot when the vocabularies change.

The catalogue carries metadata only — never source bodies. Each record links to
its publisher (`build-catalogue.py`).

**The first screen is baked in** — the newest hundred rows and the three facet
menus are written into `index.html` as markup, so the page shows results before
the payload has arrived and with JavaScript off entirely
(`documentation/catalogue-split-plan.md`, Part 1). Everything under *the baked
first screen* below mirrors a function in the page's own JavaScript, and
`scripts/test_catalogue_firstscreen.py` runs the page's copy over the payload and
compares it to what was baked. Change one and the other has to move.
"""
from __future__ import annotations
import ast, csv, hashlib, json, re, shutil, sys, unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from copy_lib import copy  # noqa: E402
import taxonomy_lib  # noqa: E402
from chrome_lib import chrome, external_links, foot, ga, styles  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
SITE = CORPUS / "site"
VOCAB = CORPUS / "outputs" / "vocab"
NAMES = CORPUS / "outputs" / "names"
TITLES = CORPUS / "outputs" / "titles"
DOC_IDS = CORPUS / "outputs" / "catalogue" / "doc-ids.csv"

ENTITY_NAMES = CORPUS / "lookups" / "entity-names.csv"
BUILD_CATALOGUE = CORPUS / "scripts" / "build-catalogue.py"

from names_lib import KEYSTOP, shard_file, shard_key  # noqa: E402  — see there for the WIN_RESERVED rule
SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def csv_cols() -> list[str]:
    """The download's column list, lifted from `build-catalogue.py` rather than restated.

    The page cuts a filtered CSV in the reader's browser, and it has to come out with
    the same sixteen columns in the same order as `raw-catalogue.csv` — two files both
    called CSV with different column sets is the thing that bites a reader six months
    later, and it is the whole reason the export fetches the full catalogue instead of
    serialising the eleven fields the browse payload happens to carry.

    So the spec is read from the one place that defines it. By syntax tree, not by
    import: `build-catalogue.py` opens the vault at module scope, which a page build
    has no business doing, and its name is hyphenated besides. A column added there
    reaches the export on the next build with nothing to change here.
    """
    tree = ast.parse(BUILD_CATALOGUE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CSV_COLS" for t in node.targets):
            return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit("catalogue: no CSV_COLS in build-catalogue.py — the filtered "
                     "download cannot be built without the column spec")


def stamp(path: Path) -> str:
    """`?v=<8 hex>` over the file's bytes, for a `src` or a `fetch`.

    **The page and its payload are two files and the browser caches them
    differently** *(Bill, 2026-08-24)*. `index.html` is small and gets revalidated;
    `catalogue-data.js` is 4.5 MB and does not, so a reader who visited before a
    rebuild is served a new page driving old data. That failed silently and
    plausibly rather than loudly: on the day the topic facet gained its taxonomy
    ordering, the vocabulary carrying the order was in the payload, an older cached
    payload had no `torder` in it, and the page fell back to sorting by record
    count — which is a sort, so nothing looked broken; it was simply the sort that
    had just been removed. The same hazard reaches `raw-catalogue.json`, where a
    stale copy would mean an export cut from a catalogue the reader is not looking
    at, and there the wrong answer is a file that leaves the building.

    A **content** hash rather than a build timestamp, so a file that did not change
    keeps its URL and stays cached — the cost of this is only paid when the bytes
    actually move. A query string is enough: GitHub Pages serves the file and
    ignores it (`RENDER.md`), so no filename and no link anywhere else changes."""
    return "?v=" + hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def publish_shards(src: Path, dst: Path, meta: dict | None, label: str) -> int:
    """Copy the shards a manifest names into `site/`, and prune whatever it does not.

    Both indexes are published this way and the rules are the same for each: copy
    only what changed, so an unchanged shard keeps its mtime and stays out of the
    diff; prune by **filename** rather than by the key it decodes to, which is what
    a stray `aux.txt` survived once; and then check that every key the page is about
    to be handed has a file behind it. A missing shard is a search that quietly
    returns less, not an error a reader would ever see.
    """
    if meta is None:
        return 0
    dst.mkdir(parents=True, exist_ok=True)
    want = set(meta["shards"])
    n = 0
    for f in sorted(src.glob("*.txt")):
        if shard_key(f.name) not in want:
            continue
        out = dst / f.name
        if not out.exists() or out.read_bytes() != f.read_bytes():
            shutil.copyfile(f, out)
        n += 1
    want_files = {shard_file(k) for k in want}
    for stale in dst.glob("*.txt"):
        if stale.name in want_files:
            continue
        try:
            stale.unlink()
        except OSError as exc:
            print(f"catalogue: could not delete {stale.name} ({exc}). If it is a "
                  f"Windows device name, remove it with:  del \\\\?\\{stale.resolve()}")
    gone = sorted(k for k in want if not (dst / shard_file(k)).is_file())
    if gone:
        raise SystemExit(f"catalogue: {len(gone)} {label} shard(s) named in the manifest "
                         f"are missing from site/: {', '.join(gone[:10])}")
    return n


def catalogue_dir() -> Path:
    for base in (OUTPUTS,):
        if (base / "catalogue" / "raw-catalogue.json").exists():
            return base / "catalogue"
    raise SystemExit("no catalogue found in outputs/ — run scripts/rebuild.py --catalogue")


def vocab():
    places, regions = {}, {}
    with open(VOCAB / "countries.csv", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            places[r["iso-3"]] = r["country-name"]
            regions[r["iso-3"]] = r.get("Region") or ""
    # Topic labels come from Corpus's `lookups/taxonomy.csv`, not from the vocabulary
    # snapshot (Bill, 2026-08-19). The snapshot is prose as well as vocabulary, and the
    # pattern this used to run over it read `dpi.registry`'s 558-character ruling as the
    # label — which reached this page's own filter list. The slugs are still OSINT's;
    # only how they are written is decided here.
    topics = taxonomy_lib.labels()
    cats = taxonomy_lib.level1s()
    # The **order** as well as the labels (Bill, prep/catalogue.md §5). The topic
    # facet used to sort by record count, which reshuffled itself every time a
    # checkbox moved and put the taxonomy's own sequence nowhere on the page.
    # `keys()` is the file's own order, so the Level 1 groups fall out of it too —
    # Governance, Finance, ICT Infrastructure, DPI, … — with no second list to keep.
    torder = taxonomy_lib.keys()
    return places, regions, topics, cats, torder


def _place_map():
    """Token(s) a slug writes -> the country name to qualify a label with."""
    m = {}
    with open(VOCAB / "countries.csv", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            name = (r.get("country-name") or "").strip()
            iso = (r.get("iso-3") or "").strip().lower()
            if not name:
                continue
            if iso:
                m[(iso,)] = name
            toks = tuple(t for t in name.lower().replace("'", " ").replace("-", " ").split() if t)
            if toks:
                m.setdefault(toks, name)
    # Forms the slugs write that the vocabulary does not, including the two-letter
    # codes — countries.csv carries iso-3 only, and `bf-`, `cv-` are common prefixes.
    m.update({("cote", "divoire"): "Côte d'Ivoire", ("civ",): "Côte d'Ivoire",
              ("drc",): "DR Congo", ("rdc",): "DR Congo", ("bf",): "Burkina Faso",
              ("cv",): "Cabo Verde", ("gnq",): "Equatorial Guinea"})
    return m


def disambiguate(ent_names: dict) -> dict:
    """Qualify a display name that several *different* entities would otherwise share.

    `build-entity-names.py` strips the place before scoring, which is right — a country
    suffix is the least distinguishing part of a slug and was winning on its own. But
    the place was then missing from the **label** too, so 17 ministries of finance and
    12 ministries of health all read the same on the page and in the row chips, and the
    reader could not tell which country's they were filtering by. 458 slugs collapsed
    onto 183 labels that way.

    Only where the collision is real: slugs that resolve to the *same* place, or to no
    place at all, are duplicate slugs for one entity (`m-kopa`, `m-kopa-holdings-ltd`)
    and should keep sharing a label. And a place already named in the display adds
    nothing — "Central Bank of Nigeria (Nigeria)" is worse than leaving it alone.
    """
    pm = _place_map()
    single = {k[0]: v for k, v in pm.items() if len(k) == 1 and len(k[0]) >= 5}

    def place_of(slug):
        t = slug.split("-")
        for n in (3, 2, 1):                      # longest wins: `burkina-faso` before `faso`
            for i in range(len(t) - n + 1):
                if tuple(t[i:i + n]) in pm:
                    return pm[tuple(t[i:i + n])]
        for tok in t:                            # last resort: adjectival or truncated
            if len(tok) < 5:
                continue
            for base, name in single.items():
                if tok.startswith(base) or base.startswith(tok):
                    return name
        return None

    by = {}
    for slug, display in ent_names.items():
        by.setdefault(display, []).append(slug)
    out = dict(ent_names)
    for display, slugs in by.items():
        if len(slugs) < 2:
            continue
        pl = {s: place_of(s) for s in slugs}
        if len(set(pl.values())) < 2:
            continue
        for s in slugs:
            p = pl[s]
            if p and p.lower() not in display.lower():
                out[s] = f"{display} ({p})"
    return out


# ---- entity display names ---------------------------------------------------
# These used to be computed in the reader's browser. They are computed here now
# because the baked first screen below has to write the same labels the live page
# writes, and the honest way to have one set of labels is to have one place that
# decides them. The page ships two maps -- `entnames`, what the sources call the
# thing, and `entpretty`, the slug written out where nothing has named it -- and
# does nothing with a slug in neither but read it as itself.

# Short tokens in this vocabulary are overwhelmingly acronyms (ITU, UNDP, NIMC,
# ODPC, DRC, ICT), so a token of four characters or fewer is uppercased unless it
# is in PLAIN_SHORT. That list was populated by measuring, not guessing: of the
# 6,774 slugs, 1,548 distinct tokens of four characters or fewer would be
# uppercased, and the frequent ones were read off and sorted by hand. Re-measure
# the same way after a big ingest; the tail below about ten occurrences is not
# worth chasing, because a wrong entry shows up as ODPC right and BANK wrong,
# which is visible and cheap. Ambiguous cases are left uppercase deliberately:
# `sa` is as often South Africa as société anonyme, and `car` is more often the
# Central African Republic than a vehicle.
FUNC_WORDS = {"of", "for", "and", "the", "de", "du", "des", "da", "do", "das", "dos",
              "la", "le", "les", "el", "al", "in", "on", "at", "et", "em", "na",
              "no", "aux", "o"}
PLAIN_SHORT = {"bank", "fund", "data", "tech", "news", "post", "west", "east", "cape",
               "town", "city", "gov", "new", "tax", "land", "port", "hub", "net",
               "pay", "tel", "web", "gas", "oil", "air", "sea", "cash", "card",
               "link", "soft", "cloud", "fibre", "fiber", "group",
               # measured off the vocabulary, 2026-08-24
               "cote", "faso", "togo", "mali", "cabo", "chad", "sao", "tome", "arab",
               "act", "law", "bill", "code", "plan", "deal", "cour", "unit", "food",
               "home", "one", "lab", "open", "blue", "cert", "tide", "jean", "moov",
               "kopa", "yas", "ltd", "inc", "pty"}


def pretty_label(slug: str) -> str:
    """A slug written out as a name, for an entity nothing has named.

    A slug is not a display name, and this is only a guess at how to write one --
    `build-entity-names.py` derives the real ones from the sources and those always
    win. Title-case, except the function words, which stay lower unless they open
    the name, and the short tokens, which are read as acronyms.
    """
    out = []
    for ix, w in enumerate(slug.split("-")):
        if not w:
            out.append(w)
        elif w in FUNC_WORDS:
            out.append(w if ix else w[:1].upper() + w[1:])
        elif len(w) <= 4 and w not in PLAIN_SHORT:
            out.append(w.upper())
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)


# ---- the baked first screen -------------------------------------------------
# `documentation/catalogue-split-plan.md` Part 1. The newest hundred rows and the
# three facet menus are all known here, so they are written into `index.html` as
# real markup rather than left for the browser to draw once 3 MB of payload has
# arrived and parsed. The page redraws over the top on load, which is what keeps
# this honest: a difference between what is baked and what the page draws corrects
# itself in front of the reader rather than persisting unseen.
#
# **Everything below mirrors a function in the page's own JavaScript**, and only
# for the unfiltered default state -- no query, no facet selected, no type-ahead
# term, no option cap. That is the whole of what can be baked, and writing only
# that is what keeps these short. `scripts/test_catalogue_firstscreen.py` lifts
# the page's own `rowHTML` and `optsHTML` out of the built file and proves the two
# agree; when one of them changes, the other has to.

SHOWN = 100          # `state.shown` in the page, and the two have to agree
PRE = "<2020"        # `PRE` in the page -- the pre-2020 year bucket

_ESC = {ord("<"): "&lt;", ord(">"): "&gt;", ord("&"): "&amp;"}


def esc(s) -> str:
    """The page's `esc()` -- `<`, `>` and `&`, for a text node."""
    return str(s).translate(_ESC)


def att(s) -> str:
    """The page's `att()` -- `esc()` and then the quote, for a quoted attribute."""
    return esc(s).replace('"', "&quot;")


def coll(s: str) -> tuple:
    """A sort key standing in for JavaScript's `localeCompare`.

    The page sorts the country facet by `localeCompare`, which compares base
    letters first and treats an accent as a tiebreak, so Côte d'Ivoire falls
    between Congo and Djibouti rather than after Zimbabwe where a code-point sort
    puts it. Stripping the combining marks and casefolding reproduces that for a
    vocabulary of country names; the raw string is the tiebreak, as it is there.
    """
    base = "".join(c for c in unicodedata.normalize("NFD", s)
                   if not unicodedata.combining(c))
    return (base.casefold(), s)


def row_html(r, places, topics, entlabel, ents) -> str:
    """One result row -- the page's `rowHTML()`, in Python."""
    tags = []
    for p in r[3][:4]:
        tags.append(f'<span class="tag pl" data-add="places" data-v="{p}">'
                    f'{places.get(p) or p}</span>')
    for t in r[4][:4]:
        tags.append(f'<span class="tag" data-add="topics" data-v="{t}">'
                    f'{topics.get(t) or t}</span>')
    for e in [ents[i] for i in r[10]][:3]:
        tags.append(f'<span class="tag en" data-add="ents" data-v="{e}">'
                    f'{esc(entlabel.get(e) or e)}</span>')
    if r[9] == "paywalled":
        tags.append('<span class="flag">paywalled</span>')
    if r[9] == "excerpt":
        tags.append('<span class="flag">excerpt only</span>')
    if r[8]:
        tags.append('<span class="flag">document held</span>')
    sub = f'<p class="sub">{esc(r[12])}</p>' if r[12] else ""
    return ('<div class="row"><div class="date">' + (r[2] or "undated") + "</div><div>"
            f'<p class="ttl"><a href="{r[6]}" target="_blank" rel="noopener">'
            f'{esc(r[0])}</a></p>{sub}'
            f'<p class="meta">{esc(r[1] or "publisher not recorded")}</p>'
            f'<div class="tags">{"".join(tags)}</div></div></div>')


def opts_html(key, keys, labels, cnt, groups=None, group_names=None) -> str:
    """A facet's option list -- the page's `optsHTML()`, unfiltered."""
    html, last_g = [], None
    for k in keys:
        lab = labels[k]
        if groups is not None:
            g = groups.get(k) or "—"
            if g != last_g:
                name = str(group_names.get(g) or g) if group_names is not None else g
                html.append(f'<div class="grp">{name}</div>')
                last_g = g
        n = cnt.get(k, 0)
        html.append(f'<label class="opt{"" if n else " zero"}">'
                    f'<input type="checkbox" data-f="{key}" value="{att(k)}">'
                    f'<span class="lbl" title="{att(lab)}">{esc(lab)}</span>'
                    f'<span class="n">{n:,}</span></label>')
    return "".join(html) or '<div class="grp">no matches</div>'


def facet_html(key, title, keys, labels, cnt, groups=None, group_names=None,
               searchable=False) -> str:
    """A whole facet block -- the page's `facetHTML()`, unfiltered."""
    h = f'<div class="facet"><h3>{title}</h3>'
    if searchable:
        h += (f'<input class="ftype" data-f="{key}" '
              f'placeholder="Filter {title.lower()}" autocomplete="off">')
    return (h + f'<div class="opts" data-opts="{key}">'
            + opts_html(key, keys, labels, cnt, groups, group_names)
            + "</div></div>")


def first_screen(rows, ents, places, regions, topics, cats, torder, entlabel) -> dict:
    """The markup the page draws with nothing filtered: facets, rows, count, note."""
    n = len(rows)

    place_cnt, topic_cnt, year_cnt = Counter(), Counter(), Counter()
    year_lab = {}
    for r in rows:
        place_cnt.update(r[3])
        topic_cnt.update(r[4])
        y = r[2][:4]
        bucket = (PRE if int(y) < 2020 else y) if y.isdigit() else ""
        if bucket:
            year_cnt[bucket] += 1
            year_lab[bucket] = "< 2020" if bucket == PRE else bucket

    # `placeGroups`, `placeGroupNames` and `placeOrder` in the page. Regions head
    # the list, then the country groups by region name, then whatever the
    # vocabulary gives no region to; inside a group, by country name.
    pg = {k: ("@regions" if k.startswith("X") else (regions.get(k) or "@none"))
          for k in places}
    pgn = {"@regions": "Regions", "@none": "Elsewhere"}
    for k, reg in regions.items():
        if reg:
            pgn[reg] = places.get(reg) or reg
    by_grp: dict = {}
    for k in places:
        by_grp.setdefault(pg[k], []).append(k)

    def grp_key(g):
        if g == "@regions":
            return (0, ())
        if g == "@none":
            return (2, ())
        return (1, coll(str(pgn.get(g) or g)))

    place_keys = []
    for g in sorted(by_grp, key=grp_key):
        place_keys += sorted(by_grp[g], key=lambda k: coll(places[k]))
    place_keys = [k for k in place_keys if place_cnt.get(k)]
    topic_keys = [k for k in torder if topics.get(k) is not None and topic_cnt.get(k)]
    year_keys = sorted((k for k in year_lab if k != PRE), reverse=True)
    if PRE in year_lab:
        year_keys.append(PRE)

    return {
        "facets": (facet_html("places", "Country", place_keys, places, place_cnt,
                              pg, pgn, True)
                   + facet_html("topics", "Topic", topic_keys, topics, topic_cnt,
                                cats, None, True)
                   + facet_html("years", "Year published", year_keys, year_lab, year_cnt)),
        "results": "".join(row_html(r, places, topics, entlabel, ents)
                           for r in rows[:SHOWN]),
        "count": f"<b>{n:,}</b> of {n:,} records",
        # Set through `textContent` in the page, so it is text and is escaped here.
        "note": esc(f"Browsing {n:,} catalogue records. Filter state is in the URL "
                    f"— copy the address bar to share this view."),
        "n": n,
    }


def pack_rows(cdir: Path):
    """The ten browse fields, the entity tags as field 10, and two more since.

    Entities are **dictionary-encoded**: field 10 holds integer offsets into a
    vocabulary array shipped once, not the slugs themselves. 24,891 tags drawn
    from 6,774 distinct slugs cost 293 KB that way against 524 KB as repeated
    strings — and the vocabulary is what the entity facet renders its menu from,
    so it would have had to be shipped regardless.
    """
    d = json.load(open(cdir / "raw-catalogue.json", encoding="utf-8"))
    items = d["items"] if isinstance(d, dict) and "items" in d else d
    ents = sorted({e for i in items for e in (i.get("entities") or [])})
    at = {slug: n for n, slug in enumerate(ents)}
    # Field 11 is the row's **stable** document id, the key the names index posts
    # against (scripts/build-names-index.py). Rows are ordered by date and shift
    # whenever a source is ingested; these ids do not.
    docid = {}
    if DOC_IDS.exists():
        with open(DOC_IDS, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                docid[r["slug"]] = int(r["id"])
    rows = [[
        i.get("title") or "",
        i.get("publisher") or "",
        (i.get("published") or "")[:10],
        i.get("places") or [],
        i.get("topics") or [],
        i.get("lens") or [],
        i.get("url") or "",
        i.get("slug") or "",
        1 if i.get("artefact") else 0,
        i.get("body_completeness") or "",
        [at[e] for e in (i.get("entities") or [])],
        docid.get(i.get("slug") or "", -1),
        # Field 12: OSINT's one-line subtitle for the record (`notes-for-corpus` 20).
        # Empty on everything ingested before 2026-09-05, and an empty string renders
        # nothing - the backfill over the older records is Bill's to commission, and
        # until it happens the page must not invent a line for them.
        i.get("catalogue_hero") or "",
    ] for i in items]
    rows.sort(key=lambda r: r[2], reverse=True)
    return rows, ents


CHROME = chrome('catalogue', depth=1)

FOOT = foot(depth=1)


BODY = r"""
<div class="cat">
  <div class="cathead">
    <div class="cathead__text">
      <h1>Catalogue</h1>
      <div class="lede">""" + copy("catalogue", "lede") + r"""</div>
    </div>

    <!-- The downloads sit beside the lede rather than under it (prep/catalogue.md
         §10), in the site's own button style: `.btn` with a leading down arrow, the
         same control every finance table already offers. `This selection` cuts the
         current filter in the reader's browser and is disabled until there is a
         selection to cut — unfiltered, the selection *is* the catalogue, and the
         published files on the row above are the citable ones. -->
    <div class="dlbox">
      <table>
        <tr><th colspan="3">Downloads</th></tr>
        <tr><td>Whole catalogue</td>
            <td><a class="btn" href="raw-catalogue.csv" download>&darr; CSV</a></td>
            <td><a class="btn" href="raw-catalogue.json" download>&darr; JSON</a></td></tr>
        <tr><td>This selection</td>
            <td><button class="btn" data-dl="csv" disabled>&darr; CSV</button></td>
            <td><button class="btn" data-dl="json" disabled>&darr; JSON</button></td></tr>
        <tr><td>Metadata</td>
            <td><a class="btn" href="../metadata/catalogue-metadata.csv" download>&darr; CSV</a></td>
            <td></td></tr>
      </table>
      <p class="dlmsg" id="dlmsg"></p>
    </div>
  </div>

  <div class="searchrow">
    <input id="q" type="search" placeholder="Search titles, publishers, and names inside the sources" autocomplete="off">
    <select class="sort" id="sort">
      <option value="new">Newest first</option>
      <option value="old">Oldest first</option>
      <option value="az">Title A&ndash;Z</option>
    </select>
  </div>

  <div class="chips" id="chips"></div>

  <div class="cols">
    <aside id="facets">{facets}</aside>
    <main>
      <div class="countrow"><p class="count" id="count">{count}</p></div>
      <div id="results">{results}</div>
      <noscript>
        <p class="note">These are the newest {shown} of {n} records, most recent
        first. Filtering, searching and cutting a selection are all done in the
        browser, so with JavaScript off they are not available &mdash; take the whole
        catalogue from the CSV or JSON link above instead. It is the same data, every
        record and every field.</p>
      </noscript>
      <button class="more" id="more" hidden>Show more</button>
      <p class="note" id="note">{note}</p>
    </main>
  </div>
</div>
"""

# `{ver}` is substituted at build time — see `stamp()`. The token is a content hash,
# so an unchanged file keeps its URL and stays cached; a rebuilt one gets a new URL
# and cannot be served stale.
SCRIPT = r"""
<script src="catalogue-data.js{ver}"></script>
<script>
(function(){
  var D = window.CATALOGUE;
  var ROWS = D.rows;
  // Region labels come from the place vocabulary itself — every region code is a
  // row in `countries.csv` with its own name — rather than from a hand-kept map
  // that had drifted (it carried XHA, which the vocabulary does not, and wrote
  // XAF and XSS differently from the way the rest of the site does).
  function regionName(code){ return D.places[code] || code; }
  // Lens and Named actor are gone from the sidebar (prep/catalogue.md §6, §7).
  var state = {q:'', places:[], topics:[], years:[], ents:[], sort:'new', shown:100};
  var FACETS = ['places','topics','ents','years'];   // every filter the state carries
  var PRE = '<2020';                                  // the pre-2020 year bucket

  // Entity slugs arrive dictionary-encoded (field 10 = offsets into D.ents).
  // Expand once, in place: the strings are interned, so this costs array slots
  // rather than 24,891 copies, and every filter below then treats entities
  // exactly like places and topics.
  // Labels are decided at build time (`catalogue.py` → `pretty_label`), because the
  // baked first screen has to write the same ones the page writes and there can only
  // be one place that decides them. `entnames` is what the sources call the thing and
  // always wins; `entpretty` is the slug written out where nothing has named it; a
  // slug in neither reads as itself.
  var ENTS = D.ents || [], DERIVED = D.entnames || {}, PRETTY = D.entpretty || {},
      ENTLABEL = {};
  for (var li = 0; li < ENTS.length; li++)
    ENTLABEL[ENTS[li]] = DERIVED[ENTS[li]] || PRETTY[ENTS[li]] || ENTS[li];

  ROWS.forEach(function(r){
    r[10] = (r[10] || []).map(function(i){ return ENTS[i]; });
    // Hyphens become spaces in the search blob so "security studies" reaches
    // institute-for-security-studies. Acronym slugs match the acronym, which is
    // usually what a reader looking for one types anyway — and the derived display
    // name goes in alongside, so the expansion finds it too: `nira-uganda` is
    // reachable by "nira" and by "National Identification and Registration Authority".
    var alias = '';
    for (var ei = 0; ei < r[10].length; ei++){
      var dn = DERIVED[r[10][ei]];
      if (dn) alias += ' ' + dn;
    }
    // The slug (field 7) goes in verbatim, hyphens and all. It is the identifier every
    // Corpus report cites by, so a reader who has one should be able to look it up here —
    // and a record whose `url:` is a documented absence is cited *to this page* by slug
    // (`report-render.slug_offline()`, notes-for-corpus 22), which lands on nothing at all
    // unless the slug is searchable. Verbatim rather than de-hyphenated so an exact slug
    // matches exactly one row.
    //
    // **Title and hero have left this blob** (split plan Part 2). They are the two
    // longest strings on a record — 1.59 MB and 1.57 MB of the corpus against 0.60 MB
    // of publisher — and they are searched through the `titles/` shards now, one fetch
    // per query, so a reader who browses without searching never pays for them at all.
    // What is left is short: a publisher out of a 6,046-value vocabulary, the slug, and
    // the actor tags, which arrive dictionary-encoded already.
    r._s = (r[1] + ' ' + r[7] + ' ' +
            r[10].join(' ').replace(/-/g, ' ') + alias).toLowerCase();
    // The year facet counts and filters on the *bucket*, not on the year: everything
    // before 2020 is one option (prep/catalogue.md §8). The base thins out fast going
    // back, and a column of single-figure years was most of the facet's height for a
    // handful of records. An undated row has no bucket and no year, as before.
    var y = r[2].slice(0,4);
    r._y = y && +y < 2020 ? PRE : y;
  });

  // ---- the prefix-shard indexes ----------------------------------------------
  // Two of them, built the same way and fetched the same way. `titles/` holds what
  // the catalogue says about a source — its title and the hero line under it, which
  // used to be searched out of the per-row blob above. `names/` holds the names
  // occurring inside the source itself, which never were.
  //
  // **The page ships each index's shard keys and nothing else**, so a first search
  // costs one request rather than a manifest round trip and then a shard. A shard is
  // fetched the first time a query needs it, cached for the session, and never
  // fetched at all by a reader who browses without searching.
  //
  // **What a fetch failing costs is not what it used to.** A dropped names shard
  // loses the extra matches and nothing else, as before. A dropped *title* shard now
  // loses the title matches themselves — the price of not shipping 20,000 titles to
  // every visitor, paid on a bad connection instead of on every page load.
  var WINRESERVED = {con:1, prn:1, aux:1, nul:1};
  var KEYSTOP = {};
  (D.keystop || []).forEach(function(w){ KEYSTOP[w] = 1; });
  var COMBINING = /[\u0300-\u036f]/g, NOTWORD = /[^0-9a-z]+/;

  function Shard(meta, dir){
    this.meta = meta; this.dir = dir; this.keys = {};
    this.cache = {}; this.hits = null; this.busy = false; this.seq = 0;
    this.fallback = meta && meta.fallback;
    if (meta) for (var i = 0; i < meta.keys.length; i++) this.keys[meta.keys[i]] = 1;
  }
  // A plain function, not only a method, so that a test can lift it out of the built
  // page and run it — the same reason `rowHTML` and `optsHTML` are plain
  // (`scripts/test_title_index.py`, `scripts/test_catalogue_firstscreen.py`).
  Shard.prototype.keyFor = function(q){ return shardKeyFor(this, q); };
  function shardKeyFor(ix, q){
    if (!ix.meta || q.length < ix.meta.minq) return null;
    // **The key is cut from the first word of the query that could be one**, not from
    // the query's own first characters, and the accents come off first. `the digital`
    // would otherwise ask for the `th` shard — which exists, for `Thailand` and
    // `through`, and holds nothing a stopword put there — and `côte` would ask for no
    // shard at all. Both are how `shard_lib.key_of` cut the keys in the first place;
    // `KEYSTOP` arrives in the payload rather than being restated here, because a
    // second copy of that word list is a copy that would eventually disagree.
    //
    // None of this widens what *matches*: `hitsFrom` still tests the query as typed.
    var toks = (q.normalize ? q.normalize('NFD').replace(COMBINING, '') : q).split(NOTWORD);
    for (var t = 0; t < toks.length; t++){
      var w0 = toks[t];
      if (w0.length < 2 || KEYSTOP[w0]) continue;
      // Longest first, over the word **padded** — `(w + '__')[:width]`, which is
      // `shard_lib.key_of` verbatim. A fat prefix was re-cut deeper at build time and
      // the short key then does not exist, so exactly one width can match; and a word
      // shorter than the width it was cut at lives under the padded key, which is what
      // makes `SA's` reachable at all once `sa` has been split into `sa_`, `sab`, `sac`.
      // Slicing the bare word tried `sa`, found it gone, and gave up.
      var pad = w0 + '__';
      for (var w = 5; w >= 2; w--)
        if (ix.keys[pad.slice(0, w)]) return pad.slice(0, w);
    }
    // No word in the query could be a key. The texts no word could key live in one
    // shard of their own — 457 of them, nearly all Arabic titles — and asking for it
    // is the only way they are reachable at all.
    return ix.fallback && ix.keys[ix.fallback] ? ix.fallback : null;
  }
  Shard.prototype.refresh = function(q){
    var self = this, k = this.keyFor(q), seq = ++this.seq;
    this.busy = false;
    if (!k){ this.hits = null; return; }
    if (this.cache[k] !== undefined){ this.hits = hitsFrom(this.cache[k], q); return; }
    if (!window.fetch){ this.hits = null; return; }
    this.hits = null; this.busy = true;
    // `con`, `prn`, `aux` and `nul` are Windows device names and cannot be filenames
    // there, so the builder escapes them with a trailing hyphen. The key stays bare
    // everywhere else — this is the one place the two differ.
    fetch(this.dir + '/' + (WINRESERVED[k] ? k + '-' : k) + '.txt')
      .then(function(res){ return res.ok ? res.text() : null; })
      .then(function(t){
        self.cache[k] = t;
        if (seq !== self.seq) return;         // a later keystroke has overtaken this one
        self.busy = false; self.hits = hitsFrom(t, q); redraw(false);
      })
      .catch(function(){
        self.cache[k] = null;
        if (seq !== self.seq) return;
        self.busy = false; redraw(false);
      });
  };

  function hitsFrom(text, q){
    // `Text<TAB>d,d,d`, ids delta-encoded. No offsets and no order — for the names
    // index there is nothing here to render as a snippet and the page never tries;
    // for the titles it would be pointless, because the row carries the title anyway.
    var ids = null;
    if (!text) return null;
    ids = {};
    var lines = text.split('\n');
    for (var i = 0; i < lines.length; i++){
      var tab = lines[i].indexOf('\t');
      if (tab < 1) continue;
      if (lines[i].slice(0, tab).toLowerCase().indexOf(q) === -1) continue;
      var parts = lines[i].slice(tab + 1).split(','), prev = 0;
      for (var j = 0; j < parts.length; j++){ prev += +parts[j]; ids[prev] = 1; }
    }
    return ids;
  }

  var TITLES = new Shard(D.titles || null, 'titles'),
      NAMES = new Shard(D.names || null, 'names'),
      MINQ = (D.titles && D.titles.minq) || (D.names && D.names.minq) || 3;
  function refreshHits(){ TITLES.refresh(state.q); NAMES.refresh(state.q); }
  function shardHit(r){
    var id = r[11];
    if (id < 0) return false;      // no stable id, so nothing can post against it
    return !!((TITLES.hits && TITLES.hits[id]) || (NAMES.hits && NAMES.hits[id]));
  }

  // ---- downloading a selection ----------------------------------------------
  // The browse payload carries eleven of the download's sixteen fields: author,
  // date_precision, finance, words and ingested were never needed to render a row,
  // so pack_rows never packed them. That leaves three ways to export a filtered
  // selection and only one of them is honest. Serialising what the page holds gives
  // a CSV with a different column set from the published one. Packing the missing
  // five gives parity, paid for by every visitor to buy an export most never ask
  // for, on a payload design.md §6 is already worried about. So: fetch the full
  // catalogue once, on the first export click, and cut the selection from it by
  // slug. A reader who browses without exporting fetches nothing at all, and what
  // comes out has the same sixteen columns as the whole-catalogue download.
  //
  // Same lazy-fetch shape as the names index above, and it degrades the same way —
  // if the fetch fails the reader still has the whole-catalogue links at the top.
  var CSVCOLS = D.cols || [], VIEW = [], FULL = null, fullPending = null, dlMsg = '';

  function fetchFull(){
    if (FULL) return Promise.resolve(FULL);
    if (fullPending) return fullPending;
    if (!window.fetch || !window.Blob || !window.URL || !URL.createObjectURL)
      return Promise.reject(new Error('unsupported'));
    // Content-hashed, like the payload script tag above: an export must not be cut
    // from a copy of the catalogue the browser cached a build ago.
    fullPending = fetch('raw-catalogue.json' + (D.rawver || ''))
      .then(function(res){ if (!res.ok) throw new Error(res.status); return res.json(); })
      .then(function(d){
        var items = d.items || [], by = {};
        for (var i = 0; i < items.length; i++) by[items[i].slug] = items[i];
        FULL = {built: d.built, note: d.note, by: by};
        return FULL;
      })
      .catch(function(err){ fullPending = null; throw err; });   // so a retry can happen
    return fullPending;
  }

  function csvCell(v){
    // `csv.DictWriter`'s QUOTE_MINIMAL, reproduced: quote only where the value
    // carries a comma, a quote or a line break, and double an inner quote.
    if (v === null || v === undefined) v = '';
    else if (v === true) v = 'True';        // Python writes its bools this way and
    else if (v === false) v = 'False';      // `finance` is one
    else if (Array.isArray(v)) v = v.join('; ');   // build-catalogue.py's own separator
    v = String(v);
    return /[",\r\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  }
  function toCSV(items){
    // CRLF and a BOM, because that is what the published file has. RENDER.md ->
    // *The finance tables* is the standing warning about the two disagreeing, and
    // `test_catalogue_export.py` compares these bytes to `raw-catalogue.csv`.
    // The BOM arrived on 2026-08-25: without it Excel on Windows reads the file in
    // the ANSI codepage, and a cut of a catalogue whose titles are largely French,
    // Portuguese and Arabic comes out mangled. `build-catalogue.py` -> `CSV_PATH`
    // carries the reasoning.
    var out = [CSVCOLS.join(',')], i, c, row;
    for (i = 0; i < items.length; i++){
      row = [];
      for (c = 0; c < CSVCOLS.length; c++) row.push(csvCell(items[i][CSVCOLS[c]]));
      out.push(row.join(','));
    }
    return '\ufeff' + out.join('\r\n') + '\r\n';
  }

  function selectionMeta(n, built){
    // The JSON carries what produced it; the CSV cannot, which is why the filename
    // carries the build date instead.
    //
    // What this is *not* is a dated edition — and neither is the whole-catalogue
    // file, deliberately (design.md §9: the catalogue is an index over other
    // people's records, republished wholesale at an undated URL). So the thing to
    // cite is the view's own url, which re-cuts against whatever the catalogue
    // holds when it is opened, and the build date says which cut this file was.
    var f = {};
    if (state.q) f.search = state.q;
    FACETS.forEach(function(k){
      if (state[k].length) f[k] = state[k].slice();
    });
    if (state.sort !== 'new') f.sort = state.sort;
    return {url: location.href, filters: f, records: n,
            of: ROWS.length, cut: new Date().toISOString().slice(0, 19) + 'Z',
            note: 'A selection cut in a reader\'s browser from the catalogue as built on ' +
                  built + '. The catalogue is republished wholesale rather than versioned, ' +
                  'so cite the url above — it re-cuts this selection against whatever the ' +
                  'catalogue holds when it is opened.'};
  }

  function save(name, text, mime){
    var blob = new Blob([text], {type: mime + ';charset=utf-8'}),
        u = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = u; a.download = name;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){ URL.revokeObjectURL(u); }, 4000);
  }

  function exportSelection(fmt){
    // **Refuse rather than write a wrong file.** `toCSV` walks CSVCOLS, so an absent
    // column spec does not fail — it produces one empty line per record, no header,
    // which is a file that downloads, opens and says nothing. It happened for real on
    // 2026-08-24: a browser holding a payload cached from before `cols` was added
    // served exactly that, while the JSON export beside it was perfect, because the
    // JSON path never touches CSVCOLS. The `?v=` content hash on the payload is what
    // stops the cache going stale in the first place; this is the belt to that
    // braces, because a silently empty export is the worst failure on this page.
    if (fmt === 'csv' && !CSVCOLS.length){
      dlMsg = 'This page loaded without its column list, so a CSV of the selection ' +
              'would come out blank. Reload the page (Ctrl+F5) and try again — the ' +
              'whole-catalogue CSV above is unaffected.';
      drawDownload(); return;
    }
    var slugs = VIEW.map(function(r){ return r[7]; });
    dlMsg = 'busy'; drawDownload();
    fetchFull().then(function(full){
      var items = [], i, it;
      for (i = 0; i < slugs.length; i++){ it = full.by[slugs[i]]; if (it) items.push(it); }
      // Same rule from the other end: the rows on screen resolved to nothing in the
      // catalogue file, which means the two are from different builds.
      if (!items.length){
        dlMsg = 'None of these ' + slugs.length.toLocaleString() + ' records could be ' +
                'matched in the catalogue file. Reload the page (Ctrl+F5) and try again.';
        drawDownload(); return;
      }
      var base = 'catalogue-selection-' + (full.built || 'undated');
      if (fmt === 'csv') save(base + '.csv', toCSV(items), 'text/csv');
      else save(base + '.json', JSON.stringify({
        built: full.built, note: full.note,
        selection: selectionMeta(items.length, full.built),
        count: items.length, items: items
      }, null, 1) + '\n', 'application/json');
      dlMsg = ''; drawDownload();
    }).catch(function(){
      // The buttons come back with the message rather than being replaced by it:
      // the commonest cause is a dropped connection, and the fix is to press again.
      dlMsg = 'That did not come through — try again, or take the whole-catalogue ' +
              'download at the top of the page.';
      drawDownload();
    });
  }

  function drawDownload(){
    // The two `This selection` buttons live in the downloads box beside the lede and
    // are always drawn; what changes is whether they are live. Unfiltered, the
    // selection *is* the catalogue and the row above already offers the published,
    // citable files — so the buttons go quiet rather than duplicating them.
    var live = VIEW.length > 0 && VIEW.length < ROWS.length && dlMsg !== 'busy',
        msg = document.getElementById('dlmsg');
    document.querySelectorAll('.dlbox button[data-dl]').forEach(function(b){
      b.disabled = !live;
      b.title = live ? 'Download these ' + VIEW.length.toLocaleString() + ' records'
                     : 'Filter or search first — this cuts the selection you are looking at';
    });
    msg.textContent = dlMsg === 'busy' ? 'Preparing the file…' : (dlMsg || '');
  }

  function passes(r, skip){
    if (state.q && r._s.indexOf(state.q) === -1 && !shardHit(r)) return false;
    if (skip !== 'places' && state.places.length && !state.places.some(function(v){return r[3].indexOf(v)>-1;})) return false;
    if (skip !== 'topics' && state.topics.length && !state.topics.some(function(v){return r[4].indexOf(v)>-1;})) return false;
    if (skip !== 'ents'   && state.ents.length   && !state.ents.some(function(v){return r[10].indexOf(v)>-1;})) return false;
    if (skip !== 'years'  && state.years.length  && state.years.indexOf(r._y) === -1) return false;
    return true;
  }
  function counts(field, idx){
    var c = {};
    for (var i=0;i<ROWS.length;i++){
      var r = ROWS[i];
      if (!passes(r, field)) continue;
      var vals = idx === 'y' ? [r._y] : r[idx];
      for (var j=0;j<vals.length;j++) c[vals[j]] = (c[vals[j]]||0)+1;
    }
    return c;
  }
  // `order` is an explicit key sequence when the vocabulary has one of its own —
  // places by region then name, topics by the taxonomy's sort order. Where it is
  // absent the facet still falls back to count-descending, which is right for a
  // vocabulary with no inherent sequence.
  //
  // **A facet is a string, not a built element.** It used to be assembled with
  // `createElement` and an `appendChild`, which is a shape only a browser can
  // produce — and `catalogue.py` has to produce the same markup at build time for
  // the baked sidebar. So the two halves below are pure: values in, string out.
  var FBLOCK = {};   // the render inputs per facet, kept so a type-ahead keystroke
                     // repaints from them rather than recounting the whole corpus
  function optsHTML(key, keys, labels, c, sel, groups, groupNames, limit, term){
    // `limit` caps how many options are put in the DOM, not how many can be
    // found: the type-ahead filters the whole vocabulary and the cap applies
    // to what survives it. Without this the entity facet renders 6,774
    // checkboxes on every redraw, which is what makes an uncapped vocabulary
    // affordable at all. A checked option is always drawn, however deep.
    var html = '', lastG = null, drawn = 0, hidden = 0;
    for (var ki = 0; ki < keys.length; ki++){
      var k = keys[ki], lab = labels[k], on = sel.indexOf(k) > -1;
      if (term && lab.toLowerCase().indexOf(term) === -1 && k.indexOf(term) === -1) continue;
      if (limit && drawn >= limit && !on){ hidden++; continue; }
      if (groups){
        var g = groups[k] || '—';
        if (g !== lastG){ html += '<div class="grp">' + (groupNames ? (groupNames[g]||g) : g) + '</div>'; lastG = g; }
      }
      var n = c[k] || 0;
      html += '<label class="opt' + (n ? '' : ' zero') + '">' +
        '<input type="checkbox" data-f="' + key + '" value="' + att(k) + '"' + (on ? ' checked' : '') + '>' +
        '<span class="lbl" title="' + att(lab) + '">' + esc(lab) + '</span>' +
        '<span class="n">' + n.toLocaleString() + '</span></label>';
      drawn++;
    }
    if (hidden) html += '<div class="trunc">' + hidden.toLocaleString() + ' more — type above to narrow</div>';
    return html || '<div class="grp">no matches</div>';
  }
  function facetHTML(key, title, idx, labels, groups, groupNames, searchable, limit, order, term){
    var c = counts(key, idx), sel = state[key];
    var keys = (order || Object.keys(labels)).filter(function(k){
      return labels[k] !== undefined && (c[k] || sel.indexOf(k) > -1);
    });
    if (!order) keys.sort(function(a,b){ return (c[b]||0)-(c[a]||0) || labels[a].localeCompare(labels[b]); });
    FBLOCK[key] = {keys: keys, labels: labels, c: c, sel: sel, groups: groups,
                   groupNames: groupNames, limit: limit};
    var h = '<div class="facet"><h3>' + title + '</h3>';
    if (searchable) h += '<input class="ftype" data-f="' + key + '" placeholder="Filter ' + title.toLowerCase() + '" autocomplete="off">';
    return h + '<div class="opts" data-opts="' + key + '">' +
           optsHTML(key, keys, labels, c, sel, groups, groupNames, limit, term) +
           '</div></div>';
  }
  // ---- the year facet: 2020 onward, newest first, then one pre-2020 bucket -----
  function yearLabels(){
    var o = {};
    ROWS.forEach(function(r){ if (r._y) o[r._y] = r._y === PRE ? '< 2020' : r._y; });
    return o;
  }
  function yearOrder(labels){
    var ks = Object.keys(labels).filter(function(k){ return k !== PRE; });
    ks.sort().reverse();
    if (labels[PRE]) ks.push(PRE);       // the bucket sorts last, whatever it is called
    return ks;
  }

  // ---- the country facet: regions first, then region by region ----------------
  // Sorted by name, never by record count (prep/catalogue.md §2-4). A count-sorted
  // list reorders itself under the reader every time a box is ticked, and a reader
  // looking for Kenya is looking alphabetically. Group 1 is REGIONS — every region
  // and bloc code the vocabulary carries, which are places a source can be tagged to
  // in their own right — and the country groups follow it alphabetically.
  var REGIONS_GRP = '@regions';
  function placeGroups(){
    var g = {};
    Object.keys(D.places).forEach(function(k){
      g[k] = /^X/.test(k) ? REGIONS_GRP : (D.regions[k] || '@none');
    });
    return g;
  }
  function placeGroupNames(){
    var n = {}; n[REGIONS_GRP] = 'Regions'; n['@none'] = 'Elsewhere';
    Object.keys(D.regions).forEach(function(k){
      var r = D.regions[k]; if (r) n[r] = regionName(r);
    });
    return n;
  }
  function placeOrder(groups, gnames){
    var byGrp = {};
    Object.keys(D.places).forEach(function(k){
      (byGrp[groups[k]] = byGrp[groups[k]] || []).push(k);
    });
    var gs = Object.keys(byGrp).sort(function(a, b){
      if (a === REGIONS_GRP) return -1;                 // REGIONS always heads the list
      if (b === REGIONS_GRP) return 1;
      if (a === '@none') return 1;
      if (b === '@none') return -1;
      return (gnames[a] || a).localeCompare(gnames[b] || b);
    });
    var out = [];
    gs.forEach(function(g){
      byGrp[g].sort(function(a, b){ return D.places[a].localeCompare(D.places[b]); });
      out = out.concat(byGrp[g]);
    });
    return out;
  }

  function drawFacets(){
    var f = document.getElementById('facets'), keep = {};
    f.querySelectorAll('.ftype').forEach(function(i){ keep[i.dataset.f] = i.value; });
    function term(k){ return (keep[k] || '').trim().toLowerCase(); }
    var pg = placeGroups(), pgn = placeGroupNames(), yl = yearLabels();
    // Topics in the taxonomy's own order, which carries the Level 1 grouping with it.
    f.innerHTML =
      facetHTML('places','Country', 3, D.places, pg, pgn, true, 0, placeOrder(pg, pgn), term('places')) +
      facetHTML('topics','Topic', 4, D.topics, D.cats, null, true, 0, D.torder, term('topics')) +
      facetHTML('years','Year published', 'y', yl, null, null, false, 0, yearOrder(yl), '');
    // The inputs are new elements, so what a reader had typed goes back into them.
    // The options were rendered against it above, so this restores the text and not
    // the filtering — which is what the old `dispatchEvent` was doing a second pass for.
    f.querySelectorAll('.ftype').forEach(function(i){ if (keep[i.dataset.f]) i.value = keep[i.dataset.f]; });
  }
  function drawChips(){
    var c = document.getElementById('chips'), h = '';
    function add(key, label, val, text){
      h += '<span class="chip"><b>' + label + '</b> ' + esc(text) +
           ' <button data-rm="' + key + '" data-v="' + att(val) + '" aria-label="Remove">&times;</button></span>';
    }
    state.places.forEach(function(v){ add('places','Country', v, D.places[v]||v); });
    state.topics.forEach(function(v){ add('topics','Topic', v, D.topics[v]||v); });
    state.ents.forEach(function(v){ add('ents','Actor', v, ENTLABEL[v]||v); });
    state.years.forEach(function(v){ add('years','Year', v, v === PRE ? 'before 2020' : v); });
    // `state.q` arrives from the URL fragment via readHash, so it is attacker-supplied
    // on a public page and must be escaped before it reaches innerHTML.
    if (state.q) h += '<span class="chip"><b>Search</b> ' + esc(state.q) + ' <button data-rm="q" data-v="">&times;</button></span>';
    if (h) h += '<button class="clearall" id="clearall">Clear all</button>';
    c.innerHTML = h;
  }
  // One result row. Pure, for the same reason `optsHTML` is: `catalogue.py` →
  // `row_html` writes the newest hundred of these into the page at build time, and
  // `test_catalogue_firstscreen.py` lifts this function out of the built file to
  // prove the two still agree.
  function rowHTML(r){
    var tags = '';
    r[3].slice(0,4).forEach(function(p){ tags += '<span class="tag pl" data-add="places" data-v="' + p + '">' + (D.places[p]||p) + '</span>'; });
    r[4].slice(0,4).forEach(function(t){ tags += '<span class="tag" data-add="topics" data-v="' + t + '">' + (D.topics[t]||t) + '</span>'; });
    // The named-actor *facet* has gone (prep/catalogue.md §7); the tags stay, because
    // they say what a record is about and clicking one is the "more like this" the
    // sidebar list never was. The chip above it is how a reader takes it off again.
    r[10].slice(0,3).forEach(function(e){ tags += '<span class="tag en" data-add="ents" data-v="' + e + '">' + esc(ENTLABEL[e]||e) + '</span>'; });
    if (r[9] === 'paywalled') tags += '<span class="flag">paywalled</span>';
    if (r[9] === 'excerpt') tags += '<span class="flag">excerpt only</span>';
    if (r[8]) tags += '<span class="flag">document held</span>';
    return '<div class="row"><div class="date">' + (r[2]||'undated') + '</div><div>' +
      '<p class="ttl"><a href="' + r[6] + '" target="_blank" rel="noopener">' + esc(r[0]) + '</a></p>' +
      // The subtitle OSINT writes onto a record at ingest. Records taken in
      // before 2026-09-05 carry none, and the line is simply absent for them
      // rather than standing empty (notes-for-corpus 20).
      (r[12] ? '<p class="sub">' + esc(r[12]) + '</p>' : '') +
      '<p class="meta">' + esc(r[1] || 'publisher not recorded') + '</p>' +
      '<div class="tags">' + tags + '</div></div></div>';
  }
  function drawResults(){
    var out = ROWS.filter(function(r){ return passes(r, null); });
    if (state.sort === 'old') out = out.slice().reverse();
    else if (state.sort === 'az') out = out.slice().sort(function(a,b){ return a[0].localeCompare(b[0]); });
    // Held for the export, after the sort rather than before it: a downloaded
    // selection comes out in the order the reader was looking at.
    VIEW = out; dlMsg = ''; drawDownload();
    document.getElementById('count').innerHTML =
      '<b>' + out.length.toLocaleString() + '</b> of ' + ROWS.length.toLocaleString() + ' records';
    var slice = out.slice(0, state.shown), h = '';
    for (var si = 0; si < slice.length; si++) h += rowHTML(slice[si]);
    document.getElementById('results').innerHTML = h || '<p class="empty">Nothing matches those filters. Try removing one.</p>';
    var m = document.getElementById('more');
    m.hidden = out.length <= state.shown;
    m.textContent = 'Show more (' + Math.min(100, out.length - state.shown) + ' of ' + (out.length - state.shown).toLocaleString() + ' remaining)';
    var note = 'Browsing ' + ROWS.length.toLocaleString() + ' catalogue records. Filter state is in the URL — copy the address bar to share this view.';
    if (VIEW.length && VIEW.length < ROWS.length)
      note += ' A downloaded selection carries the same sixteen columns as the whole-catalogue file, cut in your browser from the build you are looking at — so cite this view’s URL rather than the file, and it will re-cut against whatever the catalogue holds when it is opened. The JSON records the filter that produced it.';
    if (TITLES.busy || NAMES.busy)
      note = 'Searching titles and the names found inside the sources…';
    else if (state.q && state.q.length < MINQ)
      note = 'Type ' + MINQ + ' characters or more to search titles and the text of ' +
             'the sources. A shorter search matches publishers, slugs and actors only. ' + note;
    else if (NAMES.hits)
      note = 'Includes matches on names occurring in the sources, not only in titles. ' + note;
    document.getElementById('note').textContent = note;
  }
  function esc(s){ return String(s).replace(/[<>&]/g, function(c){ return {'<':'&lt;','>':'&gt;','&':'&amp;'}[c]; }); }
  // For a value going into a quoted attribute rather than a text node. Filter values
  // reach these from the URL fragment, so `"` has to close nothing.
  function att(s){ return esc(s).replace(/"/g, '&quot;'); }
  function writeHash(){
    var p = [];
    if (state.q) p.push('q=' + encodeURIComponent(state.q));
    // Encoded, not raw: the pre-2020 bucket's key is `<2020`, and a `<` has no
    // business travelling naked in a fragment. `readHash` decodes before it splits.
    FACETS.forEach(function(k){ if (state[k].length) p.push(k + '=' + encodeURIComponent(state[k].join(','))); });
    if (state.sort !== 'new') p.push('sort=' + state.sort);
    history.replaceState(null, '', p.length ? '#' + p.join('&') : location.pathname);
  }
  function readHash(){
    (location.hash || '').replace(/^#/, '').split('&').forEach(function(kv){
      if (!kv) return;
      var i = kv.indexOf('='), k = kv.slice(0, i), v = decodeURIComponent(kv.slice(i + 1));
      if (k === 'q') { state.q = v.toLowerCase(); document.getElementById('q').value = v; }
      else if (k === 'sort') { state.sort = v; document.getElementById('sort').value = v; }
      // By the facet list, not by "is it a key of state" — `lens` has gone and an old
      // shared URL still carrying one should be ignored rather than setting a filter
      // with no control anywhere on the page to take it off again.
      else if (FACETS.indexOf(k) > -1) state[k] = v.split(',').filter(Boolean);
    });
  }
  function redraw(resetPage){
    if (resetPage !== false) state.shown = 100;
    drawFacets(); drawChips(); drawResults(); writeHash();
  }
  document.addEventListener('change', function(e){
    var t = e.target;
    if (t.dataset && t.dataset.f && t.type === 'checkbox'){
      var arr = state[t.dataset.f], v = t.value, i = arr.indexOf(v);
      if (t.checked && i === -1) arr.push(v); else if (!t.checked && i > -1) arr.splice(i, 1);
      redraw();
    }
    if (t.id === 'sort'){ state.sort = t.value; redraw(); }
  });
  document.addEventListener('click', function(e){
    var t = e.target;
    if (t.dataset && t.dataset.rm){
      if (t.dataset.rm === 'q'){ state.q = ''; document.getElementById('q').value = ''; refreshHits(); }
      else { var a = state[t.dataset.rm], i = a.indexOf(t.dataset.v); if (i > -1) a.splice(i, 1); }
      redraw();
    }
    if (t.id === 'clearall'){
      state.q = ''; FACETS.forEach(function(k){ state[k] = []; });
      document.getElementById('q').value = ''; refreshHits(); redraw();
    }
    if (t.dataset && t.dataset.add){
      var arr2 = state[t.dataset.add];
      if (arr2.indexOf(t.dataset.v) === -1) arr2.push(t.dataset.v);
      redraw();
    }
    if (t.id === 'more'){ state.shown += 100; drawResults(); }
    if (t.dataset && t.dataset.dl && !t.disabled){ exportSelection(t.dataset.dl); }
  });
  // The facet type-aheads are redrawn with the sidebar, so the listener is on the
  // document rather than on each input. It repaints one facet's options from
  // `FBLOCK`, which is why that cache exists: recounting the corpus on a keystroke
  // is the same work as a whole redraw.
  document.addEventListener('input', function(e){
    var t = e.target;
    if (!t || !t.className || String(t.className).indexOf('ftype') === -1) return;
    var key = t.dataset.f, b = FBLOCK[key],
        box = document.querySelector('[data-opts="' + key + '"]');
    if (!b || !box) return;
    box.innerHTML = optsHTML(key, b.keys, b.labels, b.c, b.sel, b.groups, b.groupNames,
                             b.limit, t.value.trim().toLowerCase());
  });
  var timer;
  document.getElementById('q').addEventListener('input', function(){
    var v = this.value.trim().toLowerCase();
    clearTimeout(timer);
    // 150 ms rather than 120: a shard fetch is a round trip, and on a poor mobile
    // link the round trip costs far more than the bytes. Debouncing is what keeps
    // a typed word to one request instead of one per character.
    timer = setTimeout(function(){ state.q = v; refreshHits(); redraw(); }, 150);
  });
  readHash();
  refreshHits();
  redraw();
})();
</script>
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catalogue — Data Landscapers</title>
<meta name="description" content="The Data Landscapers catalogue: every source held in the base, metadata only, each record linking to its publisher.">
<link rel="icon" href="{favicon}">
{styles}
{ga}
</head>
<body>
{chrome}
{body}
{foot}
{script}
</body>
</html>
"""


def main() -> int:
    cdir = catalogue_dir()
    rows, ents = pack_rows(cdir)
    places, regions, topics, cats, torder = vocab()
    out_dir = SITE / "catalogue"
    out_dir.mkdir(parents=True, exist_ok=True)

    # The names index, if it has been built. Only the **shard key list** is packed
    # into the page — about 12 KB — so that the first search costs exactly one
    # request rather than a manifest round-trip and then a shard. The shards
    # themselves are fetched one at a time, on demand, and never by a reader who
    # only browses. See documentation/archived/catalogue-search.md.
    # Display names for entity slugs (stage 2). Absent slugs fall back to the page's
    # own prettifier — 64% named today, and the file is meant to be hand-corrected.
    ent_names = {}
    if ENTITY_NAMES.exists():
        with open(ENTITY_NAMES, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("display"):
                    ent_names[r["slug"]] = r["display"]

    ent_names = disambiguate(ent_names)

    nm = NAMES / "manifest.json"
    names_meta = json.loads(nm.read_text(encoding="utf-8")) if nm.exists() else None
    payload_names = None
    if names_meta:
        payload_names = {"keys": names_meta["shards"], "minq": names_meta["min_query"],
                         "n": names_meta["names"], "built": names_meta["built"]}

    # The title and hero index (`build-title-index.py`, split plan Part 2). Same
    # shape, same fetch, and packed the same way — only the shard key list travels,
    # about 8 KB, so the first search is one request rather than a manifest round
    # trip and then a shard.
    tm = TITLES / "manifest.json"
    titles_meta = json.loads(tm.read_text(encoding="utf-8")) if tm.exists() else None
    payload_titles = None
    if titles_meta:
        payload_titles = {"keys": titles_meta["shards"], "minq": titles_meta["min_query"],
                          "n": titles_meta["documents"], "built": titles_meta["built"],
                          "fallback": titles_meta.get("fallback")}

    # packed data the page reads
    # Only the slugs that *have* a derived name are shipped; the rest are absent and
    # the page prettifies them, so this costs nothing for the 36% still unnamed.
    # `cols` is the download's column spec, ~200 bytes, and it is what lets the page
    # cut a filtered CSV with the same sixteen columns as the published one.
    # publish the full downloads from the catalogue Corpus built. Before the payload,
    # because the payload carries the JSON's content hash so the export cannot be cut
    # from a cached older copy of it (see `stamp`).
    for name in ("raw-catalogue.csv", "raw-catalogue.json"):
        shutil.copyfile(cdir / name, out_dir / name)

    # `entnames` is what the sources call an entity; `entpretty` is the slug written
    # out for the rest. Two maps and not one merged one, because the derived names are
    # also search aliases in the page (`r._s`) and the prettified ones must not be:
    # they are the slug again, and the slug is already in that blob de-hyphenated.
    derived = {s: n for s, n in ent_names.items() if s in set(ents)}
    pretty = {s: pretty_label(s) for s in ents if s not in derived}
    entlabel = {**derived, **pretty}

    payload = {"places": places, "regions": regions, "topics": topics, "cats": cats,
               "torder": torder,
               "ents": ents, "entnames": derived, "entpretty": pretty,
               "names": payload_names, "titles": payload_titles,
               # The words a shard is never keyed on. The page has to skip exactly the
               # ones `shard_lib.key_of` skips when it picks a key out of a query, or a
               # search for "as access relays" asks for the `as` shard — which exists,
               # for `assembly` and `association`, and does not hold the record wanted.
               "keystop": sorted(KEYSTOP),
               "cols": csv_cols(),
               "rawver": stamp(out_dir / "raw-catalogue.json"), "rows": rows}
    data_js = out_dir / "catalogue-data.js"
    with open(data_js, "w", encoding="utf-8") as fh:
        fh.write("window.CATALOGUE = ")
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";")

    # The first screen, written into the markup rather than left for the browser to
    # draw when 3 MB of payload has arrived (documentation/catalogue-split-plan.md,
    # Part 1). The page redraws over the top on load.
    baked = first_screen(rows, ents, places, regions, topics, cats, torder, entlabel)
    slots = {"facets": baked["facets"], "count": baked["count"],
             "results": baked["results"], "note": baked["note"],
             "shown": f"{min(SHOWN, baked['n']):,}", "n": f"{baked['n']:,}"}
    # One pass, so that a `{token}` inside a baked title is left alone rather than
    # read as a slot by a later replacement.
    body = re.sub(r"\{(facets|count|results|note|shown|n)\}",
                  lambda m: slots[m.group(1)], BODY)

    # the page. `{ver}` is substituted here rather than through `PAGE.format`, because
    # SCRIPT is JavaScript and full of braces `format` would try to read.
    html = PAGE.format(favicon=f"{MAIN_SITE}/assets/favicon.svg",
                       styles=styles(1, "home.css", "catalogue.css"),
                       ga=ga(),
                       chrome=CHROME, body=body, foot=FOOT,
                       script=SCRIPT.replace("{ver}", stamp(data_js)))
    (out_dir / "index.html").write_text(external_links(html), encoding="utf-8")

    # publish both shard directories
    shard_dir = out_dir / "names"
    title_dir = out_dir / "titles"
    n_shards = publish_shards(NAMES, shard_dir, names_meta, "names")
    n_titles = publish_shards(TITLES, title_dir, titles_meta, "titles")

    idx = out_dir / "index.html"
    print(f"catalogue: {len(rows):,} records, {len(ents):,} entity slugs -> site/catalogue/  "
          f"(index.html, catalogue-data.js {data_js.stat().st_size/1024:.0f} KB, csv, json)")
    print(f"  first screen baked into index.html: the newest "
          f"{min(SHOWN, len(rows)):,} rows and {baked['facets'].count('<label'):,} "
          f"facet options, {idx.stat().st_size/1024:.0f} KB of page")
    if titles_meta:
        print(f"  title index: {titles_meta['texts']:,} titles and hero lines over "
              f"{n_titles:,} shards, fetched on demand")
    else:
        # After Part 3 of the split this is not a degraded search, it is no search at
        # all — the titles will not be in the payload to fall back on.
        print("  title index: not built — run scripts/build-title-index.py")
        orphans = len(list(title_dir.glob("*.txt"))) if title_dir.exists() else 0
        if orphans:
            print(f"  WARNING: {orphans:,} published title shards under "
                  f"site/catalogue/titles/ are now unreferenced.")
    if names_meta:
        print(f"  names index: {names_meta['names']:,} names over {n_shards:,} shards, "
              f"fetched on demand")
    else:
        # `outputs/names/` is gitignored, so on a fresh clone — or after a clean — it is
        # absent and the page ships with search turned off. The shards under `site/` are
        # tracked and survive, so the published tree is then serving 1,900 files nothing
        # references. Not fatal (re-running the builder fixes it) but never what anyone
        # meant, and the prune below cannot run to tidy up because there is no manifest
        # to say what is wanted.
        orphans = len(list(shard_dir.glob("*.txt"))) if shard_dir.exists() else 0
        print("  names index: not built — run scripts/build-names-index.py")
        if orphans:
            print(f"  WARNING: {orphans:,} published shards under site/catalogue/names/ are "
                  f"now unreferenced — the page shipped without search. Run "
                  f"scripts/build-names-index.py and re-run this.")
    if ent_names:
        named = sum(1 for e in ents if e in ent_names)
        print(f"  entity display names: {named:,} of {len(ents):,} "
              f"({100*named//max(len(ents),1)}%), rest prettified from the slug")
    else:
        print("  entity display names: none — run scripts/build-entity-names.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
