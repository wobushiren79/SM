---
name: system-localization
description: 多语言系统开发：TextHandler/TextManager、UITextLanguageView、语言切换、语言资源加载。
tools: Read, Write, Edit, Glob, Grep, Bash
watched_files:
  - Assets/FrameWork/Scripts/Component/Handler/TextHandler.cs
  - Assets/FrameWork/Scripts/Component/Manager/TextManager.cs
  - Assets/FrameWork/Scripts/Component/UI/UITextLanguageView.cs
  - Assets/FrameWork/Scripts/Bean/MVC/LanguageBeanPartial.cs
  - Assets/FrameWork/Scripts/Bean/GameConfigBean.cs
  - Assets/Resources/JsonText/
---

# 多语言系统 (Localization System) 开发代理

你负责多语言系统的开发。

## 职责范围

### 多语言管理
- **TextHandler** - 多语言逻辑处理，语言切换接口 [FrameWork/Scripts/Component/Handler/TextHandler.cs](Assets/FrameWork/Scripts/Component/Handler/TextHandler.cs)
- **TextManager** - 多语言文本管理器，加载语言 JSON 资源 [FrameWork/Scripts/Component/Manager/TextManager.cs](Assets/FrameWork/Scripts/Component/Manager/TextManager.cs)

### 多语言 UI 组件
- **UITextLanguageView** - 多语言文本组件，自动根据 key 切换语言 [FrameWork/Scripts/Component/UI/UITextLanguageView.cs](Assets/FrameWork/Scripts/Component/UI/UITextLanguageView.cs)

### 多语言数据
- **LanguageBean / LanguageBeanPartial** - 多语言数据模型；`LanguageBeanPartial.cs` 中的 `LanguageCfg` 静态构造与 `GetInitialLanguage()` 负责默认语言判定（Steam 优先）
- **UITextBean / UITextBeanPartial** - UI 文本数据模型
- **GameConfigBean** - `language` 字段默认空串；`GetLanguage()` 空串时回落到 `LanguageCfg.GetInitialLanguage()`

### 默认语言初始化（Steam 优先）
首次启动且无 GameConfig 存档时按以下规则决定语言：
1. `SteamManager.Initialized == true` → `SteamApps.GetCurrentGameLanguage()`：`schinese`→`cn`、`tchinese`→`tw`、其他含 `chinese`→`cn`、`japanese`→`jp`、`koreana`→`kr`、`german`→`de`、`french`→`fr`、`russian`→`ru`、`spanish`/`latam`→`es`、`brazilian`/`portuguese`→`br`、`polish`→`pl`、`turkish`→`tr`，其余 → `en`
2. 未连上 Steam / 抛异常 → `en`

语言枚举 `LanguageEnum`：`cn=0 / en=1 / jp=2 / kr=3 / tw=4 / de=5 / fr=6 / ru=7 / es=8 / br=9(巴西葡萄牙语) / pl=10 / tr=11`（追加不改旧值，存档兼容）。

实现位置：[LanguageBeanPartial.cs](Assets/FrameWork/Scripts/Bean/MVC/LanguageBeanPartial.cs)（静态构造 + `GetInitialLanguage()`），[GameConfigBean.cs](Assets/FrameWork/Scripts/Bean/GameConfigBean.cs)（`GetLanguage()` 空串回退）。

> 注意：`LanguageBean.cs` 是自动生成的，`currentLanguage = ""` 不能直接改，必须用 `LanguageBeanPartial.cs` 的静态构造覆盖。

### 语言资源
- 存放路径：`Assets/Resources/JsonText/Language_UIText_*.txt`

### 数据流
```
TextManager 加载 Language_UIText_*.txt
    → LanguageBean / UITextBean 解析
    → UITextLanguageView 绑定 key
    → 语言切换时自动更新所有 UITextLanguageView
    → 触发 EventsInfo 语言变更事件
    → 各 UI 模块刷新显示文本
```

## 约束

