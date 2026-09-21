---
name: audio-system
description: ScreenMiner 的音频(Audio)系统开发指南。使用此SKILL当需要创建或修改音效播放、背景音乐(单曲/列表循环)、环境音、音量管理、按钮点击音效、音频资源加载缓存、音频配置表(excel_audio_info/AudioInfo)等，包括 AudioHandler/AudioManager(框架层+游戏层 partial 配对)、PlaySound/PlayMusicForLoop/PlayMusicListForLoop/PlayEnvironment、PauseMusic/RestoreMusic/StopMusic/StopEnvironment、AudioInfoBean(audio_type 0音效/1音乐/2环境音)、AuidoTypeEnum、三条 AudioSource(Music/Sound/Environment)、GameConfigBean 音量(musicVolume/soundVolume/environmentVolume)、音量设置 UI、ButtonAudio/AudioView UI 音效组件、AddOnClickAction 通用 UI 点击音效等。
watched_files:
  - Assets/FrameWork/Scripts/Component/Handler/AudioHandler.cs
  - Assets/FrameWork/Scripts/Component/Manager/AudioManager.cs
  - Assets/FrameWork/Scripts/Bean/MVC/AudioInfoBean.cs
  - Assets/FrameWork/Scripts/Bean/MVC/AudioInfoBeanPartial.cs
  - Assets/FrameWork/Scripts/Component/UI/AudioView.cs
  - Assets/FrameWork/Scripts/Component/UI/ButtonAudio.cs
  - Assets/FrameWork/Scripts/Enums/BaseGameEnum.cs
---

# 音频系统 (Audio System) 开发指南

## 核心概念

音频逻辑通过 `BaseHandler<AudioHandler, AudioManager>` 配对模式组织，框架层与游戏层各有一个 `partial` 文件。
所有音频按 **三类** 区分，每类对应一条常驻 `AudioSource` 与一个资源缓存字典：

```
AudioHandler   - 音频逻辑处理器（对外 API，单例 AudioHandler.Instance）
AudioManager   - 音频资源管理器（持有 3 条 AudioSource、AudioListener、3 个 AudioClip 缓存字典）

三类音频（AuidoTypeEnum）：
  Sound       = 0  音效   → audioSourceForSound        （PlayOneShot / PlayClipAtPoint，瞬时）
  Music       = 1  音乐   → audioSourceForMusic        （loop，单曲或列表轮播）
  Environment = 2  环境音 → audioSourceForEnvironment  （loop，常驻氛围音）
```

> `AudioListener` 每帧跟随 `Camera.main` 位置（`AudioHandler.Update`），所以 3D 定位音效（`PlayClipAtPoint`）以摄像机为听者。

> **第 4 类能力：连续音效（LoopSound）**。它**不是**新的 `AuidoTypeEnum`/资源目录，而是一种**通用循环播放能力**——给任意音频 id，按其配置的 `audio_type` 走现有加载路由取 clip，在**池化的循环 AudioSource**（`Dictionary<long,AudioSource>` 活跃字典 + `Queue` 空闲池）上循环播放，支持**多路并发 + 按 id 独立起停**。用于走路/下雨等"持续循环、按需起停"的音效。详见下方「连续音效 (LoopSound)」章节。

### 分层文件速查表

