#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable Agent Workflow — Antigravity Lifecycle Hook Handler
Supports SessionStart, PreToolUse, PostToolUse, and Stop (opt-in) using
camelCase JSON stdin/stdout and Pure Python 3.10+ Standard Library.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]

ALLOW_PREFIXES = ("artifacts/", ".agents/ck/", "backup/", "scratch/")
BASE_PROTECTED_PREFIXES = (
    ".agents/rules/",
    ".agents/agents/",
    ".agents/skills/",
    ".agents/scripts/",
    ".agents/workflows/",
)
# Customize or replace {{SRC_DIR}} with your application source directory (e.g., "src/").
# Entries still containing "{{" are safely ignored until configured.
CUSTOM_PROTECTED_PREFIXES: Tuple[str, ...] = (
    "{{SRC_DIR}}",
)
PROTECTED_EXACT = {"AGENTS.md", ".agents/hooks.json"}

# Optional project-specific forbidden shell command regexes blocked at PreToolUse.
# Placeholder entries containing "{{" are safely ignored until customized.
FORBIDDEN_COMMAND_PATTERNS: List[Tuple[str, str]] = [
    (
        "{{FORBIDDEN_COMMAND_REGEX}}",
        "Command blocked by project forbidden-command policy in .agents/scripts/workflow_hooks.py",
    ),
]


def _read_stdin_payload(stdin_text: Optional[str] = None) -> Dict[str, Any]:
    raw = stdin_text if stdin_text is not None else sys.stdin.read()
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError as exc:
        print(f"[workflow_hooks] Invalid JSON on stdin: {exc}", file=sys.stderr)
        return {}


