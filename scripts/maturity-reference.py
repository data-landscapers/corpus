#!/usr/bin/env python3
r"""
maturity-reference.py — the measures' reference figures, pulled into Corpus as data (task C5).

    python scripts/maturity-reference.py            fetch every source, write the two files
    python scripts/maturity-reference.py --only internet-usage,rural-electrification

A measure is assessed for every country. Where the base holds no primary figure it takes the
reference dataset's (`maturity-assessment.md` §4). Most countries have no ledger row for a
figure, so the figures have to be here, as data, before the assessor runs. This script is the one
place they come from.

It writes two files:

- `reference/measures.csv` (`iso3, indicator_id, dataset, value, unit, year, release`):
  one row per country, measure and data year since 2010, read by `maturity-assess.py`.
- `reference/denominators.csv`, the same shape with `indicator_id` naming the series (GDP,
  population), for the compile-derived measures.

**`release` is the provider's own date for the data**: WDI's `lastupdated`, the SDG database's
quarter, UIS's data release, ILOSTAT's `last.update`. Data360 states none, so its release is the
fetch date, which is late and never early. The assessor cites a figure as `ref:{dataset}@{release}`,
and from the first live snapshot a release after the as-at is invisible. The two retrospective
snapshots see everything held (§7).

**What is not here, and why.** Every one of these is a measure that is assessed only where the
base holds a primary; the others are waiting on something named:

- the finance measures are Corpus's own compiles, computed in the assessor's measure pass;
- mobile affordability is waiting on the ITU 5 GB basket (C3 item 7);
- `tech.industry` is waiting on the figure it re-points to (C3 item 8);
- the urban–rural ratio, 9 countries on Data360's ITU copy, is not yet wired;
- SDG 4.4.1: the series is per activity, and the rubric's composite of five skill areas is not
  published;
- data-centre, energy-and-water, bandwidth routes, civil-service literacy and registration have
  no reference that meets their definition.

The API routes and coverage were checked on 2026-09-24 (`maturity-rubric-review.md`, *the
reference vintages*).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parent
OUT = CORPUS / "reference"
COUNTRIES = CORPUS / "lookups" / "countries.csv"
UA = {"User-Agent": "Mozilla/5.0 (Corpus maturity-reference)"}
FIELDS = ("iso3", "indicator_id", "dataset", "value", "unit", "year", "release")
SINCE = 2010

# ISO 3166 numeric (= UN M49) for the 54, which the SDG API keys on.
M49 = {"DZA": 12, "AGO": 24, "BEN": 204, "BWA": 72, "BFA": 854, "BDI": 108, "CPV": 132,
       "CMR": 120, "CAF": 140, "TCD": 148, "COM": 174, "COG": 178, "COD": 180, "CIV": 384,
       "DJI": 262, "EGY": 818, "GNQ": 226, "ERI": 232, "SWZ": 748, "ETH": 231, "GAB": 266,
       "GMB": 270, "GHA": 288, "GIN": 324, "GNB": 624, "KEN": 404, "LSO": 426, "LBR": 430,
       "LBY": 434, "MDG": 450, "MWI": 454, "MLI": 466, "MRT": 478, "MUS": 480, "MAR": 504,
       "MOZ": 508, "NAM": 516, "NER": 562, "NGA": 566, "RWA": 646, "STP": 678, "SEN": 686,
       "SYC": 690, "SLE": 694, "SOM": 706, "ZAF": 710, "SSD": 728, "SDN": 729, "TZA": 834,
       "TGO": 768, "TUN": 788, "UGA": 800, "ZMB": 894, "ZWE": 716}
BY_M49 = {v: k for k, v in M49.items()}


def countries() -> list[str]:
    with open(COUNTRIES, encoding="utf-8-sig", newline="") as fh:
        iso = [r["iso-3"].strip() for r in csv.DictReader(fh) if not r["iso-3"].startswith("X")]
    missing = set(iso) ^ set(M49)
    if missing:
        raise SystemExit(f"countries.csv and the M49 table disagree on {sorted(missing)}")
    return sorted(iso)


def get(url: str, tries: int = 3) -> bytes:
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))
    raise AssertionError


def num(x) -> float | None:
    try:
        return round(float(x), 4)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------- the five providers
# Each returns {(iso3, year): value} and the release date.

def wdi(code: str, iso: list[str]) -> tuple[dict, str]:
    url = (f"https://api.worldbank.org/v2/country/{';'.join(iso)}/indicator/{code}"
           f"?format=json&per_page=20000&date={SINCE}:2030")
    meta, rows = json.loads(get(url))
    out = {}
    for r in rows or []:
        v = num(r["value"])
        if v is not None:
            out[(r["countryiso3code"], int(r["date"]))] = v
    return out, meta["lastupdated"]


_sdg_releases: dict[str, str] = {}


def sdg_release(code: str) -> str:
    """The SDG database's release of a series as the last day of its quarter: `2026.Q2.G.02` is
    2026-06-30, the latest the release can have been published, so it is never claimed early."""
    if not _sdg_releases:
        for s in json.loads(get("https://unstats.un.org/sdgapi/v1/sdg/Series/List?allreleases=false")):
            _sdg_releases[s["code"]] = s.get("release") or ""
    y, q = _sdg_releases[code].split(".")[:2]
    return {"Q1": f"{y}-03-31", "Q2": f"{y}-06-30", "Q3": f"{y}-09-30", "Q4": f"{y}-12-31"}[q]


def sdg(code: str, iso: list[str], want: dict) -> tuple[dict, str]:
    """`want` fixes the dimensions (e.g. {'Sex': 'BOTHSEX'}); any other dimension must be a total."""
    out = {}
    area = "&".join(f"areaCode={M49[i]}" for i in iso)
    d = json.loads(get(f"https://unstats.un.org/sdgapi/v1/sdg/Series/Data?seriesCode={code}"
                       f"&{area}&pageSize=100000"))
    totals = {"ALLAREA", "ALLAGE", "BOTHSEX", "G", "_T"}
    for r in d["data"]:
        dims = r.get("dimensions") or {}
        if any(dims.get(k) != v for k, v in want.items()):
            continue
        if any(v not in totals for k, v in dims.items() if k not in want and k != "Reporting Type"):
            continue
        iso3 = BY_M49.get(int(r["geoAreaCode"]))
        v, y = num(r["value"]), int(float(r["timePeriodStart"]))
        if iso3 and v is not None and y >= SINCE:
            out[(iso3, y)] = v
    return out, sdg_release(code)


def uis(code: str, iso: list[str]) -> tuple[dict, str]:
    q = "&".join(f"geoUnit={i}" for i in iso)
    d = json.loads(get(f"https://api.uis.unesco.org/api/public/data/indicators?indicator={code}&{q}"
                       f"&start={SINCE}"))
    out = {(r["geoUnit"], int(r["year"])): num(r["value"]) for r in d["records"]
           if num(r["value"]) is not None}
    ver = json.loads(get("https://api.uis.unesco.org/api/public/versions/default"))
    edu = next(t for t in ver["themeDataStatus"] if t["theme"] == "EDUCATION")
    m, dd, y = edu["lastUpdate"].split("/")                                  # MM/DD/YYYY
    return out, f"{y}-{m}-{dd}"


def ilo_share(indicator: str, part: str, whole: str, iso: list[str]) -> tuple[dict, str]:
    """A classification's share of the total, per cent: e.g. ISIC J of all employment."""
    raw = get(f"https://rplumber.ilo.org/data/indicator/?id={indicator}&ref_area={'+'.join(iso)}"
              f"&sex=SEX_T&format=.csv").decode("utf-8-sig")
    cells: dict = {}
    for r in csv.DictReader(io.StringIO(raw)):
        if r["classif1"] in (part, whole) and int(r["time"]) >= SINCE and num(r["obs_value"]) is not None:
            # One source per country-year: the first in the file, so a re-run reads the same.
            cells.setdefault((r["ref_area"], int(r["time"]), r["source"]), {})[r["classif1"]] = float(r["obs_value"])
    out = {}
    for (iso3, y, _src), c in sorted(cells.items()):
        if (iso3, y) not in out and part in c and c.get(whole):
            out[(iso3, y)] = round(100 * c[part] / c[whole], 4)
    toc = get("https://rplumber.ilo.org/metadata/toc/indicator/?lang=en&format=.csv").decode("utf-8-sig")
    upd = next(r["last.update"] for r in csv.DictReader(io.StringIO(toc)) if r["id"] == indicator)
    d, m, y = upd.split()[0].split("/")                                     # DD/MM/YYYY
    return out, f"{y}-{m}-{d}"


