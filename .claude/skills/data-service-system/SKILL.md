---
name: data-service-system
description: ScreenMiner 的数据服务系统开发指南。使用此SKILL当需要创建或修改数据持久化、JSON读写、用户存档、配置数据管理、SQLite操作等，包括BaseDataService<T>泛型基类、UserDataService、GameConfigBean、数据存储(DataStorage)、自动备份机制等。
watched_files:
  - Assets/FrameWork/Scripts/MVC/BaseDataService.cs
  - Assets/FrameWork/Scripts/DataStorage/
  - Assets/FrameWork/Scripts/BaseSystem/Sqlite/
  - Assets/FrameWork/Scripts/Utils/JsonUtil.cs
  - Assets/FrameWork/Scripts/Utils/ExcelUtil.cs
  - Assets/FrameWork/Scripts/Component/Manager/GameDataManager.cs
  - Assets/FrameWork/Scripts/Component/Handler/GameDataHandler.cs
---

# 数据服务系统开发指南

## 核心概念

项目采用 **BaseDataService\<T\>** 泛型数据服务模式，Manager 直接操作 Service 进行数据读写，不再使用传统 MVC 的 Model/Controller/View 分层。

### 数据服务体系架构

```
GameDataManager (MonoBehaviour)
    │  资源加载、缓存管理
    │
    ├── BaseDataService<GameConfigBean>  ---> JSON 文件读写
    │   └── GameConfigBean: 游戏全局配置（语言、音量、设置等）
    │
    ├── BaseDataService<ModIdMapBean>    ---> JSON 文件读写
    │   └── ModIdMapBean: Mod 名称到 ID 的映射
    │
    └── UserDataService（游戏层）          ---> JSON 文件读写 + 自动备份
        └── UserDataBean: 用户存档

持久化方式:
    JSON (Newtonsoft.Json)  → 复杂数据结构（存档、配置）
    PlayerPrefs             → 简单键值对
    SQLite                  → 大量结构化数据
    Excel (EPPlus)          → 配置表导入导出
```

---

## BaseDataService\<T\> 泛型基类

**文件**: `Assets/FrameWork/Scripts/MVC/BaseDataService.cs`

### 核心方法

```csharp
public class BaseDataService<T> where T : class, new()
{
    protected string fileName;           // JSON 文件名（不含扩展名）
    protected string fileDirectory;      // 文件目录路径
    protected T data;                    // 数据实例

    // 初始化服务（指定文件名和目录）
    public void InitData(string fileName, string fileDirectory);

    // 获取数据
    public T GetData();

    // 设置数据
    public void SetData(T data);

    // 从 JSON 文件加载数据
    public T LoadData();

    // 保存数据到 JSON 文件
    public void SaveData();

    // 保存数据（异步）
    public async Task SaveDataAsync();

    // 检查数据文件是否存在
    public bool HasDataFile();
}
```

### 创建新的数据服务

```csharp
// 1. 定义数据 Bean
[Serializable]
public class MyFeatureDataBean
{
    public int version = 1;
    public Dictionary<string, int> settings = new Dictionary<string, int>();
    public List<string> records = new List<string>();
}

// 2. 创建数据服务
public class MyFeatureDataService : BaseDataService<MyFeatureDataBean>
{
    public MyFeatureDataService()
    {
        InitData("MyFeatureData", Application.persistentDataPath);
    }

    // 自定义业务方法
    public void AddRecord(string record)
    {
        var data = GetData();
        data.records.Add(record);
        SaveData();
    }
}
```

// 3. 在 Manager 中使用
```csharp
public class MyFeatureManager : BaseManager
{
    private MyFeatureDataService dataService;

    public override void Awake()
    {
        base.Awake();
        dataService = new MyFeatureDataService();
    }

    public MyFeatureDataBean GetFeatureData()
    {
        return dataService.GetData();
    }
}
```

---

## UserDataService（游戏层存档服务）

**文件约定**: `Assets/Scripts/MVC/Service/UserDataService.cs`（游戏层，继承 `BaseDataService<UserDataBean>`）

### 核心特性

- 继承 `BaseDataService<UserDataBean>`
- 自动备份机制：保存时自动创建备份文件
- 存档损坏时自动恢复

### 存档备份机制

