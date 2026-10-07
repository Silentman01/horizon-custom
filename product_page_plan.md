### STEP 2 — PRODUCT PAGE

Trigger: Operator provides competitor product page
(HTML source + full-page screenshot PDF, desktop and
mobile if available) and has confirmed brand choices
from Step 1 (or provides brand direction inline).

═══════════════════════════════════
THE METHODOLOGY
═══════════════════════════════════

This step produces a complete Shopify product page by
reverse-engineering a scaling competitor's page — extracting
its conversion architecture, rebuilding it on the
operator's store with original copy and brand identity,
and elevating it with direct-response craft the competitor
doesn't have.

Two modes exist. The operator chooses before any work
begins:

  MODE A — FAITHFUL CLONE
  Pixel-close structural reproduction. Same layout, same
  section order, same spacing relationships, same visual
  hierarchy, same component types, same funnel psychology.
  The goal: if a customer saw both pages side by side, the
  structure would be indistinguishable. Only the brand
  identity, copy, and images differ.

  MODE B — INTELLIGENT CLONE
  Same conversion funnel and section architecture, but
  optimized. CRO improvements where the competitor is
  weak, spacing and hierarchy tightened, sections
  reordered if the funnel logic benefits, mobile
  experience refined. The competitor's page is the
  blueprint. The output is a better version of that
  blueprint.

In both modes, these are absolute:
  — Copy is 100% original. Written for the operator's
    brand, voice, and product. Key parts can be paraphrased.
    The persuasion ARCHITECTURE is extracted.
  — Images are placeholders. Properly sized mock elements
    (SVG placeholders, labeled gradient blocks, ratio-
    correct empty frames) at the exact positions and
    dimensions the competitor uses. Zero competitor assets.
  — Brand identity comes from the operator's Shopify store
    (auto-detected) or from explicit brand direction. The
    competitor's colors, fonts, and logo never appear.
  — The operator publishes the theme when ready.

═══════════════════════════════════
INPUTS
═══════════════════════════════════

The operator provides:
  1. Competitor page HTML (pasted or as file)
  2. Full-page screenshot PDF (desktop, + mobile if
     available) — "gofullpage" style capture
  3. Competitor URL (for live inspection if browser access
     is available)
  4. Mode selection (Faithful or Intelligent)

The following are gathered automatically from the
connected Shopify store — the operator provides NOTHING
for these:
  — Brand name, logo
  — Product data (title, price, variants, description)
  — Theme colors and fonts (active theme settings)
  — Store language, currency, market
  — Existing pages, menus, navigation

If the operator wants to OVERRIDE any auto-detected value
(use different fonts, a specific color palette from Step 1,
a particular brand voice), they state it upfront. Otherwise,
defaults come from Shopify.

═══════════════════════════════════
THE TEAM
═══════════════════════════════════

### CONVERSION ARCHITECT
Reads the competitor page at the STRUCTURAL level. Sees
past the visual surface into the persuasion skeleton:
what sections exist, in what order, what conversion job
each section performs, how the funnel flows from attention
→ interest → desire → action, where urgency is applied,
where proof is deployed, where objections are handled,
where the buy decision is gated.

Produces: the SECTION SPEC — a complete structural
blueprint of the competitor's page, section by section
from top bar to footer.

### COPYWRITER
Takes the section spec and writes every word of copy for
the operator's product page. Applies the project's
copywriting resources and competitive paraphrasing
methodology:
  — Extracts the competitor's persuasion architecture
    per section (what emotional trigger, what promise,
    what objection handled, what proof deployed)
  — Writes completely original copy that serves the SAME
    persuasion job but in the operator's voice, with the
    operator's product data, elevated by DR techniques
  — Customer as subject. Features as evidence. Specificity
    over generality. The 11pm scroll test on every line.

Produces: complete copy for every section, every heading,
every bullet, every CTA, every badge, every FAQ, every
piece of text on the page.

### FRONT-END BUILDER
Takes the section spec + copy and builds the actual Shopify
theme sections. Reconstructs the competitor's layout in
Liquid/HTML/CSS/JS on the operator's draft theme:
  — Section-by-section construction matching the spec
  — Spacing, typography, colors from the operator's brand
    (auto-detected or overridden)
  — Image placeholders at exact positions and dimensions
  — Responsive behavior matching the competitor's mobile
    experience
  — Animations and interactions matching the competitor's
    behavior (sticky elements, scroll reveals, hover
    states, accordions, carousels)
  — All components functional (add to cart, quantity
    selectors, variant pickers, accordions, timers)

Produces: complete working draft theme with all sections, built as sections blocks native to the theme.

### VISUAL QA
Opens the competitor's page and the draft theme side by
side. Inspects EVERY section at desktop and mobile widths.
Identifies every visual discrepancy — layout drift, spacing
mismatch, color deviation, typography inconsistency,
component behavioral difference, responsive breakage.

Produces: discrepancy report → corrections → re-inspection
loop until the draft is pixel-close (Mode A) or
structurally equivalent with intentional improvements
(Mode B). The loop does not end until QA passes with zero
visible discrepancies.

═══════════════════════════════════
THE PROCESS
═══════════════════════════════════

### PHASE 1 — ANALYSIS

Read the competitor's page through ALL THREE inputs
simultaneously — HTML (structure/classes/styles), screenshot
PDF (visual render/spacing/hierarchy), and live URL if
accessible (behavior/interactions/mobile).

Produce the SECTION SPEC. For each section, top to bottom:

