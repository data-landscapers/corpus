# STATUS-INIT.md — country status initialisation

Trigger: **"status-init {ISO3}"**. Builds `outputs/reports/{ISO3}/{ISO3}-status.md` — a narrative answering, for each of the 37 sub-sections of `documentation/status-outline.md`, **what is the current status of this in this country**. The outline's bullets are the checklist of what has to be established, not the shape of the output; the output is prose.

**The campaign stopped at 40 of 54 and 14 countries were never run** (`logs/status-init-progress.csv`; a country counts because its report carries `built_by: STATUS-INIT`). Outstanding: **BDI, BWA, COM, DJI, ERI, GMB, GNB, GNQ, LSO, MDG, MLI, MRT, NER, STP**. Their rows are blank rather than annotated, the last run was ZWE on 2026-08-21, and nothing on record decides against them — so this is unfinished work, not a scope ruling, and it is Bill's call whether to finish it. Each of the fourteen currently publishes the ledger-rendered status report, which is the correct default for a unit this has not touched and is not at risk from a rebuild. *(Corrected 2026-09-04. This paragraph said the campaign was complete and all 54 were through; the count has never exceeded 40, reached 2026-08-21, and the claim was written on 2026-08-28 in a docs pass. It also made the acquire feed look drained: the fourteen have no lines in `africa-acquire.csv` because STATUS-INIT is what emits them and never ran, not because theirs were worked through.)* This file remains in force for two reasons: a future re-baseline runs it, and its rules — *When the evidence is borderline*, *Writing*, *Sources and conflicts*, *Verification* — govern every baseline revision `BUILD.md` → *Maintaining the status baseline* makes. The agent briefs it hands out live at `documentation/archived/status-init-extract.md` and `documentation/archived/status-init-write.md`.

This is a Corpus procedure at the Corpus root. It writes to `outputs/`, reads OSINT and never writes to it. Its two data inputs stay in `prep/` and are gitignored deliberately: working material for initialisation, thrown away once the countries are through, so a clean checkout cannot run status-init and does not need to.

## Status is a baseline, and sits outside the collection perimeter

**This is the governing idea, and every rule below is downstream of it.** The wiki's machinery — ingest, index membership, the acquisition queue — assumes material is news arriving now. A status report is not that: it is the baseline the news is read against. It has to be able to say a 1990 law is in force from a source the wiki will never hold, and there is no intention of ingesting ten years of material to make that possible.

Two of the wiki's rules therefore do not reach it, and neither is a conflict:

- **The ledger** carries movement over a rolling thirteen months. Status has no window, so this process neither reads nor writes `ledger.csv`.
- **Index membership** (report-layer check G) protects reports compiled from the wiki. Status draws on sources the wiki does not hold by design, so check A below widens the set to the evidence this process actually read, keeping the test exact.

**Keeping the baseline current is a successor's job**: `BUILD.md` → *Maintaining the status baseline*, one further question asked of each record BUILD already has open. **From the moment this process has run on a unit, nothing re-renders its status report from `ledger.csv`** — `report-render.py` drops `status` from an initialised unit's document set, because a ledger render of an authored baseline is a total loss reported as a successful build.

## The one hard rule

**Every stated fact carries an inline hyperlink, on the claim it supports, to the URL of the source that establishes it. No link, no claim.**

Neither the wiki nor the AfDB dataset is a source; both are intermediaries, and the link goes to the primary. A fact whose primary cannot be resolved to a URL is not written.

**The one exception is a figure the report computes itself** — a count or total that is arithmetic over the evidence, which no source states. **An aggregate is written plainly, with no link, in its own paragraph marked `<!-- derived -->`.** The marker is required, because *no link because nothing establishes this* and *no link because the writer forgot* are otherwise the same paragraph. The exception is never a way to state a sourced fact without sourcing it.

## When the evidence is borderline, the fact does not go in

**This governs the writing rules below and outranks every one of them.**

**The asymmetry is the whole argument.** The baseline is what everything else is read against. A gap in it is visible and gets filled the first time someone asks. An error in it is invisible and propagates into every comparison made against it, indefinitely. The two are not comparable costs.

