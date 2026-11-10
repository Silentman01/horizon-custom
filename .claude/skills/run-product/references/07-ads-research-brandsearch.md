# 07 — Competitor ad pull (Brandsearch MCP): complete footprint + top-30 ranking

This is Phase 1.3, the data pull that feeds Step Alpha. It has two jobs:
1. **Complete ad footprint** for Step Alpha 1.2: every ad the competitor runs or ran for this product,
   active and inactive, image and video, on every platform Brandsearch has, paged until nothing new comes
   back, plus a transcript of **every** video ad (Steps 7–9).
2. **Top 30 unique image creatives**, ranked the way that holds up for the MARKET (Steps 1–6). D2 remakes
   the top 5 and builds the pattern ads from them (08); the video picks use the same ranking (14).

This step only pulls, downloads, transcribes and ranks. Step Alpha 1.2 reads every ad (inventory table,
video beat maps, static decoding, cross-ad patterns): `19-step-alpha.md` (spec) and `20-step-alpha-runbook.md` (how).

Outputs:
- `05_ads/competitor/raw/` holds the raw Brandsearch dumps of the ranking pull, copied unedited
- `05_ads/competitor/raw/footprint/` holds the raw footprint dumps (every platform, status and page)
- `05_ads/competitor/NN_<leadid>.<ext>` holds the top 30 originals with ranked file names. The extension
  follows the real file format, and Brandsearch originals are often PNG, so glob `NN_*.*` and not `*.jpg`.