| 文件 | 层 | 职责 |
| --- | --- | --- |
| [Assets/FrameWork/Scripts/Component/Handler/AudioHandler.cs](Assets/FrameWork/Scripts/Component/Handler/AudioHandler.cs) | 框架 | 通用播放 API：`InitAudio`、`PlayMusicForLoop`、`PlayMusicListForLoop`、`PlaySound`、`PlayEnvironment`、暂停/停止/恢复；**连续音效**（`PlayLoopSound`/`StopLoopSound`/`StopAllLoopSound`/`PauseAllLoopSound`/`RestoreAllLoopSound`/`IsLoopSoundPlaying`，含异步竞态令牌防护、`LoopSoundEntry` 活跃字典）；**定时淡出音效** `PlaySoundTimedFade`（借池化独立音源+`CoroutineForPlayTimedFade` 淡出协程，一次性播放不登记 `dicLoopActive`）；**单次音效**（`PlaySoundOnce`/`StopSoundOnce`，独立音源播一次+任意时刻可截断，登记 `dicOnceActive` 含 token 竞态防护） |
| [Assets/FrameWork/Scripts/Component/Manager/AudioManager.cs](Assets/FrameWork/Scripts/Component/Manager/AudioManager.cs) | 框架 | 3 条 `AudioSource` 懒加载、`AudioListener`、按类型加载并缓存 `AudioClip`（`GetMusicClip`/`GetSoundClip`/`GetEnvironmentClip` → `LoadClipDataByAddressbles`）；**连续音效音源池**（`loopSoundRoot` 容器 + `DequeueLoopSource`/`RecycleLoopSource` + `MaxLoopSource=16` 上限） |
| `Assets/Scripts/Component/Handler/AudioHandler.cs`（游戏层，随业务建立） | 游戏 | 业务封装：按场景选曲 `PlayMusicForXxx`、`ActionForUIOnClick` 通用 UI 点击音效；**`AudioEnum` 重载**（各 `Play*`/`Stop*` 接受枚举，内部 `(long)` 转发到框架层 long 接口） |
| `Assets/Scripts/Enums/AudioEnum.cs`（游戏层，随业务建立） | 游戏 | **音频枚举**：枚举值 = `AudioInfo` 配置表 id，枚举名 = `name_res`（去扩展名）。是业务代码调用音频的**首选方式**（替代裸 id），枚举底层类型为 `long` |
| `Assets/Scripts/Component/Manager/AudioManager.cs`（游戏层 partial） | 游戏 | 通用点击音效**排除名单**：`listExcludeUIClickByName`（按 GameObject 名排除）+ `listExcludeUIClickBySprite`（按 sprite 名排除）。默认所有按钮响，命中名单者静音 |
| [Assets/FrameWork/Scripts/Bean/MVC/AudioInfoBean.cs](Assets/FrameWork/Scripts/Bean/MVC/AudioInfoBean.cs) | 框架 | 自动生成的配置 Bean + `AudioInfoCfg`（`GetItemData(id)`） |
| [Assets/FrameWork/Scripts/Bean/MVC/AudioInfoBeanPartial.cs](Assets/FrameWork/Scripts/Bean/MVC/AudioInfoBeanPartial.cs) | 框架 | 配置 Bean 的扩展方法（手写代码写这里） |
| [Assets/FrameWork/Scripts/Component/UI/ButtonAudio.cs](Assets/FrameWork/Scripts/Component/UI/ButtonAudio.cs) | 框架 | 按钮自带点击音效组件（挂在 Button 上，直接放 AudioClip） |
| [Assets/FrameWork/Scripts/Component/UI/AudioView.cs](Assets/FrameWork/Scripts/Component/UI/AudioView.cs) | 框架 | 本地 AudioClip 列表按名播放（脱离配置表的就地播放） |
| [Assets/FrameWork/Scripts/Enums/BaseGameEnum.cs](Assets/FrameWork/Scripts/Enums/BaseGameEnum.cs) | 框架 | `AuidoTypeEnum` 枚举（注意官方拼写为 **Auido**） |

> 提示：`AudioHandler` / `AudioManager` 都是 `partial` 类，框架层放通用播放能力，游戏层放业务封装（按场景选曲、UI 点击音效）。修改时按职责选对应层。

## 音频配置表

- **真实源**：`Assets/Data/Excel/excel_audio_info*.xlsx`（工作表导出为 `Assets/Resources/JsonText/AudioInfo.txt`）。改配置必须改 Excel（见 CLAUDE.md「Excel 是唯一真实源」），仅改 JSON 下次导出会被覆盖。
- **字段**（`AudioInfoBean`）：`id`、`name_res`（资源文件名，不含扩展名）、`remark`（备注）、`audio_type`（0 音效 / 1 音乐 / 2 环境音）、`volume_scale`（float，音效音量缩放；**0 或空 = 1（不缩放）**，填值后框架层 `PlaySound` 自动在基础音量上 ×该系数）。
- **读取**：`AudioInfoCfg.GetItemData(id)` 拿到 Bean，`name_res` 即资源名。

## 音频资源路径

`AudioManager` 按类型从固定 Addressables 地址加载并缓存（同名只加载一次）：

```
音效   Sound       → Assets/LoadResources/Audio/Sound/{name_res}
音乐   Music       → Assets/LoadResources/Audio/Music/{name_res}
环境音 Environment → Assets/LoadResources/Audio/Environment/{name_res}
```

