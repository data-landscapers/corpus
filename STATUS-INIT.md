# STATUS-INIT.md — country status initialisation

Trigger: **"status-init {ISO3}"**. One country per run, from a clean context.

Builds `outputs/reports/{ISO3}/{ISO3}-status.md` — a narrative answering, for each of the 37 sub-sections of `status-outline.md`, **what is the current status of this in this country**. The bullets under each sub-section in the outline are the checklist of what has to be established before that question can be answered. They are not the shape of the output. The output is prose.

## Where this runs

**This is a Corpus procedure and it lives at the Corpus root**, beside `BUILD.md` and `RENDER.md`. It initialises a document in `outputs/`, and everything in `outputs/` is Corpus's — the same rule that puts the report update and the topic layer in BUILD. It reads OSINT and never writes to it. *(This section previously said the file belonged in the OSINT root. Cowork wrote that, in the session that drafted this file, and it was wrong then: the process was already writing to `outputs/`, which the migration had already made Corpus's. Corrected on Bill's ruling, 2026-08-14.)*

**Corpus may read anything in OSINT** *(Bill, 2026-08-14)*, and the workroot now junctions `wiki/` alongside `raw/`, `index/` and `lookups/`, so the intersections and place hubs this process is built on are reachable. Run `python scripts/rebuild.py --scan` once after pulling this change to make the junction; the deferred report-initialisation stage gets the same access from it.

**Its two data inputs stay in `prep/` and are gitignored deliberately** *(Bill, 2026-08-14)*: `africa-dpi-data.csv` (17 MB) and `status-indicators-africa-dpi.csv` are working material for initialisation and are thrown away once the 54 countries are through it. They are cited by `prep/` path in this file and in `documentation/status-outline.md` for that reason — the paths are correct while they matter and go stale by design. A clean checkout cannot run status-init, and does not need to.

## It overwrites the existing status report — deliberately

`outputs/reports/{ISO3}/{ISO3}-status.md` already exists for all 54 countries, written by `REPORT-COUNTRY.md` from `outputs/reports/{ISO3}/ledger.csv`. This process replaces that file. That is the rebuild, and it is what "status-init" means. Git holds the displaced file.

## Status is a baseline, and sits outside the collection perimeter

**This is the governing idea, and every rule below is downstream of it.**

Corpus earns its keep on up-to-date intelligence, and OSINT does that daily — around a thousand new items a month. The wiki's machinery is built for that flow: ingest, index membership, the acquisition queue, contradiction briefs. All of it assumes the material is news arriving now.

**A status report is not that. It is the baseline the news is read against.** It has to be able to say that a 1990 law is in force, or that the last published figure is from 2018, and it has to be able to do so from a source the wiki will never hold. There is no intention of ingesting ten years of material at the wiki's level of detail to make that possible, and no reason to want one.

So the baseline sits outside the collection perimeter, and two of the wiki's rules do not reach it. **Neither is a conflict to be arbitrated; both are rules doing a job the baseline is not part of.**

- **The ledger** carries movement over a rolling thirteen months, which is what the progress report and the monthly update are made of. A ten-year-old source is not movement and has no business in it. Status has no window at all, so this process neither reads nor writes `ledger.csv`, and a rebuild puts nothing out of step.
- **Index membership** — report-layer check G — requires a report's URLs to be held in `index/`. That rule protects reports compiled *from the wiki* against a link synthesised from a remembered pattern, which is a real defect that has happened. The protection is right and is kept; the set is simply the wrong one. Status draws on sources the wiki does not hold, by design, so check A widens the set to the evidence this process actually read and keeps the test exact.

Of the other report-layer checks in `wiki/report-layer.md` §6: **H** is ledger-bound and cannot apply. **K** assumes marked narrative blocks and a skeleton word budget this file does not have. **I**'s vocabulary and ***Not held*** rows do not arise. **J** applies unchanged and is adopted as check I.

