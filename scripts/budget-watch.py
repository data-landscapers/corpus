#!/usr/bin/env python3
r"""
budget-watch.py — the list of budget-library pages the poll watches (strategic review 5, R102).

    python scripts/budget-watch.py build              # companions -> lookups/budget-watch.csv, probes each page
    python scripts/budget-watch.py build --no-probe   # the same, without the fetches
    python scripts/budget-watch.py poll               # fetch the due pages, stage what is new
    python scripts/budget-watch.py poll --dry-run --iso KEN --force   # list, fetch no document
    python scripts/budget-watch.py refind             # R104: one enumeration per failed library
    python scripts/budget-watch.py fetch-list         # R104: manual libraries to the fetch list
    python scripts/budget-watch.py followups          # R106: a sitting queued per pulled document
    python scripts/budget-watch.py coverage           # R106: held and absent types, dated

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
   `budget-archive/` companion's `url:`, normalised as `status-stage.py` does. It is dropped
   too if it is not a budget document (`OFF_TOPIC`, or an instrument naming no public money),
   or a twin of one: an abridged or translated edition, a bill whose enacted law is held, a
   monthly TOFE whose year-end is held or whose later month the page lists (they cumulate).
4. It is fetched, and dropped if the body is a web page rather than a file, or if its md5 is in
   `artefact-md5-index.csv` — the same document under another address.
5. What is left is staged, artefact and companion together, to
   `X:\new-queue\budget-poll-{ISO3}\`, and `READY` is written last. A folder still waiting for
   the pull is not written into; the run takes `budget-poll-{ISO3}-{YYYYMMDD}` instead.

The companion is a catalogue page on `BUDGET-COLLECT.md` step 2's shape, with `artefact:`
naming the file beside it, `source_tier: budget-document` and the type the link matched.
`published:` is read off a PDF — the latest date on its cover (`date_source: source`), else its
creation stamp — and only failing that is the server's `Last-Modified` or the upload folder's
month (`derived`). `fiscal_years_covered` is every year the link states: an MTEF is its range.
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

# `notes-for-corpus` 65: of the first poll's 233 staged, ingest dropped 91 — a third off-topic,
# the rest twins or subsets of what is held. These run on the folded link after a type matched.
# Files a library lists beside its budget documents that are not one.
OFF_TOPIC = re.compile(strip_marks(
    r"strategic plan|business plan|\bjournal\b|newsletter|economic brief|debt strategy|\bmtds\b"
    r"|appel (a|d) (candidature|offres?)|avis d appel|tender|\bminutes\b|proces verbal"
    r"|meeting calendar|calendario do|reunions? periodiques|advisory|invitation to submit"
    r"|investor engagements|close out period|lock up|public notice|speech day"
    r"|value for money|\bvfm\b|audit committee|circulaire preparatoire|guideline for the preparation"))
# `loi n`, `decret` and `arrete` type any law or order: one that names no public money is not
# a budget instrument (the first poll's electronic-communications law and a travel-allowance order).
MONEY = re.compile(strip_marks(
    r"financ|budget|credit|orcament|appropriation|depense|recette|tresor|fiscal|tax|impot"
    r"|revenue|expenditure|reglement|\bp?lf[ir]?\b|المالية|الميزانية|الموازنة|الاعتمادات"))
# A shortened or translated edition of a document whose full original is what gets held.
ABRIDGED = re.compile(r"\b(resume|synthese|summary|abridged|simplified|highlights)\b")
TRANSLATION = re.compile(r"amharic|malagasy|english version|french version|translation|traduction"
                         r"|version (anglaise|francaise|malgache)")
# A bill, a draft or a volume as submitted, which the enacted law supersedes once it is held.
BILL = re.compile(r"projet de loi|\bplfr?\b|\bplfr?20|\bbill\b|as submitted|proposta de (lei|orcamento)")
# ...unless the file is about the bill — a note on it, or the Budget Office's analysis of it.
ABOUT_BILL = re.compile(r"\bnote\b|analyse|mesures|\bpbo\b|brief|assessment|presentation")
TOFE = re.compile(r"\btofe\b")
# A held slug that is a year's closing TOFE: `…-tofe-decembre-2024…`, `…-tofe-12-2024…`, `…-tofe-annuel-2024…`.
YEAR_END_TOFE = re.compile(r"tofe-(?:.*-)?(?:dec|decembre|december|12|annuel|annual)-(20[0-4]\d)")
MONTH_WORDS = [r"janv?(ier)?|jan(uary)?|janeiro", r"fev(rier)?|feb(ruary)?|fevereiro", r"mars?|march|marco",
               r"avr(il)?|apr(il)?|abr(il)?", r"mai|may|maio", r"juin|june?|junho",
               r"juil(let)?|july?|julho", r"aout|aou|aug(ust)?|ago(sto)?", r"sept?(embre|ember)?|set(embro)?",
               r"oct(obre|ober)?|out(ubro)?", r"nov(embre|ember|embro)?", r"dec(embre|ember)?|dez(embro)?"]
MONTH_RES = [re.compile(rf"\b({w})\b") for w in MONTH_WORDS]

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


def fy_labels(text: str, fy_month: str) -> list[str]:
    """Every fiscal year the title states, as `fiscal_years_covered` holds them. A range —
    `2026-2028`, `2026 a 2028`, `2025/26-2027/28` — is every year in it (an MTEF is three, not
    its last); `2025/26` from `2025-2026`, `2025/26` or `2025_26` where the year is split; a bare
    year only where the fiscal year is the calendar year, since elsewhere it is ambiguous."""
    text = strip_marks(text).replace("–", "-").replace("—", "-")
    split = r"(20[0-4]\d)\s*[/\-_]\s*(?:20)?([0-4]\d)(?!\d)"
    m = re.search(rf"(?<!\d){split}\s*(?:-|a|to|au)\s*{split}", text)
    if m and int(m.group(2)) == (int(m.group(1)) + 1) % 100 and 0 < int(m.group(3)) - int(m.group(1)) <= 6:
        return [f"{y}/{(y + 1) % 100:02d}" for y in range(int(m.group(1)), int(m.group(3)) + 1)]
    m = re.search(r"(?<!\d)(20[0-4]\d)\s*(?:-|_|/|a|to|au)\s*(20[0-4]\d)(?!\d)", text)
    if m and fy_month == "01" and 0 < int(m.group(2)) - int(m.group(1)) <= 6:
        return [str(y) for y in range(int(m.group(1)), int(m.group(2)) + 1)]
    m = re.search(rf"(?<!\d){split}", text)
    if m and int(m.group(2)) == (int(m.group(1)) + 1) % 100:
        return [f"{m.group(1)}/{m.group(2)}"]
    ys = sorted(set(years_in(text)))
    return [str(ys[-1])] if ys and fy_month == "01" else []


def month_of(folded: str) -> int | None:
    """The month a monthly report names: `juin`, `sept`, `jan`, or `TOFE-04-2025`'s `04`."""
    m = re.search(r"tofe (0?[1-9]|1[0-2]) 20[0-4]\d", folded)
    if m:
        return int(m.group(1))
    return next((n for n, rx in enumerate(MONTH_RES, 1) if rx.search(folded)), None)


