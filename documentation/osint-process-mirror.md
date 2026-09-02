# The OSINT process mirror

*Written 2026-09-02, Corpus-side, in answer to Bill's question of the same date: how big a job would it be to split the OSINT repository in two, so that the processes that build and classify the base are public while `raw/` stays private.*

*This note is the specification. It lands in Corpus because everything CC produces lands in Corpus; the work it describes is OSINT's, and reaches OSINT as a numbered note in `C:\corpus-osint-xfer\notes-for-osint.md` when Bill says so.*

## The decision

**Publish the process layer as a one-way mirror. Do not split the repository.**

The transparency claim Corpus needs to be able to make is *anyone can read and verify how this base is built*. A published mirror satisfies that in full. A repository split would additionally allow someone to fork the process layer and run it against their own corpus — a capability nobody has asked for, bought at a price paid on every commit thereafter.

The price is measurable. The process layer is 183 tracked files and 2.4 MB against a repository of 17,407 tracked files; the bytes are nothing. The coupling is not: `raw/` is named 417 times across 97 process files, `wiki/` 243 times, `logs/` 203, `reviews/` 142, `sweep/` 94 — roughly 1,100 path references that would cross a repository boundary. Twenty scripts locate the vault with `ROOT = os.path.dirname(...)`, which is to say *the root is my parent's parent*, and that stops being true the moment there are two roots. Fixing it properly means a `paths.py` carrying `VAULT` and `PROCS` from the environment and rewiring 94 scripts through it. That is three to five sessions of work, and then a permanent tax: every change touching both layers becomes two commits in two repositories, and OSINT acquires a third boundary on top of the two it already maintains with Corpus.

A mirror costs about half a session and nothing thereafter.

## What the mirror is

A public repository — `data-landscapers/osint-process` — holding a copy of OSINT's process layer, exported from OSINT by script, never edited in place, never merged back.

It is the same arrangement Corpus already runs for `datatable.js` and `main.css`: one canonical upstream, a copy downstream, and a marker file recording the commit the copy was taken from. The properties that make that work are the ones wanted here. The copy is derived, so it cannot drift silently. The direction is fixed, so there is never a question of which side is ahead. And the marker turns staleness into something a script can see.

The consequence to accept up front: **the public repository takes no contributions.** A pull request against it has nowhere to land, because merging one would make the mirror canonical for that file and break the property the whole arrangement rests on. The README says so plainly, and points correspondence at Bill.

## Where the export runs

**In an OSINT session, against master OSINT. Never from `C:\OSINT`, and never from Corpus.**

`C:\OSINT` is a mirror refreshed on sync. An export taken from it publishes whatever the last sync happened to leave, and a folder absent from the mirror reads as empty rather than as absent — which in an allowlisted export means silently publishing less than intended, with nothing to indicate it. Exporting from the master is the only version of this that is honest about what it published.

Corpus cannot run it for the same reason it cannot do anything else in OSINT: Corpus reads OSINT and never writes to it, and an export script living in Corpus would be a Corpus process depending on OSINT's internal layout, which is exactly what the read interface exists to prevent.

So: `scripts/export-process-mirror.py` in OSINT, run at `SWEEP-CYCLE` close, on the same trigger that already refreshes the `C:\OSINT` mirror. Reusing an existing trigger matters — a mirror that depends on someone remembering to update it is a mirror that will be six weeks stale the first time anyone looks at it.

## The manifest

**An allowlist, never a denylist.** A denylist publishes every new folder by default and only stops the ones somebody thought of in advance; the first time a pass writes somewhere new, it is public before anyone notices. An allowlist fails the other way: something new is invisible to the mirror until a human adds it, and the cost of that failure is a file that should have been public not being public yet.

### Published — 183 files, 2.4 MB

| Path | Count | What it is |
|---|---|---|
| `*.md` at root | 36 | Every procedure file: the sweeps, `INGEST`, `RECONCILE`, `PRUNE`, `LINT`, `STATUS`, `RULES`, `CLAUDE.md` |
| `scripts/*.py` | 94 | The whole script layer, `vault_lib` and `finance_lib` included |
| `lookups/` | 20 | The vocabularies — `countries.csv`, `taxonomy.md`, the deal maps, the sweep source lists, `frontmatter-schema.json`, the FX table |
| `documentation/` | 14 | The method notes, including the two large budget-extraction records and the domestic-finance run log |
| `wiki/` specs | 13 | `index.md`, `intake.md`, `schemas.md`, `facets.md`, `layout.md`, `reference.md`, `capture-rule.md`, `origin-screen.md`, `operations.md`, the finance drivers and record spec |
| `.githooks/` | 5 | |
| `.claude/settings.json` | 1 | |
| `.gitignore`, `.gitattributes` | 2 | The gitignore is itself a process document — it carries the reasoning for the PDF purge and the budget-archive untracking |

### Withheld, and why

