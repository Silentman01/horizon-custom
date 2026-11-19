import json, glob, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
seen = {}; rows = []
for f in sorted(glob.glob("raw_*_p*.json")):  # Brandsearch comment pages (none returned text for this product)
    d = json.load(open(f, encoding="utf-8"))
    for c in d.get("data", []):
        if c["id"] in seen: continue
        seen[c["id"]] = 1
        rows.append(dict(id=c["id"], channel="instagram_api", ad_id=f.split("_")[1], brand_id=None, text=c["text"], like_count=c.get("like_count"), created_at=c.get("created_at")))
for r in json.load(open("raw_web_blog.json", encoding="utf-8")):
    if r["id"] not in seen:
        seen[r["id"]] = 1; rows.append(r)
open("comments_all.jsonl", "w", encoding="utf-8").write("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
print(len(rows))
