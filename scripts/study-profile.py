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

- `gap`     — what is not established: nothing found, or nothing dated inside the window. A
  coverage aspect's window is three years; a qualifier's is its own. **A gap is what Phase 1
  searches for**, so this column is the search list.

**A fact `--merge` refuses is written down.** A fact repeating a row `corrections.csv` removed -
the same aspect and value from the same source, or about the same system - is not taken, and
`maturity/{id}/refused.csv` records it: the fact's document, sub-indicator, aspect, value, date
and system, the removed row it repeats and the `rule` that matched (`source`, `system`, or
`unrecovered` where the removed row is in no facts file and aspect and value alone decide). Every
`--merge` reads the file back and tests each refusal again, so one a correction no longer
supports is taken. `ruled: {why}` marks one refused by hand, which stands; `held: {why}` one
kept back because taking it moves a stage, which waits for `MATURITY-UPDATE.md` Level 2: the
run that reassesses the cell sets its rule to `release`, and the next `--merge` takes it.

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


REFUSED_FIELDS = ["iso3", "n", "source_slug", "sub_indicator", "aspect", "value", "as_of", "system",
                  "removed", "rule", "refused_on"]


def _norm(s) -> str:
    return " ".join(str(s or "").split()).casefold()


def removed_rows(iso: str, fixes: list[dict], existing: list[dict], listed: dict[str, dict],
                 files: dict[str, dict], done: set[str], refused: set[tuple] = frozenset()) -> list[dict]:
    """The rows `corrections.csv` removed, found again in the facts files they were merged from.

    A correction names a row by id, aspect and value, not by source or system, and the ladder has
    deleted the row. **Ids are issued a document at a time, in reading-list order**, so the row
    came from the document of the nearest row still standing either side of its id; failing
    that, from one between them in the list with no row standing (past the last row, one at or
    below the last document taken). Its fact is one there stating that aspect and value that
    `evidence.csv` no longer holds and no earlier run refused (`refused`, keyed as `merge` keys
    it): a refused fact was never a row. Each such fact is a candidate, `{row_id, source_slug,
    sub_indicator, aspect, value, system}`. A correction no fact answers gives one with
    `source_slug` empty, which `refusal` matches as the old rule did, on aspect and value alone."""
    held_ids = {r["row_id"] for r in existing}
    held_text = {(r["source_slug"], _norm(r["fact"])) for r in existing}
    with_rows = {r["source_slug"] for r in existing}
    n_of = {src["slug"]: int(n) for n, src in listed.items() if n.isdigit()}

    def num(rid: str) -> int | None:
        tail = rid.split("-")[1] if "-" in rid else ""
        return int(tail) if tail.isdigit() else None
    standing = sorted((num(r["row_id"]), r["source_slug"], _norm(r["fact"])) for r in existing
                      if num(r["row_id"]) is not None)
    cap = max([n_of[s] for s in done if s in n_of] or [0]) or None
    out = []
    for f in fixes:
        rid = f.get("row_id") or f"{f.get('iso3', '')}-{f.get('n', '')}"
        if f.get("action") not in ("removed", "withdrawn") or rid in held_ids or not f.get("aspect"):
            continue
        aspect, value, k = f["aspect"].strip(), f.get("value", "").strip(), num(rid)
        below = next((t for t in reversed(standing) if k is not None and t[0] < k), (None, None, None))
        above = next((t for t in standing if k is not None and t[0] > k), (None, None, None))
        lo, hi = n_of.get(below[1]), n_of.get(above[1])

        def source(slug: str, n: int, near: bool) -> bool:
            if near or slug in with_rows:
                return near and slug in (below[1], above[1])
            if lo and hi:
                return lo < n < hi if lo <= hi else (n > lo or n < hi)
            return (not lo or n > lo) and (not hi or n < hi) and (bool(hi) or not cap or n <= cap)

        def placed(slug: str, texts: list[str], p: int) -> bool:
            """A neighbour's own fact fixes where in its document the removed one can sit: after
            the row below by no more places than ids between them, before the row above likewise."""
            ok = []
            for i, s_, t in (below, above):
                if s_ == slug and t in texts:
                    q = texts.index(t)
                    ok.append(0 < p - q <= k - i if i < k else 0 < q - p <= i - k)
            return any(ok) or not ok
        found = []
        for near in (True, False):
            for n, doc in files.items() if not found else ():
                src = listed.get(n)
                if not n.isdigit() or src is None or doc.get("slug") != src["slug"] \
                        or not source(src["slug"], int(n), near):
                    continue
                facts = doc.get("facts") or []
                texts = [_norm(x.get("fact")) for x in facts]
                for p, x in enumerate(facts):
                    said = tuple(str(x.get(c, "") or "").strip()
                                 for c in ("sub_indicator", "aspect", "value", "as_of", "system"))
                    if said[1:3] == (aspect, value) and (src["slug"], texts[p]) not in held_text \
                            and (src["slug"], *said) not in refused and (not near or placed(src["slug"], texts, p)):
                        found.append({"row_id": rid, "source_slug": src["slug"], "sub_indicator": said[0],
                                      "aspect": aspect, "value": value, "system": _norm(said[4])})
        out += found or [{"row_id": rid, "source_slug": "", "sub_indicator": "", "aspect": aspect,
                          "value": value, "system": ""}]
    return out


