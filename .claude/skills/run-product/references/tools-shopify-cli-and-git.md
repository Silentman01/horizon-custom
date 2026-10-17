# Tools — Shopify CLI and git (branch, pull, merge, check, push)

Command reference and safety procedure for every theme write in a run. The master runs these; builder/QA sub-agents never run git or `shopify theme push/pull` (their briefs say so).

## Contents
1. Golden rules (and the incidents behind them)
2. Preflight
3. Branch per brand
4. Committing
5. Pull before push (git + live theme)
6. Merging Shopify bot commits safely
7. Theme check
8. Pushing to a draft theme
9. Live templates with ad traffic (v1/v2 swap)
10. Push errors and fixes
11. No store connected
12. Quick reference card

---

## 1. Golden rules
| Rule | Why (what happened) |
|---|---|
| One branch per brand, created from clean `origin/main` | Another brand's branch carries its templates, settings and assets; mixing contaminates both stores. |
| **Commit before any `shopify theme pull`** | A theme pull overwrote uncommitted local work once (the `_ceriva-bundle-tier` thumbnail work was lost and had to be redone). Pull writes files straight to disk; git is the only undo. |
| Always pull (git + live theme) before pushing | The operator and the Shopify editor change the theme too; pushing blind deletes their edits. |
| `git pull --no-rebase`, then verify your files survived | The Shopify GitHub integration adds bot commits ("Update from Shopify for theme …") that can carry stale copies of your files. |
| Push with `--only <files>` and `--nodelete` | A full push replaces the whole theme and deletes remote-only files (editor-made templates, app files). |
| Push only to an unpublished (draft) theme id; never `--publish` | Publishing is the operator's call. |
| Never overwrite a template that receives live ad traffic | Build `<template>.<slug>-v2`, swap on approval, keep `-v1` (§9). |
| The theme repo is the operator's live work | Never `reset --hard`, `checkout -- .`, `clean`, force-push or stash the operator's changes without consent. |

## 2. Preflight
```bash
git -C "$THEME_DIR" status --short          # uncommitted work? whose?
git -C "$THEME_DIR" branch --show-current
git -C "$THEME_DIR" remote -v                # GitHub remote (Shopify GitHub integration uses it)
shopify version                              # CLI 3.x (tested 4.x of the theme commands' syntax below)
shopify theme list --store "$STORE" --json   # only if STORE known: ids, names, roles (live / unpublished / development)
```
- Read `config/settings_schema.json` → `theme_info` (name, version) to know which theme you're on (04 §1).
- Record `STORE`, `THEME_ID` (draft) and its **role** in BRIEF. If the only theme id you have is `role: live`, stop and ask for a draft (or "Duplicate" of live) before any push.
- Baseline theme check on `main` (§7) — save the offense list so you can prove later that you added none.

## 3. Branch per brand
After the branding gate (01 §5):
```bash
git fetch origin
git switch -c "$BRAND_SLUG" origin/main      # e.g. noxis
```
- If your *own* uncommitted edit blocks the switch, stash only that file (`git stash push -- <file>`), switch, re-apply. Never stash the operator's files without asking.
- `.gitignore` on the brand branch: the operator's prompt files and local asset folders (`PROMPT_*.MD`, `inspiration/`, `product-images/`). Product assets live in `PRODUCT_DIR`, never in the repo.
- Read other branches without switching: `git show ceriva:blocks/_ceriva-bundle-tier.liquid`, `git diff main..noxis --stat`.

## 4. Committing
- Stage specific paths, never `git add -A` (the operator may have unrelated work in progress):
```bash
git add blocks/noxis-*.liquid blocks/_noxis-*.liquid sections/noxis-*.liquid snippets/noxis-*.liquid \
        assets/noxis-* templates/product.json config/settings_data.json sections/header-group.json .gitignore
git commit -m "Build Noxis product page (Plaims clone, mode A)" -m "<attribution line from the session>"
```
- One commit per milestone (build, visuals, copy fixes). Messages say what changed for the merchant.
- Note the commit hash (`git rev-parse HEAD`) — you need it in §6.

## 5. Pull before push
Order matters: **commit → git pull → theme pull → diff → commit/merge → push.**
```bash
git pull --no-rebase origin "$BRAND_SLUG"           # only if the remote branch exists (git ls-remote --heads origin "$BRAND_SLUG")
shopify theme pull --store "$STORE" --theme "$THEME_ID" \
  --only templates/product.json --only config/settings_data.json --only sections/header-group.json \
  --only sections/footer-group.json --only 'sections/noxis-*' --only 'blocks/*noxis*'     # exactly the files you'll push
git status --short && git diff                      # what changed live since your commit?
```
- Empty diff → push. Non-empty diff → those are live edits (operator in the editor, an app, a review widget). Merge them into your version deliberately (keep their settings, re-apply your change), commit, then push. Never just `git checkout -- file` over them.
- Template/settings JSON written by Shopify loses your formatting and keeps the `/* auto-generated */` header — that's fine; compare content, not whitespace (`git diff -w`).

## 6. Merging Shopify bot commits safely
When the store is linked to the GitHub branch, every editor save becomes a bot commit on the remote branch.
```bash
MY=$(git rev-parse HEAD)                    # your last commit, before pulling
git pull --no-rebase origin "$BRAND_SLUG"   # merge commit, no history rewrite
git diff "$MY" HEAD -- <your files>         # must be EMPTY (or only intended live edits)
```
If the diff shows your work reverted (old copy, missing blocks), restore your version of those files from `$MY` (`git checkout "$MY" -- <file>`), re-apply any genuine live edits, commit "Restore … after Shopify sync". Never `--rebase` or force-push a branch Shopify writes to.

