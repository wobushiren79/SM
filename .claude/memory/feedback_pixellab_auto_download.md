---
name: feedback_pixellab_auto_download
description: PixelLab 生成图片后必须自动下载到 Assets/Out/ 对应子目录，无需用户提醒
metadata:
  type: feedback
---

PixelLab 生成任务完成后，必须自动将图片下载到本地 `Assets/Out/<任务名>/` 目录，不能只展示链接等用户手动下载。

**Why:** 用户明确要求自动下载，不需要每次手动点击链接。

**How to apply:** 每次 `get_object` / `get_character` / 等工具返回 completed 状态和图片 URL 后，立即用 `curl -L <url> -o <本地路径>` 下载到 `Assets/Out/<合适子目录>/`，文件名应体现风格或内容。
