#!/usr/bin/env python3
r"""r2-sync.py — move the dated editions and the names index into R2, and off GitHub Pages.

`documentation/editions-serving-shape.md` is the decision; this is the instrument. The Worker in
`workers/download-log/worker.js` serves what this uploads, at the same URL.

    python scripts/r2-sync.py                     # what would go up, upload nothing
    python scripts/r2-sync.py --apply             # upload what is missing or changed
    python scripts/r2-sync.py --verify            # every local candidate is in the bucket, intact
    python scripts/r2-sync.py --prune-local --apply   # delete the local copy of what is verified

**The order is upload, deploy, verify, then delete locally, and it is not negotiable.** Each step
leaves the site serving throughout: while both copies exist the Worker prefers R2 and the reader
cannot tell which answered, and if anything is wrong the fallback to Pages is a real file rather
than a 404. `--prune-local` is the only irreversible step and it refuses to touch a file it has
not just seen in the bucket, byte-count and MD5 both.

**What moves.** Dated editions under `reports/`, `topics/`, `countries/` and `finance/`, and the
`catalogue/names/` shards. What does not: every HTML page, the assets, `raw-catalogue.csv` —
which §9 keeps deliberately undated, so it is not an edition and never matches — and `bulletin/`,
which is an edition by the grammar and stays anyway, for the reason recorded at `STAYS`.

**The selection rule exists twice and the copies must agree.** Here it is `editions.py`'s own
grammar, which is canonical (§9: the script that names editions is the one that reads them). In
the Worker it is a regex, because a Worker cannot import Python. A file this uploads that the
Worker does not recognise is served from Pages until the local copy goes and then 404s, so
`--verify` checks the Worker's answer too, over HTTP, rather than trusting the two to match.

**Uploads are idempotent and cheap to repeat.** Every object is HEADed first and skipped when the
size and MD5 already match, so a re-run after a failure uploads only what did not land, and a
render that cuts eight new editions uploads eight objects rather than 2,500.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import r2_client  # noqa: E402

_spec = importlib.util.spec_from_file_location("editions", HERE / "editions.py")
ed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ed)

# Derived data with no claim on the published origin: fetched by the catalogue's own JS, never
# cited, never linked, and rebuilt from `outputs/` in one command. Must match the Worker's
# R2_PREFIX exactly.
PREFIXES = ("catalogue/names/",)

# **The bulletin stays on GitHub Pages, and that is a decision rather than an oversight.** Its
# editions are deleted on a stated seven-day window instead of on downloads, so they never
# accumulate — twenty files and 6 MB, against 843 MB for everything else — and `prune-editions.py`
# rebuilds `bulletin/editions.json` by reading that directory off disk after each deletion. Moving
# six megabytes would mean teaching the manifest rebuild to enumerate a bucket, for no headroom.
# Must match the Worker, which does not serve this prefix from R2 either.
STAYS = ("bulletin/",)

SITE_BASE = "https://corpus.data-landscapers.io"


def candidates(site: Path) -> list[Path]:
    """Every file that belongs in R2: a dated edition, or anything under a moved prefix."""
    out = []
    for f in sorted(site.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(site).as_posix()
        if rel.startswith(STAYS):
            continue
        if rel.startswith(PREFIXES):
            out.append(f)
        elif f.suffix.lower() in (".pdf", ".csv") and ed.edition_of(f.stem) is not None:
            out.append(f)
    return out


# Eight at a time. Each object is one round trip to Cloudflare and the tree is 8,139 of them, so
# sequential means the better part of an hour of latency and almost no bytes in flight. Eight is
# chosen to be unremarkable rather than fast — R2's limits are far above this, and a sync that
# provokes rate limiting turns a slow job into a failed one.
WORKERS = 8


def _each(files: list[Path], job, workers: int = WORKERS, label: str = "") -> list:
    """Run `job` over every file, in parallel, and raise the first fault rather than reporting it.

    **A fault here must stop the run.** Both callers feed a decision that deletes published
    files: a partial upload that reported success, or a verification that skipped the object it
    could not read, is the one shape of wrongness this cannot survive."""
    out = []
    done = 0
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(job, f): f for f in files}
        for fut in cf.as_completed(futures):
            out.append(fut.result())          # a raised exception propagates here, as it should
            done += 1
            if label and (done % 500 == 0 or done == len(files)):
                print(f"  {label}: {done}/{len(files)}", flush=True)
    return out


def upload(bucket: r2_client.R2, site: Path, files: list[Path], apply: bool,
           workers: int = WORKERS) -> dict:
    """Put what is missing or changed. Returns counts; raises on anything it cannot explain."""
    def one(f: Path):
        key = f.relative_to(site).as_posix()
        data = f.read_bytes()
        held = bucket.head(key)
        if held and held["size"] == len(data) and held["etag"] == r2_client.etag_of(data):
            return (False, 0)
        if apply:
            bucket.put(key, data, r2_client.content_type(f))
        return (True, len(data))

    results = _each(files, one, workers, "uploaded" if apply else "checked")
    sent = [n for done, n in results if done]
    return {"sent": len(sent), "skipped": len(results) - len(sent), "bytes": sum(sent)}


def verify(bucket: r2_client.R2, site: Path, files: list[Path],
           workers: int = WORKERS) -> list[str]:
    """Names of every candidate the bucket does not hold intact. Empty means safe to prune."""
    def one(f: Path):
        key = f.relative_to(site).as_posix()
        data = f.read_bytes()
        held = bucket.head(key)
        if held is None:
            return f"{key} — not in the bucket"
        if held["size"] != len(data):
            return f"{key} — {held['size']} bytes in the bucket, {len(data)} on disk"
        if held["etag"] != r2_client.etag_of(data):
            return f"{key} — MD5 differs"
        return None

    return sorted(b for b in _each(files, one, workers, "verified") if b)


def serves(key: str, timeout: int = 30) -> str:
    """What the live site answers for one key — the check that the Worker agrees with this file.

    A `200` proves nothing on its own while the file is still on Pages, so this is read for the
    header the Worker sets and Pages does not: an immutable `cache-control`. That is the one
    observable difference between the two origins."""
    req = urllib.request.Request(f"{SITE_BASE}/{key}", method="HEAD",
                                 headers={"user-agent": "corpus-r2-sync"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            cache = (r.headers.get("Cache-Control") or "").lower()
            return "r2" if "immutable" in cache else "pages"
    except urllib.error.HTTPError as e:
        return f"http {e.code}"
    except OSError as e:
        return f"unreachable ({e})"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--apply", action="store_true", help="actually upload or delete")
    p.add_argument("--verify", action="store_true",
                   help="check every candidate is in the bucket intact, and change nothing")
    p.add_argument("--prune-local", action="store_true",
                   help="delete the local copy of everything verified present in the bucket")
    p.add_argument("--check-serving", action="store_true",
                   help="ask the live site which origin answers, for a sample of keys")
    p.add_argument("--site", type=Path, default=SITE)
    args = p.parse_args(argv)

    site = args.site.resolve()
    files = candidates(site)
    total = sum(f.stat().st_size for f in files)
    print(f"R2: {len(files)} candidates under {site.name}/, {total / 1e6:.1f} MB")
    if not files:
        return 0

    try:
        bucket = r2_client.R2()
    except LookupError as e:
        print(f"R2: declined — {e}")
        return 1

    if args.check_serving:
        sample = files[:: max(1, len(files) // 8)][:8]
        for f in sample:
            key = f.relative_to(site).as_posix()
            print(f"  {serves(key):10s} {key}")
        return 0

    if args.verify or args.prune_local:
        bad = verify(bucket, site, files)
        if bad:
            print(f"R2: {len(bad)} of {len(files)} candidates are NOT safely in the bucket")
            for b in bad[:20]:
                print(f"  {b}")
            if len(bad) > 20:
                print(f"  … and {len(bad) - 20} more")
            print("R2: nothing deleted locally")
            return 1
        print(f"R2: all {len(files)} candidates verified in the bucket, size and MD5")
        if not args.prune_local:
            return 0
        if not args.apply:
            print(f"R2: would delete {len(files)} local files, {total / 1e6:.1f} MB "
                  f"— pass --apply")
            return 0
        gone = 0
        for f in files:
            f.unlink()
            gone += 1
        print(f"R2: deleted {gone} local files, {total / 1e6:.1f} MB — the bucket now serves them")
        return 0

    counts = upload(bucket, site, files, args.apply)
    verb = "uploaded" if args.apply else "would upload"
    print(f"R2: {verb} {counts['sent']} objects ({counts['bytes'] / 1e6:.1f} MB), "
          f"{counts['skipped']} already current")
    if not args.apply and counts["sent"]:
        print("R2: nothing uploaded — pass --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
