# -*- coding: utf-8 -*-
"""cite-reread.py — worksheets for the citation re-read of the authored status baselines.

    python scripts/cite-reread.py worksheet AGO      # -> logs/cite-reread/AGO-worksheet.md
    python scripts/cite-reread.py worksheet all      # every unit still owed in the progress file
    python scripts/cite-reread.py status             # what the progress file says is left
    python scripts/cite-reread.py apply AGO          # patch, gate, render, record, commit one unit

`CITE-REREAD.md` is the procedure. This script does the mechanical half: for every inline link in a
`built_by: STATUS-INIT` baseline it writes the claim the link sits on, what the link resolves to, and
the passages of the held evidence most likely to settle it, so the reader judges a claim from a page
of text instead of opening a hundred source bodies whole.

**The passages are a retrieval, not a verdict.** They are scored on the claim's figures, names and
long words; a claim whose passages do not settle it is read against the body, whose path is printed.
A figure found nowhere in its passages is the commonest sign of a claim the source does not make —
and the commonest false alarm is a figure the source writes another way (`1.35 GW` for `1,350 MW`).

Resolution, in the order `status_lib.held_urls()` accepts a link: the catalogue (a body in `raw/`),
the finance table (its row), the AfDB dataset (the rows citing the URL, with their comments), the
Ibrahim Index profiles. Anything else is *not held*: counted, never judged, because there is nothing
on this machine to judge it against."""
import csv, glob, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import status_lib  # noqa: E402

RAW = os.path.join(HERE, ".workroot", "raw")
OUT = os.path.join(REPO, "logs", "cite-reread")
PROGRESS = os.path.join(REPO, "logs", "cite-reread-progress.csv")
LINK = re.compile(r"\[((?:[^\[\]]|\[[^\]]*\])*)\]\((?:<(https?://[^>]+)>|(https?://[^)\s]+))\)")
STOP = set("The This That These Those There Their They With From Under Over Into Onto Which While Where When What Since After Before About Against Between Through During Without Within Among Also Only Most More Some Such Both Each Other Than Then Its And But For Not Nor Yet".split())


def flat(s):
    """Markdown links reduced to their text, so a claim reads as a sentence."""
    return LINK.sub(lambda m: m.group(1), s)


