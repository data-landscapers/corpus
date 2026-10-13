---
type: task
reader: cc
title: maturity-study-interoperabilitystandards.md — the thirty-first maturity study: the technical standards government systems are built to, in four questions
last_reviewed: 2026-10-13
status: prepared 2026-10-13; waits for Bill's word on the questions; nothing run
---

# Maturity study: interoperabilitystandards

*(Commissioned by Bill on 2026-10-13 as `gov.standards--national-interoperability-standards`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The technical standards the government sets for its own systems so that they can exchange data**: the data formats, codes, interfaces and protocols a system must use, whatever the document is called and whatever larger thing it sits in. A standards catalogue, the technical part of an interoperability framework or e-GIF, a set of government ICT standards, the technical standards of a government enterprise architecture, a government standard for programming interfaces or for data.

The study redraws `gov.standards--national-interoperability-standards`, which as at 2026-08-31 puts 18 countries at stage 2, 14 at stage 3 and two at stage 1, none at 4 or 5, leaves 19 unplaced and holds no cell for Seychelles. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Technical standards for government systems | National interoperability standards: technical standards for government systems | `gov.standards--national-interoperability-standards-technical-standards-for-government-systems` |

Anything else the evidence names is `other`, noted and never staged: an interoperability framework with no source saying it sets technical standards, which the interoperability framework row holds; a data exchange platform; standards for one sector only (health, statistics, land); a standard for one function, such as information security, electronic signatures, identity checks or payments; the telecoms regulator's equipment standards; a law on data sharing; a digital strategy that names standards as an aim.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Are there technical standards for government systems to exchange data, or are they being written? | A named set of standards being drafted, out for consultation, or published. A stated intention with no drafting begun is not a yes |
| 2 | Have they been published? | Issued by the government, the agency responsible or the national standards body, and not withdrawn or replaced by nothing |
| 3 | Are public bodies required to use them? | A law, decree, regulation or circular that makes the standards compulsory for the systems public bodies build or buy |
| 4 | Has a system been checked against them in the last three years? | A dated source naming a public body, system or product tested, audited or certified against the standards, or giving a count of them |

## 3. The ladders

**Technical standards for government systems**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the government has no technical standards for its systems to exchange data and none are being written |
| 2 Preparing | Yes to 1: standards being written |
| 3 Establishing | Yes to 1 and 2: standards published |
| 4 Operating | Yes to 1, 2 and 3: public bodies are required to use them |
| 5 Leading | Yes to all four: a system has been checked against them in the last three years |

- **A yes to a later question answers the earlier ones**: a system certified against the standards shows they are published.
- **Questions 1 to 3 have no time limit**: published standards stand, with their year, until a dated source says they have been withdrawn. Question 4 counts for three years.
- **A statement that there are no standards counts for three years.**
- **An interoperability framework counts only where a source says it sets technical standards.** One adopted with nothing said of its standards is the framework row's, and is noted. Where one document does both jobs it is counted in both rows.
- **A set of government ICT standards counts where a source says it covers how systems exchange data.**
- **A government enterprise architecture counts on the same test.**
- **An exchange platform places nothing**, however many bodies are connected. The published specification a system must meet to connect to it counts.
- **Standards for one sector or one function place nothing**, and are noted. This is one change from the row as it stands, which places Kenya on two health guides.
- **A mandate to write standards is not standards being written**; a version 0.1, or an edition with its approval left blank, is a draft. Both as ruled in the framework study.
- **A text that says of itself that it is compulsory is not an instrument making it so.**
- **Standards published with a later starting date are a yes to question 2**, and the summary gives the date.
- **A general check of a body's ICT counts for question 4 only where the source says it was against the standards.**
- **How good the standards are, and whether they are open or international ones, is not judged.** The African Union's interoperability framework is noted and does not change the stage.
- **Two more changes from the row as it stands**: its stage 4 asks for a mandate, a custodian and conformance testing together; its stage 5 is the African Union strategy's end state. Neither is a fact one story can state.

`study.json` holds this as two aspects: `standing` (`published`, `draft`, `none`) for questions 1 and 2, and `use` (`checked`, `required`, `none`) for 3 and 4.

## 4. The norm

The African Union's Digital Transformation Strategy asks for technical standards for checking identity in dealings between government, business and citizens, built on open standards; its interoperability framework names international ones. This study asks whether standards exist, are published, are compulsory and are checked; it does not measure them against either.

## 5. What the run reads

- **Carried, nothing opened**: the 30 facts the interoperability framework study holds that name standards, matched to the questions from their own text. The 186 documents that study read are not read again.
- **Read**: **four news stories about the standards**, in four countries; the 79 stories the current cells cite, and the 17 texts they cite only for a country with nothing else; then, for a country still short of an answer to question 1 or 2, one call of the news that mentions the subject in passing, from 150 stories.
- **Not read**: the long texts and reports, 207 of them. **No web search and no handover to OSINT.**

**The news held seldom makes standards its subject.** Most countries will be placed on what the framework study already holds, and many will print *Not held*.

## 6. Token ceiling

**30 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Read**: carry by text, then the reading of §5.
- [ ] **D3. Stage** as at 2026-09-30, with the parent's corrections and the agreement check.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
