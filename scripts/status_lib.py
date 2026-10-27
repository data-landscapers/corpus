"""The status baseline — its evidence sets, and the shape of the document.

Kept apart from `report-render.py` because the two answer to different rules. The report layer
resolves every citation through the published catalogue, which is the whole of what it may cite.
The baseline draws on two further bodies of evidence the vault does not hold, deliberately —
`STATUS-INIT.md` -> *Status is a baseline, and sits outside the collection perimeter* — so its
membership test is over a wider set. Putting that set here rather than in either caller is what
stops check G and check A drifting apart, which would be the worst outcome available: two tests
that both claim to answer "is this link real" and disagree.

**The two sets are different questions and both are needed.**

- `held_urls()` — catalogue, plus the AfDB dataset, plus the finance table. *May the baseline cite
  this?* A URL outside it was synthesised from a remembered pattern, which is the one defect no
  amount of reading can catch, because such a link is indistinguishable from a real one by eye.
- `catalogue_urls()` — the catalogue alone. *Does OSINT hold this?* A cited URL outside it and
  dated 2024 or later is a gap in the daily sweep and owes an acquire line *(Bill, 2026-08-15)*.
  Before 2024 it owes nothing: that is baseline material and outside the collection perimeter.

**Paths resolve through `realpath`, not `abspath`.** Every other script here runs from
`scripts/.workroot/`, where `scripts/` is a junction and `abspath` therefore reports the workroot
as the repo root. That is right for `raw/` and `wiki/`, which only resolve there — but `prep/` is
not junctioned in and would not be found. Resolving this file's own real location gives `C:\\CORPUS`
from either cwd, so the two prep CSVs are reachable without the workroot having to know about them.
"""

import csv
import glob
import urllib.parse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy_lib  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DPI_CSV = os.path.join(REPO, "prep", "africa-dpi-data.csv")
FINANCE_CSV = os.path.join(REPO, "outputs", "non-state-finance", "all-nonstate.csv")
# The internal table, not the download: this needs the record key, which came out of the
# published columns on 2026-09-09 (`build-catalogue.py` -> `CSV_COLS`). Same rows.
CATALOGUE_CSV = os.path.join(REPO, "outputs", "catalogue", "catalogue-internal.csv")
IIAG_CSV = os.path.join(REPO, "lookups", "iiag-profiles.csv")
# The acquire feed sits in a transfer folder outside both repos, which OSINT is given access to,
# so an OSINT session can read and mark the same file rather than wait for a copy carried across
# by hand. It was `C:\OSINT\osint-corpus-exchange` until 2026-08-20, on the same reasoning applied
# one directory further in — a shared drop point inside OSINT, the one place `CLAUDE.md` let
# Corpus write to. That stopped working when `C:\OSINT` became a **mirror** of a master repo on
# OSINT's own drive, refreshed after every `SWEEP-CYCLE`: a feed *read* from a mirror reads as
# empty the moment the mirror is out of step with its master, and a feed *written* to one is
# discarded at the next sync. Both happened on 2026-08-20 and check FM failed on all 30 baselines
# for a reason that had nothing to do with the baselines — their counts were right throughout.
# Outside both repos there is no mirror in the path and no write into OSINT at all, which retires
# the write exception rather than relocating it.
# `CORPUS_OSINT_XFER` overrides it, so a move onto a mapped share needs no code change.
EXCHANGE = os.environ.get("CORPUS_OSINT_XFER", r"C:\corpus-osint-xfer")
ACQUIRE_CSV = os.path.join(EXCHANGE, "africa-acquire.csv")
# The other end of the same queue. OSINT's STATUS-ACQUIRE takes a country's rows out of the
# feed and files them here with a `status` of `staged` or `dropped` and a `closed` date
# (first run, AGO, 2026-08-24). A row that has left the feed is settled, not forgotten, so
# both files have to be read to know whether a URL owes an acquisition.
ACQUIRE_DONE_CSV = os.path.join(EXCHANGE, "acquire-done.csv")
OUTLINE = os.path.join(REPO, "documentation", "status-outline.md")
# The outline is split across three files to keep each under the spec cap (review 5 R92; R151
# moved Governance out when its indicators were listed); each chapter's headings live in exactly
# one of them, and `outline()` reads all three.
OUTLINE_PARTS = (OUTLINE, os.path.join(REPO, "documentation", "status-outline-part-2.md"),
                 os.path.join(REPO, "documentation", "status-outline-part-3.md"))
