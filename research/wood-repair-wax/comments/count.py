import json,os,collections
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rd=lambda p:[json.loads(l) for l in open(p,encoding='utf8') if l.strip()] if os.path.exists(p) else []
cm=rd('comments_all.jsonl'); tg={t['id']:t for t in rd('tags.jsonl')}
tags=collections.Counter(x for t in tg.values() for x in t['tags'])
out={'total_comments':len(cm),'tag_counts':dict(tags),
 'intent_ratio':(tags['purchase_intent']/len(cm)) if cm else 'n/a (no ad comments)',
 'objection_labels':dict(collections.Counter(t['objection'] for t in tg.values() if t.get('objection'))),
 'countries':dict(collections.Counter(t['country'] for t in tg.values() if t.get('country'))),
 'ads_with_comments':0,'ads_probed_ig_matched':0}
json.dump(out,open('counts.json','w'),indent=1); print(out)
