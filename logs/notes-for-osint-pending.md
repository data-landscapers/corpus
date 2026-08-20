---
type: doc
title: Notes for OSINT — pending delivery
last_reviewed: 2026-08-20
---

# Notes for OSINT — pending delivery

*(**Temporary holding file, 2026-08-20.** Note 27 was written into `osint-corpus-exchange/notes-for-osint.md` during the 2026-08-20 build, at a moment when the only copies of that file were an untracked one in `C:\CORPUS` and one in `C:\OSINT`, which turns out to be a **mirror** of a master repo on OSINT's own drive and is refreshed after every `SWEEP-CYCLE`. Neither copy is versioned or authoritative, so the note had no durable home. This file is that home until Bill stands up the OSINT/Corpus exchange share, at which point the note goes there and this file is deleted.)*

*(Nothing else belongs here. This is not a second channel — it is one note, parked, because the channel it belongs in was mid-move when it was written.)*

## Note 27, as written

**27** (2026-08-20) — **Two records carry no `hub_line` at all, and one story is held twice under two slugs.** Found while reading the day's records against the ledgers in a CORPUS build; they cost nothing to collect and nothing else looks for them.

**The missing hub lines.** `raw/2026/2026-08-19-standard-bank-expands-unionpay-acceptance.md` (ITWeb Africa, nine markets, `dpi.pay`) and `raw/2026/2026-08-19-tan-ezeebit-zaru-digital-asset-merchant-payments.md` (Tech Africa News, `dpi.pay`) both end their frontmatter without a `hub_line`, and the first also carries no `origin_status`. `raw/2026/2026-08-19-wearetech-lideflow-esso-dong-djafalo-paiements-transfrontaliers.md`, `raw/2026/2026-08-19-nigeria-to-earn-41-million-from-mtns-406-million-dividend-payout.md` and `raw/2026/2026-08-19-smart-africa-afrinic-internet-governance-talks.md` are the same shape. A record with no hub line is still citable and still compiles, so nothing downstream fails — it simply cannot be read at a glance, which is the whole purpose of the field.

**The duplicate.** `raw/2026/2026-08-11-fcdo-sta-s-southern-africa-programme.md` and `raw/2026/2026-08-11-uk-fcdo-xsa-2026-sta-s.md` are the same UK FCDO call at the same URL (`https://www.gov.uk/international-development-funding/science-and-technology-accelerator-systems-sta-s-southern-africa-programme`), held under two slugs. CORPUS cites both on one ledger row rather than choosing between them, because a slug is a permanent identifier and picking a survivor is OSINT's call, not CORPUS's.

## Note 28, as written

**28** (2026-08-20) — **`@WIKI-SYNC` had never run once since it was created on 2026-08-16, and the reason is mechanical rather than an oversight: the condition gating its first run cannot become true.** *(Found by a CORPUS session reviewing Bill's supposition that the deliberative loop should go back into `SWEEP-CYCLE`; read off the `C:\OSINT` mirror, confirmed fresh as of 2026-08-20 08:44, and corroborated by Bill, who started the first run by hand the same morning.)*

**The evidence that it never ran.** Day 7 in `logs/sweep-cycle_log.md` carries `Skip = x` and a blank `Start`, with `End`, `Duration` and `Prev Duration` blank too. A blank `Start` sorts oldest and would therefore be selected first every single night — the skip is the only thing standing in front of it, and `SWEEP-CYCLE.md` is explicit that a skipped row is passed over **leaving `Start` untouched**, so nothing ages and the row can never come up. The cycle's own closing lines say so in as many words: `the standing 4/7 skips` (2026-08-17) and `rows passed over for skip: Day 4 (SWEEP-COUNTRY-BUDGET), Day 7 (@WIKI-SYNC)` (2026-08-19).

**Why the skip was never cleared.** `documentation/cc-reset-instructions-2026-08-16.md` Session 3 step 3 sets the trigger for the first sync: *"repeat nightly runs (braked, normal) until every row's `Start` post-dates 2026-08-16, then one `WIKI-SYNC`"*. Day 4 (`SWEEP-COUNTRY-BUDGET`) is itself skipped because the budget layer is suspended, so its `Start` of 2026-08-03 never advances, so **"every row" can never be satisfied while that skip stands**. Day 5 (`SWEEP-IATI`) is also still on 2026-08-11. The instruction was followed exactly and the sync was still never due — this is a gate that reads as *not yet* for ever, which is the same failure shape `SWEEP-CYCLE.md` already documents for a `Gate` command erroring as *not due*.

**What it cost, measured.** `logs/ingest-pending-writes.md` went from 396 lines at the 2026-08-16 close to roughly 2,000 on 2026-08-20 — 1,090 delta rows across **37 distinct subjects** and 554 distinct sources, accumulated over 72 Phase A runs. Outstanding acquisitions went from 24 (2026-08-19) to 46. `scripts/uncited-sources.py --recent 1` read ≈76 on 2026-08-17 and is the honest measure of the gap: sources admitted to `raw/` that no page cites yet.

**The queue is shallower than the line count suggests, and that is worth knowing before anyone redesigns around it.** Phase B drains *grouped by target page, opening each once*, so the work is **37 page-opens**, not 1,090 items — albeit with 92 deltas landing on `gov.discourse` in a single open, 88 on `gov.policy` and 73 on `tech.ai`.

**The defect this exposes is in Phase B itself, and it outlives the skip.** `INGEST.md` Phase A slices into ~10-item sub-agents above ~15 items; **Phase B has no slicing rule and no budget check at all**, so the size of the pass is set by how long it has been since the last sync. Because it runs inline and spawns no sub-agents, `scripts/budget-check.py` counts **zero** for the whole pass and the 90-agent brake cannot fire on it however large it gets: the real failure mode is context exhaustion, which the brake is blind to. That is note 26's *"the brake counts sub-agents, not tokens"* arriving in practice rather than in principle. The one thing that makes it survivable is that Phase B's writes are idempotent — `grep -F "[[<source-slug>]]"` on the target before writing, and the queue file deleted only when empty — so a death partway costs a re-walk and not a mess.

**A correction to the record, because it is easy to remember the wrong way round.** `UPDATE-WIKI.md` drained all three queues **to zero**, capped at 10 purely as a safety stop its own text says *"was never meant to be the normal ending"*. The cap of **3** is `WIKI-SYNC.md`'s own, new on 2026-08-16. So "restore the three-loop to the nightly cycle" would install the *new* bound on the *old* cadence — a combination that has never run.

**The three passes are not alike, and the loop exists for only two of them.** `WIKI-SYNC.md` states the reason itself: reconcile and acquire stage primaries back into `new/`, so the next iteration's Phase A picks them up. **Phase B does not refill `new/`** — it is per-page, idempotent and mechanical, and it is also the pass whose backlog actually hurts, since it is what leaves sources uncited and intersections stale. Reconcile and acquire are the deliberative, expensive ones the 2026-08-16 reform was built to take off the nightly path. **Splitting them is available and cheap**: Phase B returns to the nightly close as a single unlooped pass, reconcile and acquire stay on the weekly row. That fixes the backlog without re-importing the cost that made one evening run ~$83.

**What is owed here, and what is not.** Clearing Day 7's `Skip` is a one-cell edit and restores the weekly cadence the design already intends; it wants doing whatever is decided about nightly. Whether Phase B then moves back to the nightly close is a design decision with a cost attached, and the measurement that settles it is the first sync run itself — four days of backlog under Sonnet-everywhere, which is the worst case that will ever be seen. **CORPUS has made no change of any kind here**, per `CLAUDE.md`: this note is the finding, and the edits are OSINT's.

**One consequence on the CORPUS side, for completeness.** Nothing CORPUS publishes is wrong because of this — its reports resolve every citation through `raw/` and its own catalogue, and hub compile runs nightly from ingest. What is affected is `intersections_read` in the status baselines, which is as stale as the last sync, and which matters only when `STATUS-INIT` next runs on a unit.

**29** (2026-08-20) — **The primary text of Central African data-protection Law 24.001 is carried by the AfDB indicator dataset at an `arcep.cf` URL, which sits against two dated findings on the CAF hub.** *(Found by a CORPUS `STATUS-INIT` run on CAF, from `prep/africa-dpi-data.csv`. CORPUS has not fetched the URL and makes no claim that it serves — the test is OSINT's.)*

**The URL.** `https://arcep.cf/fr/images/documents/reglementation/lois/Loi_24_001_portant_protection_des_donnes_a_caractere_personnel.PDF`, appearing twice in the CAF rows of the AfDB dataset. It is **not in the CORPUS catalogue**, so the wiki does not hold it, and it has therefore been queued in `africa-acquire.csv` as `CAF / gov.protect / 2024` in the ordinary way.

**What it sits against.** `wiki/places/CAF.md` → *Record not held* states, as of 2026-07-20, that *"the primary text of 24.001 is still not held"*. The same hub's acquisition section states, as of 2026-07-26, that **`arcep.cf` still does not exist as a site** — root answering HTTP 200 with *"Site en construction"*, *"every deeper path 404s, third consecutive confirmation"*, and *"no ARCEP annual report or budget document is published anywhere"*. A deeper `arcep.cf` path to a document tree is exactly what that third confirmation rules out, so either the path test has a false negative or the tree sits somewhere the test did not reach. If it is the latter, the regulator's whole `documents/reglementation/` tree may be reachable, and ARCEP is a source the hub names as publishing nothing at all.

**Why this is more than the acquire line already raised.** The queue says *acquire this document*. It does not say *your acquisition test for this domain may be returning a false negative on a domain you have written off three times*. The second is the finding worth acting on, and only a reader holding the hub can see it — a `STATUS-INIT` extraction agent sees one dataset row and nothing else.

**What CORPUS did with it.** `CAF-status.md` states the law's provisions from this primary rather than from the secondary review it would otherwise have rested on, which is the better source under *the better source wins*. Nothing was changed in `C:\OSINT`.

## Note 30, as written (2026-08-20)

*(Supersedes the copies of notes 30, 31 and 32 parked here earlier the same day. All three were collapsed into this one before delivery, on Bill's instruction that notes be decisive; 31 and 32 stand as withdrawn stubs in the exchange file.)*

**30** `[ACT]` (2026-08-20, rewritten the same day before delivery) — **The geographic remit has no clause in the ingest screen. Here is the rule, the 23 records to delete, and the 22 to requeue through `new/` so the fixed screen is tested on real items.** *(Bill's ruling and Bill's plan for executing it, 2026-08-20. Notes 31 and 32 were folded into this one before either was delivered — three notes about one problem was the disease, not the diagnosis.)*

## The rule

The remit is **Africa**. Non-African material is admissible in **exactly two** cases:

1. **a sovereignty issue** filing under one of the closed `geopol.*` slugs — great-power positioning, rivalry and strategic influence, per the curator ruling of 2026-07-20;
2. **material treating the global south generally**, which includes Africa inside its own subject — the `XGL` place, already labelled *Global/Developing Countries* in `lookups/countries.csv`.

**A single non-African country's domestic story is out**, however transferable the lesson looks.

## Why it is not being applied

`SWEEP-DAILY-OFFLIST.md` → *Track B* casts globally on purpose and defers the bearing-on-Africa judgement to ingest, on the stated reasoning that *"a sweep agent judging 'bearing on Africa' from a snippet is worse-placed than ingest reading the full body, so a ~30% ingest-side reject rate on Track B is that design's known cost"*. But `INGEST.md` step 1 and `CLAUDE.md` → *The material* define scope **purely by subject** — *"falls outside data governance and digital transformation"* — with **no geographic clause at all**. The test the sweep hands off does not exist at the other end, which is why Japan's training-data rule and Korea's teen-algorithm debate pass: both are unambiguously data governance.

**`XGL` is half the fix.** It currently means *no African place* in practice — Türkiye's national AI plan, a Spanish press lawsuit, the Philippine AI Regulation Act and an Iowa attorney-general coalition all carry it. Applied to its own definition the rule becomes mechanical for both sides: **African place, or `XGL`, or `geopol.*` — else out.**

## Delete these 23

Single non-African country domestic stories, no sovereignty framing, no African bearing. Verified one by one against title, publisher and facets.

```
2026-08-19-thestar-anutin-th-ai-passport-five-million
2026-08-19-thailand-ai-pass-data-contract-scrutiny
2026-08-19-korea-times-teen-algorithm-rules
2026-08-19-japan-ai-training-data-disclosure
2026-08-19-india-sebi-ai-rules-kill-switch
2026-08-19-ftc-personalized-pricing-enforcement-comment
2026-08-19-amnesty-argentina-ai-surveillance-commondreams
2026-08-18-medianama-india-digital-competition-bill-market-study
2026-08-15-india-sebi-digital-kyc-nri-portability
2026-08-14-washington-state-ag-first-data-privacy-report
2026-08-14-philippines-national-cybersecurity-agency-bill
2026-08-14-india-har-ghar-tiranga-data-protection-violations
2026-08-14-eu-e-evidence-regulation-cross-border-data
2026-08-14-eu-cyber-resilience-act-draft-standards
2026-08-13-taiwan-ai-cyberattack-moda-focustaiwan
2026-08-13-taiwan-ai-assisted-cyberattack-guardian
2026-08-13-malaysia-national-data-commission-ai-oversight
2026-08-13-india-supreme-court-high-risk-ai-public-welfare
2026-08-13-french-cnil-agentic-ai-note
2026-08-13-california-data-broker-enforcement-locatesmarter
2026-08-12-us-dhs-thomson-reuters-clear-fourth-amendment-letter
2026-08-12-eu-ai-act-global-firms-compliance
2026-08-11-south-korea-pipa-amendment-civil-society-opposition
```

None is cited by anything CORPUS has published: every one of the 45 is absent from every ledger `sources` column and every status baseline, checked before this note was written. So no slug retirement is owed and the standing constraint *A record that leaves `raw/` takes a published citation with it* is not engaged. **Note 4's index question still is** — see *The mechanism* below.

## Requeue these 22 into `new/`

Not because they are wrong, but because **re-adjudicating them is the test that the fixed screen works on real items**, which is the whole point of doing it this way rather than hand-correcting the fields. If the rule is right, the first 15 come back with an African place, the next 4 come back as `XGL`, and the last 3 get a ruling that does not exist yet.

**Should come back with an African place** — African subject, `places` simply empty. Deleting any of these would lose real material:

```
2026-08-17-oadc-ai-analytics-intelligence-sovereign-ai-cloud
2026-08-17-naran-raises-10m-lease-to-own-mobility-africa
2026-08-17-mtn-digital-infrastructure-bayobab-gm-appointment
2026-08-17-flutterwave-caliza-usd-accounts-african-companies
2026-08-17-africas-real-gold-mine-isnt-underground
2026-08-17-africa-single-payments-market-currencies-divided
2026-08-15-africa-cepi-digital-policy-webinar
2026-08-14-what-jumia-s-50-million-raise-says-about-its-path-to-profitability
2026-08-13-world-bank-s-ifc-invests-25m-in-jumia-to-boost-africa-s-digital-commerce
2026-08-13-jumia-l-ve-25-millions-usd-aupr-s-de-la-sfi-pour-acc-l-rer-sa-croissance-en-afri
2026-08-13-flutterwave-and-caliza-partner-to-expand-global-payment-access-for-african-busin
2026-08-12-jumia-q2-2026-results-ifc-capital-raise
2026-08-12-ifc-world-bank-jumia-25-million-equity
2026-08-11-sparkle-the-university-of-genoa-and-the-suboptic-foundation-launch-the-second-le
2026-08-11-opinion-piece-u00a0diversity-needs-to-start-with-technology-u00a0not-just-the-wo
```

**Should come back as `XGL`** — genuinely about the developing world or the field as a whole:

```
2025-11-28-itu-global-connectivity-report-2025
2026-08-16-dark-data-final
2026-08-11-cybersecurity-tech-accord-offensive-cyber-statement
2026-08-10-tech-workers-open-letter-ai-pacing-regulation
```

**Need a ruling that does not exist yet** — each is a sovereignty story wearing a non-`geopol` tag, and the ruling wanted is a *tagging* rule (does `geopol.eu` apply to a European digital-sovereignty act?), not an exception to the geographic one:

```
2026-08-19-france-mistral-ai-government-cybersecurity-audit
2026-08-12-etri-explainable-ai-itu-standard
2026-08-11-anthropic-claude-watermark-eu-ai-act
```

The France item is the clearest case: a state excluding a US supplier from offensive audits of its own systems, on explicit sovereignty grounds, tagged `tech.ai` and `infra.cybersec`.

## The mechanism — the one thing that will break this if it is skipped

**A deleted or requeued record's URL loses its adjudication, and the next sweep re-admits it.** `lookups/raw-url-index.csv` is *"one row per source in `raw/`"* and `--rebuild` regenerates from `raw/` frontmatter, so moving the file out removes the URL's `admitted` row. `logs/sweep-url_log.md` — which `INGEST.md` tier 1 reads for `admitted`/`dropped`/`contradiction` — is pruned to **one rotation**. `logs/drop-list.csv` is the origin screen's and works at **domain** level. So within one rotation these 45 URLs are un-adjudicated and the sweeps will fetch them again.

Two consequences, opposite ways round:

- **The 23 deletions need a durable negative adjudication**, or they come straight back and the second admission looks exactly like a first. The natural home is a `retired` state in `raw-url-index.csv` itself, since it is the one store that survives for ever and is already read at tier 1. **The requirement is that the negative record outlives the positive one**; the design is OSINT's.
- **The 22 requeues need their index rows removed** (`raw-url-index.py --remove URL`), or tier 1 drops every one as `DUP-EXACT` before the screen ever sees them and the test silently runs on nothing.

This is the operational half of **note 4**, which has said since 2026-08-13 that a permissioned `raw/` deletion must also clear the slug and asked whether the DB earns its keep. Nothing new is being raised here — it is the same question, now with a batch of 45 about to walk into it.

## What CORPUS has already done

`scripts/lint-scope.py` runs as stage 2a of every build and sorts the catalogue three ways: **in** (African place or `geopol.*` tag), **XGL unverified** (placed `XGL`, no `geopol.*` — admissible if it earns the code, which is a reading no lint can do), **unaccounted** (none of the above). `scripts/bulletin.py` now filters the daily bulletin on the same rule from the same library, so out-of-remit records stop reaching a published page from today. Both **report and never gate**: CORPUS cannot enforce a rule over records it may not write.

Corpus-side scope of the backlog, for context: 10,059 of 10,255 catalogue records are in remit, 151 are `XGL` unverified, 45 are the set above. **The 151 is not a backlog to clear at speed** — it holds *Closing the Adoption Gap: How AI Is Being Built in the Global South* and a Club de Madrid paper on governing global digital public goods, both of which plainly earn the code. It settles itself as `XGL`'s meaning is tightened.

## Note 33, as written (2026-08-20)

**33** (2026-08-20) — **Two `title:` fields are stored mojibake, and both reach a published CORPUS page.** *(Found while adding the bulletin's remit filter, 2026-08-20. Small, and mechanical to fix; raised because CORPUS cannot fix it and both are on live pages.)*

`raw/2026/2026-08-19-turkiye-today-national-ai-action-plan-2026-2030.md` carries `TÃ¼rkiye unveils national AI action plan for 2026-2030` — UTF-8 read as cp1252, so `ü` became `Ã¼`. `raw/2026/2026-03-04 Rwanda–Anthropic AI deal targets health, education gains.md` has the same fault on an en dash: `Rwandaâ€“Anthropic`. They are the only two of 10,255 catalogue titles affected, so this is a one-off in whatever fetched them rather than a systemic encoding problem — worth naming the cause if it is findable, since the same reader would do it again.

Both surface publicly. The title is carried verbatim into `outputs/catalogue/raw-catalogue.csv`, which is published as a downloadable table and drives the catalogue's browse page, and the Türkiye record is on today's country bulletin. **CORPUS will not repair them in its own catalogue** — it is a derived view of `raw/` and a correction there would be overwritten by the next build and would hide the fault meanwhile. The repair is one character each, in `raw/`.

## Note 34, as written (2026-08-20)

**34** `[ACT]` (2026-08-20) — **One protocol for handling findings, identical on both sides — and yes, the irony of a note about having too many notes is noted.** *(Bill's instruction, 2026-08-20: write it down so CORPUS and OSINT handle issues the same way. This note exists to replace future ones. If it works, both queues get shorter; if it does not, it is one note to delete.)*

### What Bill said

> *"We have too many notes for me to keep up with, and many notes create the need for new notes/checks etc. Both OSINT and CORPUS need to be more decisive… We are heading towards a 90% automated solution. If I properly read every note and comment I wouldn't get any work done. This isn't a criticism — it's a reflection on how we need to move forward. I trust you and OSINT. If something goes wrong it will become obvious at some stage (as, for example, me reading the bulletin) and we can fix it then."*

The last sentence is the load-bearing one. **The recovery path is real** — Bill read a bulletin, found nine out-of-remit items, and the whole thing was fixed the same afternoon. A system with a working recovery path should spend far less on prevention-by-consultation than one without.

### The protocol — five rules, the same for both sides

**1. Take the action. The escalation test is reversibility, not importance.** If a later run can undo it, do it now and log it. Importance is not the test and never was: a wrong ledger row on a living document is important and completely reversible; a slug reissued under a live citation is small and permanent. **Where the work belongs to the other side, decide what should happen and write *that*** — the decision and the named files, not the analysis behind it.

**2. Three bands, and `[CRITICAL]` is new.**

| Band | Means | Where |
|---|---|---|
| `[CRITICAL]` | irreversible, or already public | read first, always |
| `[ACT]` | decided; the reader executes, they do not adjudicate | the queue |
| `[FYI]` | on the record, asks nothing | one log line, or the queue if the other side owns it |

`[CRITICAL]` is for evidence loss with no backup, a published page stating something false, leaked source text, a legal or licensing exposure, a slug reissued under a live citation. **If a later run can undo it, it is not `[CRITICAL]`.** Expect it empty most weeks — a band that fires often is one that gets skimmed, which is the failure it exists to prevent. OSINT's `reviews/post-run-notes.md` has no such band today and wants one; CORPUS has added it to `notes-for-osint.md` and to `logs/messages-for-bill.md`.

**3. A finding that carries its own solution is a task. Do it and log it.** This is OSINT's own bar, copied from the housekeeping register on 2026-08-03, and it is the single most useful line in either system. CORPUS has adopted it verbatim.

**4. Before writing a note, check whether one already covers it.** A restatement of an open note is worse than silence: it doubles the reading and splits the history. Three of the four notes CORPUS wrote on 2026-08-20 were withdrawn within hours for exactly this — one of them re-asked what note 4 had been asking since 2026-08-13.

**5. Reasoning lives in the repo that owns it, never in the queue.** The queue carries the decision and the work. The argument goes in `documentation/` or the relevant procedure file, where it is read once by whoever maintains it rather than every time the queue is opened.

### What each side takes from the other

**CORPUS has adopted three things from OSINT**, which were ahead on this and had been since 2026-08-03:

- **The bar** — *an entry that carries its own solution is a task, not a note* (rule 3 above).
- **The cap that forces action.** `CLAUDE.md` → *Reporting*: at 10 open notes CC does not write an eleventh, it takes the conservative option itself and logs it. **This is the best mechanism in either system**, because it converts queue pressure into decisions instead of into backlog. CORPUS now caps `logs/messages-for-bill.md` at **five open blocks** on the same rule; the run that would write the sixth takes the conservative option and logs it instead.
- **Enforcement rather than assertion.** Lint #24 counts every open note's words and both caps. A rule nobody measures drifts — which is what happened to the 60-word limit before #24 existed, and what happened to CORPUS's message file, which reached ten blocks and 102 lines with nothing counting.

**OSINT might take one thing from CORPUS:** the **withdraw-and-stub** move. When a note turns out to be wrong, misfiled or duplicative, move the full text to a resolved file and leave a one-line stub at the number saying why. It keeps numbers stable for citations, keeps the queue to what is still owed, and — the part that matters — makes withdrawing a note cheap enough to actually do. On 2026-08-20 CORPUS took its OSINT queue from **21 open notes to 11** that way in under an hour, resolving two as verified-done, consolidating six into one, and withdrawing two that were never OSINT's to begin with.

### What a review of OSINT's own files found

*(Read-only, from the `C:\\OSINT` mirror, 2026-08-20. CORPUS has changed nothing. The design is sound throughout — everything below is drift in practice, not a fault in the rules.)*

**The queue is pinned at its cap, which means the cap is doing the bar's job.** Ten open, every one under 60 words, lint #24 holding — mechanically perfect. But at least two carry their own solution and are therefore tasks under OSINT's own bar: **214** (the `acquisitions` tally undercounts because `STATUS.md`'s count requires a literal `http(s)` and some lines do not carry one) and **219** (`budget-check.py` counts only level-1 spawns, missing nested sub-agent cost). Both are script bugs with one obvious repair each; neither is a ruling only Bill can give.

**Two more have a conservative option sitting in plain view.** **200** — five `lookups/sweep-journals.csv` rows read dead or unproductive; **208** — `diggers.news` paywalled on two consecutive runs. Under *Act. Log after* the answer to both is: drop it, log it, restore it from git if it turns out to matter.

**Three are one fault under three numbers.** **209**, **210** and **218** are all the sub-agent forking/blocking failure — a background-fork violation, the finding that a level-1 sub-agent cannot block on its own child, and that failure recurring with a 0-byte transcript. That is one architecture finding with three entries, and it is the same note-breeding pattern Bill named. Consolidating them to one number would free two slots in a queue that is at its cap.

**Lint #25 is reporting noise as findings.** Nine root procedure files are over their ratchet cap — but by **1 to 10 lines, 0–5%**: `SWEEP-CYCLE.md` +10, `STATUS.md` +8, `FINANCE-COMPILE.md` +3, `FINANCE-PAGES.md` +3, then six more at +1 or +2. Note **206** escalates this as a `[DECIDE]`; it is a trim-or-raise decision, reversible either way. **And five capped files no longer exist** — `ENTITY-PASS.md`, `REPORT-COUNTRY.md`, `REPORT-MONTHLY.md`, `REPORT-REGION.md`, `REPORT-UPDATE.md`, all retired to CORPUS in the report-layer migration. `lookups/procedure-caps.csv` still carries rows for them. That is a five-line deletion and it is the clearest "carries its own solution" case in the set.

**The rest of the estate is healthy and worth saying so**, because a review that reports only faults misrepresents the thing it reviewed: housekeeping is at 6 open, acquisitions at 3 untried and 3 blocked, the fetch list at 2. Nothing else is accumulating. And `REPORT-LINT.md` is the model the other passes should be read against — *"This check fixes"*, *"Surface only where the name is a genuine question"*, *"a failure with a known repair is repaired by the calling pass, not reported"* — including its own record of retiring a `[DECIDE]` that should never have been one.

### What CORPUS has already done under this protocol

`CLAUDE.md` → *Be decisive — the bar for asking has moved up* carries the rule. `logs/messages-for-bill.md` went from ten blocks to one, every deletion verified first rather than assumed — among them the question of whether 19 status baselines built before a URL-splitting fix owed a rebuild (they did not: no surviving baseline predates it). Two standing questions were decided in place rather than left open. Its OSINT queue went from 21 open notes to 11, with zero `[CRITICAL]`, and two findings that were never OSINT's moved into `documentation/dpi-data-defects.md` where they belonged.

One defect surfaced during that verification and was fixed rather than reported: `report-register-check.py --unit all` matched a unit literally named `all` and printed a clean pass over nothing — `0 hits, 0 documents outside band, check H: 0` — while the same command with no `--unit` reported 78 documents outside band. **A check that reads nothing must never look like a check that found nothing.** Worth a glance at OSINT's own `--unit`-style arguments for the same shape.
