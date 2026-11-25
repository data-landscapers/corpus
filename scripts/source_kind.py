#!/usr/bin/env python3
"""source_kind.py — what kind of source a record in `raw/` was read from.

    python scripts/source_kind.py            the estate's spread by kind, from the catalogue
    python scripts/source_kind.py --top 25   ... with each kind's 25 biggest hosts, for review
    python scripts/source_kind.py --kind other --top 60

`classify(url)` returns `(source_kind, rule)`. The kinds and their labels are
`lookups/source-kinds.csv`; the rules are `lookups/source-kind-rules.csv`, tried in order,
first match wins (Bill, 2026-11-25: portals and datasets, trade journals, news, press
releases, other; official documents and research split out of other because `raw/` holds
thousands of each).

**A property of where a record was read, so it is derived, not stored.** Every record
carries `url:`, and OSINT's `lookups/publications.csv` already gives 7,212 registrable
domains a publisher `kind` (government, newspaper, trade, igo...). A frontmatter field
would restate that across 51,000 records and drift from it. Publisher kind is not source
kind, which is why the rule table exists: the Gates grants database and a World Bank
project page are datasets on an NGO's and an IGO's host, a PDF in a ministry's upload
folder is a document and not an announcement, and a press wire is press, not news.

A record read from a newspaper that reprints a press release is news: the kind is the
place Corpus read it, not where the words began.

`build-catalogue.py` writes the result as `source_kind` in `catalogue-internal.csv`, so a
report reads it beside the slug rather than calling this. Budget lines are not records:
their source is `doc_type` in `budgets/budgets-all-countries.csv`.
"""
from __future__ import annotations

import argparse
import collections
import csv
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# `realpath`: under the workroot `lookups/` is OSINT's, and these two files are Corpus's.
CORPUS = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
KINDS_CSV = os.path.join(CORPUS, "lookups", "source-kinds.csv")
RULES_CSV = os.path.join(CORPUS, "lookups", "source-kind-rules.csv")
MIRROR = os.environ.get("CORPUS_OSINT_MIRROR", r"C:\OSINT")
PUBLICATIONS = os.path.join(MIRROR, "lookups", "publications.csv")
CATALOGUE = os.path.join(CORPUS, "outputs", "catalogue", "catalogue-internal.csv")


def _read(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


KINDS = {r["source_kind"]: r for r in _read(KINDS_CSV)}
LABEL = {k: r["label"] for k, r in KINDS.items()}
RULES = []
for _n, _r in enumerate(_read(RULES_CSV), 2):          # line numbers, for `rule`
    if _r["source_kind"] not in KINDS:
        raise SystemExit(f"source-kind-rules.csv line {_n}: unknown kind {_r['source_kind']!r}")
    _pk = _r["publisher_kinds"]
    RULES.append((_r["source_kind"], _r["match"],
                  None if _r["match"] == "kind" else re.compile(_r["pattern"]),
                  set(_r["pattern"].split("|")) if _r["match"] == "kind" else None,
                  set(_pk.split("|")) if _pk else None, _n))
try:
    PUB = {r["domain"].strip().lower(): r["kind"].strip() for r in _read(PUBLICATIONS)}
except FileNotFoundError:                               # a missing mirror is not silent
    raise SystemExit(f"source_kind: no {PUBLICATIONS}; set CORPUS_OSINT_MIRROR")


def split(url: str) -> tuple[str, str]:
    """(host without www, lower-cased host + path + query) for matching."""
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", (url or "").strip().strip("\"'").lower())
    # An archived copy is the page it archives.
    m = re.match(r"(?:web\.)?archive\.org/web/[^/]+/(.+)", s)
    if m:
        return split(m.group(1))
    host = s.split("/")[0].split("?")[0].split("#")[0].split("@")[-1].split(":")[0]
    host = re.sub(r"^www\d?\.", "", host).strip(".")
    rest = s[len(s.split("/")[0]):]
    return host, host + rest


def publisher_kind(host: str) -> str:
    """publications.csv's kind for the host or its nearest listed parent; '' if none."""
    h = host
    while h:
        if h in PUB:
            return PUB[h]
        h = h.partition(".")[2]
    return ""


def classify(url: str) -> tuple[str, int]:
    """(source_kind, rule line in source-kind-rules.csv)."""
    host, full = split(url)
    pk = publisher_kind(host)
    for kind, match, rx, kinds, restrict, line in RULES:
        if restrict is not None and pk not in restrict:
            continue
        if match == "url" and rx.search(full):
            return kind, line
        if match == "kind" and ("*" in kinds or pk in kinds):
            return kind, line
    return "other", 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--top", type=int, default=0, help="list each kind's biggest hosts")
    ap.add_argument("--kind", help="only this kind")
    a = ap.parse_args()
    rows = _read(CATALOGUE)
    by, hosts = collections.Counter(), collections.defaultdict(collections.Counter)
    for r in rows:
        k, _ = classify(r["url"])
        by[k] += 1
        hosts[k][split(r["url"])[0] or "(no url)"] += 1
    print(f"{len(rows)} records in {os.path.relpath(CATALOGUE, CORPUS)}")
    for k in KINDS:
        if a.kind and k != a.kind:
            continue
        print(f"  {LABEL[k]:<22} {by[k]:>6}  {100 * by[k] / len(rows):5.1f}%")
        for h, n in hosts[k].most_common(a.top):
            print(f"      {n:>5}  {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
