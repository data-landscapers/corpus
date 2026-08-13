#!/usr/bin/env python3
"""
report-region-init.py — standing. The region report layer's initialisation shell
(`REPORT-REGION.md` -> Initialisation; the record layer it shells is `wiki/report-layer.md`).

**The folder is the state**, exactly as for a country: a region is *initialised* when
`outputs/reports/{X__}/ledger.csv` has rows and *outstanding* when it does not. The ledger
schema, `create_shell` and the initialised test are imported from `report-country-init.py`
rather than restated — two copies of a schema is how the two drift.

**What is different here is the scope rule** (`REPORT-REGION.md` -> Scope). A country's base is
the sources carrying its place code; a region's is that **plus the sources that tag one of its
institutions**, because an ECOWAS decision reported from Abuja is tagged `NGA` and the body it is
about is an entity. `scope()` is the one implementation of that union and `report-scan.py` imports
it, so the nightly set difference and this shell cover the same base.

Six units: XAF XCA XEA XNA XSA XWA. **XSS is folded into XAF** (a donor's category, not a place
with institutions, and overlapping XAF almost entirely — the same conflation `SWEEP-REGIONAL.md`
makes at the other end of the pipe) and **XGL is excluded** (the root above Africa, not a region
of it).

It reads and it creates empty shells. It writes no report and no ledger row — those are the run's,
and the run is a model reading the institution pages.

Usage:
  python scripts/report-region-init.py --status          what is done, what is next
  python scripts/report-region-init.py --count 2         take the next two, create their shells
  python scripts/report-region-init.py --region XWA XSA  these, in this order
  python scripts/report-region-init.py --count 2 --dry-run  print the work order, create nothing
  python scripts/report-region-init.py --scope XWA       the unit's source slugs, one per line
Exit: 0 always, unless there is nothing outstanding to take (1).
"""
import argparse
import collections
import csv
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vault_lib  # noqa: E402

# One definition of the ledger schema, the shell and "initialised", imported rather than copied.
_spec = importlib.util.spec_from_file_location("rci", os.path.join(HERE, "report-country-init.py"))
_rci = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rci)

ROOT = vault_lib.ROOT
REPORTS = os.path.join(ROOT, "outputs", "reports")
SECTIONS_CSV = os.path.join(ROOT, "lookups", "report-region-sections.csv")
COUNTRIES_CSV = os.path.join(ROOT, "lookups", "countries.csv")

# XSS reads into XAF; XGL is not a region of Africa. Both rulings are in REPORT-REGION.md.
FOLD = {"XSS": "XAF"}
EXCLUDE = {"XGL"}

# Which entity types make an institution of a region. An `organisation`, a `government-body`, an
# `initiative` and an `instrument` placed at a region are the regional layer; a `company` placed
# there is a pan-African market participant and tagging it would drag national commercial news
# into a report about institutions. `person` follows CLAUDE.md -> Entities: tag the institution.
INSTITUTION_TYPES = ("organisation", "government-body", "initiative", "instrument")

# **An entity's `places` says where it operates, not what it is of**, so membership has to be read
# off the *shape* of that list rather than off the presence of the code. A sub-region's institution
# names that sub-region and no other — the World Bank carries XEA, XSA and XWA and is an actor in
# each rather than an institution of any. XAF takes the continental bodies, which legitimately name
# sub-regions too: PAPSS (XAF, XWA, XCA) is one continental system and its rows belong to XAF's
# ledger, cited in XWA's prose. XGL marks a global actor and disqualifies.
def institution_of(codes, region):
    """Is an entity whose place list yields region codes `codes` an institution of `region`?"""
    if region == "XAF":
        return "XAF" in codes
    return codes == {region}

WINDOW = 14          # months of history printed
CLIFF_RATIO = 3.0    # later half this many times the earlier half = a cliff worth saying
TOP_INSTITUTIONS = 25


