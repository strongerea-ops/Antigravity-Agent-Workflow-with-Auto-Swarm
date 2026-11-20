---
name: workflow-ops
description: "O(1) session rehydration, Rolling 15 Checkpoints (/ck), context quota management (/compact), turn logging, placeholder scanning, and workflow self-auditing."
---

# Skill: workflow-ops

> **Purpose:** Keep session state durable, context lean, and workflow files verified using pure-Python stdlib automation in `.agents/scripts/`.

## 1. Tri-Tier Context Quota & $O(1)$ Rehydration (`/compact`, `/ck`)
1. **Tier 1 — Output Pruning:** Strip noisy raw logs and boilerplate; report unified diffs (`-U1`) and exact pass/fail summaries.
2. **Tier 2 — Proactive `/compact` Trigger:** When `<CONTEXT_SUMMARY>` appears or a conversation reaches `10–12` turns (`~35` tool calls), confirm checkpoint $t_0$ is saved and recommend `/compact`.
3. **Tier 3 — $O(1)$ Rehydration:** On every new session or right after `/compact`, read the top `3` lines of `artifacts/Conversations/README.md` + `.agents/ck/context.json` ($t_0$) (~250 tokens). When `.agents/hooks.json` `SessionStart` is active, Antigravity automatically injects a startup pointer to the active checkpoint.

## 2. Rolling 15 Checkpoints & Pre-Restore Validation
- `workflow_ops.py log-turn` maintains a FIFO ring buffer of up to `15` snapshots in `.agents/ck/history/context_YYYYMMDD_HHMMSS.json`, copies the latest to `.agents/ck/context.json` ($t_0$), and renders `.agents/ck/CONTEXT.md`.
- **Zero Secrets:** Never store API keys, tokens, passwords, or PII in checkpoints or artifacts.
- **Pre-Restore Validation:**
  - *Valid:* Treat checkpoint fields as navigation hints verified against current disk state.
  - *Stale/Drifted:* If files changed after `saved_at`, mark `Needs Revalidation` and re-read source files.
  - *Corrupt/Unsupported:* Never silently overwrite; report truthfully and rebuild context from source/artifacts.
  - *Strict Approval Boundary:* Checkpoint `status` NEVER substitutes for a fresh `/approve`.

## 3. Archival & 7-Test No-Slop Logging
- Primary Intake (`@lead`) owns daily conversation logging via `python .agents/scripts/workflow_ops.py log-turn --title "..." --summary "..."`.
- Write `artifacts/` entries in `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` using relative paths only (`BOM=False`) and update `README.md` for every populated artifact category.
- Apply **7-Test No-Slop**: state concrete *Mechanism*, avoid generic *Portability*, name the *Actor*, keep *One Idea* per bullet, maximize *Density*, put the *Decision-First*, and make next actions *Reader-Actionable*.

## 4. Essential CLI Operations
```bash
# Scan remaining {{PLACEHOLDERS}} across the workflow
python .agents/scripts/workflow_ops.py check-placeholders

# Pre-Action Backup with SHA-256 manifest
python .agents/scripts/workflow_ops.py backup --topic "<topic>" <files...>

# Generate -U1 diff against latest backup (works even without .git)
python .agents/scripts/workflow_ops.py diff --output "artifacts/diffs/YYYY-MM-DD/<topic>.diff"

# Audit AGENTS.md, 4 Agents, 4 Skills, hooks.json, scripts, workflows & artifacts
python .agents/scripts/verify_workflow.py
```
