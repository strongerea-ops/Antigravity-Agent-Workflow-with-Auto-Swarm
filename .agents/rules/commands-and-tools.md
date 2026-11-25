# Commands, Hooks & Tooling Hygiene Rules

> **Scope:** Read when configuring [.agents/hooks.json](../hooks.json), running workflow CLI commands, or creating/promoting local helper scripts. Core commands live in [AGENTS.md](../../AGENTS.md) §2.

## 1. Hook Runner CWD Contract
- Antigravity executes `.agents/hooks.json` commands with **`CWD = .agents/`**.
- All script paths inside `.agents/hooks.json` MUST resolve relative to `.agents/` (e.g., `scripts/workflow_hooks.py`).
- On Linux/macOS environments where `python` is not aliased to Python 3, switch `python` to `python3` inside `.agents/hooks.json` while keeping relative script paths intact.

## 2. Tool Storage & Promotion Hygiene
- Check `artifacts/tools/README.md` before writing a new local helper script to avoid duplication.
- **Reusable Local Tools (`artifacts/tools/`):** Store reusable diagnostic, inspection, and helper scripts here; follow Senior Invariants (`BOM=False`, relative paths, no hardcoded drive letters) and immediately index them in `artifacts/tools/README.md` (name, purpose, CLI command, status).
- **Disposable Scratch (`artifacts/scratch/`):** Store one-off reproductions, ad-hoc probes, and temporary `.log` outputs here (safe to delete anytime; excluded from `verify_workflow.py` catalog parity and ignored by `.gitignore`; do not leave disposable scripts at repo root).
- **Core Production Workflow Tooling (`.agents/scripts/`):** Keep Git-tracked workflow, hook, verifier, and unit test scripts here (pure Python 3.10+ stdlib only).
- **Promotion Rule:** Clean and promote reusable scripts from `artifacts/scratch/` into `artifacts/tools/`, and recurring invariant checks into the project's test suite or `.agents/scripts/`.
