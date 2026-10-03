#!/usr/bin/env python3
"""
build-finance-page.py {ISO3} | --all  —  the per-country finance exports.

Called by FINANCE-COMPILE.md (step 4) for each place in scope. Reads that place's
finance records from raw/ and writes two CSV exports:

  1. {ISO3}-nonstate.csv  (one row per deal)
  2. {ISO3}-budget.csv    (one row per year x vote/head x programme-line; stages as columns
                           - OSINT's records MERGED with Corpus's own extractions, below)

`{ISO3}-summary.csv`, the aggregate by origin x subject x FY, was a third until 2026-10-03
*(Bill)*: nothing read it, so the build stopped writing it.

Every row links to its raw/ record. DERIVED — do not hand-edit; rebuilt each compile.

**The budget export has two sources from 2026-09-20** *(strategic review 4 R54)*. OSINT's
domestic-state records in `raw/`, as always, and Corpus's own extractions in
`budgets/budgets-{ISO3}.csv` — tracked source files, one per country, written by a `BUDGET-EXTRACT.md` sitting reading a budget
document, and the one thing in this pipeline a build does not regenerate. The rule is
`merge_source()`: **a country-year present in the source file replaces OSINT's rows for that
year, and never adds to them.** Add-and-dedupe was the alternative and it is the wrong one —
the two sides read the same document at different grains, so a union double-counts a programme
against its own sub-programmes and no key detects it. Replacement means the folder's coverage
is legible: if `budgets/budgets-GHA.csv` holds FY2024, every GHA FY2024 row published came
out of it.

Outputs land in outputs/ so that everything the website serves sits together;
the build's two INPUTS (fx-imf-annual.csv, financier-names.csv) stay in lookups/
(Bill, 2026-08-03). The same change retired the per-country {ISO3}.md report page:
it was a human-readable view of these same tables, nothing read it, and the
website renders from the CSVs.
"""
import os, re, sys, csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy_lib                                                             # noqa: E402
import budget_source                                                            # noqa: E402
from vault_lib import dewiki                                                    # noqa: E402
from finance_lib import (split_front, fm_get, section, deal_table, raw_sources,  # noqa: E402
                         fin_name)                                              # noqa: E402

RAW = "raw"
# Corpus's own judgement of each non-state deal's scope. Absolute, because the build runs
# from the workroot, where `lookups/` is OSINT's; `realpath`, because it runs through a junction.
SCOPE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                          "lookups", "deal-scope.csv")
BUDGET_OUT = "outputs/budgets"                 # {ISO3}-budget.csv
NONSTATE_OUT = "outputs/non-state-finance"     # {ISO3}-nonstate.csv, all-nonstate.csv

# ---------------------------------------------------------------- small helpers
def taxonomy_labels():
    r"""`{slug: label}` from Corpus's `lookups/taxonomy.csv` — the display vocabulary.

    Was a regex over OSINT's `lookups/taxonomy.md` until 2026-08-19. The two now sit
    under the same directory name in different repositories, so read the extension:
    `.csv` is Corpus's labels, `.md` is OSINT's vocabulary and its prose. That file is prose as
    well as vocabulary, and the pattern `- \`slug\` — label` matched greedily to the
    end of the line: `dpi.registry`'s entry carries a 558-character ruling about
    where registry material files, and all 558 characters were arriving in the
    `sector` column (now `primary_topic`) of every published finance CSV and in the topic row of three
    countries' pivot tables. The name stays and only the source moves."""
    return taxonomy_lib.labels()


