# Antigravity Agent Workflow with Auto-Swarm

> **Language / เลือกภาษา:** [English](#english) | [ภาษาไทย](#ภาษาไทย)  
> **Complete Manuals / คู่มือฉบับสมบูรณ์:** [MANUAL_EN.md](./MANUAL_EN.md) (English) | [MANUAL_TH.md](./MANUAL_TH.md) (ภาษาไทย)

---

## English

A portable, project-agnostic **Antigravity AI Agent Workflow Starter Kit** designed for immediate drop-in adoption by any software project — featuring **3-Tier Auto Triage & Auto-Swarm**, **Auto Effort & Quota Pool Priority**, **Dirty Working Tree Swarm Safety**, **6-Event Lifecycle Hooks**, **Dynamic Python `run_workflow`**, **Rolling 15 Checkpoints ($O(1)$ Rehydration)**, **Zero-Dependency Pure-Python Verification/Backup/Diff CLI**, and **33 explicit `{{PLACEHOLDERS}}`** for your project's objectives, tasks, commands, and constraints.

### Why This Workflow Exists

Most AI coding workflows either break down as a project grows (no approval gates, no backups, bloated context) or are too heavy to reuse across projects. This starter kit balances **discipline and simplicity**:

- **Lean 4-Role Core Team (`10-Element Schema`):** `@lead` (triage & `/approve`), `@builder` (backup + minimal diff), `@verifier` (read-only dynamic QA + static diff audit), and `@researcher` (low-cost read-only discovery).
- **3-Tier Auto Triage + Auto-Swarm:** Stay in-line for 1–2 line edits (`Tier 0`), delegate scoped work to `invoke_subagent` (`Tier 1`), and scale out with `swarm` (Pool C -> Pool B -> Pool A `gemini-4-neon-*` + Auto Effort) or `run_workflow` (`Tier 2`) while preventing uncommitted-edit loss on dirty Git trees.
- **Token Conservation by Design:** English system rules & thinking, configurable `{{CHAT_AND_ARTIFACTS_LANGUAGE}}`, progressive-disclosure skills ($\le 300$ lines), `AGENTS.md` $\le 24\text{ KB}$, and default concise `no-code / no-detail` replies for general Q&A (expanding into full detail when planning, writing code, or via `/more-detail`).
- **Deterministic Runtime Guardrails (Zero External Dependencies):** Pure Python `3.10+` stdlib lifecycle hooks (`SessionStart`, `PreToolUse` backup & forbidden-command guards, `PostToolUse` audit, opt-in `Stop` gate with `continuationActive` protection) plus built-in `unittest` self-tests.
- **Works With or Without Git:** Microsecond Pre-Action Backups with `SHA-256` `manifest.json` and unified `-U1` diff generation (`workflow_ops.py diff`) work even in non-Git workspaces.
- **Latest Antigravity Capabilities Included:** Dynamic Python `run_workflow` (`workflow.json` + `project_fanout.py`), MCP template (Stdio + Streamable HTTP `/mcp`), and scheduled cron automation sidecar template (`CRON_TZ` + `"builtin": "schedule"`).

### 3-Minute Quick Start

> **Important (Hierarchical Rule Discovery):** Antigravity walks **up** from any opened file to the workspace root loading every `AGENTS.md` it encounters. Copy the **contents** of this repository directly into your target project's root directory (rather than nesting it inside another workspace that already has its own `AGENTS.md`).

1. **Clone or download this repository** and copy `AGENTS.md`, `.agents/`, `artifacts/`, and `MANUAL_EN.md` / `MANUAL_TH.md` into your target project's root directory:
   ```bash
   git clone https://github.com/strongerea-ops/Antigravity-Agent-Workflow-with-Auto-Swarm.git
   ```
2. **List all unfilled placeholders (`33` canonical placeholders):**
   ```bash
   python .agents/scripts/workflow_ops.py check-placeholders
   ```
3. **Fill your project details:** Replace `{{PLACEHOLDERS}}` in [AGENTS.md](./AGENTS.md), [.agents/rules/rules.md](./.agents/rules/rules.md), [.agents/skills/project-tasks/SKILL.md](./.agents/skills/project-tasks/SKILL.md), and (optionally) `.agents/scripts/workflow_hooks.py`, `.agents/workflows/`, and `.agents/templates/`.
   *(On Linux/macOS without a `python` alias, update `python` to `python3` in [.agents/hooks.json](./.agents/hooks.json), keeping `scripts/workflow_hooks.py` relative to `.agents/`.)*
4. **Verify schema integrity and run built-in self-tests (must exit `0`):**
   ```bash
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. **Start working in Antigravity:** Open your project workspace and run `/vibe <your goal>`. Full onboarding steps (what a new project **needs to have**, **needs to prepare**, and **needs to do**) are documented in [MANUAL_EN.md](./MANUAL_EN.md) and [MANUAL_TH.md](./MANUAL_TH.md).

### Documentation Hub

| Document | Language | Purpose |
|---|---|---|
| [MANUAL_EN.md](./MANUAL_EN.md) | **English** | Complete standalone manual: system functionality, all capabilities, all commands, and new-project onboarding guide |
| [MANUAL_TH.md](./MANUAL_TH.md) | **Thai** | Complete standalone Thai manual: system functionality, all capabilities, all commands, and new-project onboarding guide |
| [AGENTS.md](./AGENTS.md) | English | Root rule index, placeholders, hard constraints, 4-role model matrix, and global directives (`0–12`) |
| [.agents/rules/rules.md](./.agents/rules/rules.md) | English | Operational guardrails, blast-radius governance, dirty-tree swarm safety, and backup/rollback semantics |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | English & Thai | Contribution guidelines, workflow invariants, and pre-PR verification checklist |

### Repository Structure

```text
Antigravity-Agent-Workflow-with-Auto-Swarm/
├── README.md                              # Project overview & quick start (English & Thai)
├── MANUAL_EN.md                           # Complete manual & new-project guide (English)
├── MANUAL_TH.md                           # Complete manual & new-project guide (Thai)
├── AGENTS.md                              # Root index & global workflow contract (<= 24 KB)
├── CONTRIBUTING.md                        # How to contribute & PR verification standards (English & Thai)
├── LICENSE                                # GNU General Public License v3.0 (GPL-3.0)
├── .gitignore                             # Excludes local backups, caches, secrets & alerts
├── .github/
│   ├── workflows/ci.yml                   # Automated CI: verify_workflow.py + unittest (Linux & Windows)
│   ├── ISSUE_TEMPLATE/                    # Bug report & feature request templates
│   └── PULL_REQUEST_TEMPLATE.md           # PR verification checklist
├── .agents/
│   ├── rules/rules.md                     # Blast-radius rules, dirty-tree swarm safety, rollback
│   ├── agents/                            # 4 core subagents (10-element schema)
│   │   ├── lead.md                        # Triage, /approve gate, exclusive dispatcher
│   │   ├── builder.md                     # Pre-Action Backup + approved minimal-diff implementation
│   │   ├── verifier.md                    # Read-only dynamic QA + static diff audit
│   │   └── researcher.md                  # Read-only codebase & web exploration
│   ├── skills/                            # 4 progressive-disclosure skills (<= 300 lines each)
│   │   ├── project-tasks/SKILL.md         # Project objectives, tasks & acceptance criteria placeholders
│   │   ├── plan-and-build/SKILL.md        # /vibe, /design, /approve, /code, /simplify, /finalize
│   │   ├── verify-and-debug/SKILL.md      # /test, /debug (RCA), /audit, Circuit Breaker, /compound
│   │   └── workflow-ops/SKILL.md          # O(1) rehydration, Rolling 15 checkpoints, /compact, self-audit
│   ├── hooks.json                         # SessionStart, PreToolUse, PostToolUse, opt-in Stop (CWD = .agents/)
│   ├── scripts/                           # Pure Python 3.10+ stdlib (zero external dependencies)
│   │   ├── workflow_hooks.py              # Lifecycle hook handler (camelCase JSON stdin/stdout)
│   │   ├── workflow_ops.py                # backup, diff (-U1), log-turn, checkpoints, check-placeholders
│   │   ├── verify_workflow.py             # Self-contained workflow schema & hygiene auditor
│   │   └── test_workflow_ops_and_hooks.py # Deterministic unittest suite for hooks & ops
│   ├── workflows/                         # Dynamic run_workflow starter (Python + JSON args schema)
│   │   ├── workflow.json                  # Input args schema validation
│   │   └── project_fanout.py              # Parallel multi-file review/task fan-out template
│   ├── templates/                         # Opt-in capability templates (copy & configure when needed)
│   │   ├── mcp_config.example.json        # MCP servers (Stdio + Streamable HTTP /mcp)
│   │   └── sidecar.schedule.example.json  # Scheduled background automation (CRON_TZ + builtin schedule)
│   └── ck/                                # Rolling 15 context checkpoints (context.json, CONTEXT.md, history/)
└── artifacts/                             # 4-pillar archival vault (Conversations, requirements, blueprints, ADR, diffs, reviews)
```

### Contributing

Contributions, improvements, new skill/workflow patterns, and bug fixes are warmly welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a Pull Request, and make sure both automated checks pass locally:

```bash
python .agents/scripts/verify_workflow.py
python -m unittest discover -s .agents/scripts -p "test_*.py" -v
```

### License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)** — see [LICENSE](./LICENSE) for full terms.

---

## ภาษาไทย

**ชุดเวิร์กโฟลว์ AI Agent สำเร็จรูปสำหรับ Antigravity (Starter Kit)** ที่นำไปวางใช้ได้ทันทีกับทุกโปรเจกต์ซอฟต์แวร์ มาพร้อม **3-Tier Auto Triage และ Auto-Swarm**, **Auto Effort และการเรียงลำดับโควตา Pool**, **เกราะกันงานแก้ค้างหายบน `swarm` (Dirty Working Tree Safety)**, **Lifecycle Hooks ครบ 6 อีเวนต์**, **Dynamic Python `run_workflow`**, **Rolling 15 Checkpoints (ฟื้นฟูบริบทแบบ $O(1)$)**, **เครื่องมือตรวจสอบ/สำรองไฟล์/สร้าง Diff ด้วย Pure Python ที่ไม่ต้องลงแพ็กเกจเพิ่ม**, และ **`{{PLACEHOLDERS}}` ชัดเจนทั้ง `33` ตัว** สำหรับเติมเป้าหมาย งานหลัก คำสั่งรัน/เทสต์ และข้อจำกัดเฉพาะของแต่ละโปรเจกต์

### จุดเด่นของเวิร์กโฟลว์นี้

เวิร์กโฟลว์ AI จำนวนมากมักพังเมื่อโปรเจกต์ใหญ่ขึ้น (ไม่มีด่านขออนุมัติ ไม่สำรองไฟล์ ความจำแชตบวม) หรือซับซ้อนเกินกว่าจะนำไปใช้ซ้ำในโปรเจกต์อื่น ชุดตั้งต้นนี้ออกแบบให้สมดุลระหว่าง **ความรัดกุม** กับ **ความเรียบง่าย**:

- **ทีมพื้นฐานกะทัดรัด `4` บทบาท (ครบ 10-Element Schema):** `@lead` (คัดกรอง วางแผน และกำกับ `/approve`), `@builder` (สำรองไฟล์และแก้แบบ Minimal Diff), `@verifier` (รันเทสต์จริงและตรวจ Diff แบบอ่านอย่างเดียว ห้ามแก้ไฟล์เอง), และ `@researcher` (สำรวจโค้ดและค้นเอกสารอย่างประหยัดโควตา)
- **จัดขนาดงานอัตโนมัติ 3 ระดับ + Auto-Swarm:** งานแก้ 1–2 บรรทัดจบในแชตเดียว (`Tier 0`), งานเฉพาะทางใช้ `invoke_subagent` (`Tier 1`), และงานขนาดใหญ่หรือแยกหลายสายค่อยขยายเป็น `swarm` (เรียงลำดับ Pool C $\rightarrow$ Pool B $\rightarrow$ Pool A เลือก `gemini-4-neon-*` + Auto Effort) หรือ `run_workflow` (`Tier 2`) พร้อมกฎกันงานแก้ค้างในเครื่องหาย
- **ออกแบบเพื่อประหยัด Token ตั้งแต่ฐานราก:** กฎระบบและกระบวนการคิดเป็นภาษาอังกฤษ, ปรับภาษาการคุยและคลังบันทึกได้ผ่าน `{{CHAT_AND_ARTIFACTS_LANGUAGE}}`, โหลดสกิลเฉพาะตอนจำเป็น ($\le 300$ บรรทัด), `AGENTS.md` $\le 24\text{ KB}$, และตอบคำถามทั่วไปด้วยโหมดกระชับ `no-code / no-detail` (ขยายรายละเอียดครบเฉพาะตอนวางแผน เขียนโค้ด หรือเมื่อสั่ง `/more-detail`)
- **ระบบป้องกันระดับ Runtime ที่ไม่ต้องลงไลบรารีเพิ่ม:** ฮุค Python `3.10+` มาตรฐาน (`SessionStart` ฟื้นฟู Checkpoint, `PreToolUse` บังคับ Backup และบล็อกคำสั่งต้องห้าม, `PostToolUse` ตรวจสุขอนามัยหลังแก้, และ `Stop` แบบเปิดเลือกได้พร้อมตรวจ `continuationActive` กันลูป) มาพร้อมชุด `unittest` ทดสอบตัวเองในตัว
- **ใช้งานได้ทั้งแบบมี Git และไม่มี Git:** ระบบ Pre-Action Backup พร้อมรหัสตรวจ `SHA-256` ใน `manifest.json` และคำสั่งสร้าง Unified Diff `-U1` (`workflow_ops.py diff`) ทำงานได้แม้โปรเจกต์ยังไม่ได้ตั้งค่า `.git`
- **รองรับความสามารถล่าสุดของ Antigravity ครบชุด:** สคริปต์กระจายงานขนาน `run_workflow` (`workflow.json` + `project_fanout.py`), เทมเพลต MCP (Stdio + Streamable HTTP `/mcp`), และเทมเพลตงานตั้งเวลาเบื้องหลัง (`CRON_TZ` + `"builtin": "schedule"`)

### เริ่มต้นใช้งานใน 3 นาที (Quick Start)

> **ข้อควรระวัง (Hierarchical Rule Discovery):** Antigravity จะโหลดไฟล์ `AGENTS.md` เดินขึ้นจากไฟล์ที่เปิดอยู่ไปยัง Root ของ Workspace ดังนั้นให้คัดลอก **ไฟล์ข้างใน** Repository นี้ไปวางที่ **Root ของโปรเจกต์ใหม่โดยตรง** (หลีกเลี่ยงการวางซ้อนใต้ Workspace อื่นที่มี `AGENTS.md` อยู่แล้ว)

1. **โคลนหรือดาวน์โหลด Repository นี้** แล้วคัดลอก `AGENTS.md`, `.agents/`, `artifacts/`, และ `MANUAL_TH.md` / `MANUAL_EN.md` ไปวางที่ Root ของโปรเจกต์เป้าหมาย:
   ```bash
   git clone https://github.com/strongerea-ops/Antigravity-Agent-Workflow-with-Auto-Swarm.git
   ```
2. **สแกนดูช่องว่าง `{{PLACEHOLDERS}}` ทั้งหมดที่ยังไม่ได้เติม (`33` ตัว):**
   ```bash
   python .agents/scripts/workflow_ops.py check-placeholders
   ```
3. **กรอกรายละเอียดของโปรเจกต์คุณ:** แทนที่ `{{PLACEHOLDERS}}` ใน [AGENTS.md](./AGENTS.md), [.agents/rules/rules.md](./.agents/rules/rules.md), [.agents/skills/project-tasks/SKILL.md](./.agents/skills/project-tasks/SKILL.md), และ (หากต้องการ) `.agents/scripts/workflow_hooks.py`, `.agents/workflows/`, `.agents/templates/`
   *(บน Linux/macOS ที่ไม่มีคำสั่ง `python` ให้เปลี่ยนเป็น `python3` ใน [.agents/hooks.json](./.agents/hooks.json) โดยคงพาธ `scripts/workflow_hooks.py` เทียบกับ `.agents/` ไว้เหมือนเดิม)*
4. **ตรวจความสมบูรณ์ของระบบและรันชุดทดสอบ (ต้องผ่าน `Exit 0` ทั้งคู่):**
   ```bash
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. **เริ่มทำงานใน Antigravity:** เปิดโปรเจกต์แล้วพิมพ์ `/vibe <เป้าหมายของคุณ>` — อ่านคู่มือฉบับเต็ม (การทำงาน, ความสามารถ, คำสั่งทั้งหมด, และสิ่งที่โปรเจกต์ใหม่ **ต้องมี / ต้องเตรียม / ต้องทำ**) ได้ที่ [MANUAL_TH.md](./MANUAL_TH.md)

### ร่วมพัฒนา (Contributing) และสัญญาอนุญาต (License)

- ยินดีต้อนรับทุกข้อเสนอแนะ การแก้บั๊ก การเพิ่มความสามารถใหม่ และ Pull Request — อ่านกติกาและขั้นตอนได้ที่ [CONTRIBUTING.md](./CONTRIBUTING.md#ภาษาไทย)
- โปรเจกต์นี้เผยแพร่ภายใต้สัญญาอนุญาต **GNU General Public License v3.0 (GPL-3.0)** — ดูรายละเอียดเต็มใน [LICENSE](./LICENSE)
