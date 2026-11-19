# MARKET: portable wet vacuum / upholstery and carpet spot cleaner (DE focus)

Data date 2026-11-19. Raw/condensed files in `market/`. Credits used: about 90 of 250 (estimate; no usage call made). No transcribe_ad, no Trustpilot.

## Headline
This is a one-seller market in Germany, not an open one. RYER (ryer.de) is the whole demand signal: 2 stores in the Plus market, 388 active ads, ~$3,700/day est. EU spend, revenue band $500k-670k/mo for the market (modelled, `market_ryer.de_9079563419992.json`). Everything else that looks similar is either small copycats (0 active ads) or cheap chemistry at $15-20.

## Market size
- Plus market `ryer.de_9079563419992`: 2 sellers (ryer.de 1,007 ads / 382 active; ryershop.de 69 / 6), 4 countries per product card, EU reach DE 78.8% / AT 21.2% (`audience.json`). Both stores have German copy only.
- RYER also runs a second product, Hybrid (wet vac + steam, `ryer.de_15613169762648`): 166 ads / 159 active, ~$1,900/day, $230k-300k/mo seller-scope band, stage emerging, first ad 2026-07-18. Also Compact (99.99 EUR, 8 ads, 0 active) and Mattvätt Plus (Swedish, 2 ads, 0 active).
- Copycats seen: aurevia-shopping.de SpotFlow (149.99 EUR, 9 ads, 0 active, first ad 2026-11-07, DE), jet-force.fr Steam Force (179.99 EUR, 2 ads, 0 active, FR, first ad 2026-11-07), eziclean.ma (MA, W100 at $119.40, 2 active), two other MA/DZ stores with 1 ad each. `get_similar_products` returned no real look-alike markets (`similar.json`).
- Look-alike stores total about 6 outside RYER; only RYER is a live scaler. Local-language sellers: German (RYER, Aurevia), French (Jet Force, EZIclean, small), Swedish (one dead RYER listing). No English-language seller of this machine surfaced in the data (US spend is not covered by Brandsearch, so absence in EU/UK data does not prove a US gap).
- Adjacent: cheap no-machine cleaners, e.g. munichsunny.com "No-Wash Carpet & Sofa Cleaner with Brush" $19.99, 10 sellers, 26 active ads, $290/day, 6 new sellers in 30 days; Profoam (bestideasuk.co.uk, 14.99 GBP, 68 ads / 18 active, $24/day); detailrs.nl $15.54. And premium wet/dry floor machines (Tineco, Dreame $400-700). Those are different products.

## Price and offer
- Plus 139.99 EUR ($151.19), Hybrid 179.99 EUR ($194.39), Compact 99.99 EUR, Aurevia 149.99 EUR, Jet Force 179.99 EUR, EZIclean W100 $119.40. Machine price band 100-195 EUR, median about 150 EUR. Cheap chemistry $13-47.
- RYER offer stack in the ads (all verbatim in `ads_ryer.de.json`): 56% off + 30 EUR shop credit (ids 1047794624430694, 2905933063088740, 1404521325196939, 941327622095712, 1667782570916527), free shipping (1047794624430694), 30-day money back, 4-year warranty, "meistverkaufter Nasssauger in Deutschland", "über 15.000 zufriedene Kunden" (2285999288491125). Earlier 50% off urgency image (557250773920378). So the 139.99 EUR is a permanent "56% off" anchor (implied list ~318 EUR).

