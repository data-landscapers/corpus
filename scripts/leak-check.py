#!/usr/bin/env python3
"""leak-check.py — the source-body leak gate (F10).

    python scripts/leak-check.py outputs         # gate outputs/ (BUILD, before commit)
    python scripts/leak-check.py site outputs     # gate both (RENDER, before deploy)
    python scripts/leak-check.py site --no-cache  # ignore the verdict cache; read every file
    exit 0 = clean, exit 1 = a body was found (and the run must stop)

**Why this exists.** `documentation/design.md` §8 makes this the one check that
*fails* the build rather than warning: a verbatim source body must never reach
this repo's history, because a leak into a public repo is permanent. It used to
live inside `scripts/pull.py` (the pre-migration pull from OSINT, deleted 2026-08-16). The migration
retired the pull but not the risk — Corpus now **authors** `outputs/` itself, and
a bug in a compiler could still copy a body — so the gate is rehomed here, as its
own runnable thing, and each job invokes it before it commits or publishes.

`outputs/` holds metadata and compiled prose *by construction*, so this should
never fire. That is exactly why it fails the run: a firing means a compiler is
wrong, and we want to hear about it loudly, before the commit, not after.

Detection (lifted unchanged from the retired pull.py gate; `scripts/test_leak_check.py` proves each case fires):
  - any column/key named like a body (`body`, `text`, `content`, …) — immediate fail;
  - any field longer than a length cap (1000 chars; 8000 for known prose columns
    like `description`/`note`) — the backstop for a body the names miss;
  - a markdown file whose frontmatter declares `type: source` or `body_completeness`;
  - any path under `raw/` — a source page must never be here.
Adding a prose column to the higher cap is a deliberate edit, which is the point:
a new prose column should have to be admitted, not discovered.

**HTML and PDF are checked too, and that is the point of the gate** (F10).
`design.md` §8 rejected a gate that "would check the markdown and not the HTML it
becomes"; `site/` is 273 HTML and 165 PDF against 107 CSV, so a gate blind to
those two formats is looking away from almost everything it publishes.

The caps below are calibrated against the real site, not guessed:
  - longest legitimate HTML block  : 3,238 chars (median 674)  -> cap 8,000
  - longest legitimate PDF page    : 5,490 chars (median 3,242) -> cap 12,000
Recalibrate by measuring rather than by raising a cap until the gate goes quiet.

Two deliberate non-rules, because each would fire on correct output:
  - no check on class/id attributes — the site's own report markup is
    `class="article-body"`, so anything matching "body" flags every page;
  - the marker scan looks for `body_completeness:` **with the colon** (leaked
    frontmatter), since `body_completeness` alone is a legitimate catalogue column.

Known limit, stated rather than papered over: a body long enough to flow across a
PDF page break is split into per-page chunks that each sit under the page cap, so
length alone will not catch it there — the marker scan and the CSV/JSON/markdown
checks upstream of the render are what cover that case.
"""
from __future__ import annotations
import csv, datetime as dt, hashlib, json, re, sys
from html.parser import HTMLParser
from pathlib import Path

BODY_COLUMNS = {"body", "text", "content", "full_text", "fulltext",
                "article", "raw_body", "verbatim", "extract"}
MAX_FIELD = 1000
PROSE_COLUMNS = {"description", "note", "position_end", "summary"}
MAX_PROSE_FIELD = 8000
MAX_HTML_BLOCK = 8000        # observed max legitimate block 3,238
MAX_PDF_PAGE = 12000         # observed max legitimate page  5,490
MAX_MD_LINE = 6000           # observed max legitimate line  2,185 (median 25)
csv.field_size_limit(10 ** 8)

# Frontmatter that only ever belongs to an OSINT source record. Rendered into a
# page, either one means a source file reached the renderer.
LEAKED_FRONTMATTER = re.compile(r"\btype:\s*source\b|\bbody_completeness:", re.I)


def cap_for(name: str) -> int:
    return MAX_PROSE_FIELD if name.strip().lower() in PROSE_COLUMNS else MAX_FIELD


def frontmatter(text: str) -> list[str]:
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    return text[3:end].splitlines() if end != -1 else []


def body_lines(text: str) -> list[str]:
    """Everything after the frontmatter. One line per paragraph is the repo's
    writing rule, so a line here *is* a paragraph and is the right unit to cap."""
    if not text.startswith("---"):
        return text.splitlines()
    end = text.find("\n---", 3)
    if end == -1:
        return text.splitlines()
    rest = text[end + 1:]
    nl = rest.find("\n")
    return rest[nl + 1:].splitlines() if nl != -1 else []


