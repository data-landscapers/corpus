#!/usr/bin/env python3
r"""
lint-staged-queue.py — does a staged file's body belong to its own frontmatter?

**A crossed file is the one staging defect that nothing in the file declares.**
On the GNB batch of 2026-08-27, five of the eighty hand-carried
`progress-filler-GNB-2026-08-27` candidates carried another item's verbatim body
under their own frontmatter. The frontmatter was right, the `url:` was right, the
filename was right, and a URL-index check passed cleanly on every one of them —
the only thing wrong was the text, and the only thing that found it was three
ingest slices reading full bodies by hand *(OSINT `notes-for-corpus.md` note 15)*.
Had the run not been reading full text, all five would have entered `raw/` as
authentic records.

**The cost is not a missing document, it is a false one.** The deleted ASYCUDA
compendium's staged `note:` asserted that the document recorded Guinea-Bissau's
off-site backup and disaster-recovery architecture. That passage is *Cambodia's*.
A `note:` derived from the wrong body is a falsified finding wearing a correct
citation, and it is correct in every field a machine was checking.

**The first thing to say is that the note is wrong about one detail, and the
correction is the cheapest check in this file.** A crossed body is not silent: the
capture writes the fetched page's own address into the body as a second line,
`URL: https://…`, and on a crossed file that line is the address of the document
the body actually came from. It is present on 54 of the GNB batch's 205 files and
it mismatches on exactly fifteen — the five OSINT found by hand and ten more in
the 125 progress items that had not yet been carried. Nothing about that check is
a heuristic: two strings, normalised for scheme and percent-encoding, either
equal or not. It runs first because when it fires there is nothing to adjudicate.

**Where the line is absent, the body still has to be read structurally.** Four
signals, none of which needs a model:

  1. **Title.** The distinctive tokens of `title:` should occur in the body. This
     is the heuristic OSINT ran at parent level to clear the other 69, and its
     own weakness is stated in the note: it is thin on short titles and is *"not
     a substitute for the fix"*. Distinctiveness here is measured against the
     batch rather than a hand-written stopword list — a token in more than
     `--common` of the batch's bodies carries no evidence, and the corpus is
     full of them (*national*, *digital*, *report*, the country's own name).
  2. **Source.** The `url:` host and the `publisher:` should be traceable in the
     body — as a token, as a parenthesised acronym, or as a substring of the body
     with its spaces squashed out, which is what makes `documents1.worldbank.org`
     match *The World Bank Group*. A body from a different organisation almost
     never passes this, and a short title makes it no weaker.
  3. **The body's own first heading.** A captured page opens with the page's own
     title, and a crossed one therefore opens with somebody else's. Sharing not
     one distinctive word with `title:` is a doubt on its own, whatever the rest
     of the body scores — it is what identifies `# P1769320801abf09b…`, a World
     Bank document number, sitting on top of a news item about a transformer
     failure in Bafatá.
  4. **The batch itself.** Four of GNB's five crossings held a body from outside
     the batch, but one held the body of a document *staged in the same batch
     under its own correct name*. Where some other file's body scores markedly
     better on this file's title than its own body does, the pair is named — that
     is a crossing with its counterpart attached, not a suspicion.

A file is in doubt when 1 and 2 fail together, when 1 scores flat zero on a title
with something to say, or when 3 fails; 4 then names the counterpart where there
is one to name. Either way the report prints the body's own opening line, because
that is what a human adjudicates on and it is the first thing a crossed body
gives away.

**Three further checks ride along, because they are the same pass over the same
files.** `PROGRESS-FILLER.md` §5 records three staging defects that were each
found downstream rather than before the hand-off, and states the check for each
in prose. Prose checks get run when someone remembers:

  - **date** — the filename's date prefix is padded, never partial
    (`reference.md` §3: year only takes `YYYY-01-01`), and matches `published:`.
  - **yaml** — the frontmatter round-trips through a parser. An unquoted `note:`
    containing `": "` does not, and five AGO files arrived that way.
  - **title** — an all-ASCII title whose own body carries the accented form of
    its words is a transliteration this run did, not orthography the source
    lacked, and the body is the evidence for the repair.

**Nothing is fixed.** Every finding here is a judgement about which of two things
is wrong — repair the title or leave it, refetch the body or delete the file —
and three of the GNB five were resolved by refetching, deleting or routing to
acquisition rather than by any edit a script could have made.

Usage:  python scripts/lint-staged-queue.py [PATH ...] [--checks LIST]
                                            [--common F] [--min-title F] [--quiet]
        no PATH        every batch under the exchange share's `new-queue/`
        PATH           a directory (walked for *.md) or a single file; each
                       directory is scored as its own batch, since the batch is
                       what makes a token common and what a crossing pairs within
        --checks       comma-separated from url,body,date,yaml,title (default all)
        --common F     drop title tokens occurring in more than this fraction of
                       the batch's bodies (default 0.40; ignored under 20 files)
        --min-title F  a title scoring at or above this fraction on its own body
                       passes check `body` outright (default 0.55)
Exit:   0 clean, 1 findings, 2 a path could not be read.
"""
from __future__ import annotations
import argparse, os, re, sys, unicodedata, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from status_lib import EXCHANGE  # noqa: E402

