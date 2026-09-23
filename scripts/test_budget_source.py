#!/usr/bin/env python3
r"""test_budget_source.py — the schema rejects what it says it rejects, and the merge replaces.

    python scripts/test_budget_source.py

Two things here can fail silently and both are expensive.

**A check that does not fire.** These rows replace OSINT's records for a whole country-year,
so a checker that passes a malformed file hands the published export a bad figure with a
citation on it. Every rule in `budget_source.check` is exercised against a row that breaks it
and a row that does not — a checker tested only on good input is indistinguishable from one
that returns an empty list.

**A merge that adds instead of replacing.** The review's rule is replace-never-add (R56a),
and the failure mode is not an error: it is a programme published beside its own
sub-programmes, summing to twice the money, in a file that parses perfectly. So the merge is
tested on the thing that makes it hard — OSINT records whose fiscal year is written three
different ways, all of which have to match the source file's bare start year.
"""
from __future__ import annotations

import csv
import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import budget_source as bs  # noqa: E402

_spec = importlib.util.spec_from_file_location("bfp", HERE / "build-finance-page.py")
bfp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bfp)

fails: list[str] = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
    if not ok:
        print(f"          got {got!r}\n          want {want!r}")
        fails.append(label)


GOOD = {
    "deal_id": "gha-2024-011-01101-01101004", "place": "GHA", "state_level": "national",
    "spending_tier_name": "",
    "fiscal_year_label": "2024", "fy_start": "2024-01-01", "fy_end": "2024-12-31",
    "fy_calendar": "gregorian", "budget_version": "original", "supplementary_basis": "",
    "admin_head_code": "011", "admin_head": "011 - Ministry of Local Government",
    "spending_entity_code": "011", "spending_entity": "Ministry of Local Government",
    "programme_code": "01101", "programme": "Management and Administration",
    "sub_programme_code": "01101004", "sub_programme": "Research, Statistics and IM",
    "econ_class": "",
    "admin_head_basis": "printed", "programme_basis": "printed", "programme_level": "programme",
    "line_name": "Management and Administration — Research, Statistics and IM",
    "purpose": "Runs the ministry's district development data platform and its databases.",
    "primary_subject": "data.statistics",
    "scope_confidence": "partial",
    "scope_basis": "The sub-programme's stated function is information management; research "
                   "and publicity sit in the same line and are not separable.",
    "finance_origin": "domestic-state", "funding_source": "domestic-revenue",
    "is_transfer": "false", "transfer_to": "",
    "currency": "GHS", "amount_scale": "full cedis as printed",
    "proposed": "", "appropriated": "80000", "revised": "", "released": "",
    "actual": "", "audited": "",
    "baseline_stage": "appropriated", "current_stage": "appropriated",
    "exec_vs_voted": "", "exec_vs_revised": "",
    "source_tier": "budget-document", "doc_type": "budget-estimates",
    "doc_locator": "2024 PBB, table 1.5, entity 011, sub-programme 01101004",
    "source_slug": "2024-01-01-gha-pbb-2024-mlgrd-companion",
    "extracted": "2026-09-20",
    "notes": "Cross-footed against the programme's printed total.",
}


def write(root: Path, iso3: str, fy: str, rows: list[dict], header=None) -> Path:
    d = root / iso3
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{fy}.csv"
    with open(p, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(header or bs.COLUMNS))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return p


def row(**over) -> dict:
    r = dict(GOOD)
    r.update(over)
    return r


def failures(root: Path, iso3="") -> list[str]:
    out, _, _ = bs.check(iso3, str(root))
    return out


