#!/usr/bin/env python3
r"""climate-fund-stage.py — stage the climate funds' African project pages for OSINT (notes-for-corpus 84).

    python scripts/climate-fund-stage.py gef            # enumerate, fetch, test, screen, stage
    python scripts/climate-fund-stage.py gef --ready    # after lint-staged-queue passes: READY

Funds: `gef` (GEF Trust Fund, LDCF, SCCF and CBIT are one database), `gcf`, `af` (Adaptation
Fund), `crews`, `cif`, `soff`, `eo` (GMES & Africa, ClimSA, Digital Earth Africa).
CREWS, SOFF and the EO programmes pass the test by mandate. The Adaptation Fund stages the
proposal PDF and asks for ten strong mentions in it unless the title or sector passes; CIF's
card is short, so its length floor is 100 characters.

**Africa**: a project naming an African country, or one whose region is Africa. A regional or
global project is kept for the African countries it names, and `places` lists those alone.

**The component test** is `component()`: information systems, early warning, hydromet, MRV
and transparency, observation and earth observation. A strong term passes on one mention; an
incidental one (`meteorolog`, `database`, `satellite`) needs the title or three mentions,
because the first GCF run staged a renewables fund for citing the met office once. A national
communication alone does not count: on the first GEF run it was 95 of 194 matches, CBD and
1990s UNFCCC enabling activities; a combined NC/BTR still passes on the BTR. Ingest
decides what a staged project is worth. Topics are left blank for ingest, as with the
data-centre batches (notes-for-corpus 50).

**Nothing goes in twice**: the screen is `status-stage.py`'s (raw-url-index, rejected-urls),
plus a match on the fund's project identifier in any held URL — the GCF page has two URL
shapes and raw/ holds one of them.

**Date**: the project's approval date where the record gives one, else the earliest date in
its timeline, `date_source: proxy` — a database record has no publication date of its own.

Each fund's pages are cached under `prep/climate-funds/{fund}/`; every candidate's outcome is
written to `logs/climate-fund-audit.csv` (one block of rows per fund, rewritten each run). The
batch is `new-queue/dataset-climate-funds-{fund}/`, backfill lane, no `READY` until `--ready`.
"""
from __future__ import annotations

import argparse, csv, datetime as dt, html, importlib.util, io, json, os, pathlib, re, sys, time
from concurrent.futures import ThreadPoolExecutor

import requests

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import status_lib  # noqa: E402

_spec = importlib.util.spec_from_file_location("status_stage", HERE / "status-stage.py")
ss = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ss)

UA = {"User-Agent": ss.UA}
CACHE = ROOT / "prep" / "climate-funds"
AUDIT = ROOT / "logs" / "climate-fund-audit.csv"
QUEUE = pathlib.Path(status_lib.EXCHANGE) / "new-queue"

STRONG = re.compile(
    r"early[- ]warning|hydro[- ]?met|climate (?:information|services?)|"
    r"weather (?:forecast|service|station|radar|observ|information)|"
    r"MRV|(?:measurement|monitoring),? reporting,? and verification|"
    r"transparency framework|CBIT|BTRs?|biennial (?:update|transparency) report|"
    r"information (?:system|management system)|"
    r"observ(?:ation|ing) (?:system|network|station)|earth observation|remote sensing",
    re.I,
)
# Incidental on their own: a resilience project cites the met agency's data in passing.
WEAK = re.compile(
    r"meteorolog|hydrolog|weather|climate data|satellite|GIS|geospatial|forecasting|transparency|"
    r"monitoring (?:system|network|platform)|decision[- ]support (?:system|tool)|"
    r"data (?:management|platform|infrastructure|system)|database",
    re.I,
)


def component(title: str, body: str) -> str | None:
    """The matched term, or None: a strong term anywhere, a weak one in the title, or three
    weak hits in the body."""
    m = STRONG.search(title) or STRONG.search(body) or WEAK.search(title)
    if m:
        return m.group(0)
    weak = [x.group(0) for x in WEAK.finditer(body)]
    return weak[0] + f" (x{len(weak)})" if len(weak) >= 3 else None


