#!/usr/bin/env python3
r"""
status-stage.py — screen, fetch and stage one country's rows of the acquire feed.

    python scripts/status-stage.py STP              # screen, fetch, stage, write the drop list
    python scripts/status-stage.py STP --ready      # after lint-staged-queue passes: write READY

**The screen is OSINT's, stated for Corpus in `X:\status-acquire.md`** (strategic review 4,
R22a); this implements it and adds nothing. Cheap mechanical exclusion from the row alone,
before a fetch is spent: `held` and `rejected` are lookups against OSINT's `lookups/`, keyed
on the normalisation that file states; `not-a-document` is a URL shape OSINT has already
rejected for another country (`NOT_A_DOCUMENT`); everything else is fetched. Admissibility is
ingest's, so an arguable row is fetched, never dropped.

**One attempt a row.** A failed live fetch asks the Wayback Machine inside the same attempt;
failing both, the row is `unfetchable`, which OSINT never registers as a rejection.

**Each file is written as its body is fetched**, never from a list held to the end — the
crossed-body defect `lint-staged-queue.py` exists for. A body is written verbatim under a
`URL:` line, which is what that linter checks first: the requested URL for a live fetch,
redirects being the server's, and the snapshot's address for a Wayback one.

**Frontmatter carries only what the row gives**, `entities` left blank for ingest.

**`READY` is a separate step** so a batch is never delivered before its lint has been read.
The batch lands in `X:\new-queue\status-acquire-{ISO3}\`, the drops in
`X:\prepared\status-acquire-{ISO3}-drops.csv` (`url,iso3,class,note`, the URL verbatim).
"""
import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
import unicodedata
import urllib.parse as up

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osint_lib  # noqa: E402
import status_lib  # noqa: E402

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
LOOKUPS = os.path.join(osint_lib.MIRROR, "lookups")
TRACKING = re.compile(r"^(utm_\w+|fbclid|gclid|mc_cid|mc_eid)$", re.I)

# URL shapes OSINT has already registered as `not-a-document` for other countries: data
# widgets and database front ends whose country variant differs only in a parameter.
NOT_A_DOCUMENT = (
    (r"^datahub\.itu\.int/data", "ITU DataHub chart widget"),
    (r"^data\.worldbank\.org/indicator/", "World Bank indicator widget"),
    (r"^publicadministration\.un\.org/egovkb/.*/country-information/", "UN eGov database page"),
    (r"^odin\.opendatawatch\.com/data", "ODIN database front end"),
)
# Below this many characters an HTML extraction is a nav page or a shell, not a body.
THIN = 400


def norm(url: str) -> str:
    """`X:\\status-acquire.md` -> *Matching*: decode, drop scheme, `www.` and fragment and
    tracking parameters, lower-case the host only, strip a trailing slash."""
    u = up.unquote(url.strip())
    u = re.sub(r"^[a-z][a-z0-9+.-]*://", "", u, flags=re.I).split("#")[0]
    base, _, query = u.partition("?")
    host, slash, path = base.partition("/")
    host = host.lower().removeprefix("www.")
    keep = [p for p in query.split("&") if p and not TRACKING.match(p.split("=")[0])]
    out = host + slash + path
    if keep:
        return out + "?" + "&".join(keep)
    return out.rstrip("/")


def lookup(name: str) -> dict:
    with open(os.path.join(LOOKUPS, name), encoding="utf-8", newline="") as fh:
        return {r["url_normalized"]: r for r in csv.DictReader(fh)}


def screen(url: str, held: dict, rejected: dict) -> tuple[str, str] | None:
    n = norm(url)
    if n in held:
        return "held", f"held as {held[n].get('file', '')}"
    if n in rejected:
        return "rejected", f"rejected {rejected[n].get('decided', '')}: {rejected[n].get('reason', '')}"
    for pattern, what in NOT_A_DOCUMENT:
        if re.search(pattern, n, re.I):
            return "not-a-document", what
    return None


def extract(resp: requests.Response, url: str) -> tuple[str, str, str]:
    """(body, kind, the page's own title). PDF text page by page; HTML through trafilatura,
    tables kept, unless the page's own `<main>`/`<article>` holds twice as much text - a
    fact-sheet laid out as label/value pairs is what trafilatura reads as boilerplate."""
    kind = resp.headers.get("content-type", "").lower()
    if "pdf" in kind or resp.content[:5] == b"%PDF-":
        import pymupdf  # noqa: PLC0415
        doc = pymupdf.open(stream=resp.content, filetype="pdf")
        title = (doc.metadata or {}).get("title") or ""
        return "\n\n".join(p.get_text() for p in doc).strip(), "pdf", title.strip()
    import trafilatura  # noqa: PLC0415
    from bs4 import BeautifulSoup  # noqa: PLC0415
    html = resp.text
    text = (trafilatura.extract(html, url=url, include_tables=True, include_links=False,
                                include_comments=False, favor_recall=True,
                                output_format="markdown") or "").strip()
    meta = trafilatura.extract_metadata(html)
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "form", "aside"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article")
    if main is not None:
        whole = main.get_text("\n", strip=True)
        if len(whole) > 2 * len(text):
            text = whole
    return text, "html", ((meta.title if meta else "") or "").strip()


def deaccent(t: str) -> str:
    return re.sub(r"\W+", " ", unicodedata.normalize("NFKD", t).encode("ascii", "ignore")
                  .decode()).strip().lower()


