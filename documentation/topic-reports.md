# Topic reports — design note

*(The live procedure is `BUILD.md` stage 6 and `RENDER.md` → *Topics*, implemented as `scripts/topic-render.py`. This note is the reasoning.)*

## The decisions

1. **Topic reports are BUILD's.** The rule is not scripted-vs-authored, it is `outputs/` vs `site/`: everything in `outputs/` comes from BUILD, and whether a stage happens to run a script is an implementation detail. RENDER typesets what it finds and judges nothing.
2. **A topic report has no ledger, and there is not meant to be one.** It is a derived view of documents BUILD has already authored: every sentence was drafted against the register, cited on the sentence carrying the fact, and checked inside a country document before it was lifted. A ledger here would be a second record of positions already recorded once — a second thing to keep in step.
3. **Two documents per Level-2 slug** — `{slug}-monthly` and `{slug}-progress`. No status report: it answers *where is this now* for a single place, and the cross-place equivalent is a site surface (the Topics page), not a document.
4. **The progress report is sectioned by indicator, not by place, and covers countries only** *(2026-09-02)*. Since the country progress report moved onto the fixed indicator frame (`progress-report-redesign.md`), a country's own progress document has no per-subject block left to lift — its rows are indicators, not places. So the topic progress report inverts: one `## {indicator}` heading per indicator this subject's frame carries, each holding a `| Country | Developments | Progress |` table of every country whose own report has something to say. The three regions still answer the old per-subject movement ledger, which is not indicator-shaped, and their own progress report is expected to move onto topics rather than the country frame — until it does, they are simply absent from this document rather than carried in a shape it does not use. The monthly is unaffected: it was never keyed to the progress report's structure.
5. **The country and region build runs first, in the same run — a correctness condition, not a convenience.** A topic document derived from a country document stage 4 has not yet moved is stale in a way nothing downstream can detect: well-formed, live links, every check passing. The ordering *is* the integrity mechanism, so the stage checks `rebuild.py --scan` reports no unconsidered sources rather than trusting it.
6. **Checks: G only.** J, L and M are properties of the source documents, enforced where the prose was written, and are not re-implemented against a ledger this unit does not have. The register check has no authored prose to read.

## The unit and the documents

**Unit: one Level-2 taxonomy slug** (38 across ten Level-1 categories). Level-1 roll-ups are deferred — the taxonomy is a strict single-parent tree, so a Level-1 report is a later composition of the same material.

**Filenames use the hyphenated slug** (`outputs/topics/dpi-pay/dpi-pay-monthly.md`, `subject: dpi.pay` in frontmatter): the dot means something in the vocabulary and reads as an extension in a path. **The monthly's sections are places, in alphabetical order by published full name, not ISO3** — a reader scans country names, and the two orders differ (Eswatini under E, `SWZ` under S). **The progress report's sections are indicators, in the frame's own order, and it holds countries only** — the three regions issue no monthly and, since their progress report answers a different frame, currently sit in no topic progress report either (item 4 above).

## It is a lift, with nothing added

The monthly carries everything under a place heading verbatim from that place's document: every block keyed `{section}--{subject}` — **the section is read off the ledger row, never derived from the subject**, and a place can hold more than one block for one subject, all printed in document order under the single place heading. The progress report carries everything under an indicator heading verbatim from each country's own progress table: **the Developments and Progress cells of that country's row for this indicator, and nothing else** — read off the rendered document rather than rebuilt from `indicators.csv`, so the two can never disagree about what a country said. Either way, a heading with nothing to carry under it is not printed — no place with an empty monthly, no indicator no country has evidence for.

**Nothing is authored here — no summary, no cross-place block, no connecting sentence.** An authored summary was proposed and refused. The monthly is the country prose, sliced by subject and ordered by place; the progress report is the country indicator table, sliced by indicator and ordered by country.

**The period is the source documents' period, not a window of this stage's own.** Nothing is aged here; where the unit documents do not share a single period (a partial re-render leaves units on different windows until the next full pass), the topic document states the range they span rather than asserting one it does not have.

**No prose in a topic report is written for a topic reader** — every sentence was drafted to sit inside a country document, where the country is given by the page. Read under a place heading this mostly works; where it does not, the fix is upstream, because a sentence that only parses in its home document is one the country report should not have been carrying either.

## Open point — what `outputs/reports/` is renamed to

If topics get their own tree, the existing tree is renamed for symmetry. `countries/` would be inaccurate — three of the 57 units are regions, and the system's own word for *country or region* is **place** (the facet name, the ledger column, `countries.csv`'s coverage). Recommendation: **`outputs/places/` and `outputs/subjects/`**, with the site continuing to say Countries, Regions and Topics — `outputs/` is the record layer and is named in the record layer's vocabulary. The rename is a separate mechanical commit touching both runbooks and five scripts, and does not block anything: `render.py` derives the output tree from the source path, so the current arrangement works indefinitely.
