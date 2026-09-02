#!/usr/bin/env python3
"""
report-render.py — standing. Renders a report from its ledger (`documentation/report-layer.md` §5).

**The script owns everything outside the narrative markers; the model owns everything inside
them.** A render rebuilds the front matter, the section tables and the gaps table from
`outputs/reports/{unit}/ledger.csv` and `gaps.csv`, and **carries every existing
`<!-- narrative: key -->` block across untouched**. That is what makes a format change cost a
render rather than a redraft.

**Three documents, one ledger** (`documentation/report-layer.md` §1). *Status* renders the current rows,
*monthly* renders the rows whose `published` falls in the window, and *progress* answers a fixed
frame of indicators over a window (twelve months by default). All three are derived from the same
file by slicing it, so the second and third cost a render rather than a second reading of the base
— which is the whole reason the run issues all three at initialisation.

**The progress report is two documents behind one name** *(2026-08-26,
`documentation/progress-report-redesign.md`)*. A **country** answers the 121-indicator frame in
`lookups/indicators.csv`, one row per indicator and the same set everywhere, drawing its mapping
and its prose from `outputs/reports/{unit}/indicators.csv` — so its rows are chosen by design
rather than by arrival, and **No evidence** is the answer where the base holds nothing. A
**region** keeps the movement ledger this file has always rendered, because its sections run from
the region's institutions outwards rather than through the taxonomy and the frame was not drawn
for it. `render_progress()` dispatches; neither path knows about the other.

The country path is also the one place here where **the prose does not live in the document**. It
lives in `indicators.csv` and is rendered into the table, so there are no narrative markers to
carry across, nothing for a rebuild to drop, and no `<!-- narrative -->` block in a country
progress report at all.

**Both windows close on the day the document last changed, not on the month's last day and not on
the day the build ran** (§2). The base is swept nightly and that is what these reports are for; a
monthly covering July that stopped at 31 July would hold the first days of August back for a
month. There are no issues: each unit has one monthly and one progress report, living documents
whose windows slide. **Selection always runs to today** — a record published this morning is in
scope — but a build that finds nothing new to say leaves the document, and the window it prints,
exactly where they were *(Bill, 2026-08-14)*. `period:` is therefore the window the document
draws on, `compiled:` the day it last changed, and the two always agree.

**One renderer, a profile per process.** A country unit takes its sections from the ten Level-1
chapters of `lookups/taxonomy.csv`, in that file's own order, and issues all three documents;
an `X__` region unit reads `lookups/report-region-sections.csv`,
calls its objects bodies rather than systems, and issues **a monthly update and a progress
report, never a status report** (`REPORT-REGION.md`). Everything else — the ledger, the markers,
the windows, the checks — is the same code on the same schema.

Modes:
  --links     slug -> URL for every source slug in the ledger, resolved through `index/`.
              Unresolvable slugs are printed as UNRESOLVED and **must not be cited** — a URL
              reconstructed from a remembered pattern is indistinguishable from a real one.
  --render    write the document(s) named by --doc (default: status).
  --doc       status | monthly | progress | all.
  --month     YYYY-MM — the month the monthly's window opens in, and the month the progress
              window is counted back from. Default: the last closed month.
  --end       YYYY-MM-DD — close the window here rather than at today. For rebuilding a
              document to a stated date rather than to now.
  --window    months in the progress window (default 12 — an annual progress report).
  --check     Checks G, I, J, L and M over every rendered document in the folder.
              G: every http(s) URL is held in `index/`. I: no status or movement value outside
              the closed vocabularies, and every ***Not held*** row present in `gaps.csv`.
              J: no document compiled before the ledger's newest source, and every progress
              report carries its shape check. L: no narrative block left unwritten. M: every row
              that states a position cites a source that resolves. Exits non-zero on a miss. A report that
              fails G or M is not published; one that fails L is not finished; one that fails J
              needs a re-render.

Usage:
  python scripts/report-render.py --unit DZA --links
  python scripts/report-render.py --unit DZA --render --doc all --month 2026-07
  python scripts/report-render.py --unit DZA --render [--today YYYY-MM-DD]
  python scripts/report-render.py --unit DZA --check
"""
import argparse
import collections
import csv
import datetime
import hashlib
import importlib.util
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indicators_lib  # noqa: E402
import status_lib  # noqa: E402
import taxonomy_lib  # noqa: E402
import vault_lib  # noqa: E402
from copy_lib import copy_md  # noqa: E402

ROOT = vault_lib.ROOT
REPORTS = os.path.join(ROOT, "outputs", "reports")
COUNTRIES_CSV = os.path.join(ROOT, "lookups", "countries.csv")

# **One renderer, one profile per report process** (`documentation/report-layer.md` §5). What differs
# between a country report and a region one is its section map, what its object column is called,
# and which of the three documents it issues — not the rendering. A region issued the **progress
# report only** until 2026-09-02 (`REPORT-REGION.md`); it now issues the monthly too, on the same
# renderer, because `render_monthly()` never assumed a taxonomy section map or a status report to
# defer to — it already read `sections(unit)` and `profile(unit)` for both. Only the status report
# stays refused: no region has ever had one to open, and asking for it is refused here rather than
# branched around by every caller, so `--doc all` still means *all of this unit's documents* and a
# region yields two rather than crashing on a third it does not have.
PROFILES = {
    # **A country progress report opens on its own numbers, with no preamble above them** *(Bill,
    # 2026-08-25)*. The paragraph that used to sit here said three things a reader either already
    # knew or could not use: that it was compiled from the base, that its sections follow the status
    # report, and that its window runs to the date of issue rather than the month's close — the
    # last of which is a note about how the window is cut, in the place where what the window
    # *found* belongs. A region keeps an opener because its sections are not the taxonomy's and
    # nothing else on the page says so.
    "country": {"sections": None,
                "object": "System or instrument", "objects": "systems and instruments",
                "docs": ("status", "monthly", "progress"),
                "sections_note": ""},
    "region": {"sections": "report-region-sections.csv",
               "object": "Body, instrument or system", "objects": "bodies, instruments and systems",
               "docs": ("monthly", "progress"),
               "sections_note": "Sections run from the region's institutions outwards to what "
                                "funds them."},
}


def profile(unit):
    return PROFILES["region" if unit.startswith("X") else "country"]


def initialised(unit):
    """True where this unit's status report was written by `STATUS-INIT` and is no longer a
    ledger render.

    **An initialised unit stops issuing a rendered status report** *(Bill, 2026-08-15)*. Once
    `STATUS-INIT` has run, `{unit}-status.md` is a narrative baseline compiled from the wiki, the
    AfDB dataset and the finance table — not a table of ledger rows — and re-rendering it from
    `ledger.csv` does not update it, it destroys it and reports a normal build. That is the one
    failure here with no warning attached: the render succeeds, the file is well-formed, and what
    it replaced is only in git.

    So the document set is narrowed rather than the renderer branched. `PROFILES[...]["docs"]`
    already models which documents a unit issues, and a region already refuses a document it does
    not issue rather than rendering it empty; an initialised country is the same shape of fact.
    Keeping `--doc all` meaning *all of this unit's documents* is what makes the existing callers
    — BUILD stage 4, `rebuild.py --reports` — safe without any of them knowing about this.

    The test itself is `status_lib.is_baseline()` — one implementation, because check G reads the
    same property per file and two copies of "is this a baseline" would eventually disagree about
    a document one of them then overwrites. It reads the frontmatter only, never the body: a status
    report that happens to mention the process by name in its prose is not thereby initialised."""
    return status_lib.is_baseline(os.path.join(REPORTS, unit, f"{unit}-status.md"))


def issues(unit):
    """The documents this unit issues today, and why any are missing from the profile's set."""
    docs = profile(unit)["docs"]
    if "status" in docs and initialised(unit):
        return tuple(d for d in docs if d != "status"), (
            "its status report is the STATUS-INIT baseline, which BUILD maintains section by "
            "section as new sources arrive and never re-renders from the ledger (BUILD.md "
            "-> Stage 4)")
    return docs, f"this unit issues {', '.join(docs)} only (REPORT-REGION.md)"

NOT_HELD = "Not held"
BASELINE_NOT_HELD = "Baseline not held"
NO_CHANGE = "No change"
MARKER = re.compile(r"<!-- narrative: ([a-z0-9-]+) -->\n(.*?)\n<!-- /narrative -->", re.S)

# The two vocabularies, documentation/report-layer.md §3. They are STEMS: a value may be followed by a
# comma and a qualifying clause ("Implemented, under appeal"), and check I tests the stem.
STATUSES = ("Implemented", "Piloting", "In development", "Planned", "Discontinued", "Enacted",
            "Under review", NOT_HELD)
MOVEMENTS = ("Advanced", "Stalled", "Regressed", "Closed", NO_CHANGE, BASELINE_NOT_HELD)

NO_EVIDENCE = "No evidence"
MIXED = "Mixed"
PROGRESS = ("Advanced", "Stalled", "Regressed", MIXED, NO_CHANGE, NO_EVIDENCE)
"""The indicator layer's own closed set — `MOVEMENTS`'s sibling, not its successor.

The two share four words and are not the same vocabulary, and neither derives from the other
*(`progress-report-redesign.md` §2)*. `MOVEMENTS` describes **a ledger row** moving between two
dated positions and keeps serving the monthly; `PROGRESS` describes **an indicator** over a
window, and its last two values have no counterpart there. *Mixed* exists because several rows
can map to one indicator and move in different directions, which a per-row vocabulary can never
need. *No evidence* is not *Baseline not held*: the latter says the base holds a position now but
held none at the start, the former says the base holds nothing at all. Merging them would be a
defect, not a tidy-up."""


def stem(value):
    """The part of a status or movement value before its qualifying clause."""
    return (value or "").split(",")[0].strip()

# Both glossaries live in `content/document.md` now (Bill, 2026-08-19). They are markdown
# on the way into a markdown document, so `copy_md` rather than `copy`.
VOCAB = copy_md("document", "status-vocab")
MOVE_VOCAB = copy_md("document", "movement-vocab")
PROGRESS_VOCAB = copy_md("document", "progress-vocab")
# §4's explanatory paragraph: renderer-emitted boilerplate, identical across countries, standing
# in for the no-evidence count that is deliberately not published. It says what the frame is and
# what an empty row means, which is what a bare number could not.
FRAME_NOTE = copy_md("document", "progress-frame")


