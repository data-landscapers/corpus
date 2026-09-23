#!/usr/bin/env python3
r"""lint-maturity-rubric.py — the maturity rubric against the frame and the norms register.

    python scripts/lint-maturity-rubric.py                 # the chapters drafted so far
    python scripts/lint-maturity-rubric.py --complete      # every assessed indicator, all five
    python scripts/lint-maturity-rubric.py --chapter Governance

`lookups/maturity-rubric.csv` is `indicator_id, stage, anchor, interpolated`: five rows per
assessed indicator, each anchor naming the evidence that satisfies that stage, and
`interpolated` saying whether the norm states the rung or Corpus does
(`documentation/maturity-assessment.md` §5). It is drafted a chapter at a time in Cowork and
reviewed here before the next chapter starts (task C2), so this is what makes a review
mechanical: the structure, the frame, and whether `interpolated` agrees with what the register
says each norm fixes.

**Fails** — the file's shape; an id not in the assessed frame; a stage outside 1–5, repeated or
missing; an empty anchor; an `interpolated` cell that does not open *yes*, *no* or *partly*; a
chapter drafted in part (a chapter is drafted whole or not at all, so a gap is a dropped row);
and the `fixes` rules below. With `--complete`, an assessed indicator with no rows.

**The `fixes` rules** read `lookups/maturity-norms.csv`, which is the register's cut.

- *Corpus-defined* (`fixes` is `—`) — all five rungs interpolated: nothing states any of them.
- *top* — stage 5 is the norm's and is not interpolated. Stages 1–4 are Corpus's, and one marked
  otherwise is a warning: the register says the norm fixes the top and nothing below it.
- *target* — a measure's target is *meets the norm*, stage 4, so stage 4 or 5 is not
  interpolated. A *proxy* target fixes no rung of this indicator's own and is exempt.
- every row except Corpus-defined has at least one rung the norm states; all five *yes* on a
  norm-anchored row says the anchor anchors nothing.
- *rungs* — the norm supplies the ladder, so fewer than two non-interpolated stages is a warning.

**Warns** — the rules above marked as warnings, and an anchor leaning on a word that names a
judgement rather than evidence (*adequate*, *robust*, *effective* …). The rubric's own rule is
that an anchor names evidence a mapped row can satisfy, never a feeling; a word list cannot
enforce that, but it can point a reviewer at the rows to read first.

Prints the interpolated-rung count, which the methodology page publishes (task F4).
Exit 0 clean (warnings allowed), 1 a failure, 2 no rubric.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indicators_lib  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
RUBRIC = os.path.join(ROOT, "lookups", "maturity-rubric.csv")
NORMS = os.path.join(ROOT, "lookups", "maturity-norms.csv")
COLUMNS = ("indicator_id", "stage", "anchor", "interpolated")
STAGES = (1, 2, 3, 4, 5)
INTERP = re.compile(r"^(yes|no|partly)\b", re.I)
VAGUE = re.compile(r"\b(adequate(ly)?|sufficient(ly)?|robust|effective(ly)?|strong(ly)?|mature|"
                   r"good|well[- ]developed|appropriate(ly)?|meaningful(ly)?|significant(ly)?|"
                   r"satisfactory|reasonable)\b", re.I)


def read(path: str) -> tuple[list[str], list[dict]]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return list(r.fieldnames or []), list(r)


def fixes_of(text: str) -> set[str]:
    """`top`, `rungs`, `target`, `proxy` from the register's free-text fixes cell."""
    t = text.lower()
    return {k for k in ("top", "rungs", "target", "proxy") if k in t}