**Three outcomes, in this order of preference, and never a fourth:**

1. **State it plainly**, where the evidence supports it as written.
2. **State it plainly at a coarser grain** the evidence does support — the outcome most often right and most often missed: *"the register covers most of the adult population"* where sources disagree on the figure.
3. **Drop it.**

**This outranks the news.** The opening sentence carries the *best-evidenced* news, not the biggest. A striking claim resting on a single syndicated report is usually not in the report at all.

**Where two sources of equal tier disagree and recency does not separate them, neither figure is stated.** State what the sources agree on, at whatever grain that is, or state the position as not established, dated. The report never picks a side it could not defend to a reader who follows the link, and never narrates that it had to choose.

## Inputs

- `documentation/status-outline.md` — the question set. **37 sub-sections**; `finance.budget` is suspended; the appendix and `[PROPOSED]` ids are out of scope.
- `lookups/countries.csv` — ISO3 → name → region.
- `wiki/places/{ISO3}.md` — the hub. Frontmatter `topics:`, `## Active topics` and `## Record not held` are the map; `## Recent developments` is chronology, read only to date a claim; `## Financing` is an uncited aggregate. **Never read a hub whole** (NGA is 301KB).
- `wiki/intersections/*.md` — **the primary input**, the compiled current state. **Do not construct the filename**: select on frontmatter **`place: {ISO3}`**, which is authoritative in all files (several countries use unexpected prefixes). Take the region's files too where they bear on `gov.regional`. A thin country (Eritrea: none) is a real outcome, not a failed selection.
- `raw/{year}/...` — the sources; frontmatter `url` is what the report hyperlinks.
- `outputs/catalogue/raw-catalogue.csv` — resolves a slug to its URL. **This, not the index**: the catalogue is the published set; the index also carries wiki concept pages with a `url:`, which are not sources and must not resolve.
- `prep/africa-dpi-data.csv` — ~462 rows per country; only `Variable Id`, `Value Name`, `Year`, `Comments`, `Source urls` matter, and the comments and URLs are the point. Known defects: the `govtech-*` family resolves to one landing page and is largely unusable; some cells concatenate conflicting answers; mojibake is repaired, not described (`python scripts/lint-mojibake.py` says whether it has come back); and **a sourceless negative is not evidence of absence** — where the dataset alone says a country lacks an instrument, the finding is ***Not held*** with a `gaps.csv` line. (Fuller record: `documentation/archived/dpi-data-defects.md`.)
- `lookups/iiag-profiles.csv` — the Ibrahim Index country profile per country, URL verified against each PDF's own cover by `scripts/iiag-profiles.py`. The `iiag-*` rows carry no URL and are read against the profile — better evidence anyway: score, rank of 54, ten-year change.
- `outputs/non-state-finance/all-nonstate.csv` — the major source for `finance.new`; filter on `recipient_country`, taking the region code where a regional commitment names it.

## The run

**Three stages: extract, write, assemble.** The first two fan out to subagents; the third is the parent's alone. The fan-out is by **intersection**, not chapter — an intersection's `topics:` span several chapters, so chapter-shaped agents would each re-read most of the base; the intersection is one file, one agent, read exactly once.

### Stage 0 — the parent scopes the run

```bash
python scripts/log-line.py --start status-init
python scripts/status-scope.py {ISO3}
```

The stamp is per country — stage 3's log call consumes it. `status-scope.py` does the whole of stage 0: resolves the country, extracts the hub map by line range, lists the intersections by frontmatter, and writes the indicator and finance cuts to `prep/scope/{ISO3}/` — files, not stdout, because the parent's context has no business holding them. **Run it and read its output; re-derive nothing by hand.**

### Stage 1 — extract, one subagent per source of evidence

Launched in a single batch. **No extraction agent writes to the output file**: each writes facts to `prep/scope/{ISO3}/facts/{name}.json` and returns only a count. Each is given `documentation/archived/status-init-extract.md` whole, with the country substituted — a file, not a paraphrase, so twenty agents share one schema.

