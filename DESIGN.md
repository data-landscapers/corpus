---
type: doc
title: Phase 3 — the public site
status: design, nothing built
last_reviewed: 2026-08-06
---

# Phase 3 — the public site

*(Design record, opened 2026-08-05. Phase 3 of the three-phase plan — automated collection → automated reporting → public website. Nothing here is built. This file holds what has been settled, what follows from it, and what is still open; it is revised, not appended to. When the site build lands, the runnable parts move to a root procedure file and this file keeps only the reasoning.)*

## What it is

A public, browsable surface over the wiki, at **corpus.data-landscapers.com**, feeding and fed by the long-form output at data-landscapers.com.

The site is a **derived view**, generated from `outputs/`. It is not a second store, it holds no state of its own, and nothing on it is authored by hand. That is the same relation a place hub has to the sources beneath it — a hub is a derived view, not a document — applied one layer up.

## 1. Settled

Decisions taken and not to be re-opened without a reason. Each is a decision Bill has made, not an inference.

- **The site is `corpus.data-landscapers.com`** *(Bill, 2026-08-06)*. Chosen over `atlas.`, `base.` and `records.`. Site and repo carry one name, so there is nothing to map between them, and *corpus* is the term of art for a body of collected texts — which is what this is.
- **Look and feel matches data-landscapers.com.** Same family, not a separate identity.
- **The OSINT repo is private and nothing served comes from outside `outputs/`.** The build reads OSINT — that is how data reaches the site (§8) — but it reads committed `outputs/` only, never writes, and nothing else in the vault is published. Access to the full vault, bodies included, is granted individually on request: a named list of researchers who asked and why, which is better grant evidence than a download count.
- **Corpus is the single site-side repo** *(2026-08-06)*. It manages, prepares and serves the data as well as the site — the CSVs, PDFs and HTML published from `outputs/`, rewritten every time those reports are updated. There is no third repo: OSINT is the store of record and nothing else, Corpus is everything downstream of it.
- **PDFs are tracked in Corpus** *(2026-08-06)*. This reverses an earlier position and is dealt with in §8.
- **Every published file carries its build date in the filename**, and earlier editions are retained for re-access. This reverses an earlier position (no retention) and is the right way round: a citation to a dated edition stays checkable. Retain silently, expose only current plus a quiet "earlier editions" affordance — no version picker to maintain.
- **All HTML is browsable without an account. All downloads require one.** Now that Corpus both serves the data and is public, the wall is a courtesy — the CSVs and PDFs are one clone away. That is accepted rather than discovered: registration measures interest and gives grant evidence, it was never a control.
- **Registration takes three fields — name, organisation, email.** Everything else is derived, not asked.
- **An API with key control comes later.** Not at launch, but the data shapes should not preclude it.

## 2. Content at launch

| Surface | Source | Notes |
|---|---|---|
| Catalogue | `outputs/catalogue/raw-catalogue.{json,csv}` | 7,770 records; metadata only, never bodies |
| Country reports | `outputs/reports/{ISO3}/` | Status, monthly update, twelve-month progress |
| Regional reports | `REPORT-REGION.md` (written 2026-08) | Progress only — the status and monthly reports are not issued for a region |
| Topic reports | *(REPORT-TOPIC.md, unwritten)* | A Level-1 category, or one Level-2 slug, across places |
| National budgets | `outputs/budgets/{ISO3}-budget.csv` | 17 countries initialised |
| Non-state finance | `outputs/non-state-finance/` | Per country, plus `all-nonstate.csv` |
| Metadata | frontmatter, facets, freshness | Extensive, and part of the offer rather than an afterthought |

One of the seven does not exist yet: `REPORT-TOPIC.md` is named in `wiki/report-layer.md` as still to be written. The site cannot launch the Topics section ahead of it. `REPORT-REGION.md` has since been written.

## 3. Structure

