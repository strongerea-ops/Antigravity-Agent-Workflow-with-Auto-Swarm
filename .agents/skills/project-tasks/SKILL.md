---
name: project-tasks
description: "Project-specific objectives, active task backlog, acceptance criteria, and domain constraints for {{PROJECT_NAME}}. Activate before planning, implementing, or verifying project tasks."
---

# Skill: project-tasks (`{{PROJECT_NAME}}`)

> **Setup Note:** Replace every `{{PLACEHOLDER}}` below with your project's real goals, tasks, and acceptance criteria. Run `python .agents/scripts/workflow_ops.py check-placeholders` to verify nothing was missed.

## 1. Project Mission & Objectives
- **Project Name:** `{{PROJECT_NAME}}`
- **Primary Objective:** `{{PROJECT_OBJECTIVE}}`
- **Technology Stack:** `{{TECH_STACK}}`
- **Primary Directories:** Source `{{SRC_DIR}}` | Tests `{{TEST_DIR}}`

## 2. Active Project Task Catalog
Add, reorder, or remove tasks as your roadmap evolves:

### Task 1 — `{{TASK_1_NAME}}`
- **Objective:** `{{TASK_1_OBJECTIVE}}`
- **Target Scope:** `{{SRC_DIR}}` / `{{TEST_DIR}}`
- **Acceptance Criteria:** `{{TASK_1_ACCEPTANCE}}`

### Task 2 — `{{TASK_2_NAME}}`
- **Objective:** `{{TASK_2_OBJECTIVE}}`
- **Target Scope:** `{{SRC_DIR}}` / `{{TEST_DIR}}`
- **Acceptance Criteria:** `{{TASK_2_ACCEPTANCE}}`

### Task 3 — `{{TASK_3_NAME}}`
- **Objective:** `{{TASK_3_OBJECTIVE}}`
- **Target Scope:** `{{SRC_DIR}}` / `{{TEST_DIR}}`
- **Acceptance Criteria:** `{{TASK_3_ACCEPTANCE}}`

## 3. Domain Constraints & Never Cut List
- **Domain Constraints (Hard Don'ts):** `{{DOMAIN_CONSTRAINTS}}`
- **High-Blast-Radius Modules:** `{{HIGH_BLAST_RADIUS_MODULES}}`
- **Never Cut List:** `{{NEVER_CUT_LIST}}`

## 4. Authoritative Verification Commands
- **Install / Setup:** `{{INSTALL_COMMAND}}`
- **Run / Dev:** `{{RUN_COMMAND}}`
- **Build:** `{{BUILD_COMMAND}}`
- **Test:** `{{TEST_COMMAND}}`
- **Lint / Typecheck:** `{{LINT_COMMAND}}`

## 5. Task Readiness Checklist
Before requesting `/approve` on any task above:
1. Map the task to concrete files, callers, and data/config contracts (`Static-confirmed`).
2. Confirm zero Conflict/Redundancy with existing modules or rules.
3. Define measurable acceptance criteria and rollback steps (`U1, U2...`).
