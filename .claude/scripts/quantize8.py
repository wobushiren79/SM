# -*- coding: utf-8 -*-
"""
quantize8.py —— 彩色像素图标控色工具（复用工具脚本，勿删）。

把一张（伪）像素图量化到 <=N 种颜色（默认 8），用于深渊馈赠 / 成就等
32x32 彩色图标流水线的「控色 <=8」步骤（见 .claude/memory/reference_colored_icons.md）。

规则：
- 保留透明背景：alpha < 阈值(默认128) 的像素直接写成完全透明 (0,0,0,0)，
  不参与量化，也不占用调色板名额。
- 只对不透明像素做中位切分(MEDIANCUT)量化，硬保证不透明区颜色数 <= N。
- 黑色描边会自然成为其中一色。
- 可选 --size 把图缩放到指定正方形尺寸（NEAREST，保持像素硬边），默认 32。
  传 0 表示不缩放。

用法（务必经 run-python.ps1 调用）：
  run-python.ps1 quantize8.py <输入.png> [-o 输出.png] [--colors 8] [--size 32] [--alpha-threshold 128]
  - 省略 -o 时就地覆盖输入文件。
  - 支持多个输入： quantize8.py a.png b.png c.png  （逐个就地覆盖）。
"""
import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("quantize8.py: 需要 Pillow (PIL)，请先 pip install pillow\n")
    sys.exit(2)


def quantize_one(in_path, out_path, colors, size, alpha_threshold):
    img = Image.open(in_path).convert("RGBA")
    if size and (img.width != size or img.height != size):
        img = img.resize((size, size), Image.NEAREST)

    w, h = img.size
    src = img.load()

    # 收集不透明像素坐标与其 RGB
    coords = []
    rgb_list = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            if a >= alpha_threshold:
                coords.append((x, y))
                rgb_list.append((r, g, b))

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    if coords:
        n = min(colors, len(set(rgb_list)))
        n = max(1, n)
        # 只对不透明像素做中位切分量化，硬保证颜色数 <= colors
        strip = Image.new("RGB", (len(rgb_list), 1))
        strip.putdata(rgb_list)
        q = strip.quantize(colors=n, method=Image.MEDIANCUT).convert("RGB")
        qdata = list(q.getdata())
        dst = out.load()
        for (x, y), (r, g, b) in zip(coords, qdata):
            dst[x, y] = (r, g, b, 255)

    out.save(out_path)

    # 统计最终不透明颜色数
    final = out.load()
    uniq = set()
    for y in range(h):
        for x in range(w):
            r, g, b, a = final[x, y]
            if a > 0:
                uniq.add((r, g, b))
    return len(uniq), out.size


def main():
    ap = argparse.ArgumentParser(description="量化像素图标到 <=N 色，保留透明背景。")
    ap.add_argument("inputs", nargs="+", help="输入 PNG（可多个）")
    ap.add_argument("-o", "--out", default=None, help="输出路径（仅单输入有效；省略则就地覆盖）")
    ap.add_argument("--colors", type=int, default=8, help="最大颜色数（默认 8）")
    ap.add_argument("--size", type=int, default=32, help="缩放到 NxN，0 表示不缩放（默认 32）")
    ap.add_argument("--alpha-threshold", type=int, default=128, help="alpha 低于此值视为透明（默认 128）")
    args = ap.parse_args()

    if args.out and len(args.inputs) > 1:
        sys.stderr.write("quantize8.py: -o 只能配合单个输入使用\n")
        sys.exit(2)

    for in_path in args.inputs:
        out_path = args.out if args.out else in_path
        cnt, sz = quantize_one(in_path, out_path, args.colors, args.size, args.alpha_threshold)
        print(f"[OK] {os.path.basename(in_path)} -> {os.path.basename(out_path)}  {sz[0]}x{sz[1]}  colors={cnt}")


if __name__ == "__main__":
    main()
