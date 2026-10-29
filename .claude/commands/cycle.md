---
description: Run a sweep cycle the poll has claimed — opened by scripts/poll-loop.py
---

`scripts/poll-loop.py` opened this session because `python scripts/osint-cycle-ready.py --claim`
exited 0: a sweep cycle has closed and the claim is already taken. Do not claim again.

From C:\CORPUS, run `CYCLE.md` end to end — every step of *The run*, in its order, passing
`--poll` to `python scripts/unit-review.py next` — following its unattended rules: never stop
to ask, leave anything needing Bill in `C:\corpus-osint-xfer\messages-for-bill.md`. Finish
with `python scripts/osint-cycle-ready.py --done`.

Then work the oldest open job in `C:\corpus-osint-xfer\corpus-housekeeping.md`, if there is
one, once. Then, alone, run `CYCLE.md` step 8 (Research's index build) — skipped until now so
it runs last.

Before standing down, check `C:\corpus-osint-xfer` for uncommitted work, commit it naming
OSINT in the subject if the work is OSINT's, and push immediately. End on the output of
`python scripts/corpus-status.py`. Bill closes the tab.
