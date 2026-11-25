# Operational Rules — Task-Based Index

> **Project:** `{{PROJECT_NAME}}`  
> **Single Source of Truth:** Core mandates, Language Governance (including First-Time Language Selection), Hard Constraints (`6.1–6.12`), Model Matrix, and Directives (`0–12`) live in [AGENTS.md](../../AGENTS.md).  
> **How to Read:** Consult only the rule file(s) matching your current task instead of reading everything.

| Task Nature | Rule File | When to Read |
|---|---|---|
| **Code Edits, Blast Radius & Safety** | [coding-and-safety.md](./coding-and-safety.md) | Modifying protected source paths, high-blast-radius modules, shared contracts, or running backups/rollbacks |
| **Commands, Hooks & Tooling Hygiene** | [commands-and-tools.md](./commands-and-tools.md) | Configuring hooks (`CWD = .agents/`), running workflow CLI commands, or creating/promoting scripts in `artifacts/tools/` & `artifacts/scratch/` |
| **Agents, `/approve`, `/handoff` & Onboarding** | [agents-and-handoff.md](./agents-and-handoff.md) | First-time user language selection, interactive `ask_question` `/approve` menus, `/handoff`, 10-element agent schema, `Post-Approval Auto-Fix`, or `3–7` day bug reminders |

---

## Cross-Task Swarm Safety & Skill Quick Links
- **Swarm Workspace Isolation on Dirty Working Trees:** When spawning Tier 2 `swarm` workers on a repository with uncommitted local changes, **never** use `workspace:"share"` (git worktree checks out `HEAD` and omits uncommitted edits). Use `workspace:"inherit"` with strictly disjoint file ownership per worker plus a consolidated Pre-Action Backup before edits begin. Reserve `workspace:"share"` or `"branch"` strictly for clean, committed working trees.
- **Skills:** [project-tasks](../skills/project-tasks/SKILL.md) | [plan-and-build](../skills/plan-and-build/SKILL.md) | [verify-and-debug](../skills/verify-and-debug/SKILL.md) | [workflow-ops](../skills/workflow-ops/SKILL.md)
