# 14 — Video ad remakes (competitor top videos → our brand)

Goal: take the competitor's best-performing Meta video ads and remake each one for our brand with the least generation possible: keep every clean frame, fix overlays locally, re-voice only what must change, and regenerate only the clips that show the competitor's product, after the operator approves. Each final video is ours: no competitor name, logo, packaging, domain or caption left anywhere, our claims at the competitor's strength, and a script and audio curve that differ from the original.

Distilled from the Krino (Mexico, 5 HAIRO remakes, English → Mexican Spanish) and Aurea (US, Manifestly remakes, English → English) runs, October 2026. Read `00-operator-rules.md` §16 first. Scripts: `scripts/video_*.py` (run with `python -I`, all have `--help`).

## Contents
1. When this runs, inputs, outputs, folders
2. Step 1 — Candidate selection (operator gate)
3. Step 2 — Clips: scene detection and the competitor-trace audit
4. Step 3 — Audio decision per video
5. Step 4 — Script: the three mandatory remakes + competitor lines
6. Step 5 — Voice: clone the original voice (ElevenLabs)
7. Step 6 — Build the VO on the beats and splice/mix
8. Step 7 — Overlays and captions
9. Step 8 — Class (c) clips: list, cost, operator gate, generate
10. Step 9 — Assemble, strip metadata, independent check
11. Step 10 — Clean the folder, write the PLAN
12. Costs
13. Per-video checklist
14. Lessons (each one cost a redo)

---

## 1. When this runs, inputs, outputs, folders

**When:** when the operator asks for video ads ("remake their top videos", "do the videos"), after the packshot exists (`03_product-images/<slug>-packshot.png`) and the market/offer are decided (BRIEF.md, AD_COPY.md). It is separate from the 25 image ads (08) and runs in its own stream.

**Inputs:** Brandsearch MCP (07), the packshot, AD_COPY.md (offer, claims, numbers), the market language, the ElevenLabs key (`G:/Ecom/Products/.secrets/elevenlabs.env`, `ELEVENLABS_API_KEY`), the Kie key (only for class (c) clips).

**Folder rule (operator):**
```
05_ads/REMAKE_CANDIDATES.md            the ranked list the operator confirmed
05_ads/remake-candidates/NN-brand-id.mp4  downloaded sources (+ _SHEET.jpg)
05_ads/generated/videos/
    v01-<slug>.mp4                     ONLY final videos at the root
    v01-work/v01-clips.jpg             labelled clip contact sheet
    v01-work/v01-draft.mp4             last draft (REGENERAR/REGENERATE label on (c) clips)
    v01-work/v01-PLAN.md               the full record of the remake
```
Everything else (stems, TTS takes, words.json, .ass, keyframes, generated clips, frame strips, scripts) lives in `PRODUCT_DIR/scratch/videos/vNN/` while working and is deleted once the video is final (`video_finalize.py clean`). **Why:** the operator found the videos folder full of wavs, scripts and PNGs from five remakes and asked for finals only, plus one work folder per video with the clips sheet, the draft and the plan.

## 2. Step 1 — Candidate selection (operator gate)

1. Pull the competitor's video ads with both Brandsearch endpoints and `is_video="true"`, `fields` including `reach_rank` (07 §Video ads).
2. Rank by **`reach_rank` ascending** (Top rank by impressions). Tie-breakers: days running, then copies + `duplicate_count`. Spend only for EU markets (operator rule §6).
3. Keep **~20 candidates**, deduped: competitors remix the same UGC clips across many ads, so keep a pick only when its hook, script or format differs. Fill gaps (format, local proof) with 1–2 category ads.
4. Download each (`download_ad(..., media="video")`, 1 credit; fetch the URL at once, it expires) to `05_ads/remake-candidates/NN-brand-id.mp4`; `transcribe_ad` (1 credit) or a local transcript (Step 3) for the VO text.
5. Write `05_ads/REMAKE_CANDIDATES.md`: summary table (NN, brand, id, format/length, reach_rank, days, copies+dup, angle), then per ad: hook verbatim, VO verbatim, overlays, angle, why it works in the market, what the remake needs (production needs only, no copy yet). Contact sheet `_SHEET.jpg` with the frame at 0.3 s.
6. **STOP for operator confirmation.** Nothing is remade or generated before the operator confirms or swaps the picks.

