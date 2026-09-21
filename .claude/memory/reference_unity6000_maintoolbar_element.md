---
name: reference_unity6000_maintoolbar_element
description: Unity 6000.3 主工具栏新增的 MainToolbarElement 默认 displayed=False 不显示，需在 ⋮(Kebab) 菜单启用或用 Overlay.displayed 反射置 true
metadata:
  type: reference
---

# Unity 6000.3 主工具栏新元素默认隐藏的坑

Unity 6000.3+ 的主工具栏是 **Overlay 体系**（`UnityEditor.MainToolbarWindow` + `MainToolbarOverlay`），与旧版 `UnityEditor.Toolbar` 的 `ToolbarZoneLeftAlign/RightAlign`（ToolbarExtension.cs 走的旧路径）是两套树——**旧路径的树在新版本里恒为空**，排查自定义元素是否注册要去 `MainToolbarWindow.instance.overlayCanvas.overlays`。

**坑**：新注册的 `[MainToolbarElement]`（如新增「自定义标题/xxx」按钮），在**已有布局持久化数据**的编辑器上 `displayed=False`，即默认不显示、也不进右侧 ⋮(Kebab) 溢出菜单的可见项——代码、注册、编译全部正常，就是看不见。

**解决办法（两选一）**：
1. 用户手动：主工具栏进入自定义/编辑模式（或右侧 ⋮ 菜单），勾选/启用新元素。
2. 代码一次性修复（已验证可行，2026-09-05 用于「处理 Excel 快捷操作」下拉）：

```csharp
// 经 Unity MCP execute_code 执行（C#6 语法，全反射）：
// MainToolbarWindow.instance → overlayCanvas → overlays →
// 找 id 匹配的 MainToolbarOverlay → overlay.displayed = true（setter 可写，立即生效并随布局持久化）
```

**排查套路**（本案例全流程，可复用）：
1. `TypeCache`/反射确认方法带 `MainToolbarElementAttribute`（注册无问题）；
2. `Resources.FindObjectsOfTypeAll("UnityEditor.Toolbar")` 的旧树看不到元素是**正常现象**，不代表没注册；
3. 反射 `MainToolbarWindow.instance.overlayCanvas.overlays` 枚举 `id/displayed` 才是真状态。

相关：ExcelEditorWindow 的「处理 Excel」「快捷」下拉（`CreateQuickActionDropdown`）、OpenEditor、BaseUICreateWindow 的主工具栏按钮都受此机制管理。API 签名（6000.3.11f1 实测）：`MainToolbarDropdown(MainToolbarContent, Action<Rect>)`，点击回调用 `GenericMenu.DropDown(rect)` 定位菜单；`MainToolbarContent(string, Texture2D, string tooltip)`。
