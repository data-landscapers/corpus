---
type: design-note
title: raw-semantic-search.md — searching OSINT's raw/ by meaning, for the writing
last_reviewed: 2026-09-04
status: design and instructions; the build is a feature and waits for the freeze to lift on 2026-09-27
---

# Searching `raw/` by meaning

*(Written 2026-09-04 from Bill's question — how to search `raw/` as a data lake once Corpus is finished and the writing resumes. §2 is measured against the mirror as it stood that morning, not estimated. The worked example throughout is `raw/2026/2026-08-27-pulse-uganda-uncdf-digital-inclusion-closeout.md` and the class of thing it belongs to: a worthwhile programme that collapses when the donor leaves.)*

## 1. The problem, and the evidence for it

**Keyword search cannot find the article the question started from.** The best hand-written keyword query for "donor exits, project collapses" — about sixty terms across four groups, exit words, funder names, decay words, sustainability words — was written *from* the Pulse Uganda article and scored against all 16,730 documents. The article does not appear in its own results. It scores zero on the exit group, because it never says "closeout" or "phase-out" or "donor exit"; it says the programme "officially closed", that support "ended", that the gains "could disappear".

The individual terms fail in both directions, which is the shape of the problem rather than a flaw in the query.

| Search | Documents |
|---|---|
| `donor exit` | 1 |
| `no longer funded` | 0 |
| `funding ended / ceased / ran out` | 0 |
| `closeout` | 12 |
| `sustainability` | 1,079 |
| `collapse` | 240 |

Either near-nothing, or a thousand hits that are mostly environmental sustainability and the SDGs. There is no keyword that means *a worthwhile thing died when the money left*, because each source invents its own phrasing for it. That is what a meaning-based search is for, and it is the only reason to want one.

**The second question — investments that failed through bad planning, or through donors pursuing their own agendas — is harder still.** Collapse gets *described* in sources. Motive and mismanagement get *asserted, hedged or implied*, and often by us in the `hub_line` rather than by the publisher. Keyword search has almost nothing to grip there.

## 2. The corpus as measured, 2026-09-04

| | |
|---|---|
| Documents in `raw/` (`.md`) | 16,730 |
| Body text, frontmatter excluded | 191.4M characters (~47.8M tokens) |
| Median document | 3,331 characters |
| 90th percentile | 15,153 characters |
| Largest | 3.2M characters |
| Documents over 200k characters | 122 |
| Documents carrying a `hub_line` | 2,225 (13%) |
| PDFs | 747, of which 542 have a sibling `.md` |
| Pieces at ~400 tokens each | ~120,000 |

At 30,000 documents those figures roughly double: ~215,000 pieces, and a vector store of about 840 MB uncompressed or 210 MB compressed. **Both are small.** This is a laptop-sized problem and the design should stay laptop-sized; the reason to reject enterprise search infrastructure is not cost, it is that 16,730 documents and one reader is two to three orders of magnitude below the scale at which it earns its keep.

The 205 PDFs with no sibling `.md` should be checked before any of this is built. If their text was never extracted they are invisible to every layer described below, and no amount of search design fixes a document that isn't there.

## 3. The four parts, in plain language

**A meaning model.** Reads a piece of text and turns it into a long list of numbers standing for what the text is *about*. Two documents making a similar point end up with similar numbers, whether or not they share any words. It runs once over the archive; after that, searching is finding the closest numbers.

**A judge.** The meaning model is fast but rough — it compares a compressed impression of the question against a compressed impression of each document. The judge is slower and reads the question and one document *together*, properly, scoring how well that document answers that question. Far too slow for 30,000 documents, ideal for the best 200. **This is the part that turns "vaguely on topic" into "the right thing at the top", and it is the part most commonly left out.**

**Ordinary keyword search.** For exact things: a decree number, a person, a date, an entity slug. Already available — SQLite's built-in full-text search, nothing to install.

**A merge rule.** Keyword search returns one ranked list and meaning search returns another; this is the short piece of arithmetic that interleaves them. About ten lines, and there is a standard recipe (reciprocal rank fusion) that nobody should improve on.

## 4. Why both halves, and what each stage buys

**Meaning search alone is worse than keyword search at most of what this archive gets asked.** Law numbers, entity names, figures and dates are precisely what embeddings blur. Keyword search alone cannot find an idea expressed in unexpected words, which is §1. Running both and merging is not a hedge; it is the standard architecture, and Exa — whose results prompted the question — say so plainly: the most powerful arrangement combines keyword and embedding methods rather than choosing.

**The order matters and the cheap stage goes first.** Retrieve broadly and roughly — 100 to 200 candidates from the two searches combined — then let the judge re-sort them. Exa compress their vectors hard enough to lose accuracy and treat it as a non-problem because the reranker recovers it. The first stage decides what is in the room; the judge decides the order. Building only the first stage is what produces results that are on-topic and badly ordered, from which people conclude that semantic search does not work.

**What does not transfer from Exa is their model, and it is not needed.** Their distinctive asset is an embedding model trained on link prediction — learning from how people describe a link when they share it — over billions of pages and a GPU cluster. The architecture transfers; the training does not, and at 30,000 documents the architecture is where most of the quality lives.

## 5. What this corpus has that a bought product cannot use

**The `hub_line` is, in miniature, the exact signal Exa trained on.** Their training data is human descriptions of documents. A `hub_line` is a human description of a document — our own account of what a source says and why it matters. It is the ideal thing to search against, and a crude test on 2026-09-04 confirmed it: searching `hub_line` text put the Uganda article second out of 16,730, where searching full bodies excluded it entirely. **Embed the description as well as the document, and let a query match either.** Only 13% of documents carry one, so this supplements the body index rather than replacing it.

**The facets are the filter layer, and they are free.** `places`, `topics`, `entities`, `lens` and `published` are already on every document. Meaning search plus facet filtering — *documents about donor conditionality, Francophone West Africa, since 2023* — is the query shape that makes this worth building, and it is exactly what an off-the-shelf product cannot do, because it has no idea what `places: [DZA]` or `topics: [dpi.pay]` mean. The cataloguing is the asset. The search engine is a commodity.

**One structural seam works today with no new tooling.** The archive holds 31 World Bank Implementation Completion Reports and 60 documents carrying formal outcome ratings. Those are institutional post-mortems in a standard structure — a document-type filter, not a topic search, and immediately usable.

## 6. Where the index lives

**Not in `C:\OSINT`, under any circumstances.** The mirror is read-only and a write there is discarded at the next sync anyway. The index is a *derived view* of `raw/`, which puts it on the Corpus side of the boundary along with everything else CC produces.

**It is derived, and that is the whole of its risk profile.** If it corrupts, drifts, or the approach turns out to be wrong, it is deleted and rebuilt from `raw/`; nothing of record is touched. This is the same relationship Corpus already has to OSINT, and it should be stated in the script's docstring so nobody later mistakes the index for a store.

**Rebuild incrementally on `body_sha1`.** The `files` table already carries a content hash per document, so a refresh re-embeds only what changed. (Note that `index/vault.db` was a zero-byte file on 2026-09-04; that scaffolding needs rebuilding before anything can lean on it.)

## 7. Installation

Windows, PowerShell, Python 3.11 or later. From the Corpus root:

```
python -m venv .venv-search
.venv-search\Scripts\Activate.ps1
pip install sentence-transformers numpy
```

`sentence-transformers` pulls in PyTorch and the model-download machinery; on a machine with no NVIDIA GPU install the CPU build of PyTorch first, from `https://pytorch.org`, or the default install will fetch a CUDA package of several gigabytes for nothing.

**Choose the model pair by what the machine has.** The models download themselves on first use and cache under `%USERPROFILE%\.cache\huggingface`.

| | With an NVIDIA GPU | CPU only |
|---|---|---|
| Meaning model | `BAAI/bge-m3` (~2.2 GB, 1024 dims) | `intfloat/multilingual-e5-base` (~1.1 GB, 768 dims) |
| Judge | `BAAI/bge-reranker-v2-m3` (~2.2 GB) | `BAAI/bge-reranker-base` (~1.1 GB) |

All four are multilingual, which is not optional here: 220 documents are heavily non-Latin and the beat is substantially Francophone, Lusophone and Arabophone. An English-only model such as `all-MiniLM-L6-v2` will fail on those silently, returning plausible rubbish rather than an error.

**No vector database is needed and none should be installed.** At 215,000 pieces the vectors are one NumPy array of about 800 MB, which loads into memory and answers a search by matrix multiplication in well under a second — exact, not approximate, with no index to build, no tuning and no extension to load. Vector databases exist to avoid comparing against everything; comparing against everything is affordable here. Revisit only past a few million pieces.

## 8. Building the index

**Chunk into ~400-token pieces that never cross an `##` boundary.** Documents run from 3,000 characters to 3.2 million, so whole-document embedding would drown the short ones and blur the long ones. Do not split on blank lines alone: the median non-blank line in `raw/` is ten words, because most of them are headings, bullets and blockquote flags.

**Prefix every piece with its own context before embedding it.** A chunk reading *"the Authority declined to publish the figures"* is nearly useless in vector space — no country, no date, no actor. The frontmatter already carries title, publisher, `published`, `places`, `topics` and `entities`, so the prefix is a string concatenation with no model call. **This is the largest single improvement available and it is almost free.**

**Store four things per piece**: the vector, the source path, the character offsets, and enough frontmatter to filter on without reopening the file. Index the `hub_line` separately as its own searchable surface.

**Budget.** First full pass is a few hours on CPU or minutes on a GPU — run it overnight and forget it. Afterwards, refreshes touch only changed documents. A search is effectively instant; the judge adds seconds rather than milliseconds on CPU, so rerank the top 50 rather than the top 200 if that becomes irritating.

## 9. Using it

**Search by document, not by phrase.** A whole document specifies an idea far more precisely than a sentence can, and this is the case that started the question: not an abstract query but the Uganda article. Hand the system a seed document — or better, its `hub_line` — and ask for neighbours. Exa have an endpoint for exactly this and it consistently beats typed queries.

**Then use the good hits as new seeds.** Two or three rounds of that is how the full set of a pattern gets assembled, and it compounds in a way that typing better queries does not.

**When typing a query, describe the ideal document rather than listing keywords.** *"A report describing a digital health programme that declined after donor funding ended"* retrieves far better than *"donor exit sustainability"*. This costs nothing and applies to Exa today, before any of this is built.

**Filter, don't hope.** Put the country, date range or topic in the filter rather than in the query text — the filter is exact and the query text is not.

**Record the survey as a query file.** `queries/` already has a template with frontmatter scoping by place, topic, entity and lens, plus `pending`, `done` and `results`. A search worth running once during a chapter is worth being able to reconstruct in six months; a chat session is not a record.

## 10. Where this sits against the freeze

**This is a feature, not a defect, and it waits.** Nothing is *wrong* — no check passes over nothing, no stamp is impossible; something is *missing*, which under the test in `CLAUDE.md` makes it a feature. It is not one of the commissioned strategic-review tasks and it is not report-layer machinery wearing a script's clothes. **The build therefore starts on 2026-09-28**, which is close to when the writing resumes in any case.

Three things can be done before then without touching the freeze, because none is a process change: check the 205 PDFs with no extracted text; use the ICR and outcome-rating seam, which needs no new tooling; and adopt the describe-the-ideal-document query style with Exa immediately.

## 11. What this does not do

It does not read PDFs that were never text-extracted. It does not know that a 2024 figure supersedes a 2019 one — filter by date when that matters, and note that near-identical restatements of one fact can otherwise fill a result list, which is worth capping per source document. It does not judge whether a source is any good. And it does not replace the wiki: a compiled page that already holds a fact should be read rather than re-derived, which is what compiling was for.
