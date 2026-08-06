---
type: doc
title: CLAUDE.md — Corpus (the public site)
last_reviewed: 2026-08-06
---

# CLAUDE.md — Corpus

This repo holds the Phase 3 public site: design record, prototypes, and whatever is built to serve `outputs/`. `DESIGN.md` is the design record.

## The OSINT repo is read-only

**CC reads `C:\Users\bill\OSINT` and never writes to it.** No edits, no new files, no moves, no deletes, no git operations, no running of its procedure files. That includes `log.md`, `post-run-notes.md`, the review queues and every process file — the OSINT CLAUDE.md's "act, log after" applies to sessions run *in* OSINT, not to this project reaching across.

The reason is the direction of dependency. The site is a derived view of the wiki; a derived view that writes back to its own source destroys the property that makes it derivable. OSINT is also the store of record, so a mistake there is a data loss, whereas a mistake in Corpus is a rebuild.

**Everything CC produces goes in Corpus**, including anything about OSINT. If a change is needed *in* OSINT — a corrected path, a stale statement in a process file, a note for the queues — CC writes the finding as a numbered note in **`NOTES-FOR-OSINT.md`** and tells Bill; it does not make the change. Bill actions it in an OSINT session and strikes the note. That file also holds the standing constraints the site depends on, which never clear.

Reading is unrestricted: read any file, grep the whole tree, run read-only git commands, derive whatever the site needs.

## Committing

**Commit after every change, not at the end of a session** *(Bill, 2026-08-06)*. One commit per coherent change, with a terse subject saying what changed. An uncommitted working tree is the one state that is not reversible, and a session that batches its commits leaves everything since the last one at risk together.

**Deletes on this folder need permission once per session.** The sandbox blocks `unlink` on the Dropbox mount by default, which does not stop a commit but leaves `.git/HEAD.lock` behind — and that stale lock makes *every subsequent* commit fail with `cannot lock ref 'HEAD'`. Call `allow_cowork_file_delete` on any path in Corpus at the start of a session and git behaves normally thereafter. If commits start failing mid-session, look for stale `.lock` and `tmp_obj_*` files under `.git/` first.

## Writing

**One line per paragraph. Never wrap by hand.** Same rule as the wiki, and for the same reason: a hard-wrapped paragraph diffs badly, because changing one word near the start reflows every line after it and the diff shows a rewritten paragraph instead of a changed word. It does not apply where the break carries meaning — frontmatter, code blocks, tables.
