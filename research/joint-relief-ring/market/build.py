# Builds sellers.csv from CONDENSED copies of Brandsearch card fields (values copied verbatim from tool responses, 2026-11-19).
import csv, json
# (brand_id, market, url, price_usd, total_ads, active_ads, first_advertised_at, est_daily_spend_usd, countries_or_lang, note)
R = [
("tryevercalm.co.uk","joint (own market)","https://tryevercalm.co.uk/products/evercalm-ring-relief-for-stiff-aching-joints",50.79,230,142,"2026-11-06T10:47:35Z",2400,"GB 100% (EU/UK audience)","GBP 39.99; card first-adv Nov 6 but joint ads seen from 2026-10-01"),
("tryevercalm.co.uk","calmi market (earlier product)","https://tryevercalm.co.uk/products/evercalm-ring-the-original",39.99,69,0,"2026-02-24T15:40:07Z",None,"GB","earlier EverCalm product, last ad 2026-06-16"),
("tryevercalm.com","joint clone","https://tryevercalm.com/products/evercalm-ring-relief-for-stiff-aching-joints",63.49,4,4,"2026-11-17T19:48:23Z",None,"EN (GBP 49.99)","same operator, 4 ads"),
("tryevercalm.de","joint clone DE","https://tryevercalm.de/products/evercalm-ring-gelenke",53.99,4,4,"2026-11-18T21:09:14Z",None,"DE (EUR 49.99)","same operator, German, 4 ads"),
("mycalmi.com","calmi market","https://mycalmi.com/products/calmi-ring-the-original",58.9,3932,878,"2025-06-10T16:10:00Z",1000,"25 countries (market.country_count)","category leader, saturated"),
("corelo.co","calmi market","https://corelo.co/products/corelo-ring",39.99,1,0,"2026-07-05T21:45:59Z",None,"",""),
("mymoonasleep.com","calmi market","https://mymoonasleep.com/products/moonaring",34.99,35,0,"2026-07-11T23:50:00Z",None,"",""),
("myrelaxea.com","calmi market","https://myrelaxea.com/products/ring",390.0,41,0,"2026-06-16T22:22:45Z",None,"",""),
("vitalx.uk","calmi market","https://vitalx.uk/products/vital-x-ring-the-original",43.04,3,0,"2026-11-03T05:16:35Z",None,"GB","menopause angle"),
("zariajewellery.com","calmi market","https://zariajewellery.com/products/viva-ring-the-original",34.9,1,0,"2026-11-07T21:19:06Z",None,"",""),
("sylvori.com","vitality market","https://sylvori.com/products/vitality-ring",24.9,1058,0,"2025-12-13T13:13:10Z",None,"3 countries","1,125 total ads in market, 3 active"),
("auvulis.com","vitality market","https://auvulis.com/products/vitality-ring-one-size-adjustable",29.9,67,3,"2025-12-31T17:16:17Z",None,"",""),
("theserenityring.com","serenity market","https://theserenityring.com/products/serenity-ring-the-original",34.95,53,0,"2025-12-30T17:24:29Z",None,"5 countries","13 sellers, saturated"),
("magneva.co","magneva market","https://magneva.co/products/magneva-kortisol",29.95,341,0,"2025-12-24T07:10:18Z",None,"5 countries","11 sellers, 268 market active ads, cortisol"),
("raviossa.com","hlux market","https://raviossa.com/products/hlux-wellness-ring-5-in-1-health-support",49.99,3,0,"2026-01-13T01:33:09Z",None,"5 countries","13 sellers, declining"),
("verdana-home.com","healthring","https://verdana-home.com/products/healthring-magnetic-acupressure-ring",34.28,3,0,"2026-06-23T07:27:47Z",None,"GB","acupressure magnetic ring, 3 ads only"),
("uk.aureliaring.com","aurelia","https://uk.aureliaring.com/products/aurelia-weight-loss-ring",38.04,95,56,"2026-11-03T20:13:48Z",17,"GB","weight-loss ring, new"),
("bymagnova.com","magnova","https://bymagnova.com/products/magnova-wellness-ring",38.04,28,0,"2026-08-13T03:11:34Z",None,"GB",""),
("butfirstbeautyshop.com","calmora","https://butfirstbeautyshop.com/products/bfs-calmora-ring-the-natural-menopause-relief-ring",48.25,19,0,"2026-09-08T03:20:57Z",None,"GB","menopause magnetotherapy ring"),
("oluxring.com","olux","https://oluxring.com/products/olux-bracelet",68.9,28,2,"2026-01-20T01:42:31Z",12,"11 countries","magnet bracelet, market est 240/d"),
("bealur.de","bealur DE","https://bealur.de/products/velara-ring-magnetischer-akupressur-ring-zur-vagusnervstimulation",53.98,120,0,"2026-04-28T18:52:41Z",None,"DE","magnetic acupressure ring, vagus nerve; market 39 active ads, est 66/d"),
("serenering.com","serene ES","https://serenering.com/products/serene-ring",34.99,73,0,"2026-03-23T17:47:51Z",None,"1 country (Spanish copy)","market 35 active ads"),
("dermapro.fr","tourmaring FR","https://dermapro.fr/products/tourmaring-equilibrez-votre-corps-appaisez-votre-esprit-perdez-du-poids",29.99,82,0,"2026-01-20T20:35:16Z",None,"3 countries, FR",""),
("ozkiz.shop","calmi FR","https://ozkiz.shop/products/calmi-ring-quilibre-et-lgance",49.9,24,0,"2026-11-10T23:40:50Z",None,"3 countries, FR",""),
("kobly.dk","veloria DK","https://kobly.dk/products/veloria-balansring",28.85,6,0,"2026-06-13T06:44:58Z",None,"DK","8 sellers"),
("dagligshop.dk","sundhedsring DK","https://dagligshop.dk/products/sundhedsring",32.62,28,0,"2025-12-25T00:30:14Z",None,"DK",""),
("debura.de","sleepbalance DE","https://debura.de/products/sleep-balance",43.09,29,0,"2026-08-28T18:27:58Z",None,"DE",""),
("redlightbuddy.com","vibration ring","https://redlightbuddy.com/products/slimming-massage-ring",32.95,26,16,"2026-09-09T03:19:51Z",1,"",""),
]
H=["brand_id","market","url","price_usd","total_ads","active_ads","first_advertised_at","est_daily_spend_usd","countries_or_language","note"]
with open("sellers.csv","w",newline="",encoding="utf8") as f:
    w=csv.writer(f); w.writerow(H); w.writerows(R)
joint=[r for r in R if "joint" in r[1]]
ring_active=[r for r in R if r[5]>0]
import statistics
p=[r[3] for r in R if r[3]<300]
print("rows",len(R),"with active ads",len(ring_active),"sum active",sum(r[5] for r in R))
print("price min/median/max (excl 390 outlier)",min(p),statistics.median(p),max(p))
