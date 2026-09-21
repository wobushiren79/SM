---
name: system-spine
description: Spine动画系统开发：SpineHandler/SpineManager、动画播放控制、皮肤管理、Spine编辑器工具。
tools: Read, Write, Edit, Glob, Grep, Bash
watched_files:
  - Assets/FrameWork/Scripts/Component/Handler/SpineHandler.cs
  - Assets/FrameWork/Scripts/Component/Manager/SpineManager.cs
  - Assets/FrameWork/Editor/Base/Window/SpineWindow.cs
  - Assets/FrameWork/Editor/Base/Window/SpineWindowPreview.cs
  - Assets/FrameWork/Addons/Spine/
---

# Spine 动画系统 (Spine System) 开发代理

你负责 Spine 动画系统的开发。

## 职责范围

### Spine 管理
- **SpineHandler** - Spine 逻辑处理单例 [FrameWork/Scripts/Component/Handler/SpineHandler.cs](Assets/FrameWork/Scripts/Component/Handler/SpineHandler.cs)
- **SpineManager** - Spine 资源与动画管理 [FrameWork/Scripts/Component/Manager/SpineManager.cs](Assets/FrameWork/Scripts/Component/Manager/SpineManager.cs)

### Spine 数据
- **SpineSkinBean** - 皮肤数据
- **SpineAnimationStateBean / SpineAnimationStateBeanPartial** - 动画状态数据

### Spine 编辑器
- **SpineWindow** - Spine 工具窗口（皮肤提取页签）[FrameWork/Editor/Base/Window/SpineWindow.cs](Assets/FrameWork/Editor/Base/Window/SpineWindow.cs)
- **SpineWindowPreview** - 动画预览页签（partial）：绕过官方版本兼容检查的动画预览 + 皮肤分组自由搭配 [FrameWork/Editor/Base/Window/SpineWindowPreview.cs](Assets/FrameWork/Editor/Base/Window/SpineWindowPreview.cs)

### 动画播放
```csharp
// 播放循环动画
spineEntity.PlayAnim(SpineAnimationStateEnum.Idle, true);

// 播放单次动画
spineEntity.PlayAnim(SpineAnimationStateEnum.Attack, false);
```

### Spine 运行时
- [Assets/FrameWork/Addons/Spine/](Assets/FrameWork/Addons/Spine/)
- spine-unity 4.3（git 包），多线程由 `SkeletonUpdateSystem` 单例驱动（工人线程做顶点 deform，主线程做 Mesh 上传）
- **多线程性能配置**：`SpineHandler.Awake → ConfigureSkeletonUpdateSystem()` 全局应用一次——`UpdateChunksPerThread`/`LateUpdateChunksPerThread` 由官方默认 8 降为 2（骨架总量不大时切太碎反增调度/信号开销）、`GroupRenderersBySkeletonType`/`GroupAnimationBySkeletonType=true`（同种骨架连续处理提缓存命中）、`MainThreadUpdateCallbacks=false`（省"工人→主线程→再等工人"分段循环；前提是全项目无 Spine 动画事件订阅——**新增 `UpdateLocal`/`AnimationState` 事件订阅时若触碰 Unity API 须先改回 true**）
- 大量同屏 Spine 渲染器优化项：`UpdateWhenInvisible=Nothing`、关法线/切线/tintBlack/裁剪、`immutableTriangles`、`singleSubmesh`、`ThreadedAnimation`/`ThreadedMeshGeneration=Enable`

## 约束

- Spine 动画通过 SpineHandler 统一管理
- 动画状态使用 SpineAnimationStateEnum 枚举
- 皮肤切换通过 SpineSkinBean 数据驱动
- Spine 资源加载后需正确释放
