# 17 — Phases 0–5 (what to do, who does it, which reference to read)

Detail behind `SKILL.md` (formerly its §4). Phase 3 holds the stream table that QA checks row by row (10 §1).

## Contents
- Phase 0 — Intake and preflight
- Phase 1 — Competitor capture
- Phase 2 — Branding → GATE
- Phase 3 — Production (stream table + order inside the window)
- Phase 4 — QA loop
- Phase 5 — Delivery

---

## Phase 0 — Intake and preflight (master)
Read `references/01-intake-and-setup.md`. Parse inputs, confirm MARKET and PRODUCTS_ROOT, run preflight (git state, Shopify CLI, Python+Pillow, Node, Edge/Chrome, Kie key + credit balance, Brandsearch MCP), create the PRODUCT_DIR tree, write BRIEF.md from `templates/BRIEF.md`.

## Phase 1 — Competitor capture (parallel, ~immediately)
Launch together:
- **Capture agent** — `scripts/capture_page.py` + `scripts/screenshot.py` → `02_competitor/page/` (product JSON, HTML, copy, colors, fonts, apps/bundle tiers, media URLs, screenshots) **and the competitor home page** → `02_competitor/home/` (HTML, copy, media URLs, full-page screenshots). Read `references/03-competitor-page-analysis.md` §capture and `references/11-home-page.md` §capture.
- **Media agent** — `scripts/fetch_media.py --from-capture` → `02_competitor/media/` (gallery images, **raw GIFs**, testimonial and section images) + WebP conversions. `references/06-page-images-and-gifs.md`.
- **Master** — Brandsearch pulls (both endpoints) into `05_ads/competitor/raw/`, then `scripts/rank_ads.py`. `references/07-ads-research-brandsearch.md`.
- **Policies** — `scripts/policies.py fetch` → `06_policies/source/` (all competitor policy pages). `references/12-policies.md`.

## Phase 2 — Branding → GATE (master)
Read `references/02-branding.md`. From capture data: competitor snapshot table, 7–10 brand names (top 3 starred, possessive test), palette 1:1 (exact hex + roles), product title 1:1. Save `01_branding/BRANDING.md` (template `templates/BRANDING.md`). **Stop and present** (in the same message, ask for our domain + support email if unknown — needed for the policies). On approval: record decisions in BRIEF, create the git branch `BRAND_SLUG` from clean `main` (01-intake §git).

## Phase 3 — Production (parallel streams after the gate)
| Stream | Who | Reference | Output |
|---|---|---|---|
| A1 Section spec + funnel psychology | conversion-architect agent | 03 | `02_competitor/page/SECTION_SPEC.md` |
| A2 Page copy | copywriter agent (after A1) | 03 §copy rules, 04 | copy deck (returned text → master saves) |
| A3 Build | master (or builder agent) | 04, tools-shopify-cli-and-git | theme settings, sections, blocks, template |
| A4 Home page | home-page agent (after A3's shared settings + reusable sections exist; can start with spec/copy right after the gate) | 11, 04 | `templates/index.json` + `<slug>-*` home sections, 1:1 with the competitor home, **complete with no admin setup** (hero + product cards from theme assets/static settings, no native product-list/hero; 11 §4) |
| B Product images | image agent | 05, tools-kie | packshot first, then gallery remakes → `03_product-images/` |
| C Page images + GIFs | image agent | 06, tools-kie | testimonials/section remakes, WebP → `04_page-images/`, theme assets |
| D1 Ad analysis | 2 analyst agents (ranks 1–15, 16–30) | 07 | text → master compiles `05_ads/COMPETITOR_ADS.md` |
| D2a Ad variants | ad-creative agent (after D1) | 08 §1b | `05_ads/AD_VARIANTS.md` → **operator gate** |
| D2 Ad creatives | ad-creative agent or master (after approval + packshot) | 08, tools-kie | 25 ads → `05_ads/generated/` |
| E Ad copy | copy agent (after D1) | 09 | `05_ads/AD_COPY.md` (root of 05_ads, one copy set shared by image and video ads) |
| G Video ads (on request) | video agent (after the packshot + operator-confirmed candidates) | 14 | `05_ads/generated/videos/vNN-<slug>.mp4` + `vNN-work/` (clips sheet, draft, PLAN) |
| I Product import file | master (small, after B gallery + BRIEF offer) | `scripts/product_csv.py` | `08_shopify/products.spec.json` → `08_shopify/<slug>-products.csv` (Shopify Admin > Products > Import: every product to create, title/handle/vendor/type/tags/description, options + all variants, price + compare-at, SKUs, inventory not tracked, status draft, SEO) + `<slug>-products.UPLOAD.md` (template suffix to set, gallery upload order, variant images by colour, shipping-rates reminder). Image cells filled only with `--image-base-url`; otherwise images are listed for upload |
| H Checkout header | master (small, after branding + C) | `scripts/checkout_header.py`, mockup `templates/checkout-header-mockup.png` | `07_checkout/<brand>-checkout-header.png` (+@2x): logo, "trusted by" gradient bar (brand colors) with 3 real-looking customer faces cropped from our page images, 3 trust points in the store language. Config `07_checkout/checkout_header.json`; strip metadata; operator uploads it in Settings > Checkout > Customize > Header |
| F Policies | master (small) | 12 | `policies.py transform` → `06_policies/<handle>.html` + REVIEW.md (1:1 text, brand/domain/email swapped, addresses/phones/registration numbers removed) |

Order inside the window: start A1, B (packshot first), C, D1 and A4's home spec at once; A2 when A1 lands; A3 when A2 lands (settings/header/footer can start immediately); A4 builds once A3's settings and reusable sections (testimonials, image-text, comparison, FAQ) exist, reusing them and the gallery images from B; D2 when D1 + packshot land; E when D1 lands.

## Phase 4 — QA loop
Read `references/10-qa-and-delivery.md`. Visual QA agent compares competitor screenshots vs local renders (`scripts/render_sections.js` + static buy-box mock) at desktop and mobile; master fixes; loop until no unintended discrepancies. Review every image/ad batch through `scripts/contact_sheet.py` before calling it done. `validate_schemas.py` must report 0 errors and `shopify theme check` no new offenses. After every push, read the push log ("pushed with errors" = not delivered: fix and re-push) and pull `templates/*` from the theme to confirm the product and home templates exist remotely.

## Phase 5 — Delivery (master)
Commit on the brand branch, pull + merge-check, push to GitHub; push to the draft theme if STORE/THEME_ID are known (never publish). Push the policies with `policies.py push` (needs STORE + SHOPIFY_ADMIN_TOKEN; otherwise deliver the files and add the to-do). Write `DELIVERY.md` (template). Show the operator contact sheets (product images, ads) and a short summary: what was built (product page + home page), image placeholder map, operator to-dos (shipping rates for every market first: without them Shopify shows every product as sold out and add to cart fails; variants, uploads, gift/bundle app, reviews app, home product links), credits spent.
