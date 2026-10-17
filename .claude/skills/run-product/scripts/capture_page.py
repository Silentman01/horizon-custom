#!/usr/bin/env python3
"""Capture a competitor product page: product data, copy, palette, fonts, apps/offers, media, skeleton.

Fetches the Shopify product JSON (<product_url>.json) and the page HTML with a browser User-Agent,
then extracts everything needed to analyse and clone the page. Non-Shopify pages still work:
the JSON step is skipped and product data falls back to ld+json / Open Graph tags.

Outputs written to --out:
  p.json        raw Shopify product JSON (only when available)
  p.html        raw page HTML
  copy.txt      readable copy of <main>, deduplicated, with word count
  capture.json  everything extracted (machine-readable; input of fetch_media.py --from-capture)
  capture.md    the same, human-readable

Usage:
  python -I capture_page.py https://plaims.com/products/plaims-headlight-glasses --out "G:/Ecom/Products/Noxis/02_competitor/page"
  python -I capture_page.py URL --out DIR --html-file saved.html   # analyse HTML saved from a real browser (bot-protected shop)
  python -I capture_page.py URL --out DIR --no-json                # skip the .json request
"""
import argparse
import datetime
import gzip
import html as H
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zlib
from collections import Counter, OrderedDict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0")

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
VIDEO_EXT = {".mp4", ".webm", ".mov", ".m3u8", ".m4v"}
GENERIC_FONTS = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "inherit", "initial",
                 "unset", "-apple-system", "blinkmacsystemfont", "ui-sans-serif", "ui-serif", "ui-monospace",
                 "emoji", "math", "fangsong", "revert"}
ICON_FONT_RE = re.compile(r"icon|star|awesome|glyph|jdgm|judgeme|swiper|slick|loox|okendo|yotpo|kaching", re.I)
APP_VAR_RE = re.compile(r"^(jdgm|judgeme|kaching|kc-|loox|okendo|oke-|yotpo|stamped|payment-terms|shopify-account|"
                        r"rebuy|upcart|klaviyo|vitals|ali-?reviews|trustoo|ryviu|pf-|gp-)", re.I)
COLOR_NAME_RE = re.compile(r"colou?r|background|foreground|\bbg\b|-bg|bg-|accent|button|border|link|badge|text|"
                           r"shadow|gradient|primary|secondary|brand|star|highlight|surface", re.I)

APP_SIGNATURES = OrderedDict([
    ("Kaching Bundles", r"kaching-bundles|kachingbundles"),
    ("Kaching Cart", r"kaching-cart|kachingcart"),
    ("Judge.me Reviews", r"judge\.me|judgeme|jdgm-"),
    ("Loox Reviews", r"loox\.io|loox-"),
    ("Okendo Reviews", r"okendo"),
    ("Yotpo", r"yotpo"),
    ("Stamped.io", r"stamped\.io"),
    ("Reviews.io", r"reviews\.io|reviewsio"),
    ("Ali Reviews", r"alireviews|ali-reviews"),
    ("Trustoo", r"trustoo"),
    ("Ryviu", r"ryviu"),
    ("ReConvert", r"reconvert|stilyoapps"),
    ("Rebuy", r"rebuyengine|rebuy-widget|window\.Rebuy"),
    ("UpCart", r"upcart-|upcartapp|aftersell"),
    ("Monster Cart Upsell", r"monster-?cart|monsterapps"),
    ("Selleasy", r"selleasy"),
    ("Fast Bundle", r"fastbundle|fast-bundle"),
    ("Vitals", r"vitals\.app|vitalsapp|vitals-"),
    ("Klaviyo", r"klaviyo"),
    ("Omnisend", r"omnisend"),
    ("Privy", r"privy\.com"),
    ("Attentive", r"attn\.tv|attentivemobile"),
    ("Postscript", r"postscript\.io"),
    ("PageFly", r"pagefly"),
    ("GemPages", r"gempages|gem-page"),
    ("Shogun", r"getshogun|shogun-"),
    ("Replo", r"replo"),
    ("Zipify Pages", r"zipify"),
    ("Tolstoy (video)", r"gotolstoy|tolstoy-"),
    ("Recharge Subscriptions", r"rechargecdn|rechargepayments|recharge-"),
    ("Appstle Subscriptions", r"appstle"),
    ("Releasit COD", r"releasit"),
    ("EasySell COD", r"easysell"),
    ("Intelligems (price tests)", r"intelligems"),
    ("Hextom", r"hextom"),
    ("Bold", r"boldapps\.net|bold_common|boldcommerce"),
    ("Weglot", r"weglot"),
    ("Gorgias", r"gorgias"),
    ("Tidio", r"tidio"),
    ("Triple Whale", r"triplewhale|config-security\.com"),
    ("Microsoft Clarity", r"clarity\.ms"),
    ("Hotjar", r"hotjar"),
    ("Meta Pixel", r"connect\.facebook\.net|fbq\("),
    ("TikTok Pixel", r"analytics\.tiktok\.com|ttq\.load"),
    ("Google Tag Manager / GA", r"googletagmanager\.com|gtag\("),
])


def ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def fetch(url, accept, timeout):
    """GET with a browser UA -> (bytes, final_url). Falls back to curl when Python's TLS store fails."""
    headers = {"User-Agent": UA, "Accept": accept, "Accept-Language": "en-US,en;q=0.9",
               "Accept-Encoding": "gzip, deflate"}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout,
                                    context=ssl_context()) as r:
            data = r.read()
            enc = (r.headers.get("Content-Encoding") or "").lower()
            if enc == "gzip":
                data = gzip.decompress(data)
            elif enc == "deflate":
                try:
                    data = zlib.decompress(data)
                except zlib.error:
                    data = zlib.decompress(data, -zlib.MAX_WBITS)
            return data, r.geturl()
    except urllib.error.URLError as e:
        if not (isinstance(getattr(e, "reason", None), ssl.SSLError) and shutil.which("curl")):
            raise
    with tempfile.TemporaryDirectory() as tmp:
        dest = os.path.join(tmp, "body")
        cmd = ["curl", "-sSL", "--fail", "--compressed", "-m", str(timeout), "-o", dest, "-w", "%{url_effective}"]
        for k, v in headers.items():
            if k != "Accept-Encoding":
                cmd += ["-H", f"{k}: {v}"]
        r = subprocess.run(cmd + [url], capture_output=True, text=True)
        if r.returncode != 0:
            raise urllib.error.URLError(f"curl exit {r.returncode}: {r.stderr.strip()}")
        return Path(dest).read_bytes(), r.stdout.strip() or url


def product_json_url(url):
    p = urlsplit(url)
    m = re.search(r"/products/([^/?#]+)", p.path)
    if not m:
        return None
    handle = re.sub(r"\.(json|js)$", "", m.group(1))
    return f"{p.scheme or 'https'}://{p.netloc}/products/{handle}.json"


def absolute(u, base):
    u = u.strip()
    if u.startswith("//"):
        return "https:" + u
    if u.startswith(("http://", "https://")):
        return u
    return urljoin(base, u)


SIZE_SUFFIX_RE = re.compile(r"_(?:\d+x\d*|\d*x\d+|pico|icon|thumb|small|compact|medium|large|grande|master)"
                            r"(?:_crop_[a-z]+)?(?:@\dx)?(?=\.[A-Za-z0-9]+$)")


def clean_media(u):
    """Full-size URL: no query (?v=, width=...), no Shopify size suffix (_800x), https."""
    s = urlsplit(u)
    path = SIZE_SUFFIX_RE.sub("", s.path)
    return urlunsplit(("https" if s.scheme in ("", "http", "https") else s.scheme, s.netloc, path, "", ""))


