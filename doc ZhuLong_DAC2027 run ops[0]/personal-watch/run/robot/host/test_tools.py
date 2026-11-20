#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools.py 单测（L2 智能体工具层：安全求值 / 红线 / 5 工具）。"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tools  # noqa: E402
from tools import ToolError  # noqa: E402


# ── 计算器：安全求值 ──────────────────────────────────────────────
def test_calc_basic():
    assert tools.calculator("3*4") == {"result": "12"}


def test_calc_paren_and_power():
    assert tools.calculator("(2+3)^2") == {"result": "25"}


def test_calc_caret_power():
    assert tools.calculator("2^3") == {"result": "8"}


def test_calc_sqrt():
    assert tools.calculator("sqrt(9)") == {"result": "3"}


def test_calc_float_division():
    assert tools.calculator("1/2") == {"result": "0.5"}


def test_calc_strips_equal():
    assert tools.calculator("3*4=?") == {"result": "12"}


def test_calc_divide_by_zero():
    with pytest.raises(ToolError):
        tools.calculator("1/0")


def test_calc_rejects_variable():
    # 🚫 红线：含变量 = 代解方程，必须拒绝
    with pytest.raises(ToolError):
        tools.calculator("x + 3")


def test_calc_rejects_arbitrary_call():
    with pytest.raises(ToolError):
        tools.calculator("__import__('os').system('dir')")


def test_eval_rejects_bad_syntax():
    with pytest.raises(ToolError):
        tools.evaluate("2 +")


# ── 题库：只回题干，不泄答案 ──────────────────────────────────────
def test_question_bank_lookup():
    r = tools.question_bank_lookup(subject="数学", keyword="一元一次")
    assert r["count"] >= 1
    for q in r["questions"]:
        assert set(q.keys()) == {"id", "subject", "knowledge", "question"}
        assert "answer" not in q and "leak" not in q


def test_question_bank_no_answer_leak():
    r = tools.question_bank_lookup(subject="英语")
    for q in r["questions"]:
        assert "answer" not in q and "leak" not in q


# ── 错题本 / 家长报告：本地落盘，不夹带答案 ────────────────────────
@pytest.fixture
def tmp_wrong_book(tmp_path, monkeypatch):
    p = str(tmp_path / "wrong_book.json")
    monkeypatch.setattr(tools, "WRONG_BOOK_PATH", p)
    return p


def test_wrong_book_add_and_list(tmp_wrong_book):
    tools.wrong_book_add("解方程：2x+3=11", "x=5", "一元一次方程")
    tools.wrong_book_add("因式分解：x^2-9", "x=9", "因式分解")
    r = tools.wrong_book_list()
    assert r["total"] == 2
    assert len(r["recent"]) == 2
    for item in r["recent"]:
        assert "student_answer" not in item          # 🚫 列表里不夹带学生错答原文


def test_wrong_book_empty(tmp_wrong_book):
    assert tools.wrong_book_list()["total"] == 0


def test_parent_report(tmp_wrong_book, tmp_path):
    tools.wrong_book_add("解方程：2x+3=11", "x=5", "一元一次方程")
    out = str(tmp_path / "report.html")
    r = tools.parent_report(out_path=out)
    assert r["total_wrong"] == 1
    assert os.path.isfile(out)
    html = open(out, encoding="utf-8").read()
    assert "家教学习报告" in html
    assert "一元一次方程" in r["knowledge_top"][0]["knowledge"]


# ── 绘图 ─────────────────────────────────────────────────────────
def test_plot_function(tmp_path):
    out = str(tmp_path / "f.png")
    r = tools.plot_function("x^2-1", out_path=out)
    assert os.path.isfile(r["path"])
    assert os.path.getsize(out) > 500


def test_plot_requires_x():
    with pytest.raises(ToolError):
        tools.plot_function("2+3")


# ── 注册表 / 调度 ────────────────────────────────────────────────
def test_registry_has_five_tools():
    assert len(tools.TOOLS) >= 5
    for name in ("calculator", "question_bank", "wrong_book_add",
                 "parent_report", "plot_function"):
        assert name in tools.TOOLS


def test_tool_spec_is_valid_json():
    spec = json.loads(tools.tool_spec())
    assert isinstance(spec, list) and len(spec) >= 5
    assert all("name" in t and "description" in t for t in spec)


def test_call_tool_calculator():
    assert tools.call_tool("calculator", {"expr": "6*7"}) == {"result": "42"}


def test_call_tool_unknown():
    with pytest.raises(ToolError):
        tools.call_tool("not_a_tool", {})
