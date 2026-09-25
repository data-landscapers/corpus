#!/usr/bin/env python3
r"""budget_source.py — Corpus's own budget extractions: the schema, the loader, the checker.

    python scripts/budget_source.py            # check every file under budgets/
    python scripts/budget_source.py GHA        # check one country
    python scripts/budget_source.py --columns  # print the header a new file needs
    python scripts/budget_source.py --share    # the domestic-state share, per read country-year

**`budgets/{ISO3}/{FY}.csv` is a source folder, not an output** *(strategic review 4 R54)*.
Everything else Corpus publishes is derived from OSINT's `raw/`: a compile reads records and
writes `outputs/`, and a hand-edit anywhere in that chain is overwritten by the next build.
These files are the one exception. A sitting reads a budget document OSINT holds, extracts
the digital lines against `documentation/budget-extract.md`, and writes them here; nothing
regenerates them, so they are tracked and they are the record. `BUDGET-EXTRACT.md` is the
runbook that produces one.

**A row is a record, so it carries what a record carries.** The field vocabulary is
`finance-load-domestic-state.md`'s, deliberately — a Corpus row and an OSINT record say the
same thing in the same words, which is what lets `build-finance-page.py` merge the two into
one export without a mapping table between them. The 47 columns are the whole shape: the
line, the year, the classification chain and its codes, the scope judgement and its basis,
the origin gate and its funding source, six stage figures, the currency and its scale, and
the citation — `source_slug` naming the held document and `doc_locator` the page and table
the figure is printed on.

**Two kinds of row, and `origin_record` is which** *(R56a)*. A row a **BUDGET-EXTRACT sitting
read** carries the full schema and `origin_record` is empty. A row **migrated** from an OSINT
domestic-state record carries what that record held, names it in `origin_record`, and is held
to the narrower `REQUIRED_MIGRATED` — see the comment on the two sets, which is where the
reasoning and the counts are. The shortfall is reported per country by `check`, never waived.

**`purpose`, `scope_basis` and `notes` are compiled prose and never the document's words.**
This folder is tracked in a public repository, and `design.md` § *Source bodies* forbids a
verbatim source body reaching one. A line's *name* as the document prints it is a label and
is carried in `line_name`, `programme` and `sub_programme`, which is what the finance export
publishes already; anything longer a sitting writes in its own words, and a migrated row
carries the base's — the record's `## Description` and `## Notes`, which are OSINT's account
of the line and not the volume's text.

**What the checker is for.** These rows replace OSINT's for the country-year they cover
(R56a: replace, never add), so a malformed row does not sit in a corner being wrong — it
silently displaces good records. Every check below is therefore a hard failure, and
`records()` raises rather than returning a row it would not pass. The expensive ones are the
three that arithmetic cannot catch later: **a stage named as the baseline with no figure
under it**, **a parent line held alongside its own children** (they would sum), and **a
`source_slug` naming nothing the catalogue holds**, which is a citation to a document that
may not exist.

Exit: 0 every row passes, 1 a row does not, 2 there is no `budgets/` folder to check.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

# Resolved from this file rather than from the working directory, and `realpath` rather than
# `abspath`: the finance compile runs in `scripts/.workroot/`, where `scripts` is a junction
# back here, so `abspath` would put the repo root at `.workroot` and find no budgets/ at all.
# Resolving absolutely is also why the workroot needs no junction onto this folder — the
# junction list is a boundary surface, and one Corpus does not have to widen it is one worth
# not widening (`rebuild.py` -> `setup_workroot`).
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BUDGETS = os.path.join(ROOT, "budgets")
CATALOGUE = os.path.join(ROOT, "outputs", "catalogue", "catalogue-internal.csv")

COLUMNS = (
    # identity
    "deal_id", "place", "state_level", "spending_tier_name",
    # the fiscal year
    "fiscal_year_label", "fy_start", "fy_end", "fy_calendar",
    "budget_version", "supplementary_basis",
    # the classification chain — names and codes, verbatim, never invented
    "admin_head_code", "admin_head", "spending_entity_code", "spending_entity",
    "programme_code", "programme", "sub_programme_code", "sub_programme", "econ_class",
    # where the head and the programme came from, and what grain "programme" is
    "admin_head_basis", "programme_basis", "programme_level",
    # what the line is
    "line_name", "purpose", "primary_subject",
    # is it digital
    "scope_confidence", "scope_basis",
    # whose money it is
    "finance_origin", "funding_source", "is_transfer", "transfer_to",
    # the money
    "currency", "amount_scale",
    "proposed", "appropriated", "revised", "released", "actual", "audited",
    "baseline_stage", "current_stage", "exec_vs_voted", "exec_vs_revised",
    # where it is printed
    "source_tier", "doc_type", "doc_locator", "source_slug",
    # who read it, and what they had to say about it
    "extracted", "origin_record", "notes",
)

STAGES = ("proposed", "appropriated", "revised", "released", "actual", "audited")

# **`unclear` is a stage name and not a money column** *(R56a)*. The driver records the stage
# only where the source states it and writes `unclear` otherwise, and 12 of the 494 records
# migrated in say that: a presidential despacho authorising expenditure and opening a
# procurement names no point in the appropriation-to-outturn ladder. Such a row has a figure
# in its stage history and nowhere to put it, which is why it publishes with every money
# column empty. It is admitted **only on a migrated row** — a sitting that cannot say which
# stage a figure is has not finished the three questions, and `budget-extract.md` is explicit
# that such a figure is not a record.
STAGE_NAMES = STAGES + ("unclear",)

# Closed lists, all of them the driver's. A value outside one is a row this folder does not
# carry, not a row with an unusual value in it.
STATE_LEVEL = {"national", "sub-national", "soe", "levy-fund", "regulator"}
SCOPE = {"whole", "partial", "unclear"}
FUNDING = {"domestic-revenue", "domestic-borrowing", "own-source",
           "external-loan", "external-grant", "counterpart", "unstated"}
SUPP_BASIS = {"", "increment", "restated-total", "unclear"}
SOURCE_TIER = {"budget-document", "official-statement", "project-document", "reporting"}

# **Every row names its admin head and its programme** *(Bill, 2026-09-22)*, and says how it
# knows. `printed` is the document's own name for it, carried as captured; `derived` is a
# stand-in worked out from what the row already holds — the head a spending entity's own
# printed code places it under, a project line standing in for a programme the budget does
# not have — and never a code: codes are the cross-year join key and are never invented.
# `programme_level` is the grain the `programme` column actually holds, because a line-item
# budget has no programmes at all and the honest answer there is the next level it prints.
# `vote` and `body` are a whole appropriation held as one line: the programme is the head
# or the spending entity itself, which the spec allows only for a single-mandate body.
BASIS = {"printed", "derived"}
PROGRAMME_LEVEL = {"programme", "project", "activity", "action", "chapter", "line",
                   "account", "body", "vote"}
STRUCTURE = ("admin_head", "programme")

# **The migrated rows' shortfall on those two fields may only fall.** Failing all of them now
# would stop the Finance build on 414 rows, so the ceiling is per country, in
# `budgets/structure-gaps.csv`, and `--ratchet` lowers it to what is left. A country above
# its ceiling fails; a country below it is told to ratchet.
GAPS_FILE = "structure-gaps.csv"

# **Two bars, because there are two kinds of row** *(R56a, 2026-09-20)*. A row a sitting read
# against `documentation/budget-extract.md` carries everything, and REQUIRED is the whole of
# it. A row **migrated** from an OSINT domestic-state record — `origin_record` names which —
# carries what that record held, and across the 494 that existed the shortfall is large and
# structural: `admin_head_code` on 125, `admin_head` on 99, `fy_calendar` on 86, `scope_basis`
# on 240, `doc_type` on 197, and a `source_slug` resolvable for 124. Holding those to the full
# bar would leave two options, fabricating the values or refusing the migration, and the
# review asked for neither. So the bar is narrower and **the gap is counted rather than
# waived**: `check` reports, per country, how many migrated rows fall short of the full set,
# which is the work order R58 reads.
REQUIRED = ("deal_id", "place", "state_level", "fiscal_year_label", "fy_start", "fy_end",
            "fy_calendar", "budget_version", "admin_head_code", "admin_head",
            "spending_entity", "programme", "admin_head_basis", "programme_basis",
            "programme_level", "line_name", "purpose", "primary_subject",
            "scope_confidence", "scope_basis", "finance_origin", "funding_source",
            "is_transfer", "currency", "amount_scale", "baseline_stage", "current_stage",
            "source_tier", "source_slug", "extracted")

REQUIRED_MIGRATED = ("deal_id", "place", "state_level", "fiscal_year_label", "fy_start",
                     "line_name", "primary_subject", "budget_version",
                     "scope_confidence", "finance_origin", "is_transfer", "currency",
                     "baseline_stage", "current_stage", "source_tier", "extracted",
                     "origin_record")

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONEY = re.compile(r"^\d+(\.\d+)?$")            # units, normalised — no separators, no symbol
PCT = re.compile(r"^\d+(\.\d+)?$")
VERSION = re.compile(r"^(original|revised|supplementary-\d+)$")


class SourceError(Exception):
    """Raised by `records()` when a file would not pass the checker.

    The build does not catch it. A row that replaces OSINT's records for a whole
    country-year and is wrong is worse than no row, so the compile stops rather than
    publishing it."""


# ---------------------------------------------------------------- the external companion
# **`budgets/{ISO3}/external.csv` is the denominator of the financial sustainability measure**
# (`documentation/indicator-financial-sustainability.md` §5). The origin gate sends an externally
# financed digital line to the non-state side, so no `{FY}.csv` row holds it, and its size used to
# live only in the sitting's log note. Here it is a row with the same citation discipline as a
# domestic one: one per external line per fiscal year, at the grain the document prints it.
# `basis` says what kind of row it is: `line` is a printed external line; `not-printed` is one row
# for a year whose document prints no financing split at all, so the share is *origin inferred*
# rather than a hundred per cent.
EXTERNAL = "external.csv"
EXTERNAL_COLUMNS = ("fy", "fiscal_year_label", "basis", "line_name", "code", "primary_subject",
                    "scope_confidence", "funding_source", "currency", "amount_scale",
                    "proposed", "appropriated", "revised", "doc_locator", "source_slug", "extracted", "notes")
EXTERNAL_BASIS = {"line", "not-printed"}
EXTERNAL_FUNDING = {"external-grant", "external-loan", "external"}
# The stages a share may be taken at, in preference order. Both sides must carry the stage on
# every row counted, or the share would divide an appropriation by a revision. `proposed` is last:
# a year held only as a bill still has a share, and the stage it was taken at says so.
SHARE_STAGES = ("appropriated", "revised", "proposed")
# The digital lines as the extract defines them. `unclear` is neither side's.
SHARE_SCOPE = ("whole", "partial")


# ---------------------------------------------------------------- reading
def files(iso3: str = "", budgets: str = "") -> list[tuple[str, str, str]]:
    """`(ISO3, FY, path)` for every source file, sorted. `FY` is the bare start year."""
    base = budgets or BUDGETS
    out = []
    if not os.path.isdir(base):
        return out
    for country in sorted(os.listdir(base)):
        if iso3 and country != iso3:
            continue
        d = os.path.join(base, country)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            # Every other CSV is taken, so that `check` can refuse a misnamed year.
            if fn.endswith(".csv") and fn != EXTERNAL:
                out.append((country, fn[:-4], os.path.join(d, fn)))
    return out


def external(iso3: str, budgets: str = "") -> list[dict]:
    """The rows of `budgets/{ISO3}/external.csv`, or none where the file does not exist."""
    path = os.path.join(budgets or BUDGETS, iso3, EXTERNAL)
    return read(path)[1] if os.path.exists(path) else []


def check_external(iso3: str = "", budgets: str = "") -> tuple[list[str], int]:
    """Failures in every `external.csv`, and the rows read. A `line` row carries a figure and a
    citation; a `not-printed` row carries a citation and no figure; either names a fiscal year
    the country has a read file for, since a denominator with no numerator is nobody's."""
    base = budgets or BUDGETS
    fails, n = [], 0
    for country in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        if iso3 and country != iso3:
            continue
        path = os.path.join(base, country, EXTERNAL)
        if not os.path.exists(path):
            continue
        header, rows = read(path)
        where = f"{country}/{EXTERNAL}"
        if tuple(header) != EXTERNAL_COLUMNS:
            fails.append(f"{where}: header is not {','.join(EXTERNAL_COLUMNS)}")
            continue
        years = {fy for _, fy, _ in files(country, budgets)}
        for i, r in enumerate(rows, start=2):
            n += 1
            at = f"{where} line {i}"
            if r["fy"] not in years:
                fails.append(f"{at}: FY{r['fy']} has no budgets/{country}/{r['fy']}.csv")
            if r["basis"] not in EXTERNAL_BASIS:
                fails.append(f"{at}: basis {r['basis']!r}")
            if not r["source_slug"] or not r["doc_locator"]:
                fails.append(f"{at}: every row cites its document")
            if not r["currency"]:
                fails.append(f"{at}: no currency")
            amounts = [r[s] for s in SHARE_STAGES if r[s]]
            for a in amounts:
                if not MONEY.match(a):
                    fails.append(f"{at}: amount {a!r} is not normalised units")
            if r["basis"] == "line":
                if not amounts:
                    fails.append(f"{at}: a line row carries a figure at some stage")
                if r["funding_source"] not in EXTERNAL_FUNDING:
                    fails.append(f"{at}: funding_source {r['funding_source']!r}")
                if r["scope_confidence"] not in SCOPE:
                    fails.append(f"{at}: scope_confidence {r['scope_confidence']!r}")
            elif r["basis"] == "not-printed" and amounts:
                fails.append(f"{at}: a not-printed row carries no figure")
    return fails, n