tmp = Path(tempfile.mkdtemp(prefix="budget-source-test-"))
try:
    # The catalogue check needs a slug set; point it at a real one if the build has run,
    # else at nothing so the check reports itself skipped rather than failing every row.
    bs.CATALOGUE = str(HERE.parent / "outputs" / "catalogue" / "catalogue-internal.csv")
    have_catalogue = os.path.exists(bs.CATALOGUE)

    print("\na row that says everything")
    r = tmp / "clean"
    write(r, "GHA", "2024", [row()])
    check("passes", failures(r), [])

    print("\nthe shape of the file")
    cases = [
        ("a header missing a column", "header is not the schema",
         lambda d: write(d, "GHA", "2024", [{k: v for k, v in row().items() if k != "notes"}],
                         header=[c for c in bs.COLUMNS if c != "notes"])),
        ("a file named for something other than a year", "not a bare fiscal-year start year",
         lambda d: write(d, "GHA", "2024-25", [row()])),
        ("a file with no rows", "no rows",
         lambda d: write(d, "GHA", "2024", [])),
    ]
    for label, want, make in cases:
        d = tmp / label.replace(" ", "-")
        make(d)
        got = failures(d)
        check(label, any(want in f for f in got), True)

    print("\nthe row itself")
    bad = [
        ("place disagreeing with the folder", "the folder is GHA", row(place="KEN")),
        ("a year outside the file's own", "does not begin in 2024", row(
            fy_start="2025-01-01", fy_end="2025-12-31")),
        ("a deal_id for another country", "does not open with gha-", row(
            deal_id="ken-2024-011-01101")),
        ("an unknown state_level", "state_level", row(state_level="municipal")),
        ("an unknown funding_source", "funding_source", row(funding_source="donor")),
        ("an unknown scope_confidence", "scope_confidence", row(scope_confidence="mostly")),
        ("a budget_version off the list", "not original, revised", row(budget_version="supp")),
        ("a supplementary_basis off the list", "supplementary_basis",
         row(supplementary_basis="netted")),
        ("is_transfer that is not a boolean", "is not true or false", row(is_transfer="yes")),
        ("a transfer naming nobody", "transfer_to names nobody", row(is_transfer="true")),
        ("an externally financed line", "domestic-state side",
         row(finance_origin="non-state")),
        ("a currency that is not a code", "not a three-letter code", row(currency="cedi")),
        ("money with separators in it", "not a plain number", row(appropriated="80,000")),
        ("money carrying its scale", "not a plain number", row(appropriated="80k")),
        ("a row with no figure at all", "no stage carries a figure",
         row(appropriated="", baseline_stage="", current_stage="")),
        ("a baseline stage with an empty column", "baseline_stage is 'revised'",
         row(baseline_stage="revised", current_stage="revised", appropriated="",
             proposed="1")),
        ("a current stage before the baseline", "earlier in the cycle",
         row(proposed="1", baseline_stage="appropriated", current_stage="proposed")),
        ("an execution rate that is not a number", "exec_vs_voted", row(exec_vs_voted="n/a")),
        ("a budget-document line with no locator", "doc_locator is empty", row(doc_locator="")),
        ("a required field left empty", "purpose is empty", row(purpose="")),
        ("a finance facet as the subject", "what the money is FOR",
         row(primary_subject="finance.budget")),
        ("a subject outside the taxonomy", "not a taxonomy key",
         row(primary_subject="data.nonsense")),
    ]
    for label, want, r_ in bad:
        d = tmp / "bad" / label.replace(" ", "-")
        write(d, "GHA", "2024", [r_])
        got = failures(d)
        check(label, any(want in f for f in got), True)

    print("\nthe two whole-file rules")
    d = tmp / "dupe"
    write(d, "GHA", "2024", [row(), row(appropriated="90000")])
    check("one deal_id twice", any("already row" in f for f in failures(d)), True)

    d = tmp / "parent-and-child"
    write(d, "GHA", "2024", [
        row(),
        row(deal_id="gha-2024-011-01101", sub_programme_code="", sub_programme="",
            line_name="Management and Administration", appropriated="2812541905"),
    ])
    check("a parent held with its own children",
          any("would sum" in f for f in failures(d)), True)

    if have_catalogue:
        d = tmp / "bad-slug"
        write(d, "GHA", "2024", [row(source_slug="2026-01-01-not-a-document")])
        check("a citation naming nothing held",
              any("no catalogue row" in f for f in failures(d)), True)
    else:
        print("  skip  a citation naming nothing held — no catalogue built")

    print("\nthe admin head and the programme")
    # Every row names both and says how it knows (Bill, 2026-09-22). A sitting's row fails
    # without them; a migrated row is held to a per-country ceiling that only falls.
    for label, want, over in [
        ("a sitting's row with no programme", "programme is empty",
         dict(programme="", programme_basis="", programme_level="")),
        ("a basis outside the list", "admin_head_basis 'guessed'",
         dict(admin_head_basis="guessed")),
        ("a basis with nothing under it", "admin_head_basis is 'printed' and admin_head is empty",
         dict(origin_record="x-rec", admin_head="")),
        ("a level outside the list", "programme_level 'ministry'",
         dict(programme_level="ministry")),
    ]:
        d = tmp / label.replace(" ", "-").replace("'", "")
        write(d, "GHA", "2024", [row(**over)])
        check(label, any(want in f for f in failures(d)), True)

    short = dict(origin_record="x-rec", programme="", programme_basis="", programme_level="")
    d = tmp / "ceiling"
    write(d, "GHA", "2024", [row(**short), row(**short, deal_id="gha-2024-011-01102")])
    check("no ceiling file: migrated rows short of a programme pass", failures(d), [])
    (d / bs.GAPS_FILE).write_text("country,rows\n GHA,1\n".replace(" ", ""), encoding="utf-8-sig")
    check("above its ceiling fails", any("ceiling" in f for f in failures(d)), True)
    bs.ratchet(str(d))
    check("the ratchet never raises a ceiling", bs.read_gaps(str(d)), {"GHA": 1})
    (d / bs.GAPS_FILE).write_text("country,rows\nGHA,2\n", encoding="utf-8-sig")
    check("at its ceiling passes", failures(d), [])

    print("\nthe second bar — a migrated row")
    # A row carrying `origin_record` came out of an OSINT record and is held to
    # REQUIRED_MIGRATED. The point of the pair of cases below is that the bar moves and does
    # not vanish: the fields the records genuinely never carried are allowed through, and the
    # ones that identify a line are not.
    thin = dict(GOOD)
    for c in ("fy_calendar", "admin_head", "admin_head_code", "admin_head_basis", "scope_basis",
              "purpose", "funding_source", "amount_scale", "source_slug",
              "doc_type", "doc_locator", "fy_end"):
        thin[c] = ""
    thin["origin_record"] = "2024-01-01-gha-2024-011-01101-01101004"
    d = tmp / "migrated"
    write(d, "GHA", "2024", [thin])
    check("carries what the record carried and passes", failures(d), [])

    d = tmp / "migrated-free-text"
    write(d, "GHA", "2024", [row(origin_record="x-rec",
                                 funding_source="domestic-revenue (recurrent); the "
                                                "development column reads nil",
                                 budget_version="supplementary-iii")])
    check("a closed list it never closed is not a failure", failures(d), [])

    d = tmp / "migrated-still-identified"
    write(d, "GHA", "2024", [row(origin_record="x-rec", currency="", line_name="",
                                 primary_subject="")])
    got = failures(d)
    for want in ("currency", "line_name is empty", "primary_subject is empty"):
        check(f"but {want.split()[0]} is still required", any(want in f for f in got), True)

    print("\nthe unclear stage")
    unclear = row(origin_record="x-rec", baseline_stage="unclear", current_stage="unclear",
                  appropriated="")
    d = tmp / "unclear-migrated"
    write(d, "GHA", "2024", [unclear])
    check("a migrated row may be unclear with no figure", failures(d), [])

    d = tmp / "unclear-extracted"
    write(d, "GHA", "2024", [row(baseline_stage="unclear", current_stage="unclear",
                                 appropriated="")])
    got = failures(d)
    check("a row a sitting wrote may not be",
          any("has not answered the third question" in f for f in got), True)

    print("\nrecords(), and what the build sees")
    bs.BUDGETS = str(tmp / "clean")
    recs = bs.records("GHA")
    check("one record per row", len(recs), 1)
    check("the merge key is the bare start year", recs[0]["source_fy"], "2024")
    check("the record column names the file and the line", recs[0]["record_ref"],
          "budgets/GHA/2024.csv#gha-2024-011-01101-01101004")
    check("the stage total is renamed the way the driver names it",
          bfp.fm_get(recs[0]["fm"], "appropriated_total"), "80000")
    check("the subject survives into topics", bfp.primary_subject(recs[0]), "data.statistics")
    check("the classification chain reads back",
          bfp.cfield(recs[0], "programme_code"), "01101")
    check("the line name is the one the file gives",
          bfp.line_name(recs[0]),
          "Management and Administration — Research, Statistics and IM")
    check("the fiscal year displays", bfp.fy_display(recs[0]["fm"]), "2024")

    bs.BUDGETS = str(tmp / "bad" / "a-currency-that-is-not-a-code")
    try:
        bs.records("GHA")
        check("a failing file raises rather than loading", False, True)
    except bs.SourceError:
        check("a failing file raises rather than loading", True, True)

    print("\nthe merge — replace, never add")

    def osint(fy_start, label, did):
        return dict(fn=f"raw/2024/{did}.md",
                    fm=f'fy_start: "{fy_start}"\nfiscal_year_label: "{label}"',
                    deal_id=did)

    bs.BUDGETS = str(tmp / "clean")
    dom = [osint("2024-01-01", "2024", "a"),
           osint("", "2024/25", "b"),          # label only, short form
           osint("", "2024-2025", "c"),        # label only, the hyphen form
           osint("2023-01-01", "2023", "d")]
    merged, swaps = bfp.merge_source("GHA", dom)
    check("every way of writing the year is replaced",
          sorted(r["deal_id"] for r in merged),
          ["d", "gha-2024-011-01101-01101004"])
    check("and the swap is reported", swaps, [("2024", 3, 1)])
    check("which prints", bfp.swap_note("GHA", swaps),
          "  [source folder: FY2024 3->1 from budgets/GHA/2024.csv]")

    bs.BUDGETS = str(tmp / "empty")
    merged, swaps = bfp.merge_source("GHA", dom)
    check("no source folder, no change", len(merged), 4)
    check("and nothing to report", swaps, [])

    print("\nthe export row")
    bs.BUDGETS = str(tmp / "clean")
    out = tmp / "GHA-budget.csv"
    bfp.csv_budget(bs.records("GHA"), "GHA", str(out))
    with open(out, encoding="utf-8-sig", newline="") as fh:
        got = list(csv.DictReader(fh))
    check("one row out", len(got), 1)
    check("the figure lands in its stage column", got[0]["appropriated"], "80000")
    check("the citation travels", got[0]["source_slug"],
          "2024-01-01-gha-pbb-2024-mlgrd-companion")
    check("the locator travels", got[0]["doc_locator"].startswith("2024 PBB, table 1.5"), True)
    check("and record points at the source folder", got[0]["record"],
          "budgets/GHA/2024.csv#gha-2024-011-01101-01101004")

    print("\nthe external companion and the share")

    def ext(root: Path, iso3: str, rows: list[dict]):
        with open(root / iso3 / bs.EXTERNAL, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(bs.EXTERNAL_COLUMNS))
            w.writeheader()
            for r in rows:
                w.writerow({c: r.get(c, "") for c in bs.EXTERNAL_COLUMNS})

    line = dict(fy="2024", fiscal_year_label="2024", basis="line", line_name="Donor line",
                code="1", primary_subject="infra.connect", scope_confidence="whole",
                funding_source="external-grant", currency="GHS", amount_scale="units",
                appropriated="20000", doc_locator="p. 6", source_slug="some-slug")
    r = tmp / "ext"
    write(r, "GHA", "2024", [row()])
    check("no external file: no share, and it says why",
          bs.share("GHA", "2024", str(r))["share"], None)
    ext(r, "GHA", [line])
    check("external.csv is not read as a fiscal year",
          [fy for _, fy, _ in bs.files("GHA", str(r))], ["2024"])
    check("a clean external file passes", bs.check_external("GHA", str(r))[0], [])
    got = bs.share("GHA", "2024", str(r))
    check("share is domestic over domestic plus external", got["share"], 80.0)
    check("taken at the stage both sides carry", got["stage"], "appropriated")
    check("the partial domestic line is flagged", got["flags"], ["includes partial lines"])
    ext(r, "GHA", [dict(line, appropriated="", revised="20000")])
    check("no common stage: no share", bs.share("GHA", "2024", str(r))["share"], None)
    ext(r, "GHA", [dict(line, basis="not-printed", appropriated="", line_name="")])
    got = bs.share("GHA", "2024", str(r))
    check("a document with no financing split is all domestic, flagged origin inferred",
          (got["share"], got["flags"][0]), (100.0, "origin inferred"))
    ext(r, "GHA", [dict(line, fy="2023")])
    check("a denominator for a year with no read file fails",
          any("has no budgets/GHA/2023.csv" in f for f in bs.check_external("GHA", str(r))[0]),
          True)
    ext(r, "GHA", [dict(line, appropriated="")])
    check("a line row with no figure fails",
          any("carries a figure" in f for f in bs.check_external("GHA", str(r))[0]), True)

    print("\nexit codes")
    check("a clean tree exits 0", bs.main(["--budgets", str(tmp / "clean")]), 0)
    check("a bad row exits 1", bs.main(["--budgets", str(tmp / "dupe")]), 1)
    check("no folder at all exits 2", bs.main(["--budgets", str(tmp / "nope")]), 2)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
print("all cases pass" if not fails else f"{len(fails)} of the cases FAILED")
sys.exit(1 if fails else 0)
