---
type: runbook
title: Move both sites to .io, behind Cloudflare
last_reviewed: 2026-08-18
status: not yet run
---

# Move both sites to .io, behind Cloudflare

*(Written 2026-08-18 for Bill to work through. Two sites move together: **data-landscapers.com → data-landscapers.io** and **corpus.data-landscapers.com → corpus.data-landscapers.io**. Both are GitHub Pages sites in the `data-landscapers` organisation. Cloudflare goes in at the same time, because the redirect that keeps the old URLs alive has to run there and because the download log later needs it. One line per paragraph.)*

*(**Steps marked CC are mine** — the repo constants and the re-render. Everything else is registrar, Cloudflare and GitHub, which only Bill can do. The two have to be timed together at Stage D, and that is the only moment in this runbook where anything is briefly dark.)*

## Three things to know before starting

**The `.com` has to stay registered and keep answering.** It is not optional and it is not sentiment: 1,053 published PDFs carry absolute `corpus.data-landscapers.com` URLs printed inside them, 401 published pages link to it, 11 records in the catalogue cite `data-landscapers.com` article URLs, and §9 promises that a dated URL resolves for ever. Letting the `.com` lapse breaks all of that at once and there is no way to repair it afterwards. Budget for renewing it indefinitely — Stage F turns it into a permanent redirect, which costs nothing but the registration.

**`.io` has a sovereignty question attached to it, and this project is built on permanent URLs.** `.io` is the country-code domain for the British Indian Ocean Territory, and the UK agreed in 2024 to transfer sovereignty of the Chagos Archipelago to Mauritius. When a country code leaves the ISO 3166-1 list, ICANN's normal course is eventual retirement of the matching ccTLD, over a long transition. Nothing has been announced for `.io` and the registry has signalled continuity, so this is a risk to check rather than a reason to stop — but a project whose central promise is *this link still works in 2029* should make the choice knowing it, and should check the current position before the switch rather than after. If it ever does move, the discipline in Stage F is exactly the discipline that would carry the site again.

**A GitHub Pages repo has exactly one custom domain.** So the `.com` cannot go on being served by GitHub once the repo is set to the `.io` — the moment you change it, the old hostname stops being answered. That is why the redirect must be ready to go in the same sitting, and why it comes from Cloudflare rather than from GitHub.

## The order, and why it is this order

Nameserver changes are the slow part and the least reversible-feeling, so they go first while nothing depends on them. The cutovers go last, and each is small enough to undo.

| Stage | What | Anything visible to a reader? |
|---|---|---|
| A | Cloudflare account, `.com` zone imported as-is | No |
| B | `.io` zone, DNS records, proxy **off** | No |
| C | Verify both domains in the GitHub org | No |
| D | Cut both repos over to `.io` **(CC + Bill together)** | Yes — the switch |
| E | `.com` becomes a permanent redirect | Yes — old links start forwarding |
| F | Turn the Cloudflare proxy on | No, if done right |
| G | Later: the download log Worker | No |

---

## Stage A — Cloudflare account, and the `.com` moved into it

**A1.** Create the account at `dash.cloudflare.com/sign-up`. Use an address you will keep; this becomes the control point for both domains. Turn on two-factor authentication straight away — this account can now redirect your entire web presence, which makes it worth more to an attacker than the sites are.

**A2.** *Add a site* → `data-landscapers.com` → choose the **Free** plan.

**A3.** Cloudflare scans the existing DNS and shows you what it found. **Check that list against your registrar's current records before continuing** — the scan is good but not guaranteed complete, and anything it misses simply stops working when the nameservers change. Pay particular attention to **MX records and any TXT records for mail** (SPF, DKIM, DMARC). If email runs on this domain, a missed MX record means mail stops, and that is the single most common way this goes wrong.

**A4.** Set every record's proxy status to **DNS only (grey cloud)** for now, including the ones Cloudflare turns orange by default. Nothing about how the sites are served should change at this stage.

**A5.** Cloudflare gives you two nameservers. At your registrar for `data-landscapers.com`, replace the existing nameservers with those two. Keep a note of what they were.

**A6.** Wait for Cloudflare to mark the zone **Active** — usually under an hour, occasionally up to 24. Then load both sites and send yourself a test email. Nothing should have changed. If something has, revert the nameservers at the registrar; that undoes the whole stage.

