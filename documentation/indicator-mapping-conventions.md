---
type: procedure
reader: cc
title: indicator-mapping-conventions.md — how a ledger row is mapped onto the frame
last_reviewed: 2026-10-17
status: in force — binds every mapping pass over a country ledger
---

# Mapping conventions for the indicator frame

*(The mapping fed the progress report until it retired on 2026-10-17 (Bill); it now feeds the
maturity assessment, which takes each indicator's evidence from its `row_ids`
(`maturity-assess.py` → `due_at`). The `progress`, `summary` and `developments` columns are no
longer drafted. A convention that lives only in the head of whichever pass ran first is how fifty-four countries
end up answering fifty-four different questions; these are the calls, written down.)*

## The file holds what is mapped and nothing else

`outputs/reports/{unit}/indicators.csv` carries **only the indicators with evidence behind them**.
An indicator absent from the file has no evidence, which is what `load_unit()` already
assumes — so ERI's file is thirteen rows, not a hundred and twenty-one with a
hundred and eight blanks. Writing the No evidence rows out explicitly is noise that has to be
maintained, and the frame is the thing that says what was asked.

## Which indicator a row belongs to

**The indicator is chosen by what the row is, not by the subject the ledger filed it under.** The
ledger's `subject` is a taxonomy position assigned when the row was minted; the frame asks a
different question and the two do not always land together. ASYCUDA World sits on ERI's ledger
under `dpi.exchange`, and it is a customs system: it maps to `dpi.mis--customs`. Following the
subject would have put a customs platform under national data exchange and left the customs
indicator reading No evidence with the evidence sitting one row away.

**One row may map to several indicators, and should where it genuinely answers several.** ERI's
EriTel expansion row carries both a fibre figure and a bandwidth figure, and it is mapped to
`infra.connect--national-fibre-backbone` and `infra.connect--international-internet-bandwidth`
because it answers both.

**One indicator may take several rows.** `row_ids` is pipe-separated, like the ledger's own
`sources`.

**One measure may cite a budget file instead** *(2026-09-23, `indicator-financial-sustainability.md`
§7)*. `finance.sustain--financial-sustainability-of-digital-systems` takes its figure from
`budgets/budgets-{ISO3}.csv` and `external.csv`, not from a ledger row, so its `value_source` is that
country-year and its `row_ids` may be empty; a stage-1 citation is then satisfied by the
`value_source`. No other indicator has this exception. **Dormant since 2026-09-30**: `external.csv`
was retired as stale (Bill), so no compiled figure exists and the measure stands on a drafter's verdict.

## Placeholder rows are not evidence

A ledger row whose status is *Not held* **with no source on file** — ERI's `gov.protect-none` and
`dpi.pay-none` are the pattern — is a marker that the base looked and found nothing. It is
**not mapped**. Mapping it would hand the maturity assessment a position resting on a citation
that does not exist.

A *Not held* row that **does** carry a source is different and **is** mapped: Starlink listing
Eritrea with no planned launch date, or the cable industry's registry showing no landing, are
dated, cited, checkable statements that the thing is absent, and the citation is what
distinguishes a reported absence from an unexamined one.

## Further calls

**The unmapped placeholders are not lost — they surface in the gaps section.** The renderer still
prints *Where the record is thin* from the ledger's Not-held rows, so a `-none` row that the
mapping pass declines to map appears there with what would settle it.
