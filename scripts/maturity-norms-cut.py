#!/usr/bin/env python3
r"""maturity-norms-cut.py — cut `lookups/maturity-norms.csv` from the norms register.

    python scripts/maturity-norms-cut.py            # write the lookup
    python scripts/maturity-norms-cut.py --check    # exit 1 if the lookup differs from a fresh cut

**The register is the source and this is a cut of it, not a retyping** (task C1,
`documentation/archived/maturity-assessment-tasks.md`). `documentation/archived/maturity-assessment-norms.md` §3
holds one row per assessed indicator — kind, tier, anchor, provision, fixes, reference — and a
note under each chapter's table; §4 holds each instrument once, with who adopted it, when, its
status and the URL checked. The lookup is the join: one row per assessed indicator, its §3 cells
as written, and its primary anchor's §4 entry parsed for body, date, status and URL. So the two
cannot disagree at birth, and a correction to the register reaches the lookup by re-running this.

**Only names are mapped by hand.** §3 cites instruments by short name (*DTS*, *Malabo Art. 14*,
*Smart Africa Blueprint*) and §4 by full title; `ALIASES` says which §4 entry a short name means
and nothing else. No date, body or status is typed here. An anchor that resolves to nothing stops
the cut rather than writing an empty row.

**What is parsed, and how loosely.** `adopting_body` and `adopted` come from the first clause of
the §4 entry; `status` from its wording (*not in force*, *in force*, *non-binding*, *not adopted
by an organ*); `url` is the entry's first link; `vintage` is the year the instrument was adopted,
because the rubric freezes each norm as adopted. The §4 prose is written for readers, so these
fields are as good as that first clause — read them against the register when one looks odd.

**`not verified` is carried, never dropped.** A row whose note, or whose instrument's §4 entry,
still says something is not verified has that said first in `notes`, so the check that D3 runs
and anyone reading the lookup can see which cells rest on an unconfirmed source.
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indicators_lib  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
REGISTER = os.path.join(ROOT, "documentation", "archived", "maturity-assessment-norms.md")
LOOKUP = os.path.join(ROOT, "lookups", "maturity-norms.csv")

COLUMNS = ("indicator_id", "kind", "tier", "instrument", "adopting_body", "adopted", "status",
           "provision", "fixes", "reference", "url", "vintage", "notes")
KIND = {"I": "instrument", "S": "system", "M": "measure"}
TIERS = ("AU", "continental", "REC", "global", "corpus")

# Short name as §3 writes it (matched at the start of the anchor cell) -> the start of the §4
# entry's bold title. Longest match wins, so `Malabo` and `AU Interop. Framework` each need one.
ALIASES = {
    "DTS Digital Industry pillar": "Digital Transformation Strategy for Africa",
    "DTS": "Digital Transformation Strategy for Africa",
    "DPF": "AU Data Policy Framework",
    "Continental AI Strategy": "Continental Artificial Intelligence Strategy",
    "ACHPR Declaration": "ACHPR Declaration of Principles",
    "ACHPR Fair Trial": "ACHPR Principles and Guidelines on the Right to a Fair Trial",
    "Agenda 2063 Goal 20": "Agenda 2063 Second Ten-Year",
    "Agenda 2063 STYIP": "Agenda 2063 Second Ten-Year",
    "AU Interop. Framework": "AU Interoperability Framework for Digital ID",
    "AU Digital Education Strategy": "AU Digital Education Strategy",
    "Smart Africa": "Smart Africa Manifesto and Alliance",
    "Public Service Charter": "African Charter on Values and Principles of Public Service",
    "AU Declaration on Land": "AU Declaration on Land Issues",
    "SHaSA 2": "Strategy for the Harmonization of Statistics",
    "Malabo": "AU Convention on Cyber Security",
    "AfCFTA DTP": "AfCFTA Protocol on Digital Trade",
    "AfCFTA Protocol on Trade in Goods": "AfCFTA Protocol on Trade in Goods",
    "African Charter on Statistics": "African Charter on Statistics",
    "PIDA PAP 2": "PIDA Priority Action Plan 2",
    "PAQI / CAMI-20": "CAMI-20 Declaration",
    "ACDEG": "African Charter on Democracy, Elections and Governance",
    "ATU-R Rec. 005-0": "ATU-R Recommendation 005-0",
    "AfSEM": "AfSEM strategic and action plans",
    "Africa CDC": "Africa CDC Digital Transformation Strategy",
    "Protocol on Social Protection": "Protocol to the ACHPR on the Rights of Citizens to Social",
    "World Bank Global Findex": "World Bank Global Findex",
    "UPU": "UPU",
    "TADAT": "TADAT Field Guide",
    "Decentralisation Charter": "African Charter on the Values and Principles of Decentralisation",
    "(AFRIPOL Statute": "Statute of the AU Mechanism for Police Cooperation",
    "STISA-2034": "STISA-2034",
    "Maputo Protocol": "Maputo Protocol",
    "AU Disability Protocol": "Protocol to the ACHPR on the Rights of Persons with Disabilities",
    "Kampala Convention": "Kampala Convention",
    "African Space Strategy": "African Space Policy and African Space Strategy",
    "Integrated African Strategy on Meteorology": "Integrated African Strategy on Meteorology",
}

ROW = re.compile(r"^\| ([a-z]+\.[a-z]+--[a-z0-9-]+)[^|]*\|")
NOTE = re.compile(r"^- `([a-z]+\.[a-z]+--[a-z0-9-]+)` — (.+)$")
ENTRY = re.compile(r"^- \*\*(.+?)\*\*\.?\s*(?:—\s*)?(.*)$")   # global entries carry no dash
URL = re.compile(r"https?://\S+")
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
# Not after a hyphen or a letter: `STC-CICT-3 Oct 2019` names the third committee, not the 3rd.
DATE = re.compile(rf"(?<![\w-])(?:\d{{1,2}}(?:–\d{{1,2}})? {MONTH} \d{{4}}|{MONTH} \d{{4}}|"
                  rf"(?:19|20)\d{{2}}\b)")
DECISION = re.compile(r"(?:Executive Council |Assembly )?(?:EX\.CL/Dec|Assembly/AU/Dec)[^,;]*")


def section(text: str, n: int) -> str:
    i = text.index(f"\n## {n}.")
    j = text.find("\n## ", i + 5)
    return text[i: j if j > 0 else len(text)]


def parse(text: str):
    """§3 rows and notes, §4 entries."""
    s3, s4 = section(text, 3), section(text, 4)
    rows, notes = {}, {}
    for line in s3.split("\n"):
        if ROW.match(line):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            iid = c[0].split()[0]
            rows[iid] = dict(zip(("indicator_id", "kind", "tier", "anchor", "provision",
                                  "fixes", "reference"), [iid] + c[1:7]))
        m = NOTE.match(line)
        if m:
            notes[m.group(1)] = m.group(2).strip()
    entries = {}
    for line in s4.split("\n"):
        m = ENTRY.match(line)
        if m and m.group(1) not in TIERS:
            entries[m.group(1)] = m.group(2).strip()
    return rows, notes, entries


def resolve(anchor: str, entries: dict) -> tuple[str, str] | None:
    """The §4 entry the anchor's first instrument names: `(title, body)`."""
    first = anchor.split(";")[0].strip()
    keys = sorted((k for k in ALIASES if first.startswith(k)), key=len, reverse=True)
    if not keys:
        return None
    want = ALIASES[keys[0]]
    hits = [t for t in entries if t.startswith(want)]
    return (hits[0], entries[hits[0]]) if len(hits) == 1 else None


