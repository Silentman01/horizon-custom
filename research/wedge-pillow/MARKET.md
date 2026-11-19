# MARKET: wedge-pillow (Intimacy Support Pillow, 27 deg wedge)

Source: Brandsearch pulls on 2026-11-19, raw/condensed files in `market/`. Credits used: about 100 of 250. No generation, no transcripts, no Trustpilot. Raw files are CONDENSED (values copied verbatim, images/urls trimmed); `market/build.py` regenerates sellers.csv and stats.json.

## Verdict up front
Real, proven demand, but one seller owns the market and the market is peaking and now flat or slowly decaying. The spend is behind the INTIMACY angle, not sleep or reflux. A late entrant has little room unless it takes a differentiated angle or an unserved language.

## Market size
- Seller count: 19 per the market card (20 distinct brands in the member list; `market/stats.json`). 11 brands have active ads, 9 have zero. 11 of 20 sell in a local language (FR, ES, IT, DE, NL, SV, PT-BR, FR-CA).
- Look-alike markets (get_similar_products and search_products): myvelaa.com_14952164426096 (19 sellers, 255 total ads, 34 active, declining, ~$1/day); aveonfr.com_9606170869973 (10 sellers, declining); lunarastore.es_15724936855935 (4 sellers, declining, 0 active); cozycloudco.com_9684850409623 (1 seller, 168 ads, 101 active, 129 started in 30 days, first 2026-08-11, emerging, $52.75). Two or three of these are the same product under other cluster ids. Total distinct stores selling the intimacy pillow is roughly 30 or more, almost all clones.
- Countries (EU/UK transparency, get_product_audience, 4,758 ads): GB 68.4%, FR 8.8%, DE 3.8%, ES 3.4%, BE 3.3%, IT 2.7%, NL 2.3%, DK 1.7%, PT 1.5%, IE 1.0%. Audience 75.1% men, 24.9% women; ages 35-44 39.7%, 45-54 26.5%, 25-34 19.3%. No US or CA spend split exists in the data. The leader prices in USD and 4 countries are flagged in the market card (country_count 4).
- Local-language sellers: FR (belleaparis.com, shopavena.ca for CA), ES (cosalia-home.com, broeiy.com, elmunz.com), IT (ripozen.com, with ads under page brilocasa.com), DE (slomorning.com, dreamoro.de), NL (harrington-online.com), SV (nodolorix.com), PT-BR (lojazafir.com). Local-language sellers are all small.

## Prices and offers
- Price USD min / median / max across 21 member rows: 35.99 / 50.79 / 124.20 (card says median 54.59 and max 99.99 before slomorning was added). The leader sits at the cheap end: comfysleepers.com 49.99 USD (4 variants). Clones: GB 39.95-39.99 GBP (duettonights, secretpleasurescr), EU 59.95-69.99 EUR, FR/CH 64.90 CHF (belleaparis), DE 115 EUR (slomorning), US prdfr 99.99.
- Offers: leader runs 69% off, "Buy 1 Get 4 Free Gifts" (id 1789119665627613, 2026-11-11, Halloween/Black Friday), 30-night trial ("30 nights to try it", id 1298520482493061). aveonfr: 90-night trial. belleaparis: 30-day money back. So the 49.99 price is the anchor after a "69% off" markdown.

## Angles and mechanism
- Dominant angle is intimacy support for couples, euphemised. Mechanism: 27 deg incline, firm memory foam that does not flatten, waterproof cover, "stop stacking ordinary pillows" (ripozen/brilocasa id 1032521416190160).
- Winner copy (leader, ids 2322333648296176 and 1531237431991100, running from 2026-05-19): testimonial block, "bought it as a bit of a joke ... My partner said it's the best she's ever had", "intimacy feel effortless again".
- Second angle: reconnect/spark. "Bring Back The Spark" (id 1298520482493061, 2026-05-25): "She stopped feeling distant... and started reaching for me again", 30-night trial.
- Third: male-confidence/performance. "She Leaned In & Whispered 'That Felt Incredible Can We Do It Again?' ... Her Ultimate Comfort = Your Unstoppable Confidence" (id 976138665021204, 2026-06-05).
- Current: sale plus social proof, "75k+ Couples Already Made The Switch", "27 deg Lift ... Less Strain, Less Adjusting" (ids 1789119665627613, 2192236514976618).
- AI analysis (26 ads, creative_insights.json): Convenience 57.7%, Desire 15.4%, Transformation 11.5%; pain Confidence 50%, Comfort 23.1%, Health 19.2%; audience Couples 50%; funnel BOF 84.6%; Problem/Solution 80.8%.
- Back/hip comfort for 30-60 year olds is the secondary frame (ripozen/brilocasa: "Dai 20 Ai 60 Anni ... riduce la pressione su schiena, fianchi e articolazioni").
- Sleep and reflux angle is a different, tiny market. search_products "wedge pillow": hiquo.co_9572650680655 (anti-snoring wedge, 1,337 ads, 417 active, 6 sellers, market ~$41/day, saturated, $85.99); davolia.com_7631292923998 (baby reflux, 0 active, market ~$49/day, declining); norles.com_16096223887747 (baby reflux lounger, ~$47/day, scaling). Against the intimacy market's ~$3,400/day, the money is behind intimacy by roughly 80 to 1. The leader's older ads (2025-04..06) were cooling blankets and snore cervical pillows, then it pivoted to the intimacy pillow around 2026-05 (first advertised 2026-05-22).

