# Phase 3E — Ad copy (framework extraction + one copy set per angle card)

Goal: Meta ad copy for our brand that mirrors the competitor's proven caption structure beat for beat, with claims at the same strength, in the market's language, written **once per Step Alpha angle card**: per card, primary text Version A (1:1 structure), Version B (short), 5 headlines with top picks, link description; one CTA rotation for all. Output: `05_ads/AD_COPY.md` from `templates/AD_COPY.md`.

**One shared file:** `05_ads/AD_COPY.md` sits at the root of `05_ads/` and is the only copy file for the brand. It holds one copy set per angle card; every ad, image and video alike, uses the copy set of its angle card (AD_VARIANTS.md column, 08 §1b), until the operator says otherwise. Never put copy files inside `generated/`, batch or video folders, and new batches (images or videos) reuse it instead of writing new primary texts or headlines.

Read first: `00-operator-rules.md` §1 (claims — no softening, no caveat notes), §11 (copy style).
Starts after Alpha: the Step Alpha gate has passed (`00_alpha/ALPHA_DOSSIER.md`) and `05_ads/competitor/ranking.json` (captions) exists. Sub-agents return the document as text; the master saves it. All persuasive copy goes through the copy chief (13).

**Inputs from Step Alpha:**
| Dossier section | Use |
|---|---|
| 3.1 Angle Cards (validated `V#` + opportunity `O#`) | one copy set per card: its avatar, pain/desire, trigger, enemy, mechanism, promise, proof |
| 1.9 Ad Copy Patterns · 1.7 Ad Inventory | the caption groups, persuasion sequences and CTAs, and which caption runs on which angle |
| 3.3 Hook Library | the hook line of each copy set and the headlines |
| 3.5 Customer Language Bank (+ 2.6) | hook-ready and headline-ready phrases for hooks and headlines; objection-ready phrases for the feature stack and risk reversal |
| 1.4 Objections | the objections each set's feature stack answers |
| 1.1 Avatars (awareness, sophistication) | how fast each set names the product and what kind of claim leads (13) |

---

## Step 1 — Collect the captions
**Purpose:** find the copy the competitor actually pays to run.
**Do:**
1. Pull from `ranking.json`, the raw Brandsearch dumps (`05_ads/competitor/raw/`) and the dossier (1.9 Ad Copy Patterns, 1.7 Ad Inventory) for every ad of the product: primary text (body/caption), headline (title), link description, CTA type, days running, angle card. Field names: see `tools-brandsearch.md`.
2. Normalise whitespace and group identical captions. Count ads and total days running per caption group.
3. Pick the **primary caption** = the group used by the best-ranked creatives (best `reach_rank`; ties by total days running, then ad count). Competitors often lock one caption on every ad and test only creatives — then there is exactly one group.
4. Note headline variants and the CTA types used and how often.
**Output:** caption groups table (`caption # | ads | total days | first line | angle cards it runs on`).
**Done when:** the primary caption, headlines and CTAs are identified.
**Pitfalls:** captions from the brand's other products (filter by the product keyword as in 07); truncated captions in one endpoint — take the longest version.

> **Noxis run:** one caption on all 67 Plaims headlight-glasses image ads; headline "Headlight Glasses That Actually Work"; CTAs rotated Shop now / See details / Learn more.

## Step 2 — Extract the framework (beats table)
**Purpose:** copy the persuasion architecture, not the words.
**Do:** split the primary caption into beats; for each give the competitor line (verbatim or close paraphrase) and its job. The common solution-aware structure:

| Beat | What to look for | Job |
|---|---|---|
| 1. Hook | question or callout to people who tried alternatives | stop the scroll, qualify the reader (awareness level) |
| 2. Enemy | what everyone else sells ("basic tinted sunglasses with no medical backing") | make every alternative look cheap |
| 3. Mechanism | named, ownable reason it works ("GlareCut Technology engineered for aging eyes") | belief that this one is different |
| 4. Feature stack | 3 benefits, often emoji checks | answer the top 3 objections |
| 5. Authority + transformation | testing, doctors, before→after outcome | proof + the after-state |
| 6. Risk reversal + crowd | guarantee, customer count | remove risk, social proof |

Also record: line length, emoji use (✔️, 👉), paragraph rhythm, reading level, formatting (line breaks, caps), and the **headline style** (e.g. problem-solution, skeptic-aware "…That Actually Work").
**Output:** the beats table + style notes (sections 1–2 of the template).
**Done when:** every sentence of the caption belongs to a beat.

## Step 3 — Claims inventory
**Purpose:** guarantee claims carry over at full strength.
**Do:** list every claim in the caption and headline (numbers, conditions, authority, technology names, guarantees, counts) and write our line next to it. Our line keeps the **same strength and specificity**: "clinical testing and doctor recommendations" stays "clinically tested and doctor-recommended", "over 10,000 people trust us" stays "over 10,000 people trust <BRAND>", "risk-free for 30 days" stays 30 days. Mechanism names get our brand's version of the same structure ("<Name> Technology") or the competitor's generic term if it isn't trademarked to them.
**Never:** soften, drop, hedge ("may help"), or add notes like "keep only if true" / "check compliance" / alternative safer lines. The operator validates claims.

