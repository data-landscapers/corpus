#!/usr/bin/env python3
r"""whos-who-authors.py — a source's authors as Who's Who rows, without a model.

    python scripts/whos-who-authors.py           write build/whos-who/authors.csv, report
    python scripts/whos-who-authors.py --dry     report only

`documentation/whos-who.md` → *Authors* (Bill, 2026-11-20). OSINT sets `author:` (`; `-separated)
and, where the piece states a post, `author_roles:` (`Name | Position | Organisation`) across
`raw/`, and keeps `lookups/publications.csv` (`domain,publication,kind,country`) — osint-notes
348. This turns them into rows in the cache's columns plus `slug_fixed`, which
`whos_who_lib.Resolver` takes as the organisation without matching, and `place`, the outlet's
country; `whos-who-orgs.py` and `whos-who-people.py` read them beside the cache.

- **A post the piece states wins.** An `author_roles` entry that passes the cache's position
  test bar the role word (`author_fault`), at an organisation that resolves to a catalogue tag
  or is written whole (two words or more, not ending on a connector, or an acronym), is the
  author's row, and no default row is made for that author.
- **Otherwise the default.** *Journalist* at the publication for `newspaper`, `trade` and
  `agency`; *Author* for every other kind. The publication is `publications.csv`'s name for
  the source's registrable domain, its slug `slugify(publication)` (so an outlet already
  tagged as an entity is the same body), its place the row's `country`.
- **Repositories and platforms.** A copy on `doi.org`, PubMed Central or the like is placed
  at the journal the catalogue's `publisher` names (`journal`); a post on LinkedIn or Medium
  gets no default row, since *Author* there reads as staff.
- **Year** is the source's publication year, tense `holds`. No year, no row.
- **Skipped and counted:** a source whose domain has no `publications.csv` row, a wikilinked
  author (Bill's own pieces, bill-notes 147), a name outside 2–6 words.

Reads `raw/` only for `author_roles:`, which the catalogue does not carry. Writes
`build/whos-who/authors.csv` (untracked; rebuilt each night by `rebuild.py` stage 2e).
"""
from __future__ import annotations

import argparse
import collections
import csv
import importlib.util
import os
import re
import sys
from pathlib import Path

import whos_who_lib as W

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MIRROR = Path(os.environ.get("CORPUS_OSINT_MIRROR", r"C:\OSINT"))
RAW = MIRROR / "raw"
PUBLICATIONS = MIRROR / "lookups" / "publications.csv"
OUT = W.AUTHORS
JOURNALIST_KINDS = {"newspaper", "trade", "agency"}
CONNECTORS = {"and", "of", "the", "for", "in", "et", "de", "du", "des", "la", "le", "&"}
# Hosts whose tenant is the publisher (`vault_lib.MULTI_TENANT`), and second-level labels
# under a two-letter country code (`co.ke`): the registrable-domain rule OSINT keys
# `publications.csv` on.
MULTI_TENANT = ("blogspot.com", "wordpress.com", "substack.com", "medium.com", "ghost.io",
                "over-blog.com")
# Hosts that carry other people's papers: the outlet is the journal the catalogue's
# `publisher` names, its brackets and volume references cut (*BMC Health Services Research
# 21(Suppl 1):691*), not *DOI* or *National Institutes of Health*.
REPOSITORIES = {"doi.org", "nih.gov", "researchgate.net", "ssrn.com", "zenodo.org", "academia.edu",
                "semanticscholar.org", "hal.science", "osf.io", "figshare.com"}
# Platforms where anyone posts: *Author* at LinkedIn reads as an employee, so no default row.
PLATFORMS = {"linkedin.com", "medium.com", "youtube.com", "scribd.com", "x.com", "twitter.com",
             "facebook.com", "substack.com", "instagram.com", "tiktok.com"}
SLD = {"co", "com", "org", "net", "gov", "gouv", "edu", "ac", "or", "go", "mil", "sch", "ne", "web"}

_spec = importlib.util.spec_from_file_location("whos_who_cache", W.ROOT / "scripts" / "whos-who-cache.py")
CACHE_MOD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CACHE_MOD)


