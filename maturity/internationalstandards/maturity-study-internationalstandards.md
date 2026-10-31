---
type: task
reader: cc
title: maturity-study-internationalstandards.md — the thirty-third maturity study: international standards for information technology and data, in four questions
last_reviewed: 2026-10-13
status: run 2026-10-13 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: internationalstandards

*(Commissioned by Bill on 2026-10-13 as `gov.standards--adoption-of-international-standards`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Whether the country takes the world's standards for information technology and data as its own**: its standards body's membership of the international standards organisations, the international standards it has adopted as national ones, whether public bodies must meet them, and whether the country helps write them. It counts whatever the body or the rule is called.

The study redraws `gov.standards--adoption-of-international-standards`, which as at 2026-08-31 puts 13 countries at stage 2 and two at stage 3, none at 1, 4 or 5, and leaves 39 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| International standards for information technology and data | Adoption of international standards: international standards for information technology and data | `gov.standards--adoption-of-international-standards` |

Anything else the evidence names is `other`, noted and never staged: a system built to an international standard, such as a passport to the aviation specification, payments moved to the ISO 20022 message format or an identity platform on an open-source one; a company's or a data centre's certificate; certification in the country, which the national standards row holds; regional standards and membership of the African or a regional standards organisation; international standards on food, goods or any other field; a regulator's rule for one sector, such as banks; membership of the International Telecommunication Union, which every country holds; a statistical or accounting standard.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is the country's standards body a member of an international standards organisation? | The body is named as a member of ISO, the International Organization for Standardization, or of IEC, its counterpart for electrical technology, in any class of membership |
| 2 | Has the country adopted an international standard on information technology or data as a national standard? | A named ISO, IEC or ITU standard on information technology, information security, software or data, adopted by the standards body as a national standard. One out for comment is not a yes |
| 3 | Must public bodies meet a named international standard? | A law, decree, regulation, directive or circular that names an international standard on information technology or data and requires ministries, agencies or government systems to meet it |
| 4 | Has the country taken part in writing international standards on information technology in the last three years? | A dated source naming the standards body or a public body as a participating member, chair or secretariat of an ISO or IEC committee that writes standards on information technology or data. An observer seat is not a yes |

## 3. The ladders

**International standards for information technology and data**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country belongs to no international standards organisation |
| 2 Preparing | Yes to 1: the standards body is a member |
| 3 Establishing | Yes to 1 and 2: an international standard on information technology or data is a national standard |
| 4 Operating | Yes to 1, 2 and 3: public bodies must meet a named international standard |
| 5 Leading | Yes to all four: the country has taken part in writing such standards in the last three years |

- **A yes to a later question answers the earlier ones**: a national standard carrying an ISO number shows the body adopts from ISO.
- **Questions 1 to 3 have no time limit**: a membership, a standard and a rule stand, with their year, until a dated source says they have gone. Question 4 counts for three years.
- **A statement that the country belongs to no international standards organisation counts for three years.**
- **The class of membership does not change the stage.** Full, correspondent and subscriber members all answer question 1, and the summary says which. This is a change from the row as it stands, which reads the class as a rung: a correspondent member can and does adopt international standards, so the class is not a step on the way.
- **Membership of the African or a regional standards organisation places nothing**, and is noted. So do regional standards a country adopts.
- **A catalogue or a count of adopted international standards is a yes to question 2 only where the source names one on information technology or data.** The row as it stands places Zambia on a count.
- **International standards in other fields place nothing**: food, steel, units of measurement.
- **A system built to an international standard places nothing**, and is noted. The row as it stands places Angola, Burundi and Seychelles on payments moved to ISO 20022, and Mali on its passport.
- **A certificate places nothing**, whoever holds it: certification is the national standards row's.
- **A rule that is modelled on a standard is not a rule to meet it.** Question 3 needs the source to say public bodies must comply with, or be certified to, the named standard.
- **A regulator's rule for one sector places nothing**, and is noted: a central bank requiring a security standard of banks.
- **A rule binding one government system places nothing** *(settled as worded, Bill, 2026-10-31, messages-for-bill 56)*: Guinea's transport order requiring its passenger-data system to meet ISO/IEC 27001 is insufficient; GIN stays unplaced.
- **A national committee that follows an international one is a yes to question 4 only where the source says it takes part as a participating member.**
- **A seat on, or a candidature for, a board of the International Telecommunication Union places nothing.**
- **How many standards are adopted, and whether the country favours open or technology-neutral ones, is not judged.**
- **Two more changes from the row as it stands**: its stage 4 asks for a catalogue, committee seats and a mandate together; its stage 5 is the African Union strategy's end state. Neither is a fact one story can state.

`study.json` holds this as two aspects: `standing` (`adopted`, `member`, `none`) for questions 1 and 2, and `use` (`writes`, `required`, `none`) for 3 and 4.

## 4. The norm

The African Continental Free Trade Area's annex on technical barriers to trade, Article 6(2), commits its parties to develop and promote the adoption or adaptation of international standards, and the African Union's Digital Transformation Strategy asks for technology-neutral rules in line with international norms. Neither names the standards a country should adopt. This study asks whether a country is a member, has adopted such a standard, requires it of government and helps write it; it does not measure a country against either text.

## 5. What the run reads

- **Carried, nothing opened**: the national standards study's facts naming ISO membership or an adopted international standard, matched from their own text. Its 106 documents are not read again unless a question turns on one.
- **Read**: **58 news stories about international standards that no study has read**, in 30 countries; and the 99 stories and 12 texts the current cells cite.
- **Not read**: the long texts and reports, 1,658 of them, and the news that mentions the subject in passing.

## 6. Token ceiling

**30 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13.
- [x] **D2. Read**: 12 facts carried by their own text; then 61 drafters in one fan-out over the 169 documents of §5, for five more. 17 facts in 15 countries.
- [x] **D3. Staged** as at 2026-09-30: 4: 1, 3: 6, 2: 8, none at 1 or 5, and 39 without evidence; no correction; agreement 14 of 15, every staged cell drawn.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**:

- **Stage 4**: Uganda, on its 2026 information security policy, which says it is mandatory for ministries and agencies and requires compliance with ISO/IEC 27001:2022. It is a policy, not a law or decree; held strictly, Uganda has no evidence.
- **Stage 3**: Algeria, the Gambia, Mauritius, Sudan, Eswatini and Zimbabwe, each on a named national standard carrying an ISO number. **The second stager split on Algeria**: its 2026 programme lists `NA ISO/IEC 14651 (NA 13037)` under revisions, read by the parent as an existing adoption.
- **Stage 2**: eight countries, on ISO's register or a source quoting it.
- **Of the row's 13 at stage 2**, Burundi, Seychelles, Tunisia and Zambia are without evidence.
- **39 countries are without evidence**, Kenya, Nigeria, South Africa and Egypt among them: nothing held names their body as an ISO member.
- **No source names a committee**: question 4 is unanswered everywhere.
- **Tokens: about 28 million at the map**, ceiling 30 million, step 1 included.
## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
