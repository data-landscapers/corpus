#!/usr/bin/env python3
r"""whos-who-candidates.py — the deterministic candidate pass of the Who's Who index.

    python scripts/whos-who-candidates.py --place CIV            one country's candidates
    python scripts/whos-who-candidates.py --place CIV --stats    counts only, write nothing
    python scripts/whos-who-candidates.py --all                  every catalogue source not yet cached

`documentation/whos-who.md` §5 step 1. Reads catalogue sources' bodies — never their
frontmatter, so OSINT's `note:` and `catalogue_hero` are out — and keeps a sentence when a
role word from `lookups/whos-who-roles.csv` and a name-shaped run sit in it together. A
source already in `build/whos-who/extract.csv` is skipped: the cache is keyed by URL and
a source is read once.

**The output holds sentences, so it is written outside the repo** (§3): batches of JSON
under `C:\whos-who-work\candidates\` (`WHOS_WHO_WORK` overrides), one object a source with
its URL, year, tagged entities and their display names. The reading pass consumes them.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault_lib as V                                                # noqa: E402
from names_lib import NAME, body                                     # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(V.ROOT)
# Run from the repo or from the workroot: `raw/` is a junction in the latter only.
RAW = Path(os.environ.get("CORPUS_RAW") or next(
    (p for p in (ROOT / "raw", ROOT / "scripts" / ".workroot" / "raw") if p.exists()), ROOT / "raw"))
CATALOGUE = ROOT / "outputs" / "catalogue" / "raw-catalogue.json"
NAMES = ROOT / "lookups" / "entity-names.csv"
ROLES = ROOT / "lookups" / "whos-who-roles.csv"
CACHE = ROOT / "build" / "whos-who" / "extract.csv"
WORK = Path(os.environ.get("WHOS_WHO_WORK") or r"C:\whos-who-work")

# A budget volume names its minister on hundreds of pages; past this many sentences a
# source's later ones add repetition, not people. The cap is counted, never silent.
MAX_SENTENCES = 30
MAX_CHARS = 600            # a "sentence" longer than this is a table or list that lost its breaks
BATCH_SOURCES = 120

SENT = re.compile(r"(?<=[.!?;])\s+(?=[A-ZÀ-ÖØ-Þ«\"“(])|\n\s*\n|\n(?=\s*[-*•])")


def role_pattern() -> re.Pattern:
    words = sorted({r["word"].strip().lower() for r in csv.DictReader(open(ROLES, encoding="utf-8"))},
                   key=len, reverse=True)
    alt = "|".join(re.escape(w).replace(r"\ ", r"\s+") for w in words)
    return re.compile(rf"(?<![\w-])(?:{alt})s?(?![\w])", re.I)


def cached_urls() -> set[str]:
    if not CACHE.exists():
        return set()
    return {r["source_url"] for r in csv.DictReader(open(CACHE, encoding="utf-8"))}


def candidates(text: str, role: re.Pattern) -> tuple[list[str], int]:
    out, total = [], 0
    prose = re.sub(r"(?m)^(Author|URL|Source|Published):.*$", " ", body(text))
    for s in SENT.split(prose):
        s = " ".join(s.split())
        # A backtick or bold marks OSINT's own provenance prose inside a body, not the source's.
        if "`" in s or "**" in s:
            continue
        if len(s) < 25 or len(s) > MAX_CHARS or not role.search(s) or not NAME.search(s):
            continue
        total += 1
        if len(out) < MAX_SENTENCES and s not in out:
            out.append(s)
    return out, total


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--place", help="ISO-3 code; sources tagged with it")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args(argv)

    items = json.load(open(CATALOGUE, encoding="utf-8"))["items"]
    display = {r["slug"]: r["display"] for r in csv.DictReader(open(NAMES, encoding="utf-8"))}
    role, done = role_pattern(), cached_urls()
    picked = [i for i in items if (a.all or a.place in i["places"]) and i["url"] not in done]

    rows, n_sent, n_capped, n_missing, n_coarse = [], 0, 0, 0, 0
    for it in picked:
        if it["date_precision"] not in ("day", "month", "year"):
            n_coarse += 1
            continue
        fp = RAW / it["path"][len("raw/"):]
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            n_missing += 1
            continue
        sents, total = candidates(text, role)
        if not sents:
            continue
        n_sent += len(sents)
        n_capped += total > len(sents)
        rows.append({"url": it["url"], "year": it["published"][:4], "places": it["places"],
                     "entities": [[s, display.get(s, s)] for s in it["entities"]],
                     "sentences": sents})

    tag = a.place or "all"
    print(f"{tag}: {len(picked)} uncached catalogue sources; {len(rows)} with candidates; "
          f"{n_sent} sentences; {n_capped} capped at {MAX_SENTENCES}; {n_missing} unreadable; "
          f"{n_coarse} coarse-dated")
    if a.stats:
        return 0
    out = WORK / "candidates" / tag
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("batch-*.json"):
        old.unlink()
    for k in range(0, len(rows), BATCH_SOURCES):
        p = out / f"batch-{k // BATCH_SOURCES + 1:03d}.json"
        p.write_text(json.dumps(rows[k:k + BATCH_SOURCES], ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"wrote {(len(rows) + BATCH_SOURCES - 1) // BATCH_SOURCES} batches to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
