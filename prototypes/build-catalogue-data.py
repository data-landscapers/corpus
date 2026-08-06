#!/usr/bin/env python3
"""build-catalogue-data.py — the prototype's data file. *bespoke*

Rewrites `site/catalogue-data.js` from `outputs/catalogue/raw-catalogue.json`,
trimmed to the ten fields the browse surface actually uses and packed as arrays
rather than objects (2.8 MB against the catalogue's 5.9 MB).

Run it after any `scripts/build-catalogue.py`, or the prototype goes stale.
Delete both when the real site build lands — this is scaffolding for design
work, not a standing part of the pipeline.

  python site/build-catalogue-data.py
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "catalogue-data.js")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def vocab():
    places, regions = {}, {}
    with open(os.path.join(ROOT, "lookups", "countries.csv"), encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            places[r["iso-3"]] = r["country-name"]
            regions[r["iso-3"]] = r.get("Region") or ""
    topics, cats, cat = {}, {}, None
    with open(os.path.join(ROOT, "lookups", "taxonomy.md"), encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^###\s+(.+)$", line.strip())
            if m:
                cat = m.group(1).strip()
                continue
            m = re.match(r"^-\s+`([a-z0-9.]+)`\s+—\s+(.+)$", line.strip())
            if m and cat:
                topics[m.group(1)] = m.group(2).strip()
                cats[m.group(1)] = cat
    return places, regions, topics, cats


def main():
    src = os.path.join(ROOT, "outputs", "catalogue", "raw-catalogue.json")
    d = json.load(open(src, encoding="utf-8"))
    items = d["items"] if isinstance(d, dict) and "items" in d else d

    rows = [[
        i.get("title") or "",
        i.get("publisher") or "",
        (i.get("published") or "")[:10],
        i.get("places") or [],
        i.get("topics") or [],
        i.get("lens") or [],
        i.get("url") or "",
        i.get("slug") or "",
        1 if i.get("artefact") else 0,
        i.get("body_completeness") or "",
    ] for i in items]
    rows.sort(key=lambda r: r[2], reverse=True)

    places, regions, topics, cats = vocab()
    payload = {"places": places, "regions": regions, "topics": topics,
               "cats": cats, "rows": rows}
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("window.CATALOGUE = ")
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";")
    print(f"{len(rows):,} records -> site/catalogue-data.js "
          f"({os.path.getsize(OUT) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
