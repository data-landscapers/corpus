#!/usr/bin/env python3
r"""
maturity-render.py — the maturity assessment rendered for reading (tasks F3 and F1, first pass).

    python scripts/maturity-render.py indicators        # outputs/maturity/indicators/{id}.md
    python scripts/maturity-render.py countries         # outputs/reports/{ISO3}/{ISO3}-maturity.md
    python scripts/maturity-render.py all

**Why this exists before the rest of F** *(Bill, 2026-09-24)*: a stage cannot be judged in
isolation. It is judged beside the same indicator in the other 53 countries, with the evidence
in front of the reader as it will be published, not as slugs and row ids. So the one-indicator
view comes first, and every cell carries its evidence:

- for an instrument or a system, the ledger rows the stage rests on, by name and status, each
  linked to its latest source visible at the month end;
- for a measure, the figure, its unit and year, and where it comes from in words: the
  publisher and date of a cited source, Corpus's own compile, or the reference dataset with the
  kind of figure (survey, estimate) and its release.

The qualifier prints beside the evidence, and so do July and August, so a movement reads as one.

**Links resolve through `outputs/catalogue/catalogue-internal.csv` directly**, not through
`report-render.py`'s checked path, because that refuses a catalogue behind the day's ingest.
Every source a ledger cites is one Corpus read, so it is in the catalogue whatever its age. The
site render (F5) goes through the checked path. This file writes markdown into `outputs/` and
publishes nothing.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import datetime as dt
import importlib.util
import re
import sys
import urllib.parse
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import indicators_lib  # noqa: E402

_spec = importlib.util.spec_from_file_location("ma", HERE / "maturity-assess.py")
ma = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ma)

CORPUS = HERE.parent
REPORTS = CORPUS / "outputs" / "reports"
OUT_IND = CORPUS / "outputs" / "maturity" / "indicators"
CATALOGUE = CORPUS / "outputs" / "catalogue" / "catalogue-internal.csv"
COUNTRIES = CORPUS / "lookups" / "countries.csv"
SITE = "https://corpus.data-landscapers.io"
MONTHS = ("2026-07", "2026-08")
STAGE_NAME = {"1": "Absent", "2": "Nascent", "3": "Established", "4": "Operating", "5": "Leading"}

# The reference datasets, in words and at their home page, for a reader following a figure.
DATASETS = {
    "itu-sdg-17-8-1-internet-use": ("ITU, internet use (SDG 17.8.1), via the UN SDG database",
                                    "https://unstats.un.org/sdgs/dataportal"),
    "itu-sdg-5b1-mobile-ownership-10plus": ("ITU, mobile-phone ownership 10+ (SDG 5.b.1), via the UN SDG database",
                                            "https://unstats.un.org/sdgs/dataportal"),
    "itu-price-basket-5gb-gni": ("ITU ICT Price Baskets, 5 GB data-only basket",
                                 "https://www.itu.int/en/ITU-D/Statistics/Pages/ICTprices/default.aspx"),
    "wdi-elc-accs-rural": ("World Bank WDI, rural access to electricity",
                           "https://data.worldbank.org/indicator/EG.ELC.ACCS.RU.ZS"),
    "enterprise-surveys-outages": ("World Bank Enterprise Surveys, outages in a typical month",
                                   "https://www.enterprisesurveys.org/en/data"),
    "findex-account-ownership": ("World Bank Global Findex, account ownership 15+",
                                 "https://data.worldbank.org/indicator/FX.OWN.TOTL.ZS"),
    "wdi-ict-service-exports-gdp": ("World Bank WDI, ICT service exports over GDP",
                                    "https://data.worldbank.org/indicator/BX.GSR.CCIS.CD"),
    "uis-4a1-secondary-internet": ("UNESCO UIS, secondary schools with internet (SDG 4.a.1)",
                                   "https://databrowser.uis.unesco.org/"),
    "uis-stem-graduates": ("UNESCO UIS, STEM share of tertiary graduates", "https://databrowser.uis.unesco.org/"),
    "ilostat-isic-j-employment": ("ILOSTAT, employment in information and communication (ISIC J)",
                                  "https://ilostat.ilo.org/data/"),
    "itu-internet-use-gender-gap": ("ITU, internet use by sex, via the UN SDG database",
                                    "https://unstats.un.org/sdgs/dataportal"),
}
COMPILES = {
    "budgets": ("Corpus, the state's budget document as read", f"{SITE}/finance/"),
    "outputs/non-state-finance": ("Corpus, non-state finance", f"{SITE}/finance/"),
    "outputs/datasets/data-centres": ("Corpus, data centres dataset", f"{SITE}/datasets/"),
}


# --------------------------------------------------------------------------- reading

def catalogue() -> dict[str, dict]:
    with open(CATALOGUE, encoding="utf-8-sig", newline="") as fh:
        return {r["slug"].strip(): r for r in csv.DictReader(fh)}


def countries() -> dict[str, str]:
    with open(COUNTRIES, encoding="utf-8-sig", newline="") as fh:
        return {r["iso-3"]: r["country-name"] for r in csv.DictReader(fh) if not r["iso-3"].startswith("X")}


def month_end(m: str) -> dt.date:
    y, mo = map(int, m.split("-"))
    return dt.date(y, mo, calendar.monthrange(y, mo)[1])


def editions() -> dict[str, dict[str, dict[str, dict]]]:
    """{month: {unit: {indicator_id: row}}}"""
    out = {}
    for m in MONTHS:
        out[m] = {}
        for p in sorted(REPORTS.glob(f"*/maturity/{m}.csv")):
            out[m][p.parent.parent.name] = {r["indicator_id"]: r for r in ma.read_csv(p)[1]}
    return out


def esc(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def date_words(d: str) -> str:
    try:
        return dt.date.fromisoformat(d[:10]).strftime("%-d %b %Y")
    except ValueError:
        try:
            return dt.date.fromisoformat(d[:10]).strftime("%d %b %Y").lstrip("0")
        except ValueError:
            return d


# --------------------------------------------------------------------------- evidence

def source_link(slug: str, cat: dict) -> str:
    """A cited source in words: publisher and date, linked to the publisher's page, or to the
    record's row in the Corpus catalogue where no page is published."""
    r = cat.get(slug)
    d = ma.src_date(slug)
    when = date_words(d.isoformat()) if d else ""
    if not r:
        return f"{when} (not in the catalogue)" if when else esc(slug)
    who = r.get("publisher") or "source"
    url = (r.get("url") or "").strip() or f"{SITE}/catalogue/#q={urllib.parse.quote(slug)}"
    label = f"{who}, {when}" if when else who
    return f"[{esc(label)}]({url.replace('(', '%28').replace(')', '%29')})"


