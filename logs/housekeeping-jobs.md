---
type: log
title: Corpus housekeeping register
---

# Housekeeping jobs

## NEXT JOB NUMBER: 6

*(Upkeep that is real, closable and CC's to do, but too big for the run that found it. None of it needs Bill, so none of it is a message. What earns a job and what reads this file: `CLAUDE.md` → *Be decisive*. Oldest first; take the number above, write the job, then increment it. A finished job is deleted in the commit that finishes it.)*

## 1 · Trim STATUS-INIT.md to the runbook cap

- **Cause:** runbooks record each incident where it happened; R92 moved that out of `documentation/` and left the root files.
- **Work:** 4,064 words against 1,500. Move the reasoning and the incident history to `documentation/`, as R92 did; the runbook keeps what to run.
- **Done when:** `python scripts/lint-docs.py` no longer names the file.

## 2 · Trim BUILD.md to the runbook cap

- **Cause:** as job 1.
- **Work:** 3,074 words against 1,500, the same way. The cycle runs on this file: change no step, only where its reasons live.
- **Done when:** `python scripts/lint-docs.py` no longer names the file.

## 3 · Trim CYCLE.md to the runbook cap

- **Cause:** as job 1.
- **Work:** 2,503 words against 1,500, the same way.
- **Done when:** `python scripts/lint-docs.py` no longer names the file.

## 4 · Trim CITE-REREAD.md to the runbook cap

- **Cause:** as job 1.
- **Work:** 2,042 words against 1,500, the same way.
- **Done when:** `python scripts/lint-docs.py` no longer names the file.

## 5 · Trim BUDGET-EXTRACT.md to the runbook cap

- **Cause:** as job 1.
- **Work:** 1,768 words against 1,500, the same way.
- **Done when:** `python scripts/lint-docs.py` exits 0, the other four being done.
