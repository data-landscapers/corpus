---
type: task
title: indicator-financial-sustainability.md — add a financial sustainability indicator in place of finance.mou
last_reviewed: 2026-09-22
status: planned, for CC to carry out per adding-an-indicator.md; subject finance.sustain ruled by Bill 2026-09-23 (§1), so blocked on OSINT adding it; evidence depends on the budget-extract queue (§7)
---

# Financial sustainability — a new indicator in place of `finance.mou--strategic-relationships`

*(Written 2026-09-22 in Cowork on Bill's ruling that `finance.mou--strategic-relationships` leaves the assessment — a relationship is not a position — and that a financial sustainability indicator takes its place. This answers `adding-an-indicator.md` §§0–10 for that one indicator. The retired row stays in the frame with `assessed = 0`; its 54 mapped rows stay where they are.)*

## 0. The question

**Is the digital state paying for itself — are the systems in service funded to run from the state's own resources, and is the money that is voted actually spent?**

It is a measure, and that is the point: the base already reads budgets line by line (`BUDGET-EXTRACT.md`, `budget-extract.md`), applies an origin gate to every line — *domestic-revenue · domestic-borrowing · own-source* against *external-loan · external-grant · counterpart* — and carries the stage history from proposed through appropriated to actual. Nobody else publishes a country-by-country domestic share of digital spending with a citation on every line, and this indicator is where that work becomes a position.

It is distinct from the instrument beside it. `finance.budget--sustainable-domestic-financing-of-digital-transformation` asks whether a *mechanism* exists — a budget line, a fund, a levy or own-source revenue written into the finance law. This asks what the state *actually carries*. A country can have the mechanism and a 15 % domestic share, or no mechanism and a treasury that quietly pays for everything; the two rows together say which.

## 1. The subject — `finance.sustain`, which does not exist yet

**`finance.sustain` — Financial sustainability** *(Bill, 2026-09-23)*: `finance.budget` is for the facts of actual budgets, and `finance.sustain` covers efforts to make the digital estate financially sustainable — domestic financing mechanisms, funds and levies, cost recovery, plans to take externally financed systems onto the budget. The figure of record is still read from `budgets/` (§5); the subject is where the indicator sits and where sources about those efforts are tagged, and its mapped rows give the figure its context.

It is an OSINT change, cut in one patch with `geopol.sovereignty` (`indicator-digital-sovereignty.md` §1). Nothing in the frame is minted until the mirror shows the subject. `finance.mou` keeps its retired row and prints nothing in the assessment.

The instrument row `finance.budget--sustainable-domestic-financing-of-digital-transformation` keeps its subject and its id, which are never renamed, although its question is closer to the new subject's scope; its mapping may cite `finance.sustain` rows like any other.

## 2. The id

`finance.sustain--financial-sustainability-of-digital-systems`. Display text *Financial sustainability of digital systems*. No collision.

## 3. The frame row

`finance.sustain--financial-sustainability-of-digital-systems, 8, 1, Finance, Financial sustainability, finance.sustain, Financial sustainability of digital systems, measure, 1` — `Topic Sort` 8, after `finance.budget`; the subjects after it renumber by one, which is display order only. *(Minted 2026-09-23, task B3. Appending it at 40 was the first plan; the catalogue's topic facet starts a group whenever the chapter changes, so Finance would have printed twice.)* `finance.mou--strategic-relationships` gets `assessed = 0`, `retired = 2026-09-22` in the same edit.

**Kind: measure.** The figure of record is defined in §5.

## 4. The norm

Already in `maturity-assessment-norms.md` §3 (Finance). Tier **AU**; anchor **Agenda 2063 Goal 20** — *Africa takes full responsibility for financing her development* — with its First Ten-Year Plan targets (the proportion of aid in the national budget no more than 25 % of its 2013 level; national capital markets contributing at least 10 % of development financing), the **Addis Ababa Action Agenda** action area I on domestic public resources, and the **DTS**'s digital sovereignty fund. Fixes: a proxy target (the Goal 20 ratios are budget-wide, not digital) and Africa-only quintiles for the bands. Reference: the Broadband Commission's Target 1 (a *funded* national broadband plan) and the GPEDC's on-budget and country-systems indicators. Dataset: **Corpus's own** `budgets/{ISO3}/{FY}.csv`, which under `maturity-assessment-norms.md` §7 is not merely preferred over any global source here but the only one — no global dataset carries a digital-specific domestic share.

## 5. The rubric

**The figure of record** is the **domestic-state share of the digital lines of the state's own budget document for the latest read fiscal year**: domestic-state appropriated ÷ (domestic-state appropriated + externally financed digital lines in the same document), from the origin gate. `value` is the share, `unit` is per cent, `value_year` the fiscal year, `value_source` the country-year's `source_slug`. Two secondary figures ride in the qualifier and can hold the stage down: **execution** (`exec_vs_voted`, where an `actual` stage is held) and **recurrent coverage** (whether the lines that keep systems running — maintenance, licences, subscriptions, connectivity — are domestic-state, where `econ_class` lets the extract tell).

**A country whose `budgets/` folder holds only migrated placeholder rows is *unassessed*.** 372 of the 640 rows in `budgets/` on 2026-09-22 carry an `origin_record` and have not been read. On 2026-09-23 nine country-years had been (GHA, MDG and NER FY2026; CAF and ZAF FY2024–26, per `logs/budget-extract.csv`), five countries in all, and `python scripts/budget_source.py --share` computes each from the files: latest year CAF 39.8 %, GHA 86.7 %, MDG 32.2 % (at the revised stage), NER and ZAF 100 % *origin inferred*. The queue is `python scripts/budget_source.py`, and until a country-year is read the assessment says *No evidence*, which is true and is the sweep brief.

**The extract's extension is built** (task C4, 2026-09-23): the externally financed digital lines, which the origin gate sends to the non-state side, are recorded one per line per fiscal year in `budgets/{ISO3}/external.csv` with the same document and locator discipline as the domestic rows, backfilled for the nine read country-years, and `BUDGET-EXTRACT.md` step 4a makes every future sitting write them. The share is taken over whole and partial lines at the first stage both sides carry (appropriated, else revised); `budget_source.share()` is the arithmetic and `budget_source.py` checks the file. A document that prints no origin column (NER's finance law is the case in the log) yields a share flagged *origin inferred* in the qualifier, per the spec's own rule.

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

A new `### finance.sustain — Financial sustainability` sub-section, with the bullet: whether the digital estate is domestically financed and executed — answered from `budgets/{ISO3}/{FY}.csv` (share, stages, execution), not from any DPI variable — and what the state is doing to make it so, from the wiki; where the folder holds only migrated rows, the section says the budget has not yet been read, dated. `finance.budget`'s *suspended* marker is not this indicator's to lift.

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

1. Bill: ruled `finance.sustain`, 2026-09-23. CC cuts it into the OSINT patch with `geopol.sovereignty`; OSINT applies it.
2. CC: edit `lookups/indicators.csv` (§3), the norms lookup row (§4), the five rubric rows with the provisional bands (§5), the status outline (§6), the mapping-conventions exception (§7). One commit.
3. CC: extend the extract to record the external digital total per country-year (§5), backfilling it for the four read country-years from the log notes and the documents; add the step to `BUDGET-EXTRACT.md`. One commit.
4. CC: the assessment arithmetic and its check (§9), run inside the baseline pass. Changelog.

Nothing here has been done. The frame is unchanged, the extract is unextended, no share has been computed.