def share(iso3: str, fy: str, budgets: str = "") -> dict:
    """The domestic-state share of the digital lines for one read country-year.

    `{share, stage, domestic, external, currency, flags}`, or `{share: None, why}` where it
    cannot be taken. The figure of record for the financial sustainability indicator: domestic
    ÷ (domestic + external) over whole and partial lines, at the first of `SHARE_STAGES` that
    every counted row on both sides carries."""
    path = os.path.join(budgets or BUDGETS, iso3, f"{fy}.csv")
    if not os.path.exists(path):
        return {"share": None, "why": f"no budgets/{iso3}/{fy}.csv"}
    dom = [r for r in read(path)[1] if r.get("scope_confidence") in SHARE_SCOPE
           and r.get("finance_origin") == "domestic-state"]
    if any(r.get("origin_record") for r in dom):
        return {"share": None, "why": "the year holds migrated rows and has not been read"}
    ext_all = [r for r in external(iso3, budgets) if r["fy"] == fy]
    if not ext_all:
        return {"share": None, "why": f"no external.csv row for FY{fy} — the sitting did not "
                                      f"record the denominator"}
    ext = [r for r in ext_all if r["basis"] == "line" and r["scope_confidence"] in SHARE_SCOPE]
    flags = []
    if any(r["basis"] == "not-printed" for r in ext_all):
        flags.append("origin inferred")
    if any(r["scope_confidence"] == "partial" for r in dom + ext):
        flags.append("includes partial lines")
    for stage in SHARE_STAGES:
        if all(r.get(stage) for r in dom) and all(r[stage] for r in ext) and dom:
            d = sum(float(r[stage]) for r in dom)
            e = sum(float(r[stage]) for r in ext)
            return {"share": round(100 * d / (d + e), 1) if d + e else None, "stage": stage,
                    "domestic": d, "external": e, "currency": dom[0].get("currency", ""),
                    "flags": flags}
    return {"share": None, "why": "no stage is carried by every counted row on both sides"}


