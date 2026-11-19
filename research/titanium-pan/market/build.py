import json, csv
d = json.load(open('market_titanoxfrance.json', encoding='utf8'))
rows = []
for m in d['members']:
    a = m['ads']
    rows.append([m['brand_id'], m['url'], m.get('price_usd'), f"{m['price']['amount']} {m['price']['currency']}",
                 a['total'], a['active'], a['last_30d'], a['first_advertised_at'][:10], a.get('est_daily_spend_usd')])
rows.sort(key=lambda r: -r[5])
with open('sellers.csv', 'w', newline='', encoding='utf8') as f:
    w = csv.writer(f)
    w.writerow(['brand_id', 'url', 'price_usd', 'price_local', 'total_ads', 'active_ads', 'ads_last_30d', 'first_advertised_at', 'est_daily_spend_usd'])
    w.writerows(rows)
p = sorted(r[2] for r in rows if r[2] and r[2] > 5)
print('members', len(rows), 'active>0', sum(1 for r in rows if r[5] > 0), 'active>=50', sum(1 for r in rows if r[5] >= 50))
print('price min/med/max', p[0], p[len(p) // 2], p[-1])
tot = sum(r[5] for r in rows)
print('total active', tot, 'total ads', sum(r[4] for r in rows))
for r in rows[:4]:
    print(r[0], r[5], round(100 * r[5] / tot, 1), '%', r[8])
print('first adv since Oct15', len([r for r in rows if r[7] >= '2026-10-15']), 'since Nov1', len([r for r in rows if r[7] >= '2026-11-01']))
h = [x for x in d['history'] if x['advertisers']]
print('hist first', h[0], 'last', h[-1])
print('peak spend', max(h, key=lambda x: x['est_daily_spend_usd']))
for x in h[::10]:
    print(x['date'][:10], x['advertisers'], x['est_daily_spend_usd'])
