---
type: runbook
reader: cc
---

# STATUS-INIT.md — country status initialisation

Trigger: **"status-init {ISO3}"**. Builds `outputs/reports/{ISO3}/{ISO3}-status.md`: prose answering, for each of the 39 sub-sections of `documentation/status-outline.md`, **what is the current status of this in this country**. The outline's bullets are the checklist, not the shape of the output. All 54 countries are through; this file stays in force for a re-baseline and because its rules — *When the evidence is borderline*, *Writing*, *Sources and conflicts*, *Verification* — govern every revision `BUILD.md` makes to a baseline. **`documentation/status-init.md` is why each rule and step is as it is**; this file is what to run. It reads OSINT and never writes to it.

## Status is a baseline, and sits outside the collection perimeter

A baseline can state a 1990 law from a source the wiki will never hold. So this process neither reads nor writes `ledger.csv`, check A widens the held set to the evidence it read, and once a unit is initialised nothing re-renders its status from the ledger.

## The one hard rule

**Every stated fact carries an inline hyperlink, on the claim, to the URL of the source that establishes it. No link, no claim.** The wiki and the AfDB dataset are intermediaries; link the primary, and do not write a fact whose primary has no URL. **The one exception** is a count or total the report computes itself: written plainly, unlinked, in its own paragraph marked `<!-- derived -->`.

## When the evidence is borderline, the fact does not go in

**This outranks every writing rule, and the news.** Three outcomes, in this order, never a fourth:

1. **State it plainly**, where the evidence supports it as written.
2. **State it plainly at a coarser grain** the evidence does support — *"the register covers most of the adult population"*.
3. **Drop it.**

**Where two sources of equal tier disagree and recency does not separate them, neither figure is stated**: state what they agree on, or state the position as not established, dated.

## Inputs

- `documentation/status-outline.md` and `status-outline-part-2.md` — 39 sub-sections; `finance.budget` is suspended; `[PROPOSED]` ids are out of scope.
- `lookups/countries.csv`; the hub `wiki/places/{ISO3}.md` (never read whole); `wiki/intersections/*.md` selected on frontmatter **`place: {ISO3}`** — the primary input — plus the region's files for `gov.regional`.
- `raw/{year}/...` for sources; `outputs/catalogue/catalogue-internal.csv` resolves a slug to its URL.
- `prep/africa-dpi-data.csv` (a sourceless negative is ***Not held*** with a `gaps.csv` line, never an absence); `lookups/iiag-profiles.csv`; `outputs/non-state-finance/all-nonstate.csv` for `finance.new`.

## The run

**Three stages: extract, write, assemble.** The first two fan out to subagents by intersection; the third is the parent's.

### Stage 0 — the parent scopes the run

```bash
python scripts/log-line.py --start status-init
python scripts/status-scope.py {ISO3}
```

Read its output in `prep/scope/{ISO3}/`; re-derive nothing by hand.

### Stage 1 — extract, one subagent per source of evidence

**Up to 20 concurrent subagents**, the rest fed in as slots free: one per intersection, three for the indicator rows (disjoint family groups), one for the finance rows. Each is given `documentation/archived/status-init-extract.md` whole, resolves slugs with `python scripts/status-slugs.py {slug} …`, writes facts to `prep/scope/{ISO3}/facts/{name}.json` and returns only a count. **Count the files in `facts/` against the agents before pooling** — a launch over the cap fails silently.

### Stage 2 — write, one subagent per Level-1 chapter

`python scripts/status-pool.py {ISO3}` pools, dedupes and slices. Then one writer per chapter, ten in a batch, each given `documentation/archived/status-init-write.md`, its slice, its sub-sections in outline order with the `###` label and `<!-- slug -->` comment verbatim (empty ones included), and **its output path, `prep/scope/{ISO3}/draft/{nn}-{chapter}.md`, and nowhere else**.

### Stage 3 — the parent assembles

1. `python scripts/status-assemble.py {ISO3} --hub-reviewed {date} --intersections {n}`.
2. `python scripts/status-acquire.py {ISO3} --compiled {date}`, then re-run the assemble. Commit other standing work in the share first, under its own subject; push after each commit.
3. **Verify**: checks A to I on the assembled file.
4. `python scripts/status-progress.py`.
5. Report on two lines: `{ISO3} · sections written NN of 39 · not established NN · sources cited NN · acquire lines NN`, and the run cost.
6. Log and commit, one line a country:

    ```bash
    python scripts/log-line.py status-init "{ISO3}: 39 sub-sections, NN sources, NN acquire lines, A-I pass — ok"
    git add -A && git diff --cached --quiet || git commit -m "{ISO3} status baseline: 39 sub-sections, NN sources"
    ```

