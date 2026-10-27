#!/usr/bin/env python3
r"""study-datacentrepower-write.py — the data-centre power study's summaries, written from its facts.

    python scripts/study-datacentrepower-write.py
    python scripts/study-datacentrepower-write.py --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-offsitebackup-write.py`
does it. **Nothing is composed here that a fact does not state**: each paragraph is the
drafters' own fact sentences, each linked whole to its evidence row's `url`, the rows that set
the stage first, then the rest newest first while the paragraph stays inside its room. Systems
named and not staged go in *Also on file*.

Writes, per country, `outputs/maturity/datacentrepower/{ISO3}.md` and
`maturity/datacentrepower/evidence/{ISO3}/short.json`. Run it after the ladder script.

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

STUDY = "datacentrepower"
SUB = "power"
SUPPLY_ROOM, PUE_ROOM, WATER_ROOM = 120, 50, 50
DATING = re.compile(r"as_of|article(?:'s)? (?:publication )?date|publication date|\bdate is\b|"
                    r"document date|date used|is used as|no (?:other )?date|the date is|revision date|published year|"
                    r"gives no (?:\w+ )?date|no (?:launch )?date|undated|dated by|date .*not stated|period is used|"
                    r"^(?:but |though |with )?no .*\b(?:given|stated|named|listed)$", re.I)
OPENER = re.compile(r"^(?:the )?(?:article|document|report|page|story|piece|text|release|"
                    r"bidding document|request for bids|ToR)"
                    r"(?: \w+)?(?: \([^)]*\))? (?:says|states|reports|notes)(?: that)? ", re.I)
RESTS = {
    "5": "These place a data centre on a secured supply, with power set aside for data centres.",
    "4": "These place a data centre on a secured supply, with power set aside for data centres.",
    "3": "These place a data centre on a secured supply, with power set aside for data centres.",
    "2": "These place a data centre on a secured supply. No source found says power is set aside for data centres.",
    "1": "A dated statement that a data centre went short of power or water sets the lowest stage, "
         "and no source found places one on a secured supply.",
}
SHORT = {
    "5": "A data centre on secured power by {y}, with a PUE of 1.6 or less and its water use published.",
    "4": "A data centre on secured power by {y}, with a PUE of 1.6 or less stated; water use not known.",
    "3": "A data centre on secured power and power set aside for data centres by {y}; no PUE of 1.6 or less held.",
    "2": "A data centre on a secured power supply by {y}; no power set aside for data centres is known.",
    "1": "A {y} source says a data centre went short of power or water.",
}


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
        if s in seen or (r["row_id"] not in first and out and n + len(s.split()) > room):
            continue
        seen.add(s)
        out.append(link(r["url"], s) + ".")
        n += len(s.split())
    return out


def write(study: dict, iso: str, country: str, base: str, out_dir: str, dry: bool, ladder) -> str:
    supply_name, pue_name, water_name = (x["name"] for x in study["aspects"])
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
    noted, seen = [], {r["system"].strip() for r in rows}
    for s in systems:
        url, words = urls.get(s["sources"], ""), s["system"].strip()
        if url and words and words not in seen and len(noted) < 6:
            seen.add(words)
            noted.append(link(url, words))
    src = [i for i in cell["stage_sources"].split(";") if i]
    parts = [f"# {country}", "", f"## {label}", ""]
    if cell["stage"].isdigit():
        top = next(r for r in rows if r["row_id"] == src[0])
        of = lambda asp: [r for r in rows if r["aspect"] == asp]  # noqa: E731
        mine = lambda rs: [i for i in src if i in {r["row_id"] for r in rs}]  # noqa: E731
        body = sentences(of("supply"), mine(of("supply")), SUPPLY_ROOM)
        pu = sentences(of("pue"), mine(of("pue")), PUE_ROOM) or \
            [f"No source found from the past three years states a PUE of 1.6 or less for "
             f"{link(top['url'], top['system'].strip())} or any other data centre in service."]
        wa = sentences(of("water"), mine(of("water")), WATER_ROOM) or \
            [f"No source found from the past three years states the water use of "
             f"{link(top['url'], top['system'].strip())} or any other data centre in service, "
             f"or cooling that uses none."]
        parts += [f"**{supply_name}.** " + " ".join(body + [RESTS[cell["stage"]]]), "",
                  f"**{pue_name}.** " + " ".join(pu), "",
                  f"**{water_name}.** " + " ".join(wa), ""]
        short = SHORT[cell["stage"]].format(y=top["as_of"][:4])
    elif cell["stage"] == "unplaced":
        short = "No data centre is known to have a secured power supply, so no stage is set."
    else:
        short = "Nothing found says how data centres get power or water, so no stage is set."
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
    ap = argparse.ArgumentParser(description="Write the data-centre power study's summaries.")
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    spec = importlib.util.spec_from_file_location(
        "ladder", os.path.join(os.path.dirname(os.path.abspath(__file__)), "study-ladder-datacentrepower.py"))
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
        print(f"study-datacentrepower-write: {e}")
        return 2
    print(f"study-datacentrepower-write: {len(names)} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
