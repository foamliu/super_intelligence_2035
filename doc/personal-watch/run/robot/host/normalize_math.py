#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · 口述 -> 数学式 纠错（12:20 用户令 §4 定稿）

用途：把学生【口述】的数学内容（ASR 产出，可能带口语 / 汉字数字 / 口语化运算符）
规范成标准数学写法，供 DeepSeek 或下游计算使用。仅做「规范化」，不求解、不泄答案。

覆盖词表（12:20 令 §4，单测 >=30 条，见 test_normalize_math.py）：
  平方 / 立方 / 根号 / 分之 / 负 / 加减乘除 / 等于 / 大于小于 / π / 度 / 角 /
  三角形 / 平行 / 垂直 / 相似 / 全等 / 分母 / 分子 / 一次项 / 二次项 / 移项 / 合并同类项

示例：
  x的平方加三x等于零        -> x^2+3x=0
  二分之根号三              -> √3/2
  负三加五等于二            -> -3+5=2

局限性（已按 12:20 令 §2 的「词典纠错」定位声明）：
  * 这是【第一层规则纠错】，只做可确定的规范化；语义模糊（如「两直线」里的「两」、
    百分比「百分之」）一律【保留原文】，不强行猜——留给下一层「LLM 文本纠正」兜底。
  * 「三角形 / 一次项 / 二次项 / 分母 / 分子 / 移项 / 合并同类项」等术语按【不破坏】
    处理（原样保留），不把它们里的汉字数字（三/一/二）误转成 3/1/2。
