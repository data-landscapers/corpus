#!/usr/bin/env python3
r"""study-external.py — the external databases' claims read into a maturity study, one study a visit.

    python scripts/study-external.py order               # studies by claims still open
    python scripts/study-external.py plan ID [--per-call 8] [--dir DIR]
    python scripts/study-external.py screen ID           # before --merge: drop a database's absences
    python scripts/study-external.py close ID            # after the drafters and --merge

`documentation/external-datasets.md` §4 is the citing rule; CORPUS housekeeping 58 is the job.
A claim is one row of `reference/external/claims.csv` that names the study. **Every claim ends
in `maturity/{id}/external.csv`** with an outcome, and a study is done when none is `open`:

- `superseded` — a later round of the same survey answers the same question for the country.
  The database record in `raw/` carries the latest round only, so an older one has nothing to
  cite. Registers (Carnegie, UNCTAD) have no rounds and are never superseded.
- `continental` — the claim names no one of the 54 (Carnegie's `XAF` rows).
- `read-before` — its document is already on the country's reading list with a facts file: a
  drafter read that primary for this study, and the facts it stated are held.
- `open` — sent to a drafter, beside its held primary where one is held, else beside the
  country's lines of the source's database record (`passages/external/`).
- `fact` or `nothing` — what the drafter wrote, in the facts file's `claims` map; `fact`
  names the evidence row it became, once `study-profile.py --merge` has taken it.

**A database's "no" is never taken as a fact** (`screen`, 2026-11-11). Rung 1 asks for a source
saying the thing is absent *and* not being prepared; a survey's "no" says the first half at most,
and a round's year outranks an earlier dated launch. So `screen` drops from the facts files every
fact citing a database record whose value is `none` or the aspect's deferred value, before
`study-profile.py --merge` takes them, and answers its claim `nothing`.

`plan` adds one reading-list row a document, `pass` = `external`, so `--merge` takes the
facts files the usual way, and writes one drafter prompt a call of `--per-call` countries.
`close` reads the `claims` maps back. Neither touches `C:\OSINT`.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study_lib  # noqa: E402

CORPUS = study_lib.CORPUS
OSINT = r"C:\OSINT"
CLAIMS = os.path.join(CORPUS, "reference", "external", "claims.csv")
SOURCES = os.path.join(CORPUS, "lookups", "external-sources.csv")
PASSAGES = os.path.join(CORPUS, "scripts", ".workroot", "study")
LEDGER_FIELDS = ["claim", "source", "survey_year", "iso3", "item", "question", "status", "name",
                 "year", "fit", "outcome", "slug", "row_ids", "note"]
WHOLE_MAX = 6000  # words; a longer primary is read in passages around the study's terms

spec = importlib.util.spec_from_file_location("status_stage", os.path.join(HERE, "status-stage.py"))
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)
_sel = importlib.util.spec_from_file_location("study_select", os.path.join(HERE, "study-select.py"))
SELECT = importlib.util.module_from_spec(_sel)
_sel.loader.exec_module(SELECT)

BASIS = {
    "self-reported": "the government's own answer to the survey",
    "publisher-assessed": "the publisher's own assessment",
    "publisher-compiled": "the publisher's compilation",
    "by-row": "per row",
}


def rows(path: str) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def claim_id(c: dict) -> str:
    key = "|".join(c[k] for k in ("source", "survey_year", "iso3", "item", "name", "year", "status"))
    return c["source"] + "-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]


def study_claims(sid: str) -> list[dict]:
    out = []
    for c in rows(CLAIMS):
        if c["fit"] != "none" and sid in c["studies"].split(";"):
            out.append(dict(c, claim=claim_id(c)))
    return out


def ledger_path(sid: str) -> str:
    return os.path.join(study_lib.study_dir(sid), "external.csv")


def read_ledger(sid: str) -> dict[str, dict]:
    p = ledger_path(sid)
    return {r["claim"]: r for r in rows(p)} if os.path.exists(p) else {}


def records() -> dict[str, dict]:
    """source id -> its database record in raw/: {slug, path, url, title, published}."""
    held = ss.lookup("raw-url-index.csv")
    out = {}
    for s in rows(SOURCES):
        h = held.get(ss.norm(s["page_url"]))
        if h:
            path = h["file"].replace("\\", "/")
            out[s["id"]] = {"slug": os.path.splitext(os.path.basename(path))[0], "path": path,
                            "url": s["page_url"], "title": s["title"], "publisher": s["publisher"],
                            "published": h.get("published", "")}
    return out


def front(path: str) -> dict:
    """title, url and published from a raw file's frontmatter."""
    out = {}
    with open(os.path.join(OSINT, path), encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    for line in (m[1].splitlines() if m else []):
        k, _, v = line.partition(":")
        if k in ("title", "url", "published"):
            out[k] = v.strip().strip('"')
    out["text"] = text[m.end():] if m else text
    return out


def order() -> int:
    by = collections.Counter()
    for c in rows(CLAIMS):
        if c["fit"] != "none" and c["studies"]:
            for s in c["studies"].split(";"):
                by[s] += 1
    for sid, n in by.most_common():
        led = read_ledger(sid)
        tally = collections.Counter(r["outcome"] for r in led.values())
        state = "not planned" if not led else ("done" if not tally["open"] else f"{tally['open']} open")
        print(f"{sid:28} {n:6} claims  {state}  {dict(tally) if led else ''}")
    return 0


def plan(sid: str, per_call: int, out_dir: str) -> int:
    study = study_lib.load(sid)
    claims = study_claims(sid)
    if not claims:
        print(f"{sid}: no mapped claims")
        return 0
    led = read_ledger(sid)
    terms = study_lib.term_regex(study["terms"])
    recs = records()
    held = ss.lookup("raw-url-index.csv")
    countries = study_lib.countries()

    latest = {}
    for c in claims:
        if c["survey_year"]:
            k = (c["source"], c["iso3"], c["item"])
            latest[k] = max(latest.get(k, ""), c["survey_year"])

    live: dict[str, list[dict]] = collections.defaultdict(list)
    for c in claims:
        base = {f: c.get(f, "") for f in LEDGER_FIELDS}
        if c["claim"] in led and led[c["claim"]]["outcome"] != "open":
            continue
        if c["iso3"] not in countries:
            led[c["claim"]] = dict(base, outcome="continental", note="names no one of the 54")
        elif c["survey_year"] and c["survey_year"] < latest[(c["source"], c["iso3"], c["item"])]:
            led[c["claim"]] = dict(base, outcome="superseded",
                                   note=f"the {latest[(c['source'], c['iso3'], c['item'])]} round answers it")
        else:
            live[c["iso3"]].append(c)

    calls, made = [], collections.Counter()
    for iso in sorted(live):
        edir = os.path.join(study_lib.study_dir(sid), "evidence", iso)
        rl_path = os.path.join(edir, "readlist.csv")
        rl = study_lib.read_csv(rl_path) if os.path.exists(rl_path) else []
        facts_dir = os.path.join(edir, "facts")
        on_list = {r["slug"]: r for r in rl if r.get("kind") == "raw" and r.get("n")}
        nxt = max([int(r["n"]) for r in rl if (r.get("n") or "").isdigit()] + [0]) + 1
        docs: dict[str, dict] = {}       # slug -> readlist row (new or already external)
        sent: dict[str, list[dict]] = collections.defaultdict(list)

        def add(slug, path, url, title, published, read, words):
            nonlocal nxt
            if slug in on_list:
                return on_list[slug]
            r = {"n": str(nxt), "slice": "", "pass": "external", "tier": "instrument", "iso3": iso,
                 "kind": "raw", "slug": slug, "read": read, "path": path, "url": url, "title": title,
                 "published": published, "places": iso, "why": "external", "terms": "", "hits": "",
                 "words": str(words)}
            nxt += 1
            rl.append(r)
            on_list[slug] = r
            return r

        for c in live[iso]:
            base = {f: c.get(f, "") for f in LEDGER_FIELDS}
            prim = None
            for d in c["documents"].split():
                h = held.get(ss.norm(d))
                if h and h.get("file", "").replace("\\", "/").startswith("raw/") and h["file"].endswith(".md"):
                    prim = h["file"].replace("\\", "/")
                    break
            if prim:
                slug = os.path.splitext(os.path.basename(prim))[0]
                r = on_list.get(slug)
                if r and r.get("pass") != "external" and os.path.exists(os.path.join(facts_dir, f"{r['n']}.json")):
                    led[c["claim"]] = dict(base, outcome="read-before", slug=slug,
                                           note=f"reading list {r['n']}, already read for this study")
                    continue
                if slug not in docs:
                    fm = front(prim)
                    words = len(fm["text"].split())
                    if words <= WHOLE_MAX:
                        r = add(slug, prim, fm.get("url", ""), fm.get("title", slug), fm.get("published", ""),
                                "whole", words)
                    else:
                        cut = os.path.join(PASSAGES, sid, "passages", slug + ".md")
                        body = (f"# {fm.get('title', slug)}\n\nslug: {slug}\nurl: {fm.get('url', '')}\n"
                                f"published: {fm.get('published', '')}\n"
                                f"Passages only: the paragraphs carrying a study term, of {words} words.\n\n"
                                + study_lib_passages(fm["text"], terms, c))
                        os.makedirs(os.path.dirname(cut), exist_ok=True)
                        with open(cut, "w", encoding="utf-8", newline="\n") as fh:
                            fh.write(body)
                        r = add(slug, os.path.relpath(cut, CORPUS).replace("\\", "/"), fm.get("url", ""),
                                fm.get("title", slug), fm.get("published", ""), "passages", len(body.split()))
                    docs[slug] = r
            else:
                rec = recs.get(c["source"])
                if not rec:
                    led[c["claim"]] = dict(base, outcome="open", note="no database record held")
                    continue
                slug = rec["slug"]
                r = on_list.get(slug)
                if r and r.get("pass") != "external" and os.path.exists(os.path.join(facts_dir, f"{r['n']}.json")):
                    led[c["claim"]] = dict(base, outcome="read-before", slug=slug,
                                           note=f"reading list {r['n']}, the record already read for this study")
                    continue
                if slug not in docs:
                    cut = os.path.relpath(os.path.join(PASSAGES, sid, "passages", "external", iso, slug + ".md"),
                                          CORPUS).replace("\\", "/")
                    if r:   # an arrival closed unread: pointed at the country's lines instead
                        r.update(read="passages", path=cut)
                    else:
                        r = add(slug, cut, rec["url"], f"{rec['title']} ({rec['publisher']})",
                                rec["published"], "passages", 0)
                    docs[slug] = r
            led[c["claim"]] = dict(base, outcome="open", slug=slug, note="")
            sent[slug].append(c)

        if not sent:
            continue
        # The database record's lines for this country and study, each with its claim id.
        for src, rec in recs.items():
            if rec["slug"] in sent:
                cut = os.path.join(PASSAGES, sid, "passages", "external", iso, rec["slug"] + ".md")
                lines = [f"# {rec['title']} — {rec['publisher']}", "",
                         f"slug: {rec['slug']}", f"url: {rec['url']}", f"published: {rec['published']}",
                         f"Passages only: the record's lines for {countries[iso]['name']} ({iso}) that "
                         f"bear on this study, latest round only. Each line: claim id | round | "
                         f"question | answer | name | year | link | whose statement.", ""]
                for c in sent[rec["slug"]]:
                    lines.append(" | ".join([c["claim"], c["survey_year"] or "-", c["question"],
                                             c["status"] or "-", c["name"] or "-", c["year"] or "-",
                                             c["url"] or (c["documents"].split() or ["-"])[0],
                                             c["basis"]]))
                os.makedirs(os.path.dirname(cut), exist_ok=True)
                with open(cut, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write("\n".join(lines) + "\n")
                on_list[rec["slug"]]["words"] = str(sum(len(x.split()) for x in lines))
        study_lib.write_csv(rl_path, study_lib.READLIST_FIELDS, rl)
        calls.append((iso, [(docs[s], sent[s]) for s in sent]))
        made["countries"] += 1
        made["documents"] += len(sent)
        made["claims"] += sum(len(v) for v in sent.values())

    write_ledger(sid, led)
    os.makedirs(out_dir, exist_ok=True)
    for i in range(0, len(calls), per_call):
        chunk = calls[i:i + per_call]
        with open(os.path.join(out_dir, f"{sid}-{i // per_call + 1:02d}.md"), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(prompt(sid, chunk))
    tally = collections.Counter(r["outcome"] for r in led.values())
    print(f"{sid}: {len(claims)} claims; {dict(tally)}; {made['claims']} sent in {made['documents']} "
          f"documents, {made['countries']} countries, {-(-len(calls) // per_call)} calls -> {out_dir}")
    return 0


def study_lib_passages(text: str, terms: re.Pattern, c: dict) -> str:
    """The study's term passages, as `study-select.py` cuts a long document."""
    return SELECT.passages(text, terms)


def prompt(sid: str, chunk: list) -> str:
    out = [f"# External claims: study `{sid}`", "",
           "Read and follow `C:\\CORPUS\\maturity\\documentation\\drafter-brief.md`, with what follows "
           "in place of its *What you are given* step 3 and its reading rule. Read "
           f"`maturity/{sid}/study.json` and the study file it names first.", "",
           "**What this call is.** A global database (the World Bank's GovTech survey, its Statistical "
           "Performance Indicators or World Development Indicators, Carnegie's Africa Technology Policy "
           "Tracker, UNCTAD's Cyberlaw Tracker, ITU's ICT Regulatory Tracker, Open Data Watch's ODIN) "
           "made a claim about a country. Each claim below has an id and the document to check it in: "
           "the primary itself where we hold it, else the country's lines of the database record.", "",
           "**For each document**, read it (`whole`: `C:\\OSINT\\` + path; `passages`: `C:\\CORPUS\\` + "
           "path) and open the country's `maturity/" + sid + "/evidence/{ISO3}/evidence.csv`. Then:",
           "",
           "- **A primary**: record what the primary itself states on the study's aspects, as the brief "
           "says. The claim only tells you where to look.",
           "- **The database record**: a claim is a fact only where its answer states something one of the "
           "study's aspects can hold, in that aspect's closed values (a census year, a law in force, a "
           "system in use, a policy adopted). The `fact` sentence says whose statement it is: \"The "
           "government told the World Bank's GovTech survey (2025) that...\", \"The World Bank's SPI "
           "lists...\", \"Carnegie's tracker lists...\", \"ITU's regulatory tracker records...\". A "
           "bare score (`1`, `0.67`, an element score) states nothing on its own: it is a fact only "
           "where the line names what it scores (a census and its years, a named system). `as_of` is "
           "the year the stated thing was true (a census's own year, a law's year); where the line "
           "gives none, the survey round's year, and say so in the fact.",
           "- **Skip what is held**: a claim `evidence.csv` already states, from any source, is "
           "`nothing: held as {row_id}`. A claim on something the study does not assess is "
           "`nothing: {why}` in a few words.",
           "- **A primary outranks a database.** A survey round's year stands for that year's end, so "
           "a database's \"no\" would outrank an earlier dated launch: where `evidence.csv` holds a "
           "row from a primary showing the thing exists, the claim is `nothing: contradicted by "
           "{row_id}`. A \"yes\" whose link is a statistics office, a third-party platform or a home "
           "page, not the thing asked about, is `nothing: {what the link is}`. A database's \"no\" is "
           "never a fact: answer it `nothing: a database's no`.",
           "",
           "**Add to each facts file a `claims` map** answering every claim id sent with that document: "
           "`\"fact\"` where a fact you wrote carries it, else `\"nothing: ...\"`. Every id gets an answer.",
           "",
           "Write `maturity/" + sid + "/evidence/{ISO3}/facts/{n}.json` per document, as the brief "
           "says, plus the `claims` map. Do nothing else.", ""]
    for iso, docs in chunk:
        out.append(f"## {iso}")
        out.append("")
        for r, cs in docs:
            out.append(f"- document **{r['n']}** (`{r['read']}`, {r['words']} words): `{r['path']}` — slug "
                       f"`{r['slug']}`")
            for c in cs:
                bits = [c["question"], c["status"], c["name"], c["year"]]
                out.append(f"  - `{c['claim']}` ({c['source']} {c['survey_year'] or ''}, fit "
                           f"{c['fit']}): " + " | ".join(b for b in bits if b))
        out.append("")
    out.append("Reply in three lines at most: documents read, facts written, claims answered.")
    return "\n".join(out) + "\n"


def screen(sid: str) -> int:
    """Drop a database record's absence facts from the facts files, before --merge."""
    study = study_lib.load(sid)
    absent = {a["key"]: {"none", *a.get("defer", [])} for a in study["aspects"]}
    slugs = {r["slug"] for r in records().values()}
    dropped = 0
    for iso in sorted(os.listdir(os.path.join(study_lib.study_dir(sid), "evidence"))):
        edir = os.path.join(study_lib.study_dir(sid), "evidence", iso)
        rl = os.path.join(edir, "readlist.csv")
        if not os.path.exists(rl):
            continue
        for r in study_lib.read_csv(rl):
            f = os.path.join(edir, "facts", f"{r.get('n')}.json")
            if r.get("slug") not in slugs or not os.path.exists(f):
                continue
            with open(f, encoding="utf-8") as fh:
                doc = json.load(fh)
            keep = [x for x in doc.get("facts") or []
                    if x.get("value") not in absent.get(x.get("aspect"), {"none"})]
            if len(keep) == len(doc.get("facts") or []):
                continue
            dropped += len(doc["facts"]) - len(keep)
            doc["facts"] = keep
            if not keep:
                doc["claims"] = {k: (v if v.lower().startswith("nothing") else
                                     "nothing: a database's no is not the absence the ladder asks for")
                                 for k, v in (doc.get("claims") or {}).items()}
            with open(f, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(doc, fh, ensure_ascii=False, indent=2)
    print(f"{sid}: {dropped} absence fact(s) from a database dropped")
    return 0


def write_ledger(sid: str, led: dict) -> None:
    study_lib.write_csv(ledger_path(sid), LEDGER_FIELDS,
                        sorted(led.values(), key=lambda r: (r["iso3"], r["source"], r["item"], r["claim"])))


def close(sid: str) -> int:
    led = read_ledger(sid)
    missing = collections.Counter()
    for r in led.values():
        if r["outcome"] != "open":   # a closed claim, hand-corrected or not, stays as it is
            continue
        edir = os.path.join(study_lib.study_dir(sid), "evidence", r["iso3"])
        rl = {x["slug"]: x for x in study_lib.read_csv(os.path.join(edir, "readlist.csv")) if x.get("n")}
        doc = rl.get(r["slug"])
        f = os.path.join(edir, "facts", f"{doc['n']}.json") if doc else ""
        if not f or not os.path.exists(f):
            missing["no facts file"] += 1
            continue
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        ans = (data.get("claims") or {}).get(r["claim"])
        if not ans:
            missing["no answer"] += 1
            continue
        if not ans.strip().lower().startswith("nothing"):
            ev = study_lib.read_csv(os.path.join(edir, "evidence.csv"))
            ids = [e["row_id"] for e in ev if e["source_slug"] == r["slug"]]
            r.update(outcome="fact", row_ids=";".join(ids), note="")
        else:
            r.update(outcome="nothing", note=ans.split(":", 1)[-1].strip()[:200])
    write_ledger(sid, led)
    tally = collections.Counter(r["outcome"] for r in led.values())
    print(f"{sid}: {dict(tally)}" + (f"; still open: {dict(missing)}" if missing else ""))
    return 1 if tally["open"] else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("order")
    p = sub.add_parser("plan")
    p.add_argument("id")
    p.add_argument("--per-call", type=int, default=8)
    p.add_argument("--dir", default=os.path.join(PASSAGES, "_external_prompts"))
    sub.add_parser("screen").add_argument("id")
    c = sub.add_parser("close")
    c.add_argument("id")
    a = ap.parse_args(argv)
    if a.cmd == "order":
        return order()
    if a.cmd == "plan":
        return plan(a.id, a.per_call, a.dir)
    if a.cmd == "screen":
        return screen(a.id)
    return close(a.id)


if __name__ == "__main__":
    sys.exit(main())
