"""Builds raw (condensed, verbatim-valued) JSON files and sellers.csv for wood-repair-wax.
All figures copied verbatim from Brandsearch MCP responses on 2026-11-19. Files marked CONDENSED drop unneeded fields."""
import json, csv, os, statistics
D = os.path.dirname(os.path.abspath(__file__))

def dump(name, obj):
    with open(os.path.join(D, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

# ---- trend (CONDENSED to change points) cols: date,total,active,last_30d,store_daily_spend,market_daily_spend
trend_cols = ["date", "ads_total", "ads_active", "ads_last_30d", "store_est_daily_spend_usd", "market_est_daily_spend_usd"]
trend = [
["2026-08-22",510,357,203,1400,2100],["2026-08-23",510,357,193,1400,2100],["2026-09-04",514,361,168,2400,2100],
["2026-09-11",527,371,181,2400,2400],["2026-09-12",548,385,202,1700,2400],["2026-09-13",548,385,182,3300,2400],
["2026-09-25",566,403,144,3300,2400],["2026-09-26",566,252,144,3000,2400],["2026-10-03",586,270,164,2800,2400],
["2026-10-04",586,270,143,2800,2400],["2026-10-05",598,282,155,2800,2400],["2026-10-06",608,288,165,2800,2400],
["2026-10-10",668,305,237,3400,2400],["2026-10-11",668,305,221,3400,2400],["2026-10-16",677,314,193,3400,2400],
["2026-10-24",701,334,217,3200,2400],["2026-10-25",701,334,202,3200,2400],["2026-10-26",712,344,228,3000,2400],
["2026-11-06",724,356,173,3500,2400],["2026-11-11",783,353,229,3500,2400],["2026-11-14",791,361,239,4300,2400],
["2026-11-15",791,361,230,4400,2400],["2026-11-16",800,370,239,4400,2400]]
dump("trend_kitchik.com_15048615002452.json", {
 "_note": "CONDENSED get_product_trend(days=90, 2026-08-22..2026-11-19): only dates where a figure changed; market advertisers = 1 on every day. Summary line from API: ads 510->800, active 357->370, last_30d 203->239, est daily spend ~$1,400->~$4,400; market est daily spend ~$2,100->~$2,400",
 "columns": trend_cols, "points": trend})

dump("product_kitchik.com_15048615002452.json", {
 "_note": "CONDENSED get_product, values verbatim",
 "id": "kitchik.com_15048615002452", "title": "FixStik - wood repair wax pens",
 "url": "https://kitchik.com/products/kitchik-wood-repair-wax-pens",
 "price": {"amount": 279.0, "currency": "NOK"}, "price_usd": 25.67, "created_at": "2026-03-28T17:17:29+01:00",
 "ads": {"total": 800, "active": 370, "last_30d": 239, "first_advertised_at": "2026-04-03T03:31:28.677Z",
         "last_advertised_at": "2026-11-15T13:33:50.932Z", "est_daily_spend_usd": 4400},
 "market": {"id": "kitchik.com_15048615002452", "sellers": 1, "active_ads": 371, "total_ads": 527, "country_count": 5,
            "est_daily_spend_usd": 2400, "lifecycle_stage": "emerging"},
 "revenue": {"est_monthly_usd_low": 530000, "est_monthly_usd_high": 700000, "scope": "seller"},
 "audience": {"top_country": "SE", "top_country_share_pct": 30.8, "top_age": "45-54", "female_share_pct": 55.8},
 "sourcing_available": True})

dump("audience.json", {
 "_note": "CONDENSED get_product_audience kitchik.com_15048615002452 (791 EU/UK ads analysed)",
 "women_pct": 55.8, "men_pct": 44.2,
 "ages_pct": {"18-24": 0.8, "25-34": 11.5, "35-44": 23.8, "45-54": 26.1, "55-64": 23.3, "65+": 14.4},
 "age_gender_pct_female_male": {"35-44": [12.5, 11.3], "45-54": [14.4, 11.7], "55-64": [13.4, 9.9], "65+": [9.2, 5.2]},
 "country_reach_share_pct": {"SE": 30.8, "DK": 29.5, "PL": 7.8, "GB": 7.3, "DE": 5.7, "FI": 5.4, "BE": 4.3, "IT": 3.9,
                             "NL": 3.0, "AT": 1.2, "FR": 0.8, "ES": 0.2, "GR": 0.2, "CY": 0.1}})

dump("sourcing.json", {
 "_note": "CONDENSED get_product_sourcing. Auto-match is approximate: matched listing is a 2mm paint marker pen, not a wax-stick kit.",
 "supplier_title": "2mm Repair Marking Paint Pen, Waterproof, Sun-Resistant, Not Easy to Fade, Quick-Drying, Black and White Touch-Up Paint, Tire Marking Pen",
 "url": "https://detail.1688.com/offer/1035533644351.html", "unit_cost_usd": 0.18, "moq": 1, "est_shipping_usd": 4,
 "retail_price_usd": 25.67, "gross_margin_pct": 99.4, "markup": 178.39, "break_even_roas": 1.26,
 "break_even_cpa_usd": 20.45, "verdict": "profitable",
 "alternatives": ["offer 843713735834 Furniture mahogany scratch paint repair pen", "offer 1028748773638 stone inscription paint pen", "offer 840950844874 SP-110 paint marker"]})

dump("creative_insights.json", {
 "_note": "get_product_creative_insights: only 5 AI-analysed ads (tiny sample)",
 "hook": {"Comparison": 60, "Demonstration": 40}, "angle": {"Cost Savings": 80, "Convenience": 20},
 "funnel_stage": {"BOF": 100}, "awareness": {"Product Aware": 100}, "pain": {"Appearance": 80, "Money": 20},
 "audience": {"Homeowners": 100}, "motivation": {"Relief": 100}, "tone": {"Direct Response": 100},
 "strategy": {"Problem/Solution": 100}})

dump("market_torkstoretools.com_8746097737816.json", {
 "_note": "CONDENSED get_market(history=true). History series is almost all null.",
 "members": [
  {"id": "torkstoretools.com_8746097737816", "price": "44.99 USD", "ads_total": 49, "active": 42, "first_advertised_at": "2026-04-30T00:28:56.694Z", "est_daily_spend_usd": 250},
  {"id": "torkstoree.com.br_10408086733092", "price": "199 BRL = 35.82 USD", "ads_total": 54, "active": 37, "first_advertised_at": "2026-05-25T18:33:52.690Z", "est_daily_spend_usd": None}],
 "market": {"sellers": 2, "active_ads": 79, "total_ads": 103, "price_min_usd": 35.82, "price_median_usd": 40.41, "price_max_usd": 44.99, "stage": "scaling", "revenue_band_market": "34,000-45,000 USD/mo"},
 "history_nonnull": [["2026-11-13", 2, 28], ["2026-11-19", None, 250]]})

# ---- sellers: columns brand_id,url,price_usd,total_ads,active_ads,first_advertised_at,est_daily_spend_usd,country_language_guess,stage,source_id
sellers = [
 ["kitchik.com","https://kitchik.com/products/kitchik-wood-repair-wax-pens",25.67,800,370,"2026-04-03",4400,"NO(NOK) + SV DA FI PL DE NL IT FR EN-GB; EU reach SE30.8 DK29.5 PL7.8 GB7.3 DE5.7 FI5.4","emerging","kitchik.com_15048615002452"],
 ["kitchik.com (FixStik White)","https://kitchik.com/products/fixstik-white-wood-repair-wax-pens",27.51,32,26,"2026-09-03",580,"NO(NOK); FR landing","emerging","kitchik.com_15585504330068"],
 ["torkstoretools.com","https://torkstoretools.com/products/20-colors-furniture-filler-sticks-for-furniture-touch-ups-and-repairs-wood-crayon-markers-for-remover-scratches-holes-laminate",44.99,49,42,"2026-04-30",250,"US (USD, EN)","scaling","torkstoretools.com_8746097737816"],
 ["torkstoree.com.br","https://torkstoree.com.br/products/kit-de-reparo-para-mdf-com-bastoes-de-cera-20-cores",35.82,54,37,"2026-05-25",None,"BR (BRL, PT)","scaling","torkstoree.com.br_10408086733092"],
 ["hemmafixet.com (TraFix)","https://hemmafixet.com/products/trafix",None,149,0,"2026-01-12",18,"SE (SEK, SV); price listed 27.95 SEK likely parse error","declining","hemmafixet.com_10418619842903"],
 ["hemmafixet.se (TraFix)","https://hemmafixet.se/products/trafix",None,57,0,"2026-01-13",None,"SE; listed 299 USD, probably 299 SEK","declining","hemmafixet.se_15160960057674"],
 ["restorelab.se","https://restorelab.se/products/restorelab",28.41,20,0,"2026-10-22",None,"SE (SEK, SV)","declining","restorelab.se_10873978716497"],
 ["nordvella.nl","https://nordvella.nl/products/nordvella-fixstik-houtreparatieset",32.39,1,0,"2026-11-11",None,"NL (EUR, NL)","declining","nordvella.nl_12392109080894"],
 ["pilon.ch","https://pilon.ch/products/kratzer-reparaturstifte-fur-holz",49.95,11,0,"2025-12-30",None,"CH/DE (DE)","declining","pilon.ch_10068628078877"],
 ["dodeb.com","https://dodeb.com/products/mbqj",32.37,5,0,"2026-04-15",None,"DE (EUR, DE)","declining","dodeb.com_14880235749748"],
 ["novastarz.shop","https://novastarz.shop/products/nugrainnvzdeaa1",29.97,3,0,"2026-08-11",None,"DE (USD listed, DE copy)","declining","novastarz.shop_10228067139877"],
 ["studiomoreandless.com","https://studiomoreandless.com/products/wax-filler-duo",12.99,2,0,"2026-03-24",None,"DE copy","declining","studiomoreandless.com_9813060059475"],
 ["nestifymall.com","https://nestifymall.com/products/wure",12.69,1,0,"2026-11-09",None,"UK (GBP, EN)","saturated","nestifymall.com_15438205518075"],
 ["svchrono.com","https://svchrono.com/products/furniture-scratch-repair-kit-set-of-20",14.99,4,4,"2026-01-31",None,"EN/AR (USD)","emerging","svchrono.com_7583978684521"],
 ["istahly.com","https://istahly.com/products/pen",14.99,2,2,"2026-06-18",None,"EN (USD)","emerging","istahly.com_9813841871148"],
 ["getluxgrove.com","https://getluxgrove.com/products/luxgrove-furniture-repair-salve-limited-edition-kit",34.95,2,2,"2026-08-02",None,"US (USD, EN)","emerging","getluxgrove.com_9968241410387"],
 ["ganmarkt.com","https://ganmarkt.com/products/gankit-wood-furniture-repair-minikit",30.99,3,0,"2026-11-10",None,"EN (USD)","declining","ganmarkt.com_10367556256081"],
]
hdr = ["brand_id","url","price_usd","total_ads","active_ads","first_advertised_at","est_daily_spend_usd","countries_languages","stage","product_id"]
with open(os.path.join(D, "sellers.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(sellers)
dump("similar.json", {"_note": "CONDENSED get_similar_products(limit=15) + search_products (q=wood repair wax / Holz Reparatur Wachs Kratzer / furniture scratch repair kit); rows as in sellers.csv", "columns": hdr, "rows": sellers})

ads = {
 "_note": "CONDENSED search_meta_ads brand_ids=kitchik.com (471 indexed vs 800 on product card). Headlines/copy abbreviated or translated key phrases; ids, dates, reach, spend verbatim. For status active ads end_date = last scrape date, so days running is a lower bound.",
 "columns": ["id","lang","format","status","start","end","eu_reach","eu_spend_eur","headline","copy_key"],
 "top_by_eu_spend": [
  ["2104511826944370","SV","video","inactive","2026-08-16","2026-09-02",621459,5910.08,"Reporna forsvinner pa 30 sekunder","Carpenter wants 2,000 kr vs fix it yourself in 30 sec; wax sticks melt into wood; fill, scrape with card, polish"],
  ["1668638447498411","DA","video","inactive","2026-04-04","2026-05-13",542759,5042.23,"Ridser forsvinder pa 30 sekunder","Carpenter 2000 kr vs 199 kr"],
  ["1114731050864425","SV","video","inactive","2026-05-01","2026-05-25",476851,4534.85,"Reporna forsvinner pa 30 sekunder","Carpenter 2000 kr vs 299 kr"],
  ["1650055496206005","SV","video","inactive","2026-04-23","2026-05-31",443765,4220.21,"Reporna forsvinner pa 30 sekunder","same, 299 kr"],
  ["27194418166850196","SV","video","inactive","2026-05-21","2026-06-29",355020,3376.24,"Se vad som hander nar du fyller repan","Fill the scratch; works on white and wood; 10 colours"]],
 "other": [
  ["2522626781583263","IT","video","inactive","2026-09-18","2026-10-06",234220,1887.81,"I graffi spariscono in 30 secondi","20,000+ happy customers; 60-day refund"],
  ["1747741689609157","DE","video","inactive","2026-09-03","2026-09-20",182147,1830.58,"Kratzer verschwinden in 30 Sekunden","Handwerker over 150 EUR vs 26,99 EUR; laminate"],
  ["26647186671619298","PL","video","inactive","2026-05-31","2026-06-17",186084,1751.05,"Rysy znikaja w 30 sekund","Fachowiec 500 zl vs 89 zl; panels"],
  ["2213908559327717","FR","video","inactive","2026-09-07","2026-10-19",165319,1330.82,"Les rayures disparaissent en 30 secondes","20 000 clients; 60-day refund; LP fixstik-white"],
  ["3176668732722732","DA","image","active","2026-06-22","2026-07-06",12509,116.21,"Hvide flader med maerker?","Morning/midday/evening list; no paint, no drying time; white surfaces"],
  ["2810867049247785","DA","image","active","2026-06-22","2026-07-05",2037,18.92,"Hvidt, sort og trae","10 colours; 30 seconds; no tools"],
  ["1507582043646159","DA","image","active","2026-06-22","2026-07-06",986,9.16,"Sorte moebler med ridser?","black surfaces match"],
  ["1007391075591205","NO","image","active","2026-06-28","2026-07-06",None,None,"Svart tre viser alt. FixStik skjuler alt","Snekker 2000 kr vs FixStik 299 kr, 30 sec; 10 wax sticks; black wood"],
  ["1324971013159894","NO","video","active","2026-06-29","2026-07-06",None,None,"Ripene forsvinner pa 30 sekunder","carpenter 2000 vs 299 kr"],
  ["1514908813458503","EN-GB","video","active","2026-07-02","2026-07-06",1550,17.82,"Scratches disappear in 30 seconds","white painted wood works; 10 colours; no tools, no paint"],
  ["1648276732916241","EN-GB","video","active","2026-07-02","2026-07-06",3873,44.54,"Scratches disappear in 30 seconds","tradesperson hefty fee vs 30 sec"],
  ["1017874697540265","EN-GB","video","active","2026-07-02","2026-07-06",5001,57.51,"Scratches disappear in 30 seconds","same as 1514908813458503"],
  ["2646133979150932","SV","video","active","2020-11-04","2026-11-13",None,None,"Reporna forsvinner pa 30 sekunder","same SV script (start 2026-11-04)"],
  ["986424031045017","SV","video","active","2026-11-10","2026-11-13",None,None,"Black Friday-rea: Upp till 50% rabatt","same script + BF headline; 299 kr"],
  ["1612278714002692","NO","video","active","2026-11-09","2026-11-13",None,None,"Black Friday-salg: Opptil 50% rabatt","279 kr"],
  ["2331679057669571","DA","video","active","2026-11-04","2026-11-13",None,None,"Ridserne forsvinder pa 30 sekunder","white works, wood works, 10 colours"],
  ["1811243156678862","FI","video","active","2026-11-04","2026-11-13",None,None,"Naarmut katoavat 30 sekunnissa","moisture gets in, wood lightens; 10 colours birch to walnut"],
  ["880462241315445","NL","video","?","?","?",None,None,"Krassen verdwijnen in 30 seconden","white works, wood works, 10 colours (nl-nl LP)"]],
 "ads_in_index_by_language": {"de": 35, "pl": 8, "fi": 12, "nl": 16, "it": 4, "fr": 6}}
ads["other"][12][4] = "2026-11-04"
dump("ads_kitchik.com.json", ads)

# ---- computed stats
act = [s for s in sellers if s[4] and s[4] > 0]
prices = [s[2] for s in sellers if s[2] and s[7] and "likely" not in s[7] and "probably" not in s[7]]
print("sellers listed:", len(sellers), "with active ads:", len(act), [s[0] for s in act])
print("price min/median/max:", min(prices), statistics.median(prices), max(prices))
print("kitchik share of listed active ads:", 370 / sum(s[4] for s in sellers))
t = trend
print("spend", t[0][4], "->", t[-1][4], "ads", t[0][1], "->", t[-1][1], "active", t[0][2], "->", t[-1][2])
top5 = ads["top_by_eu_spend"]
from datetime import date
for a in top5:
    s = date.fromisoformat(a[4]); e = date.fromisoformat(a[5]); print(a[0], a[1], (e - s).days, "days", a[7], "EUR")
