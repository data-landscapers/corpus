#!/usr/bin/env python3
"""Pool stage 1's facts, dedupe them and slice by chapter — `STATUS-INIT.md` -> *Stage 2, step 7*.

Twenty extraction agents each write a JSON list of facts to `prep/scope/{ISO3}/facts/`. This reads
them all, drops what cannot be cited, merges the fact that arrived twice, assigns each survivor an
owning chapter, and writes one slice per chapter for the writer agents to read.

Doing it as a script rather than by hand is the point: the survivor rule and the ownership rule are
deterministic, they are applied several hundred times per country and 54 times over, and a parent
that re-derived them by eye would apply them differently on Tuesday.

    python scripts/status-pool.py NGA

Slices land in `prep/scope/{ISO3}/slices/`. Both directories are gitignored working material.
"""

import argparse
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402

SCOPE = os.path.join(S.REPO, "prep", "scope")

TIER = {"primary": 0, "official": 1, "reported": 2, "syndicated": 3}
CONF = {"solid": 0, "borderline": 1}

# Two facts about the same object arrive in different words. Within one source they are compared
# loosely, because an agent citing the same URL twice is usually saying the same thing twice; across
# sources the bar is higher, because two sources agreeing on a subject is not the same as two
# sources stating one fact.
SAME_URL = 0.55
CROSS_URL = 0.72

STOP = set("the a an of in on at to for and or by is are was were with from as its it this that "
           "has have had been be not no than which who whose whom".split())


def tokens(text):
    return frozenset(w for w in re.findall(r"[a-z0-9%.]+", text.lower()) if w not in STOP)


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load(iso):
    """Every fact stage 1 wrote, tagged with the file it came from."""
    facts, bad = [], collections.Counter()
    for path in sorted(glob.glob(os.path.join(SCOPE, iso, "facts", "*.json"))):
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            rows = json.load(open(path, encoding="utf-8"))
        except Exception as exc:                                    # noqa: BLE001
            print(f"  ! {name}: unreadable — {exc}", file=sys.stderr)
            continue
        if not isinstance(rows, list):
            print(f"  ! {name}: not a list", file=sys.stderr)
            continue
        for row in rows:
            row["source_file"] = name
            if not isinstance(row.get("fact"), str) or not row["fact"].strip():
                bad["no fact sentence"] += 1
                continue
            if not (row.get("url") or "").startswith("http"):
                bad["no url"] += 1
                continue
            slugs = [s for s in (row.get("slugs") or []) if s in SLUGS]
            if not slugs:
                bad["no live slug"] += 1
                continue
            row["slugs"] = slugs
            facts.append(row)
    return facts, bad


