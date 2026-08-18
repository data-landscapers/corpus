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


CASES = [
    ("the edition grammar parses every name in the tree", case_grammar),
    ("editions order by date, then by same-day sequence as a number", case_ordering),
    ("same-day editions take -2, -3, per document", case_suffix_is_taken_in_order),
    ("a document whose name is another's prefix keeps its own editions", case_a_prefix_is_not_a_document),
    ("publish cuts once, then holds off on unchanged bytes", case_publish_cuts_then_holds_off),
    ("publish cuts again when the bytes move, retaining the earlier edition", case_publish_cuts_on_a_change),
    ("a second publish in a day is suffixed, not overwritten", case_publish_suffixes_within_a_day),
    ("the undated predecessor is retired either way", case_undated_predecessor_is_retired),
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
