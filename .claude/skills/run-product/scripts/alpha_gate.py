#!/usr/bin/env python3
"""alpha_gate.py - Step Alpha helper: quality gate, ad inventory builder, video beat metrics.

Python 3.9+ standard library only. Run with -I. Spec: references/19-step-alpha.md.
Runbook: references/20-step-alpha-runbook.md. Template: templates/ALPHA_DOSSIER.md.

Subcommands
  [check] PATH   ("check" is the default: `alpha_gate.py PD/00_alpha/ALPHA_DOSSIER.md` works)
      PATH = PD/00_alpha (folder) or a dossier .md file (its folder is used for the other files).
      Checks the 16 QUALITY GATE boxes of the spec as far as a script can, prints PASS / FAIL per box
      with reasons, MANUAL notes for the coordinator's judgment, WARN lines, and exits 1 on any FAIL.
      Folder files it reads: ALPHA_DOSSIER.md, ad_inventory.json, transcripts/<id>.txt,
      gemini/<id>.json, analysis1/*.md, analysis2/*.md, chatgpt/CHATGPT_PROMPT.md,
      chatgpt/CHATGPT_RAW.md.

  inventory --alpha-dir PD/00_alpha --dumps [platform:]FILE ... [--keyword KW ...]
            [--expected-total N] [--fetch-videos DIR] [--fetch-images DIR] [--fetch-transcripts]
      Builds / updates PD/00_alpha/ad_inventory.json from Brandsearch dumps (any format rank_ads.py
      reads: raw JSON, harness .txt, harness toolu_*.json). Merges rows by id, keeps what you already
      filled (short_id, angle, avatar, notes, excluded/review decisions). platform prefix: meta (default),
      tiktok, instagram, other. With --keyword, rows whose copy lacks every keyword go to "review" (the
      coordinator moves each to "ads" or "excluded" with a reason; the gate fails while "review" is
      not empty). --fetch-videos downloads video_hd_url / video_sd_url to DIR/<id>.mp4 (free, browser UA,
      URLs expire 3 days after the pull). --fetch-images does the same for non-video ads
      (DIR/<id>.<png|jpg|webp|gif>). --fetch-transcripts saves transcript_url text to
      transcripts/<id>.txt (free). Prints what still needs paid calls (transcribe_ad, download_ad).

  beats GEMINI.json [--duration SECONDS]
      Prints the 1.8 fields a script can compute from a video_gemini.py JSON: BEAT MAP (timestamp,
      duration, % of total, function), HOOK DURATION, VO/TEXT SPLIT (% VO / % on-screen text only /
      % music-only), PACING (WPS average + per beat). --duration = real length (ffprobe); Gemini's
      duration_s can be ~1.5x off, so every time is rescaled by real/reported.

Examples
  python -I alpha_gate.py check "D:/Ecom/Products/_plaims/00_alpha"
  python -I alpha_gate.py inventory --alpha-dir "PD/00_alpha" --dumps meta:dump1.txt tiktok:toolu_x.json --keyword insole
  python -I alpha_gate.py beats "PD/00_alpha/gemini/123.json" --duration 31.4
"""
import argparse
import glob
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")

# ----------------------------------------------------------------------------- structure
H1_SUFFIX = "— Step Alpha Intelligence Dossier"
HEADINGS = [
    (2, "PART 1: COMPETITOR MAP"),
    (3, "1.1 Avatars (full profiles)"),
    (3, "1.2 Pain Points (ranked, with customer language)"),
    (3, "1.3 Desires & Dream Outcomes (ranked, with language)"),
    (3, "1.4 Objections (with competitor handling + gaps)"),
    (3, "1.5 Emotional Landscape (triggers by type)"),
    (3, "1.6 Unique Mechanism (UMS/UMP analysis)"),
    (3, "1.7 Ad Inventory (complete table)"),
    (3, "1.8 Video Frameworks (beat maps, formats, patterns)"),
    (3, "1.9 Ad Copy Patterns (hooks, sequences, CTAs)"),
    (3, "1.10 Funnel Congruence (ad→page path scores)"),
    (3, "1.11 Validated Angle Cards"),
    (2, "PART 2: OPPORTUNITY MAP"),
    (3, "2.1 Hidden Angles (validated by research)"),
    (3, "2.2 Underserved Avatars"),
    (3, "2.3 Emotional Territories Untapped"),
    (3, "2.4 Funnel Congruence Gaps (angles the competitor leaks traffic on — our opportunity)"),
    (3, "2.5 ChatGPT Raw Data (full market research output)"),
    (3, "2.6 Language Bank (hook-ready, headline-ready, objection-ready phrases)"),
    (3, "2.7 Emergent Angles (from raw data)"),
    (3, "2.8 Opportunity Angle Cards"),
    (2, "PART 3: QUICK-REFERENCE"),
    (3, "3.1 Angle Cards (validated + opportunity, combined)"),
    (3, "3.2 Avatar Cards"),
    (3, "3.3 Hook Library (every hook from every ad + templates)"),
    (3, "3.4 Framework Library (every video framework + beat maps)"),
    (3, "3.5 Customer Language Bank (organized by use: hooks, headlines, objection handling, social proof)"),
    (3, "3.6 ChatGPT Prompt (ready to paste for this product)"),
]

F = {  # required fields per block type (first key = type marker)
    "avatar": ["AVATAR", "DEMOGRAPHICS", "PSYCHOGRAPHICS", "TRIGGER EVENT", "AWARENESS STATE",
               "SOPHISTICATION", "CUSTOMER LANGUAGE"],
    "pain": ["PAIN POINT", "RANK", "SOURCE", "FREQUENCY", "EMOTIONAL WEIGHT", "AVATAR", "CUSTOMER LANGUAGE"],
    "desire": ["DESIRE", "RANK", "TYPE", "DREAM OUTCOME", "SOURCE", "AVATAR", "CUSTOMER LANGUAGE"],
    "objection": ["OBJECTION", "TYPE", "HOW COMPETITOR HANDLES IT", "WHERE IN FUNNEL", "STRENGTH", "GAP"],
    "emotional": ["FEAR-BASED TRIGGERS", "DESIRE-BASED TRIGGERS", "IDENTITY TRIGGERS",
                  "FRUSTRATION TRIGGERS", "CURIOSITY TRIGGERS", "DISGUST TRIGGERS"],
    "mechanism": ["MECHANISM", "MECHANISM NAME", "MECHANISM STORY", "MECHANISM PROOF", "SCHWARTZ TECHNIQUE"],
    "video": ["AD ID", "FRAMEWORK", "BEAT MAP", "FORMAT", "HOOK", "HOOK DURATION", "ANGLE", "AVATAR",
              "EMOTIONAL ARC", "RETENTION MECHANICS", "VO/TEXT SPLIT", "PACING", "MUSIC/SFX", "CTA"],
    "static": ["AD ID", "PRIMARY TEXT", "HEADLINE", "DESCRIPTION", "HOOK", "ANGLE", "AVATAR",
               "EMOTIONAL TRIGGER", "PERSUASION SEQUENCE", "PROOF TYPE", "CTA", "IMAGE FORMAT"],
    "patterns": ["VALIDATED ANGLES", "TESTING ANGLES", "DOMINANT HOOK TYPES", "DOMINANT FORMATS",
                 "DOMINANT FRAMEWORKS", "COMMON PROOF", "COMMON CTA", "CREATIVE VELOCITY", "AD VOLUME",
                 "SATURATION"],
    "map": ["AD", "ANGLE", "PROMISE", "AVATAR", "EMOTIONAL STATE AT CLICK", "LANDING",
            "FIRST SECTION THEY SEE", "CONGRUENCE"],
    "insights": ["HIGH CONGRUENCE ANGLES", "LOW CONGRUENCE ANGLES", "LANDING PAGES",
                 "CONGRUENT PAGE PER ANGLE", "PAGE STRATEGY"],
    "card": ["ANGLE", "CONFIDENCE", "AVATAR", "PAIN/DESIRE", "EMOTIONAL TRIGGER", "ENEMY", "MECHANISM",
             "PROMISE", "PROOF", "FUNNEL CONGRUENCE", "ADS USING THIS", "HOOK TEMPLATES",
             "CUSTOMER LANGUAGE", "OPPORTUNITY"],
    "explosion": ["AVATAR UNIVERSE", "PHYSICAL PAINS", "EMOTIONAL PAINS", "SOCIAL PAINS", "IDENTITY PAINS",
                  "CONVENIENCE PAINS", "FINANCIAL PAINS", "DESIRE UNIVERSE", "COMBINATIONS CROSSED",
                  "SURVIVORS", "DISCARDED"],
    "hidden": ["HIDDEN ANGLE", "AVATAR", "PAIN/DESIRE", "EMOTIONAL ENTRY", "ESTIMATED POTENTIAL",
               "COMPETITOR USING IT", "EVIDENCE IT COULD WORK", "RESEARCH VERDICT", "RESEARCH EVIDENCE"],
    "emergent": ["EMERGENT ANGLE", "AVATAR", "PAIN/DESIRE", "EMOTIONAL ENTRY", "ESTIMATED POTENTIAL", "EVIDENCE"],
}
EXTRA_KEYS = {"WHY UNDERSERVED", "EVIDENCE", "BUILT FROM"}
KNOWN = set(k for v in F.values() for k in v) | EXTRA_KEYS
ALIASES = {"HANDLES IT": "HOW COMPETITOR HANDLES IT", "AT CLICK": "EMOTIONAL STATE AT CLICK",
           "THEY SEE": "FIRST SECTION THEY SEE", "WORK": "EVIDENCE IT COULD WORK"}