## 3. Step 2 — Clips: scene detection and the competitor-trace audit

```
python -I video_clips.py SRC.mp4 --out scratch/videos/v01/clips
```
Scene detection (ffmpeg, threshold 0.25), one keyframe per clip in `kf/`, contact sheet, and a list of **weak cut candidates** (score 0.12–0.25). Audit those times too: a light-leak flash hid a cut in Krino v03, and 0.7 s of the HAIRO jar label stayed in the draft until the independent check caught it.

Audit **every clip at full resolution** (keyframe plus extra frames where things move) for any competitor trace: packaging, logo, label, wordmark, website/domain, @handles, captions and text overlays naming the brand, end cards, seals/badges, the brand spoken in the audio. Third-party brands (a Toppik bottle, a printed comb) count too. Then classify:

| Class | Meaning | Action |
|---|---|---|
| **a** | clean: no trace, no overlay to change | kept as is |
| **b** | only a text overlay, caption, bubble or small fragment to fix | fixed locally (Step 7): cover + new overlay, blur a label fragment, patch a seal |
| **c** | the competitor's product/packaging is the subject, or a trace that cannot be covered cleanly | **regeneration**, listed with prompts and costs, operator confirms first (Step 8) |

Redraw the sheet with the classes: `video_clips.py SRC --out .../clips --classes "1-20=b,21=c" --sheet .../v01-work/v01-clips.jpg`. Reuse before generating: the same shot often appears in several ads (Krino v04 reused v01's generated shelf clip, 0 credits).

## 4. Step 3 — Audio decision per video

Transcribe locally (free) and separate the stems:
```
python -I video_transcribe.py SRC.mp4 --out orig_words.json --lang en --prompt "Hairo"
python -I video_vo.py separate SRC.mp4 --out stems        # demucs htdemucs → vocals.wav, music.wav
```
Decide with the operator rules:
- **No lip sync, ever.** Never generate lip-synced video. If a presenter speaks on camera in sync with the VO and never names the competitor, keep the original audio (Aurea v04). If an on-camera line names the competitor, it is a (c) problem for that shot, not a lip-sync job.
- **Voice-over:** re-voiced. Same market: swap the brand and remake the three mandatory lines (Step 4), spliced into the original voice track with a clone of the original voice. New market: translate natively (market vocabulary from the research bible, not literal), every line re-voiced.
- **Music or sound effects only:** keep the audio unchanged (stream copy). Krino v02 (rap track) needed no VO work.
- **Character dialogue** (animated or acted scenes) that never names the competitor: keep it (Aurea v01, 0–43 s). Re-voice only the narration that names them.
- A demucs `music` stem at about −55 LUFS means there is no music bed, only room tone (Krino v04).

## 5. Step 4 — Script: the three mandatory remakes + competitor lines

```
python -I video_vo.py skeleton orig_words.json --out script.json --total 23.5 --seed <any>
```
The skeleton turns the transcript into sentence lines with their beats (`start` = original beat start, `end` = next beat start − 0.06 s) and marks:
- **Always remade, in every video, even when nothing else needs remaking (operator rule), so the script and the audio curve differ from the original:**
  1. **the hook**: the opening sentence or thought. Its length comes from the transcript logic (the whole opening question or claim, which can span two short sentences), not a fixed number of seconds. Merge or split skeleton lines so the hook line is exactly that thought.
  2. **the very end**: the closing line or CTA.
  3. **one random line from the body** (`--seed`; any line between hook and end).
- **Also re-voiced:** every line that names the competitor, its domain, its numbers that differ from ours (32,000 → our 40,000 per the bible), or its offer when ours differs. Set `"keep": false` on those.
- Every other line keeps `"keep": true`: the original voice stays.

Rewrite each remade line with the **same meaning, length and claim strength**, in the market language ("Aren't these powders just the same as the old hair fibers?" → "Aren't these powders just like the old hair fibers?"). Claims at full strength (rule §1), offer from AD_COPY.md, no price spoken if the image-ad rule applies, no third-party brand names. For TTS only, respell names phonetically in `"say"` ("Aurea" → "Awe-ree-uh", read "or-AY-uh" otherwise; "Citrine" → "Citreen"); captions keep the real spelling.

**Fit before voicing:** a line must fit its slot at natural speed or with a speed-up of **at most 1.08x**. If not, rephrase it shorter (the Krino drafts ran lines at 1.14–1.30x and they sounded rushed). Keep the original pauses and never let a line run across a cut.

## 6. Step 5 — Voice: clone the original voice (ElevenLabs)

**Operator rule: all audio and voice work goes through the ElevenLabs API directly, not Kie.** Starter plan: instant voice cloning, 40,000 characters/month, 10 voice slots.
1. Take a clean sample of the original VO from the demucs `vocals.wav`: **30–90 s** if the video has it (all of it if shorter), speech only, no music bleed, no other speakers.
2. Clone it:
   ```
   python -I video_vo.py clone --name "Krino v03 narrator" --from stems/vocals.wav --start 0 --end 60
   ```
   Record the `voice_id` in the PLAN (§Voice).
3. Write the spec (`scratch/videos/v03/voice.json`) and keep it in the PLAN:
   ```json
   {"provider": "elevenlabs", "voice_id": "<id>", "model_id": "eleven_multilingual_v2", "language_code": "es",
    "voice_settings": {"stability": 0.55, "similarity_boost": 0.9, "style": 0.15, "use_speaker_boost": true}}
   ```
   These are the operator's default settings (reference implementation: `G:/Ecom/Products/Krino/05_ads/voice-samples/elevenlabs/eleven_vo.py` + `ELEVENLABS_SPEC.json`). Same spec, same voice_id for every line of a video, so the voice is identical across the splice.
4. **Rights:** ElevenLabs' terms require the right to clone a voice. If the original sounds like a real person rather than a stock AI/TTS voice, flag it in the PLAN ("original voice sounds like a real person: operator to decide") so the operator decides before the video ships.
5. **Delete clones no longer needed** (`video_vo.py delete-voice <id>`) once the video is final; there are only 10 slots.

**New market (translation):** clone the original voice and voice the translated lines with `language_code` set. If the accent does not land, audition alternatives (`video_vo.py audition --text "<same 2–4 lines>" --spec a.json b.json`), the operator listens and picks, and the pick is saved as the brand's VOICE_SPEC.json (exact spec + the reusable function) so every later video uses the same voice. Krino MX Voz (`drn8JPuDNuSugjUdIuYG`, an ElevenLabs clone of the operator-picked Gemini take) is the Krino brand voice.

**Why not the others:** Gemini TTS (Kie) varies between takes, so separate calls never match; edge-tts was rejected as robotic (flattest pitch, 3.2 semitones SD); Kie's ElevenLabs is text-to-speech only (no clone) and was failing with 500 errors all day. The ElevenLabs free tier has no instant cloning. edge-tts stays usable only as a free timing draft.

## 7. Step 6 — Build the VO on the beats and splice/mix

```
python -I video_vo.py build script.json --out vo.wav --spec voice.json --match stems/vocals.wav
```
Only lines without `keep` are voiced (cached by text hash, so re-runs cost nothing). Each line is trimmed, inner pauses shortened to 0.13 s if needed, sped up at most 1.08x and placed at its beat start. `REPHRASE` lines (exit 2) go back to Step 4. `--match` sets the new lines to the loudness of the original voice stem. The command prints the `--replace` windows.

**Splice (same voice, original track kept elsewhere):**
```
python -I video_vo.py mix --vo vo.wav --music stems/music.wav --orig orig.wav --replace <windows> --duck 0 --out mix.wav
```
Inside each window: music stem + new line; outside: the original audio untouched; 40 ms raised-cosine crossfades, which must sit in the original pauses (check the vocal stem is below about −45 dB there). Aurea v02/v05 used this to replace only the sentence naming the competitor.

**Full re-voice (translation):** voice every line, then
```
python -I video_vo.py mix --vo vo.wav --music stems/music.wav --duck 9 --lufs -14 --out mix.wav
```
Music sits **8–10 dB under the voice** while it speaks and returns between lines; the mix is normalised to **about −14 LUFS** and limited to −1 dBTP (the Krino v03 mix clipped at +0.1 dBTP before the limiter).

## 8. Step 7 — Overlays and captions

**Old overlays:** cover every old caption, bubble, label and end-card wordmark from the frame it appears:
- `delogo` band for word-by-word captions on busy footage (Krino v01: x36 y810 648x52 from 2.3 s);
- heavy blur box (Krino v03 translucent caption boxes: blurred, then the new box drawn on top, always at least as big as the old box);
- opaque colour box where the background is flat (cream end board);
- per-frame detection when boxes change size every frame (Aurea v01: black box rows + white text extents, one delogo per box), tracked elliptical blur for a moving third-party label;
- a feathered patch of clean background for a small seal (Aurea v04).

**New overlays:** same style, position and timing as the original: measure font, cap height, colours, outline/box and centre on a full-resolution frame. Reply bubbles and header lines are PNGs drawn over the old ones (`--overlay`).

**Captions** re-timed word by word from the new audio:
```
python -I video_transcribe.py mix.wav --out words.json --lang es --prompt "Krino"
python -I video_captions.py ass words.json --out caps.ass --upper --pos 360,836 --font "Montserrat ExtraBold" --size 37 \
       --accent "fibras,krino" --accent-color B9B8F5 --start-after 2.2 --fix "crino=Krino" [--chunks chunks.txt] [--box 000000 --box-alpha 0.6]
python -I video_captions.py burn SRC.mp4 --out draft.mp4 --ass caps.ass --cover "2.3-23.5:36,810,648,52" \
       --overlay "0-2.3:bubble.png:59,224" --audio mix.wav
```
Use `--chunks` when the caption text must read exactly (brand spelling, digits like 40,000 and 30%, the original's phrase breaks). Every remade line gets its new caption; captions must match the audio word for word.

## 9. Step 8 — Class (c) clips: list, cost, operator gate, generate

**Never generate a (c) clip without the operator's confirmation.** In the PLAN, list each one: time range, what it shows, the reference frame (`cNN_ref.png`, mid frame with the caption removed), two prompts and the cost.
1. **Start frame:** `gpt-image-2-5-sunburst-image-to-image`, 1K, the video's aspect ratio; image 1 = the original frame, image 2 = our packshot. Short prompt: "Same shelf, wall and light as image 1. Replace the jars and boxes with two Krino jars exactly like image 2, on plain matte navy boxes with no text. Same angle."
2. **Animation:** `wan/2-6-image-to-video`, 720p, 5 s, image = that start frame; prompt = the original motion ("Slow handheld push-in toward the jars. Static products, no text."). Trim to the clip length.
- `wan/2-6-video-to-video` takes reference videos only, no image input, so it cannot carry our packaging.
- One 5 s generation can cover several short shots of the same scene; check reuse across videos first.
- In the draft, (c) clips carry a red REGENERAR/REGENERATE label until replaced.
After approval: generate, check the start frame before animating (Krino v01 clip 21 was clean on the first try: 76 credits), and cut it in (Step 9).

## 10. Step 9 — Assemble, strip metadata, independent check

```
python -I video_finalize.py render draft.mp4 --out ../v01-no-son-fibras.mp4 --insert "21.17-23.5=c21_gen.mp4@1.0"
python -I video_finalize.py frames ../v01-no-son-fibras.mp4 --out scratch/videos/v01/frames.jpg
python -I video_transcribe.py ../v01-no-son-fibras.mp4 --out final_words.json --lang es --prompt Krino --against words.json
```
`render` replaces the (c) intervals with the generated clips (scaled/cropped to the base size and fps), encodes with no metadata (operator rule §14) and reports length and tags. Burn captions before or after the insert as the layout needs; the insert must not cover a caption that should stay.

**Independent check** (a fresh agent or a second pass, not the one that built it):
- frames every 0.5 s (`frames`), plus full-resolution crops of every caption band, cover and blur: no competitor name, logo, packaging, domain, handle or seal left; no seam or smear that reads at playback size;
- whisper on the final (`--against words.json`): every word present, **sync within 0.15 s**, no competitor name spoken, brand pronounced right (listen: Whisper heard "Aurea" as "Oreo" in the mix);
- the three mandatory remakes are in: hook, end and one body line differ from the original in audio and captions;
- captions match the audio word for word, correct spelling in the market language;
- loudness about −14 LUFS, peak ≤ −1 dBTP, length equal to the source, no black frames;
- metadata stripped (only standard muxer tags).
Fix and re-check until it passes; record the result in the PLAN.

## 11. Step 10 — Clean the folder, write the PLAN

```
python -I video_finalize.py clean PRODUCT_DIR/05_ads/generated/videos          # dry run
python -I video_finalize.py clean PRODUCT_DIR/05_ads/generated/videos --yes
```
Then delete the scratch folder of that video and the voice clone if no further video needs it.

`vNN-PLAN.md` sections: source (file, length, size, fps, reach_rank); 1 Clips (table: #, start–end, what is shown, competitor mention, class, action); 2 Voice-over (original vs new per beat, which lines are the hook/end/body remakes, voice_id + spec, real-person flag, speed-ups); 3 Overlays (method, style measurements, original vs new text table); 4 Class (c) clips (prompts, costs); 5 Credits (spent, remaining); 6 Final cut; 7 Independent check.

## 12. Costs

| Item | Cost |
|---|---|
| Kie GPT Image 2.5 start frame, 1K | 6 credits |
| Kie `wan/2-6-image-to-video` 720p, 5 s | 70 credits |
| One (c) clip (frame + video) | 76 credits (one retry +76) |
| Kie Gemini TTS (legacy, not used) | about 0.075 credits per second of audio |
| Kie lip sync (never used) | 8 credits per second |
| ElevenLabs TTS (Starter, 40,000 characters/month) | about 1 character of quota per character sent; a 30 s ad is ~500 characters |
| ElevenLabs instant clone | included; 10 voice slots |
| Brandsearch `download_ad` / `transcribe_ad` | 1 credit each |
| faster-whisper, demucs, ffmpeg, edge-tts | free (local) |

Check the Kie balance before (c) generations and report spend in the PLAN and delivery.

## 13. Per-video checklist
- [ ] Candidate confirmed by the operator (REMAKE_CANDIDATES.md)
- [ ] Clips detected, weak cuts audited, every clip classed a/b/c, sheet `vNN-clips.jpg`
- [ ] Audio decision recorded (VO / music only / dialogue kept; no lip sync)
- [ ] Hook (whole opening thought), end/CTA and one random body line rewritten: same meaning, length, claim strength
- [ ] Every line naming the competitor re-voiced; our numbers and offer
- [ ] Original voice cloned from 30–90 s of clean vocals; voice_id in the PLAN; real-person flag if needed
- [ ] Lines fit at ≤ 1.08x, on their beats, no VO across cuts; music 8–10 dB under the voice, about −14 LUFS
- [ ] Old overlays covered; new captions same style/position, re-timed word by word, matching the remade lines
- [ ] (c) clips listed with start-frame + animation prompts and costs; generated only after the operator confirms
- [ ] Final rendered without metadata; independent check passed (frames 0.5 s, whisper, sync ≤ 0.15 s, remakes present)
- [ ] Folder cleaned (root = finals; vNN-work = clips/draft/plan); clone deleted when no longer needed

## 14. Lessons (each one cost a redo)
- **Animate-replace person swaps rendered badly and glitchy** (operator). Do not swap people with animate/replace models; keep the original people and change only our product, overlays and voice.
- **Clean up after scripts:** five remakes left hundreds of wavs, PNGs, json and one-off scripts in the videos folder. Work in `scratch/videos/vNN/`, run `video_finalize.py clean` at the end.
- **Never write into the Git Bash root** (`/`, i.e. `C:/Program Files/Git`): relative paths from a shell whose cwd was reset landed files there. Always use absolute paths into PRODUCT_DIR or scratch.
- Scene detection misses cuts behind flashes and light leaks: audit the weak cut candidates and check frame-difference spikes.
- Whisper mis-hears brand names ("Hairo" → "heroin", "Krino" → "crino"): pass `--prompt` with the brand and fix the caption words (`--fix`, `--chunks`).
- Speed-ups above 1.08x sound rushed: rephrase instead.
- Delogo bands leave a soft smear where an old box was wider than the new one; on flat backgrounds use a colour box or a background patch instead.
- Gemini TTS: about half of the first Kie attempts failed with 524 timeouts (free); takes drift 5 semitones between calls. Another reason for the ElevenLabs clone.
