---
name: workflow-ops
description: "O(1) session rehydration, Rolling 15 Checkpoints (/ck), context quota management (/compact), new-window session handoff (/handoff), turn logging, placeholder scanning, and workflow self-auditing."
---

# Skill: workflow-ops

> **Purpose:** Keep session state durable, context lean, and workflow files verified using pure-Python stdlib automation in `.agents/scripts/`.

## 1. Tri-Tier Context Quota, `/compact` & `/handoff` (`/compact`, `/handoff`, `/ck`)
1. **Tier 1 — Output Pruning:** Strip noisy raw logs and boilerplate; report unified diffs (`-U1`) and exact pass/fail summaries.
2. **Tier 2 — Proactive `/compact` or `/handoff` Alert:** When `<CONTEXT_SUMMARY>` appears or a conversation reaches `10–12` turns (`~35` tool calls), confirm checkpoint $t_0$ is saved and offer both:
   - **`/compact`** — stay in the **same chat window** with compacted history, OR
   - **`/handoff`** — hand off cleanly to a **brand-new chat window** with zero stale context.
3. **Tier 3 — New-Window `/handoff` & $O(1)$ Rehydration:**
   - Opening a new window is a UI action (`New Conversation`), while `/handoff` automates everything else: run `python .agents/scripts/workflow_ops.py handoff --objective "..." [--completed ...] [--settled ...] [--next ...] [--blockers ...] [--touched ...]`.
   - `workflow_ops.py handoff` writes `.agents/ck/HANDOFF.md` + a dated archive under `artifacts/handoffs/YYYY-MM-DD/YYYYMMDDTHHMMSSffffffZ_handoff.md` (auto-indexed in `artifacts/handoffs/README.md`), sets `status: "HANDOFF_READY"` + `active_handoff` in `.agents/ck/context.json`, and prints a **Ready-to-Paste New-Window Starter Prompt**.
   - When the user opens a fresh chat window, `.agents/hooks.json` `SessionStart` automatically detects `HANDOFF_READY` and surfaces `.agents/ck/HANDOFF.md` in its injected $O(1)$ rehydration pointer. The next normal `workflow_ops.py log-turn` clears `active_handoff` automatically so stale handoffs never linger.
   - On any fresh session or after `/compact`, read `.agents/ck/HANDOFF.md` (if active), the top `3` lines of `artifacts/Conversations/README.md`, and `.agents/ck/context.json` ($t_0$).

## 2. Rolling 15 Checkpoints & Pre-Restore Validation
- `workflow_ops.py log-turn` maintains a FIFO ring buffer of up to `15` snapshots in `.agents/ck/history/context_YYYYMMDDTHHMMSSffffffZ_NNNN.json` (RFC 3339 UTC microsecond timestamps in JSON), copies the latest to `.agents/ck/context.json` ($t_0$), and renders `.agents/ck/CONTEXT.md`.
- **Zero Secrets:** Never store API keys, tokens, passwords, or PII in checkpoints or artifacts.
- **Pre-Restore Validation:**
  - *Valid:* Treat checkpoint fields as navigation hints verified against current disk state.
  - *Stale/Drifted:* If files changed after `saved_at`, mark `Needs Revalidation` and re-read source files.
  - *Corrupt/Unsupported:* Never silently overwrite; report truthfully and rebuild context from source/artifacts.
  - *Strict Approval Boundary:* Checkpoint `status` NEVER substitutes for a fresh `/approve`.

## 3. Archival, Tooling Hygiene & 7-Test No-Slop Logging
- Primary Intake (`@lead`) owns daily conversation logging via `python .agents/scripts/workflow_ops.py log-turn --title "..." --summary "..."`.
- Write `artifacts/` entries in `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` using relative paths only (`BOM=False`) and update `README.md` for every populated category (excluding disposable `artifacts/scratch/`). Record code notes in `artifacts/comments/YYYY-MM-DD/YYYYMMDD_comment_<topic>.md`, reusable local helpers in `artifacts/tools/` (indexed in `artifacts/tools/README.md`), and disposable one-off scripts in `artifacts/scratch/`.
- Apply **7-Test No-Slop**: state concrete *Mechanism*, avoid generic *Portability*, name the *Actor*, keep *One Idea* per bullet, maximize *Density*, put the *Decision-First*, and make next actions *Reader-Actionable*.

## 4. Essential CLI Operations
```bash
# Set user chat & artifacts language for first-time setup (creates backup automatically)
python .agents/scripts/workflow_ops.py set-language --lang "<Language>"

# Scan remaining {{PLACEHOLDERS}} across the workflow
python .agents/scripts/workflow_ops.py check-placeholders

# Pre-Action Backup with SHA-256 manifest
python .agents/scripts/workflow_ops.py backup --topic "<topic>" <files...>

# Generate -U1 diff against latest backup (works even without .git)
python .agents/scripts/workflow_ops.py diff --output "artifacts/diffs/YYYY-MM-DD/<topic>.diff"

# Generate a new-window handoff packet (.agents/ck/HANDOFF.md + artifacts/handoffs/)
python .agents/scripts/workflow_ops.py handoff --objective "<next objective>" --next "<step 1>"

# Audit AGENTS.md, 4 Agents, 4 Skills, hooks.json, scripts, workflows & artifacts
python .agents/scripts/verify_workflow.py
```
