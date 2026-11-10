#!/usr/bin/env python3
"""Captions for video remakes: styled .ass from word timings, cover the old overlays, burn in.

  ass WORDS.json --out caps.ass [--chunks chunks.txt] [style options]
      WORDS.json = [[start, end, "word"], ...] from video_transcribe.py run on the NEW voice-over.
      --chunks: one caption per line, exactly as it must read (brand spelled right, numbers as digits);
      each chunk starts on its first word's time (matched in order, accents/punctuation ignored).
      Without --chunks the words are grouped automatically (--max-words, break after punctuation).
      Each caption ends when the next starts, or 0.35 s after its last word if the gap is over 0.6 s.
      --snap vo.wav: move each caption start onto the real speech onset in the clean VO (Whisper starts a
      word that follows a pause up to ~0.3 s early, so the caption showed before the voice).
  burn SRC --out OUT.mp4 [--ass caps.ass] [--cover T0-T1:X,Y,W,H[:MODE]]... [--overlay T0-T1:IMG.png:X,Y]...
       [--audio mix.wav] [--fontsdir DIR]
      MODE = delogo (default, interpolates the band), blur (heavy box blur), or a hex colour (opaque box).
      Covers run first, then PNG overlays (reply bubbles, header lines), then the .ass captions.
      Without --audio the source audio is copied.

Style options (match the original: measure its cap height, colours and centre on a full-res frame):
  --res 720x1280 --font "Montserrat ExtraBold" --size 37 --color FFFFFF --outline 3 --outline-color 000000
  --shadow 1.5 --pos 360,836 --upper --accent-color B9B8F5 --accent "fibras,krino,40,000"
  --box 000000 --box-alpha 0.6  (opaque/translucent box behind the text instead of an outline)
  --box FFFFFF --radius 5 --pad 7,6 --box-height 26 --fontfile C:/Windows/Fonts/arialbd.ttf
      CapCut/TikTok pill: a rounded box sized to each caption (measured with --fontfile), text on top
      with no outline. libass boxes (--box alone) are square-cornered.
  --start-after 2.2 (no captions before, e.g. under a reply bubble) --end 23.5 --fix "crino=Krino,click=clic"
Fonts: put the .ttf next to caps.ass or pass --fontsdir. ffmpeg: $FFMPEG, PATH or imageio-ffmpeg.
"""
import argparse, difflib, json, os, re, shutil, subprocess, sys, unicodedata


def ffmpeg():
    p = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if p:
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def norm(w):
    return re.sub(r"[^a-z0-9%]", "", unicodedata.normalize("NFKD", w.lower()).encode("ascii", "ignore").decode())


def ass_col(hexrgb, alpha=0.0):
    r, g, b = hexrgb[0:2], hexrgb[2:4], hexrgb[4:6]
    return f"&H{int(alpha * 255):02X}{b}{g}{r}".upper()


def ts(x):
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


def chunk_auto(words, fix, maxw):
    chunks, cur = [], []
    for s, e, w in words:
        c = w.strip()
        core = c.strip("¿?¡!.,:;")
        if (not core or core == "%") and (cur or chunks):  # whisper splits "30%" -> "30", "%"
            grp = cur or chunks[-1]
            grp[-1] = (grp[-1][0], e, grp[-1][2] + core)
        else:
            cur.append((s, e, fix.get(core.lower(), core)))
        if c[-1:] in ",.?!:;" or len(cur) >= maxw:
            chunks.append(cur)
            cur = []
    return chunks + ([cur] if cur else [])


def chunk_given(words, lines):
    toks = [(k, t) for k, l in enumerate(lines) for t in l.split()]
    a, b = [norm(t) for _, t in toks], [norm(w[2]) for w in words]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    hit = {m.a + i: m.b + i for m in sm.get_matching_blocks() for i in range(m.size)}
    out = []
    for k, line in enumerate(lines):
        idx = [i for i, (kk, _) in enumerate(toks) if kk == k]
        m = [hit[i] for i in idx if i in hit]
        if not m:
            print(f"WARNING: no word matched for chunk '{line}', timing interpolated")
        out.append([words[m[0]][0] if m else None, words[m[-1]][1] if m else None, line])
    for i, c in enumerate(out):  # interpolate unmatched chunks between neighbours
        if c[0] is None:
            prev = next((o[1] for o in reversed(out[:i]) if o[1] is not None), words[0][0])
            nxt = next((o[0] for o in out[i + 1:] if o[0] is not None), words[-1][1])
            c[0], c[1] = prev, nxt
    return [[(s, e, t)] for s, e, t in out]


