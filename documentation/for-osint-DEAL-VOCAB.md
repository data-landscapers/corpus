# DEAL-VOCAB.md

*(Written in Corpus 2026-08-19 for copying to the OSINT repo root as `DEAL-VOCAB.md`. The four lookup files it refers to are in Corpus `lookups/` and go to `C:\OSINT\lookups\` unchanged. Delete this italic note on the way across.)*

Three fields in every `## Deal record` — **Instrument**, **Status**, **Beneficiary type** — have never had a controlled vocabulary, and 1,260 records have been written to whatever the source happened to say. The result is 115 distinct instruments, 24 statuses and 53 beneficiary types, three of them driving filter dropdowns on the public site. This file establishes the vocabularies, states the rules for writing the three fields, and specifies the pass that brings the existing records into line.

## 1. The vocabularies

**`lookups/deal-vocabs.csv` is the authority on what may be written.** One file for all three fields — `field, sort order, value, definition` — so a value is added or reworded in one place and the fields do not drift apart in style as they would across three files. `sort order` is the order the values should appear in on a page or in a filter, which is the lifecycle for status and rough likelihood elsewhere, not the alphabet.

**Three map files say what an old wording becomes**: `lookups/deal-instrument-map.csv`, `lookups/deal-status-map.csv`, `lookups/deal-beneficiary-type-map.csv`, each `value, source_value, review, note`. They are remediation, not vocabulary — after the backswing their job is only to catch a legacy wording arriving late from IATI or a re-ingest.

**The two must agree, and something should check it**: every `value` a map produces must exist in `deal-vocabs.csv` for that field. Thirty-two values, three maps; today they agree exactly.

- **Instrument** — Bond, Buyer's Credit, Commercial Loan, Concessional Loan, Equity, Grant, Guarantee, Joint Venture, Line of Credit, Mezzanine, MoU, PPP, Self Funded, Technical Assistance, Unknown.
- **Status** — Pipeline, Approved, Active, Closed, Cancelled, Suspended, Unknown.
- **Beneficiary type** — Public Sector, Private Sector, NGO, Multilateral, Research, Fund, Multi-stakeholder, Individuals, PPP, Unknown.

A row in a map is a **mapping**: that wording, wherever it appears, becomes that value. A row whose value is blank and whose `review` reads `REVIEW` is a wording nobody has ruled on — eight instrument values are in that state and none in the other two.

**The definitions are in `deal-vocabs.csv`, not repeated here.** Fifteen instruments, seven statuses, ten beneficiary types, one line each. Restating them in this file would be the same mistake the vocabulary exists to fix: two places to change and one of them forgotten.

Four of them carry a rule rather than a description, and those are in §2 below — `Concessional Loan` takes IDA credits, `MoU` is only for an agreement whose instrument is genuinely unstated, `Unknown` is not the same as blank, and `Fund` is deliberately not `Private Sector`.

**`PPP` appears in two of the three vocabularies and means a different thing in each** — an instrument in one, a recipient in the other. That is deliberate and worth knowing before someone tries to merge them.

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

**Step 2 — the eight unruled instruments.** `5G spectrum licences`, `Spectrum award (410 MHz)`, `Investment under NTRA data-centre licence`, `Procurement contract award`, `Program-for-Results (PforR)`, `Mixed`, `Funding + technology + technical support`, `Standard loan (IATI finance-type 421)`. Each needs its source read and a ruling: a value from the vocabulary, a new vocabulary value, or — for the spectrum and procurement cases — a decision that these are not deals at all. Record the ruling as a new row in the map, and in `deal-vocabs.csv` too if it needs a value that is not there yet.

**Step 3 — the blanks.** 41, 50 and 75 records respectively. Each is either `Unknown` or a value the source does state and nobody extracted. The second kind is worth finding; the first is a one-word edit.

**Step 4 — verify.** Re-run the compile and check the distinct counts in `outputs/non-state-finance/all-nonstate.csv`: instrument 115 → 15, status 24 → 7, beneficiary type 53 → 10, and no blanks in any of the three. A value outside the vocabulary after the pass is a bug in the pass, not a new vocabulary member.

**Step 5 — hold the line.** Add the three fields to whatever lint reads a deal record, testing membership of `deal-vocabs.csv` for that field. Without it the base is 1,260 records from where it started; the vocabulary only stays true if something checks.

## 4. What this does not settle

**Whether `MoU` and `Self Funded` are instruments at all.** One is an agreement type, the other a funding source. Both are useful and both are honest, and both will absorb records that a second facet would describe better — the MoU bucket especially, since it takes everything where an agreement was announced and the terms were not.

**Whether the spectrum and licence records are deals.** Money flowing *to* the state for a licence is the opposite direction from everything else in the register.

**Whether `Industry association` is civil society.** ICTAM is a not-for-profit membership body of private firms. `NGO` is the best available fit and the case will recur.
