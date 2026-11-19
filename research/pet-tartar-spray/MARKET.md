# MARKET: pet-tartar-spray (anti-tartar / no-brush dental spray, dogs and cats)

Data: Brandsearch MCP, 2026-11-19. Raw files in `market/` (condensed copies; build.py regenerates them and sellers.csv). About 100 credits used, no transcripts, no generation.

## Verdict up front
One seller owns this market. paw-guardian.com (DentaClean) has 2,001 of the ~2,215 active ads across all spray look-alikes (90%). The "3 sellers" in its market are wrong: franceabsorkas.com and chronocalm.com are French orthopedic-pillow stores that were clustered by mistake (`sellers.json`: both 0 active ads, product URLs `oreiller-...`). Real direct competitors are tiny and mostly stale.

## Market size
- Paw Guardian: 5,587 ads, 2,001 active, 1,091 started in the last 30 days, first advertised 2025-12-24 (product.json). Its ads started as early as 2025-11-15 (ad 833701122635750). It sells other products too: active ads from Jun 2026 push an ear cleaner (waxoff-earclear, ad 1322290326141654), so it is a multi-product pet store.
- Look-alike spray stores found with search_products ("dog dental spray", "tartar spray", "dog teeth cleaning", "plaque remover dog"; sellers.csv): 12 spray stores including Paw Guardian. All 12 show active ads, but most are tiny: littlefindsco.com (127 "active" but last ad 2026-02-12, so stale), moepuppy.com (23 active), furaqua.com (12 active, stage declining, 14 countries), carispray.eu (12 active, EUR 34.99, est $3/day), pupdose.com (6, new 2026-10-22), denwild.shop (5, new 2026-11-09), twolinda.store (5, new 2026-10-27), aussie-pet.com and australianpaws.com (4 each, AUD 19.95, same generic listing), newbeeoo.com (12, stale since 2026-04), boxofsmile.in (5, stale since May).
- get_similar_products returned only pillow look-alikes (similar.json): the image signature is not useful here.
- Adjacent, different mechanisms (not the same product): Canivet ultrasonic tartar remover kit, $99.90 (trycanivet.com, 2,171 ads, 1,073 active, scaling; rarepet.co, wisebuyco.com); dental sticks (omni.pet, est $200-270k/mo, 85 active ads, est $1,700/day; poochandmutt.co.uk, 61 active); FreshWipes (shopvetpets.com, 18 sellers, declining). They show demand for "dog tartar" but are not the no-brush spray.
- Countries: audience.json (5,545 analysed EU/UK ads): GB 94.2%, IE 0.8%, FR 0.7%, ES 0.5%, PT 0.5%, DE 0.3%, GR, BE, NL 0.3%, SE 0.2%, 29 countries in total. Market card says country_count 20. Non-EU/UK reach (US, CA, AU) is not measurable. Ad copy is in English (USD pricing, "$900 vet cleanings") plus French (ads 833701122635750 and 825615377044187, landing page on paw-guardian.co).
- Local-language sellers: French only, and only as Paw Guardian's own advertorial ads (ended Apr 2026). No sellers found for DE, ES, IT, NL, PL, Nordic languages. carispray.eu (EUR) is the only EU-currency spray, with ~$3/day spend.
- Audience: 77.9% women, 22.1% men; ages 45-54 26.8%, 55-64 26.6%, 65+ 17.7%, 35-44 19.4%.

## Price points and offers
- Spray stores: min $3.95 (moepuppy, INR), median $16.99, max $55.99 (Paw Guardian). Stores at $35+ : paw-guardian $55.99 (market range $49.90-55.99), furaqua $39.99, carispray $37.79, pupdose $45.00. The mass of cheap competitors sit at $13-17 (littlefindsco 16.99, newbeeoo 13.99-16.99, aussie-pet 13.17, twolinda 15.99).
- Paw Guardian offer: free shipping ("Free Shipping" link description), 90-day money-back guarantee (ad 1419403263687298), 3 variants (bundles), up to 60% OFF Black Friday framing (ad 863323466173050), "200,000+ dog owners" social proof (ad 1419403263687298; unverified claim).

## Angles and mechanisms
- Creative insights (72 AI-analysed ads, creative_insights.json): hook Fear 41.7%, Demonstration 15.3%, Curiosity 12.5%; angle Pain 58.3%, New Mechanism 13.9%; BOF 61%; Problem Aware 52.8%, Product Aware 45.8%; motivation Fear of Loss 70.8%; Problem/Solution 93%.
- Mechanisms in the copy:
  - "Under the gums" / bacteria below the gumline: brushing and chews only scrape the surface (ads 3013220405530900, 1542336076815049).
  - "Leaky gums" (FR ad 833701122635750): a vet from the Royal Veterinary College (name given in the copy; unverified) says rebuilt protective barrier stops bacteria entering the bloodstream; ends in liver, kidney, heart damage. "Natural formula created by a vet", 80% of dogs have dental disease by age 3.
  - Avoid the $900 vet cleaning (ads 2006543786796746, 863323466173050).
  - No brushing battles, spray on food once a day (newest ads 1419403263687298 and four near-identical siblings; "works along the gumline, smell is actually gone, not just masked").
  - Listicle hook "3 dog-dental hacks (for under $10)" (ad 1542336076815049).
- Funnel: advertorial (paw-guardian.co/pages/advertorial-page-...; ad 3013220405530900) plus direct-to-PDP ads with `?trybe=` tracking variants, which shows heavy creative testing.

