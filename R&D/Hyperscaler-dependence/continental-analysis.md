---
layout: article
title: Who hosts the African state's front door
subtitle: Where 1,830 strategic institutions in 54 countries run their websites and email
date: 2026-09-30
author: Bill Anderson
category: Sovereignty
summary: We mapped who hosts the public internet services of 1,830 ministries, regulators, security bodies, central banks, commercial banks and payment systems across Africa. US cloud companies are used by two in five institutions, almost always from data centres outside Africa. Telecoms operators, foreign budget hosts and security shields carry much of the rest, and only a small share sits on government or the institutions' own systems.
has_data_table: false
---

[Corpus dataset: Institution hosting](https://corpus.data-landscapers.io/datasets/institution-hosting/) · [Methodology](https://corpus.data-landscapers.io/datasets/institution-hosting/methodology/)

In the last week of September 2026 we looked up who runs the servers behind the public internet services of 1,830 institutions in all 54 African countries. They include the presidency, parliament, ministries, the police and armed forces, the central bank, the ten largest commercial banks, the payment switch, the electoral commission, the ID authority and the data protection regulator. The aim was to put numbers on a question that is usually argued without them: how far the African state's public-facing systems depend on foreign companies, and on the large US cloud providers in particular.

The short answer is that the dependence is real but mixed. Two in five institutions use Amazon, Microsoft, Google or Oracle for part of their public estate, and nearly all of that use is in Europe or on worldwide networks, not in the cloud data centres these companies have opened in Africa. More than two in five institutions with a mail record receive their email through Microsoft or Google. At the same time, telecoms operators, foreign budget hosting firms and security shields carry a larger combined share than the US cloud companies do, and only one address in seven is on government or the institutions' own systems.

> **What this can and cannot see**
>
> The scan looks at the public edge of each institution: its websites, email servers, online portals and the name servers that direct traffic to them. It does **not** see where databases, payroll, core banking, population registers or other internal systems run. An institution can host its website abroad and keep its records at home, or the reverse.
>
> About a quarter of the addresses sit behind a shield, most often Cloudflare, which hides the server behind it. Some of those servers will be on US cloud, so every US cloud figure here is a **minimum**. Mail filtering services hide the mail provider in the same way.
>
> The figures count addresses, not importance, and they describe a single day (28 and 29 September 2026). They are evidence about dependence, not a measure of it.

## How it was done

The method follows [a September 2026 Computer Weekly study](https://www.computerweekly.com/news/366650799/Data-dive-Mapping-UK-police-forces-hyperscale-dependence) of UK police forces. It uses only public sources: the domain name system, the public logs in which website certificates are recorded, the internet registries that record who holds each block of addresses, and the address lists the cloud companies publish for their own networks. It needs no cooperation from any institution and no procurement records, and it treats every country the same way.

We drew up one list of 36 kinds of strategic institution and found each one's main internet domain in every country. Where a country has no such body, or its domain could not be found, the gap is recorded rather than filled. The scan then found 61,106 web and mail names under those domains and 65,534 working addresses, and assigned each address to the company or body that runs it. The full method, its checks and its limits are in the [methodology](https://corpus.data-landscapers.io/datasets/institution-hosting/methodology/).

## Who hosts the front door

Across the continent, the working addresses divide as follows.

| Host | Share of working addresses |
| --- | ---: |
| Behind a shield (Cloudflare and similar), host not visible | 24% |
| Telecoms operators and internet providers | 19% |
| US cloud: Amazon, Microsoft, Google, Oracle | 17% |
| Other foreign hosting firms | 12% |
| US online services such as Microsoft 365 | 11% |
| The institution's own systems | 9% |
| Government data centres | 6% |
| African data centres and IT firms | 2% |
| Chinese cloud, private and unidentified addresses | 1% |

No single kind of host dominates. The largest share is the one the scan cannot see into, and the second largest is the national telecoms operator. Taken together, US cloud and US online services account for 27% of the addresses, and that rises by an unknown amount once the shielded addresses are counted.

## US cloud is widely used, mostly from outside Africa

732 of the 1,830 institutions (40%) have at least one address on Amazon, Microsoft, Google or Oracle cloud. 968 (53%) use either US cloud or a US online service such as Microsoft 365. For most of them it is part of the estate rather than all of it: 93 institutions have more than half of their addresses on US cloud.

Microsoft accounts for half of the US cloud addresses and Amazon for most of the rest. Google and Oracle together account for 7%.

Very little of this use is in Africa. Amazon has a cloud region in Cape Town and a smaller zone in Lagos, Microsoft has regions in Johannesburg and Cape Town, and Google and Oracle have opened in Johannesburg. Only 7% of the US cloud addresses we found are in those African regions, and institutions in 19 of the 54 countries use them at all. Half are in Europe. Microsoft's and Amazon's Dublin regions alone hold a third of the total. Another third are on the companies' worldwide delivery networks, which serve copies of a website from wherever the visitor is and have no single location. About 6% are in North America.

This does not show that institutions chose Europe over Africa. Many services were set up before the African regions opened, and some cloud services are only offered from certain regions. It does show that, on the scan date, the African regions carried a small part of the African state's US cloud use.

## Email runs through Microsoft for a third of institutions

Email is the clearest single indicator of office systems, because an institution that receives its mail through Microsoft 365 or Google usually keeps its documents and calendars there too. Of the 1,637 institutions with a mail record, 629 receive their mail through Microsoft 365 and 98 through Google: 44% between them. The rest use their telecoms operator, a government mail service, their own servers or a commercial host.

Banks lean further on Microsoft than governments do: 197 of the 377 commercial banks (52%) against 432 of the 1,453 other institutions (30%). 122 institutions pass their mail through a filtering service before it reaches the mailbox, most often Mimecast, a British company. Where a filter is in place the provider behind it is not always visible, so the Microsoft and Google counts are also minimums.

## Telecoms operators and foreign budget hosts carry much of the rest

The national telecoms operator is the single most common host in several countries. In Algeria 74% of the addresses are with telecoms operators, in Rwanda 64%, in Ethiopia 54% and in Egypt 51%. Across the continent, 430 institutions have most of their addresses with a telecoms operator.

Commercial hosting firms outside Africa, other than the four US cloud companies, hold 12% of the addresses. This is ordinary shared and virtual hosting from companies such as OVH, LWS, Hostinger, Contabo, Namecheap and DigitalOcean. In six countries (Congo, Comoros, Chad, South Sudan, Sierra Leone and Liberia) these firms hold more than half of the addresses we found. French hosting companies are common among institutions in francophone countries. 300 institutions have most of their addresses with such firms.

## Government and own systems

14% of the addresses are on a government data centre or the institution's own network, and 263 institutions keep most of their estate there. The share varies widely. It is highest in Gabon (45%), Tanzania (36%) and Burkina Faso (35%), and it is under 5% in 19 countries. 258 institutions have addresses both at home and on US cloud, which is common where a ministry keeps its main systems in a national facility and uses cloud services for particular sites.

## Shields hide a large part of the estate

A quarter of the addresses are behind a shield. Cloudflare accounts for 86% of these; Imperva, Akamai, F5 and Radware for most of the rest. Shields protect websites from attack and speed them up, and they are a reasonable choice. They also make the host behind them invisible to this kind of scan. In six countries (Togo, Uganda, Kenya, Somalia, Nigeria and Libya) more than 40% of the addresses are shielded, and in 23 countries the shielded share is larger than the US cloud share. In those countries the US cloud figure says least.

The most sensitive institutions are the most shielded. Two thirds of the addresses of the armed forces and intelligence services we found are behind shields, although both groups are small: 11 armed forces and six intelligence services had domains we could scan.

## Banks and governments

Commercial banks use US cloud more than government bodies do: 22% of bank addresses against 14% of government addresses across the continent, and banks are higher in 38 of the 54 countries. Banks are also more heavily shielded (33% of their addresses). Among government bodies, stock exchanges, ID authorities, securities regulators and central banks use US cloud most. Presidencies, defence ministries, the armed forces, e-government agencies and the operators of national data centres use it least.

## Chinese cloud is almost absent

Despite the attention paid to Chinese companies in African digital infrastructure, the scan found 25 addresses on Chinese cloud services, at seven institutions, all of them telecoms operators or banks, among them Safaricom, Ethio Telecom and Telecom Egypt. At the public edge of the state, the foreign dependence the scan can see is on US and European companies. This says nothing about equipment, networks or internal systems supplied by Chinese firms, which the scan does not cover.

## Differences between regions and countries

| Region | Countries | US cloud | Behind a shield | Government or own | Telecoms | Other foreign hosts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Southern Africa | 10 | 24% | 20% | 20% | 17% | 4% |
| West Africa | 17 | 18% | 25% | 12% | 12% | 17% |
| Central Africa | 7 | 12% | 15% | 11% | 20% | 31% |
| East Africa | 15 | 11% | 30% | 14% | 23% | 11% |
| North Africa | 5 | 9% | 22% | 8% | 40% | 8% |

Southern Africa, home to all the full African cloud regions, uses US cloud most and also keeps the largest share on government or its own systems. North Africa leans most on telecoms operators, Central Africa on foreign budget hosts and East Africa on shields.

The median country has 13% of its addresses on US cloud. The highest shares are in Guinea (34%), Namibia, Equatorial Guinea (both 30%), the Gambia (29%) and South Africa (28%); Eritrea is higher still, but on 47 addresses from five institutions. The lowest are in Algeria (1%), Mauritania (2%) and Burundi (4%). Country figures rest on between five and 52 institutions each, and a country with few institutions or addresses can rank high or low on very little.

## What it means

The findings support a few careful conclusions.

- **The African cloud regions are not yet where the African state's cloud use is.** Policies that treat the opening of an African region as a solution to data residency should check how much use has actually moved.
- **Hosting choices are made institution by institution.** Most countries show a mix of telecoms, national, foreign and cloud hosting, often within a single ministry. That points to the absence of a common hosting policy, or to one that is not followed, rather than to a deliberate national choice.
- **Much of the dependence is on small commercial hosts as well as large clouds.** Sensitive institutions using shared budget hosting abroad raise questions of security and continuity that are separate from the debate about hyperscalers.
- **The shielded share is the biggest unknown.** Governments that want to know their own exposure can answer the question directly, because they know where their servers are. An outside scan cannot.

The scan also found 13 names, in nine countries, that point to cloud addresses which have been deleted and could be claimed by anyone, who could then publish under the institution's name. We have not named them and have passed them on for disclosure.

## The data

Every figure here is as of 28 and 29 September 2026. The [institution-by-institution dataset](https://corpus.data-landscapers.io/datasets/institution-hosting/) can be searched and downloaded, and the [methodology](https://corpus.data-landscapers.io/datasets/institution-hosting/methodology/) sets out how it was made and what it cannot show. A new scan in a year will show which way these figures are moving.
