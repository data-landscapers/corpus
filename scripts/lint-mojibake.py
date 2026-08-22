#!/usr/bin/env python3
r"""
lint-mojibake.py — UTF-8 text that was read once as cp1252, and can be read back.

**A mangled cell is worse than a missing one, because it reads as present.**
`Ventanilla Ãšnica Empresarial` is a value on the page, quoted into a status
baseline as if it were the source's own words, and — the part that costs
something — it silently fails every grep for the word it mangled. A coded row
about `África Austral` goes missing from a search for `África Austral` and
nothing anywhere reports a miss. That is why this exists as a check rather than
as a one-off repair: the fault arrives with third-party data and will arrive
again *(OSINT `notes-for-corpus.md` note 7, 2026-08-22, which found 85 rows of it
in OSINT's archived copy of the same dataset and 60 in ours)*.

**The damage and its inverse.** UTF-8 bytes were decoded once as cp1252, so each
byte of a multi-byte character became a character in its own right: `é`
(`C3 A9`) became `Ã©`, `—` (`E2 80 94`) became `â€"`. The inverse is exact —
encode the run back to those bytes and decode them as UTF-8 — which is what makes
this repairable at all rather than merely detectable.

**The trap is cp1252's five undefined bytes**, `0x81 0x8D 0x8F 0x90 0x9D`. A
strict cp1252 encoder cannot produce them, so a run containing one raises and, in
a naive implementation, is skipped as unrepairable. `Ã`+U+008D is `Í`; drop it
and five accented characters survive the repair looking like a clean file. The
byte table below is therefore built from cp1252 **with a latin-1 fallback**, which
is what OSINT's own guard had been missing since 2026-08-20.

**Runs of one character are never touched.** A lone `é` is a correctly encoded
letter; the signature is two or more adjacent characters from the table that
decode as valid UTF-8 together. That test, not the alphabet, is what separates
`Ã©` from a legitimate accent — an adjacent pair that is not mis-encoded almost
never forms a valid UTF-8 sequence, and the decode simply fails and leaves it be.

**Inputs are fixed; derived files are only reported.** `prep/` and `lookups/` are
data Corpus owns and nothing regenerates, so `--fix` rewrites them in place.
Anything under `outputs/` is a render of those inputs: mojibake there came from an
input and is cleared by re-rendering, so editing it would be both wrong and
temporary. A hit there means a re-render is owed — and, if the page has already
been published, that the edition stands as it is *(`RENDER.md` §9)*.

**`prep/scope/` is the exception that proves the split, and it is fixed.** Those
per-country cuts *are* regenerable — `status-scope.py` filters them straight out of
`prep/africa-dpi-data.csv` — so by the rule above they belong on the report-only
side. They are repaired anyway, for two reasons. The repair applied to a cut is
character-for-character the transformation a regeneration would apply, because a cut
is a row filter and nothing else; and regenerating one would additionally scan
OSINT's hubs and rewrite the finance and hub cuts beside it, which is a great deal
more than a lint should set in motion to clear 166 mangled sequences. They get no
`.pre-mojibake` backup for the same reason — `status-scope.py {ISO3}` is the backup.

Usage:  python scripts/lint-mojibake.py [--fix] [--derived] [--quiet] [PATH ...]
        no PATH        the input set: prep/**/*.csv, lookups/*.csv
        --derived      also walk outputs/ and report (never fixed)
        --fix          repair the input files in place; a `.pre-mojibake` copy is
                       written beside each file changed, because `prep/` is
                       gitignored and there is no history to fall back on
Exit:   0 clean, 1 mojibake found (or repaired), 2 a path could not be read.
"""
from __future__ import annotations
import argparse, os, re, sys
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent

# byte -> the character a cp1252 read turned it into. cp1252 where it is defined,
# latin-1 for the five bytes it is not (0x81 0x8D 0x8F 0x90 0x9D) — see the header.
_CHAR_TO_BYTE: dict[str, int] = {}
for _b in range(0x80, 0x100):
    try:
        _ch = bytes([_b]).decode("cp1252")
    except UnicodeDecodeError:
        _ch = bytes([_b]).decode("latin-1")
    _CHAR_TO_BYTE.setdefault(_ch, _b)

RUN = re.compile("[" + re.escape("".join(sorted(_CHAR_TO_BYTE))) + "]{2,}")

MAX_PASSES = 3          # double-encoded text needs a second pass; three is a backstop


