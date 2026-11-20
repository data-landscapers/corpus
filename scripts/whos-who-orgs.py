#!/usr/bin/env python3
r"""whos-who-orgs.py — build `lookups/organisations.csv`, the Who's Who organisations sidecar.

    python scripts/whos-who-orgs.py           rebuild the sidecar, report
    python scripts/whos-who-orgs.py --dry     report only

`documentation/whos-who.md` §4 and §6, stage 2. One row per slug a cached tuple resolves
to (`whos_who_lib.Resolver`). `hand` rows are kept as they stand and never rewritten; an
`auto` row is derived afresh each run, so a slug no tuple reaches any longer drops out.

- **`name`** is *Government of {country}* for a `government-of-*` slug, else
  `entity-names.csv`'s display where that was derived whole (`full`, `acronym`, `hand`).
  Where it is `partial` or missing it is the organisation as the sources wrote it —
  only a form that matches the slug, most frequent first, the longer on a tie, an
  initialism last. A slug no written form matches is left out until a `hand` row names it.
- **`place`** is the one country the slug names, else the dominant place of the
  catalogue sources tagging it.
- **`kind`** is `government` when the slug carries a stem from `whos-who-gov-stems.csv`.
- **A government name that does not contain its country gets `, {country}`.**
- **`canonical_slug`**: two government slugs in one country with one stem, country and
  language folded out, are one body; the more-tagged slug is canonical. Nothing else
  merges here.

Exit 1 when a published government name is shared by two countries or one has no
country to carry — the stage 2 finish line.
"""
from __future__ import annotations

import argparse
import collections
import csv
import re
import sys

import whos_who_lib as W

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WHOLE = {"full", "acronym", "hand"}


def written_name(forms: collections.Counter) -> str:
    def rank(item):
        form, n = item
        acronym = len(form.split()) == 1 and form.isupper()
        return (acronym, -n, -len(form))
    return sorted(forms.items(), key=rank)[0][0]


def _toks(s: str) -> list[str]:
    s = re.sub(r"(?i)\b[ld][’']", " ", s)          # French elision: l’Eau is eau
    toks = W.EV.strip_country(W.DRC.sub("rdc", W.EV.slugify(s)), W.STEM_PHRASES, W.STEM_CTOK, W.ISO_OF)[0]
    return [W.EV.FR_EN.get(t, t) for t in toks if t not in W.EV.STOP and len(t) > 1]


def owns(form: str, slug: str) -> bool:
    """The written form is recognisably the slug's name: at least half the slug's words
    appear in it (compared on their first five letters, after the French-English fold,
    so *Intérieur* meets `interior`), or the slug is the form's initials."""
    st, ft = _toks(slug), _toks(form)
    if not st or not ft:
        return False
    if W.match_strength(form, slug, None):
        return True
    pre = {t[:5] for t in ft}
    hit = sum(1 for t in st if t[:5] in pre)
    if hit * 2 >= len(st) and hit:
        return True
    initials = "".join(t[0] for t in ft)
    return len(st) == 1 and len(st[0]) >= 3 and initials.startswith(st[0])


GOV_OF = ("government", "gouvernement", "governo", "gobierno")


def place_of(slug: str, res, placed: dict[str, str]) -> str:
    """Where the organisation is based (Bill, 2026-11-20: the UK FCDO read as Nigeria).

    1. `org-places.csv`, by hand: international bodies (`XGL`), and foreign governments and
       companies the sources only ever report in Africa.
    2. The one country the slug names, African or foreign (`uk-fcdo`).
    3. The place most of the sources tagging it share; where none holds a majority the body
       works across many countries and its sources cannot say where it is, so it is left
       blank rather than given the country it happened to be reported in most."""
    if slug in placed:
        return placed[slug]
    toks = slug.split("-")
    named = set(W.slug_countries(slug)) | {W.FOREIGN_TOKENS[t] for t in toks if t in W.FOREIGN_TOKENS} \
        | {iso for ph, iso in W.FOREIGN_PHRASES.items() if ph in slug}
    if len(named) == 1:
        return named.pop()
    place = res.place.get(slug, "")
    seen = res.places.get(slug)
    if place and not place.startswith("X") and seen and not named \
            and seen.most_common(1)[0][1] * 2 < sum(seen.values()):
        return ""
    return place


