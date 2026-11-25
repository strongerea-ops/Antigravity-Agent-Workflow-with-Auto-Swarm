# Antigravity Agent Workflow with Auto-Swarm

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/F6V72AZBUH)

> **Language / เลือกภาษา:** [English](#english) | [ภาษาไทย](#ภาษาไทย) | [Sponsor / สนับสนุนโปรเจกต์](#support-this-project)  
> **Complete Manuals / คู่มือฉบับสมบูรณ์:** [MANUAL_EN.md](./MANUAL_EN.md) (English) | [MANUAL_TH.md](./MANUAL_TH.md) (ภาษาไทย)

---

## English

A portable, project-agnostic **Antigravity AI Agent Workflow Starter Kit** designed for immediate drop-in adoption by any software project — featuring **First-Time User Language Selection**, **Task-Based Rules (`4` focused files)**, **Interactive Clickable `/approve` Menus (`ask_question`)**, **3-Tier Auto Triage & Auto-Swarm**, **Auto Effort & Quota Pool Priority**, **Dirty Working Tree Swarm Safety**, **6-Event Lifecycle Hooks** (including `3–7` day unresolved bug reminders), **Dynamic Python `run_workflow`**, **Rolling 15 Checkpoints ($O(1)$ Rehydration) + New-Window `/handoff`**, **ISO 8601 UTC Microsecond Timestamps**, **Zero In-Code Comments (`artifacts/comments/`)**, **Zero-Dependency Pure-Python CLI**, and **33 explicit `{{PLACEHOLDERS}}`** for your project's objectives, tasks, commands, and constraints.

### Why This Workflow Exists

Most AI coding workflows either break down as a project grows (no approval gates, no backups, bloated context) or are too heavy to reuse across projects. This starter kit balances **discipline and simplicity**:

- **First-Time Language Onboarding & Accessible Style:** On first launch, `SessionStart` detects unfilled `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` and prompts the user via a clickable `ask_question` menu (or `workflow_ops.py set-language --lang "<Language>"`), keeping system docs/thinking in English while replying in plain, non-programmer-friendly language.
- **Lean 4-Role Core Team (`10-Element Schema`) + Task-Based Rules:** `@lead`, `@builder`, `@verifier`, and `@researcher`, backed by `4` task-categorized rule files (`rules.md` index -> `coding-and-safety.md`, `commands-and-tools.md`, `agents-and-handoff.md`) so agents read only what matches the current task.
- **3-Tier Auto Triage + Auto-Swarm:** Stay in-line for 1–2 line edits (`Tier 0`), delegate scoped work to `invoke_subagent` (`Tier 1`), and scale out with `swarm` (Pool C -> Pool B -> Pool A `gemini-4-neon-*` + Auto Effort) or `run_workflow` (`Tier 2`) while preventing uncommitted-edit loss on dirty Git trees.
- **Decision-First Governance & Clean Code Hygiene:** Interactive clickable `/approve` & choice menus (`ask_question`), proactive better-approach evaluation, pre-decision Action Recommendation verdicts, Self-Mistake Governance, Zero In-Code Comments (notes stored in `artifacts/comments/`), and strict `artifacts/tools/` vs. disposable `artifacts/scratch/` separation.
- **Deterministic Runtime Guardrails (Zero External Dependencies):** Pure Python `3.10+` stdlib lifecycle hooks (`SessionStart` language onboarding + checkpoint/handoff pickup + `3–7` day unresolved bug reminders, `PreToolUse` backup & forbidden-command guards, `PostToolUse` audit, opt-in `Stop` gate with `continuationActive` protection) plus built-in `unittest` self-tests.
- **Works With or Without Git:** Microsecond Pre-Action Backups with `SHA-256` `manifest.json` and unified `-U1` diff generation (`workflow_ops.py diff`) work even in non-Git workspaces.
- **Latest Antigravity Capabilities Included:** Dynamic Python `run_workflow` (`workflow.json` + `project_fanout.py`), MCP template (Stdio + Streamable HTTP `/mcp`), and scheduled cron automation sidecar template (`CRON_TZ` + `"builtin": "schedule"`).

### 3-Minute Quick Start

> **Important (Hierarchical Rule Discovery):** Antigravity walks **up** from any opened file to the workspace root loading every `AGENTS.md` it encounters. Copy the **contents** of this repository directly into your target project's root directory (rather than nesting it inside another workspace that already has its own `AGENTS.md`).

1. **Clone or download this repository** and copy `AGENTS.md`, `.agents/`, `artifacts/`, and `MANUAL_EN.md` / `MANUAL_TH.md` into your target project's root directory:
   ```bash
   git clone https://github.com/strongerea-ops/Antigravity-Agent-Workflow-with-Auto-Swarm.git
   ```
2. **Choose your chat & artifacts language (First-Time Setup):** Open the workspace in Antigravity and pick your language from the automatic first-run menu — or set it directly via CLI:
   ```bash
   python .agents/scripts/workflow_ops.py set-language --lang "English"   # or "Thai", "Japanese", etc.
   ```
3. **List and fill remaining placeholders (`33` canonical placeholders):**
   ```bash
   python .agents/scripts/workflow_ops.py check-placeholders
   ```
   Replace `{{PLACEHOLDERS}}` in [AGENTS.md](./AGENTS.md), `.agents/rules/*.md`, [.agents/skills/project-tasks/SKILL.md](./.agents/skills/project-tasks/SKILL.md), and (optionally) `.agents/scripts/workflow_hooks.py`, `.agents/workflows/`, and `.agents/templates/`.
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
│   ├── FUNDING.yml                        # GitHub repository Sponsor button (Ko-fi)
│   ├── assets/                            # Sponsor QR codes (Ko-fi & PromptPay)
│   ├── workflows/ci.yml                   # Automated CI: verify_workflow.py + unittest (Linux & Windows)
│   ├── ISSUE_TEMPLATE/                    # Bug report & feature request templates
│   └── PULL_REQUEST_TEMPLATE.md           # PR verification checklist
├── .agents/
│   ├── rules/                             # Task-based operational rules (4 focused files)
│   │   ├── rules.md                       # Task-based index & dirty-tree swarm rule
│   │   ├── coding-and-safety.md           # Blast radius, Zero In-Code Comments, rollback
│   │   ├── commands-and-tools.md          # Hook CWD contract, artifacts/tools/ vs scratch/
│   │   └── agents-and-handoff.md          # First-time language setup, clickable /approve, /handoff, 3-7d bug reminders
│   ├── agents/                            # 4 core subagents (10-element schema)
│   │   ├── lead.md                        # Triage, /approve gate, exclusive dispatcher
│   │   ├── builder.md                     # Pre-Action Backup + approved minimal-diff implementation
│   │   ├── verifier.md                    # Read-only dynamic QA + static diff audit
│   │   └── researcher.md                  # Read-only codebase & web exploration
│   ├── skills/                            # 4 progressive-disclosure skills (<= 300 lines each)
│   │   ├── project-tasks/SKILL.md         # Project objectives, tasks & acceptance criteria placeholders
│   │   ├── plan-and-build/SKILL.md        # /vibe, /design, /approve, /code, /simplify, /finalize
│   │   ├── verify-and-debug/SKILL.md      # /test, /debug (RCA), /audit, Circuit Breaker, /compound
│   │   └── workflow-ops/SKILL.md          # O(1) rehydration, Rolling 15 checkpoints, /compact, /handoff, self-audit
│   ├── hooks.json                         # SessionStart, PreToolUse, PostToolUse, opt-in Stop (CWD = .agents/)
│   ├── scripts/                           # Pure Python 3.10+ stdlib (zero external dependencies)
│   │   ├── workflow_hooks.py              # Lifecycle hooks (language setup, checkpoints, 3-7d bug alerts, backup guard)
│   │   ├── workflow_ops.py                # set-language, backup, diff (-U1), log-turn, handoff, checkpoints, check-placeholders
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

### Support This Project

If this workflow saves you time or helps your team ship faster, you can support ongoing development via **Ko-fi** or **PromptPay**:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/F6V72AZBUH)

