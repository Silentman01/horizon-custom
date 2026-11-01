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
| `PRODUCTS_ROOT` | first run | ask once, then record in BRIEF (operator default `G:\Ecom\Products`) |
| `STORE` / draft `THEME_ID` | no | needed only to push a draft theme; otherwise push to GitHub and ask at delivery |
| `KIE_API_KEY` | for images/ads | env var, project skill config, or ask |
| `OUR_DOMAIN`, `SUPPORT_EMAIL` | for policies | ask at the branding gate if unknown (myshopify domain until a custom domain exists); never invent |
| `SHOPIFY_ADMIN_TOKEN` | to push policies | custom app Admin API token with `write_legal_policies`; without it policies are delivered as files + to-do |
| Brandsearch MCP | for ads | tools `mcp__claude_ai_Brandsearch__*`; if missing, tell the operator to connect it and continue the rest |

One prompt runs everything. The only planned stop is the **branding gate** (operator picks the brand). Everything else runs to completion, in parallel, and ends with one delivery report. If the operator says "start with branding, wait for validation", stop at the gate; if they say "go all the way", still stop at the gate unless the brand is already given.

## 2. Reporting to the operator
- Short progress lines at milestones; never narrate internal deliberation.
- Show images, don't describe them: contact sheets for gallery remakes, top-10 competitor ads, generated ads.
- Gate message (branding) = tables + picks, nothing else.
- Delivery = what was built, where files are, what the operator must do, credits spent. No claim caveats (rule 1).

## 3. Partial runs and resuming
The operator often asks for one step ("just the ads", "remake their images", "branding only"). Enter at the matching phase: create/reuse PRODUCT_DIR and BRIEF.md, run only the needed preflight checks, and pull inputs you lack (e.g. ads need the packshot → generate it first). If BRIEF.md already exists, read it and continue from its decisions instead of redoing earlier phases.