def tofe_period(href: str, label: str) -> tuple[int, int] | None:
    """(year, month) of a monthly TOFE link, the year from the upload folder where the name
    omits it (`TOFE-Fev.pdf` in `/2025/03/` is February 2025)."""
    folded = fold(label)
    if not TOFE.search(folded):
        return None
    month = month_of(folded)
    if not month:
        return None
    ys = years_in(label)
    if ys:
        return max(ys), month
    m = re.search(r"/(20[0-4]\d)/(0[1-9]|1[0-2])/", up.urlsplit(href).path)
    if not m:
        return None
    return (int(m.group(1)) if month <= int(m.group(2)) else int(m.group(1)) - 1), month


def superseded(href: str, label: str, doc_type: str, iso3: str, fy_month: str,
               acts: set[tuple[str, int]], year_end_tofes: set[tuple[str, int]]) -> str:
    """Why a typed link is a twin of what is held or better fetched, else ''."""
    folded = fold(label)
    if OFF_TOPIC.search(folded):
        return "off-topic"
    if doc_type in ("executive-instrument", "appropriation-act") and not MONEY.search(folded):
        return "off-topic"
    if ABRIDGED.search(folded):
        return "abridged"
    if TRANSLATION.search(folded):
        return "translation"
    if (doc_type in ("budget-estimates", "appropriation-act") and BILL.search(folded)
            and not ABOUT_BILL.search(folded)):
        fys = fy_labels(label, fy_month)
        year = int(fys[0][:4]) if fys else max(years_in(label), default=0)
        if (iso3, year) in acts:
            return "superseded: the enacted law is held"
    period = tofe_period(href, label)
    if period and period[1] < 12 and (iso3, period[0]) in year_end_tofes:
        return "superseded: the year-end TOFE is held"
    return ""


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


