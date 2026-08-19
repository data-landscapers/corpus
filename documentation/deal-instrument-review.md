---
type: doc
title: Deal field mappings — review of Bill's proposals
last_reviewed: 2026-08-19
---

# Deal field mappings — review

Three proposals, three reviewed files. `instrument` is below; `status` and `beneficiary_type` follow it.

| field | Bill's file | reviewed | distinct → canonical | coverage |
|---|---|---|---:|---|
| instrument | `deal-instrument-fix.csv` | `lookups/deal-instrument-map.csv` | 115 → 15 | complete, 10 rows awaiting source |
| status | `deal-status-fix.csv` | `lookups/deal-status-map.csv` | 24 → 5 | complete |
| beneficiary_type | `deal-beneficiary-fix.csv` | `lookups/deal-beneficiary-map.csv` | 53 → 9 | complete |

**The case-insensitive matching point applies to all three.** So does the blank-versus-`Unknown` question: 41 rows have no instrument, 50 no status, 75 no beneficiary type, and none of the three lists says what an absence means.

# Instrument

Bill's proposal is `C:\OSINT\my-notes\deal-instrument-fix.csv`, 113 rows of `canonical,source value`. The reviewed version is `lookups/deal-instrument-map.csv` in this repo, with two columns added: `review` (blank, `CHANGED`, `ADDED`, `REVIEW`) and `note` (why). Nothing in OSINT was touched — the sweep cycle is running, and this is Corpus's to hand over rather than to apply.

It collapses **115 distinct instrument values to 15**, and after the additions below covers every row in `all-nonstate.csv` except 10 awaiting review and 41 that are blank in the data.

| instrument | rows | | instrument | rows |
|---|---:|---|---|---:|
| Grant | 603 | | Bond | 13 |
| Equity | 204 | | Self Funded | 10 |
| Commercial Loan | 151 | | Buyer's Credit | 10 |
| Concessional Loan | 115 | | Unknown | 9 |
| Technical Assistance | 38 | | PPP | 6 |
| Guarantee | 28 | | Line of Credit | 4 |
| MoU | 13 | | Mezzanine | 4 |
| | | | Joint Venture | 1 |

## One thing to fix before it is used as a rule

**Match case- and whitespace-insensitively.** Two values in the data missed the map on capitalisation alone: `Equity (seed)` against the proposal's `Equity (Seed)`, and `Public-Private Partnership` against `Public-private partnership`. Two misses out of 115 is a 98% hit rate that looks like success and is actually a warning — the same near-miss will recur on every new record, because case is exactly what a writer varies without noticing. Normalising the key costs one line and removes the class of failure.

## Seven mappings changed

**The five IDA credits: `Line of Credit` → `Concessional Loan`.** An IDA credit is IDA's concessional lending instrument — long maturity, no or negligible interest, a service charge — and not a revolving facility, which is what a line of credit is. The evidence is in the records: `IDA concessional credit (0.5% max commitment charge on unwithdrawn funds; repayment from Oct 2030, semi-annual over 20 years)` states concessional terms in the value itself. This matters beyond tidiness: `Line of Credit` would have held 10 rows of which half were misfiled, and the genuine lines of credit — India Exim to Eswatini and Nigeria — are a different animal that deserves its own count.

**`Concession agreement (20-year, financier-funded)`: `Concessional Loan` → `PPP`.** A concession is not a concessional loan; the words are false friends. The record is the AfCFTA Secretariat's 20-year, US$3.1bn customs-modernisation concession with Bergmans, financier-funded — the textbook PPP shape. **This is the third-largest commitment in the base**, so its instrument is worth getting right.

**`Donation (+ 3-year MoU)`: `MoU` → `Grant`.** The money is a donation; the MoU is the wrapper it arrived in. National Bank of Malawi, MWK 75.5m to the ICTAM Innovation Jam. Filing it under MoU records the paperwork and loses the transfer.

**`Standard loan (IATI finance-type 421)`: `Concessional Loan` → unmapped, needs the source.** IATI 421 is the *generic* loan code and carries no concessionality — that is expressed elsewhere in an IATI record, not in `finance-type`. Both rows are BOAD sovereign loans (Benin XOF 19.5bn, Senegal XOF 30.9bn), and BOAD lends on concessional and market terms both. Mapping on the code alone reads something into it that is not there.

## Twelve blanks filled

Self Funded: `Corporate capital investment`, `Corporate capital investment (self-funded)`, `Corporate investment`, `Private investment (capex)`.
Equity: `Pre-seed round`, `Fund commitment (LP)`, `Growth-capital investment (type not further specified in source)`, `Series B (equity and debt)`.
Also `Syndicated financing (CBC as Lead Underwriter…)` → Commercial Loan, matching the existing `Syndicated loan` rule; `Financing package (EC budgetary guarantee)` → Guarantee; `Export finance` → Buyer's Credit; `IDA investment financing` → Concessional Loan *(low confidence — IDA IPF can be a credit or a grant)*.

## Eight still need the source

`5G spectrum licences` and `Spectrum award (410 MHz)` — money flowing *to* the state for a licence, not finance to a recipient; arguably not deals at all. `Investment under NTRA data-centre licence` — is the instrument the licence or the capex behind it? `Procurement contract award` — a contract award is not a financing instrument. `Program-for-Results (PforR)` — a World Bank *lending* instrument rather than a finance type, and an IDA grant PforR is already mapped to Grant, so this one needs its own record read. `Mixed` and `Funding + technology + technical support` — both say only that it is more than one thing. Plus `Standard loan (IATI finance-type 421)`, above.