def regions():
    """{code: name} — the X-rows of countries.csv, less the folded and the excluded."""
    out = {}
    with open(COUNTRIES_CSV, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            code = (row.get("iso-3") or "").strip()
            if code.startswith("X") and code not in EXCLUDE and code not in FOLD:
                out[code] = (row.get("country-name") or code).strip()
    return out


def section_map():
    with open(SECTIONS_CSV, encoding="utf-8", newline="") as fh:
        return {r["subject"]: r["section"] for r in csv.DictReader(fh)}


def scope(rows=None):
    """The region scope rule, in one place.

    Returns (slugs, by_place, months, subjects, institutions):
      slugs[code]        {slug} — the union: place-tagged (XSS folded into XAF) + institution-tagged
      by_place[code]     {slug} — the place-tagged half alone, so the work order can show the split
      months[code]       Counter{'YYYY-MM': n} over the union
      subjects[code]     Counter{subject: n} over the union
      institutions[code] [(entity_slug, title, n_sources)] — the reading list, deepest first
    """
    rows = vault_lib.load_index() if rows is None else rows
    codes = set(regions())
    # Pass 1 — which entity slug is an institution of which region(s).
    ent_region, ent_title = collections.defaultdict(set), {}
    for r in rows:
        d, fm = r.get("d") or {}, r.get("fm") or {}
        if d.get("kind") != "entity":
            continue
        if str(fm.get("entity_type") or "") not in INSTITUTION_TYPES:
            continue
        places = [str(p).strip() for p in vault_lib.as_list(fm.get("places"))]
        if "XGL" in places:
            continue
        mine = {FOLD.get(p, p) for p in places if p.startswith("X")} & codes
        if not mine:
            continue
        slug = d.get("slug") or os.path.basename(r["path"])[:-3]
        for code in codes:
            if institution_of(mine, code):
                ent_region[slug].add(code)
                ent_title[slug] = str(fm.get("title") or slug)
    # Pass 2 — the sources, by both halves of the rule.
    slugs = collections.defaultdict(set)
    by_place = collections.defaultdict(set)
    months = collections.defaultdict(collections.Counter)
    subjects = collections.defaultdict(collections.Counter)
    inst_count = collections.defaultdict(collections.Counter)
    for r in rows:
        d, fm = r.get("d") or {}, r.get("fm") or {}
        if d.get("folder") != "raw" or d.get("kind") != "source":
            continue
        slug = d.get("slug") or os.path.basename(r["path"])[:-3]
        hit = set()
        for p in vault_lib.as_list(fm.get("places")):
            code = FOLD.get(str(p).strip(), str(p).strip())
            if code in codes:
                hit.add(code)
                by_place[code].add(slug)
        for e in vault_lib.as_list(fm.get("entities")):
            e = str(e).strip().strip("[]")
            for code in ent_region.get(e, ()):
                hit.add(code)
                inst_count[code][e] += 1
        month = str(fm.get("published") or "")[:7]
        for code in hit:
            slugs[code].add(slug)
            if re.fullmatch(r"\d{4}-\d{2}", month):
                months[code][month] += 1
            for t in vault_lib.as_list(fm.get("topics")):
                subjects[code][str(t)] += 1
    institutions = {}
    for code in codes:
        seen = [(n, s) for s, n in inst_count[code].items()]
        seen.sort(key=lambda x: (-x[0], x[1]))
        institutions[code] = [(s, ent_title.get(s, s), n) for n, s in seen]
    return slugs, by_place, months, subjects, institutions


def slugs_for(code, rows=None):
    """The unit's source slugs — what report-scan.py's set difference is taken over."""
    return scope(rows)[0].get(code, set())


def work_order(code, name, slugs, by_place, months, subjects, institutions, secmap):
    total = len(slugs.get(code, set()))
    placed = len(by_place.get(code, set()))
    insts = institutions.get(code, [])
    print(f"\n=== {code} — {name} ===")
    extra = " (XSS folded in)" if code == "XAF" else ""
    print(f"  base: {total} sources — {placed} carrying the place code{extra}, "
          f"{total - placed} reached only through an institution")
    hist = months.get(code, collections.Counter())
    keys = sorted(hist)[-WINDOW:]
    if keys:
        print("  by month: " + "  ".join(f"{k[5:]}:{hist[k]}" for k in keys))
        half = len(keys) // 2
        early = sum(hist[k] for k in keys[:half])
        late = sum(hist[k] for k in keys[half:])
        if early == 0 or late / max(early, 1) >= CLIFF_RATIO:
            print(f"  ** COVERAGE CLIFF: {early} sources in the earlier half against {late} in the later.")
            print("     Narrow the window, or say in the document that it is a shorter comparison"
                  " wearing a longer label (wiki/report-layer.md 7).")
    print(f"  institutions of this region: {len(insts)} — this is the reading list, deepest first")
    for slug, title, n in insts[:TOP_INSTITUTIONS]:
        page = f"wiki/entities/{slug}.md"
        kb = (os.path.getsize(os.path.join(ROOT, page)) // 1024
              if os.path.exists(os.path.join(ROOT, page)) else 0)
        print(f"     {n:4d}  {title[:52]:<52} {page}  ({kb}KB)")
    if len(insts) > TOP_INSTITUTIONS:
        tail = sum(n for _, _, n in insts[TOP_INSTITUTIONS:])
        print(f"     … and {len(insts) - TOP_INSTITUTIONS} more carrying {tail} source-tags between them")
    subs = subjects.get(code, collections.Counter())
    covered = [(n, s) for s, n in subs.items() if n >= 3 and s in secmap]
    covered.sort(reverse=True)
    print(f"  subjects with 3+ sources: {len(covered)} of {len(secmap)}")
    by_section = collections.defaultdict(list)
    for n, s in covered:
        by_section[secmap.get(s, "(unmapped)")].append(f"{s}:{n}")
    for sec in sorted(by_section):
        print(f"     {sec}: " + ", ".join(by_section[sec][:8]))
    thin = [s for s in secmap if subs.get(s, 0) == 0]
    print(f"  subjects with nothing held: {len(thin)} — these are Not held rows, and gaps.csv lines")
    hub = os.path.join("wiki", "places", f"{code}.md")
    if os.path.exists(os.path.join(ROOT, hub)):
        print(f"  hub: {hub.replace(os.sep, '/')} ({os.path.getsize(os.path.join(ROOT, hub)) // 1024}KB)"
              " — the institution pages are the compiled layer; grep the hub, never open it whole")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--count", type=int, help="take this many outstanding regions")
    ap.add_argument("--region", nargs="+", help="these regions, in this order")
    ap.add_argument("--status", action="store_true", help="what is initialised and what is next")
    ap.add_argument("--dry-run", action="store_true", help="print the work order, create nothing")
    ap.add_argument("--scope", metavar="X__", help="the unit's source slugs, one per line")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    names = regions()
    if args.scope:
        print("\n".join(sorted(slugs_for(args.scope.upper()))))
        return 0

    rows = vault_lib.load_index()
    slugs, by_place, months, subjects, institutions = scope(rows)
    secmap = section_map()
    done = [c for c in names if _rci.initialised(c)]
    outstanding = sorted((c for c in names if c not in done), key=lambda c: (-len(slugs.get(c, ())), c))

    if args.status or not (args.count or args.region):
        print(f"region reports: {len(done)} of {len(names)} initialised, {len(outstanding)} outstanding")
        if done:
            print("  initialised: " + " ".join(sorted(done)))
        print("  next up (deepest base first):")
        for c in outstanding:
            print(f"     {c} {names[c]:<28} {len(slugs.get(c, ())):4d} sources")
        if not args.status:
            print("\n  --count N to take the next N; --region XAF to override the order")
        return 0

    if args.region:
        take = [c.upper() for c in args.region]
        unknown = [c for c in take if c not in names]
        if unknown:
            print("not region units (XSS folds into XAF, XGL is excluded):", " ".join(unknown))
            return 1
    else:
        take = outstanding[:args.count]
    if not take:
        print("nothing outstanding — every region has a ledger")
        return 1

    print(f"taking {len(take)}: " + " ".join(take))
    for code in take:
        if _rci.initialised(code) and not args.region:
            continue
        work_order(code, names[code], slugs, by_place, months, subjects, institutions, secmap)
        if args.dry_run:
            print("  (dry run — no shell created)")
        else:
            print("  shell: " + os.path.relpath(_rci.create_shell(code), ROOT))
    print("\nNow run REPORT-REGION.md step 3 for each — the institution pages, then what they do not own.")
    print("Format, register and the drafting contract: wiki/report-region-skeleton.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
