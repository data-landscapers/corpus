---
type: brief
reader: cc
title: whos-who-reader-brief.md — what one Sonnet reader does with one Who's Who candidate batch
last_reviewed: 2026-11-20
---

# Who's Who reading pass — brief

You extract officeholder attestations from news and document sentences about African institutions. Accuracy matters more than recall: when unsure, leave it out.

## Input

A JSON file: a list of sources. Each has `url`, `year` (publication year), `entities` (a list of `[slug, display name]` — the organisations the source is tagged with), and `sentences` (candidate sentences from the source, in order; a sentence may depend on the one before it for who "he" or "the minister" is).

## Output

Write a JSONL file (one JSON object per line, UTF-8) to the output path you are given. One line per attestation:

```
{"url": "...", "name": "...", "position": "...", "org": "...", "slug": "...", "tense": "holds", "year": "2025", "year_to": ""}
```

And for every source that yields nothing, one line `{"url": "...", "none": true}` — every input url must appear at least once.

## What is an attestation

A sentence (with its neighbours for context) states that a **named person** holds or held a **position** at an **organisation**. All three must be present or clearly resolvable from the source. Skip:

- a person with no position at an organisation (a trader quoted, a citizen, a victim);
- an unnamed holder ("the minister said") unless the same source names that holder nearby;
- a nominated, rumoured, proposed, candidate or hypothetical holder;
- sentences describing the document itself or the record rather than reporting;
- authors and bylines.

## Fields

- **name**: the person's name exactly as written, without honorifics or titles (drop M., Mme, Dr, Hon., S.E., Prof., Colonel-Major etc.). Keep the source's order and spelling.
- **position**: the title as the source gives it, in the source's language, and nothing else — no adjectives the title does not carry, no "former", no reason for leaving, no description of the person. "Ministre de l'Économie et des Finances", "Director-General", "Président du conseil d'administration". Acting/interim qualifiers that are part of the title stay ("Directeur général par intérim").
- **org**: the organisation as written in the source. Where the title names the organisation ("Ministre de l'Économie et des Finances"), org is that ministry ("Ministère de l'Économie et des Finances"). A country's government or presidency counts only for heads of state and heads of government.
- **slug**: the matching slug from the source's `entities` list if one clearly is that organisation; otherwise "". Never invent a slug.
- **tense**: `holds` if the source presents the person in the post (including an appointment it reports); `held` if the source describes them as former, reports their departure, or states a finished term.
- **year**: the source's `year`, unless the sentence dates the event or term itself — then that year.
- **year_to**: only when the source states a term with an end year ("from 2015 to 2019"); otherwise "".

Never record how or why someone left office, and never add anything about a person beyond these fields. Deduplicate: one line per (name, position, org, tense, year) within a source.

## Working

Read the input file with the Read tool (in chunks if large), then write the output file with the Write tool. Do not run code, do not read other files, do not search. When finished, reply with one line: the number of sources, attestation lines and none-lines written.
