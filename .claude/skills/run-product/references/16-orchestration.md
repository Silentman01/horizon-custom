# 16 — Orchestration model and dependency map

Detail behind `SKILL.md` (formerly its §3 and §5). Briefs to launch: `subagent-briefs.md`.

## Contents
1. Orchestration model (coordinator → 2 Opus leads → cheap workers)
2. Dependency map

---

## 1. Orchestration model (coordinator → 2 Opus leads → cheap workers)

Cost rule: expensive reasoning only where judgment matters; everything mechanical runs on the cheapest model that can do it. Model guide: https://platform.claude.com/docs/en/about-claude/models/choosing-a-model (Opus = hardest reasoning, Sonnet = balanced quality/cost for writing, code and vision, Haiku = fastest/cheapest for mechanical work).

| Tier | Who | Model / effort | Owns |
|---|---|---|---|
| Coordinator | the main session (you) | operator's session model | inputs, gates (GATE α, branding, variants), Brandsearch MCP pulls (complete footprint + every video transcript, dump to files), Alpha dossier (α5) + quality gate (α6), git + Shopify pushes, final acceptance, BRIEF.md |
| **Lead A — Store lead** | `Agent`, `model: "opus"`, `effort: "low"` | Opus 5.5, low | Alpha: α1.1 customer intelligence + α1.3 funnel congruence · then (capture exists from Phase 1) SECTION_SPEC → copy → build (product + home) → policies → page QA |
| **Lead B — Growth lead** | `Agent`, `model: "opus"`, `effort: "low"` | Opus 5.5, low | Alpha: α1.2 advertising intelligence + α1.4 angle cards + α2 hidden angles + α3 ChatGPT prompt (+ α4 synthesis after GATE α) · then packshot → gallery remakes → page images/GIFs → ad variants → 25 ads → ad copy |
| Workers (writing, code, vision) | spawned by a lead | `model: "sonnet"` | Alpha α-analyst batches (1.2, video + static ads), α-angles (2.1 explosion), conversion architect, copywriter, section builder, image-prompt writers, ad copy, visual QA |
| Workers (mechanical) | spawned by a lead | `model: "haiku"` | capture/screenshot/fetch scripts, downloads, `video_gemini.py` runs, GIF→WebP, contact sheets, policies fetch/transform, rank_ads runs, theme check runs |

How it runs:
1. Coordinator finishes Phase 0 and Phase 1 (capture + media agents, policies fetch, the complete Brandsearch footprint + every video transcript, `ad_inventory.json`), then launches **both leads' Alpha parts in one message** (background): briefs Lead A α and Lead B α in `references/subagent-briefs.md` §Step Alpha briefs + BRIEF.md path.
2. Lead B returns 1.2 and Lead A returns 1.1; the coordinator saves them to `00_alpha/analysis1/`, sends Lead A the per-ad angle/avatar/promise tags from 1.2 to finish 1.3 (`SendMessage`), then continues Lead B with 1.4 → 2.1 → 2.2 once 1.1 + 1.3 are saved. Coordinator runs **GATE α** (one prompt block to the operator, wait), saves `CHATGPT_RAW.md`, continues Lead B with α4 (brief α-synthesis), writes the dossier (α5), runs the quality gate (α6). Detail: `20-step-alpha-runbook.md`.
3. Only after α6 passes: branding (coordinator) → branding gate. Then continue **both leads in one message** with their Phase 3 lead briefs (§Lead A / §Lead B; `SendMessage` keeps their Alpha context, or launch fresh with the brief + dossier path). Every worker brief names the dossier sections it reads.
4. Each lead plans its stream, launches its workers in parallel with explicit `model` values, verifies every return itself (opens images, reads files, runs checks) and only escalates a task to itself (Opus) when a worker failed twice or the task needs judgment (claims, 1:1 fidelity calls, fixing a broken build).
5. Leads write code/JSON/images directly; documents come back as text and the lead (or coordinator) saves them. Leads never push, publish or call Brandsearch; they report "ready to push" with a file list.
6. Coordinator reviews the two lead reports, runs the push sequence (commit → pull → merge-check → push), writes DELIVERY.md.
7. If a lead can't spawn workers (no `Agent` tool in its context), it does the worker steps itself and keeps outputs short; the model split still applies to whatever the coordinator spawns.

Constraints:
- Sub-agents may be refused when writing report/markdown files ("Subagents should return findings as text") → return documents as text.
- Workers get only the context they need (paths + exact task); leads keep the big picture. Never duplicate a running agent's work; process completions as they arrive; resume a stalled agent with `SendMessage` instead of relaunching.
- Usage limits hit all agents at once: if agents die on a rate limit, resume them (SendMessage "continue where you stopped") after the reset.

## 2. Dependency map

```
Phase 0 ─┬─ Capture agent (product + home) ──┐
         ├─ Media agent (gallery, GIFs) ─────┤
         ├─ Policies fetch ──────────────────┤
         └─ Brandsearch: complete footprint ─┴─► α0 inputs ─┬─ Lead A: α1.1 customer ─► α1.3 congruence ─┐
            + every video transcript                         │                     ▲ (per-ad tags from 1.2) │
            + rank_ads top 30 (for remakes)                  └─ Lead B: α1.2 ads (α-analyst batches) ──────┴─► α1.4 angle cards

α1.4 ─► α2 hidden angles ─► α3 ChatGPT prompt ─► GATE α (operator pastes ChatGPT result) ─► α4 synthesis ─► α5 dossier ─► α6 quality gate

α6 pass ─► Branding ─► GATE ─┬─ A1 spec ─► A2 copy ─► A3 build ─────────┤
                             ├─ A4 home spec/copy ──► home build ───────┤ (after A3 + B)
                             ├─ B packshot ─► gallery remakes ──────────┤
                             ├─ C page images/GIF webp ─────────────────┤
                             ├─ D2a variants ─► op gate ─► D2 25 ads ───┤ (D2 also needs the packshot)
                             ├─ E ad copy ──────────────────────────────┤
                             └─ I CSV · H checkout header · F policies ─┴─► QA ─► Delivery
```
Capture, media, policies fetch and Brandsearch pulls are raw-data gathering, so they run first. Everything that builds or generates (branding, spec, copy, pages, images, ads, ad copy, videos, CSV, checkout header, policies transform) waits for the Alpha quality gate and reads the dossier (ALPHA_DOSSIER.md): ad variants, ad creatives, ad copy and video ads depend on Alpha (angle cards 3.1, hook library 3.3, framework library 3.4, language bank 3.5).
Video ads (14) are a separate stream, only on request and after Alpha: candidates from the ranked footprint (validated + opportunity angles first, dossier 1.8/3.4 beat maps and frameworks) → `REMAKE_CANDIDATES.md` → **operator gate** → per-video remake (needs the packshot and AD_COPY offer; class (c) regenerations need a second operator OK) → independent check → finals.