MONTH_NAME = (r"(?P<mon>" + "|".join(f"(?P<m{n}>{w})" for n, w in enumerate(MONTH_WORDS, 1)) + ")")
DAY_DATE = [
    re.compile(rf"\b(?P<d>[0-3]?\d)(er|st|nd|rd|th)?\s+(de\s+)?{MONTH_NAME}\.?,?\s+(de\s+)?(?P<y>20[0-4]\d)\b"),
    re.compile(rf"\b{MONTH_NAME}\.?\s+(?P<d>[0-3]?\d)(st|nd|rd|th)?,?\s+(?P<y>20[0-4]\d)\b"),
    re.compile(r"\b(?P<d>[0-3]?\d)[/.](?P<mn>[01]?\d)[/.](?P<y>20[0-4]\d)\b"),
]
MONTH_DATE = re.compile(rf"\b{MONTH_NAME}\.?\s+(de\s+)?(?P<y>20[0-4]\d)\b")
# A date that ends a period is what the document covers, not when it was issued.
# Spacing tolerated: a text layer can read `END IN G 30TH JUNE`.
PERIOD_END = re.compile(r"(e ?n ?d ?(e ?d|i ?n ?g)|as at|as of|au|clos|jusqu|until|through|findo|to|a)"
                        r"\s+(le\s+)?$")


def cover_date(text: str, today: dt.date) -> tuple[str, str]:
    """The latest date on the cover no later than today, to the day, else to the month: an act
    cites older acts and a report the period before it, so the newest date is the issue.
    ('', '') where the cover states none."""
    text = strip_marks(text)
    days, months = [], []
    for rx in DAY_DATE:
        for m in rx.finditer(text):
            if PERIOD_END.search(text[max(0, m.start() - 14):m.start()]):
                continue
            mon = int(m.group("mn")) if "mn" in m.groupdict() and m.group("mn") else next(
                n for n in range(1, 13) if m.group(f"m{n}"))
            try:
                days.append(dt.date(int(m.group("y")), mon, int(m.group("d"))))
            except ValueError:
                pass
    for m in MONTH_DATE.finditer(text):
        mon = next(n for n in range(1, 13) if m.group(f"m{n}"))
        months.append(dt.date(int(m.group("y")), mon, 1))
    days = [d for d in days if dt.date(2000, 1, 1) <= d <= today]
    if days:
        return max(days).isoformat(), "day"
    months = [d for d in months if dt.date(2000, 1, 1) <= d <= today]
    return (max(months).isoformat(), "month") if months else ("", "")


DATE_FROM = {  # where `published` came from: `cover` is `date_source: source`, the rest `derived`
    "cover": "the latest date on the document's first pages",
    "stamp": "the PDF's creation stamp: its first pages state no date",
    "server": "the server's Last-Modified: the file states no date the poll could read",
    "folder": "the upload folder's month, or the poll's: neither the file nor the server dates it",
}


