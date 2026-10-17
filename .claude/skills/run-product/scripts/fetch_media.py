#!/usr/bin/env python3
"""Download media byte-for-byte (raw originals) and optionally convert animated GIFs to animated WebP.

Files keep their original names with a numeric prefix (01-name.gif) to avoid clashes. Downloads use a
browser User-Agent and `Accept: */*` so the CDN returns the original format (no WebP/AVIF swap).
Already-downloaded URLs are skipped (tracked in <out>/_manifest.json). Raw GIFs are never modified;
WebP versions go to --webp-dir.

Kinds for --from-capture (capture.json written by capture_page.py):
  gifs, videos, product (product_images), sections (section_images), testimonials, other,
  images (= product + sections), all (= everything except other)

Usage:
  python -I fetch_media.py --out media --urls https://shop.com/cdn/shop/files/a.gif https://shop.com/b.png
  python -I fetch_media.py --out "02_competitor/media" --from-capture "02_competitor/page/capture.json" --kinds gifs --webp-dir "04_page-images"
  python -I fetch_media.py --out media --from-capture capture.json --kinds product,testimonials --by-kind
"""
import argparse
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image, ImageSequence

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0")
KINDS = {
    "gifs": ["gifs"], "videos": ["videos"], "product": ["product_images"], "product_images": ["product_images"],
    "sections": ["section_images"], "section_images": ["section_images"], "testimonials": ["testimonial_images"],
    "testimonial_images": ["testimonial_images"], "other": ["other_images"], "other_images": ["other_images"],
    "images": ["product_images", "section_images"],
    "all": ["product_images", "gifs", "videos", "section_images", "testimonial_images"],
}
SUBDIR = {"product_images": "product", "gifs": "gifs", "videos": "videos", "section_images": "sections",
          "testimonial_images": "testimonials", "other_images": "other", "urls": ""}
MAGIC = [(b"GIF8", ".gif"), (b"\x89PNG", ".png"), (b"\xff\xd8", ".jpg"), (b"RIFF", ".webp"), (b"\x1aE\xdf\xa3", ".webm")]


def ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def download(url, dest, timeout):
    tmp = dest.with_name(dest.name + ".part")
    headers = {"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout,
                                    context=ssl_context()) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f, 1 << 20)
    except urllib.error.URLError as e:
        if not (isinstance(getattr(e, "reason", None), ssl.SSLError) and shutil.which("curl")):
            raise
        r = subprocess.run(["curl", "-sSL", "--fail", "-m", str(timeout), "-A", UA, "-H", "Accept: */*",
                            "-o", str(tmp), url], capture_output=True, text=True)
        if r.returncode != 0:
            raise urllib.error.URLError(f"curl exit {r.returncode}: {r.stderr.strip()}")
    os.replace(tmp, dest)


def sniff(path):
    head = Path(path).read_bytes()[:12]
    if head[4:8] == b"ftyp":
        return ".avif" if b"avif" in head[8:12] else ".mp4"
    for sig, ext in MAGIC:
        if head.startswith(sig):
            return ext
    return None


def gif_to_webp(src, dst, quality):
    im = Image.open(src)
    n = getattr(im, "n_frames", 1)
    if n < 2:
        return None
    frames, durations = [], []
    for fr in ImageSequence.Iterator(im):
        d = fr.info.get("duration", im.info.get("duration", 100)) or 100
        durations.append(100 if d <= 10 else d)
        frames.append(fr.convert("RGBA" if "transparency" in fr.info else "RGB"))
    frames[0].save(dst, "WEBP", save_all=True, append_images=frames[1:], duration=durations, loop=0,
                   quality=quality, method=6, background=(0, 0, 0, 0))
    return n


def mb(n):
    return f"{n / 1048576:.1f} MB" if n >= 104858 else f"{n / 1024:.0f} KB"


def next_index(folder):
    nums = [int(m.group(1)) for f in folder.iterdir() if (m := re.match(r"(\d+)-", f.name))] if folder.exists() else []
    return max(nums, default=0) + 1


