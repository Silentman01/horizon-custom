"""Assemble PD/00_alpha/ALPHA_DOSSIER.md from the Step Alpha working files (α5; runbook 20 §10).
Usage: python -I assemble_dossier.py <PD> --title "<Product>" --context "<Competitor … · Market … · Built …>"
The ad-count part of the context line is added automatically from ad_inventory.json.
"""
import argparse
import json
import os
import re

_ap = argparse.ArgumentParser()
_ap.add_argument("pd")
_ap.add_argument("--title", required=True, help="product name for the H1")
_ap.add_argument("--context", required=True, help="competitor · market · built date line")
_args = _ap.parse_args()
PD = _args.pd
A = os.path.join(PD, "00_alpha")


def rd(rel):
    with open(os.path.join(A, rel), encoding="utf-8") as fh:
        return fh.read()


FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")


def demote(text, drop_h1=True):
    """Outside fences, turn #..### headings into ####; drop the first H1 if asked."""
    out, fence, dropped = [], None, False
    for ln in text.splitlines():
        m = FENCE.match(ln)
        if fence is None and m:
            fence = (m.group(1)[0], len(m.group(1)))
            out.append(ln)
            continue
        if fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not m.group(2).strip():
                fence = None
            out.append(ln)
            continue
        hm = re.match(r"^(#{1,3})\s+(.*)$", ln)
        if hm:
            if drop_h1 and hm.group(1) == "#" and not dropped:
                dropped = True
                continue
            out.append("#### " + hm.group(2))
            continue
        out.append(ln)
    return "\n".join(out).strip("\n")


def sections_by_h2(text):
    """split a file on '## ' headings (outside fences) -> {title: body}"""
    res, cur, buf, fence = {}, None, [], None
    for ln in text.splitlines():
        m = FENCE.match(ln)
        if fence is None and m:
            fence = (m.group(1)[0], len(m.group(1)))
        elif fence is not None and m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not m.group(2).strip():
            fence = None
        elif fence is None and ln.startswith("## "):
            if cur is not None:
                res[cur] = "\n".join(buf)
            cur, buf = ln[3:].strip(), []
            continue
        if cur is not None:
            buf.append(ln)
    if cur is not None:
        res[cur] = "\n".join(buf)
    return res


def fenced_blocks(text):
    """-> list of (start_idx, end_idx, lines) for ``` (3-char) fences, by line index"""
    lines = text.splitlines()
    res, fence, start = [], None, None
    for i, ln in enumerate(lines):
        m = FENCE.match(ln)
        if fence is None and m:
            fence, start = (m.group(1)[0], len(m.group(1))), i
        elif fence is not None and m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not m.group(2).strip():
            if fence[1] == 3:
                res.append((start, i, lines[start + 1:i]))
            fence = None
    return res


KEY = re.compile(r"^\s*([A-Z][A-Z0-9 /&()'.\-]*?)\s*:(.*)$")


def fields(block_lines):
    d, order, last = {}, [], None
    for ln in block_lines:
        m = KEY.match(ln)
        if m and not ln.startswith("  "):
            k = re.sub(r"\s+", " ", m.group(1)).strip()
            d.setdefault(k, m.group(2).strip())
            order.append(k)
            last = k
        elif last and ln.strip():
            d[last] = (d[last] + " " + ln.strip()).strip()
    return d, order


def cell(s, n=220):
    s = re.sub(r"\s+", " ", s or "").replace("|", "/").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def first_quote(s):
    m = re.search(r'"[^"]{3,}"|“[^”]{3,}”|«[^»]{3,}»', s or "")
    return m.group(0) if m else ""


def blocks_typed(text, first_key):
    out = []
    for _, _, ls in fenced_blocks(text):
        d, order = fields(ls)
        if order and order[0] == first_key:
            out.append((d, ls))
    return out


# ------------------------------------------------------------------ inputs
cust = sections_by_h2(rd("analysis1/1.1_customer.md"))
ck = {k.split()[0] + " " + (k.split()[1] if len(k.split()) > 1 else ""): v for k, v in cust.items()}


def cust_sec(prefix):
    for k, v in cust.items():
        if k.startswith(prefix):
            return demote(v, drop_h1=False)
    raise SystemExit(f"1.1_customer.md: no section {prefix}")


