#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tutor_agent.clamp_hint 单测（11:40 令 §1.1「每次回复 ≤2 句」的确定性裁剪）。"""
import os
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


def test_does_not_hard_truncate_sentence():
    # 只删整句、不硬截单句（避免 TTS 破音）
    long_one = "这是一个超过二十个字的很长的引导句子它不会被从中间切断。"
    assert ta.clamp_hint(long_one) == long_one
