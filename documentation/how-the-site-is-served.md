---
type: reference
title: how-the-site-is-served.md — the whole arrangement, in plain language
last_reviewed: 2026-09-08
status: current — describes the live configuration as of the R2 cutover
---

# How the site is served

*(This is the plain-language explanation of how `corpus.data-landscapers.io` actually works. It
is written to be read once, start to finish, by someone who has not seen the system before.
It does not tell you how to operate anything — for that, see the pointers at the end.)*

## The short version

The site lives in two places at once.

The **pages** — everything you look at in a browser — are on GitHub Pages, the same as they
always were. The **downloadable files** — the dated PDFs and CSVs, and the catalogue's name
index — are in Cloudflare R2, which is a file store, a bit like Dropbox for machines.

A small program called a **Worker** sits in front of both and decides which one to ask. Readers
never see any of this. Every web address is exactly what it was before.

## Why it is split up

GitHub Pages will only host about **1 GB** of files. That is a hard-ish ceiling and we were
going to hit it.

The problem is the dated editions. Every time a report's content changes, a new PDF is cut and
the old one is kept, because someone may have cited it. 251 documents doing that adds up
quickly — by early September the site was 1,316 MB against a 1 GB limit, having been 924 MB
four days earlier.

There was already a rule deleting old editions nobody had ever downloaded, and it worked, but it
was never going to keep up. So the files that were causing the problem moved somewhere without a
ceiling. Cloudflare R2 charges by the gigabyte and does not charge to send files to readers,
which is the specific reason it was chosen over the alternatives.

**GitHub Pages is now about 82 MB. The bucket holds 8,139 files, about 901 MB.**

## What happens when someone downloads a report

Follow one click through the system:

1. A reader clicks a PDF link on a country page.
2. The request arrives at **Cloudflare**, which everything goes through.
3. Cloudflare hands it to the **Worker**.
4. The Worker looks at the address. It ends in `.pdf` and has a date in the filename, so this is
   a dated edition — the Worker asks the **bucket** for it.
5. The bucket has it. The Worker sends it back to the reader.
6. Separately, and without holding anything up, the Worker **makes a note** that this file was
   taken. That note goes into a small database called the download log.

If step 4 had been an ordinary web page instead of a download, the Worker would have passed the
request through to **GitHub Pages** without doing anything else.

## The three moving parts

**The Worker** is about 160 lines of code. It does two jobs: serve the dated files out of the
bucket, and note which files people take. It does nothing else, and it is deliberately small.

**The bucket** is called `editions`. It holds one copy of every dated PDF and CSV, and the
catalogue's name-index files. The name of a file in the bucket is exactly the same as its web
address, which is what keeps everything simple — one name, used everywhere.

**The download log** records the address of every PDF and CSV a reader takes, along with when it
was first taken, when it was last taken, and how many times. **It records nothing about the
reader** — no IP address, no browser, no location, no account. It cannot, because it is never
given any of that.

## Why we keep a download log at all

Because old editions have to be deleted eventually, and the only fair way to decide which is to
ask whether anyone ever actually wanted them.

The promise the site makes is that a dated web address keeps working for ever *if somebody
downloaded it*. If a report was superseded, a week has passed, and not one person or machine
ever fetched it, then nothing is resting on it and it goes. If anybody fetched it — even an
automated crawler — it stays.

That runs once per publish, on Bill's machine, and it is the only thing in the system that
deletes anything.

## The safety rule that shapes everything

**When in doubt, keep the file.**

Every uncertainty resolves the same way. If the download log cannot be read, nothing is deleted.
If it looks suspiciously empty, nothing is deleted. If it looks stale — as though the Worker
might have stopped recording — nothing is deleted. A quiet week and a broken system look
identical from the outside, so both get the cautious answer.

The reason is that the failure is invisible. If a file is wrongly deleted, the deletion looks
exactly like a correct one, and the person who eventually hits the dead link is a reader we never
hear from. So the system is built to fail towards keeping things, and to waste storage rather
than lose a file.

## What changed for the worse, stated honestly

Before this, the Worker could break and nothing much would happen — downloads would still work,
we would just lose some log entries. That is no longer true. **The Worker is now the only route
to the dated files.** If it breaks, those downloads break.

Three things guard against that:

- The Worker **tries** the bucket rather than requiring it. If the bucket does not answer, or
  the connection to it is missing, the Worker quietly falls back to GitHub Pages.
- The note-taking still cannot delay or block a download. It happens after the file is already
  on its way.
- Nothing was deleted from the local copies until every one of the 8,139 files had been read
  back out of the bucket and checked, twice.

It is a real trade and it was made deliberately: the alternative was running out of space.

## The two exceptions

**The catalogue file `raw-catalogue.csv` stays on GitHub Pages.** It has no date in its name,
because it is republished in full every time the site is built. It is a pointer to other
people's records rather than a finding of ours, so it is not an "edition" and the rules above do
not apply to it.

**The bulletin stays on GitHub Pages too.** Bulletins are deleted after seven days regardless of
whether anyone downloaded them — the page says so — so they never pile up. There are twenty of
them, about 6 MB. Moving them would have meant rewriting the part of the system that keeps track
of them, for no gain.

## If something looks wrong

**A download 404s.** Check whether the file is in the bucket. If it is, the Worker is probably
not running or has lost its connection to the bucket.

**Downloads work but nothing is being logged.** The Worker's connection to the download log is
missing or misnamed. This fails silently on purpose — a broken log should never break a
download — so it will not announce itself.

**The deletion rule says "declined" every time it runs.** That is a normal, safe outcome and it
never stops a publish. But if it happens every day, the rule is not actually in effect and
somebody should look at why.

The one thing that would be genuinely serious is the `.com` domain registration lapsing. Over a
thousand published PDFs have `data-landscapers.com` addresses printed inside them, and those
addresses only still work because Cloudflare forwards them. That is the single piece of this
with no undo.

## Where the detail lives

This file explains the arrangement. It is deliberately not the place to look up specifics,
because a fact written in two places eventually disagrees with itself.

- **`documentation/cloudflare.md`** — the operational reference: the domains, the certificates,
  the redirects, the download log, the credentials, and how to check each one is working.
- **`documentation/editions-serving-shape.md`** — why the files moved to R2, what moved and what
  did not, the migration order, and what it cost.
- **`documentation/design.md` §9** — the promise about dated addresses, and the rules for when a
  file may be deleted.
- **`RENDER.md` Steps 6a and 6b** — what happens on every publish.
