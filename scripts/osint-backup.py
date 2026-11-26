#!/usr/bin/env python3
r"""osint-backup.py — copy OSINT's git-ignored evidence from the mirror to a private R2 bucket.

*(Strategic review 2026-11-26, R196.)* OSINT keeps its original documents out of git: every
PDF, Word file, image and zip in `raw/` and `budget-archive/`, about 4,900 files and 28 GB.
Before this script, they had one second copy, the mirror on this laptop, in the same house.
This script copies them to a **second, private bucket**. `r2-sync.py` only writes the public
editions bucket that the Worker serves from. It is the wrong tool and the wrong bucket for this.
OSINT's restore drill (R180) pulls from this copy. That drill is what proves it, and the mirror
is not dropped in any move until it has passed.

**Which files.** The extensions OSINT's `.gitignore` excludes under those two folders:
`.pdf .png .jpg .jpeg .gif .webp .docx .zip`. Its `.xlsx` files are tracked there, so git
already backs them up. The list is held here, not read from OSINT's `.gitignore`: a root
process file is outside what `lint-interface.py` lets a Corpus script read. On 2026-11-26 the
list matched `git check-ignore`, run from scratch on a copy of the rules, file for file (4,900).

**Count before upload.** A folder missing from the mirror reads as empty, not as an error.
So each folder's local count must be at least its floor before anything is sent. The floor is
the bucket's own count under that prefix, or OSINT's baseline while the bucket is empty. A
short count exits 2 with nothing sent.

**Never deletes, never overwrites.** The objects are immutable originals. A file gone from the
mirror stays in the bucket, and a key whose size differs is reported, not replaced, because a
truncated local file must not overwrite the good copy. `--replace` overwrites the mismatches
after a person has looked at them.

**Nightly.** `poll-loop.py` runs `run --quiet --minutes 6` every tick. A tick with nothing new
costs one listing of about five pages. The first 28 GB goes by hand, `run` with no time limit,
in the background. A lock file stops two runs overlapping. Each upload refreshes its time, and
a lock untouched for an hour is stale.

**Credentials.** The same four keys as `r2_client.py`, for the private bucket only, from
`logs/.cloudflare-r2-backup.json` (gitignored), or from the environment as `CF_BACKUP_*`. It
is a separate S3 key pair, scoped to this bucket. The editions key cannot reach it.

Usage:  python scripts/osint-backup.py count            # local counts and floors; no network
        python scripts/osint-backup.py plan             # what a run would send
        python scripts/osint-backup.py run              # send all of it (the first upload)
        python scripts/osint-backup.py run --quiet --minutes 6     # the poll's tick
        python scripts/osint-backup.py verify           # MD5 every object against the mirror

Exit: 0 done or nothing due; 1 credentials or network; 2 a count below its floor.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2_client  # noqa: E402
from osint_lib import MIRROR  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CREDS = ROOT / "logs" / ".cloudflare-r2-backup.json"
STATE = ROOT / "logs" / "osint-backup.json"
LOCK = ROOT / "logs" / ".osint-backup.lock"
LOCK_STALE = 3600

FOLDERS = ("raw", "budget-archive")
EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".docx", ".zip"}
# OSINT's counts in the register, 2026-11-26: 2,862 in raw/ and 2,033 budget PDFs (2,037 files).
BASELINE = {"raw": 2862, "budget-archive": 2037}


def credentials() -> dict:
    keys = ("CF_ACCOUNT_ID", "CF_R2_BUCKET", "CF_R2_ACCESS_KEY_ID", "CF_R2_SECRET_ACCESS_KEY")
    got = {k: os.environ.get(k.replace("CF_", "CF_BACKUP_", 1), "") for k in keys}
    if not all(got.values()) and CREDS.exists():
        held = json.loads(CREDS.read_text(encoding="utf-8"))
        for k in keys:
            got[k] = got[k] or str(held.get(k, ""))
    missing = [k for k, v in got.items() if not v]
    if missing:
        raise LookupError(f"no credential for {', '.join(missing)} — logs/{CREDS.name}")
    if got["CF_R2_BUCKET"] == "editions":
        raise LookupError("the backup bucket must not be the public editions bucket")
    return got


def local_files() -> dict[str, Path]:
    """Every git-ignored file under the two folders, keyed by its path from the mirror's root."""
    mirror = Path(MIRROR)
    found = {}
    for folder in FOLDERS:
        for p in (mirror / folder).rglob("*"):
            if p.suffix.lower() in EXTENSIONS and p.is_file():
                found[p.relative_to(mirror).as_posix()] = p
    return found


def counts(keys) -> dict[str, int]:
    c = {f: 0 for f in FOLDERS}
    for k in keys:
        c[k.split("/", 1)[0]] += 1
    return c