try:
    import yaml
except ImportError:  # the yaml check is the only thing that needs it
    yaml = None

NEW_QUEUE = os.path.join(EXCHANGE, "new-queue")
ALL_CHECKS = ("url", "body", "date", "yaml", "title")

# Tokens that carry no evidence anywhere, whatever the batch's own frequencies
# say. Kept short on purpose: `--common` is the real filter and it calibrates
# itself, whereas a hand list written against one country's batch is a hand list
# written against one country's batch.
STOPWORDS = {
    "about", "after", "against", "annex", "avec", "before", "between", "care",
    "cette", "chez", "comme", "como", "cont", "dans", "dela", "dele", "dentro",
    "depuis", "desde", "deux", "does", "dont", "elle", "esta", "este", "from",
    "have", "into", "leur", "mais", "mesmo", "nous", "onde", "other", "para",
    "pela", "pelo", "plus", "pour", "quand", "quanto", "para", "sans", "sein",
    "sobre", "sous", "such", "sure", "than", "that", "their", "them", "then",
    "there", "these", "this", "those", "toda", "todo", "tous", "tout", "under",
    "uma", "vers", "very", "vous", "were", "what", "when", "where", "which",
    "will", "with", "within", "without",
}

# Host labels that name no organisation. A domain reduced to nothing by this is
# simply not a source signal, and the check says so rather than guessing.
HOST_NOISE = {
    "www", "www2", "www3", "web", "sites", "static", "cdn", "files", "docs",
    "com", "net", "org", "int", "gov", "edu", "info", "biz", "html", "pdf",
    "gw", "pt", "fr", "uk", "eu", "us", "ao", "za", "sn", "ci", "ng", "ke",
}

FM_RE = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.S)
DATE_PREFIX_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-")
PARTIAL_PREFIX_RE = re.compile(r"^\d{4}(-\d{2})?-(?!\d{2}-)")
ACRONYM_RE = re.compile(r"\(([A-Z][A-Z0-9&.\-]{1,9})\)")
BODY_URL_RE = re.compile(r"^URL:[ \t]*(\S+)[ \t]*$", re.M)
HEADING_RE = re.compile(r"^#{1,3}[ \t]+(\S.*)$")
UNQUOTED_COLON_RE = re.compile(r"^(\w[\w\-]*):\s+(?![\"'|>&*\[{])(.*: .*)$")