FIRST_KEY = {"AVATAR": "avatar", "PAIN POINT": "pain", "DESIRE": "desire", "OBJECTION": "objection",
             "FEAR-BASED TRIGGERS": "emotional", "MECHANISM": "mechanism", "VALIDATED ANGLES": "patterns",
             "AD": "map", "HIGH CONGRUENCE ANGLES": "insights", "ANGLE": "card",
             "AVATAR UNIVERSE": "explosion", "HIDDEN ANGLE": "hidden", "EMERGENT ANGLE": "emergent"}
EMOTIONAL_ENTRIES = ["fear", "desire", "identity", "curiosity", "frustration", "contrarian", "disgust",
                     "authority", "social proof", "mechanism", "comparison", "seasonal", "life-event"]
# spec value lists (19-step-alpha.md): objections 128-135, video FORMAT 226-232, static 258-270
OBJ_TYPES = r"price|efficacy|trust|safety|effort|social judg|alternative|is this real|shipping|return"
FUNNEL_PLACES = r"\bad\b|ads\b|landing page|hero|page body|faq|checkout"
VIDEO_FORMATS = (r"ugc|advertorial|talking head|product demo|animation|text overlay|mixed|interview|before-after|"
                 r"before/after|lifestyle montage|problem dramati[sz]ation|expert explanation|customer story|"
                 r"comparison demo|unboxing|day-in-life|day in the life|\bpov\b|reaction|transformation reveal")
IMAGE_FORMATS = (r"product shot|lifestyle|before-after|before/after|infographic|ugc screenshot|review screenshot|"
                 r"text-heavy|comparison|ingredient visual|meme|data visuali[sz]ation|testimonial card")
STATIC_TRIGGERS = r"fear|desire|identity|curiosity|frustration|disgust|aspiration"
PROOF_TYPES = r"stat|testimonial|authority|mechanism|before-after|before/after|social count|specificity"

PROMPT_REQUIRED = [  # (label, regex) the filled ChatGPT prompt must contain (spec 2.2, lines 525-685)
    ("platform Reddit", r"reddit"), ("platform Quora", r"quora"), ("platform Amazon reviews", r"amazon reviews"),
    ("platform forum threads", r"forum threads"), ("platform Facebook groups", r"facebook\.com/groups"),
    ("platform TikTok/YouTube comments", r"tiktok/youtube comments"),
    ("platform Google People Also Ask", r"people also ask"), ("platform blog comments", r"blog comments"),
    ("category 1 PAIN LANGUAGE", r"pain language"), ("category 2 DESIRE LANGUAGE", r"desire language"),
    ("category 3 OBJECTION LANGUAGE", r"objection language"), ("category 4 SOLUTION ATTEMPTS", r"solution attempts"),
    ("category 5 TRIGGER EVENTS", r"trigger events"), ("category 6 EMOTIONAL EXPRESSIONS", r"emotional expressions"),
    ("category 7 IDIOMS & SLANG", r"idioms & slang"), ("category 8 HIDDEN ANGLE VALIDATION", r"hidden angle validation"),
    ("category 9 DEMOGRAPHIC SIGNALS", r"demographic signals"), ("category 10 COMPETITOR MENTIONS", r"competitor mentions"),
    ("count 30-50 pain quotes", r"30-50 distinct verbatim pain quotes"),
    ("count 20-30 desire quotes", r"20-30 distinct verbatim desire quotes"),
    ("count 20-30 objection quotes", r"20-30 objection quotes"),
    ("count 15-20 trigger events", r"15-20 trigger events"),
    ("count 20-30 emotional expressions", r"20-30 emotional expressions"),
    ("pain tags (platform, subreddit/forum, demographic)", r"source platform, subreddit/forum, estimated demographic"),
    ("output: PAIN QUOTES", r"## pain quotes \(verbatim\)"), ("output: DESIRE QUOTES", r"## desire quotes \(verbatim\)"),
    ("output: OBJECTION QUOTES", r"## objection quotes \(verbatim\)"), ("output: SOLUTION ATTEMPTS", r"## solution attempts"),
    ("output: TRIGGER EVENTS", r"## trigger events"), ("output: EMOTIONAL EXPRESSIONS", r"## emotional expressions"),
    ("output: IDIOMS & SLANG", r"## idioms & slang"), ("output: HIDDEN ANGLE EVIDENCE", r"## hidden angle evidence"),
    ("output: DEMOGRAPHIC SIGNALS", r"## demographic signals"), ("output: COMPETITOR MENTIONS", r"## competitor mentions"),
    ("output: pain table header", r"\| # \| quote \| source \| platform \| est\. demo \|"),
    ("rule: never paraphrase", r"never paraphrase"), ("rule: never invent", r"never invent or fabricate"),
    ("rule: never analyze", r"never analyze, interpret, or recommend"), ("rule: always cite", r"always cite the source"),
    ("rule: recency", r"prioritize recency"), ("rule: emotional intensity", r"prioritize emotional intensity"),
    ("role: pure data gathering", r"do not analyze"),
]
RAW_SECTIONS = [("PAIN QUOTES", 30), ("DESIRE QUOTES", 20), ("OBJECTION QUOTES", 20), ("SOLUTION ATTEMPTS", 1),
                ("TRIGGER EVENTS", 15), ("EMOTIONAL EXPRESSIONS", 20), ("IDIOMS & SLANG", 1),
                ("HIDDEN ANGLE EVIDENCE", 1), ("DEMOGRAPHIC SIGNALS", 0), ("COMPETITOR MENTIONS", 1)]
ANALYSIS_FILES = ["analysis1/1.1_customer.md", "analysis1/1.2_ad_inventory.md", "analysis1/1.2_video_ads.md",
                  "analysis1/1.2_static_ads.md", "analysis1/1.2_patterns.md", "analysis1/1.3_congruence.md",
                  "analysis1/1.4_angle_cards.md", "analysis2/2.1_hidden_angles.md", "analysis2/2.3_synthesis.md"]
LANG_MIN = 5  # rows per language-bank group (skill minimum; the spec says "populated")


# ----------------------------------------------------------------------------- parsing helpers
def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def is_placeholder(v):
    v = norm(v)
    if not v:
        return True
    if v in ("...", "…", "-", "—", "TBD", "TODO", "n/a?"):
        return True
    if "[...]" in v or "{{" in v or re.search(r"\bTODO\b|\bTBD\b", v):
        return True
    if v.startswith("[") and v.endswith("]"):
        return True
    return False


def has_quote(v):
    return bool(re.search(r'"[^"]{3,}"|“[^”]{3,}”', v or ""))


IDS_RE = re.compile(r"\b(?:AV|[VOHESM])\d+\b|\b\d{8,}\b")


def ids_in(text):
    return set(IDS_RE.findall(text or ""))


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def split_doc(text):
    """-> (h1, [(level, title, body_lines, fenced_blocks)], headings_seen). Fence-aware."""
    lines = text.splitlines()
    h1 = None
    sections, cur = [], None
    fence = None  # (char, len)
    block = None
    headings = []
    for ln in lines:
        m = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", ln)
        if fence is None and m:
            fence = (m.group(1)[0], len(m.group(1)), m.group(2).strip())
            block = []
            if cur is not None:
                cur["lines"].append(ln)
            continue
        if fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not m.group(2).strip():
                if cur is not None:
                    cur["blocks"].append((fence, block))
                    cur["lines"].append(ln)
                fence, block = None, None
                continue
            block.append(ln)
            if cur is not None:
                cur["lines"].append(ln)
            continue
        hm = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", ln)
        if hm:
            lvl, title = len(hm.group(1)), norm(hm.group(2))
            if lvl == 1 and h1 is None:
                h1 = title
                continue
            if lvl <= 3:
                headings.append((lvl, title))
                cur = {"level": lvl, "title": title, "lines": [], "blocks": []}
                sections.append(cur)
                continue
        if cur is not None:
            cur["lines"].append(ln)
    return h1, sections, headings


def parse_block(lines):
    """Fenced block -> ordered list of (KEY, value). Accepts the spec's two-line keys
    ("HOW COMPETITOR" / "HANDLES IT:") as well as the one-line form."""
    prefixes = {"HOW COMPETITOR": "HANDLES IT", "EMOTIONAL STATE": "AT CLICK",
                "FIRST SECTION": "THEY SEE", "EVIDENCE IT COULD": "WORK"}
    out, pending = [], None
    for raw in lines:
        ln = raw.strip().strip("│|┌┐└┘").strip()
        if not ln or re.fullmatch(r"[↓─━\-=_ ]+", ln):
            continue
        if norm(ln).upper() in prefixes and ":" not in ln:
            pending = norm(ln).upper()
            continue
        m = re.match(r"^([A-Z][A-Z0-9 /&()'.\-]*?)\s*:(.*)$", ln)
        key = norm(m.group(1)) if m else None
        if key in ALIASES and pending and prefixes[pending] == key:
            key = ALIASES[key]
        pending = None
        if key in KNOWN:
            out.append([key, m.group(2).strip()])
        elif out:
            out[-1][1] = (out[-1][1] + " " + ln).strip()
    return [(k, v) for k, v in out]


