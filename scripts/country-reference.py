#!/usr/bin/env python3
"""country-reference.py — keep `lookups/country-reference.csv` current, every three months.

The table is one row per African country and one column per reference series; its companion
`lookups/country-reference-metadata.csv` has one row per column: `definition`, `url` (the
authoritative origin), `year` (the year the data describes, or the edition), `checked` (the date
the column was last checked against its origin) and `update` — `auto` or `manual`.

**`auto` columns this script refreshes itself**: the World Bank series (API), the inequality
pair (Gini as published, Palma computed from the same survey's income shares), and the fiscal
year start, read from the government budget documents Corpus holds in `budgets/`. It rewrites
those cells and their metadata `year` and `checked`, and prints each cell it changed.

**`manual` columns it cannot read** — treaty deposits, memberships, classifications published as
reports. It prints those overdue, oldest first; `documentation/country-reference.md` is how CC
checks each against its `url` and records the result.

    python scripts/country-reference.py --quarterly   # the cycle's step: nothing inside 90 days
    python scripts/country-reference.py --refresh     # now, regardless
    python scripts/country-reference.py --due         # list overdue columns, change nothing

Also checked, never written: ISO 4217 currency codes and OCHA FTS location ids — a mismatch is
printed for the manual pass. Exit 0 done or not due, 1 a source failed (the cells it would have
written are left as they were).
"""
import argparse, collections, csv, datetime, glob, io, json, os, sys, time, urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "lookups", "country-reference.csv")
META = os.path.join(ROOT, "lookups", "country-reference-metadata.csv")
DUE_DAYS = 90
TODAY = datetime.date.today()
UA = {"User-Agent": "Mozilla/5.0 (corpus reference refresh)"}

# column -> World Bank indicator. The year is the latest one with at least 85% of countries,
# so a column describes one year; a country without that year is blank, not older.
WB = {
    "Population": "SP.POP.TOTL",
    "GDP (current US$)": "NY.GDP.MKTP.CD",
    "GDP per capita (current US$)": "NY.GDP.PCAP.CD",
    "GNI per capita, Atlas (current US$)": "NY.GNP.PCAP.CD",
    "Area (sq km)": "AG.SRF.TOTL.K2",
    "Urban population (%)": "SP.URB.TOTL.IN.ZS",
    "Access to electricity (%)": "EG.ELC.ACCS.ZS",
    "Internet users (%)": "IT.NET.USER.ZS",
    "Mobile subscriptions per 100": "IT.CEL.SETS.P2",
    "Fixed broadband per 100": "IT.NET.BBND.P2",
}
ROUND = {"Population": 0, "GDP (current US$)": 0, "Area (sq km)": 0,
         "GDP per capita (current US$)": 0, "GNI per capita, Atlas (current US$)": 0}
INCOME = {"Low income": "LIC", "Lower middle income": "LMIC", "Upper middle income": "UMIC", "High income": "HIC"}


def fetch(url, binary=False):
    for n in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                b = r.read()
                return b if binary else json.loads(b)
        except Exception as e:  # the World Bank API answers 429 under load
            print(f"  retry {n + 1}: {e}", file=sys.stderr)
            time.sleep(15 * (n + 1))
    raise RuntimeError(f"failed: {url}")


