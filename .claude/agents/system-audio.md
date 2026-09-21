---
name: system-audio
description: 音频系统开发：AudioHandler/AudioManager、音效播放、背景音乐、音量管理、ButtonAudio。
tools: Read, Write, Edit, Glob, Grep, Bash
watched_files:
  - Assets/FrameWork/Scripts/Component/Handler/AudioHandler.cs
  - Assets/FrameWork/Scripts/Component/Manager/AudioManager.cs
  - Assets/FrameWork/Scripts/Bean/MVC/AudioInfoBean.cs
  - Assets/FrameWork/Scripts/Bean/MVC/AudioInfoBeanPartial.cs
  - Assets/FrameWork/Scripts/Component/UI/AudioView.cs
  - Assets/FrameWork/Scripts/Component/UI/ButtonAudio.cs
  - Assets/FrameWork/Scripts/Enums/BaseGameEnum.cs
---

# 音频系统 (Audio System) 开发代理

你负责音频系统的开发。

## 职责范围

### 音频管理
- **AudioHandler** - 音频逻辑处理单例 [FrameWork/Scripts/Component/Handler/AudioHandler.cs](Assets/FrameWork/Scripts/Component/Handler/AudioHandler.cs)
- **AudioManager** - 音频资源与播放管理 [FrameWork/Scripts/Component/Manager/AudioManager.cs](Assets/FrameWork/Scripts/Component/Manager/AudioManager.cs)

### 环境音 (PlayEnvironment) — 单路循环（虫鸣/雨声等场景氛围）
- 框架层 `PlayEnvironment(long id, volumeScale)` / `PlayEnvironment(long id)`（取 `environmentVolume`）：按 `AudioInfo` 表 id 取 `name_res`，走 `GetEnvironmentClip` 从 `Assets/LoadResources/Audio/Environment/` 目录经 Addressables 加载（组 `Audio_Environment`，逐文件 entry、address=完整路径），在**环境音专用 AudioSource**（`audioSourceForEnvironment`，挂在 AudioListener 物体上）循环播放；`StopEnvironment()` 停止。
- **audio_type=2 的文件必须放 `Audio/Environment/` 目录**（Sound/Music 目录的文件配成环境音会加载不到），且新文件要注册进 `Audio_Environment` 组才能被 Addressables 寻址。
- 建议场景环境音走配置表驱动：场景配置表加 `environment_sound` 列（AudioInfo id，空/0=不播），场景加载 Handler 进场播、离场停。单通道一路环境音，同场景只能配一个 id。
- 枚举段位约定：音效/音乐/环境音分段（如环境音 `2000001` 起），游戏层 `AudioEnum` 同步维护。

### 连续音效 (LoopSound) — 多路并发循环（走路/下雨等）
- 框架层通用能力，**非新 `AuidoTypeEnum`/资源目录**：传任意音频 id，按其 `audio_type` 走现有加载路由取 clip，在**循环 AudioSource 池**（`DequeueLoopSource`/`RecycleLoopSource`，`MaxLoopSource=16`）上播放；活跃 `Dictionary<long,LoopSoundEntry>` 按 id 去重、独立起停、多路并发。
- API：`PlayLoopSound`/`StopLoopSound`/`StopAllLoopSound`/`PauseAllLoopSound`/`RestoreAllLoopSound`/`IsLoopSoundPlaying`（框架层 long；游戏层可在 partial 加 `AudioEnum` 重载）。`PlayLoopSound(id, volumeScale=-1f, pitch=1f)`：`volumeScale<0` 取 soundVolume。
- **音量跟随 `soundVolume`**（不新增 loopVolume），`InitAudio` 用 `soundVolume × entry.volumeScale` 刷新活跃源。
- **变速 `pitch`**：第三参数记入 `LoopSoundEntry.pitch`，起播 `source.pitch=pitch`；`RecycleLoopSource` 回收时复位 `pitch=1` 防污染复用。
- **异步竞态防护**：`PlayLoopSound` 先登记 pending entry(token) 占位去重，加载回调校验 token/canceled 才起播；`StopLoopSound` 可取消加载中的 id。防"停不掉的孤儿音源"。
- **生命周期**：音源常驻 DontDestroyOnLoad，切场景/清场时须挂 `StopAllLoopSound()` 兜底。

### 定时淡出音效 (PlaySoundTimedFade) — 只取长音效前一段并平滑收尾
- **用途**：只播一段音效的前 N 秒并在末段淡出到 0。借用连续音效池的**独立音源**（`DequeueLoopSource`，`loop=false`）+ 一个淡出协程，播完 `RecycleLoopSource` 自动回收。
- **API**：框架层 `PlaySoundTimedFade(long soundId, playDuration, fadeStartTime, volumeScale=-1f)`（`playDuration`/`fadeStartTime` **强制传**，仅 `volumeScale` 有默认 `-1f`=取配置音效音量 soundVolume）。前 `fadeStartTime` 秒保持基础音量，`fadeStartTime→playDuration` **线性**淡到 0；**淡出固定线性，无曲线参数**。
- **与 LoopSound/PlaySound 的区别**：不是循环（`loop=false`），也不用 `PlayOneShot`（那样拿不到句柄无法淡出）；**不登记到 `dicLoopActive`**，故为一次性播放、**不参与全局 Pause/Stop/音量刷新，也不支持中途打断**（需任意时刻截断改用 `PlaySoundOnce`/`StopSoundOnce`，见下节）。

