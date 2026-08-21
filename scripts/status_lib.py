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
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DPI_CSV = os.path.join(REPO, "prep", "africa-dpi-data.csv")
FINANCE_CSV = os.path.join(REPO, "outputs", "non-state-finance", "all-nonstate.csv")
CATALOGUE_CSV = os.path.join(REPO, "outputs", "catalogue", "raw-catalogue.csv")
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
OUTLINE = os.path.join(REPO, "documentation", "status-outline.md")
REPORTS = os.path.join(REPO, "outputs", "reports")

# `finance.budget` is suspended and a status report carries 37 sub-sections, not 38
# (`documentation/status-outline.md` -> finance.budget).
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


def catalogue_urls():
    """Every URL the published catalogue resolves — what OSINT holds and a reader can trace."""
    if "cat" not in _cache:
        out = set()
        with open(CATALOGUE_CSV, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                u = (row.get("url") or "").strip()
                if u:
                    out |= _variants(u)
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
    """[(chapter, slug, label), ...] — the 37 live sub-sections, in outline order.

    Read from `documentation/status-outline.md` rather than hardcoded, so the outline stays the
    one statement of what a status report contains and check E cannot fall behind it."""
    if "outline" not in _cache:
        text = open(OUTLINE, encoding="utf-8").read()
        stop = APPENDIX.search(text)
        if stop:
            text = text[:stop.start()]
        out, chapter = [], None
        for line in text.splitlines():
            h2 = re.match(r"^## (.+)$", line)
            h3 = re.match(r"^### `([a-z]+\.[a-z]+)`\s*[—-]\s*(.+)$", line)
            if h2:
                chapter = h2.group(1).strip()
            elif h3 and h3.group(1) not in SUSPENDED:
                out.append((chapter, h3.group(1), h3.group(2).strip()))
        _cache["outline"] = out
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
    """Every URL carried by a markdown inline link."""
    return set(re.findall(r"\]\((https?://[^)\s]+)\)", text))


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
