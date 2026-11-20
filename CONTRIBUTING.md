# Contributing to Antigravity Agent Workflow with Auto-Swarm

Thank you for helping improve and evolve this portable Antigravity Agent Workflow! This guide explains how to propose changes, run automated checks, and keep the starter kit clean, truthful, and universally reusable.

---

## Ways to Contribute

- **Bug Fixes:** Fix issues in hooks (`workflow_hooks.py`), operations CLI (`workflow_ops.py`), verifier (`verify_workflow.py`), or workflow templates.
- **Capability Upgrades:** Add support for newly released Antigravity customization capabilities (hooks, `run_workflow`, `swarm`, MCP, plugins, automations) while keeping the starter kit lean.
- **Documentation & Translations:** Improve clarity in [MANUAL_EN.md](./MANUAL_EN.md), [MANUAL_TH.md](./MANUAL_TH.md), or add starter examples for specific ecosystems without polluting core project-agnostic files.

---

## Core Design Invariants (Please Keep Intact)

1. **Project-Agnostic Core:** Never hardcode domain-specific business logic, personal usernames, secrets, or local absolute paths into the starter kit. Use explicit `{{PLACEHOLDERS}}` instead.
2. **Zero External Dependencies:** All scripts under `.agents/scripts/` MUST use **Pure Python 3.10+ Standard Library** only so any project can run them immediately.
3. **Language Split & Manual Parity:**
   - Keep `README.md`, `AGENTS.md`, `.agents/`, scripts, and templates in **English**.
   - Keep [MANUAL_EN.md](./MANUAL_EN.md) (English) and [MANUAL_TH.md](./MANUAL_TH.md) (Thai) synchronized whenever adding commands, capabilities, or placeholders.
4. **Budget & Schema Constraints:**
   - `AGENTS.md` MUST stay $\le 24,000$ bytes (`UTF-8`, `BOM=False`).
   - Each `.agents/skills/<name>/SKILL.md` MUST stay $\le 300$ lines with matching YAML `name`.
   - Every `.agents/agents/<name>.md` MUST follow the **10-Element Agent Schema** (never put `swarm` in YAML `tools:`; keep `model` in `inherit`/`flash_lite`/`flash`/`pro`).
   - `.agents/hooks.json` script paths MUST resolve relative to `.agents/` (Antigravity Hook Runner executes with CWD = `.agents/`).
   - Never commit hardcoded drive letters, UTF-8 BOM, broken relative links, or code truncation placeholders (`// ... existing code ...`).

---

## Pull Request Workflow

1. **Fork** the repository and create a descriptive feature or fix branch from `main`.
2. Make the **smallest complete change** and update all cross-references (including `MANUAL_EN.md` / `MANUAL_TH.md` if behavior or placeholders change).
3. Add or update tests in [.agents/scripts/test_workflow_ops_and_hooks.py](./.agents/scripts/test_workflow_ops_and_hooks.py) when modifying Python scripts or hooks.
4. Run both verification commands locally before opening a Pull Request (both MUST exit `0`):
   ```bash
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. Open a Pull Request describing **what changed**, **why**, and the **exact verification output**.

---

## License

By contributing to this repository, you agree that your contributions will be licensed under the **GNU General Public License v3.0 (GPL-3.0)** ([LICENSE](./LICENSE)).
