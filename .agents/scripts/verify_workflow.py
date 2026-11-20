#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable Agent Workflow — Self-Contained Schema & Hygiene Auditor
Validates AGENTS.md byte budget, 10-element agent schema, skills, hooks.json
(resolved from .agents/ CWD), scripts, run_workflow scripts (top-level await),
JSON templates, artifacts catalog parity, UTF-8 BOM=False, and relative links.
Pure Python 3.10+ Standard Library only.
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import unquote

AGENTS_MD_BYTE_BUDGET = 24000
SKILL_MAX_LINES = 300
VALID_TOOLS = {
    "read_file",
    "edit_file",
    "write_file",
    "run_command",
    "manage_task",
    "search_web",
    "send_message",
    "invoke_subagent",
    "define_subagent",
    "manage_subagents",
    "ask_question",
    "schedule",
}
VALID_MODELS = {"inherit", "flash_lite", "flash", "pro"}
VALID_POLICIES = {"off", "auto", "eager", "sandbox"}


def _parse_frontmatter(text: str) -> Dict[str, object]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not match:
        return {}
    fm = match.group(1)
    result: Dict[str, object] = {}
    current_list_key = ""
    multiline_key = ""
    multiline_parts: List[str] = []

    def _flush_multiline() -> None:
        nonlocal multiline_key, multiline_parts
        if multiline_key:
            result[multiline_key] = " ".join(multiline_parts).strip()
            multiline_key = ""
            multiline_parts = []

    for line in fm.splitlines():
        if multiline_key:
            if line.startswith((" ", "\t")) or not line.strip():
                if line.strip():
                    multiline_parts.append(line.strip())
                continue
            _flush_multiline()
        if re.match(r"^\s*-\s+", line) and current_list_key:
            item = re.sub(r"^\s*-\s+", "", line).strip().strip("\"'")
            lst = result.setdefault(current_list_key, [])
            if isinstance(lst, list):
                lst.append(item)
            continue
        kv = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            if val in (">", ">-", "|", "|-"):
                current_list_key = ""
                multiline_key = key
                multiline_parts = []
            elif val.startswith("[") and val.endswith("]"):
                current_list_key = ""
                inner = val[1:-1].strip()
                result[key] = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()] if inner else []
            elif val == "":
                current_list_key = key
                result[key] = []
            else:
                current_list_key = ""
                result[key] = val.strip("\"'")
    _flush_multiline()
    return result


