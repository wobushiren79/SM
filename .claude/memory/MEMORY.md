# Project Memory

## Project: ScreenMiner (Unity C#)

### Key Architecture
- 框架层（Assets/FrameWork/，git 子模块 UnityFrameWork）+ 游戏逻辑层（Assets/Scripts/）
- Handler-Manager 配对模式：Handler=单例逻辑，Manager=MonoBehaviour 资源
- 全局事件系统：EventHandler 单例 + BaseEvent 实例事件

### PixelLab
- [`feedback_pixellab_require_consent.md`](feedback_pixellab_require_consent.md) — 调用 PixelLab 生成前必须征得用户明确同意（付费服务），禁止其他任务中"顺带"自行生成图片
- [`feedback_pixellab_animation_output.md`](feedback_pixellab_animation_output.md) — 帧动画只保留合成精灵表，不保留单帧文件
- [`feedback_pixellab_auto_download.md`](feedback_pixellab_auto_download.md) — 生成完成后必须自动下载到 Assets/Out/<子目录>/，不能只给链接

### Reference
- [reference_logutil_gated.md](reference_logutil_gated.md) — LogUtil 所有级别输出（含 LogError）受 ProjectConfigInfo.IS_OPEN_LOG_MSG 总开关门控，关闭时插桩日志全静默；排障插桩前先确认开关，日志缺失≠代码没跑
- [reference_unity6000_maintoolbar_element.md](reference_unity6000_maintoolbar_element.md) — Unity 6000.3 主工具栏 MainToolbarElement 默认 displayed=False 不可见（Overlay 体系）；查真状态反射 MainToolbarWindow.instance.overlayCanvas.overlays
- [reference_unityskills_shadergraph_limits.md](reference_unityskills_shadergraph_limits.md) — Unity-Skills shadergraph 工具限制：节点白名单、Vector2 赋值 bug、approval/auto/bypass 运行模式
- [reference_language_excel_source.md](reference_language_excel_source.md) — 多语言 Language_*.txt 的真实源是 excel_language 同名工作表，改文本必须改该 Excel 否则导出被覆盖；GetTextReplace 占位符模板
- [reference_unity_mcp_tool_bug.md](reference_unity_mcp_tool_bug.md) — Unity MCP 使用要点：Mcp-Session-Id 须原样回传；多实例须 set_active_instance；manage_material set_material_color 对 HDR 色用 execute_code SetColor+SetDirty+SaveAssets；无 Shader Graph 节点编辑
- [reference_unity_editor_self_run_delete_trick.md](reference_unity_editor_self_run_delete_trick.md) — 无人值守建/改 Unity 资源：临时编辑器脚本 [DidReloadScripts] 搭编译便车自动执行 + 幂等守卫 + AssetDatabase.DeleteAsset 自删；MCP 不可用时优先用
- [reference_unity_mcp_execute_code_encoding.md](reference_unity_mcp_execute_code_encoding.md) — MCP execute_code 中文路径乱码根因=PS5.1 双引号剥离+Invoke-WebRequest 按 ISO-8859-1 发 body（用 invoke-unity-mcp.ps1 -BodyBase64）
- [reference_unity_mcp_execute_code_assets.md](reference_unity_mcp_execute_code_assets.md) — execute_code 建资源踩坑：CodeDom(C#6) 不能 C#7+；中文字面量会被破坏→路径用通配符枚举；校验编译=反射 Assembly-CSharp.GetType；无人值守时 AssetDatabase 写会死锁主线程
- [reference_unity_search_index_crash.md](reference_unity_search_index_crash.md) — Unity 编辑器莫名崩溃排查：堆栈含 mdb_cursor_*/LMDBIndexStorage = Library/Search 搜索索引损坏，关编辑器删该目录重建
- [reference_ui_gradient_atlas_uv.md](reference_ui_gradient_atlas_uv.md) — UI 渐变不能用 sprite 贴图 UV（图集压缩+9宫格切段致混色）；FrameWork/UI/Shader_UI_ImageGradient 读 UV1 + UIGradientMeshUV
- [reference_fog_stripping_pc_build.md](reference_fog_stripping_pc_build.md) — PC 打包后雾消失根因：代码运行时开雾但 GraphicsSettings 雾剥离=Automatic 只扫 Build Settings 场景→FOG 变体被剥离；修法 m_FogStripping=Custom 全保留；「编辑器有包体没有」先查变体剥离
- [feedback_git_checkout_confirm_scope.md](feedback_git_checkout_confirm_scope.md) — git checkout/restore 前必须列文件清单经用户逐个确认；未提交内容 git 无法恢复；用户说"还原"先问清对象

### Collaboration Feedback
- [`feedback_play_verify_manual.md`](feedback_play_verify_manual.md) — Unity Play 模式验证一律由用户手动 Play + 截图反馈，禁止 MCP 自动启动/停止 Play 自行验证
- [`feedback_task_summary.md`](feedback_task_summary.md) — 任务总结必须列出参与的 Agent/Skill 名称及操作
- [`feedback_bean_partial.md`](feedback_bean_partial.md) — 文件可改性只看文件头有无 AUTO-GENERATED-DO-NOT-EDIT 标记：有则写 Partial，无则可直接改
- [`feedback_code_style.md`](feedback_code_style.md) — 方法/属性必须加 XML 注释并用 #region 分类；方法体内注释尽量单行
- [`feedback_comment_sync.md`](feedback_comment_sync.md) — 修改代码逻辑时必须同步更新对应的 XML 注释
- [`feedback_excel_id_sorted_insert.md`](feedback_excel_id_sorted_insert.md) — 新增配置表数据行必须按 id 升序插入，禁止 append 追加末尾（用 excel_add_row.py）
- [`feedback_input_system.md`](feedback_input_system.md) — 输入处理必须走 InputActionUIEnum，禁止使用旧版 Input API
- [`feedback_agent_skill_sync.md`](feedback_agent_skill_sync.md) — 改了被 watched_files 命中的代码必须同步 agent/skill 文档；PS 脚本必须 UTF-8 BOM
- [`feedback_inline_python_no_temp.md`](feedback_inline_python_no_temp.md) — 一次性 Python 优先用 run-python.ps1 -c 内联，别建临时 .py
- [`feedback_ask_before_architecture_change.md`](feedback_ask_before_architecture_change.md) — 涉及改变原有架构/数据流向的修改必须先询问用户确认
- [`feedback_shader_chinese_labels.md`](feedback_shader_chinese_labels.md) — shader Properties 参数显示名必须中文、Header 标题只能 ASCII；Inspector 按功能分板块可折叠
- [`feedback_prefer_language_property.md`](feedback_prefer_language_property.md) — 取多语言文本优先用框架自动生成的 _language 属性（带缓存），不手写 GetTextById
- [`feedback_text_replace_enum.md`](feedback_text_replace_enum.md) — 文本含动态数值一律用 TextReplaceEnum 占位符 + GetTextReplace 机制，禁止 string.Format 特判或数值写死
- [`feedback_audio_use_enum.md`](feedback_audio_use_enum.md) — 音频播放统一用 AudioEnum 枚举调用，禁止裸 id；音频 id 全面 long 化；新增音频须同步维护枚举
- [`feedback_toasthint_state.md`](feedback_toasthint_state.md) — UIHandler.ToastHintText(content, state) state：0=失败(红)、1=成功(绿)，默认0；正向反馈必传1
