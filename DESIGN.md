---
type: doc
title: Phase 3 — the public site
status: design, nothing built
last_reviewed: 2026-08-05
---

# Phase 3 — the public site

*(Design record, opened 2026-08-05. Phase 3 of the three-phase plan — automated collection → automated reporting → public website. Nothing here is built. This file holds what has been settled, what follows from it, and what is still open; it is revised, not appended to. When the site build lands, the runnable parts move to a root procedure file and this file keeps only the reasoning.)*

## What it is

A public, browsable surface over the wiki, at `{name}.data-landscapers.com`, feeding and fed by the long-form output at data-landscapers.com.

The site is a **derived view**, generated from `outputs/`. It is not a second store, it holds no state of its own, and nothing on it is authored by hand. That is the same relation a place hub has to the sources beneath it — a hub is a derived view, not a document — applied one layer up.

## 1. Settled

Decisions taken and not to be re-opened without a reason. Each is a decision Bill has made, not an inference.

- **Look and feel matches data-landscapers.com.** Same family, not a separate identity.
- **The OSINT repo is private and the site never touches it.** Access to the full vault, bodies included, is granted individually on request — a named list of researchers who asked and why, which is better grant evidence than a download count.
- **A second, public repo carries what is served** — the CSVs, PDFs and HTML published from `outputs/`, rewritten every time those reports are updated.
- **Every published file carries its build date in the filename**, and earlier editions are retained for re-access. This reverses an earlier position (no retention) and is the right way round: a citation to a dated edition stays checkable. Retain silently, expose only current plus a quiet "earlier editions" affordance — no version picker to maintain.
- **All HTML is browsable without an account. All downloads require one.**
- **Registration takes three fields — name, organisation, email.** Everything else is derived, not asked.
- **An API with key control comes later.** Not at launch, but the data shapes should not preclude it.

## 2. Content at launch

| Surface | Source | Notes |
|---|---|---|
| Catalogue | `outputs/catalogue/raw-catalogue.{json,csv}` | 7,770 records; metadata only, never bodies |
| Country reports | `outputs/reports/{ISO3}/` | Status, monthly update, twelve-month progress |
| Regional reports | *(REPORT-REGION.md, unwritten)* | Progress only |
| Topic reports | *(REPORT-TOPIC.md, unwritten)* | A Level-1 category, or one Level-2 slug, across places |
| National budgets | `outputs/budgets/{ISO3}-budget.csv` | 17 countries initialised |
| Non-state finance | `outputs/non-state-finance/` | Per country, plus `all-nonstate.csv` |
| Metadata | frontmatter, facets, freshness | Extensive, and part of the offer rather than an afterthought |

Two of the seven do not exist yet: `REPORT-REGION.md` and `REPORT-TOPIC.md` are named in `wiki/report-layer.md` as still to be written. The site cannot launch those sections ahead of them.

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

- `site/catalogue-prototype.html` — working browse-and-filter over all 7,770 real catalogue records. Facet counts recompute against the *other* active filters so a reader never clicks into an empty result; type-ahead inside the long lists (62 places, 38 topics); filter state in the URL hash so a filtered view is citable. Double-click to open; no server.
- `site/build-catalogue-data.py` — regenerates the prototype's data file. Bespoke scaffolding; delete both when the real build lands.
- `prototypes/record-viewer.html` — the earlier record-rendering prototype. Its palette is the working basis for the site's.

## 6. Open

- **The name.** `atlas.` reads best in a citation and matches "mapping Africa's data landscape"; `base.` and `records.` are the alternatives. Undecided.
- **Serving shape of the catalogue.** 5.9 MB JSON at 7,770 records; ~23 MB at the 30,000 projected for spring 2027. A single fetch stops being defensible around 15–20k rows. `raw/` is already sharded by year, so sharding the catalogue the same way is nearly free — but the boundary is expensive to move once anything external consumes the file. Decide before launch, not when it breaks.
- **Whether `outputs/` datasets live in the public repo.** If they do, the download wall is a courtesy — the CSVs are one clone away. That may be the right trade; it should be a choice rather than a discovery.
- **The home page.** It has to say what this is, to someone arriving from a link, in about eight seconds, without becoming a dashboard. Hardest page on the site.

## 7. Preconditions

Not website work, but the website cannot launch over them.

- **Repo size.** 4.6 GB and growing ~150 MB/day; GitHub recommend under 5 GB. Private or public, it is the same problem, and it makes "contact me for vault access" a chore rather than an offer. The 425 tracked PDFs in `raw/` are the weight, and the reasoning that removed 507 budget-archive PDFs applies to them.
- **`capture-rule.md` and `build-catalogue.py` describe a private vault that is never republished.** Whatever visibility is settled, both need to agree with it.
- **A consolidated, versioned, methodology-documented cross-country dataset** (2026-08-02 review). Fifty-nine per-country CSVs are not a citable dataset, and the budget CSV's programme grain is documented as broken. The site should launch on one or it spends its credibility on day one.
- **REPORT-LINT over the reporting layer.** The review's finding is that the system's outputs are ahead of its verification; a public site is the largest possible extension of the output surface, and publication raises the cost of a MOZ-class defect by an order of magnitude.

## 8. Publish, when it is built

A pass, not a manual step — logged in `log.md`, idempotent, reversible.

Renders reports to PDF at build time, never on request: a request-time renderer is a second uptime obligation, and it makes two downloads of the same dated file differ. `WeasyPrint` keeps one template for the HTML page and the PDF; a second toolchain is a second template that drifts.

**PDFs are never tracked in git.** `outputs/` is tracked because it is served, but that rule splits: small textual artefacts tracked, derived binaries regenerated. 54 countries × 3 report types × monthly is ~1,900 files a year.

**The publish pass refuses to push if any staged file carries a body.** A leak into a public repo's history is permanent, and a rule that fails the run is worth more than a comment in a script.
