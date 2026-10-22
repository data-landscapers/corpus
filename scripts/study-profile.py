#!/usr/bin/env python3
r"""study-profile.py — each country's profile from its evidence, and the draw for the agreement check.

    python scripts/study-profile.py health                    # every profile.csv
    python scripts/study-profile.py health --merge            # facts/*.json not yet taken, then
                                                              # only the countries they reached
    python scripts/study-profile.py health --as-at 2026-09-30
    python scripts/study-profile.py health --draw 20           # method §7 step 4: the cells
    python scripts/study-profile.py health --score             # ...and the count that agree

`maturity/documentation/maturity-study-method.md` §4, §5 and §7. A drafter writes
`evidence.csv`, one row per stated fact; **what the facts add up to is arithmetic, so a script
does it**, and does it the same way for 54 countries.

`maturity/{id}/evidence/{ISO3}/profile.csv` holds one row per sub-indicator and aspect:

- `value`   — the newest fact's. Where the aspect has facets, the newest per facet; where it
  is `multi`, every value stated inside the window; where it names a `prefer` order (a share
  over a count over *not published*), the best-ranked kind first and the newest of that.
  A value the aspect lists under `defer` stands only where nothing else is stated: a source
  saying registers are still kept on paper does not unsay a newer system another describes,
  and *no tier* does not sit beside a tier.
- `sources` — the `row_id`s that carry that value.
- `others`  — the rows that say something else. The newest stands and both are kept.
A source the study excludes (`exclude_sources` in `study.json`) gives a profile nothing: its
rows stay in `evidence.csv`, where the ruling can be reversed, and are passed over here.

- `gap`     — what is not established: nothing held, or nothing dated inside the window. A
  coverage aspect's window is three years; a qualifier's is its own. **A gap is what Phase 1
  searches for**, so this column is the search list.

An invalid `evidence.csv` is reported and its country is not profiled: a profile built over
a value outside the closed list would carry it into a stage.

**The agreement check draws from the staged cells only.** `--draw N` writes
`maturity/{id}/agreement.csv` with an empty `second_stage` for the second drafter, who stages
blind from `evidence.csv`; `--score` counts the cells where the two agree and exits 1 below
the method's 16 in 20, pro rata for another N.

Exit: 0 clean, 1 invalid evidence or agreement below the bar, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

AGREEMENT_FIELDS = ["iso3", "indicator_id", "second_stage"]
AGREE_BAR = 0.8    # 16 of 20
MERGED_FIELDS = ["iso3", "source_slug", "read", "merged_on"]


def merge(study: dict, iso: str, readlist: list[dict], files: dict[str, dict],
          existing: list[dict], fixes: list[dict] | None = None,
          merged: dict[str, str] | None = None) -> tuple[list[dict], list[dict], list[str], dict[str, str]]:
    """`(new evidence rows, systems rows, problems, documents taken)` from one country's facts files.

    A drafter writes one JSON file per document read, named for the document's `n` in the
    reading list: `{"slug", "facts": [...], "systems": [...]}`. **The slug and the URL of a
    row come from the reading list, never from the drafter**, so a fact cannot be filed
    under a source the list did not hand out. A fact is kept only for the sub-indicator's
    own class; what a document says of a tracker or a stock system is a `systems` row.

    Row ids continue from the highest already in `evidence.csv`, so a second merge - the
    Phase 2 re-read - leaves every cited id standing. A document already merged is skipped,
    **except one listed a second time as `completed`**: an excerpt since held whole is read
    again, and of what that reading states only the facts not already held for the document
    are added.

    **A correction outlives the row it removed.** The ladder deletes a row `corrections.csv`
    removes, so the slug that marked its document merged can go with it. `fixes` is the
    country's corrections: ids continue past every id one names, so no new row takes a
    corrected id; and a document not yet held is skipped, and named, where it states what a
    removed row stated, the same aspect and value.

    **A document is taken once, and a `completed` re-read once more.** `merged` is what
    `merged.csv` records as taken, slug to `read` (`completed` for the re-read). A recorded
    slug is skipped like one `evidence.csv` still cites, so a document whose every row a later
    check removed is not brought back, whether or not its correction names the aspect.
    Systems rows come only from the documents taken now, so a row an earlier run pruned stays
    pruned. The fourth value is the slugs taken now and their `read`, for `merged.csv`."""
    listed = {str(r["n"]): r for r in readlist if r.get("kind") == "raw"}
    held = {(r["source_slug"], r["sub_indicator"], r["aspect"], r["value"], r["as_of"])
            for r in existing}
    # `also_assessed` names further classes a sub-indicator stages (the censuses study's surveys).
    sub_class = {s["key"]: [s["class"], *s.get("also_assessed", [])] for s in study["sub_indicators"]}
    merged = merged or {}
    done = {r["source_slug"] for r in existing} | set(merged)
    named = [f.get("row_id") or f"{f.get('iso3', '')}-{f.get('n', '')}" for f in fixes or []]
    held_ids = {r["row_id"] for r in existing}
    gone = {(f.get("aspect", ""), f.get("value", "")) for f, rid in zip(fixes or [], named)
            if f.get("action") in ("removed", "withdrawn") and rid not in held_ids and f.get("aspect")}
    ids = [r["row_id"] for r in existing] + [i for i in named if i.startswith(f"{iso}-")]
    nxt = max([int(i.split("-")[1]) for i in ids if i.split("-")[1].isdigit()] or [0]) + 1
    rows, systems, problems, taken = [], [], [], {}
    for n in sorted(files, key=lambda k: int(k) if k.isdigit() else 0):
        doc, src = files[n], listed.get(n)
        if src is None:
            problems.append(f"{iso} facts/{n}.json: the reading list has no document {n}")
            continue
        if doc.get("slug") != src["slug"]:
            problems.append(f"{iso} facts/{n}.json: says `{doc.get('slug')}`, the list's "
                            f"document {n} is `{src['slug']}`")
            continue
        read = "completed" if src.get("why") == "completed" else ""
        if src["slug"] in done and (not read or merged.get(src["slug"]) == read):
            continue
        if src["slug"] not in done and any((str(f.get("aspect", "")).strip(), str(f.get("value", "")).strip())
                                           in gone for f in doc.get("facts") or []):
            problems.append(f"{iso} facts/{n}.json: skipped, it states what a removed row stated")
            continue
        taken[src["slug"]] = read
        for s in doc.get("systems") or []:
            systems.append({"iso3": iso, **{k: str(s.get(k, "") or "").strip()
                                           for k in study_lib.SYSTEMS_FIELDS[1:-1]},
                            "sources": src["slug"]})
        for f in doc.get("facts") or []:
            sub = f.get("sub_indicator", "")
            if sub in sub_class and f.get("class") not in sub_class[sub]:
                problems.append(f"{iso} facts/{n}.json: a {sub} fact classed `{f.get('class')}`; "
                                f"only `{'`, `'.join(sub_class[sub])}` systems are assessed there")
                continue
            key = (src["slug"], *(str(f.get(k, "") or "").strip()
                                  for k in ("sub_indicator", "aspect", "value", "as_of")))
            if key in held:
                continue
            held.add(key)
            rows.append({"row_id": f"{iso}-{nxt:03d}", "iso3": iso, "source_slug": src["slug"],
                         "url": src["url"],
                         **{k: str(f.get(k, "") or "").strip()
                            for k in ("sub_indicator", "aspect", "value", "fact", "as_of",
                                      "date_precision", "system", "class")}})
            nxt += 1
    unread = sorted(int(n) for n in listed if n not in files)
    if unread:
        problems.append(f"{iso}: no facts file for document(s) {unread} of the reading list")
    return rows, systems, problems, taken


def _rank(aspect: dict, value: str) -> int:
    late = 100 if value in aspect.get("defer", ()) else 0
    for i, prefix in enumerate(aspect.get("prefer", ())):
        if value.startswith(prefix):
            return late + i
    return late + len(aspect.get("prefer", ()))


def profile_cell(aspect: dict, rows: list[dict], as_at: dt.date) -> dict:
    """One aspect of one sub-indicator, from its evidence rows."""
    window = aspect.get("window_months", study_lib.COVERAGE_WINDOW_MONTHS)
    cutoff = study_lib.months_back(as_at, window)
    dated = sorted(((study_lib.parse_as_of(r["as_of"]), r) for r in rows),
                   key=lambda p: p[0], reverse=True)
    if not dated:
        return {"value": "", "as_of": "", "sources": "", "others": "", "gap": "nothing held"}
    inside = [p for p in dated if p[0] >= cutoff]
    gap = "" if inside else f"nothing dated since {cutoff.isoformat()}"

    if "facets" in aspect:
        chosen = {}
        for _, r in dated:
            for part in r["value"].split(";"):
                chosen.setdefault(part.split(":")[0].strip(), (part.strip(), r))
        picked = [chosen[f] for f in aspect["facets"] if f in chosen]
        missing = [f for f in aspect["facets"] if f not in chosen]
        if missing and not gap:
            gap = "not stated: " + ", ".join(missing)
        value = ";".join(v for v, _ in picked)
        winners = {r["row_id"] for _, r in picked}
    elif aspect.get("multi"):
        pool = inside or dated[:1]
        seen = []
        for _, r in pool:
            seen += [v.strip() for v in r["value"].split(";") if v.strip() not in seen]
        stated = [v for v in seen if v not in aspect.get("defer", ())] or seen
        order = aspect["values"] if isinstance(aspect.get("values"), list) else stated
        value = ";".join(sorted(stated, key=lambda v: order.index(v) if v in order else 99))
        winners = {r["row_id"] for _, r in pool if set(r["value"].split(";")) & set(stated)}
    else:
        best = min(dated, key=lambda p: (_rank(aspect, p[1]["value"]), -p[0].toordinal()))[1]
        value = best["value"]
        winners = {r["row_id"] for _, r in dated if r["value"] == value}
        picked = [(value, best)]

    newest = max(d for d, r in dated if r["row_id"] in winners)
    as_of = next(r["as_of"] for d, r in dated if r["row_id"] in winners and d == newest)
    others = [f"{r['row_id']}={r['value']}" for _, r in dated if r["row_id"] not in winners]
    return {"value": value, "as_of": as_of, "sources": ";".join(sorted(winners)),
            "others": ";".join(others), "gap": gap}


def profile(study: dict, iso: str, rows: list[dict], as_at: dt.date) -> list[dict]:
    out, barred = [], study_lib.excluded(study)
    rows = [r for r in rows if r["source_slug"] not in barred]
    for sub in study["sub_indicators"]:
        for aspect in study["aspects"]:
            mine = [r for r in rows
                    if r["sub_indicator"] == sub["key"] and r["aspect"] == aspect["key"]]
            cell = profile_cell(aspect, mine, as_at)
            out.append({"iso3": iso, "sub_indicator": sub["key"], "aspect": aspect["key"],
                        "role": aspect["role"], **cell})
    return out


def draw(cells: list[tuple[str, str]], n: int, seed: int) -> list[tuple[str, str]]:
    """`n` cells, or all of them where fewer are staged. Seeded, so the draw can be shown."""
    cells = sorted(cells)
    return sorted(random.Random(seed).sample(cells, min(n, len(cells))))


def write_changed(path: str, fields: list[str], rows: list[dict]) -> bool:
    """Write a CSV only where its rows differ from the file's, so a country nothing touched
    keeps its bytes. True if written."""
    want = [{k: "" if r.get(k) is None else str(r[k]) for k in fields} for r in rows]
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig", newline="") as fh:
            head = fh.readline()
        if head.strip().split(",") == fields and study_lib.read_csv(path) == want:
            return False
    study_lib.write_csv(path, fields, rows)
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Profiles from evidence; the agreement draw.")
    ap.add_argument("study")
    ap.add_argument("--as-at", help="YYYY-MM-DD; default today")
    ap.add_argument("--merge", action="store_true",
                    help="first fold each country's facts/*.json into its evidence.csv")
    ap.add_argument("--draw", type=int, metavar="N", help="draw N staged cells for a second drafter")
    ap.add_argument("--seed", type=int, help="the draw's seed; default the as-at's ordinal")
    ap.add_argument("--score", action="store_true", help="count agreement in agreement.csv")
    a = ap.parse_args(argv)

    try:
        study = study_lib.load(a.study)
    except study_lib.StudyError as e:
        print(f"study-profile: {e}")
        return 2
    as_at = dt.date.fromisoformat(a.as_at) if a.as_at else dt.date.today()
    agreement = os.path.join(study_lib.study_dir(a.study), "agreement.csv")
    assessment = study_lib.read_csv(os.path.join(study_lib.out_dir(a.study), "assessment.csv"))

    if a.draw:
        staged = [(r["iso3"], r["indicator_id"]) for r in assessment if r["stage"].isdigit()]
        if not staged:
            print("study-profile: assessment.csv holds no staged cell to draw from.")
            return 2
        seed = a.seed if a.seed is not None else as_at.toordinal()
        picked = draw(staged, a.draw, seed)
        study_lib.write_csv(agreement, AGREEMENT_FIELDS,
                            [{"iso3": i, "indicator_id": c, "second_stage": ""} for i, c in picked])
        print(f"study-profile: drew {len(picked)} of {len(staged)} staged cells, seed {seed}, "
              f"to {os.path.relpath(agreement, study_lib.CORPUS)}.")
        return 0

    if a.score:
        first = {(r["iso3"], r["indicator_id"]): r["stage"] for r in assessment}
        rows = study_lib.read_csv(agreement)
        blank = [r for r in rows if not r["second_stage"].strip()]
        if not rows or blank:
            print(f"study-profile: agreement.csv has {len(blank)} of {len(rows)} cells unstaged.")
            return 2
        split = [r for r in rows if first.get((r["iso3"], r["indicator_id"])) != r["second_stage"].strip()]
        for r in split:
            print(f"  {r['iso3']} {r['indicator_id']}: first "
                  f"{first.get((r['iso3'], r['indicator_id']))}, second {r['second_stage']}")
        agree = len(rows) - len(split)
        ok = agree >= AGREE_BAR * len(rows)
        print(f"study-profile: {agree} of {len(rows)} cells agree - "
              + ("the ladder holds." if ok else "below the bar: rewrite the rung that split "
                                                "them and restage every country."))
        return 0 if ok else 1

    bad = 0
    base = os.path.join(study_lib.study_dir(a.study), "evidence")
    touched = None      # under --merge, the countries a newly taken document reached
    if a.merge:
        touched = set()
        wpath = os.path.join(study_lib.study_dir(a.study), "withdrawn.csv")
        withdrawn = ({(r["iso3"], r["source_slug"]) for r in study_lib.read_csv(wpath)}
                     if os.path.exists(wpath) else set())
        fixes = study_lib.read_csv(os.path.join(study_lib.study_dir(a.study), "corrections.csv"))
        mpath = os.path.join(study_lib.study_dir(a.study), "merged.csv")
        ledger = study_lib.read_csv(mpath)
        for iso in sorted(os.listdir(base)):
            facts_dir = os.path.join(base, iso, "facts")
            if not os.path.isdir(facts_dir):
                continue
            files, problems = {}, []
            for name in sorted(os.listdir(facts_dir)):
                if not name.endswith(".json"):
                    continue
                try:
                    with open(os.path.join(facts_dir, name), encoding="utf-8") as fh:
                        files[name[:-5].lstrip("0") or "0"] = json.load(fh)
                except (OSError, ValueError) as e:
                    problems.append(f"{iso} facts/{name}: not readable JSON ({e})")
            existing = study_lib.read_csv(os.path.join(base, iso, "evidence.csv"))
            before = {r["source_slug"]: r.get("read", "") for r in ledger if r["iso3"] == iso}
            new, systems, more, taken = merge(study, iso, study_lib.read_csv(
                os.path.join(base, iso, "readlist.csv")), files, existing,
                [f for f in fixes if f.get("iso3") == iso or f.get("row_id", "").startswith(f"{iso}-")],
                before)
            # Withdrawn before `merged.csv` existed: the hand-kept form of the same record.
            new = [r for r in new if (iso, r["source_slug"]) not in withdrawn]
            for p in problems + more:
                print(f"study-profile: note - {p}")
            if new:
                study_lib.write_csv(os.path.join(base, iso, "evidence.csv"),
                                    study_lib.EVIDENCE_FIELDS, existing + new)
            spath = os.path.join(base, iso, "systems.csv")
            held = study_lib.read_csv(spath)
            seen = {tuple(r.get(k, "") for k in study_lib.SYSTEMS_FIELDS) for r in held}
            add = [s for s in systems if tuple(s[k] for k in study_lib.SYSTEMS_FIELDS) not in seen]
            if add:
                write_changed(spath, study_lib.SYSTEMS_FIELDS, held + add)
            today = dt.date.today().isoformat()
            ledger = [r for r in ledger if (r["iso3"], r["source_slug"]) not in {(iso, s) for s in taken}]
            ledger += [{"iso3": iso, "source_slug": s, "read": read, "merged_on": today}
                       for s, read in taken.items()]
            if new or add:
                touched.add(iso)
                print(f"  {iso}  {len(new):3d} new facts, {len(add):3d} new systems")
        write_changed(mpath, MERGED_FIELDS, sorted(ledger, key=lambda r: (r["iso3"], r["source_slug"])))
        print(f"study-profile: merged into {len(touched)} countr{'y' if len(touched) == 1 else 'ies'}"
              + (f": {' '.join(sorted(touched))}" if touched else "; nothing new to profile."))
    for iso, rows in study_lib.evidence(a.study).items():
        if touched is not None and iso not in touched:
            continue
        problems = study_lib.evidence_problems(study, iso, rows)
        if problems:
            bad += 1
            for p in problems:
                print(f"study-profile: FAIL - {p}")
            continue
        out = profile(study, iso, rows, as_at)
        write_changed(os.path.join(base, iso, "profile.csv"), study_lib.PROFILE_FIELDS, out)
        print(f"  {iso}  {len(rows):3d} facts  {sum(1 for r in out if r['gap']):2d} gaps")
    print(f"study-profile: {a.study} as at {as_at.isoformat()} - "
          + (f"{bad} country file(s) invalid and not profiled." if bad else "profiles written."))
    return 1 if bad else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
