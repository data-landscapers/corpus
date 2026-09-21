#!/usr/bin/env python3
"""dataset-stage.py — T5: which of a dataset's sources the catalogue holds, and staging the rest.

    python scripts/dataset-stage.py --match     # catalogue slugs into url-audit.csv (raw_slugs: dataset-scan --relink)
    python scripts/dataset-stage.py --stage     # dated documents not held -> new-queue/, no READY
    python scripts/dataset-stage.py --stage     # new-queue/dataset-data-centres-batch-NN/, 40 a batch
    python scripts/dataset-stage.py --ready     # after lint-staged-queue passes: READY in each batch

**Matching** uses the screen `status-stage.py` implements for OSINT (`norm`, `raw-url-index.csv`,
`rejected-urls.csv`), so a URL counts as held here exactly when OSINT would say it is. A held URL's
slug is written to the audit row and, in `source_urls` order, to the record's `raw_slugs`.

**Staging takes dated documents only** (documentation/datasets.md, T5). Of the 1,320 readable
sources the catalogue did not hold on 2026-09-21, most were reference pages: directory listings
(datacentermap, PeeringDB, Baxtel), encyclopaedia and company-register entries, profiles, and
operators' product pages. The catalogue is a record of dated documents, and a reference page has
no date to file it under, so it stays cited by URL and the audit says why it was not staged. A
source is staged when it is not on a reference host and a publication date can be read from the
page's own metadata, a PDF's, or a dated path (`/2024/05/…`).

Each staged file is `status-stage.py`'s format: the body verbatim from the T4 cache under a
`URL:` line, `places` for every country whose facilities cite it, `topics: [infra.store]`, and
`sweep_batch: dataset-data-centres-batch-NN-{date}`. Batches are `new-queue/dataset-data-centres-batch-NN/`,
40 documents each across countries (Bill, 2026-09-21: OSINT works them in 40s; T5's first round
went out by country), numbered on so none is reused, written without `READY`: OSINT pulls
`dataset-` folders itself.
"""
from __future__ import annotations
import argparse, collections, csv, datetime as dt, html, importlib.util, io, os, pathlib, re, sys
import urllib.parse as up
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import datasets_lib as dl  # noqa: E402
import status_lib  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ss = _load("status_stage", "status-stage.py")
du = _load("dataset_urls", "dataset-urls.py")
mojibake = _load("mojibake", "lint-mojibake.py")


def clean(t: str) -> str:
    """A page decoded as Latin-1 when it was UTF-8 (`CÃ´te`), and entities left in a title
    (`d&#x27;Ivoire`): both broke YAML on the first staging run, 2026-09-21."""
    return html.unescape(mojibake.repair(t)[0])

NAME = "data-centres"
QUEUE = pathlib.Path(status_lib.EXCHANGE) / "new-queue"
PREFIX = f"dataset-{NAME}"
BATCH = 40         # files per batch: OSINT works a dataset batch in one go (Bill, 2026-09-21)
# Reference pages: listings, registers, profiles and feeds. Cited in place, never staged.
REFERENCE = re.compile(r"(^|\.)(datacentermap\.com|wikipedia\.org|linkedin\.com|peeringdb\.com|baxtel\.com|"
                       r"inflect\.com|datacenterplatform\.com|marketscreener\.com|finance\.yahoo\.com|"
                       r"company-information\.service\.gov\.uk|youtube\.com|facebook\.com|x\.com|twitter\.com|"
                       r"zoominfo\.com|simplywall\.st|crunchbase\.com|cloudscene\.com|bloomberg\.com/profile|"
                       r"submarinecablemap\.com|dnb\.com|opencorporates\.com|pitchbook\.com|cbinsights\.com)$", re.I)
CITED_BY = "2026-06-10"         # the v2 edition's date; nothing it cites can be later
PATH_DATE = re.compile(r"/(20\d\d|19\d\d)[/-](0[1-9]|1[0-2])(?:[/-](0[1-9]|[12]\d|3[01]))?(?:/|-|$)")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def audit() -> list[dict]:
    return du.read_audit()


def match() -> None:
    held = ss.lookup("raw-url-index.csv")
    rejected = ss.lookup("rejected-urls.csv")
    rows = audit()
    slug_of, n_rej = {}, 0
    for r in rows:
        n = ss.norm(r["url"])
        if n in held:
            f = held[n].get("file", "")
            # The file stem is the catalogue's key; slug_key is a URL-derived key it does not use
            # (282 dead raw_slugs until 2026-09-21).
            r["raw_slug"] = pathlib.PurePosixPath(f).stem or held[n].get("slug_key", "")
            slug_of[r["url"]] = r["raw_slug"]
        elif n in rejected:
            r["raw_slug"] = ""
            r["note"] = f"rejected by OSINT {rejected[n].get('decided', '')}: {rejected[n].get('reason', '')}"
            n_rej += 1
    du.write_audit(rows)
    # raw_slugs is rebuilt by `dataset-scan.py --relink` from source_urls, which also keeps the slugs
    # T7 joined to rows; writing it here replaced them wholesale.
    print(f"{len(slug_of)} URLs held in the catalogue, {n_rej} rejected by OSINT. "
          "Now run: python scripts/dataset-scan.py --relink data-centres (from scripts/.workroot)")