def _extract_tool_call(payload: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    tool_call = payload.get("toolCall")
    if not isinstance(tool_call, dict):
        tool_call = {}
    name = str(tool_call.get("name") or "").strip().lower()
    args = tool_call.get("args")
    if not isinstance(args, dict):
        args = {}
    return name, args


def _resolve_target_path(args: Dict[str, Any], repo_root: Path) -> Tuple[Optional[Path], Optional[str]]:
    raw_path = args.get("Path") or args.get("path") or args.get("TargetFile") or ""
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None, None
    candidate = Path(raw_path.strip())
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    resolved = candidate.resolve()
    try:
        rel_path = resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return resolved, None
    return resolved, rel_path


def _active_protected_prefixes(custom_prefixes: Sequence[str] = CUSTOM_PROTECTED_PREFIXES) -> Tuple[str, ...]:
    extra: List[str] = []
    for raw in custom_prefixes:
        cleaned = raw.strip().replace("\\", "/")
        if not cleaned or "{{" in cleaned or "}}" in cleaned:
            continue
        if not cleaned.endswith("/"):
            cleaned += "/"
        extra.append(cleaned)
    return BASE_PROTECTED_PREFIXES + tuple(extra)


def _is_protected_path(rel_path: str, custom_prefixes: Sequence[str] = CUSTOM_PROTECTED_PREFIXES) -> bool:
    if any(rel_path.startswith(prefix) for prefix in ALLOW_PREFIXES):
        return False
    if rel_path in PROTECTED_EXACT:
        return True
    return any(rel_path.startswith(prefix) for prefix in _active_protected_prefixes(custom_prefixes))


def _is_workflow_path(rel_path: str) -> bool:
    if rel_path in PROTECTED_EXACT:
        return True
    return any(rel_path.startswith(prefix) for prefix in BASE_PROTECTED_PREFIXES)


def _candidate_backup_roots(repo_root: Path) -> List[Path]:
    backup_base = repo_root / "backup"
    roots: List[Path] = []
    if backup_base.is_dir():
        roots.append(backup_base)
        project_scoped = backup_base / repo_root.name
        if project_scoped.is_dir():
            roots.append(project_scoped)
    return roots


def _has_today_backup(rel_path: str, repo_root: Path, today_str: Optional[str] = None) -> bool:
    date_prefix = today_str or datetime.now(timezone.utc).strftime("%Y%m%d")
    for backup_root in _candidate_backup_roots(repo_root):
        # Support both ISO 8601 Basic UTC (YYYYMMDDT*) and legacy (YYYYMMDD-*) backup folders.
        candidates = sorted(
            set(backup_root.glob(f"{date_prefix}T*")) | set(backup_root.glob(f"{date_prefix}-*")),
            reverse=True,
        )
        for folder in candidates:
            manifest_path = folder / "manifest.json"
            if not manifest_path.is_file():
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            files_map = manifest.get("files")
            if not isinstance(files_map, dict):
                continue
            for raw_key, entry in files_map.items():
                if str(raw_key).replace("\\", "/") != rel_path or not isinstance(entry, dict):
                    continue
                status = entry.get("status")
                if status == "absent":
                    return True
                if status == "backed_up":
                    backup_file = str(entry.get("backup_file") or "")
                    if backup_file and (folder / backup_file).is_file():
                        return True
    return False


def handle_session_start(payload: Dict[str, Any], repo_root: Optional[Path] = None) -> Dict[str, Any]:
    """Injects an O(1) checkpoint summary systemMessage if .agents/ck/context.json exists."""
    del payload  # Common metadata not required for local checkpoint lookup
    root = (repo_root or REPO_ROOT).resolve()
    ck_path = root / ".agents" / "ck" / "context.json"
    if not ck_path.is_file():
        return {}
    try:
        ck = json.loads(ck_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(ck, dict):
        return {}
    objective = str(ck.get("active_objective") or "").strip()
    status = str(ck.get("status") or "UNKNOWN").strip()
    saved_at = str(ck.get("saved_at") or "").strip()
    if not objective:
        return {}
    msg = (
        f"[O(1) Rehydration] Latest checkpoint ({saved_at}, status={status}): {objective}. "
        "Verify current files before acting; checkpoint status is never /approve."
    )
    return {
        "injectSteps": [
            {
                "systemMessage": {
                    "systemMessage": msg,
                }
            }
        ]
    }


def handle_pre_tool(
    payload: Dict[str, Any],
    repo_root: Optional[Path] = None,
    today_str: Optional[str] = None,
    custom_prefixes: Sequence[str] = CUSTOM_PROTECTED_PREFIXES,
    forbidden_patterns: Sequence[Tuple[str, str]] = FORBIDDEN_COMMAND_PATTERNS,
) -> Dict[str, str]:
    root = (repo_root or REPO_ROOT).resolve()
    tool_name, args = _extract_tool_call(payload)

    if tool_name in ("edit_file", "write_file"):
        _, rel_path = _resolve_target_path(args, root)
        if not rel_path or not _is_protected_path(rel_path, custom_prefixes=custom_prefixes):
            return {"decision": "allow"}
        if not _has_today_backup(rel_path, root, today_str=today_str):
            return {
                "decision": "deny",
                "reason": (
                    f"Missing Pre-Action Backup for {rel_path}. "
                    f'Run: python .agents/scripts/workflow_ops.py backup --topic <topic> "{rel_path}"'
                ),
            }
        return {"decision": "allow"}

    if tool_name == "run_command":
        cmd = str(args.get("CommandLine") or args.get("command") or "")
        for pattern, message in forbidden_patterns:
            if not pattern or "{{" in pattern or "}}" in pattern:
                continue
            try:
                if re.search(pattern, cmd, re.IGNORECASE):
                    return {"decision": "deny", "reason": message}
            except re.error as exc:
                print(f"[workflow_hooks] Invalid regex '{pattern}': {exc}", file=sys.stderr)
        return {"decision": "allow"}

    return {"decision": "allow"}


def handle_post_tool(payload: Dict[str, Any], repo_root: Optional[Path] = None) -> Dict[str, Any]:
    root = (repo_root or REPO_ROOT).resolve()
    tool_name, args = _extract_tool_call(payload)
    if tool_name in ("edit_file", "write_file"):
        resolved_path, rel_path = _resolve_target_path(args, root)
        if resolved_path and resolved_path.is_file() and rel_path and _is_workflow_path(rel_path):
            if str(SCRIPT_DIR) not in sys.path:
                sys.path.insert(0, str(SCRIPT_DIR))
            from verify_workflow import audit_workspace

            errors = audit_workspace(root)
            ck_dir = root / ".agents" / "ck"
            alert_file = ck_dir / "last_alert.log"
            if errors:
                ck_dir.mkdir(parents=True, exist_ok=True)
                ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                body = f"[{ts}] Workflow audit alert ({len(errors)} issue(s)):\n" + "\n".join(
                    f"  - {err}" for err in errors
                ) + "\n"
                alert_file.write_text(body, encoding="utf-8")
            else:
                alert_file.unlink(missing_ok=True)
    return {}


def handle_stop(payload: Dict[str, Any], repo_root: Optional[Path] = None) -> Dict[str, str]:
    """Opt-in Stop gate: blocks normal stop once if .agents/ck/last_alert.log exists."""
    if payload.get("continuationActive"):
        return {"decision": "stop"}
    reason = str(payload.get("terminationReason") or "NO_TOOL_CALL")
    if reason != "NO_TOOL_CALL":
        return {"decision": "stop"}
    if payload.get("fullyIdle") is False:
        return {"decision": "stop"}

    root = (repo_root or REPO_ROOT).resolve()
    alert_file = root / ".agents" / "ck" / "last_alert.log"
    if alert_file.is_file():
        return {
            "decision": "continue",
            "reason": (
                "Unresolved workflow audit alert found in .agents/ck/last_alert.log. "
                "Inspect the alert, fix the reported issue, and re-run verify_workflow.py."
            ),
        }
    return {"decision": "stop"}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Portable Agent Workflow — Hook Handler")
    parser.add_argument("phase", choices=["session-start", "pre-tool", "post-tool", "stop"])
    args = parser.parse_args(argv)
    payload = _read_stdin_payload()
    if args.phase == "session-start":
        result = handle_session_start(payload)
    elif args.phase == "pre-tool":
        result = handle_pre_tool(payload)
    elif args.phase == "post-tool":
        result = handle_post_tool(payload)
    else:
        result = handle_stop(payload)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