REPORTS = os.path.join(REPO, "outputs", "reports")

# `finance.budget` is suspended and a status report carries 39 sub-sections, not 40
# (`documentation/status-outline-part-2.md` -> finance.budget).
SUSPENDED = ("finance.budget",)

# The appendix is out of scope and its headings are shaped like real ones, so parsing stops here.
APPENDIX = re.compile(r"^# Appendix", re.M)

_cache = {}


# --------------------------------------------------------------------------- #
# Evidence sets
# --------------------------------------------------------------------------- #

# Every separator the two source tables use to hold several URLs in one cell.
#
# The comma was the third one found, on the TGO run (2026-08-16), and it was the most expensive:
# 108 rows join their URLs with a bare comma and no space, which hid **92 real URLs** from check A
# across the dataset and cost Togo 10 facts at the pooling step. The pipe cost Egypt 15 facts and
# 46 URLs (2026-08-15) and the semicolon cost Uganda two; each was fixed where it was found, in the
# one function it was found in, which is why the third instance was still here to find.
#
# **A comma is only a separator when a URL follows it.** Splitting on every comma would break the
# URLs that legitimately carry one in the path — so the lookahead is load-bearing, not defensive.
_URL_SEP = re.compile(r"(?:[|;\s]+|,(?=\s*https?://))")


def _variants(url):
    """A URL and the forms it may legitimately take inside a markdown link.

    A literal parenthesis closes `[text](...)` early, so a held URL containing one is written
    percent-encoded and would otherwise read as a link the base does not hold. `report-render.py`
    -> `link_target()` makes the same allowance for the same reason; this is that rule applied to
    the two sets that script does not know about.

    **A trailing slash is not a different document** *(2026-08-21)*. `https://host/path/` and
    `https://host/path` are the same page to every publisher in this base, and treating them as
    two cost real work in both directions: **56 of the 2,037 lines in `africa-acquire.csv` asked
    OSINT to acquire a source it already held**, differing from the held record's URL by that one
    character — 2.7% of a queue Bill works down by hand, asking for nothing. It also fired the
    other way, as a false *not held*: CIV's and MAR's status baselines each carried an acquire
    line for a record in `raw/` all along, and both surfaced only because the record behind them
    was retired as a duplicate on 2026-08-21 and the citation had to be repointed.

    Both directions are generated rather than normalising to one, because these sets are matched
    against strings from three sources that do not agree with each other — the catalogue's `url:`
    field, the AfDB dataset's cells, and whatever an author typed inside a markdown link."""
    out = set()
    for u in (url, url.replace("(", "%28").replace(")", "%29")):
        out.add(u)
        out.add(u[:-1] if u.endswith("/") else u + "/")
    return out


def dpi_urls():
    """Every URL cited by the AfDB dataset, over all 54 countries.

    Not filtered by country. The check is "is this link real", not "did this country's rows cite
    it" — a narrower set would fail a report for citing a regional source correctly.

    Cells holding several URLs are split on `_URL_SEP` — see the note there, which carries the
    count for each separator found and why the comma needs a lookahead. 418 of the 22,848 rows
    carrying a URL use the pipe and 108 use a bare comma; reading such a cell whole holds only
    the concatenation, so every real URL in the row fails check A and the pooling step drops a
    fact citing one correctly as a link the base does not hold."""
    if "dpi" not in _cache:
        out = set()
        if os.path.exists(DPI_CSV):
            with open(DPI_CSV, encoding="utf-8-sig", newline="") as fh:
                for row in csv.DictReader(fh):
                    for u in _URL_SEP.split(row.get("Source urls") or ""):
                        u = u.strip().strip(".,;")
                        if u.startswith("http"):
                            out |= _variants(u)
        _cache["dpi"] = out
    return _cache["dpi"]


