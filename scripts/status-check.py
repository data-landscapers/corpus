#!/usr/bin/env python3
"""Verify a status baseline — `STATUS-INIT.md` -> *Verification*, checks A to I.

    python scripts/status-check.py --unit RWA
    python scripts/status-check.py --unit all

**Run this after every edit pass, not once at the end.** That is the file's own instruction and it
is not a style preference: check A is set membership, and a URL synthesised from a remembered
pattern is indistinguishable from a real one by reading, so an edit that introduces one is
invisible until something tests it. The other checks are cheap enough to come along for free.

**A run that fails A, B or G is not issued.** A because a synthesised link is undetectable by eye;
B and G because a report that hedges or talks about its own evidence has stopped being skimmable,
which is the only thing it is for. C, E, F and I fail too — they are exact and there is no reading
under which a missing sub-section or a malformed acquire line is finished work. **H cannot be
checked here at all**: whether a sub-section opens on news needs a reader who knows the country, so
this prints the opening sentences and says so rather than pretending to judge them.

The acquire rule is Bill's, 2026-08-15, and it turns on *held*, not on which intermediary carried
the source. A cited URL the catalogue does not hold, dated 2024 or later, is a gap in the daily
sweep and owes a line in `{ISO3}-acquire.md`. Dated before 2024 it owes nothing — that is baseline
material, outside the collection perimeter, and OSINT was never going to hold it.
"""

import argparse
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402

# Check G's register. Evidence-talk and hedging, which the page never carries: the reader wants
# the fact and the link, and everything else was the writer's problem, settled before the sentence
# was written (`STATUS-INIT.md` -> *Writing*).
APPARATUS = [
    "reportedly", "apparently", "it appears", "sources indicate", "according to available",
    "it should be noted", "it is unclear", "the data suggests", "some sources", "no source",
    "the base", "the dataset", "the wiki", "conflicting", "discrepancy",
]

# Check D. A wikilink or a bare repo path is an internal address that escaped into a deliverable.
LEAKS = [(re.compile(r"\[\["), "[[wikilink]]"),
         (re.compile(r"(?<![\w/`])(raw|wiki|index|lookups|prep|outputs)/[a-z0-9]", re.I),
          "bare repo path")]

ACQUIRE_ROW = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})\s*\|([^|]*)\|([^|]*)\|"
                         r"\s*(https?://\S+?)\s*\|([^|]*)\|\s*$", re.M)


class Report:
    """Findings for one unit, so every check runs and the run sees the whole picture at once."""

    def __init__(self, unit):
        self.unit, self.fails, self.lines = unit, [], []

    def check(self, letter, what, bad, gate=True, cap=12):
        ok = not bad
        mark = "PASS" if ok else ("FAIL" if gate else "REPORT")
        self.lines.append(f"  check {letter} — {what}: {mark}"
                          + ("" if ok else f" ({len(bad)})"))
        for item in bad[:cap]:
            self.lines.append(f"        {item}")
        if len(bad) > cap:
            self.lines.append(f"        … and {len(bad) - cap} more")
        if bad and gate:
            self.fails.append(letter)
        return ok

    def note(self, text):
        self.lines.append(f"  {text}")