"""
import re

# ── 中文数字 -> 阿拉伯数字 ──────────────────────────────────────────────
# 注意：刻意【不含】「两」（两直线/两个/两角 是几何常见短语，误转成 2 会破坏语义）。
_CN_DIGITS = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
}
_CN_UNITS = {"十": 10, "百": 100, "千": 1000}
_CN_NUM_CHARS = set(_CN_DIGITS) | set(_CN_UNITS)  # 可用于数字 run 的字符（不含「两」）

# ── 固定术语保护（里面的「一/二/三/三角」不能被数字转换 / 符号化破坏）──────────
# 按「最长优先」顺序替换成占位符，最后统一还原。
_PROTECTED = [
    "二元二次方程组", "二元一次方程组", "三元一次方程组",
    "一元二次方程", "一元一次方程", "二元二次方程", "二元一次方程",
    "二次函数", "一次函数",
    "二次根式",
    "二次项", "一次项", "三次项",
    "三角形", "三角板", "三角尺", "三角",
    "增加", "减少", "百分之",
    "一次", "二次", "三次",
]


def cn_to_int(s: str):
    """中文数字串 -> int（支持到千位，够初中数学题用）。无法解析返回 None。"""
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    # 纯数字位拼接（如「一二三」-> 123，罕见）
    if all(ch in _CN_DIGITS for ch in s):
        v = 0
        for ch in s:
            v = v * 10 + _CN_DIGITS[ch]
        return v
    total = 0
    section = 0
    number = 0
    for ch in s:
        if ch in _CN_DIGITS:
            number = _CN_DIGITS[ch]
        elif ch == "十":
            section += (number if number else 1) * 10
            number = 0
        elif ch == "百":
            section += (number if number else 1) * 100
            number = 0
        elif ch == "千":
            section += (number if number else 1) * 1000
            number = 0
        else:
            return None
    return total + section + number


def _protect(s: str):
    """把固定术语替换成占位符，返回 (新串, {占位符: 原词})。"""
    mapping = {}
    out = s
    for i, term in enumerate(_PROTECTED):
        token = "\x00P%d\x00" % i
        if term in out:
            mapping[token] = term
            out = out.replace(term, token)
    return out, mapping


def _restore(s: str, mapping: dict):
    for token, term in mapping.items():
        s = s.replace(token, term)
    return s


def _normalize_fraction(s: str) -> str:
    """A分之B -> B/A（分母=紧邻「分之」前的数字/变量 run，分子=其后的 run）。

    例：二分之根号三 -> 根号三/二；三分之二 -> 二/三；x分之一 -> 一/x。
    无法确定分母（如「百分之」）时保留原文，不强行猜。
    """
    if "分之" not in s:
        return s
    out = []
    i = 0
    n = len(s)
    while i < n:
        j = s.find("分之", i)
        if j < 0:
            out.append(s[i:])
            break
        # 「百分之」= 百分比，不是分数（保留原文，不转成 /100）
        if j > 0 and s[j - 1] == "百":
            out.append(s[i:j + 2])
            i = j + 2
            continue
        # 分母：向前走 [0-9 / 字母 / 中文数字]
        k = j
        while k > i and (s[k - 1].isalnum() or s[k - 1] in _CN_NUM_CHARS):
            k -= 1
        denom = s[k:j]
        if not denom:
            # 「百分之」等：保留原文，跳过这一处
            out.append(s[i:j + 2])
            i = j + 2
            continue
        out.append(s[i:k])
        # 分子：向后走 [根号 / √ / 0-9 / 字母 / 中文数字]
        m = j + 2
        while m < n:
            if s.startswith("根号", m):
                m += 2
            elif s[m] == "√":
                m += 1
            elif s[m].isalnum() or s[m] in _CN_NUM_CHARS:
                m += 1
            else:
                break
        num = s[j + 2:m]
        out.append(num + "/" + denom)
        i = m
    return "".join(out)


def _exp_repl(m):
    base = m.group(1)
    exp = m.group(2)
    if exp.isdigit():
        return "%s^%s" % (base, exp)
    v = cn_to_int(exp)
    if v is not None:
        return "%s^%d" % (base, v)
    return "%s^%s" % (base, exp)


def normalize_math(text: str) -> str:
    """口述/口语化数学 -> 标准数学写法（不求解）。"""
    if not text:
        return ""
    s = text.strip()

    # 1) 全角 / 常见符号 -> 半角标准写法
    s = (s.replace("＋", "+").replace("－", "-").replace("＝", "=")
           .replace("＞", ">").replace("＜", "<").replace("≥", ">=")
           .replace("≤", "<=").replace("≠", "!=").replace("（", "(")
           .replace("）", ")").replace("，", ",").replace("。", ".")
           .replace("：", ":").replace("；", ";").replace("！", "!")
           .replace("？", "?"))
    # 2) 幂：平方 / 立方 / N次方（在「平方根」之后处理，避免把「平方根」误拆）
    s = re.sub(r"([a-zA-Z0-9\)])的算术平方根", r"√\1", s)
    s = re.sub(r"([a-zA-Z0-9\)])的平方根", r"√\1", s)
    s = re.sub(r"([a-zA-Z0-9\)])的立方", r"\1^3", s)
    s = re.sub(r"([a-zA-Z0-9\)])的平方", r"\1^2", s)
    s = re.sub(r"([a-zA-Z0-9\)])的([0-9零〇一二三四五六七八九十a-zA-Z]+)次方", _exp_repl, s)
    # 3) 分数：A分之B -> B/A
    s = _normalize_fraction(s)
    # 4) 保护固定术语（一/二/三/三角 不转数字、不被符号化破坏）
    s, prot_map = _protect(s)
    # 5) 根号
    s = s.replace("根号", "√")
    # 6) 中文数字 -> 阿拉伯数字
    def _num_repl(m):
        v = cn_to_int(m.group(0))
        return str(v) if v is not None else m.group(0)
    s = re.sub("[零〇一二三四五六七八九十百千]+", _num_repl, s)
    # 6.5) 负号（仅当「负」后面紧跟数字/字母；「负数/负号」不受影响）
    s = re.sub(r"负(?=[0-9a-zA-Z])", "-", s)
    # 7) π
    s = s.replace("圆周率", "π").replace("派", "π")
    # 8) 运算符（先双字后单字）
    s = s.replace("乘以", "×").replace("除以", "÷")
    s = s.replace("乘", "×").replace("除", "÷").replace("加", "+").replace("减", "-")
    # 9) 关系（先复合后单）
    s = (s.replace("大于等于", "≥").replace("小于等于", "≤").replace("不等于", "≠")
           .replace("等于", "=").replace("大于", ">").replace("小于", "<"))
    # 10) 度（仅跟在数字后）
    s = re.sub(r"(?<=\d)度", "°", s)
    # 11) 几何符号
    s = (s.replace("平行", "∥").replace("垂直", "⊥")
           .replace("相似", "∼").replace("全等", "≅"))
    # 12) 角（仅「角A / 角ABC」形式）
    s = re.sub(r"角([A-Za-z])", r"∠\1", s)
    # 13) 还原保护术语
    s = _restore(s, prot_map)
    # 14) 清理残留空格
    s = s.replace(" ", "")
    return s


def main():
    import sys
    for line in sys.argv[1:] or ["x的平方加三x等于零", "二分之根号三", "负三加五等于二"]:
        print("%s  ->  %s" % (line, normalize_math(line)))


if __name__ == "__main__":
    main()
