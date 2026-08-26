#!/usr/bin/env python3
"""test_indicators.py — the indicator frame, and the rules the progress report rests on.

    python scripts/test_indicators.py

`documentation/progress-report-redesign.md` is the design; this asserts the parts of it that a
later edit could break silently. Three groups:

**The frame** — `lookups/indicators.csv` is the canonical list and is hand-maintained, so the
things a hand can get wrong are checked: a duplicate or missing id, a subject outside the
taxonomy, a chapter the taxonomy does not carry. The frame covering all 38 Level-2 subjects is
asserted rather than assumed, because §1's claim to ask "the same set of questions of every
country" is exactly that coverage.

**The rendering** — pipes and newlines cannot reach a table cell, a citation resolves from slug to
URL, an unresolvable one loses its link and is reported rather than swallowed, and a raw URL is
left alone for check M to refuse.

**The checks** — the four rules §3 says are testable are tested here on fixtures, in both
directions where §3 says both directions. The point of the group is that these are the only
machine-decidable claims in the vocabulary: *Advanced* against *No change* is a drafter's
judgement and no test here pretends otherwise.

Nothing in this file touches `outputs/`, and the two that would need a catalogue — resolving a
real slug, and check M — use a stub table instead, so the suite runs on a machine with no vault.
"""
from __future__ import annotations

import csv
import importlib.util
import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import indicators_lib as il  # noqa: E402

_spec = importlib.util.spec_from_file_location("rr", CORPUS / "scripts" / "report-render.py")
rr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rr)

failures = []


def check(what, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {what}"
          + ("" if ok else f"\n       got {got!r}\n       want {want!r}"))
    if not ok:
        failures.append(what)


# --- the frame ------------------------------------------------------------------------------
print("the frame")
frame = il.frame()
check("every indicator has an id", all(r["indicator_id"] for r in frame), True)
check("ids are unique", len({r["indicator_id"] for r in frame}), len(frame))
tax = {r["Key"]: r["Level 1"] for r in csv.DictReader(
    open(CORPUS / "lookups" / "taxonomy.csv", encoding="utf-8-sig"))}
check("every subject is in the taxonomy",
      sorted({r["subject"] for r in frame} - set(tax)), [])
check("every subject in the taxonomy has at least one indicator — §1's 'same set of questions'",
      sorted(set(tax) - {r["subject"] for r in frame}), [])
check("each indicator's chapter is its subject's Level-1 parent",
      [r["indicator_id"] for r in frame if tax.get(r["subject"]) != r["chapter"]], [])
check("the id is the subject plus a slug of the indicator, so it is composable by nobody",
      all(r["indicator_id"].startswith(r["subject"] + "--") for r in frame), True)

order = [s for _, s, _ in rr.sections("ZAF")[0]]
grouped = il.by_chapter(order)
check("by_chapter returns the taxonomy's chapters in the taxonomy's order",
      [c for c, _ in grouped], [c for c in order if c in {r["chapter"] for r in frame}])
check("grouping loses no indicator", sum(len(v) for _, v in grouped), len(frame))

# --- the rendering --------------------------------------------------------------------------
print("\nthe cell")
check("a pipe becomes an entity — it would otherwise shift every column after it",
      rr.cell("a | b"), "a &#124; b")
check("a newline is flattened — it would otherwise end the row",
      rr.cell("a\nb\n\nc"), "a b c")
check("empty stays empty", rr.cell(None), "")

print("\ncitations")
URLS = {"a-real-slug": "https://example.com/one",
        "parens-slug": "https://example.com/x(1).pdf"}
un = []
check("a slug resolves to its URL",
      rr.cite_prose("the [act](a-real-slug) passed", URLS, un),
      "the [act](https://example.com/one) passed")
check("a URL with parens is percent-encoded, or the markdown link ends early",
      rr.cite_prose("[x](parens-slug)", URLS, un),
      "[x](https://example.com/x%281%29.pdf)")
check("nothing was reported unresolved so far", un, [])
check("an unknown slug keeps its label and loses its link",
      rr.cite_prose("the [act](no-such-slug) passed", URLS, un), "the act passed")
check("and is reported, because the document cannot show it went", un, ["no-such-slug"])
un2 = []
check("a target with spaces is matched too, so an ill-formed citation cannot print raw",
      rr.cite_prose("[x](not a slug at all)", URLS, un2), "x")
check("and is reported", un2, ["not a slug at all"])
un4 = []
SLUG_PARENS = "2025-11-08 Digital 2026 Eritrea (DataReportal)"
check("a slug carrying a bracketed qualifier resolves whole — 364 of the base's do",
      rr.cite_prose(f"penetration [rose]({SLUG_PARENS}) year on year",
                    {SLUG_PARENS: "https://example.com/dr"}, un4),
      "penetration [rose](https://example.com/dr) year on year")
