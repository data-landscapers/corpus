#!/usr/bin/env python3
"""test_site_analytics.py — prove the analytics table fills, refills and never duplicates.

The table is written by a cycle nobody watches, and its failure modes all look like
data: a skipped night reads as a quiet day, a duplicated row as a busy one, a 0 where
nothing was fetched as a real zero. Each case builds a table in memory, runs the pure
parts of `site-analytics.py` against it, and asserts on what came out. No network.

    python scripts/test_site_analytics.py
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "site_analytics", Path(__file__).resolve().parent / "site-analytics.py")
sa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sa)

DL, CORPUS = sa.HOSTS
D = dt.date.fromisoformat
failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


def row(d: str, host: str, **vals) -> dict[str, str]:
    r = {f: "" for f in sa.FIELDS} | {"date": d, "host": host, "fetched_at": "old"}
    r.update({k: str(v) for k, v in vals.items()})
    return r


def filled(start: str, end: str, **vals) -> dict:
    """A table with both hosts filled for every date start..end."""
    return {(d.isoformat(), h): row(d.isoformat(), h, **vals)
            for d in sa.days(D(start), D(end)) for h in sa.HOSTS}


BOTH = {"views": 1, "users": 1, "sessions": 1, "clicks": 1, "impressions": 1}

print("range")
check("empty table starts at the floor",
      sa.fetch_start({}, "ga", D("2026-09-22")), sa.FLOOR)
t = filled("2026-09-13", "2026-09-22", **BOTH)
check("up to date: GA re-fetches its 3 days",
      sa.fetch_start(t, "ga", D("2026-09-23")), D("2026-09-21"))
check("up to date: Search Console re-fetches its 4 days",
      sa.fetch_start(t, "sc", D("2026-09-23")), D("2026-09-20"))
t = filled("2026-09-13", "2026-09-15", **BOTH) | filled("2026-09-17", "2026-09-22", **BOTH)
check("a gap is filled from its first missing date",
      sa.fetch_start(t, "ga", D("2026-09-23")), D("2026-09-16"))
t = filled("2026-09-13", "2026-09-15", **BOTH)
check("skipped nights: starts the day after the newest row",
      sa.fetch_start(t, "sc", D("2026-09-23")), D("2026-09-16"))
t = filled("2026-09-13", "2026-09-22", views=5, users=5, sessions=5)
check("a source's own blanks count as missing, not the other's values",
      sa.fetch_start(t, "sc", D("2026-09-23")), sa.FLOOR)
t = filled("2026-09-13", "2026-09-22", **BOTH)
check("zero is a value, not a gap",
      sa.fetch_start(filled("2026-09-13", "2026-09-22", views=0, users=0, sessions=0),
                     "ga", D("2026-09-23")), D("2026-09-21"))
check("--since overrides the window", sa.fetch_start(t, "ga", D("2026-09-23"), D("2026-09-14")),
      D("2026-09-14"))
check("the window never reaches before the floor",
      sa.fetch_start({}, "sc", D("2026-09-14")), sa.FLOOR)

print("host folding")
check("known hosts kept", [sa.fold_host(DL), sa.fold_host(CORPUS)], [DL, CORPUS])
check("local previews are dropped",
      {sa.fold_host(h) for h in ("localhost", "127.0.0.1", "::1")}, {None})
check("everything else is other",
      {sa.fold_host(h) for h in ("www.data-landscapers.io", None, "(not set)")}, {"other"})

print("merge")
t = filled("2026-09-20", "2026-09-21", **BOTH)
got = {("2026-09-21", DL): {"views": 10, "users": 4, "sessions": 5},
       ("2026-09-22", DL): {"views": 7, "users": 3, "sessions": 3},
       ("2026-09-22", "other"): {"views": 2, "users": 1, "sessions": 1}}
changed = sa.merge(t, "ga", D("2026-09-21"), D("2026-09-22"), got, "NOW")
check("a re-fetched date is replaced, not duplicated",
      sorted(k for k in t if k[0] == "2026-09-21"), [("2026-09-21", CORPUS), ("2026-09-21", DL)])
check("replaced values", t[("2026-09-21", DL)]["views"], "10")
check("other source's columns untouched", t[("2026-09-21", DL)]["clicks"], "1")
check("answered but silent host is 0", t[("2026-09-22", CORPUS)]["views"], "0")
check("new date's other source is blank, not 0", t[("2026-09-22", DL)]["clicks"], "")
check("other row created", t[("2026-09-22", "other")]["views"], "2")
check("changed dates reported", changed, ["2026-09-21", "2026-09-22"])
check("fetched_at moves on change", t[("2026-09-21", DL)]["fetched_at"], "NOW")
check("fetched_at stays when nothing changed", t[("2026-09-20", DL)]["fetched_at"], "old")

t = filled("2026-09-20", "2026-09-21", **BOTH)
got = {("2026-09-20", DL): {"clicks": 1, "impressions": 1},
       ("2026-09-20", CORPUS): {"clicks": 1, "impressions": 1}}
changed = sa.merge(t, "sc", D("2026-09-20"), D("2026-09-22"), got, "NOW")
check("an identical re-fetch changes nothing", changed, [])
check("unanswered dates keep their values", t[("2026-09-21", DL)]["clicks"], "1")
check("unanswered dates create no rows", ("2026-09-22", DL) in t, False)

t = filled("2026-09-20", "2026-09-20", **BOTH)
sa.merge(t, "sc", D("2026-09-20"), D("2026-09-20"), {}, "NOW")
check("a source returning nothing answers nothing", t[("2026-09-20", DL)]["clicks"], "1")

print("file")
t = filled("2026-09-20", "2026-09-20", views=3, users="", sessions="")
text = sa.render_table(t)
check("\\n endings, no \\r", "\r" in text, False)
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, "t.csv")
    sa.write_table(p, text)
    check("written bytes have no \\r", b"\r" in Path(p).read_bytes(), False)
    back = sa.read_table(p)
    check("round trip keeps blanks blank", back[("2026-09-20", DL)]["users"], "")
    check("round trip keeps values", back == t, True)
check("sorted by date then host",
      [l.split(",")[:2] for l in text.splitlines()[1:]],
      [["2026-09-20", CORPUS], ["2026-09-20", DL]])

print("summary")
t = filled("2026-09-22", "2026-09-22", views=5, users=1, sessions=1, clicks=2, impressions=9)
check("log message",
      sa.summary(t, ["2026-09-20", "2026-09-22"], D("2026-09-22"), {"sc": "boom"}),
      "2026-09-20..2026-09-22 written; 22 Sep: dl.io 5 views / 2 clicks, corpus 5 views / 2 clicks; "
      "Search Console FAILED: boom")

print()
if failures:
    print(f"{len(failures)} failed: {', '.join(failures)}")
    sys.exit(1)
print("all passed")
