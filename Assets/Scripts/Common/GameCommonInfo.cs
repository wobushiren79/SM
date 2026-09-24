/// <summary>
/// 游戏公共运行数据（游戏层）：跨场景/全局共享的运行态数据统一挂在这里。
/// </summary>
public class GameCommonInfo
{
    //场景切换数据（SceneUtil.SceneChange 写入换场前场景与目标场景，目标场景启动时读取）
    public static ScenesChangeBean ScenesChangeData = new ScenesChangeBean();
}
