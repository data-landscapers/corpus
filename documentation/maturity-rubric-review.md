---
type: review
title: maturity-rubric-review.md — CC's review of each rubric chapter before it is cut (task C2)
last_reviewed: 2026-09-23
status: Governance and the Finance instrument accepted and cut 2026-09-23; DPI reviewed 2026-09-23 — returned with six items
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

