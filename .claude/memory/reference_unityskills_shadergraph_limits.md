---
name: reference_unityskills_shadergraph_limits
description: Unity-Skills REST 工具的 shadergraph_* API 已知限制（2.8.3 复核：节点白名单、Vector2 赋值 bug 未修、URP 模板）+ 运行模式/permission 体系
metadata:
  type: reference
---

通过 Unity-Skills REST 服务（Unity 包 `com.besty.unity-skills`，localhost:8090，`shadergraph_*` skills）操作 Shader Graph 时的已知限制。**2026-09-12 按包版本 2.8.3 逐条复核**（Unity 6000.3.11f1 / ShaderGraph 17.3，对读包源码 ShaderGraphNodeRegistry.cs / ShaderGraphReflectionHelper.cs），以下限制全部仍成立：

**节点白名单（`shadergraph_add_node` 只放行 29 个节点）**
- 用 `shadergraph_list_supported_nodes` 查全集。2.8.3 注册表 = 28 个跨版本共享 + `AppendVectorNode`（仅 Unity 6，本项目可用）。
- **不支持**（实测报 `Unsupported nodeType`）：`NoiseNode`(Simple Noise)、`GradientNoiseNode`、`VoronoiNode`、`NormalFromHeightNode`、`NormalFromTextureNode`、`TimeNode`。
- 含意：**纯程序化噪声法线、时间驱动的流动动画无法通过工具构建**，只能在 Shader Graph 编辑器里手动补，或（绕过工具规则）手写 .shadergraph JSON。
- 可用的关键节点：Property/Boolean/Color/Vector1-4、SampleTexture2D、SamplerState、UV、TilingAndOffset、Split/Combine/AppendVector、Add/Subtract/Multiply/Divide/Lerp/OneMinus/Saturate/Clamp/Remap/Branch、NormalUnpack、NormalStrength、Position、NormalVector、ViewDirection。

**Vector2 属性赋值 bug（2.8.3 仍未修）**
- `shadergraph_add_property` / `update_property` 对 `Vector2` 属性设置 value 必报错 `Object of type 'UnityEngine.Vector2' cannot be converted to type 'UnityEngine.Vector4'`，任何 value 格式（{x,y} / {x,y,z,w} / 数组）都失败。
- 根因（2.8.3 源码确认）：`Vector2ShaderProperty` 继承 `AbstractShaderProperty<Vector4>`，`value` 成员是 Vector4 型；`TryAssignPropertyValue` 把 `ConvertToVector2` 的结果（Vector2）直接 SetValue 进 Vector4 成员，`ChangeType` 无 Vector2→Vector4 转换 → InvalidCast。
- 规避：Vector2 属性只能加（默认 0,0）不能设值；需要非零 Vector2 常量时改用 `Vector2Node` —— 它的 X/Y 是标量输入槽（`set_node_defaults` 用裸数字 `4.0` 可设），或 `set_node_settings` 传 `settings={value:{x,y}}` 可整体设值（节点的 `m_Value` 是 Vector2 型，此路径正常）。

**值格式约定**
- `set_node_defaults` 标量(Vector1)槽：value 传**裸数字**（`4.0`），传 `{x:4}` 报 cast 错（2.8.3 报错文案已自带各槽格式说明）。
- `add_property` Color：value=`{r,g,b,a}`；Vector1：裸数字。Vector2/3/4/Color 类槽可传 {x,y,z,w}/{r,g,b,a} 对象、JSON 数组或逗号分隔字符串。
- PropertyNode 须先 `add_property` 再 `add_node nodeType=PropertyNode settings={propertyReferenceName:"_Xxx"}`。

**模板**
- `shadergraph_create_graph templateName="0_Lit Basic"`（Cross Pipeline）产出含 HDTarget+UniversalTarget 的 Lit 图，但会带一整套示例 PBR 贴图网络（27 节点）；干净重建需先 `remove_node`/`remove_property` 清掉非 BlockNode 节点和模板属性，保留 SurfaceDescription.*/VertexDescription.* 主输出块。

**运行模式体系（approval/auto/bypass，影响 remove_* 可用性，模板清理流程必读）**
- 服务端三档运行模式（Unity 面板切换，EditorPrefs `UnitySkills_OperatingMode` 按机存）：Approval=变更类(FullAuto)技能需先授权；Auto=直接执行仅禁 Delete 类（**新装默认**）；Bypass=全放行（**老安装默认、行为不变**）。本机为老安装 → Bypass，现有直连调用不受影响。
- **Delete 类技能（`shadergraph_remove_node`/`remove_property`/`remove_keyword`，SkillOperation.Delete）在 Approval/Auto 下被自动禁用**——上文模板清理流程依赖 remove_node/remove_property，若面板被切到 Approval 或换新机器（Auto 默认），该流程会报 MODE_FORBIDDEN；解法：切回 Bypass，或 `POST /permission/allowlist/add` 加白名单。
- Approval 流程：变更调用返回 `MODE_RESTRICTED` + grant token → 征得用户同意后 `POST /permission/grant {skill, token}` 一步执行（面板未开 PanelApprovalRequired 时 AI 直调即可）。
- 另有技能面裁剪（surface profile：full/guide/noSceneAuthoring，默认 full 不隐藏）；被裁技能报 SURFACE_EXCLUDED，默认配置下 shadergraph 模块不受影响。

**端点与调用（2.8.3）**
- 调用格式不变：`POST http://localhost:8090/skill/<name>`（UTF-8 JSON）；端口默认 8090（Auto 端口时扫 8090-8100）。
- 元信息端点：`GET /health`、`GET /skills`、`GET /skills/schema`（**精确签名以此为准**）、`GET /skills/recommend?includeSchema=true`、`GET /skills/chain`、`GET /skills/meta`、`POST /skills/batch`（批量）。
- 权限端点：`GET /permission/status|audit|allowlist`、`POST /permission/grant|approve|deny|revoke|allowlist/add|allowlist/remove`。
- shadergraph 模块全量技能（2.8.3）：list_templates / create_graph / create_subgraph / list_assets / get_info / get_structure / list_supported_nodes / add_node / remove_node / move_node / connect_nodes / disconnect_nodes / set_node_defaults / set_node_settings / list_properties / add_property / update_property / remove_property / list_keywords / add_keyword / update_keyword / remove_keyword / reimport。查询类为 SemiAuto 三模式全放行；变更类为 FullAuto。
- **环境**：系统无 Python，调用工具用 PowerShell `Invoke-RestMethod` 直连即可。

成果案例：[[../../Assets/Out/WaterSurface.shadergraph]] 即用此工具构建的 URP Lit 水面图（外部法线贴图 + Lerp 深浅水色）。Unity MCP 侧仍无 Shader Graph 节点编辑，见 [[reference_unity_mcp_tool_bug]]。
