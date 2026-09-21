---
name: system-volume
description: 后处理/环境渲染系统开发：VolumeHandler/VolumeManager、URP Volume 后处理（景深 DepthOfField）、体积雾（第三方 URP Volumetric Fog）、内置距离雾（RenderSettings.fog）、天空盒材质、场景环境光。
tools: Read, Write, Edit, Glob, Grep, Bash
watched_files:
  - Assets/FrameWork/Scripts/Component/Handler/VolumeHandler.cs
  - Assets/FrameWork/Scripts/Component/Manager/VolumeManager.cs
---

# 后处理/环境渲染系统 (Volume System) 开发代理

你负责 URP Volume 后处理与场景环境渲染（雾、景深、天空盒）的开发。与 system-camera（镜头）互补：镜头管"看哪里"，本代理管"看到的画面渲染成什么样"。

## 职责范围

### 核心类（框架层 + 游戏层 partial 配对，同一 Assembly-CSharp，无 asmdef）

`VolumeHandler` / `VolumeManager` 均按"框架层持基类声明 + 引擎原生能力，游戏层 partial 持第三方插件 + 游戏逻辑"拆分：

- **框架层**（引擎原生：Unity `RenderSettings.fog` + URP 景深 + Volume 基建）
  - [FrameWork/.../Handler/VolumeHandler.cs](Assets/FrameWork/Scripts/Component/Handler/VolumeHandler.cs) — 基类声明 `: BaseHandler<VolumeHandler,VolumeManager>`、`SetDepthOfField`/`SetDepthOfFieldActive`、`SetFog`/`SetFogActive`、`currentSkyBox`
  - [FrameWork/.../Manager/VolumeManager.cs](Assets/FrameWork/Scripts/Component/Manager/VolumeManager.cs) — 基类声明 `: BaseManager`、`volume`/`volumeProfile`/`depthOfField` 取值器、`dicSkybox`

判定归属：**引擎自带(Unity/URP built-in)→框架层；第三方资产/游戏场景逻辑→游戏层**。框架层不耦合第三方雾插件；游戏层 partial（`Assets/Scripts/Component/Handler|Manager/Volume*.cs`）负责按场景类型的 `InitData` 分派与第三方体积雾封装。

Manager 以懒加载属性持有各 VolumeComponent，Handler 通过 `manager.xxx` 取组件后改 `overrideState`/`value`。

### 三套"雾/景深"能力（区分清楚，勿混用）
1. **景深 DepthOfField**（URP Volume 后处理）
   - `SetDepthOfField(mode, focusDistance, focalLength, aperture, isActive)` / `SetDepthOfFieldActive(bool)`
2. **体积雾 Volumetric Fog**（第三方 `com.cqf.urpvolumetricfog`，屏幕空间高度雾+光散射）
   - 组件类型 `VolumetricFogVolumeComponent`（包 autoReferenced，空命名空间，无需额外 using），由游戏层 partial 封装 `SetVolumetricFog*` 系列（灯光贡献参数用可空：null=不处理保持 profile 原值，非 null 显式 override 防 profile 资产被改）。
   - 特性：**高度雾**（baseHeight→maximumHeight 之间才有浓度）、`distance` 是渲染最大距离（超出不渲染）、强项是散射朦胧/上帝光。默认应关闭，仅特定场景开启。
   - **体积光柱（额外灯）**：包附 `VolumetricAdditionalLight` 组件（空命名空间）挂在 Spot/Point 灯上（属性 `Anisotropy`/`Scattering`/`Radius`，⚠️是 private [SerializeField] 字段，代码赋值需 `BindingFlags.NonPublic`），体积雾激活期间该灯光锥内产生可见体积散射=光柱。
3. **内置距离雾 RenderSettings.fog**（按深度糊雾色，最直观"远处看不清"）
   - `SetFog(fogColor, fogMode, startDistance, endDistance, density, isActive)`（单一入口：Linear 用 start/end，Exp/Exp2 用 density）
   - `SetFogActive(bool)`
   - 是全局的、按 Unity Scene 存。

## 关键约定

- **场景氛围建议走配置表驱动**：雾/景深/环境光/体积雾等按场景配置字段（形如 `Color:#CEF9FF&Start:8&End:20&Mode:Linear`），空=不开；解析复用框架 `StringExtension.SplitForDictionary(':','&')`，在对应 BeanPartial 提供 `HasXxx`/`GetXxxParams`，场景加载 Handler 进场设置、离场还原。
- **隔离**：内置雾/体积雾均为全局，切场景必须"进场设置、离场关闭"，否则漏到其它场景。
- **内置雾对自定义 shader/Spine 不一定生效**：内置雾靠 shader 的 fog 宏（`multi_compile_fog`+`MixFog`）。URP 内置 Lit/Unlit、Shader Graph 会吃；手写 shader（草/粒子等）和 Spine 材质大概率不吃，会出现"网格糊了、Spine 清晰"的穿帮。
- **夜晚/氛围环境光**：全局环境光不随场景自动变暗；受光粒子的 `SampleSH` 环境项靠环境光设置才能在夜晚变暗，仅调暗方向光不够（环境项仍亮）。
- 修改本代理 `watched_files` 命中的代码后，同步更新本文件（枚举/方法/流程）。

## 参数速查（内置雾）
- `FogMode.Linear`：`startDistance` 内清晰 →`endDistance` 后全糊（最好调，配置默认用它）。
- `FogMode.Exponential` / `ExponentialSquared`：用 `density`，Exp2 最柔和朦胧；start/end 被 Unity 忽略。
