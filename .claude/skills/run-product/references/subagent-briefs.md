# Sub-agent briefs (copy, fill the <…>, launch)

Launch with the `Agent` tool (`subagent_type: general-purpose`, `run_in_background: true`) and an explicit `model`: leads `opus` + `effort: "low"`; workers `sonnet` (writing/code/vision) or `haiku` (mechanical) — see SKILL.md §3. Launch independent agents **in the same message**. Every brief starts with the COMMON HEADER so the agent can work cold.

## Contents
- Common header
- 1 Capture agent · 2 Media agent · 3 Name brainstorm (optional)
- 4 Conversion architect · 5 Copywriter · 6 Builder (optional) · 13 Home-page builder
- 7 Product-image agent · 8 Page-image agent
- 9 Ad analyst (×2) · 10 Ad-creative agent · 11 Ad-copy agent · 14 Policies agent (optional)
- 12 Visual QA agent
- Handling returns

---

## Common header (prepend to every brief)
```
You are a sub-agent in a product launch run (skill `run-product`, root C:\Users\Moi\.claude\skills\run-product).
Read first: <PRODUCT_DIR>\BRIEF.md (inputs and decisions) and
C:\Users\Moi\.claude\skills\run-product\references\00-operator-rules.md (non-negotiable rules — claims stay at full
strength, no logo on product images, 1:1 testing, etc.).
Environment: Windows, Git Bash; run Python as `python -I`; scripts are in the skill's scripts\ folder.
Writing files: you may write code, JSON job files, images and data files at the paths given below.
Documents (analyses, specs, copy) must be RETURNED AS TEXT in your final reply — the harness may refuse report
files from sub-agents and the master will save them. Do not call Brandsearch MCP tools; use the dump files given.
Do not modify the theme repo unless this brief says so. Do not publish or push anything.
```

## Lead briefs (launch both in ONE message; `model: "opus"`, `effort: "low"`, background)

### Lead A — Store lead
```
<COMMON HEADER>
You are LEAD A (Store) of a run-product launch, running on Opus at low effort. Your job is to PLAN, DELEGATE and
VERIFY — not to do mechanical work yourself. Spawn workers with the Agent tool (general-purpose, background,
parallel when independent) using: model "haiku" for scripts/downloads/screenshots/theme check/policies fetch+transform;
model "sonnet" for SECTION_SPEC (conversion architect), copywriting, Liquid section building, visual QA.
Use the worker briefs below (1, 4, 5, 6, 12, 13, 14) and add `model` to each.
Stream: capture (product + home) → SECTION_SPEC → copy → build product page (settings, header, footer, sections,
template) → home page → policies transform → local render + QA loop.
You MAY write theme files on branch <BRAND_SLUG> (no git commands, no push, no publish) and files in <PRODUCT_DIR>.
Verify each worker output yourself (read files, run `shopify theme check`, look at screenshots). Escalate a task to
yourself only if a worker failed twice or it needs judgment (claims strength, 1:1 fidelity, broken build).
Return (text): files changed, what was built per section, QA table, operator to-dos, "ready to push" list.
```

### Lead B — Growth lead
```
<COMMON HEADER>
You are LEAD B (Growth) of a run-product launch, running on Opus at low effort. PLAN, DELEGATE, VERIFY.
Workers: model "haiku" for downloads, GIF→WebP, contact sheets, rank_ads runs, running kie_jobs.py on prepared job
files; model "sonnet" for ad analysis (vision), writing Kie prompts/job JSON (packshot, gallery remakes, page
images, 25 ads), ad copy. Use worker briefs 2, 7, 8, 9, 10, 11 and add `model` to each.
Stream: packshot FIRST → gallery remakes → page images/GIF WebP → ad analysis (2 analysts) → AD_VARIANTS.md (STOP for operator approval) → 25 ads → ad copy.
Kie budget: <credits>; check `kie_jobs.py --credits` before each batch; stay within budget, prioritise packshot →
gallery → top-5 ads → remaining ads → page images, and report what was skipped.
Open every contact sheet yourself before accepting a batch (claims at full strength, no logo, no competitor name,
correct spelling, product matches packshot).
Return (text): file lists per stream, credits spent, flaws left, documents (COMPETITOR_ADS.md, AD_COPY.md) as text.
```

---