def html_to_text(fragment):
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", fragment or "")
    t = re.sub(r"(?i)<br\s*/?>|</(p|li|h[1-6]|div|tr)>", "\n", t)
    t = H.unescape(re.sub(r"<[^>]+>", " ", t))
    lines = [re.sub(r"[ \t\xa0]+", " ", ln).strip() for ln in t.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def attrs_of(tag):
    return {k.lower(): H.unescape(v1 if v1 is not None and v1 != "" else v2)
            for k, v1, v2 in re.findall(r"""([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')""", tag)}


class CopyParser(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template", "header", "footer", "nav", "select", "option"}
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "section", "br", "tr", "summary", "details",
             "button", "label"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.out, self.cur = 0, [], []

    def flush(self, tag=None):
        t = re.sub(r"\s+", " ", "".join(self.cur)).strip()
        if t:
            pre = "## " if tag in ("h1", "h2") else "### " if tag in ("h3", "h4") else ""
            self.out.append(pre + t)
        self.cur = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        if tag in self.BLOCK:
            self.flush()

    def handle_endtag(self, tag):
        if tag in self.BLOCK:
            self.flush(tag)
        if tag in self.SKIP and self.skip:
            self.skip -= 1

    def handle_data(self, d):
        if not self.skip:
            self.cur.append(d)


def readable_lines(fragment):
    p = CopyParser()
    p.feed(fragment)
    p.flush()
    lines, seen = [], set()
    for ln in p.out:
        if len(ln) < 2 or ln in seen:
            continue
        seen.add(ln)
        lines.append(ln)
    return lines


class HeadingParser(HTMLParser):
    SKIP = {"script", "style", "svg", "template", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.level, self.buf, self.out = 0, None, [], []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in ("h1", "h2", "h3") and self.level is None:
            self.level, self.buf = tag, []

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag == self.level:
            text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            if text:
                self.out.append([int(tag[1]), text])
            self.level = None

    def handle_data(self, d):
        if self.level and not self.skip:
            self.buf.append(d)


def headings_of(fragment):
    p = HeadingParser()
    p.feed(fragment)
    return p.out


def words(text):
    return len(re.findall(r"\w+", text))


# ---------------------------------------------------------------- colors

def to_hex(r, g, b):
    return "#%02X%02X%02X" % (int(r), int(g), int(b))


def parse_color(val):
    """Return (hex, alpha) for '#hex', 'r,g,b', 'r g b', 'rgb()/rgba()'; None otherwise."""
    v = val.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})", v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        alpha = round(int(h[6:8], 16) / 255, 2) if len(h) == 8 else 1
        return "#" + h[:6].upper(), alpha
    m = (re.fullmatch(r"(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})", v) or
         re.fullmatch(r"rgba?\(\s*(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})(?:\s*[,/]\s*([\d.]+%?))?\s*\)", v))
    if m:
        r, g, b = (int(x) for x in m.groups()[:3])
        if max(r, g, b) > 255:
            return None
        a = m.groups()[3] if len(m.groups()) > 3 else None
        alpha = 1
        if a:
            alpha = float(a[:-1]) / 100 if a.endswith("%") else float(a)
        return to_hex(r, g, b), round(alpha, 2)
    return None


def rgb_str(hexv):
    return "%d,%d,%d" % tuple(int(hexv[i:i + 2], 16) for i in (1, 3, 5))


def extract_colors(src):
    var_values = {}
    for m in re.finditer(r"--([A-Za-z0-9_-]+)\s*:\s*([^;{}\"<>]+?)\s*(?=[;}\"<])", src):
        name, val = m.group(1), m.group(2)
        if not COLOR_NAME_RE.search(name) or "var(" in val:
            continue
        c = parse_color(val)
        if not c:
            continue
        var_values.setdefault(name, Counter())[c[0] if c[1] == 1 else f"{c[0]}@{c[1]}"] += 1

    def palette(app):
        hex_count, hex_vars = Counter(), {}
        for name, vals in var_values.items():
            if bool(APP_VAR_RE.search(name)) != app:
                continue
            for hv, n in vals.items():
                h = hv.split("@")[0]
                hex_count[h] += n
                hex_vars.setdefault(h, set()).add("--" + name)
        return [{"hex": h, "rgb": rgb_str(h), "count": n, "vars": sorted(hex_vars[h])[:6]}
                for h, n in hex_count.most_common(20)]

    no_svg = re.sub(r"(?is)<svg\b.*?</svg>", " ", src)
    no_svg = re.sub(r"--(?:jdgm|judgeme|kaching|loox|okendo|yotpo|payment-terms)[\w-]*\s*:[^;}\"]*", " ", no_svg)
    hex_count = Counter()
    for m in re.finditer(r"(?<![&\w])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![\w-])", no_svg):
        c = parse_color("#" + m.group(1))
        if c:
            hex_count[c[0]] += 1
    return {
        "theme_palette": palette(False),
        "app_palette": palette(True),
        "hex_top": [{"hex": h, "rgb": rgb_str(h), "count": n} for h, n in hex_count.most_common(20)],
        "color_vars": {("--" + k): dict(v.most_common()) for k, v in sorted(var_values.items())},
    }


def rgba_dict_hex(d):
    if not isinstance(d, dict) or "red" not in d:
        return None
    h = to_hex(d.get("red", 0), d.get("green", 0), d.get("blue", 0))
    a = d.get("alpha", 1)
    return h if a in (1, None) else f"{h} @{round(a, 2)}"


# ---------------------------------------------------------------- fonts

def extract_fonts(src):
    fam = Counter()
    for m in re.finditer(r"(?:font-family|--font-[\w-]*family)\s*:\s*([^;}{\"<>]+)", src, re.I):
        first = m.group(1).split(",")[0].strip().strip("'\"").strip()
        if not first or first.lower().startswith("var(") or first.lower() in GENERIC_FONTS or "{" in first:
            continue
        fam[first] += 1
    families = [{"name": n, "count": c} for n, c in fam.most_common() if not ICON_FONT_RE.search(n)]
    icon_fonts = [n for n in fam if ICON_FONT_RE.search(n)]
    files = OrderedDict()
    for m in re.finditer(r"/fonts/([a-z0-9_]+)/([a-z0-9_]+?)_([nio])(\d)\.[0-9a-f]+\.(?:woff2?|ttf|otf)", src):
        family, style, weight = m.group(2), m.group(3), int(m.group(4)) * 100
        files[(family, style, weight)] = {"family": family, "weight": weight,
                                          "style": "italic" if style in "io" else "normal",
                                          "shopify_id": f"{family}_{style}{weight // 100}"}
    google = []
    for m in re.finditer(r"fonts\.googleapis\.com/css2?\?([^\"'<>\s]+)", src):
        for fm in re.finditer(r"family=([^&|]+)", H.unescape(m.group(1))):
            google.append(fm.group(1).replace("+", " "))
    return {"families": families, "shopify_font_files": list(files.values()),
            "google_fonts": sorted(set(google)), "icon_or_app_fonts": icon_fonts}


# ---------------------------------------------------------------- apps & offers

def detect_apps(src):
    out = []
    low = src.lower()
    for name, pat in APP_SIGNATURES.items():
        n = len(re.findall(pat, low, re.I))
        if n:
            out.append({"name": name, "hits": n})
    return out


def parse_kaching(src, base_price):
    blocks = []
    for m in re.finditer(r"<script[^>]*class=\"[^\"]*kaching-bundles-deal-block-settings[^\"]*\"[^>]*>([\s\S]*?)</script>", src):
        raw = m.group(1).strip()
        try:
            d = json.loads(raw)
        except ValueError:
            try:
                d = json.loads(H.unescape(raw))
            except ValueError:
                continue
        badge_by_bar = {b.get("attachedTo", {}).get("dealBarId"): b for b in d.get("badges") or []}
        tiers = []
        for bar in d.get("dealBars") or []:
            qty = bar.get("quantity") or 1
            dtype, dval = bar.get("discountType"), bar.get("discountValue")
            price = None
            if base_price is not None:
                if dtype == "default":
                    price = round(qty * base_price, 2)
                elif dtype == "specific" and dval is not None:
                    price = round(float(dval), 2)
                elif dtype == "percentage" and dval is not None:
                    price = round(qty * base_price * (1 - float(dval) / 100), 2)
            badge = bar.get("badgeText") or (badge_by_bar.get(bar.get("id")) or {}).get("text") or ""
            tiers.append({
                "title": bar.get("title", ""), "subtitle": bar.get("subtitle", ""), "badge": badge,
                "label": bar.get("label", ""), "quantity": qty, "discount_type": dtype, "discount_value": dval,
                "price_total": price, "gifts": [g.get("text", "") for g in bar.get("freeGifts") or []],
                "type": bar.get("dealBarType", ""), "preselected": bar.get("id") == d.get("preselectedDealBarId"),
            })
        colors = {k: rgba_dict_hex(v) for k, v in (d.get("colors") or {}).items() if rgba_dict_hex(v)}
        badges = [{"text": b.get("text"), "text_color": rgba_dict_hex((b.get("colors") or {}).get("text")),
                   "background": rgba_dict_hex((b.get("colors") or {}).get("background"))}
                  for b in d.get("badges") or []]
        features = [k.replace("Enabled", "") for k in ("timerEnabled", "stickyAtcEnabled", "progressiveGiftsEnabled",
                    "checkboxUpsellsEnabled", "subscriptionsEnabled", "scratchOffEnabled", "savingsSummaryEnabled",
                    "lowStockAlertEnabled", "collectionBreaksEnabled") if d.get(k)]
        blocks.append({"block_title": d.get("blockTitle", ""), "layout": d.get("blockLayout", ""),
                       "corner_radius": d.get("cornerRadius"), "tiers": tiers, "colors": colors,
                       "badges": badges, "features_enabled": features})
    return blocks


# ---------------------------------------------------------------- product

def product_from_json(pj):
    p = pj.get("product", pj)
    variants = []
    for v in p.get("variants") or []:
        cap = v.get("compare_at_price")
        variants.append({"title": v.get("title"), "price": v.get("price"),
                         "compare_at_price": cap if cap and float(cap) > 0 else None,
                         "sku": v.get("sku"), "currency": v.get("price_currency")})
    images = [{"url": clean_media(i["src"]), "width": i.get("width"), "height": i.get("height"),
               "alt": i.get("alt")} for i in sorted(p.get("images") or [], key=lambda i: i.get("position", 0))]
    first = variants[0] if variants else {}
    return {"source": "shopify-json", "title": p.get("title"), "vendor": p.get("vendor"),
            "product_type": p.get("product_type"), "handle": p.get("handle"), "tags": p.get("tags"),
            "options": [{"name": o.get("name"), "values": o.get("values")} for o in p.get("options") or []],
            "currency": first.get("currency"), "price": first.get("price"),
            "compare_at_price": first.get("compare_at_price"), "variants": variants, "images": images,
            "body_text": html_to_text(p.get("body_html") or "")}


def product_from_html(src, meta):
    prod = {}
    for m in re.finditer(r"<script[^>]*type=\"application/ld\+json\"[^>]*>([\s\S]*?)</script>", src):
        try:
            data = json.loads(m.group(1).strip())
        except ValueError:
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data])
        for it in items:
            t = it.get("@type") if isinstance(it, dict) else None
            if t == "Product" or (isinstance(t, list) and "Product" in t):
                prod = it
                break
        if prod:
            break
    offers = prod.get("offers") or {}
    offers = offers[0] if isinstance(offers, list) and offers else offers
    imgs = prod.get("image") or meta.get("og:image") or []
    imgs = [imgs] if isinstance(imgs, str) else [i.get("url", "") if isinstance(i, dict) else i for i in imgs]
    brand = prod.get("brand")
    return {"source": "ld+json" if prod else "meta", "title": prod.get("name") or meta.get("og:title"),
            "vendor": brand.get("name") if isinstance(brand, dict) else brand, "product_type": None,
            "handle": None, "tags": None, "options": [],
            "currency": (offers or {}).get("priceCurrency") or meta.get("og:price:currency") or meta.get("product:price:currency"),
            "price": str((offers or {}).get("price") or meta.get("og:price:amount") or meta.get("product:price:amount") or "") or None,
            "compare_at_price": None, "variants": [],
            "images": [{"url": clean_media(absolute(u, "https://x/")), "width": None, "height": None, "alt": None}
                       for u in imgs if u],
            "body_text": html_to_text(prod.get("description") or meta.get("description") or "")}