def finance_urls():
    """Every URL cited by the finance table.

    Split on `_URL_SEP`, the same separator set `dpi_urls()` uses — one definition, so a separator
    found in one table is fixed in both. Six of the 1,243 rows carrying a URL hold two in the one
    cell, and reading it whole holds only the concatenation, so both real URLs fail check A and a
    report citing one correctly is failed for a synthesised link. *(Found 2026-08-15 on the UGA
    run, by the extraction agent that cited the first of the two. Sharing the constant is what
    the TGO run added: the same fault was fixed here and in `dpi_urls()` separately, and a third
    separator then sat undetected in both for a day.)*"""
    if "finance" not in _cache:
        out = set()
        if os.path.exists(FINANCE_CSV):
            with open(FINANCE_CSV, encoding="utf-8-sig", newline="") as fh:
                for row in csv.DictReader(fh):
                    for u in _URL_SEP.split(row.get("url") or ""):
                        u = u.strip().strip(".,;")
                        if u.startswith("http"):
                            out |= _variants(u)
        _cache["finance"] = out
    return _cache["finance"]


SITE_BASE = "https://corpus.data-landscapers.io"


def catalogue_urls():
    """Every URL the published catalogue resolves — what OSINT holds and a reader can trace.

    **A record that documented having no URL resolves too, to its own row in the catalogue.**
    `wiki/schemas.md` §4 admits a blank `url:` where `url_note:` states a dated, exhausted
    search; the record is then the source, and `report-render.slug_offline()` cites it at
    `/catalogue/#q={slug}` (`notes-for-corpus` 22). Check A is set membership over what a
    baseline may cite, so it has to hold the same addresses the renderer writes — or a drafter
    citing a documented absence correctly would fail the check that exists to catch invented
    URLs. Built here rather than imported so `report-render.py` and this file cannot drift into
    two answers for the same slug: both derive it from the catalogue's own `slug` column."""
    if "cat" not in _cache:
        out = set()
        with open(CATALOGUE_CSV, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                u = (row.get("url") or "").strip()
                if u:
                    out |= _variants(u)
                elif (row.get("url_note") or "").strip():
                    slug = (row.get("slug") or "").strip()
                    if slug:
                        out |= _variants(f"{SITE_BASE}/catalogue/#q={urllib.parse.quote(slug)}")
        _cache["cat"] = out
    return _cache["cat"]


def catalogue_published():
    """url -> the source's own publication date, for the held half of a baseline's citations."""
    if "pub" not in _cache:
        out = {}
        with open(CATALOGUE_CSV, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                u, p = (row.get("url") or "").strip(), (row.get("published") or "").strip()
                if u and p:
                    for v in _variants(u):
                        out[v] = p
        _cache["pub"] = out
    return _cache["pub"]


def iiag_urls():
    """The Mo Ibrahim Foundation's per-country IIAG profiles.

    96 of the DPI dataset's 462 rows per country come from the IIAG, and **not one of them carries
    a URL** — the `Source urls` column holds source-organisation abbreviations rather than links,
    so under *no link, no claim* the whole family was uncitable and the first run dropped it. The
    profile is the primary those scores are published in. It is a fourth body of evidence and
    belongs in the set for the same reason the other three do: it is what the process read.

    Read from `lookups/iiag-profiles.csv`, which `scripts/iiag-profiles.py` writes only after
    fetching every profile and reading the country name out of the PDF's own cover. A remembered
    URL pattern is precisely what check A exists to catch, so the pattern is not trusted here — the
    lookup is the record of it having been tested."""
    if "iiag" not in _cache:
        out = set()
        if os.path.exists(IIAG_CSV):
            with open(IIAG_CSV, encoding="utf-8-sig", newline="") as fh:
                for row in csv.DictReader(fh):
                    u = (row.get("url") or "").strip()
                    if u.startswith("http"):
                        out |= _variants(u)
        _cache["iiag"] = out
    return _cache["iiag"]


def acquire_rows():
    """The acquire feed, every country. `africa-acquire.csv` in EXCHANGE, written by `status-acquire.py`.

    One file rather than 54 markdown tables, so the queue can be sorted, filtered and counted, and
    read here so the checker and the writer cannot disagree about its shape."""
    if not os.path.exists(ACQUIRE_CSV):
        return []
    with open(ACQUIRE_CSV, encoding="utf-8-sig", newline="") as fh:
        return [r for r in csv.DictReader(fh) if r.get("iso3")]


def status_owned(row) -> bool:
    """Whether an acquire row is the status report's, rather than another writer's in the same feed.

    The budget extract queues the documents it needs as `finance.budget` rows *(budget sprint,
    2026-09-24)*: they carry no cited URL and often no date, because the document is what is
    missing. `finance.budget` is suspended from the status report, so no status line can carry
    it. Read as status lines they failed check F and inflated `acquire_lines` on every unit with
    a budget request (R78, 2026-09-25); rewritten as status lines, `status-acquire.py` would
    have deleted them."""
    return (row.get("sub_section") or "").strip() != "finance.budget"


def acquire_done_rows():
    """The closed half of the acquire queue. `acquire-done.csv` in EXCHANGE, written by OSINT.

    Same columns as the feed plus `closed`. Read here so that a row OSINT has settled — staged into
    its ingest queue, or dropped with a reason — is not read back as a gap by anything on this
    side: it left `africa-acquire.csv` because it was answered."""
    if not os.path.exists(ACQUIRE_DONE_CSV):
        return []
    with open(ACQUIRE_DONE_CSV, encoding="utf-8-sig", newline="") as fh:
        return [r for r in csv.DictReader(fh) if r.get("iso3")]


def extra_urls():
    """The three bodies the catalogue does not cover. What check G has to add for a baseline."""
    return dpi_urls() | finance_urls() | iiag_urls()


def held_urls():
    """Check A's set: the whole of the evidence `STATUS-INIT` read."""
    return catalogue_urls() | extra_urls()


# --------------------------------------------------------------------------- #
# The document
# --------------------------------------------------------------------------- #

def outline():
    """[(chapter, slug, label), ...] — the 39 live sub-sections, in `lookups/taxonomy.csv` order.

    **What is in the document and what order it appears in are two questions, answered by two
    files** *(2026-08-25)*. `documentation/status-outline.md` says what a status report contains —
    the 39 questions and the guidance under each — and stays the one statement of that, so check E
    cannot fall behind it. It does not say what order the report prints in: `taxonomy.csv` does,
    for every country document at once, which is what Bill asked for on 2026-08-25 and what stops
    the status baseline opening on a different chapter from the monthly beside it.

    The outline file is left in its own reading order deliberately. Reordering 650 lines of
    guidance to encode a sequence that is now read from a four-column CSV would be storing the
    same fact twice, and the copy nobody builds from is the copy that goes stale.

    Chapter *labels* come from the outline, not from the taxonomy, because the two agree and the
    outline's are the ones the drafting process names."""
    if "outline" not in _cache:
        text = ""
        for part in OUTLINE_PARTS:
            t = open(part, encoding="utf-8").read()
            stop = APPENDIX.search(t)
            text += "\n" + (t[:stop.start()] if stop else t)
        out, chapter = [], None
        for line in text.splitlines():
            h2 = re.match(r"^## (.+)$", line)
            h3 = re.match(r"^### `([a-z]+\.[a-z]+)`\s*[—-]\s*(.+)$", line)
            if h2:
                chapter = h2.group(1).strip()
            elif h3 and h3.group(1) not in SUSPENDED:
                out.append((chapter, h3.group(1), h3.group(2).strip()))
        _cache["outline"] = sorted(out, key=lambda row: taxonomy_lib.sort_key(row[1]))
    return _cache["outline"]


def frontmatter(text):
    """Flat scalar frontmatter as a dict. Empty where there is none."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def body(text):
    """The document below its frontmatter."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            return text[end + 4:]
    return text


def sections(text):
    """[(slug, label, prose), ...] as the document actually carries them, in file order.

    The slug rides in an HTML comment under its `###` heading (`STATUS-INIT.md` -> *Output shape*),
    which is what keeps the file machine-mappable without putting taxonomy noise in front of a
    reader. A heading with no comment yields a slug of None and check E reports it."""
    out, text = [], body(text)
    parts = re.split(r"^### (.+)$", text, flags=re.M)
    for i in range(1, len(parts), 2):
        label, rest = parts[i].strip(), parts[i + 1]
        m = re.match(r"\s*<!--\s*([a-z]+\.[a-z]+)\s*-->", rest)
        slug = m.group(1) if m else None
        prose = rest[m.end():] if m else rest
        # A following `##` chapter heading belongs to the next chapter, not to this section.
        prose = re.split(r"^## ", prose, flags=re.M)[0]
        out.append((slug, label, prose.strip()))
    return out


def links(text):
    """Every URL carried by a markdown inline link, in either CommonMark destination form.

    The bare form cannot carry a space, so a held URL that contains one — some publishers'
    document stores emit them — is citable only in the angle-bracket form `](<...>)`. Matching
    the bare form alone left such a citation on the page and outside every check that reads this:
    not a failed check A but an *unchecked* one, which is the state check A exists to make
    impossible, and check B passed on it because the paragraph did carry a link. Percent-encoding
    is not the way out either: the catalogue holds the unencoded URL, so an encoded citation reads
    as a URL the base does not hold. (2026-09-04, the COM run, where two writers independently hit
    the same Comorian decree and both reported the gap rather than quietly dropping the source.)
    """
    return (set(re.findall(r"\]\((https?://[^)\s]+)\)", text))
            | set(re.findall(r"\]\(<(https?://[^>]+)>\)", text)))


def is_baseline(path):
    """True where this document was written by STATUS-INIT. Frontmatter only, never the body."""
    try:
        with open(path, encoding="utf-8") as fh:
            return frontmatter(fh.read(4096)).get("built_by") == "STATUS-INIT"
    except OSError:
        return False


def paragraphs(prose):
    """Prose split into paragraphs. One line per paragraph is the house rule, but a blank-line
    split is what actually defines one and survives a hand edit that wrapped something."""
    return [p.strip() for p in re.split(r"\n\s*\n", prose) if p.strip()]


def sentences(para):
    """Rough sentence split — good enough to locate an unlinked figure, not a parser.

    Splits on `. ` followed by a capital, which leaves `4.4m`, `Ltd.` and a URL's dots intact."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z“\"'\[])", para) if s.strip()]


# ---------------------------------------------------------------------------
# The closing absence line (R150, R151)
# ---------------------------------------------------------------------------
#
# **A status sub-section closes on the indicators nothing has been found for** *(Bill, R150)*,
# and the line is emitted from the unit's maturity assessment, never written by hand (R151), so
# the two layers state one position. Only *no evidence* is an absence: *unplaced* means evidence
# was found that meets no rung. A country with no row in a studied indicator's `assessment.csv`
# reads as no evidence, as it does on the map (`maturity-site.py` -> `stage_of`); an indicator
# with no study yet is not assessed for anyone and is left out.
#
# **A sub-section takes the line once it carries the markers.** R134 adds them to ZAF's
# Governance chapter and the R137 rotation to each section it brings to the sheet
# (`report-render.py --absences`); every render after that keeps the block current.

INDICATORS_CSV = os.path.join(REPO, "lookups", "indicators.csv")
MATURITY = os.path.join(REPO, "outputs", "maturity")
ABSENCE_OPEN, ABSENCE_CLOSE = "<!-- absences -->", "<!-- /absences -->"
ABSENCE_BLOCK = re.compile(r"<!-- absences -->\r?\n(.*?)<!-- /absences -->", re.S)
ABSENCE_LEAD = "Nothing has been found on"


def section_indicators():
    """{Topic L2 slug: [(indicator_id, name), ...]} for the assessed indicators, in Indicator Sort."""
    if "indicators" not in _cache:
        rows = [r for r in csv.DictReader(open(INDICATORS_CSV, encoding="utf-8"))
                if r["assessed"] == "1" and not r["retired"] and not r["removed"]]
        out = {}
        for r in sorted(rows, key=lambda r: int(r["Indicator Sort"])):
            out.setdefault(r["Topic L2"], []).append((r["indicator_id"], r["Progress indicator"]))
        _cache["indicators"] = out
    return _cache["indicators"]


def maturity_stages():
    """{indicator_id: {iso3: stage}} from every study's `assessment.csv`."""
    if "stages" not in _cache:
        out = {}
        for path in sorted(glob.glob(os.path.join(MATURITY, "*", "assessment.csv"))):
            for r in csv.DictReader(open(path, encoding="utf-8")):
                out.setdefault(r["indicator_id"], {})[r["iso3"]] = (r["stage"] or "").strip().lower()
        _cache["stages"] = out
    return _cache["stages"]


def reader_name(name):
    """An indicator's name as it reads mid-sentence: `ICT strategy` stays, `Tax register` drops
    its capital."""
    return name[0].lower() + name[1:] if len(name) > 1 and name[1].islower() else name


def absence_line(unit, slug):
    """The emitted closing line for one sub-section, or '' where nothing is absent."""
    stages = maturity_stages()
    names = [reader_name(name) for ind, name in section_indicators().get(slug, [])
             if ind in stages and stages[ind].get(unit, "no evidence") == "no evidence"]
    if not names:
        return ""
    listed = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " or " + names[-1]
    return f"{ABSENCE_LEAD} {listed}."


def refresh_absences(text, unit, add=()):
    """`text` with every absence block rewritten from the assessment, and a block added at the end
    of each sub-section named in `add` (slugs, or `all`) that has assessed indicators.

    A sub-section is a `### ` heading and its `<!-- slug -->` marker, up to the next heading."""
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    heads = [i for i, l in enumerate(lines) if l.startswith("## ") or l.startswith("### ")]
    out = []
    for n, start in enumerate(heads + [len(lines)]):
        if n == 0:
            out += lines[:start]
            continue
        head = heads[n - 1]
        section = lines[head:start]
        slug = next((m.group(1) for l in section[1:4]
                     for m in [re.match(r"\s*<!-- ([a-z]+\.[a-z]+) -->\s*$", l)] if m), None)
        body = nl.join(section)
        if slug and lines[head].startswith("### "):
            line = absence_line(unit, slug)
            block = ABSENCE_OPEN + nl + (line + nl if line else "") + ABSENCE_CLOSE
            if ABSENCE_BLOCK.search(body):
                body = ABSENCE_BLOCK.sub(lambda m: block, body, count=1)
            elif (("all" in add) or slug in add) and slug in section_indicators():
                trimmed = body.rstrip(nl)
                body = trimmed + nl + nl + block + body[len(trimmed):]
        out.extend(body.split(nl))
    return nl.join(out)


def absence_faults(text, unit):
    """[(slug, fault)] for marked sub-sections: a block that is not what the assessment emits, or
    a hand-written absence paragraph beside it (R151)."""
    faults = []
    for m in re.finditer(r"^### [^\n]*\n\s*<!-- ([a-z]+\.[a-z]+) -->(.*?)(?=^##|\Z)", text, re.S | re.M):
        slug, body = m.group(1), m.group(2)
        block = ABSENCE_BLOCK.search(body)
        if not block:
            continue
        if block.group(1).strip() != absence_line(unit, slug):
            faults.append((slug, "the absence line is not what the assessment emits — "
                                 "run report-render.py --render, never edit it"))
        outside = ABSENCE_BLOCK.sub("", body)
        for para in re.split(r"\r?\n\s*\r?\n", outside):
            p = para.strip()
            if p and not p.startswith("<!--") and all(
                    re.match(r"(?:No|Nothing)\b.*\b(?:found|held|published)\b", s)
                    for s in sentences(p)):
                faults.append((slug, f"a hand-written absence line: {p[:70]}"))
    return faults