def _unmangle_run(run: str) -> str | None:
    """One run of high characters, read back as the UTF-8 it was. None if it is not
    mis-encoded — which is the common case for adjacent legitimate accents, since
    two of those together are almost never a valid UTF-8 sequence."""
    try:
        raw = bytes(_CHAR_TO_BYTE[c] for c in run)
    except KeyError:                      # unreachable via RUN, kept for direct calls
        return None
    try:
        out = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return out if out != run else None


def repair(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Return the repaired text and every (before, after) pair applied."""
    applied: list[tuple[str, str]] = []
    for _ in range(MAX_PASSES):
        changed = False

        def sub(m: re.Match[str]) -> str:
            nonlocal changed
            fixed = _unmangle_run(m.group(0))
            if fixed is None:
                return m.group(0)
            changed = True
            applied.append((m.group(0), fixed))
            return fixed

        text = RUN.sub(sub, text)
        if not changed:
            break
    return text, applied


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def scan(path: Path) -> tuple[str, list[tuple[int, str, str]]] | None:
    """(text, [(line, before, after)]). None if the file is not text we can read."""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        print(f"  ! {path}: {exc}", file=sys.stderr)
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        # Not UTF-8 at all. That is a different fault from this one and guessing at
        # the encoding here would only produce a second layer of the same damage.
        print(f"  ! {path}: not UTF-8; left alone", file=sys.stderr)
        return None

    hits: list[tuple[int, str, str]] = []
    for m in RUN.finditer(text):
        fixed = _unmangle_run(m.group(0))
        if fixed is not None:
            hits.append((line_of(text, m.start()), m.group(0), fixed))
    return text, hits


def targets(args: argparse.Namespace) -> tuple[list[Path], list[Path]]:
    if args.paths:
        return [Path(p) for p in args.paths], []
    inputs = sorted(CORPUS.glob("prep/**/*.csv")) + sorted(CORPUS.glob("lookups/*.csv"))
    derived: list[Path] = []
    if args.derived:
        derived = sorted(p for p in (CORPUS / "outputs").rglob("*")
                         if p.is_file() and p.suffix.lower() in (".csv", ".json", ".md", ".html"))
    return inputs, derived


def report(path: Path, hits: list[tuple[int, str, str]], quiet: bool) -> None:
    rel = path.relative_to(CORPUS) if path.is_absolute() and CORPUS in path.parents else path
    print(f"  {rel}: {len(hits)} sequence(s) on {len({h[0] for h in hits})} line(s)")
    if quiet:
        return
    seen: set[tuple[str, str]] = set()
    for line, before, after in hits:
        if (before, after) in seen:
            continue
        seen.add((before, after))
        print(f"      line {line}: {before!r} -> {after!r}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="files to check; default is the input set")
    ap.add_argument("--fix", action="store_true", help="repair the files in place")
    ap.add_argument("--derived", action="store_true", help="also walk outputs/ (report only)")
    ap.add_argument("--quiet", action="store_true", help="counts only, no per-sequence lines")
    args = ap.parse_args()

    inputs, derived = targets(args)
    if not inputs and not derived:
        print("nothing to check", file=sys.stderr)
        return 2

    unreadable = False
    found = repaired = 0

    print(f"inputs ({len(inputs)} file(s)){' — fixing' if args.fix else ''}:")
    for path in inputs:
        got = scan(path)
        if got is None:
            unreadable = True
            continue
        text, hits = got
        if not hits:
            continue
        found += len(hits)
        report(path, hits, args.quiet)
        if args.fix:
            # A regenerable cut needs no backup: `status-scope.py {ISO3}` is the backup,
            # and 44 stray files beside them would be the only thing left behind. See the
            # header on why they are repaired here rather than reported.
            regenerable = (CORPUS / "prep" / "scope") in path.parents
            if not regenerable:
                backup = path.with_suffix(path.suffix + ".pre-mojibake")
                if not backup.exists():
                    backup.write_bytes(path.read_bytes())
            fixed, applied = repair(text)
            # newline="" so the file's own line endings survive; the BOM, if there
            # was one, is inside `text` as U+FEFF and is written back with it.
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(fixed)
            repaired += len(applied)
            where = "regenerable, no backup" if regenerable else f"backup at {backup.name}"
            print(f"      repaired {len(applied)} sequence(s); {where}")

    if derived:
        print(f"derived ({len(derived)} file(s), report only):")
        for path in derived:
            got = scan(path)
            if got is None:
                unreadable = True
                continue
            _, hits = got
            if hits:
                found += len(hits)
                report(path, hits, args.quiet)

    if unreadable:
        return 2
    if not found:
        print("clean")
        return 0
    print(f"{found} sequence(s) found" + (f", {repaired} repaired" if args.fix else ""))
    return 1


if __name__ == "__main__":
    sys.exit(main())
