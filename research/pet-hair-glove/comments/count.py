import json, os, collections
os.chdir(os.path.dirname(os.path.abspath(__file__)))
com = {}
for l in open("comments_all.jsonl", encoding="utf-8"):
    r = json.loads(l); com[r["id"]] = r
tags = {}
for l in open("tags.jsonl", encoding="utf-8"):
    r = json.loads(l); tags[r["id"]] = r
meta = json.load(open("ads_meta.json", encoding="utf-8"))
out = {"channels": collections.Counter(c["channel"] for c in com.values()), "total": len(com)}
for ch in out["channels"]:
    ids = [i for i, c in com.items() if c["channel"] == ch]
    out["tags_" + ch] = dict(collections.Counter(t for i in ids for t in tags[i]["tags"]))
    out["objections_" + ch] = dict(collections.Counter(tags[i]["objection"] for i in ids if tags[i]["objection"]))
    out["countries_" + ch] = dict(collections.Counter(tags[i]["country"] for i in ids if tags[i]["country"]))
api = [i for i, c in com.items() if c["channel"] == "instagram_api"]
intent = sum("purchase_intent" in tags[i]["tags"] for i in api)
eng = sum(m.get("adspy_ig_likes", 0) + m.get("adspy_ig_comments", 0) for m in meta if m["ad_id"] in {com[i]["ad_id"] for i in api})
out["intent_comments"] = intent
out["intent_over_api_comments"] = (intent / len(api)) if api else None
out["ig_engagement_pulled_ads"] = eng
out["intent_over_engagement"] = (intent / eng) if eng else None
out["intent_ratio_note"] = "n/a (no ad comments with text beyond a heart-emoji tag and a self link)" if intent == 0 else ""
tp = [i for i, c in com.items() if c["channel"] == "trustpilot"]
stars = collections.Counter(com[i]["stars"] for i in tp)
out["trustpilot_star_counts"] = dict(stars)
out["trustpilot_share_negative_tags"] = {k: sum(k in tags[i]["tags"] for i in tp) for k in ("objection", "product_complaint", "service_complaint")}
out["age_split"] = "n/a: reviews are not tied to an ad start date; the 2 API comments are 2026-01-30..31 (ad started 2026-01-30)"
json.dump(out, open("counts.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
