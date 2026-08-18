---
type: runbook
title: Move both sites to .io, behind Cloudflare
last_reviewed: 2026-08-18
status: run 2026-08-18, complete and verified
---

# Move both sites to .io, behind Cloudflare

*(Written 2026-08-18. `data-landscapers.com → data-landscapers.io` and `corpus.data-landscapers.com → corpus.data-landscapers.io`. Both are GitHub Pages sites in the `data-landscapers` organisation, so they move together. Work down the numbered steps; the reasoning is underneath and you do not need it to follow them.)*

*(**Run on 2026-08-18 and completed the same afternoon.** Both sites serve on `.io`, every old `.com` URL redirects with its path intact, and a citation made the day before the move was followed end to end to the byte. The steps below were corrected nine times *during* the run and each correction is dated in place, so what follows is what actually happened rather than what was expected — see **What the run taught** at the end.)*

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

**If the tick is rejected and springs back, it is not broken and it is not blocking** *(seen on 2026-08-18 at step 33)*. The box ungreys as soon as GitHub is satisfied with DNS, which is slightly before the backend will accept the setting. Hard-refresh the page and try again in fifteen minutes; if it still springs back, clear the custom domain, Save, wait half a minute, retype it and Save, which re-runs provisioning and makes the tick hold. **Do not delete the `CNAME` file to force it** — the next deploy puts it straight back. Carry on with the runbook meanwhile: step 40 turns on Cloudflare's *Always Use HTTPS*, which forces every visitor onto HTTPS anyway, and step 39 encrypts the Cloudflare-to-GitHub leg. Check the certificate exists rather than trusting the tick: `curl -sS -o NUL -D - https://<hostname>/` answering `200` with no certificate complaint is the thing that matters.

> **CHECK 28.** Open `https://corpus.data-landscapers.io/` — it should load with a padlock and no warning. Open a country page. Download a PDF.

## Part 6 — make the old corpus address forward *(do this straight after step 28)*

**29.** Cloudflare → **`data-landscapers.com`** zone → **DNS → Records**. Find the record named `corpus` and **edit** it to the values below — or, if there is no such record because the step 5 scan never imported it, **create** it with those values. Either way you end up with exactly this and nothing else on that name:

| Type | Name     | Content | Proxy                |
| ---- | -------- | ------- | -------------------- |
| AAAA | `corpus` | `100::` | **Proxied (orange)** |

**30.** *(The Cloudflare dashboard is reorganised often and these screens did not match this description when the move was run on 2026-08-18. The settings below are what the rule has to **do**; find whatever screen does it. CHECK 31 tests the result rather than the form, which is the reliable way round.)* Same zone → left sidebar **Rules** → **Redirects** (it may be called *Single Redirects*; if Rules opens on an overview, press **Create rule** and pick **Redirect Rule**). **Page Rules, sitting next to it, is the older product and does this job too** — see the fallback below. Name the rule `corpus com to io` and fill it in like this:

- **When incoming requests match**: Field `Hostname` · Operator `equals` · Value `corpus.data-landscapers.com`
- **Then**: *URL redirect* → Type **Dynamic**
- **Expression** — paste exactly: `concat("https://corpus.data-landscapers.io", http.request.uri.path)`
- **Status code**: `301`
- **Preserve query string**: **on**
- Save and deploy.

**30a — the Page Rules fallback.** If Redirect Rules cannot be found, a Page Rule does the same thing and is simpler to fill in. The catch is the allowance: the free plan gives **3 Page Rules and this move needs exactly 3**, leaving none spare ever after, against 10 for Redirect Rules. Use *If the URL matches* `corpus.data-landscapers.com/*` → *Then the settings are* **Forwarding URL** → **301 Permanent Redirect** → destination `https://corpus.data-landscapers.io/$1`. The `/*` captures the path and `$1` puts it back, which is what makes a deep link land in the right place; the query string carries across on its own.