def block_type(fields):
    if not fields:
        return None
    k0 = fields[0][0]
    if k0 == "AD ID":
        keys = {k for k, _ in fields}
        return "video" if "FRAMEWORK" in keys else "static" if "PRIMARY TEXT" in keys else "adid?"
    return FIRST_KEY.get(k0)


def blocks_of(section, btype=None):
    res = []
    for (fch, flen, info), lines in section["blocks"]:
        if flen != 3:  # 4+ fences hold pasted content (2.5, 3.6)
            continue
        flds = parse_block(lines)
        t = block_type(flds)
        if t and (btype is None or t == btype):
            d = {}
            for k, v in flds:
                d.setdefault(k, v)
            res.append(d)
    return res


def tables_of(section):
    """Markdown tables outside fences -> list of tables (list of rows, header dropped)."""
    tables, cur = [], None
    in_fence = None
    for ln in section["lines"]:
        m = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", ln)
        if m:
            if in_fence is None:
                in_fence = (m.group(1)[0], len(m.group(1)))
            elif m.group(1)[0] == in_fence[0] and len(m.group(1)) >= in_fence[1]:
                in_fence = None
            continue
        if in_fence:
            continue
        s = ln.strip()
        if s.startswith("|") or s.startswith("│"):
            cells = [c.strip() for c in re.split(r"[|│]", s.strip("|│ "))]
            if cur is None:
                cur = {"header": cells, "rows": []}
                tables.append(cur)
            elif all(re.fullmatch(r":?[-─━=]+:?|┼?", c.replace("┼", "")) or c == "" for c in cells):
                continue
            else:
                cur["rows"].append(cells)
        else:
            cur = None
    return tables


def sub_tables(section):
    """#### sub-heading -> its tables (for language banks)."""
    groups, name, buf = {}, None, []
    for ln in section["lines"] + ["#### __end__"]:
        hm = re.match(r"^####\s+(.*)$", ln)
        if hm:
            if name is not None:
                groups[name] = tables_of({"lines": buf})
            name, buf = norm(hm.group(1)).lower(), []
        elif name is not None:
            buf.append(ln)
    return groups


def section_text(section):
    return "\n".join(section["lines"])


# ----------------------------------------------------------------------------- report
class Report:
    def __init__(self):
        self.items = []  # (n, title, fails, manual, warns)

    def box(self, n, title, fails, manual=None, warns=None):
        self.items.append((n, title, fails, manual or [], warns or []))

    def print(self):
        failed = 0
        for n, title, fails, manual, warns in self.items:
            state = "FAIL" if fails else "PASS"
            failed += bool(fails)
            print(f"[{state}] {n:>2}. {title}")
            for f in fails[:25]:
                print(f"         x {f}")
            if len(fails) > 25:
                print(f"         x ... {len(fails) - 25} more")
            for w in warns:
                print(f"         ! WARN {w}")
            for m in manual:
                print(f"         ? MANUAL {m}")
        print()
        print(f"Result: {len(self.items) - failed}/{len(self.items)} boxes pass" +
              ("" if not failed else f", {failed} FAIL -> Alpha is NOT complete; Phase 2 stays blocked."))
        if not failed:
            print("Script checks pass. The coordinator still reads every MANUAL line before releasing Phase 2.")
        return failed


def check_fields(blocks, req, label, fails, quote_keys=()):
    for i, b in enumerate(blocks, 1):
        name = norm(b.get(req[0], ""))[:40] or f"#{i}"
        for k in req:
            if k not in b:
                fails.append(f"{label} {name}: field {k} missing")
            elif is_placeholder(b[k]):
                fails.append(f"{label} {name}: field {k} empty/placeholder")
        for k in quote_keys:
            if k in b and not is_placeholder(b[k]) and not has_quote(b[k]):
                fails.append(f"{label} {name}: {k} has no verbatim \"quote\"")


def load_inventory(folder, fails):
    p = os.path.join(folder, "ad_inventory.json")
    if not os.path.isfile(p):
        fails.append("ad_inventory.json missing")
        return None
    try:
        data = json.load(open(p, encoding="utf-8"))
    except ValueError as e:
        fails.append(f"ad_inventory.json is not valid JSON: {e}")
        return None
    if isinstance(data, list):
        data = {"header": {}, "ads": data}
    if "header" not in data and "meta" in data:
        data["header"] = data["meta"]
    if "ads" not in data and "records" in data:
        data["ads"] = data["records"]
    data.setdefault("header", {})
    data["meta"] = data["header"]
    data.setdefault("ads", [])
    data.setdefault("excluded", [])
    data.setdefault("review", [])
    return data


def ad_keys(ad):
    return {str(ad.get("id"))} | ({str(ad["short_id"])} if ad.get("short_id") else set())


def covered(ad, ids):
    return bool(ad_keys(ad) & ids)


