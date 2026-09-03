#!/usr/bin/env python3
r"""
filler-batch.py — run PROGRESS-FILLER over a queue of countries, one fresh session each.

    python scripts/filler-batch.py --dry-run
    python scripts/filler-batch.py --until 07:00
    python scripts/filler-batch.py --only COG GAB TCD

**The context guarantee is a process boundary, not a discipline.** Each country is a
separate `claude -p` process, so its context starts at zero and ends with the process;
nothing accumulates across the night and no session has to remember to clear anything.
A driver that ran the countries as turns of one conversation would be carrying twenty
runs' worth of tool output by morning, and would degrade in the way that is hardest to
see from outside — the later runs quietly worse than the earlier ones, with nothing in
the output saying so. Within a country, PROGRESS-FILLER §6's delegation already keeps
bodies out of the parent's context; this driver's job is to not defeat that.

**The order is Bill's, and it is a file** — `prep/progress-filler-queue.md`, one ISO-3 a
line *(Bill, 2026-09-02)*. It is deliberately not the same list as the blank cells in
`logs/progress-report-log.csv`: it selects, it reorders, and it may carry a country that
has already been searched once. So where it exists it is obeyed verbatim, and the CSV
stays what it always was — the record of what has been searched, never the authority on
what to search next. With the file absent, the CSV's blank cells are the fallback queue
(PROGRESS-FILLER, *Where the trigger names no {ISO}*).

**Resuming reads tonight's ledger, not the CSV.** A driver restarted after a crash skips
what it already finished cleanly, and nothing else. Deciding that from the `Filler
Searched` cell instead would look identical until the day the order file names a
deliberate re-probe — and would then silently drop exactly the country that was asked
for. A re-probe is cheap by design: §0's re-run policy returns an unmoved subject as
`skipped-prior-nil` rather than re-buying it.

**Verify files, not answers.** §6 says that of the runs; it is more true of a driver
reading a session's own summary of itself. A run that reports a clean tally and wrote
nothing is the failure this will meet most often, so after each country the driver checks
the queue cell, the run CSV, the files on disk and `lint-staged-queue.py` over what was
staged — and records what it found rather than what it was told.

**Strictly serial, and it takes a lock.** Two of these, or one of these beside an
interactive session, would put two agents on one tree and one share. The lock holds the
pid; a stale one from a killed driver is reported, never cleared automatically, because
two drivers is the expensive mistake and a stale lock is the cheap one.

**What it does not decide.** The cap, the queue order, how much of the week to spend:
§7 puts those with Bill. This stops where it is told — a deadline, a run count, a cost
ceiling, consecutive failures, or a STOP file — and never widens its own remit. Every
stop is recorded with its reason.

Exit: 0 worked to a stopping condition with every run clean, 1 a run had problems,
      2 it could not start (lock held, no queue, no `claude` on PATH).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import signal
import statistics
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
QUEUE = CORPUS / "logs" / "progress-report-log.csv"
# **The order is Bill's, and it is a file rather than an argument** *(Bill, 2026-09-02)*.
# One ISO-3 a line. It is not the same list as the CSV's blank cells and is not meant to
# be: it selects (five pending countries are deliberately not on it) and it reorders, and
# on 2026-09-02 it carried GNB, whose cell was already filled. So where this file exists
# it is obeyed verbatim — the CSV stays the record of what has been searched, never the
# authority on what to search next.
ORDER = CORPUS / "prep" / "progress-filler-queue.md"
RUNS = CORPUS / "logs" / "progress-filler"
BATCH = CORPUS / "logs" / "filler-batch"
LOCK = BATCH / "batch.lock"
STOP = BATCH / "STOP"
QUEUE_COL = "Filler Searched"
ISO_COL = "iso-3"

# The share is outside both repos; `status_lib.EXCHANGE` is the one path that has to
# agree with this, and CORPUS_OSINT_XFER overrides both.
EXCHANGE = Path(os.environ.get("CORPUS_OSINT_XFER", r"C:\corpus-osint-xfer"))

# The prompt names the runbook rather than relying on the trigger phrase: nothing in
# CLAUDE.md maps "run the progress filler for {ISO}" to PROGRESS-FILLER.md, so a session
# left to infer it might read a different procedure, or none.
#
# **The paragraph about not ending the turn is load-bearing** *(COG, 2026-09-02 19:07)*.
# The first run under this driver spawned §6's six slices, ended its turn saying "I'll
# pick up when their completion notifications arrive", and exited. That is the right
# instinct in an interactive session and fatal in `-p`: there is no later turn to be
# notified into, so the process ended and the harness killed all six sub-agents
# (`killed: {system: 6}`). It ran 15 minutes, staged whatever had landed, wrote no run
# CSV, claimed no queue cell — and reported success with `is_error: false`. Nothing but
# the file checks caught it, and it would have repeated on every country.
PROMPT = (
    "Read C:\\CORPUS\\PROGRESS-FILLER.md and run that procedure for {iso}, end to end, "
    "including every finishing step in section 8: lint the staged batch, commit and push "
    "the share, write the note for OSINT, set the {iso} row's '{col}' cell in "
    "logs/progress-report-log.csv to today's date, and write the Corpus log line. "
    "\n\n"
    "YOU ARE IN PRINT MODE, NOT AN INTERACTIVE SESSION. There is no later turn: when you "
    "stop, the process exits and every sub-agent still running is killed on the spot. So "
    "never end your turn with work outstanding, and never say you will pick something up "
    "when a notification arrives — no notification can reach you. After you spawn the "
    "section 6 slices you must keep working until every one of them has returned its "
    "tally: wait on them, and if you are given a task id, poll it. Only then merge, audit "
    "the cap, dedup, lint, and do the section 8 finishing steps. If a slice cannot be "
    "waited on, run the slices one at a time in the foreground instead and accept that it "
    "is slower; a slow country is worth more than a fast one that staged half a batch."
    "\n\n"
    "You are running unattended from a batch driver, so there is nobody to ask: where you "
    "would have asked, take the conservative option and record it. Run {iso} and no other "
    "country. A previous attempt may have left files already staged under "
    "new-queue\\{iso}\\ — section 4's dedup covers that, so top the batch up rather than "
    "restaging what is there. Finish by printing one line: "
    "FILLER {iso} probed=<n> staged=<n> nil=<n>."
)


# ---------------------------------------------------------------------------
# the queue
# ---------------------------------------------------------------------------

def read_queue() -> list[dict]:
    with QUEUE.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def pending(rows: list[dict]) -> list[str]:
    """Countries whose `Filler Searched` cell is still blank, in file order."""
    return [r[ISO_COL].strip() for r in rows
            if r.get(ISO_COL, "").strip() and not (r.get(QUEUE_COL) or "").strip()]


def read_order(path: Path) -> list[str]:
    """Bill's order file: one ISO-3 a line, blanks and `#` comments ignored."""
    out = []
    for ln in path.read_text(encoding="utf-8-sig").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            out.append(ln.split()[0].upper())
    return out


