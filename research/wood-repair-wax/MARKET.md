# MARKET: wood-repair-wax (FixStik-type wax repair sticks), 2026-11-19

Raw files in `research/wood-repair-wax/market/` (condensed files are labelled; `build.py` regenerates sellers.csv and the stats). Credits used: about 100 of 250. No transcribe_ad used (copy shows the mechanism).

## 1. Market size and countries
- The starting card (kitchik.com_15048615002452) is a true single-seller cluster (`market.sellers` = 1), but the category is not. Look-alike markets found (`similar.json`, `sellers.csv`, 17 listings, 16 distinct stores): 7 listings have active ads, only 3 stores matter (kitchik.com, torkstoretools.com + torkstoree.com.br).
- Kitchik holds 370 of the 483 active ads across all listed sellers (77%). Next is the Tork Store pair: 42 active (US, torkstoretools.com_8746097737816) + 37 (BR, torkstoree.com.br_10408086733092) = 79 active, 103 total, stage "scaling", est $250/day, revenue band $34-45k/mo for the market. The rest have 0-4 active ads.
- Countries (EU/UK reach share, audience.json, 791 ads): SE 30.8, DK 29.5, PL 7.8, GB 7.3, DE 5.7, FI 5.4, BE 4.3, IT 3.9, NL 3.0, AT 1.2, FR 0.8. Ad-library language counts for kitchik (search_meta_ads `languages`): SV and DA (most of the 471 indexed), NO, EN-GB, NL 16, FI 12, DE 35, PL 8, FR 6, IT 4. Price in NOK (279 kr), so Norway is the home store; localised paths /sv-se /da-dk /de-de /pl-pl /fi-fi /nl-nl /it-it /fr-fr /en-gb.
- Local-language sellers: SV: kitchik, plus hemmafixet.com TraFix (149 ads, first ad 2026-01-12, 0 active, declining) and restorelab.se (20 ads from 2026-10-22, 0 active). NL: nordvella.nl "Nordvella FixStik" (1 ad on 2026-11-11, 0 active). DE: dodeb.com / novastarz.shop "NuGrain" (5 and 3 ads, 0 active), pilon.ch (11 ads, ended 2026-01-09), studiomoreandless.com (2 ads). EN-UK: nestifymall.com (1 ad). PT-BR: torkstoree.com.br (37 active). EN-US: torkstoretools.com, getluxgrove.com (2 active), svchrono.com, istahly.com (2 each).
- US/CA/AU spend is not visible (EU/UK data only); US presence confirmed only by the Tork Store USD listing.

## 2. Prices and offers
- Price (USD, from listings with a reliable price): min $12.69 (nestifymall.com, 9.99 GBP), median $29.97, max $49.95 (pilon.ch). Kitchik $25.67 (279 NOK; 299 NOK for the White variant = $27.51). Tork US $44.99 for a 20-colour kit; BR $35.82 (199 BRL). Per-country kitchik prices from ad copy: 199 kr DK (ad 1668638447498411, Apr), 299 kr SE (1114731050864425), 279 NOK, EUR 26.99 DE (1747741689609157), 89 zl PL (26647186671619298).
- Offers seen in ad copy: 10 colour sticks, "30 seconds", Black Friday "up to 50% off" (ads 986424031045017, 1612278714002692), 60-day money-back and "20,000+ happy customers" (IT ad 2522626781583263, FR 2213908559327717). No bundle/BOGO visible in ad copy (not checked on the site).

## 3. Angles and mechanisms
- Dominant angle (kitchik, almost every ad): price anchor vs tradesperson: "carpenter wants 2,000 kr, do it yourself in 30 seconds for 299 kr" (ids 2104511826944370, 1114731050864425, 1650055496206005, 1668638447498411, 1324971013159894). Mechanism line: "wax sticks melt into the wood; fill the scratch, scrape excess with a card, polish with a cloth".
- Secondary: colour-surface angles (black furniture: 1007391075591205, 1507582043646159; white painted wood/frames: 3176668732722732, 2810867049247785); "you won't believe it works until you see it" demo (1514908813458503); fear-of-damage angle (FI 1811243156678862: moisture gets in, wood darkens); social proof 20,000 customers + 60-day refund (IT/FR).
- creative_insights (only 5 analysed ads): Comparison hook 60%, Demonstration 40%, angle Cost Savings 80%, Problem/Solution 100%, homeowners, product-aware, BOF 100%.
- Not used by kitchik in what we saw: the "rental/deposit" or "moving-out" avatar, pet-scratch avatar, floor-laminate-only positioning, kit-of-fills for chips/gaps (Tork 20-colour kit and "filler duo" go there), gift or "pro finish" angle.

