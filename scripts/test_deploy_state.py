#!/usr/bin/env python3
"""test_deploy_state.py — deployed, pending or stuck, and what `--fix` will and will not do.

    python scripts/test_deploy_state.py

`deploy-state.py` turns a list of workflow runs into one of three words, and `--fix` acts
on one of them. Both are tested here with made-up runs and a recorded `call`, so nothing
touches GitHub: the judgement is a pure function, and the fix is checked by the requests
it would have sent.

**The cases that matter most are the two the old one-liner got wrong**: a run queued for
hours read as merely `queued`, and a push whose head was not the site commit read as
`no run`.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "deploy_state", Path(__file__).resolve().parent / "deploy-state.py")
ds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ds)

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


NOW = dt.datetime(2026, 10, 2, 8, 0, tzinfo=dt.timezone.utc)


def ago(mins: int) -> str:
    return (NOW - dt.timedelta(minutes=mins)).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(status: str, conclusion: str | None = None, mins: int = 1, attempt: int = 1,
        run_id: int = 7) -> dict:
    return {"id": run_id, "status": status, "conclusion": conclusion, "run_attempt": attempt,
            "created_at": ago(mins + 600), "run_started_at": ago(mins), "head_sha": "a" * 40,
            "html_url": f"https://github.com/x/y/actions/runs/{run_id}"}


def judged(covering: list[dict], is_pushed: bool = True, commit_mins: int = 60) -> str:
    return ds.judge(covering, is_pushed, NOW - dt.timedelta(minutes=commit_mins), NOW)[0]


print("the judgement")
check("a successful run is deployed", judged([run("completed", "success")]), ds.DEPLOYED)
check("a run just queued is pending", judged([run("queued", mins=2)]), ds.PENDING)
check("a run in progress is pending", judged([run("in_progress", mins=10)]), ds.PENDING)
check("queued past the limit is stuck",
      judged([run("queued", mins=ds.STUCK_AFTER_MIN + 1)]), ds.STUCK)
check("in progress past the limit is stuck",
      judged([run("in_progress", mins=ds.STUCK_AFTER_MIN + 1)]), ds.STUCK)
for conclusion in ("failure", "cancelled", "timed_out", "startup_failure"):
    check(f"ended {conclusion} is stuck", judged([run("completed", conclusion)]), ds.STUCK)
check("the reason names the run and how long",
      ds.judge([run("queued", mins=582)], True, NOW, NOW)[1], "run 7 queued for 9h42m")

print("\nwhich run is judged")
check("a newer run in flight outranks an older failure",
      judged([run("queued", mins=2, run_id=8), run("completed", "failure")]), ds.PENDING)
check("a newer failure outranks nothing but an older failure",
      judged([run("completed", "failure", run_id=8), run("completed", "failure")]), ds.STUCK)
check("a success under a newer failure is still deployed",
      judged([run("completed", "failure", run_id=8), run("completed", "success")]), ds.DEPLOYED)
# A re-run restarts the clock: the run was created ten hours ago and began again a minute ago.
check("a re-run is timed from its own start, not the run's creation",
      judged([run("queued", mins=1, attempt=2)]), ds.PENDING)

print("\nno run at all")
check("a fresh push with no run yet is pending", judged([], commit_mins=1), ds.PENDING)
check("no run after the grace is stuck",
      judged([], commit_mins=ds.NO_RUN_GRACE_MIN + 1), ds.STUCK)
check("an unpushed commit is stuck", judged([], is_pushed=False, commit_mins=1), ds.STUCK)
check("and says to push",
      "git push" in ds.judge([], False, NOW, NOW)[1], True)

print("\ncovering")
real_git = ds.git


class _Proc:
    def __init__(self, code: int):
        self.returncode, self.stdout = code, ""


ds.git = lambda *a: _Proc(0 if a[-1] == "descendant" else 128 if a[-1] == "unknown" else 1)
check("the commit itself covers", ds.covers("abc", "abc"), True)
check("a descendant covers", ds.covers("descendant", "abc"), True)
check("an unrelated sha does not", ds.covers("other", "abc"), False)
check("a sha this clone lacks does not", ds.covers("unknown", "abc"), False)
ds.git = real_git

print("\nthe fix")
sent: list[tuple[str, str]] = []
live = {"status": "completed"}


def fake_call(method, path, token="", body=None):
    sent.append((method, path))
    return dict(live) if method == "GET" else {}


ds.call = fake_call
ds.time.sleep = lambda s: None


def fixed(run_, reason="x", token="t") -> tuple[bool, list[tuple[str, str]]]:
    sent.clear()
    return ds.fix(run_, reason, token)[0], list(sent)


check("without a token nothing is sent", fixed(run("completed", "failure"), token=""), (False, []))
check("and the message says where to do it by hand",
      "actions/runs/7" in ds.fix(run("completed", "failure"), "x", "")[1], True)
check("an unpushed commit is not fixed", fixed(None, "the commit is not on the remote"), (False, []))
check("a failed run is re-run",
      fixed(run("completed", "failure")), (True, [("POST", "/runs/7/rerun")]))
check("a queued run is cancelled, seen to be gone, then re-run",
      fixed(run("queued", mins=600)),
      (True, [("POST", "/runs/7/cancel"), ("GET", "/runs/7"), ("POST", "/runs/7/rerun")]))
check("no run at all dispatches the workflow",
      fixed(None), (True, [("POST", f"/workflows/{ds.WORKFLOW}/dispatches")]))
check("the last attempt is not re-run",
      fixed(run("completed", "failure", attempt=ds.MAX_ATTEMPTS)), (False, []))
live["status"] = "queued"
acted, calls = fixed(run("queued", mins=600))
check("a run that will not cancel is force-cancelled, and not re-run if that fails too",
      (acted, ("POST", "/runs/7/force-cancel") in calls, ("POST", "/runs/7/rerun") in calls),
      (False, True, False))

print()
if failures:
    print(f"{len(failures)} FAILED: {', '.join(failures)}")
    sys.exit(1)
print("all checks passed")
