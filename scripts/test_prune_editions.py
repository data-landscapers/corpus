#!/usr/bin/env python3
"""test_prune_editions.py — prove the deletion rule fails towards *keep*, every way it can fail.

    python scripts/test_prune_editions.py

`prune-editions.py` is the only script in this repo that destroys a published artefact, and it
decides from a record gathered on somebody else's machine. Nothing about a wrong decision is
visible afterwards: the file is gone, the run says it deleted something, and the person who
meets the 404 is a reader we never hear from. So the cases here are almost all *refusals* —
the conditions under which it must delete nothing — and only one of them is a deletion.
"""

from __future__ import annotations

import importlib.util
import io
import contextlib
import shutil
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "prune_editions", Path(__file__).resolve().parent / "prune-editions.py")
pe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pe)

TODAY = "2026-09-30"          # well clear of the lag and the forward-only cutoff
FORWARD = pe.FORWARD_FROM     # 2026-08-19


def put(site: Path, rel: str, body: bytes = b"x") -> Path:
    p = site / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(body)
    return p


def verdicts(site: Path, keys=(), today=TODAY, lag=7) -> dict:
    rows = pe.plan(site, pe.fetched_set(list(keys)), today, FORWARD, lag)
    return {r["rel"]: (r["verdict"], r["why"]) for r in rows}


def run_main(argv) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = pe.main(argv)
    return code, out.getvalue()


# --------------------------------------------------------------------------- the decision

def case_current_edition_is_never_deleted(tmp):
    put(tmp, "reports/KEN/KEN-status-2026-08-20.pdf")
    v = verdicts(tmp)
    assert v["reports/KEN/KEN-status-2026-08-20.pdf"][0] == "keep", \
        "the only edition of a document is what the site is offering — never a candidate"

    put(tmp, "reports/KEN/KEN-status-2026-08-25.pdf")
    v = verdicts(tmp)
    assert v["reports/KEN/KEN-status-2026-08-25.pdf"] == ("keep", "current edition")
    assert v["reports/KEN/KEN-status-2026-08-20.pdf"][0] == "delete", \
        "a superseded, unfetched, out-of-lag edition published after the rule is the case this exists for"


def case_the_set_already_published_stands(tmp):
    put(tmp, "reports/KEN/KEN-status-2026-08-14.pdf")
    put(tmp, "reports/KEN/KEN-status-2026-08-18.pdf")     # the day the Worker went live
    put(tmp, "reports/KEN/KEN-status-2026-08-26.pdf")
    v = verdicts(tmp)
    assert v["reports/KEN/KEN-status-2026-08-14.pdf"] == ("keep", "published before the rule")
    assert v["reports/KEN/KEN-status-2026-08-18.pdf"] == ("keep", "published before the rule"), \
        "the Worker's own first day has a partial record and is not evidence of anything"


def case_the_lag_holds_a_fresh_supersession(tmp):
    put(tmp, "reports/KEN/KEN-status-2026-09-20.pdf")
    put(tmp, "reports/KEN/KEN-status-2026-09-26.pdf")     # 4 days ago
    v = verdicts(tmp)
    assert v["reports/KEN/KEN-status-2026-09-20.pdf"][0] == "keep", \
        "a log entry that arrived late must still arrive before the deletion"
    v = verdicts(tmp, today="2026-10-05")
    assert v["reports/KEN/KEN-status-2026-09-20.pdf"][0] == "delete", \
        "and once the lag is past, the same file is deletable"


def case_any_fetch_at_all_protects(tmp):
    put(tmp, "reports/KEN/KEN-status-2026-08-20.pdf")
    put(tmp, "reports/KEN/KEN-status-2026-08-25.pdf")
    for key in ("reports/KEN/KEN-status-2026-08-20.pdf",          # as the Worker writes it
                "/reports/KEN/KEN-status-2026-08-20.pdf",         # with the leading slash
                "reports/ken/ken-status-2026-08-20.pdf",          # a casing difference
                "reports/KEN/KEN%2Dstatus%2D2026%2D08%2D20.pdf"):  # percent-encoded
        v = verdicts(tmp, keys=[key])
        assert v["reports/KEN/KEN-status-2026-08-20.pdf"] == ("keep", "downloaded"), \
            f"a key that fails to match the file it names deletes that file: {key}"