inv = json.load(open(os.path.join(A, "ad_inventory.json"), encoding="utf-8"))
ads = inv["ads"]
nvid = sum(1 for a in ads if str(a.get("format", "")).lower() == "video")
inventory_md = demote(rd("analysis1/1.2_ad_inventory.md"))
video_md = demote(rd("analysis1/1.2_video_ads.md"))
static_md = demote(rd("analysis1/1.2_static_ads.md"))
families_md = demote(rd("analysis1/1.2_caption_families.md"))
patterns_raw = rd("analysis1/1.2_patterns.md")
pi = patterns_raw.find("#### Video framework patterns")
patterns_cross = demote(patterns_raw[:pi]) if pi >= 0 else demote(patterns_raw)
patterns_video = demote(patterns_raw[pi:], drop_h1=False) if pi >= 0 else ""
cong = sections_by_h2(rd("analysis1/1.3_congruence.md"))
cong_page = "\n\n".join(demote(v, drop_h1=False) for k, v in cong.items() if not k.startswith("Congruence insights"))
cong_ins = next(v for k, v in cong.items() if k.startswith("Congruence insights"))
paths_md = demote(rd("analysis1/1.3_paths.md"), drop_h1=False)
cards_md = demote(rd("analysis1/1.4_angle_cards.md"))
hidden_md = rd("analysis2/2.1_hidden_angles.md")
syn_md = rd("analysis2/2.3_synthesis.md")
raw = rd("chatgpt/CHATGPT_RAW.md")
prompt = rd("chatgpt/CHATGPT_PROMPT.md")

# ------------------------------------------------------------------ 2.1 merge verdicts
syn_h = {}
for d, ls in blocks_typed(syn_md, "HIDDEN ANGLE"):
    m = re.search(r"\bH\d+\b", d.get("HIDDEN ANGLE", ""))
    if m:
        syn_h[m.group(0)] = d
# also accept short verdict blocks keyed "H#:" lines are not supported; require blocks
hid_lines = hidden_md.splitlines()
hblocks = []
for s, e, ls in fenced_blocks(hidden_md):
    d, order = fields(ls)
    if order and order[0] == "HIDDEN ANGLE":
        hblocks.append((s, e, d, ls))
if not hblocks:
    raise SystemExit("no H blocks in 2.1")
missing_v = []
new_blocks = []
for s, e, d, ls in hblocks:
    h = re.search(r"\bH\d+\b", d["HIDDEN ANGLE"]).group(0)
    sv = syn_h.get(h)
    body = [ln for ln in ls if not re.match(r"^\s*RESEARCH (VERDICT|EVIDENCE)\s*:", ln)]
    if sv is None or "RESEARCH VERDICT" not in sv:
        missing_v.append(h)
        verdict, evid = "", ""
    else:
        verdict, evid = sv["RESEARCH VERDICT"], sv.get("RESEARCH EVIDENCE", "")
    body += [f"RESEARCH VERDICT:   {verdict}", f"RESEARCH EVIDENCE:  {evid}"]
    new_blocks.append((h, "VALIDATED" in verdict.upper(), "```\n" + "\n".join(body) + "\n```"))
if missing_v:
    print("WARN no synthesis verdict for:", ", ".join(missing_v))
first_s, last_e = hblocks[0][0], hblocks[-1][1]
pre = "\n".join(hid_lines[:first_s])
post = "\n".join(hid_lines[last_e + 1:])
ordered = [b for b in new_blocks if b[1]] + [b for b in new_blocks if not b[1]]
hidden_out = demote(pre) + "\n\n" + "\n\n".join(b[2] for b in ordered) + ("\n\n" + demote(post, False) if post.strip() else "")

# ------------------------------------------------------------------ synthesis pieces
syn_secs = sections_by_h2(syn_md)


def syn_part(*prefixes):
    for k, v in syn_secs.items():
        for p in prefixes:
            if k.upper().startswith(p.upper()):
                return demote(v, drop_h1=False)
    raise SystemExit(f"2.3_synthesis.md: no section {prefixes}")


s22 = syn_part("2.2", "UNDERSERVED")
s23 = syn_part("2.3 EMOTIONAL", "EMOTIONAL TERRITOR", "UNTAPPED")
s24 = syn_part("2.4", "FUNNEL CONGRUENCE GAPS")
s26 = syn_part("2.6", "LANGUAGE BANK")
s27 = syn_part("2.7", "EMERGENT")
s28 = syn_part("2.8", "OPPORTUNITY ANGLE CARDS", "OPPORTUNITY")

# ------------------------------------------------------------------ Part 3 tables
vcards = [d for d, _ in blocks_typed(cards_md, "ANGLE")]
ocards = [d for d, _ in blocks_typed(s28, "ANGLE")]


def card_row(d, typ):
    cid = re.search(r"\b[VO]\d+\b", d["ANGLE"]).group(0)
    name = re.sub(r"^\s*[VO]\d+\s*[—–-]\s*", "", d["ANGLE"])
    hook = first_quote(d.get("HOOK TEMPLATES", "")) or cell(d.get("HOOK TEMPLATES", ""), 120)
    return f"| {cid} | {cell(name, 90)} | {typ} | {cell(d.get('CONFIDENCE',''), 60)} | {cell(d.get('AVATAR',''), 60)} | {cell(d.get('EMOTIONAL TRIGGER',''), 60)} | {cell(d.get('PROMISE',''), 160)} | {cell(d.get('FUNNEL CONGRUENCE',''), 80)} | {cell(hook, 160)} |"


