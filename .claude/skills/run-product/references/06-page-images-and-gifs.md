# Phase 3C — Page images, GIFs and videos

Goal: every non-gallery visual on the product page (testimonial photos, lifestyle/section images, animated GIFs, videos) exists for our brand, is light enough for the theme, and is wired into the section settings — so the page looks complete in the first preview.

Read first: `00-operator-rules.md` §1, §5, §10; `tools-kie.md` (runner, PEOPLE-SWAP / CONCEPT-REMAKE / EDITORIAL patterns).
Inputs come from the SECTION_SPEC **IMAGE MAP** (conversion-architect) and the raw media downloaded in Phase 1.

## Contents
1. Inputs, outputs, budget
2. Step 1 — Build the media plan from the IMAGE MAP
3. Step 2 — Download everything raw
4. Step 3 — GIFs: keep raw, convert to animated WebP
5. Step 4 — Testimonial photos: new people, copy must match
6. Step 5 — Lifestyle and section images
7. Step 6 — Videos
8. Step 7 — Export theme-ready files
9. Step 8 — Wire into section settings
10. Step 9 — Review
11. Optional — Editorial photos for advertorial/listicle pages
12. Noxis run — worked example

---

## 1. Inputs, outputs, budget

| Input | Where |
|---|---|
| IMAGE MAP (slot, section, ratio, content, competitor source) | `02_competitor/page/SECTION_SPEC.md` |
| Competitor media URLs | `02_competitor/page/capture.json` |
| Raw media | `02_competitor/media/` (from the media agent) |
| Testimonial copy (names, text) | copy deck from the copywriter |
| Packshot | `03_product-images/<slug>-packshot.png` |

| Output | Path |
|---|---|
| Raw competitor GIFs/images/videos (untouched) | `02_competitor/media/` |
| 2K masters of remade photos | `04_page-images/<slug>-review-N.png`, `<slug>-<role>.png` |
| Animated WebP of GIFs | `04_page-images/<slug>-<name>.webp` |
| Theme-ready copies | `04_page-images/theme/<slug>-<role>.jpg|.webp` → master copies to `THEME_DIR/assets/` |
| Media plan with final file per slot | returned to the master (goes to DELIVERY.md placeholder map) |

Budget: 10 credits per remade photo at 2K (Noxis: 3 testimonials = 30). GIF/video handling costs nothing.

---

## 2. Step 1 — Build the media plan from the IMAGE MAP
**Purpose:** one row per visual slot so nothing is forgotten and every slot gets the right treatment.
**Do:** turn the IMAGE MAP into this table:

| Slot | Section / block | Ratio | Competitor source | Kind | Treatment | Our file |
|---|---|---|---|---|---|---|
| T1 | testimonials / card 1 | 1:1 | `plaims-review-Dennis.png` | testimonial photo | PEOPLE-SWAP remake | `noxis-review-1.jpg` |
| S1 | image-with-text 1 | 1:1 | `iphone-camera-no-text.gif` | GIF | raw → WebP | `noxis-night-road.webp` |

Treatment rules:
| Kind | Treatment | Why |
|---|---|---|
| GIF (demo, POV, before/after animation) | **reuse the competitor's GIF**: keep raw, convert to animated WebP | operator rule 5 — the operator asked to use the competitor's GIFs; regenerating animation isn't possible with image models |
| Testimonial / UGC photo | PEOPLE-SWAP remake (same framing, different people) | operator rule 6 — never reuse real customers' faces |
| Lifestyle / section photo | CONCEPT-REMAKE (no text) or PEOPLE-SWAP if a person dominates | same concept, our product, new people |
| Infographic / diagram with text | CONCEPT-REMAKE with text verbatim (claims at full strength) | same rules as gallery images (05) |
| Icons, badges, payment logos | not generated — the builder uses SVG/theme icons | crisp, tiny, no credits |
| Video | download raw only; operator uploads | Shopify video settings need Shopify-hosted files |
| Competitor-specific (their founder, their logo, "as seen on" with their name) | skip or ask | same as 05 Step 3 |

**Output:** the media plan table (in your return; master merges it into DELIVERY.md).
**Done when:** every IMAGE MAP slot has a treatment and a planned file name.