# GEF and GCF country names that differ from OSINT's lookups/countries.csv.
ALIASES = {
    "congo dr": "COD", "democratic republic of the congo": "COD", "congo": "COG",
    "republic of congo": "COG", "cote d'ivoire": "CIV", "côte d'ivoire": "CIV",
    "tanzania": "TZA", "united republic of tanzania": "TZA", "gambia": "GMB", "the gambia": "GMB",
    "cabo verde": "CPV", "cape verde": "CPV", "eswatini": "SWZ", "swaziland": "SWZ",
    "sao tome and principe": "STP", "são tomé and príncipe": "STP", "egypt": "EGY",
    "libya": "LBY", "africa": "XAF", "guinea-bissau": "GNB", "guinea bissau": "GNB",
    "democratic republic of congo": "COD", "drc": "COD", "dr congo": "COD",
}
# Names that contain an African one and are not African.
NOT_AFRICA = ("papua new guinea", "png", "new guinea")


def iso_map() -> dict:
    m = {}
    with open(os.path.join(ss.LOOKUPS, "countries.csv"), encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["iso-3"].startswith("X") and r["iso-3"] != "XAF":
                continue
            m[r["country-name"].strip().lower()] = r["iso-3"]
    m.update(ALIASES)
    return m


ISO = iso_map()


def places_of(names) -> list[str]:
    out = []
    for n in names:
        k = html.unescape(n).strip().lower().replace("�", "o")
        if k in ISO and ISO[k] not in out:
            out.append(ISO[k])
    return out


def get(url: str, cache: pathlib.Path | None = None, tries: int = 3):
    if cache and cache.exists():
        return cache.read_bytes()
    for _ in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=60)
            if r.ok:
                if cache:
                    cache.parent.mkdir(parents=True, exist_ok=True)
                    cache.write_bytes(r.content)
                return r.content
            if r.status_code == 404:
                return None
        except requests.RequestException:
            pass
        time.sleep(3)
    return None


class Page:
    """Enough of a `requests.Response` for `status-stage.extract`."""
    def __init__(self, content: bytes):
        self.content = content
        self.text = content.decode("utf-8", "replace")
        self.headers = {"content-type": "application/pdf" if content[:5] == b"%PDF-" else "text/html"}


def text(h: str) -> str:
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def dmy(s: str) -> str | None:
    m = re.match(r"(\d{1,2}) ([A-Za-z]{3})[a-z]* (\d{4})", s)
    if m and m.group(2).lower() in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return None


# ---------------------------------------------------------------- enumerators
# Each yields dicts: url, ident, title, publisher, places, date (or None), and optionally
# `html` — the page bytes already fetched — so the generic loop does not fetch twice.

