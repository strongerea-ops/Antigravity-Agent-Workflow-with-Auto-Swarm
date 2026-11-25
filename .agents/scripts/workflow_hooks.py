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
from datetime import date, datetime, timezone
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


CHAT_LANG_PLACEHOLDER = "{{CHAT_AND_ARTIFACTS_LANGUAGE}}"
DATE_ISO_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
MD_LINK_LABEL_RE = re.compile(r"\[([^\]]+)\]")
RESOLVED_BUG_MARKERS = (
    "🟢",
    "✅",
    "resolved",
    "closed",
    "fixed",
    "แก้ไขสมบูรณ์",
    "แก้ไขแล้ว",
)
UNRESOLVED_BUG_MARKERS = (
    "🔴",
    "🟡",
    "open",
    "unresolved",
    "pending",
    "fail",
    "รอแก้ไข",
    "รอแก้",
    "เปิดไว้",
)


def _needs_first_time_language_setup(repo_root: Path) -> bool:
    agents_md = repo_root / "AGENTS.md"
    if not agents_md.is_file():
        return False
    try:
        return CHAT_LANG_PLACEHOLDER in agents_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def _find_stale_recent_bug_reports(
    repo_root: Path,
    today: Optional[date] = None,
    min_age_days: int = 3,
    max_age_days: int = 7,
) -> List[str]:
    """Scans artifacts/bug-reports/README.md for unresolved reports aged (min_age_days, max_age_days]."""
    readme_path = repo_root / "artifacts" / "bug-reports" / "README.md"
    if not readme_path.is_file():
        return []
    try:
        content = readme_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[workflow_hooks] Failed reading {readme_path}: {exc}", file=sys.stderr)
        return []

    ref_day = today or datetime.now(timezone.utc).date()
    stale_items: List[str] = []
    seen: set[str] = set()

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        date_match = DATE_ISO_RE.search(line)
        if not date_match:
            continue
        try:
            entry_date = date.fromisoformat(date_match.group(1))
        except ValueError:
            continue
        age_days = (ref_day - entry_date).days
        if not (min_age_days < age_days <= max_age_days):
            continue

        lowered = line.lower()
        if any(marker in lowered for marker in RESOLVED_BUG_MARKERS):
            continue
        if not any(marker in lowered for marker in UNRESOLVED_BUG_MARKERS):
            continue

        label = ""
        if line.startswith("|"):
            cells = [c.strip().strip("`") for c in line.split("|")]
            if len(cells) >= 3 and cells[2]:
                label = cells[2]
        if not label:
            link_match = MD_LINK_LABEL_RE.search(line)
            if link_match:
                label = link_match.group(1).strip()
        if not label:
            label = line[:60]

        entry_summary = f"{entry_date.isoformat()} ({age_days}d): {label}"
        if entry_summary not in seen:
            seen.add(entry_summary)
            stale_items.append(entry_summary)

    return stale_items


def handle_session_start(
    payload: Dict[str, Any],
    repo_root: Optional[Path] = None,
    today: Optional[date] = None,
) -> Dict[str, Any]:
    """Injects first-time language onboarding, O(1) checkpoint/handoff summary, and 3-7d bug reminders on SessionStart."""
    del payload
    root = (repo_root or REPO_ROOT).resolve()
    parts: List[str] = []

    if _needs_first_time_language_setup(root):
        parts.append(
            f"[First-Time Setup — Language Selection] {CHAT_LANG_PLACEHOLDER} is not configured yet. "
            "Before proceeding with other tasks, present a clickable ask_question menu asking the user to choose "
            "their preferred language for chat replies and artifacts/ (e.g., English, Thai, Japanese, Chinese, or Other), "
            'then apply it with: python .agents/scripts/workflow_ops.py set-language --lang "<Language>".'
        )

    stale_bugs = _find_stale_recent_bug_reports(root, today=today)
    bug_note = ""
    if stale_bugs:
        bug_note = (
            f" Unresolved recent bug reports (3-7d): {'; '.join(stale_bugs)} "
            "— remind the user to address them."
        )

    ck_path = root / ".agents" / "ck" / "context.json"
    ck: Dict[str, Any] = {}
    if ck_path.is_file():
        try:
            loaded = json.loads(ck_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                ck = loaded
        except (OSError, json.JSONDecodeError):
            ck = {}

    objective = str(ck.get("active_objective") or "").strip()
    if objective:
        status = str(ck.get("status") or "UNKNOWN").strip()
        saved_at = str(ck.get("saved_at") or "").strip()
        active_handoff = str(ck.get("active_handoff") or "").strip()
        handoff_note = ""
        if status == "HANDOFF_READY" and active_handoff and (root / active_handoff).is_file():
            handoff_note = (
                f" Active handoff packet waiting at `{active_handoff}` — "
                "read it first to resume in this new window."
            )
        parts.append(
            f"[O(1) Rehydration] Latest checkpoint ({saved_at}, status={status}): {objective}.{handoff_note}{bug_note} "
            "Verify current files before acting; checkpoint/handoff status is never /approve."
        )
    elif bug_note:
        parts.append(f"[Bug Reminder]{bug_note}")

    if not parts:
        return {}
    return {
        "injectSteps": [
            {
                "systemMessage": {
                    "systemMessage": " ".join(parts),
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
