# Dynamic Antigravity Workflow (run_workflow)
# Execute via: run_workflow(ScriptPath="<abs-path>/.agents/workflows/project_fanout.py", Args={...}, Description="...")
# Replace {{WORKFLOW_TARGET_GLOB}} and {{PROJECT_OBJECTIVE}} with your project defaults.

from pathlib import Path

target_glob = args.get("target_glob", "{{WORKFLOW_TARGET_GLOB}}")
objective = args.get(
    "objective",
    "Audit each file against {{PROJECT_OBJECTIVE}}, Never Cut List, and error-handling invariants.",
)
max_items = int(args.get("max_items", 12))
model_tier = args.get("model_tier", "flash")

phase("Discover Targets")
root = Path(WORKSPACES[0]) if WORKSPACES else Path(".")
if "{{" in target_glob:
    raise ValueError(
        "Unfilled placeholder in target_glob. Pass Args={'target_glob': 'src/**/*.py'} "
        "or replace {{WORKFLOW_TARGET_GLOB}} in .agents/workflows/project_fanout.py."
    )

matched = sorted(
    p.relative_to(root).as_posix()
    for p in root.glob(target_glob)
    if p.is_file()
)[:max_items]

log(f"Matched {len(matched)} file(s) for glob '{target_glob}' (cap={max_items})")

if not matched:
    print("No files matched target_glob.")
else:
    phase("Parallel Inspection")
    item_schema = {
        "type": "object",
        "properties": {
            "file": {"type": "string"},
            "status": {"type": "string", "enum": ["OK", "FINDINGS"]},
            "findings": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["file", "status", "findings"],
    }

    results = await parallel(
        matched,
        lambda rel_path: agent(
            (
                f"Inspect `{rel_path}` in read-only mode.\n"
                f"Objective: {objective}\n"
                "Return JSON matching the required schema. Cite exact line numbers for any finding."
            ),
            schema=item_schema,
            role=f"Inspect {rel_path}",
            type_name="verifier",
            workspace="inherit",
            model=model_tier,
        ),
    )

    phase("Aggregate Summary")
    flagged = [r for r in results if r.get("status") == "FINDINGS"]
    log(f"Completed {len(results)} file review(s); {len(flagged)} file(s) with findings.")
    for item in flagged:
        print(f"[FINDINGS] {item['file']}")
        for note in item.get("findings", []):
            print(f"  - {note}")
    if not flagged:
        print("[OK] All inspected files passed with 0 findings.")
