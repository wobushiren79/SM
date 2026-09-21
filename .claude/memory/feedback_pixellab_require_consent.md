---
name: feedback-pixellab-require-consent
description: 调用 PixelLab 生成像素图前必须征得用户明确同意，禁止在其他任务中"顺带"自行生成图片
metadata:
  type: feedback
---

任何调用 PixelLab 生成类工具（`create_*`/`animate_*`）之前，必须征得用户**明确同意**：要么用户在当前请求中明确要求生成像素图，要么先询问"将用 PixelLab 生成 X（消耗 credits）"并获得同意。**禁止在配置表/代码等其他任务中"顺带"自行生成图片**。

**Why:** 2026-06-10 用户反馈：在"新增深渊馈赠配置"任务中，我发现新馈赠缺图标就自行用 PixelLab 生成了 2 个图标，用户指出"使用 PixelLab 生成图标需要征求我的允许，我可能不想使用 PixelLab"。PixelLab 是付费外部服务（消耗账号 credits），是否花费应由用户决定。

**How to apply:** 任务中发现缺图时：留空或用占位（`icon_unknow` fallback），在任务总结中告知用户缺图，把"是否用 PixelLab 生成"作为后续选项提出。委派给 Agent/Skill 执行 PixelLab 任务时，prompt 必须注明"用户已同意使用 PixelLab"，子代理未见该声明应拒绝生成。规则已固化到 CLAUDE.md「PixelLab 像素图生成规则→调用前必须征得用户同意」、`.claude/skills/pixellab-art/SKILL.md` 开头警示块、`.claude/agents/pixellab-art.md`「前提：用户授权」。相关：[[feedback-pixellab-auto-download]]、[[feedback-ask-before-architecture-change]]。
