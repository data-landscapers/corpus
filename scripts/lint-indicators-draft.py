"""lint-indicators-draft.py — the cheap half of the two indicator checks, run before they are.

`python scripts/lint-indicators-draft.py {ISO} {path-to-draft.csv}` from the repo root, on a draft
that has not been written into `outputs/` yet. It replicates, in one pass and without a render, every
rule that `report-render.py --check` and `report-register-check.py` would fail the file on and that
can be tested from the draft alone: the 8–40 and 25–200 word bands, the register terms and first
person, check H's rule that a figure needs a citation in its own sentence, the Progress vocabulary
and *Mixed*'s mandatory qualifying clause, that every `indicator_id` is in the frame and appears
once, that every `row_id` is on the unit's ledger, that no unsourced *Not held* placeholder is mapped
(`indicator-mapping-conventions.md`), and that every cited slug appears in the `sources` of a row the
cell maps — which is what keeps check M clean by construction.

**It verifies and never repairs**, on the same rule as the checks it stands in front of. It is not a
substitute for them: it cannot see the catalogue, so a slug that is on the ledger but absent from the
base still needs check M, and it says nothing about the rendered document. What it buys is that a
large unit's defects are found in one second rather than one render, and the two real checks then run
once.
"""
import csv, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
unit = sys.argv[1]
path = sys.argv[2]

TERMS = [
    ("first person", [r"\bwe\b", r"\bour\b", r"\bours\b"], True),
    ("tic", [r"binding constraint", r"counter-example", r"the real question",
             r"it is worth noting", r"what it does not contain", r"turns? out to be",
             r"is really about", r"the uncomfortable"], True),
    ("flash verb", [r"\blanded\b", r"\bunveil(ed|s|ing)?\b", r"rolled out", r"ramp(ed|ing) up",
                    r"doubl(ed|ing) down", r"poised to", r"sets? the stage", r"paves? the way",
                    r"marks? a turning point"], True),
    ("jargon", [r"demateriali[sz]", r"dématériali", r"attack surface", r"ecosystem",
                r"\bunlock(s|ed|ing)?\b", r"leapfrog", r"at scale", r"citizen journey",
                r"low-hanging"], False),
]
FIRST_PERSON = re.compile(r"(?<![\w'’])(I|us)(?![\w'’])")
LINK = re.compile(r"\]\((?:[^()]|\([^()]*\))*\)")
ANCHOR = re.compile(r"\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\)")
CITED_ANY = re.compile(r"\]\([^)]+\)")
FIGURE = re.compile(r"(?:US\$|R|EUR|£|\$)\s?\d[\d,.]*\s?(?:m|bn|billion|million)?"
                    r"|\b\d+(?:\.\d+)?\s?(?:%|per cent)"
                    r"|\b\d{1,3}(?:,\d{3})+\b"
                    r"|\b\d{4,}\b")
YEAR = re.compile(r"^(?:19|20)\d\d$")
BANDS = {"summary": (8, 40), "developments": (25, 200)}
VOCAB = {"Advanced", "Stalled", "Regressed", "Mixed", "No change"}

frame = {r["indicator_id"] for r in csv.DictReader(open(os.path.join(ROOT, "lookups", "indicators.csv"), encoding="utf-8-sig", newline=""))}
ledger = {r["row_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "outputs", "reports", unit, "ledger.csv"), encoding="utf-8-sig", newline=""))}

rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
bad = 0
seen = set()
for r in rows:
    iid = r["indicator_id"].strip()
    if iid not in frame:
        print(f"!! {iid}: not in the frame"); bad += 1
    if iid in seen:
        print(f"!! {iid}: duplicate row"); bad += 1
    seen.add(iid)
    prog = r["progress"].strip()
    stem = prog.split(",")[0].strip()
    if stem not in VOCAB:
        print(f"!! {iid}: progress stem {stem!r} not in vocabulary"); bad += 1
    if stem == "Mixed" and "," not in prog:
        print(f"!! {iid}: Mixed with no qualifying clause"); bad += 1
    rids = [x for x in r["row_ids"].split("|") if x]
    if not rids:
        print(f"!! {iid}: no row_ids"); bad += 1
    allowed = set()
    for rid in rids:
        if rid not in ledger:
            print(f"!! {iid}: row_id not on the ledger: {rid}"); bad += 1
        else:
            allowed |= {s for s in ledger[rid]["sources"].split("|") if s}
            if ledger[rid]["status"].strip() == "Not held" and not ledger[rid]["sources"].strip():
                print(f"!! {iid}: maps unsourced placeholder {rid}"); bad += 1
    for field in ("summary", "developments"):
        raw = (r[field] or "").strip()
        if not raw:
            print(f"!! {iid}/{field}: empty"); bad += 1; continue
        block = LINK.sub(lambda m: " " * len(m.group(0)), raw)
        countable = ANCHOR.sub(r"\1", raw)
        words = len(re.sub(r"\[([^\]]*)\]", r"\1", countable).split())
        lo, hi = BANDS[field]
        if not lo <= words <= hi:
            print(f"!! {iid}/{field}: {words} words (band {lo}-{hi})"); bad += 1
        for label, pats, icase in TERMS:
            for pat in pats:
                for mm in re.finditer(pat, block, re.I if icase else 0):
                    print(f"!! {iid}/{field}: register {label}: {mm.group(0)!r}"); bad += 1
        for mm in FIRST_PERSON.finditer(block):
            print(f"!! {iid}/{field}: register first person: {mm.group(0)!r}"); bad += 1
        for s in re.split(r"(?<=[.;])\s+", raw):
            if CITED_ANY.search(s):
                continue
            for f in dict.fromkeys(FIGURE.findall(s)):
                if not YEAR.match(f.strip()):
                    print(f"!! {iid}/{field}: uncited figure {f!r}"); bad += 1
        for m in ANCHOR.finditer(raw):
            tgt = m.group(0)[m.group(0).rindex("](") + 2:-1]
            if tgt.startswith("http"):
                print(f"!! {iid}/{field}: raw URL cited"); bad += 1
            elif tgt not in allowed:
                print(f"!! {iid}/{field}: slug not on the mapped rows: {tgt!r}"); bad += 1

print(f"\n{len(rows)} indicators, {bad} problem(s)")