- **One agent per intersection**, reading that one file whole and resolving every slug with `python scripts/status-slugs.py {slug} …` (which reads the catalogue — the same object check A tests against). A slug that resolves to no URL yields no fact. Facts, never prose.
- **Three agents for the indicator rows**, one per disjoint family group.
- **One agent for the finance rows**, country and region.

**The fact schema** — fixed here because ten writers consuming an improvised shape is this design's likeliest failure:

| Field | Contents |
| --- | --- |
| `fact` | One sentence, plain, statable on the page as written. |
| `as_at` | The date the fact is true of, or `structural`. |
| `slugs` | Every Level-2 slug the fact answers. |
| `url` | The resolved link. A fact without one is not returned. |
| `published` | The source's own publication date — this and nothing else drives the 2024 rule. |
| `publisher`, `title` | Enough to write an acquire line without going back. |
| `origin` | `wiki`, `dpi` or `finance`. |
| `tier` | `primary`, `official`, `reported` or `syndicated` — the *kind* of source. |
| `caveat` | The qualification the fact cannot safely be stated without. **Internal; never reaches the page.** |
| `confidence` | `solid` or `borderline` — the strength of the evidence, judged by the agent with the body in front of it. **`borderline` is never stated as written**: coarsened or dropped by the writer. Kept apart from `tier`: a primary source can carry a weak claim. |
| `news` | `true` where an informed reader of this country would not already know it. |

### Stage 2 — write, one subagent per Level-1 chapter

**The parent pools, dedupes and slices deterministically** — `python scripts/status-pool.py {ISO3}`, one slice per chapter. Two facts are one fact when they state the same thing about the same object; the survivor is `solid` over `borderline`, then better `tier`, then later `published`, taking the union of the losers' `slugs`. Every surviving fact gets an **owner**: the chapter of the slug its extraction agent listed first. The owning chapter states it in full; every other chapter may refer to it in passing but must not restate the figure — otherwise one coverage number appears four times in four voices. Where a sub-section owns nothing, `status-pool.py` promotes its six best-evidenced shared facts into it. **A promoted fact arrives as `mine: true` and the writer states it in full** — that is the point of promotion; `costated` and `owner_slug` are provenance, not a restriction.

**One agent per chapter, ten in a batch**, each given `documentation/archived/status-init-write.md` and the path to its slice — facts and resolved URLs, never raw wiki text. It cannot cite anything not in its slice, which is what makes no-link-no-claim enforceable.

### Stage 3 — the parent assembles

1. **Assemble in outline order** — `python scripts/status-assemble.py {ISO3} --hub-reviewed {date} --intersections {n}`, keying sub-sections on the `<!-- slug -->` comment, computing the frontmatter counts from the assembled document.
2. **Add the country's rows to `C:\corpus-osint-xfer\africa-acquire.csv`** — `python scripts/status-acquire.py {ISO3} --compiled {date}`. Re-run the assemble afterwards so `acquire_lines` counts the rows that now exist. **Commit anything else standing in the share first, under its own subject line** — the share is a shared repository and CC commits for both sides, so the other author's work goes in its own commit, named as theirs, then `africa-acquire.csv` alone. Push immediately after each.
3. **Verify** — checks A to I, on the assembled file, never per agent.
4. **Refresh the checklist**: `python scripts/status-progress.py`. A country counts as through only because its report says `built_by: STATUS-INIT`; the `notes` column is Bill's and survives every rewrite; rows are ordered heaviest first, which is also the run order.
5. **Report on two lines**: `{ISO3} · sections written NN of 37 · not established NN · sources cited NN · acquire lines NN` and the run cost.
6. **Log the country and commit it** — one line per country, not per session; the unit of work is the country:

    ```bash
    python scripts/log-line.py status-init "{ISO3}: 37 sub-sections, NN sources, NN acquire lines, A-I pass — ok"
    git add -A && git diff --cached --quiet || git commit -m "{ISO3} status baseline: 37 sub-sections, NN sources"
    ```

**On a failure, log what stopped it** (`… errored on DZA at stage 2: <message>`) and leave the country unfinished rather than issuing a partial baseline — an abandoned country simply stays unticked. STATUS-INIT needs no sentinel: it commits at the end of each country, so a dead run leaves either a clean tree at a country boundary or uncommitted work, which RENDER's Step 0 catches anyway.

