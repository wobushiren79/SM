---
name: ui-components
description: UI通用组件开发：ScrollGrid、SelectView、CartogramBarView、ProgressView、DropdownView、RadioButton等框架层UI组件。
tools: Read, Write, Edit, Glob, Grep, Bash
watched_files:
  - Assets/FrameWork/Scripts/Component/UI/
---

# UI 通用组件 (UI Components) 开发代理

你负责框架层 [FrameWork/Scripts/Component/UI/](Assets/FrameWork/Scripts/Component/UI/) 中的通用 UI 组件开发；游戏层通用组件约定放在 `Assets/Scripts/Component/UI/Common/`。

## 职责范围

### 框架层 UI 组件
- **ScrollGrid** - 滚动网格（Horizontal/Vertical/Cell/BaseContent）。`SetCellCount` 重建时「保持位置」（offsetMin 按旧 offsetMax 换算滚动偏移不变），重建后主动补一次 `OnValueChange` 复用校正——否则 content 位置不变时 ScrollRect 不再派发 onValueChanged，新 cell 全停在顶部导致视野处列表空白；`AddCellListener` 应在 Awake 只注册一次，放 Refresh 里会随每次刷新重复累积
- **SelectView / SelectColorView** - 选择器 / 颜色选择器
- **CartogramBarView / CartogramBarForItem / CartogramBaseView** - 柱状图组件
- **ProgressView** - 进度条
- **DropdownView** - 下拉框
- **RadioButtonView / RadioGroupView** - 单选按钮 / 组
- **ButtonExtendView** - 扩展按钮
- **LongPressButton** - 长按按钮
- **LineView** - 连线组件
- **UITextLanguageView** - 多语言文本组件
- **DialogView** - 弹窗基类
- **PopupShowView / PopupShowCommonView** - 气泡基类（已内建出现/消失动画：开关字段 `isAnimForShow`/`isAnimForHide`/`isAnimWithFade` + virtual 方法 `AnimForShow()`/`AnimForHide(onComplete)`/`ShowWithAnim()`/`HideWithAnim()`，DOScale 弹出/缩回+可选淡出，全部 unscaled；子类可在 Awake 置开关=false 或 override 定制；UIHandler.ShowPopup/HidePopup 已收口走 ShowWithAnim/HideWithAnim）
- **PopupButtonView / PopupButtonCommonView** - 气泡按钮（PopupButtonCommonView 另支持右键：`AddListenerForRightClick(Action<PopupButtonCommonView>)` 订阅，其 `OnPointerClick` 仅转发右键——Button 只响应左键，且点击事件冒泡到 Button 所在物体即被吞掉，**右键必须与 Button 同物体接收**，挂根节点的 `IPointerClickHandler` 收不到）
- **ToastView** - 提示基类
- **MsgView** - 消息视图
- **AudioView / ButtonAudio** - 音频控制组件
- **CursorView** - 光标组件
- **UIHoverCardView** - 小丑牌(Balatro)风格通用悬停组件（继承 BaseUIView，实现 IPointerEnter/Exit/MoveHandler）：鼠标进入弹起放大(OutBack 回弹)+上抬，光标在卡面内移动时卡牌朝光标方向 3D 倾斜(视差跟随)，倾斜由欠阻尼弹簧驱动(半隐式积分写法，unscaledDeltaTime)故快速划过会甩动、松手回摆，悬停静止期间叠加双轴错相持续摆动，移出还原(OutQuad)。参数：`targetTransform`(空=自身)、`hoverScale`、`scaleDuration`、`hoverLiftOffset`(zero=不上抬)、`maxTiltAngle`(0=纯缩放)、`tiltFollowSpeed`、`tiltOvershoot`、`idleSwayAngle`、`idleSwayFrequency`、`isListenPointer`(关闭后仅外部驱动)。API：`PlayEnterAnim()`/`PlayExitAnim()`/`KillHoverAnim()`(OnDisable/OnDestroy 自动调)/`SetHoverSuppressed(bool)`/`RefreshOriginalTransform()`。事件沿射线接收层向上冒泡；若目标物体的位置/缩放由外部布局管理，应新建子节点挂本组件驱动子节点，与布局隔离。大列表性能设计：刻意不调基类Awake、`RegisterInputAction`/`UnRegisterInputAction`重写为空、父Canvas缓存
- **MaskUIView** - UI 遮罩
- **BaseEffectView** - 特效视图基类
- **SecretCode** - 秘钥输入

### 游戏层通用组件
- 游戏层通用组件放在 `Assets/Scripts/Component/UI/Common/`，命名同样用 `UIView` 前缀，按需在本文件补充清单。

## 约束

- 框架层组件放在 FrameWork/Scripts/Component/UI/
- 游戏层组件放在 Scripts/Component/UI/Common/
- 通用组件继承 BaseUIComponent，使用 `UIView` 前缀命名
- 组件功能保持单一职责，可复用
