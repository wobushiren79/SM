from PIL import Image
import os
import sys

# 动态推导项目根目录：脚本位于 .claude/scripts/，向上两级即项目根
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(PROJECT_ROOT, "Assets", "Out")

# 支持命令行参数覆盖；缺省回退到项目内默认路径
frames_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT_DIR, "meteorite_frames")
output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "meteorite_fall_4x4.png")

cols, rows = 4, 4
frame_count = cols * rows  # 16

frames = []
for i in range(frame_count):
    path = os.path.join(frames_dir, f"{i}.png")
    img = Image.open(path).convert("RGBA")
    frames.append(img)

fw, fh = frames[0].size
sheet = Image.new("RGBA", (fw * cols, fh * rows), (0, 0, 0, 0))

for idx, img in enumerate(frames):
    x = (idx % cols) * fw
    y = (idx // cols) * fh
    sheet.paste(img, (x, y))

sheet.save(output_path)
print(f"Saved spritesheet: {output_path} ({fw*cols}x{fh*rows}px, {frame_count} frames)")
