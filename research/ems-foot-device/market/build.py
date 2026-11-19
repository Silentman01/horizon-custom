import json, csv
d = json.load(open('foot_candidates.json', encoding='utf-8'))
m = json.load(open('market_artuvate.json', encoding='utf-8'))
rows = [dict(zip(d['cols'], r)) for r in d['rows']]
for x in m['members']:
    rows.append({"brand": x['brand_id'] + " (neck FisioRest cluster)", "product_id": x['id'], "title": "neck massager cluster", "price_usd": x['price_usd'], "total_ads": x['total'], "active_ads": x['active'], "ads_30d": None, "first_advertised_at": x['first'], "est_daily_spend_usd": 1500 if x['brand_id'] == 'artuvate.co' else None, "lifecycle": "peak", "market_sellers": 10})
rows.sort(key=lambda r: -(r['active_ads'] or 0))
with open('sellers.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
foot = [r for r in d['rows'] if 'lureess' not in r[0] and 'shakti' not in r[0]]
act = [r for r in foot if r[5] > 0]
pr = sorted(r[3] for r in foot)
print("foot rows", len(foot), "with active ads", len(act), "active sum", sum(r[5] for r in foot))
print("price min/median/max", pr[0], pr[len(pr) // 2], pr[-1])
print("ads_30d>0:", [r[0] for r in foot if (r[6] or 0) > 0])
print("local-language DE/CH:", [r[0] for r in foot if r[0].endswith('.de') or r[0].endswith('.ch') or 'neuravive' in r[0] or 'celviana' in r[0]])