def case_a_second_edition_in_a_day_is_the_current_one(tmp):
    put(tmp, "reports/KEN/KEN-status-2026-08-20.pdf")
    put(tmp, "reports/KEN/KEN-status-2026-08-20-2.pdf")
    v = verdicts(tmp)
    assert v["reports/KEN/KEN-status-2026-08-20-2.pdf"] == ("keep", "current edition"), \
        "string order puts -2 first; the edition key is what decides which is current"
    assert v["reports/KEN/KEN-status-2026-08-20.pdf"][0] == "delete"


def case_a_field_dictionary_is_its_own_document(tmp):
    put(tmp, "countries/KEN/KEN-nonstate-2026-08-20.csv")
    put(tmp, "countries/KEN/KEN-nonstate-fields-2026-08-25.csv")
    v = verdicts(tmp)
    assert v["countries/KEN/KEN-nonstate-2026-08-20.csv"] == ("keep", "current edition"), \
        "the dictionary is a different document and cannot supersede the data it describes"
    assert v["countries/KEN/KEN-nonstate-fields-2026-08-25.csv"] == ("keep", "current edition")


def case_an_undated_download_is_invisible(tmp):
    put(tmp, "catalogue/raw-catalogue.csv")
    put(tmp, "assets/report.css")
    put(tmp, "reports/KEN/KEN-status-2026-08-20.pdf")
    v = verdicts(tmp)
    assert "catalogue/raw-catalogue.csv" not in v, \
        "the catalogue is not an edition (§9) and this rule must not have an opinion about it"
    assert "assets/report.css" not in v, "only .pdf and .csv carry editions"


# --------------------------------------------------------------------------- the refusals

def case_an_unreadable_record_deletes_nothing(tmp):
    put(tmp, "reports/KEN/KEN-status-2026-08-20.pdf")
    put(tmp, "reports/KEN/KEN-status-2026-08-25.pdf")
    code, out = run_main(["--apply", "--site", str(tmp), "--today", TODAY,
                          "--keys-from", str(tmp / "nothing-here.txt")])
    assert code == 0, "a record that cannot be read is a normal outcome, not a fault"
    assert "declined" in out and (tmp / "reports/KEN/KEN-status-2026-08-20.pdf").exists(), \
        "no record means no deletion of anything the record governs — which is everything but the bulletin"


def case_an_empty_record_deletes_nothing(tmp):
    put(tmp, "reports/KEN/KEN-status-2026-08-20.pdf")
    put(tmp, "reports/KEN/KEN-status-2026-08-25.pdf")
    (tmp / "keys.txt").write_text("", encoding="utf-8")
    code, out = run_main(["--apply", "--site", str(tmp), "--today", TODAY,
                          "--keys-from", str(tmp / "keys.txt")])
    assert code == 0 and "declined" in out
    assert (tmp / "reports/KEN/KEN-status-2026-08-20.pdf").exists(), \
        "an unbound namespace and a site nobody reads produce the same empty listing"


def case_a_stale_record_deletes_nothing(tmp):
    put(tmp, "reports/KEN/KEN-status-2026-08-20.pdf")
    put(tmp, "reports/KEN/KEN-status-2026-08-25.pdf")
    (tmp / "keys.txt").write_text("reports/TCD/TCD-status-2026-08-19.pdf\n", encoding="utf-8")
    code, out = run_main(["--apply", "--site", str(tmp), "--today", TODAY,
                          "--keys-from", str(tmp / "keys.txt")])
    assert code == 0 and "declined" in out, out
    assert (tmp / "reports/KEN/KEN-status-2026-08-20.pdf").exists(), \
        "the newest edition in the record is six weeks old: the Worker may simply be dead"


