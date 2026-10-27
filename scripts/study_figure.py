#!/usr/bin/env python3
r"""study_figure.py — a first-pass study of a measure the reference file holds: carried, counted, written.

    python scripts/study-figure.py schoolinternet carry
    python scripts/study-figure.py schoolinternet ladder --as-at 2026-09-30
    python scripts/study-figure.py schoolinternet write
    (each with --dry: the counts, nothing written)

`maturity/documentation/first-pass-batch.md`. The Capacity batch of 2026-10-16 held three measure
rows whose figure `reference/measures.csv` carries, so they are staged as
`study-ictproduction-*.py` staged ICT production, and one module serves the three:

- **carry**: one fact per country and year from `FROM`, or the country's latest where it has none
  since, filed under `ref:{dataset}@{release}` (`study_lib.reference_held`). A facts file already
  there is left alone. Run it after `study-select.py` and before the drafters.
A figure whose frame direction is `lower` (the gender gap, the Inclusion batch of 2026-10-16) sets
all five stages from four lines and has no condition: `lower` and `cond: None` in `FIGURES`.

- **ladder**: **one figure sets stages 1 to 4**, the latest for `FROM` or later and by the as-at,
  against the frame's own three cuts (`lookups/maturity-measures.csv`), fixed and not redrawn as
  quintiles. **Stage 5 adds the frame's condition**, a drafter's fact from the last three years,
  counted only where the figure has cleared the top line: it is a condition beside the figure, not a
  step beyond it, so method §3.3 does not apply to it. `corrections.csv` is applied first, once.
- **write**: arithmetic and the drafters' own sentences, linked whole: the latest figure, the years
  before it, the distance to the next line, and any condition fact.

Exit: 0 written, 2 the study or the reference file cannot be read.
"""
from __future__ import annotations

import argparse
import calendar
import collections
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maturity_words  # noqa: E402
import study_lib  # noqa: E402

FROM = 2023                 # a figure for this year or later sets a stage; the window, read by year
SERIES_FROM = 2021          # the years carried and written beside the latest
COND_FROM = "2023-10"       # the condition's three-year window

