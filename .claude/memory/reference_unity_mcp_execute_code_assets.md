---
name: reference_unity_mcp_execute_code_assets
description: 用 Unity MCP execute_code 建特效/资源的踩坑：CodeDom(C#6)只能反射调包类型、中文字面量会被编译器破坏(路径用通配符枚举)、Addressables 命名空间陷阱、特效走 Addressables 组 Effect 且地址=全路径、safety_checks 拦 DeleteAsset
metadata:
  type: reference
---

用 **Unity MCP（mcpforunity, HTTP 8080）的 `execute_code` 工具**在编辑器里跑 C# 直接建资源（预制/材质/贴图/粒子）时的关键约束，2026-07 建"魔物进阶完成专用特效 Effect_AscendComplete_1"实测：

## execute_code 本身
- 以「方法体」运行，`return <obj>` 回传；导入 `UnityEngine`/`UnityEditor`；`Debug.Log` 可被 `read_console` 读到。
- **编译器是 CodeDom（C# 6）**，本机没装 Roslyn(Microsoft.CodeAnalysis)——`compiler:"auto"` 回退 codedom。⇒ **不能用 C#7+ 语法**(元组/模式匹配/`out var`/本地函数等)；**包的编辑器程序集(如 Unity.Addressables.Editor)不被引用**，直接写其类型会 `does not exist / missing assembly reference` 编译失败。
- 绕过办法：**反射**。`foreach (asm in System.AppDomain.CurrentDomain.GetAssemblies()) asm.GetType("全名")` 按字符串取类型(运行时程序集都在)，再 `GetProperty/GetMethod/Invoke`。运行时类型(如 Assembly-CSharp 里的 `EffectBase`)也这样反射拿，避免编译期依赖。
- `safety_checks`(默认 true)**拦 `AssetDatabase.DeleteAsset`/`File.Delete`/`Process.Start`/死循环**等。**关掉 safety_checks 会被 Claude Code auto 分类器拒绝**(用户没点名授权)。⇒ 别用 DeleteAsset；幂等改用 **load-or-create**(`LoadAssetAtPath` 有则改+`EditorUtility.SetDirty`,无则 `CreateAsset`)；`SaveAsPrefabAsset` 本身会覆盖同路径预制。
- **⚠️ 代码里的中文字面量会被编译器破坏**（2026-07-29 实测，codedom 编译通道编码问题）：字符串字面量中的中文（如 Excel 文件名 `excel_buff_info[buff信息].xlsx`）到 Unity 侧已成乱码 → `FileInfo` 指向不存在文件，导出**静默空跑**（调用方无异常、只回显 `???`）。⇒ **路径一律别写中文字面量，改用 `Directory.GetFiles(dir, "excel_buff_info*.xlsx")` 通配符枚举**（模式串全 ASCII，中文部分交给通配符匹配）；注释里的中文无碍，返回字符串显示乱码只是回显问题、不影响执行结果。
- **校验新写的 .cs 是否编译通过**：反射 `Assembly-CSharp.GetType("类名")` 非 null 即已进程序集；查字段可见性用 `GetField("名", BindingFlags.NonPublic|Instance).IsFamily` 验 protected。 execute_code 用的是**上次成功编译**的程序集——新文件有错时不会报，必须主动校验。
- **⚠️ 无人值守(Unity 窗口非前台)时 execute_code 做任何 `AssetDatabase` 写操作会死锁 Unity 主线程**(2026-07 建成就卡脉冲动画/流光材质实测)：纯逻辑(`return 2+2`)秒回，但 `CreateAsset`/`SaveAssets` 会挂起——execute_code 占着主线程、资产导入管线又要主线程泵消息 → 死锁，并把后续所有 MCP 主线程命令(连 `editor/state` 读取)全堵死。解法：把 Unity 窗口真正切到前台(ALT 解锁 + `SetForegroundWindow`，**别用 `AttachThreadInput`(也死锁)**)，前台化后卡住的导入立即完成、队列排空。**结论：无人值守场景建资产别用 execute_code，优先「临时自跑编辑器脚本」套路(见 [[reference_unity_editor_self_run_delete_trick]])——编辑器脚本用真 Roslyn 编译，无 CodeDom/C#6 限制、`UnityEngine.UI` 等程序集都可用，还搭 Auto Refresh 便车自动跑。**

## Addressables 陷阱(反射时的正确命名空间)
- `AddressableAssetSettingsDefaultObject` 在 **`UnityEditor.AddressableAssets`**(不是 `.Settings`!)；`AddressableAssetSettings`/`AddressableAssetGroup` 在 `UnityEditor.AddressableAssets.Settings`。取错命名空间→反射找不到类型静默失败。
- 拿 settings：`AddressableAssetSettingsDefaultObject.Settings`(静态属性,`BindingFlags.Public|Static`)。注册条目：`settings.CreateOrMoveEntry(guid, group)`→`entry.address=path`→`EditorUtility.SetDirty((Object)settings)`+`AssetDatabase.SaveAssets()`。

## 本项目特效加载约定(见 [[reference_unity_mcp_tool_bug]])
- `EffectManager` 用 `LoadAddressablesUtil.LoadAssetSync(key)`=`Addressables.LoadAssetAsync(key).WaitForCompletion()`,**key = 全资源路径**(`"Assets/LoadResources/Effects/{effectName}.prefab"`,pathEffect=`Assets/LoadResources/Effects`)。
- ⇒ **新特效预制必须注册成 Addressable,且 address=该全路径**,否则 `LoadAssetSync` 返回 null 加载不出。现有特效(如 Effect_Buff_Health_1,原 Effect_Buff_1 已删)都在 **组 `Effect`**、address=各自全路径——新特效放同组、同址约定即可(可反射 `FindAssetEntry(existingGuid).parentGroup` 拿到该组)。
- 特效预制结构:根挂 `EffectBase`(`mainPS`+`listPS`),`PlayEffect()` 调 `mainPS.Play()`(默认 withChildren=true,连带子 PS 播);`EffectBean{effectName,effectPosition,timeForShow,isDestoryPlayEnd,isPlayInShow}` 走 `ShowEffect(EffectBean, cbShow)`——`isPlayInShow=false` 时回调里改完 `listPS[i].main.startColor` 再 `PlayEffect()`,可做「运行时按稀有度上色」。

## PowerShell 调 MCP streamable-http 的坑
- 每个独立 shell 调用是新进程,**MCP session 不跨调用持久**⇒ 每次要重新握手(initialize→取 `Mcp-Session-Id`→`notifications/initialized`→tools/call),或把多步塞进同一段脚本。
- pwsh `Invoke-WebRequest` 的响应头是**数组**,session id 要 `[string]($r.Headers["Mcp-Session-Id"]|Select-Object -First 1).Trim()` 强转干净字符串,否则回传 `-32600 Session not found`。响应是 SSE:取 `data:` 行 JSON。域重载(改脚本触发)会让旧 session 失效,轮询编译就绪需每轮重建 session;编译是否干净以 `read_console`(types=[error]) 为准。
- `mcpforunity://instances` 的实例列表 JSON 是**转义嵌套**在 `contents[].text` 字符串里的(`\"id\": \"项目名@hash\"`),正则取实例 id 别按干净 JSON 写 `"id":"..."`,直接按形态匹配 `[A-Za-z0-9 _]+@[0-9a-f]{12,20}`(2026-07 踩过)。
- `refresh_unity` 工具可远程触发 AssetDatabase 刷新+编译,配合「临时自跑编辑器脚本」([[reference_unity_editor_self_run_delete_trick]])实现无人值守建资源;自跑脚本成功与否看产物文件(它干完会自删),比 read_console 轮询日志更可靠(日志可能被清/被 count 截断)。
- **⚠️Unity 窗口长期不聚焦时 `EditorApplication.delayCall` 会被饿死**(2026-07-31 实测)：临时脚本已编译进程序集(execute_code 反射查得到类型)、零报错,但 `DidReloadScripts` 里注册的 delayCall 迟迟不执行,execute_code 调用并不会顺带泵 editor update 队列。**解法**：轻量 IO(如 ExcelToJsonItem 写 JSON 的纯 File 写入)直接改用 execute_code + 反射调编辑器类(避开重 AssetDatabase 写防死锁、全 ASCII 防中文乱码);滞留的临时 .cs 由 bash 删文件 + `refresh_unity` 重编译,不依赖自删。
