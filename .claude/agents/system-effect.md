---
name: system-effect
description: 特效系统开发：EffectHandler/EffectManager、特效播放与管理、BaseEffectView。
tools: Read, Write, Edit, Glob, Grep, Bash
watched_files:
  - Assets/FrameWork/Scripts/Component/Handler/EffectHandler.cs
  - Assets/FrameWork/Scripts/Component/Manager/EffectManager.cs
  - Assets/FrameWork/Scripts/Component/Effect/EffectBase.cs
  - Assets/FrameWork/Scripts/Component/UI/BaseEffectView.cs
  - Assets/FrameWork/Scripts/Component/Effect/EffectShieldBubble.cs
  - Assets/FrameWork/Shader/URP/Shader_Mesh_ShieldBubble_1.shader
  - Assets/FrameWork/Shader/URP/Shader_Mesh_ShieldLink_1.shader
---

# 特效系统 (Effect System) 开发代理

你负责特效系统的开发。

## 职责范围

### 特效管理
- **EffectHandler** - 特效逻辑处理 [FrameWork/Scripts/Component/Handler/EffectHandler.cs](Assets/FrameWork/Scripts/Component/Handler/EffectHandler.cs)
- **EffectManager** - 特效资源管理 [FrameWork/Scripts/Component/Manager/EffectManager.cs](Assets/FrameWork/Scripts/Component/Manager/EffectManager.cs)
  - **加载/播放**：`GetEffect`(一次性)、`GetEffectForEnduring`(持久,按 res_name 取单例实例)——均实例化+入池+需预制挂 `EffectBase`。
  - **仅取模型**：`GetEffectModelSync(res_name)` 返回 Effects 目录下的模型预制(缓存 `dicEffectModel`)，**不实例化/不入池/不需要 EffectBase**——供需要自管常驻 `VisualEffect` 实例的粒子用。游戏层特效走 id→res_name(`EffectInfoCfg`)配置，res_name 缓存统一在 `manager.dicEffectResName` 字典。
  - **游戏层持久型粒子两大统一通道**（游戏层 partial 实现；新增同类粒子走现成通道，勿各写 `GetEffectForEnduring` 样板）：
    - `ShowEnduringEffect(effectId, configAction)` **通用底层**（VFX 属性型粒子）：按 id 查 `dicEffectResName` 缓存→`GetEffectForEnduring` 取实例→configAction 专属配置→统一 `PlayEffect`。
    - `ShowEnduringSingletonEffect(effectId, param, actionForGet=null)` **全局单例定位版**（PS 型粒子为主、亦支持 VFX 老特效）：**带 VFX 组件的单例粒子一律不设置实例坐标**——粒子位置由图自身逻辑/`{StartPosition}` 世界注入驱动、单例容器保持自身位置（Local 空间图叠加会成 2×偏移）；纯 PS 粒子无注入通道仍移动唯一实例到落点 + `param.direction` 非 None 时对实例 transform 做 X 镜像（Left=`localScale.x` 取负、Right/其他归正；单例复用故每次按方向显式设置而非取反切换）+ `InjectVfxConfigData` 注入 VFX 暴露属性（`{Direction}`/`{Size}`/`{StartPosition}` 占位）+ **有参数才设置**主粒子参数（哨兵默认值 0=不设置、保持 prefab 原值）+ `Stop(StopEmitting)` 保活 + `Play` 重播。
  - ⚠️ **PS 单例重播要点**：playing 状态直接 `Play()` 不会重新触发爆发，须先 `mainPS.Stop(true, StopEmitting)`(保活已发射粒子) 再 `Play()`——Stop(StopEmitting) 把系统置于 stopped 状态，随后 `Play()` 从 time 0 重启并重触发 burst、且不清理旧粒子（World 空间旧粒子驻留继续模拟），故多实例交叠成立；粒子必须**世界空间模拟**（prefab `moveWithTransform=1`，序列化值 0=Local/1=World），否则移动实例会拖走上一发残留粒子。⚠️**scalingMode 负缩放坑**：单例 X 镜像给根 transform 打 `localScale.x=-1`，若粒子 `scalingMode=Hierarchy(0)`，粒子尺寸乘上带符号层级 scale → 负尺寸四边形翻转/塌陷——**凡走单例镜像通道的 PS 粒子 `scalingMode` 必须=Local(1)**。⚠️软粒子坑：大面片粒子材质开**软粒子**(SoftParticles 深度带)会把贴地粒子实时淡出——症状"透明度每次不同、甚至为 0"，遇淡出先查播放高度与软粒子带。
  - **护罩穹顶罩体（框架层通用组件）**：手写 URP shader [Shader_Mesh_ShieldBubble_1.shader](Assets/FrameWork/Shader/URP/Shader_Mesh_ShieldBubble_1.shader)（`FrameWork/URP/ShieldBubble1`：菲涅尔窄边缘光+程序化 voronoi 裂纹按 `_CrackLevel` 分档碎裂+`_HitFlash` 受击闪白+`_Dissolve` 噪声阈值消融，零贴图）+ 框架层通用视图组件 [EffectShieldBubble.cs](Assets/FrameWork/Scripts/Component/Effect/EffectShieldBubble.cs)（不继承 EffectBase：MPB 灌参驱动，`UpdateView(deltaTime)` 由持有方逐帧调用，`OnEnable` 重置视觉支持池化；`SetLifetimePercent(p)`=存续期老化——前 4/5 保持完整，最后 1/5 渐进消融；`PlayBreak` 从当前溶解度 lerp 推满 1；`SetHealthPercent` 裂纹为可选 API）。⚠️非 EffectBase 组件**不能走 `GetEffect` 管线**（其强制 `GetComponent<EffectBase>()`），需由持有方自管实例与回池。
  - **护盾能量连线（EffectShieldBubble 子功能）**：泡泡预制内子节点 `Line`（LineRenderer：useWorldSpace、2端点、TextureMode=Stretch，材质配 shader [Shader_Mesh_ShieldLink_1.shader](Assets/FrameWork/Shader/URP/Shader_Mesh_ShieldLink_1.shader)，`FrameWork/URP/ShieldLink1`：加法发光、横向边缘衰减、能量脉冲沿 uv.x 从起点流向终点、`_FlowTime`/`_HitFlash`/`_Fade`，ZTest Always 纯表现层）。由 EffectShieldBubble 统一驱动（`enabledLink` 开关、`SetLinkEndpoints` 每帧跟随、`SetLinkWidth`、受击同闪、破碎先收线）。**出现动画（OnEnable 自动播放，池化取出即播）**：罩体弹性缩放 0→目标半径（EaseOutBack）+ 能量聚合（_Dissolve 1→0）、连线生长伸出 + 渐入。

### 特效基础类
- **EffectBase** - 特效基类 [FrameWork/Scripts/Component/Effect/EffectBase.cs](Assets/FrameWork/Scripts/Component/Effect/EffectBase.cs)
- **BaseEffectView** - 特效视图基类 [FrameWork/Scripts/Component/UI/BaseEffectView.cs](Assets/FrameWork/Scripts/Component/UI/BaseEffectView.cs)
- **UIParticleSystemOld** - UI 粒子系统旧版兼容

### 特效数据
- **EffectBean** - 特效资源数据

## 约束

- 特效通过 EffectHandler 统一创建和管理
- 特效资源使用 EffectBean 配置
- 战斗特效和 UI 特效分层管理
- 特效播放完后需回收或销毁；特效实例挂 DontDestroyOnLoad 的 EffectHandler 下、不走场景卸载销毁，切场景/对局结束须统一清理，漏清即跨场景残留播放
