# MARKET: zipper compression socks (zip-compression-socks), pulled 2026-11-19

Raw/condensed files: `market/` (market_*.json, trend_nonnull_rows.json, ads_nordvera_group.json, similar_and_searches.json, audience_and_brand.json, sellers.csv via build.py). `comments/probe_log.json`. All files marked "condensed" where shortened; values verbatim. Credits used: about 95 of 250. No transcribe_ad, no Trustpilot.

## Product confirmed
Compression/support socks with a side zipper, for people who cannot pull on normal compression stockings (arthritis, bad back, swelling). Ad copy (nordveranordic.se ad 900104949486049, start 2026-08-22): "kompressionsstrømper med lynlås i siden. Du åbner, glider foden i, lukker igen. 3 sekunder. Uden hjælp." and "Samme kraftige kompression som apoteket", "Til dem der opgav almindelige strømper".

## 1. Is the Nov 13 jump real? No. It is a measurement artifact.
- Market first appears in Brandsearch history on 2026-10-05 (2 advertisers). There is no data before that, so the "60-day trend" is really 45 days.
- Market series: 10-20: 3 advertisers, $82/day; 11-05: 5, $100; 11-11: 5, $200; 11-13: 7, $1,500.
- The jump is the day nordverashop.de ($890/day appears 11-13), and the .at/.be domains ($450, $700) entered the cluster. The sum of store estimates is $2,678 vs the market's $1,500, so the numbers are not additive and are model outputs, not observed spend.
- Those new "sellers" are the same advertiser (see 2). The ads under them started Aug 1 / Aug 22 (below), long before the domains were linked.
- Real spend signal: get_brand nordvera.dk: spend_30d $11,299, spend_60d $22,598 (exactly 2x, so a flat extrapolation), 116 active / 260 total ads. About $380/day, not $1,500. Largest single ads: 900104949486049 EU reach 612,490 / EU spend EUR 5,690 over ~70 days; 1898898851067288 reach 648,573 / EUR 6,025 over ~90 days. Each is roughly EUR 65/day. Good but not huge.

Trend table (ads total / est. daily spend), from trend_nonnull_rows.json. -60 (Sep 20) has no data for anyone.

| date | market advertisers / $day | nordveranordic.se | nordvera.no | nordverashop.de |
|---|---|---|---|---|
| -60 Sep 20 | null | null | null | null |
| -30 Oct 20 | 3 / $82 | 16 ads / $74 | 22 ads / null | none |
| -14 Nov 5 | 5 / $100 | 28 / $94 | 53 / null | 4 ads / null |
| -7 Nov 12 | 5 / $200 | 50 / $190 | 53 / null | 11 / null |
| 0 Nov 19 | 7 / $1,500 | 58 (57 active) / $630 | 53 active / null | 25 / $890 |

Direction: growing in ad count (one operator adding creatives and countries), spend step is partly artifact. Note nordvera.no and nordverashop.de copies of the top ads show status "inactive", end dates Oct 30-31, while the market table lists them active, so even the "active" counts are unreliable.

## 2. Distinct operators: effectively ONE (Nord Vera), plus small fry
- Ad ids 1898898851067288, 900104949486049, 1348341300845841, 2251383488949474, 1376484817314471, 2904206446629254 appear under nordveranordic.se AND nordvera.no AND/OR nordverashop.de, same creative, same Danish copy, all pointing to https://nordvera.dk/products/kompressionsstromper.
- The real origin is nordvera.dk (created 2026-07-31, DK, ships to Denmark, avg price $42.36, 116 active/260 total ads). It is not even in the 7-seller market. Localised mirror stores: .se (SEK 799), .no (NOK 799), .de/.at (EUR 69), .be (EUR 79.99), same vendor "NORD VERA".
- Others: netoviaclean.com (FI, EUR 34.99, 14 ads, first 2026-10-04, last 2026-10-12, $8/day, 5 "active": near dormant), belviawear.se (SEK 599, 12 ads, all one day 10-28, 0 active), joumko.com (FR, EUR 39.99, 4 ads, 0 active), shimerlya.com (FR, EUR 39, 1 ad, 0 active). The last three launched Oct 28 - Nov 13 and have zero active ads: copycats that tested and stopped.
- Real count: 1 sustained operator, 1 dormant Finnish, 3 abandoned tests.

