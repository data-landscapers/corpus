#!/usr/bin/env python3
r"""study-offsitebackup-write.py — the off-site backup study's summaries, written from its facts.

    python scripts/study-offsitebackup-write.py
    python scripts/study-offsitebackup-write.py --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-nationaldatacentres-write.py`
does it. **Nothing is composed here that a fact does not state**: each paragraph is the
drafters' own fact sentences, each linked whole to its evidence row's `url`, the rows that set
the stage first, then the rest newest first while the paragraph stays inside its room. The site
paragraph holds the sites `sites.csv` marks `far` and statements of absence; a site nearer than
200 km or in no named place is `other` (study file §1) and is named in *Also on file*.

Writes, per country, `outputs/maturity/offsitebackup/{ISO3}.md` and
`maturity/offsitebackup/evidence/{ISO3}/short.json`. Run it after the ladder script.

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

STUDY = "offsitebackup"
SUB = "backup"
SITE_ROOM, PLAN_ROOM, TIER_ROOM = 120, 50, 40
DATING = re.compile(r"as_of|article(?:'s)? (?:publication )?date|publication date|\bdate is\b|"
                    r"document date|date used|is used as|no (?:other )?date|the date is|revision date|published year|"
                    r"gives no (?:\w+ )?date|no (?:launch )?date|undated|dated by|date .*not stated|period is used|"
                    r"^(?:but |though |with )?no .*\b(?:given|stated|named|listed)$", re.I)
OPENER = re.compile(r"^(?:the )?(?:article|document|report|page|story|piece|text|release|"
                    r"bidding document|request for bids|ToR)"
                    r"(?: \w+)?(?: \([^)]*\))? (?:says|states|reports|notes)(?: that)? ", re.I)
RESTS = {
    "5": "These place a backup site 200 km or more from the main one in service for the government's shared systems.",
    "4": "These place a backup site 200 km or more from the main one in service for the government's shared systems.",
    "3": "These place a backup site 200 km or more from the main one in service for the government's shared systems.",
    "2": "These place one public body's backup site 200 km or more from its main one in service. "
         "No source found says such a site serves the government's shared systems.",
    "1": "A dated statement that government systems have no off-site backup sets the lowest stage, "
         "and nothing dated later names one.",
}
SHORT = {
    "5": "A government backup site 200 km away by {y}, with recovery planned or tested and both sites at Tier III.",
    "4": "A government backup site 200 km away by {y}, with a recovery plan or test on record.",
    "3": "A backup site 200 km away serves the government's shared systems by {y}; no recovery plan or test held.",
    "2": "One public body keeps a backup site 200 km away by {y}; none found for the government's shared systems.",
    "1": "A {y} source says government systems have no off-site backup or disaster-recovery site.",
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


def write(study: dict, iso: str, country: str, base: str, out_dir: str, dry: bool, ladder, far: dict) -> str:
    site_name, plan_name, tier_name = (a["name"] for a in study["aspects"])
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
    why = {"near": "less than 200 km from the main site", "unnamed": "place not named"}
    for r in rows:
        k = far.get(r["row_id"])
        if r["aspect"] == "site" and k in why and r["system"] not in seen and len(noted) < 6:
            seen.add(r["system"])
            noted.append(link(r["url"], r["system"].strip()) + f" ({why[k]})")
    for s in systems:
        url, words = urls.get(s["sources"], ""), s["system"].strip()
        if url and words and words not in seen and len(noted) < 6 and s["class"] in ("other", "backupsite"):
            seen.add(words)
            noted.append(link(url, words))
    src = [i for i in cell["stage_sources"].split(";") if i]
    parts = [f"# {country}", "", f"## {label}", ""]
    if cell["stage"].isdigit():
        top = next(r for r in rows if r["row_id"] == src[0])
        site = [r for r in rows if r["aspect"] == "site" and (far.get(r["row_id"]) == "far" or r["value"] == "none")]
        plan = [r for r in rows if r["aspect"] == "plan"]
        tier = [r for r in rows if r["aspect"] == "tier"]
        body = sentences(site, src, SITE_ROOM)
        pl = sentences(plan, [i for i in src if i in {r["row_id"] for r in plan}], PLAN_ROOM) or \
            [f"No source found from the past three years states a recovery plan or a failover test for "
             f"{link(top['url'], 'the backup site')}."]
        ti = sentences(tier, [i for i in src if i in {r["row_id"] for r in tier}], TIER_ROOM) or \
            [f"No source found says both the main site and {link(top['url'], 'the backup site')} are Tier III or above."]
        parts += [f"**{site_name}.** " + " ".join(body + [RESTS[cell["stage"]]]), "",
                  f"**{plan_name}.** " + " ".join(pl), "",
                  f"**{tier_name}.** " + " ".join(ti), ""]
        short = SHORT[cell["stage"]].format(y=top["as_of"][:4])
    elif cell["stage"] == "unplaced":
        short = "No backup site 200 km or more from the main one has been found, so no stage is set."
    else:
        short = "Nothing found names a backup site for government systems, so no stage is set."
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
    ap = argparse.ArgumentParser(description="Write the off-site backup study's summaries.")
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    spec = importlib.util.spec_from_file_location(
        "ladder", os.path.join(os.path.dirname(os.path.abspath(__file__)), "study-ladder-offsitebackup.py"))
    ladder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ladder)
    try:
        study = study_lib.load(STUDY)
        here = study_lib.study_dir(STUDY)
        far = {r["row_id"]: r["distance"] for r in study_lib.read_csv(os.path.join(here, "sites.csv"))}
        base = os.path.join(here, "evidence")
        names = study_lib.countries()
        for iso in sorted(names):
            write(study, iso, names[iso]["name"], base, study_lib.out_dir(STUDY), a.dry, ladder, far)
    except study_lib.StudyError as e:
        print(f"study-offsitebackup-write: {e}")
        return 2
    print(f"study-offsitebackup-write: {len(names)} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