def check(rubric: str = RUBRIC, norms: str = NORMS, chapter: str = "", complete: bool = False,
          frame: list[dict] | None = None):
    """`(fails, warns, stats)` for the rubric file."""
    fails, warns = [], []
    frame = frame if frame is not None else indicators_lib.assessed()
    by_id = {r["indicator_id"]: r for r in frame}
    header, rows = read(rubric)
    if tuple(header) != COLUMNS:
        return [f"header is {','.join(header)}, not {','.join(COLUMNS)}"], [], {}
    norm = {r["indicator_id"]: r for r in read(norms)[1]} if os.path.exists(norms) else {}

    stages = defaultdict(dict)
    for i, r in enumerate(rows, start=2):
        iid, at = r["indicator_id"].strip(), f"line {i}"
        if iid not in by_id:
            fails.append(f"{at}: {iid!r} is not an assessed indicator in the frame")
            continue
        if chapter and by_id[iid]["chapter"] != chapter:
            continue
        try:
            st = int(r["stage"])
        except ValueError:
            st = 0
        if st not in STAGES:
            fails.append(f"{at}: {iid} stage {r['stage']!r} is not 1-5")
            continue
        if st in stages[iid]:
            fails.append(f"{at}: {iid} stage {st} is already line {stages[iid][st]['line']}")
            continue
        if not r["anchor"].strip():
            fails.append(f"{at}: {iid} stage {st} has no anchor")
        m = INTERP.match(r["interpolated"].strip())
        if not m:
            fails.append(f"{at}: {iid} stage {st} interpolated {r['interpolated']!r} does not "
                         f"open yes, no or partly")
        v = VAGUE.search(r["anchor"])
        if v:
            warns.append(f"{at}: {iid} stage {st} anchor leans on {v.group(0)!r} — name the "
                         f"evidence that shows it")
        stages[iid][st] = {"line": i, "interp": (m.group(1).lower() if m else "")}

    drafted = Counter(by_id[i]["chapter"] for i in stages)
    for ch in sorted(drafted):
        want = [r["indicator_id"] for r in frame if r["chapter"] == ch]
        gaps = [i for i in want if i not in stages]
        if gaps and not complete:
            fails.append(f"chapter {ch} is drafted in part — no rows for {', '.join(gaps)}")
    if complete:
        for r in frame:
            if (not chapter or r["chapter"] == chapter) and r["indicator_id"] not in stages:
                fails.append(f"{r['indicator_id']} has no rubric rows")

    interpolated = partly = 0
    for iid, got in stages.items():
        missing = [s for s in STAGES if s not in got]
        if missing:
            fails.append(f"{iid}: stage(s) {missing} missing — five rows per indicator")
        val = {s: got[s]["interp"] for s in got}
        interpolated += sum(v == "yes" for v in val.values())
        partly += sum(v == "partly" for v in val.values())
        n = norm.get(iid)
        if not n:
            fails.append(f"{iid}: no row in maturity-norms.csv, so its rungs cannot be checked")
            continue
        fx = fixes_of(n["fixes"])
        stated = [s for s, v in val.items() if v != "yes"]
        if n["tier"] == "corpus":
            if stated:
                fails.append(f"{iid}: Corpus-defined, yet stage(s) {stated} marked as the "
                             f"norm's")
            continue
        if not stated and "proxy" not in fx:
            fails.append(f"{iid}: every rung interpolated, but the register anchors it on "
                         f"{n['instrument']!r} (fixes {n['fixes']!r})")
        if "top" in fx and val.get(5) == "yes":
            fails.append(f"{iid}: the norm fixes the top (fixes {n['fixes']!r}), so stage 5 "
                         f"is not interpolated")
        if "top" in fx and "rungs" not in fx:
            below = [s for s in (1, 2, 3, 4) if val.get(s) not in ("yes", None)]
            if below:
                warns.append(f"{iid}: fixes {n['fixes']!r} is top only, yet stage(s) {below} "
                             f"are marked as the norm's — cite the provision or mark yes")
        if "target" in fx and "proxy" not in fx and val.get(4) == "yes" and val.get(5) == "yes":
            fails.append(f"{iid}: the norm states a target (fixes {n['fixes']!r}), which is "
                         f"stage 4 or 5, yet both are interpolated")
        if "rungs" in fx and len(stated) < 2:
            warns.append(f"{iid}: fixes {n['fixes']!r} says the norm supplies rungs, yet only "
                         f"{len(stated)} stage(s) are marked as the norm's")
    stats = {"indicators": len(stages), "rows": sum(len(g) for g in stages.values()),
             "interpolated": interpolated, "partly": partly, "chapters": dict(drafted)}
    return fails, warns, stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check the maturity rubric.")
    ap.add_argument("--rubric", default=RUBRIC)
    ap.add_argument("--norms", default=NORMS)
    ap.add_argument("--chapter", default="", help="one chapter only, e.g. Governance")
    ap.add_argument("--complete", action="store_true",
                    help="require every assessed indicator, not only the chapters drafted")
    a = ap.parse_args(argv)
    if not os.path.exists(a.rubric):
        print(f"lint-maturity-rubric: no rubric at {os.path.relpath(a.rubric, ROOT)} yet.")
        return 2
    fails, warns, st = check(a.rubric, a.norms, a.chapter, a.complete)
    for w in warns:
        print(f"lint-maturity-rubric: warn — {w}")
    for f in fails:
        print(f"lint-maturity-rubric: FAIL — {f}")
    if st:
        chs = ", ".join(f"{c} {n}" for c, n in sorted(st["chapters"].items()))
        print(f"lint-maturity-rubric: {st['indicators']} indicator(s), {st['rows']} row(s) "
              f"[{chs}]; {st['interpolated']} interpolated rung(s), {st['partly']} partly.")
    if fails:
        print(f"lint-maturity-rubric: {len(fails)} failure(s), {len(warns)} warning(s).")
        return 1
    print(f"lint-maturity-rubric: ok — {len(warns)} warning(s) to read.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
