#!/usr/bin/env python3
"""Remove burned-in subtitles with EAST text detection + LAMA inpainting (what VMAKE-style tools do).

The text is found per frame and the background behind it is reconstructed, so the footage stays
intact: no blur band, no dark bar, and nothing showing through. Pixel heuristics (bright + dark
outline) were tried first and were too brittle on washed-out or white backgrounds; EAST is a real
text detector and found the text on every frame of the sample where they failed.

  python -I video_desub.py SRC.mp4 --out clean.mp4 --band 0,400,360,128 \
      --skip 28.10-29.17 --skip 73.80-78.65

  --band X,Y,W,H  the zone the original captions live in. W and H are rounded down to a multiple
                  of 32 for the network, so give it a little slack. Find it with --profile.
  --skip T0-T1    ranges to leave alone: regenerated clips, an end card carrying our own text.
  --window 4      frames each side whose detections are merged in, so a caption the detector drops
                  on one frame is still covered (captions sit still for ~1-2 s).
  --pad 7         px added around each detected text box.
  --conf 0.30     EAST confidence floor. Lower it if faint captions survive.
  --east PATH     frozen_east_text_detection.pb (else $EAST_MODEL).
  --pill 16       captions sit on a solid white box (CapCut/TikTok style): also erase the box, growing
                  each text line up to 16 px to its edge. Without it the empty box stays behind and
                  smears white into the inpainted area.

  python -I video_desub.py SRC.mp4 --profile
      prints white, unsaturated pixels per row so the caption band shows up as a spike.

Pass 1 detects (stores boxes only), pass 2 inpaints and encodes at CRF 16. Audio is dropped: the
remake supplies its own mix. Needs torch + CUDA, simple-lama-inpainting, and the EAST model.
"""
import argparse, os, shutil, subprocess, sys

import cv2
import numpy as np

LAYERS = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]


