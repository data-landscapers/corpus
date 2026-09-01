# Progress filler — throughput record, COM, 2026-08-31

*(Run against the Comoros — no prior COM run, so §0's skip found nothing to carry forward, and
all 76 gap indicators were live. Batch label `progress-filler-COM-2026-08-31`. Run CSV:
`logs/progress-filler/COM-2026-08-31.csv`, with the selected and unselected registers beside
it.)*

## The headline

**76 of 76 gaps had two briefs run, 71 staged, 5 nil.** This is one of the larger fillers in
the series (GHA ran 40, GNB 205) and the widest single-country gap list yet worked in one pass
— Comoros held only 45 of 121 frame indicators before this run. Four of the five nils are not
searched absences in the ordinary sense: `gov.policy--data-storage-cloud-strategy`,
`gov.legislate--legislation-enabling-data-interoperability`, and both `infra.store`
indicators each had every candidate resolve to a document **already held in `raw/` under a
different topic** — evidence exists, it just isn't mapped to these indicators yet. That is a
mapping-pass signal, not a gap the wiki lacks. Only `dpi.mis--justice` is a genuine absence:
both briefs ran, nothing survivable on a justice case-management or MIS system came back.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 76 of 76 (no skips — no prior COM run) |
| `agent_run` calls | 152 — 2 per gap across eight parallel batches |
| Candidates returned | 464 |
| Fetched | 157 |
| Dropped (pre-fetch, scope/dedup) | 74 — mostly `already-seen` (candidate already in `raw/` under another topic), plus a handful of `off-topic`, `inadmissible-origin`, `fetch-blocked`, `url-dead`, `duplicate-in-run` |
| Cap-excluded (fetched and read, not staged) | 111, recorded with URLs in the unselected register — plus 42 further leads the register also carries but that were never fetched (ranked from the Agent's own summary and passed over), each flagged `Not fetched` in `why_not` and excluded from this count |
| **Staged after the cap** | **150 selections — 63 baseline + 87 progress**, over **118 distinct files** after merge (138 staged by the eight batches before cross-batch dedup), filed as 45 in `COM/baseline/` and 73 in `COM/progress/` |
| Nil | 5 (`gov.policy--data-storage-cloud-strategy`, `gov.legislate--legislation-enabling-data-interoperability`, `dpi.mis--justice`, `infra.store--local-data-centre-capacity-all-providers`, `infra.store--off-site-backup-capacity`) |
| Sessions | one (eight parallel sub-agents, one parent merge) |

## Slicing and cross-batch dedup

**Eight batches, grouped by Level-1 topic and sized 8–11 gaps each** per §6: Governance split
in two (policy/protection/standards, then legislation/regional — 9 and 9), ICT Infrastructure
(10), DPI split in two (exchange/identity/payments, then registries/sectoral-MIS — 11 and 10),
Digitalisation+Technology (10), Capacity+Inclusion (9), Data+Geopolitics (8). All eight
completed cleanly, no incidents, no sub-agents spawning sub-agents.

**The largest merge in the series so far: 20 duplicate-URL files removed across 16 groups**,
plus one in-place silent overwrite repaired (a health-strategy source two sibling batches
wrote to the same filename with different topic framings — merged rather than picked, since
the document genuinely answers both). Two of the sixteen duplicate groups spanned the
baseline/progress split — the World Bank IMF Article IV report and the RIA national-data-
strategy LinkedIn post each turned up independently as one batch's baseline pick and another's
progress pick for the same URL; per §5, baseline won the folder and both indicators'
selections were repointed at the survivor. `scripts/lint-staged-queue.py` flagged three
findings after the merge, all reviewed and confirmed **false positives**: two ASCII-title
flags where the source's own body is consistently unaccented in that exact phrase (not a
capture defect), and one `SUSPECT` crossed-body flag on a Chinese-language capture where the
title-token overlap check scores 0% purely because it has no CJK tokenizer — the body's own
opening heading is in fact character-for-character identical to the title.