## 3. Step 2 — Download everything raw
**Purpose:** original files are the references and, for GIFs, the actual page assets.
**Do:** if the media agent hasn't already:
```
python -I "<SKILL>/scripts/fetch_media.py" --out "<PRODUCT_DIR>/02_competitor/media" --from-capture "<PRODUCT_DIR>/02_competitor/page/capture.json" --kinds gifs,images,videos --webp-dir "<PRODUCT_DIR>/04_page-images"
```
Check file sizes: a real animated GIF is usually several MB; a 50–200 KB `.gif` is often a poster frame or a resized CDN variant — find the original URL (strip `_540x`, `?width=` etc.).
**Output:** raw files in `02_competitor/media/`, names that say what they are (`headlight-glasses-clean.gif`, `<comp>-review-<name>.png`).
**Done when:** every IMAGE MAP source exists locally at original size.
**Pitfalls:** saving only the WebP and losing the raw GIF (the operator wants the raw files kept); re-encoding raw files "to save space".

## 4. Step 3 — GIFs: keep raw, convert to animated WebP
**Purpose:** use the competitor's proven animations at ~10% of the weight.
**Do:**
1. Keep the raw GIF untouched in `02_competitor/media/`.
2. Convert to animated WebP, **quality 62, method 6**, all frames, loop forever — `fetch_media.py --webp-dir` does this. Fallback:
   ```
   python -I -c "import sys;from PIL import Image;im=Image.open(sys.argv[1]);im.save(sys.argv[2],'WEBP',save_all=True,quality=62,method=6,loop=0)" raw.gif "<PRODUCT_DIR>/04_page-images/<slug>-<name>.webp"
   ```
   (Pillow carries per-frame durations over from the GIF.)
