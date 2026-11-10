# 18 — Folders, scripts, templates, credits

Detail behind `SKILL.md` (formerly its §6 and §7).

## Contents
1. Folders, scripts, templates (PRODUCT_DIR tree, folder hygiene, script usage)
2. Credits and costs

---

## 1. Folders, scripts, templates

`PRODUCT_DIR` = `PRODUCTS_ROOT/BRAND` (before the brand exists use `PRODUCTS_ROOT/_<competitor-slug>` and rename after the gate):
```
BRIEF.md · DELIVERY.md
00_alpha/ALPHA_DOSSIER.md   (final Step Alpha dossier, exactly the spec structure)
00_alpha/analysis1/   (1.1_customer.md, 1.2_ad_inventory.md, 1.2_video_ads.md, 1.2_static_ads.md, 1.2_patterns.md, 1.3_congruence.md, 1.4_angle_cards.md)
00_alpha/analysis2/   (2.1_hidden_angles.md, 2.3_synthesis.md)
00_alpha/chatgpt/     (CHATGPT_PROMPT.md, CHATGPT_RAW.md)
00_alpha/transcripts/ (<ad_id>.txt, one per video ad)
00_alpha/gemini/      (<ad_id>.json, video_gemini.py analysis per video ad; reused by 14)
00_alpha/ad_inventory.json  (alpha_gate.py inventory: header + one record per ad: id, short_id M#/S#, platform, format, status, start, end, run_days, reach_rank, duplicate_count, page, landing_url, caption, media URLs, video_file, image_file, transcript, gemini, angle, avatar, notes; plus excluded[] and review[])
01_branding/BRANDING.md
02_competitor/page/   (p.json, p.html, capture.json/.md, copy.txt, screenshots, SECTION_SPEC.md)
02_competitor/home/   (home HTML, copy, media URLs, screenshots, HOME_SPEC.md)
02_competitor/media/  (RAW gallery images, RAW GIFs, testimonials, section images, home images)
03_product-images/    (packshot, remakes, archive/v<N>_<reason>/)
04_page-images/       (testimonial/section remakes, GIF→WebP)
05_ads/competitor/    (raw/ ranking-pull dumps, raw/footprint/ complete-footprint dumps, videos/<ad_id>.mp4 every video ad, images/<ad_id>.<ext> every non-video ad, ranked top 30 NN_<id>.<ext>, ranking.json)
05_ads/generated/     (ad-NN-<slug>.png)
05_ads/AD_VARIANTS.md · 05_ads/AD_COPY.md
05_ads/REMAKE_CANDIDATES.md · 05_ads/remake-candidates/ (source videos)
05_ads/generated/videos/  (ONLY final vNN-<slug>.mp4 at the root; vNN-work/ = vNN-clips.jpg, vNN-draft.mp4, vNN-PLAN.md; all other work files in scratch/ and deleted when final)
06_policies/          (source/ raw competitor policies, <handle>.html ours, REVIEW.md)
08_shopify/           (products.spec.json, <slug>-products.csv ready to import, <slug>-products.UPLOAD.md)
```
Theme repo: only theme files, on branch `BRAND_SLUG`, files prefixed with the brand slug.
**Folder hygiene:** never create or keep `superseded/` or duplicate media folders (`out*/`, `fix*/`, copies of finals). A replaced version moves once to `<area>/archive/v<N>_<reason>/` (e.g. `04_page-images/archive/v1_ugc-prop_rejected/`); one home per final file, work files in `<area>/_work/`. Delete `*_sheet*` contact/preview sheets once generation is done. At delivery, hash every file (SHA-256) and delete byte duplicates outside the final folders.