def dedupe(facts):
    """Merge the fact that arrived twice; keep the better copy and the union of its slugs.

    Confidence leads, because the point of pooling is that where a solid account of an object
    exists, no chapter reasons from the shaky version of the same thing."""
    facts = sorted(facts, key=lambda f: (CONF.get(f.get("confidence"), 1),
                                         TIER.get(f.get("tier"), 3),
                                         f.get("published") or "",
                                         f["fact"]))
    # Better copies come first, so the survivor is always the one already in `kept`.
    kept, merged = [], 0
    by_url = collections.defaultdict(list)
    for fact in facts:
        fact["_tok"] = tokens(fact["fact"])
        hit = None
        for other in by_url[fact["url"]]:
            if jaccard(fact["_tok"], other["_tok"]) >= SAME_URL:
                hit = other
                break
        if hit is None:
            for other in kept:
                if other["url"] != fact["url"] and jaccard(fact["_tok"], other["_tok"]) >= CROSS_URL:
                    hit = other
                    break
        if hit is None:
            fact["also"] = []
            kept.append(fact)
            by_url[fact["url"]].append(fact)
        else:
            merged += 1
            for slug in fact["slugs"]:
                if slug not in hit["slugs"]:
                    hit["slugs"].append(slug)
            if fact["url"] != hit["url"] and fact["url"] not in hit["also"]:
                hit["also"].append(fact["url"])
    for fact in kept:
        del fact["_tok"]
    return kept, merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iso3")
    args = ap.parse_args()
    iso = args.iso3.upper()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    facts, bad = load(iso)
    held = S.held_urls()
    unheld = [f for f in facts if f["url"] not in held]
    facts = [f for f in facts if f["url"] in held]

    kept, merged = dedupe(facts)

    # Ownership. The owning chapter is the chapter of the fact's first slug in outline order; it
    # states the fact in full and every other chapter refers to it in passing.
    for fact in kept:
        first = min(fact["slugs"], key=lambda s: ORDER[s])
        fact["owner_slug"] = first
        fact["owner_chapter"] = CHAPTER[first]
        fact["slugs"] = sorted(fact["slugs"], key=lambda s: ORDER[s])

    out = os.path.join(SCOPE, iso, "slices")
    os.makedirs(out, exist_ok=True)
    # The whole pool, one file, for `status-acquire.py` — the acquire line needs the publisher,
    # title and publication date of a cited URL, and the assembled document carries none of them.
    with open(os.path.join(SCOPE, iso, "pool.json"), "w", encoding="utf-8") as fh:
        json.dump(kept, fh, indent=1, ensure_ascii=False)
    for old in glob.glob(os.path.join(out, "*.json")):
        os.remove(old)

    chapters = [c for c, _, _ in S.outline()]
    seen = []
    for chapter in chapters:
        if chapter not in seen:
            seen.append(chapter)
    for n, chapter in enumerate(seen, 1):
        mine = [f for f in kept if any(CHAPTER[s] == chapter for s in f["slugs"])]
        payload = []
        for fact in mine:
            row = dict(fact)
            row["sections"] = [s for s in fact["slugs"] if CHAPTER[s] == chapter]
            row["mine"] = fact["owner_chapter"] == chapter
            payload.append(row)
        payload.sort(key=lambda r: (ORDER[r["sections"][0]], not r["mine"],
                                    CONF.get(r.get("confidence"), 1)))
        name = re.sub(r"[^a-z0-9]+", "-", chapter.lower()).strip("-")
        with open(os.path.join(out, f"{n:02d}-{name}.json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1, ensure_ascii=False)

    # The report
    print(f"# status-init pool — {iso}\n")
    print(f"facts returned      : {len(facts) + len(unheld) + sum(bad.values())}")
    for reason, n in bad.most_common():
        print(f"  dropped, {reason:<14}: {n}")
    if unheld:
        print(f"  dropped, url not held: {len(unheld)}")
        for f in unheld[:20]:
            print(f"      {f['source_file']:<26} {f['url'][:96]}")
    print(f"merged as duplicates: {merged}")
    print(f"facts pooled        : {len(kept)}")
    borderline = sum(1 for f in kept if f.get("confidence") == "borderline")
    print(f"  of which borderline: {borderline}")
    print(f"distinct urls       : {len({f['url'] for f in kept})}\n")

    print(f"{'sub-section':<20}{'owned':>7}{'shared':>8}   chapter")
    for chapter, slug, _label in S.outline():
        owned = sum(1 for f in kept if f["owner_slug"] == slug)
        shared = sum(1 for f in kept if slug in f["slugs"] and f["owner_slug"] != slug)
        flag = "  <-- nothing" if owned + shared == 0 else ""
        print(f"{slug:<20}{owned:>7}{shared:>8}   {chapter}{flag}")

    print()
    for n, chapter in enumerate(seen, 1):
        name = re.sub(r"[^a-z0-9]+", "-", chapter.lower()).strip("-")
        size = os.path.getsize(os.path.join(out, f"{n:02d}-{name}.json"))
        n_facts = sum(1 for f in kept if any(CHAPTER[s] == chapter for s in f["slugs"]))
        print(f"  slices/{n:02d}-{name}.json   {n_facts} facts   {size / 1024:.0f}KB")


OUTLINE = S.outline()
SLUGS = {slug for _c, slug, _l in OUTLINE}
ORDER = {slug: i for i, (_c, slug, _l) in enumerate(OUTLINE)}
CHAPTER = {slug: c for c, slug, _l in OUTLINE}

if __name__ == "__main__":
    main()
