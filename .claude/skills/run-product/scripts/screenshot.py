#!/usr/bin/env python3
"""Full-page desktop + mobile screenshots of a URL or local HTML file with headless Edge/Chrome.

Two engines (standard library only):
  cdp  (default) drives the browser over the DevTools protocol: real viewport + device emulation
       (390px mobile with an iPhone User-Agent), lazy-load scroll pass, true full-page capture.
       Works on shops that forbid framing (Shopify sends X-Frame-Options: DENY).
  cli  the browser's --screenshot flag with a WIDTH x --height window. Mobile goes through a 390px
       iframe wrapper (headless windows cannot be narrower than ~500px); sites that send
       X-Frame-Options / frame-ancestors come back blank, which is detected and reported.
With --engine auto, cdp is tried first and cli is the fallback.

Every capture is verified on disk (the browser exits 0 even when it writes nothing), the trailing
background is trimmed, then the shot is split for viewing.

Outputs in --out (prefix = "<name>-" when --name is given):
  desk.png, desk-01.jpg ...   full desktop shot + chunks (--chunk px tall, downscaled to --chunk-width)
  mob.png,  mob-01.jpg ...    full mobile shot + sheets (3 columns of 1300px side by side)

Usage:
  python -I screenshot.py https://plaims.com/products/plaims-headlight-glasses --out DIR
  python -I screenshot.py G:/tmp/page.html --out DIR --name ours --mobile 0      # desktop only
  python -I screenshot.py URL --out DIR --desktop 0 --engine cli                 # iframe mobile only
  python -I screenshot.py URL --out DIR --browser "C:/Program Files/Google/Chrome/Application/chrome.exe"
"""
import argparse
import base64
import glob
import json
import os
import shutil
import socket
import ssl
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image, ImageChops

Image.MAX_IMAGE_PIXELS = None

DESKTOP_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0")
MOBILE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
             "Version/17.5 Mobile/15E148 Safari/604.1")
SCROLL_JS = """(async () => {
  const H = () => Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0);
  for (let y = 0; y < H() && y < %d; y += Math.round(innerHeight * 0.8)) {
    window.scrollTo(0, y); await new Promise(r => setTimeout(r, 150));
  }
  window.scrollTo(0, H()); await new Promise(r => setTimeout(r, 400));
  window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 600));
  return H();
})()"""


