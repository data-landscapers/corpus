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

## 2026-09-01 14:05 · build

- **The bulletin's 31 August to 1 September window holds one unsummarised item, a United Nations statistics page placed COM.** You said not to touch COM records, so the run left it unwritten and did not assemble: the bulletin keeps its current edition rather than publishing a gap. Everything else in the cycle ran. If the instruction meant the COM backfill rather than incidental COM sources, say so and the next run writes it.


## 2026-09-01 11:55 · build

- **`methodology-journey.md` was cut from 200 lines to 45 at 11:53, mid-word inside a bold marker — a partial write, not an edit.** Obsidian holds the vault open and wrote its workspace file in the same minute as the mirror pass. The run restored the committed version byte-identical. If you were editing it, your change is gone. That restored text is now split into `content/document-lifecycle.md` and `content/process-inventory.md`.

## 2026-08-28 22:41 · build

- **`report-register-check.py` read narrative markers only, so the 40 status baselines authored by STATUS-INIT scored nought words and had their register and check H pass over nothing while printing 0 hits.** Fixed: it now reads body paragraphs there. That exposes 218 register hits and 47 uncited figures across those documents. This run cleared KEN's and ZAF's; the rest is a report pass of about 38 documents, which is yours to commission or leave.

## 2026-08-20 16:05 · review

- **Swept this file against the current state and deleted nine blocks that are settled. Git holds every one.** Bill's instruction of 2026-08-20 was that both systems be more decisive and that his attention is the scarce thing; a message that has been true and unread for three days is not a message, it is a backlog. Each was verified before deletion, not assumed:
  - **2026-08-20 08:44** — the exchange-folder move. Bill executed it the same morning; `C:\corpus-osint-xfer\` is live, `status_lib.EXCHANGE` points at it, and check FM passes on all 30 baselines.
  - **2026-08-20 14:24** — whether a held origin should stop a bulletin summary. Answered: the remit filter went into `bulletin.py` the same day and eight out-of-remit records were dropped from the published bulletin.
  - **2026-08-19 06:47** — three country boxes and eight region boxes 404ing, plus `/method`. **Now zero**: all 107 internal hrefs on the home page resolve to a file on disk.
  - **2026-08-19 05:08, 2026-08-17 10:28, 09:40, 06:41** — the check-H campaign and the stale `record:` digests. Check H is **0 blocks corpus-wide**; the digests were rewritten by the next build, as those blocks predicted.
  - **2026-08-17 12:40** — a file held open in Excel. One-off, fixed by closing it.
  - **2026-08-16 17:05** — the URL-splitting defect in `status_lib.py`, and whether the 19 baselines built before the fix owed a rebuild. **They do not: no surviving baseline predates it.** Every one of the 35 issued carries `compiled:` of 2026-08-17 or later, so the narrower evidence set reached nothing that is still published.

- **Two standing questions are now decided rather than left open, both reversible and both Corpus's to call.** Neither needs an answer from Bill; both are recorded so that a later run does not re-raise them.
  - **IATI d-portal citations are verified upstream or not at all.** Nothing Corpus runs fetches a URL — check A is set membership against the catalogue, check G resolution through it — so no check here can tell a working `d-portal.org` link from a dead one. The alternative on the table was asking OSINT to emit a second, server-rendered form alongside each link, which is a change to OSINT's records to serve a Corpus check: the cross-repo dependency pattern to justify before building, not after. Left as is.
  - **BUILD does not cut sourced prose to hit a word count.** 78 documents sit outside the register's word band, NGA's monthly furthest at 4,781 words against 700–2,000. The band is tuned for a median place and Nigeria moved 145 rows this window; the check reports the overage and does not gate, which is the right arrangement. This stops being reported here every run.

- **One live defect was found while verifying the above, and it is fixed.** `report-register-check.py --unit all` matched a unit literally named `all` and reported `register: 0 hits; budget: 0 documents outside band; check H: 0` — a clean pass over nothing, indistinguishable from a genuinely clean corpus, while the same command with no `--unit` reported 78 documents outside band. `all` is now the documented synonym for the default and an unknown unit exits 2 with a message instead of sweeping nothing. I had nearly reported "check H is 0 corpus-wide" off the back of the false reading.
