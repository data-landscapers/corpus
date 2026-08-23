#!/usr/bin/env python3
r"""bulletin_editions.py — the bulletin's mini-archive: `site/bulletin/editions.json`.

`documentation/bulletin-archive.md` is the design and the reasoning. This is the state it
describes, and it has two writers — `render.py` when it cuts a bulletin PDF, and
`prune-editions.py` when it deletes one — which is exactly why the rules live in one module
rather than in both.

**The archive is a listing, not a location.** The PDFs never move: they stay at
`site/bulletin/corpus-bulletin-YYYY-MM-DD[-N].pdf`, the URL their own colophon names. An
`archive/` folder would relocate files that are already published and break every downloaded
copy's account of where it came from. So the only new state is this manifest.

    {"retention_days": 7,
     "editions": [{"edition": "2026-08-22-6", "file": "corpus-bulletin-2026-08-22-6.pdf",
                   "compiled": "2026-08-22 09:35", "items": 25, "bytes": 302103}]}

Newest first. `file` is relative to the manifest's own directory, so the picker needs no base
URL and the listing is correct whether it is served from the site root or opened locally.

**The three facts the picker shows are only in hand at the moment the PDF is cut** — `compiled`
and `items` come from the frontmatter the renderer has just read, and the edition is the one it
is minting. None survives into the PDF, so this cannot be a script that walks the directory
afterwards; it has to be written by the run that mints.

**Every write rebuilds the list.** Appending would let it drift from the directory it describes,
and the two ways it drifts are both silent: an entry for a file somebody deleted by hand, and an
entry for a file a half-finished prune removed. `rebuild()` drops any entry with no file behind
it, so the picker cannot offer a 404 for longer than one render.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import editions  # noqa: E402

MANIFEST = "editions.json"

# **A week, and the page says so** (`documentation/bulletin-archive.md`). One number, read by
# the renderer for the colophon's `Retention` row and by the pruner for the deletion it acts on,
# so the promise on the page and the rule in the script cannot disagree.
RETENTION_DAYS = 7


def manifest_path(out_dir: Path) -> Path:
    return Path(out_dir) / MANIFEST


def load(out_dir: Path) -> dict:
    """The manifest, or an empty one. **Malformed reads as empty**, never raises: this is a
    convenience listing over files that are all still reachable by URL, and a render that dies
    because a JSON file has a stray comma in it has turned a cosmetic fault into an outage."""
    path = manifest_path(out_dir)
    if not path.exists():
        return {"retention_days": RETENTION_DAYS, "editions": []}
    try:
        held = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(held, dict) or not isinstance(held.get("editions"), list):
            raise ValueError("not a manifest")
        return held
    except (OSError, ValueError):
        return {"retention_days": RETENTION_DAYS, "editions": []}


def expires_on(edition: str, retention_days: int = RETENTION_DAYS) -> str:
    """The date an edition is kept until — `edition_date + retention_days`.

    **The colophon names the date, not the interval** *(design note)*. *Kept for a week* asks a
    reader to remember when they downloaded it; a date needs nothing but a calendar. It is the
    same arithmetic the pruner does, from the same constant, so the page cannot promise one
    thing while the script does another."""
    day = editions.edition_key(edition)[0] or edition[:10]
    return (dt.date.fromisoformat(day) + dt.timedelta(days=retention_days)).isoformat()


def within_window(edition: str, today: str, retention_days: int = RETENTION_DAYS) -> bool:
    """**Measured on the edition date, not on supersession** *(design note)*. A bulletin is
    superseded within hours by its own next cut, so a lag measured from that would give each
    edition a week — but a different week each, and never the week the colophon named."""
    return expires_on(edition, retention_days) >= today


def rebuild(entries: list[dict], out_dir: Path, today: str,
            retention_days: int = RETENTION_DAYS, pending: str = "") -> list[dict]:
    """The listing as it should be: on disk, inside the window, newest first, no duplicates.

    `pending` names one edition exempt from the existence test — the one the renderer is minting
    right now, whose PDF WeasyPrint has not written yet. It is an argument rather than an
    inferred special case because the exemption has to end: on the next run that edition is an
    ordinary entry and is dropped if its file never appeared.

    Sorted through `editions.edition_key` and never as a string — `-10` sorts before `-2`, and
    that module exists because getting this wrong hands back the wrong edition while looking
    entirely correct."""
    out_dir = Path(out_dir)
    seen: dict[str, dict] = {}
    for e in entries:
        edition, name = str(e.get("edition", "")), str(e.get("file", ""))
        if not edition or not name:
            continue
        if edition != pending and not (out_dir / name).exists():
            continue                                  # self-healing: no file, no entry
        if not within_window(edition, today, retention_days):
            continue
        seen[edition] = {"edition": edition, "file": name,
                         "compiled": str(e.get("compiled", "")),
                         "items": int(e.get("items") or 0),
                         "bytes": int(e.get("bytes") or 0)}
    # **A file on disk that nothing listed is the same drift as an entry with no file**, and the
    # listing should heal both ways. It matters at the two moments the manifest is furthest from
    # the truth: the first run after the archive ships, when a week of editions is already
    # published and none of them is recorded, and any run after a PDF is restored by hand.
    #
    # Only the edition is adopted, because only the edition is recoverable — it is in the
    # filename. `compiled` and `items` lived in the frontmatter of the run that cut the file and
    # are in no artefact afterwards, which is why a full listing cannot be rebuilt by walking
    # the directory. So an adopted entry carries what is known and nothing else, and `label()`
    # prints the date alone rather than a fabricated count.
    for f in sorted(out_dir.glob("*.pdf")):
        edition = editions.edition_of(f.stem)
        if not edition or edition in seen:
            continue
        if not within_window(edition, today, retention_days):
            continue
        seen[edition] = {"edition": edition, "file": f.name, "compiled": "", "items": 0,
                         "bytes": f.stat().st_size}

    return sorted(seen.values(),
                  key=lambda e: editions.edition_key(e["edition"]), reverse=True)


def refreshed(out_dir: Path, today: str, adding: dict | None = None,
              retention_days: int = RETENTION_DAYS) -> list[dict]:
    """What the listing becomes, with `adding` folded in. Computes; writes nothing.

    Separate from `save()` because the renderer needs the list *before* the PDF exists — it
    builds the page from it — and must not persist a claim about a file WeasyPrint has not
    written yet."""
    entries = list(load(out_dir).get("editions", []))
    pending = ""
    if adding:
        pending = str(adding.get("edition", ""))
        entries = [e for e in entries if e.get("edition") != pending] + [adding]
    return rebuild(entries, out_dir, today, retention_days, pending=pending)


def save(out_dir: Path, entries: list[dict],
         retention_days: int = RETENTION_DAYS) -> Path:
    """Write the manifest. `newline=""` for the reason every writer in this repo now carries it:
    without it Windows rewrites every line and the file differs from the one in git on all of
    them, in both directions, on every run."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = manifest_path(out_dir)
    body = json.dumps({"retention_days": retention_days, "editions": entries},
                      indent=2, ensure_ascii=False) + "\n"
    path.write_text(body, encoding="utf-8", newline="")
    return path


