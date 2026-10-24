#!/usr/bin/env python3
"""Split a competitor video into clips: scene detection, one keyframe per clip, labelled contact sheet.

Writes into --out:
  cuts.json   [{"n": 1, "start": 0.0, "end": 2.4, "cls": "?"}, ...] plus "weak" cut candidates
              (scene score between --weak and --threshold: flashes and light leaks hide real cuts,
              so audit those times too)
  kf/cNN.png  middle frame of each clip (full resolution, for the competitor-trace audit)
  clips.jpg   contact sheet, header "NN start-end s (class)", red header for class c

Classes: a = clean, b = text overlay fixed locally, c = needs regeneration. After the audit,
re-run with --classes to redraw the sheet from the saved cuts.json (no new detection).

Usage:
  python -I video_clips.py SRC.mp4 --out WORK/clips
  python -I video_clips.py SRC.mp4 --out WORK/clips --classes "1-20=b,21=c" --sheet WORK/v01-clips.jpg
Options: --threshold 0.25  --weak 0.12  --min-len 0.12 (merge 1-3 frame splits)  --cols 8  --redetect
ffmpeg: $FFMPEG, PATH, or the imageio-ffmpeg package.
"""
import argparse, json, os, re, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont


def ffmpeg():
    p = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if p:
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def duration(ff, src):
    err = subprocess.run([ff, "-i", src], capture_output=True, text=True, errors="replace").stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def scene_times(ff, src, thr):
    vf = f"select='gt(scene,{thr})',metadata=print:file=-"
    out = subprocess.run([ff, "-v", "error", "-i", src, "-an", "-vf", vf, "-f", "null", "-"],
                         capture_output=True, text=True, errors="replace").stdout
    t = [float(x) for x in re.findall(r"pts_time:([\d.]+)", out)]
    sc = [float(x) for x in re.findall(r"lavfi.scene_score=([\d.]+)", out)]
    return list(zip(t, sc))


def font(size):
    for n in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            pass
    return ImageFont.load_default()


def parse_classes(spec, n):
    cls = {}
    for part in filter(None, (spec or "").split(",")):
        rng, c = part.split("=")
        a, _, b = rng.partition("-")
        for i in range(int(a), int(b or a) + 1):
            if 1 <= i <= n:
                cls[i] = c.strip()
    return cls


def sheet(clips, kfdir, path, cols):
    w = 240
    ims = [Image.open(os.path.join(kfdir, f"c{c['n']:02d}.png")).convert("RGB") for c in clips]
    h = int(w * ims[0].height / ims[0].width)
    rows = (len(clips) + cols - 1) // cols
    S = Image.new("RGB", (cols * w, rows * (h + 28)), "white")
    d, f = ImageDraw.Draw(S), font(15)
    for i, (c, im) in enumerate(zip(clips, ims)):
        x, y = (i % cols) * w, (i // cols) * (h + 28)
        S.paste(im.resize((w, h)), (x, y + 28))
        d.rectangle([x, y, x + w - 1, y + 27], fill=(200, 0, 0) if c["cls"] == "c" else (30, 30, 30))
        d.text((x + 5, y + 5), f"{c['n']:02d}  {c['start']:.2f}-{c['end']:.2f}s  ({c['cls']})", fill="white", font=f)
    S.save(path, quality=88)
    print("sheet", path)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--threshold", type=float, default=0.25)
    ap.add_argument("--weak", type=float, default=0.12)
    ap.add_argument("--min-len", type=float, default=0.12)
    ap.add_argument("--classes", default="")
    ap.add_argument("--sheet", help="contact sheet path (default OUT/clips.jpg)")
    ap.add_argument("--cols", type=int, default=8)
    ap.add_argument("--redetect", action="store_true")
    a = ap.parse_args()
    ff = ffmpeg()
    os.makedirs(os.path.join(a.out, "kf"), exist_ok=True)
    cj = os.path.join(a.out, "cuts.json")
    if os.path.exists(cj) and not a.redetect:
        data = json.load(open(cj, encoding="utf-8"))
    else:
        dur = duration(ff, a.src)
        hits = scene_times(ff, a.src, a.weak)
        cuts = [0.0]
        for t, s in hits:
            if s >= a.threshold and t - cuts[-1] >= a.min_len and dur - t >= a.min_len:
                cuts.append(round(t, 3))
        cuts.append(round(dur, 3))
        clips = [{"n": i + 1, "start": cuts[i], "end": cuts[i + 1], "cls": "?"} for i in range(len(cuts) - 1)]
        weak = [round(t, 3) for t, s in hits if s < a.threshold]
        data = {"src": os.path.abspath(a.src), "threshold": a.threshold, "clips": clips, "weak_cuts": weak}
        for c in clips:
            mid = (c["start"] + c["end"]) / 2
            subprocess.run([ff, "-v", "error", "-y", "-ss", f"{mid:.3f}", "-i", a.src, "-frames:v", "1",
                            os.path.join(a.out, "kf", f"c{c['n']:02d}.png")], check=True)
    for n, c in parse_classes(a.classes, len(data["clips"])).items():
        data["clips"][n - 1]["cls"] = c
    json.dump(data, open(cj, "w", encoding="utf-8"), indent=1)
    sheet(data["clips"], os.path.join(a.out, "kf"), a.sheet or os.path.join(a.out, "clips.jpg"), a.cols)
    for c in data["clips"]:
        print(f"{c['n']:02d} {c['start']:7.2f}-{c['end']:7.2f}  {c['cls']}")
    if data.get("weak_cuts"):
        print("weak cut candidates (audit these frames):", ", ".join(f"{t:.2f}" for t in data["weak_cuts"]))


if __name__ == "__main__":
    sys.exit(main())
