# Operational Rules, Guardrails & Blast-Radius Governance

> **Project:** `{{PROJECT_NAME}}`  
> **Single Source of Truth:** Core mandates, Hard Constraints (`6.1–6.11`), Model Matrix, and Directives (`0–12`) live in [AGENTS.md](../../AGENTS.md). Keep only non-redundant operational rules, blast-radius boundaries, and rollback semantics here.

---

## 1. Blast-Radius Governance

List high-impact modules where changes affect multiple subsystems or runtime safety:
- **High-Blast-Radius Modules:** `{{HIGH_BLAST_RADIUS_MODULES}}`
  - *Mandate:* Require explicit impact tracing (`Caller -> Changed Code -> Consumer/Side Effects`), full regression tests, and `/approve` before any modification.
- **Protected Workflow & Source Paths:** `AGENTS.md`, `.agents/`, and `{{PROTECTED_PATHS}}`
  - *Mandate:* Guarded at runtime by `.agents/hooks.json` (`PreToolUse` backup verification + `PostToolUse` hygiene check).

---

## 2. Extended Guardrails & Operational Safety

- **Swarm Workspace Isolation on Dirty Working Trees:** When spawning Tier 2 `swarm` workers on a repository that contains uncommitted local changes, **never** use `workspace:"share"` (git worktree checks out `HEAD` and omits uncommitted edits). Use `workspace:"inherit"` with strictly disjoint file ownership per worker plus a consolidated Pre-Action Backup before edits begin. Reserve `workspace:"share"` or `"branch"` strictly for clean, committed working trees.
- **Environment & VCS Hygiene:** Never commit `node_modules/`, `dist/`, `build/`, `__pycache__/`, `.pytest_cache/`, `.venv/`, secrets (`.env`), or `.log` files. `file:///` links are permitted only in IDE chat responses, never in committed files. On Windows terminals handling UTF-8 / non-ASCII logs, set `PYTHONIOENCODING=utf-8` (or `chcp 65001`).
- **Project-Specific Domain Rules:** `{{DOMAIN_CONSTRAINTS}}`
- **Never Cut List:** `{{NEVER_CUT_LIST}}`
- **Shared Contract Rule:** Before renaming or changing any shared function, API schema, CLI flag, skill, or agent name, grep 100% of references across source, tests, configs, `AGENTS.md`, `.agents/`, and `hooks.json`.
- **Runtime Honesty:** Distinguish hook/OS-enforced checks (deterministic Python scripts in `.agents/scripts/`) from prompt-governed policies (`AGENTS.md` / `SKILL.md`). Never claim a model can switch its own main-chat UI model or thinking budget programmatically.

---

## 3. `/approve`, Conflict/Redundancy & Pre-Action Rollback Semantics

1. **Supreme Approval Rule (`AGENTS.md` §6.8):** Before writing, adding, or editing source code or workflow architecture:
   - `(1)` Summarize atomic steps (`U1, U2...`) and target files.
   - `(2)` Audit **Conflict & Redundancy** across configs, data flow, parameters, schemas, and cross-references *(halt and report immediately if found)*.
   - `(3)` Compare Pros/Cons **only** for genuinely divergent paths (bundle compatible improvements into one cohesive plan).
   - `(4)` Await explicit `/approve` from the user.
2. **Post-Approval Auto-Fix:** After `/approve`, if `@verifier` finds a defect strictly inside the approved scope with zero Conflict/Redundancy, `@lead` may dispatch `@builder` to fix it without re-asking `/approve` (preserving Pre-Action Backup, 100% Callers, Never Cut List, and Circuit Breaker $N \ge 3$). Any out-of-scope edit or newly discovered conflict requires a fresh `/approve`.
3. **Pre-Action Backup & Rollback Semantics:**
   - Run `python .agents/scripts/workflow_ops.py backup --topic "<topic>" <files...>` before editing protected files.
   - *Existing files:* Copied with `SHA-256` into `backup/YYYYMMDD-HHMMSS_ffffff_<topic>/manifest.json` (`"status": "backed_up"`). On rollback, copy the backup file back over the target.
   - *Newly created files:* Recorded as `"status": "absent"`. On rollback, delete the newly created file cleanly.
4. **Hook Runner CWD Contract:** Antigravity executes `.agents/hooks.json` commands with **CWD = `.agents/`**. All script paths inside `.agents/hooks.json` must resolve relative to `.agents/` (e.g., `scripts/workflow_hooks.py`).

---

## 4. Progressive Disclosure Index

- **Project Tasks, Objectives & Acceptance Criteria:** [project-tasks](../skills/project-tasks/SKILL.md)
- **Development Lifecycle (`/vibe`, `/design`, `/approve`, `/code`, `/simplify`, `/finalize`):** [plan-and-build](../skills/plan-and-build/SKILL.md)
- **Verification, Causal-Chain RCA, Circuit Breaker & `/compound`:** [verify-and-debug](../skills/verify-and-debug/SKILL.md)
- **Checkpoints (`/ck`), `/compact`, Turn Logging & Self-Audit:** [workflow-ops](../skills/workflow-ops/SKILL.md)
