#!/usr/bin/env python3
r"""study-stage.py — a maturity study's search: fetch the leads, then stage what was selected.

    python scripts/study-stage.py health fetch KEN     # a searcher runs this on its own leads
    python scripts/study-stage.py health stage         # the parent: decisions into prepared\
    python scripts/study-stage.py health stage --dry   # the counts, nothing written
    python scripts/study-stage.py health ready --note 231

`maturity/documentation/maturity-study-method.md` §5. A searcher finds leads and judges them;
**no body passes through a model on its way to the handover.** That is the rule the
crossed-body defect taught (`lint-staged-queue.py`): a body retyped or carried in a list
arrives under another item's frontmatter and passes every URL check.

**`fetch {ISO3}`** reads `maturity/{id}/search/{ISO3}/leads.json`, the searcher's list, and
for each lead runs the screen `status-stage.py` implements (held or rejected in the mirror's
`lookups/` means it is not fetched), then one attempt, live then Wayback. The text goes to
the gitignored workroot, `scripts/.workroot/study/{id}/cache/{ISO3}/{k}.txt`, under the
address it came from; `fetched.csv` beside the leads says what happened to each. The
searcher reads the cached text and writes `decisions/{k}.json`.

**`stage`** takes every decision that selects its lead and writes the candidate into
`C:\corpus-osint-xfer\prepared\maturity-study-{id}\`: frontmatter from the decision, the
body **copied from the cache by this script**. One document selected for two countries is
one file carrying both places. It rewrites the folder from the decisions each time, so a
withdrawn decision withdraws its file, and it refuses once `READY` is in the folder. Three
records, all metadata, in `maturity/{id}/search/`:

- `searched.csv`   — by country and sub-indicator: leads, fetched, selected;
- `staged.csv`     — by file handed over, which `study-returned.py` reads after ingest;
- `unselected.csv` — every lead not staged and why: held, rejected, unfetchable, or the
  searcher's reason. Leads, not evidence; a later decision to widen is served from here.

**`ready`** writes `BRIEF.md` with its `Closed by:` line and then `READY`, last. OSINT's
cycle pulls a folder that carries `READY`, so this is the delivery and is a step of its own:
it is run after `lint-staged-queue.py` has been read and Bill has the count.

Frontmatter carries what a searcher established from the page and nothing guessed:
`entities` is left for ingest, and `topics` takes the study's `stage_topic` alone.

Exit: 0 done, 1 a decision that cannot be staged, 2 a missing file or a folder already delivered.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import importlib.util
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib  # noqa: E402
import study_lib   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("status_stage", os.path.join(HERE, "status-stage.py"))
ss = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ss)

FETCHED_FIELDS = ["k", "url", "status", "detail", "cache", "words", "kind", "page_title"]
SEARCHED_FIELDS = ["iso3", "sub_indicator", "leads", "fetched", "selected"]
UNSELECTED_FIELDS = ["iso3", "k", "sub_indicator", "url", "title", "why"]
PUBLISHED = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def search_dir(study_id: str, iso: str = "") -> str:
    return os.path.join(study_lib.study_dir(study_id), "search", iso)


def cache_dir(study_id: str, iso: str) -> str:
    """Under the workroot, which git ignores: the text of other people's documents."""
    return os.path.join(study_lib.CORPUS, "scripts", ".workroot", "study", study_id, "cache", iso)


def prepared_dir(study_id: str, share: str) -> str:
    return os.path.join(share, "prepared", f"maturity-study-{study_id}")


