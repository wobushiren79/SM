---
name: feedback_text_replace_enum
description: 文本含动态数值时一律优先用 TextReplaceEnum 占位符 + TextHandler.GetTextReplace 通用机制，禁止 string.Format 特判或把数值写死进文本
metadata:
  type: feedback
---

凡是「多语言文本里需要嵌入运行时数值」的场景（描述、名称、详情等），**一律优先使用 `TextReplaceEnum` 占位符 + `TextHandler.GetTextReplace` 通用机制**，不要自己 `string.Format("{0}", ...)` 特判，也不要把数值直接写死进静态文本（数值调整后文本会过期，且 8 种语言要逐个改）。

**Why:** 这是项目已有的通用基础设施（成就 `GetLevelDescription`、BUFF `UIViewBuffShowItem` 均走此路），统一后：① 模板里占位符是语义化枚举名（`{Value}`/`{KillNum}`），各语言可自行调整语序，比位置参数 `{0}` 可读性高；② 数值与文本解耦，调数值只改代码常量；③ 后续维护者看到 `{枚举名}` 就知道走通用机制，不用猜每处的拼接方式。反例：研究节点「空格突进/突进冷却」曾把距离/冷却写死进文本，又曾用 `string.Format("{0}")`，2026-08 已统一到本机制（见 `ResearchInfoBeanPartial.GetNameLanguageWithLevelDetail`）。

**How to apply:**
- 模板：Excel 语言表文本里写 `{枚举名}` 占位符（枚举名与 `TextReplaceEnum` 值同名，如 `控制魔王时可进行突进（距离{Value}）`），8 语言各自决定占位符位置；通用数值用 `Value`，有语义占位的优先用语义占位（击杀用 `KillNum`、秒用 `Time_S`、百分比用 `Percentage`），没有合适的再在 `TextReplaceEnum`（BaseGameEnum.cs）追加新枚举值。
- 代码：构造 `Dictionary<TextReplaceEnum, string>` 后调 `TextHandler.Instance.GetTextReplace(...)`。模板来自 UIText 表用 `GetTextReplace(id, dic)` 重载；来自其他配置表先经 `_language` 属性取模板（见 [[feedback_prefer_language_property]]）再调 `GetTextReplace(originText, dic)` 重载。
- 替换值格式化：float 直接 `$"{value}"`（1.5→"1.5"、3→"3"）；百分比用 `MathUtil.GetPercentage`；取整用 `Mathf.FloorToInt`。
- 数值源必须单一真实源（如 `UserUnlockBean.SPACE_DASH_*` 常量），UI 显示与实际生效逻辑引用同一常量，禁止两边各写一份数值。
- 详细机制与两个重载区别见 localization-system skill 的「文本替换（动态参数）」章节与 [[reference_language_excel_source]]。
