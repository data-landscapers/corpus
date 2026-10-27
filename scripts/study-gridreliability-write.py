#!/usr/bin/env python3
r"""study-gridreliability-write.py — the grid reliability study's summaries, written from its figures.

    python scripts/study-gridreliability-write.py
    python scripts/study-gridreliability-write.py --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-mobile-write.py` does it. The
study holds one figure a country and its earlier years, so **what there is to say is
arithmetic**: the latest count of outages a month, who measured it, the years before it, and
how far it stands from the next line.

Writes, per country, `outputs/maturity/gridreliability/{ISO3}.md` and
`maturity/gridreliability/evidence/{ISO3}/short.json`, in the shape `writer-brief.md` sets and
`lint-study.py` holds: one paragraph for the one aspect, every claim linked to its evidence
row's `url`, then ***Also on file*** from `systems.csv` and ***Not found***.

A fact a drafter read from a document is printed as the drafter wrote it, linked, after the
figure that set the stage. Run it after the ladder script, which writes the `stage.json` it
reads.

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

STUDY = "gridreliability"
SUB = "outages"
LINES = ((10.0, "ten"), (5.0, "five"), (2.0, "two"), (1.0, "one"))
SURVEY = "the World Bank's Enterprise Survey"


def link(url: str, words: str) -> str:
    return f"[{words}](<{url}>)"


def num(value: str) -> float:
    return float(value.split(":", 1)[1])


def times(n: float) -> str:
    return f"{n:g} outage" + ("" if n == 1 else "s")


def listed(parts: list[str]) -> str:
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def paragraph(name: str, country: str, rows: list[dict], best: dict, field: list[float]) -> str:
    """The one aspect's paragraph. `rows` are the country's `outages` facts, `best` the one that set
    the stage, `field` every staged country's figure."""
    figure, year, url = num(best["value"]), best["as_of"][:4], best["url"]
    out = [f"**{name}.**"]
    if best["source_slug"].startswith("ref:"):
        out.append(f"Firms in {country} reported {link(url, f'{times(figure)} in a typical month')} "
                   f"in {SURVEY} for {year}.")
    else:
        out.append(link(url, best["fact"].rstrip(".")) + f"; that is {times(figure)} a month.")
    series = sorted((r for r in rows if r["source_slug"].startswith("ref:")
                     and r["row_id"] != best["row_id"]), key=lambda r: r["as_of"])
    if series:
        steps = listed([f"{num(r['value']):g} in {r['as_of'][:4]}" for r in series])
        survey_url = series[-1]["url"]
        said = "Earlier surveys" if best["source_slug"].startswith("ref:") else "The World Bank's Enterprise Surveys"
        out.append(f"{said} {link(survey_url, 'put the count at ' + steps)}.")
        if best["source_slug"].startswith("ref:"):
            moved = figure - num(series[0]["value"])
            how = "has not changed" if abs(moved) < 0.05 else \
                f"{'rose' if moved > 0 else 'fell'} by {abs(moved):.1f} a month"
            out.append(f"Since {series[0]['as_of'][:4]} the count {how}.")
    elif best["source_slug"].startswith("ref:"):
        out.append("No earlier survey has been found, so no source found says whether outages are rising or falling.")
    if best["value"].startswith("survey:"):
        out.append("The survey asks firms how many power outages they had in a typical month and "
                   "averages their answers; it says nothing of how long each outage lasted, and it "
                   "counts the outages firms report, not how many people the grid reaches.")
    elif "SAIFI" not in best["fact"]:
        out.append("The figure is the utility's own count of blackouts, stated in public, and is "
                   "used in place of the survey because it is the utility's and is newer.")
    else:
        out.append("An interruption frequency counts how many times in a year the average "
                   "customer's supply was cut; divided by 12 it gives the outages in a month, the "
                   "figure this study's lines are drawn on.")
    cleared = [w for line, w in LINES if figure <= line]
    ahead = [(line, w) for line, w in LINES if figure > line]
    lines = "The study's lines are ten, five, two and one outage a month"
    if not cleared:
        out.append(f"{lines}; at more than ten, {country} is above all four, by {figure - 10:.1f}.")
    elif ahead:
        out.append(f"{lines}; {country} is within {cleared[-1]} a month and {figure - ahead[0][0]:.1f} "
                   f"above {ahead[0][1]}.")
    else:
        out.append(f"{lines}; at one or fewer, {country} is within all four.")
    fewer = sum(1 for x in field if x < figure)
    out.append(f"Of the {len(field)} countries with a figure for 2023 or later, {fewer} "
               f"{'has' if fewer == 1 else 'have'} fewer outages a month than {country}.")
    for r in rows:
        if not r["source_slug"].startswith("ref:") and r["row_id"] != best["row_id"]:
            out.append(link(r["url"], r["fact"].rstrip(".")) + ".")
    return " ".join(out)


def write(study: dict, iso: str, country: str, base: str, out_dir: str, dry: bool,
          field: list[float]) -> str:
    name = study["aspects"][0]["name"]
    label = study["sub_indicators"][0]["label"]
    folder = os.path.join(base, iso)
    try:
        with open(os.path.join(folder, "stage.json"), encoding="utf-8") as fh:
            cell = json.load(fh)["cells"][0]
    except OSError:
        raise study_lib.StudyError(f"{iso}: no stage.json; run the ladder script first")
    rows = [r for r in study_lib.read_csv(os.path.join(folder, "evidence.csv")) if r["aspect"] == "outages"]
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
        best = next(r for r in rows if r["row_id"] == cell["stage_sources"])
        figure, year = num(best["value"]), best["as_of"][:4]
        parts += [paragraph(name, country, rows, best, field), ""]
        by = "firms surveyed by the World Bank" if best["value"].startswith("survey:") else "the utility or regulator"
        short = f"In {year} the power went off {figure:g} times a month, as reported by {by}."
        ahead = [line for line, _ in LINES if figure > line]
        held = (f"No figure of {ahead[0]:g} or fewer outages a month has been found." if ahead
                else "Nothing further is asked of this indicator.")
        if best["value"].startswith("survey:"):
            held += " No regulator's or utility's interruption figure for 2023 or later has been found."
    else:
        old = sorted(rows, key=lambda r: r["as_of"])
        held = cell["gaps"]
        if old:
            held += f" The latest held is {times(num(old[-1]['value']))} a month, for {old[-1]['as_of'][:4]}."
            parts += [f"**{name}.** " + link(old[-1]["url"], old[-1]["fact"].rstrip(".")) + ". "
                      "It is older than 2023, so it sets no stage.", ""]
        short = "No count of power outages for 2023 or later has been found, so no stage is set."
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
    ap = argparse.ArgumentParser(description="Write the grid reliability study's summaries.")
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    try:
        study = study_lib.load(STUDY)
        base = os.path.join(study_lib.study_dir(STUDY), "evidence")
        names = study_lib.countries()
        field = []
        for iso in sorted(names):
            with open(os.path.join(base, iso, "stage.json"), encoding="utf-8") as fh:
                cell = json.load(fh)["cells"][0]
            if cell["stage"].isdigit():
                field.append(num(cell["outages"]))
        n = 0
        for iso in sorted(names):
            write(study, iso, names[iso]["name"], base, study_lib.out_dir(STUDY), a.dry, field)
            n += 1
    except study_lib.StudyError as e:
        print(f"study-gridreliability-write: {e}")
        return 2
    print(f"study-gridreliability-write: {n} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
