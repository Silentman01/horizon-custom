# Sub-agent briefs (copy, fill the <…>, launch)

Launch with the `Agent` tool (`subagent_type: general-purpose`, `run_in_background: true`) and an explicit `model`: leads `opus` + `effort: "low"`; workers `sonnet` (writing/code/vision) or `haiku` (mechanical) — see 16-orchestration.md §1. **Exception: conversion architect (4), copywriter (5), builder (6), home-page builder (13), copy chief (15) and advertorial builder (16) ALWAYS run on Opus 4.6 (`model: "opus"`) no matter what** — these roles require the strongest judgment for adaptation and original copy. Launch independent agents **in the same message**. Every brief starts with the COMMON HEADER so the agent can work cold.

## Contents
- Common header
- Lead briefs (Phase 3 parts)
- Step Alpha briefs: Lead A α · Lead B α · α-analyst (batches) · α-angles · α-synthesis
- 1 Capture agent · 2 Media agent · 3 Name brainstorm (optional)
- 4 Conversion architect (Opus 4.6) · 5 Copywriter (Opus 4.6) · 6 Builder (Opus 4.6) · 13 Home-page builder (Opus 4.6)
- 7 Product-image agent · 8 Page-image agent
- 10 Ad-creative agent · 11 Ad-copy agent · 14 Policies agent (optional)
- 12 Visual QA agent (distinctiveness + blueprint fidelity) · 15 Copy chief (Opus 4.6, playbooks, originality gate)
- 16 Advertorial builder (Opus 4.6, when advertorial funnel detected)
- Handling returns

---

## Common header (prepend to every brief)
```
You are a sub-agent in a product launch run (skill `run-product`, root <THEME_DIR>\.claude\skills\run-product, THEME_DIR from BRIEF.md).
Read first: <PRODUCT_DIR>\BRIEF.md (inputs and decisions) and
<THEME_DIR>\.claude\skills\run-product\references\00-operator-rules.md (non-negotiable rules — claims stay at full
strength, no logo on product images, adapted framework — study the competitor's winning formula then build our own distinct version, etc.).
Environment: Windows, Git Bash; run Python as `python -I`; scripts are in the skill's scripts\ folder.
Writing files: you may write code, JSON job files, images and data files at the paths given below.
Documents (analyses, specs, copy) must be RETURNED AS TEXT in your final reply — the harness may refuse report
files from sub-agents and the master will save them. Do not call Brandsearch MCP tools; use the dump files given.
Do not modify the theme repo unless this brief says so. Do not publish or push anything.
After Step Alpha: read the sections of <PRODUCT_DIR>\00_alpha\ALPHA_DOSSIER.md that this brief names before working.
```

## Lead briefs (launch both in ONE message; `model: "opus"`, `effort: "low"`, background)
These are the Phase 3 parts, sent only after the Alpha quality gate and the branding gate: continue the leads that ran Step Alpha with `SendMessage`, or launch them fresh with these briefs. Their Alpha parts are in §Step Alpha briefs below.

### Lead A — Store lead
```
<COMMON HEADER>
You are LEAD A (Store) of a run-product launch, running on Opus at low effort. Your job is to PLAN, DELEGATE and
VERIFY — not to do mechanical work yourself. Spawn workers with the Agent tool (general-purpose, background,
parallel when independent) using: model "haiku" for scripts/downloads/screenshots/theme check/policies fetch+transform;
model "opus" (Opus 4.6) for conversion architect (4), copywriter (5), builder (6), home-page builder (13),
advertorial builder (16) — these roles require the strongest model for framework adaptation and original copy, never Sonnet;
model "sonnet" for visual QA (12) only.
Use the worker briefs below (1, 4, 5, 6, 12, 13, 14, 16) and add `model` to each.
Read <PRODUCT_DIR>\00_alpha\ALPHA_DOSSIER.md first (3.1 angle cards, 3.2 avatars, 1.4 objections, 1.6 mechanism,
1.10 + 2.4 funnel congruence, 3.5 language bank) and pass the named sections to each worker.
Stream (capture exists from Phase 1): SECTION_SPEC + ADAPTATION BLUEPRINT → fully original copy (from dossier +
playbooks, not paraphrasing competitor) → build adapted page (settings, header, footer, sections, template) →
adapted home page → advertorial pages (A5, when the competitor uses advertorial funnels — 22) → policies transform → local render + QA loop.
You MAY write theme files on branch <BRAND_SLUG> (no git commands, no push, no publish) and files in <PRODUCT_DIR>.
Verify each worker output yourself (read files, run `shopify theme check`, look at screenshots). QA now checks
DISTINCTIVENESS from the competitor (an AI comparing both pages should see two completely different things) as well
as conversion mechanics preserved. Escalate a task to yourself only if a worker failed twice or it needs judgment
(claims strength, adaptation fidelity, broken build).
Return (text): files changed, what was built per section, distinctiveness assessment, QA table, operator to-dos,
"ready to push" list.
```

