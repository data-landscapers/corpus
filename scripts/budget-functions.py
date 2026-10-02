#!/usr/bin/env python3
r"""budget-functions.py — checks B and C of the budget data review.

    python scripts/budget-functions.py          # write both logs and print the tally
    python scripts/budget-functions.py GHA      # one country, printed and not written
    python scripts/budget-functions.py --absent GHA procurement "FY2026: ... PBB 2026 MoF, table 1.6"

The plan is the share's `documentation/budget-data-review.md`. Check A counts rows, and a
count cannot find a line passed over inside a document that was read: Ghana's statistics
office was a cost centre of the finance ministry's vote and the file looked complete without
it. These two checks ask a different question — **what should be there** — from two lists
Corpus already holds.

**B. Functions → `logs/budget-functions.csv`.** Fourteen functions every state has, by
country. A cell is `found` (a row is held), `absent` (the document was read for it and it
is not there, dated, with the document and page) or `not looked`. `found` is derived here,
from the rows; **`absent` is a reading and is only ever entered by hand**, with
`basis: hand`, and this script keeps a hand row until the rows themselves find the function.
`--absent` enters one: the country, the function, and the evidence — the fiscal year, what
was read and where — dated today.
A function is found by its topic where the taxonomy has one for it, and by the body's or
the system's name where it does not. `scope` says how well: `whole` is the plan's test, and
a function held only at `partial` or `unclear` is `found` with that scope and still worth a
look — a statistics unit inside a ministry's administration line is not the statistics office.

**C. Names → `logs/budget-names.csv`.** Two lists of bodies, in the country's own language:
the institution hosting dataset's state institutions, and the `recipient_organisation` of
non-state deals from 2024. Each is `line` where a budget row carries its name, its acronym
or its domain label, and `no line` where none does. Banks, exchanges and payment switches
are not asked for: they are not in the state budget.

**Both are candidates, not findings.** A `no line` body may be funded inside another vote,
by a levy outside the vote, or under a name the match does not reach. The reading is a
BUDGET-EXTRACT sitting.

Neither file carries a date the script writes, so a run that finds nothing new moves no byte.

Exit: 0 written, 2 there is no `budgets/` folder.
"""
from __future__ import annotations

import collections
import csv
import datetime
import glob
import importlib.util
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget_source  # noqa: E402

ROOT = budget_source.ROOT
FUNCTIONS_OUT = os.path.join(ROOT, "logs", "budget-functions.csv")
NAMES_OUT = os.path.join(ROOT, "logs", "budget-names.csv")
HOSTING = os.path.join(ROOT, "R&D", "Hyperscaler-dependence", "institution-hosting.csv")
DEALS = os.path.join(ROOT, "outputs", "non-state-finance", "*-nonstate.csv")
DEALS_FROM = 2024
FUNCTION_COLUMNS = ("iso3", "function", "status", "scope", "rows", "deal_id", "named",
                    "basis", "evidence", "looked")
NAME_COLUMNS = ("iso3", "list", "type", "function", "name", "status", "deal_id")
SCOPE_ORDER = ("whole", "partial", "unclear")

