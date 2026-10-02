#!/usr/bin/env python3
"""
deploy-state.py — is the newest site/ commit actually being served?

**The push is not the deploy.** The Pages workflow publishes what is committed in `site/`,
and its run can sit queued at GitHub for hours or fail in the deploy step with nothing here
noticing: the push succeeded, so the render logged and went home. This reads the workflow
run and says one of three things about the newest commit the workflow would have fired on.

  - **deployed** — a run whose tree holds that commit completed with `success`.
  - **pending**  — the newest such run is queued or in progress and still inside
                   `STUCK_AFTER_MIN`, or the push is too fresh for a run to exist yet.
  - **stuck**    — everything else: the run failed, was cancelled or timed out; it has sat
                   unfinished past `STUCK_AFTER_MIN`; no run was ever created; or the
                   commit is not on the remote at all.

**A run covers the commit when the commit is an ancestor of the run's `head_sha`**, not
only when the two are equal. The workflow deploys the whole tree at the head of a push, so
a push carrying the site commit and a log line after it deploys the site commit under the
log line's sha — and a lookup by `head_sha` alone reads that as *no run*.

**A success among the covering runs is `deployed`, whatever came after it**, because the
tree it published holds the commit. Failing that, only the newest covering run is judged:
the workflow's concurrency group lets a newer run supersede an older one, so an old failure
under a run still in flight is history.

**`--fix` acts only on `stuck`, only with `GITHUB_TOKEN` set, and once per call.** An
unfinished run is cancelled (force-cancelled if it will not go) and re-run; a finished one
is re-run; where no run exists the workflow is dispatched on `main`. It stops re-running
at `MAX_ATTEMPTS`, because a poll that re-runs a deploy failing for a reason of its own is
a job looping on the fault that stopped it. It never pushes: an unpushed commit is the
runbook's to push. The token needs **Actions: read and write** on this repository and
nothing more; without one the reads still work, unauthenticated, at 60 requests an hour.

Usage:  python scripts/deploy-state.py                 # report
        python scripts/deploy-state.py --fix           # cancel and re-run a stuck deploy
        python scripts/deploy-state.py --fix --wait 300    # ...and wait while it is pending
        python scripts/deploy-state.py --quiet         # print nothing when deployed
Exit:   0 deployed, 1 pending, 2 stuck, 3 could not tell (GitHub or git did not answer).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "data-landscapers/corpus"
WORKFLOW = "deploy.yml"
BRANCH = "main"
API = f"https://api.github.com/repos/{REPO}/actions"
# What the workflow fires on (`.github/workflows/deploy.yml` -> `on.push.paths`).
PATHS = ["site", f".github/workflows/{WORKFLOW}"]

# A deploy takes about a minute and the workflow's own deploy step gives up at 20, so a run
# unfinished at 30 is not going to finish by being left alone.
STUCK_AFTER_MIN = 30
# A push this fresh may simply not have its run yet.
NO_RUN_GRACE_MIN = 3
MAX_ATTEMPTS = 3
POLL_SECONDS = 30

DEPLOYED, PENDING, STUCK, UNKNOWN = "deployed", "pending", "stuck", "unknown"
EXIT = {DEPLOYED: 0, PENDING: 1, STUCK: 2, UNKNOWN: 3}


class CannotTell(Exception):
    """GitHub or git did not answer; nothing here says the deploy is good or bad."""


# --------------------------------------------------------------------------- git

def git(*args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True,
                              timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        raise CannotTell(f"git {args[0]}: {exc}") from exc


def site_commit() -> tuple[str, dt.datetime]:
    """The newest commit the workflow would fire on, and when it was committed."""
    out = git("log", "-1", "--format=%H %cI", "--", *PATHS)
    if out.returncode != 0 or not out.stdout.strip():
        raise CannotTell(f"git log found no commit touching {PATHS[0]}/")
    sha, when = out.stdout.split()
    return sha, dt.datetime.fromisoformat(when)


def pushed(sha: str) -> bool:
    out = git("branch", "-r", "--contains", sha)
    return out.returncode == 0 and bool(out.stdout.strip())


def covers(run_sha: str, sha: str) -> bool:
    """True where the tree at `run_sha` holds `sha`. A sha this clone lacks covers nothing."""
    return run_sha == sha or git("merge-base", "--is-ancestor", sha, run_sha).returncode == 0


# --------------------------------------------------------------------------- GitHub

def call(method: str, path: str, token: str = "", body: dict | None = None) -> dict:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "corpus-deploy-state"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:200]
        raise CannotTell(f"GitHub {method} {path}: {exc.code} {detail}") from exc
    except (urllib.error.URLError, OSError) as exc:
        raise CannotTell(f"GitHub {method} {path}: {exc}") from exc
    return json.loads(raw) if raw.strip() else {}


def runs(token: str = "") -> list[dict]:
    """The workflow's recent runs on main, newest first."""
    got = call("GET", f"/workflows/{WORKFLOW}/runs?branch={BRANCH}&per_page=30", token)
    return got.get("workflow_runs", [])


# --------------------------------------------------------------------------- the judgement