3. Verify: same frame count as the GIF (`Image.open(f).n_frames`), plays at the same speed, target ≤ ~1.5 MB. If larger, lower quality to 50–55 or downscale to the slot's display width (e.g. 540–720 px) before converting.
4. Check the frames for burned-in competitor branding (logo watermark, their URL). Edge watermark → crop all frames; centered branding → tell the master (can't be fixed cheaply) and prefer another GIF/clean variant from the competitor's files (Plaims served "-clean" / "-no-text" variants).
5. Name with the brand prefix by content, not by competitor name: `<slug>-night-road.webp`, `<slug>-headlights.webp`; copy to `04_page-images/theme/`.
**Output:** WebP per GIF + raw kept.
**Done when:** each WebP animates correctly and is ≤ ~1.5 MB.

> **Noxis run:** "use the 2 gifs … in our noxis product page" → `iphone-camera-no-text.gif` 9.5 MB → `noxis-night-road.webp` 0.9 MB; `headlight-glasses-clean.gif` 11.0 MB → `noxis-headlights.webp` 1.2 MB (540×540, 59 and 74 frames). Raw GIFs kept in the media folder.

## 5. Step 4 — Testimonial photos: new people, copy must match
**Purpose:** UGC-style proof photos with the same framing and emotion as the competitor's, of people who don't exist — and whose photo agrees with the words next to it.
**Do:**
1. For each testimonial slot, read the competitor photo **and** our testimonial text (copy deck). Decide the person/people from the copy (gender, age, relationship, count, setting); if the copy isn't written yet, describe from the competitor photo and hand the description to the copywriter.
2. Fill PEOPLE-SWAP (§tools-kie 11): references `[competitor photo, packshot]`; describe shot type, each person (age, gender, hair, facial hair, clothing, expression), setting, light; "different people from the reference"; "Natural, unpolished, real customer photo look. No text, no logos." Ratio = slot ratio (usually 1:1), 2K, names `<slug>-review-N`.
3. Run into `04_page-images/`, Read each result.
4. **Copy-match check** for every photo vs its text: gender, age bracket, relationship words (mom/dad, husband/wife), number of people, setting (car/home/day/night), and **every pronoun in the full text** (he/she/him/her/his). Fix the copy if only words disagree (free); regenerate the photo if the photo contradicts the story.
5. Names come from our copy deck (never the competitor's customer names).
**Output:** `04_page-images/<slug>-review-N.png` + any copy corrections returned to the master.
**Done when:** each photo and its text describe the same person/people, and faces differ from the competitor's.
**Pitfalls:** text in the photo (signs, phone UI) — say "No text"; glossy studio look — say "smartphone selfie, natural, unpolished"; identical-looking faces across the 3 testimonials — vary age, hair, clothes, setting.

> **Noxis run:** the Priya photo (daughter + elderly mother) was remade as "a woman in her 40s with her elderly mother in the passenger seat, both smiling and both wearing the glasses". The copy said "I bought these for my **dad**" → changed to "mom", but "had started asking me to drive **him** to things" was missed. Scan every pronoun, not just the first mention.

## 6. Step 5 — Lifestyle and section images
**Purpose:** fill image-with-text and banner slots with on-concept visuals of our product.
**Do:**
- Image with a competitor reference → CONCEPT-REMAKE (refs `[competitor image, packshot]`), "no text" unless the original has on-image text (then quote it verbatim, claims at full strength).
- Slot with no reference (or a stock photo) → EDITORIAL (t2i, or i2i with the packshot when the product is visible).
- Ratio = the slot's ratio from the IMAGE MAP: 1:1 / 3:2 / 16:9 / 9:16 at 2K; 4:5 or 5:4 at 1K (2K doesn't support them).
- Names by role: `<slug>-problem.png`, `<slug>-howto-1.png`, `<slug>-lifestyle-couple.png`.
**Output:** 2K masters in `04_page-images/`.
**Done when:** every lifestyle/section slot in the media plan has a master.

## 7. Step 6 — Videos
**Do:** download raw MP4/MOV into `02_competitor/media/` (fetch_media `--kinds videos`). Do not convert, compress or upload. Shopify Files/product-media upload is the operator's job (theme video settings need a Shopify-hosted video). Add a to-do: "upload `<file>` to Shopify Files and pick it in section `<name>`". If the slot is a short silent loop and the operator wants it working immediately, propose (one line) converting it to animated WebP like a GIF.
**Done when:** raw videos are saved and listed in the media plan as operator uploads.

## 8. Step 7 — Export theme-ready files
**Purpose:** theme assets must be light; 2K PNGs (5–7 MB) would cripple mobile load.
**Do:**
1. Photos → JPG, quality 80–84, progressive, longest side by display size: testimonial cards ~800 px; half-width section images 1000–1200 px; full-width banners 1400 px.
   ```
   python -I -c "import sys;from PIL import Image;im=Image.open(sys.argv[1]).convert('RGB');s=int(sys.argv[3]);im.thumbnail((s,s));im.save(sys.argv[2],'JPEG',quality=82,progressive=True,optimize=True)" master.png "<PRODUCT_DIR>/04_page-images/theme/<slug>-review-1.jpg" 800
   ```
2. Animations → the WebP from Step 3.
3. Names: `<brand_slug>-<role>[-n].<ext>`, lowercase, hyphens (Shopify asset names are flat — the prefix prevents collisions with other brands in the same theme).
4. Size targets: testimonial JPG ~80–120 KB; section JPG ≤ ~250 KB; WebP animation ≤ ~1.5 MB.
5. Keep masters in `04_page-images/`; theme copies in `04_page-images/theme/`. The master (or builder) copies them into `THEME_DIR/assets/` — the theme repo gets only these light files.
**Output:** `04_page-images/theme/*`.
**Done when:** every slot has a theme-ready file within the size targets.

> **Noxis run:** testimonials exported at 800×800 JPG, 89–96 KB each (`assets/noxis-review-1..3.jpg`).

## 9. Step 8 — Wire into section settings
**Purpose:** the page shows real visuals immediately, while the operator can still swap images from the editor later.
**Do (with the builder, see 04-product-page-build.md):**
1. Each custom section/block that shows an image should have **both** an `image_picker` setting and a text setting for a theme-asset fallback, rendered in this order: picked image → theme asset (`{{ setting | asset_url }}`) → labeled placeholder. Noxis used a shared snippet (`noxis-media`) doing exactly that.
2. In the product template JSON (`templates/product.<slug>.json` or the template the builder made), set the fallback values to the asset file names:
   ```json
   "t1": {"type": "testimonial", "settings": {"name": "Gary M", "text": "<p>…</p>", "image_asset": "noxis-review-1.jpg"}},
   "image_text_1": {"type": "noxis-image-text", "settings": {"asset": "noxis-night-road.webp", "ratio": "1 / 1", "title": "…"}}
   ```
3. `image_picker` values can't point at a local file — they need an image uploaded to Shopify (`shopify://shop_images/<file>`). Leave them empty; the operator may upload and pick later (picked image wins).
4. Keep each placeholder label descriptive (it documents what the slot needs).
**Output:** settings updated in the template; asset files listed for the commit.
**Done when:** a local render / preview shows every slot filled, and `shopify theme check` is clean.
**Pitfalls:** editing the live template that receives ad traffic (operator rule 11 — build `product.<slug>-v2`); forgetting to commit the asset files with the template; GIF in `assets/` instead of the WebP.

## 10. Step 9 — Review
**Do:** `python -I "<SKILL>/scripts/contact_sheet.py" "<PRODUCT_DIR>/04_page-images/*.png" --out "<PRODUCT_DIR>/04_page-images/_sheet.jpg"` and a competitor-vs-ours pair sheet; Read both. Checklist: same framing/emotion as the competitor; different faces; product matches the packshot (no print on it); no text or logos; copy-match passed; theme files within size targets. Fix with KEEP-EDIT (small element) or regenerate (wrong person/framing); move old versions to `04_page-images/superseded/<reason>/` first.
**Done when:** the checklist passes and the master has the slot → file mapping and credits spent.

## 11. Optional — Editorial photos for advertorial/listicle pages
When the run includes an advertorial or listicle landing page (not the default product test), generate documentary-style photos with EDITORIAL: "Candid documentary smartphone photo … soft natural window light, real <market> setting, slightly imperfect framing, film grain, editorial magazine photography, not staged or glossy. No text, no logo." 3:2 at 2K. When the product is in the shot, attach the packshot (or product photo) and say "Use the reference ONLY to copy the exact product". Any readable text (e.g. a warning on packaging) must be specified verbatim in the market language.
> **Ceriva run:** `jobs_article.json` / `jobs_lp2.json` — "art-morning" (woman's bathroom routine, 3:2 2K t2i), "art-discovery" and "lp-earbuds-clean" (i2i with the product box reference: "Keep the box text exactly as in the reference; add no other text").

## 12. Noxis run — worked example

Media plan (final):
| Slot | Competitor source | Treatment | Our file (theme) |
|---|---|---|---|
| Image-with-text "You Never Decided to Stop Driving at Night" | `iphone-camera-no-text.gif` (9.5 MB) | raw kept → WebP q62 m6 | `noxis-night-road.webp` (0.9 MB) |
| Image-with-text (headlights demo) | `headlight-glasses-clean.gif` (11.0 MB) | raw kept → WebP q62 m6 | `noxis-headlights.webp` (1.2 MB) |
| Testimonial 1 (Gary M) | `plaims-review-Dennis.png` | PEOPLE-SWAP | `noxis-review-1.jpg` |
| Testimonial 2 (Lauren T) | `plaims-review-Priya.png` | PEOPLE-SWAP + copy fixed to "mom" | `noxis-review-2.jpg` |
| Testimonial 3 (Ron D) | `plaims-review-Tom.png` | PEOPLE-SWAP | `noxis-review-3.jpg` |

PEOPLE-SWAP prompt actually used for testimonial 1 (add the packshot as reference 2 and the "Reference image 2 …" sentence in future runs):
```
Use the reference only for the concept and framing; create different people. Candid smartphone selfie taken from the
driver's seat at night, a different man in his late 50s with a grey beard and a dark baseball cap, wearing a work jacket
and the black fit-over amber night driving glasses, slight smile, rainy windshield and street lights behind. Natural,
unpolished, real customer photo look, square. No text, no logos.
```
Job: `gpt-image-2-image-to-image`, 1:1, 2K, 10 credits each → 30 credits for the three.
