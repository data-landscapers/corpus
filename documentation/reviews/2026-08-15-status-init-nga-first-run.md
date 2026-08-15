---
type: doc
title: STATUS-INIT — the first run, NGA
last_reviewed: 2026-08-15
---

# STATUS-INIT — the first run, NGA

*(2026-08-15. Nigeria is the first of the 54 and the heaviest: 16 intersections, 348KB of wiki evidence, 462 indicator rows, 90 finance rows. What follows is what the run found out about the process and the data, as distinct from what it found out about Nigeria. Everything in the first two sections recurs on the other 53.)*

## What was produced

`outputs/reports/NGA/NGA-status.md` — 37 sub-sections, 248 distinct sources, none *not established*.
`outputs/reports/NGA/NGA-acquire.md` — 43 lines, every one an unheld source dated 2024 or later.

Checks A, B, D, E, F, G, I and the frontmatter check pass. C reports one item, the IDA-against-commercial split in Project BRIDGE's appraisal, which is a financing structure rather than a measurement and is correctly undated. H was read rather than grepped: 34 of the 37 openings carried news as written, and three — Energy, Literacy and Gulf — opened on the oldest fact in their section and were rewritten to open on the newest.

Twenty extraction agents returned 891 facts; 850 survived pooling, 295 of them marked `borderline` by the agent that read the body. The writers stated none of those as written.

## Two properties of the DPI dataset that bear on every country

**The Ibrahim Index family is uncitable, and it is 96 of the 462 rows.** Every `iiag-*` row carries source-organisation abbreviations in `Source urls` — `AFIDEP/BS/FH`, `V-DEM/WJP`, `AFR` — rather than links. Under *no link, no claim* the whole family yields nothing. The stage 1 agent that read them resolved the index itself to the Mo Ibrahim Foundation's data portal by search and used that as the URL for nine facts; check A's set does not hold it, so `status-pool.py` dropped all nine, which is the right outcome twice over — the rule is the rule, and a portal address found by search is exactly the kind of link check A exists to catch. **`status-outline.md` maps `iiag-*` ids under 19 of its 38 sub-sections**, and not one of the 96 rows carries an `http` address. Those bullets cannot be answered from the dataset in any country, and the outline should say so where it says it of the `[PROPOSED]` ids.

**Seventeen of NGA's 462 rows carry an empty `Source urls`, and several are the negatives a baseline most wants.** They included no e-signature law, no critical-information-infrastructure instrument, no payments statute, no e-commerce law, no open-banking instrument, no open-data policy, no e-procurement instrument, no infrastructure-sharing regulation, and six unconfirmed register-to-register linkages. A negative with no source is not statable, so the report is silent where the dataset is most informative. Some of it came back through the wiki; how much is not knowable from here.

Neither is a defect in this process. Both are the shape of the material, and both are worth knowing before the pattern is read as a thin country.

## Three defects in `STATUS-INIT.md`, all now corrected in it

**The ownership rule misfired, and it would have hollowed out four chapters.** The file named the owner as the chapter of the fact's first slug *in outline order*. The outline runs infrastructure and DPI first and finance, geopolitics and capacity last, so on NGA that left `finance.new` owning 3 of the 105 facts that answer it, `capacity.training` none of 35, and the five `geopol.*` slugs 4 of 70 between them — four chapters forbidden from stating in full the material they exist to report. The owner is now the chapter of the slug **the extraction agent listed first**, which is that agent's reading of what the fact is mainly about. The two rules disagree on 489 of NGA's 840 multi-slug facts, and on inspection the agent is right: *"Nigeria has no government platform for citizen participation in policymaking"* is a `gov.discourse` fact that outline order hands to `dpi.govtech`. Where a sub-section still owns nothing, its six best-evidenced shared facts are promoted into it.

**Stage 1 step 4 pointed at `files.jsonl`**, contradicting Inputs and check A, both of which resolve through the published catalogue. An agent following the step literally could have cited one of the 39 wiki concept pages carrying a `url:` as though it were a source.

**The agent briefs had nowhere to live.** They were drafted into `prep/`, which is gitignored, so the next country would have re-derived them — which is the failure the file warns about in stage 0 and is worse here, because the fact schema and the borderline rule are the things twenty and ten agents respectively have to receive identically. They are now `documentation/status-init-extract.md` and `documentation/status-init-write.md`.

## What the run added to `scripts/`

`status-slugs.py` — resolves wiki source slugs to catalogue rows as JSON, one call per agent.
`status-pool.py` — loads stage 1's facts, drops what check A would fail, merges the fact that arrived twice, assigns ownership and writes the chapter slices.
`status-assemble.py` — reads the chapter drafts, keys sub-sections on the `<!-- slug -->` comment rather than the heading text, and writes the report with its frontmatter counts computed from the assembled document.
`status-acquire.py` — writes the acquire file, asking the catalogue of every cited URL and taking the publisher, title and date of an unheld one from the pool.

## Two smaller things

**A parenthesis in a URL breaks the link and fails check A.** The NCC's Cyber Resilience Framework is served at an address ending `(CRF-NCS).pdf`; the literal parenthesis closes the markdown link early and the verification reads the truncated address as unheld. One writer agent percent-encoded it unprompted and two did not. The writing brief now says so.

**Splitting the indicator agent three ways was a deviation and it was the right one.** The file says one agent for the indicator rows. 462 rows at ~250 tokens each is a 115KB read producing 200-odd facts from one agent, and the rows partition cleanly by variable family into disjoint sets, so nothing is read twice and the fan-out argument is unaffected. The three cuts were `govtech-*` (149), `iiag-*`/`odin-*`/`stats-*`/`rural-*` (136) and `reg-*`/`id-*`/`ict-*`/`exchange-*`/`pay-*` (177), and they returned 27, 28 and 127 facts. Worth adopting as the rule rather than leaving as a deviation.

## Cost and shape, for planning the other 53

Thirty subagents in all: 16 intersections, 3 indicator cuts, 1 finance, 10 writers. Extraction ran about 17 minutes wall-clock to the last agent, writing about 10. NGA is the largest country in the set on every axis, so it is the ceiling rather than the median — the median country has 7 intersections and about a third of the evidence.
