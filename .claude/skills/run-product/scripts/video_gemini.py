#!/usr/bin/env python3
"""Video analysis with Google Gemini Flash through ArgoLink: scenes, competitor-trace audit, VO, overlays, framework.

Replaces the "watch and understand" part of 14-video-ads.md (Step 1 candidate write-up, Step 2 clip audit,
script framework / beat map). Mechanical timing stays local: video_clips.py for keyframes and the clip sheet,
video_transcribe.py (whisper) for word timestamps and the sync check.

Usage:
  python -I video_gemini.py SRC.mp4 --out analysis.json --competitor "Sofyre"
  python -I video_gemini.py VIDEOS_DIR --out-dir analyses/ --competitor "Sofyre" --workers 4
  python -I video_gemini.py SRC.mp4 --out a.json --competitor Sofyre --extra "Also list every shot of a tractor."
Options: --model (default gemini-3.8-flash), --max-mb (default 15: larger files are re-encoded to 480p first).
Output JSON: duration_s, format, framework, music, hook, cta, beat_map[], scenes[] (start/end, shows,
on_screen_text, competitor_traces, class a/b/c, class_reason), vo[] (start/end, speaker, on_camera, text),
overlays[] (start/end, text, position, style). Existing outputs are skipped.
Cost: about $0.005 per 30 s ad (input $0.225 / output $1.125 per 1M tokens). Tested 2026-11-01 on a Sofyre ad.
Reads ARGOLINK_API_KEY from the environment, else from D:/Ecom/Products/.secrets/argolink.env.
"""
import argparse, base64, concurrent.futures as cf, json, os, shutil, subprocess, sys, tempfile, time, urllib.request, urllib.error

sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser(description="Analyse video ads with Gemini Flash via ArgoLink.")
ap.add_argument("src", help="an .mp4 file or a folder of .mp4 files")
ap.add_argument("--out", help="output JSON (single file mode)")
ap.add_argument("--out-dir", help="output folder (folder mode): <name>.json per video")
ap.add_argument("--competitor", default="", help="competitor brand name(s) to audit for, comma-separated")
ap.add_argument("--extra", default="", help="extra instruction appended to the prompt")
ap.add_argument("--model", default="gemini-3.8-flash")
ap.add_argument("--workers", type=int, default=4)
ap.add_argument("--max-mb", type=float, default=15.0)
args = ap.parse_args()

KEY = os.environ.get("ARGOLINK_API_KEY")
if not KEY:
    p = "D:/Ecom/Products/.secrets/argolink.env"
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if line.startswith("ARGOLINK_API_KEY="):
                KEY = line.split("=", 1)[1].strip()
if not KEY:
    sys.exit("ARGOLINK_API_KEY is not set")

PROMPT = """You are a forensic analyst of direct-response video ads. Watch AND listen to the whole video.
Return ONLY JSON with exactly these keys:
{"duration_s": number,
 "format": "UGC | product demo | talking head | VSL | animation | text-overlay | mixed (say which)",
 "framework": "name the structural skeleton, e.g. Hook-Problem-Agitate-Mechanism-Proof-Offer-CTA",
 "music": "genre, energy curve, key SFX moments with timestamps",
 "hook": {"spoken": "...", "on_screen": "...", "visual": "what stops the scroll", "type": "question|bold claim|pain|stat|curiosity gap|social proof|contrarian|testimonial|warning|if-then|enemy|story|other", "ends_s": number},
 "cta": {"text": "...", "start_s": number, "urgency": "..."},
 "beat_map": [{"beat": "Hook|Problem|...", "start_s": n, "end_s": n, "function": "..."}],
 "scenes": [{"n": 1, "start_s": n, "end_s": n, "shows": "what is on screen, people, setting, camera move",
             "on_screen_text": "exact text or empty",
             "competitor_traces": ["every packaging, logo, label, wordmark, domain, @handle, caption, end card, seal or spoken name of the competitor or any third-party brand visible or heard in this scene"],
             "class": "a|b|c", "class_reason": "a = clean, nothing to change; b = only a text overlay/caption/small fragment to fix locally; c = the competitor product or packaging is the subject or a trace cannot be covered cleanly (needs regeneration)"}],
 "vo": [{"start_s": n, "end_s": n, "speaker": "narrator|on-camera person|character", "on_camera": true, "text": "verbatim"}],
 "overlays": [{"start_s": n, "end_s": n, "text": "exact", "position": "top|middle|bottom|...", "style": "font, colour, box, animation"}]}
Rules: every hard cut is its own scene (include short cuts under 1 s); timestamps in seconds with one decimal;
VO verbatim, nothing paraphrased; list traces even when tiny or brief; never invent content you did not see or hear."""


def ffmpeg():
    p = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if p:
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def load(path):
    if os.path.getsize(path) <= args.max_mb * 1e6:
        return open(path, "rb").read()
    tmp = os.path.join(tempfile.gettempdir(), "gem_" + os.path.basename(path))
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", path, "-vf", "scale=-2:480", "-c:v", "libx264",
                    "-crf", "30", "-preset", "veryfast", "-c:a", "aac", "-b:a", "64k", tmp], check=True)
    data = open(tmp, "rb").read()
    os.remove(tmp)
    return data


def analyse(src, out):
    if os.path.exists(out):
        return f"skip  {os.path.basename(out)}"
    prompt = PROMPT
    if args.competitor:
        prompt += f"\nCompetitor brand(s) to audit for: {args.competitor}."
    if args.extra:
        prompt += "\n" + args.extra
    body = {"contents": [{"role": "user", "parts": [
        {"inline_data": {"mime_type": "video/mp4", "data": base64.b64encode(load(src)).decode()}},
        {"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2}}
    url = f"https://argolink.io/v1beta/models/{args.model}:generateContent"
    for attempt in range(3):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
            "Content-Type": "application/json", "x-goog-api-key": KEY, "Authorization": f"Bearer {KEY}"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=600))
            text = "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"])
            data = json.loads(text[text.find("{"):text.rfind("}") + 1])
            data["_source"] = os.path.abspath(src)
            data["_usage"] = r.get("usageMetadata")
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            return f"ok    {os.path.basename(out)}  scenes={len(data.get('scenes', []))}  c={sum(s.get('class') == 'c' for s in data.get('scenes', []))}"
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            err = e.read().decode()[:300] if isinstance(e, urllib.error.HTTPError) else f"{e}"[:200] + " | " + locals().get("text", "")[-200:]
            time.sleep(5 * (attempt + 1))
    return f"FAIL  {os.path.basename(src)}: {err}"


if os.path.isdir(args.src):
    if not args.out_dir:
        sys.exit("--out-dir is required for a folder")
    vids = sorted(f for f in os.listdir(args.src) if f.lower().endswith(".mp4"))
    jobs = [(os.path.join(args.src, f), os.path.join(args.out_dir, f[:-4] + ".json")) for f in vids]
    with cf.ThreadPoolExecutor(args.workers) as ex:
        for line in ex.map(lambda j: analyse(*j), jobs):
            print(line)
else:
    if not args.out:
        sys.exit("--out is required for a single file")
    print(analyse(args.src, args.out))