# Each function: its key, the hosting dataset's type for it, the topics that find it without
# a name, and the name pattern that finds it under any topic. Patterns are matched on the
# folded text (no accents, lower case) of a row's body, programme and line names.
FUNCTIONS = (
    ("statistics", "Statistics office", ("data.statistics",), r""),
    ("civil-registration-id", "Civil registry / National ID authority", ("dpi.id",), r""),
    ("communications-regulator", "Communications regulator", (),
     r"regulat\w* (authority|agency|commission|board)|autorite de regul|agence de regul|"
     r"regul\w* des (tele|communications|postes)|autoridade reguladora|reguladora das comunic|"
     r"reglementation des telecom|communications? (authority|commission)|"
     r"\b(arcep|artp|arpt|anrt|artci|arptc|arpce|artec|arcom)\b"),
    ("ict-ministry-egov", "E-government agency", (),
     r"\be ?gov|govern\w* electron|administration electron|ministry of (ict|information and comm|"
     r"communications?|digital|technology)|minist\w+ (de l[ae]? ?|du |da |das |dos )?(economie )?"
     r"(numerique|digital|communicat|tecnolog|transition numerique|postes)|information technology "
     r"(agency|authority)|agence (nationale )?(de l informatique|des systemes d information|"
     r"du numerique|de developpement du digital)|digital (transformation|economy)|"
     r"transformation (numerique|digitale)|transformacao digital"),
    ("cybersecurity", "Cybersecurity agency / National CERT", ("infra.cybersec",), r""),
    ("data-protection", "Data protection authority", ("gov.protect",), r""),
    ("revenue-systems", "Revenue Service", (),
     r"revenue (authority|service|administration)|\btax\w*|impots|douan|customs|tribut|"
     r"alfandeg|fiscal\w* (system|information)|aduan"),
    ("treasury-fmis", "Treasury / Finance", (),
     r"ifmis|\bifms\b|sigfip|sigfe|\bsigif|sistafe|siafe|sigof|financial management "
     r"(information )?system|integrated financial|gestion (integree )?des finances|"
     r"systeme d information (budgetaire|financi)|comptab\w+ (publique )?informatis|"
     r"public financ\w+ management|\bpfm\b|\be ?budget|budget\w* (information )?system|"
     r"systeme (integre )?de gestion (budgetaire|des finances)|treasury single account|\btsa\b|"
     r"informatique financiere|informatis\w+ (de la |du )?(dgcpt|tresor|comptabilite)"),
    ("procurement", "Public procurement authority", (),
     r"procure|marches publics|commande publique|contrat\w+ public|aquisic|\be ?gp\b|\barmp\b|\barmds\b"),
    ("electoral-register", "Electoral commission", (),
     r"\belect(ion|or|eur)|eleit|eleic|voter|scrutin|\bceni\b"),
    ("land-registry", "Land registry", (),
     r"\blands?\b|cadast|foncier|fonciere|terras|deeds|domaines\b|conservation fonc"),
    ("social-registry", "Social protection / Social registry", (),
     r"social (registry|register)|registre social|registo social|cadastro social|safety net|"
     r"filets sociaux|protection sociale|social protection|proteccao social|\brsu\b|"
     r"beneficiar|cash transfer|transferts? monetaires?"),
    ("population-register", "", (),
     r"population regist|registre (national )?(de la |des )?(population|personnes)|"
     r"fichier (national )?(de la )?population|registo (nacional )?d[ae] popula|\brnpp\b|\brnp\b"),
    ("data-exchange", "", ("dpi.exchange",), r""),
)
# The hosting dataset's types that are not asked for of a state budget.
NOT_STATE = {"Commercial Banks", "Stock exchange", "National payment switch"}
# Words that carry no identity in a body's name, in the four languages met.
STOP = set("""of the and for de des du la le les l d et da do das dos e a o em para of
    national nationale nacional agence agency authority autorite autoridade ministry ministere
    ministerio office commission comissao service services direction generale general geral
    republic republique republica institut institute instituto bureau department board council
    conseil conselho public publique publica state etat estado government gouvernement governo
    federal centre center centro""".split())
SUFFIXES = {"gov", "gouv", "go", "org", "com", "co", "net", "ac", "edu", "www", "mil", "int", "gob"}


