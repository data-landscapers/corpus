# -*- coding: utf-8 -*-
r"""claim-audit.py — the nightly claim audit: a random sample of published claims, judged blind.

Strategic review 2026-11-26, R182. A fresh reader sees one sentence and the held text of the
source it cites, nothing else, and answers **supported**, **overstated**, **unsupported** or
**wrong figure**. A line a claim goes to `logs/claim-audit.csv`; after thirty nights the rate by
document type goes on the Statistics page.

    python scripts/claim-audit.py sample --n 500 [--seed S] [--batch 50]   # -> logs/claim-audit/
    python scripts/claim-audit.py record logs/claim-audit/DATE-NN.verdicts.csv ...
    python scripts/claim-audit.py rate                                       # by type and language
    python scripts/claim-audit.py brief logs/claim-audit/DATE-NN.md          # one reader's whole brief

**A night** (`CYCLE.md` step 4a): `sample` 100, one fresh sub-agent a worksheet given only
`brief`'s text, `record`, then repair each failure before the render and fill `repaired`.
A failure in a Corpus file (Status, Maturity, bulletin, Who's Who, budget line) is fixed in
place, in its own lookup or in the budget follow-ups; one in a field OSINT writes (a finance
row's frontmatter) goes to OSINT as one note for the night. A verdict the reader reached on the
wrong text (a multi-link sentence before 2026-11-26, a URL several records share) is re-read
and the line says so in `reason`.

**The pool.** Six document types, each a sentence or a row that names its source:

- `status` — a linked sentence of a country's Status report (`outputs/reports/*/*-status.md`);
- `maturity` — a linked sentence of a maturity paragraph (`outputs/maturity/*/paragraphs.csv`,
  every cell R162 rewrote);
- `bulletin` — a sentence of a bulletin item's summary, against the item's headline link;
- `finance` — a non-state finance row, said as one sentence, against its `url`;
- `whoswho` — a Who's Who row (*name was position at organisation in year*), against its first
  held source;
- `budget` — a budget line (*amount at stage for programme in year*), against the cited page of
  the budget document in the mirror's `budget-archive/`.

A claim whose source is not held on this machine cannot be judged and is not drawn; the pool
counts print what was left out. **Stratified** by type first (equal shares), then by the source's
language inside each type, in proportion to the square root of each language's count, so French,
Portuguese and Arabic sources are drawn more often than their share and their rate is readable.

**The worksheet is `cite-reread.py`'s**: its passage retrieval picks the lines of the held text
most likely to settle the claim, and the held file's path is printed for a claim the passages do
not settle. The worksheet does not carry *figures not in source*: that is a hint, and the reader
is blind. `verdict` is one of the four answers, or `not judgeable` where the held text proved empty or
unreadable, or the figure is one Corpus derived (a share, a sum), which is counted apart and
never in a rate.

**Failures are repaired the same night and their cause counted** (`cause`, `repaired` in the
log). The cause vocabulary is `CAUSES` below.
"""
import argparse, csv, datetime as dt, glob, hashlib, importlib.util, io, math, os, random, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import status_lib  # noqa: E402
import logging
logging.getLogger("pypdf").setLevel(logging.ERROR)
from osint_lib import MIRROR  # noqa: E402

_spec = importlib.util.spec_from_file_location("cite_reread", os.path.join(HERE, "cite-reread.py"))
cr = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(cr)

OUT = os.path.join(REPO, "logs", "claim-audit")
LOG = os.path.join(REPO, "logs", "claim-audit.csv")
ARCHIVE = os.path.join(MIRROR, "budget-archive")
TYPES = ("status", "maturity", "bulletin", "finance", "whoswho", "budget")
VERDICTS = ("supported", "overstated", "unsupported", "wrong figure", "not judgeable")
CAUSES = ("source says less", "wrong source linked", "figure miscopied", "date wrong",
          "name or title wrong", "extraction error", "inference stated as fact", "other")
