"""Builds raw (CONDENSED, values copied verbatim from Brandsearch responses of 2026-11-19) json files and sellers.csv.
Run: python build.py"""
import json, csv, os, statistics
here = os.path.dirname(os.path.abspath(__file__))

def dump(name, obj):
    with open(os.path.join(here, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

# id, brand_id, currency, price_local, price_usd, total_ads, active_ads, ads_30d, first_advertised_at, est_daily_spend_usd
members = [
 ["comfysleepers.com_7736490262605","comfysleepers.com","USD",49.99,49.99,4316,2445,513,"2026-05-22",3300],
 ["comfysleepers.com_7959897374797","comfysleepers.com","USD",49.99,49.99,16,16,16,"2026-10-03",None],
 ["solvestride.com_8896212074693","solvestride.com","INR",2999.0,35.99,28,28,28,"2026-08-23",None],
 ["belleaparis.com_15812080271737","belleaparis.com","CHF",64.9,71.39,23,17,6,"2026-09-27",None],
 ["cosalia-home.com_10752668303699","cosalia-home.com","EUR",69.99,75.59,25,14,11,"2026-08-18",9],
 ["ripozen.com_9167268380914","ripozen.com","EUR",64.95,70.15,109,13,93,"2026-08-17",4],
 ["lojazafir.com_10494026023200","lojazafir.com","BRL",227.0,40.86,12,12,12,"2026-09-10",None],
 ["slomorning.com_15478929719681","slomorning.com","EUR",115.0,124.2,7,7,7,"2026-08-27",21],
 ["harrington-online.com_16061744808261","harrington-online.com","EUR",59.95,64.75,51,6,48,"2026-10-02",5],
 ["shopavena.ca_10306753593397","shopavena.ca","CAD",79.99,58.39,6,6,6,"2026-09-25",None],
 ["colveyra.com_10350035075129","colveyra.com","USD",49.99,49.99,15,2,14,"2026-10-14",None],
 ["trendingturn.com_8997500158106","trendingturn.com","USD",79.95,79.95,3,2,2,"2026-06-25",None],
 ["broeiy.com_8697712967863","broeiy.com","USD",49.99,49.99,2,0,2,"2026-11-08",None],
 ["celmirae.shop_15925758198108","celmirae.shop","USD",49.99,49.99,4,0,4,"2026-11-14",None],
 ["dreamoro.de_15985155899774","dreamoro.de","EUR",69.99,75.59,9,0,8,"2026-07-10",None],
 ["duettonights.com_15716603363676","duettonights.com","GBP",39.95,50.74,34,0,25,"2026-08-10",None],
 ["elmunz.com_9456566534358","elmunz.com","USD",49.0,49.0,2,0,2,"2026-11-05",None],
 ["nodolorix.com_9772872335605","nodolorix.com","EUR",64.95,70.15,77,0,52,"2026-08-13",None],
 ["prdfr.com_9298686247124","prdfr.com","USD",99.99,99.99,13,0,8,"2026-09-28",None],
 ["secretpleasurescr.com_8370597658763","secretpleasurescr.com","GBP",39.99,50.79,22,0,19,"2026-08-17",None],
 ["shoppawcove.com_8721006887047","shoppawcove.com","USD",49.9,49.9,28,0,2,"2026-08-19",None],
]
lang = {"belleaparis.com":"FR (CHF price)","cosalia-home.com":"ES (EUR)","ripozen.com":"IT (EUR)","lojazafir.com":"PT-BR (BRL)",
 "slomorning.com":"DE (EUR)","harrington-online.com":"NL (EUR)","shopavena.ca":"FR-CA (CAD)","dreamoro.de":"DE (EUR)",
 "nodolorix.com":"SV (EUR price)","broeiy.com":"ES","elmunz.com":"ES","shoppawcove.com":"EN/ES","duettonights.com":"EN-UK (GBP)",
 "secretpleasurescr.com":"EN-UK (GBP)","solvestride.com":"EN (INR price)","comfysleepers.com":"EN (USD)","colveyra.com":"EN (USD)",
 "trendingturn.com":"EN (USD)","celmirae.shop":"EN (USD)","prdfr.com":"EN (USD)"}
cols = ["id","brand_id","currency","price_local","price_usd","total_ads","active_ads","ads_30d","first_advertised_at","est_daily_spend_usd"]
dump("market_comfysleepers.com_7736490262605.json", {
 "_note":"CONDENSED from get_market(history=true) 2026-11-19; member numbers copied verbatim. API said pagination.total=21 members (20 distinct brands incl. 2 comfysleepers product rows); market.sellers=19 in card.",
 "market":{"sellers":19,"active_ads":2545,"total_ads":4775,"price_min_usd":35.99,"price_median_usd":54.59,"price_max_usd":99.99,"new_sellers_30d":2,"country_count":4,"est_daily_spend_usd":3400,"lifecycle_stage":"scaling","revenue_est_monthly_usd":[450000,600000]},
 "member_columns":cols,"members":members,
 "history_summary":"daily advertisers 11 (2026-08-20) -> 18 (2026-11-18); est_daily_spend_usd 4600 (08-20), peak 5700 (09-11), 2900 (09-20), 2800 (10-06), 3200 (10-19), 3700 (10-31), 3400 (11-18)"})
dump("trend_comfysleepers.com_7736490262605.json", {
 "_note":"CONDENSED from get_product_trend(days=90). Rows verbatim: [date,total_ads,active_ads,last_30d,store_est_daily_usd,market_advertisers,market_est_daily_usd]. Summary verbatim: ads 2,351 -> 4,316, active 938 -> 2,445, started last 30d 1,092 -> 513, est daily spend ~$4,500 -> ~$3,300; market stores advertising 11 -> 18, spend ~$4,600 -> ~$3,400",
 "rows":[["2026-08-22",2351,938,1092,4500,11,4600],["2026-09-01",2655,1199,1012,4100,12,4300],["2026-09-11",2939,1401,952,5500,14,5700],["2026-09-20",3304,1665,984,2600,15,2900],["2026-10-01",3540,1804,885,3300,17,3500],["2026-10-06",3602,1822,804,2700,17,2800],["2026-10-19",3837,2011,625,3000,18,3200],["2026-10-26",3979,2150,525,3400,18,3600],["2026-11-01",4067,2234,529,3600,18,3700],["2026-11-09",4201,2349,532,3500,18,3500],["2026-11-19",4316,2445,513,3300,18,3400]]})
dump("audience.json", {"_note":"verbatim get_product_audience","analysed_ads":4758,"female_pct":24.9,"male_pct":75.1,"age_pct":{"18-24":1.8,"25-34":19.3,"35-44":39.7,"45-54":26.5,"55-64":10.5,"65+":2.3},"country_reach_pct":{"GB":68.4,"FR":8.8,"DE":3.8,"ES":3.4,"BE":3.3,"IT":2.7,"NL":2.3,"DK":1.7,"PT":1.5,"IE":1.0,"GR":0.9,"SE":0.7,"FI":0.7,"AT":0.2,"RO":0.2}})
dump("sourcing.json", {"_note":"verbatim get_product_sourcing","supplier_title":"Ice Silk Pajamas Men's Long Sleeve ... Middle-aged and Elderly Home Clothes","url":"https://detail.1688.com/offer/919753630006.html","unit_cost_usd":11.48,"bulk_unit_cost_usd":10.92,"bulk_qty":10,"moq":1,"est_shipping_usd":4.6,"retail_price_usd":49.99,"gross_margin_pct":77.0,"break_even_roas":1.55,"break_even_cpa_usd":32.2,"verdict":"profitable","WARNING":"automatic match is a silk PAJAMA listing, not a wedge pillow: cost unverified"})
dump("creative_insights.json", {"_note":"verbatim, 26 AI-analysed ads","hook":{"Demonstration":38.5,"Social Proof":11.5,"Testimonial":11.5,"Aspiration":7.7,"Curiosity":7.7},"angle":{"Convenience":57.7,"Desire":15.4,"Transformation":11.5,"Comparison":7.7,"Lifestyle":3.8},"funnel":{"BOF":84.6,"TOF":11.5,"MOF":3.8},"pain":{"Confidence":50.0,"Comfort":23.1,"Health":19.2,"Frustration":3.8,"Relationships":3.8},"audience":{"Couples":50.0,"Adults":34.6,"Women":15.4},"strategy":{"Problem/Solution":80.8,"Social Proof":15.4,"Comparison":3.8}})
dump("similar.json", {"_note":"CONDENSED get_similar_products + search_products; fields verbatim",
 "similar":[
  {"id":"lunarastore.es_15724936855935","price_usd":48.59,"ads":6,"active":0,"market_sellers":4,"stage":"declining"},
  {"id":"aveonfr.com_9606170869973","price_usd":64.69,"ads":15,"active":12,"market_sellers":10,"market_total_ads":7,"stage":"declining","copy":"inclinaison de 27 deg ... Essayez-le 90 nuits"},
  {"id":"aushomeco.com_9213823746276","price_usd":80.0,"ads":2,"stage":"emerging"},
  {"id":"vistorox.com_8756818510007","price_usd":159.0,"ads":1,"stage":"emerging"},
  {"id":"myvelaa.com_14952164426096","price_usd":89.99,"market_sellers":19,"market_total_ads":255,"market_active_ads":34,"new_sellers_30d":4,"stage":"declining","market_est_daily_spend_usd":1,"note":"title Moodie Intimacy Comfort Pillow but URL is a reading wedge pillow"}],
 "search_intimacy_pillow":[
  {"id":"cozycloudco.com_9684850409623","price_usd":52.75,"total_ads":168,"active":101,"ads_30d":129,"first":"2026-08-11","stage":"emerging"},
  {"id":"avraofficial.co_15599128445263","price_usd":77.95,"total_ads":442,"active":0,"first":"2026-01-08","stage":"declining"},
  {"id":"amoracomfort.com_8161694122031","price_usd":51.95,"market_sellers":6,"stage":"declining"}],
 "search_wedge_pillow_sleep_reflux":[
  {"id":"hiquo.co_9572650680655","title":"Anti-Snoring Wedge Pillow","price_usd":85.99,"total_ads":1337,"active":417,"first":"2025-12-23","market_sellers":6,"market_est_daily_spend_usd":41,"stage":"saturated","revenue_est":[5300,6900]},
  {"id":"davolia.com_7631292923998","title":"RefluxGuard baby pillow","price_usd":59.9,"total_ads":412,"active":0,"stage":"declining","market_est_daily_spend_usd":49},
  {"id":"norles.com_16096223887747","title":"Anti-Reflux Baby Lounger","price_usd":119.99,"market_active_ads":118,"market_est_daily_spend_usd":47,"stage":"scaling"},
  {"id":"littlejax.co.uk_7681038745854","title":"Luxury Wedge Pillow","price_usd":79.0,"total_ads":35,"stage":"emerging"}],
 "search_totals":{"q wedge pillow":251,"q intimacy pillow":102}})
dump("ads_comfysleepers.json", {"_note":"CONDENSED verbatim; 645 ads total on the pillow landing URL. Status field 'active' even for past end_date (as returned).",
 "longest_running_on_pillow_url":[
  {"id":"2322333648296176","start":"2026-05-19","end":"2026-08-15","format":"image","headline":"The Intimacy Support Pillow","copy":"\"This is one of those things you don't know you need until you try it. This Waterproof Intimacy Pillow from Comfy Sleepers has made intimacy feel effortless again.\" | \"I bought it as a bit of a joke... My partner said it's the best she's ever had.\" | \"It's honestly wild how much this has improved our intimacy... We've found our rhythm again\"","adspy_ig":{"likes":33,"comments":2}},
  {"id":"1531237431991100","start":"2026-05-19","end":"2026-08-15","format":"image","copy":"same testimonial block"},
  {"id":"1298520482493061","start":"2026-05-25","end":"2026-07-08","format":"image","headline":"Bring Back The Spark","copy":"\"She stopped feeling distant... and started reaching for me again.\" Helps reduce awkward pressure & physical tension ... 30 nights to try it. After that, your relationship will decide for you"},
  {"id":"979761628132657","start":"2026-05-27","end":"2026-07-12","format":"video","copy":"testimonial block"},
  {"id":"976138665021204","start":"2026-06-05","end":"2026-08-15","format":"image","copy":"She Leaned In & Whispered, \"That Felt Incredible Can We Do It Again?\" ... Her Ultimate Comfort = Your Unstoppable Confidence ... Don't Let Ordinary Pillows Kill The Mood. Upgrade The Way You Love","adspy_ig":{"likes":16,"comments":0}},
  {"id":"4788461118120198","start":"2026-06-05","end":"2026-07-12","format":"video","headline":"Bring Back The Spark"}],
 "newest_pillow_ads":[
  {"id":"1789119665627613","start":"2026-11-11","format":"image","headline":"Halloween Sale Is Live","copy":"69% Off + 4 Free Gifts ... With A 27 deg Lift That Keeps The Body Aligned ... Comfort That Lasts / Better Angles / Stronger Connection ... 75k+ Couples Already Made The Switch ... Buy 1 Get 4 Free Gifts"},
  {"id":"2192236514976618","start":"2026-11-10","headline":"Black Friday Sale Is Live","copy":"69% Off ... 75k+ Couples Already Made The Switch"},
  {"id":"1124911970435875","start":"2026-11-11","headline":"Black Friday Sale Is Live"},
  {"id":"2944566152585193","start":"2026-11-11","headline":"Halloween Sale Is Live"},
  {"id":"2183347482261511","start":"2026-11-10","headline":"Halloween Sale Is Live"}],
 "older_store_ads":"6 longest-running store ads (2025-04..06 starts) are cooling blanket / snore cervical pillow, e.g. 1026858649632589 (2025-04-18 -> 2026-05-09), 1388031142444311 (2025-04-24 -> 2026-04-28): store pivoted into intimacy pillow ~2026-05"})
dump("ads_clones.json", {"_note":"CONDENSED verbatim",
 "belleaparis.com":[{"id":"1059927916884343","start":"2026-09-22","end":"2026-10-04","format":"video","headline":"Le coussin de soutien intime","copy":"FR translation of comfysleepers testimonial block","link_description":"Angle de 27 deg, housse impermeable, 30 jours satisfait ou rembourse"},{"id":"2510595066113325","format":"video","headline":"Ravivez la flamme","copy":"FR translation of 'Bring Back The Spark', 30 jours pour l'essayer"}],
 "ripozen.com via advertiser page brilocasa.com":[{"id":"1032521416190160","start":"2026-07-27","end":"2026-08-13","format":"video","headline":"Il Cuscino Di Sostegno Per L'Intimita","copy":"Dai 20 Ai 60 Anni ... Inclinazione Di 27 deg ... Memory Foam Rigido ... Basta Impilare Cuscini Normali","eu_spend_eur":3.54},{"id":"2112065309377932","format":"image","link_description":"Benvenuto su RipoZen, la soluzione definitiva contro il russamento ... (store is an anti-snoring shop)"}],
 "cosalia-home.com":"top ads returned were an unrelated blanket (ES 'sabana-cosalia'); no pillow-ad data pulled",
 "note":"clones run ads from rotating advertiser pages (brilocasa.com for ripozen.com), so brand_ids filters undercount"})

# comments probe log
os.makedirs(os.path.join(here, "..", "comments"), exist_ok=True)
with open(os.path.join(here, "..", "comments", "probe_log.json"), "w", encoding="utf-8") as f:
    json.dump({"_note":"Instagram-matched ads across all 20+ market brands (query q=intimacy, adspy_platform=instagram, sort adspy_comments) plus landing-page query: only 2 ads returned in total.",
      "probes":[{"ad_id":"2322333648296176","brand":"comfysleepers.com","adspy_ig_comments":2,"adspy_ig_likes":33,"api_comments_total":0,"called":True},
                {"ad_id":"976138665021204","brand":"comfysleepers.com","adspy_ig_comments":0,"adspy_ig_likes":16,"called":False,"reason":"<5 comments"}],
      "result":"no ad with >=5 IG comments; 0 comments returned; no raw_ files saved"}, f, indent=1)

# sellers.csv with computed stats
with open(os.path.join(here, "sellers.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["brand_id","url_id","price_usd","total_ads","active_ads","ads_30d","first_advertised_at","est_daily_spend_usd","market_language"])
    for m in members:
        w.writerow([m[1], m[0], m[4], m[5], m[6], m[7], m[8], m[9] if m[9] is not None else "", lang.get(m[1], "")])
brands = {}
for m in members:
    b = brands.setdefault(m[1], [0, 0])
    b[0] += m[5]; b[1] += m[6]
prices = [m[4] for m in members]
tot = sum(b[0] for b in brands.values()); act = sum(b[1] for b in brands.values())
stats = {"distinct_brands": len(brands), "brands_with_active_ads": sum(1 for b in brands.values() if b[1] > 0),
         "total_ads": tot, "active_ads": act,
         "comfysleepers_share_total_pct": round(100 * brands["comfysleepers.com"][0] / tot, 1),
         "comfysleepers_share_active_pct": round(100 * brands["comfysleepers.com"][1] / act, 1),
         "price_usd_min": min(prices), "price_usd_median": statistics.median(prices), "price_usd_max": max(prices),
         "non_english_sellers": sum(1 for b in brands if not lang[b].startswith("EN"))}
print(json.dumps(stats, indent=1))
dump("stats.json", stats)
