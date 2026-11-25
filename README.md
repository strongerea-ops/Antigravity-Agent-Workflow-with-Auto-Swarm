# Antigravity Agent Workflow with Auto-Swarm

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/F6V72AZBUH)

> **Language / เลือกภาษา:** [English](#english) | [ภาษาไทย](#ภาษาไทย) | [Sponsor / สนับสนุนโปรเจกต์](#support-this-project)  
> **Complete Manuals / คู่มือฉบับสมบูรณ์:** [MANUAL_EN.md](./MANUAL_EN.md) (English) | [MANUAL_TH.md](./MANUAL_TH.md) (ภาษาไทย)

---

## English

### What Is This? (In Plain English)

Think of this kit as an **instruction manual, team structure, and safety net** for your AI assistant in **Antigravity**.  
Even if you are **not a programmer**, you can drop these files into any project folder so your AI assistant works in an organized, safe, and easy-to-follow way instead of making sudden, risky changes.

### What It Does for You

- **Pick Your Language on Day 1 (No Editing Needed):** The first time you open a chat, the assistant automatically shows a clickable menu to choose your preferred language (English, Thai, Japanese, Chinese, or any language). It keeps internal rules in English behind the scenes to save AI memory, while talking to you in plain, everyday words.
- **Click Instead of Typing Commands:** You get clickable menus (`ask_question`) when choosing your language, approving a plan (`/approve`), switching or compacting a long chat (`/handoff` vs. `/compact`), and choosing from recommended next commands.
- **Always Plans, Backs Up & Asks Before Editing:** Before touching important files, the assistant explains the plan in simple terms, checks for conflicts, asks for your click-to-approve, and automatically saves a **Backup copy** first so nothing is lost.
- **A Small, Organized 4-Role AI Team:**
  - `@lead` — **Project Manager:** listens to you, makes plans, asks for approval, and summarizes results.
  - `@builder` — **Maker:** makes the exact edits you approved after saving a backup.
  - `@verifier` — **Quality Checker (Read-Only):** runs real tests and checks the changes without editing your files.
  - `@researcher` — **Helper (Read-Only):** searches files and documentation quickly at low cost.
- **Smart Scaling & Memory Control:** Simple fixes happen in one step (`Tier 0`), normal tasks use one helper (`Tier 1`), and big multi-file tasks automatically split across a team (`Tier 2` Auto-Swarm) while protecting unsaved local changes. When a chat gets long (`10–12` turns), a clickable menu lets you move cleanly to a fresh window (`/handoff`) or compact the current one (`/compact`).
- **Works With or Without Git, Zero Extra Installs:** Built-in safety checks, backups, change summaries (`.diff`), and reminder checks for `3–7` day unresolved bugs run on standard Python `3.10+` with **zero extra libraries** to install.

### What Do You Want to Do? (Quick Cheat Sheet)

| What you want | Command to type (or click when offered) | What happens |
|---|---|---|
| Build or change something safely | `/vibe <describe your goal>` | Plans first → asks you to click Approve → backs up → builds → tests |
| See a plan only (do not edit files yet) | `/design <topic>` | Creates a clear blueprint and options without changing code |
| Ask for a simple, no-jargon answer | `/concept <question>` | Explains only the key ideas in `3–5` plain bullets (default for Q&A) |
| See full technical details | `/more-detail` | Shows exact files, line numbers, and full command outputs |
| Something broke — find the real cause | `/debug <problem>` | Investigates step-by-step instead of guessing |
| Chat is getting long — start a fresh window | `/handoff` *(clickable menu)* | Creates a handover note + ready-to-paste prompt for a brand-new chat |
| Chat is getting long — stay in this window | `/compact` *(type in chat)* | Compresses old messages in Antigravity so you can keep going here |

*(Note: Clicking a workflow command like `/handoff` or `/vibe` runs it immediately. Built-in Antigravity commands like `/compact` or `/plan` are typed directly into the chat box.)*

### 3-Minute Quick Start

> **Important Tip:** Antigravity reads `AGENTS.md` from your project's top folder. Copy the **contents** of this repository directly into your own project's main folder (avoid placing it inside another folder that already has an `AGENTS.md`).

1. **Download or clone this kit** and copy `AGENTS.md`, `.agents/`, `artifacts/`, and `MANUAL_EN.md` / `MANUAL_TH.md` into your project's main folder:
   ```bash
   git clone https://github.com/strongerea-ops/Antigravity-Agent-Workflow-with-Auto-Swarm.git
   ```
2. **Choose your chat language (First-Time Setup):** Open your project in Antigravity and click your language in the welcome menu — or set it with one command:
   ```bash
   python .agents/scripts/workflow_ops.py set-language --lang "English"   # or "Thai", "Japanese", etc.
   ```
3. **Fill in your project details (`33` guided blanks):** Run the command below to see every `{{PLACEHOLDER}}` blank and where it lives, then fill in your project name, folders, and commands:
   ```bash
   python .agents/scripts/workflow_ops.py check-placeholders
   ```
   *(On Mac/Linux where `python` is called `python3`, change `python` to `python3` inside [.agents/hooks.json](./.agents/hooks.json) while keeping `scripts/workflow_hooks.py` as-is.)*
4. **Run the built-in health check (both should finish with `0` errors):**
   ```bash
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. **Start chatting in Antigravity:** Open your project and type `/vibe <what you want to build>`. Step-by-step beginner explanations are in [MANUAL_EN.md](./MANUAL_EN.md) and [MANUAL_TH.md](./MANUAL_TH.md).

### Documentation Hub

| Document | Language | What's Inside |
|---|---|---|
| [MANUAL_EN.md](./MANUAL_EN.md) | **English** | Beginner-friendly complete guide: plain-English glossary, all features, every command, and step-by-step setup |
| [MANUAL_TH.md](./MANUAL_TH.md) | **Thai** | คู่มือฉบับภาษาไทยอ่านง่าย: คำศัพท์พื้นฐาน, ความสามารถทั้งหมด, คำสั่งทุกตัว, และวิธีเริ่มต้นทีละขั้น |
| [AGENTS.md](./AGENTS.md) | English | Master rulebook loaded automatically by Antigravity |
| [.agents/rules/rules.md](./.agents/rules/rules.md) | English | Task-based rule index (safety, tooling, approvals, onboarding) |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | English & Thai | How to contribute improvements and run verification before a Pull Request |

### Repository Structure

```text
Antigravity-Agent-Workflow-with-Auto-Swarm/
├── README.md                              # Plain-language overview & quick start (English & Thai)
├── MANUAL_EN.md                           # Complete beginner-friendly manual (English)
├── MANUAL_TH.md                           # Complete beginner-friendly manual (Thai)
├── AGENTS.md                              # Master rulebook loaded automatically (<= 24 KB)
├── CONTRIBUTING.md                        # Contribution guidelines (English & Thai)
├── LICENSE                                # GNU General Public License v3.0 (GPL-3.0)
├── .gitignore                             # Keeps local backups, scratch files & secrets out of Git
├── .github/
│   ├── FUNDING.yml                        # GitHub Sponsor button (Ko-fi)
│   ├── assets/                            # Sponsor QR codes (Ko-fi & PromptPay)
│   ├── workflows/ci.yml                   # Automated CI checks (Linux & Windows)
│   ├── ISSUE_TEMPLATE/                    # Bug report & feature request templates
│   └── PULL_REQUEST_TEMPLATE.md           # PR verification checklist
├── .agents/
│   ├── rules/                             # Task-based rules (4 focused files — read only what's needed)
│   │   ├── rules.md                       # Task index & dirty-tree swarm safety rule
│   │   ├── coding-and-safety.md           # Critical files, clean code notes, backup & rollback
│   │   ├── commands-and-tools.md          # Hook folder rules, reusable tools vs. disposable scratch
│   │   └── agents-and-handoff.md          # First-time language setup, clickable menus, /handoff, 3-7d bug reminders
│   ├── agents/                            # 4-role AI team (10-element schema)
│   │   ├── lead.md                        # Project manager: plans, clickable approvals, summaries
│   │   ├── builder.md                     # Maker: backs up and edits approved files cleanly
│   │   ├── verifier.md                    # Quality checker (Read-Only): runs tests & inspects changes
│   │   └── researcher.md                  # Explorer (Read-Only): searches code & web docs cheaply
│   ├── skills/                            # 4 on-demand playbooks (loaded only when needed)
│   │   ├── project-tasks/SKILL.md         # Your project's goals, tasks & pass criteria
│   │   ├── plan-and-build/SKILL.md        # /vibe, /design, /approve, /code, /simplify, /finalize
│   │   ├── verify-and-debug/SKILL.md      # /test, /debug, /audit, safety breaker, /compound
│   │   └── workflow-ops/SKILL.md          # Fast startup memory, 15 checkpoints, /compact, /handoff
│   ├── hooks.json                         # Automatic safety hooks (startup, pre-edit, post-edit, opt-in stop)
│   ├── scripts/                           # Zero-dependency Python 3.10+ helper scripts
│   │   ├── workflow_hooks.py              # Automatic startup language check, checkpoints, bug alerts & backup guard
│   │   ├── workflow_ops.py                # set-language, backup, diff, log-turn, handoff, check-placeholders
│   │   ├── verify_workflow.py             # Automated health checker for all workflow files
│   │   └── test_workflow_ops_and_hooks.py # Built-in self-test suite
│   ├── workflows/                         # Optional parallel multi-file analysis script (run_workflow)
│   ├── templates/                         # Optional MCP server & scheduled automation examples
│   └── ck/                                # Rolling 15 memory snapshots (context.json, CONTEXT.md, history/)
└── artifacts/                             # Organized records (Conversations, blueprints, diffs, reviews, comments, tools, scratch)
```

### Contributing

Improvements, ideas, and bug fixes are warmly welcome! Please check [CONTRIBUTING.md](./CONTRIBUTING.md) and confirm both checks pass before opening a Pull Request:

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

### ระบบนี้คืออะไร? (อธิบายแบบเข้าใจง่ายสำหรับทุกคน)

ลองนึกภาพชุดไฟล์นี้เป็น **“คู่มือการทำงาน + ทีมผู้ช่วย + ระบบกันพลาด”** สำหรับ AI ในแอป **Antigravity**  
แม้คุณจะ **ไม่เคยเขียนโปรแกรมมาก่อน** ก็นำชุดนี้ไปวางในโฟลเดอร์โปรเจกต์ได้ทันที เพื่อให้ AI ทำงานเป็นขั้นเป็นตอน อธิบายเข้าใจง่าย ขอความเห็นชอบก่อนแก้ และสำรองไฟล์ไว้ให้เสมอ ไม่แก้ไฟล์มั่วจนงานพัง

### สิ่งที่ระบบนี้ช่วยคุณได้ทันที

- **เลือกภาษาตั้งแต่เปิดใช้งานครั้งแรก (ไม่ต้องแก้ไฟล์เอง):** เมื่อเปิดแชตครั้งแรก AI จะเด้งเมนูคลิกให้เลือกภาษาที่อยากใช้คุยและบันทึกเอกสาร (เช่น ภาษาไทย, English, ญี่ปุ่น, จีน หรือภาษาอื่น) โดยคงกติกาเบื้องหลังเป็นอังกฤษเพื่อประหยัดความจำ AI แต่คุยกับคุณด้วยภาษาธรรมดาที่อ่านเข้าใจง่าย
- **คลิกเลือกได้ ไม่ต้องนั่งจำหรือพิมพ์คำสั่งเอง:** มีเมนูคลิกให้เลือก (`ask_question`) ครบทั้งตอนเลือกภาษาครั้งแรก, ตอนอนุมัติแผน (`/approve`), ตอนแชตยาวแล้วต้องเลือกระหว่าง `/handoff` กับ `/compact`, และตอนที่ AI แนะนำคำสั่งอื่นๆ ที่เหมาะกับงาน
- **วางแผนก่อน สำรองไฟล์ก่อน และขออนุมัติก่อนแก้ทุกครั้ง:** ก่อนแตะไฟล์สำคัญ AI จะอธิบายแผนแบบเข้าใจง่าย เช็กว่ามีจุดขัดแย้งหรือไม่ ให้คุณคลิกอนุมัติ และเซฟไฟล์สำรอง (`Backup`) อัตโนมัติเพื่อให้ย้อนกลับได้เสมอ
- **แบ่งทีม AI กะทัดรัด `4` ตำแหน่งชัดเจน:**
  - `@lead` — **หัวหน้างาน:** รับโจทย์ วางแผน เสนอเมนูให้อนุมัติ และสรุปผลการทำงาน
  - `@builder` — **ช่างลงมือทำ:** สำรองไฟล์และแก้ไขเฉพาะส่วนที่คุณอนุมัติแล้วเท่านั้น
  - `@verifier` — **ผู้ตรวจงาน (อ่านอย่างเดียว):** รันการทดสอบจริงและตรวจเช็กความเรียบร้อยโดยไม่แอบแก้ไฟล์เอง
  - `@researcher` — **ผู้ช่วยค้นหา (อ่านอย่างเดียว):** ช่วยค้นไฟล์และหาข้อมูลอย่างรวดเร็วและประหยัดโควตา
- **ปรับขนาดทีมและคุมความจำแชตอัตโนมัติ:** งานเล็กแก้จบในแชตเดียว (`Tier 0`), งานทั่วไปใช้ผู้ช่วยเดี่ยว (`Tier 1`), งานใหญ่หลายไฟล์ค่อยกระจายให้ทีมทำพร้อมกัน (`Tier 2` Auto-Swarm) โดยไม่ทำให้งานที่ยังไม่เซฟในเครื่องหาย และเมื่อคุยยาวถึง `10–12` รอบ ระบบจะเปิดเมนูคลิกให้เลือกย้ายไปหน้าต่างใหม่ (`/handoff`) หรือบีบอัดหน้าต่างเดิม (`/compact`)
- **ใช้ได้ทั้งแบบมี Git และไม่มี Git โดยไม่ต้องลงโปรแกรมเสริม:** ระบบสำรองไฟล์, สรุปจุดที่เปลี่ยน (`.diff`), ตัวตรวจความสมบูรณ์ และระบบเตือนบั๊กที่ค้างมา `3–7` วัน ทำงานด้วย Python `3.10+` มาตรฐาน ไม่ต้องติดตั้งไลบรารีเพิ่ม

### อยากทำอะไร → ใช้คำสั่งไหนดี? (ตารางลัดสำหรับมือใหม่)

| สิ่งที่คุณอยากทำ | คำสั่งที่ใช้ (พิมพ์ หรือคลิกจากเมนูเมื่อระบบเสนอ) | สิ่งที่ระบบจะทำให้ |
|---|---|---|
| สั่งสร้างหรือปรับแก้ฟีเจอร์อย่างปลอดภัย | `/vibe <บอกเป้าหมายที่ต้องการ>` | วางแผน → ให้คลิกอนุมัติ → สำรองไฟล์ → ลงมือแก้ → ทดสอบจริง |
| อยากเห็นแผนก่อน (ยังไม่ให้แก้ไฟล์) | `/design <หัวข้อ>` | ทำพิมพ์เขียวและเทียบทางเลือกให้ดูก่อน โดยยังไม่แตะไฟล์จริง |
| อยากให้อธิบายแบบสั้นๆ เข้าใจง่าย | `/concept <คำถาม>` | ตอบเฉพาะหลักการ `3–5` ข้อ ภาษาธรรมดา งดโค้ด (เป็นค่าเริ่มต้นของแชต) |
| อยากดูรายละเอียดเชิงลึกครบทุกไฟล์ | `/more-detail` | แสดงชื่อไฟล์ บรรทัด โค้ด และผลคำสั่งแบบละเอียด |
| เจอปัญหา/บั๊ก อยากหาต้นตอจริง | `/debug <อาการที่พบ>` | ไล่สืบหาสาเหตุจริงเป็นขั้นเป็นตอน แทนการเดาสุ่ม |
| แชตเริ่มยาว อยากย้ายไปหน้าต่างใหม่สะอาดๆ | `/handoff` *(คลิกเลือกจากเมนูได้)* | สร้างสรุปส่งมอบงาน + ข้อความพร้อมวางในหน้าต่างแชตใหม่ทันที |
| แชตเริ่มยาว แต่อยากทำต่อในหน้าต่างเดิม | `/compact` *(พิมพ์ในช่องแชต)* | สั่งให้แอป Antigravity บีบอัดประวัติเก่าในหน้าต่างนี้ |

*(หมายเหตุ: คำสั่งของเวิร์กโฟลว์ เช่น `/handoff` หรือ `/vibe` คลิกจากเมนูแล้ว AI รันต่อให้ทันที ส่วนคำสั่งหลักของแอป Antigravity เช่น `/compact` หรือ `/plan` ผู้ใช้พิมพ์ลงในช่องแชตโดยตรงครับ)*

### เริ่มต้นใช้งานใน 3 นาที (Quick Start)

> **ข้อควรจำ:** แอป Antigravity จะอ่านไฟล์ `AGENTS.md` จากโฟลเดอร์บนสุดของโปรเจกต์ ให้คัดลอก **ไฟล์ข้างใน** ชุดนี้ไปวางที่ **โฟลเดอร์หลักของโปรเจกต์คุณโดยตรง** (อย่าวางซ้อนใต้โปรเจกต์อื่นที่มี `AGENTS.md` อยู่แล้ว)

1. **ดาวน์โหลดหรือโคลนชุดนี้** แล้วคัดลอก `AGENTS.md`, `.agents/`, `artifacts/`, และ `MANUAL_TH.md` / `MANUAL_EN.md` ไปวางในโฟลเดอร์หลักของโปรเจกต์คุณ:
   ```bash
   git clone https://github.com/strongerea-ops/Antigravity-Agent-Workflow-with-Auto-Swarm.git
   ```
2. **เลือกภาษาสำหรับใช้งานครั้งแรก:** เปิดโปรเจกต์ใน Antigravity แล้วคลิกเลือกภาษาจากเมนูต้อนรับที่เด้งขึ้นมาอัตโนมัติ — หรือสั่งตั้งค่าทันทีผ่านคำสั่งเดียว:
   ```bash
   python .agents/scripts/workflow_ops.py set-language --lang "Thai"   # หรือ "English", "Japanese" ฯลฯ
   ```
3. **เติมข้อมูลโปรเจกต์ของคุณ (`33` ช่องที่มีคำแนะนำชัดเจน):** รันคำสั่งนี้เพื่อดูรายชื่อช่องว่าง `{{PLACEHOLDER}}` ที่ต้องเติม เช่น ชื่อโปรเจกต์ โฟลเดอร์งาน และคำสั่งรัน/เทสต์:
   ```bash
   python .agents/scripts/workflow_ops.py check-placeholders
   ```
   *(บน Mac/Linux ที่ต้องใช้คำสั่ง `python3` ให้แก้ `python` เป็น `python3` ใน [.agents/hooks.json](./.agents/hooks.json) โดยคง `scripts/workflow_hooks.py` ไว้เหมือนเดิม)*
4. **รันตัวตรวจสุขภาพระบบ (ควรผ่านด้วย `0` ข้อผิดพลาดทั้งคู่):**
   ```bash
   python .agents/scripts/verify_workflow.py
   python -m unittest discover -s .agents/scripts -p "test_*.py" -v
   ```
5. **เริ่มใช้งานใน Antigravity ได้เลย:** เปิดโปรเจกต์แล้วพิมพ์ `/vibe <สิ่งที่อยากสร้าง>` — อ่านคู่มือแบบจับมือทำทุกขั้นตอนพร้อมคำศัพท์พื้นฐานได้ที่ [MANUAL_TH.md](./MANUAL_TH.md)

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
