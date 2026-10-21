
## Bulletin

The bulletin contains a list of news stories published yesterday that have been collected and classified by Corpus' automated overnight processes. Occasionally a top-up sweep is run to include news published today.

News is discovered using Exa Search and classified by Claude Code.

You can also access all news published since the beginning of last month by country or by topic.

## Finance

Corpus' work on building finance datasets is aimed at overcoming three challenges: 
- No one has integrated non-state finance data with national budgets, expenditure and audits.
- No one has joined up the full spectrum of cross-border and domestic, public and private investment.
- With the exception of the World Bank, no investors or governments have attempted to adopt a common modern taxonomy that classifies investments in categories compatible with digital transformation.

The *Non-state Finance* dataset documents funds committed to digital transformation by financiers other than the state: bilateral and multilateral donors, development finance institutions, foundations, private investors, vendors and operators. Figures are commitments, not money spent, and are recorded in the year they were made (not spread across multi-year contracts). Regions are recipients in their own right, not totals of the countries in them.

We parse the text accompanying each commitment to arrive at a primary topic categorisation. Some commitments are only partly digital: a rural project that pairs broadband with electrification, for example. The digital part cannot be separated, so `commitment_usd_m` counts 50% of a commitment whose scope is partial or unclear. The `scope_basis` column explains why a row was judged that way,

The *Budgets* dataset monitors national budgets since 2024. Where available every digital-transformation-related budget line is traced from proposed through appropriated and revised to actual and audited expenditure. These values are recorded in the local currency. The most recent of the values is converted to US dollars for cross-country comparison.

The *All Finance* dataset combines the above two tables. As far as we are aware this is the first time this integrated approach has been attempted in Africa.

## Country news

This report collects all sources relating to your selected country that have been published since the beginning of last month; The sources are grouped by chapter, topic and story. Each story links to the original source. 

News is discovered using Exa Search and classified by Claude Code.

(NB that the Corpus repository only publishes metadata for each source to comply with the original publisher's copyright.)

## Country status

This report is an attempt to provide a comprehensive summary of the status of digital transformation in your selected country. It is grouped by chapter and topic.

The report only uses evidence from public sources catalogued in the Corpus repository. Corpus aims to discover and index all evidence that is available from public online sources. Pay-walled, password-protected and unpublished documents are not included. This means that while there should be no 'hallucinations' there may well be gaps.

The report is written by Claude Code and updated nightly whenever new relevant evidence arrives.

Two shorter country reports are also maintained. The *Progress Report* tracks developments that have taken place over the past 12 months. The *Maturity Assessment* dashboard compares the progress of all 54 countries across 115 indicators.

## Maturity assessment

The maturity assessment dashboard compares the progress of all 54 countries across 115 indicators. The indicators are grouped into 10 chapters and 35 topics. The criteria for classifying each indicator is derived from a norm or target stated in one of the African Union's foundational instruments. 

Corpus provides country analysis in three separate reports. In addition to this report the *Status Report* provides a more detailed summary of all aspects of digital transformation, and the *Progress Report* tracks developments that have taken place over the past 12 months.

These assessments are updated overnight whenever new relevant evidence arrives. And once a month each indicator is rebuilt entirely.