def d360(indicator: str, database: str, iso: list[str]) -> tuple[dict, str]:
    out = {}
    for i in iso:
        skip = 0
        while True:
            d = json.loads(get(f"https://data360api.worldbank.org/data360/data?DATABASE_ID={database}"
                               f"&INDICATOR={indicator}&REF_AREA={i}&skip={skip}"))
            for r in d["value"]:
                if all(r.get(k) in ("_T", None) for k in ("SEX", "AGE", "URBANISATION",
                                                           "COMP_BREAKDOWN_1", "COMP_BREAKDOWN_2")):
                    y, v = int(r["TIME_PERIOD"][:4]), num(r["OBS_VALUE"])
                    if v is not None and y >= SINCE:
                        out[(i, y)] = v
            skip += len(d["value"])
            if not d["value"] or skip >= d["count"]:
                break
    return out, dt.date.today().isoformat()


# --------------------------------------------------------------------------- the measures
# name: (indicator_id, dataset label, unit, fetch). A label names the definition, not only the
# provider, so a qualifier can say what the figure is.

def gender_gap(iso):
    men, rel = sdg("IT_USE_ii99", iso, {"Sex": "MALE"})
    women, _ = sdg("IT_USE_ii99", iso, {"Sex": "FEMALE"})
    return {k: round(100 * (men[k] - women[k]) / men[k], 4) for k in men if k in women and men[k]}, rel


