# 17 — Phases 0–5 and Phase α (what to do, who does it, which reference to read)

Detail behind `SKILL.md` (formerly its §4). Phase 3 holds the stream table that QA checks row by row (10 §1).

## Contents
- Phase 0 — Intake and preflight
- Phase 1 — Competitor capture
- Phase α — Step Alpha (pre-launch intelligence)
- Phase 2 — Branding → GATE
- Phase 3 — Production (stream table + order inside the window)
- Phase 4 — QA loop
- Phase 5 — Delivery

---

## Phase 0 — Intake and preflight (master)
Read `references/01-intake-and-setup.md`. Parse inputs, confirm MARKET and PRODUCTS_ROOT, run preflight (git state, Shopify CLI, Python+Pillow, Node, Edge/Chrome, Kie key + credit balance, Brandsearch MCP + credits, ArgoLink key), create the PRODUCT_DIR tree (incl. `00_alpha/`), write BRIEF.md from `templates/BRIEF.md`.

## Phase 1 — Competitor capture (parallel, ~immediately)
Raw-data gathering only (allowed before Step Alpha); nothing is built here. Launch together:
- **Capture agent** — `scripts/capture_page.py` + `scripts/screenshot.py` → `02_competitor/page/` (product JSON, HTML, copy, colors, fonts, apps/bundle tiers, media URLs, screenshots) **and the competitor home page** → `02_competitor/home/` (HTML, copy, media URLs, full-page screenshots). Read `references/03-competitor-page-analysis.md` §capture and `references/11-home-page.md` §capture.
- **Media agent** — `scripts/fetch_media.py --from-capture` → `02_competitor/media/` (gallery images, **raw GIFs**, testimonial and section images) + WebP conversions. `references/06-page-images-and-gifs.md`.
- **Master** — Brandsearch pulls of the COMPLETE ad footprint (both endpoints, every Meta ad active and inactive, image and video; TikTok/other platforms when Brandsearch has them, otherwise operator-provided) into `05_ads/competitor/raw/footprint/`, video files into `05_ads/competitor/videos/`, images into `05_ads/competitor/images/`; a transcript of EVERY video ad (`transcribe_ad`) → `00_alpha/transcripts/<ad_id>.txt`; `00_alpha/ad_inventory.json` (one record per ad, `alpha_gate.py inventory`); then `scripts/rank_ads.py` (top 30 by impressions rank, kept for the creative and video remakes). `references/07-ads-research-brandsearch.md`, `references/tools-brandsearch.md`. Check credits first (18 §2).
- **Policies** — `scripts/policies.py fetch` → `06_policies/source/` (all competitor policy pages). `references/12-policies.md`.

<a id="phase-alpha"></a>
## Phase α — Step Alpha (pre-launch intelligence)
Runs after Phase 1 and before Phase 2. Nothing is built or generated until α6 passes (00 §17). Spec, authoritative for every field, table and checkbox: `references/19-step-alpha.md`. How to run each step: `references/20-step-alpha-runbook.md`. All outputs in `00_alpha/` (tree in 18 §1).

