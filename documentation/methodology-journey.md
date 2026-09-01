---
type: draft
title: The life of a document — draft for the methodology section
last_reviewed: 2026-08-31
status: draft; placement undecided
---

# The life of a document — draft

*(Working draft for the methodology section — `prep/workflow.md` → "methodology: trace history of 1 document from search to output". Placement undecided: a section of `content/methodology.md`, which needs no renderer change, or its own page at `/methodology/journey/`, which does. Every hop below was checked in the tree on 2026-08-31; the verification note at the foot says how, and* Before this is published *lists three things to settle first.)*

---

## The narrative

### One document

On the evening of 29 August 2026, a Somali news site reported that the Upper House of Somalia's Federal Parliament had given a cybersecurity bill its first reading.

The next day it was a linked claim in three Corpus documents: a line in Somalia's monthly update, a row in its progress report, and an entry in that day's bulletin. This is what happened in between.

### It is found, not received

Nothing arrives in Corpus without a search. The looking is done by a **sweep cycle** working one day of a rotation at a time. Some sweeps run every time: a fixed list of trade journals, and a search of the open web for the last 36 hours. The rest take turns — newspapers, academic journals and think tanks on one day; financiers and donors' own structured reporting on another; deep per-country and regional research on a third. (Budgets, expenditure and audits will be a fourth.)

The list sweeps work a **window**: what this domain published since the last run, with a day of overlap so a story indexed late is caught next time. The content sweeps ask what has appeared since they last ran, however long ago. Two kinds of empty result are expected and neither is chased: search indexes lag a day or two, and most publishers do not publish at weekends.

### Two ways of looking

Searching and fetching go through [Exa](https://exa.ai/), in two modes, depending on whether the target is a *place to look* or a *thing to find out*. (The donor-finance sweep is the exception: it reads IATI's datastore through its API.)

**Standard search**, where the target is known — a query scoped to one domain, bounded by the run's dates, in that source's own language, with a separate fetch call to retrieve the page. Its virtue is hard scope: such a query *cannot* return anything from off the list, which makes the list a boundary rather than a preference.

**Agent mode**, where the target is a topic — no query string but a written brief, from which the Agent composes and follows its own searches. This is what the open-web sweep runs on, and the per-country, regional and financier briefs. It finds what a query would not, because it can follow a lead. The Somalia report came in that way: Dawan Africa is on no list.

A brief cannot be fenced, so two rules are absolute. **Nothing the Agent writes is ever stored** — its output is a synthesis, exactly the second-hand material the base refuses, so its job ends at discovery. **And its dates are not evidence**: every publication date is re-established from the fetched page.

### It is screened, then stored

Before anything is fetched, the candidate's **origin** is screened — where it came from, not what it says. A domain that fabricates, rewrites without attribution or launders others' reporting under its own byline is on a drop list and is never collected. It has to be a separate test: a hostile origin produces items fluent and specific enough to publish straight onto a page.

What is fetched is the document's **own words, in full** — never an excerpt, a summary or a machine translation. That stored text is what makes every downstream claim checkable, and it is why the store is private. A sweep can only stage a candidate: it cannot write to the archive or touch a wiki page.

### It is admitted, or it is not

**Ingest** is the one door, and it runs once at the end of the cycle. Four dispositions: admitted to the archive; turned into a **contra