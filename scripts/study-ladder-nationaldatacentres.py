#!/usr/bin/env python3
r"""study-ladder-nationaldatacentres.py — the national data centres study's four questions, counted.

    python scripts/study-ladder-nationaldatacentres.py --as-at 2026-09-30
    python scripts/study-ladder-nationaldatacentres.py --as-at 2026-09-30 --dry
    python scripts/study-ladder-nationaldatacentres.py --as-at 2026-09-30 --show KEN

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-datacentres.py` does it.
The ladder is `maturity-study-nationaldatacentres.md` §2 and §3, and no question has a window.
**A facility is national** where the newest `owner` fact on it says so, or, with none, where
`maturity/nationaldatacentres/owners.csv` (the parent's reading, method §7.2) marks the owner
`systems.csv` gives it; an owner the table leaves blank counts for neither side.

1. **A national data centre for hire**: a `centre` row of `service`, `tier3` or `two` on a
   national facility. A carried `two` names one facility, so it counts as `tier3` here.
2. **Tier III**: a `centre` row of `tier3` or `two` on a national facility.
3. **Two at Tier III**: two such facilities whose names differ once the generic words go.
4. **The state's data**: a `state` row of `hosted` on a national facility, not reversed by a
   later `none`. Stage 5 needs 3 and 4.

A `centre` of `none` dated after every positive row and inside three years sets stage 1. A
fact dated after the as-at sets nothing; a year or a month stands for its last day, and the
as-at's own year for the as-at. `corrections.csv` is applied to `evidence.csv` first, once.
Writes each `stage.json` and `ladder-test.csv`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

STUDY = "nationaldatacentres"
GAPS = {
    "5": "",
    "4": "No source found says the government hosts its own data in a nationally owned data "
         "centre in the country.",
    "3": "No source found names a second nationally owned data centre for hire at Tier III or above.",
    "2": "No source found says a nationally owned data centre for hire is Tier III or above.",
    "1": "",
}
NOISE = re.compile(r"\b(data|centres?|centers?|datacenters?|datacentres?|dc|the|campus|facility|tier|"
                   r"iii|iv|3|4|de|du|d|l|la|le|s\.?a|ltd|limited|plc|national|nationale?)\b", re.I)

# The parent's reading (method §7.2): names of one facility, folded, so question 3 counts it once.
SAME = {
    "camtel": ("camtel", "zamengoe"),
    "mauritiustelecom": ("mauritiustelecom", "rosebelle"),
    "kalaakebira": ("orangetunisiekalaa", "kalaakebira"),
    "digitalparksafrica": ("digitalparksafrica",),
    "21stcentury": ("21stcentury",),
    "galaxy": ("galaxy",),
    # TelOne's pages call a Tier 3 facility "its data centre" without naming it: counted once.
    "telone": ("telone", "mazowe"),
    "diamniadio": ("diamniadio", "adie"),
    "lome": ("lome", "socinfrastructuresnum"),
    "nouakchott": ("nouakchott",),
    "bofinet": ("digitaldelta", "bofinet"),
    "konza": ("konza",),
}


# The parent's reading of who owns a facility a `state` row names and `systems.csv` gives no
# owner for: each is run by the state or a state agency.
STATE_RUN = {
    "BFA": ("G-Cloud", "modular"), "CPV": ("NOSi",), "DZA": ("National Digital Services Centre",),
    "GHA": ("National Data Centre", "NITA"), "KEN": ("KONZA",), "MLI": ("National Data Centre", "AGETIC"),
    "MWI": ("National Data Centre",), "UGA": ("National Data Centre", "existing data center"),
    "ZAF": ("SITA",), "ZWE": ("ZCHPC", "High Performance Computing"),
}


def facility_key(system: str) -> str:
    name = re.sub(r"\(.*?\)", "", study_lib.fold(system or "")).lower()
    key = re.sub(r"[^a-z0-9]", "", NOISE.sub("", name))
    for k, starts in SAME.items():
        if any(key.startswith(s) for s in starts):
            return k
    return key


def last_day(as_of: str) -> dt.date:
    p = [int(x) for x in as_of.split("-")]
    if len(p) == 1:
        return dt.date(p[0], 12, 31)
    if len(p) == 2:
        return dt.date(p[0], p[1], calendar.monthrange(p[0], p[1])[1])
    return dt.date(*p)


def correct(rows: list[dict], fixes: list[dict]) -> tuple[list[dict], int]:
    by_id = {f"{f['iso3']}-{f['n']}": f for f in fixes}
    out, changed = [], 0
    for r in rows:
        f = by_id.get(r["row_id"])
        if f and f["action"] == "removed":
            changed += 1
            continue
        if f and f["action"].startswith("revalued: ") and r["value"] != f["action"].split(": ", 1)[1]:
            r, changed = {**r, "value": f["action"].split(": ", 1)[1]}, changed + 1
        out.append(r)
    return out, changed


def owners_of(iso: str, systems: list[dict], table: dict) -> dict[str, str]:
    """`{system: yes|no}` from the owners `systems.csv` names and the parent's table."""
    votes: dict[str, list[str]] = {}
    for s in systems:
        v = table.get((iso, s.get("owner", "")), "")
        if v:
            votes.setdefault(s["system"], []).append(v)
    out = {}
    for name, vs in votes.items():
        out[name] = "yes" if vs.count("yes") > vs.count("no") else "no"
    for s in systems:
        if s["system"] not in out and any(k.lower() in s["system"].lower() for k in STATE_RUN.get(iso, ())):
            out[s["system"]] = "yes"
    return out