def fy_normalise(lab):
    """`2024/2025` -> `2024/25`, so one fiscal year is one column.

    Domestic-state lines take `fiscal_year_label` from the record as written, and some are
    written long. A table carrying both forms shows a reader two columns for one year —
    Botswana's had `2025/26` and `2025/2026` side by side (unit review, 2026-09-18). Only a
    genuine consecutive pair is shortened; anything else is left alone.

    **The hyphen is the same label** *(2026-09-20, R53)*. Burundi writes one fiscal year as
    `2026/27` on one record and `2026-2027` on another, both verbatim from the documents, and
    the coverage table the Finance page now publishes counted them as two — it reported four
    fiscal years for a country that has three. `fiscal_year_label` stays verbatim on the
    record, as the driver requires; this is the display form, and a display form that shows
    one year twice is the thing this function exists to prevent.
    """
    m = re.fullmatch(r"(\d{4})[/-](\d{4}|\d{2})", (lab or "").strip())
    if m:
        a, b = m.group(1), m.group(2)
        full = int(b) if len(b) == 4 else int(a[:2] + b)
        if full == int(a) + 1:
            return "%s/%s" % (a, str(full)[-2:])
    return lab

def primary_subject(rec):
    """The subject a record is filed under: the explicit `primary_subject:`
    override where set, else the first non-finance slug in `topics:`
    (reference.md -> Facets — the order is load-bearing and never sorted)."""
    over = fm_get(rec["fm"], "primary_subject")
    if over and over in rec["topics"]:
        return over
    for t in rec["topics"]:
        if t and not t.startswith("finance."):
            return t
    return ""

def usd_millions(s):
    """'US$355,000,000' -> 355 ; 'US$1.30bn' -> 1300 ; 'US$45m' -> 45 ;
    'US$6 200 000 000' -> 6200.

    Space-separated thousands are read as thousands, not as a truncation. Lint #3's
    dated-conversion rewrite reformats money in place, and on 2026-07-28 one such
    rewrite turned `6200000000` into `6 200 000 000 *(dated conversion …)*` — which
    this function read as **6**, silently reporting a US$6.2bn deal as US$6m
    (LSO/Convalt). A percentage is not an amount either: a `Disbursed (USD)` cell
    reading '100% disbursement rate …' must not parse as US$100m.

    A **bare number is dollars, always.** The old `v > 100000` heuristic read a bare
    number below that as already-in-millions, which turned MWI/National Bank of
    Malawi's **US$43,516** sponsorship (MWK 75.5m) into **US$43.5bn** — 44 times
    Malawi's entire tracked finance, and it was sitting in the continental aggregate.
    A sweep of all 1,235 deals on 2026-07-28 found that record was the *only* one the
    heuristic touched, so nothing legitimately encodes millions as a bare number.
    Record millions explicitly (`US$45m`) — never as a bare `45`."""
    if not s:
        return None
    s = s.replace(",", "")
    s = re.sub(r'(?<=\d)[    ](?=\d{3}(?!\d))', '', s)   # 6 200 000 000 -> 6200000000
    m = re.search(r'([\d.]+)\s*(bn|billion|m|million)?', s, re.I)
    if not m:
        return None
    if s[m.end():m.end() + 1] == "%":
        return None
    v = float(m.group(1)); unit = (m.group(2) or "").lower()
    if unit.startswith("b"):
        return v * 1000
    if unit.startswith("m") or unit.startswith("mi"):
        return v
    return v / 1e6                           # a bare number is DOLLARS, always

def clean(s):                                # de-wikilink and de-pipe for a table cell
    # `dewiki` lives in `vault_lib` so the finance pass and the catalogue export share one
    # definition (2026-08-25). It is separate from `clean` because `clean` also turns `|`
    # into `/`, right for a one-line table cell and wrong for a paragraph of prose, which
    # is why the CSV's description column calls `dewiki` directly (Bill, 2026-08-19).
    return dewiki(s).replace("|", "/").strip()

def fy_display(fm):                          # never a blank cell / blank link text
    return fy_normalise(fm_get(fm, "fiscal_year_label")) or fm_get(fm, "fy_start")[:4] or "—"