**Extraction is where errors get baked in**: a writer never sees a verbatim body, only a fact someone drew from it. Stage 1 therefore returns facts *with* caveats and dates attached — an internal handoff, not report content. A fact the writer cannot state plainly is stated coarser, or dropped.

## Sources and conflicts

**The better source wins, and neither intermediary gets a vote.** Judge on tier: primary over secondary, official over reported, canonical over syndicated, full text over excerpt, finer date precision over coarser; for a time-varying figure, the more recent of equal tier. Where the ordering does not separate them, neither figure is stated — *When the evidence is borderline* governs.

**The test is whether the source is held, not which intermediary carried it.** The question is asked of the catalogue, and only of a URL it does not resolve:

- **Held** — nothing is owed.
- **Not held, dated before 2024** — state the fact, link the URL, carry on. Baseline material, outside the collection perimeter; no acquisition raised.
- **Not held, dated 2024 or later** — state the fact, link the URL, **and write one line to `C:\corpus-osint-xfer\africa-acquire.csv`**. A recent source found here and not held there is a gap in the sweep, not in the baseline. Bill actions the file in an OSINT session.

Framing it on *held* makes it checkable: set membership against the catalogue, which `status-check.py` performs.

**One file for all of Africa**, one row per source with the country in a column:

```
iso3,published,publisher,title,url,sub_section,found,status,notes
RWA,2025-03-14,Rwanda Ministry of ICT,National Data Policy,https://…,gov.policy,2026-08-20,,
```

**A run rewrites only its own country's rows.** The `status` and `notes` columns are Bill's and survive every rewrite, keyed on country and URL — a file that loses working state on regeneration is a report, not a worksheet.

**The queue has a far end, and a closed row does not come back.** OSINT's `STATUS-ACQUIRE` files worked rows into `C:\corpus-osint-xfer\acquire-done.csv` with a `status` (`staged`, `dropped` with a reason, `held`) and a `closed` date. A row is in exactly one of the two files, so **both are read to know whether a URL owes an acquisition**: `status-acquire.py` skips a closed URL, and `status-check.py` counts closed rows as listed. The frontmatter stamps what the baseline *found*; answering a line does not un-find the gap that produced it.

**No disagreement is narrated.** The report states the established fact and its link — never which source it preferred or that two differed. **Where a fact is genuinely unestablished, say so in one plain sentence, dated** — *"No dedicated data protection law had been enacted as at August 2026"* — stated as a fact about the country, never about the evidence: not "the base holds nothing on", not "no source could be found".

## Writing

**Who this is for**: someone who follows this country, skimming for what they did not already know. A section that walks the checklist in order and reports what everyone knows has failed, however accurate.

**The first sentence carries the news** — the skim surface, and the only line most sections get read. It states the thing a reader who knows the country would not already have. Never open with a definition, a restatement of the question, or the oldest fact in the section. **The news is the best-evidenced news, not the biggest** — *When the evidence is borderline* outranks this: a `borderline` fact is coarsened or dropped whatever it would have done for the opening line.

**No apparatus on the page.** No caveats, no hedging, no "sources indicate", no observation that accounts differ. The reader wants the fact and the link; everything else is the writer's problem, settled before the sentence is written. A hedged sentence is worse than a missing one — it costs the reader the same attention and pays nothing.

**One continuous narrative per h3**, up to 350 words, answering the outline's question. No sub-headings, bullets or tables inside a sub-section. **The outline's bullets are the checklist for establishing the status, not the running order of the prose.**

**A thin section is short, not padded.** Two sentences is a legitimate length.

**Every time-varying figure is written dated** — "covered 4.4m people (June 2026)". Structural facts are not dated.

**Money is carried in the announcing party's own currency**, any USD figure as a dated conversion (`original_amount` and `commitment_usd_m` in the finance CSV).

**House style is the wiki's**: cautiously outspoken, evidence-led, polemical about systems and not people. Inline hyperlinks sit on the claim, never gathered at the end.

**One line per paragraph. Never wrap by hand.**

## `finance.new`