# Per study: the dataset, the figure's aspect and the condition's (key, value), the frame's three
# cuts, and the words. `fact` and `fig` take {country}, {v} and {y}.
FIGURES = {
    "schoolinternet": dict(
        owner="UNESCO Institute for Statistics", dataset="uis-4a1-secondary-internet", sub="schools", cls="schoolinternet",
        figure="internet", cond=("curriculum", "compulsory"), lines=(17.0, 33.0, 50.0),
        source="UNESCO's SDG 4.a.1 series",
        fact="{v} per cent of secondary schools in {country} had internet for teaching in {y}, by UNESCO's SDG 4.a.1 series.",
        fig="{v} per cent of secondary schools had internet for teaching",
        unit="per cent of secondary schools", what="secondary schools with internet for teaching",
        cond_none="No source found since October 2023 says digital literacy or computing is a compulsory subject in the national secondary curriculum.",
        cond_short="and digital literacy or computing is compulsory in the secondary curriculum",
        cond_low="The curriculum is asked about only once half of secondary schools have internet for teaching, so with {link} none was looked for in this first pass.",
        caveat="The figure counts schools with a connection used for teaching, not how well it serves them or what is taught."),
    "stemgraduates": dict(
        owner="UNESCO Institute for Statistics", dataset="uis-stem-graduates", sub="graduates", cls="stemgraduates",
        figure="stem", cond=("nren", "service"), lines=(13.0, 27.0, 40.0),
        source="UNESCO's tertiary graduates series",
        fact="Graduates in science, technology, engineering and mathematics were {v} per cent of tertiary graduates in {country} in {y}, by UNESCO's series.",
        fig="STEM graduates were {v} per cent of tertiary graduates",
        unit="per cent of tertiary graduates", what="STEM graduates as a share of tertiary graduates",
        cond_none="No source found since October 2023 says a national research and education network is in service connecting the public universities.",
        cond_short="and a research and education network connects the public universities",
        cond_low="A research and education network is asked about only once STEM graduates reach 40 per cent, so with {link} none was looked for in this first pass.",
        caveat="The figure counts graduates in science, technology, engineering and mathematics, ICT among them; it says nothing of where they find work."),
    "ictjobs": dict(
        owner="International Labour Organization", dataset="ilostat-isic-j-employment", sub="ictjobs", cls="ictjobs",
        figure="jobs", cond=("youth", "low"), lines=(0.3, 0.6, 1.0),
        source="ILOSTAT's labour force series",
        fact="Information and communication employed {v} per cent of all workers in {country} in {y}, by ILOSTAT's labour force series.",
        fig="information and communication employed {v} per cent of all workers",
        unit="per cent of employment", what="employment in information and communication",
        cond_none="No source found since October 2023 gives youth unemployment of 14 per cent or less on the national labour force survey.",
        cond_short="and youth unemployment is 14 per cent or less",
        cond_low="Youth unemployment is asked about only once information and communication employs 1 per cent of workers, so with {link} none was looked for in this first pass.",
        caveat="The figure counts all employment in publishing, broadcasting, telecommunications and IT services, not graduates alone."),
    "gendergap": dict(
        owner="International Telecommunication Union", dataset="itu-internet-use-gender-gap", sub="gender", cls="gendergap",
        figure="gap", cond=None, lines=(30.0, 20.0, 10.0, 2.0), lower=True,
        source="ITU's internet use series by sex",
        fact="The gender gap in internet use in {country} was {v} per cent in {y}, by ITU's internet use series by sex.",
        fig="the gender gap in internet use was {v} per cent",
        unit="per cent", what="the gender gap in internet use",
        caveat="The gap is men's rate of internet use less women's, as a share of men's; below zero, women's use is the higher.",
        reading="It measures the difference between women and men, not how many use the internet: a country where few people are online "
                "stands high if women and men are online alike, and one where most are online stands low if women lag."),
    "ruralelectrification": dict(
        owner="World Bank", dataset="wdi-elc-accs-rural", sub="rural", cls="ruralpower",
        figure="access", cond=None, lines=(27.0, 53.0, 80.0, 95.0),
        source="the World Bank's rural electricity access series",
        fact="{v} per cent of rural people in {country} had electricity in {y}, by the World Bank's rural electricity access series.",
        fig="{v} per cent of rural people had electricity",
        unit="per cent of rural people", what="the share of rural people with electricity",
        caveat="The figure counts rural people with any electricity, from the grid or off it, not how reliable or affordable it is.",
        reading="The series is the one Tracking SDG7 publishes, built from household surveys and modelled between them, so a "
                "country's own survey can give a different figure. The 80 per cent line is the Agenda 2063 figure for "
                "households, applied here to rural people, and 95 per cent is universal access."),
}


def clears(c: dict, figure: float, line: float) -> bool:
    """Whether a figure is on the right side of a line: at or above it, or at or below for a `lower` figure."""
    return figure <= line if c.get("lower") else figure >= line


def last_day(as_of: str) -> dt.date:
    p = [int(x) for x in as_of.split("-")]
    if len(p) == 1:
        return dt.date(p[0], 12, 31)
    if len(p) == 2:
        return dt.date(p[0], p[1], calendar.monthrange(p[0], p[1])[1])
    return dt.date(*p)


def num(value: str) -> float:
    return float(value.split(":", 1)[1])


def fmt(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".") if x < 10 else f"{x:.1f}".rstrip("0").rstrip(".")


def link(url: str, words: str) -> str:
    return f"[{words.replace('[', '(').replace(']', ')')}](<{url}>)"