**Six top-level sections: Countries · Regions · Topics · Catalogue · Data · Method.** Plus account.

**Lead with place and topic, not document type.** Every artefact on the launch list except the catalogue hangs off a country, a region or a taxonomy slug. Filing by document type — "Reports", "Datasets", "Downloads" — forces a reader to know what they want before they can look, and the audience does not arrive wanting *a progress report*; they arrive working on Algeria, or on data protection.

**The country page is the atomic unit.** Position statement and as-of date; the three reports as dated rows with read (open) and download (gated); the ledger counts including ***Not held***; the finance summary; the source count into a filtered catalogue view. Region and topic pages take the same shape with whatever reports they carry.

**`Data` is the tables as tables** — the CSVs for someone who wants the numbers rather than the narrative. It is the same data as the country pages, at a different resolution, and it is the second of the two audiences (policy readers and researchers, weighted equally) getting what they came for without a separate site.

**`Method` is content, not boilerplate.** Inclusion criteria (the origin screen), how currency and dating work, what *Not held* means, the licence, the retention policy, the privacy notice. A project about data governance publishing an exemplary account of its own practice is a credential, not overhead.

## 4. Three design commitments

These are what distinguish the site from every other Africa-digital dashboard. They are cheap, because the base already holds what they need.

**Not held is a counted, visible number.** Eight of Algeria's ninety-nine tracked items. Publishing your own gaps says the base knows the difference between *no* and *we don't know*, and it makes depth-on-demand self-documenting: a thin country looks honestly thin rather than neglected.

**Every figure is one click from its source record.** Already true in the data and true almost nowhere else. Made visible, it answers *where did that number come from* — which is the question the whole project exists to be able to answer.

**Build dates and earlier editions in the open.** Freshness is a fact about the page, stated on the page, in the same idiom as every dated figure in the wiki.

## 5. Prototypes

- `catalogue-prototype.html` — working browse-and-filter over all 7,770 real catalogue records. Facet counts recompute against the *other* active filters so a reader never clicks into an empty result; type-ahead inside the long lists (62 places, 38 topics); filter state in the URL hash so a filtered view is citable. Double-click to open; no server.
- `build-catalogue-data.py` — regenerates the prototype's data file (`catalogue-data.js`). Bespoke scaffolding; delete all three when the real build lands.
- `prototypes/record-viewer.html`, in the OSINT repo — the earlier record-rendering prototype. Its palette is the working basis for the site's.

The first two live in this repo (Corpus) alongside this file; paths above are relative to it. They move to `prototypes/` when the layout in §8 is created, and are deleted when the real build lands.

## 6. Open

- **Serving shape of the catalogue.** 5.9 MB JSON at 7,770 records; ~23 MB at the 30,000 projected for spring 2027. A single fetch stops being defensible around 15–20k rows. `raw/` is already sharded by year, so sharding the catalogue the same way is nearly free — but the boundary is expensive to move once anything external consumes the file. Decide before launch, not when it breaks.
- **Whether the status report's re-renders are retained.** §1 settles that every published file carries its build date in the filename and earlier editions are kept. The status report is *live* — `REPORT-UPDATE.md` re-renders it on any night a row moved, and its markdown filename deliberately carries no period. Applying dated retention to it means a new tracked PDF per unit per night its ledger moves, which is the term in §8's volume estimate that could run away. The conservative default, and what to build unless it is overruled: the two dated artefacts (monthly, progress) get retained dated PDFs because those are what a citation points at; the status report is published as one current file, rebuilt in place, carrying its build date on the page rather than in the filename.
- **The home page.** It has to say what this is, to someone arriving from a link, in about eight seconds, without becoming a dashboard. Hardest page on the site.

## 7. Preconditions

Not website work, but the website cannot launch over them.