def load(name: str):
    path = os.path.join(ROOT, "scripts", name)
    spec = importlib.util.spec_from_file_location(name.replace("-", "_")[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


holes = load("budget-holes.py")
fold = holes.fold


def row_text(row: dict, purpose: bool = False) -> str:
    cols = ["admin_head", "spending_entity", "programme", "sub_programme", "line_name", "transfer_to"]
    if purpose:
        cols.append("purpose")
    return fold(" | ".join(row.get(c) or "" for c in cols))


def best(rows: list[dict]) -> tuple[str, dict]:
    """The best scope held and the first row holding it."""
    for scope in SCOPE_ORDER:
        for r in rows:
            if r.get("scope_confidence") == scope:
                return scope, r
    return "", rows[0]


def hosting() -> list[dict]:
    with open(HOSTING, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def recipients() -> list[dict]:
    out, seen = [], set()
    for path in sorted(glob.glob(DEALS)):
        iso3 = os.path.basename(path)[:3]
        with open(path, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                name = (r.get("recipient_organisation") or "").strip()
                year = (r.get("start_year") or "")[:4]
                if name and year.isdigit() and int(year) >= DEALS_FROM and (iso3, fold(name)) not in seen:
                    seen.add((iso3, fold(name)))
                    out.append({"iso3": iso3, "type": r.get("beneficiary_type", ""), "institution": name,
                                "domains": ""})
    return out


def name_keys(name: str, domains: str) -> tuple[list[str], list[str]]:
    """The identifying words of a body's name, and the short handles it also goes by: an
    acronym in brackets or standing alone, and the label of its domain."""
    handles = [fold(a) for a in re.findall(r"\(([A-Za-z][A-Za-z&-]{1,11})\)", name)]
    handles += [fold(w) for w in re.findall(r"\b[A-Z]{3,10}\b", name)]
    for dom in re.split(r"[;, ]+", domains or ""):
        labels = [p for p in dom.lower().split(".")[:-1] if p not in SUFFIXES]
        handles += [p for p in labels if len(p) >= 3]
    words = [w for w in fold(re.sub(r"\([^)]*\)", " ", name)).split() if w not in STOP and len(w) > 2]
    return words, sorted({h for h in handles if h and h not in STOP})


def name_match(words: list[str], handles: list[str], texts: list[tuple[str, dict]]) -> dict | None:
    for text, row in texts:
        tokens = set(text.split())
        if words and all(w in tokens for w in words):
            return row
        if any(h in tokens for h in handles):
            return row
    return None


def existing() -> dict[tuple[str, str], dict]:
    if not os.path.exists(FUNCTIONS_OUT):
        return {}
    with open(FUNCTIONS_OUT, encoding="utf-8-sig", newline="") as fh:
        return {(r["iso3"], r["function"]): r for r in csv.DictReader(fh)}


def build(only: str = "") -> tuple[list[dict], list[dict]]:
    by_country: dict[str, list[dict]] = collections.defaultdict(list)
    for iso3, _, row in budget_source.rows():
        by_country[iso3].append(row)
    host = hosting()
    kept = existing()
    type_function = {t: key for key, t, _, _ in FUNCTIONS if t}
    functions, names = [], []
    for iso3 in holes.countries():
        if only and iso3 != only:
            continue
        rows = by_country.get(iso3, [])
        texts = [(row_text(r), r) for r in rows]
        full = [(row_text(r, purpose=True), r) for r in rows]
        for key, htype, topics, pattern in FUNCTIONS:
            rx = re.compile(pattern) if pattern else None
            hits = [r for text, r in texts
                    if r.get("primary_topic_id") in topics or (rx and rx.search(text))]
            named = "; ".join(h["institution"] for h in host if h["iso3"] == iso3 and h["type"] == htype)
            old = kept.get((iso3, key), {})
            cell = dict.fromkeys(FUNCTION_COLUMNS, "")
            cell.update(iso3=iso3, function=key, named=named)
            if hits:
                scope, row = best(hits)
                cell.update(status="found", scope=scope, rows=str(len(hits)),
                            deal_id=row.get("deal_id", ""), basis="rows")
            elif old.get("basis") == "hand":
                cell.update({c: old.get(c, "") for c in ("status", "scope", "rows", "deal_id",
                                                         "basis", "evidence", "looked")})
            else:
                cell.update(status="not looked")
            if hits and old.get("basis") == "hand" and old.get("status") == "found":
                cell.update(evidence=old.get("evidence", ""), looked=old.get("looked", ""))
            functions.append(cell)
        for source, bodies in (("hosting", [h for h in host if h["iso3"] == iso3 and h["type"] not in NOT_STATE]),
                               ("deal-recipient", [d for d in recipients_cache() if d["iso3"] == iso3])):
            for b in bodies:
                words, handles = name_keys(b["institution"], b.get("domains", ""))
                words = [w for w in words if w not in country_words(iso3)]
                row = name_match(words, handles, full) if rows else None
                names.append(dict(zip(NAME_COLUMNS, (
                    iso3, source, b["type"], type_function.get(b["type"], ""), b["institution"],
                    "line" if row else "no line", row.get("deal_id", "") if row else ""))))
    return functions, names


def country_words(iso3: str) -> set[str]:
    """The country's own name, which a budget's bodies drop and a foreign list adds."""
    global _COUNTRY
    if _COUNTRY is None:
        with open(holes.COUNTRIES, encoding="utf-8-sig", newline="") as fh:
            _COUNTRY = {r["iso-3"]: set(fold(r["country-name"]).split()) for r in csv.DictReader(fh)}
    return _COUNTRY.get(iso3, set())


_COUNTRY: dict[str, set[str]] | None = None
_RECIPIENTS: list[dict] | None = None


def recipients_cache() -> list[dict]:
    global _RECIPIENTS
    if _RECIPIENTS is None:
        _RECIPIENTS = recipients()
    return _RECIPIENTS


def write(path: str, columns: tuple, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def mark_absent(iso3: str, function: str, evidence: str) -> int:
    """Enter one hand reading: the function was looked for in the document and is not there."""
    cells = existing()
    if (iso3, function) not in cells:
        print(f"budget-functions: no cell {iso3} {function}; run the script once first", file=sys.stderr)
        return 1
    if cells[(iso3, function)]["status"] == "found":
        print(f"budget-functions: {iso3} {function} is found in the rows; not marked", file=sys.stderr)
        return 1
    cells[(iso3, function)].update(status="absent", scope="", rows="", deal_id="", basis="hand",
                                   evidence=evidence, looked=datetime.date.today().isoformat())
    write(FUNCTIONS_OUT, FUNCTION_COLUMNS, list(cells.values()))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args[:1] == ["--absent"]:
        if len(args) != 4:
            print("usage: budget-functions.py --absent ISO3 function \"evidence\"", file=sys.stderr)
            return 1
        return mark_absent(args[1].upper(), args[2], args[3])
    if not os.path.isdir(budget_source.BUDGETS):
        print("budget-functions: no budgets/ folder", file=sys.stderr)
        return 2
    only = args[0].upper() if args else ""
    functions, names = build(only)
    if only:
        for r in functions:
            print(" | ".join(r[c] for c in ("function", "status", "scope", "rows", "deal_id", "named")))
        for r in names:
            if r["status"] == "no line":
                print(" | ".join(r[c] for c in NAME_COLUMNS))
    else:
        write(FUNCTIONS_OUT, FUNCTION_COLUMNS, functions)
        write(NAMES_OUT, NAME_COLUMNS, names)
    cells = collections.Counter((r["status"], r["scope"]) for r in functions)
    whole = cells[("found", "whole")]
    part = sum(n for (s, sc), n in cells.items() if s == "found" and sc != "whole")
    absent = sum(n for (s, _), n in cells.items() if s == "absent")
    print(f"budget-functions: {len(functions)} cells, found whole {whole}, found partial or unclear "
          f"{part}, absent {absent}, not looked {cells[('not looked', '')]}; "
          f"{sum(r['status'] == 'no line' for r in names)} of {len(names)} named bodies with no line"
          + ("" if only else f" -> {os.path.relpath(FUNCTIONS_OUT, ROOT)}, {os.path.relpath(NAMES_OUT, ROOT)}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