def read(path: str) -> tuple[list[str], list[dict]]:
    """The header as written and the rows. `utf-8-sig`, as every CSV in this repo is."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rdr = csv.DictReader(fh)
        return list(rdr.fieldnames or []), list(rdr)


def _slugs() -> set[str] | None:
    """Every catalogue slug, or `None` where the catalogue has not been built yet.

    `None` and `set()` are different answers: a missing catalogue means the citation check
    cannot run, which is reported, and an empty one would mean every citation is wrong."""
    if not os.path.exists(CATALOGUE):
        return None
    with open(CATALOGUE, encoding="utf-8-sig", newline="") as fh:
        return {r["slug"] for r in csv.DictReader(fh) if r.get("slug")}


def _subjects() -> set[str] | None:
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import taxonomy_lib
        return set(taxonomy_lib.keys())
    except Exception:
        return None


# ---------------------------------------------------------------- the checker
def check(iso3: str = "", budgets: str = "") -> tuple[list[str], int, int]:
    """`(failures, files checked, rows checked)`. Every failure names file, row and field."""
    fails: list[str] = []
    slugs = _slugs()
    subjects = _subjects()
    nfiles = nrows = 0
    thin: dict[str, int] = {}       # country -> migrated rows short of the full bar
    gap: dict[str, int] = {}        # country -> rows with no admin head or no programme
    nmig = 0

    for country, fy, path in files(iso3, budgets):
        nfiles += 1
        rel = os.path.relpath(path, budgets or BUDGETS).replace("\\", "/")
        header, rows = read(path)
        if tuple(header) != COLUMNS:
            missing = [c for c in COLUMNS if c not in header]
            extra = [c for c in header if c not in COLUMNS]
            fails.append(f"{rel}: header is not the schema"
                         + (f" — missing {missing}" if missing else "")
                         + (f" — unknown {extra}" if extra else "")
                         + ("" if missing or extra else " — the columns are out of order"))
            continue                       # every other check reads by name; stop here
        if not re.fullmatch(r"\d{4}", fy):
            fails.append(f"{rel}: the file name is not a bare fiscal-year start year. "
                         f"A bare year means the fiscal year beginning in it.")
        if not rows:
            fails.append(f"{rel}: no rows. A country-year with nothing in it is a stated "
                         f"absence in the runbook's log, not an empty file here.")

        seen: dict[str, int] = {}
        # Keyed by head as well as code: a programme code is unique only within its head in
        # some states (every Zambian head's support programme is 3499).
        parents: set[str] = set()          # head/programme_code held with no sub-programme
        children: set[str] = set()         # head/programme_code held at sub-programme grain
        for i, r in enumerate(rows, start=2):
            nrows += 1
            def bad(msg: str) -> None:
                fails.append(f"{rel}:{i} {msg}")
            g = lambda k: (r.get(k) or "").strip()                       # noqa: E731

            migrated = bool(g("origin_record"))
            def soft(msg: str) -> None:
                """A migrated row's shortfall against a closed list: counted, never failed.

                The record carried what it carried. Failing it would mean either editing
                OSINT's data in the migration or refusing to migrate, and the value is real
                information — `funding_source` running to a whole sentence about a split is
                worth more than a blank cell with the right shape."""
                if not migrated:
                    bad(msg)              # a migrated row is tallied below, once per row

            for col in (REQUIRED_MIGRATED if migrated else REQUIRED):
                if not g(col):
                    bad(f"{col} is empty, and it is required"
                        + (" even on a migrated row." if migrated else "."))
            if migrated:
                nmig += 1
                if (any(not g(c) for c in REQUIRED)
                        or g("funding_source") not in FUNDING
                        or not VERSION.match(g("budget_version") or "")
                        or g("baseline_stage") == "unclear"):
                    thin[country] = thin.get(country, 0) + 1

            if g("place") != country:
                bad(f"place is {g('place')!r} and the folder is {country}.")
            if g("fy_start")[:4] != fy:
                bad(f"fy_start {g('fy_start')!r} does not begin in {fy}, which the file "
                    f"name says every row in it does.")
            did = g("deal_id")
            if did in seen:
                bad(f"deal_id {did!r} is already row {seen[did]}. One record per line-year.")
            seen[did] = i
            if did and not did.startswith(country.lower() + "-"):
                bad(f"deal_id {did!r} does not open with {country.lower()}-.")

            for col in ("fy_start", "fy_end", "extracted"):
                if g(col) and not ISO_DATE.match(g(col)):
                    bad(f"{col} {g(col)!r} is not an ISO date.")
            if g("fy_start") and g("fy_end") and g("fy_end") <= g("fy_start"):
                bad("fy_end is not after fy_start.")

            if g("state_level") and g("state_level") not in STATE_LEVEL:
                bad(f"state_level {g('state_level')!r} is outside {sorted(STATE_LEVEL)}.")
            if g("scope_confidence") and g("scope_confidence") not in SCOPE:
                bad(f"scope_confidence {g('scope_confidence')!r} is outside {sorted(SCOPE)}.")
            if g("funding_source") and g("funding_source") not in FUNDING:
                soft(f"funding_source {g('funding_source')!r} is outside {sorted(FUNDING)}.")
            if g("supplementary_basis") not in SUPP_BASIS:
                bad(f"supplementary_basis {g('supplementary_basis')!r} is outside "
                    f"{sorted(SUPP_BASIS - {''})} or empty.")
            if g("budget_version") and not VERSION.match(g("budget_version")):
                soft(f"budget_version {g('budget_version')!r} is not original, revised or "
                     f"supplementary-N.")
            if g("source_tier") and g("source_tier") not in SOURCE_TIER:
                bad(f"source_tier {g('source_tier')!r} is outside {sorted(SOURCE_TIER)}.")
            if g("is_transfer") not in {"true", "false"}:
                bad(f"is_transfer {g('is_transfer')!r} is not true or false.")
            if g("is_transfer") == "true" and not g("transfer_to"):
                soft("is_transfer is true and transfer_to names nobody. A transfer is "
                     "captured at the spending end, so the receiving body has to be named.")

            # The origin gate has already run by the time a row is written. A line the gate
            # sends to `non-state` is matched to a held deal on the non-state side and builds
            # no record here at all; a line naming no funder beyond "external" builds none
            # anywhere. Either way this folder holds domestic-state money only.
            if g("finance_origin") and g("finance_origin") != "domestic-state":
                bad(f"finance_origin is {g('finance_origin')!r}. This folder is the "
                    f"domestic-state side; an externally financed line is a non-state deal.")

            if not re.fullmatch(r"[A-Z]{3}", g("currency")):
                bad(f"currency {g('currency')!r} is not a three-letter code.")

            held = [s for s in STAGES if g(s)]
            for s in STAGES:
                if g(s) and not MONEY.match(g(s)):
                    bad(f"{s} {g(s)!r} is not a plain number. Amounts are stored normalised "
                        f"to units — no separators, no scale suffix, no currency symbol; "
                        f"amount_scale records what the document printed.")
            unclear = g("baseline_stage") == "unclear"
            if not held and not (migrated and unclear):
                bad("no stage carries a figure. A line with no money in it is an absence, "
                    "and an absence is a finding in the log, not a row.")
            for col in ("baseline_stage", "current_stage"):
                v = g(col)
                if v == "unclear":
                    if not migrated:
                        bad(f"{col} is 'unclear'. A figure whose stage nobody can name has "
                            f"not answered the third question and is not a record.")
                elif v and v not in STAGES:
                    bad(f"{col} {v!r} is outside {list(STAGE_NAMES)}.")
                elif v and not g(v):
                    bad(f"{col} is {v!r} and the {v} column is empty.")
            if g("baseline_stage") in STAGES and g("current_stage") in STAGES:
                if STAGES.index(g("current_stage")) < STAGES.index(g("baseline_stage")):
                    bad("current_stage is earlier in the cycle than baseline_stage.")
            for col in ("exec_vs_voted", "exec_vs_revised"):
                if g(col) and not PCT.match(g(col)):
                    bad(f"{col} {g(col)!r} is not a number.")

            if g("source_tier") == "budget-document":
                for col in ("doc_type", "doc_locator"):
                    if not g(col):
                        soft(f"{col} is empty on a budget-document line. The locator is how "
                             f"a reader reaches the page the figure is printed on.")
            if slugs is not None and g("source_slug") and g("source_slug") not in slugs:
                bad(f"source_slug {g('source_slug')!r} is in no catalogue row, so it names "
                    f"no held document.")
            if subjects is not None and g("primary_subject"):
                if g("primary_subject") not in subjects:
                    bad(f"primary_subject {g('primary_subject')!r} is not a taxonomy key.")
                elif g("primary_subject").startswith("finance."):
                    bad("primary_subject is a finance facet. It is what the money is FOR.")

            for f in STRUCTURE:
                b = g(f + "_basis")
                if g(f) and b not in BASIS:
                    bad(f"{f}_basis {b!r} is outside {sorted(BASIS)}; a {f} says where it "
                        f"came from.")
                if not g(f) and b:
                    bad(f"{f}_basis is {b!r} and {f} is empty.")
            if g("programme") and g("programme_level") not in PROGRAMME_LEVEL:
                bad(f"programme_level {g('programme_level')!r} is outside "
                    f"{sorted(PROGRAMME_LEVEL)}.")
            if not g("programme") and g("programme_level"):
                bad("programme_level is set and programme is empty.")
            if any(not g(f) for f in STRUCTURE):
                gap[country] = gap.get(country, 0) + 1

            if g("programme_code"):
                key = f'{g("admin_head_code") or g("admin_head")}/{g("programme_code")}'
                (children if g("sub_programme_code") else parents).add(key)

        both = parents & children
        if both:
            fails.append(f"{rel}: programme {sorted(both)} is held both as a line of its own "
                         f"and at sub-programme grain. They would sum — a finer document "
                         f"supersedes a coarser one and the parent is retired, not kept.")

    ceiling = read_gaps(budgets)
    if ceiling is None:
        if gap:
            print(f"budget_source: note — no {GAPS_FILE}, so the admin-head and programme "
                  f"shortfall ({sum(gap.values())} row(s)) is not held to a ceiling.")
    else:
        for c in sorted(set(gap) | set(ceiling)):
            if iso3 and c != iso3:
                continue
            have, cap = gap.get(c, 0), ceiling.get(c, 0)
            if have > cap:
                fails.append(f"{c}: {have} row(s) lack an admin head or a programme and the "
                             f"ceiling in {GAPS_FILE} is {cap}. It only falls.")
            elif have < cap:
                print(f"budget_source: note — {c} is down to {have} row(s) lacking an admin "
                      f"head or a programme against a ceiling of {cap}; run --ratchet.")

    if slugs is None:
        print("budget_source: note — no catalogue at outputs/catalogue/catalogue-internal.csv, "
              "so source_slug was not resolved. Run the catalogue compile and check again.")
    # **The migrated rows are counted, and so is what they are short of.** They pass, because
    # they carry what the record they came from carried; what they do not carry is the reason
    # R58 exists, and a migration whose shortfall is invisible is one nobody ever finishes.
    if nmig:
        print(f"budget_source: {nmig} of {nrows} row(s) migrated from OSINT records; "
              f"{sum(thin.values())} of those are short of the full schema and are waiting "
              f"for a BUDGET-EXTRACT sitting (R58).")
        for c in sorted(thin):
            print(f"  {c}: {thin[c]}")
    return fails, nfiles, nrows


def read_gaps(budgets: str = "") -> dict[str, int] | None:
    path = os.path.join(budgets or BUDGETS, GAPS_FILE)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return {r["country"]: int(r["rows"]) for r in csv.DictReader(fh)}


def ratchet(budgets: str = "") -> dict[str, int]:
    """Lower each country's ceiling to what it now lacks. Never raises one."""
    gap: dict[str, int] = {}
    for country, _, path in files("", budgets):
        for r in read(path)[1]:
            if any(not (r.get(f) or "").strip() for f in STRUCTURE):
                gap[country] = gap.get(country, 0) + 1
    old = read_gaps(budgets)
    if old is not None:
        gap = {c: min(n, old.get(c, 0)) for c, n in gap.items() if old.get(c, 0)}
    with open(os.path.join(budgets or BUDGETS, GAPS_FILE), "w", encoding="utf-8-sig",
              newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["country", "rows"])
        for c in sorted(gap):
            if gap[c]:
                w.writerow([c, gap[c]])
    return gap