def pdf_date(body: bytes, today: dt.date, first_fy: int = 0) -> tuple[str, str, str]:
    """(published, date_precision, `DATE_FROM` key) off the PDF itself: the cover's date, else
    the file's creation stamp; ('', '', '') where it has neither. A cover date more than a year
    before `first_fy`, the first fiscal year the link names, is a law it cites, not its own."""
    try:
        import pymupdf  # noqa: PLC0415
        doc = pymupdf.open(stream=body, filetype="pdf")
    except Exception:  # noqa: BLE001 - not a PDF pymupdf can open: the server's date stands
        return "", "", ""
    text = ""
    for page in doc.pages(0, min(2, doc.page_count)):
        text += page.get_text() + "\n"
        if len(text) > 400:     # a cover with words on it; a blank or scanned one reads on
            break
    published, precision = cover_date(text, today)
    if published and int(published[:4]) >= first_fy - 1:
        return published, precision, "cover"
    m = re.match(r"D:(20[0-4]\d)(\d\d)(\d\d)", (doc.metadata or {}).get("creationDate") or "")
    if m:
        try:
            made = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if made <= today:
                return made.isoformat(), "day", "stamp"
        except ValueError:
            pass
    return "", "", ""


def pdf_pages(body: bytes) -> int | None:
    try:
        import pymupdf  # noqa: PLC0415
        return pymupdf.open(stream=body, filetype="pdf").page_count
    except Exception:  # noqa: BLE001 - a PDF pymupdf cannot open is still a document
        return None


# Link text that names the action, not the document: the filename says more.
GENERIC = re.compile(r"(telecharger|download|read more|lire la suite|en savoir plus|voir|view|"
                     r"open|pdf|click here|cliquez ici|baixar|descarregar|تحميل|ver mais)( ?(le|the) ?"
                     r"(document|fichier|file|pdf))?")


