#!/usr/bin/env python3
r"""study-calls.py — a maturity study's drafter calls, a regional story read once.

    python scripts/study-calls.py datacentres          # writes maturity/{id}/calls.json
    python scripts/study-calls.py datacentres --dry    # the counts, nothing written
    python scripts/study-calls.py datacentres --fan    # regional answers into facts files

`maturity/documentation/maturity-study-method.md` §4. `study-select.py` lists a regional
story in every country whose name it carries, so a story naming twenty countries was read
by twenty drafters: in the data centres study, 874 of 2,239 readings, and 732 of those 874
gave nothing *(Bill, 2026-10-14)*. **A story read whole and listed for two countries or more
is now one call**: one drafter reads it once and answers for every country listed. A long
regional document is cut per country around the country's name (`study-select.py` →
`shorten`), so its passages differ by country and stay in that country's calls.

`calls.json` is the fan-out's input, one entry per call, the parent passing it to the
workflow as it stands:

- `{"kind": "country", "iso": "KEN", "ns": [1, 2, 3]}` — the rows of one country's list,
  at most `CALL_DOCS`, never across two passes, as `slice` grouped them;
- `{"kind": "regional", "stories": [{"key": "…", "slug": "…", "path": "…",
  "countries": {"KEN": 14, …}}, …]}` — regional stories within the same bounds, each with
  its number in each country's list.

Only rows of pass `0` and `about` are planned (`about` alone for a study whose `pass` is `first`), and a row whose facts file already exists is
not: a carry or an earlier call has answered it. A regional drafter writes one file per story,
`maturity/{id}/regional/{key}.json`, `{"slug", "countries": {ISO3: {"facts", "systems",
"note"}}}`; **`--fan` writes each country's part as `evidence/{ISO3}/facts/{n}.json`**, the
shape a country drafter writes, so `study-profile.py --merge` takes both alike. A country the
drafter left out gets an empty file saying so, and a file already there is left alone.

**A batch shares its reading across studies** *(Bill, 2026-10-16)*. `--batch a b c` plans the
studies of a first-pass batch together: a story read whole and listed by two studies or more is
one `shared` call in `maturity/_batch/calls.json`, whose drafter reads it once and answers each
study's questions for each country listed, into `maturity/_batch/shared/{key}.json`,
`{"slug", "studies": {id: {"countries": {ISO3: {"facts", "systems", "note"}}}}}`. Everything
else is planned per study as above and written to that study's own `calls.json`, so each
study's regional `--fan` is unchanged. `--batch a b c --fan` writes the shared answers into
each study's facts files, the shape a country drafter writes.

    python scripts/study-calls.py --batch ailaw aistrategy          # plan the batch
    python scripts/study-calls.py --batch ailaw aistrategy --fan    # shared answers -> facts files

Exit: 0 written, 1 `--fan` found a regional file it could not read, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

PASSES = ("0", "about")
FIRST = ("about",)   # a first pass reads the `about` rows only (`first-pass-batch.md`, 2026-10-16)


def passes_of(study: dict) -> tuple[str, ...]:
    return FIRST if study.get("pass") == "first" else PASSES


def since_of(study: dict) -> str:
    """`window_from`: a story published before it can give no fact the ladder counts, so it is
    not planned. The Digital Identity batch (2026-10-16) set it to the three-year window's start."""
    return study.get("window_from", "")
CALL_DOCS, CALL_WORDS = 5, 15_000   # as `study-select.py` bounds a call


