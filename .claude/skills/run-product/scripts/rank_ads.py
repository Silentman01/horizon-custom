#!/usr/bin/env python3
"""rank_ads.py - merge Brandsearch Meta-ad dumps, download creatives, dedupe, rank.

Usage (Python 3.10+, stdlib + Pillow; run with -I):
  python -I rank_ads.py --dumps FILE [FILE ...] --out DIR [--top 30]
                        [--keyword headlight] [--sheet]
                        [--extra-image ID=PATH ...] [--offline] [--near-dup]

Accepted dump formats (any mix, any number of files/pages):
  * raw JSON object  {"pagination": {...}, "data": [ {ad}, ... ]}
  * harness .txt     plain-text prefix, JSON starts at the first "{"
  * harness .json    [{"type": "text", "text": "<json string>"}]
  * single-ad JSON   (get_meta_ad / get_ad_by_url result)

Ranking (operator rule 7), --sort:
  rank  (default, any market) Brandsearch "Top rank (by impressions)" = reach_rank,
        ascending (1 = most impressions among the brand's ads; best value across
        merged ids). Longest-running is NOT best: an ad can run for weeks on a tiny
        budget. Ads without reach_rank go after ranked ones.
  spend / reach  (EU markets only - eu_total_spend / eu_total_reach exist only for
        ads delivered in the EU; US ads have none), descending.
  days  days running = max(total_active_time / 86400, latest end - earliest start).
Tie-breakers for every mode: days running desc, then copies (ids sharing the
identical image) + duplicate_count desc, then earliest first_seen, then lead id.
Identical creatives are merged by md5 of the downloaded bytes. Images that
could not be fetched at original size (resized URL, thumbnail, download_ad
blob passed via --extra-image) are attached to an original-size group when
they are a perceptual near-match; otherwise they stay separate (thumbnail-only
groups are flagged low_res).

Outputs in --out:
  NN_<leadid>.<ext>    top-N creatives, ranked file names
  ranking.json         every unique creative (rank, file, ids, days, ...)
  missing_images.json  ids with no usable image (candidates for download_ad)
  merged_ads.json      every merged ad row with computed days and group rank
  copy_summary.md      distinct captions (title / description / CTA) + counts
  sheet_top10.jpg, sheet_NN.jpg   contact sheets (with --sheet)
  _cache/              raw downloads (<id>__<kind>.<ext>), reused on re-runs
  raw/                 copies of the input dumps (provenance)
"""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install Pillow")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
KIND_ORDER = {"original": 0, "extra": 1, "resized": 2, "thumb": 3}
URL_FIELDS = [("original", "image_original_url"), ("resized", "image_url"),
              ("thumb", "thumbnail_url")]
AD_HINT_KEYS = ("start_date", "creative", "image_url", "image_original_url",
                "thumbnail_url", "total_active_time", "is_image", "dashboard_url")
# Perceptual distance = mean abs diff of 24x24 grayscale, 0..1. Calibrated on the Plaims set:
# a download_ad blob / resized copy vs its original = 0.001-0.002; the two closest DIFFERENT
# creatives (same layout, other photo) = 0.066. Keep NEAR_T well below that.
NEAR_T = 0.02
POSSIBLE_T = 0.045  # reported as "possible near-duplicates" for a human look


# --------------------------------------------------------------------------- parsing
def parse_jsonish(text):
    """Return every top-level JSON value found in text (handles prefixed text)."""
    text = text.lstrip("\ufeff")
    try:
        return [json.loads(text)]
    except ValueError:
        pass
    dec, out, i = json.JSONDecoder(), [], 0
    pat = re.compile(r"[\[{]")
    while True:
        m = pat.search(text, i)
        if not m:
            break
        try:
            obj, end = dec.raw_decode(text, m.start())
            out.append(obj)
            i = end
        except ValueError:
            i = m.start() + 1
    return out


def looks_like_ad(d):
    return isinstance(d, dict) and "id" in d and any(k in d for k in AD_HINT_KEYS)


def extract_rows(obj, pags):
    """Yield ad rows from any nesting of dicts/lists/JSON strings."""
    if isinstance(obj, str):
        s = obj.strip()
        if s[:1] in ("{", "["):
            for o in parse_jsonish(s):
                yield from extract_rows(o, pags)
        return
    if isinstance(obj, list):
        for x in obj:
            yield from extract_rows(x, pags)
        return
    if isinstance(obj, dict):
        if looks_like_ad(obj):
            yield obj
            return
        if isinstance(obj.get("pagination"), dict):
            pags.append(obj["pagination"])
        for k, v in obj.items():
            if k != "summary" and isinstance(v, (dict, list, str)):
                yield from extract_rows(v, pags)