def gef(cache: pathlib.Path):
    rows = []
    def listing(n):
        b = get(f"https://www.thegef.org/projects-operations/database?page={n}",
                cache / "list" / f"{n}.html")
        t = (b or b"").decode("utf-8", "replace")
        out = []
        for tr in re.findall(r"<tr>(.*?)</tr>", t[t.find("<tbody"):], re.S):
            tds = [text(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            node = re.search(r"/projects-operations/projects/(\d+)", tr)
            if node and len(tds) == 9:
                out.append((node.group(1), tds))
        return out
    first = (get("https://www.thegef.org/projects-operations/database", cache / "list" / "0.html")
             or b"").decode("utf-8", "replace")
    last = max(int(x) for x in re.findall(r"[?&]page=(\d+)", first))
    with ThreadPoolExecutor(4) as ex:
        for page in ex.map(listing, range(last + 1)):
            rows.extend(page)
    cands = []
    for node, tds in rows:
        names = [x.strip() for x in tds[2].split(",")]
        pl = places_of(names)
        if pl or {"Regional", "Global"} & set(names):
            cands.append((node, tds, pl))
    def page(c):
        node, tds, pl = c
        url = f"https://www.thegef.org/projects-operations/projects/{node}"
        b = get(url, cache / "pages" / f"{node}.html")
        if b is None:
            return None
        t = text(b.decode("utf-8", "replace"))
        region = re.search(r"\bRegion (.+?) Executing Agencies", t)
        if not pl and not (region and "Africa" in region.group(1)):
            return None
        if not pl:
            pl = ["XAF"]
        tl = t[t.find(" Timeline ") + 10:] if " Timeline " in t else ""
        dates = [(lab.strip(), dmy(d)) for lab, d in
                 re.findall(r"([A-Z][A-Za-z /]+?) (\d{1,2} [A-Z][a-z]{2} \d{4})", tl)]
        dates = [(lab, d) for lab, d in dates if d]
        appr = [d for lab, d in dates if re.search(r"approv|endorse", lab, re.I)
                and not re.search(r"concept", lab, re.I)]
        date = min(appr) if appr else (min(d for _, d in dates) if dates else None)
        fund = re.search(r"Funding Source (.+?) (?:Project Documents|Financials)", t)
        return {"url": url, "ident": node, "title": tds[0], "places": pl, "date": date,
                "publisher": "Global Environment Facility", "html": b,
                "extra": fund.group(1) if fund else ""}
    with ThreadPoolExecutor(5) as ex:
        for r in ex.map(page, cands):
            if r:
                yield r


def gcf(cache: pathlib.Path):
    b = get("https://api.gcfund.org/v1/projects", cache / "projects.json")
    for p in json.loads(b):
        cs = [c for c in p["Countries"] if c.get("Region") == "Africa"]
        if not cs:
            continue
        ref = p["ApprovedRef"].lower()
        url = f"https://www.greenclimate.fund/portfolio/projects/{ref}"
        pl = places_of(c["CountryName"] for c in cs) or ["XAF"]
        yield {"url": url, "ident": ref, "title": p["ProjectName"], "places": pl,
               "date": (p.get("ApprovalDate") or "")[:10] or None,
               "publisher": "Green Climate Fund"}


AFRICA_NAMES = None


def places_in(s: str) -> list[str]:
    """African countries named anywhere in a string, longest names first so `Guinea-Bissau`
    is not also read as `Guinea`, and `Niger` is not read out of `Nigeria`."""
    global AFRICA_NAMES
    if AFRICA_NAMES is None:
        AFRICA_NAMES = sorted((k for k in ISO if k != "africa"), key=len, reverse=True)
    low, out = " " + s.lower().replace("-", " ").replace("_", " ") + " ", []
    for k in NOT_AFRICA:
        low = re.sub(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", " ", low)
    for k in AFRICA_NAMES:
        pat = r"(?<![a-z])" + re.escape(k.replace("-", " ")) + r"(?![a-z])"
        if re.search(pat, low):
            if ISO[k] not in out:
                out.append(ISO[k])
            low = re.sub(pat, " ", low)
    return out


def crews(cache: pathlib.Path):
    """Every CREWS project is an early-warning project, so the test is its region alone."""
    regional = {"acmad": "XAF", "central-africa": "XCA", "east-africa": "XEA",
                "greater-horn-of-africa": "XEA", "west-africa": "XWA"}
    b = get("https://crews-initiative.org/landing/projects/", cache / "projects.html") or b""
    urls = sorted(set(re.findall(r'https://crews-initiative\.org/project/[^"/]+/', b.decode("utf-8", "replace"))))
    for url in urls:
        slug = url.rstrip("/").rsplit("/", 1)[1]
        pg = get(url, cache / "pages" / f"{slug}.html")
        if not pg:
            continue
        t = text(pg.decode("utf-8", "replace"))
        title = t.split(" CREWS ")[0].rstrip(" -–�|")
        pl = places_in(slug.replace("-", " ")) or next(
            (v for k, v in regional.items() if slug.startswith(k)), None)
        if isinstance(pl, str):
            pl = [pl]
        if not pl:
            continue
        d = re.search(r"Duration: ([A-Z][a-z]{2})[a-z]* (\d{4})", t)
        date = f"{d.group(2)}-{MONTHS[d.group(1).lower()]:02d}-01" if d and d.group(1).lower() in MONTHS else None
        yield {"url": url, "ident": slug, "title": title, "places": pl, "date": date,
               "precision": "month", "publisher": "CREWS Initiative", "html": pg,
               "component": "CREWS (early warning)"}


def soff(cache: pathlib.Path):
    """SOFF's own documents for African countries: hydromet diagnostics, national contribution
    plans and investment requests — what a SOFF grant is spent on is observation by mandate."""
    docs = []
    for n in range(1, 30):
        b = get(f"https://www.un-soff.org/wp-json/wp/v2/document?per_page=100&page={n}",
                cache / "api" / f"{n}.json", tries=1)
        if not b:
            break
        page = json.loads(b)
        if not page:
            break
        docs.extend(page)
    kind = re.compile(r"\bCHD\b|hydromet diagnostic|\bNCP\b|national contribution plan|"
                      r"investment (?:funding )?request|investment phase|readiness|funding request",
                      re.I)
    for d in docs:
        title = html.unescape(d["title"]["rendered"]).replace("​", "").strip()
        pl = places_in(title)
        if not pl or not kind.search(title):
            continue
        pg = get(d["link"], cache / "pages" / f"{d['id']}.html")
        if not pg:
            continue
        pdf = re.search(r'href="(https://www\.un-soff\.org/wp-content/uploads/[^"]+\.pdf)"',
                        pg.decode("utf-8", "replace"))
        if not pdf:
            continue
        yield {"url": pdf.group(1), "ident": str(d["id"]), "title": title, "places": pl,
               "date": d["date"][:10], "publisher": "Systematic Observations Financing Facility",
               "component": "SOFF (observation)"}


def af(cache: pathlib.Path):
    """The Adaptation Fund's project pages are a metadata card; the document is the proposal.
    Kept: an approved African project whose sector is early warning or whose title passes the
    test. Staged: its fully-developed proposal (or project document) PDF."""
    sm = get("https://www.adaptation-fund.org/af_project-sitemap.xml", cache / "sitemap.xml") or b""
    urls = re.findall(r"<loc>([^<]+)</loc>", sm.decode("utf-8", "replace"))
    def one(url):
        slug = url.rstrip("/").rsplit("/", 1)[1]
        pg = get(url, cache / "pages" / f"{slug}.html")
        if not pg:
            return None
        h = pg.decode("utf-8", "replace")
        t = text(h)
        glance = t[t.find("At A Glance"):]
        where = re.search(r"(?:Country|Region): (.+?) (?:Sector|Implementing Entity):", glance)
        pl = places_in(where.group(1)) if where else []
        status = re.search(r"Status: (.+?)(?: Approval| Project|$)", glance)
        status = status.group(1) if status else ""
        if not pl or re.search(r"not approved|concept|withdrawn|cancel", status, re.I):
            return None
        tt = re.search(r"<title>(.*?)</title>", h, re.S)
        title = html.unescape(tt.group(1)) if tt else slug
        title = re.sub(r"^\(.*?\)\s*|\s*[–—�|-]\s*Adaptation Fund\s*$", "", title).strip()
        sector = re.search(r"Sector: (.+?) Implementing Entity", glance)
        sector = sector.group(1) if sector else ""
        hit = component(title, "") or ("sector: " + sector if "early warning" in sector.lower() else None)
        # Documents sit on the fund's own uploads and on its Azure store (fifspubprd); the
        # proposal is labelled "Project document" or "Fully-developed proposal".
        pdfs = re.findall(r'href="(https://[^"]+\.pdf)"[^>]*>([^<]*)', h)
        doc = next((u for u, lab in pdfs if re.search(r"project document|fully|proposal", lab, re.I)), None)
        appr = re.search(r"Approval Date: (\d{2})/(\d{2})/(\d{4})", glance)
        return {"url": doc or url, "ident": slug, "title": title, "places": pl,
                "date": f"{appr.group(3)}-{appr.group(1)}-{appr.group(2)}" if appr else None,
                "precision": "day", "publisher": "Adaptation Fund", "component": hit or None,
                "min_strong": 10,
                "skip": None if doc else "no proposal PDF"}
    with ThreadPoolExecutor(5) as ex:
        for r in ex.map(one, urls):
            if r:
                yield r


def cif(cache: pathlib.Path):
    """CIF's project pages are a snapshot card: title, country, region, programme, approval
    date. The test runs on the card."""
    # The listing pages are filtered client-side; the sitemap holds every project.
    urls = []
    for n in range(1, 30):
        b = get(f"https://www.cif.org/sitemap.xml?page={n}", cache / "sitemap" / f"{n}.xml", tries=1)
        if not b:
            break
        urls += [u for u in re.findall(r"<loc>https://www\.cif\.org(/projects/[^<?#]+)</loc>",
                                       b.decode("utf-8", "replace")) if u not in urls]
    def one(path):
        slug = path.rsplit("/", 1)[1]
        url = "https://www.cif.org" + path
        pg = get(url, cache / "pages" / f"{slug}.html")
        if not pg:
            return None
        t = text(pg.decode("utf-8", "replace"))
        t = t[t.find("GENERAL INFORMATION"):] if "GENERAL INFORMATION" in t else ""
        region = re.search(r" Region (.+?) Program ", t)
        country = re.search(r" Country (.+?) Region ", t)
        pl = places_in(country.group(1)) if country else []
        # "Middle East & North Africa" names Africa and holds Yemen: a regional project
        # counts only when its region is Africa itself.
        if not pl and not (region and re.fullmatch(r"(?:Sub-Saharan )?Africa(?: Region)?", region.group(1).strip())):
            return None
        title = re.search(r" Title (.+?) Project id ", t)
        appr = re.search(r"approval date (\d{2})/(\d{2})/(\d{4})", t)
        return {"url": url, "ident": slug, "title": title.group(1) if title else slug,
                "places": pl or ["XAF"], "html": pg, "min_len": 100,
                "date": f"{appr.group(3)}-{appr.group(1)}-{appr.group(2)}" if appr else None,
                "publisher": "Climate Investment Funds"}
    with ThreadPoolExecutor(5) as ex:
        for r in ex.map(one, urls):
            if r:
                yield r


def eo(cache: pathlib.Path):
    """The regional earth-observation programmes are programmes, not portfolios: no project
    database to enumerate. Staged: their dated funding documents, found by hand on 2026-11-05.
    Undated reference pages (ClimSA's EU project page, the African Space Agency's GMES page)
    are not staged, the data-centre rule (`dataset-stage.py`). Digital Earth Africa's 2023
    report is already in raw/."""
    lst = [
        ("https://digitalearthafrica.org/wp-content/uploads/Digital-Earth-Africa-2020-Annual-Report_FINAL.pdf",
         "Digital Earth Africa Annual Report 2020", "2021-01-01", "year", "Digital Earth Africa"),
        ("https://digitalearthafrica.org/wp-content/uploads/DE-Africa-Annual-report-2021.pdf",
         "Digital Earth Africa Annual Report 2021", "2022-01-01", "year", "Digital Earth Africa"),
        ("https://digitalearthafrica.org/wp-content/uploads/DEAfrica_Annual-Report_2022.pdf",
         "Digital Earth Africa Annual Report 2022", "2023-01-01", "year", "Digital Earth Africa"),
        ("https://digitalearthafrica.org/wp-content/uploads/DE-Annual-Report-2024-English.pdf",
         "Digital Earth Africa Annual Report 2024", "2025-05-30", "day", "Digital Earth Africa"),
        ("https://digitalearthafrica.org/wp-content/uploads/DE-Africa-Annual-Report-2025-English-.pdf",
         "Digital Earth Africa Annual Report 2025", "2026-05-06", "day", "Digital Earth Africa"),
        ("https://www.eu4oceanobs.eu/gmes-and-africa/", "GMES and Africa programme",
         "2021-03-11", "day", "EU4OceanObs"),
        ("https://www.eu4oceanobs.eu/gmes-africa-phase-2-kick-off/",
         "GMES & Africa: increasing use of EO data for sustainable development in Africa",
         "2022-03-23", "day", "EU4OceanObs"),
        ("https://www.cicos.int/non-classe/actualites-projet-gmes-africa/",
         "Actualités Projet GMES & Africa", "2022-03-18", "day", "CICOS"),
    ]
    for url, title, date, prec, pub in lst:
        yield {"url": url, "ident": ss.slugify(title), "title": title, "places": ["XAF"],
               "date": date, "precision": prec, "publisher": pub,
               "component": "earth-observation programme"}


FUNDS = {"gef": gef, "gcf": gcf, "crews": crews, "soff": soff, "af": af, "cif": cif, "eo": eo}


# ---------------------------------------------------------------- the generic loop

def held_idents(held: dict, fund: str) -> set[str]:
    """Project identifiers already in raw/, read off the held URLs."""
    pat = {"gef": r"thegef\.org/projects-operations/projects/(\d+)",
           "gcf": r"greenclimate\.fund/(?:portfolio/projects|project)/([a-z]+\d+)"}.get(fund)
    if not pat:
        return set()
    return {m.group(1).lower() for u in held for m in [re.search(pat, u, re.I)] if m}


def write(folder: pathlib.Path, c: dict, body: str, today: str, fund: str) -> pathlib.Path:
    date = c["date"] or today
    title = html.unescape(c["title"]).replace("�", "-")
    name = f"{date}-{ss.slugify(fund + '-' + title)}.md"
    path = folder / name
    n = 2
    while path.exists():
        path = folder / f"{date}-{ss.slugify(fund + '-' + title)}-{n}.md"
        n += 1
    fm = ["---", "type: source", f"title: {ss.yq(title)}", f"url: {c['url']}",
          f"publisher: {ss.yq(c['publisher'])}", f"published: {date}",
          f"date_precision: {c.get('precision', 'day') if c['date'] else 'day'}",
          "date_source: proxy",
          f"places: [{', '.join(c['places'])}]", "topics: []", "entities: []",
          "body_completeness: full", f"sweep_batch: dataset-climate-funds-{fund}-{today}",
          "---", "", f"# {title}", f"URL: {c['url']}", "", body.strip(), ""]
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(fm))
    return path


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("fund", choices=sorted(FUNDS))
    ap.add_argument("--ready", action="store_true")
    a = ap.parse_args()
    folder = QUEUE / f"dataset-climate-funds-{a.fund}"
    if a.ready:
        if not folder.exists() or not any(folder.iterdir()):
            print(f"{folder} is empty; no READY written", file=sys.stderr)
            return 1
        (folder / "READY").touch()
        print(f"READY written in {folder}")
        return 0
    if folder.exists() and any(folder.iterdir()):
        print(f"{folder} already holds files; not restaging over them", file=sys.stderr)
        return 1
    folder.mkdir(parents=True, exist_ok=True)
    cache = CACHE / a.fund
    held, rejected = ss.lookup("raw-url-index.csv"), ss.lookup("rejected-urls.csv")
    have = held_idents(held, a.fund)
    today = dt.date.today().isoformat()
    audit, staged = [], 0
    for c in FUNDS[a.fund](cache):
        row = {"fund": a.fund, "ident": c["ident"], "url": c["url"], "places": ";".join(c["places"])}
        hit = ss.screen(c["url"], held, rejected)
        if not hit and c["ident"].lower() in have:
            hit = ("held", "project id held under another URL")
        if hit:
            audit.append({**row, "outcome": hit[0], "note": hit[1]})
            continue
        if c.get("skip"):
            audit.append({**row, "outcome": "no-document", "note": c["skip"]})
            continue
        if "component" in c and not c["component"] and not c.get("min_strong"):
            audit.append({**row, "outcome": "no-component", "note": "title and sector"})
            continue
        ext = ".pdf" if c["url"].lower().endswith(".pdf") else ".html"
        b = c.get("html") or get(c["url"], cache / "docs" / f"{c['ident']}{ext}")
        if not b:
            audit.append({**row, "outcome": "unfetchable", "note": ""})
            continue
        body, kind, page_title = ss.extract(Page(b), c["url"])
        if kind != "html" or a.fund not in ("gef", "gcf"):
            page_title = ""  # a PDF's metadata title is a file name as often as not
        # The page's own title is clean where the listing and the API carry U+FFFD.
        page_title = re.sub(r"^[A-Z]+\d+:\s*|\s*\|\s*(?:Green Climate Fund|GEF)\s*$", "", page_title)
        if page_title and "�" not in page_title:
            c["title"] = page_title
        hit_term = c.get("component")
        if not hit_term and c.get("min_strong"):
            # A long proposal: one passing mention is noise; a component is named often.
            n = len(STRONG.findall(body))
            hit_term = f"{STRONG.search(body).group(0)} (x{n})" if n >= c["min_strong"] else None
        elif not hit_term:
            hit_term = component(c["title"], body)
        if not hit_term:
            audit.append({**row, "outcome": "no-component", "note": ""})
            continue
        if not body or len(body) < c.get("min_len", ss.THIN):
            audit.append({**row, "outcome": "thin", "note": f"{len(body)} chars"})
            continue
        path = write(folder, c, body, today, a.fund)
        staged += 1
        audit.append({**row, "outcome": "staged", "note": f"{path.name}; matched '{hit_term}'"
                      + (f"; {c['extra']}" if c.get("extra") else "")})
    old = []
    if AUDIT.exists():
        with open(AUDIT, encoding="utf-8", newline="") as fh:
            old = [r for r in csv.DictReader(fh) if r["fund"] != a.fund]
    fields = ["fund", "ident", "url", "places", "outcome", "note"]
    with open(AUDIT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(old + audit)
    from collections import Counter
    print(a.fund, dict(Counter(r["outcome"] for r in audit)), f"-> {folder}")
    print("Next: python scripts/lint-staged-queue.py over the folder, then --ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
