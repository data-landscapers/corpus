---
description: Write or strike the block the poll found owed — opened by scripts/poll-loop.py
argument-hint: "deploy | deploy-cleared | critical"
---

`scripts/poll-loop.py` opened this session for `$ARGUMENTS`. The line it read is in
`%TEMP%\corpus-poll-alert.txt`; read it first. Re-read `C:\corpus-osint-xfer\messages-for-bill.md`
before editing it, and keep to its form.

- **deploy** — write one `· deploy` block quoting the line, replacing any older `· deploy`
  block; commit and push the share; send the line with the `PushNotification` tool.
- **deploy-cleared** — delete the open `· deploy` block; commit and push the share.
- **critical** — the trigger cannot judge, and the poll has stopped. Write one block quoting
  the message, commit and push the share, and send it with `PushNotification`. Do not run a
  cycle and do not restart the poll.

Stage only `messages-for-bill.md` in the share. End on the output of
`python scripts/corpus-status.py`. Bill closes the tab.
