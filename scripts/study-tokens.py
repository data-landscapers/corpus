#!/usr/bin/env python3
r"""study-tokens.py — what a session spent, counted from its transcripts.

    python scripts/study-tokens.py                       # the newest session
    python scripts/study-tokens.py 565a5703              # one session, by the start of its id
    python scripts/study-tokens.py 565a5703 1683ae4b     # several, summed
    python scripts/study-tokens.py --total               # the newest session's total in millions, alone

`maturity/documentation/maturity-study-method.md` §0. **A study is sized by the week's quota
it consumes** *(Bill, 2026-10-11)*, and the only record of that is the transcript Claude Code
keeps: `~/.claude/projects/{project}/{session}.jsonl` for the thread and
`{session}/subagents/**/agent-*.jsonl` for every agent it started, a workflow's included.

**Every token a request carried is counted**: fresh input, cache writes, cache reads and
output. Cache reads are the bulk and are the point: a long thread resends what it has read on
every turn, and that resending is what a study's design can change. A message is counted
once, by its id, because a streamed reply is written to the transcript in several lines that
each repeat its usage.

Prints the thread and the agents apart, and the ten largest agents, since the split is what
says where to cut. Run it at the end of step 3 and of step 5, in the session that did the
work, and put the totals in the step's log line.

Exit: 0 printed, 2 no such session.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")
KINDS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


def project_dir(cwd: str) -> str:
    """Claude Code names a project's folder for its path, every separator a hyphen."""
    return os.path.join(PROJECTS, "".join(c if c.isalnum() else "-" for c in cwd))


def spent(path: str, seen: set[str]) -> dict[str, int]:
    """Tokens by kind over one transcript, each message once across every file read."""
    out = dict.fromkeys(KINDS, 0)
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"usage"' not in line:
                continue
            try:
                msg = json.loads(line).get("message") or {}
            except ValueError:
                continue
            usage, mid = msg.get("usage"), msg.get("id")
            if not isinstance(usage, dict) or not mid or mid in seen:
                continue
            seen.add(mid)
            for k in KINDS:
                out[k] += int(usage.get(k) or 0)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="What a session spent, from its transcripts.")
    ap.add_argument("session", nargs="*", help="the start of a session id; default the newest")
    ap.add_argument("--project", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    help="the project's working directory; default this repository")
    ap.add_argument("--total", action="store_true",
                    help="print the total in millions and nothing else, for a before-and-after difference")
    a = ap.parse_args(argv)

    base = project_dir(a.project)
    threads = sorted(glob.glob(os.path.join(base, "*.jsonl")), key=os.path.getmtime, reverse=True)
    if a.session:
        picked = [t for t in threads if os.path.basename(t).startswith(tuple(a.session))]
    else:
        picked = threads[:1]
    if not picked:
        print(f"study-tokens: no session {' '.join(a.session) or '(any)'} under {base}")
        return 2

    seen: set[str] = set()
    thread, agents, each = dict.fromkeys(KINDS, 0), dict.fromkeys(KINDS, 0), []
    for t in picked:
        for k, v in spent(t, seen).items():
            thread[k] += v
        # a workflow's agents sit a level down, in subagents/workflows/{run}/; its journal is not one
        for sub in glob.glob(os.path.join(t[:-len(".jsonl")], "subagents", "**", "agent-*.jsonl"),
                             recursive=True):
            got = spent(sub, seen)
            each.append((sum(got.values()), os.path.basename(sub)))
            for k, v in got.items():
                agents[k] += v

    def line(label: str, d: dict) -> str:
        return (f"  {label:<8} {sum(d.values()) / 1e6:8.1f}M   fresh {d[KINDS[0]] / 1e6:.1f}M, "
                f"cache written {d[KINDS[1]] / 1e6:.1f}M, cache read {d[KINDS[2]] / 1e6:.1f}M, "
                f"output {d[KINDS[3]] / 1e6:.1f}M")

    total = {k: thread[k] + agents[k] for k in KINDS}
    if a.total:
        print(f"{sum(total.values()) / 1e6:.1f}")
        return 0
    print(f"study-tokens: {len(picked)} session(s), {len(each)} agent(s)")
    print(line("thread", thread))
    print(line("agents", agents))
    print(line("total", total))
    for n, name in sorted(each, reverse=True)[:10]:
        print(f"    {n / 1e6:7.1f}M  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
