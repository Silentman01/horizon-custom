"""Build an original vertical video ad from our OWN stills + our OWN voiceover.

No competitor footage, audio or voice is used anywhere in this pipeline - see
VIDEO_AD_POLICY.md next to this script.

Inputs
------
  shots.json   [{"img": <path|"ENDCARD">, "start": s, "end": s,
                 "mode": "fill"|"fit", "motion": "in"|"out"|"left"|"right"|"up"|"down"|"none"}]
  words.json   from video_eleven.py tts  (word-level timings of OUR voiceover)
  vo.mp3       the voiceover itself

Output
------
  a 1080x1920 H.264 mp4, voice normalised to -14 LUFS / -1 dBTP, word-by-word
  burned-in captions, and all metadata stripped.

Steps (each can be run alone):  clips | captions | assemble | all
Usage:  python -I video_build_stills.py all --dir <workdir> --out <final.mp4>
"""
import argparse
import json
import os
import subprocess
import sys

W, H = 1080, 1920
SS, SH = W * 2, H * 2          # supersample for smooth zoompan
FPS = 30
FONTSDIR = "C:/Windows/Fonts"
FONTNAME = "Arial"

# caption styling
CAP_FONTSIZE = 76
CAP_MARGINV = 300
CAP_MARGINH = 110
CAP_IDLE = "&H00FFFFFF"        # white (ASS is &HAABBGGRR)
CAP_ACTIVE = "&H007EC8E8"      # warm gold #E8C87E -> BGR 7EC8E8
WORDS_PER_LINE = 3


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def run(cmd, quiet=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.stderr.write(" ".join(str(c) for c in cmd[:14]) + " ...\n")
        sys.stderr.write((r.stderr or "")[-3500:] + "\n")
        raise SystemExit("ffmpeg failed (%d)" % r.returncode)
    return r


def motion_filter(motion, frames):
    """zoompan expressions for a Ken Burns move. 'on' is the output frame index."""
    n = max(frames - 1, 1)
    if motion == "in":
        z = "1+0.12*on/%d" % n
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif motion == "out":
        z = "1.12-0.12*on/%d" % n
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif motion in ("left", "right"):
        z = "1.10"
        span = "(iw-iw/zoom)"
        frac = "on/%d" % n if motion == "right" else "(1-on/%d)" % n
        x, y = "%s*%s" % (span, frac), "ih/2-(ih/zoom/2)"
    elif motion in ("up", "down"):
        z = "1.10"
        span = "(ih-ih/zoom)"
        frac = "on/%d" % n if motion == "down" else "(1-on/%d)" % n
        x, y = "iw/2-(iw/zoom/2)", "%s*%s" % (span, frac)
    else:
        z = "1.001"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    return ("zoompan=z='%s':x='%s':y='%s':d=%d:s=%dx%d:fps=%d"
            % (z, x, y, frames, W, H, FPS))


def build_clip(img, dur, mode, motion, out):
    frames = max(int(round(dur * FPS)), 2)
    if mode == "fit":
        # square / landscape art: keep the whole frame, fill the rest with a
        # darkened blur of itself rather than flat bars.
        vf = ("[0:v]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,"
              "boxblur=60:3,eq=brightness=-0.30:saturation=0.7[bg];"
              "[0:v]scale=%d:%d:force_original_aspect_ratio=decrease[fg];"
              "[bg][fg]overlay=(W-w)/2:(H-h)/2,%s,setsar=1"
              % (SS, SH, SS, SH, SS, SH, motion_filter(motion, frames)))
    else:
        vf = ("[0:v]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,%s,setsar=1"
              % (SS, SH, SS, SH, motion_filter(motion, frames)))
    run([ffmpeg(), "-y", "-loop", "1", "-i", img, "-filter_complex", vf,
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium",
         "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), out])


def ass_time(t):
    t = max(t, 0)
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def esc(s):
    return s.replace("{", "(").replace("}", ")")


def build_ass(words, path, total):
    """Word-by-word captions: a 3-word line at a time, active word highlighted."""
    groups = [words[i:i + WORDS_PER_LINE] for i in range(0, len(words), WORDS_PER_LINE)]
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,%s,%d,%s,&H00000000,&H80000000,1,0,1,7,3,2,%d,%d,%d,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (W, H, FONTNAME, CAP_FONTSIZE, CAP_IDLE, CAP_MARGINH, CAP_MARGINH, CAP_MARGINV)
    lines = []
    for gi, g in enumerate(groups):
        nxt = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else total
        for wi, w in enumerate(g):
            start = w["start"]
            end = g[wi + 1]["start"] if wi + 1 < len(g) else nxt
            if end - start < 0.02:
                continue
            parts = []
            for k, ww in enumerate(g):
                txt = esc(ww["word"].upper())
                if k == wi:
                    parts.append("{\\c%s}%s{\\c%s}" % (CAP_ACTIVE, txt, CAP_IDLE))
                else:
                    parts.append(txt)
            lines.append("Dialogue: 0,%s,%s,Cap,,0,0,0,,%s"
                         % (ass_time(start), ass_time(end), " ".join(parts)))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(head + "\n".join(lines) + "\n")
    return len(lines)


def cmd_clips(args):
    shots = json.load(open(os.path.join(args.dir, "shots.json"), encoding="utf-8"))
    cdir = os.path.join(args.dir, "clips")
    os.makedirs(cdir, exist_ok=True)
    listing = []
    for i, s in enumerate(shots):
        out = os.path.join(cdir, "c%02d.mp4" % i)
        dur = s["end"] - s["start"]
        build_clip(s["img"], dur, s.get("mode", "fill"), s.get("motion", "in"), out)
        print("  c%02d  %5.2fs  %-9s %-5s %s" % (i, dur, s.get("motion"), s.get("mode"), os.path.basename(s["img"])))
        listing.append("file '%s'" % out.replace("\\", "/"))
    with open(os.path.join(args.dir, "concat.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(listing) + "\n")
    print("%d clips -> %s" % (len(shots), cdir))


def cmd_captions(args):
    data = json.load(open(os.path.join(args.dir, "vo-words.json"), encoding="utf-8"))
    words = data["words"]
    total = words[-1]["end"] + 0.4
    n = build_ass(words, os.path.join(args.dir, "captions.ass"), total)
    print("%d caption events (%d words) -> captions.ass" % (n, len(words)))


def cmd_assemble(args):
    d = args.dir
    silent = os.path.join(d, "silent.mp4")
    run([ffmpeg(), "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(d, "concat.txt"),
         "-c", "copy", silent])
    # inside a filter argument every ':' and '\' must be escaped, on both paths
    fesc = lambda p: os.path.abspath(p).replace("\\", "/").replace(":", "\\:")
    vf = "subtitles='%s':fontsdir='%s'" % (fesc(os.path.join(d, "captions.ass")), fesc(FONTSDIR))
    af = "loudnorm=I=-14:TP=-1:LRA=11"
    run([ffmpeg(), "-y", "-i", silent, "-i", os.path.join(d, "vo.mp3"),
         "-vf", vf, "-af", af,
         "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
         "-movflags", "+faststart",
         "-map_metadata", "-1", "-map_chapters", "-1",
         "-metadata", "encoder=", args.out])
    print("-> %s" % args.out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["clips", "captions", "assemble", "all"])
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.step in ("clips", "all"):
        cmd_clips(a)
    if a.step in ("captions", "all"):
        cmd_captions(a)
    if a.step in ("assemble", "all"):
        if not a.out:
            raise SystemExit("--out required")
        cmd_assemble(a)


if __name__ == "__main__":
    main()
