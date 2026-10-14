#!/usr/bin/env python3
r"""study-datacentres-carry.py — Corpus's data centres dataset, carried into the datacentres study.

    cd scripts/.workroot
    python scripts/study-datacentres-carry.py
    python scripts/study-datacentres-carry.py --dry

`maturity/documentation/maturity-study-method.md` §4: **start from what is already paid
for**, as `study-nonstate-carry.py` does for the finance tables. The frame's cells for
`infra.store--local-data-centre-capacity-all-providers` were read from
`outputs/datasets/data-centres/data-centres.csv`, so its facilities answer questions 1 to 3
of `maturity-study-datacentres.md` with no drafter reading them.

**The dataset is not a source a study may cite**: `lint-study.py` holds every source to
`raw/`. So a facility's fact is filed under one of the held documents its `raw_slugs` names,
and only one whose body names the operator or the facility, which is a string match and not
a reading:

- a facility `Operational` and `Colocation/carrier-neutral` or `Hyperscale` gives `centre` =
  `service`;
- `tier3` instead where the dataset gives it Tier III or IV **and** the chosen document's
  body states a Tier III or IV. The fact says whether the dataset has the Tier certified or
  stated by the operator.

**The fact is dated by the document's `published`**, which is the latest date the document
can show the facility at. A document the study's terms already listed is left to its
drafter, who reads more in it than this can; only documents no list holds are carried, and
are appended to `readlist.csv` as `why = carried`; one listed in a pass no drafter reads
keeps its number. A facts file already there is left alone.

Run it after `study-select.py` and before the drafters.

Exit: 0 written, 2 the study or the index cannot be read.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402
import vault_lib  # noqa: E402

STUDY = "datacentres"
SUB, CLASS = "datacentre", "datacentre"
TABLE = os.path.join(study_lib.CORPUS, "outputs", "datasets", "data-centres", "data-centres.csv")
TYPES = ("Colocation/carrier-neutral", "Hyperscale")
TIER = re.compile(r"\btier[\s-]*(iii|iv|3|4)\b", re.I)
CERTIFIED = re.compile(r"uptime[^;]*tier\s*(iii|iv|3|4)|tia-?942[^;]*(rated[\s-]*)?(3|4|iii|iv)", re.I)
# Words of an operator's name too common to show a document is about it.
COMMON = {"data", "centre", "center", "centres", "centers", "dc", "the", "group", "limited", "ltd",
          "s.a.", "sa", "plc", "telecom", "telecoms", "africa", "african", "cloud", "digital",
          "national", "technologies", "services", "networks", "company", "of", "and", "de", "du"}


def names(r: dict) -> list[str]:
    """The strings whose presence in a body shows it names this facility or its operator."""
    out = []
    for field in ("operator_name", "facility_name"):
        head = re.split(r"[(\[,;]", r[field])[0].strip()
        words = [w for w in head.split() if w.lower() not in COMMON and len(w) > 2]
        if words:
            out.append(" ".join(words[:2]))
    return out


def tier_of(r: dict) -> str:
    """`certified`, `stated` or '' for the dataset's own record of the facility's Tier."""
    certs, comments = r["security_certifications"], r["comments"]
    if CERTIFIED.search(certs):
        return "certified"
    if TIER.search(certs) or TIER.search(comments):
        return "stated"
    return ""


def body(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Carry the data centres dataset into the datacentres study.")
    ap.add_argument("--dry", action="store_true", help="print the counts, write nothing")
    a = ap.parse_args(argv)
    try:
        study_lib.load(STUDY)
        index = {row["d"]["slug"]: row for row in vault_lib.load_index()
                 if row["d"].get("folder") == "raw" and row["d"].get("ext") == ".md"}
    except (study_lib.StudyError, vault_lib.ForeignIndex, vault_lib.EmptyIndex) as e:
        print(f"study-datacentres-carry: {e}")
        return 2
    with open(TABLE, encoding="utf-8-sig", newline="") as fh:
        table = [r for r in csv.DictReader(fh)
                 if r["operational_status"] == "Operational" and r["facility_type"] in TYPES]
    base = os.path.join(study_lib.study_dir(STUDY), "evidence")
    count: collections.Counter = collections.Counter()
    by_iso = collections.defaultdict(list)
    for r in table:
        by_iso[r["country"]].append(r)
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "readlist.csv")
        mine = study_lib.read_csv(path)
        listed = {r["slug"] for r in mine if r.get("kind") == "raw" and r.get("pass") in ("about", "0")}
        n_of = {r["slug"]: str(r["n"]) for r in mine if r.get("kind") == "raw"}
        by_slug: dict[str, list[dict]] = collections.defaultdict(list)
        for r in by_iso.get(iso, ()):
            count["facilities"] += 1
            tier = tier_of(r)
            chosen, chosen_tier = "", False
            for slug in sorted((s.strip() for s in r["raw_slugs"].split(";") if s.strip()),
                               key=lambda s: str(index.get(s, {}).get("fm", {}).get("published", "")),
                               reverse=True):
                if slug not in index or slug in listed:
                    continue
                text = body(index[slug]["path"])
                if not any(n.lower() in text.lower() for n in names(r)):
                    continue
                has_tier = bool(tier and TIER.search(text))
                if not chosen or (has_tier and not chosen_tier):
                    chosen, chosen_tier = slug, has_tier
                if chosen_tier or not tier:
                    break
            if not chosen:
                count["no document"] += 1
                continue
            fm = index[chosen]["fm"]
            published = str(fm.get("published", "") or "")[:10]
            if not study_lib.AS_OF.match(published):
                count["undated"] += 1
                continue
            value = "tier3" if chosen_tier else "service"
            how = {"certified": "certified by the Uptime Institute or TIA-942",
                   "stated": "on the operator's own statement"}.get(tier, "")
            text = (f"Data centres dataset: {r['facility_name']} ({r['operator_name']}), "
                    f"{r['facility_type'].lower()}, in service"
                    + (f", Tier III or above {how}" if value == "tier3" else "")
                    + f"; this document names it (published {published}).")
            by_slug[chosen].append({"sub_indicator": SUB, "aspect": "centre", "value": value,
                                    "fact": text, "as_of": published,
                                    "date_precision": "day" if len(published) == 10 else "month",
                                    "system": r["facility_name"], "class": CLASS})
            count[value] += 1
        nxt = max([int(r["n"]) for r in mine if str(r.get("n") or "").isdigit()] or [0])
        new_rows = []
        for slug in sorted(by_slug):
            if slug not in n_of:
                nxt += 1
                d, fm = index[slug]["d"], index[slug]["fm"]
                new_rows.append({"n": nxt, "slice": "", "pass": "carried", "tier": "", "iso3": iso,
                                 "kind": "raw", "slug": slug, "read": "", "path": index[slug]["path"],
                                 "url": fm.get("url", ""), "title": fm.get("title", ""),
                                 "published": str(fm.get("published", "")), "places": iso,
                                 "why": "carried", "terms": "", "hits": 0, "words": d.get("words", 0)})
                n_of[slug] = str(nxt)
            out = os.path.join(base, iso, "facts", f"{n_of[slug]}.json")
            count["documents"] += 1
            if a.dry or os.path.exists(out):
                continue
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8", newline="\n") as fh:
                json.dump({"slug": slug, "facts": by_slug[slug], "systems": [],
                           "note": "carried from outputs/datasets/data-centres; no document opened"},
                          fh, ensure_ascii=False, indent=1)
                fh.write("\n")
        if new_rows:
            count["countries"] += 1
            if not a.dry:
                study_lib.write_csv(path, study_lib.READLIST_FIELDS, mine + new_rows)
    print("study-datacentres-carry: " + ", ".join(
        f"{k}: {count[k]}" for k in ("facilities", "countries", "documents", "service", "tier3",
                                     "no document", "undated"))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
