#!/usr/bin/env python3
"""Scope a `status-init` run — `STATUS-INIT.md` -> *Stage 0*, and the two non-wiki extraction cuts.

    python scripts/status-scope.py RWA

Prints the parent's scope to stdout and writes the two large cuts to `prep/scope/{ISO3}/`, which is
gitignored working material like the CSVs they come from. The split is the one the design asks for:
**the parent holds the map, the agents hold the mass.** The DPI cut alone runs to tens of KB per
country, which has no business in the context that is going to assemble the report.

**Why this is a script and not a model's first ten minutes.** Everything here is deterministic —
a lookup, two CSV filters, and a frontmatter scan — so doing it by hand 54 times is 54 chances to
do it differently. One of those chances is the failure `STATUS-INIT.md` names outright: *"Do not
construct the filename."* Seven countries use an intersection prefix that is not the country name,
and COM and GNQ carry files under two prefixes each, so a constructed name silently reads a subset
of the evidence and the report is thin for a reason nobody can see afterwards. Selecting on
`place: {ISO3}` frontmatter is the rule, and a script cannot be tempted out of it.

The hub is read the way stage 2 requires — headings scanned, two sections extracted by line range,
**never read whole.** Hubs run to 296KB (NGA), and `## Recent developments` is chronology, which is
the wrong input for a status report and is deliberately not printed here.
"""

import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402

OSINT = r"C:\OSINT"
PLACES = os.path.join(OSINT, "wiki", "places")
INTERSECTIONS = os.path.join(OSINT, "wiki", "intersections")
COUNTRIES = os.path.join(OSINT, "lookups", "countries.csv")
SCOPE = os.path.join(S.REPO, "prep", "scope")

# The five columns that matter out of the dataset's fourteen. **The comments and the URLs are the
# point**; the value code is a summary of them (`STATUS-INIT.md` -> *Inputs*).
DPI_COLUMNS = ("Variable Id", "Value Name", "Year", "Comments", "Source urls")

# Read for the map, not the mass. `## Recent developments` is chronology and is not among them.
HUB_SECTIONS = ("Active topics", "Record not held")


