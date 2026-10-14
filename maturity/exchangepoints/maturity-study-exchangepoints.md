---
type: task
reader: cc
title: maturity-study-exchangepoints.md — the forty-third maturity study: exchange points keeping traffic local, in four questions
last_reviewed: 2026-10-14
status: prepared 2026-10-14; waits for Bill's word on the questions
---

# Maturity study: exchangepoints

*(Commissioned by Bill on 2026-10-14 as `infra.connect--internet-exchange-points`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**A place in the country where networks hand each other traffic directly**, whoever runs it and whatever it is called: a national exchange point, an association's, or a commercial one in a data centre.

The study redraws `infra.connect--internet-exchange-points`, which as at 2026-08-31 puts 27 countries at stage 3, 19 at stage 2 and Eritrea and São Tomé and Príncipe at stage 1, none at stage 4 or 5, and leaves Algeria, Egypt, Guinea, Guinea-Bissau, Namibia and Tunisia unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Exchange points keeping traffic local | Internet exchange points: exchange points keeping traffic local | `infra.connect--internet-exchange-points-exchange-points-keeping-traffic-local` |

Anything else the evidence names is `other`, noted and never staged: an exchange decreed, planned, financed or being equipped but with no networks exchanging traffic; a content cache inside one operator's network; data centres; regional exchanges planned between countries, which `regionalinfrastructure` assesses; member counts and traffic in gigabits, which are reported in the long summary and set nothing except under question 3.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is an exchange point in service? | A source states that networks exchange traffic at an exchange point in the country |
| 2 | Does a global content network serve from it? | A source states that Google, Meta, Akamai, Netflix, Cloudflare or another content network has a cache at the exchange or peers there |
| 3 | Is its traffic shown growing? | Traffic figures for the country's exchange at two dates at least twelve months apart, the later one higher and from the past three years |
| 4 | Does it reach beyond one city? | A second exchange point in service in another city, or networks from other countries peering at the country's exchange |

## 3. The ladders

**Exchange points keeping traffic local**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no exchange point operates in the country |
| 2 Preparing | Yes to 1: an exchange point in service |
| 3 Establishing | Yes to 2: a global content network serving from it |
| 4 Operating | Yes to 3: its traffic shown growing |
| 5 Leading | Yes to 4: a second city, or networks from other countries peering there |

- **Only question 3 has a window.** An exchange or a cache in service stays in service until a later source says it has closed or peering has stopped.
- **The two traffic figures may come from one source or two**, and must be for the same exchange.
- **Stages 1 and 2 are close to the row as it stands**; a decreed or equipped exchange, which the row put at stage 2, is now `other`. The row's stage 3 asked for a small membership and its stage 4 for the main operators, content networks and the government network: whether operators are "the main" ones, and when membership is "small", are judgements, so the content network alone is asked. Stage 5 asked whether barriers to entry were removed, which no story can state; a second city or foreign members is the reach the African Union's exchange system asks for, and a story states it.

`study.json` holds this as two aspects: `exchange` (`growing`, `content`, `service`, `none`) for questions 1 to 3, and `reach` (`wider`, `none`) for question 4.

## 4. The norm

The African Union's Digital Transformation Strategy 2020–2030 and its African Internet Exchange System ask every country for an exchange point that keeps local traffic local, with content close to users and links to the region. This study asks whether a country has an exchange in service, whether a global content network serves from it, whether its traffic is shown growing and whether it reaches beyond one city; it does not measure price, latency or how much traffic stays local.

## 5. What the run reads

- **Read**: **291 news readings**, in all 54 countries: 256 about exchange points, which are 174 stories, a regional story being read once for each country it names, and 35 more that the current cells cite for this row.
- **Not read**: long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**35 million.** The fibre backbone study read 388 stories and came to 40 million with its summaries written by a script; this one reads 291. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [ ] **D1. Bill's word** on the questions.
- [ ] **D2. Read**: one fan-out of drafters over the 291 readings.
- [ ] **D3. Stage** as at 2026-09-30, the parent reading every fact that sets stage 4 or 5; agreement on 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
