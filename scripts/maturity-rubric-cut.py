#!/usr/bin/env python3
r"""maturity-rubric-cut.py — cut reviewed chapters of the rubric draft into the lookup.

    python scripts/maturity-rubric-cut.py --chapter Governance --kind instrument --kind system
    python scripts/maturity-rubric-cut.py --check      # every cut row still equals the draft

**The draft is the source until the lookup exists** (task C2). Cowork drafts
`documentation/maturity-rubric.md` a chapter's kind at a time; CC reviews it
(`documentation/maturity-rubric-review.md`) and, on acceptance, cuts exactly what was accepted —
named by chapter and kind — into `lookups/maturity-rubric.csv`. Rows already in the lookup for
other indicators are kept, so the lookup grows chapter by chapter and never takes a row that
has not been reviewed, even when the draft already holds the next chapter.

**Nothing is cut that the checker refuses.** `lint-maturity-rubric.py` runs over the draft
first, limited to what is being cut; a failure stops the cut.

**`--check` is the drift test**: every indicator in the lookup must still read, row for row,
as the draft does. A later edit to an accepted chapter is a re-review and a re-cut, not a quiet
divergence between the two files.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indicators_lib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DRAFT = os.path.join(ROOT, "documentation", "maturity-rubric.md")
LOOKUP = os.path.join(ROOT, "lookups", "maturity-rubric.csv")

_spec = importlib.util.spec_from_file_location("lr", os.path.join(HERE, "lint-maturity-rubric.py"))
lr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lr)
COLUMNS = lr.COLUMNS


def clean(r: dict) -> dict:
    return {"indicator_id": r["indicator_id"].strip(), "stage": str(int(r["stage"])),
            "anchor": r["anchor"].strip(), "interpolated": r["interpolated"].strip()}


def held() -> list[dict]:
    return [clean(r) for r in lr.read(LOOKUP)[1]] if os.path.exists(LOOKUP) else []


def render(rows: list[dict]) -> str:
    order = {r["indicator_id"]: n for n, r in enumerate(indicators_lib.frame())}
    rows = sorted(rows, key=lambda r: (order.get(r["indicator_id"], 10**6), int(r["stage"])))
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


# ------------------------------------------------------------------ the measures' specifications
# A measure's heading carries a list (maturity-rubric.md, How to read a measure) whose `Method` and
# `Cuts` lines are machine-read. They are cut into their own lookup beside the rubric, and read
# by maturity-assess.py's band(). The prose items travel with them so the lookup reads on its own.

MEASURES = os.path.join(ROOT, "lookups", "maturity-measures.csv")
MEASURE_COLUMNS = ("indicator_id", "method", "direction", "cuts", "provisional", "cut_note",
                   "unit", "value", "record", "band")
HEAD = re.compile(r"^###\s+`([a-z]+\.[a-z]+--[a-z0-9-]+)`")
ITEM = re.compile(r"^-\s+\*\*(Value|Record|Band|Method|Cuts)\*\*:\s*(.*)$")
UNIT = re.compile(r"\*\*Unit\*\*\s+([^·*]+?)\s*·")


def specs(path: str = DRAFT) -> dict[str, dict]:
    """{indicator_id: row} for every heading in the draft that carries a Method line."""
    out, cur = {}, None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = HEAD.match(line)
            if m:
                cur = {"indicator_id": m.group(1)}
                continue
            m = ITEM.match(line.rstrip("\n")) if cur is not None else None
            if m:
                cur[m.group(1).lower()] = m.group(2).strip()
                if m.group(1) == "Method":
                    out[cur["indicator_id"]] = cur
    rows = {}
    for iid, s in out.items():
        method, _, direction = (x.strip() for x in s["method"].partition("·"))
        head, _, note = s.get("cuts", "").partition("—")
        cuts = [c.strip() for c in head.split("·") if c.strip()]
        for c in cuts:
            float(c)                              # a cut that is not a number stops the cut
        u = UNIT.search(s.get("value", ""))
        rows[iid] = {"indicator_id": iid, "method": method, "direction": direction,
                     "cuts": "|".join(cuts), "provisional": "1" if "provisional" in note else "0",
                     "cut_note": note.strip(), "unit": u.group(1).strip() if u else "",
                     "value": s.get("value", ""), "record": s.get("record", ""),
                     "band": s.get("band", "")}
    return rows


def spec_problems(rows: dict[str, dict]) -> list[str]:
    bad = []
    for iid, r in rows.items():
        if r["method"] not in ("target", "quintiles", "fixed"):
            bad.append(f"{iid}: method {r['method']!r}")
        if r["direction"] not in ("higher", "lower"):
            bad.append(f"{iid}: direction {r['direction']!r}")
        cuts = [float(c) for c in r["cuts"].split("|")]
        if len(cuts) not in (3, 4):
            bad.append(f"{iid}: {len(cuts)} cuts; stages 2–4, and 5 where it is a number")
        order = cuts if r["direction"] == "higher" else [-c for c in cuts]
        if order != sorted(order):
            bad.append(f"{iid}: cuts out of order for a {r['direction']}-is-better measure")
        if r["method"] == "quintiles" and r["provisional"] != "1":
            bad.append(f"{iid}: a quintile row without provisional cuts")
    return bad


def render_specs(rows: list[dict]) -> str:
    order = {r["indicator_id"]: n for n, r in enumerate(indicators_lib.frame())}
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=MEASURE_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: order.get(r["indicator_id"], 10**6)))
    return buf.getvalue()


def held_specs() -> list[dict]:
    if not os.path.exists(MEASURES):
        return []
    with open(MEASURES, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cut reviewed rubric chapters into the lookup.")
    ap.add_argument("--chapter", action="append", default=[], help="a frame chapter, repeatable")
    ap.add_argument("--kind", action="append", default=[],
                    help="instrument, system or measure, repeatable; all kinds when omitted")
    ap.add_argument("--check", action="store_true", help="compare the lookup with the draft")
    a = ap.parse_args(argv)

    draft = [clean(r) for r in lr.read(DRAFT)[1]]
    by_id = {r["indicator_id"]: r for r in indicators_lib.assessed()}

    if a.check:
        lookup = held()
        cut_ids = {r["indicator_id"] for r in lookup}
        want = [r for r in draft if r["indicator_id"] in cut_ids]
        if render(lookup) != render(want):
            print("maturity-rubric-cut: the lookup and the draft disagree for an indicator "
                  "already cut — re-review the change and re-cut its chapter")
            return 1
        sp, have = specs(), held_specs()
        if render_specs(have) != render_specs([sp[r["indicator_id"]] for r in have
                                               if r["indicator_id"] in sp]):
            print("maturity-rubric-cut: maturity-measures.csv and the draft's specifications "
                  "disagree — re-review and re-cut the measures")
            return 1
        print(f"maturity-rubric-cut: ok — {len(cut_ids)} indicator(s) in the lookup read as "
              f"the draft does")
        return 0

    if not a.chapter:
        ap.error("name the accepted chapter(s) with --chapter")
    pick = {i for i, r in by_id.items()
            if r["chapter"] in a.chapter and (not a.kind or r["kind"] in a.kind)}
    rows = [r for r in draft if r["indicator_id"] in pick]
    for ch in a.chapter:
        fails, warns, st = lr.check(DRAFT, chapter=ch)
        mine = [f for f in fails
                if any(i in f for i in pick) or (f"{ch} " in f and "drafted in part" in f)]
        if mine:
            print("maturity-rubric-cut: the checker refuses what would be cut:\n  "
                  + "\n  ".join(mine))
            return 1
    missing = sorted(pick - {r["indicator_id"] for r in rows})
    if missing:
        print(f"maturity-rubric-cut: no draft rows for {', '.join(missing)} — nothing cut")
        return 1
    measures = {i for i in pick if by_id[i]["kind"] == "measure"}
    if measures:
        sp = specs()
        gone = sorted(measures - set(sp))
        bad = spec_problems({i: sp[i] for i in measures if i in sp})
        if gone or bad:
            print("maturity-rubric-cut: the measures' specifications refuse the cut:\n  "
                  + "\n  ".join([f"{i}: no Method line" for i in gone] + bad))
            return 1
        keep = [r for r in held_specs() if r["indicator_id"] not in measures]
        with open(MEASURES, "w", encoding="utf-8", newline="") as fh:
            fh.write(render_specs(keep + [sp[i] for i in measures]))
    kept = [r for r in held() if r["indicator_id"] not in pick]
    text = render(kept + rows)
    with open(LOOKUP, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write(text)
    ids = len({r["indicator_id"] for r in kept + rows})
    print(f"maturity-rubric-cut: {len(pick)} indicator(s), {len(rows)} row(s) cut from "
          f"{', '.join(a.chapter)}{' (' + ', '.join(a.kind) + ')' if a.kind else ''}; "
          f"the lookup now holds {ids} indicator(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