def by_name(iso: str, system: str, table: dict) -> str:
    """A facility `systems.csv` gives no owner for, read from an owner's name inside its own:
    `N+One second data center` is N+One's. The longest owner name found wins."""
    name = study_lib.fold(system or "").lower()
    best = ("", "")
    for (i, owner), v in table.items():
        key = study_lib.fold(re.sub(r"\(.*?\)", "", owner)).lower().strip()
        if i == iso and v and len(key) >= 4 and re.search(r"\b" + re.escape(key) + r"\b", name) \
                and len(key) > len(best[0]):
            best = (key, v)
    return best[1]


CARRIED = re.compile(r"^Data centres dataset: (.+?) \((.+)\), ")
DATASET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "datasets", "data-centres", "data-centres.csv")
NATIONAL_TYPES = {"Government / SOE", "Private domestic", "Joint venture (majority domestic)", "PPP"}


def load_dataset() -> dict:
    """`{(iso, facility): yes|no}` from the data centres dataset's `ownership_type`."""
    out = {}
    for d in study_lib.read_csv(DATASET):
        t = d.get("ownership_type", "")
        if t and t != "Unknown":
            out[(d["country"], d["facility_name"])] = "yes" if t in NATIONAL_TYPES else "no"
    return out


def fallback(iso: str, rows: list[dict], owned: dict, table: dict, dataset: dict) -> dict:
    """Owners for facilities `systems.csv` does not give one: an owner's name inside the
    facility's own (`by_name`), and for a fact `study-datacentres-carry.py` carried, the owner it
    names in brackets, read against the parent's table and then the dataset's `ownership_type`."""
    out = {}
    for r in rows:
        if r["system"] in owned or r["system"] in out:
            continue
        m = CARRIED.match(r["fact"])
        v = by_name(iso, r["system"], table)
        if not v and m:
            v = by_name(iso, m.group(2), table) or dataset.get((iso, m.group(1)), "")
        if v:
            out[r["system"]] = v
    return out


