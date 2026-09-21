---
name: feedback-task-summary
description: 任务结束总结必须列出参与的 Agent 和 Skill
metadata:
  type: feedback
---

任务总结中若有 Agent 或 Skill 参与，必须在结尾列出每个 Agent/Skill 的名称及其具体操作。

**Why:** CLAUDE.md 明确规定此为强制输出项，用户发现我在任务完成后只输出了修改内容，遗漏了 Agent/Skill 清单。

**How to apply:** 每次任务结束时，检查本次是否调用了 Agent 或 Skill。若有，在总结末尾添加列表，格式为：
- **Agent**：名称 + 执行的具体操作
- **Skill**：名称 + 执行的具体操作
