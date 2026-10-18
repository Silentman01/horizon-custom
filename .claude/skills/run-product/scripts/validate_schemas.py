"""Catch Shopify push errors that `shopify theme check` misses.

Usage: python -I validate_schemas.py <theme_root> [--prefix aurea-,refrain-]
Checks section/block schemas and JSON templates/groups for rules Shopify
enforces on `shopify theme push`.
"""
import glob, json, os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else "."
prefixes = None
if "--prefix" in sys.argv:
    prefixes = sys.argv[sys.argv.index("--prefix") + 1].split(",")

errs = []


def err(path, msg):
    errs.append(f"{os.path.relpath(path, root)}: {msg}")


def check_settings(path, settings, where):
    ids = [s.get("id") for s in settings if s.get("id")]
    for d in sorted({i for i in ids if ids.count(i) > 1}):
        err(path, f"{where}: duplicate setting id '{d}'")
    for s in settings:
        t, sid = s.get("type"), s.get("id")
        if t in ("header", "paragraph"):
            if not s.get("content"):
                err(path, f"{where}: {t} without content")
            continue
        if not sid:
            continue
        if "label" not in s:
            err(path, f"{where}.{sid}: missing label")
        elif isinstance(s["label"], str) and not s["label"].startswith("t:") and len(s["label"]) > 70:
            err(path, f"{where}.{sid}: label longer than 70 chars ({len(s['label'])})")
        if isinstance(s.get("info"), str) and not s["info"].startswith("t:") and len(s["info"]) > 500:
            err(path, f"{where}.{sid}: info longer than 500 chars")
        if "default" in s:
            d = s["default"]
            if (d == "" or d is None) and t in ("text", "textarea", "richtext", "inline_richtext", "html", "url", "liquid"):
                err(path, f"{where}.{sid}: empty default")
            if t == "range":
                mn, mx, st = s.get("min"), s.get("max"), s.get("step", 1)
                if not isinstance(d, (int, float)) or not (mn <= d <= mx):
                    err(path, f"{where}.{sid}: range default {d} outside {mn}..{mx}")
                elif round((d - mn) / st, 6) % 1:
                    err(path, f"{where}.{sid}: range default {d} not on step {st}")
            if t in ("select", "radio"):
                opts = [o.get("value") for o in s.get("options", [])]
                if d not in opts:
                    err(path, f"{where}.{sid}: default '{d}' not in options")
            if t == "richtext" and isinstance(d, str) and not re.match(r"\s*<(p|ul|ol|h[1-6])\b", d):
                err(path, f"{where}.{sid}: richtext default must start with <p>/<ul>/<ol>/<h1-6>")
            if t == "inline_richtext" and isinstance(d, str) and re.search(r"<(p|div|ul|ol|h[1-6])\b", d):
                err(path, f"{where}.{sid}: inline_richtext default has block tags")
            if t in ("image_picker", "video", "product", "collection", "blog", "page", "article", "product_list", "collection_list"):
                err(path, f"{where}.{sid}: type {t} cannot have a default")
            if t == "number" and not isinstance(d, (int, float)):
                err(path, f"{where}.{sid}: number default not numeric")
            if t == "url" and isinstance(d, str) and d not in ("/collections", "/collections/all"):
                err(path, f"{where}.{sid}: url default must be /collections or /collections/all")
        if t == "range":
            mn, mx, st = s.get("min"), s.get("max"), s.get("step", 1)
            if None in (mn, mx):
                err(path, f"{where}.{sid}: range missing min/max")
            elif (mx - mn) / st > 101:
                err(path, f"{where}.{sid}: range has more than 101 steps")
        if t in ("select", "radio") and not s.get("options"):
            err(path, f"{where}.{sid}: {t} without options")


def check_values(path, where, values, sch_settings, selects=True):
    by_id = {s["id"]: s for s in sch_settings if s.get("id")}
    for k, v in (values or {}).items():
        s = by_id.get(k)
        if not s:
            continue
        if s.get("type") == "range" and isinstance(v, (int, float)):
            if not (s["min"] <= v <= s["max"]):
                err(path, f"{where}.{k}: value {v} outside {s['min']}..{s['max']}")
        if selects and s.get("type") in ("select", "radio") and v not in [o.get("value") for o in s.get("options", [])]:
            err(path, f"{where}.{k}: value '{v}' not in options")


# Liquid files: one {% stylesheet %} / {% javascript %} / {% schema %} per file, no merge-conflict markers
for _p in glob.glob(os.path.join(root, "sections", "*.liquid")) + glob.glob(os.path.join(root, "blocks", "*.liquid")) + glob.glob(os.path.join(root, "snippets", "*.liquid")):
    _s = open(_p, encoding="utf-8").read()
    for _tag in ("stylesheet", "javascript", "schema"):
        if len(re.findall(r"{%-?\s*" + _tag + r"\s*-?%}", _s)) > 1:
            err(_p, f"duplicate {{% {_tag} %}} tag (Shopify allows one per file)")
    if re.search(r"^(<<<<<<<|>>>>>>>) ", _s, re.M):
        err(_p, "git merge-conflict markers")


