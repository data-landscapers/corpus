## Introduction

Corpus is a website containing a range of reports and datasets classifying, summarising and indexing public documents covering digital transformation in Africa. It is updated daily. Behind the website is a private repository containing the text of these documents - it is private for copyright reasons. 

The aim of Corpus is to provide a fast-track information service for researchers and analysts working on the digital transformation of Africa, including digital public infrastructures and data governance.

## Scope

- **Geographical**
  All documents are tagged with one or more country or region iso-3 codes. The list is available here.
- **Topics**
  Corpus has developed its own two-level taxonomy of topics. All documents are tagged with at least one level 2 topic.
- **Finance**
  Corpus is attempting to produce a single integrated view of all financing of digital transformation. The first part of this, non-state financing, is live. It includes all public and private investments sourced from the International Aid Transparency Initiative, investor portals and news articles. The second part, national budgeting, spend and auditing is still under development.
- **Time**
  Corpus' primary focus is current news with over 2,000 documents now being added each month. Older documents are collected to provide baselines to status and progress reports.

## Infrastructure

- **Architecture**
  Corpus is built by two networked machines.
	- The first is responsible for data collection and classification. Its repository is private. 
	- The second is responsible for summarising content and keeping reports and datasets up to date. It's repository is available at https://github.com/data-landscapers/corpus. 
- **Technology**
	  - Search and fetch is managed by [Exa](https://exa.ai/)
	  - Claude Code is responsible for the running all other processes. It is run on Opus but may be downgraded to Sonnet if weekly token budgets are consumed too quickly.
	  - All process instructions are written in markdown and managed by Obsidian
## Data collection

The data collection machine runs a nightly sweep cycle which consists of a standard daily search and fetch and (currently) one of 4 focused searches that repeat every 4 days.

- **Daily**
  Searches for items published in the past 48 hours for:
	- A fixed list of trade journals.
	- A general search for systems & infrastructure
	- A general search for policy, governance & citizen feedback
- **Day 1**
  Searches for digital transformation items published since the last time this day was run for:
	- A fixed list of national newspapers
	- A fixed list of academic journals
	- A fixed list of NGOs and think tanks
- **Day 2**
	- API extraction of newly published IATI activities
	- Searches for digital transformation items published since the last time this day was run for a fixed list of financiers
- **Day 3**
  Four separate deep searches for each country:
	- Non-state finance
	- Governance (institutions and instruments, excluding data exchange)
	- Data exchange (content, not transport)
	- Demand and political economy
- **Day 4**
  Deep searches for regions and regional institutions focusing on:
	- Policy collaboration and coordination
	- Legal harmonisation
	- Shared infrastructure


