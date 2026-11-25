# คู่มือระบบและการเริ่มต้นใช้งานสำหรับโปรเจกต์ใหม่ (ฉบับภาษาไทย)

> **คู่มือฉบับภาษาอังกฤษ (English Edition):** [MANUAL_EN.md](./MANUAL_EN.md)  
> **คู่มือกฎหลัก (Root Index):** [AGENTS.md](./AGENTS.md) | **กฎปฏิบัติการเสริม:** [.agents/rules/rules.md](./.agents/rules/rules.md)

## สารบัญ
1. [โครงสร้างและการทำงานของระบบ (Functionality)](#1-โครงสร้างและการทำงานของระบบ-functionality)
2. [ความสามารถทั้งหมดของระบบ (Capabilities)](#2-ความสามารถทั้งหมดของระบบ-capabilities)
3. [รายการคำสั่งทั้งหมดที่มีให้ใช้ (All Available Commands)](#3-รายการคำสั่งทั้งหมดที่มีให้ใช้-all-available-commands)
4. [ตัวอย่างลำดับการทำงานจริงตั้งแต่ต้นจนจบ](#4-ตัวอย่างลำดับการทำงานจริงตั้งแต่ต้นจนจบ)
5. [คู่มือเริ่มต้นสำหรับโปรเจกต์ใหม่: ต้องมีอะไร • ต้องเตรียมอะไร • ต้องทำอะไร](#5-คู่มือเริ่มต้นสำหรับโปรเจกต์ใหม่-ต้องมีอะไร--ต้องเตรียมอะไร--ต้องทำอะไร)

---

## 1. โครงสร้างและการทำงานของระบบ (Functionality)

เวิร์กโฟลว์นี้จัดระเบียบการทำงานของ AI Agent ออกเป็น **6 ชั้นที่ทำงานประสานกัน** เพื่อให้ทำงานได้รวดเร็ว คาดเดาได้ ปลอดภัย และประหยัด Token กับทุกโปรเจกต์

| ชั้นระบบ | ไฟล์ / โฟลเดอร์ | หน้าที่และการทำงานจริง |
|---|---|---|
| **1. กฎหลักระดับรูท** | [AGENTS.md](./AGENTS.md) | คู่มือหลักที่ระบบโหลดเสมอ ($\le 24\text{ KB}$): นโยบายภาษา, คำสั่งหลัก, ข้อห้ามเด็ดขาด, ตารางบทบาทและโมเดล 4 ตำแหน่ง, และแนวทางปฏิบัติ `0–12` |
| **2. กฎปฏิบัติการแยกตามประเภทงาน (`4` ไฟล์)** | [.agents/rules/rules.md](./.agents/rules/rules.md) | สารบัญนำทางตามงานเพื่อให้เอเจนต์อ่านเฉพาะไฟล์ที่เกี่ยวข้อง (`coding-and-safety.md`, `commands-and-tools.md`, `agents-and-handoff.md`) |
| **3. เอเจนต์เฉพาะทาง (`4` บทบาท)** | `.agents/agents/*.md` | นิยามเอเจนต์ครบ 10 องค์ประกอบ (`@lead`, `@builder`, `@verifier`, `@researcher`) แยกหน้าที่ชัดเจนระหว่างวางแผน, ลงมือแก้, ตรวจ/เทสต์แบบอ่านอย่างเดียว, และค้นคว้าข้อมูล |
| **4. ทักษะโหลดตามความจำเป็น (`4` สกิล)** | `.agents/skills/*/SKILL.md` | คู่มือขั้นตอนเฉพาะทางแบบ Progressive Disclosure ($\le 300$ บรรทัดต่อไฟล์) โหลดเฉพาะตอนเรียกใช้เพื่อไม่ให้กินหน่วยความจำแชตโดยเปล่าประโยชน์ |
| **5. Lifecycle Hooks และ Python CLI** | [.agents/hooks.json](./.agents/hooks.json), `.agents/scripts/*.py` | สคริปต์ Python 3.10+ มาตรฐาน (ไม่ต้องติดตั้งไลบรารีเพิ่ม) ทำงานตรงตามจังหวะ Lifecycle: ฟื้นฟูบริบทตอนเปิดแชต, บล็อกการแก้ไฟล์หากยังไม่ Backup, บล็อกคำสั่งต้องห้าม, ตรวจสุขอนามัยหลังแก้, สร้าง Diff และชุดทดสอบในตัว |
| **6. สถานะถาวรและส่วนขยายเสริม** | `.agents/ck/`, `artifacts/`, `backup/`, `.agents/workflows/`, `.agents/templates/` | Rolling 15 Checkpoints, เอกสาร 4 เสาหลัก, แบ็กอัปพร้อม SHA-256, สคริปต์กระจายงาน `run_workflow`, และเทมเพลตเสริม MCP/งานตั้งเวลาอัตโนมัติ |

### ตารางแยกสิ่งที่ระบบ/สคริปต์บังคับจริง เทียบกับกฎระดับ Prompt (ความโปร่งใส 100%)

| กลไก | ระดับการบังคับ | พฤติกรรมที่เกิดขึ้นจริง |
|---|---|---|
| เพดาน `AGENTS.md` `24,000` bytes และการค้นหาแบบ Hierarchical | **Antigravity Runtime (บังคับจริง)** | ระบบตัดทอนเนื้อหาหากเกิน 24 KB และค้นหาเดินขึ้นจากไฟล์ที่เปิดอยู่ไปยัง Root ของ Workspace |
| `SessionStart` เลือกภาษาครั้งแรก, ฟื้นฟู Checkpoint และเตือน Bug ค้าง (`hooks.json`) | **Hook Script (บังคับจริง)** | รัน `scripts/workflow_hooks.py session-start` ด้วย CWD = `.agents/` เพื่อตรวจจับ `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` ที่ยังไม่ตั้งค่า, แทรกสรุป Checkpoint/Handoff ล่าสุด, และแจ้งเตือน Bug ค้างอายุ `3–7` วันใน `artifacts/bug-reports/README.md` |
| `PreToolUse` ดัก Backup และคำสั่งต้องห้าม | **Hook Script (บังคับจริง)** | คืนค่า `decision: "deny"` บล็อก `edit_file`/`write_file` ทันทีหากยังไม่มี Backup Manifest ของวันนั้น หรือบล็อก `run_command` ที่ตรงกับ Regex ต้องห้าม |
| `PostToolUse` ตรวจสุขอนามัยหลังแก้ (`last_alert.log`) | **Hook Script (บังคับจริง)** | รัน `verify_workflow.audit_workspace()` หลังแก้ไฟล์เวิร์กโฟลว์ แล้วเขียนหรือล้าง `.agents/ck/last_alert.log` อัตโนมัติ |
| `Stop` ด่านกันปิดงานเมื่อมี Alert (`alert-stop-gate`) | **Hook Script (บังคับจริงเมื่อเปิดใช้)** | ปิดไว้เป็นค่าเริ่มต้น (`"enabled": false`) เพื่อความไม่จุกจิก เมื่อเปิดใช้จะเช็ก `continuationActive` กันลูปไม่รู้จบ |
| `verify_workflow.py` และ `test_workflow_ops_and_hooks.py` | **CLI Tool (บังคับจริง)** | ตรวจเชิงประจักษ์ได้ Exit Code `0` / `1` สำหรับ Schema, ลิงก์เสีย, BOM, Syntax และพฤติกรรมของ Hook |
| ด่าน `/approve`, โหมด `no-code / no-detail`, Circuit Breaker ($N \ge 3$), `Post-Approval Auto-Fix` | **Prompt-Governed Policy** | กำกับผ่านกฎใน `AGENTS.md` และบทบาทเอเจนต์ โดยให้ผู้ใช้ตรวจสอบร่วม |
| โมเดลแชตหลัก, Thinking Budget และการเปิดหน้าต่างแชตใหม่ | **UI-Only Control** | เอเจนต์สลับโมเดลหรือเปิดหน้าต่างใหม่เองไม่ได้ ต้องเลือกจาก UI / กด `New Conversation` *(ส่วน `/handoff` สร้าง Handoff Packet และให้ `SessionStart` รับช่วงต่ออัตโนมัติ)* |

---

## 2. ความสามารถทั้งหมดของระบบ (Capabilities)

1. **เลือกภาษาอัตโนมัติสำหรับผู้ใช้ครั้งแรก + แยกภาษาเพื่อประหยัด Token:** เมื่อเปิดใช้งานครั้งแรกขณะที่ `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` ยังไม่ถูกตั้งค่า ฮุค `SessionStart` จะสั่งให้ `@lead` แสดงเมนูคลิกเลือกภาษา (`ask_question`) แล้วบันทึกด้วย `workflow_ops.py set-language --lang "<Language>"` (พร้อมสำรองไฟล์อัตโนมัติ) โดยไฟล์ระบบและกระบวนการคิดภายในคงเป็นอังกฤษ ส่วนการสนทนาและ `artifacts/` ใช้ภาษาที่เลือกด้วยถ้อยคำเรียบง่ายที่คนไม่เขียนโค้ดก็เข้าใจได้
2. **คุยกระชับเป็นค่าเริ่มต้น, ขยายละเอียดเฉพาะตอนจำเป็น และฟันธงคำแนะนำ:** การถามตอบทั่วไปตอบเฉพาะหลักการและพฤติกรรม `3–5` ข้อ และจะขยายละเอียดอัตโนมัติตอน **วางแผนก่อน `/approve`** (พร้อมเมนูคลิก `ask_question`, ข้อเสนอทางเลือกที่ดีกว่า และ Acceptance Criteria), **ลงมือแก้โค้ด** (สรุป 3 ส่วน + ลิงก์ไฟล์จริง + `.diff`), หรือเมื่อสั่ง `/more-detail` โดยงานวิเคราะห์/ทดสอบก่อนตัดสินใจจะปิดท้ายด้วย **Action Recommendation Verdict** (ควรทำหรือไม่พร้อมเหตุผล)
3. **โหลดเฉพาะสิ่งที่จำเป็น, `/compact` และ `/handoff` ย้ายหน้าต่างแชตใหม่:** โหลดสกิลเฉพาะตอนใช้งาน, อ่านไฟล์ใหญ่แบบเจาะช่วง ($\le 300$ บรรทัด), เมื่อครบ `10–12` เทิร์น (`~35` calls) หรือพบ `<CONTEXT_SUMMARY>` ระบบจะเสนอ **`/compact`** (ทำต่อหน้าต่างเดิม) คู่กับ **`/handoff`** (สร้าง `.agents/ck/HANDOFF.md` + `artifacts/handoffs/` + Starter Prompt พร้อมให้ `SessionStart` ในหน้าต่างใหม่รับช่วงต่ออัตโนมัติ) พร้อมฟื้นความจำแบบ $O(1)$ (~250 tokens) จาก `Conversations/README.md` + `.agents/ck/context.json`
4. **จัดขนาดงานอัตโนมัติ 3 ระดับ + โควตา Pool + Auto Effort:**
   - **Tier 0 In-line:** แก้ 1–2 บรรทัด หรือถามตอบสั้น ($\le 3$ reads) จบในแชตเดียว
   - **Tier 1 `invoke_subagent`:** งานเฉพาะทาง (`@researcher`, `@builder`, `@verifier`) หรือแก้ `1–8` ไฟล์
   - **Tier 2 `swarm` / `run_workflow`:** งานแก้ `>= 9` ไฟล์ หรือแยก `>= 2` สายอิสระใช้ `swarm`; งานอ่าน/ตรวจหลายไฟล์แบบมีโครงสร้างใช้ `run_workflow`
   - ลำดับโควตาสำหรับ `swarm`: ใช้ **Pool C (Claude/GPT)** จนหมด `0%` ก่อนสลับ **Pool B (`gemini-4-argon-*`)** และ **Pool A (เลือก `gemini-4-neon-*` ก่อน)** พร้อม Auto Effort ตามบทบาท และหยุด Auto-Swarm เมื่อโควตาสำรองต่ำกว่า `20%`
5. **เกราะกันงานแก้ค้างหายบน `swarm` (Dirty Working Tree Safety):** หากในเครื่องมีไฟล์แก้ค้างที่ยังไม่ Commit **ห้ามใช้ `workspace:"share"`** (git worktree จะ checkout `HEAD` ทำให้ไฟล์แก้ค้างหาย) ให้ใช้ `workspace:"inherit"` คู่กับการแบ่งไฟล์ไม่ทับซ้อนและ Pre-Action Backup รวมแทน
6. **ฮุคควบคุมวงจรการทำงานครบ 6 อีเวนต์ (CWD = `.agents/`):** เชื่อมต่อพร้อมใช้ 4 อีเวนต์หลักใน [.agents/hooks.json](./.agents/hooks.json) (`SessionStart`, `PreToolUse` สำหรับทั้งแก้ไฟล์และรันคำสั่ง, `PostToolUse`, และ `Stop` แบบเปิดเลือกได้) และรองรับการต่อยอด `PreInvocation` / `PostInvocation`
7. **สคริปต์กระจายงานแบบขนานด้วย Python (`run_workflow`):** มีต้นแบบ [.agents/workflows/project_fanout.py](./.agents/workflows/project_fanout.py) + [.agents/workflows/workflow.json](./.agents/workflows/workflow.json) ใช้ `phase`, `agent`, `parallel`, `log`, JSON `schema` และตรวจ `Args` ขาเข้า
8. **สำรองข้อมูลและสร้าง Diff แม้ไม่มี Git:** `workflow_ops.py backup` บันทึกไฟล์เดิมพร้อม `SHA-256` และบันทึกไฟล์ใหม่เป็น `"status": "absent"` เพื่อ Rollback ได้แม่นยำ; `workflow_ops.py diff` สร้างไฟล์ `.diff` (`-U1`) เทียบกับ Backup Manifest ได้แม้ไม่มี `.git`
9. **กลไกกันพลาด สุขอนามัยโค้ด และเรียนรู้ถาวร:** ขออนุมัติครบ 4 ขั้นพร้อมเมนูคลิก `ask_question`, กฎป้องกันความผิดพลาดซ้ำของเอเจนต์ (Self-Mistake Governance), กฎ Zero In-Code Comments (ย้ายโน้ตไป `artifacts/comments/`), แยก `artifacts/tools/` กับ `artifacts/scratch/`, แจ้งเตือน Bug ค้าง `3–7` วัน, แยก `@verifier` แบบอ่านอย่างเดียว, ค้านด้วยหลักฐาน 3 ส่วน (`Evidence-Based Objection`), ล็อกข้อยุติ (`session-settled:`), ท้าทายสมมติฐาน ($N=2$), ตัดวงจร ($N \ge 3$), และ `Compound Learning` (`Test/Lint -> Rule -> Solution Doc`)
10. **เทมเพลตเสริม MCP และงานตั้งเวลาอัตโนมัติ (Opt-In):** เตรียม [.agents/templates/mcp_config.example.json](./.agents/templates/mcp_config.example.json) (รองรับทั้ง Stdio และ Streamable HTTP `/mcp`, ไม่รองรับ legacy SSE) และ [.agents/templates/sidecar.schedule.example.json](./.agents/templates/sidecar.schedule.example.json) (`"builtin": "schedule"`, `CRON_TZ`, `restart_policy: "always"`)

---

## 3. รายการคำสั่งทั้งหมดที่มีให้ใช้ (All Available Commands)

### A. คำสั่งหลักของแพลตฟอร์ม Antigravity (Native Slash Commands)
*(พิมพ์ตรงในช่องแชตของ Antigravity)*

| คำสั่ง | หน้าที่การใช้งาน |
|---|---|
| `/plan` | เข้าโหมดวางแผนทีละขั้นตอนอย่างละเอียดก่อนลงมือทำ |
| `/compact` | บีบอัดประวัติแชตที่ยาวเพื่อคืนพื้นที่หน่วยความจำ (แนะนำเมื่อครบ 10–12 เทิร์น) |
| `/goal` | สั่งงานระยะยาวให้ทำต่อเนื่องอย่างละเอียดจนกว่าจะบรรลุเป้าหมายครบถ้วน |
| `/schedule` | ตั้งตัวจับเวลาครั้งเดียวหรือรอบการทำงานซ้ำในเซสชัน |
| `/automation` | ตัวช่วยสร้างงานเบื้องหลังตามตารางเวลา (Cron Sidecar) |
| `/browser` | สั่งเปิดเว็บ ตรวจหน้าจอ UI หรือโต้ตอบกับเว็บแอปผ่าน Browser Subagent |
| `/grill-me` | ให้ AI สัมภาษณ์ทีละประเด็นเพื่อเคลียร์ข้อกำหนดที่ยังคลุมเครือ |
| `/teamwork` | ระดมทีมเอเจนต์ทำงานขนานกันสำหรับโปรเจกต์ขนาดใหญ่ |
| `/learn` | บันทึกแนวทางที่แก้ไขแล้วให้ระบบจดจำไว้ใช้ในงานถัดไป |
| `/boost` | เปิดโหมดคิดเชิงลึกหลายมุมมองและการตรวจรับเข้มข้นสำหรับงานซับซ้อน |
| `/plugin` | จัดการ เปิด/ปิด ติดตั้ง หรือแพ็กชุดเครื่องมือเป็น Plugin |

### B. คำสั่งลัดประจำเวิร์กโฟลว์ในแชต (Prompt Action Triggers)
*(กำกับพฤติกรรมผ่าน `AGENTS.md` และสกิลใน `.agents/skills/`)*

| คำสั่ง | สกิล / ผู้รับผิดชอบ | พฤติกรรมที่เกิดขึ้น |
|---|---|---|
| `/vibe <เป้าหมาย>` | `plan-and-build` (`@lead`) | เริ่มวงจรพัฒนาครบขั้นตอนตั้งแต่คัดกรอง → วางแผน → `/approve` → สร้าง → ตรวจรับ → ปิดงาน |
| `/design <หัวข้อ>` | `plan-and-build` (`@lead`) | ออกแบบพิมพ์เขียว (`artifacts/blueprints/` พร้อม `U-IDs`, ตรวจความขัดแย้ง, Rollback และทางเลือก) โดยยังไม่แก้โค้ด |
| `/approve [Option]` | `plan-and-build` (`@lead`) | อนุมัติแผนเพื่อให้ `@builder` ลงมือสร้างหรือแก้ไขไฟล์ตามขอบเขตที่ตกลง |
| `/code` | `plan-and-build` (`@builder`) | ทำ Pre-Action Backup และลงมือเขียนโค้ดแบบ Minimal Diff ภายในขอบเขตที่ผ่าน `/approve` |
| `/simplify` | `plan-and-build` (`@builder`) | ลดความซับซ้อนของโค้ดที่เพิ่งแก้ผ่าน 5 เลนส์ (Reuse, Quality, Efficiency, Test Value, Comments) โดยคงพฤติกรรมและเทสต์เดิมครบ 100% |
| `/test` | `verify-and-debug` (`@verifier`) | รันชุดทดสอบจริงและรายงานคำสั่ง, Exit Code, ผลลัพธ์ และ `Untested Scope` ตามความจริง |
| `/debug <ปัญหา>` | `verify-and-debug` (`@verifier`) | สืบสวนหาสาเหตุรากเหง้าด้วย Causal-Chain RCA (`Hypothesis -> Prediction -> Check`), ท้าทายสมมติฐาน ($N=2$) และ Circuit Breaker ($N \ge 3$) |
| `/audit` | `verify-and-debug` (`@verifier`) | ตรวจ Static Diff, ไล่ Callers 100% และตรวจ Never Cut List แบบอ่านอย่างเดียว |
| `/finalize` | `plan-and-build` (`@lead`) | ตรวจรับ Acceptance Criteria ทีละข้อ, สร้าง `.diff`, ประเมิน `/compound` และบันทึกประวัติประจำรอบ |
| `/compound` | `verify-and-debug` (`@lead`) | แปลงบทเรียนหลังแก้ปัญหาสำเร็จเป็นเกราะป้องกันถาวรตามลำดับที่ถูกที่สุด (`Test/Lint -> Rule -> Solution Doc`) |
| `/ck` | `workflow-ops` (`@lead`) | บันทึกหรือตรวจสอบสถานะ Rolling 15 Checkpoints ใน `.agents/ck/` |
| `/handoff` | `workflow-ops` (`@lead`) | ใช้งานคู่กับคำเตือน `/compact`: สร้าง `.agents/ck/HANDOFF.md` และบันทึกใน `artifacts/handoffs/` พร้อมตั้งสถานะ `HANDOFF_READY` ให้ `SessionStart` ในหน้าต่างแชตใหม่รับช่วงต่อทันที และแสดง Starter Prompt พร้อมคัดลอกวาง |
| `/concept`, `/no-code`, `/no-detail` | `AGENTS.md` §0 (`@lead`) | บังคับตอบเฉพาะหลักการและพฤติกรรม `3–5` ข้อแบบเข้าใจง่าย งดโค้ดและรายชื่อไฟล์ที่ไม่ถูกแก้ |
| `/more-detail` | `AGENTS.md` §0 (`@lead`) | ขยายคำตอบเชิงลึกครบทุกไฟล์ บรรทัด โค้ด และผลลัพธ์ละเอียด |
| `/refactor-agents` | `workflow-ops` (`@lead`) | ตรวจและปรับโครงสร้าง `AGENTS.md` กับ `.agents/` ให้กระชับและผ่านตัวตรวจ Schema |

### C. การเรียกบทบาทเอเจนต์เฉพาะทาง (`@role`)

| บทบาท | โมเดล Tier 1 | สิทธิ์แก้ไฟล์ | สิทธิ์รันคำสั่ง | เหมาะกับงานแบบใด |
|---|---|---|---|---|
| `@lead` | `pro` | ได้ (ผู้ประสานงาน) | `auto` | คัดกรองงาน, วางแผน, ตรวจ Conflict, กำกับ `/approve`, และปิดงาน |
| `@builder` | `flash` | ได้ (เฉพาะ Scope ที่อนุมัติ) | `auto` | ลงมือแก้ไฟล์ตาม `U-ID` พร้อม Pre-Action Backup และ Minimal Diff |
| `@verifier` | `flash` | **ไม่ได้ (Read-Only)** | `sandbox` | รันเทสต์จริง, สืบสวน RCA, และตรวจ Static Diff โดยไม่แก้ไฟล์ |
| `@researcher` | `flash_lite` | **ไม่ได้ (Read-Only)** | `off` | สำรวจโค้ด, หา Callers, และค้นเอกสารอย่างประหยัดโควตา |

### D. คำสั่ง Python CLI ที่ติดมากับเวิร์กโฟลว์
*(รันจากโฟลเดอร์ Root ของโปรเจกต์; บน Linux/macOS ที่ไม่มี `python` ให้เปลี่ยนเป็น `python3`)*

| คำสั่ง | หน้าที่การใช้งาน |
|---|---|
| `python .agents/scripts/workflow_ops.py set-language --lang "<Language>"` | ตั้งค่าภาษา `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` ครบทุกไฟล์เวิร์กโฟลว์ (พร้อม Pre-Action Backup อัตโนมัติ) และบันทึก `chat_language` ลง `context.json` |
| `python .agents/scripts/workflow_ops.py check-placeholders` | สแกนและแสดงรายการ `{{PLACEHOLDER}}` ที่ยังไม่ได้เติมทั้งหมดพร้อมไฟล์และเลขบรรทัด |
| `python .agents/scripts/workflow_ops.py check-placeholders --fail-on-found` | สแกนช่องว่างพร้อมคืน `Exit 1` หากยังมีจุดที่กรอกไม่ครบ (ใช้เป็น Readiness Gate) |
| `python .agents/scripts/workflow_ops.py backup --topic "<slug>" <files...>` | สำรองไฟล์ก่อนแก้ไขลง `backup/` พร้อม `SHA-256` และสถานะไฟล์ใหม่ (`absent`) |
| `python .agents/scripts/workflow_ops.py diff --output "artifacts/diffs/YYYY-MM-DD/<slug>.diff"` | สร้างไฟล์ `.diff` (`-U1`) เทียบกับ Backup ล่าสุด (ทำงานได้แม้ไม่มี `.git`) |
| `python .agents/scripts/workflow_ops.py log-turn --title "<t>" --summary "<s>"` | บันทึกประวัติสนทนาประจำวัน อัปเดต `README.md` และหมุนเวียน Rolling 15 Checkpoints |
| `python .agents/scripts/workflow_ops.py handoff --objective "<obj>"` | สร้าง Handoff Packet สำหรับหน้าต่างแชตใหม่ (`.agents/ck/HANDOFF.md` + `artifacts/handoffs/`), ตั้งค่า `HANDOFF_READY` ให้ `SessionStart` และสร้าง Starter Prompt |
| `python .agents/scripts/verify_workflow.py` | ตรวจความสมบูรณ์ของ `AGENTS.md`, 4 Agents, 4 Skills, `hooks.json`, สคริปต์, `run_workflow`, เทมเพลต, ลิงก์ และ BOM (ต้องได้ `Exit 0`) |
| `python .agents/scripts/verify_workflow.py --root "<path>"` | ตรวจเวิร์กโฟลว์ของโปรเจกต์อื่นโดยระบุพาธปลายทาง |
| `python -m unittest discover -s .agents/scripts -p "test_*.py" -v` | รันชุดทดสอบอัตโนมัติของสคริปต์และฮุคทั้งหมดในโฟลเดอร์ชั่วคราวแยกอิสระ |
| `python .agents/scripts/workflow_hooks.py <session-start\|pre-tool\|post-tool\|stop>` | ตัวประมวลผลฮุคที่ `.agents/hooks.json` เรียกใช้อัตโนมัติ (รับ camelCase JSON ผ่าน stdin) |

### E. คำสั่งเฉพาะโปรเจกต์ที่ต้องเติมใน `AGENTS.md`

| Placeholder | สิ่งที่ต้องเติม |
|---|---|
| `{{INSTALL_COMMAND}}` | คำสั่งติดตั้งแพ็กเกจ (เช่น `pip install -r requirements.txt`, `npm ci`) |
| `{{RUN_COMMAND}}` | คำสั่งรันแอปหรือเซิร์ฟเวอร์ในเครื่อง (เช่น `npm run dev`, `python main.py`) |
| `{{BUILD_COMMAND}}` | คำสั่งคอมไพล์หรือบิลด์ (เช่น `npm run build` หรือ `N/A` หากไม่มีขั้นบิลด์) |
| `{{TEST_COMMAND}}` | คำสั่งรันชุดทดสอบหลักของโปรเจกต์ (เช่น `python -m unittest discover -s tests`, `npm test`) |
| `{{LINT_COMMAND}}` | คำสั่งรัน Linter หรือ Typecheck (เช่น `ruff check .`, `npm run lint`) |

---

## 4. ตัวอย่างลำดับการทำงานจริงตั้งแต่ต้นจนจบ

1. **เปิดแชตใหม่ (เลือกภาษาครั้งแรก & ฟื้นฟูบริบท):** หากเปิดใช้ครั้งแรกก่อนตั้งค่า `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` ฮุค `SessionStart` จะให้ `@lead` เปิดเมนูคลิกเลือกภาษา (`ask_question`) และบันทึกด้วย `workflow_ops.py set-language` จากนั้นในรอบถัดไป `SessionStart` จะแทรกสรุปงานล่าสุด/Handoff พร้อมเตือน Bug ค้าง `3–7` วัน และ `@lead` อ่าน 3 บรรทัดบนของ `artifacts/Conversations/README.md` ($O(1)$ Rehydration)
2. **สั่งงาน:** ผู้ใช้พิมพ์ `/vibe <งาน>` (หรือถามคำถามทั่วไปซึ่ง `@lead` จะตอบสั้น `3–5` ข้อในโหมด `no-code / no-detail`)
3. **วางแผนและขออนุมัติ:** `@lead` (ร่วมกับ `@researcher` หากต้องสำรวจหลายไฟล์) ตรวจโค้ดจริง, เช็ก Conflict/Redundancy, ร่างพิมพ์เขียว (`U1, U2...`), เทียบ Pros/Cons เฉพาะทางเลือกที่ต่างกัน แล้วรอ `/approve`
4. **สำรองและลงมือทำ:** หลังได้ `/approve` ฝ่าย `@builder` รัน `workflow_ops.py backup` แล้วแก้ไฟล์แบบ Minimal Diff `-U1` (ฮุค `PreToolUse` บังคับเช็ก Backup และฮุค `PostToolUse` ตรวจสุขอนามัยให้อัตโนมัติ) จากนั้นขัดเกลาด้วย `/simplify`
5. **ทดสอบและตรวจ Diff:** `@verifier` รันเทสต์จริง (`{{TEST_COMMAND}}`) และตรวจ Static Diff แบบ Read-Only หากพบบั๊กภายใน Scope เดิม `@lead` สั่ง `Post-Approval Auto-Fix` ได้ทันที (หยุดเมื่อถึง Circuit Breaker $N \ge 3$)
6. **ปิดงานและบันทึก:** `@lead` ตรวจ Acceptance Criteria ทีละข้อ, สร้าง `.diff`, ประเมิน `/compound`, รัน `workflow_ops.py log-turn`, และรายงานผล `3` ส่วน *(สิ่งที่เกิดขึ้น, สิ่งที่แก้ไข, สิ่งที่ต้องทำต่อ)* พร้อมลิงก์ไฟล์จริง

---

## 5. คู่มือเริ่มต้นสำหรับโปรเจกต์ใหม่: ต้องมีอะไร • ต้องเตรียมอะไร • ต้องทำอะไร

### 5.1 สิ่งที่โปรเจกต์ใหม่ "ต้องมี" (Prerequisites)

| สิ่งที่ต้องมี | ความจำเป็น | รายละเอียด |
|---|---|---|
| **1. แอป Antigravity** | **จำเป็น** | Antigravity 2.0, Antigravity IDE หรือ CLI (`agy`) ที่รองรับการโหลด `AGENTS.md` และ `.agents/` |
| **2. Python 3.10+** | **จำเป็น** | Python 3.10 ขึ้นไปที่เรียกผ่านเทอร์มินัลได้ (`python` บน Windows; `python3` บน Linux/macOS) **ไม่ต้องลงไลบรารีเสริมใดๆ** |
| **3. โครงสร้างโฟลเดอร์ชัดเจน** | **จำเป็น** | โฟลเดอร์ Root ของโปรเจกต์ที่แยกซอร์สโค้ด (`{{SRC_DIR}}`) และชุดทดสอบ (`{{TEST_DIR}}`) ออกจาก `.agents/`, `artifacts/`, และ `backup/` |
| **4. คำสั่งรันเทสต์ / Linter** | **แนะนำอย่างยิ่ง** | คำสั่งรันเทสต์หรือ Linter จริงอย่างน้อย 1 คำสั่ง เพื่อให้ `@verifier` ตรวจผลเชิงประจักษ์ได้ |
| **5. Git + `.gitignore`** | **มีจะดีมาก (ไม่บังคับ)** | แนะนำเพื่อใช้ `git status` / `git diff -U1` แต่ถ้าไม่มี Git ระบบ `workflow_ops.py backup` + `diff` ก็ทำงานแทนได้; ควรเพิ่ม `backup/` และ `.agents/ck/last_alert.log` ลง `.gitignore` |

### 5.2 สิ่งที่โปรเจกต์ใหม่ "ต้องเตรียม" (Checklist ครบทั้ง `33` Placeholders)

เตรียมข้อมูลทั้ง 6 หมวดด้านล่างให้พร้อม ทุกรายการผูกตรงกับ **`{{PLACEHOLDERS}}` ทั้ง `33` ตัว** ที่คำสั่ง `workflow_ops.py check-placeholders` ตรวจสอบได้จริง:

#### หมวด 1 — ตัวตนโปรเจกต์และนโยบายภาษา (`3` ตัว)
| Placeholder | สิ่งที่ต้องเตรียม | ตัวอย่าง | ไฟล์หลักที่ใช้ |
|---|---|---|---|
| `{{PROJECT_NAME}}` | ชื่อโปรเจกต์ | `Acme Billing API` | `AGENTS.md`, `rules.md`, `lead.md`, `verifier.md`, `project-tasks`, `context.json`, templates |
| `{{PROJECT_OBJECTIVE}}` | เป้าหมายหลักของโปรเจกต์ 1–2 ประโยค | `Build a fault-tolerant invoice API with strict idempotency` | `AGENTS.md`, `project-tasks`, `project_fanout.py` |
| `{{CHAT_AND_ARTIFACTS_LANGUAGE}}` | ภาษาที่ใช้คุยและบันทึกใน `artifacts/` (ไฟล์ระบบคง English เพื่อประหยัด Token) | `Thai` หรือ `English` | `AGENTS.md`, `lead.md`, `workflow-ops`, `artifacts/README.md` |

#### หมวด 2 — เทคโนโลยี พาธหลัก และจุดเสี่ยงสูง (`6` ตัว)
| Placeholder | สิ่งที่ต้องเตรียม | ตัวอย่าง | ไฟล์หลักที่ใช้ |
|---|---|---|---|
| `{{TECH_STACK}}` | ภาษา เฟรมเวิร์ก ฐานข้อมูล และรันไทม์ | `Python 3.12, FastAPI, PostgreSQL, React 19` | `AGENTS.md`, `project-tasks` |
| `{{SRC_DIR}}` | โฟลเดอร์ซอร์สโค้ดหลัก *(เมื่อเติมใน `workflow_hooks.py` ฮุคบังคับ Backup จะเริ่มคุ้มครองซอร์สโค้ดทันที)* | `src/` | `AGENTS.md`, `project-tasks`, `workflow_hooks.py` |
| `{{TEST_DIR}}` | โฟลเดอร์ชุดทดสอบอัตโนมัติ | `tests/` | `AGENTS.md`, `project-tasks` |
| `{{PROTECTED_PATHS}}` | พาธที่ต้องสำรองและผ่าน `/approve` ก่อนแก้ | `src/, config/, AGENTS.md, .agents/` | `AGENTS.md`, `rules.md` |
| `{{HIGH_BLAST_RADIUS_MODULES}}` | ไฟล์แกนกลางที่แก้แล้วกระทบทั้งระบบ | `src/config.py, src/auth/jwt.py, src/db/schema.sql` | `rules.md`, `project-tasks` |
| `{{NAMING_CONVENTIONS}}` | มาตรฐานการตั้งชื่อไฟล์ คลาส และตัวแปร | `Python snake_case/PascalCase; TS camelCase/PascalCase` | `AGENTS.md` |

#### หมวด 3 — คำสั่งรัน บิลด์ เทสต์ และลินต์ (`5` ตัว)
| Placeholder | สิ่งที่ต้องเตรียม | ตัวอย่าง | ไฟล์หลักที่ใช้ |
|---|---|---|---|
| `{{INSTALL_COMMAND}}` | คำสั่งติดตั้ง Dependencies | `pip install -r requirements.txt` หรือ `npm ci` | `AGENTS.md`, `project-tasks` |
| `{{RUN_COMMAND}}` | คำสั่งรันโปรเจกต์ในเครื่อง | `uvicorn src.main:app --reload` หรือ `npm run dev` | `AGENTS.md`, `project-tasks` |
| `{{BUILD_COMMAND}}` | คำสั่ง Build (ใส่ `N/A` หากไม่มี) | `npm run build` หรือ `N/A` | `AGENTS.md`, `builder.md`, `project-tasks` |
| `{{TEST_COMMAND}}` | คำสั่งรันชุดทดสอบหลัก | `python -m unittest discover -s tests` หรือ `npm test` | `AGENTS.md`, `verifier.md`, `project-tasks`, `verify-and-debug` |
| `{{LINT_COMMAND}}` | คำสั่งรัน Linter / Typecheck | `ruff check .` หรือ `npm run lint` | `AGENTS.md`, `builder.md`, `verifier.md`, `project-tasks`, `verify-and-debug` |

#### หมวด 4 — งานหลักและเกณฑ์ตรวจรับ (`9` ตัว)
| กลุ่ม Placeholder | สิ่งที่ต้องเตรียม | ตัวอย่าง | ไฟล์หลักที่ใช้ |
|---|---|---|---|
| `{{TASK_1_NAME}}`, `{{TASK_1_OBJECTIVE}}`, `{{TASK_1_ACCEPTANCE}}` | งานหลักลำดับที่ 1, เป้าหมาย และเกณฑ์ตรวจผ่าน | `Auth API` / `Add JWT login` / `All 12 auth tests pass + 401 on invalid token` | `AGENTS.md`, `project-tasks` |
| `{{TASK_2_NAME}}`, `{{TASK_2_OBJECTIVE}}`, `{{TASK_2_ACCEPTANCE}}` | งานหลักลำดับที่ 2, เป้าหมาย และเกณฑ์ตรวจผ่าน | `Billing Webhook` / `Idempotent retries` / `Duplicate webhook IDs never double-charge` | `AGENTS.md`, `project-tasks` |
| `{{TASK_3_NAME}}`, `{{TASK_3_OBJECTIVE}}`, `{{TASK_3_ACCEPTANCE}}` | งานหลักลำดับที่ 3, เป้าหมาย และเกณฑ์ตรวจผ่าน (เพิ่มหัวข้อต่อได้อิสระ) | `Observability` / `Structured JSON logs` / `Zero unhandled exceptions in smoke run` | `AGENTS.md`, `project-tasks` |

#### หมวด 5 — ข้อห้ามเฉพาะโดเมนและด่านดักคำสั่ง (`3` ตัว)
| Placeholder | สิ่งที่ต้องเตรียม | ตัวอย่าง | ไฟล์หลักที่ใช้ |
|---|---|---|---|
| `{{DOMAIN_CONSTRAINTS}}` | ข้อห้ามเชิงเทคนิคหรือธุรกิจของโปรเจกต์ | `Never call live payment gateways in tests; no blocking I/O on async event loop` | `AGENTS.md`, `rules.md`, `project-tasks` |
| `{{NEVER_CUT_LIST}}` | เกราะความปลอดภัยที่ห้ามตัดทอนเด็ดขาด | `Input validation, Auth middleware, DB transaction guards, Existing tests` | `AGENTS.md`, `rules.md`, `verifier.md`, `project-tasks`, `verify-and-debug` |
| `{{FORBIDDEN_COMMAND_REGEX}}` | Regex คำสั่งต้องห้ามให้ฮุคบล็อกก่อนรัน (ใส่ `""` หากไม่ต้องการ; ถ้ายังไม่เติมระบบจะข้ามให้อัตโนมัติ) | `\brm\s+-rf\s+/` หรือ `\bpytest\s+core_pkg\b` | `.agents/scripts/workflow_hooks.py` |

#### หมวด 6 — เทมเพลตความสามารถเสริม (กรอกเมื่อต้องการเปิดใช้งาน — `7` ตัว)
| Placeholder | สิ่งที่ต้องเตรียม | ตัวอย่าง | ไฟล์หลักที่ใช้ |
|---|---|---|---|
| `{{WORKFLOW_TARGET_GLOB}}` | รูปแบบพาธไฟล์เริ่มต้นสำหรับ `run_workflow` | `src/**/*.py` | `.agents/workflows/project_fanout.py` |
| `{{MCP_SERVER_NAME}}`, `{{MCP_STDIO_COMMAND}}`, `{{MCP_HTTP_URL}}` | ชื่อเซิร์ฟเวอร์ MCP และคำสั่ง Stdio หรือ URL แบบ Streamable HTTP (`/mcp`) | `db-tools`, `sqlite-mcp-server`, `https://mcp.example.com/mcp` | `.agents/templates/mcp_config.example.json` |
| `{{IANA_TIMEZONE}}`, `{{SCHEDULE_CRON}}`, `{{SCHEDULE_TASK_PROMPT}}` | โซนเวลา IANA (ห้ามใช้ `+07:00`), ตาราง Cron 5 ช่อง และคำสั่งที่จบในตัว | `Asia/Bangkok`, `0 9 * * 1-5`, `Run test suite and summarize failures` | `.agents/templates/sidecar.schedule.example.json` |

### 5.3 สิ่งที่โปรเจกต์ใหม่ "ต้องทำ" ทีละขั้น (Step-by-Step Setup)

1. **คัดลอกไฟล์ไปวางที่ Root ของโปรเจกต์ใหม่:** คัดลอก `AGENTS.md`, `MANUAL_TH.md` (และ/หรือ `MANUAL_EN.md`), `.agents/`, และ `artifacts/` ไปวางที่ Root ของโปรเจกต์เป้าหมาย *(ห้ามวางซ้อนใต้ Workspace อื่นที่มี `AGENTS.md` อยู่แล้ว เพราะ Antigravity จะโหลดกฎเดินขึ้นสู่ Root ซ้อนกัน)* พร้อมเพิ่ม `backup/` และ `.agents/ck/last_alert.log` ลง `.gitignore`
2. **ตรวจคำสั่ง Python บนเครื่อง:** รัน `python --version` (ต้อง `3.10+`) หากใช้ Linux/macOS ที่มีเฉพาะ `python3` ให้แก้ `python` ใน [.agents/hooks.json](./.agents/hooks.json) เป็น `python3` โดย **คง** `scripts/workflow_hooks.py` ไว้เทียบกับ CWD `.agents/` เสมอ
3. **เลือกภาษาและเติม Placeholders ที่เหลือให้ครบ:**
   ```bash
   python .agents/scripts/workflow_ops.py set-language --lang "Thai"   # หรือคลิกเลือกจากเมนูตอนเปิดแชตครั้งแรก
   python .agents/scripts/workflow_ops.py check-placeholders
   ```
   เติมข้อมูลลง [AGENTS.md](./AGENTS.md), `.agents/rules/*.md`, [.agents/skills/project-tasks/SKILL.md](./.agents/skills/project-tasks/SKILL.md), เอเจนต์/สกิลที่อ้างคำสั่ง, [.agents/scripts/workflow_hooks.py](./.agents/scripts/workflow_hooks.py), [.agents/ck/context.json](./.agents/ck/context.json), และ [artifacts/README.md](./artifacts/README.md) ส่วนไฟล์ใน `.agents/templates/` ให้คัดลอกไปตั้งค่าเมื่อใช้งานจริง (หรือลบทิ้งหากยังไม่ใช้เพื่อให้ `check-placeholders --fail-on-found` คืน `Exit 0`)
4. **รันตัวตรวจและชุดทดสอบก่อนเริ่มใช้งานจริง (ต้องได้ `Exit 0` ครบ):**
   ```bash
   python .agents/scripts/workflow_ops.py check-placeholders --fail-on-found
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. **ปรับแต่งฮุคเสริม (ทางเลือก):** หากต้องการบล็อกไม่ให้ปิดรอบงานขณะที่ยังมี Alert ค้างใน `.agents/ck/last_alert.log` ให้เปลี่ยน `"enabled": false` เป็น `true` ที่ `"alert-stop-gate"` ใน [.agents/hooks.json](./.agents/hooks.json)
6. **ทดสอบรอบแรกใน Antigravity (Smoke Test):**
   - เปิดแชตใหม่ใน Workspace โปรเจกต์ ยืนยันว่า `SessionStart` ทำงานเรียบร้อยไร้ Error
   - ลองถามหลักการทั่วไปเพื่อยืนยันโหมดตอบสั้น `no-code / no-detail` ในภาษาที่ตั้งไว้
   - ทดสอบวงจร `/vibe` → `/approve` → `/finalize` กับงานเล็ก 1 ชิ้น ยืนยันว่าได้ Backup Manifest, ผลเทสต์จริง, ไฟล์ `.diff`, และบันทึกใน `artifacts/Conversations/` + `.agents/ck/context.json`
7. **แนวทางขยายระบบเมื่อโปรเจกต์เติบโต (Scaling Path):** เริ่มต้นด้วยทีมเล็ก 4 บทบาทเพื่อประหยัด Token และค่อยขยายเพิ่มเฉพาะเมื่อเกิดคอขวดจริง:
   - เพิ่ม **`@architect`** (`pro`) เมื่องานออกแบบครอบคลุมหลายบริการหรือหลายสคีมา
   - แยก **`@verifier`** เป็น **`@tester`** (รันเทสต์จริง) + **`@reviewer`** (ตรวจ Static Diff) + **`@code-skeptic`** (ผู้ตรวจหลักฐานก่อนปิดงาน) เมื่อปริมาณการเปลี่ยนแปลงสูงขึ้น
   - เพิ่ม **`@risk-guardian`** (`pro`, Read-Only Veto) สำหรับระบบการเงิน ความปลอดภัย หรือข้อมูลอ่อนไหว
   - หลังเพิ่มไฟล์ `.agents/agents/<name>.md` ครบ 10 องค์ประกอบและอัปเดตตาราง/จำนวนเอเจนต์ใน `AGENTS.md` ให้รัน `python .agents/scripts/verify_workflow.py` จนผ่าน `Exit 0` ทุกครั้ง
