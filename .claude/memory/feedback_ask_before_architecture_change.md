---
name: ask-before-architecture-change
description: 涉及改变原有架构/数据流向的修改（如配置来源从 Excel 表迁到代码字段）必须先询问用户确认，不能自行决定
metadata:
  type: feedback
---

涉及**改变原有架构或数据流向**的修改，必须先用 AskUserQuestion 询问用户确认方案后再动手，禁止自行决定。典型例子：把"献祭升级加点数"的数据来源从 Excel 配置表（`LevelInfo.attribute_point`）迁移到代码字段（`UserLimmitBean`）——用户原本的设计是走 Excel 配置，AI 擅自改成代码字段后被要求回滚。

**Why:** 项目对数据归属有既定架构设计（数值配置走 Excel 唯一真实源、运行时限制基础值走 UserLimmitBean 等）。用户提需求时可能忘记原有设计（"都忘记这个事了"），AI 单方面迁移数据来源会破坏既定架构，且回滚成本高（代码+Excel+JSON+多份文档）。

**How to apply:** 当任务隐含"改变某数据的存放位置/来源/流向"时（配置表⇄代码常量⇄存档字段之间迁移、改变单一真实源、废弃既有配置列等），先指出现状与用户要求的冲突，用 AskUserQuestion 给出方案选项（如"保持 Excel 配置仅改数值"vs"迁到代码字段"），确认后再实施。仅调整数值大小、新增同构数据行等不改变架构的修改可直接执行。相关：[[excel-id-sorted-insert]]
