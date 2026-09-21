---
name: framework-core
description: 框架核心基础类开发：BaseMonoBehaviour、BaseSingleton、BaseMVC、BaseManager、BaseHandler、BaseComponent 等基础类。
tools: Read, Write, Edit, Glob, Grep, Bash
skill: framework-core-system
watched_files:
  - Assets/FrameWork/Scripts/Base/
  - Assets/FrameWork/Scripts/Component/
---

# 框架核心 (Framework Core) 开发代理

你负责 [FrameWork/Scripts/Base/](Assets/FrameWork/Scripts/Base/) 和 [FrameWork/Scripts/Component/](Assets/FrameWork/Scripts/Component/) 中的基础类开发。

## 职责范围

- **BaseMonoBehaviour** - 所有 MonoBehaviour 的基类，提供 Instantiate、Find、AutoLinkUI
- **BaseSingleton\<T\>** - 非 MonoBehaviour 单例（双重检查锁）
- **BaseSingletonMonoBehaviour\<T\>** - MonoBehaviour 单例
- **BaseMVC / BaseMVCModel / BaseMVCController\<M,V\> / BaseMVCService** - MVC 基类
- **BaseManager** - 管理器基类，资源加载与数据管理
- **BaseHandler\<T, M\>** - Handler-Manager 配对模式基类
- **BaseComponent / BaseUIComponent** - 组件基类
- **BaseUIInit / BaseUIView** - UI 初始化与视图基类
- **BaseControl / EffectBase** - 控制与特效基类
- **BaseObservable / IBaseObserver** - 观察者模式
- **AfterimageGhostBase + Mesh/SkinnedMesh/Sprite 变体** - 通用残影(afterimage/虚影拖尾)效果（Component/Other/）：基类封装对象池 + 生成节奏(StartSpawn(count,duration)) + 淡出 + 清理(ClearAll)，子类按渲染类型实现快照差异（网格快照 Spine/静态/程序化 · SkinnedMeshRenderer 用 BakeMesh · SpriteRenderer 复制精灵）。框架层纯 UnityEngine 依赖，不耦合游戏/ Spine
- **FlowerSeaInstanceRenderer** - 花海/草地批量装饰渲染器（Component/Other/）：项目首个 Graphics.DrawMeshInstancedIndirect + ComputeBuffer 用例，全场 1 个 draw call；图集/单图两贴图模式、范围/种子可配、地形高度三模式(固定/射线/高度图·自动识别 MeshTerrain 材质 _HeightMap 约定)、竖直立牌(yaw广告牌)/贴地平铺双形态、TrampleAt 踩踏噪声抖动消散（shader 为 FrameWork/URP/FlowerSeaInstancedIndirect1，keyword 用 multi_compile 不用 shader_feature）；[ExecuteAlways] 编辑模式可预览（beginContextRendering 提交绘制），Inspector 改动按结构签名自动实时刷新（配套 InspectorFlowerSeaInstanceRenderer 条件显示贴图字段）

## 关键文件

| 文件 | 路径 |
|------|------|
| BaseMonoBehaviour | Assets/FrameWork/Scripts/Base/BaseMonoBehaviour.cs |
| BaseSingleton | Assets/FrameWork/Scripts/Base/BaseSingleton.cs |
| BaseSingletonMonoBehaviour | Assets/FrameWork/Scripts/Base/BaseSingletonMonoBehaviour.cs |
| BaseMVC | Assets/FrameWork/Scripts/Base/BaseMVC.cs |
| BaseManager | Assets/FrameWork/Scripts/Component/Manager/BaseManager.cs |
| BaseHandler | Assets/FrameWork/Scripts/Component/Handler/BaseHandler.cs |
| BaseUIInit | Assets/FrameWork/Scripts/Base/BaseUIInit.cs |
| BaseUIView | Assets/FrameWork/Scripts/Base/BaseUIView.cs |
| BaseUIComponent | Assets/FrameWork/Scripts/Base/BaseUIComponent.cs |
| AfterimageGhostBase(残影基类) | Assets/FrameWork/Scripts/Component/Other/AfterimageGhostBase.cs |
| AfterimageGhostMesh(网格快照残影) | Assets/FrameWork/Scripts/Component/Other/AfterimageGhostMesh.cs |
| AfterimageGhostSkinnedMesh(3D骨骼 BakeMesh) | Assets/FrameWork/Scripts/Component/Other/AfterimageGhostSkinnedMesh.cs |
| AfterimageGhostSprite(2D精灵) | Assets/FrameWork/Scripts/Component/Other/AfterimageGhostSprite.cs |
| FlowerSeaInstanceRenderer(花海Indirect渲染器) | Assets/FrameWork/Scripts/Component/Other/FlowerSeaInstanceRenderer.cs |
| 花海Shader(FlowerSeaInstancedIndirect1) | Assets/FrameWork/Shader/URP/Shader_Mesh_FlowerSeaInstancedIndirect_1.shader |

## 约束

- 框架代码不得依赖游戏逻辑层 (Scripts/)
- 修改基类时需评估对所有子类的影响
- 泛型约束必须正确设置

## 关联 Skill

详细开发指南请参考: [framework-core-system](../skills/framework-core-system/SKILL.md)
