#!/usr/bin/env python3
r"""build-entity-names.py — display names for OSINT's entity slugs.

    python scripts/build-entity-names.py           write lookups/entity-names.csv
    python scripts/build-entity-names.py --check    report coverage, write nothing
    python scripts/build-entity-names.py --sample N show N derivations and stop

Stage 2 of `documentation/catalogue-search.md`. The catalogue can filter by entity
tag, but a tag is a slug — `bf-ministry-digital-transition`, `nira-uganda` — and a
slug is not a name. This derives one, from the corpus itself.

**Corpus owns this, and asks nothing of OSINT.** The precedent is `taxonomy_lib`:
*"the slugs are still OSINT's; only how they are written is decided here"* (Bill,
2026-08-19). It is load-bearing in the other direction too — OSINT retired entity
pages in R11 on the reasoning that a tag is a terminal state, so there is no
registry over there to ask for, and Corpus cannot write to OSINT in any case.

**The derivation is an intersection of two things Corpus already has**: the entity
tags on each source, and the names occurring in that source's prose (`names_lib`,
which the search index is built from). For a slug, look only at the bodies of the
sources that tag it, and ask which name-shaped run best accounts for the slug.

Scoring, and the one failure mode worth naming. A first pass scored on plain token
overlap and got about two-thirds right; the third that failed did so in a single
patterned way — a slug suffixed with its country matched the *country* and nothing
else, so `pura-gambia` derived "The Gambia" and `sec-nigeria` derived "Nigeria".
Place tokens are therefore stripped before scoring, and a candidate must account for
the slug's **distinguishing** tokens. The place is still used, as a tie-break, so
that `bank-of-namibia` prefers "Bank of Namibia" over "Bank".

Acronyms are handled explicitly and are where this earns its keep: where a slug token
is the initials of a candidate, that candidate wins outright. `noa` -> "National
Orientation Agency" is not something any amount of prettifying the slug could reach.

**Every row records how it was decided.** `basis` is `acronym`, `full`, `partial` or
`hand`, and `sources` is how many of the slug's sources carried the winning name. A
row written by hand is never overwritten — this file is meant to be corrected, and a
deriver that discards the corrections is a deriver nobody will correct twice.

Runs from `scripts/.workroot/`, like every reader of the vault. **Output goes to
Corpus's own `lookups/`, resolved from this file rather than from the working root**
— under the workroot, `lookups/` is *OSINT's*, and a relative write would land in
another repository. `taxonomy_lib` carries the same warning for the same reason.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault_lib as V                                                    # noqa: E402
from names_lib import LEGAL, KEYSTOP, body, clean, names_in, tokens, initials  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# `.resolve()` because `scripts/` is itself a junction in the workroot.
CORPUS = Path(__file__).resolve().parent.parent
OUT = CORPUS / "lookups" / "entity-names.csv"
VOCAB = CORPUS / "outputs" / "vocab" / "countries.csv"
CATALOGUE = CORPUS / "outputs" / "catalogue" / "raw-catalogue.json"
RAW = Path(os.environ.get("CORPUS_RAW") or (Path(V.ROOT) / "raw"))

MAX_SOURCES = 12        # bodies read per slug; more adds cost, not accuracy
MIN_COVER = 0.60        # share of distinguishing tokens a candidate must account for
COLS = ["slug", "display", "basis", "sources"]


def places() -> set[str]:
    """Every token that names a place — country names, their words, and ISO codes.

    Stripped before scoring because a country suffix is the *least* distinguishing
    part of a slug and was winning on its own.
    """
    out = set()
    if not VOCAB.exists():
        return out
    with open(VOCAB, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            # Every ISO column, not just iso-3: two-letter codes appear in slugs as
            # prefixes (`bf-ministry-...`) and are exactly the tokens most likely to
            # be mistaken for an acronym of the country's own name.
            for k, v in r.items():
                if k and "iso" in k.lower() and (v or "").strip():
                    out.add(v.strip().lower())
            for t in tokens((r.get("country-name") or "").strip()):
                out.add(t)
    # Slugs write these forms that the vocabulary does not.
    out |= {"drc", "rdc", "civ", "cote", "divoire", "ivoire", "uk", "usa", "us", "eu",
            "africa", "african", "afrique", "sahel", "ecowas", "sadc", "eac", "au"}
    return out


def distinguishing(slug: str, place_tokens: set[str]) -> list[str]:
    """The slug's tokens that actually identify it — place and legal form removed.

    Where a slug is *only* a place (`african-union` is not, `algeria` is), there is
    nothing else to go on and the place tokens are all it has.
    """
    toks = [t for t in slug.split("-") if len(t) > 1]
    core = [t for t in toks if t not in place_tokens and t not in LEGAL and t not in KEYSTOP]
    return core or toks


def score(slug: str, cand: str, place_tokens: set[str]):
    """(rank, cover, penalty) for a candidate name, or None if it cannot be the slug.

    Rank 2 is an acronym expansion, 1 accounts for every distinguishing token, 0 for
    most of them. The penalty is how much of the candidate the slug does *not*
    explain, so that between two names that both fit, the tighter one wins.
    """
    core = distinguishing(slug, place_tokens)
    ct = tokens(cand)
    if not ct or not core:
        return None
    ctset = set(ct)
    content = [w for w in ct if w not in KEYSTOP]
    hit = sum(1 for t in core if t in ctset)
    cover = hit / len(core)
    extra = len(content) - hit          # how much of the candidate the slug cannot explain

    # Acronym: a slug token spelled by the candidate's initials. The strongest signal
    # there is — an expansion is the one thing prettifying a slug could never reach.
    ini = initials(content)
    if len(ini) >= 2 and any(t == ini for t in core):
        # ...but not where the expansion is *only* a place. `bf` is the initials of
        # "Burkina Faso", which made `bf-ministry-digital-transition` derive the
        # country and drop the ministry — the country-suffix bug in a new costume.
        if not all(w in place_tokens for w in content):
            # Rank acronyms against each other on how much of the *rest* of the slug
            # they also account for, so `malawi-ministry-of-ict` prefers an expansion
            # that keeps the ministry over one that is only the three letters.
            rest = [t for t in core if t != ini]
            oc = (sum(1 for t in rest if t in ctset) / len(rest)) if rest else 1.0
            return (2, oc, -extra)

    if cover < MIN_COVER:
        return None
    # Tie-break on the place: `bank-of-namibia` should prefer "Bank of Namibia".
    place_hit = sum(1 for t in slug.split("-") if t in place_tokens and t in ctset)
    return (1 if cover == 1.0 else 0, cover + 0.01 * place_hit, -extra)


def derive(items, place_tokens, only=None):
    by = collections.defaultdict(list)
    for it in items:
        for e in (it.get("entities") or []):
            by[e].append(it.get("path") or "")
    if only:
        by = {k: v for k, v in by.items() if k in only}

    # One read per source file, however many of its tags we are deriving.
    wanted = {p for paths in by.values() for p in paths[:MAX_SOURCES]}
    cache = {}
    for rel in wanted:
        if not rel.startswith("raw/"):
            continue
        fp = RAW / rel[len("raw/"):]
        try:
            cache[rel] = names_in(fp.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            cache[rel] = set()

    out = {}
    for slug, paths in by.items():
        tally = collections.Counter()
        for rel in paths[:MAX_SOURCES]:
            for n in cache.get(rel, ()):
                tally[n] += 1
        best, best_key = None, None
        for cand, seen in tally.items():
            s = score(slug, cand, place_tokens)
            if s is None:
                continue
            # Tightness before popularity: a name the slug fully explains beats a
            # longer one that more sources happen to carry, which is what stopped
            # `electoral-commission-uganda` deriving "ID for All The Electoral
            # Commission of Uganda" — the extraction had run across a heading.
            key = (s[0], s[1], s[2], seen)
            if best_key is None or key > best_key:
                best, best_key = cand, key
        if best is None:
            continue
        rank, _, neg_extra, seen = best_key
        extra = -neg_extra

        # **A thin derivation must be a tight one.** 4,074 of the 6,787 slugs are
        # tagged by exactly one source, so requiring two sources to agree is not a
        # quality bar, it is a 78%-to-25% coverage cut on slugs that can never
        # corroborate by construction. What separates the good single-source
        # derivations from the bad ones is not how often a name was seen but how
        # much of it the slug fails to account for: "Bank of Namibia" explains
        # itself, "Draft ODPC Guidance" and "ID for All The Electoral Commission of
        # Uganda" are extraction runs that crossed a heading. So the allowance for
        # unexplained tokens grows with corroboration, and where nothing clears it
        # the page falls back to the prettified slug — which is straight with the
        # reader, and often better than a confident wrong answer.
        # ...but this never applies to an acronym expansion, where "unexplained
        # tokens" is a meaningless count: an expansion does not contain its own
        # initials, so every word of it is unexplained by construction. Applying it
        # here cost `undp` its "United Nations Development Programme" for the crime
        # of being four words long, while three-word `itu` survived — a threshold
        # doing something entirely unrelated to what it was written for. The
        # initials match is the evidence in that case, and it is stronger than
        # tightness.
        if rank != 2 and extra > (1 if seen < 2 else 3):
            continue
        # An acronym that accounts for **none** of the rest of the slug is never worth
        # more than the slug itself, however many sources carry it. This used to admit
        # one at two sources, and corroboration is the wrong axis: nine sources agreeing
        # that `ai` expands to "Artificial Intelligence" does not make that the name of
        # `au-continental-ai-strategy`, and it collapsed nine unrelated slugs onto one
        # label. Same for `cbn-payments-circular-2026` -> "Central Bank of Nigeria",
        # which named a circular after the bank that issued it. Where the acronym is the
        # whole slug (`itu`, `undp`, `noa`) there is no rest to account for, `oc` is 1.0
        # by construction, and none of this applies.
        if rank == 2 and best_key[1] == 0:
            continue

        # The country-suffix bug's last costume. Rejecting a *place-only acronym
        # expansion* fixed `bf-ministry-digital-transition`, but the same wrong answer
        # arrives at rank 1 and 0 too: `cv-telecom`, `gov-cv` and `techpark-cv` all
        # derived "Cabo Verde". A candidate that is nothing but place tokens names the
        # country, not the thing — unless the slug is only a place, where it is right
        # (`kenya` -> "Kenya"), which is what `distinguishing()` returning `core or toks`
        # already tells us.
        cand_toks = [w for w in tokens(best) if w not in KEYSTOP]
        if (cand_toks and all(w in place_tokens for w in cand_toks)
                and any(t not in place_tokens for t in slug.split("-") if len(t) > 1)):
            continue

        basis = {2: "acronym", 1: "full", 0: "partial"}[rank]
        out[slug] = (clean(best) or best, basis, seen)
    return out


def load_existing() -> dict:
    rows = {}
    if OUT.exists():
        with open(OUT, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                rows[r["slug"]] = (r["display"], r.get("basis") or "", r.get("sources") or "0")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="report coverage, write nothing")
    ap.add_argument("--sample", type=int, metavar="N", help="show N derivations and stop")
    a = ap.parse_args()

    if not CATALOGUE.exists():
        print(f"entity-names: no catalogue at {CATALOGUE} — run build-catalogue.py first")
        return 1
    if not RAW.exists():
        print(f"entity-names: no raw/ at {RAW} — run from scripts/.workroot/, or set CORPUS_RAW")
        return 1

    doc = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    items = doc["items"] if isinstance(doc, dict) and "items" in doc else doc
    place_tokens = places()
    slugs = {e for i in items for e in (i.get("entities") or [])}
    existing = load_existing()
    derived = derive(items, place_tokens)

    if a.sample:
        for slug in sorted(derived)[:a.sample]:
            d, basis, n = derived[slug]
            print(f"  {slug[:44]:46} {basis:8} {n:>3}  {d}")
        return 0

    kept_hand = {s: v for s, v in existing.items() if v[1] == "hand"}
    rows = dict(derived)
    rows.update({s: (v[0], "hand", v[2]) for s, v in kept_hand.items()})

    if a.check:
        print(f"entity-names: {len(rows):,} of {len(slugs):,} slugs named "
              f"({100*len(rows)//max(len(slugs),1)}%), {len(kept_hand)} by hand")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLS)
        for slug in sorted(rows):
            d, basis, n = rows[slug]
            w.writerow([slug, d, basis, n])

    kinds = collections.Counter(v[1] for v in rows.values())
    print(f"entity-names: {len(rows):,} of {len(slugs):,} slugs named "
          f"({100*len(rows)//max(len(slugs),1)}%) -> lookups/entity-names.csv")
    print("  " + ", ".join(f"{k} {n:,}" for k, n in kinds.most_common()))
    print(f"  {len(slugs)-len(rows):,} unnamed — the page falls back to the prettified slug")
    return 0


if __name__ == "__main__":
    sys.exit(main())
