# 02 — Branding (Phase 2, ends at the GATE)

This step turns the captured competitor page into the decisions the whole launch depends on: brand name, palette, fonts and shape, and product title. In a product test almost all of it is copied 1:1 from what already sells. The one real creative bet is the **brand name**, and the operator makes that choice.

Read `00-operator-rules.md` §1–3 first. This file covers how to do the step.

## Contents
1. When this runs, inputs, outputs
2. Principles, and how they override PROMPT_1-1
3. Step 1: Load the capture
4. Step 2: Competitor snapshot
5. Step 3: Brand names
6. Step 4: Palette 1:1
7. Step 5: Typography and shape 1:1
8. Step 6: Product title 1:1
9. Step 7: Write BRANDING.md and present the gate
10. Step 8: Iterate on feedback
11. Step 9: After approval (record, rename, branch)
12. Delegation (optional brainstorm agent)
13. Worked example: Noxis (cloning plaims.com)
14. Done-when checklist

---

## 1. When this runs, inputs, outputs

**When:** after Phase 1 capture has landed (`02_competitor/page/capture.md`, `p.json`, screenshots). If capture hasn't run yet, run `scripts/capture_page.py` yourself first; it takes under a minute. Never brand from memory or from the URL alone, because the palette, price and positioning must come from the real page.

**Inputs**
- `COMPETITOR_URL` (one or more; the first is the page being cloned, "#1")
- `MARKET` (country, language, currency), from BRIEF.md. Ask if it's missing. Names and titles depend on it.
- `PRODUCT_DIR/02_competitor/page/`: `p.json`, `p.html`, `capture.json`, `capture.md`, desktop screenshot chunks

**Outputs**
- `PRODUCT_DIR/01_branding/BRANDING.md` (built from `templates/BRANDING.md`)
- A short gate message to the operator, then **STOP**
- After approval: BRIEF.md decisions, PRODUCT_DIR renamed to the brand, and the git branch `BRAND_SLUG`

**Skip and stop rules**
| Prompt says | Do |
|---|---|
| Brand name already given ("brand is Noxis") | Skip Step 3 and the gate. Still do Steps 2 and 4–6, record them, and continue straight into Phase 3. |
| "start with branding, wait for validation" | Stop at the gate even though other streams could proceed. |
| "go all the way" with no brand given | Still stop at the gate. It's the one planned stop in the whole run. |
| Operator proposes their own name | Accept it. Check silently for a clash with a big existing brand or a bad meaning in the market language, and flag only a real problem, in one line. |