# ---------------------------------------------------------------- the build's view
def _fm(row: dict, cols: dict) -> str:
    """A frontmatter block in the driver's own field names.

    The finance compile reads an OSINT record through `fm_get`, and every function that
    builds a budget row — the classification chain, the stage columns, the subject
    aggregate, the exclusion reasons — reads it that way. Handing those functions a
    synthesised block instead of a second code path is what keeps one export format with
    one implementation behind it: a Corpus row and an OSINT record become the same kind of
    thing at the point of reading, not at the point of writing."""
    out = []
    for key, col in cols.items():
        # `json.dumps`, not an f-string with quotes round it. `fm_get` JSON-decodes a
        # double-quoted scalar carrying a backslash and strips the quotes otherwise, so this
        # round-trips any value at all — including the one `doc_locator` in the corpus that
        # quotes the law's own words inside itself, which naive quoting turned from double
        # quotes into single ones on the published row.
        out.append(f"{key}: " + json.dumps((row.get(col) or "").strip(), ensure_ascii=False))
    return "\n".join(out)


# driver field name -> source column. The stage totals are the only rename: the record
# calls them `{stage}_total` and the export's columns are bare, so the row is written the
# way it publishes and translated the way it is read.
FM_COLS = {
    "fiscal_year_label": "fiscal_year_label", "fy_start": "fy_start",
    "admin_head": "admin_head", "admin_head_code": "admin_head_code",
    "spending_entity": "spending_entity", "spending_entity_code": "spending_entity_code",
    "programme": "programme", "programme_code": "programme_code",
    "sub_programme": "sub_programme", "sub_programme_code": "sub_programme_code",
    "econ_class": "econ_class",
    "proposed_total": "proposed", "appropriated_total": "appropriated",
    "revised_total": "revised", "released_total": "released",
    "actual_total": "actual", "audited_total": "audited",
    "execution_pct_vs_appropriated": "exec_vs_voted",
    "execution_pct_vs_revised": "exec_vs_revised",
    "baseline_stage": "baseline_stage", "current_stage": "current_stage",
    "scope_confidence": "scope_confidence", "is_transfer": "is_transfer",
    "supplementary_basis": "supplementary_basis",
    "currency": "currency", "source_tier": "source_tier",
    "doc_type": "doc_type", "doc_locator": "doc_locator",
    "source_slug": "source_slug", "primary_subject": "primary_subject",
    "origin_record": "origin_record",
    "admin_head_basis": "admin_head_basis", "programme_basis": "programme_basis",
    "programme_level": "programme_level",
}


