# Phase 3B — Product images (packshot + gallery remakes)

Goal: a product gallery for our brand that sells exactly like the competitor's — same images in the same order, same main idea, layout logic and claims — showing our product, with **no logo**, perfect spelling, and a clean packshot that every later image and ad reuses.

Read first: `00-operator-rules.md` §1 (claims) and §4 (product images), `tools-kie.md` (runner, pricing, prompt patterns).
Runs after the branding gate (needs BRAND, palette, MARKET from BRIEF.md). Uses the competitor media downloaded in Phase 1.

## Contents
1. Inputs, outputs, budget
2. Step 1 — Download the competitor gallery raw
3. Step 2 — Contact sheet
4. Step 3 — Classify every image (remake / skip)
5. Step 4 — Write PRODUCT_DESC and the claims list
6. Step 5 — Packshot first
7. Step 6 — One remake job per kept image
8. Step 7 — Run the batch
9. Step 8 — Review sheet
10. Step 9 — Fix rounds by editing, not regenerating
11. Step 10 — Final list in gallery order
12. Step 11 — Bundle thumbnails (optional)
13. Prompt templates (ready to fill)
14. Job JSON and builder example
15. Noxis run — what went wrong and the corrected first-time prompts

---

## 1. Inputs, outputs, budget

| Input | Where |
|---|---|
| Competitor gallery URLs (in order) | `02_competitor/page/capture.json` (gallery list) or `p.json` → `product.images[]` by `position` |
| Brand, palette hex, market language, mode | `BRIEF.md`, `01_branding/BRANDING.md` |
| Page copy deck (ratings, counts, offer wording) | returned by the copywriter / SECTION_SPEC copy inventory |
| Kie key + balance | env `KIE_API_KEY`; balance check in tools-kie §6 |

| Output | Path |
|---|---|
| Raw competitor gallery | `02_competitor/media/<comp>-product-NN.<ext>` (untouched) |
| Packshot | `03_product-images/<slug>-packshot.png` (1:1 2K) |
| Remakes | `03_product-images/<slug>-product-NN.png` (1:1 2K, NN = our gallery position) |
| Superseded versions | `03_product-images/superseded/<reason>/` |
| Review sheets | `03_product-images/_sheet*.jpg`, `03_product-images/_compare.jpg` |
| Builders, job JSONs, logs | `PRODUCT_DIR/scratch/` |

Budget: `10 × (1 packshot + N kept images) × 1.2`. Noxis: 1 + 5 = 60 credits (+ fixes). Check the balance before starting; if short, tell the operator before generating (tools-kie §6).

---

## 2. Step 1 — Download the competitor gallery raw
**Purpose:** work from the original full-resolution files, in gallery order, so classification and references are exact.
**Do:**
1. If the media agent already ran, verify the files exist; otherwise:
   `python -I "<SKILL>/scripts/fetch_media.py" --out "<PRODUCT_DIR>/02_competitor/media" --from-capture "<PRODUCT_DIR>/02_competitor/page/capture.json" --kinds images`
2. Make sure gallery files are named in gallery order (`<comp>-product-01…NN`). Shopify CDN originals: take `p.json` → `images[].src` (no `_800x` suffix, no `?width=`) — those are full size.
3. Note variant images separately (color swatches); they are not gallery slides unless the competitor shows them in the main gallery.
**Output:** `02_competitor/media/<comp>-product-NN.*`, raw, unmodified.
**Done when:** the file count equals the competitor's gallery count and the order matches the live page.
**Pitfalls:** thumbnails instead of originals (check pixel size ≥1000 px); duplicate downloads from both JSON and HTML (dedupe by md5); never edit or re-encode the raw files — they are the evidence and the references.

## 3. Step 2 — Contact sheet
**Purpose:** see the whole gallery at once, the way the shopper does, before deciding anything.
**Do:** `python -I "<SKILL>/scripts/contact_sheet.py" "<PRODUCT_DIR>/02_competitor/media/<comp>-product-*" --out "<PRODUCT_DIR>/03_product-images/_competitor.jpg"` and Read the sheet; Read individual originals for small text.
**Output:** `_competitor.jpg`.
**Done when:** you can describe each image's job in one line.

## 4. Step 3 — Classify every image (remake / skip)
**Purpose:** decide per image what to make, and capture every on-image string verbatim (claims live there).
**Do:** fill this table (keep it in your return and in `scratch/gallery_plan.md` or the job builder comments):

