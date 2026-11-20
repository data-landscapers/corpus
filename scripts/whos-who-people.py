#!/usr/bin/env python3
r"""whos-who-people.py — people, aliases and the fact table, from the cache and the lookups.

    python scripts/whos-who-people.py            build, write, report
    python scripts/whos-who-people.py --dry      report only
    python scripts/whos-who-people.py --place CIV  lint 5 over one country's organisations

`documentation/whos-who.md` §4 and §7, stage 3. Deterministic and model-free, so
`rebuild.py` runs it (stage 2e) and the reading pass runs it again after admitting.

**One person is one normalised name at one organisation.** Normalised is for comparison
only — titles and post-nominals off, case, accents and punctuation folded, token order
free. Two attestations merge automatically when their names normalise equal *and* they
resolve to one organisation, by `canonical_slug` or lineage; nothing else merges without a
`same` ruling in `person-rulings.csv`. A wrong merge credits one person with another's
office; a missed one shows a person twice. So a career across two ministries is two
people until ruled one, and every pair that looks alike is in `merge-candidates.csv`.

**An id is issued once and never moves.** `person_id` is opaque and sequential; `anchor`
ties it to the person's first attestation as an opaque hash of that cache row, which is
not derived from the name as published, so a spelling ruling or a canonical-name change
does not move it. A rebuild finds each group's id through any anchor among its rows; a
group with none is issued the next number. When a ruling joins two people the lower id
survives and the other is retired with its name blanked, never reissued.

Writes `lookups/people.csv` and `lookups/person-aliases.csv` (tracked; `hand` rows kept)
and `build/whos-who/positions.csv` and `merge-candidates.csv` (untracked).
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import re
import sys
import unicodedata

import whos_who_lib as W

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PEOPLE = W.ROOT / "lookups" / "people.csv"
ALIASES = W.ROOT / "lookups" / "person-aliases.csv"
RULINGS = W.ROOT / "lookups" / "person-rulings.csv"
SUPPRESS = W.ROOT / "lookups" / "whos-who-suppress.csv"
POSITIONS = W.ROOT / "build" / "whos-who" / "positions.csv"
CANDIDATES = W.ROOT / "build" / "whos-who" / "merge-candidates.csv"
PEOPLE_COLS = ["person_id", "name", "basis", "anchor"]
ALIAS_COLS = ["alias", "person_id", "basis"]
RULING_COLS = ["person_id_a", "person_id_b", "ruling", "ruled"]
SUPPRESS_COLS = ["person_id", "slug", "date"]
POS_COLS = ["person_id", "slug", "position", "tense", "year", "year_to", "source_url"]
CAND_COLS = ["person_id_a", "person_id_b", "test", "name_a", "name_b", "slug_a", "slug_b"]

# Titles and post-nominals: off for comparison, and off the published name when they lead
# or trail it. A title is not part of a name.
TITLES = {"dr", "dr.", "hon", "hon.", "honourable", "honorable", "eng", "eng.", "engr", "engr.",
          "prof", "prof.", "pr", "pr.", "s.e.", "se", "h.e.", "he", "mr", "mr.", "mrs", "mrs.",
          "ms", "ms.", "mme", "mme.", "m.", "me", "me.", "mlle", "sir", "dame", "rt", "rev", "rev.",
          "dra", "dra.", "sr", "sr.", "jr", "jr.", "mp", "phd", "esq", "obe", "mbe", "cbe", "ii", "iii"}
LEAD_ONLY = {"he", "se", "me", "m.", "pr", "sr"}   # words a name may really end with (*Sr* is a suffix too)
HEADS = re.compile(r"(?i)\b(president|presidente|président|presidential|prime minister|premier ministre|"
                   r"premier|primeiro[- ]ministro|primer ministro|vice[- ]president|vice[- ]président|"
                   r"vice[- ]presidente|head of state|chef de l'?[ée]tat|chef du gouvernement|king|roi|"
                   r"emir|chancellor|chancelier)\b")


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def tokens(name: str) -> list[str]:
    return [t for t in re.split(r"[\s\-]+", fold(name).replace("’", "'")) if t]


def key(name: str) -> str:
    # Titles come off the ends only: a middle *M.* is an initial, not *Monsieur*.
    toks = [re.sub(r"[^\w]", "", t) for t in tokens(published(name))]
    return " ".join(sorted(t for t in toks if t))


def published(name: str) -> str:
    words = name.split()
    while words and fold(words[0]) in TITLES:
        words.pop(0)
    while words and fold(words[-1]) in TITLES - LEAD_ONLY:
        words.pop()
    return " ".join(words)


def anchor(row: dict) -> str:
    # The whole cache row: a source naming one person in two posts is two rows, and a hash of
    # the source and name alone would tie two organisations' groups to one id.
    ident = "\x1f".join(row[c] for c in ("source_url", "name_as_written", "position", "org_as_written"))
    return hashlib.sha1(ident.encode()).hexdigest()[:12]


def is_national_government(slug: str) -> bool:
    return slug.split("-")[0] in ("government", "gouvernement", "governo", "gobierno") \
        and W.bare_country(slug.replace("-", " ")) is not None


class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def build(place: str | None = None, dry: bool = False) -> int:
    cat, names = W.catalogue(), W.display_names()
    res = W.Resolver(cat, names)
    orgs = {r["slug"]: r for r in W.read_csv(W.ORGS, W.ORG_COLS)}
    lineage = W.read_csv(W.LINEAGE, W.LINEAGE_COLS)
    rulings = W.read_csv(RULINGS, RULING_COLS)
    suppress = W.read_csv(SUPPRESS, SUPPRESS_COLS)
    old_people = W.read_csv(PEOPLE, PEOPLE_COLS)
    old_alias = W.read_csv(ALIASES, ALIAS_COLS)
    rows = [r for r in csv.DictReader(open(W.CACHE, encoding="utf-8")) if r["name_as_written"]]

    # Organisation identity: canonical slug, then lineage joins incarnations.
    org_uf = UF()
    for l in lineage:
        if l["slug"] in orgs and l["successor_slug"] in orgs:
            org_uf.union(orgs[l["slug"]]["canonical_slug"], orgs[l["successor_slug"]]["canonical_slug"])

    drops, facts = collections.Counter(), []
    for r in rows:
        slug, _ = res.resolve(r)
        if slug is None:
            drops["no organisation"] += 1
            continue
        o = orgs.get(slug)
        if o is None:
            drops["organisation unnamed"] += 1
            continue
        canon = o["canonical_slug"]
        if is_national_government(canon) and not HEADS.search(r["position"]):
            drops["government, not a head of state or government"] += 1
            continue
        k = key(r["name_as_written"])
        if len(k.split()) < 2:
            drops["name under two words once titles are off"] += 1
            continue
        if not r["year"]:
            drops["no year"] += 1
            continue
        facts.append({"row": r, "slug": canon, "org": org_uf.find(canon), "key": k})

    # Groups: one normalised name at one organisation.
    groups = collections.defaultdict(list)
    for f in facts:
        groups[(f["key"], f["org"])].append(f)
    gid = {g: i for i, g in enumerate(sorted(groups))}
    uf = UF()
    for g in gid.values():
        uf.find(g)

    # Existing ids, through anchors.
    by_anchor = {p["anchor"]: p["person_id"] for p in old_people if p["anchor"]}
    hand_alias = collections.defaultdict(set)
    for a in old_alias:
        if a["basis"] == "hand":
            hand_alias[a["alias"]].add(a["person_id"])
    group_ids = collections.defaultdict(set)
    for g, i in gid.items():
        for f in groups[g]:
            pid = by_anchor.get(anchor(f["row"]))
            if pid:
                group_ids[i].add(pid)
            if len(hand_alias.get(f["row"]["name_as_written"], ())) == 1:
                group_ids[i] |= hand_alias[f["row"]["name_as_written"]]

    # Rulings and hand aliases join groups through a shared id.
    same = UF()
    for r in rulings:
        if r["ruling"] == "same":
            same.union(r["person_id_a"], r["person_id_b"])
    by_pid = collections.defaultdict(list)
    for i, pids in group_ids.items():
        for p in pids:
            by_pid[same.find(p)].append(i)
    for members in by_pid.values():
        for i in members[1:]:
            uf.union(members[0], i)

    # Issue ids: a person keeps the lowest id any of its groups carries; one with none is new.
    issued = {p["person_id"] for p in old_people}
    seq = max((int(p[1:]) for p in issued), default=0)
    person_of_root, people = {}, {p["person_id"]: dict(p) for p in old_people}
    roots = collections.defaultdict(list)
    for g, i in gid.items():
        roots[uf.find(i)].append(g)
    retired, new = 0, 0
    for root, gs in sorted(roots.items()):
        pids = sorted({same.find(p) for i in (gid[g] for g in gs) for p in group_ids.get(i, ())}
                      | {p for i in (gid[g] for g in gs) for p in group_ids.get(i, ())})
        if pids:
            pid = pids[0]
            for other in pids[1:]:
                if other in people and people[other]["name"] and people[other]["basis"] != "hand":
                    people[other].update(name="", basis="retired")
                    retired += 1
        else:
            seq += 1
            new += 1
            pid = f"P{seq:06d}"
            first = min((f for g in gs for f in groups[g]), key=lambda f: (f["row"]["year"], f["row"]["source_url"]))
            people[pid] = {"person_id": pid, "name": "", "basis": "auto", "anchor": anchor(first["row"])}
        person_of_root[root] = pid

    suppressed_person = {s["person_id"] for s in suppress if not s["slug"]}
    suppressed_pair = {(s["person_id"], s["slug"]) for s in suppress if s["slug"]}

    # Canonical name: the fullest form, most frequent first on a tie; a hand row overrides.
    forms = collections.defaultdict(collections.Counter)
    person_groups = collections.defaultdict(list)
    for root, gs in roots.items():
        pid = person_of_root[root]
        person_groups[pid] += gs
        for g in gs:
            for f in groups[g]:
                forms[pid][published(f["row"]["name_as_written"])] += 1
    for pid, c in forms.items():
        p = people[pid]
        if pid in suppressed_person:
            p.update(name="", basis="hand")
            continue
        if p["basis"] == "hand":
            continue
        # Fullest first; then a form that does not shout a surname in capitals; then frequency.
        caps = lambda f: sum(1 for w in f.split() if len(w) > 1 and w.isupper())
        p["name"] = sorted(c.items(), key=lambda kv: (-len(kv[0].split()), caps(kv[0]), -kv[1], kv[0]))[0][0]
        p["basis"] = "auto"

    aliases = [a for a in old_alias if a["basis"] == "hand" and a["person_id"] not in suppressed_person]
    hand_pairs = {(a["alias"], a["person_id"]) for a in aliases}
    for pid, c in sorted(forms.items()):
        if pid in suppressed_person:
            continue
        for form in sorted(c):
            if (form, pid) not in hand_pairs:
                aliases.append({"alias": form, "person_id": pid, "basis": "auto"})

    positions = set()
    for pid, gs in person_groups.items():
        if pid in suppressed_person:
            continue
        for g in gs:
            for f in groups[g]:
                if (pid, f["slug"]) in suppressed_pair:
                    continue
                r = f["row"]
                positions.add((pid, f["slug"], " ".join(r["position"].split()), r["tense"], r["year"],
                               r["year_to"], r["source_url"]))

    # Candidates: what looks alike and was not merged.
    ruled = {frozenset((r["person_id_a"], r["person_id_b"])) for r in rulings}
    cands = []
    by_key = collections.defaultdict(set)
    for pid, gs in person_groups.items():
        for g in gs:
            by_key[g[0]].add((pid, g[1]))
    pname = {pid: people[pid]["name"] for pid in person_groups}

    def add(a, b, test):
        (pa, sa), (pb, sb) = a, b
        if pa != pb and frozenset((pa, pb)) not in ruled and pa not in suppressed_person \
                and pb not in suppressed_person:
            cands.append({"person_id_a": pa, "person_id_b": pb, "test": test, "name_a": pname[pa],
                          "name_b": pname[pb], "slug_a": sa, "slug_b": sb})

    place_of = {s: orgs[s]["place"] for s in orgs}
    for k, members in by_key.items():
        m = sorted(members)
        for i in range(len(m)):
            for j in range(i + 1, len(m)):
                same_place = place_of.get(m[i][1]) == place_of.get(m[j][1])
                add(m[i], m[j], "same name, same country" if same_place else "same name")
    by_org = collections.defaultdict(list)
    for k, members in by_key.items():
        for pid, org in members:
            by_org[org].append((k.split(), pid))
    for org, people_here in by_org.items():
        for ka, pa in people_here:
            for kb, pb in people_here:
                if pa >= pb or ka == kb:
                    continue
                sa, sb = set(ka), set(kb)
                if len(sa) >= 2 and len(sb) >= 2 and (sa < sb or sb < sa):
                    add((pa, org), (pb, org), "one name inside the other, one organisation")
                elif len(ka) == len(kb):
                    ini_a = {t for t in sa - sb if len(t) == 1}
                    ini_b = {t for t in sb - sa if len(t) == 1}
                    rest_a, rest_b = sa - sb - ini_a, sb - sa - ini_b
                    if (ini_a and all(any(r.startswith(i) for r in rest_b) for i in ini_a) and not rest_a) or \
                       (ini_b and all(any(r.startswith(i) for r in rest_a) for i in ini_b) and not rest_b):
                        add((pa, org), (pb, org), "initial against a given name, one organisation")

    # Lint 5: one published name under two ids within one organisation, unless ruled different.
    different = {frozenset((r["person_id_a"], r["person_id_b"])) for r in rulings if r["ruling"] == "different"}
    at = collections.defaultdict(set)
    for pid, slug, *_ in positions:
        if place is None or place_of.get(slug) == place:
            at[(W.fold(people[pid]["name"]), slug)].add(pid)
    lint5 = [(n, s, sorted(p)) for (n, s), p in at.items() if len(p) > 1
             and not all(frozenset((a, b)) in different for a in p for b in p if a < b)]

    merged = sum(1 for pid, c in forms.items() if len(c) > 1)
    print(f"{len(rows)} tuples; {len(facts)} facts; dropped: {dict(drops)}")
    print(f"{len(person_groups)} people ({new} new ids, {retired} retired); {merged} with more than one "
          f"written form; {len(positions)} positions; {len(cands)} merge candidates")
    print(f"lint 5{' (' + place + ')' if place else ''}: {len(lint5)} breach(es)")
    for b in lint5[:10]:
        print("  ", b)
    if not dry:
        W.write_csv(PEOPLE, PEOPLE_COLS, sorted(people.values(), key=lambda p: p["person_id"]))
        W.write_csv(ALIASES, ALIAS_COLS, sorted(aliases, key=lambda a: (a["person_id"], a["alias"])))
        for path, cols in ((RULINGS, RULING_COLS), (SUPPRESS, SUPPRESS_COLS)):
            if not path.exists():
                W.write_csv(path, cols, [])
        W.write_csv(POSITIONS, POS_COLS, [dict(zip(POS_COLS, p)) for p in sorted(positions)])
        W.write_csv(CANDIDATES, CAND_COLS, sorted(cands, key=lambda c: (c["test"], c["person_id_a"], c["person_id_b"])))
    return 1 if lint5 else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--place")
    a = ap.parse_args(argv)
    return build(a.place, a.dry)


if __name__ == "__main__":
    sys.exit(main())
