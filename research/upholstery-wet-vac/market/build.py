import csv, json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rows = [
 ("ryer.de", "https://ryer.de/products/plus", 151.19, 1007, 382, "2025-12-28", 3700, "DE 78.8% AT 21.2% (EU reach)"),
 ("ryershop.de", "https://ryershop.de/products/plus", 151.19, 69, 6, "2026-01-29", "", ""),
 ("ryer.de [Hybrid, separate market]", "https://ryer.de/products/hybrid", 194.39, 166, 159, "2026-07-18", 1900, "DE"),
 ("aurevia-shopping.de [SpotFlow clone]", "https://aurevia-shopping.de/products/aurevia-spotflow", 161.99, 9, 0, "2026-11-07", "", "DE 72.2%"),
 ("jet-force.fr [steam shampooer]", "https://jet-force.fr/products/shampouineuse-vapeur-steam-force", 194.39, 2, 0, "2026-11-07", "", "FR"),
 ("eziclean.ma [W100 injector-extractor]", "https://eziclean.ma/products/nettoyeur-detachant-portable-eziclean-spot-remover-w100", 119.4, 10, 2, "2026-08-31", "", "MA"),
]
with open("sellers.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["brand_id", "url", "price_usd", "total_ads", "active_ads", "first_advertised_at", "est_daily_spend_usd", "countries"])
    w.writerows(rows)
plus = rows[:2]
print("Plus market sellers", len(plus), "active", sum(r[4] for r in plus), "total", sum(r[3] for r in plus))
t = json.load(open("trend_ryer.de_9079563419992.json"))["rows"]
print("Plus spend", t[0][4], "->", t[-1][4], "min", min(r[4] for r in t), "active min", min(r[2] for r in t), "max", max(r[2] for r in t))