def page_meta(src):
    meta = {}
    for m in re.finditer(r"<meta\b[^>]*>", src[:200000], re.I):
        a = attrs_of(m.group(0))
        key = (a.get("property") or a.get("name") or "").lower()
        if key and "content" in a and key not in meta:
            meta[key] = a["content"]
    t = re.search(r"<title[^>]*>([\s\S]*?)</title>", src, re.I)
    meta["title"] = " ".join(H.unescape(t.group(1)).split()) if t else ""
    return meta


# ---------------------------------------------------------------- sections & media

HEAD = "(head)"
SECTION_RE = re.compile(r"<(?:div|section)\b[^>]*\bid=\"shopify-section-([^\"]+)\"[^>]*>")


def section_index(text):
    out = []
    for m in SECTION_RE.finditer(text):
        sid = m.group(1)
        key = sid.split("__")[-1]
        cls = attrs_of(m.group(0)).get("class", "")
        group = ("header" if "header-group" in cls or "header" == key else
                 "footer" if "footer-group" in cls or "footer" == key else
                 "template" if sid.startswith("template--") else "other")
        stype = "app/custom block" if re.fullmatch(r"[0-9a-f]{12,}", key) else re.sub(r"_[A-Za-z0-9]{6}$", "", key)
        out.append({"start": m.start(), "id": sid, "key": key, "type": stype, "group": group})
    return out


