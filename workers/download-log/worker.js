/**
 * download-log — records which dated editions readers actually take.
 *
 * documentation/cloudflare.md. The site is static on GitHub Pages, which gives
 * no access logs, so something has to sit between the click and the bytes. This is that
 * something, and it is deliberately almost nothing: it sees a request for a .pdf or .csv,
 * notes the filename, and passes the request through untouched.
 *
 * IT DOES NOT SERVE THE FILE. The response is fetched and returned whatever happens here, so
 * a broken logger costs a missing log entry rather than a broken download. That is the whole
 * reason this shape was chosen over a gateway that mints on demand, and it is why a deletion
 * rule can eventually be hung off it: the record can only ever be incomplete, never wrong in
 * the direction that loses a file someone is holding.
 *
 * IT LOGS NO READER. No IP address, no user-agent, no referrer, no session — the key is the
 * path of the file and the value is when it was taken and how often. A project that publishes
 * on data governance should be able to describe its own logging in one sentence, and this is
 * that sentence.
 *
 * Deployment and the KV binding are in README.md beside this file.
 */

/** Only dated downloads are editions. HTML pages are the browsable surface and are not logged. */
const DOWNLOAD = /\.(pdf|csv)$/i;

/**
 * Crawlers are flagged, not excluded.
 *
 * A bot triggering a "keep" is the safe direction of failure — it costs storage, where dropping
 * a real reader's download would eventually delete a file underneath a citation. So the count is
 * split rather than filtered, and whoever reads it later can decide what to believe. Matching on
 * the user-agent is the one place it is read, and it is not stored.
 */
const CRAWLER = /bot|crawler|spider|slurp|curl|wget|headless|python-requests|scrapy|facebookexternalhit|preview|monitor|uptime/i;

export default {
  async fetch(request, env, ctx) {
    // The response is obtained first and returned unconditionally. Nothing below can withhold it.
    const response = fetch(request);
    try {
      ctx.waitUntil(record(request, env).catch(() => {}));
    } catch {
      // waitUntil itself is unavailable or threw: the download still goes through.
    }
    return response;
  },
};

async function record(request, env) {
  if (request.method !== "GET") return;              // HEAD is a probe, not a download
  if (!env.DOWNLOADS) return;                        // no binding: log nothing, break nothing

  const url = new URL(request.url);
  if (!DOWNLOAD.test(url.pathname)) return;

  // The key is the path as published, without its leading slash — `reports/KEN/KEN-status-
  // 2026-08-18.pdf`. That is exactly the path under `site/`, so whatever reads this later can
  // match a key against a file on disk without translating between two naming schemes.
  const key = url.pathname.replace(/^\/+/, "");
  if (!key || key.length > 400) return;              // KV key ceiling is 512 bytes

  const today = new Date().toISOString().slice(0, 10);
  const crawler = CRAWLER.test(request.headers.get("user-agent") || "");

  const held = await env.DOWNLOADS.get(key, { type: "json" });
  const seen = held && typeof held === "object" ? held : null;

  await env.DOWNLOADS.put(key, JSON.stringify({
    first: seen?.first ?? today,
    last: today,
    n: (seen?.n ?? 0) + (crawler ? 0 : 1),
    bots: (seen?.bots ?? 0) + (crawler ? 1 : 0),
  }));
}
