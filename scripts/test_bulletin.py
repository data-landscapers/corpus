#!/usr/bin/env python3
"""test_bulletin.py — prove the bulletin says what it holds, and moves when it moves.

    python scripts/test_bulletin.py

**Every fault this document has had was found by reading the built page**, which is the reason
this file exists. The design note records two of them and they are the same shape. The summary
anchor and the section order agreed for a reason neither of them stated; the order changed, the
agreement broke, and nothing failed — the page rendered, every anchor resolved, the counts were
right, and the document simply would not start, because the first thing a reader met was a
pointer further down. Then `--assemble` compared the body below the frontmatter on the reasoning
that the stamp had to be excluded, which excluded the subtitle with it, so a correction to the
byline ran, reported `unchanged` and left the wrong wording on disk.

Neither could raise. Both are cases below, because the class is *a change that is invisible to
the thing that decides whether anything changed*, and the only defence against that class is an
assertion that names the property out loud.

The fixtures are written rather than copied. `test_render_gate.py` argues for a real document
and is right for its subject — the frontmatter split is what it is testing. Here the subject is
selection and placement, which need a catalogue whose dates, topics and places are chosen to
put a known item in a known section, and the real catalogue's contents move with every build.
The taxonomy is the real one: `lookups/taxonomy.csv` is the vocabulary under test, and a
stand-in would test the stand-in.
"""

from __future__ import annotations

import csv
import datetime as dt
import importlib.util
import io
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bulletin = _load("bulletin")
render_mod = _load("render")

RUN = date(2026, 5, 14)          # the run date every case uses; the window is the 13th and 14th
TODAY = "2026-05-14"
YESTERDAY = "2026-05-13"

COLUMNS = ["slug", "title", "publisher", "author", "published", "date_precision", "places",
           "topics", "entities", "lens", "body_completeness", "finance", "artefact", "words",
           "ingested", "url"]


def row(slug: str, published: str, places: str, topics: str, title: str = None) -> dict:
    r = {c: "" for c in COLUMNS}
    r.update(slug=slug, title=title or slug.replace("-", " ").title(), publisher="A Publisher",
             published=published, date_precision="day", places=places, topics=topics,
             lens="sovereignty", body_completeness="full", words="900",
             url=f"https://example.invalid/{slug}")
    return r


class Bench:
    """A catalogue, a summary store and a document, all under a temporary root.

    `bulletin.py` states its paths as module constants, which is right for a script whose paths
    never vary in production and is why they are rebound here rather than parameterised: a
    signature widened for the sake of a test is a signature the production caller has to carry.
    """

    def __init__(self, tmp: Path, rows: list[dict], summaries: dict[str, str] | None = None):
        self.tmp = tmp
        self.saved = {k: getattr(bulletin, k)
                      for k in ("CORPUS", "CATALOGUE", "STORE", "DOCUMENT", "BULLETINS", "RAW")}
        cat = tmp / "raw-catalogue.csv"
        with cat.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(rows)
        bulletin.CORPUS = tmp          # only the root the run's output lines are relative to
        bulletin.CATALOGUE = cat
        bulletin.BULLETINS = tmp
        bulletin.STORE = tmp / "summaries.json"
        bulletin.DOCUMENT = tmp / "corpus-bulletin.md"
        bulletin.RAW = tmp / "raw"
        store = {r["slug"]: {"published": r["published"], "written": TODAY,
                             "summary": (summaries or {}).get(r["slug"],
                                                              f"Summary of {r['slug']}.")}
                 for r in rows}
        bulletin.save_store(store)

    def stamp(self, when: str | None, started: str | None = None) -> None:
        """Pin OSINT's ingest clocks. `when` is the newest stamp, which becomes `compiled:`;
        `started` is when the run began, which becomes the byline and defaults to `when`.
        `None` is an unreadable mirror, in which case neither is readable."""
        parse = lambda t: dt.datetime.strptime(t, "%Y-%m-%d %H:%M") if t else None
        bulletin.osint_lib.last_ingest = lambda: parse(when)
        bulletin.osint_lib.ingest_started = lambda: parse(started or when)

    def assemble(self) -> str:
        out = io.StringIO()
        with redirect_stdout(out):
            code = bulletin.assemble(RUN)
        assert code == 0, f"--assemble exited {code}"
        return out.getvalue()

    def document(self) -> str:
        return bulletin.DOCUMENT.read_text(encoding="utf-8")

    def restore(self) -> None:
        for k, v in self.saved.items():
            setattr(bulletin, k, v)


