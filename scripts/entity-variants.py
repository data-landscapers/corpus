#!/usr/bin/env python3
r"""entity-variants.py — one body under two slugs, found by the slug rather than the prose.

Housekeeping job 116, strategic review 4 register R47. `CLAUDE.md` -> *Entities* makes a tag
a terminal state with no page behind it, so the whole value of a slug is that grepping it
finds everything — which a split slug defeats **silently**, with no lint firing and nothing
on any page looking wrong. Lint #36 counts slugs with no referent and will not catch these:
both variants have one.

**This is the second of two derivations, and it exists because the first has a floor.**
`prepared/job-105/entity-fragments.csv` groups slugs by the display name `entity-names.csv`
reads out of the prose, and a pair whose two sides are written *African Development Bank*
and *African Development Bank Group* lands in two groups and reports nothing — which is how
`afdb` against `african-development-bank`, 18 records against 378, was invisible to it
(`notes-for-corpus` 36, and R44 found it by grepping instead). This groups on the **slug**,
so it sees exactly what a display name cannot.

Job 116 names the three normalisations and all three are here:

- **strip `-{country}` suffixes** — the country name, its ISO3 code, its adjectival forms
  and the French spellings the vault uses (`mauritanie`, `maroc`, `tchad`).
- **fold French and English stems** — `ministere`/`ministry`, `banque`/`bank`,
  `numerique`/`digital`, so `ministere-education-mauritanie` reaches
  `ministry-of-education-mauritania`.
- **fold an initialism against its expansion** — `cbn` against `central-bank-of-nigeria`.

**The dominant place is what makes any of it safe.** Stripping the country from
`ministry-of-finance-ghana` and `ministry-of-finance-sudan` leaves the same stem and they
are two different ministries; requiring both sides to share a dominant place separates
them. Without it the first test returns 783 groups, most of them `government-of-*` and
`mtn-*`; with it, 434, and the head of the list is genuine. The same constraint is what
keeps the abbreviation test from pairing `ncc` with `npf-national-cybercrime-centre`.

**The abbreviation test consumes every token or it fails.** `afdb` over
`african-development-bank` takes `af`, `d`, `b` — a non-empty prefix of each token in
order. `afcfta` over `afcfta-secretariat` leaves `secretariat` unaccounted for and is
refused, which is right: a secretariat is not its parent body. That single rule is the
difference between 123 candidate pairs and 1,312.

**Nothing here rules anything.** R44 ruled the convention for the general case — *the
most-used slug wins, per entity* — so what this produces is the set that ruling applies to,
with the cost of applying it per group. The instrument is `entities-remap.py`, which takes
a group's slugs as its map.

Usage:
  python entity-variants.py                          # the table, to stdout
  python entity-variants.py --csv entity-variants.csv
  python entity-variants.py --known entity-fragments.csv   # mark what the floor already has
  python entity-variants.py --min-records 5          # the head of the list

Exit: 0 no candidate group, 1 groups found, 2 the index or a lookup is missing.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import sys
import unicodedata

# Dropped before stemming: list punctuation words that carry no identity. `national` is
# deliberately **not** here — it is what distinguishes a national body from a private one.
STOP = {"of", "the", "and", "for", "de", "la", "du", "des", "le", "les", "et", "a"}
# French stems the vault writes beside their English counterparts. Small and hand-checked:
# a generous map folds two different bodies together, and the place constraint cannot help
# when both are in the same country.
FR_EN = {
    "ministere": "ministry", "ministeres": "ministry", "banque": "bank",
    "centrale": "central", "agence": "agency", "autorite": "authority",
    "nationale": "national", "direction": "directorate", "generale": "general",
    "conseil": "council", "societe": "company", "institut": "institute",
    "numerique": "digital", "telecommunications": "telecom",
    "telecommunication": "telecom", "telecoms": "telecom", "postes": "post",
    "poste": "post", "sante": "health", "finances": "finance", "economie": "economy",
    "developpement": "development", "regulation": "regulatory", "office": "office",
}
# French and local spellings of country names the vault uses, which `countries.csv` has
# only in English. **Each carries its ISO3 and that is the point**: an unmapped spelling
# strips to nothing and claims no country, so `ministere-justice-mauritanie` and
# `ministere-justice-maroc` reach the same stem, claim nothing, and merge — two justice
# ministries in two countries, reported as one body.
EXTRA_COUNTRY = {"mauritanie": "MRT", "ivoire": "CIV", "divoire": "CIV", "maroc": "MAR",
                 "guinee": "GIN", "tchad": "TCD", "egypte": "EGY", "algerie": "DZA",
                 "tunisie": "TUN", "rdc": "COD", "senegal": "SEN", "benin": "BEN",
                 "cameroun": "CMR", "afrique": "XAF"}
# Multi-word spellings, matched as phrases for the reason the English ones are.
EXTRA_PHRASE = {("cabo", "verde"): "CPV", ("cote", "divoire"): "CIV",
                ("republique", "centrafricaine"): "CAF"}
ABBR_MIN, ABBR_MAX = 2, 8
CSV_COLS = ["group", "test", "confidence", "place", "slugs", "keep", "keep_records",
            "variants", "variant_records", "files_to_rewrite", "raw", "wiki", "displays",
            "in_entity_fragments"]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def slugify(s):
    s = unicodedata.normalize("NFKD", str(s).lower().replace("'", "").replace("’", ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def country_tokens(root):
    """(phrases, tokens, iso_of) — how a country may be written inside an entity slug.

    **A word that is merely part of a country's name is not a country token.** Taking the
    long words out of *Central African Republic* makes `central` and `african` country
    tokens, and then `central-bank-mauritania` stems to `bank` and
    `african-development-bank` claims to be about the Central African Republic. Both are
    wrong and both were live before this was split in two.

    So a multi-word name is matched **as a phrase** — `south-africa`, `sierra-leone`,
    `cote-divoire` — and only a name that is one word, its ISO3 code, or an adjectival
    built from the whole of a one-word name is a token that can be dropped on its own.
    """
    phrases, tokens, iso_of = dict(EXTRA_PHRASE), dict(EXTRA_COUNTRY), dict(EXTRA_COUNTRY)
    path = os.path.join(root, "lookups", "countries.csv")
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            iso = (row.get("iso-3") or "").strip().lower()
            if not iso:
                continue
            name = slugify(row.get("country-name") or "")
            parts = name.split("-")
            forms = {iso}
            if len(parts) == 1 and len(name) > 3:
                forms.add(name)
                for suf in ("n", "an", "ian", "ese", "aise", "ais", "ien", "ienne"):
                    forms.add(name.rstrip("a") + suf)
                    forms.add(name + suf)
            elif len(parts) > 1:
                phrases.setdefault(tuple(parts), iso.upper())
            for f in forms:
                # First writer wins: a token two countries could claim names neither
                # definitively, and a wrong claim splits a group that belongs together.
                tokens.setdefault(f, "")
                iso_of.setdefault(f, iso.upper())
    for f, iso in list(iso_of.items()):
        tokens[f] = iso
    return phrases, set(tokens), iso_of


def usage(index_dir):
    """(records per slug, places per slug, files per slug) over every indexed Markdown."""
    use, places, files = collections.Counter(), collections.defaultdict(
        collections.Counter), collections.defaultdict(set)
    with open(os.path.join(index_dir, "files.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row["d"].get("ext") != ".md":
                continue
            fm = row["fm"] or {}
            value = fm.get("entities")
            for item in (value if isinstance(value, list) else [value] if value else []):
                slug = str(item).strip()
                if not slug:
                    continue
                use[slug] += 1
                files[slug].add(row["path"])
                for place in (fm.get("places") or []):
                    places[slug][str(place)] += 1
    return use, places, files


def strip_country(slug, phrases, ctok, iso_of):
    """(remaining tokens, countries named). Phrases go first, then single tokens."""
    toks, countries = slug.split("-"), set()
    out, i = [], 0
    while i < len(toks):
        hit = None
        for span in (3, 2):
            if tuple(toks[i:i + span]) in phrases:
                hit = (span, phrases[tuple(toks[i:i + span])])
                break
        if hit:
            countries.add(hit[1])
            i += hit[0]
            continue
        if toks[i] in ctok:
            if iso_of.get(toks[i]):
                countries.add(iso_of[toks[i]])
            i += 1
            continue
        out.append(toks[i])
        i += 1
    return out, countries


def stem(slug, phrases, ctok, iso_of):
    """(stem, countries named) — the slug with country, stopwords and language removed.

    Sorted, because `ghana-ministry-of-finance` and `ministry-of-finance-ghana` are one
    body written two ways round and a positional key would miss them. The countries are
    returned rather than discarded: which country was taken out is the only thing that
    separates two national programmes whose stems are identical.
    """
    toks, countries = strip_country(slug, phrases, ctok, iso_of)
    toks = [FR_EN.get(t, t) for t in toks if t not in STOP]
    return "-".join(sorted(toks)), countries


def is_abbreviation(short, long_slug):
    """`short` is a non-empty prefix of **every** token of `long_slug`, in order.

    This is the whole precision of the test. Allowing a token to contribute nothing turns
    `ncc` into an abbreviation of `npf-national-cybercrime-centre`, and turns every
    `parent-child` slug into an abbreviation of its parent.
    """
    toks = [t for t in long_slug.split("-") if t not in STOP]
    if len(toks) < 2:
        return False
    i = 0
    for k, tok in enumerate(toks):
        remaining = len(toks) - k
        if i >= len(short) or short[i] != tok[0]:
            return False
        j = 0
        # Greedy, but never eat the letters the tokens still to come will need.
        while (i < len(short) and j < len(tok) and short[i] == tok[j]
               and len(short) - i >= remaining):
            i += 1
            j += 1
        if j == 0:
            return False
    return i == len(short)


def groups(use, places, phrases, ctok, iso_of):
    """[(test, place, {slugs})] — candidate variant sets. **The two tests never chain.**

    A union across tests is how two correct groups become one wrong one: `sec-nigeria` and
    `nigeria-sec` are a stem pair, `nigerian-immigration-service` and `nis` are an
    abbreviation pair, and a union-find that shares a member between them reports all five
    slugs as one body. So a stem group is a stem group and an abbreviation pair is a pair,
    and a slug appearing in both is reported twice — which is a question for the reader
    rather than an answer invented for them.

    **A stem group's members must name the same country or none.** Stripping the country
    from `financial-sector-deepening-uganda` and `financial-sector-deepening-kenya` leaves
    one stem, and a dominant place of XAF on both defeats the place constraint; requiring
    the *stripped* country tokens to agree separates them, because the whole difference
    between those two slugs is the token that was removed.
    """
    def dominant(slug):
        return places[slug].most_common(1)[0][0] if places[slug] else ""

    out = []
    by_stem = collections.defaultdict(list)
    for slug in use:
        key, countries = stem(slug, phrases, ctok, iso_of)
        if key:
            by_stem[(key, frozenset(countries), dominant(slug))].append(slug)
    # Merge the keys that differ only by naming no country: `ncc` against `ncc-nigeria`.
    merged = collections.defaultdict(list)
    for (key, countries, place), members in by_stem.items():
        merged[(key, place)].append((countries, members))
    for (key, place), buckets in merged.items():
        named = [b for b in buckets if b[0]]
        unnamed = [b for b in buckets if not b[0]]
        for countries, members in named:
            group = list(members) + [s for _, ms in unnamed for s in ms]
            if len(group) > 1:
                out.append(("stem", place, set(group)))
        if not named and unnamed:
            group = [s for _, ms in unnamed for s in ms]
            if len(group) > 1:
                out.append(("stem", place, set(group)))

    # **The candidate is the slug with its country taken off**, not the slug. `bcm` is
    # Banque Centrale *de Mauritanie*, so the `m` comes from the country and the
    # abbreviation only resolves against the full long slug — while the short side is
    # itself written `bcm-mauritanie`. Matching the stripped short form against the
    # unstripped long one is what reaches that pair, and it is job 116's own example.
    by_place = collections.defaultdict(list)
    for slug in use:
        if "-" in slug:
            by_place[dominant(slug)].append(slug)
    for slug in sorted(use):
        short = strip_country(slug, phrases, ctok, iso_of)[0]
        if len(short) != 1 or not (ABBR_MIN <= len(short[0]) <= ABBR_MAX):
            continue
        for long_slug in by_place.get(dominant(slug), ()):
            if long_slug != slug and is_abbreviation(short[0], long_slug):
                out.append(("abbreviation", dominant(slug), {slug, long_slug}))
    # One group found by both tests is one group, not two rows. Identical member sets
    # collapse and carry both test names; **sets that merely overlap do not**, which is
    # the chaining this function exists to avoid.
    merged = {}
    for test, place, members in out:
        key = frozenset(members)
        if key in merged:
            merged[key] = (merged[key][0] | {test}, place, members)
        else:
            merged[key] = ({test}, place, members)
    return [("+".join(sorted(t)), place, members) for t, place, members in merged.values()]


def known_groups(path):
    """Slugs already reported by the display-name derivation, so the new ones show."""
    if not path or not os.path.isfile(path):
        return set()
    seen = set()
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            seen.add((row.get("most_used") or "").strip())
            for part in (row.get("variants") or "").split(";"):
                name = part.split("(")[0].strip()
                if name:
                    seen.add(name)
    return seen


def rows(use, places, files, phrases, ctok, iso_of, names, known):
    out = []
    for test, place, members in groups(use, places, phrases, ctok, iso_of):
        ranked = sorted(members, key=lambda s: (-use[s], s))
        keep, variants = ranked[0], ranked[1:]
        touched = {p for s in variants for p in files[s]}
        displays = sorted({names.get(s, "") for s in ranked if names.get(s)})
        # **The stem test earns trust the abbreviation test does not.** A shared stem after
        # the country, the language and the stopwords come out is strong evidence of one
        # body; a short slug that happens to prefix another's tokens is not — `actis`
        # abbreviates `action-sa`, and Actis is an investor while ActionSA is a party. So
        # an abbreviation-only group whose two sides carry *different* display names read
        # from the prose is marked for a look rather than presented as a finding.
        confidence = ("check" if test == "abbreviation" and len(displays) > 1 else "high")
        out.append({
            "group": 0, "test": test, "confidence": confidence, "place": place,
            "slugs": len(ranked), "keep": keep, "keep_records": use[keep],
            "variants": "; ".join("%s(%d)" % (s, use[s]) for s in variants),
            "variant_records": sum(use[s] for s in variants),
            "files_to_rewrite": len(touched),
            "raw": sum(1 for p in touched if p.startswith("raw/")),
            "wiki": sum(1 for p in touched if p.startswith("wiki/")),
            "displays": " | ".join(displays),
            # A group every slug of which the floor already reports is one jobs 121 and 122
            # are already scoped on; anything else is new work found by the slug.
            "in_entity_fragments": "yes" if all(s in known for s in ranked) else "no",
        })
    out.sort(key=lambda r: (-r["files_to_rewrite"], r["keep"]))
    for n, row in enumerate(out, 1):
        row["group"] = n
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the repository root (default: cwd)")
    ap.add_argument("--index", default=None, help="an index/ (default: <root>/index)")
    ap.add_argument("--names", default=None,
                    help="entity-names.csv (default: Corpus's own, if it is there)")
    ap.add_argument("--known", default=None,
                    help="entity-fragments.csv, to mark what the display-name cut has")
    ap.add_argument("--min-records", type=int, default=0,
                    help="only groups whose variants hold this many records")
    ap.add_argument("--csv", default=None, help="write the table here")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    index_dir = args.index or os.path.join(root, "index")
    if not os.path.isfile(os.path.join(index_dir, "files.jsonl")):
        print("no files.jsonl under %s -- build the index first" % index_dir, file=sys.stderr)
        return 2
    if not os.path.isfile(os.path.join(root, "lookups", "countries.csv")):
        print("no lookups/countries.csv under %s" % root, file=sys.stderr)
        return 2

    # `realpath`, not `abspath`: `scripts/` is a junction in the workroot, so an unresolved
    # parent lands on `scripts/.workroot/lookups`, which is OSINT's.
    default_names = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                 "lookups", "entity-names.csv")
    names = {}
    path = args.names or default_names
    if os.path.isfile(path):
        with open(path, encoding="utf-8-sig", newline="") as fh:
            names = {r["slug"]: r.get("display", "") for r in csv.DictReader(fh)}

    use, places, files = usage(index_dir)
    phrases, ctok, iso_of = country_tokens(root)
    found = [r for r in rows(use, places, files, phrases, ctok, iso_of, names,
                             known_groups(args.known))
             if r["variant_records"] >= args.min_records]

    new = [r for r in found if r["in_entity_fragments"] == "no"]
    print("%d slug(s) in use, %d candidate group(s), %d file(s) to rewrite"
          % (len(use), len(found), sum(r["files_to_rewrite"] for r in found)))
    print("   found by the stem test        %d" % sum(1 for r in found if "stem" in r["test"]))
    print("   found by the abbreviation test %d"
          % sum(1 for r in found if "abbreviation" in r["test"]))
    print("   **not** in the display-name cut %d" % len(new))
    print("   marked `check` (abbreviation, display names disagree) %d"
          % sum(1 for r in found if r["confidence"] == "check"))
    print()
    for r in found[:30]:
        print("%3d  %-5s %-13s keep %-34s %s" % (r["group"], r["place"], r["test"],
                                                 "%s(%d)" % (r["keep"], r["keep_records"]),
                                                 r["variants"][:70]))

    if args.csv:
        with open(args.csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=CSV_COLS)
            w.writeheader()
            w.writerows(found)
        print("\n%d row(s) -> %s" % (len(found), args.csv))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
