# BRANDING — {{BRAND or "pending"}} · cloning {{COMPETITOR_NAME}} · {{MARKET}}

<!-- How to fill this: references/02-branding.md. Worked example: §13 there (Noxis / Plaims).
     Default deliverable = snapshot + 7–10 names + palette 1:1 + title 1:1, then STOP for validation.
     Remove these comments when done. -->

**Status:** DRAFT, awaiting operator validation  <!-- → VALIDATED {{YYYY-MM-DD}} -->
**Competitor (#1, the page being cloned):** {{COMPETITOR_URL}}
**Other competitors:** {{URLs or "none"}}
**Capture:** `{{PRODUCT_DIR}}/02_competitor/page/` (p.json, capture.md, screenshots)
**Market:** {{country}} · {{language}} · {{currency}}

---

## 1. Competitor snapshot

```
COMPETITOR │ PRICE                     │ PALETTE                    │ POSITIONING
───────────┼───────────────────────────┼────────────────────────────┼──────────────────────────────
{{name}}   │ {{cur}}{{p1}} ×1 / {{p2}} ×2 / {{p3}} ×3 │ #{{hex}} #{{hex}} #{{hex}} │ {{one sentence: who, pain, enemy, promise}}
```

<!-- Prices come from p.json + the bundle app config, never from the screenshot (geo currency). -->

| Fact | Value |
|---|---|
| Brand / vendor | {{vendor}} |
| Product title (verbatim) | {{product.title}} |
| Handle | {{handle}} |
| Base price / compare-at | {{price}} {{currency}} / {{compare_at or "none"}} |
| Bundle tiers (app) | {{Buy 1 …, Buy 2 … (badge, preselected?), Buy 3 …, gifts}} |
| Fonts | heading {{font}} {{weight}} · body {{font}} |
| Radii | buttons {{px}} · media {{px}} · cards {{px}} |
| Visual tone | {{3–5 words}} |
| Positioning angle | {{who · what they blame · what the brand blames instead · hype vs anti-hype}} |
| Apps seen | {{bundle app, reviews app, cart app…}} |

---

## 2. Brand names (★ = top 3)

<!-- Checklist: invented · 1 word · 2 syllables preferred (max 3) · brand-like, not descriptive ·
     passes "let me get my ___ {{product noun}}" · one pronunciation in the MARKET language ·
     not derivative of the competitor · not an existing big brand · no bad meaning ·
     NO domain filtering, don't mention domains. -->

| # | Name | Syll. | Say it | Why (1 line) |
|---|---|---|---|---|
| ★1 | {{Name}} | {{n}} | "let me get my {{Name}} {{product noun}}" | {{rationale}} |
| ★2 | {{Name}} | {{n}} | "…" | {{rationale}} |
| ★3 | {{Name}} | {{n}} | "…" | {{rationale}} |
| 4 | {{Name}} | {{n}} | "…" | {{rationale}} |
| 5 | {{Name}} | {{n}} | "…" | {{rationale}} |
| 6 | {{Name}} | {{n}} | "…" | {{rationale}} |
| 7 | {{Name}} | {{n}} | "…" | {{rationale}} |

**Operator choice:** {{pending}}

### Earlier rounds / rejected (never re-propose these)
| Round | Names | Operator reaction |
|---|---|---|
| {{1}} | {{…}} | "{{exact words}}" |

---

## 3. Palette (1:1 with {{COMPETITOR_NAME}}, exact hex)

| Role | Hex | Where it appears on the competitor page | Theme target |
|---|---|---|---|
| Primary CTA / buttons | #{{hex}} | {{ATC, …}} | Horizon `color1` + `palette_primary_button_background` · Dawn scheme `button` |
| Announcement / footer bg | #{{hex}} | {{…}} | header-group `background_color` / footer scheme |
| Text | #{{hex}} | {{…}} | `foreground` · Dawn `text` |
| Background | #{{hex}} | {{…}} | `background` |
| Deep / secondary accent | #{{hex}} | {{…}} | `color2` |
| Lines / dividers | #{{hex}} | {{…}} | `color3` |
| Card tint / section colors | {{hex or rgba}} | {{bundle cards, testimonial cards, …}} | section / block settings |
| Muted text | #{{hex}} | {{…}} | section settings |

**Excluded colors (with reason):** {{e.g. #108474: Judge.me default in settings JSON, not visible · #EB001B/#F79E1B/#FF5F00: payment icons}}

---

## 4. Typography and shape (1:1)

| Element | Competitor | Shopify handle / setting |
|---|---|---|
| Headings | {{Poppins 700}} | `type_heading_font: {{poppins_n7}}` |
| Body | {{Inter 400}} | `type_body_font: {{inter_n4}}` |
| Buttons radius | {{40px (pill)}} | {{button_border_radius_primary: 40}} |
| Media radius | {{20px}} | {{…}} |
| Card radius | {{…}} | {{card_corner_radius}} |

---

## 5. Product title (1:1)

| | Title | Handle |
|---|---|---|
| Competitor | {{Plaims Polarized Headlight Glasses}} | {{plaims-headlight-glasses}} |
| **Ours** | **{{BRAND}} {{same descriptors, same order}}** | **{{brand-slug-…}}** |

<!-- Swap only the brand token(s). Keep every descriptor ("Polarized" is a claim word). -->

---

## 6. Decisions (fill after validation)

| Decision | Value |
|---|---|
| BRAND | {{…}} |
| BRAND_SLUG | {{lowercase}} |
| CSS / file prefix | {{slug-}} |
| Product title / handle | {{…}} |
| Palette / fonts | 1:1 as above ({{or chosen variation}}) |
| MODE | {{A}} |
| PRODUCT_DIR | {{PRODUCTS_ROOT}}/{{BRAND}} (renamed from `_{{competitor-slug}}`) |
| Git branch | `{{BRAND_SLUG}}` from clean `main` |
| Validated by operator on | {{YYYY-MM-DD}} |

---

## 7. Upgrade options (ONLY if the operator asked; not for the test)

<!-- Delete this section unless requested. -->

### Palette variations
| Variation | Colors (hex · role) | Idea |
|---|---|---|
| MIRROR (same hue family) | #{{}} primary · #{{}} accent · #{{}} text | {{…}} |
| SHIFT (same spectrum, different hue) | {{…}} | {{…}} |
| CONTRAST (different spectrum) | {{…}} | {{…}} |
| WILDCARD | {{…}} | {{…}} |

### Title candidates (paraphrased structure; top 2 starred)
1. ★ {{…}}
2. ★ {{…}}
3. {{…}}
4. {{…}}
5. {{…}}
