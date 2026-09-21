---
name: commit
description: 按模块归类、生成结构化中文 git 提交信息。用户通过 /commit 触发：读取当前工作区改动（默认包含未暂存与已暂存），按改动所在目录（游戏业务 / 框架 / 编辑器 / 资源 / 配置表 等）归类汇总，输出一条规范的中文 commit message，并执行 git commit。
disable-model-invocation: true
---

# /commit —— 规范化中文提交

为 ScreenMiner 项目生成符合项目习惯的中文提交信息并完成 git 提交。仅在用户显式输入 `/commit` 时触发。

## 适用场景

- 用户完成一组改动后，希望直接 `/commit` 一键生成提交信息并提交。
- 支持任意改动规模：单文件小修，或跨多个模块的大批量改动。
- 默认提交**工作区全部改动**（已暂存 + 未暂存）；用户在参数中可附加 `staged-only` 表示只提交已暂存。

## 执行流程

### 1. 收集改动

```powershell
git status --porcelain        # 概览
git diff --stat               # 行数变化
git diff --name-status        # 改动类型 (A/M/D/R)
git diff                      # 必要时查看具体内容
```

如果用户参数包含 `staged-only`，把上述命令统统加 `--cached`。

### 2. 按模块归类

依据文件路径前缀映射到模块标签。没有固定模块清单——**按本次改动实际涉及的目录现场归纳**，同一目录的改动归为一个模块标签。常见归类参考：

| 路径模式 | 模块标签 |
|---------|---------|
| `Assets/Scripts/<领域>/**` | 按实际子目录命名模块标签（如 UI、数据、某玩法系统名） |
| `**/*Bean*.cs` | 数据模型 |
| `**/*DataService*.cs` | 数据服务 |
| `Assets/FrameWork/**` | 框架（可按子目录进一步细化，如 框架/音频、框架/UI） |
| `Assets/Editor/**` 或 `**/Editor/**` | 编辑器工具 |
| `Assets/Resources/**` 或 `Assets/AddressableAssetsData/**` | 资源 |
| `Assets/Data/Excel/**` | 配置表 |
| `.claude/**` | Claude 配置（Agent/Skill/Hook/脚本） |
| 其他 | 杂项 |

### 3. 生成提交信息

**格式约定**：

```
<主标题：动词 + 一句话总览，不超过 50 字>

- [模块A] 简述本次该模块的关键改动
- [模块B] 简述本次该模块的关键改动
- ...
```

**主标题动词**取自：新增 / 修复 / 优化 / 重构 / 调整 / 完善 / 移除。  
**多模块**：标题用最能概括的动词 + 模块数（如"调整 3 个模块的战斗与 UI"）。  
**单模块**：标题直接写该模块的具体内容（如"修复 Buff 周期触发剩余次数判断"）。  
**仅 .claude 改动**：标题前缀写 `[claude]`，例如 `[claude] 新增 PreToolUse 资源拦截 Hook`。

### 4. 执行提交

把生成的信息通过 here-string 传给 `git commit`（PowerShell 单引号 here-string，避免 `$` 被解释）：

```powershell
git add -A                    # staged-only 模式则跳过这一步
git commit -m @'
<标题>

- [模块] ...
- [模块] ...
'@
```

**重要**：`'@` 必须在第 0 列、独占一行，否则 PowerShell 解析失败。

### 5. 报告结果

提交完成后输出：

- 新提交的短 hash（`git log -1 --oneline`）
- 涉及的模块清单
- 文件统计（`git show --stat HEAD | head -1`）

## 注意事项

- **不要 `--amend`**：始终新增 commit，避免破坏历史。
- **不要 `--no-verify`**：让 pre-commit hook 正常跑。
- **签名**：沿用项目默认设置，不主动添加/移除 `-S`。
- **改动只涉及自动生成的 `*Bean.cs` 时**：标题写"重新生成 Bean"，并提示用户是否同时改了对应的 Excel/BeanPartial。
- **若工作区为空**：直接告知用户"无改动可提交"，不创建空提交。
