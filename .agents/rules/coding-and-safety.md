# Coding, Blast Radius & Rollback Safety Rules

> **Scope:** Read before modifying `{{PROTECTED_PATHS}}`, high-blast-radius modules, shared contracts, or running backups/rollbacks. Core constraints live in [AGENTS.md](../../AGENTS.md) and [rules.md](./rules.md).

## 1. Blast-Radius Governance
- **High-Blast-Radius Modules:** `{{HIGH_BLAST_RADIUS_MODULES}}`
  - *Mandate:* Require explicit impact tracing (`Caller -> Changed Code -> Consumer/Side Effects`), full regression tests, and `/approve` before any modification.
- **Protected Workflow & Source Paths:** `AGENTS.md`, `.agents/`, and `{{PROTECTED_PATHS}}`
  - *Mandate:* Guarded at runtime by `.agents/hooks.json` (`PreToolUse` backup verification + `PostToolUse` workflow hygiene check).

## 2. Extended Guardrails & Code Hygiene
- **Project-Specific Domain Rules:** `{{DOMAIN_CONSTRAINTS}}`
- **Never Cut List:** `{{NEVER_CUT_LIST}}`
- **Zero In-Code Comments (`artifacts/comments/`):** Do not write explanatory notes or comments inside source code; record necessary notes in `artifacts/comments/YYYY-MM-DD/YYYYMMDD_comment_<topic>.md` (in `{{CHAT_AND_ARTIFACTS_LANGUAGE}}`, indexed in `artifacts/comments/README.md`). Inline comments are allowed only when strictly necessary and high-importance (`CRITICAL:`, `IMPORTANT:`, `SAFETY:`, `INVARIANT:`, or mandatory interpreter/linter/type-checker directives such as `# -*- coding: utf-8 -*-`, `# type: ignore`, `eslint-disable`).
- **Shared Contract Rule:** Before renaming or changing any shared function, API schema, CLI flag, skill, or agent name, grep 100% of references across source, tests, configs, `AGENTS.md`, `.agents/`, and `hooks.json`.
- **Environment & VCS Hygiene:** Never commit `node_modules/`, `dist/`, `build/`, `__pycache__/`, `.pytest_cache/`, `.venv/`, secrets (`.env`), or `.log` files. `file:///` links are permitted only in IDE chat responses, never in committed files. On Windows terminals handling UTF-8 / non-ASCII logs, set `PYTHONIOENCODING=utf-8` (or `chcp 65001`).

## 3. Pre-Action Backup & Rollback Semantics
- Run `python .agents/scripts/workflow_ops.py backup --topic "<topic>" <files...>` before editing protected files (avoiding raw interactive shell copy commands that risk stalling).
- *Existing files:* Copied with `SHA-256` into `backup/YYYYMMDDTHHMMSSffffffZ_<topic>/manifest.json` (`"status": "backed_up"`, RFC 3339 UTC microsecond timestamp). On rollback, copy the backup file back over the target.
- *Newly created files:* Recorded as `"status": "absent"`. On rollback, delete the newly created file cleanly.
