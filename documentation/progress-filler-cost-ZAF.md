# Progress filler — cost investigation, ZAF, 2026-08-26

*(The first run of `PROGRESS-FILLER.md`. Bill's design was run **as specified and unmodified** —
two briefs per gap at `effort: "medium"` — because the point was to price that design, not a
cheaper one. Batch label `progress-filler-ZAF-2026-08-26`. Run CSV:
`logs/progress-filler/ZAF-2026-08-26.csv`.)*

## The headline

**Every gap had evidence to find. 44 of 44, zero nils.** Not one of the 44 indicators reading
***No evidence*** on the published ZAF progress report was a searched absence; every one was a
collection absence. The report's own legend says the value is *"a statement about this base, not
about the country"* — this run is the first measurement of how often that caveat is doing real
work, and for ZAF the answer is every single time.

**The money is not the constraint.** 88 `agent_run` calls at $0.10 came to **$8.80**, against a
haul of 536 staged documents. The constraint is what those 536 documents cost *downstream* —
fetching, screening, and then OSINT's ingest adjudicating every one of them.

## What it cost and what it returned

| | |
|---|---|
| Gaps worked | 44 of 44 (no skips — no prior run) |
| `agent_run` calls | 88 — 2 per gap, `effort: medium`, design unmodified |
| Agent spend | **$8.80** at $0.10/call |
| Wall clock | **~32 minutes**, five sub-agents concurrent |
| Agent-time consumed | ~132 sub-agent-minutes |
| Candidates returned | 1,006 |
| Fetched | 647 |
| Staged by sub-agents | 584 |
| Removed by parent as cross-agent duplicates | 48 |
| **Staged, final** | **536** files, 536 distinct URLs |
| Dropped at screening | 397 |
| `nil` indicators | **0** |

**Yield: 12.2 staged documents per gap, 61 per dollar of Agent spend.** Per-indicator range 2 to
20; the thinnest was `gov.legislate--statistics-legislation` at 2, and it was thin because both
of its key gazettes refused the fetcher, not because nothing exists.

**Capture quality**, which is what ingest inherits: 367 `full` bodies, 169 `excerpt`. Dates from
the page itself in 349 cases, `proxy` in 187 (35%), each naming its proxy basis in `note`.

**Drop codes**, by how many of the 44 indicators used each: `duplicate-in-run` 37 ·
`headline-only-stub` 27 · `already-seen` 20 · `fetch-blocked` 12 · `off-topic` 11 · `url-dead` 5 ·
`no-development` 4 · `out-of-window` 1. No code was invented; one use of `no-development` was
noted as a stretch (a trade site re-hosting a DHET gazette, which no code covers).

**The origin screen found nothing.** Roughly 250 domains screened across the five batches, **zero
`DROP` verdicts** — the material this frame asks for is overwhelmingly government and regulator
primary source, which is not where the hostile shapes live. So no `progress-filler-drop-list.csv`
was created and §8's note is `[FYI]`, not `[ACT]`. That is a finding about the route, not an
absence of diligence: this sweep will rarely have origin adjudications to hand over.

## The scale-out arithmetic, and why $470 was the wrong number

`PROGRESS-FILLER.md` §7 estimated a full pass at 54 × ~44 × 2 ≈ 4,700 calls ≈ $470, using ZAF's
gap count. **ZAF is the best-covered country in the base, so 44 is the floor, not the average.**
The only other unit with a mapped frame is ERI, at **13 held and 108 gaps**. On the two units that
exist, the mean is 76 gaps.

| | ZAF-shaped | Two-unit mean |
|---|---|---|
| Gaps per country | 44 | 76 |
| `agent_run` calls, 54 countries | 4,752 | 8,208 |
| Agent spend | $475 | **~$820** |
| Documents to fetch, stage and ingest | ~58,000 | **~100,000** |

The Agent spend is affordable either way. **The document volume is not.** A hundred thousand
candidates through OSINT's ingest is not a cost line, it is a different project — and the base
currently holds around 10,000 sources in `raw/` in total. A full-frame filler across 54 countries
would multiply the corpus by an order of magnitude with material the frame asked for but nobody
has read.

**That is the decision this pilot exists to inform, and it is Bill's.** The run itself is a
success by every measure it set; the question it answers is whether the design should be pointed
at all 54 countries, and the evidence says not in this shape.

## The levers, tested against what actually happened

§7 named three. The run has evidence on all three, and it changes the ranking.

**1. Batch same-L2 indicators into one brief — the strongest lever, and it is nearly free.**
`duplicate-in-run` was the most-used drop code, on 37 of 44 indicators, and the cause is
structural rather than incidental: all four `dpi.id` gaps returned substantially the same Home
Affairs corpus; the three `data.statistics` gaps returned substantially the same Stats SA corpus.
The Agent is being asked the same question with a different noun and paying full price each time.
Batching by Level-2 would cut calls materially with little coverage loss, because the documents
were already arriving together.