**What may run before the gate:** capture, media download, Brandsearch pulls and ranking, and the SECTION SPEC (it describes the competitor and doesn't need our brand). **What must wait:** anything that prints our brand: copy, images, ads, theme edits, the git branch.

---

## 2. Principles, and how they override PROMPT_1-1

PROMPT_1-1 Step 1 asks for 4 palette variations (MIRROR/SHIFT/CONTRAST/WILDCARD), 5 paraphrased titles, names that "work as a domain", names "easy to say in French AND English", and in Step 2 it says "the competitor's colors, fonts, and logo never appear". The operator then corrected this for product tests:

> "for product titles don't overthink it, just take what works already 1:1, no need to reinvent the wheel when testing a product. we upgrade later on. same for color palette"
>
> "ignore domain name, we can find ways like my[name] or try[name].com, don't reject based on domain name"
>
> "we want to run in US"

So the defaults are:

1. **Test 1:1, upgrade later.** Palette = the competitor's exact hex codes and roles. Fonts and radii are the same. Title = the competitor's title pattern with our brand. **Why:** a test answers one question ("does this product sell with our page and ads?"). Changing the palette or the title adds variables and costs time for no learning. Upgrades come after the product is proven.
2. **The PROMPT_1-1 variations become optional.** The 4 palette variations and 5 title candidates go in an "Upgrade options" section, and only when the operator asks for them or the prompt explicitly requests the full Step 1 variations. Never put them in the default gate message.
3. **Domains are never a filter.** Read "works as a domain" as "could carry a my-/try-/get- prefix", which is always true. Don't check availability, don't mention it, and don't drop a name because of it.
4. **Market language, not French + English.** Names must be pronounceable one way by a native speaker of `MARKET`'s language. If the operator works in another language, also check that they can say it, but the customer is who matters.
5. **Be opinionated.** Star the top 3 and give one line each. The operator wants to pick, not read essays.
6. **The name is the only creative bet,** so spend the thinking there and copy everything else.

---

## 3. Step 1: Load the capture

**Purpose:** work from facts, not impressions.
**Do**
1. Read `capture.md` end to end (summary of copy, colors, fonts, apps, media).
2. Read `p.json` (title, vendor, handle, variants, `price`, `compare_at_price`, `price_currency`, images).
3. Open the first two desktop screenshot chunks (header + buy box) and the chunks that hold the comparison table and footer. These are where the brand colors show.
4. Read `MARKET` from BRIEF.md.

**Output:** nothing saved yet. You know what the page looks like and what it sells for.
**Done when:** you can state the competitor's name, title, price, main CTA color and heading font without guessing.

---

## 4. Step 2: Competitor snapshot

**Purpose:** give the operator one table to scan in ten seconds, and record the facts that Steps 4–6 copy.

**Do**, for each competitor URL (#1 first):
1. **Brand:** `vendor` in `p.json`, the logo alt text, or `og:site_name`.
2. **Title:** `product.title` in `p.json`, verbatim.
3. **Price:** take it from `p.json` (`variants[].price` + `price_currency`; a `compare_at_price` of `0.00` means there isn't one) and from the bundle app config for tiers (Kaching `dealBars`: `title`, `quantity`, `discountType`/`discountValue`, `badgeText`, `freeGifts`, `preselectedDealBarId`). Write it as `24.95 (×1) / 34.95 (×2) / 44.95 (×3)`.
   **Never read prices off the screenshot.** Shopify Markets geolocates the capture machine and renders local currency. The Plaims capture from a French IP showed €22.27 for a $24.95 product.
4. **Palette:** take the candidate hex codes from `capture.json`, then **verify each one on the screenshot** and give it a role. Pitfalls:
   - **App defaults pollute frequency counts.** On Plaims, `#108474` (teal) was the most frequent hex in the HTML (26 hits). It's Judge.me's default brand color inside its settings JSON and appears nowhere on the rendered page. Only count colors you can see.
   - **Payment icon SVGs** add `#EB001B`, `#F79E1B`, `#FF5F00` (Mastercard) and the Visa and Amex blues. Ignore them.
   - **Dawn-family themes store colors as RGB triplets** (`--color-shadow: 14,27,77` → `#0E1B4D`). **Kaching stores colors as objects** (`{"red":255,"green":184,"blue":0}` → `#FFB800`). Convert both to hex.
   - **Near-duplicates** (theme `#FFB800` vs an app's `rgb(255,178,0)`): use the theme value and mention the app value only if it's visible.
   - Roles to fill: primary CTA / button, announcement and footer background, text, page background, secondary or deep accent, card tint, borders and dividers, muted text.
5. **Typography:** `--font-heading-family` / `--font-body-family` CSS vars, `@font-face`, Google Fonts links. Note the weight used for the title (usually 700).
6. **Shape:** `--buttons-radius`, `--media-radius`, `--text-boxes-radius`, card radius. For example, `40px` buttons means pill shaped.
7. **Visual tone:** 3–5 words ("clean white, amber accents, photo-led, no gradients").
8. **Positioning angle:** one sentence answering these questions: *Who is the customer? What pain do they live with? What do they blame? What does the brand blame instead? Is the tone hype or anti-hype?* Read the title, subtitle, bullets, the long-form image-with-text sections and the FAQ, which together show the angle most clearly.

**Output:** the snapshot table (PROMPT_1-1 format) plus a details block (tiers, verified palette with roles, fonts, radii, tone, positioning, apps seen).

```
COMPETITOR │ PRICE                  │ PALETTE                  │ POSITIONING
───────────┼────────────────────────┼──────────────────────────┼────────────────────────────
Plaims     │ $24.95 / 34.95 / 44.95 │ #FFB800 #000000 #FFFFFF  │ Honest anti-hype fix for ...
```

**Done when:** every hex in the palette has been seen on a screenshot and has a role, and the prices come from JSON in the competitor's store currency, with `MARKET` currency noted if it differs.

---

## 5. Step 3: Brand names

**Purpose:** give the operator 7–10 names they would actually put on a box, with the top 3 starred.

**Why this is hard:** the obvious move is a descriptive compound (Clearway, Glareguard, Nightpilot). Those read like features, not brands, and customers don't say them in the possessive. In the real run the operator rejected three rounds before choosing "Noxis". The test that unlocked it was the operator's own line:

> "think like a customer, they would say 'let me get my plaims glasses'"

**Do**
1. **Study the competitor name's mechanics.** For example, Plaims is invented, one word, short, brand-sounding, not a description, and said in the possessive ("my Plaims glasses").
2. **Generate 30–40 candidates internally** from several patterns:
   - Latin or Greek root tied to the benefit, cut short: *nox* (night) → Noxis; *lumen* → Lumes; *amber* → Ambies
   - Pure coinages with soft consonant-vowel rhythm: Kivos, Velts, Brevs
   - Truncated words with a brand ending (-is, -o, -a, -ex, -ix, -s): Glims (glimpse), Haloz
3. **Filter by the checklist.** Every name shown must pass all of these:
   - [ ] Invented or near-invented. One word. **2 syllables preferred** (3 max), roughly 4–6 letters.
   - [ ] Brand-like, not descriptive. No compounds that describe the product or benefit (Clearway, Glareguard, Nightpilot, Roadsight, Lanelight, Highbeam) and no plain dictionary words (Lumen, Nightly, Brightline, Halo Drive).
   - [ ] **Possessive test:** "let me get my ___ glasses" (use the product noun) sounds natural when said aloud by the target customer.
   - [ ] One obvious pronunciation in the `MARKET` language, spelled how it sounds after hearing it once.
   - [ ] Not derivative of the competitor (no Plaimz, Glaims, Claims) and not an existing big brand in any category (Lumix, Optiq-style optical brands).
   - [ ] No bad meaning or slang in the market language. Not a negative symptom word for the category (for example "halo" is a glare symptom, so it's weak for glare glasses).
   - [ ] Credible in the category, so it could be printed on the box and the packshot.
   - [ ] **Domain availability not checked and not mentioned.**
4. **Rank and present 7–10.** Star the top 3. Give each name one line of rationale **that includes the possessive sentence**.
5. Keep a **Rejected** list in BRANDING.md across rounds so no name comes back.

**Output (format)**
| # | Name | Syll. | Say it | Why |
|---|---|---|---|---|
| ★1 | Noxis | 2 | "let me get my Noxis glasses" | from *nox* (night), crisp, brand-like, owns the night-driving idea without describing it |

**Done when:** 7–10 names pass the checklist, 3 are starred, and every rationale includes the possessive sentence.

### Anti-patterns from the real run (example)
| Round | Names shown | Operator reaction | Lesson |
|---|---|---|---|
| 1 | Nocta, Clearway, Ambrio, Nightline, Duskline, Lumeo, Veyra, Ambra (pre-filtered by domain availability) | "ignore domain name… my[name] or try[name].com, don't reject based on domain name" + "we want to run in US" | Never filter by domain. Confirm `MARKET` before naming. |
| 2 | Clearway, Highbeam, Nightpilot, Roadsight, Duskline, Glareguard, Lanelight, Ambrix | "do brand names again" | The whole set was descriptive. Change the *pattern*, not just the words. |
| 3 | Vizor, Lumen, Nightly, Glarex, Brightline, Optiq, Roadvue, Halo Drive | "no. something like them, think like a customer, they would say 'let me get my plaims glasses'" | Dictionary words and feature names fail the possessive test. Mirror the competitor's *kind* of name. |
| 4 | Glims, Lumes, **Noxis**, Velts, Ambies, Brevs, Kivos, Haloz | Chose **Noxis** | Invented, one word, 2 syllables, brand-like, passes "let me get my Noxis glasses". |

---

## 6. Step 4: Palette 1:1

**Purpose:** reuse the color system that already converts, so the test isolates the product and the page.
**Do**
1. Copy the competitor's **exact hex codes**, with the same roles, from the verified snapshot palette.
2. Add the theme target for each role, so the builder (04) can apply it without re-deciding:
   - **Horizon:** `config/settings_data.json` → `current.color_palette` {`background`, `foreground`, `color1`, `color2`, `color3`}, `palette_primary_button_*`, `badge_sale_background_color`. Announcement `background_color` lives in the header group.
   - **Dawn and similar:** `color_schemes` → scheme-N {`background`, `text`, `button`, `button_label`, `secondary_button_label`, `shadow`}.
   - Section-level colors (card tints, testimonial card body, comparison highlight) go to section or block settings. List them here so they aren't lost.
3. List the **excluded colors** with the reason: app defaults, payment icons, colors not visible on the page.

**Optional: upgrade variations (only when asked; never in the default gate).** These are the PROMPT_1-1 variations, each 2–3 hex codes with named roles:
- **MIRROR:** same hue family as the #1 competitor
- **SHIFT:** same spectrum, different hue
- **CONTRAST:** different spectrum entirely
- **WILDCARD:** your creative call

Label them "for a later upgrade, not for the test".

**Output:** a palette table (role, hex, where it appears on the competitor page, theme target) and an excluded list.
**Done when:** every hex matches the competitor exactly (no "slightly warmer" versions) and every role has a theme target.

---

## 7. Step 5: Typography and shape 1:1

**Purpose:** the same reasoning as the palette: copy, don't redesign.
**Do**
1. Use the same heading and body fonts. Check that they're in the Shopify font library (handles like `poppins_n7`, `inter_n4`). If one isn't, pick the closest library font and say so in one line.
2. Use the same weights (title 700 and so on).
3. Use the same radii: buttons, media, cards, inputs.

**Output:** fonts with Shopify handles, plus radii.
**Done when:** the builder can set the theme typography and shape without opening the competitor page.

---

## 8. Step 6: Product title 1:1

**Purpose:** reuse a title already tuned for search and ads.
**Do**
1. Take the #1 competitor's `product.title` and **swap only the brand**: "Plaims Polarized Headlight Glasses" → "Noxis Polarized Headlight Glasses".
2. Keep every descriptor and the word order. Descriptors like "Polarized" are claims, and they stay (rule 1).
3. Mirror the pattern. If their brand is in the title, put ours in the same position. If it isn't, keep their title verbatim. If the title contains a competitor-owned line name ("Plaims Max"), swap it for ours ("Noxis Max").
4. Mirror the handle pattern: `plaims-headlight-glasses` → `noxis-headlight-glasses`.
5. **Optional (only when asked):** 5 title candidates that paraphrase the structure, top 2 starred, under "Upgrade options".

**Output:** the title line and the handle.
**Done when:** the title differs from the competitor's only by the brand token(s).

---

## 9. Step 7: Write BRANDING.md and present the gate

**Purpose:** let the operator decide in one read.
**Do**
1. Fill `templates/BRANDING.md` → `PRODUCT_DIR/01_branding/BRANDING.md`. Before the brand exists, PRODUCT_DIR is `PRODUCTS_ROOT/_<competitor-slug>`.
2. Send the gate message. It contains only tables and picks, and no process narration:

```
Branding ready for validation: <path to BRANDING.md>

<snapshot table>

Brand names (★ = my picks)
<names table, 7–10 rows>

Palette (1:1 with <competitor>): #FFB800 CTA/bars · #000000 text · #FFFFFF bg · #0E1B4D deep accent · #E5E5E5 lines
Fonts: Poppins 700 / Inter · pill buttons (40px)
Title (1:1): Noxis Polarized Headlight Glasses

Pick a name (or say "more names"). Palette and title are 1:1 for the test; say if you want variations.
```

3. **STOP.** Don't create the branch, edit theme files, write copy or generate images. You may keep running the brand-independent streams (capture, media, Brandsearch, ranking, SECTION SPEC).

**Done when:** BRANDING.md is saved, the message is sent, and you're waiting.

---

## 10. Step 8: Iterate on feedback

**Purpose:** converge in as few rounds as possible.
**Do**
1. **Read the reaction as a direction, not only as a rejection.** Map it to a change of *pattern*:

| Operator says | Change |
|---|---|
| "ignore domain name" | Drop all domain reasoning. Restore names you filtered out for domains if they were good. |
| "we want to run in US" / another market | Update `MARKET` in BRIEF.md, then re-check pronunciation and title words in that language. |
| "do brand names again" (no detail) | The whole set missed. Switch pattern (descriptive → invented), not just the words. |
| "think like a customer… my plaims glasses" | Invented, short, possessive-friendly, shaped like the competitor's name. |
| "I like X but…" | Generate siblings of X (same root, rhythm and ending). |

2. Each round, show a **fresh 7–10** in the pattern the operator signalled. Never re-show a rejected name unless the operator liked it. Add the rejected names to BRANDING.md.
3. Keep palette and title 1:1 unless the operator raises them.

**Done when:** the operator names a brand.

---

## 11. Step 9: After approval (record, rename, branch)

**Purpose:** lock the decisions so every downstream agent reads the same truth.
**Do**
1. **BRIEF.md:** `BRAND`, `BRAND_SLUG` (lowercase, e.g. `noxis`), CSS/file prefix (`noxis-` or `nx-`), palette, fonts, radii, title, handle, `MODE`, `MARKET`.
2. **BRANDING.md:** set the status to VALIDATED with the date, and fill the Decisions section.
3. **Rename PRODUCT_DIR** `_<competitor-slug>` → `BRAND`. Actually move it (don't copy), then verify the old folder is gone.
4. **Git branch** (details in `01-intake-and-setup.md` §git and `tools-shopify-cli-and-git.md`): working tree clean → `git checkout main` → `git pull` → `git checkout -b <BRAND_SLUG>`. The operator's instruction was: "make a new branch named after brand name and work on that new branch". Never branch from another brand's branch.
5. **Logo set:** next to the logo and the white logo (`01_branding/logo/<slug>-logo(.svg/.png)`, `<slug>-logo-white(...)`, transparent PNG), make the square social logos and the favicon: `python -I scripts/brand_icons.py <logo.png> <logo-white.png> <brand_hex> 01_branding/logo <slug>` → `<slug>-social-square.png` (white logo on the brand color, 1080×1080), `<slug>-social-square-light.png` (dark on white), `<slug>-favicon.png` (512, first letter of the wordmark on a rounded brand-color square) + `.ico`. Check them on a contact sheet; use `--glyph N` if the first glyph is not a clean letter. The operator uploads the favicon in Theme settings > Logo and favicon and the square logo on the social accounts.
6. Unblock the Phase 3 streams (copy, build, images, ads).

**Done when:** BRIEF.md has every decision, the folder carries the brand name, and `git branch --show-current` prints `BRAND_SLUG`.

---

## 12. Delegation (optional brainstorm agent)

Usually the master does branding alone, because it's short and taste matters. Use a brainstorm agent only if a round fails twice:
- Give it the snapshot, the checklist from Step 3, the Rejected list, `MARKET`, and the operator's exact words.
- Ask for 30 candidates, each marked pass or fail per checklist item, **returned as text** (sub-agents may be blocked from writing .md files).
- The master picks the final 7–10 and the stars.

---

## 13. Worked example: Noxis (cloning plaims.com)

> Real run, example only. Competitor: `https://plaims.com/products/plaims-headlight-glasses`. Market: United States, English, USD.

### Snapshot
```
COMPETITOR │ PRICE                      │ PALETTE                          │ POSITIONING
───────────┼────────────────────────────┼──────────────────────────────────┼──────────────────────────────────────────
Plaims     │ $24.95 ×1 / 34.95 ×2 /     │ #FFB800 #000000 #FFFFFF #0E1B4D  │ Honest, anti-hype fix for older drivers who
           │ 44.95 ×3 (+ free cases)    │                                  │ quietly stopped driving at night: blames
           │                            │                                  │ LED headlights, not age; fits over glasses.
```
Details:
- **Product:** one variant at $24.95 (no compare-at). Bundles come from Kaching: Buy 1 / Buy 2 "MOST POPULAR" (preselected, free shipping) / Buy 3 "BEST VALUE", each with "+ N FREE Glasses Case(s)".
- **Fonts:** Poppins 700 headings, Inter body. **Radii:** buttons 40px (pill), media 20px.
- **Tone:** clean white page, amber accents, photo and GIF led, plain-spoken copy.
- **Positioning:** "It is not your age. Headlights changed, your eyes did not." The page sells an honest, modest fix ("Better, not perfect"), not a miracle.
- **Apps:** Kaching Bundles + Kaching Cart, Judge.me reviews.

### Palette 1:1 (what went into the theme)
| Role | Hex | Seen on Plaims | Horizon target |
|---|---|---|---|
| CTA / announcement / footer / comparison highlight / stars | `#FFB800` | ATC pill, top bar, footer, "Plaims" column | `color1`, `palette_primary_button_background`, announcement `background_color` |
| Text | `#000000` | headings, body, button label | `foreground`, `palette_primary_button_text` |
| Background | `#FFFFFF` | page | `background` |
| Deep accent | `#0E1B4D` (navy, stored as `14,27,77`) | color-scheme shadow/accent | `color2` |
| Lines / dividers | `#E5E5E5` | accordion and FAQ separators | `color3` |
| Bundle card tint | `rgba(255,183,0,.11)` | unselected bundle cards | block setting |
| Testimonial card body | `#F3F1EC` (cream) | "What Our Customers Say" cards | section setting |
| Muted text | `#7B7B7B` | grey subtitles | section setting |
| **Excluded** | `#108474` teal (most frequent hex) | Judge.me default color in its settings JSON, not visible on the page | none |
| **Excluded** | `#EB001B` `#F79E1B` `#FF5F00` … | payment icons | none |

> The first snapshot in the real run listed "teal #108474 accents". On visual verification it turned out to be app noise, and the theme never used it. That's why Step 2 requires seeing every color.

### Names: final round (stars illustrative; the operator chose Noxis)
| # | Name | Syll. | Say it | Why |
|---|---|---|---|---|
| ★1 | **Noxis** | 2 | "let me get my Noxis glasses" | *nox* = night. Crisp, brand-like, owns night driving without describing it. **Chosen.** |
| ★2 | Ambies | 2 | "let me get my Ambies" | From amber (the lens color). Friendly, works as a nickname for the product. |
| ★3 | Kivos | 2 | "let me get my Kivos glasses" | Pure coinage, hard consonants, no baggage, easy to spell. |
| 4 | Glims | 1 | "my Glims glasses" | From glimpse. Same short shape as Plaims, but only 1 syllable. |
| 5 | Lumes | 1 | "my Lumes" | From lumen. Soft, but close to a dictionary word. |
| 6 | Velts | 1 | "my Velts glasses" | Coinage. Sounds like apparel. |
| 7 | Brevs | 1 | "my Brevs" | Coinage. Short, slightly harsh. |
| 8 | Haloz | 2 | "my Haloz glasses" | Memorable, but "halo" is a glare symptom (negative cue). |

### Title 1:1
`Plaims Polarized Headlight Glasses` → **`Noxis Polarized Headlight Glasses`** (handle pattern `noxis-headlight-glasses`). The operator rejected paraphrased titles ("just take what works already 1:1").

### Gate and after
- Operator: "start with branding, wait for manual validation". Stopped with the tables.
- After the choice: "make a new branch named after brand name and work on that new branch". Created branch `noxis` from clean `main`, set `BRAND_SLUG=noxis` and the CSS prefix `noxis-`.

---

## 14. Done-when checklist
- [ ] Snapshot built from `p.json` + capture. Prices come from JSON, not the screenshot.
- [ ] Every palette hex was seen on a screenshot and has a role and a theme target. App and payment colors are excluded.
- [ ] Fonts (with Shopify handles) and radii recorded.
- [ ] 7–10 names pass the checklist, the top 3 are starred, and each has a possessive sentence. Domains were not considered.
- [ ] Title = the competitor's title with the brand swapped. The handle mirrors theirs.
- [ ] Upgrade variations appear only if they were asked for.
- [ ] BRANDING.md saved. Gate message sent. **Stopped** (unless the prompt fixed the brand).
- [ ] After approval: BRIEF.md updated, PRODUCT_DIR renamed (moved), branch `BRAND_SLUG` created from clean `main`.
- [ ] Logo set complete: logo, white logo, square social logos (brand color + light), favicon PNG + ICO.
