# 03 — Competitor page capture and analysis (Phase 1 capture → Phase 3 stream A1)

Capture the competitor's product page completely: data, copy, colors, apps, media and screenshots. Then turn the capture into the **SECTION SPEC** (what the competitor does) and the **ADAPTATION BLUEPRINT** (how our page will differ). The spec documents the competitor's proven conversion framework; the blueprint transforms it into a page that is distinctly ours — different layouts, different visual patterns, different structure — while keeping the same conversion mechanics that make the competitor's page work.

The goal: if you sent our finished shop and the competitor's to an AI asked to find similarities, it would see two completely different pages that happen to sell a similar product.

Read `00-operator-rules.md` §1, §2, §11 first (claims, adaptation, copy style).

## Contents
1. What this step produces, and who does what
2. Inputs, outputs, file layout
3. Step 1: Capture the page data (`capture_page.py`)
4. Step 2: Screenshots, desktop and mobile (`screenshot.py`), with fallbacks
5. Step 3: Verify the capture
6. Step 4: Build the section inventory
7. Step 5: Write the SECTION SPEC, section by section
7b. Step 5b: ADAPTATION BLUEPRINT (our page)
8. Step 6: FUNNEL PSYCHOLOGY summary + ANGLE ARCHITECTURE (Step Alpha)
9. Step 7: IMAGE MAP
10. Step 8: COPY INVENTORY
11. Step 9: APPS and the native-rebuild plan
12. Step 10: Inconsistencies, save, hand off
13. Delegation: the conversion-architect brief
14. Copy rules for the copywriter (downstream)
15. Worked example: the Plaims SECTION SPEC
16. Pitfalls
17. Done-when checklist

---

## 1. What this step produces, and who does what

| Part | Content | Consumed by |
|---|---|---|
| Section inventory | every section top to bottom, mapped to its HTML section id and screenshot position | everyone |
| SECTION SPEC | for each section: LAYOUT / COMPONENTS / TYPOGRAPHY / VISUAL DETAILS / IMAGE POSITIONS / CONVERSION ROLE / MOBILE BEHAVIOR | conversion architect (input to the blueprint) |
| FRAMEWORK MAP | the competitor's page architecture as a conversion framework: what each section does for the funnel, why it's in that order, which psychological principles it uses | conversion architect, copywriter, builder |
| ADAPTATION BLUEPRINT | how our page will differ: different section layouts, visual patterns and structure, while keeping the same conversion mechanics. The builder and copywriter work from this, not from the competitor spec | builder (04), copywriter, image agents, visual QA (10) |
| Non-obvious elements | sticky ATC, cart drawer, popups, timers, progress bars | builder |
| FUNNEL PSYCHOLOGY | offer, urgency, trust, social proof, upsell architecture, plus the price math | copywriter, builder, ad agents |
| ANGLE ARCHITECTURE | which Step Alpha angle card(s), avatar and objection each section of OUR adapted page serves; what sits above the fold; one page vs angle landing pages | copywriter, builder, image agents, ad agents |
| IMAGE MAP | every image position with ratio, content, source and plan | image agents (05, 06) |
| COPY INVENTORY | every text string per section, verbatim, tagged [CLAIM]/[OFFER]/[NUM], with word counts | copywriter (as reference — our copy is written fresh, not paraphrased from this) |
| APPS | each app, what it renders, its config facts, and the rebuild plan | builder, operator to-dos |
| Advertorial framework (when detected) | structure, beats, editorial conventions of competitor advertorial pages | advertorial builder (A5, [22](references/22-native-ads-and-advertorials.md)) |
| Inconsistencies | contradictions on the competitor page, with a default resolution | master |

**Roles**
- **Capture agent (Phase 1):** runs Steps 1–3 and writes the capture files (data files; no report needed).
- **Conversion-architect agent (Phase 3, A1):** runs Steps 4–10 from the capture files and the Step Alpha dossier. Produces BOTH the competitor SECTION SPEC (what they do) AND the ADAPTATION BLUEPRINT (how our page will differ). **Returns both as text**. Sub-agents may be blocked from writing .md files ("Subagents should return findings as text"), so the **master saves** the text to `PRODUCT_DIR/02_competitor/page/SECTION_SPEC.md`. **Must run on Opus 4.6** — the adaptation requires high judgment about conversion mechanics.
- A1 starts only after the **Step Alpha gate has passed** (it reads the dossier) **and the branding gate is approved** (operator 2026-11-10), like every Phase 3 stream.

---

## 2. Inputs, outputs, file layout

