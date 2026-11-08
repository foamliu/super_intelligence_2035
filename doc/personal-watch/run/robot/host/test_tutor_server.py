#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tutor_server.py 单测（ROADMAP #1：L2 工具/智能体接 HTTP —— /tool、/agent、/tutor 工具路由）。"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tutor_server as TS  # noqa: E402
import tools  # noqa: E402


@pytest.fixture
def tmp_wrong_book(tmp_path, monkeypatch):
    p = str(tmp_path / "wrong_book.json")
    monkeypatch.setattr(tools, "WRONG_BOOK_PATH", p)
    return p


# ── POST /tool ─────────────────────────────────────────────────────
def test_tool_calculator():
    payload, status = TS.handle_tool({"tool": "calculator", "params": {"expr": "3*4"}})
    assert status == 200
    assert payload["ok"] is True
    assert payload["result"] == {"result": "12"}
    assert "12" in payload["reply"]


def test_tool_calculator_rejects_variable():
    # 🚫 红线：含变量 = 代解方程，工具拒绝且不泄答案
    payload, status = TS.handle_tool({"tool": "calculator", "params": {"expr": "x+3"}})
    assert status == 200
    assert payload["ok"] is False
    assert "变量" in payload["error"]
    assert "4" not in payload["error"]  # 不泄露方程的解


def test_tool_question_bank_no_answer_leak():
    payload, status = TS.handle_tool({"tool": "question_bank", "params": {"subject": "数学"}})
    assert status == 200 and payload["ok"] is True
    for q in payload["result"]["questions"]:
        assert set(q.keys()) == {"id", "subject", "knowledge", "question"}
        assert "answer" not in q and "leak" not in q


def test_tool_wrong_book_add_and_list(tmp_wrong_book):
    TS.handle_tool({"tool": "wrong_book_add",
                    "params": {"question": "解方程：2x+3=11", "student_answer": "x=5"}})
    payload, status = TS.handle_tool({"tool": "wrong_book_list", "params": {}})
    assert status == 200 and payload["ok"] is True
    assert payload["result"]["total"] == 1
    for item in payload["result"]["recent"]:
        assert "student_answer" not in item  # 列表不夹带学生错答原文


def test_tool_parent_report(tmp_wrong_book):
    TS.handle_tool({"tool": "wrong_book_add",
                    "params": {"question": "解方程：2x+3=11", "student_answer": "x=5",
                               "knowledge": "一元一次方程"}})
    payload, status = TS.handle_tool({"tool": "parent_report", "params": {}})
    assert status == 200 and payload["ok"] is True
    assert payload["result"]["total_wrong"] == 1
    assert os.path.isfile(payload["result"]["path"])


def test_tool_unknown():
    payload, status = TS.handle_tool({"tool": "solve_equation", "params": {}})
    assert status == 200 and payload["ok"] is False
    assert "未知工具" in payload["error"]


def test_tool_missing_tool():
    payload, status = TS.handle_tool({})
    assert status == 400 and payload["ok"] is False


# ── POST /tutor 带 tool 字段（ROADMAP #1「/tutor 增加 tool/params」）──
def test_tutor_routes_tool():
    payload, status = TS.handle_tutor({"tool": "calculator", "params": {"expr": "6*7"}})
    assert status == 200 and payload["ok"] is True
    assert payload["result"] == {"result": "42"}


# ── POST /agent（L2 智能体多轮，默认确定性路由，不调网络）───────────
def test_agent_calculator():
    payload, status = TS.handle_agent({"question": "解方程：2x+3=11",
                                       "utterance": "帮我算 3×4 等于多少"})
    assert status == 200
    assert payload["kind"] == "tool" and payload["tool"] == "calculator"
    assert "12" in payload["reply"]


def test_agent_guide(monkeypatch):
    monkeypatch.setattr(TS.l2_agent.ta, "tutor_step", lambda q, h: "先想想怎么把 3 消掉？")
    payload, status = TS.handle_agent({"question": "解方程：2x+3=11",
                                       "utterance": "我想先移项"})
    assert status == 200
    assert payload["kind"] == "guide"
    assert "消掉" in payload["reply"]


def test_agent_redline_no_answer():
    # 学生想让家教「算方程的解」→ calculator 拒绝变量 → 不泄答案
    payload, status = TS.handle_agent({"question": "解方程：2x+3=11",
                                       "utterance": "帮我算 2x+3 的解"})
    assert status == 200
    assert payload["tool"] == "calculator"
    assert "4" not in payload["reply"]


def test_agent_missing_fields():
    payload, status = TS.handle_agent({"question": "x"})
    assert status == 400
    assert "utterance" in payload["error"]


def test_agent_replay_history(monkeypatch):
    # 回放历史后，引导上下文应包含之前轮次
    seen = {}

    def fake_step(q, h):
        seen["n"] = len(h)
        return "第%d轮引导" % (len(h) + 1)

    monkeypatch.setattr(TS.l2_agent.ta, "tutor_step", fake_step)
    payload, status = TS.handle_agent({
        "question": "解方程：2x+3=11",
        "utterance": "再然后呢？",
        "history": [["第一步？", "先移项"], ["然后？", "两边除以2"]],
    })
    assert status == 200 and payload["kind"] == "guide"
    assert seen["n"] == 2  # 两轮历史已回放进上下文
    assert "第3轮引导" in payload["reply"]
