#!/usr/bin/env python3
r"""study-first-write.py — a first-pass study's summaries, written from its facts.

    python scripts/study-first-write.py dataexchange
    python scripts/study-first-write.py dataexchange --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-opendatause-write.py` does it,
for the studies whose ladder `study_first_ladder.py` counts. **Nothing is composed here that a
fact does not state**: each paragraph is the drafters' own fact sentences on that aspect, each
linked whole to its evidence row's `url`, the rows that set the stage first, then the rest newest
first while the paragraph stays inside its room. An aspect with nothing held says so, linked to
the fact that set the stage. The short summary is one sentence per stage from `SHORT`.

Writes, per country, `outputs/maturity/{id}/{ISO3}.md` and
`maturity/{id}/evidence/{ISO3}/short.json`. Run it after the ladder script.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402
import study_first_ladder as ladder  # noqa: E402

SINCE = "2023-10"   # three years back from the as-at, as the ladder reads it
ROOM = (100, 60, 60)
# Per study: the short sentence for stages 1 to 5 ({y} the year of the fact that set it), what an
# empty aspect says for the 2nd and 3rd aspects, and the thing named in an unstaged cell.
SHORT = {
    "dataexchange": (
        ["A {y} source says government systems have no data exchange platform.",
         "A government data exchange platform was under way in {y}; none in service is on record.",
         "A government data exchange platform was in service in {y}; how many systems it connects is not known.",
         "Ten or more bodies or systems were connected to the government exchange platform in {y}; its use is not reported.",
         "Use of the government data exchange platform was reported in {y}."],
        ["No source held since October 2023 counts ten or more institutions or systems connected.",
         "No source held since October 2023 gives a figure for the exchanges through the platform."],
        "a government data exchange platform"),
    "idverification": (
        ["A {y} source says no other system checks people against the national ID.",
         "Another system's use of the national ID was under way in {y}; none in service is on record.",
         "A service checked people against the national ID in {y}; use in a second sector is not known.",
         "Services in two or more sectors checked people against the national ID in {y}; volumes are not known.",
         "Use of the national ID by other services was reported with figures in {y}."],
        ["No source held since October 2023 shows services in two or more sectors checking against the ID.",
         "No source held since October 2023 gives a figure for verifications or counts the services relying on the ID."],
        "another system checking people against the national ID"),
    "healthexchange": (
        ["A {y} source says the country's health systems do not exchange data.",
         "An exchange between health systems was under way in {y}; none in service is on record.",
         "Two health systems exchanged data in {y}; exchange across the health system is not known.",
         "Health systems exchanged data across the system in {y}; patient matching by a national identifier is not known.",
         "Patient records were linked by a national identifier across health systems in {y}."],
        ["No source held since October 2023 says three or more health systems exchange data, or a national exchange is in service.",
         "No source held since October 2023 says patient records are linked through the national ID or a national health identifier."],
        "health systems exchanging data"),
    "educationexchange": (
        ["A {y} source says the country's education systems exchange no data.",
         "A link between education systems was under way in {y}; none in service is on record.",
         "Two education systems exchanged data in {y}; a shared learner identifier is not known.",
         "One learner identifier was used across education systems in {y}; links beyond education are not known.",
         "Learner records were linked to the national ID or another sector in {y}."],
        ["No source held since October 2023 says one learner identifier is used across education systems.",
         "No source held since October 2023 says learner records are linked to the national ID or another sector."],
        "education systems exchanging data"),
    "socialexchange": (
        ["A {y} source says social protection programmes keep separate lists with no exchange.",
         "A link between social protection systems was under way in {y}; none in service is on record.",
         "A social protection system exchanged data in {y}; a registry shared by programmes is not known.",
         "Two or more programmes shared one social registry in {y}; links to another sector are not known.",
         "The social registry was linked to the national ID and another sector in {y}."],
        ["No source held since October 2023 says two or more programmes share one registry.",
         "No source held since October 2023 says the registry is linked to the national ID and to another sector."],
        "social protection systems exchanging data"),
    "idrobustness": (
        ["A {y} source says there is no national ID system with a unique number.",
         "A national ID system was under way in {y}; none in service is on record.",
         "The national ID system was issuing unique numbers in {y}; biometric checks are not known.",
         "The national ID system checked people by biometrics in {y}; no certification or audit is known.",
         "The national ID system's security was certified or audited in {y}."],
        ["No source held since October 2023 says the system checks people by biometrics.",
         "No source held since October 2023 reports a certification, audit or assurance level for the system."],
        "a national ID system"),
    "idcoverage": (
        ["Fewer than a third of the population held a national ID in {y}.",
         "A third of the population or more held a national ID in {y}.",
         "Two-thirds of the population or more held a national ID in {y}.",
         "Practically everyone held a national ID in {y}; birth and death registration at the target is not known.",
         "Everyone held a national ID and births and deaths were registered at the target in {y}."],
        ["No source held since October 2023 counts 99.9% of the population or more holding a national ID.",
         "No source held since October 2023 puts birth registration at all births and deaths at 80% or more."],
        "a count of people holding a national ID"),
    "idmaintenance": (
        ["A {y} source says a foreign supplier runs the national ID system.",
         "A move to national operation of the ID system was under way in {y}.",
         "The national authority ran the ID system day to day in {y}; who maintains it is not known.",
         "National staff maintained the ID system in {y}; ownership of its code is not known.",
         "The ID system ran in {y} on code the state owns."],
        ["No source held since October 2023 says national staff maintain the system or the foreign contract has ended.",
         "No source held since October 2023 says the system runs on code the state owns."],
        "who operates the national ID system"),
    "authentication": (
        ["A {y} source says no digital authentication service exists.",
         "An authentication or e-signature service was under way in {y}; none in service is on record.",
         "An authentication service was in use in {y}; use across services is not known.",
         "Authentication was used across services in {y}; remote proof of identity by a digital ID is not known.",
         "People could prove who they are online with a digital ID in {y}."],
        ["No source held since October 2023 says authentication is used across services or channels.",
         "No source held since October 2023 says a mobile ID, ID wallet or signed credential is in service."],
        "a digital authentication service"),
    "idfrombirth": (
        ["A {y} source says a birth creates no identity record.",
         "A unique number at birth was provided for or piloted in {y}; none given in service is on record.",
         "Children were given a unique ID number at birth registration in {y}, at least in part of the country.",
         "Every registered birth was given a unique ID number in {y}; complete registration is not known.",
         "All births were registered with a unique ID number in {y}."],
        ["No source held since October 2023 says every registered birth across the country receives the number.",
         "No source held since October 2023 puts birth registration at all births and deaths at 80% or more."],
        "a unique number given at birth"),
    "birthidlink": (
        ["A {y} source says the civil register and the ID system exchange no records.",
         "A link between the civil register and the ID system was under way in {y}.",
         "The civil register and the ID system were linked one way or for one event in {y}.",
         "Births and deaths passed between the civil register and the ID system in {y}; volumes are not known.",
         "Exchange between the civil register and the ID system was reported with figures in {y}."],
        ["No source held since October 2023 says births enrol people in the ID system and deaths retire their numbers.",
         "No source held since October 2023 gives a figure for records exchanged between the two."],
        "a link between the civil register and the ID system"),
    "idregisters": (
        ["A {y} source says public registers do not use the national ID number.",
         "A public register's use of the national ID number was under way in {y}.",
         "A public register used the national ID number in {y}; use by three main registers is not known.",
         "Three or more main public registers used the national ID number in {y}; no matching figures are known.",
         "Matching of public registers against the national ID was reported with figures in {y}."],
        ["No source held since October 2023 shows three or more main public registers using the national ID number.",
         "No source held since October 2023 gives a figure from checking a register against the ID."],
        "a public register using the national ID number"),
}
DATING = re.compile(r"as_of|article(?:'s)? (?:publication )?date|publication date|\bdate is\b|"
                    r"document date|date used|is used as|no (?:other )?date|the date is|revision date|published year|"
                    r"gives no (?:\w+ )?date|no (?:launch )?date|undated|dated by|date .*not stated|period is used|"
                    r"^(?:but |though |with )?no .*\b(?:given|stated|named|listed)$", re.I)
OPENER = re.compile(r"^(?:the )?(?:article|document|report|page|story|piece|text|release|table|brief|assessment)"
                    r"(?: \w+)?(?: \([^)]*\))? (?:says|states|reports|notes)(?: that)? ", re.I)
ASIDE = re.compile(r"\s*\((?=[^)]*\b(?:date|dated|as_of|inferred|publication|published)\b)[^)]*\)", re.I)


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
        if (r["as_of"] + "-12")[:7] < SINCE:   # a year stands for its last month, as the ladder reads it
            s += f" ({r['as_of'][:4]}, before the three-year window)"
        out.append(link(r["url"], s) + ".")
        n += len(s.split())
    return out


def write(study: dict, iso: str, country: str, dry: bool) -> str:
    sid = study["id"]
    shorts, empties, thing = SHORT[sid]
    sub = study["sub_indicators"][0]
    here = study_lib.study_dir(sid)
    folder = os.path.join(here, "evidence", iso)
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
        if url and words and words.lower() not in seen and len(noted) < 6 and s["class"] != sub["class"]:
            seen.add(words.lower())
            noted.append(link(url, words))
    src = [i for i in cell["stage_sources"].split(";") if i]
    parts = [f"# {country}", "", f"## {sub['label']}", ""]
    if cell["stage"].isdigit():
        top = next(r for r in rows if r["row_id"] == src[0])
        used = False
        for k, a in enumerate(study["aspects"]):
            mine = [r for r in rows if r["aspect"] == a["key"]]
            ids = {r["row_id"] for r in mine}
            body = sentences(mine, [i for i in src if i in ids], ROOM[k])
            if body and src[0] in ids:
                used = True
            if not body:
                lead = empties[k - 1] if k else f"No source held says {thing} is under way or in service."
                near = link(top["url"], clean(top["fact"])) if not used else link(top["url"], "the one given above")
                body = [f"{lead} The nearest held fact: {near}."]
                used = True
            if k == 0 and int(cell["stage"]) >= 4 and not any(r["value"] == ladder.firsts(study)[0] for r in mine):
                body.append("A later answer places the country above that step.")   # method §3.3
            parts += [f"**{a['name']}.** " + " ".join(body), ""]
        words = len(re.sub(r"\(<[^>]*>\)", "", " ".join(parts[4:])).split())
        if words < 120:   # few facts held: say so in the first paragraph, as the statistics law study did
            n = len(rows)
            parts[4] += (" It is the only fact" if n == 1 else f" {n} facts are") + " held on the subject"                 + ": no news story or official notice read for this study says more about it, the documents the earlier cell cited included, and the systems themselves were not examined."
            if len(re.sub(r"\(<[^>]*>\)", "", " ".join(parts[4:])).split()) < 120:
                parts[4] += (" This is a first pass, which read at most fifteen stories a country; the nightly"
                             " deep dive reads further and may move the stage either way.")
        short = shorts[int(cell["stage"]) - 1].format(y=top["as_of"][:4])
    elif cell["stage"] == "unplaced":
        short = f"Nothing held since 2023 names {thing}, so no stage is set."
    else:
        short = f"Nothing held names {thing} or says there is none, so no stage is set."
    parts += ["***Noted, not assessed***. " + ("; ".join(noted) + "." if noted else "None held."), "",
              "***Not held***. " + (cell["gaps"] or "Nothing further is asked of this indicator."), ""]
    if not dry:
        out = study_lib.out_dir(sid)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, iso + ".md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(parts))
        with open(os.path.join(folder, "short.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({sub["key"]: short}, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    return cell["stage"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write a first-pass study's summaries.")
    ap.add_argument("study", choices=sorted(SHORT))
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    try:
        study = study_lib.load(a.study)
        names = study_lib.countries()
        for iso in sorted(names):
            write(study, iso, names[iso]["name"], a.dry)
    except study_lib.StudyError as e:
        print(f"study-first-write: {e}")
        return 2
    print(f"study-first-write: {a.study}, {len(names)} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
