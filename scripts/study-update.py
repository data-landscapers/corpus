#!/usr/bin/env python3
r"""study-update.py — keeping a finished maturity study current: the work order, the log and the rebuild.

    python scripts/study-update.py order                   what arrived and is unread, by study and country; exit 1 if nothing
    python scripts/study-update.py close STUDY ISO3 SLUG --outcome nothing|fact|reassessed|instrument|old|capped
    python scripts/study-update.py log STUDY ISO3 KEY --kind fact|review|ladder --note "..."
    python scripts/study-update.py next [--poll]           tonight's three indicators to rebuild; exit 1 if none is owed
    python scripts/study-update.py done STUDY KEY --minutes N --tokens M --staged N
                                                           stamp an indicator's rebuild and what it cost
    python scripts/study-update.py list                    the control list, most overdue first

`MATURITY-UPDATE.md` is the procedure; this is its mechanical half *(Bill, 2026-10-09)*.

**Arrivals.** `study-select.py {id} --new` appends to each country's reading list the catalogue
documents the study's own term test now admits and the list does not hold, and enters each in
`maturity/{id}/evidence/arrivals.csv`. `order` prints the entries still open. `close` records
what reading one came to: `nothing`, a `fact` added to `evidence.csv`, or a fact that called for
the cell to be `reassessed`. It is the same set difference BUILD stages 4 and 4b work, and like
them it never looks back, which is what the rebuild is for.

**The log.** `outputs/maturity/{id}/history.csv` holds every reassessment of a cell, whether or
not the stage moved *(Bill)*. `log` is run after the cell's `stage.json` is rewritten and before
`study-assess.py`: it reads the stage the published `assessment.csv` holds as `from`, the stage
`stage.json` now holds as `to`, appends the row and stamps the cell's `as_at` with today, so
*Last assessed* moves. `kind` says what called for it, and the site reads it:

- `fact`   — a new fact; a change of stage is a **move**, shown under *Stage last moved* and in
  the changes box;
- `review` — the rebuild's whole reassessment; a change is shown as *Reassessed*, not as movement;
- `ladder` — a rung was rewritten; likewise *Reassessed*.

**The rebuild is by indicator** *(Bill, 2026-10-09)*: a whole reassessment reads all 54
countries side by side against the one ladder, which a country at a time cannot do. **Three a
night** *(Bill, 2026-10-18; two from 2026-10-17)*. `logs/maturity-review.csv` is
the control list: one row per sub-indicator of every issued study, the date of its last
rebuild, and what that rebuild cost in minutes, tokens (millions) and documents staged for
OSINT. `next` names the `PER_NIGHT` rebuilt longest ago, never-rebuilt first, on
`unit-review.py`'s own test of whether a cycle is unattended; it names none rebuilt inside
`MIN_GAP_DAYS`. An indicator joins when its study has an issued `assessment.csv`.

**The rebuild searches** *(Bill, 2026-10-11)*, and stamps `searched`; the yearly line is the backstop. `order` and `next` print a line for any study whose
`study.json` -> `searched` is more than a year old; the runbook says what to do with it.

Exit: 0 done or work printed, 1 nothing owed, 2 a file or an argument is wrong.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import importlib.util
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

ROTATION = os.path.join(study_lib.CORPUS, "logs", "maturity-review.csv")
ROTATION_FIELDS = ["study", "key", "indicator_id", "last_reviewed", "minutes", "tokens", "staged"]
COST_FIELDS = ROTATION_FIELDS[4:]
HISTORY_FIELDS = ["date", "iso3", "indicator_id", "kind", "from", "to", "sources", "note"]
KINDS = ("fact", "review", "ladder")
OUTCOMES = ("nothing", "fact", "reassessed",
            "instrument", "old", "capped")   # closed unread by `study-arrivals.py` (Bill, 2026-10-17)
# Bill, 2026-10-11: the update is not run until every indicator has had its first study, so
# the quota goes on building them. `list`, `order` and `next` name nothing while this is True.
# Lifted 2026-10-17 (Bill): every indicator has its first study.
HELD = False
MIN_GAP_DAYS = 30          # an indicator is not reassessed whole twice inside this
PER_NIGHT = 3              # indicators rebuilt a night (Bill, 2026-10-18)
SEARCH_EVERY_DAYS = 365

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _unit_review():
    spec = importlib.util.spec_from_file_location(
        "unit_review", os.path.join(os.path.dirname(os.path.abspath(__file__)), "unit-review.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def studies(root: str | None = None) -> list[str]:
    """Every study with an issued assessment, by id."""
    root = root or study_lib.CORPUS
    out = []
    for sj in sorted(glob.glob(os.path.join(root, "maturity", "*", "study.json"))):
        sid = os.path.basename(os.path.dirname(sj))
        if os.path.exists(os.path.join(root, "outputs", "maturity", sid, "assessment.csv")):
            out.append(sid)
    return out


def arrivals_path(sid: str, root: str | None = None) -> str:
    return os.path.join(study_lib.study_dir(sid, root), "evidence", "arrivals.csv")


def history_path(sid: str, root: str | None = None) -> str:
    return os.path.join(study_lib.out_dir(sid, root), "history.csv")


def search_due(root: str | None = None, today: dt.date | None = None) -> list[str]:
    today = today or dt.date.today()
    out = []
    for sid in studies(root):
        with open(os.path.join(study_lib.study_dir(sid, root), "study.json"), encoding="utf-8") as fh:
            searched = json.load(fh).get("searched", "")
        try:
            age = (today - dt.date.fromisoformat(searched)).days
        except ValueError:
            out.append(f"standing search: {sid} has no `searched` date in study.json")
            continue
        if age > SEARCH_EVERY_DAYS:
            out.append(f"standing search due: {sid}, last searched {searched}")
    return out


def rotation(root: str | None = None, path: str | None = None) -> list[dict]:
    """The rotation reconciled against the studies issued: a new indicator joins unreviewed."""
    path = path or ROTATION
    held = {(r["study"], r["key"]): r for r in study_lib.read_csv(path)}
    for r in held.values():
        if r.get("last_reviewed"):
            dt.date.fromisoformat(r["last_reviewed"])
    return [{"study": s, "key": sub["key"], "indicator_id": sub["indicator_id"],
             **{f: held.get((s, sub["key"]), {}).get(f, "") for f in ["last_reviewed", *COST_FIELDS]}}
            for s in studies(root) for sub in study_lib.load(s, root)["sub_indicators"]]


def overdue(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda r: (r["last_reviewed"] != "", r["last_reviewed"], r["study"], r["key"]))


def log(sid: str, iso: str, key: str, kind: str, note: str, root: str | None = None,
        today: dt.date | None = None) -> dict:
    """Append one reassessment to the study's history and stamp the cell's as-at. Returns the row."""
    today = (today or dt.date.today()).isoformat()
    study = study_lib.load(sid, root)
    sub = study_lib.subs(study).get(key)
    if sub is None:
        raise ValueError(f"{key} is not a sub-indicator of {sid}")
    was = [r for r in study_lib.read_csv(os.path.join(study_lib.out_dir(sid, root), "assessment.csv"))
           if r["iso3"] == iso and r["indicator_id"] == sub["indicator_id"]]
    if not was:
        raise ValueError(f"{iso} {key}: no row in the published assessment.csv")
    path = os.path.join(study_lib.study_dir(sid, root), "evidence", iso, "stage.json")
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    cell = next((c for c in doc["cells"] if c.get("sub_indicator") == key), None)
    if cell is None:
        raise ValueError(f"{iso} {key}: no cell in stage.json")
    row = {"date": today, "iso3": iso, "indicator_id": sub["indicator_id"], "kind": kind,
           "from": was[0]["stage"], "to": str(cell["stage"]),
           "sources": str(cell.get("stage_sources", "") or ""), "note": " ".join(note.split())}
    cell["as_at"] = today
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    rows = study_lib.read_csv(history_path(sid, root)) + [row]
    study_lib.write_csv(history_path(sid, root), HISTORY_FIELDS, rows)
    return row


def main(argv=None, now: dt.datetime | None = None, root: str | None = None,
         path: str | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("order")
    c = sp.add_parser("close")
    c.add_argument("study"); c.add_argument("iso3"); c.add_argument("slug")
    c.add_argument("--outcome", required=True, choices=OUTCOMES)
    g = sp.add_parser("log")
    g.add_argument("study"); g.add_argument("iso3"); g.add_argument("key")
    g.add_argument("--kind", required=True, choices=KINDS)
    g.add_argument("--note", required=True, help="one line: what called for it and what it found")
    n = sp.add_parser("next")
    n.add_argument("--poll", action="store_true", help="the cycle was started by /poll")
    d = sp.add_parser("done")
    d.add_argument("study"); d.add_argument("key")
    d.add_argument("--minutes", default="", help="wall-clock minutes the rebuild took")
    d.add_argument("--tokens", default="", help="millions of tokens, thread and agents (study-tokens.py --total)")
    d.add_argument("--staged", default="", help="documents staged for OSINT")
    sp.add_parser("list")
    a = ap.parse_args(argv)
    now = now or dt.datetime.now()
    path = path or ROTATION

    if HELD and a.cmd in ("list", "order", "next"):
        print("held: the maturity update waits until every indicator has its first study "
              "(Bill, 2026-10-11)")
        return 1

    if a.cmd == "order":
        due, found = search_due(root, now.date()), 0
        for sid in studies(root):
            for r in study_lib.read_csv(arrivals_path(sid, root)):
                if not r.get("outcome"):
                    print(f"{sid}\t{r['iso3']}\t{r['n']}\t{r['slug']}\tlisted {r['listed']}")
                    found += 1
        for line in due:
            print(line)
        return 0 if found or due else 1

    if a.cmd == "close":
        iso, rows = a.iso3.upper(), study_lib.read_csv(arrivals_path(a.study, root))
        hit = [r for r in rows if r["iso3"] == iso and r["slug"] == a.slug and not r.get("outcome")]
        if not hit:
            print(f"study-update: no open arrival {a.slug} for {a.study} {iso}")
            return 2
        hit[0].update(outcome=a.outcome, closed=now.date().isoformat())
        study_lib.write_csv(arrivals_path(a.study, root), study_lib.ARRIVAL_FIELDS, rows)
        print(f"{a.study} {iso} {a.slug}: {a.outcome}")
        return 0

    if a.cmd == "log":
        try:
            row = log(a.study, a.iso3.upper(), a.key, a.kind, a.note, root, now.date())
        except (ValueError, OSError, study_lib.StudyError) as e:
            print(f"study-update: {e}")
            return 2
        moved = "unchanged" if row["from"] == row["to"] else f"{row['from']} -> {row['to']}"
        print(f"{a.study} {row['iso3']} {a.key}: {row['kind']}, {moved}; as-at {row['date']}")
        return 0

    try:
        rows = rotation(root, path)
    except (ValueError, KeyError, study_lib.StudyError) as e:
        print(f"study-update: {path}: {e}")
        return 2

    if a.cmd == "next":
        if not _unit_review().owed_now(a.poll, now):
            print(f"not owed: {now:%H:%M} is outside the night hours and the cycle is not from /poll")
            return 1
        if not rows:
            print("not owed: no study has an issued assessment")
            return 1
        owed = [r for r in overdue(rows) if not r["last_reviewed"] or
                (now.date() - dt.date.fromisoformat(r["last_reviewed"])).days >= MIN_GAP_DAYS][:PER_NIGHT]
        if not owed:
            print(f"not owed: every indicator was rebuilt inside {MIN_GAP_DAYS} days")
            return 1
        for r in owed:
            print(f"{r['study']}\t{r['key']}\t{r['indicator_id']}\t"
                  f"last rebuilt {r['last_reviewed'] or 'never'}")
        for line in search_due(root, now.date()):
            print(line)
        return 0

    if a.cmd == "done":
        hit = [r for r in rows if r["study"] == a.study and r["key"] == a.key]
        if not hit:
            print(f"study-update: {a.study} {a.key} is not in the control list")
            return 2
        hit[0].update(last_reviewed=now.date().isoformat(), **{f: getattr(a, f) for f in COST_FIELDS})
        study_lib.write_csv(path, ROTATION_FIELDS, rows)
        print(f"{a.study} {a.key} rebuilt {hit[0]['last_reviewed']}")
        return 0

    study_lib.write_csv(path, ROTATION_FIELDS, rows)
    for r in overdue(rows):
        cost = ", ".join(f"{f} {r[f]}" for f in COST_FIELDS if r[f])
        print(f"{r['study']}  {r['key']}  {r['last_reviewed'] or 'never'}  {r['indicator_id']}"
              + (f"  ({cost})" if cost else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