def deaccent(text: str) -> str:
    """`Relatório` -> `relatorio`. The comparison alphabet for every check here."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    ).lower()


def tokens(text: str, floor: int = 4) -> set[str]:
    r"""Words of four characters or more, in whatever script the source writes.

    **An ASCII-only split reads a non-Latin title as having no words at all**
    (2026-09-03). `[^a-z0-9]+` cut every Arabic title to nothing, so `title_score`
    returned -1.0, `weak` was true by arithmetic, the source signal could not
    trace an Arabic publisher either, and the file was reported SUSPECT — while
    its body's opening heading was the title, verbatim, which is the strongest
    evidence a file is *not* crossed. Seven such findings came out of DZA and EGY
    on one night, and MAR, TUN, LBY and MRT were queued behind them.

    `\W` is Unicode-aware, so Arabic, Cyrillic, Greek and Amharic now tokenise
    like Latin does. The `deaccent` fold in front of it is unchanged and still
    strips Arabic harakat, which is the same service it does for Portuguese."""
    return {t for t in re.split(r"[\W_]+", deaccent(text)) if len(t) >= floor}


def squash(text: str) -> str:
    """Body reduced to bare alphanumerics, so `World Bank Group` holds `worldbank`."""
    return re.sub(r"[^a-z0-9]+", "", deaccent(text))


def same_url(a: str, b: str) -> bool:
    """Two addresses for one document. Scheme, a leading `www.`, a trailing slash
    and percent-encoding are all things the capture and the frontmatter may
    disagree about without disagreeing about the document."""
    def norm(u: str) -> str:
        u = unicodedata.normalize("NFC", urllib.parse.unquote(u.strip()))
        u = re.sub(r"^[a-z]+://", "", u, flags=re.I)
        u = re.sub(r"^www\d?\.", "", u, flags=re.I)
        return u.rstrip("/").lower()
    return norm(a) == norm(b)


def read_split(path: str) -> tuple[str, str, str] | None:
    """(raw, frontmatter_text, body) — or None where there is no frontmatter."""
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except (OSError, UnicodeDecodeError):
        return None
    m = FM_RE.match(raw)
    if not m:
        return raw, "", raw
    return raw, m.group(1), m.group(2)


def scalar(fm_text: str, key: str) -> str:
    """One frontmatter scalar, read textually — this runs before the yaml check,
    and a file that fails to parse still has to be scored on its title."""
    m = re.search(rf"^{key}:[ \t]*(.*)$", fm_text, re.M)
    if not m:
        return ""
    v = m.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def host_tokens(url: str) -> set[str]:
    m = re.match(r"https?://([^/]+)", url.strip())
    if not m:
        return set()
    labels = {lbl for lbl in re.split(r"[.:]", deaccent(m.group(1))) if len(lbl) >= 3}
    return {lbl for lbl in labels - HOST_NOISE if len(lbl) >= 4}


class Doc:
    def __init__(self, path: str, fm_text: str, body: str):
        self.path = path
        self.name = os.path.basename(path)
        self.fm_text = fm_text
        self.body = body
        self.title = scalar(fm_text, "title")
        self.url = scalar(fm_text, "url")
        self.publisher = scalar(fm_text, "publisher")
        self.published = scalar(fm_text, "published")
        self.body_tokens = tokens(body)
        self.body_squashed = squash(body)
        self.title_tokens_raw = tokens(self.title) - STOPWORDS
        self.pub_tokens_raw = tokens(self.publisher) - STOPWORDS
        self.title_tokens: set[str] = set()  # narrowed to the batch's rare tokens
        self.pub_tokens: set[str] = set()
        seen: set[str] = set()
        self.src_keys_raw = []
        for kind, key in [("host", h) for h in sorted(host_tokens(self.url))] + [
            ("acronym", deaccent(a).replace(".", ""))
            for a in ACRONYM_RE.findall(self.publisher)
        ]:
            if key not in seen:
                seen.add(key)
                self.src_keys_raw.append((kind, key))
        self.src_keys: list[tuple[str, str]] = []
        self.first_line = next(
            (ln.strip() for ln in body.splitlines() if ln.strip()), ""
        )[:110]
        # The capture's own record of what it fetched, written into the body as
        # its second line. Present on about a quarter of a batch — a PDF-to-text
        # capture has one, a page scraped some other way may not.
        m = BODY_URL_RE.search(body[:2000])
        self.body_url = m.group(1) if m else ""
        # The body's own opening heading, where it has one. `# (no title)` is
        # what the capture writes when the page had none, and carries no evidence.
        self.heading = ""
        for ln in body.splitlines()[:6]:
            hm = HEADING_RE.match(ln.strip())
            if hm and hm.group(1).strip().lower() != "(no title)":
                self.heading = hm.group(1).strip()
                break

    def title_score(self, other_body_tokens: set[str] | None = None) -> float:
        """Fraction of this file's distinctive title tokens present in a body."""
        if not self.title_tokens:
            return -1.0
        pool = self.body_tokens if other_body_tokens is None else other_body_tokens
        return len(self.title_tokens & pool) / len(self.title_tokens)

    def source_signal(self) -> tuple[bool, str]:
        """Is the body traceable to this file's own `url:` host or `publisher:`?

        The publisher is read on its **rare** tokens only, for the reason the GNB
        run gives: `Ministerio dos Transportes e Comunicacoes, Republica da
        Guine-Bissau / World Bank` traces to an ITU price report, because *world*,
        *bank*, *republica*, *guine* and *bissau* are in half the bodies of a
        Guinea-Bissau batch. That crossing was the one this check let through on
        its first run, and it let it through on a publisher signal alone."""
        for kind, key in self.src_keys:
            if self.holds(key):
                return True, f"{kind} `{key}`"
        if self.pub_tokens:
            hit = self.pub_tokens & self.body_tokens
            if hit and len(hit) * 2 >= len(self.pub_tokens):
                return True, "publisher " + ", ".join(f"`{t}`" for t in sorted(hit))
        if not self.src_keys and not self.pub_tokens:
            return True, "no distinctive source signal to test"
        named = ", ".join(f"{kind} `{k}`" for kind, k in self.src_keys) or "no host"
        return False, f"{named} and publisher absent from body"

    def holds(self, key: str) -> bool:
        """Does the body carry this source key? A short key must be a word of its
        own — `itu` is inside *instituto* and `upu` inside *populaire* — while a
        longer one may run its words together, which is how `worldbank` finds
        *The World Bank Group*."""
        return key in self.body_tokens or (len(key) >= 5 and key in self.body_squashed)


