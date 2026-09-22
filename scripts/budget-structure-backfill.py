#!/usr/bin/env python3
r"""budget-structure-backfill.py — give every budget row an admin head and a programme, once.

    python scripts/budget-structure-backfill.py            # report what it would change
    python scripts/budget-structure-backfill.py --write    # rewrite budgets/ in place

*(Bill, 2026-09-22.)* `budget_source.py` now carries `admin_head_basis`, `programme_basis` and
`programme_level`, and a sitting's row must fill all three. This is the one-time pass over the
rows already in the folder, 478 of them migrated from OSINT records that seldom carried either.
It does three things:

1. **Adds the columns** in the schema's order, so every file matches `COLUMNS` again.
2. **Marks what is already there `printed`** — a value the record carried was read off the
   document, and a programme already held is at `programme` grain.
3. **Derives a stand-in where the row itself says what it is**, marked `derived`: a head from a
   spending entity that prints its own head code (`Section 30 — …`, `(organisation 0300)`,
   `(section 322)`); a programme from the grain the locator names (a Botswana project, an
   Ivorian activité, a Burkinabè chapitre) with the line's own name; a whole-vote or
   whole-body line as `vote` or `body`. **A code is only ever copied from text the row already
   holds as printed**, never inferred — codes are the cross-year join key.

What no rule reaches is left empty and counted in `budgets/structure-gaps.csv`, the ceiling
`budget_source.py` holds each country to: those rows need their document re-read. **Nothing is
guessed from outside knowledge** — Kenya's vote 1024 or South Africa's vote 5 have well-known
names, but a name the row does not hold is a reading job, not a rule.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import budget_source as bs                                               # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HEADED = re.compile(r"^(?:Section|Head|Vote|Code)\s+(\w+)\s*[—–-]\s*(.+)$")
PAREN = re.compile(r"\s*\((?:organisation|section|sect\.?|institution|MDA code|"
                   r"Unidade Orçamental)\s*(\w*)\)?\s*$", re.I)
TAIL = re.compile(r"\s+[—–-]\s+(?:Headquarters|compte d.affectation.*)\s*$")
# A spending entity that is an annotation rather than a name — "implied by …", "announced
# via …" — names nothing a head or a programme can be copied from.
NOTE = re.compile(r"implied|not named|announced|inferred", re.I)
MINISTRY = re.compile(r"^(?:Minist|Wizara|Federal Ministry|Présidence|Presidency|Primature)", re.I)
FINER = re.compile(r"programme|project|imputation|activit|action|chapitre|row `|ligne|LITERA|"
                   r"NOMENCLATURE|PRG", re.I)


def entity(se: str) -> tuple[str, str]:
    """A spending entity's name and the head code it prints, if it prints one."""
    se = se.strip()
    m = HEADED.match(se)
    if m:
        return m.group(2).strip(), m.group(1)
    m = PAREN.search(se)
    if m:
        return TAIL.sub("", se[:m.start()].strip()), m.group(1)
    return TAIL.sub("", se), ""


def nga_ministries(rows: list[dict]) -> dict[str, str]:
    """Nigeria's four-digit ministry prefix -> the ministry's name, from its own
    Headquarters line wherever the folder holds one."""
    out = {}
    for r in rows:
        se = r["spending_entity"]
        m = re.search(r"\(MDA code (\d{4})\d+\)", se) or re.search(r"MDA code (\d{4})", r["doc_locator"])
        if m and "— Headquarters" in se:
            out[m.group(1)] = se.split("— Headquarters")[0].strip()
    return out


