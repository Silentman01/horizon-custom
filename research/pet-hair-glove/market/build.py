import json,csv,statistics as st
d=json.load(open('market_softpet.json'))['sellers']
with open('sellers.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['brand_id','url','price_usd','total_ads','active_ads','first_advertised_at','est_daily_spend_usd','countries'])
    for r in d:w.writerow(r)
p=[r[2] for r in d]
print('ES market sellers',len(d),'price min/med/max',min(p),st.median(p),max(p),'active ads',sum(r[4] for r in d),'total',sum(r[3] for r in d))
s=json.load(open('similar.json'))['similar_and_search']
with open('lookalikes.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['brand','country','currency','price_usd','total_ads','active_ads','note']);[w.writerow(r+['']*(7-len(r))) for r in s]
print('lookalike stores',len(s),'with active ads',sum(1 for r in s if r[5]>0))