def gate(path):
    if os.path.isdir(path):
        folder, dossier = path, os.path.join(path, "ALPHA_DOSSIER.md")
    else:
        folder, dossier = os.path.dirname(os.path.abspath(path)), path
    rep = Report()
    if not os.path.isfile(dossier):
        print(f"FAIL: dossier not found: {dossier}")
        return 1
    raw_text = open(dossier, encoding="utf-8").read()
    text = strip_comments(raw_text)
    h1, sections, headings = split_doc(text)
    sec = {}
    for s in sections:
        m = re.match(r"^(\d+\.\d+)\s", s["title"])
        if m:
            sec[m.group(1)] = s
    empty = {"lines": [], "blocks": [], "title": ""}
    S = lambda k: sec.get(k, empty)  # noqa: E731

    inv_fails = []
    inv = load_inventory(folder, inv_fails)
    ads = inv["ads"] if inv else []
    videos = [a for a in ads if str(a.get("format", "")).lower() == "video"]
    nonvideo = [a for a in ads if str(a.get("format", "")).lower() != "video"]

    # 1 avatars
    f = []
    av = blocks_of(S("1.1"), "avatar")
    if len(av) < 2:
        f.append(f"{len(av)} avatar blocks in 1.1 (minimum 2)")
    check_fields(av, F["avatar"], "avatar", f, quote_keys=("CUSTOMER LANGUAGE",))
    names = [norm(b.get("AVATAR", "")).lower() for b in av]
    if len(set(names)) != len(names):
        f.append("avatar names are not distinct")
    for b in av:
        if not re.search(r"\bAV\d+\b", b.get("AVATAR", "")):
            f.append(f"avatar '{norm(b.get('AVATAR',''))[:30]}' has no AV id")
        if not is_placeholder(b.get("AWARENESS STATE")) and not re.search(r"aware", b.get("AWARENESS STATE", ""), re.I):
            f.append(f"avatar '{norm(b.get('AVATAR',''))[:30]}': AWARENESS STATE names no Schwartz level (Most Aware → Unaware)")
    rep.box(1, "Minimum 2 distinct avatars with full psychographic profiles and customer language", f,
            ["psychographics are specific (values, routines, media, trusted brands, decision style), not generic"])

    # 2 pains
    f = []
    pains = blocks_of(S("1.2"), "pain")
    if len(pains) < 10:
        f.append(f"{len(pains)} pain points in 1.2 (minimum 10)")
    check_fields(pains, F["pain"], "pain", f, quote_keys=("CUSTOMER LANGUAGE",))
    rep.box(2, "Minimum 10 pain points with verbatim customer language", f,
            ["pains are felt experiences, not clinical labels; ranked by frequency x emotional weight"])

    # 3 desires
    f = []
    des = blocks_of(S("1.3"), "desire")
    if len(des) < 5:
        f.append(f"{len(des)} desires in 1.3 (minimum 5)")
    check_fields(des, F["desire"], "desire", f, quote_keys=("CUSTOMER LANGUAGE",))
    for b in des:
        t = b.get("TYPE", "").lower()
        if not is_placeholder(t) and not re.search(r"functional|emotional|identity|social|aspirational", t):
            f.append(f"desire '{norm(b.get('DESIRE',''))[:30]}': TYPE not functional/emotional/identity/social/aspirational")
    rep.box(3, "Minimum 5 desires with verbatim customer language", f)

    # 4 objections
    f = []
    obj = blocks_of(S("1.4"), "objection")
    if len(obj) < 5:
        f.append(f"{len(obj)} objections in 1.4 (minimum 5)")
    check_fields(obj, F["objection"], "objection", f)
    for b in obj:
        if "STRENGTH" in b and not is_placeholder(b["STRENGTH"]) and not re.search(r"\b[1-5]\b", b["STRENGTH"]):
            f.append(f"objection '{norm(b.get('OBJECTION',''))[:30]}': STRENGTH is not a 1-5 score")
        if not is_placeholder(b.get("TYPE")) and not re.search(OBJ_TYPES, b.get("TYPE", ""), re.I):
            f.append(f"objection '{norm(b.get('OBJECTION',''))[:30]}': TYPE is none of the spec's types (price … returns)")
        if not is_placeholder(b.get("WHERE IN FUNNEL")) and not re.search(FUNNEL_PLACES, b.get("WHERE IN FUNNEL", ""), re.I):
            f.append(f"objection '{norm(b.get('OBJECTION',''))[:30]}': WHERE IN FUNNEL is none of ad / landing page / hero / body / FAQ / checkout")
    rep.box(4, "Minimum 5 objections with competitor handling analysis", f)

    # 5 emotional landscape
    f = []
    emo = blocks_of(S("1.5"), "emotional")
    if len(emo) != 1:
        f.append(f"{len(emo)} emotional landscape blocks in 1.5 (need exactly 1)")
    check_fields(emo, F["emotional"], "emotional landscape", f)
    rep.box(5, "Complete emotional landscape (all 6 trigger types mapped)", f)

    # 6 mechanism
    f = []
    mech = blocks_of(S("1.6"), "mechanism")
    if len(mech) != 1:
        f.append(f"{len(mech)} mechanism blocks in 1.6 (need exactly 1)")
    check_fields(mech, F["mechanism"], "mechanism", f)
    for b in mech:
        if not is_placeholder(b.get("SCHWARTZ TECHNIQUE")) and not re.search(
                r"mechani[sz]ation|concentration|redefinition|identification", b.get("SCHWARTZ TECHNIQUE", ""), re.I):
            f.append("SCHWARTZ TECHNIQUE names none of Mechanization / Concentration / Redefinition / Identification")
    rep.box(6, "Unique mechanism fully extracted and analyzed", f,
            ["mechanism story and proof are analysed, not just restated"])

    # 7 inventory
    f = list(inv_fails)
    warns, manual = [], ["every platform Brandsearch has for this advertiser was pulled (Meta active+inactive, "
                         "TikTok/Instagram when listed), else operator-provided ads were added"]
    inv_rows = []
    for t in tables_of(S("1.7")):
        if [norm(c).upper() for c in t["header"][:7]] == ["AD ID", "FORMAT", "PLATFORM", "STATUS", "RUN TIME", "ANGLE", "AVATAR"]:
            inv_rows.extend(t["rows"])
    if not inv_rows:
        f.append("1.7 has no inventory table with columns AD ID | FORMAT | PLATFORM | STATUS | RUN TIME | ANGLE | AVATAR")
    if inv:
        if not ads:
            f.append("ad_inventory.json has 0 ads")
        if inv["review"]:
            f.append(f"ad_inventory.json 'review' still holds {len(inv['review'])} rows: move each to ads or excluded (with reason)")
        for e in inv["excluded"]:
            if is_placeholder(str(e.get("reason", ""))):
                f.append(f"excluded ad {e.get('id')} has no reason")
        seen = set()
        for a in ads:
            for k in ("id", "platform", "format", "status"):
                if is_placeholder(str(a.get(k) or "")):
                    f.append(f"inventory record {a.get('short_id') or a.get('id')}: '{k}' empty")
            if a.get("run_days") in (None, ""):
                f.append(f"inventory record {a.get('short_id') or a.get('id')}: 'run_days' empty")
            for k in ad_keys(a):
                if k in seen:
                    f.append(f"duplicate id {k} in ad_inventory.json")
                seen.add(k)
        if inv_rows and len(inv_rows) != len(ads):
            f.append(f"1.7 table has {len(inv_rows)} rows but ad_inventory.json has {len(ads)} ads")
        first = set()
        for r in inv_rows:
            first |= ids_in(r[0]) | {norm(r[0])}
        missing = [a.get("short_id") or a.get("id") for a in ads if not covered(a, first)]
        if inv_rows and missing:
            f.append(f"ads missing from the 1.7 table: {', '.join(map(str, missing[:15]))}")
        exp = inv["meta"].get("expected_total")
        if isinstance(exp, int) and len(ads) + len(inv["excluded"]) < exp:
            f.append(f"inventory holds {len(ads)} ads + {len(inv['excluded'])} excluded < expected_total {exp} "
                     "from Brandsearch pagination: keep paging")
        plats = inv["meta"].get("platforms_checked")
        if not plats:
            warns.append("meta.platforms_checked not recorded in ad_inventory.json")
        if inv["meta"].get("gaps"):
            manual.append(f"recorded footprint gaps: {inv['meta']['gaps']} - operator asked for the missing ads?")
    for r in inv_rows:
        if any(is_placeholder(c) for c in r[:7]):
            f.append(f"1.7 row {r[0]}: empty/placeholder cell")
    rep.box(7, "Complete ad inventory from BrandSearch", f, manual, warns)

    # 8 video ads
    f = [] if inv else ["ad_inventory.json missing: cannot verify that every video ad is covered"]
    vwarns = [] if (videos or not inv) else ["inventory has no video ads"]
    vblocks = blocks_of(S("1.8"), "video")
    vb_by = {}
    for b in vblocks:
        for i in ids_in(b.get("AD ID", "")) | {norm(b.get("AD ID", ""))}:
            vb_by[i] = b
    for a in videos:
        sid = a.get("short_id") or a.get("id")
        tp = a.get("transcript") or f"transcripts/{a.get('id')}.txt"
        tpath = os.path.join(folder, tp)
        if not os.path.isfile(tpath) or os.path.getsize(tpath) == 0:
            f.append(f"video {sid}: transcript file missing/empty ({tp})")
        gp = a.get("gemini") or f"gemini/{a.get('id')}.json"
        if not os.path.isfile(os.path.join(folder, gp)):
            f.append(f"video {sid}: video_gemini.py analysis missing ({gp})")
        b = next((vb_by[k] for k in ad_keys(a) if k in vb_by), None)
        if b is None:
            f.append(f"video {sid}: no video-analysis block in 1.8")
            continue
        check_fields([b], F["video"], f"video {sid}", f)
        if not is_placeholder(b.get("BEAT MAP")) and not re.search(r"\d+(\.\d+)?\s*s\b|\d+:\d\d", b.get("BEAT MAP", "")):
            f.append(f"video {sid}: BEAT MAP has no timestamps")
        if not is_placeholder(b.get("BEAT MAP")) and "%" not in b.get("BEAT MAP", ""):
            f.append(f"video {sid}: BEAT MAP has no % of total")
        if not is_placeholder(b.get("PACING")) and not re.search(r"\d", b.get("PACING", "")):
            f.append(f"video {sid}: PACING has no WPS number")
        if not is_placeholder(b.get("FORMAT")) and not re.search(VIDEO_FORMATS, b.get("FORMAT", ""), re.I):
            vwarns.append(f"video {sid}: FORMAT is not from the spec's format list (check)")
    if videos:
        rows = [r for t in tables_of(S("1.8")) for r in t["rows"]]
        if not rows or all(any(is_placeholder(c) for c in r) for r in rows):
            f.append("1.8 'Video framework patterns' table is empty")
    rep.box(8, "Every video ad transcribed and framework-extracted", f,
            ["beat maps match the video (spot-check 2 against the Gemini JSON and transcript)"] if videos else [],
            vwarns)

    # 9 static ads
    f = [] if inv else ["ad_inventory.json missing: cannot verify that every non-video ad is covered"]
    swarns = []
    sblocks = blocks_of(S("1.9"), "static")
    sb_by = {}
    for b in sblocks:
        for i in ids_in(b.get("AD ID", "")) | {norm(b.get("AD ID", ""))}:
            sb_by[i] = b
    for a in nonvideo:
        sid = a.get("short_id") or a.get("id")
        b = next((sb_by[k] for k in ad_keys(a) if k in sb_by), None)
        if b is None:
            f.append(f"ad {sid}: no static/text-ad block in 1.9")
            continue
        check_fields([b], F["static"], f"ad {sid}", f)
        for k, rx, what in (("EMOTIONAL TRIGGER", STATIC_TRIGGERS, "trigger"), ("PROOF TYPE", PROOF_TYPES, "proof type"),
                            ("IMAGE FORMAT", IMAGE_FORMATS, "image format")):
            if not is_placeholder(b.get(k)) and not re.search(rx, b.get(k, ""), re.I):
                swarns.append(f"ad {sid}: {k} is not from the spec's {what} list (check)")
    rep.box(9, "Every text ad forensically decoded", f,
            ["PRIMARY TEXT / HEADLINE are exact copies of the ad (spot-check 3 against ad_inventory.json)"], swarns)

    # 10 cross-ad patterns
    f = []
    pat = blocks_of(S("1.9"), "patterns")
    if len(pat) != 1:
        f.append(f"{len(pat)} cross-ad pattern blocks in 1.9 (need exactly 1)")
    check_fields(pat, F["patterns"], "patterns", f)
    for b in pat:
        for k in ("CREATIVE VELOCITY", "AD VOLUME"):
            if k in b and not is_placeholder(b[k]) and not re.search(r"\d", b[k]):
                f.append(f"patterns: {k} has no number")
    rep.box(10, "Cross-ad pattern synthesis complete", f,
            ["validated vs testing angles follow run time/volume; saturation counted from other advertisers"])

    # 11 congruence
    f = []
    maps = blocks_of(S("1.10"), "map")
    map_ids = set()
    for b in maps:
        map_ids |= ids_in(b.get("AD", "")) | {norm(b.get("AD", ""))}
    check_fields(maps, F["map"], "path map", f)
    for b in maps:
        c = b.get("CONGRUENCE", "")
        if not is_placeholder(c) and not re.search(r"\b(HIGH|MED|MEDIUM|LOW)\b", c):
            f.append(f"path map {norm(b.get('AD',''))[:20]}: CONGRUENCE is not HIGH/MED/LOW")
    score_rows = []
    for t in tables_of(S("1.10")):
        if t["header"] and "PATH" in norm(t["header"][0]).upper():
            score_rows.extend(t["rows"])
    score_ids = set()
    for r in score_rows:
        score_ids |= ids_in(r[0])
        if len(r) < 3 or any(is_placeholder(c) for c in r[:3]):
            f.append(f"score row '{norm(r[0])[:30]}': empty/placeholder cell")
        elif not re.search(r"\b(HIGH|MED|MEDIUM|LOW)\b", r[1]):
            f.append(f"score row '{norm(r[0])[:30]}': CONGRUENCE is not HIGH/MED/LOW")
    for a in ads:
        sid = a.get("short_id") or a.get("id")
        if not covered(a, map_ids):
            f.append(f"ad {sid}: no ad→page path map block")
        if not covered(a, score_ids):
            f.append(f"ad {sid}: no row in the path score table")
    ins = blocks_of(S("1.10"), "insights")
    if len(ins) != 1:
        f.append(f"{len(ins)} congruence insight blocks (need exactly 1)")
    check_fields(ins, F["insights"], "insights", f)
    rep.box(11, "Funnel congruence scored for every ad→page path", f,
            ["FIRST SECTION THEY SEE matches the captured page above the fold (desktop + 390px screenshots)"])

    # 12 validated angle cards
    f = []
    cards = blocks_of(S("1.11"), "card")
    good = [c for c in cards if re.search(r"\b(HIGH|MEDIUM)\b", c.get("CONFIDENCE", ""))]
    if len(good) < 3:
        f.append(f"{len(good)} validated angle cards with CONFIDENCE HIGH/MEDIUM in 1.11 (minimum 3)")
    check_fields(cards, F["card"], "card", f, quote_keys=("HOOK TEMPLATES", "CUSTOMER LANGUAGE"))
    all_ad_ids = set()
    for a in ads:
        all_ad_ids |= ad_keys(a)
    v_ids = []
    for c in cards:
        m = re.search(r"\bV\d+\b", c.get("ANGLE", ""))
        if not m:
            f.append(f"card '{norm(c.get('ANGLE',''))[:30]}' has no V id")
        else:
            v_ids.append(m.group(0))
        used = ids_in(c.get("ADS USING THIS", "")) - {x for x in ids_in(c.get("ADS USING THIS", "")) if x.startswith(("AV", "V", "O", "H", "E"))}
        if not used and not is_placeholder(c.get("ADS USING THIS")):
            f.append(f"card {m.group(0) if m else '?'}: ADS USING THIS names no inventory ad id")
        unknown = [u for u in used if all_ad_ids and u not in all_ad_ids]
        if unknown:
            f.append(f"card {m.group(0) if m else '?'}: unknown ad ids {', '.join(sorted(unknown))}")
    rep.box(12, "Minimum 3 validated angle cards", f)

    # 13 hidden angles
    f = []
    hid = blocks_of(S("2.1"), "hidden")
    if len(hid) < 8:
        f.append(f"{len(hid)} hidden angles in 2.1 (minimum 8 beyond what the competitor runs)")
    check_fields(hid, F["hidden"][:7], "hidden angle", f)
    h_ids = []
    for b in hid:
        m = re.search(r"\bH\d+\b", b.get("HIDDEN ANGLE", ""))
        if not m:
            f.append(f"hidden angle '{norm(b.get('HIDDEN ANGLE',''))[:30]}' has no H id")
        else:
            h_ids.append(m.group(0))
        if not is_placeholder(b.get("COMPETITOR USING IT")) and not norm(b.get("COMPETITOR USING IT", "")).upper().startswith("NO"):
            f.append(f"hidden angle {m.group(0) if m else '?'}: COMPETITOR USING IT is not NO (then it is not hidden)")
        if not is_placeholder(b.get("ESTIMATED POTENTIAL")) and not re.search(r"\b(HIGH|MEDIUM|LOW)\b", b.get("ESTIMATED POTENTIAL", "")):
            f.append(f"hidden angle {m.group(0) if m else '?'}: ESTIMATED POTENTIAL is not HIGH/MEDIUM/LOW")
        if not is_placeholder(b.get("EMOTIONAL ENTRY")) and not any(
                e.split()[0] in b.get("EMOTIONAL ENTRY", "").lower() for e in EMOTIONAL_ENTRIES):
            f.append(f"hidden angle {m.group(0) if m else '?'}: EMOTIONAL ENTRY is none of the 13 entries")
    exp = blocks_of(S("2.1"), "explosion")
    if len(exp) != 1:
        f.append(f"{len(exp)} explosion-input blocks in 2.1 (need exactly 1)")
    check_fields(exp, F["explosion"], "explosion inputs", f)
    entry_rows = {}
    for t in tables_of(S("2.1")):
        for r in t["rows"]:
            if len(r) >= 4:
                entry_rows[norm(r[1]).lower()] = r
    for e in EMOTIONAL_ENTRIES:
        r = entry_rows.get(e)
        if r is None:
            f.append(f"emotional entry '{e}' missing from the 13-entry table")
        elif is_placeholder(r[3]):
            f.append(f"emotional entry '{e}': no hidden angles and no reason")
    rep.box(13, "Hidden angle explosion produced minimum 8 candidate angles beyond what competitor runs", f,
            ["every avatar x pain x desire x emotion cross was tried; weak ones discarded with reasons in analysis2/2.1_hidden_angles.md"])

    # 14 ChatGPT prompt
    f = []
    manual = ["prompt is tailored: names this product's pains, avatars, validated angles and every hidden angle"]
    pp = os.path.join(folder, "chatgpt", "CHATGPT_PROMPT.md")
    prompt = ""
    if not os.path.isfile(pp):
        f.append("chatgpt/CHATGPT_PROMPT.md missing")
    else:
        prompt = open(pp, encoding="utf-8").read()
        left = sorted(set(re.findall(r"\{\{[^}]*\}\}", prompt)))
        if left:
            f.append(f"unfilled placeholders: {', '.join(left[:10])}")
        if "cut line" in prompt.lower():
            f.append("CHATGPT_PROMPT.md still contains the template header (copy only what is below the cut line)")
        low = norm(prompt).lower()
        for label, rx in PROMPT_REQUIRED:
            if not re.search(rx, low):
                f.append(f"prompt lacks {label}")
        for h in h_ids:
            if not re.search(r"\b%s\b" % h, prompt):
                f.append(f"prompt does not list hidden angle {h} (category 8)")
        if norm(prompt) not in norm(section_text(S("3.6"))):
            f.append("dossier 3.6 does not contain CHATGPT_PROMPT.md verbatim")
    rep.box(14, "ChatGPT prompt generated, tailored to this specific product and its identified angles/avatars", f, manual)

    # 15 after ChatGPT
    f, warns = [], []
    rp = os.path.join(folder, "chatgpt", "CHATGPT_RAW.md")
    if not os.path.isfile(rp) or len(open(rp, encoding="utf-8").read().strip()) < 200:
        f.append("chatgpt/CHATGPT_RAW.md missing or empty: the operator has not pasted the ChatGPT result (GATE α)")
    else:
        rawt = open(rp, encoding="utf-8").read()
        if norm(rawt) not in norm(section_text(S("2.5"))):
            f.append("dossier 2.5 does not contain CHATGPT_RAW.md verbatim")
        for name, target in RAW_SECTIONS:
            m = re.search(r"^#+\s*%s.*$" % re.escape(name), rawt, re.M | re.I)
            if not m:
                warns.append(f"raw data has no '{name}' section")
                continue
            nxt = re.search(r"^#+\s", rawt[m.end():], re.M)
            body = rawt[m.end(): m.end() + nxt.start()] if nxt else rawt[m.end():]
            rows = [ln for ln in body.splitlines() if re.match(r"^\s*\|\s*[^-\s|]", ln)]
            n = max(0, len(rows) - 1)  # minus header
            if target and n < target:
                warns.append(f"raw '{name}': {n} rows < {target} asked (send ChatGPT 'continue' / a follow-up)")
    for b in hid:
        hn = re.search(r"\bH\d+\b", b.get("HIDDEN ANGLE", ""))
        hn = hn.group(0) if hn else "?"
        v = norm(b.get("RESEARCH VERDICT", "")).upper()
        if not re.search(r"\b(VALIDATED|KILLED)\b", v) or is_placeholder(v):
            f.append(f"hidden angle {hn}: RESEARCH VERDICT is not VALIDATED or KILLED")
        if is_placeholder(b.get("RESEARCH EVIDENCE")):
            f.append(f"hidden angle {hn}: RESEARCH EVIDENCE empty")
    validated_h = [re.search(r"\bH\d+\b", b.get("HIDDEN ANGLE", "")).group(0) for b in hid
                   if re.search(r"\bVALIDATED\b", b.get("RESEARCH VERDICT", "").upper())
                   and re.search(r"\bH\d+\b", b.get("HIDDEN ANGLE", ""))]
    emer = blocks_of(S("2.7"), "emergent")
    s27 = section_text(S("2.7"))
    if not emer and not re.search(r"^\s*NONE FOUND:\s*\S", s27, re.M):
        f.append("2.7 has no emergent angle blocks and no 'NONE FOUND:' line")
    check_fields(emer, F["emergent"], "emergent angle", f, quote_keys=("EVIDENCE",))
    e_ids = [re.search(r"\bE\d+\b", b.get("EMERGENT ANGLE", "")).group(0) for b in emer
             if re.search(r"\bE\d+\b", b.get("EMERGENT ANGLE", ""))]
    if len(e_ids) != len(emer):
        f.append("an emergent angle has no E id")
    opp = blocks_of(S("2.8"), "card")
    check_fields(opp, F["card"] + ["BUILT FROM"], "opportunity card", f, quote_keys=("HOOK TEMPLATES", "CUSTOMER LANGUAGE"))
    o_ids = []
    built = set()
    for c in opp:
        m = re.search(r"\bO\d+\b", c.get("ANGLE", ""))
        if not m:
            f.append(f"opportunity card '{norm(c.get('ANGLE',''))[:30]}' has no O id")
        else:
            o_ids.append(m.group(0))
        built |= ids_in(c.get("BUILT FROM", "")) | ids_in(c.get("ANGLE", ""))
    for x in validated_h + e_ids:
        if x not in built:
            f.append(f"{x} is validated/emergent but no 2.8 opportunity card is BUILT FROM it")
    groups = sub_tables(S("2.6"))
    for g in ("hook-ready", "headline-ready", "objection-ready", "testimony-ready"):
        rows = [r for t in groups.get(g, []) for r in t["rows"]]
        good_rows = [r for r in rows if len(r) > 1 and not is_placeholder(r[1]) and has_quote(r[1])]
        if len(good_rows) < LANG_MIN:
            f.append(f"2.6 language bank '{g}': {len(good_rows)} quoted rows (minimum {LANG_MIN})")
        if any(len(r) > 2 and is_placeholder(r[2]) for r in rows if not is_placeholder(r[1])):
            f.append(f"2.6 language bank '{g}': a row has no source")
    manual = ["integration is real: validated angles cite raw-data rows, killed ones show no demand, emergent ones are new"]
    if not emer and re.search(r"^\s*NONE FOUND:", s27, re.M):
        manual.append("2.7 says NONE FOUND: confirm the raw data really holds no unanticipated pain/desire/use case")
    rep.box(15, "After ChatGPT data returns: integration complete, angles validated/killed, language bank populated",
            f, manual, warns)

    # 16 full dossier
    f = []
    if not h1 or not h1.endswith(H1_SUFFIX) or "[Product]" in h1 or is_placeholder(h1.replace(H1_SUFFIX, "")):
        f.append(f"H1 must be '# <Product> {H1_SUFFIX}' (found: {h1!r})")
    got = [(l, norm(t)) for l, t in headings]
    exp_h = [(l, norm(t)) for l, t in HEADINGS]
    if got != exp_h:
        for i in range(max(len(got), len(exp_h))):
            g = got[i] if i < len(got) else None
            e = exp_h[i] if i < len(exp_h) else None
            if g != e:
                f.append(f"heading #{i + 1}: expected {('#' * e[0] + ' ' + e[1]) if e else 'nothing'}, "
                         f"found {('#' * g[0] + ' ' + g[1]) if g else 'nothing'}")
                break
    # placeholders anywhere outside pasted sections
    for s in sections:
        if s["title"].startswith(("2.5", "3.6")):
            continue
        for ln in s["lines"]:
            if "[...]" in ln or "{{" in ln or re.search(r"\b(TODO|TBD)\b", ln):
                f.append(f"placeholder left in '{s['title'][:28]}': {norm(ln)[:70]}")
        for t in tables_of(s):
            for r in t["rows"]:
                if r and all(is_placeholder(c) for c in r if c):
                    f.append(f"template row left in '{s['title'][:28]}': {norm(' | '.join(r))[:70]}")
    # 2.2 / 2.3 / 2.4
    under = blocks_of(S("2.2"), "avatar")
    if not under:
        f.append("2.2 has no underserved avatar blocks")
    check_fields(under, F["avatar"] + ["WHY UNDERSERVED", "EVIDENCE"], "underserved avatar", f, quote_keys=("CUSTOMER LANGUAGE",))
    if not [r for t in tables_of(S("2.3")) for r in t["rows"] if not any(is_placeholder(c) for c in r)]:
        f.append("2.3 emotional territories table is empty")
    if not [r for t in tables_of(S("2.4")) for r in t["rows"] if not any(is_placeholder(c) for c in r)] \
            and not re.search(r"^\s*NO GAPS:\s*\S", section_text(S("2.4")), re.M):
        f.append("2.4 has no congruence-gap rows and no 'NO GAPS:' line")
    # Part 3 coverage
    t31 = set()
    for t in tables_of(S("3.1")):
        for r in t["rows"]:
            t31 |= ids_in(r[0])
    for x in v_ids + o_ids:
        if x not in t31:
            f.append(f"3.1 quick reference lacks angle card {x}")
    t32 = set()
    for t in tables_of(S("3.2")):
        for r in t["rows"]:
            t32 |= ids_in(r[0])
    for b in av + under:
        m = re.search(r"\bAV\d+\b", b.get("AVATAR", ""))
        if m and m.group(0) not in t32:
            f.append(f"3.2 avatar cards lack {m.group(0)}")
    t33 = set()
    for t in tables_of(S("3.3")):
        for r in t["rows"]:
            t33 |= ids_in(" ".join(r))
    miss = [a.get("short_id") or a.get("id") for a in ads if not covered(a, t33)]
    if miss:
        f.append(f"3.3 hook library lacks the hook of: {', '.join(map(str, miss[:15]))}")
    t34 = set()
    for t in tables_of(S("3.4")):
        for r in t["rows"]:
            t34 |= ids_in(" ".join(r))
    miss = [a.get("short_id") or a.get("id") for a in videos if not covered(a, t34)]
    if miss:
        f.append(f"3.4 framework library lacks video: {', '.join(map(str, miss[:15]))}")
    groups = sub_tables(S("3.5"))
    for g in ("hooks", "headlines", "objection handling", "social proof"):
        rows = [r for t in groups.get(g, []) for r in t["rows"] if len(r) > 1 and has_quote(r[1]) and not is_placeholder(r[1])]
        if len(rows) < LANG_MIN:
            f.append(f"3.5 language bank '{g}': {len(rows)} quoted rows (minimum {LANG_MIN})")
    if not re.search(r"`{4,}", section_text(S("3.6"))) or len(norm(section_text(S("3.6")))) < 500:
        f.append("3.6 does not hold the pasted prompt")
    for rel in ANALYSIS_FILES:
        p = os.path.join(folder, rel)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            f.append(f"working file missing/empty: {rel}")
    rep.box(16, "Full dossier produced and structured for instant retrieval by downstream steps", f,
            ["a downstream step can find any avatar, angle, hook or quote by its ID in under a minute"])

    return 1 if rep.print() else 0