## Stage B — the `.io` zone and its records

**B1.** *Add a site* → `data-landscapers.io` → Free plan. Repeat A5 and A6 at the registrar for the `.io`, and wait for **Active**.

**B2.** Add these records. **Every one grey-clouded (DNS only)** — this matters and Stage F is where they change.

| Type | Name | Value | Proxy |
|---|---|---|---|
| A | `@` | `185.199.108.153` | DNS only |
| A | `@` | `185.199.109.153` | DNS only |
| A | `@` | `185.199.110.153` | DNS only |
| A | `@` | `185.199.111.153` | DNS only |
| CNAME | `www` | `data-landscapers.github.io` | DNS only |
| CNAME | `corpus` | `data-landscapers.github.io` | DNS only |

**Confirm those four addresses against GitHub's own page** — *Pages → Configuring a custom domain → apex domain* — before typing them. They have been stable for years, but they are GitHub's to change and this runbook is not the authority on them.

**Both CNAMEs point at `data-landscapers.github.io`, which is correct even though they serve different repos.** GitHub routes on the hostname the browser asked for, not on the address, and the repo that claims the hostname is whichever one has it set as its custom domain. That is also why two repos cannot claim the same hostname.

**B3.** The grey cloud is not a preference. GitHub has to issue a TLS certificate for each new hostname, and to do that it must see the name resolve to GitHub's own servers. With the proxy on, it sees Cloudflare instead, the certificate never issues, and the site serves warnings until you work out why. Grey now, orange at Stage F, in that order.

## Stage C — verify both domains in the GitHub organisation

**C1.** GitHub → your `data-landscapers` organisation → *Settings* → *Pages* → *Add a domain*. Do it for `data-landscapers.io` and again for `corpus.data-landscapers.io`.

**C2.** GitHub gives a TXT record for each — name like `_github-pages-challenge-data-landscapers`, with a token as the value. Add them in the Cloudflare `.io` zone and click *Verify*.

**This is worth the five minutes.** A verified domain cannot be claimed by anyone else's GitHub repo, which closes the takeover route where somebody else points their Pages site at a hostname of yours that has been left dangling. It matters most for exactly the situation Stage E creates.

## Stage D — the cutover

**This is the only stage with a dark window**, and it lasts from the moment a repo's custom domain changes until Stage E's redirect is in place for that hostname. Do D and E for one site, check it, then do the other. Half an hour, not a day.

**D1 (CC).** I change `site/CNAME` to `corpus.data-landscapers.io` and the `SITE_BASE` and `MAIN_SITE` constants in the six scripts that carry them — `render.py`, `country.py`, `home.py`, `catalogue.py`, `finance.py`, `topic-page.py`. Both constants are in every one of them and the domain appears nowhere else in the code.

**The `CNAME` file *is* the setting, for this repo.** The deploy workflow uploads `site/` wholesale, so whatever `site/CNAME` says overwrites the custom domain in Settings on the next deploy. Changing one without the other means they fight, and the file wins. So the file changes first and the Settings box will already show the new value when you look.

**D2 (CC).** I re-render with `--force` and push. Forcing is deliberate here: the domain is printed in every page and inside every PDF, so without it a document would go on naming the old domain until its content happened to move. It cuts a new edition of all 241 documents, about 70 MB. The editions already published keep the old domain and go on working through Stage E's redirect, which is the point of that stage.

**D3 (Bill).** GitHub → `corpus` repo → *Settings* → *Pages*. The custom domain should already read `corpus.data-landscapers.io` from the deploy. If it does not, type it and save.

**D4 (Bill).** Wait for *"DNS check successful"* and for the certificate — minutes usually, up to an hour. **Then** tick **Enforce HTTPS**. It stays greyed out until the certificate exists, which is the signal you are waiting for.

**D5 (Bill).** Load `https://corpus.data-landscapers.io/` and a PDF. Both should work with a valid certificate and no warning.

**D6.** Then Stage E for `corpus.data-landscapers.com`, immediately.

**D7.** Then repeat D3–D6 for the main site repo and `data-landscapers.io`. That repo's `CNAME` file is its own — I do not touch it, and whoever maintains it needs the same one-line change.

