#!/usr/bin/env python3
"""rd-inbox.py — the analysis and methodology pieces admitted since the last R&D sitting.

    python scripts/rd-inbox.py                  # -> R&D/inbox.md
    python scripts/rd-inbox.py --since 2026-09-01
    python scripts/rd-inbox.py --sat            # a sitting is over: stamp today, delete the inbox

The R&D lane's raw material *(strategic review of 2026-09-25, §6 and R95)*: the base already
admits academic papers, data dives, indices and methodology notes as sources, and a sitting
reads the recent ones **for method, not fact**. This lists them from the catalogue Corpus
already holds — `outputs/catalogue/raw-catalogue.csv`, by `ingested` — and nothing else is
read. `R&D/README.md` carries the date of the last sitting; `--sat` moves it to today.

**A source record has no field saying what kind of piece it is**, so the kind is read off two
things that are recorded. The publisher's host: a journal on the sweep's own journal list
(`outputs/vocab/sweep-journals.csv`), or a host that only publishes papers, is *academic*.
And the title, for the three kinds a title announces: an *index*, a *methodology note*, a
*data dive*. That is a net with holes — a data dive headlined as news is missed — and it is
meant to be: the list is reading matter for one sitting, not a census, and a title that does
not say what the piece is would not have been picked off a list either.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

CORPUS = Path(__file__).resolve().parent.parent
CATALOGUE = CORPUS / "outputs" / "catalogue" / "raw-catalogue.csv"
JOURNALS = CORPUS / "outputs" / "vocab" / "sweep-journals.csv"
RD = CORPUS / "R&D"
README, INBOX = RD / "README.md", RD / "inbox.md"

_SITTING = re.compile(r"^Last sitting: (\d{4}-\d{2}-\d{2})\s*$", re.M)

# Hosts that publish papers and nothing else, beside the sweep's journal list.
PAPER_HOSTS = ("arxiv.org", "ssrn.com", "doi.org", "sciencedirect.com", "tandfonline.com",
               "springer.com", "wiley.com", "sagepub.com", "jstor.org", "nature.com",
               "mdpi.com", "researchgate.net", "academic.oup.com", "cambridge.org",
               "journals.co.za", "ajol.info", "nber.org", "zenodo.org", "osf.io")

# The three kinds a title announces, first match wins. Methodology before index: "the index's
# methodology" is a methodology note.
KINDS = (
    ("methodology note", re.compile(
        r"\bmethodolog|\bmethods? (note|paper)|\btechnical (note|annex)|\bcodebook\b|"
        r"\bhow we (built|measured|counted|calculated|compiled)", re.I)),
    ("index", re.compile(
        r"\bindex\b|\bindices\b|\bscorecard\b|\bbarometer\b|\branking(s)?\b|\bbenchmark", re.I)),
    ("data dive", re.compile(
        r"\bdata dive\b|\bdataset\b|\bdatabase\b|\bby the numbers\b|\bin (numbers|figures|charts)\b|"
        r"\bmapping\b|\btracker\b|\bwe (analysed|analyzed|mapped|counted|scraped)\b|"
        r"\ban analysis of\b|\bevidence from\b|\bsurvey (of|results|findings)\b", re.I)),
)


def host(url: str) -> str:
    h = (urlsplit(url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def journal_hosts() -> set[str]:
    if not JOURNALS.exists():
        return set()
    with JOURNALS.open(encoding="utf-8-sig", newline="") as f:
        return {host(r.get("url") or r.get("URL") or "") for r in csv.DictReader(f)} - {""}


def kind_of(row: dict, journals: set[str]) -> str | None:
    """The kind of analysis piece a catalogue row is, or None for everything else."""
    h = host(row.get("url", ""))
    if h in journals or any(h == p or h.endswith("." + p) for p in PAPER_HOSTS):
        return "academic"
    for kind, pattern in KINDS:
        if pattern.search(row.get("title", "")):
            return kind
    return None


def last_sitting() -> str | None:
    m = _SITTING.search(README.read_text(encoding="utf-8")) if README.exists() else None
    return m.group(1) if m else None


def pieces(since: str) -> list[tuple[str, dict]]:
    journals = journal_hosts()
    out = []
    with CATALOGUE.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("ingested", "") > since:
                kind = kind_of(row, journals)
                if kind:
                    out.append((kind, row))
    order = ["academic", "data dive", "index", "methodology note"]
    return sorted(out, key=lambda p: (order.index(p[0]), p[1].get("published", ""), p[1]["title"]))


def inbox_md(since: str, found: list[tuple[str, dict]]) -> str:
    lines = ["---", "type: reference", "reader: bill", "title: R&D inbox", "---", "",
             f"# R&D inbox — admitted since {since}", "",
             f"{len(found)} pieces, read for method. Delete after the sitting: "
             f"`python scripts/rd-inbox.py --sat`.", ""]
    kind = None
    for k, r in found:
        if k != kind:
            kind = k
            lines += [f"## {k.capitalize()}", ""]
        title = r["title"].replace("[", "(").replace("]", ")")
        lines.append(f"- {r.get('published') or 'undated'} · [{title}]({r['url']}) — {r.get('publisher', '')}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="List the analysis pieces admitted since the last R&D sitting.")
    ap.add_argument("--since", help="YYYY-MM-DD; default is the last sitting in R&D/README.md")
    ap.add_argument("--sat", action="store_true", help="close a sitting: stamp today, delete the inbox")
    a = ap.parse_args()

    if a.sat:
        text = README.read_text(encoding="utf-8")
        if not _SITTING.search(text):
            print("rd-inbox: R&D/README.md carries no 'Last sitting:' line to move")
            return 1
        README.write_text(_SITTING.sub(f"Last sitting: {date.today().isoformat()}", text),
                          encoding="utf-8", newline="\n")
        INBOX.unlink(missing_ok=True)
        print(f"rd-inbox: sitting closed {date.today().isoformat()}; inbox deleted")
        return 0

    since = a.since or last_sitting()
    if not since:
        print("rd-inbox: no --since, and R&D/README.md carries no 'Last sitting:' line")
        return 1
    found = pieces(since)
    INBOX.write_text(inbox_md(since, found), encoding="utf-8", newline="\n")
    counts = {}
    for k, _ in found:
        counts[k] = counts.get(k, 0) + 1
    print(f"rd-inbox: {len(found)} pieces admitted since {since} -> R&D/inbox.md "
          f"({', '.join(f'{n} {k}' for k, n in counts.items()) or 'none'})")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
