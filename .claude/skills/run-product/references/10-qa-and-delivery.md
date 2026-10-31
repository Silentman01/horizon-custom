# Phase 4–5 — QA loop and delivery

Goal: prove the page, images and ads are right before the operator sees them, then hand over everything in one clear report.

## Contents
1. What "done" means
2. Page QA (structure, visuals, behaviour)
3. Image and ad QA
4. Discrepancy log and loop
5. Push and merge safety
6. Delivery report
7. Final message to the operator

---

## 1. What "done" means
- **Mode A:** zero visible structural discrepancies vs the competitor at desktop and mobile (brand identity, copy and images differ by design).
- **Mode B:** zero *unintended* discrepancies; every intentional improvement is logged with a reason.
- Every image/ad batch reviewed on a contact sheet; no misspellings, no competitor brand names, no logo on product images, claims at full strength.
- `shopify theme check` shows no new offenses compared with the baseline on `main`.
- **Every Phase 3 stream has its output on disk** before delivery: check the SKILL.md stream table row by row (spec, copy deck, theme, home, product images, page images, `05_ads/COMPETITOR_ADS.md`, `05_ads/AD_COPY.md`, ads, policies, checkout header, logo set, `08_shopify/<slug>-products.csv` product import file). A stop instruction like "stop at remaking ads" skips only that stream; the others still run. A missing file = not done (Krino shipped without AD_COPY.md, 2026-10-25).

## 2. Page QA
**Inputs:** competitor screenshots (`02_competitor/page/desk*.png`, mobile sheets if available), SECTION_SPEC.md, the built theme files.

**Step 2.1 — Render what can be rendered locally.**
- Custom sections: `node scripts/render_sections.js --theme <THEME_DIR> --template templates/product.json --sections ALL --out <scratch>/qa/page.html --shot` — renders every custom section with the theme's real palette/fonts and takes desktop + 390px mobile screenshots (headless Edge, own profile). Run `--help` for `--images`, `--css`, `--product`.
- Buy box: the main section depends on Shopify product objects, so render it with `--buybox` (optionally `--product <02_competitor/page/p.json or a mock>`): your custom buy-box blocks render for real against a mock product (default Buy 1/2/3 variants), native theme blocks get simple stand-ins. Compare it with the competitor's buy-box column cropped from the desktop screenshot. This caught real issues in the Noxis run (divider color, card radius 12→18px, list letter-spacing). Also test the bundle cards' selection logic in the rendered page (selected state moves, hidden variant picker follows).
- Rails: drag every horizontal rail with the mouse in the mobile render (mobile-first rule) — screenshots alone don't prove it scrolls.
- If a store/draft theme is available, also screenshot the real preview URL (`https://<store>/products/<handle>?view=<template-suffix>&preview_theme_id=<id>`).

**Step 2.2 — Compare section by section** (visual QA agent, brief in subagent-briefs.md): layout and alignment, spacing, typography (family/size/weight/color), colors (hex), component behaviour (selected states, accordions, carousels, sticky elements), image positions and ratios, mobile stacking (horizontal scroll rails, table compaction).

**Step 2.3 — Behaviour checks** (read the code if you can't click): bundle cards select the right variant and update price/form; preselected tier on load; `?variant=` respected; ATC adds the selected variant; accordions exclusive; nothing depends on `window.scrollTo` if the theme scrolls a wrapper (`scrollIntoView` instead).

**Step 2.4 — Static checks:** `shopify theme check` (only baseline offenses allowed); JSON templates valid; rich text settings wrapped in `<p>`; no hard-coded competitor names, prices in the wrong currency, or leftover placeholder copy.

**Known harness artefacts (don't "fix" the theme for these):** fonts fall back to serif when offline; lazy images blank inside headless iframes; colors empty if snippet globals aren't passed; text-glyph icons rendering in colour on some systems (use SVG icons in the theme anyway).

## 3. Image and ad QA
For every batch (gallery remakes, page images, top-5 ads, 20 ads):
1. `python -I scripts/contact_sheet.py "<dir>/*.png" --out <dir>/_sheet.jpg` and Read it.
2. Checklist per image: product matches the packshot (frame shape, amber lenses, side shields); text spelled correctly and identical to the spec; claims exactly as specified; no competitor brand; no logo/wordmark on product images; no text on the product frame; people look natural; layout matches the reference (top-5: side-by-side with the original).
3. Fix by editing (keep-everything prompt) when only text/small elements are wrong; regenerate only when composition is wrong. Keep superseded files in a subfolder.
4. Note leftover minor flaws honestly in the delivery (e.g. "ad-25 body text is decorative filler").

## 4. Discrepancy log and loop
Keep a table in `scratch/QA_LOG.md` (master writes):
```
SECTION        │ ISSUE                        │ FIX                         │ STATUS
───────────────┼──────────────────────────────┼─────────────────────────────┼────────
Bundle         │ divider lines black vs amber │ rgb(from amber / .45)       │ fixed
Comparison     │ ✕ not centered in "Others"   │ svg display:block; margin auto │ fixed
```
Apply fixes → re-render → re-compare → repeat until the table has only `fixed`/`intentional` rows.

## 5. Push and merge safety
1. Commit your work on the brand branch (specific files, attribution line).
2. Pull before pushing: `git pull --no-rebase origin <branch>` (if the remote branch exists) and, if a store is connected, `shopify theme pull --store <store> --theme <id> --only <files you'll push>`; inspect `git diff` — commit or merge live edits, never blindly overwrite them.
3. After merging Shopify bot commits: `git diff <your-last-commit> HEAD -- <your files>` must be empty (the merge didn't revert you).
4. Push: `git push -u origin <branch>`; theme: `shopify theme push --store <store> --theme <draft id> --nodelete --only <files>` (`--allow-live` only if the operator explicitly wants the live theme; never publish).
5. If a push reports errors (e.g. invalid rich text), read the full message, fix, re-push, then re-pull to confirm the remote matches.

## 6. Delivery report
Write `PRODUCT_DIR/DELIVERY.md` from `templates/DELIVERY.md`: links/paths, sections built, image placeholder map (position → file or still needed), product media list (gallery order), ads list, ad copy pointer, operator to-dos, credits spent, known minor flaws, QA log summary.

## 7. Final message to the operator
Short. Lead with the result and the preview link (or "pushed to GitHub branch X; send me the store to create the draft theme"). Then: contact sheet paths, the to-do list (variants, uploads, gift/bundle app, reviews app, store connection), credits spent. No claim caveats.

## Schema checks theme check misses (Aurea push, 2026-10-17)
Shopify rejects these on `shopify theme push` even when `shopify theme check` is clean. Scan every new section/block schema before delivery:
- no `"default": ""` on any setting (omit the key instead);
- no duplicate setting ids within a section or a block;
- range defaults and template values inside min/max (e.g. `border_radius` max 50);
- font handles in `config/settings_data.json` must exist in the Shopify font library (e.g. `cormorant_garamond_n6` is invalid).
- Run `python -I <SKILL>/scripts/validate_schemas.py <theme_root>` before every push; it must report 0 errors.
