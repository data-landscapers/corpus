#!/usr/bin/env python3
r"""lint-study.py — a maturity study's outputs say what its evidence says, in the shape the method sets.

    cd scripts/.workroot
    python scripts/lint-study.py health

`maturity/documentation/maturity-study-method.md` §8. It reads `outputs/maturity/{id}/` and the
evidence under `maturity/{id}/evidence/`, and holds them to what the method promises a reader:

- **A row for every cell.** 54 countries by the study's sub-indicators, each once, no others.
- **A stage or a reason.** `stage` is 1 to 5, `unplaced` or `no evidence`; a cell with no
  stage says what is not established in `gaps`.
- **Every source held.** A staged cell names its evidence rows in `stage_sources`; each is a
  row of that country's `evidence.csv` on that sub-indicator, and every evidence row's
  `source_slug` and `url` is held in `raw/`. Stage 1 is a claim like any other: it needs
  the cited absence.
- **The short summary inside its cap**: one line, 25 words at most, no link.
- **The cap rule applied wherever it fires.** A stage above the cap's line needs the
  governance values the study's `cap` names. Where they are missing the stage is the cap's
  line, `cap` records the rung coverage reached, and the flag is set. A `cap` or the flag
  on a cell the rule does not fire for fails too.
- **The long summaries.** `{ISO3}.md` carries a `## {label}` section per sub-indicator. For
  a staged cell: one paragraph per aspect, in the study's order, each opening with the
  aspect's name in bold and carrying a link; 120 to 250 words across them; then the two
  closing lines, ***Noted, not assessed*** and ***Not held***. Every link on the page is a
  URL held in `raw/`. A cell with no stage needs only its section and the closing lines.
- **The typology.** `systems.csv` has its columns, real countries and classes in the list.
- **The ids.** Each sub-indicator's id is what `adding-an-indicator.md` §2 mints from its text.

Prose quality is not counted here: `house-style.md` and `AI-speak.md` are a reader's job.

Runs from the workroot, because *held in `raw/`* is read from Corpus's own index.

Exit: 0 clean, 1 a breach, 2 the study or the index cannot be read.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib  # noqa: E402
import study_lib   # noqa: E402
import vault_lib   # noqa: E402

SHORT_CAP = 25
LONG_MIN, LONG_MAX = 120, 250
CLOSING = ("***Noted, not assessed***", "***Not held***")
MD_LINK = re.compile(r"\[([^\]]*)\]\((?:<[^>]*>|[^)]*)\)")


def assessment_fields(study: dict) -> list[str]:
    return (["iso3", "indicator_id", "as_at", "stage"] + [a["key"] for a in study["aspects"]]
            + ["cap", "flags", "short", "stage_sources", "gaps"])


def _flags(row: dict) -> list[str]:
    return [f.strip() for f in (row.get("flags") or "").split(";") if f.strip()]


def cap_problem(study: dict, row: dict) -> str:
    """Why this row breaks the study's cap rule, or an empty string."""
    cap = study.get("cap")
    if not cap or not row["stage"].isdigit():
        return ""
    held = {v.strip() for v in (row.get(cap["aspect"]) or "").split(";")}
    met = set(cap.get("all", ())) <= held and (not cap.get("any") or bool(set(cap["any"]) & held))
    stage, capped, flagged = int(row["stage"]), (row.get("cap") or "").strip(), cap["flag"] in _flags(row)
    if stage > cap["above"] and not met:
        return (f"stage {stage} without {cap['aspect']} of {' and '.join(cap.get('all', []))} "
                f"and one of {cap.get('any', [])}: the cap holds it at {cap['above']}")
    if capped:
        if not (capped.isdigit() and int(capped) > cap["above"]):
            return f"`cap` is `{capped}`; it records the rung coverage reached, above {cap['above']}"
        if met:
            return f"`cap` is set but {cap['aspect']} meets the rule, so nothing caps it"
        if stage != cap["above"] or not flagged:
            return f"capped from {capped}: the stage is {cap['above']} and the flag `{cap['flag']}` is set"
    elif flagged:
        return f"flagged `{cap['flag']}` with no `cap`: the flag marks a stage the rule lowered"
    return ""