# ── the cases ──────────────────────────────────────────────────────

def case_anchor_is_earliest_in_document_order(tmp):
    """The summary lands where the item **first appears**, not where its facet list starts.

    `geopol.india` is sort order 38 and `gov.policy` is 1. A record listing the first of those
    first must still be summarised under the second, because that is the heading a reader
    passing down the page reaches first. This is the fault of 2026-08-21: while the sections
    were ordered by the record's own facets the two rules were the same, and the taxonomy's
    order broke the agreement in silence."""
    r = row("late-first", TODAY, "KEN", "geopol.india; gov.policy")
    b = Bench(tmp, [r])
    assert bulletin.anchor_topic(r) == "gov.policy", bulletin.anchor_topic(r)
    b.stamp("2026-05-14 00:05")
    b.assemble()
    doc = b.document()
    here = doc.index("Summary of late-first.")
    pointer = doc.index("Summarised under")
    assert here < pointer, "the detail must come before the cross-reference to it"


def case_every_cross_reference_points_backwards(tmp):
    """No *Summarised under X* may appear before the section X it names.

    The property the anchor rule exists for, asserted over the whole document rather than over
    the rule: a reader who meets a pointer has already passed the text it points at. Five
    records spread across the taxonomy's range, several carrying three topics each, so the
    sections interleave rather than falling out in facet order by accident."""
    rows = [
        row("a", TODAY, "KEN", "geopol.china; gov.policy; data.open"),
        row("b", TODAY, "NGA", "infra.connect; gov.legislate"),
        row("c", YESTERDAY, "ZAF", "geopol.eu; data.open"),
        row("d", YESTERDAY, "GHA", "gov.protect; infra.connect; geopol.gulf"),
        row("e", TODAY, "EGY", "fin.invest; gov.policy"),
    ]
    b = Bench(tmp, rows)
    b.stamp("2026-05-14 00:05")
    b.assemble()
    doc = b.document()
    headings = {line[4:].strip(): i for i, line in enumerate(doc.splitlines())
                if line.startswith("### ")}
    for i, line in enumerate(doc.splitlines()):
        if not line.startswith("Summarised under "):
            continue
        label = line[len("Summarised under ["):line.index("](#")]
        assert label in headings, f"cross-reference to a section that is not in the document: {label}"
        assert headings[label] < i, f"forward cross-reference to {label!r} at line {i}"


def case_a_subtitle_change_rewrites_the_file(tmp):
    """The regression of 2026-08-21: a byline correction must reach the file.

    The comparison excluded the whole frontmatter to exclude the stamp, so a fix to the
    subtitle ran, found the body identical and reported `unchanged`. Simulated the way it
    happened — the generator's wording changes while the rows do not."""
    b = Bench(tmp, [row("only", TODAY, "KEN", "gov.policy")])
    b.stamp("2026-05-14 00:05")
    b.assemble()
    assert "Covering sources published on" in b.document()

    original = bulletin.covered_phrase
    try:
        bulletin.covered_phrase = lambda rows, start, end: "SOME OTHER WORDING"
        out = b.assemble()
    finally:
        bulletin.covered_phrase = original
    assert "written" in out, f"reported no write:\n{out}"
    assert "SOME OTHER WORDING" in b.document(), "the corrected byline never reached the file"


def case_a_moved_stamp_is_written_and_named_as_a_check(tmp):
    """A sweep that published nothing into the window has still updated this document.

    *(Bill, 2026-08-21.)* The stamp used to be suppressed here on the reasoning that the content
    had not moved — so a sweep that admitted fifty sources, none of them dated inside the
    window, left the page saying *last updated the 20th* through a night's work. That reports
    neglect where there was none, and a reader cannot tell it from the real thing. It writes
    now, and the run calls it a check rather than a write, because *we looked and nothing was
    published* and *here is what was published* are different things for a run to say."""
    b = Bench(tmp, [row("only", TODAY, "KEN", "gov.policy")])
    b.stamp("2026-05-14 00:05")
    b.assemble()
    before = b.document()

    b.stamp("2026-05-14 23:59")
    out = b.assemble()
    assert "checked" in out, f"a moved clock was not reported as a check:\n{out}"
    assert "23:59" in b.document(), "the new stamp never reached the file"
    assert before.split("---", 2)[-1] == b.document().split("---", 2)[-1], \
        "the body moved when only the clock should have"


