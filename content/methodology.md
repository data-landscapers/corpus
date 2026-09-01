## Introduction

Corpus is a website containing a range of reports and datasets classifying, summarising and indexing public documents covering digital transformation in Africa. It is updated daily. Behind the website is a private repository containing the text of these documents - it is private for copyright reasons. 

The aim of Corpus is to provide a fast-track information service for researchers and analysts working on the digital transformation of Africa, including digital public infrastructures and data governance.

## Scope

- **Geographical**
  All documents are tagged with one or more country or region iso-3 codes. The list is available [here](lookups/#countries).
- **Topics**
  Corpus has developed its own [two-level taxonomy](lookups/#topics) of topics. All documents are tagged with at least one level 2 topic.
- **Finance**
  Corpus is attempting to produce a single integrated view of all financing of digital transformation. The first part of this, non-state financing, is live. It includes all public and private investments sourced from the International Aid Transparency Initiative, investor portals and news articles. The second part, national budgeting, spend and auditing is still under development.
- **Time**
  Corpus' primary focus is current news with over 2,000 documents now being added each month. Older documents are collected to provide baselines to status and progress reports.

## Infrastructure

- **Architecture**
  Corpus is built by two networked machines.
	- The first is responsible for data collection and classification. Its repository is private. 
	- The second is responsible for summarising content and keeping reports and datasets up to date. Its repository is available at https://github.com/data-landscapers/corpus. 
- **Technology**
	  - Search and fetch is managed by [Exa](https://exa.ai/)
	  - Claude Code is responsible for running all other processes. It is run on Opus, with routine bulk work delegated to Sonnet.
	  - All process instructions are written in markdown and managed by Obsidian
## Data collection

The data collection machine runs a nightly sweep cycle which consists of a standard daily search and fetch and (currently) one of 4 focused searches that repeat every 4 days.

- **Daily**
  Searches for items published in the past 48 hours for:
	- A fixed list of [trade journals](lookups/#daily-journals).
	- A general search for systems & infrastructure
	- A general search for policy, governance & citizen feedback
- **Day 1**
  Searches for digital transformation items published since the last time this day was run for:
	- A fixed list of [national newspapers](lookups/#national-newspapers)
	- A fixed list of [academic journals](lookups/#academic-journals)
	- A fixed list of [NGOs and think tanks](lookups/#ngos-and-think-tanks)
- **Day 2**
  Non-state finance
	- API extraction of newly published IATI activities
	- Searches for digital transformation items published since the last time this day was run for a fixed list of [financiers](lookups/#financiers)
- **Day 3**
  Four separate deep searches for each country:
	- Non-state finance
	- Governance (institutions and instruments, excluding data exchange)
	- Data exchange (content, not transport)
	- Demand and political economy
- **Day 4**
  Deep searches for regions and [regional institutions](lookups/#regional-institutions) focusing on:
	- Policy collaboration and coordination
	- Legal harmonisation
	- Shared infrastructure

## What qualifies as a source

Corpus admits only primary or first-hand evidence: official announcements, laws and regulations, filings, court records, company statements, datasets, on-the-record reporting, primary documents, and published academic work. A source need not break news — a dated explainer or methodology note qualifies — but it must be somebody's own account, not a retelling.

- **Second-hand syntheses are leads, not sources.** AI-generated summaries and aggregator digests have already compressed and paraphrased their inputs, which launders errors into authoritative-looking text and breaks the audit trail. They are mined for the primary documents they cite; those are collected and the synthesis is discarded.
- **Promotional material is not evidence.** Paid placement, awards PR and vendor thought-leadership report no development and are discarded.
- **Origins are screened, not just content.** Domains found to fabricate, rewrite without attribution, or launder others' reporting under their own byline are placed on a drop list and never collected again, however plausible an individual item looks.
- **The full verbatim text is stored, never a paraphrase**, so every claim in every report can be traced back to the exact words of its source. This store is the private repository; what is published is metadata, classification and summaries.

## Dates, figures and currencies

Most errors in a base like this are errors of time. Corpus applies fixed rules to keep them out:

- **Every time-varying figure is written with its date** — "ranked 156th (2020)", never "ranks 156th" — so staleness stays visible on the page rather than hiding behind the present tense.
- **The event date is never the publication date.** When an outlet re-reports an older announcement, the date of the event is established from the primary source or recorded as unknown. Where a date is inferred or imprecise, that is recorded too.
- **Money is carried in the currency it was announced in.** A US-dollar figure derived from it is shown as a dated conversion — otherwise one commitment becomes three "different" numbers as exchange rates move.
- **Newer evidence supersedes older evidence, visibly.** Reports keep the current value and, where the trajectory matters, one dated prior value. An old document arriving late is treated as a baseline, never as news.
- **A genuine gap is stated, dated.** Where no law exists or no figure has been published since a known year, reports say so explicitly — a known vacuum is a finding, not a blank.

## The finance dataset

The non-state finance dataset aims at a claim nobody else supports well: an integrated, accurate view of who is financing digital transformation in Africa. Accuracy is enforced by construction, not by review:

- **The five-fact test.** No item becomes a finance record unless the source itself states all five: a named financier; an identified recipient country or region; an amount that can be treated as a commitment (or an actual disbursement — never an "up to", a target or a valuation); the date of the commitment itself; and a stated purpose specific enough to classify. An item failing any fact is kept as context but excluded from every total.
- **Double counting is prevented structurally.** Records are keyed and deduplicated across sources, re-announcements are merged into the original commitment, and amendments update a record rather than creating a second one.
- **Blanks are honest.** Where a value cannot be derived safely from the source it is left blank with the reason — never estimated, never defaulted to zero.
- **National budget data is still under development** Budget data, where available is recorded at five stages: proposed, appropriated, released, executed or audited.

## Coverage, corrections and versions

- **Coverage is deliberately uneven.** Corpus goes deep where there is active work and stays thin elsewhere; a thin country page reflects collection priorities, not necessarily a quiet country. Collection intensity should never be read as a measure of a country's actual activity.
- **A published file is never silently revised.** Reports and datasets are issued as dated editions. A correction is a new edition with its own date stating what changed and why; the record it corrects remains on the record.
- **Capture is not endorsement.** Holding a document, or profiling an organisation, implies no view of either.


