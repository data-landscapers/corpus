#!/usr/bin/env python3
"""dataset-urls.py — T4: does every URL a Data Centres row cites still answer?

    python scripts/dataset-urls.py --check            # every URL not yet checked
    python scripts/dataset-urls.py --check --recheck  # every URL, again
    python scripts/dataset-urls.py --wayback          # captures for the dead, one at a time
    python scripts/dataset-urls.py --summary          # counts from the audit, no network

Writes `outputs/datasets/data-centres/url-audit.csv`, one row per (facility, URL), and caches
each page's extracted text in `prep/dc-url-cache/{sha1}.txt` (gitignored). T5 stages a missing
source from that text, and T6 reads it to check the row's claims, so nothing is fetched twice.

**A URL is checked once, however many rows cite it** — 1,316 distinct URLs behind 306 rows.

`status` is one of:
  live      2xx with text worth reading.
  thin      2xx, but under 300 characters came out: a script-drawn page, a login wall, a stub.
  soft404   2xx, but the page is a not-found page, or a deep link that redirected to the site root.
  blocked   401/403/429/503: a bot wall, not a dead page. T6 reads it another way.
  dead      404/410, or a host that no longer resolves.
  error     anything else (TLS, timeout, 5xx).
For soft404, dead and error, `--wayback` asks the Wayback Machine for its closest capture, one
URL at a time: the archive answers 429 to anything faster, and the first run, asking twelve at
once, recorded "no capture" for all 116. `wayback_url` is the capture, `none` when the archive
has none, and blank until asked. A capture's text is cached like a live page's. **A dead URL never deletes a fact**
(documentation/datasets.md §2): the audit records the death, and T6 decides.
"""
from __future__ import annotations
import argparse, collections, csv, datetime, hashlib, io, pathlib, re, sys, threading, time
import urllib.parse as up
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import datasets_lib as dl  # noqa: E402

NAME = "data-centres"
AUDIT = dl.DATASETS / NAME / "url-audit.csv"
CACHE = dl.ROOT / "prep" / "dc-url-cache"
HEADER = ["facility_id", "url", "status", "http_code", "final_url", "wayback_url", "cached",
          "checked", "raw_slug", "supports", "note"]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126 Safari/537.36")
WORKERS, PER_HOST = 12, 2
NOT_FOUND = re.compile(r"\b(404|page not found|not found|page (?:does not|doesn't) exist|"
                       r"no longer available|page introuvable|p[aá]gina n[aã]o encontrada)\b", re.I)
_hosts = collections.defaultdict(lambda: threading.Semaphore(PER_HOST))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def key(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


def extract(resp) -> tuple[str, str]:
    """(text, title) from an HTML page or a PDF."""
    ctype = resp.headers.get("content-type", "").lower()
    if "pdf" in ctype or resp.content[:5] == b"%PDF-":
        import pymupdf  # noqa: PLC0415
        doc = pymupdf.open(stream=resp.content, filetype="pdf")
        return "\n\n".join(p.get_text() for p in doc).strip(), ((doc.metadata or {}).get("title") or "")
    import trafilatura  # noqa: PLC0415
    html = resp.text
    text = (trafilatura.extract(html, include_tables=True, include_links=False, favor_recall=True) or "").strip()
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    return text, (re.sub(r"\s+", " ", m.group(1)).strip() if m else "")


def soft404(url: str, resp, text: str, title: str) -> bool:
    asked, got = up.urlsplit(url), up.urlsplit(resp.url)
    if asked.path.strip("/") and not got.path.strip("/") and not got.query:
        return True                                  # a deep link that landed on the home page
    if NOT_FOUND.search(title):
        return True
    return len(text) < 600 and bool(NOT_FOUND.search(text[:600]))


# Some hosts (Wikipedia among them) refuse an anonymous browser string and admit a bot that
# says who it is, so a refusal is retried once as one.
BOT_UA = "DataLandscapersCorpus/1.0 (+https://corpus.data-landscapers.io/datasets/)"


def get(url: str, timeout: int = 30):
    with _hosts[up.urlsplit(url).netloc.lower()]:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout, allow_redirects=True)
        if r.status_code in (401, 403, 429):
            r = requests.get(url, headers={"User-Agent": BOT_UA}, timeout=timeout, allow_redirects=True)
        return r


