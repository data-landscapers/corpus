---
type: pointer
title: download-log — see documentation/cloudflare.md
last_reviewed: 2026-08-18
---

# download-log

**`worker.js` beside this file is deployed to Cloudflare as the Worker `download-log`, on the route `corpus.data-landscapers.io/*`.** It does two jobs: it serves the dated editions out of R2, and it notes the path of every `.pdf` and `.csv` a reader takes into the KV namespace `downloads`.

**Two bindings, and the names are load-bearing.** `DOWNLOADS` → KV namespace `downloads`; `EDITIONS` → R2 bucket `editions`. The code reads `env.DOWNLOADS` and `env.EDITIONS` and does nothing at all if either is absent — no logging, or no R2 and a fall-through to GitHub Pages — so a mistyped binding name fails silently and safely rather than breaking a download.

**Everything about the logging half is in `documentation/cloudflare.md`** — the key and value, the route, the API token, and what Corpus does with the record. **Everything about the serving half is in `documentation/editions-serving-shape.md`** — what moves, the migration order, and why a Worker that used to be out of the serving path is now in it. This file is a pointer so that the code does not sit in a directory with nothing next to it; the two references are the things to keep current.

**The deployment account of 2026-08-18**, including the dashboard screens as they were that afternoon and the `wrangler.jsonc` fallback for the binding, is in `documentation/archived/download-log-worker.md`.
