#!/usr/bin/env python3
r"""budget-source-migrate.py — OSINT's domestic-state records into Corpus's source folder, once.

    cd scripts/.workroot
    python scripts/budget-source-migrate.py            # report what would be written
    python scripts/budget-source-migrate.py --write    # write budgets/{ISO3}/{FY}.csv

**Strategic review 4, R56a.** OSINT stops minting domestic-state budget records (R57), and
the 26 countries' tables the Finance page publishes are built from exactly those records. So
they are given a home in `budgets/` before the mint stops, and from then on the source folder
is where a country-year is maintained: `build-finance-page.py` merges, and a year present
here **replaces** OSINT's rows for that year rather than adding to them.

**This is a migration, not an extraction.** Every row it writes carries `origin_record`
naming the OSINT record it came from, which is what tells a migrated row from one a
`BUDGET-EXTRACT.md` sitting read against the spec. The distinction is the whole work order
for R58: a migrated row has never been checked against `documentation/budget-extract.md`, and
the ones short of the full schema are counted per country by `budget_source.check`.

**Nothing is invented.** A field the record does not carry is written empty, which is why
`budget_source` holds a migrated row to a narrower bar. Across the 494 records the structural
gaps were `admin_head_code` on 125, `admin_head` on 99, `fy_calendar` on 86, `scope_basis` on
240 and `doc_type` on 197 — and **a source document resolvable for 124**: three quarters of
the existing lines cite a document that has no source page of its own in the base, reachable
only through the record's own `url:`.

**Six records are not migrated, and they are named in the report.** They carry no fiscal year
at all — neither `fy_start` nor a parsable `fiscal_year_label` — and `budgets/{ISO3}/{FY}.csv`
is organised by country-year, so they have no home in it. Two are `NDP 12` plan-period
figures, which `budget-extract.md` says are never records. They stay OSINT's, and the merge
cannot touch them: `rec_fy()` returns nothing for a record with no determinable year, so no
source file ever drops one. **That is the safety property, not an oversight** — but it means
R57 retires four real lines with the layer, which its own line has to decide about.

**`purpose` and `notes` are the record's `## Description` and `## Notes`**, which are OSINT's
compiled prose about the line, not the budget volume's text — the distinction `design.md` §
*Source bodies* actually draws. `notes` is flattened to one line so a row stays a row.

This script is spent once it has run. It is kept for the same reason
`drop-pre-worker-editions.py` is: the migration is a fact about the data, and the script is
the only full statement of how each field was mapped.
"""
from __future__ import annotations

import argparse
import collections
import csv
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import budget_source as bs                                                      # noqa: E402
from finance_lib import fm_get, section                                         # noqa: E402
from vault_lib import dewiki                                                    # noqa: E402

_spec = importlib.util.spec_from_file_location("bfp", os.path.join(HERE, "build-finance-page.py"))
bfp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bfp)

CATALOGUE = bs.CATALOGUE


def flat(text: str) -> str:
    """A markdown section as one line: bullets joined, links dewikied, runs collapsed."""
    if not text:
        return ""
    out = []
    for line in text.strip().splitlines():
        line = line.strip().lstrip("-* ").strip()
        if line:
            out.append(line)
    return re.sub(r"\s+", " ", dewiki(" · ".join(out))).strip()


ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9}


def version(v: str) -> str:
    """`supplementary-iii` -> `supplementary-3`, and everything else as written.

    Kenya's supplementaries are numbered in roman on the record because the volumes are;
    the schema numbers them in arabic. Rewriting the numeral is a faithful re-expression of
    the same value, which is the only kind of change this script makes. The three records
    carrying `proposed` in this field are a different thing — `proposed` is a stage, not a
    version — and they are left exactly as written and counted, because guessing which
    version a tabled budget is would be inventing the answer."""
    v = (v or "").strip()
    m = re.fullmatch(r"supplementary-([ivx]+)", v, re.I)
    return f"supplementary-{ROMAN[m.group(1).lower()]}" if m and m.group(1).lower() in ROMAN else v


def money(v: str) -> str:
    """A stage total as the schema wants it: plain units, or empty.

    The records hold these as bare numbers already; anything else — a range, a figure with
    its scale written in — is dropped rather than guessed at, and counted in the report. A
    number this cannot read is not a number this may reformat."""
    v = (v or "").strip()
    if not v:
        return ""
    v = v.replace(",", "").replace(" ", "")
    return v if bs.MONEY.match(v) else ""


