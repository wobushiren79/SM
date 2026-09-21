---
name: reference_logutil_gated
description: LogUtil 所有输出（Log/LogWarning/LogError）受 ProjectConfigInfo.IS_OPEN_LOG_MSG 总开关门控，开关关闭时插桩日志一行都不会出现——排障插桩前必须先确认该开关
metadata:
  type: reference
---

`LogUtil.Log/LogWarning/LogError`（`Assets/FrameWork/Scripts/Utils/LogUtil.cs`）全部经 `BaseDebugLog` 汇聚，首行判定 `if (!ProjectConfigInfo.IS_OPEN_LOG_MSG) return null;`——总开关关闭时**所有级别日志都静默丢弃**（包括 LogError），Console 无任何输出。

**教训（2026-09-13 大盾战士BOSS技能排障）**：加了 4 处 `[大盾Debug]` 插桩后用户测试「一条日志都没有」，一度误判为代码路径没跑到；实际护盾功能正常，只是日志开关没开。

**How to apply**：插桩排障前先确认 `ProjectConfigInfo.IS_OPEN_LOG_MSG` 为 true（或改用 `Debug.Log` 直出/弹 Toast），否则日志缺失不能作为「代码未执行」的证据。
