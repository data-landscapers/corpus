#!/usr/bin/env python3
r"""reread-brief.py — one screen of everything a stage 4 re-read of a unit needs.

    python scripts/reread-brief.py COG

Written during the 2026-09-10 repair (`documentation/considered-not-carried.md`),
after Benin's re-read took four separate queries to assemble the same picture
eight more times over. It reads only Corpus's own files and prints three things:

  1. **The reopened sources, grouped by the indicator they were staged for**, with
     the filler's own `baseline`/`progress` call and each source's `note:` — which
     is usually enough for the row decision and always enough to know whether the
     body needs opening.
  2. **The unit's ledger, by subject**, so *does a row already answer this* is
     answerable without a second pass. That question splits the work in two: an
     indicator with a row needs a mapping, one without needs a mint.
  3. **The subjects the ledger holds nothing for at all** — the shape the defect
     takes. Seven of Benin's forty-eight empty indicators sat in subjects with no
     row of any kind, and every one of them was a mint.

**It decides nothing.** Every outcome here is `BUILD.md` stage 4 step 2's to make,
under the rule as corrected on 2026-09-10: a source establishing a standing
position the ledger lacks mints a row at `movement: Baseline not held`; one
reporting activity on a position already held may move it or may do nothing.

**Mint and map are one step, not two.** A row minted and left unmapped leaves the
indicator publishing ***No evidence*** over the row that answers it — the exact
defect being repaired. It happened once on Benin and was caught only by the final
count, so the summary at the foot prints both numbers side by side.
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
OSINT_RAW = Path(r"C:\OSINT\raw")


def frame():
    rows = list(csv.DictReader((CORPUS / "lookups" / "indicators.csv").read_text(
        encoding="utf-8-sig").splitlines()))
    rows.sort(key=lambda r: (int(r["Topic Sort"]), int(r["Indicator Sort"])))
    return rows


def no_evidence(iso, pairs):
    md = CORPUS / "outputs" / "reports" / iso / f"{iso}-progress.md"
    lines = md.read_text(encoding="utf-8").split("\n")
    i, out = 0, set()
    while i < len(lines) - 1:
        rule = lines[i + 1].strip().strip("|").replace("|", "")
        if lines[i].startswith("|") and rule and set(rule) <= set("-: "):
            head = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            i += 2
            if head[-1] == "Progress":
                while i < len(lines) and lines[i].startswith("|"):
                    c = [x.strip() for x in lines[i].strip().strip("|").split("|")]
                    if c[-1].split(",")[0].strip().strip("*") == "No evidence":
                        k = pairs.get((c[0], c[1]))
                        if k:
                            out.add(k)
                    i += 1
            continue
        i += 1
    return out


def _reopened(iso: str):
    """`report-scan.py --slugs {ISO}`, which reads the base and is authoritative."""
    import subprocess
    wr = CORPUS / "scripts" / ".workroot"
    # Invoked by its path *inside* the workroot, not by the Corpus path: the script
    # derives the base root from its own location, and the workroot's own `scripts`
    # junction is what makes raw/ and wiki/ resolve. Passing the Corpus path with the
    # workroot as cwd looks equivalent and is not.
    out = subprocess.run([sys.executable, "scripts/report-scan.py", "--slugs", iso],
                         cwd=wr, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"reread-brief: report-scan failed for {iso}: "
                         + out.stderr[-600:])
    return [l.strip() for l in out.stdout.splitlines() if l.strip()]


def notes():
    """slug -> (topics, published, note), read once over raw/."""
    out = {}
    for p in glob.glob(str(OSINT_RAW / "*" / "*.md")):
        out[os.path.basename(p)[:-3]] = p
    return out


def brief(iso: str) -> int:
    fr = frame()
    byid = {r["indicator_id"]: r for r in fr}
    pairs = {(r["Topic"], r["Progress indicator"]): r["indicator_id"] for r in fr}
    d = CORPUS / "outputs" / "reports" / iso
    empty = no_evidence(iso, pairs)
    considered = {l.strip() for l in (d / "considered.txt").read_text(
        encoding="utf-8").splitlines() if l.strip()}

    # The reopened set comes from report-scan, never from the manifest. OSINT renames
    # some files at ingest — 986 of 9,178 staged names match no slug in raw/ — so a
    # staged name absent from considered.txt usually means the file is considered under
    # a *different* name, not that it is outstanding. Matching the two by similarity was
    # tried on 2026-09-10 and attached unrelated documents to indicators; it is wrong and
    # is not to be reattempted. Where a staged name is not in the reopened set, the
    # document is not this pass's work.
    reopened = set(_reopened(iso))

    led = list(csv.DictReader((d / "ledger.csv").read_text(encoding="utf-8-sig").splitlines()))
    bysub = defaultdict(list)
    for r in led:
        bysub[r["subject"]].append(r)

    staged = defaultdict(list)
    for f in sorted((CORPUS / "logs" / "progress-filler").glob(f"{iso}-*-selected.csv")):
        for r in csv.DictReader(f.read_text(encoding="utf-8-sig").splitlines()):
            iid = (r.get("indicator_id") or "").strip()
            path = (r.get("staged_file") or r.get("file") or "").strip()
            if not (iid and path):
                continue
            slug = os.path.basename(path)
            slug = slug[:-3] if slug.endswith(".md") else slug
            if iid in empty and slug in reopened:
                staged[iid].append((slug, (r.get("brief") or "?").strip(),
                                    (r.get("published") or "").strip()))

    idx = notes()
    print(f"=== {iso}: {sum(len(v) for v in staged.values())} reopened source(s) over "
          f"{len(staged)} indicator(s); {len(empty)} indicator(s) read No evidence\n")

    for iid in [r["indicator_id"] for r in fr if r in fr and r["indicator_id"] in staged]:
        sub = iid.split("--")[0]
        rows = bysub.get(sub, [])
        print(f"### {byid[iid]['Progress indicator']}  <{iid}>")
        print(f"    ledger in {sub}: "
              + (", ".join(r["row_id"][len(iso) + 1:] for r in rows) if rows
                 else ">>> NO ROW IN THIS SUBJECT — expect a mint <<<"))
        for slug, b, pub in sorted(set(staged[iid]), key=lambda x: x[2]):
            note = ""
            p = idx.get(slug)
            if p:
                fm = Path(p).read_text(encoding="utf-8").split("---", 2)
                if len(fm) > 2:
                    m = re.search(r"\nnote: *(.*?)(?=\n[a-z_]+:)", fm[1], re.S)
                    if m:
                        note = " ".join(m.group(1).split())[:260]
            else:
                note = "(NOT IN raw/)"
            print(f"    {b:8s} {pub or '?':10s} {slug}")
            if note:
                print(f"             {note}")
        print()

    bare = [s for s in {i.split('--')[0] for i in staged} if not bysub.get(s)]
    if bare:
        print(f"subjects with no ledger row at all: {', '.join(sorted(bare))}")
    print(f"\nledger {len(led)} rows | indicators.csv "
          f"{sum(1 for _ in csv.DictReader((d / 'indicators.csv').read_text(encoding='utf-8-sig').splitlines()))} "
          f"mapped of {len(fr)} | mint and map are ONE step")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("unit")
    sys.exit(brief(ap.parse_args().unit.upper()))
