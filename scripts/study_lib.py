#!/usr/bin/env python3
r"""study_lib.py — what the maturity-study scripts share: the study's definition, its paths and its files.

`maturity/documentation/maturity-study-method.md` is the procedure. A study states its typology,
aspects and ladders in prose, in `maturity/{id}/maturity-study-{id}.md`; **what a script has to
count against is stated once more as data, in `maturity/{id}/study.json`**, and nowhere else:
subjects, the term list, the sub-indicators, the classes, each aspect with its role and closed
values, the cap rule and the flags. The ladder and the norm stay in the study file, and
`study-render.py` lifts them from there, so neither is written twice.

**A value is checked against the closed list, never interpreted.** An aspect declares `values`
(literals), `facets` (a `facet:value` pair per fact, one closed list per facet) or `pattern`. A
`multi` aspect holds several values joined by `;`. `values` may be a dict keyed by sub-indicator
where the two ladders use different words.

Paths resolve through `realpath`, so they are the same from the repo root and from
`scripts/.workroot/`, where the scripts that read `raw/` have to run.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.realpath(__file__))
CORPUS = os.path.dirname(HERE)
COUNTRIES_CSV = os.path.join(CORPUS, "lookups", "countries.csv")

STAGES = {1: "Absent", 2: "Nascent", 3: "Established", 4: "Operating", 5: "Leading"}
UNPLACED, NO_EVIDENCE = "unplaced", "no evidence"
NOT_STAGED = (UNPLACED, NO_EVIDENCE)

EVIDENCE_FIELDS = ["row_id", "iso3", "sub_indicator", "aspect", "value", "fact", "as_of",
                   "date_precision", "system", "class", "source_slug", "url"]
PROFILE_FIELDS = ["iso3", "sub_indicator", "aspect", "role", "value", "as_of", "sources",
                  "others", "gap"]
SYSTEMS_FIELDS = ["iso3", "system", "country_label", "class", "platform", "owner", "tiers",
                  "sources"]
READLIST_FIELDS = ["n", "slice", "iso3", "kind", "slug", "read", "path", "url", "title", "published", "places",
                   "why", "terms", "hits", "words"]
STAGED_FIELDS = ["file", "url", "iso3", "sub_indicator", "aspect", "title", "published"]
RETURNED_FIELDS = STAGED_FIELDS + ["outcome", "slug", "reason"]
PRECISIONS = ("day", "month", "year")
AS_OF = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")

# A coverage fact older than this still places a country (method §3 rule 8); it is also what
# makes the aspect a gap to search for (§5).
COVERAGE_WINDOW_MONTHS = 36


class StudyError(Exception):
    """The study's own files are wrong: a missing key, an unknown aspect. Not a finding."""


# --------------------------------------------------------------------------- #
# The study
# --------------------------------------------------------------------------- #

def study_dir(study_id: str, root: str = CORPUS) -> str:
    return os.path.join(root, "maturity", study_id)


def out_dir(study_id: str, root: str = CORPUS) -> str:
    return os.path.join(root, "outputs", "maturity", study_id)


def load(study_id: str, root: str = CORPUS) -> dict:
    """`study.json`, checked for the keys every script reads."""
    path = os.path.join(study_dir(study_id, root), "study.json")
    try:
        with open(path, encoding="utf-8") as fh:
            study = json.load(fh)
    except OSError as e:
        raise StudyError(f"no study definition at {path}") from e
    for key in ("id", "subjects", "terms", "sub_indicators", "classes", "aspects", "flags"):
        if key not in study:
            raise StudyError(f"{path} has no `{key}`")
    if study["id"] != study_id:
        raise StudyError(f"{path} says id `{study['id']}`, asked for `{study_id}`")
    for a in study["aspects"]:
        if a.get("role") not in ("coverage", "qualifier"):
            raise StudyError(f"aspect `{a.get('key')}` has no role of coverage or qualifier")
        if not any(k in a for k in ("values", "facets", "pattern")):
            raise StudyError(f"aspect `{a['key']}` declares no values, facets or pattern")
    return study


def subs(study: dict) -> dict[str, dict]:
    return {s["key"]: s for s in study["sub_indicators"]}


def aspects(study: dict) -> dict[str, dict]:
    return {a["key"]: a for a in study["aspects"]}


def mint(subject: str, text: str) -> str:
    """`adding-an-indicator.md` §2: the id is the subject, `--`, and the slug of the full text."""
    return subject + "--" + re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def value_problem(aspect: dict, sub: str, value: str) -> str:
    """Why `value` is outside the aspect's closed list, or an empty string."""
    value = (value or "").strip()
    if not value:
        return "empty value"
    parts = [p.strip() for p in value.split(";")] if aspect.get("multi") or "facets" in aspect \
        else [value]
    if "facets" in aspect:
        for p in parts:
            facet, _, v = p.partition(":")
            if v not in aspect["facets"].get(facet, ()):
                return f"`{p}` is not one of the facets {sorted(aspect['facets'])} with a listed value"
        return ""
    if "pattern" in aspect:
        bad = [p for p in parts if not re.fullmatch(aspect["pattern"], p)]
        return f"`{bad[0]}` does not match {aspect['pattern']}" if bad else ""
    allowed = aspect["values"]
    if isinstance(allowed, dict):
        allowed = allowed.get(sub, ())
    bad = [p for p in parts if p not in allowed]
    return f"`{bad[0]}` is not one of {list(allowed)}" if bad else ""