def find_browser(explicit):
    if explicit:
        if Path(explicit).is_file():
            return explicit
        sys.exit(f"ERROR: --browser not found: {explicit}")
    roots = [os.environ.get(k) for k in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA")]
    cands = [os.path.join(r, sub) for r in roots if r for sub in (
        r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe")]
    cands += [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    cands += [shutil.which(n) or "" for n in ("msedge", "microsoft-edge", "google-chrome", "chrome",
                                              "chromium", "chromium-browser")]
    for c in cands:
        if c and Path(c).is_file():
            return c
    sys.exit("ERROR: no Edge/Chrome found; pass --browser PATH")


def to_url(target):
    if "://" in target:
        return target
    p = Path(target).resolve()
    if not p.exists():
        sys.exit(f"ERROR: file not found: {target}")
    return p.as_uri()


def framing_blocked(url):
    """True/False when response headers forbid/allow iframes; None when unknown."""
    if not url.startswith("http"):
        return False
    try:
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": DESKTOP_UA})
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            xfo = (r.headers.get("X-Frame-Options") or "").lower()
            csp = (r.headers.get("Content-Security-Policy") or "").lower()
    except Exception:
        return None
    fa = csp.split("frame-ancestors", 1)[1].split(";")[0] if "frame-ancestors" in csp else ""
    return xfo in ("deny", "sameorigin") or ("frame-ancestors" in csp and "*" not in fa)


def new_profile(out):
    root = out / ".browser-profiles"
    root.mkdir(exist_ok=True)
    return tempfile.mkdtemp(prefix="p-", dir=root)


def drop_profile(prof):
    for _ in range(5):
        shutil.rmtree(prof, ignore_errors=True)
        if not os.path.exists(prof):
            break
        time.sleep(0.5)


# ---------------------------------------------------------------- CDP engine

class CDP:
    """Minimal DevTools-protocol client over a raw WebSocket."""

    def __init__(self, ws_url, timeout=60):
        u = urlsplit(ws_url)
        self.sock = socket.create_connection((u.hostname, u.port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\n"
                           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("websocket handshake failed")
            resp += chunk
        head, rest = resp.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise ConnectionError(head.decode(errors="ignore")[:200])
        self.buf = bytearray(rest)
        self.msg_id = 0
        self.events = []

    def _exact(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(max(1 << 16, n - len(self.buf)))
            if not chunk:
                raise ConnectionError("devtools socket closed")
            self.buf += chunk
        data = bytes(self.buf[:n])
        del self.buf[:n]
        return data

    def _send(self, text, opcode=0x1):
        payload = text.encode() if isinstance(text, str) else text
        n = len(payload)
        hdr = bytearray([0x80 | opcode])
        if n < 126:
            hdr.append(0x80 | n)
        elif n < 65536:
            hdr += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            hdr += bytes([0x80 | 127]) + struct.pack(">Q", n)
        mask = os.urandom(4)
        self.sock.sendall(bytes(hdr) + mask + bytes(b ^ mask[i & 3] for i, b in enumerate(payload)))

    def _recv(self):
        parts = []
        while True:
            b1, b2 = self._exact(2)
            op, n = b1 & 0x0F, b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._exact(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._exact(8))[0]
            mask = self._exact(4) if b2 & 0x80 else None
            data = self._exact(n)
            if mask:
                data = bytes(b ^ mask[i & 3] for i, b in enumerate(data))
            if op == 0x8:
                raise ConnectionError("devtools closed the connection")
            if op == 0x9:
                self._send(data, 0xA)
                continue
            if op == 0xA:
                continue
            parts.append(data)
            if b1 & 0x80:
                return json.loads(b"".join(parts))

    def call(self, method, timeout=90, **params):
        self.msg_id += 1
        mid = self.msg_id
        self.sock.settimeout(timeout)
        self._send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = self._recv()
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error'].get('message')}")
                return msg.get("result", {})
            if "method" in msg:
                self.events.append(msg["method"])

    def wait_event(self, name, timeout):
        end = time.time() + timeout
        while name not in self.events:
            left = end - time.time()
            if left <= 0:
                return False
            self.sock.settimeout(left)
            try:
                msg = self._recv()
            except socket.timeout:
                return False
            if "method" in msg:
                self.events.append(msg["method"])
        return True


def cdp_capture(browser, url, width, mobile, max_h, wait_ms, out_png, out_dir):
    prof = new_profile(out_dir)
    proc = subprocess.Popen([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                             "--no-default-browser-check", "--disable-extensions", "--disable-sync",
                             "--remote-debugging-port=0", f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cdp = None
    try:
        port_file = Path(prof, "DevToolsActivePort")
        end = time.time() + 30
        while time.time() < end and not (port_file.exists() and len(port_file.read_text().split()) >= 2):
            time.sleep(0.2)
        if not port_file.exists():
            raise RuntimeError("browser did not open a DevTools port")
        port = int(port_file.read_text().split()[0])
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        targets = json.loads(opener.open(f"http://127.0.0.1:{port}/json/list", timeout=10).read())
        page = next(t for t in targets if t.get("type") == "page")
        cdp = CDP(page["webSocketDebuggerUrl"])
        vh = 844 if mobile else 900
        cdp.call("Emulation.setDeviceMetricsOverride", width=width, height=vh, deviceScaleFactor=1, mobile=mobile)
        cdp.call("Emulation.setUserAgentOverride", userAgent=MOBILE_UA if mobile else DESKTOP_UA)
        if mobile:
            cdp.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
        cdp.call("Page.enable")
        cdp.call("Page.navigate", url=url)
        if not cdp.wait_event("Page.loadEventFired", 60):
            print("  note: load event not fired within 60s, capturing anyway")
        time.sleep(wait_ms / 2000)
        cdp.call("Runtime.evaluate", expression=SCROLL_JS % max_h, awaitPromise=True, returnByValue=True, timeout=180)
        time.sleep(wait_ms / 2000)
        m = cdp.call("Page.getLayoutMetrics")
        size = m.get("cssContentSize") or m.get("contentSize")
        full_h = int(size["height"])
        h = min(full_h, max_h)
        shot = cdp.call("Page.captureScreenshot", format="png", captureBeyondViewport=True, fromSurface=True,
                        clip={"x": 0, "y": 0, "width": width, "height": h, "scale": 1}, timeout=180)
        Path(out_png).write_bytes(base64.b64decode(shot["data"]))
        return full_h
    finally:
        if cdp:
            try:
                cdp.call("Browser.close", timeout=10)
            except Exception:
                pass
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.kill()
        drop_profile(prof)


# ---------------------------------------------------------------- CLI engine

def cli_shot(browser, url, width, height, wait_ms, out_png, out_dir):
    out_png = Path(out_png)
    for attempt in (1, 2):
        if out_png.exists():
            out_png.unlink()
        prof = new_profile(out_dir)
        cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               "--no-default-browser-check", "--disable-extensions", "--disable-sync",
               f"--user-data-dir={prof}", "--force-device-scale-factor=1",
               f"--window-size={width},{height}", f"--virtual-time-budget={wait_ms}",
               f"--screenshot={out_png.resolve()}", url]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=wait_ms / 1000 + 120)
        except subprocess.TimeoutExpired:
            print(f"  note: browser timed out (attempt {attempt})")
        drop_profile(prof)
        if out_png.exists() and out_png.stat().st_size > 0:
            return True
        print(f"  note: browser wrote no screenshot (attempt {attempt})")
    return False


def cli_mobile(browser, url, width, height, wait_ms, out_png, out_dir, prefix):
    wrap = out_dir / f"{prefix}mobile-wrap.html"
    wrap.write_text(f'<!doctype html><html><body style="margin:0;background:#fff"><iframe src="{url}" '
                    f'style="width:{width}px;height:{height}px;border:0;display:block"></iframe></body></html>',
                    encoding="utf-8")
    ok = cli_shot(browser, wrap.resolve().as_uri(), max(width + 120, 520), height, wait_ms, out_png, out_dir)
    if ok:
        im = Image.open(out_png).convert("RGB")
        im.crop((0, 0, width, im.height)).save(out_png)
    return ok


# ---------------------------------------------------------------- post-processing

def content_ratio(im):
    small = im.resize((max(1, im.width // 8), max(1, im.height // 8)))
    colors = small.getcolors(small.width * small.height)
    dom = max(colors)[1]
    diff = ImageChops.difference(small, Image.new("RGB", small.size, dom)).convert("L").point(lambda v: 255 if v > 16 else 0)
    return diff.histogram()[255] / (small.width * small.height)


def trim(im):
    """Crop the trailing page background. Returns (image, removed_px) or (None, 0) when blank."""
    bg = im.getpixel((2, im.height - 2))
    diff = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L").point(lambda v: 255 if v > 12 else 0)
    box = diff.getbbox()
    if not box:
        return None, 0
    bottom = min(im.height, box[3] + 30)
    return im.crop((0, 0, im.width, bottom)), im.height - bottom


def clear_old(out, stem):
    for f in glob.glob(str(out / f"{stem}-[0-9][0-9].jpg")):
        os.remove(f)


def desktop_chunks(im, out, stem, chunk, chunk_w):
    clear_old(out, stem)
    files = []
    for i, top in enumerate(range(0, im.height, chunk), 1):
        c = im.crop((0, top, im.width, min(top + chunk, im.height)))
        if chunk_w and im.width > chunk_w:
            c = c.resize((chunk_w, max(1, round(c.height * chunk_w / im.width))), Image.LANCZOS)
        p = out / f"{stem}-{i:02d}.jpg"
        c.save(p, quality=85)
        files.append(p)
    return files


def mobile_sheets(im, out, stem, col_h=1300, cols=3, gap=12):
    clear_old(out, stem)
    pieces = [im.crop((0, t, im.width, min(t + col_h, im.height))) for t in range(0, im.height, col_h)]
    files = []
    for s in range(0, len(pieces), cols):
        group = pieces[s:s + cols]
        sheet = Image.new("RGB", (cols * im.width + (cols - 1) * gap, col_h), (200, 200, 200))
        for j, c in enumerate(group):
            sheet.paste(c, (j * (im.width + gap), 0))
        p = out / f"{stem}-{s // cols + 1:02d}.jpg"
        sheet.save(p, quality=85)
        files.append(p)
    return files


def finish(png, kind, args, out, prefix, page_h=None):
    """Trim, check blankness, split. Returns list of files or None on failure."""
    im = Image.open(png).convert("RGB")
    ratio = content_ratio(im)
    trimmed, removed = trim(im)
    if trimmed is None or ratio < 0.005:
        print(f"WARNING: {kind} screenshot is blank ({ratio:.1%} non-background pixels)")
        return None
    trimmed.save(png)
    limit = args.height
    if page_h and page_h > limit:
        print(f"WARNING: page is {page_h}px tall; captured the first {limit}px (raise --height)")
    elif page_h is None and removed < 40:
        print(f"WARNING: no trailing background found; page may be longer than --height {limit}")
    stem = f"{prefix}{'desk' if kind == 'desktop' else 'mob'}"
    extra = desktop_chunks(trimmed, out, stem, args.chunk, args.chunk_width) if kind == "desktop" \
        else mobile_sheets(trimmed, out, stem)
    print(f"{kind:8}: {png.name} {trimmed.width}x{trimmed.height}  ({len(extra)} view file(s))")
    return [png] + extra


def run(kind, width, args, browser, url, out, prefix):
    png = out / f"{prefix}{'desk' if kind == 'desktop' else 'mob'}.png"
    if png.exists():
        png.unlink()
    mobile = kind == "mobile"
    if args.engine in ("auto", "cdp"):
        try:
            page_h = cdp_capture(browser, url, width, mobile, args.height, args.wait, png, out)
            if png.exists() and png.stat().st_size > 0:
                res = finish(png, kind, args, out, prefix, page_h)
                if res:
                    return res, "cdp"
        except Exception as e:
            print(f"  note: cdp engine failed for {kind}: {e}")
        if args.engine == "cdp":
            return None, "cdp"
        print(f"  falling back to cli engine for {kind}")
    if mobile:
        blocked = framing_blocked(url)
        if blocked:
            print("WARNING: the site forbids iframes (X-Frame-Options / CSP frame-ancestors); "
                  "the 390px iframe capture will likely be blank")
        ok = cli_mobile(browser, url, width, args.height, args.wait, png, out, prefix)
    else:
        ok = cli_shot(browser, url, width, args.height, args.wait, png, out)
    if not ok:
        print(f"ERROR: browser produced no {kind} screenshot")
        return None, "cli"
    res = finish(png, kind, args, out, prefix)
    if res is None and mobile:
        print("WARNING: mobile capture failed (iframe blocked). Use --engine cdp, or rely on the desktop shot "
              "plus the theme's known mobile behaviour.")
    return res, "cli"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="URL (http/https/file) or local HTML file")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--desktop", type=int, default=1440, help="desktop width, 0 to skip (default 1440)")
    ap.add_argument("--mobile", type=int, default=390, help="mobile width, 0 to skip (default 390)")
    ap.add_argument("--height", type=int, default=14000, help="max capture height in px (default 14000)")
    ap.add_argument("--name", default="", help="file prefix, e.g. 'competitor' -> competitor-desk.png")
    ap.add_argument("--browser", help="path to msedge.exe / chrome.exe (auto-detected)")
    ap.add_argument("--wait", type=int, default=8000, help="settle time in ms for JS/lazy content (default 8000)")
    ap.add_argument("--engine", choices=("auto", "cdp", "cli"), default="auto", help="capture engine (default auto)")
    ap.add_argument("--chunk", type=int, default=2400, help="desktop chunk height in px (default 2400)")
    ap.add_argument("--chunk-width", type=int, default=720, help="desktop chunk width after downscale (default 720)")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    browser = find_browser(args.browser)
    url = to_url(args.target)
    prefix = f"{args.name}-" if args.name else ""
    print(f"Browser : {browser}\nTarget  : {url}")

    results, failed = {}, []
    for kind, width in (("desktop", args.desktop), ("mobile", args.mobile)):
        if width <= 0:
            continue
        files, engine = run(kind, width, args, browser, url, out, prefix)
        if files:
            results[kind] = (files, engine)
        else:
            failed.append(kind)
    shutil.rmtree(out / ".browser-profiles", ignore_errors=True)

    print("\nFiles:")
    for kind, (files, engine) in results.items():
        print(f"  [{kind}, engine {engine}]")
        for f in files:
            print(f"    {f}")
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
