# SECTION SPEC — {{COMPETITOR_NAME}} · {{product}} → {{BRAND or "pending"}}

<!-- How to fill this: references/03-competitor-page-analysis.md, Steps 4–10. Worked example: §15 there (Plaims).
     Written by the conversion-architect agent and RETURNED AS TEXT; the master saves it to
     PRODUCT_DIR/02_competitor/page/SECTION_SPEC.md. Describe the competitor AS IS (Mode A).
     '~' = measured on screenshot chunks × scale · exact values from CSS/app config · 'unknown — check live' if unsure.
     Never write "same as above": repeat the values. Remove these comments when done. -->

| Meta | Value |
|---|---|
| URL | {{COMPETITOR_URL}} |
| Captured | {{YYYY-MM-DD}} · desktop {{1440}} px · chunk scale {{2}} |
| Mobile capture | {{captured / blocked (X-Frame-Options) → fallback a/b/c/d}} |
| MODE | {{A — faithful clone}} |
| Theme family (competitor) | {{Dawn-family / custom / …}} · page width {{px}} |
| Fonts | heading {{…}} · body {{…}} |
| Currency | JSON {{USD}} · screenshot {{€ (geo)}} → use JSON |
| Word count | brand copy ≈ {{N}} · reviews-app ≈ {{N}} |
| Capture files | p.json, p.html, capture.json/.md, copy.txt, desk.png, d1–d{{N}}.png, mob.png |

---

## 0. Section inventory

| # | Section id (suffix) | Name | Chunk / y-range | Type (theme / custom liquid / app) |
|---|---|---|---|---|
| S1 | `__{{announcement-bar}}` | {{Announcement bar}} | d1 {{0–20}} | theme |
| S2 | `__{{header}}` | {{Header}} | {{…}} | theme |
| S3 | `__{{main}}` | {{Main product / buy box}} | {{…}} | {{theme + app block}} |
| S… | {{…}} | {{…}} | {{…}} | {{…}} |
| S{{n}} | `__{{footer}}` | {{Footer}} | {{…}} | theme |
| X1 | ({{app}} config) | {{Sticky ATC / cart bar / popup}} | not in capture | app |

---

## 1. Sections

<!-- Repeat this block for EVERY inventory row, top to bottom. -->

### S{{n}} — {{name}}
```
SECTION: S{{n}} — {{name}}  (id: {{shopify-section id}})

LAYOUT:
  — Structure: {{grid/flex, columns + widths, alignment}}
  — Width: {{full-bleed / contained ~Npx / max-width}}
  — Spacing: {{padding top/bottom px · gaps px · margins}}
  — Background: {{#hex / gradient / image}}

COMPONENTS:
  — Elements: {{icons, badges, buttons, images, text blocks, counters, progress bars, carousels, accordions, timers, video}}
  — Hierarchy: 1 {{…}} → 2 {{…}} → 3 {{…}}
  — Interactive: {{hover, click, swipe, accordion default state, preselected option, sticky}}

TYPOGRAPHY:
  — {{element}}: {{family}} {{weight}} ~{{size}}px/{{line-height}} · letter-spacing {{…}} · #{{hex}}
  — {{element}}: …

VISUAL DETAILS:
  — Radius: {{px per element}}
  — Shadow: {{box-shadow or none}}
  — Icons: {{outline/filled · size · #hex}}
  — Dividers: {{1px #hex / none}}

IMAGE POSITIONS:
  — {{IDs from IMAGE MAP}}: {{count · ratio · displayed px · position}}
  — Content: {{what each shows}}

CONVERSION ROLE:
  — Funnel job: {{…}}
  — Emotional trigger: {{…}}
  — Objection handled: {{…}}
  — Proof deployed: {{…}}
  — Action driven: {{…}}

MOBILE BEHAVIOR (~390px):  ({{observed | inferred}})
  — {{stack direction · hidden/reordered elements · carousel/scroll · touch interactions}}
```

---

## 2. Non-obvious elements

```
X1 {{Sticky ATC}}: {{source (app config key) · look · label · target · mobile}}
X2 {{Cart drawer / progress bar}}: {{texts · threshold · gifts}}
X3 {{Popup / exit intent / timer / floating badge}}: {{… or "none found"}}
```

---

## 3. FUNNEL PSYCHOLOGY

**Offer architecture:** {{pricing display, bundles, anchoring, crossed-out prices, per-unit math, how compare-at is computed}}

