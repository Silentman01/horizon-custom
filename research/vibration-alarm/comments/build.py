import json, glob, os
from datetime import datetime, timezone
os.chdir(os.path.dirname(os.path.abspath(__file__)))
seen = {}
for f in sorted(glob.glob("raw_*_p*.json")):
    ad = f.split("_")[1]
    d = json.load(open(f, encoding="utf-8"))
    for c in d.get("data", []):
        i = "instagram_api_" + str(c.get("id", c["text"][:30]))
        if i in seen:
            continue
        seen[i] = dict(id=i, ad_id=ad, brand_id=None, text=c["text"], like_count=c.get("like_count"),
                       created_at=datetime.fromtimestamp(c["created_at"], timezone.utc).date().isoformat(),
                       channel="instagram_api")
for r in json.load(open("web_quotes.json", encoding="utf-8")):
    seen.setdefault(r["id"], r)
open("comments_all.jsonl", "w", encoding="utf-8").write("\n".join(json.dumps(v, ensure_ascii=False) for v in seen.values()) + "\n")
print(len(seen))
