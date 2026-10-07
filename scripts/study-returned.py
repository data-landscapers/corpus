#!/usr/bin/env python3
r"""study-returned.py — what ingest admitted of a study's handover, and whether Phase 2 may open.

    python scripts/study-returned.py health --note 231

`maturity/documentation/maturity-study-method.md` §6. Corpus hands candidates over and never
writes to `raw/`; **a found document counts only once it has come back through ingest**, so
between the phases the one question is which did.

**The gate comes first, and the script refuses rather than reports when it is shut.** Phase 2
waits on two things, both read from where they are written:

1. the delivery note has left `notes-for-osint.md` for the resolved file, and
2. the mirror's `cycle-manifest.json` was written after the commit that moved it, so the
   copy of `lookups/` being read is one made after ingest finished with the batch.

**The second is a clock on the wrong event when CORPUS commits OSINT's move**, which it does
on its own next visit and so after the mirror was written. A mirror older than that commit
still opens the gate when it already holds the batch: at least half the staged URLs resolve
in its lookups, which a copy made before the ingest cannot show, because staging screened
every one of them as unheld.

A run before either holds would mark every document `not-returned` against an index that
could not yet contain it, and the gaps would be searched again.

Then every row of `maturity/{id}/search/staged.csv` is looked up by URL, normalised as
`status-stage.py` normalises it (the index holds addresses percent-decoded), in the
mirror's `lookups/raw-url-index.csv` and `lookups/rejected-urls.csv`, and
`maturity/{id}/search/returned.csv` records the outcome:

- `admitted`     — held; `slug` names the record, which joins the Phase 2 reading;
- `rejected`     — ingest declined it; `reason` is ingest's;
- `not-returned` — in neither. Not held, and its gap stands.

Exit: 0 written, 2 the gate is shut or a file is missing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osint_lib   # noqa: E402
import status_lib  # noqa: E402
import study_lib   # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "lint_prepared", os.path.join(os.path.dirname(os.path.abspath(__file__)), "lint-prepared.py"))
lint_prepared = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint_prepared)

_spec = importlib.util.spec_from_file_location(
    "status_stage", os.path.join(os.path.dirname(os.path.abspath(__file__)), "status-stage.py"))
ss = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ss)

URL_INDEX = os.path.join(osint_lib.MIRROR, "lookups", "raw-url-index.csv")
REJECTED = os.path.join(osint_lib.MIRROR, "lookups", "rejected-urls.csv")


def moved_at(note: str, share: str) -> dt.datetime | None:
    """When the note's heading first entered the resolved file, from the share's own history."""
    pattern = rf"^(\*\*{note}\*\*|#+ {note}\.)"
    try:
        out = subprocess.run(
            ["git", "-C", share, "log", "--format=%ct", "-G", pattern, "--",
             lint_prepared.NOTES_RESOLVED],
            capture_output=True, text=True, check=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return None
    return dt.datetime.fromtimestamp(int(out[-1]), dt.timezone.utc) if out else None


def manifest_written(path: str) -> dt.datetime | None:
    try:
        with open(path, encoding="utf-8") as fh:
            stamp = json.load(fh).get("written_utc", "")
        return dt.datetime.strptime(stamp, osint_lib.TS).replace(tzinfo=dt.timezone.utc)
    except (OSError, ValueError):
        return None


def gate(note: str, share: str, manifest: str, resolved: float = 0.0) -> str:
    """Why Phase 2 may not open yet, or an empty string. `resolved` is the share of staged
    URLs the mirror's lookups already hold."""
    read = lint_prepared._read
    state = lint_prepared.note_state(note, read(os.path.join(share, lint_prepared.NOTES)),
                                     read(os.path.join(share, lint_prepared.NOTES_RESOLVED)))
    if state != "closed":
        return f"notes-for-osint {note} is {state}, so the handover has not been worked"
    moved, written = moved_at(note, share), manifest_written(manifest)
    if moved is None:
        return f"the share's history does not show when note {note} was moved to the resolved file"
    if written is None:
        return f"the mirror's cycle manifest cannot be read at {manifest}"
    if written <= moved and resolved < 0.5:
        return (f"the mirror was last written {written:%Y-%m-%d %H:%M} UTC and the note moved "
                f"{moved:%Y-%m-%d %H:%M} UTC, so this copy of lookups/ predates the ingest")
    return ""


def outcomes(staged: list[dict], held: dict[str, str], rejected: dict[str, str]) -> list[dict]:
    out = []
    for row in staged:
        key = ss.norm(row.get("url", ""))
        if key in held:
            slug = os.path.splitext(os.path.basename(held[key]))[0]
            out.append({**row, "outcome": "admitted", "slug": slug, "reason": ""})
        elif key in rejected:
            out.append({**row, "outcome": "rejected", "slug": "", "reason": rejected[key]})
        else:
            out.append({**row, "outcome": "not-returned", "slug": "", "reason": ""})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="What ingest admitted of a study's handover.")
    ap.add_argument("study")
    ap.add_argument("--note", required=True, help="the notes-for-osint number that announced the delivery")
    ap.add_argument("--share", default=status_lib.EXCHANGE)
    a = ap.parse_args(argv)

    search = os.path.join(study_lib.study_dir(a.study), "search")
    staged = study_lib.read_csv(os.path.join(search, "staged.csv"))
    if not staged:
        print(f"study-returned: no rows in {os.path.join(search, 'staged.csv')}.")
        return 2
    index, declined = study_lib.read_csv(URL_INDEX), study_lib.read_csv(REJECTED)
    rows = outcomes(staged, {r["url_normalized"]: r["file"] for r in index},
                    {r["url_normalized"]: r.get("reason", "") for r in declined})
    resolved = sum(1 for r in rows if r["outcome"] != "not-returned") / len(rows)
    shut = gate(a.note, a.share, osint_lib.MANIFEST, resolved)
    if shut:
        print(f"study-returned: Phase 2 waits - {shut}.")
        return 2
    if not index:
        print(f"study-returned: the URL index is empty or missing at {URL_INDEX}.")
        return 2

    study_lib.write_csv(os.path.join(search, "returned.csv"), study_lib.RETURNED_FIELDS, rows)
    count = {k: sum(1 for r in rows if r["outcome"] == k)
             for k in ("admitted", "rejected", "not-returned")}
    print(f"study-returned: {a.study} - {len(rows)} handed over: {count['admitted']} admitted, "
          f"{count['rejected']} rejected, {count['not-returned']} not returned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
