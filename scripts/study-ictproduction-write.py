#!/usr/bin/env python3
r"""study-ictproduction-write.py — the ICT production study's summaries, written from its figures.

    python scripts/study-ictproduction-write.py
    python scripts/study-ictproduction-write.py --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-mobile-write.py` does it. The
study holds one figure a country and its earlier years, and for a country past 0.5 per cent the
drafters' facts on a plant, so **what there is to say is arithmetic and the drafters' own
sentences**: the latest share, the years before it, how far it stands from the next line, and
any plant fact, linked whole.

Writes, per country, `outputs/maturity/ictproduction/{ISO3}.md` and
`maturity/ictproduction/evidence/{ISO3}/short.json`. Run it after the ladder script.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maturity_words  # noqa: E402
import study_lib  # noqa: E402

STUDY = "ictproduction"
SUB = "production"
LINES = (0.05, 0.2, 0.5)
PLANT_FROM = "2023-10"


def link(url: str, words: str) -> str:
    return f"[{words}](<{url}>)"


def num(value: str) -> float:
    return float(value.split(":", 1)[1])


def listed(parts: list[str]) -> str:
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def exports_paragraph(name: str, country: str, rows: list[dict], best: dict) -> str:
    series = sorted((r for r in rows if r["source_slug"] == best["source_slug"]), key=lambda r: r["as_of"])
    figure, year, url = num(best["value"]), best["as_of"][:4], best["url"]
    out = [f"**{name}.**",
           f"In {year}, {link(url, f'ICT service exports from {country} were {figure:g} per cent of GDP')}, "
           f"by the World Bank's series of computer and telecommunications services sold abroad."]
    before = [r for r in series if "2021" <= r["as_of"] < best["as_of"]]
    if before:
        steps = listed([f"{num(r['value']):g} per cent in {r['as_of'][:4]}" for r in before])
        out.append(f"The same series {link(url, 'put the share at ' + steps)}.")
        moved = figure - num(before[0]["value"])
        how = "has barely moved" if abs(moved) < 0.005 else f"{'rose' if moved > 0 else 'fell'} by {abs(moved):.2f} points"
        out.append(f"Since {before[0]['as_of'][:4]} the share {how}.")
    else:
        out.append("The series gives no figure for the years just before, so no source found says "
                   "whether the share is rising or falling.")
    ahead = [line for line in LINES if figure < line]
    if ahead:
        out.append(f"The share is {ahead[0] - figure:.2f} points short of {ahead[0]:g} per cent, the next line.")
    else:
        out.append("At 0.5 per cent or more, the share is past the study's highest line for exports.")
    out.append("The figure counts computer and telecommunications services sold abroad, not equipment "
               "made or assembled at home.")
    return " ".join(out)


def plant_paragraph(name: str, plants: list[dict], cleared: bool, url: str) -> str:
    out = [f"**{name}.**"]
    if plants:
        for r in plants[:4]:
            out.append(link(r["url"], r["fact"].rstrip(".")) + ".")
    elif cleared:
        out.append(f"No source found since October 2023 says phones, computers or other ICT equipment are "
                   f"assembled or made in the country; {link(url, 'exports alone')} set the stage.")
    else:
        out.append(f"A plant is asked about only once exports reach 0.5 per cent of GDP, so with "
                   f"{link(url, 'exports below that line')} none was looked for in this first pass.")
    return " ".join(out)


def write(study: dict, iso: str, country: str, base: str, out_dir: str, dry: bool) -> str:
    names = {a["key"]: a["name"] for a in study["aspects"]}
    label = study["sub_indicators"][0]["label"]
    folder = os.path.join(base, iso)
    try:
        with open(os.path.join(folder, "stage.json"), encoding="utf-8") as fh:
            cell = json.load(fh)["cells"][0]
    except OSError:
        raise study_lib.StudyError(f"{iso}: no stage.json; run the ladder script first")
    rows = study_lib.read_csv(os.path.join(folder, "evidence.csv"))
    exports = [r for r in rows if r["aspect"] == "exports"]
    plants = sorted((r for r in rows if r["aspect"] == "plant" and r["value"] == "production"
                     and r["as_of"] >= PLANT_FROM), key=lambda r: r["as_of"], reverse=True)
    srcs = cell["stage_sources"].split(";")
    plants = [r for r in plants if r["row_id"] in srcs] + [r for r in plants if r["row_id"] not in srcs]
    urls = {r["slug"]: r["url"] for r in study_lib.read_csv(os.path.join(folder, "readlist.csv"))}
    noted, seen = [], set()
    for s in study_lib.read_csv(os.path.join(folder, "systems.csv")):
        url = urls.get(s["sources"], "")
        words = ": ".join(x for x in (s["system"].strip(), s["country_label"].strip()) if x)
        if s["class"] == "other" and url and words and words not in seen:
            seen.add(words)
            noted.append(link(url, words.replace("[", "(").replace("]", ")")))
    parts = [f"# {country}", "", f"## {label}", ""]
    if cell["stage"].isdigit():
        best = next(r for r in exports if r["row_id"] == srcs[0])
        figure, year = num(best["value"]), best["as_of"][:4]
        cleared = figure >= LINES[-1]
        parts += [exports_paragraph(names["exports"], country, exports, best), "",
                  plant_paragraph(names["plant"], plants, cleared, best["url"]), ""]
        if cell["stage"] == "5":
            short = f"ICT service exports were {figure:g} per cent of GDP in {year}, and ICT equipment is assembled in the country."
        else:
            short = f"ICT service exports were {figure:g} per cent of GDP in {year}, by the World Bank's series."
        ahead = [line for line in LINES if figure < line]
        if ahead:
            held = f"No figure of {ahead[0]:g} per cent of GDP or more has been found."
        elif cell["stage"] != "5":
            held = cell["gaps"]
        else:
            held = "Nothing further is asked of this indicator."
    else:
        old = sorted(exports, key=lambda r: r["as_of"])
        held = cell["gaps"]
        if old:
            held += f" The latest held is {num(old[-1]['value']):g} per cent, for {old[-1]['as_of'][:4]}."
        short = "No figure for ICT service exports has been found for 2023 or later, so no stage is set."
    parts += [maturity_words.ALSO_ON_FILE_LABEL + ". " + ("; ".join(noted) + "." if noted else maturity_words.NONE_FOUND), "",
              maturity_words.NOT_FOUND_LABEL + ". " + held, ""]
    if not dry:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, iso + ".md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(maturity_words.rewrite("\n".join(parts)))
        with open(os.path.join(folder, "short.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({SUB: maturity_words.rewrite(short)}, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    return cell["stage"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write the ICT production study's summaries.")
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    try:
        study = study_lib.load(STUDY)
        base = os.path.join(study_lib.study_dir(STUDY), "evidence")
        names = study_lib.countries()
        n = 0
        for iso in sorted(names):
            write(study, iso, names[iso]["name"], base, study_lib.out_dir(STUDY), a.dry)
            n += 1
    except study_lib.StudyError as e:
        print(f"study-ictproduction-write: {e}")
        return 2
    print(f"study-ictproduction-write: {n} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