def assessment_problems(study: dict, rows: list[dict], evidence: dict[str, list[dict]],
                        countries: dict) -> list[str]:
    out = []
    ids = {s["indicator_id"]: s for s in study["sub_indicators"]}
    asp = study_lib.aspects(study)
    if rows and list(rows[0]) != assessment_fields(study):
        out.append(f"assessment.csv columns are {list(rows[0])}; the study sets {assessment_fields(study)}")
        return out
    seen = {}
    for n, r in enumerate(rows, 2):
        key = (r["iso3"], r["indicator_id"])
        if key in seen:
            out.append(f"line {n}: {key[0]} {key[1]} is also on line {seen[key]}")
        seen[key] = n
        if r["iso3"] not in countries or r["indicator_id"] not in ids:
            out.append(f"line {n}: {key[0]} {key[1]} is not a cell of this study")
    for iso in sorted(countries):
        for iid in ids:
            if (iso, iid) not in seen:
                out.append(f"{iso} {iid}: no row")
    as_ats = {r["as_at"] for r in rows}
    if len(as_ats) > 1:
        out.append(f"more than one as-at: {sorted(as_ats)}")

    for n, r in enumerate(rows, 2):
        if r["indicator_id"] not in ids:
            continue
        sub = ids[r["indicator_id"]]["key"]
        where = f"line {n} ({r['iso3']} {sub})"
        stage = r["stage"].strip()
        staged = stage.isdigit() and int(stage) in study_lib.STAGES
        if not staged and stage not in study_lib.NOT_STAGED:
            out.append(f"{where}: stage `{stage}` is not 1 to 5, `unplaced` or `no evidence`")
            continue
        if not staged and not r["gaps"].strip():
            out.append(f"{where}: {stage} with no reason in `gaps`")
        for a in study["aspects"]:
            v = r[a["key"]].strip()
            bad = study_lib.value_problem(asp[a["key"]], sub, v) if v else ""
            if bad:
                out.append(f"{where}: {a['key']}: {bad}")
        for f in _flags(r):
            if f not in study["flags"]:
                out.append(f"{where}: flag `{f}` is not one of {study['flags']}")
        short = r["short"].strip()
        if not short:
            out.append(f"{where}: no short summary")
        elif "\n" in short or "](" in short or "http" in short:
            out.append(f"{where}: the short summary is one line with no link")
        elif len(short.split()) > SHORT_CAP:
            out.append(f"{where}: short summary is {len(short.split())} words; the cap is {SHORT_CAP}")
        mine = {e["row_id"] for e in evidence.get(r["iso3"], [])
                if e["sub_indicator"] == sub and e["source_slug"] not in study_lib.excluded(study)}
        named = [s.strip() for s in r["stage_sources"].split(";") if s.strip()]
        if staged and not named:
            out.append(f"{where}: stage {stage} with no `stage_sources`")
        for rid in named:
            if rid not in mine:
                out.append(f"{where}: stage_sources names `{rid}`, not a {sub} row of "
                           f"{r['iso3']}'s evidence.csv, or one from an excluded source")
        bad = cap_problem(study, r)
        if bad:
            out.append(f"{where}: {bad}")
    return out


def held_problems(evidence: dict[str, list[dict]], slugs: set[str], urls: set[str]) -> list[str]:
    out = []
    for iso, rows in evidence.items():
        for e in rows:
            if e["source_slug"] not in slugs:
                out.append(f"{iso} {e['row_id']}: source `{e['source_slug']}` is not held in raw/")
            if vault_lib.normalise_url(e["url"]) not in urls:
                out.append(f"{iso} {e['row_id']}: url {e['url']} is not a held record's")
    return out


def _words(text: str) -> int:
    return len(MD_LINK.sub(r"\1", text).replace("*", " ").split())