加载走 `LoadAddressablesUtil.LoadAssetAsync<AudioClip>`，结果存入对应 `dicMusicData/dicSoundData/dicEnvironmentData` 缓存。

## 初始化流程

```csharp
// 从存档读取音量，写入 3 条 AudioSource（音量变更后也调用此方法刷新）
AudioHandler.Instance.InitAudio();
```

音量持久化在 `GameConfigBean`（`musicVolume` / `soundVolume` / `environmentVolume`，默认 0.5）。

## 关键 API

> **调用统一用 `AudioEnum` 枚举，不要传裸 id**（游戏层 `Assets/Scripts/Enums/AudioEnum.cs`，枚举底层类型为 `long`）。枚举值即配置表 id，枚举名即 `name_res`，可读性更好且编译期校验。游戏层 `AudioHandler` partial 为每个 `Play*` 提供 `AudioEnum` 重载，内部 `(long)枚举` 转发到框架层 long 接口。**例外**：从配置 Bean 动态读出的 id（如 `soundHitId`/`soundMissId`）本就是 `long`，继续用 long 接口。

### 1. 音效（瞬时，Sound）

```csharp
// 推荐：用枚举播放，默认音量(soundVolume)在 Camera.main 位置
AudioHandler.Instance.PlaySound(AudioEnum.sound_xxx);

// 指定 3D 播放位置（PlayClipAtPoint）
AudioHandler.Instance.PlaySound(AudioEnum.sound_xxx, worldPosition);

// 完整：自定义音量、可指定 AudioSource（传 null 用 PlayClipAtPoint 在指定点播放）
// 注意：这里的 volumeScale 是【绝对音量】，直接作为最终音量，不叠加配置音量
AudioHandler.Instance.PlaySound(AudioEnum.sound_xxx, worldPosition, volumeScale, audioSource);

// 运行时音量缩放：最终音量 = 配置音效音量(soundVolume) × volumeScale（代码里临时放大/缩小）
AudioHandler.Instance.PlaySoundForVolumeScale(AudioEnum.sound_xxx, 1.5f);

// 随机播放：从多个候选音效中等概率随机取一个播放（同类多备选、避免重复）
AudioHandler.Instance.PlaySoundRandom(AudioEnum.sound_xxx_1, AudioEnum.sound_xxx_2);

// 配置驱动的动态 id（来自 Bean，long）走 long 接口
AudioHandler.Instance.PlaySound(beanData.soundHitId);
```
- **首选：配置表 `volume_scale`**（固定缩放）。某个音效需要恒定放大/缩小时，直接在 Excel `AudioInfo` 该行填 `volume_scale`，框架层 `PlaySound` 核心方法会在 `audioInfo` 取到后自动 `volumeScale *= volume_scale`（`volume_scale <= 0` 视为 1 不缩放）。调用处保持普通 `PlaySound(AudioEnum.xxx)` 即可，**无需在代码里写缩放倍率**。
- `PlaySound(..., float volumeScale, ...)` 的 `volumeScale` 是**绝对音量**（直接作为最终音量）；`PlaySoundForVolumeScale(audio, volumeScale)` 的 `volumeScale` 是**运行时叠加在配置音量上的倍率**（会与配置 `volume_scale` 叠乘：`soundVolume × 运行时倍率 × 配置 volume_scale`）。固定缩放优先用配置列，不要写死在代码里。
- `soundId == 0`（`AudioEnum.None`）或 `volumeScale == 0` 直接跳过。
- **防抖**：同一 `soundId` 在 0.1s 内重复请求会被忽略（`timeUpdateForRepeatPlay` + `lastPlaySoundId`），避免密集命中时音效炸裂。

### 2. 音乐（循环，Music）

```csharp
// 单曲循环（loop=true）
AudioHandler.Instance.PlayMusicForLoop(AudioEnum.music_xxx);
AudioHandler.Instance.PlayMusicForLoop(AudioEnum.music_xxx, volumeScale);

// 列表随机轮播：每首播完用协程切下一首随机曲（非 loop，靠协程衔接）
AudioHandler.Instance.PlayMusicListForLoop(new List<AudioEnum>{ AudioEnum.music_a, AudioEnum.music_b });
```
游戏层可按场景封装选曲（游戏层 partial）：
```csharp
AudioHandler.Instance.PlayMusicForMain();    // 主界面
AudioHandler.Instance.PlayMusicForGaming();  // 游戏进行中
```

