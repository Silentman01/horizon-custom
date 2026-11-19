import json,os
n=sum(1 for _ in open('comments_all.jsonl',encoding='utf8')) if os.path.exists('comments_all.jsonl') else 0
out={'comments_pulled':n,'tag_counts':{},'intent_ratio':'n/a (no ad comments)','ads_with_comments':0,'adspy_ig_engagement_of_probed_ads':37}
json.dump(out,open('counts.json','w'),indent=1)
print(out)