def check_markdown(path: Path, rel: str) -> list[str]:
    faults = []
    text = path.read_text(encoding="utf-8", errors="replace")
    # F19: the body, not just the frontmatter. A body pasted into a report's
    # prose used to pass here and only fail once rendered to HTML or PDF.
    for n, line in enumerate(body_lines(text), start=1):
        if LEAKED_FRONTMATTER.search(line):
            faults.append(f"{rel}: body line {n} carries source frontmatter")
            break
        if len(line) > MAX_MD_LINE:
            faults.append(f"{rel}: body line {n} is {len(line)} chars (cap {MAX_MD_LINE})")
            break
    for line in frontmatter(text):
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
    return check_json_data(data, rel)


def check_json_data(data, rel: str) -> list[str]:
    """The walk, over already-parsed data — shared with the .js checker (F20)."""
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


class _Blocks(HTMLParser):
    """Text of the page, split at block-level boundaries.

    The block, not the page, is the unit: a report page legitimately runs to
    70,000 characters of compiled prose, but no single legitimate block passes
    ~3,200. A pasted source body arrives as one very long run.
    """
    SKIP = {"script", "style"}
    BLOCK = {"p", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6",
             "blockquote", "div", "section", "article", "header", "footer", "br"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.buf, self.blocks = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self._flush()
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.BLOCK:
            self._flush()
        if self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if not any(t in self.SKIP for t in self.stack):
            self.buf.append(data)

    def _flush(self):
        text = " ".join("".join(self.buf).split())
        if text:
            self.blocks.append(text)
        self.buf = []

    def close(self):
        super().close()
        self._flush()


def check_html(path: Path, rel: str) -> list[str]:
    parser = _Blocks()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    parser.close()
    for block in parser.blocks:
        if LEAKED_FRONTMATTER.search(block):
            return [f"{rel}: rendered text carries source frontmatter"]
        if len(block) > MAX_HTML_BLOCK:
            return [f"{rel}: text block is {len(block)} chars (cap {MAX_HTML_BLOCK})"]
    return []


def check_pdf(path: Path, rel: str) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError:
        # Never pass silently: an unscannable PDF is an unchecked PDF, and this
        # gate exists to fail rather than to warn.
        return [f"{rel}: cannot scan PDF — pypdf is not installed (pip install pypdf)"]
    try:
        pages = PdfReader(str(path)).pages
    except Exception as exc:
        return [f"{rel}: PDF could not be read ({exc})"]
    for n, page in enumerate(pages, start=1):
        text = page.extract_text() or ""
        if LEAKED_FRONTMATTER.search(text):
            return [f"{rel}: page {n} carries source frontmatter"]
        if len(text) > MAX_PDF_PAGE:
            return [f"{rel}: page {n} is {len(text)} chars (cap {MAX_PDF_PAGE})"]
    return []


# A generated data file dressed as a script: `window.CATALOGUE = {...};`
JS_ASSIGNMENT = re.compile(r"^\s*(?:var|let|const)?\s*[\w.$]+\s*=\s*(.*?);?\s*$", re.S)
JS_LONG_STRING = re.compile(r'"((?:[^"\\]|\\.){%d,})"' % MAX_PROSE_FIELD)


def check_js(path: Path, rel: str) -> list[str]:
    """`site/catalogue/catalogue-data.js` is catalogue records, not code (F20).

    Unwrap the assignment and walk it as JSON, so it gets the same key-name and
    field-length checks as the .json it was packed from. A .js that is genuinely
    code will not parse — that is not a leak, so fall back to scanning its text
    for markers and oversized string literals rather than failing the run on it.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    match = JS_ASSIGNMENT.match(text.strip())
    if match:
        try:
            return check_json_data(json.loads(match.group(1)), rel)
        except json.JSONDecodeError:
            pass
    faults = []
    if LEAKED_FRONTMATTER.search(text):
        faults.append(f"{rel}: carries source frontmatter")
    for literal in JS_LONG_STRING.findall(text):
        faults.append(f"{rel}: string literal is {len(literal)} chars (cap {MAX_PROSE_FIELD})")
        break
    return faults


# ── the verdict cache ───────────────────────────────
#
# **Why one exists at all** *(2026-08-23, on Bill seeing the gate re-read 2,242 PDFs)*. The
# expensive formats here are PDF and HTML: `site/` holds 2,242 dated editions across 731 MB, and
# every one of them was being text-extracted afresh on each BUILD and each RENDER — a quarter of
# an hour of work to re-derive a verdict that could not have changed. `RENDER.md` §9 is the reason
# it could not: **a published file is never revised**, so an edition that passed this gate once is
# bytes that will never move again, and each run after it re-read them to reach the same answer.
#
# **The key is the content, not the path and not the clock.** A digest of the file's own bytes
# cannot be fooled by a rebuild that rewrites a file identically, by a copy, or by a restored
# mtime; and a file whose bytes *do* move gets a different key and is scanned again, which is
# wanted anyway — under §9 a changed edition is itself something to look at. Hashing costs one
# sequential read, where extracting a PDF's text costs orders of magnitude more.
#
# **The whole cache is dropped when this file changes.** An entry records *this gate's* verdict,
# so a raised cap, a widened regex or a fixed bug must not leave two thousand files verdicted
# under rules that no longer exist. The digest of this source sits beside the entries and a
# mismatch discards all of them — an edit to the gate costs one cold pass, which is the right
# price for changing what the gate means.
#
# **Only clean verdicts are kept.** A fault stops the run, and the file that gets fixed comes back
# with different bytes regardless, so there is nothing a cached fault would save.
CACHE = Path(__file__).resolve().parent.parent / "logs" / ".leak-check-cache.json"
CACHED_SUFFIXES = {".pdf", ".html", ".htm"}
CACHE_KEEP_DAYS = 30      # an entry unseen this long is dropped, so deleted editions age out


def rules_digest() -> str:
    """This gate's own bytes. Any edit to it invalidates every entry."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cache() -> dict:
    """`{content digest: last-seen date}` — empty if absent, unreadable or stale."""
    try:
        data = json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict) or data.get("rules") != rules_digest():
        return {}
    clean = data.get("clean")
    return clean if isinstance(clean, dict) else {}


