---
type: doc
title: Notes for OSINT
last_reviewed: 2026-08-06
---

# Notes for OSINT

*(Rolling. Findings from site work that need actioning **in** the OSINT repo. Corpus never writes to OSINT (`CLAUDE.md`), so anything CC notices there lands here and Bill actions it in an OSINT session.)*

*(Convention follows OSINT's own `reviews/post-run-notes.md`: numbered, unresolved before resolved, oldest first within each, `x` prefixed when done, never renumbered, struck entries deleted 14 days after their cleared date. Each note is one line plus a pointer — the reasoning lives in `DESIGN.md`, not here, so there is one copy of it.)*

## Standing constraints

These never clear. They are properties of OSINT the site depends on, recorded so that changing one is a decision rather than an accident.

**`outputs/` must stay git-tracked and committed.** The site build reads OSINT's *committed* `HEAD` and diffs `outputs/` against the last SHA it built (`DESIGN.md` §8). Verified 2026-08-06: 292 files tracked, committed routinely by the cycle. Gitignoring any part of it, or a cycle that stops committing it, stops the site updating **silently** — there is no error, the diff is simply empty.

**Nothing outside `outputs/` is ever read by the build.** The site is a derived view of the reporting layer, not of the vault. If something needs to reach the site, it has to be written into `outputs/` by a pass; there is no second channel.

**A catalogue slug is a permanent public identifier and must never be reissued.** Once the site is up, a slug is the target of a provenance link inside a PDF that a journalist or academic has already downloaded, and that link has to resolve years later (`DESIGN.md` §9). Retiring a slug is survivable — the URL can say the record was withdrawn, and on what date. **Reusing one for a different record is not**, because it silently redirects an old citation to unrelated evidence, which is worse than a dead link and undetectable from the outside. A replaced or corrected source takes a new slug.

## Unresolved

**1** (2026-08-06) — **`REPORT-TOPIC.md` is not written.** It is named in `wiki/report-layer.md` as still to be written, and the site's Topics section cannot launch without it. `REPORT-REGION.md` has since landed, so this is the last of the two. `DESIGN.md` §2.

**2** (2026-08-06) — **`wiki/capture-rule.md` lines 12–14 say "never republished".** Substantively still true — the claim is about the verbatim bodies in `raw/`, which stay private, and that is what the CDPA s.29 basis rests on. But once a public site exists, a reader who does not already know that distinction will take the site as contradicting the rule. Worth rewording to say the *bodies* are never republished, so the sentence survives the site's existence. Wording, not substance; low priority.

**3** (2026-08-06) — **Repo size.** 4.6 GB and growing ~150 MB/day against GitHub's recommended 5 GB. Not site work, but the site cannot launch over it, and it makes vault access on request a chore rather than an offer. The 425 tracked PDFs in `raw/` are the weight, and the reasoning that removed 507 budget-archive PDFs applies to them. `DESIGN.md` §7.

**4** (2026-08-06) — **No consolidated, versioned, methodology-documented cross-country dataset.** Fifty-nine per-country CSVs are not a citable dataset, and the budget CSV's programme grain is documented as broken (2026-08-02 review). The site should launch on one or it spends its credibility on day one. `DESIGN.md` §7.

**5** (2026-08-06) — **REPORT-LINT does not yet cover the reporting layer.** The 2026-08-02 review's finding is that the system's outputs are ahead of its verification. A public site is the largest possible extension of the output surface, and publication raises the cost of a MOZ-class defect by an order of magnitude. `DESIGN.md` §7.

## Resolved

**x6** (2026-08-06, cleared 2026-08-06) — **`build-catalogue.py` was thought to describe a vault that is never republished.** It does not, and never did: its header calls the catalogue public and says the vault "is not a place to republish them. The `url` sends a reader to the publisher." Checked while clearing the §7 precondition; no change needed.
