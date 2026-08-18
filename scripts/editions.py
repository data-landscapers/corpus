#!/usr/bin/env python3
"""editions.py — what an edition is called, when a new one is cut, and how one is published.

`documentation/design.md` §9. An edition is a dated, retained, immutable artefact: it is cut
when the content changes rather than when a build runs, it is never rewritten after publication,
and **no undated download URL exists at all** — the HTML page is the stable address a reader
browses, and every download it offers is dated.

This is a module rather than a section of `render.py` because three scripts publish editions:
`render.py` the dated PDFs, `country.py` the per-country finance CSVs and their field
dictionaries, `finance.py` the cross-country CSV. A filename grammar with one writer and
several readers is the arrangement that drifts, and it had already drifted before the `-2`
suffix existed — `country.py` and `topic-page.py` each held their own idea of what an edition
looked like, and both were wrong about it in ways that showed only as a page quietly offering
a superseded file.

**Not everything downloadable is an edition.** The catalogue is not *(Bill, 2026-08-18)*: it is
a browse index over other people's records, regenerated wholesale, and nobody cites it as of a
date. The finance CSVs are, because they are a compiled finding of ours that a reader may quote.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

# **One grammar for an edition.** The date, and a same-day sequence where a second edition was
# cut on the same day (§9). `STEM_EDITION` is anchored at the end so the monthly and progress
# names that still carry a period from before the 2026-08-13 rename —
# `KEN-monthly-2026-07-2026-08-05` — yield the edition rather than the window.
EDITION = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})(?:-(?P<seq>\d+))?$")
STEM_EDITION = re.compile(r"-(\d{4}-\d{2}-\d{2}(?:-\d+)?)$")


def edition_of(stem: str) -> str | None:
    """The edition a rendered filename carries, or None if it carries none."""
    m = STEM_EDITION.search(stem)
    return m.group(1) if m else None


def edition_key(edition: str) -> tuple[str, int]:
    """Sort key for an edition: the date, then the same-day sequence as a **number**.

    Sorting the strings gets this wrong in both directions, and silently. In a filename
    `-2026-08-18-2.pdf` sorts *before* `-2026-08-18.pdf`, because `-` precedes `.`, so taking
    the last name of a sorted list hands back the older edition. In an edition string `-10`
    sorts before `-2`. Either way the page offers a superseded file and looks entirely correct
    doing it."""
    m = EDITION.match(edition or "")
    return (m.group("date"), int(m.group("seq") or 1)) if m else ("", 0)


def editions_of(out_dir: Path, stem: str, ext: str) -> list[tuple[tuple[str, int], Path]]:
    """Every retained edition of one document, oldest first.

    **The name is checked exactly, not matched by prefix.** `KEN-nonstate-*` also matches
    `KEN-nonstate-fields-2026-08-18.csv`, which is a different document that happens to begin
    with this one's name — and its editions are its own. Stripping the edition and comparing
    what is left is the only test that separates them, and getting it wrong would have the
    finance CSV take its edition from its own field dictionary."""
    found = []
    for f in out_dir.glob(f"{stem}-*{ext}"):
        edition = edition_of(f.stem)
        if edition is None or f.stem != f"{stem}-{edition}":
            continue
        found.append((edition_key(edition), f))
    return sorted(found)


def latest(out_dir: Path, stem: str, ext: str) -> Path | None:
    """The newest retained edition of one document, or None."""
    found = editions_of(out_dir, stem, ext)
    return found[-1][1] if found else None


def next_edition(out_dir: Path, stem: str, today: str, ext: str = ".pdf") -> str:
    """Today's edition for this document — suffixed if today's name is already taken.

    **The first edition of a day is unsuffixed and the second takes `-2`** (§9). Two editions in
    one day is a normal occurrence rather than an edge case: SWEEP-CYCLE normally runs overnight,
    but a session may be run during the day to force an update on a live issue *(Bill,
    2026-08-06)*.

    **The first is never renamed when the second appears.** Making it `-1` for symmetry would
    break every URL already handed out, which is the one thing §9 exists to prevent — so the
    names are asymmetric, and since most days have one edition most of them stay clean.

    Existence on disk is the test, not a count kept somewhere. The retained artefacts *are* the
    record of which names are spoken for."""
    if not (out_dir / f"{stem}-{today}{ext}").exists():
        return today
    n = 2
    while (out_dir / f"{stem}-{today}-{n}{ext}").exists():
        n += 1
    return f"{today}-{n}"


def retire_undated(out_dir: Path, stem: str, ext: str) -> Path | None:
    """Remove the undated predecessor of a now-dated artefact. Returns it, or None.

    §9 allows no undated download URL, and until 2026-08-18 the finance CSVs were published at
    one. `site/` is generated but never purged (RENDER.md), so a file that simply stops being
    written stays there and goes on being served for ever.

    **Deleting it does break a URL that was published, and that is the lesser of the two
    breakages.** An undated URL invites a citation that changes underneath the person who made
    it — the precise failure §9 exists to prevent — and leaving the file in place would keep
    that invitation open indefinitely, against a handful of days in which the site has served
    these files at all."""
    stale = out_dir / f"{stem}{ext}"
    if stale.exists():
        stale.unlink()
        return stale
    return None


def publish(data: bytes, out_dir: Path, stem: str, ext: str = ".csv",
            today: str | None = None) -> tuple[Path, bool]:
    """Publish `data` as a dated edition of `{stem}{ext}`. Returns `(path, minted)`.

    **A new edition is cut only when the bytes have moved**, which is §9's rule applied to an
    artefact that is published byte-for-byte. The comparison can be direct here, unlike the PDF
    case: a PDF carries its build date inside it and so differs from its predecessor on every
    render, which is why `render.py` has to compare a digest of the *source* instead. A CSV
    written from unchanged data is the same file.

    **The retained editions are their own record**, so nothing has to be kept beside them. That
    also means the gate cannot drift out of step with what is actually published — if the file
    is there, its bytes are the truth about what was published under that name."""
    out_dir.mkdir(parents=True, exist_ok=True)
    current = latest(out_dir, stem, ext)
    if current is not None and current.read_bytes() == data:
        retire_undated(out_dir, stem, ext)
        return current, False

    edition = next_edition(out_dir, stem, today or date.today().isoformat(), ext)
    path = out_dir / f"{stem}-{edition}{ext}"
    path.write_bytes(data)
    retire_undated(out_dir, stem, ext)
    return path, True
