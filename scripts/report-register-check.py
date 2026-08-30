#!/usr/bin/env python3
"""
report-register-check.py — standing. Verifies report prose against the register
(`documentation/report-layer.md` → *Corpus editorial register*, and
`documentation/report-layer.md` §10 for the boundary it does not move) and the word budget
(`documentation/report-country-skeleton.md`).

**It verifies and never repairs**, the same rule `REPORT-LINT.md` holds to. A hit is not
automatically a defect — a quoted source may legitimately contain a banned term, and a
report that quotes an agency calling something an "attack surface" is doing exactly what
the register asks. The script reports; a person rules.

**Drafted prose only.** Everything outside it belongs to the renderer, and a ledger `name` is
the object's name rather than the report's prose — *Attack surface of the online service estate*
is a system this base carries, and flagging it would be flagging the world rather than the
writing. URLs are masked before matching so a slug containing `unlock` is not a register hit.

**Drafted prose lives in two places now** *(2026-08-26)*. The status report, the monthly and a
region's progress report keep it in `<!-- narrative: key -->` markers inside the document. A
**country's** progress report keeps it in `outputs/reports/{unit}/indicators.csv`, two columns
per indicator (`progress-report-redesign.md` §5), and that file is read here too — it is the
longest body of prose the site publishes and a check that saw only the markers would have
stopped seeing all of it. Its budget is per indicator rather than per document, for the reason
the country skeleton gives: how many indicators carry prose is a fact about the base, not about
the writing.

The changeover needs no flag day and gets none. A country progress report that still carries
markers has not been re-rendered yet, so it is still what the site publishes and is still
checked as a document — minus the whole-document band, which stopped applying to it. One that
carries none has moved, and is checked through its `indicators.csv` instead.

The budget is read from the skeleton rather than duplicated here, because the skeleton is
the knob: change the numbers there and this follows. If its line is reworded past the
pattern below, this exits 2 rather than silently checking nothing.

Usage:
  python scripts/report-register-check.py                 # every unit
  python scripts/report-register-check.py --unit BEN
  python scripts/report-register-check.py --terms         # print what it looks for
"""
import argparse
import csv
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault_lib  # noqa: E402

ROOT = vault_lib.ROOT
REPORTS = os.path.join(ROOT, "outputs", "reports")
# One skeleton per report process, and the budget is read from it rather than duplicated here —
# the skeleton is the knob. A region unit is an `X__` code (`REPORT-REGION.md`).
SKELETONS = {"country": os.path.join(ROOT, "documentation", "report-country-skeleton.md"),
             "region": os.path.join(ROOT, "documentation", "report-region-skeleton.md")}

MARKER = re.compile(r"<!-- narrative: ([a-z0-9-]+) -->\n(.*?)\n<!-- /narrative -->", re.S)
LINK = re.compile(r"\]\((?:[^()]|\([^()]*\))*\)")
"""A link target to blank. **It admits spaces and balanced parentheses**, because the
indicator prose cites the base by catalogue slug and this base's slugs are record titles —
`2025-11-08 Digital 2026 Eritrea (DataReportal)` and 363 others carry a bracketed qualifier.
A pattern refusing spaces leaves the slug's own words in the masked block, where the register
then reads a source's title as the drafter's prose and charges its clichés to the writer."""

# §10, grouped so the report tells a writer which rule they are against rather than which
# word they used. Each entry is (label, [regex, ...], ignore_case).
#
# **The jargon group is case-SENSITIVE, and that is the rule it encodes**: these terms are
# barred as the report's own words, not as other people's names. "Payments Ecosystem
# Modernisation" is what a programme is called; flagging it would be flagging the world
# rather than the writing, and a check that does that stops being read.
TERMS = [
    ("first person", [r"\bwe\b", r"\bour\b", r"\bours\b"], True),
    ("tic", [r"binding constraint", r"counter-example", r"the real question",
             r"it is worth noting", r"what it does not contain", r"turns? out to be",
             r"is really about", r"the uncomfortable"], True),
    ("flash verb", [r"\blanded\b", r"\bunveil(ed|s|ing)?\b", r"rolled out", r"ramp(ed|ing) up",
                    r"doubl(ed|ing) down", r"poised to", r"sets? the stage", r"paves? the way",
                    r"marks? a turning point"], True),
    ("jargon", [r"demateriali[sz]", r"dématériali", r"attack surface", r"ecosystem",
                r"\bunlock(s|ed|ing)?\b", r"leapfrog", r"at scale", r"citizen journey",
                r"low-hanging"], False),
]
# Case-sensitive, and that is the whole point: `US$40m` and the United States are not the
# first-person plural, and a check that flags them every time teaches a reader to skip it.
FIRST_PERSON = re.compile(r"(?<![\w'’])(I|us)(?![\w'’])")


