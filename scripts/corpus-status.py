#!/usr/bin/env python3
"""corpus-status.py — what is outstanding, on one line, at the end of every job.

Modelled on OSINT's `STATUS.md` *(Bill, 2026-10-23)*: two nights went unbuilt because a hold
spoke to nobody, and the remedy is a reading that every job ends on, so whatever is waiting
or wedged is in front of Bill each time CC finishes something. It reads Corpus and the share
only; nothing of OSINT's beyond the mirror freshness lint already reads.

**The tally is the queues** — work waiting to start, each with who clears it:

- **messages**     open blocks in the share's `messages-for-bill.md`. Bill clears.
- **fetch**        unstruck lines in the share's `fetch-list.md`, documents only Bill's browser
                   can get. Bill clears.
- **corpus-notes** open notes in `notes-for-corpus.md`, OSINT's asks of Corpus. Corpus clears.
- **osint-notes**  open notes in `notes-for-osint.md`. OSINT clears.
- **corpus-housekeeping** open jobs in `corpus-housekeeping.md`. A `/poll` cycle works one a night.
- **osint-housekeeping** open jobs in the share's `osint-housekeeping.md`. OSINT clears.
- **prepared**     folders in the share's `prepared/`, handovers awaiting OSINT's pull.
- **new-queue**    items in the share's `new-queue/`, awaiting OSINT's ingest.
- **budget**       follow-ups in `logs/budget-followups.md`; most wait on a document or a ruling.
- **held-facts**   `held:` lines across `maturity/*/refused.csv`, facts that would move a stage.
- **prose**        narrative blocks failing the prose sheet on the newest night of `logs/prose.csv`,
                   every unit but the wiki (`lint-prose.py`, R133). The unit-review rotation clears them.
- **commits**      uncommitted paths, Corpus plus share. A job commits what it changed.
- **unpushed**     commits not on origin, Corpus plus share. A job pushes what it commits.

**Gates are the half-finished states** — reported apart from the tally, in prose, because each
one is a reason the next cycle may not run or the site may be stale: a close owed and not yet
claimed, a cycle the trigger cannot judge, `logs/.hold-cycle` up, a build sentinel left
behind, the newest BUILD or RENDER line `errored`, a deploy stuck, the OSINT mirror stale, the
Corpus backup stale. **No gate open is the normal reading.**

It writes the reading to `logs/status.md` (gitignored) as well as printing it, so "display
status" is `cat logs/status.md` without recomputing.

    python scripts/corpus-status.py            # the tally line, then the gates
    python scripts/corpus-status.py --gates    # gates only; prints nothing and exits 0 when none

Exit 0 no gate open, 1 a gate is open.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import io
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SHARE = os.environ.get("CORPUS_OSINT_XFER", r"C:\corpus-osint-xfer")
OUT = os.path.join(ROOT, "logs", "status.md")

# The share README's two note shapes: `### 246. [ACT] …` and the bold lead `**246** [ACT] …`.
# One note carries both, so the heading alone is counted where a file uses headings.
NOTE_HEADING = re.compile(r"^#{2,3} \d+[.\s]", re.M)
NOTE_LEAD = re.compile(r"^\*\*\d+\*\*[ (]", re.M)
JOB = re.compile(r"^## \d+ · ", re.M)
FOLLOWUP = re.compile(r"^- \*\*", re.M)
# An open fetch line or OSINT job is `75. …`; a struck one is `x75. …`.
NUMBERED = re.compile(r"^\d+\. ", re.M)
MARKER = "<!-- newest first: a new block goes directly below this line -->"


def read(path: str) -> str:
    try:
        return io.open(path, encoding="utf-8").read()
    except OSError:
        return ""


def run(*cmd: str, cwd: str = ROOT, timeout: int = 180) -> tuple[int, str]:
    try:
        r = subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return 99, str(exc)


def py(script: str, *args: str) -> tuple[int, str]:
    return run(sys.executable, os.path.join(ROOT, "scripts", script), *args)


def open_notes(name: str) -> int:
    text = read(os.path.join(SHARE, name))
    text = text.split("## Unresolved", 1)[-1]
    return len(NOTE_HEADING.findall(text)) or len(NOTE_LEAD.findall(text))


def messages() -> int:
    text = read(os.path.join(SHARE, "messages-for-bill.md"))
    body = text.split(MARKER, 1)[1] if MARKER in text else ""
    return len(re.findall(r"^## ", body, re.M))


def entries(folder: str) -> int:
    path = os.path.join(SHARE, folder)
    try:
        return len([e for e in os.listdir(path) if not e.startswith(".") and e.lower() != "readme.md"])
    except OSError:
        return 0


def held_facts() -> int:
    n = 0
    for path in glob.glob(os.path.join(ROOT, "maturity", "*", "refused.csv")):
        n += sum(1 for line in read(path).splitlines() if ",held:" in line or line.startswith("held:"))
    return n


def git_count(repo: str, *args: str) -> int:
    code, out = run("git", "-C", repo, *args)
    return len([l for l in out.splitlines() if l.strip()]) if code == 0 else 0


def newest(job: str) -> str:
    for line in read(os.path.join(ROOT, "logs", "log.md")).splitlines():
        if f"· **{job}** ·" in line:
            return line
    return ""


def gates() -> list[str]:
    out = []
    code, line = py("osint-cycle-ready.py")
    line = line.splitlines()[-1] if line else ""
    if code == 0:
        out.append(f"cycle owed and not yet claimed — {line}; the next /poll tick runs it, "
                   "or run CYCLE.md by hand if no poll is armed")
    elif code == 2:
        out.append(f"cycle trigger cannot judge — {line}")
    elif line.startswith("held"):
        out.append(f"cycle {line}")
    if os.path.exists(os.path.join(ROOT, "logs", ".build-in-progress")) and "running" not in line:
        out.append("logs/.build-in-progress is present and no cycle claims it — a build died")
    for job in ("BUILD", "RENDER"):
        last = newest(job)
        if "errored" in last:
            out.append(f"newest {job} line errored — {last[:160]}")
    code, dep = py("deploy-state.py", "--quiet")
    if code == 2:
        out.append(f"deploy stuck — {dep.splitlines()[-1] if dep else ''}")
    code, fr = py("lint-osint-freshness.py")
    if code:
        out.append(f"OSINT mirror {'stale' if code == 1 else 'unreadable'} — "
                   f"{fr.splitlines()[0] if fr else ''}")
    code, mf = py("lint-mirror-freshness.py")
    if code:
        out.append(f"Corpus backup {'stale' if code == 1 else 'never recorded'} — "
                   f"{mf.splitlines()[0] if mf else ''}")
    return out


def prose() -> int:
    """Failing blocks on `prose.csv`'s newest night, the wiki apart; 0 before its first night."""
    rows = list(csv.DictReader(io.StringIO(read(os.path.join(ROOT, "logs", "prose.csv")))))
    last = max((r["date"] for r in rows), default=None)
    return sum(int(r["failing"]) for r in rows if r["date"] == last and r["unit"] != "wiki")