def cached_body(name: str) -> tuple[str, str, str]:
    """(fetched address, title, body) from a T4 cache file."""
    text = (du.CACHE / name).read_text(encoding="utf-8")
    head, _, body = text.partition("\n\n")
    meta = dict(line.split(": ", 1) for line in head.splitlines() if ": " in line)
    return meta.get("source", ""), meta.get("title", ""), body.strip()


META_DATE = [
    re.compile(r"""<meta[^>]+(?:property|name|itemprop)=["'](?:article:published_time|og:published_time|"""
               r"""datePublished|pubdate|publishdate|date|DC\.date\.issued|sailthru\.date|parsely-pub-date)["'][^>]*"""
               r"""content=["'](\d{4}-\d{2}-\d{2})""", re.I),
    re.compile(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})'),
    re.compile(r"""<time[^>]+class=["'][^"']*(?:article|post|entry|intro|byline|published)[^"']*["'][^>]*"""
               r"""datetime=["'](\d{4}-\d{2}-\d{2})""", re.I),
]


def date_of(url: str) -> tuple[str, str, str, str]:
    """(YYYY-MM-DD, precision, publisher, title), with "" for what cannot be read.

    **The page's own article metadata first, in that order**, then strict htmldate, then a dated
    path. The first staging run took trafilatura's date, which on DataCenterDynamics was the first
    related-article card on the page (88 articles all dated 2026-09-10) and on operator pages a
    copyright year read as 1 January. htmldate's `extensive_search` is off for the same reason: a
    page that does not state its date is a reference page, and guessing one misfiles it."""
    publisher = title = ""
    # Every source was cited by the June 2026 edition or the one before it, so a date after that
    # edition is the page's own "today" (a share-price page, a news page that dates itself on
    # every load), not when the document was published.
    today = CITED_BY
    try:
        r = du.get(url, timeout=30)
        if r.ok:
            if "pdf" in r.headers.get("content-type", "").lower() or r.content[:5] == b"%PDF-":
                import pymupdf  # noqa: PLC0415
                meta = pymupdf.open(stream=r.content, filetype="pdf").metadata or {}
                title = meta.get("title") or ""
                m = re.match(r"D:(\d{4})(\d{2})(\d{2})", meta.get("creationDate") or "")
                if m and f"{m[1]}-{m[2]}-{m[3]}" <= today:
                    return f"{m[1]}-{m[2]}-{m[3]}", "day", "", title
            else:
                if "charset" not in r.headers.get("content-type", "").lower():
                    r.encoding = r.apparent_encoding
                page = r.text
                import trafilatura  # noqa: PLC0415
                meta = trafilatura.extract_metadata(page)
                if meta:
                    publisher, title = meta.sitename or "", meta.title or ""
                for rx in META_DATE:
                    m = rx.search(page)
                    if m and m[1] <= today:
                        return m[1], "day", publisher, title
                import htmldate  # noqa: PLC0415
                d = htmldate.find_date(page, original_date=True, extensive_search=False)
                if d and d <= today:
                    return d, "day", publisher, title
    except Exception:  # noqa: BLE001 - an unreadable date is an undated page, not a crash
        pass
    m = PATH_DATE.search(up.urlsplit(url).path)
    if m and m[1] + "-" + m[2] <= CITED_BY[:7]:
        return ((f"{m[1]}-{m[2]}-{m[3]}", "day", publisher, title) if m[3]
                else (f"{m[1]}-{m[2]}-01", "month", publisher, title))
    return "", "", publisher, title


