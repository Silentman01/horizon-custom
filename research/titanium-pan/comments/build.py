import glob,json
rows={}
for f in glob.glob('raw_*_p*.json'):
    d=json.load(open(f,encoding='utf8'));ad=f.split('_')[1]
    for c in d.get('data',[]): rows[c.get('id',c['text'])]={'id':c.get('id'),'ad_id':ad,'text':c['text'],'like_count':c.get('like_count'),'created_at':c.get('created_at')}
open('comments_all.jsonl','w',encoding='utf8').write(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows.values()))
