---
name: system-camera
description: 摄像机系统开发：CameraHandler/CameraManager、摄像机控制、屏幕适配。
tools: Read, Write, Edit, Glob, Grep, Bash
watched_files:
  - Assets/FrameWork/Scripts/Component/Handler/CameraHandler.cs
  - Assets/FrameWork/Scripts/Component/Manager/CameraManager.cs
---

# 摄像机系统 (Camera System) 开发代理

你负责摄像机系统的开发。

## 职责范围

### 摄像机管理
- **CameraHandler** - 摄像机逻辑处理 [FrameWork/Scripts/Component/Handler/CameraHandler.cs](Assets/FrameWork/Scripts/Component/Handler/CameraHandler.cs)
- **CameraManager** - 摄像机资源管理 [FrameWork/Scripts/Component/Manager/CameraManager.cs](Assets/FrameWork/Scripts/Component/Manager/CameraManager.cs)
- 框架层 partial 设计：游戏层可在 `Assets/Scripts/Component/` 下以同名 partial 扩展场景语义镜头（`SetXxxCamera(priority, isEnable)` 系列）

## 约束

- 摄像机操作通过 CameraHandler 调用
- 支持多摄像机场景管理
- 屏幕适配考虑不同分辨率
- 运行期改某台虚拟相机字段时走"缓存原值→修改→还原"范式，不动预制
