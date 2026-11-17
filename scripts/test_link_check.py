#!/usr/bin/env python3
"""test_link_check.py — prove one bad night never makes a link dead.

The case that started link-check.py was an outage that looked like 404s, so the rules that
refuse to call a link dead are the ones asserted: a single failure, two failures inside a
week, a failure on a host failing wholesale, a block. The network is replaced by a table.

    python scripts/test_link_check.py
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("lc", os.path.join(HERE, "link-check.py"))
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)

failures: list[str] = []


def check(label, got, want):
    if got != want:
        failures.append(f"{label}: got {got!r}, want {want!r}")


tmp = tempfile.mkdtemp()
lc.STATE = os.path.join(tmp, "state.csv")
lc.HOST_GAP = 0
lc.wayback = lambda url, published: "https://web.archive.org/web/2026/" + url

CAT = {
    "https://a.example/1": {"slugs": ["s1"], "published": "2026-01-01"},
    "https://b.example/1": {"slugs": ["s2"], "published": "2026-01-01"},
    "https://down.example/1": {"slugs": ["d1"], "published": "2026-01-01"},
    "https://down.example/2": {"slugs": ["d2"], "published": "2026-01-01"},
    "https://down.example/3": {"slugs": ["d3"], "published": "2026-01-01"},
    "https://wall.example/1": {"slugs": ["w1"], "published": "2026-01-01"},
}
ANSWER = {"https://a.example/1": ("gone", "404"), "https://b.example/1": ("ok", "200"),
          "https://wall.example/1": ("blocked", "403")}
lc.catalogue = lambda: CAT
lc.probe = lambda session, url: ANSWER.get(url, ("gone", "404"))

day = ["2026-11-01"]
lc.today = lambda: day[0]


def state():
    return lc.merge(lc.load(), CAT)


lc.run(100, 5)
s = state()
check("one failure is a suspect", (s["https://a.example/1"]["state"], lc.is_dead(s["https://a.example/1"])), ("gone", False))
check("host failing wholesale is down", s["https://down.example/1"]["state"], "host-down")
check("host-down counts no failure", s["https://down.example/1"]["fails"], "0")
check("blocked is not gone", s["https://wall.example/1"]["state"], "blocked")

day[0] = "2026-11-04"
lc.run(100, 5)
s = state()
check("suspect not rechecked inside a week", s["https://a.example/1"]["checked"], "2026-11-01")

day[0] = "2026-11-08"
lc.run(100, 5)
s = state()
check("second failure a week on is dead", lc.is_dead(s["https://a.example/1"]), True)
check("dead link gets an archive", s["https://a.example/1"]["archive"].startswith("https://web.archive.org/"), True)
check("owed is the dead link only", [r["url"] for r in lc.owed(s)], ["https://a.example/1"])

ANSWER["https://b.example/1"] = ("gone", "404")
day[0] = "2026-12-08"
lc.run(100, 5)
ANSWER["https://b.example/1"] = ("ok", "200")
day[0] = "2026-12-15"
lc.run(100, 5)
s = state()
check("recovery clears a suspect", (s["https://b.example/1"]["state"], s["https://b.example/1"]["fails"]), ("ok", "0"))

lc.BATCHES = os.path.join(tmp, "batches")
path = lc.batch(s)
check("batch marks sent", lc.owed(state()), [])
check("batch names the slug", open(path, encoding="utf-8").read().count("\ns1,"), 1)

del CAT["https://a.example/1"]
check("a link OSINT replaced drops out", "https://a.example/1" in state(), False)

if failures:
    print("\n".join(failures))
    sys.exit(1)
print("link-check: all cases pass")
