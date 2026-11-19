import json,glob,os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rows={}
for f in glob.glob('raw_*_p*.json'):
    d=json.load(open(f,encoding='utf8'))
    ad=os.path.basename(f).split('_')[1]
    for c in d.get('data',d if isinstance(d,list) else []):
        rows[c['id']]={'id':c['id'],'ad_id':ad,'brand_id':c.get('brand_id'),'text':c['text'],'like_count':c.get('like_count'),'created_at':c.get('created_at')}
with open('comments_all.jsonl','w',encoding='utf8') as o:
    for r in rows.values(): o.write(json.dumps(r,ensure_ascii=False)+'\n')
print(len(rows),'comments')
