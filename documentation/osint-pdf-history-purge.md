---
type: doc
title: Purge the PDFs from OSINT's git history
status: not started — written 2026-08-16, for one OSINT session
last_reviewed: 2026-08-16
---

# Purge the PDFs from OSINT's git history

*(Written from CORPUS, for OSINT. **Self-contained** — it assumes nothing read first and names no path outside OSINT. One line per paragraph, OSINT house style.)*

*(Answers `notes-for-osint.md` note 1, open since 2026-08-06. Note 1 said the tracked PDFs in `raw/` are the weight and that removing them from the tree would not recover the space, because history retains the blobs. This is the operation that does recover it.)*

## The state, measured 2026-08-16

`.git` is **5.1 GB** and the working tree **8.1 GB**, against GitHub's soft 5 GB ceiling — so the ceiling is crossed, not approached.

**760 PDFs are tracked**: 745 under `raw/`, 15 under `new-budget/`. In the `raw/` working tree there are 747 PDFs totalling **2.61 GB**, against about 74 MB for all 9,407 markdown records. The largest single file is 64 MB.

So the PDFs are essentially the whole of the repository's weight, and the markdown — the part that is actually edited, diffed and reviewed — is a rounding error beside them.

## What this asks you to decide

**PDFs stop being version-controlled and become backed-up binary artefacts.**

That is the whole of the decision, and it is worth stating plainly because it changes what git guarantees about them. A PDF is never edited after capture: it has no diff, no merge, no history worth reading. Version control buys nothing for it and costs 2.61 GB. What a PDF does need is a backup, and the mirror already provides one.

**A new repository is not needed and is the worse option.** It would discard the markdown history, which is the part with value. `git filter-repo` rewrites the existing history in place and keeps everything else.

**Nothing outside OSINT breaks.** This was checked before the document was written: no CORPUS script reads OSINT's committed `HEAD`, every CORPUS read goes through the working tree, and nothing CORPUS publishes cites an OSINT commit SHA. A rewrite invalidates no published citation. Slug permanence is untouched — this operation moves files and rewrites commits, and mints, retires or reissues no slug.

## Do it in this order

The order is the safety property. Moving the files out first means that if the rewrite is abandoned halfway, the PDFs are already safe outside the repo and nothing is lost.

**P1 — Take a bundle first, and check it.**

```bash
git bundle create ../osint-pre-purge.bundle --all
git bundle verify ../osint-pre-purge.bundle
```

This is the rollback. It is a single file holding the entire history as it stands, and it is the only thing that can undo P3. Keep it until P5 has passed and you are satisfied.

**P2 — Move the PDFs out of the tree, and junction the store back in.**

This is the pattern `budget-archive/` already uses, so it is a known shape here rather than a new one. Move the PDF store to a sibling directory outside the repository, then junction it back so every existing path still resolves and nothing that reads `raw/` has to change.

Do it with git's own listing rather than a hand-built loop — the filenames carry spaces, en-dashes and other non-ASCII, and a naive `for` loop over `ls` will mangle them:

```bash
git ls-files -z '*.pdf' '*.PDF' | xargs -0 -I{} echo {}
```

Confirm that list is 760 lines and is what you expect before moving anything.

**P3 — Rewrite the history.**

```bash
pip install git-filter-repo
git filter-repo --path-glob '*.pdf' --path-glob '*.PDF' --invert-paths
```

`--invert-paths` means *remove these paths* rather than keep only them. `--path-glob` matches at any depth, so it takes `raw/` and `new-budget/` together.

Two things it does that surprise people, both deliberate: it **removes the `origin` remote**, so that a force-push cannot be a reflex, and it refuses to run on a repository with uncommitted changes. Commit or stash first, and re-add the remote in P4.

It repacks as it goes, so no separate `git gc` is needed.

**P4 — Push the rewritten history.**

```bash
git remote add origin <the OSINT remote URL>
git push --force --all
git push --force --tags
```

**Every commit SHA from the first PDF commit onward is different.** Any other clone of this repository must be deleted and re-cloned — pulling into an old clone will merge the two histories back together and undo the whole operation.

**P5 — Verify.**

```bash
du -sh .git
git ls-files '*.pdf' '*.PDF' | wc -l
```

Expect `.git` around 2.4–2.6 GB and a count of **0**. Then confirm the working tree still resolves: a sample of the moved PDFs should open through their original `raw/` paths via the junction.

Add `*.pdf` to `.gitignore` last, once the count is 0, so that a later capture does not quietly put the weight back.

## What is lost, and what is not

**Lost:** the ability to recover a PDF from git history. From here a PDF exists in the working tree and in the mirror, and nowhere else.

**Not lost:** the records themselves. Every markdown record in `raw/` stays tracked and committed, including the frontmatter, the body and the `url:` that makes the source citable. The standing requirement that `raw/`, `lookups/` and `wiki/` stay git-tracked is about those records, and it is unaffected — what leaves is the attached binary, not the evidence.

**The consequence to be deliberate about:** the mirror becomes the only protection for 2.61 GB of documents. That is an argument for running the mirror on a known cadence after this, not an argument against doing it.

## Timing

Not while a session is mid-flight between `new/` and `raw/` — the rewrite must run on a settled tree with nothing uncommitted.