def row_evidence(row_ids: list[str], led: dict, as_at: dt.date, cat: dict) -> str:
    parts = []
    for rid in row_ids:
        r = led.get(rid)
        if not r:
            parts.append(esc(rid))
            continue
        vis = ma.visible(r, as_at)
        latest = max(vis)[1] if vis else ""
        status = (r.get("status") or "").split(",")[0].strip()
        link = source_link(latest, cat) if latest else ""
        parts.append(f"**{esc(r['name'])}**" + (f" ({esc(status)})" if status else "") + (f" — {link}" if link else ""))
    return "<br>".join(parts)


def measure_evidence(r: dict, cat: dict, ref_nature: dict) -> str:
    value, unit, year, src = (r.get(k, "") for k in ("value", "unit", "value_year", "value_source"))
    if not value:
        return ""
    fig = f"**{value} {esc(unit)}** ({year})"
    m = ma.SOURCE_AT.match(src)
    if src.startswith("ref:"):
        ds, rel = src[4:].split("@")
        label, url = DATASETS.get(ds, (ds, ""))
        nature = ref_nature.get(ds, "")
        kind = {"estimate": "modelled estimate", "survey": "survey", "country": "country-reported",
                "tariffs": "published tariffs", "official": "official statistics"}.get(nature, "")
        tail = f"[{label}]({url})" if url else label
        return f"{fig} — {tail}{', ' + kind if kind else ''}, released {date_words(rel)}"
    if m:
        path = src.split("@")[0]
        key = next((k for k in COMPILES if path.startswith(k)), "")
        label, url = COMPILES.get(key, (path, ""))
        return f"{fig} — [{label}]({url})" if url else f"{fig} — {label}"
    return f"{fig} — {source_link(src, cat)}"


