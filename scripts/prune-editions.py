#!/usr/bin/env python3
r"""prune-editions.py — delete a superseded edition unless somebody downloaded it.

`documentation/cloudflare.md` is the reference for the whole layer; this is the rule it describes,
switched on for **PDFs and CSVs**, **forward only**. §9 of `documentation/design.md` says a
dated URL resolves for ever; under this rule it resolves for ever *if anybody ever took it*.

    python scripts/prune-editions.py              # report what it would delete, delete nothing
    python scripts/prune-editions.py --apply      # delete it

**Retention exists for readers, not for artefacts.** A citation only exists if somebody
actually took the file, so an edition nobody ever fetched has nothing resting on it. Storage
then tracks demand rather than catalogue size — and the catalogue is the thing that grows
without limit, 241 documents each cutting an edition every time its content moves.

**The file never moves.** A downloaded edition stays at the URL it was cited at, because
nothing relocates it; an undownloaded one is deleted. There is no `downloaded/` folder and no
redirect, so no link this rule keeps ever changes address.

**Every uncertainty resolves towards keeping the file.** This is the one place in the repo
where something irreversible acts on a record gathered somewhere else, and the failure is
silent: a deletion that should not have happened looks exactly like one that should, and the
reader who meets the 404 is not someone we hear from. So a missing credential, an API error, a
listing that would not parse, a listing that is suspiciously empty, a Worker that looks dead —
each of them stops the whole run and deletes nothing. There is no partial confidence here.

**Five conditions, all of which must hold before a file is deleted.**

  1. **It is not the current edition.** The newest edition of any document is never touched,
     whatever the record says, because it is what the site is offering right now.
  2. **It was published after the rule existed** (`--from`, default 2026-08-19). The ~1,053
     editions already live were published with no download record kept for the period, so
     applying the rule to them would delete every one of them for want of evidence — the wrong
     direction of failure written large. They stand, for ever; it is a one-off 314 MB.
  3. **It was superseded more than `--lag-days` ago** (default 7). Long enough that a log
     entry which arrived late still arrives before the deletion, and it also covers the reader
     who browses on Monday and downloads on Friday from a link they kept.
  4. **The download record is healthy** — see the liveness and floor checks below.
  5. **Nothing ever fetched it.** Key present in KV, in any casing, human or crawler: keep.

**Any hit at all protects the file, including a crawler's.** The Worker splits `n` from `bots`
rather than filtering, and this reads the split as *keep either way* for two reasons. A bot
causing a keep costs storage, where dropping a real reader's download eventually costs the
file. And the crawler pattern matches `curl`, `wget` and `python-requests`, which is exactly
how a technical reader takes a file they intend to cite. **One consequence is that the values
are never read**: presence of the key is the whole test, so this asks the API only for the key
list — cheaper, and with nothing to misparse.

**Two health checks on the record, because an empty answer and a quiet week look identical.**
`--min-keys` (default 1) refuses to act on an empty listing, which is what a Worker removed
from its route, an unbound namespace and a wrong namespace ID all look like. `--liveness-days`
(default 14) requires that some key in the listing names an edition minted within that window:
a key can only exist after the file it names was minted, so the newest edition date across the
keys is a lower bound on when the Worker last recorded anything. On a genuinely quiet site
this declines to delete — which is the same answer it should give when the Worker is dead,
since from here the two are indistinguishable.

**What this does not fix.** Deleting a PDF from `site/` removes it from the published site and
leaves the blob in `.git` for ever. The saving is against GitHub Pages' soft ceiling of about
1 GB, not against the repository. Getting repository weight back is a different operation
(`documentation/osint-pdf-history-purge.md`).

Credentials, which are secrets and must not be in git: `CF_ACCOUNT_ID`, `CF_KV_NAMESPACE_ID`
and `CF_API_TOKEN` in the environment, or the same three keys in the gitignored
`logs/.cloudflare-kv.json`. The token needs KV **read** scope and nothing more.

Exit: 0 ran (whether it deleted or declined — a refusal is a normal outcome, not a fault),
      1 a fault while deleting or while writing the ledger.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
LEDGER = ROOT / "logs" / "deleted-editions.csv"
CREDS = ROOT / "logs" / ".cloudflare-kv.json"

# The day the download-log Worker was deployed and verified (documentation/cloudflare.md).
# Nothing published on or before it is ever deleted: the record for that day is partial by
# definition, and the whole set behind it has no record at all.
FORWARD_FROM = "2026-08-19"

API = "https://api.cloudflare.com/client/v4"

_spec = importlib.util.spec_from_file_location(
    "editions", Path(__file__).resolve().parent / "editions.py")
ed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ed)


# --------------------------------------------------------------------------- the record

def credentials() -> dict:
    """Account, namespace and token, from the environment or the gitignored file. Never git."""
    got = {k: os.environ.get(k, "") for k in ("CF_ACCOUNT_ID", "CF_KV_NAMESPACE_ID", "CF_API_TOKEN")}
    if all(got.values()):
        return got
    if CREDS.exists():
        held = json.loads(CREDS.read_text(encoding="utf-8"))
        for k in got:
            got[k] = got[k] or str(held.get(k, ""))
    missing = [k for k, v in got.items() if not v]
    if missing:
        raise LookupError(
            f"no credential for {', '.join(missing)} — environment or {_under_root(CREDS)}")
    return got


def kv_keys(creds: dict, timeout: int = 30) -> list[str]:
    """Every key in the `downloads` namespace — the paths that have ever been fetched.

    **A page that fails takes the whole run with it.** Returning what arrived before the error
    would be a listing missing exactly the keys that protect files, which is the one shape of
    wrongness this rule cannot survive, so any fault here raises."""
    keys: list[str] = []
    cursor = ""
    base = (f"{API}/accounts/{creds['CF_ACCOUNT_ID']}/storage/kv/namespaces/"
            f"{creds['CF_KV_NAMESPACE_ID']}/keys")
    while True:
        query = {"limit": 1000}
        if cursor:
            query["cursor"] = cursor
        req = urllib.request.Request(base + "?" + urllib.parse.urlencode(query), headers={
            "Authorization": f"Bearer {creds['CF_API_TOKEN']}",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode("utf-8"))
        if not body.get("success"):
            raise RuntimeError(f"Cloudflare refused the listing: {body.get('errors')}")
        keys.extend(str(k["name"]) for k in body.get("result", []) if k.get("name"))
        cursor = (body.get("result_info") or {}).get("cursor") or ""
        if not cursor:
            return keys


def fetched_set(keys: list[str]) -> set[str]:
    """The keys as paths to match against `site/`, folded for the ways a URL can differ.

    Case and percent-encoding are the two that would silently fail *open* — a key that failed
    to match the file it names would let that file be deleted — so both variants go in."""
    got = set()
    for k in keys:
        path = urllib.parse.unquote(k).lstrip("/")
        got.add(path)
        got.add(path.lower())
    return got


def newest_edition_seen(keys: list[str]) -> str | None:
    """The newest edition date named by any key: a lower bound on the Worker's last activity."""
    dates = [e[:10] for e in (ed.edition_of(Path(k).stem) for k in keys) if e]
    return max(dates) if dates else None