def done_recently(hours: float) -> set[str]:
    """Countries a batch has already finished cleanly inside the resume window.

    Resumability is tracked here rather than against the CSV's `Filler Searched` cell,
    because the order file may legitimately carry a country whose cell is already filled
    — a deliberate re-probe, which §0's re-run policy makes cheap. Reading the cell to
    decide what to skip would silently drop exactly that country.

    **It reads every recent ledger, not today's.** The ledger is named for the date, and
    an overnight batch crosses one: a driver relaunched at 01:00 would open a new file,
    find it empty, and re-run every country the evening had already done. That failure is
    invisible in the output — the re-runs look like ordinary work."""
    cutoff = time.time() - hours * 3600
    out: set[str] = set()
    for led in BATCH.glob("*-batch.csv"):
        if led.stat().st_mtime < cutoff:
            continue
        with led.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("verdict") == "ok":
                    out.add(r["iso"])
    return out


def claimed(iso: str) -> str:
    """Whatever the queue now holds for this country — empty if still blank."""
    for r in read_queue():
        if r.get(ISO_COL, "").strip() == iso:
            return (r.get(QUEUE_COL) or "").strip()
    return ""


# ---------------------------------------------------------------------------
# what a finished run left behind
# ---------------------------------------------------------------------------

def run_csv(iso: str, since: float) -> Path | None:
    """The run CSV this run wrote, if it wrote one.

    Matched on mtime rather than on today's date: a run that starts at 23:50 names its
    file for yesterday, and a driver that looked for today's would call it missing."""
    cands = [p for p in RUNS.glob(f"{iso}-*.csv")
             if not p.name.endswith(("-selected.csv", "-unselected.csv", "-misfiled.csv"))
             and p.stat().st_mtime >= since - 60]
    return max(cands, key=lambda p: p.stat().st_mtime) if cands else None


