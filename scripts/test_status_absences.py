#!/usr/bin/env python3
"""test_status_absences.py — the closing absence line of R150 and R151, both directions.

The line is emitted from the maturity assessment and never written by hand, so the tests are of
what is emitted (no evidence only, in indicator order, an unstudied indicator left out), where it
goes (only where the markers are, or are asked for), and what check A refuses.

    python scripts/test_status_absences.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import status_lib as s  # noqa: E402

failures: list[str] = []


def check(name, got, want):
    if got != want:
        failures.append(f"{name}: got {got!r}, want {want!r}")


s._cache["indicators"] = {
    "gov.policy": [("gov.policy--dts", "Digital transformation strategy"),
                   ("gov.policy--ict", "ICT strategy"), ("gov.policy--bb", "Broadband strategy"),
                   ("gov.policy--new", "Unstudied strategy")],
    "dpi.id": [("dpi.id--auth", "Authentication")],
}
s._cache["stages"] = {
    "gov.policy--dts": {"KEN": "no evidence"},
    "gov.policy--ict": {"KEN": "unplaced"},
    "gov.policy--bb": {"KEN": "3"},
    "dpi.id--auth": {},
}

check("no evidence is named; unplaced, staged and unstudied are not",
      s.absence_line("KEN", "gov.policy"), "Nothing has been found on digital transformation strategy.")
check("a country with no row reads as no evidence",
      s.absence_line("KEN", "dpi.id"), "Nothing has been found on authentication.")
check("a sub-section with nothing absent emits nothing",
      s.absence_line("KEN", "geopol.usa"), "")
s._cache["stages"]["gov.policy--bb"]["KEN"] = "no evidence"
check("several are listed in indicator order",
      s.absence_line("KEN", "gov.policy"),
      "Nothing has been found on digital transformation strategy or broadband strategy.")
check("an acronym keeps its capitals", s.reader_name("ICT strategy"), "ICT strategy")

doc = ("## Governance\n\n### Strategies\n<!-- gov.policy -->\n\nA paragraph.\n\n"
       "### Identity\n<!-- dpi.id -->\n\nAnother.\n")
check("nothing is added unasked", s.refresh_absences(doc, "KEN"), doc)
added = s.refresh_absences(doc, "KEN", add=("gov.policy",))
check("a block is added where asked",
      added.count(s.ABSENCE_OPEN), 1)
check("it closes the sub-section", added.index(s.ABSENCE_OPEN) < added.index("### Identity"), True)
check("a second run changes nothing", s.refresh_absences(added, "KEN"), added)
check("a sub-section without indicators takes no block",
      s.refresh_absences("### US\n<!-- geopol.usa -->\n\nText.\n", "KEN", add=("all",)).count(
          s.ABSENCE_OPEN), 0)

check("an emitted block passes check A", s.absence_faults(added, "KEN"), [])
edited = added.replace("broadband strategy.", "broadband plan.")
check("an edited block fails check A", [f[0] for f in s.absence_faults(edited, "KEN")], ["gov.policy"])
by_hand = added.replace("A paragraph.", "A paragraph.\n\nNo ICT strategy has been found.")
check("a hand-written absence paragraph fails check A",
      [f[0] for f in s.absence_faults(by_hand, "KEN")], ["gov.policy"])
closing = added.replace("A paragraph.", "The 2016 paper still applies. No replacement has been found.")
check("an absence closing a paragraph of facts stands", s.absence_faults(closing, "KEN"), [])
check("unmarked sections are not read",
      s.absence_faults(doc.replace("A paragraph.", "No ICT strategy has been found."), "KEN"), [])

if failures:
    print("\n".join(failures))
    print(f"test_status_absences: FAIL - {len(failures)}")
    sys.exit(1)
print("test_status_absences: ok")
