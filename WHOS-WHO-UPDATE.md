---
type: runbook
reader: cc
title: The Who's Who reading pass — BUILD stage 4d — instruction for Claude Code
last_reviewed: 2026-11-20
---

# The Who's Who reading pass — BUILD stage 4d — runbook for Claude Code

*(`documentation/whos-who.md` is the design; this is what to run. `rebuild.py` stage 2e has already cut tonight's batches and rebuilt the organisations and the fact table from the cache. This stage reads the new sources and admits what they say. Nothing in it is published until stage 5 of the design ships the page.)*

**Work folder:** `C:\whos-who-work\` (`WHOS_WHO_WORK` overrides), outside the repository, because the batches hold source sentences and §3 forbids committing them.

1. **See what is owed.** `C:\whos-who-work\candidates\all\` holds `batch-NNN.json`, at most 150 sources each. No batches means nothing is owed: skip to step 5.
2. **Clear stale output.** `out\all\` must hold no `.jsonl` from an earlier night: move any to `done-{date}\out\`. The admission matches output to input by batch number, so an old file reads as a batch of unread sources.
3. **Read.** One Sonnet agent per batch, three at a time at most, each given `documentation/whos-who-reader-brief.md`, its input path and `out\all\batch-NNN.jsonl`, with Read and Write only. A reader is never waited on: one still out 20 minutes after its wave is stopped, and its batch left for tomorrow.
4. **Admit.** `python scripts/whos-who-cache.py all --only N[,M…]`, naming only finished batches. A source the reader skipped stays uncached and is batched again tomorrow. Then move the admitted `candidates` and `out` files to `done-{date}\`.
5. **Rebuild.** `python scripts/whos-who-orgs.py`, then `python scripts/whos-who-people.py`. The first exits 1 if a government name stands for two countries; fix that with a `hand` row in `lookups/organisations.csv` tonight. The second reports how many ids were new and how many retired. Retired should be 0 unless a ruling was added.
6. **Commit** `build/whos-who/extract.csv`, `lookups/organisations.csv`, `lookups/people.csv` and `lookups/person-aliases.csv` as `Who's Who: reading pass, N sources`. Git ignores `positions.csv` and `merge-candidates.csv`.

**Cost:** about 200k Sonnet tokens per batch. A normal night is one or two batches.
