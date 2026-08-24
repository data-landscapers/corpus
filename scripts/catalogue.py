#!/usr/bin/env python3
"""catalogue.py — the catalogue browse page (documentation/design.md §4).

    python scripts/catalogue.py
      -> site/catalogue/index.html            the browse-and-filter surface
      -> site/catalogue/catalogue-data.js     packed data the page reads
      -> site/catalogue/raw-catalogue.csv     the full download (published from source)
      -> site/catalogue/raw-catalogue.json    the full download

Promoted from `prototypes/catalogue-prototype.html` + `prototypes/build-catalogue-data.py`
once the browse surface was agreed. It reads the catalogue Corpus builds itself
(`outputs/catalogue/raw-catalogue.json`), packs the ten
browse fields into `catalogue-data.js`, and wraps the proven browse UI in the real
site chrome (`scripts/country.py`'s header/nav/footer).

Place and topic vocabularies come from `outputs/vocab/` — snapshotted from OSINT's
`lookups/`, because the site may not read outside `outputs/` (NOTES-FOR-OSINT #9).
Refresh that snapshot when the vocabularies change.

The catalogue carries metadata only — never source bodies. Each record links to
its publisher (`build-catalogue.py`).
"""
from __future__ import annotations
import ast, csv, json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from copy_lib import copy  # noqa: E402
import taxonomy_lib  # noqa: E402
from chrome_lib import chrome, foot  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
SITE = CORPUS / "site"
VOCAB = CORPUS / "outputs" / "vocab"
NAMES = CORPUS / "outputs" / "names"
DOC_IDS = CORPUS / "outputs" / "catalogue" / "doc-ids.csv"

ENTITY_NAMES = CORPUS / "lookups" / "entity-names.csv"
BUILD_CATALOGUE = CORPUS / "scripts" / "build-catalogue.py"

