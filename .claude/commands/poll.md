---
description: Watch for a closed sweep cycle and run CYCLE.md when one lands
argument-hint: "[interval, default 30m]"
---

Arm the sweep-cycle poll for this session. `$ARGUMENTS` is the interval if one was given,
otherwise use `30m`.

Do these three things and nothing else — no exploring the repo, no reading the runbooks,
no work of your own. This command exists to be typed into a clean session and answered in
one turn.

1. **Report the state in three lines**: the output of `python scripts/osint-cycle-ready.py`
   and of `python scripts/osint-cycle-ready.py --status`, and — if the trigger reads ready —
   say plainly that arming will start a full BUILD+RENDER now, so Bill can stop you.
2. **Arm the loop.** Invoke the `loop` skill with the interval, then this prompt verbatim:

   > Run `python scripts/osint-cycle-ready.py --claim` from C:\CORPUS. On exit 1, stop the
   > turn and say nothing further. On exit 2, write one block in `logs/messages-for-bill.md`
   > quoting the message, then stop the loop. On exit 0, run `CYCLE.md` end to end — BUILD.md
   > whole, then RENDER.md Step 0 and its checks, then RENDER Steps 1-7, Log and Mirror —
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