def record_cut(out_dir: Path, edition: str, filename: str, compiled: str, items: int,
               today: str, retention_days: int = RETENTION_DAYS) -> list[dict]:
    """Fold a freshly cut edition into the manifest and persist it. Called after the PDF is on
    disk, so the size is real."""
    out_dir = Path(out_dir)
    pdf = out_dir / filename
    entry = {"edition": edition, "file": filename, "compiled": compiled,
             "items": int(items or 0),
             "bytes": pdf.stat().st_size if pdf.exists() else 0}
    entries = refreshed(out_dir, today, adding=entry, retention_days=retention_days)
    save(out_dir, entries, retention_days)
    return entries


def missing(out_dir: Path) -> list[str]:
    """Entries in the manifest with no file behind them — RENDER's assertion.

    A derived listing is only safe to trust while something notices when it stops matching what
    it describes; this is the same reasoning `lint-shared-assets.py` was built on."""
    out_dir = Path(out_dir)
    return [str(e.get("file", "")) for e in load(out_dir).get("editions", [])
            if not (out_dir / str(e.get("file", ""))).exists()]


def label(entry: dict) -> str:
    """`Saturday 22 August, 09:35 — 25 entries`.

    The time is the `compiled` stamp, which is **OSINT's last ingest and not our build clock**
    (`documentation/bulletin.md`) — how late the newest thing in that cut is, which is the
    question a reader choosing between two cuts of the same day is actually asking. It is
    deliberately not the document's byline: that names `collected_to:`, when collection stopped,
    which is the different question *how recent is any of this* (Bill, 2026-08-23). A stamp that will not
    parse degrades to the date alone rather than printing a fragment of one."""
    edition = str(entry.get("edition", ""))
    day = editions.edition_key(edition)[0] or edition[:10]
    try:
        shown = dt.date.fromisoformat(day).strftime("%A %-d %B")
    except ValueError:
        shown = day
    stamp = str(entry.get("compiled", ""))
    when = stamp.split(" ", 1)[1] if " " in stamp else ""
    n = int(entry.get("items") or 0)
    parts = [shown + (f", {when}" if when else "")]
    # **No count where no count is known.** An adopted entry — a PDF on disk the manifest never
    # recorded — has no `items`, and printing *0 entries* would be a fabricated fact about a
    # file nobody can check without opening it. The date is what is certain, so the date is what
    # it says.
    if n:
        parts.append(f"{n} entr{'y' if n == 1 else 'ies'}")
    return " — ".join(parts)


if __name__ == "__main__":
    where = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "site" / "bulletin"
    held = load(where)
    print(f"{manifest_path(where)}  —  retention {held.get('retention_days')} days")
    for e in held.get("editions", []):
        print(f"  {e['edition']:<18} {label(e):<42} {e['file']}")
    gone = missing(where)
    if gone:
        print(f"MISSING: {len(gone)} entr(ies) name a file that is not there: {', '.join(gone)}")
