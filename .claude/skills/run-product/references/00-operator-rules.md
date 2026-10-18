# Operator rules (read first, every run)

These rules come from real corrections by the operator during the Noxis and Ceriva runs. Each one cost a redo the first time. Follow them by default; only deviate when the operator explicitly asks in the current prompt.

## Contents
1. Claims
2. 1:1 testing (titles, palettes, structure)
3. Brand names
4. Product images
5. Page media and GIFs
6. Competitor ads research
7. Ad creatives and copy
8. Git, branches and pushes
9. Live pages and publishing
10. Files and organisation
10b. Policies
11. Copy style
11b. Mobile first
12. Working style and reporting

---

## 1. Claims — keep them at full strength
**Rule:** Never soften, reword, remove, or add disclaimers/caveats to claims — in page copy, product images, ads or ad copy. Carry competitor claims over at the same strength.
**Examples kept as-is:** "Reduces Nighttime Glare By 85%", "Designed for cataract patients", "Cataracts / Astigmatism / Fit Over Prescription Glasses", "World's First", "Rated #1 Headlight Glasses", "GlareCut Technology™", "doctor-recommended", "over 10,000 people trust us".
**Why:** The operator validates claims and runs them already. I once softened claims unasked ("Cuts headlight glare at night", "Rainy nights / Sensitive eyes") and the operator said: "Never told you to do this, revert any claims adjustments you made. every claims we have are validated and running." It cost a full regeneration round.
**Also:** don't add "keep only if true" notes, "consider compliance" remarks, or softened alternates in deliverables. If a claim needs a number (e.g. "1,300+ drivers"), mirror the competitor's pattern with our brand.

## 2. 1:1 testing — reuse what already works
**Rule:** For product tests, take the competitor's proven elements 1:1 and upgrade later only when asked:
- **Product title:** competitor's title structure with our brand ("Plaims Polarized Headlight Glasses" → "Noxis Polarized Headlight Glasses").
- **Color palette:** the competitor's exact hex codes and roles.
- **Page structure:** Mode A faithful clone (same sections, order, components, spacing logic).
**Exception — operator brand guidelines win:** if the operator supplies a brand guideline file (palette, fonts, UI rules, product name), use it instead of the competitor's palette/fonts/title (Aurea run: `aurea-brand-guidelines.md`, pine #1E3328 / honey gold #C99A3A, Cormorant Garamond + Instrument Sans + Cinzel logo, title "Aurea® Prosperity Bracelet"). Layout/structure stays a 1:1 clone.
**Why:** "for product titles don't overthink it, just take what works already 1:1, no need to reinvent the wheel when testing a product. we upgrade later on — same for color palette."

## 3. Brand names
**Rule:** Invented single words, 2–3 syllables, brand-like, that a customer would naturally say in the possessive: "let me get my Plaims glasses" → "let me get my **Noxis** glasses". Credible in the category, pronounceable in the market language, not derivative of the competitor's name. Present 7–10 with the top 3 starred.
**Never** filter, rank or reject names by domain availability ("ignore domain name, we can find ways like my[name] or try[name].com").
**Avoid** descriptive compound names (Clearway, Glareguard, Nightpilot, Roadsight) and existing big brands (Lumix). Rounds of descriptive names were rejected three times before "Noxis" was chosen.
**Market:** names and copy follow the target market — ask if not given ("we want to run in US").

## 4. Product images
- Remake every competitor gallery image: same main idea, layout logic, text structure and claims, with our product.
- **No brand logo or wordmark** on product images. "plaims don't have their logo on them and ours lose space because of logo you added."
- Skip images that only make sense for the competitor (e.g. "IMPORTANT NOTICE — buy only from plaims.com").
- When only text must change, **edit the existing image** with a keep-everything prompt instead of regenerating (cheaper, keeps the approved look).
- Keep superseded versions in subfolders (`with-logo/`, `softened/` …) so nothing approved is lost.

## 5. Page media and GIFs
- Download competitor GIFs **raw** (original files) and keep them untouched in `02_competitor/media/`. The operator asked to reuse the competitor's two GIFs on our page.
- For the theme, convert GIFs to animated WebP (quality ~62, method 6) — ~90% lighter (9.3 MB → 0.9 MB) — and point the section at the WebP.
- Testimonial and lifestyle photos: remake with Kie (same framing, different people). Testimonial text must match its photo (the photo showed a mother, the copy said "dad" → fixed).