def case_a_still_clock_writes_nothing(tmp):
    """Nothing moved at all — not the material, not the sweep. The file is left alone."""
    b = Bench(tmp, [row("only", TODAY, "KEN", "gov.policy")])
    b.stamp("2026-05-14 00:05")
    b.assemble()
    before = b.document()
    out = b.assemble()
    assert "unchanged" in out, out
    assert b.document() == before


def case_an_unreadable_mirror_is_said_on_every_run(tmp):
    """The fallback is announced whether or not the material moved.

    `osint_lib`'s whole reason for returning None rather than guessing is that the caller says
    which it got. A caller that says so only when it happens to have news does not — and a
    fallback nobody is told about is one that becomes the normal case unnoticed."""
    b = Bench(tmp, [row("only", TODAY, "KEN", "gov.policy")])
    b.stamp("2026-05-14 00:05")
    b.assemble()

    b.stamp(None)
    out = b.assemble()
    assert "unreadable" in out, f"the mirror fallback went unsaid:\n{out}"


def case_the_stamp_is_outside_the_edition_digest(tmp):
    """A moved stamp must not cut a dated PDF, which is why the digest is the body alone.

    The page is refreshed on a held-off render instead — `test_render_gate.py` asserts that
    half. Without the split, the bulletin would mint an edition every sweep and two consecutive
    editions would carry the same news under different names, which is what §9 exists to stop."""
    b = Bench(tmp, [row("only", TODAY, "KEN", "gov.policy")])
    b.stamp("2026-05-14 00:05")
    b.assemble()
    first = render_mod.record(render_mod.frontmatter(b.document())[1])
    b.stamp("2026-05-14 23:59")
    b.assemble()
    assert render_mod.record(render_mod.frontmatter(b.document())[1]) == first, \
        "a moved clock changed the edition digest"


def case_an_empty_window_is_a_finished_bulletin(tmp):
    """It renders, it says the window was empty, and it names both days with *or*.

    A bulletin simply absent on a quiet day is indistinguishable from a build that did not
    run, and *nothing was published on the 13th **and** the 14th* is not the claim being made."""
    b = Bench(tmp, [row("old", "2026-05-01", "KEN", "gov.policy")])
    b.stamp("2026-05-14 00:05")
    out = b.assemble()
    doc = b.document()
    assert "items: 0" in doc, doc[:400]
    assert "13 or 14 May 2026" in doc, "an absence must name both days, joined by 'or'"
    assert "not that nothing arrived" in doc


def case_the_byline_states_the_days_in_hand(tmp):
    """One day's material names one day; two days' material names both, joined by *and*.

    The run happens in the small hours, so the run date is routinely empty — a byline saying
    it was covered reads as *covered and found nothing* when the day has barely started."""
    b = Bench(tmp, [row("y", YESTERDAY, "KEN", "gov.policy")])
    b.stamp("2026-05-14 00:05")
    b.assemble()
    assert "published on 13 May 2026" in b.document(), b.document()[:400]
    b.restore()

    b2 = Bench(tmp, [row("y", YESTERDAY, "KEN", "gov.policy"),
                     row("t", TODAY, "NGA", "gov.policy")])
    b2.stamp("2026-05-14 00:05")
    b2.assemble()
    assert "published on 13 and 14 May 2026" in b2.document(), b2.document()[:400]


def case_a_missing_summary_stops_the_run(tmp):
    """`--assemble` refuses rather than publishing an item with nothing under it."""
    b = Bench(tmp, [row("has", TODAY, "KEN", "gov.policy")])
    store = bulletin.load_store()
    store.pop("has")
    bulletin.save_store(store)
    b.stamp("2026-05-14 00:05")
    err = io.StringIO()
    out = io.StringIO()
    stderr, sys.stderr = sys.stderr, err
    try:
        with redirect_stdout(out):
            code = bulletin.assemble(RUN)
    finally:
        sys.stderr = stderr
    assert code == 1, f"exited {code}"
    assert "has" in err.getvalue()
    assert not bulletin.DOCUMENT.exists(), "a gap was published"