def anchor(label):
    """A heading's id, the way `markdown`'s `toc` extension slugifies it.

    Kept identical because these ids are what the reports' contents bar links to and what
    `render.py` writes onto the `<h2>` — two slugifiers that agree today and drift tomorrow give a
    nav bar of dead links, which is exactly the failure `bulletin.py` avoids by importing the
    extension's own `slugify` rather than writing a second one. Here the labels are ten known
    strings from `taxonomy.csv` rather than arbitrary prose, so a five-line rule is enough and it
    costs the report layer no dependency on `markdown`; `test_report_sections.py` asserts the two
    agree over the whole vocabulary."""
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def sections(unit):
    """[(order, section, key)] in document order, and {subject: (section, key)}.

    **A country report's sections are the taxonomy's ten Level-1 chapters, in `lookups/
    taxonomy.csv`'s own sort order** *(Bill, 2026-08-25)*. `taxonomy_lib`'s docstring has been
    holding this open since 2026-08-19 — *"Labels here; ordering not yet … when he says, `sort_key`
    is what they should use"* — and he has now said, for all three documents at once.

    What it replaces is `lookups/report-country-sections.csv`, a second grouping of the same 38
    subjects into six sections of its own. Two groupings is one too many, and the cost was not
    only that the reports opened on a different chapter from the status baseline beside them: the
    two maps **disagreed about where a subject belonged**, so `gov.legislate` sat under
    *Infrastructure* and `dpi.govtech` under *Governance and regulation*, and a subject mapped into
    two sections printed its sub-heading twice in one document. Deriving the section from the row's
    own subject makes that unrepresentable — a subject has exactly one Level-1 parent, so it can
    reach exactly one chapter.

    A region still reads `report-region-sections.csv`, and should: its sections run from the
    region's institutions outwards to what funds them, which is a different document about
    different objects and not a view of the taxonomy at all."""
    spec = profile(unit)["sections"]
    if spec is None:
        by_key, subj = {}, {}
        for key in taxonomy_lib.keys():
            l1 = taxonomy_lib.level1(key)
            if l1 not in by_key:
                by_key[l1] = (len(by_key), anchor(l1))
            subj[key] = (l1, by_key[l1][1])
        return sorted((o, l1, k) for l1, (o, k) in by_key.items()), subj
    by_key, subj = {}, {}
    with open(os.path.join(ROOT, "lookups", spec), encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            by_key[r["section_key"]] = (int(r["section_order"]), r["section"])
            subj[r["subject"]] = (r["section"], r["section_key"])
    ordered = [(o, s, k) for k, (o, s) in by_key.items()]
    return sorted(ordered), subj


def section_of(r, subj):
    """The section a ledger row renders under — **derived from its subject, not read off the row**.

    `ledger.csv` still carries a `section` column and `normalise_ledger()` keeps it in step, but
    nothing renders from it any more. A row's subject is its classification; its section is a view
    of that classification, and a stored view is a copy that can disagree with what it is a view of.
    It did: 2026-08-25 found rows whose `section` named a chapter their subject does not belong to,
    which printed them under the wrong heading with no check able to see it."""
    hit = subj.get((r.get("subject") or "").strip())
    return hit[0] if hit else (r.get("section") or "").strip()


def by_subject(rows):
    """[(subject, [rows])], grouped and ordered by `taxonomy.csv`'s sort order (§1, §5).

    A subject with no rows is simply absent from the result — which is what keeps an
    empty subject from printing a sub-heading with nothing under it in either a table
    section (status, progress) or a narrative one (monthly)."""
    groups = collections.defaultdict(list)
    for r in rows:
        groups[(r.get("subject") or "").strip()].append(r)
    return sorted(groups.items(), key=lambda kv: taxonomy_lib.sort_key(kv[0]))


def normalise_ledger(path, subj):
    """Reorders `ledger.csv` in place by `taxonomy.csv` sort order, then name, and brings each
    row's `section` into step with its subject.

    The reorder is item 1 of the 2026-08-10 report-structure change: a row's position in the file
    should follow the taxonomy, not the order a run happened to add it in.

    **The `section` rewrite is new** *(2026-08-25)*, and it is a consequence of the column no longer
    being read. `section_of()` derives the chapter from the subject, so the stored value renders
    nothing — and a column that nothing reads is a column that quietly goes wrong, which is how
    rows came to carry a section their subject does not belong to. Writing the derived value back
    keeps the file readable on its own terms and makes the disagreement impossible rather than
    merely unlikely. A row whose subject the taxonomy does not carry is left exactly as it is: the
    fix there is the subject, and overwriting the section would hide it.

    Content, `row_id`s and the file's column order are otherwise untouched, and the file is only
    rewritten when something would actually change — a ledger already in order is not rewritten,
    so this never manufactures a diff."""
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        rows = [r for r in reader if not vault_lib.blank_csv_row(r)]
    if not rows:
        return False
    before = [dict(r) for r in rows]
    if "section" in (fieldnames or []):
        for r in rows:
            hit = subj.get((r.get("subject") or "").strip())
            if hit:
                r["section"] = hit[0]
    key = lambda r: (taxonomy_lib.sort_key((r.get("subject") or "").strip()),
                     (r.get("name") or "").lower())
    rows = sorted(rows, key=key)
    if rows == before:
        return False
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)
    return True