def records(iso3: str, budgets: str = "") -> list[dict]:
    """Every source row for one country, in the shape `build-finance-page.py` scans into.

    Raises `SourceError` if any file for that country fails the checker. Two extra keys the
    OSINT records do not carry: `source_fy`, the bare start year the merge keys on, and
    `record_ref`, what the export's `record` column says instead of a raw/ filename."""
    fails, _, _ = check(iso3, budgets)
    if fails:
        raise SourceError(f"budgets/{iso3}/ does not pass:\n  " + "\n  ".join(fails))
    out = []
    for country, fy, path in files(iso3, budgets):
        _, rows = read(path)
        for r in rows:
            subj = (r.get("primary_subject") or "").strip()
            out.append(dict(
                fn="", fm=_fm(r, FM_COLS), body="",
                table={"Spending entity": (r.get("spending_entity") or "").strip()},
                origin="domestic-state", published=(r.get("fy_start") or "").strip(),
                topics=[subj, "finance.budget"] if subj else ["finance.budget"],
                url="", title=(r.get("line_name") or "").strip(),
                # The display name as the file gives it, never recomputed. `line_name()`
                # derives one from the classification chain and falls back through the
                # title and the spending entity, and on a row whose programme is blank
                # those fallbacks find different text here than they found in the record
                # — 145 of the 488 migrated rows changed their published line name when
                # this was left to be recomputed.
                line_name=(r.get("line_name") or "").strip(),
                deal_id=(r.get("deal_id") or "").strip(),
                currency=(r.get("currency") or "").strip(),
                source_fy=fy,
                record_ref=f"budgets/{country}/{fy}.csv#{(r.get('deal_id') or '').strip()}",
            ))
    return out


