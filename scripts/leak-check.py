#!/usr/bin/env python3
"""leak-check.py — the source-body leak gate (F10).

    python scripts/leak-check.py outputs         # gate outputs/ (BUILD, before commit)
    python scripts/leak-check.py site outputs     # gate both (RENDER, before deploy)
    exit 0 = clean, exit 1 = a body was found (and the run must stop)

**Why this exists.** `documentation/design.md` §8 makes this the one check that
*fails* the build rather than warning: a verbatim source body must never reach
this repo's history, because a leak into a public repo is permanent. It used to
live inside `scripts/pull.py` (the pre-migration pull from OSINT). The migration
retired the pull but not the risk — Corpus now **authors** `outputs/` itself, and
a bug in a compiler could still copy a body — so the gate is rehomed here, as its
own runnable thing, and each job invokes it before it commits or publishes.

`outputs/` holds metadata and compiled prose *by construction*, so this should
never fire. That is exactly why it fails the run: a firing means a compiler is
wrong, and we want to hear about it loudly, before the commit, not after.

Detection (lifted unchanged from the retired pull.py gate):
  - any column/key named like a body (`body`, `text`, `content`, …) — immediate fail;
  - any field longer than a length cap (1000 chars; 8000 for known prose columns
    like `description`/`note`) — the backstop for a body the names miss;
  - a markdown file whose frontmatter declares `type: source` or `body_completeness`;
  - any path under `raw/` — a source page must never be here.
Adding a prose column to the higher cap is a deliberate edit, which is the point:
a new prose column should have to be admitted, not discovered.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path

BODY_COLUMNS = {"body", "text", "content", "full_text", "fulltext",
                "article", "raw_body", "verbatim", "extract"}
MAX_FIELD = 1000
PROSE_COLUMNS = {"description", "note", "position_end", "summary"}
MAX_PROSE_FIELD = 8000
csv.field_size_limit(10 ** 8)


def cap_for(name: str) -> int:
    return MAX_PROSE_FIELD if name.strip().lower() in PROSE_COLUMNS else MAX_FIELD


def frontmatter(text: str) -> list[str]:
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    return text[3:end].splitlines() if end != -1 else []


def check_markdown(path: Path, rel: str) -> list[str]:
    faults = []
    for line in frontmatter(path.read_text(encoding="utf-8", errors="replace")):
        key, _, val = line.partition(":")
        if key.strip() == "type" and val.strip() == "source":
            faults.append(f"{rel}: frontmatter declares `type: source`")
        if key.strip() == "body_completeness":
            faults.append(f"{rel}: frontmatter carries `body_completeness`")
    return faults


def check_csv(path: Path, rel: str) -> list[str]:
    with path.open(encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            return []
        named = [c for c in header if c.strip().lower() in BODY_COLUMNS]
        if named:
            return [f"{rel}: carries body column(s) {', '.join(named)}"]
        for n, row in enumerate(reader, start=2):
            for col, value in zip(header, row):
                cap = cap_for(col)
                if len(value) > cap:
                    return [f"{rel}: row {n}, column `{col}` is {len(value)} chars (cap {cap})"]
    return []


def check_json(path: Path, rel: str) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return []
    faults: list[str] = []

    def walk(node, trail, key=""):
        if faults:
            return
        if isinstance(node, str):
            cap = cap_for(key)
            if len(node) > cap:
                faults.append(f"{rel}: `{trail}` is {len(node)} chars (cap {cap})")
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
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if len(line) > MAX_FIELD:
            return [f"{rel}: line {n} is {len(line)} chars (cap {MAX_FIELD})"]
    return []


CHECKERS = {".md": check_markdown, ".csv": check_csv, ".json": check_json, ".txt": check_text}


def scan(root: Path) -> list[str]:
    """Every source-body fault under `root`."""
    faults: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if "raw/" in rel or rel.startswith("raw"):
            faults.append(f"{rel}: path is under raw/")
            continue
        check = CHECKERS.get(path.suffix.lower())
        if check:
            faults.extend(check(path, rel))
    return faults


def main() -> int:
    roots = [Path(a) for a in sys.argv[1:]] or [Path("outputs")]
    faults: list[str] = []
    for root in roots:
        if not root.exists():
            print(f"leak-check: {root} does not exist — skipping")
            continue
        faults += scan(root)
    if faults:
        print(f"LEAK GATE FAILED — {len(faults)} problem(s); do NOT commit/publish:")
        for f in faults[:40]:
            print("  " + f)
        return 1
    print(f"leak gate: clean ({', '.join(str(r) for r in roots)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
