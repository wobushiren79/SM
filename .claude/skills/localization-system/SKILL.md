---
name: localization-system
description: ScreenMiner 的多语言(Localization)系统开发指南。使用此SKILL当需要添加新的多语言文本、创建带多语言的配置表、在UI中显示多语言文本、切换语言等。
watched_files:
  - Assets/FrameWork/Scripts/Bean/MVC/LanguageBean.cs
  - Assets/FrameWork/Scripts/Bean/MVC/LanguageBeanPartial.cs
  - Assets/FrameWork/Scripts/Bean/MVC/UITextBean.cs
  - Assets/FrameWork/Scripts/Bean/GameConfigBean.cs
  - Assets/FrameWork/Scripts/Enums/BaseGameEnum.cs
  - Assets/FrameWork/Scripts/Component/Manager/TextManager.cs
  - Assets/FrameWork/Scripts/Component/Handler/TextHandler.cs
  - Assets/FrameWork/Scripts/Component/UI/UITextLanguageView.cs
  - Assets/Resources/JsonText/
---

# 多语言系统开发指南

## 核心概念

### 系统架构

```
LanguageBean              - 多语言数据基础类
LanguageCfg               - 多语言配置管理（按语言/配置表分类存储）
TextManager               - 文本管理器（底层获取逻辑）
TextHandler               - 文本处理器（上层接口）
UITextLanguageView        - UI多语言组件（自动更新Text）
LanguageEnum              - 语言类型枚举
```

### 多语言文件存储

```
Assets/Resources/JsonText/
├── Language_UIText_cn.txt              - UI通用文本（中文）
├── Language_UIText_en.txt              - UI通用文本（英文）
├── Language_{CfgName}_{lang}.txt       - 通用命名格式（lang ∈ cn/en/jp/kr/tw/de/fr/ru/es/br/pl/tr）
└── ...
```

> ⚠️ **真实源是 Excel，不是 `.txt`**：`Language_{CfgName}_{lang}.txt` 都是从 **`excel_language[多语言_FrameWork].xlsx` 里与 `{CfgName}` 同名的工作表**导出的产物（每个工作表列：`id / content_{lang} / content_1_{lang} / remark`）。**`Language_UIText_*` 也不例外**——它来自 excel_language 的 `UIText` 工作表（导出器只对文件名含 `excel_language` 的工作簿生成 `Language_{sheet}_{lang}.txt`）；`excel_ui_text[UI文本_FrameWork].xlsx` 只是 UIText 的 id 登记表（导出 `UIText.txt` + UITextBean，`content[language]` 列存的值=多语言 id），**新增 UI 文本两处都要加行**。**新增/修改文本必须改对应 Excel 工作表**，再用 ExcelEditorWindow 导出；只改 `.txt` 会在下次导出时被**覆盖丢失**。下文示例若直接写 `.txt` 仅为说明字段结构，落地务必同步 Excel 工作表。

### 支持的语言

```csharp
LanguageEnum
├── cn = 0    - 简体中文
├── en = 1    - 英文
├── jp = 2    - 日语
├── kr = 3    - 韩语
├── tw = 4    - 繁体中文
├── de = 5    - 德语
├── fr = 6    - 法语
├── ru = 7    - 俄语
├── es = 8    - 西班牙语
├── br = 9    - 巴西葡萄牙语
├── pl = 10   - 波兰语
└── tr = 11   - 土耳其语
```

### 新增一种语言的完整流程

1. **枚举**：`LanguageEnum` 末尾追加新值（**只能追加，禁止改已有值**，展示名数组 `languageShowNames` 顺序与之绑定）。
2. **展示名**：`LanguageBeanPartial.cs` 的 `languageShowNames` 末尾追加 `简称/该语言自称`（如 `es/Español`）。
3. **Steam 映射**：`LanguageCfg.GetInitialLanguage()` 补充 Steam 语言串→新枚举的映射（见下文）。
4. **Excel**：给 `excel_language` **全部工作表**加列——单内容列结构的表加 `content_{lang}`，含详情列的表加 `content_{lang}` 与 `content_1_{lang}`；元数据行（第 2 行类型 `string`、第 3 行中文描述）一并补齐。
5. **导出**：ExcelEditorWindow 导出后自动生成 `Language_{sheet}_{lang}.txt`（导出器按 `EnumExtension.GetEnumNames<LanguageEnum>()` 驱动，加完枚举即自动识别新列，无需改导出代码）。
6. **字体**：新增其他文字体系的语言时，先核对主 UI 字体的 SDF 回退链字符覆盖。

