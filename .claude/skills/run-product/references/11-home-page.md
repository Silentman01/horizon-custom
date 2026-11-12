# Stream A4 — Home page (index) adapted from the competitor

Goal: the store's home page uses the competitor's proven conversion flow as a starting point, then adapts it into our own distinct version. The home should feel like a completely different brand while serving the same funnel purpose. Most product-test stores are one-product stores: the home page is a second sales page that routes to the product.

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
- Timing: capture in Phase 1 (with the product page); spec + copy right after the Step Alpha gate and the branding gate; build once A3's settings and reusable sections exist.
- **Inputs from Step Alpha** (`00_alpha/ALPHA_DOSSIER.md`): 3.2 Avatar Cards and 3.1 Angle Cards, plus the product page's ANGLE ARCHITECTURE (SECTION_SPEC). The home hero validates the highest-confidence angle(s), like the product page's fold; each home section gets an ANGLE ROLE (angle card IDs, avatar, objection, congruence role); people shown and testimonial personas are the avatars of their section's angle; copy uses the Customer Language Bank (3.5).

## 2. Capture the competitor home
**Do:**
1. `python -I scripts/capture_page.py "<COMPETITOR_HOME>" --out "<PRODUCT_DIR>/02_competitor/home"` — on a non-product URL the product-JSON step is skipped; you still get HTML, copy, colors, fonts, media URLs, headings.
2. `python -I scripts/screenshot.py "<COMPETITOR_HOME>" --out "<PRODUCT_DIR>/02_competitor/home" --name home` — desktop full page (mobile iframe often blocked by X-Frame-Options).
3. Add the home's media to the media download (`fetch_media.py --from-capture <home capture.json>` into `02_competitor/media/home/`) — GIFs raw, as always.
4. Read the screenshot chunks top to bottom.
**Why:** the home often reuses the product page's blocks (reviews, comparison, FAQ) but in a different order with a hero and a product grid/featured product on top; you need the exact structure and conversion flow to understand what works before adapting it.

## 3. HOME SPEC
Write `02_competitor/home/HOME_SPEC.md` in two parts:

**Part A — Competitor framework analysis.** Map the competitor's home in the same per-section format as SECTION_SPEC (03): LAYOUT / COMPONENTS / TYPOGRAPHY / VISUAL DETAILS / IMAGE POSITIONS / CONVERSION ROLE / MOBILE / ANGLE ROLE, then a short COPY INVENTORY and IMAGE MAP (with the Angle / avatar column). This documents what they do and why it converts.

