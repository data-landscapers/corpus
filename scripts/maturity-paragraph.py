#!/usr/bin/env python3
r"""maturity-paragraph.py — the maturity paragraph: what a writer is given, what is kept, how many stand.

Strategic review 8, R153 and R162 *(Bill, 2026-11-26)*. Each cell with evidence gets one paragraph
of 60 to 130 words under its stage, written under `maturity/documentation/paragraph-brief.md`
from the facts and links its `{ISO3}.md` section already holds. `maturity_words.py` holds the
rules of the file it lands in, `outputs/maturity/{id}/paragraphs.csv`; this is the instrument.

    python scripts/maturity-paragraph.py packet [--study ID ...] [--country ISO3] --out DIR
    python scripts/maturity-paragraph.py apply FILE.json ...      # keep what passes; say why not
    python scripts/maturity-paragraph.py apply --dry FILE.json    # the writer's own check; writes nothing
    python scripts/maturity-paragraph.py count [--study ID ...]   # fresh / stale / missing

**`packet`** writes `DIR/{id}.json` for each study with a cell whose paragraph is missing or
stale: the country, the indicator, the stage and the next stage's test in the ladder's own
criteria, the moves of the last twelve months from `history.csv`, `gaps`, and the section. A
cell with no evidence gets no paragraph; its short line stands.

**`apply`** reads a writer's `{ "ISO3|indicator_id": "paragraph", ... }`, written beside the
packet as `{id}.out.json`, and keeps a paragraph only if it passes: the band, `lint-prose.py`'s
numbers and words, no link the section does not already carry, a sentence on the last twelve
months, and a close on what the next stage would need. A paragraph that fails is not written;
its reasons go to `{id}.rejects.json`, and the next `packet` offers the cell again.

**`count`** is the status line's measure: evidence cells whose paragraph is fresh, of all
evidence cells, with stale and missing beside it.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import maturity_words as mw  # noqa: E402

ISSUED = os.path.join(ROOT, "outputs", "maturity")
STUDIES = os.path.join(ROOT, "maturity")
COUNTRIES = os.path.join(ROOT, "lookups", "countries.csv")
NO_EVIDENCE = "no evidence"
LINK = re.compile(r"\]\(<?([^)>\s]+)>?\)")


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lp = _load("lint_prose", "lint-prose.py")


def read_csv(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def sections(text: str) -> dict[str, str]:
    """{`## ` heading: body} of a cell file."""
    out, head, buf = {}, None, []
    for ln in text.splitlines():
        if ln.startswith("## ") and not ln.startswith("###"):
            if head is not None:
                out[head] = "\n".join(buf).strip()
            head, buf = ln[3:].strip(), []
        elif head is not None:
            buf.append(ln)
    if head is not None:
        out[head] = "\n".join(buf).strip()
    return out


def studies(only: list[str] | None) -> list[dict]:
    out = []
    for sj in sorted(glob.glob(os.path.join(STUDIES, "*", "study.json"))):
        with open(sj, encoding="utf-8") as fh:
            s = json.load(fh)
        if only and s["id"] not in only:
            continue
        if os.path.exists(os.path.join(ISSUED, s["id"], "assessment.csv")):
            out.append(s)
    return out


def cells(s: dict, country: str | None = None):
    """(row, section, sub) for every evidence cell of a study."""
    issued = os.path.join(ISSUED, s["id"])
    subs = {sub["indicator_id"]: sub for sub in s.get("sub_indicators", [])}
    by_label = {sub["label"]: sub["indicator_id"] for sub in subs.values()}
    cache: dict[str, dict] = {}
    for r in read_csv(os.path.join(issued, "assessment.csv")):
        iso, iid, stage = r["iso3"], r["indicator_id"], r["stage"].strip()
        if stage == NO_EVIDENCE or (country and iso != country) or iid not in subs:
            continue
        if iso not in cache:
            p = os.path.join(issued, f"{iso}.md")
            text = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
            cache[iso] = {by_label[h]: b for h, b in sections(text).items() if h in by_label}
        yield r, cache[iso].get(iid, ""), subs[iid]


def next_test(stage: str, sub: dict) -> list[str]:
    """The criteria the writer closes on: the next rung's, or every rung's for an unplaced cell."""
    crit = sub.get("criteria", [])
    if stage.isdigit():
        n = int(stage)
        return [f"{n + 1} {mw.STAGE_NAMES[n + 1]}: {crit[n]}"] if n < 5 and len(crit) > n else []
    return [f"{i} {mw.STAGE_NAMES[i]}: {c}" for i, c in enumerate(crit, 1)]


def packet(args) -> int:
    names = {c["iso-3"]: c["country-name"] for c in read_csv(COUNTRIES)}
    since = (dt.date.today() - dt.timedelta(days=365)).isoformat()
    os.makedirs(args.out, exist_ok=True)
    total = 0
    for s in studies(args.study):
        issued = os.path.join(ISSUED, s["id"])
        paras = mw.read_paragraphs(issued)
        hist = read_csv(os.path.join(issued, "history.csv"))
        work = []
        for r, section, sub in cells(s, args.country):
            key = (r["iso3"], r["indicator_id"])
            if mw.paragraph_state(paras.get(key), r["stage"].strip(), section) == "fresh":
                continue
            stage = r["stage"].strip()
            work.append(dict(
                key=f"{r['iso3']}|{r['indicator_id']}", country=names.get(r["iso3"], r["iso3"]),
                indicator=sub["label"], stage=stage,
                stage_name=mw.STAGE_NAMES.get(int(stage), "") if stage.isdigit() else "not staged",
                as_at=r.get("as_at", ""), short=r.get("short", ""), gaps=r.get("gaps", ""),
                next=next_test(stage, sub),
                changes=[{k: h[k] for k in ("date", "kind", "from", "to", "note")} for h in hist
                         if h["iso3"] == r["iso3"] and h["indicator_id"] == r["indicator_id"]
                         and h["date"] >= since],
                section=section))
        if args.limit:
            work = work[:args.limit]
        if work:
            with open(os.path.join(args.out, f"{s['id']}.json"), "w", encoding="utf-8") as fh:
                json.dump(dict(study=s["id"], today=dt.date.today().isoformat(), cells=work), fh,
                          ensure_ascii=False, indent=1)
            total += len(work)
            print(f"{s['id']}: {len(work)} cell(s)")
    print(f"maturity-paragraph: {total} cell(s) to write -> {args.out}")
    return 0


def problems(text: str, stage: str, section: str) -> list[str]:
    """Why a paragraph cannot be kept; empty when it can."""
    out = []
    res = lp.check([text], "paragraph")
    out += [f"lint:{f}" for f in res["fails"]]
    held = set(LINK.findall(section))
    stray = [u for u in LINK.findall(text) if u not in held]
    if stray:
        out.append(f"link not in the section: {stray[0]}")
    if not LINK.search(text):
        out.append("no link")
    if "twelve months" not in text:
        out.append("no sentence on the last twelve months")
    last = lp.sentences(lp.plain(text))[-1] if text.strip() else ""
    if stage.isdigit() and int(stage) < 5:
        nxt = mw.STAGE_NAMES[int(stage) + 1]
        if nxt not in last or "would need" not in last:
            out.append(f"does not close on what {nxt} would need")
    elif not stage.isdigit() and "would need" not in last:
        out.append("does not close on what a stage would need")
    if "\n" in text.strip():
        out.append("more than one paragraph")
    return out


def apply(args) -> int:
    kept = bad = 0
    for f in args.files:
        sid = os.path.basename(f).split(".")[0]
        s = next(iter(studies([sid])), None)
        if s is None:
            print(f"{f}: no study {sid}")
            bad += 1
            continue
        with open(f, encoding="utf-8") as fh:
            got = json.load(fh)
        issued = os.path.join(ISSUED, sid)
        paras = mw.read_paragraphs(issued)
        cellmap = {f"{r['iso3']}|{r['indicator_id']}": (r, sec) for r, sec, _ in cells(s)}
        rejects = {}
        for key, text in got.items():
            text = re.sub(r"\s+", " ", str(text)).strip()
            if key not in cellmap:
                rejects[key] = ["no such evidence cell"]
                continue
            r, section = cellmap[key]
            why = problems(text, r["stage"].strip(), section)
            if why:
                rejects[key] = why
                continue
            iso, iid = key.split("|")
            if args.dry:
                kept += 1
                continue
            paras[(iso, iid)] = dict(iso3=iso, indicator_id=iid, stage=r["stage"].strip(),
                                     digest=mw.digest(section), written=dt.date.today().isoformat(),
                                     paragraph=text)
            kept += 1
        if args.dry:
            for key, why in rejects.items():
                print(f"  {key}: {'; '.join(why)}")
            print(f"{sid}: {len(got) - len(rejects)} would be kept, {len(rejects)} refused")
            bad += len(rejects)
            continue
        mw.write_paragraphs(issued, paras)
        stem = os.path.basename(f)[:-len(".out.json")] if f.endswith(".out.json") else sid
        rj = os.path.join(os.path.dirname(f), f"{stem}.rejects.json")
        if rejects:
            with open(rj, "w", encoding="utf-8") as fh:
                json.dump(rejects, fh, ensure_ascii=False, indent=1)
        elif os.path.exists(rj):
            os.remove(rj)
        bad += len(rejects)
        print(f"{sid}: {len(got) - len(rejects)} kept, {len(rejects)} rejected")
    print(f"maturity-paragraph: {kept} kept, {bad} rejected")
    return 0


def tally(only=None) -> dict:
    n = {"fresh": 0, "stale": 0, "missing": 0}
    for s in studies(only):
        paras = mw.read_paragraphs(os.path.join(ISSUED, s["id"]))
        for r, section, _ in cells(s):
            n[mw.paragraph_state(paras.get((r["iso3"], r["indicator_id"])), r["stage"].strip(), section)] += 1
    return n


def count(args) -> int:
    n = tally(args.study)
    total = sum(n.values())
    print(f"paragraphs: {n['fresh']} of {total} fresh; {n['stale']} stale, {n['missing']} missing")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("packet")
    p.add_argument("--study", nargs="*")
    p.add_argument("--country")
    p.add_argument("--out", required=True)
    p.add_argument("--limit", type=int, default=0)
    a = sub.add_parser("apply")
    a.add_argument("files", nargs="+")
    a.add_argument("--dry", action="store_true", help="say what would be kept and why not; write nothing")
    c = sub.add_parser("count")
    c.add_argument("--study", nargs="*")
    args = ap.parse_args()
    return {"packet": packet, "apply": apply, "count": count}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
