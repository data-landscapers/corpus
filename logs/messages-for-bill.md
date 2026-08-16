---
type: log
title: Messages for Bill
last_reviewed: 2026-08-16
---

# Messages for Bill

*(Things an unattended run needed Bill for and could not ask. **Newest first**, one block per run. A job that runs while Bill is away never stops to put a question — it takes the deterministic path its runbook names, finishes the job, and writes what he would have been asked here. Bill reads this after a run and deletes what he has dealt with; nothing else clears it.)*

*(**It is not the run log.** `log.md` gets one line from every run, always, and is a skim of what happened. This file gets a block only when something is owed a decision or a look, so an empty file means the last runs needed nothing — which is the normal outcome.)*

*(**It is not `notes-for-osint.md`.** That file is findings that have to be actioned *in* OSINT and are carried across by hand. This one is Corpus's own business.)*

*(**Form.** A block per run, `## YYYY-MM-DD HH:MM · job`, then one bullet per item: what happened, what the run did about it, and what Bill's options are. Insert it directly under the marker below — appending puts the newest block at the bottom of a file that reads top-down, which is the failure nobody notices.)*

<!-- newest first: a new block goes directly below this line -->

## 2026-08-16 17:05 · status-init

- **A URL-splitting defect in `scripts/status_lib.py` was hiding 92 real source URLs from check A, and the 19 countries initialised before today were built against that narrower evidence set.** Cells in the AfDB dataset and the finance table that hold several URLs were split on `|`, `;` and whitespace but not on a bare comma, so `url1,url2,url3` was read as one token and every real URL in the row failed the held-set test. 108 rows across the dataset join their URLs that way. On TGO it silently dropped 10 facts at the pooling step, which is how it was found. **Fixed in this run** (commit "status_lib: split URL cells on a bare comma too"), one shared `_URL_SEP` now used by both set-builders, splitting on a comma only where a URL follows so paths containing commas survive; TGO's 10 facts came back.
  **This is the third instance of the same defect** — the pipe cost Egypt 15 facts and 46 URLs, the semicolon cost Uganda two, and each was fixed only in the one function it was found in, which is why a third separator was still there. Sharing the constant is what stops a fourth.
  **What is owed, and it is your call, not mine:** the 19 baselines already issued each dropped an unknown number of facts this way. Nothing in them is *wrong* — a dropped fact is a gap, not an error, and the asymmetry rule says gaps are the survivable kind. But they are thinner than they needed to be. The options are to leave them (cheapest, and the maintenance pass in `BUILD.md` will pick up anything material as new sources arrive), to re-pool and re-check them without re-running extraction (cheap — the fact JSONs are gone from `prep/`, so this is not actually available), or to re-run the affected countries in full (expensive). I would leave them and let maintenance close the gap, but the cost is yours to weigh.

- **Three facts were dropped before pooling on my judgement, not a rule the runbook states.** The IIAG/indicator agent attributed three specific claims to one URL out of a multi-URL row by inference, disclosed the inference, and marked them `borderline`. The borderline mechanism asks a writer to coarsen or drop the *claim* — it does not repair a *link* that may not establish the sentence, so coarsening would have left a possibly-wrong citation on the page. I dropped them. Civil registration turned out to be well covered by properly single-sourced facts, so nothing was lost. If you would rather the extraction brief said this explicitly, it is one line in `documentation/status-init-extract.md`.
