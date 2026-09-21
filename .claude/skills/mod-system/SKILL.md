---
name: mod-system
description: ScreenMiner 的 Mod 系统开发指南。使用此SKILL当需要创建或修改Mod加载、Mod资源管理、ModID映射、Mod配置覆盖等，包括Mod目录结构、Catalog加载、资源异步/同步加载、JsonText扩展等。
watched_files:
  - Assets/FrameWork/Scripts/Component/Manager/ModManager.cs
  - Assets/FrameWork/Scripts/Component/Handler/ModHandler.cs
  - Assets/FrameWork/Scripts/Bean/ModIdMapBean.cs
  - Assets/FrameWork/Scripts/Component/Manager/GameDataManager.cs
---

# Mod系统开发指南

## 核心概念

### Mod数据结构

```
ModManager          - Mod管理器（资源加载、缓存、卸载）
ModHandler          - Mod处理器（逻辑接口层）
ModIdMapBean        - ModID映射数据（modName -> modId）
```

### Mod系统架构

```
Mods/                          - Mod根目录（与Assets同级）
├── MyMod/                     - 示例Mod目录
│   ├── catalog.bin            - Addressables Content Catalog
│   ├── catalog.hash           - Catalog哈希
│   ├── *.bundle               - 资源Bundle文件
│   ├── settings.json          - Mod设置
│   └── JsonText/              - 可选：配置覆盖文件夹
│       └── *.txt              - 覆盖游戏的Json配置
```

### ModID映射体系

```
ModIdMapBean                      - Mod名称到modId的映射
├── modIdMap (Dictionary<string, int>)
ModIdMapService                   - 数据持久化服务 (BaseDataService<ModIdMapBean>)
```

每个已加载的Mod会被分配一个唯一的 `modId`（1~9999），用于：
- 区分不同Mod的资源，避免ID冲突
- Mod新增时不会导致旧Mod的ID变化（持久化存储在 `ModIdMap.json`）

## Mod目录结构

### 创建新Mod

```
Mods/YourModName/
├── catalog.bin            - 必需：Addressables生成的Catalog文件
├── *.bundle               - 必需：资源Bundle文件
└── JsonText/              - 可选：配置覆盖目录
    └── XxxInfo.txt        - 示例：覆盖某张配置表
```

### Mod根目录路径

```csharp
// 编辑器与打包后路径一致：与 Assets / GameName_Data 同级的 Mods 目录
string modsRoot = Path.Combine(Application.dataPath, "..", "Mods");
```

## 初始化与加载Mod

### 初始化所有Mod

```csharp
// 方式1：异步回调
ModHandler.Instance.InitializeAllMods((success) =>
{
    LogUtil.Log($"Mod初始化结果: {success}");
});

// 方式2：异步await
bool success = await ModHandler.Instance.InitializeAllModsAsync();

// 方式3：同步（仅在必要时使用）
bool success = ModHandler.Instance.InitializeAllModsSync();
```

### 加载单个Mod Catalog

```csharp
// 异步回调
ModHandler.Instance.LoadModCatalog("MyMod", (success) =>
{
    if (success)
        LogUtil.Log("Mod加载成功");
});

// 异步await
bool success = await ModHandler.Instance.LoadModCatalogAsync("MyMod");

// 同步
bool success = ModHandler.Instance.LoadModCatalogSync("MyMod");
```

## 加载Mod资源

### 同步加载单个资源

```csharp
// 加载Spine动画数据
SkeletonDataAsset skeletonData = ModHandler.Instance.LoadAssetSync<SkeletonDataAsset>(
    "MyMod", 
    "character_skeletondata"
);
```

### 异步加载单个资源

```csharp
// 方式1：回调
ModHandler.Instance.LoadAsset<Sprite>("MyMod", "icon_character", (sprite) =>
{
    if (sprite != null)
        image.sprite = sprite;
});

// 方式2：await
Sprite sprite = await ModHandler.Instance.LoadAssetAsync<Sprite>("MyMod", "icon_character");
```

### 批量加载资源（通过Label）

```csharp
ModHandler.Instance.LoadAssets<GameObject>("MyMod", "characters", (assets) =>
{
    foreach (var asset in assets)
    {
        LogUtil.Log($"加载资源: {asset.name}");
    }
});
```

## 卸载与释放

### 卸载单个Mod

```csharp
// 卸载Mod的所有资源和Catalog
ModHandler.Instance.UnloadMod("MyMod");
```

### 卸载所有Mod

```csharp
ModHandler.Instance.UnloadAllMods();
```

### 释放单个资源

```csharp
// 释放指定Mod的单个资源（从缓存中移除并释放句柄）
ModHandler.Instance.ReleaseAsset("MyMod", "icon_character");
```

### 释放批量资源

```csharp
// 释放通过Label加载的批量资源
ModHandler.Instance.ReleaseAssets("MyMod", "characters");
```

## 查询Mod信息

