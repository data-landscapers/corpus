#!/usr/bin/env python3
"""test_editions.py — prove §9's edition rules: the grammar, the suffix, and the publish gate.

    python scripts/test_editions.py

Every case here is something that fails **silently**. A misparsed edition does not raise: it
makes a page offer a superseded file, which looks exactly like a page offering the current one.
A suffix that is not taken overwrites a published citation, and the site serves the new bytes
under the old name without a word. A publish gate that never holds off just grows the repo.
None of it is visible from the output of a run, which is why it is visible here instead.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "editions", Path(__file__).resolve().parent / "editions.py")
ed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ed)

TODAY = "2026-08-18"


def case_grammar(tmp):
    assert ed.edition_of("KEN-status-2026-08-18") == "2026-08-18"
    assert ed.edition_of("KEN-status-2026-08-18-2") == "2026-08-18-2", \
        "a suffixed edition must parse whole"
    assert ed.edition_of("KEN-monthly-2026-07-2026-08-05") == "2026-08-05", \
        "a name still carrying its period must yield the edition, not the window"
    assert ed.edition_of("KEN-status") is None, "an undated name carries no edition"
    assert ed.edition_of("KEN-nonstate-fields") is None


def case_ordering(tmp):
    key = ed.edition_key
    assert key("2026-08-18-2") > key("2026-08-18"), "a same-day second edition is the newer"
    assert key("2026-08-18-10") > key("2026-08-18-2"), "the sequence orders as a number"
    assert key("2026-08-19") > key("2026-08-18-9"), "the date orders first"
    assert max(["2026-08-18-2", "2026-08-18"], key=key) == "2026-08-18-2"


def case_suffix_is_taken_in_order(tmp):
    assert ed.next_edition(tmp, "KEN-status", TODAY) == TODAY, \
        "the first edition of a day carries no suffix"
    (tmp / f"KEN-status-{TODAY}.pdf").touch()
    assert ed.next_edition(tmp, "KEN-status", TODAY) == f"{TODAY}-2"
    (tmp / f"KEN-status-{TODAY}-2.pdf").touch()
    assert ed.next_edition(tmp, "KEN-status", TODAY) == f"{TODAY}-3"
    (tmp / f"KEN-monthly-{TODAY}.pdf").touch()
    assert ed.next_edition(tmp, "KEN-progress", TODAY) == TODAY, \
        "another document's editions must not shift this one's"


def case_a_prefix_is_not_a_document(tmp):
    """`KEN-nonstate-*` also matches `KEN-nonstate-fields-…`, which is a different document
    that happens to begin with this one's name. Without the exact-name test the finance CSV
    would take its edition from its own field dictionary — and would then hold off on
    publishing whenever the dictionary happened to match."""
    (tmp / f"KEN-nonstate-fields-{TODAY}.csv").write_bytes(b"field,definition\n")
    assert ed.latest(tmp, "KEN-nonstate", ".csv") is None, \
        "a longer document's edition must not be read as this one's"
    assert ed.latest(tmp, "KEN-nonstate-fields", ".csv") is not None

    path, minted = ed.publish(b"a,b\n1,2\n", tmp, "KEN-nonstate", ".csv", today=TODAY)
    assert minted and path.name == f"KEN-nonstate-{TODAY}.csv", path.name


def case_publish_cuts_then_holds_off(tmp):
    data = b"recipient_country,commitment_usd_m\nKEN,24\n"
    first, minted = ed.publish(data, tmp, "KEN-nonstate", ".csv", today=TODAY)
    assert minted, "the first publish must cut an edition"
    assert first.name == f"KEN-nonstate-{TODAY}.csv"

    again, minted = ed.publish(data, tmp, "KEN-nonstate", ".csv", today="2026-08-19")
    assert not minted, "unchanged bytes must not cut a second edition"
    assert again == first, "and must go on offering the edition already published"
    assert len(list(tmp.glob("KEN-nonstate-*.csv"))) == 1


def case_publish_cuts_on_a_change(tmp):
    ed.publish(b"a,b\n1,2\n", tmp, "KEN-nonstate", ".csv", today=TODAY)
    second, minted = ed.publish(b"a,b\n1,3\n", tmp, "KEN-nonstate", ".csv", today="2026-08-19")
    assert minted and second.name == "KEN-nonstate-2026-08-19.csv", second.name
    assert (tmp / f"KEN-nonstate-{TODAY}.csv").read_bytes() == b"a,b\n1,2\n", \
        "the earlier edition must be retained, untouched"


def case_publish_suffixes_within_a_day(tmp):
    ed.publish(b"a,b\n1,2\n", tmp, "KEN-nonstate", ".csv", today=TODAY)
    second, minted = ed.publish(b"a,b\n1,3\n", tmp, "KEN-nonstate", ".csv", today=TODAY)
    assert minted and second.name == f"KEN-nonstate-{TODAY}-2.csv", second.name
    assert (tmp / f"KEN-nonstate-{TODAY}.csv").read_bytes() == b"a,b\n1,2\n", \
        "the morning's edition must survive an afternoon change, to the byte"
    assert ed.latest(tmp, "KEN-nonstate", ".csv") == second, "and the newer one is current"


def case_undated_predecessor_is_retired(tmp):
    """§9 allows no undated download URL. `site/` is never purged, so one that stops being
    written stays there and goes on being served."""
    stale = tmp / "KEN-nonstate.csv"
    stale.write_bytes(b"a,b\n1,2\n")
    path, minted = ed.publish(b"a,b\n1,2\n", tmp, "KEN-nonstate", ".csv", today=TODAY)
    assert minted, "an undated file is not an edition and cannot be compared against"
    assert not stale.exists(), "the undated predecessor must be removed"
    assert path.exists()

    # And on a run that cuts nothing: the removal must not depend on a new edition.
    stale.write_bytes(b"a,b\n1,2\n")
    _, minted = ed.publish(b"a,b\n1,2\n", tmp, "KEN-nonstate", ".csv", today=TODAY)
    assert not minted
    assert not stale.exists(), "a held-off publish must still retire the undated name"


# ---------------------------------------------------------------------------
# The pruned tree: what these functions can still see after the editions move
# ---------------------------------------------------------------------------

"""Since 2026-09-08 the dated file is uploaded to R2 and deleted from the tree, so every case
below runs against an **empty directory** — which is the state a render actually finds. Each
one failed before the page became the record, and each failed silently: the suffix cases by
overwriting a published name, the publish cases by minting an edition that revises nothing."""


def page_with(tmp: Path, name: str, *artefacts: tuple[str, str, str]) -> Path:
    """A page as the previous render left it, carrying its own edition and its artefacts'."""
    page = tmp / name
    page.write_text(
        "<html><head>\n"
        + "\n".join(ed.artefact_meta(*a) for a in artefacts)
        + '\n</head><body><div class="article-header__byline" data-edition="IGNORED">'
          "</div></body></html>",
        encoding="utf-8")
    return page


