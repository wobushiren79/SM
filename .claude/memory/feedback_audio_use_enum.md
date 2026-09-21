---
name: feedback_audio_use_enum
description: 音频播放统一用 AudioEnum 枚举调用，禁止裸 id；音频 id 全面 long 化；新增音频须同步维护枚举
metadata:
  type: feedback
---

音效/音乐/环境音播放统一用 `AudioEnum` 枚举调用，**禁止传裸 id**（如 `PlaySound(15)`）。音频 id（音效/音乐/环境音）统一为 `long` 类型。

**Why:** 裸 id 不直观、易写错、无编译期校验，用户明确要求改成枚举调用。

**How to apply:**
- 枚举定义在 [Assets/Scripts/Enums/AudioEnum.cs](Assets/Scripts/Enums/AudioEnum.cs)：枚举值 = `AudioInfo` 配置表 id，枚举名 = `name_res`（去扩展名），由 `AudioInfo.txt` 一一对应生成。
- 音频 id 已全面 `long` 化（`AudioInfoCfg` 主键、`AudioEnum` 底层类型均为 `long`）。游戏层 `AudioHandler` partial（[Assets/Scripts/Component/Handler/AudioHandler.cs](Assets/Scripts/Component/Handler/AudioHandler.cs)）为 `PlaySound`/`PlayMusicForLoop`/`PlayMusicListForLoop`/`PlayEnvironment` 提供 `AudioEnum` 重载，内部 `(long)枚举` 转发到框架层 `long` 接口（框架层所有 id 形参、`listMusicLoop`、`lastPlaySoundId` 均为 `long`）。
- **例外**：从配置 Bean 动态读出的 id（如 `FightUnderAttackBean.soundHitId`/`soundMissId`）也是 `long`，继续走 long 接口。
- **新增/删除音频时必须同步维护 AudioEnum**（手工维护，首次由配置表生成），否则枚举与 id 错位。
- **音效音量缩放**：某音效需固定放大/缩小时，优先在 Excel `AudioInfo` 表的 `volume_scale`（float）列填值（0/空=1 不缩放），框架层 `PlaySound` 核心会自动 `volumeScale *= volume_scale`；调用处保持普通 `PlaySound(AudioEnum.xxx)`，**不要把倍率写死在代码里**。运行时临时缩放才用 `PlaySoundForVolumeScale(audio, scale)`（会与配置列叠乘）。改了 `volume_scale` 列须在 Unity 重新「生成 Entity」（加字段）+「导出」（刷 JSON）。
- 配套文档：[[feedback_agent_skill_sync]] —— 改 AudioHandler/AudioEnum 须同步 audio-system skill 与 system-audio agent（已加 AudioEnum.cs 到 watched_files）。
