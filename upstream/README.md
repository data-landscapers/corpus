# upstream/

A 1:1 mirror of Corpus's own `outputs/`. **Nothing here is authored, and nothing here is the original.**

Since the 2026-08-13 migration this is no longer pulled from OSINT: Corpus authors `outputs/` itself (BUILD.md) and RENDER.md Step 1 mirrors it here, because the renderers still read from this path. `BUILT-FROM` records the Corpus commit the mirror was taken at.

The mirror replaces this folder wholesale, so an edit made here is overwritten without warning at the next render. This file survives only because Step 1 excludes it by name (`/XF README.md`); it is the one hand-maintained thing in the folder, which is the cost of the folder having a notice at all.

See `documentation/design.md` §8 for the reasoning and `documentation/migration-report-layer.md` for what replaced it. When the durable repoint lands — renderers reading `outputs/` directly — this whole folder goes.
