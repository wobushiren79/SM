/// <summary>
/// 项目配置信息（游戏层）：框架层读取的项目级常量统一在此定义。
/// </summary>
public class ProjectConfigInfo
{
    //日志总开关：false 时 LogUtil 全级别静默（含 LogError），排障插桩前先确认此处
    public static bool IS_OPEN_LOG_MSG = true;

    //SQLite 数据库文件名（位于 StreamingAssets/SQLiteDataBase/ 下，SQliteInit 初始化与 BaseMVCService 读写均用此名）
    public readonly static string DATA_BASE_INFO_NAME = "ScreenMiner.db";

    //Steam AppID（字符串形式，Steam 集成处经 uint.Parse 使用；480=Spacewar 官方测试 ID，上线前替换）
    public readonly static string STEAM_APP_ID = "480";

    //Steam Web API 密钥（SteamWebImpl 请求参数 key；申请后替换）
    public readonly static string STEAM_KEY_ALL = "";
}
