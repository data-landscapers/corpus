/**
 * corpus-alerts — one weekly email per reader, built here and handed to Buttondown to send.
 *
 * `documentation/catalogue-alerts.md` is the design record; the build brief this was
 * written to is archived at `documentation/archived/catalogue-alerts-build.md` Part 1 B.
 * README.md beside this file is a pointer to both.
 *
 * WHAT IT DOES. Four routes and a cron. The routes take a sign-up, serve a plain Atom feed
 * for readers who want no email at all, and let a reader list and edit what they hold. The
 * cron, at 07:00 UTC on a Monday, reads the site's own `recent.json`, works out which alerts
 * have anything new in them, builds **one** Markdown body with a section per alert wrapped in
 * a test on the reader's tags, and posts it to Buttondown with an audience filter naming
 * exactly those alerts. A reader none of whose alerts matched is outside the filter and gets
 * no email at all.
 *
 * IT HOLDS NO ADDRESS, AND IT LOGS NONE. KV holds alert *definitions* — a set of place codes
 * and topic slugs, no more personal than a catalogue URL — and three dates. Addresses live at
 * Buttondown. Two calls here receive them anyway (`manage/list`, and the cron's tally) and
 * both discard them in the same expression that reads the tags. There is no `console.log` of
 * a request or a response body anywhere below, and adding one would be the whole of the leak.
 *
 * THE BODY IS NEVER SENT TWICE. `last_sent_through` makes a missed Monday catch up rather
 * than drop items; `sent:<date>` makes a retried cron a no-op. Both are UTC, as is every date
 * in the handler and every `ingested` date the site publishes. Buttondown's own timezone is
 * London and nothing here reads it.
 *
 * SEND_MODE IS `draft` OR `about_to_send`, and either may be permanent. On `draft` the body
 * lands in Buttondown's Drafts for Bill to release, which is the workflow he already has for
 * the main site. Nothing downstream reads the difference.
 *
 * THE FIRST HALF OF THIS FILE IS PURE. Every decision — what an alert id is, what matches,
 * what the body says, what goes in the audience filter — is a function taking plain data and
 * returning plain data, and `scripts/test_alerts_worker.py` loads that half on its own and
 * runs it. The I/O shell below the marker does no deciding. That split is the only reason
 * these rules are testable at all: there is no Cloudflare runtime on the machine that builds
 * this site.
 */

/** Buttondown holds the list. Every call carries `Authorization: Token <key>`. */
const API = "https://api.buttondown.com/v1";

/** The main-site alert. Created by hand (design step A9); this Worker never creates it. */
const SITE_TAG = "alert site";

/** `alert site`, or `alert ` + ten hex. Anything else on a subscriber is somebody else's tag. */
const ALERT_TAG = /^alert (site|[0-9a-f]{10})$/;

/** The tag colour, repeated from A9 so a tag this Worker creates matches the one Bill did. */
const TAG_COLOUR = "#1a5f7a";

/** At most this many items in one section; the rest become "and N more in the catalogue". */
const ITEM_CAP = 25;

/** At most this many entries in an Atom feed. */
const FEED_CAP = 200;

/** Five of each per alert, ten alerts per reader — the caps `alerts.py` also enforces. */
const MAX_PER_FACET = 5;
const MAX_ALERTS = 10;

/** The send window never reaches back further than this, however long the cron was down. */
const MAX_WINDOW_DAYS = 21;

/*
 * AN AUDIENCE FILTER ON `subscriber.tags` TAKES A TAG'S **ID**, NOT ITS NAME — settled in D9 on
 * 2026-09-16, when every filter carrying a name came back `422 Tag filters must be valid tag
 * identifiers`. The body's Liquid test still uses names, because `subscriber.tags` in a template
 * is a list of names. So the two halves of one section are keyed differently, and the cron looks
 * every id up from `GET /v1/tags` at send time rather than trusting `def:<id>.tag_id`: that is
 * empty for any tag whose creation call was refused, and `alert site` was made by hand and has no
 * definition at all.
 */

/**
 * The tag URI namespace for feed entry ids. **The year is fixed and is not the current one.**
 * A tag URI's date names when the namespace was minted, not when the entry was written; moving
 * it would change the id of every entry already in a reader's feed reader and show them the
 * catalogue again from the top.
 */
const TAG_BASE = "tag:corpus.data-landscapers.io,2026:";

/**
 * The first line of every digest: the site logo and *New from Data Landscapers*, as one image.
 *
 * **It is in the body because nowhere else holds it in a real email** (Bill, 2026-09-16).
 * Buttondown's template puts its icon above the subject and the newsletter name below it;
 * in a sent email the icon is fixed at 40px whatever CSS says, and the Header field shows
 * only on the web version. So the newsletter icon is a transparent image, CSS hides the
 * template's subject and name, and this image leads the body. The `width` attribute is what
 * mail clients obey; the style lets a phone shrink it. `site/assets/email-banner.png` is drawn
 * at 3x for this size.
 */
const BANNER = '<img src="https://corpus.data-landscapers.io/assets/email-banner.png" ' +
  'width="446" alt="New from Data Landscapers" ' +
  'style="display:block;width:446px;max-width:100%;height:auto;border:0;margin:0 0 16px">';

/**
 * A Buttondown subscriber id, in either of the two forms it comes in: a UUID with hyphens,
 * as `{{ subscriber.id }}` renders in an email, or a TypeID with an underscore, `sub_…`, as
 * the dashboard shows it. The first version allowed hyphens only, so a manage link built
 * from the dashboard's id listed nothing and saved nothing (2026-09-16, D14). The check is
 * there to keep a path segment out of Buttondown's URL, not to know the format.
 */
