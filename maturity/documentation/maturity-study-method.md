---
type: procedure
reader: cc
title: maturity-study-method.md — how one indicator is studied, staged and written up, from a short list of questions and the news already held
last_reviewed: 2026-10-25
status: in use; Bill's rulings of 2026-10-06, 2026-10-10 and 2026-10-11. The simpler form below is his of 2026-10-11 and governs every study prepared after dataprotectionlaw
---

# A maturity study: one indicator, worked whole

*(Bill, 2026-10-06. The scale, the null and the as-at rule of `documentation/archived/maturity-assessment.md` §3 and §7 still hold.)*

## 0. What a study is

**One indicator, all 54 countries, prepared and run without stopping** *(Bill, 2026-10-11; the confirmation step removed 2026-10-16)*: Corpus writes the study file (§9), questions included, and runs straight on: read, stage, write, render, the soft-launch map (§4, §7, §8). **Bill is not asked to confirm the questions**; they are written plainly and small (§2) and reported at the end. Every doubt is settled conservatively and reported at the end.

**Most indicators are first studied in a batch**, cheaply, under `first-pass-batch.md`: "run maturity batch {ids}".

**What Bill reads is in plain words.** A question, a stage and a report line say what is true of a country, in words that need no knowledge of this file.

**A study touches its own row and no other.** Which indicators the frame holds is Bill's decision alone; a study never proposes adding, merging or retiring one.

**A study has a token ceiling, stated in its study file** *(Bill, 2026-10-11)*. Each fan-out runs as one workflow. The run checks `python scripts/study-tokens.py` after each, stops and reports at the ceiling, and puts the total in its log line.

**Where things live** *(Bill)*: anything generic in `maturity/documentation/`, a study's file and working files in `maturity/{id}/`, what it issues in `outputs/maturity/{id}/`.

## 1. What is assessed

**Say in one sentence what the thing is, by what it does and never by its form** *(Bill, 2026-10-11)*: what does the job counts, whatever it is called and whatever larger thing it sits in. Everything else the evidence names is `other`: noted in the long summary, never staged. A further class is added only where it changes a stage.

Output: `systems.csv`, one row per named thing per country.

## 2. The questions

**A study asks at most four yes or no questions, in order, each a step beyond the last.** Each is answered for a country with a date and a link, or not answered.

**A question is a fact a dated news story or official notice can state.** One that needs a law's text interpreted, or a judgement of quality, is not asked.

`study.json` restates the questions as aspects with closed values, which is what the scripts and the briefs read.

## 3. How a stage is defined

1. **Stage 1 needs a cited, dated statement that the thing is absent.**
2. **Each yes, in order, is one stage**: one yes is stage 2, four is stage 5. A study with fewer questions says which stages it cannot reach.
3. **A yes to a later question answers the earlier ones.** **Except a question of nationwide coverage** *(Bill, 2026-10-23)*: it is shown by its own evidence, listed in `study.json` → `"must_show"`; `"later_yes": false` switches the rule off for every question.
4. **A yes carries its year and a window**, three years unless the study says otherwise. Outside the window it is not a yes.
5. **Answers are as at the as-at date**: a later dated source that reverses a yes, reverses it.
6. **An unanswered question stops the count**; the short summary names it. A country with no answer at all is *No evidence*.
7. **The top stage is reachable**: its question is a published fact, never a statement of alignment with a norm.
8. **A statement of intent reaches stage 2 at most** *(Bill, 2026-10-25)*: a plan, an announcement or a promise answers a preparing rung, and stage 3 needs concrete evidence of action, such as a system built and in service, money spent or sites counted as delivering.
9. **The questions are fixed when the study file is written.** One that drafters read two ways is reworded during the run, the study file says so, and every country is restaged.

## 4. Reading

**Start from what is already paid for** *(Bill, 2026-10-11)*: the facts an earlier study holds on the subject and the frame's cells for the row, carried into `evidence.csv` with their sources and matched to the questions from their own text, no document opened.

**Then read only news that is about the subject and not yet read.** `scripts/study-select.py {id}` writes `maturity/{id}/evidence/{ISO3}/readlist.csv`; the rows to read are pass `about`: a document of the news tier that carries a study term in its title or three times in its body, and that no study has read.

