# Step 0: Brandsearch tool check (2026-11-19)

Account: Outscaler-level Adspy access (comments endpoint works). Usage at start: 59 requests / 909 credits used this month, 10,000 request limit (daily + monthly), overrun disabled. AI credits: 1,400 (transcribe/analyze). Original-post quota: 50/month (1 used in this test).

## What exists
| Need | Tool | Status |
|---|---|---|
| Product-level demand (sellers, ads, est. daily spend, lifecycle stage, revenue band) | search_products, get_product, get_market | Yes. Spend is an EU/UK-transparency-based estimate. |
| Spend trend | get_product_trend (≤90 days, daily), get_market(history=true) | Yes: ads / active ads / est. daily spend for store + market |
| Sellers + prices | get_product_sellers / get_market | Yes, ≤50 sellers |
| Ads per product | get_product_ads (newest first, max 50) | Yes |
| Ad detail | get_meta_ad | Copy, dates, status, EU reach, EU spend total. **No per-country spend split** |
| Country data | product `market.country_count`, `market_country` filter, get_product_audience | EU/UK only: share of reach by country, age and gender. **No US/CA/AU spend** |
| Instagram engagement (Adspy) | search_meta_ads `adspy` block | Likes, comments, views of the matched organic post |
| Comment text | get_meta_ad_comments | text, like_count, created_at (unix), anonymised. 1 credit per comment |
| Creative angles | get_product_creative_insights | Only on the minority of products whose ads were AI-analysed |
| Transcripts | transcribe_ad | 1 AI credit each |

## Limits found
- **Comment coverage is partial.** In a test of 6 Instagram-matched ads with 30–950 comments, only 2 returned any comment text (gisou 154 of 193; druni 146 of 450k). natulim (948), exchange-life (589) and hawkstone (438) returned 0, even after the original post was opened. An empty page costs nothing, so agents probe ads cheaply and keep the ones that have comments.
- **Facebook-matched posts give no comments** (pfotenmond ad 1474555894478090: 354 FB comments, 0 returned). Comments are Instagram only.
- Comments are anonymised: no author, @handles read `@user`. Tag-a-friend comments therefore show up as bare "@user".
- `fields` on search_meta_ads is not honoured; responses are large.
- One creative appears as several ad rows across brand domains/duplicates with the same post stats. Dedupe by post (identical adspy figures + copy).
- Spend figures are EU/UK only (Meta transparency). US-only sellers look small or empty on spend.
- No sales data. Revenue is a modelled band from ads.
