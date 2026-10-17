# 07 — Competitor ad research (Brandsearch MCP)

Goal: get the competitor's **top 30 unique image creatives for THIS product**, ranked the way that
holds up for the MARKET, analyzed to the level where we can recreate the top 5 at ~97% fidelity
(see 08-ad-creatives.md), plus the caption framework (see 09-ad-copy.md).

Outputs (all under `PRODUCT_DIR/05_ads/`):
- `competitor/raw/` holds the raw Brandsearch dumps, copied unedited
- `competitor/NN_<leadid>.<ext>` holds the top 30 originals with ranked file names. The extension
  follows the real file format, and Brandsearch originals are often PNG, so glob `NN_*.*` and not `*.jpg`.
- `competitor/ranking.json`, `missing_images.json`, `merged_ads.json`, `copy_summary.md`
- `competitor/sheet_top10.jpg`, `sheet_01.jpg`, `sheet_02.jpg`
- `COMPETITOR_ADS.md`, built from `templates/COMPETITOR_ADS.md`

Tool reference: `tools-brandsearch.md`. Script: `scripts/rank_ads.py`.
Who does what: the **master** makes every Brandsearch MCP call and runs the script, because MCP results
land in the master's context and harness files. **Sub-agents** only read the image files and return text.
Sub-agents are often blocked from writing .md files, so the master writes COMPETITOR_ADS.md.

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
- Days running and duplicates stay useful as tie-breakers and as context in the analysis (a creative duplicated into more ad sets = being scaled).

**Always request `reach_rank` (and `eu_total_spend,eu_total_reach` when EU) in the `fields` of every pull** — rank_ads.py can only sort by what the dumps contain; dumps without it fall back to days running with a warning.

`days` = max(`total_active_time` / 86400, latest `end_date` − earliest `start_date`) over every row of every id in the creative group (the two endpoints disagree: ad 1330434352342383 showed 4 days in `query_meta_ads` and 17 in `get_brand_ads`). Don't add +1. For groups of identical creatives, use the best (`min`) `reach_rank` of the group.

---

## Step 1 — Resolve the brand domain
- **Purpose:** every ad call needs `brand_id` = the cleaned domain (`plaims.com`). The brand is often
  not named the way the URL suggests.
- **Call:** `get_brand_by_url(url=COMPETITOR_URL)`. If that returns 404, call `lookup_brand(q="<name or domain>")`.
  Optional: `get_brand_advertisers(brand_id=...)` lists the Meta pages advertising for the brand.
  It is useful when the brand also runs ads from a second page or domain.
- **Check:** the record shows Meta ads active. If it shows 0 ads, stop and report this to the operator.
  Don't search other brands without asking.
- **Optional context (1 credit):** `get_brand_ads_aggregates(brand_id=...)` gives the media mix
  (image vs video share), CTA breakdown and demography. Use it to decide whether video matters (step 10).
- **Done when:** you have `brand_id` and know whether the brand has Meta image ads.

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
- Fewer than 30 unique creatives is fine. Analyze what exists and say so.
- **Done when:** the master has a final ordered list of up to 30 files.

## Step 7 — Analyze with 2 sub-agents (15 ads each, in parallel)
- **Why 2 × 15:** one agent reading 30 full-size images runs out of context and gets shallow. 15 each
  keeps the descriptions detailed enough for 97% recreation.
- Give each agent its file list (ranks 1–15 and 16–30), the matching `ranking.json` entries (days,
  copies, first_seen, size), and this brief:

```
You are an ad-creative analyst. Read each image file below (use the Read tool on every file, full size).
Do NOT write files; return everything as text in your final reply.
For EACH ad, in rank order, return:
1. Rank, file name, lead id, days running, copies, first seen (given).
2. Size in px and aspect ratio (1:1, 4:5, 9:16 ...).
3. Format type (e.g. Ours vs Theirs table, POV through product, product + callout arrows, big-type
   poster with bullets, before/after split, UGC selfie, handwritten note/planner, fake advertorial,
   listicle grid, stat poster, diagram, testimonial card, lifestyle + checklist).
4. ALL on-image text VERBATIM, top to bottom, keeping case, line breaks, emphasis, typos (mark "[sic]").
5. Visual description precise enough to recreate it at ~97% fidelity:
   - layout with approximate % positions/sizes of every element (e.g. "headline band top 0-18%, black on white")
   - colors as hex estimates (background, text, accents, panels)
   - fonts (family guess, weight, case, size relative to the canvas), icons, checks/Xs, arrows, badges
   - product: angle, size (% of width), position, lens color, cutout vs in-scene
   - people: age, gender, ethnicity, expression, clothing, pose, framing, what they are doing
   - background/scene, lighting, color grade, photo vs render vs illustration, "simulated view"-type disclaimers
6. Hook (the first thing read) and the Schwartz awareness level it targets (unaware / problem-aware /
   solution-aware / product-aware / most-aware), with one line of reasoning.
7. Claims made on the image, verbatim (do not judge or soften them).
8. Angle in 3-6 words (e.g. "cataract-specific vs generic yellow").
After all ads, return PATTERNS across your batch: winning formats, hook families, category enemy,
color system, type system, claim types, product presentation, people/casting, any quirks
(typos, wrong-market prices), and how the older long-running ads differ from the newer tests.
```
- **Done when:** both agents have returned text for all their ads and patterns.

