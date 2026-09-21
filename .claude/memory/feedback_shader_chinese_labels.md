---
name: feedback-shader-chinese-labels
description: shader 的 Properties 参数显示名必须用中文；Header 标题只能 ASCII；Inspector 尽量像 PaletteFX_Project 那样分板块可折叠
metadata:
  type: feedback
---

编写/修改任何 `.shader` 文件时，`Properties` 块里每个参数的**显示名**（即 `("...")` 引号内的字符串）必须用**中文**说明该参数是干啥的，最好附带简短作用提示，例如：

```
_SwayStrength ("摆动幅度 (左右摇摆大小)", Range(0, 1)) = 0.08
```

**Why:** 用户（美术/策划会调材质）要在 Material Inspector 里一眼看懂每个参数的作用，中文标注降低理解成本。

**How to apply:**
- 参数显示名 `("...")` 是字符串字面量，写中文完全合法，Inspector 正常显示——所有参数都要写中文。
- **但 `[Header(...)]` 分组标题括号内是标识符，不是字符串，只能用 ASCII（英文/无空格），写中文会导致 ShaderLab 解析报错** `syntax error, unexpected $undefined, expecting TVAL_ID`。所以分组标题保持英文，靠各参数的中文显示名表达含义。
- **同理 `[Enum(名, 值, …)]` 里未加引号的枚举选项标签也是标识符，只能 ASCII**，写中文（如 `[Enum(正向,1,反向,-1)]`）会报同样的 `unexpected $undefined, expecting TVAL_ID`。枚举选项用英文（`[Enum(Forward,0,Reverse,1)]`），把中文解释放到该属性的引号显示名里（如 `("旋转方向 (0=正向 / 1=反向)")`）。另外 Enum 的值尽量用非负整数，个别解析器对负值（`-1`）不友好——需要 ±1 语义时用 0/1 枚举、在着色器里 `1-2*x` 换算。
- 委派给 Agent/Skill 写 shader 时，须在 prompt 中转达这条规则。

## Inspector 分板块可折叠（尽量对齐 PaletteFX_Project）

参数较多的 shader，Inspector **尽量按功能分板块、每块可折叠**，参照 `Assets/FrameWork/Shader/Effect/PaletteFX/PaletteFXShader_Project/PaletteFX_Project.shader` 的呈现风格（主贴图/遮罩/附加图/溶解/扭曲/菲涅尔/顶点动画/全局控制… 每组一个可折叠面板），比一长条平铺参数更美观、更好找。

**Why:** 平铺几十个参数时美术要滚半天才找到目标；分组折叠后按需展开，一眼定位，观感也整洁。

**How to apply（按成本从轻到重，够用即可，"尽量"非强制）：**
- **参数少（十来个以内）**：直接用 `[Header(GroupName)]` 分组（标题仍须 ASCII，见上）+ 中文显示名即可，不必上折叠。
- **参数多、想要真折叠**：走 **`CustomEditor "<自定义 ShaderGUI 类名>"`** 路线——PaletteFX_Project 即末尾挂 `CustomEditor "PaletteFXShaderGUI_Project"`（继承 `TabShaderGUI_Project`，见 `Assets/FrameWork/Shader/Effect/PaletteFX/Editor/`），用页签/折叠面板组织参数。新 shader 要真折叠时优先**复用/继承这套已有的 TabShaderGUI 基类**，不要每个 shader 各写一套 GUI。
- 无论哪种方式，**分组边界按"功能/效果开关"划分**（一个 `[Toggle(_XXX_ON)]` 效果开关领起一组），与 shader_feature 变体一一对应，逻辑清晰。
- 委派给 Agent/Skill 写 shader 时，连同上面中文标注规则一并转达这条分板块折叠偏好。