**Part B — HOME ADAPTATION BLUEPRINT.** For each competitor section, decide how our version differs:
| Competitor section | Keep / Merge / Skip / Add | OUR VERSION (layout, components, visual direction) | CONVERSION ROLE (same as competitor's) |
The adaptation rules:
- **Conversion roles stay.** If their hero validates the top angle, ours does too — but with a different layout, different imagery style, different headline structure.
- **Visual execution changes.** Different grid layouts, different image positions (left↔right, full-bleed↔contained, card grid↔stack), different component choices (accordion↔tabs, cards↔inline list, carousel↔grid), different spacing rhythm.
- **Section order may change** when a different flow serves the funnel better (e.g. moving social proof higher if the dossier shows the avatar needs early trust).
- **Sections may merge or split.** Two thin competitor sections that serve one conversion role can become one richer section; a heavy section can split if it serves two distinct roles.
- **New sections may be added** when the dossier reveals a gap the competitor's home doesn't serve (an underserved avatar, an unanswered objection, a missing mechanism explanation).
- The goal: an AI comparing both home pages sees two completely different shops, yet every conversion role the competitor's home serves is served on ours.

Reused product-page sections keep their angle roles; the hero carries the product page's above-the-fold angle; an angle with no home on the product page may get one here. Announcement bar, header and footer are global — only verify they match (already configured in A3).

Typical one-product home (check against the real page, don't assume): hero (headline + subhead + CTA + product visual or lifestyle), trust strip / marquee, featured product (buy box or product card), benefits/how-it-works, testimonials, comparison table, image-with-text story blocks, FAQ, guarantee, final CTA.

## 4. Map components to the theme
**Rule (operator, 2026-10-31): the home page must render COMPLETE on the store with zero admin setup** — no image to upload, no collection to create, no product to pick. The Mojo home shipped with a native `hero` (empty until an image is uploaded) and two native `product-list` sections on the empty "all" collection, so the live home looked unfinished. Therefore:
- Every image slot = `image_picker` + theme-asset fallback (`<slug>-media` snippet) with the asset filled in index.json.
- **Never** a native section that needs uploads or store data to show something (hero without image, product-list / collection grid, featured-collection). Use `<slug>-home-hero` and `<slug>-home-products` (cards as blocks: product picker + fallback handle + static image/title/price/compare-at/badge/link; live product data when the product exists, the static settings otherwise).
- Bestseller cards = the product's colourways; bundle cards = the BRIEF tiers (badges, prices). CTAs → `/products/<handle>` from BRIEF.
For each section in the HOME ADAPTATION BLUEPRINT decide **native vs custom**:
- **Reuse your own `<slug>-*` sections first** (built for the product page; already QA'd) and configure them for the adapted layout: testimonials, image-with-text (supports theme-file assets such as GIF→WebP), comparison, FAQ, guarantee. The same section type can look very different with different settings (columns, image side, spacing, colors).
- **Native theme sections** when they fit the adapted blueprint: Horizon `hero`, `featured-product` / `product-information`-style product block, marquee/announcements, `rich-text`, `media-with-content`. Read their schema to set every setting from the blueprint.
- **New `<slug>-*` sections** for adapted components that neither covers (e.g. a stats band, a press-logo strip, a step diagram, or a layout the competitor doesn't use but the blueprint calls for). Same conventions as 04: scoped CSS per file, schema settings + presets, labeled placeholders at the blueprint's ratios.
Extending a reusable section for the home: only add optional settings with defaults that keep the product page unchanged.

## 5. Copy
Fully original copy, same rules as the product page (03 §14): every string written from the Step Alpha data (dossier 3.5 Customer Language Bank is the primary source, plus 3.1 angle cards, 1.1 avatars, 1.4 objections, 1.5 emotional landscape) and the copy playbooks (13). No word-for-word matches with the competitor — not a single title, headline or body line duplicated. Claims at the SAME strength. Simple direct-response language, our brand, market language and currency, each string written for its section's angle card and tagged with its ID. The home copy is consistent with the product page copy (same offer, guarantee, numbers) but adapted to the home's different section structure from the blueprint.

## 6. Images
- Prefer what already exists: the own gallery (stream B), page images and GIF WebPs (stream C), the packshot. Pick the one whose angle / avatar matches the home section's ANGLE ROLE.
- People in any new image are the avatar of the section's angle (3.2).
- Copy theme-ready versions into `assets/<slug>-home-*.jpg` (~1200 px, JPG q82 progressive).
- Generate with Kie only for an essential visual with no equivalent (hero lifestyle, banner): attach the packshot, no logo/text on the frame, 2K; keep it to a few images and report credits.
- Product cards show theme-asset images (`assets/<slug>-home-card-*.jpg`, colourway/gallery images) so they render before the product exists; once the product is imported they can switch to live product images via the product picker.

## 7. Build `templates/index.json`
- Generate it with a Python builder like the product template (04): keep the JSON header comment, deep-copy proven section configs where useful, wrap rich text in `<p>`/`<ul>`/`<h*>`, consistent section keys (`<slug>_hero`, `<slug>_reviews` …), `order` = HOME ADAPTATION BLUEPRINT order (which may differ from the competitor's section order).
- The template implements the adapted blueprint, not a mirror of the competitor's home. Different sections, different order, different settings — the conversion flow is preserved but the execution is ours.
- Links/CTAs point to the product: product picker setting where the section supports it, otherwise `/products/<handle>` from BRIEF (if the handle isn't known yet, use `routes.all_products_collection_url` or leave the link setting empty and add a to-do).
- If the live home receives ad traffic, build `index.<slug>-v2.json` instead and swap on approval (rule 9).

## 8. QA
Same loop as 10: render custom sections with `scripts/render_sections.js --template templates/index.json`, screenshot; `shopify theme check` without new offenses; index.json parses. Check against the HOME ADAPTATION BLUEPRINT:
1. **Every conversion role is served** — each role from the blueprint has a section that fulfils it.
2. **The page looks distinctly different from the competitor's home** — compare side by side: different layout, different visual rhythm, different section structure. An AI comparing both should see two completely different shops.
3. **No admin setup needed** — every image, link, and product card renders without uploads or store data (§4 rule).

## 9. Pitfalls
- Don't break the product page when extending shared sections (new settings must be optional with defaults).
- Competitor home pages often include app widgets (reviews carousels, Instagram feeds, countdowns): rebuild natively only what the spec needs; list app blocks as operator to-dos.
- Native product grids / collections render EMPTY until the operator creates products: don't use them on the home (rule in §4). The Mojo home shipped half-empty because of this.
- Keep the hero image light (WebP/JPG, sized); it's the LCP element.

## 10. Done when
Every section from the HOME ADAPTATION BLUEPRINT exists with our original copy and real images (no placeholders, nothing to upload), product cards show prices/images without any store data, links route to the product, `validate_schemas.py` = 0 errors, theme check is clean, the home is pushed with the theme, the conversion flow is complete, and the page looks distinctly our own — not a copy of the competitor's home.

## 11. Worked example and learnings (Noxis ← plaims.com)
**What the competitor home actually was:** an empty Dawn slideshow (renders nothing) + one Dawn "Featured product" section (1:1 rounded image ~55% left; right column ~400px: tiny uppercase vendor caption, big Poppins title, full-width amber pill Add to cart adding the first variant, "View full details →"). No price, no rating, no other copy. Built as: Horizon `featured-product-information` + a tiny `blocks/noxis-view-details.liquid`. 0 Kie credits.

**Note on the adaptation approach:** this example shows a simple home (Dawn slideshow + featured product). With the adaptation approach, even a simple home gets its own layout and visual treatment rather than copying the competitor's exact pattern — e.g. a split hero instead of a slideshow, a card grid instead of a single featured product, or a full-width lifestyle banner that the competitor didn't use.

Learnings to apply on every home build:
1. **List sections from the HTML first:** `grep -o 'id="shopify-section-template--[^"]*"'` gives the real section order; one-product competitor homes are often tiny. Don't clone empty sections (an empty slideshow renders nothing).
2. **Screenshot height:** on Dawn sites a 12000px-tall headless window produces a huge blank body (body stretches to the window). Scan for the last non-white row, then re-shoot at ~1440×1000 desktop and ~500×1800 mobile.
3. **Dawn "Featured product" → Horizon `featured-product-information`** (not `featured-product`, which is a full-bleed editorial card). Title = text block with `{{ closest.product.title }}`; vendor caption = small text block.
4. **Match Dawn's minimal buy box** by hiding Horizon static blocks with `"disabled": true` (quantity, accelerated-checkout inside buy-buttons) — passes theme check. `limit_details_width` ≈ Dawn's ~400px info column.
5. **Unknown product handle:** leave the section's product setting out of the JSON (an empty string is pointless); custom links fall back `closest.product.url` → `routes.all_products_collection_url`; add "select the product in the home section" to delivery to-dos.
6. **Small Dawn pieces Horizon lacks** (e.g. "View full details →") are cheapest as a tiny `blocks/<slug>-*.liquid` placed in `_product-details`.
7. **QA of native sections:** `render_sections.js --buybox` mocks them only when the section key is `main` (or the type is in its list) — copy the template to scratch, rename the key, pass `--prefix <slug>` (else custom blocks show as stand-ins) and `--product` with a local image. The mock ignores text-block `custom` preset sizes; patch mock CSS or read the theme's typography snippet before judging type size.
8. **Build with a script** that copies native block settings from a known-good template (full key sets stay valid) and keeps the JSON header comment.
9. **Check global header/footer against the competitor home too.** Noxis had Horizon's default footer (email signup + menus) while Plaims had only country selector + payment icons + copyright/policies → footer reduced to `payment-icons` (right-aligned) + utilities. Horizon's footer has no country-selector block (the header shows it) — note it if the competitor has one in the footer.
