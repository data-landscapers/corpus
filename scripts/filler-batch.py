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

**The queue is re-read before every country, never held.** `logs/progress-report-log.csv`
is the queue (PROGRESS-FILLER, *Where the trigger names no {ISO}*), and each run writes
its own row back on finishing (§8.6). Reading it fresh each time means the driver holds
no list that can go stale: a country that claimed itself is skipped without the driver
tracking it, a country whose run died before claiming comes round again, and Bill editing
the file mid-batch is obeyed rather than overwritten.

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
PROMPT = (
    "Read C:\\CORPUS\\PROGRESS-FILLER.md and run that procedure for {iso}, end to end, "
    "including every finishing step in section 8: lint the staged batch, commit and push "
    "the share, write the note for OSINT, set the {iso} row's '{col}' cell in "
    "logs/progress-report-log.csv to today's date, and write the Corpus log line. "
    "You are running unattended from a batch driver, so there is nobody to ask: where you "
    "would have asked, take the conservative option and record it. Run {iso} and no other "
    "country. Finish by printing one line: FILLER {iso} probed=<n> staged=<n> nil=<n>."
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


def dirty(path: Path) -> str:
    """Uncommitted work. The share is a repo two systems reach through different paths,
    so an edit left uncommitted there is the one thing the next run must not walk into."""
    if not (path / ".git").exists():
        return ""
    p = subprocess.run(["git", "status", "--porcelain"], cwd=str(path),
                       capture_output=True, text=True, errors="replace")
    return "\n".join(p.stdout.splitlines()[:5])


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
    if dirty(EXCHANGE):
        problems.append("share left uncommitted")
    ahead = unpushed(EXCHANGE)
    if ahead:
        problems.append(f"share {ahead} commit(s) unpushed")
    if dirty(CORPUS):
        problems.append("Corpus tree left uncommitted")

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
    return row


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
                    help="run exactly these, in this order, ignoring the queue")
    ap.add_argument("--skip", nargs="*", default=[], metavar="ISO")
    ap.add_argument("--until", metavar="HH:MM",
                    help="do not start a country that would run past this clock time")
    ap.add_argument("--max-runs", type=int, default=0, help="0 = the whole queue")
    ap.add_argument("--max-cost-usd", type=float, default=0.0, help="0 = no ceiling")
    ap.add_argument("--max-consecutive-failures", type=int, default=2)
    ap.add_argument("--timeout-min", type=int, default=120, help="per country")
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

    queue = a.only if a.only else pending(read_queue())
    queue = [i for i in queue if i not in set(a.skip)]
    if a.max_runs:
        queue = queue[:a.max_runs]

    deadline = None
    if a.until:
        hh, mm = (int(x) for x in a.until.split(":"))
        deadline = datetime.now().replace(hour=hh, minute=mm, second=0, microsecond=0)
        if deadline <= datetime.now():
            deadline += timedelta(days=1)

    print(f"filler-batch: {len(queue)} country(ies) queued — {', '.join(queue) or '(none)'}")
    print(f"  model {a.model} | one fresh session each | strictly serial")
    stops = [f"deadline {deadline:%Y-%m-%d %H:%M}" if deadline else "no deadline",
             f"{a.max_consecutive_failures} consecutive failures",
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

    ledger = BATCH / f"{date.today().isoformat()}-batch.csv"
    done: list[dict] = []
    consecutive = 0
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
            # Re-read rather than trust the list: the previous run wrote to this queue.
            if not a.only and iso not in pending(read_queue()):
                print(f"\n=== {iso} — already claimed in the queue, skipping ===")
                continue

            row = run_one(iso, a)
            done.append(row)
            append_ledger(ledger, row)
            spent += float(row["cost_usd"] or 0)
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
    left = pending(read_queue())
    print(f"  queue: {len(left)} country(ies) still unsearched"
          f"{' — ' + ', '.join(left[:8]) if left else ''}")
    return 1 if len(ok) != len(done) else 0


if __name__ == "__main__":
    raise SystemExit(main())