def deal_usd(T):
    """The rule (Bill, 2026-07-29): always use commitment; where no commitment exists,
    use disbursed and note it.

    Returns (value_or_None, basis) with basis in {"commitment", "disbursed", ""}, so
    every surface can *state* the composition of a total instead of leaving a reader to
    infer it. Before this, the fallback happened in two places and not in a third, and
    the page's own total contradicted the rows printed above it (housekeeping job 21).
    """
    v = usd_millions(T.get("Commitment (USD)", ""))
    if v:
        return v, "commitment"
    v = usd_millions(T.get("Disbursed (USD)", ""))
    if v:
        return v, "disbursed"
    return None, ""


# ------------------------------------------------- the domestic classification chain
def vote_num(rec):
    v = fm_get(rec["fm"], "admin_head_code")          # the field, where the record carries it
    if v:
        return v
    m = re.search(r'-vote-?(\d+)', rec["deal_id"])    # fallback: parse the id (pre-migration)
    return m.group(1) if m else ""

def cfield(rec, key, table_key=""):
    """A classification field: frontmatter first, body table as the migration fallback.

    finance-load-domestic-state.md moved the chain into frontmatter on 2026-08-01
    (codes are the cross-year join key, and the compile is scripted — it cannot parse
    prose). The corpus is mid-migration, so fall back to the body table where the
    field is absent. Drop the fallback once housekeeping job 34 is closed."""
    v = fm_get(rec["fm"], key)
    if not v and table_key:
        v = rec["table"].get(table_key, "")
    return clean(v)

def line_name(rec):
    """The programme/line name, from the record itself — not the bare deal_id."""
    T = rec["table"]
    prog = " — ".join(x for x in [cfield(rec, "programme", "Programme"),
                                  cfield(rec, "sub_programme", "Subprogramme")] if x)
    if prog:
        return clean(prog)
    m = re.search(r'[«"“](.+?)[»"”]', rec["title"])           # the quoted line name in the title
    if m:
        return clean(m.group(1))
    ent = re.sub(r'\s*\([^)]*\)\s*$', "", T.get("Spending entity", "")).strip()
    return clean(ent) or rec["deal_id"]

# ---------------------------------------------------------------- deal year, window, scope
def deal_year(r):
    """The deal's own year, which is authoritative (Bill, 2026-09-23): the commitment year, else
    the start year, else the record's publication year. The commitment year leads (Bill,
    2026-09-26, notes-for-corpus 69): a start before the commitment is not possible, and a top-up
    loan carrying its project's earlier start is a separate deal dated by its own signing. The summary bucketed by publication
    year while the export printed this, and 114 of 1,453 rows disagreed - a 2022 Comoros grant
    summed under 2025/26. A cell counts only where it opens with a year: five records annotate
    theirs (`2015 (2015-07-06)`) or state none (`*not stated*`), and a bare string made a column."""
    T = r["table"]
    for v in (T.get("Commitment year", ""), T.get("Start year", ""), r["published"] or ""):
        m = re.match(r"\s*((?:19|20)\d\d)(?!\d)", v)
        if m:
            return m.group(1)
    return ""

FIRST_YEAR = 2015   # the home page promises commitments "made since 2015" (Bill, 2026-09-26)

def in_window(by_place):
    """Drop non-state deals whose own year falls before FIRST_YEAR, in place, and return
    how many went. OSINT keeps the records, which reports still cite; only the dataset,
    which claims a 2015 start, leaves them out. A deal with no year stays."""
    dropped = 0
    for b in by_place.values():
        keep = [r for r in b["ns"] if not (deal_year(r) and int(deal_year(r)) < FIRST_YEAR)]
        dropped += len(b["ns"]) - len(keep)
        b["ns"] = keep
    return dropped