---

## 默认语言初始化（Steam 优先）

### 初始化策略

新用户（无 GameConfig 存档）首次启动时按下列优先级决定语言，已有存档则保留用户保存的偏好：

```
1. Steam 已连上（SteamManager.Initialized == true）
   └─ SteamApps.GetCurrentGameLanguage() 返回值
      ├─ schinese → cn   tchinese → tw   其他含 chinese → cn
      ├─ japanese → jp   koreana → kr
      ├─ german → de     french → fr     russian → ru
      ├─ spanish/latam → es   brazilian/portuguese → br
      ├─ polish → pl     turkish → tr
      └─ 其他（english / ...）→ en
2. 未连上 Steam 或异常 → en
```

### 关键代码

**[LanguageBeanPartial.cs](Assets/FrameWork/Scripts/Bean/MVC/LanguageBeanPartial.cs)** — 在 `LanguageCfg` 中提供 `GetInitialLanguage()` 和静态构造（覆盖自动生成文件中的 `currentLanguage = ""`）。

**[GameConfigBean.cs](Assets/FrameWork/Scripts/Bean/GameConfigBean.cs)** — `language` 默认空串，`GetLanguage()` 空串时回落到 Steam 检测：

```csharp
//语言（留空时由 LanguageCfg.GetInitialLanguage 判定）
public string language = "";

public LanguageEnum GetLanguage()
{
    string lang = string.IsNullOrEmpty(language) ? LanguageCfg.GetInitialLanguage() : language;
    return EnumExtension.GetEnum<LanguageEnum>(lang);
}
```

### 初始化时序

```
BaseLauncher.Start()
└─ TextHandler.Instance.InitData()
   └─ GameDataHandler.Instance.manager.GetGameConfig()
      ├─ Load() 成功 → 用户保存的 language
      └─ Load() == null → new GameConfigBean() → language = ""
   └─ gameConfig.GetLanguage()
      └─ language 为空时 → LanguageCfg.GetInitialLanguage()
   └─ ChangeLanguageEnum(language)
      └─ LanguageCfg.ChangeLanguageData(language)
```

### 注意事项

1. **`LanguageBean.cs` 是自动生成文件**：`public static string currentLanguage = "";` 不能直接改，必须通过 `LanguageBeanPartial.cs` 的静态构造覆盖。
2. **静态构造时机**：静态构造在首次访问 `LanguageCfg` 任意成员时触发，由 C# 运行时保证在字段初始化器之后执行。
3. **`GameConfigBean.language` 不硬编码**：旧存档中字面值为空串的会触发 Steam 检测，已显式存了的不变。

---

## 使用现有文本

### 通过ID获取文本

```csharp
// 获取UI通用文本
string text = TextHandler.Instance.GetTextById(1001);

// 获取指定配置表的文本
string name = TextHandler.Instance.GetTextById("XxxInfo", 10001);
```

### 在配置Bean中使用多语言

配置表字段存储文本ID，通过属性获取本地化文本：

```csharp
public partial class XxxInfoBean : BaseBean
{
    public long name;           // 文本ID
    public long content;        // 描述文本ID
    
    [JsonIgnore]
    public string name_language { 
        get { return TextHandler.Instance.GetTextById(XxxInfoCfg.fileName, name); } 
    }
    
    [JsonIgnore]
    public string content_language { 
        get { return TextHandler.Instance.GetTextById(XxxInfoCfg.fileName, content); } 
    }
}
```

使用方式：
```csharp
XxxInfoBean info = XxxInfoCfg.GetItemData(10001);
string name = info.name_language;      // 获取本地化名称
string desc = info.content_language;   // 获取本地化描述
```

### UI中显示多语言

**方式1：使用UITextLanguageView组件（推荐静态文本）**

```csharp
// 在Prefab的Text组件上挂载UITextLanguageView
// 设置textId字段为对应的文本ID
```

**方式2：代码动态设置**

