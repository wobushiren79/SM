---
name: camera-system
description: ScreenMiner 的摄像机(Camera)系统开发指南。使用此SKILL当需要创建或修改摄像机控制、Cinemachine 虚拟相机切换、场景镜头、跟随目标、镜头混合动画(Blend)、FieldOfView、屏幕适配等，包括 CameraHandler/CameraManager(框架层+游戏层 partial)、CinemachineCamera、CinemachineBrain、CV_List 场景虚拟相机组、CinemachineCameraEnum、HideAllCM、SetMainCameraDefaultBlend、GetDistanceFollow 等。
watched_files:
  - Assets/FrameWork/Scripts/Component/Handler/CameraHandler.cs
  - Assets/FrameWork/Scripts/Component/Manager/CameraManager.cs
---

# 摄像机系统 (Camera System) 开发指南

## 核心概念

本项目摄像机基于 **Unity Cinemachine 3.x**（`Unity.Cinemachine` 命名空间，类型为 `CinemachineCamera` / `CinemachineBrain` / `CinemachineFollow`）。
逻辑通过 `BaseHandler<CameraHandler, CameraManager>` 配对模式组织，框架层与游戏层各有一个 `partial` 文件。

```
CameraHandler   - 摄像机逻辑处理器（对外 API，单例 CameraHandler.Instance）
CameraManager   - 摄像机资源管理器（持有 Camera / CinemachineCamera / CinemachineBrain 引用）
CinemachineBrain- 主摄像机上的大脑，负责在多个虚拟相机间混合切换
cm_Xxx          - 场景控制跟随虚拟相机（命名约定，如 cm_Fight/cm_Base）
CV_List         - 各场景预制体下的虚拟相机组（按用途命名的多个 CinemachineCamera）
```

### 分层文件速查表

| 文件 | 层 | 职责 |
| --- | --- | --- |
| [Assets/FrameWork/Scripts/Component/Handler/CameraHandler.cs](Assets/FrameWork/Scripts/Component/Handler/CameraHandler.cs) | 框架 | 通用逻辑：`ChangeAngleForCamera`、`GetDistanceFollow` |
| [Assets/FrameWork/Scripts/Component/Manager/CameraManager.cs](Assets/FrameWork/Scripts/Component/Manager/CameraManager.cs) | 框架 | `mainCamera` / `uiCamera` 懒加载属性 |
| `Assets/Scripts/Component/Handler/CameraHandler.cs` | 游戏 | 各场景镜头切换 API（partial，随业务建立） |
| `Assets/Scripts/Component/Manager/CameraManager.cs` | 游戏 | 场景相机引用与加载、`HideAllCM`、`SetMainCameraDefaultBlend`（partial，随业务建立） |

> 提示：`CameraHandler` / `CameraManager` 都是 `partial` 类，框架层与游戏层共同组成同一个类。修改时按职责选对应层的文件。

## 初始化流程

```csharp
// 游戏启动时调用，加载主摄像机预制体
CameraHandler.Instance.InitData();   // -> manager.LoadMainCamera()
```

`LoadMainCamera()` 通过 `LoadAddressablesUtil.LoadAssetSync<GameObject>(PathInfo.CameraDataPath)` 实例化摄像机预制体，并缓存 `MainCamera` 节点（同时取其上的 `CinemachineBrain`）与各 `cm_Xxx` 控制镜头节点。

## 关键约定与 API

### 1. 控制镜头切换

```csharp
// 切换到指定控制镜头（先 HideAllCM 再启用目标）
CameraHandler.Instance.SetCameraForControl(CinemachineCameraEnum.Fight);
```
- 镜头枚举 `CinemachineCameraEnum` 定义在游戏层枚举文件中，新增控制镜头先加枚举。
- 抢镜用 `Priority = int.MaxValue`，关闭用 0。

### 2. 初始化场景镜头

- 初始化镜头时先 `SetMainCameraDefaultBlend(0)` 关闭切换动画后再设置 `Follow`/`LookAt`，并把 `PreviousStateIsValid = false` 以避免上一镜头插值残留。

### 3. 场景内 CV_List 虚拟相机组

场景预制体下挂名为 `CV_List` 的节点，内含多个按用途命名的 `CinemachineCamera`（`CV_Xxx`）。
通过统一入口 `SetCameraForBaseScene(priority, isEnable, cvName, blendTime)` 切换；语义化封装约定：

```csharp
// 游戏层为每个 CV_Xxx 加一个语义方法转调统一入口
CameraHandler.Instance.SetXxxCamera(priority, isEnable);  // -> SetCameraForBaseScene(p, e, "CV_Xxx")
```

