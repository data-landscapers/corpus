#!/usr/bin/env python3
r"""duplicate-briefs.py — same title, same date, two slugs: the pair, side by side.

Housekeeping job 107, strategic review 4 register R41. Lint #7 clusters only the records
a night's ingest admitted, so a pair whose halves arrived on different nights — or through
the backfill lane, which skips tier-3 dedup outright — is never compared and no pass
revisits it. A whole-vault run on 2026-09-10 found **24 pairs at a perfect 1.00**: identical
titles on the same date, which is one document under two slugs rather than two accounts of
one event. This is the evidence half. **The call per pair is OSINT's** — drop, replace or
keep-both is `CLAUDE.md` -> *Duplicates* applied by `LINT.md` #7, and it is a read of two
records, not a thing a script decides.

**Corpus cannot read OSINT's `lint-duplicate-sources.py`, so the set is reproduced rather
than imported.** `scripts/` is outside the interface (`CLAUDE.md` -> *The OSINT repo is
read-only*), and so is `reviews/source-duplicate-decisions.csv`, where the 275 already-ruled
pairs live. What a score of 1.00 means is stated in job 107 itself — identical title, same
`published` — and that is what this groups on. It agrees with every pair the job names,
including the *"six-pair São Tomé DGRN cluster"*, which is four records and therefore six
pairs. **Two consequences, and they are stated in the brief rather than worked around:** a
pair already ruled in `reviews/` will reappear here, and the count moves with the tree.

**Finance records are excluded, and that is the difference between 24 groups and 21.** A
record carrying `deal_id`, `finance_origin` or the budget keys is not a narrative source:
one donor programme replicated per recipient country legitimately shares a title across
seven records, and sending those to a duplicate queue is how a real hit gets lost among
them. They are reported separately, not dropped in silence.

**The first 300 words are the specified evidence and are the weakest of it.** A raw capture
often opens with a copyright block — the Burundi pair job 107 names as a textbook *replace*
begins with 300 words of CC licence on both sides — so the header and `URL:` lines are
skipped, and the brief leads with the record's own `note:`, which is the vault's written
account of what that capture contributes and is what actually tells two captures apart.

**Two numbers separate one document twice from two accounts of one event**, over 5-word
shingles of the two bodies. **Jaccard** near 1.0 is one capture against another. **Containment
— the smaller side's shingles found in the larger — near 1.0 with a low Jaccard is an excerpt
of the same document**, which is `LINT.md` #7's textbook *replace* and the shape job 107 names
in the Burundi pair. Low on both is two texts that merely share a title, and is not a
duplicate at all: six of the pairs here are that, and they are all one cluster.

Usage:
  python duplicate-briefs.py                          # the table, to stdout
  python duplicate-briefs.py --briefs BRIEFS.md       # the side-by-side read
  python duplicate-briefs.py --csv duplicate-pairs.csv
  python duplicate-briefs.py --all                    # keep finance records in

Exit: 0 no group found, 1 groups found (the expected outcome while job 107 is open), 2 the
tree or the index is not where the script was pointed.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import itertools
import json
import os
import re
import sys

CITE_KEYS = ("sources", "cite_through")
# A record carrying any of these is a deal or a budget line, not a narrative source. The
# two IATI clusters are the case that matters: one Korean programme replicated across
# seven recipient countries, seven records, one title, and nothing duplicated at all.
FINANCE_KEYS = ("deal_id", "finance_origin", "budget_version", "fiscal_year_label")
# The capture's own scaffolding, written by the fetch rather than by the publisher.
SCAFFOLD_RE = re.compile(r"^\s*(#{1,6}\s|URL:|Author:|Published:|Retrieved:)", re.I)
WORDS = 300
SHINGLE = 5
CSV_COLS = ["group", "pair", "published", "date_match", "title", "slug_a", "slug_b",
            "overlap", "contained",
            "same_url", "same_host", "cites_a", "cites_b", "words_a", "words_b",
            "completeness_a", "completeness_b", "publisher_a", "publisher_b",
            "lane_a", "lane_b", "artefact_a", "artefact_b", "hub_linked"]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def narrative(fm):
    return not any(fm.get(k) for k in FINANCE_KEYS)


def by_title(index_dir, tree, keep_finance=False):
    """title -> [row], over the records this job is about."""
    out = collections.defaultdict(list)
    with open(os.path.join(index_dir, "files.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row["d"].get("ext") != ".md" or not row["path"].startswith(tree + "/"):
                continue
            fm = row["fm"] or {}
            if not keep_finance and not narrative(fm):
                continue
            if fm.get("title"):
                out[fm["title"]].append(row)
    return out


def day(value):
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def groups(index_dir, tree, keep_finance=False, days=0):
    """[(title, [published…], [row])] — one entry per cluster of records sharing a title.

    `days` is how far the `published` dates inside a cluster may spread. **At 0 this is
    exactly what a score of 1.00 means** — identical title, identical date — which is the
    set job 107 registered, and it is the default for that reason.

    **At 7 it catches the case job 107 names and the exact grouping cannot see.** The three
    AU data-governance validation records are one press release: two carry 2025-12-02 and
    the third, the PDF, carries 2025-12-01. A day apart is the same document filed from two
    captures whose date lines disagree, not two documents, and over the whole vault a
    seven-day window adds three clusters — cheap enough to report and too pointed to omit.
    """
    out = []
    for title, rows_ in sorted(by_title(index_dir, tree, keep_finance).items()):
        if len(rows_) < 2:
            continue
        dated = sorted(((day((r["fm"] or {}).get("published")), r) for r in rows_),
                       key=lambda p: (p[0] is None, p[0] or dt.date.min,
                                      p[1]["d"]["slug"]))
        cluster = []
        for date, row in dated:
            if cluster and (date is None or cluster[0][0] is None
                            or (date - cluster[0][0]).days > days):
                if len(cluster) > 1:
                    out.append((title, [c[0] for c in cluster], [c[1] for c in cluster]))
                cluster = []
            cluster.append((date, row))
        if len(cluster) > 1:
            out.append((title, [c[0] for c in cluster], [c[1] for c in cluster]))
    return out


def citations(index_dir):
    """slug -> distinct citing pages. A page counts once; a self-reference never counts."""
    seen, count = set(), collections.Counter()
    with open(os.path.join(index_dir, "links.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            edge = json.loads(line)
            if edge["via"] not in CITE_KEYS and edge["via"] != "body":
                continue
            key = (edge["from"], edge["to"])
            if key in seen or edge["from"].endswith("/" + edge["to"] + ".md"):
                continue
            seen.add(key)
            count[edge["to"]] += 1
    return count


def body_of(root, path):
    """The capture's prose, with the fetch's own header lines dropped.

    Read from the file rather than the index: the index carries frontmatter and link
    edges, deliberately, and a body column there would double its size for one consumer.
    """
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    import vault_lib as V                                                     # noqa: E402
    text = open(os.path.join(root, path), "rb").read().decode("utf-8", "replace")
    _, _, body = V.parse_frontmatter(text)
    lines = body.split("\n")
    i = 0
    while i < len(lines) and (not lines[i].strip() or SCAFFOLD_RE.match(lines[i])):
        i += 1
    return "\n".join(lines[i:]).strip()


def shingles(text, n=SHINGLE):
    words = re.findall(r"[^\W_]+", text.lower(), re.UNICODE)
    return {tuple(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def overlap(a, b):
    """(jaccard, containment) over 5-word shingles. **Both, because neither alone decides.**

    Shingles rather than a bag of words: two reports on one event share most of their
    vocabulary and almost none of their sentences.

    **Jaccard** is the test for one capture against another — near 1.0 and the two records
    hold the same text. It punishes a size difference hard, so it cannot tell an excerpt of
    a document from a different document: a 200-word capture inside a 40,000-word one reads
    about 0.005 either way.

    **Containment** — the smaller side's shingles found in the larger — answers exactly
    that, and is the number the *replace* call is made on. It reads 1.0 whenever one side is
    short, which is why it is never reported alone. Low Jaccard with high containment is
    `LINT.md` #7's textbook replace; low on both is usually two different texts that happen
    to share a title.

    **Usually, and the exception is loud.** Both numbers are computed on characters, so a
    capture that is OCR of a scanned original scores near zero against a clean capture of
    the *same* document — group 1 here is one Nigerian Act read twice, one of them as
    mush, at 0.00 on both. A low pair is a pair to read, never a pair to dismiss.
    """
    sa, sb = shingles(a), shingles(b)
    if not sa or not sb:
        return 0.0, 0.0
    return len(sa & sb) / len(sa | sb), len(sa & sb) / min(len(sa), len(sb))


def host(url):
    m = re.match(r"https?://([^/]+)", str(url or ""), re.I)
    return (m.group(1).lower().removeprefix("www.") if m else "")


def flat(v):
    if isinstance(v, list):
        return "; ".join(flat(x) for x in v)
    return str(v) if v is not None else ""


def facts(root, row, cites):
    fm = row["fm"] or {}
    body = body_of(root, row["path"])
    return {
        "slug": row["d"]["slug"], "path": row["path"], "fm": fm, "body": body,
        "words": len(body.split()),
        "cites": cites.get(row["d"]["slug"], 0),
        "host": host(fm.get("url")),
        # Which lane brought it in. The backfill lane skips tier-3 dedup outright
        # (`wiki/index.md`), so a pair with one half from it is the shape job 107
        # describes rather than a coincidence.
        "lane": flat(fm.get("sweep_batch")),
    }


def rows(root, index_dir, tree, keep_finance=False, near_days=0):
    """The pairs, exact-date clusters first and the near-date ones after.

    A near-date cluster is reported as its own entry and flagged, never merged into the
    queue: job 107's set is the exact one, and a brief that quietly widened it would be
    answering a different question from the one the register asked.
    """
    cites = citations(index_dir)
    exact = groups(index_dir, tree, keep_finance, days=0)
    seen = {tuple(sorted(r["d"]["slug"] for r in members)) for _, _, members in exact}
    near = [g for g in groups(index_dir, tree, keep_finance, days=near_days)
            if tuple(sorted(r["d"]["slug"] for r in g[2])) not in seen] if near_days else []
    ordered = (sorted(exact, key=lambda g: (str(g[1][0]), g[0]))
               + sorted(near, key=lambda g: (str(g[1][0]), g[0])))
    out = []
    for n, (title, dates, members) in enumerate(ordered, 1):
        key = (title, str(dates[0]) if len(set(dates)) == 1
               else "%s … %s" % (dates[0], dates[-1]))
        is_near = len(set(dates)) > 1
        got = [facts(root, m, cites) for m in sorted(members, key=lambda m: m["d"]["slug"])]
        for a, b in itertools.combinations(got, 2):
            jaccard, contained = overlap(a["body"], b["body"])
            # A pair the hub line already links is ruled keep-both and is not a candidate;
            # job 107 counts 398 of them separately. Corpus cannot read `reviews/`, so this
            # is the only already-ruled class it can see, and seeing one is worth saying.
            linked = (b["slug"] in flat(a["fm"].get("hub_line_sources"))
                      or a["slug"] in flat(b["fm"].get("hub_line_sources")))
            out.append({"group": n, "key": key, "a": a, "b": b, "near": is_near,
                        "overlap": jaccard, "contained": contained,
                        "hub_linked": linked})
    return out


# ---------------------------------------------------------------- reporting

def first_words(body, n=WORDS):
    words = body.split()
    text = " ".join(words[:n])
    return text + (" …" if len(words) > n else "")


def side_by_side(pair):
    a, b = pair["a"], pair["b"]
    fa, fb = a["fm"], b["fm"]
    lines = []
    lines.append("| | **A** `%s` | **B** `%s` |" % (a["slug"], b["slug"]))
    lines.append("|---|---|---|")
    for label, key in (("publisher", "publisher"), ("author", "author"),
                       ("date precision", "date_precision"),
                       ("completeness", "body_completeness"),
                       ("doc type", "doc_type"), ("source tier", "source_tier"),
                       ("places", "places"), ("topics", "topics"),
                       ("entities", "entities"), ("ingested", "ingested"),
                       ("retrieved", "retrieved")):
        va, vb = flat(fa.get(key)), flat(fb.get(key))
        if va or vb:
            same = " " if va != vb else " *(same)* "
            lines.append("| %s | %s |%s%s |" % (label, va or "—", same if va == vb else " ",
                                                vb or "—"))
    lines.append("| lane | %s | %s |" % (a["lane"] or "—", b["lane"] or "—"))
    lines.append("| artefact | %s | %s |" % (flat(fa.get("artefact")) or "—",
                                             flat(fb.get("artefact")) or "—"))
    lines.append("| body words | %s | %s |" % (f"{a['words']:,}", f"{b['words']:,}"))
    lines.append("| **citations** | **%d** | **%d** |" % (a["cites"], b["cites"]))
    lines.append("| url | %s | %s |" % (flat(fa.get("url")) or "—", flat(fb.get("url")) or "—"))
    return "\n".join(lines)


def briefs(found, title_prefix="Job 107"):
    out = []
    for n in sorted({p["group"] for p in found}):
        members = [p for p in found if p["group"] == n]
        key = members[0]["key"]
        out.append("### %d. %s" % (n, key[0]))
        out.append("")
        n_rec = len({m["a"]["slug"] for m in members} | {m["b"]["slug"] for m in members})
        out.append("*%s — %d records, %d pair%s.*"
                   % (key[1], n_rec, len(members), "" if len(members) == 1 else "s"))
        out.append("")
        for pair in members:
            a, b = pair["a"], pair["b"]
            flags = []
            flags.append("**overlap %.2f**, **containment %.2f**"
                         % (pair["overlap"], pair["contained"]))
            if a["fm"].get("url") and a["fm"].get("url") == b["fm"].get("url"):
                flags.append("**same URL**")
            elif a["host"] and a["host"] == b["host"]:
                flags.append("same host `%s`" % a["host"])
            else:
                flags.append("`%s` against `%s`" % (a["host"] or "—", b["host"] or "—"))
            if pair["near"]:
                flags.append("**dates differ** — not in job 107's exact set")
            if pair["hub_linked"]:
                flags.append("**already linked by `hub_line_sources`**")
            out.append(" · ".join(flags))
            out.append("")
            out.append(side_by_side(pair))
            out.append("")
            for side, rec in (("A", a), ("B", b)):
                note = flat(rec["fm"].get("note"))
                if note:
                    out.append("**%s note.** %s" % (side, note))
                    out.append("")
            for side, rec in (("A", a), ("B", b)):
                out.append("**%s, first %d words.** %s" % (side, WORDS,
                                                           first_words(rec["body"])))
                out.append("")
        out.append("")
    return "\n".join(out)


def table(found):
    for pair in found:
        a, b = pair["a"], pair["b"]
        print("%2d%s ovl %.2f  cont %.2f  cites %d/%d  words %s/%s  %s"
              % (pair["group"], "~" if pair["near"] else " ",
                 pair["overlap"], pair["contained"], a["cites"], b["cites"],
                 a["words"], b["words"], (pair["key"][0] or "")[:44]))
        print("      %s" % a["slug"])
        print("      %s%s" % (b["slug"], "   [hub-linked]" if pair["hub_linked"] else ""))


def csv_rows(found):
    out = []
    for i, pair in enumerate(found, 1):
        a, b = pair["a"], pair["b"]
        out.append({
            "group": pair["group"], "pair": i,
            "published": pair["key"][1], "title": pair["key"][0],
            "date_match": "near" if pair["near"] else "exact",
            "slug_a": a["slug"], "slug_b": b["slug"],
            "overlap": "%.3f" % pair["overlap"],
            "contained": "%.3f" % pair["contained"],
            "same_url": "yes" if a["fm"].get("url") == b["fm"].get("url") else "no",
            "same_host": "yes" if a["host"] and a["host"] == b["host"] else "no",
            "cites_a": a["cites"], "cites_b": b["cites"],
            "words_a": a["words"], "words_b": b["words"],
            "completeness_a": flat(a["fm"].get("body_completeness")),
            "completeness_b": flat(b["fm"].get("body_completeness")),
            "publisher_a": flat(a["fm"].get("publisher")),
            "publisher_b": flat(b["fm"].get("publisher")),
            "lane_a": a["lane"], "lane_b": b["lane"],
            "artefact_a": "yes" if a["fm"].get("artefact") else "no",
            "artefact_b": "yes" if b["fm"].get("artefact") else "no",
            "hub_linked": "yes" if pair["hub_linked"] else "no",
        })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the repository root (default: cwd)")
    ap.add_argument("--tree", default="raw", help="the tree to group (default: raw)")
    ap.add_argument("--index", default=None,
                    help="an index/ with files.jsonl and links.jsonl (default: <root>/index)")
    ap.add_argument("--near-days", type=int, default=7,
                    help="also report same-title clusters whose dates spread this far "
                         "(default 7; 0 for the exact set alone)")
    ap.add_argument("--all", action="store_true",
                    help="keep finance and budget records in the grouping")
    ap.add_argument("--briefs", default=None, help="write the side-by-side read here")
    ap.add_argument("--csv", default=None, help="write the pair table here")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, args.tree)):
        print("no %s/ under %s" % (args.tree, root), file=sys.stderr)
        return 2
    index_dir = args.index or os.path.join(root, "index")
    if not os.path.isfile(os.path.join(index_dir, "files.jsonl")):
        print("no files.jsonl under %s -- build the index first" % index_dir, file=sys.stderr)
        return 2

    found = rows(root, index_dir, args.tree, args.all, args.near_days)
    exact = [p for p in found if not p["near"]]
    near = [p for p in found if p["near"]]
    print("%s/: %d group(s) of identical title and date, %d pair(s)"
          % (args.tree, len({p["group"] for p in exact}), len(exact)))
    if args.near_days:
        print("     plus %d group(s), %d pair(s), sharing a title with dates up to "
              "%d day(s) apart" % (len({p["group"] for p in near}), len(near),
                                   args.near_days))
    print()
    table(found)

    if args.briefs:
        with open(args.briefs, "w", encoding="utf-8") as fh:
            fh.write(briefs(found))
        print("\nbriefs -> %s" % args.briefs)
    if args.csv:
        with open(args.csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=CSV_COLS)
            w.writeheader()
            w.writerows(csv_rows(found))
        print("%d row(s) -> %s" % (len(found), args.csv))

    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
