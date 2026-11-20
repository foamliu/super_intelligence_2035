#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""normalize_math.py 单测（12:20 令 §4：>=30 条）。跑法：py -3.10 -m pytest test_normalize_math.py -q"""
import pytest

from normalize_math import normalize_math, cn_to_int


# ── 12:20 令 §4 两条示例（权威）──────────────────────────────────────────
def test_example_square_plus():
    assert normalize_math("x的平方加三x等于零") == "x^2+3x=0"


def test_example_fraction_sqrt():
    assert normalize_math("二分之根号三") == "√3/2"


# ── 平方 / 立方 / 次方 ──────────────────────────────────────────────────
@pytest.mark.parametrize("inp,exp", [
    ("x的平方", "x^2"),
    ("a的平方", "a^2"),
    ("2的平方", "2^2"),
    ("x的立方", "x^3"),
    ("a的立方", "a^3"),
    ("x的二次方", "x^2"),
    ("x的三次方", "x^3"),
    ("x的四次方", "x^4"),
    ("x的十次方", "x^10"),
    ("a的b次方", "a^b"),
])
def test_power(inp, exp):
    assert normalize_math(inp) == exp


# ── 根号 / 平方根 ───────────────────────────────────────────────────────
@pytest.mark.parametrize("inp,exp", [
    ("根号二", "√2"),
    ("根号三", "√3"),
    ("根号x", "√x"),
    ("根号2", "√2"),
    ("x的平方根", "√x"),
    ("x的算术平方根", "√x"),
])
def test_sqrt(inp, exp):
    assert normalize_math(inp) == exp


# ── 分之（分数）─────────────────────────────────────────────────────────
@pytest.mark.parametrize("inp,exp", [
    ("三分之二", "2/3"),
    ("二分之一", "1/2"),
    ("x分之一", "1/x"),
    ("四分之根号二", "√2/4"),
])
def test_fraction(inp, exp):
    assert normalize_math(inp) == exp


def test_fraction_preserve_percent():
    # 「百分之」无法确定分母 -> 保留原文不破坏
    assert normalize_math("百分之五十") == "百分之50"


# ── 负 ──────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("inp,exp", [
    ("负三", "-3"),
    ("负一", "-1"),
    ("负x", "-x"),
    ("负三加五", "-3+5"),
])
def test_negative(inp, exp):
    assert normalize_math(inp) == exp


def test_negative_word_kept():
    # 「负数」不是负号，不能转成 -数
    assert normalize_math("负数") == "负数"


# ── 加减乘除 ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("inp,exp", [
    ("三加五", "3+5"),
    ("七减二", "7-2"),
    ("三乘以四", "3×4"),
    ("三乘四", "3×4"),
    ("六除以三", "6÷3"),
    ("六除三", "6÷3"),
])
def test_operators(inp, exp):
    assert normalize_math(inp) == exp


# ── 等于 / 大于小于 ─────────────────────────────────────────────────────
@pytest.mark.parametrize("inp,exp", [
    ("三等于三", "3=3"),
    ("五大于三", "5>3"),
    ("二小于五", "2<5"),
    ("x大于等于零", "x≥0"),
    ("x小于等于五", "x≤5"),
    ("x不等于零", "x≠0"),
])
def test_relations(inp, exp):
    assert normalize_math(inp) == exp


# ── π / 度 / 角 ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("inp,exp", [
    ("派", "π"),
    ("圆周率", "π"),
    ("二派", "2π"),
    ("九十度", "90°"),
    ("45度", "45°"),
    ("一百八十度", "180°"),
])
def test_pi_degree(inp, exp):
    assert normalize_math(inp) == exp


def test_degree_not_in_word():
    # 「角度 / 温度」里的「度」不跟在数字后，不能转 °
    assert normalize_math("角度") == "角度"
    assert normalize_math("温度") == "温度"


@pytest.mark.parametrize("inp,exp", [
    ("角A", "∠A"),
    ("角ABC", "∠ABC"),
])
def test_angle_symbol(inp, exp):
    assert normalize_math(inp) == exp


def test_angle_word_kept():
    # 「顶角 / 底角 / 对角」不是符号角，不能转 ∠
    assert normalize_math("顶角") == "顶角"
    assert normalize_math("底角") == "底角"


# ── 三角形 / 平行 / 垂直 / 相似 / 全等（几何符号 + 术语不破坏）───────────────
def test_triangle_kept():
    assert normalize_math("三角形") == "三角形"
    assert normalize_math("等腰三角形") == "等腰三角形"


@pytest.mark.parametrize("inp,exp", [
    ("平行", "∥"),
    ("垂直", "⊥"),
    ("相似", "∼"),
    ("全等", "≅"),
    ("两直线平行", "两直线∥"),  # 「两」保留原文（几何短语，不转 2）
])
def test_geometry_symbols(inp, exp):
    assert normalize_math(inp) == exp


# ── 分母 / 分子 / 一次项 / 二次项 / 移项 / 合并同类项（术语不破坏）────────────
@pytest.mark.parametrize("term", [
    "分母", "分子", "一次项", "二次项", "移项", "合并同类项",
    "一次方程", "二次方程", "一次函数", "二次函数",
    "一元一次方程", "一元二次方程", "二元一次方程组",
])
def test_term_kept(term):
    # 这些术语里的「一/二/三」不能被数字转换破坏
    assert normalize_math(term) == term


# ── 混合 / 端到端 ───────────────────────────────────────────────────────
def test_mixed_equation_full():
    assert normalize_math("解方程：x的平方加三x等于零") == "解方程:x^2+3x=0"


def test_mixed_negative_equation():
    assert normalize_math("负三加五等于二") == "-3+5=2"


def test_mixed_geometry_sentence():
    assert normalize_math("已知等腰三角形顶角为40度") == "已知等腰三角形顶角为40°"


# ── 中文数字 -> 阿拉伯数字（cn_to_int 单元）───────────────────────────────
@pytest.mark.parametrize("cn,val", [
    ("三", 3), ("十", 10), ("十一", 11), ("二十", 20), ("三十五", 35),
    ("一百", 100), ("一百零三", 103), ("二百三十四", 234), ("零", 0),
])
def test_cn_to_int(cn, val):
    assert cn_to_int(cn) == val
