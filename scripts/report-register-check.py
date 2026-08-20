#!/usr/bin/env python3
"""
report-register-check.py — standing. Verifies report prose against the register
(`documentation/migration-report-layer.md` → *Corpus editorial register*, and
`documentation/report-layer.md` §10 for the boundary it does not move) and the word budget
(`documentation/report-country-skeleton.md`).

**It verifies and never repairs**, the same rule `REPORT-LINT.md` holds to. A hit is not
automatically a defect — a quoted source may legitimately contain a banned term, and a
report that quotes an agency calling something an "attack surface" is doing exactly what
the register asks. The script reports; a person rules.

**Narrative blocks only.** Everything outside the markers belongs to the renderer, and a
ledger `name` is the object's name rather than the report's prose — *Attack surface of the
online service estate* is a system this base carries, and flagging it would be flagging the
world rather than the writing. URLs are masked before matching so a slug containing
`unlock` is not a register hit.

The budget is read from the skeleton rather than duplicated here, because the skeleton is
the knob: change the numbers there and this follows. If its line is reworded past the
pattern below, this exits 2 rather than silently checking nothing.

Usage:
  python scripts/report-register-check.py                 # every unit
  python scripts/report-register-check.py --unit BEN
  python scripts/report-register-check.py --terms         # print what it looks for
"""
import argparse
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
LINK = re.compile(r"\]\([^)\s]+\)")

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


ANCHOR = re.compile(r"\[([^\]]*)\]\([^)\s]+\)")


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
    for s in re.split(r"(?<=[.;])\s+", block.strip()):
        if CITED.search(s):
            continue
        out += [f for f in dict.fromkeys(FIGURE.findall(s)) if not YEAR.match(f.strip())]
    return list(dict.fromkeys(out))


def check_file(path, budget):
    text = open(path, encoding="utf-8").read()
    spans = prose_spans(text)
    hits, words, figs = [], 0, []
    for start, block, countable, raw in spans:
        words += len(re.sub(r"\[([^\]]*)\]", r"\1", countable).split())
        bare = unprovenanced(raw)
        if bare:
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
    for path in sorted(glob.glob(pattern)):
        kind = kind_of(path)
        if not kind:
            continue
        unit = os.path.basename(os.path.dirname(path))
        band_for = budget["region" if unit.startswith("X") else "country"]
        if kind not in band_for:                 # a document the unit's skeleton does not budget
            continue
        hits, words, figs = check_file(path, band_for)
        lo, hi = band_for[kind]
        rel = os.path.relpath(path, ROOT)
        band = "" if lo <= words <= hi else (f"  OVER by {words - hi}" if words > hi
                                             else f"  UNDER by {lo - words}")
        if band:
            over += 1
        print(f"{rel}  {words} words ({lo}-{hi}){band}  {len(hits)} register hit(s)"
              + (f"  {len(figs)} uncited block(s)" if figs else ""))
        for line, label, text in hits:
            print(f"    {rel}:{line}  [{label}] {text}")
        for line, bare in figs:
            print(f"    {rel}:{line}  [check H] no citation in this block: {', '.join(bare)}")
        flagged += len(hits)
        uncited += len(figs)
    print(f"\nregister: {flagged} hit(s) to rule on; budget: {over} document(s) outside band")
    print(f"check H: {uncited} narrative block(s) carrying a figure with no source to follow")
    return 1 if (flagged or over) else 0


if __name__ == "__main__":
    sys.exit(main())
