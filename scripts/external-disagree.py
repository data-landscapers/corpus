#!/usr/bin/env python3
r"""external-disagree.py — where an external register and Corpus's evidence disagree on a fact.

    python scripts/external-disagree.py          # -> logs/external-disagreements.csv, counts printed

Strategic review 2026-11-26, R186. **Facts, not scores**: Corpus keeps the evidence behind an
external score and never the score, so this compares only what a register or a survey answer
states as fact, against the cell Corpus has staged. The sources are the two registers, UNCTAD's
Global Cyberlaw Tracker (`unctad`) and Carnegie's Africa Technology Policy Tracker (`aftech`),
and the GovTech Maturity Index survey answers (`gtmi`), as `external-claims.py` cut them into
`reference/external/claims.csv`. Indices such as ODIN, ITU's tracker and SPI are outside it.

**A claim reaches a cell** through its `studies` and `fit` (from `lookups/external-items.csv`),
and only where the fit is `same` and the study stages one indicator: a partial, broader or
narrower question, or a study of several indicators, has no single cell to disagree with (a
first run over `partial` too listed 1,709 lines, most of them a related instrument, not this one).
GTMI's latest round per country and question is used; registers have no rounds.

**Four kinds of disagreement**, each a line:

- `exists` — the register lists the law, policy or system (UNCTAD *Legislation*, every Carnegie
  row, a GTMI *Yes*), and Corpus stages the cell 1 or 2, or holds no evidence for it;
- `absent` — the register says none (UNCTAD *No Legislation*, GTMI *0 No*), and Corpus stages it
  3 or above. A register's "no" is never taken as a fact (`study-external.py`); listed for triage;
- `draft` — the register says draft or planned, and Corpus stages it 1 (absent and not prepared);
- `year` — the register dates a law, policy or strategy (an `instrument` in `indicators.csv`;
  a system's launch year is not what its stage turns on), Corpus stages it 3 or above, and the
  year appears nowhere in the cell's summary or paragraph, which name other years.

**Disagreement is not error**, and OSINT's rule that reference studies are cited and not absorbed
stands. The list says where to look first; R187's weekly checklist reads it.
"""
from __future__ import annotations

import collections
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLAIMS = os.path.join(ROOT, "reference", "external", "claims.csv")
INDICATORS = os.path.join(ROOT, "lookups", "indicators.csv")
OUT = os.path.join(ROOT, "logs", "external-disagreements.csv")
SOURCES = ("unctad", "aftech", "gtmi")
FIELDS = ["kind", "source", "iso3", "indicator_id", "study", "fit", "register", "name",
          "register_year", "corpus_stage", "corpus_years", "url"]
YEAR = re.compile(r"\b(19[89]\d|20[0-3]\d)\b")


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def register_says(source, status):
    """`exists`, `absent`, `draft` or None (no data, or not a statement of fact)."""
    s = status.strip().lower()
    if source == "aftech":
        return "exists"                      # every row is an instrument that was issued
    if source == "unctad":
        return {"legislation": "exists", "no legislation": "absent", "draft legislation": "draft"}.get(s)
    if s.startswith("0 no"):
        return "absent"
    if "planned" in s or "draft" in s or "in progress" in s:
        return "draft"
    if s[:1] in "12" and "yes" in s:
        return "exists"
    return None


def cells():
    """{study: (indicator_id, {iso3: (stage, text)})} for studies staging one indicator."""
    out = {}
    for sj in glob.glob(os.path.join(ROOT, "maturity", "*", "study.json")):
        sid = os.path.basename(os.path.dirname(sj))
        study = json.load(open(sj, encoding="utf-8"))
        subs = study.get("sub_indicators", [])
        apath = os.path.join(ROOT, "outputs", "maturity", sid, "assessment.csv")
        if len(subs) != 1 or not os.path.exists(apath):
            continue
        ind = subs[0]["indicator_id"]
        paras = {}
        ppath = os.path.join(ROOT, "outputs", "maturity", sid, "paragraphs.csv")
        if os.path.exists(ppath):
            paras = {r["iso3"]: r["paragraph"] for r in read(ppath) if r["indicator_id"] == ind}
        out[sid] = (ind, {r["iso3"]: (r["stage"], (r.get("short") or "") + " " + paras.get(r["iso3"], ""))
                          for r in read(apath) if r["indicator_id"] == ind})
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    staged = cells()
    kind_of = {r["indicator_id"]: r["kind"] for r in read(INDICATORS)}
    rows = [r for r in read(CLAIMS) if r["source"] in SOURCES and len(r["iso3"]) == 3 and not r["iso3"].startswith("X")]
    latest = {}
    for r in rows:
        if r["source"] == "gtmi":
            k = (r["iso3"], r["item"])
            if r["survey_year"] > latest.get(k, ""):
                latest[k] = r["survey_year"]
    out, seen = [], set()
    for r in rows:
        if r["source"] == "gtmi" and r["survey_year"] != latest[(r["iso3"], r["item"])]:
            continue
        says = register_says(r["source"], r["status"])
        # A Carnegie row tags one instrument with several topics (a blockchain policy under
        # digital payments); only a row on one topic is about the indicator it maps to.
        if not says or (r["source"] == "aftech" and ";" in r["item"]):
            continue
        for sid, fit in zip(r["studies"].split(";"), r["fit"].split(";")):
            if fit != "same" or sid not in staged:
                continue
            ind, by = staged[sid]
            stage, text = by.get(r["iso3"], ("", ""))
            n = int(stage) if stage.isdigit() else 0
            years = sorted(set(YEAR.findall(text)))
            kind = None
            if says == "exists" and n <= 2:
                kind = "exists"
            elif says == "absent" and n >= 3:
                kind = "absent"
            elif says == "draft" and n == 1:
                kind = "draft"
            elif (says == "exists" and n >= 3 and r["year"] and years and r["year"] not in years
                  and kind_of.get(ind) == "instrument"):
                kind = "year"
            if not kind:
                continue
            key = (kind, r["source"], r["iso3"], ind, r["name"])
            if key in seen:
                continue
            seen.add(key)
            out.append({"kind": kind, "source": r["source"], "iso3": r["iso3"], "indicator_id": ind,
                        "study": sid, "fit": fit, "register": r["status"], "name": r["name"],
                        "register_year": r["year"], "corpus_stage": stage or "no evidence",
                        "corpus_years": ";".join(years), "url": r["url"] or r["documents"]})
    out.sort(key=lambda x: (x["kind"], x["study"], x["iso3"], x["source"]))
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    by = collections.Counter((x["kind"], x["source"]) for x in out)
    print(f"external-disagree: {len(out)} disagreements over {len({(x['iso3'], x['indicator_id']) for x in out})} cells "
          f"-> {os.path.relpath(OUT, ROOT)}")
    for (k, s), n in sorted(by.items()):
        print(f"  {k:7} {s:7} {n}")


if __name__ == "__main__":
    main()
