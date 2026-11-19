# Momentum scout brief (round 2, 2026-11-19)

## Goal
We run a dropshipping/DTC operation and build one store per product. The operator wants to **ride momentum**: products whose advertising **started or accelerated in the last 30–60 days and is still climbing now**. Copycats piling in counts as a POSITIVE signal here (others see it working), as long as spend is still rising and no single seller owns the market. There are no category restrictions.

The products below were already researched and the operator rejected them, so **do not return them or close variants**: anything listed in `research/_CANDIDATES.md` (shortlist and rejected list), which includes vibration alarms, pet hair gloves, pet tartar spray, wood repair wax, titanium pans, upholstery wet vacs, bird touch lamps, EMS foot mats, neck stretchers, electric callus removers, portable bidets, wedge pillows, collagen wands, magic water colouring books, wine openers, pet memorial necklaces and birthstone necklaces.

**Round 3 addition:** also exclude everything already in `research/_momentum/MOMENTUM_SHORTLIST.md` (shoehorn, zip compression socks, LED trifold mirror, joint-relief ring, water filter straw, comfort bra, lymph drops, jawline gum, the Q4 necklaces/dolls/projector, Venzora, etc.). The operator picked the joint-relief ring and the zip-up compression socks: problem/solution health and comfort products for adults and seniors. Weight your search toward that kind of product, but don't restrict to it.

## Tools
Brandsearch MCP. Load the schemas first with ToolSearch:
`select:mcp__Brandsearch__search_products,mcp__Brandsearch__get_product,mcp__Brandsearch__get_product_trend,mcp__Brandsearch__get_market,mcp__Brandsearch__search_meta_ads,mcp__Brandsearch__get_product_by_url,mcp__Brandsearch__get_products_by_urls,mcp__Brandsearch__get_similar_products,mcp__Brandsearch__get_product_sourcing,mcp__Brandsearch__search_tiktok_ads`
Read `research/_step0_tools.md` first. Key facts: search_products cards carry `ads` (total, active, last_30d, first_advertised_at, est_daily_spend_usd) and `market` (sellers, active_ads, new_sellers_30d, est_daily_spend_usd, lifecycle_stage, price range, country_count). Spend is EU/UK-estimated only. get_product_trend(product_id, days ≤ 90) gives the daily series for the store and the market (advertisers, est. daily spend). search_meta_ads ignores `fields`, so keep page_size small. Ad comments are almost never available. Skip comment probes this round.

## Momentum test (required for every candidate you return)
Pull get_product_trend with days=60 and report the market's **est. daily spend and advertiser count at day −60, −30, −14, −7 and today**. A candidate qualifies only if:
- the market's spend or advertiser count is up strongly over 30 days (≥ 2×), AND
- the last 14 days are still flat or up (it hasn't already peaked and rolled over), AND
- total market spend today is meaningful (≥ ~$500/day EU est.), or it has ≥ 3 advertisers with active ads.
Then classify the momentum driver: **evergreen** (problem/solution, use-anytime), **winter-seasonal** (cold, heating, winter clothing) or **Q4-gift** (Christmas gifting). Report it; don't reject on it. Note that it's 19 Nov, so a Q4-gift product launched in ~7 days needs EU-fast shipping to land before Christmas.

## Budget (hard)
At most **300 Brandsearch credits** for your run. No transcribe_ad, analyze_ad, get_original_post, download_ad or generation calls. No Trustpilot.

## Output
1. Save the responses you rely on under `research/_momentum/<your-slice>/raw/`. Copy key field values verbatim, and label condensed files as condensed.
2. Write `research/_momentum/<your-slice>/candidates.md` with **up to 8 candidates**, best momentum first. For each:
   - generic product name (what it physically is)
   - card id(s), market.id, product URL
   - sellers: total / with active ads / new in 30 days, and the top 3 sellers with their active ads
   - the trend table (spend + advertisers at −60/−30/−14/−7/0)
   - price range, countries/languages served, and one line on the hook/angle from the leader's ad copy
   - momentum driver (evergreen / winter-seasonal / Q4-gift), sourcing read (generic and sourceable vs branded), and the main doubt
3. A "seen but rejected" list, one line each.
4. Final message (≤ 600 words): the compact candidate list with the trend numbers, plus your credit spend.
