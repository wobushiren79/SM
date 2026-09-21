---
name: spine-system
description: ScreenMiner 的 Spine 动画系统开发指南。使用此SKILL当需要创建或修改Spine骨骼动画相关的代码，包括动画播放、皮肤切换、动画事件处理、Spine资源管理、SpineWindow工具窗口（皮肤提取 + 动画预览页签）等。
watched_files:
  - Assets/FrameWork/Scripts/Component/Manager/SpineManager.cs
  - Assets/FrameWork/Scripts/Component/Handler/SpineHandler.cs
  - Assets/FrameWork/Scripts/Bean/SpineSkinBean.cs
  - Assets/FrameWork/Scripts/Bean/MVC/SpineAnimationStateBean.cs
  - Assets/FrameWork/Scripts/Enums/BaseGameEnum.cs
  - Assets/FrameWork/Editor/Base/SpineEditor.cs
  - Assets/FrameWork/Editor/Base/Window/SpineWindow.cs
  - Assets/FrameWork/Editor/Base/Window/SpineWindowPreview.cs
---

# Spine动画系统开发指南

## 核心概念

### Spine相关类

```
SpineManager              - Spine资源管理器（加载/缓存SkeletonDataAsset）
SpineHandler              - Spine处理器（动画播放、皮肤切换等API）
SkeletonAnimation         - 3D/世界空间Spine组件
SkeletonGraphic           - UI Spine组件
SkeletonDataAsset         - Spine数据资源
SpineSkinBean             - 皮肤数据配置
SpineAnimationStateEnum   - 动画状态枚举
```

## 动画状态枚举

```csharp
public enum SpineAnimationStateEnum
{
    None = 0,
    Idle = 10001,           // 待机
    Walk = 20001,           // 行走
    Walk2, Walk3,           // 行走变体
    Attack = 30001,         // 攻击
    Attack2, Attack3,       // 攻击变体
    Attack4, Attack5, Attack6, Attack7,
    Dead = 40001,           // 死亡
    NearDead = 50001,       // 濒死
    Hit = 60001,            // 受击
    Jump = 70001,           // 跳跃
    Run = 80001,            // 奔跑
    Dizzy = 90001,          // 晕眩
}
```

## 加载Spine资源

### 预加载Spine资源

```csharp
// 预加载多个Spine资源
List<string> assetNames = new List<string>() { "Hero", "Enemy_01", "Boss_01" };
SpineHandler.Instance.PreLoadSkeletonDataAsset(assetNames, (dicData) =>
{
    // 所有资源加载完成
    LogUtil.Log("Spine资源预加载完成");
});
```

### 获取SkeletonDataAsset

```csharp
// 同步获取
SkeletonDataAsset skeletonDataAsset = SpineManager.Instance.GetSkeletonDataAssetSync("Hero");

// 异步获取
SpineManager.Instance.GetSkeletonDataAsset("Hero", (skeletonDataAsset) =>
{
    // 使用资源
});
```

## 创建Spine对象

### 3D/世界空间Spine

```csharp
// 创建SkeletonAnimation
GameObject targetObj = new GameObject("SpineCharacter");
SkeletonAnimation skeletonAnimation = SpineHandler.Instance.AddSkeletonAnimation(
    targetObj, 
    "Hero",           // assetName
    skinData          // Dictionary<string, SpineSkinBean> 可选
);
```

### UI Spine

```csharp
// 创建SkeletonGraphic
GameObject uiObj = new GameObject("UISpine");
Material material = Resources.Load<Material>("Materials/UISpine");
SkeletonGraphic skeletonGraphic = SpineHandler.Instance.AddSkeletonGraphic(
    uiObj,
    "Hero",
    skinData,         // Dictionary<string, SpineSkinBean> 可选
    material
);
```

### 动态设置Spine数据

```csharp
// 为现有SkeletonAnimation设置数据
SkeletonAnimation skeletonAnimation = GetComponent<SkeletonAnimation>();
SpineHandler.Instance.SetSkeletonDataAsset(skeletonAnimation, "Hero", isSync: true);

// 为现有SkeletonGraphic设置数据
SkeletonGraphic skeletonGraphic = GetComponent<SkeletonGraphic>();
SpineHandler.Instance.SetSkeletonDataAsset(skeletonGraphic, "Hero", isSync: true);
```

## 播放动画