**A cross-batch counting error surfaced and was corrected during merge.** Five of the eight
batches (A, B, E, F, H) initially reported `not_selected` (cap-excluded) counts that included
candidates they had only read about in the Exa Agent's own ranked summary text, never actually
fetched via `web_fetch_exa`. Resumed and asked to separate "fetched, read, and cut by the cap"
from "ranked but never opened," each corrected its tally — batch H's apparent 41
cap-exclusions turned out to be zero true fetches (all 41 are `web_fetch_exa`-free leads,
correctly flagged `Not fetched — ranked #N` in the register and kept there for their
lead-generation value, but not counted as cap-exclusions); batch D's reconciliation went the
other way, finding it had *under*-counted five indicators' cap-exclusions. The run CSV's
`not_selected` column reflects the corrected, fetched-only counts (111); the unselected
register carries both kinds of row (153 total), distinguishable by whether `why_not` opens with
"Not fetched" — the unfetched leads are still useful for a future cap-widening decision, they
just require a fetch to become one.

## Cap audit

Zero violations over 76 rows: every indicator staged at most one baseline and at most two
progress items. 150 selections landed on 118 files because a genuinely cross-cutting document
— the PADEC appraisal report, the AMECC état-civil workshops, the RIA national-data-strategy
process, the Beit-Salam Council of Ministers items — was independently found and correctly
selected by more than one indicator's brief; §6's "count selections, not files" held throughout.

## What this run consumed

Eight parallel sub-agents in one sitting, 152 `agent_run` calls at `effort: medium`, roughly
464 candidate leads triaged down to 157 fetches and 150 staged selections. This is the sweep
stage only — stage 2 (post-ingest reading), stage 3 (mapping) and stage 4 (render) are separate
sessions on the far side of an OSINT ingest and a mirror refresh, and are recorded here once
they happen. The batch sits in `new-queue\COM\` undelivered until Bill hand-carries it
(§0/§5); nothing here has touched `raw/`.

## Stages 2 to 4 — the read, the mapping and the render (complete)

**One sitting, 2026-09-01, roughly one hour of wall time, no sub-agents.** OSINT hand-carried and
ingested the batch on 2026-09-01 (46 baseline admitted of 45 staged, 73 progress of 75), and the
whole of stages 2, 3 and 4 then ran inside a single `CYCLE.md` run: BUILD stages 0 to 7 in 44
minutes, RENDER in the same session behind it.

| | |
|---|---|
| Sources reaching stage 4 | 118 of the 150 staged selections, after ingest dedup and re-slugging |
| Gaps closed | 71 of 76 probed — Comoros goes from **45 of 121** frame indicators held to **116** |
| Still *No evidence* | the 5 the sweep returned nil on |
| Ledger | 120 rows to **172**; 62 rows minted, 21 moved, 12 *Not held* rows settled |
| *Not held* rows | 35 to **24**, six of the survivors being the budget record Corpus cannot reach |
| Corrections forced by the new primary texts | 2 — the data protection law is Loi n°14-029/AU adopted 26 June 2014, not the 2021 date an analyst review gave; the cybersecurity law is promulgated and in force since 18 January 2022, not drafted and unenacted |
| Documents rewritten | all three, plus ten empty monthly narrative blocks written and ten status sub-sections revised |
| Sessions | one, unbroken from stage 2 to deployment |

**The 32-selection gap between staged and read is note 92's arithmetic, and it cost nothing here.**
The staged filenames and the ingest slugs count in different units; the run resolved the eight
unmatched register rows by fuzzy match against the catalogue in a single pass rather than by hand,
which is the lesson SWZ paid half a day for.

## Yield against the four stages

**71 gaps closed for one sweep session and one mapping session.** The sweep is still the visible
half and the cheap one; the mapping session did the reading of 118 sources, the authoring of 71
indicator mappings at 8-40 words of summary and 25-200 of developments apiece, 62 new ledger rows,
and the revision of two documents that the widened base had made false in places. On this run the
two halves were close to even in wall time and the mapping half carried the whole of the editorial
risk — every correction above was found there, not in the sweep.

**The trade Bill has not been asked to make.** Nothing was scaled down: the cap held, all 76 gaps
were probed and all 118 ingested sources were read. What the run declined was MWI's 111
unconsidered sources, which the same work order listed and which are a second backfill of this
size, not a tail of this one.