BRIEF = r"""You are a blind fact-checker. Read the worksheet `{ws}`. Each claim comes with the held text of the
source it cites. Judge ONLY from that text, following the instructions at the top of the worksheet; where a claim
names the part a source is cited for, judge that part. If the passages shown do not settle a claim, Read the held text
file named on its `**Held text:**` line (relative paths are under C:\CORPUS). No web access, no other knowledge.
Every file is READ-ONLY except your output, and never run git anywhere, above all not in C:\OSINT.

Write `{out}` (UTF-8 CSV) with header `claim_id,verdict,reason,cause`, one row per claim. `verdict`: supported,
overstated, unsupported, wrong figure or not judgeable. `reason`: at most 20 words, what the source says where it
differs. `cause`, only when not supported, exactly one of: """ + ", ".join(CAUSES) + r""". Minor paraphrase is
supported; a different year, amount, title, or a certainty the source lacks is not. Reply with the count per verdict."""
FIELDS = ["date", "claim_id", "doc_type", "language", "where", "url", "claim", "verdict",
          "reason", "cause", "repaired"]

_STOP = {
    "en": "the and of to in is for that with was by on are from has have this which".split(),
    "fr": "le la les des et du un une est pour dans par sur au aux qui que avec sont".split(),
    "pt": "o a os as do da dos das em para com por um uma que no na não são ao".split(),
}


def language(text):
    t = text[:6000]
    if len(re.findall(r"[؀-ۿ]", t)) > 200:
        return "ar"
    words = re.findall(r"[a-zà-ÿ]+", t.lower())
    score = {k: sum(1 for w in words if w in set(v)) for k, v in _STOP.items()}
    best = max(score, key=score.get)
    return best if score[best] >= 5 else "other"


class Held:
    """Held text by URL: the catalogue's body in `raw/`, read once."""

    def __init__(self):
        self.cat, self.raw, self.cache = cr.load_catalogue(), cr.load_raw_paths(), {}

    def path(self, url, claim="", own=None):
        """The held body a claim cites. `own` is a record slug the row names itself (finance).
        A URL several records share (an OECD CRS query is one per donor and country, and holds
        up to 34 projects) resolves to the record whose text best matches the claim, never
        simply the first: the first was what the readers judged as a wrong source on 2026-11-26."""
        if own and own in self.raw:
            return self.raw[own]
        slugs = []
        for v in status_lib._variants(url.strip()):
            slugs += [s for s in self.cat.get(v, []) if s in self.raw and s not in slugs]
        if len(slugs) <= 1 or not claim:
            return self.raw[slugs[0]] if slugs else None
        def score(s):
            ps, missing = cr.passages(self.text(self.raw[s]), claim, k=3)
            return (-len(missing), sum(int(p[1:p.index("]")]) for p in ps))
        return self.raw[max(slugs, key=score)]

    def text(self, path):
        if path not in self.cache:
            t = io.open(path, encoding="utf-8", errors="replace").read()
            t = status_lib.body(t)
            self.cache[path] = re.split(r"^\*\*Sweep note", t, maxsplit=1, flags=re.M)[0]
        return self.cache[path]


def _linked(text, where, doc_type, held, out):
    for si, sent in enumerate(cr.sentences(text), 1):
        for m in cr.LINK.finditer(sent):
            url = m.group(2) or m.group(3)
            claim = cr.flat(sent)
            # a sentence carrying several links is judged, for each, on that link's own words
            part = cr.flat(m.group(0)) if len(cr.LINK.findall(sent)) > 1 else ""
            out.append(dict(doc_type=doc_type, where=f"{where} s{si}", url=url, claim=claim, part=part,
                            src=held.path(url, part or claim)))


def pool_status(held):
    out = []
    for p in sorted(glob.glob(os.path.join(REPO, "outputs", "reports", "*", "*-status.md"))):
        unit = os.path.basename(p)[:-10]
        for slug, label, prose in status_lib.sections(io.open(p, encoding="utf-8").read()):
            for pi, para in enumerate(status_lib.paragraphs(prose), 1):
                if para.startswith("<!--"):
                    continue
                _linked(para, f"reports/{unit}/{unit}-status.md {slug} p{pi}", "status", held, out)
    return out