### 3. 环境音（循环，Environment）

```csharp
AudioHandler.Instance.PlayEnvironment(AudioEnum.sound_night_1);        // 枚举
AudioHandler.Instance.PlayEnvironment(AudioEnum.sound_night_1, volumeScale);
AudioHandler.Instance.PlayEnvironment(sceneData.environment_sound);    // 配置驱动的动态 id 走 long 接口
```

- **建议场景环境音走配置表驱动**：场景配置表加 `environment_sound` 列（AudioInfo id，空/0=不播），场景加载 Handler 进场播、离场停。单通道一路环境音，同场景只能配一个 id。
- **资源要求**：audio_type=2 的文件必须在 `Assets/LoadResources/Audio/Environment/` 目录，且注册进 Addressables **`Audio_Environment`** 组（逐文件 entry、address=完整路径）才能被寻址。
- 枚举段位约定：音效/音乐/环境音分段（如音效 1~640001、音乐 1000001~1200001、**环境音 2000001 起**）。

### 4. 暂停 / 恢复 / 停止

```csharp
AudioHandler.Instance.PauseMusic();        // 暂停音乐（并停掉列表轮播协程）
AudioHandler.Instance.RestoreMusic();      // 恢复音乐
AudioHandler.Instance.StopMusic();         // 停止音乐并清 clip
AudioHandler.Instance.StopMusicListLoop(); // 仅停列表轮播协程

AudioHandler.Instance.PauseEnvironment();
AudioHandler.Instance.RestoreEnvironment();
AudioHandler.Instance.StopEnvironment();
```

### 5. UI 点击音效

三种机制并存：

- **通用点击音效**（自动，**默认全响 + 排除式**，游戏层 `AudioHandler.Awake` 里 `UIHandler.Instance.AddOnClickAction(ActionForUIOnClick)`）：点击时凡是**可交互（`interactable`）且带 sprite** 的 `Button` **默认都播** 点击音；image 名为 `ViewExit` 的退出按钮播退出音。**要让某按钮静音**（频繁/连续操作类）：把它的 **GameObject 名**加进 `AudioManager.listExcludeUIClickByName`，或把其 **sprite 名**加进 `listExcludeUIClickBySprite`。二者取并集命中即静音；sprite 名排除仅适合独占专用枠，共用通用枠的按钮**必须按 GameObject 名排除**，否则误伤大量通用按钮。
  - **该机制由 `UIHandler.Update()` 的物理鼠标点击 + `RaycastAll` 驱动，只认物理鼠标点击/触摸**，不监听 `Button.onClick`、也覆盖不到 ESC 退出。因是默认全响，各 UI **无需**在 `OnClickForButton`/打开界面处手动加播点击音（会与本机制重复）。
  - **弹窗背景点击关闭音效**（自动）：`ActionForUIOnClick` 里额外判断——点击对象经 `GetComponentInParent<DialogView>()` 命中、且正是该弹窗的 `ui_Background`、且 `dialogData.isDestroyBG==true` 时，播退出音。因背景按钮 image 常无 sprite，此判断**放在 sprite 空判之前**。所有弹窗均继承 `DialogView` 故一处覆盖全部。**游戏层实现，零框架改动。**
- **ESC 退出音效**（自动，全局补位）：游戏层可订阅 `InputActionUIEnum.ESC` 的 `InputAction.started` → 一处全局补播退出音。ESC 退出走 InputSystem、不产生鼠标点击，上面的点击机制覆盖不到。所有 UI **零改动**自动覆盖，不要在各 UI 的 ESC/退出分支里手动加播放。
- **按钮独立音效**（手动挂载）：在 Button 上挂 [ButtonAudio](Assets/FrameWork/Scripts/Component/UI/ButtonAudio.cs) 组件，填 `clickClip` 列表（随机取一个），用 `soundVolume` 在按钮位置播放。**不读配置表**，直接用本地 AudioClip。

### 6. 音量设置

设置界面用滑条改 `gameConfig.musicVolume`/`soundVolume`，每次变更调用 `AudioHandler.Instance.InitAudio()` 即时生效（环境音音量同字段）。