# ----------------------------------------------------------------------------- inventory
def parse_jsonish(text):
    text = text.lstrip("\ufeff")
    try:
        return [json.loads(text)]
    except ValueError:
        pass
    dec, out, i = json.JSONDecoder(), [], 0
    pat = re.compile(r"[\[{]")
    while True:
        m = pat.search(text, i)
        if not m:
            break
        try:
            obj, end = dec.raw_decode(text, m.start())
            out.append(obj)
            i = end
        except ValueError:
            i = m.start() + 1
    return out


AD_HINT_KEYS = ("start_date", "creative", "image_url", "image_original_url", "thumbnail_url",
                "total_active_time", "is_image", "is_video", "dashboard_url", "video_sd_url")


def extract_rows(obj, pags):
    if isinstance(obj, str):
        s = obj.strip()
        if s[:1] in ("{", "["):
            for o in parse_jsonish(s):
                yield from extract_rows(o, pags)
        return
    if isinstance(obj, list):
        for x in obj:
            yield from extract_rows(x, pags)
        return
    if isinstance(obj, dict):
        if "id" in obj and any(k in obj for k in AD_HINT_KEYS):
            yield obj
            return
        if isinstance(obj.get("pagination"), dict):
            pags.append(obj["pagination"])
        for k, v in obj.items():
            if k != "summary" and isinstance(v, (dict, list, str)):
                yield from extract_rows(v, pags)