## 3. Market size, countries, languages
- 9 stores in the cluster (7 "advertisers"), 5 domains of one operator. Price USD: min 37.79, median 73.51 (all 9; market's own median over 7 = 56.91), max 86.39. Operator charges $74-86 equivalent list (799 SEK/NOK, EUR 69/79.99) with "Buy 1 get 1 free" and, on NO, "40 % Rabatt". Netovia FI is the cheap one at EUR 34.99.
- EU reach by country (177 ads): SE 39.9%, DE 26.3%, BE 19.8%, AT 13.6%, FI 0.2%, FR 0.1%. DK and NO are not in EU/UK data (DK is in the EU, but nordvera.dk ads are probably under a different cluster, the NO ones are outside), so they are invisible here.
- Audience: 65+ 55.4%, 55-64 29.1%; men 59.3%, women 40.7%.
- Local-language sellers: DK (Nord Vera), NO, SE, DE, AT, BE-NL, FI (Netovia, dormant), FR (joumko, shimerlya, dead).

## 4. Offers and angles
- Offer: "KØB 1 PAR FÅ 1 PAR GRATIS", "Gratis fragt + 90 dages tilfredshedsgaranti", NO: "40 % Rabatt" (ads 1649865809907897, 1475877957739450).
- Angle: difficulty of putting on stockings, arthritis/bad back ("Det er umuligt, hvis du har gigt eller en dårlig ryg"), pharmacy-strength compression, "for those who gave up on normal socks". Mechanism: side zipper, 3 seconds, no help. Sophistication: the claim "compression helps swelling" is old; the zipper is the new mechanism that makes the ad work (Schwartz stage 3 for compression, stage 2-3 for the zipper: still novel in Nordics, but copied by 20+ stores elsewhere).
- Scarcity gimmick: ad 3026932664304792 (nordverashop.de, 2026-08-22 to 10-23): "SIDSTE CHANCE ... stigende toldsatser gør det desværre umuligt for os at fortsætte importen ... Når lageret er væk, er det væk for altid." A fake liquidation claim while the product is still advertised on 5 domains. Platform and consumer-law risk; do not copy.
- Longest runners: 1898898851067288 and 1348341300845841 start 2026-08-01 (about 110 days if still live; .se copy shows end 10-30); 900104949486049 and 1376484817314471 start 2026-08-22 (89 days). So the oldest zip winner in this cluster is under four months old.

## 5. Look-alike and durability evidence
Zip compression socks have been tried again and again elsewhere, and each wave died within 1-2 months:
- DE: align-heath.com (ads 2026-04-27 to 06-19, $62/day, 37 active when last seen), myillorya.com (06-17 to 07-22, 52 active), navella.de (7+9 ads one day 11-10, 0 active), lorenavia.com (10 ads 10-28, 0 active). All gone or stopped.
- FR: forstepz.com (ads 06-18 to 06-22), elaimei.fr, hopzip.fr (11-09, 0 active), joumko/shimerlya. UK/US/GR/PL/IN: roxley, saintport (7 ads), trynordvia, kreovo.pl, euzincare.gr, deltapicks.in (11 active, EUR/INR cheap), venzipa.com (07-09 to 07-17), healthysteps.store (03-19 to 04-04). Almost all "declining", under 25 ads.
- Conclusion: zip socks are a commonly cloned product; only Nord Vera has scale and it is 3.5 months old.
- Non-zip compression socks are durable: everstridesocks.com "Original Wide Compression Socks" first ad 2025-10-03, 2,454 ads, 158 active, market 34 sellers, $640/day, 21 countries (stage declining; ~13 months); "Bamboo Wide Compression Socks" first 2026-01-09, 2,911 ads / 1,891 active, 27 sellers, $440/day; onecompress.com bamboo footsleeves first 2025-11-04, 1,031 ads/570 active, 38 sellers. Also FR: aunolia.com (400 ads, first 2025-12-26), buyoxalys.com (453 ads, first 2026-01-04, declining). So plain/wide/bamboo compression socks have 12+ months of multi-seller spend, which confirms category demand; the zip is a feature variant of an evergreen category, not a one-off trend. The big evergreen markets are mostly US (country_count 1 for bamboo wide).

## 6. Sourcing, margin, logistics
- sourcing_available = false for this product, so no 1688 match from the tool. Unverified estimate (not from tool): unit cost of zip compression socks ~USD 2-4, shipping from CN 2-5. At EUR 35-69 for 1 pair (or 2 pairs on a BOGO), gross margin before ads/fees is plausibly 70-85%, but 1+1 free halves it.
- Complexity: sizing (6 variants, calf circumference), returns on wrong size, medical-claim wording ("same compression as the pharmacy", swelling), zip durability. Elderly buyers: higher customer-service load, 90-day guarantee used as a lever.

## 7. Concentration and moat
One operator holds essentially all active ads (nordvera.dk 116 active). No brand moat, patents or reviews seen; the copy is generic. The moat is spend scale and local-language stores in 6 countries.

## 8. Gaps
- Unserved languages: NL/Flemish (nordvera.be is the only one, small), FR (all attempts dead, but France is big: could be re-tried with a real offer), UK/IE English zip (6 tiny sellers, 1 ad each), PL (kreovo.pl, 1 ad), IT/ES (serenityshop.eu ES non-zip, 55 ads, $5/day), CH, CZ/HU/Baltics. Finland (Netovia dormant, $8/day) is open but small (FI reach 0.2%).
- The Nordics + DACH are taken by the same operator. Unused angles: women-led (the operator's audience is 59% men 65+), nurses/standing jobs, post-surgery/bed-ridden, caregiver-buys-for-parent ("buy for your mother"), pregnancy swelling. Unused avatar: adult children shopping for ageing parents.

## Comment evidence
Probe: 2 batched searches (zip cluster brands incl. nordvera.dk and look-alike leaders everstridesocks, onecompress, serenityshop, buyoxalys, saintport, euzincare, arlevi, hopzip, venzipa, deltapicks) with adspy_platform=instagram: total 0 matches both times. get_meta_ad_comments not called (nothing to call). No comments exist in the tool for this niche; credits spent on the probe: 2 searches, 0 comments. Voice-of-customer must come from elsewhere.

## One-line read
Closed in the Nordics/DACH to a single aggressive operator already at 116 active ads, the jump is noise, zip clones elsewhere have all died within weeks, so room exists only as a new-language, new-avatar play (FR/UK/NL) with real risk of being a fad clone of a 3.5-month-old product.
