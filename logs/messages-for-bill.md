---
type: log
title: Messages for Bill
last_reviewed: 2026-08-28
---

# Messages for Bill

*(Things an unattended run needed Bill for and could not ask. **Newest first**, one block per run. Bill reads this after a run and deletes what he has dealt with; so does the run that settles a block's subject, in the commit that settles it. An empty file is the normal outcome — the run log gets a line from every run, this file gets a block only when something is owed a decision or a look. What earns a block, and why a finding carrying its own solution is a task instead: `CLAUDE.md` → *Be decisive*.)*

*(**Caps: five open blocks, 80 words a block**, counted by `python scripts/lint-messages.py` after writing here. **At the cap a run does not write a sixth — it takes the conservative option itself and logs it.** The word cap binds blocks dated 2026-08-28 or later.)*

*(**Form.** `## YYYY-MM-DD HH:MM · job`, then one bullet per item: what happened, what the run did about it, what Bill's options are. Insert directly under the marker — appending puts the newest block at the bottom of a file that reads top-down.)*

<!-- newest first: a new block goes directly below this line -->

## 2026-09-21 16:40 · build

- Liberia's monthly fails check J: the ledger's newest row (Cybercrime Act, 19 September) is already in the document, so the renderer keeps it unchanged and never advances `compiled:`. Nothing published is wrong. Left as is; the fix is in `report-render.py` (renderer or check J), a code change for a working session, not a cycle.

## 2026-09-21 00:20 · review

- **The non-state summary's year columns are the record's publication year, not the deal's.** `aggregate3` buckets each row by `published` while the downloadable row shows `start_year`; they agree on 1,339 of 1,453 rows and differ on 114, 26 of them by two years or more — a 2022 Comoros grant prints under 2025/26. Which field is authoritative is a data-quality judgement across the estate, not a run's. Left as compiled.


## 2026-09-18 12:40 · review

- **A US$4bn MoU is summed as committed digital finance.** Botswana's non-state table carries an Indian group's renewable-energy and transmission MoU at its full headline value, and the summary adds it to a signed World Bank loan in one Energy cell reading 4,088. The record is honest — instrument MoU, amount reported — so the question is Corpus's: should non-binding instruments be excluded from summary totals estate-wide, as unclear-scope lines already are? Left as compiled.

