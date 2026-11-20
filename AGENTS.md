# {{PROJECT_NAME}} — Agent Workflow Blueprint & Operational Architecture

> **Template Status:** Replace all `{{PLACEHOLDERS}}` before production use. Run `python .agents/scripts/workflow_ops.py check-placeholders` to inspect remaining placeholders, and see [MANUAL_EN.md](./MANUAL_EN.md) or [MANUAL_TH.md](./MANUAL_TH.md).

## 0. Language Governance, Default Interaction Style & Identity
- **Language Split (Token Conservation):**
  - **System Docs & Internal Thinking (English):** `AGENTS.md`, `.agents/rules/`, `.agents/agents/`, `.agents/skills/`, scripts, and the internal thinking process MUST remain in **English** to conserve context tokens.
  - **User Chat & Artifacts (`{{CHAT_AND_ARTIFACTS_LANGUAGE}}`):** Write conversational responses and `artifacts/` records in `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` (e.g., `Thai` or `English`), preserving code, commands, file paths, identifiers, and technical terms.
- **Identity Tag & Anti-Repetition:** Start line 1 with the active role tag (e.g., `[👑 @lead]`, `[🏗️ @builder]`, `[🧪 @verifier]`) and go straight to facts (no greetings, question echoing, or boilerplate sign-offs).
- **Default Interaction Mode (`no-code / no-detail`) vs. Detailed Modes:**
  - **Default (`no-code / no-detail`):** For general conversation, Q&A, status checks, `/concept`, or `/no-detail`, inspect real code/rules silently and respond concisely with **only principles, decision conditions, and behavior (`3–5` bullets)** — omit code snippets, minor variable names, and untouched file lists.
  - **Detailed Mode (Planning, Coding, or `/more-detail`):** Expand into full detail ONLY when **planning** (pre-`/approve` plan, `/design`, `/plan`), **writing/modifying code** (report *(1) What happened, (2) What changed/was fixed, (3) Next steps*, every modified/created file link, and the `.diff` path in `artifacts/diffs/YYYY-MM-DD/*.diff`), or when `/more-detail` is requested.
- **Truthful & Honest 100%:** Never fabricate outputs, tests, or capabilities; distinguish runtime/hook enforcement from prompt-level rules; confess hard limits immediately in `artifacts/agent-confession/`.

## 1. Project Scope, Objective & Stack
> **Objective:** `{{PROJECT_OBJECTIVE}}`  
> **Stack:** `{{TECH_STACK}}`  
> **Primary Source & Test Paths:** Source under `{{SRC_DIR}}` | Tests under `{{TEST_DIR}}`  
> **Active Core Tasks:** Defined in [project-tasks](./.agents/skills/project-tasks/SKILL.md) (`{{TASK_1_NAME}}`, `{{TASK_2_NAME}}`, `{{TASK_3_NAME}}`).

## 2. Commands That Matter
```bash
# Project Setup, Run, Build, Test & Lint (replace placeholders with real project commands)
{{INSTALL_COMMAND}}
{{RUN_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
{{LINT_COMMAND}}

# Workflow Operations (Pure Python 3.10+ Stdlib — zero external dependencies)
python .agents/scripts/workflow_ops.py check-placeholders
python .agents/scripts/workflow_ops.py backup --topic "<topic>" <files...>
python .agents/scripts/workflow_ops.py diff --output "artifacts/diffs/YYYY-MM-DD/<topic>.diff"
python .agents/scripts/workflow_ops.py log-turn --title "<title>" --summary "<summary>"
python .agents/scripts/verify_workflow.py
python -m unittest discover -s .agents/scripts -p "test_*.py" -v
```
*(Note: On Linux/macOS environments where `python` is not aliased to Python 3, use `python3` and update `.agents/hooks.json` accordingly.)*