- **Repo size.** 4.6 GB and growing ~150 MB/day; GitHub recommend under 5 GB. Private or public, it is the same problem, and it makes "contact me for vault access" a chore rather than an offer. The 425 tracked PDFs in `raw/` are the weight, and the reasoning that removed 507 budget-archive PDFs applies to them.
- ~~**`capture-rule.md` and `build-catalogue.py` describe a private vault that is never republished.**~~ Cleared 2026-08-06. `outputs/` carries no verbatim bodies, so publishing it does not touch the CDPA s.29 basis, which is a claim about the bodies in `raw/` and stays true. `build-catalogue.py` already says the catalogue is public and sends readers to the publisher, so it never disagreed. A wording point remains in `capture-rule.md` and is note 2 in `NOTES-FOR-OSINT.md`.
- **A consolidated, versioned, methodology-documented cross-country dataset** (2026-08-02 review). Fifty-nine per-country CSVs are not a citable dataset, and the budget CSV's programme grain is documented as broken. The site should launch on one or it spends its credibility on day one.
- **REPORT-LINT over the reporting layer.** The review's finding is that the system's outputs are ahead of its verification; a public site is the largest possible extension of the output surface, and publication raises the cost of a MOZ-class defect by an order of magnitude.

## 8. How data reaches the site

*(Settled 2026-08-06. Replaces the earlier "Publish" section, which assumed a publish pass running inside OSINT.)*

**Corpus pulls; OSINT never pushes.** A build step in Corpus reads OSINT's committed `HEAD`, diffs `outputs/` against the last SHA it built, converts what changed, and publishes. OSINT holds no credentials for Corpus, contains no part of the site, and gains no publication step in its night.

The alternative considered was a push at the close of `REPORT-UPDATE` (or of `SWEEP-CYCLE`). Three things decided it:

- **`REPORT-UPDATE` governs one part of `outputs/`.** Budgets, non-state finance, the catalogue and country narratives are written by other passes entirely, and `REPORT-UPDATE.md` states in terms that most nights it writes nothing. A transfer hung off it ships the whole of `outputs/` on the cadence of the report layer alone. Moving the push to `SWEEP-CYCLE`'s close fixes the coverage but not the other two.
- **The night acquires no network dependency.** `SWEEP-CYCLE` has no time envelope and runs unattended past midnight. A push is a step that can fail at 02:00, into a repo the run cannot verify, in a process whose recovery model is "re-run from scratch".
- **One leak gate, at the point of publication.** A guard inside OSINT would check the markdown and not the HTML it becomes, so a push model needs two gates. Pulling puts a single gate where the artefacts actually enter the public repo.

A third shape — OSINT rendering HTML and PDF and writing them into Corpus — was rejected. It moves the presentation layer into the store of record: templates, palette and `WeasyPrint` config would live in the private vault, changing a font would be a commit to it, and the render cost would land inside the serialised night. The site is a derived view; a store that knows how its derived view looks has stopped being only a store.

**The trigger is a commit, not a clock.** Reading committed state rather than the working tree is what makes this safe against a run in progress: a clock-triggered read of `outputs/` can catch a night mid-write, whereas a half-finished night is simply not yet committed. `git diff --name-only {last-built}..HEAD -- outputs/` is the changed set, and it is cheaper than the bookkeeping a push model would have to carry. Both repos are on the same machine, so the read costs nothing.

**The build records the SHA it built from** in `upstream/BUILT-FROM`, which doubles as the citation anchor: every page can state which state of the base it was derived from. It is idempotent and reversible, like every other pass. Where the pulled copy lives, and why it is tracked rather than fetched, is the next subsection.

### Rendering

Markdown to HTML and PDF, in Corpus, at build time — never on request. A request-time renderer is a second uptime obligation, and it makes two downloads of the same dated file differ. `WeasyPrint` keeps one template for the HTML page and the PDF; a second toolchain is a second template that drifts.

**PDFs are tracked in the Corpus repo** *(Bill, 2026-08-06 — reverses the earlier "never tracked in git")*. Tracking them makes the served artefact and its history one object: the repo is the deploy unit, and a dated PDF that a citation points at is retained by the same mechanism that retains everything else, rather than by a second store with its own backup story.