check("and nothing was left over to print as text", un4, [])

un3 = []
check("a raw URL is left alone — check M refuses it rather than the renderer resolving it",
      rr.cite_prose("[x](https://example.com/raw)", URLS, un3),
      "[x](https://example.com/raw)")
check("and is not counted unresolved", un3, [])

DOUBLE = "2026-07-10 SOLLY MALATSI  Removing smartphone tax means access to opportunity"
un5 = []
check("a slug with a double space inside it survives the cell's own flattening",
      rr.developments_cell({"summary": f"the excise was [removed]({DOUBLE})."},
                           {DOUBLE: "https://example.com/excise"}, un5),
      "the excise was [removed](https://example.com/excise).")
check("and nothing was reported unresolved", un5, [])

print("\nthe developments cell")
row = {"summary": "terse.", "developments": "one.\n\ntwo."}
check("the summary leads and the full record follows in an expander",
      rr.developments_cell(row, URLS, []),
      "terse. <details><summary>Full record</summary>one.<br><br>two.</details>")
check("a No evidence row renders as nothing at all",
      rr.developments_cell({}, URLS, []), "")
check("***No evidence*** is marked; the other values are not",
      (rr.mark_progress("No evidence"), rr.mark_progress("Advanced")),
      ("***No evidence***", "Advanced"))
check("a qualified No evidence is marked on its stem",
      rr.mark_progress("No evidence, nothing swept"), "***No evidence, nothing swept***")

# --- the checks -----------------------------------------------------------------------------
print("\nthe checks")
TMP = tempfile.mkdtemp()
os.makedirs(os.path.join(TMP, "ZZZ"))
LEDGER = [{"row_id": "ZZZ-a", "place": "ZZZ", "subject": "gov.policy", "section": "Governance",
           "kind": "instrument", "name": "A thing", "status": "Implemented",
           "published": "2026-01-01", "milestone": "Gazetted", "since": "", "movement": "",
           "position_start": "", "position_end": "", "sources": "a-real-slug", "probe_at": "",
           "note": ""}]
with open(os.path.join(TMP, "ZZZ", "ledger.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(LEDGER[0])); w.writeheader(); w.writerows(LEDGER)
open(os.path.join(TMP, "ZZZ", "gaps.csv"), "w", encoding="utf-8", newline="").write(
    "row_id,name,what_would_settle_it,probe_at\n")

IID = frame[0]["indicator_id"]
IID2 = frame[1]["indicator_id"]


def with_rows(rows, fn):
    """Run one check over a fixture indicators.csv and return (rc, printed output)."""
    with open(os.path.join(TMP, "ZZZ", "indicators.csv"), "w", encoding="utf-8",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(il.UNIT_FIELDS)); w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in il.UNIT_FIELDS})
    old_reports, old_urls, old_raw = rr.REPORTS, rr.slug_urls, rr.raw_slugs
    rr.REPORTS = TMP
    rr.slug_urls = lambda: URLS
    rr.raw_slugs = lambda: set(URLS) | {"held-but-uncitable"}
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            rc = fn("ZZZ")
    finally:
        rr.REPORTS, rr.slug_urls, rr.raw_slugs = old_reports, old_urls, old_raw
    return rc, buf.getvalue()


GOOD = dict(indicator_id=IID, progress="Advanced", summary="a [claim](a-real-slug)",
            developments="the record", row_ids="ZZZ-a")
check("a well-formed row passes check I", with_rows([GOOD], rr.check_indicators)[0], 0)
check("and passes check L", with_rows([GOOD], rr.check_indicator_prose)[0], 0)
check("and passes check M", with_rows([GOOD], rr.check_indicator_sources)[0], 0)
check("No evidence with no mapped rows and no prose passes all three",
      [with_rows([dict(indicator_id=IID, progress="No evidence")], f)[0]
       for f in (rr.check_indicators, rr.check_indicator_prose, rr.check_indicator_sources)],
      [0, 0, 0])

cases_I = [
    ("a value outside the vocabulary", dict(GOOD, progress="Improving"), "outside the vocabulary"),
    ("an empty value — the frame asks every question", dict(GOOD, progress=""),
     "no progress value"),
    ("No evidence with rows mapped to it — the base holds what the row denies",
     dict(GOOD, progress="No evidence", summary="", developments=""),
     "ledger row(s) map to it"),
    ("a stated value with nothing mapped — a claim resting on nothing",
     dict(GOOD, row_ids=""), "no ledger row mapped"),
    ("Mixed without the clause §3 makes mandatory", dict(GOOD, progress="Mixed"),
     "no qualifying clause"),
    ("a mapped row that is not on the ledger", dict(GOOD, row_ids="ZZZ-nope"),
     "not on this unit's ledger"),
    ("an id the frame does not hold", dict(GOOD, indicator_id="gov.policy--invented"),
     "not an indicator the frame holds"),
]
for what, row, wanted in cases_I:
    rc, out = with_rows([row], rr.check_indicators)
    check(f"check I catches {what}", (rc, wanted in out), (1, True))