## 1 Capture agent (Phase 1)
**Launch:** immediately after preflight. **Reference:** 03 §capture.
```
<COMMON HEADER>
Task: capture the competitor product page <COMPETITOR_URL>.
1. python -I <skill>\scripts\capture_page.py "<COMPETITOR_URL>" --out "<PRODUCT_DIR>\02_competitor\page"
2. python -I <skill>\scripts\screenshot.py "<COMPETITOR_URL>" --out "<PRODUCT_DIR>\02_competitor\page" --name comp
3. Same for the competitor home page: capture_page.py "<COMPETITOR_HOME>" --out "<PRODUCT_DIR>_competitor\home"
   and screenshot.py "<COMPETITOR_HOME>" --out "<PRODUCT_DIR>_competitor\home" --name home
4. Read capture.md files and the desktop chunks/sheets.
Return (text, <400 words), plus the home page's section list top→bottom: title, price/variants, bundle/app tiers (title, badge, price, gifts), palette (top hex +
roles: buttons, accents, backgrounds), fonts, apps detected, media counts (gallery, gifs, videos, testimonials), the
section list top→bottom in one line each, mobile capture status, anything that failed.
```

## 2 Media agent (Phase 1)
**Launch:** with the capture agent; if capture.json isn't there yet, wait/poll for it (max ~5 min) or run capture_page.py yourself into a scratch dir. **Reference:** 06.
```
<COMMON HEADER>
Task: download all competitor media RAW.
1. When <PRODUCT_DIR>\02_competitor\page\capture.json exists:
   python -I <skill>\scripts\fetch_media.py --from-capture "<...>\capture.json" --out "<PRODUCT_DIR>\02_competitor\media"
   --kinds images,gifs,videos --webp-dir "<PRODUCT_DIR>\04_page-images"
2. Raw files must stay byte-identical (GIFs especially). Report WebP sizes before/after.
3. python -I <skill>\scripts\contact_sheet.py "<media>\*.*" --out "<media>\_sheet.jpg" and Read the sheet.
Return (text): list of files with type (gallery #n / gif / testimonial / section image / video), size, and a one-line
description of what each image shows (this feeds the image map). Flag competitor-specific images (anti-replica
notices, brand-name-heavy graphics) as "skip".
```

## 3 Name brainstorm agent (optional, Phase 2)
Use only if you want a wider candidate pool; the master still picks and presents.
```
<COMMON HEADER>
Task: propose 25 brand names for <product> in <MARKET>. Rules (from 02-branding.md): invented single word, 2–3
syllables, brand-like (not descriptive), natural in "let me get my ___ <product noun>", pronounceable in <language>,
not derivative of "<competitor brand>", no existing major brand. IGNORE domain availability completely.
Return: table name | possessive sentence | why it fits | risk (if any). Mark your top 5.
```

## 4 Conversion architect (Phase 3, A1)
**Launch:** right after the gate (needs capture files). **Reference:** 03 (SECTION SPEC format), templates/SECTION_SPEC.md.
```
<COMMON HEADER>
Task: produce the SECTION SPEC of the competitor page for a Mode <A/B> rebuild.
Inputs: <page dir>\capture.md, capture.json, copy.txt, p.html, screenshots (desk chunks, mobile sheets),
<media dir>\_sheet.jpg. Follow <skill>\references\03-competitor-page-analysis.md and the template
<skill>\templates\SECTION_SPEC.md exactly: every section top→bottom (incl. announcement, header, sticky ATC,
popups, footer) with LAYOUT / COMPONENTS / TYPOGRAPHY / VISUAL DETAILS / IMAGE POSITIONS / CONVERSION ROLE / MOBILE,
then FUNNEL PSYCHOLOGY, IMAGE MAP (position, ratio, content, source file), COPY INVENTORY (every string per
section), APPS (what must be rebuilt natively).
Return the full SECTION_SPEC.md content as text.
```

## 5 Copywriter (Phase 3, A2)
**Launch:** when SECTION_SPEC.md is saved. **Reference:** 03 §copy rules, 09 for tone parity.
```
<COMMON HEADER>
Task: write every word of the <BRAND> product page in <language/market>.
Inputs: <page dir>\SECTION_SPEC.md (COPY INVENTORY = the slots to fill), copy.txt (competitor wording), BRIEF.md
(brand, title, offer, guarantee).
Rules: same persuasion job per slot; original wording that paraphrases the competitor's key lines; claims at the SAME
strength (never soften, never add caveats); simple vocabulary, direct response; total length close to the
competitor's; brand name replaces theirs; testimonials rewritten as new people whose details can match the photos
listed in the image map; prices/currency for <MARKET>.
Return: a copy deck in section order, each slot labelled exactly as in the COPY INVENTORY (so the builder can map it),
plus word count vs competitor.
```

## 6 Builder (optional, Phase 3, A3)
The master usually builds (it owns the repo). Delegate only big custom sections, with explicit file paths.
```
<COMMON HEADER>
You MAY write these theme files only: <list of new files, e.g. sections/<slug>-comparison.liquid>.
Task: implement <component> per SECTION_SPEC section "<name>" and <skill>\references\04-product-page-build.md
patterns (vars snippet, media snippet, scoped CSS, schema settings + presets, mobile behaviour).
Then run `shopify theme check` and report only offenses in your files. Do not touch templates or settings.
Return: files written, settings/blocks available, check result.
```