def load_batch(paths: list[str]) -> tuple[list[Doc], list[str]]:
    docs, unreadable = [], []
    for p in paths:
        got = read_split(p)
        if got is None:
            unreadable.append(p)
            continue
        _, fm_text, body = got
        docs.append(Doc(p, fm_text, body))
    return docs, unreadable


def narrow_titles(docs: list[Doc], common: float) -> None:
    """Drop title tokens the batch's own bodies make commonplace.

    Below twenty files the document frequencies are noise, so the narrowing is
    skipped and the hard stopword list is the whole filter — a small batch is
    scored a little more loosely rather than on a frequency table it cannot
    support."""
    if len(docs) < 20:
        for d in docs:
            d.title_tokens = set(d.title_tokens_raw)
            d.pub_tokens = set(d.pub_tokens_raw)
            d.src_keys = list(d.src_keys_raw)
        return
    df: dict[str, int] = {}
    for d in docs:
        for t in d.body_tokens:
            df[t] = df.get(t, 0) + 1
    ceiling = common * len(docs)
    for d in docs:
        d.title_tokens = {t for t in d.title_tokens_raw if df.get(t, 0) <= ceiling}
        if not d.title_tokens:  # every word of the title is batch-commonplace
            d.title_tokens = set(d.title_tokens_raw)
        # The publisher gets no such fallback: a publisher named only in
        # commonplace words is not a signal, and pretending otherwise is what
        # traced an ITU report to the World Bank.
        d.pub_tokens = {t for t in d.pub_tokens_raw if df.get(t, 0) <= ceiling}

    # Host labels and acronyms are narrowed the same way, and they need it most.
    # `worldbank` is in half the bodies of a donor-authored batch and `itu` in
    # every Portuguese one; either would trace any body to any file. The
    # frequency is counted with the same predicate the check uses, so a key that
    # is commonplace *only because the test is loose* is dropped by the test's
    # own looseness.
    keys = {k for d in docs for _, k in d.src_keys_raw}
    key_df = {k: sum(1 for d in docs if d.holds(k)) for k in keys}
    for d in docs:
        d.src_keys = [kk for kk in d.src_keys_raw if key_df.get(kk[1], 0) <= ceiling]