def audit_workspace(root: Path) -> List[str]:
    """Audits AGENTS.md, .agents/ (rules, agents, skills, hooks, scripts, workflows, templates, ck), root docs, and artifacts/."""
    errors: List[str] = []
    agents_md = root / "AGENTS.md"
    agents_dir = root / ".agents" / "agents"
    skills_dir = root / ".agents" / "skills"
    rules_md = root / ".agents" / "rules" / "rules.md"
    hooks_json = root / ".agents" / "hooks.json"
    scripts_dir = root / ".agents" / "scripts"
    workflows_dir = root / ".agents" / "workflows"
    templates_dir = root / ".agents" / "templates"
    ck_dir = root / ".agents" / "ck"
    artifacts_dir = root / "artifacts"

    agents_md_text = ""
    if not agents_md.is_file():
        errors.append("Missing root AGENTS.md")
    else:
        raw = agents_md.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append("AGENTS.md contains UTF-8 BOM")
        if len(raw) > AGENTS_MD_BYTE_BUDGET:
            errors.append(f"AGENTS.md exceeds {AGENTS_MD_BYTE_BUDGET} bytes ({len(raw)} bytes)")
        agents_md_text = raw.decode("utf-8", errors="replace")

    existing_skills: Set[str] = set()
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and (d / "SKILL.md").is_file():
                existing_skills.add(d.name)
    else:
        errors.append("Missing .agents/skills directory")

    md_files: List[Path] = []
    for doc_path in sorted(root.glob("*.md")):
        if doc_path.is_file():
            md_files.append(doc_path)
    if rules_md.is_file():
        md_files.append(rules_md)
    if agents_dir.is_dir():
        md_files.extend(sorted(agents_dir.glob("*.md")))
    if skills_dir.is_dir():
        md_files.extend(sorted(skills_dir.glob("*/SKILL.md")))
    if ck_dir.is_dir():
        md_files.extend(sorted(ck_dir.glob("*.md")))
    if artifacts_dir.is_dir():
        md_files.extend(sorted(artifacts_dir.rglob("*.md")))

    # Validate skills
    for skill_file in sorted(skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else []:
        text = skill_file.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)
        rel = skill_file.relative_to(root).as_posix()
        skill_name = str(fm.get("name", ""))
        if not skill_name or not fm.get("description"):
            errors.append(f"{rel}: missing YAML name or description")
        elif skill_name != skill_file.parent.name:
            errors.append(f"{rel}: YAML name '{skill_name}' does not match folder '{skill_file.parent.name}'")
        line_count = len(text.splitlines())
        if line_count > SKILL_MAX_LINES:
            errors.append(f"{rel}: {line_count} lines exceeds {SKILL_MAX_LINES}-line ceiling")
        if agents_md_text and f"{skill_file.parent.name}/SKILL.md" not in agents_md_text:
            errors.append(f"AGENTS.md: missing reference to skill '{skill_file.parent.name}/SKILL.md'")

    # Validate 10-element agent schema
    agent_files = sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []
    referenced_skills: Set[str] = set()
    for agent_file in agent_files:
        text = agent_file.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)
        rel = agent_file.relative_to(root).as_posix()
        required_keys = (
            "name",
            "description",
            "tools",
            "subagent",
            "mainAgent",
            "model",
            "commandExecutionPolicy",
            "skills",
        )
        for key in required_keys:
            if key not in fm:
                errors.append(f"{rel}: missing YAML key '{key}'")
        agent_name = str(fm.get("name", ""))
        if agent_name and agent_name != agent_file.stem:
            errors.append(f"{rel}: YAML name '{agent_name}' does not match filename '{agent_file.stem}'")
        if "subagent" in fm and str(fm.get("subagent")).lower() != "true":
            errors.append(f"{rel}: 'subagent' must be true")
        if "mainAgent" in fm and str(fm.get("mainAgent")).lower() not in {"true", "false"}:
            errors.append(f"{rel}: invalid mainAgent '{fm.get('mainAgent')}'")
        tools = fm.get("tools")
        if not isinstance(tools, list) or not tools:
            errors.append(f"{rel}: 'tools' must be a non-empty list")
        else:
            bad_tools = [t for t in tools if t not in VALID_TOOLS]
            if bad_tools:
                errors.append(f"{rel}: unknown tools {bad_tools}")
        model = str(fm.get("model", ""))
        if model not in VALID_MODELS:
            errors.append(f"{rel}: invalid model '{model}'")
        policy = str(fm.get("commandExecutionPolicy", ""))
        if policy not in VALID_POLICIES:
            errors.append(f"{rel}: invalid commandExecutionPolicy '{policy}'")
        skills = fm.get("skills")
        if not isinstance(skills, list) or not skills:
            errors.append(f"{rel}: 'skills' must be a non-empty list")
        else:
            missing = [s for s in skills if s not in existing_skills]
            if missing:
                errors.append(f"{rel}: references missing skills {missing}")
            referenced_skills.update(s for s in skills if s in existing_skills)
        if "# System Prompt" not in text:
            errors.append(f"{rel}: missing '# System Prompt' heading")
        if "# Review Guidelines" not in text:
            errors.append(f"{rel}: missing '# Review Guidelines' heading")
        if agents_md_text and agent_file.name not in agents_md_text:
            errors.append(f"AGENTS.md: missing reference to agent '{agent_file.name}'")

    orphan_skills = sorted(existing_skills - referenced_skills)
    if orphan_skills and agent_files:
        errors.append(f".agents/skills: unreferenced by any agent YAML {orphan_skills}")

    if agents_md_text:
        for m in re.finditer(r"`?(\d+)`?\s*Agents\b", agents_md_text):
            if int(m.group(1)) != len(agent_files):
                errors.append(f"AGENTS.md: declared agent count '{m.group(0)}' != actual {len(agent_files)}")
        for m in re.finditer(r"`?(\d+)`?\s*Skills\b", agents_md_text):
            if int(m.group(1)) != len(existing_skills):
                errors.append(f"AGENTS.md: declared skill count '{m.group(0)}' != actual {len(existing_skills)}")

    # Validate hooks.json (Antigravity Hook Runner executes with CWD = .agents/)
    if hooks_json.is_file():
        h_raw = hooks_json.read_bytes()
        if h_raw.startswith(b"\xef\xbb\xbf"):
            errors.append(".agents/hooks.json: contains UTF-8 BOM")
        try:
            hooks_data = json.loads(h_raw.decode("utf-8"))
            if isinstance(hooks_data, dict):
                for hook_name, spec in hooks_data.items():
                    if not isinstance(spec, dict):
                        continue
                    for ev_items in spec.values():
                        if not isinstance(ev_items, list):
                            continue
                        for group in ev_items:
                            handlers = group.get("hooks", []) if isinstance(group, dict) and "hooks" in group else [group]
                            for handler in handlers:
                                if not isinstance(handler, dict):
                                    continue
                                cmd = str(handler.get("command", ""))
                                for sm in re.finditer(r"(\S+\.py)\b", cmd):
                                    rel_script = sm.group(1).replace("\\", "/")
                                    if not (hooks_json.parent / rel_script).resolve().is_file():
                                        errors.append(f".agents/hooks.json ({hook_name}): missing script '{rel_script}'")
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f".agents/hooks.json: invalid JSON ({exc})")

    drive_re = re.compile(r"\b[A-Za-z]:[\\/]")

    # Validate Python scripts under .agents/scripts/
    if scripts_dir.is_dir():
        for py_file in sorted(scripts_dir.glob("*.py")):
            raw_py = py_file.read_bytes()
            rel_py = py_file.relative_to(root).as_posix()
            if raw_py.startswith(b"\xef\xbb\xbf"):
                errors.append(f"{rel_py}: contains UTF-8 BOM")
            src = raw_py.decode("utf-8", errors="replace")
            try:
                compile(src, str(py_file), "exec")
            except SyntaxError as exc:
                errors.append(f"{rel_py}:{exc.lineno}: Python syntax error ({exc.msg})")
            for idx, line in enumerate(src.splitlines(), 1):
                if drive_re.search(line):
                    errors.append(f"{rel_py}:{idx}: hardcoded drive letter detected")

    # Validate run_workflow scripts (top-level await supported) & workflow.json
    if workflows_dir.is_dir():
        for wf_json in sorted(workflows_dir.glob("*.json")):
            raw_j = wf_json.read_bytes()
            rel_j = wf_json.relative_to(root).as_posix()
            if raw_j.startswith(b"\xef\xbb\xbf"):
                errors.append(f"{rel_j}: contains UTF-8 BOM")
            try:
                json.loads(raw_j.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                errors.append(f"{rel_j}: invalid JSON ({exc})")
        for wf_py in sorted(workflows_dir.glob("*.py")):
            raw_py = wf_py.read_bytes()
            rel_py = wf_py.relative_to(root).as_posix()
            if raw_py.startswith(b"\xef\xbb\xbf"):
                errors.append(f"{rel_py}: contains UTF-8 BOM")
            src = raw_py.decode("utf-8", errors="replace")
            try:
                compile(src, str(wf_py), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
            except SyntaxError as exc:
                errors.append(f"{rel_py}:{exc.lineno}: workflow Python syntax error ({exc.msg})")
            for idx, line in enumerate(src.splitlines(), 1):
                if drive_re.search(line):
                    errors.append(f"{rel_py}:{idx}: hardcoded drive letter detected")

    # Validate JSON templates under .agents/templates/
    if templates_dir.is_dir():
        for tmpl_json in sorted(templates_dir.glob("*.json")):
            raw_j = tmpl_json.read_bytes()
            rel_j = tmpl_json.relative_to(root).as_posix()
            if raw_j.startswith(b"\xef\xbb\xbf"):
                errors.append(f"{rel_j}: contains UTF-8 BOM")
            try:
                json.loads(raw_j.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                errors.append(f"{rel_j}: invalid JSON ({exc})")

    # Validate artifacts catalog parity
    if artifacts_dir.is_dir():
        root_readme = artifacts_dir / "README.md"
        root_readme_text = root_readme.read_text(encoding="utf-8") if root_readme.is_file() else ""
        for cat_dir in sorted(artifacts_dir.iterdir()):
            if not cat_dir.is_dir():
                continue
            cat_files = [p for p in sorted(cat_dir.rglob("*")) if p.is_file() and p.name != "README.md"]
            if not cat_files:
                continue
            if root_readme.is_file() and cat_dir.name not in root_readme_text:
                errors.append(f"artifacts/README.md: missing populated category '{cat_dir.name}'")
            cat_readme = cat_dir / "README.md"
            if not cat_readme.is_file():
                errors.append(f"artifacts/{cat_dir.name}: missing README.md catalog")
            else:
                cat_text = cat_readme.read_text(encoding="utf-8")
                for item in cat_files:
                    rel_item = item.relative_to(cat_dir).as_posix()
                    if rel_item not in cat_text and item.name not in cat_text:
                        errors.append(f"artifacts/{cat_dir.name}/README.md: missing entry for '{rel_item}'")

    # Global Markdown hygiene checks
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    trunc_re = re.compile(r"(//|#)\s*\.\.\.\s*(existing code|rest of)", re.IGNORECASE)
    drive_example_re = re.compile(r"`[A-Za-z]:[\\/]`")
    trunc_example_re = re.compile(r"`[^`]*(//|#)\s*\.\.\.\s*(existing code|rest of)[^`]*`", re.IGNORECASE)

    for f in md_files:
        raw = f.read_bytes()
        rel = f.relative_to(root).as_posix()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{rel}: contains UTF-8 BOM")
        text = raw.decode("utf-8", errors="replace")
        for idx, line in enumerate(text.splitlines(), 1):
            for m in link_re.finditer(line):
                target = unquote(m.group(1).split("#")[0].strip())
                if not target or target.startswith(("http://", "https://", "file://", "mailto:", "customization://")):
                    continue
                if not (f.parent / target).resolve().exists():
                    errors.append(f"{rel}:{idx}: broken relative link -> {target}")
            sanitized_drive = drive_example_re.sub("", line)
            if drive_re.search(sanitized_drive) and "file:///" not in line:
                errors.append(f"{rel}:{idx}: hardcoded drive letter detected")
            sanitized_trunc = trunc_example_re.sub("", line)
            if trunc_re.search(sanitized_trunc):
                errors.append(f"{rel}:{idx}: code truncation ellipsis detected")

    return errors


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Portable Agent Workflow integrity")
    parser.add_argument("--root", default=None, help="Target project root (default: workspace root)")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    errors = audit_workspace(root)
    if errors:
        print(f"[FAIL] {len(errors)} workflow issue(s) in {root.name}:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"[PASS] Workflow audit clean in {root.name} (0 errors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