| # | File | Type | Main idea (one line) | On-image text (verbatim, reading order) | People | Decision |
|---|---|---|---|---|---|---|

Types and how to treat them:

| Type | Recognise it by | Decision |
|---|---|---|
| Hero infographic | product large + callout arrows, often an inset (before/after) and an offer banner (free case) | remake |
| Benefits | big claim headline + product + 3–5 callout boxes with checks | remake |
| Comparison | ours vs theirs / us vs cheap alternative, checks vs crosses, "VS" badge | remake (rival = generic product, labels "OURS/THEIRS" or as competitor wrote them) |
| Lifestyle | person using the product + headline + checklist/benefit panel | remake with a **different person** (same age, gender, setting) |
| Testimonial | quote + stars + customer photo + rating strip | remake: different person, quote re-voiced to fit them, rating/count as on our page |
| Plain packshot / what's in the box / specs | product on white, contents, dimensions | remake from our packshot (specs/dimensions verbatim) |
| Brand-specific | only makes sense for the competitor: anti-replica notice ("buy only from plaims.com"), "as seen on" with their name, founder story with their name, close-up of their branded packaging | **skip** (or remake without brand only if the idea still works for us) |

**Output:** the plan table; the list of kept images = our gallery order (competitor order minus skips).
**Done when:** every image has a decision and every text line is transcribed, typos noted (e.g. "Peripheral vison" → write "Peripheral vision").
**Pitfalls:** missing small text in corners (footers like "30-Days Money Back Guarantee", badges like "Polarized") — zoom in; classifying a claim as "decoration" — see Step 4.

> **Noxis run:** 6 Plaims images → 01 hero infographic, 02 benefits, 03 comparison, 04 lifestyle, 05 testimonial, 06 **skipped** ("IMPORTANT NOTICE … Make sure to buy only from plaims.com").