def country(iso):
    """The lookup's row for this ISO3. Its headers are `iso-3,country-name,Region`, which are
    OSINT's to name — so they are matched case- and separator-insensitively rather than copied
    here, where a rename in the lookup would turn into a silent no-match."""
    def key(row, *names):
        for k, v in row.items():
            if re.sub(r"[^a-z0-9]", "", (k or "").lower()) in names:
                return (v or "").strip()
        return ""

    with open(COUNTRIES, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if key(row, "iso3").upper() == iso:
                return {"name": key(row, "countryname", "name", "country"),
                        "region": key(row, "region")}
    return {}


def hub(iso):
    """(last_reviewed, topics, {heading: body}) — read by line range, never whole."""
    path = os.path.join(PLACES, f"{iso}.md")
    if not os.path.exists(path):
        return None, [], {}, 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    size = sum(len(l) for l in lines)
    head = "".join(lines[:40])
    reviewed = (re.search(r"^last_reviewed:\s*(\S+)", head, re.M) or [None, None])[1]
    topics = re.search(r"^topics:\s*\[(.*?)\]", head, re.M | re.S)
    topics = [t.strip() for t in topics.group(1).split(",") if t.strip()] if topics else []
    marks = [(i, l[3:].strip()) for i, l in enumerate(lines) if l.startswith("## ")]
    out = {}
    for n, (i, title) in enumerate(marks):
        for want in HUB_SECTIONS:
            if title.startswith(want):
                end = marks[n + 1][0] if n + 1 < len(marks) else len(lines)
                out[title] = "".join(lines[i:end]).rstrip()
    return reviewed, topics, out, size


def intersections(iso, region):
    """Files whose frontmatter carries `place: {ISO3}`, and the region's alongside them.

    Selected on frontmatter, never on filename — the whole point of the function."""
    mine, regional = [], []
    for fn in sorted(os.listdir(INTERSECTIONS)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(INTERSECTIONS, fn)
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = fh.read(1500)
        m = re.search(r"^place:\s*\[?\s*([A-Z]{3})", head, re.M)
        if not m:
            continue
        size = os.path.getsize(path)
        topics = re.search(r"^topics:\s*\[(.*?)\]", head, re.M | re.S)
        topics = [t.strip() for t in topics.group(1).split(",") if t.strip()] if topics else []
        if m.group(1) == iso:
            mine.append((fn, size, topics))
        elif m.group(1) == region:
            regional.append((fn, size, topics))
    return mine, regional


def dpi_cut(iso, out_dir):
    rows = []
    with open(S.DPI_CSV, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if (row.get("Country") or "").strip().upper() == iso:
                rows.append({c: row.get(c, "") for c in DPI_COLUMNS})
    path = os.path.join(out_dir, f"{iso}-dpi.csv")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=DPI_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    with_urls = sum(1 for r in rows if (r["Source urls"] or "").strip())
    return path, len(rows), with_urls


def finance_cut(iso, region, out_dir):
    rows, cols = [], None
    with open(S.FINANCE_CSV, encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh)
        cols = rd.fieldnames
        key = cols[0]                      # 'recipient_country', possibly BOM-prefixed
        for row in rd:
            if (row.get(key) or "").strip().upper() in (iso, region):
                rows.append(row)
    path = os.path.join(out_dir, f"{iso}-finance.csv")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    own = sum(1 for r in rows if (r.get(cols[0]) or "").strip().upper() == iso)
    return path, len(rows), own


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso3")
    args = ap.parse_args()
    iso = args.iso3.upper()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    row = country(iso)
    if not row:
        print(f"{iso}: not in {COUNTRIES}")
        return 1
    name = (row.get("name") or row.get("country") or "").strip()
    region = (row.get("region") or "").strip().upper()
    slug = name.lower().replace(" ", "-")

    out_dir = os.path.join(SCOPE, iso)
    os.makedirs(out_dir, exist_ok=True)

    reviewed, topics, sections, hub_size = hub(iso)
    mine, regional = intersections(iso, region)
    dpi_path, dpi_rows, dpi_urls = dpi_cut(iso, out_dir)
    fin_path, fin_rows, fin_own = finance_cut(iso, region, out_dir)

    print(f"# status-init scope — {iso}\n")
    print(f"country        : {name}")
    print(f"region         : {region}")
    print(f"slug           : {slug}   (intersection filenames may NOT use this — see below)")
    print(f"hub            : wiki/places/{iso}.md   {hub_size:,} bytes, "
          f"last_reviewed {reviewed or 'not stated'}")
    print(f"                 dates the whole report. Never read this file whole.")
    print(f"\ntopics on the hub ({len(topics)}): {', '.join(topics) or 'none'}")

    print(f"\n## Intersections — {len(mine)} for {iso}"
          + (f", plus {len(regional)} for {region}" if regional else ""))
    print("   Selected on `place:` frontmatter. Read each whole; one agent each.")
    for fn, size, tops in mine:
        print(f"   {fn:<52} {size / 1024:6.1f} KB  {', '.join(tops[:6])}"
              + (" …" if len(tops) > 6 else ""))
    for fn, size, tops in regional:
        print(f"   [{region}] {fn:<45} {size / 1024:6.1f} KB  {', '.join(tops[:6])}"
              + (" …" if len(tops) > 6 else ""))
    odd = [fn for fn, _, _ in mine if not fn.startswith(slug)]
    if odd:
        print(f"\n   NOTE: {len(odd)} of these do not start with `{slug}`. This is why the list is "
              f"selected on\n         frontmatter and not constructed from the country name.")

    print(f"\n## Indicator rows — one agent")
    print(f"   {os.path.relpath(dpi_path, S.REPO)}   {dpi_rows} rows, {dpi_urls} carrying a URL")
    print(f"\n## Finance rows — one agent")
    print(f"   {os.path.relpath(fin_path, S.REPO)}   {fin_rows} rows "
          f"({fin_own} for {iso}, {fin_rows - fin_own} regional)")

    for title in HUB_SECTIONS:
        got = [v for k, v in sections.items() if k.startswith(title)]
        print(f"\n## Hub — {title}\n")
        print(got[0] if got else f"   (the hub carries no `## {title}` section)")

    print(f"\n---\nStage 1 fan-out: {len(mine) + len(regional)} intersection agents + 1 indicator "
          f"+ 1 finance = {len(mine) + len(regional) + 2} extraction agents.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
