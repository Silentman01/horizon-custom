# Brandsearch MCP: tool reference

These are the MCP tools (`mcp__claude_ai_Brandsearch__*`). They were checked against
https://docs.brandsearch.co/mcp, https://docs.brandsearch.co/ads and the live tool schemas
(Oct 2026). Load them with ToolSearch (`select:mcp__claude_ai_Brandsearch__get_brand_ads,...`)
before calling. The procedure that uses them is in `07-ads-research-brandsearch.md`.

## Who calls it
Only the **master** calls Brandsearch. Results land in its context, or as harness files under
`~/.claude/projects/<project>/<session>/tool-results/`. Sub-agents work from those files. This avoids
duplicate spend and keeps results out of sub-agent contexts.

## Resolve the brand
| Tool | Key params | Notes |
|---|---|---|
| `get_brand_by_url` | `url`, `fields` | Use the competitor URL. Returns the brand record; its `id` is the cleaned domain. |
| `lookup_brand` | `q`, `limit`, `type` | Free-text search by name, domain or handle. Use it when the URL lookup fails. |
| `get_brand` / `get_brand_summary` | `brand_id` | The summary returns profile, active Meta ads and products in one call. |
| `get_brand_advertisers` | `brand_id`, `limit` | Meta pages advertising for the brand. |
| `get_brand_ads_aggregates` | `brand_id`, `status`, `from_date`, `to_date` | Media mix, funnel, CTAs, demography, spend summary. **1 credit.** |

## Pull ads
**`get_brand_ads`**: one brand's ads.
- Params: `brand_id` (domain, required), `platform` (`meta`|`tiktok`|`instagram`, required), `q`,
  `is_image`/`is_video` (strings `"true"`), `status` (`active`|`inactive`), `sort_by`, `sort_order`
  (`desc` by default), `fields`, `min_spend`/`max_spend`/`min_reach`/`max_reach`,
  `meta_page_created_from/to`.
- **There is no page or page_size parameter in the MCP. It returns 20 rows per call** (`pagination.total`
  shows the real count). To get other rows, change `sort_by`, `sort_order` or `status`.
- Every row includes `total_active_time` and usually `image_original_url`. That makes it the best
  source for longevity and media.

**`query_meta_ads`**: JSON-body search, `body={...}`.
- Body: `brand_ids` (JSON array or CSV, cap 200), `q`, `is_image`/`is_video` (JSON booleans), `status`,
  `page` (1–1000), `page_size` (1–100), `fields`, `sort_by`, `sort_order`, plus the filters below.
- Unknown body fields return `400 validation_error` naming the field. Fix the field; don't retry blindly.
- Returns **all rows**, with pagination. Some rows have no `image_url`/`image_original_url` (only a
  thumbnail, which may 404). Its dates can be truncated compared with `get_brand_ads`. Always merge
  the two by id.

**`search_meta_ads`** takes the same filters as GET params. **It has no page or page_size in the MCP**,
so prefer `query_meta_ads`.

**`discover_meta_ads`** returns a curated random sample of high-reach ads (`niche`, `languages`,
`limit`, `max_ads_per_brand`, `seed`). Use it only for open-ended "what's trending in niche X". It is
not for a specific competitor. **1 credit per ad.**

**Single ad:** `get_meta_ad(ad_id, fields)` (**1 credit**), `get_meta_ad_by_meta_id`, and
`get_ad_by_url(url)`. The last one accepts a Meta Ads Library link, a TikTok or Instagram URL, or an
`app.brandsearch.co/ad/…` share link.

### Filters (search/query)
- `q`: phrase search over the **ad copy** and carousel variants, not on-image text. For a single
  keyword it also matches the brand's Meta page name, so never use the brand name. Join several words
  with a double space; all must match (up to 5). Max 200 chars.
- Media: `is_image`, `is_video`, `status`.
- Creative: `duplicate_count_min/max`, `duration_min/max` (video seconds), `copy_word_count_min/max`,
  `cta_types`, `funnel_types`, `languages`.
- Dates: `ad_started_from/to` (YYYY-MM-DD, ISO or unix), `meta_page_created_from/to`.
- EU only: `spend_min/max`, `daily_spend_min/max` (EUR), `reach_min/max`, `reach_rank_min/max`, `eu_countries`.
- There is no `country` filter. `country_code` is the brand's HQ. `markets` holds full country names
  (`"United States"`) and filters the brand's ships-to.