def tally(path: Path) -> dict:
    """§7's run CSV, summed. The cap is auditable from this file alone, which is why the
    driver reads it rather than the session's account of it."""
    out = {"probed": 0, "baseline": 0, "progress": 0, "nil": 0, "skipped": 0, "staged": 0}
    try:
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                out["probed"] += 1
                out["baseline"] += int((r.get("staged_baseline") or 0) or 0)
                out["progress"] += int((r.get("staged_progress") or 0) or 0)
                oc = (r.get("outcome") or "").strip()
                if oc in ("nil", "staged"):
                    out[oc] += 1
                elif oc == "skipped-prior-nil":
                    out["skipped"] += 1
    except Exception as e:                  # a malformed CSV is a finding, not a crash
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def lint_staged(iso: str) -> tuple[bool, str]:
    """§5's four staging checks, over this country's folder only."""
    folder = EXCHANGE / "new-queue" / iso
    if not folder.is_dir():
        return True, "nothing staged"
    p = subprocess.run(
        [sys.executable, str(CORPUS / "scripts" / "lint-staged-queue.py"), str(folder)],
        capture_output=True, text=True, cwd=str(CORPUS), errors="replace")
    tail = (p.stdout or p.stderr or "").strip().splitlines()
    return p.returncode == 0, (tail[-1][:200] if tail else f"exit {p.returncode}")


def staged_counts(iso: str) -> tuple[int, int]:
    """Files actually on disk, per folder — §8.5 reports the two separately, because they
    are what Bill decides between when the week is tight."""
    base = EXCHANGE / "new-queue" / iso
    return tuple(len(list((base / sub).glob("*.md"))) if (base / sub).is_dir() else 0
                 for sub in ("baseline", "progress"))


def dirty(path: Path, ignore: str = "") -> str:
    """Uncommitted work. The share is a repo two systems reach through different paths,
    so an edit left uncommitted there is the one thing the next run must not walk into.

    `ignore` drops a path prefix from the answer. The driver's own ledger and session logs
    land in `logs/filler-batch/` between runs, and a check that counted those would fault
    every session after the first for a file the driver itself wrote — two of those in a
    row and the batch would stop on its own bookkeeping."""
    if not (path / ".git").exists():
        return ""
    p = subprocess.run(["git", "status", "--porcelain"], cwd=str(path),
                       capture_output=True, text=True, errors="replace")
    lines = [ln for ln in p.stdout.splitlines()
             if not (ignore and ln[3:].strip().strip('"').startswith(ignore))]
    return "\n".join(lines[:5])


_RESET = re.compile(r"resets?\s+(\d{1,2})[:.](\d{2})\s*(am|pm)?", re.I)


# **A server-side error is the same kind of signal as a quota limit**: the run did
# not fail on its own merits, and the answer is to come back rather than to spend a
# failure on it. 529 is the one seen (2026-09-03); the neighbouring 5xx are here
# because they say the same thing and a driver that waited on one and not the next
# would be drawing a line the API does not.
SERVER_SIDE = {500, 502, 503, 529}