def link_title(url: str, text: str) -> str:
    """The link's text, unless it is short or a directory listing's truncation (`NAME..>`):
    then the filename, separators to spaces."""
    text = re.sub(r"^download\s+|\s+download$", "", text, flags=re.I).strip()
    if len(text) >= 8 and not text.endswith(("..>", "...", "…")) and not GENERIC.fullmatch(fold(text).strip()):
        return text
    name = os.path.splitext(up.unquote(os.path.basename(up.urlsplit(url).path)))[0]
    return re.sub(r"[_\-]+", " ", name).strip() or text


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def companion(row: dict, url: str, text: str, doc_type: str, artefact: str, body: bytes,
              published: str, precision: str, source: str, fys: list[str], batch: str,
              today: dt.date) -> str:
    title = link_title(url, text)
    pages = pdf_pages(body) if artefact.endswith(".pdf") else None
    extent = f"{pages} pp, " if pages else ""
    fm = [
        "---", "type: source", f"title: {yaml_str(title)}", f"url: {url}",
        f"publisher: {yaml_str(row['institution'])}", f"published: {published}",
        f"date_precision: {precision}",
        f"date_source: {'source' if source == 'cover' else 'derived'}", f"places: [{row['iso3']}]",
        "topics: [finance.budget]", "entities: []", f"retrieved: {today}",
        f"sweep_batch: {batch}",
    ]
    if fys:
        fm.append("fiscal_years_covered: [" + ", ".join(f'"{y}"' for y in fys) + "]")
    fm += [f"doc_type: {doc_type}", "source_tier: budget-document", f"artefact: {artefact}",
           "body_completeness: excerpt", "---", ""]
    body_md = [
        f"# {title}", "",
        "## Document", "",
        f"{extent}{len(body):,} bytes, md5 `{hashlib.md5(body).hexdigest()}`. Not read: the type, "
        "the fiscal years are read off the link and the date off the file, and the "
        "instrument, scope, currency and printed scale are ingest's to state.", "",
        "## Source", "",
        f"Listed as \"{text}\" on {row['institution']}'s library page, <{row['library_url']}>, "
        f"polled {today}.", "",
        "## Notes", "",
        f"Found by CORPUS's budget poll (`budget-watch.py poll`, strategic review R103): new on "
        f"the page since the last poll and held nowhere by URL or md5. `doc_type` is the "
        f"keyword match on the link. `published` is {DATE_FROM[source]}.", "",
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
    label = f"{text} {up.unquote(os.path.basename(up.urlsplit(href).path))}"
    fys = fy_labels(label, row.get("fy_start_month", ""))
    first_fy = int(fys[0][:4]) if fys else min(years_in(label), default=0)
    published, precision, source = (pdf_date(body, today, first_fy) if ext == ".pdf"
                                    else ("", "", ""))
    if not published:
        published, precision = published_of(href, last_mod, today)
        source = "server" if precision == "day" else "folder"
    stem = base = f"{published}-{row['iso3'].lower()}-{slugify(link_title(href, text), 70)}"
    n = 2
    while (folder / f"{stem}{ext}").exists():
        stem, n = f"{base}-{n}", n + 1
    batch = folder.name if re.search(r"-\d{8}$", folder.name) else f"{folder.name}-{today:%Y%m%d}"
    (folder / f"{stem}{ext}").write_bytes(body)
    (folder / f"{stem}-companion.md").write_text(
        companion(row, href, text, doc_type, f"{stem}{ext}", body, published, precision, source,
                  fys, batch, today), encoding="utf-8", newline="\n")
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
    docs = budget_documents()
    acts = {(d["iso3"], d["fy"]) for d in docs if d["doc_type"] == "appropriation-act" and d["fy"]}
    year_end_tofes = {(d["iso3"], int(m.group(1))) for d in docs
                      if (m := YEAR_END_TOFE.search(d["slug"]))}
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
            # Only a document link can become a candidate, so only one is recorded: the rest of
            # a page's navigation would be 40,000 rows a poll that nothing ever reads back.
            if not is_document(href):
                continue
            counts["docs"] += 1
            if href in seen[key]:
                continue
            counts["new"] += 1
            outcome = ""
            label = f"{text} {up.unquote(os.path.basename(up.urlsplit(href).path))}"
            doc_type = doc_type_of(label)
            ys = years_in(label)
            if not doc_type:
                outcome = "untyped"
            elif ys and max(ys) < today.year - YEARS_BACK:
                outcome = "old"
            elif not ys and first:
                outcome = "undated"
            elif ss.norm(href) in held:
                outcome = "held"
            else:
                outcome = superseded(href, label, doc_type, key[0], row.get("fy_start_month", ""),
                                     acts, year_end_tofes)
            if outcome:
                counts[outcome.split(":")[0]] += 1
                link_rows.append({"iso3": key[0], "host": key[1], "url": href, "first_seen": today,
                                  "outcome": outcome, "doc_type": doc_type})
                continue
            cands.append((href, text, doc_type, tofe_period(href, label)))
        # Monthly TOFEs are cumulative: the latest a page lists for a year contains the rest.
        latest: dict[int, int] = {}
        for *_, period in cands:
            if period:
                latest[period[0]] = max(latest.get(period[0], 0), period[1])
        for href, _, doc_type, period in [c for c in cands if c[3] and c[3][1] < latest[c[3][0]]]:
            counts["superseded"] += 1
            link_rows.append({"iso3": key[0], "host": key[1], "url": href, "first_seen": today,
                              "outcome": "superseded: a later cumulative TOFE is listed",
                              "doc_type": doc_type})
        cands = [c[:3] for c in cands if not c[3] or c[3][1] == latest[c[3][0]]]
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
        print(f"  {key[0]} {key[1]:<30} links {counts['links']:>5}  new docs {counts['new']:>4}  "
              f"docs {counts['docs']:>4}  untyped {counts['untyped']:>3}  "
              f"old {counts['old']:>3}  undated {counts['undated']:>3}  held {counts['held']:>3}  "
              f"off {counts['off-topic']:>3}  twin {counts['abridged'] + counts['translation'] + counts['superseded']:>3}  "
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


RAW = Path(MIRROR) / "raw"
FOLLOWUPS = ROOT / "logs" / "budget-followups.md"
FOLLOWUPS_HEAD = "## Queued by the budget poll"
COVERAGE = ROOT / "outputs" / "budgets" / "coverage.csv"
GRACE = 1               # months past a type's usual release before it counts as not held


def doc_stages() -> dict[str, str]:
    with open(LOOKUPS / "budget-doc-types.csv", encoding="utf-8-sig", newline="") as fh:
        return {r["doc_type"]: r["stages"] for r in csv.DictReader(fh)}


def fy_of(fm: dict) -> int | None:
    """The bare start year of the first fiscal year a document covers (`layout.md`: `2024` is
    the year beginning in 2024), from `fiscal_years_covered`, else the older single keys."""
    for key in ("fiscal_years_covered", "fiscal_year_label", "fiscal_year", "fy_start"):
        m = re.search(r"(20[0-4]\d)", fm.get(key, ""))
        if m:
            return int(m.group(1))
    return None


def budget_documents() -> list[dict]:
    """Every held budget document: the `budget-archive/` companions and the `raw/` records
    that are budget documents, one entry per slug."""
    docs: dict[str, dict] = {}
    paths = list(ARCHIVE.glob("*/*/*companion.md"))
    for f in RAW.rglob("*.md"):
        with open(f, encoding="utf-8", errors="replace") as fh:
            head = fh.read(4096)
        if "source_tier: budget-document" in head or "sweep_batch: budget-poll-" in head:
            paths.append(f)
    for f in paths:
        fm = frontmatter(f)
        m = re.search(r"\[?\s*([A-Z]{3})", fm.get("places", ""))
        if not m or not fm.get("doc_type"):
            continue
        docs[f.stem] = {"slug": f.stem, "iso3": m.group(1), "doc_type": fm["doc_type"],
                        "fy": fy_of(fm), "published": fm.get("published", ""),
                        "precision": fm.get("date_precision", ""),
                        "batch": fm.get("sweep_batch", ""), "raw": f.is_relative_to(RAW)}
    return list(docs.values())


def followups(docs: list[dict] | None = None) -> int:
    """R106: a document the poll delivered, now in `raw/`, for a country-year Corpus has
    already extracted, queues one line in `logs/budget-followups.md` — one BUDGET-EXTRACT
    sitting for that country-year, R58's grain. Queued once: a slug already in the file is
    never queued again, and the sitting strikes the line (deletes it) when it settles it."""
    docs = budget_documents() if docs is None else docs
    stages = doc_stages()
    text = FOLLOWUPS.read_text(encoding="utf-8") if FOLLOWUPS.exists() else ""
    today = dt.date.today().isoformat()
    lines = []
    for d in sorted(docs, key=lambda d: (d["iso3"], d["fy"] or 0, d["slug"])):
        if not (d["raw"] and d["batch"].startswith("budget-poll-")) or f"[[{d['slug']}]]" in text:
            continue
        year_file = BUDGETS / d["iso3"] / f"{d['fy']}.csv"
        if not year_file.exists():
            continue
        held = set()
        with open(year_file, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                held |= {s for s in ("proposed", "appropriated", "revised", "released", "actual",
                                     "audited") if (row.get(s) or "").strip()}
        wanted = stages.get(d["doc_type"], "")
        new = [s for s in wanted.split("|") if s and s not in held and s not in ("none", "as-stated")]
        adds = (f"adds {' or '.join(new)}" if new else
                f"{wanted.replace('|', ' or ')} already held — read it for a revision")
        lines.append(f"- **{d['iso3']} FY{d['fy']}** — {d['doc_type']} {adds}: [[{d['slug']}]] "
                     f"(queued {today}).")
    if lines:
        text = text.rstrip("\n") + "\n"
        if FOLLOWUPS_HEAD not in text:
            text += (f"\n{FOLLOWUPS_HEAD}\n\nOne BUDGET-EXTRACT sitting a line (R106). "
                     "`budget-watch.py followups` writes them; delete a line in the commit that "
                     "settles it.\n\n")
        FOLLOWUPS.write_text(text + "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"budget-watch followups: {len(lines)} queued")
    return 0


def month_index(iso_date: str) -> int | None:
    m = re.match(r"(\d{4})-(\d{2})", iso_date or "")
    return int(m.group(1)) * 12 + int(m.group(2)) - 1 if m else None


def coverage(docs: list[dict] | None = None) -> int:
    """R106: the coverage table's data. For each country, each type it has published and each
    fiscal year from `YEARS_BACK` years ago to this one: `held`, or `absent` once the type is
    due by that country's own calendar, or `not due`. The calendar is the median gap, in months,
    between a fiscal year's start and the type's publication across the documents held, plus
    `GRACE`. Written to `outputs/budgets/coverage.csv`, dated; the absences are review 6's count."""
    docs = budget_documents() if docs is None else docs
    stages = doc_stages()
    _, rows = read_existing()
    fsm = {}
    for r in rows.values():
        if r.get("fy_start_month"):
            fsm[r["iso3"]] = int(r["fy_start_month"])
    today = dt.date.today()
    now = today.year * 12 + today.month - 1
    gaps: dict[tuple[str, str], list[int]] = collections.defaultdict(list)
    held: dict[tuple[str, str, int], list[str]] = collections.defaultdict(list)
    for d in docs:
        if d["fy"] is None or d["iso3"] not in fsm:
            continue
        held[(d["iso3"], d["doc_type"], d["fy"])].append(d["slug"])
        pub = month_index(d["published"])
        if pub is not None and d["precision"] in ("day", "month"):
            gaps[(d["iso3"], d["doc_type"])].append(pub - (d["fy"] * 12 + fsm[d["iso3"]] - 1))
    out = []
    for (iso3, doc_type), g in sorted(gaps.items()):
        if stages.get(doc_type, "none") in ("none", "as-stated"):
            continue                    # a statement or a procurement plan is not a budget stage
        gap = sorted(g)[len(g) // 2]
        for fy in range(today.year - YEARS_BACK, today.year + 1):
            due = fy * 12 + fsm[iso3] - 1 + gap + GRACE
            slugs = held.get((iso3, doc_type, fy), [])
            status = "held" if slugs else "absent" if due <= now else "not due"
            out.append({"iso3": iso3, "fiscal_year": fy, "doc_type": doc_type,
                        "stages": stages.get(doc_type, ""), "status": status,
                        "due": f"{due // 12}-{due % 12 + 1:02d}", "held": len(slugs),
                        "as_of": today.isoformat()})
    COVERAGE.parent.mkdir(parents=True, exist_ok=True)
    with open(COVERAGE, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    count = collections.Counter(r["status"] for r in out)
    print(f"budget-watch coverage: {len({r['iso3'] for r in out})} countries, "
          + ", ".join(f"{k} {v}" for k, v in sorted(count.items()))
          + f" -> {COVERAGE.relative_to(ROOT)}")
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
    sub.add_parser("followups", help="R106: queue an extract sitting for each pulled document")
    sub.add_parser("coverage", help="R106: held and absent types per country-year")
    args = p.parse_args()
    if args.cmd == "followups":
        return followups()
    if args.cmd == "coverage":
        return coverage()
    if args.cmd == "refind":
        return refind(args.iso and args.iso.upper())
    if args.cmd == "fetch-list":
        return fetch_list(args.dry_run)
    if args.cmd == "poll":
        return poll(args.iso and args.iso.upper(), args.force, args.dry_run, args.limit)
    return build(not args.no_probe)


if __name__ == "__main__":
    sys.exit(main())
