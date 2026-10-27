#!/usr/bin/env python3
r"""study-censuses-write.py — the censuses study's summaries, written from its facts.

    python scripts/study-censuses-write.py
    python scripts/study-censuses-write.py --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-statisticsstrategy-write.py` does
it. **Nothing is composed here that a fact does not state**: each of the three paragraphs is
the drafters' own fact sentences on that aspect, each linked whole to its evidence row's
`url`, the rows that set the stage first, then the rest newest first while the paragraph stays
inside its room. An aspect with nothing found says so, linked to the fact that set the stage.

Writes, per country, `outputs/maturity/censuses/{ISO3}.md` and
`maturity/censuses/evidence/{ISO3}/short.json`. Run it after the ladder script.

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

STUDY = "censuses"
SUB = "census"
WINDOW = {"census:preparing": ("2023-10", "three"), "census:taken": ("2016-10", "ten"),
          "results:final": ("2016-10", "ten"), "survey:published": ("2023-10", "three")}   # study §2
ROOM = {"census": 90, "results": 60, "survey": 60}
DATING = re.compile(r"as_of|article(?:'s)? (?:publication )?date|publication date|\bdate is\b|"
                    r"document date|date used|is used as|no (?:other )?date|the date is|revision date|published year|"
                    r"gives no (?:\w+ )?date|no (?:launch )?date|undated|dated by|date .*not stated|period is used|"
                    r"^(?:but |though |with )?no .*\b(?:given|stated|named|listed)$", re.I)
OPENER = re.compile(r"^(?:the )?(?:article|document|report|page|story|piece|text|release|table)"
                    r"(?: \w+)?(?: \([^)]*\))? (?:says|states|reports|notes)(?: that)? ", re.I)
ASIDE = re.compile(r"\s*\((?=[^)]*\b(?:date|dated|as_of|inferred|publication|published)\b)[^)]*\)", re.I)
EMPTY = {
    "census": "No source found says a population census was counted since October 2016 or is being prepared. The nearest held fact: {l}.",
    "results": "No source found reports final results of a census counted since October 2016. The nearest held fact: {l}.",
    "survey": "No source found reports results of a national household survey published since October 2023. The nearest held fact: {l}.",
}


def shorten(cell: dict, y: str, top: dict) -> str:
    """One sentence from what the cell holds: the step that set it, then the main unknown."""
    s, name = cell["stage"], census_name(top)
    if s == "1":
        return f"A {y} source says no census has been counted in ten years and none is being prepared."
    if s == "2":
        return f"A population census was being prepared in {y}; none counted since 2016 is known."
    if s == "3":
        return f"{name[:1].upper() + name[1:]} was counted in {y}; no source found reports its final results to be out."
    if s == "4":
        return f"Final results of {name} were published in {y}; no household survey published since 2023 is known."
    return f"A national household survey published results in {y}, after final census results."


def census_name(r: dict) -> str:
    n = r.get("system", "").strip()
    if not n or len(n) > 50:
        return "the population census"
    return n if n.lower().startswith("the ") else "the " + n


def link(url: str, words: str) -> str:
    return f"[{words.replace('[', '(').replace(']', ')')}](<{url}>)"


def clean(fact: str) -> str:
    fact = ASIDE.sub("", fact)
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
        since, span = WINDOW.get(f"{r['aspect']}:{r['value']}", ("", ""))
        if (r["as_of"] + "-12")[:7] < since:   # a year stands for its last month, as the ladder reads it
            s += f" ({r['as_of'][:4]}, before the {span}-year window)"   # so the reader sees why it does not count
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
        anchor = link(top["url"], clean(top["fact"]))
        used = False   # writer brief: an empty aspect states the nearest held fact
        for a in study["aspects"]:
            k = a["key"]
            mine = [r for r in rows if r["aspect"] == k]
            body = sentences(mine, [i for i in src if i in {r["row_id"] for r in mine}], ROOM[k])
            if not body:   # the nearest held fact is linked once; a second empty aspect points back to it
                body = [EMPTY[k].format(l=anchor if not used else link(top["url"], "the one given above"))]
                used = True
                named = list(dict.fromkeys(link(urls[x["sources"].split(";")[0]], x["system"].strip()) for x in systems
                                           if x["class"] == "survey" and x["system"].strip()
                                           and urls.get(x["sources"].split(";")[0])))[:4]
                if k == "survey" and named:   # surveys the reading named, with no dated results
                    body.append("Named in what was read, with no results dated: " + "; ".join(named) + ".")
            if k == "census" and len(rows) <= 5:   # few facts held: say so, as the statistics law study did
                body.append(("It is the only fact" if len(rows) == 1 else f"{['', '', 'Two', 'Three', 'Four', 'Five'][len(rows)]} facts are")
                            + " held on the country's census and surveys" + ("" if len(rows) == 1 else ", all given here")
                            + ": no news story or official notice read for this study says more, and the census and survey reports themselves were not read.")
            parts += [f"**{a['name']}.** " + " ".join(body), ""]
        short = shorten(cell, top["as_of"][:4], top)
    elif cell["stage"] == "unplaced":
        short = "No census counted since 2016 or in preparation is on record, so no stage is set."
    else:
        short = "Nothing found says whether the country has counted or is preparing a census, so no stage is set."
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
    ap = argparse.ArgumentParser(description="Write the censuses study's summaries.")
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    spec = importlib.util.spec_from_file_location(
        "ladder", os.path.join(os.path.dirname(os.path.abspath(__file__)), "study-ladder-censuses.py"))
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
        print(f"study-censuses-write: {e}")
        return 2
    print(f"study-censuses-write: {len(names)} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
