#!/usr/bin/env python3
"""pull.py — bring OSINT's outputs/ into Corpus as upstream/.

The first half of the build (DESIGN.md §8). It reads OSINT's *committed* HEAD,
extracts outputs/ at that commit, checks it for source bodies, and replaces
upstream/ with it wholesale.

    python build/pull.py                 # pull if OSINT has moved
    python build/pull.py --dry-run       # report what would change, touch nothing
    python build/pull.py --force         # re-pull even if the SHA is unchanged
    python build/pull.py --commit        # git-commit the result in Corpus

OSINT IS READ-ONLY. Every git call here is `rev-parse`, `archive`, `diff`,
`log` or `status` — all read-only, all via `git -C`. Nothing in this file may
write to the OSINT tree, and nothing may read OSINT's working tree instead of
its committed state: a half-finished sweep is uncommitted, which is precisely
what makes reading HEAD safe against a run in progress.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
UPSTREAM = CORPUS / "upstream"
BUILT_FROM = UPSTREAM / "BUILT-FROM"

# Files in upstream/ that Corpus authors and the pull must not destroy.
PRESERVE = {"README.md", "BUILT-FROM"}

DEFAULT_OSINT = Path(os.environ.get("OSINT_PATH", r"C:\Users\bill\OSINT"))

# The gate is two layers: named checks that target the actual failure mode,
# and length caps as the backstop for anything the names miss.
#
# A body would arrive under one of these names. Any of them is an immediate
# refusal, whatever the field is long.
BODY_COLUMNS = {
    "body", "text", "content", "full_text", "fulltext",
    "article", "raw_body", "verbatim", "extract",
}

# Measured across all 99 columns in outputs/ (2026-08-06): 95 sit under 500
# chars, the longest being a 673-char url. So a 1000-char cap leaves ordinary
# metadata alone while catching any *new* column that starts carrying prose.
MAX_FIELD = 1000

# Four columns legitimately hold compiled prose — funder project abstracts and
# ledger notes — and top out at 3243 chars today. They get a higher cap, not an
# exemption. Adding to this list is a deliberate edit, which is the point:
# a new prose column should have to be admitted, not discovered.
PROSE_COLUMNS = {"description", "note", "position_end", "summary"}
MAX_PROSE_FIELD = 8000

csv.field_size_limit(10 ** 8)


# --- OSINT, read-only -------------------------------------------------------

def git(repo: Path, *args: str) -> str:
    """Run a read-only git command against `repo` and return stdout."""
    out = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, check=True,
    )
    return out.stdout.decode("utf-8", "replace").strip()


def git_bytes(repo: Path, *args: str) -> bytes:
    out = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, check=True,
    )
    return out.stdout


def extract_outputs(osint: Path, sha: str) -> Path:
    """Extract outputs/ at `sha` into a staging dir, and return it.

    `git archive` reads the object store, never the working tree.
    """
    # Staged outside the repo, deliberately: a staging dir inside Corpus can be
    # committed by accident if a run dies between extract and swap.
    staging = Path(tempfile.mkdtemp(prefix="corpus-pull-"))

    blob = git_bytes(osint, "archive", sha, "outputs/")
    with tarfile.open(fileobj=io.BytesIO(blob)) as tar:
        for member in tar.getmembers():
            # Strip the leading "outputs/" so upstream/ mirrors its contents.
            parts = Path(member.name).parts
            if len(parts) < 2:
                continue
            member.name = str(Path(*parts[1:]))
            tar.extract(member, staging)
    return staging


# --- the leak gate ----------------------------------------------------------

class Leak(Exception):
    pass


def frontmatter(text: str) -> list[str]:
    """Return the frontmatter lines of a markdown file, or []."""
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    return text[3:end].splitlines() if end != -1 else []


def check_markdown(path: Path, rel: str) -> list[str]:
    """A raw/ source page declares itself in its frontmatter. Compiled
    reports carry no `type:` key at all."""
    faults = []
    fm = frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    for line in fm:
        key = line.split(":", 1)[0].strip()
        if key == "type" and line.split(":", 1)[1].strip() == "source":
            faults.append(f"{rel}: frontmatter declares `type: source`")
        if key == "body_completeness":
            faults.append(f"{rel}: frontmatter carries `body_completeness`")
    return faults


def cap_for(name: str) -> int:
    return MAX_PROSE_FIELD if name.strip().lower() in PROSE_COLUMNS else MAX_FIELD


def check_csv(path: Path, rel: str) -> list[str]:
    faults = []
    with path.open(encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            return faults
        named = [c for c in header if c.strip().lower() in BODY_COLUMNS]
        if named:
            return [f"{rel}: carries body column(s) {', '.join(named)}"]
        for n, row in enumerate(reader, start=2):
            for col, value in zip(header, row):
                cap = cap_for(col)
                if len(value) > cap:
                    faults.append(
                        f"{rel}: row {n}, column `{col}` is {len(value)} chars "
                        f"(cap {cap})"
                    )
                    return faults  # one report per file is enough
    return faults


def check_json(path: Path, rel: str) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return []
    faults = []

    def walk(node, trail, key=""):
        if faults:
            return
        if isinstance(node, str):
            cap = cap_for(key)
            if len(node) > cap:
                faults.append(
                    f"{rel}: `{trail}` is {len(node)} chars (cap {cap})"
                )
        elif isinstance(node, dict):
            for k, v in node.items():
                if str(k).strip().lower() in BODY_COLUMNS:
                    faults.append(f"{rel}: `{trail}` carries body key `{k}`")
                    return
                walk(v, f"{trail}.{k}" if trail else str(k), str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{trail}[{i}]", key)

    walk(data, "")
    return faults


def check_text(path: Path, rel: str) -> list[str]:
    """Plain-text files in outputs/ are slug lists — every line is short."""
    for n, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
    ):
        if len(line) > MAX_FIELD:
            return [f"{rel}: line {n} is {len(line)} chars (cap {MAX_FIELD})"]
    return []


def leak_gate(staging: Path) -> None:
    """Refuse the pull if anything staged carries a source body.

    outputs/ holds metadata and compiled prose by construction, so this should
    never fire — which is exactly why it fails the run rather than warning.
    A leak into a public repo's history is permanent.
    """
    faults: list[str] = []
    checkers = {
        ".md": check_markdown,
        ".csv": check_csv,
        ".json": check_json,
        ".txt": check_text,
    }
    for path in sorted(staging.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(staging).as_posix()
        if "raw/" in rel:
            faults.append(f"{rel}: path is under raw/")
            continue
        check = checkers.get(path.suffix.lower())
        if check:
            faults.extend(check(path, rel))

    if faults:
        raise Leak(
            "leak gate FAILED — nothing was written. "
            f"{len(faults)} problem(s):\n  " + "\n  ".join(faults[:20])
        )


# --- the swap ---------------------------------------------------------------

def swap(staging: Path) -> None:
    """Replace upstream/ wholesale, preserving only Corpus-authored files.

    Wholesale, not merged: a directory removed in OSINT must disappear here,
    and a merge would leave it behind for ever.
    """
    UPSTREAM.mkdir(exist_ok=True)
    wanted = {
        p.relative_to(staging).as_posix()
        for p in staging.rglob("*") if p.is_file()
    }

    # 1. Move the new tree in, overwriting whatever is there.
    for src in sorted(staging.rglob("*")):
        if not src.is_file():
            continue
        dst = UPSTREAM / src.relative_to(staging)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            dst.unlink()
        shutil.move(str(src), str(dst))

    # 2. Delete whatever the last pull left that this one does not want, so a
    #    directory removed in OSINT disappears here too. Done file-by-file
    #    rather than by removing directories: `rmtree` on a non-empty tree is
    #    blocked on some mounts, and an empty directory left behind is
    #    harmless because git does not track directories.
    for path in sorted(UPSTREAM.rglob("*"), key=lambda p: -len(p.parts)):
        rel = path.relative_to(UPSTREAM).as_posix()
        if path.is_file():
            if rel not in wanted and rel not in PRESERVE:
                path.unlink()
        elif path.is_dir():
            try:
                path.rmdir()  # succeeds only if it is now empty
            except OSError:
                pass

    shutil.rmtree(staging, ignore_errors=True)


def verify(osint: Path, sha: str) -> list[str]:
    """upstream/ must equal outputs/ at `sha`, exactly. Cheap, and it is the
    only thing that proves the swap did what it claims."""
    expected = {
        line[len("outputs/"):]
        for line in git(osint, "ls-tree", "-r", "--name-only", sha, "outputs/").splitlines()
        if line.startswith("outputs/")
    }
    actual = {
        p.relative_to(UPSTREAM).as_posix()
        for p in UPSTREAM.rglob("*")
        if p.is_file() and p.relative_to(UPSTREAM).as_posix() not in PRESERVE
    }
    faults = []
    for missing in sorted(expected - actual)[:10]:
        faults.append(f"missing from upstream/: {missing}")
    for extra in sorted(actual - expected)[:10]:
        faults.append(f"not in OSINT outputs/: {extra}")
    return faults


def describe_change(osint: Path, old: str | None, new: str) -> str:
    if not old:
        return "first pull — no previous SHA on record"
    lines = git(
        osint, "diff", "--name-status", f"{old}..{new}", "--", "outputs/"
    ).splitlines()
    if not lines:
        return "no change to outputs/ between the two commits"
    tally: dict[str, int] = {}
    for line in lines:
        tally[line[0]] = tally.get(line[0], 0) + 1
    names = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed"}
    summary = ", ".join(
        f"{n} {names.get(k, k)}" for k, n in sorted(tally.items())
    )
    detail = "\n  ".join(lines[:15])
    more = f"\n  … and {len(lines) - 15} more" if len(lines) > 15 else ""
    return f"{summary}\n  {detail}{more}"


# --- main -------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--osint", type=Path, default=DEFAULT_OSINT)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    osint: Path = args.osint
    if not (osint / ".git").exists():
        print(f"not a git repo: {osint}", file=sys.stderr)
        return 2

    new_sha = git(osint, "rev-parse", "HEAD")
    old_sha = BUILT_FROM.read_text(encoding="utf-8").strip() if BUILT_FROM.exists() else None

    print(f"OSINT   {osint}")
    print(f"HEAD    {new_sha[:12]}  {git(osint, 'log', '-1', '--format=%s', new_sha)}")
    print(f"built   {old_sha[:12] if old_sha else '(never)'}")

    # We read committed state, so uncommitted work is invisible by design —
    # say so rather than let it look like the pull missed something.
    dirty = git(osint, "status", "--porcelain", "--", "outputs/")
    if dirty:
        n = len(dirty.splitlines())
        print(f"note    {n} uncommitted change(s) in OSINT outputs/ — not pulled")

    if old_sha == new_sha and not args.force:
        print("\nAlready at HEAD. Nothing to do.")
        return 0

    print(f"\nchange  {describe_change(osint, old_sha, new_sha)}")

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return 0

    staging = extract_outputs(osint, new_sha)
    try:
        leak_gate(staging)
    except Leak as exc:
        shutil.rmtree(staging, ignore_errors=True)
        print(f"\n{exc}", file=sys.stderr)
        return 1
    print("gate    passed")

    swap(staging)
    BUILT_FROM.write_text(new_sha + "\n", encoding="utf-8")

    faults = verify(osint, new_sha)
    if faults:
        print("\nverify FAILED — upstream/ does not match OSINT outputs/:",
              file=sys.stderr)
        for f in faults:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("verify  upstream/ matches OSINT outputs/ exactly")

    files = sum(1 for p in UPSTREAM.rglob("*") if p.is_file())
    size = sum(p.stat().st_size for p in UPSTREAM.rglob("*") if p.is_file())
    print(f"pulled  {files} files, {size / 1e6:.1f} MB → upstream/")
    print(f"        BUILT-FROM = {new_sha}")

    if args.commit:
        subject = f"upstream: pull outputs/ at OSINT {new_sha[:12]}"
        subprocess.run(["git", "-C", str(CORPUS), "add", "-A", "upstream"], check=True)
        subprocess.run(["git", "-C", str(CORPUS), "commit", "-q", "-m", subject], check=True)
        print(f"commit  {subject}")
    else:
        print("\nNot committed. To commit:")
        print(f'  git add upstream && git commit -m "upstream: pull outputs/ at OSINT {new_sha[:12]}"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
