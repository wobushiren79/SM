---
name: pixellab-art
description: 使用 PixelLab MCP 生成像素风格游戏美术资源，包括角色、地图物体、瓦片集（俯视角/横版/等轴测）。适用于需要为 ScreenMiner 生成像素美术素材的场景。触发关键词：像素图生成、生成像素图、像素图片生成、画像素图、生成像素美术、像素素材、pixel art生成、生成角色像素图、生成瓦片、生成精灵图。
---

# PixelLab 像素美术生成

> ⚠️ **调用前提（最高优先级）**：PixelLab 是付费外部服务（消耗 credits），用户可能不想使用。
> 仅当**用户在当前请求中明确要求生成像素图**，或已向用户说明"将用 PixelLab 生成 X"并获得**明确同意**后，
> 才允许调用任何 `create_*`/`animate_*` 生成类工具。
> **禁止在配置/代码等其他任务中"顺带"自行生成图片**——缺图时留空或用占位图 fallback，
> 在总结中告知用户缺图，由用户决定是否生成。委派执行时 prompt 必须注明"用户已同意使用 PixelLab"。

## 概述

通过 PixelLab MCP（`pixellab` 服务器）调用 AI 生成像素风格美术资源。所有工具均为异步生成——调用后得到 ID，需轮询 `get_*` 接口获取结果。

## 可用工具总览

| 类别 | 工具 | 说明 |
|------|------|------|
| 角色 | `create_character` | 生成带方向视图的像素角色 |
| 角色 | `create_character_state` | 生成角色的变体状态（换装、受伤等） |
| 角色 | `animate_character` | 为角色添加动画序列 |
| 角色 | `get_character` | 查询角色生成结果 |
| 角色 | `list_characters` | 列出所有已生成角色 |
| 角色 | `delete_character` | 删除角色 |
| 物体 | `create_map_object` | 生成透明背景的地图物体 |
| 物体 | `create_object` | 生成通用物体（支持多方向/动画） |
| 物体 | `create_object_state` | 生成物体变体 |
| 物体 | `animate_object` | 为物体添加动画 |
| 物体 | `get_map_object` | 查询地图物体结果 |
| 物体 | `get_object` | 查询通用物体结果 |
| 物体 | `list_objects` | 列出所有已生成物体 |
| 物体 | `delete_object` | 删除物体 |
| 物体 | `select_object_frames` | 从候选帧中选定最终结果 |
| 物体 | `dismiss_review` | 丢弃候选帧 |
| 俯视角瓦片 | `create_topdown_tileset` | 生成 Wang 瓦片集（地形过渡） |
| 俯视角瓦片 | `get_topdown_tileset` | 查询俯视角瓦片集结果 |
| 俯视角瓦片 | `list_topdown_tilesets` | 列出已生成的俯视角瓦片集 |
| 俯视角瓦片 | `delete_topdown_tileset` | 删除俯视角瓦片集 |
| 横版瓦片 | `create_sidescroller_tileset` | 生成横版平台游戏瓦片集 |
| 横版瓦片 | `get_sidescroller_tileset` | 查询横版瓦片集结果 |
| 横版瓦片 | `list_sidescroller_tilesets` | 列出已生成的横版瓦片集 |
| 横版瓦片 | `delete_sidescroller_tileset` | 删除横版瓦片集 |
| 等轴测瓦片 | `create_isometric_tile` | 生成单块等轴测瓦片 |
| 等轴测瓦片 | `get_isometric_tile` | 查询等轴测瓦片结果 |
| 等轴测瓦片 | `list_isometric_tiles` | 列出已生成的等轴测瓦片 |
| 等轴测瓦片 | `delete_isometric_tile` | 删除等轴测瓦片 |
| 高级瓦片 | `create_tiles_pro` | 生成高级等轴测瓦片（可指定视角/风格） |
| 高级瓦片 | `get_tiles_pro` | 查询高级瓦片结果 |
| 高级瓦片 | `list_tiles_pro` | 列出已生成的高级瓦片 |
| 高级瓦片 | `delete_tiles_pro` | 删除高级瓦片 |

---

## 角色生成

### `create_character` 参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `description` | string | 必填 | 角色外观描述（英文效果更佳） |
| `name` | string | null | 角色名称标识符 |
| `body_type` | `humanoid`/`quadruped` | `humanoid` | 体型：人形或四足 |
| `template` | `bear/cat/dog/horse/lion` | null | 四足动物模板（quadruped时必选） |
| `n_directions` | `4`/`8` | `8` | 方向视图数量 |
| `proportions` | preset名称 | `default` | 体型比例：`default`/`chibi`/`cartoon`/`stylized`/`realistic_male`/`realistic_female`/`heroic` |
| `size` | int | `48` | 画布像素大小 |
| `outline` | string | `single color black outline` | 描边风格 |
| `shading` | string | `basic shading` | 阴影处理 |
| `detail` | string | `medium detail` | 细节程度 |
| `ai_freedom` | float | `750` | AI 创作自由度（越高越有创意） |
| `view` | string | `low top-down` | 视角 |