BUDGET_LINE = re.compile(r"([\d,]+)\s*[–-]\s*([\d,]+)(?: words)? for an? (status|monthly|progress)")


def budgets(kind="country"):
    """{doc kind: (low, high)} read from that process's skeleton, which is the knob.

    The pattern reads each `N–M for a {doc}` pair independently, so a skeleton may name one
    document (a region, which issues the progress report only) or three."""
    path = SKELETONS[kind]
    found = {m.group(3): (int(m.group(1).replace(",", "")), int(m.group(2).replace(",", "")))
             for m in BUDGET_LINE.finditer(open(path, encoding="utf-8").read())}
    if not found:
        print(f"FATAL: the word-budget line in {os.path.relpath(path, ROOT)} no longer matches the "
              "pattern this script reads. Fix one or the other — a check that silently stops "
              "checking is worse than no check.", file=sys.stderr)
        sys.exit(2)
    return found


def mask_urls(text):
    """Blank every link target, preserving offsets so line numbers stay true."""
    return LINK.sub(lambda m: " " * len(m.group(0)), text)


ANCHOR = re.compile(r"\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\)")
"""`[label](target)` reduced to its label for the word count, on `LINK`'s pattern and for its
reason. A slug citation left unmatched would charge the drafter every word of a source's title
— eight or ten of them on the 8–40 band an indicator summary is held to."""


def prose_spans(text):
    """[(start_offset, masked_block, countable_block)] for the narrative blocks.

    Two renderings of the same prose, because the two jobs need different things. The **masked**
    one blanks each link target in place, so a register hit's line number is still true. The
    **countable** one reduces `[text](url)` to `text`, which is the method the skeletons document
    — and it is not the same as counting the masked one, because masking leaves the trailing
    punctuation stranded as its own token. That difference is small and it points the wrong way:
    it charges a document a word every time a sentence gains the citation `report-layer.md` §5
    requires it to carry."""
    return [(m.start(2), mask_urls(m.group(2)), ANCHOR.sub(r"\1", m.group(2)), m.group(2))
            for m in MARKER.finditer(text)]


FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)
NOT_PROSE = re.compile(r"\A\s*(?:#|\||>|<!--|```|-{3,}\s*\Z|[-*+]\s|\d+[.)]\s)")


def body_spans(text):
    """`prose_spans()` for a document whose prose is the body itself, not a marked block.

    An initialised unit's status report is authored by hand and carries no `<!-- narrative -->`
    markers, so `prose_spans()` returns nothing for it — and a register check that reads nothing
    printed `0 register hit(s)` over 40 published documents, which is indistinguishable from
    having checked them. Paragraphs are the unit: a run of lines that is not frontmatter, a
    heading, a table row, a list item, a blockquote, a fence or an HTML comment."""
    body = text[FRONTMATTER.match(text).end():] if FRONTMATTER.match(text) else text
    offset = len(text) - len(body)
    out, fenced = [], False
    for m in re.finditer(r"[^\n]*(?:\n|\Z)", body):
        line = m.group(0)
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or not line.strip() or NOT_PROSE.match(line):
            continue
        raw = line.rstrip("\n")
        out.append((offset + m.start(), mask_urls(raw), ANCHOR.sub(r"\1", raw), raw))
    return out


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def kind_of(path):
    name = os.path.basename(path)
    for k in ("status", "monthly", "progress"):
        if f"-{k}" in name:
            return k
    return None


