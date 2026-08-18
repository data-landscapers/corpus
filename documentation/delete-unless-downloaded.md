---
type: design-note
title: Delete unless downloaded
last_reviewed: 2026-08-18
status: design note — not yet a decision
---

# Delete unless downloaded

*(Bill's simplification, 2026-08-18, of `documentation/download-archive-design.md`. That note proposed a gateway that minted an artefact into a permanent archive the first time anyone downloaded it. This is the same instinct — keep only what someone wanted — arrived at from the other end, and it needs far less machinery. One line per paragraph.)*

## The rule

**When RENDER supersedes an edition, it deletes the old one — unless that edition was downloaded.**

That is the whole of it. Everything below is why it works, what it needs, and what it does not fix.

## What it is for

**Retention is unconditional today, and that is what makes it expensive.** Every dated PDF is kept for ever because §9 promises that a citation stays checkable — 1,053 of them and 314 MB in the thirteen days from 2026-08-05, before the content gate went in and slowed the rate to real movement. Most of those editions will never be opened by anyone.

**But retention exists for readers, not for artefacts.** A citation only exists if somebody actually took the file. An edition nobody downloaded has nothing resting on it: no reader holds it, no footnote points at it, and deleting it disappoints no one. So retention can be made conditional on the one fact that matters without weakening the promise at all — the promise is to the person holding the file, and this rule keeps exactly the files people are holding.

**It also inverts the growth curve in the right direction.** Storage then tracks demand rather than catalogue size, and the catalogue is the thing that grows without limit: 241 documents today, more as units are initialised, each cutting an edition every time its content moves. Downloads will not grow like that.

## Why the file does not move

**Bill's first sketch had three steps: copy the file to a `downloaded/` folder on download; delete the current file when a new dated one is rendered; then some mechanism for a reader to reach the copy in the archive.**

**Steps two and three are the same problem.** Deleting the file breaks the URL a reader wrote down, and step three then has to rescue exactly the citation step two just broke. An archive at a different address does not do that: the bytes survive and the link does not, and a citation nobody can follow is the failure §9 exists to prevent.

**So the file does not move — leaving it where it is *is* the archive.** A downloaded edition stays at the URL it was cited at, because nothing ever relocates it; an undownloaded one is deleted. There is no `downloaded/` folder, no copy step, no redirect, and no linking mechanism to build, because no link ever has to change. Three steps collapse into one, and the one that is left is a deletion rule rather than an archiving system.

## What it needs

**A record of which editions were taken, and nothing else.** Everything else already exists: `editions.py` knows what an edition is called, `render.py` cuts them, RENDER writes `site/` and commits it.

**The record comes from a Cloudflare Worker that does almost nothing.** The site is static on GitHub Pages, which gives no access logs, so something has to sit between the click and the bytes — there is no passive route. The Worker sees a request for a `.pdf` or `.csv`, appends the filename to a list, and passes the request straight through to GitHub untouched.

**It is deliberately not in the path of the bytes.** It does not serve the file, hold the archive or mint anything, so a Worker that breaks costs a missed log entry rather than a broken download. That is the difference from the gateway in the earlier note, where an outage would have taken downloads down with it, and it is why this shape can be trusted with a deletion rule and that one could not.

**Nothing online ever writes to the repo.** RENDER reads the list on Bill's machine, decides keep-or-delete while it is already writing `site/`, and commits the result like everything else. The archive is the repo, mirrored and backed up exactly as it is now.

## The direction of failure is always *keep*

**Something irreversible is acting on a record gathered elsewhere, so every uncertainty must resolve towards keeping the file.** A missing log entry, an unreachable list, a line that will not parse, a day the Worker was down, a list that looks suspiciously empty — each of those is a reason to delete nothing, never a reason to delete.

**This is the one place the design can do real harm**, and it is worth stating as a constraint rather than leaving to the implementation, because the failure is silent: a deletion that should not have happened looks identical to one that should, and the reader who finds the 404 is not someone we will hear from.

**A lag does most of the work.** Only delete an edition superseded more than a week ago — long enough that a log which arrived late still arrives before the deletion, and short enough that the saving is real. It also covers the reader who browses on Monday and downloads on Friday from a link they kept.

## What it does not fix

**Git does not forget.** Deleting a PDF from `site/` removes it from the served site and leaves the blob in `.git` for ever. The saving is on the **published site** — GitHub Pages' soft ceiling of about 1 GB, against `site/` at 350 MB — and not on the repository, which is 722 MB and would not move.

**Getting the repository weight back is a different operation**: PDFs stop being tracked in git, or the history is rewritten. OSINT reached 5.1 GB the same way and needed `git filter-repo` to come back (`documentation/osint-pdf-history-purge.md`, run 2026-08-17). Worth naming here so that this rule is not adopted in the belief that it solves both.

**An undownloaded edition still had a URL.** Someone may hold it without ever having downloaded — a link pasted into a message, a crawler's index, a reader who copied the address off the page. The lag covers most of that and not all of it, and the residue is the price of the rule.

## What it changes about §9

**§9 says a dated URL resolves for ever. Under this rule it resolves for ever *if anybody ever took it*.**

That is a real weakening and should be written into §9 rather than left as a divergence between the design record and the code. This repo has just been bitten by exactly that gap: §9 has said since 2026-08-06 that an edition is cut when the content changes, the renderer cut one on every render day regardless, and nobody noticed for twelve days because the design record was never checked against the tree.

## The set already published

**About 1,053 PDFs are live now, and the rule is clean only going forward.** Applying it to what is already out means deleting files that have been downloadable for days, at URLs that exist, with no download record for the period before the Worker existed — so every one of them would be deleted for want of evidence, which is the wrong direction of failure written large.

**The straightforward course is to apply it forward only** and let the existing set stand. It is 314 MB, it is a one-off, and it is the price of having published before the rule existed.

## Open questions

- Where the download list lives — Cloudflare KV, Analytics Engine, or a file the Worker appends to and RENDER fetches.
- The lag: a week is a guess, and the right number is however long it takes for a download to be observable plus a margin.
- Whether the rule covers the CSVs from the start. They are editions as of 2026-08-18 and the same mechanism applies unchanged, but they are small — the whole finance set is 5.8 MB — so there is no pressure to.
- Whether "earlier editions" (§9's quiet affordance) lists surviving editions only. It would, naturally, and a reader would see a list with gaps in it that they cannot account for.
- Whether the awareness half is worth having on its own first, before anything is deleted, simply to find out what actually gets downloaded. It is the same Worker, doing the same nothing, with the deletion rule not yet switched on — and after a month it would answer most of the questions above with evidence rather than guesses.