schemas = {}
files = glob.glob(os.path.join(root, "sections", "*.liquid")) + glob.glob(os.path.join(root, "blocks", "*.liquid"))
for p in files:
    base = os.path.basename(p)
    if prefixes and not any(base.lstrip("_").startswith(x) for x in prefixes):
        # still load schema for template validation
        pass
    s = open(p, encoding="utf-8").read()
    m = re.search(r"{%-?\s*schema\s*-?%}(.*?){%-?\s*endschema\s*-?%}", s, re.S)
    if not m:
        continue
    try:
        sch = json.loads(m.group(1))
    except Exception as e:
        err(p, f"schema JSON invalid: {e}")
        continue
    kind = "sections" if os.sep + "sections" + os.sep in p or "/sections/" in p.replace("\\", "/") else "blocks"
    schemas[(kind, base[:-7])] = sch
    if prefixes and not any(base.lstrip("_").startswith(x) for x in prefixes):
        continue
    name = sch.get("name", "")
    if isinstance(name, str) and len(name) > 25 and not name.startswith("t:"):
        err(p, f"schema name '{name}' longer than 25 chars")
    check_settings(p, sch.get("settings", []), "settings")
    for b in sch.get("blocks", []):
        if "settings" in b:
            check_settings(p, b["settings"], f"block '{b.get('type')}'")
        if b.get("name") and len(b["name"]) > 25 and not b["name"].startswith("t:"):
            err(p, f"block name '{b['name']}' longer than 25 chars")
    if kind == "sections" and sch.get("tag") and sch["tag"] not in ("article", "aside", "div", "footer", "header", "section"):
        err(p, f"invalid tag '{sch['tag']}'")
    if isinstance(sch.get("max_blocks"), int) and sch["max_blocks"] > 50:
        err(p, "max_blocks above 50")
    local_types = {b.get("type") for b in sch.get("blocks", [])}
    for pr in sch.get("presets", []):
        if not pr.get("name"):
            err(p, "preset without name")
        check_values(p, f"preset '{pr.get('name')}'", pr.get("settings"), sch.get("settings", []), selects=False)
        pbl = pr.get("blocks", [])
        for b in (pbl.values() if isinstance(pbl, dict) else pbl):
            bt = b.get("type")
            if bt not in local_types and "@theme" not in local_types and "@app" not in local_types and ("blocks", bt) not in schemas and not glob.glob(os.path.join(root, "blocks", bt + ".liquid")):
                err(p, f"preset '{pr.get('name')}': block type '{bt}' not defined")
            lb = next((x for x in sch.get("blocks", []) if x.get("type") == bt and "settings" in x), None)
            if lb:
                check_values(p, f"preset block {bt}", b.get("settings"), lb["settings"], selects=False)
    btypes = [b.get("type") for b in sch.get("blocks", [])]
    for d in sorted({t for t in btypes if btypes.count(t) > 1}):
        err(p, f"duplicate block type '{d}'")


def strip_comment(txt):
    return re.sub(r"^\s*/\*.*?\*/", "", txt, flags=re.S)


def check_blocks(path, where, blocks, order, parent_sch):
    for bid, b in (blocks or {}).items():
        bt = b.get("type")
        local = next((x for x in parent_sch.get("blocks", []) if x.get("type") == bt), None)
        if local and "settings" in local:
            check_values(path, f"{where} block {bid}", b.get("settings"), local["settings"])
        else:
            theme_block = schemas.get(("blocks", bt))
            if theme_block is None and bt not in ("@app", "@theme") and not local:
                err(path, f"{where}: block type '{bt}' not found")
            if theme_block:
                check_values(path, f"{where} block {bid}", b.get("settings"), theme_block.get("settings", []))
                check_blocks(path, f"{where} block {bid}", b.get("blocks"), b.get("block_order"), theme_block)
    for o in order or []:
        if o not in (blocks or {}):
            err(path, f"{where}: block_order id '{o}' missing")


for p in glob.glob(os.path.join(root, "templates", "*.json")) + glob.glob(os.path.join(root, "sections", "*.json")):
    try:
        data = json.loads(strip_comment(open(p, encoding="utf-8").read()))
    except Exception as e:
        err(p, f"JSON invalid: {e}")
        continue
    for sid, sec in (data.get("sections") or {}).items():
        st = sec.get("type")
        sch = schemas.get(("sections", st))
        if sch is None:
            if not st.startswith("_") or ("blocks", st) not in schemas:
                err(p, f"section '{sid}': type '{st}' has no section file")
            continue
        check_values(p, f"section {sid}", sec.get("settings"), sch.get("settings", []))
        check_blocks(p, f"section {sid}", sec.get("blocks"), sec.get("block_order"), sch)
    for o in data.get("order", []):
        if o not in (data.get("sections") or {}):
            err(p, f"order id '{o}' missing")

sd = os.path.join(root, "config", "settings_data.json")
if os.path.exists(sd):
    txt = open(sd, encoding="utf-8").read()
    for h in sorted(set(re.findall(r'"(type_[a-z_]*font[a-z_]*)"\s*:\s*"([^"]+)"', txt))):
        print(f"font handle to verify in Shopify library: {h[0]} = {h[1]}")

for e in errs:
    print("ERROR", e)
print(f"{len(errs)} error(s)")
sys.exit(1 if errs else 0)
