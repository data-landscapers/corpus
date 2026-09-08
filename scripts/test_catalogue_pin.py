#!/usr/bin/env python3
"""test_catalogue_pin.py — the catalogue is the pin, and it still catches what it must.

    python scripts/test_catalogue_pin.py

`report-render._assert_catalogue_current` refuses to resolve citations against a
catalogue that `raw/` has moved past. On 2026-09-08 it stopped treating an **added**
record as a reason to stop — a record the catalogue does not list resolves nothing, and
nothing in `outputs/` can cite a source that did not exist when the prose was written —
so that a cycle run while OSINT is working beside it finishes instead of racing.

That is a loosening in one direction, which is exactly the kind of change that wants
holding down. What this asserts is the whole of the contract:

- a record **deleted** since the build still stops the run;
- a record **edited** since the build still stops the run;
- a record **added** since the build does not, and is reported;
- and a mixed case — one added, one deleted — still stops, because the tree then holds
  the same number of files it held at the build and the addition must not be allowed to
  make up the count the deletion took away.

That last one is the failure a relaxed count of `raw/` would have, and it is why the
check counts the records at or below the stamp's own high-water mark rather than
counting everything in the tree.

Runs on a temporary tree of its own and touches nothing real.
"""
from __future__ import annotations
import os, sys, tempfile
from pathlib import Path

CORPUS = Path(__file__).resolve().parent
sys.path.insert(0, str(CORPUS))
import vault_lib  # noqa: E402


def make_tree(root: Path, n: int, mtime: int):
    raw = root / "raw" / "2026"
    raw.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        p = raw / f"2026-01-{i + 1:02d}-record.md"
        p.write_text(f"record {i}\n", encoding="utf-8")
        os.utime(p, (mtime, mtime))
    return raw


def state(root: Path, since: int):
    """What the guard computes: (records at or below the pin, newest of them, arrived after)."""
    return vault_lib.raw_md_state(root=str(root), since=since)


def main() -> int:
    fails = []
    PIN = 1_700_000_000                     # the stamp's high-water mark
    LATER = PIN + 60

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        raw = make_tree(root, 5, PIN)

        files, newest, added = state(root, PIN)
        if (files, added) != (5, 0):
            fails.append(f"an untouched tree should read 5 records and 0 added, got {files}/{added}")
        if newest != PIN:
            fails.append(f"the newest of the pinned records should be the pin, got {newest}")

        # --- an addition is ignored -----------------------------------------
        new = raw / "2026-02-01-arrived-later.md"
        new.write_text("later\n", encoding="utf-8")
        os.utime(new, (LATER, LATER))
        files, newest, added = state(root, PIN)
        if files != 5:
            fails.append(f"an added record must not change the pinned count, got {files}")
        if added != 1:
            fails.append(f"an added record must be reported, got added={added}")
        if newest > PIN:
            fails.append("an added record must not move the newest of the pinned population")

        # --- an edit stops the run ------------------------------------------
        edited = raw / "2026-01-01-record.md"
        os.utime(edited, (LATER, LATER))
        files, _, added = state(root, PIN)
        if files != 4:
            fails.append(f"an edited record must leave the pinned population, got {files}")
        if added != 2:
            fails.append(f"an edited record reads as arrived-after, got added={added}")
        os.utime(edited, (PIN, PIN))                    # put it back

        # --- a deletion stops the run, and an arrival cannot mask it ---------
        # This is the whole reason the count is taken over the *pinned* population
        # rather than over the tree. Five records at the build, one deleted and one
        # arrived since: the tree holds five files again, so a naive count of `raw/`
        # comes out equal to the stamp and passes — while the catalogue still lists a
        # slug the base no longer holds, which is the dangling citation the check was
        # written for.
        (raw / "2026-01-02-record.md").unlink()
        files, _, added = state(root, PIN)
        total = files + added
        if total != 5:
            fails.append(f"the tree should hold 5 files again — a deletion masked by an "
                         f"arrival — got {total}")
        if files != 4:
            fails.append(f"the masked deletion must still read 4 pinned records, got {files}")
        if added != 1:
            fails.append(f"the arrival should be reported as 1, got {added}")

        # --- and the old two-value call is untouched -------------------------
        # `build-catalogue.py` calls it without `since` to write the stamp in the first
        # place, so the pair must keep counting the whole tree.
        pair = vault_lib.raw_md_state(root=str(root))
        if len(pair) != 2:
            fails.append(f"raw_md_state() without `since` must still return a pair, got {pair!r}")
        if pair[0] != 5:
            fails.append(f"the pairwise call counts the whole tree, got {pair[0]}")

    if fails:
        print(f"test_catalogue_pin: FAILED — {len(fails)} problem(s)")
        for f in fails:
            print(f"    {f}")
        return 1
    print("test_catalogue_pin: ok — added records are ignored, edits and deletions still stop "
          "the run, and an arrival cannot make up a deletion's count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
