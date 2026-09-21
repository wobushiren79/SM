---
name: csharp-auto-comment
description: 自动为C#类脚本添加XML注释和#region区域分隔。当用户输入/Note命令时触发，分析当前C#脚本文件，为每个方法、属性、字段添加规范的XML注释，并按类型（生命周期/公有/私有/属性等）使用#region进行分组。
watched_files:
  - scripts/add_comments.py
---

# C# 自动注释工具

## 触发条件

当用户输入 `/Note` 命令时触发此skill。

## 工作流程

1. **识别目标文件**：确定当前需要处理的C#脚本文件路径
2. **解析代码结构**：分析类中的成员（方法、属性、字段、事件等）
3. **添加XML注释**：为每个无注释的成员添加规范的XML文档注释
4. **添加#region分组**：按类型将成员分组，使用#region/#endregion包裹

## 成员分类规则

使用以下规则对类成员进行分类：

| 分类 | 包含内容 | #region 名称 |
|------|----------|--------------|
| 序列化字段 | 带有 `[SerializeField]` 特性的字段 | #region Serialized Fields |
| 常量 | const 字段 | #region Constants |
| 事件 | event 声明 | #region Events |
| 属性 | 属性访问器 | #region Properties |
| Unity生命周期 | Awake, Start, OnEnable, OnDisable, OnDestroy, Update, FixedUpdate, LateUpdate 等 | #region Unity Lifecycle |
| 公有方法 | public 方法（非生命周期） | #region Public Methods |
| 保护方法 | protected 方法 | #region Protected Methods |
| 私有方法 | private 方法 | #region Private Methods |
| 内部方法 | internal 方法 | #region Internal Methods |

## XML注释模板

### 方法注释
```csharp
/// <summary>
/// 方法功能简述
/// </summary>
/// <param name="参数名">参数说明</param>
/// <returns>返回值说明</returns>
```

### 属性注释
```csharp
/// <summary>
/// 属性功能简述
/// </summary>
```

### 字段注释
```csharp
/// <summary>
/// 字段功能简述
/// </summary>
```

## 使用脚本

使用 `scripts/add_comments.py` 脚本自动处理C#文件：

```bash
python scripts/add_comments.py <文件路径>
```

脚本将：
1. 读取C#源文件
2. 解析类结构和成员
3. 为无注释的成员添加XML注释
4. 按类型重新组织代码，添加#region分组
5. 输出处理后的代码

## 注意事项

- 保留原有注释（如果有）
- 不要修改已有#region结构
- 保持原有代码缩进和格式
- 对于异步方法，在summary中标注"异步"
- 对于override方法，在summary中标注"重写"