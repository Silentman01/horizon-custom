# 15 — Run contract: inputs, reporting, partial runs

Detail behind `SKILL.md` (formerly its §1, §8 and §9). Phase 0 steps are in `01-intake-and-setup.md`.

## Contents
1. Inputs and the one-prompt contract
2. Reporting to the operator
3. Partial runs and resuming

---

## 1. Inputs and the one-prompt contract

Parse the prompt; ask only for what blocks progress.

| Input | Required | Default / how to get it |
|---|---|---|
| `COMPETITOR_URL` | yes | from the prompt (one or more product URLs) |
| `COMPETITOR_HOME` | no | the competitor's home page — default: the root of the first competitor domain (`https://plaims.com/`); if several competitors were sent, clone the home of the one whose product page is cloned unless told otherwise |
| `MARKET` (country, language, currency) | yes | ask if not stated — names, copy and currency depend on it (Noxis run: US, English, USD) |
| `BRAND` | no | produced in Phase 2; if the prompt names it, skip the branding gate |
| Brand guideline file | no | if given (palette, fonts, UI, product name) it overrides the 1:1 palette/fonts/title; copy it to `01_branding/` |
| `MODE` | no | **A — faithful clone** (default for product tests); B only if asked |
| `PRODUCTS_ROOT` | first run | ask once, then record in BRIEF (operator default `D:\Ecom\Products`) |
| `STORE` / draft `THEME_ID` | no | needed only to push a draft theme; otherwise push to GitHub and ask at delivery |
| `KIE_API_KEY` | for images/ads | env var, project skill config, or ask |
| `OUR_DOMAIN`, `SUPPORT_EMAIL` | for policies | ask at the branding gate if unknown (myshopify domain until a custom domain exists); never invent |
| `SHOPIFY_ADMIN_TOKEN` | to push policies | custom app Admin API token with `write_legal_policies`; without it policies are delivered as files + to-do |
| Brandsearch MCP | for Step Alpha + ads | tools `mcp__claude_ai_Brandsearch__*`: complete ad footprint + a transcript of every video ad (Phase 1.3); if missing, tell the operator to connect it or to provide the ads — Step Alpha waits for the footprint, capture continues |
| ChatGPT market research | yes (GATE α) | the operator runs our tailored prompt (`00_alpha/chatgpt/CHATGPT_PROMPT.md`) in ChatGPT and pastes the full result back → `00_alpha/chatgpt/CHATGPT_RAW.md` |
| `ARGOLINK_API_KEY` | for Step Alpha 1.2 | env or `D:/Ecom/Products/.secrets/argolink.env` (`video_gemini.py`, video beat maps) |

One prompt runs everything. Nothing is built until Step Alpha passes its quality gate (00 §17). Planned stops (gates), in run order:
1. **GATE α — ChatGPT market research** (always, every run that builds anything). After α3, give the operator ONE ready-to-paste prompt block (the full `CHATGPT_PROMPT.md`, nothing to edit) with one line: "run this in ChatGPT and paste the full result back". Then stop: the run waits. When the result arrives, save it verbatim to `00_alpha/chatgpt/CHATGPT_RAW.md` and continue with α4–α6. No downstream step starts while waiting ("After ChatGPT data returns" is a hard dependency). Phase 1 raw-data gathering may still finish.
2. **Alpha quality gate (α6)** — not an operator stop: `alpha_gate.py` + read-through; a fail sends the run back to the failing Alpha step; only a pass releases Phase 2.
3. **Branding gate** — the operator picks the brand (skipped if the prompt names it).
4. **AD_VARIANTS gate** — before any ad is generated (08 §1b).
5. **Video candidates** and **(c) clips** — only when video ads are requested (14).

Everything else runs to completion, in parallel, and ends with one delivery report. If the operator says "start with branding, wait for validation", run Step Alpha first (GATE α included), then stop at the branding gate; if they say "go all the way", still stop at GATE α and at the branding gate unless the brand is already given.

## 2. Reporting to the operator
- Short progress lines at milestones; never narrate internal deliberation.
- Show images, don't describe them: contact sheets for gallery remakes, top-10 competitor ads, generated ads.
- Gate message (branding) = tables + picks, nothing else.
- GATE α message = one line of instruction + the prompt in one copy block, nothing else.
- Delivery = what was built, where files are, what the operator must do, credits spent. No claim caveats (rule 1).

## 3. Partial runs and resuming
The operator often asks for one step ("just the ads", "remake their images", "branding only"). Enter at the matching phase: create/reuse PRODUCT_DIR and BRIEF.md, run only the needed preflight checks, and pull inputs you lack (e.g. ads need the packshot → generate it first). If BRIEF.md already exists, read it and continue from its decisions instead of redoing earlier phases.
Every entry point that builds or generates anything (branding, page, images, ads, ad copy, videos) needs a passed Step Alpha first. If BRIEF.md records a passed Alpha gate and `00_alpha/ALPHA_DOSSIER.md` exists, reuse it. Otherwise the run resumes at the **first unmet Alpha step** in the BRIEF.md progress rows (α0 → α1 → α2 → α3 → GATE α → α4 → α5 → α6): files already in `00_alpha/` are kept, and a run stopped at GATE α re-sends the same prompt block and waits.
