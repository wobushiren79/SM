---
name: feedback_prefer_language_property
description: 取多语言文本优先用框架自动生成的 _language 属性，不手写 GetTextById(fileName, id, idx)
metadata:
  type: feedback
---

读取配置 Bean 的多语言文本时，**优先使用框架自动生成的 `xxx_language` 属性**（如 `name_language`/`details_language`/`content_language`），不要手写 `TextHandler.Instance.GetTextById(Cfg.fileName, id, contentIndex)`。

**Why:** `xxx_language` 是 MVC 生成器按 Excel 的 `[language]`/`[language_1]` 列标记自动生成的框架级属性，内部封装了 `GetTextById(fileName, 对应字段, contentIndex)` 并带 `LanguageCache` 缓存。手写 GetTextById 重复了框架已做的事、绕过缓存、且把 fileName/contentIndex 硬编码进业务代码，易与 Excel 列标记不一致。

**How to apply:**
- 名称读 `name_language`（content index 0），详情/描述读 `details_language`（content index 1）。需要做占位符替换时：先 `string tmpl = info.details_language;` 取模板，再 `TextHandler.GetTextReplace(tmpl, dic)`（见 [[reference_language_excel_source]] 的 GetTextReplace 用法）。
- 仅当某 id 没有生成对应 `_language` 属性（如临时桥接字段、生成 Entity 之前）才退而手写 GetTextById；一旦「生成 Entity」补出 `_language` 属性就切回去。
- 例：成就描述 `AchievementInfoBean.GetLevelDescription` 用 `details_language` 取模板（早期 details 还是桥接字段时曾手写 GetTextById，转正后已改回 `_language`）。
