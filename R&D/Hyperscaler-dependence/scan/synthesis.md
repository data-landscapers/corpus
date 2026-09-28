---
title: Who hosts the African state's front door — three countries, one method
date: 2026-09-28
author: Bill Anderson
source: R&D/Hyperscaler-dependence/scan/ (ZAF, KEN, NGA — nodes.csv, organisations.csv, run.json each)
links: the three country reports are linked relatively below; rewrite the links when they are published
---

# Who hosts the African state's front door: three countries, one method

28 September 2026 · Bill Anderson

We scanned 150 institutions in South Africa, Kenya and Nigeria — ministries, security services, regulators, the ten largest banks in each, payment switches, exchanges and state-owned companies — to find out who hosts their public-facing systems. Nearly three quarters of them use a US cloud provider somewhere. Almost none of that is in Africa, even where Amazon, Microsoft and Google have built African data centres. And in every country a quarter to a half of the estate sits behind a shield that hides its host from view. The three country reports are here: [South Africa](ZAF/report.md), [Kenya](KEN/report.md) and [Nigeria](NGA/report.md). This note is what they add up to, and what we learned about the method.

## Where the idea came from

In September 2026 Computer Weekly published [a data dive on UK police forces' dependence on US cloud](https://www.computerweekly.com/news/366650799/Data-dive-Mapping-UK-police-forces-hyperscale-dependence). What caught our eye was not the finding — 47 of 48 forces on a US hyperscaler, 46 routing email through Microsoft 365 — but how it was reached. No freedom-of-information requests, no procurement records, no cooperation from anyone. The researchers took each force's internet domain, enumerated every web and mail address under it from public records, looked up who owned the server each address pointed to, and counted.

Everything that method consumes is public and global: the domain name system, the public logs in which every website certificate is recorded, the registries that say who owns which internet addresses, and the lists the cloud companies themselves publish of the addresses they use. None of it depends on a government publishing its contracts or answering a request. That matters in Africa, where procurement transparency is uneven and freedom-of-information laws are often absent or unenforced. The method could be run on any state from a laptop, in an afternoon, without asking.

So we ran it. We drew up a generic list of 36 kinds of strategic institution — the presidency, parliament, defence, police, intelligence, treasury, revenue, the central bank, the ID authority, the electoral commission, the data protection regulator, the payment switch and so on — found each one's domain in three countries, and scanned. The scan found 22,976 web and mail names across the 150 institutions, of which 17,930 led to a working server. The whole exercise, from reading the article to three finished reports, took four days.

## What the three countries have in common

**US cloud is everywhere, and nowhere in particular.** 108 of the 150 institutions use Amazon, Microsoft, Google or Oracle for some part of their public estate: 43 of 49 in South Africa, 36 of 51 in Nigeria, 29 of 50 in Kenya. By share of working addresses, South Africa is highest at 28%, Nigeria next at 24%, Kenya lowest at 11%. Those are lower than the UK police figures, and the reason is not that African states have chosen sovereignty; it is that they lean on other things — telecoms companies, their own servers, cheap foreign hosts and, above all, shields.

**The African data centres are barely used.** Amazon, Microsoft and Google have all opened South African regions, and Amazon a zone in Lagos, each announced as an answer to the sovereignty question. The estate has not moved. In South Africa only 4% of all working addresses are on US cloud inside South Africa; in Kenya about 2%; in Nigeria 1%, and just four addresses in the whole scan use the Lagos zone. Where these institutions use US cloud they use Europe — Microsoft in Dublin and Amsterdam, Amazon in Ireland and Frankfurt — or the providers' worldwide delivery networks, which put a copy of a website near each visitor and belong to no country at all. A hyperscaler region announced is not a hyperscaler region used, and the gap between the two is now a number.

**Microsoft carries the mail of half the state.** 79 of the 150 institutions route email through Microsoft 365; Google carries seven. Email is a fair proxy for the office: a body on Microsoft 365 for mail usually keeps its documents and calendars there too. Eight of the ten largest banks in each of South Africa and Kenya, and seven of ten in Nigeria, are on Microsoft.

**Chinese cloud is almost absent.** For all the attention paid to Huawei in African digital infrastructure, the scan found four addresses on Huawei Cloud in three countries: three at Safaricom and one at Zenith Bank, apparently for security cameras. At the public-facing edge, at least, the dependence is American and European, not Chinese.

## Where they differ

**Three models of the state's core.** Nigeria keeps the heart of the state at home: State House, Defence, Justice, Foreign Affairs, the Accountant-General and the Auditor-General hold 89–100% of their estate on Galaxy Backbone, the government's own data centre, and route their mail through it too. Kenya keeps central government's *mail* at Konza, its national data centre — the Presidency, Treasury, Foreign Affairs, Interior and five more — but its web estate sits mostly behind shields. South Africa has SITA, the state IT agency, and the Police and Home Affairs keep 71% of their estate with it; but the Presidency's website is on a commercial web host, the Treasury is 74% on US cloud, and the state as a whole leans on SITA for only 7% of its addresses. All three countries built a national data centre; only one put its core in it.

**Banks and governments trade places.** In South Africa banks and government use US cloud about equally (30% and 27%). In Kenya the banks use it two and a half times as much as government (20% against 8%). In Nigeria it is the other way round: government 30%, banks 16%, with the banks hiding two thirds of their estate behind shields. There is no single story about who is more exposed, which is itself a finding: it depends on the country, and the answer for one does not transfer.

**The regulators of data are among the most exposed.** Nigeria's Data Protection Commission runs 95% of its estate on Amazon, three quarters of it in Cape Town — the body that enforces where Nigerians' data may go keeps its own outside Nigeria. Nigeria's electoral commission is 80% on Amazon, most of it in Virginia; its national ID authority fronts its services through Amazon's delivery network. South Africa's electoral commission and statistics office hide almost everything behind a shield. Kenya's data commissioner, by contrast, is at home on government infrastructure, though its mail is on Microsoft.

## What the method threw off for free

The shares were the point of the exercise. The more actionable findings were by-products.

- **Five addresses that anyone could take over.** One at Safaricom and three at Nigeria's Central Bank, Health ministry and Accountant-General point at cloud names that have been deleted; one at Eskom relies on an outside domain that has lapsed and is now held by a domain-parking firm. Whoever claims those names could publish under an institution's own address. We have flagged them and are not naming them.
- **A land registry serving gambling adverts.** South Africa's Deeds Office domain stopped resolving during the scan; hours earlier its homepage was showing Indonesian gambling content.
- **Sensitive bodies on budget hosting.** Part of Kenya's Office of the President sits with a German budget server firm and a US web host; Kenya's Defence, Judiciary and Health ministry have servers with the same German firm. South Africa's Government Employees Pension Fund is on Lithuanian shared hosting. Nigeria's National Judicial Council is with UK and Canadian web hosts, and its health insurance authority routes mail through the German firm.
- **A British company screens half of South Africa's institutional mail.** Mimecast filters mail for 24 of the 49 South African institutions, including the Reserve Bank, the electoral commission and Stats SA. It is not a hyperscaler, and it is a dependence nobody was counting.

## What we learned about the method

**It works, and it is cheap.** Three countries, 150 institutions, four days including the write-up. The remaining 51 African states are a seed-list exercise, not a method one, and a re-run in a year gives a trajectory that no procurement register would.

**The shield is the binding limit.** A quarter of South Africa's estate, 44% of Nigeria's and 48% of Kenya's sit behind Cloudflare, Imperva, F5 or a mail filter, and the scan cannot see through them. Every US-cloud figure is therefore a floor. In Kenya the floor is low enough that the headline share says less than the institution-by-institution table does. The UK study had the same problem to a lesser degree; in Africa it is the first caveat, not the last.

**It counts addresses, not importance.** South Africa's 12,666 names against Kenya's 3,645 partly reflects bank marketing estates, and a bank with 400 test sites weighs more than a ministry with 20. The next version should report a second, narrower figure — the main portal, the mail, the login gateways — alongside the whole.

**It sees the front door only.** Websites, mail, portals, remote access, online banking. Not the core ledger, the population register or the payroll, which for banks are mostly in their own data centres. A state whose ministries all resolve to Dublin has a fact on record that its hosting policy has to answer to; it does not have a finding about where its citizens' records are.

**The by-products want their own pass.** Dangling names, lapsed domains and compromised sites are not what the scan was for, and they are what a security team would act on first. They fell out of the data unasked, which suggests a dedicated hygiene scan across all 54 states would find a great deal more.

**Nothing was touched.** The scan used public address lookups, public certificate records, the registries and the cloud companies' own published lists. It never connected to any institution's systems, and it never needs to.

Every figure here is as of 28 September 2026. The data, the institution lists and the runbook are in `R&D/Hyperscaler-dependence/scan/` and `R&D/Hyperscaler-dependence/HYPERSCALER-SCAN.md` in the Corpus repository.
