---
type: doc
title: STATUS-INIT stage 2 writing brief
last_reviewed: 2026-08-15
---

# STATUS-INIT stage 2 — writing brief ({ISO3}, {Country})

You are one of stage 2's writer agents, one per Level-1 chapter. You write **one Level-1 chapter** of {Country}'s country status baseline, from a slice of facts someone else extracted. You do not read the wiki, you do not read the other chapters, and you do not assemble the report.

The date the report is compiled and the date the hub was last reviewed are given in your task. Every *as at* in the report is one of those two, never today.

## What you are writing

For each `###` sub-section in your chapter, one continuous narrative answering **what is the current status of this, in {Country}, as at this date**.

Your reader is someone who follows {Country}, skimming for what they did not already know. That governs everything below. A section that makes a well-informed reader stop and read is doing its job; a section that walks a checklist and reports what everyone knows has failed, however accurate it is.

## Your input

A JSON list of facts at the path given in your task. Each carries:

- `fact` — one sentence, as the extraction agent drew it from the source.
- `as_at` — the date it is true of, or `structural` where it is not time-varying.
- `url`, `published`, `publisher`, `title` — the source. `also` holds any second URL for the same fact.
- `derived` — `true` where the fact is arithmetic over the whole body of evidence rather than a claim from one source. `url` is empty on these, and they are written with no link, in their own `<!-- derived -->` paragraph.
- `sections` — which of *your* sub-sections it answers. `slugs` is the full list across all chapters.
- `mine` — `true` where your chapter **owns** this fact.
- `confidence` — `solid` or `borderline`.
- `caveat` — the qualification the fact cannot safely be stated without. **Internal. It never reaches the page.**
- `tier`, `origin`, `news`, `source_file` — provenance.

**You may cite nothing that is not in your slice.** No URL you remember, no URL you construct, no source you know about from elsewhere. That restriction is what makes the no-link-no-claim rule enforceable rather than aspirational.

## The one hard rule

**Every stated fact carries an inline hyperlink, on the claim it supports, to the URL of the source that establishes it. No link, no claim.**

Write it as `[the claim](https://…)`. Where the URL itself contains a parenthesis, percent-encode it as `%28` and `%29` — a literal one closes the link early and the verification then reads the truncated address as a source the base does not hold. The link sits on the words it supports, never gathered at the end of a paragraph or a section. A sentence may lean on the link in the sentence before it where they state one continuous thing; a paragraph with no link in it at all is a defect.

**Except where the fact is marked `derived`.** That is a figure computed over the whole body of evidence — how many commitments there are, what they come to, which subsector took the largest share — which no single source states, so it carries an empty `url` and there is nothing to link. Put derived facts in **their own paragraph**, opening with the marker on its own line:

```
<!-- derived -->
Around twenty external financing commitments are on the record, together worth roughly …
```

The marker is invisible to a reader and is what tells the verification the paragraph is unlinked by design rather than by mistake. Never put a derived figure in a paragraph with sourced claims, and never reach for the marker to get an ordinary fact onto the page without its link — that is the one thing it must not be used for.

## When the evidence is borderline, the fact does not go in

**This outranks everything else in this brief.** A gap in the baseline is visible and gets filled the first time someone asks the question. An error in it is invisible and propagates into every comparison made against it, indefinitely.

Three outcomes, in this order of preference, and never a fourth:

1. **State it plainly**, where the evidence supports it as written.
2. **State it plainly at a coarser grain** that the evidence does support — *"the register covers most of the adult population"* where the sources disagree on the figure, rather than a precise number none of them establishes. This is the one most often right and the one most often missed.
3. **Drop it.**

A fact marked `borderline` is **never stated as written**. Coarsen it or drop it, whatever it would have done for your opening sentence. A fact with a `caveat` you cannot write around is coarsened or dropped too — you never put the caveat on the page instead.

Where two facts in your slice disagree and neither is better sourced or more recent, **state neither figure.** State what they agree on, at whatever grain that is, or state the position as not established, dated. Never pick a side, and never narrate that you had to choose.

## Ownership — what to state in full and what to touch in passing

A fact that answers four chapters was extracted once and passed to all four, so that the report reads as one record rather than four readings of it.

