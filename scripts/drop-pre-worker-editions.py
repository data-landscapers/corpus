#!/usr/bin/env python3
r"""drop-pre-worker-editions.py — a one-off: delete the editions that predate the download record.

**This is a migration, not a rule.** It ran once, on 2026-09-08, to clear the ~374 MB of
superseded editions published before the `download-log` Worker existed. `prune-editions.py` is
the standing rule and this is not part of it; when the tree is clear this file can go.

    python scripts/drop-pre-worker-editions.py            # report, delete nothing
    python scripts/drop-pre-worker-editions.py --apply    # delete

**Why the standing rule could not do this.** `prune-editions.py` condition 2 exempts everything
published on or before 2026-08-18 precisely *because* there is no download record for that
period — applying "delete unless somebody took it" to files nobody could have been recorded
taking would delete all of them for want of evidence, which is the wrong direction of failure.
That exemption was right while the site was public-facing with citations resting on it. Bill's
call of 2026-09-08 is that it is not: the site is not live, the only downloads in the record are
his own testing, and so there is no reader whose citation the exemption is protecting. The
exemption is therefore removed by hand, once, rather than weakened in the rule that will govern
the live site.

**The download record is deliberately not consulted.** Under the standing rule any fetch at all
protects a file. Here every fetch in the period is Bill's own testing, so honouring it would
keep an arbitrary scatter of files for no reason anybody will later be able to reconstruct. The
decision is by date, so that what survives is explainable in one sentence.

**The current edition of any document is never touched, and that is not a policy choice.** A
document whose content has not moved since July still has a pre-worker edition as its newest,
and its live page offers exactly that file. Deleting it would leave the published page pointing
at a 404 — a defect, not a smaller archive. 164 editions are held back by this and the count is
printed, because a run that silently kept a sixth of what it was pointed at should say so.

**Deletions land in `logs/deleted-editions.csv`**, the same ledger the standing rule writes, so
there is one account of what went rather than two. Git keeps every blob regardless; the ledger
is the part a person can read.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# The pruner owns the filename grammar and the ledger, and is imported rather than copied.
# §9: "Every script that reads editions parses and orders them with render.py's own functions" —
# two copies of one grammar fail silently the first time a `-2` edition is cut.
_spec = importlib.util.spec_from_file_location(
    "prune_editions", Path(__file__).resolve().parent / "prune-editions.py")
pe = importlib.util.module_from_spec(_spec)
sys.path.insert(0, str(Path(__file__).resolve().parent))
_spec.loader.exec_module(pe)

# Editions dated before this are in scope. The Worker went live on 2026-08-18, so that day's
# editions are in scope too: the record only begins part-way through it.
DEFAULT_BEFORE = "2026-08-19"


def plan(site: Path, before: str) -> list[dict]:
    """Every superseded edition older than `before`, with the current edition of each held back.

    Pure — it reads the tree and removes nothing. The shape of a row matches the pruner's, so
    `pe.write_ledger` can take these unchanged."""
    out: list[dict] = []
    for found in pe.editions_on_disk(site).values():
        for i, (key, path) in enumerate(found):
            if key[0] >= before:
                continue
            rel = path.relative_to(site).as_posix()
            row = {"path": path, "rel": rel, "edition": pe._name(key),
                   "bytes": path.stat().st_size, "superseded_by": "", "superseded_on": "",
                   "verdict": "", "why": ""}
            if i == len(found) - 1:
                row.update(verdict="keep", why="current edition")
            else:
                nxt = found[i + 1][0]
                row.update(verdict="delete", why="predates the download record",
                           superseded_by=pe._name(nxt), superseded_on=nxt[0])
            out.append(row)
    return sorted(out, key=lambda r: r["rel"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--apply", action="store_true",
                   help="actually delete; without it nothing is removed")
    p.add_argument("--before", default=DEFAULT_BEFORE,
                   help=f"editions dated before this are in scope (default {DEFAULT_BEFORE})")
    p.add_argument("--site", type=Path, default=SITE, help="tree to act on")
    p.add_argument("--ledger", type=Path, default=None,
                   help="write the account elsewhere — what a rehearsal should use")
    args = p.parse_args(argv)

    dt.date.fromisoformat(args.before)          # a malformed date must not read as "everything"
    site = args.site.resolve()
    if not site.is_dir():
        print(f"DROP: declined — no tree at {pe._under_root(site)}")
        return 0

    rows = plan(site, args.before)
    goes = [r for r in rows if r["verdict"] == "delete"]
    held = [r for r in rows if r["verdict"] == "keep"]
    size = sum(r["bytes"] for r in goes) / 1e6

    print(f"DROP: {len(rows)} editions before {args.before}, "
          f"{len(goes)} deletable ({size:.1f} MB), {len(held)} held as the current edition")
    if not args.apply:
        for r in goes[:10]:
            print(f"  would delete  {r['rel']}  (superseded by {r['superseded_by']})")
        if len(goes) > 10:
            print(f"  … and {len(goes) - 10} more")
        print("DROP: nothing deleted — pass --apply")
        return 0

    when = dt.date.today().isoformat()
    gone = []
    for r in goes:
        try:
            r["path"].unlink()
            gone.append(r)
        except OSError as e:
            print(f"DROP: could not delete {r['rel']} — {e}")
    pe.write_ledger(gone, when, args.ledger)
    print(f"DROP: deleted {len(gone)} editions, {sum(r['bytes'] for r in gone) / 1e6:.1f} MB, "
          f"logged to {pe._under_root(args.ledger or pe.LEDGER)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
