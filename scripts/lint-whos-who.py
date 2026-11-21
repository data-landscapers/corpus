#!/usr/bin/env python3
"""lint-whos-who.py — the Who's Who rules that hold the published rows to six fields.

RENDER Step 7, beside `lint-page-weight.py`. `documentation/whos-who.md` §8 numbers the
lints; this file is them, plus two the page added at stage 5:

1. `outputs/whos-who/whos-who.csv` and its site copy have exactly the six columns, in order,
   and the two are the same bytes.
2. Each tracked lookup and the cache have exactly their declared columns (§4).
3. Every published `source_url` is a catalogue URL (a row joins several with `; `); every organisation slug a published row
   resolves to is a catalogue tag, or an organisation an author row names.
4. No suppressed person or pair is published; no suppressed person has a name or an alias.
5. No published name sits under two people in one organisation unless ruled `different`.
6. Every published position passes §5's role-word, deny-list and length test; an author
   row's (`whos-who-authors.py`) is exempt from the role word.
7. The page's search index is under the 2 MB compressed line (`lint-page-weight.py`'s rule,
   which cannot see a table the page builds on demand).
8. No `person_id` appears anywhere under `site/whos-who/` (§8a).

Lints 3 and 5 read `build/whos-who/positions.csv`, which is untracked and rebuilt nightly;
without it they are reported as not run and the exit is 2.

    python scripts/lint-whos-who.py      # 0 clean · 1 a breach · 2 could not check everything
"""
from __future__ import annotations

import collections
import csv
import gzip
import importlib.util
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import whos_who_lib as W  # noqa: E402

ROOT = W.ROOT
L = ROOT / "lookups"
OUT = ROOT / "outputs" / "whos-who" / "whos-who.csv"
SITE = ROOT / "site" / "whos-who"
POSITIONS = ROOT / "build" / "whos-who" / "positions.csv"
PUBLISHED = ["name", "year", "position", "organisation", "country", "source_url"]
DECLARED = {
    L / "organisations.csv": W.ORG_COLS,
    L / "org-lineage.csv": W.LINEAGE_COLS,
    L / "people.csv": ["person_id", "name", "basis", "anchor"],
    L / "person-aliases.csv": ["alias", "person_id", "basis"],
    L / "person-rulings.csv": ["person_id_a", "person_id_b", "ruling", "ruled"],
    L / "whos-who-suppress.csv": ["person_id", "slug", "date"],
    L / "position-glossary.csv": W.GLOSSARY_COLS,
    L / "org-abbreviations.csv": W.ABBREV_COLS,
    L / "org-places.csv": W.PLACES_COLS,
    L / "naming-conventions.csv": ["iso3", "country", "order", "family_caps", "particles", "note",
                                   "basis"],
    ROOT / "build" / "whos-who" / "extract.csv": ["source_url", "name_as_written", "position",
                                                  "org_as_written", "slug_hint", "tense",
                                                  "year", "year_to"],
}
MAX_GZ = 2 * 1024 * 1024
PERSON_ID = re.compile(rb"\bP\d{6}\b")


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def header(path: Path) -> list[str]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return next(csv.reader(fh), [])


