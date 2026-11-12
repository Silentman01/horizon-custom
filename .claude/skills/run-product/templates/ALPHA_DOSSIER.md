<!--
ALPHA DOSSIER TEMPLATE. Copy to PD/00_alpha/ALPHA_DOSSIER.md and fill it (runbook: references/20-step-alpha-runbook.md α5).
Spec (field meanings, counts, gate): references/19-step-alpha.md. scripts/alpha_gate.py ignores HTML comments like this one.

Markers the gate script counts (keep them exactly):
- Headings: the H1 and every ## / ### heading below, same text, same order. Add nothing at ## or ### level; use #### for sub-groups.
- Field blocks: one fenced ``` block per item, one `KEY:` per line, continuation lines indented. A block's type is its first key:
  AVATAR: (1.1, 2.2) · PAIN POINT: (1.2) · DESIRE: (1.3) · OBJECTION: (1.4) · FEAR-BASED TRIGGERS: (1.5) · MECHANISM: (1.6)
  AD ID: + FRAMEWORK: (1.8 video) · AD ID: + PRIMARY TEXT: (1.9 static) · VALIDATED ANGLES: (1.9 cross-ad patterns)
  AD: (1.10 path map) · HIGH CONGRUENCE ANGLES: (1.10 insights) · ANGLE: + CONFIDENCE: (1.11, 2.8 angle cards)
  AVATAR UNIVERSE: (2.1 explosion inputs) · HIDDEN ANGLE: (2.1) · EMERGENT ANGLE: (2.7)
- IDs: avatars AV1.., ads by inventory short id (M1.. video, S1.. static/carousel/text; Brandsearch id in ad_inventory.json),
  validated cards V1.., opportunity cards O1.., hidden angles H1.., emergent angles E1... Put the ID first in the marker value:
  `AVATAR: AV1 — Night-shift nurse`, `ANGLE: V1 — Morning first-step pain`, `HIDDEN ANGLE: H4 — Hikers before a trip`.
- Two-line spec keys are written on one line here: HOW COMPETITOR HANDLES IT, EMOTIONAL STATE AT CLICK, FIRST SECTION THEY SEE, EVIDENCE IT COULD WORK.
- Fields added for the gate and downstream retrieval (not in the spec blocks): CUSTOMER LANGUAGE on avatars and desires (gate needs
  verbatim language for both), RANK on pains/desires (headings say "ranked"), GAP on objections (heading says "+ gaps"),
  AD ID on video/static blocks, RESEARCH VERDICT/RESEARCH EVIDENCE on hidden angles (2.3 synthesis), BUILT FROM on opportunity cards,
  WHY UNDERSERVED/EVIDENCE on 2.2 avatars, PAGE STRATEGY in the congruence insights.
- A value that is still one whole [bracketed hint], "[...]", "TBD", "TODO" or "{{...}}" counts as empty. Never leave one.
- Quotes: customer language goes in straight or curly double quotes, verbatim, with its source.
- Repeat a block once per item (copy the block). Tables: one row per item.
-->
# [Product] — Step Alpha Intelligence Dossier

Competitor: [brand · product URL(s)] · Market: [country / language] · Ads in inventory: [n] ([n] video, [n] static) · Built: [date]

## PART 1: COMPETITOR MAP

### 1.1 Avatars (full profiles)

```
AVATAR:              [AV1 — descriptive name]
DEMOGRAPHICS:        [age range, gender skew, location
                      signals, income signals — derived from
                      language, imagery, pricing, testimonial
                      profiles]
PSYCHOGRAPHICS:      [values, beliefs, daily routines, media
                      consumption, brands they trust, health
                      attitudes, shopping behavior, decision-
                      making style]
TRIGGER EVENT:       [what specific moment in their life made
                      them START searching for this product?]
AWARENESS STATE:     [Schwartz — Most Aware → Unaware, when they meet the ad]
SOPHISTICATION:      [Schwartz — stage of this market for this avatar;
                      how many claims have they already heard?]