def parse_dt(v):
    if v in (None, ""):
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v, tz=timezone.utc).replace(tzinfo=None)
    s = str(v).strip().replace("Z", "")
    if re.fullmatch(r"\d{9,11}", s):
        return datetime.fromtimestamp(int(s), tz=timezone.utc).replace(tzinfo=None)
    s = re.sub(r"([+-]\d\d:\d\d)$", "", s)
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d")
        except ValueError:
            return None


def texts(row):
    t, d, b, c = [], [], [], []
    blocks = []
    cr = row.get("creative")
    if isinstance(cr, dict):
        blocks.append(cr)
        blocks += [x for x in (cr.get("cards") or []) if isinstance(x, dict)]
    blocks += [x for x in (row.get("cards") or []) if isinstance(x, dict)]
    for bl in blocks:
        for k, dst in (("title", t), ("headline", t), ("description", d), ("body", b), ("caption", b),
                       ("link_description", d)):
            v = bl.get(k)
            if isinstance(v, str) and v.strip() and v.strip() not in dst:
                dst.append(v.strip())
        cta = bl.get("cta")
        if isinstance(cta, dict):
            s = " - ".join(x for x in (cta.get("type"), cta.get("text")) if x)
            if s and s not in c:
                c.append(s)
        elif isinstance(cta, str) and cta.strip() and cta.strip() not in c:
            c.append(cta.strip())
    return t, d, b, c


