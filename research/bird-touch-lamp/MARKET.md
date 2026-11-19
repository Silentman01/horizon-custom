# Market analysis: cordless rechargeable bird touch-dimmer lamp (2026-11-19)

Sources: Brandsearch raw/condensed files in `market/` (sellers_raw_condensed.json, ads_condensed.json, sellers.csv built by build.py) and `comments/probe_log.json`. Spend = EU/UK transparency estimate only (no US/CA/AU). Credits used: about 190 of 250. No transcripts, no generation.

## 1. Market size
- Two cards, one product: valotalo.fi_15969209254272 (30 sellers in get_product, 32 in sellers list) and zomesi.com_10546087559451 (36 / 37). Deduped across both lists: **68 stores** (sellers.csv). **20 have active Meta ads** (501 active ads in total). 6 of the 29 stores that started before Oct 1 are still active; 14 of the 39 that started Oct 1 or later are.
- Stage: both markets "scaling" (valotalo market: 272 active ads, 311 total, 5 new sellers in 30d; zomesi market: 139 active, 162 total, 11 new sellers in 30d). Modelled revenue band $0.9-1.2M/mo (valotalo market) and $100-140k/mo (zomesi market); these overlap and are modelled from EU ads, not sales.
- Countries (EU/UK reach share, get_product_audience): valotalo market 313 ads: SE 40.7%, GB 34.5%, FI 17.2%, IT 5.4%, ES 1.7%, DK 0.5%, FR 0.1%, NL 0.1%. zomesi market 133 ads: IT 99.8%, FR 0.2%. Audience: women 74-78%, top age 55-64 (24.7% / 29.4%), 65+ about 25%. No US data available.
- Local-language active sellers: FI valotalo.fi (47 active ads); SE belysningshuset.se (26), wove.se (5); NO belysningshuset.com (19), no.wove.se (2); DK belysningshuset.dk (1); UK glowstead.co.uk (60) + shopglowstead.com (139) in English; IT zomesi.com (119); FR maisonhomelynofficiel.com (12), lejolicomptoir.com (2); NL vivaluce.nl (5), luomi.nl (1); PT kabannasoficial.com (5). Stores with no active ads: DE nordenmark.de, lampista.de, wondersparks.de, glanzagipfel.de, birdzenliving.com.
- Look-alike markets (get_similar_products): spherestandouts.com_15964137128276 (US $27, 8 sellers, 12 ads, first ad 2026-11-18, emerging), samargo.com_11056381329747 (FR, 22 active, scaling, $51/day), plus declining ones (clausby.dk 0 active, birdzenlamp.com 0, flitsko.com 0, terracosy.com 0 active, 9 sellers).

## 2. Durable decor or Q4 spike?
Both, and it is not a gifting spike. Evidence:
- The product has existed since late 2025: birdzenliving.com first ad 2025-11-26 (id 835963072484616), then a Jan 2026 wave of 7 stores starting Jan 2026 (birdzenliving.com 197 ads, boutali.com 118, rayon-zen.fr 98, lalampade.com 72, armonie-home.fr 34, nevavo.nl 14). All of those now show 0 active ads. Best old-wave ad: birdzenliving.com 2855485197974730 (DE, Jan 5 to Mar 2 2026, 365,246 reach, EUR 3,670 spend).
- Spring/summer was a low tail, not zero: birdzen-it.com has run since 2026-01-26 and still has 51 active ads, but only about $110-150/day (get_product_trend). Its market had 25-28 advertisers at $160-760/day from Aug 22 to Nov 19 (peak $740 on Aug 30, $160-170 in early Oct, $550 on Nov 14, $320 on Nov 19).
- The explosion is Oct-Nov: valotalo market advertisers 1 (Oct 9) -> 3 (Oct 16) -> 7 (Nov 18); spend $200 (Oct 16) -> $600 (Oct 25) -> $6,700 (Nov 18), with noise ($3,700 Nov 10, $2,000 Nov 12). zomesi market $30 (Oct 25) -> $760 (Nov 19), advertisers 1 -> 11. New stores by first-ad month: Aug 3, Sep 4, Oct 15, Nov 24 (to Nov 19).
- Gifting is not the main angle: of 39 AI-analysed ads in the valotalo market, Gift Appeal/Giftability are 2.6% each; Convenience 46.2%, Lifestyle 35.9%. The seasonal hook is dark evenings (zomesi 1430150172396115: "Sono le cinque e fuori è già buio"), i.e. a dark-season decor effect, which fades in spring (inferred from the Jan-Mar wave dying out by March, not measured).
- Verdict: a winter decor product with a year-round small tail. Expect the Nordic/UK/IT surge to peak around Nov-Dec and the stores that started late (Nov) to be killed by Feb-Mar, as the Jan wave was. No pre-October data in look-alike markets shows a bigger earlier peak.