def check_url(docs: list[Doc]) -> list[tuple[str, str, list[str]]]:
    """The body's own `URL:` line against the frontmatter's `url:`. Exact."""
    by_url = {}
    for d in docs:
        if d.url:
            by_url.setdefault(deaccent(d.url.rstrip("/")), d)
    findings = []
    for d in docs:
        if not d.body_url or not d.url or same_url(d.url, d.body_url):
            continue
        lines = [
            f"frontmatter url: {d.url[:100]}",
            f"body's own URL:  {d.body_url[:100]}",
        ]
        owner = by_url.get(deaccent(d.body_url.rstrip("/")))
        if owner is not None and owner is not d:
            lines.append(f"that body belongs to {owner.name}, staged in this batch")
        findings.append(("MISFILED", d.path, lines))
    return findings


def check_body(docs: list[Doc], min_title: float,
               settled: set[str] | None = None) -> list[tuple[str, str, list[str]]]:
    """The crossing check. Returns (severity, path, lines).

    A file the `url` check has already settled is skipped, in **both** directions,
    and the second direction is the one that was missing. Where the check fired,
    a structural entry is the same finding with a worse evidence line and a
    second entry against one file reads as two problems. Where the check *passed*
    — the body carries its own `URL:` line and it equals the frontmatter's — the
    file is settled exactly, and this module's opening paragraph says what
    follows: *where the line is absent, the body still has to be read
    structurally.* Absent, not present-and-matching.

    **Running the heuristic over an exactly-settled file only manufactures
    doubt** *(TUN, 2026-09-03)*. The INS *Flash Logements — RGPH 2024* PDF puts
    its cover title outside the text layer, so the extraction opens at
    `# SEPTEMBRE 2025`, scores 43% on its own title and traces neither `ins` nor
    *Institut National de la Statistique* — three structural signals against a
    body whose own `URL:` line is byte-identical to its `url:`. It was reported
    SUSPECT, verified by hand, left in place, and then reported again on every
    later pass, which is what a false positive costs when a batch driver reads
    the exit code. Nothing about the exact check is a heuristic; where it has
    spoken, the heuristics have nothing to add."""
    settled = set(settled or set()) | {
        d.path for d in docs
        if d.body_url and d.url and same_url(d.url, d.body_url)
    }
    findings = []
    for d in docs:
        if d.path in settled:
            continue
        own = d.title_score()
        ok_src, why_src = d.source_signal()
        # **A source signal does not outrank a title scoring zero.** A body that
        # repeats not one distinctive word of its own title is not a document
        # about that title, whatever else it mentions — and the source signal is
        # exactly what a crossed body can pass by accident, because the
        # organisations in this corpus cite each other constantly. GNB's WARDIP
        # environmental framework held the ITU price report, scored 0% on its own
        # title, and traced to `worldbank` because the ITU report says *World
        # Bank* in its acknowledgements. A partial title score is different: there
        # the source signal is the tiebreak it was put in for.
        blank = own == 0.0 and len(d.title_tokens) >= 3
        # The heading signal, tested against the title's *unnarrowed* tokens: a
        # heading is one line and has no room to be distinctive, so a shared
        # commonplace word is enough to settle it and the batch-rarity filter
        # would only manufacture doubt.
        #
        # **It breaks ties and does not raise doubts of its own.** What a body
        # opens with is often not its title at all but an OCR artefact, a
        # document number or a copyright line — `# P177016084979202b08dd501a…`,
        # `### RIPUBTICADA GUNIüI§§ÀU`, `© 2023 International Bank for
        # Reconstruction and Development` — and on GNB seven such headings sat on
        # top of bodies that matched their own titles at 62% to 100%. So it only
        # speaks where the title has already failed, and there it is decisive: it
        # is what identifies the news item about a transformer in Bafatá whose
        # body scored 44% on the Portuguese of a World Bank framework document.
        head_off = bool(
            d.heading
            and d.title_tokens_raw
            and not (tokens(d.heading) & d.title_tokens_raw)
        )
        weak = own < min_title
        if not (blank or (weak and (not ok_src or head_off))):
            continue
        # A file passing its own signals is not in doubt, and the counterpart
        # search is not run on it. That search compares one title against every
        # other body in the batch, so at 125 files something scores well by
        # accident often enough to matter — GNB's WTO trade policy review holds
        # its own annex and scores 100% on the World Bank WARDIP appraisal beside
        # it, because both are trade-and-project English. Used to *confirm* a
        # doubt it is decisive; used to *raise* one it is noise.
        best_other, best_score = None, -1.0
        if d.title_tokens:
            for o in docs:
                if o is d:
                    continue
                s = d.title_score(o.body_tokens)
                if s > best_score:
                    best_other, best_score = o, s
        # A body too short to repeat its own title is a thin document, not a
        # crossed one — the UPU postal profile is ten lines of postcode format.
        # It is still reported, because a crossing can be short too; it is
        # reported as something to read rather than as a pair to unpick.
        short = len(d.body.strip()) < 1500
        crossed = (
            best_other is not None
            and best_score >= 0.60
            and best_score - own >= 0.34
            and not short
        )
        lines = [
            f"title `{d.title[:80]}`",
            "title tokens in own body: "
            + (f"{own:.0%}" if own >= 0 else "no distinctive tokens (thin title)")
            + (f", body is {len(d.body.strip())} chars" if short else ""),
            f"source: {'traces to ' if ok_src else 'not traced — '}{why_src}",
            f"body opens: {d.first_line or '(empty body)'}",
        ]
        if head_off:
            lines.append(
                "the body's own heading shares no word with the title"
            )
        if crossed:
            lines.append(
                f"this title scores {best_score:.0%} on {best_other.name} — "
                "read both before moving either"
            )
            findings.append(("CROSSED", d.path, lines))
        else:
            findings.append(("SUSPECT", d.path, lines))
    return findings


