---
name: feedback-excel-id-sorted-insert
description: 新增配置表数据行必须按 id 升序插入到正确位置，禁止 append 追加到末尾
metadata:
  type: feedback
---

向 `Assets/Data/Excel/` 下任何配置表（含 `excel_language` 的各子表）新增数据行时，必须按 `id` 由小到大插入到表中对应位置，保证整张表 id 始终升序，**禁止**直接 append 追加到末尾。统一走 `.claude/scripts/excel_add_row.py`（默认按 id 排序插入，仅当新 id 比所有现有 id 都大时才落到末尾），或复用其排序插入逻辑；不要自己写「写到最后一个数据行之后」的内联脚本。

**Why:** 用户指出我新增"伤害性极强"深渊馈赠时，BuffInfo 表的 `3000500001~005` 被追加到了末尾，而它们数值上小于已有的 `11xxx/12xxx/13xxx`，正确位置应在 `3000400005` 之后，破坏了 id 升序。append 式写入只在"新 id 恰好最大"时才碰巧正确（如深渊馈赠主表 `2000004xxx`），不可依赖。

**How to apply:** 改配置表前先确认新 id 在现有 id 序列中的位置；用 `excel_add_row.py` 新增（它会 `insert_rows` 到第一个比新 id 大的行之前），避免 `--append`。批量新增多行时按 id 升序逐条插入。插入后做一次"全表 id 升序"校验。相关：[[feedback-bean-partial]]、[[feedback-task-summary]]。
