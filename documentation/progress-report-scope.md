# What counts as a system or instrument

**Superseded (2026-08-27, Bill).** The progress report is now framed on the fixed indicator list — `progress-report-redesign.md` and `indicator-mapping-conventions.md` are the current design; every unit carries `indicators.csv` and ledger rows feed indicators via `row_ids`. None of the three options below was adopted; the indicator frame dissolved the question. Kept as the record of the diagnosis.

*(Design question, 2026-08-25. Bill, reviewing the country reports: "This report needs a rethink. There are too many random system or instruments. I think we need to build a structured list of what counts as a system or instrument." Nothing here has been actioned — the five stated edits to the progress report were made and this was not, because deciding what a ledger row is changes 6,083 rows across 57 ledgers and is not a change to make in the same pass as a heading rename. This is the evidence, the diagnosis and three options, so the decision can be taken rather than researched again.)*

## The complaint is measurable, and it is not really about the progress report

South Africa's ledger carries 150 rows. Twenty-five are measures, one is a `system`, and the rest are `instrument`. Reading the first thirty by name is enough to see the problem:

> Analogue television switch-off date · Cape Town internet exchange (CINX) · Cell C 5G service · Data-centre incentive instrument (SEZ, depreciation, grid priority) · Draft Radio Frequency Spectrum and Fees Regulations amendments · Equinix Cape Town land use · High-demand spectrum auction · **Human rights commission inquiry into data centres** · Johannesburg data-centre expansion · National Cybersecurity Policy Framework · Public participation in data-centre approvals · **Rights commission inquiry into data-centre expansion** · SA Connect phase 2 · Teraco CT2, Cape Town

Four different kinds of thing are on one list. A **legal instrument** (the Cybersecurity Policy Framework, the draft regulations) has a state that changes by a formal act and stays put between acts. A **state programme** (SA Connect phase 2, the spectrum auction) has a target and a delivery record. A **commercial facility** (Teraco CT2, CINX, Cell C's 5G service, Equinix's land use) is somebody else's asset, which advances continuously and by its own logic. And an **event or process** (a rights-commission inquiry, "public participation in data-centre approvals") is a thing that happens, not a thing that has a status.

The last two are what makes the report read as a list of random objects. A twelve-month movement table is a good instrument for the first two, because "did this advance, stall or regress" is a real question about a law or a programme. Asked of a private data centre it is a press-release summary; asked of "public participation in data-centre approvals" it is not a question at all.

**The bolded pair is the same inquiry, entered twice.** That is not a scope problem but it is the symptom of one: when the admission rule is "a source reported something", two reports of one event produce two rows, because there is no definition either of them has to match.

## Two other things the numbers show

**The `kind` vocabulary has already drifted.** `documentation/report-layer.md` defines two values, `instrument` and `measure`. The ledgers hold four: 5,411 `instrument`, 666 `measure`, 5 `system`, 1 `institution`. Nothing checks it, because check I skips the `kind` column entirely. Whatever rule is settled below, it wants a closed vocabulary and a check, or it will drift the same way inside a month.

**Two thirds of rows rest on a single source.** 4,011 of 6,083 cite exactly one slug. That is not wrong — a gazette notice needs one citation — but it is the shape of a base built by admitting whatever arrived, and it is why a "system or instrument" can turn out to be one article's framing of an event.

## Three ways to draw the line

**1. A typed vocabulary, enforced.** Replace `instrument`/`measure` with a closed list — say `law`, `regulation`, `policy`, `programme`, `system`, `body`, `measure` — and give check I a rule per type. The progress report tables only the types that have a formal state; the rest move to the monthly, which is where events belong. Cost: reclassifying 6,083 rows, which is a model pass over every ledger, and a decision per row that is sometimes genuinely hard. Benefit: the distinction is in the data, so every document and every future view gets it for free.

**2. An admission test, applied at the row.** Keep one type, and add a test a row must pass to exist: *does this thing have a state that changes only by a decision someone made, and can that decision be dated?* A law passes, a programme passes, a data centre fails (it advances by construction), an inquiry fails until it reports. Cost: it is a judgement, so it needs writing down carefully and it will still be argued about. Benefit: no schema change, no reclassification pass — the test is applied when a row is written and when a build revisits one.

**3. Leave the ledger alone and filter the view.** The progress report tables only rows whose `movement` is `Advanced`, `Stalled`, `Regressed` or `Closed` and whose object is state-side; everything else stays on the ledger and appears in the status report only. Cost: the smallest, and it is reversible in an afternoon. Benefit: it does not fix the underlying classification, so the status report keeps the mixed list — which may be the right place for it, since a status report is an inventory and an inventory of everything held is defensible in a way that a *progress* report over everything held is not.

**These are not exclusive, and 3 is the cheap half of 1.** The order that costs least for what it buys is: write the admission test (2), apply it to the view now (3), and reclassify (1) only if the test turns out to need types to be stated crisply.

## What is not in doubt

Whatever is decided, `measure` stays as it is. A dated measure of a system — blocked identity numbers, delivered data-centre load — is not a system or an instrument, is already excluded from the status inventory, and is already the one thing on the ledger whose place in a progress report is unambiguous.