CITED = re.compile(r"\]\(https?://")
FIGURE = re.compile(r"(?:US\$|R|EUR|£|\$)\s?\d[\d,.]*\s?(?:m|bn|billion|million)?"
                    r"|\b\d+(?:\.\d+)?\s?(?:%|per cent)"
                    r"|\b\d{1,3}(?:,\d{3})+\b"
                    r"|\b\d{4,}\b")
YEAR = re.compile(r"^(?:19|20)\d\d$")


def sentences(block):
    """`block` split into sentences, **never through the inside of a link label**.

    The split is on `.` and `;` followed by space, and a citation's label is prose. `[377,060
    identity numbers remained blocked ... unconstitutional; Home Affairs blames ...](url)` is one
    linked claim carrying a semicolon, and cutting it there left the figures in a fragment with no
    `](http` in it and the citation in the next one — check H then reported an uncited figure that
    sat inside its own citation, which is the false-positive rate `unprovenanced()`'s own docstring
    names as how a check stops being read. Fragments are rejoined until every `[` opened has closed.
    """
    out, buf = [], ""
    for part in re.split(r"(?<=[.;])\s+", (block or "").strip()):
        buf = f"{buf} {part}" if buf else part
        if buf.count("[") <= buf.count("]"):
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return out


def unprovenanced(block):
    """Check H — **a figure in narrative prose must have a source; it need not be in the ledger**
    *(Bill, 2026-08-14)*.

    This asks only **that a source exists**. It does not open the source, does not compare the
    figure against it, and does not ask which sentence the citation belongs to. Provenance, not
    fact-checking.

    **It replaces a rule that could not have worked.** §6 used to require that every figure and
    status word in a block appear in that section's ledger rows. That is an unscoped copy of a
    check OSINT ran and retired: `LINT.md` records the line-level money scan running "~90%
    false-positive" until it "stopped being read", and `REPORT-LINT.md`'s check E refuses the
    domestic block for the same reason, because "nearly every honest sentence in it holds a figure
    that sits in no single record cell". It also fought `report-layer.md` §2 — the build must never
    become a chronology, so a monthly's prose carries event detail that is deliberately *not* a
    ledger position, and the old rule made every such sentence a defect. Its own reference-study
    exemption already conceded the point: that figure was exempt precisely because it carries its
    own citation.

    OSINT's settled definition of provenance is the one used here — "a wikilink to a dated `raw/`
    slug or an inline URL" — and its scope rule is the one applied: check the prose that has no
    provenance machinery of its own. The tables have theirs, in checks M and G.

    **The sentence is the unit, not the block** *(Bill, 2026-08-14)*. It began as the block, on the
    ground that a block carrying citations is sourced prose. That was too loose: a paragraph whose
    opening sentence is linked does not source the three that follow it, and the failure clusters
    in summary blocks, which restate facts drafted elsewhere and leave their citations behind. Of
    the figures in cited blocks but uncited sentences, a third had no cited sentence anywhere near
    them — `Parliament approved a rectificative budget … at CVE 103,888 million` standing alone —
    and the rest were mostly new claims sheltering under the previous sentence's link rather than
    continuations of it.

    It still asks only **that a source exists for the sentence**, never that the figure matches
    what the source says. A sentence with no figure in it is not examined at all, so a statement of
    what the base does not hold, and the one connecting sentence the register allows, pass
    untouched."""
    out = []
    for s in sentences(block):
        if CITED.search(s):
            continue
        out += [f for f in dict.fromkeys(FIGURE.findall(s)) if not YEAR.match(f.strip())]
    return list(dict.fromkeys(out))


INDICATOR_LINE = re.compile(
    r"([\d,]+)\s*[–-]\s*([\d,]+)(?: words)? for an indicator (summary|developments)")


