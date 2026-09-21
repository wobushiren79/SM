---
name: feedback_agent_skill_sync
description: 改了被 watched_files 命中的代码后必须同步对应 agent/skill 文档；附自动 Hook 机制与 PS 脚本 BOM 编码约束
metadata:
  type: feedback
---

修改代码后，若该文件被某个 `.claude/agents/*.md` 或 `.claude/skills/*/SKILL.md` 的 frontmatter `watched_files` 命中，**必须在同一次任务内同步更新对应文档**（枚举值、流程图、文件速查表、示例等）。只改代码不更文档 = 给后续协作者/AI 喂过时的错误信息。

**Why:** 用户明确指出此前我加了测试模式却没同步 test-system skill / game-launcher agent。深查发现：本该自动提醒的 `PostToolUse` Hook（`.claude/scripts/check-cs-changed.ps1` → `check-watched.ps1`）因 4 个 bug 从未生效过，所以我从没收到提示、只能靠记忆而漏掉。

**How to apply:**
- 收到 `systemMessage`"C# change hits watched_files of these Agents/Skills..."后，逐一核对并同步；确认无需改的也要在任务总结说明原因。
- 改 `.cs` 会自动触发 Hook；改被 watch 的 `.txt`/`.json`/`.asset` 等非 `.cs` 文件**不会**触发，需手动 `.claude/scripts/check-watched.ps1` 核对。
- **PS 脚本编码铁律**：`.claude/scripts/*.ps1` 含中文注释时**必须 UTF-8 with BOM**。Hook 由 Windows PowerShell 5.1(`powershell.exe`)执行，无 BOM 时按系统 ANSI(GBK)误读中文 → 双字节吞掉行边界 → 脚本逻辑静默串位失效（`IndexOf`/`-replace $1` 等莫名返回空）。
- check-watched 的两个历史坑（已修，复发时参考）：① frontmatter 正则需 `(?s)` 否则多行 frontmatter 提取失败；② git diff 返回【仓库根】相对路径(本项目在子目录 `Demon Lord Roguelike/`)，需 `git rev-parse --show-prefix` 剥前缀才能对齐项目相对的 watched_files；③ 目录前缀项靠末尾 `/` 区分，解析时别 `TrimEnd('/')`。

相关：[[feedback_task_summary]]、[[feedback_comment_sync]]。规则正文见 CLAUDE.md「Agent/Skill 文档同步规则」。