- **A term names the subject, not its field.**
- **Step 1 reports one number: the `about` stories unread**, with the countries they cover. The size of the whole listing is not reported.
- **Instruments, reports and passing mentions are not read.** One is opened only where a carried fact cites it and a question turns on it.
- **A country whose carried facts answer every question is not read at all.**

**A drafter is a fresh call of five documents at most, planned by `scripts/study-calls.py`.** **A regional story is read once** *(Bill, 2026-10-14)*: one listed whole for two countries or more goes to a regional call, whose drafter answers for every country listed; `study-calls.py --fan` files the answers by country before the merge. Drafters work to `drafter-brief.md`, on Sonnet, read the document and not its ledger line, and write the facts `study-profile.py --merge` folds into `evidence.csv`, one row per stated fact. `study-profile.py` then writes `profile.csv`.

**The parent verifies files, not tallies**: slugs resolve in `raw/` and sampled facts match the body.

## 5. Search

**The nightly rebuild in `MATURITY-UPDATE.md` searches the web for all 54 countries on every question of the ladder, whatever is held** *(Bill, 2026-10-11 and 2026-10-19)*, and this section is how. A question nothing held answers is printed as *Not held*; the rebuild delivers with `study-stage.py ready --rebuild` and no note of its own.

One Exa brief per country, searchers on Sonnet to `searcher-brief.md`, `scripts/study-stage.py` to fetch and stage. Candidates go flat to `C:\corpus-osint-xfer\prepared\maturity-study-{id}\`, `READY` written last, under one `[ACT]` note titled *Maturity study {id}: evidence to ingest* with `Affects: outputs/maturity/{id}/`. `python scripts/lint-staged-queue.py {folder}` passes before the note. Records go in `maturity/{id}/search/`; candidate bodies are never committed.

**A found document reaches the study only through ingest** *(Bill)*.

## 6. After a search

**What ingest admits arrives through `MATURITY-UPDATE.md` stage 4c**, like any other document. `scripts/study-returned.py {id}` checks `staged.csv` against the mirror's URL indexes once the note has closed, and the spent handover is deleted in the same commit.

## 7. Stage

1. **Fix the as-at**: the last day of the month before the run opens.
2. **Stage from the answers**, §3: counting, so `scripts/study-ladder-{id}.py` does it and writes each `stage.json`; `stage_sources` names the `row_id`s that set it. **The parent first reads every fact that would set the top two stages**, and records what it removes or revalues in `corrections.csv`.
3. **Check that two drafters agree.** A second drafter, on Opus, restages 20 cells, drawn by `study-profile.py --draw`, blind from `evidence.csv`. Below 16 in agreement, the question that split them is reworded and every country restaged.

## 8. Write

**Short summary: one plain sentence, 25 words at most, no link** *(Bill, 2026-10-09)*: what happens in the country, with its year; `writer-brief.md` holds the wording.

**Long summary: one paragraph per question, in order, each opening with its name in bold; 120 to 250 words.** A link on every claim, and two closing lines: ***Noted, not assessed*** and ***Not held***. `writer-brief.md` holds the rest.

Files, in `outputs/maturity/{id}/`:

| File | Holds |
|---|---|
| `assessment.csv` | One row per country per sub-indicator; `lint-study.py` holds the columns |
| `{ISO3}.md` | The long summaries |
| `{indicator_id}.md` | Cross-country page: norm, ladder, then each country |

`scripts/study-render.py` writes the pages from the CSVs. `scripts/lint-study.py` holds them.

**The run ends on the soft-launch map and methodology page** *(Bill; `output-spec-v2.md`)*: write five `criteria` and `criteria_of` into `study.json`, run `scripts/maturity-site.py`, commit and push.

**The frame is not touched until Bill accepts the study.** On acceptance, the study's row is redrawn under `adding-an-indicator.md` §2 and §10, and the study's CSV is the baseline edition.

## 9. The study file

`maturity/{id}/maturity-study-{id}.md` holds, in this order and in plain words: what is assessed (§1); the questions and the stage each gives (§2, §3); what the run reads, as one number; the token ceiling; the tasks. It names the frame row it redraws. `study.json` beside it restates the questions as data for the scripts.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