def pool_maturity(held):
    out = []
    for p in sorted(glob.glob(os.path.join(REPO, "outputs", "maturity", "*", "paragraphs.csv"))):
        study = os.path.basename(os.path.dirname(p))
        with open(p, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                _linked(r["paragraph"], f"maturity/{study} {r['iso3']} {r['indicator_id']}", "maturity", held, out)
    return out


def pool_bulletin(held):
    out = []
    for p in glob.glob(os.path.join(REPO, "outputs", "bulletins", "*.md")):
        text = io.open(p, encoding="utf-8").read()
        for item in re.findall(r'<div class="bulletin-item"[^>]*>(.*?)</div>', text, flags=re.S):
            head = re.search(r"\*\*\[([^\]]+)\]\((https?://[^)\s]+)\)\*\*", item)
            if not head:
                continue
            summ = item[head.end():].split("\n\n", 1)[-1]
            summ = re.sub(r"<span.*?</span>", "", summ, flags=re.S).strip()
            for si, s in enumerate(status_lib.sentences(summ), 1):
                out.append(dict(doc_type="bulletin", where=f"bulletins/{os.path.basename(p)} '{head.group(1)[:50]}' s{si}",
                                url=head.group(2), claim=cr.flat(s), src=held.path(head.group(2), cr.flat(s))))
    return out


def pool_finance(held):
    out = []
    with open(status_lib.FINANCE_CSV, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            u = (r.get("url") or "").strip()
            if not u.startswith("http"):
                continue
            # a USD-native record has no original amount; its US$ figure is said only when whole
            amt = r["original_amount"] or ("an amount" if r["commitment_usd_m"] else "an unstated amount")
            # a partial or unclear row counts a share of the deal: derived, so not put to the reader
            usd = f" (US${r['commitment_usd_m']}m)" if r["commitment_usd_m"] and r["scope"] == "whole" else ""
            yrs = "-".join(x for x in (r["start_year"], r["end_year"]) if x)
            claim = (f"{r['financier']} provides {r['recipient']} a {r['instrument'].lower()} of {amt}{usd}"
                     f"{', ' + yrs if yrs else ''}, status {r['status'].lower()}, for: {r['scope_basis'] or r['title']}"
                     f"{'; recipient organisation ' + r['recipient_organisation'] if r['recipient_organisation'] else ''}.")
            out.append(dict(doc_type="finance", where=f"non-state-finance {r['record']}", url=u, claim=claim,
                            src=held.path(u, claim, own=r["record"])))
    return out


def pool_whoswho(held):
    out = []
    with open(os.path.join(REPO, "outputs", "whos-who", "whos-who.csv"), encoding="utf-8-sig", newline="") as fh:
        for i, r in enumerate(csv.DictReader(fh), 2):
            urls = [u.strip() for u in status_lib._URL_SEP.split(r["source_url"] or "") if u.strip().startswith("http")]
            claim = f"{r['name'].lstrip(chr(39))} was {r['position']} at {r['organisation']} ({r['country']}) in {r['year']}."
            got = next(((u, held.path(u, claim)) for u in urls if held.path(u)), (urls[0], None) if urls else None)
            if not got:
                continue
            out.append(dict(doc_type="whoswho", where=f"whos-who.csv line {i}", url=got[0], claim=claim, src=got[1]))
    return out


def _budget_doc(iso, slug):
    slug = re.sub(r"-companion$", "", slug)
    hits = glob.glob(os.path.join(ARCHIVE, iso, "*", slug + ".*"))
    pref = [h for h in hits if h.endswith(".ocr.txt")] + [h for h in hits if h.endswith(".pdf")] + \
           [h for h in hits if h.endswith((".md", ".txt", ".html"))]
    return pref[0] if pref else None


def pool_budget(held):
    out = []
    for p in sorted(glob.glob(os.path.join(REPO, "outputs", "budgets", "*-budget.csv"))):
        iso = os.path.basename(p)[:3]
        with open(p, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                # the locator cites the baseline stage's page first, so that is the figure judged
                base = r.get("baseline_stage") or ""
                stage = base if r.get(base) else next(
                    (s for s in ("audited", "actual", "released", "revised", "appropriated", "proposed") if r.get(s)), None)
                # a partial chapter row is a sum of the lines taken, not a figure the page prints
                if not stage or not r.get("source_slug") or (r.get("programme_level") == "chapter" and r.get("scope_confidence") != "whole"):
                    continue
                what = " / ".join(x for x in (r["spending_entity"] or r["admin_head"], r["programme"], r["sub_programme"]) if x and x != "not printed")
                claim = f"FY {r['fy']}: {what} — {stage} {r[stage]} {r['currency']}."
                doc = _budget_doc(iso, r["source_slug"])
                out.append(dict(doc_type="budget", where=f"budgets/{os.path.basename(p)} {r['record']}",
                                url=r["doc_locator"], claim=claim, src=doc))
    return out


def budget_text(path, locator):
    """The cited page of a budget document, or the whole extracted text where no page is cited."""
    m = re.search(r"PDF p\.?\s*(\d+)", locator or "")
    if path.endswith(".pdf"):
        import pypdf
        try:
            rd = pypdf.PdfReader(path)
            pages = [int(m.group(1)) - 1] if m else range(min(len(rd.pages), 40))
            return "\n".join((rd.pages[i].extract_text() or "") for i in pages if 0 <= i < len(rd.pages))
        except Exception:
            return ""
    t = io.open(path, encoding="utf-8", errors="replace").read()
    if m and "\f" in t:
        pg = t.split("\f")
        i = int(m.group(1)) - 1
        return "\n".join(pg[max(0, i - 1):i + 2]) if i < len(pg) else t
    return t


def source_text(c, held):
    if c["doc_type"] == "budget":
        return budget_text(c["src"], c["url"])
    return held.text(c["src"])


def cmd_sample(a):
    rnd = random.Random(a.seed)
    held = Held()
    pools = {t: [c for c in globals()["pool_" + t](held)] for t in TYPES}
    print("pool (claims / held):", "  ".join(f"{t} {len(v)}/{sum(1 for c in v if c['src'])}" for t, v in pools.items()))
    quota = {t: a.n // len(TYPES) + (1 if i < a.n % len(TYPES) else 0) for i, t in enumerate(TYPES)}
    drawn = []
    for t in TYPES:
        cands = [c for c in pools[t] if c["src"]]
        rnd.shuffle(cands)
        # language is read from the source text, so only for what might be drawn: 6x the quota
        cands = cands[: quota[t] * 6]
        by = defaultdict(list)
        for c in cands:
            c["text"] = source_text(c, held)
            if len(c["text"].split()) < 20:
                continue
            c["language"] = language(c["text"])
            by[c["language"]].append(c)
        w = {k: math.sqrt(len(v)) for k, v in by.items()}
        tot = sum(w.values()) or 1
        take = {k: min(len(by[k]), round(quota[t] * w[k] / tot)) for k in by}
        short = quota[t] - sum(take.values())
        for k in sorted(by, key=lambda k: -len(by[k])):   # top up from the largest
            extra = min(short, len(by[k]) - take[k]); take[k] += extra; short -= extra
        for k, v in by.items():
            drawn += v[: take[k]]
    rnd.shuffle(drawn)
    today = a.date or dt.date.today().isoformat()
    os.makedirs(OUT, exist_ok=True)
    for c in drawn:
        c["claim_id"] = hashlib.sha1((c["where"] + c["claim"]).encode()).hexdigest()[:10]
    nb = math.ceil(len(drawn) / a.batch)
    for b in range(nb):
        part = drawn[b * a.batch:(b + 1) * a.batch]
        w = [f"# Claim audit {today}, batch {b + 1:02d} of {nb:02d}", "",
             "For each claim: read the sentence, then the source text. Answer only from the source text. "
             "`supported` — the source says it. `overstated` — the source says something weaker, narrower or less certain. "
             "`unsupported` — the source does not say it. `wrong figure` — the source gives a different number, date or amount. "
             "`not judgeable` — the source text is empty or unreadable. A figure written another way (1.35 GW for 1,350 MW) is the same figure. Budget amounts are in whole currency units; the document may print them in thousands or millions. A pronoun (it, he, the agency) refers to what the source is about; judge what the sentence asserts.", ""]
        for c in part:
            ps, _ = cr.passages(c["text"], c["claim"], k=5, width=700)
            w += [f"## {c['claim_id']}", f"**Claim:** {c['claim']}"]
            if c.get("part"):
                w.append(f"**Judge only the part this source is cited for:** {c['part']}")
            w.append(f"**Cites:** {c['url']}")
            src = c["src"] if c["doc_type"] == "budget" else os.path.relpath(c["src"], REPO)
            w.append(f"**Held text:** `{src}`" + (f" (the cited page: {c['url']})" if c["doc_type"] == "budget" else ""))
            if c["doc_type"] == "budget":
                pg = c["text"]
                w.append("```\n" + (pg if len(pg) < 9000 else "\n".join(p[4:] for p in ps) or pg[:9000]) + "\n```")
            else:
                lead = " ".join(c["text"].split()[:120])
                w.append(f"> {lead}")
                for p in ps:
                    w.append(f"> {p}")
            w.append("")
        io.open(os.path.join(OUT, f"{today}-{b + 1:02d}.md"), "w", encoding="utf-8", newline="\n").write("\n".join(w) + "\n")
        with open(os.path.join(OUT, f"{today}-{b + 1:02d}.claims.csv"), "w", encoding="utf-8", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=["claim_id", "doc_type", "language", "where", "url", "claim", "part", "src"], lineterminator="\n", extrasaction="ignore")
            wr.writeheader(); wr.writerows(part)
    print(f"drawn {len(drawn)}:", dict(Counter(c["doc_type"] for c in drawn)), dict(Counter(c["language"] for c in drawn)))
    print(f"{nb} worksheets in {os.path.relpath(OUT, REPO)}")


def cmd_record(a):
    rows = []
    for vf in a.files:
        claims = {r["claim_id"]: r for r in csv.DictReader(open(vf.replace(".verdicts.csv", ".claims.csv"), encoding="utf-8"))}
        date = os.path.basename(vf)[:10]
        for v in csv.DictReader(open(vf, encoding="utf-8-sig")):
            c = claims.get(v["claim_id"])
            if not c:
                raise SystemExit(f"{vf}: {v['claim_id']} is not in the batch")
            if v["verdict"] not in VERDICTS:
                raise SystemExit(f"{vf}: {v['claim_id']} verdict {v['verdict']!r}")
            if v.get("cause") and v["cause"] not in CAUSES:
                raise SystemExit(f"{vf}: {v['claim_id']} cause {v['cause']!r}")
            rows.append({**{k: c.get(k, "") for k in FIELDS}, "date": date, **{k: v.get(k, "") for k in ("verdict", "reason", "cause", "repaired")}})
    old = list(csv.DictReader(open(LOG, encoding="utf-8"))) if os.path.exists(LOG) else []
    keys = {(r["date"], r["claim_id"]) for r in rows}
    if a.replace:   # a re-judged claim replaces its line: the source it was judged against was wrong
        old = [r for r in old if (r["date"], r["claim_id"]) not in keys]
    else:
        seen = {(r["date"], r["claim_id"]) for r in old}
        rows = [r for r in rows if (r["date"], r["claim_id"]) not in seen]
    with open(LOG, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        wr.writeheader()
        wr.writerows(old + rows)
    print(f"recorded {len(rows)} claims to {os.path.relpath(LOG, REPO)}")


def cmd_rate(a):
    rows = [r for r in csv.DictReader(open(LOG, encoding="utf-8")) if r["verdict"] != "not judgeable"]
    for key in ("doc_type", "language"):
        g = defaultdict(Counter)
        for r in rows:
            g[r[key]][r["verdict"]] += 1
        print(f"by {key}:")
        for k, c in sorted(g.items()):
            n = sum(c.values())
            print(f"  {k:10} {n:4}  supported {100 * c['supported'] / n:5.1f}%  " +
                  "  ".join(f"{v} {c[v]}" for v in VERDICTS[1:4] if c[v]))
    fails = Counter(r["cause"] for r in rows if r["verdict"] != "supported")
    print("causes:", dict(fails))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample"); s.add_argument("--n", type=int, default=100); s.add_argument("--seed", default=None)
    s.add_argument("--batch", type=int, default=50); s.add_argument("--date")
    r = sub.add_parser("record"); r.add_argument("files", nargs="+")
    r.add_argument("--replace", action="store_true", help="re-judged claims replace their line")
    sub.add_parser("rate")
    b = sub.add_parser("brief"); b.add_argument("worksheet")
    a = ap.parse_args()
    if a.cmd == "brief":
        print(BRIEF.format(ws=os.path.abspath(a.worksheet), out=os.path.abspath(a.worksheet)[:-3] + ".verdicts.csv"))
        return
    if a.cmd == "sample" and a.seed is None:
        a.seed = a.date or dt.date.today().isoformat()
    {"sample": cmd_sample, "record": cmd_record, "rate": cmd_rate}[a.cmd](a)


if __name__ == "__main__":
    main()
