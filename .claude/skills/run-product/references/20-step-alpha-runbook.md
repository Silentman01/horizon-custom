# 20 — Step Alpha runbook (how this skill runs the spec)

The spec is [19-step-alpha.md](19-step-alpha.md): the operator's text, byte-identical, never edited. It defines
every field, table, count and checkbox. This file says **how** the skill executes it: inputs, order, who does
what, which file each part lands in, and which check proves it. Where the two seem to differ, the spec wins.
Spec pointers below give its heading and line range (the file never changes, so line numbers are stable).

Operator rule: **before building anything, run Step Alpha.** Nothing is built or generated until α6 passes: no
branding, names, copy, section spec, pages, images, ads, ad copy, videos, CSV, checkout header or policy
transform (spec lines 1–26 and 794). Phase 1 raw-data gathering (capture, media, Brandsearch, policy fetch) is allowed.

## Contents
1. Rules for every Alpha step
2. Folder and files
3. Who does what
4. α0 — Inputs
5. α1 — Analysis 1: competitor intelligence
6. α2 — Hidden angle discovery
7. α3 — ChatGPT market research prompt
8. GATE α — the operator runs the prompt
9. α4 — Opportunity synthesis
10. α5 — The dossier
11. α6 — Quality gate
12. Who reads what downstream
13. Coverage table (spec → step → file → check)

---

## 1. Rules for every Alpha step
- **Every field of every spec block is filled**, for every item. No "[...]", "TBD" or empty field; when the ad
  has nothing (no description), write `none in ad`. `alpha_gate.py` fails on leftovers.
- **Verbatim stays verbatim.** Ad copy, hooks, VO, CTA text, testimonials and customer quotes are copied
  exactly, with their source. Never paraphrase or translate them; claims stay at full strength (00 §1).
- **IDs everywhere:** avatars `AV1..`, ads by inventory short id (`M1..` video, `S1..` static/carousel/text;
  the Brandsearch id stays in `ad_inventory.json`), validated angle cards `V1..`, opportunity cards `O1..`,
  hidden angles `H1..`, emergent angles `E1..`. Downstream steps retrieve by these IDs.
- **Every ad, not a sample.** The inventory, video analysis, static analysis, congruence map and hook library
  cover every ad in `ad_inventory.json` `ads`. Only exact duplicates (same creative and copy) may share a block,
  with all their IDs listed.
- **Sub-agents return documents as text** when file writes are refused; the coordinator saves them (16 §1).
- **Credits:** check balances before paid calls, stay inside any credit freeze, report spend (18 §2).
  Brandsearch `transcribe_ad` / `download_ad` 1 credit each. Gemini is not used in Step Alpha (operator 2026-11-10): video frameworks come from the transcript.