Built from `all-nonstate.csv`, not the hub's `## Financing` block (an uncited aggregate — corroboration only). Establish: what has been committed and over what window, how many distinct commitments, the leading financiers, instruments, subsectors, and the largest single live commitment, each named deal hyperlinked. Where `amount_quality` or `status` marks a figure unverified or merely approved, say so. **Counts and totals are the report's own arithmetic**: computed at extraction (where the whole cut is in front of one agent, not the writer's filtered slice), marked `derived`, and placed in their own `<!-- derived -->` paragraph.

## Sub-sections the dataset cannot answer

The five `geopol.*` slugs, `data.satellite` and `finance.mou` have no indicator coverage; `gov.regional`, `capacity.research`, `digital.localgov` and `tech.industry` little. These are answered from the wiki alone. Where the wiki holds nothing either, the section is one sentence saying so, dated — a finding, not a failure.

## Output shape

`outputs/reports/{ISO3}/{ISO3}-status.md`. Frontmatter, then straight into the chapters; no summary, no coverage table.

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

`##` is the Level-1 chapter, `###` the Level-2 label, the slug in an HTML comment underneath so the file stays machine-mappable. Chapters and sub-sections run in `status-outline.md` order.

## Context budget

The fan-out removes the ceiling: an extraction agent's context is bounded by the largest single file (~55KB), and writers see extracted facts. The parent holds only the map, the lists, the pooled facts and the assembled file — never a verbatim body. **What fills the parent is reading the finished report**, which check H requires; that, not the run, is the binding constraint on combining countries in one session. Combine only where the reports are short enough to read properly — a session that skims check H has given up the one check that needs a reader.

## Verification

**Run `python scripts/status-check.py --unit {ISO3}`** — it implements A to G and I; H needs a reader, and `--openings` prints every sub-section's first sentence for that reading. The checker also verifies the frontmatter counts against the document.

- **A — every link is held.** Every URL appears in `outputs/catalogue/raw-catalogue.csv`, `africa-dpi-data.csv` → `Source urls`, `all-nonstate.csv` → `url`, or `lookups/iiag-profiles.csv` → `url` — report-layer check G with the set widened to the four bodies of evidence this process read. Set membership is the only test that catches a URL synthesised from a remembered pattern. Re-run after every edit pass. `report-render.py --check` applies the same widened set to a `built_by: STATUS-INIT` document and only that document; one implementation, in `scripts/status_lib.py`, so the two checks cannot drift.
- **B — every claim is linked.** No sentence states a fact without a hyperlink on it or the sentence before. Two declared exemptions: the *not established* sentence, and a `<!-- derived -->` paragraph. The checker reports every derived paragraph, so the exemption stays visible.
- **C — every time-varying figure is dated.**
- **D — no `[[wikilink]]` survives into the output**, and no bare repo path.
- **E — 37 sub-sections present, in outline order, none empty**, `finance.budget` absent.
- **F — every acquire line is dated 2024 or later** and carries date, publisher, title, URL and sub-section, read from the exchange feed filtered to the unit.
- **G — no apparatus reached the page.** Grep for hedges and evidence-talk: *reportedly, apparently, it appears, sources indicate, according to available, it should be noted, however it is unclear, the data suggests, some sources, no source, the base, the dataset, the wiki, conflicting, discrepancy*. Any hit is rewritten or the claim dropped.
- **H — every sub-section opens on news.** Needs a reader, not a grep.
- **I — as-of honesty** (report-layer check J). The document is never *behind* its newest cited source; the lag the other way is disclosed, not judged. Measured against the held half of the citations only.

A run that fails A, B or G is not issued — A because a synthesised link is undetectable by eye, B and G because a report that hedges or talks about its own evidence has stopped being skimmable, which is the only thing it is for.

## What this process never does

Touches `ledger.csv`, the monthly or the progress report. Writes anywhere but `outputs/reports/{ISO3}/`. Cites a link it has not resolved. States a `borderline` fact as written. Picks between two equal-tier sources that disagree. Puts a caveat, a hedge or a word about its own evidence on the page. Narrates a disagreement. Uses a `[PROPOSED]` indicator. Writes `finance.budget`. Pads a thin section.
