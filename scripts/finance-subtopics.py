#!/usr/bin/env python3
r"""finance-subtopics.py — place every budget line and non-state deal in a sub-topic and a sector.

    python scripts/finance-subtopics.py               # check the lookups, print both summaries
    python scripts/finance-subtopics.py --out X.csv   # also write one row per line or deal
    python scripts/finance-subtopics.py --unplaced dpi.govtech 30   # sample a topic's unspecified rows

**Two facets below the primary topic** *(Bill, 2026-11-01)*. A topic is too coarse to analyse
finance by: `dpi.govtech` alone holds 40% of budget lines. So each row gets a **sub-topic** — what
the money buys, defined per topic in `lookups/finance-subtopics.csv` — and, separately, a
**sector** — the field the money serves, one list built on UN COFOG, in `lookups/finance-sectors.csv`.
They are kept apart because a single tree would have to choose between "tax systems" and "IT unit"
for a tax administration's IT unit, and either choice loses half of what the line says. A
sub-topic that names a sector is therefore a defect.

**One taxonomy for both sides** *(Bill, 2026-11-01)*, so `/finance/all/` can be cut by either
facet. Budget lines and deals share every sub-topic and sector id; what differs is the text the
rules read. Each rule carries `applies`: blank for both sides, `nonstate` for deals only.

**Sub-topic: the first match wins.** A budget line is matched on `purpose | line_name` against
the shared rules of its own primary topic, lowest `priority` first. A deal is matched on
`title | description | recipient_organisation` against the `nonstate` rules first, then the
shared ones, which were written for budget text and are only a fallback. A rule with an empty
pattern is the topic's `.unspecified` catch-all. Several budget rules read only `line_name` on
purpose: Nigeria's capital projects carry stock purpose sentences that would otherwise drag
hundreds of lines into whichever sub-topic their template happens to name.

**Sector.** A budget line: the shared rules against `admin_head`, then `spending_entity`, so a
statistics unit inside an agriculture ministry is an agriculture line. A deal: the recipient
when it is a public body the shared rules know, then the title, then the description's opening,
then its topic's default (`DEAL_TOPIC_SECTOR`; a deal naming no other field serves the digital
sector itself). Two traps are built in. A finance ministry is the borrower of record on most
sovereign loans, so it settles a deal's sector only when it is a tax, customs or public-finance
body; and financier names and loan words ("World Bank", "concessional loan", "additional
financing") are blanked before matching, since every loan title carries them.

**Status: draft for Bill's review.** Nothing reads these assignments yet. When the scheme is
approved, `budget_source.py --update` and `build-finance-page.py` should derive `subtopic_id`
and `sector_id`, and this script becomes their check.

Exit 1 when a lookup is inconsistent: a rule naming an unknown id, a pattern that does not
compile, an `indicator_overlap` naming no indicator, or a topic with rows and no catch-all.
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
DEALS = os.path.join(ROOT, "outputs", "non-state-finance", "all-nonstate.csv")

# A deal that names no field takes its topic's sector; topics absent here and not in
# DEAL_NO_DEFAULT default to digital. The listed exceptions serve too many fields to guess.
DEAL_TOPIC_SECTOR = {"dpi.pay": "finance", "data.statistics": "statistics",
                     "dpi.id": "home", "gov.discourse": "culture"}
DEAL_NO_DEFAULT = {"dpi.registry", "dpi.mis", "data.satellite", "data.open", "capacity.research",
                   "digital.localgov", "digital.rural"}
PUBLIC = {"Public Sector", "Multilateral", "PPP"}
BLANK = re.compile(r"\b(commercial|concessional|interest-free|syndicated) loan|(preferential )?buyer.?s credit"
                   r"|additional financing|bank of china|china (eximbank|development bank|construction bank)"
                   r"|world bank|exim ?bank|development bank"
                   r"|international bank for reconstruction and development", re.I)
PUBLIC_FINANCE = re.compile(r"\btax|customs|douane|revenue (authorit|administration|service)|imp[ôo]ts"
                            r"|public financ|procurement|march[ée]s publics|treasury|tr[ée]sor", re.I)


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def load():
    errors = []
    subs = {r["subtopic_id"]: r for r in read(os.path.join(LOOK, "finance-subtopics.csv"))}
    sectors = {r["sector_id"]: r for r in read(os.path.join(LOOK, "finance-sectors.csv"))}
    indicators = {r["indicator_id"] for r in read(os.path.join(LOOK, "indicators.csv"))}
    topics = {r["Key"] for r in read(os.path.join(LOOK, "taxonomy.csv"))}

    def rules(name, idcol, known):
        out = []
        for i, r in enumerate(read(os.path.join(LOOK, name))):
            if r[idcol] not in known:
                errors.append(f"{name} row {i + 2}: unknown {idcol} {r[idcol]!r}")
                continue
            if r["applies"] not in ("", "nonstate"):
                errors.append(f"{name} row {i + 2}: applies must be blank or nonstate")
                continue
            try:
                rx = re.compile(r["pattern"], re.I) if r["pattern"].strip() else None
            except re.error as e:
                errors.append(f"{name} row {i + 2}: pattern does not compile: {e}")
                continue
            out.append((int(r["priority"]), i, r[idcol], rx, r["applies"]))
        out.sort(key=lambda t: (t[0], t[1]))
        return out

    sub_rules = rules("finance-subtopic-rules.csv", "subtopic_id", subs)
    sec_rules = rules("finance-sector-rules.csv", "sector_id", sectors)
    for sid, r in subs.items():
        if r["topic_id"] not in topics:
            errors.append(f"finance-subtopics.csv: {sid} names unknown topic {r['topic_id']!r}")
        if not sid.startswith(r["topic_id"] + "."):
            errors.append(f"finance-subtopics.csv: {sid} is not under its topic {r['topic_id']}")
        for ind in filter(None, (s.strip() for s in r["indicator_overlap"].split(";"))):
            if ind not in indicators:
                errors.append(f"finance-subtopics.csv: {sid} overlaps unknown indicator {ind!r}")
    # per topic: (deal-only rules, shared rules, catch-all)
    by_topic = collections.defaultdict(lambda: ([], [], None))
    for _, _, sid, rx, applies in sub_rules:
        t = subs[sid]["topic_id"]
        ns, shared, catch = by_topic[t]
        if rx is None:
            by_topic[t] = (ns, shared, sid)
        else:
            (ns if applies else shared).append((sid, rx))
    return subs, sectors, by_topic, sec_rules, errors


def first(pairs, text):
    return next((sid for sid, rx in pairs if rx.search(text)), None)


def place_line(x, by_topic, sec_rules):
    ns, shared, catch = by_topic.get(x["primary_topic_id"], ([], [], None))
    sub = first(shared, f"{x['purpose']} | {x['line_name']}") or catch
    shared_sec = [(s, rx) for _, _, s, rx, a in sec_rules if not a]
    sector = next((h for h in (first(shared_sec, x[f]) for f in ("admin_head", "spending_entity")) if h),
                  "unattributed")
    return sub, sector


def place_deal(x, topic, by_topic, sec_rules):
    ns, shared, catch = by_topic.get(topic, ([], [], None))
    text = f"{x['title']} | {x['description']} | {x['recipient_organisation']}"
    sub = first(ns, text) or first(shared, text) or catch
    deal_only = [(s, rx) for _, _, s, rx, a in sec_rules if a]
    ordered = sorted(sec_rules, key=lambda t: (t[4] != "nonstate", t[0], t[1]))   # deal rules first
    every = [(s, rx) for _, _, s, rx, a in ordered]
    # the shared finance rules read "financing" in every loan title: a title takes finance from deal rules only
    no_budget_finance = [(s, rx) for _, _, s, rx, a in ordered if not (s == "finance" and not a)]
    public = x["beneficiary_type"] in PUBLIC
    for field, pool in (("recipient_organisation", every if public else deal_only),
                        ("title", no_budget_finance), ("description", deal_only)):
        value = BLANK.sub(" ", x[field][:400])
        hit = first(pool, value)
        if hit == "finance" and field == "recipient_organisation" and not PUBLIC_FINANCE.search(value) \
                and not first([p for p in deal_only if p[0] == "finance"], value):
            hit = None              # the finance ministry as borrower of record
        if hit:
            return sub, hit
    if topic in DEAL_NO_DEFAULT:
        return sub, "unattributed"
    return sub, DEAL_TOPIC_SECTOR.get(topic, "digital")


def summary(label, rows, subs):
    n = collections.Counter(t for t, _, _, _ in rows)
    un = collections.Counter(t for t, s, _, _ in rows if s and s.endswith(".unspecified"))
    print(f"{label}: {len(rows)} rows; unspecified {sum(un.values())} ({sum(un.values()) / len(rows):.1%}); "
          f"sector unattributed {sum(1 for r in rows if r[2] == 'unattributed')}")
    for t, k in n.most_common():
        if un[t]:
            print(f"  {t:22s} {un[t]:4d} of {k:5d} ({un[t] / k:.1%})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--unplaced", nargs=2, metavar=("TOPIC", "N"))
    a = ap.parse_args()

    subs, sectors, by_topic, sec_rules, errors = load()
    topic_key = {r["Level 2"]: r["Key"] for r in read(os.path.join(LOOK, "taxonomy.csv"))}
    lines = [(x["primary_topic_id"], *place_line(x, by_topic, sec_rules), x) for x in read(BUDGETS)]
    deals = []
    for x in read(DEALS):
        t = topic_key.get(x["primary_topic"], "")
        deals.append((t, *place_deal(x, t, by_topic, sec_rules), x))
    for side, rows, idf in (("budget", lines, "deal_id"), ("non-state", deals, "deal_id")):
        for t, sub, _, x in rows:
            if sub is None:
                errors.append(f"{side} {x[idf]}: no rule placed it in {t or '(no topic)'} (no catch-all)")

    print(f"{len(subs)} sub-topics, {len(sectors)} sectors")
    summary("budget", lines, subs)
    summary("non-state", deals, subs)

    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["side", "deal_id", "country", "year", "primary_topic_id", "subtopic_id", "sector_id", "value_usd"])
            for t, sub, sec, x in lines:
                w.writerow(["budget", x["deal_id"], x["country"], x["report_year"], t, sub, sec, x["budget_usd"]])
            for t, sub, sec, x in deals:
                m = x["commitment_usd_m"]
                w.writerow(["nonstate", x["deal_id"], x["recipient"], x["start_year"][:4], t, sub, sec,
                            f"{float(m) * 1e6:.0f}" if m else ""])
        print(f"wrote {a.out}")
    if a.unplaced:
        t, k = a.unplaced
        random.seed(0)
        for side, rows, f in (("budget", lines, lambda x: f"{x['purpose'][:110]} | {x['line_name'][:80]}"),
                              ("non-state", deals, lambda x: f"{x['title'][:110]} | {x['description'][:80]}")):
            pool = [x for tt, s, _, x in rows if tt == t and s and s.endswith(".unspecified")]
            for x in random.sample(pool, min(int(k), len(pool))):
                print(f"- {side} | {x.get('country') or x.get('recipient')} | {f(x)}")

    for e in errors:
        print("ERROR", e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