def check_date(docs: list[Doc]) -> list[tuple[str, str, list[str]]]:
    findings = []
    for d in docs:
        m = DATE_PREFIX_RE.match(d.name)
        if not m:
            partial = PARTIAL_PREFIX_RE.match(d.name)
            findings.append((
                "DATE", d.path,
                ["filename date prefix is "
                 + ("partial — `reference.md` §3 pads it, `date_precision` carries "
                    "the truth" if partial else "absent or malformed")],
            ))
            continue
        if d.published and d.published[:10] != m.group(0)[:10]:
            findings.append((
                "DATE", d.path,
                [f"filename says {m.group(0)[:10]}, `published:` says {d.published}"],
            ))
    return findings


def check_yaml(docs: list[Doc]) -> list[tuple[str, str, list[str]]]:
    if yaml is None:
        return [("YAML", "", ["PyYAML is not installed; the yaml check was skipped"])]
    findings = []
    for d in docs:
        if not d.fm_text:
            findings.append(("YAML", d.path, ["no `---` frontmatter block"]))
            continue
        try:
            loaded = yaml.safe_load(d.fm_text)
        except yaml.YAMLError as exc:
            first = str(exc).splitlines()[0]
            hint = UNQUOTED_COLON_RE.search(d.fm_text)
            lines = [f"frontmatter does not parse: {first}"]
            if hint:
                lines.append(f"unquoted `{hint.group(1)}:` carrying `\": \"`")
            findings.append(("YAML", d.path, lines))
            continue
        if not isinstance(loaded, dict):
            findings.append(("YAML", d.path, ["frontmatter is not a mapping"]))
    return findings


def check_title(docs: list[Doc]) -> list[tuple[str, str, list[str]]]:
    """An ASCII title whose own body holds the accented spelling of its words.

    **Two things de-accent to a title token without being the orthography the
    title lost**, and both were found firing on clean LBR files (2026-09-03):

      - **A compatibility fold is not a diacritic.** A PDF that sets its heading
        in a maths-italic font gives `𝐿iberia`,
        which NFKD-folds to `liberia` with no combining mark anywhere in it. The
        glyph is styling the extractor kept, and there is nothing in it for a
        title to carry. So the accented form has to actually decompose to a
        combining mark to count as one.
      - **A multilingual body spells it both ways.** An EU--Liberia treaty
        carries its French and Spanish parallel text beside its English, so
        `Libéria` and `Unión` sit in a body whose own English says `Liberia` and
        `Union`. Where the plain form is in the body too, the source uses it and
        the title is not a transliteration this run did."""
    findings = []
    for d in docs:
        if not d.title or not d.title.isascii():
            continue
        words = re.findall(r"[^\W\d_]{4,}", d.body, re.UNICODE)
        plain = {w.lower() for w in words if w.isascii()}
        accented: dict[str, str] = {}
        for raw in words:
            if raw.isascii() or raw.isupper():  # all-caps PDF headers are worse
                continue
            flat = deaccent(raw)
            if flat not in d.title_tokens_raw or flat == raw.lower():
                continue
            if not any(unicodedata.combining(c)
                       for c in unicodedata.normalize("NFKD", raw)):
                continue                        # a fold, not a diacritic
            if flat in plain:
                continue                        # the source spells it both ways
            accented.setdefault(flat, raw)
        if accented:
            pairs = ", ".join(f"`{k}` -> `{v}`" for k, v in sorted(accented.items()))
            findings.append((
                "TITLE", d.path,
                [f"title is ASCII, body carries the accented form: {pairs}",
                 f"title `{d.title[:80]}`"],
            ))
    return findings


