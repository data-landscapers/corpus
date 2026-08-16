---
type: doc
title: OSINT — correct the boundary, there is no request feed
last_reviewed: 2026-08-16
audience: OSINT (Bill, or a colleague's session run *in* OSINT)
status: written in Corpus — to be actioned in an OSINT session
---

# Correct the boundary: OSINT reads nothing from CORPUS

*(Written from CORPUS, for OSINT. **Self-contained — it assumes nothing about the migration list in `osint-migration.md` and needs none of it read first.** One change, one file, a few minutes. One line per paragraph, OSINT house style.)*

## Why

OSINT's `CLAUDE.md` currently states the boundary with an exception in it: that OSINT reads CORPUS's request feed, `logs/requests-for-osint.csv`. **That exception was a design assumption and it is wrong.**

**`C:\CORPUS` is not reachable from the machine OSINT runs on**, as the 2026-08-16 09:44 entry in `logs/log.md` already records: that session reaches OSINT over `\\bill-vivobook\OSINT`, and only that share and `\Users` are exposed. CORPUS is a directory on a different machine. This is topology, not a permission that could be granted, and **the repair is not to share the folder** — doing that would reopen a dependency that is being closed deliberately, for the reason below.

It was also unnecessary, which is the better reason to drop it. The requests only ever needed to reach an OSINT *session*, and a file was one assumption about how. Bill runs both sides; he can hand the open requests to the session directly, the way any acquisition brief arrives. `ACQUIRE` already knows what to do with a brief.

So the boundary loses its exception rather than gaining a workaround: **CORPUS reads OSINT, read-only. OSINT reads nothing from CORPUS, and writes nothing to it.** One direction, no exceptions, nothing to keep in step.

## The change

**Edit `CLAUDE.md`.** The boundary paragraph reads, today:

> **OSINT collects and classifies; CORPUS (`C:\CORPUS`) compiles, reports and analyses**, over a read-only view of `raw/`, `lookups/` and `wiki/`. OSINT writes nothing to CORPUS, and reads only CORPUS's request feed (`logs/requests-for-osint.csv`) — the one exception to that boundary.

Cut everything from *and reads only* onward, and close the sentence so it says OSINT neither writes to CORPUS nor reads from it — no exception, and no mention of a request feed. State plainly that an OSINT session cannot see `C:\CORPUS` and is not meant to.

**Add nothing to `ACQUIRE`.** No step that reads a CORPUS path, no parser for `requests-for-osint.csv`. If an earlier session added one, remove it. *(Checked from CORPUS on 2026-08-16: `ACQUIRE.md` has no such step, so this is a confirmation rather than a repair.)*

**Correct the two briefs OSINT committed into its own `documentation/`.** Both predate this decision and both still instruct a reader to wire the feed, so a later session — or the Fable pass reviewing the migration — will otherwise act on them:

- **`documentation/osint-migration.md`** — OSINT's copy is a snapshot taken before R9 was withdrawn. Three places still carry the exception: the boundary paragraph near the top (*"with one exception (the request feed, task R9)"*), **R9** itself, and **R10**'s quoted boundary sentence (*"reads only the R9 request feed"*). Strike R9 as withdrawn and correct the other two. CORPUS's copy is the authoritative one and is already corrected; this one only needs to stop contradicting it.
- **`documentation/cc-reset-instructions-2026-08-16.md`** — item 1's boundary sentence carries the same clause, and **item 6 is R9 in full**. Strike item 6 and fix item 1.

**Nothing else moves.** No sweep, no lint, no process file other than `CLAUDE.md` and those two briefs.

## How the requests reach OSINT instead

CORPUS keeps writing `logs/requests-for-osint.csv` — gaps and named documents its reports are missing. **That file is now purely CORPUS's own record**, not an interface: nothing in OSINT reads it, and OSINT does not need to know it exists.

When Bill opens an OSINT session with acquisitions to chase, he hands over the open requests as the session's brief. From OSINT's side there is nothing new to learn: a request is a brief, `ACQUIRE` runs as it always has, and what it fetches lands in `raw/` the ordinary way.

**Nothing is ever reported back.** A request is settled when CORPUS's next scan finds the record in `raw/` — CORPUS is watching the evidence, not waiting on a reply. So an OSINT session never marks a request closed, never edits a status, and never writes anywhere outside its own tree. If a request cannot be met, that is an ordinary dated absence in OSINT's own queues, and CORPUS will see the gap persist and re-raise it.