## 3. Sellers, leaders and spend
| Store | Active / total ads | First ad | Est. daily spend | Notes |
|---|---|---|---|---|
| shopglowstead.com | 139 / 166 | 2026-10-19 | $340 | EN, GBP 30.99 ($39.36); also sells Terra solar spotlight (ads since Jun 17) |
| glowstead.co.uk | 60 / 66 | 2026-10-27 | $3,500 | GBP 22.99 ($29.20), same Cora page |
| belysningshuset.se / .com / .dk | 26 + 19 + 1 | 2026-10-23 / 11-11 | $2,400 (.se) | SEK 349 ($33.16), NOK 349, DKK 229; same video ad id across domains |
| zomesi.com | 119 / 119 | 2026-10-24 | $760 | IT, EUR 34.90, also sells suction hooks (agarri) |
| valotalo.fi | 47 / 47 | 2026-10-09 | $400 | FI, EUR 34.90, in_stock false, last ad seen 2026-11-09 (scout lead is stale) |
| birdzen-it.com | 51 / 122 | 2026-01-26 | $150 | NL-language BirdZen copy, long tail |
Concentration: top 3 stores by active ads = 63% of the 501; Glowstead's two domains alone = 199 (40%). All Cora-named stores (glowstead, belysningshuset, valotalo, nordenmark.de, toiae.fr, vivaluce "Picora", Vilniaus Prekes) use the same page copy translated (3000 K, 15 hours, silver/gold/light/dark wood, free delivery, 30-day returns), so one operator or one shared supplier/agency kit. No brand moat, no patent, no review moat seen.

## 4. Price and offer
- Core price band (55 stores priced $15-60): min $16.50 (addtovibe.com), median $33.20, max $54.00 (luomi.nl). Typical: EUR 34.90 (zomesi, valotalo, maisonhomelyn, allomya, elovya), GBP 22.99-30.99, SEK/NOK 349, DKK 229. Cheapest active-ish: toftens.com $21.07, slatesage.com $26.40, westandhale.com $26.95, kqhomelight.com $24.95, addtovibe.com $16.50.
- Price-war signals: Glowstead undercuts its own .com store by about 26% on the UK domain and spends 10x per day on it; AliExpress-style listing slugs ("1pc-led-touch-control-bird-lamp-art-deco-3-levels...") on jonesmarketshop, slatesage, rayon-zen, addtovibe; stage "scaling" with 24 new stores in 19 days of November.
- Data caveat: 11 rows show $129-1,299 (myss.se 289, shoplykke.dk 245, klivra.se 349, hendalla.com 349, flixmart.dk 275, shoplycka.se 395, daglykke.dk 249, valholm.com 179.99, modadnia.com 129.99, casasgael.com.br 174, vensaa.com 1299). Those are mostly SEK/DKK/PLN/BRL amounts labelled USD by the tool; treat them as local currency, not premium positioning.
- Offers seen on the lamp: free (tracked) delivery, 30-day returns/money back, 4 finishes. No bundle, BOGO or gift-pack on the lamp ads (the 2+2 offer on zomesi is for another product). That is an open lever.

