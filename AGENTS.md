# ScreenMiner - 开发规范

## 代码规范

### 字符串拼接

**规范**：字符串拼接必须使用 `$""` 插值语法，不要使用 `+` 连接符。

**示例**：
```csharp
// ✅ 推荐
string result = $"{name} {value}";

// ❌ 不推荐
string result = name + " " + value;
```
