import json, glob, datetime, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
seen = set(); rows = []
for f in sorted(glob.glob("raw_*.json")):
    for c in json.load(open(f, encoding="utf-8"))["data"]:
        if c["id"] in seen:
            continue
        seen.add(c["id"])
        rows.append({"id": "instagram_api_" + c["id"], "channel": "instagram_api", "ad_id": c["ad_id"], "brand_id": "aurexco.in",
                     "text": c["text"], "like_count": c["like_count"],
                     "created_at": datetime.datetime.fromtimestamp(c["created_at"], datetime.timezone.utc).strftime("%Y-%m-%d")})
for r in json.load(open("web_reviews.json", encoding="utf-8")):
    rows.append({"id": r["id"], "channel": "trustpilot", "source": r["source"], "ad_id": None, "brand_id": r["brand_id"],
                 "text": r["text"], "like_count": 0, "stars": r["stars"], "created_at": r["created_at"]})
with open("comments_all.jsonl", "w", encoding="utf-8") as o:
    for r in rows:
        o.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(rows))
