---
name: run-product
description: Run a complete e-commerce product launch from a competitor product URL in one prompt — branding (brand name, palette, title), competitor page capture and section spec, Shopify product page AND home page (index) built 1:1 from the competitor in the current theme (sections/blocks/templates, original copy), product image remakes, page images and raw GIFs, store policies cloned 1:1 (brand/domain/email swapped, private info removed) and pushed, competitor Meta ad research with Brandsearch MCP (top 30 creatives ranked by impressions rank), 25 ad creatives with Kie.ai GPT Image 2.5, and ad copy (primary text, headlines, description), plus remakes of the competitor's top video ads on request (scene audit, cloned-voice re-voice, captions, regenerated product clips). Use this skill whenever the user gives a competitor/product URL and wants to "run", "launch", "test", "clone", "do 1:1", "copy this product", build a product page or home page, make product images, or make ads for a product — even if they only name one of these steps (e.g. "do this product: https://…", "start with branding", "get their top ads and make ours", "remake their images for our brand"). Works in any Shopify theme repo (Horizon, Dawn, other OS 2.0) and orchestrates parallel sub-agents.
---

# Run Product

Turn one competitor product URL into a launch-ready product: brand, product page, home page, policies, product images, page media, ad creatives and ad copy. The **coordinator** (you) owns decisions, gates, Brandsearch calls, git/Shopify pushes and the final report; **two Opus 5.5 leads (low effort)** run the Store and Growth streams and direct cheap **Sonnet/Haiku workers** for the heavy parallel work (§3).

This workflow was distilled from a real run (brand *Noxis*, cloning plaims.com headlight glasses). Every rule in `references/00-operator-rules.md` exists because the operator corrected it once — read it before anything else, every run.

## Contents
1. Inputs and the one-prompt contract
2. Operator rules (summary)
3. Orchestration model
4. Phases 0–5 (what to do, who does it, which reference to read)
5. Dependency map and parallel streams
6. Folders, scripts, templates
7. Credits and costs
8. Reporting to the operator
9. Partial runs and resuming

---

## 1. Inputs and the one-prompt contract

Parse the prompt; ask only for what blocks progress.

| Input | Required | Default / how to get it |
|---|---|---|
| `COMPETITOR_URL` | yes | from the prompt (one or more product URLs) |
| `COMPETITOR_HOME` | no | the competitor's home page — default: the root of the first competitor domain (`https://plaims.com/`); if several competitors were sent, clone the home of the one whose product page is cloned unless told otherwise |
| `MARKET` (country, language, currency) | yes | ask if not stated — names, copy and currency depend on it (Noxis run: US, English, USD) |
| `BRAND` | no | produced in Phase 2; if the prompt names it, skip the branding gate |
| Brand guideline file | no | if given (palette, fonts, UI, product name) it overrides the 1:1 palette/fonts/title; copy it to `01_branding/` |
| `MODE` | no | **A — faithful clone** (default for product tests); B only if asked |
| `PRODUCTS_ROOT` | first run | ask once, then record in BRIEF (operator default `G:\Ecom\Products`) |
| `STORE` / draft `THEME_ID` | no | needed only to push a draft theme; otherwise push to GitHub and ask at delivery |
| `KIE_API_KEY` | for images/ads | env var, project skill config, or ask |
| `OUR_DOMAIN`, `SUPPORT_EMAIL` | for policies | ask at the branding gate if unknown (myshopify domain until a custom domain exists); never invent |
| `SHOPIFY_ADMIN_TOKEN` | to push policies | custom app Admin API token with `write_legal_policies`; without it policies are delivered as files + to-do |
| Brandsearch MCP | for ads | tools `mcp__claude_ai_Brandsearch__*`; if missing, tell the operator to connect it and continue the rest |

One prompt runs everything. The only planned stop is the **branding gate** (operator picks the brand). Everything else runs to completion, in parallel, and ends with one delivery report. If the operator says "start with branding, wait for validation", stop at the gate; if they say "go all the way", still stop at the gate unless the brand is already given.

## 2. Operator rules (summary — full text in `references/00-operator-rules.md`)

