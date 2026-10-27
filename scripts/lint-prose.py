#!/usr/bin/env python3
r"""lint-prose.py — the prose sheet's numbers and words, over every narrative block in `outputs/`.

Strategic review 7, R133. The sheet is the share's `documentation/prose-style.md` (R132); this is
the half of it a script can read. Whether a change names the position it changed from (R152) is
read by a person, at the unit review, and has no check here.

**A block is the unit the sheet speaks of**, keyed so a run can tell whether it touched it:

- **status** — a status report's sub-section, keyed by the `<!-- slug -->` under its `###`
  heading. The `<!-- derived -->` paragraph and the `<!-- absences -->` block are emitted, not
  written, and are left out.
- **maturity** — one labelled paragraph of `outputs/maturity/{id}/{ISO3}.md`, keyed by indicator,
  `##` heading and label. The bold label is the writer scripts' apparatus, not prose, and is
  stripped before any check.
- **bulletin** — one summary in `outputs/bulletins/summaries.json`, keyed by slug, **written on
  or after `SHEET_FROM`** (R138). An older summary sits in a published bulletin, which is never
  revised, so it could never clear and would only floor the estate count.
- **wiki** — a `##` section of a page in the mirror's `wiki/intersections/`. **Reported, never
  gated** (R133, CORPUS final reading): it is OSINT's prose, and the count is R149's measure.

**The checks**, each a code in the output:

- `mean`     the block's mean sentence is 20 words or more (R128).
- `long`     a sentence runs over 40 words (R128).
- `contrast` `rather than` more than once in 1,000 words, rounded up, so one is allowed in any
             block under 1,000 (R128).
- `first`    status only: a paragraph's first sentence carries no link, or no year inside it,
             and is not wholly link text (R129 as reissued). A figure alone does not pass.
- `words`    the apparatus words R130 replaced: *Not held*, *Noted, not assessed*, *no X is held*,
             *is not known*, *evidence held*, *nothing held*, *source held*.
- `mood`     the sheet's mood words and set-ups: *plainly*, *quietly*, *finally*, *strikingly*,
             *alarming*, *from opposite ends*.

Words inside quotation marks are the source speaking and are not charged; link labels are the
drafter's paraphrase and are. Sentences split on `.`, `?` and `!`, never on `;` and never inside a
link label — the sheet's exemplar 1 counts its semicolon sentence as one of 36 words.

**R130's words gate in maturity blocks too** since R136: the labels live in `maturity_words.py`,
every writer passes its page through `maturity_words.rewrite()`, and what is left in the estate
is drafted prose that the nightly 4c pass rewrites when it revisits the cell.

**The gate is on blocks written or revised this run**: `--open` at a run's start records the
commit it opened on in `logs/.prose-open`; `--gate` compares each block, by key, against that
commit and fails on a changed or new block that breaks a check. A block moved unchanged is not
revised. With no `--open` taken, the base is `HEAD`.

**`logs/prose.csv` is the estate's measure**, one line a unit a night (`--log` rewrites the
day's lines): `date,unit,blocks,failing,words,sentences,mean,longest,contrast,first,word_hits,
mood_hits`. Units are a place code, `bulletin`, and `wiki`. **The estate count is the failing
blocks across every unit but `wiki`** — what the status line prints as `prose - NN`.

    python scripts/lint-prose.py                      # the estate, counts per unit; reports only
    python scripts/lint-prose.py --unit ZAF -v        # one unit, each failing block named
    python scripts/lint-prose.py --log                # the estate, and today's lines in prose.csv
    python scripts/lint-prose.py --open               # a run's first act: record the base commit
    python scripts/lint-prose.py --gate               # a run's last check: fails on revised blocks
    python scripts/lint-prose.py --file PATH          # any markdown file, its paragraphs as blocks

Exit 0 clean or reporting, 1 a gated block fails, 2 nothing readable.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import io
import json
import math
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
REPORTS = os.path.join(ROOT, "outputs", "reports")
MATURITY = os.path.join(ROOT, "outputs", "maturity")
SUMMARIES = os.path.join(ROOT, "outputs", "bulletins", "summaries.json")
WIKI = os.path.join(ROOT, "scripts", ".workroot", "wiki", "intersections")
LOG = os.path.join(ROOT, "logs", "prose.csv")
OPEN = os.path.join(ROOT, "logs", ".prose-open")
FIELDS = ["date", "unit", "blocks", "failing", "words", "sentences", "mean", "longest",
          "contrast", "first", "word_hits", "mood_hits"]

SHEET_FROM = "2026-10-28"   # the first bulletin written with BULLETIN.md's check (R138)
MEAN_UNDER, LONGEST, CONTRAST_PER = 20, 40, 1000

LINK = re.compile(r"\[([^\]]*)\]\((?:<[^>]*>|(?:[^()\s]|\([^()]*\))*)\)")
WIKILINK = re.compile(r"\[\[([^\[\]|]+?)(?:\|([^\[\]]*))?\]\]")
QUOTED = re.compile(r"“[^”]*”|\"[^\"\n]*\"")
YEAR = re.compile(r"\b(?:19|20)\d\d\b")
LABEL = re.compile(r"\A\s*\*{2,3}[^*]+\*{2,3}\.?\s*")
NOT_PROSE = re.compile(r"\A\s*(?:#|\||>|<!--|```|-{3,}\s*\Z)")
FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)
ABBREV = {"e.g", "i.e", "etc", "no", "nos", "mr", "mrs", "ms", "dr", "prof", "st", "vs", "art",
          "arts", "sec", "para", "cf", "jr", "sr", "co", "ltd", "inc", "fig", "vol", "approx"}

WORDS = [re.compile(p) for p in (
    r"\bNot held\b", r"\bNoted, not assessed\b", r"(?i)\bis not known\b", r"(?i)\bare not known\b",
    r"(?i)\bno\b(?:(?!\bwhere\b)[^.;]){0,80}?\b(?:is|are) held\b", r"(?i)\bnone held\b",
    r"(?i)\b(?:evidence|nothing) held\b", r"(?i)\bsources? held\b")]
MOOD = [re.compile(p, re.I) for p in (
    r"\bplainly\b", r"\bquietly\b", r"\bfinally\b", r"\bstrikingly\b", r"\balarming(?:ly)?\b",
    r"\bfrom opposite ends\b")]
CONTRAST = re.compile(r"\brather than\b", re.I)


# --- text ---------------------------------------------------------------------------------------

def plain(text: str) -> str:
    """Links and wikilinks to their labels, emphasis and code ticks dropped."""
    text = WIKILINK.sub(lambda m: m.group(2) or m.group(1), text)
    text = LINK.sub(r"\1", text)
    return re.sub(r"[*_`]", "", text)


def sentences(text: str) -> list[str]:
    """`text` split on `.`, `?` and `!` before a capital, a quote or a bracket, never inside a
    link label and never after an abbreviation or an initial."""
    out, buf, depth = [], [], 0
    tokens = text.split()
    for i, tok in enumerate(tokens):
        buf.append(tok)
        depth += tok.count("[") - tok.count("]")
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        end = re.search(r"[.?!][)\]\"”’*_]*\Z", tok)
        if not end or depth > 0:
            continue
        stem = re.sub(r"[.?!][)\]\"”’*_]*\Z", "", tok).lstrip("([*_\"“").lower()
        if tok.endswith(".") and (stem in ABBREV or re.fullmatch(r"[a-z]", stem)):
            continue
        if nxt and not re.match(r"[\[(\"“‘*_A-ZÀ-Þ0-9]", nxt):
            continue
        out.append(" ".join(buf))
        buf = []
    if buf:
        out.append(" ".join(buf))
    return [s for s in out if s.strip()]


def nwords(s: str) -> int:
    return len([w for w in plain(s).split() if re.search(r"\w", w)])


def first_ok(sentence: str) -> bool:
    """R129: a link and a year inside the sentence, or the sentence wholly link text."""
    if not LINK.search(sentence):
        return False
    if not re.search(r"\w", LINK.sub("", sentence)):
        return True
    return bool(YEAR.search(plain(sentence)))


def check(paragraphs: list[str], kind: str) -> dict:
    """The counts and the failing codes for one block of paragraphs."""
    sents, firsts = [], 0
    for p in paragraphs:
        ss = sentences(p)
        if kind == "status" and ss and not first_ok(ss[0]):
            firsts += 1
        sents += ss
    lens = [nwords(s) for s in sents]
    words = sum(lens)
    speech = QUOTED.sub(" ", plain(" ".join(paragraphs)))
    if kind == "doc":
        speech = re.sub(r"\*[^*]+\*|`[^`]+`", " ", " ".join(paragraphs))
        speech = QUOTED.sub(" ", plain(speech))
    contrast = len(CONTRAST.findall(speech))
    word_hits = sum(len(p.findall(speech)) for p in WORDS)
    mood_hits = sum(len(p.findall(speech)) for p in MOOD)
    fails = []
    if lens and words / len(lens) >= MEAN_UNDER:
        fails.append("mean")
    if lens and max(lens) > LONGEST:
        fails.append("long")
    if contrast > max(1, math.ceil(words / CONTRAST_PER)):
        fails.append("contrast")
    if firsts:
        fails.append("first")
    if word_hits:
        fails.append("words")
    if mood_hits:
        fails.append("mood")
    return {"words": words, "sentences": len(lens), "longest": max(lens, default=0),
            "contrast": contrast, "first": firsts, "word_hits": word_hits,
            "mood_hits": mood_hits, "fails": fails}


def gating(kind: str, fails: list[str]) -> list[str]:
    """The codes that gate: none for the wiki, every one elsewhere."""
    return [] if kind == "wiki" else fails


# --- blocks -------------------------------------------------------------------------------------

def paragraphs(lines: list[str]) -> list[str]:
    """Prose paragraphs from a run of lines: headings, tables, quotes, comments, fences and the
    paragraph under a `<!-- derived -->` marker left out."""
    out, buf, fenced, derived, absent = [], [], False, False, False
    for line in lines + [""]:
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if not s:
            if buf and not derived:
                out.append(" ".join(buf))
            buf, derived = ([], False) if buf else (buf, derived)
            continue
        if s.startswith("<!-- derived"):
            derived = True
            continue
        if s.startswith("<!-- absences"):
            absent = True
            continue
        if s.startswith("<!-- /absences"):
            absent = False
            continue
        if absent:
            continue
        if NOT_PROSE.match(line):
            continue
        item = re.match(r"\A\s*(?:[-*+]|\d+[.)])\s+", line)
        if item:
            # A list item is its own paragraph, and one that is only a citation is not prose.
            if buf and not derived:
                out.append(" ".join(buf))
            buf, derived = [], False
            s = line[item.end():].strip()
            if re.search(r"[A-Za-zÀ-ɏ]{2}", LINK.sub("", WIKILINK.sub("", s))):
                out.append(s)
            continue
        buf.append(s)
    return out


def body(text: str) -> list[str]:
    m = FRONTMATTER.match(text)
    return (text[m.end():] if m else text).splitlines()


def status_blocks(text: str) -> dict[str, list[str]]:
    """{slug: paragraphs} for a status report, one block an `###` sub-section."""
    blocks, key, run = {}, None, []
    for line in body(text) + ["### "]:
        if line.startswith("## ") or line.startswith("### "):
            if key and run:
                blocks[key] = paragraphs(run)
            key, run = line.lstrip("# ").strip() if line.startswith("### ") else None, []
            continue
        m = re.match(r"\s*<!-- ([a-z][\w.-]*) -->\s*\Z", line)
        if key is not None and m and m.group(1) != "derived" and not any(l.strip() for l in run):
            key = m.group(1)
            continue
        run.append(line)
    return {k: v for k, v in blocks.items() if v}


def maturity_blocks(text: str, prefix: str) -> dict[str, list[str]]:
    """{indicator/heading/label#n: [paragraph]} with each paragraph's bold label stripped."""
    blocks, heading = {}, ""
    for p_lines in re.split(r"\n\s*\n", "\n".join(body(text))):
        p = p_lines.strip()
        if p.startswith("## "):
            heading = p[3:].strip()
            continue
        if not p or p.startswith("#"):
            continue
        for para in paragraphs(p.splitlines()):
            m = LABEL.match(para)
            label = re.sub(r"[*.]", "", m.group(0)).strip() if m else ""
            prose = para[m.end():] if m else para
            if not re.search(r"\w", prose):
                continue
            key, n = f"{prefix}/{heading}/{label}", 1
            while f"{key}#{n}" in blocks:
                n += 1
            blocks[f"{key}#{n}"] = [prose]
    return blocks


def wiki_blocks(text: str, prefix: str) -> dict[str, list[str]]:
    blocks, heading, run = {}, "", []
    for line in body(text) + ["## "]:
        if line.startswith("## "):
            ps = paragraphs(run)
            if ps:
                blocks[f"{prefix}/{heading}"] = ps
            heading, run = line[3:].strip(), []
            continue
        run.append(line)
    return blocks


def summary_text(v) -> str:
    return v.get("summary", "") if isinstance(v, dict) else str(v or "")


def bulletin_blocks(raw: str) -> dict[str, list[str]]:
    try:
        data = json.loads(raw)
    except ValueError:
        return {}
    return {k: [summary_text(v)] for k, v in data.items() if summary_text(v).strip()
            and not (isinstance(v, dict) and v.get("written", SHEET_FROM) < SHEET_FROM)}


def read(path: str) -> str:
    try:
        with io.open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def sources(unit: str | None = None, wiki: bool = True):
    """(unit, kind, relpath, blocks-from-text) for every file the lint reads."""
    for path in sorted(glob.glob(os.path.join(REPORTS, "*", "*-status.md"))):
        u = os.path.basename(os.path.dirname(path))
        if unit in (None, u):
            yield u, "status", path, status_blocks
    for path in sorted(glob.glob(os.path.join(MATURITY, "*", "*.md"))):
        u, ind = os.path.basename(path)[:-3], os.path.basename(os.path.dirname(path))
        if re.fullmatch(r"[A-Z]{3}", u) and unit in (None, u):
            yield u, "maturity", path, (lambda t, ind=ind: maturity_blocks(t, ind))
    if unit in (None, "bulletin") and os.path.exists(SUMMARIES):
        yield "bulletin", "bulletin", SUMMARIES, bulletin_blocks
    if wiki and unit in (None, "wiki") and os.path.isdir(WIKI):
        for path in sorted(glob.glob(os.path.join(WIKI, "*.md"))):
            name = os.path.basename(path)[:-3]
            yield "wiki", "wiki", path, (lambda t, name=name: wiki_blocks(t, name))


# --- the base -----------------------------------------------------------------------------------

def git(*args: str) -> tuple[int, str]:
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", errors="replace")


def base_commit() -> str:
    sha = read(OPEN).strip()
    return sha or git("rev-parse", "HEAD")[1].strip()


def changed_paths(base: str) -> set[str]:
    """Paths under `outputs/` that differ from `base`, tracked or not."""
    out = set(git("diff", "--name-only", base, "--", "outputs")[1].split("\n"))
    out |= set(git("ls-files", "--others", "--exclude-standard", "--", "outputs")[1].split("\n"))
    return {os.path.normpath(os.path.join(ROOT, p)) for p in out if p.strip()}


def at_base(base: str, path: str) -> str:
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    code, text = git("show", f"{base}:{rel}")
    return text if code == 0 else ""


# --- runs ---------------------------------------------------------------------------------------

def survey(unit=None, wiki=True):
    """{unit: [(kind, path, key, result)]} over every block."""
    out: dict[str, list] = {}
    for u, kind, path, parse in sources(unit, wiki):
        for key, ps in parse(read(path)).items():
            out.setdefault(u, []).append((kind, path, key, check(ps, kind)))
    return out


def tally(unit: str, rows: list) -> dict:
    words = sum(r["words"] for *_, r in rows)
    sents = sum(r["sentences"] for *_, r in rows)
    return {"date": dt.date.today().isoformat(), "unit": unit, "blocks": len(rows),
            "failing": sum(1 for *_, r in rows if r["fails"]), "words": words, "sentences": sents,
            "mean": round(words / sents, 1) if sents else 0,
            "longest": max((r["longest"] for *_, r in rows), default=0),
            "contrast": round(1000 * sum(r["contrast"] for *_, r in rows) / words, 2) if words else 0,
            "first": sum(r["first"] for *_, r in rows),
            "word_hits": sum(r["word_hits"] for *_, r in rows),
            "mood_hits": sum(r["mood_hits"] for *_, r in rows)}


def write_log(lines: list[dict]) -> None:
    today = dt.date.today().isoformat()
    kept = []
    if os.path.exists(LOG):
        with io.open(LOG, encoding="utf-8", newline="") as f:
            kept = [r for r in csv.DictReader(f) if r["date"] != today]
    with io.open(LOG, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(kept + lines)


def estate_count(path: str = LOG) -> int | None:
    """The newest night's failing blocks across every unit but `wiki`; None with no log."""
    if not os.path.exists(path):
        return None
    with io.open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None
    last = max(r["date"] for r in rows)
    return sum(int(r["failing"]) for r in rows if r["date"] == last and r["unit"] != "wiki")


def open_run() -> int:
    """Record the commit the run opened on, for `--gate` to diff against."""
    sha = git("rev-parse", "HEAD")[1].strip()
    with io.open(OPEN, "w", encoding="utf-8") as f:
        f.write(sha + "\n")
    print(f"lint-prose: base {sha[:9]}")
    return 0


def gate(unit=None) -> int:
    base = base_commit()
    paths = changed_paths(base)
    bad = 0
    for u, kind, path, parse in sources(unit, wiki=False):
        if os.path.normpath(path) not in paths:
            continue
        before = parse(at_base(base, path))
        for key, ps in parse(read(path)).items():
            if before.get(key) == ps:
                continue
            fails = gating(kind, check(ps, kind)["fails"])
            if fails:
                bad += 1
                print(f"  FAIL {os.path.relpath(path, ROOT)} [{key}]: {', '.join(fails)}")
    print(f"lint-prose: {'FAIL' if bad else 'ok'} - {bad} revised block(s) failing "
          f"since {base[:9]}")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--unit")
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if a.open:
        return open_run()
    if a.gate:
        return gate(a.unit)
    if a.file:
        text = read(a.file)
        if not text:
            print(f"lint-prose: cannot read {a.file}")
            return 2
        r = check(paragraphs(body(text)), "doc")
        print(f"lint-prose: {'FAIL' if r['fails'] else 'ok'} - {a.file}: {r['words']} words, "
              f"{r['sentences']} sentences, mean {r['words'] / max(1, r['sentences']):.1f}, "
              f"longest {r['longest']}" + (f"; {', '.join(r['fails'])}" if r["fails"] else ""))
        return 1 if r["fails"] else 0
    found = survey(a.unit)
    if not found:
        print("lint-prose: nothing readable")
        return 2
    lines = [tally(u, rows) for u, rows in sorted(found.items())]
    for u, rows in sorted(found.items()):
        if a.verbose:
            for kind, path, key, r in rows:
                if r["fails"]:
                    print(f"  {u} {kind} [{key}]: {', '.join(r['fails'])}")
    if a.log:
        write_log(lines)
    estate = sum(t["failing"] for t in lines if t["unit"] != "wiki")
    blocks = sum(t["blocks"] for t in lines if t["unit"] != "wiki")
    wiki = next((t for t in lines if t["unit"] == "wiki"), None)
    print(f"lint-prose: {estate} of {blocks} block(s) failing the sheet across "
          f"{sum(1 for t in lines if t['unit'] != 'wiki')} unit(s)"
          + (f"; wiki {wiki['failing']} of {wiki['blocks']}, mean {wiki['mean']}" if wiki else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
