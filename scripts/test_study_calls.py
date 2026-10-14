#!/usr/bin/env python3
r"""test_study_calls.py — `study-calls.py`: a regional story read once, and fanned back out.

    python scripts/test_study_calls.py

What would go wrong unnoticed: a story read twice, which is the cost the script exists to
cut; a country's own document pulled into a regional call; a long regional document, cut
per country, read from one country's passages for all; and a country the regional drafter
left out, which would read as unread at the merge.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("study_calls", HERE / "study-calls.py")
calls_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calls_mod)

fails = []


def check(label, got, want):
    ok = got == want
    print(("ok   " if ok else "FAIL ") + label + ("" if ok else f"\n     got {got!r}\n     want {want!r}"))
    if not ok:
        fails.append(label)


def row(n, slug, sl="1", read="whole", pass_="about", kind="raw"):
    return {"n": str(n), "slice": sl, "pass": pass_, "kind": kind, "slug": slug, "read": read,
            "path": f"raw/{slug}.md"}


many = {f"C{i}": [row(1, f"story-{j}") for j in range(7)] for i in range(2)}
check("regional stories share a call up to five",
      [len(c["stories"]) for c in calls_mod.plan(many, set()) if c["kind"] == "regional"], [5, 2])

lists = {
    "KEN": [row(1, "ken-own"), row(2, "pan-african"), row(3, "long-report", read="passages"),
            row(4, "ken-later", sl="2"), row(5, "ken-rung", pass_="rung")],
    "NGA": [row(1, "nga-own"), row(2, "pan-african"), row(3, "long-report", read="passages")],
    "GHA": [row(7, "pan-african", sl="3")],
}
calls = calls_mod.plan(lists, set())
regional = [st for c in calls if c["kind"] == "regional" for st in c["stories"]]
check("a story listed for three countries is one call", [c["slug"] for c in regional], ["pan-african"])
check("which carries each country's own number for it", regional[0]["countries"], {"GHA": 7, "KEN": 2, "NGA": 2})
check("a long document cut per country stays in each country's calls",
      sorted((c["iso"], tuple(c["ns"])) for c in calls if c["kind"] == "country"),
      [("KEN", (1, 3)), ("KEN", (4,)), ("NGA", (1, 3))])
check("an answered reading is not planned again",
      [c["kind"] for c in calls_mod.plan(lists, {("GHA", "7"), ("KEN", "2"), ("NGA", "2")})].count("regional"), 0)
check("and one answered country leaves the story regional for the rest",
      [st["countries"] for c in calls_mod.plan(lists, {("GHA", "7")}) if c["kind"] == "regional"
       for st in c["stories"]],
      [{"KEN": 2, "NGA": 2}])

answer = {"slug": "pan-african", "countries": {
    "KEN": {"facts": [{"aspect": "centre", "value": "service"}, 2026], "systems": [], "note": ""},
    "NGA": "nothing"}}
out = calls_mod.fan(answer, regional[0])
check("every listed country gets a file", sorted(out), ["GHA", "KEN", "NGA"])
check("under the story's slug", {d["slug"] for d in out.values()}, {"pan-african"})
check("a malformed entry is dropped, not merged", out["KEN"]["facts"], [{"aspect": "centre", "value": "service"}])
check("a country left out says so", out["GHA"]["note"], "the regional reading gave nothing for this country")
check("and so does one answered with something other than an object", out["NGA"]["facts"], [])

print()
print("all cases pass" if not fails else f"{len(fails)} of the cases FAILED")
sys.exit(1 if fails else 0)
