# 22 — Native Ads and Advertorial Landing Pages

Some competitors run a funnel that goes **native ad → advertorial/pre-sell page → product page** instead of sending ads straight to the product page. When this funnel exists, we capture it, analyze it, and build our own adapted version — same conversion psychology, different execution. Step Alpha data drives every piece.

This reference is a **living document**: definitions and examples grow with every product run. When we encounter new native ad formats or advertorial structures, update the lists and guidance here.

Read first: `00-operator-rules.md` §2 (adapted framework), `03-competitor-page-analysis.md` §7b (adaptation blueprint).

## Contents
1. When this applies (detection)
2. What native ads are
3. What advertorial / pre-sell landing pages are
4. The extended funnel and congruency
5. Phase 1 — Capture (1.5)
6. Step Alpha — Analyze the funnel (extends α1.3)
7. Phase 3 — Build our own advertorial pages (A5)
8. Phase 3 — Native ads in the creative mix (extends D2)
9. Ad copy for the advertorial funnel (extends E)
10. QA and done-when
11. Pitfalls

---

## 1. When this applies (detection)

Not every competitor uses this funnel. Check during Phase 1:
1. Look at `landing_url` in the ad inventory — if ads point to URLs that are NOT the product page, they're likely advertorial or pre-sell pages.
2. Check the top-ranked ads: if the best-performing ads redirect to editorial/article-style pages instead of the product page, this is a native ad → advertorial funnel.
3. If ALL ads go directly to the product page, skip this reference (streams 1.5 and A5 don't apply; native ad formats still count inside D2 if the competitor uses them).

Record the finding in BRIEF.md: `Advertorial funnel: yes/no | <count> unique advertorial URLs | <count> ads pointing to advertorials`.

## 2. What native ads are

Native ads are image (or video) ads designed to look like organic content on the platform — not like a product ad. They bypass the "this is an ad" filter because they look like something a user would scroll past in their feed as real content.

**Known native ad formats** (update this list with every product run):
- Reddit/forum post screenshots — looks like a real Reddit post with title, upvotes, comments
- Handwritten notes or to-do lists — personal, lo-fi, handwriting on paper
- Article thumbnails with editorial headlines — looks like a news or blog link
- Text message / chat screenshots — conversation about the product
- Newspaper or magazine article layouts — editorial column, publication name, author
- Comparison charts that look like editorial content — not branded, looks researched
- "Things I wish I knew" or numbered lists — personal advice format
- Diary/journal entries — personal discovery story
- Product review screenshots — looks like a review site, not the brand's ad
- Social media post screenshots — Twitter/X, Instagram, TikTok comments
- Whiteboard or planning board — brainstorm or pros/cons
- Letter or note format — personal recommendation

**What makes them work:** they look real. The platform user sees what looks like organic content, engages with it, and only realizes it's an ad after they're already hooked by the message.

**How we remake them:** same adaptation principle as everything else — understand the format mechanism (what makes it look native, what hooks the reader, what drives the click), then build our own version with different content, different visual style, and our angle/avatar/language from Step Alpha. Never 1:1.

## 3. What advertorial / pre-sell landing pages are

Advertorial pages (also called pre-sell pages, advertorial landing pages, or editorial landers) are web pages that sit between the ad and the product page. They look like articles, reviews, or editorial content — not like a sales page. Their job: warm up cold traffic so the customer arrives at the product page already pre-sold.

**Known advertorial formats** (update this list with every product run):
- "I tried [X] and here's what happened" — personal review article
- "The science behind [problem]" — educational/explainer article
- "[N] things that actually work for [problem]" — listicle/roundup
- "[Expert/publication] reveals [solution]" — authority endorsement article
- "Warning: [problem] is worse than you think" — problem amplification article
- Quiz or assessment pages — interactive, ends with product recommendation
- "[Year] buyer's guide to [category]" — comparison article recommending the product
- "Breaking: new [technology/ingredient/method]" — news-style article about the product's mechanism

**Common advertorial structure** (the beats — similar to ad copy framework extraction):

| Beat | Job | Example |
|---|---|---|
| 1. Editorial headline | Stop the scroll with problem/curiosity, looks like a real article | "Why Most [Category] Products Don't Actually Work (And What Science Says Does)" |
| 2. Author / publication byline | Establish editorial credibility and trust | "By [Name], [Title] · [Publication] · [Date]" |
| 3. Problem story | The reader sees themselves; build problem awareness | Personal anecdote or relatable scenario |
| 4. Failed attempts | What they've tried (validates their frustration) | "Like most people, I tried X, Y, Z..." |
| 5. Discovery | Introduce the product as an editorial finding, not a sales pitch | "That's when I came across..." |
| 6. Mechanism | Why this works when others don't (the product's unique mechanism) | Scientific explanation, expert quotes |
| 7. Social proof | Testimonials, before/after, numbers — editorial tone | Customer stories, data points |
| 8. CTA to product page | Soft-sell link, availability check, "learn more" | "Check if [product] is available →" |

