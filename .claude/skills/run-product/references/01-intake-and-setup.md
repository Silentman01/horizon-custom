# Phase 0 — Intake, preflight and setup

Goal: in a few minutes, know exactly what to build, for which market, with which tools, and have the folders and BRIEF.md ready so sub-agents can start immediately.

## Contents
1. Parse the prompt
2. Ask only blocking questions
3. Preflight checks
4. Create PRODUCT_DIR and BRIEF.md
5. Git setup (before and after the branding gate)
6. Hand-off to Phase 1

---

## Step 1 — Parse the prompt
**Purpose:** extract every input the operator already gave so you never ask twice.
**Do:**
1. Collect competitor URL(s). Normalise to the product URL without query strings (keep `?variant=` only if the operator points at a specific variant). Derive `COMPETITOR_HOME` = the root of the first competitor's domain (home page is cloned too, stream A4).
2. Detect the market: explicit ("we want to run in US"), currency symbols, language of the prompt is *not* proof of market (the operator writes in English for French stores and vice versa).
3. Detect a brand name if given ("brand name: Noxis"), a mode ("faithful"/"1:1" → A, "improve"/"optimize" → B), scope words ("start with branding", "only ads", "everything").
4. Note attached files (e.g. a methodology prompt like `PROMPT_1-1.MD`, competitor HTML/PDF) — read them; if they sit in the theme repo, git-ignore them in Step 5.
5. Check for an existing `PRODUCT_DIR/BRIEF.md` (resume case) — if present, load its decisions and skip what's done.
**Output:** a filled input table (in your head, then in BRIEF.md).
**Done when:** you know URL, market (or need to ask), brand (or Phase 2 decides), mode, scope.

## Step 2 — Ask only blocking questions
**Purpose:** keep the one-prompt promise; the operator wants momentum.
Ask in one message, only if unknown:
- Market (country/language/currency) — blocks names, copy, prices.
- `PRODUCTS_ROOT` — first run only (operator default `G:\Ecom\Products`); then remember it in BRIEF and memory.
- Our domain + support email for the policies — can wait until the branding gate (ask together with the name choice).
Do **not** ask about: domains (rule 3), palette/title (1:1 by default), mode (A by default), store (only needed at delivery), images (we remake them).
If the operator already said "go", start Phase 1 while waiting for the answer — capture and ad pulls don't depend on it.

## Step 3 — Preflight checks
Run these quickly (one Bash call where possible). Record results in BRIEF.md "Tooling".

| Check | Command / method | If it fails |
|---|---|---|
| Theme repo | `git status --short`, `git branch --show-current`, `git remote -v` | uncommitted work → don't touch it; stash only with the operator's consent or work around it |
| Theme type | read `config/settings_schema.json` → `theme_info.theme_name` (Horizon, Dawn, …) | follow the generic path in 04 |
| Shopify CLI | `shopify version`; store from `shopify.theme.toml` / previous pushes / operator | build locally + GitHub, ask for store at delivery |
| Python + Pillow | `python -I -c "import PIL; print(PIL.__version__)"` | `pip install pillow` |
| Node + liquidjs | `node -v`; liquidjs in a scratch dir (`npm i liquidjs@10`) | skip local render QA, rely on theme check + mocks |
| Browser | Edge `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` or Chrome | screenshots unavailable → use competitor PDF/screens if the operator provides them |
| Kie key + credits | `KIE_API_KEY` env, project skill config, or operator; `curl -s -H "Authorization: Bearer $KEY" https://api.kie.ai/api/v1/chat/credit` | ask for the key; if balance < ~260, warn and plan priorities (SKILL §7) |
| Brandsearch MCP | `ToolSearch` query "brandsearch" → tools `mcp__claude_ai_Brandsearch__*` | tell the operator to connect it (`claude mcp add` / MCP menu) and run everything else |
| Shopify Admin token (policies) | `SHOPIFY_ADMIN_TOKEN` env (custom app, `write_legal_policies`) | policies delivered as files + operator to-do |

Windows notes: Bash is Git Bash; run Python with `-I`; set `sys.stdout.reconfigure(encoding="utf-8")` in scripts (cp1252 console crashes on ✓ and accents); paths with spaces in quotes.

## Step 4 — Create PRODUCT_DIR and BRIEF.md
**Do:**
1. Before the brand exists: `PRODUCT_DIR = PRODUCTS_ROOT/_<competitor-slug>` (e.g. `_plaims-headlight-glasses`). After the gate, rename to `PRODUCTS_ROOT/<BRAND>`.
2. Create the tree:
```bash
D="$PRODUCTS_ROOT/_plaims-headlight-glasses"
mkdir -p "$D"/{01_branding,02_competitor/page,02_competitor/home,02_competitor/media,03_product-images,04_page-images,05_ads/competitor/raw,05_ads/generated,06_policies/source,scratch}
```
3. Copy `templates/BRIEF.md` to `PRODUCT_DIR/BRIEF.md` and fill: inputs, market, mode, tooling results, credit balance, open questions.
4. Keep BRIEF.md current: every decision (brand, palette, title, store, theme id, branch) is written there — sub-agents read it instead of you re-explaining.
**Done when:** folders exist, BRIEF.md has inputs + tooling.

## Step 5 — Git setup
**Before the gate:** don't create branches yet (the name isn't known). Don't modify the repo.

**After the brand is approved:**
1. Make sure your current branch has no uncommitted changes you made; never discard the operator's.
2. Create the brand branch from a clean, up-to-date `main`:
```bash
git fetch origin
git checkout -b <brand_slug> origin/main      # e.g. noxis
```
   If uncommitted files block the checkout (e.g. a modified `.gitignore`), stash *your own* change, switch, then re-apply it. If `.gitignore` doesn't exist on main, recreate it there rather than popping a conflicting stash.
3. `.gitignore` on the brand branch: add the operator's prompt/brief files and local asset folders (e.g. `PROMPT_1-1.MD`, `inspiration/`, `product-images/`).
4. Record branch name in BRIEF.md. All brand files use the slug prefix (`blocks/noxis-*.liquid`, `assets/noxis-*.webp`).
**Why from main:** another brand's branch carries its templates, settings and assets; mixing brands contaminates both stores.

## Step 6 — Hand-off to Phase 1
Launch, in one message, the capture agent and the media agent (briefs in `subagent-briefs.md`), and start the Brandsearch pulls yourself (07). Then do branding (02) as soon as `capture.md` lands.