def ffmpeg():
    p = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if p:
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def east_boxes(net, img, conf_t):
    """Axis-aligned boxes around every text region EAST finds in img."""
    H, W = img.shape[:2]
    nW, nH = max(32, (W // 32) * 32), max(32, (H // 32) * 32)
    rW, rH = W / nW, H / nH
    blob = cv2.dnn.blobFromImage(img, 1.0, (nW, nH), (123.68, 116.78, 103.94), True, False)
    net.setInput(blob)
    scores, geo = net.forward(LAYERS)
    rects, confs = [], []
    for y in range(scores.shape[2]):
        s, x0, x1, x2, x3, ang = (scores[0, 0, y], geo[0, 0, y], geo[0, 1, y],
                                  geo[0, 2, y], geo[0, 3, y], geo[0, 4, y])
        for x in range(scores.shape[3]):
            if s[x] < conf_t:
                continue
            ox, oy = x * 4.0, y * 4.0
            cos, sin = np.cos(ang[x]), np.sin(ang[x])
            h, w = x0[x] + x2[x], x1[x] + x3[x]
            ex = ox + cos * x1[x] + sin * x2[x]
            ey = oy - sin * x1[x] + cos * x2[x]
            rects.append((int((ex - w) * rW), int((ey - h) * rH), int(w * rW), int(h * rH)))
            confs.append(float(s[x]))
    if not rects:
        return []
    idx = cv2.dnn.NMSBoxes(rects, confs, conf_t, 0.3)
    return [rects[i] for i in np.array(idx).flatten()] if len(idx) else []


def pill_boxes(img, boxes, grow):
    """Grow each caption line to the solid box (CapCut/TikTok pill) it sits in.

    EAST finds only the letters, so LAMA would erase the text and leave the empty box behind, and the
    box then bleeds into the inpainted area as a white smear. Each line's text rectangle is pushed out
    side by side while the next pixel column/row is still mostly box-coloured (near white), at most
    `grow` px, so a white background cannot run away with it."""
    if not boxes:
        return boxes
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    s = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1]
    white = (g > 200) & (s < 45)
    H, W = g.shape
    lines = []
    for b in sorted(boxes, key=lambda b: b[1] + b[3] / 2):
        cy = b[1] + b[3] / 2
        if lines and abs(lines[-1][0] - cy) < 8:
            lines[-1][1].append(b)
        else:
            lines.append([cy, [b]])
    out = list(boxes)
    for _, bs in lines:
        x0 = min(b[0] for b in bs); y0 = min(b[1] for b in bs)
        x1 = max(b[0] + b[2] for b in bs); y1 = max(b[1] + b[3] for b in bs)
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        tx0, ty0, tx1, ty1 = x0, y0, x1, y1
        for _ in range(grow):
            if x0 > 0 and white[y0:y1, x0 - 1].mean() > 0.5: x0 -= 1
            else: break
        for _ in range(grow):
            if x1 < W and white[y0:y1, x1].mean() > 0.5: x1 += 1
            else: break
        for _ in range(grow):
            if y0 > 0 and white[y0 - 1, x0:x1].mean() > 0.5: y0 -= 1
            else: break
        for _ in range(grow):
            if y1 < H and white[y1, x0:x1].mean() > 0.5: y1 += 1
            else: break
        # an anti-aliased or slightly grey box edge stops the growth a row short and leaves a thin
        # white line, so always reach at least a box's usual padding past the text
        m = max(6, grow // 2)
        x0, y0 = min(x0, tx0 - m), min(y0, ty0 - m)
        x1, y1 = max(x1, tx1 + m), max(y1, ty1 + m)
        out.append((x0 - 2, y0 - 2, x1 - x0 + 4, y1 - y0 + 4))
    return out


def cmd_profile(a):
    cap = cv2.VideoCapture(a.src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    dur = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    rows, n, t = np.zeros(H), 0, 0.5
    while t < dur:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
        ok, f = cap.read()
        if ok:
            n += 1
            g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
            rows += ((g > 215) & (hsv[:, :, 1] < 40)).sum(axis=1)
        t += max(0.5, dur / 60)
    cap.release()
    rows /= max(n, 1)
    print(f"white/unsaturated pixels per row over {n} frames (caption band = the spike):")
    for y in range(0, H, 10):
        v = rows[y:y + 10].mean()
        print(f"  y={y:4d} {v:6.1f} {'#' * int(v / 2)}")


def cmd_run(a):
    import torch
    from PIL import Image
    from simple_lama_inpainting import SimpleLama

    model = a.east or os.environ.get("EAST_MODEL")
    if not model or not os.path.exists(model):
        sys.exit("EAST model not found: pass --east PATH or set $EAST_MODEL")
    net = cv2.dnn.readNet(model)

    bx, by, bw, bh = (int(v) for v in a.band.split(","))
    skips = [tuple(float(x) for x in s.split("-")) for s in a.skip]

    cap = cv2.VideoCapture(a.src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"{W}x{H} {fps:.2f} fps {total} frames | band {bx},{by} {bw}x{bh} | skip {skips or 'none'}")

    per_frame, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        t = i / fps
        if any(s <= t <= e for s, e in skips):
            per_frame.append([])
        else:
            crop = f[by:by + bh, bx:bx + bw]
            boxes = east_boxes(net, crop, a.conf)
            per_frame.append(pill_boxes(crop, boxes, a.pill) if a.pill else boxes)
        i += 1
        if i % 200 == 0:
            print(f"  detect {i}/{total}", flush=True)
    cap.release()
    print(f"text found on {sum(1 for b in per_frame if b)}/{len(per_frame)} frames")

    masks = []
    for k in range(len(per_frame)):
        if any(s <= k / fps <= e for s, e in skips):
            masks.append(None)
            continue
        m, hit = np.zeros((bh, bw), np.uint8), False
        for j in range(max(0, k - a.window), min(len(per_frame), k + a.window + 1)):
            for (x, y, w, h) in per_frame[j]:
                hit = True
                cv2.rectangle(m, (max(0, x - a.pad), max(0, y - a.pad)),
                              (min(bw, x + w + a.pad), min(bh, y + h + a.pad)), 255, -1)
        masks.append(m if hit else None)
    print(f"after temporal merge: {sum(m is not None for m in masks)} frames to inpaint")

    lama = SimpleLama(device=torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    print("LAMA on", "cuda" if torch.cuda.is_available() else "cpu")

    ff = ffmpeg()
    tmp = os.path.join(os.path.dirname(os.path.abspath(a.out)), "_desub_tmp.mp4")
    enc = subprocess.Popen(
        [ff, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
         "-r", f"{fps}", "-i", "-", "-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
         "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)

    cap = cv2.VideoCapture(a.src)
    i = painted = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        m = masks[i] if i < len(masks) else None
        if m is not None:
            band = f[by:by + bh, bx:bx + bw]
            res = lama(Image.fromarray(cv2.cvtColor(band, cv2.COLOR_BGR2RGB)), Image.fromarray(m))
            f[by:by + bh, bx:bx + bw] = cv2.cvtColor(np.array(res.convert("RGB"))[:bh, :bw],
                                                     cv2.COLOR_RGB2BGR)
            painted += 1
        enc.stdin.write(f.tobytes())
        i += 1
        if i % 200 == 0:
            print(f"  inpaint {i}/{total} ({painted} painted)", flush=True)

    cap.release()
    enc.stdin.close()
    enc.wait()
    shutil.move(tmp, a.out)
    print(f"{a.out}: {painted} frames inpainted of {i}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--out")
    ap.add_argument("--band")
    ap.add_argument("--skip", action="append", default=[])
    ap.add_argument("--window", type=int, default=4)
    ap.add_argument("--pad", type=int, default=7)
    ap.add_argument("--conf", type=float, default=0.30)
    ap.add_argument("--east")
    ap.add_argument("--pill", type=int, default=0,
                    help="captions on a solid box: grow each text line up to N px to the box edge (0 = text only)")
    ap.add_argument("--profile", action="store_true")
    a = ap.parse_args()
    if a.profile:
        return cmd_profile(a)
    if not (a.out and a.band):
        sys.exit("--out and --band are required (or pass --profile to find the band)")
    return cmd_run(a)


if __name__ == "__main__":
    sys.exit(main())
