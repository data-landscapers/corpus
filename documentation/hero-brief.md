---
type: brief
reader: cc
---

# Hero brief

The brief `catalogue_hero` writers are given (strategic review 4, R28 and R30; `scripts/hero-batch.py` prepares their input and checks their output). The contract is OSINT's, from `wiki/schemas.md` §4; this restates it for an agent that cannot read the vault.

## The task

Each input line is one catalogue record: `slug`, `title`, `publisher`, `published`, `places`, and `text`, which is the record's own summary note (`from: note`) or the opening of its verbatim body (`from: body`). Write one subtitle per record and output one JSON line per record, `{"slug": "...", "hero": "..."}`, in input order, nothing else.

## The contract

- **At most 120 characters, English, one line.** Hard cap. Count.
- **Terse grammar.** A subtitle, not a sentence: drop articles and copulas, no terminal full stop. A semicolon, dash or comma series fits two facts.
- **Complements the title, never repeats it** — the hero must not contain the title's words in order, even as an opening clause; OSINT refuses one that does. Nor may it open on the title's first four words: start on what the title does not say. The title says what the thing is called; the hero says what the reader gets by opening it: the figure, the date, the named party, the consequence.
- **Plain text.** No bold, no `[[links]]`, no citations, no markdown.
- **Only what the text says.** Every figure, name and date must be in `text`. Never add a fact from general knowledge, never compute a figure from others (sums, compounded rates), and never make one more precise than the text ("$330bn" stays "$330bn"). The same holds for "first", "only", "just", "largest", "most" — including an editorial "only 15%" the text does not frame that way: use one only where the text says it, of the same subject (the text's "Sub-Saharan Africa's third-largest" is not "Africa's"). Where the text is thin, a shorter hero that says less is right; a guessed one is a defect.
- **About the document, never about the record.** A `note` often mixes a summary with the vault's handling: how it was captured, stubs, duplicates, replacements, `cite_through`, date sources. A hero uses the summary only. "Stub", "captured", "held elsewhere" in a hero is a defect (R28 sample: 1 of 200).
- **English even when the source is not**, with names kept as the source writes them.
- **Every record gets one.** A directory page, an undated reference page, a dataset landing page still has something a reader gets: say what it lists or covers.

## Examples of the house register

- `COSTECH's four-year Tanzania Ventures Lab targets 1,000 startups across six sectors by 2029`
- `REA signs TZS 1.2 trillion contracts to electrify 9,009 hamlets across 25 regions`
- `Q1 2026 sector data — 111.9m mobile lines, 58.9m internet users, 42.5% smartphone penetration`
- `Operators must file an identification form for a public compliance register; no deadline date given`
- `Sierra Leone's permit portal makes an NCRA-issued NIN the gate to online government service`