CUSTOMER LANGUAGE:   ["verbatim phrase" — source]
```

```
AVATAR:              [AV2 — descriptive name]
DEMOGRAPHICS:        [age range, gender skew, location signals, income signals]
PSYCHOGRAPHICS:      [values, beliefs, daily routines, media consumption, brands they trust,
                      health attitudes, shopping behavior, decision-making style]
TRIGGER EVENT:       [the moment they START searching]
AWARENESS STATE:     [Schwartz awareness]
SOPHISTICATION:      [Schwartz sophistication stage]
CUSTOMER LANGUAGE:   ["verbatim phrase" — source]
```

### 1.2 Pain Points (ranked, with customer language)

<!-- One block per pain point, rank 1 = core pain (highest FREQUENCY × EMOTIONAL WEIGHT). Minimum 10. -->

```
PAIN POINT:          [the felt experience, not the clinical
                      description]
RANK:                [1]
SOURCE:              [which ad (ID), which page section, which testimonial]
FREQUENCY:           [n times across all surfaces — core / secondary]
EMOTIONAL WEIGHT:    [HEADLINE pain or supporting mention — how hard it is amplified]
AVATAR:              [AV id(s) who feel it most]
CUSTOMER LANGUAGE:   ["exact words" — source]
```

### 1.3 Desires & Dream Outcomes (ranked, with language)

<!-- One block per desire, ranked. Minimum 5. -->

```
DESIRE:              [the felt outcome, not the feature]
RANK:                [1]
TYPE:                [functional / emotional / identity /
                      social / aspirational]
DREAM OUTCOME:       [what life looks like 6 months after buying —
                      identity-level, not feature-level]
