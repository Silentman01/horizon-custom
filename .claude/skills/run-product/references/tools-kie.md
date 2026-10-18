# Kie.ai (GPT Image 2) — models, runner, pricing, prompt patterns

Every generated image in this skill (packshot, gallery remakes, testimonials, section images, ads) goes through Kie.ai's GPT Image 2 via the bundled batch runner `scripts/kie_jobs.py`. This file is the single reference for how to call it, what it costs, and the canonical prompt blocks that 05, 06 and 08 fill in.

`SKILL` below = `~/.claude/skills/run-product` (Windows: `C:\Users\Moi\.claude\skills\run-product`).

## Contents
1. Models and discovery
2. Key handling
3. Endpoints
4. Input schema (GPT Image 2)
5. Aspect ratio × resolution matrix and cost
6. Credit check and budgeting
7. Uploading reference images
8. The runner (`kie_jobs.py`)
9. Rate limits
10. Prompt-writing rules
11. Prompt patterns (canonical blocks)
12. Failure handling
13. Result retrieval and the 14-day expiry
14. Reporting spend

---

## 1. Models and discovery

| Use | Model id | Notes |
|---|---|---|
| Edit / remake from reference images (almost everything) | `gpt-image-2-image-to-image` | `input_urls` (1–16 images) + `prompt` |
| Pure generation, no reference (editorial photos, scenes) | `gpt-image-2-text-to-image` | `prompt` only |

Why GPT Image 2: it renders long, correctly spelled on-image text, respects layout instructions given in % zones, and keeps a product faithful when the product photo is attached. Those three properties are exactly what infographics and ads need.

**Rule:** never trust a model name from memory. The catalog changes (it already lists `gpt-image-2-5-*` variants at the same price). Before the first batch of a run, confirm the model still exists and the price is unchanged:

```bash
# catalog filtered by keyword (shares a 1 req/s budget with schema/price calls)
curl -s -H "Authorization: Bearer $KIE_API_KEY" "https://api.kie.ai/api/v1/models?q=gpt-image-2"
curl -s -H "Authorization: Bearer $KIE_API_KEY" "https://api.kie.ai/api/v1/models/gpt-image-2-image-to-image/price"
curl -s -H "Authorization: Bearer $KIE_API_KEY" "https://api.kie.ai/api/v1/models/gpt-image-2-image-to-image/schema"
```
PowerShell: call `curl.exe` (plain `curl` is an alias of Invoke-WebRequest) or use the Python one-liners in §6. Space discovery calls ≥1.1 s apart. Keep using `gpt-image-2-*` unless it is gone or the operator asks; switching models mid-run changes the look across the gallery.

## 2. Key handling
- The runner reads `KIE_API_KEY` from the environment. Sources, in order: env var already set → project skill/config the operator points to → ask the operator.
- Set it for the session only: PowerShell `$env:KIE_API_KEY = "<key>"`; bash `export KIE_API_KEY=<key>`.
- Never print it, never write it into job JSONs, BRIEF.md, briefs returned as text, or any file in the theme repo.
- Sub-agents inherit the env of their own shell, not yours: pass the key in the brief only if the env var isn't set machine-wide (the brief template has a `KIE_API_KEY:` line).

## 3. Endpoints

| Purpose | Method + URL | Notes |
|---|---|---|
| Create task | `POST https://api.kie.ai/api/v1/jobs/createTask` | body `{model, input}` → `data.taskId` |
| Poll task | `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=…` | `data.state`: waiting / queuing / generating / success / fail |
| Credit balance | `GET https://api.kie.ai/api/v1/chat/credit` | `data` = number |
| Price | `GET https://api.kie.ai/api/v1/models/<model>/price` | prose `pricingDesc` |
| Schema | `GET https://api.kie.ai/api/v1/models/<model>/schema` | `data.openapi` is the OpenAPI doc (may be `null`) |
| Upload (base64, ≤10 MB) | `POST https://kieai.redpandaai.co/api/file-base64-upload` | **different host**; `{base64Data, uploadPath, fileName}` → `data.downloadUrl` |
| Upload (multipart, >10 MB) | `POST https://kieai.redpandaai.co/api/file-stream-upload` | form fields `file`, `uploadPath`, `fileName` |
| Fresh download link | `POST https://api.kie.ai/api/v1/common/download-url` | `{url}` (Kie-hosted only) → 20-min link |

