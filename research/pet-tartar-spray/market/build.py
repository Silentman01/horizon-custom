import json, csv, statistics, datetime as dt
# Condensed copies of the Brandsearch MCP responses relied on (2026-11-19)
raw = {
"product.json": {"id":"paw-guardian.com_14977703772543","price_usd":55.99,"ads":{"total":5587,"active":2001,"last_30d":1091,"first_advertised_at":"2025-12-24","est_daily_spend_usd":1800},"market":{"sellers":3,"active_ads":2001,"total_ads":5605,"price_min_usd":49.9,"price_median_usd":52.95,"price_max_usd":55.99,"country_count":20,"lifecycle_stage":"scaling"},"revenue_market_monthly_usd":[250000,330000],"sourcing_available":True},
"trend_summary.json": {"window":"2026-08-22..2026-11-19","start":{"ads_total":3339,"active":1631,"last_30d":805,"daily_spend":1200},"end":{"ads_total":5587,"active":2001,"last_30d":1091,"daily_spend":1800},"peak_daily_spend":{"2026-09-05":2600},"trough_daily_spend":{"2026-09-27..2026-10-09":1100},"active_ads_peak":{"2026-11-18":2127},"market_advertisers":2},
"sellers.json": [
 {"brand_id":"paw-guardian.com","url":"https://paw-guardian.com/products/anti-tartar-spray-dogs-cats","price_usd":55.99,"total_ads":5587,"active_ads":2001,"first_advertised_at":"2025-12-24","est_daily_spend_usd":1800,"countries":"GB 94.2% of EU/UK reach; 29 EU/UK countries; FR ads too"},
 {"brand_id":"franceabsorkas.com","url":"https://franceabsorkas.com/products/oreiller-soya-2-0","price_usd":3.0,"total_ads":20,"active_ads":0,"first_advertised_at":"2026-03-12","est_daily_spend_usd":None,"countries":"FR (pillow; mis-clustered, NOT a dental spray)"},
 {"brand_id":"chronocalm.com","url":"https://chronocalm.com/products/oreiller-orthopedique-chronocalm","price_usd":49.9,"total_ads":18,"active_ads":0,"first_advertised_at":"2026-05-01","est_daily_spend_usd":None,"countries":"FR (pillow; mis-clustered, NOT a dental spray)"},
 {"brand_id":"littlefindsco.com","url":"https://littlefindsco.com/products/pet-oral-care-spray-fresh-breath-healthy-teeth-no-brushing-needed","price_usd":16.99,"total_ads":127,"active_ads":127,"first_advertised_at":"2026-01-27","est_daily_spend_usd":None,"countries":"USD store; last ad 2026-02-12 (stale)"},
 {"brand_id":"moepuppy.com","url":"https://moepuppy.com/products/dental-spray-100ml","price_usd":3.95,"total_ads":44,"active_ads":23,"first_advertised_at":"2026-02-06","est_daily_spend_usd":None,"countries":"IN (INR)"},
 {"brand_id":"furaqua.com","url":"https://furaqua.com/products/spray","price_usd":39.99,"total_ads":117,"active_ads":12,"first_advertised_at":"2025-12-25","est_daily_spend_usd":None,"countries":"14 countries; declining"},
 {"brand_id":"carispray.eu","url":"https://carispray.eu/products/carispray-hydroxyapatite-oral-spray","price_usd":37.79,"total_ads":13,"active_ads":12,"first_advertised_at":"2026-06-30","est_daily_spend_usd":3,"countries":"EU (EUR)"},
 {"brand_id":"pupdose.com","url":"https://pupdose.com/products/dental-spray-tartar-removal-healthy-gums-fresh-breath-for-dogs","price_usd":45.0,"total_ads":6,"active_ads":6,"first_advertised_at":"2026-10-22","est_daily_spend_usd":None,"countries":"USD store"},
 {"brand_id":"denwild.shop","url":"https://denwild.shop/products/no-brush-dental-spray1","price_usd":29.99,"total_ads":10,"active_ads":5,"first_advertised_at":"2026-11-09","est_daily_spend_usd":None,"countries":"USD store"},
 {"brand_id":"twolinda.store","url":"https://twolinda.store/products/pet-dental-tartar-care-spray","price_usd":15.99,"total_ads":6,"active_ads":5,"first_advertised_at":"2026-10-27","est_daily_spend_usd":None,"countries":"USD store"},
 {"brand_id":"aussie-pet.com","url":"https://aussie-pet.com/products/brushless-tartar-control-dental-spray-for-dogs-helps-reduce-plaque-freshen-breath","price_usd":13.17,"total_ads":4,"active_ads":4,"first_advertised_at":"2026-09-29","est_daily_spend_usd":None,"countries":"AU (AUD)"},
 {"brand_id":"australianpaws.com","url":"https://australianpaws.com/products/cross-border-pet-oral-care-spray-gum-care-fresh-breath-no-brushing-required-direct-spray-gentle-oral-care-spray","price_usd":13.17,"total_ads":4,"active_ads":4,"first_advertised_at":"2026-09-23","est_daily_spend_usd":None,"countries":"AU (AUD)"},
 {"brand_id":"newbeeoo.com","url":"https://newbeeoo.com/products/gifuiealf","price_usd":16.99,"total_ads":12,"active_ads":12,"first_advertised_at":"2026-02-02","est_daily_spend_usd":None,"countries":"13 countries; last ad 2026-04-10 (stale)"},
 {"brand_id":"boxofsmile.in","url":"https://boxofsmile.in/products/teeth-cleaning-spray-for-dogs-cats","price_usd":None,"total_ads":5,"active_ads":5,"first_advertised_at":"2026-05-10","est_daily_spend_usd":None,"countries":"IN (599 INR)"},
],
"audience.json": {"women_pct":77.9,"men_pct":22.1,"ages":{"18-24":1.1,"25-34":8.3,"35-44":19.4,"45-54":26.8,"55-64":26.6,"65+":17.7},"countries":{"GB":94.2,"IE":0.8,"FR":0.7,"ES":0.5,"PT":0.5,"DE":0.3,"GR":0.3,"BE":0.3,"NL":0.3,"SE":0.2},"analysed_ads":5545},
"sourcing.json": {"supplier":"1688 Dentaclean for Dogs & Cats Pet Oral Spray (Guangzhou Xiyan Cosmetics)","unit_cost_usd":1.12,"bulk_unit_cost_usd":0.84,"bulk_qty":1000,"moq":1,"est_shipping_usd":2.9,"retail_price_usd":55.99,"gross_margin_pct":96.6,"break_even_roas":1.12,"break_even_cpa_usd":50.03,"verdict":"profitable","alt_listings":3},
"creative_insights.json": {"analysed_ads":72,"hook":{"Fear":41.7,"Demonstration":15.3,"Curiosity":12.5,"Question":9.7},"angle":{"Pain":58.3,"New Mechanism":13.9,"Convenience":6.9,"Cost Savings":5.6,"Enemy":5.6},"funnel":{"BOF":61.1,"MOF":38.9},"awareness":{"Problem Aware":52.8,"Product Aware":45.8},"motivation":{"Fear of Loss":70.8,"Relief":20.8}},
"similar.json": "get_similar_products returned only pillow (oreiller) look-alikes (image-similarity noise); no dental-spray look-alike markets.",
"ads_paw-guardian.json": [
 {"id":"2006543786796746","start":"2025-12-05","end":"2026-05-29","status":"inactive","format":"image","eu_reach":16179,"eu_spend_eur":186,"headline":"Black Friday: Dog Parents Are Snapping This Up Fast","lp":"product"},
 {"id":"1977733896117970","start":"2025-12-05","end":"2026-05-29","status":"inactive","format":"image","eu_reach":30607,"eu_spend_eur":351,"headline":"Black Friday (same)","lp":"product"},
 {"id":"1542336076815049","start":"2025-12-05","end":"2026-05-29","status":"inactive","format":"video","eu_reach":72726,"eu_spend_eur":836,"headline":"3 dog-dental hacks every pet parent should try (for under $10).","lp":"product"},
 {"id":"863323466173050","start":"2025-12-05","end":"2026-05-29","status":"inactive","format":"image","eu_reach":119693,"eu_spend_eur":1376,"headline":"Black Friday (same)","lp":"product"},
 {"id":"3013220405530900","start":"2025-12-05","end":"2026-05-27","status":"inactive","format":"video","eu_reach":203638,"eu_spend_eur":2341,"headline":"Brushing Might Be Making Your Dog's Teeth Worse","lp":"advertorial"},
 {"id":"833701122635750","start":"2025-11-15","end":"2026-04-19","status":"inactive","format":"video","eu_reach":326225,"eu_spend_eur":2689,"headline":"Avertissement du veterinaire (FR)","lp":"advertorial paw-guardian.co"},
 {"id":"825615377044187","start":"2025-11-15","end":"2026-04-16","status":"inactive","format":"video","eu_reach":170778,"eu_spend_eur":1400,"headline":"Avertissement du veterinaire (FR)","lp":"advertorial"},
 {"id":"1419403263687298","start":"2026-11-13","end":"2026-11-16","status":"active","format":"video","headline":"Fresh Breath Without Brushing","lp":"product"},
 {"id":"28913761758250779","start":"2026-11-13","end":"2026-11-17","status":"active","format":"video","headline":"Fresh Breath Without Brushing","lp":"product"},
]}
for k, v in raw.items():
    json.dump(v, open(k, "w"), indent=1, ensure_ascii=False)
sellers = raw["sellers.json"]
cols = ["brand_id","url","price_usd","total_ads","active_ads","first_advertised_at","est_daily_spend_usd","countries"]
with open("sellers.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(cols)
    for s in sellers: w.writerow([s[k] for k in cols])
spray = [s for s in sellers if s["brand_id"] not in ("franceabsorkas.com", "chronocalm.com")]
prices = [s["price_usd"] for s in spray if s["price_usd"]]
print("spray stores", len(spray), "with active ads:", sum(1 for s in spray if s["active_ads"] > 0))
print("price min/median/max", min(prices), statistics.median(prices), max(prices))
print("stores priced >= $35:", [s["brand_id"] for s in spray if (s["price_usd"] or 0) >= 35])
print("paw-guardian share of spray active ads %.1f%%" % (100 * 2001 / sum(s["active_ads"] for s in spray)))
for a in raw["ads_paw-guardian.json"][:7]:
    print(a["id"], (dt.date.fromisoformat(a["end"]) - dt.date.fromisoformat(a["start"])).days, "days")