```csharp
// 普通Text
Text textUI = GetComponent<Text>();
textUI.text = TextHandler.Instance.GetTextById(1001);

// TextMeshProUGUI
TextMeshProUGUI tmpText = GetComponent<TextMeshProUGUI>();
tmpText.text = TextHandler.Instance.GetTextById(1001);
```

---

## ⚠️ 一个多语言ID承载多条文本（content / content_1 / content_2）

**这是创建带多语言的配置表时必须遵守的核心规则。**

### 规则说明

同一个多语言ID（多语言JSON里的**一行**）最多可以承载 **3 条文本**：

| contentIndex | JSON字段 | 用途约定 |
|--------------|----------|----------|
| 0（默认） | `content`   | 名称 / 主文本 |
| 1 | `content_1` | 详情 / 描述 |
| 2 | `content_2` | 额外文本（备注等） |

由 [TextManager.GetTextById](Assets/FrameWork/Scripts/Component/Manager/TextManager.cs) 的 `contentIndex` 参数选择读取哪一列（约定：textId=0 表示无文本，静默返回空串不报错）。

**因此「名称」和「详情」应当共用同一个多语言ID**，分别用 `content`（index 0）和 `content_1`（index 1）取值，**而不是分配两个独立ID**。

### 正确示例（名称+详情共用一个ID —— 标准做法）

配置表 `XxxInfo.txt`：`name` 与 `details` 指向**同一个ID**：
```json
{"name":1000001001,"details":1000001001,"id":1000001001, ...}
```

多语言表 `Language_XxxInfo_cn.txt`：一行同时给出名称和详情：
```json
{"id":1000001001,"content":"条目名称","content_1":"条目详情描述"}
```

Bean 中名称读 index 0、详情读 index 1（注意两个属性传入**同一个 id 字段**）：
```csharp
[JsonIgnore]
public string name_language {
    get { return TextHandler.Instance.GetTextById(XxxInfoCfg.fileName, name); }          // content
}
[JsonIgnore]
public string details_language {
    get { return TextHandler.Instance.GetTextById(XxxInfoCfg.fileName, name, 1); }        // content_1（同一个 id）
}
```

### 错误示例（应避免 —— 拆成两个ID）

```json
// ❌ 名称和详情各占一个独立ID，浪费ID、割裂同一条目的文本
{"id":4001001,"content":"条目名称 I"}
{"id":4001002,"content":"条目详情描述"}
```

### 何时仍可拆分

仅当名称和详情**确实需要独立复用 / 独立维护**（例如多个条目共享同一个名称但详情不同）时，才使用独立ID。**默认一律共用一个ID + content_1。**

---

## 添加新多语言文本

### 1. 添加到现有配置表

**步骤1：修改配置Bean（Partial）**

```csharp
public partial class XxxInfoBean : BaseBean
{
    // 添加新的文本ID字段
    public long new_field;
    
    [JsonIgnore]
    public string new_field_language { 
        get { return TextHandler.Instance.GetTextById(XxxInfoCfg.fileName, new_field); } 
    }
}
```

**步骤2：在Excel配置表中添加文本ID数据**（`excel_language` 对应工作表加文本行 + 配置表加 id 列值）

**步骤3：ExcelEditorWindow 导出**（生成/刷新 `Language_XxxInfo_*.txt` 与 Bean）

### 2. 创建全新的多语言配置表

**步骤1：创建配置Bean类**

```csharp
// Assets/Scripts/Bean/MVC/Game/MyFeatureInfoBean.cs
using System;
using Newtonsoft.Json;

[Serializable]
public partial class MyFeatureInfoBean : BaseBean
{
    public long name;           // 名称+详情共用的文本ID（推荐：一个ID承载 content/content_1）
    
    [JsonIgnore]
    public string name_language { 
        get { return TextHandler.Instance.GetTextById(MyFeatureInfoCfg.fileName, name); }        // content（index 0）
    }
    
    [JsonIgnore]
    public string description_language { 
        get { return TextHandler.Instance.GetTextById(MyFeatureInfoCfg.fileName, name, 1); }     // content_1（index 1，同一个 id）
    }
}
```

**步骤2：创建多语言数据**

在 `excel_language` 中加 `MyFeatureInfo` 同名工作表（名称+详情共用一个ID）：
```
id | content_cn | content_en | content_1_cn | content_1_en | ...
1  | 功能名称    | Feature    | 功能描述内容  | Feature desc | ...
```
导出后生成 `Language_MyFeatureInfo_{lang}.txt`。

