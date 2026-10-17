# Stream A3 — Build the product page in the theme

Goal: turn `SECTION_SPEC.md` + the copy deck into theme files (settings, custom sections/blocks, a product template) in **any** OS 2.0 theme, so the merchant can edit everything in the theme editor, the bundle cards drive the real variants, and the page matches the competitor at 390 px and desktop.

Distilled from the Noxis build (Horizon 4.2, branch `noxis`) and the Ceriva build (branch `ceriva`). Git/CLI commands are in `tools-shopify-cli-and-git.md`; QA loop in `10-qa-and-delivery.md`.

## Contents
0. Principles (mobile first, editability, native first, 1:1)
1. Preflight: detect the theme
2. Global settings: palette, fonts, buttons
3. Header, announcement bar, footer
4. Component inventory: native vs custom
5. Build the custom blocks and sections (patterns)
   5.1 Naming and file layout · 5.2 Vars snippet · 5.3 Media snippet · 5.4 Bundle picker (parent + tier + JS driver) · 5.5 Small buy-box blocks · 5.6 Testimonials rail · 5.7 Image with text · 5.8 Comparison table · 5.9 FAQ · 5.10 Scroll-to-offer CTA · 5.11 Wiring to Dawn
6. Generate the template JSON with a Python builder
7. Theme check
8. Local QA render + buy-box mock
9. Commit → pull/merge → push draft
10. Delivery notes for the operator
11. Pitfalls index

---

## 0. Principles

1. **MOBILE FIRST.** Most ad traffic is on phones. Design and test every section at **390 px first**, then desktop.
   - Horizontal rails/carousels (testimonials, UGC, logos) must scroll **by touch AND by mouse drag**. The Shopify editor's mobile preview on a PC has no touch: an `overflow-x` rail without a pointer-drag handler cannot be scrolled there. The operator reported "what our drivers say cannot scroll on mobile" on the Noxis testimonials, because the rail only had native overflow scrolling.
   - Use `scroll-snap` together with a drag handler that turns snap off while dragging and snaps to the nearest card on release (§5.6). Show an affordance: let the next card **peek** (card width ≈ 76–85 vw), and add dots or arrows if the competitor has them.
   - Tables shrink instead of scrolling (smaller fonts and padding at ≤749 px). Tap targets are ≥ 44 px. Media keep the competitor's ratio. Nothing overflows the viewport horizontally.
   - QA (§8) includes a real **pointer drag** on every rail at 390 px.
2. **The merchant edits everything.** Every text, image, color choice, toggle and repeatable item is a schema setting or block, with presets. Never hard-code copy in Liquid. Labeled placeholders show where each image goes.
3. **Native first.** If a theme block or section already matches the competitor component (title, price, variant picker, buy buttons, accordion, rich text), configure it. Build `<slug>-*` custom files only for components the theme lacks (bundle cards, comparison table, rating line, testimonial cards, …).
4. **1:1 in Mode A.** Same sections, order, proportions, colors and claims as the competitor (00-operator-rules §1–2). No "improvements". List ideas in one line at delivery.
5. **Variants are the source of truth.** Bundle cards read price and compare-at from the product variants (Buy 1 / Buy 2 / Buy 3). The cards never compute prices the checkout doesn't know about.
6. **Performance and accessibility by default.** Use WebP for GIFs, lazy images below the fold, explicit width/height, no third-party fonts or scripts, real radio inputs, visible `:focus-visible`, and aria labels on icon-only content.

---

## 1. Preflight: detect the theme
**Purpose:** your choices (where the palette lives, how blocks nest, how to drive variants) depend on the theme and its version.
**Do:**
1. `config/settings_schema.json` → the `theme_info` object gives `theme_name` and `theme_version` (Noxis: Horizon 4.2.0).
2. Classify:
   | Family | Signs | Palette | Product template main section | Blocks |
   |---|---|---|---|---|
   | Horizon ≥ 4 (Shopify 2025+ themes: Horizon, Tinker, Pitch, …) | `blocks/` folder, `color_palette` setting | `current.color_palette` {background, foreground, color1–3} + `palette_*` roles | `product-information` with static `_product-media-gallery` + `_product-details` | **theme blocks** (`blocks/*.liquid`, nested, `{% content_for 'blocks' %}`) |
   | Horizon 1–3 | `blocks/`, `color_schemes` | `color_schemes` | same | theme blocks |
   | Dawn and Dawn-likes (Sense, Craft, Refresh, most paid OS 2.0) | no `blocks/`, `sections/main-product.liquid` | `current.color_schemes["scheme-1"].settings` {background, text, button, button_label, …} | `main-product` with section blocks | section blocks only (+ `@app`) |
   | Other | read `templates/product.json` and the main section schema | find the color settings | — | — |