> **CHECK 31.** Paste an old deep link into a browser — for example `https://corpus.data-landscapers.com/reports/KEN/KEN-status.html`. It must land on the **same page** on `.io`, not on the front page.
>
> **Expect this to fail from your own machine for up to an hour, with the rule working perfectly.** The old DNS answer is cached locally with its original TTL, so the browser goes straight to GitHub — which no longer claims the hostname and shows *Site not found*. That is what happened on 2026-08-18, and it looks exactly like a broken redirect.
>
> **Test the rule rather than the cache.** From a phone on mobile data, or by forcing the connection past DNS entirely:
>
> ```
> curl -sS -o NUL -D - --resolve corpus.data-landscapers.com:443:<cloudflare-ip> https://corpus.data-landscapers.com/reports/KEN/KEN-status.html
> ```
>
> Take `<cloudflare-ip>` from `Resolve-DnsName corpus.data-landscapers.com -Server 1.1.1.1`. A correct rule answers `HTTP/1.1 301`, `Server: cloudflare`, and a `Location:` carrying the **full path**. That is the check; the browser catches up on its own.

## Part 7 — move the main site

**32.** Whoever maintains the main site's repo changes its `CNAME` file to `data-landscapers.io` and pushes. One line.

**33.** In that repo: **Settings → Pages**, confirm the custom domain reads `data-landscapers.io`, wait for the certificate, tick **Enforce HTTPS**. (Same as steps 25–27.)

> **CHECK 34.** `https://data-landscapers.io/` loads with a padlock.

**35.** Cloudflare → `.com` zone → **DNS**. Delete the four `A` records on `@`. Add instead: **AAAA · `@` · `100::` · Proxied (orange)**.

**Do the same for `www` only if a `www` record is actually there.** On this domain there was none, and that is a real answer rather than another missed scan: Cloudflare always probes `www`, unlike `corpus` which it does not guess, and nothing published anywhere references it — all 11 catalogue article URLs are the bare domain. A hostname that never existed has no citations to keep alive, so it needs no record and no rule. **Do not create one to be safe**: a redirect rule can only fire on a hostname that resolves, so an invented record would be the only thing making the rule reachable, for traffic that does not exist.

**36.** **Rules → Redirects → Create rule**, named `main com to io` (or a Page Rule on the same pattern as 30a, `data-landscapers.com/*` → `https://data-landscapers.io/$1`):

- **When**: Field `Hostname` · Operator `equals` · Value `data-landscapers.com` — and `is in`, adding `www.data-landscapers.com`, only if step 35 found a `www` record to convert
- **Then**: Dynamic → `concat("https://data-landscapers.io", http.request.uri.path)` → `301` → preserve query string **on**

> **CHECK 37.** An old article link such as `https://data-landscapers.com/2026/06/16/sovereignty-dividing-line/` lands on the same article on `.io`.

## Part 8 — turn Cloudflare on properly

**38.** Cloudflare → **`.io`** zone → **DNS**. Switch three records to **Proxied (orange)**: **`data-landscapers.io`** — that is **all four `A` rows**, which share the name and must share the proxy status; the table lists records by full hostname rather than by the `@` shorthand used for entering them —, **`www.data-landscapers.io`** and **`corpus.data-landscapers.io`**. Check the zone selector says `.io` and not `.com`.

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

---

# What the run taught

*(2026-08-18. Kept because the corrections above are scattered through the steps they belong to, and because the pattern in them is the useful part.)*

**Every failure was the dashboard, and none was the plan.** The order of operations held from start to finish: nameservers first, cutover late, redirect immediately after, proxy last. Nothing had to be undone. What went wrong was always *where a control lives*, and Cloudflare moved three of them between the writing of this file and the running of it.

**So the checks are worth more than the instructions.** Every step naming a button aged badly; every check naming a result held. CHECK 31 is the clearest case: the browser said *Site not found* while the redirect was returning a perfect `301`, and the only way to know that was to test the rule past DNS rather than through it.

**A stale DNS answer looks exactly like a broken configuration**, and it lasts up to an hour. Twice during this run something appeared broken and was not. `curl --resolve`, or a phone on mobile data, settles it in seconds; a browser cannot, because the browser is the thing that is wrong.

**Cloudflare's scan does not find what it cannot guess.** `corpus` was never imported, so the old subdomain went dark at step 9 rather than step 25. `www` was absent for the opposite reason — it never existed, which the scan *would* have found. Same symptom, opposite causes, and only the published record could tell them apart.

**The site was never at risk, because the checks came before the switches.** The one genuinely dangerous moment was putting a Worker on `corpus.data-landscapers.io/*`: if the Hello World template had still been deployed, every page would have become the words *Hello World*. Checking the deployed code first cost thirty seconds.
