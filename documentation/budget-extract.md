---
type: doc
title: Budget extraction — what a figure means
last_reviewed: 2026-09-20
---

# Budget extraction — what a figure means

*(Spec for the domestic-budget work: what is being measured, which point of the budget cycle a figure is, and what a record has to carry. Written 2026-09-20, strategic review 4 R51, from OSINT's `documentation/domestic-budget-extraction.md` — 75,350 words of accumulated per-country method notes, of which this keeps the rules and drops the incident. **The incident is not deleted, it is left where it lives**: that file and its companion `documentation/budget-extraction-strategies.md` are OSINT's, and both are published in the public process mirror, [data-landscapers/osint-process](https://github.com/data-landscapers/osint-process). This file is what Corpus's `BUDGET-EXTRACT` runbook (R54) is written against and what the GHA FY2024 pilot (R56) is measured by. Where it and OSINT's driver `wiki/finance-load-domestic-state.md` disagree on a field, the driver wins.)*

## Three questions decide every figure

Is the line **digital**; is the money the **state's own**; and which **stage** of the budget cycle is it. A figure that has not answered all three is not a record, whatever else is known about it.

Most of what follows is the accumulated cost of getting one of the three wrong on a figure that looked fine.

## Scope — which lines are digital

**The unit of capture is the programme, sub-programme or project line whose stated purpose is a digital activity.** A ministry's total vote is an envelope and is never a record.

**Never compute a digital share of a mixed line.** No percentages, no apportionment. A line that demonstrably contains digital spend that cannot be separated is held at `partial`, not estimated.

**One carve-out — the single-mandate body.** Where a body's entire statutory mandate falls within data governance or digital transformation, its whole appropriation is a record at `whole`. The test is the mandate, not the name: a regulator that also licenses broadcast content or postal services is multi-purpose, and only its digital programmes record.

Every record carries `scope_confidence` (`whole` | `partial` | `unclear`) and `scope_basis`, one line on how the line was identified — programme title, project code, classification tag, narrative paragraph, named system. `partial` and `unclear` records are built and held, and reported separately from the headline total, never folded into it.

**A national statistics office is a single-mandate data body** *(2026-09-24, budget sprint)*. Official statistics is in the frame (`data.statistics`, with censuses and surveys an indicator of its own), so the office's whole appropriation records at `whole`. Where the vote prints the office's programmes or sub-programmes, hold them at that grain, never the office's total beside them. A statistics unit inside a line ministry is part of that ministry's administration and records only where it prints a digital line of its own.

**Scope by the line's text, never by its label.** States name an entire ministry's budget a *programme de digitalisation* and run a national radio station inside it. The inverse is commoner: the largest identity appropriation in a budget is usually called *Civil Registration*, *<Ministry> Computerisation* or *Passport Administration*, and no keyword reaches any of them.

**Generic office hardware is overhead, not a digital-activity line.** Computers, network maintenance and IT equipment purchases are excluded; software, systems, digitalisation, connectivity and biometric lines are recorded.

**The sector vote is never the whole, and a cross-vote scan is not optional.** Wherever it has been measured, digital money outside the digital ministry has run from about 60% of the sector vote to more than double it, and the largest single line in a country has repeatedly sat in interior, finance, justice or the head of government's own vote. The scan **locates and does not identify**: in a stacked layout a keyword and an amount five lines apart belong to different rows, so read the whole vote block and pair by position before recording anything from it.

## The origin gate — whose money it is

**A budget line financed externally is `non-state`, not `domestic-state`.** Run the gate on every line before building anything.

| Line's stated funding source | `finance_origin` | Then |
|---|---|---|
| Domestic revenue; domestic borrowing; own-source levy or fee income | `domestic-state` | build normally |
| External loan; external grant; development-partner financed | `non-state` | definite-match to a held deal first |
| Counterpart against an external project | split | only where both parts are printed separately |
| Not stated | `domestic-state`, flagged | `funding source unstated` in the notes |

`funding_source` is closed: `domestic-revenue` | `domestic-borrowing` | `own-source` | `external-loan` | `external-grant` | `counterpart` | `unstated`.

**A line naming no funder beyond "external", "Dons" or "Externo" builds no record at all** — not a domestic one and not a donor one. Its magnitude is stated as a dated finding instead. A combined counterpart figure is one line at its stated origin with the blending noted, never apportioned.

**Where the document prints an origin column, it is the most valuable property the volume has.** The forms met so far: `État Seul / Contrepartie / Subvention / Prêt`; `SOF`; `Financement intérieur / extérieur (Dons | Emprunt)`; `Treasury / Retained Revenue / Assistance / Loan`; `GoG / IGF / Funds / Donors`; `Interno / Externo`; `Tesouro / OFN / Donativo / Empréstimo`; and, in one state, the last segment of the account key itself. Where no column exists the origin is a flagged inference, and the split has to come from the settlement law, the investment programme or the minister's own account.

**Check what a "contribution" column is contributing.** One was read as an external share for a whole run and is gender-responsiveness budgeting. Read the table's own title before treating any column as a financing split.

**Own-source money is domestic-state.** A regulator's or fund's levy, licence and fee income is state revenue by another route, and it is frequently the majority of what pays for the digital state — in one country 69.7% of the largest digital programme, in another the whole of a registry body's budget. It is usually **legislated in the finance law's articles rather than appropriated in the vote**, as a revenue-share key or a ceiling on affected own revenue, so read the articles and the *comptes spéciaux*, not only the vote table.

**Transfers inside the state are captured at the spending end, once.** Where a line transfers to a body whose budget is also held, set `is_transfer: true` and name the receiving body; the compile excludes those lines from the total. Where the receiving body is not held, the line counts normally, with a note why.

**A headline is untrustworthy without the split.** One ministry's headline has misled in three different directions in three consecutive years — an external loan collapsing, the same loan returning while domestic money fell, then both falling — while the domestically financed programme moved the other way each time.

## The stages

`proposed` (tabled) | `appropriated` (enacted) | `revised` (supplementary or in-year revision) | `released` (warranted to the MDA) | `actual` (outturn) | `audited`.

**Each line-year is one record and every stage folds into it**, as a dated entry in `## Stage history` with its figure, document and locator. A later stage never overwrites an earlier one and is not a contradiction. `baseline_stage` is the earliest stage held and `current_stage` the latest; where the baseline is not `appropriated`, the first line of the notes says so.

**What promotes a figure to `appropriated` is evidence of enactment, not the document's caption.** States publish the pre-enactment text from a template whose law number is never filled in, so the blanks are not the test. Tests that have worked: the file's own modification timestamp against the reported ratification date; the accounting system's `Approved Budget` column, which is the enacted figure loaded to the ledger; a mid-year ordonnance restating the voted column; the next year's volume printing the prior year's enacted collectif as its comparator. **Aggregate agreement between bill and law does not imply line agreement** — in one year the grand totals matched exactly while five of fifteen digital bodies had moved during passage.

**An in-year figure is not an outturn.** A quarterly execution number goes in the stage history; putting it in `actual_total` lets the compile read three months as the year and print a false execution rate.

**A commitment plan is not a stage**, and neither are the engagement and liquidation columns of a French-style chain. They are context.

**MTEF outer years and plan-period totals are not records.** One state's outer-year projection understated the enacted figure by 2.3×.

`budget_version` is `original` | `supplementary-N` | `revised`. A supplementary states either an increment or a restated total and `supplementary_basis` records which; `restated-total` supersedes the original for totalling, and `unclear` excludes the line from totals.

**Execution is measured on two bases, never one.** `execution_pct_vs_appropriated` is budget credibility and is the headline; `execution_pct_vs_revised` is absorption. **Read the modifications column before quoting any rate**: a 100% draw-down on a base cancelled by 68% in-year is not delivery, and an earmarked levy line written down to collections reads ~100% by construction. **Carry the qualifier with the rate** — where the numerator excludes personnel and the denominator does not, the rate is a floor and must say so.

## The record shape

**One record per budget line per fiscal year.** The appropriation is the baseline and supplies the `## Description`, the line's stated purpose verbatim, carried unchanged as later stages accrete.

**The grain is the finest level the document prints for that line.** Where a programme is broken into sub-programmes, each digital sub-programme is its own record; where the document stops at programme, the programme is the record and the sub-programme field is blank, meaning the document published no finer level. **Never hold a programme and its own sub-programmes for the same year** — they would sum. A finer document supersedes a coarser one: the parent is retired, not kept alongside.

**Codes are the join key** across years and between budget and outturn. Capture the name and code verbatim at each level — admin head, spending entity, programme, sub-programme — and never invent a code the document does not print. `econ_class` is recorded as stated and never mapped to a house vocabulary.

**A bare year means the fiscal year beginning in that year**, whatever the country labels it, and the bare start year is the form used everywhere a fiscal year is named. `fiscal_year_label` holds the document's own form verbatim, `fy_start` / `fy_end` the ISO dates, `fy_calendar` the calendar. `published` anchors on the appropriating or reporting event where stated, else on `fy_start` at month precision.

**`amount_scale` is the first thing to establish**, recorded as printed and with every amount stored normalised to units. Where capital, recurrent and total are all given they must reconcile, and on a mismatch the line is not recorded until it resolves. Where only a combined figure exists the split is left blank, never derived.

`currency` is the announcing state's own, the code in force in that fiscal year, with any redenomination noted rather than back-converted. `amount_usd` is a dated conversion at a named fiscal-year average rate, never a spot rate at capture, and **USD is never summed across fiscal years**.

`state_level` is `national` | `sub-national` | `soe` | `levy-fund` | `regulator`; `place` is always the country ISO-3 and a sub-national unit is an entity plus a verbatim tier name. Three actors are tagged: the **financier** — the fisc, an institution and never a minister — the **spending entity**, and the **vendor** where the document names one.

`deal_id` is `{ISO3}[-{tier}]-{fy}-{admin_head_code}-{programme_code}[-{sub_programme_code}]`, with no stage suffix: the stem is the record id, one per line-year. Gaining sub-programme grain is a new id, a rename plus the parent's retirement.

Every record carries `doc_type` from the closed list and `doc_locator` as printed, and links to the one companion page holding the document's citation, scope, classification structure and scale headers.

**Corpus's carrier is a CSV row, not a wiki record** (R54: `budgets/{ISO3}/{FY}.csv`, tracked, citing the source slug per row). The field vocabulary above is the same on both sides deliberately, so that a Corpus row and an OSINT record say the same thing in the same words.

## Reading the document

**Cross-foot before recording. A table that does not cross-foot is not a table that may be published.** Every confidently wrong figure this work has produced was available to be caught here, and the ones that were caught were caught by arithmetic rather than by inspection.

**Scale is a property of the table, not of the document.** One volume routinely prints full units, thousands, millions and percent of GDP in different tables, and the narrative and the annex six pages apart disagree.

**Layout drift is the commonest silent failure.** Codes, labels and amounts are independent vertical stacks paired only by position, so a text dump attaches a row to its neighbour's money and looks entirely plausible doing it. **Bind by page geometry**, clustering words or characters on their vertical position. Where a library returns a number one digit shorter than the page prints, it is dropping glyphs — read at character level.

**`pdftotext -table` beats `-layout`** on recapitulative and summary tables, where `-layout` is unusable on several document classes. **Always extract with `-enc UTF-8`**: the default is Latin-1, and read as UTF-8 every accented search term then returns zero, which looks exactly like a finding. Corroborate any "zero occurrences" claim with an unaccented term.

**There are four text-layer states and they need different tools.** Native. A scan with no layer, which needs OCR. **Native text in a rotated frame**, which returns reversed strings and must never be sent to OCR — it is perfect data. And **a scan carrying a pre-baked OCR layer**, which passes every "is it native" test while its digits are corrupt and its pagination does not match the images. Test for a full-page image as well as for characters. A garbled page in an otherwise clean file is a font problem, not a scan.

**Before commissioning OCR, try the cheaper routes.** The bill is frequently native where the enacted law is a scan. The gazette publishes the same instrument with a text layer where the ministry's copy does not. The next year's volume carries the prior year's revised figures in its comparator column. A mid-year restating instrument recovers the voted column. The accounting-system extract carries several stages in one table. Where OCR is the only route, one attempt is a terminal state: commit the sidecar so nobody repeats it.

**Machinery-of-government changes break the code series, and they are the norm.** Ministries split and merge mid-year, programmes are renumbered, project codes are reissued, perimeters move and bodies change political master. Any series keyed on a code needs an explicit mapping row at the date of the break, and a body-level jump says nothing about the digital line inside it.

**Run one reconciliation per country-year before anything else** — a domestic figure in the estimates against the same figure in the execution annex, or a programme sum against its printed section total. It fixes the scale, confirms which annex is domestic that year, and catches a wrong join before it becomes a record.

## What is never a record

An envelope: a ministry total, a thematic total that spans ministries, or a body whose mandate is mixed. An MTEF, plan-period or indicative figure. A procurement plan or a signed contract — neither is an appropriation, and a plan re-based on the enacted vote is the same money under two naming systems. A tax expenditure: foregone revenue is not spend, though in one state it was five times the vote and no total should omit it. State revenue — privatisation proceeds, spectrum sales, the receipts a regulator mobilises for the treasury. A commitment plan. A line whose funder is named only as external. And never a parent and its own children together.

## An absence is a finding, and it has to be earned

**A nil return that searched only the sector vote is not a nil return.** Two consecutive years recorded a cybersecurity agency as absent; it had been appropriated throughout, under the prime minister's office.

**A body invisible in the estimates may still be funded.** It may sit inside another ministry's vote, be financed by statutory levy outside the vote entirely, be carried by an own-source regulator, or be named only in a supply speech, a parliamentary answer or the framing letter's chart of accounts. Establish which before writing "unfunded".

**A complete enumeration is what makes an absence evidence.** Where the library was walked end to end and the term is not in it, the absence is a dated finding and says what was searched. Where it was not, the result is that nothing was found, which is a different statement.

**The absence is often the story.** A state that has enacted a data-protection law and appropriates nothing to the authority it creates, a civil registry built entirely with other people's money in a state that finances two thirds of its own budget, a national identification line of about US$7,000 against a data centre at twenty-six billion — each of those is a figure this dataset exists to carry, and each was reached by reading what the budget does not say.

## Where the rest lives

The **instrument-level method** — how to get a figure off a particular kind of page — is OSINT's `documentation/budget-extraction-strategies.md`, the archetype library A–T. This file says what a figure means; that one says how to read it. The **per-country reconnaissance and its incident history** are OSINT's `documentation/domestic-budget-extraction.md`. Both are published in the public process mirror.

The **record's field definitions** are OSINT's `wiki/finance-load-domestic-state.md` and `wiki/finance-record-spec.md`.

Corpus's own runbook is `BUDGET-EXTRACT.md` (R54) and the first extraction against this spec is GHA FY2024 (R56). **The row shape this spec describes is stated as data in `scripts/budget_source.py`** — the 46 columns of `budgets/{ISO3}/{FY}.csv`, the closed vocabularies, and the checks a file has to pass before the finance compile will build from it.
