# Video ad policy — what these scripts will and will not do

_Written 2026-10-30 during the Mojo v01 build, after the process in
`references/14-video-ads.md` was found to require steps we cannot carry out._

## The line

Studying a competitor's winning video ads and rebuilding what makes them work is
normal, legitimate competitive practice. Shipping their actual footage and audio
as our own ad is not. The two are easy to confuse because the output looks
similar, so the line is written down here.

**We do this — all of it:**

- Pull, rank and study competitor video ads: hooks, beat structure, pacing,
  shot order, length, claim ladder, offer placement, caption style, what the
  ad is doing emotionally and why it has run for 300 days.
- Reuse the *structure*: the six-beat framework (hook / enemy / mechanism /
  feature stack / proof / offer), the beat timings, the caption treatment,
  the voice-over-driven format, the aspect ratio and length.
- Write our own script to that structure, with our claims at full strength.
- Shoot or generate our own footage and stills, and voice it with a licensed
  stock voice or a voice we own.

**We do not do any of this:**

| Not this | Why |
|---|---|
| Keeping the competitor's video clips ("class (a) clean frames") in our ad | It is their footage. Cutting our captions over it does not make it ours. |
| Keeping their original voice-over track for the lines we didn't rewrite | Same: their recording, their performance. |
| Keeping their music bed | Licensed to them, not to us. |
| Cloning the voice out of their ad with ElevenLabs instant voice cloning | ElevenLabs' terms require the right to clone a voice, and we have no consent from the speaker. If the speaker is a real person this is also a voice-likeness problem in the UK/EU and most US states. "It might be an AI voice" is not consent — we cannot tell, and the burden runs the other way. |
| Scanning frames to erase "any competitor trace" from footage we are reusing | Removing the logo, the domain and the packaging from someone else's clip, then stripping the file metadata, is concealment. The frame-sweep and the metadata strip are fine on **our own** output — that is what they are for here. |

The reusable test: **if the step only makes sense because it hides where the
material came from, the material should not be in our ad.**

## What this means in practice

`video_build_stills.py` builds the visual track from our own stills with Ken
Burns moves cut to our own voice-over's word timings. It is a complete
replacement for reusing competitor clips, and on this run it produced a
higher-resolution ad than the source would have (their downloads are 360x640).

`video_eleven.py` deliberately has **no `clone` subcommand**. It lists only the
account's premade (licensed) voices and voices the operator owns. Its `stt` and
`isolate` subcommands are for checking *our own* audio.

The older `video_vo.py` still has cloning in it. It is kept for voices the
operator legitimately owns (e.g. a brand voice built from a take the operator
recorded or commissioned). It must not be pointed at a competitor's ad.

## If the operator wants the competitor's exact look

Two legitimate routes:

1. **Licensed stock.** The lifestyle beats in these ads (man on sofa, couple in
   bedroom, close-up of fabric) are generic; equivalents are available from
   stock libraries with a commercial licence for a few pounds a clip.
2. **Generate it.** ArgoLink has image-to-video (MiniMax H3 $0.039/s at 768p,
   Wan 3.0 $0.075/s at 720p) and takes our packshot as the first frame, so we
   can produce real motion of our own product. A 45 s ad of generated motion
   costs roughly $1.75–3.40. Include the PRODUCT FIT SPEC sentence in every
   prompt.

Neither route needs anything that belongs to the competitor.