## Step 4 — Write Version A per angle card (1:1 structure)
**Do:** one copy set per card in 3.1 (validated and opportunity; killed angles get none). Keep the competitor's beat structure, and aim every beat at the card:
- Hook: from the card's HOOK TEMPLATES or the Hook Library (3.3), in customer words from the hook-ready phrases (3.5).
- Enemy: the card's ENEMY. Mechanism: the card's MECHANISM (1.6). Feature stack: answers the top objections of the card's avatar (1.4), in objection-ready phrases. Authority + transformation: the card's PROOF and PROMISE. Risk reversal + crowd: as the competitor.
- The card the competitor's primary caption runs on stays closest to 1:1.

Then, per set: one paragraph/line group per beat, same order, same approximate length and rhythm, same emoji pattern, original wording (paraphrase), simple vocabulary, market language and spelling, our brand name where the competitor uses theirs. Read it aloud: it should feel like the same ad written by a different person, for that card's avatar.

## Step 5 — Write Version B (short) per angle card
**Do:** 3–5 lines for testing: hook (one line from 3.3 / 3.5, often the blame-shift or the strongest claim) → mechanism/benefits in one sentence → risk reversal + crowd → CTA line with an emoji arrow if the competitor uses emojis. Same claims, same strength.

## Step 6 — Headlines, description, CTAs
- **5 headlines per angle card** (≤40 characters where possible): #1 mirrors the competitor's headline structure; the rest come from the Hook Library (3.3) and the headline-ready phrases (3.5) of that card (situation, enemy, fit, blame-shift, outcome). Star the top 2–3 to test first.
- **Link description:** the competitor's pattern if they use one; otherwise three proof points from the page separated by " · " (fit / guarantee / shipping offer).
- **CTA:** the competitor's CTA buttons and rotation, using Meta's button names as they appear in the data (main + 2 alternates). One rotation for every set.

## Step 7 — Final check and save
Checklist: one copy set per angle card in 3.1, each headed with its card ID, avatar and hook source · every beat present in order · every competitor claim present at the same strength · no competitor name · market language/spelling/currency · length close to the competitor's · no caveat or "note" lines anywhere · headlines starred. Return the full AD_COPY.md as text (sub-agent) or save it to `05_ads/AD_COPY.md` (master).

---

## Noxis run — worked example (corrected)
> The Noxis run had one copy set (before Step Alpha). Today this would be the copy set of the card the competitor's primary caption runs on.


Beats (Plaims, paraphrased): 1 "Wondering why some night driving glasses don't work? Here's what to look for…" · 2 others = "basic orange-tinted sunglasses with no medical backing" · 3 "Specialized GlareCut Technology engineered for aging eyes" · 4 perfect brightness, peripheral protection, fits over prescription glasses · 5 "clinical testing and doctor recommendations" + "transformed blinding LED headlights into soft, manageable light" · 6 "risk-free for 30 days" + "over 10,000 people trust us".

Version A as it should have been written (beat 5 and 6 at full strength):
```
Ever bought night driving glasses that did nothing? Here's why most of them fail...

Most "night vision" glasses are just yellow-tinted sunglasses with no medical backing. They turn white glare into
yellow glare and call it a day.

Noxis is different. Our Glare Cut Technology was engineered for the way modern LED headlights hit aging eyes:

✔️ Perfect brightness, so the road doesn't go dark
✔️ Wraparound side lenses, so nothing blinds you from the side
✔️ Slips right over your prescription glasses

Backed by clinical testing and doctor recommendations, Noxis turns blinding LED headlights into soft, manageable light.

Try Noxis risk-free for 30 days. Over 10,000 people already trust us to get them home after dark.
```
What the first Noxis draft got wrong: beat 5 became "Tested by night drivers, recommended by eye-care professionals" (weaker than clinical testing + doctors), beat 6 used "1,300+ drivers" instead of mirroring "over 10,000 people", and the file ended with a note suggesting to keep the authority claim "only if Noxis has that backing" — all three violate operator rule 1.

Version B: "LED headlights got brighter. Your eyes didn't. / Noxis amber lenses take the blinding edge off oncoming headlights, slip over your prescription glasses, and come with a 30-day money-back guarantee. / Rated 4.8/5 by 1,300+ drivers. 👉 Get yours today." (rating line = page copy figure)

Headlines: ★ Headlight Glasses That Finally Work · ★ Stop Squinting at Oncoming Headlights · Drive at Night Again, Without the Glare · The Night Driving Glasses That Fit Over Yours · Brighter Headlights? Amber Takes the Edge Off.
Description: Fits over prescription glasses · 30-day money-back guarantee · Free shipping over $30.
CTA: Shop now (main) · See details · Learn more.