def facts(title: str, body: str) -> dict:
    """Adopting body, date, status, URL and vintage from a §4 entry's prose.

    Status is read from the entry's first two sentences only: later ones describe the
    instrument's content, where *Malabo in force by 2020* is a DTS target, not the DTS's status.
    A decision number in the first clause is the adopting act and wins over a committee named
    before it; a body is the title where the clause names none."""
    prose = URL.sub("", body)
    first = re.split(r"[;.](?:\s|$)", prose, maxsplit=1)[0].strip()
    head = " ".join(re.split(r"(?<=[.])\s", prose)[:2]).lower()
    date = DATE.search(first) or DATE.search(prose) or DATE.search(title)
    adopted = date.group(0) if date else ""
    dec = DECISION.search(first)
    if dec:
        adopting = dec.group(0).strip()
        after = DATE.search(first, dec.end())
        adopted = after.group(0) if after else adopted
    elif date and date.start() > 0 and date.re.pattern and first.find(adopted) > 0:
        adopting = first[: first.find(adopted)].rstrip(" ,(")
    else:
        adopting = ""
    if not adopting or adopting[0].islower():
        adopting = title
    if "not in force" in head or "binding once in force" in head:
        status = "adopted; not in force"
    elif re.search(r"\bin force\b", head):
        status = "in force"
    elif "not adopted by an organ" in head:
        status = "not adopted by an organ"
    elif "non-binding" in head or "soft law" in head:
        status = "adopted; non-binding"
    else:
        status = "adopted"
    url = URL.search(body)
    year = re.search(r"(?:19|20)\d{2}", adopted)
    return {"adopting_body": adopting, "adopted": adopted, "status": status,
            "url": url.group(0).rstrip(".,;)") if url else "",
            "vintage": year.group(0) if year else ""}