**Fake publication names:** advertorials often use a made-up publication or blog name (not the brand, not a real outlet). Ours does the same — invent a plausible editorial name, never use our brand name as the publication and never use a real publication's name.

## 4. The extended funnel and congruency

When the competitor uses advertorial funnels, the customer journey is:

```
NATIVE AD  ──→  ADVERTORIAL PAGE  ──→  PRODUCT PAGE
(looks like     (looks like an         (the conversion
 organic         article, warms         page with the
 content)        up the customer)       offer)
```

Each hop must maintain:
- **Promise congruency:** the ad's hook → the advertorial's story → the product page's offer all speak the same language about the same promise
- **Emotional continuity:** the feeling the ad creates → the advertorial amplifies → the product page converts. No jarring tone shifts.
- **Avatar targeting:** every step addresses the same person (Step Alpha avatar from the angle card)
- **Angle consistency:** one angle card governs the entire path: ad angle → advertorial angle → product page section emphasis

**Step Alpha data in the advertorial:**
| Dossier section | Use in the advertorial |
|---|---|
| 3.1 Angle cards | each advertorial serves one angle card (its avatar, pain, desire, trigger, mechanism, promise) |
| 3.5 Language bank | the advertorial speaks in the customer's own words (hook-ready, headline-ready, objection-ready) |
| 1.1 Avatars (awareness, sophistication) | the advertorial's entry point matches the avatar's awareness stage (Schwartz) |
| 1.4 Objections | the advertorial pre-handles the top objections before the customer reaches the product page |
| 1.6 Mechanism | the advertorial explains the mechanism in an editorial frame — this is the "discovery" beat |
| 3.3 Hook library | the advertorial headline uses a hook from the library |
| 1.5 Emotional landscape | the advertorial's emotional arc matches the target avatar's triggers |

## 5. Phase 1 — Capture advertorial pages (1.5)

**When:** during Phase 1, after the ad footprint is pulled (1.3) and `ad_inventory.json` exists.
**Trigger:** any `landing_url` in the ad inventory that is NOT the product page URL.

**Do:**
1. From `ad_inventory.json`, collect every unique `landing_url` that differs from `COMPETITOR_URL`.
2. For each unique advertorial URL:
   - `python -I <SKILL>/scripts/capture_page.py "<URL>" --out "<PD>/02_competitor/advertorials/<slug>/"`
   - `python -I <SKILL>/scripts/screenshot.py "<URL>" --out "<PD>/02_competitor/advertorials/<slug>/" --name adv`
   - Note how many ads point to it and their total days running (from the inventory).
3. Save a summary: `<PD>/02_competitor/advertorials/ADVERTORIAL_INVENTORY.md` — table of URL, slug, ads pointing to it, total days, headline (from capture), what angle it serves.

**Output:** `PD/02_competitor/advertorials/<slug>/` per unique advertorial page, plus the inventory summary.

**Skip if:** every ad in the inventory points to the product page (no advertorial funnel detected).

## 6. Step Alpha — Analyze the funnel (extends α1.3)

The congruence analysis (1.3) now covers the full path when advertorials exist.

