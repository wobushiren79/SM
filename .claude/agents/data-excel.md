---
name: data-excel
description: Excel配置表处理：ExcelUtil、EPPlus、ExcelEditorWindow配置导出、Excel-JSON转换。直接读写xlsx文件使用openpyxl脚本。
tools: Read, Write, Edit, Glob, Grep, Bash
skills:
  - excel-io
watched_files:
  - Assets/FrameWork/Scripts/Utils/ExcelUtil.cs
  - Assets/FrameWork/Editor/Base/Window/ExcelEditorWindow.cs
  - Assets/Data/Excel/
  - Assets/Resources/JsonText/
  - .claude/scripts/excel_read.py
  - .claude/scripts/excel_write.py
  - .claude/scripts/excel_schema.py
  - .claude/scripts/excel_find.py
  - .claude/scripts/excel_add_row.py
  - .claude/scripts/excel_delete_row.py
---

# Excel 配置表 (Excel Config) 开发代理

你负责 Excel 配置表的读取、导出和维护。

## Excel 读写规则（重要）

直接操作 `.xlsx` 文件时，必须使用 **openpyxl** 库，不得使用其他 Excel 库。
详细操作方式参考 skill: **excel-io**（`.claude/skills/excel-io/SKILL.md`）。

### 配置表行布局（统一规范）

| 行号 | 用途 |
|------|------|
| 1 | 列名（英文，如 `id`、`hp`） |
| 2 | 数据类型（`long`、`int`、`string`、`float`） |
| 3 | 中文说明 |
| 4+ | 实际数据 |

所有脚本默认 `--header-rows 3`。如某张表布局不同可显式覆盖该参数。

### 快捷脚本

| 脚本 | 用途 |
|------|------|
| `.claude/scripts/excel_read.py` | 读取 Excel 表数据并打印（含表头） |
| `.claude/scripts/excel_schema.py` | 查看 Sheet 列表、单 Sheet 表头与样例 |
| `.claude/scripts/excel_find.py` | 按列条件查询/过滤数据行 |
| `.claude/scripts/excel_add_row.py` | 新增配置行（默认 id 查重，并按 id 由小到大插入正确位置） |
| `.claude/scripts/excel_write.py` | 修改已有单元格（按行列 / 按 ID 单列 / 按 ID 多列） |
| `.claude/scripts/excel_delete_row.py` | 删除配置行（表头受保护，支持 --dry-run） |

```bash
# 查看表结构
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".claude/scripts/run-python.ps1" ".claude/scripts/excel_schema.py" --path "Assets/Data/Excel/excel_xxx[说明].xlsx" --sheet XxxInfo --sample 2

# 读取
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".claude/scripts/run-python.ps1" ".claude/scripts/excel_read.py" --path "Assets/Data/Excel/excel_xxx[说明].xlsx" --rows 5

# 查询（数值范围/包含/精确）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".claude/scripts/run-python.ps1" ".claude/scripts/excel_find.py" --path "Assets/Data/Excel/excel_xxx[说明].xlsx" --where id=1001 --col id --col hp

# 新增
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".claude/scripts/run-python.ps1" ".claude/scripts/excel_add_row.py" --path "Assets/Data/Excel/excel_xxx[说明].xlsx" --set id=999001 --set class_entity=XxxEntity --backup

# 修改（按 ID 多列批量）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".claude/scripts/run-python.ps1" ".claude/scripts/excel_write.py" --path "Assets/Data/Excel/excel_xxx[说明].xlsx" --find-col id --find-id 1001 --set hp=500 --backup

# 删除
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".claude/scripts/run-python.ps1" ".claude/scripts/excel_delete_row.py" --path "Assets/Data/Excel/excel_xxx[说明].xlsx" --id 999001 --backup
```

> Python 调用统一走 `.claude/scripts/run-python.ps1` 包装脚本（见 CLAUDE.md「Python 执行规则」），禁止写死 python.exe 绝对路径。

## 职责范围