- **Claims stay at full strength.** Never soften, reword, remove or caveat claims ("Reduces Nighttime Glare By 85%", "Designed for cataract patients", "doctor-recommended"). The operator validates claims.
- **1:1 for tests.** Title = competitor's title pattern with our brand; palette = competitor's exact hex; page structure = competitor's (Mode A). Don't reinvent; upgrade later only when asked.
- **Brand names:** invented, one word, 2–3 syllables, passes "let me get my ___ glasses". Never filter by domain availability.
- **No logo on product images**; skip competitor-specific images (anti-replica notices); edit existing images when only text changes.
- **GIFs raw**: download originals, keep them, use animated WebP in the theme.
- **Ads ranking: Brandsearch "Top rank (by impressions)" (`reach_rank`) first; spend/reach only when targeting EU markets; days running + duplicates as tie-breakers.** Filter to the product keyword. Dedupe by image hash.
- **Copy chief + playbooks:** all persuasive copy (ad headline variants, ad copy, page/home copy, image claims, offers) is written or punched up by an Opus copy-chief agent using `books-playbooks/` — no softness, calibrated to the competitor's proven framework and promise level, sharpened with the playbooks (`references/13-copy-playbooks.md`).
- **Every ad prompt attaches our packshot**; no competitor brand names. **Before generating any ad**, write `05_ads/AD_VARIANTS.md` (each source headline → our almost-similar variant; each design → our close-but-different variant) and stop for operator validation; after approval generate and keep going (08 §1b).
- **Video ads** (on request, `references/14-video-ads.md`): ~20 candidates by `reach_rank` → operator confirms; per video, audit every clip (a clean / b overlay fixed locally / c regenerate); no lip sync; re-voice with an ElevenLabs clone of the original voice (never Kie for audio); always remake the hook, the end and one random body line; (c) clips only after operator confirmation; `generated/videos/` holds finals only.
- **Git:** branch named after the brand from clean `main`; commit → pull → merge-check → push; never publish; never overwrite a template with live ad traffic.
- **Assets live in `PRODUCT_DIR`** (shop folder), not in the theme repo.
- **Mobile first:** build and QA at 390px first; every horizontal rail scrolls by touch *and* mouse drag (editor mobile preview has no touch).

## 3. Orchestration model (coordinator → 2 Opus leads → cheap workers)

Cost rule: expensive reasoning only where judgment matters; everything mechanical runs on the cheapest model that can do it. Model guide: https://platform.claude.com/docs/en/about-claude/models/choosing-a-model (Opus = hardest reasoning, Sonnet = balanced quality/cost for writing, code and vision, Haiku = fastest/cheapest for mechanical work).

| Tier | Who | Model / effort | Owns |
|---|---|---|---|
| Coordinator | the main session (you) | operator's session model | inputs, gates, Brandsearch MCP pulls (dump to files), git + Shopify pushes, final acceptance, BRIEF.md |
| **Lead A — Store lead** | `Agent`, `model: "opus"`, `effort: "low"` | Opus 5.5, low | capture → SECTION_SPEC → copy → build (product + home) → policies → page QA |
| **Lead B — Growth lead** | `Agent`, `model: "opus"`, `effort: "low"` | Opus 5.5, low | packshot → gallery remakes → page images/GIFs → ad analysis → 25 ads → ad copy |
| Workers (writing, code, vision) | spawned by a lead | `model: "sonnet"` | conversion architect, copywriter, section builder, ad analysts, image-prompt writers, ad copy, visual QA |
| Workers (mechanical) | spawned by a lead | `model: "haiku"` | capture/screenshot/fetch scripts, downloads, GIF→WebP, contact sheets, policies fetch/transform, rank_ads runs, theme check runs |

How it runs:
1. Coordinator finishes Phase 0, pulls Brandsearch dumps, then launches **both leads in one message** (background), each with its lead brief from `references/subagent-briefs.md` (§Lead A / §Lead B) + BRIEF.md path.
2. Each lead plans its stream, launches its workers in parallel with explicit `model` values, verifies every return itself (opens images, reads files, runs checks) and only escalates a task to itself (Opus) when a worker failed twice or the task needs judgment (claims, 1:1 fidelity calls, fixing a broken build).
3. Leads write code/JSON/images directly; documents come back as text and the lead (or coordinator) saves them. Leads never push, publish or call Brandsearch; they report "ready to push" with a file list.
4. Coordinator reviews the two lead reports, runs the push sequence (commit → pull → merge-check → push), writes DELIVERY.md.
5. If a lead can't spawn workers (no `Agent` tool in its context), it does the worker steps itself and keeps outputs short; the model split still applies to whatever the coordinator spawns.

