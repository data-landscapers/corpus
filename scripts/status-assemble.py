#!/usr/bin/env python3
"""Assemble the status baseline from the chapter drafts — `STATUS-INIT.md` -> *Stage 3*.

    python scripts/status-assemble.py NGA --hub-reviewed 2026-08-09 --intersections 16

Reads `prep/scope/{ISO3}/draft/*.md`, one file per Level-1 chapter, and writes
`outputs/reports/{ISO3}/{ISO3}-status.md` in outline order with the frontmatter the report layer
expects. **It overwrites the ledger-rendered status report, deliberately** — that is what
`status-init` means, and git holds the displaced file.

The frontmatter counts are computed from the assembled document rather than reported by the run,
because a report that misstates its own source count is wrong in the place a reader is least likely
to check. `status-check.py` re-derives them independently and fails on any drift.

Sub-sections are keyed on the `<!-- slug -->` comment, not on the heading text, so a writer that
retitled a section cannot silently drop it: anything the outline expects and the drafts do not
carry is reported and the assembly stops.
"""

import argparse
import csv
import datetime
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402

OSINT = r"C:\OSINT"
SECTION = re.compile(r"^###\s+(.+?)\s*\n<!--\s*([a-z]+\.[a-z]+)\s*-->\s*\n(.*?)(?=^###\s|\Z)",
                     re.M | re.S)


def country(iso):
    with open(os.path.join(OSINT, "lookups", "countries.csv"), encoding="utf-8-sig",
              newline="") as fh:
        for row in csv.DictReader(fh):
            if (row.get("iso3") or "").upper() == iso:
                return row.get("country") or row.get("name") or iso, row.get("region") or ""
    return iso, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iso3")
    ap.add_argument("--hub-reviewed", required=True)
    ap.add_argument("--intersections", required=True, type=int)
    ap.add_argument("--compiled", default=datetime.date.today().isoformat())
    args = ap.parse_args()
    iso = args.iso3.upper()
    name, region = country(iso)

    written = {}
    for path in sorted(glob.glob(os.path.join(S.REPO, "prep", "scope", iso, "draft", "*.md"))):
        for label, slug, prose in SECTION.findall(open(path, encoding="utf-8").read()):
            if slug in written:
                print(f"! {slug} written twice — {os.path.basename(path)}", file=sys.stderr)
            written[slug] = (label, prose.strip())

    want = S.outline()
    missing = [slug for _c, slug, _l in want if slug not in written]
    if missing:
        print("! not assembled — no draft carries: " + ", ".join(missing), file=sys.stderr)
        return 1
    spare = [s for s in written if s not in {slug for _c, slug, _l in want}]
    if spare:
        print("! a draft carries a sub-section the outline does not: " + ", ".join(spare),
              file=sys.stderr)
        return 1

    body, chapter = [], None
    for c, slug, label in want:
        if c != chapter:
            chapter = c
            body.append(f"## {chapter}\n")
        drafted_label, prose = written[slug]
        body.append(f"### {drafted_label or label}\n<!-- {slug} -->\n\n{prose}\n")
    body = "\n".join(body).rstrip() + "\n"

    urls = S.links(body)
    secs = S.sections(body)
    n_written = sum(1 for _s, _l, p in secs if p.strip())
    n_notest = sum(1 for _s, _l, p in secs
                   if p.strip() and not S.links(p) and len(S.sentences(p)) <= 2)

    folder = os.path.join(S.REPORTS, iso)
    apath = os.path.join(folder, f"{iso}-acquire.md")
    n_acquire = 0
    if os.path.exists(apath):
        n_acquire = len(re.findall(r"^\|\s*\d{4}", open(apath, encoding="utf-8").read(), re.M))

    fm = [
        "---",
        f"title: {name} — digital transformation and data governance status report",
        f"compiled: {args.compiled}",
        f"place: {iso}",
        f"region: {region}",
        "built_by: STATUS-INIT",
        f"hub_last_reviewed: {args.hub_reviewed}",
        f"intersections_read: {args.intersections}",
        f"sources_cited: {len(urls)}",
        f"sections_written: {n_written}",
        f"not_established: {n_notest}",
        f"acquire_lines: {n_acquire}",
        "---",
        "",
    ]

    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{iso}-status.md")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(fm) + body)

    print(f"{path}")
    print(f"{iso} · sections written {n_written} of {len(want)} · not established {n_notest} "
          f"· sources cited {len(urls)} · acquire lines {n_acquire}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