**Keeping the baseline current is a successor's job, not this one's.** `STATUS-INIT` establishes it once. Thereafter each new source arriving through the daily flow is checked for whether it changes what a status section can say, and the section is revised where it does — which is how a baseline stays a baseline instead of decaying into an archive. That successor is **`BUILD.md` → *Maintaining the status baseline***, designed 2026-08-15: one further question asked of a record BUILD already has open, on initialised units only. It follows from the same idea rather than qualifying it, and the writing rules below govern a revised section exactly as they govern an initialised one.

**From the moment this process has run on a unit, nothing re-renders its status report from `ledger.csv` again.** `report-render.py` drops `status` from an initialised unit's document set, so `--doc all` renders its monthly and its progress report and leaves the baseline alone. That is not a courtesy — a ledger render of a file this process wrote is a total loss reported as a successful build.

## The one hard rule

**Every stated fact carries an inline hyperlink, on the claim it supports, to the URL of the source that establishes it. No link, no claim.**

Neither the wiki nor the AfDB dataset is a source. Both are intermediaries that cite primaries, and the link in the report goes to the primary, never to the intermediary. A fact whose primary cannot be resolved to a URL is not written.

## When the evidence is borderline, the fact does not go in

**This governs the writing sections below, and it outranks every one of them** *(Bill, 2026-08-15)*. The rule was already implied — by the caveat field, by *no apparatus*, by check G's "rewritten or the claim is dropped" — but only ever as a clause inside a paragraph about something else. It is stated here because it is applied 37 times in each of 54 countries, by ten writer agents that each see one slice of the evidence and none of this file's reasoning unless it is in front of them.

**The asymmetry is the whole argument.** The baseline is what everything else is read against: the monthly, the progress report, and every judgement BUILD later makes about whether a new source changes the position. A gap in it is visible and gets filled the first time someone asks the question. An error in it is invisible and propagates into every comparison made against it, indefinitely. The two are not comparable costs, so they do not get comparable treatment.

**Three outcomes, in this order of preference, and never a fourth:**

1. **State it plainly**, where the evidence supports it as written.
2. **State it plainly at a coarser grain** that the evidence does support. This is the one most often right and the one most often missed — *"the register covers most of the adult population"* where the sources disagree on the figure, rather than a precise number none of them establishes.
3. **Drop it.**

**This outranks the news.** The opening sentence carries the *best-evidenced* news, not the biggest. A striking claim resting on a single syndicated report is not the opening sentence, and is usually not in the report at all. Nothing in this file asks for a finding that is not there, and a section whose most interesting fact is borderline opens on its second most interesting one.

**Where two sources of equal tier disagree and recency does not separate them, neither figure is stated.** *The better source wins* assumes there is a better one. Where there is not, state what the sources agree on — at whatever grain that is — or state the position as not established, dated. The report never picks a side it could not defend to a reader who follows the link, and it never narrates that it had to choose.

## Inputs