Constraints:
- Sub-agents may be refused when writing report/markdown files ("Subagents should return findings as text") → return documents as text.
- Workers get only the context they need (paths + exact task); leads keep the big picture. Never duplicate a running agent's work; process completions as they arrive; resume a stalled agent with `SendMessage` instead of relaunching.
- Usage limits hit all agents at once: if agents die on a rate limit, resume them (SendMessage "continue where you stopped") after the reset.

## 4. Phases

### Phase 0 — Intake and preflight (master)
Read `references/01-intake-and-setup.md`. Parse inputs, confirm MARKET and PRODUCTS_ROOT, run preflight (git state, Shopify CLI, Python+Pillow, Node, Edge/Chrome, Kie key + credit balance, Brandsearch MCP), create the PRODUCT_DIR tree, write BRIEF.md from `templates/BRIEF.md`.

### Phase 1 — Competitor capture (parallel, ~immediately)
Launch together:
- **Capture agent** — `scripts/capture_page.py` + `scripts/screenshot.py` → `02_competitor/page/` (product JSON, HTML, copy, colors, fonts, apps/bundle tiers, media URLs, screenshots) **and the competitor home page** → `02_competitor/home/` (HTML, copy, media URLs, full-page screenshots). Read `references/03-competitor-page-analysis.md` §capture and `references/11-home-page.md` §capture.
- **Media agent** — `scripts/fetch_media.py --from-capture` → `02_competitor/media/` (gallery images, **raw GIFs**, testimonial and section images) + WebP conversions. `references/06-page-images-and-gifs.md`.
- **Master** — Brandsearch pulls (both endpoints) into `05_ads/competitor/raw/`, then `scripts/rank_ads.py`. `references/07-ads-research-brandsearch.md`.
- **Policies** — `scripts/policies.py fetch` → `06_policies/source/` (all competitor policy pages). `references/12-policies.md`.

### Phase 2 — Branding → GATE (master)
Read `references/02-branding.md`. From capture data: competitor snapshot table, 7–10 brand names (top 3 starred, possessive test), palette 1:1 (exact hex + roles), product title 1:1. Save `01_branding/BRANDING.md` (template `templates/BRANDING.md`). **Stop and present** (in the same message, ask for our domain + support email if unknown — needed for the policies). On approval: record decisions in BRIEF, create the git branch `BRAND_SLUG` from clean `main` (01-intake §git).

