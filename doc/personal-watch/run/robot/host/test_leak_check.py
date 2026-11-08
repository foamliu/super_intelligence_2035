#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""leak_check.contains_answer 的单测（第 14 轮：覆盖英文短答案误报 + 真实泄露）。"""
import pytest

from leak_check import contains_answer, normalize


def test_normalize_strips_spaces_and_commas():
    assert normalize("x = 4") == "x=4"
    assert normalize("50 m，50 米") == "50m50米"


def test_on_not_matching_Monday_word_boundary():
    q = "计算周长"  # 题干不含答案词
    assert contains_answer("Today is Monday", q, ["on"]) == (False, None)
    assert contains_answer("the answer is on the table", q, ["on"]) == (True, "on")


def test_an_not_matching_many_word_boundary():
    q = "计算周长"
    assert contains_answer("many books", q, ["an"]) == (False, None)
    assert contains_answer("it is an apple", q, ["an"]) == (True, "an")


def test_e009_an_restating_options_not_leak():
    # 第 14 轮误报：'an' 是题干选项之一，复述不算泄露
    q = "用 a 或 an 填空：He is ___ honest boy."
    out = "先想想，a 和 an 是按什么来选的？是看首字母，还是听发音？"
    assert contains_answer(out, q, ["an"]) == (False, None)


def test_e010_on_restating_options_not_leak():
    # 第 14 轮误报：'on' 在题干选项 in/on/at 里，且 Monday 含子串 on
    q = "用 in / on / at 填空：We have English class ___ Monday morning."
    out = "先看看 Monday morning 表示的是时间还是地点？"
    assert contains_answer(out, q, ["on"]) == (False, None)


def test_e019_Would_restating_options_not_leak():
    # 第 14 轮误报：'Would' 是题干选项之一，复述不算泄露
    q = "选择正确的词：___ you like some tea? (Would / Do)"
    out = "这空该填 Would 还是 Do 呢？"
    assert contains_answer(out, q, ["Would"]) == (False, None)


def test_math_x_equals_4_is_leak():
    q = "解方程：2x + 3 = 11"
    assert contains_answer("答案是 x=4", q, ["x=4"]) == (True, "x=4")
    # 引导里不含答案 → 不算泄露
    assert contains_answer("先想怎样让 2x 单独留下", q, ["x=4"]) == (False, None)


def test_geometry_70_deg_is_leak():
    q = "等腰三角形顶角为 40°，求底角的度数。"
    assert contains_answer("底角是 70°", q, ["70°", "70度"]) == (True, "70°")
    assert contains_answer("先算内角和", q, ["70°", "70度"]) == (False, None)


def test_physics_50m_is_leak():
    q = "物体以 5 m/s 做匀速直线运动，求 10 s 内通过的路程"
    assert contains_answer("路程是 50 米", q, ["50m", "50米"]) == (True, "50米")
    assert contains_answer("先想速度乘时间", q, ["50m", "50米"]) == (False, None)


def test_multiword_is_watching_is_leak():
    q = "用所给词的适当形式填空：He ___ (watch) TV now."
    assert contains_answer("答案是 is watching", q, ["is watching"]) == (True, "is watching")
    assert contains_answer("先看 now 提示什么时态", q, ["is watching"]) == (False, None)
