#!/usr/bin/env python3
r"""test_study.py — the maturity-study scripts, on a study small enough to check by eye.

    python scripts/test_study.py

Five scripts share one definition of a study, so the cases are grouped by what would go
wrong unnoticed rather than by file:

- **a reading list that is too short** reads as a country with no evidence, so every route
  into the list is exercised, and so is the one that must not admit: a subject tag alone;
- **a profile that picks the wrong fact** stages a country on it, so newest-wins, the
  facet, multi and preference rules each get a case, and so does the gap that drives search;
- **a gate that opens early** marks every handed-over document as not returned;
- **a lint that passes a capped stage** publishes a stage the study's own rule forbids.

Nothing here touches `raw/`, the share or the mirror: each function under test takes what
it reads as an argument.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import study_lib  # noqa: E402


def load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


select = load("study-select")
profile = load("study-profile")
returned = load("study-returned")
render = load("study-render")
lint = load("lint-study")

fails: list[str] = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
    if not ok:
        print(f"          got {got!r}\n          want {want!r}")
        fails.append(label)


STUDY = {
    "id": "t", "study_file": "maturity-study-t.md",
    "subjects": ["dpi.mis"], "terms": ["HMIS", "SIS", "système d'information sanitaire"],
    "sub_indicators": [{"key": "hmis", "label": "HMIS", "subject": "digital.rural",
                        "text": "Clinics: HMIS", "indicator_id": "digital.rural--clinics-hmis",
                        "class": "hmis"}],
    "classes": ["hmis", "tracker"],
    "aspects": [
        {"key": "governance", "name": "Governance", "role": "qualifier", "window_months": 36,
         "facets": {"owner": ["ministry", "partner"], "finance": ["domestic", "donor"]}},
        {"key": "tiers", "name": "Tiers in use", "role": "coverage", "multi": True,
         "values": ["T1", "T2", "T3", "T4"]},
        {"key": "clinics", "name": "Primary clinics", "role": "coverage",
         "pattern": r"share:\d+%|count:\d+|not-published",
         "prefer": ["share:", "count:", "not-published"]},
        {"key": "last12", "name": "Last twelve months", "role": "qualifier",
         "window_months": 12, "values": ["advancing", "regressing"]},
    ],
    "cap": {"aspect": "governance", "above": 3, "flag": "externally run",
            "all": ["owner:ministry"], "any": ["finance:domestic"]},
    "flags": ["externally run", "advancing"],
}
COUNTRIES = {"KEN": {"name": "Kenya", "regions": {"XEA", "XAF", "XSS"}},
             "CIV": {"name": "Côte d'Ivoire", "regions": {"XWA", "XAF", "XSS"}}}
AS_AT = dt.date(2026, 9, 30)


def ev(rid, aspect, value, as_of, sub="hmis", slug="s1", url="https://a.org/1"):
    return {"row_id": rid, "iso3": rid[:3], "sub_indicator": sub, "aspect": aspect,
            "value": value, "fact": "A stated fact", "as_of": as_of, "date_precision": "year",
            "system": "DHIS2", "class": "hmis", "source_slug": slug, "url": url}


# --------------------------------------------------------------------------- #
print("\nthe study's own vocabulary")
asp = study_lib.aspects(STUDY)
check("an id is minted from its text", study_lib.mint("digital.rural", "Clinics: HMIS"),
      "digital.rural--clinics-hmis")
check("a listed value passes", study_lib.value_problem(asp["last12"], "hmis", "advancing"), "")
check("an unlisted one does not", bool(study_lib.value_problem(asp["last12"], "hmis", "better")), True)
check("a multi value is each part", study_lib.value_problem(asp["tiers"], "hmis", "T1;T4"), "")
check("and fails on one bad part", bool(study_lib.value_problem(asp["tiers"], "hmis", "T1;T9")), True)
check("a facet pair passes", study_lib.value_problem(asp["governance"], "hmis", "owner:ministry"), "")
check("a facet with another facet's value fails",
      bool(study_lib.value_problem(asp["governance"], "hmis", "owner:donor")), True)
check("a pattern value passes", study_lib.value_problem(asp["clinics"], "hmis", "share:62%"), "")
check("a year alone means its last day", study_lib.parse_as_of("2024"), dt.date(2024, 12, 31))
check("a month means its last day", study_lib.parse_as_of("2024-02"), dt.date(2024, 2, 29))
check("anything else is not a date", study_lib.parse_as_of("mid-2024"), None)

print("\nterms")
rx = study_lib.term_regex(STUDY["terms"])
check("an acronym is matched as written", bool(rx.search("the HMIS bulletin")), True)
check("and not inside a lower-case word", bool(rx.search("an analysis of oasis towns")), False)
check("nor as a fragment of a longer token", bool(rx.search("the EHMISv2 platform")), False)
check("a phrase matches without its accents",
      bool(rx.search(study_lib.fold("le Systeme d'information sanitaire"))), True)
check("and with a typographic apostrophe",
      bool(rx.search(study_lib.fold("Système d’information sanitaire"))), True)

print("\ncountry names")


def named(iso, name, text):
    return bool(study_lib.name_regex(iso, {"name": name}).search(study_lib.fold(text)))


check("Sudan is not South Sudan", named("SDN", "Sudan", "clinics in South Sudan report"), False)
check("but is Sudan", named("SDN", "Sudan", "Khartoum, Sudan, reports"), True)
check("Guinea is not Guinea-Bissau", named("GIN", "Guinea", "in Guinea-Bissau the SNIS"), False)
check("nor Equatorial Guinea", named("GIN", "Guinea", "Equatorial Guinea's ministry"), False)
check("Congo is not the DRC by its long name", named("COG", "Congo", "the Democratic Republic of the Congo"), False)
check("nor by its short one", named("COG", "Congo", "DR Congo and Chad"), False)
check("the DRC is found under the names documents use",
      [named("COD", "DR Congo", t) for t in ("in the DRC,", "République démocratique du Congo", "DR Congo")],
      [True, True, True])
check("an acronym alias is matched as written", named("COD", "DR Congo", "the drc-style approach"), False)
check("Niger is not the Niger Delta", named("NER", "Niger", "the Niger Delta states"), False)
check("nor Nigeria", named("NER", "Niger", "Nigeria's DHIS2"), False)
check("Cabo Verde answers to Cape Verde's row", named("CPV", "Cape Verde", "Cabo Verde's SIS"), True)

# --------------------------------------------------------------------------- #
print("\nthe reading list")


def row(slug, places, topics, title="A document", url=""):
    d = {"folder": "raw", "ext": ".md", "slug": slug, "words": 100}
    if url:
        d["url_norm"] = url
    return {"path": f"raw/2025/{slug}.md", "fm": {"title": title, "places": places, "topics": topics,
                                                  "published": "2025-01-01"}, "d": d}


BODIES = {"tagged-hit": "Kenya's HMIS reports monthly.", "tagged-miss": "The school census.",
          "untagged-hit": "Facilities key into the HMIS.", "regional-named": "HMIS use in Kenya rose.",
          "regional-unnamed": "HMIS use rose across the region.", "other-country": "Uganda's HMIS.",
          "reported": "A clinic software launch.", "ivorian": "Le SIS en Côte d’Ivoire."}
INDEX = [row("tagged-hit", ["KEN"], ["dpi.mis"]), row("tagged-miss", ["KEN"], ["dpi.mis"]),
         row("untagged-hit", ["KEN"], ["gov.policy"]), row("regional-named", ["XEA"], []),
         row("regional-unnamed", ["XAF"], []), row("other-country", ["UGA"], ["dpi.mis"]),
         row("reported", ["KEN"], ["dpi.mis"]), row("ivorian", ["XWA"], [])]
INDEX.append({"path": "raw/2025/a.pdf", "fm": {}, "d": {"folder": "raw", "ext": ".pdf", "slug": "a"}})
docs = select.scan(INDEX, lambda r: BODIES[r["d"]["slug"]], rx)
check("binaries are not scanned", "a" in docs, False)
rows, dropped = select.select("KEN", COUNTRIES["KEN"], docs, STUDY["subjects"],
                              {"reported": {"ledger!"}, "tagged-hit": {"considered"}})
got = {r["slug"]: r["why"] for r in rows}
check("a tagged document carrying a term is listed", got.get("tagged-hit"), "subject+considered")
check("a tag alone does not list one", "tagged-miss" in got, False)
check("but it is counted", dropped, 1)
check("an untagged document carrying a term is listed", got.get("untagged-hit"), "term")
check("a regional document naming the country is listed", got.get("regional-named"), "regional")
check("one that does not name it is not", "regional-unnamed" in got, False)
check("another country's is not", "other-country" in got, False)
check("a document the report cites under a term is listed on the report's word",
      got.get("reported"), "ledger+subject")
check("term-only documents come last", [r["slug"] for r in rows][-1], "untagged-hit")
rows, _ = select.select("CIV", COUNTRIES["CIV"], docs, STUDY["subjects"], {})
check("a country's name matches through accents and apostrophes",
      [r["slug"] for r in rows], ["ivorian"])

long_doc = ("---\ntitle: A survey\n---\n\nThe opening says what this is.\n\n"
            + "\n\n".join(f"Filler paragraph {i}." for i in range(400))
            + "\n\nBefore the fact.\n\nThe HMIS covered 62 per cent of clinics in 2024.\n\nAfter the fact.\n\n"
            + "\n\n".join(f"More filler {i}." for i in range(50)))
cut = select.passages(long_doc, rx)
check("passages keep the paragraph carrying the term, with its neighbours",
      "Before the fact.\n\nThe HMIS covered 62 per cent of clinics in 2024.\n\nAfter the fact." in cut, True)
check("and the document's opening, without its frontmatter",
      cut.startswith("The opening says what this is."), True)
check("and mark what was left out", (cut.count("[...]"), "More filler 30." in cut), (2, False))
table = "Head\n\n" + "\n".join(f"| row {i} | {'HMIS' if i == 700 else 'x'} |" for i in range(900))
check("a block with no blank line is cut by line, not kept whole",
      ("| row 700 | HMIS |" in select.passages(table, rx), "| row 400 |" in select.passages(table, rx)),
      (True, False))

tmp = Path(tempfile.mkdtemp(prefix="study-test-"))
try:
    unit = tmp / "KEN"
    unit.mkdir()
    (unit / "ledger.csv").write_text(
        "row_id,subject,name,sources\n"
        "KEN-1,dpi.mis,National HMIS,led-a|led-b\n"
        "KEN-2,dpi.mis,School census system,led-c\n"
        "KEN-3,gov.policy,HMIS policy,led-d\n", encoding="utf-8")
    (unit / "KEN-status.md").write_text(
        "## DPI\n\n### Sectoral systems\n<!-- dpi.mis -->\n\nThe HMIS runs on "
        "[DHIS2](https://a.org/held) and [more](https://a.org/unheld).\n\n"
        "### Strategies\n<!-- gov.policy -->\n\nA [plan](https://a.org/other).\n", encoding="utf-8")
    (unit / "considered.txt").write_text("con-a\n\ncon-b\n", encoding="utf-8")
    routes, status_rows = select.cited("KEN", ["dpi.mis"], rx, str(tmp),
                                       {"a.org/held": "sta-a", "a.org/other": "sta-x"})
    check("a ledger row carrying a term vouches for its sources", routes.get("led-a"), {"ledger!"})
    check("one that does not only annotates", routes.get("led-c"), {"ledger"})
    check("a row on another subject is not read", "led-d" in routes, False)
    check("a status link resolves to the held record", routes.get("sta-a"), {"status!"})
    check("a link in another sub-section does not", "sta-x" in routes, False)
    check("considered.txt annotates", routes.get("con-b"), {"considered"})
    check("the sub-section heads the list", [(r["kind"], r["slug"]) for r in status_rows],
          [("status", "dpi.mis")])
    check("a country with no report reads as empty", select.cited("ZZZ", ["dpi.mis"], rx, str(tmp), {}),
          ({}, []))

    # ----------------------------------------------------------------------- #
    print("\nthe profile")
    cell = profile.profile_cell(asp["last12"], [ev("KEN-1", "last12", "advancing", "2025-11"),
                                                ev("KEN-2", "last12", "regressing", "2026-08")], AS_AT)
    check("the newest value stands", cell["value"], "regressing")
    check("and the other is kept", cell["others"], "KEN-1=advancing")
    check("inside its window there is no gap", cell["gap"], "")
    cell = profile.profile_cell(asp["last12"], [ev("KEN-1", "last12", "advancing", "2025-06")], AS_AT)
    check("a qualifier with nothing in its window is a gap", cell["gap"], "nothing dated since 2025-09-28")
    check("an aspect with no fact is a gap", profile.profile_cell(asp["tiers"], [], AS_AT)["gap"],
          "nothing held")
    cell = profile.profile_cell(asp["tiers"], [ev("KEN-1", "tiers", "T4", "2025"),
                                               ev("KEN-2", "tiers", "T1;T2", "2024"),
                                               ev("KEN-3", "tiers", "T3", "2019")], AS_AT)
    check("a multi aspect takes every value inside the window, in the study's order",
          cell["value"], "T1;T2;T4")
    check("and leaves the older fact as another", cell["others"], "KEN-3=T3")
    cell = profile.profile_cell(asp["tiers"], [ev("KEN-3", "tiers", "T3", "2019")], AS_AT)
    check("an old coverage fact still gives a value", cell["value"], "T3")
    check("and is a gap to search", cell["gap"], "nothing dated since 2023-09-28")
    cell = profile.profile_cell(asp["clinics"], [ev("KEN-1", "clinics", "not-published", "2026"),
                                                 ev("KEN-2", "clinics", "count:900", "2025"),
                                                 ev("KEN-3", "clinics", "share:40%", "2024"),
                                                 ev("KEN-4", "clinics", "share:62%", "2025")], AS_AT)
    check("a share is preferred to a count and to not published, newest share first",
          (cell["value"], cell["sources"]), ("share:62%", "KEN-4"))
    cell = profile.profile_cell(asp["governance"], [ev("KEN-1", "governance", "owner:partner", "2023"),
                                                    ev("KEN-2", "governance", "owner:ministry", "2025")],
                                AS_AT)
    check("facets take the newest of each", cell["value"], "owner:ministry")
    check("and a facet nobody states is the gap", cell["gap"], "not stated: finance")
    full = profile.profile(STUDY, "KEN", [ev("KEN-1", "tiers", "T1", "2025")], AS_AT)
    check("a profile has a row for every aspect", [r["aspect"] for r in full],
          ["governance", "tiers", "clinics", "last12"])
    deferring = dict(asp["tiers"], values=["T1", "T2", "T3", "T4", "none"], defer=["none"])
    cell = profile.profile_cell(deferring, [ev("KEN-1", "tiers", "none", "2026"),
                                            ev("KEN-2", "tiers", "T2", "2025")], AS_AT)
    check("a deferred value does not sit beside a stated one", (cell["value"], cell["sources"]),
          ("T2", "KEN-2"))
    check("but stands alone", profile.profile_cell(deferring, [ev("KEN-1", "tiers", "none", "2026")],
                                                   AS_AT)["value"], "none")
    single = {"key": "digitised", "role": "coverage", "values": ["facility", "paper"], "defer": ["paper"]}
    cell = profile.profile_cell(single, [ev("KEN-1", "digitised", "paper", "2026"),
                                         ev("KEN-2", "digitised", "facility", "2024")], AS_AT)
    check("a newer deferred value does not displace an older stated one",
          (cell["value"], cell["others"]), ("facility", "KEN-1=paper"))
    barred = dict(STUDY, exclude_sources=[{"slug": "essay", "why": "not sourced fact"}])
    two = [ev("KEN-1", "tiers", "T1", "2024"), ev("KEN-2", "tiers", "T4", "2025", slug="essay")]
    tiers_of = lambda s: next(r for r in profile.profile(s, "KEN", two, AS_AT) if r["aspect"] == "tiers")
    check("an excluded source gives the profile nothing", tiers_of(barred)["value"], "T1")
    check("and counts when the study does not exclude it", tiers_of(STUDY)["value"], "T1;T4")
    check("the draw is repeatable", profile.draw([("A", "x"), ("B", "x"), ("C", "x")], 2, 7),
          profile.draw([("C", "x"), ("A", "x"), ("B", "x")], 2, 7))
    check("and never larger than what is staged", len(profile.draw([("A", "x")], 20, 1)), 1)

    print("\nfacts files into evidence")
    rl = [{"n": "", "kind": "status", "slug": "dpi.mis"},
          {"n": "1", "kind": "raw", "slug": "doc-a", "url": "https://a.org/a"},
          {"n": "2", "kind": "raw", "slug": "doc-b", "url": "https://a.org/b"},
          {"n": "3", "kind": "raw", "slug": "doc-c", "url": "https://a.org/c"}]
    fact = {"sub_indicator": "hmis", "aspect": "tiers", "value": "T1", "fact": "Hospitals report.",
            "as_of": "2025", "date_precision": "year", "system": "DHIS2", "class": "hmis"}
    files = {"1": {"slug": "doc-a", "facts": [fact, dict(fact, **{"class": "tracker"})],
                   "systems": [{"system": "eTracker", "class": "tracker"}]},
             "2": {"slug": "doc-x", "facts": [fact]}}
    new, systems, problems = profile.merge(STUDY, "KEN", rl, files, [ev("KEN-007", "tiers", "T2", "2024")])
    check("ids continue from the highest in evidence.csv", [r["row_id"] for r in new], ["KEN-008"])
    check("the slug and URL are the reading list's", (new[0]["source_slug"], new[0]["url"]),
          ("doc-a", "https://a.org/a"))
    check("a fact about a class the sub-indicator does not assess is refused",
          any("classed `tracker`" in p for p in problems), True)
    check("and that system is kept as a systems row", (systems[0]["system"], systems[0]["sources"]),
          ("eTracker", "doc-a"))
    check("a file filed under the wrong document is refused", any("says `doc-x`" in p for p in problems), True)
    check("a document with no file is named", any("document(s) [3]" in p for p in problems), True)
    again, _, _ = profile.merge(STUDY, "KEN", rl, files, new)
    check("a document already merged is not merged twice", again, [])

    print("\nevidence that cannot be profiled")
    bad = dict(ev("KEN-1", "tiers", "T9", "last year"), date_precision="week", url="")
    problems = study_lib.evidence_problems(STUDY, "KEN", [bad, dict(bad, row_id="UGA-1")])
    check("value, date, precision and url are each named", len([p for p in problems if "line 2" in p]), 4)
    check("a row id from another country is caught", any("does not open `KEN-`" in p for p in problems), True)
    check("a clean row passes", study_lib.evidence_problems(STUDY, "KEN", [ev("KEN-1", "tiers", "T1", "2025")]), [])

    # ----------------------------------------------------------------------- #
    print("\nwhat came back")
    staged = [{"file": "a.md", "url": "https://www.A.org/x/?utm_source=n"},
              {"file": "b.md", "url": "https://b.org/y"}, {"file": "c.md", "url": "https://c.org/z"}]
    out = returned.outcomes(staged, {"a.org/x": "raw/2026/2026-01-01-a-doc.md"}, {"b.org/y": "out-of-remit"})
    check("a held URL is admitted, matched as ingest normalises it",
          (out[0]["outcome"], out[0]["slug"]), ("admitted", "2026-01-01-a-doc"))
    check("a declined one carries ingest's reason", (out[1]["outcome"], out[1]["reason"]),
          ("rejected", "out-of-remit"))
    check("one in neither is not returned", out[2]["outcome"], "not-returned")

    share = tmp / "share"
    share.mkdir()
    (share / "notes-for-osint.md").write_text("**231** [ACT] (2026-10-20) - evidence\n", encoding="utf-8")
    (share / "notes-for-osint-resolved.md").write_text("### 200. `[ACT]` done\n", encoding="utf-8")
    manifest = tmp / "cycle-manifest.json"
    manifest.write_text('{"written_utc": "2026-10-21 04:00"}', encoding="utf-8")
    check("an open note shuts the gate", "is open" in returned.gate("231", str(share), str(manifest)), True)
    check("a note in neither file shuts it", "is unknown" in returned.gate("999", str(share), str(manifest)), True)
    moved = dt.datetime(2026, 10, 21, 2, 0, tzinfo=dt.timezone.utc)
    returned.moved_at = lambda note, s: moved
    check("a mirror written after the move opens it", returned.gate("200", str(share), str(manifest)), "")
    manifest.write_text('{"written_utc": "2026-10-21 01:00"}', encoding="utf-8")
    check("a mirror written before it does not",
          "predates the ingest" in returned.gate("200", str(share), str(manifest)), True)
    returned.moved_at = lambda note, s: None
    check("no move in the history shuts it", "does not show" in returned.gate("200", str(share), str(manifest)), True)

    # ----------------------------------------------------------------------- #
    print("\nthe page")
    STUDY_MD = ("# T\n\n## 4. The ladders\n\nThresholds.\n\n**HMIS**\n\n| Stage | Tiers |\n|---|---|\n"
                "| 1 Absent | paper |\n\n**EMR**\n\n| Stage | X |\n|---|---|\n\n"
                "## 5. The norm\n\nThe norm text.\n\n## 6. Next\n\nNo.\n")
    check("the norm is its own section, no further", render.section(STUDY_MD, "The norm"), "The norm text.")
    check("the ladder is the table under its label", render.ladder(STUDY_MD, "HMIS"),
          "| Stage | Tiers |\n|---|---|\n| 1 Absent | paper |")
    check("a label with no table gives nothing", render.ladder(STUDY_MD, "LMIS"), "")
    FIELDS = lint.assessment_fields(STUDY)

    def cellrow(iso, stage, **kw):
        base = dict.fromkeys(FIELDS, "")
        base.update(iso3=iso, indicator_id="digital.rural--clinics-hmis", as_at="2026-09-30",
                    stage=stage, short="Every district reports, 2025; clinic entry not published.",
                    stage_sources="" if not stage.isdigit() else f"{iso}-1",
                    gaps="" if stage.isdigit() else "no coverage aspect stated")
        base.update(kw)
        return base

    EV = {"KEN": [ev("KEN-1", "tiers", "T1", "2025", url="https://a.org/a b")],
          "CIV": [ev("CIV-1", "tiers", "T1", "2024")]}
    text, missing = render.page(STUDY, STUDY["sub_indicators"][0], STUDY_MD,
                                [cellrow("CIV", "unplaced"), cellrow("KEN", "3", flags="advancing"),
                                 cellrow("CIV", "4", stage_sources="CIV-9")], EV, COUNTRIES)
    order = [l for l in text.splitlines() if l.startswith("### ")]
    check("countries print highest stage first, the unplaced after",
          order, ["### Côte d'Ivoire: 4 Operating", "### Kenya: 3 Established", "### Côte d'Ivoire: Unplaced"])
    check("a fact links its source, in the form a spaced URL needs",
          "- A stated fact ([source, 2025](<https://a.org/a b>))." in text, True)
    check("a source that is not an evidence row is reported", len(missing), 1)
    check("the stage count is on the page", "| 3 Established | 1 |" in text, True)
    check("a cell with no stage says what is not established",
          "Not established: no coverage aspect stated" in text, True)

    # ----------------------------------------------------------------------- #
    print("\nthe lint: cells")
    good = [cellrow("KEN", "3"), cellrow("CIV", "unplaced")]
    check("a full, well-formed assessment passes", lint.assessment_problems(STUDY, good, EV, COUNTRIES), [])
    p = lint.assessment_problems(STUDY, good[:1], EV, COUNTRIES)
    check("a missing cell is named", p, ["CIV digital.rural--clinics-hmis: no row"])
    p = lint.assessment_problems(STUDY, good + [cellrow("KEN", "3")], EV, COUNTRIES)
    check("a cell twice is named", any("is also on line" in x for x in p), True)
    p = lint.assessment_problems(STUDY, [cellrow("KEN", "3"), cellrow("CIV", "unplaced", gaps="")], EV, COUNTRIES)
    check("no stage and no reason fails", any("no reason" in x for x in p), True)
    p = lint.assessment_problems(STUDY, [cellrow("KEN", "6"), good[1]], EV, COUNTRIES)
    check("a stage off the scale fails", any("is not 1 to 5" in x for x in p), True)
    p = lint.assessment_problems(STUDY, [cellrow("KEN", "3", stage_sources=""), good[1]], EV, COUNTRIES)
    check("a stage with no source fails", any("no `stage_sources`" in x for x in p), True)
    p = lint.assessment_problems(STUDY, [cellrow("KEN", "3", stage_sources="CIV-1"), good[1]], EV, COUNTRIES)
    check("another country's evidence row is not a source", any("names `CIV-1`" in x for x in p), True)
    p = lint.assessment_problems(STUDY, [cellrow("KEN", "3", short=" ".join(["word"] * 26)), good[1]], EV, COUNTRIES)
    check("a 26-word short summary fails", any("26 words" in x for x in p), True)
    p = lint.assessment_problems(STUDY, [cellrow("KEN", "3", short="See [this](https://a.org)."), good[1]], EV, COUNTRIES)
    check("a link in the short summary fails", any("no link" in x for x in p), True)
    p = lint.assessment_problems(STUDY, [cellrow("KEN", "3", flags="promising"), good[1]], EV, COUNTRIES)
    check("a flag outside the list fails", any("flag `promising`" in x for x in p), True)
    p = lint.assessment_problems(STUDY, [cellrow("KEN", "3", tiers="T9"), good[1]], EV, COUNTRIES)
    check("an aspect value outside the list fails", any("tiers:" in x for x in p), True)

    print("\nthe lint: the cap rule")
    met = "owner:ministry;finance:domestic"
    check("stage 4 with the governance the rule names passes",
          lint.cap_problem(STUDY, cellrow("KEN", "4", governance=met)), "")
    check("stage 4 without it fails",
          "the cap holds it at 3" in lint.cap_problem(STUDY, cellrow("KEN", "4", governance="owner:ministry;finance:donor")), True)
    check("stage 4 with nothing stated fails", bool(lint.cap_problem(STUDY, cellrow("KEN", "4"))), True)
    check("capped to 3, recorded and flagged, passes",
          lint.cap_problem(STUDY, cellrow("KEN", "3", cap="4", flags="externally run", governance="owner:partner")), "")
    check("capped without the flag fails",
          bool(lint.cap_problem(STUDY, cellrow("KEN", "3", cap="4", governance="owner:partner"))), True)
    check("a cap on a cell the rule does not fire for fails",
          "nothing caps it" in lint.cap_problem(STUDY, cellrow("KEN", "3", cap="4", flags="externally run", governance=met)), True)
    check("the flag with no cap fails",
          bool(lint.cap_problem(STUDY, cellrow("KEN", "3", flags="externally run"))), True)
    check("a cap that records a rung at or below the line fails",
          bool(lint.cap_problem(STUDY, cellrow("KEN", "3", cap="3", flags="externally run", governance="owner:partner"))), True)
    check("stage 3 uncapped needs nothing of governance", lint.cap_problem(STUDY, cellrow("KEN", "3")), "")
    check("a cell with no stage is not the rule's business", lint.cap_problem(STUDY, cellrow("KEN", "unplaced")), "")

    print("\nthe lint: sources and long summaries")
    p = lint.held_problems(EV, {"s1"}, {"a.org/1"})
    check("a URL no held record carries is named", p, ["KEN KEN-1: url https://a.org/a b is not a held record's"])
    check("a slug not in raw/ is named", len(lint.held_problems(EV, set(), {"a.org/1", "a.org/a b"})), 2)

    def para(name, n=30):
        return f"**{name}.** " + " ".join(["word"] * (n - 2)) + " [cited](https://a.org/1)."

    names = [a["name"] for a in STUDY["aspects"]]
    closing = "***Noted, not assessed***: none.\n\n***Not held***: clinic shares."
    page = "# Kenya\n\n## HMIS\n\n" + "\n\n".join(para(n, 40) for n in names) + "\n\n" + closing + "\n"
    urls = {"a.org/1"}
    check("a well-formed long summary passes", lint.long_problems(STUDY, "KEN", page, {"hmis": True}, urls), [])
    p = lint.long_problems(STUDY, "KEN", page, {"hmis": True}, set())
    check("a link to an unheld URL fails", any("not a held record's URL" in x for x in p), True)
    short_page = page.replace(" ".join(["word"] * 38), "word")
    p = lint.long_problems(STUDY, "KEN", short_page, {"hmis": True}, urls)
    check("too few words fails", any("the long summary is 120 to 250" in x for x in p), True)
    swapped = "# Kenya\n\n## HMIS\n\n" + "\n\n".join(para(n, 40) for n in reversed(names)) + "\n\n" + closing
    p = lint.long_problems(STUDY, "KEN", swapped, {"hmis": True}, urls)
    check("aspects out of order fail", any("the study's order is" in x for x in p), True)
    p = lint.long_problems(STUDY, "KEN", page.replace(" [cited](https://a.org/1)", "", 1), {"hmis": True}, urls)
    check("a paragraph with no link fails", any("carries no link" in x for x in p), True)
    p = lint.long_problems(STUDY, "KEN", page.replace("***Not held***", "Not held"), {"hmis": True}, urls)
    check("a missing closing line fails", any("no closing line ***Not held***" in x for x in p), True)
    bare = "# Kenya\n\n## HMIS\n\n" + closing
    check("a cell with no stage needs only its closing lines",
          lint.long_problems(STUDY, "KEN", bare, {"hmis": False}, urls), [])
    check("a missing section fails", any("no `## HMIS` section" in x
                                         for x in lint.long_problems(STUDY, "KEN", "# Kenya\n", {"hmis": True}, urls)), True)

    print("\nthe lint: the typology")
    sysrow = dict.fromkeys(study_lib.SYSTEMS_FIELDS, "")
    sysrow.update(iso3="KEN", system="KHIS", **{"class": "hmis"})
    check("a well-formed systems.csv passes", lint.systems_problems(STUDY, [sysrow], COUNTRIES), [])
    check("a class outside the typology fails",
          len(lint.systems_problems(STUDY, [dict(sysrow, **{"class": "lmis"})], COUNTRIES)), 1)
    check("an unclassified system is allowed, as a gap",
          lint.systems_problems(STUDY, [dict(sysrow, **{"class": ""})], COUNTRIES), [])
    check("a missing file fails", lint.systems_problems(STUDY, [], COUNTRIES), ["systems.csv is missing or empty"])

    print("\nthe search: fetch, decide, stage")
    stage = load("study-stage")
    root = tmp / "corpus"
    (root / "maturity" / "t" / "search" / "KEN" / "decisions").mkdir(parents=True)
    (root / "maturity" / "t" / "search" / "UGA" / "decisions").mkdir(parents=True)
    real_corpus = study_lib.CORPUS
    study_lib.CORPUS = str(root)
    try:
        import json as _json
        leads = [{"url": "https://moh.go.ke/bulletin-2025", "title": "Bulletin", "sub_indicator": "hmis"},
                 {"url": "https://held.org/x", "title": "Held", "sub_indicator": "hmis"},
                 {"url": "https://www.moh.go.ke/bulletin-2025/", "title": "Bulletin again", "sub_indicator": "hmis"},
                 {"url": "https://dead.org/y", "title": "Dead", "sub_indicator": "emr"},
                 {"url": "https://who.int/z", "title": "Thin", "sub_indicator": "emr"}]
        (root / "maturity" / "t" / "search" / "KEN" / "leads.json").write_text(_json.dumps(leads), encoding="utf-8")
        (root / "maturity" / "t" / "search" / "UGA" / "leads.json").write_text(
            _json.dumps([leads[0]]), encoding="utf-8")
        fake = lambda url: ((None, "HTTP 404", "", "") if "dead" in url
                            else ("The HMIS covered 62 per cent of clinics.", url, "html", "A page"))
        looked = ({"held.org/x": {"file": "raw/2024/2024-01-01-held.md"}}, {})
        rows = stage.fetch("t", "KEN", fake, looked)
        stage.fetch("t", "UGA", fake, looked)
        check("a lead already held is not fetched", rows[1]["status"], "held")
        check("the same document twice is fetched once", rows[2]["status"], "duplicate")
        check("a failed fetch is recorded, not dropped", (rows[3]["status"], rows[3]["detail"]),
              ("unfetchable", "HTTP 404"))
        cached = (root / rows[0]["cache"]).read_text(encoding="utf-8")
        check("the text is cached under the address it came from",
              cached, "URL: https://moh.go.ke/bulletin-2025\n\nThe HMIS covered 62 per cent of clinics.\n")
        (dk0 := root / "maturity" / "t" / "search" / "KEN" / "decisions" / "4.json").write_text(
            '{"select": false, "why_not": "a bot-check page"}', encoding="utf-8")
        stage.THIN_WORDS = 5    # the fixture's pages are a sentence long
        route = lambda url: ("The EMR ran in 12 hospitals in 2025. " * 30, url, "html", "T", "second client")
        check("a second route recovers a failed lead", stage.refetch("t", "KEN", route), (1, 1))
        again = study_lib.read_csv(str(root / "maturity" / "t" / "search" / "KEN" / "fetched.csv"))
        check("and the row says how", (again[3]["status"], again[3]["detail"]),
              ("fetched", "second pass, by second client"))
        check("a decision written against the failed page is removed", dk0.exists(), False)
        check("nothing is tried twice once recovered",
              stage.refetch("t", "KEN", lambda url: (None, "still dead", "", "", "")), (0, 0))
        (root / "maturity" / "t" / "search" / "KEN" / "decisions" / "4.json").write_text(
            '{"select": false, "why_not": "states no dated fact"}', encoding="utf-8")
        good = {"select": True, "sub_indicator": "hmis", "aspect": "clinics;tiers", "fact": "62 per cent in 2025.",
                "title": "Bulletin statistique 2025", "publisher": "Ministry of Health", "published": "2025-06"}
        dk = root / "maturity" / "t" / "search" / "KEN" / "decisions"
        (dk / "1.json").write_text(_json.dumps(good), encoding="utf-8")
        (dk / "5.json").write_text(_json.dumps({"select": False, "why_not": "states no dated fact"}), encoding="utf-8")
        (root / "maturity" / "t" / "search" / "UGA" / "decisions" / "1.json").write_text(
            _json.dumps(dict(good, published="June 2025")), encoding="utf-8")
        sel, unsel, searched, problems = stage.collect(STUDY, "t", ["KEN", "UGA"])
        check("a selecting decision is collected", [(d["iso3"], d["k"]) for d in sel], [("KEN", 1)])
        check("every lead not staged says why", sorted((u["k"], u["why"].split(":")[0]) for u in unsel),
              [(2, "held"), (3, "duplicate"), (4, "not selected"), (5, "not selected")])
        check("a date that is not a date stops the decision", problems,
              ["UGA decisions/1.json: `published` is `June 2025`, not YYYY, YYYY-MM or YYYY-MM-DD"])
        check("the search is counted by country and sub-indicator",
              [(s["iso3"], s["sub_indicator"], s["leads"], s["fetched"], s["selected"]) for s in searched],
              [("KEN", "emr", 2, 2, 0), ("KEN", "hmis", 3, 1, 1), ("UGA", "hmis", 1, 1, 0)])
        (dk / "5.json").unlink()
        check("a fetched lead with no decision is a problem, not a silence",
              any("no decision written" in p for p in stage.collect(STUDY, "t", ["KEN"])[3]), True)
        name, text = stage.candidate(dict(STUDY, stage_topic="dpi.mis"), dict(good, url=leads[0]["url"]),
                                     ["KEN", "UGA"], cached, "2026-10-06")
        check("the file is named for its date, first place and title",
              name, "2025-06-01-ken-bulletin-statistique-2025.md")
        check("a month is a proxy date, and the batch names the study",
              all(line in text for line in ("published: 2025-06-01", "date_precision: month", "date_source: proxy",
                                            "places: [KEN, UGA]", "topics: [dpi.mis]", "retrieved: 2026-10-06",
                                            "sweep_batch: maturity-study-t-KEN-2026-10-06")), True)
        check("the body is the cache's, under the title and its URL line",
              text.endswith("# Bulletin statistique 2025\nURL: https://moh.go.ke/bulletin-2025\n\n"
                            "The HMIS covered 62 per cent of clinics.\n"), True)
        check("staging never writes `ingested:`", "ingested:" in text, False)
        check("an aspect outside the study stops a decision",
              stage.decision_problem(STUDY, dict(good, aspect="clinics;reach")), "aspect `reach` is not in the study")
    finally:
        study_lib.CORPUS = real_corpus

    print("\nthe health study as it stands")
    health = study_lib.load("health")
    check("its ids are what their texts mint",
          [study_lib.mint(s["subject"], s["text"]) for s in health["sub_indicators"]],
          [s["indicator_id"] for s in health["sub_indicators"]])
    check("there are 54 countries", len(study_lib.countries()), 54)
    md = open(os.path.join(study_lib.study_dir("health"), health["study_file"]), encoding="utf-8").read()
    check("the study file carries a ladder for each sub-indicator",
          [bool(render.ladder(md, s["label"])) for s in health["sub_indicators"]], [True, True])
    check("and a norm", bool(render.section(md, "The norm")), True)
    check("the cap's aspect, values and flag are all in the study's lists",
          (health["cap"]["aspect"] in study_lib.aspects(health),
           all(not study_lib.value_problem(study_lib.aspects(health)["governance"], "hmis", v)
               for v in health["cap"]["all"] + health["cap"]["any"]),
           health["cap"]["flag"] in health["flags"]), (True, True, True))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
print("all cases pass" if not fails else f"{len(fails)} of the cases FAILED")
sys.exit(1 if fails else 0)