def walk(path: str) -> list[str]:
    if os.path.isfile(path):
        return [path]
    out = []
    for root, _, names in os.walk(path):
        out.extend(os.path.join(root, n) for n in sorted(names) if n.endswith(".md"))
    return sorted(out)


def batches(paths: list[str]) -> list[tuple[str, list[str]]]:
    """A batch is a directory of staged files. Files named on the command line are
    scored together as one ad-hoc batch, because that is what the caller asked
    to compare."""
    out, loose = [], []
    for p in paths:
        if os.path.isfile(p):
            loose.append(p)
        else:
            for root, _, names in os.walk(p):
                mds = [os.path.join(root, n) for n in sorted(names) if n.endswith(".md")]
                if mds:
                    out.append((root, mds))
    if loose:
        out.append(("(named on the command line)", sorted(loose)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("paths", nargs="*", default=[])
    ap.add_argument("--checks", default=",".join(ALL_CHECKS))
    ap.add_argument("--common", type=float, default=0.40)
    ap.add_argument("--min-title", type=float, default=0.55)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    checks = [c.strip() for c in args.checks.split(",") if c.strip()]
    bad = [c for c in checks if c not in ALL_CHECKS]
    if bad:
        print(f"unknown check(s): {', '.join(bad)}; known: {', '.join(ALL_CHECKS)}")
        return 2

    paths = args.paths or [NEW_QUEUE]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        for p in missing:
            print(f"not found: {p}")
        return 2

    found, unreadable = 0, []
    groups = batches(paths)
    if not groups:
        print("no staged files found")
        return 0

    for label, files in groups:
        docs, bad_reads = load_batch(files)
        unreadable.extend(bad_reads)
        narrow_titles(docs, args.common)
        findings: list[tuple[str, str, list[str]]] = []
        if "url" in checks:
            findings += check_url(docs)
        if "body" in checks:
            findings += check_body(docs, args.min_title,
                                   {p for _, p, _ in findings})
        if "date" in checks:
            findings += check_date(docs)
        if "yaml" in checks:
            findings += check_yaml(docs)
        if "title" in checks:
            findings += check_title(docs)

        print(f"{label} — {len(docs)} file(s)"
              + (f", {len(bad_reads)} unreadable" if bad_reads else ""))
        if not findings:
            print("  clean")
            continue
        order = {"MISFILED": 0, "CROSSED": 1, "SUSPECT": 2,
                 "YAML": 3, "DATE": 4, "TITLE": 5}
        for sev, path, lines in sorted(findings, key=lambda f: (order[f[0]], f[1])):
            found += 1
            print(f"  {sev}  {os.path.basename(path) if path else '(batch)'}")
            if not args.quiet:
                for ln in lines:
                    print(f"        {ln}")

    for p in unreadable:
        print(f"unreadable: {p}")
    if unreadable:
        return 2
    if not found:
        return 0
    print(f"{found} finding(s)")
    return 1


if __name__ == "__main__":
    # A finding names the title and the body line it was found in, and those carry
    # whatever the source published — accents, and on a PDF extract the mathematical
    # italic glyphs a title-orthography finding exists to report. On a console that
    # defaults to cp1252 the *printing* of such a finding raises, killing the run
    # part-way down the queue and leaving the files after it unlinted. The traceback
    # goes to stderr, so a caller reading stdout sees a short, clean-looking report.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
