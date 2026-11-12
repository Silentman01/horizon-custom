"""Assemble a vertical ad from GENERATED clips + our VO + our music, with pill captions.

Workdir layout:
  shots.json     [{"clip": "clips/s01.mp4" | "endcard.png", "start": s, "end": s, "in": 0.0}]
                 (start/end on the VO timeline; a clip shorter than its slot is slowed to fit)
  vo.wav / words.json   from video_eleven.py tts (+ tighten)
  music.mp3      optional original bed (ElevenLabs Music)
  captions.json  optional [{"text": "...", "start": s, "end": s, "red": n_first_words_red}]
                 - if absent, phrases are built from words.json (break on punctuation, <= MAX_WORDS)

Steps:  video | captions | mix | assemble | all
  python -I video_build_clips.py all --dir <workdir> --out <final.mp4> [--font Poppins-SemiBold.ttf]
Caption style = the reference's: white rounded pill, black sentence-case text, centred at CAP_Y,
one phrase at a time; the hook's first words can be red.
"""
import argparse, json, os, subprocess, sys

W, H, FPS = 1080, 1920, 30
CAP_Y = 0.665            # pill centre as a fraction of frame height (reference ~2/3 down)
CAP_SIZE = 50
CAP_Y_OUTLINE = 0.42     # style B (outline text) centre
FONTS_DIR = "D:/Ecom/Products/Mojo/scratch/video/fonts"
MAX_WORDS = 4
MUSIC_UNDER_DB = 9.0     # music this many LU under the voice


def ff():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.stderr.write((r.stderr or "")[-3000:]); raise SystemExit("ffmpeg failed")
    return r


def probe_dur(path):
    import av
    c = av.open(path); d = c.duration / 1e6 if c.duration else 0; c.close(); return d


def step_video(d):
    shots = json.load(open(os.path.join(d, "shots.json"), encoding="utf-8"))
    os.makedirs(os.path.join(d, "norm"), exist_ok=True)
    lst = []
    for i, s in enumerate(shots):
        slot = s["end"] - s["start"]
        out = os.path.join(d, "norm", "n%02d.mp4" % i)
        src = os.path.join(d, s["clip"])
        fit = "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,setsar=1" % (W, H, W, H)
        if src.lower().endswith((".png", ".jpg")):
            n = int(round(slot * FPS))
            vf = "scale=%d:%d,zoompan=z='1+0.04*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=%d:s=%dx%d:fps=%d" % (
                W * 2, H * 2, max(n - 1, 1), n, W, H, FPS)
            run([ff(), "-y", "-loop", "1", "-i", src, "-vf", vf, "-frames:v", str(n),
                 "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", out])
        else:
            start_in = float(s.get("in", 0.0))
            avail = probe_dur(src) - start_in - 0.05
            speed = min(1.0, avail / slot) if slot > 0 else 1.0     # <1 = slow down to fill
            vf = "trim=start=%.3f,setpts=(PTS-STARTPTS)/%.4f,fps=%d,%s" % (start_in, speed, FPS, fit)
            run([ff(), "-y", "-i", src, "-vf", vf, "-an", "-t", "%.3f" % slot,
                 "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", out])
        print("  n%02d %5.2fs  %s" % (i, slot, s["clip"]))
        lst.append("file '%s'" % os.path.abspath(out).replace("\\", "/"))
    open(os.path.join(d, "concat.txt"), "w").write("\n".join(lst) + "\n")
    run([ff(), "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(d, "concat.txt"),
         "-c", "copy", os.path.join(d, "picture.mp4")])
    print("picture.mp4 %.2fs" % probe_dur(os.path.join(d, "picture.mp4")))


