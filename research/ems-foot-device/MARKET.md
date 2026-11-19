# MARKET: ems-foot-device (analyst run 2026-11-19, about 140 Brandsearch credits, 0 AI credits, no generation)

## 0. Scout card is the wrong product
Starting card artuvate.co_9108715372891 "FisioRest" is a **3-in-1 NECK massager**, not an EMS foot device. Evidence in market/product_artuvate.json, similar_artuvate.json, sourcing_artuvate.json:
- Its market members are all neck products: minakolab "3 in 1 Massage, Comfort and Support for the Neck and Upper Back", relievia "Neckrelief", trynovis "Novis Cervora | Neck Relief in 10 Minutes a Day".
- The supplier match is a "Cervical Pillow ... Heating Compress".
- get_similar_products returned only neck items.
- Its audience skews men 59.7%, 35-44 (34.3%), not seniors.

Its numbers are real but belong to the neck category: 4,342 ads / 2,121 active, est $1,500/day, first ad 2025-09-27, 10 sellers, $89, "peak", GB 97.9% of EU/UK reach. It is only a useful proxy for the "FisioRest/artuvate" funnel template. **The real EMS foot market is separate, fragmented and small.**

## 1. Market size (EMS foot / leg circulation, all look-alike markets)
Source: search_products over six queries; market/foot_candidates.json and sellers.csv. The brand ids are not strictly unique (med-fit appears under two domains).

- About 25 foot stores seen (EMS foot mats/pads, foot circulation machines, neuropathy foot devices). The big look-alike clusters are zindory.com_8740357800193 (7 sellers, 101 total ads) and tryelevatedproducts.com_7587074605135 (6 sellers, 25 total ads). All are lifecycle "declining". themassagemat.com_9090269085949 has 5 sellers and is "scaling" but has $1/day spend.
- Only **8 of 25 have any active ad right now**. Active ads for the whole set total 349, of which 239 are LegRelief Pro (a different leg product, see 3).
- Search totals: "EMS foot massager" gives 120 product cards, "foot circulation" 1,752 (mostly socks, creams and other items), "neuropathy foot" 296.
- Local-language sellers:
  - DE/CH: minvero.de (27 ads, 0 active), relievio.de (13, 0), officialneuravive.com (7, 0), sneakerly.de (4, 0), celviana.com (4, 0), fitgalaxie.ch (2, 0). **No German seller has an active ad, and all are declining.**
  - FR: nothing real. paseo.2bgroups.com "Bottes de compression à air" (1 ad) and weightworld.fr "Circulator" (1 ad) are different products.
  - EN-UK: mysameo.com, med-fit.co.uk, and others, all on UK-targeted ads. India: olivi.in (INR). Pakistan: trendfusionpk.
- EU/UK reach: for the EMS foot ad set (mysameo.com_9136390701396, 53 ads) GB = 100.0%. For the neck market, GB = 97.9% (BE 0.9, IE 0.4, DE 0.2). **Live spend is essentially UK-only.**

## 2. Price points and offers
- Foot stores (25 listings, usd): min 14.99 (tradersdelights), median 49.95, max 175.0 (tlhstore NeuroPulse). Mats and pads sit at 15-55. The "device / circulation machine" positioning sits at 90-140 (med-fit Medi-Boost 114.24 / 139.93, Medi-X-Ciser 98.74, medirelieve-type pricing is absurd and ignored).
- The same mysameo hardware is sold two ways: EMS Foot Massager at 37.97 (GBP 29.90) and LegRelief Pro at 126.87 (GBP 99.90). Same mat, 3.3x price, solely on the senior/swollen-legs framing.
- Offers seen:
  - 30-day risk-free trial (mysameo ad 26217293791304882).
  - 37% off combo (med-fit ads 27726648076930495, 1802838917564636).
  - 15% code SAM15 (mysameo ad 1641907790243633).
  - BOGO (dadajaan, a different foot relaxer).
  - Nobody shows a bundle ladder in the ad copy I saw.

## 3. Angles and mechanisms
- **mysameo "LegRelief Pro" (ads 26217293791304882, 887605237723808):** senior testimonial ("– John, 72"), pain / swollen evenings / night cramps, "gently boosts circulation with soothing electrical stimulation", "just 20 minutes a day", "designed for seniors", 30-day risk-free. Audience (53 ads): 65+ = 48.1%, 55-64 = 27.4%, women 59.1%.
- **tradersdelights (ads 5208257616066686, 972083385780224, 947922381427401, 1668933017749665, 967550049095028):** "Tired feet → Relaxed, recharged in minutes", "Standing all day? Sore feet at night?" Generic tired-feet relaxation, $14.99 impulse, no medical claim. 145 ads, 55 active.
- **med-fit (ads 4563347130563737, 27726648076930495, 1802838917564636):** "Why Are So Many People Raving About This Foot Circulation Device?"; "Foot & Leg Circulation Machine"; TENS+EMS+massage combo with 37% off. Clinical-device framing.
- Neuropathy-named products (tlhstore NeuroPulse 175.0, kemhappy ThermoMasseur, officialneuravive) have only 2-7 ads each, all inactive.
- For the neck proxy market the creative insights (17 analysed ads) are: pain 76.5%, relief 76.5%, testimonial hook 23.5%, 88.2% BOF / product-aware (creative_insights_artuvate.json).
- **Mechanism claimed everywhere:** EMS/TENS micro-current "boosts circulation". It is the same one-line claim across all sellers; nobody explains a new mechanism.

