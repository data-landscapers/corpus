#!/usr/bin/env python3
r"""
hero-batch.py — prepare and check a batch of `catalogue_hero` subtitles for OSINT to apply.

    python scripts/hero-batch.py prepare --n 200 --sample --out work/hero-00-in.jsonl
    python scripts/hero-batch.py prepare --n 2000 --out work/hero-01-in.jsonl
    python scripts/hero-batch.py check X:\prepared\hero-00.jsonl

**Strategic review 4, R28 and R30.** `catalogue_hero` is the subtitle every catalogue row
shows; 16,787 records ingested before the field was minted carry none. Corpus writes them on
Sonnet (Bill's ruling R2, for this job only) and delivers `{"slug","hero"}` per line to
`X:\prepared\hero-NN.jsonl`; OSINT's `catalogue-hero-set.py` dry-runs and writes them.

**`prepare`** reads `raw/` through the workroot, keeps records with no hero, and writes one
input line per record: slug, title, publisher, published, places, and the text a hero is
written from — the record's `note:` where it has one, the first `BODY_CHARS` of its body
otherwise. `--sample` draws at random (seeded) so Bill judges the population, not its newest
corner; without it the batch is newest first, as R30 runs. Slugs in any `hero-*.jsonl` already
on `X:\prepared\` are skipped, so batches never overlap.

**`check`** holds a written batch to the contract in OSINT's `wiki/schemas.md` §4: one line,
at most 120 characters, no terminal full stop, no markdown or wikilinks, not the title
restated, no talk of the record rather than the document, and a slug that exists and still
lacks a hero. It reports; it does not repair.

`documentation/hero-brief.md` is the brief the writing agents are given.
"""
import argparse
import glob
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib  # noqa: E402
import vault_lib as V  # noqa: E402

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".workroot", "raw")
PREPARED = os.path.join(status_lib.EXCHANGE, "prepared")
BODY_CHARS = 3000
CAP = 120


def records():
    """{slug: (frontmatter, body)} for every `raw/` source."""
    out = {}
    for path in glob.glob(os.path.join(RAW, "**", "*.md"), recursive=True):
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        fm = V.parse_frontmatter(text)
        fm = fm[0] if isinstance(fm, tuple) else fm
        body = text.split("\n---", 2)[-1] if text.startswith("---") else text
        out[os.path.splitext(os.path.basename(path))[0]] = (fm or {}, body.strip())
    return out


def delivered() -> set:
    seen = set()
    for path in glob.glob(os.path.join(PREPARED, "hero-*.jsonl")):
        with open(path, encoding="utf-8") as fh:
            seen |= {json.loads(l)["slug"] for l in fh if l.strip()}
    return seen


def prepare(a) -> int:
    recs, done = records(), delivered()
    todo = [s for s, (fm, _) in recs.items() if not fm.get("catalogue_hero") and s not in done]
    if a.sample:
        random.Random(a.seed).shuffle(todo)
    else:
        todo.sort(key=lambda s: (str(recs[s][0].get("published") or ""), s), reverse=True)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for s in todo[:a.n]:
            fm, body = recs[s]
            note = fm.get("note")
            fh.write(json.dumps({
                "slug": s,
                "title": fm.get("title") or "",
                "publisher": fm.get("publisher") or "",
                "published": str(fm.get("published") or ""),
                "places": V.as_list(fm.get("places")),
                "from": "note" if note else "body",
                "text": note if note else body[:BODY_CHARS],
            }, ensure_ascii=False) + "\n")
    print(f"{min(a.n, len(todo))} of {len(todo)} records without a hero -> {a.out}")
    return 0


def problems(hero: str, title: str) -> list:
    out = []
    if not hero.strip():
        return ["empty"]
    if len(hero) > CAP:
        out.append(f"{len(hero)} chars")
    if "\n" in hero:
        out.append("more than one line")
    if hero.rstrip().endswith("."):
        out.append("terminal full stop")
    if re.search(r"\[\[|\*\*|__|`|\]\(", hero):
        out.append("markdown")
    norm = lambda t: re.sub(r"\W+", " ", t.lower()).strip()  # noqa: E731
    if re.search(r"stub|captured|held elsewhere|cite_through|excerpt", hero, re.I):
        out.append("speaks of the record, not the document")
    if title and (norm(hero) == norm(title) or norm(hero) in norm(title)):
        out.append("restates the title")
    return out


def check(a) -> int:
    recs = records()
    bad, n, seen = 0, 0, set()
    with open(a.file, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            if not line.strip():
                continue
            n += 1
            try:
                row = json.loads(line)
                slug, hero = row["slug"], row["hero"]
            except (ValueError, KeyError) as e:
                print(f"line {i}: unreadable ({e})")
                bad += 1
                continue
            why = []
            if set(row) != {"slug", "hero"}:
                why.append(f"keys {sorted(row)}")
            if slug in seen:
                why.append("duplicate slug")
            seen.add(slug)
            if slug not in recs:
                why.append("no such record")
            elif recs[slug][0].get("catalogue_hero"):
                why.append("already has a hero")
            why += problems(hero, str(recs.get(slug, ({}, ""))[0].get("title") or ""))
            if why:
                bad += 1
                print(f"line {i} {slug}: {'; '.join(why)}\n    {hero}")
    print(f"hero-batch check: {n} line(s), {bad} with problems")
    return 1 if bad else 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--sample", action="store_true")
    p.add_argument("--seed", type=int, default=28)
    p.add_argument("--out", required=True)
    c = sub.add_parser("check")
    c.add_argument("file")
    a = ap.parse_args()
    return prepare(a) if a.cmd == "prepare" else check(a)


if __name__ == "__main__":
    sys.exit(main())
