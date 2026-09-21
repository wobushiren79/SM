---
name: reference_language_excel_source
description: 多语言 Language_*.txt 的真实源是 excel_language 工作簿的同名工作表，改文本必须改 Excel 否则导出被覆盖
metadata:
  type: reference
---

`Assets/Resources/JsonText/Language_{CfgName}_{cn,en}.txt` 是**派生产物**，真实源是 `Assets/Data/Excel/excel_language[多语言_FrameWork].xlsx` 里**与 `{CfgName}` 同名的工作表**（如成就 = `AchievementInfo` 工作表）。

- 工作表列：`id / content_{lang} / content_1_{lang} / remark`，lang 共 12 种：cn/en/jp/kr/tw/de/fr/ru/es/br/pl/tr（es=西班牙语、br=巴西葡萄牙语、pl=波兰语、tr=土耳其语，2026-08 新增）。
- `content`(index0)=名字/主文本，`content_1`(index1)=详情/描述；一个 id 一行同时给两种语言的两条文本。
- `Language_UIText_*` **不是例外**：它同样由 `excel_language` 的 `UIText` 工作表（列 `id/content_cn/content_en/.../remark`）生成——`ExcelEditorWindow` 对文件名含 `excel_language` 的表走 `ExcelToJsonItemForLanguage` → `Language_{sheet}_{lang}.txt`，运行时 `TextHandler.GetTextById(id)` → `LanguageCfg.GetItemData("UIText",id)` 读的就是它。`excel_ui_text[UI文本_FrameWork].xlsx` 是**另一张遗留表**（走 `ExcelToJsonItemForBase` → 单独的 `UIText.txt`，其列 `content[language]` 存 id 数字、文本在 `remark_content` 列、无英文列，运行期不读）；`excel_language/UIText` 每行 `remark` 标 `excel_ui_text` 只是标注内容出处。**改 UIText 文本必须改 `excel_language/UIText`（真实源，含 12 语言列）**；为防遗留同步覆盖，可顺带把同 id 行补进 `excel_ui_text/UIText`。注意 `excel_language/UIText` 工作表存在历史遗留**重复列**（`content_jp`~`content_ru` 出现两次，共 16 列），新增行两组列必须填相同值（导出按列名后者覆盖前者，值相同则无害）。
- 每个配置(BuffInfo/ItemsInfo/AbyssalBlessingInfo/...)的多语言都在 `excel_language` 的同名工作表里，不在各自的 `excel_xxx_info` 表内。

**坑**：只改 `.txt` 会在下次 ExcelEditorWindow 导出时被覆盖丢失。修改文本**必须改 `excel_language` 对应工作表**（用 openpyxl，见 [[reference_unityskills_shadergraph_limits]] 同类 Excel 读写规范），再导出 `.txt`；可同时手动写 `.txt` 让运行期即时生效。与 CLAUDE.md「配置表数据修改：Excel 是唯一真实源」一致。相关：成就描述用 `name`/`details` 双列同指一个文本id + `{Name}` 占位符模板（见 achievement-system / localization-system skill 的 GetTextReplace）。