- **真实源是 Excel，不是 `.txt`**：`Language_{CfgName}_{lang}.txt` 由 **`excel_language[多语言_FrameWork].xlsx` 中与 `{CfgName}` 同名工作表**导出（列 `id/content_{lang}/content_1_{lang}/remark`）。`Language_UIText_*` 同样来自 excel_language 的 `UIText` 工作表（导出器只对文件名含 `excel_language` 的工作簿生成 `Language_{sheet}_{lang}.txt`）；`excel_ui_text` 只是 UIText id 登记表（导出 `UIText.txt`+UITextBean），新增 UI 文本两处都要加行。改文本**必须改对应 Excel 工作表**再导出——只改 `.txt` 会在下次导出被覆盖丢失
- 多语言 key 统一放在 Excel 中管理，通过 ExcelEditorWindow 导出
- 所有文本显示必须使用 UITextLanguageView 或通过 TextHandler 获取
- 新增文本 key 需在 Excel 配置中添加
- 语言切换触发全局事件，所有 UI 需响应刷新

## ⚠️ 一个多语言ID承载多条文本（content / content_1 / content_2）

**创建带多语言的配置表时必须遵守的核心规则。**

同一个多语言ID（多语言JSON里的一行）最多承载 3 条文本，由 `GetTextById(cfgName, id, contentIndex)` 的 `contentIndex` 选择：

| contentIndex | JSON字段 | 用途约定 |
|--------------|----------|----------|
| 0（默认） | `content`   | 名称 / 主文本 |
| 1 | `content_1` | 详情 / 描述 |
| 2 | `content_2` | 额外文本 |

- **名称与详情默认共用同一个ID**：配置表里 `name` 与 `details` 字段指向**同一个 ID**，名称读 `content`（index 0）、详情读 `content_1`（index 1）。多语言JSON一行即写全：`{"id":1000001001,"content":"名称","content_1":"详情描述"}`。
- **禁止**默认就把名称和详情拆成两个独立ID——浪费ID、割裂同一条目文本。仅当名称/详情需独立复用时才拆分。
- Bean 两个 `_language` 属性须传入**同一个 id 字段**，仅 `contentIndex` 不同：
  ```csharp
  public string name_language    => TextHandler.Instance.GetTextById(Cfg.fileName, name);      // content
  public string details_language => TextHandler.Instance.GetTextById(Cfg.fileName, name, 1);   // content_1（同一个 id）
  ```

## 占位符替换 GetTextReplace（通用动态文本）

> ⭐ **强约定**：多语言文本里嵌入运行时数值的场景**一律走本机制**，禁止 `string.Format("{0}")` 特判拼接、禁止把数值写死进静态文本；数值源须单一真实源（代码常量），UI 显示与实际逻辑引用同一常量（记忆：`feedback_text_replace_enum`）。

文本里用 `{枚举名}` 占位符（枚举为 `TextReplaceEnum`，如 `{Name}`/`{KillNum}`/`{Time_H}`/`{Percentage}`/`{Value}`），运行期用 `Dictionary<TextReplaceEnum,string>` 替换。两个重载，**区别关键**：

| 重载 | 取模板来源 | 用途 |
|------|-----------|------|
| `GetTextReplace(long id, dic)` | **只从 UIText 表**(`UITextCfg`) 按 id 取 | 通用 UI 文本 |
| `GetTextReplace(string originText, dic)` | 直接对传入字符串替换 | 模板来自**其他配置表**自有 Language 表时用：先 `GetTextById(cfgName,id,idx)` 取模板，再调本重载 |

```csharp
// 模板存于业务配置表(非 UIText), 必须走 string 重载
// 取模板优先用框架自动生成的 _language 属性(带缓存), 别手写 GetTextById(fileName, id, idx)
string template = info.details_language; // = content_1, "累计击杀 {Name} 只"
var dic = new Dictionary<TextReplaceEnum, string> { { TextReplaceEnum.Name, "100" } };
string desc = TextHandler.Instance.GetTextReplace(template, dic); // "累计击杀 100 只"
```

- **同一模板套不同数值**：把"一个条目多个等级目标"做成一条带 `{Name}` 的模板，按级替换即可；省去逐级建文本。
- 模板里写死的文案（数字、单位等）原样保留；字典给哪个键替换哪个占位符。
- **选键原则**：有语义占位优先语义占位（击杀 `{KillNum}`、秒 `{Time_S}`、百分比 `{Percentage}`），无合适语义用通用 `{Value}`，都不合适再在 `TextReplaceEnum` 追加新枚举（不改旧值）。详见 [localization-system] skill。
