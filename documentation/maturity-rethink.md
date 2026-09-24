---
type: design-note
title: maturity-rethink.md — the assessment after its first run, and the case for building it from studies
date: 2026-09-24
status: discussion — Bill is sleeping on it; nothing below is decided except where marked (Bill). §1–6 CC; §7 Cowork's response, 2026-09-24
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

## 7. Cowork's response (2026-09-24)

*(Added by Cowork at Bill's request. It agrees with §3's diagnosis and with the studies model, and the points below either extend §5's proposals or qualify them. The counts are from Bill's review sheet, `outputs/maturity/indicators/review.md`, as rendered.)*

**The diagnosis is right, including the part that is Cowork's.** The wall between narrative and assessment is written into `maturity-assessment.md` §2 as a ruling — *two exercises, side by side, neither derived from the other* — and into §9, and Cowork drafted both. That ruling was meant to stop the status prose being scored; what it did was keep the assessor out of the material that could have told it what a system is. Any rebuild should reverse it explicitly rather than work around it.

**1. "Instruments are publishable" holds for about 18 of the 44, not all.** On the rendered August figures:

- **No instrument reached stage 5 in any country.** The stage-5 test, *the national instrument says it aligns with the AU instrument, or the AU or a REC records the country as compliant*, is too strict to discriminate. Very few national texts state alignment, and neither the AU nor the RECs publish compliance lists. A rung nobody can reach is a four-stage scale printed as five. Before publication, stage 5 wants either a test the evidence can meet, such as ratification where a treaty exists or a domestic instrument that transposes a named continental one, or to be dropped until a study earns it.
- **Thirteen instruments leave 20 or more of 54 countries unplaced.** They include regional legal harmonisation (49), adoption of international standards (39), cross-border data transfers (33) and national maintenance of ID systems (28). Those have the systems chapter's problem: the question is not definite enough for a drafter to answer from the rows. Eighteen instruments leave 10 or fewer unplaced, and they are the chapter that could publish. The other 26 either get tightened or wait for the study that covers them.
- **A reliability check before anything publishes.** Nobody has yet measured whether two drafters reading the same packet give the same stage. About thirty calls were corrected in vetting, which says the variance is real. Re-draft a random sample of perhaps 100 instrument cells blind and count agreement. A chapter where independent drafters disagree on a large share of cells is not ready, however clean its rubric reads. This costs a morning and is the only evidence we would have that a published stage means the same thing in Benin as in Kenya.

**2. Publish the cross-country pages now, without stages.** §5 withdraws the systems' stages but says nothing about the pages they sit on. Those pages are the best thing the run produced. The education page, for example, puts 54 countries' evidence on one question side by side, each with its source, under a stated continental norm. Nothing else in Corpus gives that view, and it is the perspective Bill finds missing from the progress report. With the stage column removed, each page is a continental evidence review: publishable now, plain about what it is, and the raw material for step 1 of whichever study takes the domain. The one care needed is that countries' own labels (*EMIS*) print as the country's label, attributed, and not as Corpus's classification.

**3. Measures: agree with dossiers, one per measure across the continent.** A dossier per measure per country is 22 × 54 pieces of drafting and will not be maintained. One page per measure, with a row per country listing each figure held (the regulator says, the operator says, the survey found, the compiler models) and why they differ, uses the same rendering machinery and keeps the comparison. Two rules keep it Corpus's rather than ITU's:

- a compiler's modelled estimate never stands alone in a row, and prints only beside at least one figure from the country itself or as *compiler's estimate only*;
- a measure is published only where the base holds such figures for enough countries to say something. The rest are collection targets for the sweeps, as ID registration's 46 *No evidence* rows already are.

**4. The frame must be allowed to change as studies land.** CC's case for the common frame (§3, point 1) is right, and it carries a risk in the other direction. The 117 questions were set before any study. A registry study may well conclude that *population register* and *digital ID system* are one question in some countries and two in others, or that the EMIS row must split from a census row. `adding-an-indicator.md` already provides for this: ids are retired and never reused, and history is kept. The studies model should say plainly that a study may redraw its domain's rows, not only fill in their rungs.

**5. Registries as the first study, scoped to include identity, and piloted.** The definitional knot the systems chapter hit runs through registries and identity together. It covers the population register against the ID database, the civil register against digital ID from birth, and the interoperability row between them, which is six rows sharing one typology. A registries study that stopped at the registry rows would leave the knot half tied. It should also pilot the method on six to eight countries with deep status reports before running all 54. That tests steps 1–3 cheaply, and it matches how the budget extract was proved.

**6. Instrument stages in the status report: test it by sub-section, not as one stage.** A status sub-section is a subject; `gov.legislate` holds nine instruments. What fits is a line of the subject's instrument stages under its heading, not a single stage, with the prose free to explain any of them. Run the soft status/assessment agreement check (`maturity-assessment.md` §9) on the test country first. If the prose and the stages disagree often, the test has found something worth knowing before anything prints.

**7. The progress report can take perspective without a score.** Keep it, as §5 says. Its rows could link to the indicator's cross-country page and carry the norm in a phrase, so that a small step reads against where the continent stands and what it committed to. That is the perspective Bill asks for, and it needs neither the stages nor a rewrite of the report.

**What stands regardless.** The norms register (`maturity-assessment-norms.md`) is worth keeping whatever is decided: continental anchoring is useful to every study's step 2 and to the pages in point 2. The frame changes that landed on the way — the sovereignty and sustainability indicators and the status-outline sub-sections — stand on their own merits.

## 8. Next Steps (Bill 2026-09-24)

Still thinking aloud.

- This week I have 'announced' on LinkedIn that the Data Centres dataset is live - this has received a very positive response.
- On **Monday 2026-09-28** I will announce that the non-state finance dataset is live.
- As OSINT has been given an extra week's worth of tokens we will finish budget data collection this week. By the end of next week we should have all country budget reports published. On **Monday 2026-10-05** I will announce that country budget datasets are live.
- That week we will work on a continental budget dataset and on the first draft of a combined non-state-finance-budget country table. These go live on **Monday 2026-10-12**
- We then start working on publishing weekly maturity studies starting **Monday 2026-10-19**. My preferred first candidates are: registries; sectoral MIS; sub-national DT/digitalisation