"""Run a batch of ArgoLink GPT Image jobs (default gpt-image-2.5-sunburst) defined in a JSON file and save the results.

Drop-in replacement for kie_jobs.py: it reads the same jobs.json format.

Usage:
  python -I argolink_jobs.py jobs.json OUT_DIR [--workers 6] [--quality high] [--model gpt-image-2.5-sunburst] [--cap 0.15]
  python -I argolink_jobs.py --check          # one tiny paid test call ($0.015) to verify the key

jobs.json: [{"name": "...",
             "input": {"prompt": "...", "aspect_ratio": "1:1", "resolution": "2K"},   # or "size": "1024x1280"
             "upload": {"field": "input_urls", "files": ["local/ref1.png", "local/packshot.png"]}}]
- --model picks the ArgoLink image model (gpt-image-2.5-sunburst default, operator 2026-11-19; gpt-image-2 and
  gpt-image-2.6-sunburst also exist; Flare variants once printed the competitor's name on our label). The job's own
  "model" field is ignored. --cap stops starting new jobs once the approved budget would be exceeded (00 §20). Jobs with reference files (upload.files or input.input_urls / image_urls)
  go to /v1/images/edits (up to 16 refs); jobs without go to /v1/images/generations.
- aspect_ratio + resolution are mapped to pixel sizes (see SIZES); input.size overrides them.
- Calls are synchronous (up to ~10 min each), so jobs run in parallel threads.
- Existing OUT_DIR/<name>.png files are skipped. Pricing: $0.015 per image up to 2K, $0.02 above (failed = free).
Reads ARGOLINK_API_KEY from the environment, else from D:/Ecom/Products/.secrets/argolink.env.
"""
import argparse, base64, concurrent.futures as cf, json, mimetypes, os, sys, time, urllib.request, urllib.error

sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser(description="Batch ArgoLink GPT Image jobs (kie_jobs.py-compatible job files).")
ap.add_argument("jobs", nargs="?", help="jobs JSON file")
ap.add_argument("out", nargs="?", help="output directory")
ap.add_argument("--workers", type=int, default=6, help="parallel requests (default 6)")
ap.add_argument("--quality", default="high", choices=["auto", "low", "medium", "high"])
ap.add_argument("--model", default="gpt-image-2.5-sunburst", help="ArgoLink image model (default gpt-image-2.5-sunburst)")
ap.add_argument("--cap", type=float, default=None, help="approved budget in USD; no new job starts once it would be exceeded")
ap.add_argument("--check", action="store_true", help="run one 1024x1024 low-quality test image and exit")
args = ap.parse_args()

KEY = os.environ.get("ARGOLINK_API_KEY")
if not KEY:
    p = "D:/Ecom/Products/.secrets/argolink.env"
    if os.path.exists(p):
        for line in open(p, encoding="utf8"):
            if line.startswith("ARGOLINK_API_KEY="):
                KEY = line.split("=", 1)[1].strip()
if not KEY:
    sys.exit("ARGOLINK_API_KEY is not set")
BASE = "https://argolink.io/v1/images"

# longest edge: 1K <= 1024, 2K <= 2048, 4K > 2048 (sides multiples of 16)
SIZES = {
    "1:1":  {"1K": "1024x1024", "2K": "1440x1440", "4K": "2160x2160"},
    "4:5":  {"1K": "1024x1280", "2K": "1632x2048", "4K": "2160x2704"},
    "5:4":  {"1K": "1280x1024", "2K": "2048x1632", "4K": "2704x2160"},
    "3:4":  {"1K": "960x1280",  "2K": "1536x2048", "4K": "2160x2880"},
    "4:3":  {"1K": "1280x960",  "2K": "2048x1536", "4K": "2880x2160"},
    "2:3":  {"1K": "1024x1536", "2K": "1360x2048", "4K": "2160x3248"},
    "3:2":  {"1K": "1536x1024", "2K": "2048x1360", "4K": "3248x2160"},
    "9:16": {"1K": "576x1024",  "2K": "1152x2048", "4K": "2160x3840"},
    "16:9": {"1K": "1024x576",  "2K": "2048x1152", "4K": "3840x2160"},
}