def load_dump(path):
    with open(path, "rb") as f:
        text = f.read().decode("utf-8", "replace")
    pags, rows = [], []
    for o in parse_jsonish(text):
        rows.extend(extract_rows(o, pags))
    return rows, pags


# --------------------------------------------------------------------------- normalising
def parse_dt(v):
    if v in (None, ""):
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v, tz=timezone.utc).replace(tzinfo=None)
    s = str(v).strip().replace("Z", "")
    if re.fullmatch(r"\d{9,11}", s):
        return datetime.fromtimestamp(int(s), tz=timezone.utc).replace(tzinfo=None)
    s = re.sub(r"([+-]\d\d:\d\d)$", "", s)
    for fmt in (None, "%Y-%m-%d"):
        try:
            return datetime.fromisoformat(s) if fmt is None else datetime.strptime(s[:10], fmt)
        except ValueError:
            continue
    return None


def creative_texts(row):
    """-> (titles, descriptions, bodies, ctas) as lists of strings."""
    titles, descs, bodies, ctas = [], [], [], []
    cr = row.get("creative")
    blocks = []
    if isinstance(cr, dict):
        blocks.append(cr)
        for card in cr.get("cards") or []:
            if isinstance(card, dict):
                blocks.append(card)
    for key in ("cards",):
        for card in row.get(key) or []:
            if isinstance(card, dict):
                blocks.append(card)
    for b in blocks:
        for k, dst in (("title", titles), ("headline", titles), ("description", descs),
                       ("body", bodies), ("caption", bodies), ("link_description", bodies)):
            v = b.get(k)
            if isinstance(v, str) and v.strip():
                dst.append(v.strip())
        cta = b.get("cta")
        if isinstance(cta, dict):
            t = " - ".join(x for x in (cta.get("type"), cta.get("text")) if x)
            if t:
                ctas.append(t)
        elif isinstance(cta, str) and cta.strip():
            ctas.append(cta.strip())
    summ = row.get("summary")
    if isinstance(summ, str) and not titles:
        m = re.search(r'Headline:\s*"?(.+?)"?\s*$', summ, re.M)
        if m:
            titles.append(m.group(1).strip())
    return titles, descs, bodies, ctas


