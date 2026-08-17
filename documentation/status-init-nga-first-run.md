---
type: doc
title: STATUS-INIT — the first run, NGA
last_reviewed: 2026-08-15
---

# STATUS-INIT — the first run, NGA

*(2026-08-15. Nigeria is the first of the 54 and the heaviest: 16 intersections, 348KB of wiki evidence, 462 indicator rows, 90 finance rows. What follows is what the run found out about the process and the data, as distinct from what it found out about Nigeria. Everything in the first two sections recurs on the other 53.)*

*(**Promoted out of `documentation/reviews/` on 2026-08-16, and not archived, because it is still operative.** STATUS-INIT stands at 19 countries through and 35 outstanding, so the properties of the material described below are ahead of the work rather than behind it. The other three files in that folder were spent and moved to `documentation/archived/`; the folder itself is gone, sorting documents by who wrote them rather than by whether they are still true. `STATUS-INIT.md` → *Read alongside* now points here, which nothing did before.)*

## What was produced

`outputs/reports/NGA/NGA-status.md` — 37 sub-sections, 246 distinct sources, none *not established*.
`osint-corpus-exchange/africa-acquire.csv` — 42 rows for NGA, every one an unheld source dated 2024 or later. The per-country markdown table became a single cross-country CSV with an `iso3` column on Bill’s instruction, 2026-08-15: it is a queue worked down in an OSINT session, and a queue wants to be sorted, filtered and counted, which 54 markdown tables will not do. `status` and `notes` are Bill’s columns and survive every rewrite.

Checks A, B, D, E, F, G, I and the frontmatter check pass. C reports one item, the IDA-against-commercial split in Project BRIDGE's appraisal, which is a financing structure rather than a measurement and is correctly undated. H was read rather than grepped, twice: on the first pass 34 of the 37 openings carried news as written and three — Energy, Literacy and Gulf — opened on the oldest fact in their section and were rewritten to open on the newest; after the IIAG revision every opening still carried news, and none of the eight revision agents had spent its new evidence on one.

Twenty-one extraction agents returned 914 facts; 882 survived pooling, 300 of them marked `borderline` by the agent that read the body. The writers stated none of those as written.

## Two properties of the DPI dataset that bear on every country

**The Ibrahim Index family carries no URL, and it is 96 of the 462 rows — resolved the same day.** Every `iiag-*` row carries source-organisation abbreviations in `Source urls` — `AFIDEP/BS/FH`, `V-DEM/WJP`, `AFR` — rather than links, so under *no link, no claim* the whole family yielded nothing on the first pass. The stage 1 agent resolved the index to the Foundation's data portal by search and used that as the URL for nine facts; check A's set does not hold it, so `status-pool.py` dropped all nine, which was right twice over — the rule is the rule, and a portal address found by search is exactly the kind of link check A exists to catch. **`status-outline.md` maps `iiag-*` ids under 19 of its 38 sub-sections**, so a fifth of the dataset and half the outline's bullets were silently unanswerable.

**They are answerable, from the Foundation's country profile** *(Bill, 2026-08-15)*, published per country at `assets.iiag.online/{year}/profiles/{year}-IIAG-profile-{iso2}.pdf`. `scripts/iiag-profiles.py` fetched all 54, read the country name out of each PDF's own cover — the pattern is tested, not trusted — and wrote `lookups/iiag-profiles.csv`; `status_lib.iiag_urls()` makes it the fourth body of evidence check A tests against, and stage 0 now writes the country's profile out as text beside the indicator cuts.

**The profile is better evidence than the rows it replaces**, which is the part worth carrying forward. The dataset gives a value band; the profile gives each of the 96 indicators its 2023 score, its **rank of 54** and its **change over ten years**, and names the country's best, worst, most improved and most deteriorated measures outright. A re-run of that one extraction returned 32 facts, and eight revision agents worked them into twenty of the 37 sub-sections. What they added is mostly contrast rather than colour: Nigerians' own rating of how easy it is to obtain an identity document is among the country's ten most deteriorated indicators over the decade in which the register grew to 136 million; the accessibility of public records ranks 6th in Africa against a gazette and a circular nobody could obtain; civil registration fell 12.5 points over the decade before the electronic platform went live; mobile communications is the country's largest single improvement of the 96 while internet use and device ownership sit at less than half that score. None of that was statable at all a day earlier.

**The rule that made it work is worth keeping.** A score is not a fact until it is written as one — with its rank, its direction, or both, and never as a bare number out of 100 — and a perception measure is written as a perception or dropped. Most of the placements available to the revision agents went unused on exactly those grounds, several of them because the section already established the same thing better from a primary source, which is the behaviour to want: an index is a second reading, and a report that prefers it to a first-hand one has turned into a scorecard.

**Seventeen of NGA's 462 rows carry an empty `Source urls`, and several are the negatives a baseline most wants.** They included no e-signature law, no critical-information-infrastructure instrument, no payments statute, no e-commerce law, no open-banking instrument, no open-data policy, no e-procurement instrument, no infrastructure-sharing regulation, and six unconfirmed register-to-register linkages. A negative with no source is not statable, so the report is silent where the dataset is most informative. Some of it came back through the wiki; how much is not knowable from here.