const SUBSCRIBER_ID = /^[A-Za-z0-9_-]{8,64}$/;

const MONTHS = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"];

// --------------------------------------------------------------------------- dates

/** `YYYY-MM-DD` for a Date, in UTC. */
function isoDay(d) {
  return d.toISOString().slice(0, 10);
}

/** `YYYY-MM-DD` shifted by whole days, in UTC. String in, string out. */
function shiftDay(iso, days) {
  const d = new Date(iso + "T00:00:00Z");
  d.setUTCDate(d.getUTCDate() + days);
  return isoDay(d);
}

/** Whole days from `a` to `b`, both `YYYY-MM-DD`. Negative when `b` is earlier. */
function daysBetween(a, b) {
  return Math.round((Date.parse(b + "T00:00:00Z") - Date.parse(a + "T00:00:00Z")) / 86400000);
}

/** `2026-09-21` -> `21 September 2026`, for the subject line a reader actually reads. */
function longDay(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || "");
  if (!m) { return iso || ""; }
  return `${Number(m[3])} ${MONTHS[Number(m[2]) - 1]} ${m[1]}`;
}

function inWindow(iso, from, to) {
  return typeof iso === "string" && iso >= from && iso <= to;
}

// --------------------------------------------------------------------------- alerts

/**
 * The canonical form of an alert definition, which is what the id is a hash of.
 *
 * `P=KEN,NGA|T=tech.ai`, with each side sorted and an empty side written `any`. Sorting is
 * what makes two readers who picked the same countries in a different order share one tag and
 * one section instead of holding two alerts that mean the same thing.
 */
function canonicalAlert(places, topics) {
  const side = (xs) => (xs && xs.length ? xs.slice().sort().join(",") : "any");
  return `P=${side(places)}|T=${side(topics)}`;
}

/** The tag name for an alert id. Sixteen characters, inside Buttondown's 100-character limit. */
function alertTagName(id) {
  return `alert ${id}`;
}

/**
 * The alert's public label — the section heading, the feed title, the tag's description.
 *
 * `Kenya, Nigeria · Artificial intelligence`, with a side written `Any country` or `Any topic`
 * where it is unconstrained. Labels come from the vocabulary the catalogue's own facets use, so
 * a heading here reads the same as the menu the reader picked from; a code the vocabulary has
 * since dropped falls back to the code rather than disappearing from its own heading.
 */
function alertLabel(places, topics, vocab) {
  const names = (xs, map, any) =>
    (xs && xs.length ? xs.map((k) => (map && map[k]) || k).join(", ") : any);
  return `${names(places, vocab && vocab.places, "Any country")} · ` +
         `${names(topics, vocab && vocab.topics, "Any topic")}`;
}

/**
 * A reader's selection, cleaned and checked, or `null` if it is not one.
 *
 * Takes what a form or a JSON body offers — a list, or one comma-joined string, or both, which
 * is what a `<select multiple>` and a hand-written query string respectively produce — and
 * returns sorted unique codes. `any` is dropped rather than rejected: it is how the page says
 * *no constraint*, and an empty list is how everything below says the same thing.
 *
 * **Null means refuse, and refusing is cheap.** A code outside the vocabulary or a sixth
 * selection is either a stale link or somebody trying to mint definitions in bulk, and neither
 * wants a tag creating for it.
 */
function cleanCodes(raw, vocab, max) {
  const parts = [];
  const push = (v) => {
    String(v).split(",").forEach((p) => {
      const t = p.trim();
      if (t && t !== "any" && parts.indexOf(t) === -1) { parts.push(t); }
    });
  };
  if (Array.isArray(raw)) { raw.forEach(push); } else if (raw !== undefined && raw !== null) { push(raw); }
  if (parts.length > (max || MAX_PER_FACET)) { return null; }
  for (const p of parts) {
    if (!vocab || !Object.prototype.hasOwnProperty.call(vocab, p)) { return null; }
  }
  return parts.sort();
}

/** A document matches an alert if it carries **any** of its places and **any** of its topics. */
function matches(record, def) {
  const hit = (have, want) => !want || !want.length ||
    (have || []).some((v) => want.indexOf(v) > -1);
  return hit(record.places, def.places) && hit(record.topics, def.topics);
}

/** Newest ingested first, with the published date and the title breaking ties. */
function byNewest(a, b) {
  if (a.ingested !== b.ingested) { return a.ingested < b.ingested ? 1 : -1; }
  if ((a.published || "") !== (b.published || "")) {
    return (a.published || "") < (b.published || "") ? 1 : -1;
  }
  return (a.title || "") < (b.title || "") ? -1 : 1;
}

/** The catalogue link under a truncated section — the catalogue's own fragment grammar. */
function catalogueUrl(def, siteBase) {
  const q = [];
  if (def.places && def.places.length) { q.push("places=" + def.places.join(",")); }
  if (def.topics && def.topics.length) { q.push("topics=" + def.topics.join(",")); }
  return `${siteBase}/catalogue/` + (q.length ? "#" + q.join("&") : "");
}

/** Where an entry points when the record carries no URL of its own. */
function catalogueSearchUrl(title, siteBase) {
  return `${siteBase}/catalogue/#q=${encodeURIComponent(title || "")}`;
}

// --------------------------------------------------------------------------- the digest

/**
 * Markdown-safe reader-facing text.
 *
 * Two hazards, and the second is the one that would not look like a bug. A title carrying `[`
 * or `*` breaks the link or italicises the rest of the section, which is visible. A title
 * carrying `{{` or `{%` is **Liquid**, and Buttondown renders the body as a template before it
 * sends — so a document called something with braces in it would have its title evaluated
 * against the subscriber, in an email nobody could unsend. Braces become entities here; they
 * render as braces and mean nothing to the template engine.
 */
