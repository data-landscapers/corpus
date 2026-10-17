---
type: runbook
reader: cc
title: first-pass-batch.md — a batch of maturity studies, run cheaply and without stopping
last_reviewed: 2026-10-16
---

# The first pass: a batch of maturity studies

*(Bill, 2026-10-16.)* **Every indicator not yet studied gets a first pass, a batch at a time; accuracy comes later**, from the nightly rebuild, two indicators at a time (`MATURITY-UPDATE.md` → *The rebuild*). So the first pass spends as little as it can.

- **"run maturity batch {id or indicator, …}"** prepares and runs every indicator named, one study each, **without stopping** until all are committed, or until Bill says stop. **A stop is clean**: the indicator in hand is finished and committed, the rest are listed as not started, and nothing is left half-written. The batch starts in a fresh session; a compacted context mid-batch carries on.
- **Prepare the whole batch first, then read it together.** Every study file and `study.json` is written and `study-select.py` run for each before any reading starts. Then `python scripts/study-calls.py --batch {ids}` plans the reading: a story two studies list is read once, by one drafter answering each study's questions, and `--batch {ids} --fan` files the answers into each study. Each study's own calls follow, then `study-calls.py {id} --fan` and `study-profile.py --merge` per study.
- **Hard evidence is not chased.** A cell whose facts conflict, or whose rung turns on reading a document's text, is staged on the lower reading and its `note` starts *First pass:* with the doubt in a few words. No document is opened beyond the drafters' calls.
- **Skipped, left to the deep dive**: the second drafter (method §7.3), and the parent's re-reading of documents behind top-stage facts (method §7.2 checks the fact rows only).
- **`study.json` carries `"pass": "first"`**, which is how the deep dive knows what it owes, and `"story_cap"`, the batch's `--cap`, which the pages print *(the Registries batch, 2026-10-16)*.
- **One token ceiling for the batch**, stated before reading, checked with `study-tokens.py` after every fan-out. At the ceiling the batch stops cleanly, as above.
- **The cost is the call, not the document** *(the Data Exchange batch, 2026-10-16: 6% of the week for five indicators, which Bill ruled too much)*. 579 calls at a median 0.33M each whatever they read, six turns apiece, each resending the brief, two study files and a readlist of up to 74 KB. So: **the first pass reads the `about` rows only**. Pass `0`, the documents the frame's cells cite, was 57% of that spend for a fact from one document in three, and is left to the deep dive. **A call hands its drafter its rows and its questions inline**, not the whole readlist and study file to look up. Size the batch from the call count before reading; the Data Exchange batch's own-call count is the one to beat.
- **Cap the reading before the drafters start** *(the Digital Identity batch, 2026-10-16: 2,421 stories, about 500 calls, cut to 741 stories in 241 calls, 68M tokens for seven studies)*. `window_from` in `study.json` drops stories published before the three-year window, which can set no stage; `study-calls.py --batch … --cap N` keeps each country's N best-ranked stories across the batch. Fifteen was the cap, which Bill ruled good value; **use 20** from the next batch *(Bill, 2026-10-16)*. Studies sharing a subject should share most terms, so most stories are shared calls.
- **A story an earlier batch shared keeps its earlier answers.** `_batch/shared/{key}.json` is named for the story, so a drafter writing it again overwrites the earlier batch's studies: copy any planned key already present aside before reading, and merge its `studies` back after *(the Payments batch, 2026-10-16: seven files)*.
- **A measure whose figure `reference/measures.csv` holds is staged from it**, not asked as questions *(the Capacity batch, 2026-10-16)*: `study-figure.py {id} carry|ladder|write`, the frame's three cuts for stages 2 to 4 and its stage-5 condition read only where the figure clears the top line (`study-figure.py {id} cleared`). A measure with no held series is asked as four questions.
- **Commit `site/` on its own, after the evidence, and push each commit separately**; run `scripts/deploy-state.py` once it is pushed. One push carrying both is filtered as one *(the Payments batch, 2026-10-16: dispatched with `deploy-state.py --fix`)*. GitHub matches the deploy's path filter against a push's first 300 files only, so a batch commit of 3,600 files never deployed *(2026-10-16)*.
- **The batch ends on one report**: per indicator, countries staged, the stage counts, *First pass* cells, and tokens spent; then the questions written, in plain words, for Bill to read.

