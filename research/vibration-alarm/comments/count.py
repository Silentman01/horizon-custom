import json, os, collections
os.chdir(os.path.dirname(os.path.abspath(__file__)))
C = {}
for l in open("comments_all.jsonl", encoding="utf-8"):
    if l.strip():
        r = json.loads(l)
        C[r["id"]] = r
T = [json.loads(l) for l in open("tags.jsonl", encoding="utf-8") if l.strip()]
meta = json.load(open("ads_meta.json", encoding="utf-8"))
out = {}
for ch in ("instagram_api", "trustpilot"):
    ids = [i for i in C if C[i]["channel"] == ch]
    tg = collections.Counter()
    ob = collections.Counter()
    for t in T:
        if t["id"] in ids:
            tg.update(t["tags"])
            if t["objection"]:
                ob[t["objection"]] += 1
    out[ch] = {"total": len(ids), "tag_counts": dict(tg), "objection_labels": dict(ob.most_common())}
tp = [C[i] for i in C if C[i]["channel"] == "trustpilot"]
out["trustpilot"]["reviewer_countries"] = dict(collections.Counter(r.get("country") for r in tp))
out["trustpilot"]["star_counts"] = dict(collections.Counter(r.get("stars") for r in tp))
out["trustpilot"]["sample_bias"] = "1-2 star filter page (20) + page 2 mixed (17 new); NOT a random sample"
out["trustpilot"]["comments_with_objection"] = sum(1 for t in T if t["objection"])
out["ad_engagement_adspy"] = {"ads": len(meta), "ig_likes": sum(m["adspy_ig_likes"] for m in meta),
                              "ig_comments": sum(m["adspy_ig_comments"] for m in meta)}
out["intent_ratio"] = "n/a (no ad comments)"
out["intent_over_engagement"] = "n/a (no ad comments)"
out["shipping_geo_counts"] = {}
out["age_split_by_ad_life"] = "n/a (no ad comments)"
json.dump(out, open("counts.json", "w"), indent=1)
print(json.dumps(out, indent=1))