**步骤3：使用**

```csharp
MyFeatureInfoBean data = MyFeatureInfoCfg.GetItemData(1);
string name = data.name_language;
string desc = data.description_language;
```

---

## 文本替换（动态参数）

当文本中包含变量时使用文本替换功能。

> ⭐ **强约定**：凡是「多语言文本里嵌入运行时数值」的场景，**一律优先使用本机制**（`TextReplaceEnum` 占位符 + `GetTextReplace`），**禁止** `string.Format("{0}")` 特判拼接、也**禁止**把数值写死进静态文本（调数值后全语种文本全部过期）。数值源须单一真实源（代码常量），UI 显示与实际逻辑引用同一常量。记忆：`feedback_text_replace_enum`。

### 定义带占位符的文本

```json
{"content":"击杀{KillNum}个敌人","id":1001}
{"content":"造成伤害{AttackDamage}","id":1002}
{"content":"生命值低于{HPRateLess}%","id":1003}
```

### 代码中使用

```csharp
// 创建替换字典
Dictionary<TextReplaceEnum, string> replaces = new Dictionary<TextReplaceEnum, string>
{
    { TextReplaceEnum.KillNum, "10" },
    { TextReplaceEnum.AttackDamage, "500" }
};

// 获取替换后的文本
string text = TextHandler.Instance.GetTextReplace(1001, replaces);
// 结果: "击杀10个敌人"
```

> **两个重载（重要区别）**：
> - `GetTextReplace(long id, dic)` —— **只从 UIText 表**(`UITextCfg`) 按 id 取模板再替换。仅适用于通用 UI 文本。
> - `GetTextReplace(string originText, dic)` —— 直接对**传入的字符串**替换。当模板来自**其他配置表**（自有 Language 表）时，必须**先**用 `GetTextById(cfgName, id, contentIndex)` 取到模板字符串，**再**调本重载。例：
>
> ```csharp
> // 优先用框架自动生成的 _language 属性取模板(带缓存), 不要手写 GetTextById(fileName, id, idx)
> string template = info.details_language; // = content_1, "累计击杀 {Name} 只"
> var dic = new Dictionary<TextReplaceEnum, string> { { TextReplaceEnum.Name, "100" } };
> string desc = TextHandler.Instance.GetTextReplace(template, dic); // "累计击杀 100 只"
> ```
>
> 占位符语法是 `{枚举名}`（如 `{Name}`/`{KillNum}`/`{Time_H}`），与 `TextReplaceEnum` 值同名；字典里给哪个键就替换哪个占位符，模板里写死的文案原样保留。

### 可用的替换类型

```csharp
TextReplaceEnum
├── Name              - 名字
├── Percentage        - 百分比
├── Time_S            - 时间（秒）
├── Time_M            - 时间（分钟）
├── Time_H            - 时间（小时）
├── KillNum           - 击杀数
├── UnderAttackDamage - 承受伤害
├── AttackDamage      - 造成伤害
├── HPRateLess        - 生命值低于百分比
├── RegainHPReceived  - 累计被治疗HP
├── RegainHPCast      - 累计施放治疗HP
├── OnFieldTime       - 在场存活时间(秒)
└── Value             - 通用数值占位（无专属语义枚举时的默认选择）
```

> **选键原则**：有语义占位的优先用语义占位（击杀→`KillNum`、秒→`Time_S`、百分比→`Percentage`），无合适语义时用通用 `Value`；都不合适再在 `TextReplaceEnum`（BaseGameEnum.cs）**追加**新枚举值（不改旧值）。同一数值可同时挂多个键。

---

## 切换语言

### 玩家入口约定

在合适的 UI（主界面/设置界面）提供语言选择列表：
- 按 LanguageEnum 数量实时生成列表项，展示名用 `LanguageCfg.GetLanguageShowName(language)`（"英文简称/该语言自称"，如 `cn/中文`、`en/English`），展示名数组在 LanguageBeanPartial.cs（顺序与 LanguageEnum 一致）。
- **点击切换**：`TextHandler.ChangeLanguageEnum` → `SaveGameConfig` 立即持久化 → `RefreshAllUI` + 当前 UI 重启刷新。

