#!/usr/bin/env python3
r"""
lint-shared-assets.py — has Corpus's copy of a shared asset fallen behind?

**Corpus is an extension of data-landscapers and shares its style and functionality
wherever it can** *(Bill, 2026-08-19)*. Where a thing is genuinely shared — so far
the datatable component — `data-landscapers` holds the canonical copy under
`assets/shared/` and Corpus carries a duplicate, because the two are separate
repositories with separate deploys and a cross-origin `<script src>` would mean
every Corpus table losing its table whenever the other domain moved a path.

A duplicate needs a way of telling you it has gone stale, or the sharing is a
statement of intent rather than a fact. Each copied asset therefore sits beside a
`{NAME}-FROM` file holding the commit it was taken from — the pattern `main.css`
already used (`MAIN-CSS-FROM`) — and this reads those markers, compares the bytes,
and says what has drifted.

**Three states, and they are not the same problem.**

  1. **Identical, marker current.** Nothing to do.
  2. **Identical, marker stale.** The canonical file has moved on in ways that did
     not change these bytes — a commit touching a sibling asset. Harmless; the
     marker is refreshed by the next copy and nothing is reported as drift.
  3. **Different.** Either the canonical copy gained something Corpus has not, or
     Corpus was edited in place and the change never went home. The second is the
     one that matters, and this cannot tell them apart from the bytes alone — it
     reports the difference and leaves the direction to a human, because guessing
     wrong means overwriting the newer of the two.

**Reports, never fixes**, on `lint-mirror-freshness.py`'s reasoning: copying in
either direction is a destructive write on one of two repositories, and a script
that picked a direction for itself would be deciding which repo is authoritative
for a given change — exactly the judgment it does not have.

Usage:  python scripts/lint-shared-assets.py [--repo PATH] [--quiet]
        --repo defaults to $DATA_LANDSCAPERS, else the sibling checkout beside
        Corpus, else C:\\Users\\bill\\Dropbox\\Github\\data-landscapers.
Exit:   0 clean, 1 drift found, 2 the canonical repo could not be read.
"""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent

# (marker file in Corpus, Corpus copy, path within the canonical repo)
#
# `main.css` joined the list on 2026-08-24 and is the reason the list exists.
# It could not be checked before: the Corpus-only rules (`.corpus-nav`,
# `.stat-bar`) were spliced into the vendored file at line 155, so the copy was
# never meant to match and a byte-comparison would have reported drift on every
# run. Those rules now live in `site/assets/css/corpus.css`, loaded after
# main.css on every page, and the vendored file is a straight copy again.
#
# **Anything Corpus needs that the website does not goes in `corpus.css`, never
# into this copy.** Editing the copy is how the two versions diverge, and the
# lint will then say so without saying which way round.
SHARED = [
    ("site/assets/css/MAIN-CSS-FROM", "site/assets/css/main.css",     "assets/css/main.css"),
    ("site/assets/DATATABLE-FROM",    "site/assets/js/datatable.js",  "assets/shared/datatable.js"),
    ("site/assets/DATATABLE-FROM",    "site/assets/css/datatable.css", "assets/shared/datatable.css"),
]

DEFAULTS = [
    Path(r"C:\Users\bill\Dropbox\Github\data-landscapers"),
    Path("/sessions") / "mnt" / "data-landscapers",
]


def canonical_repo(arg: str | None) -> Path | None:
    """Where data-landscapers is checked out. It is a sibling repository, not a
    subdirectory of this one, so there is no path that is right everywhere: a
    Cowork session sees it under its own mount and Claude Code sees the Dropbox
    path. Try the explicit answer, then the environment, then the neighbours."""
    for cand in ([Path(arg)] if arg else []) + \
                ([Path(os.environ["DATA_LANDSCAPERS"])] if os.environ.get("DATA_LANDSCAPERS") else []) + \
                [CORPUS.parent / "data-landscapers"] + DEFAULTS:
        if (cand / "assets" / "shared").is_dir():
            return cand
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", help="path to the data-landscapers checkout")
    ap.add_argument("--quiet", action="store_true", help="print only what is wrong")
    a = ap.parse_args()

    repo = canonical_repo(a.repo)
    if repo is None:
        print("lint-shared-assets: no data-landscapers checkout found — pass --repo "
              "or set DATA_LANDSCAPERS. Nothing checked.")
        return 2

    drift, checked = [], 0
    for marker, mine, theirs in SHARED:
        m, src, dst = CORPUS / marker, repo / theirs, CORPUS / mine
        if not src.exists():
            drift.append(f"{theirs}: not in {repo} — the canonical copy has moved or gone")
            continue
        if not dst.exists():
            drift.append(f"{mine}: missing from Corpus")
            continue
        checked += 1
        if src.read_bytes() != dst.read_bytes():
            drift.append(f"{mine} differs from {theirs} — one of them is ahead; "
                         f"compare before copying either way")
        elif not m.exists():
            drift.append(f"{marker}: no provenance marker beside a shared asset")

    if not a.quiet:
        print(f"lint-shared-assets: {checked} shared asset(s) checked against {repo}")
        for marker in sorted({m for m, _, _ in SHARED}):
            p = CORPUS / marker
            print(f"  {marker} -> {p.read_text().strip()[:12] if p.exists() else '(absent)'}")
    for d in drift:
        print(f"  DRIFT  {d}")
    if not drift and not a.quiet:
        print("  ok — the copies match")
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