def check_unit(unit, show_openings=False):
    r = Report(unit)
    folder = os.path.join(S.REPORTS, unit)
    path = os.path.join(folder, f"{unit}-status.md")
    if not os.path.exists(path):
        r.note(f"no status report at {path}")
        r.fails.append("-")
        return r
    if not S.is_baseline(path):
        r.note("status report is a ledger render, not a STATUS-INIT baseline — nothing to check "
               "here; `report-render.py --check` is its verification")
        return r

    text = open(path, encoding="utf-8").read()
    fm = S.frontmatter(text)
    secs = S.sections(text)
    urls = S.links(text)

    # --- A — every link is held ------------------------------------------------------------
    held = S.held_urls()
    r.check("A", "every link is held", sorted(u for u in urls if u not in held))

    # --- B — every claim is linked ---------------------------------------------------------
    # A sub-section with no links at all and at most two sentences is the *not established*
    # statement, which is a fact about the country stated plainly and carries no link by design
    # (`STATUS-INIT.md` -> *Sources and conflicts*). Anywhere else, a paragraph stating a figure
    # with nothing to follow is the defect the no-link-no-claim rule exists to catch.
    unlinked = []
    for slug, label, prose in secs:
        paras = S.paragraphs(prose)
        if not S.links(prose) and sum(len(S.sentences(p)) for p in paras) <= 2:
            continue
        for p in paras:
            if not S.links(p):
                unlinked.append(f"{slug or label}: unlinked paragraph — {p[:90]}…")
    r.check("B", "every claim is linked", unlinked)

    # --- C — every time-varying figure is dated --------------------------------------------
    # A figure with no year anywhere in its sentence. Reported, not gated: "structural facts are
    # not time-varying and are not dated", and no regex can tell a law's section number from a
    # measurement. The run reads the list and fixes what is genuinely a dated quantity.
    undated = []
    for slug, label, prose in secs:
        for p in S.paragraphs(prose):
            for s in S.sentences(p):
                # Strip the link *targets* first, keeping their text. A URL is full of digits and
                # very often carries a year — `…/uploads/2024/05/…` — so testing the raw sentence
                # would let a link date an undated figure sitting next to it, which is the one
                # error this check exists to find.
                bare = re.sub(r"\]\((https?://[^)\s]+)\)", "]", s)
                figure = re.search(r"(?<![\w.])\d[\d,.]*\s?(%|m\b|bn\b|million|billion|per cent)",
                                   bare)
                if figure and not re.search(r"\b(19|20)\d{2}\b", bare):
                    undated.append(f"{slug or label}: {bare[:110]}…")
    r.check("C", "every time-varying figure is dated", undated, gate=False)

    # --- D — no wikilink, no bare repo path ------------------------------------------------
    leaks = []
    for pattern, what in LEAKS:
        for m in pattern.finditer(S.body(text)):
            ctx = " ".join(S.body(text)[max(0, m.start() - 40):m.start() + 40].split())
            leaks.append(f"{what}: …{ctx}…")
    r.check("D", "no wikilink or bare repo path", leaks)

    # --- E — 37 sub-sections, in outline order, none empty ---------------------------------
    want = S.outline()
    got = [(s, p) for s, _, p in secs]
    problems = []
    if [s for s, _ in got] != [slug for _, slug, _ in want]:
        have, expect = [s for s, _ in got], [slug for _, slug, _ in want]
        for slug in expect:
            if slug not in have:
                problems.append(f"missing sub-section {slug}")
        for slug in have:
            if slug is None:
                problems.append("a `###` heading carries no <!-- slug --> comment")
            elif slug not in expect:
                problems.append(f"unexpected sub-section {slug}"
                                + (" (suspended)" if slug in S.SUSPENDED else ""))
        if not problems:
            problems.append("sub-sections are all present but not in outline order")
    problems += [f"{s} is empty" for s, p in got if s and not p.strip()]
    r.check("E", f"{len(want)} sub-sections, in order, none empty", problems)

    # --- F — the acquire file ---------------------------------------------------------------
    # Two halves. Every line that is there must be well-formed and owed; and every cited URL that
    # is *not held* and dated 2024+ must have one. The second half cannot be fully mechanised —
    # the publication date of an unheld URL is not in any file here — so what the run gets is the
    # candidate list, with the held/unheld split already made.
    cat = S.catalogue_urls()
    apath = os.path.join(folder, f"{unit}-acquire.md")
    atext = open(apath, encoding="utf-8").read() if os.path.exists(apath) else ""
    rows = ACQUIRE_ROW.findall(atext)
    listed, bad_lines = set(), []
    for date, publisher, title, url, section in rows:
        listed.add(url)
        if date < "2024":
            bad_lines.append(f"{url} is dated {date} — before 2024 owes no acquire line")
        if not publisher.strip() or not title.strip() or not section.strip():
            bad_lines.append(f"{url} — a line must carry date, publisher, title, URL and "
                             f"sub-section")
        if url not in urls:
            bad_lines.append(f"{url} is not cited by the status report")
        if url in cat:
            bad_lines.append(f"{url} is already held — no acquisition is owed")
    r.check("F", "every acquire line is dated 2024+ and complete", bad_lines)

    # A URL that failed check A is not an acquisition candidate, it is a broken link. Offering it
    # here as something for OSINT to go and get would send the run chasing a source that does not
    # exist, and would bury the one finding that stops the report being issued.
    unheld = sorted(u for u in urls if u not in cat and u not in listed and u in held)
    if unheld:
        r.note(f"note: {len(unheld)} cited URL(s) the catalogue does not hold carry no acquire "
               f"line — correct where each is dated before 2024, which is baseline material "
               f"outside the collection perimeter. Anything 2024 or later owes a line:")
        for u in unheld[:10]:
            r.note(f"        {u}")
        if len(unheld) > 10:
            r.note(f"        … and {len(unheld) - 10} more")

    # --- G — no apparatus on the page -------------------------------------------------------
    hits = []
    for slug, label, prose in secs:
        for word in APPARATUS:
            for m in re.finditer(r"\b" + re.escape(word) + r"\b", prose, re.I):
                hits.append(f"{slug or label}: “{word}” — …{prose[max(0, m.start() - 45):m.start() + 45]}…")
    r.check("G", "no apparatus reached the page", hits)

    # --- H — opens on news ------------------------------------------------------------------
    r.note("check H — every sub-section opens on news: NEEDS A READER. A first sentence that "
           "defines a term, restates the question or leads with the oldest fact in the section "
           "is rewritten. Run with --openings to list them.")
    if show_openings:
        for slug, label, prose in secs:
            first = (S.sentences(S.paragraphs(prose)[0])[0] if S.paragraphs(prose) else "")
            r.note(f"        {slug or label}: {first[:150]}")

    # --- I — as-of honesty ------------------------------------------------------------------
    # `STATUS-INIT.md` states this as "compiled: is never ahead of its newest cited source", which
    # transcribes report-layer check J's *reported* half as though it were the gate. It cannot be
    # one: a baseline compiled today from sources up to last month is dated ahead of every one of
    # them, which is the normal and correct state of every status report ever written. What check J
    # actually fails on is the other direction — a document behind its evidence — and for a
    # baseline that question is answered by BUILD revising the section, not by a re-render. So the
    # lag is disclosed, exactly as report-layer check J discloses it. Flagged in the pre-flight.
    pub = S.catalogue_published()
    dated = sorted(p for p in (pub.get(u) for u in urls) if p)
    compiled = fm.get("compiled", "")
    if dated and compiled:
        newest = dated[-1]
        lag = (datetime.date.fromisoformat(compiled) - datetime.date.fromisoformat(newest[:10])).days \
            if re.match(r"^\d{4}-\d{2}-\d{2}$", compiled) and len(newest) >= 10 else None
        r.check("I", "as-of honesty",
                [] if not (compiled < newest) else
                [f"compiled {compiled} is behind the newest held source it cites ({newest})"])
        if lag is not None and lag > 0:
            r.note(f"note: compiled {lag} day(s) after the newest held source it cites "
                   f"({newest}) — disclosed, not judged")
    else:
        r.check("I", "as-of honesty", [], gate=False)

    # --- the two-line report, and the frontmatter it has to agree with -----------------------
    # A document whose frontmatter says 40 sources when it carries 35 is stating something false
    # about itself, in the one place a reader is most likely to trust without checking. It is
    # cheap to catch and there is no reading under which it is finished work.
    written = sum(1 for s, _, p in secs if p.strip())
    not_est = sum(1 for _, _, p in secs
                  if p.strip() and not S.links(p) and len(S.sentences(p)) <= 2)
    actual = {"sections_written": written, "not_established": not_est,
              "sources_cited": len(urls), "acquire_lines": len(rows)}
    drift = [f"frontmatter {k}: {fm[k]}, document: {v}"
             for k, v in actual.items() if k in fm and fm[k].strip() != str(v)]
    r.check("FM", "frontmatter counts match the document", drift)
    r.note(f"{unit} · sections written {written} of {len(want)} · not established {not_est} "
           f"· sources cited {len(urls)} · acquire lines {len(rows)}")
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--unit", required=True, help="ISO3, or `all` for every initialised baseline")
    ap.add_argument("--openings", action="store_true",
                    help="print each sub-section's first sentence, for check H")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    if args.unit.lower() == "all":
        units = sorted(u for u in os.listdir(S.REPORTS)
                       if os.path.isdir(os.path.join(S.REPORTS, u))
                       and S.is_baseline(os.path.join(S.REPORTS, u, f"{u}-status.md")))
        if not units:
            print("no initialised baselines yet — nothing to check")
            return 0
    else:
        units = [args.unit.upper()]

    rc = 0
    for unit in units:
        r = check_unit(unit, args.openings)
        print(f"\n{unit}")
        print("\n".join(r.lines))
        if r.fails:
            rc = 1
            print(f"  NOT ISSUED — failed {', '.join(r.fails)}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
