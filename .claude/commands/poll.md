---
description: Say whether the automatic poll is running; it is never armed by hand
---

**The poll is automatic** *(Bill, 2026-10-29)*: `scripts/poll-loop.py` runs in the
`CORPUS-POLL` terminal tab, which starts it, every 30 minutes from 22:00 to 06:00. It opens
`/cycle` or `/poll-alert` in a new tab when there is work. Never arm a `/loop` or a cron for it.

Do one thing: say in one line whether a `python … poll-loop.py` process is running, and if
it is not, that Bill starts it by opening the `CORPUS-POLL` tab (`scripts\batches\corpus-poll.bat`).
