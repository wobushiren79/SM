---
name: reference_unity_mcp_execute_code_encoding
description: Unity MCP execute_code 传中文路径/字符串乱码成 ???？的根因与 invoke-unity-mcp.ps1 助手用法；ExcelEditorWindow 静默吞异常的"假成功"陷阱
metadata:
  type: reference
---

# Unity MCP execute_code 中文乱码 + Excel 导出假成功

## 坑 1：execute_code 中文路径乱码（ERROR_INVALID_NAME / excel_xxx[????].xlsx）

链路根因有两个叠加，均已修复（2026-08）：

1. **PowerShell 5.1 `-File` 传参会剥离内嵌双引号** → JSON body 到脚本就坏了。`invoke-unity-mcp.ps1` 用 `-BodyBase64` 传参规避（base64 只含安全字符）。
2. **PS 5.1 `Invoke-WebRequest -Body <string>` 默认按 ISO-8859-1 编码发送** → 中文全变 `?`。已修为 `[Text.Encoding]::UTF8.GetBytes($body)` 字节化发送。

**后果形态**：`execute_code` 里写 `GetFullPath("Assets/Data/Excel/excel_fight_scene[战斗场景].xlsx")` → Unity 收到 `[????]` → `FileStream` 抛 `ERROR_INVALID_NAME`。

## 坑 2：ExcelUtil.GetExcelPackage 静默吞异常 = "假成功"

`GetExcelPackage` 对文件打不开/路径错误只 `LogUtil.LogError("请先关闭对应的Excel文档")` 后 return，**不抛异常**。MCP `execute_code` 视角调用"成功"，但 `ExcelToJsonItem`/`CreateEntitiesItem` 实际什么都没做。排查 Excel 导出/生成"没生效"时先怀疑：路径乱码、文件被 WPS/Excel 占用（`~$` 锁文件）。

## invoke-unity-mcp.ps1 标准用法

```powershell
$json = '<json-rpc body>'  # 单引号字面量，进程内变量不经 -File 解析，双引号安全
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".claude/scripts/invoke-unity-mcp.ps1" -BodyBase64 $b64
# -Reinit 强制重握手；session 缓存于 $env:TEMP\unity_mcp_session_<port>.txt，失效自动重握手重试一次
```

## execute_code 跑编辑器工具链的正确顺序（含加列场景）

1. `CreateEntitiesItem` 生成 Bean → `AssetDatabase.Refresh()` 触发编译（域重载会断 MCP 会话，自动重连即可）
2. **编译完成后**再 `ExcelToJsonItem` 导 JSON —— 导出是"按程序集 Bean 反射序列化"（连 Partial 属性如 `HasVolumetricFog` 都会进 JSON），域重载前导出会用旧 Bean，新列字段缺失
3. 验证三样产物：Bean.cs 新字段、JSON 新 key、控制台无错

关联：[[reference_unity_mcp_tool_bug]]（工具集速查）、[[reference_unity_editor_self_run_delete_trick]]（MCP 不可用时的备选）
