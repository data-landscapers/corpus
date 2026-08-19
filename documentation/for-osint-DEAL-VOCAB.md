# DEAL-VOCAB.md

*(Written in Corpus 2026-08-19 for copying to the OSINT repo root as `DEAL-VOCAB.md`. The three lookup files it refers to are in Corpus `lookups/` and go to `C:\OSINT\lookups\` unchanged. Delete this italic note on the way across.)*

Three fields in every `## Deal record` — **Instrument**, **Status**, **Beneficiary type** — have never had a controlled vocabulary, and 1,260 records have been written to whatever the source happened to say. The result is 115 distinct instruments, 24 statuses and 53 beneficiary types, three of them driving filter dropdowns on the public site. This file establishes the vocabularies, states the rules for writing the three fields, and specifies the pass that brings the existing records into line.

## 1. The vocabularies

**`lookups/deal-instrument-map.csv`, `lookups/deal-status-map.csv` and `lookups/deal-beneficiary-type-map.csv` are the authority.** Each holds `value, definition, source_value, review, note`, and **the distinct set of values in the first column is the vocabulary** — there is no second list to keep in step with it, which is the point: a vocabulary held apart from its mapping is a vocabulary that will disagree with it.

The `definition` column repeats for every row carrying the same value. That redundancy is deliberate — a writer looking up what to put in a cell reads one line and has both the value and what it means, and there is no second place for the definition to drift to.

- **Instrument** — Bond, Buyer's Credit, Commercial Loan, Concessional Loan, Equity, Grant, Guarantee, Joint Venture, Line of Credit, Mezzanine, MoU, PPP, Self Funded, Technical Assistance, Unknown.
- **Status** — Pipeline, Approved, Active, Closed, Cancelled, Suspended, Unknown.
- **Beneficiary type** — Public Sector, Private Sector, NGO, Multilateral, Research, Fund, Multi-stakeholder, Individuals, PPP, Unknown.

A row with a `source_value` is a **mapping**: that wording, wherever it appears, becomes that value. A row with a blank `source_value` and `VOCAB` in `review` **declares a value nothing maps to yet** — `Cancelled` and `Suspended` are there because the IATI driver will produce them and the vocabulary should not have to be extended in a hurry when it does. A row with a blank value and `REVIEW` is a wording nobody has ruled on; eight instrument values are in that state.

**Definitions, because the value names do not carry them.**

*Instrument.* **Grant** — no repayment expected, including donations, prizes and non-reimbursable assistance. **Concessional Loan** — softer than market: below-market interest, long maturity, a grace period, or a service charge in place of interest; **IDA credits belong here**. **Commercial Loan** — market terms, including syndicated and senior debt, IBRD lending, and development-policy loans to non-IDA borrowers. **Line of Credit** — a facility drawn against up to a limit. **Buyer's Credit** — finance to the buyer so it may pay the supplier, including export finance. **Bond** — debt raised as a tradeable security. **Guarantee** — a commitment to meet another's obligation on default; no money moves unless called. **Equity** — money for an ownership stake, any round, including limited-partner commitments to a fund. **Mezzanine** — subordinated or convertible debt. **Joint Venture** — a jointly owned vehicle. **PPP** — concession, BOT or similar, private finance and operation of a public asset for a term. **Self Funded** — the recipient's own balance sheet; a funding *source* rather than an instrument, kept because the distinction is worth counting. **Technical Assistance** — expertise or advisory, cash figure or not. **MoU** — *an agreement is on record and its instrument is not*; use only where the source states an agreement and does not state how money moves, never as shorthand for unclear. **Unknown** — the source does not state it.

*Status.* **Pipeline** — proposed, identified or under negotiation; nothing committed. **Approved** — committed, approved or signed, not yet operating. **Active** — operating: implementation under way, facility inaugurated, activities launched, funds disbursing. **Closed** — finished or fully disbursed, and IATI's finalisation stage. **Cancelled** — abandoned before completion. **Suspended** — halted. **Unknown** — not stated.

*Beneficiary type.* **Public Sector** — government at any level, ministry, agency, programme, state-owned enterprise. **Private Sector** — a company receiving on its own account. **NGO** — non-governmental or civil society, including not-for-profit membership and industry associations. **Multilateral** — the AU, a regional economic community, an intergovernmental body. **Research** — university, research institute, think tank. **Fund** — an investment vehicle that will on-invest; one step removed from the ultimate recipient, which is why it is not Private Sector. **Multi-stakeholder** — several types together where no one of them is the beneficiary; a genuine consortium, not a failure to classify. **Individuals** — people rather than organisations. **PPP** — a public-private vehicle receiving as one party. **Unknown** — not stated.

**`PPP` appears in two vocabularies and means a different thing in each** — an instrument in one, a recipient in the other. That is deliberate and worth knowing.

## 2. Rules for writing a deal record

**The three fields take a value from the vocabulary, spelled exactly as the vocabulary spells it.** Nothing else is admissible. This is a change to `wiki/finance-record-spec.md:323-325`, which currently gives the permitted values for all three as `…`, and it overrides `finance-news-driver.md:69` ("nothing is normalised") *for these three fields only* — the rest of the record still keeps the source's own words.

**Where the source says more than the value carries, the extra goes in `## Notes`, never in the cell.** A table cell holds a value. `Concessional loan *(source label, unverified — see Notes)*` is a cell holding a value and a footnote, and it is why one instrument reads as two. So is `IDA grant *(corrected from the source's "Concessional loan"; PAD00070 records an SDR 69.5m IDA grant)*` — that correction is careful work and it belongs in Notes where it can be read, not in a column where it splits the count.

**Never write a sentence in one of these cells.** `Not stated; project's own dates (2023-03-01 to 2024-04-30) have elapsed as of this capture` is a Notes entry with `Unknown` in the cell.

**Never leave one blank.** `Unknown` means the source does not state it; a blank means nobody has looked, and an absence cannot be counted. Today 41 records have no instrument, 50 no status and 75 no beneficiary type, and no one can tell which of the two they are.

**In a value of the form `X — Y`, the later clause governs.** A record reading `Approved — project activities launched 2026-07-29` is **Active**: the approval is the older fact and the launch is the newer one. This is the rule that decides most of the compound statuses.

**Do not carry an IATI code into the cell.** `Standard grant (IATI finance-type 110)` maps to `Grant`; the code, if it is worth keeping, goes in Notes. And **do not infer concessionality from a finance-type code** — IATI 421 is the generic loan code and says nothing about terms.

**A concession is not a concessional loan.** They are false friends and the base has already tripped on it once, on its third-largest commitment.

## 3. The backswing

**Scope: the 1,269 files under `raw/*/` carrying a `## Deal record` section.** Nine of those are retired by merge — no `finance_origin:`, a `retired_deal_id:` and a `cite_through:` instead — and are out of scope; their stale deal tables can be left or stripped, but they reach no output either way.

**Step 1 — apply the three maps.** For each in-scope record, replace the `| Instrument |`, `| Status |` and `| Beneficiary type |` values with the mapped value, matching **case- and whitespace-insensitively**. This is not optional politeness: two of 115 instrument values missed an exact-match map on capitalisation alone, and case is exactly what a writer varies without noticing.

**Where the original wording carried more than the new value does, move that text to `## Notes` in the same edit.** This is the whole of the difference between a mapping pass and a data loss. Roughly 78 records are in that class — the annotated World Bank instrument corrections and the sentence-length values.

**Step 2 — the eight unruled instruments.** `5G spectrum licences`, `Spectrum award (410 MHz)`, `Investment under NTRA data-centre licence`, `Procurement contract award`, `Program-for-Results (PforR)`, `Mixed`, `Funding + technology + technical support`, `Standard loan (IATI finance-type 421)`. Each needs its source read and a ruling: a value from the vocabulary, a new vocabulary value, or — for the spectrum and procurement cases — a decision that these are not deals at all. Record the ruling as a new row in the map.

**Step 3 — the blanks.** 41, 50 and 75 records respectively. Each is either `Unknown` or a value the source does state and nobody extracted. The second kind is worth finding; the first is a one-word edit.

**Step 4 — verify.** Re-run the compile and check the distinct counts in `outputs/non-state-finance/all-nonstate.csv`: instrument 115 → 15, status 24 → 7, beneficiary type 53 → 10, and no blanks in any of the three. A value outside the vocabulary after the pass is a bug in the pass, not a new vocabulary member.

**Step 5 — hold the line.** Add the three fields to whatever lint reads a deal record, testing membership of the first column of the map file. Without it the base is 1,260 records from where it started; the vocabulary only stays true if something checks.

## 4. What this does not settle

**Whether `MoU` and `Self Funded` are instruments at all.** One is an agreement type, the other a funding source. Both are useful and both are honest, and both will absorb records that a second facet would describe better — the MoU bucket especially, since it takes everything where an agreement was announced and the terms were not.

**Whether the spectrum and licence records are deals.** Money flowing *to* the state for a licence is the opposite direction from everything else in the register.

**Whether `Industry association` is civil society.** ICTAM is a not-for-profit membership body of private firms. `NGO` is the best available fit and the case will recur.
