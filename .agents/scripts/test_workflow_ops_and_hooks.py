#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic unit tests for workflow_hooks.py, workflow_ops.py, and verify_workflow.py.
Uses isolated temporary directories so real workspace files are never mutated.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_ROOT = Path(__file__).resolve().parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import verify_workflow  # noqa: E402
import workflow_hooks  # noqa: E402
import workflow_ops  # noqa: E402


class TestWorkflowOps(unittest.TestCase):
    def test_backup_and_diff_existing_and_new_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "AGENTS.md"
            target.write_text("# Old\nline1\n", encoding="utf-8")

            bdir = workflow_ops.run_backup(
                topic="sample_change",
                files=["AGENTS.md", "new_file.txt"],
                repo_root=root,
            )
            manifest = json.loads((bdir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["files"]["AGENTS.md"]["status"], "backed_up")
            self.assertEqual(manifest["files"]["new_file.txt"]["status"], "absent")

            target.write_text("# New\nline1\n", encoding="utf-8")
            (root / "new_file.txt").write_text("hello\n", encoding="utf-8")

            diff_out = root / "artifacts" / "diffs" / "sample.diff"
            diff_text = workflow_ops.run_diff(backup_dir=bdir, output=diff_out, repo_root=root)
            self.assertTrue(diff_out.is_file())
            self.assertIn("-# Old", diff_text)
            self.assertIn("+# New", diff_text)
            self.assertIn("+hello", diff_text)
            with tempfile.TemporaryDirectory() as ext_tmp:
                ext_out = Path(ext_tmp) / "outside.diff"
                workflow_ops.run_diff(backup_dir=bdir, output=ext_out, repo_root=root)
                self.assertTrue(ext_out.is_file())

    def test_log_turn_and_rolling_15_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for idx in range(17):
                workflow_ops.run_log_turn(
                    title=f"Turn {idx}",
                    summary=f"Summary {idx}",
                    touched=[f"src/file_{idx}.py"],
                    repo_root=root,
                )
            history = list((root / ".agents" / "ck" / "history").glob("context_*.json"))
            self.assertEqual(len(history), workflow_ops.MAX_CHECKPOINTS)
            ck = json.loads((root / ".agents" / "ck" / "context.json").read_text(encoding="utf-8"))
            self.assertEqual(ck["active_objective"], "Turn 16")
            self.assertTrue((root / ".agents" / "ck" / "CONTEXT.md").is_file())
            self.assertTrue((root / "artifacts" / "Conversations" / "README.md").is_file())

    def test_save_checkpoint_burst_same_second_fifo_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for idx in range(20):
                workflow_ops.save_checkpoint(objective=f"Burst {idx}", repo_root=root)
            history = sorted((root / ".agents" / "ck" / "history").glob("context_*.json"))
            self.assertEqual(len(history), workflow_ops.MAX_CHECKPOINTS)
            objectives = [json.loads(p.read_text(encoding="utf-8"))["active_objective"] for p in history]
            self.assertEqual(objectives, [f"Burst {i}" for i in range(5, 20)])
            ck = json.loads((root / ".agents" / "ck" / "context.json").read_text(encoding="utf-8"))
            self.assertEqual(ck["active_objective"], "Burst 19")
            ctx_md = (root / ".agents" / "ck" / "CONTEXT.md").read_text(encoding="utf-8")
            self.assertIn("Burst 19", ctx_md)
            self.assertIn("Burst 5", ctx_md)
            self.assertNotIn("Burst 4", ctx_md)

    def test_check_placeholders_detects_and_clears(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# {{PROJECT_NAME}}\n", encoding="utf-8")
            self.assertEqual(workflow_ops.run_check_placeholders(repo_root=root, fail_on_found=True), 1)
            (root / "AGENTS.md").write_text("# Real Project\n", encoding="utf-8")
            self.assertEqual(workflow_ops.run_check_placeholders(repo_root=root, fail_on_found=True), 0)


class TestWorkflowHooks(unittest.TestCase):
    def test_session_start_graceful_empty_and_rehydration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(workflow_hooks.handle_session_start({}, repo_root=root), {})
            workflow_ops.save_checkpoint(objective="Finish API schema", status="IN_PROGRESS", repo_root=root)
            out = workflow_hooks.handle_session_start({}, repo_root=root)
            self.assertIn("injectSteps", out)
            msg = out["injectSteps"][0]["systemMessage"]["systemMessage"]
            self.assertIn("Finish API schema", msg)

    def test_pre_tool_backup_and_custom_src_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# Guide\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")

            # artifacts/ always allowed without backup
            art_payload = {"toolCall": {"name": "write_file", "args": {"Path": "artifacts/notes.md"}}}
            self.assertEqual(workflow_hooks.handle_pre_tool(art_payload, repo_root=root)["decision"], "allow")

            # AGENTS.md denied without backup
            deny_payload = {"toolCall": {"name": "edit_file", "args": {"Path": "AGENTS.md"}}}
            self.assertEqual(workflow_hooks.handle_pre_tool(deny_payload, repo_root=root)["decision"], "deny")

            # Custom src/ denied once configured
            src_payload = {"toolCall": {"name": "edit_file", "args": {"Path": "src/app.py"}}}
            self.assertEqual(
                workflow_hooks.handle_pre_tool(src_payload, repo_root=root, custom_prefixes=("src/",))["decision"],
                "deny",
            )

            # Allowed after backup
            workflow_ops.run_backup(topic="edit_agents", files=["AGENTS.md", "src/app.py"], repo_root=root)
            self.assertEqual(workflow_hooks.handle_pre_tool(deny_payload, repo_root=root)["decision"], "allow")
            self.assertEqual(
                workflow_hooks.handle_pre_tool(src_payload, repo_root=root, custom_prefixes=("src/",))["decision"],
                "allow",
            )

    def test_pre_tool_forbidden_command_ignores_placeholder_and_blocks_real_regex(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cmd_payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": "pytest legacy_pkg"}}}
            # Default unfilled placeholder must not block
            self.assertEqual(workflow_hooks.handle_pre_tool(cmd_payload, repo_root=root)["decision"], "allow")
            # Active regex must deny
            res = workflow_hooks.handle_pre_tool(
                cmd_payload,
                repo_root=root,
                forbidden_patterns=[(r"\bpytest\s+legacy_pkg\b", "Use unittest instead")],
            )
            self.assertEqual(res["decision"], "deny")
            self.assertIn("unittest", res["reason"])

    def test_stop_hook_respects_continuation_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            alert = root / ".agents" / "ck" / "last_alert.log"
            alert.parent.mkdir(parents=True, exist_ok=True)
            # Clean state -> stop
            self.assertEqual(workflow_hooks.handle_stop({"terminationReason": "NO_TOOL_CALL"}, repo_root=root)["decision"], "stop")
            # Alert present + first stop -> continue
            alert.write_text("alert\n", encoding="utf-8")
            self.assertEqual(
                workflow_hooks.handle_stop(
                    {"terminationReason": "NO_TOOL_CALL", "continuationActive": False, "fullyIdle": True},
                    repo_root=root,
                )["decision"],
                "continue",
            )
            # continuationActive=True -> must stop to prevent infinite loop
            self.assertEqual(
                workflow_hooks.handle_stop(
                    {"terminationReason": "NO_TOOL_CALL", "continuationActive": True, "fullyIdle": True},
                    repo_root=root,
                )["decision"],
                "stop",
            )


class TestVerifyWorkflow(unittest.TestCase):
    def test_template_root_passes_audit(self) -> None:
        errors = verify_workflow.audit_workspace(TEMPLATE_ROOT)
        self.assertEqual(errors, [], f"Unexpected audit errors: {errors}")

    def test_audit_catches_bom_and_drive_letter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".agents" / "skills").mkdir(parents=True)
            bad_drive = chr(67) + ":\\secret\\path"
            (root / "AGENTS.md").write_bytes(b"\xef\xbb\xbf# Bad\n" + bad_drive.encode("utf-8") + b"\n")
            errors = verify_workflow.audit_workspace(root)
            self.assertTrue(any("UTF-8 BOM" in e for e in errors))
            self.assertTrue(any("hardcoded drive letter" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