### Phase 3 — Production (parallel streams after the gate)
| Stream | Who | Reference | Output |
|---|---|---|---|
| A1 Section spec + funnel psychology | conversion-architect agent | 03 | `02_competitor/page/SECTION_SPEC.md` |
| A2 Page copy | copywriter agent (after A1) | 03 §copy rules, 04 | copy deck (returned text → master saves) |
| A3 Build | master (or builder agent) | 04, tools-shopify-cli-and-git | theme settings, sections, blocks, template |
| A4 Home page | home-page agent (after A3's shared settings + reusable sections exist; can start with spec/copy right after the gate) | 11, 04 | `templates/index.json` + `<slug>-*` home sections, 1:1 with the competitor home |
| B Product images | image agent | 05, tools-kie | packshot first, then gallery remakes → `03_product-images/` |
| C Page images + GIFs | image agent | 06, tools-kie | testimonials/section remakes, WebP → `04_page-images/`, theme assets |
| D1 Ad analysis | 2 analyst agents (ranks 1–15, 16–30) | 07 | text → master compiles `05_ads/COMPETITOR_ADS.md` |
| D2a Ad variants | ad-creative agent (after D1) | 08 §1b | `05_ads/AD_VARIANTS.md` → **operator gate** |
| D2 Ad creatives | ad-creative agent or master (after approval + packshot) | 08, tools-kie | 25 ads → `05_ads/generated/` |
| E Ad copy | copy agent (after D1) | 09 | `05_ads/AD_COPY.md` (root of 05_ads, one copy set shared by image and video ads) |
| G Video ads (on request) | video agent (after the packshot + operator-confirmed candidates) | 14 | `05_ads/generated/videos/vNN-<slug>.mp4` + `vNN-work/` (clips sheet, draft, PLAN) |
| H Checkout header | master (small, after branding + C) | `scripts/checkout_header.py`, mockup `templates/checkout-header-mockup.png` | `07_checkout/<brand>-checkout-header.png` (+@2x): logo, "trusted by" gradient bar (brand colors) with 3 real-looking customer faces cropped from our page images, 3 trust points in the store language. Config `07_checkout/checkout_header.json`; strip metadata; operator uploads it in Settings > Checkout > Customize > Header |
| F Policies | master (small) | 12 | `policies.py transform` → `06_policies/<handle>.html` + REVIEW.md (1:1 text, brand/domain/email swapped, addresses/phones/registration numbers removed) |

Order inside the window: start A1, B (packshot first), C, D1 and A4's home spec at once; A2 when A1 lands; A3 when A2 lands (settings/header/footer can start immediately); A4 builds once A3's settings and reusable sections (testimonials, image-text, comparison, FAQ) exist, reusing them and the gallery images from B; D2 when D1 + packshot land; E when D1 lands.

### Phase 4 — QA loop
Read `references/10-qa-and-delivery.md`. Visual QA agent compares competitor screenshots vs local renders (`scripts/render_sections.js` + static buy-box mock) at desktop and mobile; master fixes; loop until no unintended discrepancies. Review every image/ad batch through `scripts/contact_sheet.py` before calling it done. `shopify theme check` must show no new offenses.

### Phase 5 — Delivery (master)
Commit on the brand branch, pull + merge-check, push to GitHub; push to the draft theme if STORE/THEME_ID are known (never publish). Push the policies with `policies.py push` (needs STORE + SHOPIFY_ADMIN_TOKEN; otherwise deliver the files and add the to-do). Write `DELIVERY.md` (template). Show the operator contact sheets (product images, ads) and a short summary: what was built (product page + home page), image placeholder map, operator to-dos (shipping rates for every market first: without them Shopify shows every product as sold out and add to cart fails; variants, uploads, gift/bundle app, reviews app, home product links), credits spent.

## 5. Dependency map

```
Phase 0 ─┬─ Capture agent ──┬──────────────► Branding ──► GATE ──┬─ A1 spec ─► A2 copy ─► A3 build ─┤
         │  (product + home)│                                     ├─ A4 home spec/copy ──► home build ─┤ (after A3 + B)
         ├─ Media agent ────┤ (gallery, GIFs)                     ├─ B packshot ─► gallery remakes ───┤
         └─ Brandsearch ────┴─ rank_ads ───────────────────────────┼─ C page images/GIF webp ─────────┤
                                                                   ├─ D1 analysts ─┬─ D2 25 ads ──────┤
                                                                   │   (+packshot)─┘                  │
                                                                   └─ E ad copy (after D1) ───────────┴─► QA ─► Delivery
```
Brandsearch pulls and capture don't need the brand, so they run before the gate; generation work needs the brand, so it waits.
Video ads (14) are a separate stream, only on request: Brandsearch video pull → `REMAKE_CANDIDATES.md` → **operator gate** → per-video remake (needs the packshot and AD_COPY offer; class (c) regenerations need a second operator OK) → independent check → finals.

## 6. Folders, scripts, templates

`PRODUCT_DIR` = `PRODUCTS_ROOT/BRAND` (before the brand exists use `PRODUCTS_ROOT/_<competitor-slug>` and rename after the gate):
```
BRIEF.md · DELIVERY.md
01_branding/BRANDING.md
02_competitor/page/   (p.json, p.html, capture.json/.md, copy.txt, screenshots, SECTION_SPEC.md)
02_competitor/home/   (home HTML, copy, media URLs, screenshots, HOME_SPEC.md)
02_competitor/media/  (RAW gallery images, RAW GIFs, testimonials, section images, home images)
03_product-images/    (packshot, remakes, superseded/ subfolders)
04_page-images/       (testimonial/section remakes, GIF→WebP)
05_ads/competitor/    (raw/ dumps, ranked NN_<id>.<ext>, ranking.json)
05_ads/generated/     (ad-NN-<slug>.png)
05_ads/COMPETITOR_ADS.md · 05_ads/AD_COPY.md
05_ads/REMAKE_CANDIDATES.md · 05_ads/remake-candidates/ (source videos)
05_ads/generated/videos/  (ONLY final vNN-<slug>.mp4 at the root; vNN-work/ = vNN-clips.jpg, vNN-draft.mp4, vNN-PLAN.md; all other work files in scratch/ and deleted when final)
06_policies/          (source/ raw competitor policies, <handle>.html ours, REVIEW.md)
```
Theme repo: only theme files, on branch `BRAND_SLUG`, files prefixed with the brand slug.

Scripts (`scripts/`, run Python with `-I`; all have `--help`):
- `capture_page.py URL --out DIR [--html-file saved.html]` — product JSON, HTML, copy (+word count), colors/CSS vars, fonts, apps (Kaching tiers, reviews apps…), Shopify sections in order, media URLs (gallery, GIFs, videos, testimonials). Prices come from the product JSON (screenshots show the visitor's local currency).
- `screenshot.py TARGET --out DIR [--name comp]` — Edge/Chrome via DevTools: full-page desktop (`desk.png` + chunks) and true 390px mobile emulation (`mob.png` + sheets), works on shops that block iframes; `--engine cli` fallback.
- `fetch_media.py --out DIR --from-capture capture.json --kinds images,gifs,videos [--by-kind] [--webp-dir DIR]` — raw byte-identical downloads (manifest, skips existing) + animated GIF→WebP (q62).
- `contact_sheet.py IMAGES|GLOBS|DIRS --out sheet.jpg [--cols 5 --cell 300]` — labelled review grids (splits into sheet_1, sheet_2…).
- `rank_ads.py --dumps FILES --out DIR --keyword K [--top 30] [--sheet] [--extra-image ID=PATH]` — merge Brandsearch dumps, download, hash/near-dup merge, rank by impressions rank (`--sort rank` default; `spend`/`reach` EU only; `days`), captions summary, sheets. Run it in the same session as the pull (media URLs expire).
- `policies.py fetch|transform|push` — clone competitor policies 1:1 (identity swapped, private info removed, leftovers check) and publish them via Admin GraphQL `shopPolicyUpdate`.
- `kie_jobs.py jobs.json OUT_DIR` / `kie_jobs.py --credits` — batch Kie GPT Image 2.5 jobs (uploads local refs, polls, downloads). Needs `KIE_API_KEY`.
- `render_sections.js --theme DIR --template templates/product.json --sections ALL --out page.html [--shot] [--buybox --product p.json --prefix <slug>]` — local Liquid render of custom sections (and a mocked buy box) with the theme's real palette; needs liquidjs (`npm i liquidjs@10` in a scratch dir, pass `--modules` or NODE_PATH).
- Video remakes (14): `video_clips.py SRC --out DIR [--classes "1-20=b,21=c"]` (scene detection, keyframes, labelled clip sheet, weak-cut list) · `video_transcribe.py SRC --out words.json --lang xx [--against ref.json]` (faster-whisper word timestamps, sync check) · `video_vo.py separate|skeleton|clone|delete-voice|audition|build|mix` (demucs stems, 3 mandatory remake lines, ElevenLabs clone, beat-aligned VO ≤1.08x, splice or ducked mix at −14 LUFS) · `video_captions.py ass|burn` (styled .ass from word timings, cover old overlays, burn in) · `video_finalize.py render|frames|clean` (insert regenerated clips, strip metadata, 0.5 s frame strip, folder clean-up).
Network note: if Python reports "certificate has expired", the scripts fall back to `certifi`/`curl`; pages behind bot protection need `--html-file` with a browser-saved copy.

Templates (`templates/`): BRIEF.md, BRANDING.md, SECTION_SPEC.md, COMPETITOR_ADS.md, AD_COPY.md, DELIVERY.md.

## 7. Credits and costs
Check Kie balance (`GET https://api.kie.ai/api/v1/chat/credit`) before Phase 3. GPT Image 2.5: 1K = 6, 2K = 10, 4K = 16 credits; 4:5 only at 1K. Typical run ≈ 260 credits (packshot 10, ~5 gallery 50, 3 testimonials 30, top-5 ads 50, 20 ads 120) + fixes. If short, tell the operator before generating and prioritise: packshot → gallery → top-5 ads → remaining ads → page images. Brandsearch: list/query calls are cheap; `download_ad` 1 credit each (use only for creatives without a URL); `analyze_ad` 14–19 AI credits (not needed). Report spend in the delivery. Video remakes: (c) clip = 76 Kie credits (start frame 6 + wan i2v 720p 5 s 70); voice = ElevenLabs Starter quota (40k characters/month), see 14 §12.

## 8. Reporting to the operator
- Short progress lines at milestones; never narrate internal deliberation.
- Show images, don't describe them: contact sheets for gallery remakes, top-10 competitor ads, generated ads.
- Gate message (branding) = tables + picks, nothing else.
- Delivery = what was built, where files are, what the operator must do, credits spent. No claim caveats (rule 1).

## 9. Partial runs and resuming
The operator often asks for one step ("just the ads", "remake their images", "branding only"). Enter at the matching phase: create/reuse PRODUCT_DIR and BRIEF.md, run only the needed preflight checks, and pull inputs you lack (e.g. ads need the packshot → generate it first). If BRIEF.md already exists, read it and continue from its decisions instead of redoing earlier phases.