# ---------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check Corpus's own budget extractions.")
    ap.add_argument("iso3", nargs="?", default="", help="one country, else all of them")
    ap.add_argument("--budgets", default="", help="another budgets/ root, for tests")
    ap.add_argument("--columns", action="store_true", help="print the header and stop")
    ap.add_argument("--share", action="store_true",
                    help="print the domestic-state share for every read country-year, and stop")
    ap.add_argument("--ratchet", action="store_true",
                    help="lower the admin-head/programme ceilings to what is left, and stop")
    a = ap.parse_args(argv)

    if a.columns:
        print(",".join(COLUMNS))
        return 0
    base = a.budgets or BUDGETS
    if not os.path.isdir(base):
        print(f"budget_source: no source folder at {base}. "
              f"BUDGET-EXTRACT.md is how the first one is written.")
        return 2
    if a.share:
        for country in sorted({c for c, _, _ in files(a.iso3, a.budgets)}):
            if not external(country, a.budgets):
                continue
            for _, fy, _ in files(country, a.budgets):
                r = share(country, fy, a.budgets)
                if r["share"] is None:
                    print(f"{country} FY{fy}: no share — {r['why']}")
                else:
                    fl = f" ({'; '.join(r['flags'])})" if r["flags"] else ""
                    print(f"{country} FY{fy}: {r['share']}% domestic at {r['stage']} — "
                          f"{r['domestic']:,.0f} of {r['domestic'] + r['external']:,.0f} "
                          f"{r['currency']}{fl}")
        return 0
    if a.ratchet:
        left = ratchet(a.budgets)
        print(f"budget_source: ceilings now {sum(left.values())} row(s) over {len(left)} "
              f"countr{'y' if len(left) == 1 else 'ies'}.")
        return 0
    fails, nfiles, nrows = check(a.iso3, a.budgets)
    xfails, xrows = check_external(a.iso3, a.budgets)
    fails += xfails
    nrows += xrows
    for f in fails:
        print(f"budget_source: FAIL — {f}")
    if fails:
        print(f"budget_source: {len(fails)} failure(s) over {nrows} row(s) in {nfiles} file(s).")
        return 1
    print(f"budget_source: ok — {nrows} row(s) in {nfiles} file(s) pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
