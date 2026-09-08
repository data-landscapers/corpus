/**
 * download-log — serves dated editions from R2, and records which ones readers take.
 *
 * `documentation/cloudflare.md` is the reference for the layer; `documentation/editions-serving-
 * shape.md` is why the serving half exists. The site is static on GitHub Pages, which gives no
 * access logs and a ~1 GB ceiling, and this Worker answers both: it notes the path of every
 * `.pdf`/`.csv` a reader takes, and it serves the dated editions themselves out of R2 so that
 * they stop counting against the ceiling.
 *
 * THE URL NEVER CHANGES. `design.md` §9 promises a dated URL resolves for ever; a file moving
 * from Pages to R2 is an origin change and must not be visible. Everything below preserves the
 * published path exactly — the R2 key IS the path under `site/`, which is also the KV key, so
 * one string addresses a file in all three places and nothing translates between schemes.
 *
 * IT LOGS NO READER. No IP address, no user-agent, no referrer, no session — the key is the
 * path of the file, the value is when it was taken and how often. The user-agent is read once,
 * in memory, to split readers from crawlers, and is not stored.
 *
 * WHAT CHANGED, AND WHAT IT COST. This Worker used to be entirely out of the serving path: it
 * fetched from origin and returned the response whatever happened in the logging, so a broken
 * Worker cost a log entry rather than a download. Serving from R2 gives that up for the
 * editions — once a file is only in R2, this Worker is the only way to it. Three things are
 * built to hold that:
 *
 *   1. R2 is tried, never required. A miss, a throw, or a missing binding falls through to the
 *      origin fetch. During the migration both copies exist and the fallback is a real one.
 *   2. Logging still cannot withhold a response. It runs in waitUntil, after the body is in
 *      hand, and its failure is swallowed.
 *   3. The deletion rule keeps its safe direction. An unrecorded download costs storage; it
 *      can never delete a file somebody is holding.
 *
 * Deployment and the bindings are in README.md beside this file.
 */

/** Only dated downloads are editions. HTML pages are the browsable surface and are not logged. */
const DOWNLOAD = /\.(pdf|csv)$/i;

/**
 * A dated edition: `…-YYYY-MM-DD.pdf` or `…-YYYY-MM-DD-2.csv`.
 *
 * This is `editions.py`'s grammar and must not drift from it — the report names carry a period
 * before the edition (`AGO-monthly-2026-07-2026-08-13.pdf`), so the anchor at the end is what
 * makes the last date the edition. Undated downloads (`raw-catalogue.csv`, §9's one deliberate
 * exception) do not match, are never looked for in R2, and stay on Pages.
 */
const EDITION = /-\d{4}-\d{2}-\d{2}(-\d+)?\.(pdf|csv)$/i;

/** Derived data that is fetched, never cited, and has no claim on the published origin. */
const R2_PREFIX = ["catalogue/names/", "catalogue/titles/"];

/**
 * The bulletin stays on GitHub Pages and is never looked for in R2.
 *
 * Its editions are deleted on a stated seven-day window rather than on downloads, so they never
 * accumulate — twenty files against 2,500 — and `prune-editions.py` rebuilds their manifest by
 * reading the directory off disk. Moving them would buy no headroom and would mean teaching that
 * rebuild to enumerate a bucket. Must match `r2-sync.py`'s STAYS.
 */
const STAYS = ["bulletin/"];

/**
 * Crawlers are flagged, not excluded.
 *
 * A bot triggering a "keep" is the safe direction of failure — it costs storage, where dropping
 * a real reader's download would eventually delete a file underneath a citation. So the count is
 * split rather than filtered, and whoever reads it later can decide what to believe.
 */
const CRAWLER = /bot|crawler|spider|slurp|curl|wget|headless|python-requests|scrapy|facebookexternalhit|preview|monitor|uptime/i;

/**
 * A dated edition is immutable by construction — §9 says a published file is never revised — so
 * it is safe to cache for a year at the edge and in the reader's browser. This is also what
 * keeps the R2 bill near zero: the second reader of a file is served by Cloudflare's cache and
 * never reaches the bucket.
 */
const IMMUTABLE = "public, max-age=31536000, immutable";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const key = url.pathname.replace(/^\/+/, "");

    // The response is obtained first, from R2 where the object is there and from the origin
    // otherwise. Nothing in the logging below can withhold it.
    const response = (await fromR2(request, env, key)) ?? fetch(request);

    try {
      ctx.waitUntil(record(request, env, key).catch(() => {}));
    } catch {
      // waitUntil itself is unavailable or threw: the download still goes through.
    }
    return response;
  },
};

