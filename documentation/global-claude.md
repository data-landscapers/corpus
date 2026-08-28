---
type: doc
title: global CLAUDE.md — the cross-project rules
last_reviewed: 2026-08-19
---

# CLAUDE.md — global

**This file overrides every project's own `CLAUDE.md`** *(Bill, 2026-08-19)*. A project file says what is true of that project and nothing else; anything true of more than one belongs here. Where the two disagree, this one is right and the project file is out of date.

**It lives in Corpus and is pulled in by reference.** The user-level `~/.claude/CLAUDE.md` holds one line — `@C:\CORPUS\documentation\global-claude.md` — and nothing else. The reason is that the user-level file sits in an application directory that a Cowork session cannot reach, so the rules governing every session were the one document no session could edit; here they are writable, versioned, diffable and reviewable like anything else. The cost is a dependency: if the import ever stops resolving, **every** project loses its rules at once rather than one of them losing some, so a session that cannot see these rules should say so rather than proceed on the project file alone.

## Folder access

All projects should have these three folders attached; if any is missing, warn me before starting work.

- Corpus : `C:\CORPUS`
- Data-landscapers : `C:\Users\bill\Dropbox\Github\data-landscapers`
- OSINT : `C:\OSINT`

Cowork and Claude Code have read/write on Corpus and Data-landscapers. **Neither ever writes to OSINT, and there is no longer an exception** *(2026-08-20)*. What used to be one — a shared folder inside `C:\OSINT` — has moved out of both repositories to `C:\corpus-osint-xfer\`, a git repository of its own that Bill gives OSINT access to. That retires the exception rather than relocating it, because `C:\OSINT` is a **mirror**: a write there is discarded at the next sync, so it was never a delivery. Corpus's own `CLAUDE.md` carries the reasoning and the mechanics, and the share's `README.md` describes what is in it.

## Corpus is an extension of data-landscapers

**They share style and functionality wherever possible.** Corpus is not a separate product with a family resemblance — it is the same site, serving the compiled base, and a reader crossing from one to the other should not be able to tell where the boundary was. Type, colour, chrome, components, the way a table behaves: one decision, applied twice.

**Shared code has one canonical copy, and it lives in data-landscapers.** `assets/shared/` is where it sits. Corpus carries duplicates rather than loading across domains, because the two repositories deploy separately and a cross-origin `<script src>` means every Corpus table losing its table the day a path moves on the other side. A duplicate is therefore always accompanied by a `{NAME}-FROM` file naming the commit it was taken from, and by something that checks it — `MAIN-CSS-FROM` for the stylesheet, `DATATABLE-FROM` and `scripts/lint-shared-assets.py` for the table component. **A copy nothing checks is not sharing; it is two files that used to agree.**

**Improve a shared thing upstream, then copy down.** A fix made in the Corpus copy is a fix the other site does not get, and the next copy down silently reverts it.

## Committing

**Commit after every change, not at the end of a session** *(Bill, 2026-08-06)*. One commit per coherent change, with a terse subject saying what changed. An uncommitted working tree is the one state that is not reversible, and a session that batches its commits leaves everything since the last one at risk together.

**Push what you commit** *(Bill, 2026-08-19)*. A commit that exists only on this machine is not backed up, and nothing on the other side of the division of labour can see it — CC cannot review what Cowork has not pushed, and vice versa. Push at the end of the working sequence a commit belongs to, not necessarily after every single one.

**A Cowork session cannot push, and must say so.** Its Linux sandbox has no git credentials and no terminal to prompt on, so `git push` fails with `could not read Username for 'https://github.com'`; anonymous *read* works, which is why `git ls-remote` and `git fetch` are fine and only the push is not. There is no fix from inside the session — not a missing flag, and no connector in the registry covers it. So a Cowork session **ends by naming the commits it has left unpushed**, and Bill or a Claude Code session pushes. Not mentioning it is the actual failure: an unpushed commit nobody has been told about is indistinguishable from work that was never done.

## The Cowork sandbox

Two things behave differently there, and both have bitten already.

**Deletes are blocked on the mount.** `unlink` fails, which does not stop a commit but leaves a stale `.git/HEAD.lock`, and *every subsequent* commit then fails with `cannot lock ref 'HEAD'`. Call `allow_cowork_file_delete` once per repo at the start of the session. If commits start failing mid-session, look for stale `.lock` and `tmp_obj_*` files under `.git/` first. This does not apply to Claude Code on the machine.

**Line endings differ, and it churns published files.** Python's `csv.writer` emits `\r\n`; git on Windows normalises that to LF on commit and git on Linux does not. So a rebuild run in Cowork rewrites every generated CSV with CRLF and git reports the whole file changed though not a character of content moved. Where those files are dated editions, that is a published artefact being revised, which is exactly what the edition rule forbids. **Check for CR-only churn before committing a rebuild**, and restore what it catches:

```bash
for f in $(git diff --name-only); do [ -z "$(git diff --ignore-cr-at-eol -- "$f")" ] && git checkout HEAD -- "$f"; done
```

A `.gitattributes` would settle it permanently, but enough tracked files already hold CRLF that adding one renormalises them in a single commit — worth doing in a session spent on that and nothing else.

## Division of labour — Cowork and Claude Code

Best practice rather than a rule. **Design work takes place in Cowork; operational running takes place in Claude Code.**

Whenever Cowork makes changes, I ask CC to review them from an operational point of view. Depending on CC's response I will either ask CC to write a note for Cowork, post CC's comments back to Cowork, or ask CC to make modifications to Cowork's work.

## Writing

**One line per paragraph. Never wrap by hand.** A hard-wrapped paragraph diffs badly: change one word near the start and every following line reflows, so the diff shows a rewritten paragraph instead of a changed word. It does not apply where the break carries meaning — frontmatter, code blocks, tables.

## Talking to me

**Do not use the word "honest" or "honestly".** This covers prose written for Bill and prose written into any project's own files and published output — not verbatim quotation of someone else's words, where changing it would misquote.

**Say what is unverified.** Where something has been checked, say how; where it has not — a layout nothing rendered, a number nothing recomputed — say that plainly rather than letting the confident parts of an answer carry the unchecked parts along with them.