def uniq(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def merge_rows(all_rows):
    """all_rows: list of (source_file, row). Returns {id: merged}."""
    ads = {}
    for order, (src, r) in enumerate(all_rows):
        aid = str(r.get("id"))
        m = ads.get(aid)
        if m is None:
            m = ads[aid] = {
                "id": aid, "order": order, "sources": [], "status": None, "_status_end": None,
                "start": None, "end": None, "tat": None, "is_video": False, "is_image": None,
                "is_duplicate": None, "duplicate_count": None, "cards_count": None,
                "urls": {}, "dashboard_url": None, "titles": [], "descriptions": [],
                "bodies": [], "ctas": [], "summary": None,
                "reach_rank": None, "eu_spend": None, "eu_reach": None,
            }
        if src not in m["sources"]:
            m["sources"].append(src)
        st, en = parse_dt(r.get("start_date")), parse_dt(r.get("end_date"))
        if st and (m["start"] is None or st < m["start"]):
            m["start"] = st
        if en and (m["end"] is None or en > m["end"]):
            m["end"] = en
        status = r.get("status")
        if status:  # on conflict trust the row that saw the ad most recently
            if m["status"] is None or (en and (m["_status_end"] is None or en >= m["_status_end"])):
                m["status"], m["_status_end"] = str(status).lower(), en
        tat = r.get("total_active_time")
        if isinstance(tat, (int, float)) and (m["tat"] is None or tat > m["tat"]):
            m["tat"] = tat
        if r.get("is_video") is True:
            m["is_video"] = True
        if r.get("is_image") is not None and m["is_image"] is None:
            m["is_image"] = bool(r.get("is_image"))
        if r.get("is_duplicate") is not None and m["is_duplicate"] is None:
            m["is_duplicate"] = bool(r.get("is_duplicate"))
        rr = r.get("reach_rank")
        if isinstance(rr, (int, float)) and (m["reach_rank"] is None or rr < m["reach_rank"]):
            m["reach_rank"] = int(rr)
        for fld, key in (("eu_total_spend", "eu_spend"), ("eu_total_reach", "eu_reach")):
            v = r.get(fld)
            if isinstance(v, (int, float)) and (m[key] is None or v > m[key]):
                m[key] = v
        dc = r.get("duplicate_count")
        if isinstance(dc, (int, float)) and (m["duplicate_count"] is None or dc > m["duplicate_count"]):
            m["duplicate_count"] = int(dc)
        if r.get("cards_count") is not None and m["cards_count"] is None:
            m["cards_count"] = r.get("cards_count")
        for kind, f in URL_FIELDS:
            if r.get(f) and kind not in m["urls"]:
                m["urls"][kind] = r[f]
        if r.get("dashboard_url") and not m["dashboard_url"]:
            m["dashboard_url"] = r["dashboard_url"]
        if isinstance(r.get("summary"), str) and not m["summary"]:
            m["summary"] = r["summary"]
        t, d, b, c = creative_texts(r)
        m["titles"] = uniq(m["titles"] + t)
        m["descriptions"] = uniq(m["descriptions"] + d)
        m["bodies"] = uniq(m["bodies"] + b)
        m["ctas"] = uniq(m["ctas"] + c)
    now = datetime.utcnow()
    for m in ads.values():
        end = m["end"]
        m["end_estimated"] = False
        if end is None and m["status"] == "active" and m["start"]:
            end, m["end_estimated"] = now, True
        span = (end - m["start"]).total_seconds() / 86400 if (m["start"] and end) else 0.0
        tat_days = (m["tat"] or 0) / 86400
        m["days"] = round(max(span, tat_days, 0.0), 1)
    return ads


def text_blob(m):
    return " ".join(m["titles"] + m["descriptions"] + m["bodies"] + [m["summary"] or ""]).lower()


# --------------------------------------------------------------------------- download
def fetch(url, tries=3, timeout=40):
    err = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            Image.open(io.BytesIO(data)).verify()
            return data, None
        except urllib.error.HTTPError as e:
            body = b""
            try:
                body = e.read(300)
            except Exception:
                pass
            err = f"HTTP {e.code}"
            if b"xpired" in body:
                err += " expired (media URLs live 3 days: re-pull the dump, re-run at once)"
                break
            if e.code in (404, 410):
                err += " (file not held by Brandsearch, or URL expired)"
                break
        except Exception as e:  # network, timeout, not-an-image
            err = f"{type(e).__name__}: {e}"
        time.sleep(1.5 * (attempt + 1))
    return None, err


def img_ext(data):
    fmt = (Image.open(io.BytesIO(data)).format or "JPEG").upper()
    return {"JPEG": "jpg", "PNG": "png", "WEBP": "webp", "GIF": "gif"}.get(fmt, fmt.lower())


def cached(cache_dir, aid):
    """Best cached file for an id -> (kind, path) or None."""
    best = None
    prefix = f"{aid}__"
    for fn in os.listdir(cache_dir):
        if fn.startswith(prefix):
            kind = fn[len(prefix):].split(".")[0]
            if kind in KIND_ORDER and (best is None or KIND_ORDER[kind] < KIND_ORDER[best[0]]):
                best = (kind, os.path.join(cache_dir, fn))
    return best


def acquire(m, cache_dir, offline):
    """Ensure an image for ad m. Sets m['img'] = (kind, path) or m['img_error']."""
    hit = cached(cache_dir, m["id"])
    if hit and hit[0] in ("original", "extra"):
        m["img"] = hit
        return
    errors = []
    if not offline:
        for kind, _f in URL_FIELDS:
            url = m["urls"].get(kind)
            if not url:
                continue
            if hit and KIND_ORDER[hit[0]] <= KIND_ORDER[kind]:
                break  # cache already as good as what is left
            data, err = fetch(url)
            if data:
                path = os.path.join(cache_dir, f"{m['id']}__{kind}.{img_ext(data)}")
                with open(path, "wb") as f:
                    f.write(data)
                m["img"] = (kind, path)
                return
            errors.append(f"{kind}: {err}")
    if hit:
        m["img"] = hit
        return
    m["img_error"] = "; ".join(errors) if errors else (
        "offline and not cached" if offline else "no image URL in any dump")


# --------------------------------------------------------------------------- similarity
def signature(path):
    with Image.open(path) as im:
        w, h = im.size
        g = im.convert("L").resize((24, 24), Image.LANCZOS)
        return (w, h), list(g.getdata())


def distance(sa, sb):
    (wa, ha), pa = sa
    (wb, hb), pb = sb
    if abs(wa / ha - wb / hb) > 0.04:
        return 1.0
    return sum(abs(x - y) for x, y in zip(pa, pb)) / (255.0 * len(pa))


def aspect_label(w, h):
    r = w / h
    known = {"1:1": 1.0, "4:5": 0.8, "9:16": 0.5625, "16:9": 1.7778, "2:3": 0.6667,
             "3:4": 0.75, "1.91:1": 1.91, "5:4": 1.25}
    name, val = min(known.items(), key=lambda kv: abs(kv[1] - r))
    return name if abs(val - r) < 0.03 else f"{r:.2f}:1"


# --------------------------------------------------------------------------- contact sheet
def load_font(size):
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_sheet(entries, out_dir, path, cols=5, cell=300):
    """Inline tiling: image fitted in a 4:5 cell + 2 label lines."""
    img_h, lab_h = int(cell * 1.25), 46
    rows = (len(entries) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * (img_h + lab_h)), (245, 245, 245))
    d = ImageDraw.Draw(sheet)
    f1, f2 = load_font(17), load_font(13)
    for i, e in enumerate(entries):
        x, y = (i % cols) * cell, (i // cols) * (img_h + lab_h)
        try:
            with Image.open(os.path.join(out_dir, e["file"])) as im:
                im = im.convert("RGB")
                im.thumbnail((cell - 8, img_h - 8), Image.LANCZOS)
                sheet.paste(im, (x + (cell - im.width) // 2, y + 4 + (img_h - 8 - im.height) // 2))
        except Exception as ex:
            d.text((x + 8, y + 8), f"ERR {ex}", fill=(200, 0, 0), font=f2)
        flag = " LOW-RES" if e.get("low_res") else ""
        d.rectangle([x, y + img_h, x + cell - 1, y + img_h + lab_h - 1], fill=(20, 20, 20))
        d.text((x + 6, y + img_h + 3),
               f"#{e['rank']}  r{e.get('reach_rank') if e.get('reach_rank') is not None else '-'}  {e['days']:g}d  {e['copies']}x+{e['duplicate_count']}dup{flag}",
               fill=(255, 210, 60), font=f1)
        d.text((x + 6, y + img_h + 25), f"{e['lead_id']}  {e['width']}x{e['height']}",
               fill=(230, 230, 230), font=f2)
    sheet.save(path, quality=85)


def build_sheets(top, out_dir, per):
    paths = []
    sheet_mod = None
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(here, "contact_sheet.py")):
        try:
            sys.path.insert(0, here)
            import contact_sheet as sheet_mod  # noqa: F401  (shared helper if it exposes make_sheet)
        except Exception:
            sheet_mod = None
        finally:
            sys.path.pop(0)
    # The labelled inline tiler is used for ranked sheets (rank/days/copies labels are the point).
    _ = sheet_mod
    p = os.path.join(out_dir, "sheet_top10.jpg")
    make_sheet(top[:10], out_dir, p, cols=5, cell=360)
    paths.append(p)
    for i in range(0, len(top), per):
        p = os.path.join(out_dir, f"sheet_{i // per + 1:02d}.jpg")
        make_sheet(top[i:i + per], out_dir, p, cols=5, cell=300)
        paths.append(p)
    return paths


# --------------------------------------------------------------------------- main
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dumps", nargs="+", required=True, help="Brandsearch dump files")
    ap.add_argument("--out", required=True, help="output dir (e.g. PRODUCT_DIR/05_ads/competitor)")
    ap.add_argument("--top", type=int, default=30, help="ranked files to write (default 30)")
    ap.add_argument("--keyword", action="append", default=[],
                    help="keep ads whose caption contains this (repeatable, any match)")
    ap.add_argument("--sort", choices=["rank", "spend", "reach", "days"], default="rank",
                    help="rank = Brandsearch Top rank by impressions (default); spend/reach = EU markets only; days = days running")
    ap.add_argument("--sheet", action="store_true", help="write contact sheets")
    ap.add_argument("--sheet-per", type=int, default=15, help="creatives per batch sheet")
    ap.add_argument("--extra-image", action="append", default=[], metavar="ID=PATH",
                    help="image for an id without URL (e.g. download_ad blob)")
    ap.add_argument("--offline", action="store_true", help="no network; use _cache only")
    ap.add_argument("--near-dup", action="store_true",
                    help="also merge near-identical original-size creatives (re-encodes)")
    ap.add_argument("--include-video", action="store_true",
                    help="keep video ads (ranked by their cover frame)")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    out = os.path.abspath(a.out)
    cache = os.path.join(out, "_cache")
    rawdir = os.path.join(out, "raw")
    os.makedirs(cache, exist_ok=True)
    os.makedirs(rawdir, exist_ok=True)

    # 1. parse ------------------------------------------------------------------
    all_rows = []
    print("== Dumps ==")
    for p in a.dumps:
        rows, pags = load_dump(p)
        base = os.path.basename(p)
        all_rows.extend((base, r) for r in rows)
        pinfo = ""
        for pg in pags:
            pinfo += (f" | page {pg.get('page')}/{pg.get('total_pages')}, "
                      f"page_size {pg.get('page_size')}, total {pg.get('total')}")
            if pg.get("total_pages") and pg.get("page") and pg["page"] < pg["total_pages"]:
                pinfo += "  <-- MORE PAGES EXIST"
        print(f"  {base}: {len(rows)} rows{pinfo}")
        dst = os.path.join(rawdir, base)
        if os.path.abspath(p) != os.path.abspath(dst):
            shutil.copy2(p, dst)
    if not all_rows:
        sys.exit("No ad rows found in the dumps (check the files).")

    ads = merge_rows(all_rows)
    print(f"  merged: {len(all_rows)} rows -> {len(ads)} unique ad ids")

    # 2. filter -----------------------------------------------------------------
    kws = [k.lower() for k in a.keyword if k.strip()]
    dropped, untexted, videos = [], 0, []
    keep = {}
    for aid, m in ads.items():
        if m["is_video"] and not a.include_video:
            videos.append(aid)
            continue
        blob = text_blob(m)
        if kws:
            if not blob.strip():
                untexted += 1
            elif not any(k in blob for k in kws):
                dropped.append(m)
                continue
        keep[aid] = m
    if kws:
        print(f"== Keyword filter {kws}: kept {len(keep)}, dropped {len(dropped)}"
              f"{f', {untexted} kept without caption text' if untexted else ''} ==")
        for t, n in sorted({(m['titles'][0] if m['titles'] else '(no title)'): 0 for m in dropped}.items()):
            cnt = sum(1 for m in dropped if (m['titles'][0] if m['titles'] else '(no title)') == t)
            print(f"  dropped x{cnt}: {t[:90]}")
    if videos:
        print(f"  skipped {len(videos)} video ads (out of scope; --include-video to keep)")

    # 3. images -----------------------------------------------------------------
    for spec in a.extra_image:
        if "=" not in spec:
            sys.exit(f"--extra-image needs ID=PATH, got {spec!r}")
        aid, path = spec.split("=", 1)
        aid = aid.strip()
        if not os.path.isfile(path):
            sys.exit(f"--extra-image file not found: {path}")
        with open(path, "rb") as f:
            data = f.read()
        dst = os.path.join(cache, f"{aid}__extra.{img_ext(data)}")
        with open(dst, "wb") as f:
            f.write(data)
        if aid in ads:
            keep[aid] = ads[aid]
        else:
            m = merge_rows([("--extra-image", {"id": aid, "status": None})])[aid]
            m["order"] = len(ads)
            keep[aid] = ads[aid] = m
    todo = list(keep.values())
    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        list(ex.map(lambda m: acquire(m, cache, a.offline), todo))
    got = [m for m in todo if m.get("img")]
    failed = [m for m in todo if not m.get("img")]
    by_kind = {}
    for m in got:
        by_kind[m["img"][0]] = by_kind.get(m["img"][0], 0) + 1
    print(f"== Images: {len(got)}/{len(todo)} ads have an image {by_kind}; "
          f"{len(failed)} without ==")
    errs = {}
    for m in failed:
        errs[m["img_error"]] = errs.get(m["img_error"], 0) + 1
    for e, n in errs.items():
        print(f"  x{n}: {e}")
    if not got:
        print("No image could be downloaded. If errors say expired, re-run the Brandsearch "
              "calls (URLs live 3 days) and run this script right after.")
        sys.exit(2)

    # 4. group: md5, then attach lower-quality images by perceptual match ---------
    groups = {}
    for m in got:
        with open(m["img"][1], "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()
        m["md5"] = h
        groups.setdefault(h, []).append(m)

    def best_kind(members):
        return min(KIND_ORDER[x["img"][0]] for x in members)

    sigs = {}

    def sig_of(members):
        rep = min(members, key=lambda x: KIND_ORDER[x["img"][0]])
        key = rep["img"][1]
        if key not in sigs:
            sigs[key] = signature(key)
        return sigs[key]

    near_log, possible = [], []
    anchors = [h for h, ms in groups.items() if best_kind(ms) == 0]
    if not anchors:  # no original-size image at all: anchor on best available
        anchors = [h for h, ms in groups.items() if best_kind(ms) == min(best_kind(v) for v in groups.values())]
    weaker = sorted((h for h in groups if h not in anchors), key=lambda h: best_kind(groups[h]))
    for h in weaker:
        s = sig_of(groups[h])
        cands = sorted(((distance(s, sig_of(groups[t])), t) for t in anchors), key=lambda x: x[0])
        if cands and cands[0][0] < NEAR_T:
            dist, target = cands[0]
            if len(cands) > 1 and cands[1][0] < NEAR_T:
                possible.append((groups[target][0]["id"], groups[cands[1][1]][0]["id"], cands[1][0]))
            for x in groups[h]:
                x["matched"] = f"near:{dist:.3f}"
            near_log.append((groups[h][0]["id"], groups[h][0]["img"][0], dist, target))
            groups[target].extend(groups.pop(h))
        else:
            anchors.append(h)  # stays its own creative (new anchor for later weaker images)
            if cands and cands[0][0] < POSSIBLE_T:
                possible.append((groups[h][0]["id"], groups[cands[0][1]][0]["id"], cands[0][0]))
    if a.near_dup:
        hs = [h for h in groups if best_kind(groups[h]) == 0]
        for i, h1 in enumerate(hs):
            if h1 not in groups:
                continue
            for h2 in hs[i + 1:]:
                if h2 in groups and h1 in groups and distance(sig_of(groups[h1]), sig_of(groups[h2])) < NEAR_T:
                    near_log.append((groups[h2][0]["id"], "original", -1, h1))
                    groups[h1].extend(groups.pop(h2))
    else:  # report only (skipped on very large sets: O(n^2))
        hs = [h for h in groups if best_kind(groups[h]) == 0]
        hs = hs if len(hs) <= 400 else []
        for i, h1 in enumerate(hs):
            for h2 in hs[i + 1:]:
                dd = distance(sig_of(groups[h1]), sig_of(groups[h2]))
                if dd < NEAR_T:
                    possible.append((groups[h1][0]["id"], groups[h2][0]["id"], dd))

    # 5. rank -------------------------------------------------------------------
    entries = []
    for h, ms in groups.items():
        ms.sort(key=lambda x: (-x["days"], x["start"] or datetime.max,
                               KIND_ORDER[x["img"][0]], x["order"]))
        lead = ms[0]
        rep = min(ms, key=lambda x: (KIND_ORDER[x["img"][0]], x is not lead))
        with Image.open(rep["img"][1]) as im:
            w, hgt = im.size
        status = {}
        for x in ms:
            k = x["status"] or "unknown"
            status[k] = status.get(k, 0) + 1
        dup = max((x["duplicate_count"] or 0) for x in ms)
        starts = [x["start"] for x in ms if x["start"]]
        ends = [x["end"] for x in ms if x["end"]]
        entries.append({
            "rank": None, "file": None, "lead_id": lead["id"],
            "ids": [x["id"] for x in ms],
            "days": max(x["days"] for x in ms),
            "first_seen": min(starts).strftime("%Y-%m-%d") if starts else None,
            "last_seen": max(ends).strftime("%Y-%m-%d") if ends else None,
            "copies": len(ms), "duplicate_count": dup, "score": len(ms) + dup,
            "reach_rank": min((x["reach_rank"] for x in ms if x["reach_rank"] is not None), default=None),
            "eu_spend": max((x["eu_spend"] for x in ms if x["eu_spend"] is not None), default=None),
            "eu_reach": max((x["eu_reach"] for x in ms if x["eu_reach"] is not None), default=None),
            "status": status, "width": w, "height": hgt, "aspect": aspect_label(w, hgt),
            "image_source": rep["img"][0], "low_res": KIND_ORDER[rep["img"][0]] >= 3,
            "titles": uniq(t for x in ms for t in x["titles"]),
            "descriptions": uniq(t for x in ms for t in x["descriptions"] + x["bodies"]),
            "ctas": uniq(t for x in ms for t in x["ctas"]),
            "dashboard_url": lead["dashboard_url"],
            "members": [{"id": x["id"], "days": x["days"],
                         "start": x["start"].strftime("%Y-%m-%d") if x["start"] else None,
                         "end": x["end"].strftime("%Y-%m-%d") if x["end"] else None,
                         "status": x["status"], "duplicate_count": x["duplicate_count"],
                         "image": x["img"][0], "match": x.get("matched", "md5")} for x in ms],
            "_src": rep["img"][1],
        })
    # ties: still running (latest last_seen) first, then earliest first_seen, then id
    entries.sort(key=lambda e: e["lead_id"])
    entries.sort(key=lambda e: e["first_seen"] or "9999")
    entries.sort(key=lambda e: e["last_seen"] or "0000", reverse=True)
    def primary(e):
        if a.sort == "rank":
            rr = e.get("reach_rank")
            return (rr is None, rr if rr is not None else 0)
        if a.sort in ("spend", "reach"):
            v = e.get("eu_" + a.sort)
            return (v is None, -(v or 0))
        return (False, 0)
    entries.sort(key=lambda e: (primary(e), -e["days"], -e["score"]))
    if a.sort in ("spend", "reach") and all(e.get("eu_" + a.sort) is None for e in entries):
        print(f"WARNING: no eu_total_{a.sort} in the dumps (non-EU ads?) - order falls back to days running. Use --sort rank.")
    if a.sort == "rank" and all(e.get("reach_rank") is None for e in entries):
        print("WARNING: no reach_rank in the dumps - add 'reach_rank' to the fields of the Brandsearch calls. Order falls back to days running.")

    for fn in os.listdir(out):  # remove stale ranked files from earlier runs
        if re.match(r"^\d{2,3}_[^/\\]+\.(jpg|png|webp|gif)$", fn):
            os.remove(os.path.join(out, fn))
    width = max(2, len(str(max(a.top, 1))))
    for i, e in enumerate(entries, 1):
        e["rank"] = i
        if i <= a.top:
            ext = os.path.splitext(e["_src"])[1]
            e["file"] = f"{i:0{width}d}_{e['lead_id']}{ext}"
            shutil.copy2(e["_src"], os.path.join(out, e["file"]))
        e["cache_file"] = os.path.relpath(e.pop("_src"), out)
        for x in e["ids"]:
            ads[x]["group_rank"] = i

    # 6. missing images -----------------------------------------------------------
    missing = []
    for m in failed:
        mk = (primary({"reach_rank": m["reach_rank"], "eu_spend": m["eu_spend"], "eu_reach": m["eu_reach"]}),
              -m["days"], -(1 + (m["duplicate_count"] or 0)))
        pos = 1 + sum(1 for e in entries if (primary(e), -e["days"], -e["score"]) < mk)
        prio = "high" if pos <= 10 else ("low" if pos <= a.top else "skip")
        missing.append({"priority": prio,
            "id": m["id"], "days": m["days"],
            "start": m["start"].strftime("%Y-%m-%d") if m["start"] else None,
            "status": m["status"], "duplicate_count": m["duplicate_count"],
            "is_duplicate": m["is_duplicate"], "would_rank_about": pos,
            "reason": m["img_error"],
            "action": (f'download_ad(platform="meta", id="{m["id"]}") [1 credit], then re-run '
                       f'with --extra-image {m["id"]}=<blob path>') if prio != "skip"
                      else "skip: would rank below --top even as a unique creative",
        })
    for e in entries:
        if e["low_res"] and e["rank"] <= a.top:
            missing.append({
                "priority": "high" if e["rank"] <= 10 else "low",
                "id": e["lead_id"], "days": e["days"], "start": e["first_seen"],
                "status": None, "duplicate_count": e["duplicate_count"], "is_duplicate": None,
                "would_rank_about": e["rank"], "reason": "only a thumbnail was available (low-res)",
                "action": f'download_ad(platform="meta", id="{e["lead_id"]}") [1 credit], '
                          f're-run with --extra-image {e["lead_id"]}=<path>',
            })
    missing.sort(key=lambda x: x["would_rank_about"])

    # 7. write ------------------------------------------------------------------
    with open(os.path.join(out, "ranking.json"), "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=1, ensure_ascii=False)
    with open(os.path.join(out, "missing_images.json"), "w", encoding="utf-8") as f:
        json.dump({"note": "Ids without a usable image. Most are copies of creatives already "
                           "downloaded, so fetch only priority 'high' (would enter the top 10) "
                           "unless the top 30 must be complete. Free first: re-pull get_brand_ads "
                           "with other sort_by/status slices and re-run. download_ad costs 1 credit, "
                           "returns an inline 600px image; the harness saves it under tool-results "
                           "as mcp-claude_ai_Brandsearch-blob-*.jpg.",
                   "counts": {k: sum(1 for x in missing if x["priority"] == k)
                              for k in ("high", "low", "skip")},
                   "items": missing}, f, indent=1, ensure_ascii=False)
    merged_out = []
    for m in sorted(ads.values(), key=lambda m: m["order"]):
        merged_out.append({
            "id": m["id"], "status": m["status"], "days": m["days"],
            "start": m["start"].isoformat() if m["start"] else None,
            "end": m["end"].isoformat() if m["end"] else None,
            "end_estimated": m.get("end_estimated"), "total_active_time": m["tat"],
            "duplicate_count": m["duplicate_count"], "is_duplicate": m["is_duplicate"],
            "is_video": m["is_video"], "sources": m["sources"],
            "image": m.get("img", (None,))[0], "group_rank": m.get("group_rank"),
            "kept": m["id"] in keep, "titles": m["titles"], "ctas": m["ctas"],
        })
    with open(os.path.join(out, "merged_ads.json"), "w", encoding="utf-8") as f:
        json.dump(merged_out, f, indent=1, ensure_ascii=False)

    # copy summary: one entry per (title, description); CTA button variants counted inside
    caps = {}
    for e in entries:
        for x in e["members"]:
            m = ads[x["id"]]
            key = (" | ".join(m["titles"]) or "(no title)",
                   "\n\n".join(m["descriptions"] + m["bodies"]) or "(no description)")
            c = caps.setdefault(key, {"ads": 0, "ranks": set(), "ctas": {}})
            c["ads"] += 1
            c["ranks"].add(e["rank"])
            cta = ", ".join(m["ctas"]) or "(no CTA)"
            c["ctas"][cta] = c["ctas"].get(cta, 0) + 1
    total_ads = sum(c["ads"] for c in caps.values())
    lines = [f"# Ad copy summary - {len(caps)} distinct caption(s) across {total_ads} ads / "
             f"{len(entries)} creatives", ""]
    for n, ((t, d), v) in enumerate(sorted(caps.items(), key=lambda kv: -kv[1]["ads"]), 1):
        rk = sorted(v["ranks"])
        ctas = "; ".join(f"{k} x{c}" for k, c in sorted(v["ctas"].items(), key=lambda kv: -kv[1]))
        lines += [f"## Caption {n}: {v['ads']} ads, {len(rk)} creatives (ranks {compact_ranks(rk)})",
                  f"- Title: {t}", f"- CTA buttons: {ctas}",
                  f"- Description ({len(d.split())} words):", "", "```", d, "```", ""]
    if caps:
        top_share = max(v["ads"] for v in caps.values()) / max(total_ads, 1)
        if top_share >= 0.9:
            lines.insert(2, f"> One caption runs on {top_share:.0%} of ads with images: the brand "
                            "locks the copy and tests creatives (and CTA buttons). Capture it as "
                            "the copy framework.\n")
    summary_md = "\n".join(lines)
    with open(os.path.join(out, "copy_summary.md"), "w", encoding="utf-8") as f:
        f.write(summary_md)

    sheets = build_sheets([e for e in entries if e["file"]], out, a.sheet_per) if a.sheet else []

    # 8. report -----------------------------------------------------------------
    print(f"== Groups: {len(got)} images -> {len(entries)} unique creatives "
          f"({len(near_log)} attached by perceptual match) ==")
    for aid, kind, dist, target in near_log:
        print(f"  attached {aid} ({kind}, d={dist:.3f}) -> group of {groups[target][0]['id']}")
    for x, y, dd in possible:
        print(f"  CHECK possible near-duplicate: {x} ~ {y} (d={dd:.3f}) - eyeball; --near-dup merges")
    print(f"== Ranking (top {min(a.top, len(entries))}) - sort={a.sort}, then days desc, copies+dup desc ==")
    print(f"{'#':>3} {'rrank':>5} {'days':>5} {'cop':>3} {'dup':>3} {'first':>10} {'size':>9} {'src':>8}  lead_id / ids")
    for e in entries[:a.top]:
        others = [i for i in e["ids"] if i != e["lead_id"]]
        rr = e.get("reach_rank")
        print(f"{e['rank']:>3} {rr if rr is not None else '-':>5} {e['days']:>5g} {e['copies']:>3} {e['duplicate_count']:>3} "
              f"{e['first_seen'] or '-':>10} {str(e['width']) + 'x' + str(e['height']):>9} "
              f"{e['image_source']:>8}  {e['lead_id']}" + (f" (+{', '.join(others)})" if others else ""))
    pc = {k: sum(1 for x in missing if x["priority"] == k) for k in ("high", "low", "skip")}
    print(f"== Missing images: {len(missing)} (missing_images.json) - priority high {pc['high']} "
          f"(would enter top 10), low {pc['low']} (top {a.top}), skip {pc['skip']} ==")
    for x in missing:
        if x["priority"] == "high":
            print(f"  HIGH {x['id']}: {x['days']:g}d, would rank ~#{x['would_rank_about']} - {x['reason']}")
    print()
    print(summary_md if len(summary_md) < 6000 else summary_md[:6000] + "\n...(truncated, see copy_summary.md)")
    if sheets:
        print("== Sheets ==")
        for p in sheets:
            print("  " + p)
    print(f"Done -> {out}")


def compact_ranks(rk):
    if not rk:
        return "-"
    out, s, p = [], rk[0], rk[0]
    for r in rk[1:] + [None]:
        if r is not None and r == p + 1:
            p = r
            continue
        out.append(f"{s}" if s == p else f"{s}-{p}")
        if r is not None:
            s = p = r
    return ", ".join(out)


if __name__ == "__main__":
    main()