### sort_by
| Canonical | Aliases | Use |
|---|---|---|
| `total_active_time` | `active` | Longevity — tie-breaker only (an ad can run long on a tiny budget) |
| `start_date` | `date` | Newest launches, i.e. what is being tested now |
| `created_at` | `recent`, `newest` | When Brandsearch indexed it |
| `eu_total_spend` | `spend` | **EU markets only** (null for US ads) — primary sort only when targeting the EU |
| `eu_total_reach` | `reach` | **EU only** |
| `reach_rank` | `rank` | **Default for us**: Brandsearch "Top rank (by impressions)", ascending (1 = best). Populated for US ads too. Request the field explicitly. |
| `duration` | `length` | Video length |
| `scaler` | | Shuffled mix of high spend and high reach (EU data). Use `seed` to reproduce. |

### Fields (pass `fields="..."` to keep dumps small)
- Core: `id`, `status`, `start_date`, `end_date`, `total_active_time` (seconds), `is_image`, `is_video`,
  `is_duplicate`, `duplicate_count` (number of duplicate variants), `cards_count` (carousel),
  `creative` (`{title, description, cta:{text,type}}`, with empty keys omitted), `dashboard_url`.
- Optional: `platforms`, `language`, `copy_word_count`, `funnel_type`, `target_gender`, `target_ages`,
  `target_locations`, `eu_total_spend`, `eu_daily_spend`, `eu_total_reach`, `per_country_spend`,
  `reach_rank`, `duration`, `has_transcript`, `transcript_url`, `page_info`, `created_at`.
- Media URLs are attached automatically: `image_url` (resized), `image_original_url`, `thumbnail_url`,
  `video_sd_url`, `video_hd_url`.

## Media
- Signed media URLs **expire 3 days** after the response (`404 Expired`). Download right away.
  `transcript_url` does not expire.
- The docs say MCP clients can't fetch media hosts. **In practice, urllib with a browser User-Agent
  downloads `image_original_url` fine, and it's free.** That is what `scripts/rank_ads.py` does.
  Originals are often PNG.
- `thumbnail_url` (120×200) often returns 404 when `image_url` is missing. Treat that row as missing.
- **`download_ad(platform, id, media="auto"|"image"|"video")`** costs **1 credit**. It returns an
  **inline image only** (about 600 px compact), not a file. The harness saves it as
  `tool-results/mcp-claude_ai_Brandsearch-blob-<ts>.jpg`, and you must map blobs to ids in call order.
  `media="video"` returns the video's type, size and a download URL (no bytes).
  Use it sparingly: missing-URL rows are usually duplicates.

## AI, video and swipe tools
| Tool | Params | Cost |
|---|---|---|
| `analyze_ad` | `platform`, `id`, `force_regenerate` | **14 AI credits** for an image or email, **19** for video. Cached results are free. A low balance gives `402 insufficient_ai_credits`. |
| `transcribe_ad` | `id`, `force_regenerate` | **1 credit** per transcript. Meta video only. An image ad gives `422 ad_not_video`. It can take more than a minute. |
| `create_folder` | `folder_type` (`ads`/`brands`/`spectre`), `name` | Write. Use it for a swipe file, for example "<BRAND> competitor top 30". |
| `add_to_folder` | `folder_type`, `folder_id`, `type`=`meta`, `ad_id` | Write, idempotent. |
| `list_folders`, `get_folder_ads` | | Read saved swipe files. |

## Account
- `get_usage`: API quota left (daily and monthly). `get_ai_credits`: AI-credit pool.
  `whoami`: unmetered; reports `account_link_broken`. `get_system_freshness`: data timestamps.
- Rate limit: `429 too_many_requests` with `Retry-After`. Wait, then retry.
- If the account is inactive, every call fails. Tell the operator.

## Costs at a glance
- **Free, quota only:** `get_brand_ads`, `query_meta_ads`, `search_meta_ads`, brand lookups, direct URL downloads.
- **1 credit:** each `download_ad`, `get_meta_ad`, `transcribe_ad`; each aggregates call; each
  `discover_*` row; product tools per item.
- **AI credits:** `analyze_ad` (14 for image, 19 for video).

## Pitfalls
1. Rank by `reach_rank` (Top rank by impressions) by default; use `spend`/`reach` only when targeting EU markets (US ads have none); days running is only a tie-breaker.
2. The endpoints disagree on dates and `total_active_time`. Take the max per id across both.
3. Without `q`, other products from the same brand pollute the top ads.
4. `get_brand_ads` returns 20 rows only, and `query_meta_ads` lacks some images. Pull both.
5. Booleans: `get_brand_ads` takes the string `"true"`; `query_meta_ads` takes a JSON `true`.
6. Large results go to tool-results files (`.txt` with a text prefix, or `toolu_*.json` as
   `[{"type":"text","text":"..."}]`). `rank_ads.py` parses both.
