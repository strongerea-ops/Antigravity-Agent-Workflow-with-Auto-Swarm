# Artifacts Vault Index

- **Scope & Retention:** Durable, user-managed reference materials for this project's agent workflow (**never auto-deleted**; write entries in `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` using relative links only and `BOM=False`). If any artifact conflicts with current operations or rules, alert the user with concrete recommendations rather than deleting it.

## Core Categories
- [Conversations](./Conversations/README.md) — Daily turn logs updated automatically by `workflow_ops.py log-turn`
- [user-requirements](./user-requirements/README.md) — Captured requirements and scope baselines (`R-IDs`)
- [blueprints](./blueprints/README.md) — Architecture & feature blueprints with stable `U-IDs`
- [project-memory](./project-memory/README.md) — Architecture Decision Records (ADRs)
- [diffs](./diffs/README.md) — Unified diffs (`-U1`) generated per change
- [reviews](./reviews/README.md) — Verification and static audit reports
- **Event-Driven Categories (create `README.md` and link here only when populated):** `handoffs/` (auto-indexed by `/handoff`), `comments/` (code notes relocated from source files), `bug-reports/` (auto-checked by `SessionStart` for `3–7` day unresolved reminders), `solutions/`, `Lessons/`, `agent-confession/`, `tools/` (reusable local helpers with `README.md`, runnable via `workflow_ops.py inspect --tool`)
- **Temporary One-Off Scripts:** Do **not** save disposable scripts under workspace `artifacts/scratch/` — use Antigravity's built-in per-session `scratch/` folder instead, and promote reusable cleaned helpers into `artifacts/tools/`.