def derive(r: dict, nga: dict[str, str]) -> dict[str, str]:
    """The changes for one row, as {column: new value}."""
    g = lambda k: (r.get(k) or "").strip()                                  # noqa: E731
    ch: dict[str, str] = {}
    loc, se, ln, c = g("doc_locator"), g("spending_entity"), g("line_name"), g("place")
    if NOTE.search(se):
        se = ""
    name, code = entity(se)

    # ---- the admin head
    # A basis already written is kept, so a second run changes nothing it made.
    if g("admin_head"):
        ch["admin_head_basis"] = g("admin_head_basis") or "printed"
    else:
        head, hcode = "", ""
        if c == "NGA":
            m = re.search(r"(\d{4})\d{6}", se + " " + loc)
            if m and m.group(1) in nga:
                head, hcode = nga[m.group(1)], m.group(1)
        elif c == "ETH" and se:
            m = re.search(r"public body (?:code )?`(\d+)`", loc)
            head, hcode = se, (m.group(1) if m else "")
        elif c == "BFA":
            m = re.search(r"section (\d+) (Primature)", loc)
            if m:
                head, hcode = m.group(2), m.group(1)
            elif MINISTRY.match(se):
                m = re.search(r"section (\d+)", loc)
                head, hcode = name, (m.group(1) if m else "")
        elif HEADED.match(se) or (PAREN.search(se) and code):
            head, hcode = name, code
        elif MINISTRY.match(se) and " / " not in se:
            head = re.sub(r"\s*\(self\b.*\)$", "", name)
        if head:
            ch["admin_head"], ch["admin_head_basis"] = head, "derived"
            if hcode and not g("admin_head_code"):
                ch["admin_head_code"] = hcode
    head = ch.get("admin_head") or g("admin_head")

    # ---- the programme
    if g("programme"):
        ch["programme_basis"] = g("programme_basis") or "printed"
        ch["programme_level"] = g("programme_level") or "programme"
        return ch
    prog, pcode, level = "", "", ""
    if se.startswith("Compte spécial") or g("admin_head").startswith("Comptes spéciaux"):
        prog = re.sub(r"^Compte spécial \w+\s*[—–-]\s*", "", se)
        pcode, level = g("spending_entity_code"), "account"
    elif g("programme_code") and g("programme_code") == g("spending_entity_code") and se:
        prog, level = se, "body"
    elif c == "BWA" and (m := re.search(r"project (\d+)", loc)):
        prog, pcode, level = ln, m.group(1), "project"
    elif c == "CIV" and (m := re.search(r"activité (\d+)", loc)):
        prog, pcode, level = ln, m.group(1), "activity"
    elif c == "BEN" and (m := re.search(r"Classif Prog-Admin-Eco`, row `(\d+)`", loc)):
        if ln.startswith("Dotation"):
            prog, level = se, "body"
        else:
            prog, pcode, level = ln, m.group(1), "programme"
    elif c == "BFA" and (m := re.search(r"chapitre (\d+)", loc)):
        prog, pcode, level = ln, m.group(1), "chapter"
    elif c == "BFA" and (m := re.search(r"action (\d+)", loc)):
        prog, pcode, level = ln, m.group(1), "action"
    elif c == "BFA" and "par programme" in loc:
        prog, level = ln, "programme"
    elif not FINER.search(loc) and ln and (
            ln in (se, name, head, re.sub(r"\s*\([^)]*\)$", "", se)) or HEADED.match(ln)):
        # A whole appropriation held as one line: the head's own vote, or a body's under it.
        if head and (ln == head or HEADED.match(ln) or name in (head, entity(head)[0])
                     or ln == entity(head)[0]):
            prog, level = head, "vote"
        elif se:
            prog, level = name, "body"
    if prog:
        ch["programme"], ch["programme_basis"], ch["programme_level"] = prog, "derived", level
        if pcode and not g("programme_code"):
            ch["programme_code"] = pcode
    return ch


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    every = [(c, fy, p, bs.read(p)[1]) for c, fy, p in bs.files()]
    nga = nga_ministries([r for c, _, _, rows in every if c == "NGA" for r in rows])
    tally = Counter()
    for country, fy, path, rows in every:
        out = []
        for r in rows:
            ch = derive(r, nga)
            for k in ("admin_head", "programme"):
                if k in ch and ch.get(f"{k}_basis") == "derived":
                    tally[f"{k} derived"] += 1
                    if not a.write:
                        extra = f" [{ch['programme_level']}]" if k == "programme" else ""
                        print(f"{r['deal_id']}: {k} = {ch[k][:70]!r}{extra}")
            new = {col: (r.get(col) or "") for col in bs.COLUMNS}
            new.update(ch)
            if not (new["admin_head"].strip() and new["programme"].strip()):
                tally["still short"] += 1
            out.append(new)
        if a.write:
            with open(path, "w", encoding="utf-8-sig", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(bs.COLUMNS), lineterminator="\n")
                w.writeheader()
                w.writerows(out)
    print(dict(tally))
    return 0


if __name__ == "__main__":
    sys.exit(main())
