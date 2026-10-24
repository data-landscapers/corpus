#!/usr/bin/env python3
"""test_status_check_totals.py — status-check K: derived non-state totals against the table.

    python scripts/test_status_check_totals.py

Runs on strings and a temporary CSV; touches nothing real.
"""
from __future__ import annotations
import importlib.util, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("status_check", os.path.join(HERE, "status-check.py"))
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)
failed = 0


def case(name, ok):
    global failed
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    failed += not ok


def parse(s, prev=False):
    count, hedged, amount, _ = sc.stated_totals(s, prev)
    return count, hedged, None if amount is None else round(amount, 1)


print("parser")
case("count and amount on record",
     parse("Fourteen digital-sector financing commitments to Benin are on record, spanning 2015 "
           "to 2031 and worth around USD 560 million (October 2026).") == (14, False, 560.0))
case("billions, hyphenated number word",
     parse("Seventy-three external commitments to Kenya's digital estate are on record, worth "
           "about US$4.4 billion on windows running from 2015 to 2033.") == (73, False, 4400.0))
case("hedged count",
     parse("Around twenty external financing commitments to Ghana's digital sector are on the "
           "record, together worth roughly US$2.7 billion.") == (20, True, 2700.0))
case("recorded total across N commitments",
     parse("Chinese policy banks lead: four commitments from China Eximbank worth about US$878 "
           "million, three-quarters of a recorded total of about US$1.17 billion across twenty "
           "commitments with a stated amount.") == (20, False, 1170.0))
case("amount of commitment across N deals",
     parse("Behind that sits about US$4.3 billion of external and private commitment to Nigeria "
           "across 82 recorded deals between 2015 and 2026.") == (82, False, 4300.0))
case("N of the M: M is the record, no amount taken",
     parse("Six of the eleven digital commitments on Djibouti's record were active, worth about "
           "US$64 million.") == (11, False, None))
case("of the AMT on record, no count",
     parse("The Eximbank loan is about a twentieth of the roughly US$1.05 billion on record.")
     == (None, False, 1050.0))
case("pronoun total only after a count",
     parse("They come to about US$560 million (2015-2026).", prev=True) == (None, False, 560.0)
     and parse("They come to about US$560 million (2015-2026).") == (None, False, None))
case("link text kept, target dropped",
     parse("[Nine commitments are on record](https://example.org/2019/9), worth US$545 million.")
     == (9, False, 545.0))

print("subsets are not parsed")
case("narrowing adjective",
     parse("Five Chinese-financed commitments to Cabo Verde are on the record, worth about USD 48 "
           "million.") == (None, False, None))
case("from a named financier",
     parse("Two commitments from the European Union are on record, worth US$9 million.")
     == (None, False, None))
case("qualifier after the noun",
     parse("Nine of the 17 commitments beginning in 2025 or 2026 are commercial capital.")
     == (None, False, None))
case("regional operations counted in",
     parse("Eleven digital-sector commitments touching Guinea are on record, seven to the country "
           "and four regional operations naming it.") == (None, False, None))
case("regional operations set aside still parsed",
     parse("Ten commitments to Mauritania are on record; regional operations naming it sit "
           "outside that count.") == (10, False, None))
case("another currency",
     parse("Eight commitments are on record, worth EUR 400 million.") == (8, False, None))

print("tolerance")
case("half the last place", sc.usd_m("1.17", "billion") == (1170.0, 5.0)
     and sc.usd_m("440", "million") == (440.0, 5.0) and sc.usd_m("149", "million") == (149.0, 0.5))

print("comparison")
TEXT = """### New investments
<!-- finance.new -->

<!-- derived -->
Twenty commitments are on record, worth about US$1.17 billion. They are mostly debt.

<!-- derived -->
Ten commitments to Utopia are on record, worth about US$500 million.

Twenty commitments are on record, worth US$9 billion, says [a linked source](https://x.org).
"""
table = (21, 20, 1165.0)
drift = sc.totals_drift(TEXT, table)
case("a count matching rows-with-amount and an amount within rounding pass",
     not any("Twenty" in d for d in drift))
case("a stale count and total are both reported, with both figures",
     len(drift) == 1 and "states 10 deals, table 21 (20 with an amount)" in drift[0]
     and "US$500m, table US$1,165.0m" in drift[0])
case("a linked (non-derived) paragraph is not read", "9 billion" not in " ".join(drift))
case("hedged count within 15 per cent passes",
     sc.totals_drift("### X\n<!-- finance.new -->\n\n<!-- derived -->\nAround twenty commitments "
                     "are on record.\n", (23, 22, 10.0)) == [])

with tempfile.TemporaryDirectory() as tmp:
    sc.NONSTATE = tmp
    with open(os.path.join(tmp, "AAA-nonstate.csv"), "w", encoding="utf-8-sig", newline="") as f:
        f.write('recipient,commitment_usd_m,title\nAAA,10,"a, b"\nAAA,22.5,c\nAAA,,d\n')
    case("table: rows, rows with an amount, total", sc.nonstate_table("AAA") == (3, 2, 32.5))
    case("no table is None", sc.nonstate_table("BBB") is None)

print(f"\n{'all passed' if not failed else f'{failed} FAILED'}")
sys.exit(1 if failed else 0)