MEASURES = {
    "internet-usage": ("infra.connect--internet-usage", "wdi-it-net-user", "% of population",
                       lambda iso: wdi("IT.NET.USER.ZS", iso)),
    "mobile-penetration": ("infra.connect--mobile-penetration", "itu-sdg-5b1-mobile-ownership-10plus",
                           "% of people 10+", lambda iso: sdg("IT_MOB_OWN", iso, {"Sex": "BOTHSEX"})),
    "rural-electrification": ("infra.energy--rural-electrification", "wdi-elc-accs-rural",
                              "% of rural population", lambda iso: wdi("EG.ELC.ACCS.RU.ZS", iso)),
    "grid-reliability": ("infra.energy--grid-reliability", "enterprise-surveys-outages",
                         "outages per month", lambda iso: d360("WB_ES_T_BREADY_IN2", "WB_ES", iso)),
    "population-uptake": ("dpi.pay--population-uptake", "findex-account-ownership",
                          "% of adults 15+", lambda iso: wdi("FX.OWN.TOTL.ZS", iso)),
    "secondary-internet": ("capacity.training--dt-related-training-in-secondary-education",
                           "uis-4a1-secondary-internet", "% of secondary schools",
                           lambda iso: uis("SCHBSP.2T3.WINTERN", iso)),
    "stem-graduates": ("capacity.training--dt-related-university-facilities-and-qualifications",
                       "uis-stem-graduates", "% of tertiary graduates",
                       lambda iso: uis("FOSGP.5T8.F500600700", iso)),
    "ict-employment": ("capacity.training--graduates-entering-dt-ecosystem", "ilostat-isic-j-employment",
                       "% of employment", lambda iso: ilo_share("EMP_TEMP_SEX_ECO_NB_A", "ECO_ISIC4_J",
                                                                "ECO_ISIC4_TOTAL", iso)),
    "gender-gap": ("include.access--gender-equity", "itu-internet-use-gender-gap",
                   "% gap, men over women", gender_gap),
}
DENOMINATORS = {
    "gdp": ("gdp-current-usd", "wdi-gdp", "US$", lambda iso: wdi("NY.GDP.MKTP.CD", iso)),
    "population": ("population", "wdi-population", "persons", lambda iso: wdi("SP.POP.TOTL", iso)),
}


def pull(table: dict, only: set[str], iso: list[str]) -> list[dict]:
    rows = []
    for name, (iid, dataset, unit, fetch) in table.items():
        if only and name not in only:
            continue
        values, release = fetch(iso)
        for (iso3, year), v in sorted(values.items()):
            rows.append({"iso3": iso3, "indicator_id": iid, "dataset": dataset, "value": f"{v:g}",
                         "unit": unit, "year": year, "release": release})
        n = len({k[0] for k in values})
        print(f"  {name}: {len(values)} figures, {n} countries, released {release}")
    return rows


def write(path: Path, rows: list[dict], only: set[str], table: dict) -> None:
    """Rewrite the file, keeping the rows of any source not fetched this run.

    **A figure already held at the same value keeps its first release date.** It was known from
    then. And a re-fetch that re-dated it would make an unchanged figure read as a new one, which
    the stability rule would then treat as a dated cause."""
    kept, before = [], {}
    if path.exists():
        redone = {table[n][0] for n in (only or table) if n in table}
        with open(path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                before[(r["iso3"], r["indicator_id"], r["dataset"], r["year"], r["value"])] = r["release"]
                if r["indicator_id"] not in redone:
                    kept.append(r)
    for r in rows:
        k = (r["iso3"], r["indicator_id"], r["dataset"], str(r["year"]), r["value"])
        if k in before and before[k] < r["release"]:
            r["release"] = before[k]
    rows = sorted(kept + rows, key=lambda r: (r["indicator_id"], r["iso3"], int(r["year"])))
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", default="", help="comma-separated source names")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    iso = countries()
    print("measures")
    write(OUT / "measures.csv", pull(MEASURES, only, iso), only, MEASURES)
    print("denominators")
    write(OUT / "denominators.csv", pull(DENOMINATORS, only, iso), only, DENOMINATORS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