> 新增一个场景子镜头：在场景预制体的 `CV_List` 下放一个命名为 `CV_Xxx` 的 `CinemachineCamera`，再在游戏层 `CameraHandler` 对应 region 里加一个语义方法转调 `SetCameraForBaseScene(priority, isEnable, "CV_Xxx")` 即可。

### 4. 运行期聚焦/震动（同一 CV 改字段范式）

同一个已激活 CV 可以在**运行期改字段**做局部特写而不新建镜头：

- 仅查找 CV_List 下镜头、不改激活态/优先级：`GetBaseSceneCamera("CV_Xxx")`（通用查找）。
- 聚焦：缓存原状态（门控字段防重入）→ Follow/LookAt 切到目标 + RotationComposer.TargetOffset 清零 + DOTween 推近 CinemachineFollow.FollowOffset → 还原时读缓存。
- 震动：瞬时抬升 CV 自带 CinemachineBasicMultiChannelPerlin.AmplitudeGain 后 DOTween 回落（首次震动缓存原振幅）。

### 5. 混合动画 / 隐藏 / 工具

```csharp
// 隐藏所有受管虚拟相机
CameraHandler.Instance.manager.HideAllCM();

// 设置主相机默认混合（切换）动画：time=0 即瞬切
CameraHandler.Instance.manager.SetMainCameraDefaultBlend(0.5f);
CameraHandler.Instance.manager.SetMainCameraDefaultBlend(0.5f, CinemachineBlendDefinition.Styles.EaseInOut);

// 根据摄像机角度修正物体角度（当前实现：归零 eulerAngles）
CameraHandler.Instance.ChangeAngleForCamera(target);

// 获取虚拟相机跟随距离（读 CinemachineFollow.FollowOffset 的模长）
float dist = CameraHandler.Instance.GetDistanceFollow(cinemachineCamera);
```

### 6. 透明排序（按世界 Z 轴的自定义排序）

需要"前排显示在前"等视角无关排序时，可把主相机透明排序改为 CustomAxis（如 `Vector3.forward` 世界 Z 轴）：
- 启用某镜头时 `transparencySortMode = CustomAxis` + `transparencySortAxis = Vector3.forward`；
- `HideAllCM()` 内统一还原 `TransparencySortMode.Default`——所有镜头切换路径都先经 `HideAllCM`，切出即自动还原。

## 常见任务流程

### 切换镜头的标准范式
1. `manager.HideAllCM()`（或由统一入口内部遍历关闭其它 CV）。
2. `manager.SetMainCameraDefaultBlend(blendTime)` 设置过渡（瞬切用 0）。
3. 启用目标 `CinemachineCamera.gameObject.SetActive(true)`。
4. 设置 `Priority`（抢镜用 `int.MaxValue`，关闭用 0）。
5. 跟随类镜头设置 `Follow` / `LookAt`，并把 `PreviousStateIsValid = false`。

### 新增一种「场景控制镜头」
1. 在 `CinemachineCameraEnum` 增枚举值。
2. 摄像机预制体加一个 `CinemachineCamera` 子节点，在 `CameraManager.LoadMainCamera()` 缓存引用。
3. 在 `CameraManager.HideAllCM()` 补充隐藏。
4. 在 `CameraHandler.SetCameraForControl` 的 `switch` 增分支与对应 `SetCameraForControlXxx()`。

## 约束与注意事项

- **摄像机操作统一走 `CameraHandler`**，不要在业务代码里直接拿 `Camera.main` 或散落操作 `CinemachineCamera`。
- **Cinemachine 版本为 3.x**：用 `CinemachineCamera`（非旧版 `CinemachineVirtualCamera`）、`CinemachineFollow`（非 `CinemachineTransposer`）、`Lens.FieldOfView`、`cinemachineBrain.DefaultBlend`。
- **混合动画**：需要瞬切（初始化、传送跳转）时务必先 `SetMainCameraDefaultBlend(0)`，否则会有残留插值。
- **跟随重置**：切换跟随目标后设 `PreviousStateIsValid = false`，避免镜头从上一位置滑入。
- **场景虚拟相机依赖命名约定**：`CV_List` 容器 + `CV_Xxx` 子节点名必须与代码里的字符串一致，改名需同步代码。
- **代码规范**：所有方法/属性加 `/// <summary>` XML 注释，并用 `#region`/`#endregion` 按场景用途分类。
- **Bean 规则**：若涉及自动生成的 `*Bean.cs`，扩展写在对应 `*BeanPartial.cs`。
- **Unity 资源修改**（摄像机预制体、CV 节点）必须通过 Unity MCP，禁止直接编辑 `.prefab`。
