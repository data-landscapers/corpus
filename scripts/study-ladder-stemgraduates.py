#!/usr/bin/env python3
r"""study-ladder-stemgraduates.py — the stemgraduates study's four questions, counted.

    python scripts/study-ladder-stemgraduates.py --as-at 2026-09-30
    python scripts/study-ladder-stemgraduates.py --as-at 2026-09-30 --dry

`maturity/stemgraduates/maturity-study-stemgraduates.md` §2 and §3, counted by `study_figure.py`.

Exit: 0 written, 2 the study cannot be read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_figure  # noqa: E402

if __name__ == "__main__":
    sys.exit(study_figure.main(["stemgraduates", "ladder", *sys.argv[1:]]))