from names_lib import shard_file, shard_key  # noqa: E402  — see there for the WIN_RESERVED rule
SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def csv_cols() -> list[str]:
    """The download's column list, lifted from `build-catalogue.py` rather than restated.

    The page cuts a filtered CSV in the reader's browser, and it has to come out with
    the same sixteen columns in the same order as `raw-catalogue.csv` — two files both
    called CSV with different column sets is the thing that bites a reader six months
    later, and it is the whole reason the export fetches the full catalogue instead of
    serialising the eleven fields the browse payload happens to carry.

    So the spec is read from the one place that defines it. By syntax tree, not by
    import: `build-catalogue.py` opens the vault at module scope, which a page build
    has no business doing, and its name is hyphenated besides. A column added there
    reaches the export on the next build with nothing to change here.
    """
    tree = ast.parse(BUILD_CATALOGUE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CSV_COLS" for t in node.targets):
            return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit("catalogue: no CSV_COLS in build-catalogue.py — the filtered "
                     "download cannot be built without the column spec")


def catalogue_dir() -> Path:
    for base in (OUTPUTS,):
        if (base / "catalogue" / "raw-catalogue.json").exists():
            return base / "catalogue"
    raise SystemExit("no catalogue found in outputs/ — run scripts/rebuild.py --catalogue")


def vocab():
    places, regions = {}, {}
    with open(VOCAB / "countries.csv", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            places[r["iso-3"]] = r["country-name"]
            regions[r["iso-3"]] = r.get("Region") or ""
    # Topic labels come from Corpus's `lookups/taxonomy.csv`, not from the vocabulary
    # snapshot (Bill, 2026-08-19). The snapshot is prose as well as vocabulary, and the
    # pattern this used to run over it read `dpi.registry`'s 558-character ruling as the
    # label — which reached this page's own filter list. The slugs are still OSINT's;
    # only how they are written is decided here.
    topics = taxonomy_lib.labels()
    cats = taxonomy_lib.level1s()
    return places, regions, topics, cats


def _place_map():
    """Token(s) a slug writes -> the country name to qualify a label with."""
    m = {}
    with open(VOCAB / "countries.csv", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            name = (r.get("country-name") or "").strip()
            iso = (r.get("iso-3") or "").strip().lower()
            if not name:
                continue
            if iso:
                m[(iso,)] = name
            toks = tuple(t for t in name.lower().replace("'", " ").replace("-", " ").split() if t)
            if toks:
                m.setdefault(toks, name)
    # Forms the slugs write that the vocabulary does not, including the two-letter
    # codes — countries.csv carries iso-3 only, and `bf-`, `cv-` are common prefixes.
    m.update({("cote", "divoire"): "Côte d'Ivoire", ("civ",): "Côte d'Ivoire",
              ("drc",): "DR Congo", ("rdc",): "DR Congo", ("bf",): "Burkina Faso",
              ("cv",): "Cabo Verde", ("gnq",): "Equatorial Guinea"})
    return m


def disambiguate(ent_names: dict) -> dict:
    """Qualify a display name that several *different* entities would otherwise share.

    `build-entity-names.py` strips the place before scoring, which is right — a country
    suffix is the least distinguishing part of a slug and was winning on its own. But
    the place was then missing from the **label** too, so 17 ministries of finance and
    12 ministries of health all read the same on the page and in the row chips, and the
    reader could not tell which country's they were filtering by. 458 slugs collapsed
    onto 183 labels that way.

    Only where the collision is real: slugs that resolve to the *same* place, or to no
    place at all, are duplicate slugs for one entity (`m-kopa`, `m-kopa-holdings-ltd`)
    and should keep sharing a label. And a place already named in the display adds
    nothing — "Central Bank of Nigeria (Nigeria)" is worse than leaving it alone.
    """
    pm = _place_map()
    single = {k[0]: v for k, v in pm.items() if len(k) == 1 and len(k[0]) >= 5}

    def place_of(slug):
        t = slug.split("-")
        for n in (3, 2, 1):                      # longest wins: `burkina-faso` before `faso`
            for i in range(len(t) - n + 1):
                if tuple(t[i:i + n]) in pm:
                    return pm[tuple(t[i:i + n])]
        for tok in t:                            # last resort: adjectival or truncated
            if len(tok) < 5:
                continue
            for base, name in single.items():
                if tok.startswith(base) or base.startswith(tok):
                    return name
        return None

    by = {}
    for slug, display in ent_names.items():
        by.setdefault(display, []).append(slug)
    out = dict(ent_names)
    for display, slugs in by.items():
        if len(slugs) < 2:
            continue
        pl = {s: place_of(s) for s in slugs}
        if len(set(pl.values())) < 2:
            continue
        for s in slugs:
            p = pl[s]
            if p and p.lower() not in display.lower():
                out[s] = f"{display} ({p})"
    return out


def pack_rows(cdir: Path):
    """The ten browse fields, plus the entity tags as field 10.

    Entities are **dictionary-encoded**: field 10 holds integer offsets into a
    vocabulary array shipped once, not the slugs themselves. 24,891 tags drawn
    from 6,774 distinct slugs cost 293 KB that way against 524 KB as repeated
    strings — and the vocabulary is what the entity facet renders its menu from,
    so it would have had to be shipped regardless.
    """
    d = json.load(open(cdir / "raw-catalogue.json", encoding="utf-8"))
    items = d["items"] if isinstance(d, dict) and "items" in d else d
    ents = sorted({e for i in items for e in (i.get("entities") or [])})
    at = {slug: n for n, slug in enumerate(ents)}
    # Field 11 is the row's **stable** document id, the key the names index posts
    # against (scripts/build-names-index.py). Rows are ordered by date and shift
    # whenever a source is ingested; these ids do not.
    docid = {}
    if DOC_IDS.exists():
        with open(DOC_IDS, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                docid[r["slug"]] = int(r["id"])
    rows = [[
        i.get("title") or "",
        i.get("publisher") or "",
        (i.get("published") or "")[:10],
        i.get("places") or [],
        i.get("topics") or [],
        i.get("lens") or [],
        i.get("url") or "",
        i.get("slug") or "",
        1 if i.get("artefact") else 0,
        i.get("body_completeness") or "",
        [at[e] for e in (i.get("entities") or [])],
        docid.get(i.get("slug") or "", -1),
    ] for i in items]
    rows.sort(key=lambda r: r[2], reverse=True)
    return rows, ents


CHROME = chrome('catalogue', depth=1)

FOOT = foot(depth=1)

# Browse-surface styles — self-contained, scoped to the catalogue widget so they
# do not touch the site chrome (site-header / corpus-nav / site-footer from main.css).
STYLE = r"""
  .cat{--ink:#1b1b1b;--muted:#6b6b68;--faint:#8f8f8b;--line:#e4e2dd;
    --accent:#7a1f2b;--bg:#faf9f7;--card:#fff;--chip:#f0ede8;--warn:#8a5a12;--warnbg:#faeeda;
    max-width:1180px;margin:0 auto;padding:26px 22px 90px;color:var(--ink)}
  .cat *{box-sizing:border-box}
  .cat a{color:var(--accent);text-decoration:none}
  .cat a:hover{text-decoration:underline}
  .cat h1{font-size:26px;margin:0 0 6px;letter-spacing:-.01em}
  .cat .lede{color:var(--muted);font-size:14px;margin:0 0 8px;max-width:74ch}
  .cat .lede p{margin:0 0 8px}
  .cat .downloads{font-size:13px;color:var(--muted);margin:0 0 22px}
  .cat .searchrow{display:flex;gap:10px;margin-bottom:18px}
  .cat #q{flex:1;padding:11px 14px;border:1px solid var(--line);border-radius:8px;font-size:15px;background:var(--card);color:var(--ink)}
  .cat #q:focus{outline:none;border-color:var(--accent)}
  .cat select.sort{padding:11px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);font-size:14px;color:var(--ink)}
  .cat .chips{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:16px;min-height:1px}
  .cat .chip{display:inline-flex;align-items:center;gap:6px;background:var(--chip);border-radius:20px;padding:4px 11px;font-size:13px;color:#4a4a46}
  .cat .chip b{font-weight:500;color:var(--ink)}
  .cat .chip button{border:0;background:none;cursor:pointer;color:var(--faint);font-size:15px;line-height:1;padding:0}
  .cat .chip button:hover{color:var(--accent)}
  .cat .clearall{font-size:13px;color:var(--accent);cursor:pointer;background:none;border:0;padding:4px 2px}
  .cat .cols{display:grid;grid-template-columns:250px minmax(0,1fr);gap:30px;align-items:start}
  .cat .facet{border-bottom:1px solid var(--line);padding:0 0 14px;margin-bottom:14px}
  .cat .facet:last-child{border-bottom:0}
  .cat .facet h3{font-size:12px;text-transform:uppercase;letter-spacing:.07em;color:var(--faint);margin:0 0 9px;font-weight:600}
  .cat .ftype{width:100%;padding:6px 9px;border:1px solid var(--line);border-radius:6px;font-size:13px;margin-bottom:8px;background:var(--card);color:var(--ink)}
  .cat .ftype:focus{outline:none;border-color:var(--accent)}
  .cat .opts{max-height:236px;overflow-y:auto;margin:0 -4px}
  .cat .opt{display:flex;align-items:center;gap:8px;padding:3px 4px;border-radius:5px;cursor:pointer;font-size:13.5px;line-height:1.35}
  .cat .opt:hover{background:var(--chip)}
  .cat .opt input{margin:0;accent-color:var(--accent);flex:none}
  .cat .opt .lbl{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .cat .opt .n{color:var(--faint);font-size:12px;font-variant-numeric:tabular-nums;flex:none}
  .cat .opt.zero{opacity:.34}
  .cat .grp{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--faint);margin:9px 0 3px;padding-left:4px}
  .cat .grp:first-child{margin-top:0}
  .cat .countrow{display:flex;align-items:baseline;justify-content:space-between;gap:8px 18px;flex-wrap:wrap;margin:0 0 12px}
  .cat .count{font-size:14px;color:var(--muted);margin:0}
  .cat .count b{color:var(--ink);font-weight:600}
  .cat .dl{font-size:13px;color:var(--muted)}
  .cat .dl button{background:none;border:0;padding:0;font:inherit;color:var(--accent);cursor:pointer}
  .cat .dl button:hover{text-decoration:underline}
  .cat .dl button[disabled]{color:var(--faint);cursor:default;text-decoration:none}
  .cat .dl .dlmsg{display:block;color:var(--warn);font-size:12.5px;margin-top:3px;max-width:44ch}
  .cat .row{border-bottom:1px solid var(--line);padding:13px 0;display:grid;grid-template-columns:92px minmax(0,1fr);gap:16px}
  .cat .row .date{color:var(--faint);font-size:13px;font-variant-numeric:tabular-nums;padding-top:1px}
  .cat .row .ttl{font-size:15px;margin:0 0 3px;line-height:1.4}
  .cat .row .meta{font-size:13px;color:var(--muted);margin:0 0 6px}
  .cat .tags{display:flex;flex-wrap:wrap;gap:5px}
  .cat .tag{background:var(--chip);border-radius:4px;padding:2px 7px;font-size:12px;color:#55524c;cursor:pointer}
  .cat .tag:hover{background:#e6e2da}
  .cat .tag.pl{background:#eef1f4;color:#3f4d59}
  .cat .tag.ln{background:#f4eef0;color:#6b3742}
  .cat .tag.en{background:#eef3ee;color:#3d5442}
  .cat .opts .trunc{font-size:11.5px;color:var(--faint);padding:6px 4px 2px;font-style:italic}
  .cat .flag{background:var(--warnbg);color:var(--warn);border-radius:4px;padding:2px 7px;font-size:12px}
  .cat .empty{padding:44px 0;color:var(--muted);font-size:15px}
  .cat .more{margin:22px 0 0;padding:10px 18px;border:1px solid var(--line);background:var(--card);border-radius:8px;cursor:pointer;font-size:14px;color:var(--ink)}
  .cat .more:hover{border-color:var(--accent);color:var(--accent)}
  .cat .note{margin-top:34px;padding-top:16px;border-top:1px solid var(--line);font-size:12.5px;color:var(--faint);max-width:70ch}
  @media (max-width:860px){.cat .cols{grid-template-columns:1fr}}
"""

BODY = r"""
<div class="cat">
  <h1>Catalogue</h1>
  <div class="lede">""" + copy("catalogue", "lede") + r"""</div>
  <p class="downloads">Download the whole catalogue:
     <a href="raw-catalogue.csv" download>CSV</a> &nbsp;·&nbsp;
     <a href="raw-catalogue.json" download>JSON</a> &nbsp;— metadata only.</p>

  <div class="searchrow">
    <input id="q" type="search" placeholder="Search titles, publishers, and names inside the sources" autocomplete="off">
    <select class="sort" id="sort">
      <option value="new">Newest first</option>
      <option value="old">Oldest first</option>
      <option value="az">Title A&ndash;Z</option>
    </select>
  </div>

  <div class="chips" id="chips"></div>

  <div class="cols">
    <aside id="facets"></aside>
    <main>
      <div class="countrow"><p class="count" id="count"></p><span class="dl" id="dl"></span></div>
      <div id="results"></div>
      <button class="more" id="more" hidden>Show more</button>
      <p class="note" id="note"></p>
    </main>
  </div>
</div>
"""

SCRIPT = r"""
<script src="catalogue-data.js"></script>
<script>
(function(){
  var D = window.CATALOGUE;
  var ROWS = D.rows;
  var REGION_NAME = {XNA:'North Africa', XWA:'West Africa', XEA:'East Africa',
    XSA:'Southern Africa', XCA:'Central Africa', XAF:'Africa-wide', XSS:'Sub-Saharan', XHA:'Horn of Africa'};
  var state = {q:'', places:[], topics:[], lens:[], years:[], ents:[], sort:'new', shown:100};

  // Entity slugs arrive dictionary-encoded (field 10 = offsets into D.ents).
  // Expand once, in place: the strings are interned, so this costs array slots
  // rather than 24,891 copies, and every filter below then treats entities
  // exactly like places and topics.
  var ENTS = D.ents || [], ENTLABEL = {}, DERIVED = D.entnames || {};
  (function(){
    // A slug is not a display name — deriving those is stage 2
    // (documentation/catalogue-search.md). Until then the label is the slug,
    // mechanically prettified: title-case, except short tokens, which in this
    // vocabulary are overwhelmingly acronyms (ITU, UNDP, NIMC, ODPC, DRC, ICT).
    //
    // WORD is the exception list — short tokens that are ordinary words — and it
    // was populated by measuring, not guessing: of the 6,774 slugs, 1,548 distinct
    // tokens of four characters or fewer would be uppercased, and the frequent
    // ones were read off and sorted by hand. Re-measure the same way after a big
    // ingest; the tail below about ten occurrences is not worth chasing, because
    // a wrong entry shows up as ODPC right and BANK wrong, which is visible and
    // cheap. Ambiguous cases are left uppercase deliberately: `sa` is as often
    // South Africa as société anonyme, and `car` is more often the Central
    // African Republic than a vehicle.
    var FUNC = {of:1,for:1,and:1,the:1,de:1,du:1,des:1,da:1,do:1,das:1,dos:1,la:1,le:1,les:1,
                el:1,al:1,in:1,on:1,at:1,et:1,em:1,na:1,no:1,aux:1,o:1},
        WORD = {bank:1,fund:1,data:1,tech:1,news:1,post:1,west:1,east:1,cape:1,town:1,city:1,
                gov:1,new:1,tax:1,land:1,port:1,hub:1,net:1,pay:1,tel:1,web:1,gas:1,oil:1,
                air:1,sea:1,cash:1,card:1,link:1,soft:1,cloud:1,fibre:1,fiber:1,group:1,
                // measured off the vocabulary, 2026-08-24
                cote:1,faso:1,togo:1,mali:1,cabo:1,chad:1,sao:1,tome:1,arab:1,
                act:1,law:1,bill:1,code:1,plan:1,deal:1,cour:1,unit:1,food:1,home:1,
                one:1,lab:1,open:1,blue:1,cert:1,tide:1,jean:1,moov:1,kopa:1,yas:1,
                ltd:1,inc:1,pty:1};
    function cap(w){ return w.charAt(0).toUpperCase() + w.slice(1); }
    for (var i = 0; i < ENTS.length; i++){
      // A derived name always wins: it is what the sources themselves call the thing,
      // where the prettifier is only a guess at how to write the slug.
      if (DERIVED[ENTS[i]]){ ENTLABEL[ENTS[i]] = DERIVED[ENTS[i]]; continue; }
      ENTLABEL[ENTS[i]] = ENTS[i].split('-').map(function(w, ix){
        if (!w) return w;
        if (FUNC[w]) return ix === 0 ? cap(w) : w;
        if (w.length <= 4 && !WORD[w]) return w.toUpperCase();
        return cap(w);
      }).join(' ');
    }
  })();

  ROWS.forEach(function(r){
    r[10] = (r[10] || []).map(function(i){ return ENTS[i]; });
    // Hyphens become spaces in the search blob so "security studies" reaches
    // institute-for-security-studies. Acronym slugs match the acronym, which is
    // usually what a reader looking for one types anyway — and the derived display
    // name goes in alongside, so the expansion finds it too: `nira-uganda` is
    // reachable by "nira" and by "National Identification and Registration Authority".
    var alias = '';
    for (var ei = 0; ei < r[10].length; ei++){
      var dn = DERIVED[r[10][ei]];
      if (dn) alias += ' ' + dn;
    }
    r._s = (r[0] + ' ' + r[1] + ' ' + r[10].join(' ').replace(/-/g, ' ') + alias).toLowerCase();
    r._y = r[2].slice(0,4);
  });

  // ---- names index (stage 3) -------------------------------------------------
  // The page ships the shard *keys* only. A shard is fetched the first time a
  // query needs it, cached for the session, and never fetched at all by a reader
  // who browses without searching. Everything here degrades to the in-memory
  // search if the fetch fails, so a reader on a bad connection loses the extra
  // matches and nothing else.
  var NAMES = D.names || null, KEYS = {}, SHARDS = {}, nameHits = null, nameSeq = 0, nameBusy = false;
  var WINRESERVED = {con:1, prn:1, aux:1, nul:1};
  if (NAMES) for (var ni = 0; ni < NAMES.keys.length; ni++) KEYS[NAMES.keys[ni]] = 1;

  function shardKeyFor(q){
    // The longest shard key that prefixes the query. Fat prefixes were re-cut
    // deeper at build time and the short key then does not exist, so exactly one
    // of these can match.
    if (!NAMES || q.length < NAMES.minq) return null;
    for (var w = Math.min(5, q.length); w >= 2; w--){ var k = q.slice(0, w); if (KEYS[k]) return k; }
    return null;
  }
  function hitsFrom(text, q){
    // `Name<TAB>d,d,d`, ids delta-encoded. No offsets and no order — there is
    // nothing here to render as a snippet, and the page never tries.
    var ids = null;
    if (!text) return null;
    ids = {};
    var lines = text.split('\n');
    for (var i = 0; i < lines.length; i++){
      var tab = lines[i].indexOf('\t');
      if (tab < 1) continue;
      if (lines[i].slice(0, tab).toLowerCase().indexOf(q) === -1) continue;
      var parts = lines[i].slice(tab + 1).split(','), prev = 0;
      for (var j = 0; j < parts.length; j++){ prev += +parts[j]; ids[prev] = 1; }
    }
    return ids;
  }
  function refreshNames(){
    var q = state.q, k = shardKeyFor(q), seq = ++nameSeq;
    nameBusy = false;
    if (!k){ nameHits = null; return; }
    if (SHARDS[k] !== undefined){ nameHits = hitsFrom(SHARDS[k], q); return; }
    if (!window.fetch){ nameHits = null; return; }
    nameHits = null; nameBusy = true;
    // `con`, `prn`, `aux` and `nul` are Windows device names and cannot be filenames
    // there, so the builder escapes them with a trailing hyphen. The key stays bare
    // everywhere else — this is the one place the two differ.
    fetch('names/' + (WINRESERVED[k] ? k + '-' : k) + '.txt')
      .then(function(res){ return res.ok ? res.text() : null; })
      .then(function(t){
        SHARDS[k] = t;
        if (seq !== nameSeq) return;          // a later keystroke has overtaken this one
        nameBusy = false; nameHits = hitsFrom(t, q); redraw(false);
      })
      .catch(function(){
        SHARDS[k] = null;
        if (seq !== nameSeq) return;
        nameBusy = false; redraw(false);
      });
  }

  // ---- downloading a selection ----------------------------------------------
  // The browse payload carries eleven of the download's sixteen fields: author,
  // date_precision, finance, words and ingested were never needed to render a row,
  // so pack_rows never packed them. That leaves three ways to export a filtered
  // selection and only one of them is honest. Serialising what the page holds gives
  // a CSV with a different column set from the published one. Packing the missing
  // five gives parity, paid for by every visitor to buy an export most never ask
  // for, on a payload design.md §6 is already worried about. So: fetch the full
  // catalogue once, on the first export click, and cut the selection from it by
  // slug. A reader who browses without exporting fetches nothing at all, and what
  // comes out has the same sixteen columns as the whole-catalogue download.
  //
  // Same lazy-fetch shape as the names index above, and it degrades the same way —
  // if the fetch fails the reader still has the whole-catalogue links at the top.
  var CSVCOLS = D.cols || [], VIEW = [], FULL = null, fullPending = null, dlMsg = '';

  function fetchFull(){
    if (FULL) return Promise.resolve(FULL);
    if (fullPending) return fullPending;
    if (!window.fetch || !window.Blob || !window.URL || !URL.createObjectURL)
      return Promise.reject(new Error('unsupported'));
    fullPending = fetch('raw-catalogue.json')
      .then(function(res){ if (!res.ok) throw new Error(res.status); return res.json(); })
      .then(function(d){
        var items = d.items || [], by = {};
        for (var i = 0; i < items.length; i++) by[items[i].slug] = items[i];
        FULL = {built: d.built, note: d.note, by: by};
        return FULL;
      })
      .catch(function(err){ fullPending = null; throw err; });   // so a retry can happen
    return fullPending;
  }

  function csvCell(v){
    // `csv.DictWriter`'s QUOTE_MINIMAL, reproduced: quote only where the value
    // carries a comma, a quote or a line break, and double an inner quote.
    if (v === null || v === undefined) v = '';
    else if (v === true) v = 'True';        // Python writes its bools this way and
    else if (v === false) v = 'False';      // `finance` is one
    else if (Array.isArray(v)) v = v.join('; ');   // build-catalogue.py's own separator
    v = String(v);
    return /[",\r\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  }
  function toCSV(items){
    // CRLF and no BOM, because that is what the published file has. RENDER.md ->
    // *The finance tables* is the standing warning about the two disagreeing.
    var out = [CSVCOLS.join(',')], i, c, row;
    for (i = 0; i < items.length; i++){
      row = [];
      for (c = 0; c < CSVCOLS.length; c++) row.push(csvCell(items[i][CSVCOLS[c]]));
      out.push(row.join(','));
    }
    return out.join('\r\n') + '\r\n';
  }

  function selectionMeta(n, built){
    // The JSON carries what produced it; the CSV cannot, which is why the filename
    // carries the build date instead.
    //
    // What this is *not* is a dated edition — and neither is the whole-catalogue
    // file, deliberately (design.md §9: the catalogue is an index over other
    // people's records, republished wholesale at an undated URL). So the thing to
    // cite is the view's own url, which re-cuts against whatever the catalogue
    // holds when it is opened, and the build date says which cut this file was.
    var f = {};
    if (state.q) f.search = state.q;
    ['places','topics','ents','lens','years'].forEach(function(k){
      if (state[k].length) f[k] = state[k].slice();
    });
    if (state.sort !== 'new') f.sort = state.sort;
    return {url: location.href, filters: f, records: n,
            of: ROWS.length, cut: new Date().toISOString().slice(0, 19) + 'Z',
            note: 'A selection cut in a reader\'s browser from the catalogue as built on ' +
                  built + '. The catalogue is republished wholesale rather than versioned, ' +
                  'so cite the url above — it re-cuts this selection against whatever the ' +
                  'catalogue holds when it is opened.'};
  }

  function save(name, text, mime){
    var blob = new Blob([text], {type: mime + ';charset=utf-8'}),
        u = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = u; a.download = name;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){ URL.revokeObjectURL(u); }, 4000);
  }

  function exportSelection(fmt){
    var slugs = VIEW.map(function(r){ return r[7]; });
    dlMsg = 'busy'; drawDownload();
    fetchFull().then(function(full){
      var items = [], i, it;
      for (i = 0; i < slugs.length; i++){ it = full.by[slugs[i]]; if (it) items.push(it); }
      var base = 'catalogue-selection-' + (full.built || 'undated');
      if (fmt === 'csv') save(base + '.csv', toCSV(items), 'text/csv');
      else save(base + '.json', JSON.stringify({
        built: full.built, note: full.note,
        selection: selectionMeta(items.length, full.built),
        count: items.length, items: items
      }, null, 1) + '\n', 'application/json');
      dlMsg = ''; drawDownload();
    }).catch(function(){
      // The buttons come back with the message rather than being replaced by it:
      // the commonest cause is a dropped connection, and the fix is to press again.
      dlMsg = 'That did not come through — try again, or take the whole-catalogue ' +
              'download at the top of the page.';
      drawDownload();
    });
  }

  function drawDownload(){
    var el = document.getElementById('dl');
    // Unfiltered, the selection *is* the catalogue, and the published files are the
    // citable ones — the paragraph at the top of the page already offers them, so
    // this control stays out of the way until there is a selection to cut.
    if (!VIEW.length || VIEW.length === ROWS.length){ el.textContent = ''; return; }
    if (dlMsg === 'busy'){ el.textContent = 'Preparing the file…'; return; }
    el.innerHTML = 'Download these ' + VIEW.length.toLocaleString() + ': ' +
      '<button data-dl="csv">CSV</button> &nbsp;·&nbsp; <button data-dl="json">JSON</button>' +
      (dlMsg ? '<span class="dlmsg">' + esc(dlMsg) + '</span>' : '');
  }

  function passes(r, skip){
    if (state.q && r._s.indexOf(state.q) === -1 &&
        !(nameHits && r[11] >= 0 && nameHits[r[11]])) return false;
    if (skip !== 'places' && state.places.length && !state.places.some(function(v){return r[3].indexOf(v)>-1;})) return false;
    if (skip !== 'topics' && state.topics.length && !state.topics.some(function(v){return r[4].indexOf(v)>-1;})) return false;
    if (skip !== 'lens'   && state.lens.length   && !state.lens.some(function(v){return r[5].indexOf(v)>-1;})) return false;
    if (skip !== 'ents'   && state.ents.length   && !state.ents.some(function(v){return r[10].indexOf(v)>-1;})) return false;
    if (skip !== 'years'  && state.years.length  && state.years.indexOf(r._y) === -1) return false;
    return true;
  }
  function counts(field, idx){
    var c = {};
    for (var i=0;i<ROWS.length;i++){
      var r = ROWS[i];
      if (!passes(r, field)) continue;
      var vals = idx === 'y' ? [r._y] : r[idx];
      for (var j=0;j<vals.length;j++) c[vals[j]] = (c[vals[j]]||0)+1;
    }
    return c;
  }
  function facetBlock(key, title, idx, labels, groups, groupNames, searchable, limit){
    var c = counts(key, idx);
    var sel = state[key];
    var el = document.createElement('div');
    el.className = 'facet';
    var h = '<h3>' + title + '</h3>';
    if (searchable) h += '<input class="ftype" data-f="' + key + '" placeholder="Filter ' + title.toLowerCase() + '" autocomplete="off">';
    h += '<div class="opts" data-opts="' + key + '"></div>';
    el.innerHTML = h;
    var keys = Object.keys(labels).filter(function(k){ return c[k] || sel.indexOf(k)>-1; });
    if (idx === 'y') keys.sort().reverse();
    else keys.sort(function(a,b){ return (c[b]||0)-(c[a]||0) || labels[a].localeCompare(labels[b]); });
    var box = el.querySelector('[data-opts]');
    function paint(term){
      // `limit` caps how many options are put in the DOM, not how many can be
      // found: the type-ahead filters the whole vocabulary and the cap applies
      // to what survives it. Without this the entity facet renders 6,774
      // checkboxes on every redraw, which is what makes an uncapped vocabulary
      // affordable at all. A checked option is always drawn, however deep.
      var html = '', lastG = null, drawn = 0, hidden = 0;
      for (var ki = 0; ki < keys.length; ki++){
        var k = keys[ki], lab = labels[k], on = sel.indexOf(k) > -1;
        if (term && lab.toLowerCase().indexOf(term) === -1 && k.indexOf(term) === -1) continue;
        if (limit && drawn >= limit && !on){ hidden++; continue; }
        if (groups){
          var g = groups[k] || '—';
          if (g !== lastG){ html += '<div class="grp">' + (groupNames ? (groupNames[g]||g) : g) + '</div>'; lastG = g; }
        }
        var n = c[k] || 0;
        html += '<label class="opt' + (n ? '' : ' zero') + '">' +
          '<input type="checkbox" data-f="' + key + '" value="' + k + '"' + (on ? ' checked' : '') + '>' +
          '<span class="lbl" title="' + att(lab) + '">' + esc(lab) + '</span>' +
          '<span class="n">' + n.toLocaleString() + '</span></label>';
        drawn++;
      }
      if (hidden) html += '<div class="trunc">' + hidden.toLocaleString() + ' more — type above to narrow</div>';
      box.innerHTML = html || '<div class="grp">no matches</div>';
    }
    paint('');
    if (searchable){
      el.querySelector('.ftype').addEventListener('input', function(){ paint(this.value.trim().toLowerCase()); });
    }
    return el;
  }
  function years(){ var o={}; ROWS.forEach(function(r){ if(r._y) o[r._y]=r._y; }); return o; }
  function drawFacets(){
    var f = document.getElementById('facets');
    var keep = {};
    f.querySelectorAll('.ftype').forEach(function(i){ keep[i.dataset.f] = i.value; });
    f.innerHTML = '';
    f.appendChild(facetBlock('places','Country', 3, D.places, D.regions, REGION_NAME, true));
    f.appendChild(facetBlock('topics','Topic', 4, D.topics, D.cats, null, true));
    f.appendChild(facetBlock('ents','Named actor', 10, ENTLABEL, null, null, true, 150));
    f.appendChild(facetBlock('lens','Lens', 5, {sovereignty:'Sovereignty', colonialism:'Colonialism'}, null, null, false));
    f.appendChild(facetBlock('years','Year published', 'y', years(), null, null, false));
    f.querySelectorAll('.ftype').forEach(function(i){
      if (keep[i.dataset.f]) { i.value = keep[i.dataset.f]; i.dispatchEvent(new Event('input')); }
    });
  }
  function drawChips(){
    var c = document.getElementById('chips'), h = '';
    function add(key, label, val, text){
      h += '<span class="chip"><b>' + label + '</b> ' + esc(text) +
           ' <button data-rm="' + key + '" data-v="' + att(val) + '" aria-label="Remove">&times;</button></span>';
    }
    state.places.forEach(function(v){ add('places','Country', v, D.places[v]||v); });
    state.topics.forEach(function(v){ add('topics','Topic', v, D.topics[v]||v); });
    state.ents.forEach(function(v){ add('ents','Actor', v, ENTLABEL[v]||v); });
    state.lens.forEach(function(v){ add('lens','Lens', v, v); });
    state.years.forEach(function(v){ add('years','Year', v, v); });
    // `state.q` arrives from the URL fragment via readHash, so it is attacker-supplied
    // on a public page and must be escaped before it reaches innerHTML.
    if (state.q) h += '<span class="chip"><b>Search</b> ' + esc(state.q) + ' <button data-rm="q" data-v="">&times;</button></span>';
    if (h) h += '<button class="clearall" id="clearall">Clear all</button>';
    c.innerHTML = h;
  }
  function drawResults(){
    var out = ROWS.filter(function(r){ return passes(r, null); });
    if (state.sort === 'old') out = out.slice().reverse();
    else if (state.sort === 'az') out = out.slice().sort(function(a,b){ return a[0].localeCompare(b[0]); });
    // Held for the export, after the sort rather than before it: a downloaded
    // selection comes out in the order the reader was looking at.
    VIEW = out; dlMsg = ''; drawDownload();
    document.getElementById('count').innerHTML =
      '<b>' + out.length.toLocaleString() + '</b> of ' + ROWS.length.toLocaleString() + ' records';
    var slice = out.slice(0, state.shown), h = '';
    slice.forEach(function(r){
      var tags = '';
      r[3].slice(0,4).forEach(function(p){ tags += '<span class="tag pl" data-add="places" data-v="' + p + '">' + (D.places[p]||p) + '</span>'; });
      r[4].slice(0,4).forEach(function(t){ tags += '<span class="tag" data-add="topics" data-v="' + t + '">' + (D.topics[t]||t) + '</span>'; });
      r[10].slice(0,3).forEach(function(e){ tags += '<span class="tag en" data-add="ents" data-v="' + e + '">' + esc(ENTLABEL[e]||e) + '</span>'; });
      r[5].forEach(function(l){ tags += '<span class="tag ln" data-add="lens" data-v="' + l + '">' + l + '</span>'; });
      if (r[9] === 'paywalled') tags += '<span class="flag">paywalled</span>';
      if (r[9] === 'excerpt') tags += '<span class="flag">excerpt only</span>';
      if (r[8]) tags += '<span class="flag">document held</span>';
      h += '<div class="row"><div class="date">' + (r[2]||'undated') + '</div><div>' +
           '<p class="ttl"><a href="' + r[6] + '" target="_blank" rel="noopener">' + esc(r[0]) + '</a></p>' +
           '<p class="meta">' + esc(r[1] || 'publisher not recorded') + '</p>' +
           '<div class="tags">' + tags + '</div></div></div>';
    });
    document.getElementById('results').innerHTML = h || '<p class="empty">Nothing matches those filters. Try removing one.</p>';
    var m = document.getElementById('more');
    m.hidden = out.length <= state.shown;
    m.textContent = 'Show more (' + Math.min(100, out.length - state.shown) + ' of ' + (out.length - state.shown).toLocaleString() + ' remaining)';
    var note = 'Browsing ' + ROWS.length.toLocaleString() + ' catalogue records. Filter state is in the URL — copy the address bar to share this view.';
    if (VIEW.length && VIEW.length < ROWS.length)
      note += ' A downloaded selection carries the same sixteen columns as the whole-catalogue file, cut in your browser from the build you are looking at — so cite this view’s URL rather than the file, and it will re-cut against whatever the catalogue holds when it is opened. The JSON records the filter that produced it.';
    if (NAMES){
      if (nameBusy) note = 'Also searching ' + NAMES.n.toLocaleString() + ' names found in the sources…';
      else if (nameHits) note = 'Includes matches on names occurring in the sources, not only in titles. ' + note;
      else if (state.q && state.q.length < NAMES.minq) note = 'Type ' + NAMES.minq + ' characters or more to search names inside the sources. ' + note;
    }
    document.getElementById('note').textContent = note;
  }
  function esc(s){ return String(s).replace(/[<>&]/g, function(c){ return {'<':'&lt;','>':'&gt;','&':'&amp;'}[c]; }); }
  // For a value going into a quoted attribute rather than a text node. Filter values
  // reach these from the URL fragment, so `"` has to close nothing.
  function att(s){ return esc(s).replace(/"/g, '&quot;'); }
  function writeHash(){
    var p = [];
    if (state.q) p.push('q=' + encodeURIComponent(state.q));
    ['places','topics','ents','lens','years'].forEach(function(k){ if (state[k].length) p.push(k + '=' + state[k].join(',')); });
    if (state.sort !== 'new') p.push('sort=' + state.sort);
    history.replaceState(null, '', p.length ? '#' + p.join('&') : location.pathname);
  }
  function readHash(){
    (location.hash || '').replace(/^#/, '').split('&').forEach(function(kv){
      if (!kv) return;
      var i = kv.indexOf('='), k = kv.slice(0, i), v = decodeURIComponent(kv.slice(i + 1));
      if (k === 'q') { state.q = v.toLowerCase(); document.getElementById('q').value = v; }
      else if (k === 'sort') { state.sort = v; document.getElementById('sort').value = v; }
      else if (state[k] !== undefined) state[k] = v.split(',').filter(Boolean);
    });
  }
  function redraw(resetPage){
    if (resetPage !== false) state.shown = 100;
    drawFacets(); drawChips(); drawResults(); writeHash();
  }
  document.addEventListener('change', function(e){
    var t = e.target;
    if (t.dataset && t.dataset.f && t.type === 'checkbox'){
      var arr = state[t.dataset.f], v = t.value, i = arr.indexOf(v);
      if (t.checked && i === -1) arr.push(v); else if (!t.checked && i > -1) arr.splice(i, 1);
      redraw();
    }
    if (t.id === 'sort'){ state.sort = t.value; redraw(); }
  });
  document.addEventListener('click', function(e){
    var t = e.target;
    if (t.dataset && t.dataset.rm){
      if (t.dataset.rm === 'q'){ state.q = ''; document.getElementById('q').value = ''; refreshNames(); }
      else { var a = state[t.dataset.rm], i = a.indexOf(t.dataset.v); if (i > -1) a.splice(i, 1); }
      redraw();
    }
    if (t.id === 'clearall'){
      state.q = ''; state.places = []; state.topics = []; state.lens = []; state.years = []; state.ents = [];
      document.getElementById('q').value = ''; refreshNames(); redraw();
    }
    if (t.dataset && t.dataset.add){
      var arr2 = state[t.dataset.add];
      if (arr2.indexOf(t.dataset.v) === -1) arr2.push(t.dataset.v);
      redraw();
    }
    if (t.id === 'more'){ state.shown += 100; drawResults(); }
    if (t.dataset && t.dataset.dl){ exportSelection(t.dataset.dl); }
  });
  var timer;
  document.getElementById('q').addEventListener('input', function(){
    var v = this.value.trim().toLowerCase();
    clearTimeout(timer);
    // 150 ms rather than 120: a shard fetch is a round trip, and on a poor mobile
    // link the round trip costs far more than the bytes. Debouncing is what keeps
    // a typed word to one request instead of one per character.
    timer = setTimeout(function(){ state.q = v; refreshNames(); redraw(); }, 150);
  });
  readHash();
  refreshNames();
  redraw();
})();
</script>
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catalogue — Data Landscapers</title>
<meta name="description" content="The Data Landscapers catalogue: every source held in the base, metadata only, each record linking to its publisher.">
<link rel="icon" href="{favicon}">
<link rel="stylesheet" href="../assets/css/main.css">
<link rel="stylesheet" href="../assets/css/home.css">
<style>{style}</style>
</head>
<body>
{chrome}
{body}
{foot}
{script}
</body>
</html>
"""


def main() -> int:
    cdir = catalogue_dir()
    rows, ents = pack_rows(cdir)
    places, regions, topics, cats = vocab()
    out_dir = SITE / "catalogue"
    out_dir.mkdir(parents=True, exist_ok=True)

    # The names index, if it has been built. Only the **shard key list** is packed
    # into the page — about 12 KB — so that the first search costs exactly one
    # request rather than a manifest round-trip and then a shard. The shards
    # themselves are fetched one at a time, on demand, and never by a reader who
    # only browses. See documentation/catalogue-search.md.
    # Display names for entity slugs (stage 2). Absent slugs fall back to the page's
    # own prettifier — 64% named today, and the file is meant to be hand-corrected.
    ent_names = {}
    if ENTITY_NAMES.exists():
        with open(ENTITY_NAMES, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("display"):
                    ent_names[r["slug"]] = r["display"]

    ent_names = disambiguate(ent_names)

    nm = NAMES / "manifest.json"
    names_meta = json.loads(nm.read_text(encoding="utf-8")) if nm.exists() else None
    if names_meta:
        payload_names = {"keys": names_meta["shards"], "minq": names_meta["min_query"],
                         "n": names_meta["names"], "built": names_meta["built"]}
    else:
        payload_names = None

    # packed data the page reads
    # Only the slugs that *have* a derived name are shipped; the rest are absent and
    # the page prettifies them, so this costs nothing for the 36% still unnamed.
    # `cols` is the download's column spec, ~200 bytes, and it is what lets the page
    # cut a filtered CSV with the same sixteen columns as the published one.
    payload = {"places": places, "regions": regions, "topics": topics, "cats": cats,
               "ents": ents, "entnames": {s: n for s, n in ent_names.items() if s in set(ents)},
               "names": payload_names, "cols": csv_cols(), "rows": rows}
    data_js = out_dir / "catalogue-data.js"
    with open(data_js, "w", encoding="utf-8") as fh:
        fh.write("window.CATALOGUE = ")
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";")

    # the page
    html = PAGE.format(favicon=f"{MAIN_SITE}/assets/favicon.svg",
                       style=STYLE, chrome=CHROME, body=BODY, foot=FOOT, script=SCRIPT)
    (out_dir / "index.html").write_text(html, encoding="utf-8")

    # publish the full downloads from the catalogue Corpus built
    for name in ("raw-catalogue.csv", "raw-catalogue.json"):
        shutil.copyfile(cdir / name, out_dir / name)

    # publish the name shards, copying only what changed so an unchanged shard
    # keeps its mtime and stays out of the diff
    shard_dir = out_dir / "names"
    n_shards = 0
    if names_meta:
        shard_dir.mkdir(parents=True, exist_ok=True)
        want = set(names_meta["shards"])
        for src in sorted(NAMES.glob("*.txt")):
            if shard_key(src.name) not in want:
                continue
            dst = shard_dir / src.name
            if not dst.exists() or dst.read_bytes() != src.read_bytes():
                shutil.copyfile(src, dst)
            n_shards += 1
        # By filename, not by decoded key — see build-names-index.py's prune loop for
        # why the difference matters.
        want_files = {shard_file(k) for k in want}
        for stale in shard_dir.glob("*.txt"):
            if stale.name in want_files:
                continue
            try:
                stale.unlink()
            except OSError as exc:
                print(f"catalogue: could not delete {stale.name} ({exc}). If it is a "
                      f"Windows device name, remove it with:  del \\\\?\\{stale.resolve()}")
        # Same promise, checked again on the published side (build-names-index.py
        # → shard_file): the page fetches by key and a missing file is a silent
        # shortfall, not an error a reader would ever see.
        gone = sorted(k for k in want if not (shard_dir / shard_file(k)).is_file())
        if gone:
            raise SystemExit(f"catalogue: {len(gone)} shard(s) named in the names manifest "
                             f"are missing from site/: {', '.join(gone[:10])}")

    print(f"catalogue: {len(rows):,} records, {len(ents):,} entity slugs -> site/catalogue/  "
          f"(index.html, catalogue-data.js {data_js.stat().st_size/1024:.0f} KB, csv, json)")
    if names_meta:
        print(f"  names index: {names_meta['names']:,} names over {n_shards:,} shards, "
              f"fetched on demand")
    else:
        # `outputs/names/` is gitignored, so on a fresh clone — or after a clean — it is
        # absent and the page ships with search turned off. The shards under `site/` are
        # tracked and survive, so the published tree is then serving 1,900 files nothing
        # references. Not fatal (re-running the builder fixes it) but never what anyone
        # meant, and the prune below cannot run to tidy up because there is no manifest
        # to say what is wanted.
        orphans = len(list(shard_dir.glob("*.txt"))) if shard_dir.exists() else 0
        print("  names index: not built — run scripts/build-names-index.py")
        if orphans:
            print(f"  WARNING: {orphans:,} published shards under site/catalogue/names/ are "
                  f"now unreferenced — the page shipped without search. Run "
                  f"scripts/build-names-index.py and re-run this.")
    if ent_names:
        named = sum(1 for e in ents if e in ent_names)
        print(f"  entity display names: {named:,} of {len(ents):,} "
              f"({100*named//max(len(ents),1)}%), rest prettified from the slug")
    else:
        print("  entity display names: none — run scripts/build-entity-names.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
