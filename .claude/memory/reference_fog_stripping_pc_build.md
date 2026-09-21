---
name: reference_fog_stripping_pc_build
description: PC 打包后战斗场景雾（RenderSettings.fog）不显示的根因与修复：GraphicsSettings 雾剥离 Automatic 扫描不到运行时开启的雾 → FOG_LINEAR 变体被剥离，改为 Custom 全保留
metadata:
  type: reference
---

# PC 打包后雾消失 = shader 雾变体被剥离（2026-08-20 修复）

## 症状

编辑器里森林白天（FightScene id=10001）有雾，**PC 打包后无雾**。夜晚场景的体积雾（第三方 URP Volumetric Fog）不受影响，问题只出在内置距离雾。

## 根因链

1. 战斗场景的雾全部**运行时由代码开启**（`WorldHandler.LoadFightScene` 读 `FightSceneBean.fog` 配置 → `VolumeHandler.SetFog` → `RenderSettings.fog = true`），场景文件自身 Lighting 设置里 fog 全是关的。
2. 所有场景 shader 的雾靠 `#pragma multi_compile_fog`（FOG_LINEAR/EXP/EXP2 变体）实现。
3. `ProjectSettings/GraphicsSettings.asset` 的 `m_FogStripping: 0`（**Automatic**）：打包时 Unity 只扫描 **Build Settings 列表里场景**的雾设置来决定保留哪些雾变体。本项目 Build Settings 里只有 TestScene.unity 且 `m_Fog: 0`（战斗场景是 Addressables 加载的预制体/场景，不参与该扫描）→ **FOG_LINEAR 变体在打包时全部剥离**。
4. 编辑器下从不做变体剥离 → 编辑器正常、包体无雾。

## 修复（已落盘）

`GraphicsSettings.asset`：`m_FogStripping: 1`（Custom），`m_FogKeepLinear/m_FogKeepExp/m_FogKeepExp2` 保持 1 → 三种雾模式变体始终保留（体积稍增，可忽略）。改完必须**重新打包**才生效（shader 变体在打包编译期确定；若 shader 在 Addressables 组里需重建内容）。

通过 Unity MCP `execute_code` 用 SerializedObject 改的（`.asset` 被 block-unity-assets.ps1 拦截，不能直接 Edit）；注意 `ApplyModifiedPropertiesWithoutUndo` 后同会话内 LoadAllAssetsAtPath 回读可能拿到旧缓存值，**以磁盘 YAML 为准**。

## 排查套路

「编辑器有、包体没有」的渲染类问题，先怀疑 shader 变体剥离：GraphicsSettings 的 Fog/Lightmap/Instancing stripping、URP Global Settings 的 StripUnusedVariants。

关联：[[reference_shadergraph_fog_bypass]]（个别材质主动 bypass 雾是另一回事——那是"不想吃雾"，本条是"想吃雾但变体没了"）。
