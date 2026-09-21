---
name: feedback_play_verify_manual
description: 需要 Unity Play 模式验证的环节必须由用户手动 Play + 截图反馈，禁止 AI 通过 MCP 自动启动/停止 Play 自行验证
metadata:
  type: feedback
---

需要进入 Unity Play 模式（点击 ▶ 运行游戏）验证的环节，一律由用户**手动**完成：AI 不调用 MCP（`manage_editor` play/pause/stop、`batch_execute`、`execute_menu_item` 等）自动启动 Play 自行验证，而是完成任务后明确告知用户手动 Play、列出检查要点，用户截图（或描述现象、粘贴 Console 报错）发回，AI 根据截图判断并迭代。

**Why:** 用户反馈（2026-08-29）AI 自动启动 Play 的流程与真实操作不一致——时序、焦点、镜头、输入模拟等环节容易出问题，验证结果不可信；手动 Play 才能覆盖真实游戏流程。

**How to apply:** 任务总结或修复说明中如需验证运行效果，写出「请手动 Play 并截图 XX」+ 检查清单；等待用户反馈再判断，不要自己偷偷跑 MCP play 验证。非 Play 态的 MCP 编辑操作（改场景/资源、`run_tests` 编辑器测试）不受影响。项目规则见 CLAUDE.md「Play 模式验证规则」，与 [[reference_unity_mcp_tool_bug]] 配套（MCP 工具本身可用，只是 Play 验证不让它代跑）。