**示例：生成一个骑士角色**
```
create_character(
  description="knight in iron armor, blue cape, carrying a sword and shield",
  name="knight",
  proportions={"type": "preset", "name": "heroic"},
  size=64,
  n_directions=8
)
```

### `create_character_state` 参数详解

基于已有角色生成变体（换装、受伤状态、死亡状态等）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `character_id` | string | 是 | 源角色的 UUID |
| `edit_description` | string | 是 | 变体描述（如 "injured, covered in blood"） |
| `seed` | int | 否 | 固定随机种子，确保一致性 |

### `animate_character` 参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `character_id` | string | 必填 | 目标角色 UUID |
| `template_animation_id` | string | null | 预设动画类型（walk/run/idle 等） |
| `action_description` | string | null | 自定义动作描述（与 template 二选一） |
| `animation_name` | string | null | 动画名称标识符 |
| `directions` | int | null | 方向数量 |
| `confirm_cost` | bool | `false` | 确认消耗费用（生成前询问） |

---

## 地图物体生成

### `create_map_object` 参数详解

生成带透明背景的地图物体，适合直接叠加到游戏场景。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `description` | string | 必填 | 物体外观描述 |
| `width` | int | null | 宽度像素 |
| `height` | int | null | 高度像素 |
| `view` | string | `high top-down` | 视角 |
| `outline` | string | `single color outline` | 描边风格 |
| `shading` | string | `medium shading` | 阴影处理 |
| `detail` | string | `medium detail` | 细节程度 |
| `background_image` | string | null | 参考图（base64） |
| `inpainting` | object | null | 内容引导 |

**示例：生成宝箱**
```
create_map_object(
  description="old wooden treasure chest with iron lock, slightly open, gold coins visible inside",
  width=32,
  height=32,
  view="high top-down"
)
```

### `create_object` 参数详解

通用物体生成，支持多方向视图和动画帧。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `description` | string | 必填 | 物体描述 |
| `directions` | int | `8` | 方向视图数量 |
| `size` | int | `64` | 画布像素大小 |
| `n_frames` | int | `1` | 动画帧数 |
| `view` | string | `low top-down` | 视角 |
| `object_view` | string | null | 自定义视角描述 |
| `reference_image_base64` | string | null | 风格参考图 |
| `state_of` | string | null | 基于已有物体生成变体 |

---

## 瓦片集生成

### `create_topdown_tileset` 参数详解

生成 Wang 瓦片集，用于地形无缝过渡（如草地→沙地）。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `lower_description` | string | 必填 | 底层地形描述（如 "grass"） |
| `upper_description` | string | 必填 | 覆盖层地形描述（如 "stone path"） |
| `transition_size` | float | `0.0` | 过渡区宽度 |
| `transition_description` | string | null | 过渡区样式描述 |
| `tile_size` | dict | `{w:16, h:16}` | 瓦片像素尺寸 |
| `outline` | string | null | 描边风格 |
| `shading` | string | null | 阴影处理 |
| `detail` | string | null | 细节程度 |
| `view` | `high top-down`/`low top-down` | `high top-down` | 视角 |
| `tile_strength` | float | `1.0` | 图案强度 |
| `lower_base_tile_id` | string | null | 关联已有底层瓦片集 UUID（保持风格一致） |
| `upper_base_tile_id` | string | null | 关联已有覆盖层瓦片集 UUID |
| `tileset_adherence` | float | `100.0` | 与基础瓦片集的一致性 |
| `text_guidance_scale` | float | `8.0` | 文字描述权重 |

**示例：生成草地→石板路过渡瓦片**
```
create_topdown_tileset(
  lower_description="dark green grass with small pebbles",
  upper_description="gray stone path with cracks",
  tile_size={"width": 16, "height": 16},
  view="high top-down"
)
```

### `create_sidescroller_tileset` 参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `lower_description` | string | 必填 | 平台材质（如 "stone with moss"） |
| `transition_description` | string | 必填 | 表面装饰（如 "grass and small flowers on top"） |
| `transition_size` | float | `0.0` | 装饰覆盖范围 |
| `tile_size` | dict | `{w:16, h:16}` | 瓦片像素尺寸 |
| `seed` | int | null | 随机种子 |

### `create_isometric_tile` 参数详解

生成单块等轴测（2.5D）瓦片。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `description` | string | 必填 | 瓦片外观描述 |
| `size` | int | `32` | 像素大小 |
| `tile_shape` | `thin`/`thick`/`block` | `block` | 高度轮廓形状 |
| `outline` | `lineless`/`single color` | `lineless` | 描边风格 |
| `shading` | string | `basic shading` | 阴影处理 |
| `detail` | string | `medium detail` | 细节程度 |
| `seed` | int | null | 随机种子 |

