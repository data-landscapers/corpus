#!/usr/bin/env python3
r"""external-claims.py — global databases taken apart into claims, and their documents staged.

    python scripts/external-claims.py fetch SOURCE     download today's edition, unless unchanged
    python scripts/external-claims.py claims SOURCE    the latest edition -> claims.csv
    python scripts/external-claims.py stage SOURCE     documents not held -> new-queue/, no READY
    python scripts/external-claims.py ready SOURCE     after lint-staged-queue passes: READY

`documentation/external-datasets.md` is the design. Sources are rows of
`lookups/external-sources.csv`. Each has an adapter here, and every adapter writes the same table.

**What is kept is the evidence, not the score.** A claim is one thing the database says about one
country: a status, a name, a year, a link. `reference/external/{source}/{edition}/` holds the
download as fetched, never rewritten, and `claims.csv` beside it. `reference/external/claims.csv`
is every source's latest edition together, which is what a study reads.

**`lookups/external-items.csv` maps a source's question to a study, and says how well it fits**:
`same`, `partial`, `theirs-broader`, `theirs-narrower` or `none`. A question with no study is
still converted. Where theirs is better conceived than ours, the `note` says so, and those rows
are the case for changing an indicator (Bill, 2026-11-10).

**Staging takes documents only.** A link to a law, strategy or framework is staged; a portal,
home page or login is evidence that a system exists, and stays a claim. A document is staged when
neither its URL (`status-stage.norm` against OSINT's indexes) nor its title and country (against
the catalogue) is held. It goes to `new-queue/dataset-external-{source}-NN/`, 40 to a batch, in
`status-stage.py`'s file format. The database itself is staged once per edition as one record,
which is what a claim cites when it has no primary (Bill, 2026-11-10: cite the primary wherever
one exists). `staging.csv` beside the claims records every link's outcome, so a rerun only
fetches what is new.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import threading
import html
import importlib.util
import io
import os
import pathlib
import re
import sys
import unicodedata
import urllib.parse as up
from concurrent.futures import ThreadPoolExecutor

import requests

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import status_lib  # noqa: E402

spec = importlib.util.spec_from_file_location("status_stage", HERE / "status-stage.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)

SOURCES = ROOT / "lookups" / "external-sources.csv"
ITEMS = ROOT / "lookups" / "external-items.csv"
COUNTRIES = ROOT / "lookups" / "countries.csv"
CATALOGUE = ROOT / "outputs" / "catalogue" / "catalogue-internal.csv"
BASE = ROOT / "reference" / "external"
QUEUE = pathlib.Path(status_lib.EXCHANGE) / "new-queue"
BATCH = 40

COLUMNS = ["source", "edition", "survey_year", "iso3", "item", "question", "status", "name",
           "year", "url", "documents", "basis", "studies", "fit"]


def rows(path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path, header, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header, lineterminator="\n")
        w.writeheader()
        w.writerows(data)


def source(sid: str) -> dict:
    for r in rows(SOURCES):
        if r["id"] == sid:
            return r
    sys.exit(f"{sid} is not a row of {SOURCES.name}")


def editions(sid: str) -> list[pathlib.Path]:
    d = BASE / sid
    return sorted(p for p in d.iterdir() if p.is_dir()) if d.exists() else []


def fold(t: str) -> str:
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def countries() -> dict[str, str]:
    """folded name -> iso3, with the spellings the sources use."""
    out = {fold(r["country-name"]): r["iso-3"] for r in rows(COUNTRIES)}
    out.update({"drc": "COD", "democratic republic of the congo": "COD", "congo dem rep": "COD",
                "cote d ivoire": "CIV", "c te d ivoire": "CIV", "the gambia": "GMB",
                "sao tome": "STP", "swaziland": "SWZ", "african union au": "XAF",
                "african union": "XAF", "cabo verde": "CPV", "united republic of tanzania": "TZA", "republic of the congo": "COG"})
    return out


def clean_value(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip()
    return "" if s in ("-", "New", "n/a", "N/A") or s.startswith("=") else s


# --- mapping ---------------------------------------------------------------------------------

def mapping(sid: str) -> dict:
    """item -> [(class, study, fit)]."""
    m = collections.defaultdict(list)
    for r in rows(ITEMS):
        if r["source"] == sid:
            m[r["item"].strip().lower()].append((r["class"], r["study"], r["fit"]))
    return m


def studies_for(m: dict, items: list[str], klass: str = "") -> tuple[str, str]:
    st, fits = [], []
    for it in items:
        for c, study, fit in m.get(it.lower(), []):
            if study and (not c or c == klass) and study not in st:
                st.append(study)
                fits.append(fit)
    return ";".join(st), ";".join(fits)


# --- adapters --------------------------------------------------------------------------------

def tag(t: str) -> str:
    t = re.sub(r"\s+", " ", t.strip().lower())
    t = t.replace("centerss", "centers").replace("specialised", "specialized")
    t = t.replace(" and tv white spaces and tv white spaces", " and tv white spaces")
    return {"start-ups": "startups", "foundational skill": "foundational skills"}.get(t, t)


def adapt_aftech(d, edition, release) -> list[dict]:
    import openpyxl  # noqa: PLC0415
    ws = openpyxl.load_workbook(d / "original.xlsx", read_only=True).worksheets[0]
    data = list(ws.iter_rows(values_only=True))
    head = [str(h or "").strip() for h in data[0]]
    col = {h: i for i, h in enumerate(head) if h}
    names, m, out = countries(), mapping("aftech"), []
    for r in data[1:]:
        name = clean_value(r[col["Law, Policy or Regulation name"]])
        if not name:
            continue
        place = clean_value(r[col["Country"]])
        iso = names.get(fold(place)) or names.get(fold(place).replace("the ", ""))
        if not iso:
            print(f"aftech: no iso3 for {place!r}; row kept with iso3 blank", file=sys.stderr)
        klass = clean_value(r[col["Classification"]])
        tags = [tag(t) for t in clean_value(r[col["Key Data Points"]]).split(",") if t.strip()]
        st, fit = studies_for(m, tags, klass)
        year = clean_value(r[col["Date"]])
        out.append({
            "source": "aftech", "edition": edition, "survey_year": "", "iso3": iso or "",
            "item": "; ".join(tags),
            "question": f"{clean_value(r[col['Digital Economy Pillar']])} / {clean_value(r[col['Sub Pillars']])}",
            "status": klass, "name": name, "year": year,
            "url": "", "documents": clean_value(r[col["Document Link"]]),
            "basis": "publisher-compiled", "studies": st, "fit": fit})
    return out


DOC_WORDS = re.compile(r"(?i)strateg|polic|law|regulation|framework|report|plan|guideline|"
                       r"document|roadmap|act\b")


def gtmi_meta(wb) -> dict:
    """sub-question id -> (question, format), first occurrence wins."""
    meta = {}
    for r in wb["Metadata"].iter_rows(values_only=True):
        k = str(r[0] or "").strip()
        if re.fullmatch(r"I-\d+(\.\d+)*", k) and k not in meta:
            meta[k] = (str(r[1] or "").strip(), str(r[2] or "").strip())
    return meta


def decode(fmt: str, v: str) -> str:
    """`2` under `0= No, 1= Draft, 2= Yes (Effective)` -> `2 Yes (Effective)`."""
    for code, label in re.findall(r"(\d+)\s*=\s*(.+?)(?=,?\s*\d+\s*=|$)", fmt):
        if code == v:
            return f"{v} {label.strip(' ,')}"
    return v


def adapt_gtmi(d, edition, release) -> list[dict]:
    import openpyxl  # noqa: PLC0415
    wb = openpyxl.load_workbook(d / "original.xlsx", read_only=True)
    meta = gtmi_meta(wb)
    data = list(wb["GTMI_Data"].iter_rows(values_only=True))
    head = [str(h or "").strip() for h in data[0]]
    ours = {r["iso-3"] for r in rows(COUNTRIES)}
    m, out = mapping("gtmi"), []
    isrc = head.index("Src")
    for r in data[1:]:
        iso = str(r[1] or "").strip()
        if iso not in ours:
            continue
        basis = {"S": "self-reported", "R": "publisher-assessed"}.get(str(r[isrc]).strip(), "")
        groups = collections.defaultdict(dict)
        for h, v in zip(head, r):
            if re.fullmatch(r"I-\d+(\.\d+)*", h):
                v = clean_value(v)
                if v:
                    groups[h.split(".")[0]][h] = v
        for root in sorted(groups, key=lambda k: int(k[2:])):
            g = groups[root]
            q, fmt = meta.get(root, ("", ""))
            names, years, docs, urls = [], [], [], []
            for k, v in g.items():
                if k == root:
                    continue
                sq, sf = meta.get(k, ("", ""))
                if v.lower().startswith(("http://", "https://", "www.")):
                    is_doc = "document" in sf.lower() or "report" in sf.lower() or \
                        bool(DOC_WORDS.search(sq.split(">")[-1]))
                    (docs if is_doc and not re.search(r"(?i)home page|portal|platform", sq)
                     else urls).append(v)
                elif sf.upper() == "YYYY":
                    years.append(v)
                elif sf.lower() == "text":
                    names.append(v)
            st, fit = studies_for(m, [root])
            out.append({
                "source": "gtmi", "edition": edition, "survey_year": clean_value(r[0]),
                "iso3": iso, "item": root, "question": q,
                "status": decode(fmt, g.get(root, "")), "name": "; ".join(names),
                "year": years[0] if years else "", "url": urls[0] if urls else "",
                "documents": " ".join(dict.fromkeys(docs)), "basis": basis,
                "studies": st, "fit": fit})
    return out


UNCTAD_AREAS = ["Electronic Transactions", "Consumer Protection", "Privacy and Data Protection",
                "Cybercrime", "Indirect Taxation"]


def adapt_unctad(d, edition, release) -> list[dict]:
    """`data.csv` gives each country's status in five areas; `document_links.json` the laws
    behind it, each a (url, name) pair. One claim per law, or one per area where none is linked."""
    import json  # noqa: PLC0415
    status = {r["code"]: r for r in rows(d / "data.csv") if r.get("Africa") == "1"}
    links = json.loads((d / "document_links.json").read_text(encoding="utf-8-sig"))
    names, m, out = countries(), mapping("unctad"), []
    for code, r in status.items():
        iso = names.get(fold(r["country"]))
        if not iso:
            print(f"unctad: no iso3 for {r['country']!r}; row kept with iso3 blank", file=sys.stderr)
        for area in UNCTAD_AREAS:
            st, fit = studies_for(m, [area.lower()])
            laws = (links.get(code) or {}).get(area) or [[ "", "" ]]
            for url, name in laws:
                years = re.findall(r"\b((?:19|20)\d{2})\b", name or "")
                out.append({
                    "source": "unctad", "edition": edition, "survey_year": "", "iso3": iso or "",
                    "item": area.lower(), "question": f"{area} legislation", "status": r[area],
                    "name": re.sub(r"\s*<br\s*/?>\s*", " ", name or "").strip(),
                    "year": years[-1] if years else "", "url": "",
                    "documents": (url or "").strip().replace(" ", "%20"),
                    "basis": "publisher-compiled", "studies": st, "fit": fit})
    return out


ODIN_API = "https://odin-aim.akroninc.net/api/api/client"
ODIN_YEARS = [2016, 2017, 2018, 2020, 2022, 2024]
# What the profile carries that a claim is made from; the rest is chart data and weights.
ODIN_KEEP = ("country", "dataReports", "input", "categoryInputSource", "categories", "criteria",
             "odinScores", "selectedYear", "participatedInReview")


def fetch_odin(sid: str) -> list[tuple[str, bytes]]:
    """ODIN publishes no file; its site reads `GetCountryProfile/{year}/{ISO3}` (found from the
    site's own script, 2026-11-10). One profile per country and round, trimmed to ODIN_KEEP and
    gathered into one gzip, written with mtime 0 so an unchanged edition hashes the same."""
    import gzip  # noqa: PLC0415
    import json  # noqa: PLC0415
    ours = [r["iso-3"] for r in rows(COUNTRIES) if not r["iso-3"].startswith("X")]

    def one(job):
        iso, year = job
        r = requests.post(f"{ODIN_API}/GetCountryProfile/{year}/{iso}", json={},
                          headers={"User-Agent": ss.UA}, timeout=120)
        r.raise_for_status()
        j = r.json()
        keep = {k: j.get(k) for k in ODIN_KEEP}
        for i in keep.get("input") or []:
            i.pop("assessmentDetail", None)
        return iso, year, keep

    out = collections.defaultdict(dict)
    with ThreadPoolExecutor(4) as pool:
        for iso, year, keep in pool.map(one, [(i, y) for i in ours for y in ODIN_YEARS]):
            out[iso][str(year)] = keep
    body = json.dumps(out, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return [("original.json.gz", gzip.compress(body, mtime=0))]


ITU_API = "https://www.itu.int/net4/itu-d/metrics/api/v1.1/tracker"
ITU_PILLARS = {"regulatoryAuthority": "Regulatory authority", "regulatoryMandate": "Regulatory mandate",
               "regulatoryRegime": "Regulatory regime", "competitionFramework": "Competition framework"}


def fetch_itu(sid: str) -> list[tuple[str, bytes]]:
    """The tracker's site (app.gen5.digital) reads ITU's metrics API: `tracker/years`, and
    `tracker/entries?country={ITU's name}&year={y}&brief=false` for the 50 answers (found from
    the site's requests, 2026-11-10). ITU names countries its own way, so its `tracker/countries`
    list maps our ISO3 to the name it wants. Gathered into one gzip, mtime 0."""
    import gzip  # noqa: PLC0415
    import json  # noqa: PLC0415
    h = {"User-Agent": ss.UA}
    years = requests.get(f"{ITU_API}/years", headers=h, timeout=60).json()
    names = {c["isoCode"]: c["country"]
             for c in requests.get(f"{ITU_API}/countries", headers=h, timeout=60).json()}
    ours = [r["iso-3"] for r in rows(COUNTRIES) if not r["iso-3"].startswith("X")]

    def one(job):
        iso, year = job
        r = requests.get(f"{ITU_API}/entries", params={"country": names[iso], "year": year, "brief": "false"},
                         headers=h, timeout=60)
        r.raise_for_status()
        return iso, year, r.json()

    out = collections.defaultdict(dict)
    with ThreadPoolExecutor(4) as pool:
        for iso, year, j in pool.map(one, [(i, y) for i in ours if i in names for y in years]):
            if j:
                out[iso][str(year)] = j[0]
    body = json.dumps(out, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return [("original.json.gz", gzip.compress(body, mtime=0))]


def adapt_itu(d, edition, release) -> list[dict]:
    """One claim per country, year and indicator: ITU's answer in words, with its score."""
    import gzip  # noqa: PLC0415
    import json  # noqa: PLC0415
    data = json.loads(gzip.decompress((d / "original.json.gz").read_bytes()))
    m, out = mapping("itu"), []
    for iso in sorted(data):
        for year in sorted(data[iso]):
            e = data[iso][year]
            for key, pillar in ITU_PILLARS.items():
                for a in e.get(key) or []:
                    item = f"r{a['id']}"
                    st, fit = studies_for(m, [item])
                    v = a.get("value")
                    out.append({
                        "source": "itu", "edition": edition, "survey_year": year, "iso3": iso,
                        "item": item, "question": f"{pillar}: {(a.get('area') or '').strip()}",
                        "status": f"{(a.get('description') or '').strip()} ({v:g})" if v is not None
                                  else (a.get("description") or "").strip(),
                        "name": "", "year": "", "url": "", "documents": "",
                        "basis": "self-reported", "studies": st, "fit": fit})
    return out


FETCHERS = {"odin": fetch_odin, "itu": fetch_itu}

ODIN_CRITERIA = ["indicators", "last 5 years", "last 10 years", "first admin level",
                 "second admin level", "machine-readable", "non-proprietary", "download options",
                 "metadata", "terms of use"]


def adapt_odin(d, edition, release) -> list[dict]:
    """One claim per country, round and data category: the ten element scores as ODIN gave
    them (0, 0.5 or 1), the series found, the latest year of data, and where it was found."""
    import gzip  # noqa: PLC0415
    import json  # noqa: PLC0415
    data = json.loads(gzip.decompress((d / "original.json.gz").read_bytes()))
    m, out = mapping("odin"), []
    for iso in sorted(data):
        for year in sorted(data[iso]):
            p = data[iso][year]
            cats = {c["categoryId"]: c["category1"] for c in p.get("categories") or []}
            src = collections.defaultdict(list)
            for c in p.get("categoryInputSource") or []:
                if c.get("cisurl"):
                    src[c["inputId"]].append(c["cisurl"].strip())
            inputs = collections.defaultdict(list)
            for i in p.get("input") or []:
                inputs[i["categoryId"]].append(i)
            for rep in p.get("dataReports") or []:
                name = cats.get(rep["categoryId"], "")
                vals = [rep.get(f"criteria{n}Val") for n in range(1, 11)]
                # -1 is ODIN's "not scored" (connectivity coverage in 2024), not a score.
                status = "; ".join(f"{k} {'not scored' if v < 0 else f'{v:g}'}"
                                   for k, v in zip(ODIN_CRITERIA, vals) if v is not None)
                found = [i for i in inputs[rep["categoryId"]] if not i.get("dataNotAvailable")]
                years = [int(y) for i in found for y in re.findall(r"\b(?:19|20)\d{2}\b", i.get("yearsAvailable") or "")]
                docs = list(dict.fromkeys(u for i in found for u in src[i["inputId"]] if u.startswith("http")))
                st, fit = studies_for(m, [name.lower()])
                out.append({
                    "source": "odin", "edition": edition, "survey_year": year, "iso3": iso,
                    "item": name.lower(), "question": f"{name}: what the statistics office publishes, and how openly",
                    "status": status,
                    "name": "; ".join(dict.fromkeys((i.get("indicatorName") or "").strip() for i in found)),
                    "year": str(max(years)) if years else "", "url": "", "documents": " ".join(docs),
                    "basis": "publisher-assessed", "studies": st, "fit": fit})
    return out


ADAPTERS = {"aftech": adapt_aftech, "gtmi": adapt_gtmi, "unctad": adapt_unctad, "odin": adapt_odin,
            "itu": adapt_itu}


# --- fetch and claims ------------------------------------------------------------------------

def cmd_fetch(sid: str) -> int:
    s = source(sid)
    urls = [] if sid in FETCHERS else s["download_url"].split()
    got = FETCHERS[sid](sid) if sid in FETCHERS else []
    for u in urls:
        r = requests.get(u, headers={"User-Agent": ss.UA}, timeout=120)
        r.raise_for_status()
        name = "original.xlsx" if len(urls) == 1 else up.urlsplit(u).path.rsplit("/", 1)[-1]
        got.append((name, r.content))
    digest = hashlib.sha256(b"".join(c for _, c in got)).hexdigest()
    for e in reversed(editions(sid)):
        if (e / "sha256").exists() and (e / "sha256").read_text().strip() == digest:
            print(f"{sid}: unchanged since {e.name}; nothing written")
            return 0
        break
    today = dt.date.today().isoformat()
    d = BASE / sid / today
    d.mkdir(parents=True, exist_ok=True)
    for name, content in got:
        (d / name).write_bytes(content)
    (d / "sha256").write_text(digest + "\n")
    # The register's `release` is the publisher's date; a server's Last-Modified is when the file
    # was copied (GTMI's Dec 2025 file read 2026-10-19), so it is never used. Without a release,
    # the fetch date: late, never early.
    release = s["release"] or today
    (d / "release").write_text(release + "\n")
    print(f"{sid}: edition {today}, release {release}, {sum(len(c) for _, c in got):,} bytes")
    return 0


def cmd_claims(sid: str) -> int:
    e = editions(sid)[-1]
    release = (e / "release").read_text().strip()
    out = ADAPTERS[sid](e, e.name, release)
    write_csv(e / "claims.csv", COLUMNS, out)
    print(f"{sid} {e.name}: {len(out)} claims, {sum(1 for c in out if c['studies'])} mapped to a study")
    every = []
    for s in rows(SOURCES):
        eds = editions(s["id"])
        if eds and (eds[-1] / "claims.csv").exists():
            every += rows(eds[-1] / "claims.csv")
    write_csv(BASE / "claims.csv", COLUMNS, every)
    return 0


# --- staging ---------------------------------------------------------------------------------

DATED_PATH = re.compile(r"/((?:19|20)\d{2})[/-](0[1-9]|1[0-2])(?:[/-]|$)")


def registers() -> set[str]:
    return {r["id"] for r in rows(SOURCES) if r["shape"] == "register"}


def candidates(claims: list[dict]) -> dict[str, dict]:
    """url -> {title, year, places, publisher}; one per URL, places merged."""
    out, named = {}, registers()
    data_only = {r["id"] for r in rows(SOURCES) if r["shape"] == "index"}
    for c in claims:
        if c["source"] in data_only:
            continue
        for u in c["documents"].split():
            if not u.lower().startswith("http"):
                u = "https://" + u
            u = u.split("#")[0]  # a text fragment is a reader's highlight, not the document
            if up.urlsplit(u).path.strip("/") == "":
                continue  # a bare host is a home page, not a document
            k = out.setdefault(u, {"title": c["name"] if c["source"] in named else "",
                                   "year": c["year"], "places": [], "item": c["item"], "name": c["name"]})
            if c["iso3"] and c["iso3"] not in k["places"]:
                k["places"].append(c["iso3"])
    return out


def held_by_title() -> set[tuple[str, str]]:
    out = set()
    for r in rows(CATALOGUE):
        t = fold(r["title"])
        for p in r["places"].replace(";", " ").split():
            out.add((t, p))
    return out


# `status-stage.fetch` returns no date, so its extractor is wrapped to read the document's own:
# a PDF's creation date, an HTML page's published date. Per thread, as the fetches run in a pool.
_dates = threading.local()
_extract = ss.extract


def _extract_dated(resp, url):
    out = _extract(resp, url)
    _dates.value = own_date(resp)
    return out


ss.extract = _extract_dated


def own_date(resp) -> str:
    try:
        if resp.content[:5] == b"%PDF-":
            import pymupdf  # noqa: PLC0415
            d = (pymupdf.open(stream=resp.content, filetype="pdf").metadata or {}).get("creationDate", "")
            m = re.match(r"D:((?:19|20)\d{2})(\d{2})?", d or "")
            return (f"{m[1]}-{m[2]}" if m[2] else m[1]) if m else ""
        import trafilatura  # noqa: PLC0415
        meta = trafilatura.extract_metadata(resp.text)
        return (meta.date or "")[:7] if meta else ""
    except Exception:  # noqa: BLE001
        return ""


def published_for(u: str, own: str, year: str, sid: str) -> tuple[str, str]:
    """(YYYY[-MM], how it was read), or ("", "") when nothing dates the document. A register's
    year is the instrument's own, so it comes first: an upload path or a PDF's metadata dated
    Ghana's Electronic Transactions Act 2008 to 2026 (UNCTAD, 2026-11-10). A survey's year is
    the system's, never a page's (GTMI: a treasury's founding year dated its 2025 newsletter 1990)."""
    if sid in registers() and re.fullmatch(r"(19|20)\d{2}", year or ""):
        return year, "source"
    m = DATED_PATH.search(up.unquote(u))
    if m:
        return f"{m[1]}-{m[2]}", "path"
    if own and 1990 <= int(own[:4]) <= dt.date.today().year:
        return own, "metadata"
    return "", ""


_mj = importlib.util.spec_from_file_location("mojibake", HERE / "lint-mojibake.py")
mojibake = importlib.util.module_from_spec(_mj)
_mj.loader.exec_module(mojibake)

# A directory index or a list of publications is where a document was, not a document.
LISTING = re.compile(r"(?i)^(index of\b|publications?$|documents?$|downloads?$|resources$|view$|"
                     r"navigation menu|about\b|contact|terms|termos|conditions|mentions l|"
                     r"accueil|home$|welcome|bienvenue|knowledge repository|policy documents$|"
                     r"legislation (&|and) acts$|اتصل بنا)")
# What a PDF's metadata or a server says when nobody titled the file (GTMI, 2026-11-10: a
# third of the first run's titles were file names, "Microsoft Word - …" or "view").
JUNK = re.compile(r"(?i)^(microsoft (word|powerpoint) - |powerpoint presentation$|untitled|"
                  r"view$|document$)|\.(pdf|docx?|pptx?)$|^[\w.\[\]-]+$")


# The first lines of a government PDF are its letterhead, not its title.
LETTERHEAD = re.compile(r"(?i)^(the )?(republic|r[ée]publique|rep[úu]blica|kingdom|royaume|"
                        r"federal|state of|government|gouvernement|minist\w*|office|depart\w*|"
                        r"united republic|people's)\b")
# A server's error page answered 200 (six on the GTMI run of 2026-11-10).
ERROR_PAGE = re.compile(r"(?i)apologi[sz]e for the inconvenience|page not found|^404\b|"
                        r"access denied|^forbidden|just a moment|attention required")
GENERIC = re.compile(r"(?i)^(powerpoint presentation|untitled\w*|view|document|slide \d+)$")


def readable(t: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(mojibake.repair(t or "")[0])).strip()


def best_title(page_title: str, body: str, url: str, name: str) -> str:
    """The page's own title where it is one; else the file name made words, the body's first
    heading-like line, or the name the database gave, in that order."""
    t = readable(page_title)
    if t and not JUNK.search(t) and len(t.split()) >= 2:
        return t
    t = "" if GENERIC.match(t) else t
    stem = re.sub(r"(?i)^microsoft (word|powerpoint) - |\.(pdf|docx?|pptx?)$", "", t or
                  up.unquote(up.urlsplit(url).path.rsplit("/", 1)[-1]))
    stem = re.sub(r"[_\-+]+", " ", re.sub(r"\[\d+\]|\b\d{6,}\b", "", stem)).strip()
    stem = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", stem)  # NigeriaDataProtection -> words
    if len(re.findall(r"[A-Za-z]{3,}", stem)) >= 3:
        return stem
    for line in body[:3000].splitlines():
        line = readable(line.strip("#*> "))
        if 3 <= len(line.split()) <= 25 and re.search(r"[A-Za-z]{4,}", line) \
                and not LETTERHEAD.match(line):
            return line
    return readable(name) or stem or "Untitled document"


def yq(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_staged(folder, url, fetched, body, title, published, how, places, batch_tag, publisher=""):
    date, precision = ss.dated(published)
    # Wayback keeps the port it crawled (`host:80/`), which the URL line's check reads as
    # another address.
    fetched = re.sub(r"(?<=[a-z]):(80|443)/", "/", fetched)
    path = folder / f"{date}-{ss.slugify(title) or 'document'}.md"
    n = 2
    while path.exists():
        path = folder / f"{date}-{ss.slugify(title) or 'document'}-{n}.md"
        n += 1
    fm = ["---", "type: source", f"title: {yq(title)}", f"url: {url}",
          f"publisher: {yq(publisher)}", f"published: {date}", f"date_precision: {precision}",
          f"date_source: {'source' if how == 'source' and precision == 'day' else 'proxy'}",
          f"places: [{', '.join(places)}]", "topics: []", "entities: []",
          "body_completeness: full", f"sweep_batch: {batch_tag}", "---", "",
          f"# {title}", f"URL: {fetched}", "", body, ""]
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(fm))
    return path


def database_record(sid: str, e: pathlib.Path, claims: list[dict]) -> tuple[str, str]:
    """The edition as one readable body: what a claim with no primary cites."""
    s = source(sid)
    note = ""
    if s["shape"] == "index":
        # An index's rounds are each a full assessment; the record is the latest, which is
        # what a claim without a primary cites. Earlier rounds stay in claims.csv.
        latest = max(c["survey_year"] for c in claims)
        claims = [c for c in claims if c["survey_year"] == latest]
        note = f" The {latest} round only."
    lines = [f"{s['title']} — {s['publisher']}", "",
             f"Rendered from {s['download_url']}, fetched {e.name}. African countries only.{note}", ""]
    by = collections.defaultdict(list)
    for c in claims:
        by[c["iso3"] or "unplaced"].append(c)
    for iso in sorted(by):
        lines += [f"## {iso}", ""]
        for c in by[iso]:
            bits = [c["survey_year"], c["item"], c["question"], c["status"], c["name"], c["year"],
                    c["url"], c["documents"], c["basis"]]
            lines.append("- " + " | ".join(b for b in bits if b))
        lines.append("")
    return s["title"], "\n".join(lines)


TRANSIENT = re.compile(r"^(ConnectionError|ConnectTimeout|ReadTimeout|SSLError|HTTP 5\d\d|HTTP 429)")


def cmd_stage(sid: str, limit: int, retry: bool = False) -> int:
    s, e = source(sid), editions(sid)[-1]
    claims = rows(e / "claims.csv")
    log_path = e / "staging.csv"
    log = {r["url"]: r for r in rows(log_path)} if log_path.exists() else {}
    held = ss.lookup("raw-url-index.csv")
    rejected = ss.lookup("rejected-urls.csv")
    titles = held_by_title()
    # A link another source has staged is not in OSINT's index until it is ingested.
    elsewhere = {}
    for other in rows(SOURCES):
        eds = editions(other["id"])
        if other["id"] != sid and eds and (eds[-1] / "staging.csv").exists():
            for r in rows(eds[-1] / "staging.csv"):
                if r["outcome"] == "staged":
                    elsewhere[ss.norm(r["url"])] = f"staged by {other['id']}, batch {r['batch']}"
    today = dt.date.today().isoformat()
    todo = []
    for u, c in candidates(claims).items():
        if u in log and not (retry and log[u]["outcome"] == "unfetchable"
                             and (TRANSIENT.search(log[u]["note"]) or "drive.google" in u)):
            continue
        hit = ss.screen(u, held, rejected)
        if not hit and c["title"] and any((fold(c["title"]), p) in titles for p in c["places"]):
            hit = ("held", "title and country in the catalogue")
        if not hit and ss.norm(u) in elsewhere:
            hit = ("staged-elsewhere", elsewhere[ss.norm(u)])
        if hit:
            log[u] = {"url": u, "places": " ".join(c["places"]), "outcome": hit[0], "note": hit[1], "batch": ""}
        else:
            todo.append((u, c))
    todo = todo[:limit] if limit else todo

    def get(item):
        # A malformed PDF raises from inside the extractor, not as a request error; on the
        # first run (2026-11-10) one such file ended the whole run with nothing logged.
        u, c = item
        # A Drive viewer page is a JavaScript shell; its download form is the file itself. The
        # body is filed under the link the source gave, which is the one a reader can open.
        m = re.search(r"drive\.google\.com/file/d/([\w-]+)", u)
        _dates.value = ""
        try:
            got = ss.fetch(f"https://drive.google.com/uc?export=download&id={m[1]}" if m else u)
        except Exception as e:  # noqa: BLE001
            return item, (None, f"extraction failed: {type(e).__name__}", "", "", "")
        if m and got[0] is not None:
            got = (got[0], u, got[2], got[3])
        return item, got + (_dates.value,)

    def save():
        write_csv(log_path, ["url", "places", "outcome", "note", "batch"],
                  sorted(log.values(), key=lambda r: r["url"]))

    nums = [int(m[1]) for p in QUEUE.glob(f"dataset-external-{sid}-*")
            if (m := re.search(r"-(\d+)$", p.name))]
    done = [int(r["batch"]) for r in log.values() if r["batch"].isdigit()]
    batch_no = max(nums + done + [0]) + 1
    folder, in_batch, staged = None, 0, 0

    # The database itself goes first, once per edition.
    db_url = s["page_url"]
    if db_url not in log and not ss.screen(db_url, held, rejected):
        title, body = database_record(sid, e, claims)
        folder = QUEUE / f"dataset-external-{sid}-{batch_no:02d}"
        folder.mkdir(parents=True, exist_ok=False)
        places = sorted({c["iso3"] for c in claims if c["iso3"]})
        write_staged(folder, db_url, db_url, body, f"{title} ({e.name})", (e / "release").read_text().strip(),
                     "source", places, f"dataset-external-{sid}-{today}", s["publisher"])
        log[db_url] = {"url": db_url, "places": "", "outcome": "staged", "note": "the database record",
                       "batch": str(batch_no)}
        in_batch, staged = 1, 1

    with ThreadPoolExecutor(8) as pool:
        for (u, c), (body, fetched, kind, page_title, own) in pool.map(get, todo):
            places = " ".join(c["places"])
            if body is None:
                log[u] = {"url": u, "places": places, "outcome": "unfetchable", "note": fetched, "batch": ""}
                continue
            if len(body) < ss.THIN:
                log[u] = {"url": u, "places": places, "outcome": "thin", "note": f"{len(body)} chars", "batch": ""}
                continue
            published, how = published_for(u, own, c["year"], sid)
            if not published:
                log[u] = {"url": u, "places": places, "outcome": "undated", "note": "", "batch": ""}
                continue
            title = c["title"] or best_title(page_title, body, u, c["name"])
            if LISTING.match(title):
                log[u] = {"url": u, "places": places, "outcome": "listing", "note": title, "batch": ""}
                continue
            if ERROR_PAGE.search(readable(page_title)):
                log[u] = {"url": u, "places": places, "outcome": "error-page", "note": readable(page_title)[:80], "batch": ""}
                continue
            if folder is None or in_batch >= BATCH:
                if folder is not None:
                    batch_no += 1
                folder = QUEUE / f"dataset-external-{sid}-{batch_no:02d}"
                folder.mkdir(parents=True, exist_ok=False)
                in_batch = 0
            write_staged(folder, u, fetched, body, title, published, how, c["places"],
                         f"dataset-external-{sid}-{today}")
            log[u] = {"url": u, "places": places, "outcome": "staged", "note": how, "batch": str(batch_no)}
            in_batch += 1
            staged += 1
            save()
    save()
    tally = collections.Counter(r["outcome"] for r in log.values())
    print(f"{sid}: staged {staged} this run; log {dict(tally)}")
    return 0


def cmd_ready(sid: str) -> int:
    for f in sorted(QUEUE.glob(f"dataset-external-{sid}-*")):
        if f.is_dir() and any(f.glob("*.md")) and not (f / "READY").exists():
            (f / "READY").touch()
            print(f"READY {f.name}")
    return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["fetch", "claims", "stage", "ready"])
    ap.add_argument("source")
    ap.add_argument("--limit", type=int, default=0, help="stage: fetch at most this many links")
    ap.add_argument("--retry", action="store_true",
                    help="stage: fetch again the links a transient failure left unfetchable")
    a = ap.parse_args()
    if a.source not in ADAPTERS:
        sys.exit(f"no adapter for {a.source}")
    return {"fetch": lambda: cmd_fetch(a.source), "claims": lambda: cmd_claims(a.source),
            "stage": lambda: cmd_stage(a.source, a.limit, a.retry), "ready": lambda: cmd_ready(a.source)}[a.command]()


if __name__ == "__main__":
    sys.exit(main())