## 2. Folder and files
```
PD/00_alpha/
  ALPHA_DOSSIER.md            final dossier (α5), from templates/ALPHA_DOSSIER.md
  ad_inventory.json           every ad (α0): header + one record per ad
  transcripts/<ad_id>.txt     one per video ad (α0)
  analysis1/  1.1_customer.md · 1.2_ad_inventory.md · 1.2_video_ads.md · 1.2_static_ads.md ·
              1.2_patterns.md · 1.3_congruence.md · 1.4_angle_cards.md
  analysis2/  2.1_hidden_angles.md · 2.3_synthesis.md
  chatgpt/    CHATGPT_PROMPT.md (α3) · CHATGPT_RAW.md (GATE α, operator's paste, verbatim)
PD/05_ads/competitor/raw/footprint/   raw Brandsearch footprint dumps (unedited)
PD/05_ads/competitor/videos/<ad_id>.mp4 · images/<ad_id>.<ext>   ad media (free downloads)
```
`ad_inventory.json` shape (written by `alpha_gate.py inventory`, see [tools-brandsearch](tools-brandsearch.md#complete-ad-footprint-for-step-alpha-phase-13)):
- `header`: `counts` (per platform/status/format, total, excluded, review), `pagination_totals`, `gaps`,
  `pull_date`, `platforms_checked`, `expected_total`.
- `ads[]`: `id` (Brandsearch), `short_id` (M1.. video, S1.. static/carousel), `platform`, `format` (video / static /
  carousel), `status`, `start`, `end`, `run_days`, `reach_rank`, `duplicate_count`, `page`, `landing_url`, `caption`
  {primary_text, headline, description, cta}, `video_url`, `image_url`, `transcript_url`, `dashboard_url`,
  `video_file`, `image_file`, `transcript` (`transcripts/<id>.txt`, video only), `angle`, `avatar` (empty until α1.2), `notes`.
- `excluded[]` (other products, each with `reason`) and `review[]` (must be empty before α6).

## 3. Who does what
| Who | Model | Alpha work |
|---|---|---|
| Coordinator | session model | α0 (all Brandsearch calls, inventory, transcripts), relays tags between leads, GATE α, α5 merge, α6 gate, BRIEF.md |
| Lead A (Store) | Opus, low | α1.1 customer intelligence; α1.3 funnel congruence (page side first, every ad path once the 1.2 tags arrive) |
| Lead B (Growth) | Opus, low | α1.2 advertising intelligence (runs the analyst batches); α1.4 angle cards; α2 hidden angles; α3 prompt; α4 synthesis (via `SendMessage`, else a fresh Opus low agent) incl. Part 2 items |
| α-analyst | Sonnet | 1.2 video + static blocks for every ad, ~15 ads per batch, batches in parallel |
| α-angles | Sonnet | 2.1 angle explosion |
| Haiku worker | Haiku | ffprobe durations and `alpha_gate.py beats` per video transcript |

Briefs: [subagent-briefs §Step Alpha briefs](subagent-briefs.md#step-alpha-briefs).
Order: [16 §1](16-orchestration.md#1-orchestration-model-coordinator--2-opus-leads--cheap-workers) ·
[17 Phase α](17-phases-and-streams.md#phase-alpha).

```
α0 coordinator ─► Lead A: 1.1 ─────────────┐                 ┌─► 1.3 every path ─┐
                └► Lead B: α-analyst ─────────► 1.2 + tags ─┘ (coordinator relays) ├─► Lead B 1.4 ─► α2 ─► α3
                                                                                      │
GATE α (operator, ChatGPT) ─► α4 Lead B ─► α5 coordinator ─► α6 gate ─► Phase 2 branding
```

<a id="alpha0-inputs"></a>
## 4. α0 — Inputs
Spec: "ANALYSIS 1" input line, [19](19-step-alpha.md) lines 33–34; 1.2 intro lines 200–202.
Coordinator, during Phase 1 ([07 Steps 7–9](07-ads-research-brandsearch.md#step-7--pull-the-complete-footprint-for-step-alpha),
recipe: [tools-brandsearch](tools-brandsearch.md#complete-ad-footprint-for-step-alpha-phase-13)):
1. Competitor URL(s) and the Phase 1 capture: `02_competitor/page/` (copy, testimonials, reviews, FAQ, imagery,
   pricing, offer, desktop + 390px screenshots) and `02_competitor/home/`.
2. The **complete ad footprint**: every Meta ad, active and inactive, every format; TikTok/Instagram when Brandsearch
   has them, else ads the operator provides; paged until exhausted; raw dumps in `05_ads/competitor/raw/footprint/`.
3. `alpha_gate.py inventory … --fetch-videos --fetch-images --fetch-transcripts` → `ad_inventory.json`, media files.
   Every `review` row moved to `ads` or `excluded` with a reason.
4. A **transcript of every video ad** in `transcripts/<ad_id>.txt` (`transcript_url` free → `transcribe_ad` 1 credit →
   local `video_transcribe.py`); credits checked first.
5. The top-30 ranking (07 Steps 1–6, `rank_ads.py`) still runs for D2 and video picks; it is not the inventory.
6. Launch Lead A α and Lead B α in one message with paths to all of the above.

Done when: `alpha_gate.py inventory` shows 0 to review, 0 transcripts missing, 0 video files missing, and the header
totals match Brandsearch (or the gap is recorded in `header.gaps` and BRIEF.md).

## 5. α1 — Analysis 1: competitor intelligence

### 5.1 — 1.1 Customer intelligence (Lead A → `analysis1/1.1_customer.md`)
Spec: 1.1 lines 36–193. Read every signal: product page copy, ad copy (`caption` of every record), video
transcripts, testimonials, reviews, FAQ, imagery, pricing, offer structure, language patterns (lines 41–44).
- **Avatars** ([AVATARS / ICPs](19-step-alpha.md#avatars--icps), lines 46–74): one block per distinct persona, found
  from distinct ad angles, testimonial profiles and pain points addressed. All 6 fields: AVATAR (`AV1 — name`),
  DEMOGRAPHICS (age, gender skew, location, income signals and what they are derived from), PSYCHOGRAPHICS (values,
  beliefs, routines, media, trusted brands, health attitudes, shopping behaviour, decision style), TRIGGER EVENT,
  AWARENESS STATE (Schwartz, Most Aware → Unaware), SOPHISTICATION (Schwartz stage, claims already heard). Add
  CUSTOMER LANGUAGE (verbatim quote + source) — the gate needs it. Minimum 2.
- **Pain points** ([PAIN POINTS](19-step-alpha.md#pain-points), lines 76–100): every pain from every surface. PAIN POINT
  as the felt experience, never the clinical label; SOURCE (ad ID, page section, testimonial); FREQUENCY = count across
  page copy + ad copy + transcripts + testimonials/reviews/FAQ (high = core, low = secondary); EMOTIONAL WEIGHT
  (headline pain or supporting mention); AVATAR (AV id); CUSTOMER LANGUAGE (exact words, quoted, with source). RANK
  them 1..n by frequency × weight. Minimum 10.
- **Desires & dream outcomes** ([DESIRES & DREAM OUTCOMES](19-step-alpha.md#desires--dream-outcomes), lines 102–118):
  DESIRE (felt outcome), TYPE (functional / emotional / identity / social / aspirational), DREAM OUTCOME (6 months
  after, identity level), SOURCE, AVATAR, plus RANK and CUSTOMER LANGUAGE (verbatim). Minimum 5.
- **Objections** ([OBJECTIONS](19-step-alpha.md#objections), lines 120–138): every resistance the competitor anticipates.
  OBJECTION, TYPE (price / efficacy / trust / safety / effort / social judgment / alternatives / "is this real" /
  shipping / returns), HOW COMPETITOR HANDLES IT (FAQ, guarantee, testimonial, comparison, mechanism proof), WHERE IN
  FUNNEL (ad / landing page / product page hero / product page body / FAQ / checkout), STRENGTH 1–5, plus GAP (what
  stays open; the dossier heading asks "+ gaps"). Minimum 5.
- **Emotional landscape** ([EMOTIONAL LANDSCAPE](19-step-alpha.md#emotional-landscape), lines 140–169): all 6 trigger
  types — fear, desire, identity, frustration, curiosity, disgust — each with the competitor's actual lines.
- **Unique mechanism** ([UNIQUE MECHANISM (UMS/UMP)](19-step-alpha.md#unique-mechanism-umsump), lines 171–193):
  MECHANISM, MECHANISM NAME (branded or "unbranded"), MECHANISM STORY (who discovered it, age of the science, what
  conventional wisdom gets wrong, why mainstream doesn't know), MECHANISM PROOF, SCHWARTZ TECHNIQUE (Mechanization /
  Concentration / Redefinition / Identification, and how).
Lead A returns 1.1 first; the coordinator saves it and sends the AV list to Lead B.

### 5.2 — 1.2 Advertising intelligence (Lead B → `analysis1/1.2_*.md`)
Spec: 1.2 lines 195–291.
1. **Transcript pass** (Haiku worker): frameworks are read from the transcript; Gemini is not used in Step Alpha
   (operator 2026-11-10). Per video: real length `ffprobe -v error -show_entries format=duration -of csv=p=0
   <ad_id>.mp4` (when the file exists), then `python -I <skill>/scripts/alpha_gate.py beats
   "PD/00_alpha/transcripts/<ad_id>.txt" --duration <s>`: every timed line with timestamp, duration, % of total and
   WPS, HOOK DURATION, VO/TEXT SPLIT (speech vs no-speech gaps) and PACING. The analyst groups the lines into beats.
2. **Analyst batches** (α-analyst, Sonnet, ~15 ads each, in parallel until every ad is covered). Inputs per ad: its
   inventory record, the media file, the caption, and for video the transcript + its `beats` output.
   - **Video ad analysis** ([VIDEO AD ANALYSIS](19-step-alpha.md#video-ad-analysis), lines 214–245), one block per
     video, `AD ID` first, then all 13 spec fields: FRAMEWORK (named skeleton or a new one), BEAT MAP, FORMAT (from the
     spec's 19-item list), HOOK (exact words, type, open loop), HOOK DURATION, ANGLE, AVATAR, EMOTIONAL ARC (beat by
     beat), RETENTION MECHANICS (open loops, pattern interrupts, escalation, info drips, cliffhangers), VO/TEXT SPLIT,
     PACING, MUSIC/SFX (genre, energy curve, key moments), CTA (exact text, timestamp, urgency). Words, beats and timing come from the
     transcript (verbatim); FORMAT and what is on screen from the cover/caption (and the video file when there is one).
   - **Static / text ad analysis** ([STATIC AD / TEXT AD ANALYSIS](19-step-alpha.md#static-ad--text-ad-analysis),
     lines 247–271), one block per non-video ad (static, carousel, text), `AD ID` first, then all 11 spec fields: PRIMARY TEXT,
     HEADLINE, DESCRIPTION (exact, from `caption`), HOOK (first line, type, open loop), ANGLE, AVATAR, EMOTIONAL TRIGGER,
     PERSUASION SEQUENCE (PAS / AIDA / HSO / testimonial-proof-CTA / other), PROOF TYPE, CTA (exact + urgency),
     IMAGE FORMAT (spec list; read the image file).
   - Each batch also returns per-ad tags: id, angle, promise, avatar.
3. **Ad inventory** ([AD INVENTORY](19-step-alpha.md#ad-inventory), lines 204–212): Lead B writes the table, one row per
   `ads` record: AD ID │ FORMAT │ PLATFORM │ STATUS │ RUN TIME (`run_days`) │ ANGLE │ AVATAR. The coordinator writes the
   final angle/avatar back into `ad_inventory.json`. Row count = record count.
4. **Cross-ad pattern mining** ([CROSS-AD PATTERN MINING](19-step-alpha.md#cross-ad-pattern-mining), lines 273–291), one
   block over all ads: VALIDATED ANGLES (longest-running = proven with money), TESTING ANGLES (newer, shorter), DOMINANT
   HOOK TYPES (across winners: low `reach_rank`, long run), DOMINANT FORMATS (ratio), DOMINANT FRAMEWORKS, COMMON PROOF,
   COMMON CTA, CREATIVE VELOCITY (new ads per week from `start` dates), AD VOLUME (total, active, trajectory from
   `header.counts` and start dates), SATURATION (distinct advertisers/pages: `get_brand_advertisers` + other brands
   seen running this product).
5. Video framework patterns table (framework → ads, formats, longest run) closes 1.8 in the dossier.
Files: `1.2_ad_inventory.md`, `1.2_video_ads.md`, `1.2_static_ads.md`, `1.2_patterns.md`. The coordinator relays the
per-ad tags to Lead A.

### 5.3 — 1.3 Funnel congruence (Lead A → `analysis1/1.3_congruence.md`)
Spec: 1.3 lines 293–367.
- Page side first: what each landing page shows above the fold at desktop and 390px, where each promise and objection
  is handled. Every distinct `landing_url` in the inventory is captured (`capture_page.py`, `screenshot.py`, free);
  no URL in the data → the product page, marked `(assumed)`.
- **Map every ad → page path** ([MAP EVERY AD → PAGE PATH](19-step-alpha.md#map-every-ad--page-path), lines 309–331):
  one block per ad: AD, ANGLE, PROMISE, AVATAR, EMOTIONAL STATE AT CLICK, LANDING, FIRST SECTION THEY SEE, CONGRUENCE.
- **Score each path** ([SCORE EACH PATH](19-step-alpha.md#score-each-path), lines 333–351): table AD → PAGE PATH │
  CONGRUENCE (HIGH/MED/LOW per the definitions in lines 344–351) │ NOTES (why). Every ad has a row.
- **Congruence insights** ([CONGRUENCE INSIGHTS](19-step-alpha.md#congruence-insights), lines 353–367): HIGH angles
  (safest to copy), LOW angles (traffic leaked = opportunity), one page or one per angle, what a congruent page looks
  like per angle, and PAGE STRATEGY: one page with multi-angle architecture or angle-specific landing pages
  (`product.<slug>-<angle-id>.json` templates, 03/04).

### 5.4 — 1.4 Marketing angle map (Lead B → `analysis1/1.4_angle_cards.md`)
Spec: 1.4 lines 369–406. After 1.1 and 1.3 are saved. An angle = AVATAR × PAIN/DESIRE × EMOTIONAL TRIGGER × MECHANISM ×
PROMISE × PROOF STRATEGY (lines 377–378). One card per angle the competitor runs, every field: ANGLE (`V1 — name`),
CONFIDENCE HIGH/MEDIUM from run time and volume, AVATAR, PAIN/DESIRE, EMOTIONAL TRIGGER, ENEMY, MECHANISM, PROMISE,
PROOF, FUNNEL CONGRUENCE (from 1.3), ADS USING THIS (inventory IDs), HOOK TEMPLATES (quoted), CUSTOMER LANGUAGE
(quoted), OPPORTUNITY. Minimum 3 validated (HIGH/MEDIUM). Every ad's `angle` points at a card.

## 6. α2 — Hidden angle discovery (Lead B + α-angles → `analysis2/2.1_hidden_angles.md`)
Spec: Analysis 2 intro lines 408–415; 2.1 lines 417–500.
1. **Explosion** ([THE ANGLE EXPLOSION PROCESS](19-step-alpha.md#the-angle-explosion-process), lines 427–480), α-angles
   worker lists:
   - EVERY POSSIBLE AVATAR the competitor isn't targeting: other ages, genders, activity levels, professions, life
     stages, health conditions, motivations (lines 432–447).
   - EVERY POSSIBLE PAIN: primary, secondary, adjacent, surprising — physical, emotional, social, identity,
     convenience, financial (lines 449–454).
   - EVERY POSSIBLE DESIRE: performance, comfort, confidence, appearance, longevity, freedom, independence, social
     approval, identity, prevention, optimization (lines 456–461).
   - All 13 EMOTIONAL ENTRIES: fear, desire, identity, curiosity, frustration, contrarian, disgust, authority, social
     proof, mechanism, comparison, seasonal, life-event (lines 463–476).
2. Cross AVATAR × PAIN × DESIRE × EMOTION; discard weak combinations with a one-line reason (lines 478–480). The
   working file keeps the universe lists, the crosses, survivors and discards.
3. **Rate each survivor** ([RATE EACH HIDDEN ANGLE](19-step-alpha.md#rate-each-hidden-angle), lines 482–500): HIDDEN
   ANGLE (`H1 — name`), AVATAR, PAIN/DESIRE, EMOTIONAL ENTRY, ESTIMATED POTENTIAL (HIGH/MEDIUM/LOW on segment size,
   intensity, how underserved), COMPETITOR USING IT: NO, EVIDENCE IT COULD WORK. Minimum **8** beyond what the competitor
   runs. Lead B reviews and cuts.
4. For the dossier: the explosion-inputs block and the 13-entry table (each entry → its H ids, or "none survived — why").

## 7. α3 — ChatGPT market research prompt (Lead B → `chatgpt/CHATGPT_PROMPT.md`)
Spec: 2.2 lines 502–686. Claude Code has no access to Reddit, Quora, forums, Amazon reviews or Facebook groups, so
ChatGPT gathers raw customer language; its role is pure data gathering, no analysis (lines 506–516).
1. Copy everything below the cut line of [templates/CHATGPT_PROMPT.md](../templates/CHATGPT_PROMPT.md) into
   `chatgpt/CHATGPT_PROMPT.md` and fill every `{{placeholder}}` from α1/α2: product, category, market, competitor
   brands, avatars (1.1 + underserved from the explosion), top pains, desires, objections, validated angles (1.4), real
   subreddits / forums / Facebook group topics / Amazon competitor + adjacent products / search queries for these
   avatars, and **every hidden angle H1..Hn** with what to search for (category 8). Tailored = it names this product's
   pains, avatars and angles (lines 518–523).
2. Kept exactly as in the template (it carries the spec text): all 8 platform groups (lines 529–543); the 10 data
   categories with their counts and tags — pain 30-50 tagged platform, subreddit/forum, estimated demographic; desire
   20-30; objection 20-30; solution attempts with why they failed; trigger events 15-20; emotional expressions 20-30;
   idioms & slang; hidden angle validation; demographic signals; competitor mentions (lines 545–626); the exact OUTPUT
   FORMAT block (lines 628–673); the 6 "ChatGPT must" rules (lines 675–685).
3. Coordinator check: no `{{` left, nothing above the cut line copied (`alpha_gate.py` box 14 tests both and the
   required platforms/categories/counts/format/rules).

## 8. GATE α — the operator runs the prompt
Spec: "After the ChatGPT data returns" (line 691) is a hard dependency.
1. Coordinator sends the operator the full `CHATGPT_PROMPT.md` as ONE copy block plus one line: "Run this in ChatGPT
   (browsing / Deep Research on) and paste the full result back." Then **stops**; no α4 and no downstream step while
   waiting (15 §1).
2. If ChatGPT splits its answer ("CONTINUED"), the operator sends "continue" and pastes every part.
3. The coordinator saves the paste **verbatim** to `chatgpt/CHATGPT_RAW.md` (all parts in order, nothing edited).
4. If a category is far under its count or a hidden angle has no row, the coordinator may give the operator one
   follow-up prompt for the gaps; its answer is appended verbatim.
Resuming: a run stopped here re-sends the same prompt block and waits (15 §3).

## 9. α4 — Opportunity synthesis (Lead B via `SendMessage`, brief α-synthesis → `analysis2/2.3_synthesis.md`)
Spec: 2.3 lines 687–719. Inputs: `CHATGPT_RAW.md`, 2.1, 1.1, 1.3, 1.4.
- **Validated hidden angles** (lines 694–698): each H angle with demand in the raw data → `RESEARCH VERDICT: VALIDATED`
  plus RESEARCH EVIDENCE (quotes + sources, mainly from HIDDEN ANGLE EVIDENCE).
- **Killed hidden angles** (lines 700–703): no demand → `RESEARCH VERDICT: KILLED`, evidence = what was searched /
  "no data found".
- **Emergent angles** (lines 705–709): pains, desires or use cases only the raw data shows → `EMERGENT ANGLE: E1 — …`
  with AVATAR, PAIN/DESIRE, EMOTIONAL ENTRY, ESTIMATED POTENTIAL, EVIDENCE (quotes + source + frequency).
- **Language bank** (lines 711–719): the strongest verbatim quotes, source kept, in 4 groups: hook-ready,
  headline-ready, objection-ready (for FAQ and objection handling), testimony-ready (the model for future real
  testimonials). At least 5 per group.
- **Part 2 items** for the dossier: opportunity angle cards `O1..` (1.4 card fields + BUILT FROM: validated H, E, or a
  congruence gap), underserved avatars (AVATAR fields + WHY UNDERSERVED + EVIDENCE), untapped emotional territories,
  funnel congruence gaps (every LOW/MED path from 1.3 → what the page drops → our congruent page).

## 10. α5 — The dossier (coordinator → `PD/00_alpha/ALPHA_DOSSIER.md`)
Spec: ALPHA OUTPUT lines 721–764. Copy [templates/ALPHA_DOSSIER.md](../templates/ALPHA_DOSSIER.md); keep its
headings and order exactly (Part 1 1.1–1.11, Part 2 2.1–2.8, Part 3 3.1–3.6) and its block markers; repeat blocks per
item; delete every template example row.

**Assembler (Oragel run, 2026-11-12):** `python -I <skill>/scripts/assemble_dossier.py <PD> --title "<Product>" --context "<context line>"`
builds the whole dossier from the working files:
- **Part 1** comes from `1.1_customer.md` (`## 1.x` sections), `1.2_*`, `1.3_congruence.md` + `1.3_paths.md`, and `1.4_angle_cards.md`.
- **2.1** merges the RESEARCH VERDICT / EVIDENCE lines from `2.3_synthesis.md` into the H blocks, validated first.
- **2.2–2.8** are cut from the `## 2.x` sections of `2.3_synthesis.md`.
- **Part 3** tables are generated: 3.1 from the V+O cards, 3.2 from the avatars, 3.3 from every ad block's HOOK, 3.4 from every video block, 3.5 from the 2.6 groups.
- **2.5 and 3.6** are pasted verbatim.

Sub-headings in the inputs are demoted to `####`. The full letter bodies (`1.2_caption_families.md`) go in 1.9 as an appendix, so PRIMARY TEXT stays exact without being duplicated.

Pitfalls:
- **Markers:** mark the parts of `CHATGPT_RAW.md` with plain lines (`=== PART 1 of 2 … ===`), never HTML comments. The gate strips comments from the dossier but not from the raw file, so the 2.5 verbatim check fails.
- **French quotes:** French data uses « » quotes. The gate accepts them now; older gate copies did not.
- **Synthesis file:** keep the web supplement out of `2.3_synthesis.md`, in `chatgpt/WEB_SUPPLEMENT.md`. Otherwise it is swallowed into 2.8.

| Dossier section | Filled from |
|---|---|
| H1 `# <Product> — Step Alpha Intelligence Dossier` + context line | BRIEF inputs, inventory counts |
| 1.1 Avatars · 1.2 Pain Points (ranked) · 1.3 Desires (ranked) · 1.4 Objections (+ GAP) · 1.5 Emotional Landscape · 1.6 Unique Mechanism | `1.1_customer.md` |
| 1.7 Ad Inventory | `1.2_ad_inventory.md` (= `ad_inventory.json` `ads`) |
| 1.8 Video Frameworks (one block per video + framework patterns table) | `1.2_video_ads.md` |
| 1.9 Ad Copy Patterns (one block per non-video ad + the cross-ad pattern block) | `1.2_static_ads.md`, `1.2_patterns.md` |
| 1.10 Funnel Congruence (path maps, score table, insights) | `1.3_congruence.md` |
| 1.11 Validated Angle Cards | `1.4_angle_cards.md` |
| 2.1 Hidden Angles (explosion inputs, 13-entry table, H blocks with verdicts: validated first, then killed) | `2.1_hidden_angles.md` + `2.3_synthesis.md` |
| 2.2 Underserved Avatars · 2.3 Emotional Territories Untapped · 2.4 Funnel Congruence Gaps | `2.3_synthesis.md` (from 2.1 + 1.3) |
| 2.5 ChatGPT Raw Data | `CHATGPT_RAW.md` verbatim, inside the 5-backtick fence |
| 2.6 Language Bank (4 groups) · 2.7 Emergent Angles · 2.8 Opportunity Angle Cards | `2.3_synthesis.md` |
| 3.1 Angle Cards (every V and O card, one row each) | 1.11 + 2.8 |
| 3.2 Avatar Cards (every AV) | 1.1 + 2.2 |
| 3.3 Hook Library (the hook of every ad + templates from the cards) | 1.8, 1.9, 1.11, 2.8 |
| 3.4 Framework Library (every video framework + beat maps, with the ads using it) | 1.8 |
| 3.5 Customer Language Bank (hooks, headlines, objection handling, social proof) | 2.6 + 1.2/1.3 customer language |
| 3.6 ChatGPT Prompt | `CHATGPT_PROMPT.md` verbatim, inside the 5-backtick fence |

## 11. α6 — Quality gate (coordinator)
Spec: QUALITY GATE lines 766–794.
1. `python -I <skill>/scripts/alpha_gate.py "PD/00_alpha/ALPHA_DOSSIER.md"` (same as `check PD/00_alpha`). It prints
   PASS/FAIL per checkbox with reasons, WARN lines (e.g. raw data under the asked counts) and MANUAL lines, and exits 1
   on any FAIL.
2. Read every MANUAL line and judge it (psychographic depth, felt-language pains, mechanism analysis, platform
   completeness, verbatim copies, real integration, tailoring, retrieval).
3. Fail → back to the failing step (table below), fix, re-run. Pass → record in BRIEF.md: date, `16/16 PASS`, MANUAL
   read-through OK, counts (avatars, pains, ads, videos, V/H/E/O cards). Only then Phase 2 (branding) starts.

## 12. Who reads what downstream
| Step | Dossier sections |
|---|---|
| 02 Branding | 3.2 avatars, 1.5 emotional landscape, 1.6 mechanism, 3.5 language bank |
| 03/04 Section spec, copy, build | 3.1 angle cards + 1.10/2.4 congruence → page architecture; 1.4 objections + objection-ready language → FAQ; 1.6 → mechanism section; 3.5 → copy |
| 05/06 Images | 3.1 angle cards, 3.2 avatar cards |
| 08 Ad creatives | every variant maps to a V/O card; 3.3 hooks; 3.5 phrases |
| 09 Ad copy | 3.1 cards, 3.3 hooks, 3.5 language, objection phrases; one copy set per angle |
| 11 Home | 3.2 avatars, 3.1 angle cards |
| 13 Copy chief | whole dossier; awareness + sophistication per avatar (1.1) set the copy approach |
| 14 Video ads | 3.4 frameworks, 1.8 beat maps, 3.1 cards, 3.3 hooks; transcripts |

## 13. Coverage table (spec → step → file → check)
"gate N" = `alpha_gate.py` checkbox N. "MANUAL" = coordinator read-through (α6 step 2).

| Spec section (19, lines) | Runbook | Output file → dossier | Checker |
|---|---|---|---|
| Purpose, both analyses before anything fires (1–26) | top, §1, §11 | BRIEF gate row | α6 pass before Phase 2 |
| Analysis 1 input: URLs + ads via Brandsearch or operator (33–34) | §4 | `ad_inventory.json`, capture | gate 7 |
| 1.1 intro: every signal (36–44) | §5.1 | `1.1_customer.md` | MANUAL (gate 1–6) |
| 1.1 Avatars: 6 fields, distinct personas (46–74) | §5.1 | → 1.1, 3.2 | gate 1 (≥2, all fields, AV id, distinct, quoted language, AWARENESS STATE names a Schwartz level), gate 16 (3.2 covers all AV) |
| 1.1 Pain points: 6 fields, felt not clinical (76–100) | §5.1 | → 1.2 | gate 2 (≥10, all fields + RANK, quoted language); MANUAL felt/ranked |
| 1.1 Desires: 5 fields, 5 types (102–118) | §5.1 | → 1.3 | gate 3 (≥5, all fields, TYPE in the 5, quoted language) |
| 1.1 Objections: 5 fields, types, funnel places, 1–5 (120–138) | §5.1 | → 1.4 | gate 4 (≥5, all fields + GAP, STRENGTH 1–5, TYPE and WHERE IN FUNNEL from the spec lists) |
| 1.1 Emotional landscape: 6 triggers (140–169) | §5.1 | → 1.5 | gate 5 (one block, 6 fields) |
| 1.1 UMS/UMP: 5 fields, Schwartz technique (171–193) | §5.1 | → 1.6 | gate 6 (5 fields, names a technique); MANUAL |
| 1.2 Complete footprint, all platforms (200–202) | §4, tools-brandsearch | `raw/footprint/`, `ad_inventory.json` | gate 7 (no review rows, expected_total, gaps → MANUAL) |
| 1.2 Ad inventory table, 7 columns (204–212) | §5.2 step 3 | `1.2_ad_inventory.md` → 1.7 | gate 7 (columns, rows = records, every ad, no empty cell) |
| 1.2 Video ad analysis: transcript + 13 fields (214–245) | §4 step 4, §5.2 steps 1–2 | `transcripts/`, `1.2_video_ads.md` → 1.8, 3.4 | gate 8 (transcript + block per video, all fields, beat map timestamps and %, WPS number; FORMAT off the spec list → WARN), gate 16 (3.4 covers every video) |
| 1.2 Static / text ad analysis: 11 fields (247–271) | §5.2 step 2 | `1.2_static_ads.md` → 1.9 | gate 9 (block per non-video ad, all fields; trigger / proof type / image format off the spec lists → WARN); MANUAL exact copy |
| 1.2 Cross-ad pattern mining: 10 fields (273–291) | §5.2 step 4 | `1.2_patterns.md` → 1.9 | gate 10 (one block, 10 fields, numbers in velocity/volume) |
| 1.3 Map every ad → page path: 8 fields (309–331) | §5.3 | `1.3_congruence.md` → 1.10 | gate 11 (block per ad, all fields, HIGH/MED/LOW) |
| 1.3 Score each path + HIGH/LOW definitions (333–351) | §5.3 | → 1.10 | gate 11 (row per ad, valid score, notes) |
| 1.3 Congruence insights: 4 questions (353–367) | §5.3 | → 1.10, 2.4 | gate 11 (5 insight fields incl. PAGE STRATEGY), gate 16 (2.4 rows or NO GAPS) |
| 1.4 Angle cards: angle formula, 14 card fields, one per angle (369–406) | §5.4 | `1.4_angle_cards.md` → 1.11, 3.1 | gate 12 (≥3 HIGH/MEDIUM, all fields, V id, real ad IDs, quoted hooks/language), gate 16 (3.1 covers all) |
| Analysis 2 intro (408–415) | §6 | — | — |
| 2.1 Explosion: avatars, 6 pain kinds, desires, 13 emotional entries, cross + discard (417–480) | §6 steps 1–2, 4 | `2.1_hidden_angles.md` → 2.1 | gate 13 (explosion block 11 fields, 13-entry table filled); MANUAL every cross tried |
| 2.1 Rate each hidden angle: 7 fields, NO (482–500) | §6 step 3 | → 2.1 | gate 13 (≥8, all fields, H id, COMPETITOR USING IT = NO, potential HIGH/MEDIUM/LOW, EMOTIONAL ENTRY one of the 13) |
| 2.2 Why ChatGPT, pure data gathering, tailored (502–523) | §7 | `CHATGPT_PROMPT.md` → 3.6 | gate 14 (role line, every H id listed, 3.6 = file); MANUAL tailoring |
| 2.2 8 platform groups (529–543) | §7 step 2 | template | gate 14 (8 platform checks) |
| 2.2 10 data categories, counts, tags (545–626) | §7 step 2 | template | gate 14 (10 categories, 5 counts, pain tags) |
| 2.2 Output format (628–673) | §7 step 2 | template | gate 14 (10 output headings + pain table header); gate 15 WARN on raw counts |
| 2.2 ChatGPT must: 6 rules (675–685) | §7 step 2 | template | gate 14 (6 rule checks) |
| 2.3 After ChatGPT returns (691) | §8 | `CHATGPT_RAW.md` → 2.5 | gate 15 (raw file non-empty, 2.5 = raw verbatim) |
| 2.3 Validated / killed hidden angles (694–703) | §9 | `2.3_synthesis.md` → 2.1, 2.8 | gate 15 (verdict + evidence on every H; every validated H in an O card) |
| 2.3 Emergent angles (705–709) | §9 | → 2.7, 2.8 | gate 15 (E blocks with quoted evidence or NONE FOUND → MANUAL; every E in an O card) |
| 2.3 Language bank: 4 groups (711–719) | §9 | → 2.6, 3.5 | gate 15 (≥5 quoted rows with source per group), gate 16 (3.5 4 groups ≥5) |
| Dossier structure: Part 1–3, 25 sections, order (721–764) | §10 | `ALPHA_DOSSIER.md` | gate 16 (H1 + every heading in order, no extra ##/###, no placeholders, 2.2/2.3/2.4 filled, 3.1–3.6 coverage, working files exist) |
| Gate □ 1 — 2 avatars, psychographics, language (772–773) | §5.1 | 1.1 | gate 1 + MANUAL |
| Gate □ 2 — 10 pains, verbatim (774) | §5.1 | 1.2 | gate 2 |
| Gate □ 3 — 5 desires, verbatim (775) | §5.1 | 1.3 | gate 3 |
| Gate □ 4 — 5 objections, handling (776) | §5.1 | 1.4 | gate 4 |
| Gate □ 5 — 6 trigger types (777) | §5.1 | 1.5 | gate 5 |
| Gate □ 6 — mechanism extracted + analyzed (778) | §5.1 | 1.6 | gate 6 + MANUAL |
| Gate □ 7 — complete inventory (779) | §4, §5.2 | 1.7, `ad_inventory.json` | gate 7 + MANUAL |
| Gate □ 8 — every video transcribed + framework (780) | §4, §5.2 | 1.8, `transcripts/` | gate 8 + MANUAL |
| Gate □ 9 — every text ad decoded (781) | §5.2 | 1.9 | gate 9 + MANUAL |
| Gate □ 10 — cross-ad synthesis (782) | §5.2 | 1.9 | gate 10 + MANUAL |
| Gate □ 11 — congruence for every path (783) | §5.3 | 1.10 | gate 11 + MANUAL |
| Gate □ 12 — 3 validated angle cards (784) | §5.4 | 1.11 | gate 12 |
| Gate □ 13 — 8 hidden angles (785–786) | §6 | 2.1 | gate 13 + MANUAL |
| Gate □ 14 — tailored prompt (787–788) | §7 | 3.6, `CHATGPT_PROMPT.md` | gate 14 + MANUAL |
| Gate □ 15 — integration, validated/killed, language bank (789–790) | §8, §9 | 2.1, 2.5–2.8 | gate 15 + MANUAL |
| Gate □ 16 — full dossier, instant retrieval (791–792) | §10 | `ALPHA_DOSSIER.md` | gate 16 + MANUAL |
| "Only THEN does the launch workflow fire" (794) | §11 step 3 | BRIEF.md gate row | Phase 2 blocked until PASS |
