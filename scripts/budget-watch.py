#!/usr/bin/env python3
r"""
budget-watch.py — the list of budget-library pages the poll watches (strategic review 5, R102).

    python scripts/budget-watch.py build              # companions -> lookups/budget-watch.csv, probes each page
    python scripts/budget-watch.py build --no-probe   # the same, without the fetches
    python scripts/budget-watch.py poll               # fetch the due pages, stage what is new
    python scripts/budget-watch.py poll --dry-run --iso KEN --force   # list, fetch no document
    python scripts/budget-watch.py refind             # R104: one enumeration per failed library
    python scripts/budget-watch.py fetch-list         # R104: manual libraries to the fetch list

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

**`poll` (R103) fetches each due `live` library and stages what is new.** No model call. A row
is due weekly in a month one of its types has appeared in, monthly otherwise, and always if it
has never been polled; `refind` and `unreached` rows wait for R104. For each page:

1. Every link is read. A link already recorded for the library in `logs/budget-poll/links.csv`
   is skipped — that file is the last poll, and a link is recorded once whatever became of it,
   so a failed fetch is one attempt, never a nightly retry.
2. A link survives if it points at a document (a file extension, or a download path), its text
   or filename matches a type in `TYPE_WORDS` (the closed list, `lookups/budget-doc-types.csv`
   in OSINT), and it names a fiscal year no older than `YEARS_BACK` — or, after the first
   poll, names no year at all, because a link new on the page is itself the date.
3. It is dropped if its URL is held: `raw-url-index.csv`, `rejected-urls.csv` and every
   `budget-archive/` companion's `url:`, normalised as `status-stage.py` does.
4. It is fetched, and dropped if the body is a web page rather than a file, or if its md5 is in
   `artefact-md5-index.csv` — the same document under another address.
5. What is left is staged, artefact and companion together, to
   `X:\new-queue\budget-poll-{ISO3}\`, and `READY` is written last. A folder still waiting for
   the pull is not written into; the run takes `budget-poll-{ISO3}-{YYYYMMDD}` instead.

The companion is a catalogue page on `BUDGET-COLLECT.md` step 2's shape, with `artefact:`
naming the file beside it, `source_tier: budget-document` and the type the link matched.
`published:` is the server's `Last-Modified` or the upload folder's month, marked `derived`.
Ingest adjudicates it like anything else pulled. Each library polled appends one line to
`logs/budget-poll/runs.csv` — links read, candidates, held, fetched, staged, seconds — which
is what R107 reads for the cost of a full poll. `--limit` caps the documents fetched per
library (default 25), so a library that never lists years cannot flood one night.

**`refind` and `fetch-list` (R104) settle the rows the poll cannot read.** `refind` gives each
`refind` or `unreached` row, and each `live` row whose page lists no document, one Track B
enumeration (`DOMESTIC-FINANCE-SWEEP.md`): the host's WordPress media search where it has one,
the held URL's parent folders, and the root's own links that name a budget or a library — at
most `REFIND_PAGES` fetches. The page listing the most typed documents, `MIN_TYPED` or more,
becomes the library (`library_source: refound`). Otherwise the row is `manual` where a browser
would get through and a script cannot — a licence form, a JavaScript shell, a bot wall, a TLS
failure, a timeout — and `dead` where the host holds no library a script can find. A host
that does not answer at all is `dead` only on a second failure a week after the first.
Niger is the worked case of a licence form: its library lists plainly, and every document
behind it asks for a licence to be ticked and POSTed, so the check reads one held document's
page, not the library's.

**`note` is the dated absence.** `dead 2026-09-25: no budget library found in 12 pages` is
what the Finance page's coverage table states for the row when it returns (R106); until then
this file is where the absence is recorded. `fetch-list` writes the `manual` rows to
`X:\fetch-list.md` as one batch, no more often than every 91 days, and dates `listed`.
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures as cf
import csv
import datetime as dt
import hashlib
import importlib.util
import os
import posixpath
import re
import sys
import threading
import time
import unicodedata
import urllib.parse as up
from pathlib import Path

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib  # noqa: E402
from osint_lib import MIRROR  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = Path(MIRROR) / "budget-archive"
LOOKUPS = Path(MIRROR) / "lookups"
BUDGETS = ROOT / "budgets"
OUT = ROOT / "lookups" / "budget-watch.csv"
POLL_LOG = ROOT / "logs" / "budget-poll"
LINKS = POLL_LOG / "links.csv"
RUNS = POLL_LOG / "runs.csv"

# The closed list's types, as the words a library page labels them with — English, French,
# Portuguese, Arabic — tried in this order, so the narrower reading wins (`projet de loi de finances`
# is estimates before `loi de finances` is an act). Matched on the link's text and filename,
# accents stripped, lower-cased. `board-budget`, `ifmis-extract`, `project-document` and
# `reporting` have no words a library labels them with, so a poll never finds one.
TYPE_WORDS = [
    # A press release about an audit report or a quarterly outturn is still a press release; one
    # about anything but the public money is not a budget document at all.
    ("statement", r"(press (release|statement)|media (statement|release)|communique)"
                  r"(?=.*(budget|fiscal|appropriation|expenditure|revenue|audit|mtbps|outturn"
                  r"|orcament|finances publiques|loi de finances|الموازنة|الميزانية))"),
    ("audited-accounts", r"(?<!performance )audit|auditor|cour des comptes|tribunal de contas"
                         r"|comptes? de gestion|compte general|\bcge\b|certification"
                         r"|financial statements|annual accounts|contas gerais|conta geral"
                         r"|ديوان المحاسبة|الجهاز المركزي للمحاسبات"),
    ("procurement-plan", r"procurement plan|passation des marches|\bppm\b|plano anual de (aquisicoes|contratac)"),
    ("treasury-release", r"warrant|exchequer|cash (limit|allocation)|releases? to|mise a disposition"),
    ("mtef", r"\bmtef\b|\bmtbf\b|medium[- ]term|\bcdmt\b|\bcbmt\b|\bdpbep\b|\bdpbp\b"
             r"|programmation budgetaire|pluriannuel"
             r"|budget (framework|policy|strategy) (paper|statement)|fiscal strategy|\bbsp\b|\bbps\b"
             r"|cenario fiscal|quadro (fiscal|de despesa) de medio prazo|\bcfmp\b|متوسط المدى"),
    ("implementation-report", r"execution|execucao|outturn|implementation report|budget performance"
                              r"|quarterly|trimestr|semestr|mid[- ]year|in[- ]year|\btofe\b"
                              r"|loi de reglement|relatorio de execucao|expenditure report"
                              r"|revenue and expenditure|section (32|71)\b"
                              r"|الإيراد والإنفاق|الإيرادات والنفقات|الإيرادات والمصروفات"
                              r"|تنفيذ الميزانية|تنفيذ الموازنة|الحساب الختامي"),
    ("budget-estimates", r"estimates|budget book|projet de loi de finances|\bplf\b|proposta de (lei do )?orcamento"
                         r"|annexe|ventilation|programme budget|program based budget|budget detaille"
                         r"|\boge\b|draft budget|budget proposal|volume|\bvol\b|tome|livre"
                         r"|مشروع الموازنة|مشروع الميزانية|مشروع قانون المالية"),
    ("appropriation-act", r"appropriation|loi de finances|lei (do|que aprova o) orcamento|finance act"
                          r"|budget law|\blfr\b|\blfi\b|loi n|lei n"
                          r"|قانون الميزانية|قانون الموازنة|قانون المالية|قانون ربط"),
    ("executive-instrument", r"decret|decree|despacho|ordonnance|arrete|credit supplementaire|decreto"),
    ("statement", r"budget speech|budget statement|discours (?=.*budget)|citizens?'? budget|budget in brief"
                  r"|budget highlights|expose des motifs|البيان المالي"),
    # Arabic pages rarely say more than "the general budget"; last, so anything narrower wins.
    ("budget-estimates", r"الموازنة العامة|الميزانية العامة"),
]


def strip_marks(text: str) -> str:
    """Accents and Arabic hamza/vowel marks off, lower-cased — applied to the words and the
    links alike, so `إ` in a pattern meets `ا` + mark in a link."""
    return "".join(c for c in unicodedata.normalize("NFKD", text)
                   if not unicodedata.combining(c)).lower()


TYPE_RES = [(t, re.compile(strip_marks(p))) for t, p in TYPE_WORDS]
DOC_EXT = (".pdf", ".xls", ".xlsx", ".doc", ".docx", ".zip", ".csv", ".ods", ".odt")
YEARS_BACK = 2          # a fiscal year older than this many years before today is not polled for
MAX_BYTES = 200 * 2**20
CONTENT_EXT = {"application/pdf": ".pdf", "application/vnd.ms-excel": ".xls",
               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
               "application/msword": ".doc", "application/zip": ".zip",
               "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"}

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


def settled(row: dict) -> bool:
    """A row R104 has decided: re-pointed, or marked `dead` or `manual`. A rebuild keeps it."""
    return row.get("library_source", "held") != "held" or row.get("state") in ("dead", "manual")


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
        if settled(prev):
            for c in ("library_url", "library_source", "state", "http", "checked"):
                row[c] = prev.get(c, "")
        elif not do_probe:
            for c in ("http", "state", "checked"):
                row[c] = prev.get(c, "") if prev.get("library_url") == row["library_url"] else ""
        rows.append(row)
    kept = [r for k, r in old.items() if k not in libs and settled(r)]
    rows += kept

    if do_probe:
        todo = [r for r in rows if not settled(r)]
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


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fold(text: str) -> str:
    """`strip_marks`, then separators to spaces; any script kept, since Arabic has no ASCII."""
    return re.sub(r"[\s_\-+.%]+", " ", strip_marks(text))


def doc_type_of(text: str) -> str:
    folded = fold(text)
    return next((t for t, rx in TYPE_RES if rx.search(folded)), "")


def years_in(text: str) -> list[int]:
    return [int(y) for y in re.findall(r"(?<!\d)(20[0-4]\d)(?!\d)", text)]


def fy_label(text: str, fy_month: str) -> str:
    """`2025/26` from `2025-2026`, `2025/26` or `2025_26`; a bare year only where the fiscal
    year is the calendar year, since elsewhere it is ambiguous; otherwise blank."""
    m = re.search(r"(?<!\d)(20[0-4]\d)\s*[/\-_ ]\s*(20)?([0-4]\d)(?!\d)", text)
    if m and int(m.group(3)) == (int(m.group(1)) + 1) % 100:
        return f"{m.group(1)}/{m.group(3)}"
    ys = sorted(set(years_in(text)))
    return str(ys[-1]) if ys and fy_month == "01" else ""


def due(row: dict, today: dt.date) -> bool:
    if not row.get("last_poll"):
        return True
    gap = (today - dt.date.fromisoformat(row["last_poll"])).days
    in_season = any(f"{today.month:02d}" in part.split(":", 1)[1].split(",")
                    for part in (row.get("type_months") or "").split(";") if ":" in part)
    return gap >= (7 if in_season else 28)


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def append_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with open(path, "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerows(rows)


def page_links(url: str) -> tuple[list[tuple[str, str]], str]:
    """(href, text) for every anchor on the page, or ([], why)."""
    from bs4 import BeautifulSoup  # noqa: PLC0415
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        if r.status_code in (401, 403, 429):
            r = requests.get(url, headers={"User-Agent": BOT_UA}, timeout=60)
    except requests.RequestException as exc:
        return [], type(exc).__name__
    if not r.ok:
        return [], f"HTTP {r.status_code}"
    if "json" in r.headers.get("content-type", ""):
        # A WordPress media search, `/wp-json/wp/v2/media?search=…`: the library behind the
        # posts, and the route the budget sweeps proved best (`domestic-budget-extraction.md`).
        try:
            items = r.json()
        except ValueError:
            return [], "unreadable JSON"
        return [(i.get("source_url", ""), (i.get("title") or {}).get("rendered", ""))
                for i in items if isinstance(i, dict) and i.get("source_url")], ""
    soup = BeautifulSoup(r.text, "html.parser")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = up.urljoin(r.url, a["href"].strip()).split("#")[0]
        if href.startswith("http") and href not in seen:
            seen.add(href)
            text = " ".join(a.get_text(" ", strip=True).split()) or a.get("title", "")
            out.append((href, text))
    return out, ""


def is_document(href: str) -> bool:
    path = up.unquote(up.urlsplit(href).path).lower()
    return path.endswith(DOC_EXT) or "/download" in path or "download=" in href.lower()


def fetch_document(url: str) -> tuple[bytes | None, str, str]:
    """(bytes, extension, Last-Modified) or (None, why, '')."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=120, stream=True)
        if r.status_code in (401, 403, 429):
            r.close()
            r = requests.get(url, headers={"User-Agent": BOT_UA}, timeout=120, stream=True)
        if not r.ok:
            return None, f"HTTP {r.status_code}", ""
        kind = r.headers.get("content-type", "").split(";")[0].strip().lower()
        if kind.startswith("text/html"):
            return None, "not-a-document: the link serves a web page", ""
        body = bytearray()
        for chunk in r.iter_content(1 << 20):
            body += chunk
            if len(body) > MAX_BYTES:
                return None, f"over {MAX_BYTES >> 20} MB", ""
    except requests.RequestException as exc:
        return None, type(exc).__name__, ""
    ext = os.path.splitext(up.unquote(up.urlsplit(url).path))[1].lower()
    if ext not in DOC_EXT:
        ext = ".pdf" if bytes(body[:5]) == b"%PDF-" else CONTENT_EXT.get(kind, "")
    if not ext:
        return None, f"not-a-document: {kind or 'no content type'}", ""
    return bytes(body), ext, r.headers.get("last-modified", "")


