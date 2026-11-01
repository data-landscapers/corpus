#!/usr/bin/env python3
r"""budget-subtopics.py — place every budget line in a sub-topic and a sector, and check the rules.

    python scripts/budget-subtopics.py               # check the lookups, print the summary
    python scripts/budget-subtopics.py --out X.csv   # also write one row per line: deal_id, sub-topic, sector
    python scripts/budget-subtopics.py --unplaced dpi.govtech 30   # sample a topic's unspecified lines

**Two facets below the primary topic** *(Bill, 2026-11-01)*. A topic is too coarse to analyse a
budget by: `dpi.govtech` alone holds 40% of the lines. So each line gets a **sub-topic** — what
the money buys, defined per topic in `lookups/budget-subtopics.csv` — and, separately, a
**sector** — which part of government spends it, one list for every topic, built on UN COFOG, in
`lookups/budget-sectors.csv`. They are kept apart because a single tree would have to choose
between "tax systems" and "IT unit" for a tax administration's IT unit, and either choice loses
half of what the line says. A sub-topic that names a sector is therefore a defect.

**The rules are regexes, and the first match wins.** `budget-subtopic-rules.csv` is matched,
case-insensitively, against `purpose | line_name`, within the line's own primary topic, lowest
`priority` first; a rule with an empty pattern is the topic's `.unspecified` catch-all.
`budget-sector-rules.csv` is matched against `admin_head`, then `spending_entity` when the vote
names no sector, so a statistics unit inside an agriculture ministry is an agriculture line.
Several rules read only `line_name` on purpose: Nigeria's capital projects carry stock purpose
sentences ("Capital project of … for digitalisation of an agency's services, records or
processes") that would otherwise drag hundreds of lines into whichever sub-topic their
template happens to name.

**Status: draft for Bill's review.** Nothing reads these assignments yet. When the scheme is
approved, `budget_source.py --update` should derive `subtopic_id` and `sector_id` the way it
derives `primary_topic`, and this script becomes its check.

Exit 1 when a lookup is inconsistent: a rule naming an unknown id, a pattern that does not
compile, an `indicator_overlap` naming no indicator, or a topic with lines and no catch-all.
"""
from __future__ import annotations

import argparse
import collections
import csv
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(os.path.abspath(__file__))))
LOOK = os.path.join(ROOT, "lookups")
BUDGETS = os.path.join(ROOT, "budgets", "budgets-all-countries.csv")


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def load():
    errors = []
    subs = {r["subtopic_id"]: r for r in read(os.path.join(LOOK, "budget-subtopics.csv"))}
    sectors = {r["sector_id"]: r for r in read(os.path.join(LOOK, "budget-sectors.csv"))}
    indicators = {r["indicator_id"] for r in read(os.path.join(LOOK, "indicators.csv"))}
    topics = {r["Key"] for r in read(os.path.join(LOOK, "taxonomy.csv"))}

    def rules(name, idcol, known):
        out = []
        for i, r in enumerate(read(os.path.join(LOOK, name))):
            if r[idcol] not in known:
                errors.append(f"{name} row {i + 2}: unknown {idcol} {r[idcol]!r}")
                continue
            try:
                rx = re.compile(r["pattern"], re.I) if r["pattern"].strip() else None
            except re.error as e:
                errors.append(f"{name} row {i + 2}: pattern does not compile: {e}")
                continue
            out.append((int(r["priority"]), i, r[idcol], rx))
        out.sort(key=lambda t: (t[0], t[1]))
        return out

    sub_rules = rules("budget-subtopic-rules.csv", "subtopic_id", subs)
    sec_rules = rules("budget-sector-rules.csv", "sector_id", sectors)
    for sid, r in subs.items():
        if r["topic_id"] not in topics:
            errors.append(f"budget-subtopics.csv: {sid} names unknown topic {r['topic_id']!r}")
        if not sid.startswith(r["topic_id"] + "."):
            errors.append(f"budget-subtopics.csv: {sid} is not under its topic {r['topic_id']}")
        for ind in filter(None, (s.strip() for s in r["indicator_overlap"].split(";"))):
            if ind not in indicators:
                errors.append(f"budget-subtopics.csv: {sid} overlaps unknown indicator {ind!r}")
    by_topic = collections.defaultdict(list)
    for _, _, sid, rx in sub_rules:
        by_topic[subs[sid]["topic_id"]].append((sid, rx))
    return subs, sectors, by_topic, sec_rules, errors


def place(line, by_topic, sec_rules):
    text = f"{line['purpose']} | {line['line_name']}"
    sub = next((sid for sid, rx in by_topic.get(line["primary_topic_id"], [])
                if rx is None or rx.search(text)), None)
    sector = "unattributed"
    for field in ("admin_head", "spending_entity"):
        hit = next((s for _, _, s, rx in sec_rules if rx.search(line[field])), None)
        if hit:
            sector = hit
            break
    return sub, sector


def usd(line):
    try:
        return float(line["budget_usd"] or 0)
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--unplaced", nargs=2, metavar=("TOPIC", "N"))
    a = ap.parse_args()

    subs, sectors, by_topic, sec_rules, errors = load()
    lines = read(BUDGETS)
    placed = [(x, *place(x, by_topic, sec_rules)) for x in lines]
    for t in sorted({x["primary_topic_id"] for x in lines} - set(by_topic)):
        errors.append(f"topic {t} has budget lines and no sub-topic rules")
    for x, sub, _ in placed:
        if sub is None:
            errors.append(f"{x['deal_id']}: no rule placed it in {x['primary_topic_id']} (no catch-all)")

    n = collections.Counter(x["primary_topic_id"] for x, _, _ in placed)
    un = collections.Counter(x["primary_topic_id"] for x, s, _ in placed if s and s.endswith(".unspecified"))
    print(f"{len(lines)} lines, {len(subs)} sub-topics, {len(sectors)} sectors")
    print(f"unspecified: {sum(un.values())} lines ({sum(un.values()) / len(lines):.1%})")
    for t, k in n.most_common():
        if un[t]:
            print(f"  {t:22s} {un[t]:4d} of {k:5d} ({un[t] / k:.1%})")
    sec_n = collections.Counter(s for _, _, s in placed)
    print(f"sector unattributed: {sec_n['unattributed']} lines")

    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["deal_id", "country", "report_year", "primary_topic_id", "subtopic_id", "sector_id", "budget_usd"])
            for x, sub, sec in placed:
                w.writerow([x["deal_id"], x["country"], x["report_year"], x["primary_topic_id"], sub, sec, x["budget_usd"]])
        print(f"wrote {a.out}")
    if a.unplaced:
        t, k = a.unplaced
        pool = [x for x, s, _ in placed if x["primary_topic_id"] == t and s and s.endswith(".unspecified")]
        random.seed(0)
        for x in random.sample(pool, min(int(k), len(pool))):
            print(f"- {x['country']} | {x['purpose'][:110]} | {x['line_name'][:80]}")

    for e in errors:
        print("ERROR", e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
