---
type: doc
reader: cc
title: Phase 3 — the public site
status: built and deployed
last_reviewed: 2026-09-08
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
- **Corpus is the single site-side repo.** It manages, prepares and serves the data as well as the site. OSINT is the store of record and nothing else; Corpus is everything downstream of it.
- **PDFs are tracked in Corpus** (§8).
- **Every published file carries its build date in the filename**, and earlier editions are retained for re-access. Expose only current plus a quiet "earlier editions" affordance. §9 has the rules.
- **Everything is open. No account, no registration, no gate on anything.** No user record to hold, so no privacy surface to defend.
- **An API with key control comes later.** Not at launch, but the data shapes should not preclude it.

## 2. Content

| Surface | Source | Notes |
|---|---|---|
| Catalogue | `outputs/catalogue/raw-catalogue.{json,csv}` | metadata only, never bodies; the CSV is the download, the JSON is internal |
| Country reports | `outputs/reports/{ISO3}/` | Status, monthly update, twelve-month progress |
| Regional reports | `outputs/reports/{X__}/` | Progress only |
| Topic reports | `outputs/topics/{slug}/` | One Level-2 slug across places, two documents each |
| National budgets | `outputs/budgets/{ISO3}-budget.csv` | 17 countries initialised |
| Non-state finance | `outputs/non-state-finance/` | Per country, plus the all-Africa editions |
| Metadata | frontmatter, facets, freshness | Part of the offer rather than an afterthought |

All seven exist and publish.

**The catalogue download carries ten columns** *(Bill, 2026-09-09)* — in `raw-catalogue.csv`, the country and region cuts and a filtered selection: title, publisher, author, published, date_precision, places, topics, entities, ingested, url. `slug`, `lens`, `body_completeness`, `finance`, `artefact`, `words` and `url_note` are our handling notes and excluded.

