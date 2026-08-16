---
type: design-note
title: Download awareness and archive-on-demand
last_reviewed: 2026-08-13
status: design note — not yet a decision
---

# Download awareness, and an archive that only keeps what was downloaded

*(Bill's idea, 2026-08-13: a downloaded artefact must be permanently citable, but most artefacts are never downloaded, so publishing them all up front is waste. Keep the site light; make an artefact permanent the moment someone actually takes it. This note sketches how, and what it changes. One line per paragraph.)*

## The two wants, which need different machinery

They arrived together but they separate cleanly, and it's worth keeping them apart.

**Awareness** — knowing a download happened. Cheap.
**Archive-on-demand** — the artefact becomes permanent *because* it was downloaded, and only then. A small backend, and the interesting part.

## Why the static site can't do either as it stands

The site is served by GitHub Pages, which gives you no access logs. A plain link to a `.pdf` or `.csv` is fetched from GitHub's CDN and you never learn it happened. To know — or to act on — a download you have to **interpose** something between the click and the bytes. There is no passive route.

## Awareness — the light half

Put the site behind **Cloudflare**. You already run a custom domain (`corpus.data-landscapers.com`), so this is a DNS change; the origin stays static GitHub Pages. Cloudflare's edge then logs every request to a `.pdf`/`.csv`, including direct-URL hits and crawlers, with nothing added to the page. Cloudflare Web Analytics or a Worker gives you the counts.

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

## It unifies three things you already want

The download gateway *is* `design.md` §9. That section already requires: no undated download URL, a citation that never changes under the person who made it, and a manifest anyone can verify against. The gateway mints exactly that record, so the **downloads archive and the verification manifest become one object**, and the log of who-took-what falls out of the same step.

The **sole-door** property is what makes "only keep what was wanted" true by construction rather than by hope: if the only way to a citable URL is through the gateway, there is no raw static URL lying around to be hotlinked, so an edition that was never asked for was never made permanent.

## Precondition: the CSVs must become editions

Your outstanding CSV-dates work is not a side-quest — it's the gate for the CSV half. A downloaded CSV is only citable if it's a **frozen, dated edition**, the same discipline the PDFs already carry (build-date in the filename, a new edition only when content changes). "Add dates to the CSVs" is really "make the CSVs editions"; until they are, there's nothing stable for the archive to freeze.

## What it costs, fully weighed

- **A dependency the static site doesn't have today.** The gateway must stay up or downloads break. That's the real charge against the current no-server simplicity. A Cloudflare Worker + R2 is about as low-ops as a backend gets, but it is still a backend, and the sole-door design means a gateway outage is a *download* outage.
- **Awareness is *initiated*, not *completed*** — you learn a download started, not that it finished or was used. Fine here, worth not over-reading.
- **First-download latency.** Minting on the first hit is a little slower than a static file; every hit after is normal. Acceptable if minting is a copy from the production store, not a fresh render.
- **Bots.** A crawler can trigger a mint. Cheap to mitigate — mint only on a real download intent (a POST from the button, or a token), not on any GET — but worth designing in, or your archive fills with editions no human took.

## A recommended minimal shape

Cloudflare in front of the static origin (awareness, free); a Worker on `/download/…` as the gateway; **R2** for both the production store (all editions, private, regenerable) and the permanent archive (downloaded editions, public, immutable); the manifest as a CSV the Worker appends to and the site publishes. Phase it: **(1)** Cloudflare + analytics for awareness only, learn what actually gets downloaded; **(2)** stand up the gateway + archive once the CSV editions exist; **(3)** stop committing PDFs to git and let the archive carry them.

## Open questions for you

- Is a backend acceptable at all, given the site was kept deliberately server-free? If not, awareness (phase 1) is still yours cheaply, and the archive idea waits.
- Production store: a private bucket, or lean on the render machine's local output and mint straight from there?
- Archive storage: object store (R2/S3), or a separate content-addressed **git archive repo** — the latter costs more but keeps the provenance-as-git property §9 liked, for only the artefacts that earned it.
- Mint trigger: button POST / token vs any GET — i.e., how hard to keep bots out of the permanent archive.
