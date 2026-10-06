#!/usr/bin/env python3
r"""study-render.py — a study's cross-country pages, one per sub-indicator, from its CSVs.

    python scripts/study-render.py health

`maturity/documentation/maturity-study-method.md` §8. Writes
`outputs/maturity/{id}/{indicator_id}.md`: the norm, the ladder, then every country's stage,
short summary and the evidence that set it, each fact linked to its source.

**Nothing on the page is composed here.** The norm and the ladder are lifted from the study
file, where they are argued and fixed; the stage, the flags and the short summary are
`assessment.csv`'s; the facts are the `evidence.csv` rows `stage_sources` names. A page that
disagrees with a CSV is therefore a stale page, and re-running this is the whole repair.

The ladder is the table under the sub-indicator's bold label in the study file's ladders
section, and the norm is that file's norm section, found by their `## N. The ladders` and
`## N. The norm` headings. A study file without either stops the render.

Countries print in stage order, highest first, then the unplaced and the *No evidence*, so a
reader comparing one rung across countries has them together.

Exit: 0 written, 1 `assessment.csv` names an evidence row that does not exist, 2 the study,
its file or `assessment.csv` cannot be read.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402


def section(text: str, title: str) -> str:
    """The body of the `## N. {title}` section, or an empty string."""
    m = re.search(rf"^## \d+\. {re.escape(title)}\s*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    end = re.search(r"^## ", rest, re.M)
    return (rest[:end.start()] if end else rest).strip()


def ladder(study_text: str, label: str) -> str:
    """The markdown table that follows `**{label}**` in the ladders section."""
    body = section(study_text, "The ladders")
    m = re.search(rf"^\*\*{re.escape(label)}\*\*\s*$", body, re.M)
    if not m:
        return ""
    lines = []
    for line in body[m.end():].splitlines():
        if line.startswith("|"):
            lines.append(line)
        elif lines:
            break
    return "\n".join(lines)


def _link(url: str, label: str) -> str:
    return f"[{label}](<{url}>)" if " " in url else f"[{label}]({url})"


def _order(row: dict) -> tuple:
    stage = row["stage"]
    if stage.isdigit():
        return (0, -int(stage))
    return (1 if stage == study_lib.UNPLACED else 2, 0)


def page(study: dict, sub: dict, study_text: str, rows: list[dict],
         evidence: dict[str, list[dict]], names: dict[str, dict]) -> tuple[str, list[str]]:
    """`(the page, the stage_sources that name no evidence row)`."""
    missing = []
    rows = sorted(rows, key=lambda r: (_order(r), names.get(r["iso3"], {}).get("name", r["iso3"])))
    as_at = next((r["as_at"] for r in rows if r.get("as_at")), "")
    out = [f"# {sub['text']}", ""]
    if as_at:
        out += [f"*As at {as_at}.*", ""]
    out += ["## The norm", "", section(study_text, "The norm"), "",
            "## The ladder", "", ladder(study_text, sub["label"]), "",
            "## Countries by stage", "", "| Stage | Countries |", "|---|---|"]
    for n in sorted(study_lib.STAGES, reverse=True):
        out.append(f"| {n} {study_lib.STAGES[n]} | {sum(1 for r in rows if r['stage'] == str(n))} |")
    for word in study_lib.NOT_STAGED:
        out.append(f"| {word.capitalize()} | {sum(1 for r in rows if r['stage'] == word)} |")
    out += ["", "## Countries", ""]

    for r in rows:
        iso = r["iso3"]
        name = names.get(iso, {}).get("name", iso)
        stage = (f"{r['stage']} {study_lib.STAGES[int(r['stage'])]}" if r["stage"].isdigit()
                 else r["stage"].capitalize())
        out += [f"### {name}: {stage}", ""]
        if r.get("short"):
            out += [r["short"], ""]
        if r.get("flags"):
            out += ["*" + "; ".join(f.strip().capitalize() for f in r["flags"].split(";")) + ".*", ""]
        by_id = {e["row_id"]: e for e in evidence.get(iso, [])}
        facts = []
        for rid in filter(None, (s.strip() for s in (r.get("stage_sources") or "").split(";"))):
            e = by_id.get(rid)
            if e is None:
                missing.append(f"{iso} {sub['key']}: stage_sources names `{rid}`")
                continue
            facts.append(f"- {e['fact'].rstrip('.')} ({_link(e['url'], 'source, ' + e['as_of'])}).")
        if facts:
            out += facts + [""]
        if not r["stage"].isdigit() and r.get("gaps"):
            out += [f"Not established: {r['gaps']}", ""]
    return "\n".join(out).rstrip() + "\n", missing


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A study's cross-country pages, from its CSVs.")
    ap.add_argument("study")
    a = ap.parse_args(argv)

    try:
        study = study_lib.load(a.study)
        with open(os.path.join(study_lib.study_dir(a.study), study["study_file"]),
                  encoding="utf-8") as fh:
            study_text = fh.read()
    except (study_lib.StudyError, OSError, KeyError) as e:
        print(f"study-render: {e}")
        return 2
    out_dir = study_lib.out_dir(a.study)
    assessment = study_lib.read_csv(os.path.join(out_dir, "assessment.csv"))
    if not assessment:
        print(f"study-render: no rows in {os.path.join(out_dir, 'assessment.csv')}.")
        return 2
    if not section(study_text, "The norm"):
        print(f"study-render: {study['study_file']} has no `## N. The norm` section.")
        return 2

    evidence, names = study_lib.evidence(a.study), study_lib.countries()
    missing = []
    for sub in study["sub_indicators"]:
        if not ladder(study_text, sub["label"]):
            print(f"study-render: {study['study_file']} has no ladder table under **{sub['label']}**.")
            return 2
        rows = [r for r in assessment if r["indicator_id"] == sub["indicator_id"]]
        text, bad = page(study, sub, study_text, rows, evidence, names)
        missing += bad
        path = os.path.join(out_dir, sub["indicator_id"] + ".md")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"  {os.path.relpath(path, study_lib.CORPUS)}  {len(rows)} countries")
    for m in missing:
        print(f"study-render: FAIL - {m}, which is not a row of that country's evidence.csv.")
    print(f"study-render: {a.study} - {len(study['sub_indicators'])} page(s) written"
          + (f", {len(missing)} source(s) unresolved." if missing else "."))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