### Excel 处理工具
- **openpyxl**（Python）- 直接读写 xlsx 文件（唯一允许的库）
- **ExcelUtil** - Unity 内 Excel 读取与转换工具（C# 静态类，运行时程序集可直接调）：`GetExcelPackage`(EPPlus 读取)、`SetExcelData`(按 id+列名写单元格)、`ExcelToJsonItem`(单文件 Excel→Json 导出静态实现；`string` 重载用默认 JsonText 目录并刷新 AssetDatabase，供编辑器内工具保存后同步生成 JSON)
- **EPPlus** - Unity Excel 处理库（Assets/FrameWork/Plugins/EPPlus/）
- **ExcelEditorWindow** - Excel 编辑器窗口（导出 JSON，单文件导出 `ExcelToJsonItem(FileInfo)` 转调 ExcelUtil 静态实现）
  - **主工具栏入口（Unity 6000.3+ MainToolbarElement）**：左侧「Excel处理」下拉（`MainToolbarDropdown`），菜单直接执行「打开窗口 / 导出所有 Json(`QuickExcelToJson`) / 生成所有 Entity(`QuickCreateEntities`)」——快捷操作走 `ExcelToJsonAll`/`CreateEntitiesAll` 静态实现 + `DefaultExcelFolderPath` 等默认路径，不打开窗口。⚠️ 元素 ID 不可改——主工具栏按 ID 持久化 displayed 状态，改 ID 会被当新元素默认隐藏（见 memory `reference_unity6000_maintoolbar_element`）
  - **自动化导出/生成路径（Unity MCP）**：无需手点窗口按钮，可通过 Unity MCP 的 `execute_code` 调公共方法完成——`GetWindow<ExcelEditorWindow>(false, null, false)` 拿到窗口实例后依次调 `ExcelToJson()`（等效「所有 Excel 转 Json」）+ `CreateEntities()`（等效「生成所有 Entity」）

### 配置表位置
- **原始 Excel**: `Assets/Data/Excel/`
- **导出 JSON**: `Assets/Resources/JsonText/`

### 关键文件

| 文件 | 路径 |
|------|------|
| Excel 读取脚本 | `.claude/scripts/excel_read.py` |
| Excel 写入脚本 | `.claude/scripts/excel_write.py` |
| ExcelUtil (C#) | `Assets/FrameWork/Scripts/Utils/ExcelUtil.cs` |
| ExcelEditorWindow | `Assets/FrameWork/Editor/Base/Window/ExcelEditorWindow.cs` |
| 配置目录 | `Assets/Data/Excel/` |
| 导出目录 | `Assets/Resources/JsonText/` |

---

## 配置表总览

> 本项目配置表清单随业务开发补充于此。每张表记录：文件名（`excel_xxx[中文说明].xlsx` 命名约定）、Sheet 名、主要列（含 id 段位约定、language 列引用、`valid` 列等）。

### 框架系统（FrameWork，预期）

| 文件名 | Sheet | 主要列 |
|--------|-------|--------|
| `excel_audio_info[音频信息_FrameWork].xlsx` | AudioInfo | id, name_res, remark, audio_type(0音效/1音乐/2环境音), volume_scale |
| `excel_base_info[基础信息_FrameWork].xlsx` | BaseInfo | id, content |
| `excel_language[多语言_FrameWork].xlsx` | UIText + 各业务子表 | id, content_{语言}（含 content_1_* 详情列） |
| `excel_spine_animation_state[骨骼动画枚举_FrameWork].xlsx` | SpineAnimationState | id, res |
| `excel_ui_text[UI文本_FrameWork].xlsx` | UIText | id, content[language] |

> `excel_language` 为多 Sheet 工作簿：UIText + 每个业务配置表一个同名子表（存该表的 name/details 多语言文本）。

## 约束

- 读写 xlsx 必须使用 openpyxl，编码 UTF-8
- **新增数据必须按 id 由小到大排序插入**：新增配置行时不要直接追加到表格末尾，而要根据 id 大小插入到中间对应位置，保证整张表的 id 始终保持升序。`excel_add_row.py` 已默认按 id 排序插入（新 id 比所有现有 id 都大时才落到末尾）；除非特殊需求，禁止使用 `--append` 强制追加打乱排序。
- 写入前使用 `--backup` 参数备份原文件
- 配置表为统一 3 行表头规范（列名/类型/中文说明），数据从第 4 行开始；脚本默认 `--header-rows 3`
- 配置表修改后必须通过 ExcelEditorWindow 导出 JSON
- 导出的 JSON 文件编码为 UTF-8
- 新增配置表需在编辑器工具中注册
- 多语言文本通过 `excel_language[多语言_FrameWork].xlsx` 统一管理，各表的 `name[language]`、`content[language]` 列均引用该表
- 文件头带 `AUTO-GENERATED-DO-NOT-EDIT` 标记的 `*InfoBean.cs` / `*Bean.cs` 是自动生成的，禁止直接修改
- **`valid` 有效性列约定（生成器内置过滤）**：任意配置表只要含名为 `valid` 的列（int，`0`=无效/`1`=有效），`ExcelEditorWindow.CreateEntity` 生成的 `Cfg` 会自动加 `valid!=0` 过滤——`GetAllArrayData` 过滤数组、`GetItemData` 改走 `GetAllArrayData`，valid==0 的行运行时彻底不存在。⚠️ 给某表新增 `valid` 列后必须把现有每行填 `1` 并重新导出，否则该表全部数据被当无效丢弃（JSON int 缺省 0）。详见 editor-extension-system SKILL。
- PowerShell 操作含中文/方括号的文件路径时使用 `Copy-Item -LiteralPath` / `Remove-Item -LiteralPath` 避免方括号被解析为通配符