Scripts (`scripts/`, run Python with `-I`; all have `--help`):
- `capture_page.py URL --out DIR [--html-file saved.html]` — product JSON, HTML, copy (+word count), colors/CSS vars, fonts, apps (Kaching tiers, reviews apps…), Shopify sections in order, media URLs (gallery, GIFs, videos, testimonials). Prices come from the product JSON (screenshots show the visitor's local currency).
- `screenshot.py TARGET --out DIR [--name comp]` — Edge/Chrome via DevTools: full-page desktop (`desk.png` + chunks) and true 390px mobile emulation (`mob.png` + sheets), works on shops that block iframes; `--engine cli` fallback.
- `fetch_media.py --out DIR --from-capture capture.json --kinds images,gifs,videos [--by-kind] [--webp-dir DIR]` — raw byte-identical downloads (manifest, skips existing) + animated GIF→WebP (q62).
- `contact_sheet.py IMAGES|GLOBS|DIRS --out sheet.jpg [--cols 5 --cell 300]` — labelled review grids (splits into sheet_1, sheet_2…).
- `alpha_gate.py` — Step Alpha helper, three subcommands: `inventory --alpha-dir PD/00_alpha --dumps [meta|tiktok|instagram|other:]FILES --keyword K [--expected-total N] --fetch-videos --fetch-images --fetch-transcripts` (α0: builds `ad_inventory.json` from the footprint dumps, free media + transcript downloads, prints what still needs credits) · `beats PD/00_alpha/gemini/<ad_id>.json --duration <ffprobe s>` (α1.2: BEAT MAP, HOOK DURATION, VO/TEXT SPLIT, PACING) · `[check] PD/00_alpha/ALPHA_DOSSIER.md` (α6 quality gate: the dossier structure Part 1 1.1–1.11, Part 2 2.1–2.8, Part 3 3.1–3.6 and the 16 QUALITY GATE boxes as far as a script can; prints PASS/FAIL, WARN and MANUAL lines, exit 1 on any FAIL; the MANUAL items stay a coordinator read-through). Must pass before Phase 2.
- `rank_ads.py --dumps FILES --out DIR --keyword K [--top 30] [--sheet] [--extra-image ID=PATH]` — merge Brandsearch dumps, download, hash/near-dup merge, rank by impressions rank (`--sort rank` default; `spend`/`reach` EU only; `days`), captions summary, sheets. Run it in the same session as the pull (media URLs expire).
- `product_csv.py spec.json --out 08_shopify/<slug>-products.csv [--image-base-url URL]` — Shopify product import CSV for every product the run needs (variants from the option lists, BRIEF prices, draft status, untracked inventory) + an UPLOAD.md checklist (template suffix, image order, variant images).
- `policies.py fetch|transform|push` — clone competitor policies 1:1 (identity swapped, private info removed, leftovers check) and publish them via Admin GraphQL `shopPolicyUpdate`.
- `kie_jobs.py jobs.json OUT_DIR` / `kie_jobs.py --credits` — batch Kie GPT Image 2.5 jobs (uploads local refs, polls, downloads). Needs `KIE_API_KEY`.
- `render_sections.js --theme DIR --template templates/product.json --sections ALL --out page.html [--shot] [--buybox --product p.json --prefix <slug>]` — local Liquid render of custom sections (and a mocked buy box) with the theme's real palette; needs liquidjs (`npm i liquidjs@10` in a scratch dir, pass `--modules` or NODE_PATH).
- `video_gemini.py SRC|DIR --out a.json | --out-dir DIR --competitor <Brand>` — Gemini Flash (ArgoLink) video analysis: framework, beat map, hook, CTA, scenes, VO, overlays, music. Used for every video ad in Step Alpha 1.2 and for the remake candidates (14).
- Video remakes (14): `video_clips.py SRC --out DIR [--classes "1-20=b,21=c"]` (scene detection, keyframes, labelled clip sheet, weak-cut list) · `video_transcribe.py SRC --out words.json --lang xx [--against ref.json]` (faster-whisper word timestamps, sync check) · `video_vo.py separate|skeleton|clone|delete-voice|audition|build|mix` (demucs stems, 3 mandatory remake lines, ElevenLabs clone, beat-aligned VO ≤1.08x, splice or ducked mix at −14 LUFS) · `video_captions.py ass|burn` (styled .ass from word timings, cover old overlays, burn in) · `video_finalize.py render|frames|clean` (insert regenerated clips, strip metadata, 0.5 s frame strip, folder clean-up).
Network note: if Python reports "certificate has expired", the scripts fall back to `certifi`/`curl`; pages behind bot protection need `--html-file` with a browser-saved copy.

Templates (`templates/`): BRIEF.md, CHATGPT_PROMPT.md (α3), ALPHA_DOSSIER.md (α5), BRANDING.md, SECTION_SPEC.md, AD_COPY.md, DELIVERY.md.

## 2. Credits and costs
Check Kie balance (`GET https://api.kie.ai/api/v1/chat/credit`) before Phase 3. GPT Image 2.5: 1K = 6, 2K = 10, 4K = 16 credits; 4:5 only at 1K. Typical run ≈ 260 credits (packshot 10, ~5 gallery 50, 3 testimonials 30, top-5 ads 50, 20 ads 120) + fixes. If short, tell the operator before generating and prioritise: packshot → gallery → top-5 ads → remaining ads → page images. Brandsearch: list/query calls are quota only (no credits), so the complete-footprint pull costs quota plus 1 credit per aggregates call; `transcribe_ad` 1 credit per video ad and Step Alpha transcribes EVERY video ad (N video ads = N credits); `download_ad` 1 credit each (use only for creatives or videos without a URL); `analyze_ad` 14–19 AI credits (not needed: Step Alpha does its own analysis). Before transcribing, count the video ads in the footprint and check `get_usage` / `get_ai_credits`; if the balance is short or a credit freeze is in force, tell the operator before spending. Gemini Flash via ArgoLink (`video_gemini.py`, Step Alpha 1.2): ≈ $0.005 per 30 s video ad (14 §12). Report spend in the delivery. Video remakes: (c) clip = 76 Kie credits (start frame 6 + wan i2v 720p 5 s 70); voice = ElevenLabs Starter quota (40k characters/month), see 14 §12.