**The full rows stay unpublished**: `catalogue-internal.csv` is the download plus `slug` (the key for citations and the bulletin's summary store) and `url_note` (read by `status_lib` to send a citation of a URL-less record to its catalogue entry); `raw-catalogue.json` is the full record. Neither reaches `site/`. `build-catalogue.py` → `CSV_COLS` draws the line and `catalogue.py` reads it from there.

## 3. Structure

**Six top-level sections: Countries · Regions · Topics · Catalogue · Data · Method.** No seventh — there is no account.

**Lead with place and topic, not document type** — readers arrive working on Algeria, or on data protection.

**The country page is the atomic unit**: position statement and last-updated date; the three reports as dated rows, ungated; the ledger counts; the catalogue count, the country's cut and a link into the filtered browse; the finance summary; a budgets heading with a sentence under it even while work is under way, so an absent subject is distinguishable from an absent finding. Index rows and bylines say *last updated*, not *built*, and carry no ***Not held*** count, which belongs inside the document. Region and topic pages take the same shape.

**`Data` is the tables as tables** — the CSVs for someone who wants the numbers, serving researchers (the second of the two equally-weighted audiences, with policy readers) without a separate site.

**`Method` is content, not boilerplate** — inclusion criteria, currency and dating, what *Not held* means, the licence, retention, privacy. A data-governance project's account of its own practice is a credential.

## 4. Three design commitments

Cheap, because the base already holds what they need — and what distinguishes the site from every other Africa-digital dashboard.

- **Not held is a counted, visible number.** It shows the base knows *no* from *we don't know*, and a thin country looks accurately thin rather than neglected.
- **Every figure is one click from its source record** — the answer to *where did that number come from*, the question the project exists to answer.
- **Build dates and earlier editions in the open** — freshness stated on the page. §9 makes it checkable.

## 5. Prototypes

`prototypes/` holds disposable scaffolding. `prototypes/datatable-test.mjs` is the live jsdom test for the finance tables (`RENDER.md` → *The finance tables*); the catalogue prototype pair is superseded by `scripts/catalogue.py` and deletable.

## 6. Open

- **Serving shape of the catalogue — closed 2026-09-08.** Decided in `documentation/catalogue-serving-shape.md`; built per `documentation/archived/catalogue-split-plan.md`. A filter index of integers fetched once, row text in chunks fetched as drawn, free-text search on R2 prefix shards, and the first screen in the markup so the page draws with JavaScript off: **0.73 MB gzipped before the first draw, against 3.73 MB.** **A figure in a design record with nothing reading it back is never re-checked**; `RENDER.md` states counts as facts about the last build, not expectations.
- **The home page.** It has to say what this is, to someone arriving from a link, in about eight seconds, without becoming a dashboard. Hardest page on the site.
- **Alerts for a narrow interest — built and deployed 2026-09-16; the first digest is Monday 2026-09-21, released by hand.** Sign-up is at `/alerts/` and the catalogue's **Get alerts** button; the Worker is `workers/alerts/worker.js`. A reader picks up to five countries and five topics per alert, holds up to ten alerts, and gets **one** weekly email with a section per alert — new writing on data-landscapers.io being one more alert. The Worker builds the body on a Monday cron and hands it to Buttondown, which holds the addresses, so the site holds no user record (§1). `documentation/catalogue-alerts.md` has the rest.

  **Buttondown is a list and a sender** — one body with sections, not an RSS feed per alert (`archived/catalogue-alerts-digest.md`). Every rule about what a reader receives lives in this repo under tests, and a template mistake reaches the whole list — so the first two Mondays are drafts Bill releases by hand, and staying on drafts is a settled option. Existing subscribers move to weekly unannounced (Bill, 2026-09-16).

## 7. Preconditions — met

The launch preconditions are discharged: OSINT's repo weight (the PDF history purge), the consolidated cross-country dataset (`all-nonstate.csv`, dated editions), and verification over the report layer (checks G–M, `documentation/report-layer.md` §6).

## 8. How data reaches the site

**Corpus authors `outputs/` itself and renders it in the same repo.** No pull, no `upstream/` tree, no push from OSINT: OSINT holds no credentials for Corpus, contains no part of the site, and has no publication step. The night acquires no network dependency, and the presentation layer stays out of the store of record.

**Rendering is at build time, never on request** — a request-time renderer is a second uptime obligation and makes two downloads of one file differ. WeasyPrint keeps one template for the HTML page and the PDF; a second toolchain is a second template that drifts.

**PDFs are tracked in the Corpus repo.** The repo is the deploy unit, and a cited PDF is retained by the same mechanism as everything else. Git does not forget a binary — roughly 400 MB a year at full coverage under content-change minting (§9) — a known, accepted cost.

**One rule per folder, and the folder is the rule.** `outputs/` is written by BUILD; `site/` is generated, so an edit there is overwritten by the next build; `scripts/` is where code is authored. A file's folder is its state.

**`budgets/` is the one source folder** *(strategic review 4 R54)*. A line read from a state's own budget document has no record in OSINT's `raw/` — the row *is* the record — so it is authored here, tracked, and regenerated by nothing. **A country-year present in `budgets/` replaces OSINT's rows for that year** in `build-finance-page.py`'s export, because a union of two grains double-counts a programme against its sub-programmes undetectably. `BUDGET-EXTRACT.md` is the procedure, `scripts/budget_source.py` the schema and checker. The 488 migrated domestic-state records *(R56a)* name their source in `origin_record` and are held to a narrower bar — nothing invented — with the shortfall counted per country as the queue's work order. *Source bodies* binds the folder: a line's printed name is carried; everything longer is in Corpus's own words.

**Publish selectively.** The build renders only what it has a renderer for. **A directory in `outputs/` is not a decision to publish it**; publication is a renderer, written deliberately. (For material Corpus consumes but does not author: mirror exactly, no reshaping — a mapping between two trees fails silently when one side moves.)

### Source bodies

**`outputs/` carries metadata and compiled prose and never a verbatim source body.** A leak into a public repo's history would be permanent. The boundary is bodies, not internal reasoning — this design record and the prototypes are public, which on §3's argument is closer to an asset than a cost.

**The leak-check gate is retired.** Every file in `outputs/` is written by a compiler in this repo, so no path carries a source body into the tree. What upholds the rule is the drafter: a summary reports its source and does not lift a sentence from the body (`BUILD.md` → *Narrative integrity*).

**Material published under a reproduction ban is paraphrased and cited, never block-quoted** — compressed figures inside ledger rows, attributed in Corpus's own words, with the citation carrying the reader to the publisher's own record.

## 9. Editions and verification

*(The case: a journalist downloads a report in August, cites a figure in November, and is asked to stand it up.)*

**"Verify" is three questions** — **integrity** (*is this the file you published?*), **currency** (*is what it says still true?*), **provenance** (*where did that figure come from?*).

**The site answers currency and provenance; the integrity machinery (manifest, `Derived from` and `Verify` rows) is withdrawn.** The commitment is moral, not legal: a document says what it is and when it was cut, and is not revised afterwards. `BUILT-FROM` at the repo root records the commit each render was cut at, as the build's own record; no page prints it.

### Provenance — URLs are permanent, and never reissued

**A dated URL resolves for ever *if anybody ever took it*.** A superseded edition nobody ever fetched is deleted — a citation only exists if somebody took the file, so storage tracks demand, against GitHub Pages' ~1 GB soft ceiling. `scripts/prune-editions.py` is the rule, run by `RENDER.md` Step 6a; `documentation/cloudflare.md` holds the Worker, the KV record, the credentials and the full conditions.

**Four things keep it narrow, and every uncertainty resolves towards keeping the file**: the current edition of anything is never deleted; nothing published on or before 2026-08-18 is ever deleted (the rule is forward-only); nothing superseded less than a week ago is deleted; and any fetch at all protects, a crawler's included. Any doubt about the record stops the whole run. **The residue, stated**: someone holding a URL they never downloaded from loses the file. `logs/deleted-editions.csv` is the account of what went.

**The pre-worker archive was cleared by hand on 2026-09-08** (`scripts/drop-pre-worker-editions.py`, 1,237 superseded editions) on Bill's call that the site was not yet live and no citation rested on them; editions still *current* were kept. **The forward-only clause stays in the rule**: *delete unless somebody took it* cannot be applied to a period with no record.

**No undated download URL exists at all** (the catalogue is the named exception, below). An undated URL invites a citation that changes underneath the person who made it. Browse the HTML at a stable address; every download hands back a dated file. This makes catalogue slugs permanent identifiers upstream — a standing constraint on OSINT, recorded in the exchange's `notes-for-osint.md`.

### Currency — every edition says that it is one

**A footer on every page of every PDF: *Edition of {date} · current edition at {url}*.** Without it the retention policy manufactures the risk it exists to remove: an old edition that announces itself is an asset; one that does not is a liability.

### How often an edition is minted

**A new edition is cut when the content changes, not when a build runs.** `render.py` digests the markdown **below the frontmatter** (`compiled:` moves on every render, so hashing the rendered file would mint nightly editions of an unmoved document), stamps the digest into the served page as `<meta name="dl-record">`, and reads it back next run: same digest, no new edition, no rewrite. **The record travels inside the artefact it describes**, so no state file can fall out of step with it. `scripts/test_render_gate.py` exercises both directions — a gate that only ever holds off is indistinguishable from one that has stopped working.

The gate does not touch **naming** — the edition is the render date, so a moved document never lands on a name a citation already rests on — and does not restyle a held-off edition, since the PDF embeds the stylesheet and *not revised after publication* is meant literally. `--force` re-cuts the whole set when a presentation change should reach it.

**Two editions can share a date**: the first is unsuffixed, the second takes `-2` — a daytime update on a live issue is normal. `render.py` takes the first name of the day no retained PDF already carries; existence on disk is the test. **The first edition is never renamed when a second appears** — that would break every URL already handed out. **Every script that reads editions parses and orders them with `render.py`'s own functions** — two copies of one filename grammar fail silently the first time a `-2` is cut.

**The bulletin refreshes its page while holding its edition, and it is the only document that does.** Its freshness is news — *we looked, and nothing was published* — so a held-off render rewrites the page and leaves the PDF alone. The digest stays the body, so a moved clock cannot mint an edition; the colophon names the dated file.

With content-change minting, all three report types are citable.

### Which downloads are editions

**Compiled findings are editions; indexes over other people's records are not.** That rule decides every case:

- **The finance CSVs are editions** — per-country `{ISO3}-nonstate-{edition}.csv`, the all-Africa file, on the same terms as the reports. The gate for a CSV is a byte comparison against the newest retained edition (a CSV from unchanged data is the same file; a PDF never is, since it carries its build date). The data CSV and its field dictionary carry independent editions.
- **The catalogue is not an edition.** `raw-catalogue.csv` stays at its undated URL, republished wholesale on every build: every row points at a publisher's own document — the pointer, not the claim. If anyone ever cites a catalogue count as of a date, it should become an edition too.
- **The per-country catalogue cut follows the catalogue, not the finance CSV beside it** — same columns, rows removed, undated, republished wholesale. The compiled-finding test decides between two files in one folder.
- **A filtered selection is a cut of the catalogue and not an edition either.** The export points at **the view's own URL**, which re-cuts against the current catalogue when opened, with the build date in the filename to say which cut the file in hand was.

### Not yet

**DOIs.** Zenodo will mint one per dated edition — the academic gold standard — but it adds an external dependency and a deposit step to every publish. Revisit now the site is up.
