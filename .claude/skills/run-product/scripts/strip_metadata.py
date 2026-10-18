"""Strip metadata from generated images and videos before they are saved as final.

Usage: python -I strip_metadata.py <file-or-folder> [...] [--inplace | --out DIR]

Images (png/jpg/jpeg/webp): pixels are re-encoded with Pillow, dropping EXIF, XMP,
IPTC, PNG text chunks and embedded provenance manifests (C2PA/JUMBF). The sRGB ICC
profile is kept so colours don't shift.
Videos (mp4/mov/webm): remuxed with ffmpeg without re-encoding: global and stream
metadata, chapters and extra boxes are dropped (-map_metadata -1, bitexact).
ffmpeg is taken from PATH, or the ffmpeg-static package if FFMPEG is set to its path.
"""
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

IMG = {".png", ".jpg", ".jpeg", ".webp"}
VID = {".mp4", ".mov", ".m4v", ".webm"}


def strip_image(src, dst):
    with Image.open(src) as im:
        im.load()
        icc = im.info.get("icc_profile")
        fmt = (im.format or os.path.splitext(dst)[1].lstrip(".")).upper()
        clean = im.convert("RGBA") if im.mode == "P" else im.copy()
        clean.info = {}
        kw = {"icc_profile": icc} if icc else {}
        if fmt in ("JPEG", "JPG"):
            if clean.mode not in ("RGB", "L"):
                clean = clean.convert("RGB")
            clean.save(dst, "JPEG", quality=95, optimize=True, **kw)
        elif fmt == "WEBP":
            clean.save(dst, "WEBP", quality=92, method=6, **kw)
        else:
            clean.save(dst, "PNG", optimize=True, **kw)


def strip_video(src, dst):
    ff = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
    cmd = [ff, "-v", "error", "-y", "-i", src, "-map", "0", "-c", "copy",
           "-map_metadata", "-1", "-map_chapters", "-1", "-fflags", "+bitexact",
           "-flags:v", "+bitexact", "-flags:a", "+bitexact"]
    if dst.lower().endswith((".mp4", ".mov", ".m4v")):
        cmd += ["-movflags", "+faststart"]
    subprocess.run(cmd + [dst], check=True)


def process(path, out_dir, inplace):
    ext = os.path.splitext(path)[1].lower()
    if ext not in IMG | VID:
        return False
    if inplace:
        fd, tmp = tempfile.mkstemp(suffix=ext, dir=os.path.dirname(path) or ".")
        os.close(fd)
        (strip_image if ext in IMG else strip_video)(path, tmp)
        os.replace(tmp, path)
        dst = path
    else:
        os.makedirs(out_dir, exist_ok=True)
        dst = os.path.join(out_dir, os.path.basename(path))
        (strip_image if ext in IMG else strip_video)(path, dst)
    print("clean", dst)
    return True


def main(argv):
    inplace = "--inplace" in argv
    out_dir = None
    if "--out" in argv:
        out_dir = argv[argv.index("--out") + 1]
    targets = [a for a in argv if not a.startswith("--") and a != out_dir]
    if not targets or (not inplace and not out_dir):
        print(__doc__)
        return 2
    n = 0
    for t in targets:
        if os.path.isdir(t):
            for dp, _, fs in os.walk(t):
                for f in fs:
                    n += process(os.path.join(dp, f), out_dir, inplace)
        else:
            n += process(t, out_dir, inplace)
    print(f"{n} file(s) cleaned")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
