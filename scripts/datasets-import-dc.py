"""datasets-import-dc.py — T2: take the v2 Data Centres file into Corpus as the master. One-off.

Reads prep/data-centres.csv (the file behind the June 2026 v2 post), migrates its header to
outputs/datasets/data-centres/metadata.csv through `v2_name`, normalises values to the metadata's
allowed sets, and writes the master. The normalisations change form, never fact: each rule is
below, and the log's import row counts what each touched. Anything that would need a source read
to fix is left as it stands and listed in documentation/datasets.md for T6.

Refuses to run if the master already exists — after T2 the master is edited, never re-imported.
"""
import collections, csv, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import datasets_lib as dl
import importlib.util

_spec = importlib.util.spec_from_file_location("mojibake", pathlib.Path(__file__).with_name("lint-mojibake.py"))
mojibake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mojibake)

NAME = "data-centres"
SRC = dl.ROOT / "prep" / "data-centres.csv"

# ultimate_parent_hq_country: names to ISO3, `|`-joined where control is joint.
HQ = {
    "Angola": "AGO", "Benin": "BEN", "Botswana": "BWA", "Burkina Faso": "BFA", "Burundi": "BDI",
    "Cabo Verde": "CPV", "Cameroon": "CMR", "Chad": "TCD", "Comoros": "COM",
    "Cote d'Ivoire": "CIV", "DR Congo": "COD", "Djibouti": "DJI", "Equatorial Guinea": "GNQ",
    "Eswatini": "SWZ", "Ethiopia": "ETH", "France": "FRA", "Gambia": "GMB", "Germany": "DEU",
    "Ghana": "GHA", "Guinea": "GIN", "India": "IND", "Japan": "JPN", "Jersey": "JEY",
    "Kenya": "KEN", "Liberia": "LBR", "Madagascar": "MDG", "Malawi": "MWI", "Mali": "MLI",
    "Mauritania": "MRT", "Mauritius": "MUS", "Morocco": "MAR", "Mozambique": "MOZ",
    "Namibia": "NAM", "Nigeria": "NGA", "Republic of Congo": "COG", "Rwanda": "RWA",
    "Senegal": "SEN", "Singapore": "SGP", "Somalia": "SOM", "South Africa": "ZAF", "Spain": "ESP",
    "Sudan": "SDN", "Switzerland": "CHE", "Tanzania": "TZA", "Togo": "TGO", "UAE": "ARE",
    "Dubai": "ARE", "UK": "GBR", "USA": "USA", "Uganda": "UGA", "Zambia": "ZMB", "Zimbabwe": "ZWE",
    "N/A (jointly controlled by US and France-based entities)": "USA|FRA",
    # North Africa, from the first version (datasets-import-dc-v1.py).
    "Algeria": "DZA", "Croatia": "HRV", "Egypt": "EGY", "Libya": "LBY", "Qatar": "QAT", "Tunisia": "TUN",
}

# Exact-value renames, per column. Spelling and form only.
VALUES = {
    "expansion_plans": {"Actiive (under construction)": "Under construction"},
    "govt_data_hosted": {"Designated national/government data centre": "Designated national / government data centre"},
    "hyperscaler_presence": {"TRUE": "Yes", "FALSE": "No"},
    "hyperscaler_microsoft": {"": "No"}, "hyperscaler_aws": {"": "No"}, "hyperscaler_google": {"": "No"},
    "chinese_involvement": {"": "None identified"},
    "dfi_involvement": {"None found": "None identified"},
    "hyperscaler_relationships": {"None found": "None identified"},
    # The bracketed gloss is the metadata's job, not every row's.
    "foreign_dependency_score": {
        "Low (domestic ownership, open source stack, local compliance)": "Low",
        "Moderate (mixed ownership or stack)": "Moderate",
        "High (foreign ownership, proprietary stack, CLOUD Act exposure)": "High"},
}

# A markdown link or a bare URL, whichever comes next, so the cell's order survives.
# A URL may hold balanced brackets (Wikipedia's `Unitel_(Angola)`); the first version stopped at
# the first `)` and cut six URLs short (repaired 2026-09-21; see logs/dataset-updates.csv).
_URL = r"https?://(?:[^\s;,()\[\]\"]|\([^()\s]*\))+"
LINK = re.compile(r"\[[^\]]*\]\((" + _URL + r")\)|(" + _URL + r")")


def urls(cell):
    """Bare URLs from a cell mixing plain URLs and markdown links, in order, deduplicated."""
    found = [a or b for a, b in LINK.findall(cell)]
    seen, out = set(), []
    for u in found:
        u = u.rstrip(".")
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def main():
    if dl.master_path(NAME).exists():
        sys.exit(f"{dl.master_path(NAME)} exists: the master is edited now, not re-imported.")
    meta = dl.metadata(NAME)
    rename = {(m["v2_name"] or m["column"]): m["column"] for m in meta if m["v2_name"] != "(new)"}
    with open(SRC, encoding="utf-8", newline="") as f:
        v2 = list(csv.DictReader(f))
    touched = collections.Counter()
    rows = []
    for old in v2:
        r = {rename[k]: (v or "").strip() for k, v in old.items() if k in rename}
        for c in r:  # v2 carries UTF-8 read once as cp1252 (PÃºblica); lint-mojibake's inverse is exact
            fixed, hits = mojibake.repair(r[c])
            if hits:
                r[c] = fixed
                touched["mojibake"] += 1
        for col, table in VALUES.items():
            if r[col] in table:
                r[col] = table[r[col]]
                touched[col] += 1
        hq = r["ultimate_parent_hq_country"]
        if hq:
            parts = [hq] if hq in HQ else [p.strip() for p in hq.split("/")]
            r["ultimate_parent_hq_country"] = "|".join(
                dict.fromkeys(c for part in parts for c in HQ[part].split("|")))
            touched["ultimate_parent_hq_country"] += 1
        # source_urls is every source the row rests on (metadata.csv), so the citations inside
        # other cells join it, after the row's own list. In v2 they were half of all URLs.
        u = "; ".join(dict.fromkeys(urls(r["source_urls"]) + [
            x for c in r if c != "source_urls" for x in urls(r[c])]))
        if u != r["source_urls"]:
            touched["source_urls"] += 1
        r["source_urls"] = u
        r["raw_slugs"] = r["last_verified"] = ""
        rows.append(r)
    problems = dl.check(NAME, rows)
    if problems:
        sys.exit("values outside metadata:\n  " + "\n  ".join(problems))
    dl.write(NAME, rows)
    n_urls = len({u for r in rows for u in r["source_urls"].split("; ") if u})
    detail = (f"Imported {len(rows)} facilities from the v2 dataset (data-landscapers.io, 2026-06-10); "
              f"{n_urls} distinct source URLs, citations in other cells now listed in source_urls too. Header migrated to metadata.csv; ownership chain and "
              f"chinese_role dropped as copies of other columns. Values normalised in form only: "
              + ", ".join(f"{c} {n}" for c, n in sorted(touched.items())) + ".")
    dl.log(NAME, "ALL", "import", detail,
           "https://data-landscapers.io/lab/2026/06/10/africa-data-centres-v2/")
    print(detail)


if __name__ == "__main__":
    main()