# --------------------------------------------------------------------------- the decision

def editions_on_disk(site: Path) -> dict:
    """Every dated `.pdf`/`.csv` under `site/`, grouped by document, oldest edition first.

    Undated downloads carry no edition and are invisible here — `raw-catalogue.csv` is the
    deliberate one (§9, Bill's call: an index over other people's records is not an edition).
    The stem is what is left after the edition is stripped, which is the test `editions.py`
    uses, and it is what separates `KEN-nonstate` from `KEN-nonstate-fields`."""
    groups: dict = {}
    for f in sorted(site.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in (".pdf", ".csv"):
            continue
        edition = ed.edition_of(f.stem)
        if edition is None:
            continue
        stem = f.stem[: -(len(edition) + 1)]
        groups.setdefault((str(f.parent), stem, f.suffix), []).append((ed.edition_key(edition), f))
    for g in groups.values():
        g.sort()
    return groups


def plan(site: Path, fetched: set[str], today: str, forward_from: str, lag_days: int) -> list[dict]:
    """What is deletable, and why. Pure: it reads the tree and the record and removes nothing."""
    cutoff = dt.date.fromisoformat(today) - dt.timedelta(days=lag_days)
    out = []
    for found in editions_on_disk(site).values():
        for i, (key, path) in enumerate(found):
            rel = path.relative_to(site).as_posix()
            row = {"path": path, "rel": rel, "edition": _name(key), "bytes": 0,
                   "superseded_by": "", "superseded_on": "", "verdict": "", "why": ""}
            if i == len(found) - 1:
                row.update(verdict="keep", why="current edition")
                out.append(row)
                continue
            # The successor is the next edition *still on disk*. Where an intervening one was
            # deleted by an earlier run this reads later than the true supersede date, which
            # only ever holds a file back — the safe direction.
            nxt = found[i + 1][0]
            row["superseded_by"] = _name(nxt)
            row["superseded_on"] = nxt[0]
            if key[0] < forward_from:
                row.update(verdict="keep", why="published before the rule")
            elif dt.date.fromisoformat(nxt[0]) > cutoff:
                row.update(verdict="keep", why=f"superseded within the {lag_days}-day lag")
            elif rel in fetched or rel.lower() in fetched:
                row.update(verdict="keep", why="downloaded")
            else:
                row.update(verdict="delete", why="never fetched")
            out.append(row)
    return sorted(out, key=lambda r: r["rel"])


def _name(key: tuple) -> str:
    """An edition key back as it is written in a filename — `-1` is never spelled out (§9)."""
    return f"{key[0]}-{key[1]}" if key[1] > 1 else key[0]


# --------------------------------------------------------------------------- the act

def _under_root(path: Path) -> str:
    """A path as this repo writes it, and the path itself when it is not in the repo."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def write_ledger(rows: list[dict], when: str, ledger: Path | None = None) -> None:
    """Append what was deleted. Git keeps the blob; this keeps the account a person can read."""
    ledger = ledger or LEDGER
    ledger.parent.mkdir(parents=True, exist_ok=True)
    fresh = not ledger.exists()
    with ledger.open("a", encoding="utf-8", newline="\n") as fh:
        if fresh:
            fh.write("deleted_on,path,edition,superseded_by,superseded_on,bytes\n")
        for r in rows:
            fh.write(f"{when},{r['rel']},{r['edition']},{r['superseded_by']},"
                     f"{r['superseded_on']},{r['bytes']}\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Delete a superseded edition unless somebody downloaded it.")
    p.add_argument("--apply", action="store_true",
                   help="actually delete; without it nothing is removed")
    p.add_argument("--lag-days", type=int, default=7,
                   help="only delete an edition superseded longer ago than this (default 7)")
    p.add_argument("--from", dest="forward_from", default=FORWARD_FROM,
                   help="earliest edition date the rule may touch (default: the day after the Worker went live)")
    p.add_argument("--liveness-days", type=int, default=14,
                   help="require a key naming an edition this recent, as proof the record is still written; 0 disables")
    p.add_argument("--min-keys", type=int, default=1,
                   help="refuse to act on a listing shorter than this (default 1)")
    p.add_argument("--keys-from", metavar="FILE",
                   help="read the key list from a file instead of the API (testing)")
    p.add_argument("--today", default=dt.date.today().isoformat(), help="override the run date (testing)")
    p.add_argument("--site", default=str(SITE), help="the published tree to prune")
    p.add_argument("--ledger", default=None,
                   help="where to record the deletions (default logs/deleted-editions.csv); a rehearsal "
                        "against a scratch tree should point this somewhere else than the site's own account")
    args = p.parse_args(argv)

    site = Path(args.site)
    if not site.is_dir():
        print(f"PRUNE: no site tree at {site} — nothing to do")
        return 0

    try:
        if args.keys_from:
            keys = [ln.strip() for ln in Path(args.keys_from).read_text(encoding="utf-8").splitlines() if ln.strip()]
        else:
            keys = kv_keys(credentials())
    except Exception as e:                       # noqa: BLE001 — every fault has the same answer
        print(f"PRUNE: declined, deleted nothing — the download record could not be read ({e})")
        return 0

    if len(keys) < args.min_keys:
        print(f"PRUNE: declined, deleted nothing — the download record holds {len(keys)} keys, "
              f"below the floor of {args.min_keys}. An empty record and a broken Worker look the same.")
        return 0

    if args.liveness_days > 0:
        newest = newest_edition_seen(keys)
        floor = (dt.date.fromisoformat(args.today) - dt.timedelta(days=args.liveness_days)).isoformat()
        if newest is None or newest < floor:
            print(f"PRUNE: declined, deleted nothing — the newest edition in the record is "
                  f"{newest or 'none'}, older than {floor}. A quiet site and a dead Worker look the same.")
            return 0

    rows = plan(site, fetched_set(keys), args.today, args.forward_from, args.lag_days)
    doomed = [r for r in rows if r["verdict"] == "delete"]
    for r in doomed:
        r["bytes"] = r["path"].stat().st_size
    freed = sum(r["bytes"] for r in doomed)

    print(f"PRUNE: {len(rows)} editions on disk, {len(keys)} paths in the download record, "
          f"{len(rows) - len(doomed)} kept, {len(doomed)} deletable ({freed / 1e6:.1f} MB)")
    for r in doomed:
        print(f"  {'delete' if args.apply else 'would delete'}  {r['rel']}  "
              f"(superseded {r['superseded_on']} by {r['superseded_by']}, never fetched)")
    if not args.apply:
        if doomed:
            print("Nothing was deleted: run again with --apply.")
        return 0

    ledger = Path(args.ledger) if args.ledger else LEDGER
    gone = []
    for r in doomed:
        try:
            r["path"].unlink()
            gone.append(r)
        except OSError as e:
            print(f"PRUNE FAIL: {r['rel']} — {e}")
    if gone:
        try:
            write_ledger(gone, args.today, ledger)
        except OSError as e:
            print(f"PRUNE FAIL: deleted {len(gone)} files but could not write the ledger — {e}")
            return 1
        print(f"PRUNE: deleted {len(gone)} editions, {sum(r['bytes'] for r in gone) / 1e6:.1f} MB, "
              f"recorded in {_under_root(ledger)}")
    return 1 if len(gone) != len(doomed) else 0


if __name__ == "__main__":
    sys.exit(main())