def long_problems(study: dict, iso: str, text: str, staged: dict[str, bool],
                  urls: set[str]) -> list[str]:
    """`staged` is sub-indicator key -> whether the cell carries a stage."""
    out = []
    for url in sorted(status_lib.links(text)):
        if vault_lib.normalise_url(url) not in urls:
            out.append(f"{iso}.md: links {url}, which is not a held record's URL")
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    sections = {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}
    for sub in study["sub_indicators"]:
        where = f"{iso}.md {sub['label']}"
        if sub["label"] not in sections:
            out.append(f"{where}: no `## {sub['label']}` section")
            continue
        paras = status_lib.paragraphs(sections[sub["label"]])
        for line in CLOSING:
            if not any(p.startswith(line) for p in paras):
                out.append(f"{where}: no closing line {line}")
        if not staged.get(sub["key"]):
            continue
        body = [p for p in paras if not p.startswith(CLOSING)]
        names = [a["name"] for a in study["aspects"]]
        opens = [next((n for n in names if p.startswith(f"**{n}")), None) for p in body]
        if opens != names:
            out.append(f"{where}: paragraphs open {opens}; the study's order is {names}")
            continue
        for name, p in zip(names, body):
            if not status_lib.links(p):
                out.append(f"{where}: the paragraph on {name} carries no link")
        n = sum(_words(p) for p in body)
        if not LONG_MIN <= n <= LONG_MAX:
            out.append(f"{where}: {n} words; the long summary is {LONG_MIN} to {LONG_MAX}")
    return out


def systems_problems(study: dict, rows: list[dict], countries: dict) -> list[str]:
    if not rows:
        return ["systems.csv is missing or empty"]
    if list(rows[0]) != study_lib.SYSTEMS_FIELDS:
        return [f"systems.csv columns are {list(rows[0])}; the method sets {study_lib.SYSTEMS_FIELDS}"]
    out = []
    for n, r in enumerate(rows, 2):
        if r["iso3"] not in countries:
            out.append(f"systems.csv line {n}: `{r['iso3']}` is not a country")
        if r["class"] and r["class"] not in study["classes"]:
            out.append(f"systems.csv line {n}: class `{r['class']}` is not in the typology")
        if not r["system"].strip():
            out.append(f"systems.csv line {n}: no system named")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A maturity study's outputs, held to the method.")
    ap.add_argument("study")
    a = ap.parse_args(argv)

    try:
        study = study_lib.load(a.study)
        index = vault_lib.load_index()
    except (study_lib.StudyError, vault_lib.ForeignIndex, vault_lib.EmptyIndex) as e:
        print(f"lint-study: {e}")
        return 2
    raw = [r for r in index if r["d"].get("folder") == "raw" and r["d"].get("ext") == ".md"]
    slugs = {r["d"]["slug"] for r in raw}
    urls = {r["d"]["url_norm"] for r in raw if r["d"].get("url_norm")}

    countries, evidence = study_lib.countries(), study_lib.evidence(a.study)
    out_dir = study_lib.out_dir(a.study)
    rows = study_lib.read_csv(os.path.join(out_dir, "assessment.csv"))
    problems = []
    for s in study["sub_indicators"]:
        if study_lib.mint(s["subject"], s["text"]) != s["indicator_id"]:
            problems.append(f"study.json: `{s['indicator_id']}` is not what its text mints, "
                            f"`{study_lib.mint(s['subject'], s['text'])}`")
    for iso, ev in evidence.items():
        problems += study_lib.evidence_problems(study, iso, ev)
    problems += held_problems(evidence, slugs, urls)
    if not rows:
        problems.append("assessment.csv is missing or empty")
    else:
        problems += assessment_problems(study, rows, evidence, countries)
    ids = {s["indicator_id"]: s["key"] for s in study["sub_indicators"]}
    for iso in sorted(countries):
        try:
            with open(os.path.join(out_dir, iso + ".md"), encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            problems.append(f"{iso}.md: no long summaries")
            continue
        staged = {ids[r["indicator_id"]]: r["stage"].strip().isdigit()
                  for r in rows if r["iso3"] == iso and r["indicator_id"] in ids}
        problems += long_problems(study, iso, text, staged, urls)
    problems += systems_problems(study, study_lib.read_csv(os.path.join(out_dir, "systems.csv")),
                                 countries)

    for p in problems:
        print(f"lint-study: FAIL - {p}")
    if problems:
        print(f"lint-study: {a.study} - {len(problems)} breach(es).")
        return 1
    print(f"lint-study: ok - {a.study}: {len(rows)} cells, {sum(map(len, evidence.values()))} "
          f"facts, every source held.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
