---
type: review
title: maturity-rubric-review.md — CC's review of each rubric chapter before it is cut (task C2)
last_reviewed: 2026-09-23
status: Governance and the Finance instrument accepted and cut 2026-09-23; every instrument and system (95 of 117) accepted and cut 2026-09-23; the 22 measures are C3
---

# Rubric review

*(Task C2: Cowork drafts a chapter in `maturity-rubric.md` and stops; CC reviews it against `indicator-mapping-conventions.md`, the generic scale in `maturity-assessment.md` §3, the register and the two worked rubrics, then cuts it to `lookups/maturity-rubric.csv` or returns it. One section per chapter, newest last. `python scripts/lint-maturity-rubric.py --rubric documentation/maturity-rubric.md` is the mechanical half and runs first.)*

## Governance and the Finance instrument — reviewed 2026-09-23: returned, changes below

**The checker is clean**: 30 indicators, 150 rows, every Governance instrument and its one system present, stages 1–5 once each, `interpolated` consistent with the register's *fixes* on every hard rule. 112 interpolated rungs. Two warnings, both taken up below (items 5 and 7).

**The chapter is sound and close to cut.** The anchors name evidence rather than qualities, stage 1 is a citation throughout, stage 2 consistently holds the announced-but-not-adopted case, and the *never evidence* list is right. What follows is one rule the whole rubric depends on, three consistency fixes, and answers to the five questions the draft asked. Every change is an edit to `maturity-rubric.md`; when it is made, CC cuts the chapter.

### Changes

**1. The stage-selection rule leaves holes; state it as "highest anchor whose positive conditions are met".** *How to read an anchor* says a stage is reached when its anchor *and every lower stage's* is met. The lower anchors are mutually exclusive with the higher ones — stage 1 is a statement that nothing exists, stage 2 that it is only drafted — so no country with an adopted instrument meets stage 1's anchor, and read literally the rule puts nobody above stage 1. Many stage-3 anchors also carry a negative clause (*and no costed implementation plan, budget or M&E report on record* — DTS; *with no implementation plan or reporting* — ICT; *no funding source identified* — broadband; *with no enforcement decision on record* — DPA; *commencement, regulations or the authority still pending* — data protection), and a country that has part of stage 4 then fits neither 3 nor 4: an adopted strategy with a costed plan and no M&E report is excluded from 3 by the negative clause and short of 4. Replace the first paragraph's second sentence with:

> *The stage is the highest whose anchor's positive conditions are all met. Clauses saying what is still missing — "with no plan on record", "regulations pending" — describe the typical case at that stage and are not conditions; a country with part of the next stage stays at this one, and the qualifier names what it has.*

That one sentence fixes every row; no row needs editing for it.

**2. `interpolated` means "the anchoring norm does not state this rung" — references do not count.** Seven *top* rows name a reference as supplying rungs (ECOWAS/SADC/EAC, ID4D, G20 HLP, UNCTAD's areas, the Model Statistics Law's clauses, REC instruments, ISO membership class) and correctly leave those rungs `yes`. `gov.policy--broadband-strategy` does the opposite: stage 4 is `no` on the strength of Broadband Commission Target 1, which is the register's *reference*, not its anchor. Set broadband stage 4 to `yes` (stage 5 stays `no` for the DTS target), and add the rule to the `interpolated` paragraph: *a reference that informs a rung does not make it the norm's.*

**3. Where the anchor itself states the middle rungs, mark them `no`.** Three *rungs* rows understate what the norm fixes:

- `gov.policy--ai-strategy` stage 4 — the Continental AI Strategy's Phase 1 is "national strategies **and governance structures**"; the governance mechanism in stage 4 is the norm's. `no`.
- `gov.policy--data-governance-policy` stage 4 — stage 3 cites DPF Phase 1 and stage 5 Phases 4–5; Phases 2–3 sit between them. Cite them in the stage-4 anchor from the DPF text and mark it `no`; if the DPF's Phases 2–3 turn out not to be domestic implementation, say so in the row note and leave `yes`.
- `gov.protect--national-data-protection-readiness` stages 3 and 4 — see item 7.