### Lead B — Growth lead
```
<COMMON HEADER>
You are LEAD B (Growth) of a run-product launch, running on Opus at low effort. PLAN, DELEGATE, VERIFY.
Workers: model "haiku" for downloads, GIF→WebP, contact sheets, rank_ads runs, running kie_jobs.py on prepared job
files; model "sonnet" for writing Kie prompts/job JSON (packshot, own conversion gallery per 05 §16, page images, 25 ads), ad copy.
Use worker briefs 2, 7, 8, 10, 11 and add `model` to each.
Read <PRODUCT_DIR>\00_alpha\ALPHA_DOSSIER.md first (3.1 angle cards, 3.2 avatars, 1.7 inventory, 1.9 ad copy
patterns, 3.3 hook library, 3.4 framework library, 3.5 language bank).
Stream: write every plan/job file first (free) → SAMPLE GATE (00 §18): packshot (real packaging) + gallery hero + one graphic slide + one person/lifestyle + one page image on ONE sheet, then STOP and return for the operator's OK → after OK: own conversion gallery (GALLERY_PLAN.md, 05 §16) → page images/GIF WebP. AD_VARIANTS.md (angle card ID per variant; STOP for operator approval) → SAMPLE matched to the competitor's format mix (5 image ads + 1 video remake when both formats exist; only 5 images or only 1 video otherwise) → SAMPLE GATE → remaining ads and videos → ad copy.
Kie budget: <credits>; check `kie_jobs.py --credits` before each batch; stay within budget, prioritise packshot →
gallery → top-5 ads → remaining ads → page images, and report what was skipped.
Open every contact sheet yourself before accepting a batch (claims at full strength, no logo, no competitor name,
correct spelling, product matches packshot).
Return (text): file lists per stream, credits spent, flaws left, documents (AD_VARIANTS.md, AD_COPY.md) as text.
```

---

<a id="step-alpha-briefs"></a>
## Step Alpha briefs (Phase α; nothing is built in these)
Launch Lead A α and Lead B α in ONE message once Phase 1 data is on disk (`model: "opus"`, `effort: "low"`, background). The leads launch α-analyst and α-angles workers; α-synthesis goes to Lead B with `SendMessage` after GATE α. The spec `<skill>\references\19-step-alpha.md` is authoritative for every field; how to run each step: `<skill>\references\20-step-alpha-runbook.md`. Outputs go to `<PRODUCT_DIR>\00_alpha\` (returned as text, the coordinator saves them).

### Lead A α — customer intelligence + funnel congruence (α1.1 + α1.3)
```
<COMMON HEADER>
You are LEAD A (Store), Step Alpha part, on Opus at low effort. Spec (every field is mandatory):
<skill>\references\19-step-alpha.md; runbook: <skill>\references\20-step-alpha-runbook.md.
Nothing is built in this part: no names, copy, spec, theme files or images.
Inputs: <PRODUCT_DIR>\02_competitor\page\ (capture.md, copy.txt, p.html, screenshots: page copy, testimonials, reviews,
FAQ, imagery, pricing, offer structure), 02_competitor\home\, ad copy (captions in 00_alpha\ad_inventory.json, dumps in 05_ads\competitor\raw\footprint\), every transcript in
00_alpha\transcripts\, 00_alpha\ad_inventory.json.
1. α1.1 CUSTOMER INTELLIGENCE, exactly the spec's fields, one fenced `KEY:` block per item in the format of
   <skill>\templates\ALPHA_DOSSIER.md 1.1–1.6: AVATARS / ICPs (≥ 2 distinct, IDs AV1.., full demographics,
   psychographics, trigger event, awareness state, sophistication + CUSTOMER LANGUAGE quote), PAIN POINTS (≥ 10: felt
   experience, RANK, source, frequency, emotional weight, avatar, verbatim customer language), DESIRES & DREAM OUTCOMES
   (≥ 5: desire, RANK, type, dream outcome, source, avatar, verbatim language), OBJECTIONS (≥ 5: type, how the competitor
   handles it, where in funnel, strength 1–5, GAP), EMOTIONAL LANDSCAPE (all 6 trigger types), UNIQUE MECHANISM
   (mechanism, name, story, proof, Schwartz technique). Quotes verbatim with their source.
   Return it as text first (→ analysis1\1.1_customer.md).
2. α1.3 FUNNEL CONGRUENCE: page side now (what each landing page shows above the fold at desktop and 390px, where
   each promise and objection is handled; every distinct `landing_url` in ad_inventory.json, else the product page
   marked "(assumed)"). When the coordinator sends the per-ad tags from 1.2 (id, angle, promise, avatar), map EVERY ad
   → page path with the spec's fields (AD = inventory short id M#/S#, ANGLE, PROMISE, AVATAR, EMOTIONAL STATE AT CLICK,
   LANDING, FIRST SECTION THEY SEE, CONGRUENCE), score every path HIGH/MED/LOW with notes (table: AD → PAGE PATH |
   CONGRUENCE | NOTES), and write the 4 CONGRUENCE INSIGHTS + PAGE STRATEGY (one multi-angle page or angle-specific
   landing pages, and why). Return as text (→ analysis1\1.3_congruence.md).