def refusal(gone: list[dict], slug: str, f: dict) -> tuple[str, str] | None:
    """`(removed row, rule)` where a fact repeats a removed row, else None. **It repeats it only from
    the same source, or about the same system with the same claim** (sub-indicator, aspect and
    value): a second document stating the same value of another system, or of none, is new
    evidence. A removed row no facts file answers is matched on aspect and value alone."""
    sub, aspect, value = (str(f.get(k, "") or "").strip() for k in ("sub_indicator", "aspect", "value"))
    system = _norm(f.get("system"))
    for g in gone:
        if (g["aspect"], g["value"]) != (aspect, value):
            continue
        if not g["source_slug"]:
            return g["row_id"], "unrecovered"
        if g["source_slug"] == slug:
            return g["row_id"], "source"
        if system and g["system"] == system and g["sub_indicator"] == sub:
            return g["row_id"], "system"
    return None


def merge(study: dict, iso: str, readlist: list[dict], files: dict[str, dict],
          existing: list[dict], fixes: list[dict] | None = None,
          merged: dict[str, str] | None = None, refused: list[dict] | None = None,
          ) -> tuple[list[dict], list[dict], list[str], dict[str, str], list[dict]]:
    """`(new evidence rows, systems rows, problems, documents taken, refusals)` from one country's
    facts files.

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
    corrected id; and a fact is refused, and named, where it repeats a removed row - the same
    aspect and value **from the same source, or about the same system** (`refusal`). The
    document's other facts are taken; one with none left is skipped.

    **A refusal is kept, and tried again.** `refused` is the country's standing refusals from
    `maturity/{id}/refused.csv`; each run tests them under the rule and the corrections as they
    now stand, takes a fact that now passes as a new row, and returns the refusals that still
    hold with those made now, for the file. A refusal is how a valid fact goes missing without
    trace, so the file is the trace. One whose `rule` reads `ruled: {why}` was refused by hand,
    and one reading `held: {why}` is kept back until a reassessment takes it; neither is tested
    again until its rule is changed.

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
    ids = [r["row_id"] for r in existing] + [i for i in named if i.startswith(f"{iso}-")]
    nxt = max([int(i.split("-")[1]) for i in ids if i.split("-")[1].isdigit()] or [0]) + 1
    rows, systems, problems, taken = [], [], [], {}
    fkey = lambda slug, f: (slug, *(str(f.get(k, "") or "").strip()  # noqa: E731
                                    for k in ("sub_indicator", "aspect", "value", "as_of", "system")))
    standing = {(r["source_slug"], r["sub_indicator"], r["aspect"], r["value"], r["as_of"], r["system"]): r
                for r in refused or []}
    still, today = {}, dt.date.today().isoformat()
    gone = removed_rows(iso, fixes or [], existing, listed, files, done,
                        {k for k in standing if k[0] in done})

    def refuse(n: str, slug: str, f: dict) -> bool:
        k = fkey(slug, f)
        if standing.get(k, {}).get("rule", "").startswith(("ruled", "held")):
            still[k] = standing[k]          # refused or held back by hand: not tested again
            return True
        hit = refusal(gone, slug, f)
        if hit:
            still[k] = dict(zip(REFUSED_FIELDS, (iso, n, *k, *hit,
                                                 standing.get(k, {}).get("refused_on") or today)))
        return bool(hit)
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
        facts = doc.get("facts") or []
        if src["slug"] in done and (not read or merged.get(src["slug"]) == read):
            # Taken before: only a standing refusal of its own is looked at again.
            doc = dict(doc, facts=[f for f in facts if fkey(src["slug"], f) in standing
                                   and not refuse(n, src["slug"], f)], systems=[])
        else:
            # Only the fact repeating a removed row is refused: the rest of its document still stands.
            kept_facts = [f for f in facts if not refuse(n, src["slug"], f)]
            if len(kept_facts) < len(facts):
                problems.append(f"{iso} facts/{n}.json: skipped {len(facts) - len(kept_facts)} fact(s), "
                                "repeating a removed row (refused.csv)")
                if not kept_facts:
                    continue
                doc = dict(doc, facts=kept_facts)
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
    # A standing refusal no facts file answered this run is kept as it was: nothing tested it.
    present = {fkey(listed[n]["slug"], f) for n, doc in files.items() if n in listed
               and doc.get("slug") == listed[n]["slug"] for f in doc.get("facts") or []}
    kept = [r for k, r in standing.items() if k not in present and k not in still]
    return rows, systems, problems, taken, kept + list(still.values())


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
        return {"value": "", "as_of": "", "sources": "", "others": "", "gap": "nothing found"}
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
        rpath = os.path.join(study_lib.study_dir(a.study), "refused.csv")
        refusals = study_lib.read_csv(rpath)
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
            new, systems, more, taken, mine = merge(study, iso, study_lib.read_csv(
                os.path.join(base, iso, "readlist.csv")), files, existing,
                [f for f in fixes if f.get("iso3") == iso or f.get("row_id", "").startswith(f"{iso}-")],
                before, [r for r in refusals if r["iso3"] == iso])
            refusals = [r for r in refusals if r["iso3"] != iso] + mine
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
        if refusals or os.path.exists(rpath):
            write_changed(rpath, REFUSED_FIELDS, sorted(refusals, key=lambda r: (
                r["iso3"], int(r["n"]) if r["n"].isdigit() else 0, r["aspect"], r["value"], r["as_of"])))
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
