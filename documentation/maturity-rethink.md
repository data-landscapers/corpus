---
type: design-note
title: maturity-rethink.md — the assessment after its first run, and the case for building it from studies
date: 2026-09-24
status: discussion — Bill is sleeping on it; nothing below is decided except where marked (Bill)
supersedes: nothing yet; bears on maturity-assessment.md and maturity-assessment-tasks.md
---

# The maturity assessment: rethink after the first run

*(Written by CC on 2026-09-24 at Bill's request, from the conversation that followed his first read of the rendered assessment. It records what was built, what Bill found, CC's response, and the studies model the two converged on. Nothing in `maturity-assessment.md` is changed by this note until Bill decides.)*

## 1. What was built

Phases A to E1 of `maturity-assessment-tasks.md` ran on 2026-09-24:

- **The rubric.** 117 indicators, five stages each: 44 instruments, 51 systems and 22 measures.
- **The data.**
  - The reference data for the measures was pulled from ITU, WDI, UIS, ILOSTAT and Data360, with each figure labelled survey or estimate.
  - Four measures are computed from Corpus's own compiles.
- **Two retrospective snapshots, July and August 2026, for all 54 countries.**
  - The verdicts were drafted per country by subagents from packets of ledger rows. Every file was vetted, and about thirty calls were corrected.
  - As at August, the 6,318 cells stand at: 283 at stage 1, 1,950 at 2, 1,900 at 3, 215 at 4, 10 at 5, 1,323 unplaced, and the rest with no evidence.
- **A first rendering.**
  - One page per indicator across the 54 countries, and one document per country.
  - Evidence appears as named ledger rows linked to their sources, or as figures with their source in words.
  - The files are `outputs/maturity/indicators/` and `outputs/reports/{ISO3}/{ISO3}-maturity.md`.

The machinery holds, and it does not depend on the rubric:

- the as-at rule and the stability rule;
- write-once editions and the rebuildable history;
- evidence rendered with its sources;
- reference figures labelled survey or estimate, a survey outranking a newer estimate, and figures more than ten years old or jumping more than 30 points dropped.

## 2. What Bill found (Bill, 2026-09-24)

- **Instruments are publishable** with a bit of tweaking.
- **Measures, bar one (ID registration), are unusable.** They are too prescriptive, and they miss the more complex evidence Corpus collects every day.
- **Systems lack definition.** An EMIS is not an annual school census, yet many countries describe their census as an EMIS. The rubric's categories do not survive contact with how countries describe their own systems.
- **The biggest problem: the assessment almost totally ignores the rich and deep narrative built across Corpus as a whole.**
- **The progress report captures a real quality:** progress consists of small steps. But it lacks perspective.

Bill's direction: publish, over time, a series of in-depth studies (the maturity of registries, for example). Together they would build a maturity assessment in the longer term.

## 3. CC's response

**Agreed on the diagnosis.**

- **Measures.** A measure had to be a single number of a fixed definition. The strict rules added during the run (a different base is not the value, a count of rows held is not a figure) then removed almost everything Corpus actually holds: regulator claims, operator figures, budget lines, and sources that disagree. What survived is mostly ITU and WDI figures with a band on top. For 21 of 22 measures, the assessment republishes global datasets under a Corpus heading, the reverse of what the design said Corpus offers (`maturity-assessment.md` §4: *a figure with its date, its source and who says so*).
- **Systems.** The definitional problem accounts for much of the 22 % of cells that came out unplaced. The rubric's anchors assume clean categories; the sources use loose ones; each drafter read them differently.
- **Narrative.** This was a design fault, not an execution fault. The assessor read ledger rows (a name, a status, a one-line position) and never the status reports, the wiki or the monthly bulletins. The stages sit beside Corpus's deepest material without drawing on it.

**Disagreed in two places.**

1. **Studies alone lose comparability.** A series of deep studies with no common frame cannot be compared across countries or tracked over time. That comparison was the one thing the assessment offered that no one else does. The answer is to join the two: each study works out one domain's definitions and rungs properly, and the domain enters the assessment only when its study has earned it. The assessment grows chapter by chapter.
2. **Measures should become dossiers, not stages.** The design's strongest idea was the figure together with who says so. Published as such (the regulator says X, ITU models Y, a 2022 survey found Z, and why they differ), a measure uses exactly the complex, contested evidence Corpus gathers every day, and needs no rubric.

**A further suggestion.** The instrument stages could give the status report the perspective the progress report lacks: a stage printed in each status sub-section, with the narrative doing the explaining. That joins narrative and assessment rather than keeping them apart.

## 4. The studies model

**Bill's sequence for a study:**

1. Review the existing evidence from all countries.
2. Compare it with norms, including a discussion of whether the norms suit.
3. Develop a methodology.
4. Set a baseline for ongoing assessment.
5. Add to the overall assessment.

**CC's three refinements:**

- **Step 1 settles what the thing is before anything is compared.** The review produces a typology: what counts as a registry, an EMIS or a census, and how countries' own labels map onto it. Without it, steps 2–4 inherit the confusion that broke the systems chapter.
- **Step 1 reads the narrative, not only the ledger.** The status reports, the wiki and the bulletins hold the depth the first assessment ignored. Starting each study there is what joins narrative and assessment.
- **Step 4 reuses the machinery unchanged.** The study's methodology becomes its rubric, and its baseline runs through `maturity-assess.py` with evidence rendered and editions written once. Only the definitions and the rungs are new each time.

**Step 2 matters more than it looks.** The measures took their norms on trust: ITU's 2 % of GNI line, the African Union's US$10 per GB. The data then showed they did not fit. The DTS price line puts 52 of 53 countries at the top band on 2025 prices. `maturity-assessment-norms.md` gives each study a starting point for the discussion.

**Sequencing, as proposed.** The instruments could stand as the first chapter now, since they have in effect been through steps 1–4. Registries would make a good first study: well documented, rich in DPI data, and hard enough on definitions to test the method.

## 5. Proposed, not decided

Waiting for Bill:

- **Instruments.** Publish them as the first chapter, after tweaking, or hold them for the first study's framing.
- **Measures.** Drop their stages. Publish as figure dossiers, or not at all for now. ID registration is the one Bill would keep as a measure.
- **Systems.** Withdraw their stages. They return domain by domain, through studies.
- **The first study.** Registries, or another domain.
- **The progress report.** Keep it. Do not retire it (task G1). Its small-steps quality is what Bill values.
- **The live snapshot of 2026-10-05.** Skip it, and pause tasks E2 and E3. Nothing has been published, so a pause costs nothing.
- **A stage beside each status sub-section.** Worth testing.

## 6. What stands as it is

Everything built on 2026-09-24 is committed and is left as it stands until Bill decides:

- the rubric and measures lookups;
- the reference data;
- the July and August editions, the history and the rendered pages;
- the verdict files and `logs/maturity-d6-readlist.md`;
- Bill's review sheet, `outputs/maturity/indicators/review.md`.

The tasks file is not yet amended.