check("check I accepts Mixed once it carries its clause",
      with_rows([dict(GOOD, progress="Mixed, act enacted, regulations stalled")],
                rr.check_indicators)[0], 0)

cases_L = [
    ("a stated value with no summary", dict(GOOD, summary=""), "with no summary"),
    ("a stated value with no developments", dict(GOOD, developments=""), "with no developments"),
    ("No evidence carrying prose — the value and the text disagree",
     dict(GOOD, progress="No evidence", row_ids=""), "but carries prose"),
]
for what, row, wanted in cases_L:
    rc, out = with_rows([row], rr.check_indicator_prose)
    check(f"check L catches {what}", (rc, wanted in out), (1, True))

cases_M = [
    ("a slug the base does not hold", dict(GOOD, summary="a [claim](ghost-slug)"),
     "does not hold"),
    ("a slug held without a URL — OSINT's to fix, not the drafter's",
     dict(GOOD, summary="a [claim](held-but-uncitable)"), "an uncitable record"),
    ("a URL written directly into the prose",
     dict(GOOD, summary="a [claim](https://example.com/raw)"), "directly"),
    ("a bad citation in developments, not only in summary",
     dict(GOOD, developments="a [claim](ghost-slug)"), "does not hold"),
]
for what, row, wanted in cases_M:
    rc, out = with_rows([row], rr.check_indicator_sources)
    check(f"check M catches {what}", (rc, wanted in out), (1, True))

print("\nthe region carve-out and the refusal")
check("a region runs none of the three — it issues the movement document (§1)",
      [f("XAF") for f in (rr.check_indicators, rr.check_indicator_prose,
                          rr.check_indicator_sources)], [0, 0, 0])
os.remove(os.path.join(TMP, "ZZZ", "indicators.csv"))
old = rr.REPORTS
rr.REPORTS = TMP
try:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = rr.render_progress_indicators("ZZZ", "2026-08-26", "2026-08", 12)
    check("an unmapped unit is refused, not rendered as 121 blank rows", rc, 1)
    check("and says why", "mapping pass has not run" in buf.getvalue(), True)
    check("and wrote nothing",
          os.path.exists(os.path.join(TMP, "ZZZ", "ZZZ-progress.md")), False)
finally:
    rr.REPORTS = old
shutil.rmtree(TMP, ignore_errors=True)

# --- the register check's indicator half ------------------------------------------------------
print("\nthe register, over indicators.csv")
_rspec = importlib.util.spec_from_file_location(
    "rc", CORPUS / "scripts" / "report-register-check.py")
rc = importlib.util.module_from_spec(_rspec)
_rspec.loader.exec_module(rc)

bands = rc.indicator_budget()
check("the per-indicator bands are read from the skeleton, not hard-coded here",
      sorted(bands), ["developments", "summary"])
check("and both are (low, high) pairs with low below high",
      all(len(v) == 2 and v[0] < v[1] for v in bands.values()), True)


def reg(rows):
    """Run the register check over a fixture indicators.csv; return (hits, band, figs)."""
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "ZZZ"))
    f = os.path.join(d, "ZZZ", "indicators.csv")
    with open(f, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(il.UNIT_FIELDS))
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in il.UNIT_FIELDS})
    try:
        return rc.check_indicators_file(f, bands)
    finally:
        shutil.rmtree(d, ignore_errors=True)


CLEAN = dict(
    indicator_id=IID, progress="Advanced",
    summary="The strategy was [approved by cabinet](a-slug) in March, five years late.",
    developments="2026-03-04 — cabinet [approved the national ICT strategy](a-slug), five "
                 "years after the previous one lapsed. No implementation plan was published "
                 "alongside it and none has appeared since, so the target date rests on a "
                 "[departmental statement](b-slug) that names no budget line.")
check("clean prose raises nothing at all", reg([CLEAN]), ([], [], []))

hits, _, _ = reg([dict(CLEAN, summary="We think it will [unlock the ecosystem](a-slug).")])
check("the register reaches the summary column",
      sorted({lab for _, _, lab, _ in hits}), ["first person", "jargon"])