# --------------------------------------------------------------------------- #
# Countries
# --------------------------------------------------------------------------- #

def countries(path: str = COUNTRIES_CSV) -> dict[str, dict]:
    """iso3 -> {name, regions}. The 54: every row of `countries.csv` that is not an `X` group.

    `regions` is what a regional or continental document carries in `places:` when it covers
    the country: its own region, Africa, and Sub-Saharan Africa outside North Africa."""
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            iso, region = r["iso-3"].strip(), r["Region"].strip()
            if iso.startswith("X"):
                continue
            regions = {region, "XAF"} | ({"XSS"} if region != "XNA" else set())
            out[iso] = {"name": r["country-name"].strip(), "regions": regions}
    return out


# --------------------------------------------------------------------------- #
# Text and dates
# --------------------------------------------------------------------------- #

def fold(text: str) -> str:
    """Accents and typographic apostrophes flattened, case kept: `Système` -> `Systeme`.

    Some captured bodies arrive with their accents already lost, so a term is matched on the
    folded form of both sides or it misses exactly those."""
    text = unicodedata.normalize("NFKD", text.replace("’", "'").replace("‘", "'"))
    return "".join(c for c in text if not unicodedata.combining(c))


def term_regex(terms: list[str]) -> re.Pattern:
    """One alternation over the term list, on folded text.

    **A short all-capitals term is matched as written**: `SIS`, `EMR` and `EHR` are words, or
    parts of words, in three working languages once case is ignored. Everything else is
    case-insensitive. All are bounded so `HMIS` does not fire inside another token."""
    alts = []
    for t in terms:
        f = re.escape(fold(t.strip()))
        if not f:
            continue
        alts.append(f if (t.isupper() and len(t) <= 6) else f"(?i:{f})")
    return re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(alts) + r")(?![A-Za-z0-9])")


def parse_as_of(s: str) -> dt.date | None:
    """`2024`, `2024-06` or `2024-06-30` as the last day it could mean, else None."""
    s = (s or "").strip()
    if not AS_OF.match(s):
        return None
    y, m, d = (s.split("-") + [None, None])[:3]
    try:
        if d:
            return dt.date(int(y), int(m), int(d))
        if m:
            nxt = dt.date(int(y) + (int(m) == 12), int(m) % 12 + 1, 1)
            return nxt - dt.timedelta(days=1)
        return dt.date(int(y), 12, 31)
    except ValueError:
        return None


def months_back(day: dt.date, months: int) -> dt.date:
    y, m = divmod(day.year * 12 + day.month - 1 - months, 12)
    return dt.date(y, m + 1, min(day.day, 28))


# --------------------------------------------------------------------------- #
# Files
# --------------------------------------------------------------------------- #

def read_csv(path: str) -> list[dict]:
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            return list(csv.DictReader(fh))
    except OSError:
        return []


def write_csv(path: str, fields: list[str], rows: list[dict]) -> None:
    """LF line endings always: a CSV rewritten with the platform's is a diff of every line."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def evidence(study_id: str, root: str = CORPUS) -> dict[str, list[dict]]:
    """iso3 -> the rows of `maturity/{id}/evidence/{ISO3}/evidence.csv`."""
    base = os.path.join(study_dir(study_id, root), "evidence")
    out = {}
    if os.path.isdir(base):
        for iso in sorted(os.listdir(base)):
            rows = read_csv(os.path.join(base, iso, "evidence.csv"))
            if rows:
                out[iso] = rows
    return out


def evidence_problems(study: dict, iso: str, rows: list[dict]) -> list[str]:
    """What is wrong with one country's `evidence.csv`, as it stands on disk."""
    out, seen = [], set()
    sub_keys, asp, classes = subs(study), aspects(study), set(study["classes"])
    for n, r in enumerate(rows, 2):
        where = f"{iso} evidence.csv line {n}"
        rid = (r.get("row_id") or "").strip()
        if not rid.startswith(iso + "-"):
            out.append(f"{where}: row_id `{rid}` does not open `{iso}-`")
        if rid in seen:
            out.append(f"{where}: row_id `{rid}` is used twice")
        seen.add(rid)
        if r.get("iso3") != iso:
            out.append(f"{where}: iso3 `{r.get('iso3')}` in {iso}'s file")
        sub, a = r.get("sub_indicator", ""), r.get("aspect", "")
        if sub not in sub_keys:
            out.append(f"{where}: sub_indicator `{sub}` is not one of {list(sub_keys)}")
        if a not in asp:
            out.append(f"{where}: aspect `{a}` is not one of {list(asp)}")
        else:
            bad = value_problem(asp[a], sub, r.get("value", ""))
            if bad:
                out.append(f"{where}: {a}: {bad}")
        if r.get("class") and r["class"] not in classes:
            out.append(f"{where}: class `{r['class']}` is not in the typology")
        if parse_as_of(r.get("as_of", "")) is None:
            out.append(f"{where}: as_of `{r.get('as_of')}` is not YYYY, YYYY-MM or YYYY-MM-DD")
        if r.get("date_precision") not in PRECISIONS:
            out.append(f"{where}: date_precision `{r.get('date_precision')}` is not one of {PRECISIONS}")
        for col in ("fact", "source_slug", "url"):
            if not (r.get(col) or "").strip():
                out.append(f"{where}: no {col}")
    return out
