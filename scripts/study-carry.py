#!/usr/bin/env python3
r"""study-carry.py — the facts an earlier study holds, carried into this one's reading.

    python scripts/study-carry.py dataprotectionauthority
    python scripts/study-carry.py dataprotectionauthority --dry

`maturity/documentation/maturity-study-method.md` §4: **start from what is already paid
for** *(Bill, 2026-10-11)*. A study names the studies it carries from in `carry_studies`,
and in `carry_map` says which of their facts answer its own questions:

    "carry_map": {"dataprotectionlaw": {"sub_indicator": "body", "class": "authority",
                  "aspects": {"authority": {"to": "standing"},
                              "application": {"to": "rulings", "values": {"applied": "ruled"}}}}}

A value keeps its spelling unless `values` renames it, and a value this study's aspect does
not list is not carried: it answers none of its questions.

**No document is opened.** For every document the earlier study drew a mapped fact from,
this writes `maturity/{id}/evidence/{ISO3}/facts/{n}.json`, in the shape a drafter writes,
with the fact's own text, date and source. `study-profile.py --merge` then folds carried
and drafted files alike, so a carried fact is filed under a listed source like any other. A
source this study's terms did not list is appended to `readlist.csv` as `why = carried`,
numbered after the last and in no call. The earlier study's systems come too, under their
own class where this study has it and as `other` where it does not.

Run it after `study-select.py` and before the drafters. A facts file already there is left
alone: a drafter's reading is never overwritten by a carry.

Exit: 0 written, 2 a study cannot be read.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

FACT_KEYS = ("fact", "as_of", "date_precision", "system")


def carried(study: dict, other: str, rule: dict, rows: list[dict]) -> dict[str, list[dict]]:
    """`{slug: facts}`: the earlier study's evidence rows that answer this study's questions."""
    values = {a["key"]: set(a.get("values", ())) for a in study["aspects"]}
    out: dict[str, list[dict]] = {}
    for r in rows:
        to = rule["aspects"].get(r["aspect"])
        if not to:
            continue
        value = to.get("values", {}).get(r["value"], r["value"])
        if value not in values.get(to["to"], ()):
            continue
        out.setdefault(r["source_slug"], []).append(
            {"sub_indicator": rule["sub_indicator"], "aspect": to["to"], "value": value,
             "class": rule["class"], **{k: r[k] for k in FACT_KEYS}})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Carry an earlier study's facts into this one.")
    ap.add_argument("study")
    ap.add_argument("--dry", action="store_true", help="print the counts, write nothing")
    a = ap.parse_args(argv)
    try:
        study = study_lib.load(a.study)
        for other in study.get("carry_studies", ()):
            study_lib.load(other)
    except study_lib.StudyError as e:
        print(f"study-carry: {e}")
        return 2

    base = os.path.join(study_lib.study_dir(a.study), "evidence")
    classes, docs, facts, appended = set(study["classes"]), 0, 0, 0
    rules = {o: study.get("carry_map", {}).get(o) for o in study.get("carry_studies", ())}
    for other in [o for o, r in rules.items() if not r]:
        print(f"study-carry: `carry_map` has nothing for {other}; nothing carried from it.")
    for iso in sorted(study_lib.countries()):
        # One source may be held by two carried studies: its facts are gathered across them
        # before its file is written, or the second study's would find the file there and stop.
        by_slug: dict[str, list[dict]] = {}
        their_list: dict[str, dict] = {}
        systems: dict[str, list[dict]] = {}
        origin: dict[str, set] = {}
        for other, rule in rules.items():
            theirs = os.path.join(study_lib.study_dir(other), "evidence", iso)
            if not rule or not os.path.isdir(theirs):
                continue
            for slug, fs in carried(study, other, rule, study_lib.read_csv(
                    os.path.join(theirs, "evidence.csv"))).items():
                seen = {(f["aspect"], f["value"], f["as_of"]) for f in by_slug.get(slug, [])}
                by_slug.setdefault(slug, []).extend(
                    f for f in fs if (f["aspect"], f["value"], f["as_of"]) not in seen)
                origin.setdefault(slug, set()).add(other)
            for r in study_lib.read_csv(os.path.join(theirs, "readlist.csv")):
                if r.get("kind") == "raw":
                    their_list.setdefault(r["slug"], r)
            for x in study_lib.read_csv(os.path.join(theirs, "systems.csv")):
                row = {**{k: x[k] for k in study_lib.SYSTEMS_FIELDS[1:-1]},
                       "class": x["class"] if x["class"] in classes else ("other" if x["class"] else "")}
                if row not in systems.setdefault(x["sources"], []):
                    systems[x["sources"]].append(row)
        if not by_slug:
            continue
        path = os.path.join(base, iso, "readlist.csv")
        mine = study_lib.read_csv(path)
        n_of = {r["slug"]: str(r["n"]) for r in mine if r.get("kind") == "raw"}
        nxt = max([int(r["n"]) for r in mine if str(r.get("n") or "").isdigit()] or [0])
        new_rows = []
        for slug in sorted(by_slug):
            if slug not in n_of:
                if slug not in their_list:
                    print(f"study-carry: note - {iso} {slug}: on no carried study's list; left out")
                    continue
                nxt += 1
                new_rows.append({**their_list[slug], "n": nxt, "slice": "", "pass": "carried",
                                 "why": "carried"})
                n_of[slug] = str(nxt)
            out = os.path.join(base, iso, "facts", f"{n_of[slug]}.json")
            if os.path.exists(out):
                continue
            docs, facts = docs + 1, facts + len(by_slug[slug])
            if a.dry:
                continue
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8", newline="\n") as fh:
                json.dump({"slug": slug, "facts": by_slug[slug], "systems": systems.get(slug, []),
                           "note": f"carried from {', '.join(sorted(origin[slug]))}; no document opened"},
                          fh, ensure_ascii=False, indent=1)
                fh.write("\n")
        appended += len(new_rows)
        if new_rows and not a.dry:
            study_lib.write_csv(path, study_lib.READLIST_FIELDS, mine + new_rows)
    print(f"study-carry: {a.study} - {facts} facts from {docs} documents carried, "
          f"{appended} sources appended to the reading lists"
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
