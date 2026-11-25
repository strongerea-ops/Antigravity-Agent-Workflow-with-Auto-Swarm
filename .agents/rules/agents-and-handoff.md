# Agents, `/approve`, `/handoff` & Onboarding Governance Rules

> **Scope:** Read for first-time language onboarding, interactive `/approve` & choice menus, `/handoff`, authoring `.agents/agents/*.md`, `Post-Approval Auto-Fix`, or `3–7` day bug reminders. Core policies live in [AGENTS.md](../../AGENTS.md) and [workflow-ops](../skills/workflow-ops/SKILL.md).

## 1. First-Time User Language Selection (Onboarding)
- When starting a session where `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` is still unfilled in `AGENTS.md` (detected deterministically by the `SessionStart` hook in `workflow_hooks.py`), **pause before normal tasks** and present a clickable `ask_question` language picker (e.g., `English`, `Thai (ภาษาไทย)`, `Japanese (日本語)`, `Chinese (中文)` — the UI also provides an "Other" input for any language).
- Once the user selects a language, run `python .agents/scripts/workflow_ops.py set-language --lang "<Language>"` (which automatically creates a Pre-Action Backup, replaces `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` across active workflow files, and records `"chat_language"` in `.agents/ck/context.json`).
- Keep system docs (`AGENTS.md`, `.agents/`) and internal thinking in **English** to conserve tokens; conduct all chat replies and `artifacts/` entries in the chosen language from that point forward.

## 2. Interactive `/approve`, Proactive Proposals & Post-Approval Auto-Fix
- **Supreme Approval Gate (`AGENTS.md` §6.8):** Before writing, adding, or editing source code or workflow architecture:
  1. Summarize atomic steps (`U1, U2...`), target files, and clear **Acceptance Criteria** (mandatory for open-ended/multi-interpretation tasks).
  2. Audit **Conflict & Redundancy** across configs, data flow, parameters, schemas, and cross-references *(halt and report immediately if found)*.
  3. Compare Pros/Cons **only** on genuinely divergent paths (bundle compatible improvements) and **proactively propose** any better approach with merit & feasibility evaluation.
  4. Present a clickable **`ask_question` menu** (`Approve (/approve)` vs `Cancel`, or all proposed choices such as `Option A` / `Option B`) so the user can click instead of typing, and await explicit `/approve`.
- **Self-Mistake Governance:** Whenever an agent discovers it made a mistake, propose documenting a preventive rule or rectification method in `AGENTS.md` or `.agents/` and obtain `/approve` before editing workflow files.
- **Post-Approval Auto-Fix:** After `/approve` is granted, if `@verifier` reports `FAIL` or a defect strictly within the approved scope with zero Conflict/Redundancy, `@lead` may dispatch `@builder` to fix it without re-requesting `/approve` (preserving Pre-Action Backup, 100% Callers, Never Cut List, and Circuit Breaker $N \ge 3$). Any scope expansion or conflict requires a fresh `/approve`.

## 3. Clickable Menus for `/handoff`, `/compact` & Command Introductions + Bug Reminders
- **Context-Quota Clickable Menu (`10–12` Turns / `~35` Calls / `<CONTEXT_SUMMARY>`):** Present a clickable `ask_question` menu instead of plain text alone, with clear options:
  1. `Create /handoff for a fresh chat window (Recommended)` — executes `python .agents/scripts/workflow_ops.py handoff --objective "<objective>"` immediately on click, saving `artifacts/handoffs/YYYY-MM-DD/YYYYMMDDTHHMMSSffffffZ_handoff.md` and `.agents/ck/HANDOFF.md` (`status: HANDOFF_READY`), and gives the user: (1) link to the saved handoff file, (2) how to open a new chat window, and (3) the Ready-to-Paste Starter Prompt.
  2. `Use /compact in this window (type /compact in chat)` — confirms the latest checkpoint is saved and prompts the user to type `/compact` in the chat input (runtime-honest: native UI slash commands cannot be invoked programmatically by the agent).
  3. `Continue without compacting for now`
- **Clickable Menu When Introducing or Suggesting Commands:** Whenever recommending next-step commands (e.g., `/vibe`, `/design`, `/test`, `/debug`, `/audit`, `/simplify`, `/compound`, `/concept`, `/more-detail`, or native Antigravity commands like `/plan`, `/grill-me`, `/goal`, `/teamwork`, `/browser`, `/automation`, `/boost`), offer clickable `ask_question` choices with plain-language descriptions so users (including non-programmers) can click instead of memorizing syntax. Clearly distinguish **workflow prompt triggers** (executed immediately after clicking) from **native Antigravity UI slash commands** (which the user types in chat).
- **Unresolved Recent Bug Reminder (`3–7` Days):** `workflow_hooks.py` deterministically scans `artifacts/bug-reports/README.md` at `SessionStart`; if any unresolved bug report has age `3 < age <= 7` days, surface a concise reminder to address it.

## 4. Agent Authoring Schema (`10` Elements), Tool Mapping & Runtime Honesty
- `swarm` accepts explicit Model+Effort IDs from `AGENTS.md` §7 (**never put `swarm` in YAML `tools:`**).
- Custom Subagents (`invoke_subagent`) accept only `inherit`, `flash_lite`, `flash`, or `pro`.
- Every `.agents/agents/*.md` file MUST include `name`, `description`, `tools` (non-empty valid registry tools), `subagent: true`, `mainAgent`, `model`, `commandExecutionPolicy` (`auto`/`sandbox`/`off`), `skills`, `# System Prompt`, and `# Review Guidelines`.
- **Runtime Honesty:** Distinguish deterministic Python hook/CLI enforcement from prompt-governed policies. Never claim a model can switch its own main-chat UI model or thinking budget programmatically.