- `05_ads/competitor/ranking.json`, `missing_images.json`, `merged_ads.json`, `copy_summary.md`
- `05_ads/competitor/sheet_top10.jpg`, `sheet_01.jpg`, `sheet_02.jpg`
- `05_ads/competitor/videos/<ad_id>.mp4`: every video ad file (Step Alpha's visual beat analysis reads them)
- `00_alpha/transcripts/<ad_id>.txt`: one transcript per video ad
- `00_alpha/ad_inventory.json`: one record per ad of the footprint

Tool reference: `tools-brandsearch.md`. Script: `scripts/rank_ads.py`.
Who does what: the **master** makes every Brandsearch MCP call and runs the script, because MCP results
land in the master's context and harness files. **Sub-agents** only read the files.

---

## Ranking logic by market (read first, because it decides everything below)

| Market of the competitor's ads | Primary sort | Tie-breakers |
|---|---|---|
| **Any market (default)** | Brandsearch **"Top rank (by impressions)"** = `reach_rank`, ascending (`sort_by="rank"`, `sort_order="asc"`; 1 = most impressions among the brand's ads) | days running, then copies + `duplicate_count` |
| **EU markets only** | `eu_total_spend` (`spend`) or `eu_total_reach` (`reach`), descending — these exist only for ads delivered in the EU | `reach_rank`, then days running |

Rules (operator rule 7):
- **Spend/reach sorting only when targeting EU markets.** US ads carry no `eu_total_spend` / `eu_total_reach`; the first Noxis attempt ranked US ads by spend and the operator rejected it.
- **Don't rank by days running alone.** An ad can run for weeks on a tiny budget ("an ad might be longest running but very low spent"). In the Plaims run, "Rainy Night Driving Glasses" (10 days, `reach_rank` 11) out-ranks several 17-day ads (`reach_rank` 13–24), and the tabletop comparison, mirror-glare and sore-eyes posters entered the top 10 only by impressions rank.
- `reach_rank` is populated for US ads (e.g. 3, 7, 8, 11 … for Plaims). It ranks among ALL the brand's ads (other products included), so values have gaps after the keyword filter — use them as an order, not a count.
- Days running and duplicates stay useful as tie-breakers and as signals for Step Alpha (a creative duplicated into more ad sets = being scaled).

**Always request `reach_rank` (and `eu_total_spend,eu_total_reach` when EU) in the `fields` of every pull** — rank_ads.py can only sort by what the dumps contain; dumps without it fall back to days running with a warning.

`days` = max(`total_active_time` / 86400, latest `end_date` − earliest `start_date`) over every row of every id in the creative group (the two endpoints disagree: ad 1330434352342383 showed 4 days in `query_meta_ads` and 17 in `get_brand_ads`). Don't add +1. For groups of identical creatives, use the best (`min`) `reach_rank` of the group.

---

## Step 1 — Resolve the brand domain
- **Purpose:** every ad call needs `brand_id` = the cleaned domain (`plaims.com`). The brand is often
  not named the way the URL suggests.
- **Call:** `get_brand_by_url(url=COMPETITOR_URL)`. If that returns 404, call `lookup_brand(q="<name or domain>")`.
  `get_brand_advertisers(brand_id=...)` lists the Meta pages advertising for the brand (needed in
  Step 7). It also shows when the brand runs ads from a second page or domain.
- **Check:** the record shows ads (active or inactive). If it shows 0 ads, stop and report this to the
  operator. Don't search other brands without asking.
- **Optional context (1 credit):** `get_brand_ads_aggregates(brand_id=...)` gives the media mix
  (image vs video share), CTA breakdown and demography. Step Alpha can use the demography for its avatars.
- **Done when:** you have `brand_id` and know which platforms and formats the brand advertises on.

## Step 2 — Find the product keyword(s)
- **Purpose:** brands advertise several products. Plaims also runs a persimmon soap, so the unfiltered
  top ads were the wrong product. `q=` restricts results to ads whose **copy** contains the keyword.
- **How:** take the most distinctive noun from the competitor product title or caption ("headlight"
  from "Plaims Polarized Headlight Glasses"). Test it with one cheap call:
  `get_brand_ads(brand_id, platform="meta", q="<kw>", fields="id,creative")`, then read the titles.
- **Rules:**
  - `q` matches ad copy (and carousel variants), **not text on the image**. For a single keyword it also
    matches the Meta page name. So never use the brand name as the keyword, because it would match every ad.
  - Use one word, or several words joined by a **double space**, which means all must match (up to 5).
    Prefer one distinctive word.
  - If the product has two names (for example "night driving" and "headlight"), pull each one separately
    and pass all the dumps to the script. The script dedupes them.
- **Done when:** a test pull returns only ads for this product.

## Step 3 — Pull with BOTH endpoints and save the dumps
- **Why both:** neither endpoint is complete on its own.
  - `get_brand_ads` has `total_active_time` and `image_original_url` for every row, but in the MCP it
    returns **20 rows per call and has no page parameter**.
  - `query_meta_ads` returns everything (up to 100 per page, paginated), but in the Plaims run
    **23 of 66 rows had no image URL** and its dates were truncated.
  - Merging the two by id gives full coverage, the correct longevity, and the most image URLs.
- **Calls** (`fields` keeps the dumps small; `creative` carries title, description and CTA):
  ```
  get_brand_ads(brand_id="<domain>", platform="meta", is_image="true", q="<kw>",
                sort_by="rank", sort_order="asc",
                fields="id,status,start_date,end_date,total_active_time,duplicate_count,is_duplicate,reach_rank,eu_total_spend,eu_total_reach,creative,image_original_url,image_url,thumbnail_url")

  query_meta_ads(body={"brand_ids": ["<domain>"], "is_image": true, "q": "<kw>",
                       "page": 1, "page_size": 100,
                       "fields": "id,status,start_date,end_date,total_active_time,duplicate_count,is_duplicate,reach_rank,eu_total_spend,eu_total_reach,creative,cards_count,image_original_url,image_url"})
  ```
  Media URLs (`image_url`, `image_original_url`, `thumbnail_url`) are attached automatically.
- **Pagination:** if `pagination.total > page_size`, repeat `query_meta_ads` with `page: 2, 3, …` up to
  `total_pages`, one dump per page. `get_brand_ads` shows `total_pages > 1` too (Plaims: 4), but it
  cannot be paged in the MCP. That is expected, because `query_meta_ads` covers the rest.
- **Free coverage top-up (optional):** more `get_brand_ads` slices return other rows with full image URLs
  and true `total_active_time`. Use `sort_by="recent"`, `sort_by="date"`, `sort_order="asc"`, or
  `status="inactive"` (long-running winners that were stopped). These calls count against API quota,
  not credits.
- **Saving:** results that are too big for context are saved by the harness under
  `~/.claude/projects/<project>/<session>/tool-results/`. Two formats exist:
  - `mcp-claude_ai_Brandsearch-query_meta_ads-<ts>.txt`, which is plain text where the JSON starts at the first `{`
  - `toolu_<id>.json`, which is a list `[{"type":"text","text":"<json string>"}]`

  Pass these paths straight to the script, which copies them into `competitor/raw/`. A result that came
  back inline in context must be saved by you, verbatim, to `competitor/raw/<endpoint>-p<N>.json`.
- **Pitfall:** media URLs **expire 3 days** after the response. Run step 4 in the same session. If the
  script reports `expired`, pull again.
- **Done when:** every page of `query_meta_ads` and at least one `get_brand_ads` slice are on disk.

## Step 4 — Merge, download, dedupe and rank (script)
```
python -I ~/.claude/skills/run-product/scripts/rank_ads.py \
  --dumps <dump1> <dump2> [...] --out "PRODUCT_DIR/05_ads/competitor" \
  --keyword <kw> [--keyword <kw2>] --top 30 --sheet
```
- **What it does:**
  - Parses every dump format and merges rows by id, keeping non-null fields, the earliest start, the
    latest end and the max `total_active_time`.
  - Drops rows whose caption lacks the keyword. This is a safety net for dumps pulled without `q`.
  - Skips video ads.
  - Downloads `image_original_url`, then `image_url`, then `thumbnail_url`, with a browser UA and
    retries. Downloading directly works even though the docs say MCP clients can't, and it is free.
  - Groups identical creatives by **md5 of the bytes**.
  - Attaches lower-quality copies (resized, thumbnail, download_ad blob) to their original by
    perceptual match. Calibrated distance: copy = 0.002, closest different creative = 0.066,
    threshold = 0.02.
  - Ranks by days desc, then copies + duplicate_count desc, then still running, then first seen.
  - Writes the files listed at the top. It prints the table, the missing-image priorities, the caption
    summary, and lists CHECK lines for possible near-duplicates.
- **Checks:**
  - Total rows ≈ the `pagination.total` sum.
  - "kept X, dropped Y" makes sense. If the filter dropped the product's own ads, the keyword is wrong.
  - Images were downloaded for most ids. If 0 were downloaded, the URLs expired: go back to step 3.
  - The longest-running ads are at the top, and the days look plausible against the dates.
- **Worked example (Plaims):** 66 + 20 rows merged into 67 ids. 44 images downloaded (23 rows had only a
  thumbnail, which returned 404). These formed **32 unique creatives**. Ranks 1–6 were the 17-day Gen-1
  ads, all 1080×1080, started Sep 25 and still running: 1635066311558242 (+28918591337735464,
  1817211982641991), 1078757708070086, 1083970074006615 (+1358827606331541), 1330434352342383,
  2614982972280100 (+1109521648479176), and 4493218220931997. Ranks 7+ were the Gen-2 4:5 tests
  (10 days, then 7, 6, and so on).
- **Done when:** `ranking.json` exists and the top of the table looks right on `sheet_top10.jpg`. Read
  that sheet yourself.

## Step 5 — Handle missing images (spend credits only where it matters)
- **Why:** rows without a usable URL are **usually duplicates** of creatives you already have. In the
  Plaims run, 15 `download_ad` calls (15 credits) produced **0 new creatives**: every blob matched
  ranks 1–12.
- **Read** `missing_images.json`. Each item has `priority`:
  - `high`: the ad would enter the top 10 even as a unique creative
  - `low`: it would enter the top 30
  - `skip`: it would rank below the top 30
- **Act:**
  1. Try free first: run the extra `get_brand_ads` slices from step 3 and re-run the script. Downloads
     are cached in `_cache/`, so a re-run is fast.
  2. For each `high` id, call `download_ad(platform="meta", id="<id>")` (1 credit). It returns an
     **inline image only, not a file**. The harness saves it under tool-results as
     `mcp-claude_ai_Brandsearch-blob-<ts>.jpg` (600 px compact). Map each blob to its id in call
     order, then re-run with `--extra-image <id>=<blob path>` (repeatable). The script attaches blobs
     that match existing groups and adds any truly new creative.
  3. Fetch `low` ids only if the operator wants a complete top 30.
- **Done when:** no `high` items remain, or the operator declined the spend. Report the credits used.

## Step 6 — Select the top 30
- Take ranks 1–30 from `ranking.json`. The files are already named `01_…` to `30_…`.
- Look at `sheet_01.jpg` and `sheet_02.jpg` (15 per sheet) for:
  - **wrong product:** remove it, re-run with a better keyword, and don't hand-edit ranks
  - **CHECK near-duplicates** (same image, re-encoded): re-run with `--near-dup` if they really are the same
  - **`low_res` entries** in the top 10 (thumbnail only): use download_ad as in step 5
- Fewer than 30 unique creatives is fine. Rank what exists and say so.
- **Done when:** the master has a final ordered list of up to 30 files.

## Step 7 — Pull the complete footprint (for Step Alpha)
- **Why:** Step Alpha needs every ad, not the top 30. The quality gate checks "Complete ad inventory from
  BrandSearch" and "Every video ad transcribed" (`19-step-alpha.md`, QUALITY GATE).
- **Scope:** this product only. Use the Step 2 keyword(s). Video captions are often short: also pull
  `is_video` without `q` and keep the rows that are this product (title, transcript or landing page).
  Ads of the brand's other products stay out.
- **Meta, every status and format:** `query_meta_ads` once with `"status": "active"` and once with
  `"status": "inactive"`, no `is_image`/`is_video` filter, `page_size: 100`, and page `1, 2, 3 …` until
  `page = total_pages`. One dump per page. Add `get_brand_ads` slices for both statuses and for
  `is_video="true"` (true `total_active_time`, more media URLs).
- **Other platforms:** `get_brand_ads(platform="tiktok")` and `platform="instagram"`, both statuses. These
  return 20 rows per call with no page parameter, so slice with `sort_by` (`rank`, `date`, `recent`,
  `active`) and `sort_order` (`asc`, `desc`) until two slices in a row bring no new id.
- **Fields:** the Step 3 fields plus `is_image,is_video,platforms,language,duration,funnel_type,has_transcript,transcript_url,page_info`.
  Video URLs (`video_sd_url`, `video_hd_url`) are attached automatically.
- **Exhausted =** unique ids per platform and status ≥ the `pagination.total` Brandsearch reports. If a
  platform stays short, record the gap in `ad_inventory.json` (`"gaps"`) and in BRIEF.md, and ask the
  operator once for an export of the missing ads (the spec allows ads "provided by operator").
- **Advertisers:** `get_brand_advertisers(brand_id)` lists the pages running the product (Alpha's
  SATURATION line). Save it with the dumps.
- **Saving:** copy each harness result file (Step 3 formats), or save an inline result verbatim, to
  `05_ads/competitor/raw/footprint/<platform>-<status>-p<N>.json`. Never edit a dump.
- **Media files:** run Step 9's command right after the pull, in the same session (URLs expire after 3 days):
  `--fetch-videos` saves every video ad (`video_hd_url`, else `video_sd_url`, browser UA, free) to
  `05_ads/competitor/videos/<ad_id>.mp4`, `--fetch-images` every non-video ad to `05_ads/competitor/images/<ad_id>.<ext>`.
  Use `download_ad(platform, id, media="video")` (1 credit) only for rows without a URL.
- **Done when:** every platform and status is exhausted (or the gap is recorded) and every video ad has a file.

## Step 8 — Transcribe every video ad
- **Credits first:** count the video ads with no transcript yet (`has_transcript` false). Each
  `transcribe_ad` costs 1 credit. Check `get_usage` / `get_ai_credits`, write the count and cost in the
  BRIEF credits line, and stay inside any credit freeze or budget set for the run (18 §2).
- **Per video ad:**
  1. `transcript_url` present → download it (free, it doesn't expire).
  2. Otherwise `transcribe_ad(id)` (Meta video only, 1 credit, can take more than a minute).
  3. Not Meta, or `422`/failure → transcribe the downloaded file locally with
     `scripts/video_transcribe.py` (faster-whisper, free).
- Identical videos (`is_duplicate`, same file hash) share one transcript: transcribe once and write the
  same text into each id's file. No second credit.
- **Save** `00_alpha/transcripts/<ad_id>.txt`: first line `source: brandsearch | brandsearch-url | whisper`
  and the language, then the timed speech verbatim (`--fetch-transcripts` writes the `brandsearch-url` files with
  that line). A video with no speech still gets a file: `source: none — music only`. Never edit or translate it.
- **Done when:** every video ad id in the footprint has a transcript file.

## Step 9 — Write `00_alpha/ad_inventory.json`
- One command, run right after Step 7 and again after Step 8 (it keeps what you already filled):
  ```
  python -I <skill>/scripts/alpha_gate.py inventory --alpha-dir "PD/00_alpha" \
    --dumps meta:PD/05_ads/competitor/raw/footprint/meta-*.json tiktok:PD/05_ads/competitor/raw/footprint/tiktok-*.json \
    --keyword <kw> --expected-total <sum of pagination totals> --fetch-videos --fetch-images --fetch-transcripts
  ```
- One record per ad of the footprint, merged by id across all dumps (earliest start, latest end, max
  days, same rules as Step 4): `id`, `short_id` (M1.. video, S1.. static/carousel), `platform`, `format`
  (video / static / carousel), `status`, `start`, `end`, `run_days`, `reach_rank`, `duplicate_count`, `page`,
  `landing_url`, `caption` {primary_text, headline, description, cta}, the media URLs (`video_url`, `image_url`,
  `transcript_url`, `dashboard_url`), `video_file`, `image_file`, `transcript` (path, video only),
  plus `angle`, `avatar` and `notes` left empty. Step Alpha 1.2 fills `angle` and `avatar`.
- Header (`header`): counts per platform, status and format, the `pagination.total` values, `gaps`,
  `pull_date`, `platforms_checked`, `expected_total`. Rows whose copy lacks the keyword land in `review`:
  move each to `ads` or `excluded` (with a `reason`) by hand. Field details: [20 §2](20-step-alpha-runbook.md#2-folder-and-files).
- **Done when:** the command reports 0 to review, 0 transcripts missing and 0 video files missing, and the record
  count equals the unique ids pulled (or the gap is recorded).

## Step 10 — Report to the operator
- Show `sheet_top10.jpg` (open or attach the image), plus this table:

| Rank | Lead id | Days | Copies | Format |
|---|---|---|---|---|
| 1 | 1635066311558242 | 17 | 3 | Ours vs Theirs table |

- Add four lines: the ranking rule used (Top rank by impressions; spend only for EU markets), the
  unique-creative count, the footprint counts (ads per platform / status / format, video transcripts),
  and the credits spent.
- **Done when:** the operator has seen the top 10. Step Alpha starts from the footprint; ad generation (08)
  starts after Alpha from this ranking.

---

## Video ads
Every video ad is pulled, downloaded and transcribed in Steps 7–8, for Step Alpha. The video remake
workflow (candidate gate, clip audit, voice clone, captions, (c) regenerations, folders) is `14-video-ads.md`;
it reuses these files and the Alpha analysis instead of pulling again.
- The ranking pull (Steps 3–4) uses `is_image="true"`, and the script skips `is_video` rows.
- Video ranking for the remake candidates: the same rule (`reach_rank` ascending, then days, then copies).
  `rank_ads.py --include-video` ranks video ads by their cover frame, which only works if `image_url` or
  `thumbnail_url` exists; otherwise sort the video records of `ad_inventory.json` by `reach_rank`.
- `download_ad(platform="meta", id, media="video")` returns a download URL (1 credit). Fetch it with
  urllib right away, because it expires.
- `transcribe_ad(id)` returns the hook line, timed speech and language (1 credit; existing transcripts are
  instant).
- `analyze_ad` is not used: Step Alpha 1.2 analyses every video ad from its transcript.

## Costs (check `get_usage` / `get_ai_credits` before spending)
| Action | Cost |
|---|---|
| `get_brand_ads`, `query_meta_ads`, `search_meta_ads`, `get_brand_by_url`, `lookup_brand` | API quota only, no credits |
| Downloading `image_original_url` / `image_url` directly | free |
| `get_brand_ads_aggregates`, `get_meta_ads_aggregates` | 1 credit flat |
| `get_meta_ad` (detail) | 1 credit |
| `download_ad` | 1 credit per file served |
| `transcribe_ad` | 1 credit per transcript |
| `discover_meta_ads` | 1 credit per ad returned |
| `analyze_ad` | 14 AI credits (image) / 19 (video) |

## Pitfalls (each one happened or nearly happened)
- Ranking by spend for US ads produces wrong winners. Use `reach_rank`, then days, then copies.
- No `q` filter pulls the brand's other products. Plaims' soap ads topped the first unfiltered pull.
- Using only `query_meta_ads` gives truncated dates (5 d vs 17 d for the same ad) and 23 rows without
  images. Using only `get_brand_ads` gives 20 rows. Use both.
- Paying `download_ad` for every missing row cost 15 credits for 0 new creatives. Follow the priorities.
- URLs expire after 3 days. Run the script and the video downloads immediately after pulling, and keep `_cache/`.
- Sub-agents calling the MCP themselves leads to duplicated calls and spend, and results trapped in
  their context. The master pulls; agents read files.
- Sub-agents can't write .md files. Make them return text, and the master writes the file.
- Sorting the ranking by id or by file name loses the order. `ranking.json` order is the truth.
- The top 30 or an active-only pull is not the footprint. Step Alpha needs every ad, active and inactive,
  every format and platform, and every video transcribed (Steps 7–8).