The cost is real and it compounds, because git does not forget a binary. At full country coverage the two *dated* report types alone are 54 × 2 × 12 ≈ 1,300 PDFs a year; report markdown currently runs to a median of 35 KB and a progress report to 58 KB, so call it 300 KB rendered — roughly 400 MB a year, never shrinking. That is affordable for some years and is worth stating as a known trajectory rather than meeting as a surprise. The status report is the variable that could break it, and is in §6.

### Repo layout

*(Settled 2026-08-06.)*

```
upstream/          pulled from OSINT outputs/, 1:1 — never hand-edited
  BUILT-FROM       the OSINT SHA this copy was taken from
  budgets/ catalogue/ country-narratives/ dev/ non-state-finance/ reports/
build/             the pull, the renderer, the templates — the only authored code
site/              rendered artefacts: what is served
prototypes/        disposable scaffolding (§5)
DESIGN.md · NOTES-FOR-OSINT.md · CLAUDE.md
```

**One rule per folder, and the folder is the rule.** `upstream/` is replaced wholesale by the pull, so an edit there is overwritten without warning. `site/` is generated, so an edit there is overwritten by the next build. `build/` is the only place anything is authored. This is OSINT's own `new/ → raw/` discipline — a file's folder is its state — applied to a repo where three different things write.

**The upstream tree mirrors `outputs/` exactly, with no renaming and no reshaping.** Any transformation between the two is a mapping, and a mapping is a second copy of a structure that has to be maintained in step with the first. Adding a directory in OSINT would then require a matching edit here, and forgetting it fails silently. `SWEEP-CYCLE.md` has the same lesson written into it in blood: two copies of one mapping is how a rotation silently stops running.

**Not `osint-outputs/`.** That names the provenance rather than the role, and it imports the upstream vocabulary — *outputs* is OSINT's word for the end of its pipeline, whereas here the identical material is the input. A reader of Corpus should not have to hold OSINT's frame in their head to parse a folder name. `upstream/` states the relationship instead, and carries the conventional meaning: maintained elsewhere, vendored here, do not edit.

**The pulled copy is committed to Corpus, not read from OSINT and thrown away** *(Bill, 2026-08-06)*. The alternative was to read `outputs/` straight out of the OSINT clone at build time, render from it, and commit only the rendered result — borrowing the input for the duration of the build and keeping none of it. Three things decided it:

- **Corpus becomes rebuildable on its own.** Reading from the clone means anyone without OSINT cannot reproduce the site — which is nearly everyone, since it is private — and neither can Bill on another machine.
- **The input sits beside the output, where a reader can check it.** §4 promises that every figure is one click from its source record. Holding the data a page was rendered from in the same repo as the page is that promise at full strength.
- **Git supplies the history for free.** Any past state of the site can be recovered together with the data that produced it, which is what keeps a dated citation checkable years later.

The cost is 16 MB of duplication — the same files existing in both repos — against the ~400 MB a year of PDFs already accepted above.

**Pull exhaustively; publish selectively.** The pull takes the whole tree with no per-directory logic, so new upstream material can never be missed. The build renders only what it has a renderer for, so that material appears in the repo but is not served until someone writes one. `outputs/dev/report-drafting-method-notes.md` is the live case — internal method notes that should be pulled and not published. The two rules together fail closed, which is the right direction for a public site.

### The leak gate

**The build refuses to publish if any staged file carries a source body.** `outputs/` is metadata and compiled prose by construction, so this should never fire — which is precisely why it must be a check that fails the build rather than a comment in a script. A leak into a public repo's history is permanent.

The boundary that matters is bodies, not internal reasoning. This design record and the prototypes sit in the served repo and are therefore public; that is acceptable, and on §3's argument that method is content it is closer to an asset than a cost.