All responses are `{code, msg, data}`; **HTTP 200 does not mean success — check `code`**. Result images are in `data.response.resultUrls[0]`.

## 4. Input schema (GPT Image 2)

| Field | Type | Notes |
|---|---|---|
| `prompt` | string | required; up to 20,000 characters — long, precise specs are fine |
| `input_urls` | array of URLs | required for image-to-image; max 16; **order matters** (the prompt says "reference image 1 / 2") |
| `aspect_ratio` | enum | `auto, 1:1, 3:2, 2:3, 4:3, 3:4, 5:4, 4:5, 16:9, 9:16, 2:1, 1:2, 3:1, 1:3, 21:9, 9:21` — always set it explicitly |
| `resolution` | `1K` / `2K` / `4K` | always set explicitly |
| `background` | `transparent` / `opaque` / `auto` | **1K only** (useful for a transparent packshot) |

## 5. Aspect ratio × resolution matrix and cost

| Resolution | Credits / image | Unsupported ratios | Observed output size |
|---|---|---|---|
| 1K | 6 | none | 4:5 → 1122×1402 |
| 2K | 10 | **5:4, 4:5, 3:1, 1:3, 9:21** | 1:1 → 2048×2048 |
| 4K | 16 | 3:1, 1:3, 9:21 | — |

Defaults used by this skill:

