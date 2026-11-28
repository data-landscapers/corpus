#!/usr/bin/env python3
r"""maturity-archive.py — a night's maturity working files, sent to the private R2 bucket (R173).

    python scripts/maturity-archive.py _batch            # the night's arrivals batch
    python scripts/maturity-archive.py {id}              # a rebuild's search*/ folders
    python scripts/maturity-archive.py {id} --pull       # the latest archive back, for a rebuild
    python scripts/maturity-archive.py {id} --dry        # what would go, nothing sent

`documentation/git-weight.md` is the decision: `maturity/_batch/` and every study's `search/` and
`search-YYYY-MM-DD/` left git on 2026-11-28 (housekeeping 91), because they are read the night
they are written and never again, while git history keeps every version committed before. The run
that writes them archives them here, one `.tar.gz` a study a night, at
`corpus-maturity-work/{id}/{date}.tar.gz` (`_batch/{date}.tar.gz` for the batch). The local files
are left where they are: deleting a working file is not this script's call.

**The bucket is its own credential scope.** It uses the editions key pair in
`logs/.cloudflare-r2.json` with `CF_R2_WORK_BUCKET` (default `corpus-maturity-work`) in place of
the editions bucket, so the key must be granted that bucket too. **An archive that cannot be sent
never holds a cycle**: it says so and exits 0, and the files stay on disk for the next run.

Exit: 0 archived, pulled, or not reachable (said so); 2 nothing to archive or a bad argument.
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import r2_client  # noqa: E402

MATURITY = os.path.join(ROOT, "maturity")
DEFAULT_BUCKET = "corpus-maturity-work"


def bucket() -> r2_client.R2:
    creds = dict(r2_client.credentials())
    creds["CF_R2_BUCKET"] = os.environ.get("CF_R2_WORK_BUCKET", DEFAULT_BUCKET)
    return r2_client.R2(creds)


def folders(target: str) -> list[str]:
    """The working folders `target` names, relative to `maturity/`."""
    if target == "_batch":
        return ["_batch"] if os.path.isdir(os.path.join(MATURITY, "_batch")) else []
    here = os.path.join(MATURITY, target)
    if not os.path.isfile(os.path.join(here, "study.json")):
        raise SystemExit(f"maturity-archive: no study {target}")
    return sorted(os.path.join(target, d) for d in os.listdir(here)
                  if d == "search" or d.startswith("search-") and os.path.isdir(os.path.join(here, d)))


def pack(rels: list[str]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for rel in rels:
            tar.add(os.path.join(MATURITY, rel), arcname=rel)
    return buf.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Archive a night's maturity working files to R2.")
    ap.add_argument("target", help="a study id, or _batch")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--pull", action="store_true", help="fetch the latest archive and unpack it")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    prefix = f"{a.target}/"
    try:
        b = bucket()
        if a.pull:
            keys = sorted(b.listing(prefix))
            if not keys:
                print(f"maturity-archive: nothing archived under {prefix}")
                return 2
            data = b.get(keys[-1])
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
                tar.extractall(MATURITY, filter="data")
            print(f"maturity-archive: {keys[-1]} unpacked into maturity/")
            return 0
        rels = folders(a.target)
        if not rels:
            print(f"maturity-archive: {a.target} has no working folder")
            return 2
        data = pack(rels)
        key = f"{prefix}{a.date}.tar.gz"
        if a.dry:
            print(f"maturity-archive: {key}, {len(data) / 1e6:.1f} MB from {', '.join(rels)} (dry run)")
            return 0
        b.put(key, data, "application/gzip")
        print(f"maturity-archive: {key}, {len(data) / 1e6:.1f} MB")
        return 0
    except (LookupError, RuntimeError, OSError) as e:
        print(f"maturity-archive: not archived, the bucket is not reachable ({str(e)[:120]}); "
              "the files stay on disk")
        return 0


if __name__ == "__main__":
    sys.exit(main())
