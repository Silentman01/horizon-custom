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

## Complete ad footprint for Step Alpha (Phase 1.3)
Step Alpha 1.2 needs **every** ad of the competitor for this product, not the top 30 (spec
[19](19-step-alpha.md) lines 200–202 and the QUALITY GATE "Complete ad inventory" and "Every video ad
transcribed"). The procedure is [07 Steps 7–9](07-ads-research-brandsearch.md#step-7--pull-the-complete-footprint-for-step-alpha);
how Alpha uses it: [20 §4](20-step-alpha-runbook.md#alpha0-inputs). The calls, in order:

1. **Brand and pages.** `get_brand_by_url(url)` (else `lookup_brand`) → `brand_id`.
   `get_brand_advertisers(brand_id, limit=100)` → every Meta page advertising for the brand; save it with the
   dumps (SATURATION in Alpha 1.2). Optional, 1 credit: `get_brand_ads_aggregates(brand_id)` for totals and media mix.
2. **Meta, both statuses, every format, paged until exhausted.** For `status` in `active`, `inactive`:
   ```
   query_meta_ads(body={"brand_ids": ["<domain>"], "q": "<kw>", "status": "<status>", "page": N, "page_size": 100,
                        "fields": "id,status,start_date,end_date,total_active_time,duplicate_count,is_duplicate,reach_rank,eu_total_spend,eu_total_reach,creative,cards_count,is_image,is_video,platforms,language,duration,funnel_type,has_transcript,transcript_url,page_info,image_original_url,image_url"})
   ```
   No `is_image`/`is_video` filter. Repeat with `page` 1, 2, 3 … up to `pagination.total_pages`, one dump per page.
   Then the same without `q` and with `"is_video": true` (video captions are often short): keep the rows that
   are this product (title, transcript or landing page), drop the brand's other products.
3. **`get_brand_ads` slices** for true `total_active_time` and media URLs (20 rows each, no paging): `platform="meta"`,
   each `status`, plus `is_video="true"`, with `sort_by` = `rank`, `date`, `recent`, `active` and both `sort_order`.
4. **Other platforms.** `get_brand_ads(brand_id, platform="tiktok")` and `platform="instagram"`, both statuses, sliced
   the same way. Stop slicing a platform when two slices in a row bring no new id. Platform empty in Brandsearch → ask
   the operator once for those ads (the spec allows "provided by operator") and record the gap.
5. **Exhausted check.** Unique ids per platform and status ≥ the `pagination.total` Brandsearch reports. Short →
   record it in `ad_inventory.json` `header.gaps` and BRIEF.md.
6. **Save** every result unedited to `PD/05_ads/competitor/raw/footprint/<platform>-<status>-p<N>.json` (harness
   files: copy them; inline results: save verbatim).
7. **Inventory + free media** (one command; re-run it after every new dump, it keeps what you filled):
   ```
   python -I <skill>/scripts/alpha_gate.py inventory --alpha-dir "PD/00_alpha" \
     --dumps meta:PD/05_ads/competitor/raw/footprint/meta-*.json tiktok:PD/05_ads/competitor/raw/footprint/tiktok-*.json \
     --keyword <kw> --expected-total <sum of pagination totals per platform/status> \
     --fetch-videos --fetch-images --fetch-transcripts
   ```
   Writes `PD/00_alpha/ad_inventory.json` (header: counts, pagination totals, gaps, pull date, platforms checked;
   one record per ad: id, short_id M1../S1.., platform, format, status, start, end, run_days, reach_rank,
   duplicate_count, page, landing_url, caption, media URLs, video_file, image_file, transcript, gemini, angle, avatar,
   notes; full list in [20 §2](20-step-alpha-runbook.md#2-folder-and-files)). Videos land in
   `PD/05_ads/competitor/videos/<ad_id>.mp4`, static images in `PD/05_ads/competitor/images/<ad_id>.<ext>`,
   `transcript_url` texts in `PD/00_alpha/transcripts/<ad_id>.txt` — all free, run it the same session (URLs
   expire after 3 days). Rows whose copy lacks the keyword go to `review`: move each to `ads` or `excluded`
   (with a `reason`) by hand. The gate fails while `review` is not empty.
8. **Transcript of EVERY video ad.** The command prints how many are still missing and their credit cost.
   Check `get_usage` / `get_ai_credits` and any credit freeze first ([18 §2](18-folders-scripts-credits.md#2-credits-and-costs)).
   Then per missing Meta video: `transcribe_ad(id)` (**1 credit**, can take over a minute) → save the result
   verbatim to `PD/00_alpha/transcripts/<ad_id>.txt` (first line `source: brandsearch` + language, then the timed
   speech). Identical videos share one transcript (no second credit). `422 ad_not_video`, TikTok/Instagram or a
   failure → `python -I video_transcribe.py PD/05_ads/competitor/videos/<ad_id>.mp4 --out <scratch>.json` (free,
   local) and save its timed lines with `source: whisper`. A video with no speech still gets a file:
   `source: none — music only`.
9. **Video file missing** (no URL in any dump): `download_ad(platform, id, media="video")` (**1 credit**), fetch the
   returned URL at once, save as `<ad_id>.mp4`.

Done when: `alpha_gate.py inventory` reports 0 to review, 0 transcripts missing, 0 video files missing, and the
header totals match Brandsearch (or the gap is recorded). Cost of a footprint: quota only for the pulls, plus
1 credit per video ad without a free transcript, plus 1 credit per video/image with no URL.

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
