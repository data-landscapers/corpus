#!/usr/bin/env python3
r"""test_study_update.py — the maturity upkeep's log, register and rotation, on a fixture study.

    python scripts/test_study_update.py

`study-update.py` is run against a one-study, two-indicator tree in a temporary folder, so a
failure names the rule and not the state of the live study.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import study_lib  # noqa: E402

_spec = importlib.util.spec_from_file_location("su", HERE / "study-update.py")
su = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(su)

fails: list[str] = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
    if not ok:
        fails.append(label)
        print(f"          got  {got!r}\n          want {want!r}")


def fixture(root: Path) -> None:
    live = json.loads((Path(study_lib.CORPUS) / "maturity" / "health" / "study.json").read_text(encoding="utf-8"))
    live.update(id="t", searched="2026-10-06")
    (root / "maturity" / "t" / "evidence" / "KEN").mkdir(parents=True)
    (root / "maturity" / "t" / "study.json").write_text(json.dumps(live), encoding="utf-8")
    (root / "maturity" / "t" / live["study_file"]).write_text("# T\n", encoding="utf-8")
    cells = [{"sub_indicator": s["key"], "stage": "3", "stage_sources": "KEN-001"} for s in live["sub_indicators"]]
    (root / "maturity" / "t" / "evidence" / "KEN" / "stage.json").write_text(
        json.dumps({"iso3": "KEN", "cells": cells}), encoding="utf-8")
    study_lib.write_csv(str(root / "outputs" / "maturity" / "t" / "assessment.csv"), ["iso3", "indicator_id", "stage"],
                        [{"iso3": "KEN", "indicator_id": s["indicator_id"], "stage": "2"}
                         for s in live["sub_indicators"]])
    study_lib.write_csv(str(root / "maturity" / "t" / "evidence" / "arrivals.csv"), study_lib.ARRIVAL_FIELDS,
                        [{"iso3": "KEN", "n": "9", "slug": "a-doc", "listed": "2026-10-09", "outcome": "", "closed": ""}])
    (root / "logs").mkdir()


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixture(root)
        rot = str(root / "logs" / "maturity-review.csv")
        night = dt.datetime(2026, 10, 10, 23, 0)
        run = lambda *argv, now=night: su.main(list(argv), now=now, root=str(root), path=rot)

        print("the log")
        row = su.log("t", "KEN", "hmis", "fact", "a  new   figure", str(root), dt.date(2026, 10, 10))
        check("from is the published stage and to is stage.json's", (row["from"], row["to"]), ("2", "3"))
        check("the note is one line", row["note"], "a new figure")
        doc = json.loads((root / "maturity" / "t" / "evidence" / "KEN" / "stage.json").read_text(encoding="utf-8"))
        check("the logged cell carries the day as its as-at and the other cell none",
              [c.get("as_at") for c in doc["cells"]], ["2026-10-10", None])
        su.log("t", "KEN", "hmis", "review", "read whole, left alone", str(root), dt.date(2026, 11, 1))
        check("every reassessment is a row, moved or not",
              [(r["kind"], r["from"], r["to"]) for r in study_lib.read_csv(su.history_path("t", str(root)))],
              [("fact", "2", "3"), ("review", "2", "3")])
        check("an unknown sub-indicator is refused", run("log", "t", "KEN", "nope", "--kind", "fact", "--note", "x"), 2)

        print("the arrivals")
        check("an open arrival is work", run("order"), 0)
        check("closing it records the outcome", run("close", "t", "KEN", "a-doc", "--outcome", "nothing"), 0)
        check("and nothing is then owed", run("order"), 1)
        check("a second close finds nothing open", run("close", "t", "KEN", "a-doc", "--outcome", "fact"), 2)

        print("the rotation")
        check("one row per indicator of an issued study", [r["key"] for r in su.rotation(str(root), rot)], ["hmis", "emr"])
        check("an attended daytime cycle owes none", run("next", now=dt.datetime(2026, 10, 10, 14, 0)), 1)
        check("a night cycle owes one", run("next"), 0)
        check("from /poll it is owed by day too", run("next", "--poll", now=dt.datetime(2026, 10, 10, 14, 0)), 0)
        run("done", "t", "emr"); run("done", "t", "hmis")
        check("done stamps the day", {r["last_reviewed"] for r in su.rotation(str(root), rot)}, {"2026-10-10"})
        check("none is owed while all are inside the gap", run("next", now=dt.datetime(2026, 10, 20, 23, 0)), 1)
        check("and one is owed once the gap has run",
              run("next", now=night + dt.timedelta(days=su.MIN_GAP_DAYS)), 0)
        check("an indicator not in the rotation is refused", run("done", "t", "nope"), 2)

        print("the standing search")
        check("not due inside a year", su.search_due(str(root), dt.date(2027, 10, 6)), [])
        check("due after it", su.search_due(str(root), dt.date(2027, 10, 8)),
              ["standing search due: t, last searched 2026-10-06"])

    print(f"\n{len(fails)} failed" if fails else "\nall ok")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