def case_the_page_names_the_edition_when_the_tree_is_empty(tmp):
    page = tmp / "KEN-status.html"
    page.write_text('<div data-edition="2026-09-09">x</div>', encoding="utf-8")
    assert ed.edition_on_page(page) == "2026-09-09"
    assert ed.edition_on_page(tmp / "nothing.html") is None
    # A page from before the field existed says nothing rather than guessing.
    bare = tmp / "old.html"
    bare.write_text("<html></html>", encoding="utf-8")
    assert ed.edition_on_page(bare) is None


def case_a_pruned_tree_still_suffixes_the_second_edition(tmp):
    """The 44-PDF failure of 2026-09-09, as a test. Nothing on disk; the morning's edition is
    known only from the page, and the afternoon's cut must not land on its name."""
    page = tmp / "dpi-id-progress.html"
    page.write_text('<div data-edition="2026-09-09">x</div>', encoding="utf-8")
    got = ed.next_edition(tmp, "dpi-id-progress", "2026-09-09",
                          current=ed.edition_on_page(page))
    assert got == "2026-09-09-2", f"reused the published name: {got}"
    page.write_text('<div data-edition="2026-09-09-2">x</div>', encoding="utf-8")
    assert ed.next_edition(tmp, "dpi-id-progress", "2026-09-09",
                           current=ed.edition_on_page(page)) == "2026-09-09-3"


def case_a_page_from_another_day_does_not_suffix(tmp):
    """Yesterday's edition is not a name taken today: today's first cut stays unsuffixed."""
    assert ed.next_edition(tmp, "KEN-status", TODAY, current="2026-08-01") == TODAY


def case_disk_and_page_are_both_consulted(tmp):
    """Whichever knows about more editions wins. Disk covers a file written earlier in this
    same run, before any sync; the page covers everything already published."""
    (tmp / f"KEN-status-{TODAY}.pdf").write_bytes(b"x")
    assert ed.next_edition(tmp, "KEN-status", TODAY, current=None) == f"{TODAY}-2"
    assert ed.next_edition(tmp, "KEN-status", TODAY, current=f"{TODAY}-2") == f"{TODAY}-3"
    assert ed.next_edition(tmp, "KEN-status", TODAY, current="2026-01-01") == f"{TODAY}-2"


