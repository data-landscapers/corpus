r"""whos_who_lib.py — resolving a cached tuple to an organisation, and naming the organisation.

`documentation/whos-who.md` §4 and §6. The cache (`build/whos-who/extract.csv`) holds the
organisation **as written**; everything here is derived at build time from it, the
catalogue's tags and the lookups, so a slug merge or a hand row takes effect without the
model. Two readers: `whos-who-orgs.py` (the sidecar, stage 2) and the positions build.

**A tuple resolves only to one of its own source's tags**, with one exception: an
organisation written as a bare country (*President of Nigeria*, organisation *Nigeria*)
resolves to that country's government slug, found among the source's tags first and
otherwise the most-tagged one naming that country.

**When no tag matches, any tagged slug in the catalogue may, by name or stem only** —
source tags are sparse, and about 30% of tuples name a body their own source left
untagged. The fallback is narrower than the tag match: no initialisms, and the slug's
place must be one of the source's places, or it must be the only slug of that name
anywhere. A government slug must always share the source's place, because *Ministry of
Finance* is fifty bodies. Anything else that matches nothing, or more than one slug
equally well, is dropped and counted — never guessed.
"""
from __future__ import annotations

import collections
import csv
import importlib.util
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "build" / "whos-who" / "extract.csv"
CATALOGUE = ROOT / "outputs" / "catalogue" / "raw-catalogue.json"
NAMES = ROOT / "lookups" / "entity-names.csv"
ORGS = ROOT / "lookups" / "organisations.csv"
LINEAGE = ROOT / "lookups" / "org-lineage.csv"
GOV_STEMS = ROOT / "lookups" / "whos-who-gov-stems.csv"
COUNTRIES = ROOT / "lookups" / "countries.csv"
ORG_COLS = ["slug", "canonical_slug", "name", "place", "kind", "basis"]
LINEAGE_COLS = ["slug", "successor_slug", "year", "basis"]

_spec = importlib.util.spec_from_file_location("entity_variants", ROOT / "scripts" / "entity-variants.py")
EV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(EV)
PHRASES, CTOK, ISO_OF = EV.country_tokens(str(ROOT))
# Spellings `entity-variants.py` does not need and this does: a government slug that names
# no country is placed by its tags' dominant place, which for `china-ministry-of-foreign-
# affairs` is wherever China's ministry was last in the news. Subnational names place a
# state or province body in its country. Kept here, not in `entity-variants.py`, whose
# groups would move.
EXTRA = {"rca": "CAF", "car": "CAF", "centrafrique": "CAF", "comores": "COM", "mocambique": "MOZ",
         "bf": "BFA", "faso": "BFA", "mg": "MDG", "tunisien": "TUN", "tunisienne": "TUN",
         "zanzibar": "TZA", "somaliland": "SOM", "puntland": "SOM", "anambra": "NGA", "oyo": "NGA",
         "tshopo": "COD", "benguela": "AGO", "cubango": "AGO", "china": "CHN", "chinese": "CHN",
         "france": "FRA", "india": "IND", "karnataka": "IND", "japan": "JPN", "korea": "KOR",
         "italy": "ITA", "brasil": "BRA", "brazil": "BRA", "qatar": "QAT", "uae": "ARE",
         "jordan": "JOR", "taiwan": "TWN", "estonia": "EST", "finland": "FIN"}
EXTRA_PHRASES = {("sao", "tome"): "STP", ("guine", "bissau"): "GNB", ("saudi", "arabia"): "SAU",
                 ("united", "arab", "emirates"): "ARE", ("western", "cape"): "ZAF",
                 ("southwest", "state"): "SOM",
                 ("guinea", "ecuatorial"): "GNQ", ("guinee", "equatoriale"): "GNQ"}
FOREIGN = {"CHN": "China", "FRA": "France", "IND": "India", "JPN": "Japan", "KOR": "South Korea",
           "ITA": "Italy", "BRA": "Brazil", "QAT": "Qatar", "ARE": "United Arab Emirates",
           "JOR": "Jordan", "TWN": "Taiwan", "EST": "Estonia", "SAU": "Saudi Arabia", "FIN": "Finland"}
ISO_OF = {**ISO_OF, **EXTRA}
CTOK = CTOK | set(EXTRA)
PHRASES = {**PHRASES, **EXTRA_PHRASES}
# A state or province places a body in its country but is part of its name: stripping
# `somaliland` makes Somaliland's interior ministry Puntland's, and Tshopo's provincial
# government DR Congo's. So these count as places and are never stripped from a stem.
SUBNATIONAL = {"zanzibar", "somaliland", "puntland", "anambra", "oyo", "tshopo", "benguela",
               "cubango", "karnataka"}