## 3. Core Conventions & Senior Invariants
- **Naming Conventions:** `{{NAMING_CONVENTIONS}}`
- **Smallest Complete Change:** Follow *First Make it Work -> Then Make it Right -> Follow Practice*; data shape before logic; hierarchy `(1) Not needed -> (2) Existing -> (3) Stdlib -> (4) Dependency -> (5) 1-liner -> (6) Minimal Diff -U1`; update 100% of callers, tests, fixtures, and configs; fix root causes instead of hiding crashes.
- **Progressive Disclosure & Token Budget:** Keep `AGENTS.md` $\le 24,000$ bytes (target `10–16 KB`); store universal rules here and in [.agents/rules/rules.md](./.agents/rules/rules.md) once without duplicating paragraphs into `agents/*.md` or `skills/*/SKILL.md` (each `SKILL.md` $\le 300$ lines).

## 4. Directory Map
- `AGENTS.md` — Root rule index and operational contract | `MANUAL_EN.md` — Complete English manual & onboarding guide | `MANUAL_TH.md` — Complete Thai manual & onboarding guide
- `{{SRC_DIR}}` — Application source code | `{{TEST_DIR}}` — Automated test suite
- `.agents/` — `agents/` (`4` Agents), `skills/` (`4` Skills), `rules/rules.md`, `hooks.json`, `scripts/` (`workflow_hooks.py`, `workflow_ops.py`, `verify_workflow.py`, `test_workflow_ops_and_hooks.py`), `workflows/` (`workflow.json`, `project_fanout.py`), `templates/` (MCP & Scheduled Automation examples), `ck/` (`context.json`, `CONTEXT.md`, `history/`)
- `artifacts/` — `Conversations/`, `user-requirements/`, `blueprints/`, `project-memory/`, `diffs/`, `reviews/` (plus event-driven `bug-reports/`, `solutions/`, `Lessons/`, `agent-confession/`)
- `backup/` — `backup/YYYYMMDDTHHMMSSffffffZ_<topic>/` + `manifest.json` (SHA-256, RFC 3339 UTC)

## 5. Read-Before-Touch & Lifecycle
0. **$O(1)$ Autonomous Rehydration:** On a new session or after `/compact`, read the top `3` lines of [artifacts/Conversations/README.md](./artifacts/Conversations/README.md) + [.agents/ck/context.json](./.agents/ck/context.json) ($t_0$) immediately (~250 tokens).
1. [.agents/rules/rules.md](./.agents/rules/rules.md) before modifying protected paths | 2. [project-tasks](./.agents/skills/project-tasks/SKILL.md) before starting project tasks | 3. [workflow-ops](./.agents/skills/workflow-ops/SKILL.md) for turn logging & checkpoints.