def ref_natures() -> dict[tuple, str]:
    """{(unit, indicator, year, value): nature} to say what kind of figure a reference is."""
    out = {}
    if ma.REFERENCE.exists():
        for r in ma.read_csv(ma.REFERENCE)[1]:
            out[(r["iso3"], r["indicator_id"], r["year"], r["value"])] = r.get("nature", "")
    return out


# --------------------------------------------------------------------------- the pages

# A measure's stages in the design's own words for measures (maturity-assessment.md §3): a band
# against the norm, not a thing that exists or not.
MEASURE_NAME = {"1": "far below", "2": "below", "3": "approaching", "4": "meets", "5": "exceeds"}


def stage_cell(r: dict | None, measure: bool = False) -> str:
    if r is None:
        return "—"
    s = r.get("stage", "")
    return f"{s} {(MEASURE_NAME if measure else STAGE_NAME)[s]}" if s else "unplaced"


def indicator_page(ind: dict, eds: dict, names: dict, cat: dict, natures: dict, ledgers: dict) -> str:
    iid = ind["indicator_id"]
    rub = ma.rubric().get(iid, {})
    norm = ma.norms().get(iid, {})
    spec = ma.measures(month_end(MONTHS[-1])).get(iid)
    last, first = eds[MONTHS[-1]], eds[MONTHS[0]]
    o = [f"# {ind['indicator']}", "",
         f"*{ind['kind'].capitalize()} · {ind['chapter']} · `{iid}`*", ""]
    if norm:
        o += [f"**Norm**: {esc(norm.get('instrument'))} ({esc(norm.get('tier'))}) — "
              f"{esc(norm.get('provision'))}", ""]
    if spec:
        cuts = " · ".join(f"{c:g}" for c in spec["cuts"])
        o += [f"**Band**: {spec['method']}, {spec['direction']} is better; cuts {cuts}"
              f"{' (quintiles cut ' + spec['cut_as_at'] + ')' if spec.get('cut_as_at') else ' (provisional)' if spec.get('provisional') == '1' else ''}"
              f". {esc(spec.get('value', ''))}", ""]
    o += ["| Stage | What it takes |", "|---|---|"]
    for s in sorted(rub):
        o.append(f"| {s} {(MEASURE_NAME if ind['kind'] == 'measure' else STAGE_NAME)[str(s)]} | {esc(rub[s]['anchor'])} |")
    meas = ind["kind"] == "measure"
    words = MEASURE_NAME if meas else STAGE_NAME
    counts = Counter(stage_cell(last.get(u, {}).get(iid), meas) for u in names)
    order = [f"{k} {words[k]}" for k in "54321"] + ["unplaced", "—"]
    o += ["", "**August 2026, 54 countries**: " + " · ".join(
        f"{k.replace('—', 'No evidence')} {counts[k]}" for k in order if counts[k]), ""]
    o += ["| Country | Jul | Aug | Evidence (as at 31 Aug) | Qualifier |", "|---|---|---|---|---|"]
    rank = {k: n for n, k in enumerate(order)}
    rows = []
    for u, name in names.items():
        a, j = last.get(u, {}).get(iid), first.get(u, {}).get(iid)
        if a is None and j is None:
            rows.append((rank["—"], name, f"| {name} | — | — | *No evidence* | |"))
            continue
        cur = a or j
        if ind["kind"] == "measure":
            ev = measure_evidence(cur, cat, {})
            if cur.get("value_source", "").startswith("ref:"):
                n = natures.get((u, iid, cur.get("value_year", ""), cur.get("value", "")), "")
                ev = measure_evidence(cur, cat, {cur["value_source"][4:].split("@")[0]: n})
            # The ledger rows cited, where they add a source the figure does not already name.
            rows_ev = row_evidence(ma.indicators_lib.row_ids({"row_ids": cur.get("stage_rows", "")}),
                                   ledgers[u], month_end(MONTHS[-1]), cat) if cur.get("stage_rows") else ""
            if rows_ev and cur.get("value_source") and cat.get(cur["value_source"], {}).get("url", "~") in rows_ev:
                rows_ev = ""
            ev = "<br>".join(x for x in (ev, rows_ev) if x)
        else:
            ids = [x for x in (cur.get("stage_rows") or "").split("|") if x]
            ev = row_evidence(ids, ledgers[u], month_end(MONTHS[-1]), cat)
        moved = " ▲" if a and j and a.get("stage") != j.get("stage") and a.get("moved_by") else ""
        rows.append((rank[stage_cell(a, meas)], name,
                     f"| {name} | {stage_cell(j, meas)} | {stage_cell(a, meas)}{moved} | {ev} | {esc(cur.get('qualifier'))} |"))
    o += [r[2] for r in sorted(rows)]
    o += ["", "*▲ the stage moved in August on a source dated in the month. Unplaced: the "
          "evidence held meets no stage. —: no evidence.*", ""]
    return "\n".join(o)


