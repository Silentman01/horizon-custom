# BRIEF — <BRAND or _competitor-slug>

_Single source of truth for this product. Sub-agents read this file. Update it after every decision._

## Inputs
| Field | Value |
|---|---|
| Competitor URL(s) | |
| Market (country / language / currency) | |
| Mode | A — faithful clone (default) / B — intelligent clone |
| Scope | full run / branding only / page only / images only / ads only |
| Operator files | (e.g. PROMPT_1-1.MD, competitor PDFs) |

## Decisions
| Decision | Value | Date |
|---|---|---|
| Brand name | | |
| Brand slug / CSS prefix | | |
| Product title (1:1 pattern) | | |
| Palette (1:1 hex + roles) | | |
| Fonts | | |
| Offer / bundle tiers + prices | | |
| Angle strategy (Step Alpha): lead angle cards (V/O IDs) · page architecture (one multi-angle page / angle-specific pages) | | |
| Git branch | | |
| Store (myshopify) / draft theme id | | |
| Our domain / support email (policies) | | |

## Paths
| Item | Path |
|---|---|
| THEME_DIR | |
| PRODUCT_DIR | |

## Tooling (preflight)
| Tool | Status |
|---|---|
| Theme type | |
| Shopify CLI | |
| Python + Pillow | |
| Node + liquidjs | |
| Browser for screenshots | |
| Kie key / credits at start | |
| Brandsearch MCP / credits at start | |
| ArgoLink key (video_gemini.py) | |

## Progress
- [ ] Phase 1 capture (page, media, complete ad footprint + every video transcript, top 30 ranked)
- [ ] α0 inputs (`00_alpha/ad_inventory.json`, `transcripts/`)
- [ ] α1 analysis 1 (1.1 customer · 1.2 advertising · 1.3 congruence · 1.4 angle cards)
- [ ] α2 hidden angles (2.1)
- [ ] α3 ChatGPT prompt (`chatgpt/CHATGPT_PROMPT.md`)
- [ ] GATE α prompt sent (date) · operator's ChatGPT result saved (`chatgpt/CHATGPT_RAW.md`, date)
- [ ] α4 opportunity synthesis (2.3)
- [ ] α5 ALPHA_DOSSIER.md
- [ ] α6 quality gate: alpha_gate.py <16/16 pass / fail> · read-through <pass/fail> · date · failing items · counts (avatars, pains, ads, videos, V/H/E/O cards)
- [ ] Phase 2 branding approved
- [ ] A1 section spec · A2 copy · A3 build
- [ ] A4 home page (HOME_SPEC, index.json)
- [ ] B packshot · gallery remakes
- [ ] C page images · GIF WebP
- [ ] D2a ad variants approved · D2 25 ads
- [ ] E ad copy
- [ ] F policies (fetched · transformed · reviewed · pushed)
- [ ] QA passed
- [ ] Delivery (GitHub push, draft theme push, DELIVERY.md)

## Open questions / operator to-dos
-