**For each advertorial page, extract:**
- Headline and hook (what stops the reader)
- Angle served (which angle card from 1.4)
- Avatar targeted (which ICP)
- Mechanism presentation (how the product is introduced)
- Proof structure (what social proof, authority, data)
- CTA and destination (where it sends traffic)
- Tone (editorial voice, first-person vs third-person, publication feel)
- Beats (the framework structure — same approach as video framework extraction from transcripts)

**Extended congruence mapping:**
```
AD → ADVERTORIAL → PRODUCT PAGE
 ↓        ↓              ↓
CONGRUENCE  CONGRUENCE   (destination)
SCORE #1    SCORE #2

Score #1: does the advertorial's opening match the ad's promise?
Score #2: does the product page's hero match the advertorial's CTA promise?
```

Add to the congruence table: `AD | ANGLE | ADVERTORIAL | AD→ADV CONGRUENCE | ADV→PAGE CONGRUENCE | NOTES`.

**Congruence insights (extend):**
- Which advertorial angles have the highest overall congruence (ad→adv→page)?
- Where does the funnel leak? (high ad→adv but low adv→page = the advertorial over-promises)
- Are different advertorials used for different angles? (angle-specific advertorials = higher congruence)
- What does the advertorial do that the product page doesn't? (the "warm-up" job — we should replicate it)

## 7. Phase 3 — Build our own advertorial pages (A5)

**When:** the competitor uses advertorial funnels (detected in 1.5, analyzed in α1.3).
**Who:** advertorial builder agent (**Opus 4.6** — same mandate as page/copy agents; the advertorial is conversion copy).
**Depends on:** A1 (section spec + adaptation blueprint, for product page angle assignments) and the dossier.

**Step 1 — Advertorial framework map**
Study the competitor's advertorial structure:
- What beats does it follow? (§3 structure table)
- What editorial conventions does it use? (publication name, byline, date, images)
- How long is it? (word count, scroll depth)
- What's the reading level and tone?
- What claims does it make? (claims bank — same strength as always)
- What CTA format? (button style, link text, urgency)