Workers (sonnet/haiku) only for mechanical extraction (every testimonial/review/FAQ line verbatim); the analysis is yours.
```

### Lead B α — advertising intelligence, angles, hidden angles, ChatGPT prompt (α1.2 + α1.4 + α2 + α3)
```
<COMMON HEADER>
You are LEAD B (Growth), Step Alpha part, on Opus at low effort. Spec (every field is mandatory):
<skill>\references\19-step-alpha.md; runbook: <skill>\references\20-step-alpha-runbook.md.
Nothing is built in this part: no ads, images or copy.
Inputs: <PRODUCT_DIR>\00_alpha\ad_inventory.json (EVERY ad of the competitor; IDs = short_id M1.. video, S1.. static),
00_alpha\transcripts\ (every video ad), 05_ads\competitor\raw\footprint\ (dumps: captions, headlines, descriptions,
dates), images 05_ads\competitor\images\, videos 05_ads\competitor\videos\, page capture 02_competitor\page\.
1. α1.2 ADVERTISING INTELLIGENCE
   a. Haiku worker, per video ad: ffprobe the real length (when the file exists) and run python -I
      <skill>\scripts\alpha_gate.py beats "<PRODUCT_DIR>\00_alpha\transcripts\<ad_id>.txt" --duration <s> (timed
      lines, HOOK DURATION, VO/TEXT SPLIT, PACING). No Gemini in Step Alpha: frameworks come from the transcript.
   b. Sonnet workers (brief α-analyst) in parallel, batches of ~15 ads, until EVERY video and non-video ad is covered.
   c. You: AD INVENTORY table (every ad: AD ID, FORMAT, PLATFORM, STATUS, RUN TIME, ANGLE, AVATAR; AV IDs from 1.1 when the
      coordinator sends them, provisional labels until then), the video framework patterns table (framework → ads,
      formats, longest run) and CROSS-AD PATTERN MINING (all 10 fields).
   Return as text: 1.2_ad_inventory.md, 1.2_video_ads.md, 1.2_static_ads.md, 1.2_patterns.md, plus the per-ad tags
   (id, angle, promise, avatar) for Lead A's 1.3.
2. When the coordinator sends 1.1 + 1.3: α1.4 MARKETING ANGLE MAP, one card per angle with the exact card fields, IDs
   V1..Vn, CONFIDENCE from run time/volume, ≥ 3 validated cards (→ 1.4_angle_cards.md).
3. α2 HIDDEN ANGLE DISCOVERY: a Sonnet worker (brief α-angles) runs the explosion; you discard weak combinations and rate
   every survivor with the spec's fields, IDs H1..Hn; ≥ 8 angles beyond what the competitor runs; plus the explosion-
   inputs block and the 13-entry table (each emotional entry → its H ids, or "none survived — why")
   (→ analysis2\2.1_hidden_angles.md).
4. α3 CHATGPT PROMPT: fill <skill>\templates\CHATGPT_PROMPT.md for THIS product: its pains, avatars and angles from α1,
   EVERY hidden angle H1..Hn from α2 (category 8), the real subreddits/forums/groups/Amazon competitor + adjacent products; all 8 platform
   types, all 10 data categories with their counts and tags, the exact output format, the 6 "ChatGPT must" rules.
   One ready-to-paste block, no placeholder left (→ chatgpt\CHATGPT_PROMPT.md).
Then STOP and return. The operator runs the prompt (GATE α); α4 comes after (brief α-synthesis).
```

### α-analyst — per-ad batch (Step Alpha 1.2; `model: "sonnet"`, ~15 ads per batch, batches in parallel)
```
<COMMON HEADER>
Task: Step Alpha 1.2 analysis of competitor ads <ad IDs, batch n of m>. Spec: <skill>\references\19-step-alpha.md §1.2.
Inputs per ad: its record in <PRODUCT_DIR>\00_alpha\ad_inventory.json; media file <path>; caption, headline and
description in its `caption` (raw dumps: <PRODUCT_DIR>\05_ads\competitor\raw\footprint\); for a video: 00_alpha\transcripts\<ad_id>.txt + its `alpha_gate.py beats` output (timed lines, hook duration,
speech/no-speech split, WPS). Frameworks and beat maps are read from the transcript (no Gemini in Step Alpha).
EVERY VIDEO ad, every field: FRAMEWORK, BEAT MAP (each beat: timestamp, duration, % of total, function), FORMAT (spec
list), HOOK (exact words, type, open loop mechanism), HOOK DURATION, ANGLE, AVATAR, EMOTIONAL ARC, RETENTION MECHANICS,
VO/TEXT SPLIT, PACING (WPS average + per-beat variation, from the transcript words and times), MUSIC/SFX, CTA (exact
text, timestamp, urgency mechanism).
EVERY NON-VIDEO ad, every field: PRIMARY TEXT, HEADLINE, DESCRIPTION (exact), HOOK (first line, type, open loop), ANGLE,
AVATAR, EMOTIONAL TRIGGER, PERSUASION SEQUENCE, PROOF TYPE, CTA (exact text + urgency), IMAGE FORMAT.
Words verbatim, never paraphrased. No ad skipped; write "none in ad" for a field the ad does not have.
Return as text: one fenced block per ad, first line `AD ID: <short id M#/S#>`, then the fields as `KEY: value` in the
spec's order (format of <skill>\templates\ALPHA_DOSSIER.md 1.8 / 1.9); videos, then non-video ads. Then a tag line per
ad: id | angle | promise | avatar (for 1.3), and 5 lines on what the batch shows (angles, hook types, formats, proof, CTAs).
```

### α-angles — hidden angle explosion (Step Alpha 2.1; `model: "sonnet"`)
```
<COMMON HEADER>
Task: Step Alpha 2.1 ANGLE EXPLOSION for <product> in <MARKET>. Spec: <skill>\references\19-step-alpha.md §2.1.
Inputs: <PRODUCT_DIR>\00_alpha\analysis1\1.1_customer.md and 1.4_angle_cards.md (what the competitor already runs).
1. List EVERY POSSIBLE AVATAR (other ages, genders, activity levels, professions, life stages, conditions, motivations),
   EVERY POSSIBLE PAIN POINT (physical, emotional, social, identity, convenience, financial; primary, secondary,
   adjacent, surprising), EVERY POSSIBLE DESIRE, and all 13 EMOTIONAL ENTRIES (fear, desire, identity, curiosity,
   frustration, contrarian, disgust, authority, social proof, mechanism, comparison, seasonal, life-event).