## Winners and how long they ran (all ended; no old ad is still active)
| ad id | window | days | format | EU reach | EU spend |
|---|---|---|---|---|---|
| 2006543786796746 / 1977733896117970 / 1542336076815049 / 863323466173050 | 2025-12-05 to 2026-05-29 | 175 | image x3, video x1 | 16k to 120k | EUR 186 to 1,376 |
| 3013220405530900 (advertorial, "Brushing might be making teeth worse") | 2025-12-05 to 2026-05-27 | 173 | video | 203,638 | EUR 2,341 |
| 833701122635750 (FR advertorial, vet warning) | 2025-11-15 to 2026-04-19 | 155 | video | 326,225 | EUR 2,689 |
| 825615377044187 (FR advertorial) | 2025-11-15 to 2026-04-16 | 152 | video | 170,778 | EUR 1,400 |
EU spend per ad is small (the top ad is EUR 2.7k), so the leader wins on volume of creatives (2,001 active), not on one hero ad. The longest runs are the advertorial videos with the "gum barrier" mechanism and the Black Friday image offer. Note the Black Friday copy ran as an evergreen ad for 175 days.

## Spend direction (trend_summary.json, 2026-08-22 to 2026-11-19)
- Paw Guardian = the whole market (market advertisers 2, same spend): est. daily spend $1,200 to $1,800 (+50%), peak $2,600 on 2026-09-05, trough $1,100 for 2026-09-27 to 2026-10-09 (active ads fell from 2,030 to 1,484 on 2026-09-26), recovered to $1,800-1,900. Ads total 3,339 to 5,587, active 1,631 to 2,001 (peak 2,127 on 2026-11-18), started in last 30 days 805 to 1,091.
- Read: growing and volatile, mid-size ($1.2-2.6k/day EU/UK estimate, GB-concentrated). Market revenue band est. $250-330k/month (modelled; no sales data). Stage "scaling". Only EU/UK spend is visible, so true total spend is higher.
- Competing sprays are not scaling: Furaqua declining, newbeeoo and littlefindsco stale, newer entrants (pupdose, denwild, twolinda, aussie-pet, australianpaws) are at 4-6 ads and appeared in the last 8 weeks, which shows copycats are arriving now, mostly at $13-45.

## Concentration and moat
Extreme concentration: Paw Guardian has about 90% of active spray ads. Moat is weak: no patent, formula is a white-label 1688 product (below), the moat is only creative volume, advertorial funnels, a claimed 200,000 users, and Black Friday positioning. No retail presence found. A $3-$17 clone economy is forming below it (littlefindsco, newbeeoo, aussie-pet at 13-17), which caps price perception for a similar bottle.

## Market sophistication (Schwartz)
Stage 3 to 4 inside the US/UK English market. The basic claim (spray cleans teeth, no brushing) is already common and sold at $13-17, so buyers need a mechanism: Paw Guardian is already on mechanism ("under the gum", "leaky gums", "rebuilds the barrier"), with 13.9% New Mechanism ads and 41.7% fear hooks. Awareness: problem-aware 53%, product-aware 46%. A new entrant needs either a new mechanism or a different avatar/market; a plain "no-brush tartar spray" claim is stage 3 and commoditised.

## Sourcing and margin (sourcing.json)
Generic white-label: 1688 listing "Dentaclean for Dogs & Cats Pet Oral Spray" by 广州市喜颜化妆品有限公司 (Guangzhou, a cosmetics maker), offer 1028400468092. Unit $1.12, $0.84 at 1,000 units, MOQ 1, est. shipping $2.9, plus 3 alternative suppliers listing the same oral spray (unit costs unknown). The product name on 1688 is literally "Dentaclean", so the competitor's brand is the supplier's name: anyone can buy the same formula. Gross margin 96.6% at $55.99 (Brandsearch figure, before fees); break-even ROAS 1.12, break-even CPA $50.03 (their estimate; I think the real break-even is higher once you add payments, returns under a 90-day guarantee, and real shipping). Even at a $29-35 price margin stays above 85% on product cost. Logistics: small liquid bottle (probably ~30-50 ml), no battery, no sizing; liquids can need non-air or special-line shipping, and an oral product for animals carries regulatory/claims risk (health claims such as "removes tartar", "stops bacteria entering the bloodstream", and vet endorsements are medical claims; Meta and UK/EU rules can flag them).

## Gaps
1. Unserved languages/markets: German, Spanish, Italian, Dutch, Nordic. Paw Guardian EU reach outside GB is under 6% in total (IE 0.8, FR 0.7, ES 0.5, PT 0.5, DE 0.3...). There is no dedicated local-language spray store in DE/ES/IT/NL; the only EU-currency spray is carispray.eu at about $3/day. Dog ownership and 45+ female skew are strong there, though I could not measure demand beyond ads.
2. US/CA/AU: not measurable for spend; many $13-45 clones sit there, so likely contested.
3. Unused angles: cats specifically (the leader sells to "dogs/cats" but ads speak to dog parents), small-breed / senior dogs, post-vet-cleaning maintenance, "stop vet scale-and-polish costs under anaesthetic" with a real vet-style credibility in local language, subscription/refill (no recurring offer seen in the copy), men/gift avatar (22% male).
4. Unused avatar: owners of toy breeds and older dogs (high dental disease) and cat owners.

## Read: is there room?
Qualified yes, only as a new-market/new-language play. In GB/US English you would fight one entrenched leader with ~2,000 live ads and a pile of $13-17 clones, with no formula edge (same white-label). The room is in a non-English EU language with no local seller, at a mid price ($29-39) with a differentiated mechanism and a compliant (non-medical) claim set. Risk: medical-claim policy, regulatory wording, and the lack of any measured demand outside GB.