def correct(rows: list[dict], fixes: list[dict]) -> tuple[list[dict], int]:
    by_id = {f"{f['iso3']}-{f['n']}": f for f in fixes}
    out, changed = [], 0
    for r in rows:
        f = by_id.get(r["row_id"])
        if f and f["action"] == "removed":
            changed += 1
            continue
        if f and f["action"].startswith("revalued: ") and r["value"] != f["action"].split(": ", 1)[1]:
            r, changed = {**r, "value": f["action"].split(": ", 1)[1]}, changed + 1
        out.append(r)
    return out, changed


# ---- carry -------------------------------------------------------------------------------------

def carry(sid: str, dry: bool) -> int:
    c = FIGURES[sid]
    study_lib.load(sid)
    slugs, urls = study_lib.reference_held()
    held = [r for r in study_lib.read_csv(os.path.join(study_lib.CORPUS, "reference", "measures.csv"))
            if r["dataset"] == c["dataset"]]
    names = study_lib.countries()
    base = os.path.join(study_lib.study_dir(sid), "evidence")
    count: collections.Counter = collections.Counter()
    for iso in sorted(names):
        mine = sorted((r for r in held if r["iso3"] == iso), key=lambda r: r["year"])
        mine = [r for r in mine if int(r["year"]) >= SERIES_FROM] or mine[-1:]
        if not mine:
            continue
        slug = f"ref:{c['dataset']}@{mine[-1]['release']}"
        if slug not in slugs:
            raise study_lib.StudyError(f"{slug} is not a reference study_lib holds")
        facts = [{"sub_indicator": c["sub"], "aspect": c["figure"], "value": f"official:{r['value']}",
                  "fact": c["fact"].format(country=names[iso]["name"], v=fmt(float(r["value"])), y=r["year"]),
                  "as_of": r["year"], "date_precision": "year", "system": c["source"], "class": c["cls"]}
                 for r in mine]
        count["countries"] += 1
        count["figures"] += len(facts)
        path = os.path.join(base, iso, "readlist.csv")
        rows = study_lib.read_csv(path) if os.path.exists(path) else []
        n = next((str(r["n"]) for r in rows if r.get("slug") == slug), "")
        if not n:
            n = str(max([int(r["n"]) for r in rows if str(r.get("n") or "").isdigit()] or [0]) + 1)
            rows.append({"n": n, "slice": "", "pass": "carried", "tier": "", "iso3": iso,
                         "kind": "raw", "slug": slug, "read": "", "path": "reference/measures.csv",
                         "url": urls[slug], "title": c["source"][0].upper() + c["source"][1:],
                         "published": mine[-1]["release"], "places": iso, "why": "carried",
                         "terms": "", "hits": 0, "words": 0})
            if not dry:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                study_lib.write_csv(path, study_lib.READLIST_FIELDS, rows)
        out = os.path.join(base, iso, "facts", f"{n}.json")
        if dry or os.path.exists(out):
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"slug": slug, "facts": facts,
                       "systems": [{"system": c["source"][0].upper() + c["source"][1:], "country_label": names[iso]["name"],
                                    "class": c["cls"], "platform": "", "owner": c["owner"], "tiers": ""}],
                       "note": "carried from reference/measures.csv; no document opened"},
                      fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    print(f"study-figure {sid} carry: countries: {count['countries']}, figures: {count['figures']}"
          + (" (dry run, nothing written)." if dry else "."))
    return 0


def cleared(sid: str) -> list[str]:
    """The countries whose latest figure, for `FROM` or later, clears the top line: the only
    ones where the condition can move a stage, so the only ones read."""
    c = FIGURES[sid]
    last: dict[str, dict] = {}
    for r in study_lib.read_csv(os.path.join(study_lib.CORPUS, "reference", "measures.csv")):
        if r["dataset"] == c["dataset"] and (r["iso3"] not in last or r["year"] > last[r["iso3"]]["year"]):
            last[r["iso3"]] = r
    return sorted(i for i, r in last.items() if int(r["year"]) >= FROM and clears(c, float(r["value"]), c["lines"][-1]))