def plan(lists: dict[str, list[dict]], answered: set[tuple[str, str]], passes=PASSES, since: str = "") -> list[dict]:
    """The calls for `{iso: readlist rows}`, less the `(iso, n)` already answered."""
    todo = {iso: [r for r in rows if r.get("kind") == "raw" and r.get("pass") in passes
                  and (r.get("published") or "9999") >= since
                  and r.get("slice") and (iso, str(r["n"])) not in answered]
            for iso, rows in lists.items()}
    where = collections.defaultdict(dict)
    for iso, rows in todo.items():
        for r in rows:
            if r.get("read") == "whole":
                where[r["slug"]][iso] = r
    shared = {slug for slug, isos in where.items() if len(isos) >= 2}
    calls, batch, words = [], [], 0
    for slug in sorted(shared):
        first = next(iter(where[slug].values()))
        size = int(first.get("words") or 0)
        if batch and (len(batch) >= CALL_DOCS or words + size > CALL_WORDS):
            calls.append({"kind": "regional", "stories": batch})
            batch, words = [], 0
        batch.append({"key": hashlib.sha1(slug.encode("utf-8")).hexdigest()[:10],
                      "slug": slug, "path": first["path"],
                      "countries": {iso: int(r["n"]) for iso, r in sorted(where[slug].items())}})
        words += size
    if batch:
        calls.append({"kind": "regional", "stories": batch})
    for iso in sorted(todo):
        by_slice = collections.defaultdict(list)
        for r in todo[iso]:
            if not (r.get("read") == "whole" and r["slug"] in shared):
                by_slice[(r["pass"], r["slice"])].append(int(r["n"]))
        for k in sorted(by_slice, key=lambda k: (k[0], int(k[1]) if k[1].isdigit() else 0)):
            calls.append({"kind": "country", "iso": iso, "ns": sorted(by_slice[k])})
    return calls


def fan(answer: dict, call: dict) -> dict[str, dict]:
    """`{iso: facts file}` from one regional drafter's answer, every listed country included."""
    parts = answer.get("countries") or {}
    out = {}
    for iso in call["countries"]:
        part = parts.get(iso) if isinstance(parts.get(iso), dict) else None
        if part is None:
            part = {"facts": [], "systems": [], "note": "the regional reading gave nothing for this country"}
        out[iso] = {"slug": call["slug"],
                    "facts": [f for f in part.get("facts") or [] if isinstance(f, dict)],
                    "systems": [s for s in part.get("systems") or [] if isinstance(s, dict)],
                    "note": str(part.get("note", "") or "")}
    return out


BATCH = os.path.join(study_lib.CORPUS, "maturity", "_batch")


def todo_and_answered(study: str) -> tuple[dict[str, list[dict]], set[tuple[str, str]]]:
    """`({iso: readlist rows}, {(iso, n) already answered})` for one study."""
    base = os.path.join(study_lib.study_dir(study), "evidence")
    lists, answered = {}, set()
    for iso in sorted(study_lib.countries()):
        lists[iso] = study_lib.read_csv(os.path.join(base, iso, "readlist.csv"))
        folder = os.path.join(base, iso, "facts")
        if os.path.isdir(folder):
            answered |= {(iso, f[:-5]) for f in os.listdir(folder) if f.endswith(".json")}
    return lists, answered


def capped(lists: dict[str, dict[str, list[dict]]], reads: dict, since: dict, cap: int) -> None:
    """Keep each country's `cap` best-ranked stories across the batch, in place.

    *(Digital Identity batch, 2026-10-16: 2,421 stories would have been about 500 calls.)* A
    story's rank in a country is its best `n` in any study's list, which `study-select.py`
    ranked; the rest of the rows are dropped from the plan, not from the lists."""
    best: dict[str, dict[str, int]] = collections.defaultdict(dict)
    for sid, by_iso in lists.items():
        for iso, rows in by_iso.items():
            for r in rows:
                if r.get("kind") == "raw" and r.get("pass") in reads[sid] and (r.get("published") or "9999") >= since[sid]:
                    best[iso][r["slug"]] = min(best[iso].get(r["slug"], 10**6), int(r["n"]))
    keep = {iso: set(sorted(d, key=d.get)[:cap]) for iso, d in best.items()}
    for by_iso in lists.values():
        for iso, rows in by_iso.items():
            by_iso[iso] = [r for r in rows if r.get("kind") != "raw" or r["slug"] in keep.get(iso, ())]


