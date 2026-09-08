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
(`documentation/archived/osint-pdf-history-purge.md`).

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bulletin_editions as ba  # noqa: E402

# The bulletin's directory, the one document kind this rule treats differently. Matched on the
# path rather than on the filename so that a scratch tree passed to `--site` behaves the same.
BULLETIN_DIR = "bulletin"


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
    uses, and it is what separates `KEN-nonstate` from `KEN-nonstate-fields`.

    **The group key is the directory *relative to the tree*, not the absolute parent**, so that
    editions of one document group together whether they are found on disk or in the bucket
    (`editions_in_bucket`). During the migration a document has editions in both, and a key that
    disagreed between the two sources would split it into two documents — each with its own
    "current edition", and the older of the two would be kept for ever while the newer went."""
    groups: dict = {}
    for f in sorted(site.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in (".pdf", ".csv"):
            continue
        edition = ed.edition_of(f.stem)
        if edition is None:
            continue
        stem = f.stem[: -(len(edition) + 1)]
        where = f.parent.relative_to(site).as_posix()
        groups.setdefault((where, stem, f.suffix), []).append((ed.edition_key(edition), f))
    for g in groups.values():
        g.sort()
    return groups


class BucketEdition:
    """An edition that lives in R2 rather than on disk, presenting what `plan` needs of it.

    `documentation/editions-serving-shape.md`. After the move the published tree no longer holds
    the editions, so a pruner that only walked `site/` would find nothing to consider and would
    report a clean run for ever — retention silently switched off, which is exactly the failure
    the liveness checks exist to make impossible on the record side."""

    __slots__ = ("key", "size", "_bucket")

    def __init__(self, key: str, size: int, bucket):
        self.key, self.size, self._bucket = key, size, bucket

    def unlink(self) -> None:
        self._bucket.delete(self.key)

    def __repr__(self) -> str:
        return f"BucketEdition({self.key!r})"


class BothStores:
    """One edition that is currently in two places, and must leave both or neither.

    **This shape exists only during the migration**, between `r2-sync.py --apply` putting a copy
    in the bucket and `--prune-local` taking the copy off disk. It has to be handled and cannot
    be ignored in either direction: two rows for one edition would let the pruner treat a file as
    superseding itself and delete the copy it had just decided to keep, while deleting one store
    and not the other leaves the Worker's Pages fallback still serving a file the rule has
    retired. So the two are one row, and `unlink` empties both."""

    __slots__ = ("items",)

    def __init__(self, items):
        self.items = list(items)

    @property
    def key(self) -> str:
        for i in self.items:
            if isinstance(i, BucketEdition):
                return i.key
        return ""

    @property
    def size(self) -> int:
        return max((i.size if isinstance(i, BucketEdition) else i.stat().st_size)
                   for i in self.items)

    def unlink(self) -> None:
        for i in self.items:
            i.unlink()


def merge_groups(disk: dict, bucket_groups: dict) -> dict:
    """Disk and bucket editions as one set of documents, one row per edition.

    The group key is the relative directory, which both sources spell the same way, so a document
    half-migrated is still one document with one current edition."""
    merged: dict = {}
    for source in (disk, bucket_groups):
        for gk, found in source.items():
            merged.setdefault(gk, {})
            for ekey, item in found:
                merged[gk].setdefault(ekey, []).append(item)
    out: dict = {}
    for gk, editions in merged.items():
        rows = []
        for ekey, items in editions.items():
            rows.append((ekey, items[0] if len(items) == 1 else BothStores(items)))
        rows.sort(key=lambda t: t[0])
        out[gk] = rows
    return out


def editions_in_bucket(bucket, prefixes=("reports/", "topics/", "countries/", "finance/")) -> dict:
    """Every dated edition in R2, grouped exactly as `editions_on_disk` groups the tree.

    Only the trees that hold editions are listed. `catalogue/names/` is in the same bucket and is
    not an edition — it is derived data with no retention rule — and listing it here would put
    thousands of objects in front of a deletion rule that has no business considering them."""
    groups: dict = {}
    for prefix in prefixes:
        for key, size in bucket.list(prefix).items():
            name = key.rsplit("/", 1)[-1]
            stem, _, ext = name.rpartition(".")
            ext = "." + ext.lower()
            if ext not in (".pdf", ".csv"):
                continue
            edition = ed.edition_of(stem)
            if edition is None:
                continue
            where = key.rsplit("/", 1)[0] if "/" in key else ""
            groups.setdefault((where, stem[: -(len(edition) + 1)], ext), []).append(
                (ed.edition_key(edition), BucketEdition(key, size, bucket)))
    for g in groups.values():
        g.sort(key=lambda t: t[0])
    return groups


def is_bulletin(path: Path, site: Path) -> bool:
    return path.parent.name == BULLETIN_DIR and path.suffix.lower() == ".pdf"


def plan(site: Path, fetched: set[str], today: str, forward_from: str, lag_days: int,
         retention_days: int = ba.RETENTION_DAYS, record_ok: bool = True,
         groups: dict | None = None) -> list[dict]:
    """What is deletable, and why. Pure: it reads the tree and the record and removes nothing.

    **The bulletin leaves this rule and takes a stated retention window instead. It is not
    subject to both** (`documentation/bulletin-archive.md`). Condition 5 keeps for ever anything
    anybody ever fetched; if bulletins merely *gained* a window on top of that, the one-week
    promise printed in their own colophon would hold for every bulletin except the ones a reader
    actually took — the files someone cared about would be the files that outlived the policy,
    and the page would be false in precisely the cases that matter. So the window replaces the
    download test here; it does not join it.

    That is defensible for the bulletin and for nothing else. It is the one document that is
    explicitly not an archive (`documentation/bulletin.md` → *What it is not*) and whose content
    is fully kept elsewhere — the country pages hold a month, the monthly reports hold the month,
    the catalogue holds every record, git holds every version. A report's superseded edition is
    the only copy of what that report used to say; a bulletin's is not.

    Of the five conditions the bulletin keeps only the first. It is never the current edition
    that goes — the live page must always be able to offer its own PDF, even after a quiet month
    — and the window is measured on the **edition date**, not on supersession, because a bulletin
    is superseded within hours by its own next cut. A lag from supersession would give each
    edition a week, but a different week each, and never the week the colophon named."""
    cutoff = dt.date.fromisoformat(today) - dt.timedelta(days=lag_days)
    out = []
    if groups is None:
        groups = editions_on_disk(site)
    for found in groups.values():
        for i, (key, path) in enumerate(found):
            on_disk = isinstance(path, Path)
            rel = path.relative_to(site).as_posix() if on_disk else path.key
            row = {"path": path, "rel": rel, "edition": _name(key), "bytes": 0,
                   "superseded_by": "", "superseded_on": "", "verdict": "", "why": "",
                   "size": (lambda p=path: p.stat().st_size) if on_disk
                           else (lambda p=path: p.size),
                   "remove": path.unlink}
            if i == len(found) - 1:
                row.update(verdict="keep", why="current edition")
                out.append(row)
                continue
            if on_disk and is_bulletin(path, site):
                if ba.within_window(_name(key), today, retention_days):
                    row.update(verdict="keep",
                               why=f"inside the {retention_days}-day bulletin window")
                else:
                    row.update(verdict="delete",
                               why=f"past the {retention_days}-day bulletin window")
                out.append(row)
                continue
            # The successor is the next edition *still on disk*. Where an intervening one was
            # deleted by an earlier run this reads later than the true supersede date, which
            # only ever holds a file back — the safe direction.
            nxt = found[i + 1][0]
            row["superseded_by"] = _name(nxt)
            row["superseded_on"] = nxt[0]
            if not record_ok:
                # Everything except the bulletin, handled above, needs the download record and
                # keeps without it. The refusal is per-row rather than per-run so that a machine
                # with no Cloudflare token still honours the retention the bulletin's own
                # colophon prints, which is a promise made to a reader and not a housekeeping
                # preference.
                row.update(verdict="keep", why="download record not available")
            elif key[0] < forward_from:
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
    p.add_argument("--retention-days", type=int, default=ba.RETENTION_DAYS,
                   help=f"how long a bulletin edition is kept, from its edition date "
                        f"(default {ba.RETENTION_DAYS}); the number its colophon prints")
    p.add_argument("--no-r2", action="store_true",
                   help="prune the tree only and never open the bucket (testing, and a scratch tree)")
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

    # **A bad record no longer stops the whole run — it stops everything the record governs.**
    # The bulletin is pruned on a stated window rather than on downloads, so a missing token or
    # a dead Worker must not silently suspend a retention promise printed on the page. Every
    # other document keeps, exactly as before, and the reason is printed either way.
    keys: list[str] = []
    record_ok, declined = True, ""
    try:
        if args.keys_from:
            keys = [ln.strip() for ln in Path(args.keys_from).read_text(encoding="utf-8").splitlines() if ln.strip()]
        else:
            keys = kv_keys(credentials())
    except Exception as e:                       # noqa: BLE001 — every fault has the same answer
        record_ok, declined = False, f"the download record could not be read ({e})"

    if record_ok and len(keys) < args.min_keys:
        record_ok, declined = False, (
            f"the download record holds {len(keys)} keys, below the floor of {args.min_keys}. "
            f"An empty record and a broken Worker look the same.")

    if record_ok and args.liveness_days > 0:
        newest = newest_edition_seen(keys)
        floor = (dt.date.fromisoformat(args.today) - dt.timedelta(days=args.liveness_days)).isoformat()
        if newest is None or newest < floor:
            record_ok, declined = False, (
                f"the newest edition in the record is {newest or 'none'}, older than {floor}. "
                f"A quiet site and a dead Worker look the same.")

    if not record_ok:
        print(f"PRUNE: download-governed retention declined — {declined}")
        print("       The bulletin's own window is unaffected and is applied below.")

    # **After the move most editions are in R2 and not in the tree**, so a pruner that only
    # walked `site/` would find nothing to consider and report a clean run for ever — retention
    # switched off in silence, which is the exact failure the record's liveness checks exist to
    # prevent on the other side. The bucket is therefore listed and merged with the tree.
    groups = editions_on_disk(site)
    where_from = "on disk"
    if not args.no_r2:
        try:
            import r2_client                                       # noqa: PLC0415 — optional
            bucket = r2_client.R2()
        except LookupError:
            # No R2 credentials at all: this machine predates the move, or is a scratch tree.
            # Disk-only is exactly the old behaviour and is correct, so it is not a refusal.
            bucket = None
        except Exception as e:                                     # noqa: BLE001
            bucket = None
            print(f"PRUNE: the bucket could not be opened ({e}) — pruning the tree only")
        if bucket is not None:
            try:
                in_bucket = editions_in_bucket(bucket)
                groups = merge_groups(groups, in_bucket)
                where_from = (f"across the tree and the bucket "
                              f"({sum(len(v) for v in in_bucket.values())} in R2)")
            except Exception as e:                                 # noqa: BLE001
                # The bucket exists but would not list. Falling back to the tree cannot delete
                # anything wrongly — an edition whose successor is only in R2 simply looks
                # current and is kept — but it does mean the bucket is not being pruned, and
                # that must be said rather than discovered later as a bill.
                print(f"PRUNE: the bucket would not list ({e}) — pruning the tree only. "
                      f"Nothing in R2 is being retired; this wants looking at.")

    rows = plan(site, fetched_set(keys), args.today, args.forward_from, args.lag_days,
                args.retention_days, record_ok=record_ok, groups=groups)
    doomed = [r for r in rows if r["verdict"] == "delete"]
    for r in doomed:
        r["bytes"] = r["size"]()
    freed = sum(r["bytes"] for r in doomed)

    print(f"PRUNE: {len(rows)} editions {where_from}, {len(keys)} paths in the download record, "
          f"{len(rows) - len(doomed)} kept, {len(doomed)} deletable ({freed / 1e6:.1f} MB)")
    for r in doomed:
        print(f"  {'delete' if args.apply else 'would delete'}  {r['rel']}  ({r['why']})")
    if not args.apply:
        if doomed:
            print("Nothing was deleted: run again with --apply.")
        return 0

    ledger = Path(args.ledger) if args.ledger else LEDGER
    gone = []
    for r in doomed:
        try:
            r["remove"]()
            gone.append(r)
        except (OSError, RuntimeError) as e:
            # RuntimeError is `r2_client`'s: a bucket delete that the API refused. It is reported
            # and skipped like a failed unlink — the edition stays, which is the safe direction.
            print(f"PRUNE FAIL: {r['rel']} — {e}")
    if gone:
        try:
            write_ledger(gone, args.today, ledger)
        except OSError as e:
            print(f"PRUNE FAIL: deleted {len(gone)} files but could not write the ledger — {e}")
            return 1
        print(f"PRUNE: deleted {len(gone)} editions, {sum(r['bytes'] for r in gone) / 1e6:.1f} MB, "
              f"recorded in {_under_root(ledger)}")

    # **The party doing the deleting owns the listing** (`documentation/bulletin-archive.md`).
    # Leaving it to the next render opens a window — between `RENDER.md` Step 6a and whenever
    # the bulletin next renders — in which the picker offers a file that is gone. Prune is
    # already writing a ledger, so this is one more write inside an operation it is doing
    # anyway. Rebuilt rather than edited: the rebuild drops whatever is no longer on disk,
    # which is the same self-healing pass the renderer runs and needs no list of what went.
    if any(isinstance(r["path"], Path) and is_bulletin(r["path"], site) for r in gone):
        bulletin_dir = site / BULLETIN_DIR
        try:
            entries = ba.refreshed(bulletin_dir, args.today, retention_days=args.retention_days)
            ba.save(bulletin_dir, entries, args.retention_days)
            print(f"PRUNE: bulletin archive rewritten — {len(entries)} edition(s) listed")
        except OSError as e:
            print(f"PRUNE FAIL: deleted the files but could not rewrite "
                  f"{_under_root(ba.manifest_path(bulletin_dir))} — {e}")
            return 1
    return 1 if len(gone) != len(doomed) else 0


if __name__ == "__main__":
    sys.exit(main())