## 常见任务流程

### 新增一个音效/音乐/环境音
1. 把音频文件放到对应目录 `Assets/LoadResources/Audio/{Sound|Music|Environment}/`（**类型与目录强绑定**，环境音必须放 Environment），确保被 Addressables 标记（环境音组 = `Audio_Environment`，音效 = `Audio_Sound`，音乐 = `Audio_Music`；新目录/新类型需先建组再逐文件 entry，address = 完整路径）。
2. 在 `excel_audio_info` Excel 新增一行（按 id 升序插入，见 [feedback_excel_id_sorted_insert]）：`id` / `name_res`（= 文件名）/ `remark` / `audio_type`。
3. 在 Unity 编辑器用配置导出工具重新生成 `AudioInfo.txt`（仅改 Excel 时须提醒用户导出）。
4. **在游戏层 `AudioEnum.cs` 同步补一个枚举项**（枚举名 = `name_res` 去扩展名，值 = id），保持与配置表一一对应。
5. 代码里用对应 `Play*` API + `AudioEnum` 枚举播放。

> AudioEnum 是手工维护的枚举（首次可由 `AudioInfo.txt` 生成），配置表增删音频时**必须**同步本枚举，否则枚举与 id 错位。

### 在业务里触发音效
固定音效用枚举：`AudioHandler.Instance.PlaySound(AudioEnum.sound_xxx, worldPosition)`。配置驱动的动态音效（id 存在 Bean 里）走 long 接口。

## 连续音效 (LoopSound) — 多路并发循环（走路/下雨等）

用于"需要持续循环、按需播放/停止、且可多路并发"的音效。**复用普通音频配置**——不新增 `audio_type`/资源目录/`AudioEnum` 项，传任意音频 id 即按其 `audio_type` 走现有加载路由取 clip，在**循环 AudioSource 池**上播放。

```csharp
// 起播（默认音量=soundVolume；同 id 已在播含加载中则忽略，天然去重）
// 签名：PlayLoopSound(id, float volumeScale = -1f, float pitch = 1f)；volumeScale<0 时取 soundVolume
AudioHandler.Instance.PlayLoopSound(AudioEnum.sound_walk_1);
AudioHandler.Instance.PlayLoopSound(AudioEnum.sound_walk_1, volumeScale);     // 指定基础音量
AudioHandler.Instance.PlayLoopSound(AudioEnum.sound_walk_1, pitch: 2f);       // 默认音量+加快一倍(pitch=2,同时升调)
AudioHandler.Instance.StopLoopSound(AudioEnum.sound_walk_1);              // 停指定（加载中的也能取消）
AudioHandler.Instance.StopAllLoopSound();                                // 停全部（切场景兜底）
AudioHandler.Instance.PauseAllLoopSound();                               // 暂停（仅暂停当前在播的）
AudioHandler.Instance.RestoreAllLoopSound();                             // 恢复被暂停的那批
bool playing = AudioHandler.Instance.IsLoopSoundPlaying(AudioEnum.sound_walk_1);
```

**设计要点：**
- **音量跟随 `soundVolume`**（不新增 `loopVolume`/设置滑条）；最终音量 = `soundVolume × 配置 volume_scale`。`InitAudio()` 刷新时遍历活跃 loop 源用 `soundVolume × entry.volumeScale` 重算（不能直接赋 soundVolume，否则抹掉 volume_scale）。
- **变速 `pitch`**：`PlayLoopSound` 第三参数 `pitch`（默认 1），记入 `LoopSoundEntry.pitch`，起播时 `source.pitch = pitch`。`pitch=2` 让播放速度加快一倍（Unity 原生音源会同时升调一个八度，无法只变速不变调）。`RecycleLoopSource` 回收时**复位 `pitch=1`**，避免变速源污染下次复用。
- **异步竞态防护（关键）**：`GetClip` 是异步回调，`PlayLoopSound` 先登记 pending `LoopSoundEntry{source=null, token}` 占位（ContainsKey 即去重，防加载窗口内重复起源），加载回调校验 `token` 未变且 `!canceled` 才真正取源起播；`StopLoopSound` 对"加载中"的 id 置 `canceled` → 回调到达时丢弃。防"停请求先于加载回调到达 → 音源永久播放停不掉"。
- **音源池**：`AudioManager.DequeueLoopSource/RecycleLoopSource`，`MaxLoopSource=16` 上限（超限告警并静默不播）；回收先 `Stop()` 再清 clip（`SetActive(false)` 不会停播放）；`spatialBlend=0`（2D 全局单路，不吃位置）。
- **暂停不误启**：`PauseAllLoopSound` 只暂停当前 `isPlaying` 的源并记录到 `listLoopPaused`，`RestoreAllLoopSound` 只 UnPause 这批。
- **不复用一次性音效防抖变量**（`lastPlaySoundId`/`timeUpdateForRepeatPlay` 不碰），去重只靠 `dicLoopActive`。
- **生命周期挂钩**：连续音效音源常驻 `DontDestroyOnLoad`**不随场景销毁**，切场景/清场时必须挂 `StopAllLoopSound()` 兜底防跨场景残留。