## Step 8 — Master compiles COMPETITOR_ADS.md
- Copy `templates/COMPETITOR_ADS.md` to `PRODUCT_DIR/05_ads/COMPETITOR_ADS.md` and fill it:
  - method line, with counts and the ranking rule actually used
  - **generations**: cluster the ranks by launch date and style. Plaims had Gen 1, launched Sep 25 and
    still running at 17 days, all 1:1, Poppins Bold, amber #FFB800, hard condition claims. Gen 2
    launched Sep 28 – Oct 11, mostly 1856×2304 4:5, AI scenes, plainer copy, then lo-fi native tests.
    Long-running generations are proven. New ones are only what the brand is testing now.
  - top-30 table (rank, days, copies, format, hook)
  - patterns, merged from both agents
  - pointer to the per-ad detail
- Save each agent's full per-ad text as an appendix (`COMPETITOR_ADS.md` § Per-ad detail) or as
  `05_ads/competitor/analysis_1-15.md` and `analysis_16-30.md`. 08-ad-creatives.md needs the
  verbatim text and layout for the top 5 remakes.
- Keep claims exactly as they appear (operator rule 1). Don't add notes about claim validity.

## Step 9 — Capture the copy/caption framework
- Read `competitor/copy_summary.md`. Brands often **lock one caption and test creatives**: all 67
  Plaims ads ran "Headlight Glasses That Actually Work" with the same 108-word body, and only the CTA
  button varied (Shop now ×29, See details ×10, Learn more ×5).
- Record per caption: title, full description (verbatim), CTA button(s), number of ads and creatives,
  and which ranks use it. Paste this into COMPETITOR_ADS.md § Ad copy, and hand it to 09-ad-copy.md.
- If captions differ per creative, note which caption goes with which top-10 creative. `ranking.json`
  has `titles`, `descriptions` and `ctas` per group.

## Step 10 — Report to the operator
- Show `sheet_top10.jpg` (open or attach the image), plus this table:

| Rank | Lead id | Angle | Days | Copies |
|---|---|---|---|---|
| 1 | 1635066311558242 | Ours vs Theirs, cataract-specific vs generic yellow | 17 | 3 |

- Add three lines: the ranking rule used (Top rank by impressions; spend only for EU markets), the unique-creative count,
  and the credits spent.
- **Done when:** the operator has seen the top 10. Ad generation (08) starts from this ranking.

---

## Video ads (out of scope unless asked)
- The default pull uses `is_image="true"`, and the script skips `is_video` rows.
- If the operator asks, or aggregates show the brand is mostly video:
  1. Pull with `is_video="true"`, using the same two endpoints and the same ranking rule.
  2. `download_ad(platform="meta", id, media="video")` returns a download URL (1 credit). Fetch it with
     urllib right away, because it expires.
  3. `transcribe_ad(id)` returns the hook line, timed speech and language (1 credit; existing
     transcripts are instant).
  4. `analyze_ad(platform="meta", id)` gives an AI breakdown (19 AI credits for video, 14 for image;
     cached results are free). It is optional; our own sub-agent analysis is usually better and free.
- `rank_ads.py --include-video` ranks video ads by their cover frame, which only works if
  `image_url` or `thumbnail_url` exists.

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
- Ranking by spend for US ads produces wrong winners. Use days, then copies.
- No `q` filter pulls the brand's other products. Plaims' soap ads topped the first unfiltered pull.
- Using only `query_meta_ads` gives truncated dates (5 d vs 17 d for the same ad) and 23 rows without
  images. Using only `get_brand_ads` gives 20 rows. Use both.
- Paying `download_ad` for every missing row cost 15 credits for 0 new creatives. Follow the priorities.
- URLs expire after 3 days. Run the script immediately after pulling, and keep `_cache/`.
- Sub-agents calling the MCP themselves leads to duplicated calls and spend, and results trapped in
  their context. The master pulls; agents read files.
- Sub-agents can't write .md files. Make them return text, and the master writes the file.
- Sorting the ranking by id or by file name loses the order. `ranking.json` order is the truth.
