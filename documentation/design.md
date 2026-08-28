---
type: doc
title: Phase 3 — the public site
status: built and deployed
last_reviewed: 2026-08-28
---

# Phase 3 — the public site

*(Design record. Phase 3 of the three-phase plan — automated collection → automated reporting → public website. This file holds what has been settled, what follows from it, and what is still open; it is revised, not appended to.)*

## What it is

A public, browsable surface over the wiki, at **corpus.data-landscapers.com**, feeding and fed by the long-form output at data-landscapers.com.

The site is a **derived view**, generated from `outputs/` — which Corpus itself authors (Job 1, `BUILD.md`) and renders (Job 2, `RENDER.md`). It is not a second store, it holds no state of its own, and nothing on it is authored by hand.

## 1. Settled

Decisions taken and not to be re-opened without a reason. Each is Bill's decision, not an inference.

- **The site is `corpus.data-landscapers.com`.** Site and repo carry one name, and *corpus* is the term of art for a body of collected texts.
- **Look and feel matches data-landscapers.com.** Same family, not a separate identity.
- **The OSINT repo is private and nothing served comes from outside `outputs/`.** The build reads OSINT but publishes committed `outputs/` only. Access to the full vault, bodies included, is granted individually on request.
- **Corpus is the single site-side repo.** It manages, prepares and serves the data as well as the site. There is no third repo: OSINT is the store of record and nothing else, Corpus is everything downstream of it.
- **PDFs are tracked in Corpus** (§8).
- **Every published file carries its build date in the filename**, and earlier editions are retained for re-access — a citation to a dated edition stays checkable. Retain silently; expose only current plus a quiet "earlier editions" affordance. §9 has the rules.
- **Everything is open. No account, no registration, no gate on anything.** There is nothing to log in to and no user record to hold, which removes a privacy surface a data-governance project would rather not defend.
- **An API with key control comes later.** Not at launch, but the data shapes should not preclude it.

## 2. Content

| Surface | Source | Notes |
|---|---|---|
| Catalogue | `outputs/catalogue/raw-catalogue.{json,csv}` | metadata only, never bodies |
| Country reports | `outputs/reports/{ISO3}/` | Status, monthly update, twelve-month progress |
| Regional reports | `outputs/reports/{X__}/` | Progress only |
| Topic reports | `outputs/topics/{slug}/` | One Level-2 slug across places, two documents each |
| National budgets | `outputs/budgets/{ISO3}-budget.csv` | 17 countries initialised |
| Non-state finance | `outputs/non-state-finance/` | Per country, plus the all-Africa editions |
| Metadata | frontmatter, facets, freshness | Part of the offer rather than an afterthought |

All seven exist and publish.

## 3. Structure

**Six top-level sections: Countries · Regions · Topics · Catalogue · Data · Method.** No seventh — there is no account.

**Lead with place and topic, not document type.** The audience does not arrive wanting *a progress report*; they arrive working on Algeria, or on data protection.

**The country page is the atomic unit**: position statement and last-updated date; the three reports as dated rows, readable and downloadable without a gate; the ledger counts; the catalogue count with the country's own cut to download and a link into the filtered browse; the finance summary; a budgets heading with a sentence under it even while the work is under way — a reader who finds nothing about budgets cannot otherwise tell an absent subject from an absent finding. Index rows and bylines say *last updated*, not *built* (the reader's question, not the machine's act), and carry no ***Not held*** count — that is a property of the ledger's completeness, visible and countable inside the document; on an index row it reads as a warning about a report nobody opened. Region and topic pages take the same shape with whatever reports they carry.

**`Data` is the tables as tables** — the CSVs for someone who wants the numbers rather than the narrative; the second of the two equally-weighted audiences (policy readers and researchers) served without a separate site.

**`Method` is content, not boilerplate.** Inclusion criteria, how currency and dating work, what *Not held* means, the licence, the retention policy, the privacy notice. A project about data governance publishing an exemplary account of its own practice is a credential.

## 4. Three design commitments

Cheap, because the base already holds what they need — and what distinguishes the site from every other Africa-digital dashboard.

- **Not held is a counted, visible number.** Publishing your own gaps says the base knows the difference between *no* and *we don't know*, and a thin country looks accurately thin rather than neglected.
- **Every figure is one click from its source record.** Already true in the data and true almost nowhere else; it answers *where did that number come from*, the question the whole project exists to answer.
- **Build dates and earlier editions in the open.** Freshness is a fact about the page, stated on the page. §9 makes it checkable.

