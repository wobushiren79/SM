---
name: event-system
description: ScreenMiner 的事件系统开发指南。使用此SKILL当需要注册/触发事件、创建事件常量、理解事件驱动架构、调试事件通信等，包括EventHandler全局单例、BaseEvent实例事件、事件常量定义(EventsInfo)、事件参数类型等。
watched_files:
  - Assets/FrameWork/Scripts/BaseSystem/Event/EventHandler.cs
  - Assets/FrameWork/Scripts/BaseSystem/Event/EventEntity.cs
  - Assets/FrameWork/Scripts/Base/BaseEvent.cs
---

# 事件系统开发指南

## 核心概念

项目采用**双层事件架构**：全局事件（跨模块通信）+ 实例事件（组件内部通信）。

### 事件系统架构

```
EventHandler (全局单例)
    │  BaseSingleton<EventHandler>
    │  Dictionary<string, Delegate> eventDict
    │  支持 0-4 个泛型参数
    │  用于跨模块、跨系统通信
    │
    ├── RegisterEvent(string eventName, Action/Delegate)
    ├── UnRegisterEvent(string eventName, Action/Delegate)
    ├── TriggerEvent(string eventName, T data...)
    └── Dispose() 全局清理

BaseEvent (实例事件基类)
    │  继承后可注册/触发实例级事件
    │  用于组件内部通信
    │
    ├── RegisterEvent<T>(string eventName, Action<T>)
    ├── UnRegisterEvent(string eventName)
    ├── UnRegisterAllEvent()
    └── TriggerEvent<T>(string eventName, T data)

EventsInfo (事件常量)
    │  所有事件名称的字符串常量
    │  集中管理，避免硬编码字符串
```

---

## 事件常量定义 (EventsInfo)

事件常量类 `EventsInfo` 是**游戏层自建文件**（建议放在 `Assets/Scripts/Common/EventsInfo.cs`），集中管理所有事件名的字符串常量，避免硬编码字符串散落在业务代码里。

### 结构约定

```csharp
public static class EventsInfo
{
    // ========== 按模块分组 ==========
    // 命名规范：模块名_具体行为，常量值与常量名保持一致
    public const string MyModule_DataChange = "MyModule_DataChange";
    public const string MyModule_ItemSelect = "MyModule_ItemSelect";
}
```

### 添加新事件常量

命名规范：`模块名_具体行为`

```csharp
// Assets/Scripts/Common/EventsInfo.cs
public static class EventsInfo
{
    // 按照模块分组添加
    // 格式: [模块前缀]_[具体描述]

    // 示例：商城相关事件
    public const string Store_ItemBuy = "Store_ItemBuy";
    public const string Store_ItemSell = "Store_ItemSell";

    // 示例：成就相关事件
    public const string Achievement_Unlock = "Achievement_Unlock";
    public const string Achievement_Progress = "Achievement_Progress";
}
```

---

## 全局事件系统 (EventHandler)

### 注册事件

```csharp
// 无参数事件
EventHandler.Instance.RegisterEvent(EventsInfo.MyModule_DataChange, OnDataChange);

// 1个参数
EventHandler.Instance.RegisterEvent<SomeBean>(
    EventsInfo.MyModule_ItemSelect,
    OnItemSelect
);

// 2个参数
EventHandler.Instance.RegisterEvent<string, string>(
    EventsInfo.MyModule_SomeEvent2,
    OnSomeEvent2
);

// 3个参数
EventHandler.Instance.RegisterEvent<int, string, float>(
    EventsInfo.SomeEvent,
    OnSomeEvent
);

// 4个参数
EventHandler.Instance.RegisterEvent<int, string, float, bool>(
    EventsInfo.SomeEvent4,
    OnSomeEvent4
);
```

### 触发事件

```csharp
// 无参数
EventHandler.Instance.TriggerEvent(EventsInfo.MyModule_DataChange);

// 1个参数
EventHandler.Instance.TriggerEvent(
    EventsInfo.MyModule_ItemSelect,
    itemData
);

// 2个参数
EventHandler.Instance.TriggerEvent(
    EventsInfo.MyModule_SomeEvent2,
    arg1,
    arg2
);

// 3个参数
EventHandler.Instance.TriggerEvent(
    EventsInfo.SomeEvent,
    intValue,
    stringValue,
    floatValue
);

// 4个参数
EventHandler.Instance.TriggerEvent(
    EventsInfo.SomeEvent4,
    intValue,
    stringValue,
    floatValue,
    boolValue
);
```

### 注销事件

```csharp
// 注销指定事件
EventHandler.Instance.UnRegisterEvent(EventsInfo.MyModule_DataChange, OnDataChange);

// 注销1参数事件
EventHandler.Instance.UnRegisterEvent<SomeBean>(
    EventsInfo.MyModule_ItemSelect,
    OnItemSelect
);
```

### 回调方法签名

```csharp
// 无参数
private void OnDataChange() { }

// 1个参数
private void OnItemSelect(SomeBean itemData) { }

// 2个参数
private void OnSomeEvent2(string arg1, string arg2) { }

// 3个参数
private void OnSomeEvent(int a, string b, float c) { }

// 4个参数
private void OnSomeEvent4(int a, string b, float c, bool d) { }
```

---

## 实例事件系统 (BaseEvent)

### 在类中使用（继承 BaseEvent）

```csharp
public class MyComponent : BaseEvent
{
    private void OnEnable()
    {
        // 注册实例事件
        RegisterEvent(EventsInfo.MyModule_DataChange, OnDataChange);
        RegisterEvent<SomeBean>(EventsInfo.MyModule_ItemSelect, OnItemSelect);
    }

    private void OnDisable()
    {
        // 注销所有实例事件（防止内存泄漏）
        UnRegisterAllEvent();
    }

    private void OnDataChange()
    {
        // 处理数据变化
    }

    private void OnItemSelect(SomeBean data)
    {
        // 处理选择
    }

    // 触发实例事件（通知子组件）
    private void NotifyDataChanged()
    {
        TriggerEvent("DataChanged");
    }
}
```

