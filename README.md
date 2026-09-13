# Corpus

**[corpus.data-landscapers.io](https://corpus.data-landscapers.io/)** — reports and datasets on digital transformation, digital public infrastructure and data governance across Africa, rebuilt every night from public documents.

Corpus is a public good for researchers, analysts, funders and officials working on Africa's digital transformation. This repository is the publishing half of it: the scripts, templates and metadata that turn a private evidence base into the public site. This page is for anyone thinking of working with us.

## What Corpus publishes

- **[Country reports](https://corpus.data-landscapers.io/countries/)** for all 54 African countries: a status report, a monthly update, a progress report against [121 indicators](https://corpus.data-landscapers.io/methodology/lookups/#indicators), and a non-state finance report.
- **Region and topic reports**: monthly updates and progress reports for the five African regions, Sub-Saharan Africa, Africa as a whole and relevant global developments, and for each [topic](https://corpus.data-landscapers.io/methodology/lookups/#topics) in a two-tier taxonomy.
- **[Progress](https://corpus.data-landscapers.io/progress/)**: movement on every indicator in every country over the past 12 months, however small.
- **[Finance](https://corpus.data-landscapers.io/finance/)**: an integrated dataset of non-state financing commitments since 2015. National budgets, spend and audit are under development.
- **[Bulletin](https://corpus.data-landscapers.io/bulletin/)**: what arrived yesterday, filterable by country and topic.
- **[Catalogue](https://corpus.data-landscapers.io/catalogue/)**: metadata for every document behind every report — over 21,000 of them — so any claim can be traced to the original publication.

## How it is made

Read the methodology before anything else. It is short, and it sets the rules any collaboration has to work within.

- **[Methodology](https://corpus.data-landscapers.io/methodology/)** — scope, what qualifies as a source, how dates, figures and currencies are handled, the finance dataset's five-fact test, and how corrections work.
- **[Document lifecycle](https://corpus.data-landscapers.io/methodology/document-lifecycle/)** — one document followed from a Somali news site to three published reports, including how a contradiction with an earlier record was settled.
- **[Process inventory](https://corpus.data-landscapers.io/methodology/process-inventory/)** — every step in the pipeline, in the order the work happens.
- **[Lookups](https://corpus.data-landscapers.io/methodology/lookups/)** — the controlled vocabularies and source lists that drive search and classification: countries, topics, indicators, progress categories, and the journals, newspapers, think tanks and financiers swept.

In short: two machines. A private one searches, fetches, screens and classifies documents and stores their full text. This one reads the resulting metadata and writes the reports. Both are run by Claude Code working from written procedures, and each checks the other's work. Only primary sources are admitted, every figure carries its date, and nothing is estimated to fill a gap.

## What is in this repository

| Path | What it holds |
| --- | --- |
| `site/` | The site as served. Generated; never edited by hand. |
| `outputs/` | Metadata datasets: the catalogue, finance and budget records, bulletin summaries, vocabularies. |
| `lookups/` | Vocabularies used in the build: countries, taxonomy, indicators, finance code maps. |
| `content/` | The editable text of each page, in markdown. |
| `scripts/` | The Python that builds reports and pages from the metadata, and the checks run before publishing. |
| `documentation/` | The design record: why the site is shaped the way it is. |
| `*.md` at the root | Procedures the build agent follows, starting with `CYCLE.md`. |

**What is not here** is the full text of the documents. It sits in a private repository because publishing it would infringe copyright. Everything public — here and on the site — is metadata, classification and summary.

## Working with us

**Use the reports and data.** Everything on the site is published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Reports and datasets are dated editions and a published edition is never revised, so cite the edition you used; a correction appears as a new edition saying what changed.

**Tell us what is wrong or missing.** Every page has a feedback link. A wrong date, a misread law, a finance record that fails the five-fact test, a country page that misses something important — these are the most useful things you can send.

**Point us at sources.** Search is driven by the lists on the [Lookups](https://corpus.data-landscapers.io/methodology/lookups/) page, and a list can change without touching any code. If you know a national newspaper, regulator, gazette, journal or financier we do not sweep, or hold primary documents we lack, we want to hear about it.

**Go deep on a country or a theme.** Coverage is deliberately uneven: Corpus goes deep where there is active work. A partner working on a country, a sector or a set of indicators is the most direct way to deepen that part of the base.

**Help build the budget dataset.** National budgeting, expenditure and audit is the largest open piece of work. Budget figures are recorded at five stages — proposed, appropriated, released, executed, audited — and people who know how a given country publishes its budget are exactly what it needs.

**Challenge the taxonomy and indicators.** The topics and indicators decide what counts as progress. If they miss something that matters in your field, say so.

**Reuse the method.** The pipeline is not specific to Africa or to digital transformation. If you want to build something similar, the process inventory and this repository are the place to start, and we are happy to talk.

### Before you open a pull request

Start with an email. The site is rebuilt nightly by automated processes, so a change made directly to `site/` or `outputs/` is overwritten at the next build, and the source lists live in the private collection repository rather than here. We will work out with you where a change belongs.

## Licence

Reports and datasets: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). No licence has yet been set for the code in this repository; ask if that matters for what you have in mind.

## Contact

[info@data-landscapers.io](mailto:info@data-landscapers.io) · Corpus is part of [Data Landscapers](https://data-landscapers.io/).