def case_nothing_selected_is_ever_dropped(tmp):
    """A record with no topic, and one carrying a slug the taxonomy does not know, both appear.

    The old topic bulletin dropped both silently while counting them in its headline figure, so
    the document could say fifty and show forty-seven. The count and the content must agree."""
    rows = [row("plain", TODAY, "KEN", "gov.policy"),
            row("untopiced", TODAY, "NGA", ""),
            row("unknown", TODAY, "ZAF", "made.up.slug")]
    b = Bench(tmp, rows)
    b.stamp("2026-05-14 00:05")
    b.assemble()
    doc = b.document()
    assert "items: 3" in doc
    for slug in ("plain", "untopiced", "unknown"):
        assert f"Summary of {slug}." in doc, f"{slug} was counted and not shown"
    assert bulletin.UNTOPICED_LABEL in doc
    assert "## Other" in doc, "an unknown slug gets a section rather than vanishing"


def case_out_of_remit_records_are_named_not_dropped(tmp):
    """The remit filter excludes, and says which — a silent filter is the missing filter again.

    Thailand's passport scheme sat in a bulletin about Africa until 2026-08-20; the fix is only
    half a fix if the day it turns away a great deal looks the same as the day it turns away
    nothing."""
    b = Bench(tmp, [row("kenyan", TODAY, "KEN", "gov.policy"),
                    row("thai", TODAY, "THA", "gov.policy")])
    b.stamp("2026-05-14 00:05")
    out = b.assemble()
    doc = b.document()
    assert "items: 1" in doc
    assert "Summary of thai." not in doc
    assert "remit" in out and "1 record" in out, f"the exclusion was silent:\n{out}"


def case_country_boxes_are_countries_only(tmp):
    """A box per country page that exists; none for a region, which has no page to open."""
    names = {"KEN": "Kenya"}
    boxes = bulletin.country_boxes(row("r", TODAY, "KEN; XAFR; XGL", "gov.policy"), names)
    assert boxes.count("<a ") == 1, boxes
    assert "/countries/KEN/" in boxes and "Kenya" in boxes
    assert "XAFR" not in boxes and "XGL" not in boxes, "a box that 404s is worse than no box"


def case_the_nav_bar_holds_only_the_categories_present(tmp):
    """Ten categories exist; a two-day window reaches a few, and a dead jump is worse than none."""
    b = Bench(tmp, [row("g", TODAY, "KEN", "gov.policy"),
                    row("i", TODAY, "NGA", "infra.connect")])
    b.stamp("2026-05-14 00:05")
    b.assemble()
    doc = b.document()
    nav = doc[doc.index("<nav class=\"bulletin-nav\""):doc.index("</nav>")]
    assert nav.count("<a href=") == 2, nav
    assert ">Governance<" in nav and ">ICT Infrastructure<" in nav
    assert ">Finance<" not in nav, "a category with nothing under it must not be in the bar"


def case_every_anchor_in_the_document_resolves(tmp):
    """Both halves of a link are built from the same `slugify`, and this asserts they still are.

    Two implementations of that slug is how the nav bar and the cross-references would come to
    point at headings that are not there — and an anchor that resolves to nothing scrolls
    nowhere rather than erroring, so nothing downstream can see it."""
    rows = [row("a", TODAY, "KEN", "geopol.china; gov.policy"),
            row("b", YESTERDAY, "NGA", "infra.connect; data.open"),
            row("c", TODAY, "ZAF", "")]
    b = Bench(tmp, rows)
    b.stamp("2026-05-14 00:05")
    b.assemble()
    doc = b.document()
    from markdown.extensions.toc import slugify
    ids = {slugify(line.lstrip("#").strip(), "-") for line in doc.splitlines()
           if line.startswith("## ") or line.startswith("### ")}
    targets = {chunk.split(")")[0] for chunk in doc.split("](#")[1:]}
    targets |= {chunk.split('"')[0] for chunk in doc.split('href="#')[1:]}
    missing = sorted(targets - ids)
    assert not missing, f"anchors pointing at no heading: {missing}"


