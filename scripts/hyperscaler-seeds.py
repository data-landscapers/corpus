#!/usr/bin/env python3
r"""hyperscaler-seeds.py — confirm and lint one country's seed list for the hyperscaler scan.

Step 01 of `R&D/Hyperscaler-dependence/HYPERSCALER-DRAIN.md`. Two subcommands:

    python scripts/hyperscaler-seeds.py confirm "R&D/Hyperscaler-dependence/institutions-GHA.csv"
    python scripts/hyperscaler-seeds.py lint    "R&D/Hyperscaler-dependence/institutions-GHA.csv"

`confirm` fetches the homepage of every row that has a domain and no `confirmed` status, trying
https and http, bare and `www.`. Any HTTP answer — a 403 from a WAF included — confirms the domain
is served, and the row becomes `confirmed YYYY-MM-DD`; a certificate error is retried unverified,
because a broken certificate is a fact about the site, not its absence. A row nothing answers
becomes `unconfirmed YYYY-MM-DD` with the error in `note`, and is still scanned at step 02, whose
DNS pass is what decides `dead`. It prints status, final host and page title per row so a parked or
repurposed domain can be caught by eye; the script does not judge that. **No DNS lookup is made
beyond what the HTTP client does to connect** — the runbook reserves DNS for step 02.

`lint` checks what the runbook asks: the exact header, no duplicate `domain`, every type in
`strategic-institutions.csv` present at least once, no more than twelve bank rows. Exit 1 on a breach.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import re
import sys
import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

warnings.filterwarnings("ignore")

HERE = Path("R&D/Hyperscaler-dependence")
HEADER = ["type", "institution", "domain", "email_domain", "status", "note"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


def read(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def write(path: Path, rows: list[dict]) -> None:
    # Written to a sibling and swapped in, so a crash mid-write never truncates the seed list.
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


def fetch(domain: str) -> tuple[bool, str]:
    err = ""
    for url in (f"https://{domain}/", f"https://www.{domain}/", f"http://{domain}/", f"http://www.{domain}/"):
        for verify in (True, False):
            try:
                r = requests.get(url, timeout=20, headers={"User-Agent": UA}, verify=verify, allow_redirects=True)
                m = TITLE_RE.search(r.text[:200000])
                title = html.unescape(re.sub(r"\s+", " ", m.group(1))).strip()[:80] if m else ""
                host = requests.utils.urlparse(r.url).hostname or ""
                return True, f"{r.status_code} {host} | {title}"
            except requests.exceptions.SSLError as e:
                err = f"ssl: {type(e).__name__}"
                continue
            except requests.RequestException as e:
                err = type(e).__name__
                break
    return False, err


def confirm(path: Path) -> int:
    _, rows = read(path)
    today = dt.date.today().isoformat()
    todo = [r for r in rows if r["domain"].strip() and not r["status"].startswith("confirmed")]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda r: fetch(r["domain"].strip()), todo))
    for r, (ok, info) in zip(todo, results):
        if ok:
            r["status"] = f"confirmed {today}"
        else:
            r["status"] = f"unconfirmed {today}"
            if "homepage did not load" not in r["note"]:
                r["note"] = "; ".join(x for x in (r["note"], f"homepage did not load: {info}") if x)
        print(f"{'OK ' if ok else 'ERR'} {r['domain']:<40} {info}")
    write(path, rows)
    return 0


def lint(path: Path) -> int:
    header, rows = read(path)
    bad = []
    if header != HEADER:
        bad.append(f"header is {','.join(header)}")
    seen: dict[str, int] = {}
    for r in rows:
        d = r["domain"].strip().lower()
        if d:
            seen[d] = seen.get(d, 0) + 1
    bad += [f"duplicate domain {d}" for d, n in seen.items() if n > 1]
    _, types = read(HERE / "strategic-institutions.csv")
    have = {r["type"] for r in rows}
    bad += [f"no row for type {t['institution']}" for t in types if t["institution"] not in have]
    banks = sum(1 for r in rows if r["type"] == "Commercial Banks")
    if banks > 12:
        bad.append(f"{banks} bank rows")
    for r in rows:
        if not r["domain"].strip() and r["status"] != "absent":
            bad.append(f"blank domain without status absent: {r['type']}")
        if r["domain"].strip() and not re.match(r"^(confirmed|unconfirmed) \d{4}-\d{2}-\d{2}$", r["status"]):
            bad.append(f"domain {r['domain']} status '{r['status']}'")
    for b in bad:
        print(f"LINT {path.name}: {b}")
    n = sum(1 for r in rows if r["domain"].strip())
    print(f"{path.name}: {len(rows)} rows, {n} domains, {banks} banks, "
          f"{sum(1 for r in rows if r['status'] == 'absent')} absent, "
          f"{sum(1 for r in rows if r['status'].startswith('unconfirmed'))} unconfirmed, {len(bad)} breaches")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["confirm", "lint"])
    ap.add_argument("path")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    return {"confirm": confirm, "lint": lint}[a.cmd](Path(a.path))


if __name__ == "__main__":
    sys.exit(main())
