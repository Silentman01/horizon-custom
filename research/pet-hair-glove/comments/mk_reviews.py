import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rows = [
("Isabel Fernandez Calvo",5,"2026-10-18","Me encantaron las manoplas quita pelos las mejores acabe con el pelo de una vez"),
("Joel Chaves fernandez",5,"2026-10-18","compre dos y tardo en llegar pero todo genial la manopla saca el pelo de mi gato"),
("Celia",1,"2026-10-13","¡Experiencia pésima, es una ESTAFA! Venden un producto de mala calidad de fabricación china"),
("cliente",1,"2026-10-08","Llevo más de 15 días esperando el pedido. La empresa dice que lo ha enviado"),
("Marinaor",1,"2026-09-27","Es una estafa ,me siento engañada y timada NO COMPRÉIS EN ESTA TIENDA"),
("cliente",1,"2026-09-17","Es un producto básico como el de cualquier bazar. No vale el precio que pide."),
("Laura Schvartz",1,"2026-09-16","Estafadores. Lo compré por 19.99€ y una vez pagado"),
("Maria Perez",1,"2026-09-11","Son unos estafadores mentirosos,te dicen en la publicidad q tienes 30 días de prueba gratis"),
("Mercedes Jiménez González",1,"2026-09-11","llevo 2 meses a que me contesten por estafarme!"),
("Ser Cam",1,"2026-09-09","No doy menos porque no hay. Estafa."),
("Isabel",1,"2026-09-07","Les pregunté por sus ofertas y promociones de 50% claramente sospechosas"),
("Maria Pilar",1,"2026-08-30","No limpia tanto como dice la publicidad."),
("Cristina",1,"2026-08-30","Solo me han entregado una de las manoplas que pedí."),
("MONTSERRAT GONZALEZ MARTINEZ",1,"2026-08-29","Acabo de recibir el pedido y no se ajusta para nada a lo que pagué."),
("Ana Canales",1,"2026-08-29","He recibido mis manoplas quitapelos y no son lo que prometen para nada"),
("Evamaria",1,"2026-08-27","La manopla Softpet NO FUNCIONA, no como dicen en su video y publicidad."),
("Mercè Gimeno",1,"2026-08-26","Un timo y una estafa."),
("Hortensia Galiano Alcala",1,"2026-08-19","son unos estafadores ,llevo desde el 5 de julio q hice el pedido del guante"),
("Beatriz Martos Borrallo",1,"2026-08-19","Nefasta experiencia tanto con el guante Sofpet como con la atención el cliente"),
("E MG",1,"2026-08-15","Empiezo a pensar que es un timo."),
("cliente (CL)",1,"2026-08-04","Muy mala experiencia , el cepillo quitapelosfunciona muy mal y estropea el tejido"),
("eliscabhotmail.com",1,"2026-07-26","Pésimo, perdieron el pedido y ni devuelven el importe ni lo envían de nuevo."),
("Núria TG",1,"2026-07-18","Haces dos meses pedí un guante quitapelos, el pedido no llega por dirección incompleta"),
("José Moral",1,"2026-07-16","Cuidado con lo que compráis aquí en Softpet, hacen publicidad engañosa"),
("Matías CASACCIA",3,"2026-07-08","El envío se tomó 10 días hábiles en arribar"),
("Geijinii Almendrini",1,"2026-06-28","Es un fraude su guante (manopla) quita pelos solo lo mueve de un lado al otro"),
]
out = [{"id": f"trustpilot_{i}", "source": "https://es.trustpilot.com/review/softpet.es", "channel": "trustpilot",
        "brand_id": "softpet.es", "author": a, "stars": s, "text": t, "created_at": d} for i, (a, s, d, t) in enumerate(rows, 1)]
json.dump(out, open("web_reviews.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
