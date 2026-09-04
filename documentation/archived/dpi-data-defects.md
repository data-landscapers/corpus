---
type: doc
title: Known defects in prep/africa-dpi-data.csv
last_reviewed: 2026-09-04
---

# Known defects in `prep/africa-dpi-data.csv`

*(**Moved here from the OSINT notes queue on 2026-08-20**, where it had been sitting as note 11 and part of note 15 since 2026-08-15. It was never OSINT's: `prep/africa-dpi-data.csv` is a **Corpus** file holding a third-party dataset, OSINT keeps no copy, and there was nothing there to repair. Recording it here is what the misfiling should have been from the start — `STATUS-INIT` reads this file on every country, so the defects want stating where the next run will meet them.)*

**This is not a defect list to fix, with one exception that proves the rule.** The data is a third party's and Corpus does not correct it; a correction would be an unsourced claim wearing a dataset's authority. The exception is the **mojibake** below, which is not a claim at all but the third party's own bytes decoded wrongly, and is therefore repaired rather than described. What this file does is tell a `STATUS-INIT` run what it is looking at, so a run neither trusts a bad cell nor spends a second country rediscovering the same fault. Confirmed across **eleven countries** — NGA, SEN, TZA, CIV, MAR, EGY, SWZ and one more, then BDI, MDG and GNB on 2026-09-04 — which is what makes them structural rather than incidental. The `govtech-*` family returned exactly **one** usable fact on each of those last three, from 149 rows apiece.

## The `govtech-*` family — 149 rows a country, one URL

**Every `govtech-*` row resolves to the GTMI 2025 update landing page**, not to anything country-specific, and the `Comments` column repeats the same boilerplate — *"Selected data from the World Bank GovTech Maturity Index &lt;row-id&gt;"* — rather than reasoning about the country. That is a third of the dataset's rows for a country yielding facts that can be linked only to a page which does not itself state them. In CIV's cut the boilerplate is misspelled in the source as *"GovTech Matutiy Index"*.

Under `STATUS-INIT`'s check A — every link is held and resolves — and check B — every claim is linked — a `govtech-*` value can be used only where the run is content to cite the landing page for a fact the landing page does not carry. **The standing treatment is not to.**

### Three cell-level defects beneath it

- **Concatenated answers.** A cell holds two or three mutually exclusive answers run together into one value, most often *"Yes (via separate interfaces) Yes (via Government Service Bus)"*. Recurring ids: `customs-8.8`, `debt-14.6`, `procure-12.6`, `financial-5.13`, `hr-9.7`, `taxmanage-7.7`, `socialinsure-11.9`, `taxportal-20.2`, `taxportal-20.3` (three answers), `startup-48.5`. Counts run four to eight cells a country.
- **Repeated ids carrying conflicting values.** A single sub-indicator id appears on several rows with different answers, with nothing in the row to say which is the country's reading. Recurring: `govtech-socialinsure-11.1`, `govtech-skills-45.5`, `govtech-publicinnov-46.4`, `govtech-publicinnov-47.5`.
- **Outright self-contradiction.** On MAR, `govtech-skills-45.5` and `govtech-publicinnov-46.4` each appear as both *"Yes"* and *"No"* inside the one country's cut. Both were marked borderline and neither reached `MAR-status.md`, which is the correct outcome: `STATUS-INIT` → *When the evidence is borderline* rules that a source which merely disagrees with itself settles nothing.

**The same six ids have now recurred on five countries**, so a run meeting them should recognise rather than re-investigate them.

## The sourceless negatives — and several of them are false

*(Found on the MAR run, 2026-08-15; the third finding of what was note 15.)*

**Thirty-eight of Morocco's 462 rows carry an empty `Source urls`, and 24 of those state a flat "No"** — all in the `reg-*` families. Those 24 are exactly the absences a baseline most wants to state: no data-protection law, no digital-ID law, no right-to-information instrument, no cloud or CIIP framework, no payments law, no fintech sandbox or open banking, no e-government or open-data policy, no AI strategy, no broadband, spectrum or infrastructure-sharing instrument. None could reach `MAR-status.md`, because a claim with no link fails check B.

**What makes this worse than a gap is that the wiki contradicts several of them outright.** `reg-id-dplaw` reads "No" against **loi 09-08 of 2009**, which the base holds and the report itself cites; `reg-egov-strategy` reads "No" against **Digital Morocco 2030**; `reg-connect-spectrum` reads "No" against the **ANRT 5G spectrum tender of July 2025**.

**So a sourceless negative in this dataset is not evidence of absence and must never be read as one.** Nothing in the cut distinguishes the true absences from the false ones, and a false negative that reaches a baseline is a published statement that a country has no data-protection law when it has had one since 2009. Where the dataset is the only thing saying a country lacks an instrument, the finding is ***Not held***, with a `gaps.csv` line — not an absence.

## A cited source can be a dead one, and nothing in the row says so

*(Found through OSINT's `notes-for-corpus` note 6, 2026-08-21.)*

**Two CAF rows cite `arcep.cf` for Law No. 24.001, and that host serves nothing** — 404 on both
`arcep.cf` and `www.arcep.cf` when OSINT tested it on 2026-08-20. The rows are
`id-governance-dpaexists`, whose only source is the dead PDF, and `pay-governance-dataprivacylaw`,
which carries it second behind a review that does resolve.

**This is a different fault from the two above and worse in one specific way.** The concatenated
answers and the sourceless negatives are both visible in the cut: a run can see the run-together
value, and it can see the empty `Source urls`. A sourced row whose source is dead reads exactly
like a sourced row whose source is live, so the dataset's own most reliable third — the rows that
carry a URL — contains an unknown number of citations that go nowhere, and nothing in the file
distinguishes them.

**Nothing here fetches, so no check on this side can find the rest of them.** Check A is set
membership against the catalogue and check G is resolution through it; both are satisfied by a URL
that exists as a string. The rule that follows is about drafting rather than checking: **where a
dataset row is the only thing carrying a claim and its source is a primary document the base has
never held, prefer a secondary the base does hold, and say in the sentence that it is a secondary
reading.** `CAF-status.md`'s data-protection section was rewritten to that shape on 2026-08-21
after it had published the provisions of a law from a link that serves nothing.

**A live 404 dates the absence, not the document** *(OSINT's `ACQUIRE.md`, carried here 2026-08-21)*.
ARCEP published a full regulatory corpus — six laws, three arretes, a decision and the licensing
forms — and then replaced its site with a construction page; the Internet Archive's 2026-06-22
capture holds the tree. So the right conclusion from a dead regulator URL is that the document is
unfetched, never that it was not published, and any status line concluding that a source publishes
nothing should be read against that.

## The mojibake — 92 sequences, repaired, and the one defect here that *was* Corpus's to fix

*(Raised as OSINT's `notes-for-corpus.md` note 7, 2026-08-22, extending its note 4; repaired the same day.)*

**64 rows across 25 countries carried UTF-8 that had been read once as cp1252, every one of them in `Comments`** — `RÃ©fÃ©rentiel GÃ©nÃ©ral`, `Centre Interbancaire de MonÃ©tique`, `sensitive dataâ€”such as child protection`, `Portail National des services publics du BÃ©nin`. 92 mangled sequences in all, 18 distinct, over AGO BEN BFA CAF CIV CMR COG COM CPV GMB GNQ LSO MAR MLI MOZ MRT SEN SLE SOM TCD TGO TUN UGA ZMB ZWE. OSINT's archived copy of the same dataset carried the same fault at 85 rows and 29 countries, so **the mangle is upstream of both copies** and nothing here says which was damaged first or by what.

**This one is repaired, and the rule at the top of this file is not bent by that.** A `govtech-*` boilerplate cell or a sourceless negative is the third party's *claim*, and correcting a claim would be an unsourced assertion wearing a dataset's authority. Mojibake is not a claim — it is the third party's own bytes, decoded wrongly, and the inverse is exact: encode the run back to the bytes it came from and read them as the UTF-8 they always were. Repairing it restores what the source published rather than substituting Corpus's judgment for it, which is why it is the one defect on this page that is fixed rather than described.

**Why it was worth doing rather than noting.** `Comments` is the column `STATUS-INIT` reads and quotes, so a mangled cell reaches a status baseline as a mangled quote — and, before that, **silently fails every grep for the word it mangled**. A row about `África Austral` goes missing from a search for `África Austral` and nothing reports a miss. A defect that hides itself from the check looking for it does not stay on a list.

**Nothing published carried it.** `site/`, `outputs/` and `documentation/` were scanned and are clean — 2,399 files — so no edition states a mangled quote and no re-render is owed. `prep/scope/` did carry it, 166 sequences over 44 per-country cuts, because those are row filters of this file; they were repaired with the same transformation a regeneration would have applied.

**A check now runs, because it will arrive again.** `scripts/lint-mojibake.py` scans `prep/**/*.csv` and `lookups/*.csv`, reports `outputs/` under `--derived`, and repairs under `--fix`:

```bash
python scripts/lint-mojibake.py                # 0 clean · 1 found · 2 unreadable
python scripts/lint-mojibake.py --fix          # repair the inputs in place
```

Two things in it are worth knowing before trusting it. **A run of one character is never touched** — a lone `é` is a letter, and the signature is two or more adjacent high characters that decode as valid UTF-8 *together*; that test is what let it repair 92 sequences in this file while leaving 3,420 correct accented characters and 36 legitimate Portuguese `çã`/`çõ` pairs alone. And **cp1252's five undefined bytes** (`0x81 0x8D 0x8F 0x90 0x9D`) are read back through a latin-1 fallback, without which a strict encoder skips any run containing one and five accented characters survive the repair looking clean — the hole that had been sitting in OSINT's own guard until 2026-08-20. A `.pre-mojibake` copy is written beside any input it rewrites, because `prep/` is gitignored and there is no history to fall back on.

## A cited source can be for a *different country*, and only the URL says so

*(Found 2026-09-04 on the GNB run, the first time this class has appeared.)*

`ict-innovation-gii` for **Guinea-Bissau** carries WIPO's Global Innovation Index country page for **Guinea** — `gii-ranking/2025/gn.pdf`. `gn` is Guinea; Guinea-Bissau is `gw`. The row is otherwise well formed: it has a value, a year and a live URL from an authoritative publisher, and every check short of opening the PDF and reading whose country it is passes.

**This is worse than a dead link, because a dead link announces itself.** A mis-attributed live source produces a fact that is true of somewhere else, correctly formatted, correctly linked, and undetectable by any of `status-check.py`'s tests — check A asks whether the URL is *held*, not whether it is *about this country*. The extraction agent caught it only because it read the URL rather than the value.

**The rule it implies, for `iiag-*`, `gii-*` and any other index row whose URL encodes a country code**: read the country code in the URL against the country being written, and drop the row where they disagree. Do not repair the URL to the right country's page — that would be substituting a source the dataset does not cite, which is a fabrication however plausible.

Two countries in this dataset are especially exposed to this because their short names collide: **Guinea (GIN)**, **Guinea-Bissau (GNB)** and **Equatorial Guinea (GNQ)**, the last of which is still to be run. **Congo (COG)** and **DR Congo (COD)** are the other pair worth checking.

## What this costs, and why the dataset is still used

The `govtech-*` third is largely unusable and the sourceless negatives are unusable in the direction that matters most. What remains — the `iiag-*`, `odin-*`, `stats-*`, `rural-*` families and the sourced `reg-*` rows — carries real, citable, country-specific evidence, and `STATUS-INIT` stage 0's three-agent split (`STATUS-INIT.md` step 5) already partitions the families so a run reads each once. The dataset earns its place on the sourced rows; this file exists so that the rest is skipped knowingly rather than trusted by default.