### 继承 BaseEvent 的基类

以下基类已继承 BaseEvent，可直接使用实例事件：

| 基类 | 说明 |
|------|------|
| `BaseUIInit` | UI 初始化基类 |
| `BaseUIComponent` | UI 组件基类 |
| `BaseGameLogic` | 游戏逻辑基类 |
| `AIBaseEntity` | AI 实体基类 |

---

## 事件驱动通信模式

### 模块间解耦通信

```
                  EventHandler 全局事件总线
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   UIHandler       GameHandler     AudioHandler
   (刷新UI)        (处理逻辑)      (播放音效)
        │               │               │
        └───────────────┼───────────────┘
                        │
              TriggerEvent(EventsInfo.XXX)
```

### 典型用例

一个业务动作完成后，由产生方触发全局事件，各关心方（UI 刷新、逻辑处理、音效播放等）各自监听，互不直接引用：

```csharp
// 产生方：数据变更后广播
EventHandler.Instance.TriggerEvent(EventsInfo.MyModule_DataChange, changedId);

// 监听方A（UI）：刷新显示
// 监听方B（逻辑）：检查后续流程
// 监听方C（音频）：播放提示音
```

---

## 常用代码模板

### 在Handler中注册全局事件

```csharp
public class MyHandler : BaseHandler<MyHandler, MyManager>
{
    public override void Awake()
    {
        base.Awake();
        // 注册全局事件
        EventHandler.Instance.RegisterEvent<string>(
            EventsInfo.MyModule_DataChange,
            OnDataChange
        );
    }

    private void OnDestroy()
    {
        // 必须注销！否则内存泄漏
        EventHandler.Instance.UnRegisterEvent<string>(
            EventsInfo.MyModule_DataChange,
            OnDataChange
        );
    }

    private void OnDataChange(string dataId)
    {
        // 处理逻辑
    }
}
```

### 在UI中注册实例事件

```csharp
public class UIExample : BaseUIView
{
    public override void OpenUI()
    {
        base.OpenUI();
        // BaseUIView 已继承 BaseEvent，可直接注册
        RegisterEvent(EventsInfo.MyModule_DataChange, OnDataChange);
    }

    public override void CloseUI()
    {
        base.CloseUI();
        // CloseUI 会自动调用 UnRegisterAllEvent()
    }

    private void OnDataChange()
    {
        RefreshUI();
    }
}
```

### 带数据的事件通信

```csharp
// 发送方
public void OnItemCollected(SomeBean item)
{
    // 通知背包更新
    EventHandler.Instance.TriggerEvent(EventsInfo.MyModule_DataChange);

    // 通知UI显示获取提示
    EventHandler.Instance.TriggerEvent<SomeBean>(
        "ItemCollected",
        item
    );
}

// 接收方
private void OnEnable()
{
    EventHandler.Instance.RegisterEvent<SomeBean>(
        "ItemCollected",
        OnItemCollectedNotify
    );
}

private void OnItemCollectedNotify(SomeBean item)
{
    // 显示获取道具的UI提示
    ToastHint<UIToastNormal>($"获得 {item.name}");
}
```

---

## 事件调试

### 检查事件注册情况

```csharp
// EventHandler 内部维护 Dictionary<string, Delegate>
// 可以通过遍历检查哪些事件已注册
// 在 EventHandler.cs 中可以添加调试方法
```

### 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 事件不触发 | 接收方未注册 | 检查 RegisterEvent 是否在 OnEnable 中调用 |
| 事件触发但参数错误 | 参数数量/类型不匹配 | 检查 TriggerEvent 和 RegisterEvent 的参数类型 |
| 内存泄漏 | 未注销事件 | OnDestroy/OnDisable 中调用 UnRegisterEvent |
| 事件触发多次 | 重复注册 | 确保每次注册只执行一次，或先注销再注册 |

---

## EventEntity（泛型事件信号）

**文件**: `Assets/FrameWork/Scripts/BaseSystem/Event/EventEntity.cs`

```csharp
// 线程安全的事件信号，用于非主线程场景
public class EventSignal<T> where T : class
{
    // 用法类似弱事件模式
}
```

---

## 文件位置速查

| 功能 | 文件路径 |
|------|----------|
| 全局事件管理器 | `Assets/FrameWork/Scripts/BaseSystem/Event/EventHandler.cs` |
| 事件信号实体 | `Assets/FrameWork/Scripts/BaseSystem/Event/EventEntity.cs` |
| 实例事件基类 | `Assets/FrameWork/Scripts/Base/BaseEvent.cs` |
| 事件常量（游戏层自建） | `Assets/Scripts/Common/EventsInfo.cs`（按本项目需要创建） |

---

## 注意事项

1. **事件注销是必须的**: 注册了就必须在合适时机注销（OnDestroy/OnDisable），否则会造成内存泄漏和重复触发。
2. **参数类型严格匹配**: TriggerEvent 的参数类型必须与 RegisterEvent 完全一致，否则不会触发。
3. **全局 vs 实例**: 跨模块通信用 EventHandler.Instance，组件内部通信用 BaseEvent。
4. **事件名使用常量**: 不要在代码中硬编码事件名字符串，一律在 EventsInfo 中定义常量。
5. **避免循环触发**: A事件触发B事件，B事件又触发A事件会导致死循环。
6. **性能考虑**: 高频事件（如每帧触发）应避免使用全局事件，改用直接调用。
