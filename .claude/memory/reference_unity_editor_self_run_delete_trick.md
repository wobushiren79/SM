---
name: reference_unity_editor_self_run_delete_trick
description: 无人值守创建/改 Unity 资源的小技巧——临时编辑器脚本搭编译便车自动执行(DidReloadScripts)+干完自删(AssetDatabase.DeleteAsset)+幂等守卫
metadata:
  type: reference
---

当 Unity MCP 工具不可用(见 [[reference_unity_mcp_tool_bug]])、又要程序化创建/改 Unity 资源(.mat/.prefab/标记 Addressable 等)时，**优先用这个"自动跑+自删"的临时编辑器脚本套路**，无需手点菜单、无残留：

**三个机制拼起来**：
1. **`[UnityEditor.Callbacks.DidReloadScripts]` 静态方法 → 搭编译便车自动执行**：每次编译/域重载完成后自动被调用。改任意运行时 `.cs` 会触发编译(聚焦 Unity 即 Auto Refresh)，顺带就跑了。内部用 `EditorApplication.delayCall += DoWork` 把实际操作推迟到重载完全结算后，避免重载中途动资源。
2. **幂等守卫 → 只建一次**：`DidReloadScripts` 每次编译都触发，开头判断"目标资源已存在就 `return`"(如 `AssetDatabase.LoadAssetAtPath<T>(dstPath) != null`)。
3. **自删 → 干完删自己**：脚本是普通资源，`AssetDatabase.DeleteAsset("Assets/.../TempXxx.cs")` 可删任意资源含自身 `.cs`(连 `.meta`)。关键：放在工作做完之后；删除只触发下一次重载，重载后文件已不存在便不再触发。

**骨架**：
```csharp
public static class TempXxx {
    [UnityEditor.Callbacks.DidReloadScripts]
    static void AutoRun() => EditorApplication.delayCall += TryCreate;
    static void TryCreate() {
        if (AssetDatabase.LoadAssetAtPath<GameObject>(DstPath) != null) return; // 幂等
        try { Create(); } catch(System.Exception e){ Debug.LogError(e); }
    }
    static void Create() {
        /* CreateAsset / CopyAsset / PrefabUtility.LoadPrefabContents+SaveAsPrefabAsset /
           AddressableUtil.AddAssetEntry(group, path, address=path) ... */
        AssetDatabase.SaveAssets(); AssetDatabase.Refresh();
        AssetDatabase.DeleteAsset("Assets/FrameWork/Editor/TempXxx.cs"); // 自删
    }
}
```

**要点/坑**：临时脚本必须放 `Editor` 目录(编辑器程序集)；编辑器脚本可引用运行时类型(如 AddComponent 运行时组件)；验证用仍可用的 MCP `read_console`(脚本自删本身就反证编译成功——编译失败则域重载不完成、`DidReloadScripts` 不触发)。Addressable 标记复用项目自带 `AddressableUtil`。本仓实例：[[reference_spine_outline_vs_rim]] 的描边材质+预览预制就是这样建的。
