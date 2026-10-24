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
- **Own variants, not copies (every ad, top 5 included):** before generating, take each source ad's headline and write an *almost similar* variant: same hook mechanism, rhythm, length and claim strength, but different wording ("I rolled my eyes. Then I paid off $7,349 in debt" → "I laughed at it. Then I cleared $7,349 of debt"). Same rule for the design: keep the format, layout zones, type style and color logic, but change the scene/background/props/composition enough that it is ours (≈80–90% similar, not 97%). Numbers and claims keep their strength (rule 1).
- **Validation gate:** write all headline + design variants to `05_ads/AD_VARIANTS.md` and stop for the operator's validation. Generate only after approval, then continue the workflow without stopping again.
- The rest: inspired by the top-30 patterns (formats × hooks), each with its variant headline/design from AD_VARIANTS.md.
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

## 11. No placeholder or example labels (operator, 2026-10-18)
Never ship visible labels such as "Example review", "Avis exemple", "placeholder", "à remplacer", demo badges or "show placeholder badges" settings in any section, block, image or copy. Reviews, testimonials and stats are written as final content (operator validates them). Track anything that needs operator replacement in DELIVERY.md, never on the page.

## 12. Header defaults (operator, 2026-10-18)
Every store header ships with the search icon, country selector and language selector OFF (`show_search`, `show_country`, `show_language` = false in sections/header-group.json). `main` already has them off, so brand branches inherit it; if a branch shows them, turn them off.
- Footer: "Powered by Shopify" off (`show_powered_by` = false) and the social icons block disabled (`social-links` block `"disabled": true` in sections/footer-group.json). Also set in `main`.
- Header is not sticky (`enable_sticky_header` = "never"). Also set in `main`.

## 13. Fully customizable sections and blocks (operator, 2026-10-18)
Every NEW section or block exposes all of its content and styling in the schema, so the operator can change everything in the theme editor without code: every text, image (image_picker + asset fallback), link, icon, color (text, accent, background, buttons, borders), font family/size/weight for headings and body, alignment, spacing/padding (top/bottom, desktop and mobile), layout options (columns, image side, order), visibility toggles per element, and mobile-specific overrides. Group settings with headers and keep them under Shopify limits (max 40 settings per section/block: use blocks for repeated items). Applies to future builds only.
- Ads deliverable = creatives (per placement) + ad copy only. No media plan, budgets, campaign/ad-set structure, targeting or kill/scale rules: the operator runs Ads Manager.

## 14. Strip metadata from AI-generated media (operator, 2026-10-18)
Every AI-generated image or video (Kie GPT Image, Suno covers, Runway/Kling clips, ffmpeg ad videos built from them) has its metadata removed BEFORE it is saved as final or uploaded/pushed anywhere: run `python -I <SKILL>/scripts/strip_metadata.py <files-or-folder> --inplace` (images re-encoded without EXIF/XMP/C2PA provenance; videos remuxed with `-map_metadata -1`). Raw Kie downloads stay in scratch/raw; only cleaned copies go to 03_product-images, 04_page-images, 05_ads and theme assets. Every agent brief that generates media includes this step. Applies to new media only.

## 15. Unique CSS class prefixes per section (2026-10-19)
Every section/block/snippet uses its own class prefix (e.g. `rf-quiz__*`, `rf-hp__*`) and never reuses another component's base class for a different element (a quiz honeypot styled `.rf-hp` once hid the whole product hero on the live store). Before delivery, grep the brand prefix for classes defined in more than one file with conflicting rules, and check the LIVE storefront page (not only the theme editor).

## 16. Video ad remakes (operator, 2026-10-24) — full workflow in `14-video-ads.md`
- **Candidates:** ~20 competitor videos ranked by Brandsearch `reach_rank`, deduped by hook/script/format, in `05_ads/REMAKE_CANDIDATES.md`; stop for the operator's confirmation before remaking anything.
- **Audit every clip** for any competitor trace (packaging, logo, label, website, handles, captions, text overlays, spoken name) and class it: (a) clean, (b) text overlay fixed locally, (c) needs regeneration.
- **Never generate a (c) clip without operator confirmation.** List each with a start-frame prompt (`gpt-image-2-5-sunburst-image-to-image` 1K: original frame + our packshot) and an animation prompt (`wan/2-6-image-to-video` 720p), with costs. `wan/2-6-video-to-video` cannot take an image reference.
- **No lip sync.** Voice-over: transcribe locally (faster-whisper), rewrite (native translation for a new market, or brand swap for the same market), re-voice. Music or sound effects only: keep the audio. Keep character dialogue that never names the competitor.
- **Audio provider:** all audio and voice work uses the ElevenLabs API directly, not Kie (key `G:/Ecom/Products/.secrets/elevenlabs.env`, `ELEVENLABS_API_KEY`; Starter, instant cloning, 40k characters/month). Defaults: `eleven_multilingual_v2`, `language_code` of the market, stability 0.55 / similarity 0.9 / style 0.15 / speaker boost.
- **Clone the original voice:** isolate 30–90 s of the original VO with demucs, clone it (`POST /v1/voices/add`), re-voice only the lines that need remaking and splice them into the original voice track. Record the voice_id in the PLAN; flag when the original sounds like a real person (ElevenLabs' terms require the right to clone) so the operator decides; delete clones no longer needed (10 slots).
- **Always remake three parts of every video**, even when nothing else needs it, so the script and audio curve differ from the original: the hook (the opening sentence/thought, length from the transcript, not fixed seconds), the very end (closing line/CTA) and one random body line. Same meaning, length and claim strength, cloned voice, same beat, captions updated.
- **Sync:** each line on its original beat, original pauses kept, no voice-over across cuts, speed-up at most 1.08x (otherwise rephrase), music 8–10 dB under the voice, about −14 LUFS, captions re-timed word by word. Overlays: old ones covered, new ones in the same style, position and timing; brand names respelled phonetically for TTS only ("Awe-ree-uh").
- **Independent check** before final: frames every 0.5 s, whisper read-back, sync within 0.15 s, the three remakes present, no competitor trace; strip metadata (§14).
- **Folders:** `05_ads/generated/videos/` holds ONLY final videos (`vNN-<slug>.mp4`) at its root; each video has `vNN-work/` with only `vNN-clips.jpg`, `vNN-draft.mp4` and `vNN-PLAN.md`; everything else is deleted once the video is final.
- **Never** swap people with animate-replace models (rendered badly and glitchy); clean up after scripts; never write into the Git Bash root (use absolute paths).