def registrable(url: str) -> str:
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", (url or "").strip().lower())
    s = s.split("/")[0].split("?")[0].split("#")[0].split("@")[-1].split(":")[0]
    s = re.sub(r"^www\.", "", s).strip(".")
    parts = s.split(".")
    if len(parts) <= 2:
        return s
    for suf in MULTI_TENANT:
        n = suf.count(".") + 1
        if parts[-n:] == suf.split("."):
            return ".".join(parts[-(n + 1):])
    if len(parts[-1]) == 2 and parts[-2] in SLD:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def roles_in_raw() -> dict[str, list[tuple[str, str, str]]]:
    """url -> [(name, position, organisation)], from every `raw/` file's frontmatter."""
    out = {}
    for p in RAW.rglob("*.md"):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not text.startswith("---") or "\nauthor_roles:" not in text[:6000]:
            continue
        fm = text[3:text.find("\n---", 3)]
        url = re.search(r"(?m)^url:\s*(\S+)", fm)
        block = re.search(r"(?ms)^author_roles:\s*\n((?:[ \t]+-.*\n?)+)", fm)
        if not url or not block:
            continue
        got = []
        for ln in block.group(1).splitlines():
            v = ln.strip()[1:].strip().strip('"').strip("'")
            bits = [b.strip() for b in v.split("|")]
            if len(bits) == 3 and all(bits):
                got.append(tuple(bits))
        if got:
            out[url.group(1).strip().strip("'\"")] = got
    return out


def author_fault(pos: str) -> str | None:
    """The cache's position test without its role word: the roles list is officeholders',
    and a piece's *Business Editor* or *Senior Lecturer* is the post it states (Bill: a
    stated post always wins). Deny-list, length and *former* still hold."""
    f = CACHE_MOD.position_fault(pos)
    return None if f == "position has no role word" else f


def journal(publisher: str) -> str:
    s = re.sub(r"\s*[\(\[][^)\]]*[\)\]]", "", publisher)
    s = re.sub(r"\s+\d[\w()., :;-]*$", "", s).strip(" ,;:-")
    return s if len(s) >= 3 else ""


def whole_org(org: str) -> bool:
    words = org.split()
    if len(words) >= 2:
        return W.fold(words[-1]).strip(",") not in CONNECTORS
    return len(org) >= 3 and org.isupper()


def build(dry: bool = False) -> int:
    cat, res = W.catalogue(), W.Resolver()
    pubs = {r["domain"]: r for r in csv.DictReader(open(PUBLICATIONS, encoding="utf-8-sig"))}
    roles = roles_in_raw()
    drops, rows = collections.Counter(), []
    for url, item in cat.items():
        if not item.get("author"):
            continue
        year = (item.get("published") or "")[:4]
        if not re.fullmatch(r"(19|20)\d\d", year):
            drops["no year"] += 1
            continue
        pub = pubs.get(registrable(url))
        names = [n.strip() for n in item["author"].split(";") if n.strip()]
        stated = {}
        for name, pos, org in roles.get(url, []):
            if author_fault(pos):
                drops["stated post fails the position test (default row instead)"] += 1
                continue
            slug, _ = res.resolve({"source_url": url, "org_as_written": org, "slug_hint": ""})
            if slug is None:
                if not whole_org(org):
                    drops["stated organisation truncated (default row instead)"] += 1
                    continue
                slug = W.EV.slugify(org)
            stated.setdefault(W.fold(name), []).append((pos, org, slug))
        for name in names:
            if "[[" in name:
                drops["wikilinked author"] += 1
                continue
            if not 2 <= len(name.split()) <= 6:
                drops["name not 2-6 words"] += 1
                continue
            mine = stated.get(W.fold(name))
            if mine:
                for pos, org, slug in mine:
                    rows.append([url, name, pos, org, "", "holds", year, "", slug, ""])
                continue
            if pub is None:
                drops["domain not in publications.csv"] += 1
                continue
            if pub["domain"] in PLATFORMS:
                drops["posted on a platform, no outlet"] += 1
                continue
            outlet, place = pub["publication"], pub["country"]
            if pub["domain"] in REPOSITORIES:
                outlet, place = journal(item.get("publisher") or ""), ""
                if not outlet:
                    drops["repository copy with no journal named"] += 1
                    continue
            pos = "Journalist" if pub["kind"] in JOURNALIST_KINDS else "Author"
            rows.append([url, name, pos, outlet, "", "holds", year, "", W.EV.slugify(outlet), place])
    print(f"{len(rows)} author rows from {len({r[0] for r in rows})} sources; "
          f"{sum(1 for r in rows if r[2] not in W.AUTHOR_POSITIONS)} with a stated post; "
          f"{len({r[8] for r in rows})} organisations")
    for k, v in drops.most_common():
        print(f"  skipped {v:5d}  {k}")
    if not dry:
        W.write_csv(OUT, W.AUTHOR_COLS, [dict(zip(W.AUTHOR_COLS, r)) for r in rows])
        print(f"wrote {OUT.relative_to(W.ROOT)}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    return build(ap.parse_args(argv).dry)


if __name__ == "__main__":
    sys.exit(main())