def place_name(code):
    with open(COUNTRIES_CSV, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            if (r.get("iso-3") or "").strip() == code:
                return (r.get("country-name") or code).strip()
    return code


def read_csv(path):
    """Reads a report-layer CSV (ledger, gaps) — utf-8-sig so a BOM-written file
    never turns its first column name into `\\ufeffrow_id` and silently drops every
    keyed lookup on it (fixed 2026-08-10, token review task 7, note 199 — SLE's
    ledger carried a BOM and `--check` died on `KeyError: 'row_id'`)."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return [r for r in csv.DictReader(fh) if not vault_lib.blank_csv_row(r)]


_INDEX = None


def index_rows():
    """The index, read once per run — now for the shape check alone.

    Every citation the report layer resolves comes from `catalogue_rows()` below. What is left
    here is `source_months()`: sources per month for a unit, and for an `X__` region the scope
    traverse `report-region-init.slugs_for()` runs over `wiki/`. Neither is a slug lookup and
    neither is in the catalogue, which lists records rather than counting them.

    Read once because a single invocation checks up to 57 units. Held for the life of the process
    only, which is also what makes it safe: the base cannot move underneath a run that has already
    started reading it."""
    global _INDEX
    if _INDEX is None:
        _INDEX = vault_lib.load_index()
    return _INDEX


CATALOGUE = os.path.join(ROOT, "outputs", "catalogue", "raw-catalogue.csv")
CATALOGUE_STAMP = os.path.join(ROOT, "outputs", "catalogue", "catalogue-stamp.json")

_CATALOGUE = None


def catalogue_rows():
    """`outputs/catalogue/raw-catalogue.csv`, read once per run and checked against `raw/`.

    **The report layer resolves its citations against the published catalogue, not against
    `index/`** *(Bill, 2026-08-14)*. The catalogue is Corpus's own committed artefact — a
    `slug -> url` table for every record in `raw/`, built by stage 2 of the same run — and the
    index is local scaffolding that stage 2 happens to build it from. Citing the published view
    rather than the scaffolding means what a document links to is the same table a reader can
    download and check. Verified 2026-08-14 that the two agree exactly: 9,404 URLs each,
    identical maps, over all 5,189 slugs the 57 ledgers cite.

    **Resolution only.** The shape check (§7) still reads the index, because it asks a different
    question — how many sources the base holds per month, and for a region which slugs are in
    scope at all, which is a traverse of `wiki/` the catalogue does not carry. Checks G and M,
    and every link `cite()` writes into a document, come from here.

    What that trades is a cache that checked its own freshness for one that has to be checked,
    which is what the stamp below is for. A stale resolution table is not a crash but a wrong
    answer — an old URL printed with confidence, or a retired slug still resolving — so it is
    read as an error and not a warning.

    One deliberate narrowing: the catalogue lists **records**, so the 217 artefacts under `raw/`
    (PDFs and spreadsheets beside their record) are no longer slugs check M will accept. That is
    the right reading of §8 — an artefact is not a citable record, which is exactly what note 7
    of `notes-for-osint.md` says about the Comoros budget documents — and no ledger cites one."""
    global _CATALOGUE
    if _CATALOGUE is not None:
        return _CATALOGUE
    if not os.path.exists(CATALOGUE) or not os.path.exists(CATALOGUE_STAMP):
        raise vault_lib.StaleCatalogue(
            f"no catalogue at {CATALOGUE} — the report layer resolves every citation through it, "
            f"so there is nothing to render or check against. Run stage 2 first: "
            f"`python scripts/build-catalogue.py` (or `rebuild.py --catalogue`).")
    with open(CATALOGUE, encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("slug") or "").strip()]
    if not rows:
        raise vault_lib.StaleCatalogue(
            f"{CATALOGUE} holds no records — refusing to render or check against it, because "
            f"every citation would resolve to nothing, `cite()` would fall back to plain text, "
            f"and check G would then *pass* with no links left to check.")
    _assert_catalogue_current(len(rows))
    _CATALOGUE = rows
    return _CATALOGUE


def _assert_catalogue_current(records):
    """Refuse a catalogue that `raw/` has moved past. About a second, once per run.

    The index paid for itself by rebuilding when the base moved underneath it; the catalogue
    cannot, because building it is stage 2's job and this is stage 4 or 5. So the freshness has
    to be *asserted* instead — the same walk, the same two numbers, but the answer is stop rather
    than rebuild, since rebuilding here would put a stage's output in another stage's hands.

    Counted as well as timed: a deleted record moves no mtime, and a catalogue still carrying it
    resolves a slug the base no longer holds — a citation that publishes and then breaks, which
    is the failure `notes-for-osint.md`'s slug-permanence constraint exists to prevent."""
    stamp = json.load(open(CATALOGUE_STAMP, encoding="utf-8"))
    files, newest = vault_lib.raw_md_state()
    if not files:                                       # no raw/ under ROOT at all
        raise vault_lib.StaleCatalogue(
            f"no records under {os.path.join(ROOT, 'raw')} — this run is rooted somewhere the "
            f"base does not live, so the catalogue cannot be checked against it. Run from "
            f"scripts/.workroot/, where raw/ resolves to OSINT through the junctions.")
    behind = []
    if files != stamp.get("raw_md_files"):
        behind.append(f"{files:,} records in raw/, {stamp.get('raw_md_files', 0):,} when the "
                      f"catalogue was built")
    if newest > stamp.get("raw_md_mtime_max", 0):
        behind.append(f"a record has changed since {stamp.get('built', 'the build')}")
    if behind:
        raise vault_lib.StaleCatalogue(
            f"{CATALOGUE} is behind raw/ — " + "; ".join(behind) + ". Refusing to resolve "
            f"citations against it: a stale table does not fail, it answers wrongly. "
            f"Run stage 2 first: `python scripts/build-catalogue.py`."
            + (f" (The catalogue also holds {records:,} rows, which is not the count above.)"
               if records != stamp.get("records") else ""))


def raw_slugs():
    """Every source slug the base holds, whether or not it carries a citable URL.

    Kept apart from `slug_urls()` because the two absences are different defects and belong to
    different people. A slug the base does not hold at all is a mistake in the ledger — a typo, or
    a record retired since the row was written. A slug the base holds but which carries no `url:`
    is an uncitable record, which is OSINT's to fix and travels there as a note (§8)."""
    return {r["slug"].strip() for r in catalogue_rows()}


def slug_urls():
    """slug -> url for every record the catalogue holds.

    **A resolution table that resolves nothing is refused, not read**, in `catalogue_rows()`
    above. It is the one failure here worse than a crash: `row_url()` finds no resolvable slug,
    `cite()` falls back to plain text, and the render strips the hyperlink off every status cell
    in every document while reporting a normal build — and check G then *passes*, because a
    document with no links left has none missing. The check that exists to catch broken citations
    would certify the run that removed them all."""
    return {r["slug"].strip(): r["url"].strip()
            for r in catalogue_rows() if (r.get("url") or "").strip()}


def ledger_slugs(rows):
    seen = []
    for r in rows:
        for s in (r.get("sources") or "").split("|"):
            s = s.strip().strip("[]")
            if s and s not in seen:
                seen.append(s)
    return seen


def existing_blocks(path):
    if not os.path.exists(path):
        return {}
    return {m.group(1): m.group(2) for m in MARKER.finditer(open(path, encoding="utf-8").read())}


def link_target(url):
    """A URL safe to put inside `[text](...)`.

    A literal parenthesis closes the markdown link early, so `…XRoad%20BJ%20(1).pdf` renders as a
    dead link to `…XRoad%20BJ%20(1` and reads to check G as a URL the index does not hold. Percent-
    encoding the parens is lossless and the only difference from the held URL, so `check` compares
    against both forms rather than treating this as a missing link."""
    return url.replace("(", "%28").replace(")", "%29")


def row_url(r, urls):
    """The URL the row's current position rests on — its first resolvable source slug.

    Sources are listed with the one that establishes the present status first, so the first
    that resolves is the citation for the status cell."""
    for s in (r.get("sources") or "").split("|"):
        s = s.strip().strip("[]")
        if s and s in urls:
            return link_target(urls[s])
    return ""


def cite(value, r, urls):
    """A status cell, hyperlinked to the source it rests on.

    **The link goes on the status, not on the name.** The name is the object; the status is the
    claim, and the claim is what a reader wants to check. A ***Not held*** row carries no link
    because there is nothing behind it to link to — which is the point of the marker."""
    text = mark(value)
    if stem(value) in (NOT_HELD, BASELINE_NOT_HELD) or not value:
        return text
    url = row_url(r, urls)
    return f"[{text}]({url})" if url else text


SLUG_CITE = re.compile(r"\[([^\]]+)\]\(((?:[^()]|\([^()]*\))*)\)")
"""A citation in drafted prose: a label, and a target that should be a catalogue slug.

**The target deliberately admits spaces, and balanced parentheses, because this base's slugs
carry both.** A slug is a record's own title — `2025-11-08 Digital 2026 Eritrea (DataReportal)`
is one of 364 in the catalogue holding a bracketed qualifier — so a pattern stopping at the
first `)` would cite half of one and leave `)` printing as text. Admitting spaces has a second
purpose: a tighter pattern would simply fail to match an ill-formed
citation, and an unmatched one is not caught — it passes through
untouched and prints in the document as literal `[label](not a slug)`, which is markdown's own
behaviour for a target with a space in it. Matching it is what lets `cite_prose()` drop the dead
link and report it, and what lets check M name it. Found on a ZAF row whose `sources` field
holds a book chapter's title rather than a slug."""


def cite_prose(text, urls, unresolved):
    """Drafted indicator prose with its citations resolved from slugs to URLs.

    **The prose cites the base, not the web** *(`progress-report-redesign.md` §2)*. A drafter
    writes `[the roadmap was gazetted](2026-07-24-sa-dcdt-roadmap)` — a catalogue slug, the same
    identifier the ledger's `sources` field carries — and the slug becomes a URL here, at render
    time, exactly as `cite()` has always done for a status cell. Writing the URL directly would
    pin the document to an address the catalogue may later correct, and would let prose cite
    something the base does not hold at all.

    An unresolvable target keeps its label and loses its link, and is counted into `unresolved`
    so the run says so. That fallback is the trap `slug_urls()` names — a document with no links
    left has none missing, so check G would certify the render that stripped them — which is why
    check M tests every citation in this prose against the base independently, and fails.
    """
    def sub(m):
        label, target = m.group(1), m.group(2)
        if target.startswith(("http://", "https://", "#")):
            return m.group(0)          # left alone; check M refuses a raw URL in this prose
        if target in urls:
            return f"[{label}]({link_target(urls[target])})"
        unresolved.append(target)
        return label
    return SLUG_CITE.sub(sub, text or "")


def cell(text):
    """Prose made safe to sit in a markdown table cell.

    A literal pipe ends the cell and shifts every column after it; a newline ends the row. Both
    are silent — the table still renders, with the wrong shape — so they are removed here rather
    than checked for. The entity is what a reader sees either way.
    """
    return " ".join((text or "").replace("|", "&#124;").split())


def developments_cell(row, urls, unresolved):
    """The Developments cell: terse in the table, full behind the row's expander (§5).

    The full text is a `<details>` element written into the cell as raw HTML, which survives the
    markdown table intact and carries its own inline citations through — `render.py`'s extension
    set includes `md_in_html`, and links inside the element are converted like any others. The
    PDF prints it expanded, because a PDF has no expander and the full text is the document (§7).
    """
    # **Citations resolve before the cell is flattened, and the order is not cosmetic.**
    # `cell()` collapses runs of whitespace, and 21 slugs in this base carry a double space
    # inside them — a record's own title, kept verbatim. Flattening first rewrites the slug,
    # `slug_urls()` then fails to match it, and the citation prints as plain text with the run
    # counted only as an unresolved warning. Resolving first turns the slug into a URL, which
    # has no whitespace left to collapse. Found on a ZAF row whose slug runs two spaces after
    # a byline.
    summary = cell(cite_prose(row.get("summary"), urls, unresolved))
    # A blank line in the drafted `developments` separates one dated development from the next.
    # It cannot survive as a blank line — a table cell is one line — so it becomes the break the
    # reader would have seen anyway, and each paragraph is flattened after its own citations go.
    paras = [p.strip() for p in re.split(r"\n\s*\n", row.get("developments") or "") if p.strip()]
    full = "<br><br>".join(cell(cite_prose(p, urls, unresolved)) for p in paras)
    if not full:
        return summary
    return (f"{summary} <details><summary>Full record</summary>{full}</details>"
            if summary else f"<details><summary>Full record</summary>{full}</details>")


def mark_progress(value):
    """***No evidence*** is bold italic for the same reason ***Not held*** is (§3).

    It is not a weaker Advanced, it is a different kind of value: the other five say what the
    evidence shows, and this one says there is none. Marking it makes a column of them read as
    the absence it is rather than as a verdict the base has reached."""
    return f"***{value}***" if stem(value) == NO_EVIDENCE else (value or "—")


def status_table(rows, urls, label="System or instrument"):
    # "Milestone", not "As at" *(2026-08-14)*. The column has always printed the milestone — the
    # event that fixed the position, "Gazetted 2026-07-24" — and "As at" mislabelled it as a bare
    # date. Since the ledger's `as_at` is now `published`, the old header also named a field that
    # no longer exists. Safe for RENDER: `render.py`'s `classify_table()` keys on the *second*
    # header starting "status", not on this one, whatever its docstring says.
    out = [f"| {label} | Status | Milestone |", "|---|---|---|"]
    for r in sorted(rows, key=lambda r: (stem(r["status"]) == NOT_HELD, r["name"].lower())):
        # No fallback to `published` *(2026-08-14)*. This column prints **the event that fixed the
        # position** (§1), and `published` is the date a source reported it — a different fact. The
        # old `as_at` fallback held an event date so it could stand in; printing a publication date
        # here would put "the report said so on the 22nd" where "gazetted on the 15th" belongs,
        # which is the currency error the wiki's rules exist to prevent. 85% of rows carry a
        # milestone; the rest print an em-dash and say nothing rather than something untrue.
        at = (r.get("milestone") or "").strip() or "—"
        out.append(f"| {r['name']} | {cite(r['status'], r, urls)} | {at} |")
    return "\n".join(out)


def mark(value):
    """The not-held markers are bold italic so they read as a different kind of value (§3)."""
    return f"***{value}***" if stem(value) in (NOT_HELD, BASELINE_NOT_HELD) else (value or "—")


def month_bounds(month, window=1, end=None):
    """('YYYY-MM-DD', 'YYYY-MM-DD') — the window of `window` months ending with `month`.

    `end` carries the window past the month's last day to the day the issue is cut. The base is
    swept nightly, so a report that stops at the calendar close throws away its freshest evidence
    — the run that issues July's monthly on 4 August already holds the first four days of August
    and would otherwise hold them back a month."""
    y, m = (int(x) for x in month.split("-"))
    close = (datetime.date(y + (m == 12), (m % 12) + 1, 1) - datetime.timedelta(days=1)).isoformat()
    sm = m - window + 1
    sy = y + (sm - 1) // 12
    sm = (sm - 1) % 12 + 1
    return datetime.date(sy, sm, 1).isoformat(), max(end or close, close)


def month_span(start, end):
    """"July – August 2026" for a window that crosses a month boundary, "July 2026" for one that
    does not; the year is printed once where both months share it.

    This is the monthly's title, and it is a description of the window rather than a name for an
    issue — there are no issues (see below). It follows the window, so it changes of its own accord
    at the turn of a month, and the change is a real change to the document rather than a rebuild
    artefact: a report that now reaches into September is not the report that stopped in August."""
    a = datetime.date.fromisoformat(start)
    b = datetime.date.fromisoformat(end)
    if (a.year, a.month) == (b.year, b.month):
        return a.strftime("%B %Y")
    if a.year == b.year:
        return f"{a.strftime('%B')} – {b.strftime('%B %Y')}"
    return f"{a.strftime('%B %Y')} – {b.strftime('%B %Y')}"


"""**There is no such thing as a July issue** *(Bill, 2026-08-14)*.

There is one monthly report per unit and one progress report, each a living document whose window
slides: the monthly covers this month and last, the progress report the twelve months behind it.
Nothing is cut, replaced or superseded, so nothing is read back off the previous version — there
is no previous version, only an earlier state of the same document, which is what git is for.
`period:` is therefore always recomputed from the window the document now covers.

Everything that used to guard the boundary between issues is gone with the boundary: no
`same_issue()`, no period read-back, no blanking of narrative. Narrative always carries across,
and BUILD edits it — removing what has aged out, writing in what has arrived."""


def compiled_date(path):
    """The compiled date an existing document carries, or None."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        for line in fh.read().split("\n")[:12]:
            m = re.match(r"compiled:\s*(\d{4}-\d{2}-\d{2})\s*$", line)
            if m:
                return m.group(1)
    return None


def last_closed_month(today):
    d = datetime.date.fromisoformat(today).replace(day=1) - datetime.timedelta(days=1)
    return d.isoformat()[:7]


def in_window(date, start, end):
    return bool(date) and start <= date[:10] <= end


SLUG_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def slug_date(slug):
    """The publication date at the front of a source slug.

    **`raw/` names every source by its publication date**, so the prefix and the record's own
    `published:` field are the same date *(Bill, 2026-08-14)*. Where they differ it is only
    precision — `published: 2015` against a slug padded to `2015-01-01` — and the slug carries the
    padded form the windows need. Reading the prefix therefore costs nothing and needs no index."""
    hit = SLUG_DATE.match(slug or "")
    return hit.group(1) if hit else ""


def moved_in(rows, start, end):
    """The rows in scope for the window.

    **A report is a curated selection of `raw/` records, period-selected by their published date**
    *(Bill, 2026-08-14)*. A row is in scope when its `published` — the date of the most recent
    record it cites — falls inside the window, and it ages out when the window moves past it. At
    month turnover, records published outside the new scope are simply excluded, and because the
    date sits on the row, **the ledger is what ages both the monthly and the progress report**.

    This replaced selection on `as_at`, which was the event date a *position* was asserted from:
    the right field for dating a claim and the wrong one for choosing what a period covers. 744
    rows carried none at all and so fell out of every window however recently they were reported,
    and a row citing a July source about a February event was filed under February."""
    return [r for r in rows if in_window(r.get("published"), start, end)]


def unit_slugs(unit, rows_index):
    """The slugs that are this unit's base, or None where the place tag is the whole rule.

    A region's base is not its place tag alone (`REPORT-REGION.md` -> Scope): an ECOWAS decision
    reported from Abuja is tagged `NGA`. The scope rule has one implementation and it is imported,
    never restated — a shape check taken over a different base than the run read is a shape check
    for a different document."""
    if not unit.startswith("X"):
        return None
    spec = importlib.util.spec_from_file_location(
        "rri", os.path.join(os.path.dirname(os.path.abspath(__file__)), "report-region-init.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.slugs_for(unit, rows_index)


def source_months(unit, rows_index):
    """Sources per month for the unit — the shape check (§7), script-emitted so check J holds."""
    hist = collections.Counter()
    scoped = unit_slugs(unit, rows_index)
    for r in rows_index:
        d, fm = r.get("d") or {}, r.get("fm") or {}
        if d.get("folder") != "raw" or d.get("kind") != "source":
            continue
        if scoped is not None:
            if (d.get("slug") or os.path.basename(r["path"])[:-3]) not in scoped:
                continue
        elif unit not in [str(p) for p in vault_lib.as_list(fm.get("places"))]:
            continue
        month = str(fm.get("published") or "")[:7]
        if re.fullmatch(r"\d{4}-\d{2}", month):
            hist[month] += 1
    return hist


def shape_line(unit, start, end):
    """One sentence with the counts, near the top — §7 says record it, not run it after drafting."""
    hist = source_months(unit, index_rows())
    months = [m for m in sorted(hist) if start[:7] <= m <= end[:7]]
    if not months:
        # The printed close is the sentinel here too — this line goes into the document.
        return f"*Shape check: the base holds no dated sources for this place in {start} to {CLOSE}.*"
    half = len(months) // 2
    early = sum(hist[m] for m in months[:half])
    late = sum(hist[m] for m in months[half:])
    total = early + late
    verdict = (f" **The earlier half of the window is thin: this is a shorter comparison wearing a "
               f"longer label**, and the movement below rests mostly on the later half."
               if early == 0 or late / max(early, 1) >= 3.0 else
               " The two halves are comparable, so the comparison is made over the whole window.")
    return (f"*Shape check, run before the comparison: {total} sources for this place in the window "
            f"— {early} in the earlier half ({months[0]} to {months[half - 1] if half else months[0]}), "
            f"{late} in the later ({months[half]} to {months[-1]}).{verdict}*")


def front(title, today, unit, ledger_rows, not_held, period=None, extra=None):
    """The document's front matter. `extra` carries fields only one document has.

    **No count of what the frame found goes in here** *(`progress-report-redesign.md` §4)*. The
    progress report publishes no no-evidence count, and metadata is not a loophole in that: a
    field is a number a consumer will eventually put on a page, which is the thing §4 decided
    against. `indicators` — how many questions were asked — is a property of the frame, the same
    for every country, and says nothing about what any one of them holds."""
    fm = ["---", f"title: {title}", f"compiled: {today}"]
    if period:
        fm.append(f"period: {period}")
    fm += [f"place: {unit}", f"ledger_rows: {ledger_rows}", f"not_held: {not_held}"]
    fm += [f"{k}: {v}" for k, v in (extra or {}).items()]
    fm += [
           # The content digest `compiled:` is judged against — see write(). Filled in on write,
           # because it is a hash of the finished document.
           PENDING, "---", ""]
    return fm


LEGACY_SECTION_KEY = {
    "infrastructure": "ict-infrastructure",
    "ai-tech": "technology",
}
"""The two section keys that changed name when country reports moved onto the taxonomy's Level-1
chapters *(2026-08-25)*, so that the prose written under the old heading arrives under the new one.

`dpi`, `governance`, `inclusion` and `finance` are not here because their keys did not move; they
are the four chapters `report-country-sections.csv` and the taxonomy already agreed about.

**The four genuinely new chapters — Data, Digitalisation, Capacity, Geopolitics — start empty, and
that is right rather than a gap.** Their subjects used to be filed inside *Digital public
infrastructure*, *Governance and regulation*, *Inclusion and capacity* and *AI and the technology
sector*, so what was written about them is a paragraph *about a different chapter that mentions
them*, and there is no honest way to cut such a paragraph in two. Carrying the whole of it into
both places would publish the same prose twice under two headings; carrying it into neither would
throw away writing. So it stays where it was written and the new chapters open unwritten, which is
a state BUILD already knows how to close and check L already counts."""


def migrate_keys(keep, subj):
    """Existing narrative blocks, re-keyed onto the section scheme this render uses.

    A subject-keyed block (`{section}--{subject}`, the monthly's) carries its subject in the key,
    so its new home is computable and exact: the subject decides the chapter, and the chapter is
    the only part of the key that moved. A section-level block (the status report's and the
    progress report's) carries no subject and is re-keyed by the table above or not at all.

    Migration is additive and never overwrites: a document that already holds a block under the new
    key keeps it, so re-running this on an already-migrated file does nothing. It returns the
    retired keys as well, so `dropped()` does not report a block that was carried across under a
    different name as writing this build destroyed."""
    out, retired = dict(keep), set()
    for k, v in keep.items():
        if "--" in k:
            head, _, tail = k.partition("--")
            hit = subj.get(tail.replace("-", ".", 1))
            new = f"{hit[1]}--{tail}" if hit else k
        else:
            new = LEGACY_SECTION_KEY.get(k, k)
        if new != k:
            out.setdefault(new, v)
            retired.add(k)
    return out, retired


def blocker(path, subj=None):
    """Carry every existing narrative block across by marker id; mint empty ones for the rest.

    **An unwritten block is emitted empty, never with placeholder text** *(Bill, 2026-08-14)*.
    The renderer previously minted `_(narrative not yet written)_`, which is readable prose in a
    document a reader may download — a note-to-self that had escaped into the deliverable. An
    empty marker pair says the same thing to a drafter and to `--check`, and says nothing at all
    to a reader or to the PDF. The condition should not arise in the first place: BUILD does not
    release a document with an unwritten block (BUILD.md -> Narrative integrity), and `--check`
    counts them so BUILD can see what is left to write."""
    keep = existing_blocks(path)
    retired = set()
    if subj is not None:
        keep, retired = migrate_keys(keep, subj)
    used = set(retired)

    def block(key):
        used.add(key)
        return (f"<!-- narrative: {key} -->\n"
                f"{keep.get(key, '')}\n<!-- /narrative -->")

    def dropped():
        """Blocks that held prose and were not asked for — authored writing this build discards.

        A section with nothing in it is no longer printed, and selection moved to `published`, so
        a rebuild can legitimately drop a section that had prose under it. Legitimate is not the
        same as invisible: this is the one operation in the layer that destroys writing, and it
        used to be reported as `N narrative block(s) carried across` — counting the blocks *found*
        rather than the blocks *kept*, so a build that discarded a paragraph said it had preserved
        it. The prose is in git either way; knowing it went is the point."""
        return sorted(k for k, v in keep.items() if v.strip() and k not in used)

    return block, keep, dropped


def gaps_table(gaps, label="System or instrument"):
    out = [f"| {label} | What would settle it | Last probed |", "|---|---|---|"]
    for g in gaps:
        out.append(f"| {g['name']} | {g.get('what_would_settle_it') or '—'} | "
                   f"{g.get('probe_at') or 'not yet probed'} |")
    return out


NOT_A_DOCUMENT = ("progress-narrative-archive.md",)
"""Markdown in a unit's folder that is working material rather than a rendered document.

`progress-narrative-archive.md` holds the per-Level-1 narrative the progress report carried until
the indicator frame replaced it (`progress-report-redesign.md` §1, review item 4). It is kept as
source material for the indicator drafting pass and is published nowhere, so the document checks
have no business testing it: check G would fail a unit over a link in prose no reader can reach,
and it would do so increasingly often, since the archive is historical by design and the
catalogue moves on."""


def documents(folder):
    """The rendered documents in a unit's folder — the files the checks are about."""
    return [fn for fn in sorted(os.listdir(folder))
            if fn.endswith(".md") and fn not in NOT_A_DOCUMENT]


def load(unit):
    folder = os.path.join(REPORTS, unit)
    ledger_path = os.path.join(folder, "ledger.csv")
    normalise_ledger(ledger_path, sections(unit)[1])
    return (folder,
            read_csv(ledger_path),
            read_csv(os.path.join(folder, "gaps.csv")))


COMPILED_RE = re.compile(r"^(compiled: |\*Compiled )\d{4}-\d{2}-\d{2}", re.M)
RECORD_RE = re.compile(r"^record: [0-9a-fx]+\n", re.M)
PERIOD_CLOSE_RE = re.compile(r"^period: \d{4}-\d{2}-\d{2} to (\d{4}-\d{2}-\d{2})\s*$", re.M)
PENDING = "record: xxxxxxxxxxxx"

CLOSE = "@@CLOSE@@"
"""**The window's closing date is rendered as a sentinel and substituted on write.**

The close is not content: it is a fact about the build. It appears in `period:`, in the title, in
the H1, in the opening paragraph and — in the progress report — in every movement table's header,
and masking `period:` alone left the other five copies to move the digest every day. The document
is therefore *built* with this token wherever the close is printed, digested in that form, and the
real date substituted only when the file is actually written. Nothing is masked and nothing is
lost: two builds a week apart are byte-identical up to this one token, so they digest alike, and
a genuine change still moves the digest whatever date it carries.

`start` is a real date throughout. A window that has slid onto a new month is a different document
and should say so — which is also what pulls the printed close back into line at each turnover."""


def _canonical(text):
    """The document's content, with the two fields that describe it rather than belong to it taken
    out — the compiled date masked, the digest line removed.

    The window's close needs no masking here: it is already a sentinel in any text this sees from a
    render (see `CLOSE`). Only the *stored* copy on disk carries a real close, and `write()` puts
    that same date back into the render before comparing the two.

    The digest line is **removed** rather than masked, because a hash cannot cover the line that
    carries it, and because a document written before the field existed must canonicalise the same
    way as one written after it — otherwise the first build after the field arrives would compare
    two things that differ only in whether the field was there."""
    return RECORD_RE.sub("", COMPILED_RE.sub(r"\g<1>DATE", text))


def period_close(text):
    """The closing date a document on disk prints, or None.

    **This is not the period read-back that went with the issue model.** Nothing is rendered to it
    and nothing is decided by it: a document whose content has not changed keeps the window it
    prints by not being rewritten at all, and this reads it back only so the run can report which
    window that was."""
    m = PERIOD_CLOSE_RE.search(text)
    return m.group(1) if m else None


def digest(text):
    return hashlib.sha1(_canonical(text).encode("utf-8")).hexdigest()[:12]


def stored_digest(path):
    """The digest an existing document carries, or None if it predates the field."""
    if not os.path.exists(path):
        return None
    for line in open(path, encoding="utf-8").read().split("\n")[:12]:
        m = re.match(r"record:\s*([0-9a-f]{12})\s*$", line)
        if m:
            return m.group(1)
    return None


def note_drop(dropped, unit):
    """The write note's narrative half, plus a loud line when prose is being discarded."""
    gone = dropped()
    if gone:
        print(f"  !! {unit}: {len(gone)} narrative block(s) with prose DROPPED — their section no "
              f"longer renders: {', '.join(gone[:6])}{' ...' if len(gone) > 6 else ''}")
    return f"{len(gone)} block(s) of prose dropped" if gone else "narrative carried across"


def write(path, out, unit, note, today=None, close=None):
    """Write the document — but **only stamp a new compiled date if the record changed**
    *(Bill, 2026-08-14)*.

    `compiled:` has to mean *the date this document last changed*, not *the date the renderer last
    ran*. Those were the same thing while every render rewrote every file, which put 165 files into
    every diff and left the date unable to answer the only question it is asked.

    **The comparison is against a stored digest, not against the file.** Comparing the render to
    the file on disk looks right and is wrong, because the renderer *carries the narrative across
    from that same file*: a drafter who writes prose into a block and re-renders produces output
    identical to what is already there, so a file-to-render diff sees nothing and the date stands
    still while the document changes. That is the failure `render.py` records against 2026-08-13,
    when 116 dated PDFs were overwritten in place because bodies moved and `compiled:` did not.
    A digest of the last-written content cannot miss it: the prose is in the content, so adding
    prose changes the digest whoever wrote it and however it got there.

    A re-render that genuinely changes nothing leaves the file untouched — the old date stands, the
    mtime does not move, and **the document keeps the window it already prints** *(Bill,
    2026-08-14)*. A stated window that has fallen behind the build is acceptable, because the close
    is a property of the last change and `compiled:` says when that was. It can only ever
    understate: the close never claims evidence the document does not hold, and the next thing that
    actually moves brings both dates forward together.

    **A document with no stored digest is stamped today** *(Bill, 2026-08-14)*. There was briefly a
    migration path here that kept the existing date where the render matched the file, so that
    adding the field would neither back- nor forward-date anything. It could not work, and it
    failed in the one direction that matters: with no digest to compare against it fell back to
    comparing the render with the file, which is the exact mistake the paragraph above exists to
    reject — the renderer carries the prose across *from that file*, so a hand-written block
    reproduces itself and the comparison sees nothing. It was demonstrated on `SLE-progress.md`,
    whose prose was edited and which kept a compiled date four days older than its content, and
    it would have swallowed BUILD's whole drafting backlog, since writing prose into a block is
    precisely the change it cannot see. Stamping today is exact from the next build onward and
    wrong only in the safe direction, on the one build where the field arrives."""
    new = "\n".join(out)
    fresh = digest(new)
    stamp = close
    if today:
        held = stored_digest(path)
        if held == fresh:
            print(f"{unit}: {os.path.relpath(path, ROOT)} unchanged — "
                  f"compiled date left at {compiled_date(path) or 'unknown'}"
                  + (f", window still to {period_close(open(path, encoding='utf-8').read())}"
                     if close else ""))
            return 0
    new = new.replace(PENDING, f"record: {fresh}")
    if close:
        new = new.replace(CLOSE, stamp or close)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    print(f"{unit}: wrote {os.path.relpath(path, ROOT)} — {note}")
    return 0


def render(unit, today):
    """Status — state only, no chronology. The current rows, section by section."""
    # Belt and braces on the one operation here that cannot be undone in place. `issues()` already
    # keeps `--doc all` and `--doc status` off an initialised unit, so this should be unreachable
    # from the CLI — but it guards the function rather than the caller, because the cost of a
    # caller added later that does not know the rule is a baseline overwritten by a build that
    # reports success. Skipping, not failing: a unit whose status is maintained elsewhere has not
    # gone wrong, and a non-zero here would stop the monthly and progress renders behind it.
    if initialised(unit):
        print(f"{unit}: status is the STATUS-INIT baseline — not re-rendered from the ledger")
        return 0
    folder, ledger, gaps = load(unit)
    if not ledger:
        print(f"{unit}: ledger is empty — nothing to render")
        return 1
    ordered, subj = sections(unit)
    # A measure moves but has no current state to inventory (§1), so the status report omits it.
    ledger = [r for r in ledger if (r.get("kind") or "instrument") != "measure"]
    path = os.path.join(folder, f"{unit}-status.md")
    block, keep, dropped = blocker(path, subj)
    not_held = sum(1 for r in ledger if stem(r["status"]) == NOT_HELD)
    name = place_name(unit)
    out = front(f"{name} — digital transformation and data governance status report",
                today, unit, len(ledger), not_held) + [
        f"# {name}: status report",
        "",
        f"*Compiled {today} by Claude Opus from the documents in the Corpus repository, from "
        f"`outputs/reports/{unit}/ledger.csv` "
        f"({len(ledger)} systems and instruments, {not_held} of them ***Not held***). Each section opens with "
        f"its ledger; specific events are covered in the monthly updates. Figures are dated because most are "
        f"time-varying.*",
        "",
        VOCAB,
        "",
        "## Summary of position",
        "",
        block("summary"),
    ]
    urls = slug_urls()
    for _, section, key in ordered:
        rows = [r for r in ledger if section_of(r, subj) == section]
        out += ["", f"## {section}", ""]
        if rows:
            for subject, srows in by_subject(rows):
                out += [f"### {taxonomy_lib.label(subject)}", "", status_table(srows, urls), ""]
        else:
            out += [f"_The base holds no {section.lower()} rows for {name}. A thin evidence base is a "
                    f"finding, not a gap in this document._", ""]
        out.append(block(key))
    if gaps:
        out += ["", "## Gaps to fill", ""] + gaps_table(gaps) + ["", block("gaps")]
    out.append("")
    return write(path, out, unit, f"{len(ledger)} rows, {not_held} not held, "
                 f"{note_drop(dropped, unit)}", today)


def render_monthly(unit, today, month, end=None):
    """Monthly — what moved in the window, dated. No maturity verdicts; those are the status's.

    **A month in which nothing moved still issues a report, and the report says so** *(Bill,
    2026-08-14)*. The run used to record `nil, unchanged` and stop, which was right while a monthly
    was a dated issue nobody had to cut. It is wrong for a living document: stopping leaves the
    previous month's update on disk under its old heading, so a quiet place silently publishes a
    stale page instead of the finding that it was quiet. An absence of movement is a finding, and
    the renderer states it in its own voice — no narrative block, because there is no empty box to
    hand a drafter (BUILD.md -> Narrative integrity)."""
    folder, ledger, _ = load(unit)
    if not ledger:
        print(f"{unit}: ledger is empty — nothing to render")
        return 1
    path = os.path.join(folder, f"{unit}-monthly.md")
    start, end = month_bounds(month, 1, end or today)
    changed = moved_in(ledger, start, end)
    ordered, subj = sections(unit)
    block, keep, dropped = blocker(path, subj)
    not_held = sum(1 for r in ledger if stem(r["status"]) == NOT_HELD)
    name = place_name(unit)
    # **The title names both months the window covers** *(Bill, 2026-08-25)*. A monthly opens on
    # the first of last month and runs to the day it is cut, so "July 2026" on a document issued on
    # 25 August named the smaller half of its own window and read as an out-of-date page. Where the
    # window has not yet crossed a month boundary — a report cut inside the month it opens in —
    # `span()` prints the single month, because "July – July 2026" is a range of one.
    pretty = month_span(start, end)
    if not changed:
        out = front(f"{name} — monthly update, {pretty}", today, unit, 0, not_held,
                    period=f"{start} to {CLOSE}") + [
            f"# {name}: monthly update, {pretty}",
            "",
            f"*Nothing moved. No system or instrument on {name}'s ledger took a new position from "
            f"a source published between {start} and {CLOSE}. An absence of movement is a finding "
            f"and is reported as one: the current position of each system and instrument is in "
            f"the status report, and the comparison over the last twelve months in the progress "
            f"report.*",
            "",
        ]
        return write(path, out, unit, f"nil — no row moved in {start} to {end}, "
                     f"{note_drop(dropped, unit)}", today, end)
    # No table: §5. A monthly is developments, dated and cited, section by section — a table of
    # rows that moved restates the ledger without telling a reader what happened.
    out = front(f"{name} — monthly update, {pretty}", today, unit, len(changed), not_held,
                period=f"{start} to {CLOSE}") + [
        f"# {name}: monthly update, {pretty}",
        "",
        # **The window is described, not dated** *(Bill, 2026-08-25)*. The two ISO dates were the
        # same window the line above and the `period:` field already state, printed a third time
        # in the one place a reader arrives at first. What that reader needs from the opening
        # sentence is what the document covers, and "since the beginning of last month" says it in
        # the terms the country page's blurb uses, so the two agree without either citing a date
        # that moves nightly.
        "*Developments summarised from sources published between the beginning of last month and "
        "today.*",
        "",
        "## Summary of the month",
        "",
        block("summary"),
    ]
    for _, section, key in ordered:
        srows = [r for r in changed if section_of(r, subj) == section]
        groups = by_subject(srows)
        # **A section with nothing in it is not printed at all** *(Bill, 2026-08-14)*. Only the
        # status report states an absence, because only there is "no rows on this subject" a
        # finding about the place. In a monthly it is a finding about the window — nothing moved
        # this month — and a heading over an empty box is what handed the drafter 142 blocks to
        # fill with nothing. Silence is correct: the monthly reports what moved.
        if not groups:
            continue
        out += ["", f"## {section}", ""]
        # One narrative block per subject that actually moved this month, in taxonomy order.
        # A subject the section maps but that had nothing move gets no sub-heading and no block.
        for subject, _srows in groups:
            subkey = f"{key}--{subject.replace('.', '-')}"
            out += [f"### {taxonomy_lib.label(subject)}", "", block(subkey)]
    out.append("")
    return write(path, out, unit, f"{len(changed)} row(s) in {start} to {end}, "
                 f"{note_drop(dropped, unit)}", today, end)


def render_progress_movement(unit, today, month, window, end=None):
    """Progress — the movement ledger over a window, prior_* against current.

    **The region path.** Countries moved to the indicator frame on 2026-08-26
    (`render_progress_indicators()`); this is the document XAF, XSA and XWA still issue, and
    the only one they issue. Unchanged in behaviour.

    It is the only one of the three that can truthfully say nothing changed, and it must be willing
    to. A ***Not held*** row has no position at either end, so it is counted rather than tabled."""
    folder, ledger, gaps = load(unit)
    if not ledger:
        print(f"{unit}: ledger is empty — nothing to render")
        return 1
    ordered, subj = sections(unit)
    prof = profile(unit)
    urls = slug_urls()
    path = os.path.join(folder, f"{unit}-progress.md")
    start, end = month_bounds(month, window, end or today)
    block, keep, dropped = blocker(path, subj)
    not_held = sum(1 for r in ledger if stem(r["status"]) == NOT_HELD)
    held = [r for r in ledger if stem(r["status"]) != NOT_HELD]
    name = place_name(unit)

    def ends(r):
        """(position at start, position at end, movement) — read off the ledger.

        `position_start` and `position_end` carry the **substance** of each position, not its
        label: "30 branches, five banks (2025-08)" against "296 branches, four banks". Where the
        base establishes the thing did not exist, `position_start` says so. Only a row that
        leaves it empty falls back to ***Baseline not held***."""
        a = (r.get("position_start") or "").strip()
        b = (r.get("position_end") or "").strip()
        move = (r.get("movement") or "").strip()
        # Only the end position is cited: it is the position this run established.
        b = cite(b, r, urls) if b else f"{mark(r['status'])} ({r.get('published') or 'undated'})"
        if not a:
            a, move = mark(BASELINE_NOT_HELD), (move or BASELINE_NOT_HELD)
        return a, b, (move or NO_CHANGE)

    # A row whose most recent record was published after the window closed belongs to the status
    # report, not to a comparison it post-dates. Counted, named, kept out of the movement tables.
    after = [r for r in held if (r.get("published") or "") > end]
    held = [r for r in held if r not in after]
    rows_ends = {r["row_id"]: ends(r) for r in held}

    def mv(r):
        return stem(rows_ends[r["row_id"]][2])

    movers = [r for r in held if mv(r) in ("Advanced", "Stalled", "Regressed", "Closed")]
    unbased = [r for r in held if mv(r) == BASELINE_NOT_HELD]
    steady = [r for r in held if mv(r) == NO_CHANGE]
    # The title carries the window as months rather than as two ISO dates *(Bill, 2026-08-25)*:
    # "August 2025 – August 2026" is the span a reader is being offered, and it needs no `CLOSE`
    # sentinel because it only moves when the window crosses into a new month, which is a real
    # change to the document. The movement tables below still print the exact close, where the
    # exact date is the point.
    span = month_span(start, end)
    opener = ([f"*Compiled {today} by Claude Opus from the documents in the Corpus repository. "
               f"{prof['sections_note']} Each opens with a movement ledger comparing the position "
               f"at the start and end of the period, which runs to the date of issue rather than "
               f"to the last month's close.*", ""]
              if prof["sections_note"] else [])
    out = front(f"{name} — progress report, {span}", today, unit, len(ledger), not_held,
                period=f"{start} to {CLOSE}") + [
        f"# {name}: progress report, {span}",
        "",
    ] + opener + [
        f"*Of {len(ledger)} {prof['objects']} on this place's ledger, {len(movers)} changed "
        f"position between {start} and {CLOSE}, {len(steady)} did not, {len(unbased)} carry no "
        f"stated baseline, and {not_held} {'is' if not_held == 1 else 'are'} ***Not held*** at "
        f"both ends."
        + (f" A further {len(after)} took a position dated after {CLOSE} and are carried in the "
           f"status report rather than compared here.*" if after else "*"),
        "",
        shape_line(unit, start, end),
        "",
        MOVE_VOCAB,
        "",
        "## Summary of the period",
        "",
        block("summary"),
    ]
    # Movement first within a subject group: an unchanged row is reference matter, a moved
    # one is the report.
    rank = {NO_CHANGE: 2, BASELINE_NOT_HELD: 3}
    for _, section, key in ordered:
        rows = [r for r in held if section_of(r, subj) == section]
        # A section with no rows at either end of the window is not printed *(Bill, 2026-08-14)* —
        # see the note in render_monthly. Only the status report states an absence.
        if not rows:
            continue
        out += ["", f"## {section}", ""]
        for subject, srows in by_subject(rows):
            out += [f"### {taxonomy_lib.label(subject)}", "",
                    f"| {prof['object']} | At {start} | At {CLOSE} | Movement |",
                    "|---|---|---|---|"]
            for r in sorted(srows, key=lambda r: (rank.get(mv(r), 0), r["name"].lower())):
                a, b, m = rows_ends[r["row_id"]]
                out.append(f"| {r['name']} | {a} | {b} | {mark(m)} |")
            out.append("")
        out.append(block(key))
    if gaps:
        out += (["", "## Where the record is thin", ""] + gaps_table(gaps, prof["object"])
                + ["", block("gaps")])
    out.append("")
    return write(path, out, unit, f"{len(movers)} moved, {len(steady)} no change, "
                 f"{len(unbased)} without a baseline, {not_held} not held, "
                 f"{note_drop(dropped, unit)}", today, end)


def render_progress(unit, today, month, window, end=None):
    """Progress — dispatched on what kind of unit this is.

    **The indicator frame covers the 54 countries only** *(`progress-report-redesign.md` §1)*.
    XAF, XSA and XWA issue the progress report and nothing else, and their sections deliberately
    run from the region's institutions outwards rather than through the taxonomy — a shape the
    indicator list was not drawn for. So the region keeps the movement ledger it already has,
    rather than being handed a frame of 121 country questions to answer 121 times with No
    evidence. Extending the frame to regions later is possible; doing it silently at a migration
    is not."""
    if profile(unit)["sections"]:
        return render_progress_movement(unit, today, month, window, end)
    return render_progress_indicators(unit, today, month, window, end)


def render_progress_indicators(unit, today, month, window, end=None):
    """Progress — the fixed indicator frame, one row per indicator, the same set for every country.

    `documentation/progress-report-redesign.md` is the decision record and this is its
    implementation. The report is no longer an inventory of whatever ledger rows accumulated: its
    rows are chosen by design, and the question each answers is *what happened on this indicator
    in the window* rather than a diff of two dated positions the base often never held at both
    ends. **No evidence** is the answer where the base holds nothing, and it prints like any other
    row, because the fixed frame is precisely what makes the gaps visible (§4).

    Three properties of the old renderer do not survive, and each is deliberate. There are **no
    per-Level-1 narrative blocks** — the Developments cell does the narrative's job at the
    indicator level, and the prose lives in `indicators.csv` rather than in this file, so nothing
    is carried across and nothing can be dropped. There is **no shape check** — §7 of
    `report-layer.md` guarded a period comparison, and the frame has replaced the comparison it
    guarded. And there is **no no-evidence count** (§4): the paragraph at the top says what an
    empty row means, which a bare number never did.
    """
    folder, ledger, gaps = load(unit)
    if not ledger:
        print(f"{unit}: ledger is empty — nothing to render")
        return 1
    view = indicators_lib.load_unit(REPORTS, unit)
    if view is None:
        # **Refused, not rendered empty.** With no mapping file every indicator would resolve to
        # No evidence, and the render would write a 121-row blank frame over a real report and
        # report success — the same unrecoverable shape `initialised()` keeps off the STATUS-INIT
        # baseline, where "the render succeeds, the file is well-formed, and what it replaced is
        # only in git". The mapping pass is what fills this file; until it has run for this unit,
        # the old document is better than a correct rendering of nothing.
        print(f"{unit}: no {os.path.relpath(indicators_lib.unit_path(REPORTS, unit), ROOT)} — "
              f"the indicator mapping pass has not run for this unit, so there is nothing to "
              f"render the frame against. Refusing rather than writing 121 No evidence rows over "
              f"the existing report.")
        return 1

    ordered, _subj = sections(unit)
    prof = profile(unit)
    urls = slug_urls()
    path = os.path.join(folder, f"{unit}-progress.md")
    start, end = month_bounds(month, window, end or today)
    name = place_name(unit)
    span = month_span(start, end)
    known = {r["row_id"] for r in ledger}
    unresolved, counts = [], collections.Counter()

    out = front(f"{name} — progress report, {span}", today, unit, len(ledger),
                sum(1 for r in ledger if stem(r["status"]) == NOT_HELD),
                period=f"{start} to {CLOSE}",
                extra={"indicators": len(indicators_lib.frame())}) + [
        f"# {name}: progress report, {span}",
        "",
        FRAME_NOTE,
        "",
        f"*The period is {start} to {CLOSE}.*",
        "",
        PROGRESS_VOCAB,
        "",
    ]
    for chapter, rows in indicators_lib.by_chapter([s for _, s, _ in ordered]):
        # **Every chapter prints, and so does every indicator under it.** The old renderer skipped
        # a section with no rows, on the rule that only the status report states an absence. That
        # rule belonged to a document whose rows arrived; here the absence *is* the row, and a
        # chapter dropped for holding nothing would take the frame's whole point with it.
        out += ["", f"## {chapter}", "",
                "| Topic | Indicator | Developments | Progress |", "|---|---|---|---|"]
        for ind in rows:
            row = view.get(ind["indicator_id"]) or {}
            value = (row.get("progress") or "").strip() or NO_EVIDENCE
            counts[stem(value)] += 1
            out.append(f"| {ind['topic']} | {ind['indicator']} | "
                       f"{developments_cell(row, urls, unresolved)} | {mark_progress(value)} |")
        out.append("")
    if gaps:
        out += ["", "## Where the record is thin", ""] + gaps_table(gaps, prof["object"]) + [""]
    out.append("")

    if unresolved:
        # Loud, because the fallback is silent in the document: the label survives and the link
        # does not, so a reader sees a claim with nothing behind it and check G sees one link
        # fewer rather than one link broken. Check M is what fails the build over it.
        seen = sorted(set(unresolved))
        print(f"  !! {unit}: {len(unresolved)} citation(s) in indicator prose did not resolve and "
              f"rendered as plain text: {', '.join(seen[:6])}{' ...' if len(seen) > 6 else ''}")
    stray = sorted(i for i in view if i not in indicators_lib.ids())
    if stray:
        print(f"  !! {unit}: {len(stray)} row(s) of indicators.csv name an indicator the frame "
              f"does not hold and rendered nowhere: {', '.join(stray[:4])}")
    orphan = sorted({rid for r in view.values() for rid in indicators_lib.row_ids(r)} - known)
    if orphan:
        print(f"  !! {unit}: {len(orphan)} mapped row_id(s) are not on this ledger: "
              f"{', '.join(orphan[:4])}")
    note = ", ".join(f"{n} {v.lower()}" for v, n in counts.most_common())
    return write(path, out, unit, f"{len(indicators_lib.frame())} indicators — {note}",
                 today, end)

def check(unit):
    """Check G — every URL in the rendered documents resolves — and checks I, J, L and M.

    I, L and M each run twice for a country: once over the ledger, once over the indicator layer
    (`check_indicators`, `check_indicator_prose`, `check_indicator_sources`). The rules are the
    same rules — a closed vocabulary, nothing published unwritten, every claim sourced — asked of
    the second file the progress report now rests on.

    **The status baseline is tested against a wider set, and only the baseline** *(Bill,
    2026-08-15)*. A document compiled from the wiki may cite only what the catalogue holds, which
    is the whole of what BUILD read. `STATUS-INIT` also read the AfDB dataset and the finance
    table, deliberately and by design — a baseline has to be able to say that a 1990 law is in
    force, from a source the wiki will never hold — so testing its links against the catalogue
    alone would fail a correct report on about 250 links per country and make the check useless
    where it is most needed.

    Widening the set does not weaken the test, because set membership is the property that matters:
    a URL synthesised from a remembered pattern is not in *any* of the three, and is indistinguish-
    able from a real one by inspection, which is the only reason this check exists. What would
    weaken it is applying the wider set to the monthly and the progress report, so the widening is
    per file and keyed on the document actually being a baseline."""
    held = set(slug_urls().values())
    held |= {link_target(u) for u in held}
    bad = 0
    folder = os.path.join(REPORTS, unit)
    wider = None
    for fn in documents(folder):
        path = os.path.join(folder, fn)
        text = open(path, encoding="utf-8").read()
        urls = set(re.findall(r"\]\((https?://[^)\s]+)\)", text))
        this = held
        if fn.endswith("-status.md") and status_lib.is_baseline(path):
            if wider is None:                       # loaded lazily: 17 MB, and only a baseline needs it
                wider = held | status_lib.extra_urls()
            this = wider
        miss = [u for u in urls if u not in this]
        note = " (baseline set)" if this is wider else ""
        print(f"  {fn}: {len(urls)} links, {len(miss)} NOT HELD{note}")
        for u in miss:
            print("     NOT HELD:", u)
        bad += len(miss)
    print(f"check G: {'PASS' if not bad else 'FAIL — ' + str(bad) + ' link(s) not in index/'}")
    return ((1 if bad else 0) | check_vocab(unit) | check_asof(unit)
            | check_narrative(unit) | check_sourced(unit)
            # The indicator halves of I, L and M. Kept as separate functions rather than folded
            # into the three above because each reads a different file — the frame and the unit's
            # view of it, not the ledger — and because a country that has not yet been through
            # the mapping pass has to skip them without skipping the ledger checks beside them.
            | check_indicators(unit) | check_indicator_prose(unit)
            | check_indicator_sources(unit))


def check_narrative(unit):
    """Check L — no document carries an unwritten narrative block *(Bill, 2026-08-14)*.

    `_(narrative not yet written)_` is not acceptable, and nor is the empty block that replaced
    it: both mean a section was published with nothing said about it. BUILD.md -> Narrative
    integrity gives the two ways out — remove the section, or write the sentence explaining why
    there is no narrative.

    **This counts; it does not police.** The renderer never deletes a block body, because removing
    an author's content is not a script's decision, so the count is simply how BUILD sees the size
    of the job in front of it. It exits non-zero because an unwritten block is not a judgement call
    the way a register hit is — there is no reading of it under which the document is finished —
    and a number BUILD can act on is more use than a number it has to go looking for."""
    bad = []
    folder = os.path.join(REPORTS, unit)
    for fn in documents(folder):
        text = open(os.path.join(folder, fn), encoding="utf-8").read()
        for m in MARKER.finditer(text):
            key, body = m.group(1), m.group(2).strip()
            if not body:
                bad.append(f"{fn}: narrative block {key!r} is empty")
            elif "narrative not yet written" in body:
                bad.append(f"{fn}: narrative block {key!r} still carries the placeholder")
    for line in bad:
        print("     ", line)
    print(f"check L: {'PASS' if not bad else 'FAIL — ' + str(len(bad)) + ' unwritten block(s)'}")
    return 1 if bad else 0


def check_vocab(unit):
    """Check I — the two vocabularies are closed, and every Not held row is in gaps.csv."""
    _, ledger, gaps = load(unit)
    bad = []
    # A row whose subject this unit's map does not carry renders nowhere at all — the section loop
    # filters on equality, so it silently drops out of the document rather than failing.
    #
    # **The test is on `subject`, not on `section`** *(2026-08-25)*. It used to check the stored
    # section against the map, which could only catch a typo; the section is now derived from the
    # subject, so the subject is the field a mistake can be made in and the only one worth
    # checking. For a country that means the taxonomy — a subject outside `taxonomy.csv` has no
    # Level-1 parent — and for a region, the region's own section map.
    _, subj = sections(unit)
    for r in ledger:
        if (r.get("subject") or "").strip() not in subj:
            bad.append(f"{r['row_id']}: subject {r.get('subject')!r} is not in this unit's "
                       f"vocabulary — the row would render in no section")
        if (r.get("kind") or "instrument") == "measure":
            continue
        if stem(r["status"]) not in STATUSES:
            bad.append(f"{r['row_id']}: status {r['status']!r} is outside the vocabulary")
        move = (r.get("movement") or "").strip()
        if move and stem(move) not in MOVEMENTS:
            bad.append(f"{r['row_id']}: movement {move!r} is outside the vocabulary")
        if stem(r["status"]) != NOT_HELD and not (r.get("milestone") or "").strip():
            bad.append(f"{r['row_id']}: no milestone — the status table would print a bare date")
    gap_ids = {g["row_id"] for g in gaps}
    for r in ledger:
        if stem(r["status"]) == NOT_HELD and r["row_id"] not in gap_ids:
            bad.append(f"{r['row_id']}: Not held, but no gaps.csv line")
    for line in bad:
        print("     ", line)
    print(f"check I: {'PASS' if not bad else 'FAIL — ' + str(len(bad)) + ' problem(s)'}")
    return 1 if bad else 0


def check_asof(unit):
    """Check J — as-of honesty: a document must show what the ledger holds, and say what it rests on.

    **The failing half is staleness, and it is the one that changes what a reader sees.** A document
    compiled before the newest `published` on its ledger is rendering a position the base has
    already moved past — BUILD moved a row and did not rebuild. It is the same question OSINT's
    check C asks of a hub ("has the page been compiled since the records moved?"), asked of a
    report, and it is answered against the data rather than a file mtime, which does not survive a
    clone. The fix is a re-render, which is why this fails rather than reports.

    **The other direction is reported, not failed** *(2026-08-14)*. §6 was written as "no document
    dated ahead of its newest source", against the old behaviour where every build stamped
    `compiled:` with the render date, so a document could claim today while holding nothing since
    July, and the gap grew by a day every day. The window-close rule fixed that at the cause: the
    close and the date now move only when the document does. What remains is a genuine lag — a
    document can change for a structural reason without new evidence — and it is disclosed rather
    than judged, because a window running to a quiet tail is a true statement about a real period,
    and any threshold on it would be invented.

    The second half of §6's rule — no period comparison without the shape check recorded — is
    checked here too, **of the region document alone** *(2026-08-26)*.
    `render_progress_movement()` emits the line unconditionally, so this asserts that it stayed.
    A country progress report is no longer a period comparison: the indicator frame replaced the
    diff of two dated positions, and §7's check retired with the thing it guarded
    (`progress-report-redesign.md` §8). The `period:` half of this function is unaffected — the
    window is still real and still stated, so the lag note below still has its date."""
    folder, ledger, _ = load(unit)
    pubs = [(r.get("published") or "").strip() for r in ledger]
    newest = max([p for p in pubs if p] or [""])
    if not newest:
        print("check J: PASS (no dated source on this ledger)")
        return 0
    bad, lag = [], None
    init = initialised(unit)
    for fn in documents(folder):
        # The STATUS-INIT baseline is not derived from this ledger, so the ledger cannot date it
        # *(2026-08-15)*. The test reads "the document does not yet show it, re-render" — and both
        # halves are wrong here: the baseline draws on sources the wiki does not hold, and there is
        # no render to run. Its own currency is a different question, asked of the sources BUILD
        # reads against it, and answered by BUILD revising the section.
        if init and fn.endswith("-status.md"):
            continue
        text = open(os.path.join(folder, fn), encoding="utf-8").read()
        m = re.search(r"^compiled:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
        if m and m.group(1) < newest:
            bad.append(f"{fn}: compiled {m.group(1)}, but the ledger cites a source published "
                       f"{newest} — the document does not yet show it, re-render")
        if fn.endswith("-progress.md"):
            # **The shape check is asserted of the region document only** *(2026-08-26)*. §7's
            # rule is "no period comparison without the shape check recorded", and a country
            # progress report no longer makes a period comparison: the indicator frame replaced
            # the diff of two dated positions the check was guarding, so requiring the line here
            # would fail every country over the absence of a guard on something it no longer
            # does. The region still compares positions across a window and still records it.
            if profile(unit)["sections"] and "Shape check" not in text:
                bad.append(f"{fn}: no shape check — §7 requires it before any period comparison")
            p = re.search(r"^period: \d{4}-\d{2}-\d{2} to (\d{4}-\d{2}-\d{2})", text, re.M)
            if p:
                lag = (datetime.date.fromisoformat(p.group(1))
                       - datetime.date.fromisoformat(newest)).days
    for line in bad:
        print("     ", line)
    if lag and lag > 0:
        print(f"      note: the progress window closes {lag} day(s) after the newest source on "
              f"this ledger — a true window over a quiet tail, disclosed not judged")
    print(f"check J: {'PASS' if not bad else 'FAIL — ' + str(len(bad)) + ' problem(s)'}")
    return 1 if bad else 0


def check_sourced(unit):
    """Check M — **every piece of evidence has a source** *(Bill, 2026-08-14)*.

    This is not a lint on the ledger, it is the rule the layer rests on, enforced. A row states a
    position; a position with nothing behind it is not evidence, and the base publishes nothing it
    cannot show the reader where it got.

    ***Not held*** is the single exemption, and it is not really one: the marker's whole meaning is
    that the base holds no position, so there is nothing to cite and the row carries no link for
    exactly that reason. Everything else is in scope, **measures included** — a figure is evidence
    like any other claim, and a `kind: measure` row is skipped by check I only because it has no
    status to check against a vocabulary, not because it may float free of a source.

    What made this reachable is that the gap was invisible to the other two. Check I asks whether a
    status is *inside* the closed vocabulary, and an unsourced `Implemented` is. Check G asks
    whether the links a document *carries* are held in `index/`, and a row with no source produces
    no link, so it passes by contributing nothing to the test. The result renders as a bare status
    with no hyperlink — indistinguishable from ***Not held***, while asserting its opposite, which
    is the one confusion the marker exists to prevent.

    **A source has to resolve, not merely be typed** *(Bill, 2026-08-14)*. Testing the field for
    emptiness was the same mistake one level down: on 2026-08-14 this passed a row citing
    `…mwango-brain-brain-base-nacional-dados`, a slug with a doubled word that the base does not
    hold, and the row rendered exactly as an unsourced one would — no link for check G to test, a
    populated `sources` field for this check to be satisfied by. So each slug must be a source the
    base actually holds, and at least one must carry a URL a reader can follow. The two failures
    are reported apart because they belong to different people: a slug the base does not hold is a
    mistake in the ledger, while a slug held without a `url:` is an uncitable record and OSINT's to
    fix (§8)."""
    _, ledger, _ = load(unit)
    urls, held = slug_urls(), raw_slugs()
    bad = []
    for r in ledger:
        if stem(r["status"]) == NOT_HELD:
            continue
        what = stem(r["status"]) or r.get("kind") or "row"
        cited = [s.strip().strip("[]") for s in (r.get("sources") or "").split("|") if s.strip()]
        if not cited:
            bad.append(f"{r['row_id']}: {what} with no source — {r['name']}")
            continue
        for s in cited:
            if s not in held:
                bad.append(f"{r['row_id']}: cites {s!r}, which the base does not hold — "
                           f"a mistyped or retired slug, not a source")
        if not any(s in urls for s in cited):
            bad.append(f"{r['row_id']}: states {what!r} with no cited source carrying a URL, so "
                       f"it publishes a claim a reader cannot follow — {r['name']}")
    for line in bad:
        print("     ", line)
    print(f"check M: {'PASS' if not bad else 'FAIL — ' + str(len(bad)) + ' problem(s)'}")
    return 1 if bad else 0


def check_indicators(unit):
    """Check I's indicator half — the frame's own closed set, and what is decidable about it.

    **What is testable here is narrower than the vocabulary** *(`progress-report-redesign.md`
    §3)*. Exactly one boundary in the Progress vocabulary is machine-decidable — *No evidence*
    means the base holds nothing on this indicator, which is the same statement as *no ledger row
    maps to it*, and that is checkable in both directions. The other five are the drafter's
    judgement and always will be: a row published inside the window can restate a standing
    position, so "something was published" does not separate *Advanced* from *No change*, and no
    amount of machinery will make it. What a check can do for those is test that the value is in
    the set, that *Mixed* carries the clause §3 makes mandatory, and that every id and every
    mapped row actually exists.

    So the rules are:

    - the value is in `PROGRESS`, testing the stem;
    - *No evidence* iff no row maps to the indicator — **both directions**, because the two
      failures are different mistakes. A No evidence row with rows mapped to it means the drafter
      did not look at evidence the base holds. A non-No-evidence row with nothing mapped means a
      claim resting on nothing at all, which is check M's rule one level up;
    - *Mixed* carries a qualifying clause naming which way each instrument moved;
    - every `indicator_id` is in the frame, and appears once;
    - every mapped `row_id` is on this unit's ledger.
    """
    if profile(unit)["sections"]:
        return 0                        # a region issues the movement document, not the frame
    _, ledger, _ = load(unit)
    view = indicators_lib.load_unit(REPORTS, unit)
    if view is None:
        print("check I (indicators): SKIP — the mapping pass has not run for this unit")
        return 0
    frame = {r["indicator_id"]: r for r in indicators_lib.frame()}
    known = {r["row_id"] for r in ledger}
    bad = []
    seen = set()
    path = os.path.relpath(indicators_lib.unit_path(REPORTS, unit), ROOT)
    for iid, row in view.items():
        if iid not in frame:
            bad.append(f"{iid}: not an indicator the frame holds — the row renders nowhere")
            continue
        if iid in seen:
            bad.append(f"{iid}: named twice in {path}")
        seen.add(iid)
        value = (row.get("progress") or "").strip()
        if not value:
            bad.append(f"{iid}: no progress value — the frame prints a row for every indicator, "
                       f"so an empty one is a question left unanswered, not an absent row")
            continue
        if stem(value) not in PROGRESS:
            bad.append(f"{iid}: progress {value!r} is outside the vocabulary")
        mapped = indicators_lib.row_ids(row)
        for rid in mapped:
            if rid not in known:
                bad.append(f"{iid}: maps {rid!r}, which is not on this unit's ledger")
        if stem(value) == NO_EVIDENCE and mapped:
            bad.append(f"{iid}: No evidence, but {len(mapped)} ledger row(s) map to it — the "
                       f"base holds evidence this row says it does not")
        if stem(value) != NO_EVIDENCE and not mapped:
            bad.append(f"{iid}: states {stem(value)!r} with no ledger row mapped to it, so the "
                       f"claim rests on nothing the base holds")
        if stem(value) == MIXED and not (value.partition(",")[2] or "").strip():
            bad.append(f"{iid}: Mixed with no qualifying clause — §3 requires it to name which "
                       f"instruments moved which way")
    for line in bad:
        print("     ", line)
    print(f"check I (indicators): {'PASS' if not bad else 'FAIL — ' + str(len(bad)) + ' problem(s)'}")
    return 1 if bad else 0


def check_indicator_prose(unit):
    """Check L's indicator half — no indicator asserts something and then says nothing.

    The check-L equivalent `progress-report-redesign.md` §5 specifies: **an indicator whose
    Progress is anything but No evidence and whose Developments is empty fails**. It is the same
    rule as the narrative one it replaces — a section published with nothing said about it — moved
    down to the row, which is where the prose now lives.

    The converse is checked too, and it is not symmetry for its own sake: a No evidence row
    carrying prose is a row whose value and whose text disagree, and the value is the one a reader
    scanning the Progress column will believe.

    Both texts are required where either is. The terse summary is what the table shows and the
    full record is what the expander holds; a row with a summary and no record has an expander
    that opens on nothing, and a row with a record and no summary is blank in the only column most
    readers will read.
    """
    if profile(unit)["sections"]:
        return 0
    view = indicators_lib.load_unit(REPORTS, unit)
    if view is None:
        print("check L (indicators): SKIP — the mapping pass has not run for this unit")
        return 0
    bad = []
    for iid in sorted(view):
        row = view[iid]
        value = stem((row.get("progress") or "").strip() or NO_EVIDENCE)
        summary = (row.get("summary") or "").strip()
        full = (row.get("developments") or "").strip()
        if value == NO_EVIDENCE:
            if summary or full:
                bad.append(f"{iid}: No evidence, but carries prose — the value says the base "
                           f"holds nothing and the text says otherwise")
            continue
        if not summary:
            bad.append(f"{iid}: {value}, with no summary — the table's Developments cell would "
                       f"print empty beside a stated position")
        if not full:
            bad.append(f"{iid}: {value}, with no developments — the row's expander would open "
                       f"on nothing")
    for line in bad:
        print("     ", line)
    print(f"check L (indicators): "
          f"{'PASS' if not bad else 'FAIL — ' + str(len(bad)) + ' unwritten row(s)'}")
    return 1 if bad else 0


def check_indicator_sources(unit):
    """Check M's indicator half — every claim in the drafted prose cites a source the base holds.

    Check M's rule is *every piece of evidence has a source*, and indicator prose is evidence: it
    is the part of the progress report a reader actually reads. The same two failures are reported
    apart here for the same reason they are on the ledger — a slug the base does not hold is a
    mistake in the prose, while a slug held without a `url:` is an uncitable record and OSINT's to
    fix.

    **A raw URL is refused rather than resolved** *(`progress-report-redesign.md` §2)*. The prose
    cites the base by slug and the renderer resolves it, so an `http://` written directly into
    `indicators.csv` is a claim pinned to an address the catalogue cannot correct and may not even
    hold — indistinguishable, once rendered, from a citation that went through the base.

    A stated position with no citation at all is not caught here: it is caught by check I, which
    requires a mapped ledger row behind every value that is not No evidence, and by check L, which
    requires the prose to exist. This asks only that what the prose *does* cite is real.
    """
    if profile(unit)["sections"]:
        return 0
    view = indicators_lib.load_unit(REPORTS, unit)
    if view is None:
        print("check M (indicators): SKIP — the mapping pass has not run for this unit")
        return 0
    urls, held = slug_urls(), raw_slugs()
    bad = []
    for iid in sorted(view):
        row = view[iid]
        for field in ("summary", "developments"):
            for m in SLUG_CITE.finditer(row.get(field) or ""):
                target = m.group(2)
                if target.startswith(("http://", "https://")):
                    bad.append(f"{iid}/{field}: cites the URL {target!r} directly — this prose "
                               f"cites the base by slug and the renderer resolves it")
                elif target not in held:
                    bad.append(f"{iid}/{field}: cites {target!r}, which the base does not hold — "
                               f"a mistyped or retired slug, not a source")
                elif target not in urls:
                    bad.append(f"{iid}/{field}: cites {target!r}, which the base holds without a "
                               f"URL — an uncitable record, and OSINT's to fix")
    for line in bad:
        print("     ", line)
    print(f"check M (indicators): "
          f"{'PASS' if not bad else 'FAIL — ' + str(len(bad)) + ' problem(s)'}")
    return 1 if bad else 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", required=True)
    ap.add_argument("--links", action="store_true")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--doc", choices=("status", "monthly", "progress", "all"), default="status")
    ap.add_argument("--month", help="YYYY-MM (default: the last closed month)")
    ap.add_argument("--end", metavar="YYYY-MM-DD",
                    help="select against this date instead of today. A document whose content "
                         "does not change keeps the window it already prints, whatever is passed "
                         "here")
    ap.add_argument("--window", type=int, default=12, help="months in the progress window")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--today")
    args = ap.parse_args()
    unit = args.unit.upper()
    # Slugs, URLs and the em dash below are not cp1252 — a Windows console kills the run on
    # the first Arabic URL otherwise, which is a reporting failure, not a rendering one.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    if args.links:
        urls = slug_urls()
        rows = read_csv(os.path.join(REPORTS, unit, "ledger.csv"))
        for s in ledger_slugs(rows):
            print(f"{s}\t{urls.get(s, 'UNRESOLVED — do not cite')}")
        return 0
    rc = 0
    if args.render:
        today = args.today or datetime.date.today().isoformat()
        month = args.month or last_closed_month(today)
        docs, why = issues(unit)
        # `--doc all` means all of this unit's documents. A region issues a monthly update and a
        # progress report, never a status; an initialised country no longer issues a rendered
        # status report either. Naming a document a unit does not issue is refused rather than
        # rendered — the caller that asked for it (REPORT-MONTHLY over every initialised unit) is
        # right to ask.
        want = docs if args.doc == "all" else (args.doc,)
        for skipped in [d for d in want if d not in docs]:
            print(f"{unit}: no {skipped} report — {why}")
        if "status" in want and "status" in docs:
            rc |= render(unit, today)
        if "monthly" in want and "monthly" in docs:
            rc |= render_monthly(unit, today, month, args.end)
        if "progress" in want and "progress" in docs:
            rc |= render_progress(unit, today, month, args.window, args.end)
    if args.check:
        rc |= check(unit)
    if not (args.render or args.check):
        ap.print_help()
    return rc


if __name__ == "__main__":
    sys.exit(main())
