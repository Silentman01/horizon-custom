import json, csv, statistics as st
d = json.load(open('sellers_raw_condensed.json', encoding='utf-8'))
spend = d['est_daily_spend_usd_by_brand_verbatim']
seen = {}
rows = []
for src, b, u, p, t, a, f in d['rows']:
    if b in seen:
        continue  # toiae.fr appears in both markets
    seen[b] = 1
    rows.append(dict(brand_id=b, url=u, price_usd=p, total_ads=t, active_ads=a,
                     first_advertised_at=f, est_daily_spend_usd=spend.get(b, ''), market=src))
with open('sellers.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
n = len(rows)
act = [r for r in rows if r['active_ads'] > 0]
pr = [r['price_usd'] for r in rows if r['price_usd']]
core = [x for x in pr if 15 <= x <= 60]
pre = [r for r in rows if r['first_advertised_at'] < '2026-10-01']
print('unique sellers', n, 'active', len(act), 'sum active ads', sum(r['active_ads'] for r in rows))
print('price all min/med/max', min(pr), st.median(pr), max(pr), '| 15-60 band', min(core), st.median(core), max(core), 'n', len(core))
print('premium >=100:', [(r['brand_id'], r['price_usd']) for r in rows if r['price_usd'] and r['price_usd'] >= 100])
print('first advertised before Oct 1:', len(pre), 'active now', sum(1 for r in pre if r['active_ads'] > 0))
post = [r for r in rows if r['first_advertised_at'] >= '2026-10-01']
print('first advertised Oct 1+:', len(post), 'active', sum(1 for r in post if r['active_ads'] > 0))
print('by month:', {m: sum(1 for r in rows if r['first_advertised_at'][:7] == m) for m in sorted({r['first_advertised_at'][:7] for r in rows})})
tot = sum(r['active_ads'] for r in rows)
print('top3 active share', sum(sorted([r['active_ads'] for r in rows])[-3:]) / tot)
tld = {}
for r in rows:
    t = r['brand_id'].split('.')[-1]
    tld[t] = tld.get(t, 0) + 1
print(tld)
