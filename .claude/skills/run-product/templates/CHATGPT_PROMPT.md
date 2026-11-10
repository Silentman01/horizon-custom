# ChatGPT market research prompt — template (Step Alpha α3, spec 2.2)

How to use (runbook: `references/20-step-alpha-runbook.md` α3; spec: `references/19-step-alpha.md` lines 502–686):
1. Copy everything BELOW the cut line into `PD/00_alpha/chatgpt/CHATGPT_PROMPT.md`. Nothing above the line goes in that file.
2. Replace every `{{PLACEHOLDER}}` with this product's data from α1/α2. No `{{` may remain (`alpha_gate.py` fails on it).
3. Keep every platform, category, count, tag, the OUTPUT FORMAT block and the "You must" rules exactly as written. Add, never remove.
4. Lists go in as short bullet lines in plain words a stranger understands (no internal IDs except the hidden-angle IDs H1.. in category 8, which come back in the HIDDEN ANGLE EVIDENCE table and are matched in α4).

| Placeholder | Fill with (source) |
|---|---|
| `{{PRODUCT}}` | what the product is, in plain words, no brand (capture + the mechanism in `analysis1/1.1_customer.md`) |
| `{{PRODUCT_CATEGORY}}` | the category name shoppers use, e.g. "orthotic insoles" |
| `{{MARKET}}` | target country/countries and language (BRIEF inputs) |
| `{{COMPETITOR_BRANDS}}` | competitor brand + the other brands seen in the category (SATURATION in `1.2_patterns.md`, page, Amazon) |
| `{{AVATARS}}` | one line per avatar: the AV avatars of `1.1_customer.md` + the new avatars of the 2.1 explosion (`2.1_hidden_angles.md`): who, trigger event |
| `{{PAIN_POINTS}}` | top 10–15 ranked pains from `1.1_customer.md` in felt language |
| `{{DESIRES}}` | top ranked desires from `1.1_customer.md` |
| `{{OBJECTIONS}}` | objections from `1.1_customer.md` |
| `{{VALIDATED_ANGLES}}` | the angles the competitor runs (V cards in `1.4_angle_cards.md`, names + one line) |
| `{{SUBREDDITS}}` | suggested subreddits: category, primary pain, demographic, adjacent interests (ChatGPT may add more) |
| `{{FORUMS_AND_GROUPS}}` | niche / health / hobby / profession forums and Facebook group topics for these avatars |
| `{{AMAZON_PRODUCTS}}` | competitor products AND adjacent products in the category to read reviews of |
| `{{SEARCH_QUERIES}}` | 8–15 queries for Google "People Also Ask", TikTok/YouTube and blog comments |
| `{{HIDDEN_ANGLES}}` | every hidden angle H1..Hn from `2.1_hidden_angles.md`, one block each: `H1 — name: who, pain/desire, what to search (Reddit threads about …, Amazon reviews mentioning …, Quora questions about …)` |

✂ ─────────────── cut line: copy everything below into CHATGPT_PROMPT.md ───────────────

You are a market research DATA GATHERER. Your only job is to find and copy what real people say, verbatim, with sources.
Do NOT analyze, interpret, strategize, form hypotheses or make recommendations. Raw customer language only. Verbatim.
Use web browsing (or Deep Research) for every category below. Search the live web; do not answer from memory.

PRODUCT: {{PRODUCT}}
CATEGORY: {{PRODUCT_CATEGORY}}
MARKET: {{MARKET}}
BRANDS IN THIS CATEGORY: {{COMPETITOR_BRANDS}}

Use these to steer your searches toward the right people and topics (they are search guides, not answers to confirm):

Who buys this:
{{AVATARS}}

Problems they describe:
{{PAIN_POINTS}}

What they want:
{{DESIRES}}

Doubts they have:
{{OBJECTIONS}}

Angles already advertised in this category:
{{VALIDATED_ANGLES}}

== SEARCH these platforms ==
- Reddit: subreddits related to the product category, the primary pain, the target demographic, adjacent interests. Start with: {{SUBREDDITS}}
- Quora: questions about the product category, the pain, alternatives
- Amazon reviews: for competitor products AND adjacent products in the category — both positive and negative reviews. Start with: {{AMAZON_PRODUCTS}}
- Forum threads: niche forums, health forums, hobby forums, profession-specific forums. Start with: {{FORUMS_AND_GROUPS}}
- Facebook group discussions ("whatever" site:facebook.com/groups)
- TikTok/YouTube comments on related content
- Google "People Also Ask" results for related queries
- Blog comments on related articles
Search queries to start from (add your own): {{SEARCH_QUERIES}}

== COLLECT this data, VERBATIM ==

