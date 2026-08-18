---
type: runbook
title: Move both sites to .io, behind Cloudflare
last_reviewed: 2026-08-18
status: not yet run
---

# Move both sites to .io, behind Cloudflare

*(Written 2026-08-18. `data-landscapers.com → data-landscapers.io` and `corpus.data-landscapers.com → corpus.data-landscapers.io`. Both are GitHub Pages sites in the `data-landscapers` organisation, so they move together. Work down the numbered steps; the reasoning is underneath and you do not need it to follow them.)*

## Before you click anything

- **Keep the `.com` registered for ever.** Set it to auto-renew today. Everything already published points at it.
- **Allow two sittings, not one.** Steps 1–18 are waiting-for-DNS and change nothing for readers. Steps 19–41 are the actual switch and want an uninterrupted hour.
- **Step 24 is mine.** Tell me when you reach it and I will do it while you wait.

---

# The steps

## Part 1 — the Cloudflare account

**1.** Go to `dash.cloudflare.com/sign-up` and create an account with an email address you will keep long-term.

**2.** Click your profile icon (top right) → *My Profile* → *Authentication* → turn on **Two-Factor Authentication**.

## Part 2 — put the `.com` into Cloudflare (nothing changes for readers)

**3.** On the Cloudflare home screen click **Add a site**. Type `data-landscapers.com`. Continue.

**4.** Choose the **Free** plan. Continue.

**5.** Cloudflare shows a list of DNS records it found. **Stop and open your registrar's DNS page in another tab.** Compare the two lists line by line.

**6.** Add by hand anything Cloudflare missed, and expect it to have missed something. **Cloudflare's scan guesses common subdomain names; it does not know yours.** `corpus` is not a name it guesses, and when this was run on 2026-08-18 that record was not imported — so `corpus.data-landscapers.com` stopped resolving the moment the nameservers changed at step 9. **Look especially for `MX` records and any `TXT` records**, which are email: a missing one stops your mail and fails silently.

**7.** Go down the list and make sure **every record says "DNS only"** with a **grey** cloud. Click any orange cloud to turn it grey.

**8.** Continue. Cloudflare shows you **two nameservers** (like `alice.ns.cloudflare.com`). Copy them somewhere.

**9.** Go to the registrar where `data-landscapers.com` is registered. Find **Nameservers**. **Write down the current ones first.** Then replace them with Cloudflare's two. Save.

**10.** Wait. Cloudflare emails you when the domain shows **Active** — usually under an hour, sometimes up to 24.

> **CHECK 11.** Load **both** websites — `data-landscapers.com` **and `corpus.data-landscapers.com`**, by name, not from a bookmark that might be cached. Send yourself an email at the domain. Everything should work exactly as before. If anything is broken, the record for it was missed at step 6: add it, or put the old nameservers back at the registrar and start Part 2 again.

## Part 3 — put the `.io` into Cloudflare

**12.** Cloudflare → **Add a site** → `data-landscapers.io` → **Free** plan.

**13.** Cloudflare shows any records it found. A freshly registered domain usually carries **parking records** put there by the registrar — an `A` record on `@` pointing somewhere that is not GitHub, often proxied. Note what is there; step 17 deletes them.

**14.** Copy the **two nameservers** it gives you. They may be different from the `.com` pair — use these ones.

**15.** At the registrar for `data-landscapers.io`, replace the nameservers with those two. Save.

**16.** !!! Wait for the zone to show **Active**.

**17.** In the `.io` zone go to **DNS → Records**.

**First delete every existing `A`, `AAAA` or `CNAME` record on `@`, `www` or `corpus`.** These are the registrar's parking records and none of them points at GitHub — the only addresses that serve GitHub Pages are the four below. Left in place they sit alongside the real ones, and DNS hands the whole set out in rotation, so a share of visitors lands on a parking page instead of the site, intermittently. **Keep any `MX` or `TXT` records** if you use email on the `.io`.

**Then add these six, one at a time. Every one with the cloud grey (DNS only).**

| Type  | Name     | Content                      | Proxy    |
| ----- | -------- | ---------------------------- | -------- |
| A     | `@`      | `185.199.108.153`            | DNS only |
| A     | `@`      | `185.199.109.153`            | DNS only |
| A     | `@`      | `185.199.110.153`            | DNS only |
| A     | `@`      | `185.199.111.153`            | DNS only |
| CNAME | `www`    | `data-landscapers.github.io` | DNS only |
| CNAME | `corpus` | `data-landscapers.github.io` | DNS only |

