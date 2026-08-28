---
type: log
title: Messages for Bill
last_reviewed: 2026-08-16
---

# Messages for Bill

*(Things an unattended run needed Bill for and could not ask. **Newest first**, one block per run. A job that runs while Bill is away never stops to put a question — it takes the deterministic path its runbook names, finishes the job, and writes what he would have been asked here. Bill reads this after a run and deletes what he has dealt with; nothing else clears it.)*

*(**It is not the run log.** `log.md` gets one line from every run, always, and is a skim of what happened. This file gets a block only when something is owed a decision or a look, so an empty file means the last runs needed nothing — which is the normal outcome.)*

*(**It is not `notes-for-osint.md`.** That file is findings that have to be actioned *in* OSINT and are carried across by hand. This one is Corpus's own business.)*

*(**The bar moved up on 2026-08-20** *(Bill)*. This file is for the **irreversible and the already-public** — evidence loss with no backup, a published page stating something false, leaked source text, legal exposure, a slug reissued under a live citation. Anything a later run can undo is decided by the run, taken the conservative way, and recorded in `logs/log.md`. `CLAUDE.md` → *Be decisive* has the rule. A run that writes nothing here is the normal outcome and always was; what changed is how much counts as owing him something.)*

*(**Caps: five open blocks, 80 words a block** — `python scripts/lint-messages.py` counts both, and a run runs it after writing here. **At the cap a run does not write a sixth block — it takes the conservative option itself and logs it in `logs/log.md`.** That is what converts queue pressure into decisions instead of backlog. The word cap binds blocks dated 2026-08-28 or later; detail belongs in git, analysis in `documentation/`.)*

*(**A finding that carries its own solution is a task, not a message** — do it and log it. OSINT's bar, from its housekeeping register, adopted here on 2026-08-20.)*

*(**Form.** A block per run, `## YYYY-MM-DD HH:MM · job`, then one bullet per item: what happened, what the run did about it, and what Bill's options are. Insert it directly under the marker below — appending puts the newest block at the bottom of a file that reads top-down, which is the failure nobody notices.)*

<!-- newest first: a new block goes directly below this line -->

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