| Tier | Qty | Price | Per unit | Compare-at | SAVE shown | Extras (gifts, shipping, badge, preselected) |
|---|---|---|---|---|---|---|
| {{Buy 1}} | 1 | {{…}} | {{…}} | {{…}} | {{…}} | {{…}} |
| {{Buy 2}} | 2 | {{…}} | {{…}} | {{…}} | {{…}} | {{…}} |
| {{Buy 3}} | 3 | {{…}} | {{…}} | {{…}} | {{…}} | {{…}} |

**Urgency mechanics:** {{timers, stock counters, "selling fast", limited-time, or "none on page", and don't add any in Mode A}}
**Trust architecture:** {{guarantee terms + where repeated, badges, payment icons, review score, endorsements, honesty devices}}
**Social proof architecture:** {{rating line (score, count, placement), testimonial format + personas, UGC, reviews app count/avg}}
**Upsell architecture:** {{quantity breaks, gifts scaling, MOST POPULAR / preselected, BEST VALUE, free-shipping threshold vs tier prices, cart bar}}
**Narrative arc:** Attention {{S…}} → Interest {{S…}} → Desire {{S…}} → Action {{S…}} · awareness stage: {{…}} · buy decision gated at: {{…}}

---

## 4. IMAGE MAP

<!-- Every <img>, background image, GIF, video, icon set, logo. Plans: remake (05) · skip competitor-only ·
     from packshot (05) · Kie i2i new people, copy matches photo (06) · raw + animated WebP (06) · native SVG/theme (04). -->

| ID | Section | Position | Ratio / px | Type | Content (incl. text/claims on image) | Source (URL → media/ file) | Plan | Ref |
|---|---|---|---|---|---|---|---|---|
| P1 | S3 | gallery 1 | 1:1 · {{1080}} | {{infographic}} | {{…}} | {{…}} | remake | 05 |
| B1 | S3 | bundle card | {{~48px}} | static | {{1 unit}} | {{app media}} | from packshot | 05 |
| T1 | {{S4}} | card top | {{1:1}} | photo | {{persona, setting}} | {{…}} | Kie i2i | 06 |
| M1 | {{S5}} | {{right}} | {{1:1 · 1500}} | GIF | {{…}} | {{….gif}} | raw + WebP | 06 |
| IC | {{…}} | icons | SVG | icons | {{checks, ?, stars, chevrons}} | n/a | native | 04 |

---

## 5. COPY INVENTORY

<!-- Every string verbatim, in order. Tags: [CLAIM] keep at full strength · [OFFER] prices/tiers/guarantee/shipping ·
     [NUM] ratings/counts/% · [BOLD] bolded phrase inside a paragraph. Strip capture noise. Exclude review bodies. -->

```
S{{n}}  ({{N}} words)
  S{{n}}.01 [{{element}}]{{[TAGS]}} "{{verbatim text}}"
  S{{n}}.02 [{{element}}] "{{…}}"
…
X1  [sticky] "{{…}}"
TOTAL brand copy ≈ {{N}} words · copy budget per section = these counts ±10%
```

---

## 6. APPS

| App | Detected by | Renders | Config facts (copy, colors, behavior) | Plan (native rebuild / same app / operator to-do) |
|---|---|---|---|---|
| {{Kaching Bundles}} | {{dealBars JSON}} | {{S3 cards, X1}} | {{tiers, preselected, gifts, radius}} | {{native variant-driven cards; operator creates variants}} |
| {{Judge.me}} | {{jdgm classes}} | {{S…}} | {{avg / count}} | {{operator installs + imports; placeholder}} |

**Operator to-dos (for DELIVERY.md):** {{variants at tier prices · gift product + automatic discount · reviews app · shipping threshold}}

---

## 7. Inconsistencies and defaults

| Inconsistency | Default |
|---|---|
| {{offer term mismatch, e.g. 90 vs 30 days}} | harmonize to the main offer ({{30 days}}) |
| {{rating line vs reviews app}} | keep the claim as written |
| {{wrong-market wording}} | localize to {{MARKET}} |
| {{screenshot currency vs JSON}} | JSON wins |

---

## 8. Notes for builder / QA
- {{capture artefacts not to reproduce (blank bands, popups)}}
- {{values marked "unknown — check live"}}
- {{Mode B only: MODE B CHANGE: … (reason)}}
