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
- **Advertorial capture** (when ads point to non-product-page URLs) — `scripts/capture_page.py` + `scripts/screenshot.py` for each unique advertorial/pre-sell URL found in `ad_inventory.json` → `02_competitor/advertorials/<slug>/` + `ADVERTORIAL_INVENTORY.md`. Runs after the ad footprint is pulled (the inventory tells us which URLs to capture). Skip if every ad points to the product page. `references/22-native-ads-and-advertorials.md` §5.

<a id="phase-alpha"></a>
## Phase α — Step Alpha (pre-launch intelligence)
Runs after Phase 1 and before Phase 2. Nothing is built or generated until α6 passes (00 §17). Spec, authoritative for every field, table and checkbox: `references/19-step-alpha.md`. How to run each step: `references/20-step-alpha-runbook.md`. All outputs in `00_alpha/` (tree in 18 §1).

| Step | Who | Reads | Output |
|---|---|---|---|
| α0 Inputs | master | competitor URL(s), Phase 1 capture, complete ad footprint, transcripts | `00_alpha/ad_inventory.json`, `00_alpha/transcripts/<ad_id>.txt` (every video ad) |
| α1.1 Customer intelligence | Lead A (brief Lead A α) | page capture + copy, reviews/testimonials/FAQ, ad copy, transcripts | `analysis1/1.1_customer.md` (avatars, pains, desires, objections, emotional landscape with all 6 trigger types, unique mechanism) |
| α1.2 Advertising intelligence | Lead B + Sonnet α-analyst workers in batches (~15 ads each) + Haiku worker for `alpha_gate.py beats` per transcript | `ad_inventory.json`, transcripts (frameworks come from them; no Gemini), ad media in `05_ads/competitor/videos/` + `images/` | `analysis1/1.2_ad_inventory.md`, `1.2_video_ads.md` (every video: framework, beat map … CTA), `1.2_static_ads.md` (every non-video ad), `1.2_patterns.md` |
| α1.3 Funnel congruence | Lead A (after 1.2 per-ad tags) | 1.2 tags, page capture + screenshots, advertorial captures (1.5) when they exist | `analysis1/1.3_congruence.md` (every ad→page path mapped and scored — extended to ad→advertorial→page when advertorial funnels exist (22 §6); insights) |
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
| A1 Section spec + funnel psychology + **ADAPTATION BLUEPRINT** | conversion-architect agent (Opus 4.6: framework mapping → adapted page architecture) | 03 | `02_competitor/page/SECTION_SPEC.md` (competitor analysis + adaptation blueprint) |
| A2 Page copy (**fully original**, no 1:1 titles, through copy chief with playbooks) | copywriter agent (Opus 4.6, after A1) | 03 §copy rules, 04, 13 | copy deck (returned text → master saves) |
| A3 Build (**adapted version**, not pixel-clone) | builder agent (Opus 4.6) | 04, tools-shopify-cli-and-git | theme settings, sections, blocks, template — adapted design, not a pixel-perfect clone |
| A4 Home page (**adapted version**, not pixel-clone) | home-page agent (Opus 4.6; after A3's shared settings + reusable sections exist; can start with spec/copy right after the gate) | 11, 04 | `templates/index.json` + `<slug>-*` home sections, adapted from the competitor home, **complete with no admin setup** (hero + product cards from theme assets/static settings, no native product-list/hero; 11 §4) |
| A5 Advertorial pages (when competitor uses advertorial funnels) | advertorial-builder agent (Opus 4.6; after A1 + dossier; skip if no advertorial funnel detected in 1.5) | 22 | `09_advertorials/` — one adapted advertorial per major angle card, fully original editorial copy through copy chief with playbooks, built as Shopify page template; Step Alpha data drives the content |
| B0 Image bank top-up (every launch) | coordinator (Brandsearch search_products) + sonnet worker (pull public galleries, classify) | 05 §16.0 | `PRODUCTS_ROOT/_image-bank/`: this launch's category + up to 10 brands from niches not yet covered; INDEX.md updated (coverage, by job, sequences, patterns) |
| B Product images (**own conversion gallery**, not 1:1 remakes) | image agent; headlines via the copy chief (Opus 4.6) | 05 §16, tools-kie | packshot first (real packaging) → `GALLERY_PLAN.md` (slot job, angle, objection, headline, proof, visual) → our gallery → `03_product-images/` |
| C Page images + GIFs | image agent | 06, tools-kie | testimonials/section remakes, WebP → `04_page-images/`, theme assets |
| D2a Ad variants | ad-creative agent (dossier 3.1 angle cards, 3.3 hooks, 3.5 language) | 08 §1b | `05_ads/AD_VARIANTS.md` (angle card ID per variant) → **operator gate** |
| D2 Ad creatives | ad-creative agent or master (after approval + packshot) | 08, tools-kie | 25 ads → `05_ads/generated/` (includes native ad formats when the competitor runs them; 22 §8) |
| E Ad copy | copy agent (dossier angle cards, hook library, language bank, objection phrases) | 09 | `05_ads/AD_COPY.md` (root of 05_ads, one copy set shared by image and video ads) |
| G Video ads (on request) | video agent (dossier 1.8/3.4 frameworks + beat maps, angle cards, hooks; after the packshot + operator-confirmed candidates) | 14 | `05_ads/generated/videos/vNN-<slug>.mp4` + `vNN-work/` (clips sheet, draft, PLAN) |
| I Product import file | master (small, after B gallery + BRIEF offer) | `scripts/product_csv.py` | `08_shopify/products.spec.json` → `08_shopify/<slug>-products.csv` (Shopify Admin > Products > Import: every product to create, title/handle/vendor/type/tags/description, options + all variants, price + compare-at, SKUs, inventory not tracked, status draft, SEO) + `<slug>-products.UPLOAD.md` (template suffix to set, gallery upload order, variant images by colour, shipping-rates reminder). Image cells filled only with `--image-base-url`; otherwise images are listed for upload |
| H Checkout header | master (small, after branding + C) | `scripts/checkout_header.py`, mockup `templates/checkout-header-mockup.png` | `07_checkout/<brand>-checkout-header.png` (+@2x): logo, "trusted by" gradient bar (brand colors) with 3 real-looking customer faces cropped from our page images, 3 trust points in the store language. Config `07_checkout/checkout_header.json`; strip metadata; operator uploads it in Settings > Checkout > Customize > Header |
| F Policies | master (small) | 12 | `policies.py transform` → `06_policies/<handle>.html` + REVIEW.md (1:1 text, brand/domain/email swapped, addresses/phones/registration numbers removed) |

**Sample gate (00 §18):** B+C generate a shared ~5-image sample first (packshot, gallery hero, one graphic slide, one person image, one page image) and stop for the operator's OK; D2 generates its first ~5 ads after the variants gate and stops again; full batches only after each OK.

Order inside the window (Step Alpha has already passed, so every stream can read the dossier from the start): start A1, B (packshot first), C, D2a, E and A4's home spec at once. A1 now produces both the competitor framework analysis AND the ADAPTATION BLUEPRINT (how our page diverges) before A2 starts — A2 cannot begin without knowing the adapted section structure and angle assignments. A2 when A1 lands (the copywriter writes fully original copy using playbooks, never 1:1 titles); A3 when A2 lands (the builder constructs the adapted design, not a pixel-clone; settings/header/footer can start immediately); A4 builds once A3's settings and reusable sections (testimonials, image-text, comparison, FAQ) exist, reusing them and the gallery images from B; A5 (advertorial pages) can start once A1 lands and the advertorial captures (1.5) exist — it needs the adaptation blueprint's visual identity rules for consistency across the store (skip A5 entirely if no advertorial funnel was detected in 1.5); D2 when D2a is approved and the packshot lands; G (on request) once the packshot exists. A1, A2, A3, A4, A5 and the copy chief all run on Opus 4.6 (operator mandate 2026-11-12).

## Phase 4 — QA loop
Read `references/10-qa-and-delivery.md`. Visual QA agent compares competitor screenshots vs local renders (`scripts/render_sections.js` + static buy-box mock) at desktop and mobile; master fixes; loop until no unintended discrepancies. Review every image/ad batch through `scripts/contact_sheet.py` before calling it done. `validate_schemas.py` must report 0 errors and `shopify theme check` no new offenses. After every push, read the push log ("pushed with errors" = not delivered: fix and re-push) and pull `templates/*` from the theme to confirm the product and home templates exist remotely.

## Phase 5 — Delivery (master)
Commit on the brand branch, pull + merge-check, push to GitHub; push to the draft theme if STORE/THEME_ID are known (never publish). Push the policies with `policies.py push` (needs STORE + SHOPIFY_ADMIN_TOKEN; otherwise deliver the files and add the to-do). Write `DELIVERY.md` (template). Show the operator contact sheets (product images, ads) and a short summary: what was built (product page + home page), image placeholder map, operator to-dos (shipping rates for every market first: without them Shopify shows every product as sold out and add to cart fails; variants, uploads, gift/bundle app, reviews app, home product links), credits spent.
