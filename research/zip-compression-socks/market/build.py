import json, csv, os
here = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(here, "market_netoviaclean.com_16156885451084.json"), encoding="utf-8"))
ctry = {"se": "SE", "no": "NO", "de": "DE", "at": "AT", "be": "BE", "com": "FI?/FR"}
rows = []
for s in m["members"]:
    tld = s["brand_id"].rsplit(".", 1)[1]
    rows.append([s["brand_id"], s["url"], s["price_usd"], s["ads_total"], s["ads_active"],
                 s["first_advertised_at"], s["est_daily_spend_usd"], ctry.get(tld, "")])
with open(os.path.join(here, "sellers.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["brand_id", "url", "price_usd", "total_ads", "active_ads", "first_advertised_at", "est_daily_spend_usd", "countries_from_tld"])
    w.writerows(rows)
print("sellers", len(rows), "active_ads_sum", sum(r[4] for r in rows), "total_ads_sum", sum(r[3] for r in rows))
print("spend_sum_of_store_estimates", sum(r[6] or 0 for r in rows), "vs market series 1500")
p = sorted(r[2] for r in rows)
print("price min/median/max", p[0], p[len(p)//2], p[-1])