## Two questions about the vocabulary itself

**`MoU` and `Self Funded` are not instruments.** An MoU is an agreement type — it says a deal was signed, not what form the money takes — and "self funded" is a funding *source*. Both are useful buckets and both are honest about uncertainty, which is why I have left them; but if this list is to be the rule for new records, it is worth deciding whether they are instruments or a second facet. The MoU bucket in particular will absorb anything where an agreement was announced and the terms were not, which is a large and growing class.

**Blank and `Unknown` both exist.** 41 rows are blank and 9 map to `Unknown`. If blank means "the source did not say" and `Unknown` means the same, they should be one value. If blank means "nobody has looked", that is worth a third value rather than an absence, because an absence cannot be counted.

# Status

24 values to 5: **Active 824, Closed 262, Approved 82, Pipeline 40, Unknown 2**, plus 50 blank. The IATI codes map cleanly — `Implementation` to Active, `Pipeline/identification` to Pipeline — and the lifecycle reads correctly.

## Two changed, both the same mistake

**`Announced — facility inaugurated` → Active.** The facility is inaugurated, so it is operating. Konecta's US$100m Egyptian regional HQ and first global GenAI centre.

**`Approved — project activities launched 2026-07-29` → Active.** Activities launched, so it is running. The Pandemic Fund's Cameroon project.

Both were mapped on the word the value opens with. **In a value of the form `X — Y`, the clause after the dash is the later fact and the one that governs** — which is the rule the list already follows for `Launched (January 2026) → Active` and `Closed (100% disbursed as of 2020-12-31) → Closed`. Worth stating explicitly, because it is the reading a mapper has to apply and it is not obvious from the pairs alone.

## One added

**`(not stated)` → Unknown.** One row, and the only value in any of the three columns that the proposals missed entirely.

## Two rulings worth making

**`Announced` is ambiguous by sector, not by wording.** In a public-finance lifecycle an announcement *precedes* board approval, so it is weaker than `Approved`; in a private one it usually *follows* closing, so it is stronger. Both rows here are the private case — Fincart's seed round, co-led by Launch Africa and Antler — where announced means done. Mapping it to `Approved` is right for these two and will be wrong for the first government announcement that arrives.

**Nothing covers cancelled or suspended.** IATI activity-status carries `5 cancelled` and `6 suspended`, and the IATI driver is a live source. Neither appears in the data yet and neither has anywhere to go when it does. `Finalisation` has the milder version of the same problem: IATI 3 means activities complete with financial closure pending, so it is neither Implementation nor Closed. I have left it at `Closed` as the nearest of the five, but a deal in finalisation is still open on paper.

# Beneficiary type

53 values to 9: **Public Sector 543, Private Sector 325, NGO 192, Multilateral 35, Fund 31, Multi-stakeholder 28, Research 28, PPP 2, Individuals 1**, plus 75 blank. The regional and continental bodies all resolve to Multilateral correctly, and the long tail of private-company descriptions collapses cleanly.

## Three changed

**`Individuals / students` → Individuals, not NGO.** Startup Abuja's student aid programme, NGN 50m to students in higher education. The beneficiary is individuals; `NGO` describes the *financier*. This needs a new canonical value — there is nowhere in the six for money that goes to people.

**Two mixed lists → Multi-stakeholder.** `Public sector employees, private-sector employees, women, entrepreneurs/SMEs, Ministry of Education, training companies` was mapped to Public Sector, which is one of the six things it names. `African researchers, startups, universities, nonprofits, community organisations` — the Gates/Microsoft LINGUA Africa award — was mapped to Research, which leads the list but does not describe it.

## Two canonical values added, covering 59 rows

**`Fund` — 31 rows.** AFC's commitment to Africa-focused technology fund managers, FMO to TIDE Africa II, BII to the Africa50 Infrastructure Acceleration Fund. A fund is an investment vehicle, one step removed from whoever eventually receives the money, and that distance is the reason to count it separately rather than fold it into Private Sector: a commitment to a fund and a commitment to a company are not the same fact.

**`Multi-stakeholder` — 28 rows.** FCDO's Frontier Technologies programme, the Mastercard Foundation–UNHCR refugee partnership. Genuinely multi-party, and a real category rather than a failure to classify. `Multi-partner consortium (not yet selected)` joins it.

## Three things to settle

**There is no `Unknown`.** The instrument and status lists both have one; this list does not, and it has the most blanks of the three at 75 rows.

**`PPP` is doing two jobs.** It is a value in this vocabulary and in the instrument vocabulary, and in neither is it really the thing the column measures — a PPP is a *structure*, not a beneficiary and not an instrument.

**`Industry association` sits awkwardly at NGO.** ICTAM is a membership body of private firms and not-for-profit. NGO is the better of the available fits and I have left it, but the association case will recur and is not obviously civil society.

# What I did not do

Nothing was written to OSINT. The reviewed files are in Corpus `lookups/` and are ready to move to OSINT's `lookups/` when the sweep cycle finishes; Corpus needs its own copy in any case, because the mapping applies at `_ns_row()` in `scripts/build-finance-page.py` — the one function that writes all three columns.
