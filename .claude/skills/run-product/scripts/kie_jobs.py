"""Run a batch of Kie.ai image jobs defined in a JSON file and download the results.

Usage:
  python -I kie_jobs.py jobs.json OUT_DIR
  python -I kie_jobs.py --credits            # print the account balance and exit

jobs.json: [{"name": "...", "model": "gpt-image-2-5-sunburst-image-to-image",
             "input": {"prompt": "...", "aspect_ratio": "1:1", "resolution": "2K"},
             "upload": {"field": "input_urls", "files": ["local/ref1.png", "local/packshot.png"]}}]
Local files in "upload.files" are uploaded (Kie temp storage, 24 h) and prepended to input[field].
Results are saved as OUT_DIR/<name>.<ext>; Kie deletes generated files after 14 days, so keep the downloads.
Reads KIE_API_KEY from the environment.
"""
import argparse, base64, json, mimetypes, os, sys, time, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser(description="Batch Kie.ai GPT Image jobs: upload refs, create tasks, poll, download.")
ap.add_argument("jobs", nargs="?", help="jobs JSON file")
ap.add_argument("out", nargs="?", help="output directory")
ap.add_argument("--credits", action="store_true", help="print the Kie credit balance and exit")
args = ap.parse_args()
KEY = os.environ.get("KIE_API_KEY")
if not KEY:
    sys.exit("KIE_API_KEY is not set (export it or prefix the command: KIE_API_KEY=... python -I kie_jobs.py ...)")


def api(method, url, body=None):
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(req, data, timeout=120) as r:
        return json.loads(r.read())


if args.credits:
    print("Kie credits:", api("GET", "https://api.kie.ai/api/v1/chat/credit").get("data"))
    sys.exit(0)
if not (args.jobs and args.out):
    ap.error("jobs and out are required (or use --credits)")
jobs = json.load(open(args.jobs, encoding="utf8"))
OUT = args.out
os.makedirs(OUT, exist_ok=True)

_uploaded = {}
def upload(path):
    if path not in _uploaded:
        mime = mimetypes.guess_type(path)[0] or "image/png"
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        res = api("POST", "https://kieai.redpandaai.co/api/file-base64-upload", {
            "base64Data": f"data:{mime};base64,{b64}",
            "uploadPath": "images/run-product", "fileName": os.path.basename(path)})
        assert res.get("code") == 200, res
        _uploaded[path] = res["data"]["downloadUrl"]
    return _uploaded[path]


pending = {}
for job in jobs:
    inp = dict(job["input"])
    up = job.get("upload")
    if up:
        inp[up["field"]] = [upload(p) for p in up["files"]] + inp.get(up["field"], [])
        if job.get("first_url"):
            inp[up["field"]].insert(0, job["first_url"])
    res = api("POST", "https://api.kie.ai/api/v1/jobs/createTask", {"model": job["model"], "input": inp})
    if res.get("code") != 200:
        print(f"{job['name']}: create failed {res}"); continue
    pending[job["name"]] = res["data"]["taskId"]
    print(f"{job['name']}: task {pending[job['name']]}")
    time.sleep(0.6)

deadline = time.time() + 900
while pending and time.time() < deadline:
    time.sleep(5)
    for name, tid in list(pending.items()):
        try:
            res = api("GET", f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={tid}")
        except Exception as e:
            continue
        d = res.get("data") or {}
        if res.get("code") != 200:
            print(name, "error", res.get("msg")); pending.pop(name)
        elif d.get("state") == "success":
            url = d["response"]["resultUrls"][0]
            ext = os.path.splitext(url.split("?")[0])[1] or ".png"
            dest = os.path.join(OUT, name + ext)
            urllib.request.urlretrieve(url, dest)
            print(f"{name}: saved {dest} ({d.get('creditsConsumed')} credits)")
            pending.pop(name)
        elif d.get("state") == "fail":
            print(f"{name}: FAILED {d.get('failCode')} {d.get('failMsg')}"); pending.pop(name)
for name in pending:
    print(f"{name}: timed out, task {pending[name]}")
