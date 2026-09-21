# -*- coding: utf-8 -*-
"""从多语言 JSON 文本提取唯一字符，生成 TMP Font Asset Creator 用的字符集 txt。
用法: gen-font-charset.py [lang...]  (默认 jp kr tw)
输出: Assets/FrameWork/Resources/Front/<语言名>字符集.txt
"""
import glob
import os
import sys

# 项目根 = 脚本位置向上两级（.claude/scripts/ -> 根）
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON_DIR = os.path.join(ROOT, "Assets", "Resources", "JsonText")
OUT_DIR = os.path.join(ROOT, "Assets", "FrameWork", "Resources", "Front")

# ASCII 可打印字符（含空格）
ASCII_CHARS = "".join(chr(c) for c in range(0x20, 0x7F))
# 全角 ASCII 变体（！～），CJK 文本常混入
FULLWIDTH_ASCII = "".join(chr(c) for c in range(0xFF01, 0xFF5F))
# CJK 通用标点
CJK_PUNCT = "　、。・！？《》「」『』【】（）〔〕〈〉—…～·‥"

# 各语言的额外整区块（保证未来新词用常见字符时不缺字）
LANG_EXTRA = {
    # 平假名 U+3041-3096、片假名 U+30A1-30FA、长音/中点等
    "jp": "".join(chr(c) for c in range(0x3041, 0x3097))
    + "".join(chr(c) for c in range(0x30A1, 0x30FB))
    + "ーゝゞゟ",
    # 韩文为组合音节，无小区块可整取；补充 KS X 1001 之外的常见符号
    "kr": "ᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄋᄌᄍᄎᄏᄐᄑ하ᅢᅣᅤᅥᅦᅧᅨᅩᅪᅫᅬᅭᅮᅯᅰᅱᅲᅳᅴᅵᆨᆩᆪᆫᆬᆭᆮᆯᆰᆱᆲᆳᆴᆵᆶᆷᆸᆹᆺᆻᆼᆽᆾᆿᇀᇁᇂ",
    # 繁中：与简体共用 CJK 区块，无小区块；补充注音符号（台湾常用）
    "tw": "".join(chr(c) for c in range(0x3105, 0x312A)),
    # 拉丁：Latin-1 补充 U+00A0-00FF + 拉丁扩展A U+0100-017F（覆盖德法西意葡等变音符）+ 通用标点
    "latin": "".join(chr(c) for c in range(0x00A0, 0x0180))
    + "–—‘’‚“”„‹›«»•‰†‡…",
}
LANG_NAME = {"jp": "日语", "kr": "韩语", "tw": "繁中", "latin": "拉丁"}
# latin 为合成字符集：合并扫描这些语言的文本
LANG_SOURCES = {"latin": ["en", "de", "fr"]}


def collect_chars(lang):
    """收集某语言全部 JsonText 文本中出现的唯一字符。"""
    chars = set()
    file_count = 0
    for src in LANG_SOURCES.get(lang, [lang]):
        pattern = os.path.join(JSON_DIR, f"*_{src}.txt")
        files = glob.glob(pattern)
        file_count += len(files)
        for f in files:
            with open(f, encoding="utf-8") as fp:
                chars.update(fp.read())
    return chars, file_count


def main():
    langs = sys.argv[1:] or ["jp", "kr", "tw"]
    for lang in langs:
        chars, file_count = collect_chars(lang)
        base = set(ASCII_CHARS + FULLWIDTH_ASCII + CJK_PUNCT + LANG_EXTRA.get(lang, ""))
        all_chars = sorted(base | chars)
        # 剔除换行/回车/制表符等控制字符（TMP 字符文件不需要）
        text = "".join(c for c in all_chars if ord(c) >= 0x20 and c != "\x7f")
        out_path = os.path.join(OUT_DIR, f"{LANG_NAME.get(lang, lang)}字符集.txt")
        with open(out_path, "w", encoding="utf-8") as fp:
            fp.write(text)
        print(f"{lang}: {file_count} 个语言文件 -> {len(text)} 字符 -> {out_path}")


if __name__ == "__main__":
    main()
