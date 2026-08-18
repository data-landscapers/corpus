---
type: design-note
title: Download awareness and archive-on-demand
last_reviewed: 2026-08-18
status: design note — not yet a decision
---

# Download awareness, and an archive that only keeps what was downloaded

*(Bill's idea, 2026-08-13: a downloaded artefact must be permanently citable, but most artefacts are never downloaded, so publishing them all up front is waste. Keep the site light; make an artefact permanent the moment someone actually takes it. This note sketches how, and what it changes. One line per paragraph.)*

*(**Checked against the tree on 2026-08-18** and corrected in four places, each marked with that date: what Cloudflare's free plan actually hands back, the measured size of the PDF set, the effect of implementing §9's minting rule, and GitHub Pages' own ceiling. Nothing in the argument changed; two of its numbers and one of its assumptions did. The question was put again the same day and answered from scratch, this note not having been found — it is the record, and it lives here.)*

## The two wants, which need different machinery

They arrived together but they separate cleanly, and it's worth keeping them apart.

**Awareness** — knowing a download happened. Cheap.
**Archive-on-demand** — the artefact becomes permanent *because* it was downloaded, and only then. A small backend, and the interesting part.

## Why the static site can't do either as it stands

The site is served by GitHub Pages, which gives you no access logs. A plain link to a `.pdf` or `.csv` is fetched from GitHub's CDN and you never learn it happened. To know — or to act on — a download you have to **interpose** something between the click and the bytes. There is no passive route.

## Awareness — the light half

Put the site behind **Cloudflare**. You already run a custom domain (`corpus.data-landscapers.com`), so the origin stays static GitHub Pages and the change is at the DNS.

**But a DNS change alone does not give you per-file counts, and the first version of this paragraph said it did** *(corrected 2026-08-18)*. Cloudflare does see every request at the edge, including direct-URL hits and crawlers — the question is what it will hand back to you. Raw request logs (Logpush) are an Enterprise feature; free-plan zone analytics is aggregate, with no per-path breakdown; and Cloudflare **Web Analytics** is a JS beacon, which is the very mechanism the next paragraph rules out as a sole signal. So the free route to *"how many people took `KEN-status-2026-08-06.pdf`"* is a **Worker** on the download paths, counting into Workers Analytics Engine or KV. Still cheap — the free tier is 100,000 requests a day against a site with nothing like that traffic — but it is code at the edge, not a setting. Worth re-checking against Cloudflare's current plans before anything is built on it; plan boundaries move and this one is load-bearing for the phasing below.

**Which changes the phasing more than it changes the cost.** Awareness was filed here as the cheap half you could take without committing to a backend, and a Worker *is* the interposition the archive half needs — the same shape, doing less. Phase 1 is therefore not free of the decision in phase 2; it is the first, harmless version of it. That is arguably an argument for the idea rather than against it: the thing you would build to satisfy curiosity is the thing you would keep.

A JS click-beacon (Plausible, GoatCounter) is even lighter but only sees clicks that ran your script — it misses a pasted URL or `curl`, and it reports *initiated*, not *completed*. Fine as a supplement, wrong as the only signal.

Awareness alone, though, does not give persistence: the file still has to exist somewhere it can't vanish. That is the other half.

## Archive-on-demand — the shape

The move is to stop treating the heavy artefacts as things you publish, and treat them as things you **mint on first demand**. Publish the *readable* layer always — the HTML reports, the browse tables — because it's light. Behind the "Download" button sits a **gateway**, not a static file.

The flow, on a click:

1. The gateway resolves which artefact and which **edition** is being asked for (a report's current edition, a dated CSV).
2. It checks the **permanent archive** for that edition, keyed by a hash of its bytes.
3. If absent, it takes the exact bytes from the **production store** (below), writes them once into the archive under a content-addressed, dated URL, and appends a manifest row — hash, build-date, OSINT commit SHA, first-download timestamp.
4. It records the event and returns the file (or 302s to the archive URL).
5. Every later download of that same edition serves the archived copy directly — cheap, and now permanent.

So the permanent, cited surface grows with **demand**, not with catalogue size. Most artefacts are never minted; the ones that are, are immutable and citable from the first click.

## Two stores, and which one is permanent

The distinction that makes the efficiency real:

- **Production store** — *all* rendered artefacts, private and **regenerable**. RENDER writes every PDF/CSV edition here (a cheap object bucket, or even a scratch dir the gateway can reach). It can be pruned or rebuilt from OSINT + the pipeline at any time, so nothing here is a permanent commitment.
- **Permanent archive** — *only* the editions someone downloaded, immutable, content-addressed, with the manifest. This is the citable surface, and the only thing whose size and history you carry forever.

The saving is on the *permanent* surface, which is the one that costs you forever.

## This reverses a settled decision — deliberately

`documentation/design.md` §9 chose (2026-08-06) to **track every PDF in git, in the Corpus repo** — "the served artefact and its history are one object" — for verifiability. This idea reverses that: don't commit hundreds of PDFs (× every future edition) into git history, where they sit permanently whether or not anyone wants them. Verifiability is kept a different way — the manifest's hash + date + OSINT SHA — which is the mechanism §9 already designed. So you trade permanent git bloat for the same guarantee, paid only on demand. Flagging it so the reversal is a decision, not a drift.

**"Hundreds" was measured on 2026-08-18 and it is 1,053 PDFs, 314 MB, all committed** — accumulated in the thirteen days since 2026-08-05, with `.git` at 722 MB. So this is not a choice standing in front of you; most of it has already happened, and the question is whether to keep going.

**Most of that was churn rather than catalogue, and the churn is now fixed** *(2026-08-18)*. §9's rule — an edition is cut when the content changes, not when a build runs — had never been implemented on the render side: the edition is the render date and RENDER renders all 241 documents every run, so every render day cut 241 new dated PDFs and kept them. `render.py` now holds off on a document whose body has not moved, which removes the bulk of the growth without a backend, a Worker or a reversal of anything. **That weakens the urgency of this note and not its argument.** What remains is the real question it was written about: the *catalogue* is 241 documents and rising, editions accumulate for ever by design, and almost none of them will ever be downloaded. That case stands. It is now a case to be made on the trajectory rather than on a fire.

**The manifest this note leans on no longer exists** *(2026-08-18)*. The argument above trades git-tracked PDFs for "the same guarantee" kept by the manifest's hash + date + OSINT SHA — and the manifest, the `Derived from` row and the `Verify` row have since been withdrawn (§9): the commitment to a reader is moral rather than legal, so there is no hash apparatus for an archive to become one object with. **This removes a reason for the reversal, not a reason against it.** What made the idea attractive was never really verifiability — it was not making permanent what nobody wanted. But the note's neatest claim, that the downloads archive and the verification manifest are the same object, is gone, and the "It unifies three things you already want" section below is now two.

**And whatever is decided, the ~1,000 URLs already published are a commitment.** §9 promises a dated URL resolves for ever, and those are out in the world. Archive-on-demand can only govern what has not shipped yet; it cannot retire what has, and the sole-door property below is therefore already imperfect on the existing set. Not fatal — but it means the reversal is *from here on*, and the note should not be read as offering a way out of what is already committed.

## It unifies three things you already want

The download gateway *is* `design.md` §9. That section already requires: no undated download URL, a citation that never changes under the person who made it, and a manifest anyone can verify against. The gateway mints exactly that record, so the **downloads archive and the verification manifest become one object**, and the log of who-took-what falls out of the same step.

The **sole-door** property is what makes "only keep what was wanted" true by construction rather than by hope: if the only way to a citable URL is through the gateway, there is no raw static URL lying around to be hotlinked, so an edition that was never asked for was never made permanent.

## Precondition: the CSVs must become editions

**Done for the finance CSVs on 2026-08-18, and the catalogue is deliberately outside it** *(Bill)*. `{ISO3}-nonstate`, its field dictionary and `all-nonstate` are now dated editions on §9's rule — a new one only when the bytes move, retained, `-2` for a second in a day, and no undated URL left standing. So the precondition below is met for everything this note would archive, and the catalogue, which it would not, stays a browse index. What is left of the CSV half is the same question as the PDF half: whether a gateway mints on demand, not whether there is anything stable to mint.

Your outstanding CSV-dates work is not a side-quest — it's the gate for the CSV half. A downloaded CSV is only citable if it's a **frozen, dated edition**, the same discipline the PDFs already carry (build-date in the filename, a new edition only when content changes). "Add dates to the CSVs" is really "make the CSVs editions"; until they are, there's nothing stable for the archive to freeze.

## What it costs, fully weighed

- **A dependency the static site doesn't have today.** The gateway must stay up or downloads break. That's the real charge against the current no-server simplicity. A Cloudflare Worker + R2 is about as low-ops as a backend gets, but it is still a backend, and the sole-door design means a gateway outage is a *download* outage.
- **Awareness is *initiated*, not *completed*** — you learn a download started, not that it finished or was used. Fine here, worth not over-reading.
- **First-download latency.** Minting on the first hit is a little slower than a static file; every hit after is normal. Acceptable if minting is a copy from the production store, not a fresh render.
- **Bots.** A crawler can trigger a mint. Cheap to mitigate — mint only on a real download intent (a POST from the button, or a token), not on any GET — but worth designing in, or your archive fills with editions no human took.

## A recommended minimal shape

Cloudflare in front of the static origin; a Worker on `/download/…` as the gateway; **R2** for both the production store (all editions, private, regenerable) and the permanent archive (downloaded editions, public, immutable); the manifest as a CSV the Worker appends to and the site publishes. Phase it: **(1)** Cloudflare, plus a counting Worker on the download paths — awareness only, and it is a Worker rather than a setting (above); learn what actually gets downloaded; **(2)** stand up the gateway + archive once the CSV editions exist; **(3)** stop committing PDFs to git and let the archive carry them.

**Phase 0, which is none of the above and was done on 2026-08-18: implement §9's minting rule.** It needed no Cloudflare, no Worker and no decision, and it takes out the growth that was making this urgent. Anything below is now a considered move rather than a rescue.

**One constraint neither this note nor §8 had allowed for**: GitHub Pages publishes a site of up to about **1 GB** with a soft bandwidth ceiling around 100 GB a month, and `site/` is 350 MB. That wall is nearer than the git one, it is not moved by anything in phase 1, and it is the thing that would force a decision here whether or not anyone ever downloads a file. Confirm the current figures against GitHub's own limits page before planning to it.

## Open questions for you

- Is a backend acceptable at all, given the site was kept deliberately server-free? If not, awareness (phase 1) is still yours cheaply, and the archive idea waits.
- Production store: a private bucket, or lean on the render machine's local output and mint straight from there?
- Archive storage: object store (R2/S3), or a separate content-addressed **git archive repo** — the latter costs more but keeps the provenance-as-git property §9 liked, for only the artefacts that earned it.
- Mint trigger: button POST / token vs any GET — i.e., how hard to keep bots out of the permanent archive.
