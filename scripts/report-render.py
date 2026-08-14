#!/usr/bin/env python3
"""
report-render.py — standing. Renders a report from its ledger (`documentation/report-layer.md` §5).

**The script owns everything outside the narrative markers; the model owns everything inside
them.** A render rebuilds the front matter, the section tables and the gaps table from
`outputs/reports/{unit}/ledger.csv` and `gaps.csv`, and **carries every existing
`<!-- narrative: key -->` block across untouched**. That is what makes a format change cost a
render rather than a redraft.

**Three documents, one ledger** (`documentation/report-layer.md` §1). *Status* renders the current rows,
*monthly* renders the rows whose `published` falls in the window, *progress* compares each row's
`position_start` against its `position_end` over a window (twelve months by default). All three are derived from the same file by
slicing it, so the second and third cost a render rather than a second reading of the base — which
is the whole reason the run issues all three at initialisation.

**Both windows close on the day the document last changed, not on the month's last day and not on
the day the build ran** (§2). The base is swept nightly and that is what these reports are for; a
monthly covering July that stopped at 31 July would hold the first days of August back for a
month. There are no issues: each unit has one monthly and one progress report, living documents
whose windows slide. **Selection always runs to today** — a record published this morning is in
scope — but a build that finds nothing new to say leaves the document, and the window it prints,
exactly where they were *(Bill, 2026-08-14)*. `period:` is therefore the window the document
draws on, `compiled:` the day it last changed, and the two always agree.

**One renderer, a profile per process.** A country unit reads `lookups/report-country-sections.csv`
and issues all three documents; an `X__` region unit reads `lookups/report-region-sections.csv`,
calls its objects bodies rather than systems, and issues **the progress report only**
(`REPORT-REGION.md`). Everything else — the ledger, the markers, the windows, the checks — is the
same code on the same schema.

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
              that states a position cites a source. Exits non-zero on a miss. A report that
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
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault_lib  # noqa: E402

ROOT = vault_lib.ROOT
REPORTS = os.path.join(ROOT, "outputs", "reports")
COUNTRIES_CSV = os.path.join(ROOT, "lookups", "countries.csv")

# **One renderer, one profile per report process** (`documentation/report-layer.md` §5). What differs
# between a country report and a region one is its section map, what its object column is called,
# and which of the three documents it issues — not the rendering. A region issues the **progress
# report only** for now (`REPORT-REGION.md`); asking for the other two is refused here rather
# than branched around by every caller, so `REPORT-MONTHLY.md` runs over every initialised unit
# and a region yields its one document.
PROFILES = {
    "country": {"sections": "report-country-sections.csv",
                "object": "System or instrument", "objects": "systems and instruments",
                "docs": ("status", "monthly", "progress"),
                "sections_note": "Sections follow the status report."},
    "region": {"sections": "report-region-sections.csv",
               "object": "Body, instrument or system", "objects": "bodies, instruments and systems",
               "docs": ("progress",),
               "sections_note": "Sections run from the region's institutions outwards to what "
                                "funds them."},
}


def profile(unit):
    return PROFILES["region" if unit.startswith("X") else "country"]

NOT_HELD = "Not held"
BASELINE_NOT_HELD = "Baseline not held"
NO_CHANGE = "No change"
MARKER = re.compile(r"<!-- narrative: ([a-z0-9-]+) -->\n(.*?)\n<!-- /narrative -->", re.S)

# The two vocabularies, documentation/report-layer.md §3. They are STEMS: a value may be followed by a
# comma and a qualifying clause ("Implemented, under appeal"), and check I tests the stem.
STATUSES = ("Implemented", "Piloting", "In development", "Planned", "Discontinued", "Enacted",
            "Under review", NOT_HELD)
MOVEMENTS = ("Advanced", "Stalled", "Regressed", "Closed", NO_CHANGE, BASELINE_NOT_HELD)


def stem(value):
    """The part of a status or movement value before its qualifying clause."""
    return (value or "").split(",")[0].strip()

VOCAB = ("**Status values.** *Implemented* — in operation or in force. *Piloting* — running with a "
         "limited user group or in a controlled environment. *In development* — build or drafting "
         "under way, not yet operating. *Planned* — announced or provided for, no build or draft on "
         "record. *Enacted* — an instrument passed into law; pair with a qualifying clause for its "
         "in-force date. *Under review* — a law or policy currently being reconsidered. "
         "*Discontinued* — closed or superseded. ***Not held*** — the base carries no "
         "reliable statement of status; these are the gaps to fill and are listed again at the end.")

MOVE_VOCAB = ("**Movement values.** *Advanced* — a system entered service, a stage was completed or "
              "an instrument was made. *Stalled* — a stated target passed without delivery. "
              "*Regressed* — an instrument was withdrawn or neutralised, or a measured position "
              "worsened. *Closed* — the programme ended. *No change* — the position at both ends is "
              "the same. ***Baseline not held*** — the base carries no position at the start of the "
              "period, so no movement can be stated. A value may carry a qualifying clause after a "
              "comma, as in *Advanced, slipped*.")


def sections(unit):
    """[(order, section, key)] in document order, and {subject: (section, key)}."""
    by_key, subj = {}, {}
    path = os.path.join(ROOT, "lookups", profile(unit)["sections"])
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            by_key[r["section_key"]] = (int(r["section_order"]), r["section"])
            subj[r["subject"]] = (r["section"], r["section_key"])
    ordered = [(o, s, k) for k, (o, s) in by_key.items()]
    return sorted(ordered), subj


_TAXONOMY = None


def taxonomy():
    """(order, label, l1_of), cached — `vault_lib.load_taxonomy()`, one parse per run."""
    global _TAXONOMY
    if _TAXONOMY is None:
        _TAXONOMY = vault_lib.load_taxonomy()
    return _TAXONOMY


def by_subject(rows):
    """[(subject, [rows])], grouped and ordered by taxonomy Level-1/Level-2 (§1, §5).

    A subject with no rows is simply absent from the result — which is what keeps an
    empty subject from printing a sub-heading with nothing under it in either a table
    section (status, progress) or a narrative one (monthly)."""
    order, _, _ = taxonomy()
    groups = collections.defaultdict(list)
    for r in rows:
        groups[(r.get("subject") or "").strip()].append(r)
    return sorted(groups.items(), key=lambda kv: order.get(kv[0], (99, 99)))


def resort_ledger(path):
    """Reorders `ledger.csv` in place by taxonomy Level-1/Level-2, then name — item 1 of
    the 2026-08-10 report-structure change. A row's position in the file should follow
    the taxonomy, not the order a run happened to add it in. Content, `row_id`s and the
    file's column order are untouched; only row order moves, and only when it would
    actually change — a no-op ledger is not rewritten, so this never manufactures a diff
    on a file that is already sorted."""
    if not os.path.exists(path):
        return False
    order, _, _ = taxonomy()
    with open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        rows = [r for r in reader if not vault_lib.blank_csv_row(r)]
    if not rows:
        return False
    key = lambda r: (order.get((r.get("subject") or "").strip(), (99, 99)), (r.get("name") or "").lower())
    resorted = sorted(rows, key=key)
    if resorted == rows:
        return False
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\r\n")
        w.writeheader()
        w.writerows(resorted)
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


def slug_urls():
    """slug -> url for every source in the vault, from the index.

    **An index holding nothing is refused, not read.** It is the one failure here that is worse
    than a crash: `row_url()` finds no resolvable slug, `cite()` falls back to plain text, and the
    render strips the hyperlink off every status cell in every document while reporting a normal
    build — and check G then *passes*, because a document with no links left has none missing.
    The check that exists to catch broken citations certifies the run that removed them all.

    Zero artefacts is never a legitimate reading of this base. It means `ROOT` is not where the
    base is — a script run from the repo root rather than from `scripts/.workroot/`, which indexes
    a tree containing none of `raw/`, `wiki/` or the rest. That index then reports itself *fresh*,
    because zero files on disk agrees with zero files in `meta.json`, so nothing rebuilds it and
    nothing says a word."""
    rows = vault_lib.load_index()
    if not rows:
        raise vault_lib.EmptyIndex(
            f"{vault_lib.INDEX_DIR} holds no artefacts — refusing to render or check against it, "
            f"because every citation would be silently dropped and check G would pass with no "
            f"links left to check. Run from scripts/.workroot/, where raw/ and index/ resolve to "
            f"OSINT through the junctions rebuild.py sets up.")
    out = {}
    for r in rows:
        d, fm = r.get("d") or {}, r.get("fm") or {}
        if d.get("folder") != "raw":
            continue
        url = (fm.get("url") or "").strip()
        slug = d.get("slug") or os.path.basename(r["path"])[:-3]
        if url:
            out[slug] = url
    return out


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
    hist = source_months(unit, vault_lib.load_index())
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


def front(title, today, unit, ledger_rows, not_held, period=None):
    fm = ["---", f"title: {title}", f"compiled: {today}"]
    if period:
        fm.append(f"period: {period}")
    fm += [f"place: {unit}", f"ledger_rows: {ledger_rows}", f"not_held: {not_held}",
           # The content digest `compiled:` is judged against — see write(). Filled in on write,
           # because it is a hash of the finished document.
           PENDING, "---", ""]
    return fm


def blocker(path):
    """Carry every existing narrative block across by marker id; mint empty ones for the rest.

    **An unwritten block is emitted empty, never with placeholder text** *(Bill, 2026-08-14)*.
    The renderer previously minted `_(narrative not yet written)_`, which is readable prose in a
    document a reader may download — a note-to-self that had escaped into the deliverable. An
    empty marker pair says the same thing to a drafter and to `--check`, and says nothing at all
    to a reader or to the PDF. The condition should not arise in the first place: BUILD does not
    release a document with an unwritten block (BUILD.md -> Narrative integrity), and `--check`
    counts them so BUILD can see what is left to write."""
    keep = existing_blocks(path)
    used = set()

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


def load(unit):
    folder = os.path.join(REPORTS, unit)
    ledger_path = os.path.join(folder, "ledger.csv")
    resort_ledger(ledger_path)
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
    folder, ledger, gaps = load(unit)
    if not ledger:
        print(f"{unit}: ledger is empty — nothing to render")
        return 1
    ordered, _ = sections(unit)
    # A measure moves but has no current state to inventory (§1), so the status report omits it.
    ledger = [r for r in ledger if (r.get("kind") or "instrument") != "measure"]
    path = os.path.join(folder, f"{unit}-status.md")
    block, keep, dropped = blocker(path)
    not_held = sum(1 for r in ledger if r["status"] == NOT_HELD)
    name = place_name(unit)
    out = front(f"{name} — digital transformation and data governance status report",
                today, unit, len(ledger), not_held) + [
        f"# {name}: status report",
        "",
        f"*Compiled {today} from the Data Landscapers source base, from `outputs/reports/{unit}/ledger.csv` "
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
    _, tax_label, _ = taxonomy()
    for _, section, key in ordered:
        rows = [r for r in ledger if r["section"] == section]
        out += ["", f"## {section}", ""]
        if rows:
            for subject, srows in by_subject(rows):
                out += [f"### {tax_label.get(subject, subject)}", "", status_table(srows, urls), ""]
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
    ordered, _ = sections(unit)
    block, keep, dropped = blocker(path)
    not_held = sum(1 for r in ledger if stem(r["status"]) == NOT_HELD)
    name = place_name(unit)
    pretty = datetime.date.fromisoformat(start).strftime("%B %Y")
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
        f"*Developments recorded from artefacts published between {start} and {CLOSE} — {pretty} "
        f"carried forward to the date of issue, so the report holds the nightly catch to the day "
        f"it was cut. Sections follow the status report.*",
        "",
        "## Summary of the month",
        "",
        block("summary"),
    ]
    _, tax_label, _ = taxonomy()
    for _, section, key in ordered:
        srows = [r for r in changed if r["section"] == section]
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
            out += [f"### {tax_label.get(subject, subject)}", "", block(subkey)]
    out.append("")
    return write(path, out, unit, f"{len(changed)} row(s) in {start} to {end}, "
                 f"{note_drop(dropped, unit)}", today, end)


def render_progress(unit, today, month, window, end=None):
    """Progress — the movement ledger over a window, prior_* against current.

    It is the only one of the three that can honestly say nothing changed, and it must be willing
    to. A ***Not held*** row has no position at either end, so it is counted rather than tabled."""
    folder, ledger, gaps = load(unit)
    if not ledger:
        print(f"{unit}: ledger is empty — nothing to render")
        return 1
    ordered, _ = sections(unit)
    prof = profile(unit)
    urls = slug_urls()
    path = os.path.join(folder, f"{unit}-progress.md")
    start, end = month_bounds(month, window, end or today)
    block, keep, dropped = blocker(path)
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
    out = front(f"{name} — progress report, {start} to {CLOSE}", today, unit, len(ledger), not_held,
                period=f"{start} to {CLOSE}") + [
        f"# {name}: progress report, {start} to {CLOSE}",
        "",
        f"*Compiled {today} from the Data Landscapers source base. {prof['sections_note']} Each "
        f"opens with a movement ledger comparing the position at the start and end of the period, "
        f"which runs to the date of issue rather than to the last month's close.*",
        "",
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
    _, tax_label, _ = taxonomy()
    # Movement first within a subject group: an unchanged row is reference matter, a moved
    # one is the report.
    rank = {NO_CHANGE: 2, BASELINE_NOT_HELD: 3}
    for _, section, key in ordered:
        rows = [r for r in held if r["section"] == section]
        # A section with no rows at either end of the window is not printed *(Bill, 2026-08-14)* —
        # see the note in render_monthly. Only the status report states an absence.
        if not rows:
            continue
        out += ["", f"## {section}", ""]
        for subject, srows in by_subject(rows):
            out += [f"### {tax_label.get(subject, subject)}", "",
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


def check(unit):
    """Check G — every URL in the rendered documents is held in index/ — and check I."""
    held = set(slug_urls().values())
    held |= {link_target(u) for u in held}
    bad = 0
    folder = os.path.join(REPORTS, unit)
    for fn in sorted(os.listdir(folder)):
        if not fn.endswith(".md"):
            continue
        text = open(os.path.join(folder, fn), encoding="utf-8").read()
        urls = set(re.findall(r"\]\((https?://[^)\s]+)\)", text))
        miss = [u for u in urls if u not in held]
        print(f"  {fn}: {len(urls)} links, {len(miss)} NOT HELD")
        for u in miss:
            print("     NOT HELD:", u)
        bad += len(miss)
    print(f"check G: {'PASS' if not bad else 'FAIL — ' + str(bad) + ' link(s) not in index/'}")
    return ((1 if bad else 0) | check_vocab(unit) | check_asof(unit)
            | check_narrative(unit) | check_sourced(unit))


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
    for fn in sorted(os.listdir(folder)):
        if not fn.endswith(".md"):
            continue
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
    # A row whose `section` is not one this unit's map names renders nowhere at all — the section
    # loop filters on equality, so a typo silently deletes the row from the document rather than
    # failing. The region map made this reachable: two processes, two sets of section names.
    known = {s for _, s, _ in sections(unit)[0]}
    for r in ledger:
        if (r.get("section") or "").strip() not in known:
            bad.append(f"{r['row_id']}: section {r.get('section')!r} is not in this unit's section "
                       f"map — the row would render in no section")
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
    checked here too. `render_progress()` emits it unconditionally, so this asserts that it stayed."""
    folder, ledger, _ = load(unit)
    pubs = [(r.get("published") or "").strip() for r in ledger]
    newest = max([p for p in pubs if p] or [""])
    if not newest:
        print("check J: PASS (no dated source on this ledger)")
        return 0
    bad, lag = [], None
    for fn in sorted(os.listdir(folder)):
        if not fn.endswith(".md"):
            continue
        text = open(os.path.join(folder, fn), encoding="utf-8").read()
        m = re.search(r"^compiled:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
        if m and m.group(1) < newest:
            bad.append(f"{fn}: compiled {m.group(1)}, but the ledger cites a source published "
                       f"{newest} — the document does not yet show it, re-render")
        if fn.endswith("-progress.md"):
            if "Shape check" not in text:
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
    is the one confusion the marker exists to prevent."""
    _, ledger, _ = load(unit)
    bad = [f"{r['row_id']}: {stem(r['status']) or r.get('kind') or 'row'} with no source — "
           f"{r['name']}"
           for r in ledger
           if stem(r["status"]) != NOT_HELD and not (r.get("sources") or "").strip()]
    for line in bad:
        print("     ", line)
    print(f"check M: {'PASS' if not bad else 'FAIL — ' + str(len(bad)) + ' unsourced row(s)'}")
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
        docs = profile(unit)["docs"]
        # `--doc all` means all of this unit's documents. A region issues the progress report
        # only, and naming one it does not issue is refused rather than rendered empty — the
        # caller that asked for it (REPORT-MONTHLY over every initialised unit) is right to ask.
        want = docs if args.doc == "all" else (args.doc,)
        for skipped in [d for d in want if d not in docs]:
            print(f"{unit}: no {skipped} report — this unit issues "
                  f"{', '.join(docs)} only (REPORT-REGION.md)")
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