2. Cross AVATAR × PAIN × DESIRE × EMOTION. Discard weak combinations (one line why). Keep the survivors the competitor
   does not run.
3. Rate each survivor: HIDDEN ANGLE (`H1 — name`), AVATAR, PAIN/DESIRE, EMOTIONAL ENTRY (one of the 13), ESTIMATED
   POTENTIAL (HIGH/MEDIUM/LOW: segment size, pain/desire intensity, how underserved), COMPETITOR USING IT: NO, EVIDENCE
   IT COULD WORK (search volume, Reddit discussions, adjacent product success, logical deduction from the avatar).
At least 8 survivors beyond what the competitor runs. Also return the universe lists (avatars, the 6 pain kinds,
desires), the count of combinations crossed / kept / discarded, and per emotional entry its H ids or why none survived.
Return as text.
```

### α-synthesis — opportunity synthesis (Step Alpha 2.3; to Lead B with `SendMessage`, else `model: "opus"`, `effort: "low"`)
**Launch:** only after the operator's ChatGPT result is saved to `00_alpha\chatgpt\CHATGPT_RAW.md` (GATE α).
```
<COMMON HEADER>
Task: Step Alpha 2.3 OPPORTUNITY SYNTHESIS. Spec: <skill>\references\19-step-alpha.md §2.3.
Inputs: <PRODUCT_DIR>\00_alpha\chatgpt\CHATGPT_RAW.md (verbatim market data), analysis2\2.1_hidden_angles.md,
analysis1\1.1_customer.md, 1.3_congruence.md, 1.4_angle_cards.md.
1. VALIDATED HIDDEN ANGLES: 2.1 angles the raw data confirms → per H id `RESEARCH VERDICT: VALIDATED` + RESEARCH EVIDENCE
   (verbatim quotes + sources, mainly the HIDDEN ANGLE EVIDENCE table).
2. KILLED HIDDEN ANGLES: no demand in the data → `RESEARCH VERDICT: KILLED` + what was searched / "no data found".
3. EMERGENT ANGLES (E1..En): pains, desires or use cases found only in the raw data: EMERGENT ANGLE, AVATAR, PAIN/DESIRE,
   EMOTIONAL ENTRY, ESTIMATED POTENTIAL, EVIDENCE (quotes + source + frequency); none → one line "NONE FOUND: why".
4. LANGUAGE BANK: the strongest verbatim quotes (never paraphrased, source + platform kept) by use: hook-ready,
   headline-ready, objection-ready, testimony-ready; at least 5 per group.
5. For dossier Part 2: opportunity angle cards O1..On (1.4 card fields + BUILT FROM: every validated H and every E gets
   a card, plus congruence gaps worth building), underserved avatars (AVATAR fields, IDs continue after 1.1, + WHY
   UNDERSERVED + EVIDENCE), untapped emotional territories (entry, competitor uses it?, our H/E ids, raw-data evidence),
   funnel congruence gaps (every LOW/MED path from 1.3 → what the page drops → our congruent page, or "NO GAPS: why").
