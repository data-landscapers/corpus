---
type: task
reader: cc
title: maturity-study-satellitebroadband.md — the forty-fourth maturity study: satellite broadband licensed and on sale, in four questions
last_reviewed: 2026-10-14
status: run 2026-10-14; on the soft-launch map, waits for Bill to accept
---

# Maturity study: satellitebroadband

*(Commissioned by Bill on 2026-10-14 as `infra.connect--satellite-broadband-licensing-and-availability`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Internet access sold to households or businesses in the country over a satellite link**, whoever sells it and whatever the orbit: a low-orbit service such as Starlink or OneWeb, a geostationary one such as Konnect or YahClick, or capacity on a national satellite resold by a licensed provider.

The study redraws `infra.connect--satellite-broadband-licensing-and-availability`, which as at 2026-08-31 puts 27 countries at stage 3, 16 at stage 2 and 6 at stage 1, none at stage 4 or 5, and leaves Eritrea, Libya, Malawi, Namibia and South Sudan unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Satellite broadband licensed and on sale | Satellite broadband licensing and availability: satellite broadband licensed and on sale | `infra.connect--satellite-broadband-licensing-and-availability-satellite-broadband-licensed-and-on-sale` |

Anything else the evidence names is `other`, noted and never staged: a licence applied for, a framework drafted or a tender open; satellite links that carry a mobile operator's own traffic; direct-to-phone messaging; satellite links serving only government sites; satellite capacity for international routes, which `internationalbandwidth` assesses; prices and speeds, reported in the long summary and setting nothing.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a satellite broadband provider licensed? | A source states that the regulator or ministry has licensed or authorised a provider to sell internet over satellite in the country |
| 2 | Is it on sale? | A source states that households or businesses in the country can buy satellite broadband from a licensed provider |
| 3 | Is it on sale from more than one satellite network? | A source states that services on two different satellite networks are on sale, for instance Starlink and a OneWeb or Konnect service; two resellers of one network count once |
| 4 | Does the regulator count its subscribers? | The regulator publishes the number of satellite broadband subscribers in the country, from the past three years |

## 3. The ladders

**Satellite broadband licensed and on sale**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no satellite broadband provider is licensed, or that its sale or use is banned |
| 2 Preparing | Yes to 1: a provider licensed |
| 3 Establishing | Yes to 2: on sale to households or businesses |
| 4 Operating | Yes to 3: on sale from two satellite networks |
| 5 Leading | Yes to 4: subscribers counted by the regulator |

- **Only question 4 has a window.** A licence or a service stays in place until a later source says it has been suspended, withdrawn or stopped; a suspension of sales takes a country back to stage 2.
- **Stage 3 is the row's stage 3 as it stands.** The row's stage 2 also took a pending application or a draft framework; neither is a licence, so a country with only those now sits at stage 1 where a source says nothing is licensed, and is otherwise unplaced.
- **Stages 4 and 5 change.** The row asked for blanket licensing of terminals, published fees and mutual recognition of visiting terminals, which is what the ATU recommendation asks; no story states them, and where one provider holds the licence its customers need none of their own. Two networks on sale is the competition the recommendation aims at, and a published subscriber count is the availability the row's stage 5 asked to be reported; a story or a regulator's report states both.

`study.json` holds this as two aspects: `service` (`choice`, `sale`, `licensed`, `none`) for questions 1 to 3, and `counted` (`counted`, `none`) for question 4.

## 4. The norm

The African Telecommunications Union's Recommendation ATU-R 005-0 (2021) asks member states to license satellite broadband simply: user terminals on a blanket basis, low-orbit systems authorised quickly with published fees, and visiting terminals recognised. The African Space Strategy (2016) asks for satellite services that reach the unconnected. This study asks whether a provider is licensed, whether the service is on sale, whether more than one satellite network sells it and whether the regulator counts its subscribers; it does not measure price, speed or how licences are granted.

## 5. What the run reads

- **Read**: **820 news readings**, in all 54 countries: 779 about satellite broadband, which are 522 stories about one country and 257 readings of 29 regional stories, a regional story being read once for each country it names, and 41 more that the current cells cite for this row.
- **Not read**: long texts, reports and passing mentions, among them 9 longer documents the cells cite, opened only where a question turns on one. **No web search and no handover to OSINT.**

## 6. Token ceiling

**70 million.** The international bandwidth study read 847 readings and came to 62.4 million; this one reads 820. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [x] **D1. Bill's word**: run on it, 2026-10-14.
- [x] **D2. Read**: 200 drafters over the 820 readings; 657 facts.
- [x] **D3. Staged** as at 2026-09-30: 4: 4, 3: 31, 2: 1, 1: 16, two without evidence; 3 rows removed (`corrections.csv`); agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-14.

**Decided in the run**:

- **A dated "not licensed" reverses only the network it names.** Most such statements are Starlink's: its map marking a country "Starting in 2026", or an application pending or refused. They no longer cancel a YahClick, OneWeb or Konnect service sold beside it. Where nothing else is held, a statement that Starlink is not licensed sets stage 1. A suspension leaves the licence standing, a warning about illegal resale or unregistered kits of a licensed network cancels nothing, and a fact dated by a year alone is weighed against a dated reversal from the year's start.
- **Four are at stage 4**: Botswana and Madagascar (Starlink, and OneWeb sold to businesses), Côte d'Ivoire (Starlink, and Konnect through Orange and MTN) and South Africa (YahClick and OneWeb, Starlink still unlicensed). None is at stage 5. Benin, Ghana, Rwanda and Zimbabwe have a regulator's subscriber count, but only one network on sale.
- **Senegal is at stage 3**: the Supreme Court suspended Starlink's authorisation on 7 September 2026, and Konnect through Sonatel Orange stays on sale. Namibia is at stage 3 on OneWeb (Twoobii, June 2026), though it refused Starlink. Sudan is at stage 3 on YahClick through Canar since 2023, and Libya on OneWeb.
- **Sixteen are at stage 1**, all on Starlink pending, refused or banned with no other provider held. Algeria is at stage 2: VSAT licences held by Algérie Télécom Satellite and Djezzy, with no sale stated. Eritrea and Mauritius are without evidence.
- **Three rows removed**: a Benin sale inferred from a price survey, a Tunisian licence reported from unnamed sources, and a Senegal sale dated by its month past the suspension.
- **A script wrote the summaries**, `scripts/study-satellitebroadband-write.py`, from the drafters' fact sentences, as for exchangepoints. Eight rows with the value in the aspect column were moved to `service`.
- **Tokens: 62.6 million at the map**, ceiling 70 million, step 1 included.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
