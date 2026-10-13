---
type: task
reader: cc
title: maturity-study-qualitystandards.md — the thirty-second maturity study: national standards for information technology and data, in four questions
last_reviewed: 2026-10-13
status: run 2026-10-13 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: qualitystandards

*(Commissioned by Bill on 2026-10-13 as `gov.standards--national-quality-standards`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The country's own standards for information technology and data, and whether anyone is certified against them**: the body the law gives the job of writing national standards, the standards it has issued on information technology, information security, software or data, and certification against them. The body counts whatever it is called: a bureau, an institute, an agency, a council.

The study redraws `gov.standards--national-quality-standards`, which as at 2026-08-31 puts 27 countries at stage 2 and six at stage 3, none at 1, 4 or 5, leaves 20 unplaced and holds no cell for Benin. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| National standards for information technology and data | National quality standards: national standards for information technology and data | `gov.standards--national-quality-standards-national-standards-for-information-technology-and-data` |

Anything else the evidence names is `other`, noted and never staged: a national quality policy; the telecoms regulator's quality-of-service rules and its approval of equipment; national standards on food, goods or any other field; a quality management standard such as ISO 9001; standards a ministry sets for one sector; the technical standards government sets for its own systems, which the interoperability standards row holds; membership of the international or African standards organisations, which the international standards row holds; a company's certificate from a certifier abroad.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a national standards body? | A body set up by a law or decree to write or adopt national standards. One announced and not yet created is not a yes |
| 2 | Has it issued a national standard on information technology or data? | A named standard on information technology, information security, software or data, issued or adopted as a national standard. A standard out for comment is not a yes |
| 3 | Can an organisation be certified against one in the country? | The standards body, or a certifier accredited in the country, offers certification against such a standard or has certified an organisation against it |
| 4 | Has a public body been certified in the last three years? | A dated source naming a ministry, agency or state-owned body, or one of its systems, certified against such a standard by the standards body or a certifier accredited in the country |

## 3. The ladders

**National standards for information technology and data**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no national standards body |
| 2 Preparing | Yes to 1: a standards body exists |
| 3 Establishing | Yes to 1 and 2: it has issued a national standard on information technology or data |
| 4 Operating | Yes to 1, 2 and 3: certification against one is on offer in the country |
| 5 Leading | Yes to all four: a public body has been certified in the last three years |

- **A yes to a later question answers the earlier ones**: a certificate from the standards body against a national standard shows the standard is issued.
- **Questions 1 to 3 have no time limit**: a body and a standard stand, with their year, until a dated source says they have gone. Question 4 counts for three years.
- **A statement that there is no standards body counts for three years.**
- **Another body counts for question 2 where the law gives it the power to set national standards for information technology**, such as a national information technology agency.
- **An international standard adopted as a national one is a yes to question 2.** Whether a country's standards are international ones is the international standards row's and is not judged here.
- **A catalogue or a count of national standards is a yes to question 2 only where the source names one on information technology or data.** A catalogue said to hold none is a no, with its year.
- **A national quality policy places nothing**, and is noted. This is a change from the row as it stands, which puts Burundi at stage 3 on its policy.
- **The telecoms regulator's quality-of-service rules place nothing**, and are noted. The row as it stands puts Lesotho at stage 3 on them.
- **A standard for one sector's data places nothing unless the standards body issued it as a national standard.**
- **A certificate from a certifier abroad places nothing**, and is noted: it shows the organisation met an international standard, not that the country can certify.
- **A source that names no certifier is not a yes to question 3 or 4.**
- **Accreditation to certify quality management only is not a yes to question 3.**
- **How good the standards are is not judged.**
- **Two more changes from the row as it stands**: its stage 4 asks for a policy, accredited certifiers and certified government bodies together; its stage 5 is the Pan-African Quality Infrastructure's end state. Neither is a fact one story can state.

`study.json` holds this as two aspects: `standing` (`published`, `body`, `none`) for questions 1 and 2, and `certification` (`public-body`, `offered`, `none`) for 3 and 4.

## 4. The norm

The Abuja Treaty, Article 67, commits member states to a common policy on standardisation and quality assurance, and the African Union's ministers of industry in 2013 named the Pan-African Quality Infrastructure as the continent's platform for standards, measurement and accreditation. Neither says what a country's standards for information technology or data should be. This study asks whether a standards body exists, whether it has issued such a standard, and whether certification is on offer and used by government; it does not measure a country against either text.

## 5. What the run reads

- **Carried, nothing opened**: the frame's 33 placed cells for this row, matched to the questions from their own text. No earlier study holds facts on the subject.
- **Read**: **86 news stories about standards bodies, national standards and certification that no study has read**, in 40 countries; and the 105 stories and 30 texts the current cells cite.
- **Not read**: the long texts and reports, 407 of them, and the news that mentions the subject in passing. **No web search and no handover to OSINT.**

**Most countries will stop at stage 2.** A standards body is on record nearly everywhere; a named standard on information technology or data is held for few, and those countries will print *Not held* for question 2.

## 6. Token ceiling

**30 million.** The run checks after every fan-out and stops at it. The figure is the interoperability standards study's cost, which read about as many documents.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13.
- [x] **D2. Read**: 96 calls in one fan-out over the 221 documents of §5; 100 facts in 40 countries. Nothing was carried without reading: the cells' sources were read as documents.
- [x] **D3. Staged** as at 2026-09-30: 5: 1, 4: 1, 3: 6, 2: 32, none at 1, and 14 without evidence; one fact revalued by the parent (`corrections.csv`); agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**:

- **Stage 5**: Mauritius, whose standards bureau's register lists six public bodies certified against the national information security standard at the end of 2025. **Stage 4**: Zimbabwe, whose standards association was accredited in February 2026 to certify against the same standard.
- **Stage 3**: Algeria, Egypt, the Gambia, Sudan, Eswatini and South Africa, each on a named national standard; Egypt's is on metering data and Eswatini's on address data.
- **Zimbabwe's association rests on no law**, by the 2021 quality policy's own account. The later yes answers question 1; held strictly, the cell would be unplaced.
- **Zambia is stage 2**: its bureau says it has standards on information technology and names none.
- **Tanzania is stage 2**: the one source naming a standard on information technology is dated after the as-at.
- **Four countries the row has at stage 3 are at 2**: Angola and Rwanda on a catalogue or gazette that names no such standard, Burundi on its quality policy, Lesotho on telecoms rules.
- **Fourteen countries are without evidence**, Nigeria, Morocco, Ethiopia, Senegal and Côte d'Ivoire among them: nothing held names their standards body.
- **A fact dated by year or month after the as-at counts where its source was published by it**, as the stager brief has it; this places São Tomé and Príncipe.
- **Tokens: about 35 million at the map**, ceiling 30 million, step 1 included. The one reading fan-out took 28 million. **The summaries were written by the parent.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
