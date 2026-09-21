---
name: reference_ui_gradient_atlas_uv
description: UI 渐变 shader 不能用 sprite 贴图 UV(图集 V1 always-enabled mode=4 会压缩+9宫格切段)，须用 UIGradientMeshUV 写归一化 UV1；FrameWork/UI/Shader_UI_ImageGradient 读 UV1
metadata:
  type: reference
---

UGUI Image 做"整图双色渐变"时**禁止用 sprite 贴图 UV(TEXCOORD0)** 当渐变坐标，否则运行时只看到两色混成一片、没有过渡。

**根因（本工程已确诊）**：
- `ProjectSettings/EditorSettings.asset` 的 `m_SpritePackerMode: 4`（Sprite Atlas V1 - Always Enabled）→ 图集在编辑器播放模式和打包后都会自动打包绑定。
- `Assets/LoadResources/Textures/UI/` 整个文件夹被 `AtlasForUI.spriteatlas`(isAtlasV2:0 的 V1) 打包。运行时 Image 网格 UV 被替换成 sprite 在 2048 大图里的一小块子矩形，`lerp(A,B,uv)` 只覆盖那一小段 → 渐变压缩成近单色。Scene 不播放时图集没绑，所以编辑器静态看着正常、"实际运行"才坏。
- 9-slice(Sliced) Image 还会把 UV 切成 9 段，UV 渐变本身就不连续。
- `FrameWork/UI/Shader_UI_ImageEffect` 的渐变(`ProjectUV(IN.uv,...)`)同样直接用 TEXCOORD0，对图集**不做**归一化，并未解决此问题（它看着正常是因为用在非图集整图上、或渐变是 Multiply 轻微叠色）。

**解决方案（本工程已落地）**：
- Shader `FrameWork/UI/Shader_UI_ImageGradient`（[Shader_UI_ImageGradient.shader](Assets/FrameWork/Shader/UI/Shader_UI_ImageGradient.shader)，内置 CG/UI 管线）：渐变坐标取自 **UV1(TEXCOORD1)**，UV0 仍采样贴图。属性 `_StartColor`/`_EndColor`(与 [[reference]] GameUIUtil.SetGradientColor 兼容)、`_DirectionMode`(横/纵/双对角/角度)、`_Angle`、`_GradientOffset`、`_GradientScale`、`_Smooth`。
- 组件 `UIGradientMeshUV : BaseMeshEffect`（[UIGradientMeshUV.cs](Assets/FrameWork/Scripts/Component/UI/UIGradientMeshUV.cs)）：`ModifyMesh` 按顶点包围盒把整矩形归一化成 0~1 写入 `vertex.uv1`，并在 `OnEnable` 给**根 Canvas** `additionalShaderChannels |= TexCoord1`（不开这通道 UGUI 会剔除 UV1，渐变退化单色）。这样图集子矩形 / 9宫格都不影响渐变铺满。

**使用**：渐变 Image 须①材质用该 shader ②挂 `UIGradientMeshUV` 组件。卡片详情(UIViewCreatureCardDetails)的 ui_CardBgBoard/ui_CardSceneBg/ui_CardRate 即此用法，`SetRarity` 通过 GameUIUtil.SetGradientColor 设 `_StartColor`/`_EndColor`。

旧的 `Shader_UI_ImageGradient_1.shadergraph`"效果不好"是同一病根（依赖 sprite UV），已被 `_2`→重命名为 `Shader_UI_ImageGradient` 的手写版取代。