# **Scope, as the budget lines carry it** *(Bill's ruling, 2026-10-01)*. `lookups/deal-scope.csv`
# gives each deal `whole`, `partial`, `unclear` or `out`, with a sentence saying why. A
# `partial` or `unclear` deal counts at half its amount, as `budget_source.PARTIAL_SHARE` does
# for a budget line; an `out` deal is one where digital is incidental to another purpose and
# is left out of the dataset. OSINT keeps every record. `documentation/nonstate-scope.md`.
HALF_SCOPES = ("partial", "unclear")
SCOPE_SHARE = 0.5


def load_scope():
    with open(SCOPE_FILE, encoding="utf-8-sig", newline="") as f:
        return {r["deal_id"]: (r["scope"], r["scope_basis"]) for r in csv.DictReader(f)}


def in_scope(by_place, scope):
    """Tag each non-state deal with its scope and basis, and drop the ones marked `out`,
    in place. Returns `(out, halved, unassessed)` as sets of deal ids. A deal the lookup
    does not hold yet stays in at its full amount with a blank scope, and is counted so
    the build can say so."""
    out, halved, unassessed = set(), set(), set()
    for b in by_place.values():
        keep = []
        for r in b["ns"]:
            s, basis = scope.get(r["deal_id"], ("", ""))
            if s == "out":
                out.add(r["deal_id"])
                continue
            if not s:
                unassessed.add(r["deal_id"])
            elif s in HALF_SCOPES:
                halved.add(r["deal_id"])
            r["scope"], r["scope_basis"] = s, basis
            keep.append(r)
        b["ns"] = keep
    return out, halved, unassessed


def scope_note(out, halved, unassessed):
    return (f"  scope: {len(out)} non-state deals left out, {len(halved)} counted at half"
            + (f"; {len(unassessed)} NOT YET ASSESSED, counted in full - judge them into "
               f"lookups/deal-scope.csv: {', '.join(sorted(unassessed)[:20])}"
               if unassessed else ""))


def share(r):
    return SCOPE_SHARE if r.get("scope") in HALF_SCOPES else 1


# ---------------------------------------------------------------- CSV exports
# Canonical financier display name (approved map -> entity-page title -> prettified
# slug) moved to finance_lib 2026-08-03, so every reader of a financier's name uses one
# function, not a copy. `fin_name` stays importable from here.

def recip_org(T):
    """Recipient organisation, name only — no descriptive suffix, no trailing (ISO3)."""
    v = T.get("Recipient", "").strip()
    # "(unspecified — pan-African start-ups)" names no organisation; the dash split below
    # would otherwise publish "(unspecified" as one.
    if not v or v.lower().startswith(("recipient unspecified", "unspecified", "(")):
        return ""
    v = re.split(r'\s[—–]\s|\s-\s', v)[0].strip()      # cut at em/en dash or spaced hyphen only
    v = re.sub(r'\s*\([A-Z]{3}\)\s*$', '', v).strip()  # drop a trailing country tag
    return clean(v)

NS_HEADER = ["recipient", "start_year", "end_year", "published_date", "financier", "primary_topic",
             "instrument", "aid", "commitment_usd_m", "amount_basis", "amount_quality",
             "scope", "scope_basis", "status",
             "title", "description",
             "beneficiary_type", "recipient_organisation", "original_amount",
             "project_id", "iati_activity_id", "url", "financier_slug", "deal_id", "record"]


def published_date(r):
    """When the source was published, or, where OSINT holds only the year or month, when
    OSINT found it (Bill, 2026-09-27). A year-precision record's `published` is stamped
    `YYYY-01-01` — 1,066 of 1,402 deals, most of them IATI activities — and printing that
    would date a 2019 activity record to New Year's Day."""
    if fm_get(r["fm"], "date_precision") == "day":
        return r["published"] or ""
    return fm_get(r["fm"], "ingested") or r["published"] or ""


