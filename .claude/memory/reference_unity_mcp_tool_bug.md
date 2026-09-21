---
name: reference_unity_mcp_tool_bug
description: Unity MCP -32602 全滅 bug 已修复且工具正常；2026-09-11 Unity 包升 10.2.0（custom-tools 35 个，较 10.0.0 新增 generate_audio 付费音频生成）；仍无 Shader Graph 节点编辑
metadata:
  type: reference
---

本机 Unity MCP（`http://127.0.0.1:8080/mcp`，HTTP transport，`--project-scoped-tools`）。**版本双轨**：Unity 编辑器包 `com.coplaydev.unity-mcp`（git `#main`）已升到 **10.2.0**，Python 端 `mcp-for-unity-server`（uvx/PyPI）版本独立演进（10.0.0 时握手报 v3.4.2，以运行时握手返回为准）——工具集实际由 Unity 包动态注册（见 `mcpforunity://custom-tools`），故升包即换工具集。

## 现状（2026-09-11 复核，Unity 包 10.2.0）

- **`-32602 Invalid request parameters` 全滅 bug 早已修复**：`tools/call` 正常构建校验器并执行。实测 `manage_asset(action=search)` 返回 `success:true`；参数缺失返回正常 pydantic 校验错误（如 `path Missing required argument`）而非 -32602。
- **10.0.0 → 10.2.0 与协作相关的变化**：
  - 10.1.0：**新增 `generate_audio`**（AI 音频生成，asset_gen 组，requires_polling 上限 600s），同 `generate_image`/`generate_model` 一样属付费生成，调用前须先征得用户同意。
  - 10.1.2：`run_tests` 支持 `clear_stuck` 参数清除卡死测试 job；`manage_gameobject(action=create)` 可直接设组件属性。
  - 10.0.2：**多实例不再静默串台**——多个 Editor 连同一 server 时模糊路由会直接报错（#1023），仍需 `set_active_instance` 或每次调用携带 `unity_instance` 显式路由；`read_console` 保留多行消息体。
  - 10.2.0：`execute_code` 跳过 mcs 幻影 BOM 报错、CodeDom 程序集引用去重；`read_console` severity 修复；`manage_build` 构建前自动保存资源与场景、跳过从未保存的场景（不再弹保存框）。
- **`mcpforunity://custom-tools` 35 个（10.0.0 时 34 个，+`generate_audio`）；`tools/list` 总数以运行时为准**。工具组成（10.0.0 大扩后）：
  - **脚本编辑**：`manage_script`/`create_script`/`delete_script`/`validate_script`/`apply_text_edits`/`script_apply_edits`/`manage_script_capabilities`/`get_sha`（MCP 现可读写 `.cs`；但项目规则本就允许直接 Write/Edit `.cs`，用不用随意）。
  - **AI 生成**：`generate_image`/`generate_audio`/`generate_model`（含 `import_model`/`import_model_file`，均 `requires_polling` 上限 300s，`generate_audio` 600s）。属**付费/AI 生成类**，调用前须比照 PixelLab 规则先征得用户同意，别在别的任务里"顺带"生成（见 [[feedback_pixellab_require_consent]]）。
  - **新增 manage_* 面**：`manage_components`/`manage_camera`/`manage_animation`/`manage_ui`/`manage_physics`/`manage_probuilder`/`manage_profiler`/`manage_packages`/`manage_build`；工具类 `find_gameobjects`/`find_in_file`/`batch_execute`/`execute_code`/`unity_reflect`/`unity_docs`/`get_test_job`/`debug_request_context`。
  - **仍在**：`manage_asset`/`manage_material`/`manage_prefabs`/`manage_scene`/`manage_gameobject`/`manage_shader`/`manage_graphics`/`manage_vfx`/`manage_texture`/`manage_scriptable_object`/`execute_menu_item`/`refresh_unity`/`read_console`/`run_tests`/`manage_editor`/`set_active_instance`。
- 握手/`tools/list`/`resources/read`(`mcpforunity://instances`、`mcpforunity://custom-tools`) 正常。服务端提示：先读 `mcpforunity://custom-tools` 看动态工具；多实例须 `set_active_instance`。**踩坑**：`Mcp-Session-Id` 响应头必须原样回传每个后续请求，否则报 `-32600 Session not found`（分多条 PowerShell 命令时 session 变量易丢，建议单条脚本内一气呵成握手+调用）。

## manage_material / manage_asset 改材质颜色的坑（2026-08-09 实测）

- **`manage_material(action=set_material_color)` 会把"任一分量>1"的颜色当 Color32 字节处理，整体除以 255（连 alpha 也除）**：给 HDR 颜色（如冰球核心 (2.5,4.5,6)）落盘变成 (0.0098,0.0176,0.0235, 0.0039)≈透明黑。HDR 材质颜色**不要用它**。参数名是 `material_path`/`property`/`color`（2026-09-13 实测）。
- **2026-09-13 补充：÷255 是纯浮点除法（不做字节取整），故"×255 补偿法"也可行**——把目标值×255 传入（如目标 (0.1,0.85,2.4) 传 (25.5,216.75,612)），落盘值精确（本次 Mat_AttackModeVisual_RangedIceBall_2 四色已验证）。但 execute_code 直写法仍是首选，×255 仅作备选。
- **`manage_asset(action=modify)` 对 .mat 的 shader 属性无效**：返回 "No applicable or modifiable properties found"。
- **可靠做法 = `execute_code` 跑 C#**：`AssetDatabase.LoadAssetAtPath<Material>(路径)` → `mat.SetColor("_Xxx", new Color(...))` → `EditorUtility.SetDirty(mat)` → `AssetDatabase.SaveAssets()`（不 Save 则只改在编辑器内存，.mat 不落盘）。
- 改完务必 Grep 磁盘 `.mat` 文件核对落盘值（如本次冰球材质 Mat_AttackModeVisual_RangedIceBall 火色→冰蓝）。

## Shader Graph 说明（重要）

- **Unity MCP 无 Shader Graph 节点编辑工具**。`manage_shader` 仅是**手写 `.shader`(ShaderLab/HLSL) 文本 CRUD**(create/read/update/delete)，不碰 `.shadergraph` 节点图。`manage_material`/`manage_graphics`/`manage_vfx` 也非节点图编辑。
- `.shadergraph` 节点图的构建/编辑仍走**另一套服务 unity-skills**(`localhost:8090` 的 `shadergraph_*`，Unity 包 com.besty.unity-skills 已升 2.8.3)，见 [[reference_unityskills_shadergraph_limits]]（2.8.3 复核：节点白名单、Vector2 赋值 bug 等限制未变；注意运行模式非 Bypass 时 remove_* 被禁）。

## 历史（升级前，已过时，保留备查）

升级前多数变更工具 `tools/call` 返回 `-32602`（即使参数合法/空参也报），仅 `read_console`/`execute_code` schema 简单可调；且 `execute_code` 因本机无 Roslyn、CodeDom 回退命令行过长而编译失败。故当时回退方案是**临时编辑器脚本 + `[DidReloadScripts]` 重载自动执行**（见 [[reference_unity_editor_self_run_delete_trick]]）。**现工具已修复，可优先直接用 MCP 工具，该回退仅在特殊场景备用。**