def stage(rows: list[dict], as_at: dt.date, owned: dict[str, str], iso: str = "") -> dict:
    day = lambda a: as_at if a == str(as_at.year) else last_day(a)  # noqa: E731
    live = [(day(r["as_of"]), r) for r in rows if day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    if not rows:
        return {"stage": "no evidence", "sources": [],
                "gaps": "Nothing found names a data centre for hire, or says there is none."}
    said = {}
    for _, r in live:                      # newest first: the first owner fact stands
        if r["aspect"] == "owner":
            said.setdefault(r["system"], "yes" if r["value"] == "national" else "no")
    national = lambda r: said.get(r["system"], owned.get(r["system"])) == "yes"  # noqa: E731
    three = study_lib.months_back(as_at, 36)
    service = [(d, r) for d, r in live if r["aspect"] == "centre"
               and r["value"] in ("service", "tier3", "two") and national(r)]
    none = [(d, r) for d, r in live if r["aspect"] == "centre" and r["value"] == "none" and d >= three]
    if none and (not service or none[0][0] > service[0][0]):
        return {"stage": "1", "sources": [none[0][1]["row_id"]], "gaps": ""}
    if not service:
        return {"stage": "unplaced", "sources": [],
                "gaps": "No source found says a data centre for hire in the country is nationally "
                        "owned, and none dated in the last three years says there is none."}
    tier = [(d, r) for d, r in service if r["value"] in ("tier3", "two")]
    seen: dict[str, str] = {}
    for _, r in tier:
        seen.setdefault(facility_key(r["system"]), r["row_id"])
    run = lambda r: any(k.lower() in r["system"].lower() for k in STATE_RUN.get(iso, ()))  # noqa: E731
    hosted = [(d, r) for d, r in live if r["aspect"] == "state" and r["value"] == "hosted"
              and (national(r) or run(r))]
    gone = [(d, r) for d, r in live if r["aspect"] == "state" and r["value"] == "none"]
    if hosted and gone and gone[0][0] > hosted[0][0]:
        hosted = []
    s, src = "2", [service[0][1]["row_id"]]
    if tier:
        s, src = "3", [tier[0][1]["row_id"]]
        if len(seen) >= 2:
            s, src = "4", list(seen.values())[:2]
            if hosted:
                s, src = "5", src + [hosted[0][1]["row_id"]]
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the national data centres study from its answers.")
    ap.add_argument("--as-at", required=True)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--show", help="print one country's national facilities and its cell")
    a = ap.parse_args(argv)
    try:
        study_lib.load(STUDY)
    except study_lib.StudyError as e:
        print(f"study-ladder: {e}")
        return 2
    as_at = dt.date.fromisoformat(a.as_at)
    here = study_lib.study_dir(STUDY)
    base = os.path.join(here, "evidence")
    fixes = study_lib.read_csv(os.path.join(here, "corrections.csv"))
    table = {(r["iso3"], r["owner"]): r["national"]
             for r in study_lib.read_csv(os.path.join(here, "owners.csv"))}
    dataset = load_dataset()
    test, count = [], {}
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "evidence.csv")
        rows, changed = correct(study_lib.read_csv(path), [f for f in fixes if f["iso3"] == iso])
        if changed and not a.dry and not a.show:
            study_lib.write_csv(path, study_lib.EVIDENCE_FIELDS, rows)
        owned = owners_of(iso, study_lib.read_csv(os.path.join(base, iso, "systems.csv")), table)
        owned.update(fallback(iso, rows, owned, table, dataset))
        cell = stage(rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at), owned, iso)
        if a.show and a.show == iso:
            for r in rows:
                if r["aspect"] in ("centre", "state", "owner"):
                    print(r["row_id"], r["aspect"], r["value"], r["as_of"], owned.get(r["system"], "?"),
                          facility_key(r["system"]), "|", r["system"])
            print(cell)
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        s = cell["stage"]
        line = {"sub_indicator": "national", "stage": s,
                "centre": {"5": "two", "4": "two", "3": "tier3", "2": "service", "1": "none"}.get(s, ""),
                "owner": "national" if s in ("2", "3", "4", "5") else "",
                "state": "hosted" if s == "5" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-nationaldatacentres.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "centre", "state", "stage_sources")}})
        if a.dry or a.show:
            continue
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry and not a.show:
        study_lib.write_csv(os.path.join(here, "ladder-test.csv"),
                            ["iso3", "stage", "centre", "state", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry or a.show else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
