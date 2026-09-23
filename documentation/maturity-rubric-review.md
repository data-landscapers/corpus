---
type: review
title: maturity-rubric-review.md — CC's review of each rubric chapter before it is cut (task C2)
last_reviewed: 2026-09-23
status: Governance and the Finance instrument reviewed 2026-09-23 — returned to Cowork with the changes below; nothing cut yet
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
