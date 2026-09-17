#!/usr/bin/env python3
r"""osint-patch.py — prepare a change to OSINT's repository and deliver it as a patch.

    python scripts/osint-patch.py prepare --job 102-103
    …edit files in the work clone…
    python scripts/osint-patch.py cut --job 102-103 --subject "financier names and the label fallback"

**Corpus never writes to `C:\OSINT`, and that has not changed.** The folder is a mirror: a
write there is discarded at the next sync, and the rule naming it is absolute. What strategic
review 4 ruled (R1, 2026-09-17) is that the *repository* is not the folder. Corpus may prepare
a commit and hand it over; OSINT checks it and applies it, so `master` keeps one writer and
nothing lands in OSINT unless OSINT puts it there.

**The carrier is `git format-patch`, not a branch.** A branch needs a second clone of the
origin, a fetch and a merge step in OSINT's night, which is machinery for no gain when the
alternative is a directory of `.patch` files on the share. A patch series also names its own
base, so a file that moved underneath it merges on `git am -3` rather than failing — and where
it cannot merge, OSINT is told rather than left with a half-applied tree.

**Three trees and nothing else.** The allowed set is `scripts/`, `lookups/` and the three wiki
index pages. It excludes `raw/` because frontmatter changes travel as a script plus its input
— a patch against `raw/` is cut from a mirror that ingest rewrites every night, and across
thousands of files a conflict is a certainty rather than a risk. It excludes wiki prose because
that is where Phase B writes, and OSINT's `logs/`, `reviews/` and process files because those
are OSINT's own business and Corpus does not read them, let alone edit them.

**The check here is a convenience; the guard is OSINT's.** `assert-containment.py --patch`
runs on the side that can verify it, before `git am`. This script refusing to cut a patch that
strays outside the set means OSINT is not sent one, which is politeness, not enforcement.

**The work clone is of the mirror, never the mirror itself.** `git clone` reads; it copies
`C:\OSINT` into a directory of Corpus's own outside both repositories, and every edit and
commit happens there. Where the mirror has moved on since the clone, `prepare --refresh`
takes it forward; the patch then names the newer base and OSINT's `-3` does the rest.
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import osint_lib                                   # noqa: E402  the mirror path, in one place
import status_lib                                  # noqa: E402  the exchange share, likewise

# The work clone. Outside `C:\CORPUS` because it is not Corpus's material, and outside
# `C:\OSINT` because nothing of Corpus's belongs inside the mirror at all.
WORK = os.environ.get("CORPUS_OSINT_WORK", r"C:\osint-work")

# Where a cut patch series is delivered. The share is the one place both machines reach, and
# `prepared/` is the review's name for work handed over ready to run.
PREPARED = os.path.join(status_lib.EXCHANGE, "prepared")

# **What a patch may touch** *(strategic review 4, R1 and OSINT's register comment 5)*. Two
# directories and three files, checked against the paths git reports rather than against what
# the operator believes they edited.
ALLOWED_DIRS = ("scripts/", "lookups/")
ALLOWED_FILES = ("wiki/index.md", "wiki/places-index.md", "wiki/topics-index.md")

JOB = re.compile(r"^[0-9]+(?:-[0-9]+)*$")

# A clone inherits the system gitconfig, where `core.autocrlf` is true on this machine and
# `filter.lfs` is configured. OSINT's own `.gitattributes` settles the first (`* -text`, the
# working tree is authoritative); the second is turned off for the clone because Corpus never
# touches an LFS-tracked artefact and smudging them would copy gigabytes to no purpose.
CLONE_ENV = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")


def git(*args, cwd=None, check=True, env=None):
    """Run git and return its stdout, or raise with what git said on stderr."""
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                         env=env or os.environ)
    if check and out.returncode != 0:
        raise SystemExit(f"osint-patch: git {' '.join(args)} failed in {cwd or os.getcwd()}\n"
                         f"{out.stderr.strip()}")
    return out.stdout


def refuse(msg: str, code: int = 2) -> int:
    print(f"osint-patch: {msg}", file=sys.stderr)
    return code


def guard_paths() -> str | None:
    """Why the work clone's location is unusable, or None.

    A clone under `C:\\OSINT` would be a write into the mirror; a clone under `C:\\CORPUS`
    would put OSINT's whole tree inside Corpus's history the first time somebody ran
    `git add -A`. Both are cheap to check and expensive to discover."""
    work = os.path.abspath(WORK)
    for root, why in ((osint_lib.MIRROR, "the mirror, which Corpus never writes to"),
                      (os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "the Corpus repository")):
        root = os.path.abspath(root)
        if work == root or work.startswith(root + os.sep):
            return f"the work clone {work} is inside {root} - {why}"
    return None


def clone_exists() -> bool:
    return os.path.isdir(os.path.join(WORK, ".git"))


def mirror_head() -> str:
    head = osint_lib.mirror_head()
    if not head:
        raise SystemExit(f"osint-patch: {osint_lib.MIRROR} will not say what commit it holds "
                         f"- a failed read, not an empty mirror")
    return head


def prepare(job: str, refresh: bool) -> int:
    """Put the work clone at the mirror's HEAD, with nothing of a previous job left in it."""
    bad = guard_paths()
    if bad:
        return refuse(bad)
    head = mirror_head()
    if not clone_exists():
        print(f"cloning {osint_lib.MIRROR} into {WORK} (once; later jobs fetch)")
        git("clone", "--no-hardlinks", osint_lib.MIRROR, WORK, env=CLONE_ENV)
    elif refresh:
        git("fetch", "origin", cwd=WORK, env=CLONE_ENV)
    # **Whatever the last job left is discarded here, not carried into this one.** A patch
    # series is cut from `git status`, so an uncommitted stray from a previous sitting would
    # be delivered to OSINT inside somebody else's job.
    git("reset", "--hard", head, cwd=WORK, env=CLONE_ENV)
    git("clean", "-fd", cwd=WORK, env=CLONE_ENV)
    print(f"work clone : {WORK}")
    print(f"base       : {head[:12]}  (the mirror's HEAD)")
    print(f"job        : {job}")
    print(f"allowed    : {', '.join(ALLOWED_DIRS + ALLOWED_FILES)}")
    print(f"next       : edit in the clone, then "
          f"python scripts/osint-patch.py cut --job {job} --subject \"what changed\"")
    return 0


