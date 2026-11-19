import csv,json,statistics
# CONDENSED copy of get_product_sellers pages 1-2 (fields verbatim: brand_id,url,price_usd,total_ads,active_ads,first_advertised_at)
S="""nuvebrand.com|https://nuvebrand.com/products/silk-3-pro|189.0|2848|1034|2025-11-02
luneofficial.nl|https://luneofficial.nl/products/lune-silk-pro|42.12|283|154|2026-07-22
yombeuna-store.myshopify.com|https://yombeuna-store.myshopify.com/products/silk-3-pro|14.83|15|6|2026-05-13
elvaras.co|https://elvaras.co/products/professional-skin-smoothing-callus-remover|39.0|5|5|2026-04-13
nakura-paris.fr|https://nakura-paris.fr/products/nakura-softskin-pro|39.0|125|0|2026-02-02
beautybliss.se|https://beautybliss.se/products/silk-pro|399.0|108|0|2026-03-04
lyvabeauty.se|https://lyvabeauty.se/products/silk-pro|399.0|69|0|2026-07-02
noritokyo.com|https://noritokyo.com/products/silk|27.0|55|0|2026-01-20
norifeet.com|https://norifeet.com/products/silk|27.0|51|0|2026-06-13
solevia.uk|https://solevia.uk/products/footglow|29.95|35|0|2026-01-18
nuveo.pl|https://nuveo.pl/products/nuveo-silk|84.99|26|0|2026-08-31
frekkes.com|https://frekkes.com/products/electric-foot-callus-remover|34.95|23|0|2025-12-31
velurra.co.uk|https://velurra.co.uk/products/velurra-callus-remover|38.09|17|0|2026-06-17
lovelle.se|https://lovelle.se/products/lovelle-smooth-pro|46.45|14|0|2026-08-11
novalane.it|https://novalane.it/products/lima-elettrica-per-la-rimozione-dei-calli|21.49|12|0|2026-11-11
elystia.com|https://elystia.com/products/elystia-silk-3|42.12|10|0|2026-10-14
soleviabrand.com|https://soleviabrand.com/products/shampoing-solide-coreen|24.83|10|0|2026-10-04
mouzn.com|https://mouzn.com/products/silk-3-pro|39.0|9|0|2026-02-15
naliaco.com|https://naliaco.com/products/ponceuse|42.12|8|0|2026-11-03
snapsi.store|https://snapsi.store/products/lissea-smoo-pro|21.49|8|0|2026-01-30
venulia.com|https://venulia.com/products/lime-pied-electrique|29.99|8|0|2026-06-01
yveria.com|https://yveria.com/products/yveria-ponceuse-electrique-pieds-fini-les-callosites|86.39|8|0|2026-10-23
norvae.se|https://norvae.se/products/elektrisk-fotfil-forhardnadsborttagare-for-mjuka-valvardade-fotter|27.46|6|0|2026-04-25
gukami.nl|https://gukami.nl/products/elora-silk-verwijdert-hardnekkig-eelt-voor-zijdezachte-gladde-voeten||5|0|2026-11-01
leboria.com|https://leboria.com/products/rape-electrique-silk-pro|53.95|5|0|2026-10-26
rosalba.eu|https://rosalba.eu/products/raspa-elettrica-rosalba|43.09|5|0|2026-08-25
shopformfunction.com|https://shopformfunction.com/products/heel-recovery-device|38.09|5|0|2026-06-26
househarmony.it|https://househarmony.it/products/lissea-smoo-pro|21.49|4|0|2026-10-22
miazelia.com|https://miazelia.com/products/azelia-dolce-pro|42.12|4|0|2026-11-07
sculptiq.nl|https://sculptiq.nl/products/sculptiq-pedi-pro-3|37.75|3|0|2026-11-08
shopsoely.com|https://shopsoely.com/products/silk-pro|42.01|3|0|2026-10-16
trysilvora.com|https://trysilvora.com/products/silk-3-pro|43.15|3|0|2026-11-11
altiorae.com|https://altiorae.com/products/lune-silk-pro|42.12|2|0|2026-11-09
huishelden.online|https://huishelden.online/products/silk-3-pro|37.75|2|0|2026-07-26
lanivia.com|https://lanivia.com/products/velfeet|75.49|2|0|2026-09-13
thefound.es|https://thefound.es/products/velv|39.99|2|0|2026-11-12
vitarialife.com|https://vitarialife.com/products/sole-silk-pro|43.09|2|0|2026-11-11
dailiva.com|https://dailiva.com/products/dailiva-rimuovi-calli-professionale|43.09|1|0|2026-11-12
danvella.com|https://danvella.com/products/elektrisk-fodfil-haard-hud|43.35|1|0|2026-11-11
primma.fi|https://primma.fi/products/ammattilaisen-kovettumienpoistaja|19.95|1|0|2026-11-13
xelae.com|https://xelae.com/products/silk-3-pro-xelae|39.96|1|0|2026-11-08"""
rows=[l.split('|') for l in S.split('\n')]
tld=lambda b:b.rsplit('.',1)[-1]
with open('sellers.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['brand_id','url','price_usd','total_ads','active_ads','first_advertised_at','tld'])
    for r in rows:w.writerow(r+[tld(r[0])])
act=[r for r in rows if int(r[4])>0]
pr=[float(r[2]) for r in rows if r[2]]
print('sellers listed',len(rows),'(API total 41; get_product says 42)')
print('active sellers',len(act),[r[0] for r in act])
print('price min/median/max',min(pr),statistics.median(pr),max(pr))
print('first-ad in last 30d',sum(r[5]>='2026-10-20' for r in rows))
print('NL tld',[r[0] for r in rows if tld(r[0])=='nl'])
