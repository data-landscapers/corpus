#!/usr/bin/env python3
"""Verify a status baseline — `STATUS-INIT.md` -> *Verification*, checks A to K.

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

**J — every sub-section within 350 words — reports and never fails** (housekeeping 33,
2026-10-23). STATUS-INIT caps an h3 at 350 words, and stage 4's baseline edits add sentences night
after night; nothing counted them, and 743 sub-sections across all 54 reports were over when
this was added. An over-cap section is still a correct one, so J never triggers
`REPORT-UPDATE.md`'s revert rule: it is `UNIT-REVIEW.md` step 3's list of what to trim. **A word is a whitespace-separated token of the
prose a reader sees**: HTML comments dropped and each link reduced to its text, so a URL is never
counted, and a free-standing dash is. ZAF's `tech.ai`, put at 343 by a careful hand count on
2026-10-23, reads 343.

**K — derived non-state totals agree with the table — reports and never fails** (housekeeping 34,
2026-10-24). A `<!-- derived -->` paragraph that counts the unit's non-state commitments or totals
their US$ is the report's own arithmetic over `{U}-nonstate.csv`, and the next deal added makes it
wrong with nothing changing in the report. K reads the forms that name the whole record — *N
commitments are on record … worth about US$X*, *of the N commitments*, *a recorded total of US$X
across N commitments*, *of the US$X on record*, *They come to US$X* after a count — and compares
them with the table's rows, rows with an amount, and `commitment_usd_m` summed. A count matches
either row figure; a hedged one ("around twenty") is allowed 15 per cent. An amount is allowed half
its last stated place, or 5 per cent hedged and 2 per cent bare, never more than 15. It does not
read a subset, a figure in another currency, a sentence naming regional operations it does not set
aside, or anything outside a derived paragraph. Fixed by recomputing the sentence from the table.

The acquire rule is Bill's, 2026-08-15, and it turns on *held*, not on which intermediary carried
the source. A cited URL the catalogue does not hold, dated 2024 or later, is a gap in the daily
sweep and owes a line in the transfer folder's `africa-acquire.csv`. Dated before 2024 it owes nothing — that is baseline
material, outside the collection perimeter, and OSINT was never going to hold it.
"""

import argparse
import csv
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
# Marks a paragraph the report computed itself rather than took from a source. HTML comments pass
# through the renderer unseen, so it is invisible to a reader and still machine-checkable.
DERIVED = "<!-- derived -->"

# Check J. The cap is STATUS-INIT's (*Writing*: "one continuous narrative per h3, up to 350 words").
CAP = 350
LINK_TEXT = re.compile(r"\[([^\]]*)\]\((?:<[^>]*>|[^)\s]*)\)")


def prose_words(prose):
    """Words as a reader counts them — comments dropped, every link reduced to its text."""
    prose = re.sub(r"<!--.*?-->", "", prose, flags=re.S)
    return len(LINK_TEXT.sub(r"\1", prose).split())


# Check K. A derived paragraph's unit-level count of non-state commitments, and the US$ total it
# gives them, against `outputs/non-state-finance/{U}-nonstate.csv` — the table, which already
# applies the 2015 floor and the scope halving (`documentation/nonstate-scope.md`), so a row there
# is a deal and `commitment_usd_m` is what it counts for. Only the forms that name the whole
# record are read; a subset ("four commitments from China Eximbank") is never parsed, because a
# false alarm on a correct paragraph costs a reader more than a miss costs the check.
NONSTATE = os.path.join(S.REPO, "outputs", "non-state-finance")
_UNITS = ("one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
          "fifteen sixteen seventeen eighteen nineteen").split()
_TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()
NUM_WORDS = {w: i + 1 for i, w in enumerate(_UNITS)}
for _i, _t in enumerate(_TENS):
    NUM_WORDS[_t] = 20 + 10 * _i
    for _j, _u in enumerate(_UNITS[:9]):
        NUM_WORDS[f"{_t}-{_u}"] = 20 + 10 * _i + _j + 1
NUM = (r"(?:\d{1,4}|(?:" + "|".join(_TENS) + r")(?:-(?:" + "|".join(_UNITS[:9]) + r"))?|"
       + "|".join(sorted(_UNITS, key=len, reverse=True)) + r")")
HEDGE = (r"(?:about|around|roughly|some|approximately|nearly|almost|close\s+to|just\s+over|"
         r"just\s+under|over|more\s+than)")
# The only words allowed between the number and the noun: each names the whole record. One that
# narrows it — Chinese-financed, multilateral, regional, active — stops the match.
ADJ = (r"(?:distinct|external|digital|digital-sector|sector|financing|finance|country-level|"
       r"costed|non-state|recorded)")