## 6. Hard Constraints (Don'ts)
1. Never commit hardcoded drive letters (e.g., `C:\`, `D:\`) or absolute local paths, and enforce UTF-8 without BOM (`BOM=False`); use relative paths only (except `file:///` links in chat).
2. Never create a new Git branch unless explicitly instructed.
3. Never edit protected source code (`{{PROTECTED_PATHS}}`), `AGENTS.md`, or `.agents/` before running Pre-Action Backup (`workflow_ops.py backup`) into `backup/YYYYMMDDTHHMMSSffffffZ_<topic>/` + `manifest.json`.
4. Never violate project-specific domain constraints: `{{DOMAIN_CONSTRAINTS}}`.
5. Never weaken or delete items on the Never Cut List: `{{NEVER_CUT_LIST}}` (Trust-Boundary Validation, Data-Integrity Error Handling, Security Controls, Automated Tests).
6. Never truncate code or specs with placeholders like `// ... existing code ...` — write 100% complete replacements.
7. Never read large files (`> 300` lines) whole — use search/grep + targeted line-range reads.
8. Never write, add, or edit production code or workflow architecture without completing all `4` steps: (1) summarize steps & target files, (2) check Conflict/Redundancy (config, data flow, params, schemas, cross-references — stop and report if found), (3) compare Pros/Cons only on divergent paths, (4) await `/approve` — except: (a) automatic logging in `artifacts/` and `.agents/ck/`, (b) trivial 1–2 line low-risk fixes with explicit target (still check Conflict/Redundancy + Backup), and (c) `Post-Approval Auto-Fix` strictly inside the approved scope with zero Conflict/Redundancy.
9. Never hide crashes with bare/broad catch-all `try-except` or dummy/mock values on owned code — fix the root cause and fail fast.
10. Never modify a shared contract, schema, API, or skill name without grepping and updating 100% of callers, tests, and cross-references.
11. Never fabricate test/audit results — run real commands, report exact commands + exit codes, and disclose `Untested/Unreviewed Scope` honestly.

## 7. Lean Agent Ecosystem (`4` Agents) & Auto-Effort Model Matrix
| Tier / Role | File | Primary Tier 2 Auto Swarm *(Pool C: Claude/GPT)* | Tier 1 YAML `model` & Escalation / Fallback |
|---|---|---|---|
| **Tier 0: In-line** | *(main chat)* | Main Chat UI Model | 1–2 line fixes / short Q&A ($\le 3$ reads) on warm KV cache |
| **👑 @lead** | [lead.md](./.agents/agents/lead.md) | `claude-opus-5-5-high` *(or `claude-sonnet-5-5-high`)* | `pro` • Triage, `/approve`, Exclusive Dispatcher, Evidence Closure (Fallback: `gemini-4-argon-high` / `gemini-4-neon-xhigh`) |
| **🏗️ @builder** | [builder.md](./.agents/agents/builder.md) | `claude-sonnet-5-5-medium` *(complex/core -> `high`)* | `flash` • Backup + Minimal Diff per approved plan + simplify (Fallback: `gemini-4-neon-medium` -> `high` / `hydrogen-medium`) |
| **🧪 @verifier** | [verifier.md](./.agents/agents/verifier.md) | `gpt-oss-120b-medium` *(RCA/critical diff -> `claude-sonnet-5-5-high`)* | `flash` • Read-Only Dynamic QA + Static Diff Audit (Fallback: `gemini-4-neon-low` -> `high` / `hydrogen-low`) |
| **🔎 @researcher** | [researcher.md](./.agents/agents/researcher.md) | `gpt-oss-120b-medium` *(deep cross-module -> `claude-sonnet-5-5-low`)* | `flash_lite` • Read-Only Codebase & Web Exploration (Fallback: `gemini-4-neon-low` / `hydrogen-low`) |

> **Quota Pools, Auto Effort, Tool Contract & Runtime Scope:**
> - **Pool Priority & Auto Effort:** Prefer **Pool C (Claude/GPT)** for Tier 2 `swarm` (`claude-opus-5-5-{low,medium,high}`, `claude-sonnet-5-5-{low,medium,high}`, `gpt-oss-120b-medium`) and **exhaust Pool C (`0%`) first** before falling back to **Pool B** (`gemini-4-argon-{low,medium,high}`) and **Pool A** (preferring **Gemini 4 Neon**: `gemini-4-neon-{low,medium,high,xhigh}` ahead of `gemini-4-hydrogen-*` and `gemini-3.8-flash-*`). Apply **Auto Effort** per role/task complexity on `swarm` `add` or `model` transitions; halt Auto-Swarm if active fallback pool quota `< 20%`.
> - **Tool Mapping & 10-Element Agent Schema:** `swarm` accepts explicit Model+Effort IDs (**never put `swarm` in YAML `tools:`**); Custom Subagents (`invoke_subagent`) accept only `inherit`, `flash_lite`, `flash`, or `pro`. Every `.agents/agents/*.md` file MUST include `name`, `description`, `tools` (non-empty valid registry tools), `subagent: true`, `mainAgent`, `model`, `commandExecutionPolicy` (`auto`/`sandbox`/`off`), `skills`, `# System Prompt`, and `# Review Guidelines`.
> - **Runtime Scope:** Main chat model cannot be switched programmatically (UI Dropdown only); model elevation applies on new worker spawns or phase transitions.

## 8. Modular Skills Directory (`4` Skills)
*(`/vibe`, `/design`, `/approve`, `/code`, `/simplify`, `/test`, `/debug`, `/audit`, `/finalize`, `/compound`, `/ck`, `/concept`, `/no-code`, `/no-detail`, `/more-detail` are Prompt Action Triggers in chat.)*
- **Project Tasks & Objectives:** [project-tasks](./.agents/skills/project-tasks/SKILL.md)
- **Plan, Build & Simplify:** [plan-and-build](./.agents/skills/plan-and-build/SKILL.md)
- **Verify, RCA & Compound Learning:** [verify-and-debug](./.agents/skills/verify-and-debug/SKILL.md)
- **Checkpoints, Logging & Self-Audit:** [workflow-ops](./.agents/skills/workflow-ops/SKILL.md)

## 9. Global System Directives (0–12)
0. **Logging & Checkpoint:** Record every completed turn in `artifacts/Conversations/YYYY-MM-DD/YYYYMMDD_conversations.md`, `README.md`, and `.agents/ck/context.json` via `workflow_ops.py log-turn`.
1. **Zero-Mock & Truthful:** Never mock owned code; confess real limits in `artifacts/agent-confession/`.
2. **Explain-First & Evidence-Based Objection:** On bottlenecks, bad commands, or conflict/redundancy, stop and object in `3` parts: **(1) conflicting/redundant evidence, (2) impact/risk, (3) valid alternatives**, while respecting `session-settled:` user decisions.
3. **Read-Only Audit Separation:** `@verifier` and `@researcher` never edit project files; `@verifier` reports defects back to `@lead` (never dispatches `@builder` directly).
4. **Boundaries, `/approve` & Backup:** Automatic writes are allowed only in `artifacts/` and `.agents/ck/` (plus `Post-Approval Auto-Fix` within the approved scope); code/workflow edits require Constraints `6.3` & `6.8`.
5. **4-Pillar Sync:** Update `user-requirements/`, `project-memory/` (ADR), `Conversations/`, and `backup/` in the same turn for architectural or feature changes.
6. **Mandatory Blueprint:** New features, modules, or workflow changes require a blueprint with stable `U-IDs` (`U1, U2...`) in `artifacts/blueprints/`.
7. **Proposal Bundling:** Merge compatible proposals into one cohesive plan; show Pros/Cons only for divergent paths.
8. **Relative Paths & Clean UTF-8:** Enforce `BOM=False`, relative paths only in committed files, and clean syntax via `verify_workflow.py`.
9. **Context Quota & Auto Compact:** Read `<= 300` lines; prune noisy logs; recommend `/compact` upon `<CONTEXT_SUMMARY>` or `10–12` turns (`~35` tool calls); restore in $O(1)$ from `.agents/ck/context.json` (checkpoint status NEVER equals `/approve`).
10. **Premise Check & Circuit Breaker ($N \ge 3$):** After `2` failures on the same premise, **Attack the Premise**; after `3` consecutive failures on the same root cause, halt immediately into Explain-First mode.
11. **Senior Dev & Compound Learning:** Minimal Diff `-U1`, 100% Callers, Never Cut List, and evaluate `/compound` (`Test/Lint -> Rule -> Solution Doc`) after closing non-trivial bugs.
12. **3-Tier Auto Triage Gate (`Tier 0–2` + `run_workflow`):**
    - **Tier 0 In-line:** 1–2 line edits, `<= 3` reads, or concise Q&A on warm cache.
    - **Tier 1 `invoke_subagent`:** Multi-file research (`@researcher`), long test/lint logs (`@verifier`), or `1–8` file edits (`@builder`).
    - **Tier 2 `swarm` / `run_workflow`:** `>= 9` modified files (excluding `artifacts/`/`.agents/ck/`) or `>= 2` disjoint workstreams use `swarm` (obeying the Dirty-Tree Rule in `.agents/rules/rules.md`); structured multi-file read/review fan-outs use `run_workflow` (see `.agents/workflows/project_fanout.py`); never edit code before `/approve`.