3. Read `templates/product.json` (main section, its block tree, the order of sections) and the main section's schema (`"blocks"` it accepts, e.g. `@theme`, `@app`).
4. Run the theme-check baseline on `main` (tools §7). Note the theme's breakpoint (Horizon/Dawn: 750 px, so mobile = `max-width: 749px`).
**Output:** in BRIEF: theme family + version, palette location, main section type, breakpoint, baseline offenses.
**Done when:** you know where settings go and how a custom block plugs into the buy box.
**Pitfalls:** `settings_data.json` `current` can be a preset **name** (string) instead of an object. The settings then live in `presets[<name>]`.

## 2. Global settings: palette, fonts, buttons
**Purpose:** the competitor's exact look (rule 2) with the fewest moving parts. Custom sections read the palette, so a later palette tweak restyles everything.
**Do** (in `config/settings_data.json` → `current`):
- **Horizon 4:** `color_palette` = competitor hex 1:1, with roles chosen once and documented in the vars snippet. Noxis: `background #FFFFFF`, `foreground #000000`, `color1 #FFB800` (amber accent), `color2 #0E1B4D` (navy), `color3 #E5E5E5` (lines). Point roles at the palette: `palette_primary_button_background: "{{ settings.color_palette.color1 }}"`, `palette_primary_button_text: "{{ settings.color_palette.foreground }}"`, `palette_primary_button_border`, `badge_sale_background_color`. Fonts: `type_heading_font: "poppins_n7"`, `type_accent_font: "poppins_n7"`, `type_body_font: "inter_n4"`. Buttons: `button_border_radius_primary/secondary: 40`, `card_corner_radius: 12`.
- **Dawn:** edit `color_schemes.scheme-1` (page) and add schemes for accent bands (e.g. `scheme-3` amber, `scheme-4` navy). Set `type_header_font` / `type_body_font` and `buttons_radius`.
- **Fonts:** use the font-picker handle closest to the competitor's family (`<family>_n<weight/100>`, e.g. `poppins_n7`). If the competitor uses a custom font the picker lacks, self-host a `.woff2` in `assets/<slug>-*.woff2` with `@font-face` in a snippet. **Never load Google Fonts / Typekit from the theme** (RemoteAsset, privacy, speed).
**Output:** settings diff limited to the keys above.
**Done when:** the editor's Theme settings show the competitor palette/fonts, and buttons are pill-shaped if theirs are.
**Pitfalls:** on a store that sells other products, global settings change every page. Ask the operator before pushing `settings_data.json` there, or scope colors to your sections. Keep hex values exact (no "close enough").

## 3. Header, announcement bar, footer
**Purpose:** the first visual band and the offer line ("FREE Shipping on orders over $30+") are part of the clone.
**Do:**
- Horizon: `sections/header-group.json` → `_announcement` block `text`, `font_size`, `weight`. Announcement section `background_color: "{{ settings.color_palette.color1 }}"`, `divider_width: 0`, padding. Header `logo_position` (Noxis: `center`), `show_language: false` if one market. `sections/footer-group.json`: only adjust if the competitor footer differs structurally (Noxis kept the default).
- Dawn: `sections/header-group.json` → `announcement-bar` blocks + `color_scheme`. Header `logo_position`, `menu`.
- The logo is the operator's upload (Theme settings → logo). Don't generate one unless asked.
**Done when:** the top 120 px of the page matches the competitor screenshot at 390 px and desktop.
**Pitfalls:** group JSON files are shared by all templates. Change only the keys you need.

## 4. Component inventory: native vs custom
**Purpose:** decide, per SECTION_SPEC component, the cheapest faithful implementation before writing code.
**Do:** fill this table in your working notes (one row per component, top to bottom):
```
COMPONENT (spec §)      │ NATIVE OPTION (theme)             │ MATCH? │ DECISION
────────────────────────┼───────────────────────────────────┼────────┼───────────────────────────────
Gallery                 │ _product-media-gallery / main-product media │ yes │ native; images = Shopify product media
Rating line             │ none (reviews app shows stars)    │ no     │ custom block <slug>-rating
Title                   │ text block {{ closest.product.title }} │ yes │ native, type_preset h3
Subtitle                │ text block                        │ yes    │ native (rich text → <p>)
Benefit checklist       │ none                              │ no     │ custom block <slug>-checklist
Bundle & save cards     │ variant-picker buttons            │ no     │ custom <slug>-bundle + _<slug>-bundle-tier, drives hidden native picker
Add to cart             │ buy-buttons                       │ yes    │ native (theme primary button = palette color1)
Info accordion          │ accordion / collapsible_tab       │ yes    │ native rows
Testimonials            │ none matching (cards w/ photo)    │ no     │ custom section <slug>-testimonials
Image + text story      │ media-with-content / image-with-text │ partial │ custom <slug>-image-text if layout/ratio differs
Comparison table        │ none                              │ no     │ custom section <slug>-comparison
FAQ                     │ accordion section                 │ partial │ custom <slug>-faq if icons/exclusive behaviour needed
```
**Done when:** every spec component has a decision, and every custom component has a file name.
**Pitfalls:** "partial" native matches usually cost more time in tweaks than a small custom section. Custom files are also easier to keep identical across brands.