def name_for(slug: str, place: str, display: dict | None, forms: collections.Counter,
             country: dict) -> tuple[str, str]:
    """(name, how). A written form is used only if it is recognisably the slug's own
    name: the model's slug pick is right far more often than its wording is the body's
    name, so *Government of Lesotho* written against `office-of-the-prime-minister-lesotho`
    names the government, not the office."""
    # Only a national government: `gouvernement-provincial-tshopo` is not DR Congo's.
    if slug.split("-")[0] in GOV_OF and place in country and not place.startswith("X") \
            and W.bare_country(slug.replace("-", " ")) == place:
        return f"Government of {country[place]}", "government"
    if display and display["basis"] in WHOLE:
        return display["display"], "display"
    own = collections.Counter({f: n for f, n in forms.items() if owns(f, slug)})
    if own:
        return written_name(own), "written"
    return "", "unnamed"


def names_place(name: str, iso: str, country: str) -> bool:
    f = W.EV.slugify(name)
    toks = f.split("-")
    if any(W.ISO_OF.get(t) == iso for t in toks):
        return True
    if any(f"-{'-'.join(p)}-" in f"-{f}-" for p, i in W.PHRASES.items() if i == iso):
        return True
    return W.EV.slugify(country) in f


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)

    cat, names = W.catalogue(), W.display_names()
    res, stems, country = W.Resolver(cat, names), W.gov_stems(), W.countries()
    rows = [r for r in csv.DictReader(open(W.CACHE, encoding="utf-8")) if r["name_as_written"]]

    how, forms = collections.Counter(), collections.defaultdict(collections.Counter)
    for r in rows:
        slug, h = res.resolve(r)
        how[(slug is not None, h)] += 1
        if slug:
            forms[slug][" ".join(r["org_as_written"].split())] += 1

    use = res.use
    hand = {r["slug"]: r for r in W.read_csv(W.ORGS, W.ORG_COLS) if r["basis"] == "hand"}
    placed = {r["slug"]: r["place"] for r in W.read_csv(W.PLACES, W.PLACES_COLS)}
    out, named, unnamed, national = {}, collections.Counter(), [], set()
    for slug in forms:
        if slug in hand:
            out[slug] = hand[slug]
            continue
        kind = "government" if W.is_government(slug, stems) else "other"
        # A government is always some country's: the majority test is for bodies that work
        # across many.
        place = place_of(slug, res, placed) or (res.place.get(slug, "") if kind == "government" else "")
        name, nh = name_for(slug, place, names.get(slug), forms[slug], country)
        named[nh] += 1
        if not name:
            # No name the sources wrote is recognisably this slug's: left out, its rows
            # unpublished, until a `hand` row names it.
            unnamed.append((sum(forms[slug].values()), slug, forms[slug].most_common(1)[0][0]))
            continue
        if kind == "government" and place in country and not place.startswith("X") \
                and not names_place(name, place, country[place]):
            name = f"{name}, {country[place]}"
        out[slug] = {"slug": slug, "canonical_slug": slug, "name": name, "place": place,
                     "kind": kind, "basis": "auto"}
        if nh == "government":
            national.add(slug)

    # One body, two slugs: both government, one country, one stem once the country and the
    # language are folded out (`ghana-ministry-of-health`, `ministry-of-health-ghana`). Equal
    # names alone are not enough: a truncated display makes *Ministry of Health and
    # Sanitation* read as *Ministry of Health*, and each incarnation keeps its own row (§6).
    by_name = collections.defaultdict(list)
    for o in out.values():
        # Only slugs that name their country: a place read off the tags is a guess.
        if o["kind"] == "government" and o["basis"] == "auto" and W.slug_countries(o["slug"]) == {o["place"]}:
            # A national government is one body in any language: `gouvernement-du-niger`.
            key = "national-government" if o["slug"] in national else W._key(o["slug"])
            by_name[(key, o["place"])].append(o["slug"])
    merged = 0
    for slugs in by_name.values():
        if len(slugs) > 1:
            keep = max(slugs, key=lambda s: (use[s], s))
            for s in slugs:
                out[s]["canonical_slug"] = keep
            merged += len(slugs) - 1

    # Abbreviations and one body under two names (Bill, 2026-11-20). A slug spelt as a
    # listed abbreviation is that body (`afdb` is `african-development-bank`), and the list
    # names the body where it gives a name: the sources' *La BEAC* or *GIZ Kenya* is not one.
    # Then two `other` slugs with one name are one body when the list holds either, or
    # they share their one country (`powertel`, `powertel-communications`). One name in two
    # countries stays two: *Senate*, *Orange Money*. Governments are left to the stem rule
    # above, because a truncated display is not the body's name.
    abbrev = W.read_csv(W.ABBREV, W.ABBREV_COLS)
    listed = {r["slug"] for r in abbrev}
    for r in abbrev:
        if r["name"] and r["slug"] in out and out[r["slug"]]["basis"] == "auto":
            out[r["slug"]]["name"] = r["name"]
    folded = 0
    for r in abbrev:
        s = W.EV.slugify(r["abbreviation"])
        if s != r["slug"] and s in out and r["slug"] in out and out[s]["basis"] == "auto":
            out[s].update(canonical_slug=r["slug"], name=out[r["slug"]]["name"])
            folded += 1
    same = collections.defaultdict(list)
    for o in out.values():
        if o["kind"] == "other" and o["basis"] == "auto" and o["canonical_slug"] == o["slug"]:
            same[W.fold(o["name"])].append(o["slug"])
    for slugs in same.values():
        if len(slugs) < 2:
            continue
        mine = [s for s in slugs if s in listed]
        if not mine and len({out[s]["place"] for s in slugs if not out[s]["place"].startswith("X")}) > 1:
            continue
        keep = mine[0] if mine else max(slugs, key=lambda s: (use[s], s))
        for s in slugs:
            if s != keep:
                out[s]["canonical_slug"] = keep
                folded += 1

    # Finish line: no published government name stands for two countries, or for none.
    faults = []
    pub = collections.defaultdict(set)
    for o in out.values():
        if o["kind"] == "government" and o["canonical_slug"] == o["slug"]:
            pub[W.fold(o["name"])].add(o["place"])
            if not o["place"] or o["place"].startswith("X"):
                faults.append(f"no country: {o['slug']} -> {o['name']} [{o['place']}]")
    faults += [f"two countries: {n} {sorted(p)}" for n, p in pub.items() if len(p) > 1]

    ok = sum(n for (k, _), n in how.items() if k)
    print(f"{len(rows)} tuples; {ok} resolved, {len(rows) - ok} dropped")
    for (k, h), n in sorted(how.items(), key=lambda x: -x[1]):
        print(f"  {'resolved' if k else 'dropped '}  {h}: {n}")
    kinds = collections.Counter(o["kind"] for o in out.values())
    print(f"{len(out)} organisations ({kinds['government']} government, {kinds['other']} other); "
          f"{len(hand)} hand; {merged} government slugs folded into another; "
          f"{folded} by abbreviation or name")
    print(f"names: {dict(named)}; {len(unnamed)} slugs left unnamed, "
          f"{sum(n for n, _, _ in unnamed)} rows")
    for n, slug, form in sorted(unnamed, reverse=True)[:15]:
        print(f"  unnamed {slug} ({n}) written {form!r}")
    for f in sorted(faults):
        print("  FAULT", f)
    if not a.dry:
        W.write_csv(W.ORGS, W.ORG_COLS, sorted(out.values(), key=lambda o: o["slug"]))
        if not W.LINEAGE.exists():
            W.write_csv(W.LINEAGE, W.LINEAGE_COLS, [])
        print(f"wrote {W.ORGS.relative_to(W.ROOT)}")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main())