```csharp
// UserDataService 自动处理
// 保存流程:
// 1. 将当前数据写入 UserData.json
// 2. 复制上一份到 UserData_backup.json
// 3. 如果写入失败，尝试从备份恢复
```

### 拆分存档约定（大数据量模块独立文件）

数据量大的模块（解锁/成就/背包等）从 `UserData_{slot}` 主存档**拆分为同槽目录下的独立文件**，避免主存档膨胀：

```
{persistentDataPath}/UserData_{slot}/
├── UserData_{slot}                 # 主存档(含备份 _Backups_0/1/2)
└── UserXxx_{slot}                  # 各拆分档(独立, 对应 UserXxxBean)
```

- 拆分字段在 `UserDataBean` 上为包裹型 Bean 字段并标注 `[Newtonsoft.Json.JsonIgnore]`，**不随主存档序列化**；统一用懒初始化取数器访问（`GetUserXxxData()`）。
- **拆分读写封装在 `UserDataService` 内部**（不另建子类服务）：`Save` 存完主存档后用即建的 `BaseDataService<T>` 实例写独立文件；`Load` 读主存档后注入拆分数据；`Delete` 一并删除。`GameDataManager` 只调 `userDataService.Save/Load/Delete`，对拆分无感知。
- 关键技巧：`BaseDataService<T>` 是可实例化的具体类（约束 `where T : class, new()`），`StoragePath` public、`FileName` 由构造函数传入，故用 `new BaseDataService<T>(fileName){ StoragePath = ... }` 即可复用泛型读写，无需为每个类型建子类。
- 独立文件**无备份**：备份回滚只还原主存档，不联动拆分文件。
- 聚合根编排：与货币/阵容等耦合的增删方法仍放 `UserDataBean` 上（内部操作容器 Bean 的列表），容器 Bean 仅作纯数据存储。

---

## GameConfigBean - 游戏配置

```csharp
public class GameConfigBean
{
    public LanguageEnum language;         // 当前语言
    public float musicVolume;             // 音乐音量 (0-1)
    public float sfxVolume;               // 音效音量 (0-1)
    public bool isFullscreen;             // 是否全屏
    public int resolutionIndex;           // 分辨率索引
    // ... 其他全局配置
}

// 使用
GameConfigBean config = GameDataHandler.Instance.manager.GetGameConfig();
config.language = LanguageEnum.cn;
config.musicVolume = 0.8f;
GameDataHandler.Instance.manager.SaveGameConfig();
```

---

## JSON 工具类 (JsonUtil)

**文件**: `Assets/FrameWork/Scripts/Utils/JsonUtil.cs`

```csharp
// 序列化
string json = JsonUtil.ToJson(myObject);

// 反序列化
MyClass obj = JsonUtil.FromJson<MyClass>(jsonString);

// 从文件读取
MyClass data = JsonUtil.LoadFromFile<MyClass>(filePath);

// 保存到文件
JsonUtil.SaveToFile(filePath, myObject);

// 使用 Unity 的 Newtonsoft.Json 序列化器
UnityNewtonsoftJsonSerializer.Serialize(obj);
UnityNewtonsoftJsonSerializer.Deserialize<T>(json);
```

---

## SQLite 操作

**文件**: `Assets/FrameWork/Scripts/BaseSystem/Sqlite/`

### SQliteHandle 核心方法

```csharp
// 初始化数据库
SQliteHandle handle = new SQliteHandle(dbPath);

// 执行查询
List<T> results = handle.Query<T>("SELECT * FROM TableName WHERE id = ?", id);

// 执行非查询
int affected = handle.Execute("INSERT INTO TableName VALUES (?, ?)", value1, value2);

// 批量操作
handle.BeginTransaction();
// ... 多次 Execute ...
handle.Commit();
```

### 使用 SQLiteHelper

```csharp
// 创建表
SQLiteHelper.CreateTable<T>(dbPath);

// 插入数据
SQLiteHelper.Insert(dbPath, myObject);

// 批量插入
SQLiteHelper.InsertAll(dbPath, listObjects);

// 更新数据
SQLiteHelper.Update(dbPath, myObject);

// 查询
List<T> items = SQLiteHelper.Query<T>(dbPath, "WHERE column = ?", value);
```

---

## Excel 配置处理 (ExcelUtil)

**文件**: `Assets/FrameWork/Scripts/Utils/ExcelUtil.cs`

### 读取 Excel 配置

