---
type: design-note
title: exa-highlights-assessment.md — what Exa's highlights would and would not save the progress filler
last_reviewed: 2026-09-02
status: assessment for the post-freeze queue; two in-freeze defects named in §6
---

# Exa highlights, measured against the filler as it actually runs

*(Written 2026-09-02 from Bill's question — the Exa Highlights post of 22 April 2026, the Dynamic Highlights preview of 28 August, and whether either bears on the `agent_run` route now that the filler has become expensive. The verdict changed once the whole series was counted rather than the three archived cost write-ups, and §2 is that correction.)*

## 1. The verdict in one paragraph

**Highlights are worth adopting, but not for the reason the ZAF cost record suggests, and the saving is smaller than that record implies.** The large fetch-amplification highlights would have cut was already cut, by §4a's cap and §2's objective form, in the second run of the series. What remains is a quality argument rather than a token one: today's selection is made from the Agent's own descriptions of candidates, which §3 already forbids the run from trusting on dates, and highlights would let the same selection be made from the pages' own words at roughly the context cost of the descriptions. Dynamic Highlights additionally attacks the one waste the record names as dominant — one event staged many times — and is the piece worth a measured trial. None of it touches the capture rule: a highlight is a lead, never a body.

## 2. The correction — ZAF is not the process

The three archived cost write-ups cover runs one to three. The series is now 33 runs, and every run CSV under `logs/progress-filler/` survives even though the per-country write-ups were deleted on 2026-09-01, so the whole series can be counted rather than sampled.

| | 33 runs | per gap |
|---|---|---|
| Gap indicators worked | 2,135 | — |
| `agent_run` briefs at `effort: medium` | 4,272 | 2.00 |
| Candidates returned | 16,626 | 7.79 |
| Fetched | 6,355 | 2.98 |
| Staged selections | 5,617 (2,073 baseline + 3,544 progress) | 2.63 |
| Recorded unselected | 3,998 | — |
| Dropped | 1,405 | — |
| `nil` outcomes | 12 | 0.6% |

**ZAF fetched 14.7 documents per gap. Every run since has fetched about 2.9.** Excluding ZAF and ERI — whose CSV is empty in these columns, §6 — the series fetched 5,708 documents against 1,983 gaps, and returned 7.9 candidates per gap to do it. The sub-agents are therefore already choosing roughly three candidates out of eight *before* fetching, and the fetch is close to the floor the cap sets: one baseline and two progress items is three, and 2.98 is what three looks like once some indicators fall short.

**So the "fetch everything, then select with the bodies in hand" pattern that §4a was written to describe is not what the run now does.** §4a says the cap is applied with bodies in hand, and on ZAF it was; in practice the sub-agents have moved the decision upstream of the fetch and apply it to the Agent's lead list. That is cheaper, and it is also a quieter change to the procedure than it looks, because it means the cap is now applied to *descriptions of documents* rather than to documents.

**The consequence for this assessment is direct.** A highlights-first selection tier cannot save 500 fetches a country, because those fetches stopped happening after run one. What it can do is put evidence under a decision currently made on the Agent's say-so.

## 3. What highlights actually offer

**Selection on the page's own words, at about the cost of the lead list.** Exa's claim is 500 characters of highlights matching the accuracy of the first 8,000 characters of the page, and 4,000 characters beating 32,000 of full text; the Contents API prices highlights at $1 per 1,000 pages and they are free on `/search` up to ten results. Eight candidates a gap at a few hundred characters each is comparable in context to the eight-item lead list the sub-agent reads today, and it is query-conditioned against the indicator rather than against whatever the Agent decided the item was about.

**Two of the record's named failure classes are decided at exactly this point.** The wrong-object rejects — general-government MoUs under a finance MoU indicator, Earth-observation posts under a meteorological satellite indicator — are the selector believing a title. So is the capture-defect class: a "statute" that turns out to be a 877-character record page is visible in a highlight and invisible in a lead description. Neither is a fetch-volume problem; both are a *what got fetched* problem, which is where the week is actually lost, because a wrongly chosen fetch is also a wrongly staged file and therefore OSINT ingest work spent on nothing.

**Dynamic Highlights is the piece aimed at the dominant waste.** ZAF's finding was one-event-many-files — 410 of 536 excluded, five records of one police budget vote, three of one Mashatile visit, eight CIPC notices of a kind — and §4a's hardest instruction is *two distinct events, never two reports of one event*. Dynamic Highlights allocates a single shared budget across the result set with awareness of the other documents, giving redundant pages fewer tokens or none; Exa report a 40% token gain with a 3.8% quality increase single-turn, and 30% fewer agent tokens with a 2.1% quality gain agentic. That is the same judgement the selector makes by hand, made upstream.

**With a caveat that has to be stated.** A page starved to zero tokens is an assertion of redundancy, and a run that acts on it is trusting the allocator rather than checking. It is a research preview behind the `Exa-Beta: dynamic-highlights-2026-08-28` header, it must not be combined with `maxCharacters`, and the correct trial is one country run both ways against its own `-unselected.csv`, which records every excluded candidate with its URL and is exactly the ground truth this comparison needs.

## 4. What highlights do not offer

**They are never a capture.** `wiki/capture-rule.md` requires the full verbatim body, never an excerpt or a synthesis, and highlights are a synthesis by construction. They sit on the selection side of §4a alongside the Agent's leads and are never written to `new-queue`. This is a reason to adopt them, not a caution against it: they occupy a slot the procedure already has, and they do not move the line between leads and evidence at all.

**They do not reduce the staged fetch.** 5,617 selections had to be captured verbatim and would still have to be. That volume is the product, not overhead.

**They do not reduce `agent_run` count or spend.** 4,272 briefs at `$0.10` is about $427 across the whole series — real but not the constraint §7 names, and unchanged by anything in this note.

## 5. The effort level, which is the untested knob

**`effort: medium` has never been compared with anything.** Fixed-effort pricing runs minimal $0.012, low $0.025, medium $0.10, high $0.50, x-high $1.00. Twelve nils in 2,135 gaps says medium is finding what is there; it says nothing about whether low would find the same, because low has not been run.

**The test is cheap and the ground truth already exists.** One country, one Level-1 chapter at `low` against the same chapter at `medium`, compared on candidates returned, selections made and — the number that matters — how many of the medium run's *staged* items the low run also found. The unselected registers make it auditable after the fact without a re-run. This is a post-freeze item.

**A note against over-reading the nil count.** GNB's record shows the Agent doing genuine research — finding that the most authoritative instrument in existence is a draft, a terms of reference or a donor project document, and evidencing that a *projeto* never reached the *Boletim Oficial*. That is not a lookup, and a cheaper effort level may not do it. The trial should be read on the hard chapters, not the easy ones.

## 6. Two defects found while measuring, both fixable inside the freeze

These are *wrong*, not *missing*, and they are in the report layer's own machinery, so both exemptions apply.

**`ERI-2026-08-31.csv` is empty in five of its twelve columns, for all 108 rows.** `candidates_returned`, `fetched`, `not_selected`, `dropped` and `subject_rows_at_probe` are blank throughout. Two things follow. §7's claim that the cap is auditable from the run CSV alone is false for ERI. And §0's re-run policy reads `subject_rows_at_probe` to decide whether a prior nil is skipped or re-opened, so ERI's rows cannot be adjudicated by it at all — a later run has no recorded count to compare against and must re-buy the whole country. `ZMB-2026-08-29.csv` has the same fault on 7 of 65 rows. Whether the fields can be reconstructed from the selected and unselected registers has not been checked.

**`MDG-2026-08-31.csv` carries `outcome: partial`, which is outside §7's closed set.** The set is `staged` / `nil` / `skipped-prior-nil`. One row, `include.access--citizen-feedback-portals`. It reads as an indicator that staged a baseline and no progress item, which is `staged` — the cap is a maximum, not a quota, and §4a says so. An invented value in a closed vocabulary is the failure mode the closed vocabulary exists to prevent.

**A third thing that may be a defect and has not been established.** ZAF recorded 169 of 536 bodies as `excerpt` and two statutes captured as sub-3k landing pages. The Exa fetch tool exposed to a Cowork session defaults to `maxCharacters: 3000`. If the filler's fetch route carries the same default then the excerpt rate is a mechanism rather than a property of the pages, and a truncated capture staged as a body is a falsified record under a citation that checks out. **This has not been verified** — it needs the filler's own MCP configuration read, which this assessment did not do.

## 7. What to do, and when

**Now, inside the freeze**: the two defects in §6, and establish whether the `maxCharacters` default is real.

**Post-freeze, from 2026-09-28**, in this order:

1. **Reconcile §4a's text with what the run does.** The procedure describes selection with bodies in hand; the run selects from lead descriptions. Whichever is right, the file should say it, because the justification in *Why this is not the value-drop sweeps are forbidden* rests on holding the bodies.
2. **A highlights tier between the Agent and the fetch** — highlights for every candidate, full capture only for the survivors. This is where §4a's evidence claim becomes true again, at a context cost comparable to today's lead list.
3. **A Dynamic Highlights trial on one country**, scored against that country's existing `-unselected.csv`.
4. **The effort-level A/B**, one chapter, low against medium.

**One practical obstacle to (2) and (3).** The Exa MCP surface available to a Cowork session exposes no `highlights` parameter and no `dynamic` flag — `web_search_exa` takes a query and a result count, `web_fetch_exa` takes URLs and `maxCharacters`. Whether the MCP the filler runs against is the same one has not been checked. If it is, this is an API-side change rather than a parameter change, which is a further reason it is post-freeze work rather than a tweak.

## 8. What is unverified

The 33-run aggregate is computed from the run CSVs and is only as good as they are — §6 is the known part of that. The claim that sub-agents now select before fetching is inferred from the fetch-per-gap ratio, not from reading a sub-agent's transcript. Exa's eval numbers are theirs, restated, and nothing here reproduces them. Nothing in this note was run against the API.

*Sources: [Exa Highlights](https://exa.ai/blog/highlights-for-agents) (22 Apr 2026), [Dynamic Highlights](https://exa.ai/blog/dynamic-highlights) (28 Aug 2026), [Contents API guide](https://exa.ai/docs/reference/contents-api-guide), [Exa pricing](https://exa.ai/pricing); `PROGRESS-FILLER.md` §§0, 2, 3, 4a, 7; `logs/progress-filler/*.csv`; `documentation/archived/progress-filler-cost-{ZAF,AGO,GNB}.md`.*
