#!/usr/bin/env python3
r"""study-select.py — a maturity study's reading list, one per country.

    cd scripts/.workroot
    python scripts/study-select.py health            # all 54
    python scripts/study-select.py health --iso KEN  # one country
    python scripts/study-select.py health --dry      # the counts, nothing written

`maturity/documentation/maturity-study-method.md` §4. Writes
`maturity/{id}/evidence/{ISO3}/readlist.csv`, the list a drafter reads whole, and
`maturity/{id}/evidence/summary.csv`, the size of each list, which is what H3 is sized from.

**A document is listed when its title or body carries one of the study's terms.** The
study's subjects are broader than the study: `dpi.mis` holds every sector's management
system, so a subject tag alone would hand a health drafter the education ministry's. The
term list narrows the tagged documents and catches the untagged ones, and one test does
both. What a tag adds is recorded in `why`, never used to admit.

`why` names every route that reached the document, joined by `+`:

- `subject`  — `topics:` holds one of the study's subjects;
- `ledger`   — a ledger row on a study subject cites it;
- `status`   — the status report's sub-section on a study subject links it;
- `considered` — the country's `considered.txt` holds it;
- `regional` — it is filed to the country's region or to Africa, not to the country, and
  its text names the country.

A document cited by a study-subject ledger row or status sub-section is listed whether or
not its body matches, when the row or the sub-section itself carries a term: the status
report already read it as being about this.

**Tagged documents the terms dropped are counted, not hidden**: `summary.csv` carries them
as `tagged_no_term`, so a term list that is missing a country's name for its system shows
up as a large number beside a short list.

The status sub-sections themselves head each list as `kind = status` rows. Runs from the
workroot because it reads `raw/` through Corpus's own index.

Exit: 0 written, 2 the study or the index cannot be read.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib  # noqa: E402
import study_lib   # noqa: E402
import vault_lib   # noqa: E402

SUMMARY_FIELDS = ["iso3", "documents", "words", "status_sections", "tagged_no_term"]
ROUTES = ("status", "ledger", "subject", "considered", "regional")


def scan(rows: list[dict], read, terms: re.Pattern) -> dict[str, dict]:
    """slug -> what every country's selection needs of one `raw/` document, read once.

    `read(row)` returns the file's text. Bodies are folded and dropped here, so 380 MB is
    held one document at a time."""
    out = {}
    for r in rows:
        d, fm = r["d"], r["fm"]
        if d.get("folder") != "raw" or d.get("ext") != ".md":
            continue
        title = str(fm.get("title") or d["slug"])
        folded = study_lib.fold(title + "\n" + (read(r) or ""))
        found = terms.findall(folded)
        out[d["slug"]] = {
            "slug": d["slug"], "path": r["path"], "title": title,
            "published": str(fm.get("published") or d.get("file_date") or ""),
            "places": [str(p) for p in vault_lib.as_list(fm.get("places"))],
            "topics": [str(t) for t in vault_lib.as_list(fm.get("topics"))],
            "url_norm": d.get("url_norm", ""), "words": d.get("words", 0),
            "terms": sorted({t.lower() for t in found}), "hits": len(found),
            "folded": folded if found else "",
        }
    return out


def cited(iso: str, subjects: list[str], terms: re.Pattern, reports: str,
          by_url: dict[str, str]) -> tuple[dict[str, set], list[dict]]:
    """What the country's own report already holds on the study's subjects.

    Returns `(slug -> routes, status rows)`. A route marked `!` admits the document on the
    report's word: the ledger row or sub-section citing it carries a term itself."""
    routes: dict[str, set] = {}
    status_rows = []
    unit = os.path.join(reports, iso)

    for row in study_lib.read_csv(os.path.join(unit, "ledger.csv")):
        if row.get("subject") not in subjects:
            continue
        text = study_lib.fold(" ".join(str(v) for v in row.values()))
        mark = "ledger!" if terms.search(text) else "ledger"
        for slug in filter(None, (s.strip() for s in (row.get("sources") or "").split("|"))):
            routes.setdefault(slug, set()).add(mark)

    status_path = os.path.join(unit, f"{iso}-status.md")
    try:
        with open(status_path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        text = ""
    for slug, label, prose in status_lib.sections(text):
        if slug not in subjects or not prose:
            continue
        hit = terms.search(study_lib.fold(prose))
        status_rows.append({"iso3": iso, "kind": "status", "slug": slug,
                            "path": os.path.relpath(status_path, study_lib.CORPUS).replace("\\", "/"),
                            "title": label, "why": "status", "words": len(prose.split()),
                            "hits": 1 if hit else 0})
        for url in status_lib.links(prose):
            held = by_url.get(vault_lib.normalise_url(url))
            if held:
                routes.setdefault(held, set()).add("status!" if hit else "status")

    try:
        with open(os.path.join(unit, "considered.txt"), encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    routes.setdefault(line.strip(), set()).add("considered")
    except OSError:
        pass
    return routes, status_rows


def select(iso: str, country: dict, docs: dict[str, dict], subjects: list[str],
           routes: dict[str, set]) -> tuple[list[dict], int]:
    """`(readlist rows, tagged documents the terms dropped)` for one country."""
    name = re.compile(r"(?<![A-Za-z])" + re.escape(study_lib.fold(country["name"]))
                      + r"(?![A-Za-z])", re.I)
    rows, dropped = [], 0
    for slug, doc in docs.items():
        why = {r.rstrip("!") for r in routes.get(slug, ())}
        reported = any(r.endswith("!") for r in routes.get(slug, ()))
        in_country = iso in doc["places"]
        tagged = in_country and bool(set(doc["topics"]) & set(subjects))
        regional = (not in_country and bool(set(doc["places"]) & country["regions"])
                    and bool(doc["hits"]) and bool(name.search(doc["folded"])))
        if not (in_country or regional or reported):
            continue
        if not doc["hits"] and not reported:
            dropped += tagged
            continue
        if tagged:
            why.add("subject")
        if regional:
            why.add("regional")
        rows.append({"iso3": iso, "kind": "raw", "slug": slug, "path": doc["path"],
                     "title": doc["title"], "published": doc["published"],
                     "places": ";".join(doc["places"]),
                     "why": "+".join(r for r in ROUTES if r in why) or "term",
                     "terms": ";".join(doc["terms"]), "hits": doc["hits"],
                     "words": doc["words"]})
    # Newest first, with the documents only a term reached after everything a tag or the
    # country's own report vouches for.
    rows.sort(key=lambda r: r["published"], reverse=True)
    rows.sort(key=lambda r: r["why"] == "term")
    return rows, dropped


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A maturity study's reading list, per country.")
    ap.add_argument("study")
    ap.add_argument("--iso", action="append", help="one country; repeatable")
    ap.add_argument("--dry", action="store_true", help="print the counts, write nothing")
    a = ap.parse_args(argv)

    try:
        study = study_lib.load(a.study)
        index = vault_lib.load_index()
    except (study_lib.StudyError, vault_lib.ForeignIndex, vault_lib.EmptyIndex) as e:
        print(f"study-select: {e}")
        return 2

    def read(row):
        try:
            with open(os.path.join(vault_lib.ROOT, row["path"]), encoding="utf-8",
                      errors="replace") as fh:
                return fh.read()
        except OSError:
            return ""

    terms = study_lib.term_regex(study["terms"])
    docs = scan(index, read, terms)
    by_url = {d["url_norm"]: s for s, d in docs.items() if d["url_norm"]}
    all_countries = study_lib.countries()
    wanted = a.iso or sorted(all_countries)
    unknown = [i for i in wanted if i not in all_countries]
    if unknown:
        print(f"study-select: not a country in lookups/countries.csv: {', '.join(unknown)}")
        return 2

    base = os.path.join(study_lib.study_dir(a.study), "evidence")
    summary = []
    for iso in wanted:
        routes, status_rows = cited(iso, study["subjects"], terms, status_lib.REPORTS, by_url)
        rows, dropped = select(iso, all_countries[iso], docs, study["subjects"], routes)
        summary.append({"iso3": iso, "documents": len(rows),
                        "words": sum(int(r["words"]) for r in rows),
                        "status_sections": len(status_rows), "tagged_no_term": dropped})
        if not a.dry:
            study_lib.write_csv(os.path.join(base, iso, "readlist.csv"),
                                study_lib.READLIST_FIELDS, status_rows + rows)
    if not a.dry and not a.iso:
        study_lib.write_csv(os.path.join(base, "summary.csv"), SUMMARY_FIELDS, summary)

    for s in summary:
        print(f"  {s['iso3']}  {s['documents']:4d} documents  {s['words']:8d} words  "
              f"{s['tagged_no_term']:4d} tagged, no term")
    print(f"study-select: {a.study} - {len(summary)} countries, "
          f"{sum(s['documents'] for s in summary)} listings, "
          f"{sum(s['words'] for s in summary)} words"
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