def indicator_budget():
    """`{field: (low, high)}` — the per-indicator bands, read from the country skeleton.

    **The progress report's prose is budgeted per indicator and not per document** *(the country
    skeleton, → *Word budget*, 2026-08-26)*. A whole-document band would fail a country for the
    state of the base rather than the state of its writing: five indicators carrying evidence and
    eighty are both correct, and no single number can hold both. Read from the skeleton for the
    same reason the document bands are — the skeleton is the knob, and a number duplicated here
    would be a second knob nobody turns.
    """
    path = SKELETONS["country"]
    found = {m.group(3): (int(m.group(1).replace(",", "")), int(m.group(2).replace(",", "")))
             for m in INDICATOR_LINE.finditer(open(path, encoding="utf-8").read())}
    missing = {"summary", "developments"} - set(found)
    if missing:
        print(f"FATAL: the per-indicator word-budget line in {os.path.relpath(path, ROOT)} no "
              f"longer names {', '.join(sorted(missing))}. Fix one or the other — a check that "
              f"silently stops checking is worse than no check.", file=sys.stderr)
        sys.exit(2)
    return found


# **Provenance in indicator prose is a slug, not a URL.** The narrative blocks cite the web
# directly and `CITED` tests for that; `indicators.csv` cites the base by catalogue slug and the
# renderer resolves it (`report-render.py` -> `cite_prose`). Testing the stored prose for
# `](https://` would therefore find no citation anywhere and report every figure in every
# indicator as unprovenanced — a check firing on all of its input, which is how a check stops
# being read. Check M is what tests that the slug is real; this only asks that one is there.
CITED_ANY = re.compile(r"\]\([^)]+\)")


def unprovenanced_slug(block):
    """`unprovenanced()`'s rule — a figure needs a source in its own sentence — for slug prose."""
    out = []
    for s in sentences(block):
        if CITED_ANY.search(s):
            continue
        out += [f for f in dict.fromkeys(FIGURE.findall(s)) if not YEAR.match(f.strip())]
    return list(dict.fromkeys(out))


INDICATOR_FIELDS = ("summary", "developments")


def check_indicators_file(path, bands):
    """The register, the per-indicator budget and check H, over one unit's `indicators.csv`.

    **The country progress report's prose stopped living in the document it appears in**
    (`progress-report-redesign.md` §5), and a register check that reads only `<!-- narrative -->`
    markers stopped seeing any of it — while it became the longest body of prose the site
    publishes. This reads the two prose columns of `indicators.csv` instead. Same register, same
    check H, same rule that it verifies and never repairs.

    Line numbers are real ones, found by locating each `indicator_id` at the start of its row, so
    a hit is something an editor can open the file at rather than a row number to count to.

    Returns `(hits, rows_over_band, unprovenanced)` — the counts are per **cell**, not per
    document, because that is the unit the band is set in.
    """
    text = open(path, encoding="utf-8-sig").read()
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    hits, over, figs = [], [], []
    for r in rows:
        iid = (r.get("indicator_id") or "").strip()
        if not iid:
            continue
        m = re.search(r"^" + re.escape(iid) + r"[,\r\n]", text, re.M)
        line = line_of(text, m.start()) if m else 0
        for field in INDICATOR_FIELDS:
            raw = (r.get(field) or "").strip()
            if not raw:
                # An empty cell is check L's business, not the register's: it knows whether the
                # row is No evidence, where empty is correct, and this does not.
                continue
            block = mask_urls(raw)
            countable = ANCHOR.sub(r"\1", raw)
            words = len(re.sub(r"\[([^\]]*)\]", r"\1", countable).split())
            lo, hi = bands[field]
            if not lo <= words <= hi:
                over.append((line, iid, field, words, lo, hi))
            for label, patterns, icase in TERMS:
                for pat in patterns:
                    for mm in re.finditer(pat, block, re.I if icase else 0):
                        hits.append((line, f"{iid}/{field}", label, mm.group(0)))
            for mm in FIRST_PERSON.finditer(block):
                hits.append((line, f"{iid}/{field}", "first person", mm.group(0)))
            bare = unprovenanced_slug(raw)
            if bare:
                figs.append((line, f"{iid}/{field}", bare))
    return sorted(hits), sorted(over), sorted(figs)

DERIVED = "<!-- derived -->"


