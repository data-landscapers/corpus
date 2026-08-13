#!/usr/bin/env python3
"""finance-compile-scope.py — repo-review task 22.

FINANCE-COMPILE recomputes the `## Financing` section on every place that has
finance records (58 hubs as of 2026-07-24). A single sweep usually changes one
country's records, so recompiling all 58 is wasted work. This helper scopes the
compile to **only the places whose finance records changed since the last
compile**, keyed off git (no manifest needed — task 19).

State: `reviews/finance-compile-state.json` = {"last_compile_commit": "<sha>"}.

Usage:
  python scripts/finance-compile-scope.py            # print places to recompile
  python scripts/finance-compile-scope.py --all      # print ALL finance places (full rebuild)
  python scripts/finance-compile-scope.py --commit    # advance the state ref to HEAD

Scope logic (default): the places tagged on every finance record (`finance_origin`)
that appears in `git diff <last_compile_commit> -- raw/` (ref vs working tree, so it
catches committed *and* not-yet-committed records). No state ref yet, or a bad ref
=> behaves like --all (establish the baseline, then --commit). Deleted records are
resolved from the ref version so a place isn't stranded with a stale aggregate.
"""
import argparse, glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "reviews", "finance-compile-state.json")

def git(*args):
    """git, decoded as UTF-8 rather than the console's locale codec.

    `text=True` alone decodes with `locale.getpreferredencoding()` — cp1252 on this
    machine — so any non-ASCII byte in a path or a diff raised
    `UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d` inside the reader
    thread. The exception surfaced as a traceback while the process still printed a
    place list and exited 0, so the gate read as a full house of 75 places and looked
    like a pass (note 119, 2026-08-05). A gate that crashes must not read like a gate
    that succeeded.
    """
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")

def places_of(text):
    m = re.search(r"^places:\s*(.*)$", text, re.M)
    return set(re.findall(r"[A-Z]{3}|X[A-Z]{2}", m.group(1))) if m else set()

def is_finance(text):
    fm_end = text.find("\n---", 3)
    fm = text[:fm_end] if fm_end > 0 else text
    return re.search(r"^finance_origin:", fm, re.M) is not None

def all_finance_places():
    places = set()
    for p in glob.glob(os.path.join(ROOT, "raw", "**", "*.md"), recursive=True):
        t = open(p, encoding="utf-8").read()
        if is_finance(t):
            places |= places_of(t)
    return places

def read_ref():
    try:
        return json.load(open(STATE, encoding="utf-8")).get("last_compile_commit")
    except Exception:
        return None

def changed_places(ref):
    # ref vs working tree, name-status so we can resolve deletions from the ref side
    r = git("diff", "--name-status", ref, "--", "raw/")
    if r.returncode != 0:
        return None  # bad ref -> caller falls back to --all
    lines = list(r.stdout.splitlines())

    # ...plus untracked records. `git diff` never lists them, and on the normal path —
    # ingest admitting records and firing the compile before anything is committed —
    # every new record is untracked. Without this the helper returned nothing to
    # recompile for exactly the records that triggered it. (Post-run note 35, fixed
    # 2026-07-28.)
    u = git("ls-files", "--others", "--exclude-standard", "--", "raw/")
    if u.returncode == 0:
        lines += ["A\t" + p for p in u.stdout.splitlines() if p.strip()]

    places = set()
    for line in lines:
        parts = line.split("\t")
        status, path = parts[0], parts[-1]
        if not path.endswith(".md"):
            continue
        if status.startswith("D"):
            show = git("show", "%s:%s" % (ref, path))
            text = show.stdout if show.returncode == 0 else ""
        else:
            fp = os.path.join(ROOT, path)
            text = open(fp, encoding="utf-8").read() if os.path.exists(fp) else ""
        if text and is_finance(text):
            places |= places_of(text)
    return places

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--commit", action="store_true")
    a = ap.parse_args()

    if a.commit:
        head = git("rev-parse", "HEAD").stdout.strip()
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        json.dump({"last_compile_commit": head}, open(STATE, "w", encoding="utf-8"), indent=2)
        print("finance-compile baseline set to", head)
        return

    if a.all:
        places = all_finance_places()
    else:
        ref = read_ref()
        places = None if not ref else changed_places(ref)
        if places is None:
            sys.stderr.write("no/invalid compile ref -> full scope (baseline run)\n")
            places = all_finance_places()

    for pl in sorted(places):
        print(pl)

if __name__ == "__main__":
    main()
