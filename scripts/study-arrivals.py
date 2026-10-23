#!/usr/bin/env python3
r"""study-arrivals.py — BUILD stage 4c's arrivals, read as news and read once across studies.

    cd scripts/.workroot
    python scripts/study-arrivals.py triage           close what is not read: instruments, pre-window
    python scripts/study-arrivals.py plan --cap 20    the shared calls -> maturity/_batch/arrivals/calls.json
    python scripts/study-arrivals.py prompts DIR      one self-contained drafter file per call, DIR/{n}.md
    python scripts/study-arrivals.py fan              answers -> each study's facts files; empty ones closed

`MATURITY-UPDATE.md` → *Stage 4c*. `study-select.py {id} --new` lists the arrivals one study at
a time; a story four studies admit is one document, so it is read once, by one drafter who
answers each study's questions for each country listed, as the first-pass batches read theirs
(`maturity/documentation/first-pass-batch.md`).

**The useful facts are in news, not in large documents** *(Bill, 2026-10-17)*. `triage` closes
an arrival unread, and says why, where:

- `instrument` — the reading list's `tier` says the document runs past `NEWS_WORDS` in the
  original: a law, a strategy, a report. The rotation opens one for a rung that needs its text;
  stage 4c never does;
- `old`        — published before the three-year window, so it can set no stage;
- `capped`     — `plan --cap N` keeps each country's N best-ranked stories across every study
  (news before the rest of the ranking, a titled story first, the country's own before a
  regional one, then newest), and closes the rest.

`plan` writes `maturity/_batch/arrivals/calls.json`, one entry per call of at most `CALL_DOCS`
stories and `CALL_WORDS` words: `{"stories": [{"key", "slug", "path", "words",
"studies": {id: {ISO3: n}}}]}`. A drafter writes `maturity/_batch/arrivals/{key}.json`,
`{"slug", "studies": {id: {"countries": {ISO3: {"facts", "systems", "note"}}}}}`.

`prompts DIR` writes each call as a file a drafter needs nothing else to act on: the stories,
each study's questions cut from its study file (what is assessed, the questions or aspects and
the ladders) and the sub-indicators, classes and aspect values spelt as `evidence.csv` takes
them. The parent starts one drafter per file.

`fan` writes each part as `maturity/{id}/evidence/{ISO3}/facts/{n}.json`, the shape a country
drafter writes, so `study-profile.py --merge` takes it, and closes an arrival whose part states
no fact as `nothing`. An arrival with a fact stays open for its cell to be reassessed and
closed `fact` or `reassessed`. A facts file already there is left alone.

Exit: 0 done, 1 `fan` found an answer it could not read, 2 a file is wrong.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402
import vault_lib  # noqa: E402

OSINT = vault_lib.ROOT     # run from scripts/.workroot, as study-select.py is: raw/ is read, never written

BATCH = os.path.join(study_lib.CORPUS, "maturity", "_batch", "arrivals")
CALL_DOCS, CALL_WORDS = 5, 12_000
CALL_STUDIES = 6          # question blocks a call carries; a story asked by more is a call alone
WINDOW_YEARS = 3

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def studies() -> list[str]:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "study_update", os.path.join(os.path.dirname(os.path.abspath(__file__)), "study-update.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.studies()


def key_of(slug: str) -> str:
    return hashlib.sha1(slug.encode("utf-8")).hexdigest()[:10]


def window_start(today: dt.date) -> str:
    try:
        return today.replace(year=today.year - WINDOW_YEARS).isoformat()
    except ValueError:      # 29 February
        return today.replace(year=today.year - WINDOW_YEARS, day=28).isoformat()


def open_arrivals(sid: str) -> tuple[list[dict], list[dict], dict]:
    """`(all arrival rows, the open ones, {(iso, n): readlist row})` for one study."""
    path = os.path.join(study_lib.study_dir(sid), "evidence", "arrivals.csv")
    rows = study_lib.read_csv(path)
    lists = {}
    for iso in {r["iso3"] for r in rows if not r.get("outcome")}:
        for r in study_lib.read_csv(os.path.join(study_lib.study_dir(sid), "evidence", iso, "readlist.csv")):
            if r.get("kind") == "raw":
                lists[(iso, str(r["n"]))] = r
    return rows, [r for r in rows if not r.get("outcome")], lists


def close(sid: str, rows: list[dict], shut: dict[tuple, str], today: str) -> None:
    for r in rows:
        why = shut.get((r["iso3"], str(r["n"])))
        if why and not r.get("outcome"):
            r.update(outcome=why, closed=today)
    study_lib.write_csv(os.path.join(study_lib.study_dir(sid), "evidence", "arrivals.csv"),
                        study_lib.ARRIVAL_FIELDS, rows)


def triage(today: dt.date) -> int:
    since, counts = window_start(today), collections.Counter()
    for sid in studies():
        rows, todo, lists = open_arrivals(sid)
        shut = {}
        for r in todo:
            src = lists.get((r["iso3"], str(r["n"])))
            if src is None:
                print(f"study-arrivals: {sid} {r['iso3']} {r['n']}: not on the reading list")
                return 2
            if src.get("tier") != "news":
                shut[(r["iso3"], str(r["n"]))] = "instrument"
            elif (src.get("published") or "0000") < since:
                shut[(r["iso3"], str(r["n"]))] = "old"
        if shut:
            close(sid, rows, shut, today.isoformat())
        counts.update(shut.values())
        counts["open"] += len(todo) - len(shut)
    print(f"study-arrivals: triage - {counts['instrument']} instruments and {counts['old']} pre-window "
          f"closed unread; {counts['open']} news arrivals open")
    return 0


def raw_path(src: dict) -> str:
    """The `raw/` path of a listed document, relative to the OSINT root, whichever form its
    row points at: a news story is read whole even where a regional list cut it to passages."""
    if src.get("read") == "whole":
        return src["path"]
    year = (src.get("published") or "")[:4]
    cand = f"raw/{year}/{src['slug']}.md"
    if os.path.exists(os.path.join(OSINT, cand)):
        return cand
    hits = glob.glob(os.path.join(OSINT, "raw", "*", glob.escape(src["slug"]) + ".md"))
    if hits:
        return os.path.relpath(hits[0], OSINT).replace("\\", "/")
    raise FileNotFoundError(f"{src['slug']}: no raw file for {src['path']}")


def plan(cap: int, today: dt.date) -> int:
    stories: dict[str, dict] = {}
    per_iso: dict[str, dict[str, tuple]] = collections.defaultdict(dict)
    held = {}
    for sid in studies():
        rows, todo, lists = open_arrivals(sid)
        held[sid] = rows
        for r in todo:
            src = lists[(r["iso3"], str(r["n"]))]
            why = src.get("why", "").split("+")
            rank = (not src.get("terms") or "regional" in why, -int(src.get("hits") or 0) // 3,
                    "".join(chr(255 - ord(c)) for c in (src.get("published") or "")))
            st = stories.setdefault(src["slug"], {"key": key_of(src["slug"]), "slug": src["slug"],
                                                  "src": src, "studies": {}})
            st["studies"].setdefault(sid, {})[r["iso3"]] = int(r["n"])
            best = per_iso[r["iso3"]].get(src["slug"])
            per_iso[r["iso3"]][src["slug"]] = min(best, rank) if best else rank
    keep = {(iso, slug) for iso, by in per_iso.items()
            for slug, _ in sorted(by.items(), key=lambda kv: kv[1])[:cap or None]}
    shut = collections.defaultdict(dict)
    for slug, st in list(stories.items()):
        for sid, isos in list(st["studies"].items()):
            for iso in list(isos):
                if (iso, slug) not in keep:
                    shut[sid][(iso, str(isos.pop(iso)))] = "capped"
            if not isos:
                del st["studies"][sid]
        if not st["studies"]:
            del stories[slug]
    for sid, s in shut.items():
        close(sid, held[sid], s, today.isoformat())
    out = []
    for st in stories.values():
        st["path"] = raw_path(st.pop("src"))
        src_words = 0
        try:
            with open(os.path.join(OSINT, st["path"]), encoding="utf-8", errors="replace") as fh:
                src_words = len(fh.read().split())
        except OSError:
            print(f"study-arrivals: {st['slug']}: {st['path']} cannot be read")
            return 2
        st["words"] = src_words
        out.append(st)
    # stories asking the same studies sit together, and a call carries few question blocks
    out.sort(key=lambda s: (sorted(s["studies"]), s["slug"]))
    calls, cur, words, asked = [], [], 0, set()
    for st in out:
        wider = asked | set(st["studies"])
        if cur and (len(cur) >= CALL_DOCS or words + st["words"] > CALL_WORDS
                    or len(wider) > CALL_STUDIES):
            calls.append({"stories": cur})
            cur, words, wider = [], 0, set(st["studies"])
        cur.append(st)
        words, asked = words + st["words"], wider
    if cur:
        calls.append({"stories": cur})
    os.makedirs(BATCH, exist_ok=True)
    with open(os.path.join(BATCH, "calls.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(calls, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    readings = sum(len(v) for st in out for v in st["studies"].values())
    print(f"study-arrivals: plan - {len(out)} stories, {readings} study-country readings, "
          f"{len(calls)} calls; {sum(len(v) for v in shut.values())} capped at {cap} a country")
    return 0


RULES = r"""You are a drafter for a Corpus maturity study, reading news that arrived after the study was made. Everything you need is in this file: do not open any study file, brief or reading list. Read the documents named below and no others, opening them all in your first turn. C:\OSINT is read-only: never write, move or delete anything there.