## 4. How long winners have run
- tradersdelights ads: 2026-05-02 to 2026-11-08, about 190 days, status active (the five ids above).
- mysameo 26217293791304882: 2026-04-17 to 2026-08-12, 117 days. LegRelief Pro store first advertised 2025-12-30 (mysameo_11912789852500, 895 ads, 239 active).
- med-fit.store Medi-Boost: first ad 2025-12-25, 32 ads, 0 active. med-fit ads ran only days to weeks (4563347130563737: 2026-06-30 to 2026-07-19).
- Neck proxy: artuvate first ad 2025-09-27 (about 418 days), still adding about 1,091 ads/30d.

## 5. Spend direction
- Neck proxy (artuvate, trend_artuvate.json): active ads 638 (2026-08-22) to 2,121 (2026-11-19); total 2,277 to 4,342; est daily spend about $1,100 to about $1,500, dipping to 920 on 2026-10-06 and jumping to 1,600 on 2026-10-30. **Growing**, with the Q4 ramp.
- EMS foot, mysameo: ads 31 to 17 total, active 25 to 13; est daily spend about $8 to $23 (noisy; the count jumps 28 to 53 and back as ads relist). Flat/decaying and tiny. LegRelief Pro: lifecycle "declining", est $74/day store, $170/day market, 179 new ads in the last 30 days.
- Leaders in the strict EMS foot set: tradersdelights (no spend estimate, est revenue $7,200-9,500/mo, ads started 2026-06-05, 54 in last 30d, **growing**), tryrevora.store (18 ads, all started 2026-10-14..16, brand new), med-fit (est $9/day).
- The big multi-seller clusters (zindory, tryelevated, kiago, medralife, everyly) have **0 active ads** and last ran Mar-Aug 2026. **The classic "EMS foot mat" wave (spring 2026) has burnt out.**
- Whole-market revenue bands: neck market $240-320k/mo (scope market). EMS foot individual sellers: tradersdelights $7.2-9.5k, mysameo foot $2.4-3.1k, tryrevora $3.2-4.2k, LegRelief Pro market $22-29k.

## 6. Concentration and moat
- The foot niche has no dominant seller and no moat: no patents, no brand and no retail. Every listing is the same 1688 pulse mat.
- The only larger foot-circulation seller is mysameo (LegRelief Pro market $22-29k/mo, 895 ads). Its moat is not real, because it is a mat re-skinned as a senior device.
- In the neck cluster artuvate is 4,342 of the 4,369 total ads (99%), so that market is monopolised by one advertiser. This does NOT apply to foot.

## 7. Sophistication (Schwartz)
Stage 3 and drifting to 4. The basic claim "EMS foot mat improves circulation / relieves tired feet" is saturated: dozens of identical $15-55 listings, all of them "Improves blood circulation". The three leaders have each differentiated only by framing:
- tradersdelights: tired feet relief.
- mysameo/LegRelief: senior swollen legs.
- med-fit: clinical circulation machine / TENS combo.

Buyers do not need a new mechanism to buy, but they need a new reason to trust (medical credibility, "who it is for", a risk reversal). Nobody explains why EMS increases circulation, and no one has clinical-style proof in the ad copy I saw.

## 8. Sourcing and margin
- mysameo foot (sourcing_artuvate/ mysameo_foot.json): 1688 EMS foot mat, unit cost $0.69, MOQ 1, est shipping $6, retail $37.97, gross margin 98.2%, break-even ROAS 1.27, break-even CPA $29.86, verdict "profitable".
- tradersdelights: unit cost $0.91, shipping $8.4, retail $14.99, break-even ROAS 3.04, CPA $4.93, verdict "difficult" because of the low price.
- At a senior framing of about $79-99 the break-even ROAS would be about 1.2-1.3 (extrapolated from the figures above, not a tool output).
- Shipping complexity is low: flat, light, USB-rechargeable pad. Concerns: battery/electrical product compliance (CE, UKCA, medical claims in UK/EU), and electrode wear.

## 9. Gaps
1. **Language:** Germany, Austria, Switzerland and France have no seller with active ads. The 6 German listings are 4-27 ads each, all dead since Apr-Nov 2026, so German demand is untested rather than proven. This is the best unserved language market, but it is unproven at scale.
2. **Angle:** nobody pairs EMS with a plausible mechanism explanation (muscle pump / "second heart" idea; only reliefrecoverydirect has the "Second Heart" title, 4 ads), a neuropathy-specific proof angle, or a physio/doctor-led trust angle. Every active ad is a BOF testimonial or an impulse benefit statement.
3. **Avatar:** 65+ is partly served only by mysameo (UK). Younger, standing-all-day workers (nurses, hairdressers) are served by tradersdelights only at $15. There is a thin middle at $59-99 for carers/adult children of seniors.
4. **Market:** non-UK English (US/CA/AU) is invisible, since spend data are EU/UK only.

## 10. Comment evidence
Probe (comments/probe_log.json, market/comment_probe_raw.json): I searched Instagram-matched ads, sorted by adspy_comments, for the seven sellers with active foot ads (tradersdelights, mysameo, med-fit.co.uk/.store, tryrevora, reliefrecoverydirect, minvero) and for artuvate.co. Result: 2 rows (one ad, 1802838917564636, shown under two domains), IG 0 comments, 36 views. artuvate.co has **0** Instagram-matched ads. No ad reached the 5-comment threshold, so get_meta_ad_comments was never called and 0 comments were pulled. There is no comment evidence for this market.

## 11. Verdict
EMS foot as a generic mat is a **closed, price-war category** ($15-55, 17 of 25 stores with zero active ads, burnt-out spring wave). There is room only for a **repositioned senior / "swollen legs and neuropathy" device** at about $79-99 with a trust-led angle, as mysameo's LegRelief Pro proves (3.3x price on the same mat, $22-29k/mo market revenue, though in "declining" stage with 239 active ads). It is not a land-grab.