## 5. Build the custom blocks and sections

### 5.1 Naming and file layout
- Prefix everything with the brand slug: `sections/<slug>-comparison.liquid`, `blocks/<slug>-bundle.liquid`, private child blocks `blocks/_<slug>-bundle-tier.liquid` (leading `_` = only usable inside its parent), `snippets/<slug>-vars.liquid`, `assets/<slug>-night-road.webp`. Section keys in templates: `<short>_<role>` (`nx_testimonials`).
- CSS class prefix: short and unique (`nx-`, `nxb`, `nxt`, `nxc`, `nxf`) so nothing collides with theme classes.
- Each file defines **all** classes it uses in its own `{% stylesheet %}` (ValidScopedCSSClass). Duplicate tiny base rules (heading, padding) per file instead of sharing a base stylesheet. Ceriva's shared `cv` base stylesheet in a snippet triggered scoped-CSS problems, and Noxis fixed it by duplicating.
- Every section: `padding_top`/`padding_bottom` range settings → CSS vars, `"tag": "section"`, and a preset with sample blocks so it appears in "Add section".

### 5.2 Vars snippet (palette → CSS custom properties)
Purpose: one place maps theme settings to brand tokens, so sections never hard-code brand hex.
```liquid
{%- comment -%} snippets/<slug>-vars.liquid — inline CSS vars from the theme palette {%- endcomment -%}
--nx-amber: {{ settings.color_palette.color1 }}; --nx-navy: {{ settings.color_palette.color2 }}; --nx-line: {{ settings.color_palette.color3 }};
--nx-bg: {{ settings.color_palette.background }}; --nx-fg: {{ settings.color_palette.foreground }};
--nx-amber-soft: rgb(from {{ settings.color_palette.color1 }} r g b / 0.11);
--nx-heading: var(--font-heading--family); --nx-body: var(--font-body--family);
```
Use: `<div class="nxt" style="{% render '<slug>-vars' %} --nx-pt: {{ section.settings.padding_top }}px;">`. Dawn: read `settings.color_schemes['scheme-1'].settings.button` etc., or put the section on a `color_scheme` setting and use `rgb(var(--color-button))`.
Pitfall: snippets rendered with `{% render %}` have an isolated scope. `settings` is global in Shopify, but local harnesses must pass it as a global (render_sections.js does).