**On a failure**, log `… errored on {ISO3} at stage N: <message>` and leave the country unfinished; never issue a partial baseline.

## Sources and conflicts

**The better source wins, and neither intermediary gets a vote**: primary over secondary, official over reported, canonical over syndicated, full text over excerpt, finer date over coarser; for a time-varying figure, the more recent of equal tier. Where that does not separate them, *When the evidence is borderline* governs.

For a URL the catalogue does not hold:

- **dated before 2024** — state the fact, link it, nothing owed;
- **dated 2024 or later** — state it, link it, and add one line to `C:\corpus-osint-xfer\africa-acquire.csv` (`iso3,published,publisher,title,url,sub_section,found,status,notes`). A run rewrites only its own country's rows; `status` and `notes` are Bill's. Read `acquire-done.csv` too: a closed row does not come back.

**No disagreement is narrated.** Where a fact is unestablished, one plain dated sentence about the country — *"No dedicated data protection law had been enacted as at August 2026"* — never about the evidence.

## Writing

- **The first sentence carries the news** — the best-evidenced news, not the biggest. Never open with a definition, a restatement of the question or the oldest fact.
- **No apparatus**: no caveats, hedging, "sources indicate" or note that accounts differ.
- **One continuous narrative per h3**, up to 350 words; no sub-headings, bullets or tables. **A thin section is short, not padded.**
- **Every time-varying figure is dated** — "covered 4.4m people (June 2026)"; structural facts are not.
- **Money in the announcing party's currency**, any USD as a dated conversion.
- House style is `documentation/report-layer.md` §10; links sit on the claim; one line per paragraph, never wrapped by hand.

## `finance.new`

From `all-nonstate.csv`, not the hub's `## Financing` block. Establish the commitments and their window, how many, the leading financiers, instruments and subsectors, and the largest live commitment, each named deal linked; say where `amount_quality` or `status` marks a figure unverified. Counts and totals are computed at extraction and go in a `<!-- derived -->` paragraph.

## Sub-sections the dataset cannot answer

The five `geopol.*` slugs, `data.satellite` and `finance.mou` have no indicator coverage; `gov.regional`, `capacity.research`, `digital.localgov` and `tech.industry` little. Answer them from the wiki; where it holds nothing, one dated sentence saying so.

## Output shape

`outputs/reports/{ISO3}/{ISO3}-status.md`: frontmatter (`title`, `compiled`, `place`, `region`, `built_by: STATUS-INIT`, `hub_last_reviewed`, `intersections_read`, `sources_cited`, `sections_written`, `not_established`, `acquire_lines`), then the chapters — `##` the Level-1 chapter, `###` the Level-2 label, `<!-- slug -->` beneath it — in outline order. No summary, no coverage table.

## Verification

**`python scripts/status-check.py --unit {ISO3}`** runs A to G, I and the frontmatter counts; H needs a reader, and `--openings` prints every first sentence for it.

- **A** — every link is held: in the catalogue, `africa-dpi-data.csv`, `all-nonstate.csv` or `iiag-profiles.csv`. Re-run after every edit pass.
- **B** — every claim is linked (exempt: the *not established* sentence and a `<!-- derived -->` paragraph).
- **C** — every time-varying figure is dated.
- **D** — no `[[wikilink]]` or bare repo path.
- **E** — 39 sub-sections, in outline order, none empty, `finance.budget` absent.
- **F** — every acquire line is dated 2024 or later and complete.
- **G** — no apparatus: none of *reportedly, apparently, it appears, sources indicate, according to available, it should be noted, however it is unclear, the data suggests, some sources, no source, the base, the dataset, the wiki, conflicting, discrepancy*.
- **H** — every sub-section opens on news.
- **I** — as-of honesty: never behind the newest held source it cites.

**A run that fails A, B or G is not issued.**

## What this process never does

Touches `ledger.csv`, the monthly or the progress report. Writes anywhere but `outputs/reports/{ISO3}/`. Cites a link it has not resolved. States a `borderline` fact as written. Picks between two equal-tier sources that disagree. Puts a caveat, a hedge or a word about its own evidence on the page. Narrates a disagreement. Uses a `[PROPOSED]` indicator. Writes `finance.budget`. Pads a thin section.