def pill_path(w, h, r):
    """ASS vector drawing (\\p1) of a w x h rectangle with rounded corners, origin top-left."""
    r = min(r, h / 2, w / 2)
    k = r * 0.45  # bezier handle: close to a quarter circle
    f = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")
    return " ".join([
        f"m {f(r)} 0", f"l {f(w - r)} 0", f"b {f(w - r + k)} 0 {f(w)} {f(r - k)} {f(w)} {f(r)}",
        f"l {f(w)} {f(h - r)}", f"b {f(w)} {f(h - r + k)} {f(w - r + k)} {f(h)} {f(w - r)} {f(h)}",
        f"l {f(r)} {f(h)}", f"b {f(r - k)} {f(h)} 0 {f(h - r + k)} 0 {f(h - r)}",
        f"l 0 {f(r)}", f"b 0 {f(r - k)} {f(r - k)} 0 {f(r)} 0"])


def speech_db(wav):
    """10 ms energy envelope (dB re peak) of a wav, for snapping captions to real speech onsets."""
    import wave
    import numpy as np
    w = wave.open(wav)
    sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
    x = np.frombuffer(w.readframes(w.getnframes()), {2: np.int16, 4: np.int32}[sw]).astype(float)
    x = x.reshape(-1, ch).mean(1)
    hop = sr // 100
    n = len(x) // hop
    env = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-9)
    return 20 * np.log10(env / env.max())


def snap(t, db, back=0.3, fwd=0.6):
    """Whisper puts a word that follows a pause too early (up to ~0.3 s). If t falls in silence, move it to
    the next speech onset; if t is mid-speech right after a gap, move it back to that onset."""
    i, n = int(round(t * 100)), len(db)
    loud = lambda k: 0 <= k < n and db[k] > -32 and all(db[min(n - 1, k + j)] > -38 for j in range(3))
    if i < n and db[i] < -40:
        for k in range(i, min(n, i + int(fwd * 100))):
            if loud(k):
                return k / 100
        return t
    for k in range(i, max(0, i - int(back * 100)), -1):
        if db[k - 1] < -40 and loud(k):
            return k / 100
    return t


def cmd_ass(a):
    words = [w for w in json.load(open(a.words, encoding="utf-8")) if w[0] >= a.start_after]
    fix = dict(kv.split("=", 1) for kv in filter(None, a.fix.split(",")))
    if a.chunks:
        lines = [l.strip() for l in open(a.chunks, encoding="utf-8") if l.strip()]
        chunks = chunk_given(words, lines)
    else:
        chunks = chunk_auto(words, fix, a.max_words)
    if a.snap:
        db = speech_db(a.snap)
        moved = 0
        for c in chunks:
            s0 = c[0][0]
            s1 = snap(s0, db)
            if abs(s1 - s0) >= 0.03:
                moved += 1
            c[0] = (s1, max(s1, c[0][1]), c[0][2])
        print(f"snapped {moved}/{len(chunks)} caption starts to speech onsets in {a.snap}")
    acc = {norm(w) for w in a.accent.split(",") if w}
    W, H = a.res.split("x")
    rounded = a.box and a.radius > 0
    if rounded:
        from PIL import ImageFont
        if not a.fontfile:
            sys.exit("--radius needs --fontfile (the .ttf of --font) to size each box")
        meas = ImageFont.truetype(a.fontfile, 200)
        scale = a.size / sum(meas.getmetrics())  # libass sizes a font by ascent + descent
        padx, pady = (float(v) for v in a.pad.split(","))
        cx, cy = (float(v) for v in a.pos.split(","))
        bh = a.box_height or a.size + 2 * pady
    end_all = a.end or chunks[-1][-1][1] + 0.35
    ev = []
    for k, c in enumerate(chunks):
        s = c[0][0]
        e = chunks[k + 1][0][0] if k + 1 < len(chunks) else end_all
        if e - c[-1][1] > 0.6:
            e = c[-1][1] + 0.35
        txt = " ".join(t for _, _, t in c)
        txt = txt.upper() if a.upper else txt
        plain = txt
        if acc:
            txt = " ".join(f"{{\\c{ass_col(a.accent_color)}}}{w}{{\\c{ass_col(a.color)}}}" if norm(w) in acc else w
                           for w in txt.split())
        if rounded:
            bw = meas.getlength(plain) * scale + 2 * padx
            ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\an7\\pos({cx - bw / 2:.1f},{cy - bh / 2:.1f})"
                      f"\\p1\\bord0\\shad0\\1c{ass_col(a.box)}\\1a&H{int((1 - a.box_alpha) * 255):02X}&}}"
                      f"{pill_path(bw, bh, a.radius)}")
        ev.append(f"Dialogue: 1,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\pos({a.pos})}}{txt}")
    if rounded:
        border, back, outline_col, a.outline, a.shadow = 1, ass_col("000000", 1), ass_col("000000", 1), 0, 0
    else:
        border, back = (3, ass_col(a.box, 1 - a.box_alpha)) if a.box else (1, ass_col("000000", 0.5))
        outline_col = ass_col(a.box, 1 - a.box_alpha) if a.box else ass_col(a.outline_color)
    hdr = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 2\n\n[V4+ Styles]\n"
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
           "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
           "MarginR, MarginV, Encoding\n"
           f"Style: Cap,{a.font},{a.size},{ass_col(a.color)},{ass_col(a.color)},{outline_col},{back},0,0,0,0,100,100,"
           f"{a.spacing},0,{border},{a.outline},{a.shadow},5,10,10,10,1\n\n[Events]\n"
           "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    open(a.out, "w", encoding="utf-8").write(hdr + "\n".join(ev) + "\n")
    for e in ev:
        if e.startswith("Dialogue: 1") or not rounded:
            print(e[12:34], re.sub(r"\{[^}]*\}", "", e.split(",,", 2)[2]))
    print(len(ev), "captions ->", a.out)


