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

OSINT's `CLAUDE.md` currently states the boundary with an exception in it: that OSINT reads CORPUS's request feed, `logs/requests-for-osint.csv`. **That exception was a design assumption and it is wrong.** An OSINT session cannot see `C:\CORPUS` at all — it is scoped to its own tree, which is the same isolation that keeps CORPUS out of OSINT, working in the other direction. The instruction asked for something the environment correctly refuses.

It was also unnecessary, which is the better reason to drop it. The requests only ever needed to reach an OSINT *session*, and a file was one assumption about how. Bill runs both sides; he can hand the open requests to the session directly, the way any acquisition brief arrives. `ACQUIRE` already knows what to do with a brief.

So the boundary loses its exception rather than gaining a workaround: **CORPUS reads OSINT, read-only. OSINT reads nothing from CORPUS, and writes nothing to it.** One direction, no exceptions, nothing to keep in step.

## The change

**Edit `CLAUDE.md`.** The boundary paragraph reads, today:

> **OSINT collects and classifies; CORPUS (`C:\CORPUS`) compiles, reports and analyses**, over a read-only view of `raw/`, `lookups/` and `wiki/`. OSINT writes nothing to CORPUS, and reads only CORPUS's request feed (`logs/requests-for-osint.csv`) — the one exception to that boundary.

Cut everything from *and reads only* onward, and close the sentence so it says OSINT neither writes to CORPUS nor reads from it — no exception, and no mention of a request feed. State plainly that an OSINT session cannot see `C:\CORPUS` and is not meant to.

**Add nothing to `ACQUIRE`.** No step that reads a CORPUS path, no parser for `requests-for-osint.csv`. If an earlier session added one, remove it. *(Checked from CORPUS on 2026-08-16: `ACQUIRE.md` has no such step, so this is a confirmation rather than a repair.)*

**Nothing else moves.** No sweep, no lint, no process file other than `CLAUDE.md`.

## How the requests reach OSINT instead

CORPUS keeps writing `logs/requests-for-osint.csv` — gaps and named documents its reports are missing. **That file is now purely CORPUS's own record**, not an interface: nothing in OSINT reads it, and OSINT does not need to know it exists.

When Bill opens an OSINT session with acquisitions to chase, he hands over the open requests as the session's brief. From OSINT's side there is nothing new to learn: a request is a brief, `ACQUIRE` runs as it always has, and what it fetches lands in `raw/` the ordinary way.

**Nothing is ever reported back.** A request is settled when CORPUS's next scan finds the record in `raw/` — CORPUS is watching the evidence, not waiting on a reply. So an OSINT session never marks a request closed, never edits a status, and never writes anywhere outside its own tree. If a request cannot be met, that is an ordinary dated absence in OSINT's own queues, and CORPUS will see the gap persist and re-raise it.