Neither is a defect in this process. Both are the shape of the material, and both are worth knowing before the pattern is read as a thin country.

## Three defects in `STATUS-INIT.md`, all now corrected in it

**The ownership rule misfired, and it would have hollowed out four chapters.** The file named the owner as the chapter of the fact's first slug *in outline order*. The outline runs infrastructure and DPI first and finance, geopolitics and capacity last, so on NGA that left `finance.new` owning 3 of the 105 facts that answer it, `capacity.training` none of 35, and the five `geopol.*` slugs 4 of 70 between them — four chapters forbidden from stating in full the material they exist to report. The owner is now the chapter of the slug **the extraction agent listed first**, which is that agent's reading of what the fact is mainly about. The two rules disagree on 489 of NGA's 840 multi-slug facts, and on inspection the agent is right: *"Nigeria has no government platform for citizen participation in policymaking"* is a `gov.discourse` fact that outline order hands to `dpi.govtech`. Where a sub-section still owns nothing, its six best-evidenced shared facts are promoted into it.

**Stage 1 step 4 pointed at `files.jsonl`**, contradicting Inputs and check A, both of which resolve through the published catalogue. An agent following the step literally could have cited one of the 39 wiki concept pages carrying a `url:` as though it were a source.

**The agent briefs had nowhere to live.** They were drafted into `prep/`, which is gitignored, so the next country would have re-derived them — which is the failure the file warns about in stage 0 and is worse here, because the fact schema and the borderline rule are the things twenty and ten agents respectively have to receive identically. They are now `documentation/status-init-extract.md` and `documentation/status-init-write.md`.

## What the run added to `scripts/`

`iiag-profiles.py` — fetches and verifies the 54 IIAG country profiles into `lookups/iiag-profiles.csv`, and writes one country's profile out as text for stage 1.
`status-slugs.py` — resolves wiki source slugs to catalogue rows as JSON, one call per agent.
`status-pool.py` — loads stage 1's facts, drops what check A would fail, merges the fact that arrived twice, assigns ownership and writes the chapter slices.
`status-assemble.py` — reads the chapter drafts, keys sub-sections on the `<!-- slug -->` comment rather than the heading text, and writes the report with its frontmatter counts computed from the assembled document.
`status-acquire.py` — adds the country’s rows to `osint-corpus-exchange/africa-acquire.csv`, asking the catalogue of every cited URL and taking the publisher, title and date of an unheld one from the pool. It rewrites only its own country’s rows.

## Two smaller things

**A parenthesis in a URL breaks the link and fails check A.** The NCC's Cyber Resilience Framework is served at an address ending `(CRF-NCS).pdf`; the literal parenthesis closes the markdown link early and the verification reads the truncated address as unheld. One writer agent percent-encoded it unprompted and two did not. The writing brief now says so.

**Splitting the indicator agent three ways was a deviation and it was the right one — now adopted.** The file said one agent for the indicator rows. 462 rows at ~250 tokens each is a 115KB read producing 200-odd facts from one agent, and the rows partition cleanly by variable family into disjoint sets, so nothing is read twice and the fan-out argument is unaffected. The three cuts are `govtech-*` (149), `iiag-*`/`odin-*`/`stats-*`/`rural-*` (136) and `reg-*`/`id-*`/`ict-*`/`exchange-*`/`pay-*` (177), and they returned 27, 28 and 127 facts. `status-scope.py` now writes them, `STATUS-INIT.md` step 5 names them, and stage 0 reports the fan-out as 3 indicator agents rather than 1.

## Cost and shape, for planning the other 53

Thirty subagents for the run proper: 16 intersections, 3 indicator cuts, 1 finance, 10 writers. Extraction ran about 17 minutes wall-clock to the last agent, writing about 10. The IIAG correction added nine more — one extraction and eight revisions — but that cost is Nigeria's alone: every country after this one gets the profile in stage 0 and picks it up in the ordinary `b` cut, with no revision pass at all.

NGA is the largest country in the set on every axis, so it is the ceiling rather than the median — the median country has 7 intersections and about a third of the evidence.

## The revision pass is the successor's shape, tried early

`STATUS-INIT.md` hands the job of keeping a baseline current to `BUILD.md` → *Maintaining the status baseline*: each new source is checked for whether it changes what a section can say, and the section is revised where it does. The IIAG correction ran exactly that loop, three hours after the baseline was first written, and it worked — eight agents given their own draft, the new facts, and an instruction to leave everything else alone returned chapters that changed in the five or six places the evidence reached and were byte-identical everywhere else.

Two things made it safe and are worth carrying into BUILD. The agent was told **which sub-sections must come back unchanged**, so an untouched section could not drift. And it was told **what had been fixed by hand since the section was written** — the three rewritten openings and the four dated figures — so a revision could not quietly undo a verified correction. Neither is inferable from the draft.
