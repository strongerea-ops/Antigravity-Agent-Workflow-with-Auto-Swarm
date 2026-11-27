# Commands, Hooks & Tooling Hygiene Rules

> **Scope:** Read when configuring [.agents/hooks.json](../hooks.json), running expanded workflow CLI commands (`rollback`, `prune`, `inspect`), managing `artifacts/` retention, or promoting reusable helper scripts. Core commands live in [AGENTS.md](../../AGENTS.md) §2.

## 1. Hook Runner CWD Contract & Built-In `PreToolUse` Guards
- Antigravity executes `.agents/hooks.json` commands with **`CWD = .agents/`**.
- All script paths inside `.agents/hooks.json` MUST resolve relative to `.agents/` (e.g., `scripts/workflow_hooks.py`).
- On Linux/macOS environments where `python` is not aliased to Python 3, switch `python` to `python3` inside `.agents/hooks.json` while keeping relative script paths intact.
- **Deterministic Built-In `PreToolUse` Guards (`workflow_hooks.py`):**
  - Blocks `edit_file`/`write_file` on protected workflow/source files if today's Pre-Action Backup is missing.
  - Blocks unauthorized Git branch creation (`git checkout -b/-B`, `git switch -c/--create`, `git branch <name>`) and destructive Git commands (`git reset --hard`, `git clean -f`, `git checkout -- .`).
  - Blocks automatic deletion commands targeting `artifacts/` (`rm`, `del`, `Remove-Item`, `shutil.rmtree`, `os.remove`, `.unlink(`) so user-managed reference files are never wiped automatically.
  - Evaluates optional project-specific regex patterns in `FORBIDDEN_COMMAND_PATTERNS`.

## 2. Expanded CLI Reference (`rollback`, `prune`, `inspect`)
```bash
python .agents/scripts/workflow_ops.py rollback --backup "<dir>" [--apply]  # Dry-run default; --apply restores (SHA-256) & removes absent
python .agents/scripts/workflow_ops.py prune --keep-days 30 [--apply]       # Backup-only (max 30d; auto-runs on backup; never touches artifacts/)
python .agents/scripts/workflow_ops.py inspect --mode quick                 # quick | full | tools-only (+ --tool, --fail-fast, --json, --report)
```

## 3. Tool Storage, Artifact Retention & Promotion Hygiene
- Check `artifacts/tools/README.md` before writing a new local helper script to avoid duplication.
- **Artifacts Are User-Managed Reference Materials (Never Auto-Delete):** Never automatically delete any file under `artifacts/`. If a document in `artifacts/` conflicts with current operations or rules, proactively notify the user and recommend how to address it (update, mark superseded, or let the user remove it).
- **No Workspace `artifacts/scratch/` Saves:** Never save one-off probes, disposable scripts, or temporary logs under workspace `artifacts/scratch/` (or root `scratch/`) — always use Antigravity's built-in per-session scratch folder (`<appDataDir>/brain/<conversation-id>/scratch/`) for temporary files.
- **Reusable Local Tools (`artifacts/tools/`):** Clean reusable diagnostic/inspection scripts to comply with Senior Invariants (`BOM=False`, relative paths, no hardcoded drive letters), save them under `artifacts/tools/`, and index them in `artifacts/tools/README.md`. They can be executed safely via `workflow_ops.py inspect --tool artifacts/tools/<script>.py`.
- **Core Production Workflow Tooling (`.agents/scripts/`):** Keep Git-tracked workflow, hook, verifier, and unit test scripts here (pure Python 3.10+ stdlib only).
- **Promotion Rule:** Clean and promote reusable scripts from session scratch into `artifacts/tools/`, and recurring invariant checks into the project's test suite or `.agents/scripts/`.