def published_of(url: str, last_modified: str, today: dt.date) -> tuple[str, str]:
    """(published, date_precision): the server's Last-Modified, else an upload folder's
    `/YYYY/MM/`, else today to the month. All three are `date_source: derived`."""
    if last_modified:
        try:
            from email.utils import parsedate_to_datetime  # noqa: PLC0415
            return parsedate_to_datetime(last_modified).date().isoformat(), "day"
        except (TypeError, ValueError):
            pass
    m = re.search(r"/(20[0-4]\d)/(0[1-9]|1[0-2])/", up.urlsplit(url).path)
    if m:
        return f"{m.group(1)}-{m.group(2)}-01", "month"
    return f"{today:%Y-%m}-01", "month"


def pdf_pages(body: bytes) -> int | None:
    try:
        import pymupdf  # noqa: PLC0415
        return pymupdf.open(stream=body, filetype="pdf").page_count
    except Exception:  # noqa: BLE001 - a PDF pymupdf cannot open is still a document
        return None


def link_title(url: str, text: str) -> str:
    """The link's text, unless it is short or a directory listing's truncation (`NAME..>`):
    then the filename, separators to spaces."""
    text = re.sub(r"^download\s+|\s+download$", "", text, flags=re.I).strip()
    if len(text) >= 8 and not text.endswith(("..>", "...", "…")):
        return text
    name = os.path.splitext(up.unquote(os.path.basename(up.urlsplit(url).path)))[0]
    return re.sub(r"[_\-]+", " ", name).strip() or text


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def companion(row: dict, url: str, text: str, doc_type: str, artefact: str, body: bytes,
              published: str, precision: str, fy: str, batch: str, today: dt.date) -> str:
    title = link_title(url, text)
    pages = pdf_pages(body) if artefact.endswith(".pdf") else None
    extent = f"{pages} pp, " if pages else ""
    fm = [
        "---", "type: source", f"title: {yaml_str(title)}", f"url: {url}",
        f"publisher: {yaml_str(row['institution'])}", f"published: {published}",
        f"date_precision: {precision}", "date_source: derived", f"places: [{row['iso3']}]",
        "topics: [finance.budget]", "entities: []", f"retrieved: {today}",
        f"sweep_batch: {batch}",
    ]
    if fy:
        fm.append(f'fiscal_years_covered: ["{fy}"]')
    fm += [f"doc_type: {doc_type}", "source_tier: budget-document", f"artefact: {artefact}",
           "body_completeness: excerpt", "---", ""]
    body_md = [
        f"# {title}", "",
        "## Document", "",
        f"{extent}{len(body):,} bytes, md5 `{hashlib.md5(body).hexdigest()}`. Not read: the type, "
        "the fiscal year and the date are read off the library page and the server, and the "
        "instrument, scope, currency and printed scale are ingest's to state.", "",
        "## Source", "",
        f"Listed as \"{text}\" on {row['institution']}'s library page, <{row['library_url']}>, "
        f"polled {today}.", "",
        "## Notes", "",
        f"Found by CORPUS's budget poll (`budget-watch.py poll`, strategic review R103): new on "
        f"the page since the last poll and held nowhere by URL or md5. `doc_type` is the "
        f"keyword match on the link, `published` is {'the server' if precision == 'day' else 'the upload folder or the poll'}'s "
        f"date, not the document's.", "",
    ]
    return "\n".join(fm + body_md)


