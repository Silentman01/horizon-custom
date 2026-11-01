"""ArgoLink image-to-video batch runner (first-frame animation).

Usage:
  python -I video_argolink.py jobs.json OUT_DIR [--workers 3] [--model minimax-h3] [--resolution 768p]

jobs.json: [{"name": "s01", "image": "frames/s01.png", "prompt": "...", "duration": 4,
             "model": "minimax-h3"?, "resolution": "768p"?}]
- Local images are uploaded through /v1/media/uploads, then sent as start_image.url.
- Polls /v1/videos/{id} every 12 s; downloads to OUT_DIR/<name>.mp4. Existing outputs are skipped.
- Cost is logged per job (rate table below; failed / expired tasks are free) and summed in OUT_DIR/cost.json.
Key: ARGOLINK_API_KEY env, else D:/Ecom/Products/.secrets/argolink.env.
Every prompt for a worn-product shot must carry the brand's PRODUCT FIT SPEC sentence.
"""
import argparse, concurrent.futures as cf, json, mimetypes, os, sys, time, urllib.error, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
API = "https://argolink.io/v1"
RATES = {("minimax-h3", "768p"): 0.039, ("minimax-h3", "2k"): 0.064,
         ("wan-3", "480p"): 0.038, ("wan-3", "720p"): 0.075, ("wan-3", "1080p"): 0.15,
         ("wan-3-prime", "720p"): 0.11, ("seedance-2.0-fast", "720p"): 0.103,
         ("grok-imagine-video-1.5", "720p"): 0.056}


def key():
    k = os.environ.get("ARGOLINK_API_KEY")
    if k:
        return k
    for line in open("D:/Ecom/Products/.secrets/argolink.env", encoding="utf8"):
        if line.startswith("ARGOLINK_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("ARGOLINK_API_KEY not set")


KEY = key()


def req(method, url, body=None, raw=None, headers=None, timeout=120):
    h = {"Authorization": "Bearer " + KEY}
    data = None
    if body is not None:
        data = json.dumps(body).encode(); h["Content-Type"] = "application/json"
    if raw is not None:
        data = raw
    h.update(headers or {})
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError("HTTP %s %s: %s" % (e.code, url, e.read()[:600].decode("utf8", "replace")))


def upload(path, model):
    ctype = mimetypes.guess_type(path)[0] or "image/png"
    size = os.path.getsize(path)
    meta = json.loads(req("POST", API + "/media/uploads",
                          {"model": model, "type": "image", "content_type": ctype, "size_bytes": size}))
    put = urllib.request.Request(meta["upload_url"], data=open(path, "rb").read(), method="PUT",
                                 headers={"Content-Type": ctype})
    urllib.request.urlopen(put, timeout=300).read()
    return meta["media_url"]


def run(job, out_dir, d_model, d_res):
    dest = os.path.join(out_dir, job["name"] + ".mp4")
    if os.path.exists(dest):
        return job["name"], "skipped", 0.0
    model = job.get("model", d_model); res = job.get("resolution", d_res)
    dur = int(job.get("duration", 5))
    t0 = time.time()
    url = job["image"] if job["image"].startswith("http") else upload(job["image"], model)
    body = {"model": model, "prompt": job["prompt"], "duration": dur, "resolution": res,
            "aspect_ratio": "adaptive", "start_image": {"url": url}}
    rid = json.loads(req("POST", API + "/videos", body))["request_id"]
    while True:
        time.sleep(12)
        st = json.loads(req("GET", API + "/videos/" + rid))
        if st["status"] == "done":
            break
        if st["status"] in ("failed", "expired"):
            return job["name"], "FAILED %s" % st.get("error"), 0.0
    data = req("GET", API + "/videos/%s/content" % rid, timeout=600)
    with open(dest, "wb") as fh:
        fh.write(data)
    cost = RATES.get((model, res), 0) * (st.get("video", {}).get("duration") or dur)
    return job["name"], "saved %s (%s %s %ds, %.0fs, $%.3f)" % (dest, model, res, dur, time.time() - t0, cost), cost


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jobs"); ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--model", default="minimax-h3")
    ap.add_argument("--resolution", default="768p")
    ap.add_argument("--only", help="comma-separated job names")
    a = ap.parse_args()
    jobs = json.load(open(a.jobs, encoding="utf8"))
    if a.only:
        keep = set(a.only.split(",")); jobs = [j for j in jobs if j["name"] in keep]
    os.makedirs(a.out, exist_ok=True)
    total = 0.0
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(run, j, a.out, a.model, a.resolution) for j in jobs]
        for f in cf.as_completed(futs):
            try:
                name, msg, cost = f.result()
            except Exception as e:
                name, msg, cost = "?", "ERROR %s" % e, 0.0
            total += cost
            print("%s: %s" % (name, msg), flush=True)
    cpath = os.path.join(a.out, "cost.json")
    prev = json.load(open(cpath)) if os.path.exists(cpath) else {"total": 0.0, "runs": []}
    prev["runs"].append({"jobs": len(jobs), "cost": round(total, 3), "at": time.strftime("%Y-%m-%d %H:%M")})
    prev["total"] = round(prev["total"] + total, 3)
    json.dump(prev, open(cpath, "w"), indent=1)
    print("done: %d jobs, this run $%.3f, cumulative $%.3f" % (len(jobs), total, prev["total"]))


if __name__ == "__main__":
    main()