def load_json(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- #
# fetch
# --------------------------------------------------------------------------- #

def fetch(study_id: str, iso: str, fetcher=None, lookups=None) -> list[dict]:
    """Screen and fetch one country's leads. `fetcher` and `lookups` are for tests."""
    leads = load_json(os.path.join(search_dir(study_id, iso), "leads.json"))
    held, rejected = lookups or (ss.lookup("raw-url-index.csv"), ss.lookup("rejected-urls.csv"))
    fetcher = fetcher or ss.fetch
    out_dir = cache_dir(study_id, iso)
    os.makedirs(out_dir, exist_ok=True)
    rows, seen = [], {}
    for k, lead in enumerate(leads, 1):
        url = (lead.get("url") or "").strip()
        row = {"k": k, "url": url, "status": "", "detail": "", "cache": "", "words": 0,
               "kind": "", "page_title": ""}
        key = ss.norm(url)
        screened = ss.screen(url, held, rejected) if url else ("unfetchable", "no url")
        if key in seen:
            row.update(status="duplicate", detail=f"same document as lead {seen[key]}")
        elif screened:
            row.update(status=screened[0], detail=screened[1])
        else:
            seen[key] = k
            body, where, kind, title = fetcher(url)
            if body is None:
                row.update(status="unfetchable", detail=where)
            else:
                path = os.path.join(out_dir, f"{k}.txt")
                with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(f"URL: {where}\n\n{body}\n")
                row.update(status="fetched", cache=os.path.relpath(path, study_lib.CORPUS).replace("\\", "/"),
                           words=len(body.split()), kind=kind, page_title=title)
        rows.append(row)
    study_lib.write_csv(os.path.join(search_dir(study_id, iso), "fetched.csv"), FETCHED_FIELDS, rows)
    return rows


# --------------------------------------------------------------------------- #
# stage
# --------------------------------------------------------------------------- #

def decision_problem(study: dict, d: dict) -> str:
    """Why a selecting decision cannot be staged, or an empty string."""
    for key in ("title", "publisher", "published", "sub_indicator", "aspect", "fact"):
        if not str(d.get(key) or "").strip():
            return f"no `{key}`"
    if not PUBLISHED.match(str(d["published"]).strip()):
        return f"`published` is `{d['published']}`, not YYYY, YYYY-MM or YYYY-MM-DD"
    if d["sub_indicator"] not in study_lib.subs(study):
        return f"sub_indicator `{d['sub_indicator']}` is not in the study"
    known = study_lib.aspects(study)
    bad = [a for a in str(d["aspect"]).split(";") if a.strip() not in known]
    if bad:
        return f"aspect `{bad[0]}` is not in the study"
    if d.get("date_source", "source") not in ("source", "proxy"):
        return f"date_source `{d.get('date_source')}` is not source or proxy"
    return ""


def candidate(study: dict, d: dict, places: list[str], body: str, today: str) -> tuple[str, str]:
    """`(file name, file text)` for one selected document."""
    date, precision = ss.dated(str(d["published"]).strip())
    name = f"{date}-{places[0].lower()}-{ss.slugify(d['title'], 70)}.md"
    source = d.get("date_source") or ("source" if precision == "day" else "proxy")
    note = (f"Maturity study {study['id']}: selected for {d['sub_indicator']} "
            f"({str(d['aspect']).replace(';', ', ')}).")
    lines = ["---", "type: source", f"title: {ss.yq(d['title'].strip())}", f"url: {d['url']}",
             f"publisher: {ss.yq(d['publisher'].strip())}", f"published: {date}",
             f"date_precision: {precision}", f"date_source: {source}", f"retrieved: {today}",
             f"places: [{', '.join(places)}]", f"topics: [{study.get('stage_topic', '')}]",
             "entities: []", "body_completeness: full",
             f"sweep_batch: maturity-study-{study['id']}-{places[0]}-{today}",
             f"note: {ss.yq(note)}", "---", "", f"# {d['title'].strip()}"]
    return name, "\n".join(lines) + "\n" + body.rstrip("\n") + "\n"


def collect(study: dict, study_id: str, isos: list[str]) -> tuple[list[dict], list[dict], list[dict], list[str]]:
    """`(selected, unselected, searched, problems)` across every country's decisions."""
    selected, unselected, searched, problems = [], [], [], []
    for iso in isos:
        base = search_dir(study_id, iso)
        if not os.path.isfile(os.path.join(base, "leads.json")):
            continue
        leads = load_json(os.path.join(base, "leads.json"))
        fetched = {int(r["k"]): r for r in study_lib.read_csv(os.path.join(base, "fetched.csv"))}
        count = collections.defaultdict(lambda: collections.Counter())
        for k, lead in enumerate(leads, 1):
            sub = lead.get("sub_indicator", "")
            row = fetched.get(k)
            count[sub]["leads"] += 1
            miss = {"iso3": iso, "k": k, "sub_indicator": sub, "url": lead.get("url", ""),
                    "title": lead.get("title", "")}
            if row is None:
                unselected.append({**miss, "why": "not fetched: the lead was added after the fetch"})
                continue
            if row["status"] != "fetched":
                unselected.append({**miss, "why": f"{row['status']}: {row['detail']}"})
                continue
            count[sub]["fetched"] += 1
            path = os.path.join(base, "decisions", f"{k}.json")
            if not os.path.isfile(path):
                problems.append(f"{iso} lead {k}: fetched, and no decision written")
                continue
            try:
                d = load_json(path)
            except ValueError as e:
                problems.append(f"{iso} decisions/{k}.json: not readable JSON ({e})")
                continue
            if not d.get("select"):
                unselected.append({**miss, "why": "not selected: " + str(d.get("why_not") or "no reason given")})
                continue
            d = {**d, "url": lead["url"], "sub_indicator": d.get("sub_indicator") or sub}
            bad = decision_problem(study, d)
            if bad:
                problems.append(f"{iso} decisions/{k}.json: {bad}")
                continue
            count[d["sub_indicator"]]["selected"] += 1
            selected.append({**d, "iso3": iso, "k": k, "cache": row["cache"]})
        for sub in sorted(count):
            searched.append({"iso3": iso, "sub_indicator": sub, **{f: count[sub][f]
                                                                  for f in SEARCHED_FIELDS[2:]}})
    return selected, unselected, searched, problems


def stage(study: dict, study_id: str, share: str, today: str, dry: bool) -> int:
    folder = prepared_dir(study_id, share)
    if os.path.exists(os.path.join(folder, "READY")):
        print(f"study-stage: {folder} carries READY; it is delivered and is not rewritten.")
        return 2
    selected, unselected, searched, problems = collect(study, study_id, sorted(study_lib.countries()))
    held_names = {os.path.basename(r["file"]) for r in ss.lookup("raw-url-index.csv").values()}

    by_url: dict[str, list[dict]] = collections.OrderedDict()
    for d in selected:
        by_url.setdefault(ss.norm(d["url"]), []).append(d)
    files, staged = {}, []
    for group in by_url.values():
        first = group[0]
        try:
            with open(os.path.join(study_lib.CORPUS, first["cache"]), encoding="utf-8") as fh:
                body = fh.read()
        except OSError:
            problems.append(f"{first['iso3']} lead {first['k']}: its cached text is gone; fetch again")
            continue
        places = list(dict.fromkeys(d["iso3"] for d in group))
        name, text = candidate(study, first, places, body, today)
        stem, n = name[:-3], 2
        while name in files or name in held_names:
            name, n = f"{stem}-{n}.md", n + 1
        files[name] = text
        for d in group:
            staged.append({"file": name, "url": d["url"], "iso3": d["iso3"],
                           "sub_indicator": d["sub_indicator"], "aspect": d["aspect"],
                           "title": d["title"], "published": d["published"]})

    for p in problems:
        print(f"study-stage: FAIL - {p}")
    by_country = collections.Counter(s["iso3"] for s in staged)
    print(f"study-stage: {study_id} - {len(files)} document(s) selected for {len(by_country)} "
          f"countries, {len(unselected)} lead(s) not staged, {len(problems)} problem(s)"
          + (" (dry run)." if dry else "."))
    if dry:
        return 1 if problems else 0

    os.makedirs(folder, exist_ok=True)
    for old in os.listdir(folder):
        if old.endswith(".md") and old != "BRIEF.md" and old not in files:
            os.remove(os.path.join(folder, old))
    for name, text in files.items():
        with io.open(os.path.join(folder, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    base = search_dir(study_id)
    study_lib.write_csv(os.path.join(base, "staged.csv"), study_lib.STAGED_FIELDS, staged)
    study_lib.write_csv(os.path.join(base, "unselected.csv"), UNSELECTED_FIELDS, unselected)
    study_lib.write_csv(os.path.join(base, "searched.csv"), SEARCHED_FIELDS, searched)
    return 1 if problems else 0


def ready(study: dict, study_id: str, share: str, note: str, lint: str) -> int:
    folder = prepared_dir(study_id, share)
    staged = study_lib.read_csv(os.path.join(search_dir(study_id), "staged.csv"))
    files = sorted({s["file"] for s in staged})
    missing = [f for f in files if not os.path.isfile(os.path.join(folder, f))]
    if not files or missing:
        print(f"study-stage: nothing to deliver, or {len(missing)} staged file(s) are not in {folder}.")
        return 2
    per = collections.Counter()
    for f in files:
        per[next(s["iso3"] for s in staged if s["file"] == f)] += 1
    lines = [f"# Maturity study {study_id}: evidence to ingest", "",
             f"**This folder is evidence for maturity study `{study_id}`, not general ingest.** "
             f"CORPUS reviewed what `raw/` holds on the study's sub-indicators across 54 countries, "
             f"searched for what was missing and selected these {len(files)} documents.", "",
             f"**Closed by:** notes-for-osint {note}", "",
             "**Selection rule.** A fetched document is here when its body states a dated fact, on "
             "an aspect the study had no dated fact for, that nothing held states. There is no "
             "numeric cap. Bodies are verbatim from the fetch, copied by script.", "",
             f"**Lane asked for:** backfill; every file carries `sweep_batch: maturity-study-{study_id}-{{ISO3}}-{{date}}`.", "",
             f"**Staging lint:** {lint}", "",
             "**Count by country:** " + ", ".join(f"{iso} {n}" for iso, n in sorted(per.items())) + ".", ""]
    with io.open(os.path.join(folder, "BRIEF.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    with io.open(os.path.join(folder, "READY"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("")
    print(f"study-stage: BRIEF.md and READY written; {len(files)} documents delivered under note {note}.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A maturity study's search: fetch leads, stage selections.")
    ap.add_argument("study")
    ap.add_argument("command", choices=("fetch", "stage", "ready"))
    ap.add_argument("iso", nargs="?")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--note", help="ready: the notes-for-osint number announcing the delivery")
    ap.add_argument("--lint", default="", help="ready: the staging lint's result line, for the brief")
    ap.add_argument("--share", default=status_lib.EXCHANGE)
    a = ap.parse_args(argv)
    try:
        study = study_lib.load(a.study)
    except study_lib.StudyError as e:
        print(f"study-stage: {e}")
        return 2
    today = dt.date.today().isoformat()
    if a.command == "fetch":
        if a.iso not in study_lib.countries():
            print("study-stage: fetch takes a country, e.g. `study-stage.py health fetch KEN`.")
            return 2
        try:
            rows = fetch(a.study, a.iso)
        except (OSError, ValueError) as e:
            print(f"study-stage: {a.iso} leads.json cannot be read ({e}).")
            return 2
        for r in rows:
            print(f"  {r['k']:3d}  {r['status']:11s} {int(r['words']):7d} words  "
                  f"{r['cache'] or r['detail']}")
        print(f"study-stage: {a.iso} - {sum(1 for r in rows if r['status'] == 'fetched')} of "
              f"{len(rows)} lead(s) fetched; see fetched.csv.")
        return 0
    if a.command == "stage":
        return stage(study, a.study, a.share, today, a.dry)
    if not a.note or not a.lint:
        print("study-stage: ready needs --note and --lint.")
        return 2
    return ready(study, a.study, a.share, a.note, a.lint)


if __name__ == "__main__":
    sys.exit(main())
