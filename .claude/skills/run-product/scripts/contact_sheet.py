#!/usr/bin/env python3
"""Tile images into one or more labelled contact sheets (aspect ratio kept) for quick review.

Accepts files, folders and glob patterns (expanded here, since Windows shells do not expand them).
Each cell gets a small black label box: file name + size, a 1-based index, or nothing.
When more images than --max-per-sheet are given, sheets are numbered: sheet_1.jpg, sheet_2.jpg ...

Usage:
  python -I contact_sheet.py "media/product/*.png" --out product-sheet.jpg
  python -I contact_sheet.py media/testimonials media/product --out review.jpg --cols 4 --cell 360 --labels index
  python -I contact_sheet.py "ads/*.jpg" --out ads.jpg --max-per-sheet 20 --cols 5
"""
import argparse
import glob
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

Image.MAX_IMAGE_PIXELS = None
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}


def expand(patterns):
    files = []
    for p in patterns:
        if os.path.isdir(p):
            hits = sorted(str(f) for f in Path(p).iterdir() if f.suffix.lower() in EXTS)
        else:
            hits = sorted(glob.glob(p)) or ([p] if os.path.isfile(p) else [])
        if not hits:
            print(f"WARNING: no match for {p}")
        files += [os.path.normpath(h) for h in hits if Path(h).suffix.lower() in EXTS and os.path.normpath(h) not in files]
    return files


def font(size):
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def label_box(draw, xy, text, fnt, max_w):
    while len(text) > 4 and draw.textlength(text, font=fnt) > max_w - 8:
        text = text.rstrip("…")[:-1] + "…"
    w = draw.textlength(text, font=fnt)
    x, y = xy
    draw.rectangle((x, y, x + w + 8, y + fnt.size + 6), fill=(0, 0, 0))
    draw.text((x + 4, y + 2), text, fill=(255, 255, 255), font=fnt)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+", help="image files, folders or glob patterns")
    ap.add_argument("--out", required=True, help="output sheet path (.jpg or .png)")
    ap.add_argument("--cols", type=int, default=5, help="columns (default 5)")
    ap.add_argument("--cell", type=int, default=300, help="cell size in px (default 300)")
    ap.add_argument("--labels", choices=("name", "index", "none"), default="name", help="label style (default name)")
    ap.add_argument("--max-per-sheet", type=int, default=15, help="images per sheet (default 15)")
    args = ap.parse_args()

    files = expand(args.images)
    if not files:
        print("ERROR: no images found", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cell, gap, cols = args.cell, 6, max(1, args.cols)
    fnt = font(max(11, cell // 24))
    per = max(1, args.max_per_sheet)
    n_sheets = math.ceil(len(files) / per)
    sheets, failed = [], []

    for s in range(n_sheets):
        batch = files[s * per:(s + 1) * per]
        c = min(cols, len(batch))
        rows = math.ceil(len(batch) / c)
        sheet = Image.new("RGB", (c * cell + (c + 1) * gap, rows * cell + (rows + 1) * gap), (235, 235, 235))
        draw = ImageDraw.Draw(sheet)
        for i, f in enumerate(batch):
            x = gap + (i % c) * (cell + gap)
            y = gap + (i // c) * (cell + gap)
            idx = s * per + i + 1
            try:
                with Image.open(f) as im:
                    w, h = im.size
                    im = ImageOps.exif_transpose(im.convert("RGBA"))
                    im.thumbnail((cell, cell), Image.LANCZOS)
                    tile = Image.new("RGB", (cell, cell), (255, 255, 255))
                    tile.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2), im)
                sheet.paste(tile, (x, y))
                text = f"{idx}. {Path(f).name} {w}x{h}" if args.labels == "name" else str(idx)
            except (OSError, ValueError) as e:
                failed.append(f)
                text = f"{idx}. {Path(f).name} UNREADABLE"
                print(f"WARNING: cannot read {f}: {e}")
            if args.labels != "none":
                label_box(draw, (x + 3, y + 3), text, fnt, cell - 6)
        path = out if n_sheets == 1 else out.with_name(f"{out.stem}_{s + 1}{out.suffix}")
        if path.suffix.lower() in (".jpg", ".jpeg"):
            sheet.save(path, quality=85)
        else:
            sheet.save(path)
        sheets.append(path)

    print(f"{len(files)} image(s) -> {len(sheets)} sheet(s)")
    if args.labels == "index":
        for i, f in enumerate(files, 1):
            print(f"  {i:>3}  {f}")
    for p in sheets:
        print(f"Sheet: {p.resolve()}")
    return 1 if failed and len(failed) == len(files) else 0


if __name__ == "__main__":
    sys.exit(main())