SUB_PHRASES = {("western", "cape"), ("southwest", "state")}
STEM_CTOK = CTOK - SUBNATIONAL
STEM_PHRASES = {k: v for k, v in PHRASES.items() if k not in SUB_PHRASES}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower().replace("’", "'"))
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).split())


def countries() -> dict[str, str]:
    with open(COUNTRIES, encoding="utf-8-sig", newline="") as fh:
        return {**FOREIGN, **{r["iso-3"]: r["country-name"] for r in csv.DictReader(fh)}}


def catalogue() -> dict[str, dict]:
    return {i["url"]: i for i in json.load(open(CATALOGUE, encoding="utf-8"))["items"] if i["url"]}


def display_names() -> dict[str, dict]:
    return {r["slug"]: r for r in csv.DictReader(open(NAMES, encoding="utf-8"))}


def gov_stems() -> list[tuple[str, str]]:
    return [(r["stem"], r["where"]) for r in csv.DictReader(open(GOV_STEMS, encoding="utf-8"))]


def is_government(slug: str, stems) -> bool:
    for stem, where in stems:
        if slug == stem or slug.startswith(stem + "-"):
            return True
        if where == "any" and f"-{stem}-" in f"-{slug}-":
            return True
    return False


DRC = re.compile(r"democratic-republic-of-(the-)?congo|republique-democratique-du-congo|dr-congo|rd-congo|(?<![a-z])drc(?![a-z])")


def slug_countries(slug: str) -> set[str]:
    return EV.strip_country(DRC.sub("rdc", slug), PHRASES, CTOK, ISO_OF)[1]


def bare_country(org: str) -> str | None:
    """ISO-3 if the organisation as written is a country and nothing else."""
    s = EV.slugify(org)
    if DRC.fullmatch(s) or s in ("drc", "rdc", "the-drc"):
        return "COD"
    for lead in ("government-of-the-", "government-of-", "gouvernement-du-", "gouvernement-de-la-",
                 "gouvernement-de-", "gouvernement-", "gobierno-de-", "governo-de-", "the-", "republic-of-", "republique-du-", "republique-de-", "republique-",
                 "federal-republic-of-", "united-republic-of-", "kingdom-of-", "state-of-"):
        if s.startswith(lead) and len(s) > len(lead):
            s = s[len(lead):]
    # `congo` alone is the Republic; the Democratic Republic is told apart only by its adjective.
    if re.fullmatch(r"(the-)?(democratic-republic-of-(the-)?congo|republique-democratique-du-congo"
                    r"|rd-?congo|dr-congo|drc|rdc)", s):
        return "COD"
    # A region is not a country: `government-of-karnataka` is not India's government.
    left, found = EV.strip_country(s, STEM_PHRASES, STEM_CTOK, ISO_OF)
    if any(t in ("democratique", "democratic") for t in left):
        return None
    left = [t for t in left if t not in ("du", "de")]
    if found == {"STP"}:                    # the four-word name outruns strip_country's phrases
        left = [t for t in left if t not in ("and", "e", "principe")]
    return next(iter(found)) if len(found) == 1 and not left else None


def _key(s: str) -> str:
    return EV.stem(DRC.sub("rdc", EV.slugify(s)), STEM_PHRASES, STEM_CTOK, ISO_OF)[0]


def _stripped(slug: str) -> str:
    return "-".join(EV.strip_country(DRC.sub("rdc", slug), STEM_PHRASES, STEM_CTOK, ISO_OF)[0])


def org_countries(org: str) -> set[str]:
    return slug_countries(EV.slugify(org))


def match_strength(org: str, slug: str, display: str | None) -> int:
    """3 exact name, 2 same stem, 1 initialism either way, 0 no match.

    **Two named countries must agree.** The stem drops the country from both sides, so
    without this *Burkina Faso Ministry of Health* is Eswatini's ministry and *Togo AI* is
    `ai-uganda`. One side naming no country is allowed: *Huawei Namibia* is `huawei`.
    """
    if display and fold(org) == fold(display):
        return 3
    co, cs = org_countries(org), slug_countries(slug)
    if co and cs and co != cs:
        return 0
    k = _key(org)
    if k and (k == _key(slug) or (display and k == _key(display))):
        return 2
    o, s = EV.slugify(org), _stripped(slug)
    if o and s and (EV.is_abbreviation(o, s) or EV.is_abbreviation(s, o)
                    or (display and EV.is_abbreviation(o, _stripped(EV.slugify(display))))):
        return 1
    return 0