# ---- ladder ------------------------------------------------------------------------------------

def stage(c: dict, rows: list[dict], as_at: dt.date) -> dict:
    k, lines = c["figure"], c["lines"]
    ck, cv = c["cond"] or (None, None)
    blank = {k: "", **({ck: ""} if ck else {})}

    def when(r: dict) -> dt.date:
        d = last_day(r["as_of"])
        # A reference series is cited by its release date: a year it covers stands for the as-at.
        published = r["source_slug"].rsplit("@", 1)[-1] if r["source_slug"].startswith("ref:") \
            else r["source_slug"][:10]
        if (d > as_at and r["date_precision"] != "day" and published <= as_at.isoformat()
                and r["as_of"] <= as_at.isoformat()[:len(r["as_of"])]):
            return as_at
        return d
    if not [r for r in rows if r["aspect"] == k]:
        return {"stage": "no evidence", **blank, "sources": [], "gaps": f"Nothing found gives {c['what']}."}
    live = [(when(r), r) for r in rows if r["aspect"] == k and r["as_of"]
            and dt.date(FROM, 1, 1) <= when(r) <= as_at]
    if not live:
        return {"stage": "unplaced", **blank, "sources": [],
                "gaps": f"No figure for {FROM} or later has been found for {c['what']}."}
    _, best = max(live, key=lambda p: (p[0], p[1]["source_slug"].startswith("ref:"), p[1]["row_id"]))
    figure = num(best["value"])
    up = sum(1 for line in lines if clears(c, figure, line))
    if not ck:
        gap = ("All four lines are passed." if up == len(lines) else
               "" if up == 0 else
               f"The latest figure, {fmt(figure)} {c['unit']} for {best['as_of'][:4]}, is above {fmt(lines[up])}.")
        return {"stage": str(up + 1), k: best["value"], "sources": [best["row_id"]], "gaps": gap}
    conds = sorted(((when(r), r) for r in rows if r["aspect"] == ck and r["value"] == cv and r["as_of"]
                    and last_day(COND_FROM) <= last_day(r["as_of"]) and when(r) <= as_at), key=lambda p: p[0])
    if up == len(lines) and conds:
        return {"stage": "5", k: best["value"], ck: cv, "sources": [best["row_id"], conds[-1][1]["row_id"]],
                "gaps": "All four questions are answered."}
    if up == len(lines):
        gap = c["cond_none"]
    elif up == 0:
        gap = ""
    else:
        gap = f"The latest figure, {fmt(figure)} {c['unit']} for {best['as_of'][:4]}, is below {fmt(lines[up])}."
    return {"stage": str(up + 1), k: best["value"], ck: "", "sources": [best["row_id"]], "gaps": gap}


def ladder(sid: str, as_at_s: str, dry: bool) -> int:
    c = FIGURES[sid]
    study_lib.load(sid)
    as_at = dt.date.fromisoformat(as_at_s)
    here = study_lib.study_dir(sid)
    base = os.path.join(here, "evidence")
    fixes = study_lib.read_csv(os.path.join(here, "corrections.csv"))
    aspects = (c["figure"], c["cond"][0]) if c["cond"] else (c["figure"],)
    test, count = [], {}
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "evidence.csv")
        rows = study_lib.read_csv(path) if os.path.exists(path) else []
        rows, changed = correct(rows, [f for f in fixes if f["iso3"] == iso])
        if changed and not dry:
            study_lib.write_csv(path, study_lib.EVIDENCE_FIELDS, rows)
        cell = stage(c, rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at, c["sub"]))
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        line = {"sub_indicator": c["sub"], "stage": cell["stage"], **{a: cell[a] for a in aspects},
                "cap": "", "flags": "", "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": f"First pass: counted from the four questions by study-figure.py {sid}."}
        test.append({"iso3": iso, **{x: line[x] for x in ("stage", *aspects, "stage_sources")}})
        if dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not dry:
        study_lib.write_csv(os.path.join(here, "ladder-test.csv"), ["iso3", "stage", *aspects, "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{x}: {count[x]}" for x in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if dry else "."))
    return 0