def case_publish_holds_off_on_the_page_record_alone(tmp):
    """The 61-CSV churn. The published file is in the bucket, not the tree; the page's digest
    says the bytes have not moved, so no edition is cut and the standing name comes back."""
    data = b"a,b\n1,2\n"
    page = page_with(tmp, "finance.html",
                     ("KEN-nonstate", "2026-09-04", ed.digest(data)))
    path, minted = ed.publish(data, tmp, "KEN-nonstate", ".csv", today=TODAY, page=page)
    assert not minted, "minted an edition over an unchanged CSV that was already published"
    assert path.name == "KEN-nonstate-2026-09-04.csv", path.name
    assert not list(tmp.glob("*.csv")), "wrote a file for an edition it did not cut"


def case_publish_cuts_when_the_page_record_differs(tmp):
    data = b"a,b\n1,3\n"
    page = page_with(tmp, "finance.html",
                     ("KEN-nonstate", "2026-09-04", ed.digest(b"a,b\n1,2\n")))
    path, minted = ed.publish(data, tmp, "KEN-nonstate", ".csv", today=TODAY, page=page)
    assert minted and path.name == f"KEN-nonstate-{TODAY}.csv", path.name
    assert path.read_bytes() == data


def case_publish_suffixes_against_the_page_when_the_tree_is_empty(tmp):
    """Changed twice in a day, with the first cut already pruned out of the tree."""
    page = page_with(tmp, "finance.html",
                     ("KEN-nonstate", TODAY, ed.digest(b"a,b\n1,2\n")))
    path, minted = ed.publish(b"a,b\n1,9\n", tmp, "KEN-nonstate", ".csv",
                              today=TODAY, page=page)
    assert minted and path.name == f"KEN-nonstate-{TODAY}-2.csv", path.name


def case_one_page_records_several_artefacts(tmp):
    page = page_with(tmp, "finance.html",
                     ("KEN-nonstate", "2026-09-04", "a" * 12),
                     ("all-nonstate", "2026-09-07", "b" * 12))
    got = ed.artefacts_on_page(page)
    assert got == {"KEN-nonstate": ("2026-09-04", "a" * 12),
                   "all-nonstate": ("2026-09-07", "b" * 12)}, got
    # A stem this page says nothing about must not borrow another's record.
    path, minted = ed.publish(b"z", tmp, "XXX-nonstate", ".csv", today=TODAY, page=page)
    assert minted and path.name == f"XXX-nonstate-{TODAY}.csv", path.name


def case_no_page_falls_back_to_minting(tmp):
    """Wrong only in the safe direction: an edition minted needlessly, never a name reused."""
    path, minted = ed.publish(b"a", tmp, "KEN-nonstate", ".csv", today=TODAY, page=None)
    assert minted and path.name == f"KEN-nonstate-{TODAY}.csv"
    assert ed.next_edition(tmp, "KEN-status", TODAY, current=None) == TODAY


CASES = [
    ("the edition grammar parses every name in the tree", case_grammar),
    ("editions order by date, then by same-day sequence as a number", case_ordering),
    ("same-day editions take -2, -3, per document", case_suffix_is_taken_in_order),
    ("a document whose name is another's prefix keeps its own editions", case_a_prefix_is_not_a_document),
    ("publish cuts once, then holds off on unchanged bytes", case_publish_cuts_then_holds_off),
    ("publish cuts again when the bytes move, retaining the earlier edition", case_publish_cuts_on_a_change),
    ("a second publish in a day is suffixed, not overwritten", case_publish_suffixes_within_a_day),
    ("the undated predecessor is retired either way", case_undated_predecessor_is_retired),
    ("the page names the edition when the tree is empty",
     case_the_page_names_the_edition_when_the_tree_is_empty),
    ("a pruned tree still suffixes the second edition of a day",
     case_a_pruned_tree_still_suffixes_the_second_edition),
    ("yesterday's edition does not suffix today's first",
     case_a_page_from_another_day_does_not_suffix),
    ("disk and page are both consulted, the higher wins",
     case_disk_and_page_are_both_consulted),
    ("publish holds off on the page record alone",
     case_publish_holds_off_on_the_page_record_alone),
    ("publish cuts when the page record differs",
     case_publish_cuts_when_the_page_record_differs),
    ("publish suffixes against the page when the tree is empty",
     case_publish_suffixes_against_the_page_when_the_tree_is_empty),
    ("one page records several artefacts, each its own",
     case_one_page_records_several_artefacts),
    ("no page at all falls back to minting", case_no_page_falls_back_to_minting),
]


def run() -> int:
    failures = 0
    for name, case in CASES:
        tmp = Path(tempfile.mkdtemp(prefix="editions-"))
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
