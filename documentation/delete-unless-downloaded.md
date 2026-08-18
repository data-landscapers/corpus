---
type: design-note
title: Delete unless downloaded
last_reviewed: 2026-08-18
status: implemented 2026-08-18 — PDFs and CSVs, forward only
---

# Delete unless downloaded

*(Bill's simplification, 2026-08-18, of `documentation/download-archive-design.md`. That note proposed a gateway that minted an artefact into a permanent archive the first time anyone downloaded it. This is the same instinct — keep only what someone wanted — arrived at from the other end, and it needs far less machinery. One line per paragraph.)*

## Implemented, the same day *(Bill: "can we implement delete-unless-downloaded now. pdfs and csvs. moving forward only")*

**`scripts/prune-editions.py` is the rule; `RENDER.md` Step 6a runs it with `--apply`, after the site is written and before the leak gate and the commit.** So a deletion is carried by the same commit as the render that superseded the file, and the gate reads the tree as it will be published. The three answers Bill gave are the three decisions this note left open: **both formats**, since the mechanism is identical and a finance CSV is the format a reader is most likely to quote a figure straight out of; **forward only**, so nothing published before the record existed is ever touched; and **now**, rather than after a month of watching — forward-only makes the waiting automatic, because the first edition the rule can even consider is one the Worker watched from the day it was minted.

**Five conditions, all of which must hold, and every uncertainty resolves towards keeping the file.** Not the current edition; dated after 2026-08-18; superseded more than seven days ago; the download record healthy; nothing ever fetched it. A missing credential, an API error, an unparseable answer, an empty listing or a record that looks stale stops the whole run rather than being read as *nobody wanted these* — deleting nothing at all, not file by file.

**Two health checks stand in for the awareness month this note wondered about.** `--min-keys` refuses an empty listing, which is what an unbound namespace, a wrong namespace ID and a Worker knocked off its route all look like. `--liveness-days` requires that some key in the record names an edition minted in the last fortnight: a key can only exist after the file it names was minted, so the newest edition date across the keys is a lower bound on when the Worker last recorded anything. On a genuinely quiet site this declines to delete, which is also the right answer when the Worker is dead — from here the two are indistinguishable.

**Any fetch at all protects the file, a crawler's included.** The Worker splits `n` from `bots` rather than filtering, and the pruner reads the split as *keep either way*: a bot causing a keep costs storage, where dropping a real reader's download eventually costs the file, and the crawler pattern matches `curl`, `wget` and `python-requests`, which is how a technical reader takes a file they mean to cite. One consequence is that the values are never read — presence of the key is the whole test, so the pruner asks Cloudflare only for the key list, which is cheaper and has nothing in it to misparse.

**`scripts/test_prune_editions.py` is almost entirely a test of refusals**, because that is where the harm lives: eleven of its twelve cases assert that nothing was deleted. `logs/deleted-editions.csv` is the account of what did go — git keeps the blob regardless, and the ledger is the part a person can read.

**Expect it to delete nothing for weeks.** Every one of the 1,401 editions on disk today predates the rule.

**Run end to end on 2026-08-18, in a full RENDER.** Step 6a read the live record and reported `1401 editions on disk, 3 paths in the download record, 1401 kept, 0 deletable`, which is forward-only doing its job rather than a check that proved nothing.

**A deletion was rehearsed the same run, because a rule that has never deleted anything is a rule nobody has watched work.** Live token, live KV record, six files in a scratch tree, the calendar simulated with `--today` and `--from` and the liveness check disabled — the two paths the real record holds were kept as *downloaded*, the two nobody has fetched were deleted, both current editions were untouched, and the ledger recorded the pair. `--ledger` exists for exactly this: a rehearsal must not write into the site's own account of what it lost.

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

That is a real weakening and should be written into §9 rather than left as a divergence between the design record and the code. **Done the same day**, in §9's *Provenance* subsection, along with what keeps the amendment narrow and what the residue is. This repo has just been bitten by exactly that gap: §9 has said since 2026-08-06 that an edition is cut when the content changes, the renderer cut one on every render day regardless, and nobody noticed for twelve days because the design record was never checked against the tree.

## The set already published

**About 1,053 PDFs are live now, and the rule is clean only going forward.** Applying it to what is already out means deleting files that have been downloadable for days, at URLs that exist, with no download record for the period before the Worker existed — so every one of them would be deleted for want of evidence, which is the wrong direction of failure written large.

**The straightforward course is to apply it forward only** and let the existing set stand. It is 314 MB, it is a one-off, and it is the price of having published before the rule existed.

## The questions this note left open, and what they were answered with

- **Where the download list lives** — **Cloudflare KV**, keyed by the file's path as published. Settled when the Worker was built; the key doubles as the thing the pruner matches against `site/`, so there is no translating between two naming schemes.
- **The lag** — **seven days**, still a guess, and `--lag-days` is where to change it. It is not a guess about a slow log any more, since KV is written within seconds of the download; it is a guess about the reader who browses on Monday and downloads on Friday from a link they kept.
- **Whether the rule covers the CSVs from the start** — **yes** *(Bill, 2026-08-18)*. The mechanism is identical and the finance set is small, so this buys little storage; what it buys is one rule rather than two, and no format where a reader's download quietly does not protect their citation.
- **Whether "earlier editions" lists surviving editions only** — it will, and the gaps will be visible. Not a problem to solve now, because the affordance is not built: nothing on the site links a superseded edition today, which is also why deleting one breaks no link the site itself carries. When it is built, the honest form is a list that says what it is — the editions still held — rather than one that implies it is complete.
- **Whether the awareness half is worth having alone first** — **superseded by forward-only**, which makes the watching period automatic rather than a decision to remember to revisit. The rule cannot touch anything the Worker did not watch from the day it was minted, so switching it on now and waiting a month produce the same first deletion.

## Still open

- **Nobody reads the record for interest.** The pruner asks for the key list and acts; the counts of who took what sit in KV unexamined. *Which editions do readers actually take* was the question the Worker was built to answer, and answering it needs a reader for the values rather than the keys.
- **A `PRUNE: declined` line is easy to stop seeing.** It is printed by an unattended run into a log nobody reads line by line, and a rule that quietly stopped being in effect looks exactly like a rule that has nothing to delete. If declining ever becomes the normal state, it wants a message to Bill rather than a line of output.