/**
 * The object out of R2, or null to let the origin answer.
 *
 * **Null is always a safe answer and is the answer to everything unexpected** — no binding, a
 * path that is not an edition, a miss, or a throw from R2 itself. During the migration the file
 * is still on Pages and the reader cannot tell; after it, they get whatever Pages says, which is
 * a 404 that looks like every other 404 rather than a 500.
 */
async function fromR2(request, env, key) {
  if (!env.EDITIONS) return null;                              // not bound: Pages serves, as before
  if (request.method !== "GET" && request.method !== "HEAD") return null;
  if (!key || key.length > 1024) return null;
  if (STAYS.some((p) => key.startsWith(p))) return null;
  if (!EDITION.test(key) && !R2_PREFIX.some((p) => key.startsWith(p))) return null;

  try {
    // `onlyIf` hands R2 the conditional headers, so a reader with the file cached gets a 304
    // and no body is billed or transferred. `range` serves the byte ranges a PDF viewer asks
    // for when it opens a large file without downloading all of it.
    //
    // **`range` is passed only when the request actually carried one.** Handed the full header
    // set unconditionally, R2 resolves the absent Range to the whole object and reports it back
    // as a span — which read as "this was a range request" and turned every ordinary download
    // into a `206 Partial Content` covering the entire file. Legal by the letter, wrong in
    // practice, and the sort of thing a download manager and a cache each mishandle differently.
    const wantsRange = request.headers.has("range");
    const object = await env.EDITIONS.get(key, {
      onlyIf: request.headers,
      ...(wantsRange ? { range: request.headers } : {}),
    });
    if (object === null) return null;                          // not in the bucket: origin answers

    const headers = new Headers();
    object.writeHttpMetadata(headers);                         // content-type recorded at upload
    headers.set("etag", object.httpEtag);
    headers.set("cache-control", IMMUTABLE);
    headers.set("accept-ranges", "bytes");

    // R2 returns an object with no body when `onlyIf` did not match — that is a 304, and it is
    // the only way to tell one from a HEAD, which also wants no body but means 200.
    const conditional = request.headers.has("if-none-match") ||
                        request.headers.has("if-modified-since");
    if (!("body" in object) || object.body === null) {
      return new Response(null, { status: conditional ? 304 : 200, headers });
    }
    if (request.method === "HEAD") {
      headers.set("content-length", String(object.size));
      return new Response(null, { status: 200, headers });
    }

    // A range request R2 satisfied carries the resolved span and must be answered 206. The
    // suffix form (`bytes=-500`) resolves to an offset here too, but defensively: anything this
    // cannot express as a span is returned whole, which is a slower correct answer.
    //
    // **`content-length` is left to the runtime on anything carrying a body.** It computes one
    // from the stream, and a header that disagreed with the bytes actually sent is a truncated
    // download rather than an error anybody would see.
    const span = wantsRange ? object.range : null;
    if (span && typeof span.offset === "number" && typeof span.length === "number") {
      const end = span.offset + span.length - 1;
      headers.set("content-range", `bytes ${span.offset}-${end}/${object.size}`);
      return new Response(object.body, { status: 206, headers });
    }
    return new Response(object.body, { status: 200, headers });
  } catch {
    return null;                                               // R2 unwell: the origin still has it
  }
}

async function record(request, env, key) {
  if (request.method !== "GET") return;              // HEAD is a probe, not a download
  if (!env.DOWNLOADS) return;                        // no binding: log nothing, break nothing
  if (!DOWNLOAD.test(key)) return;

  // The key is the path as published, without its leading slash — `reports/KEN/KEN-status-
  // 2026-08-18.pdf`. That is exactly the path under `site/` and exactly the R2 key, so the
  // pruner can match a KV key against a bucket object and a file on disk with no translation.
  // **Stored exactly as it arrives, still percent-encoded if it arrived that way**, because the
  // record already holds keys written that way and `prune-editions.py` unquotes on the way in;
  // normalising here would put two spellings of one path in one namespace.
  const logged = key;
  if (!logged || logged.length > 400) return;        // KV key ceiling is 512 bytes

  const today = new Date().toISOString().slice(0, 10);
  const crawler = CRAWLER.test(request.headers.get("user-agent") || "");

  const held = await env.DOWNLOADS.get(logged, { type: "json" });
  const seen = held && typeof held === "object" ? held : null;

  await env.DOWNLOADS.put(logged, JSON.stringify({
    first: seen?.first ?? today,
    last: today,
    n: (seen?.n ?? 0) + (crawler ? 0 : 1),
    bots: (seen?.bots ?? 0) + (crawler ? 1 : 0),
  }));
}
