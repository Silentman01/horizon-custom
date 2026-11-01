---
name: run-product
description: >-
  Run a complete e-commerce product launch from a competitor product URL in one prompt — branding (brand name, palette, title), competitor page capture and section spec, Shopify product page AND home page (index) built 1:1 from the competitor in the current theme (sections/blocks/templates, original copy), product image remakes, page images and raw GIFs, store policies cloned 1:1 (brand/domain/email swapped, private info removed) and pushed, competitor Meta ad research with Brandsearch MCP (top 30 creatives ranked by impressions rank), 25 ad creatives with Kie.ai GPT Image 2.5, and ad copy (primary text, headlines, description), plus remakes of the competitor's top video ads on request (scene audit, cloned-voice re-voice, captions, regenerated product clips). Use this skill whenever the user gives a competitor/product URL and wants to "run", "launch", "test", "clone", "do 1:1", "copy this product", build a product page or home page, make product images, or make ads for a product — even if they only name one of these steps (e.g. "do this product: https://…", "start with branding", "get their top ads and make ours", "remake their images for our brand"). Works in any Shopify theme repo (Horizon, Dawn, other OS 2.0) and orchestrates parallel sub-agents.
---

# Run Product

Turn one competitor product URL into a launch-ready product: brand, product page, home page, policies, product images, page media, ad creatives and ad copy. The **coordinator** (you) owns decisions, gates, Brandsearch calls, git/Shopify pushes and the final report; **two Opus 5.5 leads (low effort)** run the Store and Growth streams and direct cheap **Sonnet/Haiku workers** for the heavy parallel work ([16 §1](references/16-orchestration.md#1-orchestration-model-coordinator--2-opus-leads--cheap-workers)).

This workflow was distilled from a real run (brand *Noxis*, cloning plaims.com headlight glasses). Every rule in `references/00-operator-rules.md` exists because the operator corrected it once — read it before anything else, every run.

**This file is the index.** Run the phases in order (streams inside a phase run in parallel), open the linked reference before each step, tick the done-checklist at the end. All detail lives in the linked files; nothing here replaces them.

## Always-on rules
- [00 Operator rules](references/00-operator-rules.md) — full text, read first every run; one-line [summary](references/00-operator-rules.md#operator-rules-summary--full-text-in-the-sections-above) at its end.
- Claims at full strength: [00 §1](references/00-operator-rules.md#1-claims--keep-them-at-full-strength). 1:1 for tests (+ brand-guideline exception): [00 §2](references/00-operator-rules.md#2-11-testing--reuse-what-already-works). Persuasive copy goes through the copy chief: [13](references/13-copy-playbooks.md).
- Mobile first (390px, rails drag): [00 §11b](references/00-operator-rules.md#11b-mobile-first). No placeholder labels: [00 §11](references/00-operator-rules.md#11-no-placeholder-or-example-labels-operator-2026-10-18). Header defaults: [00 §12](references/00-operator-rules.md#12-header-defaults-operator-2026-10-18). Fully customizable sections: [00 §13](references/00-operator-rules.md#13-fully-customizable-sections-and-blocks-operator-2026-10-18). Unique CSS prefixes: [00 §15](references/00-operator-rules.md#15-unique-css-class-prefixes-per-section-2026-10-19).
- Strip metadata from all AI media: [00 §14](references/00-operator-rules.md#14-strip-metadata-from-ai-generated-media-operator-2026-10-18) · [tools-kie final step](references/tools-kie.md#final-step-for-every-batch).
- Home page renders complete with zero admin setup: [11 §4](references/11-home-page.md#4-map-components-to-the-theme).
- Files: assets in `PRODUCT_DIR`, not the theme repo: [00 §10](references/00-operator-rules.md#10-files-and-organisation). Folder hygiene: [18 §1](references/18-folders-scripts-credits.md#1-folders-scripts-templates) · [10 §1](references/10-qa-and-delivery.md#1-what-done-means).
- Git and pushes (brand branch from clean `main`, commit → pull → merge-check → push, never publish, live-traffic templates): [00 §8–9](references/00-operator-rules.md#8-git-branches-and-pushes) · [tools-shopify §1](references/tools-shopify-cli-and-git.md#1-golden-rules). Schema validation before every push + remote check after: [10 §2](references/10-qa-and-delivery.md#2-page-qa) · [10 schema checks](references/10-qa-and-delivery.md#schema-checks-theme-check-misses-aurea-push-2026-10-17) · [17 Phase 4](references/17-phases-and-streams.md#phase-4--qa-loop).
- Credits: check before batches, prioritise if short, report spend: [18 §2](references/18-folders-scripts-credits.md#2-credits-and-costs) · [tools-kie §6](references/tools-kie.md#6-credit-check-and-budgeting).
- Inputs, one-prompt contract and gates: [15 §1](references/15-inputs-and-run-contract.md#1-inputs-and-the-one-prompt-contract). Reporting style: [15 §2](references/15-inputs-and-run-contract.md#2-reporting-to-the-operator). Partial runs / resume from BRIEF.md: [15 §3](references/15-inputs-and-run-contract.md#3-partial-runs-and-resuming).
- Who does what (coordinator → Lead A Store / Lead B Growth → workers, models, constraints): [16 §1](references/16-orchestration.md#1-orchestration-model-coordinator--2-opus-leads--cheap-workers). Briefs: [subagent-briefs](references/subagent-briefs.md). Dependency map: [16 §2](references/16-orchestration.md#2-dependency-map).

## Steps (phases in execution order)
Phase 3 streams are listed in stream-table order; their real start order and dependencies are in [17 P3 “Order inside the window”](references/17-phases-and-streams.md#phase-3--production-parallel-streams-after-the-gate) and [16 §2](references/16-orchestration.md#2-dependency-map). Phase detail: [17](references/17-phases-and-streams.md). `PD` = `PRODUCT_DIR` ([18 §1](references/18-folders-scripts-credits.md#1-folders-scripts-templates) tree).

**Phase 0 — Intake and preflight** (coordinator) · [17 P0](references/17-phases-and-streams.md#phase-0--intake-and-preflight-master) · [01](references/01-intake-and-setup.md)
- 0.1 Parse inputs, ask only blocking questions → input table in BRIEF.md · [15 §1](references/15-inputs-and-run-contract.md#1-inputs-and-the-one-prompt-contract) · [01 Step 1](references/01-intake-and-setup.md#step-1--parse-the-prompt) · [Step 2](references/01-intake-and-setup.md#step-2--ask-only-blocking-questions)
- 0.2 Preflight (git, Shopify CLI, Python+Pillow, Node, browser, Kie key + credits, Brandsearch MCP, Admin token) → BRIEF "Tooling" · [01 Step 3](references/01-intake-and-setup.md#step-3--preflight-checks)
- 0.3 PRODUCT_DIR tree + BRIEF.md → `PRODUCTS_ROOT/_<competitor-slug>/` · [01 Step 4](references/01-intake-and-setup.md#step-4--create-product_dir-and-briefmd) · `templates/BRIEF.md`
- 0.4 Hand-off: launch Phase 1 (+ both leads in one message after the Brandsearch dumps) · [01 Step 6](references/01-intake-and-setup.md#step-6--hand-off-to-phase-1) · [16 §1](references/16-orchestration.md#1-orchestration-model-coordinator--2-opus-leads--cheap-workers) · [Lead briefs](references/subagent-briefs.md#lead-briefs-launch-both-in-one-message-model-opus-effort-low-background)

**Phase 1 — Competitor capture** (parallel, before the gate) · [17 P1](references/17-phases-and-streams.md#phase-1--competitor-capture-parallel-immediately)
- 1.1 Capture product + home → `PD/02_competitor/page/`, `PD/02_competitor/home/` · [03 §3–5](references/03-competitor-page-analysis.md#3-step-1-capture-the-page-data-capture_pagepy) · [11 §2](references/11-home-page.md#2-capture-the-competitor-home) · `capture_page.py`, `screenshot.py` · brief 1
- 1.2 Media raw (gallery, GIFs, section images) + WebP → `PD/02_competitor/media/` · [06](references/06-page-images-and-gifs.md#3-step-2--download-everything-raw) · `fetch_media.py` · brief 2
- 1.3 Brandsearch pulls + ranking (coordinator) → `PD/05_ads/competitor/` · [07 Steps 1–6](references/07-ads-research-brandsearch.md#ranking-logic-by-market-read-first-because-it-decides-everything-below) · [tools-brandsearch](references/tools-brandsearch.md) · `rank_ads.py`
- 1.4 Policies fetch → `PD/06_policies/source/` · [12 §3](references/12-policies.md#3-fetch) · `policies.py fetch`

**Phase 2 — Branding → GATE** (coordinator) · [17 P2](references/17-phases-and-streams.md#phase-2--branding--gate-master) · [02](references/02-branding.md)
- 2.1 Snapshot, 7–10 names, palette 1:1, typography, title 1:1 → `PD/01_branding/BRANDING.md` · [02 §3–9](references/02-branding.md#3-step-1-load-the-capture) · `templates/BRANDING.md` · brief 3 (optional)
- 2.2 **GATE**: present, ask domain + support email if unknown; iterate · [02 §9–10](references/02-branding.md#9-step-7-write-brandingmd-and-present-the-gate)
- 2.3 After approval: record in BRIEF, rename PD, brand branch from clean `main`, logo set → `PD/01_branding/logo/` · [02 §11](references/02-branding.md#11-step-9-after-approval-record-rename-branch) · [01 Step 5](references/01-intake-and-setup.md#step-5--git-setup) · [tools-shopify §3](references/tools-shopify-cli-and-git.md#3-branch-per-brand) · `brand_icons.py`

**Phase 3 — Production streams** (parallel after the gate) · [17 P3 stream table + order inside the window](references/17-phases-and-streams.md#phase-3--production-parallel-streams-after-the-gate)
- A1 Section spec + funnel psychology → `PD/02_competitor/page/SECTION_SPEC.md` · [03 §6–13](references/03-competitor-page-analysis.md#6-step-4-build-the-section-inventory) · `templates/SECTION_SPEC.md` · brief 4
- A2 Page copy (after A1) → copy deck (returned text, saved by coordinator) · [03 §14](references/03-competitor-page-analysis.md#14-copy-rules-for-the-copywriter-downstream) · [04](references/04-product-page-build.md) · [13](references/13-copy-playbooks.md) · brief 5, copy chief
- A3 Build product page → theme settings, sections, blocks, template, bundle selector ([04 §5.4](references/04-product-page-build.md#54-bundle-picker-parent-block--tier-blocks--js-driver)), cart drawer ([04 §5.12](references/04-product-page-build.md#512-cart-drawer)), sticky add to cart ([04 §5.13](references/04-product-page-build.md#513-sticky-add-to-cart)) · [04](references/04-product-page-build.md) · [tools-shopify](references/tools-shopify-cli-and-git.md) · brief 6 (optional)
- A4 Home page → `templates/index.json` + `<slug>-*` home sections · [11](references/11-home-page.md) · [04](references/04-product-page-build.md) · brief 13
- B Product images (packshot first, then gallery remakes) → `PD/03_product-images/` · [05](references/05-product-images.md) · [tools-kie](references/tools-kie.md) · `kie_jobs.py`, `contact_sheet.py` · brief 7
- C Page images + GIFs → `PD/04_page-images/`, theme assets · [06](references/06-page-images-and-gifs.md) · [tools-kie](references/tools-kie.md) · brief 8
- D1 Ad analysis (2 analysts) → `PD/05_ads/COMPETITOR_ADS.md` · [07 Steps 7–10](references/07-ads-research-brandsearch.md#step-7--analyze-with-2-sub-agents-15-ads-each-in-parallel) · `templates/COMPETITOR_ADS.md` · brief 9
- D2a Ad variants (after D1) → `PD/05_ads/AD_VARIANTS.md` → **operator GATE** · [08 §1b](references/08-ad-creatives.md#1b-variants-gate-before-any-generation--operator-rule-7) · [00 §7](references/00-operator-rules.md#7-ad-creatives-and-copy) · brief 10, copy chief
- D2 Ad creatives (after approval + packshot) → 25 ads in `PD/05_ads/generated/` · [08](references/08-ad-creatives.md) · [tools-kie](references/tools-kie.md) · `kie_jobs.py` · brief 10
- E Ad copy (after D1) → `PD/05_ads/AD_COPY.md` · [09](references/09-ad-copy.md) · `templates/AD_COPY.md` · brief 11, copy chief
- G Video ads (on request; candidates → **operator GATE**, (c) clips → second OK) → `PD/05_ads/generated/videos/vNN-<slug>.mp4` + `vNN-work/` · [14](references/14-video-ads.md) · [00 §16](references/00-operator-rules.md#16-video-ad-remakes-operator-2026-10-24--full-workflow-in-14-video-adsmd) · `video_*.py`
- I Product import file → `PD/08_shopify/<slug>-products.csv` + `.UPLOAD.md` · [17 P3 row I](references/17-phases-and-streams.md#phase-3--production-parallel-streams-after-the-gate) · `product_csv.py`
- H Checkout header → `PD/07_checkout/<brand>-checkout-header.png` (+@2x) · [17 P3 row H](references/17-phases-and-streams.md#phase-3--production-parallel-streams-after-the-gate) · `checkout_header.py`, `templates/checkout-header-mockup.png`
- F Policies transform → `PD/06_policies/<handle>.html` + REVIEW.md · [12 §4–5](references/12-policies.md#4-transform-rules) · `policies.py transform` · brief 14 (optional)

**Phase 4 — QA loop** · [17 P4](references/17-phases-and-streams.md#phase-4--qa-loop) · [10 §1–4](references/10-qa-and-delivery.md#1-what-done-means)
- 4.1 Page QA (local render, section compare, behaviour, static checks) · [10 §2](references/10-qa-and-delivery.md#2-page-qa) · `render_sections.js`, `validate_schemas.py`, `shopify theme check` · brief 12 (visual QA)
- 4.2 Image and ad QA on contact sheets · [10 §3](references/10-qa-and-delivery.md#3-image-and-ad-qa) · `contact_sheet.py`
- 4.3 Discrepancy log → `PD/scratch/QA_LOG.md`, loop until only fixed/intentional · [10 §4](references/10-qa-and-delivery.md#4-discrepancy-log-and-loop)

**Phase 5 — Delivery** (coordinator) · [17 P5](references/17-phases-and-streams.md#phase-5--delivery-master)
- 5.1 Commit → pull → merge-check → push (GitHub; draft theme if known, never publish), then read the push log and pull `templates/*` · [10 §5](references/10-qa-and-delivery.md#5-push-and-merge-safety) · [tools-shopify §4–8](references/tools-shopify-cli-and-git.md#4-committing) · [17 P4](references/17-phases-and-streams.md#phase-4--qa-loop)
- 5.2 Policies push (or files + to-do) · [12 §6](references/12-policies.md#6-push) · `policies.py push`
- 5.3 Folder hygiene + SHA-256 dedupe at delivery; `PD/DELIVERY.md` · [18 §1](references/18-folders-scripts-credits.md#1-folders-scripts-templates) · [10 §6](references/10-qa-and-delivery.md#6-delivery-report) · `templates/DELIVERY.md`
- 5.4 Final message (result, contact sheets, to-dos, credits) · [10 §7](references/10-qa-and-delivery.md#7-final-message-to-the-operator) · [15 §2](references/15-inputs-and-run-contract.md#2-reporting-to-the-operator)

## Done-checklist (definition of done: [10 §1](references/10-qa-and-delivery.md#1-what-done-means))
Every Phase 3 stream needs its output on disk; a stop instruction skips only that stream, a missing file = not done ([10 §1](references/10-qa-and-delivery.md#1-what-done-means)).
- [ ] 0.1–0.4 BRIEF.md with inputs, tooling, credits; PD tree exists; Phase 1 launched
- [ ] 1.1 product + home capture and screenshots · 1.2 raw media + WebP · 1.3 dumps + ranking · 1.4 policy sources
- [ ] 2.1 BRANDING.md · 2.2 gate approved · 2.3 BRIEF updated, PD renamed, logo set, brand branch
- [ ] A1 SECTION_SPEC.md · A2 copy deck · A3 product page built (bundle selector + cart drawer configured + sticky add to cart) · A4 home page built (no admin setup)
- [ ] B packshot + gallery · C page images + WebP · D1 COMPETITOR_ADS.md · D2a AD_VARIANTS.md approved · D2 25 ads · E AD_COPY.md
- [ ] G video finals (only if requested) · I products CSV + UPLOAD.md · H checkout header · F policies transformed
- [ ] 4.1 page QA + `validate_schemas.py` 0 errors + theme check no new offenses · 4.2 every batch on a contact sheet · 4.3 QA log only fixed/intentional
- [ ] 5.1 pushed, push log clean, templates confirmed remotely · 5.2 policies pushed or to-do · 5.3 hygiene + DELIVERY.md · 5.4 final message

## Scripts and templates index
Usage, flags and notes: [18 §1](references/18-folders-scripts-credits.md#1-folders-scripts-templates). Run Python with `-I`; all have `--help`.
- `scripts/capture_page.py` — competitor page/home capture · 1.1
- `scripts/screenshot.py` — desktop + 390px mobile screenshots · 1.1
- `scripts/fetch_media.py` — raw media downloads + GIF→WebP · 1.2, B, C
- `scripts/rank_ads.py` — merge/dedupe/rank Brandsearch dumps · 1.3
- `scripts/policies.py` — `fetch` 1.4 · `transform` F · `push` 5.2
- `scripts/brand_icons.py` — square social logos + favicon · 2.3
- `scripts/kie_jobs.py` — Kie GPT Image 2.5 batch runner, `--credits` · B, C, D2
- `scripts/contact_sheet.py` — review grids · B, C, D2, 4.2
- `scripts/strip_metadata.py` — strip AI media metadata · every generated batch (00 §14)
- `scripts/render_sections.js` — local Liquid render + buy-box mock · A3, A4, 4.1
- `scripts/validate_schemas.py` — schema errors theme check misses · 4.1, before every push
- `scripts/product_csv.py` — Shopify product import CSV + UPLOAD.md · I
- `scripts/checkout_header.py` — checkout header image · H
- `scripts/video_clips.py`, `video_transcribe.py`, `video_vo.py`, `video_captions.py`, `video_finalize.py` — video remake pipeline · G ([14](references/14-video-ads.md))
- `scripts/video_eleven.py`, `video_build_stills.py` — ElevenLabs helper; video from our own stills + VO · named only in `scripts/VIDEO_AD_POLICY.md`
- `scripts/argolink_jobs.py` (ArgoLink GPT Image 2, drop-in for kie_jobs.py), `video_argolink.py` (ArgoLink image-to-video), `video_build_clips.py` (ad from generated clips + VO) — not referenced by any step
- `scripts/VIDEO_AD_POLICY.md` — video ad policy note (Mojo v01)
- Templates (`templates/`): `BRIEF.md` 0.3 · `BRANDING.md` 2.1 · `SECTION_SPEC.md` A1 · `COMPETITOR_ADS.md` D1 · `AD_COPY.md` E · `DELIVERY.md` 5.3 · `checkout-header-mockup.png` H
- `books-playbooks/*.html` — copy chief library · all persuasive copy ([13](references/13-copy-playbooks.md)) · `evals/evals.json` — trigger/behaviour evals
- Related, not a run-product step: the operator's separate video remake skill `D:\Ecom\Claude\skills\video-ad-remake\SKILL.md` (no step here points at it; this skill's video reference is [14](references/14-video-ads.md))
