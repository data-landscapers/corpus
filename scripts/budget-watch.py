#!/usr/bin/env python3
r"""
budget-watch.py — the list of budget-library pages the poll watches (strategic review 5, R102).

    python scripts/budget-watch.py build              # companions -> lookups/budget-watch.csv, probes each page
    python scripts/budget-watch.py build --no-probe   # the same, without the fetches

**One row per library, read from the mirror's `budget-archive/` companions.** A library is a
country's documents on one host: `(iso3, host)`, `www.` folded. Its URL is the deepest
directory every held URL on that host shares — the held URL's own directory when it holds one.
That is often a file store (`wp-content/uploads/`, `sites/default/files/`) rather than a page
that lists anything; the probe says which, and R104 re-points what it finds wanting.

Columns: `iso3, host, institution, library_url, library_source, docs, doc_types, type_months,
fy_start_month, fy_source, last_published, http, state, checked`.

- `institution` — the commonest `publisher:` among the host's companions.
- `type_months` — `type:MM,MM;type:MM`, the months of `published:` each type has appeared in,
  counting only dates stated to the month or day. R103's due rule reads it.
- `fy_start_month` — from Corpus's own `budgets/{ISO3}/*.csv` `fy_start` where the country has
  rows (`fy_source: budgets`), else a companion's `fy_start:` (`companion`), else `01` where
  every `fiscal_years_covered` label is a bare year (`label`), else blank.
- `state` — `live` (answered below 400), `refind` (404 or 410), `unreached` (anything else,
  timeouts included). R104 sorts `unreached` into `refind` or `manual`.

**A row R104 has re-pointed is kept, not rebuilt.** Where `library_source` is anything but
`held`, the existing `library_url` and `state` stand, and so does every column this script does
not write (R103's poll state), so a rebuild after a night's ingest adds what is new and
overwrites nothing a later step decided.
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures as cf
import csv
import datetime as dt
import os
import posixpath
import re
import sys
import threading
import urllib.parse as up
from pathlib import Path

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osint_lib import MIRROR  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = Path(MIRROR) / "budget-archive"
BUDGETS = ROOT / "budgets"
OUT = ROOT / "lookups" / "budget-watch.csv"

COLUMNS = ["iso3", "host", "institution", "library_url", "library_source", "docs", "doc_types",
           "type_months", "fy_start_month", "fy_source", "last_published", "http", "state",
           "checked"]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126 Safari/537.36")
BOT_UA = "DataLandscapersCorpus/1.0 (+https://corpus.data-landscapers.io/)"


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    return {k: v.strip().strip("\"'") for k, v in re.findall(r"^([a-z_]+):[ \t]*(.*)$", block, re.M)}


def common_dir(urls: list[str]) -> str:
    """The deepest directory every URL shares, scheme and host from the first."""
    parts = [up.urlsplit(u) for u in urls]
    dirs = [posixpath.dirname(p.path).rstrip("/").split("/") for p in parts]
    shared = []
    for segs in zip(*dirs):
        if len(set(segs)) != 1:
            break
        shared.append(segs[0])
    path = "/".join(shared).rstrip("/") + "/"
    if not path.startswith("/"):
        path = "/" + path
    return f"{parts[0].scheme}://{parts[0].netloc}{path}"


def budgets_fy_month(iso3: str) -> str:
    months = collections.Counter()
    for f in (BUDGETS / iso3).glob("*.csv"):
        with open(f, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                if row.get("state_level", "national") == "national" and re.match(
                        r"\d{4}-\d{2}", row.get("fy_start") or ""):
                    months[row["fy_start"][5:7]] += 1
    return months.most_common(1)[0][0] if months else ""


def collect() -> dict[tuple[str, str], dict]:
    libs: dict[tuple[str, str], dict] = {}
    for f in sorted(ARCHIVE.glob("*/*/*companion.md")):
        fm = frontmatter(f)
        url = fm.get("url", "")
        if not url.startswith("http"):
            continue
        iso3 = f.parts[-3]
        host = up.urlsplit(url).netloc.lower().removeprefix("www.")
        lib = libs.setdefault((iso3, host), {"urls": [], "pubs": collections.Counter(),
                                              "types": collections.defaultdict(set),
                                              "published": [], "fy_start": [], "labels": []})
        lib["urls"].append(url)
        if fm.get("publisher"):
            lib["pubs"][fm["publisher"]] += 1
        doc_type = fm.get("doc_type", "")
        published = fm.get("published", "")
        if published:
            lib["published"].append(published)
        if doc_type:
            months = lib["types"][doc_type]
            if fm.get("date_precision") in ("day", "month") and re.match(r"\d{4}-\d{2}", published):
                months.add(published[5:7])
        if re.match(r"\d{4}-\d{2}", fm.get("fy_start", "")):
            lib["fy_start"].append(fm["fy_start"][5:7])
        lib["labels"] += re.findall(r"\"?([0-9/\-]+)\"?", fm.get("fiscal_years_covered", ""))
    return libs


def row_for(iso3: str, host: str, lib: dict, fy_cache: dict[str, tuple[str, str]]) -> dict:
    if iso3 not in fy_cache:
        month = budgets_fy_month(iso3)
        fy_cache[iso3] = (month, "budgets") if month else ("", "")
    month, source = fy_cache[iso3]
    if not month and lib["fy_start"]:
        month, source = collections.Counter(lib["fy_start"]).most_common(1)[0][0], "companion"
    if not month and lib["labels"] and all(re.fullmatch(r"\d{4}", x) for x in lib["labels"]):
        month, source = "01", "label"
    return {
        "iso3": iso3, "host": host,
        "institution": lib["pubs"].most_common(1)[0][0] if lib["pubs"] else "",
        "library_url": common_dir(lib["urls"]), "library_source": "held",
        "docs": str(len(lib["urls"])),
        "doc_types": "|".join(sorted(lib["types"])),
        "type_months": ";".join(f"{t}:{','.join(sorted(m))}" for t, m in sorted(lib["types"].items())),
        "fy_start_month": month, "fy_source": source,
        "last_published": max(lib["published"], default=""),
        "http": "", "state": "", "checked": "",
    }


_locks: dict[str, threading.Lock] = collections.defaultdict(threading.Lock)


def probe(url: str) -> tuple[str, str]:
    """(http, state) for one page — one request per host at a time, a refusal retried as a bot."""
    with _locks[up.urlsplit(url).netloc.lower()]:
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=30, allow_redirects=True,
                             stream=True)
            if r.status_code in (401, 403, 429):
                r.close()
                r = requests.get(url, headers={"User-Agent": BOT_UA}, timeout=30,
                                 allow_redirects=True, stream=True)
            r.close()
        except requests.RequestException as exc:
            return type(exc).__name__, "unreached"
    code = r.status_code
    return str(code), "live" if code < 400 else "refind" if code in (404, 410) else "unreached"


def read_existing() -> tuple[list[str], dict[tuple[str, str], dict]]:
    if not OUT.exists():
        return [], {}
    with open(OUT, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), {(r["iso3"], r["host"]): r for r in reader}


def build(do_probe: bool) -> int:
    if not ARCHIVE.is_dir():
        print(f"budget-watch: no {ARCHIVE} - is the mirror mounted?", file=sys.stderr)
        return 1
    libs = collect()
    fields, old = read_existing()
    extra = [c for c in fields if c not in COLUMNS]
    fy_cache: dict[str, tuple[str, str]] = {}
    rows = []
    for key in sorted(libs):
        row = row_for(*key, libs[key], fy_cache)
        prev = old.get(key, {})
        for c in extra:
            row[c] = prev.get(c, "")
        if prev.get("library_source", "held") != "held":
            for c in ("library_url", "library_source", "state", "http", "checked"):
                row[c] = prev.get(c, "")
        elif not do_probe:
            for c in ("http", "state", "checked"):
                row[c] = prev.get(c, "") if prev.get("library_url") == row["library_url"] else ""
        rows.append(row)
    kept = [r for k, r in old.items() if k not in libs and r.get("library_source", "held") != "held"]
    rows += kept

    if do_probe:
        todo = [r for r in rows if r["library_source"] == "held"]
        today = dt.date.today().isoformat()
        with cf.ThreadPoolExecutor(12) as pool:
            for r, (code, state) in zip(todo, pool.map(lambda r: probe(r["library_url"]), todo)):
                r["http"], r["state"], r["checked"] = code, state, today

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS + extra, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    states = collections.Counter(r["state"] or "unprobed" for r in rows)
    print(f"budget-watch: {len(rows)} libraries, {len({r['iso3'] for r in rows})} countries, "
          f"{sum(int(r['docs'] or 0) for r in rows)} documents -> {OUT.relative_to(ROOT)}")
    print("  " + ", ".join(f"{k} {v}" for k, v in sorted(states.items())))
    print(f"  fy_start_month blank on {sum(1 for r in rows if not r['fy_start_month'])}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="companions -> lookups/budget-watch.csv")
    b.add_argument("--no-probe", action="store_true", help="skip the fetch of each library page")
    args = p.parse_args()
    return build(not args.no_probe)


if __name__ == "__main__":
    sys.exit(main())
