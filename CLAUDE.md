# CLAUDE.md

## 回复语言规则

**所有 AI 的回答，以及让用户做的任何选择（如 AskUserQuestion 的问题与选项），都必须使用中文。** 包括任务说明、总结、提问、选项标签与描述等面向用户的文本一律用中文表述。

## Shell 优先级规则

**执行命令行操作时一律优先使用 PowerShell（pwsh 7+）**，遵循 PowerShell 语法（`$null`、`$env:VAR`、反引号续行、动词-名词 cmdlet 等）。仅当任务确需 POSIX/Unix 脚本能力时才改用 Bash。

## Python 执行规则

**运行任何 Python（脚本或 `-c` 内联）一律通过包装脚本 [.claude/scripts/run-python.ps1](.claude/scripts/run-python.ps1)，禁止用写死的 python.exe 绝对路径直接调用**。原因：本机 `python`/`py` 不一定在 PATH 上（python.exe 常只装在 `%LOCALAPPDATA%\Programs\Python\PythonXY\`），写死绝对路径既违反「路径动态化规则」，又无法被一条可复用的 allow 规则稳定命中，导致每次执行都弹权限确认。

- **标准调用形式**（已被 `settings.json` 的 allow 规则预授权，永不弹窗）：

  ```
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".claude/scripts/run-python.ps1" <脚本.py 或 -c "代码"> [参数...]
  ```

- `run-python.ps1` 会按 `PATH → py launcher → %LOCALAPPDATA%\Programs\Python\* → Program Files\Python*` 顺序动态定位 python，并自动设置 `PYTHONUTF8=1` 保证中文输出不乱码，退出码原样透传。
- 自检解析到的解释器：加 `-WhichOnly` 参数。
- **委派给 Agent/Skill 执行 Python 任务时**，须在 prompt 中告知统一走 `run-python.ps1`，不要写死 python.exe 绝对路径。

## 路径动态化规则

**所有需要记录/写入文件的路径（配置、脚本、权限规则、文档示例等）一律使用动态/相对地址，禁止写死静态绝对路径**（如 `E:\Unity\Project\...`、`C:\Users\<USER>\...`）。原因：项目会在不同电脑、不同用户、不同盘符下打开，静态绝对路径换环境即失效。

具体要求：

- **权限规则（`.claude/settings*.json`）**：用相对项目根目录的写法（如 `Read(.claude/scripts/**)`），用户主目录用 `~`（如 `Read(~/.claude/projects/**/memory/**)`），禁止写绝对盘符路径。
- **PowerShell 脚本**：用 `$PSScriptRoot` 推导脚本所在目录、`$env:USERPROFILE` 取用户主目录；项目根目录 = 脚本位置按层级 `Split-Path` 向上推导（`.claude/scripts/` 下脚本向上两级即项目根）。
- **Python 脚本**：用 `os.path.dirname(__file__)` / `Path(__file__).resolve().parents[N]` 推导项目根，禁止硬编码绝对路径；可变路径通过命令行参数传入。
- **文档/示例**：涉及用户名、盘符的路径用占位符（如 `C:\Users\<USER>\...`）或相对路径，不写具体机器路径。
- **记忆文件**：统一存项目内 `.claude/memory/`（见下方「记忆系统」），随 git 共享，禁止写入 C 盘用户主目录。

## Unity资源修改规则

所有Unity资源文件的修改（创建、编辑、删除）**优先通过 Unity MCP（mcpforunityserver）进行**，以下类型文件不要直接用 Write/Edit 工具盲目操作：

- `.prefab` - 预制体
- `.unity` - 场景
- `.mat` - 材质
- `.anim` / `.controller` - 动画/动画控制器
- `.asset` - ScriptableObject等资源
- `.meta` - 资源元数据
- 其他Unity序列化的二进制/YAML资源文件

当 Unity MCP **未连接**时，按下方「MCP连接与Unity操作规则」先询问用户是否开启 MCP；用户选择不开启时，再评估是否用其他方式（如手工提示用户在 Unity 编辑器中操作）处理，不得在未告知的情况下直接编辑上述资源文件。

C#脚本（`.cs`）不受此限制，可以正常直接编辑。

## MCP连接与Unity操作规则

MCP 相关操作**优先执行，但不再强制自动执行**。涉及 Unity 资源/场景/GameObject 操作时，按以下流程处理：

1. **MCP连接检测**：运行 `.claude/scripts/check-unity-mcp.ps1` 检查 HTTP 服务器状态。
2. **未连接时先询问**：若检测到 MCP 未连接/未启动，**先询问用户是否要开启 MCP**（可用 AskUserQuestion），不要擅自启动或直接跳过。
   - 用户同意开启：自动启动服务器并继续后续握手流程。
   - 用户选择不开启：改用其他方式完成任务（如提示用户手工在 Unity 编辑器中操作、或退化为非 MCP 的处理路径），并在总结中说明未使用 MCP。
3. **MCP会话初始化**（已连接或用户同意开启后执行）：发送 `initialize` 请求并获取 `Mcp-Session-Id`，随后发送 `notifications/initialized` 完成握手。
4. **Unity实例查询与设置**：读取 `mcpforunity://instances` 资源获取活跃实例，调用 `set_active_instance` 设置目标实例。
5. **通过Unity MCP工具操作场景/GameObject/资源**：调用 `manage_scene`、`manage_gameobject`、`manage_asset` 等 MCP 工具。

MCP 已连接（或用户已同意开启）后，上述操作的 PowerShell 命令（`Invoke-WebRequest`/`Invoke-RestMethod` 到 `http://127.0.0.1:8080/mcp`）均视为已授权，可直接执行无需逐步确认。

## Play 模式验证规则

**凡是需要进入 Unity Play 模式（点击 ▶ 运行游戏）验证的环节，一律由用户手动完成，禁止 AI 通过 MCP 自动启动/停止 Play 模式自行验证。**

- **禁止自动验证**：不得调用 `manage_editor` 的 `play`/`pause`/`stop`、`batch_execute`、`execute_menu_item` 等 MCP 工具"跑一遍看效果"，也不得用 MCP 自动操作游戏内部流程代替真实操作。
- **原因**：AI 自动启动的 Play 流程与真实操作不一致（时序、焦点、镜头、输入模拟等环节容易出问题），验证结果不可信；只有用户手动操作才与真实游戏流程一致。
- **正确做法**：AI 完成代码/资源修改后，若运行结果需要 Play 验证，明确告知用户：
  1. 请用户在 Unity 编辑器中**手动点击 Play**；
  2. 列出**检查要点**（如"打开 XX 界面，确认 XX 显示正常/数字符合预期"）；
  3. 用户**截图**（或描述现象、粘贴 Console 报错）发回；
  4. AI 依据截图与描述判断是否通过；未通过则继续修复，再请用户重测。
- **不受影响**：非 Play 态的 MCP 操作（改场景/资源、编辑器测试 `run_tests`、脚本生成等）仍按上一节「MCP连接与Unity操作规则」正常使用。

## 代码注释与分类规则

所有 C# 文件中的方法和属性必须：

- 使用 `/// <summary>` XML 注释说明用途
- 用 `#region` / `#endregion` 按功能分类组织代码

**方法体内的注释（行内/局部注释）尽量单行显示**：

- 优先用一行写完，避免冗长的多行注释块。
- 发现已有多行注释时，先**尝试归纳总结**成更精炼的一行。
- 仅当总结后一行仍放不下（内容确实复杂）时，才退回多行显示。

## Agent/Skill 文档同步规则

每个 `.claude/agents/*.md` 与 `.claude/skills/*/SKILL.md` 在 frontmatter 里用 `watched_files` 声明了它所对应的代码文件/目录。**当你修改了某个被 `watched_files` 命中的代码文件时，必须在同一次任务内同步更新对应的 agent/skill 文档**（枚举值、流程、文件速查表、示例等），不得只改代码不更文档——文档过时等同于给后续协作者/AI 喂错误信息。

- **自动提示机制**：`PostToolUse` Hook（[.claude/scripts/check-cs-changed.ps1](.claude/scripts/check-cs-changed.ps1)）会在每次 Write/Edit 改动 `Assets/**/*.cs` 后，调用 [.claude/scripts/check-watched.ps1](.claude/scripts/check-watched.ps1) 比对 git 改动与各 `watched_files`，用 `systemMessage` 列出**仅命中本次改动文件**的 Agent/Skill。收到该提示后必须逐一核对并同步，确认无需改动的也要在任务总结里说明原因。
- **手动核对**：任何时候可运行 `.claude/scripts/check-watched.ps1`（可加 `-BaseRef origin/master` 比对整个分支）查看当前工作树命中了哪些 Agent/Skill。
- **当前局限**：自动 Hook 仅在改动 `.cs` 文件时触发；若改的是被 `watched_files` 声明的 `.txt`/`.json`/`.asset` 等非 `.cs` 文件，需**手动**运行 `check-watched.ps1` 核对。
- **脚本编码约束**：`.claude/scripts/*.ps1` 含中文注释时**必须存为 UTF-8 with BOM**——Hook 实际由 Windows PowerShell 5.1 (`powershell.exe`) 执行，无 BOM 时它会按系统 ANSI(GBK) 误读中文，导致脚本逻辑串位失效。

## 输入处理规则

游戏内所有键盘/手柄等输入处理一律走 **InputActionUIEnum + Unity InputSystem** 体系，**禁止使用旧版 `Input` API**（如 `Input.GetKeyDown`、`Input.GetKey`、`Input.GetMouseButton`、`Input.GetAxis` 等）。

- UI 类（继承 `BaseUIInit`/`BaseUIView`/`BaseUIComponent`）通过重写 `OnInputActionForStarted(InputActionUIEnum inputType, InputAction.CallbackContext callback)` 响应输入，输入动作来源于框架层 `GameInputActions.inputactions`（`Assets/FrameWork/Prefabs/Input/`），由 `InputManager.dicInputUI` 映射到 `InputActionUIEnum`。
- 新增按键需求时，应在 `GameInputActions.inputactions` 中配置绑定、在 `InputActionUIEnum` 中补充枚举，再通过 `OnInputActionForStarted` 派发，**不要**在 `Update()` 里轮询 `Input`。
- 数字键已封装为 `InputActionUIEnum.N1~N9`（同时绑定主键盘与小键盘），可直接复用。

## 异步与定时逻辑规则

游戏内延迟/定时/顺序流程等异步逻辑（动画编排、等待执行、分步流程等），**一律优先使用框架层 [GTask](Assets/FrameWork/Scripts/Utils/GTask.cs) 门面处理**：

- **等待**：`GTask.Wait`/`WaitReal`（受/不受 timeScale 的秒级等待）、`GTask.WaitFrame`/`WaitFrames(n)`、`GTask.WaitUntil`/`WaitWhile`、`GTask.WaitTween`（等 DOTween 播完，均收 `GTaskCancel`，可空=不可取消）。
- **发射**：发射即忘的异步方法声明为 **`async UniTaskVoid`**，调用点用 **`_ = Method()`** 显式丢弃（消除「未观察异步调用」警告；取消的 OCE 静默、真异常由 UniTaskScheduler 记录，无需 try/catch）；**禁止 `async void`**——其取消抛出的 `OperationCanceledException` 会作为未处理异常进 Console。`GTask.Run` 仅用于「方法返回 `UniTask` 供他处 await，个别调用点又要发射即忘」的复用场景。
- **取消**：取消源 `GTask.NewCancel(gameObject)` 懒创建一次复用（链接销毁令牌自动收口），每次开始任务调 `Reset()` 重建令牌，停止调 `Cancel()`（幂等）。
- **业务层不要直接** new `CancellationTokenSource`、传 `CancellationToken`、调 UniTask 原生 API（`UniTask.Delay`/`.Forget()` 等）——统一由 GTask 封装。UniTask 已通过 OpenUPM 源引入（`com.cysharp.unitask`，见 `Packages/manifest.json`）。
- **避免使用协程**（`StartCoroutine`/`IEnumerator`）——停止/取消依赖 `StopCoroutine`/`StopAllCoroutines`，关闭管理不便且易残留；**Update 逐帧轮询仅在万不得已时使用**（必须逐帧且无法异步表达的持续逻辑）。
- **存量写法豁免**：框架 async 桥接（`IEnumeratorAwaitExension.cs` 的 `await new WaitForSeconds(x)`/`Awaiters.Until(...)` 等）与存量协程（资源加载/Web 请求/AudioHandler 等）暂不强制重构；**新增与改动的代码按本规则执行**。

## Bean 修改规则

文件是否可改**只看"文件头是否带自动生成标记"**（不看路径、不看文件名是否以 `Bean.cs` 结尾、也不看是否存在同名 Partial）：

- **自动生成、禁止直接修改**：文件头带有 `AUTO-GENERATED-DO-NOT-EDIT` 标记（`// <auto-generated>` 注释块）的文件。该标记由生成工具 `ExcelEditorWindow.CreateEntity` 及模板 [Excel_LanguageEntity.txt](Assets/FrameWork/Editor/ScriptsTemplates/Excel_LanguageEntity.txt) 在每次生成时写入 `*Bean.cs` 头部。扩展方法、辅助属性、解析逻辑必须写在对应的 `*BeanPartial.cs` 中。
- **手写、可直接修改**：文件头**没有**该标记的文件。包括：
  - 手写的运行时数据 Bean（如 `Assets/Scripts/Bean/Game/**/*Bean.cs`，字段与核心逻辑均为手工维护）。
  - **MVCEditorWindow 脚手架生成的 Bean**："空脚手架生成一次→手工填字段"的模式，**不带标记、可直接手改**（字段就是手工维护的，不会被重新生成）。
  - 任意 `*Partial.cs`（始终可改）。

> PreToolUse Hook [.claude/scripts/block-bean-edits.ps1](.claude/scripts/block-bean-edits.ps1) **纯按标记**拦截：读目标文件头若含 `AUTO-GENERATED-DO-NOT-EDIT` 即拦（与路径无关），`*Partial.cs` 及一切无标记文件放行。注意：Excel 生成的 Bean 需在 Unity 跑过一次"生成 Entity"带上标记后才会被拦。

## 记忆系统

项目记忆存储在 `.claude/memory/` 目录下，所有 AI 协作记忆（feedback、project、user、reference）均写入此目录，**禁止写入用户个人目录（C盘）**。读写记忆时路径统一使用：

```
.claude/memory/MEMORY.md         # 索引文件
.claude/memory/<name>.md         # 各条记忆文件
```

**团队共享机制**：`.claude/memory/` 随 git 提交，所有成员 clone/pull 即可获得。由于 Claude Code 原生只自动加载用户主目录下的记忆（不读仓库内的 `.claude/memory/`），项目通过 `.claude/settings.json` 的 **SessionStart Hook**（`.claude/scripts/load-memory.ps1`）在每次会话开始时把 `MEMORY.md` 索引注入上下文，确保任何成员的 AI 都能识别。新增/修改记忆后**必须同步更新 `MEMORY.md` 索引**，否则不会被注入。

### 领域术语主动校准（domain-modeling）

记忆/文档不只是单向记录，遇到用词不准时要**主动校准**，把项目术语磨锋利——目标是"用 1 个词代替 20 个词"，让后续协作用项目黑话即可对齐，而非每次长篇解释。

- **主动质疑用词**：当用户或文档用了**模糊、歧义或自相矛盾**的术语时（如"那个数值/这个表"指代不清，或同一概念在不同处叫不同名字），先指出并提议一个精确、一致的叫法，确认后再继续——不要将就着用模糊词往下做。
- **沉淀到记忆**：达成一致的关键术语（实体名、字段含义、模块边界）按本章规则写入 `.claude/memory/`（reference/project 类）并更新 `MEMORY.md`，让术语成为团队共享词汇。
- **保持一致**：同一概念全项目用同一个词；发现旧记忆/文档与新约定冲突时，按"单一真实源"原则更新旧条目而非新增重复条目。
- **边界**：只在术语确实影响沟通/实现准确性时校准，不为咬文嚼字打断正常推进。

## Excel 读写规则

所有通过脚本对 `.xlsx` 文件的读取和写入操作必须使用 **openpyxl** 库，并遵守以下规范：

- 文件编码统一使用 **UTF-8**（openpyxl 默认支持，无需额外指定）
- 读取时使用 `openpyxl.load_workbook(path)` 或 `load_workbook(path, read_only=True)`
- 写入时调用 `workbook.save(path)` 保存，**不得覆盖原文件前未备份**
- 禁止使用 `xlrd`、`xlwt`、`xlwings`、`pandas.read_excel` 等其他 Excel 库
- Python 脚本文件统一存放在 `.claude/scripts/` 目录下

### 配置表数据修改：Excel 是唯一真实源

当用户要求**新增/修改/删除配置表数据**时（例如 `excel_*[*].xlsx` 下的任何配置表），必须遵守：

- **Excel 源表必须修改**：`Assets/Data/Excel/excel_*.xlsx` 是配置数据的唯一真实源（single source of truth），任何配置数据变更**必须落到对应的 Excel 文件**。
- **对应的 JSON 可以不修改**：`Assets/Resources/JsonText/*.txt` 是由 Excel 通过 `ExcelEditorWindow` 编辑器工具导出生成的产物，理论上是可再生的派生数据。
  - 如果只改 JSON 不改 Excel，下次运行编辑器导出工具时会**直接覆盖丢失**这次修改 —— 严禁此类操作。
  - 仅修改 Excel 而不同步 JSON 时，应在任务总结中明确告知用户："JSON 未同步，需在 Unity 编辑器中运行配置导出工具重新生成"。
- **当 Excel 与 JSON 数据不一致时**（例如 JSON 存在但 Excel 缺失），默认以 **JSON 现存的运行时数据为参考**补齐 Excel，并提示用户核对源头是否还有遗漏。
- **禁止**仅修改 JSON 文件来"快速生效"配置变更，即使运行时立即可见，也是技术债，下一次导出就会丢失。

### Excel 备份清理规则

修改 Excel 前为防丢失数据创建的备份文件（如 `xxx.xlsx.bak`、`xxx.xlsx.bak.20260524_150955` 等任何形式的副本），在任务结束时**必须及时删除**，禁止遗留：

- **判定标准**：仅为本次修改做的"编辑前快照"或一次性回滚副本，属于临时备份，必须清理。
- **严禁留在 `Assets/Data/Excel/` 目录内**：该目录会被 `ExcelEditorWindow` 的"全部导出/全部生成 Entity"按文件遍历，导出的 JSON 以**工作表名**命名。备份文件含同名工作表时会**覆盖真表导出的 JSON**（典型症状：单个导出正常，全部导出却把数据还原成旧值），同时 Unity 还会为其生成多余的 `.meta`。
- **删除时机**：Excel 改动已验证/落盘后，立即删除备份文件（及其 `.meta`）。
- **确需长期保留备份时**：放到仓库工作区**之外**或 `Assets/` 之外的目录（例如仓库根的 `ExcelBackup/` 并加入 `.gitignore`），**绝不**放在被导出工具扫描的 Excel 目录里。
- **禁止把备份提交进 git**：提交前确认 `git status` 中没有 `*.bak*` 文件被 `add`。
- **委派给 Agent/Skill 修改 Excel 时**，须在 prompt 中明确告知"任务结束前删除所有 Excel 备份文件"。
- **任务结束总结**中如创建过 Excel 备份，应说明已删除（或已移出 Excel 目录）的备份路径，便于用户审计。

## 临时脚本清理规则

为完成单次任务而临时生成的 **PowerShell**（`.ps1`）或 **Python**（`.py`）脚本，在任务结束后必须**及时删除**，避免污染项目目录：

- **判定标准**：仅用于本次任务一次性执行（如临时图片合成、临时数据转换、一次性查询等），且不属于可复用工具链一部分的脚本，视为"临时脚本"。
- **删除时机**：脚本执行完毕、产出结果已经被验证或落盘后，立即删除该脚本文件。
- **保留例外**：明确具有复用价值、长期维护需求或被项目其他流程引用的脚本（例如位于 `.claude/scripts/` 下的通用工具脚本），不属于临时脚本，**不应删除**。是否保留如有疑问，须先与用户确认。
- **委派给 Agent/Skill 执行任务**时，若过程中产生临时脚本，亦需在任务结束总结前完成清理，或在 prompt 中明确告知子代理执行该清理动作。
- **任务结束总结**中如有创建过临时脚本，应在总结里简要说明已删除的脚本路径，便于用户审计。

## PixelLab 像素图生成规则

### 调用前必须征得用户同意（最高优先级）

PixelLab 是付费外部服务（消耗账号 credits），用户可能不想使用它。**任何**调用生成类工具（`create_*`、`animate_*`）之前，必须满足以下其一，否则禁止调用：

- 用户在**当前请求中明确要求**生成像素图（如使用"生成像素图/画像素图/生成像素美术"等触发词），且生成对象就是用户点名的内容；
- 已先向用户说明"计划用 PixelLab 生成 X（会消耗 credits）"并获得**明确同意**（可用 AskUserQuestion 或直接询问）。

特别禁止：**在配置表/代码等其他任务中"顺带"自行生成图片**（例如新增配置时发现缺图标就直接生成）。缺图时应留空或使用占位图，在任务总结中告知用户缺图，由用户决定是否生成。**委派给 Agent/Skill 执行 PixelLab 任务时**，prompt 中必须注明"用户已同意使用 PixelLab"；子代理未收到该声明时应拒绝生成并返回要求先征得同意。

### Outline（描边）规则

使用 PixelLab MCP 工具生成像素图时，所有生成的图片中的物体轮廓必须带有 **outline（描边）**：

- 调用任何生成类工具（`create_character`、`create_object`、`create_isometric_tile`、`create_topdown_tileset`、`create_sidescroller_tileset`、`create_tiles_pro` 等）时，必须在 `description` 或相关参数中明确要求 outline，例如添加描述词：`with black outline`、`outlined`、`with clear pixel outline`。
- 若工具提供独立的 outline 参数，优先使用该参数开启描边。
- 禁止生成无轮廓（no outline）的像素图片。

### 生成等待与轮询规则

PixelLab 所有生成类工具均为异步任务（返回 job/资源 ID 后需要后续查询）。**无论是主对话直接调用，还是通过 Agent（如 general-purpose、Explore、Plan 等子代理）或 Skill 间接调用 PixelLab MCP 工具**，在等待生成结果期间均必须遵守以下轮询规范：

- **轮询间隔固定为 60 秒**：每次调用对应的 `get_*` 工具（如 `get_character`、`get_object`、`get_isometric_tile`、`get_topdown_tileset`、`get_sidescroller_tileset`、`get_tiles_pro` 等）查询状态后，若状态仍为 `processing` / `pending` / `review` 未完成，等待 60 秒再发起下一次查询，不要进行其他操作。
- **不得使用更短的轮询间隔**（如每 1~15 秒查询一次），避免对 PixelLab 服务造成不必要的负担。
- 等待过程中应通过 `ScheduleWakeup` 或带有 60 秒延迟的脚本/sleep 命令实现间隔检测，禁止使用空轮询或无延迟循环。
- 一旦状态变为 `completed` 或 `failed`，立即停止轮询并处理结果。
- **委派给 Agent/Skill 执行 PixelLab 任务时**，必须在 prompt 中明确写明"轮询间隔固定为 60 秒"的要求，确保子代理或技能内部循环亦遵守该规则。

## 任务结束总结规则

每次任务处理完成后的总结中，如果有 Agent 或 Skill 参与执行，必须列出：

- **Agent**：每个 Agent 的名称及其执行的具体操作
- **Skill**：每个 Skill 的名称及其执行的具体操作
