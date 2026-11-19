# MARKET: pet-hair-glove (2026-11-19, Brandsearch, ~75 credits used)
Raw/condensed data: market/ (market_softpet.json, trend_softpet.json, audience.json, similar.json, sellers.csv, lookalikes.csv, build.py). Note: raw responses are condensed by hand into these files, not verbatim dumps.

## Market size
- ES market (softpet.es_15471612821836): 7 listings / 5 brands (softpet.es x3 listings, cleveria.store, cuidamascota.es, formy.es, petzuno.store). 983 total ads, 419 active, all active ads are softpet (cleveria/cuidamascota/formy/petzuno show 0 active now; they ran 14-29 ads each, mostly started Nov 1-10).
- Audience (1,077 ads): ES 99.2%, PT 0.8%; women 67.1%; 45-54 = 30.5%, 55-64 = 21%, 35-44 = 21.5%.
- Look-alikes (36 stores in lookalikes.csv, 19 with active ads) by language:
  - ES-local: tiendapelora.com (ES, 4 ads), trendyplus.online (Dropea, 92 ads, 0 active, declining), sporteletro.com (PT-language copy, 0 active). LatAm: baratitogt (GT), wolfytienda/nuvorashop/clickhub (CL), tiendakivo; all 2-8 ads, tiny.
  - DE/CH: mysera.de (75 ads, 0 active, $8-10k/mo market est, declining), amarelu.de, enliy.shop, fluffbesen.de, reinhab-de.com, mein-einfach-zuhause.de (45 ads, 0 active), azena.ch, fellstopp.ch (6 active, CHF 29.90), mypetly.ch. None active at scale; Germany market "declining".
  - IT: varibeestore.com (289 ads, 26 active, ~$190/day, $26-34k/mo market, declining), petplaz.com (123 ads, 8 active), rinopaws.shop (57, 6 active), mimers.it.
  - FR: pawshome.fr (19 ads, 0 active), splooty.fr, shop-ovoo.com, nouvina.com, pilpoilshop.com, pawkitpro.com; kaneo-shop.com (8 active, started 2026-11-17). All declining/small, none scaling.
  - EN: stridepaws.com (121 ads, 59 active, BOGO $23.99), zyntira.com (46 active, BOGO $19.99), getfurzilla.com (48 active), urbanstylehaven.com (80 ads, all ran Dec-Jan), pawlyticlab.com (235 ads, 69 active, $38.99), easylivinguk.co.uk (UK, 4 active, GBP 14.99). US spend invisible to Brandsearch.

## Price and offer
- ES: min/median/max $20.79 / $25.91 / $26.99 (EUR 19.99-24.99). softpet EUR 23.99; petzuno $20.79; cuidamascota EUR 19.99 (3 variants).
- DE/CH EUR 12.95-37.79; IT EUR 25.90-28.99; FR EUR 19.90-29.95; EN US $19-39.
- Offers: free shipping + cash on delivery ("Envio contrareembolso gratis", ad 1486100179747799); "Envio gratis solo hoy" (ad 2340576499760062); 100-day money-back guarantee; Black Friday 50% off + third free (ad 4585056855069248); BOGO is the standard EN offer (stridepaws, zyntira); 2+1 / 2x1 in PT/LatAm (sporteletro, emeyestore).

## Angles / mechanism
- softpet winner copy (ids 25318282087871934, 1486100179747799, 2340576499760062): problem-agitation ("rodillos que apenas funcionan, cepillos, aspiradora asusta a tu mascota... lo has probado todo") then mechanism "tecnologia electrostatica" + double-sided, works on sofa/bed/rug/clothes/car, pet enjoys it (petting, not fighting), testimonial ("5 minutos recoge mas que mi cepillo caro en 20"). Hook: "Ganale la batalla al pelo de tu mascota." Format: video, product funnel, COD.
- Newest BFCM ads (4585056855069248, 1105946858943133): "Si compraste la SoftPET esta semana, lo sentimos. Te mentimos en una cosa... el precio" reverse-confession price copy; "arranca el pelo incrustado", "se lava con agua y dura meses, sin recambios".
- Others: IT petplaz "metodo piu veloce ... in 10 secondi"; DE "Fellmagnet", "FluffAway"; EN "Last Day Promotion 49% OFF electrostatic gloves", BOGO.

## Longevity
- softpet 25318282087871934: Jan 19 - Sep 16 2026 (240 days), EU spend EUR 33,074, reach 3.51M (status inactive now). 1486100179747799 / 3294414420735492: Feb 13 - Jul 3 (140 days, low spend EUR 85-120). 2340576499760062: Apr 9 - Jul 13. Store first advertised 2026-01-07, so ~10.5 months of continuous scaling.

## Spend direction (get_product_trend 90d)
- Market est. daily spend $930 (Aug 22) -> ~$1,000-1,100 (Sep-Oct) -> $3,200-3,700 (Nov 9-18, BFCM bump) -> $2,900 (Nov 19). Active ads 146 -> 419; total ads 300 -> 907; advertisers 3 -> 5 (Sep 16). Growing, but the late jump is Black Friday-driven and may fall back after Cyber Monday. Revenue band whole market $390-510k/mo (modelled).
- Followers entering Nov 2026: cleveria (ad start 2026-11-06), cuidamascota (11-10), petzuno (11-01), softpet launched 2nd/3rd listings Oct 31/Nov 7 (121 and 31 ads). All four copycats are exact-product clones (same URL slug "manopla-quita-pelos-mascota") with 0 active ads now: they tested and stopped within ~1-2 weeks.

## Concentration
- softpet = 907/983 ads (92%) and 100% of active ads. One dominant seller, no patent or brand moat visible (generic AliExpress-type glove, 1 variant, EUR 23.99). Moat is ad volume/creative testing, COD logistics and review/UGC. Not tied to a unique formula.

## Sophistication (Schwartz)
- Spain: stage 2-3. The category "pet hair removal" is well known (rollers, brushes named in the copy as failed), so the claim alone is not new; softpet uses a mechanism (electrostatic double-sided) and "tried everything" framing = stage 3. Globally (EN/DE/IT/FR) the glove is stage 3-4: dozens of clones, "49% OFF last day" and BOGO price games; buyers need a new mechanism/proof or brand/price angle.

## Sourcing / margin
- sourcing_available=false (no 1688 match). Assumption, not from data: such gloves are typically $1-2.5 landed per unit, light, small, no battery/liquid/sizing: very easy shipping. At ~EUR 24 sell price the gross margin is large (~85-90% before shipping/fees), which is why 6 clones and COD work. Free shipping + COD in ES lowers net.

## Gaps
- Unserved/under-served language markets: Spain is owned by one seller but the four followers failed; PT-PT (only sporteletro, 2 ads, 0 active) and FR (all declining, no scaler; kaneo-shop new 8 ads) are open; DE/AT/CH has many short-lived tests but no scaler (mysera 75 ads ended Nov 6); IT has one declining leader (varibee). UK has no scaler (easylivinguk 4 active). Unused angles: older/45-64 female skew is already targeted; no one leads with allergy/asthma, baby/crawling floor, car-seat, or "rent to cat owners" use; none seen with lint/vet-recommended proof.
- Unused avatar: seniors/55+ (21% + 7% of reach), allergy sufferers, multi-pet households.

## One-line read
ES is a real, scaling market but 92% owned by softpet with high ad volume ($2.9k/day, 419 active ads) and recent follower clones all stopped within days; the realistic room is in a language market without a scaler (FR, DE/CH, IT, PT-PT), with a distinct mechanism/offer, not a straight ES clone. Product is trivially cheap to source and ship.
