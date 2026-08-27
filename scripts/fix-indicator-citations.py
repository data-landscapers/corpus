# -*- coding: utf-8 -*-
"""fix-indicator-citations.py - move a paragraph's citation onto the clause that carries its figures.

`from fix_indicator_citations import fix` is not the usage: the file is imported by path from a
drafting script, or its `fix()` is applied to each `developments` cell before the draft CSV is
written. Written during the GHA mapping (2026-08-27), where the defect it repairs fired 29 times in
one pre-lint run.

The two indicator checks split sentences on `.` and `;`, so a development written as
"<clause with figures>; <clause> ([label](slug))." leaves the figures uncited. This walks each
development paragraph and, where a fragment carries a figure and no citation while a later
fragment in the same paragraph does, repeats that paragraph's first citation onto the offending
fragment. It never invents a source: the citation it adds is already the paragraph's own.
"""
import re

ANCHOR = re.compile(r"\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\)")
CITED = re.compile(r"\]\([^)]+\)")
FIGURE = re.compile(r"(?:US\$|R|EUR|£|\$)\s?\d[\d,.]*\s?(?:m|bn|billion|million)?"
                    r"|\b\d+(?:\.\d+)?\s?(?:%|per cent)"
                    r"|\b\d{1,3}(?:,\d{3})+\b"
                    r"|\b\d{4,}\b")
YEAR = re.compile(r"^(?:19|20)\d\d$")


def _needs(frag):
    if CITED.search(frag):
        return False
    return any(not YEAR.match(f.strip()) for f in dict.fromkeys(FIGURE.findall(frag)))


def fix(text):
    out_paras = []
    for para in text.split("\n\n"):
        m = ANCHOR.search(para)
        if not m:
            out_paras.append(para)
            continue
        cite = "(" + m.group(0) + ")"
        frags = re.split(r"((?<=[.;])\s+)", para)
        for i in range(0, len(frags), 2):
            f = frags[i]
            if not _needs(f):
                continue
            body, tail = (f[:-1], f[-1]) if f[-1:] in ".;" else (f, "")
            frags[i] = body.rstrip() + " " + cite + tail
        out_paras.append("".join(frags))
    return "\n\n".join(out_paras)
