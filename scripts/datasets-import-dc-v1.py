"""datasets-import-dc-v1.py — bring the North African rows back from the first version. One-off.

The first Data Centres file on the main site (data-landscapers.io/assets/data/data-centres.csv,
saved to prep/data-centres-v1.csv) held 378 rows. v2 kept 306 of them, all with the same IDs and
names, and dropped Egypt, Morocco, Algeria, Tunisia and Libya (71 rows) and ETH-009 (Deep Water
Cloud Ethiopia). v2 dropping ETH-009 is taken as a decision, so it stays out and its ID stays retired.

The 71 rows go through the T2 import's normalisation (datasets-import-dc.py), with two differences:

- **v1 has no control_* columns.** Its `sovereignty_category` was replaced in v2 by a reassessed
  `control_category`, and the two disagree too often to map one onto the other. So control is
  derived from `ultimate_parent_hq_country` by the rule below (84% agreement with v2's
  judgements on the 289 rows where both exist), with `control_confidence` blank and a rationale
  saying so. T6 assesses them like every other row.
- `chinese_involvement` "None" becomes "None identified", the form the metadata allows.

Each row is logged as an `add`.
"""
import csv, importlib.util, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import datasets_lib as dl  # noqa: E402

_spec = importlib.util.spec_from_file_location("imp", HERE / "datasets-import-dc.py")
imp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(imp)

NAME = "data-centres"
SRC = dl.ROOT / "prep" / "data-centres-v1.csv"
V1_URL = "https://data-landscapers.io/assets/data/data-centres.csv"
NORTH = {"EGY", "MAR", "DZA", "TUN", "LBY"}
AFRICA = {r["iso-3"] for r in csv.DictReader(open(dl.ROOT / "lookups" / "countries.csv", encoding="utf-8-sig"))
          if not r["iso-3"].startswith("X")}


def control(hq: str) -> str:
    c = [x for x in hq.split("|") if x]
    if not c:
        return ""
    african = [x in AFRICA for x in c]
    if all(african):
        return "African control"
    if any(african):
        return "Joint African/foreign control"
    return "US control" if "USA" in c else "Other foreign control"


def main():
    meta = dl.metadata(NAME)
    rename = {(m["v2_name"] or m["column"]): m["column"] for m in meta if m["v2_name"] != "(new)"}
    have = dl.read(NAME)
    ids = {r["facility_id"] for r in have}
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        v1 = [r for r in csv.DictReader(f) if r["country"] in NORTH]
    if any(r["facility_id"] in ids for r in v1):
        sys.exit("some North African IDs are already in the master: this has been run")
    added = []
    for old in v1:
        r = {rename[k]: (v or "").strip() for k, v in old.items() if k in rename}
        for c in r:
            r[c] = imp.mojibake.repair(r[c])[0]
        for col, table in imp.VALUES.items():
            if col in r and r[col] in table:
                r[col] = table[r[col]]
        if r["chinese_involvement"] == "None":
            r["chinese_involvement"] = "None identified"
        hq = r["ultimate_parent_hq_country"]
        if hq:
            parts = [hq] if hq in imp.HQ else [p.strip() for p in hq.split("/")]
            r["ultimate_parent_hq_country"] = "|".join(
                dict.fromkeys(c for part in parts for c in imp.HQ[part].split("|")))
        r["source_urls"] = "; ".join(dict.fromkeys(imp.urls(r["source_urls"]) + [
            x for c in r if c != "source_urls" for x in imp.urls(r[c])]))
        r["hyperscaler_presence"] = "Yes" if "Yes" in (
            r["hyperscaler_microsoft"], r["hyperscaler_aws"], r["hyperscaler_google"]) else "No"
        cat = control(r["ultimate_parent_hq_country"])
        r["control_category"] = cat
        r["control_confidence"] = ""
        r["control_rationale"] = (f"Provisional: derived from the ultimate parent's country "
                                  f"({r['ultimate_parent_hq_country'] or 'unknown'}); not yet assessed"
                                  if cat else "Not yet assessed: ultimate parent unknown")
        r["raw_slugs"] = r["last_verified"] = ""
        added.append(r)
    rows = have + added
    rows.sort(key=lambda r: (r["country"], r["facility_id"]))
    problems = dl.check(NAME, rows)
    if problems:
        sys.exit(f"{len(problems)} values outside metadata, e.g.:\n  " + "\n  ".join(problems[:15]))
    dl.write(NAME, rows)
    for r in reversed(added):
        dl.log(NAME, r["facility_id"], "add",
               f"{r['facility_name']} ({r['country_name']}) restored from the first version of the dataset, "
               f"which v2 had dropped with the rest of North Africa. Control is provisional until assessed.",
               V1_URL)
    print(f"added {len(added)} facilities: " + ", ".join(
        f"{c} {sum(1 for r in added if r['country'] == c)}" for c in sorted(NORTH)))


if __name__ == "__main__":
    main()