Return as text (→ analysis2\2.3_synthesis.md).
```

---

## 1 Capture agent (Phase 1)
**Launch:** immediately after preflight. **Reference:** 03 §capture.
```
<COMMON HEADER>
Task: capture the competitor product page <COMPETITOR_URL>.
1. python -I <skill>\scripts\capture_page.py "<COMPETITOR_URL>" --out "<PRODUCT_DIR>\02_competitor\page"
2. python -I <skill>\scripts\screenshot.py "<COMPETITOR_URL>" --out "<PRODUCT_DIR>\02_competitor\page" --name comp
3. Same for the competitor home page: capture_page.py "<COMPETITOR_HOME>" --out "<PRODUCT_DIR>\02_competitor\home"
   and screenshot.py "<COMPETITOR_HOME>" --out "<PRODUCT_DIR>\02_competitor\home" --name home
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
Fit the names to <PRODUCT_DIR>\00_alpha\ALPHA_DOSSIER.md: 3.2 avatar cards, 1.5 emotional landscape, 1.6 mechanism,
3.5 customer language bank.
Return: table name | possessive sentence | why it fits | risk (if any). Mark your top 5.
```

## 4 Conversion architect (Phase 3, A1)
**Launch:** right after the gate (needs capture files). **Model: `"opus"` (Opus 4.6) — always.** **Reference:** 03 (SECTION SPEC format + ADAPTATION BLUEPRINT), templates/SECTION_SPEC.md.
```
<COMMON HEADER>
Task: TWO deliverables — (1) the SECTION SPEC of the competitor page, then (2) an ADAPTATION BLUEPRINT for our page.
Inputs: <page dir>\capture.md, capture.json, copy.txt, p.html, screenshots (desk chunks, mobile sheets),
<media dir>\_sheet.jpg, and <PRODUCT_DIR>\00_alpha\ALPHA_DOSSIER.md: 3.1 angle cards + 1.10/2.4 funnel congruence
(page architecture), 1.4 objections + 3.5 objection-ready language (FAQ/objection handling), 1.6 mechanism,
3.2 avatar cards, 1.5 emotional landscape, 3.5 language bank.
Also read: <skill>\books-playbooks\*.html headings (grep for relevant conversion principles).

PART 1 — COMPETITOR SECTION SPEC (mapping their framework):
Follow <skill>\references\03-competitor-page-analysis.md and the template
<skill>\templates\SECTION_SPEC.md exactly: every section top→bottom (incl. announcement, header, sticky ATC,
popups, footer) with LAYOUT / COMPONENTS / TYPOGRAPHY / VISUAL DETAILS / IMAGE POSITIONS / CONVERSION ROLE / MOBILE,
then FUNNEL PSYCHOLOGY (price math, urgency, trust, social proof, upsell, narrative arc), ANGLE ARCHITECTURE
(angle table, above-the-fold, gap angles, landing decision, objection map, mechanism section), IMAGE MAP,
COPY INVENTORY (every string verbatim, tagged), APPS.

