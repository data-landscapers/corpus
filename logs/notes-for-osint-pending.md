---
type: doc
title: Notes for OSINT — pending delivery
last_reviewed: 2026-08-20
---

# Notes for OSINT — pending delivery

*(**Temporary holding file, 2026-08-20.** Note 27 was written into `osint-corpus-exchange/notes-for-osint.md` during the 2026-08-20 build, at a moment when the only copies of that file were an untracked one in `C:\CORPUS` and one in `C:\OSINT`, which turns out to be a **mirror** of a master repo on OSINT's own drive and is refreshed after every `SWEEP-CYCLE`. Neither copy is versioned or authoritative, so the note had no durable home. This file is that home until Bill stands up the OSINT/Corpus exchange share, at which point the note goes there and this file is deleted.)*

*(Nothing else belongs here. This is not a second channel — it is one note, parked, because the channel it belongs in was mid-move when it was written.)*

## Note 27, as written

**27** (2026-08-20) — **Two records carry no `hub_line` at all, and one story is held twice under two slugs.** Found while reading the day's records against the ledgers in a CORPUS build; they cost nothing to collect and nothing else looks for them.

**The missing hub lines.** `raw/2026/2026-08-19-standard-bank-expands-unionpay-acceptance.md` (ITWeb Africa, nine markets, `dpi.pay`) and `raw/2026/2026-08-19-tan-ezeebit-zaru-digital-asset-merchant-payments.md` (Tech Africa News, `dpi.pay`) both end their frontmatter without a `hub_line`, and the first also carries no `origin_status`. `raw/2026/2026-08-19-wearetech-lideflow-esso-dong-djafalo-paiements-transfrontaliers.md`, `raw/2026/2026-08-19-nigeria-to-earn-41-million-from-mtns-406-million-dividend-payout.md` and `raw/2026/2026-08-19-smart-africa-afrinic-internet-governance-talks.md` are the same shape. A record with no hub line is still citable and still compiles, so nothing downstream fails — it simply cannot be read at a glance, which is the whole purpose of the field.

**The duplicate.** `raw/2026/2026-08-11-fcdo-sta-s-southern-africa-programme.md` and `raw/2026/2026-08-11-uk-fcdo-xsa-2026-sta-s.md` are the same UK FCDO call at the same URL (`https://www.gov.uk/international-development-funding/science-and-technology-accelerator-systems-sta-s-southern-africa-programme`), held under two slugs. CORPUS cites both on one ledger row rather than choosing between them, because a slug is a permanent identifier and picking a survivor is OSINT's call, not CORPUS's.