def retry_after(result: dict) -> tuple[datetime, str] | None:
    """When to come back and why, or None where the run failed on its own merits.

    **A rate limit is not a failed run** *(GMB and LBR, 2026-09-02 23:36)*. The quota ran
    out mid-GMB; LBR then bounced in 373ms at $0.00 with `api_error_status: 429` and
    "You've hit your session limit · resets 1:50am". Two runs in a row with problems is
    the stop condition, so the batch stopped — correctly, on the rule as written, and
    wrongly on the facts. The limit reset at 01:50 and the batch sat idle until it was
    looked at, wasting three hours of quota that was there for the taking.

    A limit says *come back later*, so the driver now waits and retries the same country
    rather than counting it against the failure budget. The reset time comes out of the
    message where it is given; where it is not, a default wait applies, because the one
    thing not to do is spin.

    **An outage was reaching the failure budget the same way a limit used to**
    *(TUN, CIV and CPV, 2026-09-03 14:42 to 14:54)*. The API went to `529 Overloaded`
    and every session came back in under four minutes at $0.00 with one turn. Each was
    counted a failure, so the driver worked down the queue at four minutes a country and
    would have spent the lot inside an hour — three countries lost to twelve minutes of
    weather, and nothing in the ledger to distinguish them from a country that had
    genuinely been tried.

    The wait for a server-side error is a **fixed cadence, not a backoff**. Exponential
    backoff exists to keep many clients from converging on a struggling server; this is
    one client, strictly serial, and the only thing it would buy is an outage tolerance
    nobody can read off the arguments. At a fixed ten minutes, `--max-waits` *is* the
    tolerance: twenty waits is a bit over three hours of outage, stated in one number."""
    if not result:
        return None
    text = str(result.get("result", ""))
    status = result.get("api_error_status")
    if status in SERVER_SIDE:
        return datetime.now() + timedelta(minutes=10), f"API {status}, server-side"
    if status != 429 and "limit" not in text.lower():
        return None
    m = _RESET.search(text)
    if not m:
        return datetime.now() + timedelta(minutes=30), "quota exhausted"
    hh, mm, ampm = int(m.group(1)), int(m.group(2)), (m.group(3) or "").lower()
    if ampm == "pm" and hh != 12:
        hh += 12
    elif ampm == "am" and hh == 12:
        hh = 0
    when = datetime.now().replace(hour=hh % 24, minute=mm, second=0, microsecond=0)
    if when <= datetime.now():
        when += timedelta(days=1)
    return when, "quota exhausted"


def share_settled(iso: str, tries: int = 6, wait: float = 5.0) -> str:
    """Is this country's staged batch committed in the share? '' when it is.

    **Scoped to the country, and retried** *(GAB, 2026-09-02 20:02)*. The first version
    asked whether the whole share was clean the instant the session exited, and got two
    things wrong at once. It **raced the session's own push**: GAB was reported as leaving
    the share uncommitted while its 125 files and its note were landing a moment later, in
    commits that are both there. And it would have **faulted a blameless run for someone
    else's work** — the share is written by Bill and by OSINT too, and a hand-carry out of
    `new-queue/` mid-batch (RWA, the same night) looks identical to a run that failed to
    commit.

    Asking only about `new-queue/{ISO}` answers the question that was actually meant: did
    this run put its own batch in. The retry covers the push still being in flight; a run
    that genuinely wrote nothing stays dirty through every try."""
    sub = f"new-queue/{iso}"
    if not (EXCHANGE / ".git").exists() or not (EXCHANGE / sub).exists():
        return ""
    for i in range(tries):
        p = subprocess.run(["git", "status", "--porcelain", "--", sub], cwd=str(EXCHANGE),
                           capture_output=True, text=True, errors="replace")
        out = p.stdout.strip()
        if not out:
            return ""
        if i < tries - 1:
            time.sleep(wait)
    return out.splitlines()[0][:70]


def unpushed(path: Path) -> int:
    """In a repository two systems reach through different paths, an unpushed commit is
    exactly as invisible as an uncommitted edit."""
    if not (path / ".git").exists():
        return 0
    p = subprocess.run(["git", "rev-list", "--count", "@{u}..HEAD"], cwd=str(path),
                       capture_output=True, text=True, errors="replace")
    try:
        return int(p.stdout.strip())
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# one country
# ---------------------------------------------------------------------------