## 6. Competitor ads research (Brandsearch)
- **Primary ranking = Brandsearch "Top rank (by impressions)"** (`reach_rank`, ascending; request the field). It works for US ads too. "An ad might be longest running but very low spent" — so days running is only a tie-breaker, together with duplicate copies + `duplicate_count`.
- **Spend/reach sorting only when targeting EU markets** (`eu_total_spend` / `eu_total_reach` exist only for EU-delivered ads). The operator stopped a spend-ranked download of US ads: "don't save top 10 by spend because they sell US and Meta US doesn't show impressions."
- Days running = max of `total_active_time` and end−start dates (the two endpoints disagree).
- Merge identical creatives by image hash; filter to the product with a keyword (the brand also advertised a soap).

## 7. Ad creatives and copy
- Generate a clean packshot first; **attach our packshot to every ad prompt** ("Make sure to upload product image attached with the prompts").
- Top 5 competitor ads: recreate at ~97% fidelity (same layout, text word-for-word incl. claims, fonts, colors, aspect ratio), our product swapped in, new faces for people.
- The rest: inspired by the top-30 patterns (formats × hooks), not copies.
- Never show the competitor's brand name; no text/logo on our product frame (the packshot's temple print came out garbled).
- Ad copy mirrors the competitor's caption framework with the same claim strength.

## 8. Git, branches and pushes
- New branch named after the brand (`noxis`), created from clean `main` — never from another brand's branch.
- Git-ignore prompt/brief files the operator drops in the repo (e.g. `PROMPT_1-1.MD`).
- **Always pull before pushing** (git pull + `shopify theme pull --only <files>`). **Commit first**: a theme pull once overwrote uncommitted local work.
- Shopify's GitHub integration adds bot commits; after `git pull --no-rebase`, verify with `git diff <your-commit> HEAD -- <files>` that nothing of yours was reverted.
- Commit messages end with the attribution line the session specifies.

## 9. Live pages and publishing
- Never publish a theme. Push only to a draft/unpublished theme id (or GitHub only if no store is connected — then ask for the store at delivery).
- If the page already receives live ad traffic, don't overwrite it: build `product.<slug>-v2`, let the operator validate, then swap content into the live template on approval and keep `-v1` for rollback.

## 10. Files and organisation
- All product assets (captures, raw media, generated images, ads, analyses, copy) live in `PRODUCT_DIR` = `PRODUCTS_ROOT/BRAND`, not in the theme repo. The theme repo holds only theme files.
- When moving assets, actually move them (a previous "move" only copied and left duplicates).

## 11. Copy style
- Original wording; paraphrase the key parts; keep the persuasion architecture.
- Simple vocabulary, direct response, short lines; length close to the competitor's (the operator found a 1,500-word page "big and heavy to read compared to inspirations").
- Market language and currency; native typography for the language (e.g. French non-breaking spaces).

## 10b. Policies
**Rule:** Clone the competitor's policies (footer links or `<site>/policies/<handle>`) **1:1, word for word**; replace only their brand name, domain and email addresses with ours; **remove — and never add — postal addresses, phone numbers, registration numbers or any private information**; push them to the store with the rest of the run.
**Why:** operator instruction when finalising the launch automation ("get them 1:1 exactly same… remove (do not put any) specified addresses or private informations… push these pages as well when running a product").

## 11b. Mobile first
**Rule:** Design, build and QA every section at 390px first, then desktop. Most ad traffic is mobile.
- Horizontal rails/carousels (testimonials, reviews, videos) must scroll by **touch and by mouse/pen drag**: the Shopify editor's mobile preview on a desktop has no touch, so a plain `overflow-x: auto` rail can't be scrolled there. Add a pointer-drag handler (disable scroll-snap while dragging, settle on the nearest card on release, suppress the click after a drag) and a visible affordance (next card peeking).
- QA includes a real drag/swipe check of every rail, not just a screenshot.
**Why:** the operator reported "section 'What Our Drivers Say' cannot scroll on mobile" on Noxis; Ceriva's video rail had the same bug earlier.

## 12. Working style and reporting
- Branding first, then wait for validation, then build.
- Use a master + parallel sub-agents; be efficient; don't stall waiting when other streams can run.
- Check Kie credits before batches; report spend.
- Show the operator images (contact sheets), keep messages short, no internal narration.
- Don't add unrequested features or "improvements" in Mode A; mention ideas in one line at the end instead.

## 12. Header defaults (operator, 2026-10-18)
Every store header ships with the search icon, country selector and language selector OFF (`show_search`, `show_country`, `show_language` = false in sections/header-group.json). `main` already has them off, so brand branches inherit it; if a branch shows them, turn them off.