> **CHECK 18.** Exactly six `A`/`CNAME` records are listed, they are the six above, and all six clouds are **grey**. A leftover seventh is the thing to look for. If any is orange, the certificate in Part 5 will never appear.

## Part 4 — tell GitHub the domains are yours

**19.** Go to `github.com` → your **data-landscapers** organisation → **Settings** → **Pages** → **Add a domain**.

**20.** Type `data-landscapers.io` → Continue. GitHub shows you a `TXT` record — a name and a value.

**21.** In Cloudflare, `.io` zone → **DNS → Add record** → type **TXT** → paste the name and the value → Save.

**22.** Back in GitHub, click **Verify**. Wait for the tick. If it fails, wait five minutes and try again.

**23.** Do steps 19–22 again for `corpus.data-landscapers.io`.

## Part 5 — move the corpus site *(the switch begins here)*

**24. Tell me you are at step 24.** I change the domain in the repo, re-render every page and PDF, and push. A few minutes. Wait for me to say it is done before step 25.

**25.** GitHub → `data-landscapers/corpus` → **Settings** → **Pages**. The **Custom domain** box should already say `corpus.data-landscapers.io`. If it does not, type it and press **Save**.

**26.** Wait for **"DNS check successful"**, and then for the **Enforce HTTPS** tickbox to stop being greyed out. Minutes usually; up to an hour.

**27.** Tick **Enforce HTTPS**.

> **CHECK 28.** Open `https://corpus.data-landscapers.io/` — it should load with a padlock and no warning. Open a country page. Download a PDF.

## Part 6 — make the old corpus address forward *(do this straight after step 28)*

**29.** Cloudflare → **`data-landscapers.com`** zone → **DNS → Records**. Find the record named `corpus` and **edit** it to the values below — or, if there is no such record because the step 5 scan never imported it, **create** it with those values. Either way you end up with exactly this and nothing else on that name:

| Type | Name     | Content | Proxy                |
| ---- | -------- | ------- | -------------------- |
| AAAA | `corpus` | `100::` | **Proxied (orange)** |

**30.** Same zone → **Rules → Redirect Rules → Create rule**. Name it `corpus com to io`. Fill it in like this:

- **When incoming requests match**: Field `Hostname` · Operator `equals` · Value `corpus.data-landscapers.com`
- **Then**: *URL redirect* → Type **Dynamic**
- **Expression** — paste exactly: `concat("https://corpus.data-landscapers.io", http.request.uri.path)`
- **Status code**: `301`
- **Preserve query string**: **on**
- Save and deploy.

> **CHECK 31.** Paste an old deep link into a browser — for example `https://corpus.data-landscapers.com/reports/KEN/KEN-status.html`. It must land on the **same page** on `.io`, not on the front page.

## Part 7 — move the main site

**32.** Whoever maintains the main site's repo changes its `CNAME` file to `data-landscapers.io` and pushes. One line.

**33.** In that repo: **Settings → Pages**, confirm the custom domain reads `data-landscapers.io`, wait for the certificate, tick **Enforce HTTPS**. (Same as steps 25–27.)

> **CHECK 34.** `https://data-landscapers.io/` loads with a padlock.

**35.** Cloudflare → `.com` zone → **DNS**. Delete the four `A` records on `@`. Add instead: **AAAA · `@` · `100::` · Proxied (orange)**. Change the `www` record to **AAAA · `www` · `100::` · Proxied (orange)** as well.

**36.** **Rules → Redirect Rules → Create rule**, named `main com to io`:

- **When**: Field `Hostname` · Operator `is in` · Value `data-landscapers.com` and `www.data-landscapers.com`
- **Then**: Dynamic → `concat("https://data-landscapers.io", http.request.uri.path)` → `301` → preserve query string **on**

> **CHECK 37.** An old article link such as `https://data-landscapers.com/2026/06/16/sovereignty-dividing-line/` lands on the same article on `.io`.

## Part 8 — turn Cloudflare on properly

**38.** Cloudflare → **`.io`** zone → **DNS**. Switch the apex, `www` and `corpus` records to **Proxied (orange)**.

**39.** **SSL/TLS → Overview** → set to **Full (strict)**. **Do not choose Flexible.**

**40.** **SSL/TLS → Edge Certificates** → turn **Always Use HTTPS** on.

> **CHECK 41.** Both sites load. A PDF downloads. A CSV downloads. An old `.com` link still forwards.

**Done.** The download log — the Worker in `documentation/delete-unless-downloaded.md` — is a separate job for another day. It needs step 38 to have been done and nothing else from here.

---

# Why it is in this order

