---
type: brief
reader: cc
title: stager-brief.md — what one stager does with one country of a maturity study
last_reviewed: 2026-10-07
status: first used for maturity study health, task H6
---

# Stager brief: read a country's evidence, stage its cells

*(Method §7 step 3 as instructions. The parent assembles and checks what you write.)*

## What you are given

A study id `{id}`, a country `{ISO3}` and an as-at date, under `C:\CORPUS`.

1. Read `maturity/{id}/study.json`: the sub-indicators, each aspect's closed list of values, the cap and the flags.
2. Read the study file it names, in `maturity/{id}/`: the typology, the aspects, the cap rule and the ladders. **The ladders are the whole test.**
3. Read `maturity/{id}/evidence/{ISO3}/evidence.csv`, every row with its `fact` text, then `profile.csv` and `systems.csv` beside it.

**Read nothing else**: no source document, no status report, no other country. Use nothing you know of the country.

## Staging

**One cell per sub-indicator. Stage it from the evidence rows of that sub-indicator, with their text in hand.** A row from a source the study excludes sets nothing, and neither does a fact dated after the as-at.

- **The coverage aspects pick the rung.** For each, the newest dated fact stands; where two disagree, say so in `gaps`. Read the fact, not only its value: a system *deployed in*, *rolled out to* or *available to* facilities is not those facilities entering their own data, and a fact about one facility, one district or one province does not carry the country.
- **A rung is reached only when its whole row is met.** Where the evidence stops short, the cell takes the rung below, and `gaps` names what was missing.
- **Qualifier aspects never raise a stage.** Governance is read over 36 months to the as-at and the last twelve months over 12; older facts are not carried into those two columns. A date given as a year or a month stands for its last day. A fact so dated from a source published by the as-at is inside the window. **A plan is the exception**: it is `plan:current` where the period the fact gives for it includes the as-at, whenever the fact is dated, and not current once that period has ended.
- **The cap rule**: where coverage reaches a rung above the cap's line and governance does not hold what the cap names, the stage is the cap's line, `cap` is the rung coverage reached, and the cap's flag is set. Otherwise `cap` is empty and that flag is never set.
- **Flags**: `advancing` or `regressing` where a dated event inside the twelve months says so; `community integrated` where a row or `systems.csv` shows a community system exchanging data with this sub-indicator's system.
- **`no evidence`**: the country has no evidence row on the sub-indicator. **`unplaced`**: it has rows, and they cannot set a rung. Either needs its reason in `gaps`.
- **Stage 1 is a claim**: it needs the dated statement of absence the ladder asks for.

## What you write

**One file**: `maturity/{id}/evidence/{ISO3}/stage.json`.

```json
{
  "iso3": "",
  "cells": [
    {"sub_indicator": "", "stage": "", "governance": "", "tiers": "", "digitised": "",
     "last12": "", "clinics": "", "cap": "", "flags": "", "stage_sources": "", "gaps": "",
     "note": ""}
  ]
}
```

- `stage`: `1` to `5`, `unplaced` or `no evidence`.
- The five aspect columns: values from the aspect's closed list, exactly as spelt, as the evidence stands at the as-at; several joined by `;`; empty where nothing is held.
- `stage_sources`: the `row_id`s that set the stage, joined by `;`. Only rows of this country and this sub-indicator.
- `gaps`: what is not established, in a sentence or two.
- `note`: why this rung and not the one above, in two sentences at most.

**Write with the Write tool. Create no other file, edit none, delete none, and start no agent of your own.**

## When you finish

Reply in three lines at most: the two stages, and anything the parent must know.
