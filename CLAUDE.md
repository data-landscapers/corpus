---
type: doc
title: CLAUDE.md — Corpus (the public site)
last_reviewed: 2026-08-28
---

# CLAUDE.md — Corpus

This repo holds the Phase 3 public site: design record, prototypes, and whatever is built to serve `outputs/`. `documentation/design.md` is the design record.

**The global `CLAUDE.md` overrides this file.** Committing and pushing, the writing rules, how to talk to Bill, the Cowork sandbox's quirks and the relationship between this repo and `data-landscapers` live there; what is below is only what is true of Corpus and of nowhere else. If a rule here contradicts the global file, the global file wins and this one is wrong.

## Corpus is an extension of data-landscapers

**They share style and functionality wherever possible.** Two consequences are Corpus's own business:

`site/assets/css/main.css` is a copy of the other repo's, and `MAIN-CSS-FROM` holds the commit it came from. The datatable is the same arrangement: `data-landscapers/assets/shared/` is canonical, Corpus carries copies at `site/assets/js/datatable.js` and `site/assets/css/datatable.css`, and `site/assets/DATATABLE-FROM` names the commit. **A copy is not sharing unless something notices when it goes stale**: `scripts/lint-shared-assets.py` compares the bytes and reports drift. It fixes nothing — copying in either direction is a destructive write on one of two repositories, and picking the direction is a judgement about which repo is ahead.

**A change to a shared asset belongs upstream first.** Edit it in `data-landscapers/assets/shared/`, then copy down and update the marker. Editing the Corpus copy in place is how the two versions diverge.

## The OSINT repo is read-only

**CC reads `C:\OSINT` and never writes to it, without exception.** No edits, no new files, no moves, no deletes, no git operations, no running of its procedure files anywhere else in the tree — including `log.md`, the review queues and every process file. Writing is what the boundary forbids; **what CC may read is now bounded too, by the interface below** — the prohibition on writing has not narrowed, and never does.

**The interface is data, and it is the whole of what CC reads.** CC may read OSINT's **`raw/`**, **`wiki/`** and **`lookups/`** — the evidence and the vocabularies — and the mirror's own git metadata as a staleness clock. It may **not** read OSINT's `logs/`, `reviews/`, `index/`, `new/`, `sweep/` or any process file. Nothing physically stops a wider read; what changed is that a wider read is no longer permitted. Because nothing defined what Corpus may rely on, Corpus read everything and policed what it found — dedicated linters over OSINT's internal logs, forensic parsing of `ingested_log.md`, incident histories of OSINT's defects carried in docstrings. `scripts/lint-interface.py` counts it: the workroot junction list and every OSINT path a script builds, with today's two log reads named as exceptions that retire on the cycle manifest. A read outside the set fails; so does an exception that no longer applies, so the list shrinks rather than settling in. **An observation about OSINT that does not change a Corpus output is not logged, not noted and not mentioned** — the same test the note template applies. The rule is symmetrical: OSINT reads Corpus's data through the share and never its `logs/`, `documentation/` or runbooks.

**`C:\OSINT` is a mirror.** The master OSINT repo lives on OSINT's own drive; the mirror is refreshed when a `SWEEP-CYCLE` completes, after every OSINT commit, or by hand. Two consequences:

- A file **read** from the mirror reads as whatever the last sync left — a folder absent from the mirror reads as empty, which is not the same as empty.
- A file **written** to the mirror is discarded at the next sync — a write there is not a delivery, it is a delay before the change disappears.