**The base itself.** `raw/` (14,522 files), `budget-archive/`, `new-budget/`, `sweep/`, `new/`, `index/`, `outputs/`. These are the corpus and its derivatives. Withholding `raw/` is the point of the exercise: it holds verbatim source bodies, and republishing those is a licensing exposure with no upside.

**Compiled wiki content.** `wiki/concepts/` (38), `wiki/places/` (62), `wiki/intersections/` (661), `places-index.md`, `topics-index.md`. This is the *product*, not the process. It is also the seam that would have been hardest to place in a repository split, and the mirror makes it cheap: the folder is filtered at file level by an explicit list of thirteen names, which no split could have done without physically moving files apart.

**Operational records.** `logs/`, `reviews/`. In-flight state — open contradictions, the fetch list, post-run notes, the decision registers. Nobody verifying the method needs them, and they name work that is not finished. Both `CLAUDE.md` files already treat these as internal on both sides of the Corpus boundary; the same judgement holds against the public.

**Two lookups, on the vocabulary-versus-derived line.** `raw-url-index.csv` (13,426 rows) is the private corpus in index form and is withheld without argument. `rejected-urls.csv` (158 rows of URL, reason and date) is the marginal call: it is corpus-derived, so it falls on the withheld side of the stated rule, but it is also the single best evidence that the scope rule is applied rather than merely written down. **Withheld, and this is the one line in the manifest most worth overruling.**

**Machine configuration and state.** `SyncSettings.ffs_*`, `cycle-manifest.json`, `.env`. Already gitignored and therefore already outside the export: `my-notes/`, `scratchpad/`, `.obsidian/`.

### One thing the manifest deliberately does not do

**It does not rewrite paths.** The published files will say `C:\CORPUS`, `X:\new-queue\`, `C:\Users\bill\OSINT`. That is honest — this is one half of a two-repository system driven from one machine, and a mirror that scrubbed the evidence of that would be describing a system that does not exist. A reader who wants to run any of it will have to supply their own paths, and the README says so.

## The safety gate

The allowlist is the first gate and does the real work. A second gate catches the realistic accident, which is not a stray folder but a procedure file that illustrates itself with a real source body:

**Before each push, the export scans every file it is about to publish for a block quote longer than 200 characters and fails if it finds one.** A hit is not automatically a leak — it may be a quoted rule — so the script refuses and asks, rather than filtering. Today the process layer has exactly one such file (`documentation/osint-no-request-feed.md`), which wants reading once before the first export and then never again.

There are no credentials in the published set. One key exists, `IATI_API_KEY`, and it lives in `.env`, which is gitignored and therefore unreachable by an allowlist that never names it. Nine scripts read environment variables and all nine are benign (`TESSERACT_EXE`, `TESSDATA_PREFIX`, `COMPILE_ASOF`, `CLAUDE_CODE_SESSION_ID`).

## Mechanics

The export copies the manifest into a checkout of the public repository, commits with a subject naming the OSINT commit it came from, and pushes. It writes `PROCESS-FROM` at the mirror root holding that SHA and the export date, on the model of Corpus's `DATATABLE-FROM` and `MAIN-CSS-FROM`.

History does not come across, and should not. The mirror starts at commit one with a note in its README saying that OSINT's 1,579 commits of prior history are private. Carrying the history over would mean a `git filter-repo` extraction, and the reason not to bother is that the history is dense with paths and filenames from `raw/` — the extracted commits would leak the shape of the private base in exchange for a provenance nobody is asking for.

Staleness is a lint, and it belongs to OSINT: `PROCESS-FROM` naming a commit that is not `HEAD` at a cycle close is a finding. It fails rather than warns, because the mirror's only failure mode is being quietly out of date, and a warning about that is a warning nobody reads.

## Cost and sequencing

The export script, the manifest and the staleness lint are about half a session — roughly 150 lines and a list. Creating the public repository, writing its README and setting the licence is another hour, and the licence is a Bill decision worth making before the first push rather than after, since re-licensing a published repository means chasing consent from nobody but is still a mess. **The process files and scripts want a permissive or CC-BY licence; the recommendation is to decide it and state it in the README before commit one.**

Ongoing cost is zero. The export is triggered, not remembered.

**Against the freeze**, this is a new capability in OSINT's process layer — something missing rather than something wrong — and therefore a feature that waits until 2026-09-28. It is not urgent: nothing is broken, and Corpus's transparency claim is not currently being made in public anywhere that this would falsify. The recommendation is to settle the manifest now, while the reasoning is fresh, and build it on the far side of the freeze.

## What is open

Three things, in descending order of how much they matter:

1. **The licence.** Decide before the first push.
2. **`rejected-urls.csv`** — withheld by the stated rule, arguably the best transparency artefact in the repository. Overrule if you want it in.
3. **Whether the mirror is announced.** A public repository nobody links to is transparency in the technical sense only. If Corpus's site is to point at it, that is a Corpus change and a separate piece of work.

When you want this actioned, it goes to OSINT as a numbered note in `C:\corpus-osint-xfer\notes-for-osint.md`, tagged `[ACT]`, with this file named as the specification.
