import json, csv, statistics as st, os
d = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(d, 'sellers.json')))
with open(os.path.join(d, 'sellers.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['brand_id', 'url', 'price_usd', 'total_ads', 'active_ads', 'first_advertised_at', 'est_daily_spend_usd', 'countries'])
    for b, p, t, a, fa in rows:
        fs = b == 'fitsleeps.com'
        w.writerow([b, 'https://' + b, p, t, a, fa,
                    '5500 (market est)' if fs else '',
                    'GB36.5 DE14 NL8.2 SE7.8 BE6 IE5 (market reach %)' if fs else ''])
pr = [r[1] for r in rows]
core = [p for p in pr if p < 100]
print('sellers', len(rows), 'with active>0', sum(r[3] > 0 for r in rows), 'active>=10', sum(r[3] >= 10 for r in rows))
print('price all min/med/max', min(pr), st.median(pr), max(pr))
print('price <100: min/med/max', min(core), st.median(core), max(core), 'n', len(core))
tot = sum(r[2] for r in rows); act = sum(r[3] for r in rows)
print('total ads', tot, 'active', act, 'fitsleeps share total %.1f%% active %.1f%%' % (100 * rows[0][2] / tot, 100 * rows[0][3] / act))
print('first advertised since 2026-10-01:', sum(r[4] >= '2026-10-01' for r in rows), '| since 2026-11-01:', sum(r[4] >= '2026-11-01' for r in rows))
print('sellers with <=30 total ads:', sum(r[2] <= 30 for r in rows))
print('price >=100:', [(r[0], r[1]) for r in rows if r[1] >= 100])