def phrases_from_words(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if w["word"][-1] in ".,!?;:" or len(cur) >= MAX_WORDS:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    caps = []
    for i, p in enumerate(out):
        nxt = out[i + 1][0]["start"] if i + 1 < len(out) else p[-1]["end"] + 0.4
        caps.append({"text": " ".join(w["word"] for w in p), "start": p[0]["start"], "end": nxt})
    return caps


def pill(text, font, red_words=0):
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(font, CAP_SIZE)
    words = text.split(" ")
    space = f.getlength(" ")
    widths = [f.getlength(w) for w in words]
    maxw = W - 2 * 90 - 2 * 34
    # balanced wrap into 1 or 2 lines
    lines = [list(range(len(words)))]
    if sum(widths) + space * (len(words) - 1) > maxw:
        best = None
        for k in range(1, len(words)):
            a = sum(widths[:k]) + space * (k - 1); b = sum(widths[k:]) + space * (len(words) - k - 1)
            if max(a, b) <= maxw and (best is None or max(a, b) < best[0]):
                best = (max(a, b), k)
        k = best[1] if best else len(words) // 2
        lines = [list(range(k)), list(range(k, len(words)))]
    asc, desc = f.getmetrics(); lh = asc + desc + 4
    lw = [sum(widths[i] for i in ln) + space * (len(ln) - 1) for ln in lines]
    padx, pady = 34, 18
    bw, bh = int(max(lw) + 2 * padx), int(lh * len(lines) + 2 * pady - 4)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0 = (W - bw) // 2; y0 = int(H * CAP_Y - bh / 2)
    d = ImageDraw.Draw(img)
    r = min(bh, int(asc + desc + 2 * pady)) // 2.6
    d.rounded_rectangle([x0 + 3, y0 + 5, x0 + bw + 3, y0 + bh + 5], radius=r, fill=(0, 0, 0, 60))  # soft shadow
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=r, fill=(255, 255, 255, 255))
    for li, ln in enumerate(lines):
        x = (W - lw[li]) / 2; y = y0 + pady + li * lh
        for i in ln:
            d.text((x, y), words[i], font=f, fill=(222, 38, 38) if i < red_words else (17, 17, 17))
            x += widths[i] + space
    return img