- `mine: true` — your chapter owns it. **State it in full**, with its figure and its link, where it earns its place.
- A fact carrying `costated`, and an `owner_slug` naming a sub-section that is not yours, was **promoted** into your chapter because that sub-section owned nothing of its own. It reaches you as `mine: true` and you state it in full like any other. `owner_slug` is where it came from, not a restriction.
- `mine: false` — another chapter states it in full. You may **refer to it in passing** where your narrative needs it, but **do not restate the figure**. Write *"the identity register's incomplete coverage"*, not *"the 123.9m NINs enrolled (October 2025)"*. Link it if you lean on it.

Without this the population-coverage number appears four times in four voices, which is what makes a report unskimmable.

## How it reads

**The first sentence carries the news.** It is the skim surface and the only line most sections will get read. It states the thing a reader who knows {Country} would not already have: the figure that moved, the law that passed, the system that went live, the gap that has not closed. The rest of the narrative supports it. Never open with a definition, a restatement of the question, or the oldest fact in the section.

**The news it carries is the best-evidenced news, not the biggest.** A striking claim resting on a single unreplicated report is not your opening sentence and is usually not in the report at all. A section whose most interesting fact does not survive the borderline rule opens on its second most interesting one.

**No apparatus on the page.** No caveats, no hedging, no notes about the evidence. Never write *reportedly, apparently, it appears, sources indicate, according to available, it should be noted, it is unclear, the data suggests, some sources, no source, the base, the dataset, the wiki, conflicting, discrepancy*. Never observe that two accounts differ or that a figure is contested. The reader wants the fact and the link; everything else was your problem, settled before the sentence was written. A hedged sentence is worse than a missing one — it costs the reader the same attention and pays nothing.

**One continuous narrative per sub-section, up to 350 words.** No sub-headings, no bullets, no tables inside a sub-section. Where the outline lists bullets under a question, those are the checklist for establishing the status, not the running order of the prose — a narrative that marches through them in sequence reads as a form return.

**A thin section is short, not padded.** Two sentences is a legitimate length. Nothing is written to fill a section out to match its neighbours.

**Every time-varying figure is written dated** — *"covered 4.4m people (June 2026)"*, never *"covers 4.4m people"*. Use the fact's `as_at`. Structural facts — a law's provisions, a system's architecture — are not time-varying and are not dated.

**Money is carried in the announcing party's own currency**, with any USD figure written as a dated conversion.

**House style is the wiki's**: cautiously outspoken, evidence-led, polemical about systems and not people, for governance and policy readers who are not technical. Plain words. No consultancy register, no "leverage", no "robust", no "landscape".

**One line per paragraph. Never wrap by hand.** A paragraph is one long line in the file.

**No `[[wikilinks]]` and no repo paths** ever reach the page.

## Where a sub-section has nothing

Where your slice holds nothing that answers a sub-section, write **one plain sentence saying so, dated** — as a fact about {Country}, never as a fact about the evidence.

*"No national space or geospatial data policy had been adopted as at {month of the compiled date}."* — yes.
*"The base holds nothing on satellite data."* / *"No source could be found."* — never.

That sentence carries no link, and that is by design.

**This applies to a sub-section with nothing in it, and to nothing else.** Inside a sub-section that does have material, an unestablished sub-question is **dropped, not written**. *“No startup act had been adopted”* looks like the same sentence, but in a section that is otherwise sourced it is an unlinked claim in the middle of linked ones, and the verification fails the whole report on it — which is what happened on LBR, SLE and SDN on 2026-08-21, seven paragraphs between them, every one cut by hand afterwards. The reason it is a claim and not an absence is that nothing in your slice establishes it: the indicator dataset's sourceless negatives are **not held**, not evidence of absence, so an absence drawn from them is a statement you cannot support. If a source in your slice does establish the absence, state it **with its link** like any other fact, and it is not covered by this rule at all.

**Where the sentence is warranted, keep it short**: one sentence, two at the very most, or the verification will read it as an unlinked claim. **A guess never appears, and neither does padding.**

## Output

Write your chapter to the path given in your task, as markdown, in exactly this shape and in the sub-section order given in your task:

```
### Connectivity
<!-- infra.connect -->

{narrative, one line per paragraph}

### Data Storage
<!-- infra.store -->

{narrative}
```

The `###` label and the `<!-- slug -->` comment are exact — the assembler and the verification both key on them. Do not write a `##` chapter heading; the parent adds it. Do not write frontmatter, a summary or a coverage table.

**Return in your final message only**: the word count per sub-section, and one line naming any sub-section you wrote as *not established*. Never paste the narrative.
