#!/usr/bin/env python3
r"""test_entity_variants.py — what may be merged, and the four ways it must not be.

    python scripts/test_entity_variants.py

`entity-variants.py` proposes which entity slugs name one body (housekeeping job 116). A
false pair costs a wrong merge and a tag that no longer means what it said, so the tests
are mostly about what it refuses:

- **A word inside a country's name is not a country.** Taking `central` and `african` out
  of slugs because *Central African Republic* contains them makes `central-bank-mauritania`
  stem to `bank` and hands `african-development-bank` to the wrong country. Multi-word
  names match as phrases.
- **A shared stem is not enough.** `ministry-of-finance-ghana` and
  `ministry-of-finance-sudan` have one stem and are two ministries; the country taken out
  has to agree, and so does the dominant place.
- **An abbreviation must account for every token.** `afcfta` abbreviates
  `afcfta-secretariat` on a lax test, and a secretariat is not its parent body.
- **The two tests must not chain.** A union that shares one member across tests reports
  five slugs as one body; groups merge only when their members are identical.

And one thing about the report rather than the set: **`check` counted as 0 must not be
printed where no display name could be read** (`notes-for-corpus` 38). `entity-names.csv`
is Corpus's, so a run in OSINT's tree finds none at the default path, every abbreviation
group scores `high`, and a bare `0` reads as *nothing disagrees* when it means *nothing was
compared* -- which is the difference between 55 groups looked at and 55 merged unseen.
"""
from __future__ import annotations

import collections
import importlib.util
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "entity_variants", Path(__file__).resolve().parent / "entity-variants.py")
ev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ev)

fails = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"        got  {got!r}\n        want {want!r}")
        fails.append(name)


COUNTRIES = ("iso-3,country-name,Region\n"
             "NGA,Nigeria,XWA\nGHA,Ghana,XWA\nSDN,Sudan,XAF\nMRT,Mauritania,XWA\n"
             "CAF,Central African Republic,XCA\nZAF,South Africa,XSA\nXAF,Africa (continental),XGL\n")


def lookups(tmp):
    root = Path(tmp)
    (root / "lookups").mkdir(parents=True)
    (root / "lookups" / "countries.csv").write_text(COUNTRIES, encoding="utf-8")
    return ev.country_tokens(str(root))


# -- the country tokens ----------------------------------------------------

print("what counts as a country inside a slug")
with tempfile.TemporaryDirectory() as tmp:
    phrases, ctok, iso_of = lookups(tmp)
    check("a one-word name is a token", "nigeria" in ctok, True)
    check("its adjectival is too", "nigerian" in ctok, True)
    check("a multi-word name is a phrase, not its words",
          ("central" in ctok, "african" in ctok, ("central", "african", "republic") in phrases),
          (False, False, True))
    check("`central-bank-mauritania` keeps its `central`",
          ev.stem("central-bank-mauritania", phrases, ctok, iso_of),
          ("bank-central", {"MRT"}))
    # `african` is not a country either: XAF is written "Africa (continental)", which is
    # a phrase, so the adjective stays in the stem where it belongs.
    check("`african-development-bank` claims no country and keeps its adjective",
          ev.stem("african-development-bank", phrases, ctok, iso_of),
          ("african-bank-development", set()))
    check("a phrase comes off whole",
          ev.stem("mtn-south-africa", phrases, ctok, iso_of), ("mtn", {"ZAF"}))
    check("French folds to English",
          ev.stem("ministere-education-mauritanie", phrases, ctok, iso_of)[0],
          ev.stem("ministry-of-education-mauritania", phrases, ctok, iso_of)[0])
    check("word order does not matter",
          ev.stem("ghana-ministry-of-finance", phrases, ctok, iso_of),
          ev.stem("ministry-of-finance-ghana", phrases, ctok, iso_of))


# -- the abbreviation test -------------------------------------------------

print("\nan abbreviation accounts for every token")
for short, long_slug, want in (
        ("afdb", "african-development-bank", True),
        ("ncc", "nigerian-communications-commission", True),
        ("cbn", "central-bank-of-nigeria", True),
        ("bcm", "banque-centrale-de-mauritanie", True),
        ("afcfta", "afcfta-secretariat", False),
        ("ncc", "npf-national-cybercrime-centre", False),
        ("mtn", "mtn-group", False),
        ("abc", "alpha", False),
):
    check("%-8s <- %-34s" % (short, long_slug),
          ev.is_abbreviation(short, long_slug), want)


# -- the grouping ----------------------------------------------------------