def fetch(url: str) -> tuple:
    """One attempt: live, then Wayback inside the same attempt.
    (body, the address the body is filed under, kind, page title) or (None, why, "", "").
    A live redirect is the server's and is filed under the requested URL, so the body's
    `URL:` line agrees with `url:`; `lint-staged-queue.py`'s structural checks still read it."""
    why = ""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        if r.ok and re.search(r"/error[^/]*$", up.urlsplit(r.url).path, re.I):
            why = f"redirected to an error page, {r.url}"
        elif r.ok:
            body, kind, title = extract(r, url)
            if body:
                return body, url, kind, title
            why = "empty extraction"
        else:
            why = f"HTTP {r.status_code}"
    except requests.RequestException as e:
        why = type(e).__name__
    try:
        a = requests.get("https://archive.org/wayback/available", params={"url": url},
                         headers={"User-Agent": UA}, timeout=30)
        if not a.ok:
            return None, f"{why}; Wayback HTTP {a.status_code}, not checked", "", ""
        snap = (a.json().get("archived_snapshots") or {}).get("closest") or {}
        if snap.get("available"):
            r = requests.get(snap["url"], headers={"User-Agent": UA}, timeout=60)
            if r.ok:
                body, kind, title = extract(r, url)
                if body:
                    return body, snap["url"], kind, title
        why += "; no usable Wayback capture"
    except (requests.RequestException, ValueError) as e:
        why += f"; Wayback {type(e).__name__}"
    return None, why, "", ""


def slugify(text: str, cap: int = 80) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:cap].rstrip("-")


def dated(published: str) -> tuple[str, str]:
    """(padded date, precision) from the row's `published`."""
    p = published.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p):
        return p, "day"
    if re.fullmatch(r"\d{4}-\d{2}", p):
        return p + "-01", "month"
    return p[:4] + "-01-01", "year"


def yq(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_file(folder: str, row: dict, body: str, fetched: str, today: str, iso: str,
               page_title: str = "") -> str:
    date, precision = dated(row["published"])
    # The row's title is Corpus's, often transliterated; the page's own wins where the two
    # are the same words, so the source's orthography is kept.
    same = page_title and deaccent(page_title) == deaccent(row["title"])
    title = page_title if same else row["title"]
    name = f"{date}-{slugify(row['title'])}.md"
    path = os.path.join(folder, name)
    n = 2
    while os.path.exists(path):
        path = os.path.join(folder, f"{date}-{slugify(row['title'])}-{n}.md")
        n += 1
    fm = [
        "---",
        "type: source",
        f"title: {yq(title)}",
        f"url: {row['url']}",
        f"publisher: {yq(row['publisher'])}",
        f"published: {date}",
        f"date_precision: {precision}",
        f"date_source: {'source' if precision == 'day' else 'proxy'}",
        f"places: [{iso}]",
        f"topics: [{row['sub_section']}]" if row.get("sub_section") else "topics: []",
        "entities: []",
        "body_completeness: full",
        f"sweep_batch: status-acquire-{iso}-{today}",
        "---",
        "",
        f"# {title}",
        f"URL: {fetched}",
        "",
        body,
        "",
    ]
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(fm))
    return path


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("iso3")
    ap.add_argument("--ready", action="store_true", help="write READY; nothing else")
    a = ap.parse_args()
    iso = a.iso3.upper()
    folder = os.path.join(status_lib.EXCHANGE, "new-queue", f"status-acquire-{iso}")
    drops_path = os.path.join(status_lib.EXCHANGE, "prepared", f"status-acquire-{iso}-drops.csv")

    if a.ready:
        if not os.listdir(folder):
            print(f"{folder} is empty; no READY written", file=sys.stderr)
            return 1
        open(os.path.join(folder, "READY"), "w").close()
        print(f"READY written in {folder}")
        return 0

    if os.path.exists(folder) and os.listdir(folder):
        print(f"{folder} already holds files; not restaging over them", file=sys.stderr)
        return 1
    os.makedirs(folder, exist_ok=True)
    rows = [r for r in status_lib.acquire_rows() if r["iso3"].upper() == iso]
    held, rejected = lookup("raw-url-index.csv"), lookup("rejected-urls.csv")
    today = dt.date.today().isoformat()
    drops, staged = [], 0
    for r in rows:
        hit = screen(r["url"], held, rejected)
        if hit:
            drops.append({"url": r["url"], "iso3": iso, "class": hit[0], "note": hit[1]})
            print(f"drop  {hit[0]:<15} {r['url']}")
            continue
        body, fetched, kind, page_title = fetch(r["url"])
        if body is None:
            drops.append({"url": r["url"], "iso3": iso, "class": "unfetchable", "note": fetched})
            print(f"drop  unfetchable     {r['url']}  ({fetched})")
            continue
        path = write_file(folder, r, body, fetched, today, iso, page_title)
        staged += 1
        flag = "  THIN - read it" if kind == "html" and len(body) < THIN else ""
        print(f"stage {kind:<4} {len(body):>8,}  {os.path.basename(path)}{flag}")
    with io.open(drops_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["url", "iso3", "class", "note"], lineterminator="\n")
        w.writeheader()
        w.writerows(drops)
    print(f"\n{len(rows)} rows: {staged} staged, {len(drops)} dropped -> {drops_path}")
    print("Next: python scripts/lint-staged-queue.py over the folder, then --ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
