/// <summary>
/// 场景枚举：成员名必须与场景文件名完全一致（SceneUtil 通过 GetEnumName / GetEnum 与场景名互转）。
/// 新增场景时在此追加同名成员，只能往末尾追加，不要改动已有值。
/// </summary>
public enum ScenesEnum
{
    SampleScene = 0,//示例场景
    LoadingScene = 1,//预加载过渡场景（SceneUtil.SceneChange 在 hasLoadingScene=true 时固定先加载该场景，框架硬引用此成员）
}

/// <summary>
/// Toast 提示类型：成员名对应 Resources 下 Toast 预制体（UI/Toast/UIToast{成员名}.prefab，UIManager.GetToastModel 按名加载）。
/// 新增 Toast 样式时在此追加成员并放置同名预制体。
/// </summary>
public enum ToastEnum
{
    Normal = 0,//普通提示（UIHandler.ToastHintText 系列默认使用）
}

/// <summary>
/// Dialog 弹窗类型：成员名对应 Resources 下 Dialog 预制体（UI/Dialog/UIDialog{成员名}.prefab，UIManager.GetDialogModel 按名加载）。
/// 新增弹窗时在此追加成员并放置同名预制体。
/// </summary>
public enum DialogEnum
{
}

/// <summary>
/// Popup 气泡类型：成员名对应 Resources 下 Popup 预制体（UI/Popup/UIPopup{成员名}.prefab，UIManager.GetPopupModel 按名加载）。
/// 新增气泡时在此追加成员并放置同名预制体。
/// </summary>
public enum PopupEnum
{
}

/// <summary>
/// AI 意图类型：游戏层 AI 实体在 InitIntentEnum 中声明实体持有的意图列表；
/// AIBaseEntity 优先经 RegisterIntentFactory 注册的工厂创建意图实例，兜底按 "AIIntent{枚举名}" 类名反射创建。
/// 新增意图时在此追加成员并配套注册工厂或提供同名意图类。
/// </summary>
public enum AIIntentEnum
{
}
