---
type: doc
title: Notes for OSINT
last_reviewed: 2026-08-06
---

# Notes for OSINT

*(Rolling. Findings from site work that need actioning **in** the OSINT repo. Corpus never writes to OSINT (`CLAUDE.md`), so anything CC notices there lands here and Bill actions it in an OSINT session.)*

*(Convention follows OSINT's own `reviews/post-run-notes.md`: numbered, unresolved before resolved, oldest first within each, `x` prefixed when done, never renumbered, struck entries deleted 14 days after their cleared date. Each note is one line plus a pointer — the reasoning lives in `documentation/design.md`, not here, so there is one copy of it.)*

## Standing constraints

These never clear. They are properties of OSINT the site depends on, recorded so that changing one is a decision rather than an accident.

**`outputs/` must stay git-tracked and committed.** The site build reads OSINT's *committed* `HEAD` and diffs `outputs/` against the last SHA it built (`documentation/design.md` §8). Verified 2026-08-06: 292 files tracked, committed routinely by the cycle. Gitignoring any part of it, or a cycle that stops committing it, stops the site updating **silently** — there is no error, the diff is simply empty.

**Nothing outside `outputs/` is ever read by the build.** The site is a derived view of the reporting layer, not of the vault. If something needs to reach the site, it has to be written into `outputs/` by a pass; there is no second channel.

**A catalogue slug is a permanent public identifier and must never be reissued.** Once the site is up, a slug is the target of a provenance link inside a PDF that a journalist or academic has already downloaded, and that link has to resolve years later (`documentation/design.md` §9). Retiring a slug is survivable — the URL can say the record was withdrawn, and on what date. **Reusing one for a different record is not**, because it silently redirects an old citation to unrelated evidence, which is worse than a dead link and undetectable from the outside. A replaced or corrected source takes a new slug.

## Unresolved

**1** (2026-08-06) — **`REPORT-TOPIC.md` is not written.** It is named in `wiki/report-layer.md` as still to be written, and the site's Topics section cannot launch without it. `REPORT-REGION.md` has since landed, so this is the last of the two. `documentation/design.md` §2. — **Superseded 2026-08-14, for Bill to strike.** The report layer moved to Corpus (`prep/osint-migration.md` R1, R7), so the topic layer is Corpus's to write and is no longer OSINT's to action. Carried in `documentation/design.md` §2 and BUILD.md → *Deferred stages*.

**2** (2026-08-06) — **`wiki/capture-rule.md` lines 12–14 say "never republished".** Substantively still true — the claim is about the verbatim bodies in `raw/`, which stay private, and that is what the CDPA s.29 basis rests on. But once a public site exists, a reader who does not already know that distinction will take the site as contradicting the rule. Worth rewording to say the *bodies* are never republished, so the sentence survives the site's existence. Wording, not substance; low priority.

**3** (2026-08-06) — **Repo size.** 4.6 GB and growing ~150 MB/day against GitHub's recommended 5 GB. Not site work, but the site cannot launch over it, and it makes vault access on request a chore rather than an offer. The 425 tracked PDFs in `raw/` are the weight, and the reasoning that removed 507 budget-archive PDFs applies to them. `documentation/design.md` §7.

**4** (2026-08-06) — **No consolidated, versioned, methodology-documented cross-country dataset.** Fifty-nine per-country CSVs are not a citable dataset, and the budget CSV's programme grain is documented as broken (2026-08-02 review). The site should launch on one or it spends its credibility on day one. `documentation/design.md` §7.

**5** (2026-08-06) — **REPORT-LINT does not yet cover the reporting layer.** The 2026-08-02 review's finding is that the system's outputs are ahead of its verification. A public site is the largest possible extension of the output surface, and publication raises the cost of a MOZ-class defect by an order of magnitude. `documentation/design.md` §7.

**6** (2026-08-11) — **Two counts of the same ledger.** `outputs/reports/KEN/ledger.csv` holds 171 rows, 6 of them `Not held`; `KEN-status.md` frontmatter says `ledger_rows: 146`, `not_held: 4`; `KEN-progress-2026-07.md` says 169 and 6. The country page publishes a *Not held* count as one of its four headline figures (`documentation/design.md` §4), so which number is the place's ledger size has to be settled before it goes on a page — a site whose selling point is stating its own gaps cannot show two of them. Found while building the country-page mock-up.

**7** (2026-08-11) — **`FINANCE-COMPILE.md` documents 18 columns; the CSV carries 20.** `{ISO3}-nonstate.csv` also holds `amount_basis` and `amount_quality`, which the "CSV export" section does not list. The full-table page offers a field dictionary as a download (the cable factsheet's *Download metadata*), and those two rows currently have to be read off the data rather than cited to the spec. Definitions for them would close it.

**8** (2026-08-11) — **The nightly stats want a machine-readable shape, not the markdown report.** `REPO-STATUS.md` writes `reviews/repo-status.md`, which is prose with tables; the home page needs the same counts as data, in `outputs/catalogue/` so the build can reach them (nothing outside `outputs/` is readable — standing constraint above). Proposed as `outputs/catalogue/stats.json`: `generated`, `documents`, `by_year`, `by_month`, `by_place`, `by_topic`. The mock-up counts `raw-catalogue.csv` itself in the meantime and prefers the file the moment it appears, so nothing here blocks. Shape is in `prototypes/build-home-page.py` → `STATS_SHAPE`.

**9** (2026-08-11) — **The site has to duplicate two vocabularies it is not allowed to read.** Country names come from `lookups/countries.csv` and Level-1 subject labels from `lookups/taxonomy.md`, both outside `outputs/`. The home and country pages therefore carry their own copies, which is the two-copies-of-one-mapping failure `documentation/design.md` §8 refuses everywhere else: renaming a category in OSINT would silently leave the site showing the old label. Copying both into `outputs/` — unchanged, as the pull takes them 1:1 — would close it.

**10** (2026-08-13) — **A slug survives in `index/` after its source left `raw/`.** `2026-08-07-nitda-partners-women-educators-on-nationwide-digital-literacy-drive` (Tech Africa News, NGA) is in the catalogue Corpus built on 2026-08-11 and absent from the one built on 2026-08-13. No file for it remains under `raw/`, but the slug is still present in `index/vault.db`. If it was pruned deliberately that is fine and only the dangling index entry needs clearing; if it was not, a source has left the vault unnoticed. Worth settling before launch because of the standing constraint above: once the site is live a slug is a permanent public identifier, and a record that can disappear between two builds is a citation that can break. Found while investigating a catalogue count discrepancy whose other 192 records turned out to be a Corpus-side staleness, not an OSINT one.

**11** (2026-08-14) — **Proposal: `INGEST` could establish the earlier position a progress report compares against.** *(Bill's suggestion; recorded here for an OSINT session to weigh, not actioned.)* Corpus's report ledger carries `position_start` and `position_end` per row — the substance of a position at each end of a twelve-month window, as free text: `30 branches, five banks (2025-08)` against `296 branches, four banks`. `position_end` comes from the record in hand. **`position_start` does not**: establishing it means going back through the wiki for an earlier relevant occurrence of the same object, which is a different kind of search from the one BUILD is doing, and it happens **once per row** — once a row is in the ledger the start position never changes.

That work sits closer to `INGEST` than to Corpus. INGEST is already reading each new record against the base and is already across places, concepts and intersections, which is exactly the traverse `position_start` needs; Corpus reaches `raw/` and `index/` read-only and has no equivalent view. Doing it at ingest would also do it at the one moment the question is cheap — while the record is being placed — rather than at report time on a base someone has to re-enter.

Current state, for whatever it is worth to the decision: `position_start` is filled on 4,112 of 5,421 rows (75%), `position_end` on 4,760 (87%). A row with no `position_start` renders ***Baseline not held***, so a quarter of rows currently publish as having no stated baseline. Bill's own view is that the field is ambitious and he is **not confident it is currently accurate** — so this is worth settling on correctness grounds, not only on where the work belongs. Nothing in Corpus blocks on it; the field degrades gracefully.

## Resolved

**x6** (2026-08-06, cleared 2026-08-06) — **`build-catalogue.py` was thought to describe a vault that is never republished.** It does not, and never did: its header calls the catalogue public and says the vault "is not a place to republish them. The `url` sends a reader to the publisher." Checked while clearing the §7 precondition; no change needed.

12. **The UNITEL outage has two incompatible durations in the base.** `2026-07-30-...unitel-restores-services...` documents restoration in stages — localised from 11:45 on 29 July, full 2G/3G national coverage about 23:00 on 30 July, messaging and electronic airtime back on 31 July, i.e. three to four days. `2026-08-10-angola-unitel-cyberattack-customer-reaction` frames the same event as running 28 July to 5 August, nine days, for about 20.8 million customers. They may be reconcilable — full restoration against residual degradation, and the held source does note card terminals still unreliable four days in — but nothing in the base states which. Corpus has kept the better-evidenced staged account in `AGO-monthly.md` and has not adopted the nine-day framing. *(Raised by BUILD, 2026-08-14.)*
