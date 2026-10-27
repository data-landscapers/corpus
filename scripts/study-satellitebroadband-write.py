#!/usr/bin/env python3
r"""study-satellitebroadband-write.py — the satellite broadband study's summaries, written from its facts.

    python scripts/study-satellitebroadband-write.py
    python scripts/study-satellitebroadband-write.py --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-exchangepoints-write.py` does
it, and for the same reason: the run's token ceiling left no room for 54 writers. **Nothing is
composed here that a fact does not state.** Each paragraph is the drafters' own fact sentences,
each linked whole to its evidence row's `url`: the rows that set the stage first, then the rest
newest first while the summary stays inside `ROOM` words. A drafter's note on how it dated a
fact is cut, and so is an opening that names the document rather than who said it.

The short summary is one sentence per stage, with the year of the fact that set it. Writes, per
country, `outputs/maturity/satellitebroadband/{ISO3}.md` and
`maturity/satellitebroadband/evidence/{ISO3}/short.json`, in the shape `lint-study.py` holds. Run it
after the ladder script, which writes the `stage.json` it reads.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maturity_words  # noqa: E402
import study_lib  # noqa: E402

STUDY = "satellitebroadband"
SUB = "satellite"
ROOM = 170
REACH_ROOM = 60
# A clause that is the drafter's note on its own dating, not the fact.
DATING = re.compile(r"as_of|article(?:'s)? (?:publication )?date|publication date|\bdate is\b|"
                    r"document date|date used|is used as|no (?:other )?date|the date is|revision date|published year|"
                    r"gives no (?:\w+ )?date|no (?:peak |launch )?date|capture year|undated|"
                    r"^(?:but |though |with )?no .*\b(?:given|stated|named|listed)$", re.I)
OPENER = re.compile(r"^(?:the )?(?:article|document|report|page|story|piece|text)"
                    r"(?: \w+)? (?:says|states|reports|notes|describes)(?: that)? ", re.I)
# What the stage rests on, in plain words, closing the first paragraph.
RESTS = {
    "5": "Together these place satellite broadband licensed, on sale and sold on two satellite "
         "networks, the first three of the study's questions, and the stage rests on that and "
         "on the subscriber count below.",
    "4": "Together these place satellite broadband licensed, on sale and sold on two satellite "
         "networks, which answers the first three of the study's four questions.",
    "3": "These place satellite broadband licensed and on sale, which answers the first two of "
         "the study's four questions. Services on a second satellite network are not stated.",
    "2": "These place a satellite broadband provider licensed, which answers the first of the "
         "study's four questions. Sale to households or businesses is not stated, or was suspended.",
    "1": "A dated statement that no satellite broadband provider is licensed, or that its sale "
         "or use is banned, sets the lowest stage, and nothing dated later names one licensed.",
}
LENGTH = "Prices and speeds are given where a source states them; they set no stage."
OPEN = ("Only a count the regulator publishes, from the past three years, answers this question; "
        "counts given by an operator or an analyst do not.")
SHORT = {
    "5": "Satellite broadband licensed and on sale by {y}, on two satellite networks, with subscribers counted by the regulator.",
    "4": "Satellite broadband licensed and on sale by {y}, on two satellite networks.",
    "3": "Satellite broadband licensed and on sale by {y}, on one satellite network.",
    "2": "A satellite broadband provider licensed by {y}, with no service on sale held.",
    "1": "A {y} source says satellite broadband is not licensed or is banned.",
}


def link(url: str, words: str) -> str:
    return f"[{words.replace('[', '(').replace(']', ')')}](<{url}>)"


def clean(fact: str) -> str:
    parts = [p.strip() for p in re.split(r";\s+|(?<!\bi\.e\.)(?<!\be\.g\.)(?<=[a-z0-9)]\.)\s+(?=[A-Z])", fact.strip()) if p.strip()]
    kept = [p for p in parts if not DATING.search(p.rstrip("."))] or parts[:1]
    text = "; ".join(p.rstrip(".;,") for p in kept)
    text = OPENER.sub("", text)
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


def write(study: dict, iso: str, country: str, base: str, out_dir: str, dry: bool) -> str:
    routes_name, access_name = (a["name"] for a in study["aspects"])
    label = study["sub_indicators"][0]["label"]
    folder = os.path.join(base, iso)
    try:
        with open(os.path.join(folder, "stage.json"), encoding="utf-8") as fh:
            cell = json.load(fh)["cells"][0]
    except OSError:
        raise study_lib.StudyError(f"{iso}: no stage.json; run the ladder script first")
    rows = study_lib.read_csv(os.path.join(folder, "evidence.csv")) \
        if os.path.exists(os.path.join(folder, "evidence.csv")) else []
    fixes = {f"{f['iso3']}-{f['n']}" for f in study_lib.read_csv(
        os.path.join(study_lib.study_dir(STUDY), "corrections.csv")) if f["action"] == "removed"}
    rows = [r for r in rows if r["row_id"] not in fixes]
    urls = {r["slug"]: r["url"] for r in study_lib.read_csv(os.path.join(folder, "readlist.csv"))}
    noted, seen = [], set()
    for s in study_lib.read_csv(os.path.join(folder, "systems.csv")) \
            if os.path.exists(os.path.join(folder, "systems.csv")) else []:
        url = urls.get(s["sources"], "")
        words = s["system"].strip()
        if s["class"] == "other" and url and words and words not in seen and len(noted) < 6:
            seen.add(words)
            noted.append(link(url, words))
    src = [i for i in cell["stage_sources"].split(";") if i]
    parts = [f"# {country}", "", f"## {label}", ""]
    if cell["stage"].isdigit():
        routes = [r for r in rows if r["aspect"] == "service"]
        access = [r for r in rows if r["aspect"] == "counted"]
        said = sentences(access, [i for i in src if i in {r["row_id"] for r in access}], REACH_ROOM)
        top = next(r for r in rows if r["row_id"] == src[0])
        if not said and cell["stage"] == "1":
            said = [f"With {link(top['url'], 'no provider licensed')}, there is nothing to count."]
        elif not said:
            said = [f"Nothing found gives a regulator's count of the subscribers to "
                    f"{link(top['url'], 'the service')}."]
        used = sum(len(s.split()) for s in said)
        body = sentences(routes, src, ROOM - used - len(RESTS[cell["stage"]].split()) - len(LENGTH.split()))
        parts += [f"**{routes_name}.** " + " ".join(body + [RESTS[cell["stage"]], LENGTH]), "",
                  f"**{access_name}.** " + " ".join(said + [OPEN]), ""]
        top = next(r for r in rows if r["row_id"] == src[0])
        short = SHORT[cell["stage"]].format(y=top["as_of"][:4])
    else:
        short = ("Nothing found says a satellite broadband provider is licensed, or that none "
                 "is, so no stage is set.")
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
    ap = argparse.ArgumentParser(description="Write the satellite broadband study's summaries.")
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    try:
        study = study_lib.load(STUDY)
        base = os.path.join(study_lib.study_dir(STUDY), "evidence")
        names = study_lib.countries()
        for iso in sorted(names):
            write(study, iso, names[iso]["name"], base, study_lib.out_dir(STUDY), a.dry)
    except study_lib.StudyError as e:
        print(f"study-satellitebroadband-write: {e}")
        return 2
    print(f"study-satellitebroadband-write: {len(names)} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