def short_folders(local: dict, remote: dict) -> list[str]:
    """Folders whose local count is under their floor: the bucket's count, or the baseline."""
    have, held = counts(local), counts(remote)
    return [f"{f}: {have[f]} on the mirror, floor {max(held[f], BASELINE[f])}"
            for f in FOLDERS if have[f] < max(held[f], BASELINE[f])]


def take_lock() -> bool:
    try:
        if LOCK.exists() and time.time() - LOCK.stat().st_mtime > LOCK_STALE:
            LOCK.unlink()
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, f"{os.getpid()} {dt.datetime.now():%Y-%m-%d %H:%M}\n".encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False


def save_state(**fields) -> None:
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    state.update(fields, at=dt.datetime.now().isoformat(timespec="seconds"))
    STATE.write_text(json.dumps(state, indent=1), encoding="utf-8")


def gb(n: int) -> str:
    return f"{n / 1e9:.2f} GB"


def main() -> int:
    ap = argparse.ArgumentParser(description="OSINT's git-ignored evidence, to a private bucket.")
    ap.add_argument("command", choices=("count", "plan", "run", "verify"))
    ap.add_argument("--minutes", type=float, default=0, help="run: stop starting uploads after this")
    ap.add_argument("--quiet", action="store_true", help="run: print nothing when nothing was due")
    ap.add_argument("--replace", action="store_true", help="run: overwrite keys whose size differs")
    a = ap.parse_args()

    local = local_files()
    if a.command == "count":
        have = counts(local)
        print(" · ".join(f"{f} {have[f]} (baseline {BASELINE[f]})" for f in FOLDERS)
              + f" · {gb(sum(p.stat().st_size for p in local.values()))}")
        return 2 if any(have[f] < BASELINE[f] for f in FOLDERS) else 0

    try:
        bucket = r2_client.R2(credentials())
        remote = bucket.listing()
    except (LookupError, RuntimeError) as e:
        print(f"osint-backup: {e}")
        return 1
    remote = {k: v for k, v in remote.items() if k.split("/", 1)[0] in FOLDERS}

    short = short_folders(local, remote)
    if short:
        print("osint-backup: count below floor, nothing sent — " + "; ".join(short))
        return 2

    if a.command == "verify":
        bad = [k for k, p in local.items()
               if k in remote and r2_client.etag_of(p.read_bytes()) != remote[k][1]]
        absent = len(local.keys() - remote.keys())
        print(f"osint-backup verify: {len(remote)} held, {len(bad)} differ, {absent} not yet sent")
        for k in bad[:20]:
            print(f"  differs: {k}")
        return 0

    todo = sorted(k for k in local if k not in remote)
    mismatched = sorted(k for k in local if k in remote and local[k].stat().st_size != remote[k][0])
    if a.replace:
        todo += mismatched
    size = sum(local[k].stat().st_size for k in todo)
    if a.command == "plan":
        print(f"osint-backup plan: {len(todo)} to send, {gb(size)}; {len(remote)} held; "
              f"{len(mismatched)} differ in size")
        for k in mismatched[:20]:
            print(f"  size differs: {k}")
        return 0

    if not todo:
        save_state(held=len(remote), local=len(local), mismatched=len(mismatched))
        if not a.quiet or mismatched:
            print(f"osint-backup: all {len(remote)} held"
                  + (f", {len(mismatched)} differ in size" if mismatched else ""))
        return 0
    if not take_lock():
        if not a.quiet:
            print("osint-backup: another run holds the lock")
        return 0
    sent = sent_bytes = new = 0
    start = time.monotonic()
    try:
        for k in todo:
            if a.minutes and time.monotonic() - start > a.minutes * 60:
                break
            p = local[k]
            data = p.read_bytes()
            etag = bucket.put(k, data, r2_client.content_type(p))
            if etag and etag != r2_client.etag_of(data):
                raise RuntimeError(f"{k}: R2 answered ETag {etag}, local MD5 differs")
            sent += 1
            new += k not in remote
            sent_bytes += len(data)
            LOCK.touch()
            if not a.quiet and sent % 50 == 0:
                print(f"  {sent}/{len(todo)} · {gb(sent_bytes)}", flush=True)
    except RuntimeError as e:
        print(f"osint-backup: stopped after {sent} — {e}")
        return 1
    finally:
        LOCK.unlink(missing_ok=True)
        save_state(held=len(remote) + new, local=len(local), mismatched=len(mismatched))
    left = len(todo) - sent
    print(f"osint-backup: sent {sent} ({gb(sent_bytes)}), {left} left; "
          f"{len(remote) + new} of {len(local)} held"
          + (f"; {len(mismatched)} differ in size" if mismatched else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
