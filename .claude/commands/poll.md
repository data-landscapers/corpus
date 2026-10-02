---
description: Watch for a closed sweep cycle and run CYCLE.md when one lands
argument-hint: "[interval, default 30m]"
---

Arm the sweep-cycle poll for this session. `$ARGUMENTS` is the interval if one was given,
otherwise use `30m`.

Do these three things and nothing else — no exploring the repo, no reading the runbooks,
no work of your own. This command exists to be typed into a clean session and answered in
one turn.

1. **Report the state in four lines**: the output of `python scripts/osint-cycle-ready.py`,
   of `python scripts/osint-cycle-ready.py --status` and of `python scripts/deploy-state.py`,
   and — if the trigger reads ready — say plainly that arming will start a full BUILD+RENDER
   now, so Bill can stop you.
2. **Arm the loop.** Invoke the `loop` skill with the interval, then this prompt verbatim:

   > From C:\CORPUS, first run `python scripts/deploy-state.py --fix --quiet`. On exit 2,
   > unless `logs/messages-for-bill.md` already holds a `· deploy` block quoting the same
   > line: write that block (it is exempt from the five-block cap; replace an older one),
   > commit and push it, and send the line with the `PushNotification` tool. On exit 0,
   > delete a `· deploy` block if one is open, commit and push. On exit 1 or 3 do nothing.
   > Then run `python scripts/osint-cycle-ready.py --claim`. On exit 1, stop the
   > turn and say nothing further. On exit 2, write one block in `logs/messages-for-bill.md`
   > quoting the message, then stop the loop. On exit 0, run `CYCLE.md` end to end — drain any
   > open notes in `C:\corpus-osint-xfer\notes-for-corpus.md` first, then BUILD.md whole, then
   > UNIT-REVIEW.md for each unit `python scripts/unit-review.py next --poll` names, then
   > RENDER.md Step 0 and its checks, then RENDER Steps 1-7, Log and Mirror —
   > following its unattended rules: never stop to ask, leave anything needing Bill in
   > `logs/messages-for-bill.md`. Finish with `python scripts/osint-cycle-ready.py --done`.
   > Before standing down, check `C:\corpus-osint-xfer` for uncommitted work, commit it
   > naming OSINT in the subject if the work is OSINT's, and push immediately.

3. **Say what would kill it**: the job is session-only, so a reboot or closing the window
   ends it — and that a lost poller costs a delay and not a night, because the watermark is
   not advanced and the close is still waiting when a session next polls.

**What the trigger is and why it reads a closed row rather than a timestamp** is
`CYCLE.md` -> *What starts a cycle*, and the reasoning is in the head of
`scripts/osint-cycle-ready.py`. Read either only if something looks wrong; this command
does not need them to do its job.