def load_jobs(args):
    if args.urls:
        return [("urls", u) for u in args.urls]
    cap = json.loads(Path(args.from_capture).read_text(encoding="utf-8"))
    media = cap.get("media", {})
    jobs, seen = [], set()
    for k in [k.strip() for k in args.kinds.split(",") if k.strip()]:
        if k not in KINDS:
            sys.exit(f"ERROR: unknown kind '{k}'. Use: {', '.join(KINDS)}")
        for key in KINDS[k]:
            for item in media.get(key, []):
                if item["url"] not in seen:
                    seen.add(item["url"])
                    jobs.append((key, item["url"]))
    return jobs


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="download directory")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--urls", nargs="+", help="URLs to download")
    src.add_argument("--from-capture", help="capture.json from capture_page.py")
    ap.add_argument("--kinds", default="gifs,images,videos", help="kinds to take from capture.json (default gifs,images,videos)")
    ap.add_argument("--by-kind", action="store_true", help="put each kind in its own subfolder (product/, gifs/, ...)")
    ap.add_argument("--webp-dir", help="convert every animated GIF to animated WebP into this folder")
    ap.add_argument("--webp-quality", type=int, default=62, help="WebP quality (default 62)")
    ap.add_argument("--force", action="store_true", help="re-download and re-convert even if present")
    ap.add_argument("--timeout", type=int, default=180, help="per-file timeout in seconds (default 180)")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    jobs = load_jobs(args)
    if not jobs:
        print("Nothing to download (no matching URLs).")
        return 1

    done, skipped, failed, files = 0, 0, [], []
    for kind, url in jobs:
        folder = out / SUBDIR.get(kind, "") if args.by_kind else out
        folder.mkdir(parents=True, exist_ok=True)
        prev = manifest.get(url)
        if prev and (out / prev).exists() and not args.force:
            skipped += 1
            files.append((kind, out / prev))
            print(f"skip  {prev}")
            continue
        name = unquote(os.path.basename(urlsplit(url).path)) or "file"
        dest = (out / prev) if prev else folder / f"{next_index(folder):02d}-{name}"
        try:
            download(url, dest, args.timeout)
        except (OSError, ValueError) as e:
            failed.append(url)
            print(f"FAIL  {url}  ({e})")
            continue
        real = sniff(dest)
        ext = dest.suffix.lower().replace(".jpeg", ".jpg")
        note = f"  WARNING: content is {real}" if real and ext and real != ext else ""
        manifest[url] = dest.relative_to(out).as_posix()
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        done += 1
        files.append((kind, dest))
        print(f"got   {manifest[url]}  {mb(dest.stat().st_size)}{note}")

    converted = []
    if args.webp_dir:
        wdir = Path(args.webp_dir)
        wdir.mkdir(parents=True, exist_ok=True)
        for _, f in files:
            if f.suffix.lower() != ".gif" or sniff(f) != ".gif":
                continue
            dst = wdir / (re.sub(r"^\d+-", "", f.stem) + ".webp")
            if dst.exists() and not args.force:
                print(f"skip  webp {dst.name} (exists)")
                converted.append((f, dst))
                continue
            try:
                n = gif_to_webp(f, dst, args.webp_quality)
            except (OSError, ValueError) as e:
                print(f"FAIL  webp {f.name} ({e})")
                failed.append(str(f))
                continue
            if n is None:
                print(f"skip  webp {f.name} (static GIF)")
                continue
            converted.append((f, dst))
            a, b = f.stat().st_size, dst.stat().st_size
            print(f"webp  {f.name} {mb(a)} -> {dst.name} {mb(b)}  ({n} frames, -{100 - b * 100 // a}%)")

    print(f"\nSummary: {done} downloaded, {skipped} skipped, {len(failed)} failed, {len(converted)} webp")
    print(f"Raw files in: {out.resolve()}")
    if args.webp_dir:
        print(f"WebP in    : {Path(args.webp_dir).resolve()}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