def tally() -> str:
    counts = [
        ("messages", messages()),
        ("fetch", len(NUMBERED.findall(read(os.path.join(SHARE, "fetch-list.md"))))),
        ("corpus-notes", open_notes("notes-for-corpus.md")),
        ("osint-notes", open_notes("notes-for-osint.md")),
        ("corpus-housekeeping", len(JOB.findall(read(os.path.join(SHARE, "corpus-housekeeping.md"))))),
        ("osint-housekeeping", len(NUMBERED.findall(
            read(os.path.join(SHARE, "osint-housekeeping.md")).split("## Jobs", 1)[-1]))),
        ("prepared", entries("prepared")),
        ("new-queue", entries("new-queue")),
        ("budget", len(FOLLOWUP.findall(read(os.path.join(ROOT, "logs", "budget-followups.md"))))),
        ("held-facts", held_facts()),
        ("prose", prose()),
        ("commits", git_count(ROOT, "status", "--porcelain") + git_count(SHARE, "status", "--porcelain")),
        ("unpushed", git_count(ROOT, "log", "--oneline", "@{u}..") + git_count(SHARE, "log", "--oneline", "@{u}..")),
    ]
    return " ; ".join(f"{k} - {v}" for k, v in counts)


def main() -> int:
    ap = argparse.ArgumentParser(description="What is outstanding, on one line.")
    ap.add_argument("--gates", action="store_true", help="gates only; silent when none is open")
    args = ap.parse_args()

    open_gates = gates()
    lines = [] if args.gates else [tally()]
    if open_gates:
        lines += [f"gate: {g}" for g in open_gates]
    elif not args.gates:
        lines.append("gates: none open")

    if not args.gates:
        stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        io.open(OUT, "w", encoding="utf-8", newline="\n").write(
            f"# Corpus status, {stamp}\n\n" + "\n".join(lines) + "\n")
    if lines:
        print("\n".join(lines))
    return 1 if open_gates else 0


if __name__ == "__main__":
    sys.exit(main())