## 5. Angles and long-running winners
- Dominant (Cora network, ids 982136891600175 Glowstead, 1615953616835880 Belysningshuset, 1776574116844302 Valotalo): product demo + convenience: "One tap on its head. Then it glows." (tap on head turns on, same finger dims; warm 3000 K "never bluish"; cordless USB, 15 hours; nursery/windowsill/bedside "no socket nearby").
- Zomesi (ids 1430150172396115, 1649792676890120): problem/solution on the dark evening vs. ceiling light: "Spegni il lampadario. Accendi l'uccellino".
- Old BirdZen angle: wooden bird, 3 light levels, aroma diffuser, hang on tree/plant, "ideal gift", 12 h (birdzen-it.com 1751508259152425; birdzenliving.com 2855485197974730).
- AI facets (39 ads): hook Demonstration 53.8%, Aspiration 20.5%; strategy Problem/Solution 61.5%; funnel TOF 43.6%, BOF 38.5%; audience Homeowners 61.5%.
- How long winners ran: 982136891600175 Sep 30 -> Nov 14+ (45+ days) EUR 23,205 spend, 2,017,849 reach; 1615953616835880 Sep 23 -> Nov 11+ (49+ days) EUR 4,949, 520,484 reach; valotalo 1776574116844302 Sep 27 -> Nov 9 (43 days) EUR 1,278; zomesi 1430150172396115 Oct 23 -> Nov 9 (17 days) EUR 2,548; old wave birdzenliving.com Jan 5 -> Mar 2 (56 days); birdzen-it.com ads running since May 9.

## 6. Sophistication (Schwartz)
Stage 3 trending to 4. Buyers already know "a cordless bird lamp"; the leaders sell the mechanism and spec (touch-head dim, 3000 K not bluish, 15 h, four finishes) and every Cora clone repeats it. New entrants win on creative execution, offer or audience/language, not on the basic claim. Awareness mix: Product Aware 41.0%, Solution Aware 25.6%, Unaware 15.4% (AI sample of 39).

## 7. Sourcing and margin
Brandsearch: `sourcing_available` false on both cards, so no supplier cost. Not verifiable here: the generic AliExpress-style listings and the identical Cora kit across stores indicate a commodity supplier item. Retail ex-VAT at EUR 34.90 is about EUR 28 (25% VAT, assumption), so a typical landed cost would need to be checked with a supplier quote. Shipping: Li-ion battery (air restrictions/surcharge), fragile wood/metal-look body, small parcel, 4 variants. Both stores' ads promise free tracked delivery, which the operator must absorb.

## 8. Gaps
- **Germany**: 4+ DE stores, none with active ads, and DE is absent from the reach list (zero EU share), despite birdzenliving.com's 56-day DE winner in Jan-Mar. Largest unserved language market.
- **Spain/Portugal-EU, Poland, Czechia, Baltics**: ES is 1.7% of reach with no Spanish-language store in either list; modadnia.com (PL) and terracosy.com (CZ) are inactive. France has many stores but almost no scaled spend (0.1-0.2% reach).
- Unused angles: gift bundle/2-pack (none seen), elderly/55+ reading and nightlight safety (audience is 55+ and 75% women, ads sell lifestyle), a stronger offer (2+1 free), kids' room/nursery as an explicit angle (only a mention in the copy), outdoor/garden/balcony use.
- Unused avatar: 65+ (24-26% of reach, no copy speaks to them), men gifting a partner.

## 9. Comment evidence
Probe result: **none**. Two search_meta_ads probes (adspy_platform=instagram, sort_by=adspy_comments) over the 8 top sellers, then over 20 active and old-wave stores, returned: 0 ads with >=5 Instagram comments, and 1 Instagram-matched ad in total (zomesi.com 1352731096290045, suction hooks, 0 comments). 0 calls to get_meta_ad_comments, 0 comments pulled. The bird-lamp ads run as dark posts with no matched organic post, so there is no voice-of-customer from comments. Log: `comments/probe_log.json`.

## 10. Risk summary
Seasonal winter peak; copycat flood (24 stores started in Nov; most fail after 1-6 ads); price war ($16-34); three operators hold 63% of active ads; shared creative kit means near-zero differentiation; no sourcing data, battery shipping; no comment/review data to read buyer language.
