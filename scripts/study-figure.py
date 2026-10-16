#!/usr/bin/env python3
r"""study-figure.py — carry, stage or write a first-pass study of a held measure.

    python scripts/study-figure.py {study} carry|ladder|write|cleared [--as-at YYYY-MM-DD] [--dry]

`study_figure.py` is the whole of it.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_figure  # noqa: E402

if __name__ == "__main__":
    sys.exit(study_figure.main())
