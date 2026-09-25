---
type: spec
reader: cc
title: report-layer-register.md — the register of every Corpus report (report-layer.md §10)
last_reviewed: 2026-08-28
status: in force; Corpus-owned
---

# report-layer-register.md — §10 of `report-layer.md`

## 10. The register

**Two styles exist side by side, and neither is a draft of the other** *(Bill, 2026-09-22)*. Bill's own writing — the OSINT wiki and his essays on data-landscapers.io — is cautiously outspoken, evidence-led and polemical about systems rather than people. Corpus reports use the register below. Never carry one into the other, and never "correct" his style towards this one.

**Corpus editorial register — light touch.** **The evidence speaks; the lens decides what gets noticed and connected, and then gets out of the way.**

- **The spine stays fully disciplined.** The ledger, the tables, every dated figure, the published *Not held* count — script-emitted, cited, explicit about gaps. A reader must always be able to **take the facts and refuse the reading**.
- **The prose stays factual**: dated, attributed, no flash verbs, no staged reveals, no arguing a heading. A report may *connect* facts in a sentence a reader can check against the rows above it. It states the connection; it does not press it.
- **The lens is a quiet set of questions, asked by what gets included.** Who owns the infrastructure, who holds the data and under whose jurisdiction, what dependency a financing arrangement creates, who is vendor and who is regulator. They rarely need to be spoken.
- **A connecting sentence is itself a checkable fact, never an opinion.** One sentence. No charge, no thesis, no verdict. Worked contrast: *the circular of 24 July sets no implementation deadline; the estimates published the next day carry no budget line for the agency named to implement it* — then, at most: *the mandate names an implementing agency the same week's estimates do not fund.*

### Plain English

**Readers come for information, not mood or opinion.** Write plain British English. Terse is fine; flashy is not — no clever lead sentence with the facts after it. `documentation/AI-speak.md` lists examples.

- **Open with the fact.** Who did what, and when. A sentence that sums up a paragraph without stating a fact is cut.
- **Literal words only.** People and bodies act: they publish, approve, block, say, launch. Abstractions do not: compute does not *arrive*, a series does not *move*. No metaphor: *hardened*, *reached dates*, *put a name to the ceiling*, *moved the wrong way*.
- **Name the thing.** No teasers or counting openers: *Two things arrived…*, *The month's largest infrastructure fact was not the state's*.
- **No contrast set-ups.** *X rather than Y*, *not X but Y*, *from opposite ends*. Use a contrast only when the contrast is the fact.
- **No mood words.** *Plainly*, *quietly*, *finally*, *strikingly*, *alarming* — unless inside a quoted source.
- **Don't write about the report or the month.** *Nothing moved at a municipality this month* describes the ledger, not the country.
- **British spelling and usage** — *programme*, *organisation*, *licence* (noun). No American business idiom.

| Not this | This |
|---|---|
| *Compute arrived and so did the questions about what it costs.* A sovereign AI cloud was brought into service… | A sovereign AI cloud was brought into service on 27 August… |
| *Identity and data protection both hardened.* Home affairs blocked… | Home affairs blocked about 300,000 identity documents on suspicion of fraud. |
| *The supervisor said plainly what it cannot do.* | On 18 August the information regulator said it cannot test systems for privacy compliance before launch. |
| *Two things arrived on 7 September that answer the same question from opposite ends.* | A study published on 7 September costs universal household broadband at about R140bn. |
| *On 8 September a ratings agency put a name to the ceiling.* | On 8 September [the agency] said [what it said]. |

**The test for every sentence: could a reader check it against a source or a row?** If not, cut it.

`report-register-check.py`'s tic-scanner reports rather than gates. **Its `headline` group** catches the phrasings of *Plain English*; no drain is run for them — a run rewrites the hits in a block it is already editing. Checks G–M bind unchanged.

**No document in this layer carries a comment section.** The argument belongs downstream, in the published work these reports feed; a comment section leaks its verdict into the body.

**The prose never narrates the ledger.** "Twenty-three rows moved this month" is a fact about the document. Write about the systems.

**The register is against the report's vocabulary, not against the world's.** Case-sensitivity is not enough on its own. The test is whose sentence it is: a term inside `[…](url)`, or naming an instrument, a study, an index band or a defined term, is the source speaking and stands; the same term in the report's bare prose is Corpus speaking, and the rule reaches it.

**A standing hit is not an unfixed one, and no script can tell them apart** — which is why check K reports and a person rules. The floor after the last ruling is 91 hits in five standing categories, not to be ruled again:

- **First person, 27.** Roman numerals (`Phase I`, `Tier I to Tier III`, `NFIS I`, `Diário da República I Série`), catalogue slugs carrying `-us-`, quoted source speech, and Telecom Egypt's brand `WE`. `FIRST_PERSON` already excludes the commonest.
- **`landed`, 4.** A submarine cable is *landed* at a landing station: the industry's word.
- **`ecosystem`, 48**, and **`dematerialis`, 9.** Each is a source's own name for the thing — a study's title, an index's category, a defined term, a francophone administration's word for its programme.
- **`at scale`, 3.** All inside link text rendering a source's sentence.

A drain that leaves the count above zero is finished. The floor moves only when the estate is ruled through again; a run that finds it higher has found new prose to fix.
