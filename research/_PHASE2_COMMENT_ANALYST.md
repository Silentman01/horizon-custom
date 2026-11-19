# Comment analyst brief

## Goal
We run a dropshipping/DTC operation and build one store per product. We're deciding whether to launch the product named in your task, and how to sell it. Comments are the only place the market talks back to an ad, so your job is to show what real buyers say: intent, objections, failures, uses, who buys it, and where they want it shipped. A wrong "launch" costs real ad spend, so finding that the evidence is weak is a good outcome. Report it honestly.

## Tools
Brandsearch MCP. Load the schemas first with ToolSearch:
`select:mcp__Brandsearch__search_meta_ads,mcp__Brandsearch__get_meta_ad_comments,mcp__Brandsearch__get_product_ads,mcp__Brandsearch__get_meta_ad,mcp__Brandsearch__get_market,mcp__Brandsearch__get_product,mcp__Brandsearch__search_products,WebSearch,WebFetch`
Read `research/_step0_tools.md` first. Key facts:
- get_meta_ad_comments(ad_id, page_size ≤ 50, page) returns `text`, `like_count`, `created_at` (unix seconds) for the Instagram post matched to the ad. Coverage is partial: many ads return 0 (free). Facebook-only matches never return comments.
- Find the product's Instagram-matched ads with search_meta_ads: `landing_page_url=<product url>` and/or `brand_ids=<store>` (+ `q=<product words>`), `adspy_platform=instagram`, `sort_by=adspy_comments`. Repeat for EVERY store in the market that sells the product (the store list is in your task, or get it from get_market(market_id)).
- The same creative often shows up as several ad ids with identical adspy figures. Pull each creative's comments once.

## Budget (hard)
- At most **450 Brandsearch credits** (1 per comment returned, 1 per ad row). Probe with page_size=1 first; pull up to 50–100 comments per ad, and aim for 10–20 ads across all sellers. Stop once you've spent the budget.
- No transcribe_ad, analyze_ad, get_original_post, download_ad or any paid AI/generation call.

## Coverage warning and fallback (read this)
The scouts probed about 60 Instagram-matched product ads, and only 3 returned comment text. Expect most products to have **no** API comments. Work in this order:
1. **Exhaust Brandsearch first (cheap: empty calls are free).** For EVERY seller in the market (get_market) and in look-alike markets of the same product (search_products q=<generic product words>, top 5 by ads), list their Instagram-matched ads (search_meta_ads brand_ids=<store>, adspy_platform=instagram, sort_by=adspy_comments, page_size 10) and probe each one with page_size=1. Log every probe (ad id, adspy IG comments, API total) in `comments/probe_log.json`.
2. **If fewer than 100 API comments exist in total, add a voice-of-customer fallback from public sources** using WebSearch/WebFetch:
   - **Do NOT use Trustpilot** (operator instruction, 2026-11-19). Don't fetch it, quote it or count it.
   - Amazon product reviews or Q&A for the same generic product (search "<generic product> amazon reviews"), and Reddit threads about the product type (old.reddit.com, or reddit search pages)
   - YouTube/TikTok pages only if the comments are present as text in the fetched page
   Save every fetched page's relevant text verbatim to `comments/web_<source>_<n>.md`, with the URL and fetch date at the top. Each quote you extract goes into `comments_all.jsonl` with `source` = the URL and `channel` = "trustpilot" / "amazon" / "reddit" / "instagram_api", and an id = `<channel>_<n>`.
   - Never invent or paraphrase a quote. If a page doesn't load, say so in the probe log and move on.
   - Send only generic product words and competitor domains to search engines. Never send anything about us.
3. Keep channels separate in every count. Reviews are written AFTER a purchase, so they speak to product failures, objections and buyer identity, but **not** to purchase intent from ad viewers. Report the intent ratio as "n/a (no ad comments)" when there are no API comments; don't compute it from reviews.

## Steps
1. Make the folder `research/<product-slug>/comments/`. Save each raw comments response (full JSON as returned) to `raw_<ad_id>_p<page>.json`, and the ad list you chose from to `ads_index.json`. Write `ads_meta.json` with one entry per ad you pulled: ad id, brand_id, start_date, status, EU spend/reach, adspy IG likes/comments, and the first 200 chars of the ad copy.
2. Write a Python script `research/<product-slug>/comments/build.py` that merges every raw file into `comments_all.jsonl`, deduplicated by comment id. Each row: id, ad_id, brand_id, text, like_count, created_at (ISO date).
3. Tag every comment. Read them yourself (you are the classifier) and write `tags.jsonl` (one line per comment id: `{"id":..., "tags":[...], "objection":"<label or null>", "country":"<or null>", "note":"<short>"}`). Tags, one or more:
   `purchase_intent` (wants to buy, asks price/where/how to order, "ordered", "need this"), `shipping_geo` (asks if it ships to a country / is available in a country), `objection` (with a short label: price, scam/trust, doesn't work, safety, quality, size/fit, etc.), `product_complaint` (it broke, didn't work, side effect), `service_complaint` (shipping delay, refund, support), `use_case_unadvertised`, `buyer_identity` (who they are or who they buy for: "my mum", "as a nurse"), `saturation` ("seen this everywhere", "cheaper on Temu/AliExpress/Amazon", "dropshipping"), `comparison` (vs another product), `seeding_suspect` (generic praise with no detail, e.g. "love it 😍", "amazing product!!"), `tag_friend` (only @user mentions), `noise`.
   Generic praise without detail counts as probable seeding: tag it `seeding_suspect` and leave it out of intent counts.
4. Write `research/<product-slug>/comments/count.py`, which computes from tags.jsonl + comments_all.jsonl: counts per tag, intent comments ÷ total comments pulled, intent ÷ total IG engagement (likes + comments reported by adspy for the ads pulled), objection label counts, country counts, and the per-ad split by comment age (first 30 days of the ad vs later, using created_at vs the ad's start_date) for intent/objection/complaint shares. Run it and save its output to `counts.json`. **All numbers in your report come from this output, not from memory.**
5. Write `research/<product-slug>/COMMENTS.md`:
   - coverage: ads probed, ads with comments, comments pulled, brands covered, credits spent
   - counts per tag (from counts.json) and the intent ratios
   - top 5 objections with counts and 1–2 verbatim quotes each (quote exactly, with comment id)
   - product failures that survive in the comments (where the competitors' promise breaks), with quotes + ids
   - use cases and buyer types the ads don't target (compare with the ad copy in ads_meta.json)
   - countries people ask for shipping to, with counts
   - exact phrases buyers use for the problem and for the desired result (verbatim, with ids, in the original language + an English gloss when it isn't English)
   - sentiment over the ad's life (if the dates allow it)
   - caveats: brands delete negative comments, so absence of complaints proves little; how much of the engagement is tag-a-friend or seeding
6. Final message (≤ 500 words): coverage numbers, intent ratio, top 3 objections, the single most useful failure/gap, saturation-signal count, and your one-line read: is there real buying intent here? Every number must come from counts.json.