def section_at(sections, pos, body_start):
    if pos < body_start:
        return HEAD
    cur = None
    for s in sections:
        if s["start"] > pos:
            break
        cur = s["key"]
    return cur or "(outside sections)"


URL_RE = re.compile(r"(?:https?:)?//[\w.-]+\.[a-zA-Z]{2,}(?::\d+)?/[^\s\"'<>()\\,{}|^`]*"
                    r"|(?<![\w/.])/cdn/shop/[^\s\"'<>()\\,{}|^`]+")
TESTI_CTX_RE = re.compile(r"testimonial|review|rt-card|rt-photo|rt-quote|quote|ugc|customer-?(?:photo|story)|"
                          r"star-?rating|out of 5|verified", re.I)
TESTI_NAME_RE = re.compile(r"testimonial|review|ugc|customer|avatar|reviewer|before.?after", re.I)
PERSON_ALT_RE = re.compile(r"^[A-Z][a-z]+(?:[ .-]+[A-Z][a-z]*\.?){0,2}$")
LOGO_RE = re.compile(r"logo|icon|favicon|badge|payment|flag|sprite|placeholder|loader|spinner", re.I)


def extract_media(src, base, product_files):
    text = H.unescape(src.replace("\\/", "/").replace("\\u0026", "&"))
    sections = section_index(text)
    body = re.search(r"<body\b", text, re.I)
    body_start = body.start() if body else 0

    alts = {}
    for m in re.finditer(r"<img\b[^>]*>", src, re.I):
        a = attrs_of(m.group(0))
        alt = (a.get("alt") or "").strip()
        if not alt:
            continue
        for attr in ("src", "data-src", "srcset", "data-srcset"):
            for part in re.split(r",\s+", a.get(attr, "")):
                u = part.strip().split(" ")[0]
                if u:
                    alts.setdefault(os.path.basename(clean_media(absolute(u, base))).lower(), alt)

    items = OrderedDict()
    for m in URL_RE.finditer(text):
        url = absolute(m.group(0).rstrip(".;:"), base)
        s = urlsplit(url)
        path = s.path
        ext = os.path.splitext(path)[1].lower()
        host = s.netloc.lower()
        embed = re.search(r"(youtube\.com/embed/|youtu\.be/|player\.vimeo\.com/video/)", url)
        if ext == ".gif":
            kind = "gifs"
        elif ext in VIDEO_EXT or ("/videos/" in path and ext not in IMG_EXT and ext not in (".js", ".css")) or embed:
            kind = "videos"
        elif ext in IMG_EXT:
            kind = "shop" if ("/cdn/shop/" in path or "/s/files/" in path or host == "cdn.shopify.com") else "other_images"
        else:
            continue
        clean = url.split("#")[0] if embed else clean_media(url)
        fname = os.path.basename(urlsplit(clean).path)
        key = fname.lower() if kind in ("shop", "gifs") else clean
        it = items.get(key)
        if not it:
            it = items[key] = {"url": clean, "file": fname, "kind": kind, "count": 0, "pos": m.start(),
                               "section": section_at(sections, m.start(), body_start)}
            if it["section"] == HEAD:
                it["head_only"] = True
        it["count"] += 1
        if host == "cdn.shopify.com" and "cdn.shopify.com" not in it["url"]:
            it["url"] = clean
        if m.start() >= body_start and it.get("head_only"):
            it["head_only"] = False
            it["section"] = section_at(sections, m.start(), body_start)
            it["pos"] = m.start()

    media = OrderedDict((k, []) for k in ("product_images", "gifs", "videos", "section_images",
                                          "testimonial_images", "other_images"))
    for it in items.values():
        alt = alts.get(it["file"].lower(), "")
        rec = {"url": it["url"], "file": it["file"], "section": it["section"], "count": it["count"]}
        if alt:
            rec["alt"] = alt
        if it["kind"] == "shop":
            if it["file"].lower() in product_files:
                media["product_images"].append(rec)
                continue
            if it["section"] == HEAD:
                media["other_images"].append(rec)
                continue
            if LOGO_RE.search(it["file"]):
                rec["logo_or_icon"] = True
            media["section_images"].append(rec)
            window = text[max(0, it["pos"] - 700): it["pos"] + 700]
            score = (2 if re.search(r"review|testimonial|ugc|social", it["section"], re.I) else 0) + \
                    (2 if TESTI_NAME_RE.search(it["file"]) else 0) + \
                    (1 if TESTI_CTX_RE.search(window) else 0) + \
                    (1 if alt and len(alt) < 30 and PERSON_ALT_RE.match(alt) else 0)
            if score >= 2 and not rec.get("logo_or_icon"):
                media["testimonial_images"].append(rec)
        else:
            media[it["kind"]].append(rec)
    return media, sections, text


