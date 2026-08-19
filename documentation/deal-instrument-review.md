---
type: doc
title: Deal instrument mapping — review of Bill's proposal
last_reviewed: 2026-08-19
---

# Deal instrument mapping — review

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