def stage(round_: str = "") -> None:
    rows = audit()
    recs = {r["facility_id"]: r for r in dl.read(NAME)}
    places = collections.defaultdict(list)
    for r in rows:
        places[r["url"]].append(recs[r["facility_id"]]["country"])
    by_url = {}
    for r in rows:
        by_url.setdefault(r["url"], r)
    # A URL is done if ANY row citing it is held, rejected or staged: judging by the first row alone
    # restaged three documents a second row also cited (T9, 2026-09-21).
    done = {r["url"] for r in rows
            if r["raw_slug"] or r["note"].startswith("rejected") or r["note"].startswith("staged")}
    cand, skipped = [], collections.Counter()
    for u, r in by_url.items():
        host = up.urlsplit(u).netloc.lower().removeprefix("www.")
        if u in done:
            continue
        if not r["cached"]:
            skipped["no readable text"] += 1
            continue
        if REFERENCE.search(host) or not up.urlsplit(u).path.strip("/"):
            skipped["reference page"] += 1
            r["note"] = "not staged: reference page, cited in place"
            continue
        cand.append(u)
    print(f"{len(cand)} candidates; reading dates")
    with ThreadPoolExecutor(du.WORKERS) as pool:
        dates = dict(zip(cand, pool.map(date_of, cand)))
    today = dt.date.today().isoformat()
    # A title many pages share is the site's, not the document's ("Magazine - Data Centres Africa"):
    # take the document's own words from its URL instead.
    shared = collections.Counter(d[3] for d in dates.values() if d[3])
    for u, d in dates.items():
        if d[3] and shared[d[3]] > 1:
            q = up.parse_qs(up.urlsplit(u).query)
            words = (q.get("post") or [up.urlsplit(u).path.rstrip("/").rsplit("/", 1)[-1]])[0]
            words = re.sub(r"-\d+$", "", re.sub(r"\.\w+$", "", words)).replace("-", " ").replace("_", " ").strip()
            dates[u] = (*d[:3], words[:1].upper() + words[1:] if words else d[3])
    items = []
    for u in cand:
        date, precision, publisher, page_title = dates[u]
        if not date:
            skipped["undated"] += 1
            by_url[u]["note"] = "not staged: no publication date readable, cited in place"
            continue
        iso = collections.Counter(places[u]).most_common(1)[0][0]
        items.append((iso, u, date, precision, publisher, page_title))
    items.sort()
    # Batches of BATCH across countries, numbered on from the highest batch any folder or audit note
    # has used, so a number is never reissued after OSINT pulls and empties a folder.
    used = [int(m.group(1)) for m in (re.search(r"-batch-(\d+)$", f.name) for f in QUEUE.glob(f"{PREFIX}-batch-*")) if m]
    used += [int(m.group(1)) for m in (re.search(r"staged .*-batch-(\d+)", r["note"]) for r in rows) if m]
    nxt = max(used, default=0) + 1
    staged = 0
    for k in range(0, len(items), BATCH):
        folder = QUEUE / f"{PREFIX}-batch-{nxt + k // BATCH:02d}"
        if folder.exists() and any(folder.iterdir()):
            print(f"{folder} already holds files; not restaging over them")
            continue
        folder.mkdir(parents=True, exist_ok=True)
        for iso, u, date, precision, publisher, page_title in items[k:k + BATCH]:
            fetched, title, body = cached_body(by_url[u]["cached"])
            title = page_title or title
            title, body, publisher = clean(title), clean(body), clean(publisher)
            title = title or up.urlsplit(u).path.rstrip("/").rsplit("/", 1)[-1].replace("-", " ")[:120]
            row = {"url": u, "title": title, "publisher": publisher or up.urlsplit(u).netloc.removeprefix("www."),
                   "published": date[:7] if precision == "month" else date, "sub_section": "infra.store"}
            path = ss.write_file(str(folder), row, body, fetched or u, today, iso, title)
            # status-stage writes one place and its own batch name; a dataset source can serve several.
            text = pathlib.Path(path).read_text(encoding="utf-8")
            text = text.replace(f"places: [{iso}]", f"places: [{', '.join(sorted(set(places[u])))}]", 1)
            text = text.replace(f"sweep_batch: status-acquire-{iso}-{today}", f"sweep_batch: {folder.name}-{today}", 1)
            pathlib.Path(path).write_text(text, encoding="utf-8", newline="\n")
            by_url[u]["note"] = f"staged {folder.name}"
            staged += 1
    for r in rows:
        r["note"] = by_url[r["url"]]["note"]
    du.write_audit(rows)
    print(f"staged {staged} in {-(-staged // BATCH)} batch(es); not staged: " + ", ".join(f"{k} {v}" for k, v in skipped.items()))


def ready() -> None:
    for folder in sorted(QUEUE.glob(f"{PREFIX}-*")):
        if folder.is_dir() and any(f.suffix == ".md" for f in folder.iterdir()):
            (folder / "READY").touch()
            print(f"READY {folder.name}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--match", action="store_true")
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--ready", action="store_true")
    ap.add_argument("--round", default="", help="--stage: a later pass's folder suffix, e.g. t8")
    a = ap.parse_args()
    if a.match:
        match()
    if a.stage:
        stage(a.round)
    if a.ready:
        ready()
    if not (a.match or a.stage or a.ready):
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
