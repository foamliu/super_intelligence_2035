#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tutor_agent.clamp_hint 单测（11:40 令 §1.1「每次回复 ≤2 句」的确定性裁剪）。"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tutor_agent as ta  # noqa: E402


def test_short_text_unchanged():
    assert ta.clamp_hint("你先想想要先处理哪一项？") == "你先想想要先处理哪一项？"


def test_clamp_to_two_sentences():
    text = "我们先看这道题。想一想第一步做什么？再告诉我答案。"
    out = ta.clamp_hint(text, max_sentences=2)
    assert out == "我们先看这道题。想一想第一步做什么？"


def test_empty_and_none():
    assert ta.clamp_hint("") == ""
    assert ta.clamp_hint("   ") == ""


def test_newline_and_paragraph_split():
    text = "我们先看这道题：2x + 3 = 11。\n\n我想先问问你：第一步做什么？\n\n说说你的想法。"
    out = ta.clamp_hint(text, max_sentences=2)
    # 保留前 2 句；段落间的连续换行被过滤为空句
    assert "说说你的想法" not in out
    assert "第一步做什么" in out
    assert out.count("？") + out.count("。") >= 2


def test_no_terminal_punctuation_kept():
    # 无句末标点时整段视为一句，原样返回
    assert ta.clamp_hint("先移项") == "先移项"


def test_clamp_never_adds_answer():
    # 裁剪只会删内容、不会新增内容 → 红线判定单调安全
    raw = "所以 x=4。再检验一下。"
    clipped = ta.clamp_hint(raw, max_sentences=1)
    assert clipped == "所以 x=4。"
    assert len(clipped) <= len(raw)


def test_sentence_capped_at_soft_pause_keeps_tail_question():
    # 单句超 20 字：在软停顿（逗号）处断开，优先保「句首 + 句尾问句」
    long_q = "先看看，方程左边有括号，你想先怎么处理它？"  # 21 字
    out = ta.clamp_hint(long_q)
    assert len(out) <= 20
    assert "你想先怎么处理它？" in out       # 句尾问句保留
    assert "方程左边有括号" not in out       # 中间细节被裁掉


def test_sentence_capped_at_colon_preserves_question():
    # 冒号也是软停顿；28 字长句 -> 保句首 + 句尾问句
    long_q = "先说说你的想法：要把 x 单独留下，第一步该处理哪个数？"
    out = ta.clamp_hint(long_q)
    assert len(out) <= 20
    assert "第一步该处理哪个数？" in out
    assert "要把 x 单独留下" not in out


def test_no_soft_pause_hard_truncates_to_20():
    # 整句无软停顿时硬截到 20 字并保留句末标点（最后手段）
    long_one = "这是一个超过二十个字的很长的引导句子它不会被从中间切断。"
    out = ta.clamp_hint(long_one)
    assert len(out) <= 20
    assert out.endswith("。")


def test_cap_applies_per_sentence():
    # 多句时每一句都压到 ≤20 字
    text = "左边剩下5x是对的。右边18加7，先算18加2，再加5，你试试得多少？"
    out = ta.clamp_hint(text, max_sentences=2)
    for s in re.split(r"(?<=[。！？!?；;])", out):
        if s.strip():
            assert len(s.strip()) <= 20
    assert "你试试得多少？" in out
