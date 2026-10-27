#!/usr/bin/env python3
r"""study-affordability-write.py — the mobile affordability study's summaries, written from its figures.

    python scripts/study-affordability-write.py
    python scripts/study-affordability-write.py --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-internet-write.py` does it.
The study holds one figure a country and the figures before it, so **what there is to say is
arithmetic**: the newest cost of 5 GB of mobile data for a month as a share of average monthly
income, where it comes from, the years before it, and how far it stands from the next line.

Writes, per country, `outputs/maturity/mobileaffordability/{ISO3}.md` and
`maturity/mobileaffordability/evidence/{ISO3}/short.json`, in the shape `writer-brief.md` sets
and `lint-study.py` holds: one paragraph for the one aspect, every claim linked to its
evidence row's `url`, then ***Also on file*** from `systems.csv` and ***Not found***.

**A stated price is printed as the drafter wrote it, then as the share `study_afford.share()`
makes of it**, with the income year named. The World Bank's series is data in
`reference/denominators.csv`, not a held record, so it is named and not linked. A price that
cannot be set against income is printed without one. Other figures read from stories follow,
newest first, while the paragraph stays inside `ROOM` words. Run it after the ladder script,
which writes the `stage.json` it reads.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_afford  # noqa: E402
import maturity_words  # noqa: E402
import study_lib  # noqa: E402

STUDY = "mobileaffordability"
SUB = "price"
LINES = (10.0, 5.0, 2.0, 1.0)
ROOM = 215


def link(url: str, words: str) -> str:
    return f"[{words}](<{url}>)"


def points(n: float) -> str:
    n = round(abs(n), 2)
    return f"{n:g} point" + ("" if n == 1 else "s")


def listed(parts: list[str]) -> str:
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def worked(iso: str, r: dict) -> str:
    """The sentence that turns a stated price into a share, or says why it gives none."""
    if r["value"].startswith("share:"):
        return ""
    figure = study_afford.share(iso, r["value"])
    got = study_afford.income(iso, r["value"].split(":")[1])
    if figure is None or not got:
        return "No income figure has been found in that currency, so it is not set against income."
    return (f"At that price 5 GB for a month comes to {figure:g} per cent of average monthly income, on "
            f"the World Bank's figure for income per person in {got[1]}.")


def paragraph(name: str, iso: str, country: str, rows: list[dict], best: dict) -> str:
    """The one aspect's paragraph. `rows` are the country's `cost` facts, `best` the one that set the stage."""
    held = sorted((r for r in rows if r["source_slug"].startswith("ref:")), key=lambda r: r["as_of"])
    figure, year, url = study_afford.share(iso, best["value"]), best["as_of"][:4], best["url"]
    own = best["source_slug"].startswith("ref:")
    out = [f"**{name}.**"]
    if own:
        out.append(f"In {year}, the cheapest 30-day plan of at least 5 GB from the largest operator in "
                   f"{country} cost {link(url, f'{figure:g} per cent of average monthly income')}, on the "
                   f"International Telecommunication Union's price figures.")
    else:
        out.append(link(url, best["fact"].rstrip(".")) + ".")
        if worked(iso, best):
            out.append(worked(iso, best))
        out.append("It is the newest figure held, and sets the stage.")
    recent = [r for r in held if r["as_of"] < best["as_of"] or not own]
    series = "The same figures" if own else "The International Telecommunication Union's price figures"
    if recent:
        steps = listed([f"{float(r['value'][6:]):g} per cent in {r['as_of'][:4]}" for r in recent])
        out.append(f"{series} {link(recent[-1]['url'], 'put the cost at ' + steps)}.")
        if own:
            moved = figure - float(recent[0]["value"][6:])
            how = "has not moved" if abs(moved) < 0.005 else \
                f"{'rose' if moved > 0 else 'fell'} by {points(moved)}"
            out.append(f"Since {recent[0]['as_of'][:4]} the cost {how}.")
    elif own:
        out.append("No earlier year has been found, so no source found says whether the cost is rising or falling.")
    under = [line for line in LINES if figure <= line]
    over = [line for line in LINES if figure > line]
    if not under:
        out.append(f"A month of data costs more than a tenth of a month's income, and is "
                   f"{points(figure - 10)} above 10 per cent.")
    elif over:
        out.append(f"The cost is within {under[-1]:g} per cent and {points(figure - over[0])} above "
                   f"{over[0]:g} per cent" + (", the international target." if over[0] == 2 else "."))
    else:
        out.append("At 1 per cent or less, the cost is half the international target of 2 per cent.")
    out.append("Average monthly income is gross national income per person divided by 12, so the "
               "figure says nothing of what the poorest pay against what they earn.")
    out.append("The stage rests on that one figure, the newest held for 2024 or later, whoever published it.")
    said = {(f"{figure:g}", year)}
    read = sorted((r for r in rows if not r["source_slug"].startswith("ref:") and r["row_id"] != best["row_id"]),
                  key=lambda r: (r["as_of"], r["row_id"]), reverse=True)
    for r in read:
        f = study_afford.share(iso, r["value"])
        key = (f"{f:g}" if f is not None else r["value"], r["as_of"][:4])
        tail = worked(iso, r)
        if key in said or len(" ".join(out).split()) + len((r["fact"] + " " + tail).split()) > ROOM:
            continue
        said.add(key)
        out.append(link(r["url"], r["fact"].rstrip(".")) + "." + (" " + tail if tail else ""))
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
    rows = [r for r in study_lib.read_csv(os.path.join(folder, "evidence.csv")) if r["aspect"] == "cost"]
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
        figure, year = study_afford.share(iso, best["value"]), best["as_of"][:4]
        parts += [paragraph(name, iso, country, rows, best), ""]
        short = (f"In {year}, 5 GB of mobile data for a month cost {figure:g} per cent of average monthly income, "
                 + ("on international price figures." if best["source_slug"].startswith("ref:") else
                    "on a stated share." if best["value"].startswith("share:") else "on a stated price."))
        over = [line for line in LINES if figure > line]
        held = (f"No figure of {over[0]:g} per cent or less has been found." if over
                else "Nothing further is asked of this indicator.")
    else:
        old = sorted((r for r in rows if study_afford.share(iso, r["value"]) is not None),
                     key=lambda r: r["as_of"])
        held = cell["gaps"]
        if old:
            held += (f" The latest held is {study_afford.share(iso, old[-1]['value']):g} per cent, "
                     f"for {old[-1]['as_of'][:4]}.")
        short = ("No figure for what a month of mobile data costs against income has been found for 2024 or "
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
    ap = argparse.ArgumentParser(description="Write the mobile affordability study's summaries.")
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
        print(f"study-affordability-write: {e}")
        return 2
    print(f"study-affordability-write: {n} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
