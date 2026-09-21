---
name: feedback_pixellab_animation_output
description: PixelLab 帧动画输出规则：只保留合成精灵表，不保留单帧文件
metadata:
  type: feedback
---

生成帧动画时，最终只保存合成好的精灵表（spritesheet），不保留单帧 PNG 文件。

**Why:** 单帧文件对项目没有用处，只会占用空间，用户明确要求不保留。

**How to apply:** 下载帧到临时目录 → 合成精灵表 → 删除临时帧文件。最终 `Assets/Out/` 中只留 `<名称>_4x4.png`（或对应规格的精灵表）。