def source_index() -> dict[str, list[str]]:
    """`{url: [slug, …]}` from Corpus's own catalogue export."""
    out: dict[str, list[str]] = collections.defaultdict(list)
    if not os.path.exists(CATALOGUE):
        return out
    with open(CATALOGUE, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("url"):
                out[r["url"].strip()].append(r["slug"])
    return out


def source_slug(rec, by_url, record_slugs) -> str:
    """The held document this line's figure is printed in, or empty.

    Three sources, in order. A `[[slug]]` in the body that resolves to a held page — the
    stage history cites the companion that way. Then a catalogue row sharing the record's
    own `url:`, **excluding every other domestic line-item record**, because the siblings
    built from one volume all carry that same URL and pointing a row at its sibling would
    be a citation to nothing. A `-companion` page wins over any other match. Otherwise
    empty: the document has no page of its own and the record's `url:` is the only route
    to it, which is a fact about the base and not something to paper over."""
    held = set(s for slugs in by_url.values() for s in slugs)
    for link in re.findall(r"\[\[([^\]]+)\]\]", rec["body"]):
        if link in held and link not in record_slugs:
            return link
    url = fm_get(rec["fm"], "url").strip()
    cand = [s for s in by_url.get(url, []) if s != rec["fn"][:-3] and s not in record_slugs]
    for s in cand:
        if s.endswith("-companion"):
            return s
    return cand[0] if cand else ""


def fy_of(rec) -> str:
    """The bare start year, or empty where the record states no fiscal year at all."""
    fy = fm_get(rec["fm"], "fy_start")[:4]
    if fy.isdigit():
        return fy
    m = re.search(r"\d{4}", fm_get(rec["fm"], "fiscal_year_label"))
    return m.group(0) if m else ""


def row_for(place, rec, by_url, record_slugs) -> dict:
    fm = rec["fm"]
    F = lambda k: fm_get(fm, k).strip()                                   # noqa: E731
    C = lambda k, t="": bfp.cfield(rec, k, t)                             # noqa: E731
    T = lambda k: (rec["table"].get(k, "") or "").strip()                 # noqa: E731
    r = {c: "" for c in bs.COLUMNS}
    r.update({
        "deal_id": rec["deal_id"], "place": place,
        "state_level": F("state_level") or "national",
        "spending_tier_name": F("spending_tier_name"),
        "fiscal_year_label": bfp.fy_normalise(F("fiscal_year_label")) or fy_of(rec),
        "fy_start": F("fy_start"), "fy_end": F("fy_end"), "fy_calendar": F("fy_calendar"),
        "budget_version": version(F("budget_version")) or "original",
        "supplementary_basis": F("supplementary_basis"),
        "admin_head_code": bfp.vote_num(rec), "admin_head": C("admin_head"),
        "spending_entity_code": C("spending_entity_code"),
        "spending_entity": C("spending_entity", "Spending entity"),
        "programme_code": C("programme_code"), "programme": C("programme", "Programme"),
        "sub_programme_code": C("sub_programme_code"),
        "sub_programme": C("sub_programme", "Subprogramme"),
        "econ_class": C("econ_class"),
        "line_name": bfp.line_name(rec),
        "purpose": flat(section(rec["body"], "Description")),
        "primary_subject": bfp.primary_subject(rec),
        "scope_confidence": F("scope_confidence"), "scope_basis": flat(T("scope_basis")),
        "finance_origin": F("finance_origin"),
        "funding_source": F("funding_source") or T("funding_source"),
        "is_transfer": F("is_transfer") or "false", "transfer_to": T("transfer_to"),
        "currency": F("currency"), "amount_scale": flat(F("amount_scale") or T("amount_scale")),
        "baseline_stage": F("baseline_stage"), "current_stage": F("current_stage"),
        "exec_vs_voted": money(F("execution_pct_vs_appropriated")),
        "exec_vs_revised": money(F("execution_pct_vs_revised")),
        "source_tier": F("source_tier"), "doc_type": C("doc_type", "doc_type"),
        "doc_locator": C("doc_locator", "doc_locator"),
        "source_slug": source_slug(rec, by_url, record_slugs),
        "extracted": F("ingested") or F("retrieved") or F("published")[:10],
        "origin_record": rec["fn"][:-3],
        "notes": flat(section(rec["body"], "Notes")),
    })
    for stage in bs.STAGES:
        r[stage] = money(F(f"{stage}_total"))
    return r


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Migrate OSINT's budget records into budgets/.")
    ap.add_argument("--write", action="store_true", help="write the files; else report only")
    ap.add_argument("--budgets", default=bs.BUDGETS, help="another budgets/ root, for tests")
    a = ap.parse_args(argv)

    by_place = bfp.scan_all()
    record_slugs = {r["fn"][:-3] for b in by_place.values() for r in b["dom"]}
    by_url = source_index()
    if not by_url:
        print("budget-source-migrate: no catalogue, so no source document can be resolved. "
              "Run the catalogue compile first.")
        return 2

    files: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    skipped: list[tuple[str, str]] = []
    lost_money = 0
    for place in sorted(by_place):
        for rec in by_place[place]["dom"]:
            fy = fy_of(rec)
            if not fy:
                skipped.append((place, rec["fn"][:-3]))
                continue
            r = row_for(place, rec, by_url, record_slugs)
            if not any(r[s] for s in bs.STAGES):
                lost_money += 1
            files[(place, fy)].append(r)

    n = sum(len(v) for v in files.values())
    print(f"{n} row(s) into {len(files)} country-year file(s) across "
          f"{len({p for p, _ in files})} countries.")
    if skipped:
        print(f"\n{len(skipped)} record(s) state no fiscal year and are NOT migrated — "
              f"`budgets/` is organised by country-year and they belong to none:")
        for place, slug in skipped:
            print(f"  {place}  {slug}")
    if lost_money:
        print(f"\n{lost_money} row(s) carry no stage figure this could read.")

    # What the migration is short of, by field. The report is the point: it is the only
    # statement of how much of the published table rests on a record that never carried
    # what the spec asks for.
    short = collections.Counter()
    for rows in files.values():
        for r in rows:
            for c in bs.REQUIRED:
                if not r[c]:
                    short[c] += 1
    if short:
        print(f"\nfields empty across the {n} migrated row(s), against the full schema:")
        for c, k in short.most_common():
            print(f"  {k:4d}  {c}")

    if not a.write:
        print("\n(report only — pass --write to write the files)")
        return 0

    for (place, fy), rows in sorted(files.items()):
        d = os.path.join(a.budgets, place)
        os.makedirs(d, exist_ok=True)
        rows.sort(key=lambda r: (r["admin_head_code"].zfill(6), r["deal_id"]))
        with open(os.path.join(d, f"{fy}.csv"), "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(bs.COLUMNS))
            w.writeheader()
            w.writerows(rows)
    print(f"\nwrote {len(files)} file(s) under {a.budgets}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
