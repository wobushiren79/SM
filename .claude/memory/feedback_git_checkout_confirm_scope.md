---
name: feedback_git_checkout_confirm_scope
description: 执行 git checkout/restore 等破坏性还原前必须逐个文件与用户确认范围——曾一次 blanket checkout 丢掉用户未提交的预制体修改
metadata:
  type: feedback
---

# git 破坏性还原必须先确认文件范围

2026-08-17 真实事故：用户只要求还原"AI 上次改的 fog 配置"，某会话却执行了
`git checkout -- Mesh_TerrainPlane_1.asset FightScene_Desert_1.prefab FightScene_Forest_1.prefab MatFightSceneRoad.mat Mat_Ground_2.mat ...`
一次性还原 6 个文件，把用户**手动摆放且从未提交**的森林场景雨天子场景（Details/DayRain、Details/NightLight 及其灯光、雨效实例、水洼面片、反射组件）全部丢弃。git 无法恢复未提交内容，最终靠翻 Claude Code 会话记录（`~/.claude/projects/<项目>/*.jsonl` 里的 Read/Grep/git-diff 结果）逐参数重建。

**Why:** 未 `git add`/`git commit` 的工作区修改被 checkout 后永久丢失；用户的一句"还原"通常只指某一个改动，不指整片工作区。

**How to apply:**
- 执行 `git checkout --` / `git restore` / `git clean` 前，先 `git status`+`git diff --stat` 列出待还原文件，逐个说明每个文件将被丢弃的内容，经用户明确确认后才执行；
- 用户说"还原"时先问清对象：是还原 AI 刚做的某次修改，还是还原用户自己的改动；能用定向手段（改回字段值）就不用整文件 checkout；
- 批量资源文件改动后建议用户及时 commit（哪怕 WIP 提交），这是唯一的可靠保险。
