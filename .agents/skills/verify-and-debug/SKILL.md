---
name: verify-and-debug
description: "Dynamic test execution (/test), Causal-Chain RCA debugging (/debug), Read-Only static diff auditing (/audit), Circuit Breaker N >= 3, and Compound Learning (/compound)."
---

# Skill: verify-and-debug

> **Active Agents:** `@verifier` (Read-Only QA & Static Audit) and `@lead` (Escalation, Circuit Breaker & Compound Learning Closure).

## 1. Dynamic Verification (`/test`)
1. **Preflight Check:** Confirm test environment isolation (no destructive production writes, no forbidden commands).
2. **Real Execution Only:** Run `{{TEST_COMMAND}}`, `{{LINT_COMMAND}}`, and `python .agents/scripts/verify_workflow.py` (plus `python -m unittest discover -s .agents/scripts -p "test_*.py" -v` when scripts change).
3. **Truthful Reporting:** Output exact command, pass/fail counts, exit code, verdict (`PASS / FAIL / PARTIAL / NOT RUN`), pre-existing failures separated clearly, and explicit `Untested Scope`. Never mock owned code to force a green test.

## 2. Systematic Debugging & Causal-Chain RCA (`/debug`)
When tests fail or bugs occur, do **not** guess-patch:
1. **Reproduce & Evidence:** Capture exact traceback, inputs, file:line, and observed vs. expected behavior.
2. **Hypothesis -> Prediction -> Check:** State a falsifiable hypothesis, predict what a targeted read/test will show, and verify.
3. **Causal Chain:** Trace `Trigger -> Intermediate State -> Root Cause -> Symptom` and fix at the root cause (never hide with broad `try-except` or dummy defaults).
4. **Attack the Premise ($N = 2$):** After `2` failed fix attempts on the same premise, stop and explicitly challenge the underlying assumption (wrong file, wrong runner, stale cache, mismatched contract, OS line endings).
5. **Circuit Breaker ($N \ge 3$):** After `3` consecutive failed cycles on the same root cause (reset on pass, new root cause, or environment failure), emit `HALT_CIRCUIT_BREAKER` to `@lead` and enter Explain-First mode immediately.

## 3. Read-Only Static Diff Audit (`/audit`)
1. Inspect `git diff -U1` (or `python .agents/scripts/workflow_ops.py diff` in non-Git repos) against approved scope.
2. Trace `Caller -> Changed Code -> Consumer/Side Effects` to verify 100% caller/test/config updates and no unwired parameters.
3. Check Never Cut List (`{{NEVER_CUT_LIST}}`), Zero-Mock, Zero In-Code Comments (notes in `artifacts/comments/`, allowing only high-importance exceptions/directives), crash-hiding `try-except`, `BOM=False`, no hardcoded drive letters, no truncation ellipses, and clean `.agents/ck/last_alert.log`.
4. Issue `Static Audit: PASS / FAIL / PARTIAL / NOT AUDITED` with severity-ranked findings (`Critical`, `Major`, `Minor`) back to `@lead`.

## 4. Compound Learning (`/compound`)
After closing a non-trivial bug or recurring architectural pitfall with `PASS`, permanently prevent recurrence using the **cheapest effective guard first**:
1. **Automated Test or Linter Rule (Preferred):** Add a regression test in `{{TEST_DIR}}` or a check in `.agents/scripts/verify_workflow.py` / `workflow_hooks.py`.
2. **Operational Rule / Skill Update:** Update `.agents/rules/rules.md` or a skill only for constraints a linter cannot enforce.
3. **Solution / Lesson Document:** Record under `artifacts/solutions/<category>/<slug>.md` or `artifacts/Lessons/YYYY-MM-DD/` and index its `README.md`.