## 7 Product-image agent (Phase 3, B)
**Launch:** right after the gate. **Reference:** 05, tools-kie.
```
<COMMON HEADER>
KIE_API_KEY: <key or "in env">. Credits budget for this agent: <n>.
Task: produce <BRAND>'s product gallery.
1. Packshot FIRST: isolate our product (from <best gallery image or supplier photo>) on pure white, no text or logo on
   the frame, 1:1 2K → <PRODUCT_DIR>\03_product-images\<slug>-packshot.png. Read it; redo if wrong.
2. For each competitor gallery image in <media dir> (skip those flagged "skip"): write one job in
   <PRODUCT_DIR>\scratch\jobs_gallery.json using the CONCEPT-REMAKE template from 05 (same idea/layout/claims/text
   structure with our product; NO brand logo or wordmark; correct spelling; 1:1 2K).
3. python -I <skill>\scripts\kie_jobs.py <jobs> "<PRODUCT_DIR>\03_product-images"
4. Contact sheet → Read → fix with KEEP-EDIT jobs (text-only fixes) → keep superseded versions in a subfolder.
Return: final file list in gallery order (one line each: what it shows), credits spent, any flaw left.
```

## 8 Page-image agent (Phase 3, C)
**Launch:** after the gate (needs the image map or the media agent's list). **Reference:** 06, tools-kie.
```
<COMMON HEADER>
Task: produce page images for <BRAND>.
1. Testimonial/lifestyle images listed in the image map: Kie remakes (same framing, DIFFERENT people), 1:1 2K →
   <PRODUCT_DIR>\04_page-images. Keep each person consistent with the testimonial text slot (gender/age/relationship).
2. GIFs: confirm raw files exist in media\, WebP versions in 04_page-images (fetch_media.py --webp-dir).
3. Export theme-ready copies: JPG q80–84 progressive, 800–1400 px, named <slug>-<role>.jpg / .webp, into
   <PRODUCT_DIR>\04_page-images\theme\ (the master copies them into the theme's assets/).
Return: mapping image-map position → file, credits spent.
```

## 9 Ad analyst (×2, Phase 3, D1)
**Launch:** after rank_ads.py (can start before the gate). Split ranks 1–15 / 16–30. **Reference:** 07.
```
<COMMON HEADER>
Task: analyze competitor Meta image ads ranks <01–15 | 16–30> in <PRODUCT_DIR>\05_ads\competitor\ (files NN_<id>.* — real extension, often .png;
ranking.json has reach_rank, days running, copies, captions). Ranking = Brandsearch Top rank by impressions (reach_rank), ties by days running + duplicates.
For EACH ad: rank, file, pixel size + aspect, format type, VERBATIM on-image text (reading order, note highlighted
words), visual description precise enough to recreate at ~97% (layout zones in %, background, product angle/size/
position, people: age/gender/setting/expression, colors hex, fonts weight/case/family-style, icons, badges),
hook/angle + Schwartz awareness level, claims made (verbatim).
Then a PATTERNS section: formats, hooks, color system, typography, claim types, newest angles being tested.
Return everything as text (markdown).
```

## 12 Copy chief (Opus, playbooks)
**Launch:** whenever persuasive copy is written (AD_VARIANTS, AD_COPY, page/home copy deck, image claims). **Reference:** 13, 00 §1.
```
<COMMON HEADER>
You are the COPY CHIEF. Read the relevant sections of <SKILL>/books-playbooks/*.html first (grep headings). Write specific
direct-response copy with NO softness, calibrated to the competitor's proven framework and promise level (they scale);
sharpen with the playbooks, push promises further only where the angle needs it; no hedges or caveats; claims at full strength. Keep the given structure/format; return the copy + one line per piece naming the
playbook principle used.
```

## 10 Ad-creative agent (Phase 3, D2)
**Launch:** when COMPETITOR_ADS.md and the packshot exist. **Reference:** 08, tools-kie.
```
<COMMON HEADER>
KIE_API_KEY: <…>. Credits budget: <n> (top-5 at 2K = 50; 20 × 4:5 1K = 120).
Task: create 25 Meta image ads for <BRAND>.
0. FIRST write 05_ads/AD_VARIANTS.md (08 §1b): for all 25 ads, original headline → our almost-similar variant headline,
   original design → our design variant. Return it and STOP; generate only after the operator approves.
1. Top 5 (ranks 1–5): jobs with TWO references [competitor ad file NN_<id>.*, our packshot], same aspect ratio and format,
   but the APPROVED variant headline and design variant (≈80–90% similar, not a copy), new faces, no competitor brand.
2. 20 more: pick formats × hooks from COMPETITOR_ADS.md patterns (selection matrix in 08); write one detailed spec per
   ad (layout zones %, verbatim text, colors, fonts, people, product placement); packshot attached to EVERY job;
   4:5 at 1K.
3. Run kie_jobs.py into <PRODUCT_DIR>\05_ads\generated (names ad-NN-<slug>), contact sheets, Read, fix.
Return: table ad | format | hook | headline on image | file, credits spent, flaws left.
```

## 11 Ad-copy agent (Phase 3, E)
**Launch:** when ranking.json (captions) and COMPETITOR_ADS.md exist. **Reference:** 09, templates/AD_COPY.md.
```
<COMMON HEADER>
Task: extract the competitor's ad copy framework from the captions in ranking.json (titles, descriptions, CTAs) and
write <BRAND>'s copy in <language>: framework beats table, Primary text A (mirrors the structure 1:1), Primary text B
(short), 5 headlines (star top 2), link description, CTA rotation. Claims at the same strength; no caveat notes.
Return the full AD_COPY.md content as text.
```

## 12 Visual QA agent (Phase 4)
**Launch:** after the first build + renders. **Reference:** 10.
```
<COMMON HEADER>
Task: compare competitor vs our build section by section.
Inputs: competitor screenshots <page dir>\comp_*.png / sheets; our renders <scratch>\qa\ours_*.png and buy-box mock
screenshot; SECTION_SPEC.md.
For each section at desktop and mobile: layout, spacing, typography, colors, component states, image positions/ratios.
Ignore harness artefacts listed in 10-qa-and-delivery.md §2.
Return a discrepancy table: SECTION | ISSUE (measured: e.g. radius 12→18px) | SUGGESTED FIX (CSS/setting) | SEVERITY.
```

## 13 Home-page builder (Phase 3, A4)
**Launch:** after the gate; it can write HOME_SPEC + copy immediately and build once A3's settings and reusable
sections exist. **Reference:** 11, 04.
```
<COMMON HEADER>
You MAY write: templates/index.json (or index.<slug>-v2.json if the live home has ad traffic), new
sections/<slug>-*.liquid, blocks/<slug>-*.liquid, snippets/<slug>-*.liquid, assets/<slug>-home-*; you may extend
existing <slug>-* sections with OPTIONAL settings only. No git commands, no theme push/pull (the master does that).
Task: clone the competitor home <COMPETITOR_HOME> 1:1 (Mode <A/B>) following <skill>
eferences	-home-page.md:
1. Read <PRODUCT_DIR>_competitor\home\ (capture + screenshots); write the HOME SPEC (return it as text).
2. Map each section: reuse <slug>-* sections → native theme sections → new <slug>-* sections.
3. Copy: original, claims at the same strength, consistent with the product page copy and BRIEF offer.
4. Images: reuse 03_product-images / 04_page-images / packshot; Kie only for essential missing visuals (budget <n>).
5. Build index.json with a Python builder (rich text in <p>), theme check (no new offenses), local render +
   side-by-side screenshot comparison, fix.
Return: HOME_SPEC text, section mapping table (competitor section → our section, native/custom), files written,
images used/credits, theme check + QA notes, operator to-dos (product links, app widgets).
```

## 14 Policies agent (optional; the master can do it in minutes)
**Launch:** after the gate when OUR_DOMAIN and SUPPORT_EMAIL are known. **Reference:** 12.
```
<COMMON HEADER>
Task: clone the competitor's policies for <BRAND>.
1. python -I <skill>\scripts\policies.py fetch --site <competitor root> --out "<PRODUCT_DIR>\06_policies\source"
   --html "<PRODUCT_DIR>\02_competitor\page\p.html"
2. python -I <skill>\scripts\policies.py transform --in "<...>\source" --out "<PRODUCT_DIR>\06_policies"
   --brand-from <Competitor> --brand-to <BRAND> --domain-from <competitor domain> --domain-to <OUR_DOMAIN>
   --email-to <SUPPORT_EMAIL>
3. Read REVIEW.md and every <handle>.html: text must stay 1:1; remove any remaining address, phone, person or
   registration detail by hand; no competitor identity left.
Do NOT push (the master pushes with the store token).
Return: table policy | words | replacements | removals | leftovers, plus any manual edits you made.
```

---

## Handling returns
- Save returned documents immediately to their target paths (SECTION_SPEC.md, COMPETITOR_ADS.md, AD_COPY.md, copy deck).
- Verify claims of success: open generated images/contact sheets yourself before reporting them as done.
- If an agent stalls or fails, resume it with `SendMessage` (keeps its context) rather than starting a new one.
- Update BRIEF.md progress after each return.