def main() -> int:
    faults: list[str] = []
    unchecked: list[str] = []

    def fail(n: int, msg: str, items=()):
        items = list(items)
        faults.append(f"lint {n}: {msg}" + (f" ({len(items)})" if items else ""))
        faults.extend(f"    {x}" for x in items[:5])

    if not OUT.exists():
        print("lint-whos-who: no outputs/whos-who/whos-who.csv — run whos-who-publish.py")
        return 2
    # 1
    for p in (OUT, SITE / "whos-who.csv"):
        if not p.exists() or header(p) != PUBLISHED:
            fail(1, f"{p.relative_to(ROOT)} is not exactly {','.join(PUBLISHED)}")
    if (SITE / "whos-who.csv").exists() and OUT.read_bytes() != (SITE / "whos-who.csv").read_bytes():
        fail(1, "site/whos-who/whos-who.csv differs from outputs/whos-who/whos-who.csv")
    # 2
    for p, cols in DECLARED.items():
        if p.exists() and header(p) != cols:
            fail(2, f"{p.relative_to(ROOT)} columns {header(p)} != {cols}")
    rows = read(OUT)
    # 3
    cat = W.catalogue()
    fail_urls = [u for r in rows for u in r["source_url"].split("; ") if u not in cat]
    if fail_urls:
        fail(3, "published source_url not in the catalogue", fail_urls)
    # 4
    sup = read(L / "whos-who-suppress.csv")
    people = {r["person_id"]: r["name"] for r in read(L / "people.csv")}
    aliases = collections.defaultdict(list)
    for r in read(L / "person-aliases.csv"):
        aliases[r["person_id"]].append(r["alias"])
    orgs = {r["slug"]: r for r in read(L / "organisations.csv")}
    published = {(r["name"], r["organisation"]) for r in rows}
    for s in sup:
        pid, slug = s["person_id"], s["slug"]
        if not slug and (people.get(pid) or aliases.get(pid)):
            fail(4, f"suppressed {pid} still has a name or an alias")
        if slug and (people.get(pid), orgs.get(slug, {}).get("name")) in published:
            fail(4, f"suppressed pair {pid} / {slug} is published")
    # 6
    cache = load("whos_who_cache", ROOT / "scripts" / "whos-who-cache.py")
    # An author row's post is the one its piece states, or *Journalist* or *Author*
    # (`whos-who-authors.py`): held to the test bar the role word, which is officeholders'.
    authored = {r["position"] for r in W.read_csv(W.AUTHORS, W.AUTHOR_COLS)}
    bad = sorted({r["position"] for r in rows if r["position"] not in authored
                  and cache.position_fault(re.sub(r" \(former\)$", "", r["position"]))})
    if bad:
        fail(6, "published position fails the role, deny or length test", bad)
    # 3 (slugs) and 5 need the fact table
    if POSITIONS.exists():
        # An outlet or employer an author row names is a body off the tags (`whos-who-authors.py`).
        tags = {e for i in cat.values() for e in (i.get("entities") or [])} | set(W.author_slugs())
        pos = read(POSITIONS)
        canon = {r["slug"]: r["canonical_slug"] for r in orgs.values()}
        off = sorted({canon.get(r["slug"], r["slug"]) for r in pos} - tags)
        if off:
            fail(3, "organisation slug not a catalogue tag", off)
        different = {frozenset((r["person_id_a"], r["person_id_b"]))
                     for r in read(L / "person-rulings.csv") if r["ruling"] == "different"}
        at = collections.defaultdict(set)
        for r in pos:
            if people.get(r["person_id"]):
                at[(W.fold(people[r["person_id"]]), canon.get(r["slug"], r["slug"]))].add(r["person_id"])
        two = [f"{n} @ {s}: {sorted(p)}" for (n, s), p in at.items() if len(p) > 1
               and not all(frozenset((a, b)) in different for a in p for b in p if a < b)]
        if two:
            fail(5, "one name under two people in one organisation", two)
    else:
        unchecked.append("lints 3 (slugs) and 5: build/whos-who/positions.csv missing")
    # 7
    idx = SITE / "data" / "index.json"
    if idx.exists():
        gz = len(gzip.compress(idx.read_bytes()))
        if gz > MAX_GZ:
            fail(7, f"data/index.json {gz:,} bytes compressed, over 2 MB")
    else:
        unchecked.append("lint 7: site/whos-who/data/index.json missing")
    # 8
    # Source URLs are left out: a World Bank project id is also P and six digits, and the
    # `src-*.json` blocks hold nothing but URLs keyed by catalogue document id.
    ids = set(people)
    leaks = [str(p.relative_to(ROOT)) for p in (SITE / "index.html", SITE / "data" / "index.json")
             if p.exists() and {m.decode() for m in PERSON_ID.findall(p.read_bytes())} & ids]
    leaks += [f"whos-who.csv: {r['name']}" for r in rows
              if any(PERSON_ID.search(r[c].encode()) for c in PUBLISHED[:-1])]
    if leaks:
        fail(8, "person_id found on the site", leaks)

    for line in faults + [f"not run: {u}" for u in unchecked]:
        print(line)
    print(f"lint-whos-who: {len(rows):,} rows, "
          f"{sum(1 for f in faults if f.startswith('lint'))} breach(es)")
    return 1 if faults else 2 if unchecked else 0


if __name__ == "__main__":
    raise SystemExit(main())