### 基础播放

```csharp
// 播放待机动画（循环）
SpineHandler.Instance.PlayAnim(
    skeletonAnimation, 
    SpineAnimationStateEnum.Idle, 
    isLoop: true
);

// 播放攻击动画（不循环）
SpineHandler.Instance.PlayAnim(
    skeletonAnimation, 
    SpineAnimationStateEnum.Attack, 
    isLoop: false
);
```

### 指定动画名称播放

```csharp
// 播放特定名称的动画
SpineHandler.Instance.PlayAnim(
    skeletonAnimation,
    SpineAnimationStateEnum.Attack,
    isLoop: false,
    animNameAppoint: "attack_special"
);
```

### 设置起始时间

```csharp
// 从第0.5秒开始播放
SpineHandler.Instance.PlayAnim(
    skeletonAnimation,
    SpineAnimationStateEnum.Idle,
    isLoop: true,
    animStartTime: 0.5f
);
```

### 添加动画队列

```csharp
// 先播放攻击，然后自动切换到待机
SpineHandler.Instance.PlayAnim(skeletonAnimation, SpineAnimationStateEnum.Attack, isLoop: false);

// 添加待机动画到队列（攻击完成后播放）
SpineHandler.Instance.AddAnimation(
    skeletonAnimation,
    trackIndex: 0,
    SpineAnimationStateEnum.Idle,
    isLoop: true,
    delay: 0
);
```

### 设置混合时间

```csharp
// 播放攻击动画，设置混合过渡时间为0.2秒
TrackEntry trackEntry = SpineHandler.Instance.PlayAnim(
    skeletonAnimation,
    SpineAnimationStateEnum.Attack,
    isLoop: false,
    mixDuration: 0.2f
);
```

## 皮肤系统

### 皮肤数据结构

```csharp
// SpineSkinBean定义
public class SpineSkinBean
{
    public long skinId;           // 皮肤ID
    public bool hasColor;         // 是否自定义颜色
    public ColorBean skinColor;   // 皮肤颜色
}

// 创建皮肤数据
SpineSkinBean skin = new SpineSkinBean(skinId: 1001);
SpineSkinBean skinWithColor = new SpineSkinBean(
    skinId: 1001, 
    hasColor: true, 
    color: Color.red
);
```

### 切换皮肤

```csharp
// 构建皮肤数据字典
Dictionary<string, SpineSkinBean> skinData = new Dictionary<string, SpineSkinBean>
{
    { "head/helmet", new SpineSkinBean(1001) },
    { "body/armor", new SpineSkinBean(1002, true, Color.blue) },
    { "weapon/sword", new SpineSkinBean(1003) }
};

// 应用到Skeleton
SpineHandler.Instance.ChangeSkeletonSkin(skeletonAnimation.skeleton, skinData);
```

### 修改部位颜色

```csharp
// 修改特定slot的颜色
SpineHandler.Instance.ChangeSlotColor(
    skeletonAnimation.skeleton, 
    "helmet",           // slot名称
    Color.red
);
```

### 移除皮肤部件

```csharp
// 移除特定slot的皮肤
SpineHandler.Instance.RemoveSkeletonSkin(
    skeletonAnimation.skeleton, 
    "helmet"
);
```

### 优化皮肤（合图）

```csharp
// 将多个皮肤合并为一张纹理，优化DrawCall
Material oldMat = skeletonAnimation.GetComponent<Renderer>().material;
Texture2D oldTex = oldMat.mainTexture as Texture2D;

Material newMat;
Texture2D newTex;
SpineHandler.Instance.OptimizeSkeletonAnimationSkin(
    skeletonAnimation,
    oldMat,
    oldTex,
    out newMat,
    out newTex
);
```

## 动画事件监听

```csharp
// 获取TrackEntry并监听事件
TrackEntry trackEntry = skeletonAnimation.AnimationState.SetAnimation(0, "attack", false);

// 动画开始
trackEntry.Start += (entry) =>
{
    LogUtil.Log("动画开始");
};

// 动画结束
trackEntry.End += (entry) =>
{
    LogUtil.Log("动画结束");
};

// 动画完成
trackEntry.Complete += (entry) =>
{
    LogUtil.Log("动画完成");
};

// 动画事件（Spine中定义的事件）
trackEntry.Event += (entry, e) =>
{
    LogUtil.Log($"事件触发: {e.Data.Name}");
};
```