- `documentation/status-outline.md` — the question set. **37 sub-sections**: `finance.budget` is suspended and is not written until budget work resumes. The appendix is out of scope; `[PROPOSED]` ids are not used, and the bullets carrying them are answered from the wiki or stated as not established.
- `lookups/countries.csv` — ISO3 → country name → region. The country slug used in intersection filenames is the name lowercased with spaces hyphenated.
- `wiki/places/{ISO3}.md` — the hub. Its frontmatter `topics:` lists which slugs have coverage at all; `## Active topics` maps that coverage to the intersection pages; `## Record not held` states what the base knows it lacks. `## Recent developments` is chronology, which is the wrong input for a status report and is read only to date a claim. `## Financing` is the wiki's own compiled aggregate and carries no source URL.
- `wiki/intersections/*.md` — **the primary input.** These are the compiled current state. The median is seven and NGA has fourteen; Eritrea has none, Mauritania two and Lesotho three, so a thin country is a real outcome and not a sign the selection went wrong. **Do not construct the filename.** The prefix is usually the country name hyphenated, but seven countries use something else — `caf`, `civ`, `drc`, `gnq`, `com`, `cabo-verde`, `sao-tome` — and COM and GNQ each carry files under *two* prefixes. Select instead on the frontmatter, which is authoritative and present in all 396: **`place: {ISO3}`**. Take the region's files too (`place: XEA`, `place: XWA`) where they bear on `gov.regional`.
- `raw/{year}/...` — the sources themselves. Frontmatter `url` is what the report hyperlinks to.
- `outputs/catalogue/raw-catalogue.csv` — resolves a source slug to its URL. **This, not `index/files.jsonl`.** The catalogue is Corpus's published table, the one a reader can download and the one the report layer resolves citations through; the index is what the catalogue is built from. It holds **9,407 records, of which 9,404 carry a URL** — the other three resolve to nothing and are therefore uncitable. *(Corrected 2026-08-15. This pointed at `index/files.jsonl` and gave its file count as 10,171. The index now covers `raw/` **and** `wiki/` — 12,588 files, 9,443 with a URL — and the 39 extra URLs are wiki concept pages carrying a `url:`. Those are not sources, and an extraction agent resolving a slug against the index could have cited one as though it were.)*
- `prep/africa-dpi-data.csv` — 462 rows per country, for all but three: Eritrea and Sudan carry 439 and the Seychelles 432. A short cut is the dataset's own coverage and not a sign the filter went wrong. Only five columns matter: `Variable Id`, `Value Name`, `Year`, `Comments`, `Source urls`. **The comments and the URLs are the point**; the value code is a summary of them. **Two things it does not carry**: the 96 `iiag-*` rows have no URL — see stage 1 step 5, which reads them against the IIAG profile instead — and around 17 rows a country have an empty `Source urls`, several of them the negatives a baseline most wants, which are not statable from here and have to come from the wiki or not at all.
- `lookups/iiag-profiles.csv` — the Mo Ibrahim Foundation's country profile for each of the 54, verified against each PDF's own cover by `scripts/iiag-profiles.py`. The source behind the `iiag-*` rows, and the fourth body of evidence check A tests against.
- `outputs/non-state-finance/all-nonstate.csv` — the major source for `finance.new`. Filter on `recipient_country`, and take the country's region code as well where a regional commitment names it.

## The run

**Three stages: extract, write, assemble.** Both of the first two fan out to subagents; the third is the parent's alone.

**Why the fan-out is by intersection and not by chapter.** An intersection page's `topics:` list spans four Level-1 chapters on average and up to eight, so the evidence does not partition by chapter. Chapter-shaped agents would each re-read most of the base: for NGA the Governance agent alone needs 329KB of the country's 348KB, and the ten agents together read 5.2× the evidence for no reduction in the peak. The intersection is the natural unit — one file, one agent, read exactly once.

### Stage 0 — the parent scopes the run

```bash
python scripts/status-scope.py {ISO3}
```

This does the whole of stage 0 and prints it. **Run it and read its output; do not re-derive any of it by hand** — every step below is deterministic, and doing it afresh 54 times is 54 chances to do it differently.

1. **Resolve the country.** ISO3 → name, region from `countries.csv`. Note the hub's `last_reviewed` date; it dates the whole report.
2. **Read the map, not the mass.** Hub frontmatter `topics:`, then `## Active topics` and `## Record not held`, which the tool extracts by line range. **Never read a hub whole** — NGA is 301KB, ZAF 264KB, KEN 234KB, and `## Recent developments` is chronology, which is the wrong input for a status report and is deliberately not printed.
3. **List the intersections** whose frontmatter carries `place: {ISO3}`, plus the region's where they bear on `gov.regional`. Seven on average, fourteen at most. The tool selects on frontmatter and reports how many of the files do *not* start with the country slug, which for Côte d'Ivoire is all eleven and for Comoros four of five.

It also writes the two non-wiki extraction cuts to `prep/scope/{ISO3}/` — the country's ~460 indicator rows reduced to the five columns that matter, and its finance rows including the region's. **They go to files, not to stdout**: the DPI cut alone is 140KB for Rwanda, and the parent's context has no business holding it. Stage 1's indicator and finance agents are given the paths.

`prep/` is gitignored, like the two CSVs the cuts come from, and for the same reason — this is working material, thrown away once the 54 countries are through.

### Stage 1 — extract, one subagent per source of evidence

Launched in a single batch so they run concurrently. **No extraction agent writes to the output file**; each writes its facts to `prep/scope/{ISO3}/facts/{name}.json` and returns only a count. Several hundred facts pasted back through twenty agents' final messages would put the whole of the evidence in the parent's context, which is the one thing the fan-out exists to prevent.