NOUN = r"(?:commitments(?:\s+and\s+pledges)?|deals)"
AMT = r"(?:US\$|USD\s?|\$)\s?(?P<v>\d[\d,]*(?:\.\d+)?)\s*(?P<u>bn|billion|m|million)\b"
_H = rf"(?P<h>{HEDGE}\s+)?"
COUNT_SUBJECT = [   # the record as a sentence's subject: an amount `worth …` after it is its total
    re.compile(rf"(?<![\w-]){_H}(?P<n>{NUM})\s+(?:{ADJ}\s+){{0,4}}{NOUN}\b(?P<tail>[^.;:]{{0,90}}?)"
               r"\b(?:(?:are|is|were)\s+(?:on\s+(?:the\s+)?record|recorded|held|captured)|"
               r"in\s+all|make\s+up\s+th(?:at|e)\s+record|carry\s+the\s+whole|touch|reach)\b", re.I),
    re.compile(rf"\b(?:there\s+(?:are|were)|has\s+drawn)\s+{_H}(?P<n>{NUM})\s+(?:{ADJ}\s+){{0,4}}"
               rf"{NOUN}\b(?P<tail>)", re.I),
]
# "four of the ten commitments on record": the ten is the record — unless a qualifier follows the
# noun ("of the 17 commitments beginning in 2025"), which makes it a subset.
COUNT_OF_THE = re.compile(rf"\b(?:of|across)\s+the\s+(?P<n>{NUM})\s+(?:{ADJ}\s+){{0,4}}{NOUN}"
                          r"(?=\s*(?:[,.;:()]|$|on\s+(?:the\s+)?record|recorded|on\s+[\w'’]+\s+record"
                          r"|to\s|touching\s|naming\s|for\s+[A-Z]|are\s|were\s))", re.I)
COUNT_ACROSS = [    # an amount and the count it spans, stated as the whole
    re.compile(rf"\btotal\s+of\s+(?P<ah>{HEDGE}\s+)?{AMT}\s+across\s+(?P<n>{NUM})\s+"
               rf"(?:{ADJ}\s+){{0,4}}{NOUN}", re.I),
    re.compile(rf"(?P<ah>{HEDGE}\s+)?{AMT}\s+of\s+(?:[\w-]+\s+){{0,5}}?commitments?\s+"
               rf"(?:to\s+[\w'’ -]+?\s+)?across\s+(?P<n>{NUM})\s+(?:{ADJ}\s+){{0,4}}{NOUN}", re.I),
]
AMT_AFTER_COUNT = re.compile(rf"\b(?:worth|value\s+of|come\s+to|comes\s+to|together|"
                             rf"at\s+a\s+combined)\s+(?P<ah>{HEDGE}\s+)?{AMT}", re.I)
AMT_WHOLE = [       # the total named as such, with or without a count beside it
    re.compile(rf"\b(?:recorded|whole)\s+total\s+of\s+(?P<ah>{HEDGE}\s+)?{AMT}", re.I),
    re.compile(rf"\bof\s+the\s+(?P<ah>{HEDGE}\s+)?{AMT}\s+on\s+(?:the\s+)?record\b", re.I),
]
AMT_PRONOUN = re.compile(rf"^(?:They|Together\s+they|Those\s+with\s+a\s+(?:recorded|stated)\s+"
                         rf"(?:value|amount))\s+come\s+to\s+(?P<ah>{HEDGE}\s+)?{AMT}")
REGIONAL_IN = re.compile(r"\bregional\b", re.I)
REGIONAL_OUT = re.compile(r"\b(outside|separately|not\s+in|excluded|aside|not\s+among)\b", re.I)


def number(word):
    w = word.lower()
    return int(w) if w.isdigit() else NUM_WORDS.get(w)


def usd_m(v, u):
    """A prose amount in US$m, and the rounding its own precision allows (half its last place)."""
    digits = v.replace(",", "")
    scale = 1000 if u.lower() in ("bn", "billion") else 1
    if "." in digits:
        place = 10 ** -len(digits.split(".")[1])
    else:
        place = 10 ** (len(digits) - len(digits.rstrip("0")))
    return float(digits) * scale, place * scale / 2


