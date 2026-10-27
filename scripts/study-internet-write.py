#!/usr/bin/env python3
r"""study-internet-write.py — the internet usage study's summaries, written from its figures.

    python scripts/study-internet-write.py
    python scripts/study-internet-write.py --dry

`maturity/documentation/maturity-study-method.md` §8. The study holds one figure a country
and its earlier years, so **what there is to say is arithmetic**: the latest share, what
kind of figure it is, the years before it, and how far it stands from the next line. A
script says it the same way for 54 countries, where 54 writers would each read two style
guides to restate a number.

Writes, per country, `outputs/maturity/internetusage/{ISO3}.md` and
`maturity/internetusage/evidence/{ISO3}/short.json`, in the shape `writer-brief.md` sets
and `lint-study.py` holds: one paragraph for the one aspect, every claim linked to its
evidence row's `url`, then ***Also on file*** from `systems.csv` and ***Not found***.

A fact a drafter read from a story is printed as the drafter wrote it, linked, after the
series: newest first, each figure once, while the paragraph stays inside `ROOM` words. Run it after the ladder script, which writes the `stage.json` it reads.

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

STUDY = "internetusage"
SUB = "use"
LINES = ((25.0, "a quarter"), (50.0, "half"), (80.0, "four in five"), (95.0, "nearly everyone"))
ROOM = 225
BASIS = {"survey": "a survey figure the country reported to the International Telecommunication Union",
         "estimate": "an estimate by the International Telecommunication Union"}


def link(url: str, words: str) -> str:
    return f"[{words}](<{url}>)"


def num(value: str) -> float:
    return float(value.split(":", 1)[1])


def points(n: float) -> str:
    n = round(abs(n), 1)
    return f"{n:g} point" + ("" if n == 1 else "s")


def listed(parts: list[str]) -> str:
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def paragraph(name: str, country: str, rows: list[dict], best: dict) -> str:
    """The one aspect's paragraph. `rows` are the country's `users` facts, `best` the one that set the stage."""
    held = sorted((r for r in rows if r["source_slug"].startswith("ref:")), key=lambda r: r["as_of"])
    figure, year, url = num(best["value"]), best["as_of"][:4], best["url"]
    kind = best["value"].split(":")[0]
    own = best["source_slug"].startswith("ref:")
    out = [f"**{name}.**"]
    if own:
        out.append(f"In {year}, {link(url, f'{figure:g} per cent of the population')} of "
                   f"{country} used the internet, {BASIS[kind]}.")
    else:
        out.append(link(url, best["fact"].rstrip(".")) + ".")
    out.append(f"That leaves {100 - figure:.1f} per cent offline.")
    recent = [r for r in held if "2021" <= r["as_of"] and (r["as_of"] < best["as_of"] or not own)]
    series = "The same series" if own else "The International Telecommunication Union's series"
    if recent:
        steps = listed([f"{num(r['value']):g} per cent in {r['as_of'][:4]}" for r in recent])
        out.append(f"{series} {link(recent[-1]['url'], 'put the share at ' + steps)}.")
        if own:
            moved = figure - num(recent[0]["value"])
            how = "has not moved" if abs(moved) < 0.05 else                 f"{'rose' if moved > 0 else 'fell'} by {points(moved)}"
            out.append(f"Since {recent[0]['as_of'][:4]} the share {how}.")
    else:
        out.append("The series gives no figure for 2021, 2022 or 2023, so no source found says "
                   "whether the share is rising or falling.")
    surveys = [r for r in recent if r["value"].startswith("survey:")]
    if kind == "estimate":
        if surveys:
            was = f"{num(surveys[-1]['value']):g} per cent, for {surveys[-1]['as_of'][:4]}"
            out.append(f"The last survey figure in the series is {link(surveys[-1]['url'], was)}; "
                       f"every later year is an estimate.")
        else:
            out.append("Every figure since 2021 is an estimate, not a survey result.")
    cleared = [w for line, w in LINES if figure >= line]
    ahead = [(line, w) for line, w in LINES if figure < line]
    if not cleared:
        out.append(f"Fewer than a quarter of people use the internet, and the share is "
                   f"{points(25 - figure)} short of a quarter.")
    elif ahead:
        out.append(f"The share is past {cleared[-1]} and {points(ahead[0][0] - figure)} short of "
                   f"{ahead[0][0]:g} per cent, which is {ahead[0][1]}.")
    else:
        out.append("At 95 per cent or more, nearly everyone uses the internet.")
    out.append("The figure counts a person once, whatever the number of subscriptions they hold, "
               "and counts anyone who used the internet in the last three months, from any place "
               "and on any device.")
    # What the stories add, newest first, each figure once, as far as the long summary's cap allows.
    # A story that repeats the series' estimate adds nothing; a survey report behind its figure does.
    said = {(f"{num(r['value']):g}", r["as_of"][:4]) for r in held if r["value"].startswith("estimate:")}
    if not own:
        said.add((f"{num(best['value']):g}", best["as_of"][:4]))
    read = sorted((r for r in rows if not r["source_slug"].startswith("ref:") and r["row_id"] != best["row_id"]),
                  key=lambda r: (r["as_of"], r["row_id"]), reverse=True)
    for r in read:
        key = (f"{num(r['value']):g}", r["as_of"][:4])
        more = link(r["url"], r["fact"].rstrip(".")) + "."
        if key in said or len(" ".join(out + [r["fact"]]).split()) > ROOM:
            continue
        said.add(key)
        out.append(more)
    return " ".join(out)


def write(study: dict, iso: str, country: str, base: str, out_dir: str, dry: bool) -> str:
    name = study["aspects"][0]["name"]
    label = study["sub_indicators"][0]["label"]
    folder = os.path.join(base, iso)
    try:
        with open(os.path.join(folder, "stage.json"), encoding="utf-8") as fh:
            cell = json.load(fh)["cells"][0]
    except OSError:
        raise study_lib.StudyError(f"{iso}: no stage.json; run the ladder script first")
    rows = [r for r in study_lib.read_csv(os.path.join(folder, "evidence.csv")) if r["aspect"] == "users"]
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
        figure, year, kind = num(best["value"]), best["as_of"][:4], best["value"].split(":")[0]
        parts += [paragraph(name, country, rows, best), ""]
        short = (f"In {year}, {figure:g} per cent of the population used the internet, "
                 + ("by an international estimate." if kind == "estimate" else
                    "by a national survey." if best["source_slug"].startswith("ref:") else
                    "by the country's own figure."))
        ahead = [line for line, _ in LINES if figure < line]
        held = (f"No figure of {ahead[0]:g} per cent or more has been found." if ahead
                else "Nothing further is asked of this indicator.")
        if kind == "estimate":
            held += " No national survey or census figure for 2024 or later has been found."
    else:
        old = sorted(rows, key=lambda r: r["as_of"])
        held = cell["gaps"]
        if old:
            held += f" The latest held is {num(old[-1]['value']):g} per cent, for {old[-1]['as_of'][:4]}."
        short = ("No figure for the share of the population who use the internet has been found for 2024 or "
                 "later, so no stage is set.")
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
    ap = argparse.ArgumentParser(description="Write the internet usage study's summaries.")
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
        print(f"study-internet-write: {e}")
        return 2
    print(f"study-internet-write: {n} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
