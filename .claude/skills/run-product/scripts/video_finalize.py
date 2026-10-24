#!/usr/bin/env python3
"""Finish a video remake: cut in regenerated clips, encode without metadata, frame strip, clean up.

  render BASE.mp4 --out vNN-<slug>.mp4 [--insert T0-T1=CLIP.mp4@OFFSET]... [--audio mix.wav] [--crf 18]
      --insert replaces BASE video between T0 and T1 with CLIP from OFFSET (scaled/cropped to BASE size,
      BASE fps). The BASE audio is kept unless --audio is given. The output carries no metadata
      (-map_metadata -1, bitexact) and is checked: duration, size, tags.
  frames VIDEO --out strip.jpg [--every 0.5] [--cols 10] [--width 180]
      one frame every 0.5 s with its timestamp, for the independent check (several sheets if long).
      Write it to a scratch folder: it is not kept in vNN-work/.
  clean VIDEOS_DIR [--yes]
      enforces the folder rule: VIDEOS_DIR root keeps only final vNN-<slug>.mp4 files and vNN-work/
      folders; vNN-PLAN.md / vNN-clips.jpg / vNN-draft.mp4 found at the root move into vNN-work/;
      everything else in vNN-work/ (and stray root files) is deleted. Dry run unless --yes.
ffmpeg: $FFMPEG, PATH or imageio-ffmpeg.
"""
import argparse, os, re, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

KEEP = ("-clips.jpg", "-draft.mp4", "-PLAN.md")
STD = ("major_brand", "minor_version", "compatible_brands", "encoder")  # standard muxer tags


def ffmpeg():
    p = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if p:
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


FF = ffmpeg()


def probe(p):
    err = subprocess.run([FF, "-i", p], capture_output=True, text=True, errors="replace").stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    w, hh = re.search(r"Video:.*?, (\d{2,5})x(\d{2,5})", err).groups()
    fps = re.search(r"([\d.]+) fps", err)
    tags = [l.strip() for l in err.split("Metadata:", 1)[1].split("Duration:", 1)[0].splitlines() if ":" in l and not l.strip().startswith(STD)] \
        if "Metadata:" in err.split("Duration:", 1)[0] else []
    return {"dur": int(h) * 3600 + int(m) * 60 + float(s), "w": int(w), "h": int(hh),
            "fps": float(fps.group(1)) if fps else 30.0, "tags": tags}


def cmd_render(a):
    b = probe(a.base)
    inputs, chain, cur = ["-i", a.base], [], "[0:v]"
    for i, ins in enumerate(a.insert, 1):
        span, clip = ins.split("=", 1)
        clip, _, off = clip.rpartition("@") if "@" in clip else (clip, "", "0")
        t0, t1 = (float(v) for v in span.split("-"))
        inputs += ["-i", clip]
        chain.append(f"[{i}:v]trim=start={off}:duration={t1 - t0:.3f},setpts=PTS-STARTPTS+{t0}/TB,fps={b['fps']},"
                     f"scale={b['w']}:{b['h']}:force_original_aspect_ratio=increase,crop={b['w']}:{b['h']},setsar=1[g{i}];"
                     f"{cur}[g{i}]overlay=0:0:eof_action=pass:enable='between(t,{t0},{t1})'[v{i}]")
        cur = f"[v{i}]"
    if not chain:
        chain.append("[0:v]null[v0]")
        cur = "[v0]"
    amap = ["-map", "0:a?"]
    if a.audio:
        inputs += ["-i", a.audio]
        amap = ["-map", f"{len(a.insert) + 1}:a"]
    subprocess.run([FF, "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain), "-map", cur, *amap,
                    "-t", f"{b['dur']:.3f}", "-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-map_metadata", "-1", "-map_chapters", "-1", "-fflags", "+bitexact", "-flags:v", "+bitexact",
                    "-flags:a", "+bitexact", "-movflags", "+faststart", a.out], check=True)
    o = probe(a.out)
    print(f"{a.out}: {o['w']}x{o['h']} {o['fps']} fps {o['dur']:.2f} s (base {b['dur']:.2f} s), tags: {o['tags'] or 'none'}")


def cmd_frames(a):
    d = probe(a.video)["dur"]
    times = [round(i * a.every, 2) for i in range(int(d / a.every) + 1)]
    try:
        f = ImageFont.truetype("arialbd.ttf", 14)
    except OSError:
        f = ImageFont.load_default()
    per = a.cols * a.rows
    for s in range(0, len(times), per):
        cells = []
        for t in times[s:s + per]:
            png = subprocess.run([FF, "-v", "error", "-ss", f"{t:.2f}", "-i", a.video, "-frames:v", "1",
                                  "-vf", f"scale={a.width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                                 capture_output=True).stdout
            if png:
                from io import BytesIO
                cells.append((t, Image.open(BytesIO(png)).convert("RGB")))
        w, h = cells[0][1].size
        rows = (len(cells) + a.cols - 1) // a.cols
        S = Image.new("RGB", (a.cols * w, rows * h), "black")
        dr = ImageDraw.Draw(S)
        for k, (t, im) in enumerate(cells):
            x, y = (k % a.cols) * w, (k // a.cols) * h
            S.paste(im, (x, y))
            dr.rectangle([x, y, x + 52, y + 18], fill="black")
            dr.text((x + 3, y + 2), f"{t:.1f}s", fill="white", font=f)
        out = a.out if len(times) <= per else a.out.replace(".jpg", f"_{s // per + 1}.jpg")
        S.save(out, quality=85)
        print("frames", out)


def cmd_clean(a):
    root = a.dir
    acts = []
    for f in sorted(os.listdir(root)):
        p = os.path.join(root, f)
        m = re.match(r"(v\d+)-", f)
        if os.path.isdir(p):
            if re.fullmatch(r"v\d+-work", f):
                for g in sorted(os.listdir(p)):
                    if not (g.startswith(f[:-5]) and g.endswith(KEEP)):
                        acts.append(("delete", os.path.join(p, g)))
            else:
                acts.append(("delete", p))
        elif m and f.endswith(KEEP):
            acts.append(("move", p, os.path.join(root, m.group(1) + "-work", f)))
        elif not (m and f.endswith(".mp4")):
            acts.append(("delete", p))
    for act in acts:
        print(("" if a.yes else "[dry run] ") + " ".join(act))
        if not a.yes:
            continue
        if act[0] == "move":
            os.makedirs(os.path.dirname(act[2]), exist_ok=True)
            shutil.move(act[1], act[2])
        elif os.path.isdir(act[1]):
            shutil.rmtree(act[1])
        else:
            os.remove(act[1])
    print(f"{len(acts)} action(s)" + ("" if a.yes else ", re-run with --yes to apply"))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("render"); p.add_argument("base"); p.add_argument("--out", required=True)
    p.add_argument("--insert", action="append", default=[]); p.add_argument("--audio")
    p.add_argument("--crf", type=int, default=18); p.set_defaults(f=cmd_render)
    p = sub.add_parser("frames"); p.add_argument("video"); p.add_argument("--out", required=True)
    p.add_argument("--every", type=float, default=0.5); p.add_argument("--cols", type=int, default=10)
    p.add_argument("--rows", type=int, default=6); p.add_argument("--width", type=int, default=180)
    p.set_defaults(f=cmd_frames)
    p = sub.add_parser("clean"); p.add_argument("dir"); p.add_argument("--yes", action="store_true")
    p.set_defaults(f=cmd_clean)
    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