## Stage E — the `.com` becomes a permanent redirect

**E1.** In the Cloudflare **`.com`** zone, replace the record for the hostname you have just moved with a placeholder that exists only to be proxied:

| Type | Name | Value | Proxy |
|---|---|---|---|
| AAAA | `corpus` | `100::` | **Proxied (orange)** |

**`100::` is the IPv6 discard address and nothing is behind it.** A redirect rule runs at Cloudflare's edge before any origin is contacted, but a proxied record has to exist for the request to reach the edge at all. This is Cloudflare's own documented pattern for a domain that redirects and hosts nothing.

**E2.** *Rules* → *Redirect Rules* → *Create rule*.

- **When**: `Hostname` equals `corpus.data-landscapers.com`
- **Then**: Dynamic redirect, expression `concat("https://corpus.data-landscapers.io", http.request.uri.path)`
- **Status**: `301` (permanent)
- **Preserve query string**: on

**The path has to be carried across.** A redirect that lands every visitor on the front page is worse than no redirect for our purposes: the whole point is that `…/reports/KEN/KEN-status-2026-08-06.pdf` still reaches that exact PDF. Test with a deep link, not the home page.

**E3.** Repeat for the apex: hostname `data-landscapers.com` → `https://data-landscapers.io` + path, and the same for `www.data-landscapers.com`. The apex needs its own placeholder record (`AAAA @ 100::`, proxied) once the A records to GitHub are removed.

**E4.** Check a deep link, an old PDF URL, and the home page of each site. `301` in the browser's network panel, landing on the right `.io` page.

**Leave these rules in place for ever.** They are the thing keeping every citation made before today alive, and there is no date at which it becomes safe to remove them.

## Stage F — turn the proxy on for `.io`

**F1.** Only once Stage D has a working certificate on both hostnames. In the `.io` zone, switch the apex, `www` and `corpus` records to **Proxied (orange)**.

**F2.** *SSL/TLS* → *Overview* → set the mode to **Full (strict)**. **Not Flexible** — Flexible plus GitHub's own HTTPS redirect produces an endless redirect loop, and it is the classic way this pairing breaks.

**F3.** *SSL/TLS* → *Edge Certificates* → **Always Use HTTPS** on. Leave GitHub's *Enforce HTTPS* on as well; they are two different legs of the journey.

**F4.** Check both sites again, and one PDF, and one CSV.

**Caching is worth one thought and probably no action.** Cloudflare caches static files such as PDFs and CSVs at its edge by default, and does not cache HTML unless told to. That happens to suit us exactly: the dated files are immutable, so caching them is free speed, and the pages that change on every render are not cached. If a page ever looks stale after a render, *Caching → Purge Everything* fixes it, and it would be reasonable to add that as a last step of RENDER later.

## Stage G — later, the download log

Not part of this move. The Worker described in `documentation/delete-unless-downloaded.md` needs the proxy from Stage F to be on, and nothing else from this runbook. Do the move, let it settle for a week, then take that up separately.

## If something goes wrong

**During A or B**, revert the nameservers at the registrar. Everything returns to how it was, at DNS propagation speed.

**During D**, set the repo's custom domain and `site/CNAME` back to the `.com` and push. The `.com` records in Cloudflare are still pointing at GitHub at that moment, so the old site comes straight back.

**During F**, grey-cloud the records again. That takes Cloudflare out of the serving path entirely and leaves plain GitHub Pages, which is where we are today.

**The one thing with no undo is letting the `.com` registration lapse.** Everything else here is a setting.

## What still carries the old domain afterwards

**The 1,053 PDFs already published**, inside their own text. They keep working through Stage E and cannot be corrected, because a retained edition is not revised after publication (§9). New editions carry `.io` from Stage D.

**11 catalogue records** cite `data-landscapers.com` article URLs. They will redirect and go on resolving. They live in OSINT's source base rather than here, so correcting them is a note for an OSINT session rather than something to do in this runbook — worth raising once the move is done and settled, not before.

**Every page fetches its favicon from the main site** (`{MAIN_SITE}/assets/favicon.svg`), so that follows the constant I change at D1 and needs the main site's `.io` to be serving before it resolves. A missing favicon is cosmetic and self-corrects; it is only listed here so it is not a surprise.