def cut() -> list[dict]:
    rows, notes, entries = parse(open(REGISTER, encoding="utf-8").read())
    assessed = [r["indicator_id"] for r in indicators_lib.assessed()]
    missing = [i for i in assessed if i not in rows]
    extra = [i for i in rows if i not in assessed]
    if missing or extra:
        raise SystemExit(f"maturity-norms-cut: register and frame disagree — not in the "
                         f"register {missing}, not an assessed frame row {extra}")
    out, unresolved = [], []
    for iid in assessed:
        r = rows[iid]
        if r["tier"] not in TIERS:
            raise SystemExit(f"maturity-norms-cut: {iid} tier {r['tier']!r}")
        note = notes.get(iid, "")
        if r["tier"] == "corpus":
            got = resolve(r["anchor"].strip("()"), entries) if r["anchor"] else None
            f = facts(*got) if got else dict.fromkeys(("adopting_body", "adopted", "status",
                                                         "url", "vintage"), "")
            f.update(adopting_body="Corpus", status="Corpus-defined")
            body = ""
        else:
            got = resolve(r["anchor"], entries)
            if not got:
                unresolved.append(f"{iid}: {r['anchor']!r}")
                continue
            f, body = facts(*got), got[1]
        if "not verified" in note.lower():
            note = "not verified: " + note
        elif "not verified" in body.lower():
            # The gap is the instrument's, not the row's — say which entry carries it.
            said = re.search(r"\(([^()]*not verified[^()]*)\)", body)
            note = (f"not verified ({got[0]}): {said.group(1) if said else 'see §4'}"
                    + (f". {note}" if note else ""))
        out.append({"indicator_id": iid, "kind": KIND[r["kind"]], "tier": r["tier"],
                    "instrument": r["anchor"], **f, "provision": r["provision"],
                    "fixes": r["fixes"], "reference": r["reference"], "notes": note})
    if unresolved:
        raise SystemExit("maturity-norms-cut: no §4 entry for\n  " + "\n  ".join(unresolved))
    return out


def render(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: r[c] for c in COLUMNS})
    return buf.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cut lookups/maturity-norms.csv from the register.")
    ap.add_argument("--check", action="store_true", help="compare, write nothing")
    a = ap.parse_args(argv)
    text = render(cut())
    if a.check:
        held = open(LOOKUP, encoding="utf-8-sig", newline="").read() if os.path.exists(LOOKUP) else ""
        if held.replace("\r\n", "\n") != text:      # a CRLF checkout is the same cut
            print("maturity-norms-cut: the lookup differs from a fresh cut of the register — "
                  "re-run without --check and commit both")
            return 1
        print("maturity-norms-cut: ok — the lookup is the register's cut")
        return 0
    with open(LOOKUP, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write(text)
    n = text.count("\n") - 1
    print(f"maturity-norms-cut: {n} rows -> {os.path.relpath(LOOKUP, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
