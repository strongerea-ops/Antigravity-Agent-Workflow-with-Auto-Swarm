# Artifacts Vault Index

- **Scope:** Durable records for this project's agent workflow (write entries in `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` using relative links only and `BOM=False`).

## Core Categories
- [Conversations](./Conversations/README.md) — Daily turn logs updated automatically by `workflow_ops.py log-turn`
- [user-requirements](./user-requirements/README.md) — Captured requirements and scope baselines (`R-IDs`)
- [blueprints](./blueprints/README.md) — Architecture & feature blueprints with stable `U-IDs`
- [project-memory](./project-memory/README.md) — Architecture Decision Records (ADRs)
- [diffs](./diffs/README.md) — Unified diffs (`-U1`) generated per change
- [reviews](./reviews/README.md) — Verification and static audit reports
- **Event-Driven Categories (create `README.md` and link here only when populated):** `handoffs/` (auto-indexed by `/handoff`), `comments/` (code notes relocated from source files), `bug-reports/` (auto-checked by `SessionStart` for `3–7` day unresolved reminders), `solutions/`, `Lessons/`, `agent-confession/`, `tools/` (reusable local helpers with `README.md`)
- **Disposable Category (safe to delete anytime; excluded from catalog parity & ignored by `.gitignore`):** `scratch/`