## 动画配置表

动画名称映射通过 `SpineAnimationStateCfg` 配置表实现：

```
SpineAnimationState表结构：
- id: 对应SpineAnimationStateEnum的值
- res: 动画名称（多个用,分隔）
- remark: 备注
```

### 动画匹配规则

```csharp
// 系统会根据配置表自动匹配动画名称
// 例如 Idle(10001) 配置为 "idle,stand"
// 会依次查找 "idle" -> "stand" -> 使用默认
```

## 常用代码模板

### 创建带皮肤的角色

```csharp
public void CreateCharacter(string assetName, Dictionary<long, long> equipData)
{
    GameObject obj = new GameObject("Character");
    
    // 构建皮肤数据
    Dictionary<string, SpineSkinBean> skinData = new Dictionary<string, SpineSkinBean>();
    foreach (var equip in equipData)
    {
        string slotName = GetSlotNameByEquipType(equip.Key);
        skinData.Add(slotName, new SpineSkinBean(equip.Value));
    }
    
    // 创建Spine
    SkeletonAnimation anim = SpineHandler.Instance.AddSkeletonAnimation(obj, assetName, skinData);
    
    // 播放待机动画
    SpineHandler.Instance.PlayAnim(anim, SpineAnimationStateEnum.Idle, isLoop: true);
}
```

### 播放攻击连招

```csharp
public void PlayAttackCombo(SkeletonAnimation skeletonAnimation, int comboIndex)
{
    SpineAnimationStateEnum[] comboAnims = new[]
    {
        SpineAnimationStateEnum.Attack,
        SpineAnimationStateEnum.Attack2,
        SpineAnimationStateEnum.Attack3
    };
    
    var animState = comboAnims[comboIndex % comboAnims.Length];
    
    // 播放攻击动画
    SpineHandler.Instance.PlayAnim(skeletonAnimation, animState, isLoop: false);
    
    // 添加待机动画到队列
    SpineHandler.Instance.AddAnimation(
        skeletonAnimation,
        0,
        SpineAnimationStateEnum.Idle,
        true,
        0
    );
}
```

### 根据状态切换动画

```csharp
// 按业务状态机分支播对应动画（状态枚举由游戏层自行定义）
switch (state)
{
    case MyStateEnum.Idle:
        SpineHandler.Instance.PlayAnim(anim, SpineAnimationStateEnum.Idle, isLoop: true);
        break;
    case MyStateEnum.Walk:
        SpineHandler.Instance.PlayAnim(anim, SpineAnimationStateEnum.Walk, isLoop: true);
        break;
    case MyStateEnum.Attack:
        SpineHandler.Instance.PlayAnim(anim, SpineAnimationStateEnum.Attack, isLoop: false);
        break;
    case MyStateEnum.Dead:
        SpineHandler.Instance.PlayAnim(anim, SpineAnimationStateEnum.Dead, isLoop: false);
        break;
}
```

### 创建UI角色展示

```csharp
public SkeletonGraphic CreateUICharacter(GameObject parent, string assetName)
{
    GameObject obj = new GameObject("UICharacter");
    obj.transform.SetParent(parent.transform);
    
    // 使用UI材质
    Material uiMaterial = Resources.Load<Material>("Materials/UISpine");
    
    // 创建SkeletonGraphic
    SkeletonGraphic graphic = SpineHandler.Instance.AddSkeletonGraphic(
        obj,
        assetName,
        null,
        uiMaterial
    );
    
    // 播放待机动画
    SpineHandler.Instance.PlayAnim(graphic, SpineAnimationStateEnum.Idle, isLoop: true);
    
    return graphic;
}
```

## SpineWindow 工具窗口（皮肤提取 + 动画预览）

菜单 `Custom/工具弹窗/Spine工具` 打开，窗口含两个页签：**皮肤提取**（原有，批量导出皮肤贴图）与**动画预览**。

### 动画预览页签解决什么问题

骨架数据版本与 spine-unity 运行时 minor 版本不一致（如数据 4.2 / 运行时 4.3）时，官方 SkeletonDataAsset Inspector 的兼容性检查（`SkeletonDataCompatibility.GetCompatibilityProblemInfo` 要求 major.minor 完全一致）会拦截 `preview.Initialize`，导致 Inspector 底部 Preview 面板空白。而运行时 `GetSkeletonData` 读取成功即直接返回（兼容检查仅在读取失败时才执行），所以游戏能跑但编辑器预览不可用。该页签绕过官方 Inspector 自行实现预览。