def post(endpoint, body):
    req = urllib.request.Request(f"{BASE}/{endpoint}", method="POST", data=json.dumps(body).encode(), headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:500].decode('utf8', 'ignore')}")


def data_url(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


def save(res, dest):
    item = (res.get("data") or [{}])[0]
    if item.get("b64_json"):
        open(dest, "wb").write(base64.b64decode(item["b64_json"]))
    elif item.get("url"):
        urllib.request.urlretrieve(item["url"], dest)
    else:
        raise RuntimeError(f"no image in response: {str(res)[:300]}")


if args.check:
    t = time.time()
    res = post("generations", {"model": args.model, "prompt": "A plain white ceramic cup on a light grey table, studio photo",
                               "size": "1024x1024", "quality": "low", "n": 1, "response_format": "b64_json"})
    dest = os.path.join(os.environ.get("TEMP", "."), "argolink_check.png")
    save(res, dest)
    print(f"OK {dest} in {time.time() - t:.0f}s (usage: {res.get('usage')})")
    sys.exit(0)
if not (args.jobs and args.out):
    ap.error("jobs and out are required (or use --check)")
jobs = json.load(open(args.jobs, encoding="utf8"))
os.makedirs(args.out, exist_ok=True)


import threading
_lock = threading.Lock()
_committed = [0.0]


def run(job):
    name = job["name"]
    dest = os.path.join(args.out, name + ".png")
    if os.path.exists(dest):
        return f"{name}: exists, skipped", 0
    inp0 = job.get("input", {})
    size0 = inp0.get("size") or SIZES.get(inp0.get("aspect_ratio", "1:1"), SIZES["1:1"]).get(inp0.get("resolution", "1K"), "1024x1024")
    est = 0.02 if max(int(x) for x in size0.split("x")) > 2048 else 0.015
    with _lock:
        if args.cap is not None and _committed[0] + est > args.cap + 1e-9:
            return f"{name}: SKIPPED (cap ${args.cap:.3f} reached; committed ${_committed[0]:.3f})", 0
        _committed[0] += est
    inp = job.get("input", {})
    size = inp.get("size") or SIZES.get(inp.get("aspect_ratio", "1:1"), SIZES["1:1"]).get(inp.get("resolution", "1K"), "1024x1024")
    refs = []
    up = job.get("upload") or {}
    refs += [data_url(p) for p in up.get("files", [])]
    for k in ("input_urls", "image_urls", "images"):
        refs += [u for u in inp.get(k, []) if isinstance(u, str)]
    if job.get("first_url"):
        refs.insert(0, job["first_url"])
    body = {"model": args.model, "prompt": inp["prompt"], "size": size,
            "quality": inp.get("quality", args.quality), "n": 1, "response_format": "b64_json"}
    t = time.time()
    for attempt in (1, 2):
        try:
            if refs:
                body["images"] = [{"image_url": u} for u in refs[:16]]
                res = post("edits", body)
            else:
                res = post("generations", body)
            save(res, dest)
            cost = 0.02 if max(int(x) for x in size.split("x")) > 2048 else 0.015
            return f"{name}: saved {dest} ({size}, {len(refs)} refs, {time.time() - t:.0f}s, ${cost})", cost
        except Exception as e:
            err = e
            time.sleep(5)
    with _lock:
        _committed[0] -= est  # failed generations are free
    return f"{name}: FAILED {err}", 0


total = 0.0
with cf.ThreadPoolExecutor(max(1, args.workers)) as ex:
    for msg, cost in ex.map(run, jobs):
        total += cost
        print(msg, flush=True)
print(f"done: {len(jobs)} jobs, model {args.model}, spent ${total:.3f}" + (f" (cap ${args.cap:.3f})" if args.cap is not None else ""))
