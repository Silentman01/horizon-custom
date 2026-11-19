import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
U = "https://www.ibisik.com/?p=22977"
B = [("I noticed a slight reduction in tartar near my dog’s gum line.", ["objection"], "weak efficacy", "blogger test of Paw Guardian spray"),
("Results were modest rather than dramatic.", ["objection"], "weak efficacy", ""),
("Receiving four boxes when I only ordered one immediately made me worry about possible subscription charges", ["service_complaint", "objection"], "subscription/billing", "")]
raw = []; tags = []
for j, (t, tg, ob, n) in enumerate(B, 1):
    i = f"blog_{j}"
    raw.append(dict(id=i, channel="blog", source=U, ad_id=None, brand_id="paw-guardian.com", text=t, like_count=0, created_at="2026-11-19"))
    tags.append(dict(id=i, tags=tg, objection=ob, country=None, note=n))
json.dump(raw, open("raw_web_blog.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open("tags.jsonl", "w", encoding="utf-8").write("\n".join(json.dumps(t, ensure_ascii=False) for t in tags) + "\n")