```
SECTION: [name — e.g., "Announcement Bar", "Hero/Buy Box",
  "Benefits Grid", "How It Works", "Comparison Table",
  "Reviews Carousel", "FAQ Accordion", "Sticky ATC"]

LAYOUT:
  — Structure (grid/flex, columns, alignment)
  — Width (full-bleed / contained / max-width)
  — Spacing (padding, margins, gaps — in px)
  — Background (color, gradient, image, pattern)

COMPONENTS:
  — What elements exist (icons, badges, buttons, images,
    text blocks, counters, progress bars, carousels,
    accordions, timers, video embeds)
  — Component hierarchy (what the eye hits first, second,
    third)
  — Interactive behavior (hover, click, scroll, accordion
    expand, carousel swipe)

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
  — How many images, what dimensions/ratios, what position
  — Content description (what the image shows — product
    shot, lifestyle, infographic, badge, icon)
  — These become placeholder specs

CONVERSION ROLE:
  — What job does this section perform in the funnel?
  — What emotional trigger does it pull?
  — What objection does it handle?
  — What proof does it deploy?
  — What action does it drive?

MOBILE BEHAVIOR:
  — How does this section adapt on mobile (~390px)?
  — Stack direction, hidden elements, reordered elements,
    touch interactions
```

The spec must cover EVERY section — nothing skipped, nothing
summarized. Include non-obvious elements: sticky add-to-cart
bars, exit-intent popups, announcement marquees, floating
badges, cart drawer behavior, quantity discount UI.

Capture the FUNNEL PSYCHOLOGY as a separate summary:
  — Offer architecture (pricing display, bundles, anchoring,
    crossed-out prices, per-unit calculations)
  — Urgency mechanics (timers, stock counters, "selling fast"
    badges, limited-time labels)
  — Trust architecture (guarantees, certifications, lab
    tested badges, payment icons, review scores, doctor
    endorsements)
  — Social proof architecture (review count, star display,
    testimonial format, UGC photos, video testimonials,
    before/after)
  — Upsell architecture (bundle offers, quantity breaks,
    "most popular" highlighting, free shipping thresholds)

### PHASE 2 — COPY

Using the section spec and the competitive paraphrasing
methodology from the copywriting skill:

For each section:
  1. Extract the competitor's persuasion architecture
     (what they're doing and why it converts)
  2. Write original copy that performs the same conversion
     job in the operator's brand voice
  3. Elevate with DR techniques the competitor missed:
     — Their headline targets the wrong awareness state?
       Fix it.
     — Their benefits section lists features without
       benefit translation? Apply "so that..." bridge.
     — Their social proof is generic? Add specificity.
     — Their comparison table compares materials instead
       of experiences? Reorient.
     — Their FAQ answers informational questions instead
       of preempting purchase objections? Restructure.
     — Their CTA is generic "Add to Cart"? Add micro-copy
       reassurance.
  4. Apply project copywriting resources throughout —
     Schwartz's awareness states, Bencivenga's persuasion
     equation, Hopkins' specificity, the full toolkit.

Copy must be in the store's language (auto-detected from
Shopify, or operator-specified). Health/supplement products
use compliant language automatically ("supports," "helps,"
"contributes to" — never "cures" or "treats").

### PHASE 3 — BUILD

Duplicate the live theme → "[Brand] — clone (draft)".

Build every section from the spec on the draft theme:
  — Liquid sections with schema settings for future
    merchant editing
  — CSS matching the spec's spacing, typography, colors,
    shadows, radii (using the operator's brand values,
    not the competitor's)
  — JS for interactive components (accordions, carousels,
    timers, sticky bars, quantity selectors)
  — Image placeholders: properly sized SVG or gradient
    blocks with descriptive labels at each image position,
    matching the competitor's exact dimensions and ratios
  — Product data wired: real product title, price, variants,
    images from the operator's Shopify product
  — All components functional: add to cart works, variant
    selection works, quantity updates, cart drawer triggers

Push to GitHub when the build is complete.

### PHASE 4 — VISUAL VERIFICATION

This phase is a LOOP, not a checklist.

  1. Open side by side: competitor page (A) and draft
     preview (B)
  2. For each section, at DESKTOP width:
     — Compare layout, spacing, alignment
     — Compare typography (family, size, weight, color)
     — Compare colors (#hex accuracy)
     — Compare component behavior
     — Compare image placeholder positions/dimensions
  3. Same comparison at MOBILE width (~390px)
  4. Log every discrepancy in a table:
     ```
     SECTION        │ ISSUE              │ FIX
     ───────────────┼────────────────────┼──────
     Hero           │ Padding 40px→24px  │ fixed
     Buy Box        │ Button radius 8→12 │ fixed
     ```
  5. Apply fixes to the draft
  6. RE-INSPECT. Compare again. New discrepancies → fix →
     re-inspect. Loop until the table is empty.

The loop ends when:
  — Mode A: Zero visible structural discrepancies at both
    desktop and mobile. Pixel-close.
  — Mode B: Zero unintentional discrepancies. Intentional
    improvements are logged and justified.

### PHASE 5 — DELIVERY

Output:
  — Draft theme preview link
  — Section-by-section summary (what was built, any notes)
  — Image placeholder map (which placeholders need which
    real images, with dimensions and content descriptions)
  — Discrepancy log (final — should be empty or
    intentional-only)
  — GitHub push confirmation
  — If operator requested product import → confirmation
    that product description HTML was pushed to the
    Shopify product

The operator reviews the preview and publishes when ready.
The draft is never auto-published.