def changed(cwd: str) -> list[str]:
    """Every path git reports as changed, renames counted at both ends."""
    out = git("status", "--porcelain", "-z", cwd=cwd)
    fields = [f for f in out.split("\0") if f]
    paths, i = [], 0
    while i < len(fields):
        entry = fields[i]
        status, path = entry[:2], entry[3:]
        paths.append(path)
        if "R" in status and i + 1 < len(fields):     # a rename carries its source next
            i += 1
            paths.append(fields[i])
        i += 1
    return sorted(set(paths))


def outside(paths) -> list[str]:
    """The paths that are not in the allowed set — the whole of what this refuses on."""
    out = []
    for p in paths:
        p = p.replace("\\", "/").strip('"')
        if p in ALLOWED_FILES or any(p.startswith(d) for d in ALLOWED_DIRS):
            continue
        out.append(p)
    return out


def cut(job: str, subject: str, dry_run: bool) -> int:
    """Commit what is in the clone and write the series to the share."""
    bad = guard_paths()
    if bad:
        return refuse(bad)
    if not clone_exists():
        return refuse(f"no work clone at {WORK} - run prepare --job {job} first")
    paths = changed(WORK)
    if not paths:
        return refuse(f"nothing has changed in {WORK} - there is no patch to cut")
    stray = outside(paths)
    if stray:
        print(f"osint-patch: {len(stray)} path(s) outside the allowed set "
              f"({', '.join(ALLOWED_DIRS + ALLOWED_FILES)}):", file=sys.stderr)
        for p in stray:
            print(f"    {p}", file=sys.stderr)
        print("Nothing was committed. A change to raw/ frontmatter travels as a script plus "
              "its input; wiki prose and OSINT's own files are not Corpus's to edit.",
              file=sys.stderr)
        return 2

    base = git("rev-parse", "HEAD", cwd=WORK).strip()
    out_dir = os.path.join(PREPARED, f"job-{job}")
    print(f"job {job}: {len(paths)} file(s)")
    for p in paths:
        print(f"    {p}")
    if dry_run:
        print(f"dry run - nothing committed, nothing written to {out_dir}")
        return 0

    git("add", "--", *paths, cwd=WORK)
    git("commit", "-m", f"job {job}: {subject}", cwd=WORK)

    os.makedirs(out_dir, exist_ok=True)
    for old in os.listdir(out_dir):                  # a re-cut replaces its own series
        if old.endswith(".patch") or old == "BASE":
            os.remove(os.path.join(out_dir, old))
    git("format-patch", f"{base}..HEAD", "-o", out_dir, cwd=WORK)

    with io.open(os.path.join(out_dir, "BASE"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"{base}\n")
        fh.write(f"# job {job}, cut {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} from the "
                 f"mirror's HEAD.\n")
        fh.write("# Apply on OSINT's machine:\n")
        fh.write(f"#   python scripts/assert-containment.py --patch X:\\prepared\\job-{job}\n")
        fh.write(f"#   git am --keep-cr -3 X:\\prepared\\job-{job}\\*.patch\n")
        fh.write("# then lint and commit. A conflict means master wins: refuse the series in "
                 "one line and Corpus re-cuts it.\n")

    series = sorted(f for f in os.listdir(out_dir) if f.endswith(".patch"))
    print(f"delivered  : {out_dir}")
    for f in series:
        print(f"    {f}")
    print(f"base       : {base[:12]}  (named in BASE beside the series)")
    print("Tell OSINT in an [ACT] note naming the job and the directory; nothing in OSINT "
          "polls for it.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare a change to OSINT's repository and "
                                             "deliver it as a patch series.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare", help="clone or reset the work clone to the mirror's HEAD")
    p.add_argument("--job", required=True, help="the housekeeping job number, e.g. 102-103")
    p.add_argument("--refresh", action="store_true",
                   help="fetch the mirror first, where it has moved since the clone")

    c = sub.add_parser("cut", help="commit the clone's changes and write the series to the share")
    c.add_argument("--job", required=True)
    c.add_argument("--subject", required=True, help="the commit subject, after 'job NN: '")
    c.add_argument("--dry-run", action="store_true",
                   help="list what would be committed and check containment, write nothing")

    args = ap.parse_args()
    if not JOB.match(args.job):
        return refuse(f"--job {args.job!r} is not a job number (digits, or digits joined by "
                      f"hyphens for a pair worked together)")
    if args.cmd == "prepare":
        return prepare(args.job, args.refresh)
    return cut(args.job, args.subject, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
