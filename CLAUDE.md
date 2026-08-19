---
type: doc
title: CLAUDE.md — Corpus (the public site)
last_reviewed: 2026-08-19
---

# CLAUDE.md — Corpus

This repo holds the Phase 3 public site: design record, prototypes, and whatever is built to serve `outputs/`. `documentation/design.md` is the design record.

**The global `CLAUDE.md` overrides this file** *(Bill, 2026-08-19)*. Committing and pushing, the writing rules, how to talk to Bill, the Cowork sandbox's quirks and the relationship between this repo and `data-landscapers` all live there now, because they are not Corpus's to decide and were drifting out of step with the other repo by being stated here. What is left below is only what is true of Corpus and of nowhere else. If a rule here contradicts the global file, the global file wins and this one is wrong.

## Corpus is an extension of data-landscapers

**They share style and functionality wherever possible** *(Bill, 2026-08-19)*, and the global file carries the rule. Two things follow that are Corpus's own business.

`site/assets/css/main.css` is a copy of the other repo's, and `MAIN-CSS-FROM` holds the commit it came from. The datatable component is the same arrangement: `data-landscapers/assets/shared/` is canonical, Corpus carries a copy at `site/assets/js/datatable.js` and `site/assets/css/datatable.css`, and `site/assets/DATATABLE-FROM` names the commit. **A copy is not sharing unless something notices when it goes stale**, so `scripts/lint-shared-assets.py` compares the bytes and reports drift; it fixes nothing, because copying in either direction is a destructive write on one of two repositories and picking the direction is a judgment about which repo is ahead.

**A change to a shared asset belongs upstream first.** Edit it in `data-landscapers/assets/shared/`, then copy down and update the marker. Editing the Corpus copy in place is how the two versions diverge, and the lint will tell you it happened but not which way round.

## The OSINT repo is read-only

**CC reads `C:\OSINT` and never writes to it, with exactly one exception: `C:\OSINT\osint-corpus-exchange\`.** No edits, no new files, no moves, no deletes, no git operations, no running of its procedure files anywhere else in the tree. That includes `log.md`, `post-run-notes.md`, the review queues and every process file — the OSINT CLAUDE.md's "act, log after" applies to sessions run *in* OSINT, not to this project reaching across.

**The exchange folder** *(Bill, 2026-08-17)* is a shared drop point, read/write from both sides, created to end the hand-copying of files between the two systems. Its own `README.md` states the same thing from OSINT's side. Nothing else is in the exception: `raw/`, `lookups/` and `wiki/` stay exactly as read-only as before, and a write anywhere in `C:\OSINT` outside that one folder is still the thing this rule exists to prevent.

The reason is the direction of dependency. The site is a derived view of the wiki; a derived view that writes back to its own source destroys the property that makes it derivable. OSINT is also the store of record, so a mistake there is a data loss, whereas a mistake in Corpus is a rebuild.

**Everything CC produces goes in Corpus**, including anything about OSINT. If a change is needed *in* OSINT — a corrected path, a stale statement in a process file, a note for the queues — CC writes the finding as a numbered note in **`osint-corpus-exchange/notes-for-osint.md`** and tells Bill; it does not make the change. Bill actions it in an OSINT session and strikes the note. That file also holds the standing constraints the site depends on, which never clear.

**What crosses to OSINT now sits in the exchange folder, but delivery is still Bill's call** *(Bill, 2026-08-17, replacing the hand-carrying of 2026-08-16)*. `osint-corpus-exchange/` holds `notes-for-osint.md`, its archive `notes-for-osint-resolved.md`, and the acquisition feed `africa-acquire.csv`. Both sides can now open the same file, which is the whole point of it — but **nothing in OSINT polls and no note is acted on until Bill says so**. An OSINT session reads a note only on his instruction, and may mark items done in the file; it does not go looking. So the old discipline survives its mechanism: CC still never writes anything whose delivery depends on OSINT noticing it by itself, and still never tells OSINT to read a `C:\CORPUS` path — a session there cannot see Corpus at all, which is the same isolation that keeps Corpus out of OSINT, working the other way. *(This was very nearly broken once already: `osint-migration.md` R9 asked `ACQUIRE` to read the request feed at a Corpus path, and was withdrawn on 2026-08-16 when a running OSINT session refused it. `documentation/archived/osint-no-request-feed.md` is the correction, and it still stands — the fix was to move the file to a path OSINT owns, not to point OSINT at Corpus.)*

**Two consequences of a shared file that a Corpus-only file did not have.** OSINT writes to these too, so **CC is no longer the only author**: re-read before editing, never write back a copy held from earlier in a session, and treat an unexpected change as OSINT's rather than as corruption. And the folder is **outside Corpus's git but inside OSINT's**, with no ignore rule excluding it, so **OSINT's commits are what version these files from here** — Corpus's history for them stops at the 2026-08-17 move. The remaining channel that has not moved is the instruction documents in `documentation/`, which are still Corpus-side and still carried by hand. *(The old request feed `logs/requests-for-osint.csv` is not a channel any more: it holds a header row and nothing else, and the attempt to have OSINT read it directly was withdrawn — see `documentation/archived/osint-no-request-feed.md`. It is left in place, empty, rather than deleted.)*

Reading is unrestricted: read any file, grep the whole tree, run read-only git commands, derive whatever the site needs.

## Editions

**A published file is never revised.** `RENDER.md` §9 is the full rule and the scripts implement it; what matters here is that the dated CSVs and PDFs under `site/` are citable artefacts, so a rebuild that rewrites one in place has broken something even when the content is identical. `RENDER.md` → *The finance tables* carries the trap this most often springs through, which is line endings under a Cowork build.
