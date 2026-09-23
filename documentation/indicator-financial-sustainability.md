---
type: task
title: indicator-financial-sustainability.md — add a financial sustainability indicator in place of finance.mou
last_reviewed: 2026-09-22
status: planned, for CC to carry out per adding-an-indicator.md; no taxonomy change if Bill accepts the finance.budget placement (§1); evidence depends on the budget-extract queue (§7)
---

# Financial sustainability — a new indicator in place of `finance.mou--strategic-relationships`

*(Written 2026-09-22 in Cowork on Bill's ruling that `finance.mou--strategic-relationships` leaves the assessment — a relationship is not a position — and that a financial sustainability indicator takes its place. This answers `adding-an-indicator.md` §§0–10 for that one indicator. The retired row stays in the frame with `assessed = 0`; its 54 mapped rows stay where they are.)*

## 0. The question

**Is the digital state paying for itself — are the systems in service funded to run from the state's own resources, and is the money that is voted actually spent?**

It is a measure, and that is the point: the base already reads budgets line by line (`BUDGET-EXTRACT.md`, `budget-extract.md`), applies an origin gate to every line — *domestic-revenue · domestic-borrowing · own-source* against *external-loan · external-grant · counterpart* — and carries the stage history from proposed through appropriated to actual. Nobody else publishes a country-by-country domestic share of digital spending with a citation on every line, and this indicator is where that work becomes a position.

It is distinct from the instrument beside it. `finance.budget--sustainable-domestic-financing-of-digital-transformation` asks whether a *mechanism* exists — a budget line, a fund, a levy or own-source revenue written into the finance law. This asks what the state *actually carries*. A country can have the mechanism and a 15 % domestic share, or no mechanism and a treasury that quietly pays for everything; the two rows together say which.

## 1. The subject — `finance.budget`, which exists

Proposed under **`finance.budget` — Domestic budget appropriations and expenditure**, because the subject label already covers expenditure and the evidence is the budget file. No taxonomy change, no OSINT dependency. The alternative — a new `finance.sustain` subject so that the indicator has a section of its own — would travel to OSINT as a patch alongside `geopol.sovereignty`; it is Bill's call (`maturity-assessment.md` §13), and this note is written for `finance.budget`. `finance.mou` keeps its retired row and prints nothing in the assessment.

The status outline marks `finance.budget` *suspended pending budget work*. That suspension is what this indicator ends: the budget work exists now, and the sub-section's question can be answered from `budgets/`.

## 2. The id

`finance.budget--financial-sustainability-of-digital-systems`. Display text *Financial sustainability of digital systems*. No collision.

## 3. The frame row

`finance.budget--financial-sustainability-of-digital-systems, 7, 2, Finance, Domestic budget appropriations and expenditure, finance.budget, Financial sustainability of digital systems, measure, 1` — `Indicator Sort` 2, after the existing `finance.budget` row. `finance.mou--strategic-relationships` gets `assessed = 0`, `retired = 2026-09-22` in the same edit.

**Kind: measure.** The figure of record is defined in §5.

## 4. The norm

Already in `maturity-assessment-norms.md` §3 (Finance). Tier **AU**; anchor **Agenda 2063 Goal 20** — *Africa takes full responsibility for financing her development* — with its First Ten-Year Plan targets (the proportion of aid in the national budget no more than 25 % of its 2013 level; national capital markets contributing at least 10 % of development financing), the **Addis Ababa Action Agenda** action area I on domestic public resources, and the **DTS**'s digital sovereignty fund. Fixes: a proxy target (the Goal 20 ratios are budget-wide, not digital) and Africa-only quintiles for the bands. Reference: the Broadband Commission's Target 1 (a *funded* national broadband plan) and the GPEDC's on-budget and country-systems indicators. Dataset: **Corpus's own** `budgets/{ISO3}/{FY}.csv`, which under `maturity-assessment-norms.md` §7 is not merely preferred over any global source here but the only one — no global dataset carries a digital-specific domestic share.

## 5. The rubric

**The figure of record** is the **domestic-state share of the digital lines of the state's own budget document for the latest read fiscal year**: domestic-state appropriated ÷ (domestic-state appropriated + externally financed digital lines in the same document), from the origin gate. `value` is the share, `unit` is per cent, `value_year` the fiscal year, `value_source` the country-year's `source_slug`. Two secondary figures ride in the qualifier and can hold the stage down: **execution** (`exec_vs_voted`, where an `actual` stage is held) and **recurrent coverage** (whether the lines that keep systems running — maintenance, licences, subscriptions, connectivity — are domestic-state, where `econ_class` lets the extract tell).

**A country whose `budgets/` folder holds only migrated placeholder rows is *unassessed*.** 372 of the 640 rows in `budgets/` on 2026-09-22 carry an `origin_record` and have not been read; four country-years have (GHA, MDG, NER, CAF, per `logs/budget-extract.csv`). The queue is `python scripts/budget_source.py`, and until a country-year is read the assessment says *No evidence*, which is true and is the sweep brief.

**One extension to the extract is needed** (§7): the externally financed digital lines are gated to *the non-state side* today and their magnitudes are stated as a dated finding in the sitting's log note, not in the CSV. The share needs the denominator, so the sitting records the external digital total for the country-year as a companion figure — one row per country-year in a small `budgets/{ISO3}/external.csv` or a column on the log, CC's call — with the same document and locator discipline as the domestic rows. A document that prints no origin column (NER's finance law is the case in the log) yields a share flagged *origin inferred* in the qualifier, per the spec's own rule.

| stage | anchor | interpolated |
|---|---|---|
| 1 Absent | Domestic-state share in the bottom Africa quintile, or no domestic-state digital line at all in a read budget document; operating costs of systems in service externally financed or unfunded | yes |
| 2 Nascent | Second quintile; digital lines appropriated but the majority externally financed; recurrent lines not separately provided or not domestic | yes |
| 3 Established | Middle quintile; domestic-state carries a substantial minority or a bare majority; recurrent lines exist and are domestic; execution held or credible | yes |
| 4 Operating | Fourth quintile; domestic-state carries the clear majority including recurrent costs; execution against voted ≥ a stated floor where an outturn is held; own-source or levy mechanisms in the finance law | yes |
| 5 Leading | Top quintile; multi-year domestic financing of the estate with renewal provisioned, external finance confined to capital, outturn published and audited — the Goal 20 posture applied to the digital estate | partly — Goal 20 states the posture, not the digital share |

**Provisional absolute bands until the quintiles can be cut.** Africa-only quintiles *(Bill)* need enough read country-years to mean anything; with four, they do not. Until fifteen countries have a read country-year, the bands are absolute on the share — < 20 %, 20–40 %, 40–60 %, 60–80 %, > 80 % — and the rubric row says *provisional*. At fifteen the quintiles are cut, the vintage recorded, and every affected row is flagged `reassessed` in that month; thereafter they are recut each July with the rest of the measure quintiles.

**Which part decides.** The share sets the stage; execution and recurrent coverage can lower it by one, never raise it, and the qualifier names which did.

## 6. The status outline

Under `### finance.budget`, lift the *suspended* marker and add the bullet: whether the digital estate is domestically financed and executed — answered from `budgets/{ISO3}/{FY}.csv` (share, stages, execution), not from any DPI variable; where the folder holds only migrated rows, the section says the budget has not yet been read, dated.

## 7. The mapping pass

**The evidence is not in the ledger; it is in `budgets/`.** This is the first indicator whose figure of record comes from a Corpus-maintained dataset rather than a mapped ledger row, and the mapping conventions need one sentence for it: a measure may cite a `budgets/` country-year as its `value_source`, and its `row_ids` then carry the ledger rows that give the position context (the finance law's passage, a supplementary, an audit report) rather than the figure itself. Where no ledger row exists the `row_ids` may be empty for this indicator alone, and the check that stage 1 requires a citation is satisfied by the `value_source`. CC writes that exception into `indicator-mapping-conventions.md` at build.

The pass itself is arithmetic over the read country-years plus the extension in §5, run inside the assessment pass; the sitting procedure in `BUDGET-EXTRACT.md` gains one step — record the external digital total — so that every future read country-year arrives assessable.

## 8. Snapshots

Assessed retrospectively as at 2026-07-31 and 2026-08-31 with the rest of the frame. The figure's `value_year` is the fiscal year read, which for most countries will predate the as-at by a year or more; that is the normal shape of a budget measure and the grid prints the year.

## 9. Checks, methodology, changelog

The frame checks in `maturity-assessment.md` §11, plus one of its own: `value` for this indicator must equal the share recomputed from the country-year's rows and the external figure, to the rounding stated. Changelog entry: *The Finance chapter of the maturity assessment now carries a financial sustainability indicator — the share of a country's digital budget lines that its own treasury finances, read from the budget document — in place of a row that recorded agreements signed. A reader sees whether the digital state pays for itself; a country whose budget has not yet been read shows No evidence until it has.*

## 10. The one that retires

`finance.mou--strategic-relationships` — `assessed = 0`, `retired = 2026-09-22`; rows, mapped rows and prose kept; the status report's `finance.mou` sub-section is unaffected.

## Build steps, in order

1. Bill: confirm `finance.budget` as the subject, or ask for `finance.sustain` (then §1 of `indicator-digital-sovereignty.md` applies and the two slugs travel in one patch).
2. CC: edit `lookups/indicators.csv` (§3), the norms lookup row (§4), the five rubric rows with the provisional bands (§5), the status outline (§6), the mapping-conventions exception (§7). One commit.
3. CC: extend the extract to record the external digital total per country-year (§5), backfilling it for the four read country-years from the log notes and the documents; add the step to `BUDGET-EXTRACT.md`. One commit.
4. CC: the assessment arithmetic and its check (§9), run inside the baseline pass. Changelog.

Nothing here has been done. The frame is unchanged, the extract is unextended, no share has been computed.
