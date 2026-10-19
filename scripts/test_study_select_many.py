#!/usr/bin/env python3
"""test_study_select_many.py — the one-pass arrivals scan lists what the per-study scan lists.

Housekeeping 25 made `study-select.py --new` take several studies, or ALL, from one read of
`raw/`. That is only safe if, for every study and country, `select` gives the same reading list
from `view(scan_many(...))` as from `scan(...)`. This runs both over a sample of the index —
every fifth document, which keeps it to minutes while still holding regional and untagged
documents — for three studies of different shapes, and compares every country's rows.

    cd scripts/.workroot
    python scripts/test_study_select_many.py
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

HERE = Path(os.path.abspath(__file__)).parent
sys.path.insert(0, str(HERE))
_spec = importlib.util.spec_from_file_location("study_select", HERE / "study-select.py")
ss = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ss)
import status_lib  # noqa: E402
import study_lib   # noqa: E402
import vault_lib   # noqa: E402

STUDIES = ("addressregister", "accesstoinformationlaw", "health")
SAMPLE = 5

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {str(got)[:300]}\n         want: {str(want)[:300]}")
        failures.append(name)


def main() -> int:
    index = vault_lib.load_index()[::SAMPLE]
    countries = study_lib.countries()
    studies = {s: study_lib.load(s) for s in STUDIES}
    terms = {s: study_lib.term_regex(st["terms"]) for s, st in studies.items()}
    base, hits = ss.scan_many(index, ss.read_raw, terms, countries)
    by_url_many = {d["url_norm"]: s for s, d in base.items() if d["url_norm"]}
    for s, st in studies.items():
        old = ss.scan(index, ss.read_raw, terms[s])
        new = ss.view(base, hits[s])
        check(f"{s}: same documents scanned", sorted(new), sorted(old))
        by_url = {d["url_norm"]: k for k, d in old.items() if d["url_norm"]}
        check(f"{s}: same url map", by_url_many, by_url)
        bad, regional = [], 0
        for iso in sorted(countries):
            routes, _ = ss.cited(iso, st["subjects"], terms[s], status_lib.REPORTS, by_url,
                                 tuple(st.get("carry", ())))
            a = ss.select(iso, countries[iso], old, st["subjects"], routes)
            b = ss.select(iso, countries[iso], new, st["subjects"], routes)
            if a != b:
                bad.append(iso)
            regional += sum("regional" in r["why"].split("+") for r in a[0])
        check(f"{s}: every country's reading list identical", bad, [])
        check(f"{s}: regional documents were compared", regional > 0, True)

        # The incremental --new: pretend each list was made at `since`, holding every document
        # the full selection admits that was written before it, less those a report vouches
        # for (as if the report cited them only after the list was made). What changed_docs then adds
        # must be exactly what the full selection adds on top.
        since = sorted(int(r["d"]["mtime"]) for r in ss.raw_rows(index))[len(ss.raw_rows(index)) * 9 // 10]
        mt = {r["d"]["slug"]: int(r["d"]["mtime"]) for r in ss.raw_rows(index)}
        lists, routed, full_new = {}, {}, {}
        for iso in sorted(countries):
            routed[iso], _ = ss.cited(iso, st["subjects"], terms[s], status_lib.REPORTS, by_url,
                                      tuple(st.get("carry", ())))
            rows = ss.select(iso, countries[iso], old, st["subjects"], routed[iso])[0]
            lists[iso] = [{"kind": "raw", "slug": r["slug"]} for r in rows
                          if mt[r["slug"]] < since
                          and not any(h.endswith("!") for h in routed[iso].get(r["slug"], ()))]
            held = {r["slug"] for r in lists[iso]}
            full_new[iso] = [r["slug"] for r in rows if r["slug"] not in held]
        part = ss.changed_docs(index, since, routed, lists, ss.read_raw, terms[s])
        inc_new = {iso: [r["slug"] for r in ss.select(iso, countries[iso], part, st["subjects"], routed[iso])[0]
                         if r["slug"] not in {x["slug"] for x in lists[iso]}] for iso in sorted(countries)}
        check(f"{s}: incremental arrivals equal the full scan's", inc_new, full_new)
        check(f"{s}: incremental read a fraction of raw/", len(part) < len(old) // 4, True)
    print(f"test_study_select_many: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