t31 = ["| ID | ANGLE | TYPE | CONFIDENCE | AVATAR | EMOTIONAL TRIGGER | PROMISE | CONGRUENCE | LEAD HOOK |",
       "|---|---|---|---|---|---|---|---|---|"]
t31 += [card_row(d, "validated") for d in vcards] + [card_row(d, "opportunity") for d in ocards]

avs = [(d, "competitor") for d, _ in blocks_typed(cust_sec("1.1"), "AVATAR")] + \
      [(d, "underserved") for d, _ in blocks_typed(s22, "AVATAR")]
pains = [d for d, _ in blocks_typed(cust_sec("1.2"), "PAIN POINT")]


def rank(d):
    m = re.search(r"\d+", d.get("RANK", "99"))
    return int(m.group(0)) if m else 99


t32 = ["| ID | AVATAR | SOURCE | DEMOGRAPHICS | TRIGGER EVENT | AWARENESS | SOPHISTICATION | TOP PAINS | KEY PHRASE |",
       "|---|---|---|---|---|---|---|---|---|"]
for d, src in avs:
    aid = re.search(r"\bAV\d+\b", d["AVATAR"]).group(0)
    name = re.sub(r"^\s*AV\d+\s*[—–-]\s*", "", d["AVATAR"])
    tp = [p for p in sorted(pains, key=rank) if re.search(r"\b%s\b" % aid, p.get("AVATAR", ""))][:3]
    tps = "; ".join(cell(p["PAIN POINT"], 70) for p in tp) or cell(d.get("WHY UNDERSERVED", ""), 160)
    t32.append(f"| {aid} | {cell(name, 80)} | {src} | {cell(d.get('DEMOGRAPHICS',''), 160)} | {cell(d.get('TRIGGER EVENT',''), 140)} | {cell(d.get('AWARENESS STATE',''), 80)} | {cell(d.get('SOPHISTICATION',''), 80)} | {tps} | {cell(first_quote(d.get('CUSTOMER LANGUAGE','')) or d.get('CUSTOMER LANGUAGE',''), 160)} |")

# hook library: every ad block's hook
card_hook = {}
for d in vcards:
    cid = re.search(r"\bV\d+\b", d["ANGLE"]).group(0)
    card_hook[cid] = first_quote(d.get("HOOK TEMPLATES", ""))
t33 = ["| # | HOOK (VERBATIM) | TYPE | AD ID | ANGLE | TEMPLATE |", "|---|---|---|---|---|---|"]
n = 0
for src_md in (video_md, static_md):
    for _, _, ls in fenced_blocks(src_md):
        d, order = fields(ls)
        if not order or order[0] != "AD ID":
            continue
        hook = d.get("HOOK", "")
        q = first_quote(hook) or hook
        typ = ""
        mt = re.search(r"type:\s*([^—;]+)", hook)
        if mt:
            typ = mt.group(1).strip()
        vid = re.search(r"\bV\d+\b", d.get("ANGLE", ""))
        v = vid.group(0) if vid else cell(d.get("ANGLE", ""), 40)
        tmpl = card_hook.get(v, "") or "card hook templates in 1.11"
        n += 1
        t33.append(f"| {n} | {cell(q, 240)} | {cell(typ, 60) or 'see 1.8/1.9 HOOK'} | {cell(d['AD ID'], 400)} | {v} | {cell(tmpl, 160)} |")
for d in vcards + ocards:
    cid = re.search(r"\b[VO]\d+\b", d["ANGLE"]).group(0)
    for q in re.findall(r'"[^"]{3,}"|“[^”]{3,}”', d.get("HOOK TEMPLATES", "")):
        n += 1
        t33.append(f"| {n} | {cell(q, 240)} | template | {cid} card | {cid} | {cell(q, 160)} |")

# framework library: one row per video
t34 = ["| FRAMEWORK | BEAT MAP (BEAT · % OF TOTAL) | ADS | FORMATS | LONGEST RUN |", "|---|---|---|---|---|"]
run = {a.get("short_id"): a.get("run_days") for a in ads}
for _, _, ls in fenced_blocks(video_md):
    d, order = fields(ls)
    if order and order[0] == "AD ID" and "FRAMEWORK" in d:
        ids = re.findall(r"\bM\d+\b", d["AD ID"])
        rr = max([run.get(i) or 0 for i in ids] or [0])
        t34.append(f"| {cell(d['FRAMEWORK'], 200)} | {cell(d.get('BEAT MAP',''), 900)} | {', '.join(ids)} | {cell(d.get('FORMAT',''), 80)} | {rr} days |")