def run_one(iso: str, a) -> dict:
    """Spawn the session, wait, then look at what is on disk. Returns the ledger row."""
    started = time.time()
    log = BATCH / f"{date.today().isoformat()}-{iso}.json"
    cmd = [a.claude, "-p", PROMPT.format(iso=iso, col=QUEUE_COL),
           "--model", a.model,
           "--permission-mode", "bypassPermissions",
           "--output-format", "json",
           "-n", f"filler {iso}"]

    print(f"\n=== {iso} — started {datetime.now():%H:%M:%S} "
          f"(timeout {a.timeout_min}m) ===", flush=True)

    result, err = {}, ""
    try:
        p = subprocess.run(cmd, cwd=str(CORPUS), capture_output=True, text=True,
                           errors="replace", timeout=a.timeout_min * 60)
        raw = p.stdout or ""
        log.write_text(raw + ("\n--- stderr ---\n" + p.stderr if p.stderr else ""),
                       encoding="utf-8", newline="")
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            err = "session produced no JSON result"
        if p.returncode != 0 and not err:
            err = f"claude exited {p.returncode}"
    except subprocess.TimeoutExpired:
        err = f"timed out after {a.timeout_min}m"
    except FileNotFoundError:
        err = f"{a.claude} not found"

    mins = (time.time() - started) / 60
    if result.get("is_error"):
        err = err or str(result.get("result", "session reported an error"))[:200]

    # What the session said, then what is on disk. Only the second decides the verdict.
    csv_path = run_csv(iso, started)
    t = tally(csv_path) if csv_path else {}
    lint_ok, lint_msg = lint_staged(iso)
    base_files, prog_files = staged_counts(iso)
    cell = claimed(iso)

    problems = []
    if err:
        problems.append(err)
    if not cell:
        problems.append(f"'{QUEUE_COL}' still blank — the queue will offer {iso} again")
    if csv_path is None:
        problems.append("no run CSV written")
    elif t.get("error"):
        problems.append(f"run CSV unreadable: {t['error']}")
    elif not t.get("probed"):
        problems.append("run CSV is empty — no gap was probed")
    if not lint_ok:
        problems.append(f"lint-staged-queue: {lint_msg}")
    if (t.get("baseline", 0) + t.get("progress", 0)) and not (base_files + prog_files):
        problems.append("run CSV counts staged files that are not on disk")
    stuck = share_settled(iso)
    if stuck:
        problems.append(f"{iso}'s batch not committed in the share: {stuck}")
    ahead = unpushed(EXCHANGE)
    if ahead:
        problems.append(f"share {ahead} commit(s) unpushed")
    own = dirty(CORPUS, ignore="logs/filler-batch/")
    if own:
        problems.append(f"Corpus tree left uncommitted: {own.splitlines()[0][:60]}")

    row = {
        "iso": iso,
        "started": datetime.fromtimestamp(started).isoformat(timespec="seconds"),
        "minutes": f"{mins:.1f}",
        "verdict": "ok" if not problems else "PROBLEM",
        "probed": t.get("probed", ""),
        "staged_rows": t.get("staged", ""),
        "nil": t.get("nil", ""),
        "skipped_prior_nil": t.get("skipped", ""),
        "files_baseline": base_files,
        "files_progress": prog_files,
        "queue_cell": cell,
        "cost_usd": f"{result.get('total_cost_usd', 0):.2f}" if result else "",
        "turns": result.get("num_turns", ""),
        "session_id": result.get("session_id", ""),
        "problems": "; ".join(problems),
    }

    print(f"--- {iso} {row['verdict']} in {mins:.0f}m — probed {row['probed']}, staged "
          f"{base_files} baseline + {prog_files} progress, nil {row['nil']}, "
          f"${row['cost_usd']}", flush=True)
    for pr in problems:
        print(f"    ! {pr}", flush=True)
    return row, result


# ---------------------------------------------------------------------------
# the batch
# ---------------------------------------------------------------------------

LEDGER_COLS = ["iso", "started", "minutes", "verdict", "probed", "staged_rows", "nil",
               "skipped_prior_nil", "files_baseline", "files_progress", "queue_cell",
               "cost_usd", "turns", "session_id", "problems"]


def append_ledger(path: Path, row: dict) -> None:
    """Appended after every country, not written at the end: a driver killed at 4am
    should leave behind everything it had already learned."""
    new = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LEDGER_COLS)
        if new:
            w.writeheader()
        w.writerow(row)


