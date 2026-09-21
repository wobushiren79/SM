---
name: writing-great-skills
description: 写/改 Skill 的质量尺子与参考手册。当需要新建一个 .claude/skills/*/SKILL.md、或体检/重构已有 skill 是否写得"可预测、结构清晰、不冗余"时，用此手册校准。涵盖触发方式、description 写法、信息层次、粒度拆分、去冗余、引导词、常见失败模式。用户也可显式输入 /writing-great-skills 阅读。借鉴 mattpocock/skills 的 writing-great-skills，按本项目规则改写。
disable-model-invocation: true
---

# 写出好 Skill 的尺子

这是一份**参考手册**，不执行具体任务。新建或体检 skill 时拿它逐条对照。

## 1. 触发方式：model-invoked 还是 user-invoked

- **user-invoked（显式 /命令）**：在 frontmatter 加 `disable-model-invocation: true`。适合有副作用、不该自动跑的动作（如 `/commit`、`/Note`、本手册）。
- **model-invoked（自动触发）**：不加该字段。适合"该自动生效的判断/纪律"（如 `grill`、`diagnosing-bugs`）。
- 一个能力若**既想自动又想手动**，保持 model-invoked，并在 description 里把自动触发的边界写清，避免过度打扰。

## 2. description 是命中率的关键

- **触发词前置**：把"什么时候用我"放在最前面，用用户/场景真实会出现的词（中文项目用中文触发语）。本项目所有 skill 的 description 必须中文。
- **可被搜索**：description 是 model 决定调不调用的唯一依据，要把典型场景、关键类名、关键术语都塞进去。
- **不与正文重复**：description 说"何时用"，正文说"怎么做"。同一句话不要两边都写。

## 3. 信息层次：三档放置

1. **步骤（正文主体）**：要照着做的流程，写成有序步骤。
2. **skill 内参考**：表格、清单、模板——查阅性内容，和步骤分开放。
3. **skill 外参考**：指向 `MD/ProjectDocs.md`、`.claude/memory/*`、具体代码文件，用相对链接，不把外部内容抄进来。

## 4. 粒度：何时拆分

- **按触发方式拆**：自动的纪律和手动的命令分成两个 skill（如盘问循环 vs 一次性命令）。
- **按时序拆**：一个长流程里有明显独立的阶段，且各阶段可单独被调用时，拆开。
- 不要为拆而拆——彼此总是一起用、没有独立调用价值的，留在一个 skill 里。

## 5. 去冗余：单一真实源（最重要）

- **一个事实只写一处**。规则属于 CLAUDE.md 的，skill 里用链接指过去，不复制粘贴——CLAUDE.md 改了 skill 不会跟着改，复制就是制造未来的不一致。
- 删掉 no-op：没有信息量的客套话、"请仔细思考"之类空指令一律删。
- 与 `.claude/memory/` 重叠的，引用记忆条目而非重写。

## 6. 引导词：用预训练过的紧凑概念

- 用 model 已经"懂"的标准词汇（"红绿重构""幂等""单一真实源""可证伪假设"），一个词顶一句解释，输出更可预测。
- 避免生造黑话；项目专属术语第一次出现时给一句锚定或链接到文档。

## 7. 常见失败模式（自查）

- **过早完工**：步骤没走完就收尾——在流程类 skill 里显式写"做完 X 才算结束"。
- **重复**：description 与正文、skill 与 CLAUDE.md、skill 与记忆之间抄来抄去。
- **臃肿（sprawl）**：什么都往一个 skill 里塞，触发面糊成一团，model 不知道何时该用。
- **描述空泛**：description 没有具体触发词，model_invoked 命不中。

## 体检已有 skill 的用法

逐个 skill 对照上面 7 条打分，重点查：description 触发词是否具体、有没有和 CLAUDE.md/记忆重复的整段内容、是否存在该拆未拆或该并未并。发现问题就地修，改完在任务总结里列出改了哪些 skill。