def case_without_apply_it_deletes_nothing(tmp):
    put(tmp, "reports/KEN/KEN-status-2026-08-20.pdf")
    put(tmp, "reports/KEN/KEN-status-2026-09-01.pdf")
    (tmp / "keys.txt").write_text("reports/TCD/TCD-status-2026-09-28.pdf\n", encoding="utf-8")
    code, out = run_main(["--site", str(tmp), "--today", TODAY, "--keys-from", str(tmp / "keys.txt")])
    assert code == 0 and "would delete" in out, out
    assert (tmp / "reports/KEN/KEN-status-2026-08-20.pdf").exists(), \
        "the default run is a report; deleting takes --apply"


# --------------------------------------------------------------------------- the bulletin branch
#
# The bulletin leaves the download rule and takes a stated retention window instead
# (`documentation/bulletin-archive.md`). These cases exist because that is the one place in this
# script where the safe direction is *delete*: the colophon of every bulletin PDF prints the date
# it is kept until, so a window that quietly stops being applied makes a published promise false.

def case_a_bulletin_inside_its_window_is_kept(tmp):
    put(tmp, "bulletin/corpus-bulletin-2026-09-26.pdf")
    put(tmp, "bulletin/corpus-bulletin-2026-09-30.pdf")
    v = verdicts(tmp)
    assert v["bulletin/corpus-bulletin-2026-09-26.pdf"][0] == "keep", \
        "four days old, superseded, never fetched — the window is the only test that applies"


def case_a_fetched_bulletin_past_its_window_still_goes(tmp):
    """The sharp edge, and the whole reason this is a branch rather than a sixth condition."""
    doomed = put(tmp, "bulletin/corpus-bulletin-2026-09-01.pdf")
    put(tmp, "bulletin/corpus-bulletin-2026-09-30.pdf")
    v = verdicts(tmp, keys=["bulletin/corpus-bulletin-2026-09-01.pdf"])
    assert v[doomed.relative_to(tmp).as_posix()][0] == "delete", \
        ("a download must not outrank the retention the page printed — otherwise the promise "
         "holds for every bulletin except the ones a reader actually took")


def case_the_current_bulletin_is_never_deleted(tmp):
    put(tmp, "bulletin/corpus-bulletin-2026-01-05.pdf")
    v = verdicts(tmp)
    assert v["bulletin/corpus-bulletin-2026-01-05.pdf"] == ("keep", "current edition"), \
        "after a quiet month the live page must still be able to offer its own PDF"


def case_bulletins_prune_without_a_download_record(tmp):
    """No Cloudflare token: everything else correctly declines, the bulletin window does not."""
    doomed = put(tmp, "bulletin/corpus-bulletin-2026-09-01.pdf")
    put(tmp, "bulletin/corpus-bulletin-2026-09-30.pdf")
    report = put(tmp, "reports/KEN/KEN-status-2026-08-20.pdf")
    put(tmp, "reports/KEN/KEN-status-2026-09-25.pdf")
    ledger = tmp / "ledger.csv"
    code, out = run_main(["--apply", "--site", str(tmp), "--today", TODAY, "--ledger", str(ledger),
                          "--keys-from", str(tmp / "no-such-file.txt")])
    assert code == 0, out
    assert not doomed.exists(), "the bulletin window does not depend on the download record"
    assert report.exists(), "everything the record governs still keeps when it cannot be read"
    assert "declined" in out, out


