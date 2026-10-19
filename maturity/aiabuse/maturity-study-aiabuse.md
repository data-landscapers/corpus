---
type: task
reader: cc
title: maturity-study-aiabuse.md — rules and an authority against harms from AI, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: aiabuse

*(Commissioned by Bill on 2026-10-16 as `tech.ai--control-of-ai-abuse`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with aigovernment, aisectoral, aisystems, aiabuse, techhubs and startups: the chapter Technology.)*

## 1. What is assessed

**Rules and an authority against harms from AI**: a rule in force or a body with a mandate that addresses a harm from AI, such as deepfakes, automated decisions, manipulation in elections or bias. What controls a harm from AI counts, whatever it is called.

The study redraws `tech.ai--control-of-ai-abuse`, which as at 2026-08-31 puts 11 countries at stage 3, 23 at 2, five at 1 and 15 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| AI harms | Control of AI abuse: AI harms | `tech.ai--control-of-ai-abuse-ai-harms` |

Anything else the evidence names is `other`, noted and never staged: an AI strategy with no rule, a workshop, guideline or ethics principle with no legal effect, a general data-protection or cybercrime law unless the source says it applies to AI or deepfakes, a company's own policy.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a rule or authority on AI harms being drafted? | A source from the last three years says a bill, draft regulation or draft guideline addressing a harm from AI is published, or a draft provides for an authority over AI |
| 2 | Is a rule on AI harms in force? | A source from the last three years says a law, decree, regulation or binding directive in force addresses a harm from AI, such as deepfakes, automated decisions or AI in elections |
| 3 | Is an authority designated? | A source from the last three years says a body is designated by law or decree with a mandate over AI harms or AI systems |
| 4 | Has it been enforced? | A source from the last three years gives a dated enforcement, audit, takedown, penalty or redress decision about a harm from AI, under a rule or by that body |

## 3. The ladders

**AI harms**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no authority, rule or mechanism addresses harms from AI. |
| 2 Draft | Yes to 1 |
| 3 Rule in force | Yes to 2 |
| 4 Authority | Yes to 3 |
| 5 Enforced | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `rule` (`inforce`, `draft`, `none`) for stage 1 and questions 1 and 2, `authority` (`designated`) for 3 and `enforced` (`applied`) for 4.

## 4. The norm

The Continental AI Strategy asks for risk-based regulation, an independent oversight body with enforcement and redress, technical safety standards and a part in regional oversight. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **624 story readings about the subject**, published since October 2023, in at most 20 stories a country: 552 in the batch's shared calls (147 calls over 732 stories), read once for every study that lists them, and 72 in 48 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 7,423 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**14 million** for this study; **85 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 50 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 6 at 4, 8 at 3, 8 at 2, 7 at 1; unplaced 1, no evidence 24. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: a secretary of state appointed to promote AI read as a body over AI (Equatorial Guinea, now 2); a cabinet approval to create an AI agency read as a body designated (Rwanda, now no evidence).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
