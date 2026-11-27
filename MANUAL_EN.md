# System Manual & Beginner-Friendly Onboarding Guide (English Edition)

> **Thai Edition (คู่มือฉบับภาษาไทย):** [MANUAL_TH.md](./MANUAL_TH.md)  
> **Master Rulebook:** [AGENTS.md](./AGENTS.md) | **Task-Based Rules:** [.agents/rules/rules.md](./.agents/rules/rules.md)

## Table of Contents
1. [Plain-English Overview, Mini Glossary & How the System Works](#1-plain-english-overview-mini-glossary--how-the-system-works)
2. [All Capabilities (And Clickable Menus)](#2-all-capabilities-and-clickable-menus)
3. [Commands Guide: Goal-to-Command Cheat Sheet & Full Reference](#3-commands-guide-goal-to-command-cheat-sheet--full-reference)
4. [What a Real Session Looks Like (Step-by-Step)](#4-what-a-real-session-looks-like-step-by-step)
5. [New Project Setup Guide: Needs to Have • Needs to Prepare • Needs to Do](#5-new-project-setup-guide-needs-to-have--needs-to-prepare--needs-to-do)

---

## 1. Plain-English Overview, Mini Glossary & How the System Works

You do **not** need a programming background to use this workflow. It turns your AI assistant in Antigravity into an organized, safety-first team that explains things clearly, offers clickable menus instead of making you memorize commands, saves backups before editing, and verifies every change.

### Mini Glossary (Everyday Meanings)

| Term | Plain-English Meaning |
|---|---|
| **Agent (`@lead`, `@builder`, etc.)** | A specialized AI role with clear boundaries — e.g., the planner makes plans, the builder edits files, and the checker only reads and tests. |
| **Skill** | A step-by-step playbook opened only when needed so the AI's memory stays light and fast. |
| **Hook** | An automatic background guard that runs at key moments (opening a chat, before saving a file, after saving a file) to enforce backups and catch mistakes. |
| **Checkpoint** | A short progress snapshot saved automatically after each turn (keeps the latest `15`) so a new chat remembers where you left off in seconds. |
| **Pre-Action Backup (`<= 30` days)** | A safety copy of files saved inside `backup/` before the AI edits them (backups older than `30` days are auto-pruned; `artifacts/` are never auto-deleted). |
| **`rollback` / `prune` / `inspect`** | Built-in CLI helpers in `workflow_ops.py`: `rollback` restores files with `SHA-256` checks (dry-run by default), `prune` cleans expired `backup/` folders (`> 30` days), and `inspect` runs all health gates in one command. |
| **Diff (`.diff` file)** | A clean before-and-after record showing only the lines that changed. |
| **Placeholder (`{{LIKE_THIS}}`)** | A fill-in-the-blank label where you put your own project's name, folders, or commands. |
| **`/handoff` vs. `/compact`** | Two ways to handle a long chat: **`/handoff`** packs everything neatly for a brand-new chat window; **`/compact`** is a built-in Antigravity command (type `/compact` and press `Enter`) to shrink old messages in the current window. |

### The 6 Building Blocks

| Layer | File / Folder | What It Does (In Plain Words) |
|---|---|---|
| **1. Master Rulebook** | [AGENTS.md](./AGENTS.md) | Always-loaded rule summary ($\le 24\text{ KB}$): language setup, main commands, strict don'ts, 4-role team chart, and core habits (`0–12`). |
| **2. Task-Based Rules (`4` files)** | [.agents/rules/rules.md](./.agents/rules/rules.md) | Smart index sending the AI to only the rule file that matches the current task (`coding-and-safety.md`, `commands-and-tools.md`, `agents-and-handoff.md`). |
| **3. AI Team (`4` Roles)** | `.agents/agents/*.md` | Clean role boundaries (`@lead`, `@builder`, `@verifier`, `@researcher`) separating planning, editing, read-only testing, and low-cost research. |
| **4. On-Demand Playbooks (`4` Skills)** | `.agents/skills/*/SKILL.md` | Short step-by-step guides ($\le 300$ lines each) loaded **only** when triggered. |
| **5. Automatic Guards & Helper CLI** | [.agents/hooks.json](./.agents/hooks.json), `.agents/scripts/*.py` | Zero-install Python `3.10+` scripts that prompt first-time language choice, block edits without a backup, check workflow health, generate diffs, and self-test. |
| **6. Memory, Vault & Optional Add-Ons** | `.agents/ck/`, `artifacts/`, `backup/`, `.agents/workflows/`, `.agents/templates/` | Rolling `15` checkpoints, organized project archive, backups, plus optional multi-file scripts, MCP servers, and scheduled background tasks. |

### What Is Enforced Automatically vs. Guided by Rules (100% Honest Disclosure)

| Mechanism | Enforcement Level | Actual Runtime Behavior |
|---|---|---|
| `AGENTS.md` `24,000`-byte cap & folder discovery | **Antigravity App (Automatic)** | Truncated above 24 KB; Antigravity walks up from opened files to the workspace root. |
| `SessionStart` language check, memory & bug check (`hooks.json`) | **Hook Script (Automatic)** | Runs `scripts/workflow_hooks.py session-start` (with working folder `.agents/`) to spot unfilled `{{CHAT_AND_ARTIFACTS_LANGUAGE}}`, load the latest checkpoint/handoff pointer, and remind you about unresolved `3–7` day bug reports. |
| `PreToolUse` backup, Git & `artifacts/` guard | **Hook Script (Automatic)** | Blocks `edit_file`/`write_file` if today's backup is missing, blocks unauthorized Git branch creation (`checkout -b`, `switch -c`, `branch <name>`), blocks destructive Git (`reset --hard`, `clean -f`, `checkout -- .`), blocks commands that delete `artifacts/`, and evaluates custom forbidden patterns. |
| `PostToolUse` workflow health check (`last_alert.log`) | **Hook Script (Automatic)** | Runs `verify_workflow.audit_workspace()` after editing workflow files; writes or clears `.agents/ck/last_alert.log`. |
| `Stop` alert gate (`alert-stop-gate`, opt-in) | **Hook Script (Automatic when enabled)** | Off by default (`"enabled": false`); safely stops after one retry check (`continuationActive`) to prevent loops. |
| `verify_workflow.py` & `test_workflow_ops_and_hooks.py` | **CLI Tool (Automatic)** | Returns exact `Exit 0` (pass) or `Exit 1` (fail) for schemas, links, file encoding, syntax, and hook behavior. |
| `/approve` menus, plain-language default, Circuit Breaker ($N \ge 3$), `Post-Approval Auto-Fix` | **AI Rule Policy** | Followed by the AI via `AGENTS.md` and role prompts, reinforced by your approval clicks. |
| Main chat model selector, thinking level, opening a new chat window & typing native slash commands (`/compact`, `/plan`, etc.) | **App UI Only** | The AI cannot click app buttons or run Antigravity's native slash commands for you — it gives clickable menus to confirm your choice, runs workflow commands immediately, and tells you when to type a native slash command or click `New Conversation`. |

---

## 2. All Capabilities (And Clickable Menus)

1. **First-Time Language Picker & Plain-Language Replies:** On your first session (while `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` is still blank), `SessionStart` triggers a clickable `ask_question` menu to pick your language and applies it with `workflow_ops.py set-language --lang "<Language>"` (saving a backup first). System rules stay in English behind the scenes to save tokens, while replies use simple, everyday words in your chosen language.
2. **Clickable Menus Everywhere Decisions Happen (`ask_question`):** You do not have to memorize syntax — the assistant presents clickable menus for:
   - **First-time language selection**
   - **Plan approval (`/approve`) and multi-option comparisons (`Option A` / `Option B`)**
   - **Long-chat memory choices (`/handoff` vs. `/compact` vs. continue as-is)**
   - **Recommended next commands** (e.g., `/vibe`, `/design`, `/test`, `/debug`, `/more-detail`, or native commands like `/plan` and `/grill-me`) — clearly distinguishing workflow commands that run right after clicking from native UI commands you type in chat.
3. **Short Answers by Default, Full Detail When Needed:** General questions return `3–5` plain bullets (`no-code / no-detail`) with no overwhelming code dumps. Full detail turns on automatically during planning, editing code, or when you ask for `/more-detail`. Pre-decision analyses close with a clear **Action Recommendation Verdict** (whether you should proceed and why).
4. **Long-Chat Protection (`/compact` + `/handoff` + Fast Startup):** Skills load only when needed and large files are read in slices (`<= 300` lines). At `10–12` turns (`~35` calls) or `<CONTEXT_SUMMARY>`, a clickable menu lets you pick **`/handoff`** (creates `.agents/ck/HANDOFF.md` + `artifacts/handoffs/` + ready-to-paste prompt for a fresh window automatically picked up by `SessionStart`) or **`/compact`** (shrinks the current window).
5. **Smart 3-Level Sizing + Auto-Swarm Safety:**
   - **Tier 0 In-line:** Tiny 1–2 line fixes or quick questions (`<= 3` reads) finish right in chat.
   - **Tier 1 `invoke_subagent`:** Focused tasks (`@researcher`, `@builder`, `@verifier`) or `1–8` edited files.
   - **Tier 2 `swarm` / `run_workflow`:** `>= 9` edited files or `>= 2` separate workstreams scale to a team (`Pool C` Claude/GPT to `0%` first → `Pool B` `gemini-4-argon-*` → `Pool A` `gemini-4-neon-*`, halting Auto-Swarm below `20%` fallback quota). On dirty Git working trees (unsaved local changes), workers strictly use `workspace:"inherit"` with non-overlapping files so uncommitted work is never lost.
6. **Clean Code Hygiene, Safe Retention & Permanent Learning:** Pre-Action Backup (auto-pruned after `30` days) + `SHA-256` verified `rollback` + `-U1` Diff (works even without Git) + unified `inspect` gates; `artifacts/` are user-managed reference materials (**never auto-deleted**, protected by `PreToolUse` hook — if an artifact conflicts with current rules, the assistant alerts you with options); temporary one-off scripts live in Antigravity's built-in session `scratch/` folder (not workspace `artifacts/scratch/`) while reusable scripts live in `artifacts/tools/`; Read-Only `@verifier`, Self-Mistake Governance, Zero In-Code Comments (`artifacts/comments/`), `3–7` day unresolved bug reminders, 3-part Evidence-Based Objection, Attack the Premise ($N=2$), Circuit Breaker ($N \ge 3$), and Compound Learning (`/compound`).
7. **Optional Power Add-Ons:** Ready-to-adapt parallel Python workflow ([project_fanout.py](./.agents/workflows/project_fanout.py) + [workflow.json](./.agents/workflows/workflow.json)), MCP server example ([mcp_config.example.json](./.agents/templates/mcp_config.example.json)), and scheduled background cron example ([sidecar.schedule.example.json](./.agents/templates/sidecar.schedule.example.json)).

---

## 3. Commands Guide: Goal-to-Command Cheat Sheet & Full Reference

### Quick Cheat Sheet — Pick by What You Want to Do

| Your Goal | Command | How to Trigger |
|---|---|---|
| Build a feature or make a safe change | `/vibe <goal>` | Type in chat or click when offered |
| Only plan and compare options (no edits yet) | `/design <topic>` | Type in chat or click when offered |
| Approve the plan so the AI starts editing | `/approve` | Click **Approve** in the menu (or type `/approve`) |
| Get a short, jargon-free explanation | `/concept <question>` | Type in chat (also the default for Q&A) |
| See full file paths, code & logs | `/more-detail` | Type in chat or click when offered |
| Find the real cause of an error or bug | `/debug <problem>` | Type in chat or click when offered |
| Run real tests / check changes | `/test` or `/audit` | Type in chat or click when offered |
| Move a long chat to a fresh window | `/handoff` | Click **`/handoff`** in the menu (or type `/handoff`) |
| Shrink a long chat and stay here | `/compact` | Type `/compact` in the chat box and press `Enter` |
| Undo recent changes or clean old backups | `workflow_ops.py rollback` / `prune` | Dry-run preview first; add `--apply` to execute |
| Run all workflow checks in one go | `workflow_ops.py inspect --mode quick` | Runs audit + self-tests (+ optional `--tool` scripts) |
| Let the AI interview you to clarify a vague idea | `/grill-me` | Type `/grill-me` in the chat box and press `Enter` |

### A. Native Antigravity Slash Commands
*(Typed directly in the Antigravity chat input — cannot be executed programmatically by an agent)*

| Command | Plain-English Purpose |
|---|---|
| `/plan` | Enter careful step-by-step planning before making changes. |
| `/compact` | Compress older chat messages to free up memory in the current window. |
| `/goal` | Keep working thoroughly on a big task until the goal is completely done. |
| `/schedule` | Set a one-time timer or recurring reminder inside the current session. |
| `/automation` | Guided setup for a recurring background task (runs on a schedule). |
| `/browser` | Open and interact with live websites or web apps in the built-in browser. |
| `/grill-me` | Have the AI ask focused questions one by one to clarify a fuzzy idea. |
| `/teamwork` | Coordinate a multi-agent team for large parallel projects. |
| `/learn` | Save a solved trick or preference so the AI remembers it next time. |
| `/boost` | Turn on deep multi-angle thinking and extra-careful verification. |
| `/plugin` | Manage, enable, disable, or package plugins. |

### B. Workflow Prompt Action Triggers (Chat)
*(Handled by `AGENTS.md` and `.agents/skills/` — can also be triggered right after clicking a menu option)*

| Trigger | Owner | What It Does |
|---|---|---|
| `/vibe <goal>` | `@lead` (`plan-and-build`) | Full guided flow: size the task → plan → click `/approve` → back up → build → test → summarize. |
| `/design <topic>` | `@lead` (`plan-and-build`) | Write a clear blueprint (`artifacts/blueprints/` with `U1, U2...` steps and rollback plan) without editing code. |
| `/approve [Option]` | `@lead` (`plan-and-build`) | Authorize `@builder` to make the exact edits in the agreed plan. |
| `/code` | `@builder` (`plan-and-build`) | Save a backup and apply the smallest clean change inside the approved plan. |
| `/simplify` | `@builder` (`plan-and-build`) | Clean up recent edits (remove waste, move stray code notes to `artifacts/comments/`) without breaking tests. |
| `/test` | `@verifier` (`verify-and-debug`) | Run real test/lint commands and report exact pass/fail counts, exit codes, and `Untested Scope`. |
| `/debug <issue>` | `@verifier` (`verify-and-debug`) | Trace root cause systematically (`Hypothesis -> Prediction -> Check`), challenge assumptions at $N=2$, stop at $N \ge 3$. |
| `/audit` | `@verifier` (`verify-and-debug`) | Read-only check of the change diff, caller updates, and safety guardrails. |
| `/finalize` | `@lead` (`plan-and-build`) | Verify every success criterion, save `.diff`, check `/compound`, and log the turn. |
| `/compound` | `@lead` (`verify-and-debug`) | Turn a solved non-trivial bug into a permanent safeguard (`Test/Lint -> Rule -> Solution Doc`). |
| `/ck` | `@lead` (`workflow-ops`) | Save or inspect the Rolling `15` Checkpoints in `.agents/ck/`. |
| `/handoff` | `@lead` (`workflow-ops`) | Offered in a clickable menu alongside `/compact`: creates `.agents/ck/HANDOFF.md`, archives under `artifacts/handoffs/`, marks `HANDOFF_READY` for `SessionStart`, and prints a Ready-to-Paste Starter Prompt for a fresh chat window. |
| `/concept`, `/no-code`, `/no-detail` | `@lead` (`AGENTS.md` §0) | Force a short `3–5` bullet plain-language explanation with no code snippets or untouched file lists. |
| `/more-detail` | `@lead` (`AGENTS.md` §0) | Show full file paths, line numbers, code/config details, and full command outputs. |
| `/refactor-agents` | `@lead` (`workflow-ops`) | Audit and tidy `AGENTS.md` and `.agents/` while keeping budgets and schemas clean. |

### C. AI Team Roles (`@role`)

| Role | Tier 1 Model | Can Edit Files? | Shell Policy | Best Used For |
|---|---|---|---|---|
| `@lead` | `pro` | Yes (Coordinator) | `auto` | Planning, checking conflicts, clickable `/approve` menus, and final summaries. |
| `@builder` | `flash` | Yes (Approved Scope Only) | `auto` | Backing up and making approved edits cleanly. |
| `@verifier` | `flash` | **No (Read-Only)** | `sandbox` | Running real tests, investigating bugs, and auditing diffs safely. |
| `@researcher` | `flash_lite` | **No (Read-Only)** | `off` | Fast, low-cost codebase exploration and web documentation lookups. |

### D. Bundled Python CLI Commands
*(Run from your project's main folder; use `python3` on Mac/Linux if `python` is not available)*

| Command | Plain-English Purpose |
|---|---|
| `python .agents/scripts/workflow_ops.py set-language --lang "<Language>"` | Set your preferred chat & `artifacts/` language across workflow files (saves a backup automatically). |
| `python .agents/scripts/workflow_ops.py check-placeholders` | List every unfilled `{{PLACEHOLDER}}` blank with exact file and line numbers. |
| `python .agents/scripts/workflow_ops.py check-placeholders --fail-on-found` | Same scan, returning `Exit 1` if any blank is still unfilled (readiness check). |
| `python .agents/scripts/workflow_ops.py backup --topic "<slug>" <files...>` | Save a timestamped safety copy + `SHA-256` manifest under `backup/` (auto-prunes backups older than `30` days). |
| `python .agents/scripts/workflow_ops.py diff --output "artifacts/diffs/YYYY-MM-DD/<slug>.diff"` | Save a clean before-and-after `.diff` against the latest backup (works without Git). |
| `python .agents/scripts/workflow_ops.py rollback --backup "<dir>" [--apply]` | Dry-run preview (default) or `--apply` to restore `SHA-256`-verified files and remove newly created `absent` files. |
| `python .agents/scripts/workflow_ops.py prune --keep-days 30 [--apply]` | Dry-run preview (default) or `--apply` to delete `backup/` entries older than `30` days (never touches `artifacts/`). |
| `python .agents/scripts/workflow_ops.py inspect --mode quick` | Run unified health gates (`quick` / `full` / `tools-only`, optional `--tool`, `--fail-fast`, `--json`, `--report`). |
| `python .agents/scripts/workflow_ops.py log-turn --title "<t>" --summary "<s>"` | Log the session summary in `artifacts/Conversations/` and update the Rolling `15` Checkpoints. |
| `python .agents/scripts/workflow_ops.py handoff --objective "<obj>"` | Build a fresh-window handoff packet (`.agents/ck/HANDOFF.md` + `artifacts/handoffs/`) and starter prompt. |
| `python .agents/scripts/verify_workflow.py` | Check all workflow rules, agents, skills, hooks, links, and encoding (`Exit 0` = healthy). |
| `python .agents/scripts/verify_workflow.py --root "<path>"` | Run the same health check on another project folder. |
| `python -m unittest discover -s .agents/scripts -p "test_*.py" -v` | Run all built-in self-tests in isolated temporary folders (never touches your real files). |
| `python .agents/scripts/workflow_hooks.py <session-start\|pre-tool\|post-tool\|stop>` | Automatic hook runner invoked by `.agents/hooks.json`. |

### E. Project Placeholder Commands (Filled in `AGENTS.md`)

| Placeholder | What to Fill In |
|---|---|
| `{{INSTALL_COMMAND}}` | Command to install packages (e.g., `pip install -r requirements.txt`, `npm ci`). |
| `{{RUN_COMMAND}}` | Command to start your app locally (e.g., `npm run dev`, `python main.py`). |
| `{{BUILD_COMMAND}}` | Command to build/compile (e.g., `npm run build`, or `N/A` if none). |
| `{{TEST_COMMAND}}` | Command to run your automated tests (e.g., `python -m unittest discover -s tests`, `npm test`). |
| `{{LINT_COMMAND}}` | Command to run your code checker (e.g., `ruff check .`, `npm run lint`). |

---

## 4. What a Real Session Looks Like (Step-by-Step)

1. **Open a Chat (Automatic Setup & Memory):**
   - *First time ever:* `SessionStart` notices `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` is still blank and pops up a clickable language menu. Click your language and the assistant saves it automatically.
   - *Every session after:* `SessionStart` loads your latest checkpoint (or `.agents/ck/HANDOFF.md` if you just moved windows) and reminds you if any bug report has been open for `3–7` days.
2. **Ask or Request Work:** Ask a question (get a crisp `3–5` bullet plain-language reply) or type `/vibe <what you want>`.
3. **Review Plan & Click Approve:** `@lead` checks your files for conflicts, summarizes the plan and success criteria in plain words, and shows a clickable **Approve / Cancel** (or **Option A / Option B**) menu.
4. **Backup & Build:** After you click Approve, `@builder` saves a Pre-Action Backup, makes the minimal edits, cleans up any stray notes into `artifacts/comments/`, and runs syntax checks.
5. **Real Verification:** `@verifier` runs real tests and inspects the change diff in Read-Only mode. If a small in-scope bug appears, `@lead` can fix it right away without re-asking `/approve` (stopping cleanly if stuck `3` times).
6. **Wrap Up & Long-Chat Care:** `@lead` reports *(1) What happened, (2) What changed, (3) Next steps* with clickable file links and a `.diff`. When the chat reaches `10–12` turns, a clickable menu offers **`/handoff`** (start fresh) or **`/compact`** (stay here).

---

## 5. New Project Setup Guide: Needs to Have • Needs to Prepare • Needs to Do

### 5.1 What a New Project NEEDS TO HAVE (Prerequisites)

| Requirement | Status | Plain-English Details |
|---|---|---|
| **1. Antigravity App** | **Required** | Antigravity 2.0 desktop app, Antigravity IDE, or Antigravity CLI (`agy`) supporting `AGENTS.md` and `.agents/`. |
| **2. Python 3.10+** | **Required** | Standard Python 3.10+ installed (`python` on Windows; `python3` on Mac/Linux). **Zero extra packages** required. |
| **3. Clear Project Folder** | **Required** | A top-level project folder separating your app code (`{{SRC_DIR}}`) and tests (`{{TEST_DIR}}`) from `.agents/`, `artifacts/`, and `backup/`. |
| **4. Test / Lint Command** | **Recommended** | At least one real test or check command (`{{TEST_COMMAND}}` / `{{LINT_COMMAND}}`) so `@verifier` can prove changes work. |
| **5. Git + `.gitignore`** | **Optional** | Helpful for history, though backups and `.diff` work without Git. Add `backup/`, `artifacts/scratch/`, `.agents/ck/last_alert.log`, and `.env` to `.gitignore`. |

### 5.2 What a New Project NEEDS TO PREPARE (Complete `33`-Placeholder Checklist)

Gather the details below before filling in the blanks. Each item matches one of the **`33` `{{PLACEHOLDERS}}`** scanned by `python .agents/scripts/workflow_ops.py check-placeholders`.

#### Group 1 — Identity & Language (`3` placeholders)
| Placeholder | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{PROJECT_NAME}}` | Your project's name | `Acme Billing API` | `AGENTS.md`, `rules.md`, `lead.md`, `verifier.md`, `project-tasks`, `context.json`, templates |
| `{{PROJECT_OBJECTIVE}}` | 1–2 sentences describing what the project does | `Build a reliable invoice API that never double-charges` | `AGENTS.md`, `project-tasks`, `project_fanout.py` |
| `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` | Your preferred chat & notes language *(can be set via first-run menu or `set-language`)* | `English` or `Thai` | `AGENTS.md`, `lead.md`, `coding-and-safety.md`, `workflow-ops`, `artifacts/README.md` |

#### Group 2 — Stack, Folders & High-Risk Files (`6` placeholders)
| Placeholder | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{TECH_STACK}}` | Languages, frameworks, and databases used | `Python 3.12, FastAPI, PostgreSQL, React 19` | `AGENTS.md`, `project-tasks` |
| `{{SRC_DIR}}` | Main app source folder *(turns on automatic backup guard in `workflow_hooks.py` once filled)* | `src/` | `AGENTS.md`, `project-tasks`, `workflow_hooks.py` |
| `{{TEST_DIR}}` | Automated test folder | `tests/` | `AGENTS.md`, `project-tasks` |
| `{{PROTECTED_PATHS}}` | Folders/files requiring backup + `/approve` | `src/, config/, AGENTS.md, .agents/` | `AGENTS.md`, `coding-and-safety.md` |
| `{{HIGH_BLAST_RADIUS_MODULES}}` | Core files where a mistake affects the whole app | `src/config.py, src/auth/jwt.py, src/db/schema.sql` | `coding-and-safety.md`, `project-tasks` |
| `{{NAMING_CONVENTIONS}}` | Preferred naming style for files and code | `Python snake_case/PascalCase; TS camelCase/PascalCase` | `AGENTS.md` |

#### Group 3 — Project Commands (`5` placeholders)
| Placeholder | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{INSTALL_COMMAND}}` | Install dependencies | `pip install -r requirements.txt` or `npm ci` | `AGENTS.md`, `project-tasks` |
| `{{RUN_COMMAND}}` | Start the app locally | `uvicorn src.main:app --reload` or `npm run dev` | `AGENTS.md`, `project-tasks` |
| `{{BUILD_COMMAND}}` | Build/compile (or `N/A`) | `npm run build` or `N/A` | `AGENTS.md`, `builder.md`, `project-tasks` |
| `{{TEST_COMMAND}}` | Run automated tests | `python -m unittest discover -s tests` or `npm test` | `AGENTS.md`, `verifier.md`, `project-tasks`, `verify-and-debug` |
| `{{LINT_COMMAND}}` | Run code checker / linter | `ruff check .` or `npm run lint` | `AGENTS.md`, `builder.md`, `verifier.md`, `project-tasks`, `verify-and-debug` |

#### Group 4 — Main Project Tasks & Pass Criteria (`9` placeholders)
| Placeholder Group | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{TASK_1_NAME}}`, `{{TASK_1_OBJECTIVE}}`, `{{TASK_1_ACCEPTANCE}}` | Priority 1 task, goal, and how to prove it works | `Auth API` / `Add login` / `All 12 auth tests pass + invalid token rejected` | `AGENTS.md`, `project-tasks` |
| `{{TASK_2_NAME}}`, `{{TASK_2_OBJECTIVE}}`, `{{TASK_2_ACCEPTANCE}}` | Priority 2 task, goal, and how to prove it works | `Billing Webhook` / `Safe retries` / `Duplicate requests never double-charge` | `AGENTS.md`, `project-tasks` |
| `{{TASK_3_NAME}}`, `{{TASK_3_OBJECTIVE}}`, `{{TASK_3_ACCEPTANCE}}` | Priority 3 task, goal, and how to prove it works | `Logging` / `Clear JSON logs` / `Zero crashes in smoke run` | `AGENTS.md`, `project-tasks` |

#### Group 5 — Safety Rules & Blocked Commands (`3` placeholders)
| Placeholder | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{DOMAIN_CONSTRAINTS}}` | Hard project rules the AI must never break | `Never call live payment gateways in tests` | `AGENTS.md`, `coding-and-safety.md`, `project-tasks` |
| `{{NEVER_CUT_LIST}}` | Safeguards the AI must never remove or weaken | `Input validation, Auth checks, DB transaction guards, Existing tests` | `AGENTS.md`, `coding-and-safety.md`, `verifier.md`, `project-tasks`, `verify-and-debug` |
| `{{FORBIDDEN_COMMAND_REGEX}}` | Optional pattern of dangerous terminal commands to block (leave blank `""` if unused) | `\brm\s+-rf\s+/` | `.agents/scripts/workflow_hooks.py` |

#### Group 6 — Optional Add-On Templates (`7` placeholders)
| Placeholder | What to Prepare | Example | Primary Files |
|---|---|---|---|
| `{{WORKFLOW_TARGET_GLOB}}` | Default file pattern for parallel `run_workflow` reviews | `src/**/*.py` | `.agents/workflows/project_fanout.py` |
| `{{MCP_SERVER_NAME}}`, `{{MCP_STDIO_COMMAND}}`, `{{MCP_HTTP_URL}}` | MCP tool name and local command or `/mcp` URL (only if using MCP) | `db-tools`, `sqlite-mcp-server`, `https://mcp.example.com/mcp` | `.agents/templates/mcp_config.example.json` |
| `{{IANA_TIMEZONE}}`, `{{SCHEDULE_CRON}}`, `{{SCHEDULE_TASK_PROMPT}}` | Timezone name (like `Asia/Bangkok`), schedule, and task prompt (only if scheduling jobs) | `Asia/Bangkok`, `0 9 * * 1-5`, `Run test suite and summarize failures` | `.agents/templates/sidecar.schedule.example.json` |

### 5.3 What a New Project NEEDS TO DO (Step-by-Step)

1. **Copy the Workflow Into Your Project's Top Folder:** Copy `AGENTS.md`, `MANUAL_EN.md` (and/or `MANUAL_TH.md`), `.agents/`, and `artifacts/` directly into your project's root folder (not inside another folder that already has `AGENTS.md`). Add `backup/`, `artifacts/scratch/`, and `.agents/ck/last_alert.log` to `.gitignore`.
2. **Check Python:** Run `python --version` (`3.10+`). On Mac/Linux where only `python3` exists, change `python` to `python3` in [.agents/hooks.json](./.agents/hooks.json), keeping `scripts/workflow_hooks.py` relative to `.agents/`.
3. **Pick Your Language & Fill the Blanks:**
   ```bash
   python .agents/scripts/workflow_ops.py set-language --lang "English"   # or click from the first-run chat menu
   python .agents/scripts/workflow_ops.py check-placeholders
   ```
   Fill in [AGENTS.md](./AGENTS.md), `.agents/rules/*.md`, [.agents/skills/project-tasks/SKILL.md](./.agents/skills/project-tasks/SKILL.md), the agent/skill command references, [.agents/scripts/workflow_hooks.py](./.agents/scripts/workflow_hooks.py), [.agents/ck/context.json](./.agents/ck/context.json), and [artifacts/README.md](./artifacts/README.md). Delete `.agents/templates/*` if you do not need MCP or scheduled sidecars yet so `--fail-on-found` passes cleanly.
4. **Run the Health Check & Self-Tests (All Should Pass With `Exit 0`):**
   ```bash
   python .agents/scripts/workflow_ops.py check-placeholders --fail-on-found
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. **Optional Strict Stop Guard:** To block ending a turn while `.agents/ck/last_alert.log` still has an alert, change `"enabled": false` to `true` on `"alert-stop-gate"` inside [.agents/hooks.json](./.agents/hooks.json).
6. **Try a Quick First Session:**
   - Open your project in Antigravity and verify startup completes cleanly.
   - Ask *"Explain how this project is organized"* to confirm clear, jargon-free `3–5` bullet answers in your language.
   - Run one small task through `/vibe` → click Approve → `/finalize`, confirming backup, tests, `.diff`, and saved history.
7. **Grow the Team Only When Needed:** Start lean with `4` roles (`lead`, `builder`, `verifier`, `researcher`) and add specialists only when your project outgrows them:
   - Add **`@architect`** (`pro`) for complex multi-service designs.
   - Split **`@verifier`** into **`@tester`**, **`@reviewer`**, and **`@code-skeptic`** as change volume grows.
   - Add **`@risk-guardian`** (`pro`, Read-Only Veto) for finance, security, or sensitive-data apps.
   - After adding any `.agents/agents/<name>.md`, update the team table and count in `AGENTS.md` and run `python .agents/scripts/verify_workflow.py` (`Exit 0`).