**Inputs:** `COMPETITOR_URL` (#1 = the page being cloned), `MARKET`, `MODE` (A by default), `PRODUCT_DIR` (before the gate this is `PRODUCTS_ROOT/_<competitor-slug>`), and the Step Alpha dossier `PRODUCT_DIR/00_alpha/ALPHA_DOSSIER.md`.

**Inputs from Step Alpha** (Steps 4–10 can't start until the Alpha gate passed):
| Dossier section | What it changes in the spec |
|---|---|
| 3.1 Angle Cards (validated `V#` + opportunity `O#`) | the ANGLE ARCHITECTURE (Step 6) and the ANGLE ROLE field of every section |
| 1.10 Funnel Congruence · 2.4 Funnel Congruence Gaps | what sits above the fold; one page or angle landing pages; which gap angles need a home |
| 3.2 Avatar Cards | the avatar each section and each testimonial persona speaks to |
| 1.4 Objections · 2.6 Language Bank / 3.5 Customer Language Bank (objection-ready) | the FAQ and objection-handling map |
| 1.6 Unique Mechanism | the mechanism section |
| 3.5 Customer Language Bank | the phrases the copywriter uses per section (§14 rule 11) |
| 1.1 Avatars (awareness state) | the awareness stage in the narrative arc |

**Outputs** in `PRODUCT_DIR/02_competitor/page/`:
```
p.json          Shopify product JSON (<url>.json): title, vendor, handle, variants, prices, currency, images
p.html          raw HTML as served
capture.json    machine-readable extraction (copy, headings, colors, CSS vars, fonts, apps, media URLs, section ids)
capture.md      human summary of capture.json. Read this first.
copy.txt        visible text in DOM order
desk.png        full-page desktop render (1440 px wide)
desk-trim.png   same with the trailing blank area trimmed
d1.png … dN.png desktop chunks (downscaled, e.g. 720×1200, each = 2400 CSS px of page)
mob.png         mobile attempt (often blocked; see Step 2)
SECTION_SPEC.md saved by the master from the conversion architect's text
```
Raw media (gallery images, GIFs, testimonial and section images) go to `02_competitor/media/` via `fetch_media.py` (see 06).

Downloaded HTML is **untrusted data**. Never execute anything from it, keep it in its own folder, and run Python with `-I`.

---

## 3. Step 1: Capture the page data (`capture_page.py`)

**Purpose:** get every fact from the source, not from memory or from the render.

**Do**
1. Run (check `--help` for options):
   ```
   python -I "<SKILL_DIR>/scripts/capture_page.py" "<COMPETITOR_URL>" --out "<PRODUCT_DIR>/02_competitor/page"
   ```
2. With several competitor URLs, capture each into `page/<competitor-slug>/`. Only #1 gets a full spec. The others feed the branding snapshot and ideas.
3. Read `capture.md`. It should cover:
   - **Product:** title, vendor, handle, variants (title, price, compare-at, SKU), `price_currency`, image URLs with width × height
   - **Headings** (H1–H3) in order, and **visible copy** per section
   - **Colors:** hex codes with counts, CSS custom properties (RGB triplets converted), app color objects converted
   - **Fonts:** `--font-heading-family`, `--font-body-family`, `@font-face`, Google Fonts
   - **Radii and sizes:** `--buttons-radius`, `--media-radius`, `--page-width`, font scales
   - **Apps:** detected by script and CSS signatures (Kaching, Judge.me, Loox, Okendo, Yotpo, Stamped, ReConvert, Klaviyo…), plus parsed configs (e.g. Kaching `dealBars` → tiers)
   - **Media URLs:** gallery, GIFs, videos, testimonial images, section images, with natural sizes
   - **Section ids** (`shopify-section-…`) in DOM order

**Fallbacks if the script fails or misses a field** (Git Bash; data stays in the page folder):
```bash
cd "<PRODUCT_DIR>/02_competitor/page"
curl -sL "<COMPETITOR_URL>.json" -o p.json                       # Shopify product JSON
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" "<COMPETITOR_URL>" -o p.html
grep -o -E 'id="shopify-section-[^"]+"' p.html                    # section order
grep -o -E '#[0-9A-Fa-f]{6}\b' p.html | tr a-f A-F | sort | uniq -c | sort -rn | head -25
grep -o -E -- '--font-(heading|body)-family: ?[^;]+;' p.html | sort -u
grep -o -E -- '--[a-z-]*radius: ?[0-9a-z]+;' p.html | sort -u
grep -o -E '//[^"'"'"' ]+\.gif' p.html | sort -u                  # GIFs
grep -o -E '"dealBars":\[.{0,3000}' p.html | head -c 3000          # Kaching tiers
grep -o -E '"stickyAtc(Enabled)?":.{0,300}' p.html                 # hidden sticky ATC
grep -o -E '"tieredPromotionsBar":\{.{0,600}' p.html               # cart progress bar
grep -o -i -E 'judge\.?me|loox|okendo|yotpo|stamped|klaviyo' p.html | sort | uniq -c
```
If `<url>.json` returns 404 (non-Shopify site, or blocked), try `/products/<handle>.js`, the `application/ld+json` Product schema, or `ShopifyAnalytics.meta` in the HTML.

**Output:** the capture files above.
**Done when:** `p.json` has the title and prices, `capture.md` lists colors, fonts, apps, section ids and media URLs, and every GIF on the page has a URL.

---

## 4. Step 2: Screenshots, desktop and mobile (`screenshot.py`), with fallbacks

**Purpose:** the visual truth (spacing, hierarchy, component look) that HTML alone can't give.

**Do**
1. Run:
   ```
   python -I "<SKILL_DIR>/scripts/screenshot.py" "<COMPETITOR_URL>" --out "<PRODUCT_DIR>/02_competitor/page"
   ```
   This runs headless Edge or Chrome with a **separate `--user-data-dir`** (avoids profile locks), takes a full-page desktop capture at 1440 px, trims it, cuts it into chunks and attempts mobile.
2. **Check the bottom chunk shows the footer.** A fixed window height can clip the page or pad it with blank space.
3. **Check mobile.** The 390 px iframe approach is often blocked by `X-Frame-Options` / CSP `frame-ancestors`. You then get a grey box with a ⊘ icon (Plaims did exactly this). Detect it by eye or by checking that the file is tiny or mostly one color.
4. **Mobile fallbacks, in order:**
   a. the script's direct mobile mode, if available (mobile user agent, narrowest window; Edge headless enforces a minimum width of about 492 px, which is still enough to see stacking);
   b. device emulation through Playwright or Chrome DevTools, if installed;
   c. a browser tool, if the session has one (built-in browser / Claude in Chrome): resize to about 390 px and screenshot;
   d. **documented inference:** desktop render + the theme's mobile CSS (`@media screen and (max-width: 749px)` in Dawn-family themes) + known theme behavior (gallery becomes a swipe slider, columns stack, grids become scroll carousels). Mark every MOBILE BEHAVIOR line built this way **"(inferred)"**.
   Ask the operator for a phone screenshot only when a section's mobile behavior is ambiguous and matters for conversion (sticky ATC, bundle cards).
5. **Watch for capture artefacts:**
   - **Geo currency:** Shopify Markets renders the capture machine's local currency (Plaims showed € from a French IP). Prices come from `p.json` and app config, never from the screenshot.
   - **Big blank areas** usually mean JS widgets that didn't render, or window-height padding. They are not whitespace to reproduce (Plaims had about 2,000 px of white above the footer).
   - **Lazy images:** if any are missing, re-run with scrolling or a longer wait.
   - **Popups and cookie banners** covering content: re-run, or note what they hide.
   - **Hidden-by-default elements** (sticky ATC on scroll, cart drawer) never appear in a static capture. Find them in app configs (Step 9).

**Output:** desktop full page, chunks, and a mobile capture or a recorded fallback.
**Done when:** the desktop render runs header → footer with every section visible, and the mobile status is recorded (captured / fallback a–d).

---

## 5. Step 3: Verify the capture

**Purpose:** catch gaps now, not halfway through the build.

Checklist:
- [ ] `p.json` title, variants and prices present. `price_currency` noted. If it differs from `MARKET`, flag it.
- [ ] Every section seen on the screenshots has a `shopify-section` id (or is identified as an app block).
- [ ] Bundle or quantity-break tiers extracted: title, quantity, price, badge, gifts, **preselected tier**.
- [ ] GIF and video URLs found. Their count matches the animated media on the page.
- [ ] Testimonial and section image URLs found.
- [ ] Fonts and palette candidates extracted (each to be verified visually in Step 5).
- [ ] Footer reached in the desktop capture.
- [ ] Mobile captured, or the fallback recorded.

**Done when:** every box is ticked, or the gap is written into the spec's notes with the reason.

---

## 6. Step 4: Build the section inventory

**Purpose:** a numbered skeleton that every later part refers to (S1, S2…). It prevents skipped sections.

**Do**
1. Walk the desktop chunks top to bottom and name each visual section.
2. Map each one to its `shopify-section-…` id in DOM order. **Trust the render over section names.** On Plaims, the section id `how_to_use` holds the anti-hype image-with-text block, not a how-to.
3. Record the chunk and y-range (in chunk pixels) for each section, so QA can find it again.
4. Add the **invisible elements** found in configs: sticky ATC, cart drawer and its progress bar, popups, timers, exit intent.
5. Read the copy for each section in `copy.txt` to confirm the boundaries.

**Output:** an inventory table (`#`, id, name, chunk / y-range, type: theme section / custom liquid / app block).
**Done when:** every pixel band of the page belongs to exactly one inventory row.

---

## 7. Step 5: Write the SECTION SPEC, section by section

**Purpose:** a blueprint precise enough that the builder never needs to open the competitor page, and QA can check each line.

**Format: exactly PROMPT_1-1's block, repeated for every section** (template: `templates/SECTION_SPEC.md`):
```
SECTION: S<n> — <name>  (id: <shopify-section id>)

LAYOUT:
  — Structure (grid/flex, columns, alignment)
  — Width (full-bleed / contained / max-width)
  — Spacing (padding, margins, gaps — in px)
  — Background (color, gradient, image, pattern)

COMPONENTS:
  — Elements (icons, badges, buttons, images, text blocks, counters, progress bars, carousels, accordions, timers, video)
  — Hierarchy (what the eye hits first, second, third)
  — Interactive behavior (hover, click, scroll, accordion expand, carousel swipe, default states)

TYPOGRAPHY:
  — Font family per element (heading, body, label, badge)
  — Sizes, weights, line-heights, letter-spacing
  — Text colors (#hex per element)

VISUAL DETAILS:
  — Border radius values
  — Shadow values (box-shadow specifics)
  — Icon style (outline/filled, size, color)
  — Dividers/separators (line, spacing, none)

IMAGE POSITIONS:
  — Count, dimensions/ratios, position  → IDs from the IMAGE MAP
  — Content description (product shot, lifestyle, infographic, badge, icon)

CONVERSION ROLE:
  — Funnel job · emotional trigger · objection handled · proof deployed · action driven

MOBILE BEHAVIOR (~390px):
  — Stack direction, hidden/reordered elements, touch interactions  (observed | inferred)

ANGLE ROLE (Step Alpha, our page):
  — Angle card(s) served (V#/O#) · avatar (AV#) · objection handled (1.4) · congruence role
    (above-the-fold validation / home for a gap angle / objection handling / mechanism proof / offer / none)
```
The first seven fields are PROMPT_1-1's. ANGLE ROLE is the one field about our page; fill it from the ANGLE ARCHITECTURE (Step 6).

**How to get each value (prefer CSS truth over measuring):**
- **Scale:** `scale = desk.png width ÷ chunk width` (1440 ÷ 720 = 2). Pixels measured on a chunk × scale = CSS px. Prefix measured values with `~`.
- **Spacing:** Dawn-family themes print exact per-section padding: `.section-<id>-padding { padding-top: Xpx; padding-bottom: Ypx }`, with mobile at 0.75 ×. Grep for the section id. Page width comes from `--page-width` (e.g. `120rem` = 1200 px).
- **Type sizes:** the theme scale vars (`--font-heading-scale`, `--font-body-scale`) plus the theme's h1–h6 rules. Otherwise measure the cap height on the chunk (cap height ≈ 0.7 × font-size).
- **Colors:** pick from the screenshot and confirm against the CSS or app config. Every hex used in the spec must be visible on the page.
- **Radii and shadows:** CSS vars (`--buttons-radius`, `--media-radius`, `--text-boxes-radius`) and app style configs (Kaching `cornerRadius`, `borderRadius`).
- **Behavior:** app configs (preselected tier, sticky ATC enabled, button shows price or not), theme markup (`<details>` = accordion, closed unless `open`), a browser tool if available. If you can't determine something, write `unknown — check live` rather than guessing.

**Rules**
- Cover **every** section, including the announcement bar, header and footer. No "same as above". Repeat the values.
- Describe the competitor **as is** — the spec documents what they built. Our adaptations belong in Step 5b (ADAPTATION BLUEPRINT).
- Don't write our copy here. Quote theirs in the COPY INVENTORY.
- Keep CONVERSION ROLE concrete: name the trigger, the objection and the proof in this page's words.

**Output:** one block per inventory row, plus a "Non-obvious elements" block.
**Done when:** a builder could reproduce every section from the text alone, and each value is either measured (`~`), taken from CSS or config, or marked unknown.

---

## 7b. Step 5b: ADAPTATION BLUEPRINT (our page)

**Purpose:** define how our page will differ from the competitor's while keeping the conversion mechanics that make their page work. The builder and copywriter work from this blueprint, not from the competitor spec. The test: if an AI compared our finished page against the competitor's, it would see two completely different pages that happen to sell a similar product.

**Inputs:** the SECTION SPEC (Step 5), the FUNNEL PSYCHOLOGY and ANGLE ARCHITECTURE (Step 6), and the Step Alpha dossier (3.1 angle cards, 3.2 avatars, 3.5 language bank, 1.4 objections, 1.5 emotional landscape, 1.6 mechanism).

**Write the blueprint in five parts:**

### 5b.1 Section reordering
Map the competitor's section order to ours. The conversion flow (Attention → Interest → Desire → Action from the FUNNEL PSYCHOLOGY) stays intact, but the sections that deliver each stage can change: sections may be reordered, merged, split or replaced. For each change, state: what moves, why (which conversion mechanic it preserves), and where it lands in our flow.

Example: competitor has S4 testimonials → S5 story → S6 comparison → S7 honesty → S8 FAQ. Our blueprint might merge S5 story and S7 honesty into one section, move comparison above testimonials, and split FAQ into two: mechanism questions above the fold, objection questions below.

### 5b.2 Layout adaptation
For **every section** in our adapted page, define how the visual layout differs from the competitor's equivalent:
- Different column structures (competitor's 2-col image-left text-right → our full-width hero stack)
- Different component patterns (competitor's 3-card grid testimonials → our 2-col large quote + portrait)
- Different visual treatments (competitor's flat white bg → our accent-band alternation; competitor's contained width → our full-bleed media sections)
- Different spacing rhythm (competitor's uniform padding → our progressive density)

The builder follows these layouts, not the competitor's.

### 5b.3 Component swaps
Replace component patterns while preserving their conversion job:
- Competitor's comparison **table** → our feature **grid** (icons + short labels, no "us vs them" columns)
- Competitor's accordion **FAQ** → our tabbed FAQ or expandable cards
- Competitor's trust **badge row** → our trust **strip** or **marquee** with different iconography
- Competitor's **bundle cards** → our **stepped selector** or **slider** or **visual tier cards** with a different layout

Each swap states: COMPETITOR COMPONENT → OUR COMPONENT | CONVERSION ROLE PRESERVED | VISUAL DIFFERENCE.

### 5b.4 Visual identity
Define the visual language that makes our page feel distinct:
- **Border treatments:** rounded vs sharp corners, visible vs invisible borders, accent-colored vs neutral
- **Background patterns:** solid vs gradient vs texture vs alternating bands
- **Image treatments:** rounded corners vs sharp crop, overlay text vs clean image + separate text, full-bleed vs contained
- **Spacing rhythm:** tight vs airy, progressive density (loose at top → dense at the offer) vs uniform
- **Typography hierarchy:** our heading scale, weight progression, and color usage (does our accent appear in headings? subheadings? badges only?)
- **Section transitions:** hard cuts vs flowing shapes vs overlapping cards

These choices apply globally. The builder uses them everywhere.

### 5b.5 The blueprint table
One row per section in OUR page order (not the competitor's):

```
| OUR SECTION | CONVERSION ROLE | LAYOUT (our version) | COMPETITOR EQUIVALENT | KEY DIFFERENCES | WHAT WE KEEP (the mechanic) |
|---|---|---|---|---|---|
```

Fill this for every section from announcement bar to footer. The builder reads this table to know what to build; the copywriter reads it to know how many strings each section needs and what conversion job each one serves.

**Done when:** every conversion mechanism from the FUNNEL PSYCHOLOGY has a home in the blueprint, every HIGH angle and gap angle from the ANGLE ARCHITECTURE has a home in the adapted layout, and the blueprint table covers announcement bar → footer with no gaps. A builder could describe our page without ever seeing the competitor's.

---

## 8. Step 6: FUNNEL PSYCHOLOGY summary

**Purpose:** capture *why* the page converts, so the copy, offer, images and ads keep the mechanisms even when every word changes.

**Write these five blocks** (from PROMPT_1-1), then the arc:
1. **Offer architecture:** pricing display, bundles, anchoring, crossed-out prices, per-unit math. **Include a price-math table**: tier, quantity, price, per unit, compare-at, SAVE value, extras, and how the app computes compare-at (Kaching `includeInCompareAt: true` adds the free gift's value to compare-at, which inflates the anchor).
2. **Urgency mechanics:** timers, stock counters, "selling fast", limited-time labels. **Record absence too** ("none on page"). Don't add urgency the competitor doesn't use.
3. **Trust architecture:** guarantee terms (length, refund type, keep-the-product), certifications, badges, payment icons, review scores, endorsements, "Track your order" links, and honesty or anti-hype used as a trust device.
4. **Social proof architecture:** rating line (score + count + placement), testimonial format (photo / video / text, persona per testimonial), UGC, reviews app (count, average), and "thousands of customers" claims.
5. **Upsell architecture:** quantity breaks, gifts scaling with quantity, "MOST POPULAR" and the preselected tier, the "BEST VALUE" anchor, the free-shipping threshold relative to tier prices, cart progress bars, post-purchase offers.
6. **Narrative arc:** map the sections to Attention → Interest → Desire → Action. State the awareness stage the page assumes (Schwartz) and where the buy decision is gated, and compare it with the avatars' awareness states (dossier 1.1).

**Done when:** the copywriter could explain, for each section, which mechanism it carries, and the price math reproduces the competitor's displayed SAVE and compare-at values.

### ANGLE ARCHITECTURE (Step Alpha)
**Purpose:** the competitor sends many angles to one page, and the page drops some of them (spec 1.3). Every angle we advertise must land on a page that confirms it. This block decides which section carries which angle card, so the copy, the images and the ads line up. Read 3.1, 1.10 and 2.4 first, and the congruence insights in [19 CONGRUENCE INSIGHTS](19-step-alpha.md#congruence-insights) (spec lines 353–367).

**The ADAPTATION BLUEPRINT defines which sections carry which angles.** The architecture decides how each angle is served in OUR adapted layout, not the competitor's. The blueprint may have different section names, different component types and a different order — the angle architecture maps each card to a slot in OUR structure. Where the competitor drops an angle (LOW congruence in 1.10), our adapted layout can give it a better home.

**Do**
1. **Angle table.** One row per card in 3.1: ID, name, confidence, avatar, competitor congruence (1.10 HIGH/MED/LOW), gap angle (2.4) yes/no, and its home on our page (S#.## string or image ID).
2. **Above the fold validates the highest-confidence angle(s).** The buy box zone seen first on a phone (rating line, subtitle, bullets, first gallery image) confirms the validated card(s) with HIGH confidence, the ones most ad traffic arrives on. With two such cards, the subtitle carries one and the bullets or the first image the other. The title stays 1:1 (02 Step 6).
3. **Every HIGH angle and every congruence-gap opportunity angle gets a home.** A gap angle (the competitor's ad works, its page doesn't follow through) is where we win the traffic the competitor leaks. Its home is a slot that confirms its promise in its avatar's words: a bullet, a testimonial persona of that avatar, an FAQ question on its objection, an image-with-text block on its pain. Use the slot whose job is closest; never leave such an angle without a home.
4. **One page or angle landing pages.** Decide from the congruence insights and write the decision with one line of reason:
   - **One page with multi-angle architecture** (default): every angle above fits a slot, and the above-the-fold angles cover most of the ad traffic.
   - **Angle landing pages** when an angle's promise can't be confirmed above the fold without pushing out the main angle, and that angle gets its own ads (a HIGH validated card, or a gap angle with HIGH potential). Each landing page is a copy of the product template (`product.<slug>-<angle-id>.json`, 04 §6) with the same sections; only its above-the-fold strings, section images and section order aim at that angle. The product gallery is shared by every template (Shopify product media), so it stays the same. List each landing page with its angle card ID; the ads of that card link to it (08, 09).
5. **Objections → FAQ and objection handling.** Map each objection in 1.4 (type, competitor handling, STRENGTH) to its slot in OUR adapted layout: FAQ question, expandable card, feature grid row, testimonial or any component the blueprint assigns to objection handling. Objections the competitor handles weakly (STRENGTH 1–3) or not at all come first. Questions are written in the skeptic's own words from the objection-ready phrases (2.6 / 3.5). The blueprint decides the count and format; it doesn't have to match the competitor's FAQ count.
6. **Mechanism → the mechanism section.** The section that explains why the product works (an accordion row "How do they work?", an image-with-text block, a comparison row) carries the mechanism from 1.6: name, story and proof, at the competitor's claim strength.
7. **Customer language → copy.** For each section, list the language bank lines (3.5: hook-ready, headline-ready, objection-ready, testimony-ready) the copywriter should use.
8. Fill the ANGLE ROLE field of every section block from this table.

**Output:** the ANGLE ARCHITECTURE block in SECTION_SPEC.md (template §3b) + ANGLE ROLE in every section block.
**Advertorial landing decision:** when the competitor sends certain angles through advertorial/pre-sell pages (detected in 1.5, analyzed in α1.3), record which angle cards use the advertorial funnel and which go direct. Our adapted version follows the same funnel structure: angles that the competitor funnels through advertorials get our own adapted advertorial (A5, [22](references/22-native-ads-and-advertorials.md)); angles sent direct stay direct. The advertorial's angle card governs its content (avatar, pain, mechanism, hook). List each advertorial with its angle card ID in the landing decision table.

**Done when:** every card in 3.1 with HIGH confidence and every gap angle from 2.4 has a home or a landing page (or an advertorial when the competitor uses one for that angle), every 1.4 objection has a slot or a stated reason why not, and the landing decision is written.

---

## 9. Step 7: IMAGE MAP

**Purpose:** one table that turns every visual on the page into a production task, so nothing is forgotten and every image ends up in the right ratio.

**Columns:** `ID | Section | Position | Ratio / px | Type (static / GIF / video / icon / logo) | Content (what it shows, text on it, claims) | Source (URL → raw file in 02_competitor/media) | Plan | Ref | Angle / avatar (V#/O# · AV#, from the ANGLE ARCHITECTURE; people shown = that avatar)`

**Plans** (from the operator rules):
| Image kind | Plan | Ref |
|---|---|---|
| Product gallery image | Remake each one with our product: same idea, layout logic, text and claims. **No logo.** | 05 |
| Competitor-only image (e.g. "Replica notice: buy only from <competitor>.com") | **Skip** | 05 |
| Bundle tier thumbnails (1 / 2 / 3 units) | Build from our packshot | 05 |
| Testimonial and lifestyle photo | Kie i2i remake: same framing, different people. The copy must match the photo. | 06 |
| GIF / video | Download **raw** and keep it. Theme uses animated WebP (q≈62, method 6). | 06 |
| Icons (checks, ?, stars, chevrons) | Native SVG in the theme | 04 |
| Logo | Our wordmark | 04 |
| Payment icons | Theme native | 04 |

**ID scheme:** `P#` gallery, `B#` bundle thumbnails, `G#` gift, `T#` testimonials, `M#` section media (GIF/video), `I#` other images, `IC` icon sets.

**Done when:** every `<img>`, background image, GIF and video in the capture has a row and a plan. Ratios come from natural sizes (`p.json` width × height, `width`/`height` attributes) or are measured.

---

## 10. Step 8: COPY INVENTORY

**Purpose:** give the copywriter the complete list of strings to replace, with a length budget, so the new page has the same structure and the same weight.

**Do**
1. For each section, list **every string verbatim, in order**, with an ID and element type: `S3.04 [bullet] "Wears over your prescription glasses"`. Include the microcopy: badges, pills, button labels, gift strips, accordion titles and bodies, table labels, Yes/No cells, sticky-ATC label, cart bar text, alt-text-like labels on images (image text belongs to the IMAGE MAP).
2. **Tag** strings: `[CLAIM]` (must survive at full strength; rule 1), `[OFFER]` (prices, tiers, guarantee terms, shipping threshold), `[NUM]` (ratings, counts, percentages), `[BOLD]` (bolded phrases inside paragraphs, so emphasis is kept).
3. Give **word counts** per section and in total. Count brand-written copy separately from reviews-app content.
4. Exclude reviews-app review bodies (reviews are imported or collected separately). Record only the count and average.
5. Strip capture noise ("Couldn't load pickup availability", duplicated titles, hidden labels like "Features List").

**Done when:** the copywriter can write every string without opening the competitor page, and the word budget per section is explicit.

---

## 11. Step 9: APPS and the native-rebuild plan

**Purpose:** know which UI comes from third-party apps, because apps aren't copied with the theme and each needs a decision.

**Columns:** `App | Detected by | What it renders | Config facts (copy, colors, behavior) | Plan (rebuild natively / install the same app / operator to-do)`

**Default plans**
- **Bundle / quantity-break app** (Kaching, Bundler, Fast Bundle…): **rebuild natively** as variant-driven cards (e.g. Horizon: a custom block that drives the hidden native variant picker; the operator creates variants per quantity at the tier prices). Record the tiers, badges, preselected tier, gifts and card styles.
- **Free gifts:** an operator to-do (gift product + automatic discount, or an app). Show the gift strip natively.
- **Cart drawer extras** (progress bar, upsells): note the threshold and texts. Use a native shipping rate at the same threshold. The theme has a built-in cart drawer mockup: the "Cart drawer" section in the header group (`sections/cart-drawer-extras.liquid` + `snippets/cart-extras.liquid`), editable in the theme editor; selecting it opens the drawer: announcement bar, timer bar, free-shipping bar, price details (subtotal / discounts / shipping, labels auto-translated), badges and payment icons under the checkout button, tax note hidden. Everything is off by default: turn on and fill in the copy in the `cart_drawer` entry of `sections/header-group.json` to match the competitor's drawer, in the store language. Never fork it into a brand snippet.
- **Sticky ATC:** native if the theme has one or the builder adds a light block. Record its label and target.
- **Reviews app** (Judge.me, Loox…): an operator to-do (install + import). Build a placeholder in the same position. Static rating lines and testimonial cards are theme content. Rebuild them.
- **Popups / email capture:** note them. Don't rebuild them unless the operator asks.

**Done when:** every app-rendered element on the page has a plan, and every operator to-do is listed for DELIVERY.md.

---

## 12. Step 10: Inconsistencies, save, hand off

**Purpose:** surface contradictions once, with a default, instead of letting each agent improvise.

**Do**
1. List the contradictions on the competitor page and give each a default:
   - **Offer terms** (guarantee days, shipping threshold): harmonize to the main offer on the page and use it everywhere.
   - **Claims, ratings and counts:** keep them as written at full strength (rule 1). Don't add caveats or notes about whether they're true.
   - **Wrong-market wording** (UK words on a US page): localize to `MARKET`.
   - **Currency** shown in the screenshot vs the JSON: JSON wins.
2. **Master** saves the returned text to `PRODUCT_DIR/02_competitor/page/SECTION_SPEC.md` and links it in BRIEF.md.
3. Hand off:
   - **Copywriter:** the spec (FUNNEL PSYCHOLOGY + ANGLE ARCHITECTURE + COPY INVENTORY), §14 copy rules, BRIEF.md (brand, title, market), the dossier (3.1, 3.2, 3.5, 1.4, 1.6).
   - **Builder:** the spec (sections, non-obvious elements, APPS, landing decision) + the copy deck + BRANDING.md.
   - **Image agents:** the IMAGE MAP + ANGLE ARCHITECTURE + raw media folder + packshot + the dossier (3.1, 3.2).
   - **Visual QA:** the spec + competitor chunks.

**Done when:** SECTION_SPEC.md is saved and each downstream brief points to it.

---

## 13. Delegation: the conversion-architect brief

Launch one agent (`model: "claude-opus-4-6"`) in the background as soon as the capture files exist. The conversion architect must run on **Opus 4.6** — the adaptation requires high judgment about conversion mechanics, layout design and differentiation.

Template:

```
You are the CONVERSION ARCHITECT for a Shopify product page.
Your job has two parts: (1) map the competitor's page framework, (2) design OUR adaptation that uses
the same conversion mechanics but looks and feels completely different.
Read first:
  - <SKILL_DIR>/references/03-competitor-page-analysis.md  (Steps 4–10 AND Step 5b: ADAPTATION BLUEPRINT)
  - <SKILL_DIR>/templates/SECTION_SPEC.md                   (output format, follow it exactly)
  - <SKILL_DIR>/references/00-operator-rules.md §1 (claims)
  - <SKILL_DIR>/references/19-step-alpha.md CONGRUENCE INSIGHTS (spec lines 353–367)
Inputs (all in <PRODUCT_DIR>/02_competitor/page/):
  capture.md, capture.json, copy.txt, p.json, p.html, desk.png, d1.png…dN.png, mob.png (mobile status: <captured|blocked → infer>)
Step Alpha dossier (gate passed): <PRODUCT_DIR>/00_alpha/ALPHA_DOSSIER.md: 3.1 Angle Cards, 1.10 Funnel Congruence,
  2.4 Funnel Congruence Gaps, 3.2 Avatar Cards, 1.4 Objections, 1.6 Unique Mechanism, 2.6/3.5 Language Bank, 1.1 Avatars
Market: <MARKET>. Competitor: <COMPETITOR_URL>.

PART 1 — COMPETITOR SECTION SPEC: section inventory, one PROMPT_1-1 block per section (header to footer, nothing
skipped, px and #hex values; '~' = measured on chunks at scale <S>), non-obvious elements (check app configs for
sticky ATC, cart drawer bars, popups, timers), FUNNEL PSYCHOLOGY with a price-math table, IMAGE MAP (every image,
ratio, content, source URL, plan), COPY INVENTORY (every string verbatim, tagged [CLAIM]/[OFFER]/[NUM]/[BOLD], word
counts per section), APPS with rebuild plan, inconsistencies with defaults. Describe the competitor AS IT IS.

PART 2 — ADAPTATION BLUEPRINT (§5b): design our page that keeps every conversion mechanism but differs visually:
  - Section reordering: which sections move, merge, split or get replaced (conversion flow stays)
  - Layout adaptation: for every section, how our layout differs (different column structures, component patterns,
    visual treatments). The builder works from these layouts, not the competitor's.
  - Component swaps: replace component patterns (table → grid, accordion → tabs, etc.) while preserving
    their conversion job
  - Visual identity: our border treatments, bg patterns, image treatments, spacing rhythm, typography hierarchy
  - Blueprint table: one row per section in OUR order (OUR SECTION | CONVERSION ROLE | LAYOUT | COMPETITOR
    EQUIVALENT | KEY DIFFERENCES | WHAT WE KEEP)
  - ANGLE ARCHITECTURE: angle table, above the fold, a home for every HIGH and gap angle in OUR adapted
    layout, one page vs angle landing pages, objection map, mechanism section, language bank lines per section.
    ANGLE ROLE in every section block refers to OUR sections.
  THE TEST: if an AI compared our finished page to the competitor's, it would see two completely different pages.

Don't write our copy. Keep claims verbatim. Mark mobile lines (observed) or (inferred). Write 'unknown — check
live' rather than guessing.
Return the whole document (PART 1 + PART 2) as TEXT in your final message (don't write .md files; the master saves it).
```

The master reviews the result against §17 before saving, and sends it back with the gaps listed if sections are missing or summarized.

---

## 14. Copy rules for the copywriter (downstream)

These rules travel with the spec to the copywriter agent (Phase 3, A2). The copywriter works from the ADAPTATION BLUEPRINT (our page structure) and the Step Alpha dossier (customer intelligence), not from the competitor's copy. The copy chief reads the relevant playbook sections (`books-playbooks/*.html`) before writing every piece. **The copywriter agent must run on Opus 4.6.**

1. **Fully original wording, same persuasion job.** No title, headline, subtitle or body text may be word-for-word identical to the competitor's. Every string is written fresh using the playbooks (`books-playbooks/*.html`: Schwartz, Bencivenga, Halbert, Kennedy, Hopkins) and the Step Alpha language bank. The persuasion JOB of each section stays — the WORDS are entirely ours. Customers must recognize themselves, feel listened to and understood.
2. **Claims at full strength (rule 1).** Every `[CLAIM]` string keeps its strength, numbers and trademarks: "Rated #1 Headlight Glasses", "GlareCut Technology™", "Reduces Nighttime Glare By 85%", "4.8/5". Never soften, caveat or drop them, and never add "results may vary".
   > **Real incident (example):** the first Noxis copy turned "GlareCut Technology™" into "Polarized layer", "Rated #1 Headlight Glasses" into "Built for the drive home", and the comparison row "Glare Cut Technology" into "Polarized Amber Lens". The operator had them reverted (commit "Restore original claims in Noxis page copy").
3. **Don't invent new claims either.** Carry the competitor's. New wording you write states benefits in plain terms.
4. **Simple vocabulary, direct response.** Short sentences, contractions, everyday words ("eye doctor" over "optometrist"), the customer as subject, features as evidence, specific over general. Run the 11 pm scroll test: would a tired reader on a phone keep reading this line?
5. **Similar weight, adapted structure.** Keep total copy weight similar to the competitor's (the operator once found a 1,500-word page "big and heavy to read"). But our section structure comes from the ADAPTATION BLUEPRINT, not the competitor's — sections may have different counts, different lengths, different formats.
6. **Match the blueprint, not the competitor's shape.** The ADAPTATION BLUEPRINT defines our structure: how many bullets, how many FAQ items, how many testimonials, what format each section uses. Match that structure. The competitor's literal counts are reference only.
7. **Market language.** Spelling, idioms, places and units for `MARKET` (UK "dual carriageway" → US "Interstate"; "ring road" → "beltway"). Use the market's currency and the native typography of its language (e.g. French non-breaking spaces before `: ; ! ?`).
8. **Offer terms consistent.** One guarantee length, one shipping threshold, matching the offer, everywhere.
9. **Testimonials match their photos** (mother vs father, age, setting). Keep the persona and the objection each testimonial answers.
10. **Follow the ADAPTATION BLUEPRINT for structure and the ANGLE ARCHITECTURE for content mapping.** The blueprint says what each section is and what conversion job it does; the angle architecture says which angle card and avatar it serves. Sharpen every piece with the playbooks (Schwartz awareness/sophistication for the avatar, Bencivenga proof arsenal, Halbert word pictures, Kennedy urgency triggers, Hopkins specifics).
11. **Customer language from the Language Bank** (dossier 3.5 / 2.6). Headlines and subtitles use hook-ready and headline-ready phrases, FAQ questions and objection answers use objection-ready phrases (the skeptic's exact words), testimonials are modelled on testimony-ready phrases. Use the phrase as the customer said it, fitted to the string's length budget. Claims still come from the competitor (rules 2–3).
12. **Write each string for its section's angle.** Follow the section's ANGLE ROLE (angle card, avatar, objection). Tag every string in the copy deck with its angle card ID(s) (`S3.03 [V1]`), so QA and the ads can check congruence.
13. **PLAYBOOK MANDATORY.** The copy chief reads the relevant sections of `books-playbooks/*.html` before writing every piece. Per piece, state one line naming the angle card, the avatar, its awareness/sophistication and the playbook principle used (e.g. "V2 · AV2 problem aware, stage 4 → Schwartz: improved-mechanism headline").
14. **Step Alpha data in every string.** Every string must be informed by Step Alpha: verbatims from the language bank (3.5), pain points (1.2), dream outcomes (1.3), emotional triggers (1.5). The customer reads the page and thinks: "they get me." Strong promises backed by specific pains, specific desires, specific language the customer actually uses.

**Paraphrase examples (Plaims → Noxis, pre-adaptation era)**
> These examples predate the adaptation approach and show the MINIMUM text-level distance from the competitor. With the adaptation blueprint, our section structure and visual execution differ substantially more. The copy examples below show only the text-level difference; in the current workflow, every string is written fresh from the playbooks and language bank, not paraphrased from the competitor's wording.
| Plaims | Noxis | Note |
|---|---|---|
| Every winter, night driving gets harder. More glare, more rain, more blinding headlights. | Every winter the drive home gets harder. Brighter headlights, more rain, more of that blinding glare. | same three-beat rhythm |
| Wears over your prescription glasses | Slips right over your prescription glasses | bullet count kept (4) |
| Rated 4.8/5 by 1,356+ Customers! | Rated 4.8/5 by 1,300+ drivers | same pattern and score |
| …Dual carriageway, roadworks, standing water… | …Interstate, construction zone, every headlight bouncing off the wet road… | US localization |
| My optometrist says these do not work. Why should I believe you? | My eye doctor says these don't work. Who's right? | simpler words, shorter |
| We're Not Going to Tell You It's a Miracle | We Won't Pretend They're Magic | same anti-hype job |
| Rated #1 Headlight Glasses · GlareCut Technology™ · Glare Cut Technology | unchanged | [CLAIM], kept verbatim |
| FAQ: "Try them for 90 days…" (but the guarantee is 30 days) | "Try them for 30 days…" | offer term harmonized |

---

## 15. Worked example: the Plaims SECTION SPEC

> **Note:** This worked example predates the adaptation approach. It shows a SECTION SPEC only (Part 1).
> New runs must also produce an ADAPTATION BLUEPRINT (Part 2 — see §7b) alongside the spec.

> Real run, example only. Source: `plaims.com/products/plaims-headlight-glasses`, captured at 1440 px. Chunks are 720 px wide (scale 2). `~` = measured. Mobile capture blocked by X-Frame-Options, so mobile lines are inferred unless the operator's notes say otherwise. Theme: Dawn family (RGB-triplet CSS vars, `--page-width` about 1200 px, `--buttons-radius: 40px`, `--media-radius: 20px`). Fonts: Poppins (headings), Inter (body). About 1,050 words of brand-written copy from the rating line to the FAQ, plus about 1,000 words of Judge.me reviews (about 2,000 in total).

### Section inventory
| # | Section id (suffix) | Name | Chunk / y | Type |
|---|---|---|---|---|
| S1 | `__announcement-bar` | Announcement bar | d1 0–20 | theme |
| S2 | `__header` | Header | d1 20–68 | theme |
| S3 | `__main` | Main product (gallery + buy box) | d1 70–650 | theme + Kaching block |
| S4 | `__testimonials_RRfJdi` | What Our Customers Say | d1 680–1060 | theme |
| S5 | `__mechanism` | Image-with-text: "You Never Decided to Stop Driving at Night" | d1 1090 – d2 180 | theme |
| S6 | `__custom_liquid_X9WFbc` | Comparison: "Why Choose Us?" | d2 230–520 | custom liquid |
| S7 | `__how_to_use` (name misleading) | Image-with-text: "We're Not Going to Tell You It's a Miracle" | d2 575–865 | theme |
| S8 | `__faq` | FAQ | d2 885–1060 | theme |
| S9 | `__17893804680a74c380` | Customer Reviews (Judge.me) | d2 1100 – d3 500 | app section |
| S10 | `__footer` | Footer | d5 1050–1180 | theme |
| X1 | (Kaching config) | Sticky ATC "Choose bundle" | not in capture | app |
| X2 | (Kaching Cart config) | Cart drawer + free-shipping progress bar | not in capture | app |

### S1 — Announcement bar
```
SECTION: S1 — Announcement Bar  (id: sections--…__announcement-bar)
LAYOUT:      single centered line · full-bleed · ~40px tall (~10px padding top/bottom) · bg #FFB800
COMPONENTS:  one static text, no rotation, no marquee, no link, no close button
TYPOGRAPHY:  Inter 700 ~13px · #000000 · centered
VISUAL:      no divider, no icon
IMAGES:      none
CONVERSION:  states the free-shipping threshold ($30) just above the 1-unit price ($24.95), which seeds the Buy 2
             upgrade and preempts the shipping-cost objection. No direct action.
MOBILE:      same bar, one line at ~12–13px (inferred)
```

### S2 — Header
```
SECTION: S2 — Header  (id: sections--…__header)
LAYOUT:      3 zones: menu left · logo center · utilities right · contained (~1156px content) · ~96px tall · bg #FFFFFF · no bottom border
COMPONENTS:  menu "Home", "Contact", "Track your order" · wordmark logo "plaims" (lowercase, bold) ·
             "United States | USD $" selector with chevron · search, account, cart icons
             Eye: logo → cart. Hover: link underline (theme default).
TYPOGRAPHY:  menu Inter 400 ~14px #000000 (≈75% opacity) · selector Inter 400 ~14px
VISUAL:      outline icons ~20px black · no shadow
IMAGES:      I1 logo wordmark (~120×30)
CONVERSION:  minimal nav keeps the visitor on the page; "Track your order" signals a real store (trust)
MOBILE:      hamburger left · logo center · search + cart right (inferred, Dawn default)
```

### S3 — Main product (gallery + buy box)
```
SECTION: S3 — Hero / Buy Box  (id: template--…__main)
LAYOUT:      2 columns · gallery left ~45% (~520px) · info right ~50% (~584px) · gap ~52px · contained page width ·
             bg #FFFFFF · ~10px top padding
COMPONENTS (eye order, right column):
  1 rating row: 5 amber stars (~14px) + "Rated 4.8/5 by 1,356+ Customers!"
  2 H1 title (2 lines)
  3 subtitle paragraph (pain statement)
  4 4 bullets, each with an outline circle-check icon
  5 "BUNDLE & SAVE" label centered between two 1px hairlines
  6 3 bundle cards (Kaching, quantity breaks), radio behavior, Buy 2 PRESELECTED:
      card: radius ~18px · unselected bg rgba(255,183,0,.11) + thin light border · selected bg #FFFFFF + 2px #FFB800 border
      left: tier thumbnail ~48px (1 / 2 / 3 pairs stacked) · title "Buy N" · amber pill "SAVE $X" · subtitle "Free Shipping" (Buy 2, 3)
      right: price bold + compare-at struck through, grey
      corner badge overlapping the top border: "MOST POPULAR" (Buy 2), "BEST VALUE" (Buy 3), amber bg, small caps
      bottom gift strip full width: mini case image ~24px + "+ N FREE Glasses Case(s)" + struck gift value;
      grey (#D9D9D9-ish) when unselected, #FFB800 when selected
  7 ATC button full width "ADD TO CART" (no price shown: Kaching showTotalPriceInAddToCartButton=false)
  8 4 accordions, closed by default: "What do they actually do?" · "How do they work?" ·
    "Will they fit over my glasses?" · "Our guarantee"
  Left column: main image 1:1 + thumbnail slider (4 visible, prev/next chevrons); clicking a thumb swaps the main image
TYPOGRAPHY:  rating Inter 400 ~13px #000 · H1 Poppins 700 ~40px/1.2 #000 · subtitle Inter 400 ~16px/1.6 #000 ≈75% ·
             bullets Inter 400 ~14px #000 · BUNDLE & SAVE 700 ~12px uppercase, letter-spacing ~1px ·
             card title Poppins 600 ~20px · SAVE pill 700 ~11px #000 on #FFB800 · price 700 ~20px · compare ~13px #7B7B7B ·
             badge 700 ~11px uppercase · gift strip 700 ~12px · ATC Inter 700 ~14px uppercase, letter-spacing ~2px #000 ·
             accordion titles 700 ~14px #000
VISUAL:      gallery radius 20px · thumbs radius ~12px · ATC radius 40px (pill), ~48px tall, bg #FFB800 · no shadows ·
             accordion separators 1px #E5E5E5 · chevrons ~10px right-aligned · check icons outline ~18px black
IMAGES:      P1–P6 gallery 1:1 (1080×1080) · B1–B3 tier thumbnails ~48px 1:1 · G1 case thumbnail ~24px
CONVERSION:  the action gate. Social proof first (rating above the title), then the promise and the pain (title +
             subtitle), benefits that kill the fit objection (bullets), offer anchoring (SAVE pills, struck prices
             including gift value, gifts scaling with quantity, MOST POPULAR preselected so the default basket is 2 units),
             the CTA, then the mechanism and risk reversal in accordions (what / how / fit / 30-day refund, keep the product).
MOBILE:      gallery full width on top with swipe + thumbnails · info stacks below · cards and ATC full width ·
             sticky ATC X1 appears on scroll (inferred + Kaching config sameSizeOnMobile=true)
```

### S4 — What Our Customers Say
```
SECTION: S4 — Photo Testimonials  (id: template--…__testimonials_RRfJdi)
LAYOUT:      heading + subtitle centered · 3 equal cards in a row · contained ~1034px · gap ~16px · ~60px vertical padding · bg #FFFFFF
COMPONENTS:  H2 · subtitle · 3 cards: photo on top, then 5 stars, review text, name. No carousel arrows on desktop.
             Eye: photos (faces) → stars → names.
TYPOGRAPHY:  H2 Poppins 700 ~42px #000 · subtitle Inter 400 ~16px #000 · stars black ~14px · body Inter 400 ~13px/1.5 #000 centered ·
             name Inter 700 italic ~13px
VISUAL:      card body bg #F3F1EC (cream) · photo top corners radius ~10px · no shadow · no border
IMAGES:      T1–T3 selfies in a car at night, 1:1, ~334px: T1 man in his 50s in a cap · T2 daughter (40s) + mother (71) ·
             T3 man in his 70s
CONVERSION:  social proof by persona, each testimonial answering one objection: T1 the skeptic ("ready to send them back…
             then it rained"), T2 the gift buyer for an aging parent ("Mom's verdict"), T3 the driver who quietly gave up
             night driving and got it back. Trigger: identification, regained independence.
MOBILE:      horizontal scroll-snap row, cards ~85% wide (inferred / operator brief)
```

### S5 — Image with text: "You Never Decided to Stop Driving at Night"
```
SECTION: S5 — Problem / Reframe Story  (id: template--…__mechanism)
LAYOUT:      2 columns 50/50 · text left (vertically centered, ~72px inner padding) · media right · contained ~1156px · bg #FFFFFF
COMPONENTS:  H2 · one paragraph with 8 bolded key phrases · GIF on the right. No button.
TYPOGRAPHY:  H2 Poppins 700 ~28px/1.25 #000 · body Inter 400 ~15px/1.7 #000 ≈75% · bold phrases Inter 700 #000
VISUAL:      media radius 20px on the outer corners only (media and text panel share the inner edge) · no shadow
IMAGES:      M1 GIF 1:1 (1500×1500, displayed ~580px): driver's POV of a dark road with oncoming glare
CONVERSION:  agitation + reframe: an identity story ("You never decided…"), blame shifted from age to LED headlights
             ("It is not your age"), hope with immediacy ("something about tonight"). Objection handled: "it's just
             my age, nothing helps".
MOBILE:      stacks, media on top then text (inferred, theme default)
```

### S6 — Comparison: "Why Choose Us?"
```
SECTION: S6 — Comparison Table  (id: template--…__custom_liquid_X9WFbc)
LAYOUT:      centered heading + subtitle · 3-column table ~760px centered · ~60px vertical padding · bg #FFFFFF
             columns: labels left (~300px) · highlighted brand column (~290px) · "Others" (~120px) · 5 rows ~66px each
COMPONENTS:  H2 "Why Choose " + "Us?" (amber) · subtitle "Rated #1 Headlight Glasses" · header cells "Plaims Headlight Glasses" / "Others"
             rows: LED Headlights ✓/✕ · Sensitive Eyes ✓/✓ · Fit Over Prescription Glasses ✓/✕ · Glare Cut Technology ✓/✕ ·
             30-Day Guarantee Yes/No. Static, no interaction.
TYPOGRAPHY:  H2 Poppins 700 ~40px #000, "Us?" #FFB800 · subtitle Inter 400 ~16px #7B7B7B · header cells 700 ~14px #000 ·
             row labels 700 ~13px #000 · Yes/No 700 ~13px
VISUAL:      brand column = one rounded panel bg #FFB800, radius ~14px, extending above the header row and below the last row ·
             brand-column icons: white filled circle ~22px with a black check · Others column: thin black ✕/✓ glyph ~12px, centered ·
             no row dividers
IMAGES:      none (icons only → IC)
CONVERSION:  differentiation and claim reinforcement ("Rated #1", "Glare Cut Technology"), the guarantee as a risk-reversal row.
             The single ✓ for Others (Sensitive Eyes) makes the table believable.
MOBILE:      3 columns kept, label column narrower, ~12px text (inferred)
```

### S7 — Image with text: "We're Not Going to Tell You It's a Miracle"
```
SECTION: S7 — Anti-hype Credibility  (id: template--…__how_to_use)
LAYOUT:      mirror of S5: media left · text right · 50/50 · contained ~1156px · bg #FFFFFF
COMPONENTS:  H2 · one paragraph with 7 bolded phrases · GIF on the left
TYPOGRAPHY:  same as S5 (H2 Poppins 700 ~26–28px · body Inter ~15px/1.7 with 700 bold phrases)
VISUAL:      media radius 20px on the outer corners only
IMAGES:      M2 GIF 1:1 (1500×1500): oncoming car at night, two bright LED headlights
CONVERSION:  trust through honesty: admits the limits ("Better, not perfect"), attacks the category enemy (cheap yellow
             tints that "turn a white glare into a yellow glare"), sets expectations (fewer refunds), and offers a
             low-risk proof ("you will know inside one drive").
MOBILE:      stacks, media on top (inferred)
```

### S8 — FAQ
```
SECTION: S8 — FAQ Accordion  (id: template--…__faq)
LAYOUT:      centered H2 · narrow list ~740px centered · 5 rows ~52px · bg #FFFFFF
COMPONENTS:  "FAQ" heading · 5 accordion rows, closed by default: outline "?" circle icon left · question · chevron right
             (single vs multiple open: unknown, check live)
TYPOGRAPHY:  H2 Poppins 700 ~44px #000 · questions 700 ~14px #000 · answers Inter 400 ~14px/1.6
VISUAL:      1px #E5E5E5 separators · "?" icon outline ~16px black · chevron ~10px
IMAGES:      none
CONVERSION:  last-mile objections: authority ("My optometrist says these do not work"), safety (pedestrians in dark
             clothes), fit (over prescription glasses), category skepticism (cheap yellow tints), risk (full refund
             within 30 days, keep the case)
MOBILE:      full width with 16px gutters (inferred)
```

### S9 — Customer Reviews (Judge.me)
```
SECTION: S9 — Reviews Widget  (id: template--…__17893804680a74c380, app section)
LAYOUT:      contained ~1156px · header row: title + average left, actions right · list of reviews separated by 1px lines · pagination centered
COMPONENTS:  "Customer Reviews" · 4.7 average + stars + "68 reviews" · histogram (72% 5★, 28% 4★) · "Write a review" button ·
             filter + sort icon buttons · each review: 5 stars, avatar circle with initial, name, date, title, body ·
             pagination 1 2 3 4 … 14 with the active page in an amber circle
TYPOGRAPHY:  Inter · review title 700 ~18px · body ~14px · name 700 ~13px · date ~12px #7B7B7B
VISUAL:      stars #FFB800 ~24px · avatar bg light cream · button bg #FFB800 radius ~8px · separators 1px #E5E5E5
IMAGES:      none (text reviews)
CONVERSION:  volume and recency of social proof; unpolished customer voice reads as authentic
MOBILE:      Judge.me responsive default
NOTE:        the widget area renders late, which left a ~2,000px blank band above the footer in the capture. Don't reproduce it.
```

### S10 — Footer
```
SECTION: S10 — Footer  (id: sections--…__footer)
LAYOUT:      full-bleed bg #FFB800 · contained content · row 1: "Country/region" label + selector (left), payment icons (right) ·
             row 2: copyright + policy links · ~40px vertical padding
COMPONENTS:  selector pill "United States | USD $" with chevron · 10 payment icons · "© 2026, Plaims Powered by Shopify ·
             Privacy policy · Refund policy · Terms of service · Shipping policy · Contact information". No menus, no newsletter.
TYPOGRAPHY:  Inter 400 ~12–14px #000
VISUAL:      selector outline 1px #000, radius 40px · no dividers
IMAGES:      payment icons (theme native)
CONVERSION:  trust (payment brands, policies) with no exits or distractions
MOBILE:      stacked, centered (inferred)
```

### Non-obvious elements
```
X1 Sticky ATC (Kaching, stickyAtcEnabled=true): white bar · product photo 40px · title "{{product}}" Inter 16px ·
   button "Choose bundle" bg #FFB800, text #000 700 16px, radius 8px, padding 15px · same size on mobile.
   Appears on scroll and leads back to the bundle cards.
X2 Cart drawer (Kaching Cart): tiered promotions bar "Add {{progress_needed}} to unlock Free shipping!" → "Free shipping unlocked!",
   threshold $30 cart total (AU market: $50) · free gifts added automatically.
Not present: popups, exit intent, countdown timers, stock counters.
```

### FUNNEL PSYCHOLOGY (Plaims)
**Offer architecture.** One SKU at $24.95, sold through quantity breaks with free gifts. The compare-at includes the gift value (Kaching `includeInCompareAt: true`). The gift case is valued at about $14.95, derived from the € render: the SAVE on Buy 1 equals the gift value.

| Tier | Qty | Price | Per unit | Compare-at | SAVE pill | Extras |
|---|---|---|---|---|---|---|
| Buy 1 | 1 | $24.95 | $24.95 | $39.90 | $14.95 | + 1 free case · pays shipping (under $30) |
| Buy 2 · MOST POPULAR · preselected | 2 | $34.95 | $17.48 | $79.80 | $44.85 | + 2 free cases · Free Shipping |
| Buy 3 · BEST VALUE | 3 | $44.95 | $14.98 | $119.70 | $74.75 | + 3 free cases · Free Shipping |

**Urgency.** None on the page (no timers, no stock counters). The urgency is emotional ("something about tonight"). Don't add any.
**Trust.** 30-day guarantee, stated three times (accordion, comparison row, FAQ): full refund, "not store credit", "we do not ask for them back", "the case is yours either way". "Rated #1". Honesty as proof (S7). Payment icons, policies, "Track your order".
**Social proof.** Rating line above the title (4.8/5, 1,356+). "Thousands of customers already wear…". 3 persona photo testimonials. Judge.me list (4.7, 68 reviews, recent dates).
**Upsell.** Free-shipping threshold of $30 sits between the 1-unit and 2-unit prices. The 2-unit tier is preselected and badged MOST POPULAR. BEST VALUE anchors the 3-unit tier. Gifts scale with quantity. The cart progress bar repeats the threshold.
**Arc.** Attention: rating + title + pain subtitle → Interest: bullets + mechanism accordions → Desire: testimonials → identity story (S5) → comparison (S6) → honesty (S7) → Action: bundles sit above the fold, the FAQ removes the last objections, and the sticky ATC brings the visitor back to the bundles. The page assumes a problem-aware older driver arriving from an ad.

### ANGLE ARCHITECTURE (illustrative: Step Alpha did not exist in the Plaims run; card names are examples)
| Card | Angle | Confidence / potential | Avatar | Competitor congruence | Gap (2.4) | Home on our page |
|---|---|---|---|---|---|---|
| V1 | "It's not your age, it's LED headlights" | HIGH | AV1 older driver who quietly stopped driving at night | HIGH | no | above the fold: S3.03 subtitle, P1; S5 story |
| V2 | Cataract / astigmatism drivers | HIGH | AV2 driver with an eye condition | LOW (ads name the condition, the page never does) | yes | S3 bullet S3.04, FAQ S8 question 1, testimonial T3 persona |
| O1 | Adult child buying for an aging parent | HIGH potential | AV3 gift buyer, 40s | none | yes | testimonial T2 persona, S3 gift strip wording |

Landing decision: one page with multi-angle architecture (V2 and O1 fit existing slots; V1 already owns the fold).
Objection map: "my eye doctor says these don't work" (1.4, STRENGTH 3) → FAQ 1 in the skeptic's words · "cheap yellow tints" → S7 + comparison row.
Mechanism (1.6): GlareCut Technology™ → accordion S3.15–S3.16 + comparison row S6.08.

### IMAGE MAP (Plaims, abridged)
| ID | Section | Position | Ratio / px | Type | Content | Source | Plan |
|---|---|---|---|---|---|---|---|
| P1 | S3 | gallery 1 | 1:1 · 1080 | static infographic | glasses + arrows "Fits over prescription glasses", "Peripheral vision without glare", "Engineered for night vision clarity", Before/After night-road inset, amber banner "Includes FREE Glasses Case" | `New1.png` | remake (05) |
| P2–P5 | S3 | gallery 2–5 | 1:1 · 1080 | infographics / lifestyle | e.g. "Reduces Nighttime Glare By 85%" claim card, benefit list, woman driving at night (describe each from the raw file) | `media/` | remake each (05) |
| P6 | S3 | gallery 6 | 1:1 · 1080 | notice | "Replica Notice", buy only from plaims.com | `Replica_Notice…png` | **skip** |
| B1–B3 | S3 | bundle cards | ~48px · 1:1 | static | 1 / 2 / 3 pairs | Kaching media | from packshot (05) |
| G1 | S3 | gift strip | ~24px | static | glasses case | Kaching gift product | case image |
| T1–T3 | S4 | card tops | 1:1 · ~334px | photo | night car selfies (see S4) | testimonial image URLs | Kie i2i, new people; copy matches photo (06) |
| M1 | S5 | right | 1:1 · 1500 | GIF | driver's POV, night road glare | `iphone-camera-no-text.gif` | raw + animated WebP (06) |
| M2 | S7 | left | 1:1 · 1500 | GIF | oncoming LED headlights | `headlight-glasses-clean.gif` | raw + animated WebP (06) |
| I1 | S2 | logo | ~120×30 | wordmark | "plaims" | n/a | our wordmark (04) |
| IC | S3, S6, S8, S9 | icons | SVG | icons | circle checks, ✓/✕, "?" circles, stars, chevrons | n/a | native SVG (04) |

> In the Noxis run the operator asked to reuse the competitor's two GIFs. They were downloaded raw, kept in media/, and shipped as animated WebP (about 90% lighter).

### COPY INVENTORY (Plaims, excerpt; the real inventory lists every section)
```
S1  (6 words)
  S1.01 [bar][OFFER] "FREE Shipping on orders over $30+"
S3  (~330 words incl. accordions)
  S3.01 [rating][NUM][CLAIM] "Rated 4.8/5 by 1,356+ Customers!"
  S3.02 [h1] "Plaims Polarized Headlight Glasses"            → title 1:1 from BRANDING
  S3.03 [subtitle] "Every winter, night driving gets harder. More glare, more rain, more blinding headlights."
  S3.04 [bullet] "See the road again after dark"
  S3.05 [bullet] "Wears over your prescription glasses"
  S3.06 [bullet] "No more flinching at every oncoming car"
  S3.07 [bullet] "One size fits all"
  S3.08 [label] "BUNDLE & SAVE"
  S3.09 [tier][OFFER] "Buy 1" · pill "SAVE {{saved_total}}" · gift "+ 1 FREE Glasses Case"
  S3.10 [tier][OFFER] "Buy 2" · sub "Free Shipping" · badge "MOST POPULAR" · gift "+ 2 FREE Glasses Cases"
  S3.11 [tier][OFFER] "Buy 3" · sub "Free Shipping" · badge "BEST VALUE" · gift "+ 3 FREE Glasses Cases"
  S3.12 [button] "Add to cart"
  S3.13 [acc-title] "What do they actually do?"   S3.14 [acc-body] (~95 words, list of 3 benefits)
  S3.15 [acc-title] "How do they work?"           S3.16 [acc-body] "Amber Filters (Not a tint)…" + [CLAIM] "GlareCut Technology™…"
  S3.17 [acc-title] "Will they fit over my glasses?"  S3.18 [acc-body] (~25 words)
  S3.19 [acc-title] "Our guarantee"               S3.20 [acc-body][OFFER] "Drive in them for 30 days… we do not ask for them back."
S6  (~30 words)
  S6.01 [h2] "Why Choose " + [accent] "Us?"
  S6.02 [subtitle][CLAIM] "Rated #1 Headlight Glasses"
  S6.03 [col] "Plaims Headlight Glasses"   S6.04 [col] "Others"
  S6.05–09 [row] "LED Headlights" · "Sensitive Eyes" · "Fit Over Prescription Glasses" · [CLAIM] "Glare Cut Technology" · [OFFER] "30-Day Guarantee"
  S6.10 [cells] "Yes" / "No"
X1  [sticky] "Choose bundle"
X2  [cart] "Add {{progress_needed}} to unlock Free shipping!" · "Free shipping unlocked!"
TOTAL brand copy ≈ 1,050 words (reviews excluded)
```

### APPS (Plaims)
| App | Detected by | Renders | Config facts | Plan |
|---|---|---|---|---|
| Kaching Bundles | `kaching-bundles`, `dealBars` JSON | S3 bundle cards, X1 sticky ATC | 3 quantity-break tiers, Buy 2 preselected, badges, gifts with `includeInCompareAt`, card radius ~18–25, sticky "Choose bundle" | **Native rebuild:** variant-driven cards + gift strips. Operator creates the 1/2/3-pair variants at 24.95/34.95/44.95. |
| Kaching Cart | `kaching-cart`, `tieredPromotionsBar` | X2 cart drawer bar | free shipping at $30 (AU $50), gifts added automatically | native shipping rate at $30 · gift via automatic discount = **operator to-do** |
| Judge.me | `judgeme` / `jdgm` classes, settings JSON | S9 reviews list | 4.7 / 68 reviews, amber stars and button | **operator to-do:** install + import · placeholder in the template |

### Inconsistencies (Plaims) and defaults
- Rating line 4.8/5 by 1,356+ vs Judge.me 4.7 / 68 → keep the rating line as written (claim).
- FAQ "Try them for 90 days" vs the 30-day guarantee everywhere else → harmonize to 30 days.
- UK wording on a US page ("dual carriageway", "ring road") → localize to US.
- Screenshot prices in € vs JSON USD → USD from JSON.

---

## 16. Pitfalls

| Pitfall | Effect | Prevention |
|---|---|---|
| Prices read from the screenshot | wrong currency and amounts (€22.27 for $24.95) | prices from `p.json` + app config only |
| Most frequent hex treated as a brand color | phantom teal `#108474` (Judge.me default) | every spec color must be seen on the page |
| Payment icon colors in the palette | random reds and blues | ignore footer SVG colors |
| Mobile iframe blocked | grey ⊘ box mistaken for capture | detect it, use fallbacks a–d, mark lines (inferred) |
| Static capture misses app UI | sticky ATC / cart bar never built | grep app configs (`stickyAtc`, `tieredPromotionsBar`, popups, timers) |
| Section ids trusted over the render | wrong names, wrong order | the render decides, ids are only for mapping |
| Blank bands reproduced | huge empty gaps on our page | blank areas = unrendered widgets or window artefacts |
| "Same as above" in the spec | builder guesses, QA can't check | repeat the values in every block |
| Copy inventory without counts | copy grows ("big and heavy to read") | word count per section, ±10% budget |
| Claims softened by the copywriter | operator-mandated rewrite | `[CLAIM]` tags + §14 rule 2 |
| Spec written by a sub-agent as a file | write refused | the agent returns text, the master saves |
| An advertised angle with no home on the page | the ad's promise hits a wall (LOW congruence), visitors bounce | ANGLE ARCHITECTURE: every HIGH and gap angle has a home or a landing page |

---

## 17. Done-when checklist

### Part 1 — SECTION SPEC (competitor framework)
- [ ] Capture files present: p.json, p.html, capture.json/.md, copy.txt, desktop chunks; mobile captured or fallback recorded.
- [ ] Inventory covers announcement bar → footer, plus invisible app elements.
- [ ] Every section has all seven PROMPT_1-1 fields with px and #hex values (`~` measured, CSS/config exact, or "unknown — check live").
- [ ] FUNNEL PSYCHOLOGY has all five blocks, the arc, and a price-math table that reproduces the displayed SAVE and compare-at values.
- [ ] IMAGE MAP has every image, GIF, video, icon set and logo, with ratio, content, source and plan; competitor-only images are marked skip.
- [ ] COPY INVENTORY lists every string verbatim with tags and per-section word counts, with noise stripped.
- [ ] APPS table has a plan per app and the operator to-dos listed.
- [ ] Inconsistencies listed with defaults.

### Part 2 — ADAPTATION BLUEPRINT (our page)
- [ ] Section reordering defined: every competitor section accounted for (kept, moved, merged, split or replaced), conversion flow preserved.
- [ ] Layout adaptation written for every section: our layout differs from the competitor's (different column structures, component patterns, visual treatments).
- [ ] Component swaps specified: replaced patterns (table → grid, accordion → tabs, etc.) with conversion role preserved.
- [ ] Visual identity defined: our border treatments, bg patterns, image treatments, spacing rhythm, typography hierarchy — visually distinct from competitor.
- [ ] Blueprint table complete: one row per section in OUR order with all six columns (OUR SECTION | CONVERSION ROLE | LAYOUT | COMPETITOR EQUIVALENT | KEY DIFFERENCES | WHAT WE KEEP).
- [ ] ANGLE ARCHITECTURE done from the dossier (Alpha gate passed): above the fold validates the highest-confidence angle(s), every HIGH and gap angle has a home in OUR adapted layout, landing decision written, objection map, mechanism section; every section block has ANGLE ROLE referencing OUR sections.
- [ ] **AI test**: if you sent our blueprint and the competitor's page to an AI, it would see two completely different pages while serving the same conversion mechanics.

### Delivery
- [ ] Master saved `PRODUCT_DIR/02_competitor/page/SECTION_SPEC.md` (both parts) and briefed the copywriter (with §14), the builder (with the blueprint), the image agents and QA.
