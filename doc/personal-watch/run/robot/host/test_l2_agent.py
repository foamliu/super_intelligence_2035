#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l2_agent.py 单测（工具路由 / 表达式抽取 / LLM 决策解析 / 会话多轮与红线）。"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import l2_agent as L2  # noqa: E402
import tools  # noqa: E402


# ── 确定性路由 ────────────────────────────────────────────────────
def test_route_calculator():
    d = L2.route_tool("帮我算 3×4 等于多少")
    assert d["tool"] == "calculator"
    assert d["params"]["expr"] == "3×4"


def test_route_question_bank():
    d = L2.route_tool("给我一道类似题练练")
    assert d["tool"] == "question_bank"


def test_route_wrong_book_add():
    d = L2.route_tool("这题我错了，记入错题本")
    assert d["tool"] == "wrong_book_add"


def test_route_wrong_book_list():
    d = L2.route_tool("看看错题本")
    assert d["tool"] == "wrong_book_list"


def test_route_parent_report():
    assert L2.route_tool("生成家长报告")["tool"] == "parent_report"


def test_route_plot():
    assert L2.route_tool("画一下 x^2-1 的图像")["tool"] == "plot_function"


def test_route_none():
    assert L2.route_tool("我想先移项") is None


# ── 表达式抽取 ────────────────────────────────────────────────────
def test_extract_math_basic():
    assert L2._extract_math("帮我算 3×4 等于多少") == "3×4"


def test_extract_math_chinese_ops():
    assert L2._extract_math("算一下 3 加 4") == "3+4"


def test_extract_math_keeps_variable():
    # 保留变量 → 交给 calculator 拒绝（防代解方程）
    assert L2._extract_math("帮我算 2x+3 的解") == "2x+3"


def test_extract_func():
    assert L2._extract_func("画一下 x^2-1 的图像") == "x^2-1"


def test_route_plot_extracts_expr():
    d = L2.route_tool("画一下 x^2-1 的图像")
    assert d["tool"] == "plot_function"
    assert d["params"]["expr"] == "x^2-1"


# ── LLM 决策解析（纯函数，不调网络）───────────────────────────────
def test_parse_decision_valid():
    d = L2._parse_decision('{"tool": "calculator", "params": {"expr": "6*7"}}')
    assert d["tool"] == "calculator"


def test_parse_decision_fenced():
    d = L2._parse_decision('```json\n{"tool": "plot_function", "params": {"expr": "x^2"}}\n```')
    assert d["tool"] == "plot_function"


def test_parse_decision_null():
    assert L2._parse_decision('{"tool": null}')["tool"] is None


def test_parse_decision_unknown_tool():
    with pytest.raises(ValueError):
        L2._parse_decision('{"tool": "solve_equation"}')


# ── 会话：多轮 + 红线 ─────────────────────────────────────────────
def test_session_calculator():
    s = L2.L2Session("解方程：2x + 3 = 11")
    r = s.respond("帮我算 3×4 等于多少")
    assert r["kind"] == "tool" and r["tool"] == "calculator"
    assert "12" in r["reply"]


def test_session_guide_uses_tutor(monkeypatch):
    monkeypatch.setattr(L2.ta, "tutor_step", lambda q, h: "先想想怎么把 3 消掉？")
    s = L2.L2Session("解方程：2x + 3 = 11")
    r = s.respond("我想先移项")
    assert r["kind"] == "guide"
    assert "消掉" in r["reply"]


def test_session_redline_no_answer_for_equation():
    # 学生想让家教「算方程的解」→ calculator 拒绝变量 → 友好引导，不泄答案
    s = L2.L2Session("解方程：2x + 3 = 11")
    r = s.respond("帮我算 2x+3 的解")
    assert r["tool"] == "calculator"
    assert "4" not in r["reply"]
    assert "方程" in r["reply"]


def test_session_multi_turn_context(monkeypatch):
    monkeypatch.setattr(L2.ta, "tutor_step", lambda q, h: "第%d轮引导" % (len(h) + 1))
    s = L2.L2Session("解方程：2x + 3 = 11")
    s.respond("第一步？")
    s.respond("然后呢？")
    r = s.respond("再然后？")
    assert len(s.history) == 3
    assert "第3轮引导" in r["reply"]


def test_session_wrong_book(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "WRONG_BOOK_PATH", str(tmp_path / "wb.json"))
    s = L2.L2Session("解方程：2x + 3 = 11", knowledge="一元一次方程")
    r = s.respond("这题我错了，记入错题本")
    assert r["tool"] == "wrong_book_add"
    assert tools.wrong_book_list()["total"] == 1