### 运行时切换语言

```csharp
// 切换到英文
TextHandler.Instance.ChangeLanguageEnum(LanguageEnum.en);

// 切换到中文
TextHandler.Instance.ChangeLanguageEnum(LanguageEnum.cn);
```

### 获取当前语言

```csharp
string currentLang = LanguageCfg.currentLanguage;  // "en" 或 "cn"
LanguageEnum langEnum = GameDataHandler.Instance.manager.GetGameConfig().GetLanguage();
```

### 语言切换后刷新UI

切换语言后需要手动刷新UI显示：

```csharp
// 方案1：遍历所有UITextLanguageView组件
UITextLanguageView[] textViews = FindObjectsByType<UITextLanguageView>(FindObjectsSortMode.None);
foreach (var view in textViews)
{
    view.RefreshUI();
}

// 方案2：发送全局事件通知UI刷新
EventHandler.Instance.TriggerEvent(EventsInfo.Language_Change);
```

---

## 常用代码模板

### 快速添加多语言支持到UI

```csharp
public class MyUIComponent : BaseUIComponent
{
    public Text titleText;
    public Text descText;
    
    public void SetData(long titleId, long descId)
    {
        titleText.text = TextHandler.Instance.GetTextById(titleId);
        descText.text = TextHandler.Instance.GetTextById(descId);
    }
}
```

### 带参数的多语言文本

```csharp
public string GetLevelText(int level)
{
    Dictionary<TextReplaceEnum, string> replaces = new Dictionary<TextReplaceEnum, string>
    {
        { TextReplaceEnum.Name, level.ToString() }
    };
    return TextHandler.Instance.GetTextReplace(1001, replaces);
}
```

### 防止文本换行（空格替换为不间断空格）

```csharp
// 将普通空格替换为不间断空格，防止在空格处换行
string text = TextHandler.Instance.GetTextByIdNoBreakingSpace("XxxInfo", 10001);
```

---

## 文件位置速查

| 功能 | 文件路径 |
|------|----------|
| 多语言数据Bean（自动生成） | `Assets/FrameWork/Scripts/Bean/MVC/LanguageBean.cs` |
| 多语言Bean手写扩展（含 Steam 默认语言判定） | `Assets/FrameWork/Scripts/Bean/MVC/LanguageBeanPartial.cs` |
| UI文本Bean | `Assets/FrameWork/Scripts/Bean/MVC/UITextBean.cs` |
| 游戏配置（含 language 字段、`GetLanguage()` 空串回退） | `Assets/FrameWork/Scripts/Bean/GameConfigBean.cs` |
| 语言枚举 | `Assets/FrameWork/Scripts/Enums/BaseGameEnum.cs` |
| 文本管理器 | `Assets/FrameWork/Scripts/Component/Manager/TextManager.cs` |
| 文本处理器 | `Assets/FrameWork/Scripts/Component/Handler/TextHandler.cs` |
| UI多语言组件 | `Assets/FrameWork/Scripts/Component/UI/UITextLanguageView.cs` |
| 多语言JSON文件 | `Assets/Resources/JsonText/Language_*.txt` |
| Bean代码模板 | `Assets/FrameWork/Editor/ScriptsTemplates/Excel_LanguageEntity.txt` |

---

## 注意事项

1. **文本ID唯一性**：同一配置表内的文本ID必须唯一，不同配置表可以重复
2. **textId=0 保留为「无文本」约定**：`GetTextById` 对 id=0 静默返回空串，不报「没有找到文本」错误。不需要名字的字段应配 0，而不是指向不存在的行
3. **一个ID承载多条文本**：名称与详情应共用同一个ID（`content` / `content_1` / `content_2`，最多3条），通过 `GetTextById(..., contentIndex)` 区分，禁止默认就拆成两个独立ID（详见上方 ⚠️ 专章）
4. **JSON格式**：多语言JSON文件必须使用UTF-8编码，确保中文正常显示
5. **字段命名**：配置表中的文本字段名建议与多语言属性名对应（如`name`对应`name_language`）
6. **延迟加载**：多语言文本是按需加载的，首次访问时会从JSON文件读取
7. **编辑器预览**：在Editor中可以直接使用`UITextLanguageView`预览多语言效果