def take_lock() -> bool:
    BATCH.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        print(f"filler-batch: a driver is already running — {LOCK} holds "
              f"{LOCK.read_text(encoding='utf-8').strip()}")
        print("  If that process is gone, delete the lock and start again. It is never "
              "cleared automatically: two drivers on one tree is the expensive mistake, "
              "and a stale lock is the cheap one.")
        return False
    LOCK.write_text(f"pid {os.getpid()} started {datetime.now():%Y-%m-%d %H:%M}\n",
                    encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Run PROGRESS-FILLER over a queue of "
                                             "countries, one fresh session each.")
    ap.add_argument("--only", nargs="*", metavar="ISO",
                    help="run exactly these, in this order, ignoring the queue file")
    ap.add_argument("--queue-file", metavar="PATH",
                    help=f"order file, one ISO-3 a line (default {ORDER.name}; falls back "
                         f"to {QUEUE.name}'s blank cells when absent)")
    ap.add_argument("--skip", nargs="*", default=[], metavar="ISO")
    ap.add_argument("--until", metavar="HH:MM",
                    help="do not start a country that would run past this clock time")
    ap.add_argument("--max-runs", type=int, default=0, help="0 = the whole queue")
    ap.add_argument("--max-cost-usd", type=float, default=0.0, help="0 = no ceiling")
    ap.add_argument("--max-consecutive-failures", type=int, default=2)
    ap.add_argument("--max-waits", type=int, default=8,
                    help="how many times to wait out a quota reset before giving up")
    ap.add_argument("--timeout-min", type=int, default=120, help="per country")
    ap.add_argument("--resume-window-h", type=float, default=24.0,
                    help="treat a country finished clean this recently as already done")
    ap.add_argument("--assume-min", type=int, default=45,
                    help="expected run length before any has finished, for --until")
    ap.add_argument("--model", default="claude-opus-5[1m]")
    ap.add_argument("--claude", default=shutil.which("claude") or "claude")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not QUEUE.exists():
        print(f"filler-batch: no queue at {QUEUE}")
        return 2
    if not a.dry_run and not (shutil.which(a.claude) or Path(a.claude).exists()):
        print(f"filler-batch: {a.claude} not on PATH")
        return 2

    order_file = Path(a.queue_file) if a.queue_file else ORDER
    if a.only:
        queue, source = a.only, "--only"
    elif order_file.exists():
        queue, source = read_order(order_file), order_file.relative_to(CORPUS).as_posix()
    else:
        queue, source = pending(read_queue()), f"{QUEUE.name} (blank cells)"
    queue = [i for i in queue if i not in set(a.skip)]
    if a.max_runs:
        queue = queue[:a.max_runs]

    deadline = None
    if a.until:
        hh, mm = (int(x) for x in a.until.split(":"))
        deadline = datetime.now().replace(hour=hh, minute=mm, second=0, microsecond=0)
        if deadline <= datetime.now():
            deadline += timedelta(days=1)

    ledger = BATCH / f"{date.today().isoformat()}-batch.csv"
    print(f"filler-batch: {len(queue)} country(ies) queued from {source}")
    print(f"  {', '.join(queue) or '(none)'}")
    # Named rather than skipped: a country whose cell is already filled is a re-probe if
    # it was put on the list deliberately, and silently dropping it would look identical.
    already = [i for i in queue if claimed(i)]
    if already:
        print(f"  note: already searched, will be re-probed — "
              + ", ".join(f"{i} ({claimed(i)})" for i in already))
    missing = [i for i in queue if i not in {r[ISO_COL].strip() for r in read_queue()}]
    if missing:
        print(f"  note: not rows in {QUEUE.name} — {', '.join(missing)}")
    print(f"  model {a.model} | one fresh session each | strictly serial")
    stops = [f"deadline {deadline:%Y-%m-%d %H:%M}" if deadline else "no deadline",
             f"{a.max_consecutive_failures} consecutive failures",
             f"more than {a.max_waits} quota waits",
             f"${a.max_cost_usd:.2f} total" if a.max_cost_usd else "no cost ceiling",
             f"{STOP.name} in {BATCH.relative_to(CORPUS).as_posix()}"]
    print(f"  stop on: {', '.join(stops)}")
    if a.dry_run:
        print("  --dry-run: nothing spawned")
        return 0
    if not queue:
        return 0
    if not take_lock():
        return 2

    done: list[dict] = []
    consecutive = 0
    waits = 0
    spent = 0.0
    stopped = ""

    def release(*_):
        LOCK.unlink(missing_ok=True)

    signal.signal(signal.SIGINT, lambda *x: (release(), sys.exit(130)))
    try:
        for iso in queue:
            if STOP.exists():
                stopped = f"{STOP.name} present"
                break
            if deadline:
                mins = (statistics.median(float(r["minutes"]) for r in done)
                        if done else a.assume_min)
                if datetime.now() + timedelta(minutes=mins) > deadline:
                    stopped = (f"next run ({mins:.0f}m at the running median) would pass "
                               f"{deadline:%H:%M}")
                    break
            if a.max_cost_usd and spent >= a.max_cost_usd:
                stopped = f"spent ${spent:.2f} of ${a.max_cost_usd:.2f}"
                break
            # Resume: skip only what this batch has already finished cleanly. Re-read from
            # the ledger each time rather than tracking it in memory, so a driver restarted
            # after a crash picks up exactly where the last one left off.
            if iso in done_recently(a.resume_window_h):
                print(f"\n=== {iso} — already run clean within "
                      f"{a.resume_window_h:g}h, skipping ===")
                continue

            row, result = run_one(iso, a)
            spent += float(row["cost_usd"] or 0)

            # A limit and an outage both say come back later, not that the run was bad.
            # Wait it out and put the country back at the head of the queue rather than
            # spending a failure on it — see `retry_after`. The ledger still gets the
            # row, so the wait is on the record and the cost of the truncated attempt is
            # counted.
            later = retry_after(result)
            if later is not None and waits < a.max_waits:
                resets, why = later
                waits += 1
                row["verdict"] = "waited"
                append_ledger(ledger, row)
                secs = max(60.0, (resets - datetime.now()).total_seconds() + 120)
                print(f"    {why} — waiting until {resets:%H:%M} "
                      f"({secs / 60:.0f}m), then retrying {iso} "
                      f"(wait {waits} of {a.max_waits})", flush=True)
                if STOP.exists():
                    stopped = f"{STOP.name} present"
                    break
                time.sleep(secs)
                queue.insert(queue.index(iso) + 1, iso)   # try it again next
                continue

            done.append(row)
            append_ledger(ledger, row)
            consecutive = 0 if row["verdict"] == "ok" else consecutive + 1
            if consecutive >= a.max_consecutive_failures:
                stopped = f"{consecutive} runs in a row had problems"
                break
        else:
            stopped = "queue worked through"
    finally:
        release()

    ok = [r for r in done if r["verdict"] == "ok"]
    print(f"\n{'=' * 68}\nfiller-batch: {len(done)} run(s), {len(ok)} clean — stopped: {stopped}")
    if done:
        print(f"  wall {sum(float(r['minutes']) for r in done) / 60:.1f}h | ${spent:.2f} | "
              f"median {statistics.median(float(r['minutes']) for r in done):.0f}m a country")
        print(f"  staged {sum(r['files_baseline'] for r in done)} baseline + "
              f"{sum(r['files_progress'] for r in done)} progress file(s) — undelivered in "
              f"{EXCHANGE / 'new-queue'} until Bill moves them")
        print(f"  ledger: {ledger.relative_to(CORPUS).as_posix()}")
    for r in done:
        if r["verdict"] != "ok":
            print(f"  PROBLEM {r['iso']}: {r['problems']}")
    # The driver's own record is committed here rather than after every country: mid-batch
    # the ledger is a file being appended to, and a commit between each pair would put
    # twenty near-identical commits in the history for one night's work.
    if done and dirty(CORPUS):
        for cmd in (["git", "add", "--", BATCH.relative_to(CORPUS).as_posix()],
                    ["git", "commit", "-m",
                     f"Filler batch {date.today().isoformat()}: {len(done)} run(s), "
                     f"{len(ok)} clean — {stopped}"],
                    ["git", "push"]):
            subprocess.run(cmd, cwd=str(CORPUS), capture_output=True, text=True)

    left = pending(read_queue())
    print(f"  queue: {len(left)} country(ies) still unsearched"
          f"{' — ' + ', '.join(left[:8]) if left else ''}")
    return 1 if len(ok) != len(done) else 0


if __name__ == "__main__":
    raise SystemExit(main())
