# Market analyst brief

## Goal
We run a dropshipping/DTC operation and build one store per product. We're deciding whether to launch the product named in your task, and how. You map the competitive market: who sells it, where, at what price and offer, with which angles, and whether spend is growing or decaying. A wrong "launch" costs real ad spend, so finding that the market is closed or decaying is a good outcome. Report it honestly. There are no category restrictions.

## Tools
Brandsearch MCP. Load the schemas first with ToolSearch:
`select:mcp__Brandsearch__get_product,mcp__Brandsearch__get_market,mcp__Brandsearch__get_product_sellers,mcp__Brandsearch__get_product_trend,mcp__Brandsearch__get_product_ads,mcp__Brandsearch__get_meta_ad,mcp__Brandsearch__search_meta_ads,mcp__Brandsearch__get_product_audience,mcp__Brandsearch__get_product_creative_insights,mcp__Brandsearch__get_similar_products,mcp__Brandsearch__get_product_sourcing,mcp__Brandsearch__search_products,mcp__Brandsearch__get_brand`
Read `research/_step0_tools.md` first. Key facts: spend figures are EU/UK estimates only (no US spend split). get_market(market_id, history=true) lists every seller plus the market's daily advertisers/spend series. get_product_trend(days ≤ 90) gives the daily series. get_product_audience covers EU/UK reach by country, age and gender. get_product_creative_insights exists only for some products (a 404 is free). get_similar_products finds look-alike markets (other clusters selling the same thing; check it, because the same product is often split across several markets). get_product_sourcing gives supplier/unit economics when `sourcing_available`.

## Budget (hard)
- At most **250 Brandsearch credits**. Use small page sizes.
- You MAY use transcribe_ad on at most **2** of the longest-running video ads (1 AI credit each), only if the ad copy doesn't show the mechanism. No analyze_ad, get_original_post, download_ad or generation calls.

## Steps
1. Folder `research/<product-slug>/market/`. Save every raw response you rely on as JSON (`market_<id>.json`, `trend_<id>.json`, `sellers.json`, `ads_<brand>.json`, `audience.json`, `similar.json`, `sourcing.json`, …).
2. Build `research/<product-slug>/market/sellers.csv` with a Python script (`build.py`) from the raw files: brand_id, url, price_usd, total_ads, active_ads, first_advertised_at, est daily spend, countries if known. Compute counts with code.
3. For the top 3–5 sellers by active ads, pull 5–10 of their longest-running and newest ads (search_meta_ads brand_ids=<store>, landing_page_url or q, sort_by=longest_running and recent; small page_size). Note each ad's id, start date, status, days running, EU spend/reach, format, headline, and the angle/mechanism/offer in the copy.
3b. **Comment probe (needed, cheap).** For every seller with active ads (and the top look-alike stores), list its Instagram-matched ads (search_meta_ads brand_ids=<store>, adspy_platform=instagram, sort_by=adspy_comments, page_size 10) and call get_meta_ad_comments(ad_id, page_size=1) on each ad with ≥ 5 adspy IG comments. Empty results are free. Save every probe (ad id, brand, adspy IG comments, API total) to `research/<product-slug>/comments/probe_log.json`. If ANY ad returns comments, pull up to 150 comments in total across those ads (page_size 50), save them raw to `comments/raw_<ad_id>_p<n>.json`, and list them in MARKET.md under "Comment evidence" with verbatim quotes + comment ids, tagged as purchase intent / objection / complaint / shipping-geo / use case / buyer identity / saturation. Don't use Trustpilot.
4. Write `research/<product-slug>/MARKET.md`:
   - market size: number of stores selling (all look-alike markets included), how many advertise actively, in which countries (EU/UK from audience data; others from currency/TLD/copy language), and which language markets have a **local-language** seller
   - price points (min/median/max) and offers (bundles, BOGO, free gifts, guarantees, shipping promises), with seller ids
   - angles and mechanisms used, with ad ids; which ones the long-running winners use
   - how long the winners have run (ad ids + days)
   - spend direction: trend start → end values for the market and leaders (from the trend/history series); growing, flat or decaying
   - concentration: is one seller dominant? Does it have a moat (brand, patents, retail, unique formula, huge review count)?
   - market sophistication (Schwartz): is the basic claim still new, or do buyers need a new mechanism to care? Justify it with the ad copy.
   - sourcing/margin: unit cost if available, typical sell price, rough gross margin, shipping complexity (size, fragility, batteries, liquids, sizing)
   - gaps: unserved country/language, unused angle, unused avatar
   - every claim cites an id or a number from the raw files
5. Final message (≤ 450 words): sellers count, leaders and their spend trend, price range, dominant angle, sophistication level, best unserved market, sourcing/margin read, and your one-line read: is there room for us?