**4. Two ids in the Finance section are the old ones.** Lines 330 and 340 name `finance.budget--financial-sustainability-of-digital-systems`; since B3 (2026-09-23) it is `finance.sustain--financial-sustainability-of-digital-systems`, in its own subject.

**5. `gov.protect--data-protection-authority` stage 5 says *effective*.** It is the DPF checklist's own word, but an assessor cannot cite effectiveness. Replace with what shows it: *enforcement decisions and sanctions published, and complaints resolved on record*.

### Answers to the draft's questions

**6. `ict-strategy` stage 5 as integration — agreed, keep it.** The DTS subsumes the sector strategy, so a country whose digital strategy carries the sector's targets is at the top whether or not a separate ICT strategy exists. Under rule 1 it reads 5 without meeting stage 4's sector-plan anchor, which is the intended result.

**7. `national-data-protection-readiness` — use the ordinary ladder, and mark 3 and 4 `no`.** Counting elements lets *guidelines adopted without a law* (stage 2) and *Malabo ratified with no law* sit on the same rung as a bill, and the checker warns because the register's *rungs* are then carried by stage 5 alone. The composite's elements are the norm's (the register's note: ratification · law in force · DPA operating · Guidelines practices), so: 2 a bill or draft; 3 a law in force (`no`); 4 law in force and an authority operating, with the Guidelines' practices on record (`no`); 5 all four plus cooperation (`no`). The drafter's own fallback in its note is this, and it is the better form.

**8. `data-localisation-policies` stage 2 holding blanket localisation — agreed, keep it.** It matches the DPF and the sovereignty indicator's own rubric, which puts *localisation with no portability* at stage 2. No edit.

**9. `open-discussion-of-government-policy` — key on 12 months, not "the window".** "The window" is the snapshot month, so as written a single month without a shutdown lifts a country to 3 and the next shutdown drops it — the series would oscillate with the news. Change *in the window* in stages 1–3 to *in the 12 months to the as-at date*. That creates the case the stability rule does not cover: a restriction ageing out of the 12 months moves the stage with no new dated row. CC takes that into D2 as a named exception (an event leaving a look-back period is itself the dated cause, dated the day it leaves), so the anchor can be written this way now.

**10. Stage 5 "aligned with" needs one test — put it in *How to read an anchor*.** Add: *"Aligned with" a continental instrument means the national instrument says so, or the AU or a REC records the country as compliant; an assessor's own comparison is not alignment.* Then the per-row wording can stay.

### After the changes

Cowork edits `maturity-rubric.md` and says so; CC re-runs the checker, reads the ten items against the file, and cuts the chapter into `lookups/maturity-rubric.csv` by script (as `maturity-norms.csv` is cut from its register), so the draft stays the source until the lookup exists. The next chapter starts after the cut.

## Governance and the Finance instrument — second review 2026-09-23: accepted and cut

**All ten items are in the draft**, and the checker reads it clean with no warnings: 30 indicators, 150 rows, 110 interpolated rungs (112 before item 2 and item 3's rungs moved). Cut by `scripts/maturity-rubric-cut.py --chapter Governance` and `--chapter Finance --kind instrument`; `--check` confirms the lookup reads as the draft.

**Cowork's own finding, taken**: the DPF has no numbered "five implementation phases", only a figure of *formulation → domestication → monitoring and evaluation*. The register's two §3 rows and §4 entry are corrected and the item is open in §6, and `lookups/maturity-norms.csv` is re-cut from the corrected register in the same commit.

**One call left as Cowork made it**: `data-governance-policy` stage 4 names the DPF's *domestication* stage but stays `yes` until the phases item is settled. That is the cautious side — it claims less for the norm, not more — and it changes no stage an assessor gives.

**Carried to D2**: the 12-month look-back exception for `open-discussion-of-government-policy` (recorded on the D2 task).

## DPI — reviewed 2026-09-23: returned, six items

**The checker is clean**: 34 indicators (31 systems, 3 instruments), 170 rows, no warnings, and the chapters already cut still read as the draft does. The two measures wait for C3, as the draft says. **The chapter is sound**: the system ladder is applied consistently, stage 1 is always a cited absence, the *rungs* rows name the norm's own stages (EMIS 1.0 → 2.0, the Framework's three layers, the HIE pillars, TADAT A–D) and mark them `no`, and every register anchor matches the heading. Six items, four of them small.