# ---- write -------------------------------------------------------------------------------------

def listed(parts: list[str]) -> str:
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def figure_paragraph(c: dict, name: str, rows: list[dict], best: dict) -> str:
    series = sorted((r for r in rows if r["source_slug"] == best["source_slug"]), key=lambda r: r["as_of"])
    figure, year, url = num(best["value"]), best["as_of"][:4], best["url"]
    out = [f"**{name}.**", f"In {year}, {link(url, c['fig'].format(v=fmt(figure)))}, by {c['source']}."]
    before = [r for r in series if str(SERIES_FROM) <= r["as_of"] < best["as_of"]]
    if before:
        steps = listed([f"{fmt(num(r['value']))} in {r['as_of'][:4]}" for r in before])
        out.append(f"The same series {link(url, 'gives ' + steps)}.")
        moved = figure - num(before[0]["value"])
        how = "has barely moved" if abs(moved) < 0.005 else f"{'rose' if moved > 0 else 'fell'} by {fmt(abs(moved))} points"
        out.append(f"Since {before[0]['as_of'][:4]} the figure {how}.")
    else:
        out.append("The series gives no figure for the years just before, so no source found says whether it is rising or falling.")
    ahead = [line for line in c["lines"] if not clears(c, figure, line)]
    if ahead:
        out.append(f"It is {fmt(abs(ahead[0] - figure))} points {'above' if c.get('lower') else 'short of'} {fmt(ahead[0])}, the next line.")
    else:
        out.append(f"At {fmt(c['lines'][-1])} or {'less' if c.get('lower') else 'more'}, it is past the study's highest line for the figure.")
    out.append(f"The study's lines are {listed([fmt(x) for x in c['lines']])} {c['unit']}, "
               f"the frame's own cuts, and the latest figure for {FROM} or later sets the stage, so a "
               f"{'rise is a rise' if c.get('lower') else 'fall is a fall'}.")
    out.append(c["caveat"])
    if c.get("reading"):
        out.append(c["reading"])
    return " ".join(out)


def cond_paragraph(c: dict, name: str, conds: list[dict], top: bool, url: str) -> str:
    out = [f"**{name}.**"]
    if conds:
        out += [link(r["url"], r["fact"].rstrip(".")) + "." for r in conds[:4]]
    elif top:
        out.append(c["cond_none"] + f" The figure {link(url, 'alone')} set the stage.")
    else:
        out.append(c["cond_low"].format(link=link(url, "the figure below that line")))
    return " ".join(out)