def cache(url: str, text: str, title: str, source: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{key(url)}.txt"
    p.write_text(f"url: {url}\nsource: {source}\ntitle: {title}\n\n{text}", encoding="utf-8")
    return p.name


def wayback(url: str) -> tuple[str, str]:
    """(capture URL, cache file); ("none", "") when the archive has none; ("", "") when it would
    not answer, so the URL is asked again next run rather than recorded as having no capture."""
    try:
        for wait in (0, 30, 60, 120, 240):
            time.sleep(wait)
            a = requests.get("https://archive.org/wayback/available", params={"url": url},
                             headers={"User-Agent": BOT_UA}, timeout=30)
            if a.status_code != 429:
                break
        else:
            return "", ""
        snap = (a.json().get("archived_snapshots") or {}).get("closest") or {}
        if not snap.get("available"):
            return "none", ""
        r = get(snap["url"], timeout=60)
        if r.ok:
            text, title = extract(r)
            if len(text) >= 300:
                return snap["url"], cache(url, text, title, snap["url"])
        return snap["url"], ""
    except (requests.RequestException, ValueError):
        return "", ""


def check(url: str) -> dict:
    out = dict(status="error", http_code="", final_url="", wayback_url="", cached="", note="")
    try:
        r = get(url)
        out["http_code"] = str(r.status_code)
        out["final_url"] = r.url if r.url != url else ""
        if r.ok:
            try:
                text, title = extract(r)
            except Exception as e:  # noqa: BLE001 - a page that will not parse is a finding, not a crash
                text, title, out["note"] = "", "", f"extract failed: {type(e).__name__}"
            if soft404(url, r, text, title):
                out["status"] = "soft404"
            elif len(text) < 300:
                out["status"] = "thin"
                if text:
                    out["cached"] = cache(url, text, title, url)
            else:
                out["status"] = "live"
                out["cached"] = cache(url, text, title, url)
        elif r.status_code in (401, 403, 429, 503):
            out["status"] = "blocked"
        elif r.status_code in (404, 410):
            out["status"] = "dead"
        else:
            out["note"] = f"HTTP {r.status_code}"
    except requests.exceptions.ConnectionError as e:
        s = str(e)
        out["status"] = "dead" if re.search(r"NameResolution|getaddrinfo|Name or service", s) else "error"
        out["note"] = "host does not resolve" if out["status"] == "dead" else "connection failed"
    except requests.RequestException as e:
        out["note"] = type(e).__name__
    return out


def wayback_pass() -> None:
    rows = read_audit()
    ask = sorted({r["url"] for r in rows if r["status"] in ("soft404", "dead", "error") and not r["wayback_url"]})
    print(f"{len(ask)} URLs to ask the Wayback Machine about")
    found = {}
    for n, u in enumerate(ask, 1):
        found[u] = wayback(u)
        time.sleep(1.5)
        if n % 10 == 0 or n == len(ask):
            for r in rows:
                if r["url"] in found:
                    r["wayback_url"], c = found[r["url"]]
                    r["cached"] = c or r["cached"]
            write_audit(rows)
            print(f"  {n}/{len(ask)}", flush=True)
    summary()


def read_audit() -> list[dict]:
    if not AUDIT.exists():
        return []
    with open(AUDIT, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_audit(rows: list[dict]) -> None:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=HEADER, lineterminator="\n")
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: (r["facility_id"], r["url"])))
    AUDIT.write_text(buf.getvalue(), encoding="utf-8", newline="")


def pairs() -> list[tuple[str, str]]:
    return [(r["facility_id"], u) for r in dl.read(NAME)
            for u in r["source_urls"].split("; ") if u]


def run(recheck: bool) -> None:
    old = {(r["facility_id"], r["url"]): r for r in read_audit()}
    todo_pairs = pairs()
    done = {r["url"]: r for r in old.values() if r["checked"] and not recheck}
    urls = sorted({u for _, u in todo_pairs} - set(done))
    print(f"{len(urls)} URLs to check ({len(done)} already checked)")
    today = datetime.date.today().isoformat()
    results = {u: {k: done[u][k] for k in HEADER[2:8] + ["note"]} for u in done}
    lock = threading.Lock()

    def save():
        rows = []
        for fid, u in todo_pairs:
            prev = old.get((fid, u), {})
            res = results.get(u)
            if res is None and not prev:
                continue
            rows.append({"facility_id": fid, "url": u, **(res or {k: prev.get(k, "") for k in HEADER[2:8]}),
                         "raw_slug": prev.get("raw_slug", ""), "supports": prev.get("supports", ""),
                         "note": (res or prev).get("note", "")})
        write_audit(rows)

    with ThreadPoolExecutor(WORKERS) as pool:
        futs = {pool.submit(check, u): u for u in urls}
        for n, f in enumerate(as_completed(futs), 1):
            u = futs[f]
            with lock:
                results[u] = {**f.result(), "checked": today}
                if n % 50 == 0:
                    save()
                    print(f"  {n}/{len(urls)}", flush=True)
    save()
    summary()


def summary() -> None:
    rows = read_audit()
    by_url = {r["url"]: r for r in rows}
    c = collections.Counter(r["status"] for r in by_url.values())
    wb = sum(1 for r in by_url.values() if r["wayback_url"] not in ("", "none"))
    print(f"{len(by_url)} URLs across {len(rows)} citations: " +
          ", ".join(f"{k} {v}" for k, v in c.most_common()) + f"; Wayback capture for {wb}")
    live = {r["url"] for r in by_url.values() if r["status"] == "live" or r["cached"]}
    per = collections.Counter()
    for r in rows:
        if r["url"] in live:
            per[r["facility_id"]] += 1
    ids = {r["facility_id"] for r in dl.read(NAME)}
    under = sorted(i for i in ids if per[i] < 2)
    print(f"rows with fewer than two readable sources: {len(under)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--recheck", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--wayback", action="store_true")
    a = ap.parse_args()
    if a.check:
        run(a.recheck)
    elif a.wayback:
        wayback_pass()
    elif a.summary:
        summary()
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
