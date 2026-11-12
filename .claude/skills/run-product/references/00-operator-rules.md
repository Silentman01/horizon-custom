# Operator rules (read first, every run)

These rules come from real corrections by the operator during the Noxis and Ceriva runs. Each one cost a redo the first time. Follow them by default; only deviate when the operator explicitly asks in the current prompt.

## Contents
1. Claims
2. Adapted framework (study what works, build our own)
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
17. Step Alpha before anything is built
18. Sample gate: about 5 images confirmed before any batch

---

## 1. Claims — keep them at full strength
**Rule:** Never soften, reword, remove, or add disclaimers/caveats to claims — in page copy, product images, ads or ad copy. Carry competitor claims over at the same strength.
**Examples kept as-is:** "Reduces Nighttime Glare By 85%", "Designed for cataract patients", "Cataracts / Astigmatism / Fit Over Prescription Glasses", "World's First", "Rated #1 Headlight Glasses", "GlareCut Technology™", "doctor-recommended", "over 10,000 people trust us".
**Why:** The operator validates claims and runs them already. I once softened claims unasked ("Cuts headlight glare at night", "Rainy nights / Sensitive eyes") and the operator said: "Never told you to do this, revert any claims adjustments you made. every claims we have are validated and running." It cost a full regeneration round.
**Also:** don't add "keep only if true" notes, "consider compliance" remarks, or softened alternates in deliverables. If a claim needs a number (e.g. "1,300+ drivers"), mirror the competitor's pattern with our brand.