**Step 2 — Advertorial adaptation blueprint**
Design our version — the test: an AI comparing both advertorial pages sees two completely different articles.
- Different editorial style (if theirs is a "review article", ours might be a "science report" or "buyer's guide")
- Different story structure (reorder beats where it serves conversion better)
- Different visual identity (consistent with our product page's adaptation blueprint)
- Different publication name and author persona
- Same conversion psychology: problem → mechanism → proof → CTA
- Same claims at full strength

**Step 3 — Write the advertorial**
One advertorial per major angle card that the competitor serves with an advertorial. Write from:
- Step Alpha dossier (language bank 3.5, pains 1.2, desires 1.3, avatar language, emotional landscape 1.5)
- Books-playbooks (through the copy chief on Opus 4.6)
- The adaptation blueprint (our editorial style, not the competitor's)
- Fully original — no text word-for-word from the competitor's advertorial

**Step 4 — Build it**
Build as a Shopify page template: `templates/page.<slug>-advertorial-<angle-id>.json` or as a custom Liquid page, depending on the store setup. The advertorial must:
- Render complete with zero admin setup (same rule as home page, 11 §4)
- Look editorial, not like a Shopify product page
- Have a clear CTA that links to the product page (or the angle-specific landing page if one exists)
- Be responsive (mobile-first, same as product page)
- Be SEO-invisible if needed (noindex, no sitemap) — advertorials are ad destinations, not organic content

**Step 5 — Per-angle advertorials**
When the competitor has multiple advertorials for different angles, build one adapted advertorial per angle card. Each advertorial:
- Maps to one angle card ID (V# or O#)
- Targets that card's avatar in that avatar's language
- Pre-handles that card's top objections
- Leads to the product page (or angle landing page) with its angle emphasized above the fold

**Output:** `PD/09_advertorials/` — one directory per advertorial, containing the page template, the copy, and the framework analysis. The product page's `AD_COPY.md` and `AD_VARIANTS.md` reference the advertorial URL per angle card.

## 8. Phase 3 — Native ads in the creative mix (extends D2)

When the competitor's top-performing ads include native formats, they get specific treatment in the ad creatives workflow (08).

**In the selection matrix (08 §5):** native ad formats are a row in the matrix alongside comparison, poster, lifestyle, etc. If the competitor runs ≥ 2 native ads in the top 30, at least one native format appears in the top 5 remakes and at least 2 in the pattern ads.

**Native ad remake guidance:**
- The adaptation principle applies doubly: native ads work because they look organic, so our version must also look organic — but different organic. A Reddit-style ad becomes a different Reddit-style ad (different subreddit name, different post title, different comments), not a carbon copy.
- The hook mechanism is what matters: "social proof through community discussion" is the mechanism, "r/HomePestControl" is the execution.
- Native ad text follows the same rules: from the language bank (3.5), through the copy chief, fully original.
- Pack shot placement in native ads is subtle (often the product appears in a photo within the "post" or in a "comment image"), not a hero placement.

**Native ad specs (in ad builder files):** when writing the spec for a native ad, include:
- The platform it imitates (Reddit, Twitter, article thumbnail, note, etc.)
- The UI chrome it uses (upvote buttons, comment counts, timestamps, usernames — all fake, never real Reddit/Twitter UI trademarks)
- The "organic content" that makes it look real (post title, comment text, article headline)
- Where the product appears and how subtle it is
- The hook and angle (from the angle card and hook library)

## 9. Ad copy for the advertorial funnel (extends E)

When advertorial pages exist, the ad copy in `AD_COPY.md` (09) needs an additional field per angle card:

```
Landing: <advertorial URL or advertorial template name> (not the product page)
```

The primary text and headlines are written to drive traffic to the advertorial (not the product page), so the CTA and promise should match the advertorial's opening — not the product page's offer.

For angle cards that DON'T use advertorials (direct to product page), the copy stays as before.

## 10. QA and done-when

**Advertorial QA (within Phase 4):**
- [ ] Every advertorial renders complete at desktop and mobile with zero admin setup
- [ ] Copy is fully original (originality check against competitor's advertorial text)
- [ ] Claims at full strength (no softening in editorial tone)
- [ ] CTA links to the correct product page (or angle landing page)
- [ ] The advertorial looks editorial, not like a product page
- [ ] Congruency check: read the ad → advertorial → product page path for each angle — does the story flow?
- [ ] Fake publication name is not our brand, not the competitor's brand, not a real publication
- [ ] No competitor brand name anywhere

**Native ad QA (within D2 contact sheet review):**
- [ ] Looks like organic content (not like a traditional ad)
- [ ] No real platform trademarks (fake Reddit UI, fake usernames, etc.)
- [ ] Product placement is subtle and correct (matches the format)
- [ ] Copy is original and from the language bank
- [ ] If the competitor's native ad links to an advertorial, ours does too

**Done when:**
- Every advertorial page is built, QA'd, and the ad → advertorial → product page path is congruent for each angle card
- Native ads are in the creative mix (at least 2 when the competitor runs ≥ 2 native formats in the top 30)
- `AD_VARIANTS.md` shows which ads link to advertorials and which go direct to the product page
- `DELIVERY.md` lists each advertorial with its angle card, URL, and the ads that point to it

## 11. Pitfalls

- **Advertorial reads like a sales page.** The whole point is editorial tone. If it sounds like the product page, it's not an advertorial. Use books-playbooks (Halbert's "personal letter" and Hopkins's "editorial advertising") to maintain an editorial voice while being persuasive.
- **Native ad looks too polished.** Native ads work because they're lo-fi. Over-designing them defeats the purpose. Keep the design rough where the format demands it.
- **Funnel breaks at the hop.** The advertorial promises one thing, the product page opens with something else. Check congruency by reading the path as a customer would.
- **Copy is 1:1 from the competitor's advertorial.** Same adaptation rules apply: study the framework, write your own version from the dossier data.
- **Fake publication uses a real outlet's name.** Invent a plausible name. Never impersonate a real publication.
- **Advertorial is indexed by search engines.** Add noindex meta tag — advertorials are ad destinations, not organic content.
- **Skipping the advertorial funnel when it exists.** If the competitor's best ads use advertorials, our ads should too. Sending native ads straight to the product page breaks congruency.