## Angles and mechanisms
Creative insights (50 analysed ads, `creative_insights.json`): hook Demonstration 48%, Fear 20%, Shock 18%; angle Pain 36%, Cost Savings 20%, Convenience 18%; funnel BOF 92%; awareness Product Aware 88%; pain Time 42% / Health 40%; audience Homeowners 92%; motivation Fear of Loss 52%, Relief 42%; Problem/Solution 98%.
Ad copy confirms the pattern:
- "Dirty-water reveal": show the filthy water that comes out of the couch/mattress (2285999288491125 "Ich bin schockiert, was aus meiner Couch kam"; 2905933063088740 Opa's armchair; 1404521325196939 autumn cleaning; 1667782570916527 mouldy car).
- Hygiene/allergy fear: mites, mould spores, sweat, skin flakes, allergens (928296522557814 "Schütze dich vor Allergenen?", 1047794624430694).
- Power spec: 9,000 Pa (Nov 2025 ad 824785320173143) rising to 15,000 Pa (2026 ads) and 18,000 Pa on Hybrid. A spec race is visible.
- Cost saving: skip 200-300 EUR car detailing (1667782570916527); "600 EUR vacuum never got this" (2905933063088740).
- No chemistry, tap water only; dry in 30 minutes.
- Hybrid: steam 100 C, 99% bacteria, landlord/move-in story (941327622095712), mattress story (2374026773129114).
- Seasonal hooks: Black Friday, summer, autumn cleaning.
Mostly UGC-style first-person video with a demo; one image ad among the long runners.

## Winners and duration
- Longest runners (all RYER, inactive now): 928296522557814 2024-11-18 to 2026-09-25 (~676 days, EUR 15,330 spend, 1.55M reach); 891426529844513 2024-12-16 to 2026-05-09 (EUR 19,632, 1.99M reach); 1708739086337564 2024-11-18 to 2026-02-17 (EUR 17,558). All "Schütze dich vor Allergenen?" video, landing on ryershop.de/products/plus. Image 557250773920378 ran 2024-11-18 to 2025-11-19 (~366 days).
- Biggest currently active by spend: 1047794624430694 (started 2026-07-23, EUR 22,969, 2.32M reach), 2905933063088740 (2026-06-24, EUR 11,788), 1404521325196939 (2026-10-08, EUR 11,260 in 5 weeks), 941327622095712 (Hybrid, 2026-10-22, EUR 10,042 in 3 weeks).
- RYER has been advertising this product since at least Nov 2024 (about 12 months before today), earlier than the 2025-12-28 "first advertised" on the card (which belongs to the ryer.de store; the older domains were ryershop.de and teppichreiniger-ryer.de).

## Spend direction (`trend_*.json`, `market_*.json`)
- Plus market daily spend: $3,500 (Aug 20) -> $3,500-3,600 through Sep 23 -> $1,500 on Sep 26 -> $1,400 early Oct -> $1,700 Oct 18 -> $2,700-2,800 Oct 27 -> $2,200-2,500 early Nov -> $3,700-4,000 Nov 16-17. Active ads fell 610 -> 231 on 2026-09-26 (mass shutdown, probably ad-account or creative reset), then rebuilt to 382. New ads in last 30 days 362. Net: flat-to-growing over 90 days ($3,200 -> $3,700 store), with a 3-week dip, and recovering into Black Friday. Seasonal peak (Black Friday) is imminent, so the current number is flattered.
- Hybrid: $1,000 -> $560-780 (Sep-Oct) -> $1,900 (Nov 17); active ads 47 -> 159. Growing, new, and the part of RYER that is expanding.
- Combined RYER est. spend now ~ $5,600/day.

## Concentration and moat
Extreme: one operator (2 domains) is the only scaler. Moat is not patents or retail; it is brand ("meistverkaufter Nasssauger in Deutschland" claim), 1,000+ ads of creative testing, about 12 months of ads, 15,000-customer claim, 4-year warranty and a 56%-off anchor. Because the machine itself looks like a white-label injector-extractor (assumption; no supplier match was available), the product is copyable, which Aurevia and Jet Force did in Nov 2026, but both have 0 active ads and "declining" stage: copycats so far fail to scale.

## Sophistication (Schwartz)
Stage 3 to 4. The basic claim (a machine that sprays water and sucks dirt out) is known; 88% product-aware ads, 92% BOF. The differentiation is the mechanism proof (dirty-water demo) plus a Pa-spec race (9,000 -> 15,000 -> 18,000) and a new mechanism add-on (steam 100 C in Hybrid). A new entrant needs a new mechanism or a new proof, not another "we remove stains".

## Sourcing and margin
Brandsearch has no supplier match (`get_product_sourcing` 404 sourcing_unavailable for Hybrid and Aurevia; `sourcing_available: false` on Plus and Aurevia). So no data-backed unit cost. Not from the data, treat as assumption to verify: Bissell Little Green-type injector-extractor units are typically sourced in the roughly $25-45 range at volume, 3-5 kg boxed, mains-powered or battery. A 139.99 EUR sell price would leave a gross margin well above 60% before ads and shipping, but that needs a real supplier quote. Shipping complexity: bulky (about 5 kg), has a water tank, motor, possibly a battery; EU plug (Schuko, 230 V) for DE/AT, UK needs a Type G plug; US 120 V needs a different model. Returns risk: 30-day money-back is table stakes in the market. Break-even guidance: RYER's CPA tolerance is unknown; at 140 EUR with ~60% margin the product can carry a CPA of up to roughly 80 EUR gross, which is plausible for a considered purchase, but unverified.

## Gaps
- Language: no seller in the data in NL, PL, ES, IT, DK, SE with live ads. Dutch/French/Polish/Spanish locals are only shown with cheap chemistry (detailrs.nl, ultracoat.eu PL leather cleaner). France: Jet Force 2 ads, 0 active. EU reach is 78.8% DE / 21.2% AT, with FR and IT 0%.
- Avatar: RYER targets homeowners/mattress/allergy/car, 65.8% women, 35-44. Under-served on the data: pet owners (2% of analysed ads), parents/baby, renters ("Vermieter" angle only on Hybrid), car resellers. Audience is mostly women but Aurevia skews 68% male, 25-34 (car/mechanic frame).
- Angle: no ads in the sample show a comparison against the cheaper chemical cleaners or a rental machine (Kärcher rental), nor a pet-odour angle.

## Comment evidence
Comment probe done (step 3b): zero Instagram-matched ads for ryer.de, ryershop.de, teppichreiniger-ryer.de, aurevia, jet-force, munichsunny, bestideasuk, eziclean, and the `q=Nasssauger` search returned 0 (`comments/probe_log.json`). `get_meta_ad_comments` was therefore not called and no comments exist. The market's voice-of-customer has to come from elsewhere; none of it is in this file.

## Read
Room only if we differentiate, not a clone. The category has proof of demand (RYER ~$500-670k/mo market band, 12 months running), but one German operator owns it and copycats are dying at 0 active ads. The viable openings are an untapped language/country (NL, FR, PL, IT, UK) with local copy, or a clear mechanism/avatar twist (pets, steam, renters, car). A straight German Plus-clone is not recommended.