**接入范式（移动脚步声类单实体消费方）：** 移动分支 `PlayLoopSound(AudioEnum.sound_walk_1, pitch: 1.5f)`、静止分支 `StopLoopSound(...)`、控制禁用分支也 `StopLoopSound(...)`（覆盖"走着走着打开界面"）。靠 `PlayLoopSound`/`StopLoopSound` 幂等，每 FixedUpdate 重复调无害；走路声**复用一次性音效**（不新建 `loop_walk_1`）。

> 未做（如需再扩展）：独立 `loopVolume` 音量条；按句柄多路 + 3D 位置跟随；同 id 平滑换 clip（当前按 id 去重会忽略）。`dicLoopData` 同其它音频缓存一样从不 `Addressables.Release`（既有技术债，池仅解 AudioSource 组件泄漏）。

## 定时淡出音效 (PlaySoundTimedFade) — 只取长音效前一段并平滑收尾

用于"一段长音效只需播前 N 秒，并在末段淡出到 0"的场景（如 10s 音效只用 5s、第 4s 起淡出）。**借用连续音效池的独立音源**（`DequeueLoopSource`，`loop=false`）+ 一个淡出协程，播完 `RecycleLoopSource` 自动回收——借此拿到"独立音源句柄"从而能中途改音量淡出（`PlaySound` 走 `PlayOneShot`/`PlayClipAtPoint` 无句柄，改音量会波及整条共享源）。若停止时机播放时无法预知（需任意时刻截断），改用单次音效 `PlaySoundOnce`/`StopSoundOnce`（见下节）。

```csharp
// 框架层签名：PlaySoundTimedFade(long id, float playDuration, float fadeStartTime, float volumeScale=-1f) —— 前两参强制传,仅volumeScale默认-1f取soundVolume
// 游戏层 AudioEnum 重载无默认值，四参必须全传：PlaySoundTimedFade(AudioEnum, playDuration, fadeStartTime, volumeScale)
AudioHandler.Instance.PlaySoundTimedFade(AudioEnum.sound_xxx, 5f, 4f, -1f);   // 播5秒,第4秒起线性淡出,音量取soundVolume
AudioHandler.Instance.PlaySoundTimedFade(AudioEnum.sound_xxx, 6f, 5f, 0.8f);  // 播6秒,第5秒起淡出,基础音量0.8
```

**设计要点：**
- **参数**：`playDuration` 总时长到点停止（应 ≤ clip 长度）；`fadeStartTime` 淡出起点（应 ≤ playDuration），此前保持基础音量；`volumeScale<0` 取 `soundVolume`，最终基础音量 = `volumeScale × 配置 volume_scale`。**淡出固定线性 `1-progress`，无曲线参数**。入参已纠偏（`fadeStartTime` 夹在 `[0, playDuration]`）。
- **与 LoopSound 的区别**：`loop=false` 一次性播放；**不登记到 `dicLoopActive`**，故**不参与全局 `PauseAllLoopSound`/`StopAllLoopSound`/`InitAudio` 音量刷新，也不支持中途打断**。切场景时若仍在播，会借 `DontDestroyOnLoad` 的音源播完剩余时长后自行回收（一次性短音效可接受）。
- **协程 `CoroutineForPlayTimedFade`**：`WaitForSeconds(fadeStartTime)` → 逐帧 `source.volume = baseVolume × (1-progress)` → 到点 `RecycleLoopSource`（内部 `Stop()` + 复位 volume/pitch）。