**1. There is no CAMCR 2022 target** (A2, 2026-09-23: only CAMCR-6's expert segment met; the 100 % / 80 % figures are SDG 17.19.2(b)). `dpi.id--digital-id-from-birth` — heading and stage 5 — and `dpi.registry--civil-register` stage 5 say *the CAMCR target*. Make both *the SDG 17.19.2(b) target (100 % of births, 80 % of deaths registered)*; the digital-ID row's heading takes the register's anchor, *DTS; SDG 17.19.2(b); AU No Name Campaign declaration*. The register's own civil-register row still said CAMCR-style; CC corrected it (`ae41569`), so the lookup and the draft agree once this is made.

**2. The exchange rows must read the exchange, not the system.** Three sectors carry both an MIS or registry row and an interoperability row, and in two the ladders are the same ladder:

- `dpi.exchange--interoperability-of-education-systems` stages 2–4 are `dpi.mis--education`'s stages 2–4 (EMIS procured → EMIS 1.0 → EMIS 2.0), so one country's EMIS moves both indicators together and the assessment counts one fact twice.
- `dpi.exchange--interoperability-of-social-protection-systems` stage 3 (*a programme MIS or single social registry in service … not linked*) is `dpi.mis--social-protection` stage 3 and `dpi.registry--social-protection-register` stage 3.

Rebase both exchange rows on links: 2 a link planned or piloted; 3 **one** exchange in service (the EMIS with examinations or payroll; the registry with the ID or a payment provider); 4 exchanges across the main systems on a shared identifier; 5 as drafted. For education, the DES's EMIS 2.0 is *individual-level, ID-linked*, so stages 4–5 stay `no` and stage 3 becomes `yes`; the MIS row keeps EMIS 1.0 → 2.0 as its own rungs. Health already reads the exchange and needs no change.

**3. A stage marked `no` must be the anchoring norm's, and FELA is a reference.** `dpi.registry--land-register` stage 5 and `dpi.mis--land` stage 5 are *the FELA end state*, marked `no`; FELA is the register's reference column, so by item 2 of the first review those rungs cannot be the norm's. The anchor both rows can now use is the land F&G §3.6.2 — *registration and tracking of land rights through computerized Land Information Systems* — verified in A2 and now in both register rows. Make stage 5 the F&G end state (computerised LIS covering the registration and tracking of rights, customary tenure included, as §3.6 requires), and move LADM and FELA's pathways into the anchor only as *e.g.*; stage 5 stays `no`.

**4. A published TADAT score is a reference, not the record.** The two TADAT rows mark A–D as the norm's rungs, which is right for a global-tier anchor, but the anchors read as if the assessor looks up the country's TADAT score. `maturity-assessment-norms.md` §7 and the rubric's own *never evidence* list forbid that. Add to the DPI chapter note: *the assessor applies TADAT's criteria for the named indicators to the base's own rows; a published TADAT assessment is a reference, cited in the qualifier where it disagrees.* The drafter's offer on wording is accepted in part: check each level against the Field Guide's scoring criteria and keep the paraphrase.

**5. `dpi.mis--tax` needs one rule for three areas.** TADAT scores indicators, not POAs, and POA1 is `dpi.registry--tax-register`'s. Name the indicators this row reads — POA4's use of electronic filing and POA5's use of electronic payment, by their Field Guide numbers — drop POA1, and add *the lower of the two scores decides the stage*, as the sovereignty indicator's lowest-part rule does.

**6. The two ID-use rows — the split is right; make it clean at stage 4.** `dpi.exchange--use-of-digital-id-in-other-systems` stage 4 lists *tax, elections* among its consumers, which are public registers and `dpi.id--use-by-other-systems`'s evidence. Replace the list with *services, public and private, consuming a verification or authentication service* and leave the registers to the other row. The drafter's narrowing note is then true of the anchors as written.

**Accepted as drafted**: the sovereignty overlap on `national-maintenance-of-id-and-credentials-systems` (both rows say so, and the sovereignty row's lowest-part rule governs the estate); `digital-id-from-birth` stage 5 citing the measure's figure without defining it; the weak `mis--justice` anchor.

When the six are in, CC re-runs the checker and cuts DPI (instruments and systems).

## DPI — second review 2026-09-23: accepted and cut

**All six items are in**, the checker reads the draft clean with no warnings, and the Governance chapter still reads as its cut. The two exchange rows now read links — one exchange in service at stage 3, exchanges on a shared identifier at stage 4 — so an EMIS or a social registry coming into service moves the MIS or registry row and not the exchange row as well. Cut by `maturity-rubric-cut.py --chapter DPI --kind instrument --kind system`: 34 indicators, 170 rows; the lookup holds 64 of 117, 229 interpolated rungs.

**Register aligned**: Cowork corrected `dpi.pay--revenue-collection`'s TADAT reference to P5-15; CC made `dpi.mis--tax`'s anchor P4-14 and P5-15 with the lower deciding, as the rubric now reads, and re-cut `maturity-norms.csv`.

## Infrastructure, Digitalisation and Technology — reviewed 2026-09-23: returned, three one-line items

**The checker is clean**: 19 indicators (14 systems, 5 instruments), 95 rows, no warnings; earlier cuts unchanged. Every heading matches the register's anchor and *fixes*. **Reviewing the three chapters as one is fine** — the checker's counts keep them apart. The shared `digital.rural` ladder, the composite cybersecurity row with the lower element deciding, the unbanded backbone length carried in the qualifier, and the Corpus-defined police row all interpolated are right as drafted. Three edits, then CC cuts all three chapters' instruments and systems.

**1. `infra.connect--internet-exchange-points` stages 3–4 key on the snapshot month.** *No growth in the window* (stage 3) and *published and growing* (stage 4) read growth over one month, which is noise for an IXP and would move the stage with each traffic report. Delete *no growth in the window* from stage 3, and make stage 4's clause *traffic or capacity published at two dates at least 12 months apart, showing growth*.

**2. `gov.policy--open-data-policy` stage 4 has the same fault, in the chapter already cut.** *Publication activity in the window on record* — CC missed it in the Governance review. Make it *in the 12 months to the as-at date*, as `open-discussion` now reads. CC re-cuts Governance with this chapter and has widened D2's look-back exception to cover both rows.

**3. `tech.innovate--technology-hubs` stage 5 — "connected to" its region's park names no evidence.** Make it *the country hosting its region's technology park, or a national park linked to it by an agreement on record*.

**The draft's question on `rural-primary-schools` stage 4: keep `no`.** `interpolated` asks who states the rung, and the DES states the 2027 figures; that they are national and the row reads rural schools changes what the assessor counts, not who set the bar. The row's note should say the figure is the DES's national one, and the qualifier carries the rural share where the base holds it.

## Infrastructure, Digitalisation and Technology — second review 2026-09-23: accepted and cut

**All three edits are in**, and the rural-schools note says the figure is the DES's national one. The checker is clean with no warnings. The drift check flagged exactly one cut row as changed — `gov.policy--open-data-policy` stage 4, the intended edit — so Governance was re-cut with it. Cut: ICT Infrastructure 7, Digitalisation 6, Technology 6 (instruments and systems). The lookup holds 83 of 117; 301 interpolated rungs.

## Capacity, Inclusion, Data and Geopolitics — reviewed 2026-09-23: returned, two one-line items

**The checker is clean**: 12 indicators, 60 rows, no warnings; earlier cuts unchanged. With `--complete` the only failures are the 22 measures, which are C3 — so with this leg every assessed instrument and system has a rubric. Headings match the register. The consultation split with the cut `non-governmental-contribution` row, the open-data pair, the census row's round-neutral stage 5, and AMCOMET's figures at stage 5 only are right as drafted. **The sovereignty row is accepted as transcribed**, 12-month look-back and DPF rungs included, and the checker's earlier warning on it is gone.

**1. `include.access--citizen-feedback-portals` stage 5 rests on a reference.** *Reaching the e-decision-making level of the E-Participation Index* is the register's reference column, and the rung is marked `no`; by the first review's rule a reference cannot be the norm's rung. Drop the EPI clause (the qualifier can cite the EPI level where it disagrees) and let stage 5 stand on the Charter and Declaration: feedback reaching representatives, outcomes published proactively, and the channel covering local government.

**2. `include.access--inclusion-of-persons-with-disabilities` stage 3's second limb is not evidence of the stage.** *Or the state's report to the treaty body naming the gaps* documents what is missing, not an instrument in force; as written, a country with no law reaches stage 3 by reporting that it has none. Delete the limb; such a report is good evidence for stage 1 or 2 and the qualifier.

**Decided by CC, no edit needed from Cowork**:

- **D2's look-back exception is general.** Four rows now key on *the 12 months to the as-at date* (open discussion, open data stage 4, citizen participation stages 2–3, sovereignty stages 2–3). The D2 task names the rule, not the rows: any anchor with that phrase may move when an event leaves the period.
- **The sovereignty rubric's source is this file.** At the cut, CC points `indicator-digital-sovereignty.md` §5 here and keeps its table as the design record, so there is one source for the lookup.

When the two are in, CC cuts all four chapters' instruments and systems and C2's drafting of non-measures is complete; the measures follow in C3.

## Capacity, Inclusion, Data and Geopolitics — second review 2026-09-23: accepted and cut

**Both edits are in** — feedback-portal stage 5 on the Charter and Declaration with the EPI left to the qualifier, and the disabilities treaty-report limb gone — and the checker is clean. Cut: Capacity 1, Inclusion 4, Data 6, Geopolitics 1. **The lookup holds all 95 assessed instruments and systems**, 347 interpolated rungs; `--complete` now fails on exactly the 22 measures, which are C3. `indicator-digital-sovereignty.md` §5 now points here as the source.

## Measures (C3) — reviewed 2026-09-24: returned, five items

**The checker is clean on the draft**: 117 indicators, 585 rows, 429 interpolated rungs, 3 partly, no warnings. The preamble is right: precedence, strict definitions, the three band methods, and the top-only quintile rule. The DPI dataset is kept to a lead. The compile columns the two finance rows name all exist with those values (`beneficiary_type` Public Sector, Private Sector, Fund, PPP; `status` Active, Approved, Closed, Pipeline, Unknown; `instrument` MoU, Unknown). **Accepted as drafted**: the four norm figures applied to a neighbouring population, on the rural-schools ruling; energy and water for data centres kept as a measure (*No evidence* almost everywhere is the true reading, and a kind change would reopen the frame for no gain); registration at 99.9 % of all people; `tech.industry` on quintiles until the register names a figure; the two absorption readings.

**1. A machine-readable line per specification.** The measures lookup is cut by script, like the others, so each specification gains two list items in this form:
`- **Method**: target · higher` (or `quintiles · lower`, `fixed · higher`)
`- **Cuts**: 27 · 53 · 80 · 95` — the lower bound of stages 2, 3, 4 and 5 for *higher*, the upper bound for *lower*, in the value's unit. Leave out the stage-5 number where stage 5 is a condition only. A quintile row lists its provisional cuts (item 2) and says `provisional`.

**2. Provisional cuts on every quintile row, not only the thin ones.** A stage has to be computable from the figure on the day of the baseline, whatever the count turns out to be. And a row that gains cuts later has changed its rubric. So `mobile-penetration`, `grid-reliability`, `tech.industry`, `graduates-entering-dt-ecosystem`, `gender-equity` and `mobilisation-of-non-state-finance` each state absolute provisional cuts for stages 2–4, replaced by the quintiles once fifteen countries hold a figure.

**3. `local-data-centre-capacity-all-providers`: the value is what is banded.** The rungs are Tiers, but the value is MW per million, so a country with a Tier III facility on record and no published MW would read *No evidence*. Make the value the count of Tier III-or-higher facilities in service (unit *facilities*), with the Tier I–II case as stage 2, and move MW per million to the stage-5 condition and the qualifier.

**4. `mobilisation-of-non-state-finance`: the window at year precision.** `start_year` is a year, so *the 36 months to the as-at date* has no exact reading. Make it *commitments whose `start_year` is the as-at year or either of the two before, summed and divided by three*. Also say, in both finance rows, that commitments to NGO, multilateral, research and multi-stakeholder beneficiaries count in neither row. Otherwise a reader takes it for an omission.

**5. The value forms `value_source` may take.** Measures are assessed for every country, from the reference where the base holds nothing (item on CC's side, below). So the preamble should say `value_source` is one of:
- a `raw/` slug, for a cited primary;
- `budgets/{ISO3}/{FY}.csv`;
- `outputs/non-state-finance/{ISO3}-nonstate.csv`;
- `ref:{dataset}@{release date}`.

The date is what makes a new figure a dated cause under the stability rule.

**Bill ruled 2026-09-24: keep the on-budget share** (`maturity-assessment.md` §2). CC's recommendation, for the record: keep the partner-financing row as redefined — the on-budget share. It is a different fact from the sustainability share, not the same one twice. It is also the standard aid-effectiveness measure, and its coverage grows with the budget-extract queue. Retiring it instead changes the published counts to 116 for a row that costs nothing to carry as *No evidence*. The 85 % line is being checked against the Paris text in the vintage pass.

**On CC's side, recorded here so the leg reads whole.** The band is computed by script from the value and the cuts; it is a ceiling the drafter's stage may not exceed, and a compound anchor or the secondary execution test may hold the stage below it. Stage 5 needs the band's top and its condition. Quintile cuts are computed once, from the baseline's figures across all units, and written into the lookup with their year. Measures are due for every unit regardless of mapping, and *No evidence* for a measure means no figure of the definition in the base or the reference. The reference figures are pulled into Corpus as data (task C5, new). The vintages are recorded below when the check returns.

### Measures — the reference vintages, and three more items (2026-09-24)

**Checked 2026-09-24** (a web research pass, official APIs where the portals refuse scripts; coverage is African countries with a value in the latest five years):

| reference | route | latest release | data year | African coverage |
|---|---|---|---|---|
| ITU mobile-phone ownership (SDG 5.b.1, **ages 10+**) | UN SDG API `IT_MOB_OWN` | SDG DB 2026.Q2 | 2024 | 51, mostly ITU estimates |
| Internet use (SDG 17.8.1) | WDI `IT.NET.USER.ZS` | 13 Jul 2026 | 2024 | 52 |
| ICT skills (SDG 4.4.1) | UN SDG API `SE_ADT_ACTS` | 2026.Q2 | 2024 | 10 |
| Internet use by sex / by area | SDG API `IT_USE_ii99`; Data360 `ITU_DH` | 2026.Q2 / Apr 2026 | 2024 | 10 / 9 |
| International bandwidth per user | Data360 `INT_BAND_PER_USR` | 3 Apr 2026 | 2023 | 46 |
| ITU price baskets | ITU workbook 2008–2025 | 10 Dec 2025 | 2025 | 51; **5 GB is the official data basket from 2025**, 2 GB ran 2021–24 |
| Rural electricity access | WDI `EG.ELC.ACCS.RU.ZS` | 13 Jul 2026 | 2024 | 52 |
| Outages in a typical month | WDI `IC.ELC.OUTG` (Enterprise Surveys) | 13 Jul 2026 | 2025 | about 49 |
| Secondary schools with internet (4.a.1) | UIS `SCHBSP.2T3.WINTERN` | Feb 2026 | 2025 | 28 |
| STEM share of tertiary graduates | UIS `FOSGP.5T8.F500600700` | Feb 2026 | 2025 | 20 |
| Employment in ISIC J | ILOSTAT `EMP_TEMP_SEX_ECO_NB_A` | live | 2025 | 36 |
| Value added in ISIC J | UN Main Aggregates / UNCTADstat | Jan 2026 | 2024 | **0: J is not separated** |
| GDP, current USD | WDI `NY.GDP.MKTP.CD` | 13 Jul 2026 | 2025 | 52 |
| Population | UN WPP 2024 | Jul 2024 | est. to 2023 | 54 |
| ID ownership, adults 15+ | ID4D 2025 (Findex) | Mar 2026 | 2024 | 37 (qualifier only, as drafted) |

**The 85 % line is verified**: Paris Declaration indicator 3, "with at least 85% reported on budget" (OECD/LEGAL/5017), carried word for word as GPEDC's 2012 indicator 6. The 2022 GPEDC framework keeps an on-budget indicator with no number. So the reference should read *Paris Declaration indicator 3 (2005), as carried by GPEDC 2012 indicator 6*.

**6. `mobile-penetration`: the definition that exists is 10+.** ITU's series (SDG 5.b.1) counts individuals aged 10 and over. Under the strict-definition rule, a 15+ row reads *No evidence* in the 51 countries ITU covers and stands only where a national survey happens to cut at 15. Make the value ITU's definition (10+). The UMC's 15+ goes to the qualifier where a survey gives it.

**7. `mobile-affordability`: the 5 GB basket.** ITU replaced the 2 GB data-only basket with a 5 GB one from 2025. Price per GB from the current official basket keeps the row on the series ITU maintains, and the DTS line (US$10 per GB) is unchanged. A 2 GB figure from 2021–24 is a different basket and goes in the qualifier.

**8. `tech.industry`: no reference exists for ISIC J value added.** The UN aggregates fold J into *other activities*, so the row stands only where a statistics office publishes section J, and it will not reach fifteen countries. Either keep it, with provisional cuts, as *No evidence* nearly everywhere, or re-point it at a figure that exists. **CC's recommendation is the second**: ICT service exports as a share of service exports (WDI `BX.GSR.CCIS.ZS`, from UNCTAD and the IMF), which reads production capacity in the part of the sector that trades and covers most of the continent. The DTS manufacturing condition stays at stage 5. Cowork drafts whichever reads better against the norm.

**Accepted as they fall**: SDG 4.4.1 (10 countries), gender (10) and the urban–rural ratio (9) will read *No evidence* in most of the continent. That is the truthful position and what the base's own survey primaries can improve on. Item 2's provisional cuts cover the gender quintiles.

## Measures (C3) — second review 2026-09-24: accepted and cut; items 6–8 still owed

**Items 1–5 are in, and the extension of item 3 is right.** Both data-centre rows now read Corpus's own dataset, which bands 31 countries where MW would have banded almost none. The checker is clean. Cut by `maturity-rubric-cut.py --kind measure`: 22 indicators, 110 rows. **The rubric lookup holds all 117 assessed indicators**, and `lint-maturity.py` check R passes. The same cut writes `lookups/maturity-measures.csv` from the `Method` and `Cuts` lines (22 rows). The cutter refuses a method or direction outside the vocabulary, cuts out of order, a count other than three or four, and a quintile row without provisional cuts. `--check` holds the measures lookup to the draft as it does the rubric.

**The guard, run on real figures.** `reference/measures.csv` (C5) now holds the figures the provisional cuts were set without. Banded as at the baseline, **no row puts more than half its countries on one stage**:
- mobile ownership: 8 · 13 · 16 · 12 · 3 over 52 countries;
- grid reliability: 9 · 12 · 15 · 15 over 51;
- ICT employment: 16 · 14 · 6 · 10 over 46;
- gender gap: 9 · 3 · 7 · 4 · 3 over 26.

Each of these four holds fifteen or more figures, so it is cut to real quintiles at the baseline, and its provisional cuts will only ever apply where the count falls short.

**Items 6–8 were appended after this revision began, and are still owed**: `mobile-penetration` on ITU's 10+ definition, `mobile-affordability` on the 5 GB basket, and `tech.industry` either kept on ISIC J or re-pointed (CC recommends ICT service exports). They are cut as drafted for now, so nothing waits on them. They are re-cut when they land, before the baseline, while re-cutting still costs nothing. Until item 6 lands, `mobile-penetration` takes no reference figure: the fetched series is 10+ and the row says 15+.

## Measures (C3) — items 6–8 in and re-cut 2026-09-24; one more item from the guard

**Items 6–8 are in and re-cut.** `tech.industry` bands ICT service exports as a share of GDP, not of service exports, because the service-exports share runs high wherever other service trade is small; that is better than CC's suggestion. The measures lookup and `--check` are clean.

**The reference now says what kind of figure it is** *(CC, on Bill's remark that he does not have much respect for ITU numbers)*. Every figure in `reference/measures.csv` carries a `nature`: `survey`, `country`, `tariffs`, `official` or `estimate`. The SDG database marks ITU's own models as estimates figure by figure, so internet use now comes through it rather than WDI, which does not mark them. **A country's own figure from the last five years outranks a newer estimate**, and a stage resting on an estimate says *on the compiler's modelled estimate* in its qualifier. As at the baseline, **internet use rests on an ITU estimate in 41 of 54 countries and mobile ownership in 39 of 52**. Those are the rows where a survey primary in the base changes most, and the packet tells the drafter so.

**9. `mobile-affordability`: the DTS line no longer separates anyone.** Banded on the 2025 5 GB basket, **52 of 53 countries are at US$10 per GB or less**: prices have fallen well past a line set in 2020. The guard trips. The basket as a share of monthly GNI per capita does separate countries (51 countries: 12 at or below 2 %, 20 at or below 4 %, 30 at or below 6 %, 42 at or below 10 %; quintiles 1.6 · 4.1 · 6.1 · 9.4). **CC's recommendation**: band on the share of GNI, target T = 2 (the Broadband Commission's line, carried by the ITU's UMC targets), lower-is-better thirds as the preamble sets them (stage 3 at or below 4, stage 2 at or below 6, stage 1 above). That puts 12 · 8 · 10 · 21 across stages 4 to 1. The DTS's 1 US cent per MB becomes a condition every country already meets, kept in the anchor as the continental floor. Stage 5 is Cowork's to set; 1 % or less holds 3 countries. The value is then the GNI share and the US$ per GB goes to the qualifier. The reference fetch follows whichever the row says.

**10. `local-data-centre-capacity-all-providers`: drop "stage 4 is also met by one Tier IV facility".** The value counts Tier III-or-higher facilities, so a lone Tier IV counts 1 and bands at 3. The clause and the cuts disagree, and only one country, Seychelles, falls between them. The clause should go rather than the band: stage 4 asks for more than one facility because two give redundancy, and one facility of any tier is a single point of failure. Until the draft says so, the band holds Seychelles at 3. The four Corpus-computed measures are in `scripts/maturity_compile.py` (the sustainability share, 5 countries; non-state mobilisation, 54, of which 31 are zero; data centres, 54 and 41). The partner on-budget share stands on a drafter's verdict until a country-year is matched.

**A reference figure's age** *(CC, 2026-09-24, from the LBY draft)*. The reference picker took the latest year it held, which for Libya's rural electrification was WDI's 0.8 % from 2012. Fifty-six reference figures in use were more than six years old, back to Findex 2014 and UIS 2015. **A reference figure more than ten years before the as-at is not a figure of record, and the measure is *No evidence*** (`maturity-assess.py` `MAX_REFERENCE_AGE`). A drafter's cited primary is not held to the limit; it carries its own year, and the year prints beside the stage.