**Nameservers first, because they are the slow part and nothing depends on them.** Parts 2 and 3 are invisible to readers: the same servers go on serving the same files, with Cloudflare merely answering the question of where they live. That gets the waiting out of the way while everything still works.

**Grey cloud until the certificate exists (steps 17, 18, 38).** GitHub issues a TLS certificate for each new hostname, and to do it must see that hostname resolving to GitHub's own servers. With the proxy on it sees Cloudflare instead, the certificate never issues, and the site serves security warnings while you try to work out why. This is the single most common way this pairing goes wrong.

**Full (strict), never Flexible (step 39).** Flexible tells Cloudflare to talk to the origin over plain HTTP. GitHub answers by redirecting to HTTPS, which arrives back at Cloudflare, which strips it again — an endless loop, and the second most common way this goes wrong.

**The old address has to forward from Cloudflare, not from GitHub, and Part 6 has to happen straight after Part 5.** A GitHub Pages repo has exactly **one** custom domain. The moment the corpus repo is set to `.io`, GitHub stops answering for the `.com` — so the gap between step 27 and step 30 is the only time anything is dark, and it should be minutes.

**`100::` is a placeholder that goes nowhere.** A redirect rule runs at Cloudflare's edge before any origin is contacted, but a **proxied** record must exist for the request to reach the edge at all. `100::` is the IPv6 discard address; nothing is behind it, which is the point.

**The redirect must carry the path (steps 30, 36).** A redirect that drops every visitor on the front page is worse than none for our purposes — the whole objective is that `…/KEN-status-2026-08-06.pdf` still reaches that exact file. That is what `concat(…, http.request.uri.path)` does, and why the check uses a deep link.

**Domain verification (Part 4) takes five minutes and closes a real hole.** A verified domain cannot be claimed by anyone else's GitHub repo — which matters most in exactly the situation Part 6 creates, where a hostname of yours stops pointing at a site of yours.

**Confirm GitHub's four addresses before typing them (step 17).** GitHub's own page — *Pages → Configuring a custom domain → apex domain* — is the authority. They have been stable for years, but they are GitHub's to change and this file is not the record of them.

**Both `CNAME`s point at `data-landscapers.github.io` even though they serve different repos.** GitHub routes on the hostname the browser asked for, and the repo that claims a hostname is whichever one has it set as its custom domain. That is also why two repos cannot claim the same one.

**Caching needs a thought and probably no action.** Cloudflare caches PDFs and CSVs at its edge by default and does not cache HTML unless told to — which suits us exactly, since the dated files never change and the pages do. If a page ever looks stale after a render, *Caching → Purge Everything* fixes it.

---

# Two decisions this rests on

**The `.com` stays registered indefinitely.** 1,053 published PDFs carry absolute `corpus.data-landscapers.com` URLs printed inside them, 401 published pages link to it, 11 catalogue records cite `data-landscapers.com` article URLs, and §9 promises that a dated URL resolves for ever. The redirects in Parts 6 and 7 are what keep every one of those alive, and there is no date at which it becomes safe to remove them. Letting the registration lapse is the only step in this runbook with no undo.

**`.io` carries a sovereignty question, and this project's central promise is permanence.** `.io` is the country-code domain for the British Indian Ocean Territory, and the UK agreed in 2024 to transfer sovereignty of the Chagos Archipelago to Mauritius. When a country code leaves the ISO 3166-1 list, ICANN's usual course is eventual retirement of the matching domain, over a long transition. Nothing has been announced for `.io` and the registry has signalled continuity — so this is worth checking the current position on before the switch rather than after, not a reason to stop. If it ever did move, the discipline in Part 6 is exactly what would carry the site again.

---

# If something goes wrong

**In Parts 2 or 3** — put the old nameservers back at the registrar. Everything returns to how it was.

**In Part 5** — tell me, and I will put the repo back to the `.com` and push. The `.com` records still point at GitHub at that moment, so the old site comes straight back.

**In Part 8** — turn the clouds grey again. That takes Cloudflare out of the serving path entirely and leaves plain GitHub Pages, which is where we are today.

---

# What still carries the old domain afterwards

**The 1,053 PDFs already published**, inside their own text. They go on working through the redirect and cannot be corrected, because a retained edition is not revised after publication (§9). Every new edition carries `.io` from step 24.

**11 catalogue records** cite `data-landscapers.com` article URLs. They will redirect and go on resolving. They live in OSINT's source base rather than here, so correcting them is a note for an OSINT session — worth raising once the move has settled, not before.

**Every page fetches its favicon from the main site**, so it follows the constant I change at step 24 and needs the main site's `.io` to be live before it resolves. A missing favicon between step 24 and step 33 is cosmetic and self-corrects.
