---
name: feedback_toasthint_state
description: UIHandler.ToastHintText(content, state) 的 state 第二参数约定 0=失败 1=成功，别传错图标
metadata:
  type: feedback
---

`UIHandler.ToastHintText(string content, int state = 0)`（[UIHandler.cs:23](Assets/Scripts/Component/Handler/UIHandler.cs#L23)）的第二个参数 `state` 控制提示图标：

- `0` = **失败**：红色图标 `ui_other_3`（#E32626），也是默认值。
- `1` = **成功**：绿色图标 `ui_other_6`（#25BC29）。

**Why:** 曾在献祭失败提示里误传 `1`，导致失败提示显示成绿色成功图标。

**How to apply:** 调用 `ToastHintText` 时，正向/成功反馈必须显式传 `1`，负向/失败反馈传 `0`（或省略走默认）。每次写 Toast 都核对这个 state 传值。相关系统见 [[feedback_audio_use_enum]] 同理——魔法数字调用要对照语义。