# 3.5 from 2.6 groups (+ ANGLE column copied from the bank's 5th column if present)
grp = {}
cur = None
for ln in s26.splitlines():
    hm = re.match(r"^####\s+(.*)$", ln)
    if hm:
        cur = hm.group(1).strip().lower()
        grp[cur] = []
    elif cur and ln.strip().startswith("|") and not re.match(r"^\|\s*[-:| ]+\|?$", ln.strip()) and not re.match(r"^\|\s*#\s*\|", ln.strip()):
        grp[cur].append([c.strip() for c in ln.strip().strip("|").split("|")])


def bank(gname, outname, col4):
    rows = None
    for k, v in grp.items():
        if k.startswith(gname):
            rows = v
    if rows is None:
        raise SystemExit(f"2.6 has no group {gname}")
    out = [f"#### {outname}", "", f"| # | PHRASE (VERBATIM) | SOURCE | {col4} |", "|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        extra = r[4] if len(r) > 4 and r[4] else (r[3] if len(r) > 3 else "")
        out.append(f"| {i} | {r[1]} | {r[2] if len(r) > 2 else ''} | {extra or 'all'} |")
    return "\n".join(out)


t35 = "\n\n".join([bank("hook", "Hooks", "ANGLE"), bank("headline", "Headlines", "ANGLE"),
                   bank("objection", "Objection handling", "OBJECTION"), bank("testimony", "Social proof", "ANGLE")])

# ------------------------------------------------------------------ write
counts = f"Ads in inventory: {len(ads)} ({nvid} video, {len(ads) - nvid} static/carousel)"
doc = f"""# {_args.title} — Step Alpha Intelligence Dossier

{_args.context} · {counts}

## PART 1: COMPETITOR MAP

### 1.1 Avatars (full profiles)

{cust_sec('1.1')}

### 1.2 Pain Points (ranked, with customer language)

{cust_sec('1.2')}

### 1.3 Desires & Dream Outcomes (ranked, with language)

{cust_sec('1.3')}

### 1.4 Objections (with competitor handling + gaps)

{cust_sec('1.4')}

### 1.5 Emotional Landscape (triggers by type)

{cust_sec('1.5')}

### 1.6 Unique Mechanism (UMS/UMP analysis)

{cust_sec('1.6')}

### 1.7 Ad Inventory (complete table)

{inventory_md}

### 1.8 Video Frameworks (beat maps, formats, patterns)

{video_md}

{patterns_video}

### 1.9 Ad Copy Patterns (hooks, sequences, CTAs)

{static_md}

#### Cross-ad pattern mining (all ads)

{patterns_cross}

#### Full verbatim letter bodies (PRIMARY TEXT by T-id)

{families_md}

### 1.10 Funnel Congruence (ad→page path scores)

{cong_page}

{paths_md}

#### Congruence insights

{cong_ins.strip()}

### 1.11 Validated Angle Cards

{cards_md}

## PART 2: OPPORTUNITY MAP

### 2.1 Hidden Angles (validated by research)

{hidden_out}

### 2.2 Underserved Avatars

{s22}

### 2.3 Emotional Territories Untapped

{s23}

### 2.4 Funnel Congruence Gaps (angles the competitor leaks traffic on — our opportunity)

{s24}

### 2.5 ChatGPT Raw Data (full market research output)

`````text
{raw.rstrip()}
`````

### 2.6 Language Bank (hook-ready, headline-ready, objection-ready phrases)

{s26}

### 2.7 Emergent Angles (from raw data)

{s27}

### 2.8 Opportunity Angle Cards

{s28}

## PART 3: QUICK-REFERENCE

### 3.1 Angle Cards (validated + opportunity, combined)

{chr(10).join(t31)}

### 3.2 Avatar Cards

{chr(10).join(t32)}

### 3.3 Hook Library (every hook from every ad + templates)

{chr(10).join(t33)}

### 3.4 Framework Library (every video framework + beat maps)

{chr(10).join(t34)}

### 3.5 Customer Language Bank (organized by use: hooks, headlines, objection handling, social proof)

{t35}

### 3.6 ChatGPT Prompt (ready to paste for this product)

`````text
{prompt.rstrip()}
`````
"""
out = os.path.join(A, "ALPHA_DOSSIER.md")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(doc)
print("wrote", out, os.path.getsize(out), "bytes;", len(t33) - 2, "hook rows;", len(t31) - 2, "cards;", len(t32) - 2, "avatars")