The shared drop point is **`C:\corpus-osint-xfer\`**, outside both repos. Corpus writes there and nowhere in `C:\OSINT` at all. (`scripts/status_lib.py` → `EXCHANGE` is the one path that has to agree, overridable by `CORPUS_OSINT_XFER`.)

The reason is the direction of dependency. The site is a derived view of the wiki; a derived view that writes back to its source destroys the property that makes it derivable. OSINT is also the store of record — the master, not the mirror — so a mistake there is a data loss, whereas a mistake in Corpus is a rebuild. That the mirror is cheap to restore is not a licence to write to it: a write CC cannot see the fate of is worse than one it is refused.

## Be decisive — the bar for asking has moved up

**Bill is not the bottleneck any of this should route through.** Take the action; where it is not CC's to take, decide what should happen and write that. The analysis behind a decision goes in `documentation/`, read once by whoever maintains the file, not in the thing Bill opens. A note or message ending in a question CC could have answered by reading two more files is CC's own work, unfinished.

**The escalation test is reversibility, not importance.** If a later run can undo it, act now and record it. Reserve Bill's attention for the irreversible and the already-public: evidence loss with no backup, a published page stating something false, a leak of source text, a legal or licensing exposure, a slug reissued under a live citation. `logs/messages-for-bill.md` holds what a run would have asked, **capped at five open blocks of at most 80 words each** (`scripts/lint-messages.py` counts both): at the cap a run does not write a sixth — it takes the conservative option and logs it. A run that takes the conservative option and states it plainly is finished, not deferred.

**A finding that carries its own solution is a task, not a message** — do it and log it.

**Notes for OSINT carry `[CRITICAL]`, `[ACT]` or `[FYI]`**, defined in the share's `README.md` → *Conventions*; the same reversibility test picks the tag. Most of what used to be a decision request is an `[ACT]` with the conservative option already taken.

**None of this touches the boundaries.** OSINT stays read-only, the metadata-only commitment on `outputs/` holds, and a destructive or outward-facing step still gets confirmed. Being decisive is not licence to widen what CC may touch.

## The exchange

**Everything CC produces goes in Corpus**, including anything about OSINT. If a change is needed *in* OSINT — a corrected path, a stale statement, a note for the queues — CC writes it as a numbered note in **`C:\corpus-osint-xfer\notes-for-osint.md`** and tells Bill; it does not make the change. Bill actions it in an OSINT session and strikes the note.

**`C:\corpus-osint-xfer\` holds the channel files, and delivery is Bill's call.** `notes-for-osint.md` and `notes-for-corpus.md` with an archive apiece (`…-resolved.md`), OSINT's housekeeping register `housekeeping-jobs.md` and its archive, the acquisition feed `africa-acquire.csv` and its far end `acquire-done.csv`, and **`new-queue/`, Bill's hand-carry into OSINT** — a file left there is **not** queued for ingest until he moves it, so say so when leaving one. The share's own `README.md` is the canonical description of all of it, for both sides.

**The share's `README.md` is where the channel conventions live, and a channel file carries a pointer to it rather than a copy.** `scripts/lint-preambles.py` holds each preamble to 250 words and fails on a rule restated away from home — a rule stated twice is one that will eventually disagree with itself. It reports rather than fails on `housekeeping-jobs.md` and `messages-from-bill.md`, which are OSINT's and Bill's; OSINT asserts the same over its own files from `LINT.md` #24. Run it whenever the share is edited.

**Nothing in OSINT polls, and no note is acted on until Bill says so.** Never write anything whose delivery depends on OSINT noticing it by itself, and never tell OSINT to read a `C:\CORPUS` path — a session there cannot see Corpus at all, the same isolation that keeps Corpus out of OSINT. The instruction documents in `documentation/` remain Corpus-side and hand-carried. (The retired request feed `logs/requests-for-osint.csv` holds a header row and nothing else, and is left in place.)

**Closing a note means moving it out, and nothing is left at the number.** When CC resolves or withdraws a note, the full text and every dated annotation go to the resolved file and nothing stays behind; the open file carries what is still owed and nothing else. **Numbers are never reused and the gap stays** — the resolved file is where a closed number resolves, which is what keeps numbers citable. OSINT runs the same rule on its files; the share's `README.md` states it for all three.

**Two consequences of a shared file.** OSINT writes to these too, so CC is not the only author: **re-read before editing**, never write back a copy held from earlier in a session, and treat an unexpected change as OSINT's rather than as corruption. And the folder is **its own git repository** (remote: `data-landscapers/CORPUS-OSINT-XFER`), where **CC does the committing, for both sides**. Three things follow, none optional:

- **Check the share for uncommitted work on opening it and again before finishing** — that is what makes OSINT writing and stopping safe.
- **Push immediately after committing, never at the end of a session** — in a repository two systems reach through different paths, an unpushed commit is exactly as invisible as an uncommitted edit.
- **Name OSINT in the subject line when the work is OSINT's** — a shared history that misattributes who said what has lost the one thing it was keeping.

## Editions

**A published file is never revised.** `documentation/design.md` §9 is the full rule and the scripts implement it: the dated CSVs and PDFs under `site/` are citable artefacts, so a rebuild that rewrites one in place has broken something even when the content is identical. `RENDER.md` → *The finance tables* carries the trap this most often springs through — line endings under a Cowork build.