def save_cache(clean: dict) -> None:
    """Never fail the run over the cache: it is an optimisation, and a gate that stops because it
    could not write a scratch file has confused the two."""
    cutoff = (dt.date.today() - dt.timedelta(days=CACHE_KEEP_DAYS)).isoformat()
    kept = {d: seen for d, seen in clean.items() if seen >= cutoff}
    try:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps({"rules": rules_digest(), "clean": kept},
                                    indent=0, sort_keys=True), encoding="utf-8", newline="")
    except OSError as exc:
        print(f"leak-check: could not write the verdict cache ({exc}) — the gate still ran")


CHECKERS = {".md": check_markdown, ".csv": check_csv, ".json": check_json,
            ".txt": check_text, ".html": check_html, ".htm": check_html,
            ".pdf": check_pdf, ".js": check_js}


def scan(root: Path, clean: dict | None = None) -> list[str]:
    """Every source-body fault under `root`.

    `clean` is the verdict cache, read and updated in place. Passing `None` scans every file,
    which is what the tests do — a gate proved against a cache it filled itself has proved
    nothing about the checks."""
    faults: list[str] = []
    today = dt.date.today().isoformat()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relpath = path.relative_to(root)
        rel = relpath.as_posix()
        # A *directory* named raw, matched on path components. The old string
        # test (`rel.startswith("raw")`) also caught `raw-catalogue.csv`, so the
        # gate's verdict depended on which root you passed it: clean under
        # `site`, false-positive under `site/catalogue`.
        if "raw" in relpath.parts[:-1]:
            faults.append(f"{rel}: path is under raw/")
            continue
        check = CHECKERS.get(path.suffix.lower())
        if not check:
            continue
        cacheable = clean is not None and path.suffix.lower() in CACHED_SUFFIXES
        digest = file_digest(path) if cacheable else None
        if digest is not None and digest in clean:
            clean[digest] = today          # seen today, so it does not age out
            continue
        found = check(path, rel)
        faults.extend(found)
        if digest is not None and not found:
            clean[digest] = today
    return faults


def main() -> int:
    args = sys.argv[1:]
    # `--no-cache` scans every file whatever the cache holds. Reach for it when the question is
    # *is the gate itself right*, rather than *is today's output clean*.
    use_cache = "--no-cache" not in args
    roots = [Path(a) for a in args if a != "--no-cache"] or [Path("outputs")]
    clean = load_cache() if use_cache else None
    reused = len(clean) if clean is not None else 0

    faults: list[str] = []
    for root in roots:
        if not root.exists():
            print(f"leak-check: {root} does not exist — skipping")
            continue
        faults += scan(root, clean)

    if clean is not None:
        save_cache(clean)

    if faults:
        print(f"LEAK GATE FAILED — {len(faults)} problem(s); do NOT commit/publish:")
        for f in faults[:40]:
            print("  " + f)
        return 1
    where = ", ".join(str(r) for r in roots)
    if clean is None:
        print(f"leak gate: clean ({where}; cache bypassed, every file scanned)")
    else:
        print(f"leak gate: clean ({where}; {reused} PDF/HTML verdict(s) reused, "
              f"{len(clean) - reused} newly scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