def landing(row):
    for src in (row, row.get("creative") if isinstance(row.get("creative"), dict) else {}):
        for k in ("link_url", "landing_page_url", "landing_url", "destination_url", "cta_link", "website_url"):
            v = src.get(k) if isinstance(src, dict) else None
            if isinstance(v, str) and v.startswith("http"):
                return v
    return None


def fetch(url, dest, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    with open(dest, "wb") as fh:
        fh.write(data)
    return len(data)


def inventory(a):
    folder = a.alpha_dir
    os.makedirs(os.path.join(folder, "transcripts"), exist_ok=True)
    os.makedirs(os.path.join(folder, "gemini"), exist_ok=True)
    p = os.path.join(folder, "ad_inventory.json")
    old = {"header": {}, "ads": [], "excluded": [], "review": []}
    if os.path.isfile(p):
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, list):
            d = {"ads": d}
        if "meta" in d and "header" not in d:
            d["header"] = d.pop("meta")
        if "records" in d and "ads" not in d:
            d["ads"] = d.pop("records")
        old.update(d)
    pd = os.path.dirname(os.path.abspath(folder))
    vid_dir = a.fetch_videos or os.path.join(pd, "05_ads", "competitor", "videos")
    img_dir = a.fetch_images or os.path.join(pd, "05_ads", "competitor", "images")
    where = {}
    for bucket in ("ads", "excluded", "review"):
        for r in old.get(bucket, []):
            where[str(r.get("id"))] = (bucket, r)

    merged, pags_all = {}, []
    jobs = []
    for spec in a.dumps:
        plat, path = ("meta", spec)
        m = re.match(r"^(meta|tiktok|instagram|other):(.+)$", spec, re.I)
        if m:
            plat, path = m.group(1).lower(), m.group(2)
        hits = sorted(glob.glob(path)) if any(ch in path for ch in "*?[") else [path]
        if not hits:
            print(f"  no dump matches {path}")
        jobs += [(plat, h) for h in hits]
    for plat, path in jobs:
        txt = open(path, "rb").read().decode("utf-8", "replace")
        pags = []
        rows = [r for o in parse_jsonish(txt) for r in extract_rows(o, pags)]
        pags_all += [{"file": os.path.basename(path), **pg} for pg in pags]
        for r in rows:
            aid = str(r.get("id"))
            m2 = merged.setdefault(aid, {"id": aid, "platform": plat, "start": None, "end": None, "tat": None,
                                         "status": None, "is_video": False, "cards": None, "titles": [],
                                         "descs": [], "bodies": [], "ctas": [], "urls": {}, "reach_rank": None,
                                         "dup": None, "page": None, "landing": None})
            if isinstance(r.get("platforms"), list) and r["platforms"]:
                m2["platform_list"] = r["platforms"]
            st, en = parse_dt(r.get("start_date")), parse_dt(r.get("end_date"))
            if st and (m2["start"] is None or st < m2["start"]):
                m2["start"] = st
            if en and (m2["end"] is None or en > m2["end"]):
                m2["end"] = en
            if r.get("status"):
                m2["status"] = str(r["status"]).lower()
            tat = r.get("total_active_time")
            if isinstance(tat, (int, float)) and (m2["tat"] is None or tat > m2["tat"]):
                m2["tat"] = tat
            if r.get("is_video") is True or r.get("is_video") == "true":
                m2["is_video"] = True
            if r.get("cards_count") is not None:
                m2["cards"] = r.get("cards_count")
            rr = r.get("reach_rank")
            if isinstance(rr, (int, float)) and (m2["reach_rank"] is None or rr < m2["reach_rank"]):
                m2["reach_rank"] = int(rr)
            dc = r.get("duplicate_count")
            if isinstance(dc, (int, float)) and (m2["dup"] is None or dc > m2["dup"]):
                m2["dup"] = int(dc)
            for k in ("video_hd_url", "video_sd_url", "image_original_url", "image_url", "thumbnail_url",
                      "transcript_url", "dashboard_url"):
                if r.get(k) and k not in m2["urls"]:
                    m2["urls"][k] = r[k]
            pi = r.get("page_info")
            if isinstance(pi, dict) and not m2["page"]:
                m2["page"] = pi.get("name") or pi.get("page_name")
            m2["landing"] = m2["landing"] or landing(r)
            t, d, b, c = texts(r)
            for src, key in ((t, "titles"), (d, "descs"), (b, "bodies"), (c, "ctas")):
                m2[key] += [x for x in src if x not in m2[key]]

    now = datetime.utcnow()
    kws = [k.lower() for k in (a.keyword or [])]
    counters = {"M": 0, "S": 0}
    for bucket in ("ads", "excluded", "review"):
        for r in old.get(bucket, []):
            m = re.fullmatch(r"([MS])(\d+)", str(r.get("short_id") or ""))
            if m:
                counters[m.group(1)] = max(counters[m.group(1)], int(m.group(2)))

    def order(m):
        return (m["reach_rank"] is None, m["reach_rank"] or 0, -(m.get("days") or 0), m["id"])

    for m in merged.values():
        end = m["end"] or (now if m["status"] == "active" else None)
        span = (end - m["start"]).total_seconds() / 86400 if (m["start"] and end) else 0.0
        m["days"] = round(max(span, (m["tat"] or 0) / 86400), 1)

    new_counts = {"ads": 0, "review": 0, "updated": 0}
    for m in sorted(merged.values(), key=order):
        fmt = "video" if m["is_video"] else ("carousel" if (m["cards"] or 0) > 1 else "static")
        rec = {
            "id": m["id"], "platform": m["platform"], "format": fmt, "status": m["status"],
            "start": m["start"].date().isoformat() if m["start"] else None,
            "end": m["end"].date().isoformat() if m["end"] else None,
            "run_days": m["days"], "reach_rank": m["reach_rank"], "duplicate_count": m["dup"],
            "page": m["page"], "landing_url": m["landing"],
            "caption": {"primary_text": "\n---\n".join(m["bodies"]) or None,
                        "headline": " | ".join(m["titles"]) or None,
                        "description": " | ".join(m["descs"]) or None, "cta": " | ".join(m["ctas"]) or None},
            "video_url": m["urls"].get("video_hd_url") or m["urls"].get("video_sd_url"),
            "image_url": m["urls"].get("image_original_url") or m["urls"].get("image_url") or m["urls"].get("thumbnail_url"),
            "transcript_url": m["urls"].get("transcript_url"), "dashboard_url": m["urls"].get("dashboard_url"),
        }
        if fmt == "video":
            rec["transcript"] = f"transcripts/{m['id']}.txt"
            rec["gemini"] = f"gemini/{m['id']}.json"
            rec["video_file"] = None
        if m["id"] in where:
            bucket, r = where[m["id"]]
            for k, v in rec.items():
                if v not in (None, "") and k not in ("angle", "avatar", "short_id", "notes"):
                    r[k] = v
            new_counts["updated"] += 1
            continue
        pref = "M" if fmt == "video" else "S"
        counters[pref] += 1
        rec["short_id"] = f"{pref}{counters[pref]}"
        rec.update({"angle": "", "avatar": "", "notes": ""})
        blob = " ".join(m["titles"] + m["descs"] + m["bodies"]).lower()
        bucket = "ads" if (not kws or any(k in blob for k in kws)) else "review"
        if bucket == "review":
            rec["review_reason"] = "copy lacks every --keyword: check the creative/transcript, then move to ads or excluded"
        old.setdefault(bucket, []).append(rec)
        where[m["id"]] = (bucket, rec)
        new_counts[bucket] += 1

    meta = old.setdefault("header", {})
    meta["pull_date"] = now.date().isoformat()
    meta["pagination_totals"] = pags_all or meta.get("pagination_totals", [])
    meta.setdefault("gaps", [])
    if a.expected_total:
        meta["expected_total"] = a.expected_total
    plats = sorted(set(meta.get("platforms_checked", [])) | {m["platform"] for m in merged.values()})
    meta["platforms_checked"] = plats

    # free fetches
    for r in old["ads"] + old["review"]:  # files already on disk (07 Step 7 downloads)
        dest = os.path.join(vid_dir, f"{r['id']}.mp4")
        if r.get("format") == "video" and os.path.isfile(dest) and os.path.getsize(dest) > 0:
            r["video_file"] = dest
    if a.fetch_videos is not None:
        a.fetch_videos = vid_dir
        os.makedirs(a.fetch_videos, exist_ok=True)
        for r in old["ads"] + old["review"]:
            if r.get("format") == "video" and r.get("video_url"):
                dest = os.path.join(a.fetch_videos, f"{r['id']}.mp4")
                if os.path.isfile(dest) and os.path.getsize(dest) > 0:
                    r["video_file"] = dest
                    continue
                try:
                    n = fetch(r["video_url"], dest)
                    r["video_file"] = dest
                    print(f"  video {r['short_id']} {r['id']}: {n // 1024} KB")
                except Exception as e:  # noqa: BLE001
                    print(f"  video {r['short_id']} {r['id']}: download failed ({e}); URL expired? re-pull or download_ad media=video (1 credit)")
    if a.fetch_images is not None:
        a.fetch_images = img_dir
        os.makedirs(a.fetch_images, exist_ok=True)
        for r in old["ads"] + old["review"]:
            if r.get("format") != "video" and r.get("image_url"):
                have = [f for f in os.listdir(a.fetch_images) if f.startswith(r["id"] + ".")]
                if have:
                    r["image_file"] = os.path.join(a.fetch_images, have[0])
                    continue
                tmp = os.path.join(a.fetch_images, r["id"] + ".part")
                try:
                    fetch(r["image_url"], tmp)
                    head = open(tmp, "rb").read(12)
                    ext = ("png" if head.startswith(b"\x89PNG") else "gif" if head[:3] == b"GIF"
                           else "webp" if head[8:12] == b"WEBP" else "jpg")
                    dest = os.path.join(a.fetch_images, f"{r['id']}.{ext}")
                    os.replace(tmp, dest)
                    r["image_file"] = dest
                except Exception as e:  # noqa: BLE001
                    if os.path.exists(tmp):
                        os.remove(tmp)
                    print(f"  image {r['short_id']} {r['id']}: download failed ({e}); re-pull, or download_ad (1 credit)")
    if a.fetch_transcripts:
        for r in old["ads"] + old["review"]:
            if r.get("format") == "video" and r.get("transcript_url"):
                dest = os.path.join(folder, r["transcript"])
                if os.path.isfile(dest) and os.path.getsize(dest) > 0:
                    continue
                try:
                    fetch(r["transcript_url"], dest)
                    body = open(dest, "rb").read().decode("utf-8", "replace")
                    with open(dest, "w", encoding="utf-8") as fh:  # first line = source (07 Step 8)
                        fh.write("source: brandsearch-url\n" + body)
                    print(f"  transcript {r['short_id']}: saved")
                except Exception as e:  # noqa: BLE001
                    print(f"  transcript {r['short_id']}: fetch failed ({e}) -> transcribe_ad (1 credit)")

    counts = {}
    for r in old["ads"]:
        k = f"{r.get('platform')}/{r.get('status')}/{r.get('format')}"
        counts[k] = counts.get(k, 0) + 1
    meta["counts"] = dict(sorted(counts.items()))
    meta["counts"]["total_ads"] = len(old["ads"])
    meta["counts"]["excluded"] = len(old["excluded"])
    meta["counts"]["review"] = len(old["review"])
    order_keys = ["header", "ads", "excluded", "review"]
    old = {k: old[k] for k in order_keys if k in old} | {k: v for k, v in old.items() if k not in order_keys}
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(old, fh, indent=1, ensure_ascii=False)

    ads = old["ads"]
    vids = [r for r in ads + old["review"] if r.get("format") == "video"]
    need_tr = [r for r in vids if not (os.path.isfile(os.path.join(folder, r["transcript"]))
                                       and os.path.getsize(os.path.join(folder, r["transcript"])) > 0)]
    need_vid = [r for r in vids if not r.get("video_file")]
    by = {}
    for r in ads:
        k = (r.get("platform"), r.get("format"), r.get("status"))
        by[k] = by.get(k, 0) + 1
    print(f"ad_inventory.json: {len(ads)} ads, {len(old['review'])} to review, {len(old['excluded'])} excluded "
          f"(this run: +{new_counts['ads']} ads, +{new_counts['review']} review, {new_counts['updated']} updated)")
    for k, v in sorted(by.items(), key=lambda kv: str(kv[0])):
        print(f"  {k[0]:<9} {k[1]:<8} {str(k[2]):<8} {v}")
    print(f"videos: {len(vids)} · transcripts missing: {len(need_tr)} "
          f"(Meta: transcribe_ad, 1 credit each = {sum(1 for r in need_tr if r.get('platform') in ('meta', 'instagram'))} credits; "
          f"other platforms: video_transcribe.py, free)")
    print(f"video files missing: {len(need_vid)} (free URL download first; download_ad media=video = 1 credit each only if the URL is gone)")
    if pags_all:
        tot = sorted({(pg.get("file"), pg.get("total")) for pg in pags_all if pg.get("total") is not None})
        print("pagination totals seen:", ", ".join(f"{f}={t}" for f, t in tot[:12]))
    return 0


