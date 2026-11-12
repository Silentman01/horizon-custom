# Phase 3D2 — Ad creatives (top-5 recreations + 20 pattern ads)

Goal: 25 launch-ready Meta image ads for our brand: the competitor's 5 best-ranked creatives remade with our product, plus 20 new ads built on the formats the competitor's top 30 prove work. Every ad maps to one Step Alpha angle card, validated (`V#`) or opportunity (`O#`), so the mix tests the angles the competitor proved with money and the ones it misses. Every ad shows our exact product (packshot attached), carries the claims at full strength, and never shows the competitor's name.

Read first: `00-operator-rules.md` §1 (claims) and §7 (ads); `tools-kie.md` (runner, FIDELITY-97 / PATTERN-AD / KEEP-EDIT patterns, 4:5 = 1K).
Native ad formats (Reddit-style, editorial, lo-fi) get specific treatment when the competitor runs them: [22 §8](references/22-native-ads-and-advertorials.md#8-phase-3--native-ads-in-the-creative-mix-extends-d2).
Video ads are a separate workflow: `14-video-ads.md`.
Starts after Alpha: the Step Alpha gate has passed (`00_alpha/ALPHA_DOSSIER.md`) and `03_product-images/<slug>-packshot.png` exists (05 Step 5).

**Inputs from Step Alpha** (dossier sections and what they change):
| Dossier section | Use |
|---|---|
| 3.1 Angle Cards (1.11 validated + 2.8 opportunity) | every variant gets one angle card ID; the variant mix covers validated and opportunity cards (§1b) |
| 3.3 Hook Library | the hook of every variant headline (the hook of the source ad, or a template of the card) |
| 3.5 Customer Language Bank (+ 2.6) | hook-ready and headline-ready phrases in headlines; objection-ready phrases in objection ads |
| 1.7 Ad Inventory | angle and avatar of each ranked competitor ad (`00_alpha/ad_inventory.json`) |
| 1.9 Ad Copy Patterns · cross-ad patterns (`00_alpha/analysis1/1.2_patterns.md`, `1.2_static_ads.md`) | formats, hook types, proof types, CTA patterns for the selection matrix |
| 3.2 Avatar Cards | the people shown in each ad (its card's avatar) |

## Contents
1. Inputs, outputs, budget
2. Step 1 — Load the inputs and the claims bank
3. Step 2 — Top 5: prepare each recreation
4. Step 3 — Top 5: build, run, compare
5. Step 4 — Pattern ads: selection matrix
6. Step 5 — Pattern ads: one detailed spec per ad
7. Step 6 — Run the 20
8. Step 7 — Review via contact sheets
9. Step 8 — Fix list and fix round
10. Step 9 — Deliver
11. Spec checklist and anti-patterns
12. Noxis run — worked examples

---

## 1. Inputs, outputs, budget

| Input | Where |
|---|---|
| Top-30 ranked competitor creatives | `05_ads/competitor/NN_<adid>.jpg` (NN = rank), `ranking.json` (days, copies, captions) |
| Angle cards, hooks, language, per-ad angle/avatar, patterns | `00_alpha/ALPHA_DOSSIER.md` (3.1, 3.3, 3.5, 1.7, 1.9, 3.2) + `00_alpha/analysis1/1.2_static_ads.md` |
| Packshot | `03_product-images/<slug>-packshot.png` |
| Brand, palette, market language | `BRIEF.md` |
| Claims bank | page copy + gallery claims list (05 Step 4) + claims in the competitor ads |

| Output | Path |
|---|---|
| 25 ads | `05_ads/generated/ad-NN-<slug>.png` (01–05 recreations in rank order, 06–25 pattern ads) |
| Contact sheets | `05_ads/generated/_top5_compare.jpg`, `_sheet1.jpg`, `_sheet2.jpg` |
| Replaced versions | `05_ads/generated/archive/v<N>_<reason>/` |
| Builders, job JSONs, logs | `PRODUCT_DIR/scratch/` (`mk_ads_top5.py`, `jobs_ads_top5.json`, `mk_ads_20.py`, `jobs_ads_20.json`) |
| Ad map table | in the return → master adds to DELIVERY.md |

Budget: top 5 at 10 each if their ratio is 1:1/9:16/16:9 (2K) or 6 each if 4:5 (1K) → ≤50; 20 pattern ads × 6 (4:5 1K) = 120; fixes ~10–20%. **≈170–200 credits.** Check the balance first (tools-kie §6); if short, tell the operator and run top 5 first, then as many pattern ads as the balance allows, in matrix priority order.

**File naming:** `ad-NN-<slug>` — NN two digits, slug 2–5 kebab-case words naming the hook or format (`ad-01-ours-vs-theirs`, `ad-07-rainy-night-poster`). The job `name` is the file name without extension.

---

## 1b. Variants gate (before ANY generation — operator rule §7)
For all 25 ads (top 5 included) write `05_ads/AD_VARIANTS.md`, one row per ad:
`ad-NN | angle card | source rank | original headline (verbatim) | our variant headline | hook (3.3 #) | original design | our design variant`.
- **Angle card:** every variant maps to one card from 3.1, a validated `V#` or an opportunity `O#`. A remade ad keeps the card of its source ad (1.7: the ad's angle → its card). Never a variant without a card, never a card that isn't in 3.1 (killed angles stay out).
- **Variant mix:** every `V#` card has at least one ad; every `O#` card has at least one ad and the highest-potential `O#` cards two; at least 6 of the 20 pattern ads go to `O#` cards. An opportunity ad takes a format the competitor proved (1.9 / top-30 ranks) and the hook, avatar and promise of its `O#` card: proven format × new angle.
- **Hooks from the Hook Library (3.3):** a remade ad keeps its source ad's hook type; an `O#` ad uses a hook template from its card (HOOK TEMPLATES) or 3.3. Write the hook in customer words from the language bank (3.5 hook-ready / headline-ready phrases) where one fits.
- Headline variant: same hook mechanism, structure, length and claim/number strength; different words. Never identical, never softened.
- Design variant: same format, zones, type style, palette logic; different scene, background, props, people, angle (≈80–90% similar).
- Top 5 use FIDELITY-VARIANT (tools-kie) with the variant text instead of word-for-word text.
Stop and present the table to the operator. After approval, run Steps 1–9 with the approved text and do not stop again until delivery (except credit shortage).

## 2. Step 1 — Load the inputs and the claims bank
**Purpose:** everything the prompts need in one place, so specs are precise and claims consistent.
**Do:**
1. Read the dossier sections listed above (3.1, 3.3, 3.5, 1.7, 1.9, 3.2) and the approved AD_VARIANTS.md, open the top-30 sheet(s), and Read the top-5 originals at full size (their layout, text and fonts come from the image itself; it is reference image 1 of the prompt).
2. Note each top-5 creative's pixel size → aspect ratio (1080×1080 → 1:1; 1856×2304 or 1080×1350 → 4:5; 1080×1920 → 9:16).
3. Build the **claims bank**: every claim the competitor uses in ads, page and gallery (verbatim), plus our offer facts from the page (guarantee length, free gift, rating line, shipping threshold). Pattern-ad text may only use claims from this bank — at the same strength. Don't invent new statistics; a number on an ad must come from the competitor's materials (mirrored) or our page.
4. Note the color system and type styles of the top 30 from the sheets and the cross-ad patterns (e.g. black/white + one accent; cold blue = problem, warm amber = solution).
5. Note per ad its angle card and that card's avatar (3.2): the people in the ad are that avatar.
**Output:** notes in the builder file header (claims bank, palette, PRODUCT_DESC from 05).
**Done when:** you can write any ad's text without opening the dossier again.

## 3. Step 2 — Top 5: prepare each recreation
**Purpose:** the 5 best-ranked creatives (Top rank by impressions) are proven; reproduce them almost exactly with our product.
**Do,** for each of ranks 1–5:
1. References in this order: `[competitor ad file, our packshot]`.
2. Prompt = FIDELITY-97 (tools-kie §11) + an `EXTRA` line covering only what must differ:
   - **People:** "The <n> customer photos must show <n> DIFFERENT people (similar ages, genders and settings as the reference) wearing our <product>." Their profile is the avatar of the ad's angle card (3.2).
   - **Rival product** in comparisons: "The 'Theirs' side shows a different, generic <cheap alternative> (not identical to the reference photo)."
   - **Competitor name** in the text: replace with our brand only where the format needs a name (letter sign-off, "A MESSAGE FROM <BRAND>"); remove where it is a logo.
   - **Typos** in the original: give the corrected string ("write 'Peripheral vision' (correct spelling)").
   - **POV / through-the-lens** shots: say what is seen through our lenses.
3. Keep **everything else word for word**, including every claim ("Designed for cataract patients", "World's First") — no softening, no added disclaimers.
4. Aspect ratio = the original's; resolution 2K, except 4:5/5:4 → 1K.
**Output:** five `(name, file, extra)` tuples in `scratch/mk_ads_top5.py`.
**Pitfalls:** transcribing and "tidying" the text (changes claims); forgetting the packshot (product drifts to the competitor's exact photo); keeping the competitor's customer faces.

## 4. Step 3 — Top 5: build, run, compare
**Do:**
```
python -I scratch/mk_ads_top5.py scratch/jobs_ads_top5.json
python -I "<SKILL>/scripts/kie_jobs.py" scratch/jobs_ads_top5.json "<PRODUCT_DIR>/05_ads/generated" | tee scratch/run_ads_top5.log
python -I "<SKILL>/scripts/contact_sheet.py" <comp 01> <ad-01> <comp 02> <ad-02> … --out "<PRODUCT_DIR>/05_ads/generated/_top5_compare.jpg"
```
Read the comparison (and full-size images for small text).
**Done when:** each recreation matches layout, proportions, colors, typography and text of its original; the product is ours (packshot) with nothing printed on it; people are new; no competitor name anywhere.

## 5. Step 4 — Pattern ads: selection matrix
**Purpose:** 20 ads that test the competitor's proven formats and hooks broadly, not 20 variants of one idea.
**Do:**
1. From the cross-ad patterns (1.9, `1.2_patterns.md`: dominant formats and hook types) and the top-30 sheets, list **formats** (rows) and **hook families** from the Hook Library 3.3 (columns). Typical formats: comparison table, POV through the lens, big-type "[SITUATION] <PRODUCT>" poster with "+" bullets, lifestyle + benefit panel, native lo-fi (notes/planner, whiteboard, letter, newspaper advertorial), numbered list/listicle, stat poster, timeline, split before/after, diagram/anatomy, still life, UGC selfie. Typical hooks: condition/audience, situation (rain, mirror glare, tired eyes), blame-shift ("it isn't your eyes"), category enemy (cheap alternative), identity/age, couple/gift (2-pack), social proof.
2. Default selection = **one ad per competitor creative from rank 6 downward**, adapted (new headline wording on the same hook mechanism, new scene, same format mechanics), skipping near-duplicates and formats already covered by the top 5, until 20 ads.
3. Check coverage with the matrix: every format the competitor runs ≥2 times appears at least once (its winning format 2–3 times with different hooks); every hook family appears at least once; mix of visual styles (photo, typographic, native lo-fi, diagram). Then check the angle mix of §1b (every `V#` and `O#` card covered, at least 6 `O#` ads). Swap picks until both hold.

**Native ad formats:** when the competitor's top 30 includes native-style ads (Reddit posts, article thumbnails, handwritten notes, chat screenshots, editorial layouts — see [22 §2](references/22-native-ads-and-advertorials.md#2-what-native-ads-are)), these are a first-class format row in the matrix. If the competitor runs ≥ 2 native ads in the top 30, at least one native format appears in the top-5 remakes (if it's in the top 5) and at least 2 in the pattern ads. Native ads that the competitor sends to an advertorial page also send ours to our advertorial (A5); those that go direct to the product page stay direct.
4. Order the 20 by the competitor rank they derive from (priority if credits run short); keep at least one ad per `O#` card inside the first 15.
**Output:** a table `ad-NN | angle card | source rank | format | hook | headline` (part of your return).
**Done when:** 20 rows, matrix and angle mix covered, no two ads with the same format + hook + angle.

## 6. Step 5 — Pattern ads: one detailed spec per ad
**Purpose:** GPT Image 2.5 follows precise specs well; vague specs produce generic ads with weak text.
**Do:** for each ad write one paragraph (50–150 words) after the PATTERN-AD base block, containing:
- **Format** in a few words ("Big-type poster on a light grey-white gradient background").
- **Layout zones in %** ("Top 65%: … Bottom 35%: …"), or element positions (top / center / bottom-left).
- **All text verbatim in quotes**, line breaks shown with " / ", emphasis stated ("the word Glare in amber on a black box"). Large, legible at feed size.
- **Colors** (hex for brand colors; color grade: "cold blue grade" for problem, "warm amber" for solution).
- **Fonts** by style: "Poppins Bold Title Case", "ultra-condensed all-caps like Anton", "extra-bold sans sentence case", "handwritten navy pen", "serif masthead".
- **People:** age, gender, hair, clothing, expression, action, setting, matching the avatar of the ad's angle card (3.2), or "no people".
- **Product placement:** where, how big, angle, effects (rain droplets, reflection, spotlight), "worn by", "held up to the windshield".
- **Brand name only where the format needs it** (letter title/signature, CTA button "TRY <BRAND>"); never on the product, never the competitor's name. Fake publication names in advertorials are invented (not our brand, not a real outlet).
- Labels like "Simulated view" only if the competitor's version of that format carries one.
- Settings: 4:5, 1K, packshot attached (`upload.files: [PACK]`).

**Native ad specs:** for a native-format ad, also specify: the platform it imitates (Reddit, Twitter, article, note, etc.); the UI chrome (fake upvotes, timestamps, usernames — never real platform trademarks); the "organic content" (post title, comment text, article headline); where the product appears and how subtle it is; and the hook from the angle card / hook library. Native ads should look lo-fi and organic — over-designing defeats the purpose. See [22 §8](references/22-native-ads-and-advertorials.md#8-phase-3--native-ads-in-the-creative-mix-extends-d2).

**Output:** `scratch/mk_ads_20.py` → `scratch/jobs_ads_20.json`.
**Done when:** every ad has a full spec and every quoted claim exists in the claims bank at the same strength.

## 7. Step 6 — Run the 20
```
python -I scratch/mk_ads_20.py scratch/jobs_ads_20.json
python -I "<SKILL>/scripts/kie_jobs.py" scratch/jobs_ads_20.json "<PRODUCT_DIR>/05_ads/generated" | tee scratch/run_ads_20.log
```
The top-5 and pattern batches are independent; run them in parallel if both are ready. 20 jobs ≈ 2–4 min.

## 8. Step 7 — Review via contact sheets
**Do:** `python -I "<SKILL>/scripts/contact_sheet.py" "<PRODUCT_DIR>/05_ads/generated/ad-*.png" --out "<PRODUCT_DIR>/05_ads/generated/_sheet.jpg"` (10 per sheet reads well) and Read every sheet; open full size any ad with small text.
Checklist per ad:
- product = packshot (shape, colors, parts), **no text/logo on the product**;
- every string spelled correctly and identical to the spec; claims verbatim;
- no competitor name or logo; our brand only where intended;
- hands, faces, glasses-on-face geometry natural; no duplicated objects;
- headline legible at thumbnail size; layout matches the spec zones;
- top 5: side by side with the original ≈97%.
**Output:** fix list `ad | problem | fix type | exact text/spec change`.

## 9. Step 8 — Fix list and fix round
- Text wrong / small artefact / stray print → KEEP-EDIT on the existing ad.
- Composition, product or person wrong → regenerate with the corrected spec (packshot still attached).
- Move each old version to `05_ads/generated/archive/v<N>_<reason>/` first and upload from there (the runner overwrites same-name files).
- One job file per round (`scratch/jobs_ads_fix1.json`); re-sheet; re-check. After two failed edits on one ad, regenerate.
**Done when:** the checklist passes for all 25, or remaining minor flaws are listed honestly in the return (e.g. "ad-25 body text is decorative filler").

## 10. Step 9 — Deliver
Return to the master: the ad map table (`ad-NN | angle card | source rank | format | hook | on-image headline | landing page | file`), contact sheet paths, credits spent, flaws left. Landing page = advertorial URL for ads in the advertorial funnel, product page for direct ads (see AD_VARIANTS.md and [22 §9](references/22-native-ads-and-advertorials.md#9-ad-copy-for-the-advertorial-funnel-extends-e)); when no advertorial funnel exists, the SECTION_SPEC's landing decision gives the ad's angle card (the main product page unless an angle landing page exists). Each ad's copy is the copy set of its angle card in AD_COPY.md (09). The master shows the operator the sheets.

## 11. Spec checklist and anti-patterns
Always: packshot attached · PRODUCT_DESC verbatim · "NO text or logo on the frame" · quoted text · market-language spelling · zones in % · ratio/resolution valid (4:5 → 1K) · one angle card per ad.
Never: competitor brand names · softened or caveated claims · invented statistics · our logo stamped in a corner "for branding" · 4:5 at 2K (fails) · reusing competitor faces · an ad on a killed angle or with no angle card.

## 12. Noxis run — worked examples

Top 5 (FIDELITY-97, refs `[competitor ad, noxis-packshot.png]`, all originals 1080×1080 → 1:1 2K, 50 credits):
| Ad | Source rank / format | EXTRA used |
|---|---|---|
| ad-01-ours-vs-theirs | #1 Ours vs Theirs table | "Keep the 'Theirs' side showing a different, generic pair of cheap yellow-lens fit-over glasses (not identical to the reference photo)." |
| ad-02-worlds-first-after-dark | #2 POV through lens + 4 customer photos | "The bottom row of four customer photos must show four DIFFERENT people (similar ages, genders and car/home settings as the reference) wearing our glasses." |
| ad-03-cataract-solution | #3 product + callout arrows | none (should have corrected the original's typo "Peripheral vison", which was copied) |
| ad-04-worlds-first-cataracts-pov | #4 rear POV through lens | "Through the lenses the night highway looks warm amber and clear." |
| ad-05-ours-vs-theirs-lens-view | #5 comparison, lens close-ups | "'Ours' shows our glasses close-up with the warm amber view of cars at night; 'Theirs' a generic cheap yellow sport lens." |

Base block used (FIDELITY-97 filled):
```
Reference image 1 is an existing ad: recreate it at about 97% fidelity — same canvas layout, same proportions and
positions, same background, same colors, same typography (weights, sizes, case), same icons, and the SAME on-image text
word for word. Reference image 2 is our product: wherever our glasses appear in the ad, use exactly the glasses from
reference 2 (black wraparound fit-over frame, amber/orange lenses, amber side shields) with no text or logo on the
frame. Do not show any brand name or logo anywhere. Crisp, correctly spelled text.
```

Pattern ads (PATTERN-AD, ref `[packshot]`, 4:5 1K, 120 credits) — derived one-to-one from ranks 6–28: lifestyle + panel (#6), rainy-night poster (#7), planner (#8), rain POV (#9), floating glasses (#10), 3 reasons list (#11), hands holding glasses (#12), side-glare poster (#13), tabletop vs (#14), beam diagram (#15), anatomy (#16), tired-eyes poster (#17), garage whiteboard (#18), "6 IN 10" stat poster (#19, stat mirrored from the competitor), split before/after (#20), brand letter (#21), couple two pairs (#22), timeline 2005/2015/Tonight (#28), six-signs humor grid (#24), newspaper advertorial (#26).

Example spec (ad-07-rainy-night-poster):
```
Big-type poster on a light grey-white gradient background. Huge black ultra-condensed all-caps headline filling the
top: "RAINY NIGHT?" / "NO PROBLEM.". Below, four bullets with amber "+" signs in black condensed sentence case:
"Cuts the glare off wet roads", "Softens blinding LED headlights", "Slips over your prescription glasses",
"30-day money-back guarantee". Bottom 40%: the glasses large in three-quarter view with rain droplets on the lenses
and a glossy reflection below.
```
Example spec (ad-06-see-the-road, claims at full strength):
```
Lifestyle + benefit panel. Top 65%: candid photo of a smiling man in his early 60s with grey hair driving at night,
wearing the glasses, warm light on his face, blue city bokeh outside. White bold Poppins headline on the right:
"See The Road," / "Not The" / "Glare" with the word Glare in amber on a black box. Bottom 35%: solid amber panel with
three black outlined circle-check icons and black bold text "Cataracts", "Astigmatism", "Fits Over Prescription
Glasses", the glasses product at the right of the panel.
```
Example of brand name where the format needs it (ad-21-letter): title "A NOTE FROM NOXIS", script signature "Noxis", product bottom right — mirrors the competitor's "A MESSAGE FROM PLAIMS" letter.