def case_deleting_a_bulletin_rewrites_the_listing(tmp):
    """The party doing the deleting owns the listing, or the picker offers a file that is gone."""
    import json
    doomed = put(tmp, "bulletin/corpus-bulletin-2026-09-01.pdf")
    current = put(tmp, "bulletin/corpus-bulletin-2026-09-30.pdf")
    (tmp / "bulletin" / "editions.json").write_text(json.dumps({"retention_days": 7, "editions": [
        {"edition": "2026-09-30", "file": current.name, "compiled": "2026-09-30 06:00", "items": 9},
        {"edition": "2026-09-01", "file": doomed.name, "compiled": "2026-09-01 06:00", "items": 4},
    ]}), encoding="utf-8")
    code, out = run_main(["--apply", "--site", str(tmp), "--today", TODAY,
                          "--ledger", str(tmp / "ledger.csv"),
                          "--keys-from", str(tmp / "none.txt")])
    assert code == 0 and not doomed.exists(), out
    listed = json.loads((tmp / "bulletin" / "editions.json").read_text(encoding="utf-8"))
    names = [e["file"] for e in listed["editions"]]
    assert names == [current.name], f"the deleted edition must leave the listing too: {names}"


# --------------------------------------------------------------------------- the one deletion

def case_apply_deletes_and_accounts_for_it(tmp):
    doomed = put(tmp, "reports/KEN/KEN-status-2026-08-20.pdf", b"12345")
    kept = put(tmp, "reports/KEN/KEN-status-2026-08-22.pdf")
    current = put(tmp, "reports/KEN/KEN-status-2026-09-25.pdf")
    (tmp / "keys.txt").write_text(
        "reports/KEN/KEN-status-2026-08-22.pdf\nreports/KEN/KEN-status-2026-09-25.pdf\n", encoding="utf-8")
    ledger = tmp / "deleted-editions.csv"
    held, pe.LEDGER = pe.LEDGER, ledger
    try:
        code, out = run_main(["--apply", "--site", str(tmp), "--today", TODAY,
                              "--keys-from", str(tmp / "keys.txt")])
    finally:
        pe.LEDGER = held
    assert code == 0, out
    assert not doomed.exists(), "the unfetched edition is what this rule is for"
    assert kept.exists() and current.exists(), "a fetched edition and the current one both stay"
    lines = ledger.read_text(encoding="utf-8").strip().splitlines()
    assert lines[0].startswith("deleted_on,"), "the ledger carries a header"
    assert lines[1] == f"{TODAY},reports/KEN/KEN-status-2026-08-20.pdf,2026-08-20,2026-08-22,2026-08-22,5", lines[1]


CASES = [
    ("the current edition is never deleted", case_current_edition_is_never_deleted),
    ("everything published before the rule stands", case_the_set_already_published_stands),
    ("the lag holds a freshly superseded edition", case_the_lag_holds_a_fresh_supersession),
    ("any fetch at all protects, however the key is written", case_any_fetch_at_all_protects),
    ("a same-day second edition is the current one", case_a_second_edition_in_a_day_is_the_current_one),
    ("a field dictionary is its own document", case_a_field_dictionary_is_its_own_document),
    ("an undated download is invisible to the rule", case_an_undated_download_is_invisible),
    ("an unreadable record deletes nothing", case_an_unreadable_record_deletes_nothing),
    ("an empty record deletes nothing", case_an_empty_record_deletes_nothing),
    ("a stale record deletes nothing", case_a_stale_record_deletes_nothing),
    ("without --apply it deletes nothing", case_without_apply_it_deletes_nothing),
    ("a bulletin inside its window is kept", case_a_bulletin_inside_its_window_is_kept),
    ("a fetched bulletin past its window still goes", case_a_fetched_bulletin_past_its_window_still_goes),
    ("the current bulletin is never deleted", case_the_current_bulletin_is_never_deleted),
    ("bulletins prune without a download record", case_bulletins_prune_without_a_download_record),
    ("deleting a bulletin rewrites the listing", case_deleting_a_bulletin_rewrites_the_listing),
    ("--apply deletes the unfetched edition and records it", case_apply_deletes_and_accounts_for_it),
]


def run() -> int:
    failures = 0
    for name, case in CASES:
        tmp = Path(tempfile.mkdtemp(prefix="prune-"))
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
