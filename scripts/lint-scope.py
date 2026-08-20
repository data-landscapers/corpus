#!/usr/bin/env python3
r"""
lint-scope.py — is anything in the catalogue outside the geographic remit?

**The remit is Africa, and it is narrow** *(Bill, 2026-08-20)*. Non-African material
is admissible in exactly two cases and no others:

  1. **a sovereignty issue** that files under one of the closed `geopol.*` slugs —
     great-power positioning, rivalry and strategic influence (`taxonomy.md` →
     *Geopolitics*, curator ruling 2026-07-20); or
  2. **material treating the global south generally**, which includes Africa inside
     its own subject — the `XGL` place, whose vocabulary label is already
     *Global/Developing Countries*.

Everything else datelined outside Africa is out of scope. A single non-African
country's domestic story is out however good it is, and however transferable the
lesson looks: Japan's training-data rule, Korea's teen-algorithm debate and India's
market-regulator AI rules are all digital governance, and none of them is this
base's subject.

**This reports; it never deletes.** The records are OSINT's — `CLAUDE.md` has the
read-only rule and the reasoning — and the catalogue Corpus builds from them is a
derived view, so removing a row here would be papering over the record rather than
correcting it. What this does is make the arrivals visible on the run that admits
them, which is the whole of what Corpus can do about it.

**Three verdicts, and the middle one is the point.**

  - **in** — carries an African place (any code in `countries.csv` other than
    `XGL`), or carries a `geopol.*` tag. Mechanical either way.
  - **unverified** — placed `XGL` with no `geopol.*` tag. `XGL` *means* the global
    south, so the record is admissible if it earns the code, and a great many do
    not: a national AI plan for Türkiye, a Spanish press lawsuit and an Indian data
    protection explainer are all filed `XGL` in the base today. Whether a given one
    earns it is a reading of the body, which a lint cannot do — so it is counted
    and named, not judged.
  - **unaccounted** — no African place, not `XGL`, no `geopol.*` tag. **This is a
    review list and not a delete list**, and the distinction was learned the hard
    way: the first run of this lint put Jumia's capital raise, Flutterwave's
    correspondent accounts and MTN Bayobab's management appointment in the same
    bucket as Thailand's passport and Japan's disclosure rule. Those are African
    stories whose `places` field is simply empty — a tagging defect, where deleting
    the record would lose real material. A third group belongs in neither: the ITU
    Global Connectivity Report and the SubOptic cable programme should carry `XGL`
    and do not. So the bucket says *nothing here accounts for its geography*, which
    is a question, and the answer is one of delete, place it, or code it `XGL`.

**Which is why this reports counts and names rather than proposing an action.** The
mechanical part — has this record accounted for its geography at all — is worth
running every build. The part after it is a reading of the record, and it is
OSINT's, because the record is OSINT's.

`--since` narrows to what arrived recently, on the `ingested` column rather than
`published`, because the question this answers is *what did the last sweep send*
and a 2019 paper ingested last night is a new arrival. With no `--since` it reads
the whole catalogue, which is the backlog view.

Exit: 0 clean · 1 unaccounted records found · 2 the catalogue is missing.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOGUE = ROOT / "outputs" / "catalogue" / "raw-catalogue.csv"
COUNTRIES = ROOT / "outputs" / "vocab" / "countries.csv"

GLOBAL_SOUTH = "XGL"


def african_codes() -> set[str]:
    """Every place code the vocabulary holds except `XGL`.

    `countries.csv` is the authority and carries the regions as well as the states —
    `XAF` Africa, `XSS` Sub-Saharan Africa and the five sub-regions — so this needs
    no hardcoded list and grows with the vocabulary rather than against it. `XGL`'s
    own region cell is empty because it sits above `XAF`, which is what marks it out
    as the one code that is not a place in Africa."""
    codes = set()
    with io.open(COUNTRIES, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            code = (row.get("iso-3") or "").strip()
            if code and code != GLOBAL_SOUTH:
                codes.add(code)
    return codes


def facets(value: str) -> list[str]:
    return [v.strip() for v in (value or "").split(";") if v.strip()]


def verdict(row: dict, african: set[str]) -> str:
    places = facets(row.get("places", ""))
    if any(p in african for p in places):
        return "in"
    if any(t.startswith("geopol.") for t in facets(row.get("topics", ""))):
        return "in"
    if GLOBAL_SOUTH in places:
        return "unverified"
    return "unaccounted"


def classify(since: str | None) -> dict[str, list[dict]]:
    african = african_codes()
    buckets: dict[str, list[dict]] = {"in": [], "unverified": [], "unaccounted": []}
    with io.open(CATALOGUE, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if since and (row.get("ingested") or "").strip() < since:
                continue
            buckets[verdict(row, african)].append(row)
    return buckets


def report(buckets: dict[str, list[dict]], limit: int, since: str | None) -> None:
    total = sum(len(v) for v in buckets.values())
    scope = f" ingested on or after {since}" if since else ""
    print(f"scope lint: {total} record(s){scope} — "
          f"{len(buckets['in'])} in remit, "
          f"{len(buckets['unverified'])} XGL unverified, "
          f"{len(buckets['unaccounted'])} unaccounted for")

    for name, heading in (("unaccounted", "with no African place, no XGL and no geopol.* tag — "
                                          "out of scope, or the place is missing, or it should be XGL"),
                          ("unverified", "placed XGL with no geopol.* tag — admissible only if it "
                                         "treats the developing world generally, which is a reading")):
        rows = buckets[name]
        if not rows:
            continue
        rows.sort(key=lambda r: (r.get("ingested") or "", r.get("published") or ""), reverse=True)
        print(f"\n  {len(rows)} {heading}:")
        for r in rows[:limit]:
            print(f"    {r.get('published','')}  {r.get('slug','')}")
            print(f"        {(r.get('title') or '')[:96]}")
            print(f"        places={facets(r.get('places',''))} topics={facets(r.get('topics',''))}")
        if limit and len(rows) > limit:
            print(f"    … and {len(rows) - limit} more (--list to raise the cap)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", metavar="YYYY-MM-DD",
                    help="only records whose `ingested` date is on or after this")
    ap.add_argument("--list", type=int, default=10, metavar="N",
                    help="how many records to name per bucket (default 10)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    if not CATALOGUE.exists():
        print(f"scope lint: no catalogue at {CATALOGUE} — run stage 2 first", file=sys.stderr)
        return 2

    buckets = classify(args.since)
    if args.json:
        print(json.dumps({k: [r.get("slug") for r in v] for k, v in buckets.items()}, indent=2))
    else:
        report(buckets, args.list, args.since)
    return 1 if buckets["unaccounted"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
