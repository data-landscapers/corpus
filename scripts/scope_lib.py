#!/usr/bin/env python3
r"""
scope_lib.py — the geographic remit, in one place.

    from scope_lib import verdict, in_remit, african_codes, GLOBAL_SOUTH
    verdict(row)   -> "in" | "unverified" | "unaccounted"
    in_remit(row)  -> True for "in" and "unverified", False for "unaccounted"

**The remit is Africa, and it is narrow** *(Bill, 2026-08-20)*. Non-African material is
admissible in exactly two cases and no others:

  1. **a sovereignty issue** filing under one of the closed `geopol.*` slugs — great-power
     positioning, rivalry and strategic influence (`taxonomy.md` → *Geopolitics*, curator
     ruling 2026-07-20); or
  2. **material treating the global south generally**, which includes Africa inside its own
     subject — the `XGL` place, labelled *Global/Developing Countries* in `countries.csv`.

Everything else datelined outside Africa is out. A single non-African country's domestic
story is out however transferable the lesson looks: Japan's training-data rule, Korea's
teen-algorithm debate and India's market-regulator AI rules are all digital governance, and
none of them is this base's subject.

**Why this is a library and not two copies of an `if`.** It has two callers with different
jobs — `lint-scope.py`, which reports what arrived, and `bulletin.py`, which decides what is
published — and a rule stated twice is a rule that will eventually be stated two ways.
`CLAUDE.md` makes the same point about the shared assets: a copy is not sharing unless
something notices when it goes stale, and here nothing would. The one that would drift is the
bulletin's, because it is the one under pressure to make an exception.

**The three verdicts, and why the middle one exists.**

  - **in** — an African place, or a `geopol.*` tag. Mechanical.
  - **unverified** — placed `XGL` with no `geopol.*` tag. `XGL` *means* the global south, so
    such a record is admissible if it earns the code — and many do not: a Türkiye national AI
    plan, a Spanish press lawsuit and an Indian data-protection explainer all carry `XGL` in
    the base today. Whether a given one earns it is a reading of the body, which no rule here
    can do. **It counts as in remit**, because the alternative is a filter silently dropping
    the ITU's connectivity report alongside them.
  - **unaccounted** — none of the above. The record has not accounted for its geography.
    Under the rule there is no route by which it is in.

**`unaccounted` is not the same as "out of scope", and the distinction is load-bearing.** The
first run of the lint put Jumia's capital raise, Flutterwave's correspondent accounts and MTN
Bayobab's management appointment in this bucket — African stories whose `places` field is
simply empty. So for a lint the bucket is a question (delete it, place it, or code it `XGL`,
all of them OSINT's call), while for the bulletin it is a decision: a record that does not say
where it belongs is not published, and the repair is upstream.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
COUNTRIES = CORPUS / "outputs" / "vocab" / "countries.csv"

GLOBAL_SOUTH = "XGL"

_AFRICAN: set[str] | None = None


def african_codes() -> set[str]:
    """Every place code the vocabulary holds except `XGL`.

    `countries.csv` is the authority and carries the regions as well as the states — `XAF`
    Africa, `XSS` Sub-Saharan Africa and the five sub-regions — so this needs no hardcoded
    list and grows with the vocabulary rather than against it. `XGL`'s own region cell is
    empty because it sits above `XAF`, which is what marks it out as the one code in the file
    that is not a place in Africa.

    Cached: the bulletin asks this once per record over a whole catalogue."""
    global _AFRICAN
    if _AFRICAN is None:
        codes = set()
        with io.open(COUNTRIES, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                code = (row.get("iso-3") or "").strip()
                if code and code != GLOBAL_SOUTH:
                    codes.add(code)
        _AFRICAN = codes
    return _AFRICAN


def facets(value: str) -> list[str]:
    """A catalogue facet cell — `;`-separated, as `build-catalogue.py` writes it."""
    return [v.strip() for v in (value or "").split(";") if v.strip()]


def verdict(row: dict) -> str:
    """`in`, `unverified` or `unaccounted` for one catalogue row."""
    places = facets(row.get("places", ""))
    african = african_codes()
    if any(p in african for p in places):
        return "in"
    if any(t.startswith("geopol.") for t in facets(row.get("topics", ""))):
        return "in"
    if GLOBAL_SOUTH in places:
        return "unverified"
    return "unaccounted"


def in_remit(row: dict) -> bool:
    """Publishable under the remit — `in` or `unverified`, never `unaccounted`."""
    return verdict(row) != "unaccounted"