## 7. Theme check
```bash
shopify theme check --path "$THEME_DIR" --output json > "$SCRATCH/tc.json"   # or plain text without --output
```
- Pass = **no new offenses** vs the baseline from `main`. Horizon ships baseline offenses (e.g. `ExcessiveSettingsCount` on header, `UnusedDocParam` on divider) — leave them.
- Offenses you will hit in custom files and the fix:
  | Check | Cause | Fix |
  |---|---|---|
  | `ValidScopedCSSClass` | `{% stylesheet %}` uses a class defined in another file | Define every class used in the file's own stylesheet; duplicate tiny base rules per file instead of sharing a base stylesheet |
  | `RemoteAsset` | Google Fonts / CDN script or image | Self-host in `assets/` or use the theme font picker |
  | `AssetPreload` | Hand-written `<link rel=preload>` | `{{ 'x.css' \| asset_url \| preload_tag: as: 'style' }}` |
  | `UndefinedObject` / `UnusedAssign` | Leftover variables | Remove or use them |
  | `ImgWidthAndHeight` | `<img>` without dimensions | Add `width`/`height` (CLS) |
  | `MissingTemplate` / `MissingAsset` | Typo in `render` / `asset_url` | Fix the name |
  | `ValidSchema` / `ValidJSON` | Bad schema JSON, wrong setting type | Validate; `richtext` defaults must start with `<p>` |
- Also parse every template you generated: `python -I -c "import json,re,sys; s=open(sys.argv[1],encoding='utf8').read(); json.loads(re.sub(r'^\s*/\*[\s\S]*?\*/','',s))" templates/product.json`.

## 8. Pushing to a draft theme
```bash
shopify theme list --store "$STORE"          # confirm THEME_ID role is unpublished/development
shopify theme push --store "$STORE" --theme "$THEME_ID" --nodelete \
  --only templates/product.json --only config/settings_data.json --only sections/header-group.json \
  --only 'sections/noxis-*' --only 'blocks/*noxis*' --only 'snippets/noxis-*' --only 'assets/noxis-*'
```
- `--only` takes globs; repeat the flag. Push everything a template references (sections, blocks, snippets, assets) or the editor shows "section type not found".
- `--allow-live` is only needed when the target is the live theme; use it only when the operator explicitly asked for a live push (e.g. the live theme *is* the one linked to the brand branch and they approved). Never `--publish`.
- `config/settings_data.json` holds global settings (palette, fonts, buttons): pushing it changes the whole store's look. On a store shared with other products, push it only with the operator's OK; otherwise use section-level settings.
- After pushing: `shopify theme pull --only <same files>` into a temp copy or re-run `git diff` to confirm the remote equals your commit; share preview links: `https://<store>/products/<handle>?preview_theme_id=<id>` (+ `&view=<suffix>` for alternate templates) and the editor URL from the push output.

## 9. Live templates with ad traffic (v1/v2 swap)
If `templates/product.<x>.json` (or `index.json`) already receives paid traffic:
1. Build `templates/product.<slug>-v2.json` (same sections, new copy/layout); push it; preview with `?view=<slug>-v2`.
2. On explicit approval: copy the live content to `product.<slug>-v1.json` (rollback), then copy v2's content into the live template name (products keep their assigned template, so the URL and ads don't change). Commit "Make v2 live (v1 kept for rollback)".
3. Never rename/delete the live template — products assigned to it would fall back to the default template.

## 10. Push errors and fixes
| Error (FR/EN) | Cause | Fix |
|---|---|---|
| « La configuration « text » est non valide. Tous les nœuds de niveau supérieur doivent être des balises `<p>`, `<ul>`, `<ol>` ou `<h1>`-`<h6>` » / "Setting 'text' is invalid … top level nodes must be …" | Plain text written into a `richtext`/inline-richtext setting | Wrap in `<p>…</p>` (builder `setv()` does it automatically — 04 §6) |
| "Section type 'x' does not refer to an existing section file" | Template pushed without its section/block files | Add them to `--only` |
| "Invalid block 'x': … not allowed" | Block type not listed in the parent schema `blocks` (or `@theme` missing) | Add the type to the parent's schema |
| "setting with id='x' … value must be one of" | Select value not in options / out-of-range `range` | Use an allowed value; ranges must respect min/max/step |
| Push hangs on a prompt | Non-interactive session needs explicit target | Always pass `--store` and `--theme` (and `--allow-live` only per §8) |
| "theme pull overwrote my changes" | Pulled before committing | Recover from git if committed; otherwise redo — that's why §1 says commit first |

## 11. No store connected
(Noxis run.) Commit and push the brand branch to GitHub only: `git push -u origin "$BRAND_SLUG"`. In the delivery, ask the operator for the store domain and a draft theme id (or to connect the branch with Shopify's GitHub integration, which creates the theme from the branch). Do not create stores, themes or apps yourself.

## 12. Quick reference card
```
branch     git fetch origin && git switch -c <slug> origin/main
commit     git add <paths> && git commit -m "..." -m "<attribution>"; MY=$(git rev-parse HEAD)
git pull   git pull --no-rebase origin <slug>;  git diff $MY HEAD -- <files>   # must be empty
th. pull   shopify theme pull --store S --theme ID --only <files>; git diff   # merge live edits, commit
check      shopify theme check --path . --output json   # no new offenses vs main
push       shopify theme push --store S --theme ID --nodelete --only <files>   # draft id; never --publish
github     git push -u origin <slug>
```
