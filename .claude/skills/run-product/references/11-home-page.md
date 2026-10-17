# Stream A4 — Home page (index) 1:1 from the competitor

Goal: the store's home page mirrors the competitor's home page (Mode A by default) with our brand, copy and images, so traffic that lands on `/` sees the same proven funnel as on the product page. Most product-test stores are one-product stores: the home page is a second sales page that routes to the product.

## Contents
1. Inputs and timing
2. Capture the competitor home
3. HOME SPEC
4. Map components to the theme (native vs custom)
5. Copy
6. Images
7. Build `templates/index.json`
8. QA
9. Pitfalls
10. Done when
11. Worked example and learnings (Noxis ← plaims.com)

---

## 1. Inputs and timing
- `COMPETITOR_HOME`: the root of the competitor's domain (e.g. `https://plaims.com/`) unless the operator names another page. If several competitors were sent, use the home of the competitor whose product page you cloned, unless told otherwise.
- Needs: BRIEF decisions (brand, palette, title, offer), theme settings already set by A3 (palette, fonts, header/announcement/footer), reusable `<slug>-*` sections from A3 (testimonials, image-with-text, comparison, FAQ, media/vars snippets), gallery images from stream B.
- Timing: capture in Phase 1 (with the product page); spec + copy right after the gate; build once A3's settings and reusable sections exist.

## 2. Capture the competitor home
**Do:**
1. `python -I scripts/capture_page.py "<COMPETITOR_HOME>" --out "<PRODUCT_DIR>/02_competitor/home"` — on a non-product URL the product-JSON step is skipped; you still get HTML, copy, colors, fonts, media URLs, headings.
2. `python -I scripts/screenshot.py "<COMPETITOR_HOME>" --out "<PRODUCT_DIR>/02_competitor/home" --name home` — desktop full page (mobile iframe often blocked by X-Frame-Options).
3. Add the home's media to the media download (`fetch_media.py --from-capture <home capture.json>` into `02_competitor/media/home/`) — GIFs raw, as always.
4. Read the screenshot chunks top to bottom.
**Why:** the home often reuses the product page's blocks (reviews, comparison, FAQ) but in a different order with a hero and a product grid/featured product on top; you need the exact order and proportions to clone it faithfully.

## 3. HOME SPEC
Write `02_competitor/home/HOME_SPEC.md` in the same per-section format as SECTION_SPEC (03): LAYOUT / COMPONENTS / TYPOGRAPHY / VISUAL DETAILS / IMAGE POSITIONS / CONVERSION ROLE / MOBILE, then a short COPY INVENTORY and IMAGE MAP. Announcement bar, header and footer are global — only verify they match (already configured in A3).

