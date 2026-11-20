# Contributing to Antigravity Agent Workflow with Auto-Swarm
# คู่มือการร่วมพัฒนาโปรเจกต์

> **Language / เลือกภาษา:** [English](#english) | [ภาษาไทย](#ภาษาไทย)

---

## English

Thank you for helping improve and evolve this portable Antigravity Agent Workflow! This guide explains how to propose changes, run automated checks, and keep the starter kit clean, truthful, and universally reusable.

### Ways to Contribute

- **Bug Fixes:** Fix issues in hooks (`workflow_hooks.py`), operations CLI (`workflow_ops.py`), verifier (`verify_workflow.py`), or workflow templates.
- **Capability Upgrades:** Add support for newly released Antigravity customization capabilities (hooks, `run_workflow`, `swarm`, MCP, plugins, automations) while keeping the starter kit lean.
- **Documentation & Translations:** Improve clarity in [README.md](./README.md), [MANUAL_EN.md](./MANUAL_EN.md), and [MANUAL_TH.md](./MANUAL_TH.md), or add opt-in examples without polluting core project-agnostic files.

### Core Design Invariants (Please Keep Intact)

1. **Project-Agnostic Core:** Never hardcode domain-specific business logic, personal usernames, secrets, or local absolute paths into the starter kit. Use explicit `{{PLACEHOLDERS}}` instead.
2. **Zero External Dependencies:** All scripts under `.agents/scripts/` MUST use **Pure Python 3.10+ Standard Library** only so any project can run them immediately.
3. **Language Split & Documentation Parity:**
   - **Agent-Loaded System Files (English 100%):** Keep `AGENTS.md`, `.agents/rules/`, `.agents/agents/`, `.agents/skills/`, `.agents/scripts/`, `.agents/workflows/`, and `.agents/templates/` in **English** to conserve agent context tokens.
   - **Human-Facing GitHub Docs (English & Thai):** Keep both English and Thai sections in sync across [README.md](./README.md), [CONTRIBUTING.md](./CONTRIBUTING.md), [MANUAL_EN.md](./MANUAL_EN.md), and [MANUAL_TH.md](./MANUAL_TH.md) whenever adding commands, capabilities, or placeholders.
4. **Budget & Schema Constraints:**
   - `AGENTS.md` MUST stay $\le 24,000$ bytes (`UTF-8`, `BOM=False`).
   - Each `.agents/skills/<name>/SKILL.md` MUST stay $\le 300$ lines with matching YAML `name`.
   - Every `.agents/agents/<name>.md` MUST follow the **10-Element Agent Schema** (never put `swarm` in YAML `tools:`; keep `model` in `inherit`/`flash_lite`/`flash`/`pro`).
   - `.agents/hooks.json` script paths MUST resolve relative to `.agents/` (Antigravity Hook Runner executes with CWD = `.agents/`).
   - Never commit hardcoded drive letters, UTF-8 BOM, broken relative links, or code truncation placeholders (`// ... existing code ...`).

### Pull Request Workflow

1. **Fork** the repository and create a descriptive feature or fix branch from `main`.
2. Make the **smallest complete change** and update all cross-references (including English & Thai docs if behavior, commands, or placeholders change).
3. Add or update unit tests in [.agents/scripts/test_workflow_ops_and_hooks.py](./.agents/scripts/test_workflow_ops_and_hooks.py) whenever modifying Python scripts or hooks.
4. Run both verification commands locally before opening a Pull Request (both MUST exit `0`):
   ```bash
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. Open a Pull Request describing **what changed**, **why**, and the **exact verification output**.

### License

By contributing to this repository, you agree that your contributions will be licensed under the **GNU General Public License v3.0 (GPL-3.0)** ([LICENSE](./LICENSE)).

---

## ภาษาไทย

ขอบคุณที่เข้ามามีส่วนร่วมพัฒนาและต่อยอด **Antigravity Agent Workflow with Auto-Swarm**! คู่มือนี้สรุปแนวทางการส่งงาน การรันชุดตรวจสอบอัตโนมัติ และกฎเหล็กที่ช่วยคงให้เทมเพลตนี้สะอาด โปร่งใส และนำไปใช้ได้กับทุกโปรเจกต์

### แนวทางการมีส่วนร่วม

- **แก้บั๊ก (Bug Fixes):** ปรับปรุงข้อผิดพลาดในระบบฮุค (`workflow_hooks.py`), คำสั่ง CLI (`workflow_ops.py`), ตัวตรวจสอบ (`verify_workflow.py`), หรือไฟล์เทมเพลต
- **ต่อยอดความสามารถใหม่ (Capability Upgrades):** เพิ่มการรองรับฟีเจอร์ใหม่ของ Antigravity (เช่น Hooks, `run_workflow`, `swarm`, MCP, Plugins, Scheduled Automations) โดยยังคงความกะทัดรัดของชุดเริ่มต้น
- **ปรับปรุงเอกสารและคำแปล (Docs & Translations):** เพิ่มความชัดเจนให้ [README.md](./README.md), [MANUAL_EN.md](./MANUAL_EN.md), และ [MANUAL_TH.md](./MANUAL_TH.md) หรือเพิ่มเทมเพลตเสริมโดยไม่ทำให้แกนกลางผูกติดกับโดเมนเฉพาะ

### กฎหลักที่ต้องรักษาไว้เสมอ (Core Design Invariants)

1. **แกนกลางต้องใช้ได้กับทุกโปรเจกต์ (Project-Agnostic):** ห้ามใส่ตรรกะเฉพาะธุรกิจ ชื่อผู้ใช้ส่วนตัว ความลับ/API Key หรือพาธเครื่องส่วนตัวลงในไฟล์ Commit ให้ใช้ `{{PLACEHOLDERS}}` แทนเสมอ
2. **ห้ามเพิ่ม Dependency ภายนอก:** สคริปต์ทั้งหมดใน `.agents/scripts/` ต้องใช้ **Pure Python 3.10+ Standard Library** เท่านั้น เพื่อให้ทุกโปรเจกต์รันได้ทันทีโดยไม่ต้องลงแพ็กเกจเพิ่ม
3. **นโยบายแยกภาษาเพื่อประหยัด Token และความตรงกันของคู่มือ:**
   - **ไฟล์ระบบที่เอเจนต์โหลด (English 100%):** คง `AGENTS.md`, `.agents/rules/`, `.agents/agents/`, `.agents/skills/`, `.agents/scripts/`, `.agents/workflows/`, และ `.agents/templates/` เป็น **ภาษาอังกฤษ** เพื่อประหยัด Token ของเอเจนต์
   - **เอกสารสำหรับคนอ่านบน GitHub (English & ภาษาไทย):** เมื่อเพิ่มคำสั่ง ความสามารถ หรือ Placeholder ใหม่ ให้ปรับเนื้อหาทั้งอังกฤษและไทยให้สอดคล้องกันใน [README.md](./README.md), [CONTRIBUTING.md](./CONTRIBUTING.md), [MANUAL_EN.md](./MANUAL_EN.md), และ [MANUAL_TH.md](./MANUAL_TH.md)
4. **เพดานขนาดไฟล์และมาตรฐาน Schema:**
   - `AGENTS.md` ต้องมีขนาด $\le 24,000$ bytes (`UTF-8`, `BOM=False`)
   - ไฟล์ `.agents/skills/<name>/SKILL.md` แต่ละไฟล์ต้องยาว $\le 300$ บรรทัด และ YAML `name` ตรงกับชื่อโฟลเดอร์
   - ไฟล์ `.agents/agents/<name>.md` ทุกไฟล์ต้องครบ **10-Element Agent Schema** (ห้ามใส่ `swarm` ใน YAML `tools:`; คง `model` อยู่ใน `inherit`/`flash_lite`/`flash`/`pro`)
   - พาธสคริปต์ใน `.agents/hooks.json` ต้องเทียบกับโฟลเดอร์ `.agents/` เสมอ (เพราะ Antigravity Hook Runner รันด้วย CWD = `.agents/`)
   - ห้าม Commit Drive Letter, UTF-8 BOM, ลิงก์ Relative ที่เสีย, หรือข้อความตัดทอนโค้ด (`// ... existing code ...`)

### ขั้นตอนการส่ง Pull Request (PR)

1. **Fork** Repository นี้ แล้วสร้าง Branch ใหม่จาก `main` พร้อมตั้งชื่อให้สื่อถึงงานที่ทำ
2. แก้ไขให้กระชับตรงจุดที่สุด (**Smallest Complete Change**) และอัปเดตจุดอ้างอิงรวมถึงเอกสารภาษาอังกฤษ/ไทยให้ครบ `100%`
3. เพิ่มหรือปรับชุดทดสอบใน [.agents/scripts/test_workflow_ops_and_hooks.py](./.agents/scripts/test_workflow_ops_and_hooks.py) ทุกครั้งที่แก้สคริปต์ Python หรือฮุค
4. รันคำสั่งตรวจสอบทั้ง 2 ชุดในเครื่องก่อนเปิด Pull Request (ต้องผ่าน **`Exit 0`** ทั้งคู่ — GitHub Actions CI จะรันชุดเดียวกันตรวจซ้ำบน Linux และ Windows):
   ```bash
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. เปิด Pull Request พร้อมอธิบาย **สิ่งที่เปลี่ยน**, **เหตุผล**, และแนบ **ผลลัพธ์จากคำสั่งตรวจสอบจริง**

### สัญญาอนุญาต (License)

การส่งโค้ดหรือเอกสารเข้าสู่ Repository นี้ถือว่าผู้ส่งยินยอมให้เผยแพร่งานภายใต้สัญญาอนุญาต **GNU General Public License v3.0 (GPL-3.0)** ([LICENSE](./LICENSE))
