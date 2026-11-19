import json, collections, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
C = {}; T = {}
for l in open("comments_all.jsonl", encoding="utf-8"):
    if l.strip(): x = json.loads(l); C[x["id"]] = x
for l in open("tags.jsonl", encoding="utf-8"):
    if l.strip(): x = json.loads(l); T[x["id"]] = x
out = {"total": len(C), "by_channel": collections.Counter(c["channel"] for c in C.values())}
out["api_comments"] = out["by_channel"].get("instagram_api", 0)
out["tags"] = collections.Counter(t for x in T.values() for t in x["tags"])
out["objections"] = collections.Counter(x["objection"] for x in T.values() if x["objection"])
out["countries_asked_shipping"] = collections.Counter(x["country"] for x in T.values() if x["country"] and "shipping_geo" in x["tags"])
out["intent_ratio"] = "n/a (no ad comments)" if out["api_comments"] == 0 else None
out["saturation_signal_count"] = out["tags"].get("saturation", 0)
out["per_ad_age_split"] = "n/a (no API comments)"
for k in list(out):
    if isinstance(out[k], collections.Counter): out[k] = dict(out[k])
json.dump(out, open("counts.json", "w"), indent=1)
print(json.dumps(out, indent=1))
