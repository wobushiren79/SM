---
name: reference_unity_search_index_crash
description: Unity 编辑器莫名崩溃排查路径：mdb_cursor_*/LMDB 堆栈 = Library/Search 索引损坏，关编辑器删该目录重建
metadata:
  type: reference
---

# Unity 编辑器崩溃：Search 索引（LMDB）损坏

**症状特征**：Unity.exe 崩溃，事件查看器报 `异常代码 0xc0000005、错误模块 Unity.dll`；崩溃日志（`%LOCALAPPDATA%\Temp\Unity\Editor\Crashes\Crash_*\Editor.log` 尾部）堆栈含 `mdb_cursor_*` / `mdb_page_search*` → `LMDBIndexStorage::RemoveDocuments/GetDocuments` → `SearchDatabase:MergeArtifacts` → `ProcessIncrementalUpdate`。崩溃前日志常见 `Reloading assemblies after forced synchronous recompile` + `SearchTask 'Update' thread did not stop within 5 seconds`。

**根因**：Unity 内置 Search/QuickSearch 资源索引库（`Library/Search/`，LMDB 格式）B-tree 损坏；改 C# 脚本触发程序集重载时，后台索引线程合并增量数据撞上坏页 → 访问违例拖崩整个编辑器。重启后会反复崩（待合并变更还在）。

**修复**（2026-09-06 已执行一次）：
1. 关闭所有 Unity 实例，并检查有无残留的孤儿 `AssetImportWorker` 进程（`Get-Process Unity`，崩过的父编辑器会留下无窗口僵尸 worker，须 `Stop-Process` 杀掉——2026-08-18 崩溃留了一个活 19 天的 PID 100328）；
2. 删除项目 `Library/Search` 整个文件夹（纯缓存，自动重建）；
3. 重开项目等索引重建。

**若重建后复发**：是 Unity 6000.3.11f1 自身 Search bug → 升级 6000.3 更新补丁，或 `Edit → Preferences → Search` 关闭自动索引（代价 Ctrl+K 全局搜索变慢）。

**排查路径速查**：事件查看器 `Application Error` 筛 Unity.exe 拿崩溃时间与异常码 → `%LOCALAPPDATA%\Temp\Unity\Editor\Crashes\Crash_*` 取崩溃会话的 Editor.log 尾部看堆栈 → `%LOCALAPPDATA%\Unity\Editor\UnityBugReporter.log` 看崩溃历史时间线。注意多实例/僵尸进程共踩 `%LOCALAPPDATA%\Unity\Editor\Editor.log` 会导致该日志时间戳不可信。