def started(run: dict) -> dt.datetime:
    """When the current attempt began — `run_started_at` moves on a re-run, `created_at` does not."""
    return dt.datetime.fromisoformat(run.get("run_started_at") or run["created_at"])


def minutes(delta: dt.timedelta) -> str:
    m = int(delta.total_seconds() // 60)
    return f"{m}m" if m < 120 else f"{m // 60}h{m % 60:02d}m"


def judge(covering: list[dict], is_pushed: bool, committed: dt.datetime,
          now: dt.datetime) -> tuple[str, str, dict | None]:
    """(state, reason, the run it was judged on) from the covering runs, newest first."""
    for run in covering:
        if run["status"] == "completed" and run["conclusion"] == "success":
            return DEPLOYED, f"run {run['id']} succeeded", run
    if not is_pushed:
        return STUCK, "the commit is not on the remote - `git push`", None
    if not covering:
        age = now - committed
        if age < dt.timedelta(minutes=NO_RUN_GRACE_MIN):
            return PENDING, "pushed, no run yet", None
        return STUCK, f"no run {minutes(age)} after the commit", None
    run = covering[0]
    if run["status"] == "completed":
        return STUCK, f"run {run['id']} ended {run['conclusion']}", run
    age = now - started(run)
    if age < dt.timedelta(minutes=STUCK_AFTER_MIN):
        return PENDING, f"run {run['id']} {run['status']} for {minutes(age)}", run
    return STUCK, f"run {run['id']} {run['status']} for {minutes(age)}", run


def state(token: str = "") -> tuple[str, str, dict | None, str]:
    sha, committed = site_commit()
    covering = [r for r in runs(token) if covers(r["head_sha"], sha)]
    now = dt.datetime.now(dt.timezone.utc)
    return (*judge(covering, pushed(sha), committed, now), sha)


# --------------------------------------------------------------------------- the fix

def fix(run: dict | None, reason: str, token: str) -> tuple[bool, str]:
    """(acted, what was done or why not). Called on `stuck` only."""
    if "not on the remote" in reason:
        return False, "not fixed: pushing is the runbook's"
    if not token:
        where = run["html_url"] if run else f"https://github.com/{REPO}/actions"
        return False, f"not fixed: GITHUB_TOKEN is not set - re-run by hand at {where}"
    if run is None:
        call("POST", f"/workflows/{WORKFLOW}/dispatches", token, {"ref": BRANCH})
        return True, f"dispatched {WORKFLOW} on {BRANCH}"
    if run.get("run_attempt", 1) >= MAX_ATTEMPTS:
        return False, (f"not fixed: attempt {run['run_attempt']} of {MAX_ATTEMPTS} - "
                       f"{run['html_url']}")
    did = "re-run"
    if run["status"] != "completed":
        call("POST", f"/runs/{run['id']}/cancel", token)
        did = "cancelled and re-run"
        if not cancelled(run["id"], token):
            call("POST", f"/runs/{run['id']}/force-cancel", token)
            if not cancelled(run["id"], token):
                return False, f"not fixed: run {run['id']} will not cancel - {run['html_url']}"
    call("POST", f"/runs/{run['id']}/rerun", token)
    return True, f"run {run['id']} {did}"


def cancelled(run_id: int, token: str, tries: int = 12, pause: float = 5) -> bool:
    """A re-run is refused while the run is still live, so wait for the cancel to land."""
    for _ in range(tries):
        if call("GET", f"/runs/{run_id}", token).get("status") == "completed":
            return True
        time.sleep(pause)
    return False


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description="Deployed, pending or stuck - the newest site/ commit.")
    ap.add_argument("--fix", action="store_true",
                    help="cancel and re-run a stuck deploy (needs GITHUB_TOKEN)")
    ap.add_argument("--wait", type=int, default=0, metavar="SECONDS",
                    help="while pending, look again until this long has passed")
    ap.add_argument("--quiet", action="store_true", help="print nothing when deployed")
    args = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN", "").strip()

    deadline = time.monotonic() + args.wait
    fixed, acted, attempt = "", False, None
    try:
        while True:
            verdict, reason, run, sha = state(token)
            if verdict == STUCK and args.fix and not fixed:
                acted, fixed = fix(run, reason, token)
                attempt = run.get("run_attempt") if run else None
                if acted:
                    verdict = PENDING
            elif verdict == STUCK and acted and (run is None or run.get("run_attempt") == attempt):
                # GitHub has not yet shown the attempt just asked for; the old one is not news.
                verdict = PENDING
            if verdict != PENDING or time.monotonic() + POLL_SECONDS > deadline:
                break
            time.sleep(POLL_SECONDS)
    except CannotTell as exc:
        print(f"deploy: could not tell - {exc}")
        return EXIT[UNKNOWN]

    if verdict == DEPLOYED and args.quiet:
        return EXIT[DEPLOYED]
    print(f"deploy: {verdict} - {sha[:7]}, {reason}" + (f"; {fixed}" if fixed else ""))
    return EXIT[verdict]


if __name__ == "__main__":
    sys.exit(main())