def case_the_byline_is_when_collection_stopped_not_when_ingest_finished(tmp):
    """*Last updated* names the start of the ingest run, and `compiled:` names its end.

    Bill, 2026-08-23: the time on the bulletin should be the moment collection stopped — the end
    of the night's last sweep — and the start of ingest is the proxy for it, since ingest reads
    what collection staged. The newest ingest stamp had been the byline, and it runs on for hours
    after the sweep has finished: on 2026-08-23 it said 05:20 of material that stopped moving at
    23:55 the evening before, which overstates the page's freshness by five and a half hours.
    Both facts are kept, because the edition picker asks the other question — how late is the
    newest thing in this cut."""
    b = Bench(tmp, [row("only", TODAY, "KEN", "gov.policy")])
    b.stamp("2026-05-14 05:20", started="2026-05-13 23:55")
    b.assemble()
    text = b.document()
    assert "Last updated 13-05-2026 at 23:55" in text, \
        f"the byline did not take the start of the ingest run:\n{text[:400]}"
    assert "collected_to: 2026-05-13 23:55" in text, "collected_to: is not on the file"
    assert "compiled: 2026-05-14 05:20" in text, \
        "compiled: lost the newest ingest, which is what the edition picker shows"


def case_a_run_that_only_ingests_later_does_not_move_the_byline(tmp):
    """More slices written from the same night's catch are not more collection.

    The stamps move apart, `compiled:` follows the newest and the byline does not move at all —
    which is the whole point of separating them. Nothing was collected in those hours."""
    b = Bench(tmp, [row("only", TODAY, "KEN", "gov.policy")])
    b.stamp("2026-05-14 02:00", started="2026-05-13 23:55")
    b.assemble()
    b.stamp("2026-05-14 05:20", started="2026-05-13 23:55")
    b.assemble()
    text = b.document()
    assert "Last updated 13-05-2026 at 23:55" in text, "the byline moved on a later ingest"
    assert "compiled: 2026-05-14 05:20" in text, "compiled: did not follow the newest ingest"


CASES = [
    ("the summary anchors on the earliest topic in document order",
     case_anchor_is_earliest_in_document_order),
    ("every cross-reference points backwards", case_every_cross_reference_points_backwards),
    ("every anchor in the document resolves", case_every_anchor_in_the_document_resolves),
    ("a subtitle change rewrites the file", case_a_subtitle_change_rewrites_the_file),
    ("a moved stamp is written and named as a check",
     case_a_moved_stamp_is_written_and_named_as_a_check),
    ("a still clock writes nothing", case_a_still_clock_writes_nothing),
    ("an unreadable mirror is said on every run", case_an_unreadable_mirror_is_said_on_every_run),
    ("the stamp is outside the edition digest", case_the_stamp_is_outside_the_edition_digest),
    ("an empty window is a finished bulletin", case_an_empty_window_is_a_finished_bulletin),
    ("the byline states the days in hand", case_the_byline_states_the_days_in_hand),
    ("a missing summary stops the run", case_a_missing_summary_stops_the_run),
    ("nothing selected is ever dropped", case_nothing_selected_is_ever_dropped),
    ("out-of-remit records are named, not dropped", case_out_of_remit_records_are_named_not_dropped),
    ("country boxes are countries only", case_country_boxes_are_countries_only),
    ("the nav bar holds only the categories present",
     case_the_nav_bar_holds_only_the_categories_present),
    ("the byline is when collection stopped, not when ingest finished",
     case_the_byline_is_when_collection_stopped_not_when_ingest_finished),
    ("a later ingest of the same catch does not move the byline",
     case_a_run_that_only_ingests_later_does_not_move_the_byline),
]


def run() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    failures = 0
    for name, case in CASES:
        tmp = Path(tempfile.mkdtemp(prefix="bulletin-"))
        bench_saved = {k: getattr(bulletin, k)
                       for k in ("CORPUS", "CATALOGUE", "STORE", "DOCUMENT", "BULLETINS", "RAW")}
        ingest_saved = (bulletin.osint_lib.last_ingest,
                        bulletin.osint_lib.ingest_started)
        try:
            case(tmp)
            print(f"  ok   {name}")
        except AssertionError as e:
            failures += 1
            print(f"  FAIL {name}")
            print(f"       {e}")
        finally:
            for k, v in bench_saved.items():
                setattr(bulletin, k, v)
            (bulletin.osint_lib.last_ingest,
             bulletin.osint_lib.ingest_started) = ingest_saved
            shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print(f"{failures} of {len(CASES)} cases FAILED")
        return 1
    print(f"all {len(CASES)} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