# ----------------------------------------------------------------------------- beats
def beats(a):
    g = json.load(open(a.gemini, encoding="utf-8"))
    rep_d = float(g.get("duration_s") or 0) or None
    real = a.duration or rep_d
    if not real:
        print("no duration: pass --duration")
        return 1
    k = (real / rep_d) if (a.duration and rep_d) else 1.0

    def T(x):
        return round(float(x) * k, 1)

    print(f"duration: {real:.1f}s" + (f" (Gemini said {rep_d:.1f}s, times scaled x{k:.3f})" if abs(k - 1) > 0.01 else ""))
    bm = g.get("beat_map") or []
    vo = [(T(v.get("start_s", 0)), T(v.get("end_s", 0)), v.get("text", "")) for v in g.get("vo") or []]
    ov = [(T(o.get("start_s", 0)), T(o.get("end_s", 0))) for o in g.get("overlays") or []]
    hook = g.get("hook") or {}
    print(f"HOOK DURATION:      {T(hook.get('ends_s', 0))}s")
    lines = []
    for b in bm:
        s, e = T(b.get("start_s", 0)), T(b.get("end_s", 0))
        d = max(0.0, e - s)
        words = 0.0
        for vs, ve, txt in vo:
            ol = max(0.0, min(e, ve) - max(s, vs))
            if ve > vs and ol > 0:
                words += len(txt.split()) * ol / (ve - vs)
        wps = words / d if d else 0
        lines.append(f"{s:.1f}–{e:.1f}s ({d:.1f}s, {100 * d / real:.0f}%) {b.get('beat', '?')} — {b.get('function', '')} [{wps:.1f} WPS]")
    print("BEAT MAP:           " + ("\n                    ".join(lines) if lines else "(no beat_map in JSON)"))
    step = 0.1
    n = int(real / step)
    v_t = o_t = only_o = none = 0
    for i in range(n):
        t = i * step + step / 2
        inv = any(s <= t < e for s, e, _ in vo)
        ino = any(s <= t < e for s, e in ov)
        v_t += inv
        o_t += ino
        only_o += (ino and not inv)
        none += (not inv and not ino)
    pct = lambda x: 100 * x / n if n else 0  # noqa: E731
    print(f"VO/TEXT SPLIT:      VO {pct(v_t):.0f}% · on-screen text only {pct(only_o):.0f}% · music-only {pct(none):.0f}% "
          f"(text on screen {pct(o_t):.0f}% of the time, overlapping VO {pct(o_t - only_o):.0f}%)")
    vo_words = sum(len(t.split()) for _, _, t in vo)
    vo_secs = sum(max(0, e - s) for s, e, _ in vo)
    print(f"PACING:             {vo_words / vo_secs if vo_secs else 0:.2f} WPS average over {vo_secs:.1f}s of VO "
          f"({vo_words} words); per beat in BEAT MAP")
    print(f"FORMAT (Gemini):    {g.get('format', '')}")
    print(f"FRAMEWORK (Gemini): {g.get('framework', '')}")
    print(f"MUSIC/SFX (Gemini): {g.get('music', '')}")
    cta = g.get("cta") or {}
    print(f"CTA (Gemini):       \"{cta.get('text', '')}\" at {T(cta.get('start_s', 0))}s; urgency: {cta.get('urgency', '')}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Step Alpha: quality gate (check), ad inventory (inventory), "
                                             "video beat metrics (beats).",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("check", help="run the 16-box quality gate")
    c.add_argument("path", help="PD/00_alpha folder or a dossier .md")
    i = sp.add_parser("inventory", help="build/update ad_inventory.json from Brandsearch dumps")
    i.add_argument("--alpha-dir", required=True)
    i.add_argument("--dumps", nargs="+", required=True, help="[meta|tiktok|instagram|other:]FILE")
    i.add_argument("--keyword", action="append", help="product keyword (repeatable); rows without any go to review")
    i.add_argument("--expected-total", type=int, help="ads Brandsearch reports for the advertiser (all statuses)")
    i.add_argument("--fetch-videos", metavar="DIR", nargs="?", const="",
                   help="download video URLs to DIR/<id>.mp4 (free; default PD/05_ads/competitor/videos)")
    i.add_argument("--fetch-images", metavar="DIR", nargs="?", const="",
                   help="download image URLs of non-video ads to DIR/<id>.<ext> (free; default PD/05_ads/competitor/images)")
    i.add_argument("--fetch-transcripts", action="store_true", help="save transcript_url text (free)")
    b = sp.add_parser("beats", help="1.8 beat map / VO-text split / WPS from a video_gemini.py JSON")
    b.add_argument("gemini")
    b.add_argument("--duration", type=float, help="real duration in seconds (ffprobe)")
    argv = sys.argv[1:]
    if argv and argv[0] not in ("check", "inventory", "beats", "-h", "--help"):
        argv = ["check"] + argv  # `alpha_gate.py PD/00_alpha/ALPHA_DOSSIER.md` = check
    a = ap.parse_args(argv)
    if a.cmd == "check":
        return gate(a.path)
    if a.cmd == "inventory":
        return inventory(a)
    return beats(a)


if __name__ == "__main__":
    sys.exit(main())