| Asset | Ratio | Resolution | Credits |
|---|---|---|---|
| Packshot | 1:1 | 2K | 10 |
| Gallery remake / fix edit | 1:1 (or the competitor's ratio) | 2K | 10 |
| Testimonial / section photo | slot ratio (1:1, 3:2, 16:9 …) | 2K | 10 |
| Top-5 ad recreation | competitor's ratio: 1:1 / 9:16 / 16:9 → 2K; **4:5 → 1K** | 2K or 1K | 10 or 6 |
| Pattern ad | 4:5 | 1K | 6 |
| Bundle thumbnail | 1:1 | 1K | 6 |

Why 4:5 at 1K: 2K rejects 4:5 (the createTask call fails with a validation code), and 1122×1402 already exceeds Meta's 1080×1350 feed spec. Use 4K (16 credits) only if the operator explicitly wants print-size ads.

## 6. Credit check and budgeting

Check the balance **before every batch** and compare with the batch cost:
```bash
python -I -c "import os,json,urllib.request as u;r=u.Request('https://api.kie.ai/api/v1/chat/credit',headers={'Authorization':'Bearer '+os.environ['KIE_API_KEY']});print(json.load(u.urlopen(r)))"
```
Budget formula: `Σ(jobs × price per resolution) × 1.2` (20% headroom for fix rounds).

Typical full run (Noxis): packshot 10 + 5 gallery remakes 50 + 3 testimonials 30 + top-5 ads 50 + 20 pattern ads 120 = **≈260 credits**, plus fixes. Noxis actually spent ~80 more on two avoidable fix rounds (softened claims 30, logo removal 50) — following the rules in 05 avoids them.

If the balance is short: tell the operator the shortfall in one line **before** generating, then run in priority order: packshot → gallery → top-5 ads → remaining ads → page images. Never start a batch you can't finish — a half gallery is worse than a later complete one.

## 7. Uploading reference images
- The runner uploads every local path in `upload.files` with the base64 endpoint (`uploadPath: images/run-product`) and caches the URL per path for that run.
- Base64 adds ~33%: a file above ~7 MB can exceed the 10 MB limit and the runner stops on an `AssertionError` showing the upload response. Fix: save a JPG copy (quality 92) of big PNG references and attach that (`python -I -c "from PIL import Image;Image.open('big.png').convert('RGB').save('big.jpg',quality=92)"`).
- Uploaded files are deleted after 24 h. That only matters if you reuse URLs by hand; the runner re-uploads each run.
- A reference that is already a public HTTPS URL can go in `input.input_urls` directly (or `first_url`, see §8) without upload.

## 8. The runner (`kie_jobs.py`)

```
python -I "<SKILL>/scripts/kie_jobs.py" <jobs.json> <out_dir>
```
- Reads `KIE_API_KEY`; creates all tasks (0.6 s apart — inside the 20/10 s limit), polls every 5 s, downloads each result to `<out_dir>/<name>.<ext>` (ext from the result URL, normally `.png`), prints `name: saved … (N credits)`.
- Stops waiting after **900 s** for the whole batch and prints `name: timed out, task <taskId>` for anything still running (recover with §13).
- **Overwrites** an existing file with the same name in `out_dir`. Before an edit round, move the current version to a `superseded/<reason>/` folder and upload it from there (see 05 §9).
- Create failures print `name: create failed {…}` and the batch continues; task failures print `name: FAILED <failCode> <failMsg>`.

Job file format (a JSON array):
```json
[
  {
    "name": "noxis-product-02",
    "model": "gpt-image-2-image-to-image",
    "upload": {"field": "input_urls", "files": ["G:/Ecom/Products/Noxis/02_competitor/media/plaims-product-02.png",
                                               "G:/Ecom/Products/Noxis/03_product-images/noxis-packshot.png"]},
    "input": {"prompt": "…", "aspect_ratio": "1:1", "resolution": "2K"}
  }
]
```
- `upload.files` are uploaded in order and **prepended** to `input[field]`; any URLs already in `input.input_urls` come after them. Optional `first_url` (string) is inserted at position 0, before the uploads.
- Text-to-image jobs simply omit `upload` and use `gpt-image-2-text-to-image`.
- Use forward slashes in paths inside JSON (or escaped backslashes).

Working practice:
- Write jobs with a small Python **builder** (constants for shared prompt blocks + a list of `(name, reference, description)` tuples), exactly like the Noxis builders. Builders make fix rounds trivial (edit one tuple, rebuild, rerun only that job).
- Keep builders, job JSONs and run logs in `PRODUCT_DIR/scratch/` (`jobs_gallery.json`, `jobs_gallery_fix1.json`, `jobs_ads_top5.json` …). They are prompt files: never put them in the theme repo.
- Log every run: bash `… | tee PRODUCT_DIR/scratch/run_gallery.log`; PowerShell `… | Tee-Object -FilePath <log>`.
- Run one batch per asset family (gallery, page images, top-5 ads, pattern ads) so a failure or review round never blocks the others. Independent batches can run at the same time in separate shells/agents.
- 20 jobs typically finish in 2–4 minutes; a single 2K edit in about one minute.

## 9. Rate limits

| Endpoint | Limit | Effect |
|---|---|---|
| `createTask` | 20 requests / 10 s per account | runner's 0.6 s spacing stays below it; parallel runners can collide → `code 429` "create failed" |
| `recordInfo` | 10 requests / s per taskId | runner polls every 5 s |
| `models`, `schema`, `price`, `success-rate` | 1 request / s, one shared budget | space discovery calls ≥1.1 s |

A 429 is returned in the body with HTTP 200 and the request is **not** queued: rerun only the failed jobs (filter the JSON by name) after a few seconds.

## 10. Prompt-writing rules
These rules come from what worked (and what broke) in the Noxis run.
1. **Name the role of each reference.** "Reference image 1 is an existing ad … Reference image 2 is our product …". Without it the model blends both.
2. **One fixed product sentence (`PRODUCT_DESC`)**, reused verbatim in every prompt of the run, e.g. "black wraparound fit-over night driving glasses with amber/orange polarized lenses and amber side shields". Consistency of wording = consistency of product.
3. **Always attach the packshot** whenever our product appears (ads: mandatory). Reference + description beats description alone.
4. **No text or logo on the product itself.** Small prints render garbled (the Noxis packshot's temple print came out as "noɓıs"). Say "with no text or logo on the frame/product".
5. **No brand logo or wordmark on gallery images**, and never the competitor's name anywhere. Say it explicitly: "Do not show any brand name or logo anywhere."
6. **Quote every on-image string exactly** (`"Reduces Nighttime Glare By 85%"`). Claims are copied at full strength — see 00-operator-rules §1. Add "All text crisp, large and correctly spelled <market language>, exactly as written in quotes."
7. **Layout in zones with %** ("Top 65%: photo … Bottom 35%: amber panel …"), plus colors as hex, fonts as a family/style ("Poppins Bold, Title Case", "ultra-condensed all-caps like Anton").
8. **People: describe the new person precisely** (age, gender, hair, clothing, expression, setting) and say "different people from the reference" — otherwise the face is cloned.
9. **Editing beats regenerating** when the image is approved except for text or one element: KEEP-EDIT costs the same, keeps everything else, and converges in one round.
10. **Don't add disclaimers** ("simulated", "results may vary") unless the competitor's own creative carries them — then they are part of the format you mirror.

## 11. Prompt patterns (canonical blocks)
Fill the `<…>` slots. Worked, filled versions live in 05 (product images), 06 (page images) and 08 (ads).

### PRODUCT_DESC
```
<one sentence: product type, shape, colors, materials, distinctive parts — no brand, no print>
```

### PACKSHOT (i2i, 1:1 2K, reference = clearest product photo)
```
Isolate ONLY the product from the reference and create a clean e-commerce packshot: the exact same <PRODUCT_DESC>,
<angle, e.g. three-quarter front view>, centered, filling about 75% of the width, on a pure white #FFFFFF background
with a soft natural contact shadow. Remove all text, arrows, insets, banners, badges, people and accessories.
No text, print or logo anywhere on the product. Photorealistic studio product photo, sharp, accurate materials and
reflections. Square.
```

### CONCEPT-REMAKE (gallery / section images; refs = [competitor image, packshot])
```
Reference image 1 shows the concept only: recreate it as a NEW, original image with the same main idea, layout logic,
text structure and color mood (<palette hex>), but different composition details, different photography and redrawn
graphics. Reference image 2 is our exact product: <PRODUCT_DESC>; reproduce it faithfully wherever the product
appears, with no text or logo on it. Do not show any brand name, wordmark or logo anywhere on the image.
All text crisp, large, correctly spelled <language>, exactly as written in quotes.
<DESC: layout zones + every text line in quotes + people + product placement>
```

### FIDELITY-97 (top-5 ad recreation; refs = [competitor ad, packshot])
```
Reference image 1 is an existing ad: recreate it at about 97% fidelity — same canvas layout, same proportions and
positions, same background, same colors, same typography (weights, sizes, case), same icons, and the SAME on-image
text word for word. Reference image 2 is our product: wherever the product appears in the ad, use exactly the product
from reference 2 (<PRODUCT_DESC>) with no text or logo on it. Do not show any brand name or logo anywhere.
Crisp, correctly spelled text. <EXTRA: people swaps, typo corrections, brand-name replacements, generic rival product>
```

### PATTERN-AD (new ad inspired by a format; ref = [packshot])
```
Create a high-converting Meta feed ad, 4:5 portrait. The reference image is our exact product: <PRODUCT_DESC>.
Whenever the product appears, reproduce it faithfully, with NO text or logo on it. Brand colors <hex list>.
All on-image text must be crisp, large, correctly spelled <language>, exactly as written in quotes.
<SPEC: format, layout zones %, verbatim text, colors, fonts, people, product placement, scene/grade>
```

### KEEP-EDIT (change only text or one element; ref = [the image to edit])
```
Edit this exact image. Keep everything identical (layout, product, colors, photography, typography style) and change
ONLY what is described below. All text crisp and correctly spelled.
<list: Change "<old text>" to "<new text>". … Keep "<text>" as is.>
```

### NO-LOGO (remove a wordmark/logo and reflow; ref = [the image to edit])
```
Edit this exact image. Remove the "<brand>" wordmark/logo entirely, including any brand print on the product.
Recompose so the freed space is used: enlarge and re-center the headline, product and other elements to fill the
canvas naturally, with no empty gap where the logo was. Keep every other text EXACTLY the same word for word, same
colors, same product, same style. All text crisp and correctly spelled. <ratio word, e.g. Square>.
```

### PEOPLE-SWAP (testimonial / lifestyle photo; refs = [competitor photo, packshot])
```
Use reference image 1 only for the concept and framing; create DIFFERENT people. Reference image 2 is the product
they wear/use: <PRODUCT_DESC>, with no text or logo on it. <DESC: shot type (e.g. candid smartphone selfie from the
driver's seat at night), person/people (age, gender, hair, clothing, expression), setting, light>.
Natural, unpolished, real customer photo look. No text, no logos.
```

### BUNDLE (1/2/3-unit thumbnails; ref = [packshot])
```
Use the reference ONLY to copy the exact product: <PRODUCT_DESC>. Create a clean e-commerce packshot: exactly <ONE|TWO|
THREE> identical <units> <arrangement, e.g. side by side, slightly overlapping>, slight three-quarter front view,
centered, together filling about 70% of the frame width. Pure white #FFFFFF seamless background, soft natural contact
shadows, bright even studio lighting. No other objects, no text, no badges, no logo. Square image.
```

### EDITORIAL (advertorial / listicle photos; t2i, or i2i with packshot)
```
Candid documentary <smartphone photo|photograph>: <scene, people, action>. <light>, real <market> home/car setting,
slightly imperfect framing, film-like grain, editorial magazine photography, not staged or glossy.
<If product visible: use the reference ONLY for the exact product.> No text, no logo.
```

## 12. Failure handling

| Symptom | Cause | Fix |
|---|---|---|
| `create failed {'code': 401 …}` | key missing/invalid | check `KIE_API_KEY` in this shell |
| `create failed {'code': 402 …}` | insufficient credits | stop; report shortfall to the operator (§6) |
| `create failed {'code': 422 …}` | invalid input (e.g. 4:5 at 2K, >16 refs, empty prompt) | fix the job; rerun that job only |
| `create failed {'code': 429 …}` | rate limit (parallel runners) | wait ~10 s; rerun failed jobs only |
| `create failed {'code': 455/500 …}` | service issue | check `/models/<model>/success-rate`; retry later |
| `FAILED <failCode> <failMsg>` | generation refused/failed (often content policy on a phrase or a real-looking minor/celebrity) | read the message, rephrase the trigger part, keep claims intact; rerun |
| `AssertionError` with upload response | reference >10 MB after base64, or upload host down | attach a JPG copy (§7); retry |
| `timed out, task <id>` | slow queue | poll that taskId later (§13); don't resubmit (double charge) |
| Garbled small text on product | model invents a print | KEEP-EDIT "remove any text or print from the <frame>"; keep "no text on product" in future prompts |
| Misspelling / wrong word | long text block | KEEP-EDIT with the exact corrected strings |
| Product drift (shape/color) | no packshot attached or vague description | attach packshot as a reference; reuse PRODUCT_DESC verbatim; regenerate |
| Competitor name/logo leaked from reference | reference text copied | NO-LOGO / KEEP-EDIT; add "Do not show any brand name" |
| Same face as the reference person | identity copied | PEOPLE-SWAP with a more different description (age, hair, clothes) |

## 13. Result retrieval and the 14-day expiry
- Result files are deleted by Kie after **14 days**; the runner downloads immediately. Never store result URLs as the only copy.
- Recover a timed-out task (prints the state; downloads when done):
```bash
python -I -c "import os,sys,json,urllib.request as u;t,o=sys.argv[1],sys.argv[2];r=u.Request('https://api.kie.ai/api/v1/jobs/recordInfo?taskId='+t,headers={'Authorization':'Bearer '+os.environ['KIE_API_KEY']});d=json.load(u.urlopen(r))['data'];print(d['state'],d.get('failMsg'));d['state']=='success' and u.urlretrieve(d['response']['resultUrls'][0],o)" <taskId> <out.png>
```
- Task records (prompt + metadata) stay queryable for 2 months — handy to recover a lost prompt.

## 14. Reporting spend
Sum the `(N credits)` values from the run logs (or balance before − after) and report per batch in the agent's return and in DELIVERY.md: e.g. "Kie: packshot 10, gallery 50, testimonials 30, ads 170, fixes 20 → 280 credits; balance left 1,720."

## Final step for every batch
After checking a batch, strip metadata before saving finals: `python -I <SKILL>/scripts/strip_metadata.py <out-folder> --inplace` (set FFMPEG to an ffmpeg binary for videos if it is not on PATH). See operator rules section 14.
