#!/usr/bin/env python3
r"""whos-who-cache.py — admit the reading pass's output to the extraction cache.

    python scripts/whos-who-cache.py CIV          merge C:\whos-who-work\out\CIV\*.jsonl
    python scripts/whos-who-cache.py CIV --dry    counts only, write nothing

`documentation/whos-who.md` §4–§5. The model writes JSONL outside the repo; this checks
every tuple against its input batch and §5's rules and appends what passes to
`build/whos-who/extract.csv`, the tracked cache keyed by `source_url`. A source that
yielded nothing gets one row with the rest blank, so it is not read again. A tuple that
fails is dropped and counted by cause — never repaired.

**A source the output never mentions is left uncached**, not cached as empty, so the next
candidate pass batches it again; the rest of its batch is admitted. Run it only on batches
whose agent has finished — a batch still being written reads as mostly unread.
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
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(os.environ.get("WHOS_WHO_WORK") or r"C:\whos-who-work")
CACHE = ROOT / "build" / "whos-who" / "extract.csv"
COLS = ["source_url", "name_as_written", "position", "org_as_written", "slug_hint",
        "tense", "year", "year_to"]
MAX_POSITION_WORDS = 12


def fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))


def wordlist(name: str) -> re.Pattern:
    words = sorted({fold(r["word"].strip()) for r in csv.DictReader(open(ROOT / "lookups" / name, encoding="utf-8"))},
                   key=len, reverse=True)
    alt = "|".join(re.escape(w).replace(r"\ ", r"\s+") for w in words)
    return re.compile(rf"(?<![\w-])(?:{alt})s?(?![\w])")


ROLE, DENY = wordlist("whos-who-roles.csv"), wordlist("whos-who-deny.csv")
AUTHORS = {i["url"]: fold(i.get("author") or "") for i in
           json.load(open(ROOT / "outputs" / "catalogue" / "raw-catalogue.json", encoding="utf-8"))["items"]}


def position_fault(p: str) -> str | None:
    f = fold(p)
    if not ROLE.search(f):
        return "position has no role word"
    if DENY.search(f):
        return "position carries a denied word"
    if len(p.split()) > MAX_POSITION_WORDS:
        return "position over 12 words"
    # At the start only: "Ministre des Anciens Combattants" is a title, not a former holder.
    if re.match(r"(former|ancien|ancienne|ex)\b", f):
        return "position carries 'former'"
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", help="comma-separated batch numbers whose agents have finished")
    a = ap.parse_args(argv)

    have = set()
    if CACHE.exists():
        have = {r["source_url"] for r in csv.DictReader(open(CACHE, encoding="utf-8"))}
    drops, rows, kept_batches, skipped = collections.Counter(), [], 0, []
    only = {int(x) for x in a.only.split(",")} if a.only else None
    for cand in sorted((WORK / "candidates" / a.tag).glob("batch-*.json")):
        if only is not None and int(cand.stem.split("-")[1]) not in only:
            continue
        # A large batch may come back in parts: batch-NNN.jsonl and batch-NNN.partK.jsonl.
        outs = sorted((WORK / "out" / a.tag).glob(cand.stem + ".*jsonl"))
        if not outs:
            continue
        src = {s["url"]: s for s in json.load(open(cand, encoding="utf-8"))}
        if all(u in have for u in src):
            continue
        lines = []
        for ln in (x for p in outs for x in open(p, encoding="utf-8")):
            ln = ln.strip()
            if not ln:
                continue
            try:
                lines.append(json.loads(ln))
            except json.JSONDecodeError:
                drops["unparseable line"] += 1
        # A source the agent never mentioned is left uncached, not cached as empty, so the
        # next candidate pass batches it again. Its siblings are admitted.
        seen_urls = {o.get("url") for o in lines}
        missing = set(src) - seen_urls
        if missing:
            skipped.append(f"{cand.stem}: {len(missing)} sources unread, left for the next pass")
        kept_batches += 1
        batch_rows, yielded = [], set()
        for o in lines:
            u = o.get("url")
            if not u or u not in src:
                drops["url empty or not in input"] += 1
                continue
            if o.get("none"):
                continue
            s = src[u]
            name, pos, org = (str(o.get(k) or "").strip() for k in ("name", "position", "org"))
            pos = " ".join(pos.split())
            slug = str(o.get("slug") or "").strip()
            tense, year, year_to = o.get("tense"), str(o.get("year") or ""), str(o.get("year_to") or "")
            if not name or not pos or not org:
                drops["missing name, position or org"] += 1
                continue
            if len(name.split()) < 2 or len(name.split()) > 6:
                drops["name not 2-6 words"] += 1
                continue
            # A source's own author never yields a row, even where the text states their post:
            # the index is about officeholders a source reports, not who wrote it.
            if AUTHORS.get(u) and all(t in AUTHORS[u] for t in fold(name).split() if len(t) > 2):
                drops["name is the source's author"] += 1
                continue
            fault = position_fault(pos)
            if fault:
                drops[fault] += 1
                continue
            if tense not in ("holds", "held"):
                drops["bad tense"] += 1
                continue
            if not re.fullmatch(r"(19|20)\d\d", year) or int(year) > int(s["year"]):
                drops["bad year"] += 1
                continue
            if year_to and (not re.fullmatch(r"(19|20)\d\d", year_to) or year_to < year or tense != "held"):
                drops["bad year_to"] += 1
                continue
            if slug and slug not in {e[0] for e in s["entities"]}:
                slug = ""
                drops["slug not in tags (blanked, row kept)"] += 1
            key = (u, name, pos, org, tense, year, year_to)
            if key in yielded:
                continue
            yielded.add(key)
            batch_rows.append(dict(zip(COLS, [u, name, pos, org, slug, tense, year, year_to])))
        got = {r["source_url"] for r in batch_rows}
        for u in src:
            if u in have or u in missing:
                continue
            if u not in got:
                batch_rows.append(dict(zip(COLS, [u] + [""] * (len(COLS) - 1))))
        rows += [r for r in batch_rows if r["source_url"] not in have]

    real = [r for r in rows if r["name_as_written"]]
    print(f"{a.tag}: {kept_batches} batches admitted; {len(real)} rows from "
          f"{len({r['source_url'] for r in real})} sources; "
          f"{len({r['source_url'] for r in rows}) - len({r['source_url'] for r in real})} sources with none")
    for k, v in drops.most_common():
        print(f"  dropped {v:5d}  {k}")
    for s in skipped:
        print(f"  skipped  {s}")
    if a.dry or not rows:
        return 0
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    new = not CACHE.exists()
    with open(CACHE, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"appended {len(rows)} rows to {CACHE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
