import json,csv,statistics as st
d=json.load(open('lookalikes_condensed.json',encoding='utf8'))
rows=d['rows']
with open('sellers.csv','w',newline='',encoding='utf8') as f:
    w=csv.writer(f);w.writerow(d['cols']);w.writerows(rows)
p=[r[2] for r in rows if r[2]<300]
act=[r for r in rows if r[4]>0]
print('stores',len(rows),'active',len(act),'price min/median/max',min(p),st.median(p),max(p))
print('active ads excluding rinsemate',sum(r[4] for r in rows[1:]))