hits, _, _ = reg([dict(CLEAN, developments="It was unveiled at scale. [x](a-slug)")])
check("and the developments column",
      sorted({lab for _, _, lab, _ in hits}), ["flash verb", "jargon"])
check("a hit names the indicator and the field it is in",
      hits[0][1], IID + "/developments")

# **A slug citation is not the drafter's prose.** This base cites by record title, so a target
# runs to eight or ten words and 364 of them carry a bracketed qualifier. Counted, they blow an
# 8-40 word band; read, they charge a source's own headline to the writer's register.
LONG_SLUG = "2025-11-08 Digital 2026 Eritrea (DataReportal)"
hits, band, _ = reg([dict(CLEAN,
    summary=f"Connections [rose 8.2% year on year]({LONG_SLUG}) to 859,000, "
            f"among Africa's lowest.")])
check("a slug target with spaces and parens is not counted into the word budget", band, [])
check("nor read as prose the register can charge to the drafter", hits, [])

_, band, _ = reg([dict(CLEAN, summary="Too short.")])
check("the budget catches a summary under band",
      [(w, f, n < lo) for _, w, f, n, lo, _ in band], [(IID, "summary", True)])

_, band, _ = reg([dict(CLEAN, summary="word " * (bands["summary"][1] + 5) + "[x](a-slug)")])
check("and over band",
      [(w, f, n > hi) for _, w, f, n, _, hi in band], [(IID, "summary", True)])

_, _, figs = reg([dict(CLEAN, summary="Spending reached US$412m over the period.")])
check("check H catches a figure in a sentence with no citation",
      [(w, bare) for _, w, bare in figs], [(IID + "/summary", ["US$412m"])])

_, _, figs = reg([dict(CLEAN, summary="Spending reached [US$412m](a-slug) over the period.")])
check("a slug citation counts as provenance — this prose cites the base, not the web", figs, [])

_, _, figs = reg([dict(CLEAN, summary="The 2026 review [reported back](a-slug) on time.")])
check("a bare year is not a figure", figs, [])

check("an empty cell is not the register's business — check L knows if it should be empty",
      reg([dict(indicator_id=IID, progress="No evidence")]), ([], [], []))

MULTI = dict(CLEAN, developments=CLEAN["developments"] + "\n\n2026-06-01 — a second "
             "[development](b-slug) followed, long enough to clear the floor the band sets.")
hits, _, _ = reg([MULTI, dict(CLEAN, indicator_id=IID2, summary="We got this wrong.")])
check("a newline inside a quoted field does not throw the line numbers off",
      [ln for ln, _, _, _ in hits], [5])


# The migration switch: a country progress report is checked out of its narrative markers while
# it still has them, and out of `indicators.csv` once it does not. Nothing announces the
# changeover — the document's own shape decides, so the two states can coexist across 54 units.
print("\nthe migration switch")


def run(progress_body, with_indicators):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "ZZZ"))
    open(os.path.join(d, "ZZZ", "ZZZ-progress.md"), "w", encoding="utf-8",
         newline="\n").write(progress_body)
    if with_indicators:
        with open(os.path.join(d, "ZZZ", "indicators.csv"), "w", encoding="utf-8",
                  newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(il.UNIT_FIELDS))
            w.writeheader()
            w.writerow({k: CLEAN.get(k, "") for k in il.UNIT_FIELDS})
    old_reports, old_argv = rc.REPORTS, sys.argv
    rc.REPORTS, sys.argv = d, ["x", "--unit", "ZZZ"]
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            rc.main()
    finally:
        rc.REPORTS, sys.argv = old_reports, old_argv
        shutil.rmtree(d, ignore_errors=True)
    return buf.getvalue()


LEGACY = ("---\ntitle: x\n---\n\n# x\n\n<!-- narrative: governance -->\n"
          "We unveiled the ecosystem at scale.\n<!-- /narrative -->\n")
out = run(LEGACY, with_indicators=False)
check("a progress report still carrying markers is still register-checked",
      "[first person]" in out and "[jargon]" in out, True)
check("but is not held to a whole-document band that no longer applies to it",
      "not budgeted" in out, True)
check("and its missing indicators.csv is named rather than passed over in silence",
      "no indicators.csv" in out, True)

RENDERED = "---\ntitle: x\n---\n\n# x\n\n| Topic | Indicator | Developments | Progress |\n"
out = run(RENDERED, with_indicators=True)
check("a re-rendered one is not read as a document at all — its prose is not in it",
      "ZZZ-progress.md" in out, False)
check("and its indicators.csv is checked instead",
      "indicators.csv" in out and "no indicators.csv" not in out, True)

print(f"\n{'PASS' if not failures else 'FAIL — ' + str(len(failures)) + ' assertion(s)'}")
sys.exit(1 if failures else 0)
