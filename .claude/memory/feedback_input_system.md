---
name: feedback-input-system
description: 输入处理必须走 InputActionUIEnum，禁止使用旧版 Input API
metadata:
  type: feedback
---

游戏内所有键盘/手柄等输入处理一律走 **InputActionUIEnum + Unity InputSystem** 体系，**禁止使用旧版 `Input` API**（`Input.GetKeyDown`、`Input.GetKey`、`Input.GetMouseButton`、`Input.GetAxis` 等）。

**Why:** 项目已统一到 Unity InputSystem（`GameInputActions.inputactions`），通过 `InputManager.dicInputUI` 把动作映射到 `InputActionUIEnum`，并由 `BaseUIInit.OnInputActionForStarted` 统一派发。混用旧 `Input` 轮询会绕过门禁（`CanInputActionStarted`/弹窗拦截）、难以重绑定，且与新体系不一致。

**How to apply:**
- UI 类（`BaseUIInit`/`BaseUIView`/`BaseUIComponent`）重写 `OnInputActionForStarted(InputActionUIEnum inputType, InputAction.CallbackContext callback)` 响应输入，**不要**在 `Update()` 里轮询 `Input`。
- 数字键已封装为 `InputActionUIEnum.N1~N9`（同时绑定主键盘与小键盘），`N1~N9` 连续可用 `inputType - InputActionUIEnum.N1 + 1` 取序号。
- 新按键：先在 `GameInputActions.inputactions` 配绑定 + `InputActionUIEnum` 补枚举，再走回调派发。
- 已落地示例：战斗卡片 1-9 快捷选择由 `UIFightMain.OnInputActionForStarted` 接 N1~N9，派发到 `UIViewCreatureCardItemForFight.HandleForPressKeySelect()`（再次按同键取消选中）。

详见 CLAUDE.md「输入处理规则」。相关：[[feedback-code-style]]