def nonstate_table(unit):
    """`(deals, deals with an amount, US$m total)` for the unit, or None with no table."""
    path = os.path.join(NONSTATE, f"{unit}-nonstate.csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    amounts = [float(r["commitment_usd_m"]) for r in rows if (r.get("commitment_usd_m") or "").strip()]
    return len(rows), len(amounts), sum(amounts)


def stated_totals(sentence, prev_counted=False):
    """`(count, count_hedged, amount_usd_m, amount_tolerance)` the sentence states of the whole
    non-state record, any of them None where it states none. Unit-level only: a sentence naming
    regional operations without setting them aside is skipped, as is every subset form."""
    s = re.sub(r"\s+", " ", re.sub(r"\]\((?:https?://[^)\s]+)\)", "]", sentence))
    s = re.sub(r"\[([^\]]*)\]", r"\1", s)
    if REGIONAL_IN.search(s) and not REGIONAL_OUT.search(s):
        return None, False, None, None
    count = hedged = amount = tol = None
    amt_m = None
    for rx in COUNT_ACROSS:
        m = rx.search(s)
        if m:
            count, hedged, amt_m = number(m["n"]), False, m
            break
    subject = None
    if count is None:
        for rx in COUNT_SUBJECT:
            m = rx.search(s)
            if m and not re.search(rf"\b(?:from|by)\s+(?!{NUM}\b)", m["tail"], re.I):
                subject, count, hedged = m, number(m["n"]), bool(m["h"])
                break
    if count is None:
        m = COUNT_OF_THE.search(s)
        if m:
            count, hedged = number(m["n"]), False
    if amt_m is None and subject is not None:
        amt_m = AMT_AFTER_COUNT.search(s, subject.end())
    if amt_m is None and prev_counted:
        amt_m = AMT_PRONOUN.search(s)
    if amt_m is None:
        amt_m = next((m for m in (rx.search(s) for rx in AMT_WHOLE) if m), None)
    if amt_m is not None:
        amount, half = usd_m(amt_m["v"], amt_m["u"])
        rel = 0.05 if amt_m["ah"] else 0.02
        tol = min(max(half, rel * amount), 0.15 * amount)
    return count, bool(hedged), amount, tol


def totals_drift(text, table):
    """Every derived sentence whose stated count or US$ total of the non-state record disagrees
    with the table `(deals, deals with an amount, total)`, as one line apiece."""
    n_all, n_amt, total = table
    out = []
    for slug, label, prose in S.sections(text):
        for p in S.paragraphs(prose):
            if not p.startswith(DERIVED):
                continue
            prev = False
            for sent in S.sentences(p[len(DERIVED):].strip()):
                count, hedged, amount, tol = stated_totals(sent, prev)
                prev = count is not None and amount is None   # "They come to …" is its total
                bad = []
                if count is not None:
                    slack = max(1, round(0.15 * count)) if hedged else 0
                    if min(abs(count - n_all), abs(count - n_amt)) > slack:
                        bad.append(f"{count} deals, table {n_all}"
                                   + (f" ({n_amt} with an amount)" if n_amt != n_all else ""))
                if amount is not None and abs(amount - total) > tol:
                    bad.append(f"US${amount:,.0f}m, table US${total:,.1f}m")
                if bad:
                    out.append(f"{slug or label}: states {'; '.join(bad)} — {sent[:150]}…")
    return out


LEAKS = [(re.compile(r"\[\["), "[[wikilink]]"),
         (re.compile(r"(?<![\w/`])(raw|wiki|index|lookups|prep|outputs)/[a-z0-9]", re.I),
          "bare repo path")]


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
    #
    # The other exemption is a paragraph marked `<!-- derived -->`: a figure the report computed
    # itself over the evidence it read — how many commitments there are, what they come to, which
    # subsector took the most. No source states it, so there is nothing to link, and the rule that
    # a claim carries the URL establishing it does not reach it (`STATUS-INIT.md` -> *The one hard
    # rule*). The marker is required rather than inferred, because "no link because nothing
    # establishes this" and "no link because the writer forgot" are the same paragraph otherwise.
    # The closing absence block is emitted from the maturity assessment (R151), states what has
    # not been found, and carries no link by construction; check A in `report-register-check.py`
    # holds it to what the assessment says.
    unlinked, derived = [], []
    for slug, label, prose in secs:
        paras = S.paragraphs(S.ABSENCE_BLOCK.sub("", prose))
        if not S.links(prose) and sum(len(S.sentences(p)) for p in paras) <= 2:
            continue
        for p in paras:
            if p.startswith(DERIVED):
                derived.append(f"{slug or label}: {p[len(DERIVED):].strip()[:90]}…")
                continue
            if not S.links(p):
                unlinked.append(f"{slug or label}: unlinked paragraph — {p[:90]}…")
    r.check("B", "every claim is linked", unlinked)
    if derived:
        r.note(f"note: {len(derived)} derived paragraph(s) carry no link by design — the report's "
               f"own arithmetic over the evidence it read, which no source states:")
        for d in derived[:10]:
            r.note(f"        {d}")
        if len(derived) > 10:
            r.note(f"        … and {len(derived) - 10} more")

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
    # Scanned with the http(s) link targets stripped out. Check D is about an internal address
    # reaching a reader, and a link target is not prose — a real repo path used as a target still
    # shows, because only http(s) targets are removed, and check A tests the targets themselves.
    # Without this, any cited URL with a path segment ending in one of the repo folder names trips
    # it: WIPO's `…/global-innovation-index/docs-en…` read as a bare `index/` path on SDN,
    # 2026-08-21, because the lookbehind excludes a word character and a slash but not a hyphen.
    prose = re.sub(r"\]\((https?://[^)\s]+)\)", "]", S.body(text))
    leaks = []
    for pattern, what in LEAKS:
        for m in pattern.finditer(prose):
            ctx = " ".join(prose[max(0, m.start() - 40):m.start() + 40].split())
            leaks.append(f"{what}: …{ctx}…")
    r.check("D", "no wikilink or bare repo path", leaks)

    # --- E — 39 sub-sections, in outline order, none empty ---------------------------------
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

    # --- F — the acquire feed ---------------------------------------------------------------
    # Two halves. Every line that is there must be well-formed and owed; and every cited URL that
    # is *not held* and dated 2024+ must have one. The second half cannot be fully mechanised —
    # the publication date of an unheld URL is not in any file here — so what the run gets is the
    # candidate list, with the held/unheld split already made.
    #
    # The feed is `africa-acquire.csv` in the transfer folder, one row per source across all 54 countries, and this
    # reads only the rows whose `iso3` is the unit under check. It was `{ISO3}-acquire.md` until
    # 2026-08-15; a queue Bill works down wants to be sortable and countable, which 54 markdown
    # tables are not.
    #
    # A row OSINT has closed has left the feed for `acquire-done.csv` and is not read back as an
    # open line: it is not checked for well-formedness — a staged one will appear in the catalogue
    # once ingested, and reporting *already held — no acquisition is owed* against a line that did
    # its job is backwards — but its URL still counts as listed, so the note below stops offering
    # it as something nobody has asked for. First round-trip: AGO, 47 rows, 2026-08-24.
    cat = S.catalogue_urls()
    rows = [row for row in S.acquire_rows()
            if row.get("iso3", "").upper() == unit and S.status_owned(row)]
    closed = {row.get("url", "") for row in S.acquire_done_rows()
              if row.get("iso3", "").upper() == unit and S.status_owned(row)}
    listed, bad_lines = set(closed), []
    for row in rows:
        url, date = row.get("url", ""), row.get("published", "")
        listed.add(url)
        if date < "2024":
            bad_lines.append(f"{url} is dated {date or 'nothing'} — before 2024 owes no acquire "
                             f"line")
        if not row.get("publisher", "").strip() or not row.get("title", "").strip() \
                or not row.get("sub_section", "").strip():
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

    # --- J — every sub-section within the cap ---------------------------------------------
    long = [(slug or label, prose_words(p)) for slug, label, p in secs]
    r.check("J", f"every sub-section within {CAP} words",
            [f"{name}: {n} words" for name, n in long if n > CAP], gate=False, cap=50)

    # --- K — derived non-state totals agree with the table --------------------------------
    table = nonstate_table(unit)
    if table is None:
        r.note(f"check K — derived non-state totals agree with the table: SKIP (no {unit}-nonstate.csv)")
    else:
        r.check("K", "derived non-state totals agree with the table", totals_drift(text, table),
                gate=False)

    # --- the two-line report, and the frontmatter it has to agree with -----------------------
    # A document whose frontmatter says 40 sources when it carries 35 is stating something false
    # about itself, in the one place a reader is most likely to trust without checking. It is
    # cheap to catch and there is no reading under which it is finished work.
    written = sum(1 for s, _, p in secs if p.strip())
    not_est = sum(1 for _, _, p in secs
                  if p.strip() and not S.links(p) and len(S.sentences(p)) <= 2)
    # `acquire_lines` counts the open feed *and* the closed rows. The frontmatter stamps what the
    # baseline found, and OSINT answering a line does not un-find the gap that produced it — a
    # count that fell to zero the day the queue was worked would make every issued report drift
    # against its own frontmatter for a reason that is not about the report *(2026-08-24)*.
    owed = len(rows) + len(closed)
    actual = {"sections_written": written, "not_established": not_est,
              "sources_cited": len(urls), "acquire_lines": owed}
    drift = [f"frontmatter {k}: {fm[k]}, document: {v}"
             for k, v in actual.items() if k in fm and fm[k].strip() != str(v)]
    r.check("FM", "frontmatter counts match the document", drift)
    r.note(f"{unit} · sections written {written} of {len(want)} · not established {not_est} "
           f"· sources cited {len(urls)} · acquire lines {owed}"
           + (f" ({len(closed)} closed)" if closed else ""))
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