def fesc(p):
    return p.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def cmd_burn(a):
    ff = ffmpeg()
    inputs, chain, cur, n = ["-i", a.src], [], "[0:v]", 0
    for i, c in enumerate(a.cover):
        t, box, *mode = c.split(":")
        t0, t1 = t.split("-")
        x, y, w, h = box.split(",")
        en = f"between(t,{t0},{t1})"
        mode = mode[0] if mode else "delogo"
        if mode == "delogo":
            chain.append(f"{cur}delogo=x={x}:y={y}:w={w}:h={h}:enable='{en}'[c{i}]")
        elif mode == "blur":
            chain.append(f"{cur}split[m{i}][s{i}];[s{i}]crop={w}:{h}:{x}:{y},boxblur=20:3[b{i}];"
                         f"[m{i}][b{i}]overlay={x}:{y}:enable='{en}'[c{i}]")
        else:
            chain.append(f"{cur}drawbox=x={x}:y={y}:w={w}:h={h}:color=0x{mode}:t=fill:enable='{en}'[c{i}]")
        cur = f"[c{i}]"
    for i, o in enumerate(a.overlay):
        t, rest = o.split(":", 1)
        img, xy = rest.rsplit(":", 1)  # the image path may contain a drive colon
        t0, t1 = t.split("-")
        n += 1
        inputs += ["-loop", "1", "-i", img]
        x, y = xy.split(",")
        chain.append(f"{cur}[{n}:v]overlay={x}:{y}:shortest=1:enable='between(t,{t0},{t1})'[o{i}]")
        cur = f"[o{i}]"
    cwd = None
    if a.ass:
        cwd = os.path.dirname(os.path.abspath(a.ass))
        fd = f":fontsdir='{fesc(os.path.abspath(a.fontsdir))}'" if a.fontsdir else ":fontsdir=."
        chain.append(f"{cur}subtitles='{os.path.basename(a.ass)}'{fd}[vout]")
        cur = "[vout]"
    if cur == "[0:v]":
        chain.append("[0:v]null[vout]")
        cur = "[vout]"
    amap = ["-map", "0:a?", "-c:a", "aac", "-b:a", "192k"]
    if a.audio:
        inputs += ["-i", os.path.abspath(a.audio)]
        amap = ["-map", f"{n + 1}:a", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    inputs = [os.path.abspath(v) if k and inputs[k - 1] == "-i" else v for k, v in enumerate(inputs)]
    cmd = [ff, "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain), "-map", cur, *amap,
           "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           os.path.abspath(a.out)]
    subprocess.run(cmd, check=True, cwd=cwd)
    print("burned", a.out)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ass")
    p.add_argument("words"); p.add_argument("--out", required=True); p.add_argument("--chunks")
    p.add_argument("--max-words", type=int, default=3); p.add_argument("--res", default="720x1280")
    p.add_argument("--font", default="Montserrat ExtraBold"); p.add_argument("--size", type=int, default=37)
    p.add_argument("--color", default="FFFFFF"); p.add_argument("--outline", type=float, default=3)
    p.add_argument("--outline-color", default="000000"); p.add_argument("--shadow", type=float, default=1.5)
    p.add_argument("--spacing", type=float, default=0); p.add_argument("--pos", default="360,836")
    p.add_argument("--upper", action="store_true"); p.add_argument("--accent", default="")
    p.add_argument("--accent-color", default="B9B8F5"); p.add_argument("--box"); p.add_argument("--box-alpha", type=float, default=1.0)
    p.add_argument("--start-after", type=float, default=0.0); p.add_argument("--end", type=float)
    p.add_argument("--radius", type=float, default=0); p.add_argument("--pad", default="8,6")
    p.add_argument("--box-height", type=float); p.add_argument("--fontfile"); p.add_argument("--snap")
    p.add_argument("--fix", default=""); p.set_defaults(f=cmd_ass)
    p = sub.add_parser("burn")
    p.add_argument("src"); p.add_argument("--out", required=True); p.add_argument("--ass")
    p.add_argument("--cover", action="append", default=[]); p.add_argument("--overlay", action="append", default=[])
    p.add_argument("--audio"); p.add_argument("--fontsdir"); p.set_defaults(f=cmd_burn)
    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