def write_one(sid: str, study: dict, iso: str, country: str, dry: bool) -> str:
    c = FIGURES[sid]
    k = c["figure"]
    ck, cv = c["cond"] or (None, None)
    names = {a["key"]: a["name"] for a in study["aspects"]}
    here = study_lib.study_dir(sid)
    folder = os.path.join(here, "evidence", iso)
    try:
        with open(os.path.join(folder, "stage.json"), encoding="utf-8") as fh:
            cell = json.load(fh)["cells"][0]
    except OSError:
        raise study_lib.StudyError(f"{iso}: no stage.json; run the ladder first")
    path = os.path.join(folder, "evidence.csv")
    rows = study_lib.read_csv(path) if os.path.exists(path) else []
    rows, _ = correct(rows, [f for f in study_lib.read_csv(os.path.join(here, "corrections.csv")) if f["iso3"] == iso])
    figs = [r for r in rows if r["aspect"] == k]
    srcs = cell["stage_sources"].split(";")
    conds = sorted((r for r in rows if r["aspect"] == ck and r["value"] == cv and r["as_of"] >= COND_FROM),
                   key=lambda r: r["as_of"], reverse=True)
    conds = [r for r in conds if r["row_id"] in srcs] + [r for r in conds if r["row_id"] not in srcs]
    rl = os.path.join(folder, "readlist.csv")
    urls = {r["slug"]: r["url"] for r in study_lib.read_csv(rl)} if os.path.exists(rl) else {}
    noted, seen = [], set()
    sp = os.path.join(folder, "systems.csv")
    for s in study_lib.read_csv(sp) if os.path.exists(sp) else []:
        url = urls.get(s["sources"].split(";")[0], "")
        words = s["system"].strip()
        if s["class"] == "other" and url and words and words.lower() not in seen and len(noted) < 6:
            seen.add(words.lower())
            noted.append(link(url, words))
    parts = [f"# {country}", "", f"## {study['sub_indicators'][0]['label']}", ""]
    if cell["stage"].isdigit():
        best = next(r for r in figs if r["row_id"] == srcs[0])
        figure, year = num(best["value"]), best["as_of"][:4]
        top = clears(c, figure, c["lines"][-1])
        parts += [figure_paragraph(c, names[k], figs, best), ""]
        if ck:
            parts += [cond_paragraph(c, names[ck], conds, top, best["url"]), ""]
        lead = c["fig"].format(v=fmt(figure))
        short = f"In {year}, {lead}" + (f", {c['cond_short']}." if cell["stage"] == "5" and ck else ".")
        ahead = [line for line in c["lines"] if not clears(c, figure, line)]
        held = (f"No figure of {fmt(ahead[0])} {c['unit']} or {'less' if c.get('lower') else 'more'} is held." if ahead
                else cell["gaps"] if cell["stage"] != "5" else "Nothing further is asked of this indicator.")
    else:
        old = sorted(figs, key=lambda r: r["as_of"])
        held = cell["gaps"]
        if old:
            held += f" The latest held is {fmt(num(old[-1]['value']))}, for {old[-1]['as_of'][:4]}."
        short = f"No figure for {c['what']} has been found for {FROM} or later, so no stage is set."
    short = short[0].upper() + short[1:]
    parts += [maturity_words.ALSO_ON_FILE_LABEL + ". " + ("; ".join(noted) + "." if noted else maturity_words.NONE_FOUND), "",
              maturity_words.NOT_FOUND_LABEL + ". " + held, ""]
    if not dry:
        out = study_lib.out_dir(sid)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, iso + ".md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(maturity_words.rewrite("\n".join(parts)))
        with open(os.path.join(folder, "short.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({c["sub"]: maturity_words.rewrite(short)}, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    return cell["stage"]


def write(sid: str, dry: bool) -> int:
    study = study_lib.load(sid)
    names = study_lib.countries()
    for iso in sorted(names):
        write_one(sid, study, iso, names[iso]["name"], dry)
    print(f"study-figure {sid} write: {len(names)} countries" + (" (dry run, nothing written)." if dry else " written."))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Carry, stage or write a first-pass figure study.")
    ap.add_argument("study", choices=sorted(FIGURES))
    ap.add_argument("step", choices=("carry", "ladder", "write", "cleared"))
    ap.add_argument("--as-at", help="YYYY-MM-DD, for ladder")
    ap.add_argument("--dry", action="store_true", help="the counts, nothing written")
    a = ap.parse_args(argv)
    try:
        if a.step == "carry":
            return carry(a.study, a.dry)
        if a.step == "ladder":
            if not a.as_at:
                ap.error("ladder needs --as-at")
            return ladder(a.study, a.as_at, a.dry)
        if a.step == "cleared":
            print(" ".join(cleared(a.study)))
            return 0
        return write(a.study, a.dry)
    except study_lib.StudyError as e:
        print(f"study-figure {a.study}: {e}")
        return 2