| Step | Who | Reads | Output |
|---|---|---|---|
| α0 Inputs | master | competitor URL(s), Phase 1 capture, complete ad footprint, transcripts | `00_alpha/ad_inventory.json`, `00_alpha/transcripts/<ad_id>.txt` (every video ad) |
| α1.1 Customer intelligence | Lead A (brief Lead A α) | page capture + copy, reviews/testimonials/FAQ, ad copy, transcripts | `analysis1/1.1_customer.md` (avatars, pains, desires, objections, emotional landscape with all 6 trigger types, unique mechanism) |
| α1.2 Advertising intelligence | Lead B + Sonnet α-analyst workers in batches (~15 ads each) + Haiku worker for `video_gemini.py` | `ad_inventory.json`, transcripts, `00_alpha/gemini/<ad_id>.json` per video, ad media in `05_ads/competitor/videos/` + `images/` | `analysis1/1.2_ad_inventory.md`, `1.2_video_ads.md` (every video: framework, beat map … CTA), `1.2_static_ads.md` (every non-video ad), `1.2_patterns.md` |
| α1.3 Funnel congruence | Lead A (after 1.2 per-ad tags) | 1.2 tags, page capture + screenshots | `analysis1/1.3_congruence.md` (every ad→page path mapped and scored, insights) |
| α1.4 Marketing angle map | Lead B | 1.1–1.3 | `analysis1/1.4_angle_cards.md` (one card per angle, `V1..Vn`, ≥ 3 HIGH/MEDIUM) |
| α2 Hidden angle discovery (2.1) | Lead B + Sonnet worker (brief α-angles) | 1.1–1.4 | `analysis2/2.1_hidden_angles.md` (angle explosion, all 13 emotional entries, every survivor rated `H1..Hn`, ≥ 8 beyond the competitor's) |
| α3 ChatGPT prompt (2.2) | Lead B drafts, master checks | 1.1–1.4, 2.1, `templates/CHATGPT_PROMPT.md` | `chatgpt/CHATGPT_PROMPT.md` (tailored, ready to paste) |
| **GATE α** | operator | the prompt as ONE copy block | `chatgpt/CHATGPT_RAW.md` (pasted result, verbatim); the run waits (15 §1) |
| α4 Opportunity synthesis (2.3) | Lead B (brief α-synthesis) | 2.1, CHATGPT_RAW.md | `analysis2/2.3_synthesis.md` (validated / killed hidden angles `H#`, emergent angles `E1..En`, opportunity cards `O1..On`, language bank, underserved avatars, untapped territories, congruence gaps) |
| α5 Dossier | master | everything above | `00_alpha/ALPHA_DOSSIER.md` from `templates/ALPHA_DOSSIER.md`: exactly Part 1 1.1–1.11, Part 2 2.1–2.8, Part 3 3.1–3.6 |
| α6 Quality gate | master | the dossier | `python -I scripts/alpha_gate.py 00_alpha/ALPHA_DOSSIER.md` (structure + counts) + read-through of the judgment items; result in BRIEF.md. Fail → back to the failing step. Pass → Phase 2 |

## Phase 2 — Branding → GATE (master)
Starts only after α6 passes. Read `references/02-branding.md` and the dossier (3.2 avatars, 1.5 emotional landscape, 1.6 mechanism, 3.5 language bank). From capture data: competitor snapshot table, 7–10 brand names (top 3 starred, possessive test), palette 1:1 (exact hex + roles), product title 1:1. Save `01_branding/BRANDING.md` (template `templates/BRANDING.md`). **Stop and present** (in the same message, ask for our domain + support email if unknown — needed for the policies). On approval: record decisions in BRIEF, create the git branch `BRAND_SLUG` from clean `main` (01-intake §git).

## Phase 3 — Production (parallel streams after the gate)
Every stream reads `00_alpha/ALPHA_DOSSIER.md` (the sections named in its reference).
| Stream | Who | Reference | Output |
|---|---|---|---|
| A1 Section spec + funnel psychology | conversion-architect agent | 03 | `02_competitor/page/SECTION_SPEC.md` |
| A2 Page copy | copywriter agent (after A1) | 03 §copy rules, 04 | copy deck (returned text → master saves) |
| A3 Build | master (or builder agent) | 04, tools-shopify-cli-and-git | theme settings, sections, blocks, template |
| A4 Home page | home-page agent (after A3's shared settings + reusable sections exist; can start with spec/copy right after the gate) | 11, 04 | `templates/index.json` + `<slug>-*` home sections, 1:1 with the competitor home, **complete with no admin setup** (hero + product cards from theme assets/static settings, no native product-list/hero; 11 §4) |
| B Product images | image agent | 05, tools-kie | packshot first, then gallery remakes → `03_product-images/` |
| C Page images + GIFs | image agent | 06, tools-kie | testimonials/section remakes, WebP → `04_page-images/`, theme assets |
| D2a Ad variants | ad-creative agent (dossier 3.1 angle cards, 3.3 hooks, 3.5 language) | 08 §1b | `05_ads/AD_VARIANTS.md` (angle card ID per variant) → **operator gate** |
| D2 Ad creatives | ad-creative agent or master (after approval + packshot) | 08, tools-kie | 25 ads → `05_ads/generated/` |
| E Ad copy | copy agent (dossier angle cards, hook library, language bank, objection phrases) | 09 | `05_ads/AD_COPY.md` (root of 05_ads, one copy set shared by image and video ads) |
| G Video ads (on request) | video agent (dossier 1.8/3.4 frameworks + beat maps, angle cards, hooks; after the packshot + operator-confirmed candidates) | 14 | `05_ads/generated/videos/vNN-<slug>.mp4` + `vNN-work/` (clips sheet, draft, PLAN) |
| I Product import file | master (small, after B gallery + BRIEF offer) | `scripts/product_csv.py` | `08_shopify/products.spec.json` → `08_shopify/<slug>-products.csv` (Shopify Admin > Products > Import: every product to create, title/handle/vendor/type/tags/description, options + all variants, price + compare-at, SKUs, inventory not tracked, status draft, SEO) + `<slug>-products.UPLOAD.md` (template suffix to set, gallery upload order, variant images by colour, shipping-rates reminder). Image cells filled only with `--image-base-url`; otherwise images are listed for upload |
| H Checkout header | master (small, after branding + C) | `scripts/checkout_header.py`, mockup `templates/checkout-header-mockup.png` | `07_checkout/<brand>-checkout-header.png` (+@2x): logo, "trusted by" gradient bar (brand colors) with 3 real-looking customer faces cropped from our page images, 3 trust points in the store language. Config `07_checkout/checkout_header.json`; strip metadata; operator uploads it in Settings > Checkout > Customize > Header |
| F Policies | master (small) | 12 | `policies.py transform` → `06_policies/<handle>.html` + REVIEW.md (1:1 text, brand/domain/email swapped, addresses/phones/registration numbers removed) |

Order inside the window (Step Alpha has already passed, so every stream can read the dossier from the start): start A1, B (packshot first), C, D2a, E and A4's home spec at once; A2 when A1 lands; A3 when A2 lands (settings/header/footer can start immediately); A4 builds once A3's settings and reusable sections (testimonials, image-text, comparison, FAQ) exist, reusing them and the gallery images from B; D2 when D2a is approved and the packshot lands; G (on request) once the packshot exists.

## Phase 4 — QA loop
Read `references/10-qa-and-delivery.md`. Visual QA agent compares competitor screenshots vs local renders (`scripts/render_sections.js` + static buy-box mock) at desktop and mobile; master fixes; loop until no unintended discrepancies. Review every image/ad batch through `scripts/contact_sheet.py` before calling it done. `validate_schemas.py` must report 0 errors and `shopify theme check` no new offenses. After every push, read the push log ("pushed with errors" = not delivered: fix and re-push) and pull `templates/*` from the theme to confirm the product and home templates exist remotely.

## Phase 5 — Delivery (master)
Commit on the brand branch, pull + merge-check, push to GitHub; push to the draft theme if STORE/THEME_ID are known (never publish). Push the policies with `policies.py push` (needs STORE + SHOPIFY_ADMIN_TOKEN; otherwise deliver the files and add the to-do). Write `DELIVERY.md` (template). Show the operator contact sheets (product images, ads) and a short summary: what was built (product page + home page), image placeholder map, operator to-dos (shipping rates for every market first: without them Shopify shows every product as sold out and add to cart fails; variants, uploads, gift/bundle app, reviews app, home product links), credits spent.