def usd_m_cell(usd):
    """The `commitment_usd_m` cell: US$m, and never a real amount printed as zero.

    The column was `f"{usd:.0f}"`, which is right above a million and a falsehood below
    it: on 2026-09-17 forty of the 1,455 deals published **0** against a stated amount —
    a US$450,000 equity ticket, a US$350,000 census grant, UNESCO transfers down to
    US$366.85. A reader downloading the CSV could not tell those from the 44 rows whose
    amount genuinely is not held, which read blank, and summing the column loses them
    silently. The aggregate never had the bug: `usd_millions` returns a float and the
    subject totals add that, so this changes the published cell and no total.

    Three significant figures below a million is enough to keep the smallest deal held
    (US$366.85 → 0.000367) distinguishable from nothing, and an empty string stays what
    it has always meant: no amount is held. A genuine zero is not a deal."""
    if not usd:
        return ""
    return f"{usd:.0f}" if usd >= 1 else f"{usd:.3g}"


def halved_cell(usd):
    """A halved amount keeps its half million: US$45m at half is 22.5, never 22, so that
    doubling the cell gives back the amount as announced."""
    if not usd:
        return ""
    h = usd * SCOPE_SHARE
    return f"{h:.1f}".rstrip("0").rstrip(".") if h >= 1 else f"{h:.3g}"


def amount_quality(rec):
    """How the amount was arrived at — frontmatter first, body table as fallback.

    `interpolated` is the one value that changes what a page may say: the figure is
    CONSTRUCTED, not published. Four Mastercard Foundation records carry straight-line
    annual increments between anchored milestones, built so the series sums to a
    source-stated cumulative — so the total is real and no single row is. It was
    recorded only as `Estimated` in a body table, which is what 98 genuine estimates
    of a disclosed figure also say, and which nothing downstream could read.
    (Note 101; Bill ruled 'flag them as derived', 2026-08-03.)"""
    return (fm_get(rec["fm"], "amount_quality")
            or rec["table"].get("Amount quality", "")).strip().lower()

# **`aid` is true for the three instruments that are aid** *(Bill, 2026-09-30)*: a grant, a
# concessional loan or technical assistance. Everything else is false, `Unknown` included —
# an instrument nobody could name is not counted as aid.
AID_INSTRUMENTS = {"grant", "concessional loan", "technical assistance"}


def is_aid(instrument: str) -> str:
    return "true" if (instrument or "").strip().lower() in AID_INSTRUMENTS else "false"


def _ns_row(r, country, lab):
    T = r["table"]; fm = r["fm"]
    usd, basis = deal_usd(T)
    sec = primary_subject(r)
    status = T.get("Status", "")
    return [country, deal_year(r), T.get("End year", ""), published_date(r),
            fin_name(fm_get(fm, "financier_slug")), lab.get(sec, sec),
            T.get("Instrument", ""), is_aid(T.get("Instrument", "")),
            halved_cell(usd) if share(r) != 1 else usd_m_cell(usd), basis,
            amount_quality(r), r.get("scope", ""), r.get("scope_basis", ""), status,
            dewiki(r["title"]), dewiki(section(r["body"], "Description")),
            T.get("Beneficiary type", ""), recip_org(T), T.get("Original amount", ""),
            T.get("Project ID", ""), T.get("IATI activity ID", ""),
            r["url"], fm_get(fm, "financier_slug"), r["deal_id"], r["fn"][:-3]]

