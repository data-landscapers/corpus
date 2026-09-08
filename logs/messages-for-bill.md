---
type: log
title: Messages for Bill
last_reviewed: 2026-08-28
---

# Messages for Bill

*(Things an unattended run needed Bill for and could not ask. **Newest first**, one block per run. Bill reads this after a run and deletes what he has dealt with; nothing else clears it. An empty file is the normal outcome — the run log gets a line from every run, this file gets a block only when something is owed a decision or a look. What earns a block, and why a finding carrying its own solution is a task instead: `CLAUDE.md` → *Be decisive*.)*

*(**Caps: five open blocks, 80 words a block**, counted by `python scripts/lint-messages.py` after writing here. **At the cap a run does not write a sixth — it takes the conservative option itself and logs it.** The word cap binds blocks dated 2026-08-28 or later.)*

*(**Form.** `## YYYY-MM-DD HH:MM · job`, then one bullet per item: what happened, what the run did about it, what Bill's options are. Insert directly under the marker — appending puts the newest block at the bottom of a file that reads top-down.)*

<!-- newest first: a new block goes directly below this line -->

## 2026-09-08 15:10 · catalogue split

- The title shards are **uploaded and verified** — 2,283 objects, 29.4 MB, and
  `--verify` passes on all 7,965 in the bucket. What is left is **deploying
  `workers/download-log/worker.js`**, whose `R2_PREFIX` now carries
  `catalogue/titles/`; until it goes, the live page 404s every title shard and search
  reaches publishers, actors and source names but not titles. The test after
  deploying: `digital public infrastructure` returns 259, not 245.