PART 2 — ADAPTATION BLUEPRINT (how our page will be DISTINCT):
Study the competitor's framework (section roles, conversion mechanics, funnel psychology) and design our ADAPTED
version. The test: an AI comparing our shop and the competitor's should see two completely different things.
For each section, specify:
  - OUR SECTION: renamed role, different layout/grid, different visual pattern, different component choices
  - CONVERSION MECHANICS PRESERVED: the trigger, objection, proof and action the section carries (same job, different execution)
  - WHAT CHANGES: section order shifts, layout flips, typography choices, color application, component swaps,
    spacing rhythm, visual hierarchy reordering — everything that makes it visually and structurally distinct
  - WHAT STAYS: the conversion principle, the dossier angle/avatar it serves, the emotional arc position
  - ANGLE ROLE: same mapping as in the spec (V#/O# · AV# · objection · congruence role)
Include: our SECTION ORDER (different from theirs), our VISUAL IDENTITY RULES (layout patterns, spacing rhythm,
component vocabulary — all different from the competitor), our FUNNEL FLOW (same psychology, different execution).
Use the dossier data (avatars, pains, desires, language bank) to make the page speak to our customers more directly
than the competitor does — customers should feel listened to and understood.
Return BOTH documents as text (the master saves them to SECTION_SPEC.md and ADAPTATION_BLUEPRINT.md).
```

## 5 Copywriter (Phase 3, A2)
**Launch:** when SECTION_SPEC.md + ADAPTATION_BLUEPRINT.md are saved. **Model: `"opus"` (Opus 4.6) — always.** **Reference:** 03 §copy rules, 13 (playbooks), 09 for tone parity.
```
<COMMON HEADER>
Task: write every word of the <BRAND> product page in <language/market>. FULLY ORIGINAL — no title, headline,
subtitle or body text may be word-for-word identical to the competitor's.
Inputs: <page dir>\SECTION_SPEC.md (COPY INVENTORY = reference for slot structure and word budget),
<page dir>\ADAPTATION_BLUEPRINT.md (our adapted section structure — write for THIS structure, not the competitor's),
copy.txt (competitor wording — for reference only, never copy), BRIEF.md (brand, title, offer, guarantee),
ALPHA_DOSSIER.md (3.1 angle cards, 1.1 awareness + sophistication per avatar, 1.2 pains, 1.3 desires,
1.5 emotional landscape, 3.5 language bank incl. objection-ready phrases, 3.3 hook library).
BEFORE WRITING: read the relevant sections of <skill>\books-playbooks\*.html (Schwartz awareness/sophistication
approach, Bencivenga proof arsenal, Halbert word pictures, Kennedy emotional triggers, Hopkins specifics).
Rules:
- Write from the Step Alpha dossier data (language bank, pains, desires, emotional landscape) and the playbooks,
  NOT from paraphrasing competitor strings. The customer's own words are your primary source.
- Same persuasion JOB per section (trigger, objection, proof, action) but fully original EXECUTION.
- Claims at the SAME strength (never soften, never add caveats) — carry competitor claims as-is (rule 1).
- Simple vocabulary, direct response, short lines; total length within ±10% of competitor per section.
- Customers should feel listened to, understood and recognized — use their actual language from 3.5.
- Strong promises backed by the dossier's mechanism (1.6) and proof points.
- Testimonials as new people whose details match the image map; different stories, same objection-handling job.
- Prices/currency for <MARKET>; brand name replaces theirs.
- State the playbook principle used per piece (e.g. "V2 · AV2 problem aware, stage 4 → Schwartz: mechanism headline").
ORIGINALITY CHECK: before returning, compare every title, headline, subtitle and body line against the competitor's
COPY INVENTORY. Flag and rewrite any word-for-word or near-identical matches.
Return: a copy deck following the ADAPTATION BLUEPRINT's section order, each slot labelled with its adapted section
ID (so the builder can map it), angle card tag per string, plus word count vs competitor and originality report.
```

## 6 Builder (optional, Phase 3, A3)
The master usually builds (it owns the repo). Delegate only big custom sections, with explicit file paths. **Model: `"opus"` (Opus 4.6) — always** (section design/adaptation requires the strongest judgment).
```
<COMMON HEADER>
You MAY write these theme files only: <list of new files, e.g. sections/<slug>-comparison.liquid>.
Task: implement <component> per the ADAPTATION BLUEPRINT (not a pixel clone of the competitor) and
<skill>\references\04-product-page-build.md patterns (vars snippet, media snippet, scoped CSS, schema settings +
presets, mobile behaviour). Build the ADAPTED layout, visual patterns and component choices specified in the
blueprint. The section must serve the same conversion role as the competitor's equivalent but look and feel distinct.
Then run `shopify theme check` and report only offenses in your files. Do not touch templates or settings.
Return: files written, settings/blocks available, check result, distinctiveness notes (what differs from competitor).
```

## 7 Product-image agent (Phase 3, B)
**Launch:** right after the gate. **Reference:** 05, tools-kie.
```
<COMMON HEADER>
KIE_API_KEY: <key or "in env">. Credits budget for this agent: <n>.
Task: produce <BRAND>'s product gallery. Messaging and people shown follow ALPHA_DOSSIER.md 3.2 avatar cards and
3.1 angle cards.
1. Packshot FIRST: isolate our product (from <best gallery image or supplier photo>) on pure white, no text or logo on
   the frame, 1:1 2K → <PRODUCT_DIR>\03_product-images\<slug>-packshot.png. Read it; redo if wrong.
2. OWN CONVERSION GALLERY (05 §16, default): map the competitor gallery in <media dir> (the job of each slide, its claims), then write
   <PRODUCT_DIR>\03_product-images\GALLERY_PLAN.md (7–10 slides: job, angle V/O id, objection killed, headline +
   support text from the copy chief on Opus 4.6, proof, visual, why it beats the competitor's slide), then one job per slide
   in <PRODUCT_DIR>\scratch\jobs_gallery.json. Use one design system across the slides, 6 % safe margins, mobile-legible
   headlines, the real packaging from the packshot, no overlaid logo, correct spelling, 1:1 2K. CONCEPT-REMAKE of each
   competitor image (1:1 remakes) only when the brief asks for a v1 A/B set.
3. SAMPLE GATE (00 §18): run only the packshot + 3–4 representative slides first, contact sheet → STOP and return for the operator's OK.
   After OK: python -I <skill>\scripts\kie_jobs.py <jobs> "<PRODUCT_DIR>\03_product-images" (the rest)
4. Contact sheet → Read → fix with KEEP-EDIT jobs (text-only fixes) → move replaced versions once to <area>\archive\v<N>_<reason>\.
Return: final file list in gallery order (one line each: what it shows), credits spent, any flaw left.
```

## 8 Page-image agent (Phase 3, C)
**Launch:** after the gate (needs the image map or the media agent's list). **Reference:** 06, tools-kie.
```
<COMMON HEADER>
Task: produce page images for <BRAND>. Messaging and people shown follow ALPHA_DOSSIER.md 3.2 avatar cards and
3.1 angle cards.
1. Testimonial/lifestyle images listed in the image map: Kie remakes (same framing, DIFFERENT people), 1:1 2K →
   <PRODUCT_DIR>\04_page-images. Keep each person consistent with the testimonial text slot (gender/age/relationship).
2. GIFs: confirm raw files exist in media\, WebP versions in 04_page-images (fetch_media.py --webp-dir).
3. Export theme-ready copies: JPG q80–84 progressive, 800–1400 px, named <slug>-<role>.jpg / .webp, into
   <PRODUCT_DIR>\04_page-images\theme\ (the master copies them into the theme's assets/).
Return: mapping image-map position → file, credits spent.
```

## 15 Copy chief (Opus 4.6, playbooks)
**Launch:** whenever persuasive copy is written (AD_VARIANTS, AD_COPY, page/home copy deck, image claims). **Model: `"opus"` (Opus 4.6, `claude-opus-4-6`) — always.** **Reference:** 13, 00 §1.
```
<COMMON HEADER>
You are the COPY CHIEF. Read <PRODUCT_DIR>/00_alpha/ALPHA_DOSSIER.md first (mandatory: awareness state + sophistication
per avatar from 1.1 decide the copy approach; 3.1 angle cards, 3.3 hooks, 3.5 language bank, 1.5 emotional landscape),
then the relevant sections of <SKILL>/books-playbooks/*.html (grep headings). Write specific
direct-response copy with NO softness, calibrated to the competitor's proven framework and promise level (they scale);
sharpen with the playbooks, push promises further only where the angle needs it; no hedges or caveats; claims at full
strength. The playbooks and the Step Alpha language bank are the PRIMARY sources — not the competitor's copy.
EVERY piece must be FULLY ORIGINAL — no word-for-word matches with the competitor's copy. Run an originality check
against the competitor's COPY INVENTORY before finalizing: flag and rewrite any identical or near-identical strings.
Keep the given structure/format; return the copy + one line per piece naming the playbook principle used +
originality confirmation.
```

## 10 Ad-creative agent (Phase 3, D2)
**Launch:** after the gate, once the packshot exists (Step Alpha has passed). **Reference:** 08, tools-kie.
```
<COMMON HEADER>
KIE_API_KEY: <…>. Credits budget: <n> (top-5 at 2K = 50; 20 × 4:5 1K = 120).
Task: create 25 Meta image ads for <BRAND>.
0. FIRST write 05_ads/AD_VARIANTS.md (08 §1b): for all 25 ads, original headline → our almost-similar variant headline,
   original design → our design variant, and the angle card ID it serves (ALPHA_DOSSIER.md 3.1: V.. validated or O..
   opportunity; hooks from 3.3, phrases from 3.5). Return it and STOP; generate only after the operator approves.
1. Top 5 (ranks 1–5): jobs with TWO references [competitor ad file NN_<id>.*, our packshot], same aspect ratio and format,
   but the APPROVED variant headline and design variant (≈80–90% similar, not a copy), new faces, no competitor brand.
2. 20 more: pick formats × hooks from the dossier (1.7 inventory, 1.9 ad copy patterns, 3.3 hook library) and the
   top-30 sheet (selection matrix in 08), spread across the angle cards; write one detailed spec per
   ad (layout zones %, verbatim text, colors, fonts, people, product placement); packshot attached to EVERY job;
   4:5 at 1K.
3. Run kie_jobs.py into <PRODUCT_DIR>\05_ads\generated (names ad-NN-<slug>), contact sheets, Read, fix.
Return: table ad | angle card | format | hook | headline on image | file, credits spent, flaws left.
```

## 11 Ad-copy agent (Phase 3, E)
**Launch:** after the gate (ranking.json captions and ALPHA_DOSSIER.md exist). **Reference:** 09, templates/AD_COPY.md.
```
<COMMON HEADER>
Task: take the competitor's ad copy framework from ALPHA_DOSSIER.md 1.9 (ad copy patterns) and the captions in
ranking.json (titles, descriptions, CTAs), and write <BRAND>'s copy in <language>, one copy set per angle card (3.1),
hooks from 3.3, language bank + objection-ready phrases from 3.5, following 09: framework beats table, Primary text A (mirrors the structure 1:1), Primary text B
(short), 5 headlines (star top 2), link description, CTA rotation. Claims at the same strength; no caveat notes.
Return the full AD_COPY.md content as text.
```

## 12 Visual QA agent (Phase 4)
**Launch:** after the first build + renders. **Reference:** 10.
```
<COMMON HEADER>
Task: QA our build against the ADAPTATION BLUEPRINT and check DISTINCTIVENESS from the competitor.
Inputs: competitor screenshots <page dir>\comp_*.png / sheets; our renders <scratch>\qa\ours_*.png and buy-box mock
screenshot; SECTION_SPEC.md, ADAPTATION_BLUEPRINT.md.
Two checks per section at desktop and mobile:
1. BLUEPRINT FIDELITY: does our section match the ADAPTATION BLUEPRINT's layout, components, visual pattern and
   conversion role? Flag deviations from the blueprint.
2. DISTINCTIVENESS: would an AI comparing our page and the competitor's see two DIFFERENT pages? Flag any section
   that looks too similar to the competitor (same layout, same visual pattern, same component arrangement).
Also check: conversion mechanics preserved (trigger, objection, proof, action per section), mobile behaviour,
component states, image positions/ratios. Ignore harness artefacts listed in 10-qa-and-delivery.md §2.
Return a table: SECTION | CHECK (blueprint/distinctiveness/conversion/mobile) | ISSUE | SUGGESTED FIX | SEVERITY.
```

## 13 Home-page builder (Phase 3, A4)
**Launch:** after the gate; it can write HOME_SPEC + copy immediately and build once A3's settings and reusable
sections exist. **Model: `"opus"` (Opus 4.6) — always.** **Reference:** 11, 04.
```
<COMMON HEADER>
You MAY write: templates/index.json (or index.<slug>-v2.json if the live home has ad traffic), new
sections/<slug>-*.liquid, blocks/<slug>-*.liquid, snippets/<slug>-*.liquid, assets/<slug>-home-*; you may extend
existing <slug>-* sections with OPTIONAL settings only. No git commands, no theme push/pull (the master does that).
Task: build an ADAPTED version of the competitor home <COMPETITOR_HOME> following <skill>\references\11-home-page.md:
1. Read <PRODUCT_DIR>\02_competitor\home\ (capture + screenshots); write the HOME SPEC with an ADAPTATION section
   (how our home differs: different section order, different hero approach, different layout patterns, different
   visual identity — the test: an AI comparing both homes sees two different pages). Return it as text.
2. Map each section: reuse <slug>-* sections → native theme sections → new <slug>-* sections. Apply the product
   page's ADAPTATION BLUEPRINT visual identity rules for consistency across our store.
3. Copy: FULLY ORIGINAL (no word-for-word matches with competitor), claims at the same strength, consistent with the
   product page copy and BRIEF offer; write from the dossier data (3.5 language bank, 3.2 avatars, 3.1 angle cards)
   and books-playbooks principles. Customers should feel listened to and understood.
4. Images: reuse 03_product-images / 04_page-images / packshot; Kie only for essential missing visuals (budget <n>).
5. Build index.json with a Python builder (rich text in <p>), theme check (no new offenses), local render +
   distinctiveness comparison (NOT similarity check — confirm our home looks different from theirs), fix.
Return: HOME_SPEC text (with adaptation section), section mapping table (competitor section → our adapted section,
native/custom), files written, images used/credits, theme check + distinctiveness QA notes, operator to-dos.
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

## 16 Advertorial builder (Phase 3, A5 — only when advertorial funnel detected)
**Launch:** after A1 (needs adaptation blueprint + dossier); skip if no advertorial funnel in BRIEF.md. **Model: `"opus"` (Opus 4.6) — always.** **Reference:** 22.
```
<COMMON HEADER>
Task: build adapted advertorial/pre-sell landing pages for <BRAND>. The competitor uses advertorial funnels
(ads → advertorial → product page); we build our own version — same conversion psychology, completely
different execution.
Inputs: <PRODUCT_DIR>\02_competitor\advertorials\ (captured competitor advertorials + ADVERTORIAL_INVENTORY.md),
<page dir>\SECTION_SPEC.md + ADAPTATION_BLUEPRINT.md (visual identity rules for store consistency),
<PRODUCT_DIR>\00_alpha\ALPHA_DOSSIER.md (3.1 angle cards, 3.5 language bank, 1.1 avatars awareness/sophistication,
1.4 objections, 1.5 emotional landscape, 1.6 mechanism, 3.3 hook library, 1.3 congruence incl. advertorial paths).
BEFORE WRITING: read the relevant sections of <skill>\books-playbooks\*.html (Halbert "personal letter" for
editorial voice, Hopkins "editorial advertising" for advertorial tone, Schwartz awareness for entry point).
Per angle card that the competitor serves with an advertorial:
1. ADVERTORIAL FRAMEWORK MAP: extract the competitor's advertorial beats, editorial conventions, tone, word count, claims.
2. ADVERTORIAL ADAPTATION BLUEPRINT: our version — different editorial style, story structure, visual identity,
   publication name; same conversion psychology (problem → mechanism → proof → CTA). The test: an AI comparing
   both advertorial pages sees two completely different articles.
3. WRITE: fully original editorial copy from Step Alpha data (language bank, pains, avatar language, emotional
   landscape) + playbooks. Claims at full strength. No word-for-word matches with competitor.
4. BUILD: as Shopify page template `templates/page.<slug>-advertorial-<angle-id>.json` or custom Liquid page.
   Must render complete with zero admin setup. Responsive (mobile-first). Add noindex meta.
   Visual identity consistent with the product page's adaptation blueprint.
5. ORIGINALITY CHECK: compare against competitor's advertorial text — flag and rewrite any matches.
Return: per advertorial: framework map, adaptation blueprint, copy, files written, angle card served,
congruency assessment (read the ad → advertorial → product page path), originality report.
```

---

## Handling returns
- Save returned documents immediately to their target paths (Step Alpha files in `00_alpha/` per 18 §1, SECTION_SPEC.md, ADAPTATION_BLUEPRINT.md, AD_VARIANTS.md, AD_COPY.md, copy deck).
- Verify claims of success: open generated images/contact sheets yourself before reporting them as done.
- **Originality gate:** verify that no returned copy (page deck, home deck, ad copy, advertorial copy, image claims) contains word-for-word matches with the competitor's copy inventory. If matches are found, send the piece back to the copy chief for rewriting before saving.
- **Advertorial congruency:** for each A5 return, read the full ad → advertorial → product page path and confirm the story flows without jarring hops. Send back for revision if the advertorial's CTA promise doesn't match the product page's above-the-fold content.
- If an agent stalls or fails, resume it with `SendMessage` (keeps its context) rather than starting a new one.
- Update BRIEF.md progress after each return.
