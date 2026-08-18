---
type: pointer
title: download-log — see documentation/cloudflare.md
last_reviewed: 2026-08-18
---

# download-log

**`worker.js` beside this file is deployed to Cloudflare as the Worker `download-log`, on the route `corpus.data-landscapers.io/*`.** It notes the path of every `.pdf` and `.csv` a reader takes, writes it to the KV namespace `downloads`, and passes the request through untouched.

**Everything about it is in `documentation/cloudflare.md`** — the binding, the key and value, the route, the API token, and what Corpus does with the record. This file is a pointer so that the code does not sit in a directory with nothing next to it; the reference is the thing to keep current.

**The deployment account of 2026-08-18**, including the dashboard screens as they were that afternoon and the `wrangler.jsonc` fallback for the binding, is in `documentation/archived/download-log-worker.md`.