print("\nwhat may be grouped")
with tempfile.TemporaryDirectory() as tmp:
    phrases, ctok, iso_of = lookups(tmp)
    use = collections.Counter({
        "ministry-of-finance-ghana": 10, "ghana-ministry-of-finance": 3,
        "ministry-of-finance-sudan": 8,
        "ncc": 20, "ncc-nigeria": 4, "nigerian-communications-commission": 2,
        "sec-nigeria": 9, "nigeria-sec": 2,
        "nigerian-immigration-service": 5, "nis": 1,
    })
    def place_of(slug):
        if slug.endswith("sudan"):
            return "SDN"
        return "GHA" if "ghana" in slug else "NGA"

    places = collections.defaultdict(collections.Counter)
    for slug in use:
        places[slug][place_of(slug)] = use[slug]
    got = {frozenset(m): t for t, _, m in ev.groups(use, places, phrases, ctok, iso_of)}

    check("one ministry written two ways round is a group",
          frozenset({"ministry-of-finance-ghana", "ghana-ministry-of-finance"}) in got, True)
    check("two countries' ministries are not",
          any("ministry-of-finance-sudan" in g for g in got), False)
    # **The NCC arrives as two overlapping rows, not one**, and that is the price of not
    # chaining: `ncc`/`ncc-nigeria` share a stem, `ncc`/`nigerian-communications-commission`
    # are an abbreviation, and joining them through their shared member is the mechanism
    # that also produces the wrong five-slug group below. Overlap is left for the reader.
    check("the NCC arrives as two overlapping pairs",
          sorted(sorted(g) for g in got if "ncc" in g),
          [["ncc", "ncc-nigeria"], ["ncc", "nigerian-communications-commission"]])
    check("a stem pair and an abbreviation pair are never merged into one group",
          max(len(g) for g in got), 2)
    check("the stem pair is right",
          frozenset({"sec-nigeria", "nigeria-sec"}) in got, True)
    # **A known false positive, asserted rather than hidden.** `nis` abbreviates
    # `nigeria-sec` as `ni` + `s`, and the two are different agencies. Nothing in the slugs
    # separates them; what does is the display name read from the prose, which is why an
    # abbreviation-only group whose displays disagree is marked `check` rather than
    # presented as a finding.
    check("an abbreviation can still pair two different bodies",
          frozenset({"nigeria-sec", "nis"}) in got, True)
    check("  …and such a group is marked for a look when the displays disagree",
          [r["confidence"] for r in ev.rows(
              use, places, {s: {"x"} for s in use}, phrases, ctok, iso_of,
              {"nigeria-sec": "Securities and Exchange Commission",
               "nis": "Nigeria Immigration Service"}, set())
           if r["keep"] in ("nigeria-sec", "nis") and "nis" in r["variants"] + r["keep"]
           and "sec" in r["variants"] + r["keep"]], ["check"])

# -- the report, where the absence of display names is the finding ------------

print("\nwhat the run says when it has no display names")

# The fact the output must not misreport: with no names read, `check` cannot be reached,
# so a count of it is a statement about the input rather than about the corpus.
_u = collections.Counter({"african-development-bank": 9, "afdb": 2})
_p = {"african-development-bank": collections.Counter({"NGA": 9}),
      "afdb": collections.Counter({"NGA": 2})}
_ph, _ct, _iso = lookups(tempfile.mkdtemp(prefix="ev-names-"))
check("with no display names nothing can be marked `check`",
      {r["confidence"] for r in ev.rows(_u, _p, {s: {"x"} for s in _u}, _ph, _ct, _iso,
                                        {}, set())
       if r["test"] == "abbreviation"},
      {"high"})

_tmp = Path(tempfile.mkdtemp(prefix="ev-main-"))
try:
    (_tmp / "lookups").mkdir(parents=True)
    (_tmp / "lookups" / "countries.csv").write_text(COUNTRIES, encoding="utf-8")
    (_tmp / "index").mkdir()
    with io.open(_tmp / "index" / "files.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for i, slug in [(n, "african-development-bank") for n in range(9)] + \
                       [(n, "afdb") for n in range(9, 11)]:
            fh.write(json.dumps({"path": "raw/2026/r%02d.md" % i, "d": {"ext": ".md"},
                                 "fm": {"entities": [slug], "places": ["NGA"]}}) + "\n")
    names_csv = _tmp / "entity-names.csv"
    names_csv.write_text("slug,display\nafdb,AfDB\n"
                         "african-development-bank,African Development Bank Group\n",
                         encoding="utf-8")

    def run(*argv):
        out = io.StringIO()
        keep, sys.stdout = sys.stdout, out
        try:
            return ev.main(list(argv)), out.getvalue()
        finally:
            sys.stdout = keep

    _rc, missing = run("--root", str(_tmp), "--names", str(_tmp / "nope.csv"))
    _rc, present = run("--root", str(_tmp), "--names", str(names_csv))

    check("a run with no names file says so instead of counting",
          ("NOT COMPARED" in missing, "disagree) 0" in missing), (True, False))
    check("and names where it looked", str(_tmp / "nope.csv") in missing, True)
    check("a run with the file counts as before",
          ("NOT COMPARED" in present, "disagree)" in present), (False, True))
finally:
    shutil.rmtree(_tmp, ignore_errors=True)

print()
if fails:
    print("%d FAILED: %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("all checks passed")
