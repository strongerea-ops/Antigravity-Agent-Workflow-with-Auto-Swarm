#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable Agent Workflow — Unified Operations CLI
Pure Python 3.10+ Standard Library only.
Commands:
  backup              Pre-Action microsecond backup with SHA-256 manifest.json
  diff                Unified diff (-U1) against backup manifest (works without .git)
  log-turn            Append daily conversation log, update README, rotate Rolling 15 Checkpoints
  check-placeholders  Scan workflow templates for remaining {{PLACEHOLDER}} tokens
"""

import argparse
import difflib
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_CHECKPOINTS = 15
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


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
) -> Path:
    """Creates backup/YYYYMMDDTHHMMSSffffffZ_<topic>/ with RFC 3339 UTC manifest.json."""
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


def _insert_readme_bullet(readme_path: Path, bullet: str) -> None:
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    if not readme_path.exists():
        readme_path.write_text(f"# Conversations Vault\n\n{bullet}\n", encoding="utf-8")
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


def scan_placeholders(repo_root: Optional[Path] = None) -> Dict[str, List[Tuple[str, int]]]:
    """Scans active workflow config, agent, skill, hook, workflow, and template files for {{PLACEHOLDERS}}."""
    root = (repo_root or REPO_ROOT).resolve()
    targets: List[Path] = []
    agents_md = root / "AGENTS.md"
    if agents_md.is_file():
        targets.append(agents_md)
    rules_md = root / ".agents" / "rules" / "rules.md"
    if rules_md.is_file():
        targets.append(rules_md)
    for folder, pattern in (
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

    found: Dict[str, List[Tuple[str, int]]] = {}
    for path in targets:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for idx, line in enumerate(text.splitlines(), 1):
            for match in PLACEHOLDER_RE.finditer(line):
                token = match.group(0)
                if token == "{{PLACEHOLDERS}}" or token == "{{PLACEHOLDER}}":
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

    cp = subparsers.add_parser("check-placeholders", help="List remaining {{PLACEHOLDERS}} in workflow files")
    cp.add_argument("--fail-on-found", action="store_true", help="Exit 1 if unfilled placeholders remain")
    cp.add_argument("--repo-root", default=None, help="Override repository root")
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
    if args.command == "check-placeholders":
        return run_check_placeholders(repo_root=root, fail_on_found=args.fail_on_found)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