What to record
- A fact is one thing the document itself states that answers one of the study's questions, or settles one of its aspects, for one named country: a value from that aspect's list below. Nothing from another document or from what you know. Skip everything else; most documents state nothing a study asks.
- fact: one English sentence giving what the document states, with its figures and who says so. Quote no more than a few words.
- as_of: when the stated thing was true, YYYY, YYYY-MM or YYYY-MM-DD: the event's date, not the document's. Where none is given, use the document's publication date.
- date_precision: year, month or day.
- system: the system's or instrument's name as the document gives it. class: the sub-indicator's class given below, or the fact is not recorded; a study's other classes are for systems rows, even where the fact is about the body or instrument one names.
- Classify by what the document says a thing does, never by its name. A plan, a pledge, a workshop or a donor's intention is not the thing delivered. Do not stage, summarise or judge.
- systems: the systems the document names for the country (system, country_label, class, platform, owner, tiers; class "other" where it is not the study's own). Keep it short; empty is fine.
- note: one line, why there is no fact where there is none.

A part for one country is {"facts": [...], "systems": [...], "note": ""}; each fact is {"sub_indicator", "aspect", "value", "fact", "as_of", "date_precision", "system", "class"}, sub_indicator, aspect and value spelt exactly as below.

Write with the Write tool only. Create no other file, edit none, delete none, start no agent. Reply in one line: documents read, facts written.
"""
SKIP = re.compile(r"(\d+\.\s*)?(The norm|What (the run|Phase)|Token|Tasks|Boundary|Phase|Search|Sources|Cost)")
NL = "\n"


def questions(sid: str) -> str:
    """One study's questions, cut from its study file, with the values `evidence.csv` takes."""
    study = study_lib.load(sid)
    with open(os.path.join(study_lib.study_dir(sid), os.path.basename(study["study_file"])),
              encoding="utf-8") as fh:
        md = fh.read()
    keep = [x for x in re.split(r"(?m)^## ", md)[1:] if not SKIP.match(x)]
    subs = "; ".join(f'"{s["key"]}" (class "{s["class"]}"' + (
        f', also {", ".join(s["also_assessed"])}' if s.get("also_assessed") else "") + ")"
        for s in study["sub_indicators"])
    def spelt(a: dict) -> str:
        if "facets" in a:
            return "one facet:value pair per fact, from " + "; ".join(
                f'{f}: ' + ", ".join(f'"{f}:{v}"' for v in vs) for f, vs in a["facets"].items())
        if "pattern" in a:
            return f'a value matching {a["pattern"]}'
        if isinstance(a["values"], dict):
            return "; ".join(f'for {sub}: ' + ", ".join(f'"{v}"' for v in vs) for sub, vs in a["values"].items())
        return ", ".join(f'"{v}"' for v in a["values"]) + ("; several joined by ';'" if a.get("multi") else "")

    aspects = NL.join(f'- aspect "{a["key"]}": {spelt(a)}' for a in study["aspects"])
    return (f"### Study {sid}{NL}{NL}sub_indicator: {subs}{NL}{NL}Aspects and their values:{NL}{aspects}{NL}{NL}"
            + NL.join("#### " + x.strip() for x in keep))


def prompts(out: str) -> int:
    calls = json.load(open(os.path.join(BATCH, "calls.json"), encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    blocks, index = {}, []
    for n, c in enumerate(calls, 1):
        used = sorted({sid for st in c["stories"] for sid in st["studies"]})
        docs = []
        for st in c["stories"]:
            lst = "; ".join(f"{sid}: {', '.join(sorted(v))}" for sid, v in sorted(st["studies"].items()))
            source = os.path.join(r"C:\OSINT", *st["path"].split("/"))
            target = os.path.join(BATCH, st["key"] + ".json")
            shape = {"slug": st["slug"], "studies": {"STUDY": {"countries": {"ISO3": "part"}}}}
            docs.append(f"- {source}{NL}  answer for: {lst}{NL}  write {target} as "
                        f"{json.dumps(shape, ensure_ascii=False)}, every listed study and country "
                        f"present (empty lists and a note where nothing is stated)")
        for sid in used:
            if sid not in blocks:
                blocks[sid] = questions(sid)
        body = (RULES + f"{NL}## Your documents (read each once; answer each listed study for each "
                f"listed country, from what it says about that country by name){NL}" + NL.join(docs)
                + f"{NL}{NL}## The questions{NL}{NL}" + (NL + NL).join(blocks[s] for s in used) + NL)
        with open(os.path.join(out, f"{n}.md"), "w", encoding="utf-8", newline=NL) as fh:
            fh.write(body)
        index.append({"n": n, "words": len(body.split()) + sum(st["words"] for st in c["stories"]),
                      "files": [os.path.join(BATCH, st["key"] + ".json") for st in c["stories"]]})
    with open(os.path.join(out, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=0)
    print(f"study-arrivals: prompts - {len(calls)} call files in {out}; "
          f"{sum(i['words'] for i in index):,} words to read in all")
    return 0


DROPPED_FIELDS = ["study", "iso3", "slug", "sub_indicator", "aspect", "value", "fact", "why"]


def checked(sid: str, iso: str, slug: str, facts: list[dict], dropped: list[dict]) -> list[dict]:
    """The facts a study can take: a lone sub-indicator's key is set where the drafter misspelt
    it, and a fact whose aspect or value is off the study's lists is set aside, never merged,
    since one bad value stops `study-profile.py` profiling the country."""
    study = study_lib.load(sid)
    subs = [s["key"] for s in study["sub_indicators"]]
    aspects = {a["key"]: a for a in study["aspects"]}
    keep = []
    for f in facts:
        if f.get("sub_indicator") not in subs and len(subs) == 1:
            f["sub_indicator"] = subs[0]
        a = aspects.get(f.get("aspect", ""))
        why = ("not a sub-indicator" if f.get("sub_indicator") not in subs else
               "not an aspect" if a is None else
               study_lib.value_problem(a, f["sub_indicator"], str(f.get("value", ""))))
        if why:
            dropped.append({"study": sid, "iso3": iso, "slug": slug, "why": why,
                            **{k: str(f.get(k, "")) for k in ("sub_indicator", "aspect", "value", "fact")}})
        else:
            keep.append(f)
    return keep


def classed(sid: str, systems: list[dict]) -> list[dict]:
    """A system the drafter classed outside the study's typology is `other`, or not kept."""
    classes = study_lib.load(sid).get("classes") or []
    out = []
    for x in systems:
        if x.get("class") not in classes:
            if "other" not in classes:
                continue
            x = {**x, "class": "other"}
        out.append(x)
    return out


def fan(today: dt.date) -> int:
    path = os.path.join(BATCH, "calls.json")
    calls = json.load(open(path, encoding="utf-8"))
    bad, written, empty, dropped = [], 0, collections.Counter(), []
    shut = collections.defaultdict(dict)
    for c in calls:
        for st in c["stories"]:
            ans = os.path.join(BATCH, st["key"] + ".json")
            if not os.path.exists(ans):
                continue
            try:
                raw = open(ans, "rb").read()
                try:
                    d = json.loads(raw.decode("utf-8-sig"))
                except UnicodeDecodeError:      # a drafter on Windows sometimes writes cp1252
                    d = json.loads(raw.decode("cp1252"))
            except ValueError as e:
                bad.append(f"{st['key']}: {e}")
                continue
            for sid, isos in st["studies"].items():
                got = ((d.get("studies") or {}).get(sid) or {}).get("countries") or {}
                for iso, n in isos.items():
                    part = got.get(iso) or {"facts": [], "systems": [],
                                            "note": "the drafter returned nothing for this country"}
                    part["facts"] = checked(sid, iso, st["slug"], part.get("facts") or [], dropped)
                    part["systems"] = classed(sid, part.get("systems") or [])
                    f = os.path.join(study_lib.study_dir(sid), "evidence", iso, "facts", f"{n}.json")
                    if not os.path.exists(f):
                        os.makedirs(os.path.dirname(f), exist_ok=True)
                        with open(f, "w", encoding="utf-8", newline="\n") as fh:
                            json.dump({"slug": st["slug"], "facts": part.get("facts") or [],
                                       "systems": part.get("systems") or [], "note": part.get("note", "")},
                                      fh, ensure_ascii=False, indent=1)
                            fh.write("\n")
                        written += 1
                    if not part.get("facts"):
                        shut[sid][(iso, str(n))] = "nothing"
    for sid, s in shut.items():
        rows = study_lib.read_csv(os.path.join(study_lib.study_dir(sid), "evidence", "arrivals.csv"))
        close(sid, rows, s, today.isoformat())
        empty[sid] = len(s)
    if dropped:
        study_lib.write_csv(os.path.join(BATCH, "dropped.csv"), DROPPED_FIELDS, dropped)
    for b in bad:
        print(f"study-arrivals: unreadable answer {b}")
    print(f"study-arrivals: {len(dropped)} facts off their study's lists set aside in dropped.csv")
    print(f"study-arrivals: fan - {written} facts files written, {sum(empty.values())} arrivals closed "
          f"`nothing`")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("triage")
    p = sp.add_parser("plan")
    p.add_argument("--cap", type=int, default=20, help="each country's best N stories, 0 for all")
    q = sp.add_parser("prompts")
    q.add_argument("out", help="the folder the call files are written to")
    sp.add_parser("fan")
    a = ap.parse_args(argv)
    today = dt.date.today()
    try:
        if a.cmd == "triage":
            return triage(today)
        if a.cmd == "plan":
            return plan(a.cap, today)
        if a.cmd == "prompts":
            return prompts(a.out)
        return fan(today)
    except (OSError, KeyError, study_lib.StudyError) as e:
        print(f"study-arrivals: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