## 2. Adapted framework — study what works, build our own
**Rule:** We do NOT do pixel-perfect 1:1 clones. We MAP the competitor's proven framework (section order, conversion flow, offer architecture, trust architecture, social proof placement, funnel psychology) and then BUILD OUR OWN ADAPTED VERSION that uses the same winning principles but looks distinctly different. The goal: if an AI compared our shop and the competitor's shop side by side, it would struggle to find similarities and see two completely different things.
- **Product title:** use the competitor's title STRUCTURE and PATTERN with our brand ("Plaims Polarized Headlight Glasses" → "Noxis Polarized Headlight Glasses"). The pattern stays; the words are ours.
- **Color palette:** start from the competitor's palette reasoning (same color roles — accent, background, trust, CTA) but adapt the palette to our brand. Same role logic, possibly different shades and combinations.
- **Page structure:** study the competitor's section order, conversion mechanics and funnel psychology (why it converts), then ADAPT it — same conversion principles, different execution. Reorder sections where it makes sense, change layouts (2-col → stacked, grid → rail, etc.), use different visual patterns, while preserving the same funnel psychology and conversion architecture. The framework MAP documents what each section does for conversion; the ADAPTATION BLUEPRINT describes how our version achieves the same job differently.
- **Copywriting:** no title, headline, subtitle or body text may be word-for-word identical to the competitor's. Every string is our own original version, informed by the Step Alpha dossier (verbatim customer language, pain points, dream outcomes, objection-ready phrases). The copy chief always runs the books-playbooks for all persuasive copy.
- **Shop design:** sections, blocks, spacing, colors, imagery and typography are our own. We keep the proven conversion mechanics (what the visitor sees first, how urgency works, where trust is built, how the offer is framed) but the visual execution is ours.
**Exception — operator brand guidelines win:** if the operator supplies a brand guideline file (palette, fonts, UI rules, product name), use it instead of the competitor-derived palette/fonts/title (Aurea run: `aurea-brand-guidelines.md`, pine #1E3328 / honey gold #C99A3A, Cormorant Garamond + Instrument Sans + Cinzel logo, title "Aurea® Prosperity Bracelet").
**Why:** we extract the competitor's winning formula (what converts), then build our own version so we have fully original content while keeping the proven conversion mechanics. The goal is distinctiveness: an AI comparing both shops sees two completely different things.

## 3. Brand names
**Rule:** Invented single words, 2–3 syllables, brand-like, that a customer would naturally say in the possessive: "let me get my Plaims glasses" → "let me get my **Noxis** glasses". Credible in the category, pronounceable in the market language, not derivative of the competitor's name. Present 7–10 with the top 3 starred.
**Never** filter, rank or reject names by domain availability ("ignore domain name, we can find ways like my[name] or try[name].com").
**Avoid** descriptive compound names (Clearway, Glareguard, Nightpilot, Roadsight) and existing big brands (Lumix). Rounds of descriptive names were rejected three times before "Noxis" was chosen.
**Market:** names and copy follow the target market — ask if not given ("we want to run in US").

## 4. Product images
- **Own conversion gallery, not 1:1 remakes (operator 2026-11-12):** "a second version on product images that are not 1:1 from competitors but instead are improved and our fully own while helping CVR, horizontal scroll, framework, direct response". Map the competitor gallery (the job of each slide, its claims), then build our own swipe story from the dossier (05 §16 GALLERY FRAMEWORK): hero thumb-stop → problem → mechanism → demo → outcome → comparison + cost → social proof → objection buster → risk reversal. Use one design system, keep claims at full strength in our wording, and use the real packaging. A 1:1 remake set (the old default) is made only for an A/B, in `v1_remake/`.
- **Never show a price on product images** (operator 2026-11-12): no € / $ figure, "Dès …", per-week cost or crossed-out price on any gallery or page image. Offer words without numbers ("90 jours satisfait ou remboursé", "Le plus choisi") are fine. Prices live in the buy box only.
- **Inspiration bank before the gallery plan** (operator 2026-11-12): "get inspiration from any brands that are scaling on brandsearch and have proven frameworks … making a bank of product images, by category/niches … and we make our own mix". See 05 §16.0.
- **No brand logo or wordmark overlaid on the image layout** (corner logos, wordmark headers on infographics). "plaims don't have their logo on them and ours lose space because of logo you added."
- **But the product's own packaging carries OUR brand** (operator 2026-11-12, Oralys): when the product is a tube, box, bottle or sachet and the competitor prints its brand on it, ours shows our logo the same way. "product doesn't have our logo on them, is that normal? if not, fix". I had specced a blank tube, and ~25 images were redone. Define the branded packaging in BRANDING.md, build the packshot with the padded logo file as an edit reference, keep the printed text LARGE and minimal, and every later image uses that packshot.
- **The packaging is the real supplier product, rebranded, never an invented design** (same day): "we want to remake this exact same one … So customers receive that product and not different from our product images … see it as a kind of mockup or template". The operator sent the white-label supplier tube+box ("Bond Base 7"), which the competitor sells rebranded as "Oragel 7". Use that photo as the template, swap only the brand word, the tagline (into the market language) and the units, and keep the shape, colours, fonts, layout and number marks. Store it as `01_branding/packaging/<supplier>-original.png`. At the branding gate, ask for the supplier photo when the competitor's packaging looks white-label, meaning the same pack shows up under other brand names.
- Skip images that only make sense for the competitor (e.g. "IMPORTANT NOTICE — buy only from plaims.com").
- When only text must change, **edit the existing image** with a keep-everything prompt instead of regenerating (cheaper, keeps the approved look).
- Keep replaced versions once in `<area>/archive/v<N>_<reason>/` (`v1_with-logo/`, `v1_softened/` …) so nothing approved is lost; never a `superseded/` or duplicate folder.

## 5. Page media and GIFs
- Download competitor GIFs **raw** (original files) and keep them untouched in `02_competitor/media/`. The operator asked to reuse the competitor's two GIFs on our page.
- For the theme, convert GIFs to animated WebP (quality ~62, method 6) — ~90% lighter (9.3 MB → 0.9 MB) — and point the section at the WebP.
- Testimonial and lifestyle photos: remake with Kie (same framing, different people). Testimonial text must match its photo (the photo showed a mother, the copy said "dad" → fixed).

## 6. Competitor ads research (Brandsearch)
- **Pull the complete footprint (2026-11-10):** every ad of the competitor (active and inactive, every platform Brandsearch has) plus a transcript of every video ad, for Step Alpha (§17). The top-30 ranking below is still made for the creative and video remakes.
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
- **Fully original wording — no 1:1 copies.** No title, headline, subtitle or body text may be word-for-word identical to the competitor's. Every string must be our own original version. Paraphrase the persuasion job (what each line does for conversion), not the words themselves. Use Step Alpha's customer language (verbatim pain points, dream outcomes, objection-ready phrases from 3.5) so customers feel heard — but in our own sentences.
- Simple vocabulary, direct response, short lines; length close to the competitor's (the operator found a 1,500-word page "big and heavy to read compared to inspirations").
- Market language and currency; native typography for the language (e.g. French non-breaking spaces).

## 10b. Policies
**Rule:** Clone the competitor's policies (footer links or `<site>/policies/<handle>`) **1:1, word for word**; replace only their brand name, domain and email addresses with ours; **remove — and never add — postal addresses, phone numbers, registration numbers or any private information**; push them to the store with the rest of the run. **In the market's language:** when the competitor writes in another language, the 1:1 text is translated faithfully into the market language — never ask (operator 2026-11-12: "use common sense pls, we run FR so it's FR").
**Why:** operator instruction when finalising the launch automation ("get them 1:1 exactly same… remove (do not put any) specified addresses or private informations… push these pages as well when running a product").

## 11b. Mobile first
**Rule:** Design, build and QA every section at 390px first, then desktop. Most ad traffic is mobile.
- Horizontal rails/carousels (testimonials, reviews, videos) must scroll by **touch and by mouse/pen drag**: the Shopify editor's mobile preview on a desktop has no touch, so a plain `overflow-x: auto` rail can't be scrolled there. Add a pointer-drag handler (disable scroll-snap while dragging, settle on the nearest card on release, suppress the click after a drag) and a visible affordance (next card peeking).
- QA includes a real drag/swipe check of every rail, not just a screenshot.
**Why:** the operator reported "section 'What Our Drivers Say' cannot scroll on mobile" on Noxis; Ceriva's video rail had the same bug earlier.

## 12. Working style and reporting
- Step Alpha first (§17), then branding, then wait for validation, then build.
- Use a master + parallel sub-agents; be efficient; don't stall waiting when other streams can run.
- Check Kie credits before batches; report spend.
- Show the operator images (contact sheets), keep messages short, no internal narration.
- Don't add unrequested features or "improvements"; mention ideas in one line at the end instead.

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
- **Video analysis (operator, 2026-11-01):** scenes, the a/b/c trace audit, framework/beat map, hook, overlays and the VO are read by Gemini Flash through ArgoLink (`scripts/video_gemini.py`, `gemini-3.8-flash`); whisper stays for word timings and the sync check, and the full-resolution keyframe look stays as the backstop for clips Gemini marks clean.
- **Only (c) clips are regenerated (operator, 2026-11-04).** (a) clips keep the original footage and (b) clips get a local fix. A video with 6 (c) shots costs about $1.26, not $7+. This is the biggest cost lever in the remake.
- **Burned-in subtitles are REMOVED, never covered (operator, 2026-11-04).** Run `scripts/video_desub.py` (EAST text detection + LAMA inpainting on the local GPU, free) so the background behind the text is reconstructed. A blur band, a dark bar and a full-width delogo all fail — they hide the footage and the original text still ghosts through. Process is always: clear the original subtitles, then write the new ones at the same measured position.
- **Pipeline order (2026-11-04):** insert the (c) clips FIRST, then de-subtitle, then burn the new captions and audio. Burning captions before the inserts leaves the generated clips with no captions.
- **No lip sync.** Voice-over: transcribe locally (faster-whisper), rewrite (native translation for a new market, or brand swap for the same market), re-voice. Music or sound effects only: keep the audio. Keep character dialogue that never names the competitor.
- **Audio provider:** all audio and voice work uses the ElevenLabs API directly, not Kie (key `D:/Ecom/Products/.secrets/elevenlabs.env`, `ELEVENLABS_API_KEY`; Starter, instant cloning, 40k characters/month). Defaults: `eleven_multilingual_v2`, `language_code` of the market, stability 0.55 / similarity 0.9 / style 0.15 / speaker boost.
- **Clone the original voice:** isolate 30–90 s of the original VO with demucs, clone it (`POST /v1/voices/add`), re-voice only the lines that need remaking and splice them into the original voice track. Record the voice_id in the PLAN; flag when the original sounds like a real person (ElevenLabs' terms require the right to clone) so the operator decides; delete clones no longer needed (10 slots).
- **Always remake three parts of every video**, even when nothing else needs it, so the script and audio curve differ from the original: the hook (the opening sentence/thought, length from the transcript, not fixed seconds), the very end (closing line/CTA) and one random body line. Same meaning, length and claim strength, cloned voice, same beat, captions updated.
- **Sync:** each line on its original beat, original pauses kept, no voice-over across cuts, speed-up at most 1.08x (otherwise rephrase), music 8–10 dB under the voice, about −14 LUFS, captions re-timed word by word. Overlays: old ones covered, new ones in the same style, position and timing; brand names respelled phonetically for TTS only ("Awe-ree-uh").
- **Independent check** before final: frames every 0.5 s, whisper read-back, sync within 0.15 s, the three remakes present, no competitor trace; strip metadata (§14).
- **Folders:** `05_ads/generated/videos/` holds ONLY final videos (`vNN-<slug>.mp4`) at its root; each video has `vNN-work/` with only `vNN-clips.jpg`, `vNN-draft.mp4` and `vNN-PLAN.md`; everything else is deleted once the video is final.
- **Never** swap people with animate-replace models (rendered badly and glitchy); clean up after scripts; never write into the Git Bash root (use absolute paths).

## 17. Step Alpha before anything is built (operator 2026-11-10)
**Rule:** after the competitor capture (Phase 1, raw data only), run Step Alpha, the pre-launch intelligence dossier, and pass its quality gate before anything is built or generated: no branding, names, copy, section spec, pages, images, ads, ad copy, videos, product CSV, checkout header or policies transform. Spec (authoritative, verbatim): `references/19-step-alpha.md`; how to run it: `references/20-step-alpha-runbook.md`. The run stops once inside Alpha (GATE α): the operator runs our tailored prompt in ChatGPT and pastes the result back; the synthesis, dossier and quality gate come after it. Every downstream step reads the dossier sections it names.
**Why (operator's words, spec lines 1–26):**
> STEP ALPHA — PRE-LAUNCH INTELLIGENCE
> Runs BEFORE any asset is created.
> Nothing is built until Alpha is complete.
>
> This step produces the intelligence foundation that every downstream step in the workflow consumes. Product pages, ad copy, video scripts, image creatives, branding — all of it inherits from Alpha's output. The quality of every asset the workflow produces is capped by the quality of this intelligence. Treat it accordingly.
>
> Step Alpha has TWO ANALYSES:
>
> ANALYSIS 1 — COMPETITOR INTELLIGENCE — "What are they doing, who are they selling to, and how is their funnel constructed?"
>
> ANALYSIS 2 — OPPORTUNITY INTELLIGENCE — "What can WE do that they aren't — hidden angles, underserved audiences, untapped emotional territories, and raw customer language we can weaponize?"
>
> Both analyses must complete before ANY downstream step fires.

## 18. Sample gate: about 5 images confirmed before any batch (operator 2026-11-12)
**Rule:** never generate a full image batch before the operator has confirmed a small sample. Each generation stream first makes **about 5 representative images**, shows them on ONE contact sheet and **stops**. Only after the operator's OK does it generate the rest, then continue without stopping again.
- **Product / page images (streams B + C), one shared sample:** the packshot (real packaging, 00 §4), the gallery hero (slide 1), one graphic slide (mechanism or comparison, to check text, spelling, margins and the design system), one lifestyle or testimonial image with a person (to check the people, the product in hand and the fit spec), and one page or advertorial image.
- **Ads (D2):** after the AD_VARIANTS gate, generate the first ~5 ads (the top-ranked variants, including one native lo-fi format when the competitor runs them) → sample gate → the remaining ads.
- **Video (G):** the existing candidate and clip gates already apply.
- **Free before the gate:** prompts, job files, GALLERY_PLAN.md and AD_VARIANTS.md cost nothing, so write them in full before the gate. The operator's feedback is then applied to every job before the batch runs.
- **Sample sheet:** `<area>/_samples.jpg` (temporary, deleted after the gate). Report the cost of the sample and the estimated cost of the full batch.
**Why:** on Oralys, about 90 images were generated before the operator first looked. The packaging was wrong (a blank tube instead of the real supplier tube rebranded) and the gallery was a 1:1 remake instead of our own, so most of the batch had to be redone. The operator: "never generates all these images before we confirm few … generate around 5 images and once confirmed it can go through everything else. so we don't waste credits like we did and give feedbacks again".

Also: "before building anything, we must run step alpha". The old Phase 3 ad analysis is removed fully: "you can remove the ad analysis phase 3 since we do every analysis in step alpha now" and "it doesn't move, remove it fully, step alpha is a way better and improved way and contains everything that needs to be analyzed". Step Alpha is the only ad and customer analysis in this skill.

## Operator rules (summary — full text in the sections above)

- **Step Alpha before anything is built (§17).** Phase 1 capture (incl. every competitor ad + every video transcript) → Step Alpha dossier → ChatGPT prompt to the operator (GATE α, wait for the pasted result) → synthesis → dossier passes the quality gate (`alpha_gate.py` + read-through). Only then branding and every other step, each reading the dossier. Step Alpha is the only analysis step.
- **Claims stay at full strength.** Never soften, reword, remove or caveat claims ("Reduces Nighttime Glare By 85%", "Designed for cataract patients", "doctor-recommended"). The operator validates claims.
- **Adapted framework, not 1:1 clones (§2).** MAP the competitor's winning formula (conversion flow, funnel psychology, offer/trust/proof architecture), then BUILD OUR OWN version: same conversion principles, different execution. Title pattern stays with our brand; palette adapted from the competitor's role logic; page structure, copy, and design are distinctly ours. No string word-for-word identical to the competitor's.
- **Brand names:** invented, one word, 2–3 syllables, passes "let me get my ___ glasses". Never filter by domain availability.
- **Sample gate (§18):** every image stream first makes ~5 representative images on one sheet → operator OK → then the full batch. Plans and job files are written in full before the gate (free).
- **No logo overlaid on product images, but the packaging is the real supplier product rebranded with our name (§4)**; own conversion gallery, not 1:1 remakes; skip competitor-specific images (anti-replica notices); edit existing images when only text changes.
- **GIFs raw**: download originals, keep them, use animated WebP in the theme.
- **Ads ranking: Brandsearch "Top rank (by impressions)" (`reach_rank`) first; spend/reach only when targeting EU markets; days running + duplicates as tie-breakers.** Filter to the product keyword. Dedupe by image hash.
- **Copy chief + playbooks:** all persuasive copy (ad headline variants, ad copy, page/home copy, image claims, offers) is written or punched up by an Opus copy-chief agent using `books-playbooks/` — no softness, calibrated to the competitor's proven framework and promise level, sharpened with the playbooks (`references/13-copy-playbooks.md`).
- **Every ad prompt attaches our packshot**; no competitor brand names. **Before generating any ad**, write `05_ads/AD_VARIANTS.md` (each source headline → our almost-similar variant; each design → our close-but-different variant) and stop for operator validation; after approval generate and keep going (08 §1b).
- **Video ads** (on request, `references/14-video-ads.md`): ~20 candidates by `reach_rank` → operator confirms; per video, audit every clip (a clean / b overlay fixed locally / c regenerate); no lip sync; re-voice with an ElevenLabs clone of the original voice (never Kie for audio); always remake the hook, the end and one random body line; (c) clips only after operator confirmation; `generated/videos/` holds finals only.
- **Git:** branch named after the brand from clean `main`; commit → pull → merge-check → push; never publish; never overwrite a template with live ad traffic.
- **Assets live in `PRODUCT_DIR`** (shop folder), not in the theme repo.
- **Mobile first:** build and QA at 390px first; every horizontal rail scrolls by touch *and* mouse drag (editor mobile preview has no touch).