class Resolver:
    def __init__(self, cat=None, names=None):
        self.cat = cat if cat is not None else catalogue()
        self.names = names if names is not None else display_names()
        stems = self.stems = gov_stems()
        use = collections.Counter(e for i in self.cat.values() for e in i["entities"] or [])
        places = collections.defaultdict(collections.Counter)
        for i in self.cat.values():
            for e in i["entities"] or []:
                for p in i["places"] or []:
                    places[e][p] += 1
        self.use, self.places = use, places
        self.place = {}
        for slug in use:
            cs = slug_countries(slug)
            self.place[slug] = next(iter(cs)) if len(cs) == 1 else (
                places[slug].most_common(1)[0][0] if places[slug] else "")
        self.by_name, self.by_key = collections.defaultdict(set), collections.defaultdict(set)
        for slug in use:
            d = self.names.get(slug, {}).get("display")
            if d:
                self.by_name[fold(d)].add(slug)
                k = _key(d)
                if k:
                    self.by_key[k].add(slug)
            k = _key(slug)
            if k:
                self.by_key[k].add(slug)
        self.gov_of = {}
        for slug, n in use.most_common():
            if is_government(slug, stems) and slug.split("-")[0] in ("government", "gouvernement", "governo", "gobierno"):
                cs = slug_countries(slug)
                if len(cs) == 1:
                    self.gov_of.setdefault(next(iter(cs)), slug)

    def home(self, org: str, item: dict) -> set[str]:
        """Where a government body this tuple names may sit: the country the organisation
        names, else the one country the source is about, else nowhere."""
        named = org_countries(org) - {"XAF"}
        src = {p for p in item["places"] or [] if not p.startswith("X")}
        return named or (src if len(src) == 1 else set())

    def resolve(self, row: dict) -> tuple[str | None, str]:
        """(slug, how) — `how` is the method, or the cause of a drop when slug is None."""
        item = self.cat.get(row["source_url"])
        if item is None:
            return None, "source not in catalogue"
        tags = item["entities"] or []
        hint = row["slug_hint"]
        org = row["org_as_written"]
        named = org_countries(org) - {"XAF"}
        # The model's pick is trusted unless the organisation names a country the slug is not
        # in: *Ministry of Foreign Affairs of Malawi* is not the UAE's ministry.
        if hint and hint in tags and not (is_government(hint, self.stems) and named
                                          and self.place.get(hint) not in named):
            return hint, "hint"
        iso = bare_country(org)
        if iso:
            for t in tags:
                if t.split("-")[0] in ("government", "gouvernement", "governo", "gobierno") and slug_countries(t) == {iso}:
                    return t, "country, tagged"
            if iso in self.gov_of:
                return self.gov_of[iso], "country, untagged"
            return None, "country with no government slug"
        scored = collections.defaultdict(list)
        home = self.home(org, item)
        for t in tags:
            # A story about Sudan that tags China's foreign ministry is not naming it.
            if is_government(t, self.stems) and self.place.get(t) not in home:
                continue
            d = self.names.get(t, {}).get("display")
            m = match_strength(org, t, d)
            if m:
                scored[m].append(t)
        if not scored:
            return self._fallback(org, item)
        best = scored[max(scored)]
        if len(best) > 1:
            return None, "two tags match equally"
        return best[0], ["", "initialism", "stem", "name"][max(scored)]


    def _fallback(self, org: str, item: dict) -> tuple[str | None, str]:
        src = set(item["places"] or [])
        src_countries = {p for p in src if not p.startswith("X")}
        named = org_countries(org)
        for pool, how in ((self.by_name.get(fold(org), set()), "name, untagged"),
                          (self.by_key.get(_key(org), set()) if _key(org) else set(), "stem, untagged")):
            if not pool:
                continue
            pool = {s for s in pool if not (named and slug_countries(s) and slug_countries(s) != named)}
            # A government body must sit in the one country the source is about, or the one
            # the organisation names: *Ministry of Finance* in a regional story is no one's.
            # A body whose slug names a country must sit in one of the source's: *Supreme
            # Court* in a Mozambican story is not Ghana's.
            home = self.home(org, item)
            pool = {s for s in pool if (not is_government(s, self.stems) or self.place[s] in home)
                    and not (slug_countries(s) - {"XAF"} and self.place[s] not in src)}
            local = {s for s in pool if self.place[s] in src}
            if len(local) == 1:
                return next(iter(local)), how
            if len(local) > 1:
                return None, "two untagged slugs match equally"
            free = {s for s in pool if not is_government(s, self.stems)}
            if len(pool) == 1 and free:
                return next(iter(free)), how
        return None, "no slug matches"


def read_csv(path: Path, cols: list[str]) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        if rd.fieldnames != cols:
            raise SystemExit(f"{path.name}: columns {rd.fieldnames}, expected {cols}")
        return list(rd)


def write_csv(path: Path, cols: list[str], rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
