---
type: doc
title: CLAUDE.md — Corpus (the public site)
last_reviewed: 2026-08-06
---

# CLAUDE.md — Corpus

This repo holds the Phase 3 public site: design record, prototypes, and whatever is built to serve `outputs/`. `documentation/design.md` is the design record.

## The OSINT repo is read-only

**CC reads `C:\OSINT` and never writes to it, with exactly one exception: `C:\OSINT\osint-corpus-exchange\`.** No edits, no new files, no moves, no deletes, no git operations, no running of its procedure files anywhere else in the tree. That includes `log.md`, `post-run-notes.md`, the review queues and every process file — the OSINT CLAUDE.md's "act, log after" applies to sessions run *in* OSINT, not to this project reaching across.

**The exchange folder** *(Bill, 2026-08-17)* is a shared drop point, read/write from both sides, created to end the hand-copying of files between the two systems. Its own `README.md` states the same thing from OSINT's side. Nothing else is in the exception: `raw/`, `lookups/` and `wiki/` stay exactly as read-only as before, and a write anywhere in `C:\OSINT` outside that one folder is still the thing this rule exists to prevent.

The reason is the direction of dependency. The site is a derived view of the wiki; a derived view that writes back to its own source destroys the property that makes it derivable. OSINT is also the store of record, so a mistake there is a data loss, whereas a mistake in Corpus is a rebuild.

**Everything CC produces goes in Corpus**, including anything about OSINT. If a change is needed *in* OSINT — a corrected path, a stale statement in a process file, a note for the queues — CC writes the finding as a numbered note in **`osint-corpus-exchange/notes-for-osint.md`** and tells Bill; it does not make the change. Bill actions it in an OSINT session and strikes the note. That file also holds the standing constraints the site depends on, which never clear.

**What crosses to OSINT now sits in the exchange folder, but delivery is still Bill's call** *(Bill, 2026-08-17, replacing the hand-carrying of 2026-08-16)*. `osint-corpus-exchange/` holds `notes-for-osint.md`, its archive `notes-for-osint-resolved.md`, and the acquisition feed `africa-acquire.csv`. Both sides can now open the same file, which is the whole point of it — but **nothing in OSINT polls and no note is acted on until Bill says so**. An OSINT session reads a note only on his instruction, and may mark items done in the file; it does not go looking. So the old discipline survives its mechanism: CC still never writes anything whose delivery depends on OSINT noticing it by itself, and still never tells OSINT to read a `C:\CORPUS` path — a session there cannot see Corpus at all, which is the same isolation that keeps Corpus out of OSINT, working the other way. *(This was very nearly broken once already: `osint-migration.md` R9 asked `ACQUIRE` to read the request feed at a Corpus path, and was withdrawn on 2026-08-16 when a running OSINT session refused it. `documentation/archived/osint-no-request-feed.md` is the correction, and it still stands — the fix was to move the file to a path OSINT owns, not to point OSINT at Corpus.)*

**Two consequences of a shared file that a Corpus-only file did not have.** OSINT writes to these too, so **CC is no longer the only author**: re-read before editing, never write back a copy held from earlier in a session, and treat an unexpected change as OSINT's rather than as corruption. And the folder is **outside Corpus's git and currently untracked in OSINT's**, so nothing versions it — which is why the note asking OSINT to commit it matters more than it looks. The remaining channel that has not moved is the instruction documents in `documentation/`, which are still Corpus-side and still carried by hand. *(The old request feed `logs/requests-for-osint.csv` is not a channel any more: it holds a header row and nothing else, and the attempt to have OSINT read it directly was withdrawn — see `documentation/archived/osint-no-request-feed.md`. It is left in place, empty, rather than deleted.)*

Reading is unrestricted: read any file, grep the whole tree, run read-only git commands, derive whatever the site needs.

## Committing

**Commit after every change, not at the end of a session** *(Bill, 2026-08-06)*. One commit per coherent change, with a terse subject saying what changed. An uncommitted working tree is the one state that is not reversible, and a session that batches its commits leaves everything since the last one at risk together.

**Deletes (Cowork sessions only).** In a Cowork session the sandbox blocks `unlink` on its mount, which does not stop a commit but leaves a stale `.git/HEAD.lock` that then makes *every subsequent* commit fail with `cannot lock ref 'HEAD'`; call `allow_cowork_file_delete` on any path in Corpus once at the start of a Cowork session. This does not apply to Claude Code running on the machine — Corpus is off Dropbox now, and there is no such tool there. The general symptom is still worth knowing either way: if commits start failing mid-session, look for stale `.lock` and `tmp_obj_*` files under `.git/` first.

## Communication with Bill

**Do not use the word "honest" (or "honestly").** *(Bill, 2026-08-13.)* A cross-project preference; promote it to the global `~/.claude/CLAUDE.md` for it to apply everywhere.

## Writing

**One line per paragraph. Never wrap by hand.** Same rule as the wiki, and for the same reason: a hard-wrapped paragraph diffs badly, because changing one word near the start reflows every line after it and the diff shows a rewritten paragraph instead of a changed word. It does not apply where the break carries meaning — frontmatter, code blocks, tables.
