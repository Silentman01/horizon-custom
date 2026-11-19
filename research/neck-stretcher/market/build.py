import json, csv, statistics
rows=[]
for f in ["market_monsori.nl_16292307009868.json","market_myspinea.com_15805788914037.json"]:
    d=json.load(open(f,encoding="utf-8"))
    for m in d["members"]:
        a=m["ads"]
        rows.append([m["brand_id"],m["url"],m["price_usd"],a["total"],a["active"],a["first_advertised_at"][:10],a["est_daily_spend_usd"],"",f.split("_")[1]])
c=json.load(open("cards_other_markets.json",encoding="utf-8"))
seen={r[0]+"|"+r[1] for r in rows}
for x in c["cards"]:
    rows.append([x[1],x[0],x[3],x[4],x[5],x[6][:10],x[7],x[12] if x[12] else "",x[14]])
rows.sort(key=lambda r:(-(r[4] or 0)))
with open("sellers.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.writer(fh); w.writerow(["brand_id","url_or_product_id","price_usd","total_ads","active_ads","first_advertised_at","est_daily_spend_usd","market_country_count","source"]); w.writerows(rows)
act=[r for r in rows if (r[4] or 0)>0]
pr=[r[2] for r in rows if r[2]]
print("rows",len(rows),"advertising now",len(act),"active>=50",len([r for r in rows if r[4]>=50]))
print("price min/med/max",min(pr),statistics.median(pr),max(pr))
print("sum est daily spend (listed)",sum(r[6] or 0 for r in rows))