def terms(claim):
    nums = {n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", claim) if len(n.replace(",", "")) >= 2}
    names = {w for w in re.findall(r"\b[A-Z][A-Za-zÀ-ɏ'-]{2,}", claim) if w not in STOP}
    longs = {w.lower() for w in re.findall(r"[A-Za-zÀ-ɏ]{8,}", claim)}
    return nums, names, longs


def passages(body, claim, k=2, width=420):
    nums, names, longs = terms(claim)
    # OSINT's sweep annotations sit inside some bodies and are not the source speaking: a claim
    # that only a sweep note supports is a claim the source does not make, so they never match.
    body = re.split(r"^\*\*Sweep note", body, maxsplit=1, flags=re.M)[0]
    lines = [ln.strip() for ln in body.splitlines() if len(ln.strip()) > 30]
    scored = []
    for i, ln in enumerate(lines):
        flatln = ln.replace(",", "")
        s = 3 * sum(1 for n in nums if n in flatln) + 2 * sum(1 for n in names if n in ln) \
            + sum(1 for w in longs if w in ln.lower())
        if s:
            scored.append((s, i))
    out, used = [], set()
    for s, i in sorted(scored, reverse=True):
        if i in used:
            continue
        used.update({i - 1, i, i + 1})
        txt = lines[i]
        if len(txt) > width:
            # centre the window on the first figure or name the claim carries
            hit = next((txt.replace(",", "").find(n) for n in list(nums) + list(names) if n in txt.replace(",", "")), 0)
            start = max(0, hit - width // 3)
            txt = ("…" if start else "") + txt[start:start + width] + "…"
        out.append(f"[{s}] {txt}")
        if len(out) >= k:
            break
    missing = sorted(n for n in nums if n not in body.replace(",", ""))
    return out, missing


def load_catalogue():
    cat = {}
    with open(os.path.join(REPO, "outputs", "catalogue", "catalogue-internal.csv"), encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            for v in status_lib._variants(r["url"].strip()):
                cat.setdefault(v, []).append(r["slug"])   # a URL can carry two held records
    return cat


def load_raw_paths():
    out = {}
    for p in glob.glob(os.path.join(RAW, "*", "*.md")):
        out[os.path.basename(p)[:-3]] = p
    return out


def load_rows(path, urlcol):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            for u in status_lib._URL_SEP.split(r.get(urlcol) or ""):
                u = u.strip().strip(".,;")
                if u.startswith("http"):
                    for v in status_lib._variants(u):
                        out.setdefault(v, []).append(r)
    return out


def worksheet(unit, ctx):
    path = os.path.join(REPO, "outputs", "reports", unit, f"{unit}-status.md")
    text = io.open(path, encoding="utf-8").read()
    if status_lib.frontmatter(text).get("built_by") != "STATUS-INIT":
        raise SystemExit(f"{unit}: not an authored baseline")
    cat, raw, fin, dpi, iiag = ctx
    bodies = {}
    w = [f"# {unit} citation worksheet", "",
         f"Source file: `outputs/reports/{unit}/{unit}-status.md`. One entry per link: the claim, what the link resolves to, and the best-matching passages of the held evidence with their match score. `figures not in source` lists numbers in the claim that appear nowhere in the held body — check each (a source may write the figure another way).", ""]
    counts = {"links": 0, "held": 0, "finance": 0, "dpi": 0, "iiag": 0, "not held": 0, "derived": 0}
    for slug, label, prose in status_lib.sections(text):
        w += [f"## {label} ({slug})", ""]
        for pi, para in enumerate(status_lib.paragraphs(prose), 1):
            if para.startswith(status_lib.DERIVED if hasattr(status_lib, "DERIVED") else "<!-- derived -->"):
                counts["derived"] += 1
                w += [f"### ¶{pi} — derived paragraph, not checked", ""]
                continue
            for si, sent in enumerate(status_lib.sentences(para), 1):
                for m in LINK.finditer(sent):
                    url = m.group(2) or m.group(3)
                    counts["links"] += 1
                    claim = flat(sent)
                    w.append(f"### ¶{pi}.{si} — {url}")
                    w.append(f"**Link text:** {m.group(1)}")
                    w.append(f"**Sentence:** {claim}")
                    for s in cat.get(url, []):
                        rp = raw.get(s)
                        if not rp:
                            w.append(f"**Held:** `{s}` — body file not found under raw/")
                        else:
                            if rp not in bodies:
                                t = io.open(rp, encoding="utf-8", errors="replace").read()
                                parts = t.split("---", 2)
                                bodies[rp] = parts[2] if t.startswith("---") and len(parts) == 3 else t
                            b = re.split(r"^\*\*Sweep note", bodies[rp], maxsplit=1, flags=re.M)[0]
                            ps, missing = passages(b, claim)
                            w.append(f"**Held:** `{s}` · body {len(b.split())} words · `{os.path.relpath(rp, REPO)}`")
                            if missing:
                                w.append(f"**Figures not in source:** {', '.join(missing)}")
                            for p in ps or ["(no passage matched the claim's figures or names)"]:
                                w.append(f"> {p}")
                    if url in cat:
                        counts["held"] += 1
                    elif url in fin:
                        counts["finance"] += 1
                        for r in fin[url][:3]:
                            w.append(f"**Finance row:** {r.get('recipient_country')} · {r.get('financier')} · {r.get('instrument')} · {r.get('original_amount')} · US${r.get('commitment_usd_m')}m · {r.get('start_year')}-{r.get('end_year')} · {r.get('status')} · {r.get('title')}")
                    elif url in dpi:
                        counts["dpi"] += 1
                        for r in dpi[url][:3]:
                            w.append(f"**AfDB dataset:** {r.get('Country')} · {r.get('Variable Name')} · {r.get('Value Name')} ({r.get('Year')}) — {(r.get('Comments') or '')[:400]}")
                    elif url in iiag:
                        counts["iiag"] += 1
                        w.append("**Ibrahim Index profile** — check against the held IIAG profile record for this country if the catalogue carries one")
                    else:
                        counts["not held"] += 1
                        w.append("**Not held** — nothing on this machine to check against; leave as written")
                    w.append("")
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"{unit}-worksheet.md")
    head = f"**Counts:** {counts['links']} links · {counts['held']} held bodies · {counts['finance']} finance rows · {counts['dpi']} AfDB dataset · {counts['iiag']} IIAG · {counts['not held']} not held · {counts['derived']} derived paragraphs"
    w.insert(3, head)
    io.open(out, "w", encoding="utf-8", newline="\n").write("\n".join(w) + "\n")
    print(f"{unit}: {out} — {head[11:]}")
    return counts


def progress():
    with open(PROGRESS, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def run(cmd, cwd=REPO):
    import subprocess
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def apply(unit):
    """Apply one unit's patch, gate it, render it, record it, commit it. `CITE-REREAD.md` → *The loop*, 3-4.

    A patch that fails A, B, E, G or FM is reverted and the unit stays `owed` with the reason — the
    last good baseline is at HEAD because every earlier unit was committed alone."""
    patch = os.path.join(OUT, f"{unit}-patch.py")
    summ = os.path.join(OUT, f"{unit}-summary.md")
    tot = [ln for ln in io.open(summ, encoding="utf-8").read().splitlines() if ln.startswith("TOTALS:")]
    if not tot:
        raise SystemExit(f"{unit}: summary carries no TOTALS line")
    counts = dict(kv.split("=") for kv in tot[-1][len("TOTALS:"):].split())
    code, out = run([sys.executable, patch])
    print(out.strip()[-1500:])
    if code:
        raise SystemExit(f"{unit}: patch failed (exit {code}); nothing committed")
    code, out = run([sys.executable, os.path.join(HERE, "status-check.py"), "--unit", unit])
    bad = [ln.strip() for ln in out.splitlines() if re.match(r"\s*check (A|B|E|G|FM) ", ln) and "PASS" not in ln]
    if bad:
        print(out)
        run(["git", "checkout", "--", f"outputs/reports/{unit}"])
        raise SystemExit(f"{unit}: gate failed, reverted: {bad}")
    wr = os.path.join(HERE, ".workroot")
    run([sys.executable, "scripts/report-render.py", "--unit", unit, "--render", "--doc", "all"], cwd=wr)
    code, out = run([sys.executable, "scripts/report-render.py", "--unit", unit, "--check"], cwd=wr)
    fails = [ln.strip() for ln in out.splitlines() if "FAIL" in ln]
    code, reg = run([sys.executable, "scripts/report-register-check.py", "--unit", unit], cwd=wr)
    hits = [ln.strip() for ln in reg.splitlines() if re.match(r"\s+outputs.*\[", ln)]
    print(f"{unit}: status gate PASS; render check {'FAIL ' + str(fails) if fails else 'PASS'}; register lines: {len(hits)}")
    for h in hits:
        print("   ", h)
    rows = progress()
    for r in rows:
        if r["unit"] == unit:
            repaired = sum(int(counts.get(k, 0)) for k in ("coarsened", "relinked", "dropped"))
            r.update(state="done", date=__import__("datetime").date.today().isoformat(), links=counts.get("links", ""),
                     held_checked=counts.get("held_checked", ""), claims_repaired=str(repaired),
                     note=f"supported {counts.get('supported')}, coarsened {counts.get('coarsened')}, relinked {counts.get('relinked')}, dropped {counts.get('dropped')}, gateway {counts.get('gateway')}, not held {counts.get('not_held')}")
    with open(PROGRESS, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    if fails:
        raise SystemExit(f"{unit}: report-render check failed — fix before committing; progress row written")
    run(["git", "add", f"outputs/reports/{unit}", "logs/cite-reread-progress.csv"])
    msg = (f"CITE-REREAD {unit}: {repaired} claims repaired over {counts.get('held_checked')} held links\n\n"
           "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>\n"
           "Claude-Session: https://claude.ai/code/session_01YGULwKCQKYvGq61x84oUj9\n")
    code, out = run(["git", "commit", "-q", "-m", msg])
    print(f"{unit}: committed" if code == 0 else f"{unit}: commit returned {code}: {out[-300:]}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2 or sys.argv[1] not in ("worksheet", "status", "apply"):
        print(__doc__); sys.exit(2)
    rows = progress()
    if sys.argv[1] == "status":
        left = [r["unit"] for r in rows if r["state"] != "done"]
        print(f"{len(rows) - len(left)} of {len(rows)} done; left: {' '.join(left)}")
        return
    if sys.argv[1] == "apply":
        for u in sys.argv[2:]:
            apply(u)
        return
    units = [r["unit"] for r in rows if r["state"] != "done"] if sys.argv[2] == "all" else sys.argv[2:]
    ctx = (load_catalogue(), load_raw_paths(),
           load_rows(status_lib.FINANCE_CSV, "url"), load_rows(status_lib.DPI_CSV, "Source urls"),
           status_lib.iiag_urls())
    for u in units:
        worksheet(u, ctx)


if __name__ == "__main__":
    main()