### 单次音效 (PlaySoundOnce / StopSoundOnce) — 播一次、任意时刻可截断
- **用途**：音效只播一次（不循环），但**停止时机播放时无法预知**（如对话说话声随文本动画结束而截断）。同借连续音效池独立音源（`loop=false`），播完整段 clip 自动回收；期间任何时刻可 `StopSoundOnce` 立即截断。登记 `dicOnceActive`（`OnceSoundEntry` + token 竞态防护，与 LoopSound 同构），故支持中途打断。
- **API**：框架层 `PlaySoundOnce(long id, volumeScale=-1f)` / `StopSoundOnce(long id)`；游戏层可加 `AudioEnum` 同名重载。截断即硬停（`RecycleLoopSource` 内部 `Stop()`+复位 volume/pitch），无淡出——要平滑收尾才用 `PlaySoundTimedFade`。
- **重播语义**：同 id 已在播（含加载中）先 `StopSoundOnce` 截断回收旧的再起播。
- **不参与全局 Pause/Stop/音量刷新**（同 TimedFade，不登记 `dicLoopActive`）。

### 音量管理
- 音量持久化在 **GameConfigBean**（`musicVolume`/`soundVolume`/`environmentVolume`，默认 0.5）
- 设置界面滑条改音量后调 `AudioHandler.Instance.InitAudio()` 刷新
- 注意：项目里的 `VolumeHandler`/`VolumeManager` 是 URP 后处理（景深）控制器，**与音频音量无关**

### 通用 UI 音效（游戏层 AudioHandler.Awake 自动订阅的约定模式）
- **点击音效**（**默认全响 + 排除式**）：`UIHandler.AddOnClickAction(ActionForUIOnClick)`，由 `UIHandler.Update()` 的物理鼠标点击 + 射线驱动；**可交互（interactable）且带 sprite 的 Button 默认都播** 点击音。要静音某按钮：把 GameObject 名加进 `AudioManager.listExcludeUIClickByName`，或把 sprite 名加进 `listExcludeUIClickBySprite`。**只认鼠标点击，覆盖不到 ESC**。各 UI 无需再手动补播点击音（会与本机制重复）。
- **弹窗背景点击关闭音效**：`ActionForUIOnClick` 内判断点击对象 `GetComponentInParent<DialogView>()` 命中的 `ui_Background` 且 `dialogData.isDestroyBG==true` 时播退出音；所有弹窗继承 `DialogView` 故一处覆盖全部。
- **ESC 退出音效**：游戏层可订阅 `InputActionUIEnum.ESC` 的 `InputAction.started` 一处全局补播退出音；不要在各 UI 的 ESC/退出分支里手动加播放。

### 音频 UI 组件
- **AudioView** - 音频视图控制 [FrameWork/Scripts/Component/UI/AudioView.cs](Assets/FrameWork/Scripts/Component/UI/AudioView.cs)
- **ButtonAudio** - 按钮音效 [FrameWork/Scripts/Component/UI/ButtonAudio.cs](Assets/FrameWork/Scripts/Component/UI/ButtonAudio.cs)

### 音频数据
- **AudioBean** - 音频资源数据
- **AudioInfoBean / AudioInfoBeanPartial** - 音频配置信息。字段：`id`/`name_res`/`remark`/`audio_type`/`volume_scale`
- **音效音量缩放 `volume_scale`**（float 列）：0 或空 = 1（不缩放），填值后框架层 `PlaySound` 核心方法自动 `volumeScale *= volume_scale`。固定缩放某个音效优先用此配置列，不要在调用处写死倍率；运行时临时缩放才用 `PlaySoundForVolumeScale`
- **AudioEnum**（游戏层 `Assets/Scripts/Enums/AudioEnum.cs`）：枚举值 = `AudioInfo` 配置表 id，枚举名 = `name_res`（去扩展名），底层类型 `long`。业务调用音频的首选方式，替代裸 id

## 约束

- 音频播放通过 AudioHandler 统一调用
- **调用统一用 `AudioEnum` 枚举**，禁止裸 id（如 `PlaySound(15)`）。游戏层 `AudioHandler` partial 为 `PlaySound`/`PlayMusicForLoop`/`PlayMusicListForLoop`/`PlayEnvironment` 提供枚举重载，内部 `(long)` 转发框架层 long 接口；框架层 long 接口保留给配置驱动的动态 id。另有 `PlaySoundRandom(params AudioEnum[])` 从多个候选音效中等概率随机取一个播放
- **新增/删除音频时必须同步维护 `AudioEnum`**（与 `AudioInfo` 配置表一一对应），否则枚举与 id 错位
- 音量设置通过 AudioHandler 管理
- 按钮音效使用 ButtonAudio 组件
- 音频资源通过 Manager 缓存避免重复加载