## 4. How long winners ran
Kitchik churns creatives fast; end dates are scrape dates for active ads, so these are the longest closed runs among the 5 highest EU-spend ads: 1668638447498411 (DA) 2026-04-04 to 05-13 = 39 days, EUR 5,042, reach 542,759; 27194418166850196 (SV) 05-21 to 06-29 = 39 days, EUR 3,376; 1650055496206005 (SV) 04-23 to 05-31 = 38 days, EUR 4,220; 1114731050864425 (SV) 05-01 to 05-25 = 24 days, EUR 4,534; 2104511826944370 (SV) 08-16 to 09-02 = 17 days, EUR 5,910, reach 621,459 (largest). No ad in the sample ran longer than about 6 weeks. The script (same carpenter line) is recycled across ~800 variants, so the "winner" is the script, not one ad.

## 5. Spend direction
- Kitchik store (trend_kitchik..., 2026-08-22 to 11-19): total ads 510 to 800, active ads 357 to 370 (dip to 252 on 2026-09-26 after 403 on 09-25, then rebuilt), new ads in last 30 days 203 to 239, est daily spend about $1,400 to $4,400 (steps: 2,400 Sep 4, 3,300 Sep 13, 3,000 Sep 26, 3,400 Oct 10, 3,500 Nov 6, 4,300-4,400 Nov 14-16). GROWING, with Black Friday ads already live.
- The "market" series for the cluster reads $2,100 to $2,400, lower than the store's own $4,400 (inconsistent in the source; treat spend as an order of magnitude). Brandsearch revenue band for kitchik: $530-700k/mo (modelled from ads, not sales).
- Tork Store market: first non-null spend point $28/day on 2026-11-13, $250/day on 2026-11-19; scaling but small. TraFix SE (the earlier Swedish seller) ended: 0 active, declining.

## 6. Concentration and moat
One dominant seller (kitchik, 77% of active ads, about 95% of known spend). No hard moat: generic product (standard wax crayon sticks), no patent, no brand equity beyond claimed "20,000 customers"; the moat is ad volume and localised funnels in 9 languages. Copycats in SE (TraFix Jan 2026, RestoreLab Oct 2026), NL (Nordvella "FixStik" Nov 2026) and DE (NuGrain) have all stalled at 0 active ads, which suggests a copy without kitchik's creative volume does not hold.

## 7. Market sophistication (Schwartz)
Stage 2-3. Wax repair crayons are an old item, so the plain claim "fills scratches" is not new; buyers still need the quick cost-comparison hook and the "melts in, 10 colours match your wood" mechanism. Kitchik competes on price anchor + demonstration, not a novel mechanism. A new differentiated mechanism (e.g. colour-matching guide, hard-wax heat melt, kit that also fills gaps) would move this to stage 3-4 and is not yet used in Nordics (not seen in sampled ads).

## 8. Sourcing and margin
get_product_sourcing: unit $0.18, MOQ 1, est shipping $4, retail $25.67, gross margin 99.4% before shipping and fees, break-even ROAS 1.26, break-even CPA $20.45, verdict profitable. Caveat: the auto-match is a 2mm paint marker (1688 offer 1035533644351), not a wax-stick set; a real 10-colour wax set will cost more but stays far below $5. Product is small, light, non-fragile, no battery or liquid: easy shipping. Colour matching of wood tones and returns on mismatch are the practical risks.

## 9. Gaps
- Language/country with weak or no coverage: Germany (kitchik only 35 ads, 5.7% reach; DE local sellers dead), Netherlands/Belgium (16 kitchik ads; Nordvella 1 ad), France (6 ads), Italy (4 ads), UK (EN-GB ads exist but small, nestifymall 1 ad, UK reach 7.3%), Austria/CH. Best unserved: DE/AT/CH or NL/BE; second: FR, IT.
- US/CA/AU: Tork Store only, at $44.99 (we cannot see its spend split).
- Unused avatars: renters/landlords, pet-owner floors, furniture flippers, "pro kit" for decorators. Unused mechanism: colour-matching proof/test.
- Seasonal: Black Friday/Q4 already used by kitchik.

## 10. Verdict
Room exists only if we localise outside the Nordics and bring more creative volume or a sharper mechanism than the generic carpenter-price script. Kitchik is growing and strong in SE/DK/NO; head-on Nordic entry is not advised.
