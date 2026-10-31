"""Write a Shopify product import CSV (Admin > Products > Import) from a small JSON spec.

Usage:
  python -I product_csv.py spec.json --out PRODUCT_DIR/08_shopify/<slug>-products.csv [--image-base-url URL]

spec.json: {"products": [{
    "handle": "mojo-silk-boxers-sustainable-comfort",
    "title": "Mojo silk boxers | Premium Comfort, Sustainably Made",
    "vendor": "Mojo", "type": "Underwear", "tags": ["silk", "boxers"],
    "body_html": "<p>...</p>",
    "status": "draft",                       # draft | active (default draft: the operator reviews, then activates)
    "options": [{"name": "Colour", "values": ["Beige", "Black"]}, {"name": "Size", "values": ["S", "M"]}],
    "price": "29.95", "compare_at": "50.00",
    "price_overrides": {"Black / XL": "31.95"},   # optional, keyed by "value1 / value2"
    "sku_prefix": "MOJO-SB", "grams": 60,
    "images": [{"file": "03_product-images/.../01.png", "alt": "..."}],   # gallery order; "src" = URL overrides file
    "variant_images": {"Beige": "03_product-images/.../pair-beige.png"},  # by first option value
    "seo_title": "...", "seo_description": "...",
    "template_suffix": "mojo"               # not a CSV column: written to the checklist for the operator
}]}

Image Src must be a public URL. With --image-base-url, local files map to <base>/<file name>; without it the
image cells stay empty and <out>.UPLOAD.md lists the files in gallery order for a manual upload.
Inventory is not tracked (policy "continue") so variants never show as sold out on a dropshipping test.
"""
import argparse, csv, itertools, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
COLS = ["Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", "Published",
        "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name", "Option3 Value",
        "Variant SKU", "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Policy",
        "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price", "Variant Requires Shipping",
        "Variant Taxable", "Variant Barcode", "Image Src", "Image Position", "Image Alt Text", "Gift Card",
        "SEO Title", "SEO Description", "Variant Image", "Variant Weight Unit", "Status"]

ap = argparse.ArgumentParser(description="Shopify product import CSV from a JSON spec.")
ap.add_argument("spec")
ap.add_argument("--out", required=True)
ap.add_argument("--image-base-url", default="")
a = ap.parse_args()
spec = json.load(open(a.spec, encoding="utf8"))
base_dir = os.path.dirname(os.path.abspath(a.spec))


def url(img):
    if isinstance(img, dict) and img.get("src"):
        return img["src"]
    f = img["file"] if isinstance(img, dict) else img
    return f"{a.image_base_url.rstrip('/')}/{os.path.basename(f)}" if a.image_base_url else ""


rows, upload, notes = [], [], []
for p in spec["products"]:
    opts = p["options"][:3]
    combos = list(itertools.product(*[o["values"] for o in opts])) or [("Default Title",)]
    if not opts:
        opts = [{"name": "Title", "values": ["Default Title"]}]
    imgs = p.get("images", [])
    vimg = p.get("variant_images", {})
    for i, combo in enumerate(combos):
        key = " / ".join(combo)
        r = dict.fromkeys(COLS, "")
        r.update({"Handle": p["handle"],
                  "Variant SKU": f'{p.get("sku_prefix", p["handle"][:8].upper())}-' + "-".join(c.replace(" ", "")[:4].upper() for c in combo),
                  "Variant Grams": p.get("grams", 0), "Variant Inventory Tracker": "",
                  "Variant Inventory Policy": "continue", "Variant Fulfillment Service": "manual",
                  "Variant Price": p.get("price_overrides", {}).get(key, p["price"]),
                  "Variant Compare At Price": p.get("compare_at", ""), "Variant Requires Shipping": "TRUE",
                  "Variant Taxable": "TRUE", "Variant Weight Unit": "g",
                  "Variant Image": url(vimg[combo[0]]) if combo[0] in vimg else ""})
        for n, (o, v) in enumerate(zip(opts, combo), 1):
            r[f"Option{n} Name"] = o["name"] if i == 0 else ""
            r[f"Option{n} Value"] = v
        if i == 0:
            r.update({"Title": p["title"], "Body (HTML)": p.get("body_html", ""), "Vendor": p.get("vendor", ""),
                      "Product Category": p.get("category", ""), "Type": p.get("type", ""),
                      "Tags": ", ".join(p.get("tags", [])), "Published": "TRUE", "Gift Card": "FALSE",
                      "SEO Title": p.get("seo_title", ""), "SEO Description": p.get("seo_description", ""),
                      "Status": p.get("status", "draft")})
        if i < len(imgs) and url(imgs[i]):
            r.update({"Image Src": url(imgs[i]), "Image Position": i + 1,
                      "Image Alt Text": imgs[i].get("alt", "") if isinstance(imgs[i], dict) else ""})
        rows.append(r)
    for j in range(len(combos), len(imgs) if a.image_base_url else 0):  # extra image-only rows (need URLs)
        r = dict.fromkeys(COLS, "")
        r.update({"Handle": p["handle"], "Image Src": url(imgs[j]), "Image Position": j + 1,
                  "Image Alt Text": imgs[j].get("alt", "") if isinstance(imgs[j], dict) else ""})
        rows.append(r)
    if not a.image_base_url:
        upload.append((p, imgs, vimg))
    if p.get("template_suffix"):
        notes.append(f'- {p["handle"]}: set Theme template to "product.{p["template_suffix"]}" (not a CSV column)')

os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
with open(a.out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)

md = [f"# Shopify import: {os.path.basename(a.out)}", "",
      "1. Admin > Products > Import > choose this CSV (leave \"Overwrite products with matching handles\" off unless updating).",
      "2. After import, open each product and:"] + [f"   {n}" for n in notes] + [
      "   - check prices / compare-at, then set Status to Active when the page is ready.",
      "3. Shipping rates for every market must exist, or the product shows as sold out and add to cart fails."]
for p, imgs, vimg in upload:
    md += ["", f"## Images to upload for {p['handle']} (in this order)"]
    md += [f"{k}. `{im['file'] if isinstance(im, dict) else im}`" + (f" (alt: {im.get('alt')})" if isinstance(im, dict) and im.get('alt') else "")
           for k, im in enumerate(imgs, 1)]
    if vimg:
        md += ["", "Variant images (assign by colour):"] + [f"- {k}: `{v}`" for k, v in vimg.items()]
open(os.path.splitext(a.out)[0] + ".UPLOAD.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print(f"{len(rows)} rows, {len(spec['products'])} product(s) -> {a.out}")
print(f"checklist -> {os.path.splitext(a.out)[0]}.UPLOAD.md")
