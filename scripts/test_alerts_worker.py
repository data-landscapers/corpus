#!/usr/bin/env python3
"""test_alerts_worker.py — the rules `workers/alerts/worker.js` decides by.

    python scripts/test_alerts_worker.py

The Worker runs on Cloudflare and nothing on this machine is Cloudflare. So the file
is written in two halves with a marker line between them: above it, every decision —
what an alert id is, what matches, what the body says, what goes in the audience
filter — as a function taking plain data and returning plain data; below it, the I/O
that does no deciding. This loads the half above the marker into a JavaScript engine
and runs it. **A test that reimplemented those rules in Python would only prove the
reimplementation right**, which is `test_catalogue_firstscreen.py`'s argument for
lifting the page's own functions out of the built page rather than copying them.

**Node if it is there, Duktape if it is not, skip if neither.** Node is the house
runner (`test_catalogue_export.py`, `test_catalogue_firstscreen.py`) and is closest to
the Worker's own runtime, but it is not installed on the machine that builds this site,
and a Worker test that never runs is not a test. `pip install dukpy` puts an engine in
Python; it handles everything the pure core uses and nothing the pure core uses is
exotic. Where the two disagree, believe Node.

Four of the cases here are about consent and privacy rather than correctness, and they
are the reason this file exists at all:

  - **the subscribe body carries no `type` key** — `type: "regular"` is how Buttondown
    documents bypassing double opt-in, it is one word wide, and it is the plausible
    wrong fix for a test address that sits at `unactivated`;
  - **`manage/list` returns no address**, on a route reachable by anyone holding a
    forwarded link;
  - **`manage/save` keeps the tags it did not write**, because Buttondown's PATCH
    replaces the list outright;
  - **the email is `archival_mode: "disabled"`**, because one body holds every reader's
    sections and the web archive has no subscriber to test them against.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
WORKER = CORPUS / "workers" / "alerts" / "worker.js"
MARKER = "// === PURE CORE ENDS HERE"

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        failures.append(name)
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")


def diff(name: str, got: str, want: str) -> None:
    """A string comparison that prints the first line that differs, not both files."""
    if got == want:
        print(f"  ok   {name}")
        return
    failures.append(name)
    g, w = got.split("\n"), want.split("\n")
    for i in range(max(len(g), len(w))):
        a = g[i] if i < len(g) else "(end)"
        b = w[i] if i < len(w) else "(end)"
        if a != b:
            print(f"  FAIL {name}\n         line {i + 1}\n         got:  {a!r}\n"
                  f"         want: {b!r}")
            return


# --------------------------------------------------------------------------- the engine

def pure_core() -> str:
    text = WORKER.read_text(encoding="utf-8")
    cut = text.find(MARKER)
    if cut < 0:
        raise SystemExit(f"test_alerts_worker: no marker line in {WORKER.name}. The "
                         f"pure core is whatever sits above '{MARKER}'; without it "
                         f"there is nothing to load.")
    return text[:cut]


def node_runner(core: str):
    tmp = Path(tempfile.mkdtemp()) / "core.js"
    tmp.write_text(core, encoding="utf-8")

    def run(expr: str):
        src = f"{core}\nprocess.stdout.write(JSON.stringify({expr}));"
        f = tmp.with_name("run.js")
        f.write_text(src, encoding="utf-8")
        p = subprocess.run(["node", str(f)], capture_output=True, text=True,
                           encoding="utf-8")
        if p.returncode != 0:
            raise SystemExit(f"node: {p.stderr.strip()[:800]}")
        return json.loads(p.stdout)
    return run


def dukpy_runner(core: str):
    import dukpy

    def run(expr: str):
        return json.loads(dukpy.evaljs(f"{core}\nJSON.stringify({expr});"))
    return run


def engine():
    core = pure_core()
    if shutil.which("node"):
        return "node", node_runner(core)
    try:
        import dukpy  # noqa: F401
    except ImportError:
        return None, None
    return "dukpy", dukpy_runner(core)


name, js = engine()
if js is None:
    print("test_alerts_worker: skipped — no JavaScript engine. Install node, or "
          "`pip install dukpy`, and run again.")
    sys.exit(0)
print(f"engine: {name}\n")


# --------------------------------------------------------------------------- fixtures

# One week of catalogue, written here rather than read from the built site: the site's
# own `recent.json` moves every day, and a golden body has to be pinned to something
# that does not. a2 carries a `{%` and a `[` in its title on purpose — see mdText.
RECORDS = """[
  {"id":"a1","title":"Kenya opens a data centre","publisher":"Nation",
   "published":"2026-09-15","ingested":"2026-09-15","places":["KEN"],
   "topics":["tech.ai"],"url":"https://example.org/1"},
  {"id":"a2","title":"Nigeria's {% raw %} [AI] strategy","publisher":"Punch",
   "published":"2026-09-14","ingested":"2026-09-14","places":["NGA"],
   "topics":["tech.ai"],"url":""},
  {"id":"a3","title":"Kenya's third licence","publisher":"Standard",
   "published":"2026-09-13","ingested":"2026-09-13","places":["KEN"],
   "topics":["tech.ai","infra.connect"],"url":"https://example.org/3"},
  {"id":"a4","title":"Ghana broadband","publisher":"Graphic",
   "published":"2026-09-13","ingested":"2026-09-13","places":["GHA"],
   "topics":["infra.connect"],"url":"https://example.org/4"},
  {"id":"a5","title":"Last month in Kenya","publisher":"Nation",
   "published":"2026-08-01","ingested":"2026-08-01","places":["KEN"],
   "topics":["tech.ai"],"url":"https://example.org/5"}
]"""

DEFS = """{
  "alert 4f1c8a20b3": {"places":["KEN","NGA"],"topics":["tech.ai"],
                       "label":"Kenya, Nigeria · Artificial intelligence","tag_id":"t1"},
  "alert 00aaff1122": {"places":["ZAF"],"topics":[],
                       "label":"South Africa · Any topic","tag_id":"t2"}
}"""

# `alert deadbeef00` has a subscriber and no definition — the orphan case. `wip-import`
# is somebody else's tag and is not an alert at all.
TALLY = """{
  "alert site": 3, "alert 4f1c8a20b3": 2, "alert 00aaff1122": 1,
  "alert deadbeef00": 1, "wip-import": 5
}"""

POSTS = """[
  {"title":"Mapping the continent","url":"https://data-landscapers.io/p/1",
   "date":"2026-09-12","description":"A note on method."},
  {"title":"An older piece","url":"https://data-landscapers.io/p/0",
   "date":"2026-07-01","description":"Out of the window."}
]"""

# What `GET /v1/tags` returns, by name. `alert 4f1c8a20b3` is deliberately given an id here that
# differs from the `tag_id` its definition holds: Buttondown's own list is the one that counts.
TAG_IDS = '{"alert site": "tag_site", "alert 4f1c8a20b3": "tag_kenya", "alert 00aaff1122": "tag_zaf"}'

PLAN = (f'planDigest({{tally: {TALLY}, defs: {DEFS}, records: {RECORDS}, tagIds: {TAG_IDS}, '
        f'mainPosts: {POSTS}, from: "2026-09-08", to: "2026-09-15", cap: 2, '
        f'siteBase: "https://corpus.data-landscapers.io"}})')


# --------------------------------------------------------------------------- the id

print("the alert id is a hash of a canonical definition")

check("places are sorted",
      js('canonicalAlert(["NGA","KEN"], ["tech.ai"])'), "P=KEN,NGA|T=tech.ai")
check("order does not matter",
      js('canonicalAlert(["NGA","KEN"], ["tech.ai"]) === '
         'canonicalAlert(["KEN","NGA"], ["tech.ai"])'), True)
check("topics are sorted too",
      js('canonicalAlert(["KEN"], ["tech.industry","tech.ai"])'),
      "P=KEN|T=tech.ai,tech.industry")
check("an empty side is Any", js('canonicalAlert([], ["tech.ai"])'), "P=any|T=tech.ai")
check("Any on both sides", js("canonicalAlert([], [])"), "P=any|T=any")
check("undefined is Any as well", js("canonicalAlert(undefined, undefined)"), "P=any|T=any")
check("Any and a country are different alerts",
      js('canonicalAlert([], ["tech.ai"]) === canonicalAlert(["KEN"], ["tech.ai"])'), False)
check("the tag name is the id, sixteen characters",
      js('alertTagName("4f1c8a20b3")'), "alert 4f1c8a20b3")
check("and it is inside Buttondown's name limit",
      js('alertTagName("4f1c8a20b3").length <= 100'), True)

check("the label reads as the menu did",
      js('alertLabel(["KEN","NGA"], ["tech.ai"], '
         '{places:{KEN:"Kenya",NGA:"Nigeria"}, topics:{"tech.ai":"AI"}})'),
      "Kenya, Nigeria · AI")
check("an unconstrained side says so",
      js('alertLabel(["KEN"], [], {places:{KEN:"Kenya"}, topics:{}})'),
      "Kenya · Any topic")
check("a code the vocabulary lost falls back to the code",
      js('alertLabel(["ZZZ"], [], {places:{}, topics:{}})'), "ZZZ · Any topic")


print("\na selection is cleaned, or refused")

vocab = '{KEN:1,NGA:1,ZAF:1,GHA:1,TZA:1,UGA:1}'
check("a comma-joined string splits", js(f'cleanCodes("NGA,KEN", {vocab}, 5)'), ["KEN", "NGA"])
check("a repeated field works too", js(f'cleanCodes(["NGA","KEN"], {vocab}, 5)'), ["KEN", "NGA"])
check("any is dropped, not refused", js(f'cleanCodes(["any"], {vocab}, 5)'), [])
check("duplicates collapse", js(f'cleanCodes(["KEN","KEN"], {vocab}, 5)'), ["KEN"])
check("a code outside the vocabulary is refused",
      js(f'cleanCodes(["ZZZ"], {vocab}, 5)'), None)
check("a sixth selection is refused",
      js(f'cleanCodes(["KEN","NGA","ZAF","GHA","TZA","UGA"], {vocab}, 5)'), None)
check("five is allowed",
      js(f'cleanCodes(["KEN","NGA","ZAF","GHA","TZA"], {vocab}, 5).length'), 5)
check("nothing given is Any", js(f'cleanCodes(undefined, {vocab}, 5)'), [])


print("\nmatching: any of the places and any of the topics")

rec = '{places:["KEN","NGA"], topics:["tech.ai","gov.policy"]}'
check("both sides, one hit each", js(f'matches({rec}, {{places:["KEN"], topics:["tech.ai"]}})'), True)
check("both sides, several given",
      js(f'matches({rec}, {{places:["ZAF","NGA"], topics:["gov.policy","infra.connect"]}})'), True)
check("place hits, topic misses",
      js(f'matches({rec}, {{places:["KEN"], topics:["infra.connect"]}})'), False)
check("topic hits, place misses",
      js(f'matches({rec}, {{places:["ZAF"], topics:["tech.ai"]}})'), False)
check("place only", js(f'matches({rec}, {{places:["KEN"], topics:[]}})'), True)
check("place only, missing", js(f'matches({rec}, {{places:["ZAF"], topics:[]}})'), False)
check("topic only", js(f'matches({rec}, {{places:[], topics:["gov.policy"]}})'), True)
check("topic only, missing", js(f'matches({rec}, {{places:[], topics:["data.open"]}})'), False)
check("Any on both sides matches everything",
      js(f'matches({rec}, {{places:[], topics:[]}})'), True)
check("a record tagged to nothing matches only Any",
      js('matches({places:[], topics:[]}, {places:["KEN"], topics:[]})'), False)


print("\nthe digest: which sections, and which tags lost their definition")

plan = js(PLAN)
check("the main-site section leads", plan["sections"][0]["tag"], "alert site")
check("two sections, not four", [s["tag"] for s in plan["sections"]],
      ["alert site", "alert 4f1c8a20b3"])
check("an alert with no match is dropped",
      any(s["tag"] == "alert 00aaff1122" for s in plan["sections"]), False)
check("a tag with no definition is recorded", plan["orphans"], ["alert deadbeef00"])
check("and the rest of the email is still built", len(plan["sections"]), 2)
check("a tag that is not an alert is ignored",
      any("wip" in s["tag"] for s in plan["sections"]), False)
check("the cap truncates and says how many are left",
      (len(plan["sections"][1]["items"]), plan["sections"][1]["more"]), (2, 1))
check("the more link is the catalogue's own fragment",
      plan["sections"][1]["moreUrl"],
      "https://corpus.data-landscapers.io/catalogue/#places=KEN,NGA&topics=tech.ai")
check("newest ingested first",
      [i["title"] for i in plan["sections"][1]["items"]],
      ["Kenya opens a data centre", "Nigeria's {% raw %} [AI] strategy"])
check("a record with no URL points at the catalogue",
      plan["sections"][1]["items"][1]["url"],
      "https://corpus.data-landscapers.io/catalogue/"
      "#q=Nigeria's%20%7B%25%20raw%20%25%7D%20%5BAI%5D%20strategy")
check("a main-site post outside the window is left out",
      [i["title"] for i in plan["sections"][0]["items"]], ["Mapping the continent"])
check("the audience filter takes Buttondown's tag id, not the name",
      [s["filter"] for s in plan["sections"]], ["tag_site", "tag_kenya"])
check("every section has an id to filter on", plan["unresolved"], [])
check("a section with no id anywhere is reported, not sent",
      js(f'planDigest({{tally: {TALLY}, defs: {DEFS}, records: {RECORDS}, tagIds: {{}}, '
         f'mainPosts: {POSTS}, from: "2026-09-08", to: "2026-09-15", cap: 2, '
         f'siteBase: "x"}}).unresolved'),
      ["alert site"])
check("a definition's stored tag_id is the fallback when the list lacks it",
      js(f'planDigest({{tally: {TALLY}, defs: {DEFS}, records: {RECORDS}, tagIds: {{}}, '
         f'mainPosts: {POSTS}, from: "2026-09-08", to: "2026-09-15", cap: 2, '
         f'siteBase: "x"}}).sections[1].filter'),
      "t1")


print("\nthe body, character for character")

GOLDEN = """<img src="https://corpus.data-landscapers.io/assets/email-banner.png" width="446" alt="New from Data Landscapers" style="display:block;width:446px;max-width:100%;height:auto;border:0;margin:0 0 16px">