def build_sections(src):
    secs = section_index(src)
    out = []
    for i, s in enumerate(secs):
        chunk = src[s["start"]: secs[i + 1]["start"] if i + 1 < len(secs) else len(src)]
        lines = readable_lines(chunk)
        body = " ".join(ln.lstrip("# ") for ln in lines)
        files = []
        for m in URL_RE.finditer(H.unescape(chunk.replace("\\/", "/"))):
            ext = os.path.splitext(urlsplit(m.group(0)).path)[1].lower()
            if ext in IMG_EXT | {".gif"} | VIDEO_EXT:
                f = os.path.basename(clean_media(absolute(m.group(0), "https://x/")))
                if f not in files and not LOGO_RE.search(f):
                    files.append(f)
        out.append({"id": s["id"], "key": s["key"], "type": s["type"], "group": s["group"],
                    "headings": headings_of(chunk), "words": words(body), "snippet": body[:220],
                    "media": files[:20]})
    return out


# ---------------------------------------------------------------- report

def md_table(headers, rows):
    esc = lambda v: str("" if v is None else v).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def write_md(cap, path):
    p, o = cap["product"], cap["offers"]["kaching"]
    L = [f"# Competitor capture: {p.get('title') or cap['page'].get('title')}", "",
         f"- URL: {cap['url']}", f"- Final URL: {cap['final_url']}", f"- Captured: {cap['captured_at']}",
         f"- Shopify product JSON: {'yes' if cap['shopify_json'] else 'no'} (product data source: {p.get('source')})",
         f"- Page title: {cap['page'].get('title', '')}", f"- Meta description: {cap['page'].get('description', '')}", "",
         "## Product", "",
         f"- Title: **{p.get('title')}**", f"- Vendor: {p.get('vendor')}  |  Type: {p.get('product_type')}  |  Handle: {p.get('handle')}",
         f"- Price: **{p.get('price')} {p.get('currency') or ''}**  |  Compare-at: {p.get('compare_at_price')}",
         f"- Options: {', '.join(o_['name'] + ': ' + '/'.join(map(str, o_['values'] or [])) for o_ in p.get('options') or []) or '-'}", ""]
    if p.get("variants"):
        L += [md_table(["Variant", "Price", "Compare-at", "SKU"],
                       [[v["title"], v["price"], v["compare_at_price"], v["sku"]] for v in p["variants"]]), ""]
    L += [f"### Product images ({len(p.get('images') or [])})", ""]
    L += [f"{i}. {im['url']}" + (f"  ({im['width']}x{im['height']})" if im.get("width") else "")
          for i, im in enumerate(p.get("images") or [], 1)]
    L += ["", "### Description (body_html)", "", p.get("body_text") or "_(empty)_", ""]

    L += ["## Offers / bundles", ""]
    if not o:
        L += ["No Kaching deal block found (check screenshots for other bundle apps or native variants).", ""]
    for b in o:
        L += [f"### Kaching Bundles: \"{b['block_title']}\" (layout {b['layout']}, radius {b['corner_radius']})", "",
              md_table(["Tier", "Subtitle", "Badge", "Qty", "Discount", "Total price", "Label", "Gifts", "Preselected"],
                       [[t["title"], t["subtitle"], t["badge"], t["quantity"], f"{t['discount_type']} {t['discount_value']}",
                         t["price_total"], t["label"], "; ".join(t["gifts"]), "yes" if t["preselected"] else ""]
                        for t in b["tiers"]]), "",
              "Colors: " + ", ".join(f"{k} {v}" for k, v in b["colors"].items()), "",
              "Badges: " + ", ".join(f"{x['text']} ({x['text_color']} on {x['background']})" for x in b["badges"]), "",
              "Enabled extras: " + (", ".join(b["features_enabled"]) or "none"), ""]

    L += ["## Apps detected", "", ", ".join(f"{a['name']} ({a['hits']})" for a in cap["apps"]) or "none", ""]

    c = cap["colors"]
    L += ["## Palette", "", "### Theme color variables (CSS custom properties, app vars excluded)", "",
          md_table(["Hex", "RGB", "Count", "Example vars"],
                   [[x["hex"], x["rgb"], x["count"], ", ".join(x["vars"][:4])] for x in c["theme_palette"]]), "",
          "### Hex literals, top 20 (inline SVG and app variables excluded)", "",
          md_table(["Hex", "RGB", "Count"], [[x["hex"], x["rgb"], x["count"]] for x in c["hex_top"]]), ""]
    if c["app_palette"]:
        L += ["App colors (not brand): " + ", ".join(f"{x['hex']} ({x['vars'][0]})" for x in c["app_palette"][:8]), ""]

    f = cap["fonts"]
    L += ["## Fonts", "",
          "- font-family declarations: " + (", ".join(f"{x['name']} ({x['count']})" for x in f["families"]) or "-"),
          "- Shopify font files: " + (", ".join(x["shopify_id"] for x in f["shopify_font_files"]) or "-"),
          "- Google Fonts: " + (", ".join(f["google_fonts"]) or "-"),
          "- Icon/app fonts: " + (", ".join(f["icon_or_app_fonts"]) or "-"), ""]

    L += ["## Page skeleton (Shopify sections in order)", ""]
    for i, s in enumerate(cap["sections"], 1):
        hs = " / ".join(f"H{lv}: {t}" for lv, t in s["headings"][:6]) or "(no h1-h3)"
        L.append(f"{i}. **{s['key']}** [{s['group']}, type `{s['type']}`] {s['words']} words. {hs}")
        if s["media"]:
            L.append(f"   - media: {', '.join(s['media'][:10])}")
    L += ["", "## Headings in <main> (h1-h3)", ""]
    L += [f"{'  ' * (lv - 1)}- H{lv} {t}" for lv, t in cap["headings"]]

    L += ["", "## Media URLs", ""]
    for k, items in cap["media"].items():
        L += [f"### {k.replace('_', ' ').title()} ({len(items)})", ""]
        L += [f"- {x['url']}  [section: {x['section']}]" + (f" alt=\"{x['alt']}\"" if x.get("alt") else "")
              for x in items[:60]] or ["- none"]
        if len(items) > 60:
            L.append(f"- ... {len(items) - 60} more in capture.json")
        L.append("")
    L += ["## Copy", "", f"Readable copy of <main>: copy.txt ({cap['copy']['words']} words).", ""]
    Path(path).write_text("\n".join(L), encoding="utf-8")