SOURCE:              [where this desire appears]
AVATAR:              [AV id(s) who want this most]
CUSTOMER LANGUAGE:   ["exact words" — source]
```

### 1.4 Objections (with competitor handling + gaps)

<!-- One block per objection. Minimum 5. -->

```
OBJECTION:           [the doubt, in the customer's words]
TYPE:                [price / efficacy / trust / safety /
                      effort / social judgment / alternatives /
                      "is this real" / shipping / returns]
HOW COMPETITOR HANDLES IT: [where and how — FAQ answer? guarantee?
                      testimonial? comparison? mechanism proof?]
WHERE IN FUNNEL:     [ad / landing page / product page hero /
                      product page body / FAQ / checkout]
STRENGTH:            [1-5 — how well their handling resolves it]
GAP:                 [what their handling leaves open — our opening]
```

### 1.5 Emotional Landscape (triggers by type)

```
FEAR-BASED TRIGGERS:   [what fears do they activate?]
DESIRE-BASED TRIGGERS: [what desires do they pull?]
IDENTITY TRIGGERS:     [what identity does buying this claim?]
FRUSTRATION TRIGGERS:  [what past failures do they reference?]
CURIOSITY TRIGGERS:    [what knowledge gaps do they create?]
DISGUST TRIGGERS:      [what do they make the customer reject?]
```

### 1.6 Unique Mechanism (UMS/UMP analysis)

```
MECHANISM:           [how does the competitor explain WHY
                      their product works? process, technology,
                      ingredient, design feature or principle]
MECHANISM NAME:      [branded name, or "unbranded"]
MECHANISM STORY:     [who discovered it, how old is the science,
                      what conventional wisdom gets wrong, why
                      mainstream doesn't know about it]
MECHANISM PROOF:     [studies, expert endorsements, visual
                      demonstrations, specifics]
SCHWARTZ TECHNIQUE:  [Mechanization / Concentration /
                      Redefinition / Identification — and how]
```

### 1.7 Ad Inventory (complete table)

<!-- One row per record in PD/00_alpha/ad_inventory.json "ads" (every ad, active and inactive, every platform). Row count must equal the record count. -->

| AD ID | FORMAT | PLATFORM | STATUS | RUN TIME | ANGLE | AVATAR |
|---|---|---|---|---|---|---|
| [M1] | [video] | [Meta] | [active] | [21 days] | [V1 pain] | [AV1] |

### 1.8 Video Frameworks (beat maps, formats, patterns)

<!-- One block per video ad in the inventory. Inputs: transcripts/<ad_id>.txt (frameworks come from the transcript; no Gemini). Timed lines / VO/TEXT SPLIT / PACING / HOOK DURATION: `alpha_gate.py beats transcripts/<ad_id>.txt [--duration <ffprobe s>]` prints them. -->

```
AD ID:              [M1]
FRAMEWORK:          [structural skeleton — Hook→Problem→
                     Solution→Proof→CTA / Hook→Demo→
                     Benefits→Urgency / Hook→Story→Reveal→
                     Offer / etc. — or a new framework]
BEAT MAP:           [each beat with timestamp, duration,
                     % of total, function]
FORMAT:             [UGC / advertorial / talking head /
                     product demo / animation / text overlay /
                     mixed / interview / before-after /
                     lifestyle montage / problem dramatization /
                     expert explanation / customer story /
                     comparison demo / unboxing / day-in-life /
                     POV / reaction / transformation reveal]
HOOK:               [exact words, type, open loop mechanism]
HOOK DURATION:      [seconds]
ANGLE:              [which marketing angle]
AVATAR:             [AV id]
EMOTIONAL ARC:      [beat-by-beat emotional journey]
RETENTION MECHANICS:[open loops, pattern interrupts,
                      escalation, new info drips, cliffhangers]
VO/TEXT SPLIT:      [% voiceover vs % on-screen text vs
                      % music-only]
PACING:             [WPS average + per-beat variation]
MUSIC/SFX:          [genre, energy curve, key moments]
CTA:                [exact text, timestamp, urgency mechanism]
```

#### Video framework patterns

| FRAMEWORK | ADS | FORMATS | LONGEST RUN |
|---|---|---|---|
| [Hook→Problem→Solution→Proof→CTA] | [M1, M4] | [UGC] | [21 days] |

### 1.9 Ad Copy Patterns (hooks, sequences, CTAs)

<!-- One block per non-video ad (static, carousel, text) in the inventory, then ONE cross-ad pattern block over all ads. -->

```
AD ID:              [S1]
PRIMARY TEXT:       [exact]
HEADLINE:           [exact]
DESCRIPTION:        [exact, or "none in ad"]
HOOK:               [first line, type, open loop]
ANGLE:              [which angle]
AVATAR:             [AV id]
EMOTIONAL TRIGGER:  [fear / desire / identity / curiosity /
                     frustration / disgust / aspiration]
PERSUASION SEQUENCE:[PAS / AIDA / HSO / testimonial-proof-
                      CTA / other]
PROOF TYPE:         [stat / testimonial / authority /
                      mechanism / before-after / social count /
                      specificity]
CTA:                [exact text + urgency mechanism]
IMAGE FORMAT:       [product shot / lifestyle / before-after /
                      infographic / UGC screenshot / review
                      screenshot / text-heavy / comparison /
                      ingredient visual / meme-style / data
                      visualization / testimonial card]
```

#### Cross-ad pattern mining (all ads)

```
VALIDATED ANGLES:   [angles with longest-running ads —
                      these are PROVEN with money]
TESTING ANGLES:     [newer ads, shorter run time —
                      competitor is exploring these]
DOMINANT HOOK TYPES:[which hooks appear most across winners]
DOMINANT FORMATS:   [UGC vs demo vs VSL vs advertorial —
                      what ratio?]
DOMINANT FRAMEWORKS:[video script structures that repeat]
COMMON PROOF:       [proof types that appear in most ads]
COMMON CTA:         [CTA patterns, urgency types]
CREATIVE VELOCITY:  [how many new ads per week? how fast
                      do they iterate?]
AD VOLUME:          [total ads, active ads, trajectory]
SATURATION:         [how many distinct advertisers/pages
                      run this product?]
```

### 1.10 Funnel Congruence (ad→page path scores)

#### Map every ad → page path

<!-- One block per ad. Only exact duplicates (same creative and copy) may share one block: list their IDs in AD. -->

```
AD:                 [M1]
ANGLE:              [name]
PROMISE:            [what the ad promises]
AVATAR:             [AV id]
EMOTIONAL STATE AT CLICK: [curious? hopeful? urgent? skeptical? excited?]
                     ↓
LANDING:            [destination URL / product page]
                     ↓
FIRST SECTION THEY SEE: [what the page shows above the fold]
CONGRUENCE:         [HIGH/MED/LOW — does the page's opening MATCH the
                     ad's promise? is the emotional state VALIDATED
                     or DISRUPTED?]
```

#### Score each path

| AD → PAGE PATH | CONGRUENCE | NOTES |
|---|---|---|
| [M1 (pain angle) → /products/x] | [HIGH/MED/LOW] | [why] |

#### Congruence insights

```
HIGH CONGRUENCE ANGLES:   [safest angles to copy — ad AND page aligned]
LOW CONGRUENCE ANGLES:    [the ad works but the page doesn't follow
                           through — traffic the competitor is leaking]
LANDING PAGES:            [different landing pages per angle, or one
                           page for all? (one = guaranteed gaps)]
CONGRUENT PAGE PER ANGLE: [what a congruent page looks like for each angle]
PAGE STRATEGY:            [our decision: one page with multi-angle
                           architecture, or angle-specific landing pages — and why]
```

### 1.11 Validated Angle Cards

<!-- One card per angle the competitor runs. Minimum 3 with CONFIDENCE HIGH or MEDIUM. IDs V1... -->

```
ANGLE:            [V1 — descriptive name]
CONFIDENCE:       [HIGH/MEDIUM (based on ad run time/volume)]
AVATAR:           [AV id — who]
PAIN/DESIRE:      [the core emotional driver]
EMOTIONAL TRIGGER:[fear / desire / identity / etc.]
ENEMY:            [positioned against what?]
MECHANISM:        [how/why product solves it]
PROMISE:          [specific outcome]
PROOF:            [evidence type used]
FUNNEL CONGRUENCE:[HIGH/MED/LOW with page]
ADS USING THIS:   [M1, S3, ...]
HOOK TEMPLATES:   ["...", "..."]
CUSTOMER LANGUAGE:["exact phrases from this angle"]
OPPORTUNITY:      [what can WE do better on this angle?]
```

## PART 2: OPPORTUNITY MAP

### 2.1 Hidden Angles (validated by research)

#### Explosion inputs

```
AVATAR UNIVERSE:      [every possible avatar — age groups, genders, activity levels,
                       professions, life stages, health conditions, motivations]
PHYSICAL PAINS:       [...]
EMOTIONAL PAINS:      [...]
SOCIAL PAINS:         [...]
IDENTITY PAINS:       [...]
CONVENIENCE PAINS:    [...]
FINANCIAL PAINS:      [...]
DESIRE UNIVERSE:      [performance, comfort, confidence, appearance, longevity,
                       freedom, independence, social approval, identity,
                       prevention, optimization — product-specific]
COMBINATIONS CROSSED: [n avatar × pain × desire × emotion combinations]
SURVIVORS:            [n hidden angles kept]
DISCARDED:            [n — main reasons]
```

#### Emotional entries (all 13)

| # | EMOTIONAL ENTRY | SPEC PROMPT | HIDDEN ANGLES (H ids) |
|---|---|---|---|
| 1 | Fear | what could go wrong without this | [H…, or "none survived — why"] |
| 2 | Desire | what life looks like with this | [H…] |
| 3 | Identity | what kind of person uses this | [H…] |
| 4 | Curiosity | what you don't know about [topic] | [H…] |
| 5 | Frustration | why everything else failed | [H…] |
| 6 | Contrarian | what the industry gets wrong | [H…] |
| 7 | Disgust | what's actually in your current [X] | [H…] |
| 8 | Authority | what experts say about [X] | [H…] |
| 9 | Social proof | why [X] people switched | [H…] |
| 10 | Mechanism | the science behind why this works | [H…] |
| 11 | Comparison | this vs every alternative | [H…] |
| 12 | Seasonal | why [time of year] makes this urgent | [H…] |
| 13 | Life-event | triggered by a specific moment | [H…] |

#### Hidden angles (minimum 8; validated first, then killed)

```
HIDDEN ANGLE:       [H1 — name]
AVATAR:             [who (AV id if profiled)]
PAIN/DESIRE:        [core driver]
EMOTIONAL ENTRY:    [type — one of the 13]
ESTIMATED POTENTIAL: [HIGH / MEDIUM / LOW — based on:
                      how large is this audience segment?
                      how intense is their pain/desire?
                      how underserved are they by existing
                      ads in the market?]
COMPETITOR USING IT: [NO — that's why it's hidden]
EVIDENCE IT COULD WORK: [search volume? Reddit discussions?
                      adjacent product success? logical
                      deduction from avatar profile?]
RESEARCH VERDICT:   [VALIDATED / KILLED — from the ChatGPT data]
RESEARCH EVIDENCE:  ["verbatim quote" — source, or "no data found"]
```

### 2.2 Underserved Avatars

<!-- Avatars from the explosion the competitor does not target. Same fields as 1.1, IDs continue (AV3...). -->

```
AVATAR:              [AV3 — descriptive name]
DEMOGRAPHICS:        [...]
PSYCHOGRAPHICS:      [...]
TRIGGER EVENT:       [...]
AWARENESS STATE:     [...]
SOPHISTICATION:      [...]
CUSTOMER LANGUAGE:   ["verbatim phrase" — source (ChatGPT raw data)]
WHY UNDERSERVED:     [no competitor ad, angle or page section speaks to them]
EVIDENCE:            [raw-data rows that show they exist and care]
```

### 2.3 Emotional Territories Untapped

| TERRITORY (EMOTIONAL ENTRY) | COMPETITOR USES IT? | OUR ANGLES (H/E ids) | EVIDENCE (RAW DATA) |
|---|---|---|---|
| [Contrarian] | [no] | [H2] | ["verbatim" — source] |

### 2.4 Funnel Congruence Gaps (angles the competitor leaks traffic on — our opportunity)

<!-- Every LOW / MED path from 1.10. If every path is HIGH, replace the table with one line starting "NO GAPS:" and the reason. -->

| ANGLE | ADS | CONGRUENCE | WHAT THE PAGE DROPS | OUR CONGRUENT PAGE |
|---|---|---|---|---|
| [V2 sport] | [S4, M2] | [LOW] | [hero talks pain, ad promised performance] | [above-the-fold block for this angle] |

### 2.5 ChatGPT Raw Data (full market research output)

<!-- Paste PD/00_alpha/chatgpt/CHATGPT_RAW.md here verbatim inside the 5-backtick fence (keeps its headings out of the dossier structure). -->

`````text
[paste CHATGPT_RAW.md verbatim]
`````

### 2.6 Language Bank (hook-ready, headline-ready, objection-ready phrases)

<!-- Most powerful verbatim quotes from the raw data (2.3 synthesis). Minimum 5 rows per group. -->

#### Hook-ready

| # | PHRASE (VERBATIM) | SOURCE | PLATFORM |
|---|---|---|---|
| 1 | ["..."] | [r/sub or URL] | [Reddit] |

#### Headline-ready

| # | PHRASE (VERBATIM) | SOURCE | PLATFORM |
|---|---|---|---|
| 1 | ["..."] | [source] | [platform] |

#### Objection-ready

| # | PHRASE (VERBATIM) | SOURCE | PLATFORM |
|---|---|---|---|
| 1 | ["..."] | [source] | [platform] |

#### Testimony-ready

| # | PHRASE (VERBATIM) | SOURCE | PLATFORM |
|---|---|---|---|
| 1 | ["..."] | [source] | [platform] |

### 2.7 Emergent Angles (from raw data)

<!-- Angles not in 2.1 that emerged from the raw data. If truly none, replace the block with one line starting "NONE FOUND:" and why. -->

```
EMERGENT ANGLE:     [E1 — name]
AVATAR:             [who]
PAIN/DESIRE:        [core driver]
EMOTIONAL ENTRY:    [type]
ESTIMATED POTENTIAL:[HIGH / MEDIUM / LOW]
EVIDENCE:           ["verbatim quote" — source, frequency in the raw data]
```

### 2.8 Opportunity Angle Cards

<!-- One card per validated hidden angle, emergent angle and congruence gap worth building. IDs O1... BUILT FROM names the H/E ids or the 2.4 gap. -->

```
ANGLE:            [O1 — descriptive name]
CONFIDENCE:       [HIGH/MEDIUM (based on research evidence strength)]
BUILT FROM:       [H3 / E1 / 2.4 gap on V2]
AVATAR:           [AV id — who]
PAIN/DESIRE:      [the core emotional driver]
EMOTIONAL TRIGGER:[fear / desire / identity / etc.]
ENEMY:            [positioned against what?]
MECHANISM:        [how/why product solves it]
PROMISE:          [specific outcome]
PROOF:            [evidence type we will use]
FUNNEL CONGRUENCE:[the page section that will validate it above the fold]
ADS USING THIS:   [none — competitor does not run it]
HOOK TEMPLATES:   ["...", "..."]
CUSTOMER LANGUAGE:["exact phrases from the raw data"]
OPPORTUNITY:      [why we win here]
```

## PART 3: QUICK-REFERENCE

### 3.1 Angle Cards (validated + opportunity, combined)

| ID | ANGLE | TYPE | CONFIDENCE | AVATAR | EMOTIONAL TRIGGER | PROMISE | CONGRUENCE | LEAD HOOK |
|---|---|---|---|---|---|---|---|---|
| [V1] | [name] | [validated] | [HIGH] | [AV1] | [fear] | [outcome] | [HIGH] | ["..."] |

### 3.2 Avatar Cards

| ID | AVATAR | SOURCE | DEMOGRAPHICS | TRIGGER EVENT | AWARENESS | SOPHISTICATION | TOP PAINS | KEY PHRASE |
|---|---|---|---|---|---|---|---|---|
| [AV1] | [name] | [competitor / underserved] | [...] | [...] | [...] | [...] | [...] | ["..."] |

### 3.3 Hook Library (every hook from every ad + templates)

| # | HOOK (VERBATIM) | TYPE | AD ID | ANGLE | TEMPLATE |
|---|---|---|---|---|---|
| 1 | ["..."] | [pain] | [M1] | [V1] | ["If you ___, ..."] |

### 3.4 Framework Library (every video framework + beat maps)

| FRAMEWORK | BEAT MAP (BEAT · % OF TOTAL) | ADS | FORMATS | LONGEST RUN |
|---|---|---|---|---|
| [Hook→Problem→Solution→Proof→CTA] | [Hook 8% · Problem 22% · ...] | [M1, M4] | [UGC] | [21 days] |

### 3.5 Customer Language Bank (organized by use: hooks, headlines, objection handling, social proof)

#### Hooks

| # | PHRASE (VERBATIM) | SOURCE | ANGLE |
|---|---|---|---|
| 1 | ["..."] | [source] | [V1] |

#### Headlines

| # | PHRASE (VERBATIM) | SOURCE | ANGLE |
|---|---|---|---|
| 1 | ["..."] | [source] | [V1] |

#### Objection handling

| # | PHRASE (VERBATIM) | SOURCE | OBJECTION |
|---|---|---|---|
| 1 | ["..."] | [source] | [price] |

#### Social proof

| # | PHRASE (VERBATIM) | SOURCE | ANGLE |
|---|---|---|---|
| 1 | ["..."] | [source] | [V1] |

### 3.6 ChatGPT Prompt (ready to paste for this product)

<!-- Paste PD/00_alpha/chatgpt/CHATGPT_PROMPT.md here verbatim inside the 5-backtick fence. -->

`````text
[paste CHATGPT_PROMPT.md verbatim]
`````