**The brief they are given is `documentation/status-init-extract.md`**, whole, with the country substituted. It is a file rather than a prompt because the schema below is worth nothing if twenty agents each receive a paraphrase of it, and because a judgement made once and written down is the only kind that survives 54 countries. *(Added 2026-08-15, on the first run: the brief was drafted into `prep/`, which is gitignored, and would have been re-derived differently for every country.)*

4. **One agent per intersection.** It reads that one file whole — 3–14KB, so its context never exceeds ~25KB — resolves every source slug in the body and frontmatter to a URL with `python scripts/status-slugs.py {slug} …`, and returns facts in the schema below. A slug that resolves to no URL yields no fact. It returns facts, never prose. *(Corrected 2026-08-15, on the first run: this step said `files.jsonl` and contradicted Inputs and check A, both of which resolve through the catalogue. An agent following it literally could have cited a wiki concept page carrying a `url:` as though it were a source. `status-slugs.py` reads the catalogue and returns one JSON record per slug, so the resolver is the same object the check tests against.)*
5. **Three agents for the indicator rows**, from the three cuts stage 0 writes — `govtech-*`; `iiag-*`/`odin-*`/`stats-*`/`rural-*`; and `reg-*`/`id-*`/`ict-*`/`exchange-*`/`pay-*`. Each row is `Variable Id`, `Value Name`, `Year`, `Comments`, `Source urls`; the comments carry the reasoning and the caveats and are the point, and the value code is a summary of them. Same schema. *(Three rather than one from 2026-08-15: 462 rows is a 100KB-plus read producing two hundred facts from a single agent, and the families partition into disjoint sets, so nothing is read twice and the fan-out's own argument is untouched.)*

   **The `iiag-*` rows carry no URL and are read against the profile, not on their own.** All 96 of them hold source-organisation abbreviations in `Source urls` rather than links, so under *no link, no claim* they yield nothing — which is what happened on the first run, silently, to a fifth of the dataset and to bullets under 19 of the 38 sub-sections. The Mo Ibrahim Foundation publishes a country profile per country, `lookups/iiag-profiles.csv` holds the 54 verified URLs, `status_lib.iiag_urls()` puts them in check A's set, and stage 0 writes the country's profile out as text beside the cuts. It is better evidence than the rows: score, **rank of 54** and **ten-year change** for each of the 96 indicators, where the dataset carries a value code. *(Bill, 2026-08-15. The URL pattern is not trusted — `scripts/iiag-profiles.py` fetches all 54 and reads the country name out of each PDF's own cover before writing the lookup, because a URL synthesised from a remembered pattern is exactly what check A exists to catch.)*
6. **One agent for the finance rows.** Country and region, from `all-nonstate.csv`. Same schema.

**The fact schema.** One JSON object per fact, returned as a list. Ten writer agents consuming an improvised shape is this design's most likely failure, so the shape is fixed here and agents do not vary it.

| Field | Contents |
| --- | --- |
| `fact` | One sentence, plain, statable on the page as written. Not a note, not a fragment. |
| `as_at` | The date the fact is true of — `YYYY`, `YYYY-MM` or `YYYY-MM-DD` — or `structural` where it is not time-varying. |
| `slugs` | Every taxonomy Level-2 slug the fact answers. Usually one or two, occasionally four. |
| `url` | The resolved link. A fact without one is not returned. |
| `published` | The source's own publication date. This and nothing else drives the 2024 rule. |
| `publisher`, `title` | Needed to write an acquire line without going back to the source. |
| `origin` | `wiki`, `dpi` or `finance` — which stage-1 agent found it. |
| `tier` | `primary`, `official`, `reported` or `syndicated`. Drives better-source-wins at the pooling step. |
| `caveat` | The qualification the fact cannot safely be stated without, or empty. **Internal. Never reaches the page** — it exists so the writer can judge whether to state the fact, state it coarser, or drop it. |
| `confidence` | `solid` or `borderline`. **`borderline` is never stated as written** — the writer coarsens it or drops it. Judged by the agent that read the body, because that is the only point in the run where the body is in front of anyone; a writer sees a sentence someone else drew from it and cannot tell a well-attested figure from a single unreplicated one. Kept apart from `tier`, which is the *kind* of source and not the strength of the evidence: a primary source can carry a weak claim and a reported one a solid claim, and collapsing the two would lose exactly the distinction this field exists to carry. |
| `news` | `true` where an informed reader of this country would not already know it. Feeds the writer's choice of opening sentence. |

### Stage 2 — write, one subagent per Level-1 chapter

7. **The parent pools the facts, dedupes them and slices the pool by slug.** A fact that answers four chapters is written once and passed to all four, so the writers see a consistent record rather than four readings of it.

**Dedupe and ownership, deterministically** — `python scripts/status-pool.py {ISO3}`, which does all of this and writes one slice per chapter to `prep/scope/{ISO3}/slices/`. Two facts are one fact when they state the same thing about the same object — the same law, system, register, figure or commitment — whatever words they arrived in. The survivor is `solid` over `borderline` first, then the better `tier`, then the later `published`, and it takes the **union** of the losers' `slugs`. Confidence leads because the point of the pool is that a solid account of an object is available to every chapter that needs it: where one exists, no chapter should be reasoning from the shaky version of the same fact. A fact that survives as `borderline` reaches the writer still marked, and is coarsened or dropped there. Every surviving fact then gets an **owner**: the chapter of **the slug its extraction agent listed first**, which is that agent's judgement of what the fact is mainly about, made with the body in front of it. The owning chapter states it in full; every other chapter receiving it may refer to it in passing but must not restate the figure. Without this the population-coverage number appears four times in four voices, which is what makes a report unskimmable.

*(Corrected 2026-08-15, on the first run. This said the owner was the chapter of the fact's first slug **in `status-outline.md` order**, and that rule misfires: the outline runs infrastructure and DPI first and finance, geopolitics and capacity last, so on NGA it left `finance.new` owning 3 of the 105 facts that answer it, `capacity.training` owning none of 35, and the five `geopol.*` slugs owning 4 of 70 between them. Four chapters would have been forbidden from stating in full the material they exist to report, and a* not established *line there would have been false. The two rules disagree on 489 of NGA's 840 multi-slug facts and the agent is right on inspection — "Nigeria has no government platform for citizen participation in policymaking" is a `gov.discourse` fact that outline order hands to `dpi.govtech`. Where a sub-section still owns nothing, `status-pool.py` promotes its six best-evidenced shared facts into it, because a section every one of whose facts belongs to someone else cannot be written at all.)*
8. **One agent per chapter, ten in a batch.** Each is given `documentation/status-init-write.md` as its brief and the path to its slice — facts and resolved URLs, never raw wiki text, never the hub — and writes the narrative for its sub-sections to `prep/scope/{ISO3}/draft/`. It cannot cite anything not in its slice, which is what makes the no-link-no-claim rule enforceable rather than aspirational. Its task adds only what the brief cannot know: the chapter, its sub-sections in outline order with the question each answers, and the two or three distinctions that chapter's sub-sections blur if left alone.

### Stage 3 — the parent assembles

9. **Assemble in outline order** — `python scripts/status-assemble.py {ISO3} --hub-reviewed {date} --intersections {n}`, which reads the chapter drafts, keys sub-sections on the `<!-- slug -->` comment rather than the heading text, and writes `outputs/reports/{ISO3}/{ISO3}-status.md` with its frontmatter counts computed from the assembled document. Where the same fact has surfaced in several chapters, it is stated in full in the one where it is load-bearing and referred to in passing elsewhere; the report does not repeat a figure four times.
10. **Write `outputs/reports/{ISO3}/{ISO3}-acquire.md`** — `python scripts/status-acquire.py {ISO3} --compiled {date} --country {name}`, which asks the catalogue of every cited URL and takes the publisher, title and publication date of an unheld one from the pool. See *Conflicts*. Re-run step 9 afterwards so the frontmatter's `acquire_lines` counts the file that now exists.
11. **Verify** — checks A to I below, on the assembled file. Never per agent.
12. **Refresh the checklist**: `python scripts/status-progress.py`. It rewrites `logs/status-init-progress.csv`, where a country counts as through because its status report says `built_by: STATUS-INIT` and for no other reason — so the file cannot drift out of step with the work the way a hand-ticked list does. Its `notes` column is Bill's and survives every rewrite. Rows are ordered heaviest first, so it is also the run order.
13. **Report on two lines**: `{ISO3} · sections written NN of 37 · not established NN · sources cited NN · acquire lines NN` and the run cost.

**What this costs, and where the caveats stop.** Extraction is where errors get baked in: a writer never sees a verbatim body, only a fact someone else drew from it, so an extraction agent that drops a qualification has silently changed what the report can say. Stage 1 therefore returns facts *with* their caveats and dates attached — **and that is an internal handoff, not report content.** The caveat exists so the writer can judge whether the fact is safe to state. It does not travel to the page. A fact the writer cannot state plainly is stated plainly at a coarser grain, or dropped.

## Sources and conflicts

**The better source wins, and neither intermediary gets a vote.** Judge on tier, in this order: primary over secondary, official over reported, canonical over syndicated, full text over excerpt, finer date precision over coarser. For a time-varying figure, the more recent of two sources of equal tier wins.

**Where that ordering does not separate them, neither figure is stated** — *When the evidence is borderline*, above. This rule names the winner when there is one; it does not license inventing one when there is not.

**The test is whether the source is held, not which intermediary carried it** *(Bill, 2026-08-15)*. The 2024 line is not about what the report may cite — the report cites it either way — but about **whether the wiki should have caught it**, and a source the wiki already holds raises nothing whatever its date or its route. So the question is asked of the catalogue, and only of a URL the catalogue does not resolve:

- **Held** — nothing is owed. It came through the daily flow or the vault has it anyway.
- **Not held, dated before 2024** — state the fact, link the URL, and carry on. This is baseline material, outside the collection perimeter and outside OSINT's job. No acquisition is raised.
- **Not held, dated 2024 or later** — state the fact, link the URL, **and write one line to `outputs/reports/{ISO3}/{ISO3}-acquire.md`**. Recent material is current-awareness material, which the daily flow exists to catch. A 2024-or-later source found here and not held there is a gap in the sweep, not a gap in the baseline, and that is what the line reports. Bill actions the file in an OSINT session.

Framing it on *held* rather than on *arrived through the dataset* is what makes it checkable: the held/not-held split is set membership against the catalogue, which `status-check.py` performs, so the check reports the candidate list rather than the run having to remember where each fact came from.

The acquire file is a table, so that it is readable in an OSINT session and parseable by check F:

```
---
title: {Country} — sources found by STATUS-INIT and not held
place: {ISO3}
compiled: {date}
built_by: STATUS-INIT
---

| Published | Publisher | Title | URL | Sub-section |
| --- | --- | --- | --- | --- |
| 2025-03-14 | Rwanda Ministry of ICT | National Data Policy | https://… | gov.policy |
```

**No disagreement is narrated.** The report states the established fact and its link. It does not say which source it preferred, that two sources differed, or that the dataset says otherwise. A reader who wants the argument can follow the link.

**Where a fact is genuinely unestablished, say so in one plain sentence, dated.** *"No dedicated data protection law had been enacted as at August 2026"* is news to most readers and belongs in the narrative. It is stated as a fact about the country, never as a fact about the evidence — not "the base holds nothing on", not "no source could be found". A guess never appears, and neither does padding.

## Writing

**Who this is for.** Someone who follows this country skimming for what they did not already know. That governs everything below. A section that makes a well-informed reader stop and read is doing its job; a section that walks the checklist in order and reports what everyone knows has failed, however accurate it is.

**The first sentence carries the news.** It is the skim surface, and the only line most sections will get read. It states the thing a reader who knows the country would not already have: the figure that moved, the law that passed, the system that went live, the gap that has not closed. The rest of the narrative supports it. Never open with a definition, a restatement of the question, or the oldest fact in the section.

**The news it carries is the best-evidenced news, not the biggest** — see *When the evidence is borderline*, which outranks this section. The pressure runs the other way here and it is worth naming: a rule to lead on news, next to a rule forbidding hedges, reads as an instruction to assert the most striking thing available. It is not. A `borderline` fact is coarsened or dropped whatever it would have done for the opening line, and a section whose most interesting fact does not survive that opens on its second most interesting one.

**No apparatus on the page.** No caveats, no hedging, no notes about the evidence, no "sources indicate", no "it should be noted", no observation that two accounts differ or that a figure is contested. The reader wants the fact and the link. Everything else is the writer's problem, settled before the sentence is written. Where a fact is too shaky to state, it does not appear — a hedged sentence is worse than a missing one, because it costs the reader the same attention and pays nothing.

**One continuous narrative per h3**, up to 350 words, answering the question in the outline. Sub-headings, bullets and tables do not appear inside a sub-section. **The bullets in `status-outline.md` are the checklist for establishing the status, not the running order of the prose** — a narrative that marches through them in sequence reads as a form return.

**A thin section is short, not padded.** Two sentences is a legitimate length. Nothing is written to fill a section out to match its neighbours.

**Every time-varying figure is written dated** — "covered 4.4m people (June 2026)", never "covers 4.4m people". Structural facts — a law's provisions, a system's architecture — are not time-varying and are not dated.

**Money is carried in the announcing party's own currency**, with any USD figure written as a dated conversion. The finance CSV holds both: `original_amount` is the announcement, `commitment_usd_m` is the conversion.

**House style is the wiki's**: cautiously outspoken, evidence-led, polemical about systems and not people, for governance and policy readers who are not technical. Inline hyperlinks sit on the claim they support and are never gathered at the end.

**One line per paragraph. Never wrap by hand.**

## `finance.new`

`all-nonstate.csv` is the major source, and the narrative is built from it rather than from the hub's `## Financing` block — that block is the wiki's own aggregate and carries no URL, so it can corroborate but cannot be cited.

The narrative establishes: what has been committed and over what window, how many distinct commitments that is, who the leading financiers are, what instruments they used, which subsectors took the money, and the largest single live commitment. Each named deal is hyperlinked to its `url`. Where `amount_quality` or `status` marks a figure as unverified or merely approved, the narrative says so rather than reporting it as money moved.

## Sub-sections the dataset cannot answer

The five `geopol.*` slugs, `data.satellite` and `finance.mou` have no indicator coverage, and `gov.regional`, `capacity.research`, `digital.localgov` and `tech.industry` have very little. These are answered from the wiki alone, where `geopol.*`-tagged and finance-tagged sources carry named actors and dated commitments. Where the wiki holds nothing either, the section is one sentence saying so, dated. That is a finding, not a failure.

## Output shape

`outputs/reports/{ISO3}/{ISO3}-status.md`. Frontmatter, then straight into the chapters. No summary, no coverage table.

The frontmatter follows the fields the displaced report already used — `place:` and `compiled:` are the house keys and are kept — with the ledger counts replaced by this process's own.

```
---
title: Rwanda — digital transformation and data governance status report
compiled: 2026-08-14
place: RWA
region: XEA
built_by: STATUS-INIT
hub_last_reviewed: 2026-07-28
intersections_read: 8
sources_cited: 61
sections_written: 34
not_established: 3
acquire_lines: 7
---

## ICT Infrastructure

### Connectivity
<!-- infra.connect -->

{narrative}
```

`##` is the Level-1 chapter, `###` is the Level-2 label, and the slug rides in an HTML comment underneath so the file stays machine-mappable without putting taxonomy noise in front of a reader. Chapters and sub-sections run in the order of `status-outline.md`.

## Context budget

**No country needs more than one run, and every country runs identically.** The fan-out removes the ceiling: an extraction agent reads one intersection, so its context is bounded by the largest single file in the corpus rather than by the size of the country. NGA's fourteen intersections total 348KB, but the largest single file in the whole corpus is `nigeria--dpi-pay.md` at 55KB, and the writers see extracted facts rather than any of it.

**The parent's own context stays small** — the hub map, the intersection list, the pooled facts, and the assembled file. It never holds a verbatim body.

For reference, the volumes the fan-out is avoiding, measured as a single pass with intersections read whole and the hub read selectively: median **~42k tokens**, worst case **~132k** (NGA), then ZAF 118k, KEN 101k, GHA 88k, AGO 88k, UGA 77k. Reading a hub whole would put NGA at ~207k, which is why step 2 forbids it whatever the architecture.

**One country per run, context cleared between countries.** Nothing carries across runs except this file — there is no method memory to preserve, which is exactly why the method lives here and not in a session. Countries are never combined in a run. What limits a session is cost, not context.

## Verification

**Run `python scripts/status-check.py --unit {ISO3}` — it implements A to G and I.** H needs a reader and says so; `--openings` prints every sub-section's first sentence for that reading. The checker also verifies the frontmatter counts against the document, because a report that misstates its own source count is wrong in the place a reader is least likely to check.

- **A — every link is held.** Every URL in the output appears in `outputs/catalogue/raw-catalogue.csv`, in `africa-dpi-data.csv` → `Source urls`, in `all-nonstate.csv` → `url`, or in `lookups/iiag-profiles.csv` → `url`. That is report-layer check G with the set widened to the four bodies of evidence this process read, which is the whole of what it read. *(The fourth was added 2026-08-15 with the IIAG profiles; see stage 1 step 5.)* Set membership is the only test that catches a URL synthesised from a remembered pattern, since such a link is indistinguishable from a real one by inspection. Re-run after every edit pass, never once at the end. *(Corrected 2026-08-15: this said `index/`. The report layer resolves citations through the published catalogue — the table a reader can download — and has done since 2026-08-14; the index is what the catalogue is built from and is not the published set. The two differ by 39 wiki concept pages carrying a `url:`, which are not sources and must not resolve.)*

  `report-render.py --check` applies the same widened set to a `built_by: STATUS-INIT` document, and only to that document — the monthly and the progress report in the same folder keep the catalogue-only test, because they may cite nothing else. One implementation, in `scripts/status_lib.py`, so the two checks cannot drift into disagreeing about whether a link is real.
- **B — every claim is linked.** No sentence states a fact without a hyperlink on it or on the sentence before it.
- **C — every time-varying figure is dated.**
- **D — no `[[wikilink]]` survives into the output**, and no bare repo path.
- **E — 37 sub-sections present, in outline order, none empty**, and `finance.budget` absent.
- **F — every acquire line is dated 2024 or later** and carries date, publisher, title, URL and sub-section.
- **G — no apparatus reached the page.** Grep the output for hedges and evidence-talk: *reportedly, apparently, it appears, sources indicate, according to available, it should be noted, however it is unclear, the data suggests, some sources, no source, the base, the dataset, the wiki, conflicting, discrepancy*. Any hit is rewritten or the claim is dropped.
- **H — every sub-section opens on news.** The first sentence states something a reader who follows the country would not already know. A first sentence that defines a term, restates the question or leads with the oldest fact in the section is rewritten. This one needs a reader, not a grep.
- **I — as-of honesty** (report-layer check J). The document is never *behind* its newest cited source, and the lag the other way is disclosed rather than judged. *(Corrected 2026-08-15: this said `compiled:` is never **ahead** of its newest cited source, which transcribed report-layer check J's reported half as though it were the gate. It cannot be one — a baseline compiled today from sources published last month is dated ahead of every one of them, which is the normal state of every status report ever written. Check J fails on the opposite direction and reports this one.)* Measured against the held half of the citations only: the AfDB dataset carries the year a value is true of, not the date its source was published.

A run that fails A, B or G is not issued — A because a synthesised link is undetectable by eye, B and G because a report that hedges or talks about its own evidence has stopped being skimmable, which is the only thing it is for.

## What this process never does

Runs before it has been moved to the repo root. Touches `ledger.csv`, the monthly update or the progress report. Writes anywhere but `outputs/reports/{ISO3}/`. Cites a link it has not resolved. **States a `borderline` fact as written, rather than coarsening it or dropping it. Picks between two equal-tier sources that disagree.** Puts a caveat, a hedge or a word about its own evidence on the page. Narrates a disagreement between sources. Uses a `[PROPOSED]` indicator. Writes `finance.budget`. Pads a thin section.