{% if "alert site" in subscriber.tags %}
**[Mapping the continent](https://data-landscapers.io/p/1)**
A note on method.
{% endif %}

{% if "alert 4f1c8a20b3" in subscriber.tags %}
## Kenya, Nigeria · Artificial intelligence

**[Kenya opens a data centre](https://example.org/1)**
Nation · published 2026-09-15

**[Nigeria's &#123;% raw %&#125; \\[AI\\] strategy](https://corpus.data-landscapers.io/catalogue/#q=Nigeria's%20%7B%25%20raw%20%25%7D%20%5BAI%5D%20strategy)**
Punch · published 2026-09-14

…and 1 more in the catalogue: https://corpus.data-landscapers.io/catalogue/#places=KEN,NGA&topics=tech.ai
{% endif %}

---
Change or stop your alerts: https://corpus.data-landscapers.io/alerts/manage/#s={{ subscriber.id }}"""

body = js(f'renderDigest(({PLAN}).sections, '
          f'{{siteBase: "https://corpus.data-landscapers.io"}})')
diff("the digest body matches the golden", body, GOLDEN)

check("a title's Liquid is neutralised", "{% raw %}" in body, False)
check("only the tag tests and the subscriber id are left for Buttondown",
      sorted(set(re.findall(r"\{[%{][^}]*[%}]\}", body))),
      ['{% endif %}', '{% if "alert 4f1c8a20b3" in subscriber.tags %}',
       '{% if "alert site" in subscriber.tags %}', '{{ subscriber.id }}'])


print("\nthe email Buttondown is handed")

email = js(f'buildEmail(({PLAN}).sections, {{monday: "2026-09-21", body: "B", '
           f'sendMode: "draft"}})')
check("the archive is off", email["archival_mode"], "disabled")
check("the filter is an or", email["filters"]["predicate"], "or")
check("one filter per non-empty alert, and no others",
      [f["value"] for f in email["filters"]["filters"]],
      ["tag_site", "tag_kenya"])
check("the filter is on subscriber.tags",
      sorted({f["field"] for f in email["filters"]["filters"]}), ["subscriber.tags"])
check("SEND_MODE draft is a draft", email["status"], "draft")
check("SEND_MODE about_to_send sends",
      js('buildEmail([], {monday:"2026-09-21", body:"B", sendMode:"about_to_send"}).status'),
      "about_to_send")
check("anything else is a draft",
      js('buildEmail([], {monday:"2026-09-21", body:"B", sendMode:"whatever"}).status'), "draft")
check("the subject names the Monday a reader can read",
      email["subject"], "Data Landscapers alerts — week of 21 September 2026")
check("the subject is inside Buttondown's 2000-character limit",
      len(email["subject"]) <= 2000, True)


print("\nthe window, and a cron that ran twice")

check("a first run takes the last seven days",
      js('cronPlan({today:"2026-09-21", lastSentThrough:null, alreadySent:false})'),
      {"skip": False, "from": "2026-09-14", "to": "2026-09-20"})
check("an ordinary week carries on where it stopped",
      js('cronPlan({today:"2026-09-21", lastSentThrough:"2026-09-13", alreadySent:false})'),
      {"skip": False, "from": "2026-09-14", "to": "2026-09-20"})
check("a missed Monday catches up",
      js('cronPlan({today:"2026-09-21", lastSentThrough:"2026-09-06", alreadySent:false})'),
      {"skip": False, "from": "2026-09-07", "to": "2026-09-20"})
check("a long outage is capped at 21 days",
      js('cronPlan({today:"2026-09-21", lastSentThrough:"2026-01-01", alreadySent:false})'),
      {"skip": False, "from": "2026-08-31", "to": "2026-09-20"})
check("21 days is the window's length",
      js('daysBetween("2026-08-31", "2026-09-20") + 1'), 21)
check("a retried cron sends nothing",
      js('cronPlan({today:"2026-09-21", lastSentThrough:"2026-09-13", alreadySent:true})'),
      {"skip": True, "reason": "sent"})
check("already caught up sends nothing",
      js('cronPlan({today:"2026-09-21", lastSentThrough:"2026-09-25", alreadySent:false})'),
      {"skip": True, "reason": "caught-up", "to": "2026-09-20"})


print("\nthe subscribe call")

sub = js('subscriberBody("reader@example.org", ["alert 4f1c8a20b3","alert site"], '
         '"203.0.113.1", "https://corpus.data-landscapers.io/alerts/")')
check("no `type` key, so double opt-in cannot be bypassed", "type" in sub, False)
check("the keys are the four Buttondown is given",
      sorted(sub), ["email_address", "ip_address", "referrer_url", "tags"])
check("the tags go through", sub["tags"], ["alert 4f1c8a20b3", "alert site"])
check("no IP is no key",
      "ip_address" in js('subscriberBody("a@b.co", [], "", "")'), False)

# The source read: a site-only sign-up must reach the subscribe call with no tag
# created for it, which is a branch in the shell rather than a value from the core.
src = WORKER.read_text(encoding="utf-8")
shell = src[src.index(MARKER):]


def code_only(text: str) -> str:
    """The file with its comments taken out.

    The last two checks below are bans — on a `type: "regular"` and on a
    `console.log` — and both of those strings are written out in the Worker's own
    comments, where they are the explanation of why they are banned. A check over
    the raw file would fail on the warning rather than on the thing warned about,
    and the obvious way to make it pass again would be to delete the warning."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(l for l in text.split("\n") if not l.lstrip().startswith("//"))


code = code_only(src)
check("the only /tags call sits behind a definition",
      re.findall(r'bd\(env, "/tags"', shell), ['bd(env, "/tags"'])
check("and it is inside defineAlert",
      shell.index('bd(env, "/tags"') > shell.index("async function defineAlert"), True)
check("defineAlert is called only when there is a selection",
      'if (places.length || topics.length) {\n      tags.push(await defineAlert' in shell,
      True)
check("no `type: \"regular\"` anywhere in the code",
      re.search(r"\btype:\s*[\"']regular[\"']", code) is None, True)
check("and the warning saying why is still in the file",
      'type: "regular"' in src, True)
check("no request or response body is logged", "console.log" in code, False)


print("\nwhat a reader is shown, and what is kept when they save")

listed = js('listResponse(["alert site","alert 4f1c8a20b3","wip-import"], '
            '{"alert 4f1c8a20b3": {places:["KEN","NGA"], topics:["tech.ai"], '
            'label:"Kenya, Nigeria · AI"}})')
check("the main-site box reflects the tag", listed["site"], True)
check("one alert, with its definition", listed["alerts"],
      [{"id": "4f1c8a20b3", "places": ["KEN", "NGA"], "topics": ["tech.ai"],
        "label": "Kenya, Nigeria · AI"}])
check("no address anywhere in the response",
      "@" in json.dumps(listed), False)
check("the keys are the four the page uses",
      sorted(listed["alerts"][0]), ["id", "label", "places", "topics"])
check("an unknown subscriber looks like one with no alerts",
      js("listResponse([], {})"), {"site": False, "alerts": []})
check("an alert whose definition has gone still lists, blank",
      js('listResponse(["alert deadbeef00"], {})')["alerts"],
      [{"id": "deadbeef00", "places": [], "topics": [], "label": ""}])

check("a save keeps the tags it did not write",
      js('mergeTags(["wip-import","alert 4f1c8a20b3","alert site"], ["alert 00aaff1122"])'),
      ["wip-import", "alert 00aaff1122"])
check("saving nothing drops every alert and keeps the rest",
      js('mergeTags(["wip-import","alert site"], [])'), ["wip-import"])
check("a tag already held is not added twice",
      js('mergeTags(["alert site"], ["alert site"])'), ["alert site"])
check("alert tags are recognised by shape",
      js('[ALERT_TAG.test("alert site"), ALERT_TAG.test("alert 4f1c8a20b3"), '
         'ALERT_TAG.test("alert 4F1C8A20B3"), ALERT_TAG.test("alerts"), '
         'ALERT_TAG.test("alert 4f1c8a20"), ALERT_TAG.test("wip-import")]'),
      [True, True, False, False, False, False])

check("a subscriber id passes in both of Buttondown's forms, and a path does not",
      js('[SUBSCRIBER_ID.test("sub_0vv0sth0p68038he7avwn9cnf1"), '
         'SUBSCRIBER_ID.test("3f1c2a4e-1b2c-4d5e-8f90-123456789abc"), '
         'SUBSCRIBER_ID.test("../emails"), SUBSCRIBER_ID.test("a@b.co")]'),
      [True, True, False, False])
check("an address shaped like one passes",
      js('[looksLikeEmail("reader@example.org"), looksLikeEmail("a@b.co"), '
         'looksLikeEmail("reader@example"), looksLikeEmail("reader"), '
         'looksLikeEmail("a b@example.org"), looksLikeEmail("")]'),
      [True, True, False, False, False, False])


print("\nthe feed is a feed, empty or full")

ATOM = "{http://www.w3.org/2005/Atom}"


def parse(xml: str):
    return ET.fromstring(xml)


opts = ('{title:"Kenya · AI", selfUrl:"https://corpus.data-landscapers.io/api/alerts/'
        'feed?places=KEN", altUrl:"https://corpus.data-landscapers.io/catalogue/#places=KEN", '
        'siteBase:"https://corpus.data-landscapers.io", built:"2026-09-16"}')

empty = js(f"atomFeed([], {opts})")
root = parse(empty)
check("an empty feed parses", root.tag, f"{ATOM}feed")
check("and has no entries", len(root.findall(f"{ATOM}entry")), 0)
check("but still carries a title and an updated",
      (root.findtext(f"{ATOM}title"), root.findtext(f"{ATOM}updated")),
      ("Kenya · AI", "2026-09-16T00:00:00Z"))

full = js(f"atomFeed({RECORDS}, {opts})")
root = parse(full)
entries = root.findall(f"{ATOM}entry")
check("a full feed parses", root.tag, f"{ATOM}feed")
check("one entry per record", len(entries), 5)
check("the feed's updated is the newest entry",
      root.findtext(f"{ATOM}updated"), "2026-09-15T00:00:00Z")
check("the entry id is a tag URI with a fixed year",
      entries[0].findtext(f"{ATOM}id"), "tag:corpus.data-landscapers.io,2026:a1")
check("the title is the record's, unescaped by the parser",
      entries[1].findtext(f"{ATOM}title"), "Nigeria's {% raw %} [AI] strategy")
check("a record with no URL links to the catalogue",
      entries[1].find(f"{ATOM}link").get("href").startswith(
          "https://corpus.data-landscapers.io/catalogue/#q="), True)
check("dates are the ingested day at midnight UTC",
      entries[0].findtext(f"{ATOM}updated"), "2026-09-15T00:00:00Z")
check("the summary is the publisher and the publication date",
      entries[0].findtext(f"{ATOM}summary"), "Nation · published 2026-09-15")


print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
