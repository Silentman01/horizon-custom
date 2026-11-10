"""Square social logos + favicon from the brand logo files (local, no credits).

Usage:
  python -I brand_icons.py <logo.png> <logo-white.png> <brand_hex> <out_dir> <slug> [--glyph N]

Writes to out_dir:
  <slug>-social-square.png        1080x1080, white logo on the brand color (profile pictures)
  <slug>-social-square-light.png  1080x1080, dark logo on white
  <slug>-favicon.png              512x512, first glyph of the wordmark in white on the brand color, rounded square
  <slug>-favicon.ico              16/32/48 px
--glyph N uses the Nth glyph group instead of the first (glyphs are split on empty columns of the logo alpha).
Logos must be transparent PNGs (the branding step already makes them).
"""
import os, sys
from PIL import Image, ImageDraw


def trim(im):
    box = im.getchannel('A').getbbox()
    return im.crop(box) if box else im


def fit(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def square(logo, bg, size=1080, width_ratio=0.72):
    canvas = Image.new('RGBA', (size, size), bg)
    lg = fit(trim(logo), int(size * width_ratio), int(size * 0.5))
    canvas.alpha_composite(lg, ((size - lg.width) // 2, (size - lg.height) // 2))
    return canvas.convert('RGB')


def glyph(logo, n=0):
    lg = trim(logo)
    a = lg.getchannel('A')
    cols = [any(a.getpixel((x, y)) > 20 for y in range(0, a.height, 2)) for x in range(a.width)]
    runs, start = [], None
    for x, on in enumerate(cols + [False]):
        if on and start is None:
            start = x
        elif not on and start is not None:
            runs.append((start, x))
            start = None
    s, e = runs[min(n, len(runs) - 1)]
    return trim(lg.crop((s, 0, e, lg.height)))


def main():
    logo, white, bg, out, slug = sys.argv[1:6]
    n = int(sys.argv[sys.argv.index('--glyph') + 1]) if '--glyph' in sys.argv else 0
    os.makedirs(out, exist_ok=True)
    dark_im, white_im = Image.open(logo).convert('RGBA'), Image.open(white).convert('RGBA')
    square(white_im, bg).save(os.path.join(out, f'{slug}-social-square.png'))
    square(dark_im, '#FFFFFF').save(os.path.join(out, f'{slug}-social-square-light.png'))
    size = 512
    fav = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.22), fill=255)
    fav.paste(Image.new('RGBA', (size, size), bg), (0, 0), mask)
    g = fit(glyph(white_im, n), int(size * 0.6), int(size * 0.68))
    fav.alpha_composite(g, ((size - g.width) // 2, (size - g.height) // 2))
    fav.save(os.path.join(out, f'{slug}-favicon.png'))
    fav.save(os.path.join(out, f'{slug}-favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
    print('wrote', out)


if __name__ == '__main__':
    main()
