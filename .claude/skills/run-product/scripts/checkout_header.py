"""Render the checkout header image (logo + "trusted by" bar with customer faces + 3 trust points).

Mockup: templates/checkout-header-mockup.png (Aurea). Output is 1000x300 (and @2x) PNG for
Settings > Checkout > Customize > Header / Banner image.

Usage:
  python -I checkout_header.py config.json out.png [--preview-avatars]

config.json:
{
  "logo": "path/to/logo.png",                # dark logo on transparent or white
  "logo_height": 110,
  "font": "Instrument Sans",                 # Google font
  "bar_from": "#09184C", "bar_to": "#3D5AFE",  # bar gradient (left -> right)
  "bar_text": "MÁS DE 40,000 HOMBRES CONFÍAN EN NOSOTROS",
  "accent": "#3D5AFE",                       # bold words of the trust points
  "text": "#111111",
  "avatars": [{"src": "face.png", "cx": 0.5, "cy": 0.3, "size": 0.25}],  # crop center + side, fractions of the image
  "points": [["30 DÍAS", " DE GARANTÍA"], ["ENVÍO EN ", "24 HRS"], ["PAGO ", "SEGURO"]],
  "icons": ["guarantee", "truck", "lock"]    # optional, one per point: built-in name, inline "<svg…>" or null
}
In each point, items at even indexes are accent bold, odd ones plain: ["30 DAYS", " GUARANTEE"],
["", "SHIPS IN ", "24 HOURS"] (empty first item when the point starts plain). The bar text shrinks to fit;
the points shrink too if they collide.
Icons sit before the point text at text height, in "icon_color" (default accent). Built-ins: guarantee, truck,
lock, check. Inline SVGs should use stroke/fill="currentColor"; their width/height are overridden.
Save config.json as UTF-8 (a "£" read as "Â£" means it was saved in another encoding).
"""
import base64, io, json, os, re, sys
from PIL import Image

_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">%s</svg>'
ICONS = {
    'guarantee': _SVG % '<path d="M12 2.5 4 5.5v6c0 5 3.4 8.8 8 10 4.6-1.2 8-5 8-10v-6z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    'truck': _SVG % '<path d="M1.5 5h12v11h-12z"/><path d="M13.5 9h4.5l3.5 3.5V16h-8z"/><circle cx="6" cy="17.5" r="2" fill="#fff"/><circle cx="17.5" cy="17.5" r="2" fill="#fff"/>',
    'lock': _SVG % '<rect x="4.5" y="10.5" width="15" height="11" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/><path d="M12 15v2.5"/>',
    'check': _SVG % '<circle cx="12" cy="12" r="9.5"/><path d="m7.5 12 3 3 6-6"/>',
}


def icon_svg(v):
    if not v:
        return ''
    svg = v if v.lstrip().startswith('<svg') else ICONS[v]
    svg = re.sub(r'<svg[^>]*>', lambda m: re.sub(r'\s(width|height)="[^"]*"', '', m.group(0)), svg, count=1)
    return '<i class="ic">' + svg + '</i>'


def crop_avatar(a, px=200):
    im = Image.open(a['src']).convert('RGB')
    w, h = im.size
    side = a.get('size', 0.25) * min(w, h)
    cx, cy = a['cx'] * w, a['cy'] * h
    box = [int(cx - side / 2), int(cy - side / 2), int(cx + side / 2), int(cy + side / 2)]
    return im.crop(box).resize((px, px), Image.LANCZOS)


def b64(im, fmt='PNG'):
    buf = io.BytesIO()
    im.save(buf, fmt)
    return 'data:image/%s;base64,' % fmt.lower() + base64.b64encode(buf.getvalue()).decode()


def main():
    cfg = json.load(open(sys.argv[1], encoding='utf-8'))
    out = sys.argv[2]
    faces = [crop_avatar(a) for a in cfg['avatars']]
    if '--preview-avatars' in sys.argv:
        sheet = Image.new('RGB', (210 * len(faces), 210), 'white')
        for i, f in enumerate(faces):
            sheet.paste(f, (210 * i + 5, 5))
        sheet.save(out)
        return
    logo = Image.open(cfg['logo'])
    font = cfg.get('font', 'Inter')
    pts = ''
    icons = cfg.get('icons') or []
    for n, p in enumerate(cfg['points']):
        pts += '<span>' + icon_svg(icons[n] if n < len(icons) else None) + ''.join(
            ('<b>%s</b>' if i % 2 == 0 else '%s') % s for i, s in enumerate(p)) + '</span>'
    avs = ''.join('<img class="av" src="%s">' % b64(f, 'JPEG') for f in faces)
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@400;600;700;800&display=block" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1000px;height:300px;background:#fff;font-family:'{font}',sans-serif;color:{cfg.get('text', '#111')};overflow:hidden}}
.logo{{position:absolute;top:{cfg.get('logo_top', 16)}px;left:0;right:0;display:flex;justify-content:center}}
.logo img{{height:{cfg.get('logo_height', 110)}px;width:auto}}
.bar{{position:absolute;left:12px;right:12px;top:150px;height:97px;border-radius:49px;display:flex;align-items:center;gap:18px;padding-left:46px;
background:linear-gradient(90deg,{cfg['bar_from']},{cfg['bar_to']})}}
.avs{{display:flex;flex-shrink:0}}
.av{{width:74px;height:74px;border-radius:50%;border:3px solid #fff;object-fit:cover;margin-left:-22px}}
.av:first-child{{margin-left:0}}
.bt{{color:#fff;font-weight:600;font-size:{cfg.get('bar_size', 40)}px;letter-spacing:.01em;white-space:nowrap;text-transform:uppercase}}
.pts{{position:absolute;left:18px;right:18px;top:258px;display:flex;justify-content:space-between;font-size:{cfg.get('points_size', 21)}px;text-transform:uppercase;white-space:nowrap}}
.pts b{{color:{cfg['accent']};font-weight:800}}
.pts span{{display:inline-flex;align-items:center;white-space:pre}}
.ic{{display:inline-flex;color:{cfg.get('icon_color', cfg['accent'])};margin-right:.35em}}
.ic svg{{width:1.1em;height:1.1em;display:block}}
</style></head><body>
<div class="logo"><img src="{b64(logo)}"></div>
<div class="bar"><div class="avs">{avs}</div><div class="bt">{cfg['bar_text']}</div></div>
<div class="pts">{pts}</div>
</body></html>"""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for scale, path in ((1, out), (2, out.replace('.png', '@2x.png'))):
            pg = b.new_page(viewport={'width': 1000, 'height': 300}, device_scale_factor=scale)
            pg.set_content(html, wait_until='networkidle')
            pg.evaluate('document.fonts.ready')
            # shrink the bar text until it fits next to the faces
            pg.evaluate('''() => { const bar = document.querySelector('.bar'), t = document.querySelector('.bt');
              let s = parseFloat(getComputedStyle(t).fontSize);
              while (t.getBoundingClientRect().right > bar.getBoundingClientRect().right - 40 && s > 18) { s -= 1; t.style.fontSize = s + 'px'; }
              // shrink the points until they keep at least 24px between them
              const p = document.querySelector('.pts'), sp = [...p.children];
              let f = parseFloat(getComputedStyle(p).fontSize);
              const room = () => p.clientWidth - sp.reduce((a, e) => a + e.getBoundingClientRect().width, 0);
              while (room() < 24 * (sp.length - 1) && f > 12) { f -= 0.5; p.style.fontSize = f + 'px'; } }''')
            pg.screenshot(path=path)
        b.close()
    print('wrote', out)


if __name__ == '__main__':
    main()