Typical one-product home (check against the real page, don't assume): hero (headline + subhead + CTA + product visual or lifestyle), trust strip / marquee, featured product (buy box or product card), benefits/how-it-works, testimonials, comparison table, image-with-text story blocks, FAQ, guarantee, final CTA.

## 4. Map components to the theme
For each HOME SPEC section decide **native vs custom**:
- **Reuse your own `<slug>-*` sections first** (built for the product page; same look, already QA'd): testimonials, image-with-text (supports theme-file assets such as GIF→WebP), comparison, FAQ, guarantee.
- **Native theme sections** when they match closely: Horizon `hero`, `featured-product` / `product-information`-style product block, `product-list` / collection grid, marquee/announcements, `rich-text`, `media-with-content`. Read their schema to set every setting from the spec.
- **New `<slug>-*` sections** only for components neither covers (e.g. a stats band, a press-logo strip, a step diagram). Same conventions as 04: scoped CSS per file, schema settings + presets, labeled placeholders at the competitor's ratios.
Extending a reusable section for the home: only add optional settings with defaults that keep the product page unchanged.

## 5. Copy
Same rules as the product page: original wording paraphrasing the competitor's key lines, same persuasion job per section, claims at the SAME strength, simple direct-response language, our brand instead of theirs, market language and currency. Keep the home consistent with the product page copy (same offer, guarantee, numbers).

## 6. Images
- Prefer what already exists: gallery remakes (stream B), page images and GIF WebPs (stream C), the packshot.
- Copy theme-ready versions into `assets/<slug>-home-*.jpg` (~1200 px, JPG q82 progressive).
- Generate with Kie only for an essential visual with no equivalent (hero lifestyle, banner): attach the packshot, no logo/text on the frame, 2K; keep it to a few images and report credits.
- Product images inside product cards/featured product come from the Shopify product — leave the product setting for the operator if the store/product doesn't exist yet (previews show a placeholder) and list it in the delivery to-dos.

## 7. Build `templates/index.json`
- Generate it with a Python builder like the product template (04): keep the JSON header comment, deep-copy proven section configs where useful, wrap rich text in `<p>`/`<ul>`/`<h*>`, consistent section keys (`<slug>_hero`, `<slug>_reviews` …), `order` = HOME SPEC order.
- Links/CTAs point to the product: product picker setting where the section supports it, otherwise `/products/<handle>` from BRIEF (if the handle isn't known yet, use `routes.all_products_collection_url` or leave the link setting empty and add a to-do).
- If the live home receives ad traffic, build `index.<slug>-v2.json` instead and swap on approval (rule 9).

## 8. QA
Same loop as 10: render custom sections with `scripts/render_sections.js --template templates/index.json`, screenshot, compare side by side with the competitor home; read native sections' settings against the spec; `shopify theme check` without new offenses; index.json parses.

## 9. Pitfalls
- Don't break the product page when extending shared sections (new settings must be optional with defaults).
- Competitor home pages often include app widgets (reviews carousels, Instagram feeds, countdowns): rebuild natively only what the spec needs; list app blocks as operator to-dos.
- Product grids need real products/collections — they render empty until the operator creates the product; say so.
- Keep the hero image light (WebP/JPG, sized); it's the LCP element.

## 10. Done when
Every HOME SPEC section exists in order with our copy and images (or labeled placeholders), links route to the product, theme check is clean, and the side-by-side comparison shows no unintended structural differences.

## 11. Worked example and learnings (Noxis ← plaims.com)
**What the competitor home actually was:** an empty Dawn slideshow (renders nothing) + one Dawn "Featured product" section (1:1 rounded image ~55% left; right column ~400px: tiny uppercase vendor caption, big Poppins title, full-width amber pill Add to cart adding the first variant, "View full details →"). No price, no rating, no other copy. Built as: Horizon `featured-product-information` + a tiny `blocks/noxis-view-details.liquid`. 0 Kie credits.

Learnings to apply on every home clone:
1. **List sections from the HTML first:** `grep -o 'id="shopify-section-template--[^"]*"'` gives the real section order; one-product competitor homes are often tiny. Don't clone empty sections (an empty slideshow renders nothing).
2. **Screenshot height:** on Dawn sites a 12000px-tall headless window produces a huge blank body (body stretches to the window). Scan for the last non-white row, then re-shoot at ~1440×1000 desktop and ~500×1800 mobile.
3. **Dawn "Featured product" → Horizon `featured-product-information`** (not `featured-product`, which is a full-bleed editorial card). Title = text block with `{{ closest.product.title }}`; vendor caption = small text block.
4. **Match Dawn's minimal buy box** by hiding Horizon static blocks with `"disabled": true` (quantity, accelerated-checkout inside buy-buttons) — passes theme check. `limit_details_width` ≈ Dawn's ~400px info column.
5. **Unknown product handle:** leave the section's product setting out of the JSON (an empty string is pointless); custom links fall back `closest.product.url` → `routes.all_products_collection_url`; add "select the product in the home section" to delivery to-dos.
6. **Small Dawn pieces Horizon lacks** (e.g. "View full details →") are cheapest as a tiny `blocks/<slug>-*.liquid` placed in `_product-details`.
7. **QA of native sections:** `render_sections.js --buybox` mocks them only when the section key is `main` (or the type is in its list) — copy the template to scratch, rename the key, pass `--prefix <slug>` (else custom blocks show as stand-ins) and `--product` with a local image. The mock ignores text-block `custom` preset sizes; patch mock CSS or read the theme's typography snippet before judging type size.
8. **Build with a script** that copies native block settings from a known-good template (full key sets stay valid) and keeps the JSON header comment.
9. **Check global header/footer against the competitor home too.** Noxis had Horizon's default footer (email signup + menus) while Plaims had only country selector + payment icons + copyright/policies → footer reduced to `payment-icons` (right-aligned) + utilities. Horizon's footer has no country-selector block (the header shows it) — note it if the competitor has one in the footer.
