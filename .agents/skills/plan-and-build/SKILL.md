---
name: plan-and-build
description: "End-to-end planning, approval, implementation, simplification, and closure lifecycle (/vibe, /design, /approve, /code, /simplify, /finalize) with Pre-Action Backup and Post-Approval Auto-Fix."
---

# Skill: plan-and-build

> **Core Rules:** Reference [AGENTS.md](../../../AGENTS.md) (§3, §6, §9) and [rules.md](../../rules/rules.md). This skill governs `/vibe`, `/design`, `/approve`, `/code`, `/simplify`, and `/finalize`.

## 1. Proportional Triage (`/vibe`)
- **Tier 0 (In-line Fast Path):** 1–2 line low-risk fixes with explicit targets or concise Q&A (`<= 3` reads).
- **Tier 1 (`invoke_subagent`):** Scoped feature/bug work (`1–8` files) routed through `@researcher`, `@builder`, and `@verifier`.
- **Tier 2 (`swarm` / `run_workflow`):** `>= 9` modified files or `>= 2` disjoint workstreams use `swarm` (obeying the Dirty-Tree Rule in `rules.md`: `workspace:"inherit"` on dirty trees, `workspace:"share"`/`"branch"` only on clean committed trees). Structured multi-file analysis uses `run_workflow` (`.agents/workflows/project_fanout.py`).

## 2. Design & Blueprint Phase (`/design`)
For new features, architectural changes, or multi-file tasks, write a blueprint under `artifacts/blueprints/YYYY-MM-DD/YYYYMMDD_blueprint_<topic>.md` containing:
1. **As-Is vs. To-Be Evidence:** Real entry points, callers, configs (`Static-confirmed` / `Runtime-confirmed` / `Unknown`).
2. **Conflict, Redundancy & Guardrails:** Config, schema, data-flow checks + Never Cut List.
3. **Edge Cases & Considered-and-Not-Built:** Failure modes and intentionally skipped abstractions (KISS/YAGNI).
4. **Stable Implementation Units (`U1, U2...`) & Rollback:** Never renumber existing `U-IDs`; append new IDs if scope expands.
5. **Acceptance Criteria & Verification Matrix:** Measurable checks mapped to `U-IDs`.

## 3. Supreme Approval Gate (`/approve`)
Before editing source code or workflow architecture, present:
1. Atomic steps (`U-IDs`), exact target files, and clear **Acceptance Criteria** bullets (for open-ended or multi-interpretation tasks).
2. Conflict/Redundancy audit results (halt immediately if found).
3. Pros/Cons **only** for divergent architectural options (bundle compatible items) and proactively propose any better approach with merit & feasibility evaluation.
4. A clickable `ask_question` menu (`Approve (/approve)` / `Cancel`, or all proposed options) and await explicit `/approve` (respecting `session-settled:` user choices). On any agent mistake, propose a preventive rule for `AGENTS.md`/`.agents/` and obtain `/approve` first.

## 4. Build & Simplify (`/code`, `/simplify`)
1. **Pre-Action Backup:** Run `python .agents/scripts/workflow_ops.py backup --topic "<topic>" <files...>` before modifying protected files.
2. **Baseline & Idempotent Re-entry:** Check `git status --short` (or backup manifest in non-Git repos); never revert pre-existing user changes; skip units already satisfied.
3. **Minimal Diff Implementation:** Smallest Complete Change, 100% caller updates, root-cause fixes, zero mock data on owned code, Zero In-Code Comments (`artifacts/comments/`), `BOM=False`, relative paths only.
4. **Post-Build Simplification (`/simplify`):** Pass changes through `5` lenses — **Reuse**, **Quality**, **Efficiency**, **Test Value**, and **Zero In-Code Comments** (relocate any necessary notes to `artifacts/comments/YYYY-MM-DD/YYYYMMDD_comment_<topic>.md`; keep inline comments only for high-importance safety/invariant markers or mandatory directives) — without weakening validations or tests.

## 5. Post-Approval Auto-Fix & Closure (`/finalize`)
- **Post-Approval Auto-Fix:** If `@verifier` reports a defect strictly inside approved scope with zero Conflict/Redundancy, `@lead` may dispatch `@builder` again without re-asking `/approve` (respecting Circuit Breaker $N \ge 3$).
- **Acceptance Evidence Closure (`/finalize`):** Verify every criterion (`Verified / Not Verified / N/A`), attach modified file links + `.diff` (`workflow_ops.py diff`), evaluate `/compound`, and run `workflow_ops.py log-turn`.
