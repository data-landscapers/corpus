---
type: runbook
reader: cc
title: first-pass-batch.md — a batch of maturity studies, run cheaply and without stopping
last_reviewed: 2026-10-16
---

# The first pass: a batch of maturity studies

*(Bill, 2026-10-16.)* **Every indicator not yet studied gets a first pass, a batch at a time; accuracy comes later**, from the nightly deep dive of one indicator at a time (`MATURITY-UPDATE.md` → *The rotation*). So the first pass spends as little as it can.

- **"run maturity batch {id or indicator, …}"** prepares and runs every indicator named, one study each, **without stopping** until all are committed, or until Bill says stop. **A stop is clean**: the indicator in hand is finished and committed, the rest are listed as not started, and nothing is left half-written. The batch starts in a fresh session; a compacted context mid-batch carries on.
- **Prepare the whole batch first, then read it together.** Every study file and `study.json` is written and `study-select.py` run for each before any reading starts. Then `python scripts/study-calls.py --batch {ids}` plans the reading: a story two studies list is read once, by one drafter answering each study's questions, and `--batch {ids} --fan` files the answers into each study. Each study's own calls follow, then `study-calls.py {id} --fan` and `study-profile.py --merge` per study.
- **Hard evidence is not chased.** A cell whose facts conflict, or whose rung turns on reading a document's text, is staged on the lower reading and its `note` starts *First pass:* with the doubt in a few words. No document is opened beyond the drafters' calls.
- **Skipped, left to the deep dive**: the second drafter (method §7.3), and the parent's re-reading of documents behind top-stage facts (method §7.2 checks the fact rows only).
- **`study.json` carries `"pass": "first"`**, which is how the deep dive knows what it owes.
- **One token ceiling for the batch**, stated before reading, checked with `study-tokens.py` after every fan-out. At the ceiling the batch stops cleanly, as above.
- **The batch ends on one report**: per indicator, countries staged, the stage counts, *First pass* cells, and tokens spent; then the questions written, in plain words, for Bill to read.