```csharp
// 从 Excel 读取配置数据（Editor 环境）
var items = ExcelUtil.GetExcelDataList<ItemsInfoBean>(
    "Assets/Data/Excel/items.xlsx", 
    "ItemsInfo"
);

// 导出 Excel 数据为 JSON（使用编辑器窗口）
// 菜单: Custom/工具弹窗/Excel编辑器
```

### Excel 配置表结构

```
Assets/Data/Excel/
├── excel_xxx[中文说明].xlsx   # 业务配置表（命名约定）
└── ...
```

### 配置表字段命名规范

```
Excel列名 -> Bean字段名
- id       -> id (long)
- name     -> name (long, 文本表ID)
- remark   -> remark (string)
- ... 其他业务字段
```

---

## 常用代码模板

### 新增持久化数据模块

```csharp
// 1. 定义 Bean
[Serializable]
public class MySaveData
{
    public int version = 1;
    public long lastSaveTime;
    public List<MyRecord> records = new List<MyRecord>();
}

// 2. 创建 Service
public class MySaveDataService : BaseDataService<MySaveData>
{
    public MySaveDataService()
    {
        InitData("MySaveData", Application.persistentDataPath);
    }
}

// 3. 在 GameDataManager 中集成
private MySaveDataService mySaveDataService;

public MySaveData GetMySaveData()
{
    if (mySaveDataService == null)
        mySaveDataService = new MySaveDataService();
    return mySaveDataService.GetData();
}

public void SaveMySaveData()
{
    mySaveDataService?.SaveData();
}
```

### 使用 PlayerPrefs（简单设置）

```csharp
// 简单键值对的存储
PlayerPrefs.SetInt("TutorialComplete", 1);
PlayerPrefs.SetFloat("MusicVolume", 0.8f);

// 读取（带默认值）
int tutorialComplete = PlayerPrefs.GetInt("TutorialComplete", 0);

// 保存到磁盘
PlayerPrefs.Save();
```

---

## 文件位置速查

| 功能 | 文件路径 |
|------|----------|
| 数据服务基类 | `Assets/FrameWork/Scripts/MVC/BaseDataService.cs` |
| 用户数据服务（游戏层，含拆分存档读写） | `Assets/Scripts/MVC/Service/UserDataService.cs` |
| 游戏数据管理器 | `Assets/FrameWork/Scripts/Component/Manager/GameDataManager.cs` |
| 游戏数据处理器 | `Assets/FrameWork/Scripts/Component/Handler/GameDataHandler.cs` |
| 用户数据Bean（游戏层） | `Assets/Scripts/Bean/MVC/UserDataBean.cs` |
| 数据读取基类 | `Assets/FrameWork/Scripts/DataStorage/BaseDataRead.cs` |
| 数据存储基类 | `Assets/FrameWork/Scripts/DataStorage/BaseDataStorage.cs` |
| JSON工具 | `Assets/FrameWork/Scripts/Utils/JsonUtil.cs` |
| Excel工具 | `Assets/FrameWork/Scripts/Utils/ExcelUtil.cs` |
| SQLite操作 | `Assets/FrameWork/Scripts/BaseSystem/Sqlite/SQliteHandle.cs` |
| SQLite辅助 | `Assets/FrameWork/Scripts/BaseSystem/Sqlite/SQLiteHelper.cs` |
| SQLite初始化 | `Assets/FrameWork/Scripts/BaseSystem/Sqlite/SQliteInit.cs` |
| Excel编辑器窗口 | `Assets/FrameWork/Editor/Base/Window/ExcelEditorWindow.cs` |
| MVC编辑器窗口 | `Assets/FrameWork/Editor/Base/Window/MVCEditorWindow.cs` |

---

## 注意事项

1. **线程安全**: JSON 文件读写使用了 `async/await` 支持异步操作，非主线程读写时注意线程安全。
2. **自动备份**: UserDataService 自动维护备份文件，但极端情况（磁盘满、权限不足）会导致保存失败。
3. **数据版本**: Bean 中的 `version` 字段可用于数据迁移，升级时处理旧格式兼容。
4. **文件路径**: 编辑器环境使用 Application.dataPath 同级目录，打包后使用 Application.persistentDataPath。
5. **序列化**: 使用 Newtonsoft.Json 而非 Unity 内置 JsonUtility，支持更丰富的序列化特性（字典、私有字段等）。
