---
type: doc
title: CLAUDE.md — Corpus (the public site)
last_reviewed: 2026-08-06
---

# CLAUDE.md — Corpus

This repo holds the Phase 3 public site: design record, prototypes, and whatever is built to serve `outputs/`. `documentation/design.md` is the design record.

## The OSINT repo is read-only

**CC reads `C:\OSINT` and never writes to it.** No edits, no new files, no moves, no deletes, no git operations, no running of its procedure files. That includes `log.md`, `post-run-notes.md`, the review queues and every process file — the OSINT CLAUDE.md's "act, log after" applies to sessions run *in* OSINT, not to this project reaching across.

The reason is the direction of dependency. The site is a derived view of the wiki; a derived view that writes back to its own source destroys the property that makes it derivable. OSINT is also the store of record, so a mistake there is a data loss, whereas a mistake in Corpus is a rebuild.

**Everything CC produces goes in Corpus**, including anything about OSINT. If a change is needed *in* OSINT — a corrected path, a stale statement in a process file, a note for the queues — CC writes the finding as a numbered note in **`logs/notes-for-osint.md`** and tells Bill; it does not make the change. Bill actions it in an OSINT session and strikes the note. That file also holds the standing constraints the site depends on, which never clear.

**Everything crossing to OSINT is carried by Bill, by hand** *(Bill, 2026-08-16 — "for the moment", so this is current practice rather than a permanent property)*. There are three channels and no others: `logs/notes-for-osint.md`, the request feed `logs/requests-for-osint.csv`, and instruction documents written in `documentation/`. **All three are inert** — Corpus writes them and stops. Nothing in OSINT reads them, nothing polls, and no OSINT session fetches anything from Corpus: a session there cannot see `C:\CORPUS` at all, which is the same isolation that keeps Corpus out of OSINT, working the other way. So CC never writes anything whose delivery depends on OSINT reaching across for it, and never tells OSINT to read a Corpus path. *(This was very nearly not true: `osint-migration.md` R9 asked `ACQUIRE` to read the request feed directly, and was withdrawn on 2026-08-16 when a running OSINT session refused the path. `documentation/archived/osint-no-request-feed.md` is the correction.)*

Reading is unrestricted: read any file, grep the whole tree, run read-only git commands, derive whatever the site needs.

## Committing

**Commit after every change, not at the end of a session** *(Bill, 2026-08-06)*. One commit per coherent change, with a terse subject saying what changed. An uncommitted working tree is the one state that is not reversible, and a session that batches its commits leaves everything since the last one at risk together.

**Deletes (Cowork sessions only).** In a Cowork session the sandbox blocks `unlink` on its mount, which does not stop a commit but leaves a stale `.git/HEAD.lock` that then makes *every subsequent* commit fail with `cannot lock ref 'HEAD'`; call `allow_cowork_file_delete` on any path in Corpus once at the start of a Cowork session. This does not apply to Claude Code running on the machine — Corpus is off Dropbox now, and there is no such tool there. The general symptom is still worth knowing either way: if commits start failing mid-session, look for stale `.lock` and `tmp_obj_*` files under `.git/` first.

## Communication with Bill

**Do not use the word "honest" (or "honestly").** *(Bill, 2026-08-13.)* A cross-project preference; promote it to the global `~/.claude/CLAUDE.md` for it to apply everywhere.

## Writing

**One line per paragraph. Never wrap by hand.** Same rule as the wiki, and for the same reason: a hard-wrapped paragraph diffs badly, because changing one word near the start reflows every line after it and the diff shows a rewritten paragraph instead of a changed word. It does not apply where the break carries meaning — frontmatter, code blocks, tables.
