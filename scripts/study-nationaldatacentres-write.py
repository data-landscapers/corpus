#!/usr/bin/env python3
r"""study-nationaldatacentres-write.py — the national data centres study's summaries, written from its facts.

    python scripts/study-nationaldatacentres-write.py
    python scripts/study-nationaldatacentres-write.py --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-datacentres-write.py`
does it, and for the same reason: the run's token ceiling left no room for 54 writers. **Nothing is
composed here that a fact does not state.** Each paragraph is the drafters' own fact sentences,
each linked whole to its evidence row's `url`: the rows that set the stage first, then the rest
newest first while the summary stays inside `ROOM` words. A drafter's note on how it dated a
fact is cut, and so is an opening that names the document rather than who said it.

The short summary is one sentence per stage, with the year of the fact that set it. Writes, per
country, `outputs/maturity/nationaldatacentres/{ISO3}.md` and
`maturity/nationaldatacentres/evidence/{ISO3}/short.json`, in the shape `lint-study.py` holds. The centre paragraph holds the nationally owned facilities only, as the ladder script reads
them; a foreign-owned one is `other` (study file §1) and is named in *Also on file*.
Run it after the ladder script, which writes the `stage.json` it reads.

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

STUDY = "nationaldatacentres"
SUB = "national"
ROOM = 175
OWN_ROOM = 45
STATE_ROOM = 55
# A clause that is the drafter's note on its own dating, not the fact.
DATING = re.compile(r"as_of|article(?:'s)? (?:publication )?date|publication date|\bdate is\b|"
                    r"document date|date used|is used as|no (?:other )?date|the date is|revision date|published year|"
                    r"gives no (?:\w+ )?date|no (?:peak |launch )?date|capture (?:year|date)|undated|"
                    r"this document names it|"
                    r"^(?:but |though |with )?no .*\b(?:given|stated|named|listed)$", re.I)
# The opening a carried fact takes (`study-datacentres-carry.py`), which names the dataset, not the source.
CARRIED = re.compile(r"^Data centres dataset:\s*")
OPENER = re.compile(r"^(?:the )?(?:article|document|report|page|story|piece|text|release|addendum|"
                    r"bidding document|request for bids|ToR)"
                    r"(?: \w+)?(?: \([^)]*\))? (?:says|states|reports|notes)(?: that)? ", re.I)
# What the stage rests on, in plain words, closing the first paragraph.
RESTS = {
    "5": "Together these place two nationally owned data centres for hire at Tier III or above in "
         "service, the first three of the study's questions.",
    "4": "Together these place two nationally owned data centres for hire at Tier III or above in "
         "service, which answers the first three of the study's four questions.",
    "3": "These place a nationally owned data centre for hire at Tier III or above in service. A "
         "second at Tier III is not stated.",
    "2": "These place a nationally owned data centre for hire in service. No source found states "
         "one at Tier III or above: built so that power and cooling can be maintained without "
         "shutting the data centre down, as the Uptime Institute defines it.",
    "1": "A dated statement that no data centre in the country rents space or computing to "
         "others sets the lowest stage, and nothing dated later names one.",
}
OWN = ("Owned in the country means by the state, a state enterprise or a company owned mostly in "
       "the country; a facility a foreign group controls is not counted.")
SHORT = {
    "5": "Two nationally owned data centres for hire at Tier III or above by {y}, and the state's own data hosted with a national provider.",
    "4": "Two nationally owned data centres for hire at Tier III or above by {y}; state hosting with them not known.",
    "3": "A nationally owned data centre for hire at Tier III or above by {y}; no second one held.",
    "2": "A nationally owned data centre for hire in service by {y}, none found at Tier III or above.",
    "1": "A {y} source says no data centre in the country rents space or computing to others.",
}


def link(url: str, words: str) -> str:
    return f"[{words.replace('[', '(').replace(']', ')')}](<{url}>)"


def clean(fact: str) -> str:
    parts = [p.strip() for p in re.split(r";\s+|(?<!\bi\.e\.)(?<!\be\.g\.)(?<=[a-z0-9)]\.)\s+(?=[A-Z])", fact.strip()) if p.strip()]
    kept = [p for p in parts if not DATING.search(p.rstrip("."))] or parts[:1]
    text = "; ".join(p.rstrip(".;,") for p in kept)
    text = CARRIED.sub("", OPENER.sub("", text))
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
    centre_name, owner_name, state_name = (a["name"] for a in study["aspects"])
    label = study["sub_indicators"][0]["label"]
    here = study_lib.study_dir(STUDY)
    folder = os.path.join(base, iso)
    try:
        with open(os.path.join(folder, "stage.json"), encoding="utf-8") as fh:
            cell = json.load(fh)["cells"][0]
    except OSError:
        raise study_lib.StudyError(f"{iso}: no stage.json; run the ladder script first")
    rows = study_lib.read_csv(os.path.join(folder, "evidence.csv")) \
        if os.path.exists(os.path.join(folder, "evidence.csv")) else []
    fixes = study_lib.read_csv(os.path.join(here, "corrections.csv"))
    rows, _ = ladder.correct(rows, [f for f in fixes if f["iso3"] == iso])
    systems = study_lib.read_csv(os.path.join(folder, "systems.csv")) \
        if os.path.exists(os.path.join(folder, "systems.csv")) else []
    table = {(r["iso3"], r["owner"]): r["national"]
             for r in study_lib.read_csv(os.path.join(here, "owners.csv"))}
    owned = ladder.owners_of(iso, systems, table)
    owned.update(ladder.fallback(iso, rows, owned, table, ladder.load_dataset()))
    said = {}
    for r in sorted(rows, key=lambda r: r["as_of"], reverse=True):
        if r["aspect"] == "owner":
            said.setdefault(r["system"], "yes" if r["value"] == "national" else "no")
    whose = lambda r: said.get(r["system"], owned.get(r["system"]))  # noqa: E731
    urls = {r["slug"]: r["url"] for r in study_lib.read_csv(os.path.join(folder, "readlist.csv"))}
    noted, seen = [], set()
    for r in rows:                         # a foreign-owned data centre for hire is `other` here
        if r["aspect"] == "centre" and r["value"] != "none" and whose(r) == "no" \
                and r["system"] not in seen and len(noted) < 6:
            seen.add(r["system"])
            noted.append(link(r["url"], r["system"].strip()))
    for s in systems:
        url = urls.get(s["sources"], "")
        words = s["system"].strip()
        if s["class"] == "other" and url and words and words not in seen and len(noted) < 6:
            seen.add(words)
            noted.append(link(url, words))
    src = [i for i in cell["stage_sources"].split(";") if i]
    parts = [f"# {country}", "", f"## {label}", ""]
    if cell["stage"].isdigit():
        top = next(r for r in rows if r["row_id"] == src[0])
        centre = [r for r in rows if r["aspect"] == "centre" and (whose(r) == "yes" or r["value"] == "none")]
        owner = [r for r in rows if r["aspect"] == "owner" and r["value"] == "national"]
        state = [r for r in rows if r["aspect"] == "state"]
        st = sentences(state, [i for i in src if i in {r["row_id"] for r in state}], STATE_ROOM)
        if not st:
            st = [f"Nothing found says the government hosts its own data beside "
                  f"{link(top['url'], 'the national data centres')}."]
        ow = sentences(owner, [], OWN_ROOM)
        if not ow:
            names, done = [], set()
            for r in centre:
                own = next((s["owner"] for s in systems if s["system"] == r["system"] and s["owner"]), "")
                if own and r["system"] not in done and len(names) < 3:
                    done.add(r["system"])
                    bare = re.sub(r"\(.*?\)", "", own).strip()
                    names.append(link(r["url"], r["system"].strip())
                                 + ("" if bare.lower() in r["system"].lower() else f" ({own})"))
            ow = ["Nationally owned: " + "; ".join(names) + "."] if names else \
                [f"No source found states who owns {link(top['url'], 'the data centre')}."]
        used = sum(len(s.split()) for s in st + ow) + len(OWN.split())
        body = sentences(centre, src, ROOM - used - len(RESTS[cell["stage"]].split()))
        parts += [f"**{centre_name}.** " + " ".join(body + [RESTS[cell["stage"]]]), "",
                  f"**{owner_name}.** " + " ".join(ow + [OWN]), "",
                  f"**{state_name}.** " + " ".join(st), ""]
        short = SHORT[cell["stage"]].format(y=top["as_of"][:4])
    elif cell["stage"] == "unplaced":
        short = ("Nothing found says a data centre for hire in the country is nationally owned, "
                 "so no stage is set.")
    else:
        short = ("Nothing found says a data centre in the country rents space or computing to "
                 "others, so no stage is set.")
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
    ap = argparse.ArgumentParser(description="Write the national data centres study's summaries.")
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    spec = importlib.util.spec_from_file_location(
        "ladder", os.path.join(os.path.dirname(os.path.abspath(__file__)), "study-ladder-nationaldatacentres.py"))
    ladder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ladder)
    try:
        study = study_lib.load(STUDY)
        base = os.path.join(study_lib.study_dir(STUDY), "evidence")
        names = study_lib.countries()
        for iso in sorted(names):
            write(study, iso, names[iso]["name"], base, study_lib.out_dir(STUDY), a.dry, ladder)
    except study_lib.StudyError as e:
        print(f"study-nationaldatacentres-write: {e}")
        return 2
    print(f"study-nationaldatacentres-write: {len(names)} countries"
          + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
