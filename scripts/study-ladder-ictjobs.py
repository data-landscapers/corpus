#!/usr/bin/env python3
r"""study-ladder-ictjobs.py — the ictjobs study's four questions, counted.

    python scripts/study-ladder-ictjobs.py --as-at 2026-09-30
    python scripts/study-ladder-ictjobs.py --as-at 2026-09-30 --dry

`maturity/ictjobs/maturity-study-ictjobs.md` §2 and §3, counted by `study_figure.py`.

Exit: 0 written, 2 the study cannot be read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_figure  # noqa: E402

if __name__ == "__main__":
    sys.exit(study_figure.main(["ictjobs", "ladder", *sys.argv[1:]]))