### 检查Mod状态

```csharp
// 检查Mod是否已加载
bool loaded = ModHandler.Instance.IsModLoaded("MyMod");

// 获取所有已加载的Mod名称
List<string> loadedMods = ModHandler.Instance.GetLoadedModNames();

// 获取所有可用的Mod名称（存在catalog.bin的目录）
List<string> availableMods = ModHandler.Instance.GetAvailableModNames();
```

### 资源归属查询

```csharp
// 判断指定assetKey是否属于某个已加载的Mod
bool isModAsset = ModHandler.Instance.IsModAsset("character_skeletondata");

// 获取包含指定assetKey的Mod名称
string modName = ModHandler.Instance.GetModNameForAsset("character_skeletondata");
```

### 获取ModID

```csharp
// 获取指定Mod的modId（1~9999），未分配则返回1
int modId = ModManager.Instance.GetModId("MyMod");
```

### 获取Mod目录路径

```csharp
string modPath = ModHandler.Instance.GetModPath("MyMod");
// 返回: .../Mods/MyMod
```

## JsonText配置覆盖

Mod可以通过 `JsonText` 目录覆盖游戏的配置数据。

### 文件结构

```
Mods/YourModName/JsonText/
├── XxxInfo.txt            - 覆盖对应名称的配置表
└── ...
```

### 查询JsonText文件

```csharp
// 检查是否有Mod包含指定名称的JsonText文件
bool hasFile = ModManager.Instance.HasModJsonTextFile("XxxInfo");

// 获取包含指定fileName的所有Mod信息
var fileInfos = ModManager.Instance.GetModJsonTextFileInfos("XxxInfo");
foreach (var (modId, modName, filePath) in fileInfos)
{
    LogUtil.Log($"Mod[{modName}] ID={modId} 路径={filePath}");
}
```

## ModID映射持久化

### 获取/保存ModID映射

```csharp
// 通过GameDataManager获取ModID映射
ModIdMapBean modIdMap = GameDataHandler.Instance.manager.GetModIdMap();

// 遍历所有已记录的ModID
foreach (var kvp in modIdMap.modIdMap)
{
    LogUtil.Log($"Mod: {kvp.Key} -> ID: {kvp.Value}");
}

// 保存ModID映射（通常由系统自动管理）
GameDataHandler.Instance.manager.SaveModIdMap();
```

### ModID分配规则

1. ModID按Mod名称字母顺序分配
2. 已分配ID的Mod持久化存储，跨会话保持不变
3. 新增Mod分配第一个空闲ID（从1开始递增）
4. 卸载Mod不会删除其ID映射，保证重新加载时ID不变

## 常用代码模板

### 在UI中显示Mod资源图片

```csharp
ModHandler.Instance.LoadAsset<Sprite>(modName, assetKey, (sprite) =>
{
    if (sprite != null)
    {
        imgIcon.sprite = sprite;
        imgIcon.SetNativeSize();
    }
});
```

### 加载Mod Spine动画

```csharp
SkeletonDataAsset skeletonData = ModHandler.Instance.LoadAssetSync<SkeletonDataAsset>(
    modName, 
    $"{characterName}_skeletondata"
);

if (skeletonData != null)
{
    skeletonGraphic.skeletonDataAsset = skeletonData;
    skeletonGraphic.Initialize(true);
}
```

### 安全加载Mod资源（带fallback）

```csharp
public Sprite GetIcon(string modName, string assetKey)
{
    if (ModHandler.Instance.IsModLoaded(modName))
    {
        var sprite = ModHandler.Instance.LoadAssetSync<Sprite>(modName, assetKey);
        if (sprite != null)
            return sprite;
    }
    // Fallback到游戏内置资源
    return LoadInternalIcon(assetKey);
}
```

### 初始化时加载所有Mod并执行后续操作

```csharp
public void StartGameWithMods()
{
    ModHandler.Instance.InitializeAllMods((success) =>
    {
        if (success)
        {
            var loadedMods = ModHandler.Instance.GetLoadedModNames();
            LogUtil.Log($"已加载 {loadedMods.Count} 个Mod");
            
            // 继续初始化游戏...
            InitGameData();
        }
    });
}
```

## 文件位置速查

| 功能 | 文件路径 |
|------|----------|
| Mod管理器 | `Assets/FrameWork/Scripts/Component/Manager/ModManager.cs` |
| Mod处理器 | `Assets/FrameWork/Scripts/Component/Handler/ModHandler.cs` |
| ModID映射Bean | `Assets/FrameWork/Scripts/Bean/ModIdMapBean.cs` |
| ModID映射服务 | `Assets/FrameWork/Scripts/Component/Manager/GameDataManager.cs` (内联使用 BaseDataService<ModIdMapBean>) |
| 游戏数据管理器 | `Assets/FrameWork/Scripts/Component/Manager/GameDataManager.cs` |
| Mod根目录 | `项目根目录/Mods/` |