## 单次音效 (PlaySoundOnce / StopSoundOnce) — 播一次、任意时刻可截断

用于"音效只播一次（不循环），但停止时机播放时无法预知"的场景（如对话说话声随文本动画结束而截断）。与 `PlaySoundTimedFade` 同借连续音效池独立音源（`loop=false`），但**不限定时长、不预定淡出**——播完整段 clip 后自动回收；期间任何时刻可 `StopSoundOnce` 立即截断。**登记到独立字典 `dicOnceActive`（与 LoopSound 同构的 token 竞态防护），因此支持中途打断**。

```csharp
// 起播（默认音量=soundVolume；同 id 已在播则先截断旧的起播新的——重新起播语义）
AudioHandler.Instance.PlaySoundOnce(AudioEnum.sound_talk_1);
// 中途截断（立即停止并回收音源；未在播/已自然播完为空操作；加载中的直接取消）
AudioHandler.Instance.StopSoundOnce(AudioEnum.sound_talk_1);
```

**设计要点：**
- **独立音源 + token**：登记 `dicOnceActive`（`OnceSoundEntry{source, token, canceled, coroutineForRecycle}`），加载回调校验令牌防"停请求先于加载回调到达 → 音源永久播放"；最终音量 = `volumeScale × 配置 volume_scale`（`volumeScale<0` 取 `soundVolume`）。
- **自然结束自动回收**：起播时登记 `CoroutineForOnceSoundRecycle`（`WaitForSeconds(clip.length)` 后回收音源+移登记）；截断/重播时先终止该协程。
- **截断即硬停**：`StopSoundOnce` 直接 `RecycleLoopSource`（内部 `Stop()`+复位 volume/pitch），无淡出——要平滑收尾才用 `PlaySoundTimedFade`。
- **重播语义**：同 id 已在播（含加载中）时 `PlaySoundOnce` 先 `StopSoundOnce` 截断回收旧的再起播。
- **不参与全局控制**：同 TimedFade——不登记 `dicLoopActive`，不受 `PauseAllLoopSound`/`StopAllLoopSound`/`InitAudio` 音量刷新影响；切场景时短音效自行播完回收，可接受。

## 约束与注意事项

- **音频播放统一走 `AudioHandler`**，不要在业务代码里直接 new `AudioSource` 或散落调 `AudioSource.PlayClipAtPoint`（脱离配置/缓存的本地播放才用 `AudioView`/`ButtonAudio`）。
- **调用统一用 `AudioEnum` 枚举**，禁止写裸 id（如 `PlaySound(15)`）。游戏层 partial 为各 `Play*` 提供枚举重载；框架层接口为 `long`，供配置驱动的动态 id 使用（音频 id 已全面 long 化）。新增音频务必同步维护 `AudioEnum`。
- **配置表是唯一真实源**：音频 id ↔ 资源名映射改在 Excel，别只改 `AudioInfo.txt`（下次导出会被覆盖）。
- **资源缓存**：clip 按 `{路径}/{name_res}` 缓存，重复播放不重复加载；新增音频确保 Addressables 地址与三类固定路径前缀一致，否则加载失败（日志 `没有名字为:xxx 的音效资源`）。
- **枚举拼写**：类型枚举为 `AuidoTypeEnum`（源码即写作 **Auido**，非 Audio），引用时勿"纠正"拼写。
- **音效防抖**：0.1s 内同 id 不重复播放是刻意设计，需要叠加同音效时注意此限制。
- **`VolumeHandler` 不是音量管理**：项目里的 `VolumeHandler`/`VolumeManager` 是 URP 后处理（景深 DepthOfField）控制器，与音频音量无关。音频音量在 `GameConfigBean` + 设置界面。
- **Bean 规则**：`AudioInfoBean.cs` 自动生成，扩展写在 [AudioInfoBeanPartial.cs](Assets/FrameWork/Scripts/Bean/MVC/AudioInfoBeanPartial.cs)。
- **代码规范**：所有方法/属性加 `/// <summary>` XML 注释，用 `#region`/`#endregion` 按「音乐播放/音效播放/环境音效/停止相关」分区。
- **配套 agent**：复杂改动可委派 `system-audio` 子代理；改了本 skill `watched_files` 命中的代码须同步更新本文档（见 [feedback_agent_skill_sync]）。