## Winners and duration
Longest-running pillow ads on the leader's landing URL: 2322333648296176 and 1531237431991100 (start 2026-05-19, 184 days to 2026-11-19; status "active" as returned though end_date 2026-08-15, so treat the run as at least 88 days confirmed, up to 184), 1298520482493061 (from 2026-05-25), 979761628132657 (video, from 2026-05-27), 976138665021204 (from 2026-06-05). Clone ads are short bursts (belleaparis 2026-09-22 to 2026-10-04, ripozen 2026-07-27 to 2026-08-13). 645 ads on the leader's pillow URL alone, 498 of them listed as active-sorted by recency.

## Spend direction
- Market (trend_*.json / history): advertisers 11 (2026-08-22) to 18 (2026-11-19); est daily spend about $4,600 to $3,400, with a peak $5,700 on 2026-09-11 and a trough $2,800 on 2026-10-06. Leader alone: $4,500 to $3,300/day. Active ads still climbing (938 to 2,445) while ads started in last 30 days fell 1,092 to 513.
- Reading: stores are piling in (11 to 18) but total spend is down about 26% from late August and flat since mid-October. Classic early-peak: leader has settled into volume testing, clones are fragmenting spend. Lifecycle label: "scaling".
- Estimate caution: spend is EU/UK-only; the leader prices in USD and may spend heavily in the US that is invisible here. Market revenue band $450k-$600k/month is modelled.

## Concentration
comfysleepers.com holds 4,316 of 4,802 total ads (90.2%) and 2,445 of 2,568 active ads (95.8%) and about $3,300 of $3,400 daily spend (97%). Second place cosalia-home.com about $9/day, ripozen.com about $4/day. No patent or brand moat: the product is a generic memory-foam wedge, the clones are identical products with translated creatives (belleaparis copy is a French translation of the leader's testimonial block). The leader's moat is creative volume (2,445 active ads), pixel data and offer.

## Sophistication (Schwartz)
Stage 3-4. The basic claim ("a pillow for positions") is known; ads sell a mechanism (27 deg lift, firm foam, waterproof), then proof (testimonials, 75k couples) and discount. 84.6% of analysed ads are BOF/product-aware. A buyer needs a new angle (partner comfort, back/hip pain, post-surgery, pregnancy, mobility) rather than a new claim.

## Sourcing and margin
Brandsearch match is a silk pajama listing (wrong); its $11.48 cost, 77% gross margin, break-even ROAS 1.55 and CPA $32.20 are NOT reliable for this product. Plausible real cost for a firm memory-foam wedge with waterproof cover is likely $8-15 landed (unverified). At 49.99 that leaves healthy margin, but the leader's 69% off pricing implies a list price of about $160 and sets a low conversion-price anchor. Shipping: bulky but light foam; no battery or liquid. Meta policy friction (below) is the main cost.

## Meta ad-policy friction visible in seller wording
- Sellers avoid explicit words and say "intimacy", "connection", "comfort for every position", "angles", "closeness". No body parts in copy. "Waterproof" in the product title is the only hint of use.
- The leader runs it from a sleep/bedding page ("Comfy Sleepers is your go-to source for top-rated sleep and bedding products", link_description) mixed with blankets and pillows, not a standalone adult store.
- Clones rotate advertiser pages: ripozen.com ads are served from page brilocasa.com, and its link description sells an anti-snoring store ("Benvenuto su RipoZen, la soluzione definitiva contro il russamento..."), which looks like cloaking friction. Many clone stores show 0 active ads but recent ads (e.g. nodolorix.com 77 ads, 52 in 30 days, 0 active; duettonights 34 ads, 25 in 30 days, 0 active), consistent with takedowns or ad-account churn. Treat the 0-active column on these as friction evidence, not proof.
- Copy edges that could draw reviews: "That Felt Incredible Can We Do It Again?", "Her Ultimate Comfort = Your Unstoppable Confidence", "Upgrade The Way You Love" (id 976138665021204).

## Comment evidence
Probe: the only two Instagram-matched ads in the whole market are comfysleepers 2322333648296176 (33 likes, 2 comments) and 976138665021204 (16 likes, 0 comments). Neither has 5 comments; I called get_meta_ad_comments on 2322333648296176 anyway: 0 comments returned. Nothing found; no raw comment files. See `comments/probe_log.json`. Clone sellers have no IG matches.

## Gaps
- Unserved languages with zero seller: Polish, Danish, Czech, Hungarian, Romanian, Greek, Portuguese-PT, Swedish proper (only a low-activity SV store), Finnish. EU audience reach exists for DK 1.7%, PT 1.5%, SE 0.7%, FI 0.7%.
- Active local-language competition is thin: FR (belleaparis 17 active, shopavena 6), ES (cosalia 14), IT (ripozen 13), DE (slomorning 7, dreamoro 0), NL (harrington 6). All are 2-16 ad stores.
- Unused avatar: women-led purchase (only 24.9% women reached; creatives are male-voiced "she craves more"), older couples 55+ (only 12.8% of reach), back/hip pain, post-surgery, pregnancy support. Unused angle: pure comfort/back-pain framing without sexual cue (safer for Meta), couples gifting.
- Weakness to exploit: offer chaos (69% off to everyone), thin proof (IG comments nearly zero), and a luxury positioning gap (clones all cheap, only slomorning at 115 EUR).

## Read
Room exists only in a niche: a non-English, non-GB market with a differentiated comfort/back-pain angle and clean Meta-compliant copy. A direct clone into GB or the US means fighting a single advertiser running 2,445 live ads at $3.3k/day and an account-ban risk.
