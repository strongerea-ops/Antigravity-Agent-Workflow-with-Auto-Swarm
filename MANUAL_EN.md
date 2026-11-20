# System Manual & New Project Onboarding Guide (English Edition)

> **Thai Edition (คู่มือฉบับภาษาไทย):** [MANUAL_TH.md](./MANUAL_TH.md)  
> **Root Rule Index:** [AGENTS.md](./AGENTS.md) | **Extended Rules:** [.agents/rules/rules.md](./.agents/rules/rules.md)

## Table of Contents
1. [System Architecture & Functionality](#1-system-architecture--functionality)
2. [All Capabilities](#2-all-capabilities)
3. [All Available Commands](#3-all-available-commands)
4. [End-to-End Session Walkthrough](#4-end-to-end-session-walkthrough)
5. [New Project Onboarding Guide: Needs to Have • Needs to Prepare • Needs to Do](#5-new-project-onboarding-guide-needs-to-have--needs-to-prepare--needs-to-do)

---

## 1. System Architecture & Functionality

This workflow organizes AI-assisted engineering into **six cooperating layers** so agents stay fast, predictable, safe, and low-token across any codebase.

| Layer | File / Folder | Functionality |
|---|---|---|
| **1. Root Contract** | [AGENTS.md](./AGENTS.md) | Always-loaded rule index ($\le 24\text{ KB}$): language policy, commands, hard constraints, 4-role model matrix, and global directives `0–12`. |
| **2. Extended Rules** | [.agents/rules/rules.md](./.agents/rules/rules.md) | Non-redundant operational rules: high-blast-radius modules, dirty-tree `swarm` safety, `/approve` + `Post-Approval Auto-Fix`, and rollback semantics. |
| **3. Custom Agents (`4`)** | `.agents/agents/*.md` | 10-element role definitions (`@lead`, `@builder`, `@verifier`, `@researcher`) cleanly separating planning, editing, read-only auditing, and low-cost discovery. |
| **4. On-Demand Skills (`4`)** | `.agents/skills/*/SKILL.md` | Progressive-disclosure playbooks ($\le 300$ lines each) loaded **only** when triggered, preventing context bloat. |
| **5. Lifecycle Hooks & Stdlib CLI** | [.agents/hooks.json](./.agents/hooks.json), `.agents/scripts/*.py` | Zero-dependency Python 3.10+ automation executing at lifecycle events: startup checkpoint rehydration, pre-edit backup blocking, forbidden-command blocking, post-edit hygiene checks, diffs, and unit self-tests. |
| **6. Durable State & Opt-In Extensions** | `.agents/ck/`, `artifacts/`, `backup/`, `.agents/workflows/`, `.agents/templates/` | Rolling 15 checkpoints, 4-pillar archival vault, SHA-256 pre-action backups, dynamic `run_workflow` scripts, MCP templates, and scheduled cron automation templates. |

### Runtime-Enforced vs. Prompt-Governed Boundaries (100% Honest Disclosure)

| Mechanism | Enforcement Level | Actual Runtime Behavior |
|---|---|---|
| `AGENTS.md` `24,000`-byte cap & hierarchical discovery | **Antigravity Runtime (Hard)** | Truncated above 24 KB; walks up from any opened file to workspace root. |
| `SessionStart` checkpoint injection (`hooks.json`) | **Hook Script (Hard)** | Runs `scripts/workflow_hooks.py session-start` with CWD = `.agents/` and injects a $t_0$ pointer whenever `.agents/ck/context.json` exists. |
| `PreToolUse` backup & forbidden-command guard | **Hook Script (Hard)** | Deterministically returns `decision: "deny"` before `edit_file`/`write_file` if today's backup manifest is missing, or before `run_command` matching configured forbidden regexes. |
| `PostToolUse` workflow audit (`last_alert.log`) | **Hook Script (Hard)** | Runs `verify_workflow.audit_workspace()` after editing workflow files; writes or removes `.agents/ck/last_alert.log`. |
| `Stop` alert gate (`alert-stop-gate`, opt-in) | **Hook Script (Hard when enabled)** | Disabled by default (`"enabled": false`); checks `continuationActive` to prevent infinite retry loops. |
| `verify_workflow.py` & `test_workflow_ops_and_hooks.py` | **CLI Tool (Hard)** | Deterministic exit code `0` / `1` on schemas, links, UTF-8 BOM, syntax, and hook behavior. |
| `/approve` gate, `no-code / no-detail` default, Circuit Breaker ($N \ge 3$), `Post-Approval Auto-Fix` | **Prompt-Governed Policy** | Enforced via `AGENTS.md`, `rules.md`, and role prompts; reinforced by human review. |
| Main chat UI model, thinking budget & opening a new window | **UI-Only Control** | Cannot be switched or opened programmatically; use UI dropdown / `New Conversation` (while `/handoff` automates packet creation and `SessionStart` pickup). |

---

## 2. All Capabilities

1. **Language Split for Token Conservation:** System docs (`AGENTS.md`, `.agents/`) and internal thinking remain in **English** to minimize token usage, while user conversations and `artifacts/` records adapt to `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` (e.g., `Thai` or `English`).
2. **Default `no-code / no-detail` Interaction + Smart Detail Expansion:** General Q&A and status checks return `3–5` concise principle-first bullets without code snippets or untouched file lists. Full technical detail activates automatically during **planning** (pre-`/approve`), **code implementation** (3-part summary + modified file links + `.diff`), or on `/more-detail`.
3. **Progressive Disclosure, `/compact` & New-Window `/handoff`:** Skills load on demand; large file reads stay sliced (`<= 300` lines); upon `10–12` turns (`~35` calls) or `<CONTEXT_SUMMARY>`, `@lead` offers **`/compact`** (continue in this window) or **`/handoff`** (generate `.agents/ck/HANDOFF.md` + `artifacts/handoffs/` + ready-to-paste prompt for a fresh chat window automatically detected by `SessionStart`); $O(1)$ rehydration (~250 tokens) reads `Conversations/README.md` + `.agents/ck/context.json`.
4. **3-Tier Auto Triage + Quota Pool Priority + Auto Effort:**
   - **Tier 0 In-line:** 1–2 line fixes or quick Q&A (`<= 3` reads) on warm cache.
   - **Tier 1 `invoke_subagent`:** Scoped tasks (`@researcher`, `@builder`, `@verifier`) or `1–8` file edits.
   - **Tier 2 `swarm` / `run_workflow`:** `>= 9` modified files or `>= 2` disjoint workstreams use `swarm`; structured multi-file read/review fan-outs use `run_workflow`.
   - Tier 2 `swarm` exhausts **Pool C (Claude/GPT)** to `0%` first before falling back to **Pool B (`gemini-4-argon-*`)** and **Pool A (`gemini-4-neon-*` preferred)**, applying Auto Effort per role/complexity and halting Auto-Swarm below `20%` fallback quota.
5. **Dirty Working Tree Swarm Safety:** Whenever uncommitted local changes exist, **never** use `workspace:"share"` (git worktrees check out `HEAD` and omit uncommitted edits); use `workspace:"inherit"` with strictly disjoint file ownership plus a consolidated Pre-Action Backup instead.
6. **6-Event Lifecycle Hooks (CWD = `.agents/`):** Pre-wired for `SessionStart`, `PreToolUse` (`edit_file|write_file` + `run_command`), `PostToolUse`, and opt-in `Stop` (`continuationActive` guard) in [.agents/hooks.json](./.agents/hooks.json), and extensible with `PreInvocation` / `PostInvocation`.
7. **Dynamic Python Workflows (`run_workflow`):** Includes [.agents/workflows/project_fanout.py](./.agents/workflows/project_fanout.py) + [.agents/workflows/workflow.json](./.agents/workflows/workflow.json) using `phase`, `agent`, `parallel`, `log`, JSON `schema` enforcement, and `Args` schema validation.
8. **Git-Optional Pre-Action Backup, `-U1` Diff & Rollback:** `workflow_ops.py backup` snapshots existing files with `SHA-256` and records newly created files as `"status": "absent"`; `workflow_ops.py diff` produces unified `-U1` diffs against the manifest even without `.git`.
9. **Quality & Compound Learning Safeguards:** 4-step `/approve` gate, Read-Only `@verifier` separation, 3-part `Evidence-Based Objection`, `session-settled:` lock, `Attack the Premise` ($N=2$), `Circuit Breaker` ($N \ge 3$), and `Compound Learning` (`Test/Lint -> Rule -> Solution Doc`).
10. **Opt-In MCP & Scheduled Automations:** Ready-to-adapt templates for **MCP** (Stdio + Streamable HTTP `/mcp`; legacy SSE unsupported) in [.agents/templates/mcp_config.example.json](./.agents/templates/mcp_config.example.json) and **Scheduled Cron Sidecars** (`"builtin": "schedule"`, `CRON_TZ`, `restart_policy: "always"`) in [.agents/templates/sidecar.schedule.example.json](./.agents/templates/sidecar.schedule.example.json).

---

## 3. All Available Commands

### A. Native Antigravity Slash Commands
*(Typed directly in the Antigravity chat input)*

| Command | Purpose |
|---|---|
| `/plan` | Enter structured step-by-step planning before execution. |
| `/compact` | Summarize and compact long conversation context to free token budget (recommended at 10–12 turns). |
| `/goal` | Run a thorough, long-running task continuously until the goal is achieved. |
| `/schedule` | Set a one-time delayed timer or recurring in-session schedule. |
| `/automation` | Interactive wizard to create a persistent cron background sidecar automation. |
| `/browser` | Delegate live web browsing, UI inspection, or web-app actions to the browser subagent. |
| `/grill-me` | Interactive interview to clarify ambiguous requirements and align on design decisions. |
| `/teamwork` | Coordinate a multi-agent team / swarm for large parallel projects. |
| `/learn` | Persist a correction or solved setup pattern for future tasks. |
| `/boost` | Deep thinking, multi-perspective planning, and rigorous verification for complex tasks. |
| `/plugin` | Manage, enable, disable, or package customizations into a plugin bundle. |

### B. Workflow Prompt Action Triggers (Chat)
*(Governed by `AGENTS.md` and `.agents/skills/`)*

| Trigger | Skill / Owner | Behavior |
|---|---|---|
| `/vibe <goal>` | `plan-and-build` (`@lead`) | Start the full proportional lifecycle (Triage -> Plan -> `/approve` -> Build -> Verify -> Close). |
| `/design <topic>` | `plan-and-build` (`@lead`) | Produce a blueprint (`artifacts/blueprints/` with `U-IDs`, conflict check, rollback, and options) without editing source code. |
| `/approve [Option]` | `plan-and-build` (`@lead`) | Authorize `@builder` to implement the approved blueprint scope (`U-IDs`). |
| `/code` | `plan-and-build` (`@builder`) | Execute Pre-Action Backup + Minimal Diff implementation strictly inside approved scope. |
| `/simplify` | `plan-and-build` (`@builder`) | Refine recent edits through 5 lenses (Reuse, Quality, Efficiency, Test Value, Comments) preserving 100% behavior and tests. |
| `/test` | `verify-and-debug` (`@verifier`) | Run real test/lint commands and report exact commands, exit codes, verdicts, and `Untested Scope`. |
| `/debug <issue>` | `verify-and-debug` (`@verifier`) | Run Causal-Chain RCA (`Hypothesis -> Prediction -> Check`), `Attack the Premise` ($N=2$), and Circuit Breaker ($N \ge 3$). |
| `/audit` | `verify-and-debug` (`@verifier`) | Perform Read-Only static diff inspection, 100% caller tracing, and Never Cut List verification. |
| `/finalize` | `plan-and-build` (`@lead`) | Run Acceptance Evidence Closure, generate `.diff`, evaluate `/compound`, and log the turn. |
| `/compound` | `verify-and-debug` (`@lead`) | Convert solved non-trivial issues into permanent guards (`Test/Lint -> Rule -> Solution Doc`). |
| `/ck` | `workflow-ops` (`@lead`) | Save or inspect Rolling 15 Checkpoints (`.agents/ck/context.json` & `CONTEXT.md`). |
| `/handoff` | `workflow-ops` (`@lead`) | Paired with `/compact` alerts: generate `.agents/ck/HANDOFF.md`, archive under `artifacts/handoffs/`, mark `HANDOFF_READY` for `SessionStart` pickup, and output a Ready-to-Paste Starter Prompt for a fresh chat window. |
| `/concept`, `/no-code`, `/no-detail` | `AGENTS.md` §0 (`@lead`) | Force concise `3–5` bullet principle/behavior explanation with zero code snippets or untouched file lists. |
| `/more-detail` | `AGENTS.md` §0 (`@lead`) | Expand into full file paths, line numbers, code/config details, and full command outputs. |
| `/refactor-agents` | `workflow-ops` (`@lead`) | Audit and streamline `AGENTS.md` and `.agents/` while keeping byte budgets and schemas valid. |

### C. Agent Role Mentions (`@role`)

| Role | Tier 1 Model | File Writes | Shell Policy | Best Used For |
|---|---|---|---|---|
| `@lead` | `pro` | Yes (Orchestrator) | `auto` | Triage, planning, conflict checks, `/approve`, and closure. |
| `@builder` | `flash` | Yes (Approved Scope) | `auto` | Executing approved `U-ID` edits with backup & minimal diff. |
| `@verifier` | `flash` | **No (Read-Only)** | `sandbox` | Running real tests, RCA debugging, and static diff auditing. |
| `@researcher` | `flash_lite` | **No (Read-Only)** | `off` | Cheap codebase mapping, caller lookup, and official doc searches. |

### D. Bundled Python CLI Commands
*(Run from project root; replace `python` with `python3` on Linux/macOS if needed)*

| Command | Purpose |
|---|---|
| `python .agents/scripts/workflow_ops.py check-placeholders` | List every unfilled `{{PLACEHOLDER}}` across active workflow files with file:line locations. |
| `python .agents/scripts/workflow_ops.py check-placeholders --fail-on-found` | Same scan, returning `Exit 1` if any placeholder remains (readiness/CI gate). |
| `python .agents/scripts/workflow_ops.py backup --topic "<slug>" <files...>` | Create microsecond Pre-Action Backup + SHA-256 `manifest.json` under `backup/`. |
| `python .agents/scripts/workflow_ops.py diff --output "artifacts/diffs/YYYY-MM-DD/<slug>.diff"` | Generate unified `-U1` diff against the latest backup manifest (works without `.git`). |
| `python .agents/scripts/workflow_ops.py log-turn --title "<t>" --summary "<s>"` | Append to daily `artifacts/Conversations/`, update `README.md`, and rotate Rolling 15 Checkpoints. |
| `python .agents/scripts/workflow_ops.py handoff --objective "<obj>"` | Generate a new-window handoff packet (`.agents/ck/HANDOFF.md` + `artifacts/handoffs/`), set `HANDOFF_READY` for `SessionStart`, and output a starter prompt. |
| `python .agents/scripts/verify_workflow.py` | Self-audit `AGENTS.md`, 4 Agents, 4 Skills, `hooks.json`, scripts, `run_workflow` syntax, templates, links, and BOM (`Exit 0`). |
| `python .agents/scripts/verify_workflow.py --root "<path>"` | Audit another project's workflow from outside its directory. |
| `python -m unittest discover -s .agents/scripts -p "test_*.py" -v` | Run deterministic self-tests for hooks, backup, diff, checkpoints, placeholder scanner, and verifier. |
| `python .agents/scripts/workflow_hooks.py <session-start\|pre-tool\|post-tool\|stop>` | Hook handler invoked automatically by `.agents/hooks.json` (accepts camelCase JSON on stdin). |

### E. Project Placeholder Commands (Filled in `AGENTS.md`)

| Placeholder | Fill With |
|---|---|
| `{{INSTALL_COMMAND}}` | Dependency install command (e.g., `pip install -r requirements.txt`, `npm ci`). |
| `{{RUN_COMMAND}}` | Local dev/server launch command (e.g., `npm run dev`, `python main.py`). |
| `{{BUILD_COMMAND}}` | Compile/bundle command (e.g., `npm run build`, or `N/A` if no build step). |
| `{{TEST_COMMAND}}` | Authoritative test suite command (e.g., `python -m unittest discover -s tests`, `npm test`). |
| `{{LINT_COMMAND}}` | Static linter/typecheck command (e.g., `ruff check .`, `npm run lint`). |

---

## 4. End-to-End Session Walkthrough

1. **Start Session:** `SessionStart` hook injects the latest checkpoint from `.agents/ck/context.json`; `@lead` reads the top `3` lines of `artifacts/Conversations/README.md` ($O(1)$ rehydration).
2. **Request Work:** User types `/vibe <task>` (or asks a general question which `@lead` answers in `3–5` concise `no-code / no-detail` bullets).
3. **Plan & Gate:** `@lead` (with `@researcher` when needed) inspects real files, checks Conflict/Redundancy, writes a blueprint (`U1, U2...`), compares Pros/Cons only on divergent paths, and awaits `/approve`.
4. **Backup & Build:** After `/approve`, `@builder` runs `workflow_ops.py backup`, applies Minimal Diff `-U1` edits (`PreToolUse` enforces backup; `PostToolUse` verifies workflow hygiene), and runs `/simplify`.
5. **Verify & Audit:** `@verifier` runs real tests (`{{TEST_COMMAND}}`) and static diff audit in Read-Only mode. For strictly in-scope defects, `@lead` may dispatch `Post-Approval Auto-Fix` (halting at Circuit Breaker $N \ge 3$).
6. **Close & Archive:** `@lead` verifies Acceptance Criteria item by item, writes unified `.diff`, evaluates `/compound`, runs `workflow_ops.py log-turn`, and reports *(1) What happened, (2) What was fixed, (3) Next steps* with clickable file links.

---

## 5. New Project Onboarding Guide: Needs to Have • Needs to Prepare • Needs to Do

### 5.1 What a New Project NEEDS TO HAVE (Prerequisites)

| Requirement | Status | Details |
|---|---|---|
| **1. Antigravity Runtime** | **Required** | Antigravity 2.0 desktop app, Antigravity IDE, or Antigravity CLI (`agy`) supporting `AGENTS.md` and `.agents/` discovery. |
| **2. Python 3.10+** | **Required** | Standard Python 3.10+ on `PATH` (`python` on Windows; `python3` on macOS/Linux). **Zero third-party packages** are needed — all workflow scripts use pure Python stdlib. |
| **3. Clear Project Layout** | **Required** | A project root directory separating application source (`{{SRC_DIR}}`) and tests (`{{TEST_DIR}}`) from `.agents/`, `artifacts/`, and `backup/`. |
| **4. Real Test / Lint Command** | **Recommended** | At least one runnable command (`{{TEST_COMMAND}}` / `{{LINT_COMMAND}}`) so `@verifier` can enforce real verification. |
| **5. Git + `.gitignore`** | **Optional** | Recommended for `git status` and `git diff -U1`, though `workflow_ops.py backup` + `diff` works without Git. Add `backup/`, `.agents/ck/last_alert.log`, `.env`, and build/cache dirs to `.gitignore`. |

### 5.2 What a New Project NEEDS TO PREPARE (Complete `33`-Placeholder Checklist)

Gather the decisions below before setup. Every entry maps 1-to-1 with the **`33` exact `{{PLACEHOLDERS}}`** scanned by `python .agents/scripts/workflow_ops.py check-placeholders`.

#### Group 1 — Identity & Language Policy (`3` placeholders)
| Placeholder | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{PROJECT_NAME}}` | Official project name | `Acme Billing API` | `AGENTS.md`, `rules.md`, `lead.md`, `verifier.md`, `project-tasks`, `context.json`, templates |
| `{{PROJECT_OBJECTIVE}}` | 1–2 sentence core mission and target outcome | `Build a fault-tolerant invoice API with strict idempotency` | `AGENTS.md`, `project-tasks`, `project_fanout.py` |
| `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` | Language for chat replies & `artifacts/` logs (system docs stay English) | `Thai` or `English` | `AGENTS.md`, `lead.md`, `workflow-ops`, `artifacts/README.md` |

#### Group 2 — Stack, Paths & Blast Radius (`6` placeholders)
| Placeholder | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{TECH_STACK}}` | Languages, frameworks, databases, runtimes | `Python 3.12, FastAPI, PostgreSQL, React 19` | `AGENTS.md`, `project-tasks` |
| `{{SRC_DIR}}` | Main application source folder *(activates `PreToolUse` source backup guard in `workflow_hooks.py` once filled)* | `src/` | `AGENTS.md`, `project-tasks`, `workflow_hooks.py` |
| `{{TEST_DIR}}` | Automated test directory | `tests/` | `AGENTS.md`, `project-tasks` |
| `{{PROTECTED_PATHS}}` | Paths requiring backup + `/approve` before editing | `src/, config/, AGENTS.md, .agents/` | `AGENTS.md`, `rules.md` |
| `{{HIGH_BLAST_RADIUS_MODULES}}` | Critical shared files with system-wide impact | `src/config.py, src/auth/jwt.py, src/db/schema.sql` | `rules.md`, `project-tasks` |
| `{{NAMING_CONVENTIONS}}` | File, class, and symbol naming standards | `Python snake_case/PascalCase; TS camelCase/PascalCase` | `AGENTS.md` |

#### Group 3 — Exact Project Commands (`5` placeholders)
| Placeholder | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{INSTALL_COMMAND}}` | Dependency install command | `pip install -r requirements.txt` or `npm ci` | `AGENTS.md`, `project-tasks` |
| `{{RUN_COMMAND}}` | Local app/server run command | `uvicorn src.main:app --reload` or `npm run dev` | `AGENTS.md`, `project-tasks` |
| `{{BUILD_COMMAND}}` | Compile/bundle command (or `N/A`) | `npm run build` or `N/A` | `AGENTS.md`, `builder.md`, `project-tasks` |
| `{{TEST_COMMAND}}` | Authoritative test suite command | `python -m unittest discover -s tests` or `npm test` | `AGENTS.md`, `verifier.md`, `project-tasks`, `verify-and-debug` |
| `{{LINT_COMMAND}}` | Linter / typecheck command | `ruff check .` or `npm run lint` | `AGENTS.md`, `builder.md`, `verifier.md`, `project-tasks`, `verify-and-debug` |

#### Group 4 — Core Project Tasks & Acceptance Criteria (`9` placeholders)
| Placeholder Group | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{TASK_1_NAME}}`, `{{TASK_1_OBJECTIVE}}`, `{{TASK_1_ACCEPTANCE}}` | Priority 1 deliverable, goal, and measurable pass condition | `Auth API` / `Add JWT login` / `All 12 auth tests pass + 401 on invalid token` | `AGENTS.md`, `project-tasks` |
| `{{TASK_2_NAME}}`, `{{TASK_2_OBJECTIVE}}`, `{{TASK_2_ACCEPTANCE}}` | Priority 2 deliverable, goal, and pass condition | `Billing Webhook` / `Idempotent retries` / `Duplicate webhook IDs never double-charge` | `AGENTS.md`, `project-tasks` |
| `{{TASK_3_NAME}}`, `{{TASK_3_OBJECTIVE}}`, `{{TASK_3_ACCEPTANCE}}` | Priority 3 deliverable, goal, and pass condition (add more freely) | `Observability` / `Structured JSON logs` / `Zero unhandled exceptions in smoke run` | `AGENTS.md`, `project-tasks` |

#### Group 5 — Safety Constraints & Hook Policy (`3` placeholders)
| Placeholder | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{DOMAIN_CONSTRAINTS}}` | Project-specific technical or business hard don'ts | `Never call live payment gateways in tests; no blocking I/O on async event loop` | `AGENTS.md`, `rules.md`, `project-tasks` |
| `{{NEVER_CUT_LIST}}` | Protections agents must never delete or weaken | `Input validation, Auth middleware, DB transaction guards, Existing tests` | `AGENTS.md`, `rules.md`, `verifier.md`, `project-tasks`, `verify-and-debug` |
| `{{FORBIDDEN_COMMAND_REGEX}}` | Optional regex blocked by `PreToolUse` on `run_command` (set `""` if unused; unfilled placeholder is safely ignored) | `\brm\s+-rf\s+/` or `\bpytest\s+core_pkg\b` | `.agents/scripts/workflow_hooks.py` |

#### Group 6 — Optional Advanced Templates (`7` placeholders)
| Placeholder | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{WORKFLOW_TARGET_GLOB}}` | Default relative glob for dynamic `run_workflow` parallel review | `src/**/*.py` | `.agents/workflows/project_fanout.py` |
| `{{MCP_SERVER_NAME}}`, `{{MCP_STDIO_COMMAND}}`, `{{MCP_HTTP_URL}}` | Local Stdio binary or remote Streamable HTTP (`/mcp`) endpoint (legacy SSE unsupported) | `db-tools`, `sqlite-mcp-server`, `https://mcp.example.com/mcp` | `.agents/templates/mcp_config.example.json` |
| `{{IANA_TIMEZONE}}`, `{{SCHEDULE_CRON}}`, `{{SCHEDULE_TASK_PROMPT}}` | IANA timezone (never raw offsets like `+07:00`), 5-field cron, and self-contained scheduled prompt | `Asia/Bangkok`, `0 9 * * 1-5`, `Run test suite and summarize failures` | `.agents/templates/sidecar.schedule.example.json` |

### 5.3 What a New Project NEEDS TO DO (Step-by-Step Setup)

1. **Copy Workflow Into Your Project Root:** Copy `AGENTS.md`, `MANUAL_EN.md` (and/or `MANUAL_TH.md`), `.agents/`, and `artifacts/` directly into the root directory of your new project. Do not nest it inside another workspace that already has an `AGENTS.md` (hierarchical discovery stacks both). Add `backup/` and `.agents/ck/last_alert.log` to `.gitignore`.
2. **Verify Python Alias:** Confirm `python --version` (`3.10+`). On Linux/macOS where only `python3` exists, update `"python scripts/workflow_hooks.py ..."` in [.agents/hooks.json](./.agents/hooks.json) to `"python3 scripts/workflow_hooks.py ..."` — keep `scripts/workflow_hooks.py` relative to `.agents/` because Antigravity executes hooks with **CWD = `.agents/`**.
3. **Scan and Fill All Placeholders:**
   ```bash
   python .agents/scripts/workflow_ops.py check-placeholders
   ```
   Populate [AGENTS.md](./AGENTS.md), [.agents/rules/rules.md](./.agents/rules/rules.md), [.agents/skills/project-tasks/SKILL.md](./.agents/skills/project-tasks/SKILL.md), the agent/skill command references, [.agents/scripts/workflow_hooks.py](./.agents/scripts/workflow_hooks.py), [.agents/ck/context.json](./.agents/ck/context.json), and [artifacts/README.md](./artifacts/README.md). Copy `.agents/templates/*` to `~/.gemini/config/` only when enabling MCP or scheduled sidecars (or delete unused template files so `--fail-on-found` passes `Exit 0`).
4. **Run Verification Gate (Must Exit `0`):**
   ```bash
   python .agents/scripts/workflow_ops.py check-placeholders --fail-on-found
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. **Optional Hook Tuning:** To prevent finishing a turn while `.agents/ck/last_alert.log` contains an unresolved audit alert, change `"enabled": false` to `true` on `"alert-stop-gate"` inside [.agents/hooks.json](./.agents/hooks.json).
6. **Run First-Session Smoke Test:**
   - Open your project in a fresh Antigravity session and confirm `SessionStart` loads cleanly with zero errors.
   - Ask *"Summarize this project's architecture and rules"* to verify default concise `no-code / no-detail` responses in `{{CHAT_AND_ARTIFACTS_LANGUAGE}}`.
   - Execute one small Task 1 item through `/vibe` -> `/approve` -> `/finalize`, confirming backup manifest, real test logs, unified `.diff`, and updated `artifacts/Conversations/` + `.agents/ck/context.json`.
7. **Scaling Up as Your Project Grows:** Start lean with the `4` core agents (`lead`, `builder`, `verifier`, `researcher`) and add roles only when a real bottleneck emerges:
   - Add **`@architect`** (`pro`) when designs regularly span multiple services or schemas.
   - Split **`@verifier`** into **`@tester`** (dynamic QA) + **`@reviewer`** (static diff) + **`@code-skeptic`** (proof gatekeeper) as PR volume grows.
   - Add **`@risk-guardian`** (`pro`, Read-Only Veto) for financial, auth, security, or compliance-critical projects.
   - Whenever adding `.agents/agents/<name>.md` (following the 10-element schema), update the agent table and count in `AGENTS.md` and re-run `python .agents/scripts/verify_workflow.py` (`Exit 0`).
