#!/usr/bin/env python3
r"""study-cybersecurity-write.py — the national cyber response study's summaries, written from its facts.

    python scripts/study-cybersecurity-write.py
    python scripts/study-cybersecurity-write.py --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-offsitebackup-write.py` does
it. **Nothing is composed here that a fact does not state**: each of the four paragraphs is
the drafters' own fact sentences on that aspect, each linked whole to its evidence row's
`url`, the rows that set the stage first, then the rest newest first while the paragraph stays
inside its room. An aspect with nothing found says so, linked to the fact that set the stage.

Writes, per country, `outputs/maturity/cybersecurity/{ISO3}.md` and
`maturity/cybersecurity/evidence/{ISO3}/short.json`. Run it after the ladder script.

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

STUDY = "cybersecurity"
SUB = "readiness"
WINDOW = "2023-10"   # three years before the as-at, method §3.4
ROOM = {"foundation": 60, "response": 60, "cii": 50, "figures": 50}
DATING = re.compile(r"as_of|article(?:'s)? (?:publication )?date|publication date|\bdate is\b|"
                    r"document date|date used|is used as|no (?:other )?date|the date is|revision date|published year|"
                    r"gives no (?:\w+ )?date|no (?:launch )?date|undated|dated by|date .*not stated|period is used|"
                    r"^(?:but |though |with )?no .*\b(?:given|stated|named|listed)$", re.I)
OPENER = re.compile(r"^(?:the )?(?:article|document|report|page|story|piece|text|release|"
                    r"bidding document|request for bids|ToR)"
                    r"(?: \w+)?(?: \([^)]*\))? (?:says|states|reports|notes)(?: that)? ", re.I)
ASIDE = re.compile(r"\s*\((?=[^)]*\b(?:date|dated|as_of|inferred|publication|published)\b)[^)]*\)", re.I)
EMPTY = {
    "foundation": "No source found says the country adopted a national cybersecurity strategy or created a national cyber agency or response team; the stage rests on {l}.",
    "response": "No source found says the national body handled an incident or issued a public alert since October 2023, so no response to an attack is on record; the stage rests on {l}.",
    "cii": "No source found says the country designated its critical information infrastructure or required the operators of its critical systems to report incidents to the national body; the stage rests on {l}.",
    "figures": "No source found says the national body published a count of the incidents it handled for a quarter or more ending in the last two years; the stage rests on {l}.",
}


def shorten(cell: dict, y: str) -> str:
    """One sentence from what the cell holds: the step that set it, then the main unknown."""
    s = cell["stage"]
    if s == "1":
        return f"A {y} source says the country has no cybersecurity strategy and no national cyber body."
    if s == "2":
        what = "a national cyber body" if cell.get("foundation") == "body" else "a cybersecurity strategy"
        return f"The country had {what} by {y}; no incident response by a national body is known since 2023."
    if s == "3":
        return f"The national cyber body responded to an incident or issued an alert in {y}; no critical infrastructure designation is known."
    if s == "4":
        return f"Critical information infrastructure designated by {y}; the national body publishes no recent incident count that is known."
    return f"The national cyber body published a count of incidents handled for a period to {y}."


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
        if r["as_of"][:7] < WINDOW:
            s += f" ({r['as_of'][:4]}, before the three-year window)"   # so the reader sees why it does not count
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
    elif cell["stage"] == "unplaced":
        short = "No source found says whether the country has a cybersecurity strategy or a national cyber body, so no stage is set."
    else:
        short = "Nothing found says whether the country has a national cyber response, so no stage is set."
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
    ap = argparse.ArgumentParser(description="Write the national cyber response study's summaries.")
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    spec = importlib.util.spec_from_file_location(
        "ladder", os.path.join(os.path.dirname(os.path.abspath(__file__)), "study-ladder-cybersecurity.py"))
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
        print(f"study-cybersecurity-write: {e}")
        return 2
    print(f"study-cybersecurity-write: {len(names)} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