def ass_t(t):
    return "%d:%02d:%05.2f" % (int(t // 3600), int(t % 3600 // 60), t % 60)


def step_captions_outline(d, font):
    """Reference style B: bold white sentence-case text, dark outline + soft shadow, centred at CAP_Y_OUTLINE.
    Burned with libass at assemble time (writes captions.ass)."""
    caps = json.load(open(os.path.join(d, "captions.json"), encoding="utf-8"))
    fontname = "Poppins"
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: %d\nPlayResY: %d\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Cap,%s,112,&H00FFFFFF,&H00FFFFFF,&H00151515,&H64000000,-1,0,0,0,100,100,0,0,1,5,3,5,90,90,0,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n") % (W, H, fontname)
    ev = []
    for c in caps:
        y = int(H * c.get("y", CAP_Y_OUTLINE))
        ev.append("Dialogue: 0,%s,%s,Cap,,0,0,0,,{\\an5\\pos(%d,%d)}%s" % (ass_t(c["start"]), ass_t(c["end"]), W // 2, y,
                                                                         c["text"].replace("{", "(").replace("}", ")")))
    open(os.path.join(d, "captions.ass"), "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")
    print("%d outline captions -> captions.ass" % len(ev))


def step_captions(d, font):
    cpath = os.path.join(d, "captions.json")
    if os.path.exists(cpath):
        caps = json.load(open(cpath, encoding="utf-8"))
    else:
        words = json.load(open(os.path.join(d, "words.json"), encoding="utf-8"))["words"]
        caps = phrases_from_words(words)
        json.dump(caps, open(cpath, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    from PIL import Image
    cd = os.path.join(d, "caps"); os.makedirs(cd, exist_ok=True)
    blank = os.path.join(cd, "blank.png"); Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    total = probe_dur(os.path.join(d, "picture.mp4"))
    lines, t = [], 0.0
    for i, c in enumerate(caps):
        if c["start"] > t + 0.01:
            lines += ["file '%s'" % blank.replace("\\", "/"), "duration %.3f" % (c["start"] - t)]
        p = os.path.join(cd, "c%03d.png" % i)
        pill(c["text"], font, c.get("red", 0)).save(p)
        end = min(c["end"], total)
        lines += ["file '%s'" % os.path.abspath(p).replace("\\", "/"), "duration %.3f" % (end - c["start"])]
        t = end
    if total > t:
        lines += ["file '%s'" % blank.replace("\\", "/"), "duration %.3f" % (total - t)]
    lines.append("file '%s'" % blank.replace("\\", "/"))
    open(os.path.join(d, "caps.txt"), "w").write("\n".join(lines) + "\n")
    run([ff(), "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(d, "caps.txt"),
         "-vf", "fps=%d,format=argb" % FPS, "-c:v", "qtrle", "-t", "%.3f" % total, os.path.join(d, "caps.mov")])
    print("%d caption pills -> caps.mov" % len(caps))


def step_mix(d):
    vo = os.path.join(d, "vo.wav")
    total = probe_dur(os.path.join(d, "picture.mp4"))
    music = os.path.join(d, "music.mp3")
    if os.path.exists(music):
        mI = -14.0 - MUSIC_UNDER_DB - 1.0
        fc = ("[0:a]loudnorm=I=-15:TP=-2:LRA=9,aresample=44100,apad[v];"
              "[1:a]loudnorm=I=%.1f:TP=-6:LRA=7,aresample=44100,afade=t=out:st=%.2f:d=1.2[m];"
              "[v][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:%.3f,"
              "loudnorm=I=-14:TP=-1.5:LRA=11[a]" % (mI, total - 1.2, total))
        run([ff(), "-y", "-i", vo, "-i", music, "-filter_complex", fc, "-map", "[a]",
             "-ar", "44100", "-ac", "2", os.path.join(d, "mix.wav")])
    else:
        run([ff(), "-y", "-i", vo, "-af", "apad,atrim=0:%.3f,loudnorm=I=-14:TP=-1:LRA=11" % total,
             "-ar", "44100", "-ac", "2", os.path.join(d, "mix.wav")])
    print("mix.wav")


def step_assemble(d, out, cap_style="pill"):
    if cap_style == "outline":
        fesc = lambda p: os.path.abspath(p).replace("\\", "/").replace(":", "\\:")
        vf = "subtitles='%s':fontsdir='%s',format=yuv420p" % (fesc(os.path.join(d, "captions.ass")), fesc(FONTS_DIR))
        run([ff(), "-y", "-i", os.path.join(d, "picture.mp4"), "-i", os.path.join(d, "mix.wav"),
             "-vf", vf, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
             "-map_metadata", "-1", "-map_chapters", "-1", "-fflags", "+bitexact", out])
        print("-> %s" % out)
        return
    run([ff(), "-y", "-i", os.path.join(d, "picture.mp4"), "-i", os.path.join(d, "caps.mov"),
         "-i", os.path.join(d, "mix.wav"),
         "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
         "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
         "-map_metadata", "-1", "-map_chapters", "-1", "-fflags", "+bitexact", out])
    print("-> %s" % out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["video", "captions", "mix", "assemble", "all"])
    ap.add_argument("--dir", required=True); ap.add_argument("--out")
    ap.add_argument("--font", default="D:/Ecom/Products/Mojo/scratch/video/fonts/Poppins-SemiBold.ttf")
    ap.add_argument("--cap-style", default="pill", choices=["pill", "outline"])
    a = ap.parse_args()
    if a.step in ("video", "all"): step_video(a.dir)
    if a.step in ("captions", "all"):
        (step_captions_outline if a.cap_style == "outline" else step_captions)(a.dir, a.font)
    if a.step in ("mix", "all"): step_mix(a.dir)
    if a.step in ("assemble", "all"):
        if not a.out: raise SystemExit("--out required")
        step_assemble(a.dir, a.out, a.cap_style)


if __name__ == "__main__":
    main()
