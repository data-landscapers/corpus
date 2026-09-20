# Document furniture

The standing note that appears on every bulletin, and the glossaries that explain a report's status, movement and progress values. Read by `scripts/render.py` (the note, as HTML) and `scripts/report-render.py` (the glossaries, as markdown).

The `meta-*` blocks are the **search-result descriptions** — the one sentence Google shows under a report's title, and the only prose about the document a reader sees before opening it. `render.py` reads them as plain text, one per kind, filling `{subject}` with the place or topic the title opens with. They were written on 2026-09-20; before that every report carried its own title back at itself — *Status report — South Africa: status report. Edition of 2026-09-17* — which told a searcher nothing and named none of the subjects the site is about. Keep them under about 155 characters and put the expendable clause last: what is past that is what gets cut off.

`bulletin-notes` appears on the bulletin alone, and is the whole of what *About this document* says there — Bill wrote it on 2026-08-21 (`prep/bulletin.md` 15) and it replaced two paragraphs about batch acquisition and what the page is not.

`report-notes` was the same furniture on all 241 reports and **came off on 2026-09-09** (Bill). Its two paragraphs said that figures are dated and that a dated edition is not revised; the document says both of those itself, in the byline, in the Edition row and on every dated figure. A report's *About this document* is now the Edition, This file and Licence rows and nothing else.

Editing rule: this appears on *every* document of its kind, so a sentence added here is a sentence added several hundred times. Say less rather than more.

## bulletin-notes

This bulletin is produced automatically at the end of each data collection sweep but only includes items published on the day cited in the edition, and the previous day. Items published in the last month can be found on the [country pages](https://corpus.data-landscapers.io/countries/). The links to all items stored in the corpus can be found in the [catalogue](https://corpus.data-landscapers.io/catalogue/).

Bulletins are kept for a week — the last week's editions are listed above, each at its own dated address — and are then deleted. Older material is in the country pages and the monthly reports.

## status-vocab

**Status values.** *Implemented* — in operation or in force. *Piloting* — running with a limited user group or in a controlled environment. *In development* — build or drafting under way, not yet operating. *Planned* — announced or provided for, no build or draft on record. *Enacted* — an instrument passed into law; pair with a qualifying clause for its in-force date. *Under review* — a law or policy currently being reconsidered. *Discontinued* — closed or superseded. ***Not held*** — the repository carries no reliable statement of status; these are the gaps to fill and are listed again at the end.

## movement-vocab

**Progress values.** *Movement* — some form of progress, however minor, has been recorded. *Stalled* — a stated target passed without delivery. *Regressed* — an instrument was withdrawn or neutralised, or a reported position worsened. *Closed* — the programme ended. *No change* — the repository holds a standing position and nothing in the period touched it. ***Baseline not held*** — there is evidence of movement but no baseline to compare it against. A value may carry a qualifying clause after a comma, as in *Movement, slipped*.

## progress-vocab

**Progress values.** *Movement* — some form of progress, however minor, has been recorded. *Stalled* — a stated target passed without delivery. *Regressed* — an instrument was withdrawn or neutralised, or a reported position worsened. *Mixed* — the indicator's instruments moved in different directions in the period; the clause after the comma names which moved which way. *No change* — the repository holds a standing position and nothing in the period touched it. ***No evidence*** — the repository holds nothing on this indicator at all. A value may carry a qualifying clause after a comma, as in *Movement, regulations still pending*.

## progress-frame

This report asks the same set of questions of every country. The rows below are a fixed frame of indicators, one row each, chosen in advance and covering all thirty-eight subjects the repository tracks — so what appears here is decided by the frame and not by whichever records happened to accumulate. Each row says what happened on that indicator during the period, with every claim linked to the source it rests on.

Where a row reads ***No evidence***, the repository holds nothing on that indicator. **That is a statement about this repository, not about the country** — it does not mean nothing exists, only that nothing has been collected here yet. The rows that carry evidence say what it is; the rows that do not are left to speak for themselves.

## meta-status

{subject}: digital transformation, digital public infrastructure and data governance — policy, regulation, finance, connectivity and skills, each claim sourced.

## meta-monthly

What moved this month in {subject}: digital transformation, DPI, data governance, policy, regulation, infrastructure and finance, each item sourced.

## meta-progress

A year in {subject}, indicator by indicator: digital transformation, DPI and data governance — what moved, what stalled, and what is not held.

## meta-topic-monthly

{subject} across Africa this month: digital transformation, DPI and data governance, country by country, each item sourced.

## meta-topic-progress

{subject} across Africa over a year: digital transformation, DPI and data governance, country by country — what moved, what stalled, and what is not held.

## meta-bulletin

Today on digital transformation, DPI and data governance across Africa. {subtitle}