**2. Merge the two briefs into one — looks attractive, costs more than it saves.** Every batch
independently reported a third to a half of Brief 2's returns already sitting in Brief 1's set,
which reads like pure waste. It is not. Batches 1 and 2 both found the briefs return *different
classes* of document: Brief 1 surfaces the founding statutes and standing instruments that Brief 2
never reaches, and Brief 2 surfaces in-window movement that Brief 1 mostly misses. Merging them
would collapse a real distinction to save calls that batching by L2 saves anyway. **Recommend
against.**

**3. Drop `effort` below `medium` — untested.** No evidence either way from this run. If the
document volume is the problem, lowering effort is the wrong tool: it would reduce quality without
reducing the thing that actually costs.

## Defects this run exposed, ranked

**1. `{indicator}` alone is not a searchable object, and 35 of the 121 frame rows are one or two
words.** The brief in §2 puts the indicator in the objective and the topic in a trailing context
line, which produces objectives reading *"Establish whether **Land** exists in South Africa at
all"*. All seven `dpi.mis--*` rows are bare nouns — Health, Education, Justice, Tax, Customs,
Land, Social protection — meaningless without their Topic, "Sectoral management information
systems"; the seven `dpi.registry--*` rows are the same shape. The Agent correctly reported `Land`
unresolvable. **Fix: compose the objective as `{topic}: {indicator}`.** This is the brief's
defect, not the frame's — the frame carries the disambiguation, §2 just failed to use it.

**2. An ambiguous indicator name can burn a brief on the wrong subject.** `gov.standards--national-quality-standards`
was read by Brief 1 as *health-facility* quality standards: 13 off-topic candidates, zero usable
baseline, $0.10 on the wrong question. Brief 2 read it as data standards and carried the gap
alone. At 54-country scale that misread repeats 54 times. It argues for a disambiguating clause on
ambiguous frame rows, not for a change to the brief.

**3. Exa's Agent concurrency limit is 50 *account-wide*, not per sub-agent.** Batches 2, 3 and 4
all saturated it and had launch waves refused with `CONCURRENCY_LIMIT_REACHED`. No spend was lost —
refused runs are never created — but wall clock was. **Any scale-out needs a launch throttle**,
and this is a property of the delegation design, not of Bill's brief design.

**4. Concurrent sub-agents cannot dedup against a shared queue.** §4 tells each agent to
cross-check `new-queue\`, which cannot work when five of them write to it simultaneously: 48
redundant files across 44 URLs. The parent removed them, keeping `full` bodies over `excerpt`.
**Cross-queue dedup belongs to the parent, after the batches return** — one pass, no race. §4
should say so.

**5. Ten of those duplicate pairs disagreed with themselves about the date.** Two independent
captures of the same page produced different `published` values — the DHA White Paper as
2019-01-01 and 2019-08-01, the draft National AI Policy as 2026-04-09 and 2026-04-10, and eight
more. Each survivor now carries the conflict in its `note` for ingest to settle with the document
in hand. This is a useful accidental control: it says the date discipline is not merely
theoretical, and that two careful reads of the same page disagree about 2% of the time.

**6. Agent dates were wrong constantly, and the guard held every time.** Batch 1 corrected three
(one by seven months), batch 5 at least six, batch 4 two. `SWEEP-COUNTRY-DEEP.md` §3a's rule is
earning its place on every batch, not occasionally. One document defeated both: an Operation
Vulindlela report served from a `202604/...q4.pdf` path with a cover reading "Q1 | 2025-26 | JUNE
2025" — found independently by two batches, flagged by both, staged with the conflict noted.

**7. One capture was silently corrupt.** StatsSA's SASQAF guidelines PDF extracted with every line
character-reversed. Dropped rather than staged. Nothing in the capture rule covers a body that
fetches successfully and is garbage; worth a line in `capture-rule.md` if it recurs.

**8. My own brief let sub-agents collide on a shared scratchpad filename.** No data lost — the
affected agent renamed and carried on — but per-agent scratch namespacing belongs in the brief.

## Whether a searched nil should stamp anything

Moot this run: there were none. The mechanism is untested and stays as `PROGRESS-FILLER.md` §0
specifies it — recorded in the run CSV via `subject_rows_at_probe`, stamped nowhere else. Note
that a run yielding zero nils also means the re-run policy has nothing to suppress, so a second
ZAF run would re-buy all 44 gaps at full price. That is correct — the base will have moved by
then, since this run's own 536 documents are what moves it.
