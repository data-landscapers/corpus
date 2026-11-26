r"""maturity_words.py — the maturity pages' apparatus words, in one place.

Strategic review 7, R136, after Bill's ruling R130 (2026-10-27). Every maturity writer imports its
closing labels and the map's legend words from here, so the next rename is one edit and no study
night writes the old words back. The `study-*-write.py` writers and `study_figure.py` also pass the
page and the short line through `rewrite()` before writing, because a cell's `gaps` text comes from
stage files written before the ruling, and from hand-written cells.

**`rewrite()` is R130 as a substitution**: *Not held* → *Not found*; *Noted, not assessed* →
*Also on file*; *nothing held*, *none held*, *no source held*, *evidence held* → *found*; *no X is
held* → *no X has been found*; *X is not known* → *no source found says whether …* or *no source
found reports X*. A match stays inside one sentence, one line and one table cell, and *where X is
held* means stored and is left. It is idempotent, and `lint-prose.py`'s `words` check is its test:
what it leaves behind is drafted prose for the nightly 4c pass, not a stock line.

    python scripts/maturity_words.py PATH ...     # rewrite files in place; prints the count changed
"""
from __future__ import annotations

import re
import sys

NOT_FOUND = "Not found"
ALSO_ON_FILE = "Also on file"
NOT_FOUND_LABEL = f"***{NOT_FOUND}***"
ALSO_ON_FILE_LABEL = f"***{ALSO_ON_FILE}***"
CLOSING = (ALSO_ON_FILE_LABEL, NOT_FOUND_LABEL)
NONE_FOUND = "None found."
NOTHING_FOUND = "Nothing found."
NOTHING_YET = "Nothing found for this country yet."

# The map legend, in maturity.json and on the methodology page (R130 as reissued).
UNPLACED_DESC = "Not staged: evidence found that meets no rung."
BLANK_DESC = "Not staged: nothing found states any fact the ladder tests."

_ASKS = r"(?:[Ww]hether|[Hh]ow|[Ww]ho|[Ww]hich|[Ww]hat|[Ww]hen|[Ww]here)"
_SPAN = r"[^.;\n|]"
_HELD = r"(?:(?!\bwhere\b)" + _SPAN + r")"
_RULES = [
    (re.compile(r"\bNot held\b"), NOT_FOUND),
    (re.compile(r"\bNoted, not assessed\b"), ALSO_ON_FILE),
    (re.compile(r"\b([Nn])(one|othing) held\b"), r"\1\2 found"),
    (re.compile(r"\b([Ee]vidence|[Ss]ources?) held\b"), r"\1 found"),
    (re.compile(r"(?i)(\bno\b" + _HELD + r"{0,80}?\b)is held\b"), r"\1has been found"),
    (re.compile(r"(?i)(\bno\b" + _HELD + r"{0,80}?\b)are held\b"), r"\1have been found"),
]
_ASKED = re.compile(r"\b(" + _ASKS + r"\b" + _SPAN + r"*?) (?:is|are) not known\b")
_NAMED_AFTER = re.compile(r"(?:(?<=; )|(?<= but ))(" + _SPAN + r"+?) (?:is|are) not known\b")
_NAMED_START = re.compile(r"(?:(?<=\. )|^)([A-Z]" + _SPAN + r"*?) (?:is|are) not known\b", re.M)


def _asked(m: re.Match) -> str:
    clause = m.group(1)
    lead = "No" if clause[0].isupper() else "no"
    return f"{lead} source found says {clause[0].lower()}{clause[1:]}"


def _lower_first(s: str) -> str:
    return s[0].lower() + s[1:] if len(s) > 1 and s[1].islower() else s


def rewrite(text: str) -> str:
    """R130's substitution over `text`; text already in the new words passes through unchanged."""
    for rx, new in _RULES:
        text = rx.sub(new, text)
    text = _ASKED.sub(_asked, text)
    text = _NAMED_AFTER.sub(lambda m: "no source found reports " + m.group(1).rstrip(","), text)
    return _NAMED_START.sub(
        lambda m: "No source found reports " + _lower_first(m.group(1).rstrip(",")), text)


# ---------------------------------------------------------------------------
# The paragraph (strategic review 8, R153 and R162)
# ---------------------------------------------------------------------------
# *(Bill, 2026-11-26.)* One paragraph an indicator, under its stage: what exists, what changed in
# the last twelve months, what has not been found said as what the next stage would need. 60 to
# 130 words (R153 ruled 110; Bill raised the cap to 130 when R162 ran). The labelled evidence of
# `{ISO3}.md` stays as written and renders in a closed fold under it.
#
# The paragraphs live in `outputs/maturity/{id}/paragraphs.csv`, not in `{ISO3}.md`, so the
# writers that rebuild a cell's evidence cannot drop them. A row records the stage and a digest
# of the section it was written from. **A paragraph is shown only while its stage still holds**;
# when the section moves under it, it is stale and is rewritten by the next 4c or rebuild night
# (`scripts/maturity-paragraph.py`), and shown until then. The brief is
# `maturity/documentation/paragraph-brief.md`.

PARAGRAPH_FILE = "paragraphs.csv"
PARAGRAPH_FIELDS = ["iso3", "indicator_id", "stage", "digest", "written", "paragraph"]
PARAGRAPH_WORDS = (60, 130)
EVIDENCE_FOLD = "Show the evidence"
STAGE_NAMES = {1: "Absent", 2: "Preparing", 3: "Establishing", 4: "Operating", 5: "Mature"}


def digest(section: str) -> str:
    """A section's fingerprint, blind to line endings and trailing space."""
    import hashlib
    norm = "\n".join(ln.rstrip() for ln in section.replace("\r\n", "\n").strip().splitlines())
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]


def read_paragraphs(issued) -> dict:
    """{(iso3, indicator_id): row} from a study's `paragraphs.csv`; empty when there is none."""
    import csv
    import os
    path = os.path.join(str(issued), PARAGRAPH_FILE)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8", newline="") as fh:
        return {(r["iso3"], r["indicator_id"]): r for r in csv.DictReader(fh)}


def write_paragraphs(issued, rows: dict) -> None:
    import csv
    import os
    path = os.path.join(str(issued), PARAGRAPH_FILE)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=PARAGRAPH_FIELDS, lineterminator="\n")
        w.writeheader()
        for key in sorted(rows):
            w.writerow({k: rows[key].get(k, "") for k in PARAGRAPH_FIELDS})


def paragraph_state(row: dict | None, stage: str, section: str) -> str:
    """`fresh`, `stale` (section moved, stage holds: still shown) or `missing` (none, or the stage
    moved under it: not shown)."""
    if not row or row.get("stage") != stage or not row.get("paragraph", "").strip():
        return "missing"
    return "fresh" if row.get("digest") == digest(section) else "stale"


def shown_paragraph(row: dict | None, stage: str, section: str) -> str:
    """The paragraph to print, or '' when there is none whose stage still holds."""
    return row["paragraph"].strip() if paragraph_state(row, stage, section) != "missing" else ""


def main(paths: list[str]) -> int:
    changed = 0
    for p in paths:
        with open(p, encoding="utf-8", newline="") as fh:
            old = fh.read()
        new = rewrite(old)
        if new != old:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
            changed += 1
    print(f"{changed} of {len(paths)} files rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
