#!/usr/bin/env python3
r"""link-check.py — work through the catalogue's source links a slice at a time, and say which are dead.

*(Bill, 2026-11-17.)* A catalogue entry's link is the URL in OSINT's raw record, and nothing
checked that it still resolved: a reader found the newest entry, a BusinessDay SENS page,
returning 404. **This finds dead links; it does not mend them.** The URL is OSINT's frontmatter,
so a confirmed dead link goes to OSINT as one `[ACT]` note per batch (`CYCLE.md` step 1b).

**The poll runs a slice every tick** (`--limit`, `--minutes`), so it costs no model turn. Each
slice takes, in order: suspects due their second check, links never checked, then the
oldest-checked link past `RECHECK_DAYS`. Hosts run in parallel; requests to one host are
spaced `HOST_GAP` seconds apart. The state is `logs/link-check.csv`, which is gitignored: it
changes every ten minutes all night, and losing it costs only a re-check. A batch sent to
OSINT, `logs/link-dead/<date>.csv`, is the record and is committed.

**One 404 is not proof a link is dead.** The case that started this was an outage: every SENS
page on BusinessDay returned 404 while its listing loaded. So:

- **dead** means `gone` (404, 410 or a name that no longer resolves) on two checks at least
  `CONFIRM_DAYS` apart, with nothing better between;
- **host-down**: when most of a host's links fail in the same slice, the host is down, not
  the links, and those failures do not count;
- **blocked** (401, 403, 429, a bot wall) and **error** (timeouts, 5xx, TLS) mean "could not
  check". Neither ever becomes dead.

**The note** (`CYCLE.md` step 1b): `[ACT]`, `Affects: site/catalogue/`, naming the batch as
`Y:\logs\link-dead\<date>.csv`. It asks OSINT to put each row's `archive` URL in the record's
`url` and keep the old one in `url_note`; where `archive` is `none`, to record the dead link in
`url_note` and leave `url` alone. A row OSINT changes drops out of the catalogue's link set, so
the batch closes itself.

For each confirmed dead link it asks the Wayback Machine for the snapshot nearest the source's
publication date, so the note can name the replacement.

    python scripts/link-check.py run [--limit 100] [--minutes 4]   # one slice (the poll's call)
    python scripts/link-check.py summary                            # counts by state
    python scripts/link-check.py owed                               # dead links not yet sent; exit 1 if any
    python scripts/link-check.py batch                              # write logs/link-dead/<today>.csv, mark them sent

Exit 0 normally; `owed` exits 1 when a batch is owed; 2 when the catalogue cannot be read.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import io
import json
import os
import random
import sys
import threading
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE = os.path.join(ROOT, "outputs", "catalogue", "raw-catalogue.json")
STATE = os.path.join(ROOT, "logs", "link-check.csv")
BATCHES = os.path.join(ROOT, "logs", "link-dead")
LOCK = os.path.join(ROOT, "logs", ".link-check.lock")

HOST_GAP = 5          # seconds between two requests to one host
WORKERS = 12          # hosts checked at once
RECHECK_DAYS = 30     # a good link is looked at again after this
CONFIRM_DAYS = 7      # a failure is confirmed by a second one at least this far on
DOWN_SHARE = 0.8      # this share of a host's links failing in one slice: the host is down
DOWN_MIN = 3          # ... once at least this many of its links were checked
LOCK_STALE = 30 * 60

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
COLS = ["url", "slugs", "published", "state", "code", "checked", "fails",
        "first_fail", "archive", "sent"]
BATCH_COLS = ["slug", "url", "published", "first_fail", "last_fail", "code", "archive"]

GONE = {404, 410}
BLOCKED = {401, 403, 405, 406, 429, 451, 999}


def today() -> str:
    return dt.date.today().isoformat()


def days_between(a: str, b: str) -> int:
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days


def host(url: str) -> str:
    return urllib.parse.urlsplit(url).netloc.lower()


# --- state -----------------------------------------------------------------------------

def catalogue() -> dict[str, dict]:
    """url -> {slugs, published} for every http(s) link the catalogue serves."""
    try:
        items = json.load(open(CATALOGUE, encoding="utf-8"))["items"]
    except (OSError, ValueError, KeyError) as e:
        print(f"link-check: cannot read {CATALOGUE}: {e}", file=sys.stderr)
        sys.exit(2)
    out: dict[str, dict] = {}
    for it in items:
        u = (it.get("url") or "").strip()
        if not u.lower().startswith(("http://", "https://")):
            continue
        row = out.setdefault(u, {"slugs": [], "published": it.get("published") or ""})
        row["slugs"].append(it["slug"])
    return out


def load() -> dict[str, dict]:
    try:
        with open(STATE, encoding="utf-8", newline="") as fh:
            return {r["url"]: r for r in csv.DictReader(fh)}
    except FileNotFoundError:
        return {}


def save(state: dict[str, dict]) -> None:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    for u in sorted(state):
        w.writerow({c: state[u].get(c, "") for c in COLS})
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(buf.getvalue())
    os.replace(tmp, STATE)


def merge(state: dict[str, dict], cat: dict[str, dict]) -> dict[str, dict]:
    """The catalogue decides which links exist: a link OSINT replaced or retired drops out,
    which is how a sent batch closes itself."""
    out = {}
    for u, c in cat.items():
        r = dict(state.get(u) or {"url": u, "state": "", "fails": "0"})
        r["slugs"] = ";".join(sorted(c["slugs"]))
        r["published"] = c["published"]
        out[u] = r
    return out


def is_dead(r: dict) -> bool:
    return r.get("state") == "gone" and int(r.get("fails") or 0) >= 2 \
        and days_between(r["first_fail"], r["checked"]) >= CONFIRM_DAYS


# --- one slice ---------------------------------------------------------------------------

def due(state: dict[str, dict], now: str) -> list[str]:
    suspects, fresh, stale = [], [], []
    for u, r in state.items():
        if r.get("sent") or is_dead(r):
            continue
        if not r.get("checked"):
            fresh.append(u)
        elif r.get("state") == "gone":
            if days_between(r["checked"], now) >= CONFIRM_DAYS:
                suspects.append(u)
        elif days_between(r["checked"], now) >= RECHECK_DAYS:
            stale.append(u)
    random.shuffle(fresh)       # a fresh catalogue is checked evenly across hosts, not host by host
    stale.sort(key=lambda u: state[u]["checked"])
    return suspects + fresh + stale


def probe(session, url: str) -> tuple[str, str]:
    """(state, code) for one GET that reads no body."""
    import requests
    try:
        with session.get(url, stream=True, timeout=(10, 25), allow_redirects=True) as r:
            code = r.status_code
            server = r.headers.get("server", "").lower()
    except requests.exceptions.ConnectionError as e:
        text = str(e)
        if "NameResolution" in text or "getaddrinfo" in text or "Name or service" in text:
            return "gone", "dns"
        if "SSL" in text or "certificate" in text.lower():
            return "error", "tls"
        return "error", "conn"
    except requests.exceptions.Timeout:
        return "error", "timeout"
    except requests.exceptions.RequestException as e:
        return "error", type(e).__name__
    if code < 400:
        return "ok", str(code)
    if code in GONE:
        return "gone", str(code)
    if code in BLOCKED or (code == 503 and "cloudflare" in server):
        return "blocked", str(code)
    return "error", str(code)


def run(limit: int, minutes: float) -> str:
    import requests
    now = today()
    state = merge(load(), catalogue())
    queue = due(state, now)[:limit]
    by_host: dict[str, list[str]] = {}
    for u in queue:
        by_host.setdefault(host(u), []).append(u)
    deadline = time.monotonic() + minutes * 60
    results: dict[str, tuple[str, str]] = {}
    lock = threading.Lock()

    def work(urls: list[str]) -> None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept": "text/html,application/pdf,*/*;q=0.8"})
        for i, u in enumerate(urls):
            if time.monotonic() > deadline:
                return
            if i:
                time.sleep(HOST_GAP)
            res = probe(s, u)
            with lock:
                results[u] = res

    with cf.ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(work, by_host.values()))

    # A host failing wholesale in this slice is down; its links are not judged tonight.
    down = set()
    for h, urls in by_host.items():
        got = [results[u][0] for u in urls if u in results]
        if len(got) >= DOWN_MIN and sum(g == "gone" for g in got) / len(got) >= DOWN_SHARE:
            down.add(h)

    for u, (st, code) in results.items():
        r = state[u]
        if st == "gone" and host(u) in down:
            st = "host-down"
        prev = int(r.get("fails") or 0)
        if st == "gone":
            r["fails"] = str(prev + 1)
            r["first_fail"] = r.get("first_fail") or now
        elif st == "ok":
            r["fails"], r["first_fail"] = "0", ""
        # blocked, error, host-down: leave the failure count where it stood
        if st in ("blocked", "error", "host-down") and r.get("state") == "gone":
            pass  # keep the suspect a suspect; checked moves on so it is retried in a week
        else:
            r["state"] = st
        r["code"], r["checked"] = code, now
        if is_dead(r) and not r.get("archive"):
            r["archive"] = wayback(u, r.get("published", ""))

    save(state)
    tally: dict[str, int] = {}
    for st, _ in results.values():
        tally[st] = tally.get(st, 0) + 1
    parts = ", ".join(f"{k} {v}" for k, v in sorted(tally.items()))
    hd = f"; host down: {', '.join(sorted(down))}" if down else ""
    dead = sum(1 for r in state.values() if is_dead(r) and not r.get("sent"))
    return f"links: checked {len(results)} ({parts or 'none due'}){hd}; dead owed {dead}"


def wayback(url: str, published: str) -> str:
    """The Wayback snapshot nearest publication, or `none`; empty when the lookup failed."""
    import requests
    ts = published.replace("-", "")[:8] or "2026"
    try:
        r = requests.get("https://archive.org/wayback/available",
                         params={"url": url, "timestamp": ts}, timeout=30,
                         headers={"User-Agent": UA})
        snap = r.json().get("archived_snapshots", {}).get("closest") or {}
    except Exception:
        return ""
    if snap.get("available") and str(snap.get("status", "")).startswith("2"):
        return snap["url"].replace("http://web.archive.org", "https://web.archive.org")
    return "none"


# --- reporting ---------------------------------------------------------------------------

def owed(state: dict[str, dict]) -> list[dict]:
    return [r for r in state.values() if is_dead(r) and not r.get("sent")]


def batch(state: dict[str, dict]) -> str:
    rows = owed(state)
    if not rows:
        return ""
    for r in rows:
        if not r.get("archive"):
            r["archive"] = wayback(r["url"], r.get("published", ""))
    os.makedirs(BATCHES, exist_ok=True)
    path = os.path.join(BATCHES, f"{today()}.csv")
    existing = []
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as fh:
            existing = list(csv.DictReader(fh))
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=BATCH_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(existing)
        for r in sorted(rows, key=lambda r: r["slugs"]):
            for slug in r["slugs"].split(";"):
                w.writerow({"slug": slug, "url": r["url"], "published": r["published"],
                            "first_fail": r["first_fail"], "last_fail": r["checked"],
                            "code": r["code"], "archive": r.get("archive") or "none"})
            r["sent"] = today()
    save(state)
    return path


def acquire_lock() -> bool:
    try:
        if time.time() - os.path.getmtime(LOCK) > LOCK_STALE:
            os.remove(LOCK)
    except OSError:
        pass
    try:
        os.close(os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        return True
    except FileExistsError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Check the catalogue's source links, a slice at a time.")
    ap.add_argument("cmd", choices=["run", "summary", "owed", "batch"])
    ap.add_argument("--limit", type=int, default=100, help="links per slice")
    ap.add_argument("--minutes", type=float, default=4, help="stop starting requests after this")
    ap.add_argument("--quiet", action="store_true", help="run: print nothing when nothing was due")
    a = ap.parse_args()

    if not acquire_lock():
        if not a.quiet:
            print("links: another check is running")
        return 0
    try:
        if a.cmd == "run":
            line = run(a.limit, a.minutes)
            if not (a.quiet and "checked 0" in line):
                print(line)
            return 0
        state = merge(load(), catalogue())
        if a.cmd == "summary":
            t: dict[str, int] = {}
            for r in state.values():
                k = "dead-sent" if r.get("sent") else "dead" if is_dead(r) else \
                    "suspect" if r.get("state") == "gone" else r.get("state") or "unchecked"
                t[k] = t.get(k, 0) + 1
            print(f"links {len(state)}: " + ", ".join(f"{k} {v}" for k, v in sorted(t.items())))
            return 0
        if a.cmd == "owed":
            n = len(owed(state))
            print(f"dead links owed: {n}")
            return 1 if n else 0
        path = batch(state)
        print(path or "nothing owed")
        return 0
    finally:
        try:
            os.remove(LOCK)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