### 实现原理（SpineWindowPreview.cs）

- 用 `EditorInstantiation.InstantiateSkeletonAnimation` 实例化隐藏的 `SkeletonAnimation`（`HideAndDontSave` + Layer 30），并 **`previewUtility.AddSingleGO(go)` 移入预览场景**——本项目 URP 环境下 PreviewRenderUtility 相机只渲染预览场景内的物体，留在活动场景会渲染为空（已用像素回读实验证实）；`PreviewRenderUtility` 正交相机只渲染该层，`BeginPreview → camera.Render() → EndPreview` 输出纹理绘制到窗口。
- **预览物体的 MeshRenderer 必须保持 `enabled = true`**——4.3 中 `SkeletonRenderer.NeedsToGenerateMesh = meshRenderer.enabled`，renderer 禁用时 `LateUpdate()` 直接跳过网格重建，画面冻结在第一帧（症状：能显示初始姿势但动画/换皮肤都不动）。官方 Inspector 预览是"渲染前临时 enable、渲染后 disable + 在 enable 状态下 Update/LateUpdate"，不要照搬到常开渲染的自定义窗口里。
- `EditorApplication.update` 中手动 `skeletonAnimation.Update(dt)` + `Renderer.LateUpdate()` 驱动播放（编辑模式下组件自身不会走 Update）。
- 皮肤搭配：按 `/` 前缀分组（Clothes/Pants/Weapon/...），每组下拉单选（含"不显示"），`new Skin` + `AddSkin` 合成后 `SetSkin` + `SetupPose` + `Update(0)` 重摆姿势。
- 支持：动画列表播放/暂停/停止、循环开关、速度滑条、进度条拖拽定位、滚轮缩放、拖拽平移、数据版本显示、重新加载（`SkeletonDataAsset.Clear()` 强制重读）。

### 4.3 API 注意事项（写编辑器预览代码时）

- `AnimationState.GetTrack(0)` 取当前轨道（4.3 已无 `GetCurrent`）。
- `skeletonAnimation.Update(float)` 与 `ISkeletonRenderer.LateUpdate()` 是公开方法，用于手动推进。
- `Skeleton.SetupPose()` / `skeleton.UpdateWorldTransform(Spine.Physics.Update)`（旧名 `SetToSetupPose`/`Skeleton.Physics` 已废弃）。
- 编辑器脚本同时 `using Spine;` 和 `using UnityEngine;` 时，`Animation`/`Event`/`EventType` 与 UnityEngine 同名类型冲突，需写全名（`Spine.Animation`、`UnityEngine.Event`、`UnityEngine.EventType`）。

## 文件位置速查

| 功能 | 文件路径 |
|------|----------|
| Spine管理器 | `Assets/FrameWork/Scripts/Component/Manager/SpineManager.cs` |
| Spine处理器 | `Assets/FrameWork/Scripts/Component/Handler/SpineHandler.cs` |
| 皮肤数据Bean | `Assets/FrameWork/Scripts/Bean/SpineSkinBean.cs` |
| 动画状态Bean | `Assets/FrameWork/Scripts/Bean/MVC/SpineAnimationStateBean.cs` |
| 动画状态枚举 | `Assets/FrameWork/Scripts/Enums/BaseGameEnum.cs` |
| Spine编辑器工具 | `Assets/FrameWork/Editor/Base/SpineEditor.cs` |
| Spine窗口 | `Assets/FrameWork/Editor/Base/Window/SpineWindow.cs` |
| Spine窗口-动画预览页签 | `Assets/FrameWork/Editor/Base/Window/SpineWindowPreview.cs` |

## 注意事项

1. **资源加载**: 大量使用Spine时建议先调用 `PreLoadSkeletonDataAsset` 预加载资源
2. **内存管理**: 使用 `OptimizeSkeletonAnimationSkin` 可以优化皮肤内存占用
3. **Mod支持**: 系统支持从Mod加载Spine资源，会自动检测并优先加载Mod资源
4. **UI Spine**: UI中使用SkeletonGraphic，需要指定合适的Material
5. **动画混合**: 设置合适的 `mixDuration` 可以让动画过渡更平滑
