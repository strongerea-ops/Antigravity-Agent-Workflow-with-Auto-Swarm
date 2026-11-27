#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable Agent Workflow — Unified Operations CLI
Pure Python 3.10+ Standard Library only.
Commands:
  set-language        Configure {{CHAT_AND_ARTIFACTS_LANGUAGE}} for first-time setup (with backup)
  backup              Pre-Action microsecond backup with SHA-256 manifest.json (auto-prunes >30d backups)
  diff                Unified diff (-U1) against backup manifest (works without .git)
  rollback            Preview or restore files & remove absent entries from a backup manifest (SHA-256 verified)
  prune               Preview or delete backup/ entries older than 30 days (never touches artifacts/)
  inspect             Run unified workflow health gates (+ optional --tool scripts under artifacts/tools/)
  log-turn            Append daily conversation log, update README, rotate Rolling 15 Checkpoints
  handoff             Generate new-window handoff packet (.agents/ck/HANDOFF.md + artifacts/handoffs/)
  check-placeholders  Scan workflow templates for remaining {{PLACEHOLDER}} tokens
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_CHECKPOINTS = 15
BACKUP_MAX_RETENTION_DAYS = 30
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
ALLOWED_INSPECT_SCRIPT_ROOTS: Tuple[Tuple[str, ...], ...] = (
    ("artifacts", "tools"),
    (".agents", "scripts"),
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_rfc3339_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _format_basic_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _sanitize_slug(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", text.strip())
    return cleaned.strip("_") or "backup"


def _normalize_rel_path(file_path: str, target_root: Path) -> str:
    candidate = Path(file_path)
    if not candidate.is_absolute():
        candidate = target_root / candidate
    resolved = candidate.resolve()
    return resolved.relative_to(target_root.resolve()).as_posix()


def run_backup(
    topic: str,
    files: List[str],
    desc: Optional[str] = None,
    repo_root: Optional[Path] = None,
    auto_prune_days: Optional[int] = BACKUP_MAX_RETENTION_DAYS,
) -> Path:
    """Creates backup/YYYYMMDDTHHMMSSffffffZ_<topic>/ with RFC 3339 UTC manifest.json and prunes backups older than 30 days."""
    root = (repo_root or REPO_ROOT).resolve()
    now = _utc_now()
    ts_basic = _format_basic_utc(now)
    ts_iso = _format_rfc3339_utc(now)
    slug = _sanitize_slug(topic)
    backup_base = root / "backup"
    backup_base.mkdir(parents=True, exist_ok=True)
    backup_dir = backup_base / f"{ts_basic}_{slug}"
    seq = 1
    while backup_dir.exists():
        backup_dir = backup_base / f"{ts_basic}_{seq:02d}_{slug}"
        seq += 1
    backup_dir.mkdir(parents=True, exist_ok=True)

    manifest_files: Dict[str, Dict[str, object]] = {}
    used_names = set()

    for raw_path in files:
        rel_path = _normalize_rel_path(raw_path, root)
        src_path = root / rel_path
        if src_path.is_file():
            backup_name = src_path.name
            if backup_name in used_names:
                backup_name = rel_path.replace("/", "__")
            used_names.add(backup_name)
            shutil.copy2(src_path, backup_dir / backup_name)
            data = src_path.read_bytes()
            manifest_files[rel_path] = {
                "status": "backed_up",
                "backup_file": backup_name,
                "sha256": hashlib.sha256(data).hexdigest(),
                "size": len(data),
            }
        else:
            manifest_files[rel_path] = {"status": "absent"}

    manifest = {
        "project": root.name,
        "timestamp": ts_iso,
        "description": desc or f"Pre-Action Backup ({slug})",
        "files": manifest_files,
    }
    (backup_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"[Backup] Created {backup_dir.relative_to(root).as_posix()} ({len(manifest_files)} entries)")
    if auto_prune_days is not None:
        run_prune(keep_days=auto_prune_days, apply=True, repo_root=root, quiet_if_empty=True)
    return backup_dir


def _find_latest_backup(repo_root: Path) -> Path:
    backup_base = repo_root / "backup"
    if not backup_base.is_dir():
        raise FileNotFoundError(f"No backup directory found under {repo_root}")
    candidates = [
        d for d in sorted(backup_base.iterdir()) if d.is_dir() and (d / "manifest.json").is_file()
    ]
    if not candidates:
        raise FileNotFoundError(f"No backup manifest.json found under {backup_base}")
    return candidates[-1]


def run_diff(
    backup_dir: Optional[Path] = None,
    output: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> str:
    """Generates unified diff (-U1) against a Pre-Action Backup manifest."""
    root = (repo_root or REPO_ROOT).resolve()
    bdir = backup_dir.resolve() if backup_dir else _find_latest_backup(root)
    manifest = json.loads((bdir / "manifest.json").read_text(encoding="utf-8"))

    diff_lines: List[str] = []
    for rel_path, entry in manifest.get("files", {}).items():
        status = entry.get("status")
        old_lines: List[str] = []
        from_label = f"a/{rel_path}"
        if status == "backed_up":
            bf = bdir / str(entry.get("backup_file", ""))
            if bf.is_file():
                old_lines = bf.read_text(encoding="utf-8", errors="replace").splitlines()
        elif status == "absent":
            from_label = "/dev/null"

        cur_file = root / rel_path
        new_lines: List[str] = []
        to_label = f"b/{rel_path}"
        if cur_file.is_file():
            new_lines = cur_file.read_text(encoding="utf-8", errors="replace").splitlines()
        else:
            to_label = "/dev/null"

        diff_lines.extend(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=from_label,
                tofile=to_label,
                n=1,
                lineterm="",
            )
        )

    diff_text = ("\n".join(diff_lines) + "\n") if diff_lines else ""
    if output is not None:
        out_path = (output if output.is_absolute() else root / output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(diff_text, encoding="utf-8")
        try:
            display_out = out_path.relative_to(root).as_posix()
        except ValueError:
            display_out = out_path.as_posix()
        print(f"[Diff] Wrote {len(diff_lines)} lines to {display_out}")
    elif diff_text:
        print(diff_text, end="")
    else:
        print(f"[Diff] No differences vs {bdir.name}")
    return diff_text


def _render_context_markdown(history_items: List[Dict[str, Any]], updated_at: str) -> str:
    lines = [
        "# Durable Context Checkpoints (Rolling 15 Snapshots)",
        "",
        f"- **Last Updated:** {updated_at}",
        f"- **Architecture:** Rolling FIFO Ring Buffer (max {MAX_CHECKPOINTS} checkpoints)",
        "- **Active Pointer:** `.agents/ck/context.json` (always reflects $t_0$)",
        "- **History:** `.agents/ck/history/` (O(1) context rollback)",
        "",
        "---",
        "",
        "## Recent Trajectory (Latest 15 Turns)",
        "",
        "| Checkpoint | Time (UTC) | Active Objective | Files | Status |",
        "|---|---|---|---|---|",
    ]
    for idx, item in enumerate(history_items):
        label = "**$t_0$ (Current)**" if idx == 0 else f"**$t_{{-{idx}}}$**"
        ts_raw = str(item.get("saved_at", ""))
        time_part = ts_raw.split("T", 1)[1] if "T" in ts_raw else ts_raw
        obj = str(item.get("active_objective", "-")).replace("|", "\\|")
        touched = item.get("touched_files") or []
        if touched:
            extra = f" (+{len(touched) - 1} more)" if len(touched) > 1 else ""
            files_col = f"`{touched[0]}`{extra}"
        else:
            files_col = "-"
        status = str(item.get("status", "-")).replace("|", "\\|")
        lines.append(f"| {label} | `{time_part}` | {obj} | {files_col} | {status} |")
    lines.append("")
    return "\n".join(lines)


def save_checkpoint(
    objective: str,
    status: str = "COMPLETED",
    touched_files: Optional[List[str]] = None,
    key_decisions: Optional[List[str]] = None,
    pending_next_steps: Optional[List[str]] = None,
    active_handoff: Optional[str] = None,
    repo_root: Optional[Path] = None,
) -> Path:
    """Saves a checkpoint snapshot using RFC 3339 UTC microsecond precision and Rolling 15 FIFO."""
    root = (repo_root or REPO_ROOT).resolve()
    ck_dir = root / ".agents" / "ck"
    history_dir = ck_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    now = _utc_now()
    saved_at = _format_rfc3339_utc(now)
    stamp = _format_basic_utc(now)

    payload: Dict[str, Any] = {
        "schema_version": "1.2.0",
        "saved_at": saved_at,
        "project": root.name,
        "active_objective": objective,
        "status": status,
        "key_decisions": key_decisions or [],
        "touched_files": touched_files or [],
        "pending_next_steps": pending_next_steps or [],
    }
    if active_handoff:
        payload["active_handoff"] = active_handoff

    # Monotonic ISO 8601 UTC microsecond + 4-digit sequence prevents collisions and FIFO self-deletion.
    prefix = f"context_{stamp}_"
    same_tick = sorted(history_dir.glob(f"{prefix}*.json"))
    next_seq = 0
    if same_tick:
        tail = same_tick[-1].stem.rsplit("_", 1)[-1]
        if tail.isdigit():
            next_seq = int(tail) + 1
    history_file = history_dir / f"{prefix}{next_seq:04d}.json"

    history_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    all_history = sorted(history_dir.glob("context_*.json"))
    while len(all_history) > MAX_CHECKPOINTS:
        drop_idx = 1 if all_history[0] == history_file else 0
        all_history.pop(drop_idx).unlink(missing_ok=True)

    shutil.copy2(history_file, ck_dir / "context.json")

    recent_items: List[Dict[str, Any]] = []
    for path in reversed(all_history):
        try:
            recent_items.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue

    (ck_dir / "CONTEXT.md").write_text(
        _render_context_markdown(recent_items, saved_at), encoding="utf-8"
    )
    return history_file


def _insert_readme_bullet(readme_path: Path, bullet: str, default_heading: str = "# Conversations Vault") -> None:
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    if not readme_path.exists():
        readme_path.write_text(f"{default_heading}\n\n{bullet}\n", encoding="utf-8")
        return
    lines = readme_path.read_text(encoding="utf-8").splitlines()
    insert_idx = 0
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("# "):
            insert_idx = idx + 1
            break
    new_lines = lines[:insert_idx] + ["", bullet]
    tail = lines[insert_idx:]
    if tail and tail[0].strip() != "":
        new_lines.append("")
    new_lines.extend(tail)
    readme_path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")


def run_log_turn(
    title: str,
    summary: str,
    objective: Optional[str] = None,
    status: str = "COMPLETED",
    touched: Optional[List[str]] = None,
    decisions: Optional[List[str]] = None,
    next_steps: Optional[List[str]] = None,
    test_status: Optional[str] = None,
    role: str = "[👑 @lead]",
    repo_root: Optional[Path] = None,
) -> Dict[str, str]:
    """Appends a turn record, updates Conversations/README.md, and saves a checkpoint."""
    root = (repo_root or REPO_ROOT).resolve()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    ymd = now.strftime("%Y%m%d")

    conv_dir = root / "artifacts" / "Conversations" / date_str
    conv_dir.mkdir(parents=True, exist_ok=True)
    conv_file = conv_dir / f"{ymd}_conversations.md"

    touched_list = touched or []
    decisions_list = decisions or []
    next_list = next_steps or []
    effective_test_status = test_status or "No tests executed in this turn"

    entry_lines = [
        f"## Topic: {title}",
        f"- **Primary Intake:** `{role}`",
        f"- **Test Status:** {effective_test_status}",
    ]
    if touched_list:
        entry_lines.append("- **Touched Files:**")
        for item in touched_list:
            entry_lines.append(f"  - `{item}`")
    entry_lines.extend(["", "### Summary", summary])
    if decisions_list:
        entry_lines.extend(["", "### Key Decisions"])
        for dec in decisions_list:
            entry_lines.append(f"- {dec}")
    if next_list:
        entry_lines.extend(["", "### Next Steps"])
        for nxt in next_list:
            entry_lines.append(f"- {nxt}")

    entry_block = "\n".join(entry_lines) + "\n"
    if conv_file.exists():
        existing = conv_file.read_text(encoding="utf-8").rstrip()
        updated = f"{existing}\n\n---\n\n{entry_block}" if existing else entry_block
    else:
        updated = f"# Conversation Log ({date_str})\n\n{entry_block}"
    conv_file.write_text(updated, encoding="utf-8")

    readme_path = root / "artifacts" / "Conversations" / "README.md"
    bullet = f"- {date_str} — {role}: [{title}](./{date_str}/{ymd}_conversations.md) — {summary}"
    _insert_readme_bullet(readme_path, bullet)

    history_file = save_checkpoint(
        objective=objective or title,
        status=status,
        touched_files=touched_list,
        key_decisions=decisions_list,
        pending_next_steps=next_list,
        repo_root=root,
    )
    print(
        f"[LogTurn] Updated {conv_file.relative_to(root).as_posix()} "
        f"and {readme_path.relative_to(root).as_posix()}"
    )
    return {
        "conversation_file": str(conv_file),
        "readme_file": str(readme_path),
        "checkpoint_file": str(history_file),
    }


def run_handoff(
    objective: str,
    summary: Optional[str] = None,
    completed: Optional[List[str]] = None,
    settled: Optional[List[str]] = None,
    next_steps: Optional[List[str]] = None,
    blockers: Optional[List[str]] = None,
    touched: Optional[List[str]] = None,
    repo_root: Optional[Path] = None,
) -> Dict[str, str]:
    """Generates a new-window handoff packet (.agents/ck/HANDOFF.md + artifacts/handoffs/) and marks HANDOFF_READY."""
    root = (repo_root or REPO_ROOT).resolve()
    now = _utc_now()
    ts_iso = _format_rfc3339_utc(now)
    ts_basic = _format_basic_utc(now)
    date_str = now.strftime("%Y-%m-%d")

    handoff_dir = root / "artifacts" / "handoffs" / date_str
    handoff_dir.mkdir(parents=True, exist_ok=True)
    handoff_file = handoff_dir / f"{ts_basic}_handoff.md"
    seq = 1
    while handoff_file.exists():
        handoff_file = handoff_dir / f"{ts_basic}_{seq:02d}_handoff.md"
        seq += 1

    completed_list = completed or []
    settled_list = settled or []
    next_list = next_steps or ["Continue from the active objective after verifying disk state"]
    blockers_list = blockers or []
    touched_list = touched or []

    lines: List[str] = [
        "# Session Handoff Packet",
        "",
        f"- **Generated (UTC):** `{ts_iso}`",
        f"- **Project:** `{root.name}`",
        f"- **Active Objective:** {objective}",
        "- **Status:** `HANDOFF_READY` *(verify disk state before editing; handoff never equals `/approve`)*",
        "",
    ]
    if summary:
        lines.extend(["## Context Summary", summary, ""])
    lines.append("## Completed & Verified")
    lines.extend([f"- {item}" for item in completed_list] or ["- None recorded"])
    lines.extend(["", "## Key Touched Files"])
    lines.extend([f"- `{item}`" for item in touched_list] or ["- None recorded"])
    lines.extend(["", "## Session-Settled Decisions (`session-settled:`)"])
    lines.extend([f"- {item}" for item in settled_list] or ["- None recorded"])
    lines.extend(["", "## Pending Next Steps"])
    lines.extend([f"- {item}" for item in next_list])
    lines.extend(["", "## Open Risks, Blockers & Untested Scope"])
    lines.extend([f"- {item}" for item in blockers_list] or ["- None recorded"])
    lines.extend(
        [
            "",
            "## Ready-to-Paste New-Window Starter Prompt",
            "```text",
            f"Resume from handoff: read `.agents/ck/HANDOFF.md`, `.agents/ck/context.json`, and the top 3 lines of `artifacts/Conversations/README.md`.",
            f"Active objective: {objective}",
            "Verify current files on disk before proposing edits (handoff status is not /approve).",
            "```",
            "",
        ]
    )
    content = "\n".join(lines)
    handoff_file.write_text(content, encoding="utf-8")

    active_pointer = root / ".agents" / "ck" / "HANDOFF.md"
    active_pointer.parent.mkdir(parents=True, exist_ok=True)
    active_pointer.write_text(content, encoding="utf-8")

    handoffs_readme = root / "artifacts" / "handoffs" / "README.md"
    rel_from_cat = handoff_file.relative_to(root / "artifacts" / "handoffs").as_posix()
    bullet = f"- {date_str} (`{ts_iso}`) — [{objective}](./{rel_from_cat})"
    _insert_readme_bullet(handoffs_readme, bullet, default_heading="# Session Handoffs Vault")

    root_art_readme = root / "artifacts" / "README.md"
    if root_art_readme.is_file():
        art_text = root_art_readme.read_text(encoding="utf-8")
        if "handoffs" not in art_text:
            art_text = art_text.rstrip() + "\n- [handoffs](./handoffs/README.md) — New-window session handoff packets (`/handoff`)\n"
            root_art_readme.write_text(art_text, encoding="utf-8")

    history_file = save_checkpoint(
        objective=objective,
        status="HANDOFF_READY",
        touched_files=touched_list,
        key_decisions=settled_list,
        pending_next_steps=next_list,
        active_handoff=".agents/ck/HANDOFF.md",
        repo_root=root,
    )
    rel_handoff = handoff_file.relative_to(root).as_posix()
    print(f"[Handoff] Created {rel_handoff} and updated .agents/ck/HANDOFF.md")
    return {
        "handoff_file": str(handoff_file),
        "active_handoff": str(active_pointer),
        "checkpoint_file": str(history_file),
    }


CHAT_LANG_PLACEHOLDER = "{{CHAT_AND_ARTIFACTS_LANGUAGE}}"


def _placeholder_target_files(root: Path) -> List[Path]:
    targets: List[Path] = []
    agents_md = root / "AGENTS.md"
    if agents_md.is_file():
        targets.append(agents_md)
    for folder, pattern in (
        (root / ".agents" / "rules", "*.md"),
        (root / ".agents" / "agents", "*.md"),
        (root / ".agents" / "skills", "*/SKILL.md"),
        (root / ".agents" / "workflows", "*"),
        (root / ".agents" / "templates", "*.json"),
    ):
        if folder.is_dir():
            targets.extend(sorted(p for p in folder.glob(pattern) if p.is_file()))
    hooks_py = root / ".agents" / "scripts" / "workflow_hooks.py"
    if hooks_py.is_file():
        targets.append(hooks_py)
    for extra_file in (
        root / ".agents" / "ck" / "context.json",
        root / "artifacts" / "README.md",
    ):
        if extra_file.is_file():
            targets.append(extra_file)
    return targets


def run_set_language(
    language: str,
    repo_root: Optional[Path] = None,
    create_backup: bool = True,
) -> Dict[str, Any]:
    """Replaces {{CHAT_AND_ARTIFACTS_LANGUAGE}} across workflow files (with Pre-Action Backup) and records chat_language."""
    lang = language.strip()
    if not lang or "{{" in lang or "}}" in lang:
        raise ValueError("Language must be a non-empty string without placeholder braces.")

    root = (repo_root or REPO_ROOT).resolve()
    candidates = [
        p
        for p in _placeholder_target_files(root)
        if p.name != "workflow_hooks.py"
        and CHAT_LANG_PLACEHOLDER in p.read_text(encoding="utf-8", errors="replace")
    ]
    updated_rel = [p.relative_to(root).as_posix() for p in candidates]
    backup_dir: Optional[Path] = None
    if updated_rel and create_backup:
        backup_dir = run_backup(
            topic="set_language",
            files=updated_rel,
            desc=f"Configure chat/artifacts language to {lang}",
            repo_root=root,
        )

    for path in candidates:
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(CHAT_LANG_PLACEHOLDER, lang), encoding="utf-8")

    ck_path = root / ".agents" / "ck" / "context.json"
    if ck_path.is_file():
        try:
            ck = json.loads(ck_path.read_text(encoding="utf-8"))
            if isinstance(ck, dict):
                ck["chat_language"] = lang
                ck_path.write_text(json.dumps(ck, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except (OSError, json.JSONDecodeError):
            pass

    print(f"[Language] Set chat/artifacts language to '{lang}' across {len(updated_rel)} file(s).")
    return {
        "language": lang,
        "updated_files": updated_rel,
        "backup_dir": str(backup_dir) if backup_dir else None,
    }


def scan_placeholders(repo_root: Optional[Path] = None) -> Dict[str, List[Tuple[str, int]]]:
    """Scans active workflow config, rule, agent, skill, hook, workflow, and template files for {{PLACEHOLDERS}}."""
    root = (repo_root or REPO_ROOT).resolve()
    targets = _placeholder_target_files(root)

    found: Dict[str, List[Tuple[str, int]]] = {}
    for path in targets:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for idx, line in enumerate(text.splitlines(), 1):
            for match in PLACEHOLDER_RE.finditer(line):
                token = match.group(0)
                if token in ("{{PLACEHOLDERS}}", "{{PLACEHOLDER}}"):
                    continue
                if path.name == "workflow_hooks.py" and token == CHAT_LANG_PLACEHOLDER:
                    continue
                found.setdefault(token, []).append((rel, idx))
    return dict(sorted(found.items()))


def run_check_placeholders(repo_root: Optional[Path] = None, fail_on_found: bool = False) -> int:
    found = scan_placeholders(repo_root=repo_root)
    if not found:
        print("[Placeholders] All workflow placeholders have been filled (0 remaining).")
        return 0
    total_refs = sum(len(locs) for locs in found.values())
    print(f"[Placeholders] Found {len(found)} unique placeholder(s) ({total_refs} reference(s)):")
    for token, locs in found.items():
        sample = ", ".join(f"{rel}:{ln}" for rel, ln in locs[:4])
        extra = f" (+{len(locs) - 4} more)" if len(locs) > 4 else ""
        print(f"  - {token}: {sample}{extra}")
    return 1 if fail_on_found else 0


def _parse_backup_utc(item: Path) -> datetime:
    fallback = datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc)
    match = re.match(r"^(\d{8})T(\d{6})(\d{6})Z", item.name)
    if match:
        try:
            return datetime.strptime(
                f"{match.group(1)}{match.group(2)}{match.group(3)}", "%Y%m%d%H%M%S%f"
            ).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    match_day = re.match(r"^(\d{8})(?:[-_]|$)", item.name)
    if match_day:
        try:
            return datetime.strptime(match_day.group(1), "%Y%m%d").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    if item.is_dir():
        manifest_file = item / "manifest.json"
        if manifest_file.is_file():
            try:
                data = json.loads(manifest_file.read_text(encoding="utf-8"))
                ts = str(data.get("timestamp") or "").strip()
                if ts.endswith("Z"):
                    ts = ts[:-1] + "+00:00"
                if ts:
                    parsed = datetime.fromisoformat(ts)
                    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
            except (OSError, ValueError, json.JSONDecodeError):
                pass
    return fallback


def _dir_size_bytes(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                continue
    return total


def _remove_entry_safe(path: Path, retries: int = 3, delay_sec: float = 0.15) -> Optional[str]:
    def _handle_readonly(func: Any, target_path: str, exc: BaseException) -> None:
        if isinstance(exc, PermissionError):
            try:
                os.chmod(target_path, stat.S_IWRITE)
                func(target_path)
                return
            except OSError:
                raise exc
        raise exc

    last_err: Optional[str] = None
    for attempt in range(retries):
        try:
            if path.is_dir() and not path.is_symlink():
                if sys.version_info >= (3, 12):
                    shutil.rmtree(path, onexc=_handle_readonly)
                else:
                    shutil.rmtree(path, onerror=lambda f, p, ei: _handle_readonly(f, p, ei[1]))
            else:
                try:
                    path.unlink(missing_ok=True)
                except PermissionError:
                    os.chmod(path, stat.S_IWRITE)
                    path.unlink(missing_ok=True)
            return None
        except OSError as exc:
            last_err = str(exc)
            if attempt + 1 < retries:
                time.sleep(delay_sec * (attempt + 1))
    return last_err


def run_rollback(
    backup_dir: Optional[Path] = None,
    apply: bool = False,
    repo_root: Optional[Path] = None,
) -> Dict[str, List[str]]:
    """Restores backed_up files (verifying SHA-256) and removes absent files per manifest.json."""
    root = (repo_root or REPO_ROOT).resolve()
    bdir = (
        (backup_dir if backup_dir.is_absolute() else root / backup_dir).resolve()
        if backup_dir
        else _find_latest_backup(root)
    )
    manifest_path = bdir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Backup manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files_map = manifest.get("files")
    if not isinstance(files_map, dict):
        raise ValueError(f"Invalid manifest files map in {manifest_path}")

    planned_restore: List[Tuple[str, Path, Path]] = []
    planned_remove: List[Tuple[str, Path]] = []
    unchanged: List[str] = []

    for raw_rel, entry in files_map.items():
        rel_path = str(raw_rel).replace("\\", "/")
        dest = (root / rel_path).resolve()
        try:
            dest.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Refusing path outside repo root: {rel_path}") from exc
        if not isinstance(entry, dict):
            continue
        status = entry.get("status")
        if status == "backed_up":
            backup_name = str(entry.get("backup_file") or "")
            src = bdir / backup_name
            if not backup_name or not src.is_file():
                raise FileNotFoundError(f"Missing backup file for {rel_path}: {src}")
            expected_sha = str(entry.get("sha256") or "")
            if expected_sha:
                actual_sha = hashlib.sha256(src.read_bytes()).hexdigest()
                if actual_sha != expected_sha:
                    raise ValueError(
                        f"SHA-256 mismatch for {rel_path}: expected {expected_sha}, got {actual_sha}"
                    )
            planned_restore.append((rel_path, src, dest))
        elif status == "absent":
            if dest.is_file():
                planned_remove.append((rel_path, dest))
            else:
                unchanged.append(rel_path)

    restored: List[str] = []
    removed: List[str] = []
    for rel_path, src, dest in planned_restore:
        if apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        restored.append(rel_path)
    for rel_path, dest in planned_remove:
        if apply:
            dest.unlink(missing_ok=True)
        removed.append(rel_path)

    mode_label = "Applied" if apply else "Dry-Run"
    print(
        f"[Rollback {mode_label}] source={bdir.name} restore={len(restored)} "
        f"remove={len(removed)} unchanged={len(unchanged)}"
    )
    return {"restored": restored, "removed": removed, "unchanged": unchanged}


def run_prune(
    keep_days: int = BACKUP_MAX_RETENTION_DAYS,
    apply: bool = False,
    repo_root: Optional[Path] = None,
    quiet_if_empty: bool = False,
) -> Dict[str, object]:
    """Previews or deletes backup/ entries older than keep_days (default 30). Never touches artifacts/."""
    if keep_days < 0:
        raise ValueError("keep_days must be non-negative")
    root = (repo_root or REPO_ROOT).resolve()
    now = _utc_now()
    cutoff_ts = now.timestamp() - (keep_days * 86400)
    today_utc = now.date()

    backup_candidates: List[Path] = []
    backup_base = root / "backup"
    if backup_base.is_dir():
        entries = list(backup_base.iterdir())
        entries.sort(key=lambda d: (_parse_backup_utc(d), d.name), reverse=True)
        for item in entries:
            item_dt = _parse_backup_utc(item)
            if keep_days > 0 and item_dt.date() >= today_utc:
                continue
            if item_dt.timestamp() < cutoff_ts:
                backup_candidates.append(item)

    reclaimed_bytes = sum(_dir_size_bytes(p) for p in backup_candidates)
    deleted_backups: List[str] = []
    skipped_locked: List[str] = []

    if apply:
        reclaimed_bytes = 0
        for item in backup_candidates:
            item_bytes = _dir_size_bytes(item)
            err = _remove_entry_safe(item)
            rel_item = item.relative_to(root).as_posix()
            if err is None:
                deleted_backups.append(rel_item)
                reclaimed_bytes += item_bytes
            else:
                skipped_locked.append(f"{rel_item}: {err}")

    if not quiet_if_empty or backup_candidates or skipped_locked:
        mode_label = "Applied" if apply else "Dry-Run"
        reclaimed_mb = reclaimed_bytes / (1024 * 1024)
        print(
            f"[Prune {mode_label}] backups={len(deleted_backups) if apply else len(backup_candidates)} "
            f"skipped_locked={len(skipped_locked)} reclaimable={reclaimed_mb:.2f} MB"
        )
        for locked_note in skipped_locked:
            print(f"[Prune Skipped] {locked_note}", file=sys.stderr)
    return {
        "backup_candidates": [p.relative_to(root).as_posix() for p in backup_candidates],
        "deleted_backups": deleted_backups,
        "skipped_locked": skipped_locked,
        "reclaimed_bytes": reclaimed_bytes,
    }


def resolve_inspect_script(raw_path: str, repo_root: Path) -> Path:
    """Resolves a --tool script strictly inside artifacts/tools/ or .agents/scripts/."""
    root = repo_root.resolve()
    candidate = Path(raw_path.strip())
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Script path outside repository root is blocked: {raw_path}") from exc
    parts_lower = tuple(p.lower() for p in rel.parts)
    in_allowed = any(
        len(parts_lower) > len(prefix) and parts_lower[: len(prefix)] == prefix
        for prefix in ALLOWED_INSPECT_SCRIPT_ROOTS
    )
    if not in_allowed:
        raise ValueError(
            f"Script must reside under artifacts/tools/ or .agents/scripts/: {rel.as_posix()}"
        )
    if resolved.suffix.lower() != ".py":
        raise ValueError(f"Only .py scripts are supported for --tool: {rel.as_posix()}")
    if not resolved.is_file():
        raise FileNotFoundError(f"Tool script not found: {rel.as_posix()}")
    return resolved


def run_inspect(
    mode: str = "quick",
    tools: Optional[Sequence[str]] = None,
    timeout: int = 120,
    fail_fast: bool = False,
    json_output: bool = False,
    report: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Runs standardized workflow health gates and optional --tool scripts in one command."""
    root = (repo_root or REPO_ROOT).resolve()
    gates: List[Tuple[str, str, List[str]]] = []

    if mode in ("quick", "full"):
        verifier = root / ".agents" / "scripts" / "verify_workflow.py"
        if verifier.is_file():
            gates.append(("verify_workflow", "workflow", [sys.executable, str(verifier), "--root", str(root)]))
        scripts_dir = root / ".agents" / "scripts"
        if scripts_dir.is_dir() and list(scripts_dir.glob("test_*.py")):
            gates.append(
                (
                    "workflow_unittest",
                    "test",
                    [sys.executable, "-m", "unittest", "discover", "-s", ".agents/scripts", "-p", "test_*.py"],
                )
            )
    if mode == "full":
        ops_script = root / ".agents" / "scripts" / "workflow_ops.py"
        if ops_script.is_file():
            gates.append(
                (
                    "check_placeholders",
                    "setup",
                    [sys.executable, str(ops_script), "check-placeholders", "--repo-root", str(root)],
                )
            )

    for raw_tool in tools or []:
        resolved_tool = resolve_inspect_script(raw_tool, root)
        rel_tool = resolved_tool.relative_to(root).as_posix()
        gates.append((f"tool:{rel_tool}", "tool", [sys.executable, str(resolved_tool)]))

    results: List[Dict[str, Any]] = []
    failed = 0
    for name, category, cmd in gates:
        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            exit_code = proc.returncode
            combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
            tail = "\n".join(line.rstrip() for line in combined.splitlines()[-12:])
            status = "PASS" if exit_code == 0 else "FAIL"
        except subprocess.TimeoutExpired:
            exit_code = 124
            tail = f"Timed out after {timeout}s"
            status = "FAIL"
        duration = round(time.monotonic() - t0, 3)
        results.append(
            {
                "name": name,
                "category": category,
                "status": status,
                "exit_code": exit_code,
                "duration_sec": duration,
                "tail_output": tail,
            }
        )
        if status != "PASS":
            failed += 1
            if fail_fast:
                break

    summary: Dict[str, Any] = {
        "timestamp": _format_rfc3339_utc(_utc_now()),
        "mode": mode,
        "overall_status": "PASS" if failed == 0 else "FAIL",
        "exit_code": 0 if failed == 0 else 1,
        "total_gates": len(results),
        "failed_gates": failed,
        "gates": results,
    }
    if report is not None:
        out_path = (report if report.is_absolute() else root / report).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if json_output:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(
            f"[Inspect {summary['overall_status']}] mode={mode} gates={len(results)} failed={failed}"
        )
        for item in results:
            print(
                f"  - [{item['status']}] {item['name']} (exit={item['exit_code']}, {item['duration_sec']}s)"
            )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable Agent Workflow — Unified Ops CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    b = subparsers.add_parser("backup", help="Create Pre-Action Backup with SHA-256 manifest.json")
    b.add_argument("--topic", required=True, help="Short slug for backup folder")
    b.add_argument("--desc", default=None, help="Backup description")
    b.add_argument("--repo-root", default=None, help="Override repository root")
    b.add_argument("files", nargs="+", help="File paths to back up")

    d = subparsers.add_parser("diff", help="Generate unified diff (-U1) against backup manifest")
    d.add_argument("--backup", default=None, help="Backup directory (defaults to latest)")
    d.add_argument("--output", default=None, help="Optional .diff output file path")
    d.add_argument("--repo-root", default=None, help="Override repository root")

    rb = subparsers.add_parser(
        "rollback", help="Preview or restore files & remove absent entries from a backup manifest"
    )
    rb.add_argument("--backup", default=None, help="Specific backup folder path (defaults to latest)")
    rb.add_argument("--apply", action="store_true", help="Apply rollback changes (default is dry-run preview)")
    rb.add_argument("--repo-root", default=None, help="Override repository root")

    pr = subparsers.add_parser(
        "prune", help="Preview or delete backup/ entries older than 30 days (never touches artifacts/)"
    )
    pr.add_argument(
        "--keep-days",
        type=int,
        default=BACKUP_MAX_RETENTION_DAYS,
        help="Maximum backup retention in days (default: 30)",
    )
    pr.add_argument("--apply", action="store_true", help="Delete expired backups (default is dry-run preview)")
    pr.add_argument("--repo-root", default=None, help="Override repository root")

    ins = subparsers.add_parser(
        "inspect", help="Run unified workflow health gates (+ optional --tool scripts under artifacts/tools/)"
    )
    ins.add_argument(
        "--mode",
        choices=("quick", "full", "tools-only"),
        default="quick",
        help="Inspection depth profile (default: quick)",
    )
    ins.add_argument(
        "--tool",
        action="append",
        default=[],
        help="Reusable .py tool script under artifacts/tools/ or .agents/scripts/ (repeatable)",
    )
    ins.add_argument("--timeout", type=int, default=120, help="Per-gate timeout in seconds (default: 120)")
    ins.add_argument("--fail-fast", action="store_true", help="Stop immediately on first failing gate")
    ins.add_argument("--json", action="store_true", dest="json_output", help="Output JSON report to stdout")
    ins.add_argument("--report", default=None, help="Optional output path to save JSON report")
    ins.add_argument("--repo-root", default=None, help="Override repository root")

    lg = subparsers.add_parser("log-turn", help="Log turn to Conversations/ and rotate checkpoints")
    lg.add_argument("--title", required=True, help="Turn title")
    lg.add_argument("--summary", required=True, help="Turn summary")
    lg.add_argument("--objective", default=None, help="Checkpoint active objective")
    lg.add_argument("--status", default="COMPLETED", help="Checkpoint status")
    lg.add_argument("--touched", nargs="*", default=None, help="Touched file paths")
    lg.add_argument("--decisions", nargs="*", default=None, help="Key decisions")
    lg.add_argument("--next", nargs="*", default=None, dest="next_steps", help="Pending next steps")
    lg.add_argument("--test-status", default=None, help="Test status summary")
    lg.add_argument("--role", default="[👑 @lead]", help="Active role tag")
    lg.add_argument("--repo-root", default=None, help="Override repository root")

    sl = subparsers.add_parser("set-language", help="Configure chat/artifacts language for first-time setup")
    sl.add_argument("--lang", required=True, help="Preferred user chat & artifacts language (e.g., English, Thai)")
    sl.add_argument("--no-backup", action="store_true", help="Skip automatic Pre-Action Backup before replacing")
    sl.add_argument("--repo-root", default=None, help="Override repository root")

    cp = subparsers.add_parser("check-placeholders", help="List remaining {{PLACEHOLDERS}} in workflow files")
    cp.add_argument("--fail-on-found", action="store_true", help="Exit 1 if unfilled placeholders remain")
    cp.add_argument("--repo-root", default=None, help="Override repository root")

    ho = subparsers.add_parser("handoff", help="Generate new-window handoff packet (/handoff)")
    ho.add_argument("--objective", required=True, help="Active objective for the new chat window")
    ho.add_argument("--summary", default=None, help="Brief context summary")
    ho.add_argument("--completed", nargs="*", default=None, help="Completed and verified items")
    ho.add_argument("--settled", nargs="*", default=None, help="Session-settled decisions")
    ho.add_argument("--next", nargs="*", default=None, dest="next_steps", help="Pending next steps")
    ho.add_argument("--blockers", nargs="*", default=None, help="Open risks, blockers, or untested scope")
    ho.add_argument("--touched", nargs="*", default=None, help="Key touched relative file paths")
    ho.add_argument("--repo-root", default=None, help="Override repository root")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.repo_root) if getattr(args, "repo_root", None) else None
    if args.command == "backup":
        run_backup(topic=args.topic, files=args.files, desc=args.desc, repo_root=root)
        return 0
    if args.command == "diff":
        run_diff(
            backup_dir=Path(args.backup) if args.backup else None,
            output=Path(args.output) if args.output else None,
            repo_root=root,
        )
        return 0
    if args.command == "rollback":
        run_rollback(
            backup_dir=Path(args.backup) if args.backup else None,
            apply=args.apply,
            repo_root=root,
        )
        return 0
    if args.command == "prune":
        run_prune(keep_days=args.keep_days, apply=args.apply, repo_root=root)
        return 0
    if args.command == "inspect":
        result = run_inspect(
            mode=args.mode,
            tools=args.tool,
            timeout=args.timeout,
            fail_fast=args.fail_fast,
            json_output=args.json_output,
            report=Path(args.report) if args.report else None,
            repo_root=root,
        )
        return int(result["exit_code"])
    if args.command == "log-turn":
        run_log_turn(
            title=args.title,
            summary=args.summary,
            objective=args.objective,
            status=args.status,
            touched=args.touched,
            decisions=args.decisions,
            next_steps=args.next_steps,
            test_status=args.test_status,
            role=args.role,
            repo_root=root,
        )
        return 0
    if args.command == "set-language":
        run_set_language(language=args.lang, repo_root=root, create_backup=not args.no_backup)
        return 0
    if args.command == "check-placeholders":
        return run_check_placeholders(repo_root=root, fail_on_found=args.fail_on_found)
    if args.command == "handoff":
        run_handoff(
            objective=args.objective,
            summary=args.summary,
            completed=args.completed,
            settled=args.settled,
            next_steps=args.next_steps,
            blockers=args.blockers,
            touched=args.touched,
            repo_root=root,
        )
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