## 5. Prototypes

`prototypes/` holds disposable scaffolding. `prototypes/datatable-test.mjs` is the live jsdom test for the finance tables (`RENDER.md` → *The finance tables*); the catalogue prototype pair is superseded by `scripts/catalogue.py` and deletable.

## 6. Open

- **Serving shape of the catalogue.** ~7.2 MB JSON now; ~23 MB at the 30,000 records projected for spring 2027. A single fetch stops being defensible around 15–20k rows; `raw/` is already sharded by year, so sharding the catalogue the same way is nearly free — but the boundary is expensive to move once anything external consumes the file, and there are two consumers (the page, and the filtered download's export fetch). Decide before it breaks.
- **The home page.** It has to say what this is, to someone arriving from a link, in about eight seconds, without becoming a dashboard. Hardest page on the site.

## 7. Preconditions — met

The launch preconditions are discharged: OSINT's repo weight (the PDF history purge), the consolidated cross-country dataset (`all-nonstate.csv`, dated editions), and verification over the report layer (checks G–M, `documentation/report-layer.md` §6).

## 8. How data reaches the site

**Corpus authors `outputs/` itself and renders it in the same repo.** There is no pull, no `upstream/` tree, and no push from OSINT: OSINT holds no credentials for Corpus, contains no part of the site, and has no publication step in its night. The night acquires no network dependency, and the presentation layer stays out of the store of record.

**Rendering is at build time, never on request.** A request-time renderer is a second uptime obligation, and it makes two downloads of the same dated file differ. WeasyPrint keeps one template for the HTML page and the PDF; a second toolchain is a second template that drifts.

**PDFs are tracked in the Corpus repo.** The repo is the deploy unit, and a dated PDF a citation points at is retained by the same mechanism that retains everything else. Git does not forget a binary, so the trajectory is a known cost — roughly 400 MB a year at full coverage under content-change minting (§9) — accepted rather than met as a surprise.

**One rule per folder, and the folder is the rule.** `outputs/` is written by BUILD; `site/` is generated, so an edit there is overwritten by the next build; `scripts/` is where code is authored. A file's folder is its state.

**Publish selectively.** The build renders only what it has a renderer for. **A directory in `outputs/` is not a decision to publish it**; publication is a renderer, written deliberately. (For any material Corpus consumes but does not author, the standing constraints are: mirror exactly, no reshaping — a mapping between two trees is a second copy of a structure that fails silently when one side moves.)

### Source bodies

**`outputs/` carries metadata and compiled prose and never a verbatim source body.** A leak into a public repo's history would be permanent. The boundary is bodies, not internal reasoning — this design record and the prototypes are public, which on §3's argument that method is content is closer to an asset than a cost.

**The leak-check gate is retired.** Every file in `outputs/` is written by a compiler in this repo, so there is no path along which a source body reaches the tree; a gate against a fault the architecture cannot produce is a standing cost, not a safety net. What upholds the rule is the drafter, at the point of writing: a summary reports its source and does not lift a sentence out of the body — a lifted sentence was always a register failure first (`BUILD.md` → *Narrative integrity*).

**Material published under a reproduction ban is paraphrased and cited, never block-quoted**, and the citation carries the reader to the publisher's own record rather than standing in for it. Holding the capture is the vault's business on its own basis; what Corpus controls is what reaches a page, and compressed figures inside ledger rows, attributed in Corpus's own words, is the shape the rule asks for.

## 9. Editions and verification

*(The case: a journalist downloads a report in August, cites a figure in November, and is asked to stand it up.)*

**"Verify" is three questions** — **integrity** (*is this the file you published?*), **currency** (*is what it says still true?*), **provenance** (*where did that figure come from?*).

**The site answers currency and provenance; the integrity machinery (manifest, `Derived from` and `Verify` rows) is withdrawn.** The commitment to a reader is a moral one, not a legal one: what is owed is that a document says plainly what it is and when it was cut, and that it is not revised afterwards — which dating, retention and permanent URLs do whether or not anyone audits us. `BUILT-FROM` at the repo root still records the commit each render was cut at, as the build's own record; no page prints it.

### Provenance — URLs are permanent, and never reissued

**A dated URL resolves for ever *if anybody ever took it*.** Retention is conditional on the one fact that matters — whether a reader actually downloaded the edition — and a superseded edition nobody ever fetched is deleted. `documentation/cloudflare.md` holds the Worker, the KV record and the credentials; `scripts/prune-editions.py` is the rule, run by `RENDER.md` Step 6a. The promise was always to a person rather than to a URL: a citation only exists if somebody took the file. What it buys is that storage tracks demand rather than catalogue size, against GitHub Pages' soft ceiling of ~1 GB; the repository does not shrink, because git keeps the blob.

**Four things keep it narrow, and every uncertainty resolves towards keeping the file**: the current edition of anything is never deleted; nothing published on or before 2026-08-18 is ever deleted (the rule is forward-only); nothing superseded less than a week ago is deleted, so a late log entry still arrives first; and any fetch at all protects, a crawler's included. A missing credential, an API error, an empty listing or a stale-looking record stops the whole run rather than being read as *nobody wanted these*. **The residue, stated**: someone may hold a URL they never downloaded from — a link pasted into a message — and for them the file goes. `logs/deleted-editions.csv` is the account of what went.

**No undated download URL exists at all** (the catalogue is the named exception, below). An undated URL invites a citation that changes underneath the person who made it. Browse the HTML at a stable address; every download hands back a dated file. This makes catalogue slugs permanent identifiers upstream — a constraint on OSINT, recorded as a standing constraint in the exchange's `notes-for-osint.md`.

### Currency — every edition says that it is one

**A footer on every page of every PDF: *Edition of {date} · current edition at {url}*.** Without it the retention policy manufactures the risk it exists to remove: an old edition that announces itself is an asset; one that does not is a liability.

### How often an edition is minted

**A new edition is cut when the content changes, not when a build runs.** `render.py` digests the markdown **below the frontmatter** (`compiled:` moves on every render, so hashing the rendered file would mint nightly editions of an unmoved document), stamps the digest into the served page as `<meta name="dl-record">`, and reads it back next run: same digest, no new edition, no rewrite. **The record travels inside the artefact it describes**, so no state file can fall out of step with it. `scripts/test_render_gate.py` exercises both directions — a gate that only ever holds off is indistinguishable from one that has stopped working.

Two things the gate deliberately does not do: it does not touch **naming** — the edition is the render date, so a moved document can never land on a name a citation already rests on — and it does not restyle a held-off edition, since the PDF embeds the stylesheet and *not revised after publication* is meant literally. `--force` re-cuts the whole set when a presentation change should reach it.

**Two editions can share a date**: the first is unsuffixed, the second takes `-2` — a daytime session forcing an update on a live issue is normal, not an edge case. `render.py` takes the first name of the day no retained PDF already carries; existence on disk is the test. **The first edition is never renamed when a second appears** — retrospective `-1` symmetry would break every URL already handed out. **Every script that reads editions parses and orders them with `render.py`'s own functions** — the script that names them is the one that reads them; two copies of one filename grammar fail silently the first time a `-2` is cut.

**The bulletin refreshes its page while holding its edition, and it is the only document that does.** Its freshness is itself news — *we looked, and nothing was published* — so a held-off render rewrites the page under the edition it is holding and leaves the PDF alone. The digest stays the body, so a moved clock cannot mint an edition; the byline is a claim about the material, the colophon names the dated file, and a PDF is a snapshot entitled to the stamp it was cut with.

With content-change minting, all three report types are citable — volume tracks real movement, and a country whose ledger moves twice a year gets two editions, not seven hundred.

### Which downloads are editions

**Compiled findings are editions; indexes over other people's records are not.** That is the rule that decides every case:

- **The finance CSVs are editions** — per-country `{ISO3}-nonstate-{edition}.csv`, the all-Africa file, on the same terms as the reports. The gate for a CSV is a byte comparison against the newest retained edition (a CSV from unchanged data is the same file; a PDF never is, since it carries its build date inside it). The data CSV and its field dictionary carry independent editions — columns move far less often than rows.
- **The catalogue is not an edition.** `raw-catalogue.csv` stays at its undated URL, republished wholesale on every build: every row points at a publisher's own document, and it is the pointer rather than the claim. If anyone ever cites a catalogue count as of a date, it should become an edition too.
- **The per-country catalogue cut follows the catalogue, not the finance CSV beside it** — same columns, rows removed, undated, republished wholesale. Two files in one folder under opposite rules, and the compiled-finding test is what decides which is which.
- **A filtered selection is a cut of the catalogue and not an edition either.** The export points at **the view's own URL**, which re-cuts against whatever the catalogue holds when opened, with the build date riding in the filename to say which cut the file in hand was.

### Not yet

**DOIs.** Zenodo will mint one per dated edition — the academic gold standard — but it adds an external dependency and a deposit step to every publish. Revisit now the site is up.
