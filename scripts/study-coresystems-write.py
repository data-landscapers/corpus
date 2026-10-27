#!/usr/bin/env python3
r"""study-coresystems-write.py — the core government systems study's summaries, written from its facts.

    python scripts/study-coresystems-write.py
    python scripts/study-coresystems-write.py --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-offsitebackup-write.py` does
it. **Nothing is composed here that a fact does not state**: each of the five paragraphs is
the drafters' own fact sentences on that aspect, each linked whole to its evidence row's
`url`, the rows that set the stage first, then the rest newest first while the paragraph stays
inside its room. An aspect with nothing found says so, linked to the fact that set the stage.

Writes, per country, `outputs/maturity/coresystems/{ISO3}.md` and
`maturity/coresystems/evidence/{ISO3}/short.json`. Run it after the ladder script.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maturity_words  # noqa: E402
import study_lib  # noqa: E402

STUDY = "coresystems"
SUB = "core"
ROOM = {"finance": 60, "revenue": 50, "payroll": 50, "renewed": 45, "architecture": 35}
DATING = re.compile(r"as_of|article(?:'s)? (?:publication )?date|publication date|\bdate is\b|"
                    r"document date|date used|is used as|no (?:other )?date|the date is|revision date|published year|"
                    r"gives no (?:\w+ )?date|no (?:launch )?date|undated|dated by|date .*not stated|period is used|"
                    r"^(?:but |though |with )?no .*\b(?:given|stated|named|listed)$", re.I)
OPENER = re.compile(r"^(?:the )?(?:article|document|report|page|story|piece|text|release|"
                    r"bidding document|request for bids|ToR)"
                    r"(?: \w+)?(?: \([^)]*\))? (?:says|states|reports|notes)(?: that)? ", re.I)
EMPTY = {
    "finance": "No source found from 2023 or later says the government's financial management system is in use; the nearest held fact is {l}.",
    "revenue": "No source found from 2023 or later says the tax authority's system is in use; the stage rests on {l}.",
    "payroll": "No source found from 2023 or later says the civil-service payroll runs on a computer system; the stage rests on {l}.",
    "renewed": "No source found says the financial, tax or payroll system went live on a new or upgraded system since October 2023; the stage rests on {l}.",
    "architecture": "No source found says the government has published an enterprise architecture or an inventory of its systems; the stage rests on {l}.",
}
def shorten(cell: dict, y: str) -> str:
    """One sentence from what the cell holds: the step that set it, then the main unknown."""
    s, all3 = cell["stage"], all(cell.get(k) == "inuse" for k in ("finance", "revenue", "payroll"))
    if s == "1":
        return f"A {y} source says the government's finances are not run on a computer system."
    if s == "2":
        tail = cell["gaps"].replace("A source found says the", "the").rstrip(".")             if cell["gaps"].startswith("A source found says") else "no source found says whether tax and payroll do too"
        return f"The government budgets and pays through a computer system by {y}; {tail}."
    if s == "3":
        return f"Finance, tax and payroll run on computer systems by {y}; none is known to have been renewed since 2023."
    if s == "4":
        lead = "Finance, tax and payroll systems in use, one" if all3 else "A core government system"
        return f"{lead} renewed in {y}; no published map of government systems is known."
    lead = "Finance, tax and payroll in use, one renewed" if all3 and cell.get("renewed")         else "A core system renewed" if cell.get("renewed") else ""
    if lead:
        return f"{lead}, and a map of government systems published by {y}."
    return f"A map of government systems published by {y}; nothing found says which core systems are in use."




def link(url: str, words: str) -> str:
    return f"[{words.replace('[', '(').replace(']', ')')}](<{url}>)"


def clean(fact: str) -> str:
    parts = [p.strip() for p in re.split(r";\s+|(?<!\bi\.e\.)(?<!\be\.g\.)(?<=[a-z0-9)]\.)\s+(?=[A-Z])", fact.strip()) if p.strip()]
    kept = [p for p in parts if not DATING.search(p.rstrip("."))] or parts[:1]
    text = OPENER.sub("", "; ".join(p.rstrip(".;,") for p in kept))
    return text[:1].upper() + text[1:]


def sentences(rows: list[dict], first: list[str], room: int) -> list[str]:
    order = [r for i in first for r in rows if r["row_id"] == i]
    order += sorted((r for r in rows if r["row_id"] not in first),
                    key=lambda r: (r["as_of"], r["row_id"]), reverse=True)
    out, n, seen = [], 0, set()
    for r in order:
        s = clean(r["fact"])
        if s in seen or (out and n + len(s.split()) > room):
            continue
        seen.add(s)
        out.append(link(r["url"], s) + ".")
        n += len(s.split())
    return out


def write(study: dict, iso: str, country: str, base: str, out_dir: str, dry: bool, ladder) -> str:
    label = study["sub_indicators"][0]["label"]
    here = study_lib.study_dir(STUDY)
    folder = os.path.join(base, iso)
    try:
        with open(os.path.join(folder, "stage.json"), encoding="utf-8") as fh:
            cell = json.load(fh)["cells"][0]
    except OSError:
        raise study_lib.StudyError(f"{iso}: no stage.json; run the ladder script first")
    path = os.path.join(folder, "evidence.csv")
    rows = study_lib.read_csv(path) if os.path.exists(path) else []
    rows, _ = ladder.correct(rows, [f for f in study_lib.read_csv(os.path.join(here, "corrections.csv"))
                                    if f["iso3"] == iso])
    path = os.path.join(folder, "systems.csv")
    systems = study_lib.read_csv(path) if os.path.exists(path) else []
    urls = {r["slug"]: r["url"] for r in study_lib.read_csv(os.path.join(folder, "readlist.csv"))}
    noted, seen = [], set()
    for s in systems:
        url, words = urls.get(s["sources"].split(";")[0], ""), s["system"].strip()
        if url and words and words.lower() not in seen and len(noted) < 6 and s["class"] == "other":
            seen.add(words.lower())
            noted.append(link(url, words))
    src = [i for i in cell["stage_sources"].split(";") if i]
    parts = [f"# {country}", "", f"## {label}", ""]
    if cell["stage"].isdigit():
        top = next(r for r in rows if r["row_id"] == src[0])
        anchor = link(top["url"], "the source that sets it" if cell["stage"] != "1" else "this source")
        for a in study["aspects"]:
            k = a["key"]
            mine = [r for r in rows if r["aspect"] == k]
            body = sentences(mine, [i for i in src if i in {r["row_id"] for r in mine}], ROOM[k])
            if not body:
                body = [EMPTY[k].format(l=anchor)]
            parts += [f"**{a['name']}.** " + " ".join(body), ""]
        short = shorten(cell, top["as_of"][:4])
    elif cell["stage"] == "unplaced" and cell["gaps"].startswith("A source found says"):
        short = cell["gaps"].replace("A source found says the", "The").rstrip(".") + ", so no stage is set."
    elif cell["stage"] == "unplaced":
        short = "No source found from 2023 or later says the government's financial system is in use, so no stage is set."
    else:
        short = "Nothing found says whether the government's finance, tax or payroll systems are in use, so no stage is set."
    parts += [maturity_words.ALSO_ON_FILE_LABEL + ". " + ("; ".join(noted) + "." if noted else maturity_words.NONE_FOUND), "",
              maturity_words.NOT_FOUND_LABEL + ". " + (cell["gaps"] or "Nothing further is asked of this indicator."), ""]
    if not dry:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, iso + ".md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(maturity_words.rewrite("\n".join(parts)))
        with open(os.path.join(folder, "short.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({SUB: maturity_words.rewrite(short)}, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    return cell["stage"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write the core government systems study's summaries.")
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    spec = importlib.util.spec_from_file_location(
        "ladder", os.path.join(os.path.dirname(os.path.abspath(__file__)), "study-ladder-coresystems.py"))
    ladder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ladder)
    try:
        study = study_lib.load(STUDY)
        here = study_lib.study_dir(STUDY)
        base = os.path.join(here, "evidence")
        names = study_lib.countries()
        for iso in sorted(names):
            write(study, iso, names[iso]["name"], base, study_lib.out_dir(STUDY), a.dry, ladder)
    except study_lib.StudyError as e:
        print(f"study-coresystems-write: {e}")
        return 2
    print(f"study-coresystems-write: {len(names)} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