| Ko-fi QR Code | PromptPay QR Code (Thailand) |
| :---: | :---: |
| <img src="./.github/assets/qr-kofi.png" alt="Ko-fi QR Code" width="200" /> | <img src="./.github/assets/qr-promptpay.jpg" alt="PromptPay QR Code" width="200" /> |
| [ko-fi.com/F6V72AZBUH](https://ko-fi.com/F6V72AZBUH) | Scan with any Thai banking app |

### License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)** — see [LICENSE](./LICENSE) for full terms.

---

## ภาษาไทย

**ชุดเวิร์กโฟลว์ AI Agent สำเร็จรูปสำหรับ Antigravity (Starter Kit)** ที่นำไปวางใช้ได้ทันทีกับทุกโปรเจกต์ซอฟต์แวร์ มาพร้อม **ขั้นตอนเลือกภาษาอัตโนมัติสำหรับผู้ใช้ครั้งแรก**, **กฎแยกตามประเภทงาน (`4` ไฟล์)**, **เมนูคลิก `/approve` และตัวเลือกด้วย `ask_question`**, **3-Tier Auto Triage และ Auto-Swarm**, **Auto Effort และการเรียงลำดับโควตา Pool**, **เกราะกันงานแก้ค้างหายบน `swarm`**, **Lifecycle Hooks ครบ 6 อีเวนต์** (รวมแจ้งเตือน Bug ค้าง `3–7` วัน), **Dynamic Python `run_workflow`**, **Rolling 15 Checkpoints ($O(1)$) + คำสั่ง `/handoff` คู่กับ `/compact`**, **กฎ Zero In-Code Comments (`artifacts/comments/`)**, **มาตรฐานเวลา ISO 8601 UTC Microsecond**, และ **`{{PLACEHOLDERS}}` ชัดเจนทั้ง `33` ตัว**

### จุดเด่นของเวิร์กโฟลว์นี้

เวิร์กโฟลว์ AI จำนวนมากมักพังเมื่อโปรเจกต์ใหญ่ขึ้น (ไม่มีด่านขออนุมัติ ไม่สำรองไฟล์ ความจำแชตบวม) หรือซับซ้อนเกินกว่าจะนำไปใช้ซ้ำในโปรเจกต์อื่น ชุดตั้งต้นนี้ออกแบบให้สมดุลระหว่าง **ความรัดกุม** กับ **ความเรียบง่าย**:

- **เลือกภาษาอัตโนมัติสำหรับผู้ใช้ครั้งแรก + ภาษาเข้าใจง่าย:** เปิดใช้ครั้งแรกฮุค `SessionStart` จะตรวจจับ `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` และเปิดเมนูคลิกเลือกภาษาทันที (หรือตั้งด้วย `workflow_ops.py set-language --lang "<Language>"`) โดยคงไฟล์ระบบและการคิดภายในเป็นอังกฤษเพื่อประหยัด Token และสื่อสารด้วยภาษาธรรมดาที่คนไม่เขียนโค้ดก็เข้าใจได้
- **ทีมพื้นฐานกะทัดรัด `4` บทบาท + กฎแยกตามประเภทงาน (`4` ไฟล์):** `@lead`, `@builder`, `@verifier`, และ `@researcher` คู่กับ `.agents/rules/` ที่แบ่งตามงาน (`rules.md` สารบัญ $\rightarrow$ `coding-and-safety.md`, `commands-and-tools.md`, `agents-and-handoff.md`) ให้เอเจนต์อ่านเฉพาะส่วนที่เกี่ยวกับงานตรงหน้า
- **จัดขนาดงานอัตโนมัติ 3 ระดับ + Auto-Swarm:** งานแก้ 1–2 บรรทัดจบในแชตเดียว (`Tier 0`), งานเฉพาะทางใช้ `invoke_subagent` (`Tier 1`), และงานขนาดใหญ่หรือแยกหลายสายค่อยขยายเป็น `swarm` (Pool C $\rightarrow$ Pool B $\rightarrow$ Pool A `gemini-4-neon-*` + Auto Effort) หรือ `run_workflow` (`Tier 2`) พร้อมกฎกันงานแก้ค้างในเครื่องหาย
- **การตัดสินใจที่ชัดเจนและโค้ดสะอาด:** เมนูคลิก `/approve` และตัวเลือก (`ask_question`), ข้อเสนอทางเลือกที่ดีกว่าพร้อมประเมินความคุ้มค่า, บทสรุปฟันธงว่าควรทำหรือไม่ (Action Recommendation Verdict), กฎป้องกันความผิดพลาดซ้ำ (Self-Mistake Governance), กฎ Zero In-Code Comments (ย้ายโน้ตไป `artifacts/comments/`), และแยก `artifacts/tools/` กับ `artifacts/scratch/` ชัดเจน
- **ระบบป้องกันระดับ Runtime ที่ไม่ต้องลงไลบรารีเพิ่ม:** ฮุค Python `3.10+` มาตรฐาน (`SessionStart` เลือกภาษาครั้งแรก + ฟื้นฟู Checkpoint/Handoff + แจ้งเตือน Bug ค้าง `3–7` วัน, `PreToolUse` บังคับ Backup และบล็อกคำสั่งต้องห้าม, `PostToolUse` ตรวจสุขอนามัย, และ `Stop` แบบเปิดเลือกได้) พร้อมชุด `unittest` ทดสอบตัวเองในตัว
- **ใช้งานได้ทั้งแบบมี Git และไม่มี Git:** ระบบ Pre-Action Backup พร้อม `SHA-256` ใน `manifest.json` และคำสั่งสร้าง Unified Diff `-U1` (`workflow_ops.py diff`) ทำงานได้แม้โปรเจกต์ยังไม่ได้ตั้งค่า `.git`
- **รองรับความสามารถล่าสุดของ Antigravity ครบชุด:** สคริปต์กระจายงานขนาน `run_workflow` (`workflow.json` + `project_fanout.py`), เทมเพลต MCP (Stdio + Streamable HTTP `/mcp`), และเทมเพลตงานตั้งเวลาเบื้องหลัง (`CRON_TZ` + `"builtin": "schedule"`)

### เริ่มต้นใช้งานใน 3 นาที (Quick Start)

> **ข้อควรระวัง (Hierarchical Rule Discovery):** Antigravity จะโหลดไฟล์ `AGENTS.md` เดินขึ้นจากไฟล์ที่เปิดอยู่ไปยัง Root ของ Workspace ดังนั้นให้คัดลอก **ไฟล์ข้างใน** Repository นี้ไปวางที่ **Root ของโปรเจกต์ใหม่โดยตรง** (หลีกเลี่ยงการวางซ้อนใต้ Workspace อื่นที่มี `AGENTS.md` อยู่แล้ว)

1. **โคลนหรือดาวน์โหลด Repository นี้** แล้วคัดลอก `AGENTS.md`, `.agents/`, `artifacts/`, และ `MANUAL_TH.md` / `MANUAL_EN.md` ไปวางที่ Root ของโปรเจกต์เป้าหมาย:
   ```bash
   git clone https://github.com/strongerea-ops/Antigravity-Agent-Workflow-with-Auto-Swarm.git
   ```
2. **เลือกภาษาสำหรับใช้งานครั้งแรก (First-Time Setup):** เปิด Workspace ใน Antigravity แล้วคลิกเลือกภาษาจากเมนูที่แสดงขึ้นอัตโนมัติ หรือตั้งค่าผ่านคำสั่ง CLI ได้ทันที:
   ```bash
   python .agents/scripts/workflow_ops.py set-language --lang "Thai"   # หรือ "English", "Japanese" ฯลฯ
   ```
3. **สแกนและกรอกช่องว่าง `{{PLACEHOLDERS}}` ที่เหลือ (`33` ตัว):**
   ```bash
   python .agents/scripts/workflow_ops.py check-placeholders
   ```
   แทนที่ `{{PLACEHOLDERS}}` ใน [AGENTS.md](./AGENTS.md), `.agents/rules/*.md`, [.agents/skills/project-tasks/SKILL.md](./.agents/skills/project-tasks/SKILL.md), และ (หากต้องการ) `.agents/scripts/workflow_hooks.py`, `.agents/workflows/`, `.agents/templates/`
   *(บน Linux/macOS ที่ไม่มีคำสั่ง `python` ให้เปลี่ยนเป็น `python3` ใน [.agents/hooks.json](./.agents/hooks.json) โดยคงพาธ `scripts/workflow_hooks.py` เทียบกับ `.agents/` ไว้เหมือนเดิม)*
4. **ตรวจความสมบูรณ์ของระบบและรันชุดทดสอบ (ต้องผ่าน `Exit 0` ทั้งคู่):**
   ```bash
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. **เริ่มทำงานใน Antigravity:** เปิดโปรเจกต์แล้วพิมพ์ `/vibe <เป้าหมายของคุณ>` — อ่านคู่มือฉบับเต็ม (การทำงาน, ความสามารถ, คำสั่งทั้งหมด, และสิ่งที่โปรเจกต์ใหม่ **ต้องมี / ต้องเตรียม / ต้องทำ**) ได้ที่ [MANUAL_TH.md](./MANUAL_TH.md)

### สนับสนุนโปรเจกต์ (Sponsor)

หากเวิร์กโฟลว์นี้ช่วยให้คุณทำงานได้เร็วและเป็นระบบขึ้น สามารถร่วมสนับสนุนการพัฒนาต่อยอดได้ผ่าน **Ko-fi** หรือ **พร้อมเพย์ (PromptPay)**:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/F6V72AZBUH)

| QR Code Ko-fi | QR Code พร้อมเพย์ (PromptPay) |
| :---: | :---: |
| <img src="./.github/assets/qr-kofi.png" alt="Ko-fi QR Code" width="200" /> | <img src="./.github/assets/qr-promptpay.jpg" alt="PromptPay QR Code" width="200" /> |
| [ko-fi.com/F6V72AZBUH](https://ko-fi.com/F6V72AZBUH) | สแกนผ่านแอปธนาคารในประเทศไทย |

### ร่วมพัฒนา (Contributing) และสัญญาอนุญาต (License)

- ยินดีต้อนรับทุกข้อเสนอแนะ การแก้บั๊ก การเพิ่มความสามารถใหม่ และ Pull Request — อ่านกติกาและขั้นตอนได้ที่ [CONTRIBUTING.md](./CONTRIBUTING.md#ภาษาไทย)
- โปรเจกต์นี้เผยแพร่ภายใต้สัญญาอนุญาต **GNU General Public License v3.0 (GPL-3.0)** — ดูรายละเอียดเต็มใน [LICENSE](./LICENSE)