## 5. Step 4 — Write PRODUCT_DESC and the claims list
**Purpose:** one product sentence keeps the product identical across every prompt; one claims list keeps claims identical across images, page and ads.
**Do:**
1. `PRODUCT_DESC` = one sentence: product type, shape, colors, materials, distinctive parts. No brand, no print. Reuse it verbatim everywhere (gallery, page images, ads).
2. Claims list = every on-image line that states efficacy, a number/percentage, a condition or audience, a comparison, a technology name, a guarantee, a rating/review count, a gift/offer, "World's first"/"#1"/"doctor-recommended". **When unsure whether a line is a claim, treat it as one.**
3. Text policy for remakes:
   - **Claims: verbatim, full strength.** No softening, no rewording, no disclaimers (operator rule 1).
   - **Mode A (default): all on-image text verbatim** except: competitor brand name (drop it, or use "OURS" in comparisons), obvious typos (correct them), testimonial quotes (re-voice to fit the new person, same meaning and strength), ratings/review counts (use exactly the figure in our page copy deck, which mirrors the competitor's, so page and images agree).
   - Mode B: claims verbatim; non-claim wording may be original.
   - Keep the **same text structure**: same number of callouts, same headline/sub/footer roles, same emphasis (highlighted word stays highlighted).
**Output:** PRODUCT_DESC + claims list in the builder.
**Pitfalls:** "improving" a claim into something safer — this caused a full fix round in the Noxis run.

> **Noxis run:** `PRODUCT_DESC` = "black wraparound fit-over night driving glasses with amber/orange polarized lenses and amber side shields". Claims kept verbatim: "Reduces Nighttime Glare By 85%", "Built with Glare Cut Technology", "Perfect brightness for sensitive eyes", "Full peripheral protection", "Designed for LED headlights", "Terrible for LED headlights", "Cataracts", "Astigmatism", "Fit Over Prescription Glasses", "30-Days Money Back Guarantee", "Includes FREE Glasses Case", "Rated 4.8/5 by …".

## 6. Step 5 — Packshot first
**Purpose:** a clean, text-free product image is the product reference for every remake and every ad. Making it first lets the ad stream start in parallel and keeps the product identical everywhere.
**Do:**
1. Pick the reference: the competitor image (or supplier photo) with the largest, sharpest, least-occluded view of the product — usually the hero infographic or a plain product slide.
2. Fill the PACKSHOT template (§13.1); job: `gpt-image-2-5-sunburst-image-to-image`, 1:1, 2K, name `<slug>-packshot`. For a transparent PNG, use `"resolution": "1K", "background": "transparent"` instead (6 credits).
3. Run (Step 7 command) into `03_product-images/`, then Read the result at full size.
4. Check: exact shape and parts (compare side by side with the reference), colors, **no text, print or logo on the product**, pure white background, soft shadow, nothing else in frame.
5. If a print or artefact appears, KEEP-EDIT it away ("Remove any text or print from the frame; keep everything else identical") rather than regenerating.
**Output:** `03_product-images/<slug>-packshot.png`. Tell the master it exists (the ad stream waits for it).
**Done when:** a stranger could not tell it apart from the real product, and there is no text on it.
**Pitfalls:** asking for "small <brand> print on the temple" — GPT Image renders small prints garbled; packaging with the competitor's brand (for boxed products: either a plain unbranded box, or our own packaging only if BRANDING.md defines one).

> **Noxis run:** the packshot was made *last*, from our remake 01, with "small 'noxis' print on the temple" → the print came out as "noɓıs". The ad prompts then had to say "no text or logo on the frame". Make it first, text-free.

## 7. Step 6 — One remake job per kept image
**Purpose:** recreate each image's selling idea with our product, without copying pixels, and with claims intact.
**Do:** for each kept image write one job:
- References in this order: `[competitor image (concept), our packshot (product)]`.
- Prompt = CONCEPT-REMAKE (§13.2) + an image-specific `DESC` that states: canvas zones (in %), background color/hex, each text line **in quotes** with its position, style and emphasis, icons (green checks, red crosses, arrows), product placement/angle/size, people (new person described precisely), insets/banners.
- Same aspect ratio as the competitor image (almost always 1:1) at 2K; name `<slug>-product-NN` where NN = our gallery position.
- No brand logo/wordmark on the image, no print on the product, no competitor name.
**Output:** `scratch/jobs_gallery.json` (via a builder, §14).
**Done when:** every kept image has a job and every text line from Step 3 appears in quotes in its DESC (or is deliberately dropped because it is brand-only).
**Pitfalls:** a generic STYLE/BRAND block that adds a wordmark (the Noxis builder did — rejected: "plaims don't have their logo on them and ours lose space because of logo you added"); vague DESC ("an infographic about benefits") → the model invents weaker text.

## 8. Step 7 — Run the batch
**Do:**
```
python -I "<SKILL>/scripts/kie_jobs.py" "<PRODUCT_DIR>/scratch/jobs_gallery.json" "<PRODUCT_DIR>/03_product-images"  | tee "<PRODUCT_DIR>/scratch/run_gallery.log"
```
(PowerShell: `| Tee-Object -FilePath …`.) Packshot and remakes may share one batch only if the remakes don't attach the packshot; otherwise run the packshot batch first, then the remakes.
**Done when:** every job printed `saved`; anything `FAILED`/`timed out` handled per tools-kie §12–13.

## 9. Step 8 — Review sheet
**Purpose:** catch every problem in one pass, before the operator does.
**Do:**
1. `python -I "<SKILL>/scripts/contact_sheet.py" "<PRODUCT_DIR>/03_product-images/<slug>-*.png" --out "<PRODUCT_DIR>/03_product-images/_sheet.jpg"`; also build a competitor-vs-ours comparison (pass files in pairs: `<comp>-product-01 <slug>-product-01 …` → `_compare.jpg`). Read both, then Read any image whose text is too small to verify on the sheet.
2. Checklist per image:
   - same main idea and layout logic as the competitor image;
   - every claim present **verbatim**; text structure the same; spelling correct (market language);
   - **no logo/wordmark**, no competitor name, no print on the product;
   - product matches the packshot (shape, colors, parts);
   - people are different from the competitor's and match age/gender/setting;
   - text readable at gallery-thumbnail size (mobile).
3. Write a fix list: `image | problem | fix type (KEEP-EDIT / NO-LOGO / regenerate) | exact new text`.
**Done when:** the fix list is empty, or every item has a planned fix.

## 10. Step 9 — Fix rounds by editing, not regenerating
**Purpose:** converge fast and keep what is already right.
**Do:**
1. Pick the fix type:
   - **Text-only** (wrong word, softened claim, typo, wrong number) → KEEP-EDIT (§13.3) on the existing image, listing every change as `Change "<old>" to "<new>"` and the lines to keep.
   - **Remove an element** (logo, wordmark, stray badge) → NO-LOGO (§13.4) with reflow so no empty gap remains.
   - **Composition or product wrong** → regenerate the remake job with a corrected DESC.
2. Before running, move each current version to `03_product-images/superseded/<reason>/` (e.g. `softened/`, `with-logo/`, `round1/`) and point the edit job's `upload.files` at that moved copy — the runner overwrites same-name files in the output folder.
3. Batch all fixes of one round into one job file (`scratch/jobs_gallery_fix1.json`), run into `03_product-images/`, re-sheet, re-check.
**Output:** corrected images; superseded versions kept (nothing approved is ever lost).
**Done when:** the checklist passes on every image.
**Pitfalls:** regenerating from scratch for a text fix (new composition = new problems); forgetting to move the old file first (it gets overwritten and the history is lost); editing an edited image many times — after 2 failed edits of the same image, regenerate.

## 11. Step 10 — Final list in gallery order
**Do:** produce the final mapping (return it to the master; it goes into DELIVERY.md):

| Gallery position | File | Source competitor image | What it shows | Status |
|---|---|---|---|---|
| 1 | `<slug>-product-01.png` | `<comp>-product-01` | hero infographic | final |

- Order = competitor order minus skipped images. In Mode A, don't add extra slides; the packshot goes into the gallery only if the competitor has a plain product slide at that position (it is mainly the reference for ads and bundles).
- Shopify accepts the 2K PNGs as-is (≤20 MB). Uploading media to the product is the operator's job unless a product-upload tool is available — list it in the to-dos.
**Done when:** the master has the table and the contact sheet path.

## 12. Step 11 — Bundle thumbnails (optional)
**When:** the buy box shows bundle/quantity cards with product images (1 / 2 / 3 units), per SECTION_SPEC.
**Do:** BUNDLE template (§13.5) with the packshot as reference; one job per tier; 1:1 1K (6 credits each); names `<slug>-bundle-1`, `-2`, `-3`; output `03_product-images/`. Theme-ready JPG copies (≤600 px) go to `04_page-images/theme/` for the builder.
> **Ceriva run:** `jobs_bundles.json` made 1-, 2- and 4-box packshots from the product box reference, "exactly TWO identical boxes standing upright side by side, slightly overlapping … No other objects, no text, no badges".

---

## 13. Prompt templates (ready to fill)

### 13.1 PACKSHOT
```
Isolate ONLY the product from the reference and create a clean e-commerce packshot: the exact same <PRODUCT_DESC>,
<three-quarter front view>, centered, filling about 75% of the width, on a pure white #FFFFFF background with a soft
natural contact shadow. Remove all text, arrows, insets, banners, badges, people and accessories (<e.g. the case>).
No text, print or logo anywhere on the product. Photorealistic studio product photo, sharp, accurate materials and
reflections. Square.
```

### 13.2 CONCEPT-REMAKE (+ DESC per type)
```
Reference image 1 shows the concept only: recreate it as a NEW, original image with the same main idea, layout logic,
text structure and color mood (<palette, e.g. amber #FFB800 accents, black and white>), but different composition
details, different photography and redrawn graphics. Reference image 2 is our exact product: <PRODUCT_DESC>; reproduce
it faithfully wherever the product appears, with no text or logo on it. Do not show any brand name, wordmark or logo
anywhere on the image. All text crisp, large, correctly spelled <US English>, exactly as written in quotes.
<DESC>
```
DESC skeletons:
- **Hero infographic:** "Square hero infographic on a soft white background: the product large in the center, three-quarter view. Callout labels with hand-drawn arrows: top-left \"<text>\", bottom-left \"<text>\", bottom-right \"<text>\". Top-right: a two-panel inset of <scene>, labeled \"Before\" (<problem look>) and \"After\" (<solution look>). Bottom <color> banner with bold black text \"<offer text>\" and a small <gift item> at the right."
- **Benefits:** "Square benefits infographic on a <color> background: bold black headline \"<claim headline>\" across the top. The product in the center inside a thin <color> circle; four white rounded callout boxes with green check icons around it: top-left \"<text>\", top-right \"<text>\", bottom-left \"<text>\", bottom-right \"<text>\"."
- **Comparison:** "Square comparison graphic split diagonally: left half <brand color> with three green-check pills at the top \"<text>\", \"<text>\", \"<text>\", our product below and the label \"OURS\"; right half light grey labeled \"THEIRS\" showing a generic <cheap alternative>, with three red-cross pills \"<text>\", \"<text>\", \"<text>\". A \"VS\" circle on the diagonal. Small footer text bottom-left \"<guarantee text>\" with a shield icon."
- **Lifestyle:** "Square lifestyle ad: top 65% a candid photo of <new person: age, gender, hair, clothing> <action> wearing/using the product, <setting and light>. White headline on the right \"<headline>\" with \"<word>\" highlighted on a <color> box. Bottom 35% <color> panel with three black outlined check icons and bold text \"<item>\", \"<item>\", \"<item>\", the product at the right of the panel <+ small badge \"<text>\" if the original has one>."
- **Testimonial:** "Square testimonial ad: left half a bold black quote \"<re-voiced quote>\" with five gold stars underneath and the product below. Right half a rounded-corner photo of <new person> <pose> wearing the product. Bottom <color> strip with bold text \"<rating text as on our page>\"."

### 13.3 KEEP-EDIT
```
Edit this exact image. Keep everything identical (layout, product, colors, photography, typography style) and change
ONLY the text described below. All text crisp and correctly spelled.
Change "<old>" to "<new>". Change "<old>" to "<new>", with "<word>" highlighted in <color>. Keep "<text>" as is.
```

### 13.4 NO-LOGO
```
Edit this exact image. Remove the "<brand>" wordmark/logo text entirely, including any brand print on the product.
Recompose so the freed space is used: enlarge and re-center the headline, product and other elements to fill the
canvas naturally, with no empty gap where the logo was. Keep every other text EXACTLY the same word for word, same
colors, same product, same style. All text crisp and correctly spelled. Square.
```

### 13.5 BUNDLE
```
Use the reference ONLY to copy the exact product: <PRODUCT_DESC>. Create a clean e-commerce packshot: exactly <TWO>
identical <pairs/boxes/units> <side by side, slightly overlapping, the front one a bit in front>, slight three-quarter
front view, centered, together filling about 70% of the frame width. Pure white #FFFFFF seamless background, soft
natural contact shadows, bright even studio lighting. No other objects, no text, no badges, no logo. Square image.
```

## 14. Job JSON and builder example

Builder (`scratch/mk_gallery_jobs.py`) — the pattern used in the Noxis run, with the rules above applied:
```python
import json, sys
M = "G:/Ecom/Products/Noxis/02_competitor/media/"
PACK = "G:/Ecom/Products/Noxis/03_product-images/noxis-packshot.png"
PRODUCT_DESC = ("black wraparound fit-over night driving glasses with amber/orange polarized lenses "
                "and amber side shields")
BASE = ("Reference image 1 shows the concept only: recreate it as a NEW, original image with the same main idea, "
        "layout logic, text structure and color mood (amber #FFB800 accents, black and white), but different "
        "composition details, different photography and redrawn graphics. Reference image 2 is our exact product: "
        + PRODUCT_DESC + "; reproduce it faithfully wherever the product appears, with no text or logo on it. "
        "Do not show any brand name, wordmark or logo anywhere on the image. "
        "All text crisp, large, correctly spelled US English, exactly as written in quotes. ")
IMAGES = [  # (our name, competitor file, DESC)
    ("noxis-product-02", "plaims-product-02.png",
     "Square benefits infographic on a warm cream background: bold black headline \"Reduces Nighttime Glare By 85%\" "
     "across the top. The glasses in the center inside a thin amber circle, four white rounded callout boxes with "
     "green check icons: top-left \"Built with Glare Cut Technology\", top-right \"Perfect brightness for sensitive "
     "eyes\", bottom-left \"Full peripheral protection\", bottom-right \"Fits over normal glasses\"."),
    # … one tuple per kept image
]
jobs = [{"name": n, "model": "gpt-image-2-5-sunburst-image-to-image",
         "upload": {"field": "input_urls", "files": [M + ref, PACK]},
         "input": {"prompt": BASE + desc, "aspect_ratio": "1:1", "resolution": "2K"}} for n, ref, desc in IMAGES]
json.dump(jobs, open(sys.argv[1], "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(len(jobs), "jobs")
```
Run: `python -I scratch/mk_gallery_jobs.py scratch/jobs_gallery.json` then the runner (Step 7).

Resulting job entry:
```json
{"name": "noxis-product-02", "model": "gpt-image-2-5-sunburst-image-to-image",
 "upload": {"field": "input_urls", "files": ["G:/Ecom/Products/Noxis/02_competitor/media/plaims-product-02.png",
                                            "G:/Ecom/Products/Noxis/03_product-images/noxis-packshot.png"]},
 "input": {"prompt": "Reference image 1 shows the concept only: … Square benefits infographic … \"Reduces Nighttime Glare By 85%\" …",
           "aspect_ratio": "1:1", "resolution": "2K"}}
```

Fix-round job (KEEP-EDIT, uploading the moved copy):
```json
{"name": "noxis-product-04", "model": "gpt-image-2-5-sunburst-image-to-image",
 "upload": {"field": "input_urls", "files": ["G:/Ecom/Products/Noxis/03_product-images/superseded/softened/noxis-product-04.png"]},
 "input": {"prompt": "Edit this exact image. Keep everything identical (layout, product, colors, photography, typography style) and change ONLY the text described below. All text crisp and correctly spelled. Change the headline to \"Drive Confidently At Night With Glare-Free Vision\", with \"Glare-Free\" highlighted in amber. Change the three check items in the bottom amber panel to \"Cataracts\", \"Astigmatism\", \"Fit Over Prescription Glasses\".",
           "aspect_ratio": "1:1", "resolution": "2K"}}
```

## 15. Noxis run — what went wrong and the corrected first-time prompts

**What happened (130 credits for 5 images instead of 50):**
1. Round 1 builder had a `BRAND` block ("write \"noxis\" in a bold, rounded lowercase sans-serif wordmark") and paraphrased the text: "Cuts Headlight Glare at Night" instead of "Reduces Nighttime Glare By 85%"; "Rainy nights / Sensitive eyes" instead of "Cataracts / Astigmatism"; "CHEAP TINTS" instead of "THEIRS".
2. Operator: *"Never told you to do this, revert any claims adjustments you made. every claims we have are validated and running."* → KEEP-EDIT on 02/03/04 restoring the exact text (old files → `superseded/softened/`).
3. Operator: *"remake product images, plaims don't have their logo on them and ours lose space because of logo you added"* → NO-LOGO edit with reflow on all 5 (old files → `superseded/with-logo/`).
4. Final accepted set: logo-free, claims verbatim, product consistent; the competitor's anti-replica slide skipped.

**Corrected first-time DESCs (use as the quality bar):**
- **01 hero:** "Square hero infographic on a soft white background: the glasses large in the center, three-quarter view. Callout labels with hand-drawn arrows: top-left \"Fits over prescription glasses\", bottom-left \"Engineered for night vision clarity\", bottom-right \"Peripheral vision without glare\". Top-right: a two-panel inset of a night city street, labeled \"Before\" (harsh white glare) and \"After\" (warm, clear amber view). Bottom amber banner with bold black text \"Includes FREE Glasses Case\" and a small black zip case at the right." (typo "vison" corrected)
- **03 comparison:** "Square comparison graphic split diagonally: left half amber with three green-check white pills at the top \"Designed for LED headlights\", \"Perfect for sensitive eyes\", \"Fits over prescription glasses\", our glasses below and the bold label \"OURS\"; right half light grey labeled \"THEIRS\" showing generic flimsy yellow-lens sport glasses, with three red-cross pills \"Terrible for LED headlights\", \"Too bright for sensitive eyes\", \"Poor fit over prescriptions\". A \"VS\" circle on the diagonal. Small footer bottom-left \"30-Days Money Back Guarantee\"."
- **04 lifestyle:** "Square lifestyle ad: top 65% a candid photo of a smiling woman in her late 50s with shoulder-length brown hair and a beige sweater driving at dusk, wearing the glasses, city lights outside. White headline on the right \"Drive Confidently At Night With Glare-Free Vision\" with \"Glare-Free\" on an amber box. Bottom 35% amber panel with three black outlined check icons and bold text \"Cataracts\", \"Astigmatism\", \"Fit Over Prescription Glasses\", the glasses at the right of the panel and a small outlined pill \"Polarized\"."
- **05 testimonial:** "Square testimonial ad: left half the bold black quote \"I finally drive home after dark again\" with five gold stars and the glasses below. Right half a rounded-corner photo of a friendly man in his early 60s with short grey hair and stubble, navy fleece, in the driver's seat, adjusting the glasses. Bottom amber strip with bold text \"Rated 4.8/5 by 1,300+ drivers\"." (rating line = exactly the figure in our page copy, which mirrors Plaims' "Rated 4.8/5 by 1,356+ happy drivers", so page and image agree)
