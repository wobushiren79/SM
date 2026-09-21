---
name: feedback_comment_sync
description: 修改代码逻辑时必须同步更新对应的 XML 注释，保持注释与实现一致
metadata:
  type: feedback
---

修改代码逻辑时，对应的 `/// <summary>` 注释必须同步修改，反映新的行为。

**Why:** 用户发现注释未随代码变动更新，导致注释与实现不一致，容易误导阅读者。

**How to apply:** 每次修改方法/属性的实现逻辑后，立即检查并更新其 `/// <summary>` 注释，确保描述与当前代码行为一致。
