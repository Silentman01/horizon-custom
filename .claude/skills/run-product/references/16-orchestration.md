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
| Coordinator | the main session (you) | operator's session model | inputs, gates, Brandsearch MCP pulls (dump to files), git + Shopify pushes, final acceptance, BRIEF.md |
| **Lead A — Store lead** | `Agent`, `model: "opus"`, `effort: "low"` | Opus 5.5, low | capture → SECTION_SPEC → copy → build (product + home) → policies → page QA |
| **Lead B — Growth lead** | `Agent`, `model: "opus"`, `effort: "low"` | Opus 5.5, low | packshot → gallery remakes → page images/GIFs → ad analysis → 25 ads → ad copy |
| Workers (writing, code, vision) | spawned by a lead | `model: "sonnet"` | conversion architect, copywriter, section builder, ad analysts, image-prompt writers, ad copy, visual QA |
| Workers (mechanical) | spawned by a lead | `model: "haiku"` | capture/screenshot/fetch scripts, downloads, GIF→WebP, contact sheets, policies fetch/transform, rank_ads runs, theme check runs |

How it runs:
1. Coordinator finishes Phase 0, pulls Brandsearch dumps, then launches **both leads in one message** (background), each with its lead brief from `references/subagent-briefs.md` (§Lead A / §Lead B) + BRIEF.md path.
2. Each lead plans its stream, launches its workers in parallel with explicit `model` values, verifies every return itself (opens images, reads files, runs checks) and only escalates a task to itself (Opus) when a worker failed twice or the task needs judgment (claims, 1:1 fidelity calls, fixing a broken build).
3. Leads write code/JSON/images directly; documents come back as text and the lead (or coordinator) saves them. Leads never push, publish or call Brandsearch; they report "ready to push" with a file list.
4. Coordinator reviews the two lead reports, runs the push sequence (commit → pull → merge-check → push), writes DELIVERY.md.
5. If a lead can't spawn workers (no `Agent` tool in its context), it does the worker steps itself and keeps outputs short; the model split still applies to whatever the coordinator spawns.

Constraints:
- Sub-agents may be refused when writing report/markdown files ("Subagents should return findings as text") → return documents as text.
- Workers get only the context they need (paths + exact task); leads keep the big picture. Never duplicate a running agent's work; process completions as they arrive; resume a stalled agent with `SendMessage` instead of relaunching.
- Usage limits hit all agents at once: if agents die on a rate limit, resume them (SendMessage "continue where you stopped") after the reset.

## 2. Dependency map

```
Phase 0 ─┬─ Capture agent ──┬──────────────► Branding ──► GATE ──┬─ A1 spec ─► A2 copy ─► A3 build ─┤
         │  (product + home)│                                     ├─ A4 home spec/copy ──► home build ─┤ (after A3 + B)
         ├─ Media agent ────┤ (gallery, GIFs)                     ├─ B packshot ─► gallery remakes ───┤
         └─ Brandsearch ────┴─ rank_ads ───────────────────────────┼─ C page images/GIF webp ─────────┤
                                                                   ├─ D1 analysts ─┬─ D2 25 ads ──────┤
                                                                   │   (+packshot)─┘                  │
                                                                   └─ E ad copy (after D1) ───────────┴─► QA ─► Delivery
```
Brandsearch pulls and capture don't need the brand, so they run before the gate; generation work needs the brand, so it waits.
Video ads (14) are a separate stream, only on request: Brandsearch video pull → `REMAKE_CANDIDATES.md` → **operator gate** → per-video remake (needs the packshot and AD_COPY offer; class (c) regenerations need a second operator OK) → independent check → finals.