# ---------------------------------------------------------------- main

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", help="competitor product page URL")
    ap.add_argument("--out", required=True, help="output directory (created if missing)")
    ap.add_argument("--html-file", help="use this saved HTML instead of fetching the page")
    ap.add_argument("--no-json", action="store_true", help="do not request <url>.json")
    ap.add_argument("--timeout", type=int, default=40, help="HTTP timeout in seconds (default 40)")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    url = args.url.strip()
    warnings = []

    pj = None
    json_url = None if args.no_json else product_json_url(url)
    if json_url:
        try:
            data, _ = fetch(json_url, "application/json,text/javascript,*/*;q=0.1", args.timeout)
            pj = json.loads(data.decode("utf-8"))
            if "product" not in pj:
                raise ValueError("no 'product' key")
            (out / "p.json").write_bytes(data)
        except (ValueError, OSError) as e:
            pj = None
            warnings.append(f"product JSON unavailable ({json_url}): {e}")
    elif not args.no_json:
        warnings.append("URL has no /products/<handle> path; skipped product JSON")

    if args.html_file:
        src = Path(args.html_file).read_text(encoding="utf-8", errors="ignore")
        final_url = url
    else:
        try:
            data, final_url = fetch(url, "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", args.timeout)
        except OSError as e:
            print(f"ERROR: could not fetch page HTML: {e}", file=sys.stderr)
            print("Tip: save the page from a browser and pass --html-file.", file=sys.stderr)
            return 2
        src = data.decode("utf-8", errors="ignore")
    (out / "p.html").write_text(src, encoding="utf-8")
    if len(src) < 2000 or re.search(r"cf-challenge|captcha|Access denied", src[:5000], re.I):
        warnings.append("HTML looks like a bot challenge or is very small; consider --html-file")

    meta = page_meta(src)
    product = product_from_json(pj) if pj else product_from_html(src, meta)
    try:
        base_price = float(product.get("price")) if product.get("price") else None
    except ValueError:
        base_price = None
    product_files = {os.path.basename(urlsplit(i["url"]).path).lower() for i in product["images"]}

    main_m = re.search(r"<main\b[\s\S]*?</main>", src, re.I)
    main_html = main_m.group(0) if main_m else src
    copy_lines = readable_lines(main_html)
    copy_text = "\n".join(copy_lines)
    n_words = words(copy_text)
    (out / "copy.txt").write_text(f"WORDS: {n_words}\n\n{copy_text}\n", encoding="utf-8")

    media, _, _ = extract_media(src, final_url, product_files)
    known = {m["file"].lower() for m in media["product_images"]}
    for im in product["images"]:
        f = os.path.basename(urlsplit(im["url"]).path)
        if f.lower() not in known:
            media["product_images"].append({"url": im["url"], "file": f, "section": "(product json)", "count": 0})
    order = {os.path.basename(urlsplit(i["url"]).path).lower(): n for n, i in enumerate(product["images"])}
    media["product_images"].sort(key=lambda r: order.get(r["file"].lower(), 999))
    for r in media["product_images"]:
        j = order.get(r["file"].lower())
        if j is not None:
            r["url"] = product["images"][j]["url"]

    cap = OrderedDict([
        ("url", url), ("final_url", final_url), ("json_url", json_url), ("shopify_json", bool(pj)),
        ("captured_at", datetime.datetime.now().isoformat(timespec="seconds")),
        ("page", {"title": meta.get("title", ""), "description": meta.get("description", ""),
                  "og_image": meta.get("og:image", "")}),
        ("product", product),
        ("offers", {"kaching": parse_kaching(src, base_price)}),
        ("apps", detect_apps(src)),
        ("colors", extract_colors(src)),
        ("fonts", extract_fonts(src)),
        ("sections", build_sections(src)),
        ("headings", headings_of(main_html)),
        ("media", media),
        ("copy", {"file": "copy.txt", "words": n_words}),
        ("warnings", warnings),
    ])
    (out / "capture.json").write_text(json.dumps(cap, indent=2, ensure_ascii=False), encoding="utf-8")
    write_md(cap, out / "capture.md")

    p = product
    print(f"Product : {p.get('title')}  |  {p.get('price')} {p.get('currency') or ''}"
          f"  |  {len(p.get('variants') or [])} variant(s)  |  {len(p.get('images') or [])} image(s)  [{p.get('source')}]")
    for b in cap["offers"]["kaching"]:
        tiers = "; ".join(f"{t['title']}" + (f" [{t['badge']}]" if t["badge"] else "") +
                          (f" {t['price_total']}" if t["price_total"] is not None else "") for t in b["tiers"])
        print(f"Kaching : {b['block_title']} -> {tiers}")
    print("Apps    : " + (", ".join(a["name"] for a in cap["apps"]) or "none"))
    print("Palette : " + ", ".join(f"{x['hex']}({x['rgb']})" for x in cap["colors"]["theme_palette"][:8]))
    print("Hex top : " + ", ".join(f"{x['hex']}x{x['count']}" for x in cap["colors"]["hex_top"][:8]))
    f = cap["fonts"]
    print("Fonts   : " + ", ".join(x["name"] for x in f["families"][:6]) +
          ("  | files: " + ", ".join(x["shopify_id"] for x in f["shopify_font_files"]) if f["shopify_font_files"] else ""))
    print("Media   : " + ", ".join(f"{k}={len(v)}" for k, v in media.items()))
    for g in media["gifs"]:
        print(f"  gif   : {g['url']}")
    for v in media["videos"]:
        print(f"  video : {v['url']}")
    print(f"Sections: {len(cap['sections'])}  |  headings in main: {len(cap['headings'])}  |  copy: {n_words} words")
    for w in warnings:
        print(f"WARNING : {w}")
    print("Wrote   : " + ", ".join(str(out / n) for n in ("p.json", "p.html", "copy.txt", "capture.json", "capture.md")
                                   if (out / n).exists()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