def plan_batch(studies: list[str], cap: int = 0) -> tuple[list[dict], dict[str, list[dict]]]:
    """`(shared calls, {study: its own calls})` for a batch.

    A row is shared when its story is read whole and listed by two studies or more; each such
    row is taken out of its study's own plan by marking it answered for the planning only."""
    lists, answered, reads, since = {}, {}, {}, {}
    where = collections.defaultdict(lambda: collections.defaultdict(dict))
    for sid in studies:
        lists[sid], answered[sid] = todo_and_answered(sid)
        reads[sid] = passes_of(study_lib.load(sid))
        since[sid] = since_of(study_lib.load(sid))
    if cap:
        capped(lists, reads, since, cap)
    for sid in studies:
        for iso, rows in lists[sid].items():
            for r in rows:
                if (r.get("kind") == "raw" and r.get("pass") in reads[sid] and r.get("slice")
                        and (r.get("published") or "9999") >= since[sid]
                        and r.get("read") == "whole" and (iso, str(r["n"])) not in answered[sid]):
                    where[r["slug"]][sid][iso] = r
    shared = {slug for slug, by in where.items() if len(by) >= 2}
    calls, batch, words = [], [], 0
    for slug in sorted(shared):
        first = next(iter(next(iter(where[slug].values())).values()))
        size = int(first.get("words") or 0)
        if batch and (len(batch) >= CALL_DOCS or words + size > CALL_WORDS):
            calls.append({"kind": "shared", "stories": batch})
            batch, words = [], 0
        batch.append({"key": hashlib.sha1(slug.encode("utf-8")).hexdigest()[:10],
                      "slug": slug, "path": first["path"],
                      "studies": {sid: {iso: int(r["n"]) for iso, r in sorted(isos.items())}
                                  for sid, isos in sorted(where[slug].items())}})
        words += size
    if batch:
        calls.append({"kind": "shared", "stories": batch})
    own = {}
    for sid in studies:
        taken = {(iso, str(r["n"])) for slug in shared for iso, r in where[slug].get(sid, {}).items()}
        own[sid] = plan(lists[sid], answered[sid] | taken, reads[sid], since[sid])
    return calls, own


def write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")


def fan_batch(studies: list[str], dry: bool) -> int:
    try:
        with open(os.path.join(BATCH, "calls.json"), encoding="utf-8") as fh:
            stories = [st for c in json.load(fh) for st in c["stories"]]
    except OSError:
        print("study-calls: no maturity/_batch/calls.json; plan the batch first")
        return 2
    written, missing = 0, []
    for st in stories:
        try:
            with open(os.path.join(BATCH, "shared", st["key"] + ".json"), encoding="utf-8") as fh:
                answer = json.load(fh)
        except (OSError, ValueError):
            missing.append(st["key"])
            continue
        for sid, isos in st["studies"].items():
            if sid not in studies:
                continue
            part = (answer.get("studies") or {}).get(sid) or {}
            view = {"slug": st["slug"], "countries": isos}
            for iso, doc in fan({"countries": part.get("countries") or {}}, view).items():
                out = os.path.join(study_lib.study_dir(sid), "evidence", iso, "facts", f"{isos[iso]}.json")
                if os.path.exists(out) or dry:
                    continue
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with open(out, "w", encoding="utf-8", newline="\n") as fh:
                    json.dump(doc, fh, ensure_ascii=False, indent=1)
                    fh.write("\n")
                written += 1
    print(f"study-calls: {len(stories) - len(missing)} shared answers fanned into {written} facts files"
          + (f"; unreadable or missing: {', '.join(missing)}" if missing else "") + ".")
    return 1 if missing else 0


