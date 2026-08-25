#!/usr/bin/env python3
"""test_render_gate.py — prove `render.py` cuts an edition when, and only when, it should.

The gate decides *whether* to cut one; the naming rule decides what it is called when two are
cut in a day. Both are design.md §9 and both are here, because they fail together: a gate that
holds off correctly still overwrites a published citation if the name it picks is taken.

    python scripts/test_render_gate.py

A gate that has only ever passed is not evidence of anything (`test_mirror_freshness.py`
makes the same argument), and this one fails in two directions rather than one. Too eager and it
cuts 241 dated PDFs a day that nobody asked for, which is the bloat it was written to stop.
Too keen to hold off and a document that has genuinely moved keeps a stale edition and is
never rendered again — silently, because holding off is what success looks like from the
outside. Both directions are cases below.

Two cases cut real PDFs, so the run takes a few seconds. They are worth their cost: they are
the two branches that decide an *edition name* rather than whether to render at all, and a
name is the thing a citation rests on. The grammar those names are built from is
`editions.py`, and it is tested by `test_editions.py`.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "render", Path(__file__).resolve().parent / "render.py")
render_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(render_mod)

CORPUS = Path(__file__).resolve().parent.parent
SOURCE = CORPUS / "outputs" / "reports" / "KEN" / "KEN-status.md"


def fixture(tmp: Path, pdf: bool = False):
    """A copy of a real report, rendered once. Returns (src, out, html, edition).

    A real document rather than a fabricated one: the gate digests the body, and a two-line
    stand-in would not exercise the frontmatter split that decides where the body starts."""
    src_dir, out = tmp / "src", tmp / "out"
    src_dir.mkdir(parents=True)
    src = src_dir / SOURCE.name
    shutil.copy(SOURCE, src)
    html, _, minted = render_mod.render(src, out, pdf=pdf)
    return src, out, html, minted


def edition_of(html: Path) -> str:
    return render_mod.PRIOR_EDITION.search(html.read_text(encoding="utf-8")).group(1)


def record_of(html: Path) -> str:
    return render_mod.PRIOR_RECORD.search(html.read_text(encoding="utf-8")).group(1)


def case_first_render(tmp):
    _, _, html, minted = fixture(tmp)
    assert minted, "the first render must cut an edition"
    assert record_of(html), "the page must carry the record it was cut from"


def case_unchanged_holds_off(tmp):
    src, out, html, _ = fixture(tmp)
    was = html.stat().st_mtime_ns
    _, _, minted = render_mod.render(src, out, pdf=False)
    assert not minted, "an unchanged source must not cut a second edition"
    assert html.stat().st_mtime_ns == was, "an unchanged source must not rewrite the page"


def case_moved_body_cuts(tmp):
    src, out, html, _ = fixture(tmp)
    before = record_of(html)
    with src.open("a", encoding="utf-8") as fh:
        fh.write("\nA sentence that was not there before.\n")
    _, _, minted = render_mod.render(src, out, pdf=False)
    assert minted, "a body that has moved must cut an edition"
    assert record_of(html) != before, "the record must move with the body"


def case_frontmatter_only_holds_off(tmp):
    """`compiled:` moves whenever the source is rewritten, so a digest that covered the
    frontmatter would fire on every run and the gate would never hold off once."""
    src, out, _, _ = fixture(tmp)
    text = src.read_text(encoding="utf-8")
    assert "compiled:" in text, "the fixture must carry the field this case is about"
    src.write_text(text.replace("compiled:", "compiled: 2099-01-01 #", 1),
                   encoding="utf-8", newline="")
    _, _, minted = render_mod.render(src, out, pdf=False)
    assert not minted, "a frontmatter-only change must not cut an edition"


BULLETIN = CORPUS / "outputs" / "bulletins" / "corpus-bulletin.md"


def bulletin_fixture(tmp):
    src_dir, out = tmp / "src", tmp / "out"
    src_dir.mkdir(parents=True)
    src = src_dir / BULLETIN.name
    shutil.copy(BULLETIN, src)
    html, _, _ = render_mod.render(src, out, pdf=False)
    return src, out, html


def case_the_bulletin_refreshes_its_page_while_holding_its_edition(tmp):
    """**A moved clock reaches the page and not the PDF** *(Bill, 2026-08-21)*.

    A sweep that admits fifty sources of which none is dated inside the two-day window has
    still updated the bulletin: we looked, and nothing was published. A page that goes on
    saying *last updated the 20th* through that reports neglect where there was work. So the
    gate holds the edition — the news has not moved, and two editions holding the same news
    under different names is what §9 exists to stop — while the page is rewritten so the byline
    is current. Both halves are asserted here, because either alone is a fault: no refresh and
    the page reads as stale, no hold and the bulletin mints a PDF every sweep for ever."""
    if not BULLETIN.exists():
        return
    src, out, html = bulletin_fixture(tmp)
    text = src.read_text(encoding="utf-8")
    assert "compiled:" in text and "Last updated" in text, "the fixture must carry both fields"
    moved = text.replace("Last updated ", "Last updated at some later hour ", 1)
    src.write_text(moved, encoding="utf-8", newline="")

    _, _, minted = render_mod.render(src, out, pdf=False)
    assert not minted, "a moved clock must not cut a bulletin edition"
    assert "Last updated at some later hour" in html.read_text(encoding="utf-8"), \
        "the refreshed byline never reached the served page"


def case_a_report_page_is_not_refreshed_in_place(tmp):
    """The exception above is the bulletin's alone. Everywhere else the frontmatter is
    machinery, and a held-off document is left entirely alone, page included."""
    src, out, html, _ = fixture(tmp)
    was = html.stat().st_mtime_ns
    text = src.read_text(encoding="utf-8")
    src.write_text(text.replace("compiled:", "compiled: 2099-01-01 #", 1),
                   encoding="utf-8", newline="")
    render_mod.render(src, out, pdf=False)
    assert html.stat().st_mtime_ns == was, "a held-off report must not have its page rewritten"


def case_missing_pdf_is_repaired_in_place(tmp):
    src, out, html, _ = fixture(tmp, pdf=True)
    edition = edition_of(html)
    pdf = out / f"{src.stem}-{edition}.pdf"
    assert pdf.exists(), "the fixture must have cut a PDF to delete"
    pdf.unlink()
    _, again, minted = render_mod.render(src, out, pdf=True)
    assert minted, "an edition whose PDF is gone must be cut again"
    assert again == pdf, "the repair must restore the published name, not mint a new one"
    assert edition_of(html) == edition, "the page must still name the edition it named"


def case_a_published_edition_is_never_overwritten(tmp):
    """The whole point of the suffix, end to end: cut, move the body, cut again the same day,
    and the first PDF must still be the bytes that were published under its name."""
    src, out, html, _ = fixture(tmp, pdf=True)
    first = out / f"{src.stem}-{edition_of(html)}.pdf"
    was = first.read_bytes()

    with src.open("a", encoding="utf-8") as fh:
        fh.write("\nA sentence that was not there before.\n")
    _, second, minted = render_mod.render(src, out, pdf=True)

    assert minted, "a body that has moved must cut an edition"
    assert second != first, "the second cut of a day must not take the first's name"
    assert second.name.endswith("-2.pdf"), f"expected a -2 suffix, got {second.name}"
    assert first.read_bytes() == was, "the published edition must be untouched, to the byte"
    assert edition_of(html).endswith("-2"), "the page must now name the edition it offers"


def case_force_overrides(tmp):
    src, out, _, _ = fixture(tmp)
    _, _, minted = render_mod.render(src, out, pdf=False, force=True)
    assert minted, "--force must cut whatever the gate thinks"


def case_explicit_edition_overrides(tmp):
    src, out, _, _ = fixture(tmp)
    _, _, minted = render_mod.render(src, out, edition="2026-01-01", pdf=False)
    assert minted, "an explicit --edition must cut whatever the gate thinks"


def case_page_without_a_record_cuts(tmp):
    """Every page served before 2026-08-18 is this case. It must cut rather than adopt the
    edition it finds: with no record there is nothing to compare, and adopting would keep a
    stale edition for a document that had moved — and then never notice, because the record
    stamped in would be the current one."""
    src, out, html, _ = fixture(tmp)
    html.write_text(
        html.read_text(encoding="utf-8").replace('<meta name="dl-record"', '<meta name="was"'),
        encoding="utf-8", newline="")
    _, _, minted = render_mod.render(src, out, pdf=False)
    assert minted, "a page written before the gate existed must cut an edition"


CASES = [
    ("a first render cuts an edition", case_first_render),
    ("an unchanged source cuts nothing and rewrites nothing", case_unchanged_holds_off),
    ("a body that has moved cuts an edition", case_moved_body_cuts),
    ("a frontmatter-only change cuts nothing", case_frontmatter_only_holds_off),
    ("the bulletin refreshes its page while holding its edition",
     case_the_bulletin_refreshes_its_page_while_holding_its_edition),
    ("a report's page is not refreshed in place", case_a_report_page_is_not_refreshed_in_place),
    ("a deleted PDF is re-cut under its own name", case_missing_pdf_is_repaired_in_place),
    ("a published edition survives a same-day re-cut, to the byte", case_a_published_edition_is_never_overwritten),
    ("--force cuts regardless", case_force_overrides),
    ("an explicit --edition cuts regardless", case_explicit_edition_overrides),
    ("a page carrying no record cuts", case_page_without_a_record_cuts),
]


def run() -> int:
    if not SOURCE.exists():
        print(f"no source to test against: {SOURCE}")
        return 2

    failures = 0
    for name, case in CASES:
        tmp = Path(tempfile.mkdtemp(prefix="render-gate-"))
        try:
            case(tmp)
            print(f"  ok   {name}")
        except AssertionError as e:
            failures += 1
            print(f"  FAIL {name}")
            print(f"       {e}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print(f"{failures} of {len(CASES)} cases FAILED")
        return 1
    print(f"all {len(CASES)} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