def stage_folder(iso3: str, today: dt.date) -> Path:
    """`budget-poll-{ISO3}`, unless it is waiting for the pull (it carries `READY`): then the
    dated name. A folder without `READY` is this script's own unfinished run, and is resumed."""
    base = Path(status_lib.EXCHANGE) / "new-queue"
    folder = base / f"budget-poll-{iso3}"
    if (folder / "READY").exists():
        folder = base / f"budget-poll-{iso3}-{today:%Y%m%d}"
    return folder


def stage(folder: Path, row: dict, href: str, text: str, doc_type: str, body: bytes, ext: str,
          last_mod: str, today: dt.date, slugify) -> str:
    folder.mkdir(parents=True, exist_ok=True)
    published, precision = published_of(href, last_mod, today)
    fy = fy_label(f"{text} {up.unquote(href)}", row.get("fy_start_month", ""))
    stem = base = f"{published}-{row['iso3'].lower()}-{slugify(link_title(href, text), 70)}"
    n = 2
    while (folder / f"{stem}{ext}").exists():
        stem, n = f"{base}-{n}", n + 1
    batch = folder.name if re.search(r"-\d{8}$", folder.name) else f"{folder.name}-{today:%Y%m%d}"
    (folder / f"{stem}{ext}").write_bytes(body)
    (folder / f"{stem}-companion.md").write_text(
        companion(row, href, text, doc_type, f"{stem}{ext}", body, published, precision, fy,
                  batch, today), encoding="utf-8", newline="\n")
    return stem