def render_indicators() -> int:
    eds, names, cat, natures = editions(), countries(), catalogue(), ref_natures()
    ledgers = {u: ma.ledger(REPORTS, u) for u in names if (REPORTS / u / "ledger.csv").exists()}
    OUT_IND.mkdir(parents=True, exist_ok=True)
    frame = indicators_lib.assessed()
    index = ["# Maturity assessment — by indicator", "",
             "*Each page shows one indicator across the 54 countries, July and August 2026, with "
             "the evidence each stage rests on.*", ""]
    chapter = None
    for ind in frame:
        if ind["chapter"] != chapter:
            chapter = ind["chapter"]
            index += ["", f"## {chapter}", ""]
        (OUT_IND / f"{ind['indicator_id']}.md").write_text(
            indicator_page(ind, eds, names, cat, natures, ledgers), encoding="utf-8")
        c = Counter(stage_cell(eds[MONTHS[-1]].get(u, {}).get(ind["indicator_id"]), ind["kind"] == "measure")
                    for u in names)
        index.append(f"- [{ind['indicator']}]({ind['indicator_id']}.md) — *{ind['kind']}* — "
                     + ", ".join(f"{k.split()[0]}: {v}" for k, v in sorted(c.items()) if k[0].isdigit()))
    (OUT_IND / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    return len(frame)


def country_page(unit: str, name: str, eds: dict, cat: dict, natures: dict, led: dict) -> str:
    """F1: one country's assessment, by chapter and kind, with its evidence and the month's
    movement. Counts are per kind and never across kinds (§4, §11)."""
    last, first = eds[MONTHS[-1]].get(unit, {}), eds[MONTHS[0]].get(unit, {})
    as_at = month_end(MONTHS[-1])
    frame = indicators_lib.assessed()
    o = [f"# {name}: maturity assessment", "",
         f"*As at 31 August 2026, beside 31 July. Each indicator is placed on five stages against "
         f"a continental norm: for a law, strategy or system, 1 Absent · 2 Nascent · 3 Established "
         f"· 4 Operating · 5 Leading; for a measure, 1 far below · 2 below · 3 approaching · "
         f"4 meets · 5 exceeds the norm's target. **Unplaced** means the repository holds evidence "
         f"that meets no stage. **No evidence** means it holds none. A stage moves only on a "
         f"source dated inside the month.*", ""]
    for kind in indicators_lib.KINDS:
        ids = [f["indicator_id"] for f in frame if f["kind"] == kind]
        c = Counter(stage_cell(last.get(i), kind == "measure") for i in ids)
        words = MEASURE_NAME if kind == "measure" else STAGE_NAME
        order = [f"{k} {words[k]}" for k in "54321"] + ["unplaced", "—"]
        o.append(f"- **{kind.capitalize()}s ({len(ids)})**: " + " · ".join(
            f"{k.replace('—', 'no evidence')} {c[k]}" for k in order if c[k]))
    moves = [(i, first.get(i), a) for i, a in last.items()
             if first.get(i) and first[i].get("stage") != a.get("stage")]
    o += ["", "## This month", ""]
    if not moves:
        o.append("No stage moved in August.")
    ind_name = {f["indicator_id"]: f for f in frame}
    for i, j, a in moves:
        f = ind_name[i]
        why = a.get("moved_by", "")
        src = ("a correction to the rubric or a re-read" if why == "reassessed" else
               source_link(why, cat) if ma.src_date(why) and not ma.SOURCE_AT.match(why) else esc(why))
        o.append(f"- **{f['indicator']}**: {stage_cell(j, f['kind'] == 'measure')} → "
                 f"{stage_cell(a, f['kind'] == 'measure')}, on {src}. {esc(a.get('qualifier'))}")
    chapter = None
    for f in frame:
        if f["chapter"] != chapter:
            chapter = f["chapter"]
            o += ["", f"## {chapter}", "", "| Indicator | Jul | Aug | Evidence | Qualifier |",
                  "|---|---|---|---|---|"]
        i, meas = f["indicator_id"], f["kind"] == "measure"
        a, j = last.get(i), first.get(i)
        cur = a or j
        label = f"[{esc(f['indicator'])}](../../maturity/indicators/{i}.md)<br>*{f['kind']}*"
        if cur is None:
            o.append(f"| {label} | — | — | *No evidence* | |")
            continue
        if meas:
            n = natures.get((unit, i, cur.get("value_year", ""), cur.get("value", "")), "")
            ev = measure_evidence(cur, cat, {cur.get("value_source", "")[4:].split("@")[0]: n})
        else:
            ev = row_evidence([x for x in (cur.get("stage_rows") or "").split("|") if x], led, as_at, cat)
        moved = " ▲" if a and j and a.get("stage") != j.get("stage") else ""
        o.append(f"| {label} | {stage_cell(j, meas)} | {stage_cell(a, meas)}{moved} | {ev} | "
                 f"{esc(cur.get('qualifier'))} |")
    o += ["", "*▲ the stage moved in August. Each indicator links to its page across the 54 "
          "countries.*", ""]
    return "\n".join(o)


def render_countries() -> int:
    eds, names, cat, natures = editions(), countries(), catalogue(), ref_natures()
    n = 0
    for unit, name in names.items():
        if unit not in eds[MONTHS[-1]]:
            continue
        led = ma.ledger(REPORTS, unit)
        (REPORTS / unit / f"{unit}-maturity.md").write_text(
            country_page(unit, name, eds, cat, natures, led), encoding="utf-8")
        n += 1
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("what", choices=("indicators", "countries", "all"))
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    if a.what in ("indicators", "all"):
        print(f"{render_indicators()} indicator pages in {OUT_IND.relative_to(CORPUS)}")
    if a.what in ("countries", "all"):
        print(f"{render_countries()} country documents, outputs/reports/{{ISO3}}/{{ISO3}}-maturity.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