def wb_series(code, iso):
    rows = fetch(f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&date=1990:{TODAY.year}&per_page=20000")[1]
    by = collections.defaultdict(dict)
    for x in rows:
        if x["value"] is not None and x["countryiso3code"] in iso:
            by[int(x["date"])][x["countryiso3code"]] = x["value"]
    time.sleep(3)
    return by


def fmt(v, col):
    if v is None or v == "":
        return ""
    nd = ROUND.get(col, 1)
    return str(int(round(v))) if nd == 0 else f"{v:.{nd}f}"


def read(path):
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write(path, fields, rows):
    with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def overdue(meta):
    late = []
    for m in meta:
        d = datetime.date.fromisoformat(m["checked"]) if m["checked"] else datetime.date.min
        if (TODAY - d).days >= DUE_DAYS:
            late.append((d, m))
    return sorted(late, key=lambda x: x[0])


def refresh(fields, rows, meta):
    iso = {r["ISO-3 Code"]: r for r in rows}
    mrow = {m["column"]: m for m in meta}
    changed, failed = [], False

    def put(col, i, val, year):
        if iso[i].get(col, "") != val:
            changed.append(f"{i} {col}: {iso[i].get(col, '')!r} -> {val!r}")
            iso[i][col] = val
        if col in mrow:
            mrow[col]["year"] = str(year)
            mrow[col]["checked"] = TODAY.isoformat()

    try:
        for col, code in WB.items():
            by = wb_series(code, iso)
            y = max(yr for yr, v in by.items() if len(v) >= 0.85 * len(iso))
            for i in iso:
                put(col, i, fmt(by[y].get(i), col), y)
        meta_rows = fetch("https://api.worldbank.org/v2/country/all?format=json&per_page=400")[1]
        for m in meta_rows:
            if m["id"] in iso:
                put("WB Region", m["id"], m["region"]["value"].strip(), TODAY.year)
                put("WB Income Group", m["id"], INCOME.get(m["incomeLevel"]["value"], m["incomeLevel"]["value"]), TODAY.year)
                put("WB Lending", m["id"], m["lendingType"]["value"], TODAY.year)
        # inequality: the latest survey with a Gini; Palma = top 10% share / bottom 40% share, same survey
        s = {c: wb_series(c, iso) for c in ("SI.POV.GINI", "SI.DST.10TH.10", "SI.DST.FRST.20", "SI.DST.02ND.20")}
        for i in iso:
            ys = sorted((y for y in s["SI.POV.GINI"] if i in s["SI.POV.GINI"][y]), reverse=True)
            if not ys:
                for c in ("Gini index", "Palma ratio", "Inequality survey year"):
                    put(c, i, "", TODAY.year)
                continue
            y = ys[0]
            g = s["SI.POV.GINI"][y][i]
            parts = [s[c].get(y, {}).get(i) for c in ("SI.DST.10TH.10", "SI.DST.FRST.20", "SI.DST.02ND.20")]
            palma = f"{parts[0] / (parts[1] + parts[2]):.2f}" if None not in parts else ""
            put("Gini index", i, f"{g:.1f}", TODAY.year)
            put("Palma ratio", i, palma, TODAY.year)
            put("Inequality survey year", i, str(y), TODAY.year)
    except RuntimeError as e:
        print(f"World Bank: {e}", file=sys.stderr)
        failed = True

    # fiscal year start month: the latest national fiscal year in the country's own budget documents
    for f in glob.glob(os.path.join(ROOT, "budgets", "budgets-[A-Z][A-Z][A-Z].csv")):
        i = os.path.basename(f)[8:11]
        if i not in iso:
            continue
        _, b = read(f)
        starts = sorted(r["fy_start"][:10] for r in b if r.get("fy_start"))
        if starts:
            put("Fiscal year start month", i, str(int(starts[-1][5:7])), int(starts[-1][:4]))

    # checks only: ISO 4217 and OCHA FTS
    try:
        x = ET.fromstring(fetch("https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml", binary=True))
        live = {e.findtext("Ccy") for e in x.iter("CcyNtry")}
        for i, r in iso.items():
            if r["Currency Code"] and r["Currency Code"] not in live:
                print(f"CHECK {i} currency {r['Currency Code']} is no longer an ISO 4217 code")
        fts = {d.get("iso3"): str(d["id"]) for d in fetch("https://api.hpc.tools/v1/public/location")["data"] if d.get("iso3")}
        for i, r in iso.items():
            if fts.get(i) and fts[i] != r["FTS Code"]:
                print(f"CHECK {i} FTS Code {r['FTS Code']} vs FTS {fts[i]}")
    except RuntimeError as e:
        print(f"checks: {e}", file=sys.stderr)

    for c in changed:
        print(c)
    print(f"{len(changed)} cells changed")
    return failed


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--quarterly", action="store_true")
    g.add_argument("--refresh", action="store_true")
    g.add_argument("--due", action="store_true")
    a = ap.parse_args()
    fields, rows = read(TABLE)
    mfields, meta = read(META)
    late = overdue(meta)
    if a.quarterly and not late:
        print("country reference: not due")
        return 0
    failed = False
    if not a.due:
        failed = refresh(fields, rows, meta)
        write(TABLE, fields, rows)
        write(META, mfields, meta)
        late = overdue(meta)
    for d, m in late:
        print(f"DUE {m['column']} — checked {m['checked'] or 'never'} — {m['url']}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