---

## 物体动画生成与帧下载

### `animate_object` 参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `object_id` | string | 必填 | 目标物体 UUID（必须已完成生成） |
| `animation_description` | string | 必填 | 动画动作描述（英文） |
| `animation_name` | string | null | 动画名称标识符 |
| `frame_count` | int | `8` | 帧数，可选 4/6/8/10/12/14/16 |
| `directions` | list | null | 方向列表，1方向物体默认 `["unknown"]` |

**示例：为陨石生成下落动画**
```
animate_object(
  object_id="5554280b-...",
  animation_description="meteorite falling down from sky, tumbling and rotating while descending, glowing hot trail behind it",
  frame_count=16,
  animation_name="fall"
)
```

### 动画帧 URL 规律

`animate_object` 返回 `animation_id`，帧图像存储于：

```
https://backblaze.pixellab.ai/file/pixellab-characters/objects/{user_id}/{object_id}/animations/{animation_id}/{direction}/{frame_index}.png
```

- `{user_id}`：从 `get_object` 返回的 Storage URL 中提取（`objects/` 与 `{object_id}` 之间的 UUID）
- `{direction}`：1方向物体为 `unknown`，8方向物体为 `south`/`north` 等
- `{frame_index}`：从 `0` 开始，共 N 帧

**提取 user_id 示例**：
Storage URL 格式：`https://backblaze.pixellab.ai/file/pixellab-characters/objects/{user_id}/{object_id}/rotations/unknown.png`

### 批量下载帧

所有下载的资源必须保存到 `Assets/Out/` 目录下。使用 curl 批量下载（bash）：

```bash
FRAMES_DIR="Assets/Out/<资源名>/frames"
mkdir -p "$FRAMES_DIR"
for i in $(seq 0 15); do
  curl -s "https://backblaze.pixellab.ai/file/pixellab-characters/objects/{user_id}/{object_id}/animations/{animation_id}/unknown/${i}.png" \
    -o "$FRAMES_DIR/${i}.png"
done
```

### 合成精灵图（PowerShell）

使用 `.claude/scripts/make_spritesheet.ps1` 将帧合成为 NxN 精灵图，输出文件保存到 `Assets/Out/`：

```powershell
# 修改脚本中的变量后执行
powershell.exe -ExecutionPolicy Bypass -File ".claude/scripts/make_spritesheet.ps1"
```

脚本变量说明（修改脚本顶部）：
- `$framesDir`：帧图像目录（如 `Assets/Out/<资源名>/frames`）
- `$output`：输出精灵图路径（必须在 `Assets/Out/` 下，如 `Assets/Out/<资源名>_spritesheet.png`）
- `$cols` / `$rows`：列数与行数（如 4x4 = 16帧）
- `$frameCount`：使用的帧数（`$cols * $rows`）

输出为 RGBA PNG，尺寸 = `(单帧宽 × cols) x (单帧高 × rows)`。

---

## 生成结果查询模式

所有生成工具均为**异步**，需要轮询 `get_*` 工具获取结果：

```
1. 调用 create_* → 返回 { id: "xxx", status: "pending" }
2. 调用 get_*(id) → 检查 status 字段
   - "pending" / "processing" → 继续等待，5-10秒后重试
   - "completed" → 结果已就绪，获取图像数据
   - "failed" → 生成失败
```

**轮询间隔建议**：
- 角色/物体：10-30秒
- 瓦片集：15-30秒
- 等轴测瓦片：5-15秒

---

## Outline 强制规则

**所有生成的像素图片，物体轮廓必须有 outline（描边）**，这是本项目的硬性规定：

- `create_character` / `create_character_state`：`outline` 参数必须设为 `"single color black outline"`（工具默认值即为此，禁止改为 `"no outline"` 或 `"lineless"`）
- `create_map_object` / `create_object`：`outline` 参数必须设为 `"single color outline"` 或 `"single color black outline"`
- `create_isometric_tile`：`outline` 参数必须设为 `"single color"`（**注意：工具默认值为 `"lineless"`，必须显式覆盖**）
- `create_topdown_tileset` / `create_sidescroller_tileset` / `create_tiles_pro`：若工具支持 `outline` 参数，必须传入 `"single color outline"`；若不支持，在 description 中加入 `with clear pixel outline`
- 禁止使用 `"lineless"`、`"no outline"` 或省略 outline 参数（等轴测瓦片除外不适用——实际上也必须显式设置）

---

## 项目风格建议

为保持项目像素风格统一，建议在 description 中固定加入本项目的风格外关键词（题材、色调、时代感等，由项目美术方向确定），同一批资源保持同一套关键词。

**推荐参数组合**：
- 角色尺寸：`size=48` 或 `size=64`
- 瓦片尺寸：`tile_size={"width": 16, "height": 16}`
- 描边：`single color black outline`（**必填，不可省略**）
- 细节：`medium detail`