function mdText(s) {
  return String(s === undefined || s === null ? "" : s)
    .replace(/\s+/g, " ")
    .replace(/\\/g, "\\\\")
    .replace(/([[\]*_`#])/g, "\\$1")
    .replace(/\{/g, "&#123;")
    .replace(/\}/g, "&#125;")
    .trim();
}

/** A URL safe inside `(...)` — and, like the text above, carrying no braces for Liquid. */
function mdUrl(u) {
  return String(u || "")
    .replace(/\s/g, "%20")
    .replace(/\(/g, "%28")
    .replace(/\)/g, "%29")
    .replace(/\{/g, "%7B")
    .replace(/\}/g, "%7D");
}

/**
 * Which sections this week's email has, and which tags have lost their definition.
 *
 * The main-site section leads, then one section per alert tag that has a subscriber, a
 * definition and at least one match inside the window. Alerts with no match are dropped
 * entirely — that is what *No new documents, no email* is, once the audience filter is built
 * from the same list.
 *
 * **A tag whose definition has gone is skipped and recorded, not fatal.** `recent.json` carries
 * 28 days and the window reaches back at most 21, so a definition restored inside three weeks
 * costs its reader nothing; abandoning the run would cost everybody else their email.
 */
function planDigest(o) {
  const tally = o.tally || {};
  const defs = o.defs || {};
  const cap = o.cap || ITEM_CAP;
  const tagIds = o.tagIds || {};
  const sections = [];
  const orphans = [];

  if (tally[SITE_TAG] > 0) {
    const posts = (o.mainPosts || [])
      .filter((p) => inWindow((p.date || "").slice(0, 10), o.from, o.to));
    if (posts.length) {
      sections.push({
        tag: SITE_TAG,
        filter: tagIds[SITE_TAG] || "",
        heading: "New on data-landscapers.io",
        items: posts.slice(0, cap).map((p) => ({
          title: p.title, url: p.url, line: p.description || "",
        })),
        more: 0,
        moreUrl: "",
      });
    }
  }

  const names = Object.keys(tally)
    .filter((n) => n !== SITE_TAG && ALERT_TAG.test(n) && tally[n] > 0)
    .sort();

  for (const name of names) {
    const def = defs[name];
    if (!def) { orphans.push(name); continue; }
    const hits = (o.records || [])
      .filter((r) => inWindow(r.ingested, o.from, o.to) && matches(r, def))
      .sort(byNewest);
    if (!hits.length) { continue; }
    sections.push({
      tag: name,
      filter: tagIds[name] || (def.tag_id ? String(def.tag_id) : ""),
      heading: def.label || alertLabel(def.places, def.topics, o.vocab),
      items: hits.slice(0, cap).map((r) => ({
        title: r.title,
        url: r.url || catalogueSearchUrl(r.title, o.siteBase),
        line: [r.publisher, r.published ? `published ${r.published}` : ""]
          .filter(Boolean).join(" · "),
      })),
      more: Math.max(0, hits.length - cap),
      moreUrl: catalogueUrl(def, o.siteBase),
    });
  }

  // A section whose tag has no id cannot be put in the audience filter, and sending it
  // without one would send it to nobody — or, filtered on nothing, to everybody. The caller
  // refuses to build the email while this list is not empty.
  const unresolved = sections.filter((s) => !s.filter).map((s) => s.tag);
  return { sections, orphans, unresolved };
}

/**
 * The one Markdown body every reader receives, with a Liquid test around each section.
 *
 * Only `subscriber.tags` and `subscriber.id` are left for Buttondown to render; the items are
 * written in here. The tag test is the documented form — `subscriber.tags` is a list of tag
 * **names**, and Buttondown's own example is `{% if 'python' in subscriber.tags %}`.
 */
function renderDigest(sections, o) {
  // No opening sentence and no heading over the main site's section: the banner already says
  // *New from Data Landscapers*, and a line repeating it under the banner read as a second
  // title (Bill, 2026-09-16). The catalogue sections keep their headings — they are how a
  // reader with several alerts tells them apart.
  const out = [BANNER, ""];
  for (const s of sections) {
    out.push(`{% if "${s.tag}" in subscriber.tags %}`);
    // `###`, an h3: the site sets a section heading at h3 size, and at h2 the email's headings
    // outweighed the banner above them (Bill, 2026-09-16).
    if (s.tag !== SITE_TAG) { out.push(`### ${mdText(s.heading)}`, ""); }
    const blocks = s.items.map((it) => {
      const lines = [`**[${mdText(it.title)}](${mdUrl(it.url)})**`];
      if (it.line) { lines.push(mdText(it.line)); }
      return lines.join("\n");
    });
    if (s.more) {
      blocks.push(`…and ${s.more} more in the catalogue: ${s.moreUrl}`);
    }
    out.push(blocks.join("\n\n"));
    out.push("{% endif %}", "");
  }
  out.push("---", `Change or stop your alerts: ${o.siteBase}/alerts/manage/#s={{ subscriber.id }}`);
  return out.join("\n");
}

/**
 * The `POST /v1/emails` body.
 *
 * **`archival_mode` is `disabled` and must stay so.** One body holds every reader's sections,
 * and a web archive render has no subscriber to test against — so every section would show at
 * once, at a permanent public URL. Nothing private leaks; the page is simply not readable and
 * not where this belongs.
 *
 * The filter is an `or` over one entry per section, so a reader whose alerts all came up empty
 * is outside the audience and receives nothing.
 */
function buildEmail(sections, o) {
  return {
    subject: `Data Landscapers alerts — week of ${longDay(o.monday)}`,
    body: o.body,
    status: String(o.sendMode || "").trim() === "about_to_send" ? "about_to_send" : "draft",
    archival_mode: "disabled",
    filters: {
      predicate: "or",
      groups: [],
      filters: sections.map((s) => ({
        field: "subscriber.tags", operator: "contains", value: s.filter,
      })),
    },
  };
}

/**
 * The send window, or a reason not to send.
 *
 * The day after `last_sent_through` to yesterday, capped at 21 days; the last 7 on a first run.
 * A cron that already wrote `sent:<today>` stops here — a retry must not send a second copy of
 * a body Buttondown already has.
 */
function cronPlan(o) {
  if (o.alreadySent) { return { skip: true, reason: "sent" }; }
  const to = shiftDay(o.today, -1);
  let from = o.lastSentThrough ? shiftDay(o.lastSentThrough, 1) : shiftDay(to, -6);
  if (daysBetween(from, to) > MAX_WINDOW_DAYS - 1) { from = shiftDay(to, -(MAX_WINDOW_DAYS - 1)); }
  if (from > to) { return { skip: true, reason: "caught-up", to }; }
  return { skip: false, from, to };
}

// --------------------------------------------------------------------------- subscribers

/**
 * The `POST /v1/subscribers` body.
 *
 * **It must never carry a `type` field.** `SubscriberInput` accepts one, and `type: "regular"`
 * is precisely how Buttondown documents bypassing double opt-in for a single subscriber. Sent
 * from here it would confirm an address nobody confirmed — a consent failure, one word wide, in
 * the one call that handles a stranger's email address. Absent, Buttondown creates the
 * subscriber `unactivated` and sends its own confirmation, which is the whole point.
 *
 * It is also the plausible wrong fix: a test address sitting at `unactivated` looks like a bug,
 * and `type: "regular"` makes the symptom go away. `scripts/test_alerts_worker.py` asserts the
 * key's absence so that edit cannot survive a test run.
 */
function subscriberBody(email, tags, ip, referrer) {
  const body = { email_address: email, tags: tags.slice() };
  if (ip) { body.ip_address = ip; }
  if (referrer) { body.referrer_url = referrer; }
  return body;
}

/**
 * The tag list to PATCH onto a subscriber: their alerts replaced, everything else kept.
 *
 * Buttondown's PATCH replaces the list outright, so the tags it holds for some other reason —
 * a segment Bill made, an import marker — have to be read back and written again or the save
 * quietly strips them.
 */
function mergeTags(existing, alertTags) {
  const keep = (existing || []).filter((t) => !ALERT_TAG.test(t));
  const out = keep.slice();
  for (const t of alertTags.slice().sort()) {
    if (out.indexOf(t) === -1) { out.push(t); }
  }
  return out;
}

/** Every alert tag on a subscriber, in a stable order. */
function alertTags(tags) {
  return (tags || []).filter((t) => ALERT_TAG.test(t)).sort();
}

/**
 * What `manage/list` answers with.
 *
 * **No address, ever** — not the field, not a hash of it, not a masked form of it. The page
 * knows whose alerts it is showing because the reader opened it from their own email; it has
 * no use for the address and this response is reachable by anyone holding a forwarded link.
 * An unknown subscriber id gets the same shape as one with no alerts.
 */
function listResponse(tags, defs) {
  const held = alertTags(tags);
  return {
    site: held.indexOf(SITE_TAG) > -1,
    alerts: held.filter((t) => t !== SITE_TAG).map((t) => {
      const def = defs[t] || {};
      return {
        id: t.slice("alert ".length),
        places: def.places || [],
        topics: def.topics || [],
        label: def.label || "",
      };
    }),
  };
}

/** An address shaped like one. Buttondown decides whether it exists; this rejects the typos. */
function looksLikeEmail(s) {
  return typeof s === "string" && s.length <= 254 &&
    /^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$/.test(s);
}

// --------------------------------------------------------------------------- the feed

function xmlEscape(s) {
  return String(s === undefined || s === null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/**
 * Atom 1.0 for a selection, for readers who want the catalogue without giving an address.
 *
 * An empty result is a valid feed with no entries, not a 404: a reader whose countries had a
 * quiet week should see an empty feed rather than an error their reader will eventually stop
 * polling. Dates are the `ingested` day at midnight UTC — the catalogue records a day, not a
 * time, and inventing one would put entries in an order the catalogue does not hold.
 */
function atomFeed(rows, o) {
  const updated = rows.length ? rows[0].ingested : o.built;
  const out = [
    '<?xml version="1.0" encoding="utf-8"?>',
    '<feed xmlns="http://www.w3.org/2005/Atom">',
    `  <title>${xmlEscape(o.title)}</title>`,
    `  <id>${xmlEscape(o.selfUrl)}</id>`,
    `  <link rel="self" href="${xmlEscape(o.selfUrl)}"/>`,
    `  <link rel="alternate" href="${xmlEscape(o.altUrl)}"/>`,
    `  <updated>${xmlEscape(updated)}T00:00:00Z</updated>`,
    "  <author><name>Data Landscapers</name></author>",
  ];
  for (const r of rows) {
    const link = r.url || catalogueSearchUrl(r.title, o.siteBase);
    const summary = [r.publisher, r.published ? `published ${r.published}` : ""]
      .filter(Boolean).join(" · ");
    out.push(
      "  <entry>",
      `    <id>${TAG_BASE}${xmlEscape(r.id)}</id>`,
      `    <title>${xmlEscape(r.title)}</title>`,
      `    <link href="${xmlEscape(link)}"/>`,
      `    <updated>${xmlEscape(r.ingested)}T00:00:00Z</updated>`,
      `    <published>${xmlEscape(r.ingested)}T00:00:00Z</published>`,
      `    <summary>${xmlEscape(summary)}</summary>`,
      "  </entry>");
  }
  out.push("</feed>");
  return out.join("\n");
}

// === PURE CORE ENDS HERE — scripts/test_alerts_worker.py loads everything above this line ===

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "");
    try {
      if (path === "/api/alerts/feed" && request.method === "GET") {
        return await feedRoute(request, env, url, ctx);
      }
      if (path === "/api/alerts/subscribe" && request.method === "POST") {
        return await subscribeRoute(request, env);
      }
      if (path === "/api/alerts/manage/list" && request.method === "POST") {
        return await manageListRoute(request, env);
      }
      if (path === "/api/alerts/manage/save" && request.method === "POST") {
        return await manageSaveRoute(request, env);
      }
      if (path === "/api/alerts/run" && request.method === "POST") {
        return await runRoute(request, env);
      }
    } catch (err) {
      // The error's message, never the request: a body here would be an address in a
      // response. Every message that can reach this line is one this file writes
      // (`vocab.json 404`, `subscribers 403`) or the runtime's own, and none carries a
      // reader's data — so it is returned, because a 503 that says only "unavailable"
      // is how D1 cost a round of guessing.
      return json({ error: "unavailable", detail: String((err && err.message) || err) }, 503);
    }
    return new Response("Not found", { status: 404 });
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(runCronRecorded(env));
  },
};

// --------------------------------------------------------------------------- helpers

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

function seeOther(location) {
  return new Response(null, { status: 303, headers: { location } });
}

/**
 * A URL variable as typed into the dashboard, trimmed of spaces and a trailing slash.
 *
 * The dashboard stores exactly what is pasted, and on 2026-09-16 `SITE` came through with a
 * leading space that survived being re-entered — so every link this Worker writes began
 * ` https://`. Trimming here means a stray space in a settings field is not a defect in
 * every email.
 */
function urlVar(value, fallback) {
  return String(value || fallback).trim().replace(/\/+$/, "");
}

function site(env) { return urlVar(env.SITE, "https://corpus.data-landscapers.io"); }
function mainSite(env) { return urlVar(env.MAIN_SITE, "https://data-landscapers.io"); }

function bd(env, path, init) {
  const opts = init || {};
  return fetch(API + path, {
    method: opts.method || "GET",
    headers: Object.assign({
      Authorization: `Token ${env.BUTTONDOWN_API_KEY}`,
      "content-type": "application/json",
    }, opts.headers || {}),
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
}

/**
 * Turnstile, with the client IP, as Cloudflare documents it.
 *
 * A missing secret fails closed. A widget key that has not been created yet (the placeholder
 * `alerts.py` ships until step C4) fails here rather than reaching Buttondown, which is the
 * right direction: no tag, no subscriber, no confirmation email.
 */
async function turnstileOk(request, env, token) {
  // Trimmed for the reason `urlVar` trims: the dashboard keeps a pasted space.
  const secret = String(env.TURNSTILE_SECRET || "").trim();
  const response = String(token || "").trim();
  if (!secret || !response) { return false; }
  const form = new FormData();
  form.append("secret", secret);
  form.append("response", response);
  const ip = request.headers.get("cf-connecting-ip");
  if (ip) { form.append("remoteip", ip); }
  const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify",
                          { method: "POST", body: form });
  if (!res.ok) { return false; }
  const data = await res.json();
  return data.success === true;
}

/**
 * Where `recent.json` and `vocab.json` are read from: the committed copies in the Corpus
 * repository, not the published site.
 *
 * **Not `SITE`, and the reason is Cloudflare's, not ours.** `corpus.data-landscapers.io/*` is
 * `download-log`'s route, so a fetch from here to the site's own address is one Worker fetching
 * through another on the same zone — which Cloudflare refuses unless a compatibility flag is set
 * that the dashboard does not offer (design step D1, 2026-09-16: every call came back 503). The
 * repository holds the same bytes, because `site/` is rendered locally and committed, and GitHub
 * Pages serves what was pushed. It lags a push by a few minutes, which a file read once a week
 * and cached for fifteen minutes does not notice.
 */
const DATA_BASE = "https://raw.githubusercontent.com/data-landscapers/corpus/main/site";

/** `recent.json` and `vocab.json`, cached at the edge — the site rebuilds them once a day. */
async function siteJson(env, name, ttl) {
  const res = await fetch(`${DATA_BASE}/alerts/${name}`, {
    cf: { cacheTtl: ttl, cacheEverything: true },
  });
  if (!res.ok) { throw new Error(`${name} ${res.status}`); }
  return res.json();
}

/** The alert id: ten hex of the SHA-256 of the canonical definition. */
async function alertId(places, topics) {
  const data = new TextEncoder().encode(canonicalAlert(places, topics));
  const hash = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 10);
}

async function putDef(env, id, places, topics, label, tagId) {
  await env.ALERTS.put(`def:${id}`, JSON.stringify({
    places, topics, label,
    tag_name: alertTagName(id),
    tag_id: tagId || "",
    created: isoDay(new Date()),
  }));
}

/**
 * Make sure `def:<id>` exists for a selection, creating the Buttondown tag the first time.
 * Returns the tag name, which is all the caller needs.
 *
 * `X-Buttondown-Collision-Behavior: overwrite` makes a second call to create the same tag an
 * update rather than a 409 — two readers submitting the same selection in the same minute is
 * the ordinary case here, not the exceptional one.
 *
 * **A 403 on `/tags` is expected enough to be survivable.** The API key screen grants scopes
 * per object and has none for tags, so the call may simply refuse. Buttondown's own contract
 * covers it: `SubscriberInput.tags` states that tags which do not exist are created, so the
 * subscribe call attaches the tag regardless. What is lost is the public description and the
 * tag id, not the tag — so the definition is written either way and the sign-up goes through.
 */
async function defineAlert(env, places, topics, vocab) {
  const id = await alertId(places, topics);
  const name = alertTagName(id);
  const held = await env.ALERTS.get(`def:${id}`, { type: "json" });
  if (held) { return name; }

  const label = alertLabel(places, topics, vocab);
  let tagId = "";
  try {
    const res = await bd(env, "/tags", {
      method: "POST",
      headers: { "X-Buttondown-Collision-Behavior": "overwrite" },
      body: { name, color: TAG_COLOUR, public_description: label, subscriber_editable: false },
    });
    if (res.ok) {
      const tag = await res.json();
      tagId = tag && tag.id ? String(tag.id) : "";
    }
  } catch (err) {
    tagId = "";                       // the subscribe call creates the tag by name regardless
  }
  await putDef(env, id, places, topics, label, tagId);
  return name;
}

// --------------------------------------------------------------------------- routes

async function feedRoute(request, env, url, ctx) {
  const cache = caches.default;
  const hit = await cache.match(request);
  if (hit) { return hit; }

  const vocab = await siteJson(env, "vocab.json", 900);
  const places = cleanCodes(url.searchParams.getAll("places"), vocab.places, MAX_PER_FACET);
  const topics = cleanCodes(url.searchParams.getAll("topics"), vocab.topics, MAX_PER_FACET);
  if (places === null || topics === null || (!places.length && !topics.length)) {
    return new Response("Give up to five places and up to five topics, from the catalogue's " +
                        "own codes, and at least one of the two.\n", { status: 400 });
  }

  const recent = await siteJson(env, "recent.json", 900);
  const def = { places, topics };
  const rows = (recent.items || []).filter((r) => matches(r, def)).sort(byNewest).slice(0, FEED_CAP);

  const selfUrl = `${site(env)}/api/alerts/feed?${url.searchParams.toString()}`;
  const body = atomFeed(rows, {
    title: alertLabel(places, topics, vocab),
    selfUrl,
    altUrl: catalogueUrl(def, site(env)),
    siteBase: site(env),
    built: recent.built || isoDay(new Date()),
  });
  const res = new Response(body, {
    headers: {
      "content-type": "application/atom+xml; charset=utf-8",
      "cache-control": "public, max-age=1800",
    },
  });
  ctx.waitUntil(cache.put(request, res.clone()));
  return res;
}

/**
 * Why Buttondown refused a call, as `<status>-<code>` — `400-rate_limited`, `403-`.
 *
 * **The code only, never the `detail`.** Buttondown's `code` is an enum
 * (`SubscriberInputValidationErrorCode`: `email_blocked`, `ip_address_spammy`, …) and names
 * no one; its `detail` is prose and may quote the address it refused. The code goes into the
 * redirect so a failed sign-up says why in the address bar, which is where D5's first
 * `?e=later` left nothing to go on (2026-09-16). Anything not shaped like an enum is dropped.
 */
async function refusal(res, withMessages) {
  let code = "";
  try {
    const body = await res.json();
    if (body && typeof body.code === "string" && /^[a-z_]{1,60}$/.test(body.code)) {
      code = body.code;
    } else if (body && Array.isArray(body.detail)) {
      // A 422 is a list of field errors rather than a code. The field path and error type
      // name a place in the request, never a value from it; the prose message may quote
      // the value, so it is included only where the caller says the request held nothing
      // personal — the email body, never a subscriber.
      code = body.detail.slice(0, 5).map((d) =>
        [(d.loc || []).join("."), d.type, withMessages ? d.msg : ""].filter(Boolean).join(":"))
        .join(" | ");
    }
  } catch (err) {
    code = "";
  }
  return `${res.status}-${code}`;
}

async function subscribeRoute(request, env) {
  const back = (q) => seeOther(`${site(env)}/alerts/${q}`);
  const form = await request.formData();

  if (!(await turnstileOk(request, env, form.get("cf-turnstile-response")))) {
    return back("?e=check");
  }

  const vocab = await siteJson(env, "vocab.json", 900);
  const places = cleanCodes(form.getAll("places"), vocab.places, MAX_PER_FACET);
  const topics = cleanCodes(form.getAll("topics"), vocab.topics, MAX_PER_FACET);
  const wantsSite = form.get("site") === "1";
  const email = (form.get("email") || "").toString().trim();

  if (places === null || topics === null || !looksLikeEmail(email) ||
      (!places.length && !topics.length && !wantsSite)) {
    return back("?e=input");
  }

  try {
    const tags = [];
    // Steps 3 and 4 of the design: a site-only sign-up defines no alert and calls no /tags.
    if (places.length || topics.length) {
      tags.push(await defineAlert(env, places, topics, vocab));
    }
    if (wantsSite) { tags.push(SITE_TAG); }

    const ip = request.headers.get("cf-connecting-ip") || "";
    const res = await bd(env, "/subscribers", {
      method: "POST",
      headers: { "X-Buttondown-Collision-Behavior": "add" },
      body: subscriberBody(email, tags, ip, `${site(env)}/alerts/`),
    });
    if (!res.ok) {
      // Buttondown's firewall (Settings → Firewall) turns a sign-up away with
      // `subscriber_blocked`. "Try again later" is the wrong advice for that — a retry is
      // what raises the risk score — so it gets a message of its own.
      const why = encodeURIComponent(await refusal(res));
      return back(`?e=${/-(subscriber_blocked|ip_address_spammy|email_blocked)$/.test(decodeURIComponent(why)) ? "blocked" : "later"}&why=${why}`);
    }
    // A reader who is already confirmed gets no confirmation email, so "check your inbox"
    // is wrong for them. Buttondown's reply says which they are; the address in the same
    // reply is not read.
    let type = "";
    try { type = String((await res.json()).type || ""); } catch (err) { type = ""; }
    return back(type === "regular" ? "?ok=added" : "?ok=1");
  } catch (err) {
    return back("?e=later");
  }
}

async function manageListRoute(request, env) {
  const body = await request.json();
  if (!(await turnstileOk(request, env, body["cf-turnstile-response"]))) {
    return json({ error: "check" }, 400);
  }
  const s = String(body.s || "");
  if (!SUBSCRIBER_ID.test(s)) { return json({ site: false, alerts: [] }); }

  const res = await bd(env, `/subscribers/${encodeURIComponent(s)}`);
  if (!res.ok) { return json({ site: false, alerts: [] }); }

  // The response carries the address. It is read for its tags and nothing else keeps it.
  const tags = alertTags((await res.json()).tags);
  const defs = {};
  for (const t of tags) {
    if (t === SITE_TAG) { continue; }
    const def = await env.ALERTS.get(`def:${t.slice("alert ".length)}`, { type: "json" });
    if (def) { defs[t] = def; }
  }
  return json(listResponse(tags, defs));
}

async function manageSaveRoute(request, env) {
  const body = await request.json();
  if (!(await turnstileOk(request, env, body["cf-turnstile-response"]))) {
    return json({ error: "check" }, 400);
  }
  const s = String(body.s || "");
  if (!SUBSCRIBER_ID.test(s)) { return json({ error: "input" }, 400); }

  const wanted = Array.isArray(body.alerts) ? body.alerts : [];
  if (wanted.length > MAX_ALERTS) { return json({ error: "input" }, 400); }

  const vocab = await siteJson(env, "vocab.json", 900);
  const clean = [];
  for (const a of wanted) {
    const places = cleanCodes(a && a.places, vocab.places, MAX_PER_FACET);
    const topics = cleanCodes(a && a.topics, vocab.topics, MAX_PER_FACET);
    if (places === null || topics === null) { return json({ error: "input" }, 400); }
    if (!places.length && !topics.length) { continue; }
    clean.push({ places, topics });
  }

  const res = await bd(env, `/subscribers/${encodeURIComponent(s)}`);
  if (!res.ok) { return json({ error: "input" }, 400); }
  const current = (await res.json()).tags || [];

  const tags = [];
  for (const a of clean) { tags.push(await defineAlert(env, a.places, a.topics, vocab)); }
  if (body.site) { tags.push(SITE_TAG); }

  const patch = await bd(env, `/subscribers/${encodeURIComponent(s)}`, {
    method: "PATCH",
    body: { tags: mergeTags(current, tags) },
  });
  if (!patch.ok) { return json({ error: "later" }, 502); }
  return json({ saved: clean.length, site: !!body.site });
}

// --------------------------------------------------------------------------- the cron

/**
 * Count, in one pass, how many subscribers hold each alert tag.
 *
 * `Subscriber.tags` is a list of tag **names**, so this needs no per-tag call. Buttondown
 * carries no subscriber count on a tag, and `/v1/tags/{id}/analytics` reports
 * `created_subscribers` — those created *with* the tag, not those holding it now — so one pass
 * is the only correct count as well as the cheapest.
 *
 * **It throws rather than returning a short count.** A rate limit that cut the paging short
 * would silently drop every reader on the pages that did not arrive, and they would never know
 * which week they missed; abandoning the run loses one Monday and `last_sent_through` catches
 * it up next week.
 */
async function tallyTags(env) {
  const tally = {};
  let url = "/subscribers?type=regular";
  let pages = 0;
  let retries = 0;
  while (url && pages < 200) {
    const res = await bd(env, url);
    if (res.status === 429) {
      // Bounded, and it gives up rather than waiting a run out: three tries and at most
      // a minute each. A loop that retried indefinitely would sit inside `waitUntil`
      // until Cloudflare killed it, which looks from the outside like a Monday that
      // simply did not happen.
      const wait = Number(res.headers.get("retry-after") ||
                          res.headers.get("x-ratelimit-reset") || 0);
      retries += 1;
      if (!wait || wait > 60 || retries > 3) { throw new Error("rate limited"); }
      await new Promise((r) => setTimeout(r, wait * 1000));
      continue;
    }
    if (!res.ok) { throw new Error(`subscribers ${res.status}`); }
    const page = await res.json();
    // Each subscriber's address is in this payload and is read for its tags alone.
    for (const sub of page.results || []) {
      for (const t of alertTags(sub.tags)) { tally[t] = (tally[t] || 0) + 1; }
    }
    // `next` is an absolute URL on Buttondown's own host. Anything else — a relative
    // path, a redirect somewhere new — ends the paging rather than being pasted onto
    // `API` and fetched, because a tally that followed a link off Buttondown is worse
    // than a tally that stopped.
    url = page.next && String(page.next).startsWith(API)
      ? String(page.next).slice(API.length) : "";
    pages += 1;
  }
  return tally;
}

/**
 * `{tag name: tag id}` for every tag on the newsletter, from `GET /v1/tags`.
 *
 * The audience filter needs ids and the body needs names (see the note at the top of the
 * file), and this is the only place both are held by Buttondown itself rather than by KV.
 */
async function tagIdsByName(env) {
  const ids = {};
  let url = "/tags?page_size=100";
  let pages = 0;
  while (url && pages < 50) {
    const res = await bd(env, url);
    if (!res.ok) { throw new Error(`tags ${await refusal(res)}`); }
    const page = await res.json();
    for (const t of page.results || []) {
      if (t && t.name && t.id) { ids[t.name] = String(t.id); }
    }
    url = page.next && String(page.next).startsWith(API)
      ? String(page.next).slice(API.length) : "";
    pages += 1;
  }
  return ids;
}

/** Every `def:` entry, keyed by tag name, for the tags this week's tally actually found. */
async function loadDefs(env, tally) {
  const defs = {};
  for (const name of Object.keys(tally)) {
    if (name === SITE_TAG || !ALERT_TAG.test(name)) { continue; }
    const def = await env.ALERTS.get(`def:${name.slice("alert ".length)}`, { type: "json" });
    if (def) { defs[name] = def; }
  }
  return defs;
}

/**
 * `cron_status` in KV: when the cron last ran, how far it got, and what stopped it.
 *
 * **The cron's errors used to go only to Cloudflare's logs**, which D9 showed are not where
 * anyone looks: the run left nothing in KV and nothing in Buttondown, and whether it had run
 * at all could not be told from either (2026-09-16). One key, overwritten each run, readable
 * on the KV pairs screen. It holds counts, stages and error codes — never an address, and
 * never a Buttondown `detail`.
 *
 * Two writes a run — one on starting, one on finishing — because KV's free tier allows a
 * thousand writes a day, and a schedule left at every five minutes for testing makes 288 runs.
 */
async function cronStatus(env, fields) {
  try {
    await env.ALERTS.put("cron_status", JSON.stringify(
      Object.assign({ at: new Date().toISOString() }, fields)));
  } catch (err) {
    // A status that cannot be written must not turn a successful run into a failed one.
  }
}

/** The cron, with its failure recorded in `cron_status` rather than only thrown. */
async function runCronRecorded(env) {
  try {
    await runCron(env);
  } catch (err) {
    await cronStatus(env, { stage: "failed", error: String((err && err.message) || err) });
  }
  return env.ALERTS.get("cron_status", { type: "json" });
}

/**
 * `POST /api/alerts/run` with `Authorization: Bearer <RUN_TOKEN>` — the Monday job, now.
 *
 * **Why it exists.** The dashboard offers no button to fire a cron, and on 2026-09-16 a
 * five-minute schedule left no trace at all, so D9 could not be run. This runs exactly what
 * the schedule runs, `sent:` guard included, and answers with `cron_status`.
 *
 * **Why it has a token.** In `draft` mode the worst a stranger could build is a draft — but a
 * run also moves `last_sent_through` forward, and a window moved on a Thursday is four days a
 * Monday reader never gets. With no `RUN_TOKEN` bound the route does not exist (404), so
 * removing the secret is how to switch it off.
 */
async function runRoute(request, env) {
  const want = String(env.RUN_TOKEN || "").trim();
  if (!want) { return new Response("Not found", { status: 404 }); }
  const got = (request.headers.get("authorization") || "").replace(/^Bearer\s+/i, "").trim();
  if (!sameString(got, want)) { return json({ error: "forbidden" }, 403); }
  return json(await runCronRecorded(env));
}

/** Compare without stopping at the first differing character. */
function sameString(a, b) {
  if (a.length !== b.length) { return false; }
  let diff = 0;
  for (let i = 0; i < a.length; i += 1) { diff |= a.charCodeAt(i) ^ b.charCodeAt(i); }
  return diff === 0;
}

async function runCron(env) {
  const today = isoDay(new Date());
  await cronStatus(env, { stage: "started" });
  const alreadySent = (await env.ALERTS.get(`sent:${today}`)) !== null;
  const plan = cronPlan({
    today,
    lastSentThrough: await env.ALERTS.get("last_sent_through"),
    alreadySent,
  });
  if (plan.skip) {
    if (plan.reason === "caught-up") { await env.ALERTS.put("last_sent_through", plan.to); }
    await cronStatus(env, { stage: "skipped", reason: plan.reason });
    return;
  }

  const [recent, feed, tally] = await Promise.all([
    siteJson(env, "recent.json", 300),
    fetch(`${mainSite(env)}/feed.json`, { cf: { cacheTtl: 300, cacheEverything: true } })
      .then((r) => (r.ok ? r.json() : { items: [] }))
      .catch(() => ({ items: [] })),
    tallyTags(env),
  ]);

  const defs = await loadDefs(env, tally);
  const tagIds = await tagIdsByName(env);
  const { sections, orphans, unresolved } = planDigest({
    tally, defs, tagIds,
    records: recent.items || [],
    mainPosts: feed.items || [],
    from: plan.from, to: plan.to,
    cap: ITEM_CAP,
    siteBase: site(env),
  });

  for (const name of orphans) {
    const key = `orphan:${name}`;
    if ((await env.ALERTS.get(key)) === null) { await env.ALERTS.put(key, today); }
  }

  if (unresolved.length) {
    throw new Error(`no Buttondown tag id for ${unresolved.join(", ")}`);
  }

  const counts = {
    from: plan.from, to: plan.to,
    records: (recent.items || []).length, posts: (feed.items || []).length,
    tags: Object.keys(tally).length, sections: sections.length, orphans: orphans.length,
  };
  if (!sections.length) {
    await env.ALERTS.put("last_sent_through", plan.to);
    await cronStatus(env, Object.assign({ stage: "nothing-matched" }, counts));
    return;
  }

  const body = renderDigest(sections, { siteBase: site(env) });
  const email = buildEmail(sections, { monday: today, body, sendMode: env.SEND_MODE });
  const res = await bd(env, "/emails", { method: "POST", body: email });
  if (!res.ok) { throw new Error(`emails ${await refusal(res, true)}`); }
  const made = await res.json();

  await env.ALERTS.put("last_sent_through", plan.to);
  await env.ALERTS.put(`sent:${today}`, made && made.id ? String(made.id) : "sent");
  await cronStatus(env, Object.assign({ stage: "email-created", mode: email.status }, counts));
}
