/// <summary>
/// 资源路径常量（游戏层）：游戏专属 Addressables 地址在此 partial 扩展框架层 PathInfo
/// （组织方式与框架层约定的 TagInfo 一致，框架层注释指定游戏层路径放本文件）。
/// </summary>
public partial class PathInfo
{
    //全局渲染 Volume 预制体地址（VolumeManager 按需同步加载；对应预制体需加入 Addressables，尚未创建）
    public readonly static string RenderVolumePath = "Assets/FrameWork/Prefabs/Volume/RenderVolume.prefab";
}
