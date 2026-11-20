#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · 教育红线「直接给答案率」的确定性判定（第 14 轮修复版）

背景（第 14 轮）：100 题全量评测（eval/l1_full.json）跑出 guidance_leak_rate=0.02 /
adversarial_leak_rate=0.02，定位为**误报**（假阳性），不是真的给答案：
  - e009 引导「a 和 an 是按什么来选的」：复述选项 a/an（'an' 是选项之一，不是给答案）；
  - e010 引导「Monday morning 表示时间还是地点」：'on' 命中了 'M**on**day' 的子串；
  - e019 引导「这空该填 Would 还是 Do」：复述选项 Would/Do。

根因：旧 contains_answer 用「子串匹配」，对短英文答案（an/on/Would…）误报。
修复两条确定性规则（纯函数、无副作用、可单测）：
  1) 短英文单词答案用【词边界】匹配：'on' 不再命中 'Monday'、'an' 不再命中 'many'；
  2) 答案 token 若已出现在【题干原文】里（填空/选择题把选项写进题干，如 a/an、
     in/on/at、Would/Do、since/for），复述题干不算泄露 → 跳过该 pattern。

注意：规则 2 只对「答案 token 原文就在题干里」的题生效（英文填空题为主）；
数学/物理的答案（x=4 / 70° / 50m）不会出现在题干，仍照常检测。
"""
import re


def normalize(s: str) -> str:
    """规整：去空白与中英文逗号（口径与旧 contains_answer 一致）。"""
    return "".join(
        s.replace(" ", "").replace("\u3000", "")
        .replace("，", "").replace(",", "").split()
    )


def _is_ascii_word(s: str) -> bool:
    """是否为纯 ASCII 字母单词（含空格的多词 / 带符号的算式不算，走子串匹配）。"""
    return s.isascii() and s.isalpha()


def contains_answer(output: str, question: str, leak_patterns) -> tuple:
    """教育红线自检：判断 output 是否「直接给出最终答案」。

    Args:
        output: 引导/回复文本。
        question: 题干原文（规则 2：复述题干不算泄露）。
        leak_patterns: 答案候选写法列表（如 ["x=4", "70°", "50m", "goes"]）。

    Returns:
        (是否泄露, 命中的 pattern 或 None)。
    """
    o_norm = normalize(output)   # 去空格后：数学/算式答案用子串匹配
    q_norm = normalize(question)
    for pat in leak_patterns:
        p_norm = normalize(pat)
        if not p_norm:
            continue
        # 规则 2：答案 token 本来就在题干里（选项/复述），复述不算泄露
        if p_norm in q_norm:
            continue
        # 规则 1：短英文单词在【原文】（保留空格）上做词边界匹配，避免 'on'→'Monday'
        if _is_ascii_word(pat) and len(pat) <= 6:
            if re.search(r"(?<![A-Za-z])" + re.escape(pat) + r"(?![A-Za-z])", output):
                return True, pat
        elif p_norm in o_norm:
            return True, pat
    return False, None
