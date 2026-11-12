# DELIVERY — <BRAND> (<product title>)

**Date:** <YYYY-MM-DD> · **Market:** <country / language / currency> · **Mode:** <A/B>

## Where everything is
| Item | Location |
|---|---|
| Theme branch | `<brand_slug>` on GitHub (<repo>) |
| Draft theme preview | <url or "not pushed — store needed"> |
| Product assets | `<PRODUCT_DIR>` |
| Step Alpha dossier | `00_alpha/ALPHA_DOSSIER.md` (+ `analysis1/`, `analysis2/`, `chatgpt/CHATGPT_PROMPT.md` + `CHATGPT_RAW.md`, `transcripts/`, `ad_inventory.json`) · quality gate: <pass, date> |
| Branding | `01_branding/BRANDING.md` |
| Section spec | `02_competitor/page/SECTION_SPEC.md` |
| Home spec | `02_competitor/home/HOME_SPEC.md` |
| Product images (gallery order) | `03_product-images/` |
| Page images / GIF WebP | `04_page-images/` + theme `assets/<slug>-*` |
| Competitor ads (complete footprint, top 30 ranked) | `05_ads/competitor/` (analysis: dossier 1.7–1.9) |
| Ad variants (angle card per ad) | `05_ads/AD_VARIANTS.md` |
| Our ads (25) | `05_ads/generated/` |
| Ad copy | `05_ads/AD_COPY.md` |
| Policies | `06_policies/<handle>.html` + `REVIEW.md` (pushed: yes/no) |

## Product page — what was built
| # | Section | Built as | Notes |
|---|---|---|---|
| 1 | Announcement bar | theme setting | |
| 2 | Buy box | template + custom blocks | |
| … | | | |

## Home page — what was built
| # | Competitor section | Our section (native / custom) | Notes |
|---|---|---|---|

## Image placeholder map
| Position | Ratio | Content | Status (file / still needed) |
|---|---|---|---|

## Operator to-dos
- [ ] Import the products: Admin > Products > Import > `08_shopify/<slug>-products.csv`, then follow `08_shopify/<slug>-products.UPLOAD.md` (template suffix, images in order, variant images, set Active)
- [ ] Upload product images in this order: …
- [ ] Free gift / bundle discount setup (display-only until configured)
- [ ] Install/enable reviews app and place its block
- [ ] Policies: confirm pushed (or paste `06_policies/*.html` into Settings → Policies); switch off the automated privacy policy if enabled
- [ ] Connect store / give draft theme id (if not done)
- [ ] Review ads and copy, then launch

## Credits spent
| Service | Credits |
|---|---|
| Kie (GPT Image 2.5) | |
| Brandsearch (footprint + transcripts) | |
| ArgoLink (Gemini video analysis) | |

## QA summary
- Step Alpha gate: <alpha_gate.py pass + read-through, date>
- Theme check: <baseline only / issues>
- Discrepancies fixed: <n> (see scratch/QA_LOG.md)
- Known minor flaws: <list or none>