1. PAIN LANGUAGE
   - Exact quotes from real people describing their problem in their own words
   - The more raw, unfiltered, and emotional the better
   - "I can barely walk to the bathroom in the morning" is gold. "I experience discomfort" is worthless.
   - Collect 30-50 distinct verbatim pain quotes
   - Tag each with: source platform, subreddit/forum, estimated demographic of the poster

2. DESIRE LANGUAGE
   - Exact quotes from real people describing what they WANT, what they WISH for, what "better" looks like
   - "I just want to be able to play with my kids without wincing" is gold
   - Collect 20-30 distinct verbatim desire quotes
   - Tag each with source

3. OBJECTION LANGUAGE
   - Exact quotes from people expressing skepticism, doubt, or resistance about products in this category
   - "I've tried three different brands and they all flatten after a week" — that's a real objection in real language
   - Collect 20-30 objection quotes
   - Tag each with source

4. SOLUTION ATTEMPTS
   - What have people ALREADY TRIED to solve this problem?
   - List every alternative mentioned: other products, DIY solutions, medical treatments, lifestyle changes, things that worked, things that didn't
   - Include WHY they failed (in the customer's words)
   - This maps the competitive landscape from the CUSTOMER'S perspective, not the marketer's

5. TRIGGER EVENTS
   - What specific moments or events made people START looking for a solution?
   - "My doctor told me I need surgery if this doesn't improve" — that's a trigger
   - "I couldn't finish a hike with my family" — trigger
   - Collect 15-20 trigger events with verbatim quotes

6. EMOTIONAL EXPRESSIONS
   - Raw emotional language about this problem: frustration, anger, sadness, hopelessness, embarrassment, fear, determination
   - "I'm so tired of feeling like an old person at 35"
   - Collect 20-30 emotional expressions
   - These become the HOOKS and HEADLINES in our ads

7. IDIOMS & SLANG
   - How does this community TALK about this topic?
   - What nicknames, abbreviations, slang terms, inside jokes, common phrases, metaphors do they use?
   - This is how our copy sounds NATIVE to the audience instead of like a marketer who googled the topic

8. HIDDEN ANGLE VALIDATION
   - For each angle below, search for evidence that real people care about this angle
   - Are there Reddit threads about the angle's topic? Amazon reviews mentioning the use case? Quora questions about the pain?
   - This validates or kills hidden angles with real data
   - Report what you find for EVERY angle, including "no data found". Keep the angle ID (H1, H2, …) in the Angle column.
{{HIDDEN_ANGLES}}

9. DEMOGRAPHIC SIGNALS
   - What demographic patterns emerge from the discussions?
   - What age groups dominate the conversation?
   - What gender skew?
   - What professions or lifestyles mentioned most?
   - What geographic or cultural patterns?

10. COMPETITOR MENTIONS
    - What do real customers say about specific competitor brands in this category?
    - What do they praise? What do they complain about?
    - What brand names come up most? (= market awareness)
    - What features do customers compare across brands?

== OUTPUT FORMAT (use exactly this structure) ==

```
# {{PRODUCT_CATEGORY}} — Raw Market Data

## PAIN QUOTES (verbatim)
| # | Quote | Source | Platform | Est. Demo |
|---|-------|--------|----------|-----------|
| 1 | "..." | r/[sub]| Reddit   | F, 40s    |
...

## DESIRE QUOTES (verbatim)
[same table format]

## OBJECTION QUOTES (verbatim)
[same table format]

## SOLUTION ATTEMPTS
| Solution Tried | Why It Failed (verbatim) | Source |
|----------------|--------------------------|--------|
...

## TRIGGER EVENTS
[same table format as pain quotes]

## EMOTIONAL EXPRESSIONS
[same table format]

## IDIOMS & SLANG
| Term/Phrase | Meaning | Frequency | Source |
|-------------|---------|-----------|--------|
...

## HIDDEN ANGLE EVIDENCE
| Angle | Evidence Found | Source | Strength |
|-------|----------------|--------|----------|
...

## DEMOGRAPHIC SIGNALS
[summary with source citations]

## COMPETITOR MENTIONS
| Brand | Praise | Complaints | Frequency |
|-------|--------|------------|-----------|
...
```

Put the URL in the Source cell whenever you have it. Number the rows of every table.
If the answer is too long for one message, stop at the end of a full table row, write "CONTINUED — reply 'continue'", and carry on from the next row when asked. Never summarize to save space.

You must:
- NEVER paraphrase quotes. Verbatim only.
- NEVER invent or fabricate data. If a search yields nothing, say "no data found" — that's useful too.
- NEVER analyze, interpret, or recommend. Raw data only.
- ALWAYS cite the source (platform, subreddit/forum, URL if possible)
- Prioritize RECENCY — posts from the last 12 months carry more weight than older ones
- Prioritize EMOTIONAL INTENSITY — a long frustrated rant is more valuable than a neutral mention