def poll(iso: str | None, force: bool, dry_run: bool, limit: int) -> int:
    ss = _load("status_stage", "status-stage.py")
    today = dt.date.today()
    fields, rows = read_existing()
    if not rows:
        print("budget-watch: no watch list - run build first", file=sys.stderr)
        return 1
    fields = fields + [c for c in ("last_poll", "last_staged") if c not in fields]
    held = set(ss.lookup("raw-url-index.csv")) | set(ss.lookup("rejected-urls.csv"))
    held |= {ss.norm(frontmatter(f).get("url", "")) for f in ARCHIVE.glob("*/*/*companion.md")}
    with open(LOOKUPS / "artefact-md5-index.csv", encoding="utf-8", newline="") as fh:
        md5s = {r["md5"]: r["artefact"] for r in csv.DictReader(fh)}
    seen: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    for r in read_csv(LINKS):
        seen[(r["iso3"], r["host"])].add(r["url"])

    todo = [r for k, r in sorted(rows.items())
            if (not iso or k[0] == iso) and r.get("state") == "live" and (force or due(r, today))]
    print(f"budget-watch poll: {len(todo)} due of {len(rows)} libraries"
          f"{' (dry run: no document fetched, nothing staged or recorded)' if dry_run else ''}")
    folders: dict[str, Path] = {}
    for row in todo:
        link_rows = []
        key, start = (row["iso3"], row["host"]), time.time()
        first = not seen[key]
        links, why = page_links(row["library_url"])
        counts = collections.Counter(links=len(links))
        cands = []
        for href, text in links:
            if href in seen[key]:
                continue
            counts["new"] += 1
            outcome = ""
            label = f"{text} {up.unquote(os.path.basename(up.urlsplit(href).path))}"
            is_doc = is_document(href)
            counts["docs"] += is_doc
            doc_type = doc_type_of(label) if is_doc else ""
            ys = years_in(label)
            if not doc_type:
                outcome = "untyped"
            elif ys and max(ys) < today.year - YEARS_BACK:
                outcome = "old"
            elif not ys and first:
                outcome = "undated"
            elif ss.norm(href) in held:
                outcome = "held"
            if outcome:
                counts[outcome] += 1
                link_rows.append({"iso3": key[0], "host": key[1], "url": href, "first_seen": today,
                                  "outcome": outcome, "doc_type": doc_type})
                continue
            cands.append((href, text, doc_type))
        counts["candidates"] = len(cands)
        for href, text, doc_type in cands[:limit]:
            if dry_run:
                print(f"  would fetch  {doc_type:<22} {href}")
                continue
            body, ext_or_why, last_mod = fetch_document(href)
            outcome = "failed: " + ext_or_why if body is None else ""
            if body is not None:
                counts["fetched"] += 1
                digest = hashlib.md5(body).hexdigest()
                if digest in md5s:
                    outcome = f"held-md5: {md5s[digest]}"
                else:
                    folder = folders.setdefault(key[0], stage_folder(key[0], today))
                    stem = stage(folder, row, href, text, doc_type, body, ext_or_why, last_mod,
                                 today, ss.slugify)
                    outcome = f"staged: {folder.name}/{stem}"
                    counts["staged"] += 1
                    md5s[digest] = "(staged this poll)"
            link_rows.append({"iso3": key[0], "host": key[1], "url": href, "first_seen": today,
                              "outcome": outcome, "doc_type": doc_type})
        secs = round(time.time() - start)
        print(f"  {key[0]} {key[1]:<30} links {counts['links']:>5}  new {counts['new']:>5}  "
              f"docs {counts['docs']:>4}  untyped {counts['untyped'] - (counts['new'] - counts['docs']):>3}  "
              f"old {counts['old']:>3}  undated {counts['undated']:>3}  held {counts['held']:>3}  "
              f"cands {counts['candidates']:>3}  staged {counts['staged']:>2}  {secs}s"
              f"{'  ' + why if why else ''}")
        if dry_run:
            continue
        # Recorded library by library, so a run that stops part-way re-fetches nothing it staged.
        row["last_poll"] = today.isoformat()
        if counts["staged"]:
            row["last_staged"] = today.isoformat()
        append_csv(LINKS, ["iso3", "host", "url", "first_seen", "outcome", "doc_type"], link_rows)
        append_csv(RUNS, ["date", "iso3", "host", "links", "new", "candidates", "held", "fetched",
                          "staged", "seconds", "error"],
                   [{"date": today, "iso3": key[0], "host": key[1], "links": counts["links"],
                     "new": counts["new"], "candidates": counts["candidates"],
                     "held": counts["held"], "fetched": counts["fetched"],
                     "staged": counts["staged"], "seconds": secs, "error": why}])
        with open(OUT, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(rows[k] for k in sorted(rows))

    for folder in folders.values():
        (folder / "READY").touch()          # last, per the share's README
        print(f"READY written in {folder}")
    return 0


# Links on a site's own pages that lead towards a document library. Budget words first, so a
# page named for the budget is tried before a generic *Publications*.
LIB_WORDS = [re.compile(strip_marks(p)) for p in (
    r"budget|orcament|finances publiques|loi de finances|estimates|الميزانية|الموازنة",
    r"document|publication|download|telecharg|biblioth|library|resource|rapport|report|relatorio"
    r"|legisla|المنشورات|الوثائق|التقارير",
)]
FILE_HOST = re.compile(r"(static|media|assets|cdn|backdata|files?|uploads?)\.", re.I)
LICENCE = re.compile(r"phocadownload|license_agree|licence_agree", re.I)
WP_TERMS = ("budget", "loi de finances", "orcamento", "finances")
REFIND_PAGES = 12       # one enumeration: at most this many pages fetched per library
MIN_TYPED = 3           # fewer typed documents than this is a homepage mentioning one, not a library
UNREACHABLE = 7         # days an unreachable host is given before a second failure marks it dead


def get(url: str, timeout: int = 45):
    """(response, '') or (None, why) — one request, a refusal retried once as a bot."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout)
        if r.status_code in (401, 403, 429):
            r = requests.get(url, headers={"User-Agent": BOT_UA}, timeout=timeout)
    except requests.exceptions.SSLError:
        return None, "TLS failure"
    except requests.exceptions.Timeout:
        return None, "times out"
    except requests.exceptions.ConnectionError as exc:
        return None, "host does not resolve" if re.search(
            r"NameResolution|getaddrinfo|Name or service", str(exc)) else "connection refused"
    except requests.RequestException as exc:
        return None, type(exc).__name__
    return r, ""


def typed_docs(links: list[tuple[str, str]]) -> int:
    return sum(1 for href, text in links if is_document(href) and doc_type_of(
        f"{text} {up.unquote(os.path.basename(up.urlsplit(href).path))}"))


def enumerate_library(row: dict) -> tuple[str, str, str]:
    """One Track B enumeration (`DOMESTIC-FINANCE-SWEEP.md`): fetch the site's document
    library directly. (state, library_url, why): `live` with the page holding the most typed
    budget documents; `manual` where a browser would get through and a script cannot; `dead`
    where the host is gone or holds no library a script can find."""
    held = up.urlsplit(row["library_url"])
    root = f"{held.scheme}://{held.netloc}/"
    if FILE_HOST.match(held.netloc):
        return "dead", "", "a file host: its documents are listed on another site"
    r, why = get(root)
    if r is None and why in ("host does not resolve", "connection refused"):
        return "dead", "", why
    if r is None:
        return "manual", "", why
    if r.status_code in (401, 403, 429):
        return "manual", "", f"bot wall (HTTP {r.status_code})"
    if r.status_code >= 500:
        return "manual", "", f"server error (HTTP {r.status_code})"
    if LICENCE.search(r.text or ""):
        return "manual", "", "licence form before every download"

    tried, best = 0, ("", 0)

    def score(url: str) -> None:
        nonlocal tried, best
        if tried >= REFIND_PAGES:
            return
        tried += 1
        links, _ = page_links(url)
        n = typed_docs(links)
        if n > best[1]:
            best = (url, n)

    root_links, _ = page_links(root)
    if not root_links:
        return "manual", "", "JavaScript wall: the page serves no links"
    wp, _ = get(root + "wp-json/")
    if wp is not None and wp.ok and "json" in wp.headers.get("content-type", ""):
        for term in WP_TERMS:
            score(f"{root}wp-json/wp/v2/media?search={up.quote(term)}&per_page=100")
    parts = [p for p in held.path.split("/") if p]
    for i in range(len(parts), 0, -1):
        score(f"{root}{'/'.join(parts[:i])}/")
    host = held.netloc.lower().removeprefix("www.")
    pages = [(h, t) for h, t in root_links if not is_document(h)
             and up.urlsplit(h).netloc.lower().removeprefix("www.") == host]
    for rx in LIB_WORDS:
        for h, t in pages:
            if rx.search(fold(f"{t} {up.unquote(up.urlsplit(h).path)}")):
                score(h)
    best_url, n = best
    if n == 0 and typed_docs(root_links):
        best_url, n = root, typed_docs(root_links)
    if n >= MIN_TYPED:
        return "live", best_url, f"{n} typed documents listed"
    return "dead", "", f"no budget library found in {tried} pages"


def refind(iso: str | None) -> int:
    """R104 over the watch list: `refind` and `unreached` rows get one enumeration, and so does
    a `live` row whose page lists no document at all. A `live` row behind a licence form is
    marked `manual` without one. Every decision is dated in `note`."""
    today = dt.date.today().isoformat()
    fields, rows = read_existing()
    fields = fields + [c for c in ("note", "listed") if c not in fields]
    held_urls = {k: v["urls"] for k, v in collect().items()}
    todo = []
    for key, row in sorted(rows.items()):
        if iso and key[0] != iso or row.get("state") in ("dead", "manual"):
            continue
        if row.get("state") in ("refind", "unreached"):
            todo.append(row)
            continue
        if row.get("state") == "live" and row.get("library_source", "held") == "held":
            # The gate sits on the document's page, not the library's: Niger's library lists
            # plainly and every file behind it asks for a licence to be ticked and POSTed.
            r, _ = get(held_urls.get(key, [row["library_url"]])[0])
            if r is not None and LICENCE.search(r.text or ""):
                row.update(state="manual", note=f"manual {today}: licence form before every download")
                print(f"  {key[0]} {key[1]:<32} manual   licence form before every download")
            elif r is not None and not any(is_document(h) for h, _ in page_links(row["library_url"])[0]):
                todo.append(row)
    print(f"budget-watch refind: {len(todo)} libraries to enumerate")

    def one(row):
        return row, enumerate_library(row)

    with cf.ThreadPoolExecutor(8) as pool:
        for row, (state, url, why) in pool.map(one, todo):
            old = row["library_url"]
            if why in ("host does not resolve", "connection refused"):
                # A host down once may be down for the afternoon: `dead` takes a second failure
                # a week on, and until then the row stays `refind` with the first one dated.
                first = re.match(r"unreachable (\d{4}-\d{2}-\d{2})", row.get("note", ""))
                if not first or (dt.date.fromisoformat(today) -
                                 dt.date.fromisoformat(first.group(1))).days < UNREACHABLE:
                    state = "refind"
                    row.update(state=state, checked=today,
                               note=row.get("note") if first else f"unreachable {today}: {why}")
                    print(f"  {row['iso3']} {row['host']:<32} refind   {why}; dead if still so "
                          f"after {UNREACHABLE} days", flush=True)
                    continue
            if state == "live":
                row.update(library_url=url, library_source="refound", state="live", http="200",
                           checked=today, note=f"refound {today} from {old}: {why}")
            else:
                row.update(state=state, checked=today, note=f"{state} {today}: {why}")
            print(f"  {row['iso3']} {row['host']:<32} {state:<8} {why}"
                  f"{'  -> ' + url if state == 'live' else ''}", flush=True)
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows[k] for k in sorted(rows))
    states = collections.Counter(r.get("state") or "unprobed" for r in rows.values())
    print("  " + ", ".join(f"{k} {v}" for k, v in sorted(states.items())))
    return 0


FETCH_LIST = Path(status_lib.EXCHANGE) / "fetch-list.md"
QUARTER = 91            # days between two batches to the fetch list


def fetch_list(dry_run: bool) -> int:
    """The `manual` rows to `X:\\fetch-list.md`, one batch a quarter: a row not listed in the
    last 91 days gets one line, numbered on from the file's highest, and `listed` is dated."""
    today = dt.date.today()
    fields, rows = read_existing()
    fields = fields + [c for c in ("note", "listed") if c not in fields]
    listed = [dt.date.fromisoformat(r["listed"]) for r in rows.values() if r.get("listed")]
    if listed and (today - max(listed)).days < QUARTER:
        print(f"budget-watch fetch-list: last batch {max(listed)}; next due "
              f"{max(listed) + dt.timedelta(days=QUARTER)}")
        return 0
    # A library that has given nothing inside the poll's window is not worth a browser visit.
    since = f"{today.year - YEARS_BACK}-01-01"
    due = [r for _, r in sorted(rows.items())
           if r.get("state") == "manual" and (r.get("last_published") or "") >= since]
    if not due:
        print("budget-watch fetch-list: no manual libraries")
        return 0
    text = FETCH_LIST.read_text(encoding="utf-8")
    n = max((int(m) for m in re.findall(r"^x?(\d+)\.", text, re.M)), default=0)
    lines = []
    for r in due:
        n += 1
        why = r.get("note", "").split(": ", 1)[-1] or "no automated route"
        types = r["doc_types"].replace("|", ", ")
        lines.append(
            f"{n}. ({today}) **{r['institution']}, budget library** — "
            f"`{up.urlsplit(r['library_url']).scheme}://{up.urlsplit(r['library_url']).netloc}/`. "
            f"*Budget documents new since {r.get('last_published') or 'the last held'} — "
            f"{types} — into `new/`; the poll ({today}) cannot read this page.* "
            f"Automated route dead, tested {r.get('checked') or today}: {why}.")
        r["listed"] = today.isoformat()
    block = "\n\n".join(lines)
    if dry_run:
        print(block)
        return 0
    FETCH_LIST.write_text(text.rstrip("\n") + "\n\n" + block + "\n", encoding="utf-8", newline="\n")
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows[k] for k in sorted(rows))
    print(f"budget-watch fetch-list: {len(lines)} lines to {FETCH_LIST}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="companions -> lookups/budget-watch.csv")
    b.add_argument("--no-probe", action="store_true", help="skip the fetch of each library page")
    q = sub.add_parser("poll", help="fetch the due library pages and stage what is new")
    q.add_argument("--iso", help="one country")
    q.add_argument("--force", action="store_true", help="poll whether due or not")
    q.add_argument("--dry-run", action="store_true",
                   help="read the pages and list what would be fetched; fetch, stage and record nothing")
    q.add_argument("--limit", type=int, default=25, help="documents fetched per library (default 25)")
    f = sub.add_parser("refind", help="R104: one enumeration for each failed library")
    f.add_argument("--iso", help="one country")
    fl = sub.add_parser("fetch-list", help="R104: the manual libraries to the fetch list, quarterly")
    fl.add_argument("--dry-run", action="store_true", help="print the batch, write nothing")
    args = p.parse_args()
    if args.cmd == "refind":
        return refind(args.iso and args.iso.upper())
    if args.cmd == "fetch-list":
        return fetch_list(args.dry_run)
    if args.cmd == "poll":
        return poll(args.iso and args.iso.upper(), args.force, args.dry_run, args.limit)
    return build(not args.no_probe)


if __name__ == "__main__":
    sys.exit(main())
