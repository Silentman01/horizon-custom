# Comments / voice of customer: vibration-alarm (2026-11-19)

## Coverage
- Brandsearch: market card fitsleeps.com_9604404576605 lists 45 sellers but get_market returned 3 (fitsleeps.com, viereve.com, volbelli.com). Probed Instagram-matched ads for 12 brand domains (7 market + histrips, zzen.dk, itsnolya, tryawakeband, vibeloopbans) and three keyword searches. Result: **3 Instagram-matched ads in total** (vibeloopbans x2, jskmarketplace x1), all with 0 comments, 2 likes and 7-40 views. The big sellers (fitsleeps, dawnbands, softset, try-novia, truesleep) have none matched. **API comments: 0.** Credits spent about 40, none on comments.
- Fallback: Trustpilot of fitsleeps.com, 37 reviews quoted (20 from the 1-2 star filter, 17 from page 2). **This sample is biased to negatives, not random.** Reddit and Amazon searches returned nothing usable; competitor stores other than fitsleeps were not fetched.
- Caveat on quotes: the fetch tool returned quotes capped at 120 chars via a small model; treat as near-verbatim excerpts. Ids trustpilot_1..37 in comments_all.jsonl.

## Counts (counts.json, reviews only, channel "trustpilot")
objection 24, product_complaint 16, buyer_identity 6, service_complaint 4, seeding_suspect 4, noise 3, comparison 2, use_case_unadvertised 1. Stars: 1-star 15, 2-star 5, 4-star 3, 5-star 14. Intent ratio: **n/a (no ad comments)**. Shipping geo asks: 0. Reviewer countries: US 29, CA 2, GB 2, AU/FI/IE/MY 1 each.

## Top objections (labels from tags)
1. Vibration too weak (7) / doesn't work (5) / doesn't wake heavy sleepers (2): 14 comments, the core failure.
   - trustpilot_3 (US): "I slept through the alarms everyday. The vibrations are not that strong."
   - trustpilot_15 (US): "my phone on vibrate on my nightstand has a more aggressive vibration than the watch on my wrist."
2. Setup / no app (3 incl. usability): trustpilot_9 (GB): "An absolute pain to set up. Why something like this cannot be done via an app is beyond me." trustpilot_35 (US): "I wish there was a power button so I could shut it off on the weekends since the alarm times are hard to change."
3. Return cost / refund (2 return cost + 4 service complaints): trustpilot_18 (FI): "Returns are possible, but shipping costs more than the return itself is worth." trustpilot_19 (GB): "Return fees on this are ENORMOUS"
4. Trust/scam (2): trustpilot_8 (US): "Overall, a terrible experience which feels like a scam."
5. Design/reliability (2): trustpilot_17: "it does not vibrate on the body side, it vibrates away from body on the outboard side"; trustpilot_20: "its only gone off once when i needed it to and i’ve been wearing it for four nights"

## Failures where the competitor's promise breaks
- "100% wake-up" promise fails for heavy sleepers; the Pro version also fails (trustpilot_16: "The vibration did not wake me up, and I was somehow able to turn it off easily while asleep."; trustpilot_14: "The alarm was NOT waking my son up. He said he could barely feel it"). The company pushes the Pro up as a fix and it does not cure the gap.
- Phone vibrate is the real comparison (trustpilot_7, _15). Any stronger, escalating motor, on-body-side placement and a phone app are open gaps.
- Positive minority: gradual escalation and battery liked (trustpilot_21: "love the longevity of the battery life and how it starts off vibrating gently then increases intensity if not silenced."); heavy sleeper success (trustpilot_36: "And the intense pulse wakes me being a very heavy sleeper.").

## Use cases and buyers the ads don't target
Parents buying for teen sons (trustpilot_8, _14: bought the Pro for "my son"), partners buying for him (trustpilot_6), heavy sleepers, shared-home sleepers wanting not to wake others (trustpilot_32: "i love that i can get up without waking the whole house."), replacing a "blaring" alarm (trustpilot_24). The only ads found (vibeloopbans, jskmarketplace) target fitness/roommates, none of which show up in reviews.

## Countries
No shipping-geo comments (0). Reviewer countries: US 29 of 37; Trustpilot regional sites exist for AU, CA, IE, FR-BE, so the product ships to at least GB, CA, AU, IE, FI, MY.

## Buyer phrases (English)
Problem: "I slept through the alarms everyday" (trustpilot_3); "heavy sleepers" in title of review trustpilot_3. Desired result: "get up without waking the whole house" (trustpilot_32); "get me up without needing my blaring alarms" (trustpilot_24: "The fitsleep pro version has been able to help get me up without needing my blaring alarms.").

## Sentiment over time
Not computable for ads. In the review sample, all 1-2 star reviews are dated 2026-10-25 to 2026-11-17, a steady flow of failures (about 20 in 3.5 weeks on the filter page alone); no earlier history was fetched.

## Caveats
- Zero ad comments, so there is no evidence of buying intent from ad viewers. Reviews show post-purchase failure rates, not intent.
- Review sample is skewed to the negatives by design; do not read 15 one-star out of 37 as a failure rate. Trustpilot headline score reported 4.3-4.5 (unverified).
- One review alleges negative reviews are deleted; unverifiable.
- Seeding-like generic 5-stars: 4 of 37.
