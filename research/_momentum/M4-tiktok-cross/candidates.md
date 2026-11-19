# M4-tiktok-cross candidates (2026-11-19)

Trend = get_product_trend days=60 (Sep 21 to Nov 19). It reflects Meta/EU/UK spend only, not TikTok. TikTok figures are the card fields `ads.tiktok` (this store's TikTok ads) and tiktok_shop_matched. The `market_tiktok_likes` / `tiktok_shop_plays` values are not returned on the cards, so likes/plays are NOT available in the response; only TikTok ad counts are.

Search note: the two requested passes returned almost nothing. Pass 1 (source=tiktok_shop, created_from 2026-08-01, price>=15, sort tiktok_shop_plays) gave 59 results, all weak: single-seller, 0 active Meta ads or "declining" (K-beauty resellers, apparel). Pass 2 (ad_platform=meta,tiktok, market_tiktok_ads_min=5, first_advertised_from 2026-09-01) returned 0 results. Relaxed (no date filter, tiktok_ads>=2-3, new sellers>=1, spend>=300) gave about 30 distinct rows, nearly all saturated/branded. Cross-platform + new is a very thin slice.

## Passing (loosely)

### 1. Message-card "An meinen Schatz" necklace (Halskette, DE/AT) -- jabany.at
- card id: jabany.at_9633289175380 (market.id same). URL https://jabany.at/products/halskette-an-meinen-schatz
- sellers: 6 total, 4 advertising, 1 new in 30d. Store: 133 ads, 32 active, 5 TikTok ads (ads.tiktok=5), 86 started in 30d. Top-3 per-seller split not pulled (budget).
- trend (market): spend/advertisers: -60 (Sep 21) $930/4 | -30 (Oct 20) $700/4 | -14 (Nov 5) $110/4 (data dip Oct 28-Nov 5, likely recording gap) | -7 (Nov 12) $1,400/4 | today $1,500/4. Store: active ads 16 -> 21 -> 29 -> 22 -> 32; spend $44 -> $29 -> $110 -> $66 -> $140.
- 30-day change $700 -> $1,500 (2.1x), last 14 days up, spend $1.5k/day. Advertiser count flat at 4, so the test passes on spend only.
- price 59.95 EUR ($64.75) store; market median $42, range $40-65. Countries: 3 (DE/AT focus). Lifecycle: saturated per Brandsearch.
- hook: sentimental message-card necklace for a partner ("to my love").
- driver: Q4-gift. Needs EU-fast shipping; lands after Christmas by dropship.
- sourcing: generic jewellery plus message card, easily sourced. Doubt: close to the rejected pet-memorial/birthstone necklace family, and the market is labelled saturated.

### 2. Wrinkle-free / non-iron slim fit shirt (FR) -- bellutia.com
- card id: bellutia.com_15635880083800. URL https://bellutia.com/products/chemise-infroissable-a-coupe-ajustee
- sellers: 20 total, 5 advertising, 0 new in 30d. Store: 3,766 ads, 1,445 active, 1,121 started in 30d, 3 TikTok ads.
- trend (market = this store essentially): spend/advertisers: -60 $1,700/5 | -30 (Oct 20) $1,500/5 | -14 (Nov 5) $2,000/5 | -7 (Nov 12) $2,200/5 | today $2,600/5. Active ads 648 | 758 | 1,164 | 1,262 | 1,445. Ads started last 30d 410 | 524 | 883 | 1,098 | 1,121.
- 30-day: spend 1.7x (below 2x), active ads 1.9x, new ads/30d 2.1x; last 14 days clearly up. Counts as borderline pass.
- price 49.90 EUR ($53.89), market $27-54, 20 countries. Lifecycle: scaling. Revenue band $350-470k/mo (market).
- hook: "crease-free" shirt that needs no ironing, fitted cut.
- driver: evergreen (workwear), mild winter fit.
- sourcing: generic non-iron shirts, sourceable; 80 variants (size/colour) is heavy. Doubt: apparel returns, 20 sellers already exist, only 3 TikTok ads.

### 3. Chain/cross pendant (silver) -- sava-amsterdam.com (borderline, fails spend test)
- card id: sava-amsterdam.com_8831396217166. URL https://sava-amsterdam.com/products/cross-chain
- sellers: 28 total, 14 advertising, 5 new in 30d. Store 689 ads, 224 active, 291 started in 30d, 10 TikTok ads.
- trend: spend/advertisers: -60 $3,100/14 | -30 $1,500/14 | -14 $1,800/14 | -7 $1,700/14 | today $2,400/14. Active ads 118 | 79 | 114 | 157 | 224.
- 30-day spend 1.6x, active ads 2.8x, last 14 days up. Spend today is below day -60, so it is a rebound, not a ramp.
- price 49.95 EUR ($54), market median $49, 23 countries. Lifecycle: saturated. Revenue band $330-440k/mo.
- driver: Q4-gift / jewellery. Doubt: saturated, 28 sellers, brand-led (Sava).

## Seen but rejected
- Ciezkomis weighted plush bear (misioterapia.pl_12197808931156): market advertisers 4 -> 19 and spend $680 -> $2,300, but the whole jump happened on Oct 10 (40 days ago); last 30 days only 1.2x. Saturated, 29 sellers, 13 TikTok ads. Fails the 30-day test.
- NOSE PATCHES (vueswiss.com_7320308809918): market $18k -> $22k/day, 3 advertisers, saturated, flat.
- Purple Mouthwash (shop.drdent.co_10200684396824): TikTok-Shop matched, 1,533 active ads, $1.6k -> $1.4k flat/down, started-in-30d falling 918 -> 505, UK only.
- TYMO ring/CurlPro: branded, spend $460 -> $740, 3-4 advertisers.
- Meroda Changing Foundation, Pure NMN, Camp Snap CS-8, Fellwunder brush: branded or on exclusion list.
- Elevateshoes (two cards): saturated/declining, branded.
- Creatine for women (misuplemento.es): saturated, $440/day.
- Voviabags Ciara vintage bag: declining.
- Heatable hoodie (heathoody.com): last ad Aug 28, stopped.
- Anti-roll shaper shorts (tryfemlush.com): 23 sellers but est spend $31/day.
- Hair mask Georgie Mane, Firming oil, wigs, bamboo bra, Hush pillow: spend null/tiny, branded or low.
- Pass-1 TikTok Shop rows (medicube resellers, SteamPulse, Pantysoul, Elegance trousers, techwear windbreaker, etc.): 0 active ads, single seller, declining or emerging with <15 ads.
- 47skin anti-blemish serum, EKKO beater, Bykaer set: single branded sellers.

## Credits
About 125 credits (searches ~105 returned rows plus 7 trend calls). No transcribe/analyze/download calls.