def derived_lines(text):
    """Line numbers of the paragraph a `<!-- derived -->` marker introduces.

    **A figure the report computed from its own tables carries no link by design**, and
    `status-check.py` has exempted these paragraphs since the baseline layer was written. Check H
    did not, because `body_spans()` drops HTML comments before the prose reaches it, so the marker
    was invisible here and the paragraph read as uncited narrative. Two checks over one document
    then disagreed about the same two paragraphs, and every run re-reported a hit the other check
    had already ruled exempt — which is how a check stops being read. The exemption is the
    marker's whole purpose; what was missing was its application here.
    """
    out = set()
    pat = re.compile("^" + re.escape(DERIVED) + r"[^\n]*\n((?:[^\n]+\n?)+)", re.M)
    for m in pat.finditer(text):
        first = text.count("\n", 0, m.start(1)) + 1
        out.update(range(first, first + len(m.group(1).rstrip("\n").split("\n"))))
    return out


def check_file(path, budget, authored=False):
    text = open(path, encoding="utf-8").read()
    spans = body_spans(text) if authored else prose_spans(text)
    exempt = derived_lines(text)
    hits, words, figs = [], 0, []
    for start, block, countable, raw in spans:
        words += len(re.sub(r"\[([^\]]*)\]", r"\1", countable).split())
        bare = unprovenanced(raw)
        if bare and line_of(text, start) not in exempt:
            figs.append((line_of(text, start), bare))
        for label, patterns, icase in TERMS:
            for pat in patterns:
                for m in re.finditer(pat, block, re.I if icase else 0):
                    hits.append((line_of(text, start + m.start()), label, m.group(0)))
        for m in FIRST_PERSON.finditer(block):
            hits.append((line_of(text, start + m.start()), "first person", m.group(0)))
    for m in re.finditer(r"^## Comment\s*$", text, re.M):
        hits.append((line_of(text, m.start()), "comment section",
                     "## Comment — removed from the layer 2026-08-04"))
    return sorted(hits), words, figs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", help="one ISO-3 / region / topic unit (default: all)")
    ap.add_argument("--terms", action="store_true", help="print the term list and exit")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    if args.terms:
        for label, patterns, icase in TERMS:
            case = "any case" if icase else "lower case only - a capital marks a proper name"
            print(f"{label} ({case}): {', '.join(patterns)}")
        print("first person: I, us (case-sensitive — US$ and the United States are not hits)")
        return 0

    budget = {k: budgets(k) for k in SKELETONS}
    bands = indicator_budget()

    # **`--unit all` used to match a unit literally named `all` and report a clean pass over nothing**
    # *(2026-08-20)*. It printed `register: 0 hit(s); budget: 0 document(s) outside band; check H: 0`
    # — indistinguishable from a genuinely clean corpus, and the default with no `--unit` at the time
    # reported 78 documents outside band. A check that reads nothing must never look like a check that
    # found nothing, so `all` is now the documented synonym for the default and an unknown unit is an
    # error rather than an empty sweep. `status-check.py` already took `all` this way; the two agree now.
    unit = (args.unit or "").strip().upper()
    if unit in ("", "ALL"):
        pattern = os.path.join(REPORTS, "*", "*.md")
    else:
        pattern = os.path.join(REPORTS, unit, "*.md")
        if not os.path.isdir(os.path.join(REPORTS, unit)):
            print(f"report-register-check: no unit {unit} under {REPORTS} — "
                  f"nothing was checked", file=sys.stderr)
            return 2

    flagged = over = uncited = 0
    # **A country's progress prose is in `indicators.csv`, so that is what gets checked**
    # *(2026-08-26)*. The document itself carries no narrative markers any more, so reading it
    # would score every country at nought words and report 54 documents under band — a check
    # loudly measuring a thing that moved. The regions are untouched: their progress report is
    # still the movement document and its prose is still in its markers.
    seen_units = []
    for path in sorted(glob.glob(pattern)):
        kind = kind_of(path)
        if not kind:
            continue
        unit = os.path.basename(os.path.dirname(path))
        region = unit.startswith("X")
        band_for = budget["region" if region else "country"]
        if not region and unit not in seen_units:
            seen_units.append(unit)
        # **A country's progress prose moved to `indicators.csv`, so the whole-document band no
        # longer applies to the document** — but the document does not vanish the moment the band
        # does. Until the mapping pass has run and the report been re-rendered, the old one is
        # still what the site publishes and its narrative blocks are still live prose. So the
        # band is dropped for it and the register and check H are not: skipping it outright
        # would leave 54 published documents and ~590k characters unchecked for the length of
        # the migration, which is exactly the window in which nobody would notice.
        legacy = kind == "progress" and not region
        if legacy and not MARKER.search(open(path, encoding="utf-8").read()):
            continue                             # re-rendered: its prose is in indicators.csv now
        # **An initialised unit's status report is authored, not rendered, and carries no
        # narrative markers** — `BUILD.md` → *Maintaining the status baseline*. Reading it for
        # marker words scored 40 of the 54 status reports at nought and reported each of them
        # 1,000 words under band, while every one of them held thousands of words of live prose:
        # the same defect this file already names for the progress document, in the one place a
        # deficit can never be true. The band is dropped for it; the register and check H are
        # not, because unlike the progress case the prose is in this document and nowhere else.
        authored = (kind == "status" and not region
                    and not MARKER.search(open(path, encoding="utf-8").read()))
        if not (legacy or authored) and kind not in band_for:  # not budgeted by the skeleton
            continue
        hits, words, figs = check_file(path, band_for, authored=authored)
        rel = os.path.relpath(path, ROOT)
        if legacy:
            # No band, and said so rather than printed as a clean nought.
            head = f"{rel}  {words} words (not budgeted — prose moves to indicators.csv)"
        elif authored:
            head = f"{rel}  (not budgeted — authored baseline, prose outside the markers)"
        else:
            lo, hi = band_for[kind]
            band = "" if lo <= words <= hi else (f"  OVER by {words - hi}" if words > hi
                                                 else f"  UNDER by {lo - words}")
            if band:
                over += 1
            head = f"{rel}  {words} words ({lo}-{hi}){band}"
        print(head + f"  {len(hits)} register hit(s)"
              + (f"  {len(figs)} uncited block(s)" if figs else ""))
        for line, label, text in hits:
            print(f"    {rel}:{line}  [{label}] {text}")
        for line, bare in figs:
            print(f"    {rel}:{line}  [check H] no citation in this block: {', '.join(bare)}")
        flagged += len(hits)
        uncited += len(figs)

    cells = missing = checked = 0
    for unit in seen_units:
        ipath = os.path.join(REPORTS, unit, "indicators.csv")
        if not os.path.exists(ipath):
            # Named, not skipped in silence. Until the mapping pass has run for a unit there is
            # no progress prose to check, and a run that says nothing about it is indistinguish-
            # able from one that checked it and found nothing — the `--unit all` mistake of
            # 2026-08-20, in a second place.
            missing += 1
            continue
        checked += 1
        hits, band, figs = check_indicators_file(ipath, bands)
        rel = os.path.relpath(ipath, ROOT)
        print(f"{rel}  {len(hits)} register hit(s)"
              + (f"  {len(band)} cell(s) outside band" if band else "")
              + (f"  {len(figs)} uncited cell(s)" if figs else ""))
        for line, where, label, txt in hits:
            print(f"    {rel}:{line}  [{label}] {where}: {txt}")
        for line, where, field, words, lo, hi in band:
            how = f"OVER by {words - hi}" if words > hi else f"UNDER by {lo - words}"
            print(f"    {rel}:{line}  [budget] {where}/{field}: {words} words ({lo}-{hi})  {how}")
        for line, where, bare in figs:
            print(f"    {rel}:{line}  [check H] no citation in this cell: {where}: "
                  f"{', '.join(bare)}")
        flagged += len(hits)
        cells += len(band)
        uncited += len(figs)

    print(f"\nregister: {flagged} hit(s) to rule on; budget: {over} document(s) outside band"
          + (f", {cells} indicator cell(s) outside band in {checked} file(s)" if checked else ""))
    print(f"check H: {uncited} block(s) or cell(s) carrying a figure with no source to follow")
    if missing:
        print(f"indicator prose: {missing} country unit(s) have no indicators.csv — the mapping "
              f"pass has not run for them, so their progress prose was not checked")
    return 1 if (flagged or over or cells) else 0


if __name__ == "__main__":
    sys.exit(main())
