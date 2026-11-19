# Scout brief (shared by all scouts)

## Goal
We run a dropshipping/DTC operation and build a new store per product, so niche doesn't matter. We are looking for **products** (not brands) worth launching, with evidence that someone is spending profitably on them. A wrong pick costs real ad spend, so a short list of well-proven candidates beats a long list of plausible ones. There are no category restrictions: if stores run it on Meta, it's allowed.

## Tools
Use the Brandsearch MCP tools. Load the schemas first with ToolSearch, e.g.
`select:mcp__Brandsearch__search_products,mcp__Brandsearch__get_product,mcp__Brandsearch__get_product_trend,mcp__Brandsearch__get_market,mcp__Brandsearch__get_product_sellers,mcp__Brandsearch__search_meta_ads,mcp__Brandsearch__get_meta_ad_comments,mcp__Brandsearch__get_product_ads,mcp__Brandsearch__get_meta_ad,mcp__Brandsearch__get_products_by_urls,mcp__Brandsearch__get_product_by_url`

Known facts (from Step 0, see research/_step0_tools.md):
- search_products returns product cards with `ads` (total, active, last_30d, first_advertised_at, est_daily_spend_usd), `market` (sellers, active_ads, price range, new_sellers_30d, country_count, est_daily_spend_usd, lifecycle_stage: emerging/scaling/peak/saturated/declining) and a revenue band. Spend figures are EU/UK estimates only. Max page_size 25.
- get_product_trend(product_id, days ≤ 90) gives a daily series of the store's and the market's ads and estimated daily spend. Use it to judge rising vs decaying.
- Comment text (get_meta_ad_comments) exists only for SOME Instagram-matched ads, and never for Facebook-only matches. Comments are our edge, so **every candidate needs a comment probe**: find 1–3 of its ads that have an Instagram match (search_meta_ads with `landing_page_url` = the product URL or `brand_ids` = the store + `adspy_platform=instagram`), then call get_meta_ad_comments with page_size=1. An empty result is free. Record how many comments the API reports (`pagination.total`) per ad probed.
- search_meta_ads ignores `fields`, so responses are large; use small page_size values.
- One creative often appears as several rows (same copy, same adspy figures). Count it once.

## Budget (hard)
- At most **300 Brandsearch credits** for your whole run (1 credit per product card, ad row, seller row or comment returned; get_product/get_product_trend = 1). Keep page sizes small. Track your running spend in your notes.
- Do NOT call transcribe_ad, analyze_ad, get_original_post, download_ad or any generation tool. No paid AI calls.

## What qualifies
Signals of real, profitable spend on a **product**:
- ads running a long time (60+ days) with several versions/ads still active
- meaningful and rising estimated spend/reach, ideally from more than one store selling the same product (`market.sellers` ≥ 2 with active ads)
- recent launch-and-scale (first advertised recently, ads_30d high, spend growing in the trend)
Discount: giveaways/contests, brand-awareness ads, retail/omnichannel brands (sold in supermarkets), unique branded products that a dropshipper can't source (e.g. a famous brand's own formula), services, digital goods, and markets that are 'saturated' or 'declining' unless the trend shows a fresh climb.

## Output
1. Save the raw tool responses you rely on as JSON files under `research/_scouts/<your-slice>/raw/` (one file per call is fine; name them so they are traceable, e.g. `products_page1.json`, `trend_<product_id>.json`). Write them with the Write tool. The files need the full response, not a summary.
2. Write `research/_scouts/<your-slice>/candidates.md` with **up to 10 candidates**, best first. For each:
   - product (generic name of the thing, e.g. "self-cleaning slicker brush for dogs") + the product card id(s) + market.id + product URL
   - stores selling it (brand_ids) and how many have active ads
   - the justifying numbers, copied from the tool: total/active ads, ads_30d, first_advertised_at, market est daily spend, lifecycle stage, price range, country_count, and the trend direction from get_product_trend (start → end values over the window)
   - comment probe: ad ids probed, adspy IG comment counts, comments available via API (total)
   - one line on why it qualifies and one line on the main doubt
3. A short "rejected in this slice" list (name + one-line reason) so it isn't re-researched.
4. Your final message: the candidate list in compact form (product, ids, key numbers, comment availability), plus your credit spend. Keep it under 700 words. No claims without a number or id behind them.
