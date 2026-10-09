#!/usr/bin/env python3
r"""study-select.py — a maturity study's reading list, one per country.

    cd scripts/.workroot
    python scripts/study-select.py health            # all 54
    python scripts/study-select.py health --iso KEN  # one country
    python scripts/study-select.py health --dry      # the counts, nothing written
    python scripts/study-select.py health --add      # Phase 2: append what ingest returned
    python scripts/study-select.py health --new      # upkeep: append what has arrived since

`maturity/documentation/maturity-study-method.md` §4. Writes
`maturity/{id}/evidence/{ISO3}/readlist.csv`, the list a drafter reads whole, and
`maturity/{id}/evidence/summary.csv`, the size of each list, which is what H3 is sized from.

**A document is listed when its title or body carries one of the study's terms.** The
study's subjects are broader than the study: `dpi.mis` holds every sector's management
system, so a subject tag alone would hand a health drafter the education ministry's. The
term list narrows the tagged documents and catches the untagged ones, and one test does
both. What a tag adds is recorded in `why`, never used to admit.

`why` names every route that reached the document, joined by `+`:

- `subject`  — `topics:` holds one of the study's subjects;
- `ledger`   — a ledger row on a study subject cites it;
- `status`   — the status report's sub-section on a study subject links it;
- `considered` — the country's `considered.txt` holds it;
- `regional` — it is filed to the country's region or to Africa, not to the country, and
  its text names the country.

A document cited by a study-subject ledger row or status sub-section is listed whether or
not its body matches, when the row or the sub-section itself carries a term: the status
report already read it as being about this.

**Tagged documents the terms dropped are counted, not hidden**: `summary.csv` carries them
as `tagged_no_term`, so a term list that is missing a country's name for its system shows
up as a large number beside a short list.

**A long document is read around its terms, not whole** *(Bill, 2026-10-06)*. The 54 lists
came to 6.9 million words, a handful of documents carrying most of it: one demographic
survey is 340,000. Past `PASSAGE_WORDS` the list points at a passages file instead - every
paragraph that carries a term, with its neighbours, under the document's opening - and says
so in `read`. So does a document past `SPARSE_WORDS` with no more than `SPARSE_HITS` hits:
123 such listings held 1.8 million words between them, each for a mention in passing. The
risk is a fact stated away from any term, taken knowingly. Passages are
source text, so they are written under the gitignored workroot and never committed.

**`--add` is the Phase 2 re-read (method §7) and renumbers nothing.** It appends to each
existing list the documents `search/returned.csv` marks admitted, as `why = returned`, and
the held excerpts of `search/reacquire.csv` that are no longer excerpts, as
`why = completed`. A document goes to the country its record's `places:` now names, which
ingest may have corrected, and to the country it was staged for where it names none. `n`
continues from the list's highest and the new rows open new slices, so every facts file
already written still names its document.

**`--new` is the upkeep's set difference** (`MATURITY-UPDATE.md`): the same selection, less what
each list already holds, appended as `--add` appends and entered in `evidence/arrivals.csv`
as open work for `study-update.py`. With `--dry` it counts and writes nothing.

The status sub-sections themselves head each list as `kind = status` rows. Runs from the
workroot because it reads `raw/` through Corpus's own index.

Exit: 0 written, 2 the study or the index cannot be read.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib  # noqa: E402
import study_lib   # noqa: E402
import vault_lib   # noqa: E402

SUMMARY_FIELDS = ["iso3", "documents", "passages", "words", "status_sections", "tagged_no_term"]
PASSAGE_WORDS = 20_000     # a document longer than this is read as passages
SPARSE_WORDS = 8_000       # ...and so is one past this that carries a term only in passing
SPARSE_HITS = 2
SLICE_WORDS = 70_000       # what one drafter reads
OPENING_WORDS = 300        # what of its opening is always kept, for what the document is
LONG_BLOCK = 400           # a "paragraph" past this is a table or a wrapped page: cut by line
ROUTES = ("status", "ledger", "subject", "considered", "regional")


def scan(rows: list[dict], read, terms: re.Pattern) -> dict[str, dict]:
    """slug -> what every country's selection needs of one `raw/` document, read once.

    `read(row)` returns the file's text. Bodies are folded and dropped here, so 380 MB is
    held one document at a time."""
    out = {}
    for r in rows:
        d, fm = r["d"], r["fm"]
        if d.get("folder") != "raw" or d.get("ext") != ".md":
            continue
        title = str(fm.get("title") or d["slug"])
        folded = study_lib.fold(title + "\n" + (read(r) or ""))
        found = terms.findall(folded)
        out[d["slug"]] = {
            "slug": d["slug"], "path": r["path"], "title": title,
            "published": str(fm.get("published") or d.get("file_date") or ""),
            "places": [str(p) for p in vault_lib.as_list(fm.get("places"))],
            "topics": [str(t) for t in vault_lib.as_list(fm.get("topics"))],
            "url": str(fm.get("url") or ""),
            "url_norm": d.get("url_norm", ""), "words": d.get("words", 0),
            "terms": sorted({t.lower() for t in found}), "hits": len(found),
            "folded": folded if found else "",
        }
    return out


def passages(text: str, terms: re.Pattern) -> str:
    """The paragraphs of `text` that carry a term, each with the one before and after it.

    Paragraphs rather than a window of words, because a fact and the year it is stated for
    sit in one paragraph far more often than within any fixed distance of a term. A block
    with no blank line in it - a table, a page captured as one run - is cut by line first,
    or a single hit would keep the whole of it."""
    body = text.split("\n---", 1)[1] if text.startswith("---") and "\n---" in text[3:] else text
    blocks = []
    for block in re.split(r"\n\s*\n", body):
        if len(block.split()) > LONG_BLOCK:
            blocks += [line for line in block.splitlines() if line.strip()]
        elif block.strip():
            blocks.append(block.strip())
    keep, opening = set(), 0
    for i, block in enumerate(blocks):
        if opening < OPENING_WORDS:
            keep.add(i)
            opening += len(block.split())
        if terms.search(study_lib.fold(block)):
            keep.update((i - 1, i, i + 1))
    out, last = [], -1
    for i in sorted(k for k in keep if 0 <= k < len(blocks)):
        if i != last + 1:
            out.append("[...]")
        out.append(blocks[i])
        last = i
    if last != len(blocks) - 1:
        out.append("[...]")
    return "\n\n".join(out) + "\n"


def cited(iso: str, subjects: list[str], terms: re.Pattern, reports: str,
          by_url: dict[str, str]) -> tuple[dict[str, set], list[dict]]:
    """What the country's own report already holds on the study's subjects.

    Returns `(slug -> routes, status rows)`. A route marked `!` admits the document on the
    report's word: the ledger row or sub-section citing it carries a term itself."""
    routes: dict[str, set] = {}
    status_rows = []
    unit = os.path.join(reports, iso)

    for row in study_lib.read_csv(os.path.join(unit, "ledger.csv")):
        if row.get("subject") not in subjects:
            continue
        text = study_lib.fold(" ".join(str(v) for v in row.values()))
        mark = "ledger!" if terms.search(text) else "ledger"
        for slug in filter(None, (s.strip() for s in (row.get("sources") or "").split("|"))):
            routes.setdefault(slug, set()).add(mark)

    status_path = os.path.join(unit, f"{iso}-status.md")
    try:
        with open(status_path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        text = ""
    for slug, label, prose in status_lib.sections(text):
        if slug not in subjects or not prose:
            continue
        hit = terms.search(study_lib.fold(prose))
        status_rows.append({"iso3": iso, "kind": "status", "slug": slug,
                            "path": os.path.relpath(status_path, study_lib.CORPUS).replace("\\", "/"),
                            "title": label, "why": "status", "words": len(prose.split()),
                            "hits": 1 if hit else 0})
        for url in status_lib.links(prose):
            held = by_url.get(vault_lib.normalise_url(url))
            if held:
                routes.setdefault(held, set()).add("status!" if hit else "status")

    try:
        with open(os.path.join(unit, "considered.txt"), encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    routes.setdefault(line.strip(), set()).add("considered")
    except OSError:
        pass
    return routes, status_rows


def number(status_rows: list[dict], rows: list[dict]) -> None:
    """Give each document its number and its slice, in place.

    `n` is what a drafter names its facts file after, so a list with a file for every `n` has
    been read through. `slice` packs the list into runs of at most `SLICE_WORDS`, one drafter
    each: a country's reading does not always fit one context, and a drafter that runs out
    of room partway stops reading without saying so. Status rows are context for every
    slice and carry neither."""
    for r in status_rows:
        r.update(n="", slice="")
    part, room = 1, SLICE_WORDS
    for n, r in enumerate(rows, 1):
        words = int(r["words"])
        if words > room and room < SLICE_WORDS:
            part, room = part + 1, SLICE_WORDS
        room -= words
        r.update(n=n, slice=part)


def added(iso: str, existing: list[dict], docs: dict[str, dict], returned: list[dict],
          reacquired: list[dict], complete: set[str], known: set[str]) -> list[dict]:
    """The rows `--add` appends to one country's list, unnumbered."""
    listed = {r["slug"]: r for r in existing if r.get("kind") == "raw"}
    if any(r.get("why") in ("returned", "completed") for r in listed.values()):
        return []          # this list has had its Phase 2 rows; a second run adds none
    rows = []

    def mine(slug: str, staged_iso: str) -> bool:
        places = set(docs[slug]["places"]) & known
        return iso in places if places else staged_iso == iso

    def row(slug: str, why: str) -> dict:
        doc = docs[slug]
        return {"iso3": iso, "kind": "raw", "slug": slug, "path": doc["path"], "read": "whole",
                "url": doc["url"], "title": doc["title"], "published": doc["published"],
                "places": ";".join(doc["places"]), "why": why,
                "terms": ";".join(doc["terms"]), "hits": doc["hits"], "words": doc["words"]}

    for r in returned:
        slug = r.get("slug", "")
        if r.get("outcome") == "admitted" and slug in docs and slug not in listed                 and mine(slug, r["iso3"]):
            rows.append(row(slug, "returned"))
    for r in reacquired:
        slug = r.get("slug", "")
        was = listed.get(slug, {})
        grown = was.get("read") != "whole" or int(docs[slug]["words"]) > int(was.get("words") or 0)
        if slug in docs and slug in complete and grown and mine(slug, r["iso3"]):
            rows.append(row(slug, "completed"))
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: r["published"], reverse=True):
        if r["slug"] not in seen:
            seen.add(r["slug"])
            out.append(r)
    return out


def renumber(existing: list[dict], rows: list[dict]) -> None:
    """Number appended rows after the list's last, in slices after its last, in place."""
    raw = [r for r in existing if r.get("kind") == "raw"]
    n = max([int(r["n"]) for r in raw] or [0])
    part, room = max([int(r["slice"]) for r in raw] or [0]) + 1, SLICE_WORDS
    for r in rows:
        words = int(r["words"])
        if words > room and room < SLICE_WORDS:
            part, room = part + 1, SLICE_WORDS
        room -= words
        n += 1
        r.update(n=n, slice=part)


def select(iso: str, country: dict, docs: dict[str, dict], subjects: list[str],
           routes: dict[str, set]) -> tuple[list[dict], int]:
    """`(readlist rows, tagged documents the terms dropped)` for one country."""
    name = study_lib.name_regex(iso, country)
    rows, dropped = [], 0
    for slug, doc in docs.items():
        why = {r.rstrip("!") for r in routes.get(slug, ())}
        reported = any(r.endswith("!") for r in routes.get(slug, ()))
        in_country = iso in doc["places"]
        tagged = in_country and bool(set(doc["topics"]) & set(subjects))
        regional = (not in_country and bool(set(doc["places"]) & country["regions"])
                    and bool(doc["hits"]) and bool(name.search(doc["folded"])))
        if not (in_country or regional or reported):
            continue
        if not doc["hits"] and not reported:
            dropped += tagged
            continue
        if tagged:
            why.add("subject")
        if regional:
            why.add("regional")
        rows.append({"iso3": iso, "kind": "raw", "slug": slug, "path": doc["path"],
                     "read": "whole", "url": doc["url"],
                     "title": doc["title"], "published": doc["published"],
                     "places": ";".join(doc["places"]),
                     "why": "+".join(r for r in ROUTES if r in why) or "term",
                     "terms": ";".join(doc["terms"]), "hits": doc["hits"],
                     "words": doc["words"]})
    # Newest first, with the documents only a term reached after everything a tag or the
    # country's own report vouches for.
    rows.sort(key=lambda r: r["published"], reverse=True)
    rows.sort(key=lambda r: r["why"] == "term")
    return rows, dropped


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A maturity study's reading list, per country.")
    ap.add_argument("study")
    ap.add_argument("--iso", action="append", help="one country; repeatable")
    ap.add_argument("--dry", action="store_true", help="print the counts, write nothing")
    ap.add_argument("--add", action="store_true",
                    help="Phase 2: append the returned and completed documents, renumbering nothing")
    ap.add_argument("--new", action="store_true",
                    help="upkeep: append the documents that have arrived since, as open arrivals")
    a = ap.parse_args(argv)

    try:
        study = study_lib.load(a.study)
        index = vault_lib.load_index()
    except (study_lib.StudyError, vault_lib.ForeignIndex, vault_lib.EmptyIndex) as e:
        print(f"study-select: {e}")
        return 2

    def read(row):
        try:
            with open(os.path.join(vault_lib.ROOT, row["path"]), encoding="utf-8",
                      errors="replace") as fh:
                return fh.read()
        except OSError:
            return ""

    terms = study_lib.term_regex(study["terms"])
    docs = scan(index, read, terms)
    by_url = {d["url_norm"]: s for s, d in docs.items() if d["url_norm"]}
    all_countries = study_lib.countries()
    wanted = a.iso or sorted(all_countries)
    unknown = [i for i in wanted if i not in all_countries]
    if unknown:
        print(f"study-select: not a country in lookups/countries.csv: {', '.join(unknown)}")
        return 2

    base = os.path.join(study_lib.study_dir(a.study), "evidence")
    cut_dir = os.path.join(vault_lib.ROOT, "study", a.study, "passages")
    cut: dict[tuple, int] = {}

    def shorten(r: dict, iso: str) -> None:
        """Point a long document's row at its passages file.

        A country's own document is cut once, around the terms, however many lists carry it.
        **A regional one is cut per country, around the country's name**: one continental
        report was otherwise read at 29,000 words by each of 52 drafters, for the paragraph
        or two that concerned theirs."""
        slug, regional = r["slug"], "regional" in r["why"].split("+")
        key = (slug, iso if regional else "")
        path = os.path.join(cut_dir, iso, slug + ".md") if regional else \
            os.path.join(cut_dir, slug + ".md")
        if key not in cut:
            what = (f"the paragraphs naming {all_countries[iso]['name']}" if regional
                    else "the paragraphs carrying a study term")
            text = (f"# {r['title']}\n\nslug: {slug}\nurl: {r['url']}\npublished: {r['published']}\n"
                    f"Passages only: {what}, of {r['words']} words.\n\n"
                    + passages(read({"path": r["path"]}),
                               study_lib.name_regex(iso, all_countries[iso]) if regional else terms))
            cut[key] = len(text.split())
            if not a.dry:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(text)
        r.update(read="passages", words=cut[key],
                 path=os.path.relpath(path, study_lib.CORPUS).replace("\\", "/"))

    if a.add:
        search = os.path.join(study_lib.study_dir(a.study), "search")
        returned = study_lib.read_csv(os.path.join(search, "returned.csv"))
        reacquired = study_lib.read_csv(os.path.join(search, "reacquire.csv"))
        complete = {r["d"]["slug"] for r in index
                    if str(r["fm"].get("body_completeness") or "full") != "excerpt"}
        total = 0
        for iso in wanted:
            path = os.path.join(base, iso, "readlist.csv")
            existing = study_lib.read_csv(path)
            rows = added(iso, existing, docs, returned, reacquired, complete, set(all_countries))
            for r in rows:
                if int(r["words"]) > PASSAGE_WORDS or (int(r["words"]) > SPARSE_WORDS
                                                        and int(r["hits"]) <= SPARSE_HITS):
                    shorten(r, iso)
            renumber(existing, rows)
            total += len(rows)
            if rows and not a.dry:
                study_lib.write_csv(path, study_lib.READLIST_FIELDS, existing + rows)
            if rows:
                print(f"  {iso}  {len(rows):3d} added  {sum(int(r['words']) for r in rows):7d} words  "
                      f"slices {rows[0]['slice']}-{rows[-1]['slice']}")
        print(f"study-select: {a.study} - {total} documents added to the reading lists"
              + (" (dry run, nothing written)." if a.dry else "."))
        return 0

    if a.new:
        register = os.path.join(base, "arrivals.csv")
        arrivals, today, total = study_lib.read_csv(register), dt.date.today().isoformat(), 0
        for iso in wanted:
            path = os.path.join(base, iso, "readlist.csv")
            existing = study_lib.read_csv(path)
            if not existing:
                continue        # never listed: the study has not reached this country
            listed = {r["slug"] for r in existing if r.get("kind") == "raw"}
            routes, _ = cited(iso, study["subjects"], terms, status_lib.REPORTS, by_url)
            rows = [r for r in select(iso, all_countries[iso], docs, study["subjects"], routes)[0]
                    if r["slug"] not in listed]
            for r in rows:
                if int(r["words"]) > PASSAGE_WORDS or (int(r["words"]) > SPARSE_WORDS
                                                        and int(r["hits"]) <= SPARSE_HITS):
                    shorten(r, iso)
            renumber(existing, rows)
            total += len(rows)
            for r in rows:
                arrivals.append({"iso3": iso, "n": r["n"], "slug": r["slug"], "listed": today,
                                 "outcome": "", "closed": ""})
                print(f"  {iso}  {r['n']:>4}  {r['slug']}  {r['words']} words")
            if rows and not a.dry:
                study_lib.write_csv(path, study_lib.READLIST_FIELDS, existing + rows)
        if total and not a.dry:
            study_lib.write_csv(register, study_lib.ARRIVAL_FIELDS, arrivals)
        print(f"study-select: {a.study} - {total} new document(s) on the reading lists"
              + (" (dry run, nothing written)." if a.dry else "."))
        return 0

    summary = []
    for iso in wanted:
        routes, status_rows = cited(iso, study["subjects"], terms, status_lib.REPORTS, by_url)
        rows, dropped = select(iso, all_countries[iso], docs, study["subjects"], routes)
        for r in rows:
            if int(r["words"]) > PASSAGE_WORDS or (int(r["words"]) > SPARSE_WORDS
                                                    and int(r["hits"]) <= SPARSE_HITS):
                shorten(r, iso)
        summary.append({"iso3": iso, "documents": len(rows),
                        "passages": sum(1 for r in rows if r["read"] == "passages"),
                        "words": sum(int(r["words"]) for r in rows),
                        "status_sections": len(status_rows), "tagged_no_term": dropped})
        number(status_rows, rows)
        if not a.dry:
            study_lib.write_csv(os.path.join(base, iso, "readlist.csv"),
                                study_lib.READLIST_FIELDS, status_rows + rows)
    if not a.dry and not a.iso:
        study_lib.write_csv(os.path.join(base, "summary.csv"), SUMMARY_FIELDS, summary)

    for s in summary:
        print(f"  {s['iso3']}  {s['documents']:4d} documents  {s['words']:8d} words  "
              f"{s['tagged_no_term']:4d} tagged, no term")
    print(f"study-select: {a.study} - {len(summary)} countries, "
          f"{sum(s['documents'] for s in summary)} listings, "
          f"{sum(s['words'] for s in summary)} words"
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