### 5.3 Media snippet (ratio-locked frame + labeled placeholder)
Purpose: images keep the competitor's exact ratio, and until real images exist, the placeholder tells the operator what to upload.
```liquid
{%- comment -%} snippets/<slug>-media.liquid  params: image, asset, ratio ('4 / 5'), label, sizes, radius, eager {%- endcomment -%}
<div class="nx-media" style="aspect-ratio: {{ ratio | default: '1 / 1' }};{% if radius %} --nx-media-radius: {{ radius }}px;{% endif %}">
  {%- if image -%}{{ image | image_url: width: 1600 | image_tag: loading: 'lazy', sizes: sizes, widths: '360, 540, 720, 900, 1200, 1600', alt: image.alt }}
  {%- elsif asset != blank -%}<img src="{{ asset | asset_url }}" alt="{{ label | escape }}" loading="lazy" decoding="async" width="1200" height="1200">
  {%- else -%}<div class="nx-media__ph" role="img" aria-label="{{ label | escape }}"><span>{{ label }}</span></div>{%- endif -%}
</div>
{% stylesheet %} .nx-media{position:relative;overflow:hidden;border-radius:var(--nx-media-radius,0);background:#ececec}
 .nx-media>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
 .nx-media__ph{position:absolute;inset:0;display:grid;place-items:center;padding:16px;background:linear-gradient(135deg,#f1f1f1,#dcdcdc);color:#6b6b6b;font-size:12px;text-align:center} {% endstylesheet %}
```
Settings pair in each section: `image` (`image_picker`, the merchant's upload) **or** `asset` (`text`, a theme file such as `noxis-night-road.webp`, used for GIF→WebP conversions and pre-made remakes you ship in `assets/`), plus `placeholder_label`. Each placeholder label describes the shot ("Man in his 50s, selfie in the driver's seat at night, wearing the glasses"). Set the ratio to the competitor's measured ratio.
Pass `eager: true` only for the above-the-fold image (LCP).

### 5.4 Bundle picker (parent block + tier blocks + JS driver)
Purpose: competitor-style "Bundle & Save" cards that **select real variants**, so price, sticky bar, form `id` and cart all update through the theme's own code. The native variant picker stays in the DOM, hidden, and the cards drive it.

**Parent `blocks/<slug>-bundle.liquid`** (Horizon theme block placed inside `_product-details`):
```liquid
{%- liquid
  assign product_resource = closest.product
  if request.visual_preview_mode and product_resource == blank
    assign product_resource = collections.all.products.first
  endif
-%}
{%- unless product_resource == blank -%}
<nx-bundle class="nxb" style="{% render '<slug>-vars' %}" {% if block.settings.hide_native_picker %}data-hide-native{% endif %} {{ block.shopify_attributes }}>
  {%- if block.settings.heading != blank %}<p class="nxb__heading">{{ block.settings.heading }}</p>{% endif -%}
  <div class="nxb__tiers" role="radiogroup" aria-label="{{ block.settings.heading | default: 'Choose your bundle' | escape }}">
    {% content_for 'blocks', closest.product: product_resource %}
  </div>
</nx-bundle>
{%- endunless -%}
{% stylesheet %}
  /* ...card list styles... */
  .product-details:has(.nxb[data-hide-native]) variant-picker { display: none; } /* hidden, still in the DOM */
{% endstylesheet %}
{% javascript %}
if (!customElements.get('nx-bundle')) {
  customElements.define('nx-bundle', class extends HTMLElement {
    connectedCallback() {
      this.addEventListener('change', this.onChange);
      customElements.whenDefined('variant-picker').then(() => this.syncInitialState());
    }
    disconnectedCallback() { this.removeEventListener('change', this.onChange); }
    picker() { return (this.closest('.shopify-section') || document).querySelector('variant-picker'); }
    syncInitialState() {                       // preselected tier wins unless ?variant= is in the URL
      const inputs = [...this.querySelectorAll('.nxb-tier__input')], checked = inputs.find((i) => i.checked);
      if (checked?.dataset.preselect !== undefined && checked.dataset.variantId && !new URL(location.href).searchParams.has('variant'))
        return this.select(checked.dataset.variantId);
      if (!checked) {                          // mirror the variant the theme already shows
        const p = this.picker(), cur = p?.querySelector('input:checked')?.dataset.variantId || p?.querySelector('option:checked')?.dataset.variantId;
        const m = inputs.find((i) => i.dataset.variantId === cur) || inputs[0];
        if (m) { m.checked = true; m.closest('.nxb-tier')?.classList.add('is-selected'); }
      }
    }
    onChange = (e) => {
      const i = e.target; if (!(i instanceof HTMLInputElement) || !i.dataset.variantId) return;
      this.querySelectorAll('.nxb-tier').forEach((t) => t.classList.toggle('is-selected', t.contains(i)));
      this.select(i.dataset.variantId);
    };
    select(id) {                               // forward to the native picker: theme updates price/form/cart
      const p = this.picker(); if (!p) return;
      const r = p.querySelector(`input[type="radio"][data-variant-id="${id}"]`);
      if (r) { if (!r.checked) r.click(); return; }
      const o = p.querySelector(`option[data-variant-id="${id}"]`), s = o?.closest('select');
      if (o && s && s.value !== o.value) { s.value = o.value; s.dispatchEvent(new Event('change', { bubbles: true })); }
    }
  });
}
{% endjavascript %}
{% schema %}{ "name": "<Brand> bundle & save", "blocks": [{ "type": "_<slug>-bundle-tier" }],
  "settings": [ { "type": "paragraph", "content": "Each card is a product variant (option \"Bundle\": Buy 1 / Buy 2 / Buy 3). Prices come from the variants. Keep the Variant picker block: it is hidden and driven by these cards." },
    { "type": "text", "id": "heading", "label": "Heading", "default": "Bundle & Save" },
    { "type": "checkbox", "id": "hide_native_picker", "label": "Hide the native variant picker", "default": true } ],
  "presets": [{ "name": "<Brand> bundle & save", "blocks": { "tier_1": {...}, "tier_2": {..., "preselect": true}, "tier_3": {...} }, "block_order": ["tier_1","tier_2","tier_3"] }] }{% endschema %}
```

**Tier `blocks/_<slug>-bundle-tier.liquid`.** It finds its variant **by name** (`option_value` = exact variant title) or **by position** (`variant_position`), computes SAVE = compare − price, and falls back safely when the product has no variants:
```liquid
{%- liquid
  assign p = closest.product
  assign bs = block.settings
  assign v = null
  if bs.option_value != blank
    assign wanted = bs.option_value | strip | downcase
    for x in p.variants
      assign t = x.title | strip | downcase
      if t == wanted
        assign v = x
        break
      endif
    endfor
  endif
  if v == null
    assign idx = bs.variant_position | minus: 1
    if p.variants.size > idx
      assign v = p.variants[idx]
    endif
  endif
  assign matched = true
  if v == null or p.has_only_default_variant
    assign matched = false
    assign v = p.selected_or_first_available_variant
  endif
  assign compare = v.compare_at_price | default: 0
  assign saved = 0
  if compare > v.price
    assign saved = compare | minus: v.price
  endif
  assign selected = false
  if p.selected_variant
    if matched and v.id == p.selected_variant.id
      assign selected = true
    endif
  elsif bs.preselect
    assign selected = true
  endif
-%}
<label class="nxb-tier{% if selected %} is-selected{% endif %}{% unless v.available %} is-unavailable{% endunless %}" {{ block.shopify_attributes }}>
  <input class="nxb-tier__input visually-hidden" type="radio" name="nxb-{{ section.id }}" value="{{ v.id }}"
    {% if matched %}data-variant-id="{{ v.id }}"{% endif %} {% if selected %}checked{% endif %} {% if bs.preselect %}data-preselect{% endif %} {% unless v.available %}disabled{% endunless %}>
  {%- if bs.badge != blank %}<span class="nxb-tier__badge">{{ bs.badge }}</span>{% endif -%}
  <span class="nxb-tier__main">
    <span class="nxb-tier__thumb">{% assign th = bs.image | default: v.featured_image | default: p.featured_image %}{% if th %}{{ th | image_url: width: 120 | image_tag: loading: 'lazy', alt: '', width: 44, height: 44 }}{% endif %}</span>
    <span class="nxb-tier__title">{{ bs.title | default: v.title }}{% if saved > 0 %} <span class="nxb-tier__pill">SAVE {{ saved | money }}</span>{% endif %}</span>
    <span class="nxb-tier__prices"><span>{{ v.price | money }}</span>{% if compare > v.price %}<s>{{ compare | money }}</s>{% endif %}</span>
  </span>
  {%- if bs.gift != blank %}<span class="nxb-tier__gift"><span>{{ bs.gift }}</span>{% if bs.gift_value != blank %}<s>{{ bs.gift_value }}</s>{% endif %}</span>{% endif -%}
</label>
```
Tier schema settings: `option_value`, `variant_position` (range 1–10), `title`, `subtitle`, `badge` ("MOST POPULAR"/"BEST VALUE"), `image`, `gift` ("+ 2 FREE Glasses Cases"), `gift_value` (crossed out), `gift_image`, `preselect`.
Styling to copy from the competitor: radius (Noxis 18 px), border in the accent color, soft accent background on unselected cards and white on the selected one, gift strip grey→accent when selected, badge overlapping the top-right corner, divider lines on the heading in the accent at 45% opacity. Accessibility: the radio is visually hidden, not `display:none`, and the focus ring goes on the card: `.nxb-tier:has(.nxb-tier__input:focus-visible){outline:2px solid #000;outline-offset:2px}`.
**Why drive the native picker instead of writing `input[name=id]` yourself:** the theme then updates price, sticky add-to-cart, media, URL and availability exactly as with its own buttons. Writing the form id directly leaves the rest of the page stale.
**Limits:** this works for single-option products (one "Bundle" option). With two options (color × bundle), a card must set both option inputs. Build that only if the spec needs it.

### 5.5 Small buy-box blocks
- `<slug>-rating`: 5 SVG stars filled with the accent + one text setting ("Rated 4.8/5 by 1,300+ drivers", carried 1:1 from the competitor pattern).
- `<slug>-checklist`: `item_1..item_6` text settings, rendering only the non-blank ones, with an outline check SVG. Copy letter-spacing and size from the competitor (Noxis: 14 px, 0.04 em).
- Add them in `_product-details` `block_order` in the competitor's order: rating → title → subtitle → checklist → bundle → (hidden) variant picker → buy buttons → accordion.

### 5.6 Testimonials rail (mobile first + drag)
Desktop: 3-column grid. Mobile: horizontal rail with snap, a peeking next card, and **pointer drag**.
```liquid
<div class="nxt__grid" data-nx-drag>{% for block in section.blocks %}<article class="nxt__card" {{ block.shopify_attributes }}>
  {% render '<slug>-media', image: block.settings.image, asset: block.settings.image_asset, ratio: '1 / 1', label: block.settings.placeholder_label %}
  <div class="nxt__body"><span class="nxt__stars" aria-label="5 out of 5 stars">★★★★★</span><div class="nxt__text">{{ block.settings.text }}</div><p class="nxt__name">{{ block.settings.name }}</p></div>
</article>{% endfor %}</div>
{% stylesheet %}
 .nxt__grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;max-width:1040px;margin:0 auto;padding-inline:16px}
 @media screen and (max-width:749px){
  .nxt__grid{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scroll-padding-inline:16px;scrollbar-width:none;cursor:grab;overscroll-behavior-x:contain}
  .nxt__grid::-webkit-scrollbar{display:none}
  .nxt__grid.is-dragging{scroll-snap-type:none;cursor:grabbing;user-select:none}
  .nxt__card{flex:0 0 clamp(230px,76vw,320px);scroll-snap-align:start} }
{% endstylesheet %}
{% javascript %}
(() => {                                   // mouse/pen drag for rails; touch keeps native swipe
  const init = () => document.querySelectorAll('[data-nx-drag]:not([data-nx-drag-ready])').forEach((rail) => {
    rail.dataset.nxDragReady = '';
    let x0 = 0, s0 = 0, id = -1, moved = false;
    rail.addEventListener('pointerdown', (e) => {
      if (e.pointerType === 'touch' || e.button !== 0 || rail.scrollWidth <= rail.clientWidth) return;
      id = e.pointerId; x0 = e.clientX; s0 = rail.scrollLeft; moved = false;
    });
    rail.addEventListener('pointermove', (e) => {
      if (e.pointerId !== id) return;
      const dx = e.clientX - x0;
      if (!moved && Math.abs(dx) < 4) return;
      if (!moved) { moved = true; rail.classList.add('is-dragging'); rail.setPointerCapture(id); }
      rail.scrollLeft = s0 - dx;
    });
    const end = () => {
      if (id === -1) return; id = -1; if (!moved) return;
      const left = rail.scrollLeft; rail.classList.remove('is-dragging'); rail.scrollLeft = left;
      const card = rail.firstElementChild, step = card ? card.getBoundingClientRect().width + parseFloat(getComputedStyle(rail).columnGap || 0) : 0;
      if (step) rail.scrollTo({ left: Math.round(left / step) * step, behavior: 'smooth' });
    };
    rail.addEventListener('pointerup', end); rail.addEventListener('pointercancel', end);
    rail.addEventListener('click', (e) => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  });
  init(); document.addEventListener('shopify:section:load', init);
})();
{% endjavascript %}
```
Block settings: `image`, `image_asset`, `placeholder_label`, `text` (richtext), `name`. The review text must match its photo (00 §5: mom vs dad).

### 5.7 Image with text
Two-column grid (`1fr 1fr`), `image_first` checkbox to flip on desktop, single column on mobile with the **image first** (it's the hook on phones), `ratio` select (`1 / 1`, `4 / 5`, `4 / 3` — add the competitor's), rich-text body with `<strong>` emphasis in the foreground color. Point `asset` at the WebP conversions of the competitor GIFs (`<slug>-night-road.webp`, ~90% lighter than the GIF). Keep the raw GIFs in `PRODUCT_DIR`.

### 5.8 Comparison table
A semantic `<table>` (`th scope="col"/"row"`). The highlighted "us" column has an accent background with rounded top (header cell) and bottom (last row) corners. Per-row settings: `label`, `us` (check), `us_text` (word instead of icon, e.g. "Yes"), `them`, `them_text`. Heading + `title_accent` span in the accent color ("Why Choose **Us?**"). Icons are SVG with `aria-label="Yes"/"No"` and `display:block; margin-inline:auto` so they center (a QA fix in Noxis). On mobile, compact the table (padding 10 px 4 px, 11–12 px text) so it never scrolls.

### 5.9 FAQ
Native `<details name="nxf-{{ section.id }}">` gives an **exclusive accordion** (opening one closes the others) without JS. Use `summary` with `list-style:none` and hide `::-webkit-details-marker`. The caret rotates on `[open]`. Answers are richtext, so they need `<p>` (§6). Put the objection-handling questions first, as the competitor does.

### 5.10 Scroll-to-offer CTA (when the spec has "Get yours" buttons below the fold)
Horizon scrolls `.page-wrapper` on desktop, not `window`, so `window.scrollTo` does nothing there. Use `target.scrollIntoView({behavior:'smooth', block:'start'})` with `scroll-margin-top` = header height + 16. Target the bundle block (`.nxb`) → `.buy-buttons-block` → `[id^="ProductInformation-"]`, then flash it briefly. Pattern: `assets/ceriva.js` on branch `ceriva` (`git show ceriva:assets/ceriva.js`) with the `ceriva-cta` snippet (`data-cv-action="offer|cart"`). Respect `prefers-reduced-motion`.

### 5.11 Wiring to Dawn (and Dawn-likes)
- Dawn has no theme blocks inside `main-product`. Either (a) add a block type `{"type":"<slug>_bundle","name":"Bundle & save","settings":[...]}` to `main-product`'s schema and render it with `{% when '<slug>_bundle' %}{% render '<slug>-bundle', block: block, product: product %}` (tier data as `tier_1_*`…`tier_3_*` settings), or (b) use an `@app`-style section below the main section if the spec allows. (a) edits a core file, so keep the diff minimal and note it in delivery (theme updates will conflict).
- Variant driving: Dawn ≥ 11 renders `<variant-selects>` with radios `input[type=radio]` whose **value is the option value** (no variant id), or `<select>`. Find the radio whose `value` == `variant.option1` (output `data-option-value="{{ v.option1 | escape }}"` on the card) and `.click()` it, or set the select value and dispatch `change` with `bubbles: true`. Dawn then re-renders price and updates `product-form input[name="id"]`. Dawn < 11: `<variant-radios>` / `<variant-selects>` with the same value matching.
- Hide the native picker with `.product__info-wrapper:has([data-hide-native]) variant-selects{display:none}`.
- Colors: section `color_scheme` setting (`class="color-{{ section.settings.color_scheme }}"`), and use `rgb(var(--color-button))` instead of palette tokens.

## 6. Generate the template JSON with a Python builder
**Purpose:** reproducible templates, valid settings (Shopify rejects some values only at push time), and fast copy swaps (v2 pages, translations).
**Do:** write `PRODUCT_DIR/scratch/build_<slug>_template.py`:
```python
"""Build templates/product.json for <Brand> (Mode A clone of <competitor>)."""
import copy, json, re, sys
SRC, OUT = sys.argv[1], sys.argv[2]           # SRC = a template that already works in this theme (e.g. main's product.json)
raw = open(SRC, encoding="utf8").read()
header = re.match(r"\s*/\*[\s\S]*?\*/\s*", raw).group(0)    # keep Shopify's auto-generated header comment
src = json.loads(raw[len(header):])

main = copy.deepcopy(src["sections"]["main"])  # deep-copy a PROVEN main section: all required settings stay valid
pd = main["blocks"]["product-details"]; cvb = pd["blocks"]

def setv(node, **kw):
    """Set settings; wrap plain text in <p> when the original value was rich text (push rejects bare text)."""
    for k, v in kw.items():
        orig = node["settings"].get(k)
        if isinstance(v, str) and isinstance(orig, str) and orig.lstrip().startswith("<") and not v.lstrip().startswith("<"):
            v = f"<p>{v}</p>"
        node["settings"][k] = v

def text_block(html, preset="paragraph"):     # clone a native text block and replace its content
    b = copy.deepcopy(cvb["subtitle"]); setv(b, text=html, type_preset=preset); return b

blocks = {
  "rating": {"type": "<slug>-rating", "settings": {"text": "Rated 4.8/5 by 1,300+ drivers"}, "blocks": {}},
  "title": copy.deepcopy(cvb["title"]),                                  # "<h1>{{ closest.product.title }}</h1>"
  "subtitle": text_block("Every winter the drive home gets harder."),     # -> auto <p>
  "checklist": {"type": "<slug>-checklist", "settings": {"item_1": "...", "item_2": "..."}, "blocks": {}},
  "bundle": {"type": "<slug>-bundle", "settings": {"heading": "Bundle & Save", "hide_native_picker": True},
             "blocks": {f"tier_{i}": {"type": "_<slug>-bundle-tier", "settings": s} for i, s in enumerate(TIERS, 1)},
             "block_order": [f"tier_{i}" for i in range(1, len(TIERS) + 1)]},
  "variant_picker": copy.deepcopy(cvb["variant_picker"]),               # keep: hidden, driven by the cards
  "buy_buttons": copy.deepcopy(cvb["buy_buttons"]),
  "accordion": ACCORDION,                                               # deep-copied rows with new heading/text
}
pd["blocks"] = blocks; pd["block_order"] = list(blocks)

sections = {"main": main, "nx_testimonials": {...}, "nx_compare": {...}, "nx_faq": {...}}
tpl = {"sections": sections, "order": ["main", "nx_testimonials", "nx_story", "nx_compare", "nx_honest", "nx_faq"]}
open(OUT, "w", encoding="utf8", newline="\n").write(header + json.dumps(tpl, ensure_ascii=False, indent=2) + "\n")
```
- **Copy:** paste the copywriter's deck verbatim, with claims at full strength (00 §1). Rich-text settings (`richtext`, Horizon `text` block `text`, accordion row text, FAQ answers) must start with `<p>`, `<ul>`, `<ol>` or `<h1>`–`<h6>`. Otherwise the push fails with « Tous les nœuds de niveau supérieur doivent être des balises <p>… ».
- **French or other markets:** add a typography helper (FR: narrow no-break space before `? ! : ;` and inside `« »`: `re.sub(r" ([?!:;»])", " \\1", t)`) and apply it in `setv`.
- **Variant pages (v2):** load the live template instead of building from scratch, `setv` only the copy, drop or reorder sections, print a word count of the visible copy (the operator compares length with the competitor), and write `product.<slug>-v2.json` (tools §9).
- Placeholders: set `placeholder_label` + competitor ratio for every image you don't have yet, and `image_asset`/`asset` for files you ship.
**Output:** `templates/product.json` (fresh brand branch from main) or `product.<slug>.json` / `-v2.json` (store with live traffic). Keep the builder script in `PRODUCT_DIR/scratch/`.
**Done when:** the JSON parses, every `type` has a file, every block type is allowed by its parent schema, and every setting id exists in the schema.
**Pitfalls:** hand-typing a main section loses required settings and breaks editor previews, so always deep-copy. Range values must respect min/max/step. Select values must be valid options. Block ids must be unique per parent.

## 7. Theme check
Run `shopify theme check` (tools §7). Pass = no new offenses vs the main baseline. Fix ValidScopedCSSClass by moving class definitions into the file. Fix RemoteAsset by self-hosting. Use `preload_tag` for preloads, and give every `<img>` width/height.

## 8. Local QA render + buy-box mock
**Purpose:** see the real Liquid/CSS output at 390 px and desktop before any push (and without a store).
**Do:**
1. One-time: `npm i liquidjs@10 --prefix "$PRODUCT_DIR/scratch/qa"` (never inside the theme repo).
2. Render + screenshot:
```bash
node "<skill>/scripts/render_sections.js" --theme "$THEME_DIR" --template templates/product.json \
  --modules "$PRODUCT_DIR/scratch/qa/node_modules" --buybox --product "$PRODUCT_DIR/02_competitor/page/p.json" \
  --title "Noxis Polarized Headlight Glasses" --images "$PRODUCT_DIR/04_page-images" \
  --out "$PRODUCT_DIR/scratch/qa/page.html" --shot
```
   - Prints theme, palette (from `color_palette` or the first `color_schemes` entry) and fonts read from `settings_data.json`. Check that they're the competitor's.
   - Renders every non-main section whose file exists (`--sections key1,key2` to pick). Collects `{% stylesheet %}`/`{% javascript %}`, stubs `asset_url`/`image_url`/`image_tag`/`money`/`t`/`preload_tag`, resolves `{% content_for 'blocks' %}`, and forces `loading="eager"`.
   - `--buybox`: renders the main section's **custom** blocks (prefix auto-detected or `--prefix`) for real against a mock product (`--product` = competitor `p.json`, or a default Buy 1/2/3), and native blocks as stand-ins (title, text, hidden `variant-picker` radios, ATC in the theme button colors, accordions). The bundle JS runs, so clicking a card selects the native radio and updates the mock price.
   - `--shot`: headless Edge/Chrome with its own `--user-data-dir` writes `page-desktop.png` (1280 wide) and `page-mobile.png` (390 px iframe inside a 500 px window, so crop x ≤ 390). Heights are measured automatically.
   - Exit code 1 = a Liquid error (shown in the page as a red box).
3. Read the screenshots next to the competitor's (`10-qa` §2): desktop and mobile, section by section.
4. **Pointer-drag test (mobile first):** open the page in a 390 px viewport (Edge device mode or the editor's mobile preview) and drag each rail with the mouse. It must move and snap. A rail that only scrolls with touch or a trackpad fails.
5. If the theme's main section uses native blocks you replaced visually (e.g. a price block styled by the theme), compare with a cropped competitor buy box, or finish with the real draft preview once a store exists.
**Known harness artefacts:** theme base CSS isn't loaded (pass `--css base.css` for Dawn), lazy images are forced eager, Google Fonts are loaded for QA only (`--fonts none` offline), and the theme's own gallery and header aren't rendered.

## 9. Commit → pull/merge → push draft
Follow tools §4–§8 exactly: stage your files, commit (attribution line), `git pull --no-rebase` + `git diff <yours> HEAD -- <files>`, `shopify theme pull --only <files>` (commit first!), theme check, push with `--nodelete --only` to the **draft** id, and `git push -u origin <slug>`. No store yet → GitHub only, and ask for the store in delivery.

## 10. Delivery notes for the operator
Paste into DELIVERY.md, filled in:
- [ ] **Create the product** with the exact title (`<Brand> <competitor title pattern>`) and assign template `product` (or `product.<slug>-v2`).
- [ ] **Create variants**: option "Bundle" with Buy 1 / Buy 2 / Buy 3, each with **price + compare-at price** (list them from the competitor capture: e.g. $39.95/$59.90, $69.90/$119.80, $89.85/$179.70). The cards show SAVE = compare − price, so a missing compare-at hides the pill.
- [ ] **Upload product media** in gallery order (`03_product-images/` remakes, packshot first). The gallery comes from the Shopify product, not the theme.
- [ ] **Page images**: either already shipped as theme assets (list `assets/<slug>-*`), or upload them in the editor into the labeled placeholders (map: section → placeholder label → file in `04_page-images/`).
- [ ] **Free gifts are display-only.** The gift strips ("+ 2 FREE Glasses Cases") don't add anything to the cart. Configure a bundle app (e.g. Kaching-style) or an automatic discount / free-gift rule, or remove the strips.
- [ ] **Reviews app** if the competitor shows a review widget (stars count, review list): install and place its app block. The rating line is static text.
- [ ] **Store connection**: store domain + draft theme id (if pushed to GitHub only), or connect the branch via Shopify's GitHub integration.
- [ ] Global settings changed (palette, fonts, buttons, announcement): confirm on a shared store.
- [ ] Preview links: product preview with `preview_theme_id`, editor link.

## 11. Pitfalls index
| Pitfall | Where |
|---|---|
| Rail scrolls only by touch → can't scroll in the editor's mobile preview | §0, §5.6 |
| Rich text without `<p>` → push rejected | §6, tools §10 |
| `{% stylesheet %}` class defined in another file → ValidScopedCSSClass | §5.1 |
| Google Fonts / CDN → RemoteAsset | §2 |
| `window.scrollTo` does nothing in Horizon | §5.10 |
| Snippet loses `settings` in local harness | §5.2, §8 |
| Bundle cards writing the form id directly → stale price/sticky bar | §5.4 |
| Multi-option products and bundle cards | §5.4 limits |
| Gifts shown but not delivered | §10 |
| Theme pull overwrote uncommitted work | tools §1 |
| Bot merge reverted your files | tools §6 |
| Overwriting a template with live ads | tools §9 |
| Main section hand-written → invalid settings in editor | §6 |
| Lazy images blank in headless screenshots | §8 |
