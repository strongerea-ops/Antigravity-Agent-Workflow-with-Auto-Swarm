# Durable Context Checkpoints (Rolling 15 Snapshots)

- **Architecture:** Rolling FIFO Ring Buffer (max 15 checkpoints)
- **Active Pointer:** `.agents/ck/context.json` (always reflects $t_0$)
- **History:** `.agents/ck/history/` (created automatically on the first `workflow_ops.py log-turn`)

---

## Recent Trajectory (Latest 15 Turns)

| Checkpoint | Time (UTC) | Active Objective | Files | Status |
|---|---|---|---|---|
| **$t_0$ (Current)** | `00:00:00.000000Z` | Initialize portable agent workflow and fill project placeholders | - | TEMPLATE_READY |
