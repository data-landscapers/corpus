---
type: brief
reader: cc
title: note-for-cc-2026-10-06.md — what Bill and Cowork settled on maturity studies, before CC starts
date: 2026-10-06
status: handover; delete once H1 is under way and the review points below are answered
---

# Maturity studies: handover from Cowork, 2026-10-06

*(Written at Bill's request after an afternoon's design session. It says what was decided, what was written, and what nothing has yet checked. The two documents carry the rules; this note does not repeat them.)*

## What changed

**The assessment is rebuilt as studies** *(Bill)*: topic by topic, indicator by indicator, each study worked whole across 54 countries. The first is rural health clinics, split into HMIS and EMR. The first run's pages are in `outputs/archived/` and its design documents in `documentation/archived/`.

**Read, in this order:**

1. `maturity/documentation/maturity-study-method.md` — the reusable procedure, two phases around OSINT's ingest.
2. `maturity/health/maturity-study-health.md` — the first study, with tasks H1 to H8.

**Layout** *(Bill)*: generic documents in `maturity/documentation/`, each study's file and working files in `maturity/{id}/`, what a study issues in `outputs/maturity/{id}/`, scripts and lookups where they always go.

## What Bill ruled

Each is marked *(Bill)* in the two files. The ones that most shape the build:

- One stage per sub-indicator, set by coverage: tiers in use, where data is digitised, and the share of primary clinics doing the input. Governance and the last twelve months cap or flag a stage and never raise it.
- The ids are `digital.rural--digitalisation-of-rural-health-clinics-hmis` and `-emr`.
- An HMIS must report how many patients were treated, and for what. Single-function systems, programme trackers and community systems are noted and not assessed.
- All 54 countries in one run, no pilot.
- Corpus runs the Exa searches and never writes to `raw/`. Relevance selects; there is no numeric cap.
- Found documents are handed over in `prepared\` under an `[ACT]` note that says they are maturity evidence, not general ingest.

## Cowork's readings, not yet confirmed by Bill

- That the documents themselves go to `prepared\`, replacing `new-queue\`.
- That `dpi.mis--health` is retired at acceptance along with the rural row.
- That *community integrated* is a flag and does not change the stage.

## What nothing has checked

- **No script exists and nothing has run.** The four scripts the method names are H1.
- **How OSINT moves candidates from `prepared\note-NNN\candidates\` into its ingest is not specified.** The method leaves it to the brief. Decide whether the handover needs a script with its input, as `prepared/` usually carries.
- **The lane.** `BACKFILL_PREFIXES` in the mirror's `scripts/ingest-lane.py` was read on 2026-10-06 and holds no maturity prefix. H2 adds one. Whether a prefix is the right way to mark the lane is yours to judge.
- **PROGRESS-FILLER is cited by section number** (§0, §3 to §6, with §4a and §5's folders replaced). Check the citations still say what the method takes them to say.
- **No cap means no ceiling on what OSINT ingests.** H5 tells Bill the count before the note is written. Quota is his call.
- **The ladders are untested.** H4 tests them on the Phase 1 profiles, before any search.
- **`scripts/.workroot/` was not reachable from Cowork's sandbox**, so the junction paths are unverified.

## State of the repository

- Cowork's commits: `5eb3fe170`, then `7b564692b`. **`7b564692b` is not pushed.**
- `scripts/lint-docs.py` now also reads `maturity/*/*.md`. Both documents pass, each within ten words of the 1,500 cap: an addition needs a trim.
- `maturity-rethink.md` now sits in `outputs/maturity/`, the folder the method reserves for what studies issue. It reads as belonging in `maturity/documentation/`; that is Bill's to say.

## What is asked of you

**Review both documents operationally before building**: say what will not run as written, and change it. Then start at H1.