def main_batch(studies: list[str], dry: bool, do_fan: bool, cap: int = 0) -> int:
    for sid in studies:
        try:
            study_lib.load(sid)
        except study_lib.StudyError as e:
            print(f"study-calls: {e}")
            return 2
    if do_fan:
        return fan_batch(studies, dry)
    shared, own = plan_batch(studies, cap)
    if not dry:
        write_json(os.path.join(BATCH, "calls.json"), shared)
        os.makedirs(os.path.join(BATCH, "shared"), exist_ok=True)
        for sid, calls in own.items():
            write_json(os.path.join(study_lib.study_dir(sid), "calls.json"), calls)
    stories = [st for c in shared for st in c["stories"]]
    saved = sum(sum(len(i) for i in st["studies"].values()) for st in stories) - len(stories)
    print(f"study-calls: batch of {len(studies)} - {len(shared)} shared calls over {len(stories)} stories "
          f"(saving {saved} readings); "
          + ", ".join(f"{sid} {len(c)}" for sid, c in own.items()) + " own calls"
          + (" (dry run, nothing written)." if dry else "."))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Plan a maturity study's drafter calls.")
    ap.add_argument("study", nargs="?")
    ap.add_argument("--batch", nargs="+", metavar="STUDY",
                    help="plan (or with --fan, fan out) a first-pass batch of studies together")
    ap.add_argument("--cap", type=int, default=0, help="with --batch: plan each country's best N stories only")
    ap.add_argument("--dry", action="store_true", help="print the counts, write nothing")
    ap.add_argument("--fan", action="store_true", help="write the regional answers into facts files")
    a = ap.parse_args(argv)
    if a.batch:
        return main_batch(a.batch, a.dry, a.fan, a.cap)
    if not a.study:
        ap.error("name a study, or --batch and the studies")
    try:
        study_lib.load(a.study)
    except study_lib.StudyError as e:
        print(f"study-calls: {e}")
        return 2
    sdir = study_lib.study_dir(a.study)
    base = os.path.join(sdir, "evidence")
    calls_path = os.path.join(sdir, "calls.json")
    if a.fan:
        try:
            with open(calls_path, encoding="utf-8") as fh:
                calls = [st for c in json.load(fh) if c["kind"] == "regional" for st in c["stories"]]
        except OSError:
            print(f"study-calls: no {calls_path}; plan the calls first")
            return 2
        written, missing = 0, []
        for c in calls:
            try:
                with open(os.path.join(sdir, "regional", c["key"] + ".json"), encoding="utf-8") as fh:
                    answer = json.load(fh)
            except (OSError, ValueError):
                missing.append(c["key"])
                continue
            for iso, doc in fan(answer, c).items():
                out = os.path.join(base, iso, "facts", f"{c['countries'][iso]}.json")
                if os.path.exists(out) or a.dry:
                    continue
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with open(out, "w", encoding="utf-8", newline="\n") as fh:
                    json.dump(doc, fh, ensure_ascii=False, indent=1)
                    fh.write("\n")
                written += 1
        print(f"study-calls: {len(calls) - len(missing)} regional answers fanned into {written} facts files"
              + (f"; unreadable or missing: {', '.join(missing)}" if missing else "") + ".")
        return 1 if missing else 0
    lists, answered = {}, set()
    for iso in sorted(study_lib.countries()):
        lists[iso] = study_lib.read_csv(os.path.join(base, iso, "readlist.csv"))
        folder = os.path.join(base, iso, "facts")
        if os.path.isdir(folder):
            answered |= {(iso, f[:-5]) for f in os.listdir(folder) if f.endswith(".json")}
    study = study_lib.load(a.study)
    calls = plan(lists, answered, passes_of(study), since_of(study))
    regional = [st for c in calls if c["kind"] == "regional" for st in c["stories"]]
    readings = sum(len(c["countries"]) for c in regional) + sum(len(c["ns"]) for c in calls if c["kind"] == "country")
    reads = len(regional) + sum(len(c["ns"]) for c in calls if c["kind"] == "country")
    if not a.dry:
        with open(calls_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(calls, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
    print(f"study-calls: {a.study} - {len(calls)} calls, {sum(c['kind'] == 'regional' for c in calls)} of them regional; "
          f"{readings} readings in {reads} reads" + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