def csv_nonstate(ns, lab, iso3, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:   # BOM for Excel
        w = csv.writer(f); w.writerow(NS_HEADER)
        for r in sorted(ns, key=lambda x: x["published"], reverse=True):
            w.writerow(_ns_row(r, iso3, lab))

def csv_nonstate_all(by_place, lab, path):
    """One combined file, one row per deal (deduped by record). `recipient` is
    the record's own place — each deal is tagged to exactly one place (country or, for
    multi-country deals, a region), so this is a clean partition with no double-count."""
    seen = {}
    for iso3, bucket in by_place.items():
        for r in bucket["ns"]:
            seen.setdefault(r["fn"], (r, iso3))   # a deal lives under exactly one place
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(NS_HEADER)
        for r, iso3 in sorted(seen.values(), key=lambda x: (x[0]["published"] or ""), reverse=True):
            w.writerow(_ns_row(r, iso3, lab))
    return len(seen)

def csv_budget(dom, iso3, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:   # BOM for Excel
        w = csv.writer(f)
        # The classification chain, one column per level with its code — the codes are
        # the cross-year join key (finance-load-domestic-state.md § Classification).
        # programme_line stays as a trailing DISPLAY column: it is all 395 unmigrated
        # records carry. Drop it when housekeeping job 34 closes.
        # `source_tier`, `doc_type` and `doc_locator` are the citation *(2026-09-20, R53)*.
        # These rows publish on the Finance page from this run, and a figure a reader
        # cannot trace to the instrument it came from is a figure they have to take on
        # trust. The three together say which kind of source the line rests on and where
        # in it the number is printed — the same job `url` does on the non-state side,
        # where the source is a web page rather than page 412 of a gazette.
        w.writerow(["fy", "admin_head_code", "admin_head",
                    "spending_entity_code", "spending_entity",
                    "programme_code", "programme",
                    "sub_programme_code", "sub_programme", "econ_class",
                    # How the head and the programme are known, and the programme's grain
                    # *(Bill, 2026-09-22)*: a `derived` value is a stand-in and says so.
                    "admin_head_basis", "programme_basis", "programme_level",
                    # `proposed` was missing from the ladder *(2026-09-20, R53)*. The driver's
                    # stage vocabulary opens at `proposed` (tabled, pre-enactment) and several
                    # countries hold nothing else — Sierra Leone's whole record is a tabled
                    # figure, and Cameroon's FY2026 is proposed throughout because the enacted
                    # law is a scan. Exporting the ladder from `appropriated` onwards published
                    # those lines with every money column empty, which reads as a row with no
                    # figure rather than as a figure at the stage it was observed at.
                    "proposed", "appropriated", "revised", "released",
                    "actual", "audited", "exec_vs_voted", "exec_vs_revised",
                    "baseline_stage", "current_stage", "scope_confidence", "is_transfer",
                    "currency", "source_tier", "doc_type", "doc_locator",
                    # `source_slug` names the held document a Corpus extraction was read out
                    # of *(2026-09-20, R54)*; it is blank on an OSINT record, whose citation
                    # is the record `record` names. `finance.py` drops both from the published
                    # download for the same reason — they are keys into trees only we hold.
                    "source_slug",
                    # `origin_record` names the OSINT record a migrated row came from
                    # *(2026-09-20, R56a)* — empty on a row a BUDGET-EXTRACT sitting read,
                    # and the one column that says which of the two a published figure is.
                    "origin_record",
                    "record", "programme_line"])
        def sk(r):
            n = vote_num(r); return (fm_get(r["fm"], "fy_start"), int(n) if n.isdigit() else 999, r["deal_id"])
        for r in sorted(dom, key=sk):
            fm = r["fm"]
            w.writerow([fy_display(fm), vote_num(r), cfield(r, "admin_head"),
                        cfield(r, "spending_entity_code"),
                        cfield(r, "spending_entity", "Spending entity"),
                        cfield(r, "programme_code"), cfield(r, "programme", "Programme"),
                        cfield(r, "sub_programme_code"),
                        cfield(r, "sub_programme", "Subprogramme"),
                        cfield(r, "econ_class"),
                        fm_get(fm, "admin_head_basis"), fm_get(fm, "programme_basis"),
                        fm_get(fm, "programme_level"),
                        fm_get(fm, "proposed_total"),
                        fm_get(fm, "appropriated_total"), fm_get(fm, "revised_total"),
                        fm_get(fm, "released_total"),
                        fm_get(fm, "actual_total"), fm_get(fm, "audited_total"),
                        fm_get(fm, "execution_pct_vs_appropriated"), fm_get(fm, "execution_pct_vs_revised"),
                        fm_get(fm, "baseline_stage"), fm_get(fm, "current_stage"),
                        fm_get(fm, "scope_confidence"), fm_get(fm, "is_transfer"),
                        fm_get(fm, "currency"),
                        fm_get(fm, "source_tier"),
                        cfield(r, "doc_type", "doc_type"),
                        cfield(r, "doc_locator", "doc_locator"),
                        fm_get(fm, "source_slug"), fm_get(fm, "origin_record"),
                        # `record_ref` where the row came from Corpus's source folder: the
                        # file and the deal_id inside it, which is what a reader of this
                        # column wants — the place the row is maintained.
                        r.get("record_ref") or r["fn"][:-3],
                        r.get("line_name") or line_name(r)])

# ---------------------------------------------------------------- assemble
def scan_all():
    """One pass over raw/: bucket every finance record under each place it tags."""
    by_place = {}
    for fn, path in raw_sources(RAW):
        # errors="replace": a raw body is upstream evidence Corpus cannot repair, and
        # OSINT holds at least one record with a stray byte from a PDF extraction. A
        # single bad byte must degrade that record, never halt the build.
        t = open(path, encoding="utf-8", errors="replace").read()
        if "finance_origin:" not in t:      # cheap prefilter only — a superset, see below
            continue
        fm, body = split_front(t)
        if not fm:
            continue
        # The real test is the frontmatter key, never the file text. A record retired by
        # merge drops `finance_origin:` and says so in its retirement note — so the note's
        # own words passed the prefilter and the record was then bucketed as domestic,
        # putting a junk row in 8 budget exports. (Found and fixed 2026-08-03, housekeeping 38.)
        if not re.search(r'^finance_origin:\s*\S', fm, re.M):
            continue
        pm = re.search(r'places:\s*\[([^\]]*)\]', fm)
        places = re.findall(r'[A-Z]{3}|X[A-Z]{2}', pm.group(1)) if pm else []
        if not places:
            continue
        tm = re.search(r'topics:\s*\[([^\]]*)\]', fm)
        rec = dict(fn=fn, fm=fm, body=body, table=deal_table(body),
                   origin=fm_get(fm, "finance_origin"), published=fm_get(fm, "published"),
                   topics=[x.strip() for x in tm.group(1).split(",")] if tm else [],
                   url=(fm_get(fm, "url") or "").split()[0] if (fm_get(fm, "url") or "").split() else "", title=fm_get(fm, "title"),
                   deal_id=fm_get(fm, "deal_id"), currency=fm_get(fm, "currency"))
        for pl in places:
            b = by_place.setdefault(pl, {"ns": [], "dom": []})
            b["ns" if rec["origin"] == "non-state" else "dom"].append(rec)
    return by_place

def rec_fy(r):
    """The bare fiscal-year start year a domestic record belongs to.

    `fy_start` first, because it is an ISO date and unambiguous; the label second, because
    the migration left some records carrying only that. The label's own first four digits
    are the start year by the spec's rule — *a bare year means the fiscal year beginning in
    that year* — so `2024/25`, `2024-2025` and `2024` all answer 2024, which is what makes
    the merge below insensitive to how a state writes its year."""
    fy = fm_get(r["fm"], "fy_start")[:4]
    if fy.isdigit():
        return fy
    m = re.search(r"\d{4}", fm_get(r["fm"], "fiscal_year_label"))
    return m.group(0) if m else ""


def merge_source(iso3, dom):
    """OSINT's records for this place, with Corpus's own extractions swapped in.

    **Replace, never add** — the rule the review set with the source folder (R56a). Where
    `budgets/budgets-{ISO3}.csv` holds a fiscal year, every OSINT record for that year is
    dropped and the file's rows stand in their place; a year the file says nothing about is
    untouched.
    Returns `(records, [(fy, dropped, added), ...])` so the caller can *print* the swap: a
    build that silently replaced a country's published figures with a different reading of
    the same document would be indistinguishable from one that lost them.

    A file that fails `budget_source.check` raises out of here and stops the compile."""
    src = budget_source.records(iso3)
    if not src:
        return dom, []
    years = {r["source_fy"] for r in src}
    kept = [r for r in dom if rec_fy(r) not in years]
    swaps = [(fy,
              sum(1 for r in dom if rec_fy(r) == fy),
              sum(1 for r in src if r["source_fy"] == fy))
             for fy in sorted(years)]
    return kept + src, swaps


def swap_note(iso3, swaps):
    """What the merge did, per fiscal year, on the build's own line. Silence would be worse
    than noise here: the whole effect of the source folder is that some published rows are
    no longer the ones OSINT's records would have produced."""
    if not swaps:
        return ""
    parts = [f"FY{fy} {out}->{ins}" for fy, out, ins in swaps]
    return f"  [budgets/budgets-{iso3}.csv: " + "; ".join(parts) + "]"


def build_one(iso3, ns, dom, lab):
    csv_nonstate(ns, lab, iso3, os.path.join(NONSTATE_OUT, f"{iso3}-nonstate.csv"))
    dom, swaps = merge_source(iso3, dom)
    budget_csv = os.path.join(BUDGET_OUT, f"{iso3}-budget.csv")
    if dom:
        csv_budget(dom, iso3, budget_csv)
    elif os.path.exists(budget_csv):     # no budget CSV where there is no budget data — the
        os.remove(budget_csv)            # gap is the signal, so a stale one has to go
    return len(ns), len(dom), swaps

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "ZAF"
    # Any other flag was being read as a place code, so `--help` wrote
    # `--help-nonstate.csv` into outputs/ (found by review task 25's smoke test).
    if arg.startswith("-") and arg != "--all":
        print(__doc__.strip())
        return 0
    lab = taxonomy_labels()
    for d in (BUDGET_OUT, NONSTATE_OUT):
        os.makedirs(d, exist_ok=True)
    if arg == "--all":
        by_place = scan_all()
        print(f"  before {FIRST_YEAR}: {in_window(by_place)} non-state deals left out")
        print(scope_note(*in_scope(by_place, load_scope())))
        # A country Corpus has extracted and OSINT holds no finance record for is still a
        # country with a budget export. `scan_all` only sees raw/, so it would be skipped
        # entirely — and the 32 states with no domestic records at all (R58) are exactly the
        # ones the source folder is for.
        for iso3, _ in budget_source.files():
            by_place.setdefault(iso3, {"ns": [], "dom": []})
        budget_source.update()
        for iso3 in sorted(by_place):
            nn, nd, swaps = build_one(iso3, by_place[iso3]["ns"], by_place[iso3]["dom"], lab)
            print(f"  {iso3}: {nn} non-state, {nd} domestic" + swap_note(iso3, swaps))
        n_all = csv_nonstate_all(by_place, lab, os.path.join(NONSTATE_OUT, "all-nonstate.csv"))
        print(f"wrote CSV exports for {len(by_place)} places to {NONSTATE_OUT}/ and "
              f"{BUDGET_OUT}/ + all-nonstate.csv ({n_all} deals)")
    else:
        by_place = scan_all()
        in_window(by_place)
        print(scope_note(*in_scope(by_place, load_scope())))
        b = by_place.get(arg, {"ns": [], "dom": []})     # place-based, matches --all exactly
        budget_source.update(arg)       # the country file's budget_usd, then the all-countries file
        nn, nd, swaps = build_one(arg, b["ns"], b["dom"], lab)
        print(f"wrote {arg} CSV exports  ({nn} non-state, {nd} domestic)"
              + swap_note(arg, swaps))

if __name__ == "__main__":
    main()
